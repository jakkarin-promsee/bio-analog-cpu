"""
P10.3 — the MULTI-DOMAIN GAUNTLET (THE money figure) (design §3 P10.3). The frozen object at ALL FIVE grids (the
money figure draws grid-4 + the Tier-1 rep + grid-8 + grid-16; the per-domain strip draws all five — K7) vs
ER-strong (+ er_budget/naive field), across ≈5 native domain-IL domains (digit transforms, shared 40-D input,
shared 10-class head — K5/B2/R3), 5 seeds, + ONE reversed-order control (grid-4 + ER-strong, 5 seeds; K9). Score
new/1-back/all-prev accuracy + AAA + cumulative same-substrate energy + throughput/steps-behind + SCFF:Namer ratio
vs difficulty; overlay sleep positions; re-meter the substrate 2x2.

§10 E3 extension (post-close, pre-registered): the per-BATCH GAUNTLET-STREAM view — live-batch accuracy
(prequential) + seen-so-far all-domain accuracy + EXACT prefix-priced cumulative energy for OURS(g4) vs ER-strong,
via the triple-guarded lockstep replay (cell bit-exact vs the cache; head vs the committed err_trace; energy
endpoint vs the committed meter total). Measurement-only — every committed key must reproduce bit-exactly.
§10 E6 (round 2): the SAME view on the REVERSED domain order {noised first} — answers (a) is ER's low start real
and (b) is the late-stream drop noise- or position-specific; ER-strong now runs the reversed stream too
(completing K9's grid-4 + ER-strong letter; its reversed final AA reported).

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
LONG_BLOCKS = [68, 63, 56, 57, 68]                                     # §10 E8 — pinned per-domain lengths (rng(20260703),
                                                                       # ints [50,70], %6 redrawn): non-multiples of the
                                                                       # 24-step grid-4 sleep period; ~2-3 sleeps/domain


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
    slive = {"g4": [], "er_strong": []}; sseen = {"g4": [], "er_strong": []}    # §10 E3 — the per-batch stream view
    scume = {("g4", "analog"): [], ("g4", "digital"): [], ("er_strong", "analog"): [], ("er_strong", "digital"): []}
    sfires = []; ssleeps = []; onsets = None
    rlive = {"g4": [], "er_strong": []}; rseen = {"g4": [], "er_strong": []}    # §10 E6 — the REVERSED stream view
    rcume = {("g4", "analog"): [], ("g4", "digital"): [], ("er_strong", "analog"): [], ("er_strong", "digital"): []}
    rfires = []; rsleeps = []; ronsets = None; er_rev_aa = []
    llive = {"g4": [], "er_strong": []}; lseen = {"g4": [], "er_strong": []}    # §10 E8 — the ALIGNMENT-BREAK stream view
    lcume = {("g4", "analog"): [], ("g4", "digital"): [], ("er_strong", "analog"): [], ("er_strong", "digital"): []}
    lfires = []; lsleeps = []; lonsets = None
    lallprev = {"g4": [], "er_strong": []}; ours_long_aa = []; er_long_aa = []
    lallprev_al = []; ours_alignedlong_aa = []; alsleeps = []                    # §10 E8b — the ALIGNED-long control
    for s in SEEDS:
        gstream = P.make_gauntlet_stream(CFG, s, domains=domains)
        cache = P.build_cache_p9(P.make_committed_cell, gstream, s, CFG, store_reps=False, quick=QUICK)
        hf = R.committed_hf(s)
        n_steps = len(cache["steps"]); spd = max(1, n_steps // D)
        ra_g4 = None
        # OURS at all five grids
        for gr in GRIDS:
            ra = P.ours_bundle(cache, hf, CFG, gr)
            if gr == 4:
                ra_g4 = ra
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
        # ER-strong on the gauntlet (curves=True is read-only — the learner trajectory is bit-identical; §10 E3)
        m = P.run_bp_stream(gstream, "er", er["bp_dims"], CFG, s, lr=er["lr"], l2=er["l2"],
                            replay=er["replay"], buffer_cap=er["buffer_cap"], curves=True)
        ap, pl, ob = domain_curves(m, D)
        allprev["er_strong"].append(ap); plast["er_strong"].append(pl); oneb["er_strong"].append(ob)
        aaa["er_strong"].append(m["aaa"]); wbwt["er_strong"].append(m["worst_bwt"])
        en_an["er_strong"].append(P.bp_stream_energy(CFG, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="analog")["total"])
        en_di["er_strong"].append(P.bp_stream_energy(CFG, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="digital")["total"])
        # §10 E3 — the per-batch stream view (triple-guarded lockstep replay; measurement-only)
        curves_o = P.gauntlet_batch_curves(gstream, cache, ra_g4, hf, CFG, s)
        slive["g4"].append(curves_o["live"]); sseen["g4"].append(curves_o["seen"])
        slive["er_strong"].append(m["live_curve"]); sseen["er_strong"].append(m["seen_curve"])
        scume[("g4", "analog")].append(P.ours_cum_energy(CFG, cache, ra_g4, substrate="analog"))
        scume[("g4", "digital")].append(P.ours_cum_energy(CFG, cache, ra_g4, substrate="digital"))
        scume[("er_strong", "analog")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps,
                                                              replay=er["replay"], substrate="analog"))
        scume[("er_strong", "digital")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps,
                                                               replay=er["replay"], substrate="digital"))
        sfires.append(np.asarray(ra_g4["fires"], bool)); ssleeps.append(np.asarray(ra_g4["sleeps"], bool))
        onsets = list(gstream["real_onsets"])                          # deterministic block layout (same every seed)
        # reversed-order control (grid-4 + ER-strong)
        grev = P.make_gauntlet_stream(CFG, s, domains=domains, order="reversed")
        crev = P.build_cache_p9(P.make_committed_cell, grev, s, CFG, store_reps=False, quick=QUICK)
        ra_rev = P.ours_bundle(crev, hf, CFG, 4)
        o_fwd = P.ours_bundle(cache, hf, CFG, 4)["aa"]; o_rev = ra_rev["aa"]
        order_delta.append(o_rev - o_fwd)
        # §10 E6 — the REVERSED per-batch stream view (same triple-guarded replay + ER-strong on the reversed stream,
        # completing K9's grid-4 + ER-strong letter)
        curves_r = P.gauntlet_batch_curves(grev, crev, ra_rev, hf, CFG, s)
        rlive["g4"].append(curves_r["live"]); rseen["g4"].append(curves_r["seen"])
        m_rev = P.run_bp_stream(grev, "er", er["bp_dims"], CFG, s, lr=er["lr"], l2=er["l2"],
                                replay=er["replay"], buffer_cap=er["buffer_cap"], curves=True)
        rlive["er_strong"].append(m_rev["live_curve"]); rseen["er_strong"].append(m_rev["seen_curve"])
        er_rev_aa.append(m_rev["aa"])
        rcume[("g4", "analog")].append(P.ours_cum_energy(CFG, crev, ra_rev, substrate="analog"))
        rcume[("g4", "digital")].append(P.ours_cum_energy(CFG, crev, ra_rev, substrate="digital"))
        n_steps_rev = len(crev["steps"])
        rcume[("er_strong", "analog")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps_rev,
                                                              replay=er["replay"], substrate="analog"))
        rcume[("er_strong", "digital")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps_rev,
                                                               replay=er["replay"], substrate="digital"))
        rfires.append(np.asarray(ra_rev["fires"], bool)); rsleeps.append(np.asarray(ra_rev["sleeps"], bool))
        ronsets = list(grev["real_onsets"])
        # §10 E8 — the ALIGNMENT-BREAK long stream (forward order, pinned non-multiple per-domain blocks; the sleeps
        # land MID-domain and every switch lands at a drifting sleep phase — g4 + ER-strong, measurement-only)
        glong = P.make_gauntlet_stream(CFG, s, domains=domains, block=LONG_BLOCKS)
        clong = P.build_cache_p9(P.make_committed_cell, glong, s, CFG, store_reps=False, quick=QUICK)
        ra_long = P.ours_bundle(clong, hf, CFG, 4)
        ap_l, _, _ = domain_curves(ra_long, D)
        lallprev["g4"].append(ap_l); ours_long_aa.append(ra_long["aa"])
        curves_l = P.gauntlet_batch_curves(glong, clong, ra_long, hf, CFG, s)   # guards anchor to THIS run's cache
        llive["g4"].append(curves_l["live"]); lseen["g4"].append(curves_l["seen"])
        n_steps_long = len(clong["steps"])
        m_long = P.run_bp_stream(glong, "er", er["bp_dims"], CFG, s, lr=er["lr"], l2=er["l2"],
                                 replay=er["replay"], buffer_cap=er["buffer_cap"], curves=True)
        ap_le, _, _ = domain_curves(m_long, D)
        lallprev["er_strong"].append(ap_le); er_long_aa.append(m_long["aa"])
        llive["er_strong"].append(m_long["live_curve"]); lseen["er_strong"].append(m_long["seen_curve"])
        lcume[("g4", "analog")].append(P.ours_cum_energy(CFG, clong, ra_long, substrate="analog"))
        lcume[("g4", "digital")].append(P.ours_cum_energy(CFG, clong, ra_long, substrate="digital"))
        lcume[("er_strong", "analog")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps_long,
                                                              replay=er["replay"], substrate="analog"))
        lcume[("er_strong", "digital")].append(P.bp_cum_energy(CFG, er["bp_dims"], "er", n_steps=n_steps_long,
                                                               replay=er["replay"], substrate="digital"))
        lfires.append(np.asarray(ra_long["fires"], bool)); lsleeps.append(np.asarray(ra_long["sleeps"], bool))
        lonsets = list(glong["real_onsets"])
        # §10 E8b — the ALIGNED-long control (block 72 = exactly 3x the 24-step sleep period -> sleeps back ON the
        # boundaries; OURS g4 only) — de-confounds domain LENGTH from sleep ALIGNMENT (design §10 round 3)
        galn = P.make_gauntlet_stream(CFG, s, domains=domains, block=[72] * D)
        caln = P.build_cache_p9(P.make_committed_cell, galn, s, CFG, store_reps=False, quick=QUICK)
        ra_aln = P.ours_bundle(caln, hf, CFG, 4)
        ap_al, _, _ = domain_curves(ra_aln, D)
        lallprev_al.append(ap_al); ours_alignedlong_aa.append(ra_aln["aa"])
        alsleeps.append(np.asarray(ra_aln["sleeps"], bool))
        del caln
        # throughput FLOPs (once)
        if not flops:
            fb_o = P.fair_budget_meter(CFG, learner="ours", ours_res=P.ours_bundle(cache, hf, CFG, 4), ours_cache=cache)
            fb_e = P.fair_budget_meter(CFG, learner="er", bp_dims=er["bp_dims"], replay=er["replay"], buffer_cap=er["buffer_cap"], in_dim=CFG.DIM)
            flops = {"ours_g4": fb_o["flops_per_sample"], "er_strong": fb_e["flops_per_sample"]}
        print(f"  seed {s}: OURS g4 allprev[-1]={allprev['g4'][-1][-1]:.3f} ER allprev[-1]={allprev['er_strong'][-1][-1]:.3f} "
              f"order-delta={order_delta[-1]:+.3f} | LONG worst-allprev OURS={min(ap_l):.3f} ER={min(ap_le):.3f}", flush=True)
        del cache, crev, clong

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
    print(f"  §10 stream view (per-batch, replay-guarded): final seen-so-far OURS g4 "
          f"{R.med(np.array(sseen['g4'])[:, -1]):.3f} vs ER {R.med(np.array(sseen['er_strong'])[:, -1]):.3f} | "
          f"live-batch mean OURS {np.nanmean(np.array(slive['g4'])):.3f} vs ER "
          f"{np.nanmean(np.array(slive['er_strong'])):.3f}", flush=True)
    print(f"  §10 E6 REVERSED stream view (noised first): final seen-so-far OURS g4 "
          f"{R.med(np.array(rseen['g4'])[:, -1]):.3f} vs ER {R.med(np.array(rseen['er_strong'])[:, -1]):.3f} | "
          f"live-batch mean OURS {np.nanmean(np.array(rlive['g4'])):.3f} vs ER "
          f"{np.nanmean(np.array(rlive['er_strong'])):.3f} | ER reversed final AA {R.fmt(er_rev_aa)} "
          f"(vs forward {R.fmt(np.array(allprev['er_strong'])[:, -1])}) — K9's ER leg completed", flush=True)
    # --- §10 E8/E8b — the ALIGNMENT-BREAK read (pinned BLIND; mechanism attribution decided by the E8b control) ---
    worst_lo = R.med([min(a) for a in lallprev["g4"]]); worst_le = R.med([min(a) for a in lallprev["er_strong"]])
    sl0 = np.where(lsleeps[0])[0]; per_dom_sleeps = [int(((sl0 >= a) & (sl0 < b)).sum())
                                                    for a, b in zip(lonsets, lonsets[1:] + [len(lsleeps[0])])]
    align_gap = R.med([min(a) - min(b) for a, b in zip(lallprev_al, lallprev["g4"])])   # paired: aligned-72 - misaligned
    worst_al = R.med([min(a) for a in lallprev_al])
    sl_al = np.where(alsleeps[0])[0]
    if worst_lo >= worst_le - dacc:
        verdict_long = (f"ALIGNMENT-INDEPENDENT (OURS worst-point all-prev {worst_lo:.3f} >= ER {worst_le:.3f} - delta "
                        f"on the misaligned stream — the P10.3 retention mechanism survives sleep/boundary misalignment)")
    elif abs(align_gap) <= dacc:
        verdict_long = (f"LENGTH-EFFECT (OURS aligned-72 {worst_al:.3f} vs misaligned {worst_lo:.3f}, paired gap "
                        f"{align_gap:+.3f} <= delta — alignment is a NON-FACTOR for OURS; ER strengthens on longer "
                        f"domains (final AA {R.med(er_long_aa):.3f} long vs "
                        f"{R.med(np.array(allprev['er_strong'])[:, -1]):.3f} committed) -> the P10.3 relative win is "
                        f"switch-frequency-scoped, banked as a money-figure scope line)")
    else:
        verdict_long = (f"ALIGNMENT-LUCK (OURS aligned-72 {worst_al:.3f} vs misaligned {worst_lo:.3f}, paired gap "
                        f"{align_gap:+.3f} > delta — the committed gauntlet's flat line was partly the 24-step "
                        f"alignment; banked as a P10.3 caveat)")
    print(f"  §10 E8 ALIGNMENT-BREAK stream (blocks {LONG_BLOCKS}, {len(lsleeps[0])} steps): final seen-so-far OURS g4 "
          f"{R.med(np.array(lseen['g4'])[:, -1]):.3f} vs ER {R.med(np.array(lseen['er_strong'])[:, -1]):.3f} | "
          f"live-batch mean OURS {np.nanmean(np.array(llive['g4'])):.3f} vs ER "
          f"{np.nanmean(np.array(llive['er_strong'])):.3f} | final AA OURS {R.fmt(ours_long_aa)} vs ER {R.fmt(er_long_aa)} | "
          f"sleeps/domain (seed {SEEDS[0]}) {per_dom_sleeps} at steps {sl0.tolist()} (onsets {lonsets}) — "
          f"sleeps land MID-domain", flush=True)
    print(f"  §10 E8b ALIGNED-long control (block 72x5): OURS worst-point all-prev {worst_al:.3f} vs misaligned "
          f"{worst_lo:.3f} (paired gap {align_gap:+.3f}) | final AA {R.fmt(ours_alignedlong_aa)} | sleeps (seed "
          f"{SEEDS[0]}) at steps {sl_al.tolist()} (boundaries at 71,143,215,287,359)", flush=True)
    print(f"  §10 E8 VERDICT: {verdict_long}", flush=True)
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
    # §10 E3 — the per-batch stream view (GAUNTLET-STREAM)
    for c in ("g4", "er_strong"):
        A[f"streamlive_{c}"] = np.array(slive[c]); A[f"streamseen_{c}"] = np.array(sseen[c])
        A[f"streamcume_{c}_analog"] = np.array(scume[(c, "analog")])
        A[f"streamcume_{c}_digital"] = np.array(scume[(c, "digital")])
    A["streamfires_g4"] = np.array(sfires); A["streamsleeps_g4"] = np.array(ssleeps)
    A["stream_onsets"] = np.array(onsets, int)
    # §10 E6 — the REVERSED stream view (GAUNTLET-STREAM-REV)
    for c in ("g4", "er_strong"):
        A[f"streamrevlive_{c}"] = np.array(rlive[c]); A[f"streamrevseen_{c}"] = np.array(rseen[c])
        A[f"streamrevcume_{c}_analog"] = np.array(rcume[(c, "analog")])
        A[f"streamrevcume_{c}_digital"] = np.array(rcume[(c, "digital")])
    A["streamrevfires_g4"] = np.array(rfires); A["streamrevsleeps_g4"] = np.array(rsleeps)
    A["streamrev_onsets"] = np.array(ronsets, int)
    A["domains_rev"] = np.array(domains[::-1]); A["er_rev_aa"] = np.array(er_rev_aa)
    # §10 E8 — the ALIGNMENT-BREAK stream view (GAUNTLET-STREAM-LONG)
    for c in ("g4", "er_strong"):
        A[f"streamlonglive_{c}"] = np.array(llive[c]); A[f"streamlongseen_{c}"] = np.array(lseen[c])
        A[f"streamlongcume_{c}_analog"] = np.array(lcume[(c, "analog")])
        A[f"streamlongcume_{c}_digital"] = np.array(lcume[(c, "digital")])
        A[f"longallprev_{c}"] = np.array(lallprev[c])
    A["streamlongfires_g4"] = np.array(lfires); A["streamlongsleeps_g4"] = np.array(lsleeps)
    A["streamlong_onsets"] = np.array(lonsets, int); A["blocklong"] = np.array(LONG_BLOCKS, int)
    A["ours_long_aa"] = np.array(ours_long_aa); A["er_long_aa"] = np.array(er_long_aa)
    # §10 E8b — the ALIGNED-long control
    A["alignedlongallprev_g4"] = np.array(lallprev_al); A["ours_alignedlong_aa"] = np.array(ours_alignedlong_aa)
    A["alignedlongsleeps_g4"] = np.array(alsleeps)
    man = R.base_manifest("P10.3", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          domains=domains, tier1_rep=f"grid-{rep}", cfgs=cfgs, verdict=verdict,
                          worst_allprev=dict(ours_g4=worst_o, er_strong=worst_e),
                          substrate_total_win=total_win, order_delta=R.fmt(order_delta),
                          throughput=thr,
                          long_blocks=LONG_BLOCKS, verdict_long=verdict_long,
                          worst_allprev_long=dict(ours_g4=worst_lo, er_strong=worst_le),
                          long_final_aa=dict(ours_g4=R.fmt(ours_long_aa), er_strong=R.fmt(er_long_aa)),
                          long_sleeps_per_domain=per_dom_sleeps,
                          aligned_long=dict(block=72, worst_allprev=worst_al, align_gap_paired=align_gap,
                                            final_aa=R.fmt(ours_alignedlong_aa)),
                          notes="retention curve = post-checkpoint AA(d) per domain (learner-independent); worst-point "
                                "is the P9 honest read. Per-DOMAIN cumulative energy = proportional-to-steps shape; the "
                                "§10 GAUNTLET-STREAM arrays carry the EXACT per-batch prefix-priced cumulative energy "
                                "(supersedes the shape note at batch resolution). GD-share per domain = fire-fraction "
                                "within each domain block. §10 stream view = triple-guarded lockstep replay "
                                "(cell bit-exact vs cache fingerprint+phi_b; head vs committed err_trace; energy "
                                "endpoint vs committed meter total).",
                          summary={c: dict(allprev_last=R.fmt(np.array(allprev[c])[:, -1]),
                                           worst_allprev=R.med([min(a) for a in allprev[c]]),
                                           aaa=R.fmt(aaa[c]), e_digital=R.med(en_di[c])) for c in cfgs})
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.3 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
