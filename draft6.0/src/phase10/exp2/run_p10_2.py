"""
P10.2 — the CADENCE FRONTIER (the family) (design §3 P10.2 + §10 E2). Swept variable = the sleep cadence grid ∈
{4,5,6,8,12,16} (the ONLY dial that moves; the object is otherwise frozen — every LEARNED part identical), object
frozen, 5 seeds. Score accuracy × energy × worst-BWT. This re-races the exact P9.5 internal frontier (grid-4
bit-exact reproduced) but now positions it as a cost-frontier FAMILY for P10's external scaling story + meters each
grid's energy. grid-12 = the §10 post-close gap-filler between grid-8 and grid-16 (never run before, not even in
P9.5) — it makes the Tier-2 break's shape legible on the AA-vs-energy trend the author read as super-linear.

Read (pinned BLIND): grid-4 is the committed headline — NEVER swapped, always plotted. A Tier-1 SHOWCASE REP
(visualization only) may be named iff Pareto-non-dominated AND its worst-point BWT is within delta_acc of grid-4's
(paired) AND its energy is IQR-disjointly lower -> grid-5 the only candidate (grid-6 -0.087 fails the BWT gate).
Tier-2 break confirmed iff grid-8 worst-BWT < -delta vs oracle (forgetting) and/or grid-16 AA drop > delta.
grid-12 read (§10, expectation-free): does it fail the veto (grid-8's axis), AA-held (grid-16's axis), both, or hold?
§10 E5 (round 2): cliff PROBES {7,13,14,15} localize the two cliff edges (safety in 6..8, accuracy in 12..16) —
characterization probes, NOT family members (CAD_FAMILY + its guard untouched); per-probe read = which side of each
cliff (absolute: |wBWT - g4's| <= delta = safe; AA >= g4 - delta = holds), banked wherever the numbers land.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_2.py [--quick]
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
import p10lib as P                                                     # noqa: E402
import p10cfg as CFG                                                   # noqa: E402
import p10run as R                                                     # noqa: E402
import plot_p10                                                        # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p10_2" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
GRIDS = sorted([4, 5, 6, 8, 12, 16] + [7, 13, 14, 15])                 # family (+g12, §10 E2) + the §10 E5 cliff probes
PROBES = [7, 13, 14, 15]                                               # characterization probes, NOT family members


def main():
    t0 = time.time()
    print(f"P10.2 — cadence frontier  (QUICK={QUICK}, seeds={SEEDS}, grids={GRIDS})", flush=True)
    g = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)

    acc = {gr: [] for gr in GRIDS}; en = {gr: [] for gr in GRIDS}; wbwt = {gr: [] for gr in GRIDS}
    orc = {gr: [] for gr in GRIDS}; gd = {gr: [] for gr in GRIDS}; nslp = {gr: [] for gr in GRIDS}
    for s in SEEDS:
        _, cache = R.build_life_cache(s, quick=QUICK, store_reps=False, verbose=False)
        hf = R.committed_hf(s)
        fam = P.cadence_family_runner(cache, hf, CFG, grids=GRIDS)
        for gr in GRIDS:
            ra = fam[gr]["res"]; met = P.ours_stream_energy(CFG, cache, ra, substrate="analog")
            acc[gr].append(ra["aa"]); en[gr].append(met["total"]); wbwt[gr].append(ra["worst_bwt"])
            orc[gr].append(fam[gr]["oracle_worst_bwt"]); gd[gr].append(met["gdshare"]); nslp[gr].append(ra["nsleep"])
        print(f"  seed {s}: " + " | ".join(f"g{gr} aa={acc[gr][-1]:.3f} wBWT={wbwt[gr][-1]:+.3f}" for gr in GRIDS), flush=True)
        del cache

    # --- Tier-1 showcase-rep gate (visualization only; grid-4 is ALWAYS the committed headline) ---
    dacc = CFG.DELTA_ACC
    g4_bwt = np.array(wbwt[4])
    rep = None
    for gr in [5, 6]:                                                   # only Tier-1 non-headline candidates
        within = abs(R.med(wbwt[gr]) - R.med(g4_bwt)) <= dacc
        cheaper = R.med(en[gr]) < R.med(en[4]) and (np.percentile(en[gr], 75) < np.percentile(en[4], 25))
        if within and cheaper and rep is None:
            rep = gr
    tier1_rep = f"grid-{rep}" if rep else "none (grid-4 stands alone; grid-6 fails the BWT gate)"

    # --- Tier-2 break (+ the §10 grid-12 both-axis read, expectation-free) ---
    g8_break = R.paired_sign_neg(wbwt[8], orc[8], tol=dacc) > len(SEEDS) - 4
    g16_aa_drop = R.med(acc[16]) < R.med(acc[4]) - dacc
    g12_veto_fail = R.paired_sign_neg(wbwt[12], orc[12], tol=dacc) > len(SEEDS) - 4
    g12_aa_drop = R.med(acc[12]) < R.med(acc[4]) - dacc

    # --- §10 E5 cliff localization (per probe: which side of each cliff — absolute reads, expectation-free) ---
    # safety side: worst-BWT within delta of grid-4's (safe) vs beyond (broken); accuracy side: AA >= g4 - delta.
    cliff = {}
    for gr in GRIDS:
        safe = abs(R.med(wbwt[gr]) - R.med(wbwt[4])) <= dacc
        aa_holds = R.med(acc[gr]) >= R.med(acc[4]) - dacc
        cliff[gr] = dict(safety_holds=bool(safe), aa_holds=bool(aa_holds),
                         wbwt=R.med(wbwt[gr]), aa=R.med(acc[gr]), nsleep=int(R.med(nslp[gr])))
    safety_edge = next((gr for gr in GRIDS if not cliff[gr]["safety_holds"]), None)
    aa_edge = next((gr for gr in GRIDS if not cliff[gr]["aa_holds"]), None)

    print(f"\n  == CADENCE FRONTIER (delta_acc={dacc}) ==", flush=True)
    print(f"  {'grid':>5} {'acc':>18} {'energy(pJ)':>12} {'worst-BWT':>18} {'oracle-wBWT':>12} {'GD-share':>10} {'nsleep':>7}", flush=True)
    for gr in GRIDS:
        print(f"  {('g'+str(gr)):>5} {R.fmt(acc[gr]):>18} {R.med(en[gr]):>12.3e} {R.fmt(wbwt[gr]):>18} "
              f"{R.med(orc[gr]):>+12.3f} {R.med(gd[gr]):>10.3f} {R.med(nslp[gr]):>7.0f}", flush=True)
    print(f"  grid-4 = COMMITTED HEADLINE (never swapped). Tier-1 showcase rep: {tier1_rep}", flush=True)
    print(f"  Tier-2 break: grid-8 forgets (veto-fail vs oracle)={g8_break} | grid-16 AA drop>delta={g16_aa_drop}", flush=True)
    print(f"  grid-12 (the §10 gap-filler): veto-fail={g12_veto_fail} | AA drop>delta={g12_aa_drop}", flush=True)
    print(f"  §10 E5 cliff map (per grid: safety-holds / AA-holds / nsleep):", flush=True)
    for gr in GRIDS:
        c = cliff[gr]
        print(f"    g{gr:<3} safety={'HOLD' if c['safety_holds'] else 'BROKEN'} (wBWT {c['wbwt']:+.3f}) | "
              f"AA={'HOLD' if c['aa_holds'] else 'DROP'} ({c['aa']:.3f}) | nsleep {c['nsleep']}", flush=True)
    print(f"  -> SAFETY cliff edge: first broken grid = g{safety_edge} | ACCURACY cliff edge: first dropped grid = g{aa_edge}", flush=True)

    A = dict(seeds=np.array(SEEDS), grids=np.array([f"g{gr}" for gr in GRIDS]),
             tier1_rep=np.array(tier1_rep), **R.inv_arrays(g))
    for gr in GRIDS:
        A[f"acc_g{gr}"] = np.array(acc[gr]); A[f"energy_g{gr}"] = np.array(en[gr])
        A[f"bwtworst_g{gr}"] = np.array(wbwt[gr]); A[f"gdshare_g{gr}"] = np.array(gd[gr])
    man = R.base_manifest("P10.2", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          grids=GRIDS, probes=PROBES, tier1_rep=tier1_rep, grid4_headline_no_swap=True,
                          tier2_break=dict(grid8_forgets=bool(g8_break), grid16_aa_drop=bool(g16_aa_drop),
                                           grid12_veto_fail=bool(g12_veto_fail), grid12_aa_drop=bool(g12_aa_drop)),
                          cliff_map=cliff, safety_cliff_first_broken=safety_edge, accuracy_cliff_first_dropped=aa_edge,
                          summary={f"grid-{gr}": dict(acc=R.fmt(acc[gr]), energy=R.med(en[gr]),
                                                      worst_bwt=R.fmt(wbwt[gr]), gdshare=R.med(gd[gr]),
                                                      nsleep=R.med(nslp[gr])) for gr in GRIDS})
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.2 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
