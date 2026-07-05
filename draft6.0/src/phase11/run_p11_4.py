"""P11.4 — the cross-dataset gauntlet (the author's aggressive ask). MNIST -> Fashion -> CIFAR-gray as ONE class-IL
30-way stream (class-offset labels 0-29), single pass, one contiguous block per source, iid within block (R1). ONE
shared source-1-fit porthole + scaler (primary — the honest gain-shock read, R7); CIFAR center-cropped 32->28 to
share the 784 native space. forward + reversed, both arms. Reads: type-robust / type-scoped / type-broken —
does the LUT/namer keep all three DATA TYPES alive?
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp4", "figs_p11_4")
SEEDS = P.SEEDS
t0 = time.time()
med = lambda x: float(np.median(x))
C = 30
CHANCE = 1.0 / C
SOURCES = [("mnist", list(range(10)), 0), ("fashion", list(range(10)), 10), ("cifar10gray", list(range(10)), 20)]
print("=" * 78, "\nP11.4 CROSS-DATASET GAUNTLET — MNIST->Fashion->CIFAR-gray, class-IL 30-way\n", "=" * 78, flush=True)


def run_xdata(arm, cfg, seed, order):
    stream = P.make_ci_stream(SOURCES, cfg, seed, ntr=1000, nte=1500, order=order, task_size=10, shared_porthole=True)
    cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
    res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, C, seed=seed, **cfg.SLDA_KNOB), cfg, **P.COMMITTED_LOOP_G4)
    # per-block final accuracy (retention on each data TYPE after the stream ends)
    mat = res["matrix"]; T = len(mat)
    per_block_final = [mat[T - 1][k] for k in range(T)]
    ret = P.allprev_retention(mat)
    # conditioning: Gram condition number of the 30-way probe features (the namer's covariance health, R Q8)
    Fpr = P.all_tap_feats(P.make_committed_cell([cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH, seed), stream["Xpr"])
    G = Fpr.T @ Fpr
    cond = float(np.linalg.cond(G + 1e-3 * np.eye(G.shape[0])))
    return res, per_block_final, ret, cond, stream


arrays = {}; table = {}
for arm, mkcfg in [("A", lambda: P.arm_a_cfg(C)), ("B", lambda: P.recipe_instance(160, C))]:
    cfg = mkcfg()
    print(f"\n--- Arm {arm}: D={cfg.DIM} W={cfg.WIDTH} C={C} ---", flush=True)
    fwd_aa, rev_aa, worst_ret, conds = [], [], [], []
    per_block = {0: [], 1: [], 2: []}
    er_final, er_ret = [], []
    er = None
    for seed in SEEDS:
        res, pbf, ret, cond, stream = run_xdata(arm, cfg, seed, None)
        fwd_aa.append(res["aa"]); worst_ret.append(ret["worst"]); conds.append(cond)
        for k in range(3):
            per_block[k].append(pbf[k])
        resr, *_ = run_xdata(arm, cfg, seed, "reversed")
        rev_aa.append(resr["aa"])
        # ER class-IL 30-way (fixed head convention, uniform)
        if er is None:
            er = P.tune_er_arena(lambda s: P.make_ci_stream(SOURCES, cfg, s, ntr=1000, nte=1500, task_size=10),
                                 cfg, cfg.DIM, C, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
        m = P.run_bp_stream(stream, "er", er["bp_dims"], cfg, seed, lr=er["lr"], replay=er["replay"], buffer_cap=er["buffer_cap"])
        er_final.append(m["aa"]); er_ret.append(P.allprev_retention(m["matrix"])["worst"])
    oa, ra = med(fwd_aa), med(rev_aa)
    wr, erwr = med(worst_ret), med(er_ret)
    pbf_med = [med(per_block[k]) for k in range(3)]
    collapse = any(pbf_med[k] < CHANCE + 2 * CFG0.DELTA_ACC for k in range(3))
    print(f"    OURS final30 {oa:.3f} (rev {ra:.3f}, |Δ| {abs(oa-ra):.3f}) | worst-ret {wr:.3f} vs ER {erwr:.3f}", flush=True)
    print(f"    per-block final [mnist {pbf_med[0]:.3f} | fashion {pbf_med[1]:.3f} | cifar {pbf_med[2]:.3f}] "
          f"(chance {CHANCE:.3f}) | cond(G) {med(conds):.1e}", flush=True)
    if collapse:
        which = [["mnist", "fashion", "cifar"][k] for k in range(3) if pbf_med[k] < CHANCE + 2 * CFG0.DELTA_ACC]
        verd = f"TYPE-SCOPED — block(s) {which} collapse toward chance (name the mechanism)"
    elif wr >= erwr - CFG0.DELTA_ACC:
        verd = "TYPE-ROBUST — worst-point retention >= ER and all 3 data types stay alive"
    else:
        verd = "TYPE-SCOPED — all types alive but retention trails ER"
    print(f"    verdict: {verd}", flush=True)
    table[arm] = dict(final30=oa, rev=ra, orderdelta=abs(oa - ra), worst_ret=wr, er_worst_ret=erwr,
                      per_block=pbf_med, cond=med(conds), collapse=bool(collapse), verdict=verd)
    for nm, v in [("final", fwd_aa), ("rev", rev_aa), ("worstret", worst_ret), ("cond", conds),
                  ("er_worstret", er_ret)]:
        arrays[f"xdata_{arm}_{nm}"] = np.array(v, float)
    for k in range(3):
        arrays[f"xdata_{arm}_block{k}"] = np.array(per_block[k], float)

manifest = dict(rung="P11.4", git=P.git_hash(), seeds=SEEDS, C=C, chance=CHANCE, sources=[s[0] for s in SOURCES],
                table=table, note="class-IL 30-way (harder than the field's task-IL); shared source-1 porthole+scaler "
                "(primary, R7); single pass, one block/source, iid within block (R1). ER = fixed 30-way head.",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
