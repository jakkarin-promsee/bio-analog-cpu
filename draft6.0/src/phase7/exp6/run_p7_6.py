"""
P7.6 — synthesis: the assembled-head confirmation (design.md §3 P7.6).

The committed pipeline = RanPAC (the P7.1 no-gradient winner) + the P7.3 imbalance guard (class-balanced reservoir).
A combined regression OVERRIDES per-rung optimism (levers may not stack). The bar (pinned): if the assembled head's
accuracy x BWT falls below its P7.1 solo number (AA 0.617) by more than the §B band (delta=0.02), the guard is
reverted. On the balanced A6 home the cbrs guard is ~a no-op (the buffer is already balanced) — the confirmation is
that adding the guard does NOT degrade the home number, while P7.3 shows it fixes the bursty-skew regime.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_6.py [--quick]
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
import p7lib as P                                                       # noqa: E402
import p7cfg as CFG                                                     # noqa: E402
import plot_p7                                                          # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p7_6" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
SCFF_EP = 2 if QUICK else CFG.SCFF_EP
HEAD = CFG.COMMITTED_HEAD                                              # "ranpac"
KNOB = CFG.COMMITTED_KNOBS[HEAD]
BAND = 0.02
CBRS_CAP = 2000                                                       # generous cap: cbrs ~no-op on the balanced home
P71_SOLO_AA = 0.617                                                   # the P7.1 RanPAC solo AA (the bar to hold)


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def run_seed(seed):
    C = CFG.NCLASS
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed, dim=CFG.DIM, n_class=C, n_clusters=CFG.NCLUST)
    cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, C, seed, scff_ep=SCFF_EP)
    hf = lambda s: P.make_head(HEAD, C, seed=s, **KNOB)
    solo = P.eval_head_on_cache(cache, hf, seed)                       # RanPAC solo (= P7.1/P7.4)
    asm = P.eval_head_on_cache(cache, hf, seed, buffer_cap=CBRS_CAP, C=C)   # RanPAC + cbrs (assembled)
    return dict(solo_aa=solo["aa"], solo_bwt=solo["bwt"], asm_aa=asm["aa"], asm_bwt=asm["bwt"])


def main():
    t0 = time.time()
    print(f"P7.6 — assembled-head confirmation: {HEAD} + cbrs  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    rows = [run_seed(s) for s in SEEDS]
    for s, r in zip(SEEDS, rows):
        print(f"  seed {s:5d}: solo AA={r['solo_aa']:.3f}/B{r['solo_bwt']:+.3f}  assembled(+cbrs) AA={r['asm_aa']:.3f}/B{r['asm_bwt']:+.3f}", flush=True)

    solo_aa = np.array([r["solo_aa"] for r in rows]); asm_aa = np.array([r["asm_aa"] for r in rows])
    A = dict(seeds=np.array(SEEDS), heads=np.array([HEAD + "-solo", HEAD + "+cbrs"]))
    A[f"aa_{HEAD}-solo"] = solo_aa; A[f"aa_{HEAD}+cbrs"] = asm_aa
    A[f"bwt_{HEAD}-solo"] = np.array([r["solo_bwt"] for r in rows]); A[f"bwt_{HEAD}+cbrs"] = np.array([r["asm_bwt"] for r in rows])
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    med_solo, med_asm = float(np.median(solo_aa)), float(np.median(asm_aa))
    holds = med_asm >= P71_SOLO_AA - BAND
    manifest = dict(rung="P7.6", git=_git(), quick=QUICK, seeds=SEEDS, wall_s=round(time.time() - t0, 1),
                    committed_head=HEAD, knob=KNOB, cbrs_cap=CBRS_CAP,
                    assembled_aa=med_asm, solo_aa=med_solo, p71_solo_aa=P71_SOLO_AA, band=BAND, holds=bool(holds),
                    versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print("\n== P7.6 ASSEMBLED-HEAD CONFIRMATION ==", flush=True)
    print(f"  committed = {HEAD} {KNOB} + cbrs(cap={CBRS_CAP})", flush=True)
    print(f"  assembled AA={med_asm:.3f}  vs  solo AA={med_solo:.3f}  vs  P7.1 solo bar={P71_SOLO_AA:.3f} (band {BAND})", flush=True)
    print(f"  -> {'HOLDS (guard non-degrading on the balanced home; P7.3 shows it fixes the bursty skew)' if holds else 'BELOW BAND — revert guard'}", flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
