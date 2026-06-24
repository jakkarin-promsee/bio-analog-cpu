"""P4.3 decay-investigation figures: python plot_p4_3_decay.py figs_p4_3_decay
WIDEN_ACC (fix64 vs widen vs BP, per regime; x = depth+widen-width) · WIDEN_DIAG (per-layer probe/dead/erank at
deepest L, headroom) · MIXED (flat+headroom: OURS vs BP per-subset acc vs depth + per-subset per-layer probe)."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_FIX, C_WID, C_BP = "#2c6fbf", "#d9690a", "#6f6f6f"          # fix64=blue, widen=orange, BP=grey
C_FLAT, C_HEAD, C_ALL = "#1b8a3a", "#7d3cb5", "#444444"        # mixed: flat=green, head=purple, all=dark-grey
REGIMES = ["flat", "headroom"]


def _sibling_bp(OUT):
    """Load the main P4.3 sweep's tuned-BP curves (figs_p4_3/arrays.npz) for an apples-to-apples reference."""
    p = os.path.join(os.path.dirname(os.path.abspath(OUT)), "figs_p4_3", "arrays.npz")
    if not os.path.exists(p):
        return None
    s = np.load(p)
    return {"depths": s["depths"], "flat": s["flat_bp"], "headroom": s["headroom_bp"]}


def draw_all(a, OUT):
    wd = a["wid_depths"]; wx = np.arange(len(wd)); wdeep = int(a["wid_deep"])
    wbase, wstep = int(a["wbase"]), int(a["wstep"])
    widen_last = [wbase + (int(L) - 1) * wstep for L in wd]                # widen arm's deepest-layer width
    wxt = [f"L{int(L)}\nW{w}" for L, w in zip(wd, widen_last)]
    bp = _sibling_bp(OUT)

    # WIDEN_ACC: does growing width with depth stop the decay? fix64 vs widen (+ tuned-BP reference), per regime
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, rg in zip(axes, REGIMES):
        if bp is not None and len(bp[rg]) == len(wx):
            ax.plot(wx, bp[rg], color=C_BP, lw=2.0, ls="--", marker="s", ms=4, label="BP (tuned)")
        ax.plot(wx, a[f"wid_fix64_{rg}_acc"], color=C_FIX, lw=2.4, marker="s", ms=6, label=f"fix W{wbase}")
        ax.plot(wx, a[f"wid_widen_{rg}_acc"], color=C_WID, lw=2.6, marker="o", ms=6,
                label=f"widen W{wbase}+{wstep}·l")
        ax.set_xticks(wx); ax.set_xticklabels(wxt, fontsize=8)
        ax.set_xlabel("depth  (W = widen arm's deepest-layer width)")
        ax.set_ylabel("held-out accuracy (last-layer readout)")
        ax.set_title(f"[{rg}] does widening deep layers stop the decay?", fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.suptitle("P4.3 WIDEN — fixed width vs width-growing-with-depth (OURS), vs tuned BP", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "WIDEN_ACC.png"), dpi=130, facecolor="white"); plt.close(fig)

    # WIDEN_DIAG: the mechanism — per-layer probe / dead-fraction / effective-rank at the deepest depth (headroom)
    rg = "headroom"
    if f"wid_fix64_{rg}_probe" in a:
        li = np.arange(1, wdeep + 1)
        fig, (p1, p2, p3) = plt.subplots(1, 3, figsize=(15, 4.2))
        for ax, key, ylab, ttl in [
            (p1, "probe", "linear-probe accuracy", "separability (higher = better)"),
            (p2, "dead", "dead-unit fraction", "dead units (lower = better)"),
            (p3, "erank", "effective rank", "collapse (higher = richer)")]:
            ax.plot(li, a[f"wid_fix64_{rg}_{key}"], color=C_FIX, lw=2.4, marker="s", ms=5, label=f"fix W{wbase}")
            ax.plot(li, a[f"wid_widen_{rg}_{key}"], color=C_WID, lw=2.6, marker="o", ms=5, label="widen")
            ax.set_xticks(li); ax.set_xlabel("layer index (1 = first)"); ax.set_ylabel(ylab)
            ax.set_title(ttl, fontsize=9); ax.legend(fontsize=8); ax.grid(alpha=0.25)
        fig.suptitle(f"P4.3 WIDEN_DIAG — [{rg}] per-layer at L{wdeep}: is the decay dead-units / class-collapse, "
                     f"and does widening fix it?", fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "WIDEN_DIAG.png"), dpi=130, facecolor="white"); plt.close(fig)

    # MIXED: flat+headroom in one task — OURS vs tuned BP per-subset accuracy vs depth (iso-budget) + per-layer probe
    md = a["mix_depths"]; mx = np.arange(len(md)); mdeep = int(a["mix_deep"])
    mw = a["mix_widths"] if "mix_widths" in a else [0] * len(md)
    mxt = [f"L{int(L)}\nW{int(w)}" for L, w in zip(md, mw)]
    fig, (q1, q2) = plt.subplots(1, 2, figsize=(12.5, 4.5))
    for key, col, mk, lab in [("acc_all", C_ALL, "D", "overall"), ("acc_flat", C_FLAT, "o", "flat subset"),
                              ("acc_head", C_HEAD, "^", "headroom subset")]:
        q1.plot(mx, a[f"mix_{key}"], color=col, lw=2.6, marker=mk, ms=6, label=f"OURS {lab}")
    for key, col, mk, lab in [("bp_all", C_ALL, "D", "overall"), ("bp_flat", C_FLAT, "o", "flat"),
                              ("bp_head", C_HEAD, "^", "headroom")]:
        if f"mix_{key}" in a:
            q1.plot(mx, a[f"mix_{key}"], color=col, lw=1.8, ls="--", marker=mk, ms=4, alpha=0.8, label=f"BP {lab}")
    q1.set_xticks(mx); q1.set_xticklabels(mxt, fontsize=8)
    q1.set_xlabel("depth at fixed budget"); q1.set_ylabel("held-out accuracy (last-layer readout)")
    q1.set_title("flat-bad / headroom-good? (solid = OURS, dashed = BP)", fontsize=9)
    q1.legend(fontsize=7, ncol=2); q1.grid(alpha=0.25)
    if "mix_probe_flat" in a:
        li = np.arange(1, mdeep + 1)
        q2.plot(li, a["mix_probe_flat"], color=C_FLAT, lw=2.6, marker="o", ms=5, label="flat subset")
        q2.plot(li, a["mix_probe_head"], color=C_HEAD, lw=2.6, marker="^", ms=5, label="headroom subset")
        q2.set_xticks(li); q2.set_xlabel("layer index (1 = first)"); q2.set_ylabel("per-subset linear-probe acc")
        q2.set_title(f"where each subtask is solved (L{mdeep}) — does flat decay through deep layers?", fontsize=9)
        q2.legend(fontsize=8); q2.grid(alpha=0.25)
    fig.suptitle("P4.3 MIXED — half flat + half headroom in one 4-class problem (OURS vs tuned BP)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "MIXED.png"), dpi=130, facecolor="white"); plt.close(fig)
    print(f"  [plot] WIDEN_ACC/WIDEN_DIAG/MIXED -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
