"""P4.6 figures: python plot_p4_6.py figs_p4_6 — NOISE-CURVE (accuracy + retention vs weight-noise sigma).
OURS=orange, BP=blue, Mono=purple."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B, C_M = "#d9690a", "#2c6fbf", "#8a1b8a"


def draw_all(a, OUT):
    sg = a["sigmas"]
    fig, (p1, p2) = plt.subplots(1, 2, figsize=(12, 4.5))
    # accuracy vs sigma (with seed IQR bands)
    for k, col, lab in [("ours_all", C_O, "OURS"), ("bp_all", C_B, "BP (tuned)"), ("mono_all", C_M, "Mono-Forward")]:
        M = a[k]; med = np.median(M, 0); lo = np.percentile(M, 25, 0); hi = np.percentile(M, 75, 0)
        p1.plot(sg, med, color=col, lw=2.4, marker="o", ms=5, label=lab)
        p1.fill_between(sg, lo, hi, color=col, alpha=0.15)
    p1.set_xlabel("weight-noise sigma (multiplicative)"); p1.set_ylabel("held-out accuracy")
    p1.set_title("NOISE-CURVE — accuracy vs analog weight noise", fontsize=9)
    p1.legend(fontsize=8); p1.grid(alpha=0.25)
    # retention acc(sigma)/acc(0)
    for k, col, lab in [("ours_ret", C_O, "OURS"), ("bp_ret", C_B, "BP"), ("mono_ret", C_M, "Mono")]:
        p2.plot(sg, a[k], color=col, lw=2.6, marker="o", ms=5, label=lab)
    p2.axhline(1.0, color="k", lw=0.7, ls=":", alpha=0.6)
    p2.set_xlabel("weight-noise sigma"); p2.set_ylabel("retention  acc(sigma)/acc(0)")
    p2.set_title("RETENTION — graceful degradation? (flatter = more robust)", fontsize=9)
    p2.set_ylim(0, 1.05); p2.legend(fontsize=8); p2.grid(alpha=0.25)
    fig.suptitle("P4.6 — noise robustness (the substrate axis): does OURS degrade more gracefully than BP?",
                 fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "NOISE_CURVE.png"), dpi=130); plt.close(fig)
    print(f"  [plot] NOISE_CURVE -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
