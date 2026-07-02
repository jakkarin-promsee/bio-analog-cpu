"""
P8.2 — the trigger signal (orthogonal to the detector; design.md sec 3 P8.2). On the drift stream with harmful (real
class onsets) + nuisance (covariate) drift, race the SIGNAL feeding a COMMON detection rule (threshold-crossing
calibrated on the stationary interior -- so the only variable is the signal):
  error_ema  = the LABELED reference (precise, lags; a labeled magnitude, NOT spine-clean)
  tap_dir    = the committed candidate: MMD drift ALONG post-norm/class structure (spine-clean, nuisance-invariant)
  tap_mag    = the false-fire NULL: MMD on the RAW input (a magnitude-of-shift; fires on nuisance by construction)
  driftlens  = the label-free reference: post-norm embedding-distance MMD (nuisance-invariant)
  studd      = the conservative arm: student mimic-loss (fewer alarms, slower)
Score MTD x FAR. Verdict: tap_dir EARNS-EARLY iff MTD(tap)<MTD(error) AND FAR(tap,nuis)<=FAR(error,nuis); else
early-but-noisy / no-lead. The magnitude null is EXPECTED to false-fire on nuisance (the spine demonstration).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_2.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p8_2" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
TRIGS = ["error_ema", "tap_dir", "tap_mag", "driftlens", "studd"]


def signals(cache, stream):
    """Build every trigger's per-step signal. error_ema + studd need a fitted head's traces (an always-pay run)."""
    r = P.run_economy(cache, lambda: P.make_stream_head("ranpac", CFG.NCLASS, seed=0, **CFG.RANPAC_KNOB),
                      CFG, gate="always", sleep_policy="checkpoint")
    err = np.nan_to_num(r["err_trace"], nan=0.0)
    return dict(error_ema=P.sig_error_ema(err, CFG.EMA_BETA),
                tap_dir=P.sig_tap_drift_direction(cache), tap_mag=P.sig_tap_drift_magnitude(cache),
                driftlens=P.sig_driftlens(cache), studd=P.sig_studd(r["studd"]))


def main():
    t0 = time.time()
    print(f"P8.2 — trigger bake-off  (QUICK={QUICK}, seeds={SEEDS}, triggers={TRIGS})", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    res = {t: dict(mtd=[], far=[], excess=[], mtfa=[], det=[]) for t in TRIGS}
    for s in SEEDS:
        stream, cache = caches[s]
        sg = signals(cache, stream)
        for t in TRIGS:
            thr = P.calibrate_threshold(sg[t], stream["calib_steps"])
            fires = P.detect_crossings(sg[t], thr)
            m = P.mtd_far(fires, stream)
            res[t]["mtd"].append(m["mtd"]); res[t]["far"].append(m["far"])
            res[t]["excess"].append(m["excess_far"]); res[t]["mtfa"].append(m["mtfa"]); res[t]["det"].append(m["n_detected"])
        print(f"  seed {s}: tap_dir MTD={res['tap_dir']['mtd'][-1]:.0f} FAR={res['tap_dir']['far'][-1]:.2f} | "
              f"error MTD={res['error_ema']['mtd'][-1]:.0f} FAR={res['error_ema']['far'][-1]:.2f} | "
              f"tap_mag FAR={res['tap_mag']['far'][-1]:.2f}", flush=True)

    A = dict(seeds=np.array(SEEDS), triggers=np.array(TRIGS))
    for t in TRIGS:
        A[f"mtd_{t}"] = np.array(res[t]["mtd"]); A[f"far_{t}"] = np.array(res[t]["far"])
        A[f"excess_{t}"] = np.array(res[t]["excess"]); A[f"mtfa_{t}"] = np.array(res[t]["mtfa"])
    A["inv_partial_fit"] = np.array([1.0]); A["inv_detector_far"] = np.array([1.0])
    A["inv_far_by_trig"] = np.array([R.med(res[t]["far"]) for t in TRIGS])

    # verdict uses EXCESS FAR (above each arm's OWN stationary floor -- design C2), not raw FAR
    mtd_e, exc_e = R.med(res["error_ema"]["mtd"]), R.med(res["error_ema"]["excess"])
    mtd_t, exc_t = R.med(res["tap_dir"]["mtd"]), R.med(res["tap_dir"]["excess"])
    if mtd_t < mtd_e and exc_t <= exc_e + 0.02:
        tap_verdict = "earns-early"
    elif exc_t <= exc_e + 0.02:
        tap_verdict = "no-lead (spine-clean, but does not beat error MTD)"
    else:
        tap_verdict = "early-but-noisy"
    mag_far = R.med(res["tap_mag"]["far"])
    man = R.base_manifest("P8.2", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1),
                          detection_rule="threshold-crossing @ calib-interior 97.5pct*1.10",
                          tap_verdict=tap_verdict, magnitude_null_far=mag_far,
                          summary={t: dict(mtd=R.fmt(res[t]["mtd"]), far=R.fmt(res[t]["far"]),
                                           excess_far=R.med(res[t]["excess"]), mtfa=R.med(res[t]["mtfa"])) for t in TRIGS})
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.2 SUMMARY (median) ==", flush=True)
    print(f"  {'trigger':10s} {'MTD':>16s} {'FAR(nuis)':>16s} {'excess':>7s} {'MTFA':>7s}", flush=True)
    for t in TRIGS:
        print(f"  {t:10s} {R.fmt(res[t]['mtd']):>16s} {R.fmt(res[t]['far']):>16s} {R.med(res[t]['excess']):.3f} "
              f"{R.med(res[t]['mtfa']):.1f}", flush=True)
    print(f"  tap-drift verdict: {tap_verdict}", flush=True)
    print(f"  magnitude-null FAR on nuisance = {mag_far:.3f} (expected HIGH -> the spine demonstration)", flush=True)
    print(f"  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
