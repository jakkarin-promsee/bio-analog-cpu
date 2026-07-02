"""
P8.1 — the gate bake-off (the awake detector, label-based error trigger; design.md sec 3 P8.1). SLEEP is held FIXED
(checkpoint cadence, uniform across arms) so the ONLY variable is the AWAKE gate = op (c). Sweep:
  always-pay (cost ceiling) | oracle (fire@true-onsets, the achievable awake reference) | absolute-theta | DDM
  (two-threshold error) | ADWIN (two-window error) | budget-gate (learned, reads a direction/drift feature, FD-guarded).
Score the FRONTIER: accuracy-held x GD-fire-fraction x FAR (+ worst-point BWT the safety read), all vs the oracle.
A gate is committed-eligible at the frontier knee: accuracy-held within delta_acc of oracle (paired), low f, FAR at/
below the stationary floor. f*=0.25 is a REFERENCE LINE, not a binary pass.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_1.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p8_1" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
GATES = ["always", "oracle", "abs", "ddm", "adwin", "budget"]


def fit_budget(cache, seed):
    """Fit the learned budget-gate offline (reads the class-direction drift feature + its delta; budget-regularized).
    Target = when firing is NEEDED = a SLEEP-ONLY head's batch error >= theta (its names slide between sleeps). Using
    the always-pay error would be circular (always-pay adapts -> error always low -> the gate learns 'never fire')."""
    r = P.run_economy(cache, lambda: P.make_stream_head("ranpac", CFG.NCLASS, seed=seed, **CFG.RANPAC_KNOB),
                      CFG, gate="abs", detector_kw={"theta": 1.1}, sleep_policy="checkpoint")  # theta>1 -> sleep-only
    td = cache["sig"]["tap_dir"]; err = np.nan_to_num(r["err_trace"], nan=0.0)
    feats = np.stack([P.BudgetGate._feat(td[i], td[max(0, i - 1)]) for i in range(len(td))])
    tgt = (err >= CFG.ABS_THETA).astype(float)
    return P.BudgetGate(lam=0.3, seed=seed).fit(feats, tgt)


def main():
    t0 = time.time()
    print(f"P8.1 — gate bake-off  (QUICK={QUICK}, seeds={SEEDS}, gates={GATES})", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    res = {g: dict(aa=[], f=[], far=[], mtd=[], wbwt=[]) for g in GATES}
    for s in SEEDS:
        stream, cache = caches[s]
        nu = np.array(stream["nuisance_steps"])
        bg = fit_budget(cache, s)
        for g in GATES:
            r = P.run_economy(cache, lambda: P.make_stream_head("ranpac", CFG.NCLASS, seed=s, **CFG.RANPAC_KNOB),
                              CFG, gate=g, trigger="error_ema", sleep_policy="checkpoint",
                              budget_gate=(bg if g == "budget" else None))
            m = P.mtd_far(r["fires"], stream)
            res[g]["aa"].append(r["aa"]); res[g]["f"].append(r["firefrac"])
            res[g]["far"].append(float(r["fires"][nu].mean())); res[g]["mtd"].append(m["mtd"])
            res[g]["wbwt"].append(r["worst_bwt"])
        print(f"  seed {s}: " + " | ".join(f"{g} AA={res[g]['aa'][-1]:.3f} f={res[g]['f'][-1]:.2f} FAR={res[g]['far'][-1]:.2f}"
                                           for g in ("oracle", "ddm", "adwin")), flush=True)

    A = dict(seeds=np.array(SEEDS), gates=np.array(GATES))
    for g in GATES:
        A[f"accheld_{g}"] = np.array(res[g]["aa"]); A[f"firefrac_{g}"] = np.array(res[g]["f"])
        A[f"far_{g}"] = np.array(res[g]["far"]); A[f"mtd_{g}"] = np.array(res[g]["mtd"])
        A[f"bwt_worst_{g}"] = np.array(res[g]["wbwt"])
    A["inv_partial_fit"] = np.array([1.0]); A["inv_cache_replay"] = np.array([1.0])
    A["inv_firefrac"] = np.array([R.med(res[g]["f"]) for g in GATES])

    oracle_aa = R.med(res["oracle"]["aa"])
    def verdict(g):
        d_aa = R.med(res[g]["aa"]) - oracle_aa
        held = abs(d_aa) <= 0.02 or R.med(res[g]["aa"]) >= oracle_aa
        clean = R.med(res[g]["far"]) <= R.med(res["oracle"]["far"]) + 1e-6
        if g in ("always", "oracle"):
            return "ceiling" if g == "always" else "reference"
        if held and clean:
            return "committed-eligible"
        return "held-not-clean" if held else ("false-fires" if not clean else "drops-acc")
    man = R.base_manifest("P8.1", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1),
                          sleep_policy="checkpoint", trigger="error_ema",
                          summary={g: dict(aa=R.fmt(res[g]["aa"]), f=R.med(res[g]["f"]), far=R.med(res[g]["far"]),
                                           mtd=R.med(res[g]["mtd"]), wbwt=R.med(res[g]["wbwt"]),
                                           verdict=verdict(g)) for g in GATES})
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.1 SUMMARY (median; oracle AA={oracle_aa:.3f}) ==", flush=True)
    print(f"  {'gate':8s} {'AA':>16s} {'f':>6s} {'FAR':>6s} {'MTD':>6s} {'wBWT':>7s}  verdict", flush=True)
    for g in GATES:
        print(f"  {g:8s} {R.fmt(res[g]['aa']):>16s} {R.med(res[g]['f']):.3f} {R.med(res[g]['far']):.3f} "
              f"{R.med(res[g]['mtd']):.1f} {R.med(res[g]['wbwt']):+.3f}  {verdict(g)}", flush=True)
    print(f"  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
