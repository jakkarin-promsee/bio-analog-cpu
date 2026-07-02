"""
plot_p9 — the ONE plotting module for Phase 9 (result-format.md §A/§C). One function per figure code; the look lives
ONLY in STYLE = {**plot_p8.STYLE, **P9_NEW} (never re-defines a shared constant). `regen(run_dir)` redraws every figure
whose arrays are present in <run-dir>/arrays.npz — the citable path. No rung styles matplotlib inline.

Read by role (result-format §A): black dash-dot = the internal oracle/frozen reference (matching it cheaper is the
win); teal = the committed/adopted P9 choice; black-dashed-x = a spine null (herding, expected to fail); red = the
destruction/undefended read; grey = the P8 baseline arm; light-grey dotted = cited-not-built (LDC).
"""
from __future__ import annotations
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase8"))
import plot_p8   # noqa: E402  (inherit the canonical STYLE)

P9_NEW = dict()                                                        # P9 adds no NEW global constant (dpi/figsize/etc carried)
STYLE = {**plot_p8.STYLE, **P9_NEW}

# entity -> (colour, linestyle, marker) — the P9-new encodings (§A)
ENC = {
    "oracle":        ("#111111", "-.", "*"), "frozen": ("#111111", "-.", None),
    "always":        ("#2ca02c", "--", None), "always-pay": ("#2ca02c", "--", None),
    "rotation":      ("#2c6fbf", "-", None),
    "staleness":     ("#7f7f7f", "--", "o"),
    "destruction":   ("#d62728", "-", "o"),
    "no-N2":         ("#7f7f7f", "-", None), "no_n2": ("#7f7f7f", "-", None),
    "llrd-rate":     ("#0b8f6a", "-", "^"), "llrd": ("#0b8f6a", "-", "^"),
    "ema-view":      ("#9467bd", "-", "s"), "ema": ("#9467bd", "-", "s"),
    "ldc":           ("#cccccc", ":", None),
    "alltap":        ("#7f7f7f", "-", None),
    "truncK":        ("#0b8f6a", "-", "^"), "trunc":  ("#0b8f6a", "-", "^"),
    "perdepth":      ("#2c6fbf", "--", "s"),
    "cbrs":          ("#0b8f6a", "-", "^"),
    "reservoir":     ("#2c6fbf", "-", "s"),
    "recency":       ("#d9690a", "-", None),
    "herding":       ("#111111", "--", "x"),
    "dcbrs":         ("#0b8f6a", ":", "^"),
    "undefended":    ("#d62728", "--", None), "defended": ("#0b8f6a", "-", None),
    "committed":     ("#0b8f6a", "-", "^"),
}
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["base"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"],
                     "axes.grid": True, "grid.color": STYLE["grid"], "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none",
                     "savefig.transparent": True})


def _enc(name):
    return ENC.get(name, ("#555555", "-", None))


def _keys(d):
    return d.files if hasattr(d, "files") else list(d)


def _names(d, key):
    return [h.decode() if isinstance(h, bytes) else str(h) for h in d[key]] if key in _keys(d) else []


def _med(x):
    return float(np.median(np.atleast_1d(np.asarray(x, float))))


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    fig.tight_layout(); fig.savefig(p); plt.close(fig)
    return p


def _band(ax, x, M, color, label, ls="-", marker=None):
    M = np.atleast_2d(np.asarray(M, float))
    med = np.median(M, 0); q1 = np.percentile(M, 25, 0); q3 = np.percentile(M, 75, 0)
    ax.plot(x, med, ls, color=color, lw=STYLE["lw"], label=label, marker=marker, ms=4)
    if M.shape[0] > 1:
        ax.fill_between(x, q1, q3, color=color, alpha=STYLE["band_alpha"], linewidth=0)
    return med


# ============================================================ DRIFT-LIFELONG (P9.0 headline)
def fig_drift_lifelong(d, out):
    if "bulkdrift_life" not in _keys(d):
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    B = np.atleast_2d(np.asarray(d["bulkdrift_life"], float)); x = np.arange(B.shape[1])
    _band(axL, x, B, *(_enc("rotation")[:1]), label="rotation  cos(rep_t, birth)")
    axL.set_ylim(0, 1.03); axL.set_xlabel("probe-grid checkpoint (lifelong stream)")
    axL.set_ylabel("cosine to birth"); axL.set_title("(1) ROTATION — the taps rotate"); axL.legend(fontsize=7)
    for key, lab in (("frozenprobe_ret", "(2) staleness — fixed head fit at birth"),
                     ("refitprobe_ret", "(3) DESTRUCTION — re-fit optimal probe (verdict)")):
        if key in _keys(d):
            col, ls, mk = _enc("staleness" if "frozen" in key else "destruction")
            _band(axR, x, d[key], col, lab, ls=ls, marker=mk)
    axR.axhline(1.0, color="#111111", lw=0.7, ls=":")
    axR.axhline(1.0 - float(d["delta_acc"]) if "delta_acc" in _keys(d) else 0.98, color="#bbbbbb", ls=":", lw=0.8)
    axR.set_xlabel("probe-grid checkpoint"); axR.set_ylabel("retention / birth score")
    axR.set_title("early-task retention (verdict = curve 3)"); axR.legend(fontsize=6.5, loc="best")
    fig.suptitle("DRIFT-LIFELONG — does the bulk ROTATE (sleep fixes it) or FORGET (re-fit retention decays)?", fontsize=9.5)
    return [_save(fig, out, "DRIFT_LIFELONG.png")]


# ============================================================ N2-BAKEOFF (P9.1)
def fig_n2_bakeoff(d, out):
    arms = _names(d, "n2_arms")
    arms = [a for a in arms if f"accheld_{a}" in _keys(d)]
    if not arms:
        return []
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.0))
    metrics = [("drift_red", "drift-reduction ↓"), ("sleepfreq", "sleep-freq (@held acc)"),
               ("bwt_worst", "worst-pt A6-BWT"), ("plasticity", "new-task acc (tax)")]
    for ax, (mt, ttl) in zip(axes, metrics):
        vals, labs, cols = [], [], []
        for a in arms:
            k = f"{mt}_{a}"
            if k in _keys(d):
                vals.append(_med(d[k])); labs.append(a); cols.append(_enc(a)[0])
        if vals:
            ax.bar(labs, vals, color=cols)
        if mt == "bwt_worst":
            ax.axhline(0.0, color="#111111", lw=0.8)
        ax.set_title(ttl, fontsize=8.5); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelrotation=40, labelsize=7)
    fig.suptitle("N2-BAKEOFF — does a read-side N2 ↓drift -> sparser sleep at held A6 without a plasticity tax?", fontsize=9.5)
    return [_save(fig, out, "N2_BAKEOFF.png")]


# ============================================================ CADENCE-DEPTH (P9.2)
def fig_cadence_depth(d, out):
    depths = _names(d, "depths")
    depths = [dp for dp in depths if f"bwt_worst_{dp}" in _keys(d)]
    if not depths:
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    x = np.arange(len(depths)); cols = [_enc(dp)[0] for dp in depths]
    axL.bar(x, [_med(d[f"bwt_worst_{dp}"]) for dp in depths], color=cols)
    axL.axhline(0.0, color="#111111", lw=0.8)
    axL.set_xticks(x); axL.set_xticklabels(depths, fontsize=8); axL.set_title("worst-point A6-BWT")
    axL.grid(axis="x", visible=False)
    sc = [_med(d[f"sleepcost_{dp}"]) if f"sleepcost_{dp}" in _keys(d) else 0.0 for dp in depths]
    axR.bar(x, sc, color=cols); axR.set_yscale("log")
    axR.set_xticks(x); axR.set_xticklabels(depths, fontsize=8)
    axR.set_ylabel("sleep re-fit energy (pJ; Fdim-scaled)"); axR.set_title("metered sleep-cost (solve/Gram term)")
    axR.grid(axis="x", visible=False)
    fig.suptitle("CADENCE-DEPTH — which consolidation depth holds A6 at the lowest sleep cost?", fontsize=9.5)
    return [_save(fig, out, "CADENCE_DEPTH.png")]


# ============================================================ EVICT (P9.3)
def fig_evict(d, out):
    pols = _names(d, "evict_policies")
    pols = [p for p in pols if f"evictbwt_{p}" in _keys(d)]
    if not pols:
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    order = sorted(pols, key=lambda p: -_med(d[f"evictbwt_{p}"]))       # order by measured BWT (best first)
    x = np.arange(len(order))
    for xi, p in zip(x, order):
        M = np.atleast_1d(np.asarray(d[f"evictbwt_{p}"], float))
        col = _enc(p)[0]
        axL.bar(xi, np.median(M), color=col, yerr=[[np.median(M) - np.percentile(M, 25)],
                                                   [np.percentile(M, 75) - np.median(M)]], capsize=3)
    if "evictbwt_oracle" in _keys(d):
        axL.axhline(_med(d["evictbwt_oracle"]), color="#111111", ls="-.", lw=1.2, label="unbounded oracle")
        axL.legend(fontsize=7)
    axL.axhline(0.0, color="#111111", lw=0.8)
    axL.set_xticks(x); axL.set_xticklabels(order, rotation=40, ha="right", fontsize=7)
    axL.set_ylabel("worst-point BWT at the bound"); axL.set_title("eviction bake-off (@ pinned cap)")
    axL.grid(axis="x", visible=False)
    if "cap_scaling" in _keys(d):
        SC = np.asarray(d["cap_scaling"], float)                       # [Ncap, 3] = cap, #classes, min-cap-holding-BWT
        axR.plot(SC[:, 0], SC[:, 2], "-o", color="#0b8f6a", lw=STYLE["lw"], ms=4)
        axR.set_xlabel("buffer cap"); axR.set_ylabel("worst-pt BWT (cbrs)")
        axR.set_title("cap x #classes scaling")
    else:
        axR.axis("off")
    fig.suptitle("EVICT — does CBRS hold BWT at the bound; does eviction re-import forgetting (herding the null)?", fontsize=9)
    return [_save(fig, out, "EVICT.png")]


# ============================================================ RESIDUAL (P9.4, conditional)
def fig_residual(d, out):
    if "residual_ret" not in _keys(d):
        return []
    R = np.atleast_2d(np.asarray(d["residual_ret"], float))             # [S, 2] undefended, defended
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    labs = ["undefended", "read-side defended"]; cols = [_enc("undefended")[0], _enc("defended")[0]]
    ax.bar([0, 1], np.median(R, 0), color=cols,
           yerr=[np.median(R, 0) - np.percentile(R, 25, 0), np.percentile(R, 75, 0) - np.median(R, 0)], capsize=4)
    ax.axhline(1.0, color="#111111", lw=0.8, ls=":")
    ax.set_xticks([0, 1]); ax.set_xticklabels(labs, fontsize=9)
    ax.set_ylabel("directional retention (/ no-residual)")
    ax.set_title("RESIDUAL — can a read-side re-fit defend the Phase-6 residual?")
    ax.grid(axis="x", visible=False)
    return [_save(fig, out, "RESIDUAL.png")]


# ============================================================ FREEZE (P9.5 headline)
def fig_freeze(d, out):
    if "freeze_bwt_worst" not in _keys(d):
        return []
    fig, axes = plt.subplots(1, 3, figsize=STYLE["figsize_wide"])
    panels = [("freeze_bwt_worst", "worst-pt A6-BWT", 0.0), ("freeze_accheld", "accuracy-held (AA)", None),
              ("freeze_gdshare", "GD-share (<= 0.25)", 0.25)]
    for ax, (k, ttl, ref) in zip(axes, panels):
        if k in _keys(d):
            M = np.atleast_1d(np.asarray(d[k], float))
            ax.bar([0], [np.median(M)], color="#0b8f6a", width=0.5,
                   yerr=[[np.median(M) - np.percentile(M, 25)], [np.percentile(M, 75) - np.median(M)]], capsize=4)
            if "freeze_oracle_bwt" in _keys(d) and k == "freeze_bwt_worst":
                ax.axhline(_med(d["freeze_oracle_bwt"]), color="#111111", ls="-.", lw=1.2, label="oracle")
                ax.legend(fontsize=7)
            if ref is not None:
                ax.axhline(ref, color="#d62728" if ref == 0.25 else "#111111", ls=":", lw=1.0)
        ax.set_title(ttl, fontsize=9); ax.set_xticks([]); ax.grid(axis="x", visible=False)
    hh = _names(d, "freeze_hash")
    fig.suptitle(f"FREEZE — the assembled loop, live-safe at the metered economy  (hash {hh[0][:10] if hh else '?'})",
                 fontsize=9.5)
    return [_save(fig, out, "FREEZE.png")]


# ============================================================ CONT-SAFETY (assembled loop; carried from plot_p8)
def fig_cont_safety(d, out):
    cfgs = _names(d, "safety_cfgs")
    cfgs = [c for c in cfgs if f"bwt_worst_{c}" in _keys(d)]
    if not cfgs:
        return []
    fig, axes = plt.subplots(1, 3, figsize=STYLE["figsize_wide"])
    for ax, (mt, ttl) in zip(axes, [("aa", "AA"), ("bwt_worst", "worst-pt BWT"), ("forget", "forget")]):
        vals, labs, cols = [], [], []
        for c in cfgs:
            k = f"{mt}_{c}"
            if k in _keys(d):
                vals.append(_med(d[k])); labs.append(c); cols.append(_enc(c)[0])
        if vals:
            ax.bar(labs, vals, color=cols)
        ax.axhline(0.0, color="#111111", lw=0.8); ax.set_title(ttl, fontsize=9)
        ax.tick_params(axis="x", labelrotation=45, labelsize=7); ax.grid(axis="x", visible=False)
    fig.suptitle("CONT-SAFETY — the LIVE A6 gate on the assembled loop (worst mid-stream, pre-sleep)", fontsize=9.5)
    return [_save(fig, out, "CONT_SAFETY.png")]


# ============================================================ INV (every run)
def fig_inv(d, out):
    panels = [k for k in _keys(d) if k.startswith("inv_")]
    if not panels:
        return []
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(min(2.1 * n, 14), 2.3))
    if n == 1:
        axes = [axes]
    for ax, k in zip(axes, sorted(panels)):
        va = np.atleast_1d(np.asarray(d[k], float)).ravel(); name = k[len("inv_"):]
        if va.size > 1:
            ax.plot(np.arange(va.size), va, "-", color="#0b8f6a", lw=STYLE["lw"])
        else:
            ax.bar([name], [float(va[0])], color="#0b8f6a" if va[0] > 0.5 else "#d62728")
        ax.set_ylim(0, 1.15); ax.set_title(name, fontsize=7.5); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelsize=6)
    fig.suptitle("INV — guards (all bit-exact) + fire/sleep economy + apparatus sanity", fontsize=10)
    return [_save(fig, out, "INV.png")]


_ALL = [fig_drift_lifelong, fig_n2_bakeoff, fig_cadence_depth, fig_evict, fig_residual, fig_freeze,
        fig_cont_safety, fig_inv]


def regen(run_dir):
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
