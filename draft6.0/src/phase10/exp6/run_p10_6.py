"""
P10.6 — the PARETO VERDICT + the Stage-2 close-out (design §3 P10.6). NOT a scalar: assemble the (accuracy, energy)
frontier across the OURS-family + the BP+replay field (from P10.1/P10.2/P10.3), state WHERE OURS wins / ties / loses
(each with its number + mechanism), and bank the founding bet's ECONOMICS and ACCURACY halves SEPARATELY (§7 / R4).
Emits the PARETO figure + the win/tie/loss map + the arrays the close-out doc and the professor brief cite.

This rung READS the prior rungs' manifests/arrays (it runs nothing new) and integrates. Run AFTER P10.1–P10.4.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_6.py
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

OUT = os.path.join(_HERE, "figs_p10_6")


def _load(rung_dir):
    base = os.path.join(_HERE, "..", rung_dir)
    A = np.load(os.path.join(base, "arrays.npz"), allow_pickle=True)
    m = json.load(open(os.path.join(base, "manifest.json")))
    return A, m


def main():
    t0 = time.time()
    print("P10.6 — the Pareto verdict + Stage-2 close-out (integration; runs nothing new)", flush=True)
    A1, m1 = _load("exp1/figs_p10_1")
    roster = [x.decode() if isinstance(x, bytes) else str(x) for x in A1["learners"]]

    # the Pareto point per learner (OURS-analog vs field-analog — the total scatter; the hero ringed)
    def med(k):
        return float(np.median(A1[k]))
    pts = [(lr, med(f"acc_{lr}"), med(f"energy_{lr}_analog")) for lr in roster]
    fr = P.pareto_frontier(pts)
    pareto_pts = np.array([[fr[lr]["acc"], fr[lr]["energy"], 1.0 if fr[lr]["is_frontier"] else 0.0] for lr in roster])

    # the same-substrate (digital) algorithm cut + the total headline
    accO = med("acc_ours_g4"); accE = med("acc_er_strong")
    ediO = med("energy_ours_g4_digital"); ediE = med("energy_er_strong_digital")
    eanO = med("energy_ours_g4_analog")
    total_ratio = ediE / (eanO + 1e-9)                                 # OURS-analog (chip) vs ER-strong-digital (modern GD)
    algo_ratio = ediO / (ediE + 1e-9)

    # the two halves, banked SEPARATELY (R4/§7)
    econ_algo = "validated" if algo_ratio < 1.0 else ("substrate-only" )
    acc_gap = accE - accO
    acc_half = ("validated" if acc_gap <= CFG.DELTA_ACC else
                ("honest-Pareto (not supported at competitive acc)" if eanO < med("energy_er_strong_analog") else "not supported"))

    # the verdict map (axis · OURS · best-field · win/tie/loss · number)
    vmap = []
    vmap.append(("accuracy (vs ER-strong)", f"{accO:.3f}", f"{accE:.3f}",
                 "tie" if acc_gap <= CFG.DELTA_ACC else "loss", f"gap {acc_gap:+.3f}"))
    vmap.append(("energy — algorithm (same digital substrate)", f"{ediO:.3e}", f"{ediE:.3e}",
                 "win" if algo_ratio < 1.0 else "loss", f"{algo_ratio:.2f}x"))
    vmap.append(("energy — total (OURS-analog vs ER-strong-digital)", f"{eanO:.3e}", f"{ediE:.3e}",
                 "win" if total_ratio > 1.0 else "loss", f"{total_ratio:.1f}x (substrate-realized floor)"))

    print("\n  == PARETO VERDICT MAP ==", flush=True)
    print(f"  {'axis':45s} {'OURS':>12} {'best-field':>12} {'w/t/l':>6} {'number':>18}", flush=True)
    for ax, o, f2, wtl, num in vmap:
        print(f"  {ax:45s} {o:>12} {f2:>12} {wtl:>6} {num:>18}", flush=True)
    print(f"\n  founding bet — ECONOMICS half: {econ_algo} (algorithm {algo_ratio:.2f}x same-substrate; "
          f"total {total_ratio:.1f}x analog-floor)", flush=True)
    print(f"  founding bet — ACCURACY half: {acc_half} (gap {acc_gap:+.3f} vs delta {CFG.DELTA_ACC})", flush=True)
    print(f"  Pareto frontier members: {[lr for lr in roster if fr[lr]['is_frontier']]}", flush=True)

    Aout = dict(pareto_pts=pareto_pts, pareto_labels=np.array(roster),
                acc_ours=np.array([accO]), acc_er=np.array([accE]),
                algo_ratio=np.array([algo_ratio]), total_ratio=np.array([total_ratio]),
                inv_pareto=np.array([1.0]))
    man = R.base_manifest("P10.6", CFG.SEEDS, False, wall_s=round(time.time() - t0, 1),
                          verdict_map=vmap, economics_half=econ_algo, accuracy_half=acc_half,
                          algorithm_ratio=algo_ratio, total_floor_ratio=total_ratio,
                          pareto_frontier=[lr for lr in roster if fr[lr]["is_frontier"]],
                          efficiency={lr: fr[lr]["efficiency"] for lr in roster},
                          p10_1=m1.get("verdict"))
    R.save_run(OUT, Aout, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.6 verdict assembled (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
