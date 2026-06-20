"""
Exp 1a — one block vs pure GD, on HIGH-D FINITE data (the only place the headline is real).

block   = SCFF body [D,H,H,H,H] (unsupervised, local, sum-goodness, input-norm)
          -> freeze -> Output-GD readout [(allH),32,C] (Adam, x-ent) on ALL-layer taps
pure-GD = MLP [D,w,w,w,w,C] with total weights MATCHED to the block

Measures, block vs GD, n=5 seeds: held-out + train-on-seen curves (memorization gap),
per-layer separability (SCFF bottom-up vs GD top-down), backward cost/locality.

Reuses the tested exp0 components (SCFF, MLP, match_width) via sys.path. numpy only.
Run:  python run_exp1.py digits     |     python run_exp1.py mnist
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from sklearn.linear_model import LogisticRegression

_EXP0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp0")
sys.path.insert(0, _EXP0)
from scff_gate import SCFF, THETA, LR_SCFF, GOODNESS_MODE          # noqa: E402
from models_extra import MLP, match_width                          # noqa: E402
import subprocess                                                  # noqa: E402


def _git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=os.path.dirname(os.path.abspath(__file__)),
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

SEEDS = [42, 137, 271, 314, 1729]
BATCH = 32
# Tap ALL SCFF layers (= SCFF paper's all-layer concat), NOT S3's "last n". Diagnostic
# (tap_diag.py): SCFF degrades with depth, so the last layers are the WORST; tapping all
# (or the early ones) recovers ~+0.21 held-out on MNIST. SCFF body here is 4 layers.
TAPS = 4
PROBE_C = 1.0

CFG = {  # per-dataset: input handled by loader; H, epochs, train/test sizes
    "digits": dict(H=64, scff_ep=40, sup_ep=60, n_train=600, n_test=600),
    "mnist":  dict(H=128, scff_ep=25, sup_ep=40, n_train=3000, n_test=3000),
}
SUP_CKPTS = [1, 2, 4, 8, 15, 30, 60]


# ----------------------------------------------------------------------------- data
def load_data(name, n_train, n_test, seed):
    rng = np.random.default_rng(seed)
    if name == "digits":
        from sklearn.datasets import load_digits
        d = load_digits(); X = d.data / 16.0; Y = d.target
    elif name == "mnist":
        from sklearn.datasets import fetch_openml
        d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
        X = d.data.astype(np.float64) / 255.0; Y = d.target.astype(int)
    else:
        raise ValueError(name)
    idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return X[tr], Y[tr], X[te], Y[te], int(Y.max() + 1)


# ----------------------------------------------------------------------------- helpers
def taps_feat(sc, X):
    return np.concatenate(sc.infer(X)[-TAPS:], axis=1)


def gd_hidden(gd, X):
    gd.forward(X); return gd.cache[1:]            # hidden activations (post-ReLU)


def probe_layers(reps_tr, Ytr, reps_te, Yte):
    accs = []
    for rtr, rte in zip(reps_tr, reps_te):
        clf = LogisticRegression(C=PROBE_C, max_iter=3000).fit(rtr, Ytr)
        accs.append(float(clf.score(rte, Yte)))
    return accs


def train_mlp(mlp, F, Y, rng, epochs, ckpts, Fte, Yte):
    """Train an MLP; log (train_acc, held_out_acc) at epoch ckpts."""
    curve = []
    for ep in range(1, epochs + 1):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            mlp.train_step(F[idx[s:s + BATCH]], Y[idx[s:s + BATCH]])
        if ep in ckpts:
            curve.append((mlp.accuracy(F, Y), mlp.accuracy(Fte, Yte)))
    return np.array(curve)                          # [n_ckpt, 2] = (train, held-out)


def bwd_flops(dims):                                # transpose-chain backprop FLOPs
    return sum(4 * dims[i] * dims[i + 1] for i in range(len(dims) - 1))


# ----------------------------------------------------------------------------- one seed
def run_seed(seed, name):
    c = CFG[name]; H = c["H"]
    Xtr, Ytr, Xte, Yte, C = load_data(name, c["n_train"], c["n_test"], seed)
    D = Xtr.shape[1]
    scff_dims = [D, H, H, H, H]
    readout_dims = [TAPS * H, 32, C]
    block_w = sum((scff_dims[i] + 1) * scff_dims[i + 1] for i in range(len(scff_dims) - 1)) \
        + sum((readout_dims[i] + 1) * readout_dims[i + 1] for i in range(len(readout_dims) - 1))
    w, gd_w = match_width(block_w, D, C, 4)
    gd_dims = [D, w, w, w, w, C]
    out = {"block_w": block_w, "gd_w": gd_w, "gd_width": w, "C": C, "D": D}

    # --- BLOCK: SCFF unsupervised (multi-epoch), freeze, then readout supervised ---
    sc = SCFF(scff_dims, THETA, LR_SCFF, seed, objective="two_sided", goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed)
    for _ in range(c["scff_ep"]):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            sc.train_step(Xtr[idx[s:s + BATCH]], rng)
    Ftr, Fte = taps_feat(sc, Xtr), taps_feat(sc, Xte)
    ro = MLP(readout_dims, seed, lr=2e-3)
    ck = [e for e in SUP_CKPTS if e <= c["sup_ep"]]
    out["block_curve"] = train_mlp(ro, Ftr, Ytr, np.random.default_rng(seed), c["sup_ep"], ck, Fte, Yte)
    out["block_train"], out["block_held"] = float(ro.accuracy(Ftr, Ytr)), float(ro.accuracy(Fte, Yte))
    # bare top-layer linear readout (pass-gate baseline)
    top_tr, top_te = sc.infer(Xtr)[-1], sc.infer(Xte)[-1]
    out["scff_bare_top"] = float(LogisticRegression(C=PROBE_C, max_iter=3000)
                                 .fit(top_tr, Ytr).score(top_te, Yte))

    # --- PURE GD: supervised, matched weights ---
    gd = MLP(gd_dims, seed, lr=1e-3)
    out["gd_curve"] = train_mlp(gd, Xtr, Ytr, np.random.default_rng(seed), c["sup_ep"], ck, Xte, Yte)
    out["gd_train"], out["gd_held"] = float(gd.accuracy(Xtr, Ytr)), float(gd.accuracy(Xte, Yte))

    # --- F3 separability: SCFF (bottom-up) vs GD hidden (top-down) ---
    out["scff_perlayer"] = probe_layers(sc.infer(Xtr), Ytr, sc.infer(Xte), Yte)
    out["gd_perlayer"] = probe_layers(gd_hidden(gd, Xtr), Ytr, gd_hidden(gd, Xte), Yte)
    out["scff_dead"] = sc.dead_fraction(Xte)            # INV

    # --- F7 backward cost / locality ---
    out["gd_bwd"] = bwd_flops(gd_dims)                          # full-depth transpose chain
    out["block_backprop"] = bwd_flops(readout_dims)            # the only transpose chain in the block
    out["scff_local"] = sum(4 * scff_dims[i] * scff_dims[i + 1]  # local, forward-only, distance 0
                            for i in range(len(scff_dims) - 1))
    out["gd_credit_dist"] = len(gd_dims) - 1
    out["block_credit_dist"] = len(readout_dims) - 1
    out["ckpts"] = ck
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    seeds = SEEDS if "--quick" not in sys.argv else SEEDS[:2]
    t0 = time.time()
    runs = [run_seed(s, name) for s in seeds]
    for s, r in zip(seeds, runs):
        print(f"  seed {s}: block held {r['block_held']:.3f} (gap {r['block_train']-r['block_held']:+.3f}) | "
              f"GD held {r['gd_held']:.3f} (gap {r['gd_train']-r['gd_held']:+.3f}) | "
              f"bare-top {r['scff_bare_top']:.3f}", flush=True)

    def st(k): return np.array([r[k] for r in runs])
    def cell(k): a = st(k); return f"{np.median(a):.3f} [{np.percentile(a,25):.3f},{np.percentile(a,75):.3f}]"
    block_gap = st("block_train") - st("block_held"); gd_gap = st("gd_train") - st("gd_held")
    print(f"\n=== Exp 1a [{name}] median [IQR], n={len(seeds)} ===")
    print(f"  block held-out {cell('block_held')}   gap {np.median(block_gap):+.3f} [{np.percentile(block_gap,25):+.3f},{np.percentile(block_gap,75):+.3f}]")
    print(f"  pure-GD held-out {cell('gd_held')}   gap {np.median(gd_gap):+.3f} [{np.percentile(gd_gap,25):+.3f},{np.percentile(gd_gap,75):+.3f}]")
    print(f"  SCFF bare-top readout {cell('scff_bare_top')}  (pass-gate: block > bare-top?)")
    print(f"  weights: block {runs[0]['block_w']}  pure-GD {runs[0]['gd_w']} (width {runs[0]['gd_width']})")
    print(f"  backward: GD full-chain {runs[0]['gd_bwd']:,} FLOPs (dist {runs[0]['gd_credit_dist']})  |  "
          f"block backprop {runs[0]['block_backprop']:,} (dist {runs[0]['block_credit_dist']}) + "
          f"SCFF local {runs[0]['scff_local']:,} (dist 0, fwd-only)")
    print(f"  ratio block-backprop / GD-backprop = {runs[0]['block_backprop']/runs[0]['gd_bwd']:.2%}")
    print(f"  separability SCFF {np.round(np.median(st('scff_perlayer'),0),3)}  "
          f"GD {np.round(np.median(st('gd_perlayer'),0),3)}")

    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"figs_exp1_{name}")
    os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in runs[0].keys() if k != "ckpts"}
    saved["ckpts"] = np.array(runs[0]["ckpts"]); saved["seeds"] = np.array(seeds)
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)

    manifest = {"experiment": f"exp1a-{name}", "git_commit": _git_hash(), "seeds": list(seeds),
                "dataset": name, "config": CFG[name], "taps": "all-layers", "theta": THETA,
                "lr_scff": LR_SCFF, "goodness": GOODNESS_MODE, "batch": BATCH,
                "block_weights": int(runs[0]["block_w"]), "gd_weights": int(runs[0]["gd_w"]),
                "results_median": {
                    "block_held": float(np.median(st("block_held"))),
                    "gd_held": float(np.median(st("gd_held"))),
                    "block_gap": float(np.median(block_gap)), "gd_gap": float(np.median(gd_gap)),
                    "scff_bare_top": float(np.median(st("scff_bare_top"))),
                    "backprop_ratio": float(runs[0]["block_backprop"] / runs[0]["gd_bwd"])},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    import plot_exp1
    A = np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True)
    plot_exp1.draw_all(A, name, OUT)
    print(f"  ({time.time()-t0:.0f}s) arrays+manifest+figures -> {OUT}  (git {manifest['git_commit'][:8]})")
    return name, OUT


if __name__ == "__main__":
    main()
