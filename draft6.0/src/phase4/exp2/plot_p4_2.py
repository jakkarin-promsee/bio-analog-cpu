"""P4.2 figures: python plot_p4_2.py figs_p4_2  — SLOPE (headline), MAP (depth×difficulty), DEPTH (per-layer), INV.
Depth-composition instrument = per-layer probe slope. OURS-w2=orange solid, OURS-w1=orange dashed (no-coord control),
GD-hidden=blue (ceiling)."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B = "#d9690a", "#2c6fbf"


def draw_all(a, OUT):
    ov = a["overlap"]; chance = float(a["chance"]); L = int(a["L"])
    layers = np.arange(1, L + 1)

    # SLOPE (headline): depth-slope vs difficulty, 3 curves + 0-line. Composition = slope > 0.
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.axhline(0, color="k", lw=0.9, ls="-", alpha=0.6)
    ax.plot(ov, a["gd_slope"], color=C_B, lw=2.0, marker="s", ms=5, label="GD-hidden (ceiling — headroom where >0)")
    ax.plot(ov, a["ours2_slope"], color=C_O, lw=2.6, marker="o", ms=5, label="OURS w=2 (coordination)")
    ax.plot(ov, a["ours1_slope"], color=C_O, lw=1.8, ls="--", marker="x", ms=5, label="OURS w=1 (no-coord control)")
    ax.set_xlabel("overlap (difficulty →)"); ax.set_ylabel("per-layer probe depth-slope  [>0 = depth composes]")
    ax.set_title("P4.2 SLOPE — does depth-composition generalize across difficulty?", fontsize=9)
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SLOPE.png"), dpi=130); plt.close(fig)

    # MAP (deliverable): OURS-w2 per-layer probe over (layer × difficulty)
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    M = a["ours2_prof"].T                                              # [L, n_overlap]
    im = ax.imshow(M, aspect="auto", origin="lower", cmap="viridis",
                   extent=[ov.min(), ov.max(), 0.5, L + 0.5])
    ax.set_xlabel("overlap (difficulty →)"); ax.set_ylabel("SCFF layer (depth →)")
    ax.set_title("P4.2 MAP — OURS (w2) per-layer probe accuracy", fontsize=9)
    cb = fig.colorbar(im, ax=ax); cb.set_label("linear-probe accuracy")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "MAP.png"), dpi=130); plt.close(fig)

    # DEPTH: per-layer probe vs layer at representative difficulties (easy / P3.2-winner / hard)
    pick = [0, len(ov) // 2, len(ov) - 1]
    fig, axes = plt.subplots(1, len(pick), figsize=(4.3 * len(pick), 4.0), sharey=True)
    for axi, i in zip(axes, pick):
        axi.plot(layers, a["gd_prof"][i], color=C_B, lw=2.0, marker="s", ms=4, label="GD-hidden")
        axi.plot(layers, a["ours2_prof"][i], color=C_O, lw=2.6, marker="o", ms=4, label="OURS w=2")
        axi.plot(layers, a["ours1_prof"][i], color=C_O, lw=1.8, ls="--", marker="x", ms=4, label="OURS w=1")
        axi.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6)
        axi.set_xlabel("layer (depth →)"); axi.set_title(f"overlap {ov[i]:.2f}", fontsize=9); axi.grid(alpha=0.25)
    axes[0].set_ylabel("linear-probe accuracy"); axes[0].legend(fontsize=8)
    fig.suptitle("P4.2 DEPTH — per-layer probe profiles (does it rise with depth?)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "DEPTH.png"), dpi=130); plt.close(fig)

    # INV: headroom existence (GD slope) + OURS top-layer probe vs difficulty
    fig, (p1, p2) = plt.subplots(1, 2, figsize=(11, 4.0))
    p1.axhline(0.004, color="k", ls=":", lw=0.8, alpha=0.6); p1.text(ov[0], 0.004, " headroom thresh", fontsize=7, va="bottom")
    p1.plot(ov, a["gd_slope"], color=C_B, lw=2.0, marker="s", ms=4)
    p1.set_xlabel("overlap (difficulty →)"); p1.set_ylabel("GD-hidden depth-slope")
    p1.set_title("INV-a · where does headroom exist? (GD slope>0)", fontsize=9); p1.grid(alpha=0.25)
    p2.plot(ov, a["gd_top"], color=C_B, lw=2.0, marker="s", ms=4, label="GD top-layer")
    p2.plot(ov, a["ours2_top"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS w2 top-layer")
    p2.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6)
    p2.set_xlabel("overlap (difficulty →)"); p2.set_ylabel("top-layer probe accuracy")
    p2.set_title("INV-b · top-of-stack readability vs difficulty", fontsize=9); p2.legend(fontsize=8); p2.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] SLOPE/MAP/DEPTH/INV -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
