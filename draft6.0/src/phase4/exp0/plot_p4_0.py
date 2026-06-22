"""P4.0 figures: python plot_p4_0.py figs_p4_0  — RACE, GAP-CURVE, PARETO.
Encoding (result-format Layer A): OURS=orange, BP=blue, Mono=purple, chance=black dotted, Bayes=green dashed."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B, C_M = "#d9690a", "#2c6fbf", "#8a1b8a"


def draw_all(a, OUT):
    ov, bayes = a["overlap"], a["bayes"]; chance = float(a["chance"])
    x = bayes                                                          # difficulty axis = Bayes error

    # RACE: the three racers' accuracy vs difficulty, + chance + Bayes-optimal
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.plot(x, 1 - bayes, color="#1b8a3a", ls="--", lw=1.6, marker="^", ms=4, label="Bayes-optimal")
    ax.plot(x, a["bp"], color=C_B, lw=2.0, marker="s", ms=4, label="BP-ceiling (tuned)")
    ax.plot(x, a["ours"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS (contrast+coord)")
    ax.plot(x, a["mono"], color=C_M, lw=2.0, marker="d", ms=4, label="Mono-Forward")
    ax.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6); ax.text(x.max(), chance, " chance", fontsize=7,
                                                                      va="bottom", ha="right")
    ax.set_xlabel("Bayes error (difficulty →)"); ax.set_ylabel("held-out accuracy")
    ax.set_title("P4.0 RACE — the three racers vs task difficulty", fontsize=9)
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "RACE.png"), dpi=130); plt.close(fig)

    # GAP-CURVE: gap-to-BP vs difficulty (the headline), + capture
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
    a1.axhline(0, color=C_B, lw=1.2, label="BP (=0)")
    a1.plot(x, a["gap"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS gap-to-BP")
    a1.plot(x, a["bp"] - a["mono"], color=C_M, lw=1.8, marker="d", ms=4, label="Mono gap-to-BP")
    a1.set_xlabel("Bayes error (difficulty →)"); a1.set_ylabel("gap to BP (acc(BP) − acc(·))  [↓ = better]")
    a1.set_title("GAP-CURVE — does the gap open with difficulty?", fontsize=9)
    a1.legend(fontsize=8); a1.grid(alpha=0.25)
    a2.plot(x, a["capture"], color=C_O, lw=2.6, marker="o", ms=4)
    a2.set_xlabel("Bayes error (difficulty →)"); a2.set_ylabel("Bayes-normalized capture  [1 = optimal]")
    a2.set_ylim(0, 1.05); a2.set_title("CAPTURE — fraction of the achievable OURS gets", fontsize=9)
    a2.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "GAP_CURVE.png"), dpi=130); plt.close(fig)

    # PARETO: accuracy (easiest cell) vs measured backward cost
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    i = int(np.argmin(bayes))                                          # the easiest cell, for a clean read
    for lab, acc, bwd, col in [("OURS", a["ours"][i], a["ours_bwd"][i], C_O),
                               ("BP", a["bp"][i], a["bp_bwd"][i], C_B),
                               ("Mono-Forward", a["mono"][i], a["mono_bwd"][i], C_M)]:
        ax.scatter(bwd / 1000, acc, s=90, color=col, label=f"{lab} ({acc:.2f} @ {bwd/1000:.0f}k)")
    ax.set_xlabel("backward credit-assignment work (analytic · substrate, k)  [← cheaper]")
    ax.set_ylabel("held-out accuracy (easiest cell)")
    ax.set_title("PARETO — accuracy vs backward credit-assignment work", fontsize=9)
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "PARETO.png"), dpi=130); plt.close(fig)

    # INV: apparatus + health sanity (mandatory per result-format) — Bayes monotone, cost meter, gen-gap
    fig, (p1, p2, p3) = plt.subplots(1, 3, figsize=(13.5, 3.9))
    p1.plot(ov, bayes, color="#1b8a3a", lw=2.0, marker="^", ms=4)
    p1.set_xlabel("overlap (dial)"); p1.set_ylabel("exact Bayes error")
    p1.set_title("INV-a · Bayes monotone in the dial?", fontsize=9); p1.grid(alpha=0.25)
    labs = ["OURS", "BP", "Mono"]; cols = [C_O, C_B, C_M]
    costs = [float(a["ours_bwd"][0]) / 1000, float(a["bp_bwd"][0]) / 1000, float(a["mono_bwd"][0]) / 1000]
    p2.bar(labs, costs, color=cols)
    for i, c in enumerate(costs):
        p2.text(i, c, f"{c:.0f}k", ha="center", va="bottom", fontsize=8)
    p2.set_ylabel("backward credit-assignment work (k)")
    p2.set_title("INV-b · cost-meter sanity", fontsize=9); p2.grid(alpha=0.25, axis="y")
    for tr, te, col, lab in [(a["ours_tr"], a["ours"], C_O, "OURS"), (a["bp_tr"], a["bp"], C_B, "BP"),
                             (a["mono_tr"], a["mono"], C_M, "Mono")]:
        p3.plot(x, tr - te, color=col, lw=2.0, marker="o", ms=3, label=lab)
    p3.set_xlabel("Bayes error (difficulty →)"); p3.set_ylabel("generalization gap (train − test)")
    p3.set_title("INV-c · over/under-fit per racer", fontsize=9); p3.legend(fontsize=8); p3.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] RACE/GAP_CURVE/PARETO/INV -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
