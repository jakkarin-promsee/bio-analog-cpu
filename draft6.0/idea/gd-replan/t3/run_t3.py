"""
T3 — the cheap-credit ladder (Phase-5).  T0.2 proved the ~5-layer composing ceiling is LOCALITY-bound: the same
InfoNCE objective composes all 12 layers under full end-to-end backprop (window=L) but caps ~5 under local windows.
w=L is the FORBIDDEN full backprop (a diagnostic upper bound, not deployable).  The question this run answers:

    can we extend credit REACH toward the w12 ceiling WITHOUT a deep gradient chain — i.e. cheaply on the substrate
    where the backward DEPTH (gradient chain length) is the expensive operation, not the FLOP count?

The lever: OVERLAPPING coordination windows (stride < window).  Non-overlapping w2 cuts credit hard at every group
boundary (layer 1 never sees what layer 2 needs).  Overlapping w2 (stride 1) adds the [1,2] group, so credit CHAINS
one layer per overlapping group across training steps — a relaxation/message-passing approximation of global credit,
at backward DEPTH = window (= 2, cheap), paying only more groups (FLOPs), never a longer chain.

Three blocks, all on the P4.3 apparatus (L=12, W=64, per-layer linear probe to L12), 5 seeds:
  LOCALITY dose-response (non-overlap, stride=window):  w in {1,2,3,4,6,12}  -> depth-vs-reach + the w12 ceiling.
  OVERLAP (the discovery):  w2s1, w3s1, w4s2, w4s1  -> reach gained per unit backward-DEPTH.
  TEMPERATURE (the T0.1 free lever):  w2@temp0.2 and w2s1@temp0.2 (does the free lever STACK with overlap?).
  FLAT spot-check (make_gauss, known Bayes error):  w1, w2, w4, w12, w2s1  -> does the story hold off headroom?

Pre-registered decision rules (fixed before the run):
  * OVERLAP HELPS iff w2s1 (backward-depth 2) reaches a deeper peak / higher tail-L12 than w2s2 (non-overlap, also
    depth 2).  CHEAP-CREDIT WIN iff w2s1 reaches ~w4s4's composition at HALF the backward depth (2 vs 4).
  * gradients are normalized by per-layer participation count, so overlap vs non-overlap differ ONLY in credit reach,
    not effective lr (one-thing-changed).
  * EQUIVALENCE GUARD (--quick): SCFFContrastOverlap(window=2,stride=2) must reproduce the tested
    SCFFContrastOLU(window=2) bit-for-bit -> a subclass bug can't masquerade as a result.

CHECKPOINTED + safe-launch (the OpenMP-phantom box): thread caps BEFORE numpy import, python -u, per-cell fsync
beacons, pure-numpy hot path (numpy linear probe + numpy effective_rank; NO sklearn).
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_t3.py [--quick]
"""
from __future__ import annotations
import os
# --- thread caps BEFORE numpy import (the phantom-hang guard) ---
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys, time
import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "..", "..", "draft6.0", "src")
sys.path.insert(0, os.path.join(_SRC, "phase4"))                       # p4lib
sys.path.insert(0, os.path.join(_SRC, "phase3"))                       # p3lib (SCFFContrastOLU)
sys.path.insert(0, os.path.join(_SRC, "phase2"))                       # p2lib (make_tierb, effective_rank)
from p4lib import fit_readout, readout_feats, linear_probe, make_gauss  # noqa: E402
from p3lib import SCFFContrastOLU                                      # noqa: E402
from p2lib import make_tierb, effective_rank, EPS                      # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
PROBE_EP = 60
BATCH = 32
OUT = os.path.join(_HERE, "figs_t3")


# ============================================================ the overlap cell (subclass; p3lib untouched)
class SCFFContrastOverlap(SCFFContrastOLU):
    """SCFFContrastOLU + an overlap STRIDE.  Coordination groups start every `stride` layers; each group is EXACTLY
    `window` layers deep (the last group is anchored at L-window so the top is always covered at full depth), so the
    backward DEPTH (gradient chain length, the substrate-expensive op) is always = window regardless of overlap.
    stride == window reproduces the original non-overlapping SCFFContrastOLU (guarded in --quick).  Per-layer
    gradients are divided by the layer's participation count, so overlap changes credit REACH, not effective lr."""

    def __init__(self, dims, *, stride=None, window=2, **kw):
        super().__init__(dims, window=window, **kw)
        self.stride = window if stride is None else stride

    def _starts(self):
        w = min(self.window, self.L)
        last = self.L - w
        st = list(range(0, last + 1, self.stride))
        if not st or st[-1] != last:
            st.append(last)
        return st, w

    def train_step(self, Xb, rng, neg_partner=None):
        a0 = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb); I = np.eye(B)
        # clean rep at each layer's INPUT, computed once with current (fixed) weights -> a_in[l] = input to layer l
        a_in = [a0]; ac = a0
        for l in range(self.L):
            ac = self._norm(np.maximum(ac @ self.W[l].T + self.b[l], 0.0))
            a_in.append(ac)
        gW = [np.zeros_like(Wl) for Wl in self.W]; gb = [np.zeros_like(bl) for bl in self.b]
        cnt = np.zeros(self.L)
        starts, w = self._starts()
        for s in starts:
            a = a_in[s]; din = a.shape[1]
            a1 = a * (rng.random((B, din)) >= self.mask_ratio)
            a2 = a * (rng.random((B, din)) >= self.mask_ratio)
            u1, n1, c1, ht1 = self._view_fwd(a1, s, w)
            u2, n2, c2, ht2 = self._view_fwd(a2, s, w)
            S = (u1 @ u2.T) / self.temp; P = softmax(S, axis=1); dS = (P - I) / B
            du1 = (dS @ u2) / self.temp; du2 = (dS.T @ u1) / self.temp
            self._view_bwd(du1, n1, c1, ht1, w, gW, gb, s)
            self._view_bwd(du2, n2, c2, ht2, w, gW, gb, s)
            cnt[s:s + w] += 1
        for l in range(self.L):
            scale = self.lr / max(cnt[l], 1.0)                          # lr-match: divide by participation count
            self.W[l] -= scale * gW[l]
            self.b[l] -= scale * gb[l]


def _mlp_cost(dims):                                                   # full backprop work for a small MLP
    Ln = len(dims) - 1
    return sum((Ln - l) * (dims[l] + 1) * dims[l + 1] for l in range(Ln))


def cost_overlap(D, Wd, Lb, window, stride, C, readout_last_n=1):
    """(total backward WORK, max backward DEPTH).  Depth = the gradient chain length (substrate-expensive) = window.
    Work = sum over groups, over layers in group, of window*(din+1)*dout (each group backprops `window` deep)."""
    dims = [D] + [Wd] * Lb
    w = min(window, Lb); last = Lb - w
    starts = list(range(0, last + 1, stride))
    if not starts or starts[-1] != last:
        starts.append(last)
    bulk = 0
    for s in starts:
        for j in range(w):
            l = s + j
            bulk += w * (dims[l] + 1) * dims[l + 1]
    readout = _mlp_cost([min(readout_last_n, Lb) * Wd, 32, C])
    return bulk + readout, w


# ============================================================ tasks
def make_headroom(n, seed):
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def make_flat(n, seed):
    X, Y, _ = make_gauss(n, np.random.default_rng(seed), dim=DIM, n_class=NCLASS)
    return X, Y


# ============================================================ cells
def CELL(tag, task="headroom", window=2, stride=None, temp=0.5, mask=0.5, lr=0.03, ep=25):
    return dict(tag=tag, task=task, window=window, stride=window if stride is None else stride,
                temp=temp, mask=mask, lr=lr, ep=ep)


CELLS = [
    # --- headroom: locality dose-response (non-overlap) ---
    CELL("h_w1", window=1), CELL("h_w2", window=2), CELL("h_w3", window=3),
    CELL("h_w4", window=4), CELL("h_w6", window=6), CELL("h_w12", window=12),
    # --- headroom: OVERLAP (extend reach at bounded backward depth) ---
    CELL("h_w2s1", window=2, stride=1), CELL("h_w3s1", window=3, stride=1),
    CELL("h_w4s2", window=4, stride=2), CELL("h_w4s1", window=4, stride=1),
    # --- headroom: TEMPERATURE (the T0.1 free lever, alone and stacked with overlap) ---
    CELL("h_w2_t02", window=2, temp=0.2), CELL("h_w2s1_t02", window=2, stride=1, temp=0.2),
    # --- FLAT spot-check (make_gauss, known Bayes error) ---
    CELL("f_w1", task="flat", window=1), CELL("f_w2", task="flat", window=2),
    CELL("f_w4", task="flat", window=4), CELL("f_w12", task="flat", window=12),
    CELL("f_w2s1", task="flat", window=2, stride=1),
]
QUICK = ["h_w2", "h_w2s1", "h_w12", "f_w2"]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def train_cell(Xtr, cfg, seed):
    dims = [DIM] + [W] * L
    m = SCFFContrastOverlap(dims, lr=cfg["lr"], seed=seed, window=cfg["window"], stride=cfg["stride"],
                            mask_ratio=cfg["mask"], temp=cfg["temp"])
    rng = np.random.default_rng(seed)
    for _ in range(cfg["ep"]):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_cell(cfg, seed):
    mk = make_flat if cfg["task"] == "flat" else make_headroom
    Xtr, Ytr = mk(NTR, seed + 1); Xte, Yte = mk(NTE, seed + 2)
    m = train_cell(Xtr, cfg, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP)
             for rt, re in zip(reps_tr, reps_te)]
    dead = [float(x) for x in m.dead_fraction(Xte)]
    erank = [float(effective_rank(r)) for r in reps_te]
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed)
    acc_last = float((ro.predict(Fte) == Yte).mean())
    work, depth = cost_overlap(DIM, W, L, cfg["window"], cfg["stride"], NCLASS, 1)
    return dict(tag=cfg["tag"], task=cfg["task"], window=cfg["window"], stride=cfg["stride"],
                temp=cfg["temp"], mask=cfg["mask"], lr=cfg["lr"], ep=cfg["ep"], seed=seed,
                probe=[float(p) for p in probe], dead=dead, erank=erank, acc_last=acc_last,
                bwd_work=int(work), bwd_depth=int(depth), nan=bool(np.any(~np.isfinite(probe))))


def rkey(r):
    return (r["tag"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[rkey(r)] = r
    return done


def _med(rows, key):
    return np.median(np.array([r[key] for r in rows]), axis=0)


def _peak(pr):
    return int(np.argmax(pr)) + 1


def equivalence_guard():
    """SCFFContrastOverlap(window=2,stride=2) must reproduce the tested SCFFContrastOLU(window=2) bit-for-bit."""
    Xtr, _ = make_headroom(400, 7)
    dims = [DIM] + [W] * L
    ref = SCFFContrastOLU(dims, lr=0.03, seed=3, window=2, mask_ratio=0.5, temp=0.5)
    new = SCFFContrastOverlap(dims, lr=0.03, seed=3, window=2, stride=2, mask_ratio=0.5, temp=0.5)
    r1 = np.random.default_rng(11); r2 = np.random.default_rng(11)
    for _ in range(4):
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[s:s + BATCH]
            if len(xb) >= 4:
                ref.train_step(xb, r1); new.train_step(xb, r2)
    d = max(float(np.abs(ref.W[l] - new.W[l]).max()) for l in range(L))
    print(f"  [equivalence guard] max|W_ref - W_overlap(stride=window)| = {d:.2e}  "
          f"{'OK' if d < 1e-9 else '!! MISMATCH — subclass bug'}", flush=True)
    assert d < 1e-9, "overlap subclass does not reproduce SCFFContrastOLU at stride=window"


def main():
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    cells = [c for c in CELLS if c["tag"] in QUICK] if quick else CELLS
    os.makedirs(OUT, exist_ok=True)
    if quick:
        equivalence_guard()
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== T3 cheap-credit | {len(cells)} cells | seeds {seeds} | L{L} W{W} | {len(done)} cached ===",
          flush=True)
    fck = open(ckpt, "a")
    for cfg in cells:
        for s in seeds:
            if (cfg["tag"], s) in done:
                continue
            r = run_cell(cfg, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {cfg['tag']:12s} seed {s}: peak@L{_peak(r['probe']):>2} ({max(r['probe']):.3f})  "
                  f"tailL12 {r['probe'][-1]:.3f}  acc {r['acc_last']:.3f}  bwd_depth {r['bwd_depth']:>2} "
                  f"work {r['bwd_work']:>9}{'  [NAN]' if r['nan'] else ''}", flush=True)
    fck.close()

    rows = list(done.values())
    save = {"seeds": np.array(seeds), "L": L, "W": W}
    print(f"\n--- T3 SUMMARY (median over n={len(seeds)}) ---")
    hdr = f"  {'cfg':12s} {'task':8s} {'w':>2} {'str':>3} {'temp':>4} {'peak@L':>6} {'peak':>6} " \
          f"{'tailL12':>7} {'slope':>8} {'acc':>5} {'bwd_d':>5} {'work/w1':>7}"
    print(hdr)
    w1work = None
    for cfg in cells:
        rs = [r for r in rows if r["tag"] == cfg["tag"]]
        if not rs:
            continue
        pr = _med(rs, "probe"); pk = _peak(pr)
        slope = float((pr[-1] - pr[0]) / (len(pr) - 1))
        bd = rs[0]["bwd_depth"]; wk = rs[0]["bwd_work"]
        if cfg["tag"] == "h_w1":
            w1work = wk
        wr = (wk / w1work) if w1work else float("nan")
        save[f"{cfg['tag']}_probe"] = pr; save[f"{cfg['tag']}_peak"] = pk
        save[f"{cfg['tag']}_work"] = wk; save[f"{cfg['tag']}_depth"] = bd
        print(f"  {cfg['tag']:12s} {cfg['task']:8s} {cfg['window']:>2} {cfg['stride']:>3} {cfg['temp']:>4} "
              f"{pk:>6} {float(np.max(pr)):>6.3f} {float(pr[-1]):>7.3f} {slope:>+8.4f} "
              f"{float(np.median([r['acc_last'] for r in rs])):>5.3f} {bd:>5} {wr:>7.2f}")

    # pre-registered comparisons
    def tail(tag):
        return float(save[f"{tag}_probe"][-1]) if f"{tag}_probe" in save else float("nan")

    def peak(tag):
        return int(save.get(f"{tag}_peak", -1))
    print("\n  >> OVERLAP test (does stride<window extend reach at bounded backward depth?)")
    print(f"     w2s2 (non-overlap, depth2): peak@L{peak('h_w2')} tail {tail('h_w2'):.3f}")
    print(f"     w2s1 (overlap,    depth2): peak@L{peak('h_w2s1')} tail {tail('h_w2s1'):.3f}   "
          f"-> overlap HELPS if deeper/higher than w2s2")
    print(f"     w4s4 (non-overlap, depth4): peak@L{peak('h_w4')} tail {tail('h_w4'):.3f}")
    print(f"     CHEAP-CREDIT WIN if w2s1 (depth2) ~ reaches w4s4 (depth4)")
    print(f"     w12  (full e2e, depth12, UPPER BOUND): peak@L{peak('h_w12')} tail {tail('h_w12'):.3f}")
    print(f"  >> TEMP free lever: w2 {tail('h_w2'):.3f} -> w2@t0.2 {tail('h_w2_t02'):.3f} ; "
          f"stacked w2s1@t0.2 {tail('h_w2s1_t02'):.3f}")

    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in save.items()})
    json.dump({"experiment": "t3_cheap_credit", "git_commit": _git(), "seeds": list(seeds),
               "L": L, "W": W, "dim": DIM, "n_class": NCLASS, "probe_ep": PROBE_EP,
               "cells": [c["tag"] for c in cells], "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
