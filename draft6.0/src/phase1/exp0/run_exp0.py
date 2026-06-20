"""
exp0 FULL — 5 seeds, with IQR. Answers the three exp0 questions + sets the open knobs:

  (1) SCFF separates?      -> F4 goodness sep, F3 separability heatmap, F5 boundary (gate, re-confirmed n=5)
  (2) full-GD ceiling?     -> 0c, the number Exp 1-3 quote against (F1)
  0a two-sided vs contrast -> ablation table (linear probe AND 2-layer MLP readout)
  0b SCFF vs Oja vs random -> ablation table (the linear probe is the discriminating read)
  rise-with-depth probe    -> per-layer linear probe on a 3-D 64-cluster checkerboard

Two readouts on purpose: a strict LINEAR probe (shows feature quality; SCFF's edge lives here)
and the spec's 2-layer Adam MLP readout (the 'system' number; strong enough to wash out 0b).

Reproducible: writes manifest.json + raw arrays.npz next to the figures. numpy only.
Run: python run_exp0.py            (~few min for 5 seeds)
"""
from __future__ import annotations
import json, os, time
import numpy as np
from sklearn.linear_model import LogisticRegression

from scff_gate import (SCFF, make_checkerboard, probe_acc_per_layer,
                       DIMS, SEED, THETA, LR_SCFF, GOODNESS_MODE, TAPS,
                       CHECK_GRID, CHECK_SPACING, CHECK_OVERLAP, PROBE_C)
from models_extra import (MLP, OjaStack, RandomProjStack, match_width,
                          make_checkerboard_hd)
import subprocess
import plot   # figures regenerate from saved arrays via plot.draw_all


def _git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=os.path.dirname(os.path.abspath(__file__)),
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

SEEDS   = [42, 137, 271, 314, 1729]
BATCH   = 32
STREAM  = 50_000
CKPTS   = [100, 300, 1000, 3000, 10000, 30000, 50000]
OUT     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs_exp0")
os.makedirs(OUT, exist_ok=True)


def taps_feat(stack, X):
    return np.concatenate(stack.infer(X)[-TAPS:], axis=1)


def linprobe(stack, Xtr, Ytr, Xte, Yte):
    clf = LogisticRegression(C=PROBE_C, max_iter=3000).fit(taps_feat(stack, Xtr), Ytr)
    return clf.score(taps_feat(stack, Xte), Yte)


def mlp_readout(stack, Xtr, Ytr, Xte, Yte, seed, epochs=120):
    F, Fte = taps_feat(stack, Xtr), taps_feat(stack, Xte)
    ro = MLP([F.shape[1], 32, 2], seed, lr=2e-3); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            ro.train_step(F[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    return ro.accuracy(Fte, Yte)


def run_seed(seed):
    gen = make_checkerboard
    Xtr, Ytr = gen(2000, np.random.default_rng(seed + 1))
    Xte, Yte = gen(2000, np.random.default_rng(seed + 2))
    Xg, _ = gen(2000, np.random.default_rng(seed + 3))
    out = {}

    # --- SCFF (two-sided): checkpointed goodness + per-layer probe + tapped held-out curve ---
    sc = SCFF(DIMS, THETA, LR_SCFF, seed, objective="two_sided", goodness_mode=GOODNESS_MODE)
    gpos, gneg, perlayer, scff_curve, dead = [], [], [], [], []

    def scff_ckpt():
        Gp, Gn = sc.goodness(Xg)
        gpos.append(Gp); gneg.append(Gn)
        perlayer.append(probe_acc_per_layer(sc, Xtr, Ytr, Xte, Yte))
        scff_curve.append(linprobe(sc, Xtr, Ytr, Xte, Yte))
        dead.append(sc.dead_fraction(Xg))

    rng = np.random.default_rng(seed); seen = 0; it = iter(CKPTS); nx = next(it)
    scff_ckpt()
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng); sc.train_step(Xb, rng); seen += BATCH
        if nx and seen >= nx:
            scff_ckpt(); nx = next(it, None)
    out["scff_curve"] = scff_curve
    out["gpos"] = gpos; out["gneg"] = gneg; out["perlayer"] = perlayer; out["dead"] = dead
    out["scff_lin"] = linprobe(sc, Xtr, Ytr, Xte, Yte)
    out["scff_mlp"] = mlp_readout(sc, Xtr, Ytr, Xte, Yte, seed)
    # arrays so F4/F5 regenerate from saved data (no retraining in the figure code)
    GPs, GNs = sc.goodness_samples(Xg, seed=7)
    out["gp_top"] = GPs[:, -1]; out["gn_top"] = GNs[:, -1]
    bclf = LogisticRegression(C=PROBE_C, max_iter=3000).fit(taps_feat(sc, Xtr), Ytr)
    lim = ((CHECK_GRID - 1) / 2 * CHECK_SPACING + 3 * CHECK_OVERLAP) * 1.12
    bxs = np.linspace(-lim, lim, 300); BXX, BYY = np.meshgrid(bxs, bxs)
    out["bz"] = bclf.predict(taps_feat(sc, np.stack([BXX.ravel(), BYY.ravel()], 1))).reshape(300, 300)
    out["blim"] = lim; out["bacc"] = linprobe(sc, Xtr, Ytr, Xte, Yte)

    # --- SCFF (contrast) final ---
    sc2 = SCFF(DIMS, THETA, LR_SCFF, seed, objective="contrast", goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed); seen = 0
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng); sc2.train_step(Xb, rng); seen += BATCH
    out["contrast_lin"] = linprobe(sc2, Xtr, Ytr, Xte, Yte)
    out["contrast_mlp"] = mlp_readout(sc2, Xtr, Ytr, Xte, Yte, seed)

    # --- 0b rivals ---
    oja = OjaStack(DIMS, seed, lr=0.01); rng = np.random.default_rng(seed); seen = 0
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng); oja.train_step(Xb, rng); seen += BATCH
    out["oja_lin"] = linprobe(oja, Xtr, Ytr, Xte, Yte)
    out["oja_mlp"] = mlp_readout(oja, Xtr, Ytr, Xte, Yte, seed)
    rp = RandomProjStack(DIMS, seed)
    out["rp_lin"] = linprobe(rp, Xtr, Ytr, Xte, Yte)
    out["rp_mlp"] = mlp_readout(rp, Xtr, Ytr, Xte, Yte, seed)

    # --- 0c full-GD ceiling (checkpointed held-out curve) + memorization gap ---
    tgt = sum(W.size + b.size for W, b in zip(sc.W, sc.b)) + (128*32+32+32*2+2)
    w, _ = match_width(tgt, 2, 2, 4)
    gd = MLP([2, w, w, w, w, 2], seed, lr=1e-3)
    gd_curve, seen_buf_X, seen_buf_Y = [], [], []
    rng = np.random.default_rng(seed); seen = 0; it = iter(CKPTS); nx = next(it)
    gd_curve.append(gd.accuracy(Xte, Yte))
    while seen < STREAM:
        Xb, Yb = gen(BATCH, rng); gd.train_step(Xb, Yb); seen += BATCH
        if len(seen_buf_X) < 2000:
            seen_buf_X.append(Xb); seen_buf_Y.append(Yb)
        if nx and seen >= nx:
            gd_curve.append(gd.accuracy(Xte, Yte)); nx = next(it, None)
    out["gd_curve"] = gd_curve
    out["gd_final"] = gd.accuracy(Xte, Yte)
    bufX = np.concatenate(seen_buf_X)[:2000]; bufY = np.concatenate(seen_buf_Y)[:2000]
    out["gd_gap"] = gd.accuracy(bufX, bufY) - gd.accuracy(Xte, Yte)   # train-on-seen - held-out
    out["gd_width"] = w; out["gd_weights"] = gd.n_weights()

    # --- rise-with-depth probe: SCFF on a 3-D 64-cluster checkerboard (per-layer probe) ---
    genhd = make_checkerboard_hd
    Hr, Yr = genhd(4000, np.random.default_rng(seed + 11))
    He, Ye = genhd(4000, np.random.default_rng(seed + 12))
    schd = SCFF([3] + DIMS[1:], THETA, LR_SCFF, seed, objective="two_sided",
                goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed); seen = 0
    while seen < STREAM:
        Xb, _ = genhd(BATCH, rng); schd.train_step(Xb, rng); seen += BATCH
    out["rise_perlayer"] = probe_acc_per_layer(schd, Hr, Yr, He, Ye)
    rphd = RandomProjStack([3] + DIMS[1:], seed)
    out["rise_random_perlayer"] = probe_acc_per_layer(rphd, Hr, Yr, He, Ye)
    return out


def main():
    t0 = time.time()
    runs = []
    for s in SEEDS:
        print(f"[exp0] seed {s} ...", flush=True)
        runs.append(run_seed(s))
    print(f"[exp0] all seeds done ({time.time()-t0:.0f}s).")

    def stack(key):
        return np.array([r[key] for r in runs])

    samples = np.array([0] + CKPTS)

    # --- persist raw arrays (every figure regenerates from these; see plot.py) ---
    saved = {k: stack(k) for k in runs[0].keys()}
    saved["samples"] = samples; saved["seeds"] = np.array(SEEDS)
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)

    # --- manifest: git hash + resolved config + medians (result-format A2) ---
    manifest = {
        "experiment": "exp0-full", "git_commit": _git_hash(), "seeds": SEEDS,
        "task": "checkerboard_2d", "check": [CHECK_GRID, CHECK_SPACING, CHECK_OVERLAP],
        "dims": DIMS, "theta": THETA, "lr_scff": LR_SCFF, "goodness": GOODNESS_MODE,
        "normalize_input": True, "taps": TAPS, "stream": STREAM, "batch": BATCH,
        "probe_C": PROBE_C, "gd_width": int(runs[0]["gd_width"]),
        "gd_weights": int(runs[0]["gd_weights"]),
        "results_median": {k: float(np.median(stack(k))) for k in
                           ["gd_final", "gd_gap", "scff_lin", "scff_mlp", "contrast_lin",
                            "contrast_mlp", "oja_lin", "oja_mlp", "rp_lin", "rp_mlp"]},
        "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # --- figures: redraw from the SAVED arrays (proves the reproducibility contract) ---
    A = np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True)
    plot.draw_all(A, OUT)

    # ---- console summary ----
    def cell(key):
        a = stack(key); return f"{np.median(a):.3f} [{np.percentile(a,25):.3f},{np.percentile(a,75):.3f}]"
    print("\n=== exp0 ablation (median [IQR], n=5) ===")
    print(f"  0c full-GD ceiling         held-out  {cell('gd_final')}  (gap {np.median(stack('gd_gap')):+.3f})")
    print(f"  0a SCFF two-sided   linear {cell('scff_lin')}   mlp {cell('scff_mlp')}")
    print(f"  0a SCFF contrast    linear {cell('contrast_lin')}   mlp {cell('contrast_mlp')}")
    print(f"  0b Oja/GHA          linear {cell('oja_lin')}   mlp {cell('oja_mlp')}")
    print(f"  0b random-proj      linear {cell('rp_lin')}   mlp {cell('rp_mlp')}")
    rise = stack("rise_perlayer"); riser = stack("rise_random_perlayer")
    print(f"  rise probe (3D 64-clust) SCFF per-layer {np.round(np.median(rise,0),3)}  "
          f"random {np.round(np.median(riser,0),3)}")
    print(f"[exp0] manifest+arrays+figures in {OUT}  "
          f"({manifest['wall_clock_s']}s, git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
