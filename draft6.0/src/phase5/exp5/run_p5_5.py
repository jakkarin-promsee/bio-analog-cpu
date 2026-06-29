"""
P5.5 — calibrated early-exit on the CONTINUAL workload (design.md §3 P5.5 — STOPPING MARK ①).

The cost half of the readout redesign, on the home turf. Inheriting the committed cell (temp0.2/w2) and P5.4's
verdict (per-depth heads Pareto-dominate all-tap), this asks the decisive question: on the *continual* stream,
does a calibrated head-confidence exit read DEEP ENOUGH PER SAMPLE to hold accuracy, at LOWER forward
expected-compute than BOTH all-tap (always-deep) and the truncation floor (always-shallow-fixed)?

  * the stream — the P4.5 class-incremental synthetic home (10 classes / 40 clusters / 5 tasks of 2, make_gauss
    overlap 0.7). SCFF trains forward-only through it; the readouts are sleep-consolidated on the full buffer.
  * the exit — head MAX-SOFTMAX (class-confidence, THE SPINE — not goodness/energy), τ calibrated CALM-style to
    hold ≥95% of all-tap acc on a DISJOINT cal split. ONE-SHOT τ (calibrated on the EARLY tasks 0-1, classes
    0-3) vs PER-TASK-REFIT τ (calibrated on all classes) — which one is needed is itself the cost question.
  * the floor — a from-scratch L=(profiler-peak+1) stack trained on the same stream, read at its TOP (1 head).
  * the oracle — best-per-input layer (shallowest correct head): the upper bound on any gate + the true-class
    signal the label-free confidence proxy is scored against (the spine risk: confidence mis-calibrates on shift).

STOPPING MARK ①: T1 restores the 80/20 iff exit (ONE-SHOT τ) E_compute beats all-tap AND truncation, accuracy
held. C5-pessimistic branch (pre-registered): if exit wins only with refit-τ, or never beats truncation → the
honest verdict is "ship truncation / all-tap on the continual stream" (a complete answer, not a failure).

Heaviest rung: 3 seeds, checkpoint-mandatory, single-thread-verified (the 14-hr-ghost guard).
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_5.py [--quick]
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
from p5lib import (SCFFContrastOverlap, synth_stream, train_scff_stream, CISTREAM_TASKS,     # noqa: E402
                   CalibratedExit, fit_readout, readout_feats, exit_compute, forward_cost_alltap,
                   forward_cost_trunc, equivalence_guard, fd_gradient_check, effective_rank)

SEEDS = [42, 137, 271]                                                  # 3 — heaviest rung (design §5)
L, W, DIM, NCLASS = 12, 64, 40, 10
NTR, NTE = 4000, 1500
SCFF_EP, BATCH, TEMP, WIN = 8, 32, 0.2, 2                               # SCFF_EP=8 = the A6 home protocol
OVERLAP = 0.7
EARLY_CLASSES = [c for cls in CISTREAM_TASKS[:2] for c in cls]          # tasks 0-1 -> classes 0,1,2,3
KEEP = 0.95
OUT = os.path.join(_HERE, "figs_p5_5")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _newcell(nl, seed):
    w = min(WIN, nl)
    return SCFFContrastOverlap([DIM] + [W] * nl, lr=0.03, seed=seed, window=w, stride=w,
                               mask_ratio=0.5, temp=TEMP)


def run_cell(seed):
    Xtr, Ytr, Xte, Yte = synth_stream(NTR, NTE, OVERLAP, seed)
    Xcal, Ycal, _, _ = synth_stream(NTR, NTE, OVERLAP, seed + 5000)     # cal split DISJOINT from test

    # --- the committed L12 cell through the class-incremental stream (forward-only) + sleep-consolidated heads ---
    cell = _newcell(L, seed)
    Xbuf, Ybuf = train_scff_stream(cell, Xtr, Ytr, CISTREAM_TASKS, seed, scff_ep=SCFF_EP, batch=BATCH)
    reps_buf, reps_te, reps_cal = cell.infer(Xbuf), cell.infer(Xte), cell.infer(Xcal)
    heads = [fit_readout(reps_buf[l], Ybuf, NCLASS, seed + l) for l in range(L)]
    logit_te = [heads[l].forward(reps_te[l]) for l in range(L)]
    logit_cal = [heads[l].forward(reps_cal[l]) for l in range(L)]

    exit = CalibratedExit(L)
    conf_te, pred_te = exit.conf_pred(logit_te)
    conf_cal, pred_cal = exit.conf_pred(logit_cal)
    depth_acc = [float((pred_te[:, l] == Yte).mean()) for l in range(L)]
    peak_d = int(np.argmax(depth_acc)); k = max(1, peak_d + 1)          # truncation depth = profiler-peak + 1

    # --- all-tap (the deployed P3.3/P4.5 readout) ---
    ro_at = fit_readout(readout_feats(reps_buf, None), Ybuf, NCLASS, seed)
    at_te = ro_at.predict(readout_feats(reps_te, None))
    at_cal = ro_at.predict(readout_feats(reps_cal, None))
    alltap_acc = float((at_te == Yte).mean())

    # --- truncation floor: from-scratch L=k, read at TOP ---
    cellk = _newcell(k, seed + 100)
    Xbk, Ybk = train_scff_stream(cellk, Xtr, Ytr, CISTREAM_TASKS, seed + 100, scff_ep=SCFF_EP, batch=BATCH)
    ro_k = fit_readout(cellk.infer(Xbk)[-1], Ybk, NCLASS, seed + 100)
    trunc_acc = float((ro_k.predict(cellk.infer(Xte)[-1]) == Yte).mean())

    # --- calibrate τ: one-shot (EARLY classes only) vs refit (all classes) ---
    em = np.isin(Ycal, EARLY_CLASSES)
    at_early = float((at_cal[em] == Ycal[em]).mean()); at_full = float((at_cal == Ycal).mean())
    tau1 = exit.calibrate(conf_cal[em], pred_cal[em], Ycal[em], at_early, keep=KEEP)
    tauR = exit.calibrate(conf_cal, pred_cal, Ycal, at_full, keep=KEEP)

    # --- evaluate the five readers on the test stream ---
    e1_pred, e1_d = exit.predict(conf_te, pred_te, tau1)
    eR_pred, eR_d = exit.predict(conf_te, pred_te, tauR)
    or_d = exit.oracle_depth(pred_te, Yte)
    or_pred = pred_te[np.arange(len(or_d)), or_d]
    at_cost = float(forward_cost_alltap(DIM, W, L, NCLASS))
    tr_cost = float(forward_cost_trunc(DIM, W, k, NCLASS))

    dead = [float((reps_te[l].max(0) <= 1e-9).mean()) for l in range(L)]   # dead-UNIT frac (never fires), not sparsity
    erank = [float(effective_rank(reps_te[l])) for l in range(L)]
    return dict(
        seed=seed, k=k, peak_d=peak_d + 1, depth_acc=depth_acc, tau1=float(tau1), tauR=float(tauR),
        alltap_acc=alltap_acc, alltap_cost=at_cost, trunc_acc=trunc_acc, trunc_cost=tr_cost,
        exit1_acc=float((e1_pred == Yte).mean()), exit1_cost=exit_compute(DIM, W, NCLASS, e1_d),
        exit1_depth=float(e1_d.mean() + 1),
        exitR_acc=float((eR_pred == Yte).mean()), exitR_cost=exit_compute(DIM, W, NCLASS, eR_d),
        exitR_depth=float(eR_d.mean() + 1),
        oracle_acc=float((or_pred == Yte).mean()), oracle_cost=exit_compute(DIM, W, NCLASS, or_d),
        oracle_depth=float(or_d.mean() + 1),
        dead=dead, erank=erank)


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[r["seed"]] = r
    return done


def main():
    global OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    OUT = os.path.join(_HERE, "figs_p5_5_quick" if quick else "figs_p5_5")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.5 guards ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.5 calibrated exit on continual | overlap {OVERLAP} | seeds {seeds} | {len(done)} cached ===",
          flush=True)
    fck = open(ckpt, "a")
    for s in seeds:
        if s in done:
            continue
        r = run_cell(s); done[s] = r
        fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        print(f"  seed {s}: peakL{r['peak_d']} truncL{r['k']} | "
              f"exit1 {r['exit1_acc']:.3f}@{r['exit1_cost']/1000:.1f}k(d{r['exit1_depth']:.1f},τ{r['tau1']:.2f}) "
              f"all-tap {r['alltap_acc']:.3f}@{r['alltap_cost']/1000:.1f}k "
              f"trunc {r['trunc_acc']:.3f}@{r['trunc_cost']/1000:.1f}k "
              f"oracle {r['oracle_acc']:.3f}@{r['oracle_cost']/1000:.1f}k", flush=True)
    fck.close()

    def col(key):
        return np.array([done[s][key] for s in seeds], float)

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, temp=TEMP, window=WIN, overlap=OVERLAP,
                trunc_k=int(np.median(col("k"))), tau_oneshot=float(np.median(col("tau1"))),
                tau_refit=float(np.median(col("tauR"))),
                inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_deadfrac=np.array([done[s]["dead"] for s in seeds]),
                inv_erank=np.array([done[s]["erank"] for s in seeds]))
    for who in ("exit1", "exitR", "alltap", "trunc", "oracle"):
        save[f"pareto_{who}_acc"] = col(f"{who}_acc")
        save[f"pareto_{who}_cost"] = col(f"{who}_cost")
    save["depth_profile"] = np.array([done[s]["depth_acc"] for s in seeds])
    save["exit1_depth"] = col("exit1_depth")
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    def med(key):
        return float(np.median(col(key)))

    e1c, atc, trc = med("exit1_cost"), med("alltap_cost"), med("trunc_cost")
    e1a, ata = med("exit1_acc"), med("alltap_acc")
    win_cost = (e1c < atc) and (e1c < trc)
    win_acc = e1a >= KEEP * ata
    refit_needed = med("exitR_cost") < 0.9 * e1c or med("exitR_acc") > e1a + 0.02
    if win_cost and win_acc:
        verdict = "STOP① PASS — exit (one-shot τ) beats all-tap AND truncation, accuracy held -> depth read cheaply"
    elif e1c < atc and not (e1c < trc):
        verdict = "C5-PESSIMISTIC — exit beats all-tap but NOT truncation on the flat home -> SHIP TRUNCATION"
    else:
        verdict = "C5-PESSIMISTIC — exit does not clear the bar -> ship truncation/all-tap (complete answer)"

    print(f"\n--- P5.5 READS (n={len(seeds)}) — accuracy @ forward expected-compute (kMACs), median ---")
    for who, lab in (("exit1", "exit one-shot τ"), ("exitR", "exit refit τ"), ("alltap", "all-tap"),
                     ("trunc", f"truncation L{save['trunc_k']}"), ("oracle", "oracle (upper bnd)")):
        a, c = col(f"{who}_acc"), col(f"{who}_cost") / 1000
        print(f"  {lab:20s} acc {np.median(a):.3f}[{np.percentile(a,25):.3f}-{np.percentile(a,75):.3f}]  "
              f"cost {np.median(c):.1f}k[{np.percentile(c,25):.1f}-{np.percentile(c,75):.1f}]")
    print(f"\n  τ one-shot {save['tau_oneshot']:.3f} vs refit {save['tau_refit']:.3f}  "
          f"(refit-needed: {refit_needed})")
    print(f"  STOP①: exit1 cost {e1c/1000:.1f}k {'<' if win_cost else '>='} min(all-tap {atc/1000:.1f}k, "
          f"trunc {trc/1000:.1f}k); acc {e1a:.3f} {'>=' if win_acc else '<'} 0.95·all-tap {KEEP*ata:.3f}")
    print(f"  -> {verdict}", flush=True)

    json.dump(dict(experiment="p5_5_exit", git_commit=_git(), seeds=list(seeds), L=L, W=W, temp=TEMP, window=WIN,
                   overlap=OVERLAP, scff_ep=SCFF_EP, keep=KEEP, trunc_k=save["trunc_k"],
                   tau_oneshot=save["tau_oneshot"], tau_refit=save["tau_refit"], verdict=verdict,
                   guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p5
        figs = [plot_p5.fig_exit_pareto(OUT), plot_p5.fig_inv(OUT)]
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
