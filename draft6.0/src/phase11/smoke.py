"""P11 apparatus smoke test — exercise every organ on tiny inputs; NOT a result, just wiring."""
import time, numpy as np, p11lib as P

t0 = time.time()
print("== cfg / recipe guard ==")
cA = P.arm_a_cfg(10); cB = P.recipe_instance(80, 10)
okA, _ = P.recipe_guard(cA, arm="A", C=10)
okB, _ = P.recipe_guard(cB, arm="B", C=10)
print("  armA ok", okA, "armB ok", okB, "cB.DIM/WIDTH", cB.DIM, cB.WIDTH)

print("== MNIST offline load ==")
try:
    Xtr, Ytr, Xte, Yte, side = P.load_image_split("mnist", 42, 400, 400)
    print("  mnist", Xtr.shape, "side", side, "y uniq", np.unique(Ytr).size, "range", round(float(Xtr.min()),2), round(float(Xtr.max()),2))
except Exception as e:
    print("  MNIST FAIL", type(e).__name__, str(e)[:120])

print("== digits gauntlet (proj vs bulk), 1 seed, tiny ==")
c = P.arm_a_cfg(10)
stream = P.make_arena_gauntlet_stream("digits", c, 42, ntr=400, nte=300, block=8, regime="rapid")
print("  stream n_steps", stream["n_steps"], "Xtr", stream["Xtr"].shape, "domains", stream["domains"])
hf = lambda: P.make_stream_head(P.HEAD, c.NCLASS, seed=42, **c.SLDA_KNOB)
for name, cf in [("bulk", P.make_committed_cell), ("proj", P.identity_cell), ("reservoir", P.random_frozen_cell)]:
    cache = P.build_cache_p9(cf, stream, 42, c, store_reps=False, quick=False)
    res = P.run_economy_p9(cache, hf, c, **P.COMMITTED_LOOP_G4)
    m = P.meter_from_trace(c, P.HEAD, cache, res)
    print(f"  {name:10s} aa={res['aa']:.3f} worstBWT={res['worst_bwt']:+.3f} nsleep={res['nsleep']} "
          f"Fdim={cache['steps'][0]['phi_b'].shape[1]} gdshare={m['gdshare']:.3f}")

print("== gas real stream ==")
cg = P.arm_a_cfg(6)
gs, meta = P.make_real_stream("gas", cg, 42, arm="A")
print("  gas n_steps", gs["n_steps"], "blocks", meta["blocks"], "imbalance", round(meta["imbalance"],2), "Xtr", gs["Xtr"].shape)
cache = P.build_cache_p9(P.make_committed_cell, gs, 42, cg, store_reps=False)
res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, 6, seed=42, **cg.SLDA_KNOB), cg, **P.COMMITTED_LOOP_G4)
print("  gas OURS aa(matrix)", round(res["aa"],3), "worstBWT", round(res["worst_bwt"],3), "nsleep", res["nsleep"])
print("  no-change balacc", round(P.nochange_baseline(gs),3), "| sgd-linear balacc", round(P.sgd_linear(gs, 6, cg.DIM, lr=0.1),3))

print("== meter-share derivation + floor ==")
Ws, sh = P.meter_share_derivation([64,128,256], D=80, C=10)
print("  gdshare vs W", list(np.round(sh,3)))
print("  floor", P.floor_state(0.5, 0.52, ceiling=0.87, chance=0.1)["label"],
      "|", P.floor_state(0.11, 0.10, ceiling=0.15, chance=0.1)["label"])
print(f"== smoke done {time.time()-t0:.1f}s ==")
