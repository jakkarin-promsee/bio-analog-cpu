"""P11.3 — the real-world streams (the phase HEADLINE). gas (nature's own gauntlet) -> HAR -> electricity ->
covertype. The accuracy channel = PREQUENTIAL (balanced) accuracy, every learner incl. no-change (R2); 80/20
within-block splits feed worst-BWT/retention only. Roster: OURS-A (porthole-40) · OURS-B (recipe D) · ER-strong-
matched (byte-matched buffer) · ER-strong-bigbuf (cap min(10%,5000)) · sgd-linear (native) · first-block-frozen ·
no-change. Verdicts vs the STRONGER ER (R3). FLOOR where no-change wins (D2). Reads: win / safer-not-stronger / loss.
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp3", "figs_p11_3")
t0 = time.time()
med = lambda x: float(np.median(x)) if len(x) else float("nan")
NATIVE = dict(gas=128, har=561, electric=8, covtype=54)
CLASSES = dict(gas=6, har=6, electric=2, covtype=7)
print("=" * 78, "\nP11.3 REAL-WORLD STREAMS — prequential balanced accuracy (the headline)\n", "=" * 78, flush=True)


def ours_on(stream, meta, cfg, seed):
    cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
    res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, meta["C"], seed=seed, **cfg.SLDA_KNOB),
                           cfg, **P.COMMITTED_LOOP_G4)
    pq = P.ours_prequential(cache, res, cfg, seed)
    m = P.meter_from_trace(cfg, P.HEAD, cache, res)
    return res, pq, m


def race_arena(arena, seeds, *, reversed_order=False, arms=("A", "B"), full_roster=True, max_n=None):
    C = CLASSES[arena]
    R = {}
    def add(k, v): R.setdefault(k, []).append(v)
    curves = None; meta0 = None; er = None
    for seed in seeds:
        streamA = None
        for arm in arms:
            cfg = P.arm_a_cfg(C) if arm == "A" else P.recipe_instance(min(NATIVE[arena], 160), C)
            stream, meta = P.make_real_stream(arena, cfg, seed, arm=arm, max_n=max_n)
            res, pq, m = ours_on(stream, meta, cfg, seed)
            add(f"ours_{arm}", pq["bal"]); add(f"ours_{arm}_bwt", res["worst_bwt"]); add(f"ours_{arm}_gd", m["gdshare"])
            if arm == "A":
                streamA, metaA = stream, meta
                if seed == seeds[0]:
                    curves = dict(live=pq["live"], sleeps=res["sleeps"].astype(float),
                                  onsets=np.array(stream["real_onsets"]), nochange=P.nochange_baseline(stream))
                    meta0 = meta
        cfgA = P.arm_a_cfg(C)
        add("nochange", P.nochange_baseline(streamA)); add("sgd", P.sgd_linear(streamA, C, cfgA.DIM, lr=0.1))
        add("frozen", P.first_block_frozen(streamA, cfgA, C, seed))
        if er is None:
            er = P.tune_er_arena(lambda s: P.make_real_stream(arena, P.arm_a_cfg(C), s, max_n=max_n)[0],
                                 cfgA, cfgA.DIM, C, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
        big_cap = int(min(0.1 * streamA["n_steps"] * cfgA.BATCH, 5000))
        add("er_matched", P.bp_prequential(streamA, "er", er["bp_dims"], cfgA, seed, lr=er["lr"],
                                           replay=er["replay"], buffer_cap=CFG0.PROBE_N)["bal"])
        if full_roster:
            add("er_bigbuf", P.bp_prequential(streamA, "er", er["bp_dims"], cfgA, seed, lr=er["lr"],
                                              replay=er["replay"], buffer_cap=big_cap)["bal"])
        if reversed_order:
            sr, mr = P.make_real_stream(arena, cfgA, seed, arm="A", order="reversed", max_n=max_n)
            _, pqr, _ = ours_on(sr, mr, cfgA, seed)
            add("ours_A_rev", pqr["bal"])
    return R, curves, meta0


arrays = {}; table = {}
plans = [("gas", P.SEEDS, True, ("A", "B"), True, None),
         ("har", P.SEEDS, False, ("A", "B"), True, None),
         ("electric", P.SEEDS, False, ("A", "B"), True, None),
         ("covtype", P.SEEDS[:3], False, ("A", "B"), False, 40000)]      # covtype heavy: 3 seeds (declared), 40k slice
for arena, seeds, rev, arms, full, max_n in plans:
    print(f"\n--- {arena} (C={CLASSES[arena]}, native={NATIVE[arena]}, {len(seeds)} seeds) ---", flush=True)
    R, curves, meta = race_arena(arena, seeds, reversed_order=rev, arms=arms, full_roster=full, max_n=max_n)
    for k, v in R.items():
        arrays[f"balacc_{k}_{arena}" if not k.endswith(("_bwt", "_gd", "_rev")) else f"{k}_{arena}"] = np.array(v, float)
    nc = med(R["nochange"]); fr = med(R["frozen"]); sg = med(R["sgd"])
    oa, ob = med(R["ours_A"]), med(R.get("ours_B", [np.nan]))
    em = med(R["er_matched"]); eb = med(R.get("er_bigbuf", R["er_matched"]))
    er_strong = max(em, eb)
    print(f"    OURS-A {oa:.3f} | OURS-B {ob:.3f} | ER-matched {em:.3f} | ER-bigbuf {eb:.3f} | "
          f"sgd-lin {sg:.3f} | frozen {fr:.3f} | no-change {nc:.3f}", flush=True)
    # FLOOR (D2): does any raced learner beat no-change + delta?
    raced = [oa, ob, em, eb, sg]
    floor = not any(a > nc + CFG0.DELTA_ACC for a in raced if not np.isnan(a))
    # verdict vs the STRONGER ER (R3): win / safer-not-stronger / loss
    obwt = med(R["ours_A_bwt"])
    if floor:
        verd = f"FLOOR (no-change {nc:.3f} not beaten)"
    elif oa >= er_strong - CFG0.DELTA_ACC:
        verd = "WIN (OURS >= stronger-ER at prequential accuracy)"
    elif oa > fr + CFG0.DELTA_ACC:
        verd = "SCOPED (safer-not-stronger: loses acc but beats the frozen learning floor)"
    else:
        verd = "LOSS (below the stronger ER and near the frozen floor)"
    print(f"    worst-BWT(OURS-A) {obwt:+.3f} | verdict: {verd}", flush=True)
    if rev:
        print(f"    order-invariance |fwd-rev| = {abs(oa - med(R['ours_A_rev'])):.3f}", flush=True)
    table[arena] = dict(ours_A=oa, ours_B=ob, er_matched=em, er_bigbuf=eb, sgd=sg, frozen=fr, nochange=nc,
                        ours_A_bwt=obwt, verdict=verd, floor=bool(floor),
                        imbalance=round(meta["imbalance"], 2), C=CLASSES[arena])
    if curves is not None:
        arrays[f"streamlive_ours_{arena}"] = curves["live"]
        arrays[f"streamsleeps_ours_{arena}"] = curves["sleeps"]
        arrays[f"stream_onsets_{arena}"] = curves["onsets"]
        arrays[f"nochange_{arena}"] = np.array([curves["nochange"]])

manifest = dict(rung="P11.3", git=P.git_hash(), seeds=P.SEEDS, covtype_seeds=P.SEEDS[:3], table=table,
                roster=["ours_A(porthole40)", "ours_B(recipe)", "er_matched(byte)", "er_bigbuf", "sgd_linear",
                        "first_block_frozen", "no_change"],
                note="accuracy channel = prequential balanced acc (R2); verdicts vs the STRONGER ER (R3); "
                     "FLOOR where no-change wins (D2). covtype 3 seeds/40k (heavy, declared).",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
import plot_p11
for arena in ["gas", "har", "electric", "covtype"]:
    try: plot_p11.fig_stream(OUT, arena)
    except Exception as e: print(f"  (stream {arena} skipped: {e})")
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
