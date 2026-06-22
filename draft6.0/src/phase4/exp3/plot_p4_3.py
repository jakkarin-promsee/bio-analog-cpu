"""P4.3 figures: python plot_p4_3.py figs_p4_3 — WIDTHxDEPTH (per regime), PARETO, INV.
OURS=orange, BP=blue. x-axis = depth at fixed budget (wide-shallow -> narrow-deep)."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B = "#d9690a", "#2c6fbf"
REGIMES = ["flat", "headroom"]


def draw_all(a, OUT):
    depths = a["depths"]; widths = a["widths"]
    xt = [f"L{int(L)}\nW{int(W)}" for L, W in zip(depths, widths)]
    x = np.arange(len(depths))

    # WIDTHxDEPTH: accuracy vs depth-at-fixed-budget, per regime (2 panels), OURS vs BP, best shape marked
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=False)
    for ax, rg in zip(axes, REGIMES):
        ours, bp = a[f"{rg}_ours"], a[f"{rg}_bp"]
        ax.plot(x, bp, color=C_B, lw=2.0, marker="s", ms=5, label="BP (tuned)")
        ax.plot(x, ours, color=C_O, lw=2.6, marker="o", ms=5, label="OURS")
        ax.scatter([np.argmax(ours)], [ours.max()], s=160, facecolors="none", edgecolors=C_O, lw=2, zorder=5)
        ax.scatter([np.argmax(bp)], [bp.max()], s=160, facecolors="none", edgecolors=C_B, lw=2, zorder=5)
        ax.set_xticks(x); ax.set_xticklabels(xt, fontsize=8)
        ax.set_xlabel("shape at fixed budget  (wide-shallow -> narrow-deep)")
        ax.set_ylabel("held-out accuracy"); ax.set_title(f"[{rg}] which shape wins?", fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.suptitle("P4.3 WIDTHxDEPTH — best Scap allocation, per regime (circle = best shape)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "WIDTHxDEPTH.png"), dpi=130); plt.close(fig)

    # PARETO: accuracy vs backward credit-assignment work across shapes, per regime
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, rg in zip(axes, REGIMES):
        for lab, acc, bwd, col, mk in [("OURS", a[f"{rg}_ours"], a[f"{rg}_ours_bwd"], C_O, "o"),
                                       ("BP", a[f"{rg}_bp"], a[f"{rg}_bp_bwd"], C_B, "s")]:
            ax.plot(bwd / 1000, acc, color=col, lw=1.2, ls="--", alpha=0.6)
            ax.scatter(bwd / 1000, acc, s=70, color=col, marker=mk, label=lab, zorder=5)
            for i, L in enumerate(depths):
                ax.annotate(f"L{int(L)}", (bwd[i] / 1000, acc[i]), fontsize=6, xytext=(3, 3),
                            textcoords="offset points")
        ax.set_xlabel("backward credit-assignment work (k)  [<- cheaper]")
        ax.set_ylabel("held-out accuracy"); ax.set_title(f"[{rg}] accuracy vs backward cost", fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.suptitle("P4.3 PARETO — at fixed weights, does paying for depth (more backward) buy accuracy?", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "PARETO.png"), dpi=130); plt.close(fig)

    # INV: iso-budget sanity (total weights ~flat) + width-vs-depth, + the gap per regime
    fig, (p1, p2) = plt.subplots(1, 2, figsize=(11, 4.0))
    p1.plot(x, widths, color="k", lw=2.0, marker="o", ms=4)
    p1.set_xticks(x); p1.set_xticklabels([f"L{int(L)}" for L in depths], fontsize=8)
    p1.set_xlabel("depth"); p1.set_ylabel("OURS bulk width (iso-budget)")
    p1.set_title("INV-a · width shrinks as depth grows (iso-budget)", fontsize=9); p1.grid(alpha=0.25)
    for rg, col in zip(REGIMES, [C_O, "#b03060"]):
        p2.plot(x, a[f"{rg}_gap"], lw=2.2, marker="o", ms=4, color=col, label=f"{rg} gap-to-BP")
    p2.axhline(0, color="k", lw=0.8, alpha=0.6)
    p2.set_xticks(x); p2.set_xticklabels([f"L{int(L)}" for L in depths], fontsize=8)
    p2.set_xlabel("shape (depth at fixed budget)"); p2.set_ylabel("gap to BP  [<0 = OURS wins]")
    p2.set_title("INV-b · gap-to-BP vs shape, per regime", fontsize=9); p2.legend(fontsize=8); p2.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] WIDTHxDEPTH/PARETO/INV -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
