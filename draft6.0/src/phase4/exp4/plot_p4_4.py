"""P4.4 figures: python plot_p4_4.py figs_p4_4 — RACE, GAP-CURVE, INV (class-count axis + real anchors).
OURS=orange, BP=blue, Mono=purple, chance=black dotted, Bayes=green dashed. Real anchors = star markers."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B, C_M = "#d9690a", "#2c6fbf", "#8a1b8a"


def draw_all(a, OUT):
    C = a["n_class"]; bayes = a["bayes"]; chance = a["chance"]
    rn = [str(x) for x in a["real_names"]]; rc = a["real_nclass"]
    ro, rb, rm, rg = a["real_ours"], a["real_bp"], a["real_mono"], a["real_gap"]
    mk = {"digits": "*", "cifar": "P"}

    # RACE: accuracy vs class count, + chance + Bayes, + real anchors
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(C, 1 - bayes, color="#1b8a3a", ls="--", lw=1.5, marker="^", ms=4, label="Bayes-optimal")
    ax.plot(C, chance, color="k", ls=":", lw=1.0, marker=".", label="chance (1/C)")
    ax.plot(C, a["bp"], color=C_B, lw=2.0, marker="s", ms=4, label="BP (tuned)")
    ax.plot(C, a["ours"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS")
    ax.plot(C, a["mono"], color=C_M, lw=2.0, marker="d", ms=4, label="Mono-Forward")
    for i, nm in enumerate(rn):
        ax.scatter(rc[i], ro[i], color=C_O, marker=mk.get(nm, "*"), s=150, zorder=6, edgecolors="k", lw=0.5)
        ax.scatter(rc[i], rb[i], color=C_B, marker=mk.get(nm, "*"), s=150, zorder=6, edgecolors="k", lw=0.5)
        ax.scatter(rc[i], rm[i], color=C_M, marker=mk.get(nm, "*"), s=130, zorder=6, edgecolors="k", lw=0.5)
        ax.annotate(nm, (rc[i], ro[i]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.set_xscale("log"); ax.set_xticks(C); ax.set_xticklabels([int(c) for c in C])
    ax.set_xlabel("number of classes (log)"); ax.set_ylabel("held-out accuracy")
    ax.set_title("P4.4 RACE — three racers vs class count (stars = real flat data)", fontsize=9)
    ax.legend(fontsize=7.5, ncol=2); ax.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "RACE.png"), dpi=130); plt.close(fig)

    # GAP-CURVE: gap-to-BP vs class count + real anchors; capture
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.2))
    a1.axhline(0, color=C_B, lw=1.2, label="BP (=0)")
    a1.plot(C, a["gap"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS gap-to-BP")
    a1.plot(C, a["bp"] - a["mono"], color=C_M, lw=1.8, marker="d", ms=4, label="Mono gap-to-BP")
    for i, nm in enumerate(rn):
        a1.scatter(rc[i], rg[i], color=C_O, marker=mk.get(nm, "*"), s=150, zorder=6, edgecolors="k", lw=0.5)
        a1.annotate(nm, (rc[i], rg[i]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    a1.set_xscale("log"); a1.set_xticks(C); a1.set_xticklabels([int(c) for c in C])
    a1.set_xlabel("number of classes (log)"); a1.set_ylabel("gap to BP  [<0 = OURS wins]")
    a1.set_title("GAP-CURVE — does the gap open with class count?", fontsize=9)
    a1.legend(fontsize=8); a1.grid(alpha=0.25, which="both")
    a2.plot(C, a["capture"], color=C_O, lw=2.6, marker="o", ms=4)
    a2.set_xscale("log"); a2.set_xticks(C); a2.set_xticklabels([int(c) for c in C])
    a2.set_xlabel("number of classes (log)"); a2.set_ylabel("Bayes-normalized capture")
    a2.set_ylim(0, 1.05); a2.set_title("CAPTURE — fraction of achievable (synthetic)", fontsize=9)
    a2.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "GAP_CURVE.png"), dpi=130); plt.close(fig)

    # INV: bayes & chance vs C; gen-gap per racer
    fig, (p1, p2) = plt.subplots(1, 2, figsize=(11, 4.0))
    p1.plot(C, bayes, color="#1b8a3a", lw=2.0, marker="^", ms=4, label="Bayes error")
    p1.plot(C, chance, color="k", ls=":", lw=1.2, marker=".", label="chance 1/C")
    p1.set_xscale("log"); p1.set_xticks(C); p1.set_xticklabels([int(c) for c in C])
    p1.set_xlabel("classes"); p1.set_ylabel("rate"); p1.set_title("INV-a · Bayes & chance vs class count", fontsize=9)
    p1.legend(fontsize=8); p1.grid(alpha=0.25, which="both")
    for tr, te, col, lab in [(a["ours_tr"], a["ours"], C_O, "OURS"), (a["bp_tr"], a["bp"], C_B, "BP"),
                             (a["mono_tr"], a["mono"], C_M, "Mono")]:
        p2.plot(C, tr - te, color=col, lw=2.0, marker="o", ms=3, label=lab)
    p2.set_xscale("log"); p2.set_xticks(C); p2.set_xticklabels([int(c) for c in C])
    p2.set_xlabel("classes"); p2.set_ylabel("generalization gap (train - test)")
    p2.set_title("INV-b · over/under-fit vs class count", fontsize=9); p2.legend(fontsize=8); p2.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] RACE/GAP_CURVE/INV -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz"), allow_pickle=True), sys.argv[1])
