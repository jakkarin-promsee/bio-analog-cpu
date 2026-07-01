"""
P6.6 — continual-safety: the home-turf gate (design.md §3 P6.6; the spine gate, un-skippable).

The question: does each adopted noise fix PRESERVE the A6 sleep-recovery continual win? The gate: BWT / AA /
retention of each candidate change vs the FIX-FREE committed cell (itself referenced to the P4.5 class-incremental
baseline), on the validated sleep/consolidation loop. **5 seeds NEVER 3**; "within noise" is NOT an auto-pass — a
change negative-BWT in ≥4/5 paired seeds FAILS even if IQR overlaps (the paired-sign veto). A fix that dents A6 is
rejected regardless of its A7 gain.

Changes tested (set ADOPT from the P6.1 verdict): fixfree · the adopted augmentation · (optional) alternatives.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_6.py [--quick]
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
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p6lib
from p6lib import (continual_safety, make_committed_cell, NoiseAugContrast, COMMITTED,          # noqa: E402
                   load_digits_split, CISTREAM_TASKS)

SEEDS = [42, 137, 271, 314, 1729]                                      # the GATE runs the full 5, never 3
NCLASS = 10                                                            # digits A6 home (matches the P5.7 referent BWT -0.026)
# ADOPT: the changes to gate. Set the adopted augmentation from the P6.1 verdict (filled after P6.1).
ADOPT = {
    "fixfree": lambda dims, seed: make_committed_cell(dims, seed),
    "aug_iid_1.0": lambda dims, seed: NoiseAugContrast(dims, seed=seed, sig_aug=1.0, variant="iid",
                                                       randax_seed=seed + 7, **COMMITTED),
}
OUT = os.path.join(_HERE, "figs_p6_6")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def run_change(change, seed):
    Xtr, Ytr, Xte, Yte = load_digits_split(seed)                       # the digits A6 home (matches P5.7)
    r = continual_safety(ADOPT[change], Xtr, Ytr, Xte, Yte, CISTREAM_TASKS, NCLASS, seed,
                         scff_ep=8, sleep_ep=60, sleep=True)
    return dict(change=change, seed=seed, aa=r["aa"], bwt=r["bwt"], forget=r["forget"],
                scff_probe=r["scff_probe"])


def rkey(r):
    return (r["change"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rkey(rr)] = rr
    return done


def main():
    global OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:2] if quick else SEEDS
    changes = list(ADOPT)
    OUT = os.path.join(_HERE, "figs_p6_6_quick" if quick else "figs_p6_6")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    print(f"=== P6.6 continual-safety GATE | changes {changes} × seeds {seeds} (full 5, never 3) ===", flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")
    for change in changes:
        for s in seeds:
            if (change, s) in done:
                r = done[(change, s)]
            else:
                r = run_change(change, s); done[(change, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {change:14s} seed {s}: AA {r['aa']:.3f}  BWT {r['bwt']:+.3f}  forget {r['forget']:.3f}", flush=True)
    fck.close()

    def arr(change, key):
        return np.array([done[(change, s)][key] for s in seeds], float)

    save = dict(seeds=np.array(seeds))
    for change in changes:
        for mt in ("aa", "bwt", "forget"):
            save[f"cont_{mt}_{change}"] = arr(change, mt)
    save["cont_ret_fixfree"] = arr("fixfree", "aa")                    # retention proxy = final all-task AA
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    # ============================================================ the GATE READS (paired-sign veto)
    print(f"\n--- P6.6 GATE READS (n={len(seeds)}) ---")
    base_bwt = arr("fixfree", "bwt"); base_aa = arr("fixfree", "aa")
    print(f"  fixfree: AA {np.median(base_aa):.3f} [{np.percentile(base_aa,25):.3f}-{np.percentile(base_aa,75):.3f}]  "
          f"BWT {np.median(base_bwt):+.3f}")
    for change in changes:
        if change == "fixfree":
            continue
        aa = arr(change, "aa"); bwt = arr(change, "bwt")
        d_bwt = bwt - base_bwt                                          # paired by seed
        neg = int((d_bwt < 0).sum())
        veto = neg >= 4                                                # negative in ≥4/5 paired seeds = FAIL
        iqr_overlap = not (np.percentile(aa, 25) > np.percentile(base_aa, 75) or
                           np.percentile(aa, 75) < np.percentile(base_aa, 25))
        verdict = "FAIL (paired-sign veto)" if veto else ("PASS" if np.median(aa) >= np.median(base_aa) - 0.02 else "CHECK")
        print(f"  {change:14s}: AA {np.median(aa):.3f}  BWT {np.median(bwt):+.3f}  ΔBWT {np.median(d_bwt):+.3f} "
              f"(neg {neg}/5)  → {verdict}")

    json.dump(dict(experiment="p6_6_continual_safety", git_commit=_git(), seeds=list(seeds), changes=changes,
                   numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p6
        print("\n  figures:", [os.path.basename(p) for p in plot_p6.regen(OUT)])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) → {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
