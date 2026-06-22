"""P3.1 figures: python plot_p3_1.py figs_p3_1_cifar
Coordination window on the contrastive cell — w1 (=P3.0 baseline) vs w2,w4 (coordination)."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_GD, C_RD, C_EN = "#2c6fbf", "#bbbbbb", "#888888"
C_WIN = {1: "#d9690a", 2: "#1b8a3a", 4: "#8a1b8a"}     # w1 orange (=P3.0 contrast), w2 green, w4 purple


def _band(ax, y, color, label, ls="-", lw=2.0, marker=None):
    x = np.arange(1, y.shape[1] + 1)
    ax.fill_between(x, np.percentile(y, 25, 0), np.percentile(y, 75, 0), color=color, alpha=0.15)
    ax.plot(x, np.median(y, 0), color=color, ls=ls, lw=lw, marker=marker, ms=4, label=label)
    return np.median(y, 0)


def _slope(p):
    return float(np.polyfit(np.arange(1, len(p) + 1), p, 1)[0])


def draw_all(a, name, OUT):
    chance = float(a["chance"]); wins = [int(w) for w in a["windows"]]

    # F3+ depth curve: windows overlaid + references
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    _band(ax, a["gd_perlayer"], C_GD, "GD-hidden (ceiling)", lw=1.4)
    _band(ax, a["rand_probe"], C_RD, "random floor", ls=":", lw=1.4)
    _band(ax, a["energy_probe"], C_EN, "energy-wall", ls="--", lw=1.4)
    subs = []
    for w in wins:
        p = _band(ax, a[f"ct_w{w}"], C_WIN.get(w, "#444"),
                  f"contrast w={w}" + (" (=P3.0)" if w == 1 else ""), lw=2.6 if w > 1 else 1.8)
        subs.append(f"w{w} {_slope(p):+.4f}")
    ax.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6)
    ax.set_xlabel("layer index"); ax.set_ylabel("linear-probe accuracy")
    ax.set_title(f"P3.1 [{name}] cross-layer coordination window on contrast\nslope/layer: " + " | ".join(subs),
                 fontsize=8.5)
    ax.legend(fontsize=7.5, loc="best"); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_depth.png"), dpi=130); plt.close(fig)

    # SLOPE bar: slope vs window (the make-or-break read)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    sl = [_slope(np.median(a[f"ct_w{w}"], 0)) for w in wins]
    ax.bar([str(w) for w in wins], sl, color=[C_WIN.get(w, "#444") for w in wins])
    ax.axhline(0, color="k", lw=0.9)
    ax.axhline(_slope(np.median(a["energy_probe"], 0)), color=C_EN, ls="--", lw=1, label="energy wall")
    ax.set_xlabel("coordination window w"); ax.set_ylabel("depth-slope (≥0 = depth helps)")
    ax.set_title("SLOPE vs coordination window — does sharing gradient across layers fix the decline?",
                 fontsize=8)
    ax.legend(fontsize=8); ax.grid(alpha=0.25, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SLOPE.png"), dpi=130); plt.close(fig)

    # SELECT: selectivity per layer, per window
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    for w in wins:
        _band(ax, a[f"sel_w{w}"], C_WIN.get(w, "#444"), f"w={w}", lw=2.4 if w > 1 else 1.6)
    ax.axhline(0, color="k", lw=0.8, ls="--")
    ax.set_xlabel("layer index"); ax.set_ylabel("Δ probe vs random")
    ax.set_title("SELECT — class info above random, per coordination window (>0 = real)", fontsize=8.5)
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SELECT.png"), dpi=130); plt.close(fig)
    print(f"  [plot] figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]; nm = "cifar" if "cifar" in d else "synth"
    draw_all(np.load(os.path.join(d, "arrays.npz")), nm, d)
