"""
P8.4 — the honest hardware cost meter + the RanPAC-vs-SLDA verdict (design.md sec 3 P8.4). Build the behavioral,
ADC-centred, literature-calibrated per-op energy model (NeuroSim/ISAAC/PUMA level -- NOT SPICE) and price the WHOLE
LIVE loop for RanPAC vs SLDA on FRESHLY-MEASURED live AA (not P7's frozen tie). Ops: (a) SCFF fwd+update every step
[the 80%]; (b) namer inference every step; (c) namer partial_fit on FIRES; (d) sleep re-forward+solve. ADC dominant.
Verdict: commit SLDA over RanPAC iff E_meter(RanPAC)/E_meter(SLDA) >= 2 AND |AA(RanPAC)-AA(SLDA)| <= 0.02 (both live);
else keep RanPAC. + an ADC-bits sensitivity sweep (the meter's verdict is only as honest as e_ADC).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_4.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p8_4" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
AWAKE_GATE = "ddm"                                                    # the committed awake gate (P8.1)


def main():
    t0 = time.time()
    print(f"P8.4 — cost meter + RanPAC-vs-SLDA  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    heads = {"ranpac": CFG.RANPAC_KNOB, "slda": CFG.SLDA_KNOB}
    E = {h: {op: [] for op in ["mac", "adc", "write", "solve", "total", "gd", "scff"]} for h in heads}
    AA = {h: [] for h in heads}
    for s in SEEDS:
        stream, cache = caches[s]
        for h, knob in heads.items():
            r = P.run_economy(cache, lambda: P.make_stream_head(h, CFG.NCLASS, seed=s, **knob),
                              CFG, gate=AWAKE_GATE, trigger="error_ema", sleep_policy="checkpoint")
            AA[h].append(r["aa"])
            m = P.meter_from_trace(CFG, h, cache, r)
            for op in E[h]:
                E[h][op].append(m[op])
        print(f"  seed {s}: RanPAC AA={AA['ranpac'][-1]:.3f} E_gd={R.med(E['ranpac']['gd']):.2e} | "
              f"SLDA AA={AA['slda'][-1]:.3f} E_gd={R.med(E['slda']['gd']):.2e}", flush=True)

    e_gd_ranpac = R.med(E["ranpac"]["gd"]); e_gd_slda = R.med(E["slda"]["gd"])
    e_tot_ranpac = R.med(E["ranpac"]["total"]); e_tot_slda = R.med(E["slda"]["total"])
    ratio_gd = e_gd_ranpac / (e_gd_slda + 1e-30); ratio_tot = e_tot_ranpac / (e_tot_slda + 1e-30)
    d_aa = R.med(AA["ranpac"]) - R.med(AA["slda"])
    commit_slda = (ratio_gd >= 2.0) and (abs(d_aa) <= 0.02)
    verdict = "commit SLDA (cheaper namer, AA ties live)" if commit_slda else "keep RanPAC"

    # ADC-bits sensitivity (does the verdict survive the e_ADC assumption?)
    bits_sweep = {}
    s0 = SEEDS[0]; stream0, cache0 = caches[s0]
    for b in (4, 6, 8, 10):
        rr = {h: P.run_economy(cache0, lambda: P.make_stream_head(h, CFG.NCLASS, seed=s0, **heads[h]),
                               CFG, gate=AWAKE_GATE, sleep_policy="checkpoint") for h in heads}
        mr = {h: P.meter_from_trace(CFG, h, cache0, rr[h], adc_bits=b) for h in heads}
        bits_sweep[b] = float(mr["ranpac"]["gd"] / (mr["slda"]["gd"] + 1e-30))

    A = dict(seeds=np.array(SEEDS))
    for h in heads:
        for op in ["mac", "adc", "write", "solve", "total", "gd", "scff"]:
            A[f"energy_{h}_{op}"] = np.array(E[h][op])
        A[f"aa_live_{h}"] = np.array(AA[h])
    A["e_ratio_gd"] = np.array([ratio_gd]); A["e_ratio_total"] = np.array([ratio_tot])
    A["adc_bits_sweep"] = np.array([[b, bits_sweep[b]] for b in sorted(bits_sweep)])
    A["inv_meter_proxy"] = np.array([1.0]); A["inv_partial_fit"] = np.array([1.0])
    man = R.base_manifest("P8.4", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1),
                          meter=CFG.METER_CITE, meter_params=dict(E_ADC_STEP=CFG.E_ADC_STEP, ADC_BITS=CFG.ADC_BITS,
                          E_MAC=CFG.E_MAC, E_WRITE=CFG.E_WRITE, E_DIGITAL=CFG.E_DIGITAL),
                          verdict=verdict, ratio_gd=float(ratio_gd), ratio_total=float(ratio_tot), d_aa=float(d_aa),
                          adc_bits_sweep={int(b): float(v) for b, v in bits_sweep.items()},
                          summary=dict(aa_ranpac=R.fmt(AA["ranpac"]), aa_slda=R.fmt(AA["slda"]),
                                       E_gd_ranpac=e_gd_ranpac, E_gd_slda=e_gd_slda,
                                       E_total_ranpac=e_tot_ranpac, E_total_slda=e_tot_slda))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.4 SUMMARY (median; behavioral ADC-centred meter, pJ) ==", flush=True)
    for h in heads:
        print(f"  {h:7s} AA(live)={R.fmt(AA[h])}  E_total={R.med(E[h]['total']):.3e}  E_gd(namer)={R.med(E[h]['gd']):.3e} "
              f"[adc={R.med(E[h]['adc']):.2e} solve={R.med(E[h]['solve']):.2e}]", flush=True)
    print(f"  namer E-ratio RanPAC/SLDA = {ratio_gd:.1f}x  (total {ratio_tot:.2f}x)  |  dAA = {d_aa:+.3f}", flush=True)
    print(f"  ADC-bits sensitivity (namer ratio): {({b: round(v,1) for b,v in bits_sweep.items()})}", flush=True)
    print(f"  VERDICT: {verdict}  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
