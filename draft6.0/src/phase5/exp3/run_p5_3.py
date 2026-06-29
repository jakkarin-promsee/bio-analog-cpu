"""
P5.3 — lost or rotated? + the profiler + the truncation floor (design.md §3 P5.3).

Inheriting the committed cell (temp=0.2, window=2), this rung opens the READ thread with three separable questions:
  (a) LOST vs ROTATED — linear-probe vs MLP-probe per depth. If the MLP recovers the post-peak layers, the class
      info is ROTATED (not destroyed) -> cheap PLACEMENT beats objective-surgery. If it can't -> genuinely LOST.
  (b) THE PROFILER — per-layer probe peak + the per-depth READOUT-optimal depth (the two must agree within +/-1, or
      placement is driven by the readout not the probe). Swept over difficulty (overlap {0.4,0.6,0.9}) to test the
      "extractor length rises with task complexity" trigger.
  (c) THE TRUNCATION FLOOR — a FROM-SCRATCH L=peak+1 stack (matched budget AND own-tuned), read at its top: the
      cheap baseline every later tier must beat (fewer layers = fewer Scaps = cheaper silicon).

Committed cell read at the TOP suffers the residual decay; the profiler finds where to read instead. Guards first.
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_3.py [--quick]
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
from p5lib import (SCFFContrastOverlap, make_headroom, make_flat, make_mixed, make_tierb,    # noqa: E402
                   equivalence_guard, fd_gradient_check, fit_readout, readout_feats,
                   linear_probe, mlp_probe, effective_rank)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH, TEMP, WIN = 25, 32, 0.2, 2
PROBE_EP = 120
OVERLAPS = [0.4, 0.6, 0.9]                                            # difficulty dial (0.6 = the committed)
TRUNC_DEPTHS = [5, 7, 9]
OWN_TUNE = [(0.03, 25), (0.05, 25), (0.03, 40), (0.05, 40)]           # truncation own-budget grid (the fairness arm)
OUT = os.path.join(_HERE, "figs_p5_3")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _make(task, n, seed, overlap=0.6):
    if task == "headroom":
        return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=overlap,
                          label="random", n_class=NCLASS) + (None,)
    if task == "flat":
        X, Y, _ = make_flat(n, seed); return X, Y, None
    X, Y, m = make_mixed(n, seed); return X, Y, m


def train(Xtr, Ldepth, lr, ep, seed):
    m = SCFFContrastOverlap([DIM] + [W] * Ldepth, lr=lr, seed=seed, window=WIN, stride=WIN, mask_ratio=0.5, temp=TEMP)
    rng = np.random.default_rng(seed)
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


# ---- the committed-cell profiler (per-depth probe + readout) ----
def run_profile(task, seed, with_mlp):
    Xtr, Ytr, mtr = _make(task, NTR, seed + 1); Xte, Yte, mte = _make(task, NTE, seed + 2)
    m = train(Xtr, L, 0.03, EP, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    if task == "mixed":                                              # the corruption metric = flat-subtask only
        ftr, fte = mtr["flat"], mte["flat"]
        rt = [r[ftr] for r in reps_tr]; re = [r[fte] for r in reps_te]; yt, ye = Ytr[ftr], Yte[fte]
    else:
        rt, re, yt, ye = reps_tr, reps_te, Ytr, Yte
    lin = [linear_probe(a, yt, b, ye, NCLASS, seed, epochs=PROBE_EP) for a, b in zip(rt, re)]
    rod = [float((fit_readout(a, yt, NCLASS, seed).predict(b) == ye).mean()) for a, b in zip(rt, re)]  # readout@depth
    out = dict(part="profile", task=task, seed=seed, lin=[float(x) for x in lin], readout_depth=rod,
               peak_lin=int(np.argmax(lin)) + 1, readout_opt=int(np.argmax(rod)) + 1,
               readout_top=float(rod[-1]), readout_best=float(np.max(rod)),
               dead=[float(x) for x in m.dead_fraction(Xte)],
               erank=[float(effective_rank(r)) for r in reps_te])
    if with_mlp:
        out["mlp"] = [float(mlp_probe(a, yt, b, ye, NCLASS, seed, epochs=PROBE_EP)) for a, b in zip(rt, re)]
    return out


def run_complexity(overlap, seed):
    Xtr, Ytr, _ = _make("headroom", NTR, seed + 1, overlap=overlap)
    Xte, Yte, _ = _make("headroom", NTE, seed + 2, overlap=overlap)
    m = train(Xtr, L, 0.03, EP, seed)
    lin = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP) for rt, re in zip(m.infer(Xtr), m.infer(Xte))]
    return dict(part="complexity", overlap=overlap, seed=seed, lin=[float(x) for x in lin],
                peak_lin=int(np.argmax(lin)) + 1)


def run_truncation(Ldepth, lr, ep, seed, tag):
    Xtr, Ytr, _ = _make("headroom", NTR, seed + 1); Xte, Yte, _ = _make("headroom", NTE, seed + 2)
    m = train(Xtr, Ldepth, lr, ep, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)   # read at the TOP of the truncated stack
    acc = float((fit_readout(Ftr, Ytr, NCLASS, seed).predict(Fte) == Yte).mean())
    return dict(part="trunc", tag=tag, Ldepth=Ldepth, lr=lr, ep=ep, seed=seed, top_readout=acc)


def rkey(r):
    p = r["part"]
    if p == "profile":
        return (p, r["task"], r["seed"])
    if p == "complexity":
        return (p, r["overlap"], r["seed"])
    return (p, r["tag"], r["seed"])


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
    OUT = os.path.join(_HERE, "figs_p5_3_quick" if quick else "figs_p5_3")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.3 guards ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")

    def do(key, fn, *a):
        if key in done:
            return done[key]
        r = fn(*a); done[rkey(r)] = r
        fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        return r

    tasks = ["headroom"] if quick else ["headroom", "flat", "mixed"]
    overlaps = [0.6] if quick else OVERLAPS
    trunc_d = [7] if quick else TRUNC_DEPTHS
    print(f"\n=== P5.3 | profiler {tasks} | complexity {overlaps} | trunc {trunc_d} | seeds {seeds} | "
          f"PROBE_EP={PROBE_EP} | {len(done)} cached ===", flush=True)
    for task in tasks:                                               # (a)+(b) profiler (MLP only on headroom)
        for s in seeds:
            r = do(("profile", task, s), run_profile, task, s, task == "headroom")
            print(f"  profile {task:8s} seed {s}: peak_lin@L{r['peak_lin']:>2} readout_opt@L{r['readout_opt']:>2} "
                  f"readout_top {r['readout_top']:.3f} readout_best {r['readout_best']:.3f}", flush=True)
    for ov in overlaps:                                             # complexity (peak vs difficulty)
        if ov == 0.6:
            continue                                                # 0.6 == the committed headroom profile (reuse)
        for s in seeds:
            r = do(("complexity", ov, s), run_complexity, ov, s)
            print(f"  complexity ov{ov} seed {s}: peak_lin@L{r['peak_lin']}", flush=True)
    for Ld in trunc_d:                                              # (c) truncation floor — matched budget
        for s in seeds:
            r = do(("trunc", f"L{Ld}_matched", s), run_truncation, Ld, 0.03, EP, s, f"L{Ld}_matched")
            print(f"  trunc L{Ld} matched seed {s}: top_readout {r['top_readout']:.3f}", flush=True)
    for (lr, ep) in (OWN_TUNE if not quick else [(0.05, 25)]):       # own-tuned L7 (fairness arm)
        for s in seeds:
            do(("trunc", f"L7_own_lr{lr}_ep{ep}", s), run_truncation, 7, lr, ep, s, f"L7_own_lr{lr}_ep{ep}")
    fck.close()

    # ---- aggregate ----
    def prof(task, key):
        return np.array([done[("profile", task, s)][key] for s in seeds])

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, probe_ep=PROBE_EP, temp=TEMP, window=WIN,
                inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_deadfrac=prof("headroom", "dead"), inv_erank=prof("headroom", "erank"),
                profiler_overlaps=np.array(overlaps), trunc_depths=np.array(trunc_d))
    for task in tasks:
        save[f"{task}_lin"] = prof(task, "lin")
        save[f"{task}_readout_depth"] = prof(task, "readout_depth")
        save[f"{task}_peak_lin"] = prof(task, "peak_lin")
        save[f"{task}_readout_opt"] = prof(task, "readout_opt")
        save[f"{task}_readout_top"] = prof(task, "readout_top")
        save[f"{task}_readout_best"] = prof(task, "readout_best")
    if "headroom" in tasks:
        save["headroom_mlp"] = prof("headroom", "mlp")
    # complexity: peak vs overlap (0.6 from the headroom profile)
    cov = []; cpk = []
    for ov in overlaps:
        if ov == 0.6:
            pk = save["headroom_peak_lin"]
        else:
            pk = np.array([done[("complexity", ov, s)]["peak_lin"] for s in seeds])
        cov.append(ov); cpk.append(pk)
    save["complexity_overlaps"] = np.array(cov); save["complexity_peak"] = np.array(cpk).T   # [S, n_ov]
    # truncation
    for Ld in trunc_d:
        save[f"trunc_L{Ld}_matched"] = np.array([done[("trunc", f"L{Ld}_matched", s)]["top_readout"] for s in seeds])
    own = {}
    for (lr, ep) in (OWN_TUNE if not quick else [(0.05, 25)]):
        own[(lr, ep)] = np.array([done[("trunc", f"L7_own_lr{lr}_ep{ep}", s)]["top_readout"] for s in seeds])
    own_best = np.max(np.stack(list(own.values())), 0)               # best own-tuned L7 per seed
    save["trunc_L7_owntuned"] = own_best
    np.savez(os.path.join(OUT, "arrays.npz"), **save)
    json.dump(dict(experiment="p5_3_profiler_truncation", git_commit=_git(), seeds=list(seeds), L=L, W=W,
                   temp=TEMP, window=WIN, probe_ep=PROBE_EP, overlaps=overlaps, trunc_depths=trunc_d,
                   guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    # ---- the Reads ----
    print(f"\n--- P5.3 READS (n={len(seeds)}) ---")
    hl = np.median(save["headroom_lin"], 0); hr = np.median(save["headroom_readout_depth"], 0)
    print(f"  HEADROOM profiler: probe-peak@L{int(np.argmax(hl))+1} ({hl.max():.3f})  "
          f"readout-opt@L{int(np.argmax(hr))+1} ({hr.max():.3f})  readout-top {hr[-1]:.3f}")
    agree = abs((int(np.argmax(hl)) + 1) - (int(np.argmax(hr)) + 1))
    print(f"     profiler↔readout agreement: |{int(np.argmax(hl))+1} - {int(np.argmax(hr))+1}| = {agree} "
          f"({'AGREE (≤1)' if agree <= 1 else 'DISAGREE -> readout-driven'})")
    if "headroom_mlp" in save:
        hm = np.median(save["headroom_mlp"], 0)
        tail_gap = hm[-1] - hl[-1]
        print(f"  LOST-vs-ROTATED (L12 tail): linear {hl[-1]:.3f}  MLP {hm[-1]:.3f}  Δ{tail_gap:+.3f}  "
              f"-> {'ROTATED (MLP recovers)' if tail_gap > 0.02 else 'LOST (MLP can not recover)'}")
    cpk_med = np.median(save["complexity_peak"], 0)
    print(f"  COMPLEXITY: peak vs overlap {list(save['complexity_overlaps'])} = {[int(x) for x in cpk_med]}  "
          f"-> {'peak RISES with difficulty' if cpk_med[-1] >= cpk_med[0] else 'flat/inverse'}")
    print(f"  TRUNCATION floor (headroom top-readout):")
    for Ld in trunc_d:
        print(f"     L{Ld} matched: {np.median(save[f'trunc_L{Ld}_matched']):.3f}")
    print(f"     L7 own-tuned: {np.median(save['trunc_L7_owntuned']):.3f}  vs full-L12 readout-best "
          f"{np.median(save['headroom_readout_best']):.3f} / top {np.median(save['headroom_readout_top']):.3f}")

    try:
        import plot_p5
        figs = [plot_p5.fig_placement(OUT, "headroom"), plot_p5.fig_inv(OUT)]
        for task in ("flat", "mixed"):
            if f"{task}_lin" in save:
                figs.append(plot_p5.fig_placement(OUT, task))
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
