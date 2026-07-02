"""
P9.2 — readout-aware sleep cadence: the consolidation DEPTH (latent replay) (design.md §3 P9.2). Swept variable = the
sleep-consolidation feature depth ∈ {all-tap (P8 default) · trunc-K (the deployed short reader, S9) · per-depth (a
single sharp layer)}. Score worst-point A6-BWT × metered sleep-cost. Read: trunc-depth holds A6 at strictly lower
sleep cost -> adopt depth-matched consolidation / depth doesn't matter -> keep P8's all-tap cadence, note it. The
depth verdict is read at the COMMITTED frequency (grid-8); the depth applies to the whole loop (awake + sleep re-slice
the same reader). Inherits P9.1's N2 (tunes on the possibly-slowed drift — the P8 'cadence is drift-rate-conditional'
debt). sleep-cost prices the Fdim-scaled solve/Gram term (trunc re-slices the top of the full forward -> the SCFF
re-forward is unchanged, reported apart).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_2.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p9_2" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
DEPTHS = CFG.SLEEP_DEPTHS                                             # ['alltap','truncK','perdepth']
SCFF_DIMS = [CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH


def main():
    t0 = time.time()
    committed_n2 = R.load_prior("exp1", "committed_n2", None)          # tune on P9.1's slowed drift (coupled loop)
    n2_fac, needs_llrd, rho = R.n2_view_for(committed_n2)
    print(f"P9.2 — consolidation depth  (QUICK={QUICK}, seeds={SEEDS}, inherited N2={committed_n2})", flush=True)
    g, _ = R.run_all_guards(verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)

    per = {dp: dict(acc=[], bwt=[], cost=[], reforward=[]) for dp in DEPTHS}
    for s in SEEDS:
        cf = (lambda dims, ss: P.make_llrd_cell(dims, ss, rho=rho, late=CFG.N2_LATE_LAYERS)) if needs_llrd else None
        _, cache = R.build_life_cache(s, quick=QUICK, store_reps=True, cell_factory=cf)
        hf = R.committed_hf(s)
        probe_n = next((r["phi_probe"].shape[0] for r in cache["steps"] if "phi_probe" in r), CFG.PROBE_N)
        for dp in DEPTHS:
            r = P.run_economy_p9(cache, hf, CFG, **{**R.COMMITTED_LOOP, "sleep_depth": dp, "n2_view": n2_fac()})
            sc = P.sleep_cost_at_depth(CFG, R.HEAD, dp, r["nsleep"], probe_n, SCFF_DIMS)
            per[dp]["acc"].append(r["aa"]); per[dp]["bwt"].append(r["worst_bwt"])
            per[dp]["cost"].append(sc["sleep_cost"]); per[dp]["reforward"].append(sc["reforward_e"])
        print(f"  seed {s}: " + " | ".join(
            f"{dp} AA={per[dp]['acc'][-1]:.3f} wBWT={per[dp]['bwt'][-1]:+.3f} cost={per[dp]['cost'][-1]:.2e}"
            for dp in DEPTHS), flush=True)
        del cache

    # verdict: adopt trunc iff worst-point A6-BWT held (within delta of all-tap, paired) at E-ratio >= SLEEP_COST_ERATIO
    base_bwt = per["alltap"]["bwt"]; base_cost = R.med(per["alltap"]["cost"])
    eval_depth = {}
    for dp in DEPTHS:
        if dp == "alltap":
            continue
        held = R.med(per[dp]["bwt"]) >= R.med(base_bwt) - CFG.DELTA_ACC
        eratio = base_cost / max(R.med(per[dp]["cost"]), 1e-9)
        eval_depth[dp] = dict(a6_held=bool(held), eratio=float(eratio),
                              adopt=bool(held and eratio >= CFG.SLEEP_COST_ERATIO))
    adopt = next((dp for dp in ("truncK", "perdepth") if eval_depth.get(dp, {}).get("adopt")), None)
    committed_depth = adopt or "alltap"
    verdict = (f"adopt {committed_depth} (A6 held, E-ratio {eval_depth[committed_depth]['eratio']:.1f}x)"
               if adopt else "keep ALL-TAP (trunc did not hold A6 within delta_acc)")

    A = dict(seeds=np.array(SEEDS), depths=np.array(DEPTHS), **R.inv_arrays(g),
             inv_firefrac=np.array([R.med([1.0])]))
    for dp in DEPTHS:
        A[f"bwt_worst_{dp}"] = np.array(per[dp]["bwt"]); A[f"sleepcost_{dp}"] = np.array(per[dp]["cost"])
        A[f"accheld_{dp}"] = np.array(per[dp]["acc"])
    man = R.base_manifest("P9.2", _HERE, SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          inherited_n2=committed_n2, committed_depth=committed_depth, depth_eval=eval_depth,
                          summary={dp: dict(acc=R.fmt(per[dp]["acc"]), wbwt=R.fmt(per[dp]["bwt"]),
                                            sleep_cost=R.fmt(per[dp]["cost"]),
                                            reforward=R.fmt(per[dp]["reforward"])) for dp in DEPTHS} | {"verdict": verdict})
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p9.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P9.2 SUMMARY (wall {man['wall_s']}s, inherited N2={committed_n2}) ==", flush=True)
    for dp in DEPTHS:
        print(f"  {dp:8s}: AA {R.fmt(per[dp]['acc'])} wBWT {R.fmt(per[dp]['bwt'])} "
              f"sleep-cost {R.fmt(per[dp]['cost'])} (reforward {R.fmt(per[dp]['reforward'])})", flush=True)
    for dp, e in eval_depth.items():
        print(f"  {dp}: A6-held={e['a6_held']} E-ratio={e['eratio']:.1f}x adopt={e['adopt']}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)


if __name__ == "__main__":
    main()
