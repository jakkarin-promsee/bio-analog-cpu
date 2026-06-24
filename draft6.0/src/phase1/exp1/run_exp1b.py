"""
Exp 1b — scale-free check: does the block-vs-GD difference (held-out + memorization gap)
hold as TOTAL WEIGHTS sweep small->large? Block and pure-GD matched at each size point.
digits (fast). Sets the default size Exp 2/3 inherit. Figures regenerate from arrays.
Run: python run_exp1b.py
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))
from scff_gate import SCFF, THETA, LR_SCFF, GOODNESS_MODE              # noqa: E402
from models_extra import MLP, match_width                             # noqa: E402
from run_exp1 import load_data, taps_feat, _git_hash                  # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
BATCH, SCFF_EP, SUP_EP = 32, 40, 50
WIDTHS = [16, 24, 32, 48, 64, 96]            # SCFF width H -> the size axis
N_TRAIN, N_TEST = 600, 600
C_BLOCK, C_GD = "#117a78", "#e08214"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": False, "savefig.facecolor": "white"})


def train_block(Xtr, Ytr, Xte, H, seed):
    sc = SCFF([Xtr.shape[1], H, H, H, H], THETA, LR_SCFF, seed,
              objective="two_sided", goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed)
    for _ in range(SCFF_EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            sc.train_step(Xtr[idx[s:s + BATCH]], rng)
    return sc


def train_mlp(dims, F, Y, seed, lr):
    m = MLP(dims, seed, lr=lr); rng = np.random.default_rng(seed)
    for _ in range(SUP_EP):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            m.train_step(F[idx[s:s + BATCH]], Y[idx[s:s + BATCH]])
    return m


def run():
    t0 = time.time()
    res = {k: np.zeros((len(WIDTHS), len(SEEDS))) for k in
           ["block_held", "block_gap", "gd_held", "gd_gap", "weights"]}
    for hi, H in enumerate(WIDTHS):
        for si, seed in enumerate(SEEDS):
            Xtr, Ytr, Xte, Yte, C = load_data("digits", N_TRAIN, N_TEST, seed)
            D = Xtr.shape[1]
            sc = train_block(Xtr, Ytr, Xte, H, seed)
            Ftr, Fte = taps_feat(sc, Xtr), taps_feat(sc, Xte)
            ro = train_mlp([Ftr.shape[1], 32, C], Ftr, Ytr, seed, 2e-3)
            block_w = sum((sc.W[i].size + sc.b[i].size) for i in range(len(sc.W))) \
                + (Ftr.shape[1] * 32 + 32 + 32 * C + C)
            w, gd_w = match_width(block_w, D, C, 4)
            gd = train_mlp([D, w, w, w, w, C], Xtr, Ytr, seed, 1e-3)
            res["block_held"][hi, si] = ro.accuracy(Fte, Yte)
            res["block_gap"][hi, si] = ro.accuracy(Ftr, Ytr) - ro.accuracy(Fte, Yte)
            res["gd_held"][hi, si] = gd.accuracy(Xte, Yte)
            res["gd_gap"][hi, si] = gd.accuracy(Xtr, Ytr) - gd.accuracy(Xte, Yte)
            res["weights"][hi, si] = block_w
        print(f"  H={H:3d} w~{int(res['weights'][hi].mean()):6d}: "
              f"block {np.median(res['block_held'][hi]):.3f} (gap {np.median(res['block_gap'][hi]):+.3f})  "
              f"GD {np.median(res['gd_held'][hi]):.3f} (gap {np.median(res['gd_gap'][hi]):+.3f})", flush=True)

    OUT = os.path.join(_HERE, "figs_exp1b_digits"); os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), widths=np.array(WIDTHS), seeds=np.array(SEEDS), **res)
    json.dump({"experiment": "exp1b-digits", "git_commit": _git_hash(), "widths": WIDTHS,
               "seeds": SEEDS, "n_train": N_TRAIN, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    _fig(res, OUT)
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}")


def _fig(res, OUT):
    wts = np.median(res["weights"], 1)
    def mi(a): return np.median(a, 1), np.percentile(a, 25, 1), np.percentile(a, 75, 1)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for key, c, lab in [("block_held", C_BLOCK, "block"), ("gd_held", C_GD, "pure-GD")]:
        m, lo, hi = mi(res[key]); ax[0].plot(wts, m, color=c, marker="o", label=lab)
        ax[0].fill_between(wts, lo, hi, color=c, alpha=0.2)
    ax[0].set_xscale("log"); ax[0].set_xlabel("total weights"); ax[0].set_ylabel("held-out acc")
    ax[0].set_title("F6 1b: held-out vs size (scale-free check)"); ax[0].legend(fontsize=8)
    for key, c, lab in [("block_gap", C_BLOCK, "block"), ("gd_gap", C_GD, "pure-GD")]:
        m, lo, hi = mi(res[key]); ax[1].plot(wts, m, color=c, marker="o", label=lab)
        ax[1].fill_between(wts, lo, hi, color=c, alpha=0.2)
    ax[1].set_xscale("log"); ax[1].set_xlabel("total weights"); ax[1].set_ylabel("memorization gap")
    ax[1].axhline(0, color="grey", ls=":", lw=1)
    ax[1].set_title("1b: memorization gap vs size"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F6_scale.png")); plt.close(fig)


if __name__ == "__main__":
    run()
