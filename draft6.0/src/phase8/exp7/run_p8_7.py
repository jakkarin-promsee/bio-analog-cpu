"""
P8.7 — the substrate ablation: WHY ANALOG? (design.md sec 3 P8.7). Phases 8.4/8.5 metered OURS and BP+replay on the
SAME analog substrate table (the bp_ratio 0.501 = the ALGORITHM win on analog). This rung adds the missing axis the
"why build the analog chip" question needs: price the EXACT committed economy (SLDA + DDM + cbrs + grid-8/full/lam1.0)
AND the fair BP+replay baseline on BOTH substrates -> the full 2x2 {OURS, GD+replay} x {analog, digital}. The headline
three the comparison rests on: OURS-analog vs OURS-digital vs GD-digital.

The digital substrate = the conventional von-Neumann / digital-accelerator (GPU-class) baseline: the SAME per-op
counts, but a real digital 8-bit MAC (E_MAC_DIG, operands fetched -- the memory wall), NO ADC (the analog tax
vanishes), an SRAM weight write, the same digital solve. Matched 8-bit precision -> the axis under test is the
SUBSTRATE, not the number format. The three decompositions:
  * SUBSTRATE win  = E(OURS-digital) / E(OURS-analog)  -- same algorithm, CIM vs von-Neumann ("why analog")
  * ALGORITHM win  = E(GD-digital)   / E(OURS-digital) -- same digital substrate, our 80/20 vs real backprop+replay
  * TOTAL win      = E(GD-digital)   / E(OURS-analog)  -- what adopting the chip actually buys (algorithm x substrate)
+ an E_MAC_DIG memory-wall sensitivity sweep (arithmetic-only -> with data movement): OURS-analog is a flat reference,
the digital costs rise -> the analog advantage the central value reports is a CONSERVATIVE FLOOR.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_7.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import json

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p8lib as P                                                      # noqa: E402
import p8cfg as CFG                                                    # noqa: E402
import p8run as R                                                      # noqa: E402
import plot_p8                                                         # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p8_7" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
HEAD = "slda"                                                          # the P8.4-committed deployed head
AWAKE = "ddm"                                                          # the P8.1-committed awake gate


def committed_cadence():
    """The P8.3-committed sleep cadence (== P8.6's loader): grid-8 / full history / lam_ema 1.0."""
    m3 = os.path.join(_HERE, "..", "exp3", "figs_p8_3", "manifest.json")
    pol, cad, lf, le = "grid", 8, 1.0, 1.0
    try:
        c = json.load(open(m3))["committed_cadence"]
        fmap = {"oracle-boundary": ("checkpoint", 1), "grid-2": ("grid", 2), "grid-4": ("grid", 4), "grid-8": ("grid", 8)}
        hmap = {"full/l1.0": (1.0, 1.0), "half/l1.0": (0.5, 1.0), "qtr/l1.0": (0.25, 1.0), "full/l0.9": (1.0, 0.9)}
        pol, cad = fmap.get(c["freq"], (pol, cad)); lf, le = hmap.get(c["hist"], (lf, le))
    except Exception:
        pass
    return dict(sleep_policy=pol, cadence_every=cad, lut_frac=lf, lam_ema=le)


def _guards():
    """Guards FIRST (netlist rule). The two touched by the substrate edit: meter_proxy (the ANALOG path still reduces
    to the P7 proxy -> my digital branch left the default untouched) + partial_fit_equiv. Any fail -> STOP."""
    print("== guards (meter_proxy = analog path unchanged; partial_fit_equiv) ==", flush=True)
    ok1, _ = P.meter_proxy_guard(CFG)
    ok2, _ = P.partial_fit_equiv_guard(verbose=True)
    if not (ok1 and ok2):
        print("!! GUARD FAILED -> STOP", flush=True); sys.exit(1)
    return ok1 and ok2


def main():
    t0 = time.time()
    print(f"P8.7 — substrate ablation (WHY ANALOG)  (QUICK={QUICK}, seeds={SEEDS}, head={HEAD}, awake={AWAKE}+cbrs)", flush=True)
    _guards()
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    knob = CFG.RANPAC_KNOB if HEAD == "ranpac" else CFG.SLDA_KNOB
    cad = committed_cadence()
    print(f"  committed economy: head={HEAD} awake={AWAKE}+cbrs sleep={cad}", flush=True)

    # the fair BP+replay baseline dims: iso-weight-budget MLP (same as P8.5)
    nh = 3
    bw = max(8, int(np.sqrt(P.ours_budget(CFG.DIM, CFG.WIDTH, CFG.DEPTH, CFG.NCLASS) / nh)))
    bp_dims = [CFG.DIM] + [bw] * nh + [CFG.NCLASS]

    E = {"ours_analog": [], "ours_digital": [], "gd_analog": [], "gd_digital": []}
    GDSHARE = {"analog": [], "digital": []}                            # does the 80/20 hold on both substrates?
    for s in SEEDS:
        stream, cache = caches[s]
        r = P.run_economy(cache, lambda: P.make_stream_head(HEAD, CFG.NCLASS, seed=s, **knob),
                          CFG, gate=AWAKE, trigger="error_ema", cbrs=True, **cad)     # the committed economy, run LIVE
        m_oa = P.meter_from_trace(CFG, HEAD, cache, r, substrate="analog")
        m_od = P.meter_from_trace(CFG, HEAD, cache, r, substrate="digital")
        assert m_od["adc"] == 0.0, "digital substrate must have NO ADC"                # sanity: the analog tax is gone
        n_steps = len(cache["steps"])
        bp_a = P.bp_replay_energy(CFG, Fdim=CFG.DIM, C=CFG.NCLASS, n_steps=n_steps,
                                  batch=CFG.BATCH, replay_batch=CFG.BATCH, bp_dims=bp_dims, substrate="analog")
        bp_d = P.bp_replay_energy(CFG, Fdim=CFG.DIM, C=CFG.NCLASS, n_steps=n_steps,
                                  batch=CFG.BATCH, replay_batch=CFG.BATCH, bp_dims=bp_dims, substrate="digital")
        E["ours_analog"].append(m_oa["total"]); E["ours_digital"].append(m_od["total"])
        E["gd_analog"].append(bp_a["total"]); E["gd_digital"].append(bp_d["total"])
        GDSHARE["analog"].append(m_oa["gdshare"]); GDSHARE["digital"].append(m_od["gdshare"])
        print(f"  seed {s}: OURS analog={m_oa['total']:.3e} digital={m_od['total']:.3e} | "
              f"GD analog={bp_a['total']:.3e} digital={bp_d['total']:.3e}", flush=True)

    oa, od = R.med(E["ours_analog"]), R.med(E["ours_digital"])
    ga, gd = R.med(E["gd_analog"]), R.med(E["gd_digital"])
    # per-seed ratios (median [IQR]) -- the honest paired reads
    sub_win = [b / a for a, b in zip(E["ours_analog"], E["ours_digital"])]          # OURS digital/analog  (>1)
    alg_win = [g / o for o, g in zip(E["ours_digital"], E["gd_digital"])]           # GD/OURS on digital    (>1)
    tot_win = [g / a for a, g in zip(E["ours_analog"], E["gd_digital"])]            # GD-digital / OURS-analog
    bp_ratio_analog = [a / g for a, g in zip(E["ours_analog"], E["gd_analog"])]     # cross-check vs P8.5 (0.501)

    # the E_MAC_DIG memory-wall sensitivity sweep (median over seeds), OURS-analog flat
    sweep = []
    for emd in CFG.E_MAC_DIG_SWEEP:
        od_e, gd_e = [], []
        for s in SEEDS:
            stream, cache = caches[s]
            r = P.run_economy(cache, lambda: P.make_stream_head(HEAD, CFG.NCLASS, seed=s, **knob),
                              CFG, gate=AWAKE, trigger="error_ema", cbrs=True, **cad)
            od_e.append(P.meter_from_trace(CFG, HEAD, cache, r, substrate="digital", e_mac_dig=emd)["total"])
            gd_e.append(P.bp_replay_energy(CFG, Fdim=CFG.DIM, C=CFG.NCLASS, n_steps=len(cache["steps"]),
                        batch=CFG.BATCH, replay_batch=CFG.BATCH, bp_dims=bp_dims,
                        substrate="digital", e_mac_dig=emd)["total"])
        sweep.append([emd, R.med(od_e), R.med(gd_e)])
    sweep = np.array(sweep)

    A = dict(seeds=np.array(SEEDS),
             E_ours_analog=np.array(E["ours_analog"]), E_ours_digital=np.array(E["ours_digital"]),
             E_gd_analog=np.array(E["gd_analog"]), E_gd_digital=np.array(E["gd_digital"]),
             gdshare_analog=np.array(GDSHARE["analog"]), gdshare_digital=np.array(GDSHARE["digital"]),
             substrate_win=np.array(sub_win), algorithm_win_digital=np.array(alg_win),
             total_win=np.array(tot_win), bp_ratio_analog=np.array(bp_ratio_analog),
             emac_sweep=sweep, inv_meter_proxy=np.array([1.0]), inv_partial_fit=np.array([1.0]))
    man = R.base_manifest("P8.7", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1), head=HEAD,
                          awake_gate=AWAKE, cbrs=True, sleep_cadence=cad, bp_dims=bp_dims,
                          meter=CFG.METER_CITE, meter_dig=CFG.METER_CITE_DIG,
                          meter_params=dict(E_MAC=CFG.E_MAC, E_ADC_STEP=CFG.E_ADC_STEP, ADC_BITS=CFG.ADC_BITS,
                                            E_WRITE=CFG.E_WRITE, E_DIGITAL=CFG.E_DIGITAL,
                                            E_MAC_DIG=CFG.E_MAC_DIG, E_WRITE_DIG=CFG.E_WRITE_DIG),
                          summary=dict(E_ours_analog=oa, E_ours_digital=od, E_gd_analog=ga, E_gd_digital=gd,
                                       substrate_win=R.fmt(sub_win), algorithm_win_digital=R.fmt(alg_win),
                                       total_win=R.fmt(tot_win), bp_ratio_analog=R.fmt(bp_ratio_analog),
                                       gdshare_analog=R.fmt(GDSHARE["analog"]), gdshare_digital=R.fmt(GDSHARE["digital"])))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.7 SUMMARY (median; behavioral, pJ) ==", flush=True)
    print(f"  OURS   analog={oa:.3e}   digital={od:.3e}", flush=True)
    print(f"  GD+rep analog={ga:.3e}   digital={gd:.3e}", flush=True)
    print(f"  SUBSTRATE win  (OURS digital/analog)   = {R.fmt(sub_win)}x", flush=True)
    print(f"  ALGORITHM win  (GD/OURS on digital)    = {R.fmt(alg_win)}x", flush=True)
    print(f"  TOTAL win      (GD-digital/OURS-analog)= {R.fmt(tot_win)}x", flush=True)
    print(f"  x-check bp_ratio analog (vs P8.5 0.501)= {R.fmt(bp_ratio_analog)}", flush=True)
    print(f"  80/20 GD-share: analog={R.fmt(GDSHARE['analog'])}  digital={R.fmt(GDSHARE['digital'])}", flush=True)
    print(f"  E_MAC_DIG sweep (memory wall): {[(float(e), f'{od_:.2e}', f'{gd_:.2e}') for e, od_, gd_ in sweep]}", flush=True)
    print(f"  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
