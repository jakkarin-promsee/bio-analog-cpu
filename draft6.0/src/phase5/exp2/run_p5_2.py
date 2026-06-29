"""
P5.2 — credit reach: does temperature suffice, or do we need the bounded window? (design.md §3 P5.2, trimmed).

Inheriting the committed temp=0.2 (P5.1), this rung asks: how much composing depth does adding a bounded coordination
WINDOW buy on top of the sharp objective — and does it close the residual 0.026 to the w12 ceiling?

  * the cheap closer: temp0.2 x window {2,3,4} on headroom + flat + mixed (w2 = the P5.1 temp0.2 baseline).
  * the temp0.2 objective ceiling: temp0.2 x w12 on headroom (full e2e credit at the sharp temp — the best the
    temp0.2 objective can do; distinguishes "objective can't" from "window too short").
  * re-confirm the struck OVERLAP negative at temp0.2: headroom w4-stride2 (overlap) vs w4-stride4 (non-overlap) —
    T3 struck overlap at temp0.5 (chain LENGTH composes, not path MULTIPLICITY); does it stay struck at temp0.2?
  (The naive top-down negative was struck FD-verified in T3 and is a NEW backward path — NOT rebuilt here; it
   re-opens only if a real gap to w12 survives, per the pre-registered Track-C rule. Logged, not re-run.)

References (w12@temp0.5 ceiling, w2@temp0.5 baseline, tuned-BP) carried from P5.0. Guards re-run first.
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_2.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
from p5lib import (SCFFContrastOverlap, cost_overlap, make_headroom, make_flat, make_mixed,    # noqa: E402
                   equivalence_guard, fd_gradient_check, mean_infonce_loss,
                   fit_readout, readout_feats, linear_probe, effective_rank)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH, TEMP = 25, 32, 0.2
PROBE_EP = 120
WINDOWS = [2, 3, 4]
TASKS = ["headroom", "flat", "mixed"]
OUT = os.path.join(_HERE, "figs_p5_2")
P50 = os.path.join(_HERE, "..", "exp0", "figs_p5_0", "arrays.npz")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _make(task, n, seed):
    if task == "headroom":
        X, Y = make_headroom(n, seed); return X, Y, None
    if task == "flat":
        X, Y, _ = make_flat(n, seed); return X, Y, None
    X, Y, m = make_mixed(n, seed); return X, Y, m


def train(Xtr, window, stride, seed, trace=False):
    m = SCFFContrastOverlap([DIM] + [W] * L, lr=0.03, seed=seed, window=window, stride=stride,
                            mask_ratio=0.5, temp=TEMP)
    rng = np.random.default_rng(seed); Xheld = Xtr[:256]; lrng = np.random.default_rng(seed + 555); tr = []
    for _ in range(EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
        if trace:
            tr.append(mean_infonce_loss(m, Xheld, lrng))
    return m, [float(x) for x in tr]


def run_cell(cfg, seed):
    task = cfg["task"]
    Xtr, Ytr, mtr = _make(task, NTR, seed + 1); Xte, Yte, mte = _make(task, NTE, seed + 2)
    is_inv = (cfg["tag"] == "headroom_w4")                            # INV reference cell carries the loss trace
    m, trace = train(Xtr, cfg["window"], cfg["stride"], seed, trace=is_inv)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    work, depth = cost_overlap(DIM, W, L, cfg["window"], cfg["stride"], NCLASS, 1)
    base = dict(tag=cfg["tag"], task=task, window=cfg["window"], stride=cfg["stride"], seed=seed,
                bwd_work=int(work), bwd_depth=int(depth), losstrace=trace,
                dead=[float(x) for x in m.dead_fraction(Xte)],
                erank=[float(effective_rank(r)) for r in reps_te])
    if task == "mixed":
        ftr, fte = mtr["flat"], mte["flat"]; htr, hte = mtr["head"], mte["head"]
        pf = [linear_probe(rt[ftr], Ytr[ftr], re[fte], Yte[fte], NCLASS, seed, epochs=PROBE_EP)
              for rt, re in zip(reps_tr, reps_te)]
        ph = [linear_probe(rt[htr], Ytr[htr] - NCLASS, re[hte], Yte[hte] - NCLASS, NCLASS, seed, epochs=PROBE_EP)
              for rt, re in zip(reps_tr, reps_te)]
        ro = fit_readout(readout_feats(reps_tr, 1), Ytr, 2 * NCLASS, seed); pred = ro.predict(readout_feats(reps_te, 1))
        base.update(probe_flat=[float(p) for p in pf], probe_head=[float(p) for p in ph],
                    readout_flat=float((pred[fte] == Yte[fte]).mean()),
                    readout_head=float((pred[hte] == Yte[hte]).mean()), nan=bool(np.any(~np.isfinite(pf + ph))))
    else:
        probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP) for rt, re in zip(reps_tr, reps_te)]
        ro = fit_readout(readout_feats(reps_tr, 1), Ytr, NCLASS, seed)
        base.update(probe=[float(p) for p in probe],
                    readout=float((ro.predict(readout_feats(reps_te, 1)) == Yte).mean()),
                    nan=bool(np.any(~np.isfinite(probe))))
    return base


def build_cells():
    cells = []
    for task in TASKS:
        for w in WINDOWS:
            cells.append(dict(tag=f"{task}_w{w}", task=task, window=w, stride=w))
    cells.append(dict(tag="headroom_w12", task="headroom", window=12, stride=12))     # temp0.2 objective ceiling
    cells.append(dict(tag="headroom_w4s2", task="headroom", window=4, stride=2))      # overlap re-confirmation
    return cells


def rkey(r):
    return (r["tag"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rkey(rr)] = rr
    return done


def main():
    global PROBE_EP, OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    PROBE_EP = 40 if quick else 120
    OUT = os.path.join(_HERE, "figs_p5_2_quick" if quick else "figs_p5_2")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.2 guards (pre-cell) ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    cells = build_cells()
    if quick:
        cells = [c for c in cells if c["task"] == "headroom"]
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.2 cells (temp={TEMP}) | {len(cells)} cells x seeds {seeds} | PROBE_EP={PROBE_EP} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for cfg in cells:
        for s in seeds:
            if (cfg["tag"], s) in done:
                continue
            r = run_cell(cfg, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            tail = (r["probe_flat"] if cfg["task"] == "mixed" else r["probe"])[-1]
            pk = int(np.argmax(r["probe_flat"] if cfg["task"] == "mixed" else r["probe"])) + 1
            print(f"  {cfg['tag']:16s} seed {s}: peak@L{pk:>2} tail {tail:.3f}  bwd_depth {r['bwd_depth']:>2} "
                  f"work {r['bwd_work']:>7}{'  [NAN]' if r.get('nan') else ''}", flush=True)
    fck.close()

    def tail_of(rec):
        return (rec["probe_flat"] if rec["task"] == "mixed" else rec["probe"])[-1]

    def ro_of(rec):
        return rec["readout_flat"] if rec["task"] == "mixed" else rec["readout"]

    def prof_of(rec):
        return rec["probe_flat"] if rec["task"] == "mixed" else rec["probe"]

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, probe_ep=PROBE_EP, temp=TEMP,
                windows=np.array(WINDOWS), inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_deadfrac=np.array([done[("headroom_w4", s)]["dead"] for s in seeds]),
                inv_erank=np.array([done[("headroom_w4", s)]["erank"] for s in seeds]),
                inv_losstrace=np.array([done[("headroom_w4", s)]["losstrace"] for s in seeds]))
    for task in TASKS:
        if not all((f"{task}_w{w}", s) in done for w in WINDOWS for s in seeds):
            continue
        save[f"{task}_w_tail"] = np.array([[tail_of(done[(f"{task}_w{w}", s)]) for w in WINDOWS] for s in seeds])
        save[f"{task}_w_readout"] = np.array([[ro_of(done[(f"{task}_w{w}", s)]) for w in WINDOWS] for s in seeds])
        save[f"{task}_w_peakL"] = np.array([[int(np.argmax(prof_of(done[(f"{task}_w{w}", s)]))) + 1
                                             for w in WINDOWS] for s in seeds])
        save[f"{task}_w_probe"] = np.array([[prof_of(done[(f"{task}_w{w}", s)]) for w in WINDOWS] for s in seeds])
        save[f"{task}_w_work"] = np.array([done[(f"{task}_w{w}", seeds[0])]["bwd_work"] for w in WINDOWS])
    if all(("headroom_w12", s) in done for s in seeds):
        save["hr_w12_tail"] = np.array([tail_of(done[("headroom_w12", s)]) for s in seeds])
        save["hr_w12_readout"] = np.array([ro_of(done[("headroom_w12", s)]) for s in seeds])
        save["hr_w12_probe"] = np.array([prof_of(done[("headroom_w12", s)]) for s in seeds])
        save["hr_w12_work"] = int(done[("headroom_w12", seeds[0])]["bwd_work"])
    if all(("headroom_w4s2", s) in done for s in seeds):
        save["hr_w4s2_tail"] = np.array([tail_of(done[("headroom_w4s2", s)]) for s in seeds])
        save["hr_w4s2_readout"] = np.array([ro_of(done[("headroom_w4s2", s)]) for s in seeds])
        save["hr_w4s2_work"] = int(done[("headroom_w4s2", seeds[0])]["bwd_work"])
    if os.path.exists(P50):
        p = dict(np.load(P50))
        save["ref_w12t05_tail"] = float(np.median(p["hr_probe_w12"][:, -1]))     # w12 @ temp0.5 (P5.0 ceiling)
        save["ref_w12t05_ro"] = float(np.median(p["hr_ro_w12"]))
        save["ref_bp"] = float(np.median(p["hr_bp"]))
        save["ref_w2t05_tail"] = float(np.median(p["hr_probe_w2"][:, -1]))       # w2 @ temp0.5 baseline
    np.savez(os.path.join(OUT, "arrays.npz"), **save)
    json.dump(dict(experiment="p5_2_credit_reach", git_commit=_git(), seeds=list(seeds), L=L, W=W, dim=DIM,
                   n_class=NCLASS, probe_ep=PROBE_EP, temp=TEMP, windows=WINDOWS,
                   guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    # ---- the Reads (pre-registered gap rule) ----
    print(f"\n--- P5.2 READS (n={len(seeds)}, headroom, temp={TEMP}) ---")
    hrt = np.median(save["headroom_w_tail"], 0); hrr = np.median(save["headroom_w_readout"], 0)
    for i, w in enumerate(WINDOWS):
        print(f"  w{w}: tail-L12 {hrt[i]:.3f}  readout {hrr[i]:.3f}  peak@L{int(np.median(save['headroom_w_peakL'][:, i]))}"
              f"  work {save['headroom_w_work'][i]}")
    if "hr_w12_tail" in save:
        print(f"  w12 (temp0.2 objective ceiling): tail {np.median(save['hr_w12_tail']):.3f}  "
              f"readout {np.median(save['hr_w12_readout']):.3f}  work {save['hr_w12_work']}")
    if "ref_w12t05_tail" in save:
        print(f"  refs: w12@temp0.5 tail {save['ref_w12t05_tail']:.3f} (ro {save['ref_w12t05_ro']:.3f})  "
              f"tuned-BP {save['ref_bp']:.3f}  w2@temp0.5 baseline {save['ref_w2t05_tail']:.3f}")
        gap_w4 = save["ref_w12t05_tail"] - hrt[WINDOWS.index(4)]
        print(f"  >> RESIDUAL: temp0.2×w4 tail {hrt[WINDOWS.index(4)]:.3f} vs w12@temp0.5 {save['ref_w12t05_tail']:.3f}"
              f"  -> gap {gap_w4:+.3f}  ({'CLOSED (≤0.02)' if abs(gap_w4) <= 0.02 else 'residual survives -> P5.2 read'})")
    if "hr_w4s2_tail" in save:
        ov = float(np.median(save["hr_w4s2_tail"])); w4 = hrt[WINDOWS.index(4)]
        print(f"  >> OVERLAP re-confirm: w4-stride2 {ov:.3f} vs w4-stride4 {w4:.3f}  "
              f"-> {'STRUCK again (overlap <= non-overlap)' if ov <= w4 + 0.005 else 'overlap helps?? investigate'}")

    try:
        import plot_p5
        figs = [plot_p5.fig_credit_reach(OUT), plot_p5.fig_inv(OUT)]
        for task in TASKS:
            figs.append(plot_p5.fig_depth_profile_window(OUT, task))
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
