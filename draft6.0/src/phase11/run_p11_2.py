"""P11.2 — the MNIST rung (r1; both arms). (a) the 5-domain gauntlet in native 784-space -> porthole, BOTH switch
regimes (rapid-24 + long-randomized [50,70], the E8 primary); (b) Split-MNIST class-IL (5x2) + the anchor cell;
(c) the volume length-invariants (light). Arm A = frozen recipe (D40); Arm B = recipe instance (D80/W128).
Reads: does the frozen recipe survive real MNIST data (safety/retention/order-invariance while AA does what it does),
and does the architecture scale (Arm B)?
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp2", "figs_p11_2")
SEEDS = P.SEEDS
t0 = time.time()
print("=" * 78, "\nP11.2 MNIST RUNG — gauntlet (both regimes, both arms) + Split-MNIST + anchor\n", "=" * 78, flush=True)


def gauntlet_fight(arm, cfg, regime, seeds, er_cfg):
    """OURS(arm) vs ER-strong vs naive on the MNIST gauntlet; returns per-seed {aa,worst_bwt,ret} per learner."""
    out = {L: {"aa": [], "worst_bwt": [], "ret": []} for L in ["ours", "er", "naive"]}
    curves = None
    for seed in seeds:
        stream = P.make_arena_gauntlet_stream("mnist", cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000,
                                              block=24, regime=regime)
        hf = lambda: P.make_stream_head(P.HEAD, cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB)
        cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
        res = P.run_economy_p9(cache, hf, cfg, **P.COMMITTED_LOOP_G4)
        r = P.allprev_retention(res["matrix"])
        out["ours"]["aa"].append(res["aa"]); out["ours"]["worst_bwt"].append(res["worst_bwt"]); out["ours"]["ret"].append(r["worst"])
        if seed == seeds[0]:
            pq = P.ours_prequential(cache, res, cfg, seed)
            curves = dict(live=pq["live"], sleeps=res["sleeps"].astype(float), onsets=np.array(stream["real_onsets"]))
        for pol in ["er", "naive"]:
            m = P.run_bp_stream(stream, pol, er_cfg["bp_dims"], cfg, seed, lr=er_cfg["lr"],
                                replay=(er_cfg["replay"] if pol == "er" else 0),
                                buffer_cap=(er_cfg["buffer_cap"] if pol == "er" else 0))
            rr = P.allprev_retention(m["matrix"])
            out[pol]["aa"].append(m["aa"]); out[pol]["worst_bwt"].append(m["worst_bwt"]); out[pol]["ret"].append(rr["worst"])
    return out, curves


def order_inv(arm, cfg, er_cfg):
    """|AA(fwd) - AA(rev)| for OURS on the long-regime gauntlet (order-invariance)."""
    d = []
    for seed in SEEDS:
        aas = {}
        for order in [None, "reversed"]:
            stream = P.make_arena_gauntlet_stream("mnist", cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000,
                                                  block=24, regime="long", order=order)
            cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
            res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB),
                                   cfg, **P.COMMITTED_LOOP_G4)
            aas[order] = res["aa"]
        d.append(abs(aas[None] - aas["reversed"]))
    return d


med = lambda x: float(np.median(x))
arrays = {}; table = {}

for arm, cfg in [("A", P.arm_a_cfg(10)), ("B", P.recipe_instance(80, 10))]:
    print(f"\n--- Arm {arm}: D={cfg.DIM} W={cfg.WIDTH} ---", flush=True)
    # tune ER-strong per arm (input dim = cfg.DIM), modest grid for the overnight budget (grid pinned in bench)
    def gstream(seed): return P.make_arena_gauntlet_stream("mnist", cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000, block=24, regime="rapid")
    er = P.tune_er_arena(gstream, cfg, cfg.DIM, 10, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
    print(f"    ER-strong tuned: lr={er['lr']} hidden={er['hidden']} replay={er['replay']} (seed-7 AA {er['aa']:.3f})", flush=True)
    for regime in ["rapid", "long"]:
        fight, curves = gauntlet_fight(arm, cfg, regime, SEEDS, er)
        for L in fight:
            for ch in fight[L]:
                arrays[f"gaunt_{arm}_{regime}_{L}_{ch}"] = np.array(fight[L][ch], float)
        ob, eb = fight["ours"]["worst_bwt"], fight["er"]["worst_bwt"]
        oa, ea = fight["ours"]["aa"], fight["er"]["aa"]
        orr, err_ = fight["ours"]["ret"], fight["er"]["ret"]
        print(f"    [{regime:5s}] OURS aa {med(oa):.3f} worstBWT {med(ob):+.3f} ret {med(orr):.3f}  |  "
              f"ER aa {med(ea):.3f} worstBWT {med(eb):+.3f} ret {med(err_):.3f}", flush=True)
        table[f"{arm}_{regime}"] = dict(ours_aa=med(oa), ours_bwt=med(ob), ours_ret=med(orr),
                                        er_aa=med(ea), er_bwt=med(eb), er_ret=med(err_))
        if regime == "long" and curves is not None:
            arrays[f"streamlive_ours_mnist"] = curves["live"]
            arrays[f"streamsleeps_ours_mnist"] = curves["sleeps"]
            arrays[f"stream_onsets_mnist"] = curves["onsets"]
    oi = order_inv(arm, cfg, er)
    arrays[f"orderdelta_{arm}_mnist"] = np.array(oi, float)
    print(f"    order-invariance |AA(fwd)-AA(rev)| = {med(oi):.3f} (long regime)", flush=True)
    table[f"{arm}_orderinv"] = med(oi)

# ---- Split-MNIST class-IL (5x2) + anchor cell ----------------------------------------------------
print("\n--- Split-MNIST class-IL (5x2) + anchor ---", flush=True)
cA = P.arm_a_cfg(10)
def split_sources():
    return [("mnist", list(range(10)), 0)]
er_split = None
ours_split, er_splitv = [], []
for seed in SEEDS:
    stream = P.make_ci_stream(split_sources(), cA, seed, ntr=1000, nte=1500, task_size=2)
    cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cA, store_reps=False)
    res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, 10, seed=seed, **cA.SLDA_KNOB), cA, **P.COMMITTED_LOOP_G4)
    ours_split.append(res["aa"])
    if er_split is None:
        er_split = P.tune_er_arena(lambda s: P.make_ci_stream(split_sources(), cA, s, ntr=1000, nte=1500, task_size=2),
                                   cA, cA.DIM, 10, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
    m = P.run_bp_stream(stream, "er", er_split["bp_dims"], cA, seed, lr=er_split["lr"], replay=er_split["replay"], buffer_cap=er_split["buffer_cap"])
    er_splitv.append(m["aa"])
arrays["split_ours"] = np.array(ours_split); arrays["split_er"] = np.array(er_splitv)
anchor_region = [0.80, 0.98]
in_band = anchor_region[0] <= med(er_splitv) <= anchor_region[1]
print(f"    Split-MNIST class-IL: OURS-A aa {med(ours_split):.3f} | ER {med(er_splitv):.3f} "
      f"(anchor region {anchor_region} {'IN' if in_band else 'OUT — note: porthole-40, not the published raw-784 config'})", flush=True)

# ---- verdict (bet holds/scoped/broken) -----------------------------------------------------------
def safe(arm, reg): return table[f"{arm}_{reg}"]["ours_bwt"] >= table[f"{arm}_{reg}"]["er_bwt"] - CFG0.DELTA_ACC
holdsA = all(safe("A", r) for r in ["rapid", "long"]) and table["A_orderinv"] <= 0.05
holdsB = all(safe("B", r) for r in ["rapid", "long"])
verdict = ("BET HOLDS on MNIST — safety(worst-BWT)/order-invariance stay green (both arms) while static AA does what "
           "it does" if (holdsA and holdsB) else
           "BET SCOPED — safety holds in some regimes/arms but not all (see table); the claim gains a resolution ceiling")
print(f"\n  VERDICT: {verdict}", flush=True)
manifest = dict(rung="P11.2", git=P.git_hash(), seeds=SEEDS, table=table,
                split=dict(ours=med(ours_split), er=med(er_splitv), anchor_region=anchor_region, in_band=bool(in_band),
                           note="anchor run at porthole-40 (not published raw-784); exact band transcription OWED (bench)"),
                verdict=verdict, arms=dict(A="D40/W64 frozen", B="D80/W128 recipe"),
                regimes=["rapid-24", "long-randomized[50,70] (E8 primary)"], wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
import plot_p11
try:
    plot_p11.fig_stream(OUT, "mnist")
except Exception as e:
    print("  (stream fig skipped:", e, ")")
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
