"""
P2.1 figures — regenerate from arrays.npz, never a live run (result-format reproducibility contract).
Emits: F3+ (the 9-cell depth curve, heroes bold + GD/wall envelopes), SLOPE (the make-or-break bar:
depth-slope per cell, >=0 = depth helps), REPR (erank/Fisher/NCC vs depth + CKA wall-vs-hero), INV
(dead-units + goodness-gap vs depth), CONT (continual preview: does the fix forget?).

House style inherited from exp0/plot.py: median line + IQR band, fixed dpi, reference lines, transparent.
Run standalone:  python plot_exp1.py figs_exp1_cifar
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": False, "savefig.facecolor": "white"})
C_GD = "#e08214"

# each cell -> ONE colour+style forever (result-format Layer A): wall dashed grey; the two substrate
# heroes (layer-norm+linear, online-BN+linear) bold; batch-norm = GPU ref (thin blue); group dotted
# purple; none thin red. Goodness within a family: linear = solid/heavy, squared = dotted/light.
STYLE = {
    "c1_lensq":    dict(color="#555555", ls="--", lw=2.2, marker="o", band=True),
    "c2_lenlin":   dict(color="#9a9a9a", ls=":",  lw=1.3, marker=".", band=False),
    "c3_layerlin": dict(color="#2c7d2c", ls="-",  lw=2.8, marker="o", band=True),
    "c4_layersq":  dict(color="#7fbf7f", ls=":",  lw=1.3, marker=".", band=False),
    "c5_grouplin": dict(color="#7b3fbf", ls="-.", lw=1.6, marker="^", band=False),
    "c6_obnlin":   dict(color="#117a78", ls="-",  lw=2.8, marker="s", band=True),
    "c7_bbnlin":   dict(color="#1f5fbf", ls="-",  lw=1.3, marker="v", band=False),
    "c8_bbnsq":    dict(color="#6f9fd8", ls=":",  lw=1.3, marker="v", band=False),
    "c9_nonelin":  dict(color="#c1272d", ls=":",  lw=1.1, marker="x", band=False),
}
LABEL = {"c1_lensq": "len+sq (WALL)", "c2_lenlin": "len+lin", "c3_layerlin": "layer+lin (HERO)",
         "c4_layersq": "layer+sq", "c5_grouplin": "group+lin", "c6_obnlin": "onlineBN+lin (HERO)",
         "c7_bbnlin": "batchBN+lin (ref)", "c8_bbnsq": "batchBN+sq (Trifecta)", "c9_nonelin": "none+lin"}
ORDER = list(STYLE.keys())


def _slope(v):
    return float(np.polyfit(np.arange(1, len(v) + 1), v, 1)[0])


def _collapsed(A, k, chance):
    """A cell that learns nothing (flat at chance because every unit died) must NOT count as a 'pass'
    — its slope ~0 is degenerate, not depth-helps. Excludes squared-goodness-under-mean-zero death."""
    fin = float(np.median(A[f"probe_{k}"][:, -1]))
    dead = float(np.median(A[f"dead_{k}"], 0)[-1]) if f"dead_{k}" in A.files else 0.0
    return fin <= chance + 0.02 or dead >= 0.99


def _band(ax, x, A, color, label, ls="-", lw=1.5, marker="o", band=True, alpha=0.15):
    m = np.median(A, 0)
    ax.plot(x, m, color=color, ls=ls, lw=lw, marker=marker, ms=4, label=label)
    if band:
        ax.fill_between(x, np.percentile(A, 25, 0), np.percentile(A, 75, 0), color=color, alpha=alpha)
    return m


def draw_all(A, name, OUT):
    L = int(A["L"]); n = len(A["seeds"])
    keys = [k for k in ORDER if f"probe_{k}" in A.files]
    xw = np.arange(1, L + 1)
    C = int(np.median(A["C"])) if "C" in A.files else 10
    chance = 1.0 / max(C, 2)

    # ---------------------------------------------------------------- F3+ : the 9-cell depth curve
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for k in keys:
        s = STYLE[k]
        m = _band(ax, xw, A[f"probe_{k}"], s["color"], f"{LABEL[k]} ({_slope(np.median(A[f'probe_{k}'],0)):+.3f})",
                  ls=s["ls"], lw=s["lw"], marker=s["marker"], band=s["band"], alpha=0.13)
    if "gd_perlayer" in A.files:
        gd = A["gd_perlayer"]; xg = np.arange(1, gd.shape[1] + 1)
        _band(ax, xg, gd, C_GD, "pure-GD hidden (envelope)", ls="-", lw=1.6, marker="", band=True, alpha=0.10)
    if "wall_ref_probe" in A.files:
        wr = np.median(A["wall_ref_probe"], 0)
        ax.plot(xw, wr, color="#222222", ls=(0, (1, 1)), lw=1.0, alpha=0.6, label="WALL_REF (P2.0 two-sided)")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    learn = [k for k in keys if not _collapsed(A, k, chance)]                 # cells that actually learn
    best = max(learn, key=lambda k: _slope(np.median(A[f"probe_{k}"], 0))) if learn else keys[0]
    bslope = _slope(np.median(A[f"probe_{best}"], 0))
    wslope = _slope(np.median(A["probe_c1_lensq"], 0)) if "probe_c1_lensq" in A.files else float("nan")
    ax.set_xticks(list(xw)); ax.set_xlabel("layer index (depth)")
    ax.set_ylabel("linear-probe acc (frozen 2k/2k, C=1.0)")
    lo = min(chance - 0.03, min(float(np.median(A[f"probe_{k}"], 0).min()) for k in keys) - 0.03)
    ax.set_ylim(lo, 1.0)
    gate = "RISES -> gate PASSED" if bslope >= 0 else "still DECLINES -> gate FAILED (no transmission fix)"
    ax.set_title(f"F3+ P2.1 [{name}]: norm x goodness grid (contrast loss, n={n})\n"
                 f"wall slope {wslope:+.3f}/layer  ->  best LEARNING cell ({LABEL[best]}) {bslope:+.3f}/layer "
                 f"({gate})", fontsize=9)
    ax.legend(fontsize=6.8, loc="upper right" if float(np.median(A["probe_c1_lensq"][:, -1])) < 0.55 else "lower left",
              ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_grid.png")); plt.close(fig)

    # ---------------------------------------------------------------- SLOPE : the make-or-break bar
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    sl_med, sl_lo, sl_hi, cols, dead = [], [], [], [], []
    for k in keys:
        per_seed = np.array([_slope(v) for v in A[f"probe_{k}"]])
        sl_med.append(np.median(per_seed)); sl_lo.append(np.percentile(per_seed, 25))
        sl_hi.append(np.percentile(per_seed, 75)); cols.append(STYLE[k]["color"])
        dead.append(_collapsed(A, k, chance))
    order = np.argsort(sl_med)
    xs = np.arange(len(keys))
    err = [[sl_med[i] - sl_lo[i] for i in order], [sl_hi[i] - sl_med[i] for i in order]]
    ax.bar(xs, [sl_med[i] for i in order], yerr=err, capsize=4,
           color=[cols[i] for i in order], alpha=0.85,
           hatch=["xx" if dead[i] else "" for i in order])
    ax.axhline(0, color="black", lw=1)
    labs = [LABEL[keys[i]] + ("\n(COLLAPSED)" if dead[i] else "") for i in order]
    ax.set_xticks(xs); ax.set_xticklabels(labs, rotation=35, ha="right", fontsize=7.2)
    ax.set_ylabel("depth-slope (probe change / layer)")
    npass = sum(1 for i, k in enumerate(keys) if (not dead[i]) and sl_med[i] >= 0)
    nlearn = sum(1 for d in dead if not d)
    verdict = "GATE FAILED -> STOP/rethink (README s5)" if npass == 0 else f"{npass} cell(s) PASS"
    ax.set_title(f"SLOPE P2.1 [{name}]: the make-or-break — {npass}/{nlearn} LEARNING cells reach slope>=0 "
                 f"(hatched = collapsed to chance, excluded)\n{verdict}", fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "SLOPE.png")); plt.close(fig)

    # ---------------------------------------------------------------- REPR : erank/Fisher/NCC + CKA
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.7))
    for mi, (mk, ylab) in enumerate([("erank", "effective rank"), ("fisher", "Fisher tr(S_B)/tr(S_W)"),
                                     ("ncc", "NCC accuracy")]):
        for k in keys:
            if f"{mk}_{k}" not in A.files:
                continue
            s = STYLE[k]
            _band(ax[mi], xw, A[f"{mk}_{k}"], s["color"], LABEL[k], ls=s["ls"], lw=s["lw"],
                  marker=s["marker"], band=False)
        ax[mi].set_xlabel("layer"); ax[mi].set_ylabel(ylab); ax[mi].set_xticks(list(xw))
    ax[0].set_title("REPR effective rank (collapse with depth?)")
    ax[1].set_title("REPR Fisher ratio (separability margin)")
    ax[2].set_title("REPR NCC (neural collapse / clustering)")
    ax[2].legend(fontsize=6.2, ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "REPR.png")); plt.close(fig)

    if "cka_wall" in A.files and "cka_hero" in A.files:
        fig, ax = plt.subplots(1, 2, figsize=(9, 4.0))
        for j, (mk, tt) in enumerate([("cka_wall", "WALL (len+sq)"), ("cka_hero", "HERO (layer+lin)")]):
            M = np.median(A[mk], 0)
            im = ax[j].imshow(M, vmin=0, vmax=1, cmap="viridis", origin="lower")
            ax[j].set_title(f"CKA layer x layer — {tt}", fontsize=9)
            ax[j].set_xlabel("layer"); ax[j].set_ylabel("layer")
            ax[j].set_xticks(range(L)); ax[j].set_xticklabels(range(1, L + 1))
            ax[j].set_yticks(range(L)); ax[j].set_yticklabels(range(1, L + 1))
            fig.colorbar(im, ax=ax[j], fraction=0.046)
        fig.suptitle("CKA: high off-diagonal = layers redundant (homogenization)", fontsize=9)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "REPR_CKA.png")); plt.close(fig)

    # ---------------------------------------------------------------- INV : dead-units + goodness-gap
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
    for k in keys:
        s = STYLE[k]
        if f"dead_{k}" in A.files:
            _band(ax[0], xw, A[f"dead_{k}"], s["color"], LABEL[k], ls=s["ls"], lw=s["lw"], marker=s["marker"], band=False)
        if f"gap_{k}" in A.files:
            _band(ax[1], xw, A[f"gap_{k}"], s["color"], LABEL[k], ls=s["ls"], lw=s["lw"], marker=s["marker"], band=False)
    ax[0].set_xlabel("layer"); ax[0].set_ylabel("dead-unit fraction"); ax[0].set_xticks(list(xw))
    ax[0].set_title("INV dead units (squared deactivation: ~0.47 vs linear ~0.05)")
    ax[1].axhline(0, color="grey", ls=":", lw=1)
    ax[1].set_xlabel("layer"); ax[1].set_ylabel("goodness gap (G_pos - G_neg)"); ax[1].set_xticks(list(xw))
    ax[1].set_title("INV goodness separation per layer")
    ax[1].legend(fontsize=6.2, ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "INV.png")); plt.close(fig)

    # ---------------------------------------------------------------- CONT : the light continual preview
    cont_keys = [k for k in A.files if k.startswith("cont_")]
    if cont_keys:
        fig, ax = plt.subplots(figsize=(6.6, 4.2))
        tasklab = ["+0,1", "+2,3", "+4,5", "+6,7", "+8,9"]
        for ck in cont_keys:
            kk = ck[len("cont_"):]
            col = STYLE.get(kk, {"color": "#444"})["color"]
            T = A[ck]; x = np.arange(1, T.shape[1] + 1)
            m = np.median(T, 0)
            ax.plot(x, m, color=col, marker="o", label=LABEL.get(kk, kk))
            ax.fill_between(x, np.percentile(T, 25, 0), np.percentile(T, 75, 0), color=col, alpha=0.15)
        ax.set_xticks(range(1, len(tasklab) + 1)); ax.set_xticklabels(tasklab)
        ax.set_xlabel("tasks seen (class-incremental)"); ax.set_ylabel("SCFF all-class linear-probe acc")
        ax.set_title("CONT preview: does the depth-fix FORGET? (flat=safe; declining=stats rot)\n"
                     "the early veto sniff — Continual-Norm predicts BN rots, per-sample stays flat", fontsize=8.5)
        ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "CONT_preview.png")); plt.close(fig)
    print(f"  figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    draw_all(np.load(os.path.join(d, "arrays.npz"), allow_pickle=True),
             os.path.basename(d).replace("figs_exp1_", ""), d)
