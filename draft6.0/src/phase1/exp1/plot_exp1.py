"""
Exp 1 figures, regenerated from saved arrays only.
    python plot_exp1.py <run-dir> <dataset>
Emits F1 (learning + memorization gap), F3 (separability block vs GD), F7 (backward
cost/locality), INV (SCFF dead units). numpy/matplotlib only.
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_BLOCK, C_GD = "#117a78", "#e08214"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": True})


def _mi(a, ax=0):
    return np.median(a, ax), np.percentile(a, 25, ax), np.percentile(a, 75, ax)


def draw_all(A, name, out):
    ck = A["ckpts"]; n = len(A["seeds"])

    # F1 — learning panel: held-out (solid) + train-on-seen (dashed), gap shaded, block vs GD
    bc = A["block_curve"]; gc = A["gd_curve"]              # [seed, ckpt, 2] = (train, held)
    bt, btl, bth = _mi(bc[:, :, 0]); bh, bhl, bhh = _mi(bc[:, :, 1])
    gt, gtl, gth = _mi(gc[:, :, 0]); gh, ghl, ghh = _mi(gc[:, :, 1])
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(ck, gh, color=C_GD, lw=2, label="pure-GD held-out")
    ax.plot(ck, gt, color=C_GD, lw=1.3, ls="--", label="pure-GD train")
    ax.fill_between(ck, gh, gt, color=C_GD, alpha=0.18)
    ax.plot(ck, bh, color=C_BLOCK, lw=2, label="block held-out")
    ax.plot(ck, bt, color=C_BLOCK, lw=1.3, ls="--", label="block train")
    ax.fill_between(ck, bh, bt, color=C_BLOCK, alpha=0.18)
    bgap = np.median(A["block_train"] - A["block_held"]); ggap = np.median(A["gd_train"] - A["gd_held"])
    ax.set_xscale("log"); ax.set_xlabel("supervised epochs"); ax.set_ylabel("accuracy")
    ax.set_title(f"F1 {name}: memorization gap — block {bgap:+.3f} vs GD {ggap:+.3f} (n={n})\n"
                 f"shaded = train-held gap (the memorization)")
    ax.legend(fontsize=8, loc="lower right"); fig.tight_layout()
    fig.savefig(os.path.join(out, "F1_gap.png")); plt.close(fig)

    # F3 — separability per layer: SCFF (bottom-up) vs GD hidden (top-down)
    sm, sl, sh = _mi(A["scff_perlayer"]); gm, gl, gh2 = _mi(A["gd_perlayer"])
    L = len(sm); xs = range(1, L + 1)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(xs, sm, color=C_BLOCK, marker="o", label="SCFF (unsupervised)")
    ax.fill_between(xs, sl, sh, color=C_BLOCK, alpha=0.2)
    ax.plot(xs, gm, color=C_GD, marker="s", label="pure-GD hidden")
    ax.fill_between(xs, gl, gh2, color=C_GD, alpha=0.2)
    ax.axhline(0.5, color="grey", ls=":", lw=1)
    ax.set_xticks(list(xs)); ax.set_xlabel("layer (input → output)")
    ax.set_ylabel("linear-probe accuracy")
    ax.set_title(f"F3 {name}: separability by layer (n={n})\nSCFF degrades with depth; GD stays high")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(out, "F3_separability.png")); plt.close(fig)

    # F7 — backward cost / locality
    gd_bwd = float(np.median(A["gd_bwd"]))
    blk_bp = float(np.median(A["block_backprop"])); scff_loc = float(np.median(A["scff_local"]))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["pure-GD\n(full chain)"], [gd_bwd], color=C_GD, width=0.55)
    ax.bar(["block"], [blk_bp], color=C_BLOCK, width=0.55, label="GD readout backprop (serial)")
    ax.bar(["block"], [scff_loc], bottom=[blk_bp], color=C_BLOCK, width=0.55, alpha=0.4,
           hatch="//", label="SCFF local (forward-only, dist 0)")
    ax.set_ylabel("backward FLOPs")
    ax.set_title(f"F7 {name}: backward cost — block backprop = "
                 f"{blk_bp/gd_bwd:.0%} of GD\n(GD credit dist {int(A['gd_credit_dist'][0])}, "
                 f"block dist {int(A['block_credit_dist'][0])})")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(out, "F7_backward.png")); plt.close(fig)

    # INV — SCFF dead-unit fraction per layer
    dm, dl, dh = _mi(A["scff_dead"])
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(range(1, len(dm) + 1), dm, yerr=[dm - dl, dh - dm], color=C_BLOCK, capsize=3)
    ax.set_xlabel("SCFF layer"); ax.set_ylabel("dead-unit fraction")
    ax.set_title(f"INV {name}: SCFF dead units (n={n})"); fig.tight_layout()
    fig.savefig(os.path.join(out, "INV_dead.png")); plt.close(fig)
    print(f"[plot_exp1] {name}: F1, F3, F7, INV -> {out}")


if __name__ == "__main__":
    run_dir = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else "dataset"
    A = np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True)
    draw_all(A, name, run_dir)
