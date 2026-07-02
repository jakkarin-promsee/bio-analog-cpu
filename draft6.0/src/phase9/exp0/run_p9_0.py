"""
P9.0 — the risk gate: bench + guards + the bulk-drift rate + the ROTATION / STALENESS / DESTRUCTION split
(design.md §3 P9.0). No knob is tuned — a MEASUREMENT + the fork that gates the rest of the ladder. Asks:
  * do ALL guards pass (7 carried P8 + n2_readside + evict_equiv) — ANY fail -> STOP;
  * on a LONG lifelong stream (revisit cycles -> accumulated drift), does the bulk only ROTATE (a fresh sleep re-solve
    tracks it -> the cheap-replay story holds) or does it FORGET (an OPTIMAL probe RE-FIT on the current bulk still
    loses early-task accuracy -> the founding assumption breaks)?
  * the verdict keys on curve (3), the RE-FIT destruction curve (a frozen probe conflates rotation with forgetting).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_0.py [--quick]
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
import p9lib as P                                                      # noqa: E402
import p9cfg as CFG                                                    # noqa: E402
import p9run as R                                                      # noqa: E402
import plot_p9                                                         # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p9_0" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS


def main():
    t0 = time.time()
    print(f"P9.0 — risk gate: guards + lifelong drift + rotation/staleness/DESTRUCTION  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    print("== GUARDS (any fail -> STOP) ==", flush=True)
    g, n2d = R.run_all_guards(verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print("  -> all guards PASS", flush=True)

    rot_all, stale_all, destroy_all = [], [], []
    aa_c, wb_c, f_c, aa_a, wb_a, aa_o, wb_o = ([] for _ in range(7))
    bulk_minmax = []
    for s in SEEDS:
        stream, cache = R.build_life_cache(s, quick=QUICK)
        pr = P.probe_retention(cache, CFG)                            # the 3-curve instrument (all-tap depth)
        rot_all.append(pr["rotation"]); stale_all.append(pr["staleness"]); destroy_all.append(pr["destruction"])
        # context references on the SAME lifelong stream: committed loop, always-pay, oracle
        hf = R.committed_hf(s); sig = P.sig_tap_drift_direction(cache)
        r_c = P.run_economy_p9(cache, hf, CFG, **R.COMMITTED_LOOP)
        r_a = P.run_economy_p9(cache, hf, CFG, gate="always", sleep_policy="grid", cadence_every=8, cbrs=True)
        r_o = P.run_economy_p9(cache, hf, CFG, gate="oracle", sleep_policy="grid", cadence_every=8, cbrs=True)
        aa_c.append(r_c["aa"]); wb_c.append(r_c["worst_bwt"]); f_c.append(r_c["firefrac"])
        aa_a.append(r_a["aa"]); wb_a.append(r_a["worst_bwt"])
        aa_o.append(r_o["aa"]); wb_o.append(r_o["worst_bwt"])
        bd = cache["sig"]["bulkdrift"]; bulk_minmax.append((float(bd.min()), float(bd.max())))
        print(f"  seed {s}: rotation {pr['rotation'][-1]:.3f} staleness {pr['staleness'][-1]:.3f} "
              f"DESTRUCTION {pr['destruction'][-1]:.3f} (birth-refit {pr['destroy0']:.3f}) | "
              f"committed AA={r_c['aa']:.3f} wBWT={r_c['worst_bwt']:+.3f} f={r_c['firefrac']:.3f}", flush=True)
        del cache, stream

    K = min(len(r) for r in rot_all)
    rot = np.array([r[:K] for r in rot_all]); stale = np.array([r[:K] for r in stale_all])
    destroy = np.array([r[:K] for r in destroy_all])

    # verdict — keyed on curve (3): rotation-only iff final destruction retention within delta_acc of birth (1.0);
    # 'bulk forgets' iff destruction drops > delta_acc, sign >=4/5.
    destroy_final = destroy[:, -1]; destroy_min = destroy.min(1)
    forgets = int((destroy_final < 1.0 - CFG.DELTA_ACC).sum())
    verdict = ("bulk FORGETS (destruction decays > delta_acc, sign %d/5)" % forgets if forgets >= 4
               else "ROTATION-ONLY — the cheapness holds (re-fit retention within delta_acc of birth)")

    A = dict(seeds=np.array(SEEDS), delta_acc=np.array([CFG.DELTA_ACC]),
             bulkdrift_life=rot, frozenprobe_ret=stale, refitprobe_ret=destroy,
             safety_cfgs=np.array(["committed", "oracle", "always"]),
             aa_committed=np.array(aa_c), bwt_worst_committed=np.array(wb_c), forget_committed=np.array(f_c),
             aa_oracle=np.array(aa_o), bwt_worst_oracle=np.array(wb_o),
             aa_always=np.array(aa_a), bwt_worst_always=np.array(wb_a),
             **R.inv_arrays(g),
             inv_firefrac=np.array([R.med(f_c)]))
    man = R.base_manifest("P9.0", _HERE, SEEDS, QUICK, guards=g, n2_detail=n2d, wall_s=round(time.time() - t0, 1),
                          summary=dict(rotation_final=R.fmt(rot[:, -1]), staleness_final=R.fmt(stale[:, -1]),
                                       destruction_final=R.fmt(destroy_final), destruction_min=R.fmt(destroy_min),
                                       bulk_minmax=bulk_minmax, verdict=verdict,
                                       committed_aa=R.fmt(aa_c), committed_wbwt=R.fmt(wb_c), committed_f=R.fmt(f_c),
                                       oracle_aa=R.fmt(aa_o), oracle_wbwt=R.fmt(wb_o),
                                       always_aa=R.fmt(aa_a), always_wbwt=R.fmt(wb_a)))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p9.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P9.0 SUMMARY (wall {man['wall_s']}s) ==", flush=True)
    print(f"  rotation(final)    {R.fmt(rot[:, -1])}   (taps rotate — expected)", flush=True)
    print(f"  staleness(final)   {R.fmt(stale[:, -1])}   (a FIXED head fit at birth — what sleep fixes)", flush=True)
    print(f"  DESTRUCTION(final) {R.fmt(destroy_final)}  min {R.fmt(destroy_min)}   <- the VERDICT curve (2203.13381)", flush=True)
    print(f"  committed loop: AA {R.fmt(aa_c)} wBWT {R.fmt(wb_c)} f {R.fmt(f_c)}", flush=True)
    print(f"  oracle ref:     AA {R.fmt(aa_o)} wBWT {R.fmt(wb_o)}  | always-pay: AA {R.fmt(aa_a)} wBWT {R.fmt(wb_a)}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)


if __name__ == "__main__":
    main()
