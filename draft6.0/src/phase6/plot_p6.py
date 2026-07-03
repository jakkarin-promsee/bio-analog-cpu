"""
plot_p6 — the ONE plotting module for Phase 6 (result-format.md §A/§C). One function per figure code; the look
lives ONLY in STYLE. `regen(run_dir)` redraws every figure whose arrays are present in <run-dir>/arrays.npz — the
citable path (a figure you can't regen from saved data is a screenshot, not a result). No rung styles matplotlib
inline; no rung draws outside these functions.

Array-schema keys (result-format §A): a7acc_<method>_<channel>_<variant>, a7dir_<...>, dirinv_<method>_<channel>,
robust_vs_aug_<variant>, select_vs_aug_<variant>, flatness_<method>, doorb_<corruption>_<purity>, drift_<method>,
cont_<metric>_<change>, selectivity_<method>, inv_<panel>. Each fig draws only if its keys are present.
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
    ours="#d9690a", lin="#7f7f7f", ceil="#2ca02c", sam="#2ca02c",
    ch=dict(tap="#d9690a", input="#2c6fbf", adc="#8a1b8a", weight="#111111"),
    chance="#111111",
)
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["base"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"],
                     "axes.grid": True, "grid.color": STYLE["grid"], "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.transparent": False})


def _band(ax, x, M, color, label, ls="-", marker=None):
    """Median line + IQR shaded fill (the house band). M: [S, R]."""
    M = np.atleast_2d(M)
    med = np.median(M, 0); q1 = np.percentile(M, 25, 0); q3 = np.percentile(M, 75, 0)
    ax.plot(x, med, ls, color=color, lw=STYLE["lw"], label=label, marker=marker, ms=4)
    if M.shape[0] > 1:
        ax.fill_between(x, q1, q3, color=color, alpha=STYLE["band_alpha"], linewidth=0)
    return med


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    fig.tight_layout(); fig.savefig(p); plt.close(fig)
    return p


def _has(d, *keys):
    return all(k in d for k in keys)


def _keys_like(d, prefix):
    return [k for k in d.files if k.startswith(prefix)] if hasattr(d, "files") else [k for k in d if k.startswith(prefix)]


# ============================================================ A7-CURVE (the headline)
def fig_a7_curve(d, out):
    keyset = d.files if hasattr(d, "files") else d
    if "rms" not in keyset:
        return []
    rms = d["rms"]; R = len(rms); written = []

    def ok(k):                                                        # present AND on the shared rms grid
        return k in keyset and np.atleast_2d(d[k]).shape[1] == R
    for metric, pre, ylab in [("acc", "a7acc", "readout accuracy"), ("dir", "a7dir", "direction-invariance cos")]:
        fig, ax = plt.subplots(figsize=STYLE["figsize_wide"])
        drew = False
        # P6.8 assembled view: fix-free (dashed) vs hardened (solid bold), the directional channels
        for ch in ("tap", "input"):
            col = STYLE["ch"].get(ch, STYLE["ours"])
            if ok(f"{pre}_hardened_{ch}_dir") or ok(f"{pre}_fixfree_{ch}_dir"):
                if ok(f"{pre}_fixfree_{ch}_dir"):
                    _band(ax, rms, d[f"{pre}_fixfree_{ch}_dir"], col, f"fix-free {ch}·dir", ls="--"); drew = True
                if ok(f"{pre}_hardened_{ch}_dir"):
                    _band(ax, rms, d[f"{pre}_hardened_{ch}_dir"], col, f"hardened {ch}·dir", ls="-"); drew = True
        for ch in ("tap", "input"):                                   # P6.0 reproduction view (ours = fix-free)
            col = STYLE["ch"].get(ch, STYLE["ours"])
            for var, ls in [("iid", "-"), ("dir", "--")]:
                k = f"{pre}_ours_{ch}_{var}"
                if ok(k):
                    _band(ax, rms, d[k], col, f"OURS {ch}·{var}", ls=ls); drew = True
        # references
        if ok(f"{pre}_ceiling_tap_dir"):
            _band(ax, rms, d[f"{pre}_ceiling_tap_dir"], STYLE["ceil"], "noiseless ceiling", ls="--")
        for var, mk in [("dir", "o"), ("iid", None)]:
            k = f"{pre}_linbase_input_{var}"
            if ok(k):
                _band(ax, rms, d[k], STYLE["lin"], f"linear-ctrl input·{var}", ls="-", marker=mk)
        if not drew:
            plt.close(fig); continue
        ax.set_xlabel("injected RMS (projected on class axis)")
        ax.set_ylabel(ylab); ax.set_title(f"A7 sensitivity — {metric} (solid = iid, dashed = directional)")
        ax.legend(fontsize=7, ncol=2, loc="best")
        written.append(_save(fig, out, f"A7_CURVE_{metric}.png"))
    return written


# ============================================================ DIR-INVARIANCE (the spine)
def fig_dir_invariance(d, out):
    ks = _keys_like(d, "dirinv_")
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    for k in sorted(ks):
        _, method, ch = k.split("_", 2)
        col = STYLE["ours"] if method == "hardened" else STYLE["lin"]
        ls = "-" if method == "hardened" else "--"
        M = np.atleast_2d(d[k]); x = np.arange(1, M.shape[1] + 1)
        _band(ax, x, M, col, f"{method}·{ch}", ls=ls)
    ax.set_xlabel("depth (layer)"); ax.set_ylabel("cos(clean-rep, noisy-rep)")
    ax.set_title("Direction-invariance per depth (fix vs fix-free)")
    ax.legend(fontsize=8); ax.set_ylim(top=1.01)
    return [_save(fig, out, "DIR_INVARIANCE.png")]


# ============================================================ AUG-SWEEP
def fig_aug_sweep(d, out):
    if "sigaug" not in (d.files if hasattr(d, "files") else d):
        return []
    sig = d["sigaug"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    mk = {"iid": ("-", None), "dir": ("-", "o"), "randax": ("-", "^")}
    for var, (ls, m) in mk.items():
        rk = f"robust_vs_aug_{var}"; sk = f"select_vs_aug_{var}"
        if rk in (d.files if hasattr(d, "files") else d):
            _band(a1, sig, d[rk], STYLE["ours"], var, ls=ls, marker=m)
        if sk in (d.files if hasattr(d, "files") else d):
            _band(a2, sig, d[sk], STYLE["ours"], var, ls=ls, marker=m)
    a1.set_xlabel("σ_aug"); a1.set_ylabel("direction-invariance @ σ*"); a1.set_title("robustness gain"); a1.legend(fontsize=8)
    a2.set_xlabel("σ_aug"); a2.set_ylabel("clean selectivity"); a2.set_title("collapse / capacity guard"); a2.legend(fontsize=8)
    return [_save(fig, out, "AUG_SWEEP.png")]


# ============================================================ FLATNESS
def fig_flatness(d, out):
    ks = _keys_like(d, "flatness_")
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    labs = [k.split("_", 1)[1] for k in ks]
    meds = [float(np.median(d[k])) for k in ks]
    cols = [STYLE["sam"] if "sam" in k else STYLE["ours"] for k in ks]
    ax.bar(labs, meds, color=cols)
    ax.set_ylabel("sharpness (Δloss under unit perturbation)"); ax.set_title("Flatness — lower is flatter")
    ax.grid(axis="x", visible=False)
    return [_save(fig, out, "FLATNESS.png")]


# ============================================================ DOOR-B
def fig_door_b(d, out):
    ks = _keys_like(d, "doorb_")
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    labs = [k.split("_", 1)[1] for k in ks]; meds = [float(np.median(d[k])) for k in ks]
    ax.bar(labs, meds, color=STYLE["ours"])
    if "doorb_clean_ref" in (d.files if hasattr(d, "files") else d):
        ax.axhline(float(np.median(d["doorb_clean_ref"])), color=STYLE["ceil"], ls="--", label="clean-data cell")
        ax.legend(fontsize=8)
    ax.set_ylabel("direction-formed (ratio to clean)"); ax.set_title("Door B — all-noisy stream × buffer purity")
    ax.grid(axis="x", visible=False)
    return [_save(fig, out, "DOOR_B.png")]


# ============================================================ BULK-DRIFT
def fig_bulk_drift(d, out):
    ks = _keys_like(d, "drift_")
    if not ks:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    for k in sorted(ks):
        M = np.atleast_2d(d[k]); x = np.arange(M.shape[1])
        col = STYLE["ours"] if "hardened" in k else STYLE["lin"]
        _band(ax, x, M, col, k.split("_", 1)[1], ls="-" if "hardened" in k else "--")
    ax.set_xlabel("stream step (task)"); ax.set_ylabel("cos(rep_t, rep_{t+Δ})")
    ax.set_title("Bulk-drift over the continual stream"); ax.legend(fontsize=8)
    return [_save(fig, out, "BULK_DRIFT.png")]


# ============================================================ CONT-SAFETY (the gate)
def fig_cont_safety(d, out):
    metrics = ["aa", "bwt", "ret"]
    changes = sorted({k.split("_")[2] for k in _keys_like(d, "cont_")})
    if not changes:
        return []
    fig, axes = plt.subplots(1, 3, figsize=STYLE["figsize_wide"])
    for ax, mt in zip(axes, metrics):
        vals, labs = [], []
        for ch in changes:
            k = f"cont_{mt}_{ch}"
            if k in (d.files if hasattr(d, "files") else d):
                vals.append(float(np.median(d[k]))); labs.append(ch)
        cols = [STYLE["lin"] if l == "fixfree" else STYLE["ours"] for l in labs]
        ax.bar(labs, vals, color=cols); ax.set_title(mt.upper()); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelrotation=40)
    fig.suptitle("Continual-safety — each change vs fix-free committed cell")
    return [_save(fig, out, "CONT_SAFETY.png")]


# ============================================================ NAT-ANCHOR
def fig_nat_anchor(d, out):
    if "rms" not in (d.files if hasattr(d, "files") else d) or not _keys_like(d, "nat_"):
        return []
    rms = d["rms"]
    fig, ax = plt.subplots(figsize=STYLE["figsize_wide"])
    style = {"digits": ("-", "o"), "cifar": ("--", "s")}
    for k in sorted(_keys_like(d, "nat_")):
        parts = k.split("_")   # nat_<dataset>_<method>_<channel>
        ds = parts[1]; ls, m = style.get(ds, ("-", None))
        col = STYLE["ours"] if "hardened" in k else STYLE["lin"]
        _band(ax, rms, d[k], col, "_".join(parts[1:]), ls=ls, marker=m)
    ax.set_xlabel("injected RMS"); ax.set_ylabel("direction-invariance / acc")
    ax.set_title("Natural-data anchor — digits + CIFAR-flat"); ax.legend(fontsize=7)
    return [_save(fig, out, "NAT_ANCHOR.png")]


# ============================================================ INV (every run)
def fig_inv(d, out):
    panels = [k for k in _keys_like(d, "inv_")]
    if not panels:
        return []
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(min(3 * n, 12), 2.4))
    if n == 1:
        axes = [axes]
    for ax, k in zip(axes, sorted(panels)):
        v = d[k]; name = k.split("_", 1)[1]
        va = np.atleast_1d(v).astype(float).ravel()
        if va.size > 1:
            ax.plot(np.arange(va.size), va, "-", color=STYLE["ours"], lw=STYLE["lw"])
        else:
            ax.bar([name], [float(va[0])], color=STYLE["ours"])
        ax.set_title(name, fontsize=9); ax.grid(axis="x", visible=False)
    fig.suptitle("INV — health + apparatus sanity", fontsize=10)
    return [_save(fig, out, "INV.png")]


_ALL = [fig_a7_curve, fig_dir_invariance, fig_aug_sweep, fig_flatness, fig_door_b,
        fig_bulk_drift, fig_cont_safety, fig_nat_anchor, fig_inv]


def regen(run_dir):
    """Redraw every figure whose arrays are present in <run-dir>/arrays.npz. The citable path."""
    d = np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True)
    written = []
    for fn in _ALL:
        try:
            written += fn(d, run_dir)
        except Exception as e:                                         # a missing-key fig is a skip, not a crash
            print(f"  [plot {fn.__name__} skipped: {e}]")
    return written


if __name__ == "__main__":
    import sys
    for p in regen(sys.argv[1]):
        print(os.path.basename(p))
