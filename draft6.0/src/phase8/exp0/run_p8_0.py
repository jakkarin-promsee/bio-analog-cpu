"""
P8.0 — bench + guards + the live drift + the drift-visibility sanity panel + the always-pay/oracle references
(design.md sec 3 P8.0). Turns on the REAL mechanism (SCFF + namer LIVE) for the first time and asks:
  * do ALL guards pass (partial_fit_equiv, live_path_anchor, scff_static_frozen, meter_proxy, detector_far,
    cache_replay, fd_budget_gate) -- ANY fail -> STOP;
  * is the streaming schedule sound (gradual class onset -> CONTINUOUS drift), pinned + reported;
  * how fast + how bounded is the live SCFF drift (bulk_drift -- "the bulk doesn't forget");
  * is the DETECTION PROBLEM well-posed: do the label-free signals move at REAL onsets and NOT at the NUISANCE
    covariate shift, and do error-rate and tap-drift measure DIFFERENT things (else the P8.2 trigger bake-off
    compares two views of one signal);
  * the always-pay cost ceiling + the oracle-cadence achievable reference.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_0.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p8_0" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS


def run_guards():
    print("== GUARDS (any fail -> STOP) ==", flush=True)
    g = {}
    g["partial_fit_equiv"], _ = P.partial_fit_equiv_guard(verbose=True)
    g["fd_budget_gate"], _ = P.fd_budget_gate_guard(verbose=True)
    g["meter_proxy"], _ = P.meter_proxy_guard(CFG, verbose=True)
    g["detector_far"], _ = P.detector_far_guard(CFG, verbose=True)
    g["scff_static_frozen"], _ = P.scff_static_frozen_guard(CFG, verbose=True)
    g["live_path_anchor"], _ = P.live_path_anchor_guard(CFG, verbose=True)
    g["cache_replay"], _ = P.cache_replay_guard(CFG, verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print("  -> all guards PASS", flush=True)
    return g


def driftvis_row(stream, sig, err):
    """Normalized [tap_dir, tap_mag, error] at [calib, real-onset, nuisance] -> each signal / its calib baseline.
    A well-posed problem: error+tap-dir elevated at REAL onsets (not nuisance); tap-mag elevated at NUISANCE (not
    onsets) -> the three measure DIFFERENT things."""
    onset = np.array([i for i, st in enumerate(stream["steps"]) if st["seg"].startswith("onset")])
    calib = np.array(stream["calib_steps"]); nuis = np.array(stream["nuisance_steps"])
    sigs = {"tap_dir": sig["tap_dir"], "tap_mag": sig["tap_mag"], "error": err}
    row = np.zeros((3, 3))                                             # [seg, sig]
    for j, nm in enumerate(["tap_dir", "tap_mag", "error"]):
        s = np.nan_to_num(sigs[nm], nan=np.nanmean(sigs[nm]))
        base = s[calib].mean() + 1e-9
        row[0, j] = s[calib].mean() / base; row[1, j] = s[onset].mean() / base; row[2, j] = s[nuis].mean() / base
    return row


def main():
    t0 = time.time()
    print(f"P8.0 — bench + guards + live drift + drift-visibility  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g = run_guards()

    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    n_steps = caches[SEEDS[0]][0]["n_steps"]
    hf = lambda s: P.make_stream_head("ranpac", CFG.NCLASS, seed=s, **CFG.RANPAC_KNOB)

    bulk = np.zeros((len(SEEDS), n_steps)); driftvis = np.zeros((len(SEEDS), 3, 3))
    acc_always, acc_oracle, f_always, f_oracle, far_always, far_oracle = ([] for _ in range(6))
    for i, s in enumerate(SEEDS):
        stream, cache = caches[s]
        bulk[i] = cache["sig"]["bulkdrift"][:n_steps]
        r_al = P.run_economy(cache, lambda: hf(s), CFG, gate="always", sleep_policy="checkpoint")
        r_or = P.run_economy(cache, lambda: hf(s), CFG, gate="oracle", sleep_policy="checkpoint")
        driftvis[i] = driftvis_row(stream, cache["sig"], r_al["err_trace"])
        nu = np.array(stream["nuisance_steps"])
        acc_always.append(r_al["aa"]); acc_oracle.append(r_or["aa"])
        f_always.append(r_al["firefrac"]); f_oracle.append(r_or["firefrac"])
        far_always.append(float(r_al["fires"][nu].mean())); far_oracle.append(float(r_or["fires"][nu].mean()))
        print(f"  seed {s}: bulk_drift {bulk[i].min():.3f}..{bulk[i].max():.3f} | always AA={r_al['aa']:.3f} "
              f"f={r_al['firefrac']:.2f} FAR={far_always[-1]:.2f} | oracle AA={r_or['aa']:.3f} f={r_or['firefrac']:.3f}", flush=True)

    A = dict(seeds=np.array(SEEDS), gates=np.array(["always", "oracle"]),
             bulkdrift=bulk, driftvis=driftvis, driftvis_labels=np.array(["tap_dir", "tap_mag", "error"]),
             accheld_always=np.array(acc_always), accheld_oracle=np.array(acc_oracle),
             firefrac_always=np.array(f_always), firefrac_oracle=np.array(f_oracle),
             far_always=np.array(far_always), far_oracle=np.array(far_oracle),
             inv_partial_fit=np.array([1.0 if g["partial_fit_equiv"] else 0.0]),
             inv_live_path=np.array([1.0 if g["live_path_anchor"] else 0.0]),
             inv_scff_frozen=np.array([1.0 if g["scff_static_frozen"] else 0.0]),
             inv_meter_proxy=np.array([1.0 if g["meter_proxy"] else 0.0]),
             inv_detector_far=np.array([1.0 if g["detector_far"] else 0.0]),
             inv_cache_replay=np.array([1.0 if g["cache_replay"] else 0.0]),
             inv_fdguard=np.array([1.0 if g["fd_budget_gate"] else 0.0]),
             inv_firefrac=np.array([R.med(f_always), R.med(f_oracle)]))
    man = R.base_manifest("P8.0", _HERE, SEEDS, QUICK, CFG, guards=g, wall_s=round(time.time() - t0, 1),
                          n_steps=int(n_steps),
                          summary=dict(bulk_min=float(bulk.min()), bulk_max=float(bulk.max()),
                                       acc_always=R.med(acc_always), acc_oracle=R.med(acc_oracle),
                                       f_always=R.med(f_always), f_oracle=R.med(f_oracle),
                                       far_always=R.med(far_always), far_oracle=R.med(far_oracle),
                                       driftvis_median=np.median(driftvis, 0).round(2).tolist()))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    dv = np.median(driftvis, 0)
    print(f"\n== P8.0 SUMMARY ==\n  bulk_drift {bulk.min():.3f}..{bulk.max():.3f}  (bounded -> the bulk doesn't forget)", flush=True)
    print(f"  drift-visibility (normalized to calib): [calib/onset/nuis] x [tap_dir/tap_mag/error]", flush=True)
    for r, lab in zip(dv, ["calib   ", "onset   ", "nuisance"]):
        print(f"    {lab}: tap_dir={r[0]:.2f}  tap_mag={r[1]:.2f}  error={r[2]:.2f}", flush=True)
    print(f"  always-pay ceiling AA={R.med(acc_always):.3f} f={R.med(f_always):.2f} FAR={R.med(far_always):.2f}", flush=True)
    print(f"  oracle-cadence ref AA={R.med(acc_oracle):.3f} f={R.med(f_oracle):.3f} FAR={R.med(far_oracle):.2f}  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
