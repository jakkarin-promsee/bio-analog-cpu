"""
P10.1 — the EXISTENTIAL FIGHT (design §3 P10.1). Swept variable = learner ∈ {OURS(grid-4), ER-strong, ER-budget,
A-GEM, DER++, GDumb, naive-BP} (+ the joint-BP CEILING as a non-raced dashed reference — K1), continual home
(the lifelong synthetic stream = the class-IL leg, K13), 5 seeds. Score accuracy × same-substrate energy (the Pareto
point) + BWT + AAA. The LOAD-BEARING rung: OURS's continual accuracy has only ever been raced against naive online-BP
(a strawman); here it races a BUDGETED, TUNED experience replay (Prabhu CVPR'23 — ER is strong under a matched
budget). ER-strong is byte-matched to OURS's LUT + tuned on the DISJOINT tuning stream (seed 7; P10.0). Verdict
shape pinned BLIND (design §2.3):
  win           iff acc(OURS) >= acc(ER-strong) - delta AND E(OURS-digital) < E(ER-digital) strictly
  honest-Pareto iff acc(OURS) <  acc(ER-strong) - delta BUT E(OURS-digital) << E(ER-digital)  (accuracy half "not supported")
  dominated     iff acc(OURS) <  acc(ER-strong) - delta AND E(OURS-digital) >= E(ER-digital)  (the founding bet fails)
The same-substrate cut (E(OURS-digital) vs E(ER-digital)) is the contestable ALGORITHM win; OURS-analog/GD-digital is
the floor-flagged TOTAL headline overlay (R1).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_1.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
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
OUT = os.path.join(_HERE, "figs_p10_1" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
ROSTER = ["ours_g4", "er_strong", "er_budget", "agem", "derpp", "gdumb", "naive"]


def load_er_cfg():
    m = json.load(open(os.path.join(_HERE, "..", "exp0", "figs_p10_0", "manifest.json")))
    return m["er_strong_config"]


def bp_field_cfg(er):
    field = [CFG.DIM, 64, 64, CFG.NCLASS]
    return {
        "er_strong": dict(policy="er", bp_dims=er["bp_dims"], lr=er["lr"], l2=er["l2"], replay=er["replay"], cap=er["buffer_cap"]),
        "er_budget": dict(policy="er", bp_dims=er["bp_dims"], lr=er["lr"], l2=er["l2"], replay=CFG.ER_BUDGET_REPLAY, cap=CFG.PROBE_N),
        "agem": dict(policy="agem", bp_dims=field, lr=er["lr"], l2=er["l2"], replay=er["replay"], cap=CFG.PROBE_N),
        "derpp": dict(policy="derpp", bp_dims=field, lr=er["lr"], l2=er["l2"], replay=er["replay"], cap=CFG.PROBE_N),
        "gdumb": dict(policy="gdumb", bp_dims=field, lr=er["lr"], l2=er["l2"], replay=0, cap=CFG.PROBE_N),
        "naive": dict(policy="naive", bp_dims=field, lr=er["lr"], l2=er["l2"], replay=0, cap=0),
    }


def main():
    t0 = time.time()
    print(f"P10.1 — the existential fight  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)
    er = load_er_cfg(); fcfg = bp_field_cfg(er)
    print(f"  ER-strong (from P10.0): dims={er['bp_dims']} lr={er['lr']} replay={er['replay']} cap={er['buffer_cap']}", flush=True)

    acc = {k: [] for k in ROSTER}; en_an = {k: [] for k in ROSTER}; en_di = {k: [] for k in ROSTER}
    bwt = {k: [] for k in ROSTER}; aaa = {k: [] for k in ROSTER}; wbwt = {k: [] for k in ROSTER}
    joint = []
    for s in SEEDS:
        stream, cache = R.build_life_cache(s, quick=QUICK, store_reps=False, verbose=False)
        hf = R.committed_hf(s)
        # OURS grid-4 (the frozen object)
        ours = P.ours_bundle(cache, hf, CFG, 4)
        e_an = P.ours_stream_energy(CFG, cache, ours, substrate="analog")
        e_di = P.ours_stream_energy(CFG, cache, ours, substrate="digital")
        acc["ours_g4"].append(ours["aa"]); en_an["ours_g4"].append(e_an["total"]); en_di["ours_g4"].append(e_di["total"])
        bwt["ours_g4"].append(ours["worst_bwt"]); aaa["ours_g4"].append(ours["aaa"]); wbwt["ours_g4"].append(ours["worst_bwt"])
        n_steps = len(cache["steps"])
        # the BP+replay field
        line = [f"OURS g4 aa={ours['aa']:.3f}"]
        for k in ROSTER[1:]:
            c = fcfg[k]
            m = P.run_bp_stream(stream, c["policy"], c["bp_dims"], CFG, s, lr=c["lr"], l2=c["l2"],
                                replay=c["replay"], buffer_cap=c["cap"])
            ea = P.bp_stream_energy(CFG, c["bp_dims"], c["policy"], n_steps=n_steps, replay=c["replay"], substrate="analog")
            ed = P.bp_stream_energy(CFG, c["bp_dims"], c["policy"], n_steps=n_steps, replay=c["replay"], substrate="digital")
            acc[k].append(m["aa"]); en_an[k].append(ea["total"]); en_di[k].append(ed["total"])
            bwt[k].append(m["worst_bwt"]); aaa[k].append(m["aaa"]); wbwt[k].append(m["worst_bwt"])   # worst-pre-sleep for ALL (R6)
            line.append(f"{k}={m['aa']:.3f}")
        joint.append(P.joint_bp_ceiling(stream, CFG, CFG.DIM, CFG.NCLASS, s))
        print(f"  seed {s}: " + " ".join(line) + f" joint={joint[-1]:.3f}", flush=True)
        del cache, stream

    # --- the verdict (pinned BLIND; the two halves banked SEPARATELY — §7/R4) ---
    dacc = CFG.DELTA_ACC
    accO = R.med(acc["ours_g4"]); accE = R.med(acc["er_strong"])
    eanO = R.med(en_an["ours_g4"]); ediO = R.med(en_di["ours_g4"]); ediE = R.med(en_di["er_strong"])
    real, disj, sign = R.real_diff(acc["er_strong"], acc["ours_g4"])
    acc_below = (accO < accE - dacc) and real                          # ER-strong REALLY beats OURS by > delta
    acc_tie = not acc_below                                            # within-noise or OURS-higher -> accuracy competitive
    algo_win = ediO < ediE                                             # the same-substrate (digital) ALGORITHM cut
    total_win = eanO < ediE                                            # OURS-analog (the chip) vs ER-on-digital (conventional GD)
    tot_ratio = ediE / (eanO + 1e-9)                                   # chip-vs-conventional-GD total ratio (substrate-realized)
    if acc_tie and algo_win:
        verdict = f"WIN (accuracy tie within delta AND same-substrate E(OURS-dig) < E(ER-dig) at {ediO/ediE:.2f}x)"
    elif acc_tie and not algo_win:
        verdict = (f"ACCURACY-COMPETITIVE / algorithm-energy NOT a win: OURS ties ER-strong on acc (gap {accE-accO:+.3f}) "
                   f"but is {ediO/ediE:.2f}x MORE expensive same-substrate (the deep unsupervised bulk vs a small tuned "
                   f"net). The energy win is SUBSTRATE-realized: OURS-analog is {tot_ratio:.2f}x cheaper than ER-on-digital.")
    elif acc_below and total_win:
        verdict = (f"HONEST-PARETO (substrate): acc below ER-strong by {accE-accO:.3f} (>delta) but OURS-analog "
                   f"{tot_ratio:.2f}x cheaper than ER-digital — accuracy half NOT supported")
    else:
        verdict = "DOMINATED (acc below AND not cheaper even analog-vs-digital — the founding bet fails)"

    print(f"\n  == FIGHT (delta_acc={dacc}) ==", flush=True)
    print(f"  {'learner':10s} {'acc':>18} {'E(analog)':>11} {'E(digital)':>11} {'BWT':>8} {'AAA':>8}", flush=True)
    for k in ROSTER:
        print(f"  {k:10s} {R.fmt(acc[k]):>18} {R.med(en_an[k]):>11.3e} {R.med(en_di[k]):>11.3e} "
              f"{R.med(bwt[k]):>+8.3f} {R.med(aaa[k]):>8.3f}", flush=True)
    print(f"  joint-BP ceiling AA = {R.fmt(joint)}  (accuracy-axis reference only)", flush=True)
    print(f"  same-substrate (digital) algorithm cut: E(OURS)={ediO:.3e} vs E(ER-strong)={ediE:.3e} -> {ediO/ediE:.3f}x", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    # arrays (schema §A)
    A = dict(seeds=np.array(SEEDS), learners=np.array(ROSTER), acc_joint=np.array(joint), **R.inv_arrays(g))
    for k in ROSTER:
        A[f"acc_{k}"] = np.array(acc[k]); A[f"bwt_{k}"] = np.array(bwt[k]); A[f"aaa_{k}"] = np.array(aaa[k])
        A[f"energy_{k}_analog"] = np.array(en_an[k]); A[f"energy_{k}_digital"] = np.array(en_di[k])
    # pareto points (OURS-analog vs field-analog — the total scatter; hero ringed)
    pts = np.array([[R.med(acc[k]), R.med(en_an[k]), 0.0] for k in ROSTER])
    fr = P.pareto_frontier([(k, R.med(acc[k]), R.med(en_an[k])) for k in ROSTER])
    for i, k in enumerate(ROSTER):
        pts[i, 2] = 1.0 if fr[k]["is_frontier"] else 0.0
    A["pareto_pts"] = pts; A["pareto_labels"] = np.array(ROSTER)

    man = R.base_manifest("P10.1", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          er_strong_config=er, roster=ROSTER, verdict=verdict,
                          summary={k: dict(acc=R.fmt(acc[k]), e_analog=R.med(en_an[k]), e_digital=R.med(en_di[k]),
                                           bwt=R.fmt(bwt[k]), aaa=R.fmt(aaa[k])) for k in ROSTER},
                          joint_ceiling=R.fmt(joint),
                          algorithm_cut=dict(ours_digital=ediO, er_digital=ediE, ratio=ediO / ediE),
                          total_floor_ratio=tot_ratio)
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.1 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
