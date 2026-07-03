"""
T3.2 — objective-side global credit: a detached TOP-DOWN consistency term in the local InfoNCE (`lambda_topdown`).

The deep-lit pass (temp/ref/lit-cheap-credit.md) found the cheapest flow-safe global-credit lever is NOT a wire (DFA)
nor wider windows (T3.1) but the LOCAL OBJECTIVE: add to each layer's loss a term that rewards keeping the class
structure the rest of the stack needs (CLAPP predictive term + InfoPro principle; 2601.21683 reaches BP-SSL parity by
fixing the local update, not by adding wiring). Phase-3-correct twist: the preserved quantity is the CLASS DIRECTION
(a contrastive consistency term), NEVER reconstruction (Phase 3 rejected recon: preserves density, not class).

MECHANISM (per layer l, gradient-isolated, backward DEPTH = 1 — the CHEAPEST possible):
  input a_l  = detached clean rep from below (standard greedy).
  two masked views -> embeddings u1,u2 (L2-normalized relu activations).   LOCAL term  = InfoNCE(u1,u2).
  reference g = DETACHED L2-normalized clean embedding of a reference layer R (R = top L-1, or R = l+1 "next").
  TOP-DOWN term = InfoNCE(u1,g) + InfoNCE(u2,g)   (pull layer l's views toward R's discriminative structure).
  loss_l = LOCAL + lambda * TOP-DOWN ;  update W_l,b_l by its gradient.
Flow-safe BY CONSTRUCTION: the top-down term changes only the weight gradient; the clean rep that PROPAGATES to l+1
is untouched (no stream rewrite). g is detached -> no deep backward chain -> stays depth-1 (cheap on the substrate).

This isolates global credit from the window: window=1 is the MOST-local, MOST-decayed baseline (peak ~L3), so any lift
is PURE top-down credit at depth-1 cost. Two reference directions are tested (anchor-to-top vs predict-next) and the
DATA picks — no freelanced sign. Pre-registered rules:
  * TOP-DOWN COMPOSES iff some lambda>0 lifts peak-depth and/or tail-L12 above lambda=0 (= w1).
  * CHEAP-CREDIT WIN (the prize) iff a depth-1 top-down cell reaches what bounded windows (w4 depth-4, T3.1) reach,
    or approaches the w12 ceiling -> global credit at the cheapest possible cost.
  * If all lambda>0 <= lambda=0 -> top-down-contrast does NOT compose (anchor-to-decayed-top failure) -> fall back to
    the bounded window (T3.1) / DFA (T3.3).

GUARDS (the antidote to this project's recurring sign/direction bug):
  (1) FINITE-DIFFERENCE gradient check on _layer_grads (analytic vs central-difference, fixed masks) < 1e-5.
  (2) lambda=0 must reproduce SCFFContrastOLU(window=1) bit-for-bit (same masks, same accumulate-then-step timing).

Safe-launch (OpenMP-phantom box): thread caps BEFORE numpy, python -u, fsync beacons, pure-numpy, NO sklearn.
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_topdown.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys, time
import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "..", "..", "draft6.0", "src")
sys.path.insert(0, os.path.join(_SRC, "phase4"))
sys.path.insert(0, os.path.join(_SRC, "phase3"))
sys.path.insert(0, os.path.join(_SRC, "phase2"))
from p4lib import fit_readout, readout_feats, linear_probe, make_gauss   # noqa: E402
from p3lib import SCFFContrastOLU                                       # noqa: E402
from p2lib import make_tierb, effective_rank, normalize, relu, EPS      # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
PROBE_EP = 60
BATCH = 32
OUT = os.path.join(_HERE, "figs_topdown")


# ============================================================ the InfoNCE + top-down layer gradient (FD-checkable)
def _l2(h):
    n = np.linalg.norm(h, axis=1, keepdims=True) + EPS
    return h / n, n


def _nce_diag(S):
    """InfoNCE loss + dL/dS for positives on the diagonal. L = -mean_i log softmax(S)[i,i]."""
    B = S.shape[0]; P = softmax(S, axis=1)
    L = float(-np.mean(np.log(P[np.arange(B), np.arange(B)] + 1e-12)))
    return L, (P - np.eye(B)) / B


def _l2_vjp(du, u, n):
    """grad wrt h, for u = h/n (row L2-norm): dh = (du - u*<u,du>)/n."""
    return (du - u * (u * du).sum(1, keepdims=True)) / n


def _layer_grads(a, W, b, mask1, mask2, g, lam, temp):
    """Return (loss, gW, gb) for one gradient-isolated layer with the local two-view InfoNCE PLUS a detached
    top-down consistency term (weight `lam`) toward reference embedding `g` (already L2-normalized, detached).
    `a` (layer input), `g`, and the masks are detached/fixed -> backward depth = 1. Used by both train_step and
    the finite-difference check (with fixed masks)."""
    a1 = a * mask1; a2 = a * mask2
    z1 = a1 @ W.T + b; h1 = relu(z1); u1, n1 = _l2(h1)
    z2 = a2 @ W.T + b; h2 = relu(z2); u2, n2 = _l2(h2)
    # local two-view InfoNCE (both views differentiated) — matches SCFFContrast
    Sloc = (u1 @ u2.T) / temp
    Lloc, dSloc = _nce_diag(Sloc)
    du1 = (dSloc @ u2) / temp
    du2 = (dSloc.T @ u1) / temp
    loss = Lloc
    # top-down consistency: each view's embedding contrasts against the DETACHED reference g (positives diagonal)
    if lam != 0.0 and g is not None:
        St1 = (u1 @ g.T) / temp; Lt1, dSt1 = _nce_diag(St1); du1 = du1 + lam * ((dSt1 @ g) / temp)
        St2 = (u2 @ g.T) / temp; Lt2, dSt2 = _nce_diag(St2); du2 = du2 + lam * ((dSt2 @ g) / temp)
        loss = loss + lam * (Lt1 + Lt2)
    # backward each view through L2-norm -> relu -> linear, on its OWN masked input
    dz1 = _l2_vjp(du1, u1, n1) * (z1 > 0)
    dz2 = _l2_vjp(du2, u2, n2) * (z2 > 0)
    gW = dz1.T @ a1 + dz2.T @ a2
    gb = dz1.sum(0) + dz2.sum(0)
    return loss, gW, gb


class TopDownContrast:
    """Per-layer InfoNCE (window=1, gradient-isolated, layer-norm propagation — identical forward/infer to
    SCFFContrastOLU) + a detached top-down consistency term. `ref` in {"top","next"}; `lam` weights it. lam=0
    == SCFFContrastOLU(window=1)."""

    def __init__(self, dims, *, lr=0.03, seed=0, mask_ratio=0.5, temp=0.5, lam=0.0, ref="top",
                 normalize_input=True):
        rng = np.random.default_rng(seed)
        self.W = [rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i])) for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.lr = lr; self.mask_ratio = mask_ratio; self.temp = temp
        self.lam = lam; self.ref = ref; self.normalize_input = normalize_input
        self.L = len(self.W)

    def _norm(self, a):
        return normalize(a, "layernorm")

    def infer(self, X):
        a = self._norm(X) if self.normalize_input else X
        reps = []
        for Wl, bl in zip(self.W, self.b):
            a = self._norm(relu(a @ Wl.T + bl)); reps.append(a)
        return reps

    def dead_fraction(self, X):
        a = self._norm(X) if self.normalize_input else X
        fr = []
        for Wl, bl in zip(self.W, self.b):
            h = relu(a @ Wl.T + bl); fr.append(float((h.max(0) <= EPS).mean())); a = self._norm(h)
        return np.array(fr)

    def _clean_reps(self, Xb):
        """clean rep at each layer INPUT (a_in[l]) + each layer OUTPUT (a_out[l] = layernorm rep), current weights."""
        a = self._norm(Xb) if self.normalize_input else Xb
        a_in = [a]; a_out = []
        for Wl, bl in zip(self.W, self.b):
            a = self._norm(relu(a @ Wl.T + bl)); a_out.append(a); a_in.append(a)
        return a_in, a_out

    def train_step(self, Xb, rng, lam=None):
        lam = self.lam if lam is None else lam
        B = len(Xb)
        a_in, a_out = self._clean_reps(Xb)                              # detached references (current weights)
        gW = [np.zeros_like(Wl) for Wl in self.W]; gb = [np.zeros_like(bl) for bl in self.b]
        for l in range(self.L):
            a = a_in[l]; din = a.shape[1]
            m1 = (rng.random((B, din)) >= self.mask_ratio).astype(a.dtype)
            m2 = (rng.random((B, din)) >= self.mask_ratio).astype(a.dtype)
            if lam != 0.0:
                R = self.L - 1 if self.ref == "top" else min(l + 1, self.L - 1)
                g, _ = _l2(a_out[R])                                    # detached L2-normalized reference embedding
            else:
                g = None
            _, gWl, gbl = _layer_grads(a, self.W[l], self.b[l], m1, m2, g, lam, self.temp)
            gW[l] = gWl; gb[l] = gbl
        for l in range(self.L):
            self.W[l] -= self.lr * gW[l]; self.b[l] -= self.lr * gb[l]


# ============================================================ guards
def fd_check():
    """central-difference vs analytic gradient of _layer_grads (fixed masks, fixed detached g)."""
    rng = np.random.default_rng(0)
    B, din, dout = 16, 10, 8
    a = rng.normal(size=(B, din)); W = rng.normal(size=(dout, din)) * 0.3; b = rng.normal(size=dout) * 0.1
    m1 = (rng.random((B, din)) >= 0.5).astype(float); m2 = (rng.random((B, din)) >= 0.5).astype(float)
    g, _ = _l2(rng.normal(size=(B, dout)))
    lam, temp = 0.7, 0.5
    _, gW, gb = _layer_grads(a, W, b, m1, m2, g, lam, temp)
    eps = 1e-6; errW = 0.0
    for i in range(dout):
        for j in range(din):
            Wp = W.copy(); Wp[i, j] += eps; Lp, _, _ = _layer_grads(a, Wp, b, m1, m2, g, lam, temp)
            Wm = W.copy(); Wm[i, j] -= eps; Lm, _, _ = _layer_grads(a, Wm, b, m1, m2, g, lam, temp)
            errW = max(errW, abs((Lp - Lm) / (2 * eps) - gW[i, j]))
    errb = 0.0
    for i in range(dout):
        bp = b.copy(); bp[i] += eps; Lp, _, _ = _layer_grads(a, W, bp, m1, m2, g, lam, temp)
        bm = b.copy(); bm[i] -= eps; Lm, _, _ = _layer_grads(a, W, bm, m1, m2, g, lam, temp)
        errb = max(errb, abs((Lp - Lm) / (2 * eps) - gb[i]))
    ok = errW < 1e-5 and errb < 1e-5
    print(f"  [FD grad check] max|analytic-FD|  W {errW:.2e}  b {errb:.2e}  {'OK' if ok else '!! GRADIENT BUG'}",
          flush=True)
    assert ok, "top-down layer gradient fails finite-difference check"


def lam0_equivalence():
    """lambda=0 TopDownContrast must reproduce SCFFContrastOLU(window=1) bit-for-bit."""
    Xtr, _ = make_headroom(400, 7)
    dims = [DIM] + [W] * L
    ref = SCFFContrastOLU(dims, lr=0.03, seed=3, window=1, mask_ratio=0.5, temp=0.5)
    new = TopDownContrast(dims, lr=0.03, seed=3, mask_ratio=0.5, temp=0.5, lam=0.0)
    r1 = np.random.default_rng(11); r2 = np.random.default_rng(11)
    for _ in range(4):
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[s:s + BATCH]
            if len(xb) >= 4:
                ref.train_step(xb, r1); new.train_step(xb, r2)
    d = max(float(np.abs(ref.W[l] - new.W[l]).max()) for l in range(L))
    print(f"  [lam=0 equivalence] max|W_w1 - W_td(lam0)| = {d:.2e}  "
          f"{'OK' if d < 1e-9 else '!! lam=0 != window-1'}", flush=True)
    assert d < 1e-9, "TopDownContrast(lam=0) does not reproduce SCFFContrastOLU(window=1)"


# ============================================================ tasks / cells
def make_headroom(n, seed):
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def make_flat(n, seed):
    X, Y, _ = make_gauss(n, np.random.default_rng(seed), dim=DIM, n_class=NCLASS)
    return X, Y


def CELL(tag, task="headroom", lam=0.0, ref="top", temp=0.5, warm=False, ep=25):
    return dict(tag=tag, task=task, lam=lam, ref=ref, temp=temp, warm=warm, ep=ep)


CELLS = [
    CELL("td_off"),                                       # lambda=0 == w1 (cross-check)
    CELL("td_top_l05", lam=0.5, ref="top"),
    CELL("td_top_l10", lam=1.0, ref="top"),
    CELL("td_next_l05", lam=0.5, ref="next"),
    CELL("td_next_l10", lam=1.0, ref="next"),
    CELL("td_top_l10_warm", lam=1.0, ref="top", warm=True),   # warmup: addresses random-top bootstrap poisoning
    CELL("f_td_off", task="flat"),
    CELL("f_td_top_l10", task="flat", lam=1.0, ref="top"),
]
QUICK = ["td_off", "td_top_l10", "td_next_l10"]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def train_cell(Xtr, cfg, seed):
    m = TopDownContrast([DIM] + [W] * L, lr=0.03, seed=seed, mask_ratio=0.5, temp=cfg["temp"],
                        lam=cfg["lam"], ref=cfg["ref"])
    rng = np.random.default_rng(seed)
    for e in range(cfg["ep"]):
        lam = cfg["lam"] * min(1.0, 2.0 * e / cfg["ep"]) if cfg["warm"] else cfg["lam"]   # ramp over first half
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng, lam=lam)
    return m


def run_cell(cfg, seed):
    mk = make_flat if cfg["task"] == "flat" else make_headroom
    Xtr, Ytr = mk(NTR, seed + 1); Xte, Yte = mk(NTE, seed + 2)
    m = train_cell(Xtr, cfg, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP) for rt, re in zip(reps_tr, reps_te)]
    dead = [float(x) for x in m.dead_fraction(Xte)]
    erank = [float(effective_rank(r)) for r in reps_te]
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed)
    acc_last = float((ro.predict(Fte) == Yte).mean())
    return dict(tag=cfg["tag"], task=cfg["task"], lam=cfg["lam"], ref=cfg["ref"], temp=cfg["temp"],
                warm=cfg["warm"], seed=seed, probe=[float(p) for p in probe], dead=dead, erank=erank,
                acc_last=acc_last, bwd_depth=1, nan=bool(np.any(~np.isfinite(probe))))


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


def main():
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    cells = [c for c in CELLS if c["tag"] in QUICK] if quick else CELLS
    os.makedirs(OUT, exist_ok=True)
    fd_check(); lam0_equivalence()                                     # guards ALWAYS run
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== T3.2 top-down credit | {len(cells)} cells | seeds {seeds} | L{L} W{W} (window=1 base) | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for cfg in cells:
        for s in seeds:
            if (cfg["tag"], s) in done:
                continue
            r = run_cell(cfg, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {cfg['tag']:16s} seed {s}: peak@L{_peak(r['probe']):>2} ({max(r['probe']):.3f})  "
                  f"tailL12 {r['probe'][-1]:.3f}  acc {r['acc_last']:.3f}"
                  f"{'  [NAN]' if r['nan'] else ''}", flush=True)
    fck.close()

    rows = list(done.values())
    save = {"seeds": np.array(seeds), "L": L, "W": W}
    print(f"\n--- T3.2 SUMMARY (median over n={len(seeds)}; window=1 base, backward depth=1) ---")
    print(f"  {'cfg':16s} {'task':8s} {'lam':>4} {'ref':>5} {'peak@L':>6} {'peak':>6} {'tailL12':>7} "
          f"{'slope':>8} {'acc':>5}")
    for cfg in cells:
        rs = [r for r in rows if r["tag"] == cfg["tag"]]
        if not rs:
            continue
        pr = _med(rs, "probe"); pk = _peak(pr); slope = float((pr[-1] - pr[0]) / (len(pr) - 1))
        save[f"{cfg['tag']}_probe"] = pr; save[f"{cfg['tag']}_peak"] = pk
        print(f"  {cfg['tag']:16s} {cfg['task']:8s} {cfg['lam']:>4.1f} {cfg['ref']:>5} {pk:>6} "
              f"{float(np.max(pr)):>6.3f} {float(pr[-1]):>7.3f} {slope:>+8.4f} "
              f"{float(np.median([r['acc_last'] for r in rs])):>5.3f}")

    def tail(t):
        return float(save[f"{t}_probe"][-1]) if f"{t}_probe" in save else float("nan")

    def pk(t):
        return int(save.get(f"{t}_peak", -1))
    print("\n  >> PRE-REGISTERED: top-down COMPOSES iff lam>0 lifts peak-depth/tail above lam=0 (w1).")
    print(f"     lam=0 (w1)          : peak@L{pk('td_off')} tail {tail('td_off'):.3f}")
    print(f"     top  lam0.5/1.0     : peak@L{pk('td_top_l05')}/{pk('td_top_l10')} "
          f"tail {tail('td_top_l05'):.3f}/{tail('td_top_l10'):.3f}")
    print(f"     next lam0.5/1.0     : peak@L{pk('td_next_l05')}/{pk('td_next_l10')} "
          f"tail {tail('td_next_l05'):.3f}/{tail('td_next_l10'):.3f}")
    print(f"     top lam1.0 +warmup  : peak@L{pk('td_top_l10_warm')} tail {tail('td_top_l10_warm'):.3f}")
    print(f"  >> CHEAP-CREDIT WIN if any depth-1 cell ~ reaches w4 (T3 h_w4, depth-4) or the w12 ceiling.")

    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in save.items()})
    json.dump({"experiment": "t3_2_topdown_credit", "git_commit": _git(), "seeds": list(seeds),
               "L": L, "W": W, "dim": DIM, "n_class": NCLASS, "probe_ep": PROBE_EP,
               "cells": [c["tag"] for c in cells], "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
