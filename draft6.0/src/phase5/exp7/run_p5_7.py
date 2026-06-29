"""
P5.7 — the continual-safety gate (design.md §3 P5.7 — THE SPINE GATE; un-skippable).

The architecture's reason for being is the A6 sleep-recovery continual win (online forgets; a periodic sleep
recovers it). A Phase-5 change is BANKED only if it preserves that win — however well it scores on a static probe.
This rung gates the one cell change Phase 5 actually adopts: **the sharper InfoNCE temperature (0.5 → 0.2)**, which
P5.1 flagged as a continual RISK (a sharper contrast is more class-selective on the CURRENT task → plausibly more
aggressive overwriting of prior-task structure, the A6 mechanism).

Conditions (one variable = the cell config; sleep on/off isolates readout consolidation), the all-tap readout
(the A6-validated deployed reader) throughout, on the class-incremental stream + sleep:
  t05_L4_sleep    — temp0.5, L4 : the P4.5 / P3.3 A6-VALIDATED baseline (the win to preserve)
  t02_L4_sleep    — temp0.2, L4 : THE PRIMARY GATE — temp-only change, depth held (the P5.1 tension)
  t02_L12_sleep   — temp0.2, L12: temp + the committed bulk depth (does deeper composing hurt continual?)
  t02_L4_nosleep  — temp0.2, L4 : the rot control (no consolidation → online forgetting shows)

Tasks: digits home (64-D, the A6 anchor) + synth class-incremental (40-D, overlap 0.7). 3 seeds (heaviest rung).
PASS gate: BWT(t02) ≥ BWT(t05) − 0.02 AND AA holds AND the all-class SCFF probe stays flat (the bulk doesn't
forget). If t02 FAILS, the pre-registered resolution (P5.1) is to fall back to the mildest temp that passes here
and still beats baseline depth — the gate OUTRANKS the depth gain.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_7.py [--quick]
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
from p5lib import (continual_eval, synth_stream, load_digits_split, CISTREAM_TASKS,    # noqa: E402
                   equivalence_guard, fd_gradient_check)

SEEDS = [42, 137, 271]
W, WIN, NCLASS = 64, 2, 10
SCFF_EP, SLEEP_EP, BATCH = 8, 60, 32
OVERLAP = 0.7
NTR, NTE = 4000, 1500
# (label, temp, L, sleep)
CONDS = [("t05_L4_sleep", 0.5, 4, True), ("t02_L4_sleep", 0.2, 4, True),
         ("t02_L12_sleep", 0.2, 12, True), ("t02_L4_nosleep", 0.2, 4, False)]
LAB = {"t05_L4_sleep": "temp0.5 L4 +sleep (A6 baseline)", "t02_L4_sleep": "temp0.2 L4 +sleep (GATE)",
       "t02_L12_sleep": "temp0.2 L12 +sleep (committed depth)", "t02_L4_nosleep": "temp0.2 L4 no-sleep (rot)"}
OUT = os.path.join(_HERE, "figs_p5_7")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _data(task, seed):
    if task == "digits":
        Xtr, Ytr, Xte, Yte = load_digits_split(seed); return Xtr, Ytr, Xte, Yte, Xtr.shape[1]
    Xtr, Ytr, Xte, Yte = synth_stream(NTR, NTE, OVERLAP, seed); return Xtr, Ytr, Xte, Yte, Xtr.shape[1]


def run_cell(task, cond, seed):
    lab, temp, L, sleep = next(c for c in CONDS if c[0] == cond)
    Xtr, Ytr, Xte, Yte, D = _data(task, seed)
    r = continual_eval([D] + [W] * L, temp, WIN, Xtr, Ytr, Xte, Yte, CISTREAM_TASKS, NCLASS, seed,
                       scff_ep=SCFF_EP, sleep_ep=SLEEP_EP, batch=BATCH, sleep=sleep, probe=True)
    return dict(task=task, cond=cond, seed=seed, aa=r["aa"], bwt=r["bwt"], forget=r["forget"],
                scff_probe=[float(x) for x in r["scff_probe"]])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[(rr["task"], rr["cond"], rr["seed"])] = rr
    return done


def main():
    global OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    tasks = ["digits"] if quick else ["digits", "synth"]
    OUT = os.path.join(_HERE, "figs_p5_7_quick" if quick else "figs_p5_7")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.7 guards ===", flush=True)
    eq_ok, eq_d = equivalence_guard(width=W, L=4, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check()
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.7 continual-safety gate | {tasks} | conds {[c[0] for c in CONDS]} | seeds {seeds} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for task in tasks:
        for cond, *_ in CONDS:
            for s in seeds:
                if (task, cond, s) in done:
                    continue
                r = run_cell(task, cond, s); done[(task, cond, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                print(f"  {task:6s} {cond:16s} seed {s}: AA {r['aa']:.3f}  BWT {r['bwt']:+.3f}  "
                      f"forget {r['forget']:.3f}  scff-probe {np.round(r['scff_probe'], 2)}", flush=True)
    fck.close()

    def col(task, cond, key):
        return np.array([done[(task, cond, s)][key] for s in seeds], float)

    save = dict(seeds=np.array(seeds), conds=np.array([c[0] for c in CONDS]),
                tasks=np.array(tasks), inv_fdguard=fd_d, inv_equiv=eq_d)
    for task in tasks:
        for cond, *_ in CONDS:
            for key in ("aa", "bwt", "forget"):
                save[f"{task}__{cond}__{key}"] = col(task, cond, key)
            save[f"{task}__{cond}__scff_probe"] = np.array([done[(task, cond, s)]["scff_probe"] for s in seeds])
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    print(f"\n--- P5.7 READS (n={len(seeds)}) — AA / BWT, median [IQR] ---")
    verdicts = {}
    for task in tasks:
        print(f"  [{task}]")
        for cond, *_ in CONDS:
            aa = col(task, cond, "aa"); bwt = col(task, cond, "bwt")
            print(f"    {LAB[cond]:36s} AA {np.median(aa):.3f}[{np.percentile(aa,25):.3f}-{np.percentile(aa,75):.3f}]"
                  f"  BWT {np.median(bwt):+.3f}[{np.percentile(bwt,25):+.3f},{np.percentile(bwt,75):+.3f}]")
        b05 = float(np.median(col(task, "t05_L4_sleep", "bwt")))
        b02 = float(np.median(col(task, "t02_L4_sleep", "bwt")))
        a05 = float(np.median(col(task, "t05_L4_sleep", "aa")))
        a02 = float(np.median(col(task, "t02_L4_sleep", "aa")))
        sp = np.median(save[f"{task}__t02_L4_sleep__scff_probe"], 0)
        sp_flat = (sp[-1] - sp[0]) > -0.05
        gate = (b02 >= b05 - 0.02) and (a02 >= a05 - 0.03) and sp_flat
        verdicts[task] = gate
        print(f"    GATE: temp0.2 BWT {b02:+.3f} vs temp0.5 {b05:+.3f} (AA {a02:.3f} vs {a05:.3f}); "
              f"SCFF-probe {'flat' if sp_flat else 'DROPS'} -> "
              f"{'PASS — temp0.2 keeps the A6 win' if gate else 'FAIL — temp0.2 dents A6 (fall back to milder temp)'}",
              flush=True)
    overall = all(verdicts.values())
    print(f"\n  P5.7 VERDICT: {'PASS on all tasks — bank temp0.2' if overall else 'FAIL on '+str([t for t in tasks if not verdicts[t]])+' — gate outranks depth, fall back'}",
          flush=True)

    json.dump(dict(experiment="p5_7_contsafety", git_commit=_git(), seeds=list(seeds), conds=[c[0] for c in CONDS],
                   tasks=tasks, window=WIN, scff_ep=SCFF_EP, sleep_ep=SLEEP_EP, overlap=OVERLAP,
                   verdicts={t: bool(v) for t, v in verdicts.items()}, guards=dict(equiv=eq_d, fd=fd_d),
                   numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p5
        figs = [plot_p5.fig_cont_safety(OUT, task) for task in tasks]
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
