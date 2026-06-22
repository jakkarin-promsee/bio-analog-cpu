"""P3.3 figures: python plot_p3_3.py figs_p3_3_digits  — the continual veto (CONT)."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL = {"gd": "#c0392b", "energy_sleep": "#888888", "contrast_sleep": "#d9690a", "contrast_nosleep": "#bbbbbb"}
LAB = {"gd": "GD-online", "energy_sleep": "energy+sleep (P1/P2)", "contrast_sleep": "contrast+coord+sleep (NEW)",
       "contrast_nosleep": "contrast no-sleep (rot)"}
CONDS = ["gd", "energy_sleep", "contrast_sleep", "contrast_nosleep"]


def draw_all(a, OUT):
    # CONT veto: trajectory + BWT/final bars + SCFF-probe stability
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 3.8))
    for c in CONDS:
        tj = a[f"{c}__traj"]; x = np.arange(1, tj.shape[1] + 1)
        ax1.plot(x, np.median(tj, 0), color=COL[c], lw=2.4 if "contrast_sleep" == c else 1.6,
                 marker="o", ms=3, label=LAB[c])
    ax1.set_xlabel("task #"); ax1.set_ylabel("all-class test acc"); ax1.set_title("continual trajectory", fontsize=9)
    ax1.legend(fontsize=7); ax1.grid(alpha=0.25)

    x = np.arange(len(CONDS))
    bwt = [np.median(a[f"{c}__bwt"]) for c in CONDS]; fin = [np.median(a[f"{c}__final"]) for c in CONDS]
    ax2.bar(x - 0.2, fin, 0.4, color=[COL[c] for c in CONDS], label="final ACC")
    ax2.bar(x + 0.2, bwt, 0.4, color=[COL[c] for c in CONDS], alpha=0.5, label="BWT")
    ax2.axhline(0, color="k", lw=0.8); ax2.set_xticks(x)
    ax2.set_xticklabels(["GD", "energy", "contrast", "c-nosleep"], fontsize=7.5)
    ax2.set_title("final ACC (solid) + BWT (faded)", fontsize=9); ax2.legend(fontsize=7.5); ax2.grid(alpha=0.25, axis="y")

    for c in ("energy_sleep", "contrast_sleep"):
        sp = a[f"{c}__scff_probe"]; x = np.arange(1, sp.shape[1] + 1)
        ax3.plot(x, np.median(sp, 0), color=COL[c], lw=2.2, marker="s", ms=3, label=LAB[c])
    ax3.set_xlabel("task #"); ax3.set_ylabel("all-class SCFF probe"); ax3.set_ylim(0, 1)
    ax3.set_title("SCFF-probe stability (flat = doesn't forget)", fontsize=9)
    ax3.legend(fontsize=7.5); ax3.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "CONT_veto.png"), dpi=130); plt.close(fig)
    print(f"  [plot] CONT_veto -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
