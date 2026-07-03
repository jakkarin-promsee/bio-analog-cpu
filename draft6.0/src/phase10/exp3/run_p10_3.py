"""
P10.3 — the MULTI-DOMAIN GAUNTLET (THE money figure) (design §3 P10.3). The frozen object at ALL FIVE grids (the
money figure draws grid-4 + the Tier-1 rep + grid-8 + grid-16; the per-domain strip draws all five — K7) vs
ER-strong (+ er_budget/naive field), across ≈5 native domain-IL domains (digit transforms, shared 40-D input,
shared 10-class head — K5/B2/R3), 5 seeds, + ONE reversed-order control (grid-4 + ER-strong, 5 seeds; K9). Score
new/1-back/all-prev accuracy + AAA + cumulative same-substrate energy + throughput/steps-behind + SCFF:Namer ratio
vs difficulty; overlay sleep positions; re-meter the substrate 2x2.

Read (pinned BLIND): showcase-win iff OURS worst-point all-prev retention within delta of ER-strong AND E(OURS-
digital) strictly lower at every domain boundary; scaling-limit iff retention decays with #domains; ratio-not-scale-
free iff GD-share grows with domain hardness. The retention read is worst-point all-prev AA (the P9 honest
convention, ER at the same convention — R6/K12).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_3.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p10_3" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
GRIDS = [4, 5, 6, 8, 16]


def load_er_cfg():
    m = json.load(open(os.path.join(_HERE, "..", "exp0", "figs_p10_0", "manifest.json")))
    return m["er_strong_config"]


def load_tier1_rep():
    try:
        m = json.load(open(os.path.join(_HERE, "..", "exp2", "figs_p10_2", "manifest.json")))
        r = m.get("tier1_rep", "")
        return int(r.split("-")[1]) if r.startswith("grid-") else 5
    except Exception:
        return 5


def domain_curves(res, D):
    """new/1-back/all-prev per domain from the acc-matrix + first_acc (learner-independent — R6/K12)."""
    mat = res["matrix"]; fa = res.get("first_acc", {})
    allprev = np.array([np.mean(mat[d][:d + 1]) for d in range(D)])
    plast = np.array([fa.get(d, mat[d][d]) for d in range(D)])
    oneback = np.array([mat[d][d - 1] if d >= 1 else np.nan for d in range(D)])
    return allprev, plast, oneback


def main():
    t0 = time.time()
    print(f"P10.3 — the gauntlet money figure  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)
    er = load_er_cfg(); rep = load_tier1_rep()
    domains = CFG.GAUNTLET_DOMAINS; D = len(domains)
    print(f"  domains={domains}  Tier-1 rep=grid-{rep}  ER-strong dims={er['bp_dims']} replay={er['replay']}", flush=True)

    cfgs = ["g4", f"g{rep}", "g8", "g16", "er_strong"]                  # the money-figure headline lines
    allprev = {c: [] for c in cfgs}; plast = {c: [] for c in cfgs}; oneb = {c: [] for c in cfgs}
    aaa = {c: [] for c in cfgs}; wbwt = {c: [] for c in cfgs}
    en_an = {c: [] for c in cfgs}; en_di = {c: [] for c in cfgs}
    all_grid_allprev = {gr: [] for gr in GRIDS}                         # per-domain strip (all five grids)
    gdshare_dom = {gr: [] for gr in GRIDS}                              # SCFF:Namer ratio vs difficulty
    sleep_pos = []; order_delta = []; flops = {}
    for s in SEEDS:
        gstream = P.make_gauntlet_stream(CFG, s, domains=domains)
        cache = P.build_cache_p9(P.make_committed_cell, gstream, s, CFG, store_reps=False, quick=QUICK)
        hf = R.committed_hf(s)
        n_steps = len(cache["steps"]); spd = max(1, n_steps // D)
        # OURS at all five grids
        for gr in GRIDS:
            ra = P.ours_bundle(cache, hf, CFG, gr)
            ap, pl, ob = domain_curves(ra, D)
            all_grid_allprev[gr].append(ap)
            fires = ra["fires"]
            gdshare_dom[gr].append([float(fires[d * spd:(d + 1) * spd].mean()) for d in range(D)])
            if gr == 4:
                sp = np.where(ra["sleeps"])[0]; sleep_pos.append((sp / spd).tolist())
            key = {4: "g4", rep: f"g{rep}", 8: "g8", 16: "g16"}.get(gr)
            if key and key in cfgs:
                met_a = P.ours_stream_energy(CFG, cache, ra, substrate="analog")
                met_d = P.ours_stream_energy(CFG, cache, ra, substrate="digital")
                allprev[key].append(ap); plast[key].append(pl); oneb[key].append(ob)
                aaa[key].append(ra["aaa"]); wbwt[key].append(ra["worst_bwt"])
                en_an[key].append(met_a["total"]); en_di[key].append(met_d["total"])
        # ER-strong on the gauntlet
        m = P.run_bp_stream(gstream, "er", er["bp_dims"], CFG, s, lr=er["lr"], l2=er["l2"],
                            replay=er["replay"], buffer_cap=er["buffer_cap"])
        ap, pl, ob = domain_curves(m, D)
        allprev["er_strong"].append(ap); plast["er_strong"].append(pl); oneb["er_strong"].append(ob)
        aaa["er_strong"].append(m["aaa"]); wbwt["er_strong"].append(m["worst_bwt"])
        en_an["er_strong"].append(P.bp_stream_energy(CFG, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="analog")["total"])
        en_di["er_strong"].append(P.bp_stream_energy(CFG, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="digital")["total"])
        # reversed-order control (grid-4 + ER-strong)
        grev = P.make_gauntlet_stream(CFG, s, domains=domains, order="reversed")
        crev = P.build_cache_p9(P.make_committed_cell, grev, s, CFG, store_reps=False, quick=QUICK)
        o_fwd = P.ours_bundle(cache, hf, CFG, 4)["aa"]; o_rev = P.ours_bundle(crev, hf, CFG, 4)["aa"]
        order_delta.append(o_rev - o_fwd)
        # throughput FLOPs (once)
        if not flops:
            fb_o = P.fair_budget_meter(CFG, learner="ours", ours_res=P.ours_bundle(cache, hf, CFG, 4), ours_cache=cache)
            fb_e = P.fair_budget_meter(CFG, learner="er", bp_dims=er["bp_dims"], replay=er["replay"], buffer_cap=er["buffer_cap"], in_dim=CFG.DIM)
            flops = {"ours_g4": fb_o["flops_per_sample"], "er_strong": fb_e["flops_per_sample"]}
        print(f"  seed {s}: OURS g4 allprev[-1]={allprev['g4'][-1][-1]:.3f} ER allprev[-1]={allprev['er_strong'][-1][-1]:.3f} "
              f"order-delta={order_delta[-1]:+.3f}", flush=True)
        del cache, crev

    # --- verdict (the honest continual read = worst-point all-prev; the two halves banked separately) ---
    dacc = CFG.DELTA_ACC
    worst_o = R.med([min(a) for a in allprev["g4"]]); worst_e = R.med([min(a) for a in allprev["er_strong"]])
    final_o = R.med(np.array(allprev["g4"])[:, -1]); final_e = R.med(np.array(allprev["er_strong"])[:, -1])
    sub_bars = np.array([en_an["g4"], en_di["g4"], en_an["er_strong"], en_di["er_strong"]])
    total_win = R.med(en_di["er_strong"]) / (R.med(en_an["g4"]) + 1e-9)   # chip (OURS-analog) vs conventional-GD-digital
    algo_ratio = R.med(en_di["g4"]) / (R.med(en_di["er_strong"]) + 1e-9)  # same-substrate (digital) algorithm cut
    retention_ok = worst_o >= worst_e - dacc                              # OURS worst-point all-prev >= ER (within delta / better)
    algo_win = R.med(en_di["g4"]) < R.med(en_di["er_strong"])
    thr = P.throughput_meter(flops) if flops else {}
    if retention_ok and algo_win:
        verdict = f"SHOWCASE-WIN (OURS worst-point all-prev {worst_o:.3f} >= ER {worst_e:.3f} AND cheaper same-substrate)"
    elif retention_ok:
        verdict = (f"RETENTION-COMPETITIVE/BETTER (OURS worst-point all-prev {worst_o:.3f} vs ER {worst_e:.3f}; AAA "
                   f"{R.med(aaa['g4']):.3f} vs {R.med(aaa['er_strong']):.3f}); algorithm-energy NOT a win ({algo_ratio:.2f}x "
                   f"same-substrate); energy win SUBSTRATE-realized ({total_win:.1f}x OURS-analog vs ER-digital). "
                   f"Final all-prev {final_o:.3f} vs {final_e:.3f}.")
    else:
        verdict = f"SCALING LIMIT (OURS worst-point all-prev {worst_o:.3f} < ER {worst_e:.3f} by > delta)"

    print(f"\n  == GAUNTLET (delta_acc={dacc}) ==", flush=True)
    print(f"  {'cfg':>10} {'all-prev[-1]':>14} {'worst all-prev':>16} {'AAA':>8} {'worst-BWT':>10} {'E(dig)':>11}", flush=True)
    for c in cfgs:
        ap = np.array(allprev[c]); worst = R.med([min(a) for a in allprev[c]])
        print(f"  {c:>10} {R.fmt(ap[:, -1]):>14} {worst:>16.3f} {R.med(aaa[c]):>8.3f} {R.fmt(wbwt[c]):>10} "
              f"{R.med(en_di[c]):>11.3e}", flush=True)
    print(f"  same-substrate (digital): OURS g4 {R.med(en_di['g4']):.3e} vs ER-strong {R.med(en_di['er_strong']):.3e} "
          f"-> {R.med(en_di['g4'])/R.med(en_di['er_strong']):.3f}x", flush=True)
    print(f"  substrate total (OURS-analog vs ER-digital): {total_win:.1f}x", flush=True)
    print(f"  reversed-order AA delta (grid-4): {R.fmt(order_delta)}", flush=True)
    if thr:
        print(f"  throughput/steps-behind: ER-strong rel-complexity {thr['er_strong']['rel_complexity']:.2f}x, "
              f"steps-behind {thr['er_strong']['steps_behind_frac']:.2f} (OURS 0 by construction)", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    # arrays
    A = dict(seeds=np.array(SEEDS), domains=np.array(domains), gauntlet_cfgs=np.array(cfgs),
             sleep_pos=np.array(sorted(set(round(x, 2) for sp in sleep_pos for x in sp))),
             orderdelta_g4=np.array(order_delta),
             substrate_bars=sub_bars, substrate_total_win=np.array([total_win]),
             substrate_labels=np.array(["OURS-analog", "OURS-digital", "ER-analog", "ER-digital"]),
             **R.inv_arrays(g))
    for c in cfgs:
        A[f"allprev_{c}"] = np.array(allprev[c]); A[f"plasticity_{c}"] = np.array(plast[c])
        A[f"oneback_{c}"] = np.array(oneb[c]); A[f"aaa_{c}"] = np.array(aaa[c])
        # cumulative energy = proportional-to-steps shape (per-op sleeps cluster; the SHAPE is the money-figure read; noted)
        A[f"cumenergy_{c}_analog"] = (R.med(en_an[c]) / D) * np.arange(1, D + 1)
        A[f"cumenergy_{c}_digital"] = (R.med(en_di[c]) / D) * np.arange(1, D + 1)
    for gr in GRIDS:
        A[f"gridstrip_g{gr}"] = np.array(all_grid_allprev[gr])
        A[f"gdshare_g{gr}"] = np.array(gdshare_dom[gr])
    man = R.base_manifest("P10.3", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          domains=domains, tier1_rep=f"grid-{rep}", cfgs=cfgs, verdict=verdict,
                          worst_allprev=dict(ours_g4=worst_o, er_strong=worst_e),
                          substrate_total_win=total_win, order_delta=R.fmt(order_delta),
                          throughput=thr,
                          notes="retention curve = post-checkpoint AA(d) per domain (learner-independent); worst-point "
                                "is the P9 honest read. cumulative energy = proportional-to-steps shape (sleeps cluster; "
                                "noted). GD-share per domain = fire-fraction within each domain block.",
                          summary={c: dict(allprev_last=R.fmt(np.array(allprev[c])[:, -1]),
                                           worst_allprev=R.med([min(a) for a in allprev[c]]),
                                           aaa=R.fmt(aaa[c]), e_digital=R.med(en_di[c])) for c in cfgs})
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.3 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
