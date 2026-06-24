"""
P2.2 figures — regenerate from arrays.npz (result-format reproducibility contract).
Emits: F3+ (negatives overlaid + WALL_REF & GD envelopes), SLOPE (does class-aware bend it >=0?),
REPR (erank/Fisher/NCC vs depth — does hard-neg build class structure WITH depth?), INV (dead/gap),
ABLATION (final-probe lift per negative vs random, the README s2 gate).
Run:  python plot_exp2.py figs_exp2_cifar
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": False, "savefig.facecolor": "white"})
C_GD = "#e08214"
STYLE = {  # each negative -> one colour+style forever
    "random":      dict(color="#555555", ls="--", lw=2.0, marker="o", band=True),
    "hard_oracle": dict(color="#2c7d2c", ls="-",  lw=2.8, marker="o", band=True),   # the mechanism upper-bound
    "hard_proto":  dict(color="#7fbf3f", ls="-.", lw=1.8, marker="^", band=False),  # prototype variant
    "hard_unsup":  dict(color="#117a78", ls="-",  lw=2.6, marker="s", band=True),   # the substrate version
}
LABEL = {"random": "random (P2.1 base)", "hard_oracle": "hard-oracle (diff TRUE class)",
         "hard_proto": "hard-proto (diff class mean)", "hard_unsup": "hard-unsup (diff KMeans cluster)"}
ORDER = list(STYLE.keys())


def _slope(v):
    return float(np.polyfit(np.arange(1, len(v) + 1), v, 1)[0])


def _band(ax, x, A, s, label, band=None, alpha=0.14):
    m = np.median(A, 0)
    ax.plot(x, m, color=s["color"], ls=s["ls"], lw=s["lw"], marker=s["marker"], ms=4, label=label)
    if (s["band"] if band is None else band):
        ax.fill_between(x, np.percentile(A, 25, 0), np.percentile(A, 75, 0), color=s["color"], alpha=alpha)
    return m


def draw_all(A, name, OUT):
    L = int(A["L"]); n = len(A["seeds"]); xw = np.arange(1, L + 1)
    keys = [k for k in ORDER if f"probe_{k}" in A.files]
    C = int(np.median(A["C"])) if "C" in A.files else 10
    chance = 1.0 / max(C, 2)
    purity = float(np.median(A["purity"])) if "purity" in A.files else float("nan")

    # ---- F3+ : the negatives overlaid + envelopes ----
    fig, ax = plt.subplots(figsize=(7.8, 4.9))
    for k in keys:
        _band(ax, xw, A[f"probe_{k}"], STYLE[k], f"{LABEL[k]} ({_slope(np.median(A[f'probe_{k}'],0)):+.3f})")
    if "gd_perlayer" in A.files:
        gd = A["gd_perlayer"]; xg = np.arange(1, gd.shape[1] + 1)
        m = np.median(gd, 0); ax.plot(xg, m, color=C_GD, lw=1.6, label="pure-GD hidden (envelope)")
        ax.fill_between(xg, np.percentile(gd, 25, 0), np.percentile(gd, 75, 0), color=C_GD, alpha=0.10)
    if "wall_ref_probe" in A.files:
        ax.plot(xw, np.median(A["wall_ref_probe"], 0), color="#222", ls=(0, (1, 1)), lw=1.0, alpha=0.6,
                label="WALL_REF (P2.0)")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    osl = _slope(np.median(A["probe_hard_oracle"], 0)) if "probe_hard_oracle" in A.files else float("nan")
    rsl = _slope(np.median(A["probe_random"], 0)) if "probe_random" in A.files else float("nan")
    ax.set_xticks(list(xw)); ax.set_xlabel("layer index (depth)")
    ax.set_ylabel("linear-probe acc (frozen 2k/2k, C=1.0)")
    lo = min(chance - 0.03, min(float(np.median(A[f"probe_{k}"], 0).min()) for k in keys) - 0.03)
    ax.set_ylim(lo, 1.0)
    gate = "RISES -> objective IS the lever" if osl >= 0 else "still declines"
    ax.set_title(f"F3+ P2.2 [{name}]: class-aware negatives (transmission fixed: layer-norm+linear+contrast, n={n})\n"
                 f"random slope {rsl:+.3f} -> hard-oracle {osl:+.3f}/layer ({gate}); KMeans purity {purity:.2f}",
                 fontsize=8.5)
    ax.legend(fontsize=7.2, loc="upper right" if float(np.median(A["probe_random"][:, -1])) < 0.55 else "lower left")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_negatives.png")); plt.close(fig)

    # ---- SLOPE : does any negative bend it >= 0? ----
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    sl_med = [np.median([_slope(v) for v in A[f"probe_{k}"]]) for k in keys]
    sl_lo = [np.percentile([_slope(v) for v in A[f"probe_{k}"]], 25) for k in keys]
    sl_hi = [np.percentile([_slope(v) for v in A[f"probe_{k}"]], 75) for k in keys]
    xs = np.arange(len(keys))
    err = [[sl_med[i] - sl_lo[i] for i in range(len(keys))], [sl_hi[i] - sl_med[i] for i in range(len(keys))]]
    ax.bar(xs, sl_med, yerr=err, capsize=4, color=[STYLE[k]["color"] for k in keys], alpha=0.85)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(xs); ax.set_xticklabels([LABEL[k] for k in keys], rotation=30, ha="right", fontsize=7.3)
    ax.set_ylabel("depth-slope (probe change / layer)")
    npass = sum(1 for s in sl_med if s >= 0)
    ax.set_title(f"SLOPE P2.2 [{name}]: does a class-aware objective bend the wall up? "
                 f"{npass}/{len(keys)} reach >=0\n(P2.1 transmission got 0/7 — this is the decisive test)",
                 fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SLOPE.png")); plt.close(fig)

    # ---- REPR : erank / Fisher / NCC vs depth ----
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.7))
    for mi, (mk, ylab) in enumerate([("erank", "effective rank"), ("fisher", "Fisher tr(S_B)/tr(S_W)"),
                                     ("ncc", "NCC accuracy")]):
        for k in keys:
            if f"{mk}_{k}" in A.files:
                _band(ax[mi], xw, A[f"{mk}_{k}"], STYLE[k], LABEL[k], band=False)
        ax[mi].set_xlabel("layer"); ax[mi].set_ylabel(ylab); ax[mi].set_xticks(list(xw))
    ax[0].set_title("REPR effective rank")
    ax[1].set_title("REPR Fisher (class margin — RISING with depth = the win)")
    ax[2].set_title("REPR NCC (class clustering)")
    ax[2].legend(fontsize=6.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "REPR.png")); plt.close(fig)

    # ---- INV : dead + goodness gap ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
    for k in keys:
        if f"dead_{k}" in A.files:
            _band(ax[0], xw, A[f"dead_{k}"], STYLE[k], LABEL[k], band=False)
        if f"gap_{k}" in A.files:
            _band(ax[1], xw, A[f"gap_{k}"], STYLE[k], LABEL[k], band=False)
    ax[0].set_xlabel("layer"); ax[0].set_ylabel("dead-unit fraction"); ax[0].set_xticks(list(xw))
    ax[0].set_title("INV dead units"); ax[1].axhline(0, color="grey", ls=":", lw=1)
    ax[1].set_xlabel("layer"); ax[1].set_ylabel("goodness gap (G_pos - G_neg)"); ax[1].set_xticks(list(xw))
    ax[1].set_title("INV goodness separation"); ax[1].legend(fontsize=6.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png")); plt.close(fig)

    # ---- ABLATION : final-layer probe per negative (the README s2 lift gate) ----
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    fin = [A[f"probe_{k}"][:, -1] for k in keys]
    vals = [np.median(f) for f in fin]
    err = [[np.median(f) - np.percentile(f, 25) for f in fin], [np.percentile(f, 75) - np.median(f) for f in fin]]
    ax.bar(np.arange(len(keys)), vals, yerr=err, capsize=5, color=[STYLE[k]["color"] for k in keys], alpha=0.85)
    ax.axhline(np.median(fin[0]), color="#555", ls="--", lw=1, label="random baseline")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    ax.set_xticks(np.arange(len(keys))); ax.set_xticklabels([LABEL[k] for k in keys], rotation=30, ha="right", fontsize=7.3)
    ax.set_ylabel("final-layer probe acc"); ax.set_ylim(chance - 0.04, max(vals) + 0.06)
    ax.set_title(f"ABLATION P2.2 [{name}]: final-probe lift vs random (the README §2 gate)", fontsize=9)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.005, f"{v:.3f}", ha="center", fontsize=8.5)
    ax.legend(fontsize=7.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "ABLATION.png")); plt.close(fig)
    print(f"  figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    draw_all(np.load(os.path.join(d, "arrays.npz"), allow_pickle=True),
             os.path.basename(d).replace("figs_exp2_", ""), d)
