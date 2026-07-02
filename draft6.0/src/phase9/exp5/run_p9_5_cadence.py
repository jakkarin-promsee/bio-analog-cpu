"""
P9.5 addendum — the sleep-CADENCE re-confirm (the freeze-driven frequency sub-table). The initial P9.5 assemble (the
committed grid-8 loop, which == the P8.6 shipped object bit-for-bit since every P9 knob was struck/kept) did NOT clear
the worst-point oracle-veto on the lifelong revisit stream: 2/5 seeds' worst-point (pre-sleep) BWT is materially
more-negative than the known-boundary oracle. Diagnosis: the gap is the committed DDM awake-gate's FIRE-timing trailing
the boundary-onset oracle (both sleep on the SAME grid cadence — run_economy_p9 line 675), NOT sleep frequency. The gate
is COMMITTED / out of P9 scope (design §0.2), so the one P9-legal lever is the sleep CADENCE (S7 / P9.2's deferred
frequency re-confirm — deferred under 'N2 struck', now OWED by the freeze failure). Denser sleep repairs the PRE-sleep
worst-point state, so it MIGHT close the veto even though the gap is fire-timing-driven — an empirical question.

This sweeps cadence_every ∈ {2,4,6,8} on the lifelong stream (committed loop otherwise), scoring the SAME three freeze
cuts, all vs INTERNAL references (NEVER the P10 baseline): (1) worst-point BWT paired-sign veto vs the oracle at the
SAME cadence (neg <= 1); (2) AA-held within delta_acc of the P8.6 shipped loop (grid-8 base AA); (3) GD-share <= 0.25.
The cache is cadence-INDEPENDENT (the SCFF trajectory does not depend on the loop), so build ONCE per seed and replay all
cadences on it. Read (incl. failure): a denser cadence clears the veto at held AA + GD-share <= 0.25 -> commit it,
re-freeze / no cadence clears it -> the gap is the committed gate's fire-timing (out of P9 scope) -> NAME it to P10.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_5_cadence.py [--quick]
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

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p9_5_cadence" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
CADENCES = [2, 4, 8] if QUICK else [2, 4, 6, 8]                       # denser than (and incl.) the committed grid-8
SHIPPED_CADENCE = 8                                                    # the P8.6 committed loop's cadence (the AA ref)


def loop(cache, hf, gate, cad):
    return P.run_economy_p9(cache, hf, CFG, **{**R.COMMITTED_LOOP, "gate": gate, "cadence_every": cad})


def main():
    t0 = time.time()
    print(f"P9.5 cadence re-confirm  (QUICK={QUICK}, seeds={SEEDS}, cadences={CADENCES})", flush=True)
    g, _ = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)

    asm = {c: dict(bwt=[], aa=[], gd=[], nslp=[]) for c in CADENCES}
    orc = {c: dict(bwt=[]) for c in CADENCES}
    base_aa = []                                                       # the shipped loop (grid-8 ddm) AA — the AA ref
    for s in SEEDS:
        _, cache = R.build_life_cache(s, quick=QUICK, store_reps=False)
        hf = R.committed_hf(s)
        base_aa.append(loop(cache, hf, "ddm", SHIPPED_CADENCE)["aa"])
        for c in CADENCES:
            ra = loop(cache, hf, "ddm", c); ro = loop(cache, hf, "oracle", c)
            met = P.loop_energy(CFG, R.HEAD, ra, cache)
            asm[c]["bwt"].append(ra["worst_bwt"]); asm[c]["aa"].append(ra["aa"])
            asm[c]["gd"].append(met["gdshare"]); asm[c]["nslp"].append(ra["nsleep"])
            orc[c]["bwt"].append(ro["worst_bwt"])
        print(f"  seed {s}: " + " | ".join(
            f"c{c} wBWT={asm[c]['bwt'][-1]:+.3f}/orc{orc[c]['bwt'][-1]:+.3f} nslp={asm[c]['nslp'][-1]}"
            for c in CADENCES), flush=True)
        del cache

    base_aa_med = R.med(base_aa)
    print(f"\n  shipped (grid-8) base AA = {base_aa_med:.3f}  (AA-held bar = {base_aa_med - CFG.DELTA_ACC:.3f})", flush=True)
    print(f"  {'cadence':>8} {'neg/5':>6} {'AA':>18} {'AA-held':>8} {'GD-share':>18} {'GD<=.25':>8} {'nsleep':>7} {'FREEZE?':>8}", flush=True)
    winner = None
    for c in CADENCES:
        neg = R.paired_sign_neg(asm[c]["bwt"], orc[c]["bwt"], tol=CFG.DELTA_ACC)
        veto_ok = neg <= len(SEEDS) - 4
        aa_ok = R.med(asm[c]["aa"]) >= base_aa_med - CFG.DELTA_ACC
        gd_ok = R.med(asm[c]["gd"]) <= CFG.GD_SHARE_CAP
        frozen = veto_ok and aa_ok and gd_ok
        if frozen and winner is None:
            winner = c
        print(f"  {c:>8} {neg:>6} {R.fmt(asm[c]['aa']):>18} {str(aa_ok):>8} {R.fmt(asm[c]['gd']):>18} "
              f"{str(gd_ok):>8} {R.med(asm[c]['nslp']):>7.0f} {str(frozen):>8}", flush=True)

    print(f"\n== CADENCE RE-CONFIRM (wall {round(time.time()-t0,1)}s) ==", flush=True)
    if winner is not None:
        print(f"  WINNER: cadence_every={winner} clears the oracle-veto (neg<=1) at held AA + GD-share<=0.25 "
              f"-> commit as the lifelong cadence, re-freeze.", flush=True)
    else:
        print(f"  NO cadence clears the oracle-veto -> the worst-point gap is the committed DDM gate's fire-timing "
              f"(out of P9 scope), NOT sleep frequency. Name it to P10; the loop regresses 0/5 vs the shipped object.", flush=True)


if __name__ == "__main__":
    main()
