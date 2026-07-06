"""
plot_p8 — the ONE plotting module for Phase 8 (result-format.md sec A/C). One function per figure code; the look lives
ONLY in STYLE. `regen(run_dir)` redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable
path (a figure you can't regen from saved data is a screenshot, not a result). No rung styles matplotlib inline.

Gate / trigger / head encoding (result-format sec A, fixed forever): green-dashed = always-pay (cost ceiling);
black dash-dot = oracle-cadence (THE reference the detector must approach); grey = absolute-theta; orange = DDM /
error-EMA (error-based / labeled — the DEPLOYED gate trigger); blue = ADWIN / SLDA; teal = tap-drift-direction /
DriftLens / STUDD / RanPAC (label-free; P8.2-preferred signal, validated NOT deployed); black-dashed-x =
tap-drift-magnitude (the false-fire NULL); purple = budget-gate (learned,
spine-flagged); magenta = BP energy model. The GATE-BAKEOFF frontier orders arms by MEASURED GD-fire-fraction; arms
failing the accuracy-held cut are greyed.
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
# entity -> (colour, linestyle, marker)
ENC = {
    "always":        ("#2ca02c", "--", None), "always-pay": ("#2ca02c", "--", None),
    "oracle":        ("#111111", "-.", "*"), "oracle-cadence": ("#111111", "-.", "*"),
    "abs":           ("#7f7f7f", "-", None), "absolute": ("#7f7f7f", "-", None),
    "ddm":           ("#d9690a", "-", "o"), "adwin": ("#2c6fbf", "-", "s"),
    "budget":        ("#9467bd", "-", "P"), "budget-gate": ("#9467bd", "-", "P"),
    "hddm":          ("#7f7f7f", ":", None), "rddm": ("#7f7f7f", ":", None),
    "error_ema":     ("#d9690a", ":", "o"), "error-ema": ("#d9690a", ":", "o"),
    "tap_dir":       ("#0b8f6a", "-", "^"), "tap-drift-direction": ("#0b8f6a", "-", "^"),
    "tap_mag":       ("#111111", "--", "x"), "tap-drift-magnitude": ("#111111", "--", "x"),
    "driftlens":     ("#0b8f6a", "--", "^"), "studd": ("#0b8f6a", ":", "^"),
    "ranpac":        ("#0b8f6a", "-", "^"), "slda": ("#2c6fbf", "--", "s"),
    "bp":            ("#8a1b8a", "--", None), "bp_replay": ("#8a1b8a", "--", None),
    "chance":        ("#111111", ":", None),
}
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["base"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"],
                     "axes.grid": True, "grid.color": STYLE["grid"], "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.transparent": False})


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


# ============================================================ GATE-BAKEOFF (THE headline)
def fig_gate_bakeoff(d, out):
    gates = _names(d, "gates")
    gates = [g for g in gates if f"accheld_{g}" in _keys(d)]
    if not gates:
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    oracle_acc = _med(d["accheld_oracle"]) if "accheld_oracle" in _keys(d) else None
    for g in gates:
        col, ls, mk = _enc(g)
        acc = _med(d[f"accheld_{g}"]); f = _med(d[f"firefrac_{g}"]) if f"firefrac_{g}" in _keys(d) else 0.0
        far = _med(d[f"far_{g}"]) if f"far_{g}" in _keys(d) else 0.0
        greyed = (oracle_acc is not None and acc < oracle_acc - 0.02 and g not in ("always", "oracle"))
        c = "#cccccc" if greyed else col
        size = 60 + 400 * far                                          # FAR as the third axis (marker size)
        axL.scatter([f], [acc], color=c, marker=mk or "o", s=size, zorder=3, edgecolor="k", linewidth=0.4, label=g)
        axL.annotate(g, (f, acc), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    if oracle_acc is not None:
        axL.axhline(oracle_acc, color=_enc("oracle")[0], ls="-.", lw=1.2, label="oracle acc")
        axL.axhline(oracle_acc - 0.02, color="#cccccc", ls=":", lw=1.0)
    if "accheld_always" in _keys(d):
        axL.axhline(_med(d["accheld_always"]), color=_enc("always")[0], ls="--", lw=1.0, label="always-pay ceiling")
    axL.axvline(0.25, color="#bbbbbb", ls=":", lw=1.0)                 # f*=0.25 reference LINE (not binary)
    axL.set_xlabel("GD-fire-fraction  f  (dashed = f*=0.25 ref)"); axL.set_ylabel("accuracy-held (final AA)")
    axL.set_title("gate frontier (marker size = FAR)"); axL.legend(fontsize=5.5, loc="best")
    # right: scorecard (accuracy-held, f, FAR)
    x = np.arange(len(gates)); w = 0.27
    axR.bar(x - w, [_med(d[f"accheld_{g}"]) for g in gates], w, color=[_enc(g)[0] for g in gates], label="acc-held")
    axR.bar(x, [_med(d[f"firefrac_{g}"]) if f"firefrac_{g}" in _keys(d) else 0 for g in gates], w,
            color="#7f7f7f", alpha=0.7, label="fire-frac")
    axR.bar(x + w, [_med(d[f"far_{g}"]) if f"far_{g}" in _keys(d) else 0 for g in gates], w,
            color="#d9690a", alpha=0.6, label="FAR")
    axR.set_xticks(x); axR.set_xticklabels(gates, rotation=55, ha="right", fontsize=6)
    axR.set_ylim(0, 1.05); axR.set_title("scorecard"); axR.legend(fontsize=6); axR.grid(axis="x", visible=False)
    fig.suptitle("GATE-BAKEOFF — accuracy-held x GD-fire-fraction (FAR the 3rd axis) vs the oracle", fontsize=10)
    return [_save(fig, out, "GATE_BAKEOFF.png")]


# ============================================================ TRIGGER (MTD x FAR)
def fig_trigger(d, out):
    trigs = _names(d, "triggers")
    trigs = [t for t in trigs if f"mtd_{t}" in _keys(d)]
    if not trigs:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    for t in trigs:
        col, ls, mk = _enc(t)
        mtd = _med(d[f"mtd_{t}"]); far = _med(d[f"far_{t}"]) if f"far_{t}" in _keys(d) else 0.0
        ax.scatter([mtd], [far], color=col, marker=mk or "o", s=90, zorder=3, edgecolor="k", linewidth=0.4, label=t)
        ax.annotate(t, (mtd, far), fontsize=7, xytext=(4, 3), textcoords="offset points")
    if "far_error_ema" in _keys(d):
        ax.axhline(_med(d["far_error_ema"]), color=_enc("error_ema")[0], ls=":", lw=1.0)
    ax.set_xlabel("MTD (detection delay; lower = earlier)"); ax.set_ylabel("FAR on nuisance (lower = spine-clean)")
    ax.set_title("TRIGGER — does class-direction lead error without false-firing?")
    ax.legend(fontsize=6.5, loc="best")
    return [_save(fig, out, "TRIGGER.png")]


# ============================================================ CADENCE (P8.3)
def fig_cadence(d, out):
    if "cadence_grid" not in _keys(d):
        return []
    G = np.asarray(d["cadence_grid"], float)                          # [S, F, H] accuracy-held
    accH = np.median(G, 0)                                            # [F, H]
    fig, axes = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    freqs = _names(d, "cadence_freqs") or [str(i) for i in range(accH.shape[0])]
    hists = _names(d, "cadence_hists") or [str(i) for i in range(accH.shape[1])]
    im = axes[0].imshow(accH, aspect="auto", cmap="viridis", origin="lower")
    axes[0].set_xticks(range(len(hists))); axes[0].set_xticklabels(hists, fontsize=7)
    axes[0].set_yticks(range(len(freqs))); axes[0].set_yticklabels(freqs, fontsize=7)
    axes[0].set_xlabel("LUT history frac x lam_ema"); axes[0].set_ylabel("sleep cadence (every-k)")
    axes[0].set_title("accuracy-held"); fig.colorbar(im, ax=axes[0], fraction=0.046)
    if "cadence_bwt" in _keys(d):
        Bw = np.median(np.asarray(d["cadence_bwt"], float), 0)
        im2 = axes[1].imshow(Bw, aspect="auto", cmap="RdYlGn", origin="lower", vmin=-0.2, vmax=0.05)
        axes[1].set_xticks(range(len(hists))); axes[1].set_xticklabels(hists, fontsize=7)
        axes[1].set_yticks(range(len(freqs))); axes[1].set_yticklabels(freqs, fontsize=7)
        axes[1].set_xlabel("LUT history frac x lam_ema"); axes[1].set_title("worst-point A6-BWT")
        fig.colorbar(im2, ax=axes[1], fraction=0.046)
    fig.suptitle("CADENCE — cheapest sleep cadence x history x lam_ema that holds the A6 win", fontsize=10)
    return [_save(fig, out, "CADENCE.png")]


# ============================================================ COST-METER (per-op breakdown)
def fig_cost_meter(d, out):
    heads = [h for h in ("ranpac", "slda") if f"energy_{h}_total" in _keys(d)]
    if not heads:
        return []
    ops = ["mac", "adc", "write", "solve"]
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    x = np.arange(len(heads)); bottom = np.zeros(len(heads))
    opcol = {"mac": "#7f7f7f", "adc": "#d9690a", "write": "#2c6fbf", "solve": "#9467bd"}
    for op in ops:
        vals = [_med(d[f"energy_{h}_{op}"]) if f"energy_{h}_{op}" in _keys(d) else 0.0 for h in heads]
        ax.bar(x, vals, 0.5, bottom=bottom, color=opcol[op], label=op + (" (ADC)" if op == "adc" else ""))
        bottom += np.array(vals)
    ax.set_xticks(x); ax.set_xticklabels(heads, fontsize=9); ax.set_yscale("log")
    ax.set_ylabel("energy (pJ; behavioral, ADC-centred)"); ax.set_title("COST-METER — per-op energy, RanPAC vs SLDA")
    ax.legend(fontsize=7); ax.grid(axis="x", visible=False)
    return [_save(fig, out, "COST_METER.png")]


# ============================================================ METERED-8020 (GD vs SCFF share)
def fig_metered_8020(d, out):
    cfgs = _names(d, "econ_configs")
    cfgs = [c for c in cfgs if f"gdshare_{c}" in _keys(d)]
    if not cfgs:
        return []
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    x = np.arange(len(cfgs))
    gd = [_med(d[f"gdshare_{c}"]) for c in cfgs]
    scff = [1 - g for g in gd]
    ax.bar(x, scff, 0.5, color="#2ca02c", label="SCFF share (a+b)")
    ax.bar(x, gd, 0.5, bottom=scff, color="#9467bd", label="GD share (c+d)")
    ax.axhline(1 - 0.25, color="#111111", ls=":", lw=1.0)             # the 80/20 reference line
    ax.text(len(cfgs) - 0.5, 0.75, "80/20 line", fontsize=6, ha="right", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels(cfgs, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("fraction of metered energy"); ax.set_ylim(0, 1.05)
    ax.set_title("METERED-8020 — GD share vs the 80/20 target"); ax.legend(fontsize=7); ax.grid(axis="x", visible=False)
    outs = [_save(fig, out, "METERED_8020.png")]
    if "bp_ratio" in _keys(d):
        fig2, ax2 = plt.subplots(figsize=STYLE["figsize_single"])
        br = np.atleast_1d(np.asarray(d["bp_ratio"], float))
        ax2.bar(["OURS / BP+replay"], [_med(br)], 0.4, color="#8a1b8a")
        ax2.axhline(1.0, color="#111111", ls=":", lw=1.0)
        ax2.set_ylabel("energy ratio (lower = OURS cheaper)")
        ax2.set_title("bp_ratio — OURS vs BP+replay (matched retention)"); ax2.grid(axis="x", visible=False)
        outs += [_save(fig2, out, "METERED_8020_bp.png")]
    return outs


# ============================================================ DRIFT (P8.0: live bulk-drift + drift-visibility)
def fig_drift(d, out):
    if "bulkdrift" not in _keys(d):
        return []
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    B = np.atleast_2d(np.asarray(d["bulkdrift"], float))              # [S, K]
    x = np.arange(B.shape[1])
    _band(axL, x, B, "#0b8f6a", "bulk_drift cos(rep_t, rep_ref)", ls="-")
    axL.set_ylim(0, 1.02); axL.set_xlabel("stream step"); axL.set_ylabel("cosine to reference")
    axL.set_title("live SCFF drift ('the bulk doesn't forget')"); axL.legend(fontsize=7)
    # right: drift-visibility -- do the signals move at REAL onsets vs the NUISANCE covariate shift, and do
    # error-rate and tap-drift measure DIFFERENT things?  driftvis = [S, 3(seg), nsig], normalized to calib=1.
    if "driftvis" in _keys(d):
        V = np.median(np.asarray(d["driftvis"], float), 0)           # [3(seg), nsig]
        labs = ["calib", "real-onset", "nuisance"]
        siglabs = _names(d, "driftvis_labels") or [f"s{j}" for j in range(V.shape[1])]
        sigcol = {"tap_dir": "#0b8f6a", "tap_mag": "#111111", "error": "#d9690a", "driftlens": "#2c6fbf"}
        xg = np.arange(3); nsig = V.shape[1]; w = 0.8 / nsig
        for j, sl in enumerate(siglabs):
            axR.bar(xg + (j - (nsig - 1) / 2) * w, V[:, j], w, color=sigcol.get(sl, "#888888"),
                    alpha=0.85, label=sl)
        axR.axhline(1.0, color="#111111", lw=0.7, ls=":")
        axR.set_xticks(xg); axR.set_xticklabels(labs, fontsize=8)
        axR.set_ylabel("signal / calib baseline"); axR.set_title("drift-visibility (well-posed?)")
        axR.legend(fontsize=6.5); axR.grid(axis="x", visible=False)
    fig.suptitle("DRIFT — is the detection problem well-posed (signals move at real, not nuisance)", fontsize=10)
    return [_save(fig, out, "DRIFT.png")]


# ============================================================ CONT-SAFETY (the LIVE A6 gate, worst point)
def fig_cont_safety(d, out):
    gates = _names(d, "gates")
    gates = [g for g in gates if f"bwt_worst_{g}" in _keys(d) or f"bwt_{g}" in _keys(d)]
    if not gates:
        return []
    fig, axes = plt.subplots(1, 3, figsize=STYLE["figsize_wide"])
    metrics = [("aa", "AA"), ("bwt_worst", "BWT (worst mid-stream)"), ("forget", "forget")]
    for ax, (mt, ttl) in zip(axes, metrics):
        vals, labs, cols = [], [], []
        for g in gates:
            k = f"{mt}_{g}"
            if k in _keys(d):
                vals.append(_med(d[k])); labs.append(g); cols.append(_enc(g)[0])
        if vals:
            ax.bar(labs, vals, color=cols)
        ax.axhline(0.0, color="#111111", lw=0.8)
        ax.set_title(ttl, fontsize=9); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelrotation=55, labelsize=6)
    fig.suptitle("CONT-SAFETY — the LIVE A6 gate at the awake gate's WORST point (pre-sleep)", fontsize=10)
    return [_save(fig, out, "CONT_SAFETY.png")]


# ============================================================ SUBSTRATE (P8.7 — "why analog?")
def fig_substrate(d, out):
    """The 2x2 substrate ablation: {OURS, GD+replay} x {analog, digital}. Left: the four total-energy bars (log-y),
    the headline three (OURS-analog / OURS-digital / GD-digital) foregrounded, the win-arrows annotated. Right: the
    E_MAC_DIG memory-wall sensitivity sweep (OURS-analog is a flat reference; the digital costs rise with data
    movement -> the analog advantage is a floor)."""
    need = ("E_ours_analog", "E_ours_digital", "E_gd_analog", "E_gd_digital")
    if not all(k in _keys(d) for k in need):
        return []
    oa = _med(d["E_ours_analog"]); od = _med(d["E_ours_digital"])
    ga = _med(d["E_gd_analog"]); gd = _med(d["E_gd_digital"])
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    labels = ["OURS\nanalog\n(the chip)", "OURS\ndigital", "GD+replay\nanalog", "GD+replay\ndigital\n(status quo)"]
    vals = [oa, od, ga, gd]
    cols = ["#0b8f6a", "#7fcbb4", "#c98ac9", "#8a1b8a"]                 # teal=OURS, magenta=GD; dark=headline substrate
    x = np.arange(4)
    bars = axL.bar(x, vals, 0.62, color=cols, edgecolor="k", linewidth=0.5, zorder=3)
    bars[0].set_edgecolor("#0b8f6a"); bars[0].set_linewidth(2.4)        # ring the hero (OURS-analog = the chip)
    axL.set_xticks(x); axL.set_xticklabels(labels, fontsize=7)
    axL.set_ylabel("total substrate energy (pJ; behavioral)")
    axL.set_title("the 2x2: model x substrate (linear)")
    axL.set_ylim(0, max(vals) * 1.18)
    for xi, v in zip(x, vals):                                          # value labels
        axL.annotate(f"{v:.2e}", (xi, v), fontsize=6.5, ha="center", va="bottom", xytext=(0, 2),
                     textcoords="offset points")
    # the three win-ratios (annotated, not asserted): substrate (OURS d->a), algorithm (GD d -> OURS d), total (GD d -> OURS a)
    sub_win = od / (oa + 1e-30); alg_win = gd / (od + 1e-30); tot_win = gd / (oa + 1e-30)
    txt = (f"substrate win (OURS digital/analog) = {sub_win:.1f}x\n"
           f"algorithm win (digital GD/OURS) = {alg_win:.1f}x\n"
           f"TOTAL win (GD-digital / OURS-analog) = {tot_win:.1f}x")
    axL.text(0.03, 0.97, txt, transform=axL.transAxes, fontsize=6.6, va="top", ha="left",
             bbox=dict(boxstyle="round", fc="#f7f7f7", ec="#999999", alpha=0.95))
    axL.grid(axis="x", visible=False)
    # right: the memory-wall sweep
    if "emac_sweep" in _keys(d):
        SW = np.asarray(d["emac_sweep"], float)                        # [K, 3] = e_mac_dig, ours_digital, gd_digital
        e = SW[:, 0]
        axR.plot(e, SW[:, 1], "-o", color="#7fcbb4", lw=STYLE["lw"], ms=4, label="OURS digital")
        axR.plot(e, SW[:, 2], "-s", color="#8a1b8a", lw=STYLE["lw"], ms=4, label="GD+replay digital")
        axR.axhline(oa, color="#0b8f6a", ls="-.", lw=1.6, label="OURS analog (substrate-indep.)")
        axR.axvline(0.2, color="#bbbbbb", ls=":", lw=1.0)              # the Horowitz arithmetic-only anchor
        axR.annotate("Horowitz 8b MAC", (0.2, oa), fontsize=6, va="bottom", ha="center", color="#666666",
                     xytext=(0, 3), textcoords="offset points")
        axR.set_yscale("log"); axR.set_xscale("log")
        axR.set_xlabel("digital MAC energy E_MAC_DIG (pJ)")
        axR.set_ylabel("total energy (pJ)"); axR.set_title("memory-wall sensitivity")
        axR.legend(fontsize=6.2, loc="lower right")
    fig.suptitle("SUBSTRATE — why analog: OURS-analog vs OURS-digital vs GD-digital", fontsize=9.5, y=1.0)
    return [_save(fig, out, "SUBSTRATE.png")]


# ============================================================ INV (every run)
def fig_inv(d, out):
    panels = [k for k in _keys(d) if k.startswith("inv_")]
    if not panels:
        return []
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(min(2.6 * n, 13), 2.4))
    if n == 1:
        axes = [axes]
    for ax, k in zip(axes, sorted(panels)):
        va = np.atleast_1d(np.asarray(d[k], float)).ravel(); name = k[len("inv_"):]
        if va.size > 1:
            ax.plot(np.arange(va.size), va, "-", color="#0b8f6a", lw=STYLE["lw"])
        else:
            ax.bar([name], [float(va[0])], color="#0b8f6a")
        ax.set_title(name, fontsize=8); ax.grid(axis="x", visible=False)
    fig.suptitle("INV — guards + fire economy + apparatus sanity", fontsize=10)
    return [_save(fig, out, "INV.png")]


_ALL = [fig_gate_bakeoff, fig_trigger, fig_cadence, fig_cost_meter, fig_metered_8020,
        fig_drift, fig_cont_safety, fig_substrate, fig_inv]


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
