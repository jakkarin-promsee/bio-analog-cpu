"""
P8.3 — the sleep cadence (the SAME drift response, slow; design.md sec 3 P8.3). The awake gate is FIXED (the P8.1
committed detector); this sweeps the SLEEP cadence x LUT-history-fraction x running-Gram EMA-decay lam_ema, scoring
accuracy-held x sleep-cost x the worst-point A6-BWT. The awake gate creates the ~90% staleness only sleep fixes, so
gate + cadence are one coupled loop -- this rung finds the cheapest cadence + smallest history + lam_ema that HOLDS
the A6 win. The committed cadence is flagged DRIFT-RATE-CONDITIONAL (re-tune if P9's N2 slows the drift).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_3.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p8lib as P                                                      # noqa: E402
import p8cfg as CFG                                                    # noqa: E402
import p8run as R                                                      # noqa: E402
import plot_p8                                                         # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p8_3" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
AWAKE_GATE = "ddm"                                                    # the P8.1 committed awake detector
# F axis: sleep cadence (freq: dense -> sparse). H axis: (lut_frac, lam_ema).
FREQS = [("checkpoint", 1, "oracle-boundary"), ("grid", 2, "grid-2"), ("grid", 4, "grid-4"), ("grid", 8, "grid-8")]
HISTS = [(1.0, 1.0, "full/l1.0"), (0.5, 1.0, "half/l1.0"), (0.25, 1.0, "qtr/l1.0"), (1.0, 0.9, "full/l0.9")]


def main():
    t0 = time.time()
    print(f"P8.3 — sleep cadence  (QUICK={QUICK}, seeds={SEEDS}, awake={AWAKE_GATE})", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    S, F, H = len(SEEDS), len(FREQS), len(HISTS)
    grid_aa = np.zeros((S, F, H)); grid_bwt = np.zeros((S, F, H)); grid_sleepcost = np.zeros((S, F, H))
    for si, s in enumerate(SEEDS):
        stream, cache = caches[s]
        for fi, (pol, cad, _fl) in enumerate(FREQS):
            for hi, (lf, le, _hl) in enumerate(HISTS):
                r = P.run_economy(cache, lambda: P.make_stream_head("ranpac", CFG.NCLASS, seed=s, **CFG.RANPAC_KNOB),
                                  CFG, gate=AWAKE_GATE, trigger="error_ema", sleep_policy=pol, cadence_every=cad,
                                  lut_frac=lf, lam_ema=le)
                grid_aa[si, fi, hi] = r["aa"]; grid_bwt[si, fi, hi] = r["worst_bwt"]
                grid_sleepcost[si, fi, hi] = float(r["sleeps"].sum())
        print(f"  seed {s}: AA[oracle-bound,full]={grid_aa[si,0,0]:.3f} AA[grid-8,full]={grid_aa[si,3,0]:.3f} "
              f"AA[grid-4,qtr]={grid_aa[si,2,2]:.3f}", flush=True)

    A = dict(seeds=np.array(SEEDS), cadence_grid=grid_aa, cadence_bwt=grid_bwt,
             cadence_freqs=np.array([f[2] for f in FREQS]), cadence_hists=np.array([h[2] for h in HISTS]),
             cadence_sleepcost=grid_sleepcost, inv_partial_fit=np.array([1.0]), inv_cache_replay=np.array([1.0]))
    aa_ref = np.median(grid_aa[:, 0, 0])                              # oracle-boundary / full-history reference
    # the cheapest (SPARSEST sleep F, smallest history/lam) cell that HOLDS the A6 win (AA within 0.02 of the ref);
    # the worst-point BWT is reported alongside (a P8.6-safety read, not a cadence gate -- it is inherently negative
    # mid-stream). Search sparsest-first over F, then history order.
    best = None
    for fi in range(F - 1, -1, -1):
        for hi in range(H):
            aa = np.median(grid_aa[:, fi, hi]); bwt = np.median(grid_bwt[:, fi, hi])
            if aa >= aa_ref - 0.02:
                best = dict(freq=FREQS[fi][2], hist=HISTS[hi][2], aa=float(aa), bwt=float(bwt),
                            sleep_cost=float(np.median(grid_sleepcost[:, fi, hi]))); break
        if best:
            break
    man = R.base_manifest("P8.3", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1), awake_gate=AWAKE_GATE,
                          aa_reference=float(aa_ref), committed_cadence=best, drift_conditional=True,
                          summary=dict(aa_grid=np.median(grid_aa, 0).round(3).tolist(),
                                       bwt_grid=np.median(grid_bwt, 0).round(3).tolist()))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.3 SUMMARY (median AA; ref[oracle-boundary,full]={aa_ref:.3f}) ==", flush=True)
    print("  cadence \\ history: " + "  ".join(h[2] for h in HISTS), flush=True)
    for fi, fl in enumerate(FREQS):
        print(f"  {fl[2]:16s} " + "  ".join(f"{np.median(grid_aa[:,fi,hi]):.3f}" for hi in range(H)), flush=True)
    print(f"  committed cadence (cheapest holding A6): {best}", flush=True)
    print(f"  (flagged DRIFT-RATE-CONDITIONAL -- re-tune if P9's N2 slows the drift.)  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
