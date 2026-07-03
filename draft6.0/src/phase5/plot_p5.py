"""
plot_p5 — the ONE plotting module for Phase 5 (result-format.md §0/§A). Every figure is exactly one `fig_*`
function reading `arrays.npz` (+ `manifest.json`) from a run dir, drawing in the single locked STYLE, writing a
300-dpi transparent PNG. No rung styles inline; `regen(run_dir)` redraws every figure whose arrays are present —
the citable path (a figure you can't regen from saved data is a screenshot, not a result).

Grows rung-by-rung: P5.0 fills `fig_depth_profile` (the headline, parameterized by task profile) + `fig_inv`;
the rest are declared stubs (one function per catalog CODE) filled when their rung runs.
"""
from __future__ import annotations
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

# ============================================================ §A — the single locked STYLE
STYLE = dict(
    dpi=300,
    figsize_single=(6.0, 4.0), figsize_wide=(7.5, 4.0), figsize_strip=(10, 2.2),
    font="DejaVu Sans", fs_base=10, fs_title=11, fs_axis=10, fs_tick=9, fs_cap=9,
    iqr_alpha=0.18, line_lw=1.8, bold_lw=2.2, grid_c="#d9d9d9", grid_lw=0.6,
    # method encoding (colour · style) — fixed forever; carries P3/P4
    c_ours="#d9690a", c_trunc="#111111", c_w12="#2ca02c", c_bp="#2c6fbf", c_mono="#8a1b8a",
    c_chance="#111111", c_bayes="#2ca02c",
)
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["fs_base"],
                     "axes.titlesize": STYLE["fs_title"], "axes.labelsize": STYLE["fs_axis"],
                     "xtick.labelsize": STYLE["fs_tick"], "ytick.labelsize": STYLE["fs_tick"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"]})


# ------------------------------------------------------------ shared helpers
def _med_iqr(a):
    """median, q25, q75 across seeds (axis 0). a: [S] or [S, L]."""
    a = np.asarray(a, float)
    return np.median(a, 0), np.percentile(a, 25, 0), np.percentile(a, 75, 0)


def _grid(ax):
    ax.grid(True, color=STYLE["grid_c"], lw=STYLE["grid_lw"], zorder=0)
    ax.set_axisbelow(True)


def _band(ax, x, arr, color, label, *, ls="-", lw=None, marker=None):
    """median line + IQR fill (the house curve)."""
    m, lo, hi = _med_iqr(arr)
    ax.plot(x, m, color=color, ls=ls, lw=lw or STYLE["line_lw"], marker=marker, ms=4,
            label=label, zorder=3)
    ax.fill_between(x, lo, hi, color=color, alpha=STYLE["iqr_alpha"], lw=0, zorder=2)
    return m


def _save(fig, run, name):
    out = os.path.join(run, name)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def _has(d, *keys):
    return all(k in d for k in keys)


# ============================================================ DEPTH-PROFILE (the headline; P5.0 reproduction)
_PROFILES = {
    # profile -> (ours_key, w12_key|None, scalar_ref_key|None, ref_kind, title)
    "headroom": ("hr_probe_w2", "hr_probe_w12", "hr_bp", "bp", "Headroom — depth should pay"),
    "flat":     ("fl_probe_w2", "fl_probe_w12", "fl_bayes", "bayes", "Flat — depth should NOT pay (known Bayes)"),
}


def fig_depth_profile(run, profile="headroom"):
    """Per-layer linear-probe vs depth, OURS(w2) vs the w12 objective-capability ceiling, with the achievable
    reference (tuned-BP on headroom; Bayes-optimal on flat) + chance. Answers: does the lever stop the decay /
    march the peak deeper? (For P5.0: does the P4.3 decay reproduce?) Truncation-floor ref is added at P5.3."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if profile == "mixed":
        return _fig_mixed(run, d)
    ok_key, w12_key, ref_key, ref_kind, title = _PROFILES[profile]
    if ok_key not in d:
        return None
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    m = _band(ax, x, d[ok_key], STYLE["c_ours"], "OURS (w2, adopted)", lw=STYLE["bold_lw"])
    peak = int(np.argmax(m)) + 1
    ax.axvline(peak, color=STYLE["c_ours"], ls=":", lw=0.8, zorder=1)
    if w12_key and w12_key in d:
        _band(ax, x, d[w12_key], STYLE["c_w12"], "w12 ceiling (objective limit; never deployed)", ls="--")
    if ref_key and ref_key in d:
        rm = float(np.median(d[ref_key]))
        if ref_kind == "bayes":
            rm = 1.0 - rm                                            # bayes_err -> achievable accuracy
            lab = f"Bayes-optimal ({rm:.2f})"
            ax.axhline(rm, color=STYLE["c_bayes"], ls=":", lw=1.2, label=lab)
        else:
            ax.axhline(rm, color=STYLE["c_bp"], ls="-", lw=1.4, label=f"tuned-BP ({rm:.2f})")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({1.0/nclass:.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("linear-probe accuracy"); ax.set_title(title)
    ax.set_xticks(x); ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    return _save(fig, run, f"DEPTH-PROFILE-{profile}.png")


def _fig_mixed(run, d):
    """The corruption detector: per-subtask per-layer probe on the mixed (disjoint-label) task. The flat
    subtask (solved early) vs the headroom subtask (needs depth) under the adopted w2 cell — does depth
    CORRUPT the early-solved flat subtask? tuned-BP per-subtask = the 'BP doesn't corrupt' reference."""
    if "mx_probe_flat_w2" not in d:
        return None
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    _band(ax, x, d["mx_probe_flat_w2"], STYLE["c_ours"], "flat subtask (OURS w2)", lw=STYLE["bold_lw"], marker="o")
    _band(ax, x, d["mx_probe_head_w2"], STYLE["c_ours"], "headroom subtask (OURS w2)", ls="--", marker="s")
    if _has(d, "mx_bp_flat", "mx_bp_head"):
        ax.axhline(float(np.median(d["mx_bp_flat"])), color=STYLE["c_bp"], ls="-", lw=1.2,
                   label=f"tuned-BP flat ({np.median(d['mx_bp_flat']):.2f})")
        ax.axhline(float(np.median(d["mx_bp_head"])), color=STYLE["c_bp"], ls="--", lw=1.2,
                   label=f"tuned-BP head ({np.median(d['mx_bp_head']):.2f})")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({1.0/nclass:.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("per-subtask linear-probe acc")
    ax.set_title("Mixed — does depth corrupt the early-solved flat subtask?")
    ax.set_xticks(x); ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    return _save(fig, run, "DEPTH-PROFILE-mixed.png")


# ============================================================ TEMP-FLOOR (P5.1 headline — is temp the free lever?)
def _collapse_idx(tail_med, temps):
    """First (sharpest, low-temp) index whose tail is real-below the next-milder temp -> the collapse cliff."""
    for i in range(1, len(temps)):
        if tail_med[i] < tail_med[i - 1] - 0.02:
            return i
    return None


def fig_temp_floor(run, task="headroom"):
    """tail-L12 (left) & real-readout (right) vs InfoNCE temperature, with the lr-matched temp=0.5 control line
    (above it = the gain is direction/free; at the sweep's temp0.5 = lr does nothing), the w12 ceiling + tuned-BP
    refs (headroom), and the collapse region shaded. The decisive figure: is a sharper temp the FREE depth lever?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_tail" not in d:
        return None
    temps = list(d["temps"]); x = np.arange(len(temps))
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    for ax, key, lrm_key, ylab in ((axL, f"{task}_tail", f"{task}_lrm_tail", "tail-L12 (linear probe)"),
                                   (axR, f"{task}_readout", f"{task}_lrm_readout", "readout accuracy")):
        _grid(ax)
        m = _band(ax, x, d[key], STYLE["c_ours"], "OURS (temp sweep)", lw=STYLE["bold_lw"], marker="o")
        ci = _collapse_idx(m, temps)
        if ci is not None:
            ax.axvspan(ci - 0.5, len(temps) - 0.5, color="#bbbbbb", alpha=0.22, zorder=1)
            ax.text(ci, ax.get_ylim()[0], " collapse", fontsize=STYLE["fs_cap"], color="#555555", va="bottom")
        if lrm_key in d:
            lrm = float(np.median(d[lrm_key]))
            ax.axhline(lrm, color=STYLE["c_ours"], ls=(0, (4, 3)), lw=1.4,
                       label=f"temp0.5 @ lr-matched ({lrm:.3f})")
        if task == "headroom":
            if "ref_w12_tail" in d and ax is axL:
                ax.axhline(float(d["ref_w12_tail"]), color=STYLE["c_w12"], ls="--", lw=1.3, label="w12 ceiling")
            if "ref_w12_ro" in d and ax is axR:
                ax.axhline(float(d["ref_w12_ro"]), color=STYLE["c_w12"], ls="--", lw=1.3, label="w12 ceiling")
            if "ref_bp" in d:
                ax.axhline(float(d["ref_bp"]), color=STYLE["c_bp"], ls="-", lw=1.2, label="tuned-BP")
        ax.set_xticks(x); ax.set_xticklabels([f"{t:g}" for t in temps])
        ax.set_xlabel("InfoNCE temperature (mild → sharp)"); ax.set_ylabel(ylab)
        ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    fig.suptitle(f"TEMP-FLOOR — {task}: is a sharper objective the free depth lever?", fontsize=STYLE["fs_title"])
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return _save(fig, run, f"TEMP-FLOOR-{task}.png")


def fig_depth_profile_temps(run, task="headroom"):
    """Per-layer probe vs depth, one curve per temperature (orange light=mild → dark=sharp), + the w12-tail ceiling.
    Shows whether a sharper temp marches the peak deeper and lifts the tail (the DEPTH-PROFILE, per-temp variant)."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_probe" not in d:
        return None
    temps = list(d["temps"]); L = int(d["L"]); xl = np.arange(1, L + 1)
    prof = np.asarray(d[f"{task}_probe"], float)                      # [S, T, L]
    shades = plt.cm.Oranges(np.linspace(0.42, 0.96, len(temps)))
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    for ti, t in enumerate(temps):
        med = np.median(prof[:, ti, :], 0)
        ax.plot(xl, med, color=shades[ti], lw=STYLE["line_lw"], marker="o", ms=3, label=f"temp {t:g}", zorder=3)
    if "ref_w12_tail" in d:
        ax.axhline(float(d["ref_w12_tail"]), color=STYLE["c_w12"], ls="--", lw=1.3, label="w12 tail (ceiling)")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({1.0/nclass:.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("linear-probe accuracy"); ax.set_xticks(xl)
    ax.set_title(f"DEPTH-PROFILE per temp — {task}")
    ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9, ncol=2)
    return _save(fig, run, f"DEPTH-PROFILE-temps-{task}.png")


# ============================================================ CREDIT-REACH (P5.2 — window on top of temp0.2)
def fig_credit_reach(run, task="headroom"):
    """Composing depth (tail-L12) per unit credit reach: temp0.2 × window {2,3,4} (+ the temp0.2 w12 objective
    ceiling), vs the w12@temp0.5 ceiling and tuned-BP. Panel A = tail vs window; panel B = the cost-Pareto
    (tail vs backward-work). Answers: does a bounded window close the residual to w12, and at what cost?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_w_tail" not in d:
        return None
    win = [int(w) for w in d["windows"]]; work = list(np.asarray(d[f"{task}_w_work"], float))
    xs = list(win); ys = [d[f"{task}_w_tail"][:, i] for i in range(len(win))]
    if task == "headroom" and "hr_w12_tail" in d:                    # add the temp0.2 full-credit ceiling point
        xs = xs + [12]; ys = ys + [d["hr_w12_tail"]]; work = work + [float(d["hr_w12_work"])]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    # panel A: tail vs window
    _grid(axA)
    med = np.array([np.median(y) for y in ys]); lo = np.array([np.percentile(y, 25) for y in ys])
    hi = np.array([np.percentile(y, 75) for y in ys])
    axA.plot(xs, med, color=STYLE["c_ours"], lw=STYLE["bold_lw"], marker="o", label="temp0.2 × window")
    axA.fill_between(xs, lo, hi, color=STYLE["c_ours"], alpha=STYLE["iqr_alpha"], lw=0)
    if "hr_w4s2_tail" in d and task == "headroom":
        axA.scatter([4], [np.median(d["hr_w4s2_tail"])], color="#111111", marker="x", s=45, zorder=5,
                    label="w4 overlap (s2)")
    if task == "headroom":                                           # the w12/BP refs are headroom-specific
        for key, c, lab in (("ref_w12t05_tail", STYLE["c_w12"], "w12@temp0.5 ceiling"),
                            ("ref_bp", STYLE["c_bp"], "tuned-BP"), ("ref_w2t05_tail", "#999999", "w2@temp0.5 baseline")):
            if key in d:
                axA.axhline(float(d[key]), color=c, ls="--" if "w12" in key else "-", lw=1.2, label=lab)
    axA.set_xlabel("coordination window (backward depth)"); axA.set_ylabel("tail-L12 (linear probe)")
    axA.set_xticks(xs); axA.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    # panel B: cost-Pareto (tail vs backward-work)
    _grid(axB)
    axB.plot(work, med, color=STYLE["c_ours"], lw=STYLE["line_lw"], marker="o")
    for xw, ym, w_ in zip(work, med, xs):
        axB.annotate(f"w{w_}", (xw, ym), fontsize=STYLE["fs_cap"], xytext=(3, 3), textcoords="offset points")
    if task == "headroom" and "ref_w12t05_tail" in d:
        axB.axhline(float(d["ref_w12t05_tail"]), color=STYLE["c_w12"], ls="--", lw=1.2, label="w12@temp0.5")
    axB.set_xlabel("backward work (substrate units)"); axB.set_ylabel("tail-L12")
    axB.set_xscale("log"); axB.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    fig.suptitle(f"CREDIT-REACH — {task}: does a bounded window close the residual to w12?", fontsize=STYLE["fs_title"])
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return _save(fig, run, f"CREDIT-REACH-{task}.png")


def fig_depth_profile_window(run, task="headroom"):
    """Per-layer probe vs depth, one curve per window (orange light=w2 → dark=w4) at temp0.2, + the w12 ceiling.
    Does adding window march the peak deeper / lift the tail past what temp0.2 alone reached?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_w_probe" not in d:
        return None
    win = [int(w) for w in d["windows"]]; Ln = int(d["L"]); xl = np.arange(1, Ln + 1)
    prof = np.asarray(d[f"{task}_w_probe"], float)                    # [S, Wn, L]
    shades = plt.cm.Oranges(np.linspace(0.45, 0.95, len(win)))
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    for wi, w in enumerate(win):
        ax.plot(xl, np.median(prof[:, wi, :], 0), color=shades[wi], lw=STYLE["line_lw"], marker="o", ms=3,
                label=f"w{w}", zorder=3)
    if task == "headroom" and "hr_w12_probe" in d:
        ax.plot(xl, np.median(d["hr_w12_probe"], 0), color=STYLE["c_w12"], ls="--", lw=1.5, label="w12 (temp0.2)")
    if task == "headroom" and "ref_w12t05_tail" in d:
        ax.axhline(float(d["ref_w12t05_tail"]), color=STYLE["c_w12"], ls=":", lw=1.0, label="w12@temp0.5 tail")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({1.0/nclass:.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("linear-probe accuracy"); ax.set_xticks(xl)
    ax.set_title(f"DEPTH-PROFILE per window — {task} (temp0.2)")
    ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9, ncol=2)
    return _save(fig, run, f"DEPTH-PROFILE-window-{task}.png")


# ============================================================ PLACEMENT (P5.3 — profiler + lost/rotated + floor)
def fig_placement(run, task="headroom"):
    """Per-depth linear probe (the profiler) + MLP probe (lost-vs-rotated) + per-depth READOUT, with the probe-peak
    and readout-optimal depths marked, and the from-scratch truncation floor (headroom). Answers: where does the
    extractor end, do probe & readout agree, is the deep info lost or rotated, and does a short stack match?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_lin" not in d:
        return None
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    lin = _band(ax, x, d[f"{task}_lin"], STYLE["c_ours"], "linear probe", lw=STYLE["bold_lw"])
    if f"{task}_mlp" in d:
        _band(ax, x, d[f"{task}_mlp"], STYLE["c_ours"], "MLP probe (lost vs rotated)", ls="--")
    rod = _band(ax, x, d[f"{task}_readout_depth"], STYLE["c_bp"], "readout @ depth", marker="o")
    ppk = int(np.argmax(lin)) + 1; ropt = int(np.argmax(rod)) + 1
    ax.axvline(ppk, color=STYLE["c_ours"], ls=":", lw=1.0)
    ax.axvline(ropt, color=STYLE["c_bp"], ls=":", lw=1.0)
    ax.annotate(f"probe-peak L{ppk}", (ppk, lin.max()), fontsize=STYLE["fs_cap"], color=STYLE["c_ours"],
                xytext=(2, -12), textcoords="offset points")
    ax.annotate(f"readout-opt L{ropt}", (ropt, rod.max()), fontsize=STYLE["fs_cap"], color=STYLE["c_bp"],
                xytext=(2, 6), textcoords="offset points")
    if task == "headroom" and "trunc_L7_owntuned" in d:
        tr = float(np.median(d["trunc_L7_owntuned"]))
        ax.axhline(tr, color=STYLE["c_trunc"], ls="-", lw=1.4, label=f"truncation floor L7 ({tr:.2f})")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({1.0/nclass:.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("accuracy"); ax.set_xticks(x)
    ax.set_title(f"PLACEMENT — {task}: where does the extractor end?")
    ax.legend(fontsize=STYLE["fs_cap"], loc="lower center", framealpha=0.9, ncol=2)
    return _save(fig, run, f"PLACEMENT-{task}.png")


# ============================================================ fig_heads (P5.4 — per-depth heads vs all-tap)
def fig_heads(run, task="headroom"):
    """Per-depth head accuracy (MLP heads = circles, linear heads = light) vs the all-tap baseline (dashed) and
    the truncation floor (black). Marks the placement-optimal head. Answers: do per-depth heads match all-tap at
    lower read-cost?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}_head_mlp" not in d:
        return None
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    hm = _band(ax, x, d[f"{task}_head_mlp"], STYLE["c_ours"], "per-depth head (MLP)", lw=STYLE["bold_lw"], marker="o")
    if f"{task}_head_lin" in d:
        ax.plot(x, np.median(d[f"{task}_head_lin"], 0), color="#e8a96a", lw=1.3, marker=".", label="per-depth head (linear)")
    at = float(np.median(d[f"{task}_alltap"]))
    ax.axhline(at, color=STYLE["c_ours"], ls=(0, (5, 3)), lw=1.6, label=f"all-tap ({at:.3f})")
    bd = int(np.argmax(hm)) + 1
    ax.scatter([bd], [hm.max()], color=STYLE["c_ours"], marker="*", s=140, zorder=6,
               label=f"head-best L{bd} ({hm.max():.3f})")
    if "trunc_floor" in d:
        ax.axhline(float(d["trunc_floor"]), color=STYLE["c_trunc"], ls="-", lw=1.3, label=f"trunc floor ({float(d['trunc_floor']):.3f})")
    nclass = int(d["n_class"]) if "n_class" in d else 4
    cval = 1.0 / (2 * nclass) if task == "mixed" else 1.0 / nclass
    ax.axhline(cval, color=STYLE["c_chance"], ls=":", lw=0.8, label=f"chance ({cval:.2f})")
    rc = float(np.median(d[f"{task}_cost_head"]) / np.median(d[f"{task}_cost_alltap"]))
    ax.set_xlabel("layer (head depth)"); ax.set_ylabel("readout accuracy"); ax.set_xticks(x)
    ax.set_title(f"HEADS vs ALL-TAP — {task} (read-best ≈ {rc:.2f}× all-tap cost)")
    ax.legend(fontsize=STYLE["fs_cap"], loc="lower center", framealpha=0.9, ncol=2)
    return _save(fig, run, f"PLACEMENT-heads-{task}.png")


# ============================================================ EXIT-PARETO (P5.5 — cost on the continual stream)
def fig_exit_pareto(run):
    """The STOPPING-MARK-① picture: accuracy vs FORWARD expected-compute on the CONTINUAL stream, for the five
    readers — calibrated exit (one-shot τ / per-task-refit τ), all-tap (the deployed baseline), truncation (the
    floor), and the oracle-exit (best-per-input layer, the upper bound). Median ± IQR over seeds. The exit WINS
    iff its one-shot point sits left of BOTH the all-tap and truncation cost lines while holding the 0.95·all-tap
    accuracy floor (lower-right is better: cheap + accurate)."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if "pareto_exit1_acc" not in d:
        return None
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    readers = [
        ("exit1", STYLE["c_ours"], "*", 200, "calibrated exit (one-shot τ)"),
        ("exitR", "#e8a96a", "P", 90, "calibrated exit (refit τ)"),
        ("alltap", STYLE["c_bp"], "s", 70, "all-tap (deployed)"),
        ("trunc", STYLE["c_trunc"], "D", 60, "truncation floor"),
        ("oracle", STYLE["c_w12"], "^", 80, "oracle exit (upper bound)"),
    ]
    at_acc = float(np.median(d["pareto_alltap_acc"]))
    at_cost = float(np.median(d["pareto_alltap_cost"]))
    tr_cost = float(np.median(d["pareto_trunc_cost"]))
    ax.axhline(0.95 * at_acc, color="#999999", ls=":", lw=1.1, label=f"0.95·all-tap ({0.95*at_acc:.3f})")
    ax.axvline(at_cost / 1000, color=STYLE["c_bp"], ls=(0, (4, 3)), lw=1.0, alpha=0.7)
    ax.axvline(tr_cost / 1000, color=STYLE["c_trunc"], ls=(0, (4, 3)), lw=1.0, alpha=0.7)
    for key, c, mk, ms, lab in readers:
        acc = np.asarray(d[f"pareto_{key}_acc"], float)
        cost = np.asarray(d[f"pareto_{key}_cost"], float) / 1000.0       # kMACs
        am, alo, ahi = _med_iqr(acc); cm, clo, chi = _med_iqr(cost)
        ax.errorbar([cm], [am], xerr=[[cm - clo], [chi - cm]], yerr=[[am - alo], [ahi - am]],
                    fmt=mk, color=c, ms=np.sqrt(ms), mec="k", mew=0.5, ecolor=c, elinewidth=1.0,
                    capsize=2.5, label=lab, zorder=5)
    ax.set_xlabel("forward expected-compute (kMACs / sample)"); ax.set_ylabel("continual accuracy")
    nclass = int(d["n_class"]) if "n_class" in d else 10
    ax.axhline(1.0 / nclass, color=STYLE["c_chance"], ls=":", lw=0.7, label=f"chance ({1.0/nclass:.2f})")
    k = int(d["trunc_k"]) if "trunc_k" in d else 0
    ax.set_title(f"EXIT-PARETO — continual stream (truncation L{k}; lower-right wins)")
    ax.legend(fontsize=STYLE["fs_cap"], loc="lower right", framealpha=0.9)
    return _save(fig, run, "EXIT-PARETO.png")


# ============================================================ INV (every run) — health + apparatus sanity
def fig_inv(run):
    """Small-multiples: loss-slope (cell learns) · dead-unit % (≈0) · effective-rank · cost-meter sanity ·
    guards pass (FD < 1e-5, equiv bit-exact). The at-a-glance apparatus check the design gates every rung on."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, axs = plt.subplots(1, 5, figsize=STYLE["figsize_strip"])
    # 1) loss-slope (headroom w2 training trace)
    ax = axs[0]; _grid(ax)
    if "inv_losstrace" in d:
        tr = np.asarray(d["inv_losstrace"], float)
        m, lo, hi = _med_iqr(tr) if tr.ndim == 2 else (tr, tr, tr)
        ax.plot(np.arange(1, len(m) + 1), m, color=STYLE["c_ours"], lw=STYLE["line_lw"])
        if tr.ndim == 2:
            ax.fill_between(np.arange(1, len(m) + 1), lo, hi, color=STYLE["c_ours"], alpha=STYLE["iqr_alpha"], lw=0)
    ax.set_title("InfoNCE loss\n(falls = learns)", fontsize=STYLE["fs_cap"]); ax.set_xlabel("epoch")
    # 2) dead-fraction (≈0)
    ax = axs[1]; _grid(ax)
    if "inv_deadfrac" in d:
        _band(ax, x, d["inv_deadfrac"], STYLE["c_ours"], None)
    ax.axhline(0, color=STYLE["c_chance"], ls=":", lw=0.8)
    ax.set_title("dead-unit %\n(≈0 expected)", fontsize=STYLE["fs_cap"]); ax.set_xlabel("layer"); ax.set_ylim(-0.02, 1)
    # 3) effective rank
    ax = axs[2]; _grid(ax)
    if "inv_erank" in d:
        _band(ax, x, d["inv_erank"], STYLE["c_ours"], None)
    ax.set_title("effective rank", fontsize=STYLE["fs_cap"]); ax.set_xlabel("layer")
    # 4) cost-meter sanity (monotone in window)
    ax = axs[3]; _grid(ax)
    if "inv_costsane_w" in d and "inv_costsane_work" in d:
        ax.plot(d["inv_costsane_w"], d["inv_costsane_work"], color=STYLE["c_trunc"], marker="o", lw=STYLE["line_lw"])
    ax.set_title("backward work\n(monotone in w)", fontsize=STYLE["fs_cap"]); ax.set_xlabel("window")
    # 5) guards pass
    ax = axs[4]; ax.axis("off")
    fd = float(d["inv_fdguard"]) if "inv_fdguard" in d else float("nan")
    eq = float(d["inv_equiv"]) if "inv_equiv" in d else float("nan")
    fd_ok = fd < 1e-5; eq_ok = eq < 1e-9
    ax.text(0.5, 0.92, "GUARDS", ha="center", va="top", weight="bold", fontsize=STYLE["fs_cap"])
    ax.text(0.5, 0.52, f"FD grad: {fd:.1e}\n{'PASS' if fd_ok else 'FAIL'}", ha="center", va="center",
            color=("#1a7f37" if fd_ok else "#d62728"), fontsize=STYLE["fs_cap"])
    ax.text(0.5, 0.12, f"equiv: {eq:.1e}\n{'PASS' if eq_ok else 'FAIL'}", ha="center", va="bottom",
            color=("#1a7f37" if eq_ok else "#d62728"), fontsize=STYLE["fs_cap"])
    fig.suptitle("INV — apparatus health & guards", fontsize=STYLE["fs_title"])
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    return _save(fig, run, "INV.png")


# ============================================================ CONT-SAFETY (P5.7 — the A6 gate)
_CS_STYLE = {  # cond -> (color, label)
    "t05_L4_sleep": ("#999999", "temp0.5 L4 (A6 base)"),
    "t02_L4_sleep": ("#d9690a", "temp0.2 L4 (GATE)"),
    "t02_L12_sleep": ("#8a1b8a", "temp0.2 L12 (depth)"),
    "t02_L4_nosleep": ("#111111", "temp0.2 L4 (no-sleep rot)"),
}


def fig_cont_safety(run, task="digits"):
    """The A6-gate picture: AA + BWT per condition (left) and the all-class SCFF-probe trajectory (right). The
    GATE (temp0.2 L4) must hold AA and keep BWT within 0.02 of the temp0.5 baseline, and the SCFF probe must stay
    flat (the bulk doesn't forget). The no-sleep rot bar shows the forgetting sleep recovers."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if f"{task}__t05_L4_sleep__aa" not in d:
        return None
    conds = [c for c in ("t05_L4_sleep", "t02_L4_sleep", "t02_L12_sleep", "t02_L4_nosleep")
             if f"{task}__{c}__aa" in d]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    x = np.arange(len(conds)); wbar = 0.38
    for i, c in enumerate(conds):
        col, _ = _CS_STYLE[c]
        aa = _med_iqr(d[f"{task}__{c}__aa"]); bwt = _med_iqr(d[f"{task}__{c}__bwt"])
        axA.bar(x[i] - wbar / 2, aa[0], wbar, color=col, alpha=0.85,
                yerr=[[aa[0] - aa[1]], [aa[2] - aa[0]]], capsize=2, label="AA" if i == 0 else None)
        axA.bar(x[i] + wbar / 2, bwt[0], wbar, color=col, alpha=0.45, hatch="//",
                yerr=[[bwt[0] - bwt[1]], [bwt[2] - bwt[0]]], capsize=2, label="BWT" if i == 0 else None)
    b05 = float(np.median(d[f"{task}__t05_L4_sleep__bwt"]))
    axA.axhline(b05 - 0.02, color=STYLE["c_trunc"], ls=":", lw=1.0, label="BWT gate (−0.02)")
    axA.axhline(0, color="#444444", lw=0.6)
    _grid(axA)
    axA.set_xticks(x); axA.set_xticklabels([_CS_STYLE[c][1] for c in conds], rotation=30, ha="right",
                                           fontsize=STYLE["fs_cap"] - 1)
    axA.set_ylabel("accuracy / BWT"); axA.set_title(f"A6 gate — {task} (AA solid · BWT hatched)")
    axA.legend(fontsize=STYLE["fs_cap"], loc="lower left", framealpha=0.9)
    # right: SCFF-probe trajectory
    _grid(axB)
    for c in conds:
        sp = d[f"{task}__{c}__scff_probe"]; t = np.arange(1, sp.shape[1] + 1)
        _band(axB, t, sp, _CS_STYLE[c][0], _CS_STYLE[c][1])
    axB.set_xlabel("task #"); axB.set_ylabel("all-class SCFF probe")
    axB.set_title("does the BULK forget? (flat = no)")
    axB.legend(fontsize=STYLE["fs_cap"] - 1, loc="lower left", framealpha=0.9)
    fig.tight_layout()
    return _save(fig, run, f"CONT-SAFETY-{task}.png")


# ============================================================ SCORECARD (P5.9 — the assembled-cell verdict)
def fig_scorecard(run):
    """The Phase-5 verdict in one frame (assembled from the committed-cell columns of every rung): depth-EARNED
    (headroom tail vs w12 / tuned-BP), read-CHEAPLY (continual Pareto), continual-SAFE (BWT gate), natural-CONFIRM
    (digits+CIFAR decay→fix). One config — temp0.2/w2 — ran every rung, so this is the assembled-cell confirmation."""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    if "de_ours" not in d:
        return None
    fig, axs = plt.subplots(2, 2, figsize=(9.5, 7.2))
    # (0,0) DEPTH-EARNED — headroom tail: OURS vs w12 ceiling vs tuned-BP
    ax = axs[0, 0]; _grid(ax)
    bars = [("OURS\ntemp0.2", "de_ours", STYLE["c_ours"]), ("w12\nceiling", "de_w12", STYLE["c_w12"]),
            ("tuned-BP", "de_bp", STYLE["c_bp"])]
    for i, (lab, key, c) in enumerate(bars):
        m, lo, hi = _med_iqr(d[key])
        ax.bar(i, m, 0.6, color=c, alpha=0.85, yerr=[[m - lo], [hi - m]], capsize=3)
        ax.text(i, m + 0.01, f"{m:.3f}", ha="center", fontsize=STYLE["fs_cap"])
    ax.set_xticks(range(3)); ax.set_xticklabels([b[0] for b in bars], fontsize=STYLE["fs_cap"])
    ax.set_ylabel("headroom tail-L12 (probe)"); ax.set_title("① depth EARNED (headroom)")
    ax.set_ylim(0, max(np.median(d["de_w12"]), np.median(d["de_ours"])) + 0.12)
    # (0,1) READ-CHEAPLY — continual Pareto
    ax = axs[0, 1]; _grid(ax)
    pts = [("all-tap", "rc_alltap", STYLE["c_bp"], "s"), ("truncation", "rc_trunc", STYLE["c_trunc"], "D"),
           ("exit", "rc_exit", STYLE["c_ours"], "*"), ("oracle", "rc_oracle", STYLE["c_w12"], "^")]
    for lab, key, c, mk in pts:
        am = float(np.median(d[f"{key}_acc"])); cm = float(np.median(d[f"{key}_cost"])) / 1000
        ax.scatter([cm], [am], color=c, marker=mk, s=110, ec="k", lw=0.5, label=lab, zorder=5)
    ax.set_xlabel("forward kMACs/sample"); ax.set_ylabel("continual acc")
    ax.set_title("② read CHEAPLY (ship truncation)"); ax.legend(fontsize=STYLE["fs_cap"] - 1, loc="lower right")
    # (1,0) CONTINUAL-SAFE — BWT gate
    ax = axs[1, 0]; _grid(ax)
    grp = [("digits", "cs_digits"), ("synth", "cs_synth")]; xx = np.arange(len(grp)); wb = 0.38
    for j, (tlab, c) in enumerate((("t05", "#999999"), ("t02", STYLE["c_ours"]))):
        vals = [_med_iqr(d[f"{key}_{tlab}_bwt"]) for _, key in grp]
        ax.bar(xx + (j - 0.5) * wb, [v[0] for v in vals], wb, color=c, alpha=0.85,
               yerr=[[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]], capsize=2,
               label="temp0.5" if j == 0 else "temp0.2")
    ax.axhline(0, color="#444", lw=0.6); ax.set_xticks(xx); ax.set_xticklabels([g[0] for g in grp])
    ax.set_ylabel("BWT (0 = no forgetting)"); ax.set_title("③ continual SAFE (gate PASS)")
    ax.legend(fontsize=STYLE["fs_cap"], loc="lower right")
    # (1,1) NATURAL-CONFIRM — tail decay→fix
    ax = axs[1, 1]; _grid(ax)
    grp = [("digits", "nat_digits"), ("CIFAR-flat", "nat_cifar")]; xx = np.arange(len(grp))
    for j, (tlab, c) in enumerate((("t05", "#999999"), ("t02", STYLE["c_ours"]))):
        vals = [_med_iqr(d[f"{key}_{tlab}_tail"]) for _, key in grp]
        ax.bar(xx + (j - 0.5) * wb, [v[0] for v in vals], wb, color=c, alpha=0.85,
               yerr=[[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]], capsize=2,
               label="temp0.5" if j == 0 else "temp0.2")
    ax.set_xticks(xx); ax.set_xticklabels([g[0] for g in grp])
    ax.set_ylabel("tail-L12 probe"); ax.set_title("④ natural CONFIRM (decay→fix)")
    ax.legend(fontsize=STYLE["fs_cap"], loc="upper right")
    fig.suptitle("PHASE-5 SCORECARD — the committed cell (temp0.2 / w2): SCFF close-out", fontsize=STYLE["fs_title"] + 1)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, run, "SCORECARD.png")


# ============================================================ later-rung figures (one fn per CODE; filled per rung)
def _stub(code, rung):
    def f(run, *a, **k):
        raise NotImplementedError(f"{code} is added at {rung} (result-format §C) — not part of the P5.0 slice.")
    return f


fig_residual_ablation = _stub("RESIDUAL-ABLATION", "P5.6")


# ============================================================ NAT-ANCHOR (P5.8 — natural-data confirmation)
def fig_nat_anchor(run, dataset="digits"):
    """The synthetic-artifact gate: per-layer probe on a REAL flat anchor (digits / CIFAR-flat) for the decay
    baseline (temp0.5) vs the adopted fix (temp0.2). Does the decay AND the fix reproduce off synthetic data?"""
    d = dict(np.load(os.path.join(run, "arrays.npz")))
    t5, t2 = f"{dataset}_t05_probe", f"{dataset}_t02_probe"
    if t5 not in d:
        return None
    L = int(d["L"]); x = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    _grid(ax)
    m5 = _band(ax, x, d[t5], "#999999", "temp0.5 (decay baseline)", lw=STYLE["line_lw"], marker="o")
    m2 = _band(ax, x, d[t2], STYLE["c_ours"], "temp0.2 (adopted fix)", lw=STYLE["bold_lw"], marker="o")
    for m, c in ((m5, "#999999"), (m2, STYLE["c_ours"])):
        pk = int(np.argmax(m)) + 1
        ax.axvline(pk, color=c, ls=":", lw=0.8, zorder=1)
    ax.axhline(1.0 / int(d["n_class"]), color=STYLE["c_chance"], ls=":", lw=0.8,
               label=f"chance ({1.0/int(d['n_class']):.2f})")
    ax.set_xlabel("layer"); ax.set_ylabel("linear-probe accuracy"); ax.set_xticks(x)
    dd = int(np.median(d[f"{dataset}_t02_peak"])) if f"{dataset}_t02_peak" in d else 0
    name = {"digits": "digits (64-D)", "cifar": "CIFAR-flat (3072-D)"}.get(dataset, dataset)
    ax.set_title(f"NAT-ANCHOR — {name}: decay + temp-fix on real flat data")
    ax.legend(fontsize=STYLE["fs_cap"], loc="best", framealpha=0.9)
    return _save(fig, run, f"NAT-ANCHOR-{dataset}.png")


# ============================================================ the citable regen path
def regen(run_dir):
    """Redraw every figure whose arrays are present in <run-dir>/arrays.npz (result-format §0). Skips a figure
    whose arrays are absent (a rung emits a subset). Returns the list of PNGs written."""
    d = dict(np.load(os.path.join(run_dir, "arrays.npz")))
    written = []
    if "de_ours" in d:                                               # P5.9 — assembled-cell scorecard
        try:
            p = fig_scorecard(run_dir)
            if p:
                written.append(p)
        except Exception as e:
            print(f"  [regen] SCORECARD skipped: {e}")
        return [w for w in written if w]
    if any(k.endswith("_t05_probe") for k in d):                     # P5.8 — natural-data confirmation
        for dataset in ("digits", "cifar"):
            try:
                p = fig_nat_anchor(run_dir, dataset)
                if p:
                    written.append(p)
            except Exception as e:
                print(f"  [regen] NAT-ANCHOR({dataset}) skipped: {e}")
        try:
            written.append(fig_inv(run_dir))
        except Exception as e:
            print(f"  [regen] INV skipped: {e}")
        return [w for w in written if w]
    if any(k.endswith("__t05_L4_sleep__aa") for k in d):             # P5.7 — continual-safety gate
        for task in ("digits", "synth"):
            try:
                p = fig_cont_safety(run_dir, task)
                if p:
                    written.append(p)
            except Exception as e:
                print(f"  [regen] CONT-SAFETY({task}) skipped: {e}")
        return [w for w in written if w]                             # P5.7 emits no INV
    if "pareto_exit1_acc" in d:                                      # P5.5 — calibrated exit on continual
        try:
            p = fig_exit_pareto(run_dir)
            if p:
                written.append(p)
        except Exception as e:
            print(f"  [regen] EXIT-PARETO skipped: {e}")
    elif "windows" in d:                                             # P5.2 — credit reach (window sweep)
        for task in ("headroom", "flat", "mixed"):
            for fn in (fig_credit_reach, fig_depth_profile_window):
                try:
                    p = fn(run_dir, task)
                    if p:
                        written.append(p)
                except Exception as e:
                    print(f"  [regen] {fn.__name__}({task}) skipped: {e}")
    elif any(k.endswith("_head_mlp") for k in d):                    # P5.4 — heads vs all-tap
        for task in ("headroom", "flat", "mixed"):
            try:
                p = fig_heads(run_dir, task)
                if p:
                    written.append(p)
            except Exception as e:
                print(f"  [regen] fig_heads({task}) skipped: {e}")
    elif "profiler_overlaps" in d:                                   # P5.3 — profiler + truncation
        for task in ("headroom", "flat", "mixed"):
            try:
                p = fig_placement(run_dir, task)
                if p:
                    written.append(p)
            except Exception as e:
                print(f"  [regen] PLACEMENT({task}) skipped: {e}")
    elif "temps" in d:                                                # P5.1 — temperature sweep
        for task in ("headroom", "flat", "mixed"):
            for fn in (fig_temp_floor, fig_depth_profile_temps):
                try:
                    p = fn(run_dir, task)
                    if p:
                        written.append(p)
                except Exception as e:
                    print(f"  [regen] {fn.__name__}({task}) skipped: {e}")
    else:                                                             # P5.0 — bench reproduction
        for prof in ("headroom", "flat", "mixed"):
            try:
                p = fig_depth_profile(run_dir, prof)
                if p:
                    written.append(p)
            except Exception as e:
                print(f"  [regen] DEPTH-PROFILE-{prof} skipped: {e}")
    try:
        written.append(fig_inv(run_dir))
    except Exception as e:
        print(f"  [regen] INV skipped: {e}")
    return [w for w in written if w]


if __name__ == "__main__":
    import sys
    rd = sys.argv[1] if len(sys.argv) > 1 else "."
    print("regen ->", regen(rd))
