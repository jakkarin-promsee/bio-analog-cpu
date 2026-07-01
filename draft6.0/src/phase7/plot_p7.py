"""
plot_p7 — the ONE plotting module for Phase 7 (result-format.md §A/§C). One function per figure code; the look lives
ONLY in STYLE. `regen(run_dir)` redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable
path (a figure you can't regen from saved data is a screenshot, not a result). No rung styles matplotlib inline.

Head-family colour encoding (result-format §A): orange=cosine (the spine candidate); grey=linear floor; blue=NCM
(solid)/SLDA(dashed); magenta=FeCAM (max-magnitude); teal=RanPAC(solid)/RLS(dashed)/GKEAL(dotted); purple=MLP;
green=race_bp (STATIC ceiling — static/AAA panels ONLY); black=random-projection control (dotted taps / dash-dot pixels).
Frontier plots order heads by MEASURED spine-cleanliness among accuracy-competitive heads; sub-floor heads greyed.
"""
from __future__ import annotations
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

STYLE = dict(
    dpi=300, figsize_single=(6.0, 4.0), figsize_wide=(7.5, 4.0), figsize_strip=(10, 2.2),
    font="DejaVu Sans", base=10, band_alpha=0.18, lw=1.8, grid="#d9d9d9",
)
# head -> (colour, linestyle, marker, role)
HEADSTYLE = {
    "cosine-ncm":     ("#d9690a", "-", "o"), "cosine-softmax": ("#d9690a", "--", "o"),
    "cosine":         ("#d9690a", "-", "o"),
    "linear":         ("#7f7f7f", "-", None), "linear-softmax": ("#7f7f7f", "-", None),
    "ncm":            ("#2c6fbf", "-", "s"), "slda": ("#2c6fbf", "--", "s"),
    "fecam":          ("#8a1b8a", "-", "D"),
    "ranpac":         ("#0b8f6a", "-", "^"), "rls": ("#0b8f6a", "--", "^"), "gkeal": ("#0b8f6a", ":", "P"),
    "mlp":            ("#9467bd", "-", None), "race_bp": ("#2ca02c", "--", None),
    "randproj_taps":  ("#111111", ":", None), "randproj_pixels": ("#111111", "-.", None),
    "chance":         ("#111111", ":", None),
}
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["base"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"],
                     "axes.grid": True, "grid.color": STYLE["grid"], "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none",
                     "savefig.transparent": True})


def _hs(name):
    return HEADSTYLE.get(name, ("#555555", "-", None))


def _keys(d):
    return d.files if hasattr(d, "files") else list(d)


def _has(d, *ks):
    K = _keys(d)
    return all(k in K for k in ks)


def _heads(d):
    return [h.decode() if isinstance(h, bytes) else str(h) for h in d["heads"]] if "heads" in _keys(d) else []


def _med_iqr(M):
    M = np.atleast_2d(M).astype(float)
    return np.median(M, 0), np.percentile(M, 25, 0), np.percentile(M, 75, 0)


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    fig.tight_layout(); fig.savefig(p); plt.close(fig)
    return p


def _band(ax, x, M, color, label, ls="-", marker=None):
    M = np.atleast_2d(M).astype(float)
    med = np.median(M, 0); q1 = np.percentile(M, 25, 0); q3 = np.percentile(M, 75, 0)
    ax.plot(x, med, ls, color=color, lw=STYLE["lw"], label=label, marker=marker, ms=4)
    if M.shape[0] > 1:
        ax.fill_between(x, q1, q3, color=color, alpha=STYLE["band_alpha"], linewidth=0)
    return med


# ============================================================ BAKEOFF (THE headline)
def fig_bakeoff(d, out):
    heads = _heads(d)
    accs = [h for h in heads if f"acc_{h}" in _keys(d)]
    if not accs:
        return []
    # left: accuracy x BWT frontier; right: 4-axis scorecard
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    floor = float(np.median(d["acc_linear"])) if "acc_linear" in _keys(d) else None
    for h in accs:
        col, ls, mk = _hs(h)
        acc = float(np.median(d[f"acc_{h}"]))
        bwt = float(np.median(d[f"bwt_{h}"])) if f"bwt_{h}" in _keys(d) else 0.0
        greyed = (floor is not None and acc < floor - 0.03)            # sub-floor -> greyed
        c = "#cccccc" if greyed else col
        axL.scatter([bwt], [acc], color=c, marker=mk or "o", s=70, zorder=3,
                    edgecolor="k", linewidth=0.4, label=h)
        axL.annotate(h, (bwt, acc), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    if "acc_race_bp" in _keys(d):
        axL.axhline(float(np.median(d["acc_race_bp"])), color=_hs("race_bp")[0], ls="--", lw=1.3, label="race_bp (static ceil)")
    if floor is not None:
        axL.axhline(floor, color=_hs("linear")[0], ls="-", lw=1.0, label="linear floor")
    axL.set_xlabel("BWT (forgetting; 0 = none)"); axL.set_ylabel("readout accuracy")
    axL.set_title("acc x BWT frontier"); axL.legend(fontsize=5.5, loc="best")
    # right: scorecard bars (acc, BWT-shifted, 1-spineflip, log cost) per head
    metrics = []
    for h in accs:
        acc = float(np.median(d[f"acc_{h}"]))
        bwt = float(np.median(d[f"bwt_{h}"])) if f"bwt_{h}" in _keys(d) else np.nan
        sflip = float(np.median(np.atleast_2d(d[f"spineflip_{h}"])[:, -1])) if f"spineflip_{h}" in _keys(d) else np.nan
        metrics.append((h, acc, bwt, sflip))
    x = np.arange(len(metrics)); w = 0.38
    axR.bar(x - w / 2, [m[1] for m in metrics], w, color=[_hs(m[0])[0] for m in metrics], label="acc")
    axR.bar(x + w / 2, [1 - m[3] if not np.isnan(m[3]) else 0 for m in metrics], w, color="#d9690a", alpha=0.5, label="spine-clean (1-flip)")
    axR.set_xticks(x); axR.set_xticklabels([m[0] for m in metrics], rotation=55, ha="right", fontsize=6)
    axR.set_ylim(0, 1.05); axR.set_title("scorecard"); axR.legend(fontsize=6); axR.grid(axis="x", visible=False)
    fig.suptitle("BAKEOFF — where acc x BWT peaks on the direction->magnitude axis", fontsize=10)
    return [_save(fig, out, "BAKEOFF.png")]


# ============================================================ SPINE-CLEAN (the spine)
def fig_spine_clean(d, out):
    heads = [h for h in _heads(d) if f"spineflip_{h}" in _keys(d)]
    if not heads or "perturb" not in _keys(d):
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    x = d["perturb"]
    floor = float(np.median(d["acc_linear"])) if "acc_linear" in _keys(d) else None
    for h in heads:
        col, ls, mk = _hs(h)
        greyed = (floor is not None and f"acc_{h}" in _keys(d) and float(np.median(d[f"acc_{h}"])) < floor - 0.03)
        c = "#cccccc" if greyed else col
        _band(axL, x, d[f"spineflip_{h}"], c, h, ls=ls, marker=mk)
    axL.set_xlabel("per-class norm perturb (sigma)"); axL.set_ylabel("argmax-flip rate")
    axL.set_title("(a) scale-invariance (cosine flat at 0)"); axL.legend(fontsize=6)
    # right: recency-drop bars
    rd = [(h, float(np.median(d[f"recencydrop_{h}"]))) for h in _heads(d) if f"recencydrop_{h}" in _keys(d)]
    if rd:
        axR.bar([r[0] for r in rd], [r[1] for r in rd], color=[_hs(r[0])[0] for r in rd])
        axR.set_ylabel("old-class acc drop (bursty)"); axR.set_title("(b) task-recency read")
        axR.tick_params(axis="x", labelrotation=55, labelsize=6); axR.grid(axis="x", visible=False)
    fig.suptitle("SPINE-CLEAN — how a pure magnitude nuisance moves each verdict", fontsize=10)
    return [_save(fig, out, "SPINE_CLEAN.png")]


# ============================================================ MULTIMODAL (P7.2)
def fig_multimodal(d, out):
    rungs = ["mean", "slda", "fecam", "gkeal", "mixture"]
    datasets = [ds for ds in ("digits", "cifarflat", "synthblob") if any(f"mm_{r}_{ds}" in _keys(d) for r in rungs)]
    if not datasets:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    ds_style = {"digits": ("-", "o"), "cifarflat": ("--", "s"), "synthblob": (":", "^")}
    for ds in datasets:
        ls, mk = ds_style.get(ds, ("-", None))
        xs, ys = [], []
        for i, r in enumerate(rungs):
            k = f"mm_{r}_{ds}"
            if k in _keys(d):
                xs.append(i); ys.append(np.atleast_1d(d[k]).astype(float))
        if xs:
            med = [float(np.median(y)) for y in ys]
            col = "#cccccc" if ds == "synthblob" else "#d9690a"
            ax.plot(xs, med, ls, marker=mk, color=col, lw=STYLE["lw"], label=f"{ds}" + (" (sanity)" if ds == "synthblob" else ""))
    ax.set_xticks(range(len(rungs))); ax.set_xticklabels(rungs, rotation=30, fontsize=8)
    ax.set_ylabel("readout accuracy"); ax.set_title("MULTIMODAL — closed-form fallback ladder (natural decides)")
    ax.legend(fontsize=7)
    outs = [_save(fig, out, "MULTIMODAL.png")]
    if "nmodes" in _keys(d):
        fig2, ax2 = plt.subplots(figsize=STYLE["figsize_single"])
        nm = np.atleast_2d(d["nmodes"]).astype(float)
        ax2.bar(np.arange(nm.shape[1]), np.median(nm, 0), color="#2c6fbf")
        ax2.set_xlabel("class"); ax2.set_ylabel("n-modes (BIC)"); ax2.set_title("per-class multimodality (natural tap space)")
        ax2.grid(axis="x", visible=False)
        outs += [_save(fig2, out, "MULTIMODAL_nmodes.png")]
    return outs


# ============================================================ IMBALANCE (P7.3)
def fig_imbalance(d, out):
    ks = [k for k in _keys(d) if k.startswith("imbal_")]
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_wide"])
    labs, olds, recents = [], [], []
    for k in sorted(ks):
        v = np.atleast_2d(d[k]).astype(float)
        labs.append(k[len("imbal_"):]); olds.append(float(np.median(v[:, 0]))); recents.append(float(np.median(v[:, 1])))
    x = np.arange(len(labs)); w = 0.38
    ax.bar(x - w / 2, olds, w, color="#2c6fbf", label="old classes")
    ax.bar(x + w / 2, recents, w, color="#d9690a", label="recent classes")
    ax.set_xticks(x); ax.set_xticklabels(labs, rotation=55, ha="right", fontsize=6)
    ax.set_ylabel("accuracy"); ax.set_title("IMBALANCE — old vs recent, guard on/off"); ax.legend(fontsize=7)
    ax.grid(axis="x", visible=False)
    return [_save(fig, out, "IMBALANCE.png")]


# ============================================================ CONT-SAFETY (the GATE)
def fig_cont_safety(d, out):
    heads = [h for h in _heads(d) if f"bwt_{h}" in _keys(d)]
    if not heads:
        return []
    fig, axes = plt.subplots(1, 3, figsize=STYLE["figsize_wide"])
    for ax, mt in zip(axes, ["aa", "bwt", "forget"]):
        vals, labs, cols = [], [], []
        for h in heads:
            k = f"{mt}_{h}"
            if k in _keys(d):
                vals.append(float(np.median(d[k]))); labs.append(h)
                cols.append("#7f7f7f" if h in ("linear", "linear-softmax") else _hs(h)[0])
        ax.bar(labs, vals, color=cols); ax.set_title(mt.upper()); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelrotation=60, labelsize=6)
    fig.suptitle("CONT-SAFETY — each head vs the floor-head-on-same-bulk (the A6 gate)", fontsize=10)
    return [_save(fig, out, "CONT_SAFETY.png")]


# ============================================================ NAT-ANCHOR (P7.5)
def fig_nat_anchor(d, out):
    # keys nat_<dataset>_acc_<head> ; nat_<dataset>_bwt_<head>
    ks = [k for k in _keys(d) if k.startswith("nat_")]
    if not ks:
        return []
    datasets = sorted({k.split("_")[1] for k in ks})
    fig, axes = plt.subplots(1, len(datasets), figsize=(min(4 * len(datasets), 9), 4.0), squeeze=False)
    for ax, ds in zip(axes[0], datasets):
        rows = [(k.split("_", 3)[3], float(np.median(d[k]))) for k in ks if k.startswith(f"nat_{ds}_acc_")]
        if rows:
            ax.bar([r[0] for r in rows], [r[1] for r in rows], color=[_hs(r[0])[0] for r in rows])
            ax.set_title(ds, fontsize=9); ax.tick_params(axis="x", labelrotation=60, labelsize=6)
            ax.grid(axis="x", visible=False); ax.set_ylabel("accuracy")
    fig.suptitle("NAT-ANCHOR — the bake-off headline on real flat data", fontsize=10)
    return [_save(fig, out, "NAT_ANCHOR.png")]


# ============================================================ RANDUMB (P7.0 control)
def fig_randumb(d, out):
    ks = [k for k in _keys(d) if k.startswith("randumb_")]
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    labs = [k[len("randumb_"):] for k in sorted(ks)]
    arr = np.stack([np.median(np.atleast_2d(d[k]).astype(float), 0) for k in sorted(ks)])   # [H,3]
    x = np.arange(len(labs)); w = 0.26
    ax.bar(x - w, arr[:, 0], w, color="#d9690a", label="OURS bulk")
    ax.bar(x, arr[:, 1], w, color=_hs("randproj_taps")[0], label="rand-proj taps")
    ax.bar(x + w, arr[:, 2], w, color=_hs("randproj_pixels")[0], label="rand-proj pixels", alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels(labs, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("accuracy"); ax.set_title("RANDUMB — did the trained bulk earn its keep?")
    ax.legend(fontsize=7); ax.grid(axis="x", visible=False)
    return [_save(fig, out, "RANDUMB.png")]


# ============================================================ COST-PROXY (descriptive-only)
def fig_cost(d, out):
    ks = [k for k in _keys(d) if k.startswith("cost_")]
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    labs = [k[len("cost_"):] for k in sorted(ks)]
    vals = [float(np.median(np.atleast_1d(d[k]).astype(float))) for k in sorted(ks)]
    ax.bar(labs, vals, color=[_hs(l)[0] for l in labs])
    ax.set_ylabel("readout fwd-MACs (PROXY; real=P8)"); ax.set_yscale("log")
    ax.set_title("COST-PROXY — descriptive only, NOT a decision axis")
    ax.tick_params(axis="x", labelrotation=55, labelsize=6); ax.grid(axis="x", visible=False)
    return [_save(fig, out, "COST_PROXY.png")]


# ============================================================ INV (every run)
def fig_inv(d, out):
    panels = [k for k in _keys(d) if k.startswith("inv_")]
    if not panels:
        return []
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(min(3 * n, 12), 2.4))
    if n == 1:
        axes = [axes]
    for ax, k in zip(axes, sorted(panels)):
        va = np.atleast_1d(d[k]).astype(float).ravel(); name = k[len("inv_"):]
        if va.size > 1:
            ax.plot(np.arange(va.size), va, "-", color="#d9690a", lw=STYLE["lw"])
        else:
            ax.bar([name], [float(va[0])], color="#d9690a")
        ax.set_title(name, fontsize=9); ax.grid(axis="x", visible=False)
    fig.suptitle("INV — health + apparatus sanity", fontsize=10)
    return [_save(fig, out, "INV.png")]


_ALL = [fig_bakeoff, fig_spine_clean, fig_multimodal, fig_imbalance, fig_cont_safety,
        fig_nat_anchor, fig_randumb, fig_cost, fig_inv]


def regen(run_dir):
    """Redraw every figure whose arrays are present in <run-dir>/arrays.npz. The citable path."""
    d = np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True)
    written = []
    for fn in _ALL:
        try:
            written += fn(d, run_dir)
        except Exception as e:
            print(f"  [plot {fn.__name__} skipped: {e}]")
    return written


if __name__ == "__main__":
    import sys
    for p in regen(sys.argv[1]):
        print(os.path.basename(p))
