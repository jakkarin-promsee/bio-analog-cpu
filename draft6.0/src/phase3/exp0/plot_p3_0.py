"""P3.0 figures — regenerate from saved arrays, no retrain:  python plot_p3_0.py figs_p3_0_cifar
Encoding (result-format Layer A): energy-wall = dashed grey (baseline), masked-recon = bold green,
contrast = bold orange (the discriminative hero), GD-hidden = thin blue (ceiling), random = dotted grey."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_EN, C_RC, C_GD, C_RD, C_CT = "#888888", "#1b8a3a", "#2c6fbf", "#bbbbbb", "#d9690a"


def _band(ax, y, color, label, ls="-", lw=2.0, marker=None):
    L = y.shape[1]; x = np.arange(1, L + 1)
    med = np.median(y, 0); lo = np.percentile(y, 25, 0); hi = np.percentile(y, 75, 0)
    ax.fill_between(x, lo, hi, color=color, alpha=0.15)
    ax.plot(x, med, color=color, ls=ls, lw=lw, marker=marker, ms=4, label=label)
    return med


def _sc(p, chance):
    L = len(p); layers = np.arange(1, L + 1); pk = int(np.argmax(p))
    slope = float(np.polyfit(layers, p, 1)[0])
    tail = float(p[-max(1, L // 4):].mean() / (p[pk] + 1e-12))
    decline = float(np.clip(p[pk] - p[pk:], 0, None).sum() / L)
    return slope, decline, tail


def draw_all(a, name, OUT):
    en, rc = a["energy_probe"], a["recon_probe"]
    gd, rd = a["gd_perlayer"], a["rand_probe"]
    has_ct = "contrast_probe" in a.files
    ct = a["contrast_probe"] if has_ct else None
    chance = float(a["chance"]); L = int(a["L"])

    # --- F3+ depth curve ---
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    _band(ax, gd, C_GD, "GD-hidden (ceiling)", ls="-", lw=1.4)
    _band(ax, rd, C_RD, "random floor", ls=":", lw=1.4)
    men = _band(ax, en, C_EN, "energy-wall (P2.1 baseline)", ls="--", lw=1.8)
    mrc = _band(ax, rc, C_RC, "masked-recon", ls="-", lw=2.0)
    s_en, d_en, t_en = _sc(men, chance); s_rc, d_rc, t_rc = _sc(mrc, chance)
    sub = (f"energy {s_en:+.4f} | recon {s_rc:+.4f}")
    if has_ct:
        mct = _band(ax, ct, C_CT, "contrast (CLAPP hero)", ls="-", lw=2.8)
        s_ct, d_ct, t_ct = _sc(mct, chance); sub += f" | contrast {s_ct:+.4f} (tail {t_ct:.2f})"
    ax.axhline(chance, color="k", lw=0.7, ls=":", alpha=0.6)
    ax.text(L, chance, " chance", va="bottom", ha="right", fontsize=7, color="k")
    ax.set_xlabel("layer index"); ax.set_ylabel("linear-probe accuracy")
    ax.set_title(f"P3.0 [{name}] objective swap — energy vs preservation vs contrast\nslope/layer: {sub}",
                 fontsize=8.5)
    ax.legend(fontsize=7.5, loc="best"); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_depth.png"), dpi=130); plt.close(fig)

    # --- SCORECARD (shape metrics) ---
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    mets = ["slope×10", "decline", "1−tail_ret"]
    cells = [("energy", men, C_EN), ("masked-recon", mrc, C_RC)]
    if has_ct:
        cells.append(("contrast", mct, C_CT))
    x = np.arange(len(mets)); ww = 0.8 / len(cells)
    for i, (lab, p, col) in enumerate(cells):
        s, d, t = _sc(p, chance)
        ax.bar(x + (i - (len(cells) - 1) / 2) * ww, [s * 10, d, 1 - t], ww, color=col, label=lab)
    ax.axhline(0, color="k", lw=0.7); ax.set_xticks(x); ax.set_xticklabels(mets, fontsize=8)
    ax.set_title("SCORECARD — depth shape (lower decline / 1−tail healthier; slope↑ = depth helps)", fontsize=8)
    ax.legend(fontsize=8); ax.grid(alpha=0.25, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SCORECARD.png"), dpi=130); plt.close(fig)

    # --- INFOPRESERVE (recon error vs depth) ---
    if "recon_err" in a.files:
        fig, ax = plt.subplots(figsize=(6, 3.6))
        _band(ax, a["recon_err"], C_RC, "masked-recon reconstruction error", lw=2.2, marker="o")
        ax.set_xlabel("layer index"); ax.set_ylabel("mean recon MSE (per dim)")
        ax.set_title("INFOPRESERVE — is information kept with depth? (flat/low = preserved)", fontsize=8.5)
        ax.grid(alpha=0.25); fig.tight_layout()
        fig.savefig(os.path.join(OUT, "INFOPRESERVE.png"), dpi=130); plt.close(fig)

    # --- SELECT (selectivity per layer: recon vs contrast) ---
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    _band(ax, a["select"], C_RC, "masked-recon − random", lw=2.0, marker="o")
    if "select_ct" in a.files:
        _band(ax, a["select_ct"], C_CT, "contrast − random", lw=2.6, marker="s")
    ax.axhline(0, color="k", lw=0.8, ls="--")
    ax.set_xlabel("layer index"); ax.set_ylabel("Δ probe accuracy vs random")
    ax.set_title("SELECT — does TRAINING add CLASS-readable info above random? (>0 = real)", fontsize=8.5)
    ax.legend(fontsize=8); ax.grid(alpha=0.25); fig.tight_layout()
    fig.savefig(os.path.join(OUT, "SELECT.png"), dpi=130); plt.close(fig)

    # --- REPR/INV (dead + erank) ---
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
    _band(a1, a["energy_dead"], C_EN, "energy", ls="--"); _band(a1, a["recon_dead"], C_RC, "recon")
    if "contrast_dead" in a.files:
        _band(a1, a["contrast_dead"], C_CT, "contrast")
    a1.set_xlabel("layer"); a1.set_ylabel("dead-unit fraction"); a1.set_title("INV — dead units", fontsize=8.5)
    a1.legend(fontsize=8); a1.grid(alpha=0.25)
    _band(a2, a["energy_erank"], C_EN, "energy", ls="--"); _band(a2, a["recon_erank"], C_RC, "recon")
    if "contrast_erank" in a.files:
        _band(a2, a["contrast_erank"], C_CT, "contrast")
    a2.set_xlabel("layer"); a2.set_ylabel("effective rank"); a2.set_title("REPR — effective rank", fontsize=8.5)
    a2.legend(fontsize=8); a2.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "REPR_INV.png"), dpi=130); plt.close(fig)
    print(f"  [plot] figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    nm = "cifar" if "cifar" in d else "synth"
    draw_all(np.load(os.path.join(d, "arrays.npz")), nm, d)
