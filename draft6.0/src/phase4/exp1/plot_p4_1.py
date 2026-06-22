"""P4.1 figures: python plot_p4_1.py figs_p4_1  — RACE, GAP-CURVE, INV (ambient-dim axis, log-x).
Encoding (result-format Layer A): OURS=orange, BP=blue, Mono=purple, chance=black dotted, Bayes=green dashed."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_O, C_B, C_M = "#d9690a", "#2c6fbf", "#8a1b8a"


def draw_all(a, OUT):
    dim, bayes = a["dim"], a["bayes"]; chance = float(a["chance"])
    x = dim                                                            # axis = ambient dim (log)

    # RACE: the three racers' accuracy vs ambient dim, + chance + Bayes (flat ceiling)
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.plot(x, 1 - bayes, color="#1b8a3a", ls="--", lw=1.6, marker="^", ms=4, label="Bayes-optimal (flat)")
    ax.plot(x, a["bp"], color=C_B, lw=2.0, marker="s", ms=4, label="BP-ceiling (tuned)")
    ax.plot(x, a["ours"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS (contrast+coord)")
    ax.plot(x, a["mono"], color=C_M, lw=2.0, marker="d", ms=4, label="Mono-Forward")
    ax.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6); ax.text(x.max(), chance, " chance", fontsize=7,
                                                                      va="bottom", ha="right")
    ax.set_xscale("log"); ax.set_xlabel("ambient input dim (nuisance dims →)"); ax.set_ylabel("held-out accuracy")
    ax.set_title("P4.1 RACE — three racers vs ambient dimension", fontsize=9)
    ax.legend(fontsize=8); ax.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "RACE.png"), dpi=130); plt.close(fig)

    # GAP-CURVE: gap-to-BP vs dim (clean read here — Bayes flat), + capture
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
    a1.axhline(0, color=C_B, lw=1.2, label="BP (=0)")
    a1.plot(x, a["gap"], color=C_O, lw=2.6, marker="o", ms=4, label="OURS gap-to-BP")
    a1.plot(x, a["bp"] - a["mono"], color=C_M, lw=1.8, marker="d", ms=4, label="Mono gap-to-BP")
    a1.set_xscale("log"); a1.set_xlabel("ambient input dim (nuisance dims →)")
    a1.set_ylabel("gap to BP (acc(BP) − acc(·))  [↓ = better]")
    a1.set_title("GAP-CURVE — does the gap open as nuisance grows?", fontsize=9)
    a1.legend(fontsize=8); a1.grid(alpha=0.25, which="both")
    a2.plot(x, a["capture"], color=C_O, lw=2.6, marker="o", ms=4)
    a2.set_xscale("log"); a2.set_xlabel("ambient input dim (nuisance dims →)")
    a2.set_ylabel("Bayes-normalized capture  [1 = optimal]")
    a2.set_ylim(0, 1.05); a2.set_title("CAPTURE — fraction of the achievable OURS gets", fontsize=9)
    a2.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "GAP_CURVE.png"), dpi=130); plt.close(fig)

    # INV: apparatus + health — Bayes flat in dim (the A2 claim), cost grows, gen-gap
    fig, (p1, p2, p3) = plt.subplots(1, 3, figsize=(13.5, 3.9))
    p1.plot(x, bayes, color="#1b8a3a", lw=2.0, marker="^", ms=4)
    p1.axhline(float(np.median(bayes)), color="k", ls=":", lw=0.8, alpha=0.6)
    p1.set_xscale("log"); p1.set_ylim(max(0, float(bayes.min()) - 0.05), float(bayes.max()) + 0.05)
    p1.set_xlabel("ambient dim"); p1.set_ylabel("exact Bayes error")
    p1.set_title("INV-a · Bayes FLAT in dim? (apparatus)", fontsize=9); p1.grid(alpha=0.25, which="both")
    for bwd, col, lab in [(a["ours_bwd"], C_O, "OURS"), (a["bp_bwd"], C_B, "BP"), (a["mono_bwd"], C_M, "Mono")]:
        p2.plot(x, bwd / 1000, color=col, lw=2.0, marker="o", ms=3, label=lab)
    p2.set_xscale("log"); p2.set_yscale("log"); p2.set_xlabel("ambient dim")
    p2.set_ylabel("backward credit-assignment work (k)")
    p2.set_title("INV-b · cost grows with dim", fontsize=9); p2.legend(fontsize=8); p2.grid(alpha=0.25, which="both")
    for tr, te, col, lab in [(a["ours_tr"], a["ours"], C_O, "OURS"), (a["bp_tr"], a["bp"], C_B, "BP"),
                             (a["mono_tr"], a["mono"], C_M, "Mono")]:
        p3.plot(x, tr - te, color=col, lw=2.0, marker="o", ms=3, label=lab)
    p3.set_xscale("log"); p3.set_xlabel("ambient dim"); p3.set_ylabel("generalization gap (train − test)")
    p3.set_title("INV-c · over/under-fit per racer", fontsize=9); p3.legend(fontsize=8); p3.grid(alpha=0.25, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] RACE/GAP_CURVE/INV -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz")), sys.argv[1])
