"""
exp0 figures — regenerated from saved arrays ONLY (result-format Layer A2 contract).

    python plot.py <run-dir>      # redraws every figure from <run-dir>/arrays.npz

No training happens here: F4's histogram and F5's boundary read arrays saved by run_exp0
(gp_top/gn_top, bz). The F5 scatter is the *task* (deterministic from the saved seed), so
it is regenerated from the seed, not retrained. This is what makes a result citable later.
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scff_gate import make_checkerboard, DIMS, THETA

C_SCFF, C_GD, C_RP = "#117a78", "#e08214", "#999999"
C_POS, C_NEG = "#1f5fbf", "#c1272d"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": True})


def _mi(a, ax=0):
    return np.median(a, ax), np.percentile(a, 25, ax), np.percentile(a, 75, ax)


def draw_all(A, out):
    L = len(DIMS) - 1
    samples = A["samples"]; x = np.clip(samples, 1, None)
    seeds = A["seeds"]

    # F1 — held-out learning panel: SCFF (linear probe) vs full-GD ceiling, IQR bands
    sm, slo, shi = _mi(A["scff_curve"]); gm, glo, ghi = _mi(A["gd_curve"])
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(x, gm, color=C_GD, lw=2, label="full-GD (ceiling)")
    ax.fill_between(x, glo, ghi, color=C_GD, alpha=0.2)
    ax.plot(x, sm, color=C_SCFF, lw=2, label="SCFF + linear probe")
    ax.fill_between(x, slo, shi, color=C_SCFF, alpha=0.2)
    ax.axhline(0.5, color="grey", ls="--", lw=1, label="chance")
    ax.set_xscale("log"); ax.set_ylim(0.45, 1.0)
    ax.set_xlabel("samples seen"); ax.set_ylabel("held-out accuracy")
    ax.set_title(f"F1 held-out: SCFF vs full-GD ceiling (n={len(seeds)}, checkerboard)")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(out, "F1_learning.png")); plt.close(fig)

    # F4 — goodness gap per layer (median) + top-layer histogram (seed 0 = 42)
    gap = np.median(A["gpos"] - A["gneg"], 0)            # [ckpt, layer]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for l in range(L):
        ax[0].plot(x, gap[:, l], color=C_SCFF, alpha=0.35 + 0.65 * l / L,
                   marker="o", ms=3, label=f"L{l+1}")
    ax[0].axhline(0, color="grey", ls=":", lw=1); ax[0].set_xscale("log")
    ax[0].set_xlabel("samples seen"); ax[0].set_ylabel(f"goodness gap G_pos-G_neg (median n={len(seeds)})")
    ax[0].set_title("F4 goodness separation per layer"); ax[0].legend(fontsize=7, title="layer")
    gp_s, gn_s = A["gp_top"][0], A["gn_top"][0]
    bins = np.linspace(min(gp_s.min(), gn_s.min()), max(gp_s.max(), gn_s.max()), 40)
    ax[1].hist(gp_s, bins=bins, color=C_POS, alpha=0.6, label=f"G_pos ({gp_s.mean():.2f})")
    ax[1].hist(gn_s, bins=bins, color=C_NEG, alpha=0.6, label=f"G_neg ({gn_s.mean():.2f})")
    ax[1].axvline(THETA, color="grey", ls=":", lw=1, label="theta")
    ax[1].set_xlabel("top-layer goodness (sum h^2)"); ax[1].set_ylabel("count")
    ax[1].set_title(f"F4 top-layer goodness histogram (seed {seeds[0]})"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, "F4_goodness.png")); plt.close(fig)

    # F3 — separability heatmap (median probe)
    pl = np.median(A["perlayer"], 0)                     # [ckpt, layer]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    im = ax.imshow(pl.T, aspect="auto", origin="lower", cmap="viridis", vmin=0.5, vmax=1.0)
    ax.set_xticks(range(len(samples))); ax.set_xticklabels(samples, rotation=45, fontsize=7)
    ax.set_yticks(range(L)); ax.set_yticklabels([f"L{l+1}" for l in range(L)])
    ax.set_xlabel("samples seen"); ax.set_ylabel("SCFF layer")
    ax.set_title(f"F3 separability (linear-probe acc, median n={len(seeds)})")
    fig.colorbar(im, ax=ax, label="probe acc"); fig.tight_layout()
    fig.savefig(os.path.join(out, "F3_separability.png")); plt.close(fig)

    # F5 — boundary (seed 0); Z saved, scatter regenerated from the deterministic seed
    bz = A["bz"][0]; lim = float(A["blim"][0]); bacc = float(A["bacc"][0])
    xs = np.linspace(-lim, lim, 300); XX, YY = np.meshgrid(xs, xs)
    Xte, Yte = make_checkerboard(2000, np.random.default_rng(int(seeds[0]) + 2))
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.contourf(XX, YY, bz, levels=[-0.5, 0.5, 1.5], colors=[C_POS, C_NEG], alpha=0.25)
    ax.scatter(Xte[Yte == 0, 0], Xte[Yte == 0, 1], s=4, color=C_POS)
    ax.scatter(Xte[Yte == 1, 0], Xte[Yte == 1, 1], s=4, color=C_NEG)
    ax.set_title(f"F5 boundary — SCFF tapped readout (acc {bacc:.3f})")
    ax.set_aspect("equal"); fig.tight_layout()
    fig.savefig(os.path.join(out, "F5_boundary.png")); plt.close(fig)

    # INV — dead-unit fraction (median) + rise-with-depth probe
    dead = np.median(A["dead"], 0)
    rise = np.median(A["rise_perlayer"], 0); riser = np.median(A["rise_random_perlayer"], 0)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
    for l in range(L):
        ax[0].plot(x, dead[:, l], marker="o", ms=3, label=f"L{l+1}")
    ax[0].set_xscale("log"); ax[0].set_xlabel("samples seen"); ax[0].set_ylabel("dead-unit fraction")
    ax[0].set_title(f"INV dead units (median n={len(seeds)})"); ax[0].legend(fontsize=7)
    ax[1].plot(range(1, L + 1), rise, color=C_SCFF, marker="o", label="SCFF")
    ax[1].plot(range(1, L + 1), riser, color=C_RP, marker="s", ls="--", label="random-proj")
    ax[1].set_xlabel("SCFF layer"); ax[1].set_ylabel("linear-probe acc")
    ax[1].set_title("rise-probe: 3-D 64-cluster checkerboard"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, "INV_and_rise.png")); plt.close(fig)
    print(f"[plot] redrew F1, F3, F4, F5, INV+rise -> {out}")


if __name__ == "__main__":
    run_dir = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs_exp0")
    A = np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True)
    draw_all(A, run_dir)
