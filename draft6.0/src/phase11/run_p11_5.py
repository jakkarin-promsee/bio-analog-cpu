"""P11.5 — the hardness ladder r2/r3 + the class-count crossover (the strike-3 'does it scale?' answer, hardness +
memory halves).
  (A) r2 (Fashion) + r3 (CIFAR-gray) gauntlet rungs — the P11.2 protocol, long regime (E8 primary), both arms, vs
      per-arm-tuned ER + naive. The FLOOR criterion keeps r3 honest (grayscale-cropped CIFAR through a 40-D porthole
      is near the resolution floor). Reads: bet holds/scoped/broken per rung + fraction-of-ceiling.
  (B) the memory-fairness CROSSOVER — the analytic bytes-vs-C curve: a fixed-byte REPLAY buffer dilutes per-class as
      O(1/C); the PROTOTYPE+GRAM namer (SLDA: mu C x F + tied cov F x F) grows as O(C*F + F^2) but never dilutes
      per-class. Report the crossover C* where prototype+Gram becomes the more memory-efficient representation, with
      measured retention points at C=10 (Split-MNIST) and C=20 (MNIST+Fashion 20-way). NOTHING tuned.
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0
import plot_p11

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp5", "figs_p11_5")
SEEDS = P.SEEDS
med = lambda x: float(np.median(x))
t0 = time.time()
print("=" * 78, "\nP11.5 HARDNESS LADDER r2/r3 (Fashion, CIFAR-gray) + class-count CROSSOVER\n", "=" * 78, flush=True)


def gauntlet_fight(arena, cfg, seeds, er_cfg, regime="long"):
    out = {L: {"aa": [], "worst_bwt": [], "ret": []} for L in ["ours", "er", "naive"]}
    for seed in seeds:
        stream = P.make_arena_gauntlet_stream(arena, cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000, block=24, regime=regime)
        cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
        res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB),
                               cfg, **P.COMMITTED_LOOP_G4)
        r = P.allprev_retention(res["matrix"])
        out["ours"]["aa"].append(res["aa"]); out["ours"]["worst_bwt"].append(res["worst_bwt"]); out["ours"]["ret"].append(r["worst"])
        for pol in ["er", "naive"]:
            m = P.run_bp_stream(stream, pol, er_cfg["bp_dims"], cfg, seed, lr=er_cfg["lr"],
                                replay=(er_cfg["replay"] if pol == "er" else 0),
                                buffer_cap=(er_cfg["buffer_cap"] if pol == "er" else 0))
            rr = P.allprev_retention(m["matrix"])
            out[pol]["aa"].append(m["aa"]); out[pol]["worst_bwt"].append(m["worst_bwt"]); out[pol]["ret"].append(rr["worst"])
    return out


arrays = {}; table = {}
# ---- (A) r2 / r3 gauntlet rungs -------------------------------------------------------------------
for rung, arena, seeds in [("r2", "fashion", SEEDS), ("r3", "cifar10gray", SEEDS[:3])]:
    print(f"\n--- {rung}: {arena} gauntlet (long regime, both arms) ---", flush=True)
    ceil = None
    for arm, cfg in [("A", P.arm_a_cfg(10)), ("B", P.recipe_instance(80, 10))]:
        def gstream(seed): return P.make_arena_gauntlet_stream(arena, cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000, block=24, regime="rapid")
        er = P.tune_er_arena(gstream, cfg, cfg.DIM, 10, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
        fight = gauntlet_fight(arena, cfg, seeds, er, regime="long")
        oa, ob = med(fight["ours"]["aa"]), med(fight["ours"]["worst_bwt"])
        orr = med(fight["ours"]["ret"]); ea = med(fight["er"]["aa"]); eb = med(fight["er"]["worst_bwt"]); err_ = med(fight["er"]["ret"])
        if ceil is None:                                               # joint-BP ceiling once per arena (Arm A dim)
            st = P.make_arena_gauntlet_stream(arena, P.arm_a_cfg(10), seeds[0], ntr=CFG0.GAUNTLET_NTR, nte=2000, regime="long")
            ceil = P.P10.joint_bp_ceiling(st, P.arm_a_cfg(10), 40, 10, seeds[0])
        floor = ceil < 0.1 + 5 * CFG0.DELTA_ACC or (oa < 0.1 + 2 * CFG0.DELTA_ACC and ea < 0.1 + 2 * CFG0.DELTA_ACC)
        safe = ob >= eb - CFG0.DELTA_ACC
        verd = ("FLOOR (ceiling %.2f)" % ceil if floor else
                ("BET HOLDS (safety win)" if safe else "BET SCOPED (safety not > ER here)"))
        print(f"    [{arm}] OURS aa {oa:.3f} worstBWT {ob:+.3f} ret {orr:.3f} | ER aa {ea:.3f} worstBWT {eb:+.3f} ret {err_:.3f} "
              f"| ceiling {ceil:.3f} -> {verd}", flush=True)
        table[f"{rung}_{arm}"] = dict(arena=arena, ours_aa=oa, ours_bwt=ob, ours_ret=orr, er_aa=ea, er_bwt=eb,
                                      er_ret=err_, ceiling=ceil, floor=bool(floor), verdict=verd)
        for L in fight:
            for ch in fight[L]:
                arrays[f"gaunt_{rung}_{arm}_{L}_{ch}"] = np.array(fight[L][ch], float)

# ---- (B) class-count crossover --------------------------------------------------------------------
print("\n--- class-count crossover (analytic bytes-vs-C + measured C=10/C=20) ---", flush=True)
# analytic: fixed-byte replay keeping k samples/class (F-dim raw) vs prototype+Gram (C*F means + F*F tied cov)
F = 12 * 64                                                             # Arm-A all-tap feature dim (L*W)
k = 2                                                                   # replay samples/class (byte-matched regime)
Cs = np.arange(2, 101)
replay_bytes = Cs * k * (F + 1)                                        # C * k * (features+label), grows O(C)
protogram_bytes = Cs * F + F * F                                      # C*F means + F*F tied covariance, O(C*F + F^2)
cross_idx = np.where(protogram_bytes < replay_bytes)[0]
Cstar = int(Cs[cross_idx[0]]) if len(cross_idx) else None
print(f"    F={F} k={k}: prototype+Gram bytes < replay bytes for C >= {Cstar} (the crossover; beyond it the namer "
      f"is the more memory-efficient representation)", flush=True)

# measured points: OURS vs byte-matched ER retention at C=10 (Split-MNIST) and C=20 (MNIST+Fashion 20-way)
def ci_retention(sources, C, seeds, task_size=2):
    cfg = P.arm_a_cfg(C)
    ours, er_ret = [], []
    er = None
    for seed in seeds:
        stream = P.make_ci_stream(sources, cfg, seed, ntr=1000, nte=1500, task_size=task_size)
        cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
        res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, C, seed=seed, **cfg.SLDA_KNOB), cfg, **P.COMMITTED_LOOP_G4)
        ours.append(P.allprev_retention(res["matrix"])["worst"])
        if er is None:
            er = P.tune_er_arena(lambda s: P.make_ci_stream(sources, cfg, s, ntr=1000, nte=1500, task_size=task_size),
                                 cfg, cfg.DIM, C, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
        m = P.run_bp_stream(stream, "er", er["bp_dims"], cfg, seed, lr=er["lr"], replay=er["replay"], buffer_cap=er["buffer_cap"])
        er_ret.append(P.allprev_retention(m["matrix"])["worst"])
    return med(ours), med(er_ret)

o10, e10 = ci_retention([("mnist", list(range(10)), 0)], 10, SEEDS, task_size=2)
o20, e20 = ci_retention([("mnist", list(range(10)), 0), ("fashion", list(range(10)), 10)], 20, SEEDS, task_size=2)
print(f"    measured worst-retention: C=10  OURS {o10:.3f} vs ER {e10:.3f} | C=20  OURS {o20:.3f} vs ER {e20:.3f}", flush=True)
print(f"    -> as C grows the replay buffer dilutes; OURS retention gap vs ER: C10 {o10-e10:+.3f} -> C20 {o20-e20:+.3f}", flush=True)

arrays["crossover_analytic_C"] = Cs.astype(float)
arrays["crossover_replay_bytes"] = replay_bytes.astype(float)
arrays["crossover_protogram_bytes"] = protogram_bytes.astype(float)
arrays["crossover_measured_C"] = np.array([10, 20], float)
arrays["crossover_measured_ours"] = np.array([o10, o20], float)
arrays["crossover_measured_er"] = np.array([e10, e20], float)

manifest = dict(rung="P11.5", git=P.git_hash(), seeds=SEEDS, table=table,
                crossover=dict(F=F, k=k, Cstar=Cstar, measured=dict(C10=[o10, e10], C20=[o20, e20])),
                note="r2/r3 gauntlet long-regime both arms vs per-arm-tuned ER; FLOOR by joint-BP ceiling. crossover "
                     "analytic bytes-vs-C (replay O(C) vs prototype+Gram O(C*F+F^2)) + measured worst-retention C=10/20.",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
try:
    plot_p11.fig_crossover(OUT)
except Exception as e:
    print("  (crossover fig skipped:", e, ")")
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
