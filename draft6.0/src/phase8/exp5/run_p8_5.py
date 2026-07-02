"""
P8.5 — the metered 80/20 (design.md sec 3 P8.5). The committed live loop metered vs the BP+replay energy model at
matched retention (same substrate table). GD-share = E[(c)+(d)]/E_total (the namer); SCFF-share = E[(a)+(b)]/E_total.
"80/20 confirmed" iff GD-share <= 0.25 with the committed gate on. bp_ratio = OURS E_total / BP+replay E_total (the
BP model does a backward pass EVERY step + full-weight writes + a replay mini-batch to reach OURS's retention -- NOT a
naive backward-every-step BP that forgets, a strawman). The FIRST non-proxy 80/20 the project has ever had.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_5.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p8_5" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
HEAD = "slda"                                                        # P8.4 committed SLDA over RanPAC (16.7x cheaper namer,
#                                                                      AA ties live) -> the deployed head realizes the 80/20
CONFIGS = [("committed", "ddm"), ("always-pay", "always")]           # gate-on (economy) vs no-gate (ceiling)


def main():
    t0 = time.time()
    print(f"P8.5 — metered 80/20  (QUICK={QUICK}, seeds={SEEDS}, head={HEAD})", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    knob = CFG.RANPAC_KNOB if HEAD == "ranpac" else CFG.SLDA_KNOB
    gdshare = {c: [] for c, _ in CONFIGS}; bp_ratio = []
    Fdim = None; scff_dims = [CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH
    bp_dims = None
    for s in SEEDS:
        stream, cache = caches[s]
        Fdim = cache["steps"][0]["phi_b"].shape[1]
        for cname, gate in CONFIGS:
            r = P.run_economy(cache, lambda: P.make_stream_head(HEAD, CFG.NCLASS, seed=s, **knob),
                              CFG, gate=gate, trigger="error_ema", sleep_policy="checkpoint", cbrs=True)
            m = P.meter_from_trace(CFG, HEAD, cache, r)
            gdshare[cname].append(m["gdshare"])
            if cname == "committed":
                # BP+replay energy model at matched retention (same substrate table); iso-weight-budget MLP shape
                nh = 3; bw = max(8, int(np.sqrt(P.ours_budget(CFG.DIM, CFG.WIDTH, CFG.DEPTH, CFG.NCLASS) / nh)))
                bp_dims = [CFG.DIM] + [bw] * nh + [CFG.NCLASS]
                bpm = P.bp_replay_energy(CFG, Fdim=CFG.DIM, C=CFG.NCLASS, n_steps=len(cache["steps"]),
                                         batch=CFG.BATCH, replay_batch=CFG.BATCH, bp_dims=bp_dims)
                bp_ratio.append(m["total"] / (bpm["total"] + 1e-30))
        print(f"  seed {s}: committed GD-share={gdshare['committed'][-1]:.3f} always GD-share={gdshare['always-pay'][-1]:.3f} "
              f"bp_ratio={bp_ratio[-1]:.3f}", flush=True)

    gd_committed = R.med(gdshare["committed"])
    confirmed = gd_committed <= 0.25
    A = dict(seeds=np.array(SEEDS), econ_configs=np.array([c for c, _ in CONFIGS]),
             bp_ratio=np.array(bp_ratio), inv_meter_proxy=np.array([1.0]), inv_partial_fit=np.array([1.0]))
    for c, _ in CONFIGS:
        A[f"gdshare_{c}"] = np.array(gdshare[c])
    man = R.base_manifest("P8.5", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1), head=HEAD,
                          meter=CFG.METER_CITE, bp_dims=bp_dims,
                          gd_share_confirmed_8020=bool(confirmed),
                          summary=dict(gdshare_committed=R.fmt(gdshare["committed"]),
                                       gdshare_always=R.fmt(gdshare["always-pay"]), bp_ratio=R.fmt(bp_ratio)))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.5 SUMMARY (median) ==", flush=True)
    print(f"  committed GD-share = {R.fmt(gdshare['committed'])}  ({'80/20 CONFIRMED' if confirmed else 'GD-share > 0.25'})", flush=True)
    print(f"  always-pay GD-share = {R.fmt(gdshare['always-pay'])}  (no-gate ceiling)", flush=True)
    print(f"  bp_ratio (OURS / BP+replay, matched retention, same substrate) = {R.fmt(bp_ratio)}", flush=True)
    print(f"  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
