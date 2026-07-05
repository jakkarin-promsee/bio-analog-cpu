"""P11.6 — capacity scaling (the strike-3 'does it scale?' answer, economy half). Two one-variable sweeps on the
Fashion (r2) long-regime gauntlet:
  * W-sweep {64,128,256} at FIXED D=80 — a deliberate capacity ablation (W is NOT the recipe's ceil(1.6D) here; the
    recipe_guard would flag it, correctly — this sweep is characterization, not an Arm-B instance).
  * D-sweep {40,80,160} at recipe-W (W=ceil(1.6D)=64/128/256) — the recipe stretched.
Reads (design §2.4-P11.6): accuracy vs W (does capacity buy the gap back, or is the wall objective-shaped — P5 said
temperature not size?); GD-share vs W against the BENCH-PINNED meter-derived shape (P11.0: {0.21,0.34,0.53} — whatever
the formula predicted, the measurement confirms or breaks it, both findings); the substrate factor vs W
(E(OURS-digital)/E(OURS-analog), the P8.7 crossbar advantage re-metered — non-decreasing = the chip's best sentence);
safety (worst-BWT) per width. 3 seeds (W256 declared heavy at bench). NOTHING tuned.
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0
import plot_p11

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp6", "figs_p11_6")
SEEDS3 = P.SEEDS[:3]                                                    # declared heavy (W256/D160); 3 seeds
ARENA = "fashion"                                                      # the r2 arena
med = lambda x: float(np.median(x))
t0 = time.time()
print("=" * 78, "\nP11.6 CAPACITY SCALING — Fashion long-regime gauntlet (W-sweep @ D80, D-sweep @ recipe-W)\n", "=" * 78, flush=True)


def ours_scaled(cfg, seed):
    """One OURS run on the Fashion long gauntlet -> (aa, worst_bwt, gd-share, substrate factor). The substrate factor
    = E(OURS-digital)/E(OURS-analog) on the SAME op-counts (the compute-in-memory crossbar advantage, P8.7)."""
    stream = P.make_arena_gauntlet_stream(ARENA, cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=2000, block=24, regime="long")
    cache = P.build_cache_p9(P.make_committed_cell, stream, seed, cfg, store_reps=False)
    res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB),
                           cfg, **P.COMMITTED_LOOP_G4)
    m_a = P.meter_from_trace(cfg, P.HEAD, cache, res, substrate="analog")
    m_d = P.meter_from_trace(cfg, P.HEAD, cache, res, substrate="digital")
    return res["aa"], res["worst_bwt"], m_a["gdshare"], m_d["total"] / (m_a["total"] + P.EPS)


def sweep(cfgs, label):
    acc, bwt, gd, sub = [], [], [], []
    for tag, cfg in cfgs:
        aas, bwts, gds, subs = [], [], [], []
        for seed in SEEDS3:
            aa, wb, g, s = ours_scaled(cfg, seed)
            aas.append(aa); bwts.append(wb); gds.append(g); subs.append(s)
        acc.append(med(aas)); bwt.append(med(bwts)); gd.append(med(gds)); sub.append(med(subs))
        print(f"    [{label} {tag}] D={cfg.DIM} W={cfg.WIDTH} Fdim={cfg.DEPTH*cfg.WIDTH}  "
              f"AA {med(aas):.3f}  worstBWT {med(bwts):+.3f}  GD-share {med(gds):.3f}  substrate× {med(subs):.2f}",
              flush=True)
    return dict(acc=acc, bwt=bwt, gd=gd, sub=sub)


# ---- W-sweep at D=80 (capacity ablation; W != recipe rule, stated) --------------------------------
Ws = [64, 128, 256]
print("\n[W-sweep @ fixed D=80]", flush=True)
wcfgs = [(f"W{W}", P.clone_cfg(DIM=80, WIDTH=W, DEPTH=12, NCLASS=10, CBRS_CAP=P._cbrs_cap(10))) for W in Ws]
Wr = sweep(wcfgs, "W")
# the bench-pinned meter-derived shape (P11.0 pre-derivation 1)
_, gd_pinned = P.meter_share_derivation(Ws, D=80, L=12, C=10)
print(f"    pinned GD-share shape (bench, meter-derived) = {list(np.round(gd_pinned,3))}", flush=True)

# ---- D-sweep at recipe-W ---------------------------------------------------------------------------
Ds = [40, 80, 160]
print("\n[D-sweep @ recipe-W = ceil(1.6D)]", flush=True)
dcfgs = [(f"D{D}", P.recipe_instance(D, 10)) for D in Ds]
Dr = sweep(dcfgs, "D")

# ---- verdicts (pinned-shape confirm; capacity read; substrate read) --------------------------------
rises_meas = Wr["gd"][-1] > Wr["gd"][0]
rises_pin = gd_pinned[-1] > gd_pinned[0]
shape_confirmed = rises_meas == rises_pin
cap_buys = (Wr["acc"][-1] - Wr["acc"][0]) > CFG0.DELTA_ACC
sub_nondecr = Wr["sub"][-1] >= Wr["sub"][0] - 0.05
print("\n" + "=" * 78, flush=True)
print(f"  GD-share vs W: measured {list(np.round(Wr['gd'],3))} {'RISES' if rises_meas else 'falls'} "
      f"| pinned {'RISES' if rises_pin else 'falls'} -> shape {'CONFIRMED' if shape_confirmed else 'BROKEN'}", flush=True)
print(f"  accuracy vs W: {list(np.round(Wr['acc'],3))} -> capacity {'BUYS the gap back' if cap_buys else 'does NOT buy it (objective-shaped wall, P5)'}", flush=True)
print(f"  substrate× vs W: {list(np.round(Wr['sub'],2))} -> {'NON-DECREASING (the chip holds at scale)' if sub_nondecr else 'DECREASING (better to know)'}", flush=True)

arrays = dict(scale_W=np.array(Ws, float), gdshare_measured=np.array(Wr["gd"]),
              gdshare_pinned=np.array(gd_pinned), acc_vs_W=np.array(Wr["acc"]),
              substrate_vs_W=np.array(Wr["sub"]), bwt_vs_W=np.array(Wr["bwt"]),
              scale_D=np.array(Ds, float), acc_vs_D=np.array(Dr["acc"]),
              gdshare_vs_D=np.array(Dr["gd"]), substrate_vs_D=np.array(Dr["sub"]), bwt_vs_D=np.array(Dr["bwt"]))
manifest = dict(rung="P11.6", git=P.git_hash(), seeds=SEEDS3, arena=ARENA, regime="long",
                W_sweep=dict(W=Ws, acc=Wr["acc"], gdshare_measured=Wr["gd"], gdshare_pinned=gd_pinned.tolist(),
                             substrate=Wr["sub"], worst_bwt=Wr["bwt"]),
                D_sweep=dict(D=Ds, W=[int(np.ceil(1.6 * d)) for d in Ds], acc=Dr["acc"], gdshare=Dr["gd"],
                             substrate=Dr["sub"], worst_bwt=Dr["bwt"]),
                verdict=dict(shape_confirmed=bool(shape_confirmed), capacity_buys=bool(cap_buys),
                             substrate_nondecreasing=bool(sub_nondecr)),
                note="W-sweep is a capacity ablation (W != recipe ceil(1.6D), stated); D-sweep is the recipe stretched. "
                     "GD-share measured vs the bench-pinned meter shape (P11.0). substrate× = E(digital)/E(analog), same op-counts.",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
try:
    plot_p11.fig_scaling(OUT)
except Exception as e:
    print("  (scaling fig skipped:", e, ")")
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
