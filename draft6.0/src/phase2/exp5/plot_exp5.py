"""
P2.5 figures — regenerate from arrays.npz (result-format reproducibility contract).
Emits: BLOCK (final acc vs #GD-checkpoints N, read vs write, + pure-SCFF & GD-ceiling envelopes — the
headline), F3+ (per-block all-tap probe trajectory: does the stream stay class-separable?), F7 (acc vs
backward-cost Pareto — the substrate claim).
Run:  python plot_exp5.py figs_exp5_cifar
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": True})
C_READ, C_WRITE, C_PURE, C_GD = "#c1272d", "#117a78", "#555555", "#e08214"


def _med_iqr(a):
    return np.median(a), np.percentile(a, 25), np.percentile(a, 75)


def draw_all(A, name, OUT):
    n = len(A["seeds"])
    C = int(np.median(A["C"])) if "C" in A.files else 10
    chance = 1.0 / max(C, 2)
    pure = A["acc_pure_N1"]; pm, pl, ph = _med_iqr(pure)
    gdm, gdl, gdh = _med_iqr(A["gd_held"])
    Ns = [2, 4, 8]

    # ---- BLOCK : final acc vs #GD-checkpoints, read vs write ----
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for mode, col in [("read", C_READ), ("write", C_WRITE)]:
        xs = [1] + Ns
        ys = [pm] + [np.median(A[f"acc_{mode}_N{N}"]) for N in Ns]
        lo = [pl] + [np.percentile(A[f"acc_{mode}_N{N}"], 25) for N in Ns]
        hi = [ph] + [np.percentile(A[f"acc_{mode}_N{N}"], 75) for N in Ns]
        ax.plot(xs, ys, color=col, marker="o", lw=2.2, label=f"GD-between ({mode})")
        ax.fill_between(xs, lo, hi, color=col, alpha=0.15)
    ax.axhline(gdm, color=C_GD, ls="-", lw=1.6, label=f"pure-GD ceiling {gdm:.3f}")
    ax.axhline(pm, color=C_PURE, ls="--", lw=1.4, label=f"pure-SCFF (N=1) {pm:.3f}")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 8]); ax.set_xticklabels([1, 2, 4, 8])
    ax.set_xlabel("# GD checkpoints  N  (cadence k = 8/N SCFF layers per block)")
    ax.set_ylabel("final held-out accuracy")
    best_mode = max(["read", "write"], key=lambda m: max(np.median(A[f"acc_{m}_N{N}"]) for N in Ns))
    best_acc = max(np.median(A[f"acc_{best_mode}_N{N}"]) for N in Ns)
    closed = (best_acc - pm) / (gdm - pm + 1e-9) * 100
    ax.set_title(f"BLOCK P2.5 [{name}]: does GD *between* shallow SCFF earn depth? (n={n})\n"
                 f"best = {best_mode} {best_acc:.3f} — closes {closed:.0f}% of the pure-SCFF→GD gap "
                 f"(pure deep SCFF can't, P2.1)", fontsize=8.5)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "BLOCK.png")); plt.close(fig)

    # ---- F3+ : per-block all-tap probe trajectory (deepest cadence N=8: write vs read vs the stream) ----
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    for mode, col in [("read", C_READ), ("write", C_WRITE)]:
        P = A[f"probe_{mode}_N8"]; x = np.arange(1, P.shape[1] + 1)
        m = np.median(P, 0)
        ax.plot(x, m, color=col, marker="o", label=f"{mode} per-block probe")
        ax.fill_between(x, np.percentile(P, 25, 0), np.percentile(P, 75, 0), color=col, alpha=0.15)
    ax.axhline(gdm, color=C_GD, ls="-", lw=1.2, label=f"GD ceiling {gdm:.3f}")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    ax.set_xlabel("block index (N=8, k=1 — GD after every SCFF layer)")
    ax.set_ylabel("per-block all-tap probe acc")
    ax.set_title(f"F3+ P2.5 [{name}]: per-block separability — does WRITE keep the stream class-aligned\n"
                 f"where READ's raw-SCFF stream degrades? (n={n})", fontsize=8.5)
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_perblock.png")); plt.close(fig)

    # ---- F7 : accuracy vs backward cost (the substrate Pareto) ----
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for mode, col, mk in [("read", C_READ, "o"), ("write", C_WRITE, "s")]:
        for N in Ns:
            a = A[f"acc_{mode}_N{N}"]; gw = np.median(A[f"gdw_{mode}_N{N}"])
            ax.errorbar(gw, np.median(a), yerr=[[np.median(a) - np.percentile(a, 25)],
                        [np.percentile(a, 75) - np.median(a)]], color=col, marker=mk, ms=7, capsize=3)
            ax.annotate(f"N{N}", (gw, np.median(a)), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.errorbar(np.median(A["gdw_pure_N1"]), pm, color=C_PURE, marker="D", ms=8, capsize=3, label="pure-SCFF")
    ax.axhline(gdm, color=C_GD, ls="-", lw=1.4, label=f"pure-GD ceiling {gdm:.3f}")
    gdwf = np.median(A["gd_w_full"]) if "gd_w_full" in A.files else None
    if gdwf:
        ax.annotate(f"pure-GD\n(full backward\n{int(gdwf)} w)", (gdwf, gdm), fontsize=7, color=C_GD,
                    xytext=(-10, -28), textcoords="offset points", ha="right")
    ax.plot([], [], color=C_READ, marker="o", ls="", label="read")
    ax.plot([], [], color=C_WRITE, marker="s", ls="", label="write")
    ax.set_xscale("log"); ax.set_xlabel("backward (GD) weights — the substrate cost")
    ax.set_ylabel("final held-out accuracy")
    ax.set_title(f"F7 P2.5 [{name}]: accuracy vs backward cost — how cheaply does GD-between buy depth?",
                 fontsize=8.5)
    ax.legend(fontsize=7.5, loc="best")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F7_backward.png")); plt.close(fig)
    print(f"  figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    draw_all(np.load(os.path.join(d, "arrays.npz"), allow_pickle=True),
             os.path.basename(d).replace("figs_exp5_", ""), d)
