"""
plot_p10 — the ONE plotting module for Phase 10 (result-format.md §A/§C). One function per figure code; the look
lives ONLY in STYLE = {**plot_p9.STYLE, **P10_NEW} (never re-defines a shared constant). `regen(run_dir)` redraws
every figure whose arrays are present in <run-dir>/arrays.npz — the citable path. No rung styles matplotlib inline.

Read by role (result-format §A): teal = OURS (grid-4 ringed = the committed object; Tier-1 solid/dashed); orange =
the Tier-2 degradation arms; magenta family = the BP+replay opponent (ER-strong load-bearing); black staircase =
the Pareto envelope; light-grey ticks = the sleep events; dash-dot = the joint-BP ceiling.
"""
from __future__ import annotations
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase9"))
import plot_p9   # noqa: E402  (inherit the canonical STYLE chain: plot_p9 <- plot_p8)

P10_NEW = dict(figsize_frontier=(7.5, 4.0), figsize_twin=(10, 4.0), figsize_strip=(10, 2.2))
STYLE = {**plot_p9.STYLE, **P10_NEW}

# entity -> (colour, linestyle, marker, ring?) — the P10-new encodings (result-format §A)
ENC = {
    "ours_g4":  ("#0b8f6a", "-", "o", True),   "g4":  ("#0b8f6a", "-", "o", True),
    "ours_g5":  ("#0b8f6a", "-", "^", False),
    "g5":       ("#0b8f6a", "-", "^", False),  "g6":  ("#0b8f6a", "--", "^", False),
    "g8":       ("#d9690a", "-", "s", False),  "g12": ("#d9690a", "-.", "v", False),
    "g16":      ("#d9690a", ":", "x", False),
    "g7":       ("#d9690a", "", "p", False),   "g13": ("#d9690a", "", "<", False),   # §10 E5 cliff probes
    "g14":      ("#d9690a", "", ">", False),   "g15": ("#d9690a", "", "d", False),   # (scatter-only)
    "er_strong": ("#8a1b8a", "-", "o", False), "er_budget": ("#8a1b8a", "--", "o", False),
    "agem":     ("#c98ac9", "-", "s", False),  "derpp": ("#6a1b6a", "-", "^", False),
    "gdumb":    ("#7f7f7f", "-", "D", False),  "naive": ("#111111", ":", None, False),
    "joint":    ("#111111", "-.", None, False),
    "clean":    ("#0b8f6a", "-", "o", False),  "iid": ("#2c6fbf", "-", "s", False),
    "directional": ("#d62728", "-", "^", False), "adc3b": ("#d9690a", "-", "x", False),
    "nuisance": ("#7f7f7f", "--", "D", False),
}
_LBL = {"ours_g4": "OURS grid-4", "ours_g5": "OURS grid-5", "g4": "OURS g4", "g5": "OURS g5", "g6": "OURS g6",
        "g8": "OURS g8 (Tier-2)", "g12": "OURS g12 (Tier-2)",
        "g16": "OURS g16 (Tier-2)", "g7": "OURS g7 (probe)", "g13": "OURS g13 (probe)",
        "g14": "OURS g14 (probe)", "g15": "OURS g15 (probe)",
        "er_strong": "ER-strong", "er_budget": "ER-budget", "agem": "A-GEM",
        "derpp": "DER++", "gdumb": "GDumb", "naive": "naive-BP", "joint": "joint-BP ceiling"}
plt.rcParams.update({"font.family": STYLE["font"], "font.size": STYLE["base"],
                     "figure.dpi": STYLE["dpi"], "savefig.dpi": STYLE["dpi"],
                     "axes.grid": True, "grid.color": STYLE["grid"], "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none",
                     "savefig.transparent": True})


def _enc(name):
    return ENC.get(name, ("#555555", "-", None, False))


def _keys(d):
    return d.files if hasattr(d, "files") else list(d)


def _names(d, key):
    return [h.decode() if isinstance(h, bytes) else str(h) for h in d[key]] if key in _keys(d) else []


def _med(x):
    return float(np.median(np.atleast_1d(np.asarray(x, float))))


def _iqr(x):
    x = np.atleast_1d(np.asarray(x, float))
    return np.percentile(x, 25), np.percentile(x, 75)


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    fig.tight_layout(); fig.savefig(p); plt.close(fig)
    return p


def _lbl(k):
    return _LBL.get(k, k)


# ============================================================ FIGHT (P10.1 headline)
def fig_fight(d, out):
    if "learners" not in _keys(d):
        return []
    learners = _names(d, "learners")
    fig, (axA, axE) = plt.subplots(1, 2, figsize=STYLE["figsize_twin"])
    x = np.arange(len(learners))
    for i, lr in enumerate(learners):
        col, ls, mk, ring = _enc(lr)
        acc = np.atleast_1d(np.asarray(d[f"acc_{lr}"], float))
        axA.bar(i, np.median(acc), color=col, width=0.7,
                yerr=[[np.median(acc) - np.percentile(acc, 25)], [np.percentile(acc, 75) - np.median(acc)]],
                capsize=3, edgecolor=("#000000" if ring else "none"), linewidth=1.5 if ring else 0)
    if "acc_joint" in _keys(d):
        axA.axhline(_med(d["acc_joint"]), color="#111111", ls="-.", lw=1.2, label="joint-BP ceiling")
        axA.legend(fontsize=7)
    axA.set_xticks(x); axA.set_xticklabels([_lbl(l) for l in learners], rotation=40, ha="right", fontsize=7)
    axA.set_ylabel("final AA (continual home)"); axA.set_title("accuracy — OURS(g4) vs the budgeted racer field")
    axA.grid(axis="x", visible=False)
    for i, lr in enumerate(learners):
        col = _enc(lr)[0]
        for sub, hatch, a in (("analog", "", 0.9), ("digital", "//", 0.5)):
            k = f"energy_{lr}_{sub}"
            if k in _keys(d):
                e = _med(d[k]); axE.bar(i + (0.2 if sub == "digital" else -0.2), e, width=0.38, color=col,
                                        alpha=a, hatch=hatch)
    axE.set_yscale("log"); axE.set_xticks(x)
    axE.set_xticklabels([_lbl(l) for l in learners], rotation=40, ha="right", fontsize=7)
    axE.set_ylabel("metered energy (pJ; solid=analog, hatch=digital)")
    axE.set_title("energy — same-substrate is the load-bearing cut"); axE.grid(axis="x", visible=False)
    fig.suptitle("FIGHT — does OURS(grid-4) match a budgeted ER on accuracy at lower energy?", fontsize=10)
    return [_save(fig, out, "FIGHT.png")]


# ============================================================ CADENCE-FRONTIER (P10.2)
def fig_cadence_frontier(d, out):
    if "grids" not in _keys(d):
        return []
    grids = _names(d, "grids")
    fig, (axL, axR) = plt.subplots(1, 2, figsize=STYLE["figsize_frontier"])
    for g in grids:
        col, ls, mk, ring = _enc(g)
        acc = np.atleast_1d(np.asarray(d[f"acc_{g}"], float)); en = np.atleast_1d(np.asarray(d[f"energy_{g}"], float))
        axL.scatter(_med(en), _med(acc), c=col, marker=mk or "o", s=90 if ring else 55,
                    edgecolors=("#000000" if ring else col), linewidths=1.5 if ring else 0.8, zorder=3,
                    label=_lbl(g))
    axL.set_xscale("log"); axL.set_xlabel("metered energy (pJ)"); axL.set_ylabel("final AA")
    axL.set_title("cost-frontier (g4 ringed = committed)", fontsize=9); axL.legend(fontsize=6.5, loc="best")
    xs = np.arange(len(grids))
    for xi, g in zip(xs, grids):
        col = _enc(g)[0]; bw = np.atleast_1d(np.asarray(d[f"bwtworst_{g}"], float))
        axR.bar(xi, _med(bw), color=col, width=0.7,
                yerr=[[_med(bw) - np.percentile(bw, 25)], [np.percentile(bw, 75) - _med(bw)]], capsize=3)
    axR.axhline(-float(d["delta_acc"]) if "delta_acc" in _keys(d) else -0.02, color="#d62728", ls=":", lw=1.0)
    axR.axhline(0.0, color="#111111", lw=0.8)
    axR.set_xticks(xs); axR.set_xticklabels([_lbl(g) for g in grids], rotation=30, fontsize=7)
    axR.set_ylabel("worst-point BWT"); axR.set_title("Tier-1 sweet spot vs Tier-2 break", fontsize=9)
    axR.grid(axis="x", visible=False)
    fig.suptitle(f"CADENCE-FRONTIER — the frozen object as a {len(grids)}-point cost-frontier family", fontsize=10)
    return [_save(fig, out, "CADENCE_FRONTIER.png")]


# ============================================================ GAUNTLET (THE money figure, P10.3)
def fig_gauntlet(d, out):
    if "domains" not in _keys(d):
        return []
    domains = _names(d, "domains"); cfgs = _names(d, "gauntlet_cfgs")
    D = len(domains); x = np.arange(D)
    fig, (axT, axB) = plt.subplots(2, 1, figsize=STYLE["figsize_twin"], sharex=True)
    for c in cfgs:
        k = f"allprev_{c}"
        if k not in _keys(d):
            continue
        col, ls, mk, ring = _enc(c)
        M = np.atleast_2d(np.asarray(d[k], float))                    # [S, D]
        med = np.median(M, 0)
        axT.plot(x, med, ls, color=col, marker=mk, ms=4, lw=STYLE["lw"], label=_lbl(c))
        if M.shape[0] > 1:
            axT.fill_between(x, np.percentile(M, 25, 0), np.percentile(M, 75, 0), color=col, alpha=STYLE["band_alpha"])
    for xi in x:                                                       # domain-boundary markers
        axT.axvline(xi, color="#7f7f7f", ls="--", lw=0.6, alpha=0.5)
    if "sleep_pos" in _keys(d):                                       # sleep-position overlay (fractional domain pos)
        for sp in np.atleast_1d(np.asarray(d["sleep_pos"], float)):
            axT.axvline(sp, color="#bdbdbd", ls="-", lw=0.7, alpha=0.5)
    axT.set_ylabel("all-prev AA")                                      # short label (the title carries the convention)
    axT.set_title("retention across domains — worst pre-sleep all-prev AA (sleep ticks light-grey)")
    axT.legend(fontsize=6.5, ncol=2, loc="best")
    for c in cfgs:
        k = f"cumenergy_{c}_analog"
        if k not in _keys(d):
            continue
        col = _enc(c)[0]
        M = np.atleast_2d(np.asarray(d[k], float)); axB.plot(x, np.median(M, 0), "-", color=col, lw=STYLE["lw"],
                                                             marker=_enc(c)[2], ms=3)
    axB.set_yscale("log"); axB.set_xticks(x); axB.set_xticklabels(domains, rotation=30, fontsize=7)
    axB.set_xlabel("gauntlet domain (in order)"); axB.set_ylabel("cum. E (pJ)")   # short label — no y-label collision
    axB.set_title("cumulative metered energy (same-substrate)")
    fig.suptitle("GAUNTLET — 5 domains without forgetting, cheaper than BP (the money figure)", fontsize=10)
    return [_save(fig, out, "GAUNTLET.png")]


# ============================================================ GAUNTLET-STREAM (§10 ext — the per-batch view, P10.3)
def _gauntlet_stream_panel(d, out, *, pre, onset_key, dom_key, fname, suptitle):
    """Shared drawer for the per-batch stream view (forward + reversed): live-batch acc (thin, prequential) +
    seen-so-far all-domain acc (thick) for OURS(g4) vs ER-strong, sleep ticks + domain onsets; bottom = per-batch
    prefix-priced cumulative energy. `pre` = the arrays key prefix ('stream' / 'streamrev')."""
    if f"{pre}seen_g4" not in _keys(d):
        return []
    import warnings
    fig, (axT, axB) = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 2]})
    N = np.atleast_2d(np.asarray(d[f"{pre}seen_g4"], float)).shape[1]
    x = np.arange(N)
    for c in ("g4", "er_strong"):
        col = _enc("ours_g4" if c == "g4" else c)[0]
        L = np.atleast_2d(np.asarray(d[f"{pre}live_{c}"], float))
        S = np.atleast_2d(np.asarray(d[f"{pre}seen_{c}"], float))
        with warnings.catch_warnings():                                # step-0 live is NaN by construction (head unfit)
            warnings.simplefilter("ignore", RuntimeWarning)
            medL = np.nanmedian(L, 0); medS = np.nanmedian(S, 0)
            q25 = np.nanpercentile(S, 25, 0); q75 = np.nanpercentile(S, 75, 0)
        axT.plot(x, medL, "-", color=col, lw=0.8, alpha=0.4)           # thin = live batch (named in the title)
        axT.plot(x, medS, "-", color=col, lw=2.0, label=_lbl("ours_g4" if c == "g4" else c))
        if S.shape[0] > 1:
            axT.fill_between(x, q25, q75, color=col, alpha=STYLE["band_alpha"])
    if f"{pre}sleeps_g4" in _keys(d):                                  # sleep ticks (grid cadence — seed-invariant)
        sl = np.atleast_2d(np.asarray(d[f"{pre}sleeps_g4"], float))[0]
        for sp in np.where(sl > 0.5)[0]:
            axT.axvline(sp, color="#bdbdbd", ls="-", lw=0.7, alpha=0.5)
    onsets = np.atleast_1d(np.asarray(d[onset_key], int)) if onset_key in _keys(d) else []
    doms = _names(d, dom_key) or _names(d, "domains")
    for i, sp in enumerate(onsets):
        axT.axvline(sp, color="#7f7f7f", ls="--", lw=0.8); axB.axvline(sp, color="#7f7f7f", ls="--", lw=0.8)
        if i < len(doms):
            axT.text(sp + 0.8, 0.97, doms[i], fontsize=6.5, color="#555555",
                     ha="left", va="top", transform=axT.get_xaxis_transform())
    axT.set_ylabel("accuracy"); axT.legend(fontsize=7, loc="lower right")
    axT.set_title("batch-by-batch — live-batch acc (thin) vs all-seen-domains acc (thick); sleep ticks light-grey")
    for c in ("g4", "er_strong"):
        col = _enc("ours_g4" if c == "g4" else c)[0]
        k = f"{pre}cume_{c}_analog"
        if k in _keys(d):
            E = np.atleast_2d(np.asarray(d[k], float))
            axB.plot(x, np.median(E, 0), "-", color=col, lw=STYLE["lw"], label=_lbl(c))
    axB.set_yscale("log"); axB.set_xlabel("stream batch"); axB.set_ylabel("cum. E (pJ)")
    axB.set_title("per-batch cumulative metered energy (exact prefix pricing; sleeps cluster where they fire)")
    axB.legend(fontsize=6.5, loc="lower right")
    fig.suptitle(suptitle, fontsize=10)
    return [_save(fig, out, fname)]


def fig_gauntlet_stream(d, out):
    return _gauntlet_stream_panel(d, out, pre="stream", onset_key="stream_onsets", dom_key="domains",
                                  fname="GAUNTLET_STREAM.png",
                                  suptitle="GAUNTLET-STREAM — the in-domain vs domain-switch activity, batch by batch")


def fig_gauntlet_stream_rev(d, out):
    return _gauntlet_stream_panel(d, out, pre="streamrev", onset_key="streamrev_onsets", dom_key="domains_rev",
                                  fname="GAUNTLET_STREAM_REV.png",
                                  suptitle="GAUNTLET-STREAM-REV — the SAME view, domain order reversed "
                                           "(noised first) — §10 E6")


# ============================================================ SUBSTRATE (carried from plot_p8; re-metered)
def fig_substrate(d, out):
    if "substrate_bars" not in _keys(d):
        return []
    bars = np.atleast_2d(np.asarray(d["substrate_bars"], float))       # [4, S] rows: OURS-an, OURS-di, GD-an, GD-di
    labs = _names(d, "substrate_labels") or ["OURS-analog", "OURS-digital", "GD-analog", "GD-digital"]
    cols = ["#0b8f6a", "#7fcbb4", "#c98ac9", "#8a1b8a"]
    fig, ax = plt.subplots(figsize=STYLE["figsize_single"])
    for i in range(bars.shape[0]):
        m = np.median(bars[i]); ax.bar(i, m, color=cols[i % 4],
                                       edgecolor="#000000" if i == 0 else "none", linewidth=1.5 if i == 0 else 0)
    ax.set_yscale("log"); ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, rotation=30, fontsize=8)
    ax.set_ylabel("metered energy (pJ)")
    ttl = "SUBSTRATE — chip (OURS-analog) vs conventional GD-on-digital"
    if "substrate_total_win" in _keys(d):
        ttl += f"  (total {_med(d['substrate_total_win']):.1f}x)"
    ax.set_title(ttl, fontsize=9); ax.grid(axis="x", visible=False)
    return [_save(fig, out, "SUBSTRATE.png")]


# ============================================================ NOISE-SHOWCASE (P10.4)
def fig_noise_showcase(d, out):
    if "noise_envs" not in _keys(d):
        return []
    envs = _names(d, "noise_envs"); learners = _names(d, "noise_learners") or ["ours", "bp", "naive"]
    x = np.arange(len(envs)); w = 0.8 / len(learners)
    lc = {"ours": "#0b8f6a", "bp": "#8a1b8a", "naive": "#111111"}
    fig, ax = plt.subplots(figsize=STYLE["figsize_frontier"])
    for li, lr in enumerate(learners):
        vals = []
        for e in envs:
            k = f"dirret_{lr}_{e}"
            vals.append(_med(d[k]) if k in _keys(d) else 0.0)
        ax.bar(x + (li - (len(learners) - 1) / 2) * w, vals, width=w, color=lc.get(lr, "#555555"),
               label={"ours": "OURS-hardened", "bp": "BP+replay", "naive": "naive"}.get(lr, lr))
    ax.axhline(1.0, color="#111111", ls=":", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(envs, rotation=20, fontsize=8)
    ax.set_ylabel("directional retention (/ clean)"); ax.legend(fontsize=7)
    ax.set_title("NOISE-SHOWCASE — held-out battery; does the hardened cell hold the class DIRECTION?", fontsize=9)
    ax.grid(axis="x", visible=False)
    return [_save(fig, out, "NOISE_SHOWCASE.png")]


# ============================================================ PARETO (THE verdict, P10.6)
def fig_pareto(d, out):
    if "pareto_pts" not in _keys(d):
        return []
    pts = np.atleast_2d(np.asarray(d["pareto_pts"], float))            # [N,3] acc, energy, is_frontier
    labs = _names(d, "pareto_labels")
    fig, ax = plt.subplots(figsize=STYLE["figsize_frontier"])
    for i in range(len(pts)):
        nm = labs[i] if i < len(labs) else str(i)
        col, ls, mk, ring = _enc(nm)
        ax.scatter(pts[i, 1], pts[i, 0], c=col, marker=mk or "o", s=110 if ring else 60,
                   edgecolors=("#000000" if ring else col), linewidths=1.6 if ring else 0.8, zorder=3, label=_lbl(nm))
    fr = pts[pts[:, 2] > 0.5]
    if len(fr) > 1:
        order = np.argsort(fr[:, 1]); ax.step(fr[order, 1], fr[order, 0], where="post", color="#111111", lw=1.0,
                                              alpha=0.7, zorder=2)
    ax.set_xscale("log"); ax.set_xlabel("metered energy (pJ)"); ax.set_ylabel("final AA")
    ax.legend(fontsize=6, loc="best", ncol=2)
    ax.set_title("PARETO — where the whole object stands vs the field (hero ringed)", fontsize=9)
    return [_save(fig, out, "PARETO.png")]


# ============================================================ INV (every run)
def fig_inv(d, out):
    panels = [k for k in _keys(d) if k.startswith("inv_")]
    if not panels:
        return []
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(min(1.6 * n, 15), 2.3))
    if n == 1:
        axes = [axes]
    for ax, k in zip(axes, sorted(panels)):
        va = np.atleast_1d(np.asarray(d[k], float)).ravel(); name = k[len("inv_"):]
        if va.size > 1:
            ax.plot(np.arange(va.size), va, "-", color="#0b8f6a", lw=STYLE["lw"])
        else:
            ax.bar([name], [float(va[0])], color="#0b8f6a" if va[0] > 0.5 else "#d62728")
        ax.set_ylim(0, 1.15); ax.set_title(name, fontsize=6.5); ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelsize=5.5)
    fig.suptitle("INV — guards (all bit-exact) + fair-budget + freeze-content + fire/sleep economy", fontsize=10)
    return [_save(fig, out, "INV.png")]


_ALL = [fig_fight, fig_cadence_frontier, fig_gauntlet, fig_gauntlet_stream, fig_gauntlet_stream_rev, fig_substrate,
        fig_noise_showcase, fig_pareto, fig_inv]


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
