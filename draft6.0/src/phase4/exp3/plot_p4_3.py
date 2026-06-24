"""P4.3 figures: python plot_p4_3.py figs_p4_3 — WIDTHxDEPTH, PARETO, INV, WALL (per regime).
OURS=orange, OLD(energy-Sh2)=grey, BP=blue. x-axis = depth at fixed budget (wide-shallow -> narrow-deep).
Headline accuracy = the LAST-LAYER readout (the realistic GD-head position); WALL = the per-layer linear-probe
decay that all-tap would hide."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B, C_E = "#d9690a", "#2c6fbf", "#6f6f6f"
REGIMES = ["flat", "headroom"]


def draw_all(a, OUT):
    depths = a["depths"]; widths = a["widths"]
    xt = [f"L{int(L)}\nW{int(W)}" for L, W in zip(depths, widths)]
    x = np.arange(len(depths))
    has_old = "flat_energy" in a

    # WIDTHxDEPTH: held-out accuracy (last-layer readout) vs depth-at-fixed-budget, per regime, 3 racers
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=False)
    for ax, rg in zip(axes, REGIMES):
        ours, bp = a[f"{rg}_ours"], a[f"{rg}_bp"]
        ax.plot(x, bp, color=C_B, lw=2.0, marker="s", ms=5, label="BP (tuned)")
        if has_old:
            ax.plot(x, a[f"{rg}_energy"], color=C_E, lw=2.0, marker="^", ms=5, ls="--",
                    label=r"OLD (energy $\Sigma h^2$)")
        ax.plot(x, ours, color=C_O, lw=2.6, marker="o", ms=5, label="OURS (contrast)")
        ax.scatter([np.argmax(ours)], [ours.max()], s=160, facecolors="none", edgecolors=C_O, lw=2, zorder=5)
        ax.scatter([np.argmax(bp)], [bp.max()], s=160, facecolors="none", edgecolors=C_B, lw=2, zorder=5)
        ax.set_xticks(x); ax.set_xticklabels(xt, fontsize=8)
        ax.set_xlabel("shape at fixed budget  (wide-shallow -> narrow-deep)")
        ax.set_ylabel("held-out accuracy (last-layer readout)"); ax.set_title(f"[{rg}] which shape wins?", fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.suptitle("P4.3 WIDTHxDEPTH — best Scap allocation, per regime (circle = best shape)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "WIDTHxDEPTH.png"), dpi=130, facecolor="white"); plt.close(fig)

    # PARETO: accuracy vs backward credit-assignment work across shapes, per regime
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, rg in zip(axes, REGIMES):
        racers = [("OURS", a[f"{rg}_ours"], a[f"{rg}_ours_bwd"], C_O, "o")]
        if has_old:
            racers.append((r"OLD ($\Sigma h^2$)", a[f"{rg}_energy"], a[f"{rg}_energy_bwd"], C_E, "^"))
        racers.append(("BP", a[f"{rg}_bp"], a[f"{rg}_bp_bwd"], C_B, "s"))
        for lab, acc, bwd, col, mk in racers:
            ax.plot(bwd / 1000, acc, color=col, lw=1.2, ls="--", alpha=0.6)
            ax.scatter(bwd / 1000, acc, s=70, color=col, marker=mk, label=lab, zorder=5)
            for i, L in enumerate(depths):
                ax.annotate(f"L{int(L)}", (bwd[i] / 1000, acc[i]), fontsize=6, xytext=(3, 3),
                            textcoords="offset points")
        ax.set_xlabel("backward credit-assignment work (k)  [<- cheaper]")
        ax.set_ylabel("held-out accuracy"); ax.set_title(f"[{rg}] accuracy vs backward cost", fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.suptitle("P4.3 PARETO — at fixed weights, does paying for depth (more backward) buy accuracy?", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "PARETO.png"), dpi=130, facecolor="white"); plt.close(fig)

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
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130, facecolor="white"); plt.close(fig)

    # WALL: the depth-wall the all-tap readout hid. (a,b) last-layer linear probe vs depth, per regime;
    # (c) per-layer probe profile at the deepest shape (the within-stack decay). OURS holds, OLD droops.
    if has_old:
        fig, (pa, pb, pc) = plt.subplots(1, 3, figsize=(15, 4.2))
        for ax, rg in zip((pa, pb), REGIMES):
            ax.plot(x, a[f"{rg}_ours_probe_last"], color=C_O, lw=2.6, marker="o", ms=5, label="OURS (contrast)")
            ax.plot(x, a[f"{rg}_energy_probe_last"], color=C_E, lw=2.2, marker="^", ms=5, ls="--",
                    label=r"OLD (energy $\Sigma h^2$)")
            ax.set_xticks(x); ax.set_xticklabels([f"L{int(L)}" for L in depths], fontsize=8)
            ax.set_xlabel("depth at fixed budget"); ax.set_ylabel("last-layer linear-probe accuracy")
            ax.set_title(f"[{rg}] the readout's view vs depth", fontsize=9); ax.legend(fontsize=8); ax.grid(alpha=0.25)
        deep_L = int(a["deep_L"]); li = np.arange(1, deep_L + 1)
        if "headroom_ours_profile" in a:
            pc.plot(li, a["headroom_ours_profile"], color=C_O, lw=2.6, marker="o", ms=5, label="OURS (contrast)")
            pc.plot(li, a["headroom_energy_profile"], color=C_E, lw=2.2, marker="^", ms=5, ls="--",
                    label=r"OLD (energy $\Sigma h^2$)")
        pc.set_xticks(li); pc.set_xlabel("layer index (1 = first)"); pc.set_ylabel("linear-probe accuracy")
        pc.set_title(f"[headroom] per-layer decay at L{deep_L}", fontsize=9); pc.legend(fontsize=8); pc.grid(alpha=0.25)
        fig.suptitle("P4.3 WALL — energy goodness rots the deep representation the readout reads; contrast holds",
                     fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "WALL.png"), dpi=130, facecolor="white"); plt.close(fig)

    # CONTROL: fixed-width depth sweep (width held constant) — separates depth-decay from the iso width-shrink.
    # (a,b) last-layer accuracy vs depth at constant W, per regime; (c) per-layer profile at the deepest control L.
    if "ctrl_flat_ours" in a:
        cd = a["ctrl_depths"]; cw = int(a["ctrl_w"]); cx = np.arange(len(cd))
        fig, (qa, qb, qc) = plt.subplots(1, 3, figsize=(15, 4.2))
        for ax, rg in zip((qa, qb), REGIMES):
            ax.plot(cx, a[f"ctrl_{rg}_ours"], color=C_O, lw=2.6, marker="o", ms=5, label="OURS (contrast)")
            ax.plot(cx, a[f"ctrl_{rg}_energy"], color=C_E, lw=2.2, marker="^", ms=5, ls="--",
                    label=r"OLD (energy $\Sigma h^2$)")
            ax.set_xticks(cx); ax.set_xticklabels([f"L{int(L)}" for L in cd], fontsize=8)
            ax.set_xlabel(f"depth at FIXED width W{cw}"); ax.set_ylabel("held-out accuracy (last-layer readout)")
            ax.set_title(f"[{rg}] droop here = decay, not width", fontsize=9); ax.legend(fontsize=8); ax.grid(alpha=0.25)
        cdl = int(a["ctrl_deep_L"]); li = np.arange(1, cdl + 1)
        if "ctrl_headroom_ours_profile" in a:
            qc.plot(li, a["ctrl_headroom_ours_profile"], color=C_O, lw=2.6, marker="o", ms=5, label="OURS (contrast)")
            qc.plot(li, a["ctrl_headroom_energy_profile"], color=C_E, lw=2.2, marker="^", ms=5, ls="--",
                    label=r"OLD (energy $\Sigma h^2$)")
        qc.set_xticks(li); qc.set_xlabel("layer index (1 = first)"); qc.set_ylabel("linear-probe accuracy")
        qc.set_title(f"[headroom] per-layer profile at L{cdl}, W{cw}", fontsize=9); qc.legend(fontsize=8); qc.grid(alpha=0.25)
        fig.suptitle(f"P4.3 CONTROL — fixed width W{cw}: does depth still droop when width is held constant?",
                     fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "CONTROL.png"), dpi=130, facecolor="white"); plt.close(fig)
    print(f"  [plot] WIDTHxDEPTH/PARETO/INV/WALL/CONTROL -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
