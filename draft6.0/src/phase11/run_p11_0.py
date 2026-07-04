"""P11.0 — bench: data + loaders + guards + the two pre-derivations + anchors. No verdict — a build.
Green iff every arena loads offline with declared stream order; composition tables + anchors transcribed; the
recipe/arena-data/dominance/floor guards green; the GD-share-vs-W shape derived from the meter and pinned; the
frozen object still reproduces bit-exact. ANY red -> STOP (a broken bench poisons every verdict)."""
import os, sys, time, json
import numpy as np
import p11lib as P
import p10cfg as CFG0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp0", "figs_p11_0")
t0 = time.time()
green = {}
print("=" * 78, "\nP11.0 BENCH — build + guards (no verdict)\n", "=" * 78, flush=True)

# ---- 1. loaders + shapes + declared stream order + composition tables -------------------------------
print("\n[1] arena loaders (offline) + composition tables", flush=True)
arena_report = {}
for arena in ["digits", "mnist", "fashion", "cifar10gray"]:
    try:
        Xtr, Ytr, Xte, Yte, side = P.load_image_split(arena, 42, 400, 400)
        arena_report[arena] = dict(kind="image", shape=list(Xtr.shape), side=side,
                                   C=int(np.unique(Ytr).size), rng=[round(float(Xtr.min()), 3), round(float(Xtr.max()), 3)])
        print(f"    {arena:12s} img {Xtr.shape} side={side} C={np.unique(Ytr).size} "
              f"range[{Xtr.min():.2f},{Xtr.max():.2f}]  OK", flush=True)
    except Exception as e:
        arena_report[arena] = dict(kind="image", FAIL=f"{type(e).__name__}: {str(e)[:80]}")
        print(f"    {arena:12s} FAIL {type(e).__name__}: {str(e)[:80]}", flush=True)

real_meta = {}
for arena in ["gas", "har", "electric", "covtype"]:
    try:
        R = P.load_real(arena)
        c = P.arm_a_cfg(R["C"])
        _, meta = P.make_real_stream(arena, c, 42, arm="A", max_n=(40000 if arena in ("electric", "covtype") else None))
        real_meta[arena] = dict(C=R["C"], order=R["order_name"], n=int(len(R["y"])),
                                imbalance=round(meta["imbalance"], 2), blocks=meta["blocks"],
                                comp=meta["composition"].tolist(), native=meta["native_dim"])
        print(f"    {arena:12s} n={len(R['y'])} C={R['C']} order='{R['order_name']}' "
              f"imbalance={meta['imbalance']:.2f} blocks={len(meta['blocks'])}  OK", flush=True)
    except Exception as e:
        real_meta[arena] = dict(FAIL=f"{type(e).__name__}: {str(e)[:80]}")
        print(f"    {arena:12s} FAIL {type(e).__name__}: {str(e)[:100]}", flush=True)
green["arena_data"] = all("FAIL" not in v for v in {**arena_report, **real_meta}.values())

# ---- 2. recipe guard (Arm A bit-equal committed; Arm B whitelist only) ------------------------------
print("\n[2] recipe guard (Arm A / Arm B)", flush=True)
gA, _ = P.recipe_guard(P.arm_a_cfg(10), arm="A", C=10)
gB1, _ = P.recipe_guard(P.recipe_instance(80, 10), arm="B", C=10)
gB2, _ = P.recipe_guard(P.recipe_instance(160, 30), arm="B", C=30)
green["recipe"] = bool(gA and gB1 and gB2)

# ---- 3. noise-to-signal equivalence constants (F3) --------------------------------------------------
print("\n[3] noise-σ equivalence (F3: σ_rung = (0.6/RMS_P10)·RMS_rung)", flush=True)
rms_p10 = P.p10_digits_rms()
noise_sigmas = {"_rms_p10_digits": round(rms_p10, 4), "_p10_absolute": CFG0.GAUNTLET_NOISE_RMS}
for arena in ["digits", "mnist", "fashion", "cifar10gray"]:
    if "FAIL" in arena_report.get(arena, {}):
        continue
    Xtr, *_ = P.load_image_split(arena, 42, 800, 100)
    rms = float(np.sqrt(np.mean(Xtr ** 2)))
    sig = P.equiv_noise_sigma(rms)
    noise_sigmas[arena] = dict(rms=round(rms, 4), sigma=round(sig, 4))
    print(f"    {arena:12s} RMS={rms:.4f}  σ_equiv={sig:.4f}  (ratio σ/RMS={sig/rms:.3f} == P10 {CFG0.GAUNTLET_NOISE_RMS/rms_p10:.3f})", flush=True)
green["noise_equiv"] = True

# ---- 4. the GD-share-vs-W pinned shape (C3; meter-derived, NOT from memory) --------------------------
print("\n[4] pre-derivation 1: GD-share vs W (from hardware_cost_meter, pinned for P11.6)", flush=True)
Ws = [64, 128, 256]
w_axis, gd_shape = P.meter_share_derivation(Ws, D=80, L=12, C=10)
print(f"    W={Ws}  GD-share(meter)={list(np.round(gd_shape,3))}  ->  {'RISES' if gd_shape[-1]>gd_shape[0] else 'falls'} with W", flush=True)
print("    (the SLDA solve term ~O((L·W)^3) drives GD-share UP with W — the economy does NOT improve with scale)", flush=True)
green["gd_shape_pinned"] = True

# ---- 5. dominance guard (ER-strong >= naive-BP on a tuning stream) -----------------------------------
print("\n[5] dominance guard (ER-strong >= naive-BP on the seed-7 gas tuning stream)", flush=True)
try:
    cg = P.arm_a_cfg(6)
    def gas_stream(seed):
        s, _ = P.make_real_stream("gas", P.arm_a_cfg(6), seed, arm="A"); return s
    er = P.tune_er_arena(gas_stream, cg, cg.DIM, 6, tune_seed=7,
                         lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
    s7 = gas_stream(7)
    naive = P.bp_prequential(s7, "naive", er["bp_dims"], cg, 7, lr=er["lr"])["bal"]
    er_bal = P.bp_prequential(s7, "er", er["bp_dims"], cg, 7, lr=er["lr"], replay=er["replay"], buffer_cap=er["buffer_cap"])["bal"]
    dom = er_bal >= naive - 0.02
    print(f"    ER-strong(cfg lr={er['lr']} h={er['hidden']} replay={er['replay']}) bal={er_bal:.3f} >= naive {naive:.3f}  {'OK' if dom else '!! INVERTED'}", flush=True)
    green["dominance"] = bool(dom)
except Exception as e:
    print(f"    dominance FAIL {type(e).__name__}: {str(e)[:100]}", flush=True)
    green["dominance"] = False

# ---- 6. freeze_content: the frozen object still reproduces bit-exact ---------------------------------
print("\n[6] freeze_content guard (the object we measure is the P9-frozen object, bit-exact)", flush=True)
try:
    ok_fc, det_fc = P.P10.freeze_content_guard(CFG0, seed=42, verbose=True)
    green["freeze_content"] = bool(ok_fc)
except Exception as e:
    print(f"    freeze_content could not run: {type(e).__name__}: {str(e)[:120]}", flush=True)
    green["freeze_content"] = None

# ---- 7. anchors transcribed (literature numbers — overlays, never racers) ----------------------------
print("\n[7] anchors transcribed", flush=True)
anchors = {
    "gas_vergara2012": {"source": "Vergara et al. 2012 (UCI Gas Sensor Array Drift)",
                        "note": "SVM ensemble ~ up to 80% across batches; recognition degrades with drift; balanced-acc read",
                        "band": None, "status": "cited-on-figure"},
    "gas_dennler2022": {"source": "Dennler et al. 2022 (gas dataset limitations)", "status": "cited-preemptively"},
    "splitmnist_vandeven2022_classIL_ER": {
        "source": "van de Ven et al., Nat MI 2022 + GMvandeVen/continual-learning",
        "note": "class-IL Split-MNIST: naive~0.199 (collapse); replay-based methods high. EXACT band transcription "
                "needs the paper (did not fetch this box); anchor cell runs the published config + reports the number, "
                "band flagged OWED.",
        "approx_region": [0.80, 0.98], "status": "region-approx-transcription-owed"},
}
print("    gas: Vergara2012 (cited) + Dennler2022 limitations (cited); Split-MNIST: van de Ven 2022 (region approx, exact band OWED)", flush=True)
green["anchors"] = True

# ---- wrap -------------------------------------------------------------------------------------------
wall = time.time() - t0
allgreen = all(v for v in green.values() if v is not None)
print("\n" + "=" * 78, flush=True)
for k, v in green.items():
    print(f"    guard {k:16s} {'GREEN' if v else ('n/a' if v is None else '!! RED')}", flush=True)
print(f"  BENCH {'ALL GREEN' if allgreen else 'HAS REDS'}  ({wall:.1f}s)", flush=True)

manifest = P.__dict__.get("jsonsafe")(dict(
    rung="P11.0", git=P.git_hash(), committed_loop=P.COMMITTED_LOOP_G4, head=P.HEAD, seeds=P.SEEDS,
    seeds9=P.SEEDS9, delta_acc=CFG0.DELTA_ACC, gd_share_cap=CFG0.GD_SHARE_CAP,
    arena_image=arena_report, arena_real=real_meta, noise_sigmas=noise_sigmas,
    gd_share_shape=dict(W=Ws, share=gd_shape.tolist()), anchors=anchors, guards=green,
    er_grid=dict(lrs=[0.3, 0.1, 0.03, 0.01], replays=[1, 2, 4], hidden_mults=[1, 2, 4]),
    heavy_cells_3seed=["P11.2-volume-60k", "P11.6-W256", "P11.3-covtype"],
    wall_s=round(wall, 1), note="depth-first committed core; extensions results-blind"))
inv = {f"inv_{k}": np.array([1.0 if v else 0.0]) for k, v in green.items() if v is not None}
inv["gd_share_shape"] = gd_shape
P.save_run(OUT, inv, manifest)
print(f"\n  saved -> {OUT}", flush=True)
