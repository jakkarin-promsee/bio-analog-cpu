"""
P2.0 figures — regenerate from arrays.npz, never from a live run (result-format reproducibility contract).
Emits: F3+ (the wall + GD-hidden envelope), DECIDE (lost/entangled), F6+ (width x depth), REPR/INV
(dead-units + effective-rank + goodness-gap per layer). House style: median line + IQR band, fixed dpi,
reference lines, caption = the one-sentence takeaway.

Run standalone:  python plot.py figs_exp0_synth
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_WALL, C_GD, C_DECIDE, C_REF = "#555555", "#e08214", "#117a78", "#1f5fbf"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": False, "savefig.facecolor": "white"})


def _band(ax, x, A, color, label, ls="-", marker="o"):
    m = np.median(A, 0); lo, hi = np.percentile(A, 25, 0), np.percentile(A, 75, 0)
    ax.plot(x, m, color=color, ls=ls, marker=marker, ms=4, label=label)
    ax.fill_between(x, lo, hi, color=color, alpha=0.18)
    return m


def draw_all(A, name, OUT):
    L = int(A["L"]); n = len(A["seeds"])
    wall = A["wall_probe"]; gdpl = A["gd_perlayer"]
    xw = np.arange(1, L + 1); xg = np.arange(1, gdpl.shape[1] + 1)
    chance = 1.0 / max(int(np.median(A["C"])), 2)
    gd_ceiling = float(np.median(A["gd_held"]))

    # ---- F3+ : the wall (single SCFF config) + GD-hidden & chance reference envelopes (the headline) ----
    # P2.0 scope = the WALL alone, the curve every Phase-2 lever must bend up. The candidate-fix overlay
    # (old-vs-new SCFF) is a P2.1 figure, not here. GD is matched-depth (L hidden) so it shares the 1..L
    # axis. Caption states the envelope gap (result-format: a curve with no envelope separation is moot).
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    mw = _band(ax, xw, wall, C_WALL, "deep SCFF (length-norm + squared) — the wall", ls="--", marker="o")
    mg = _band(ax, xg, gdpl, C_GD, "pure-GD hidden (envelope, flat-high)", ls="-", marker="s")
    ax.axhline(gd_ceiling, color=C_GD, ls=":", lw=1, alpha=0.7, label=f"GD held-out ceiling {gd_ceiling:.3f}")
    ax.axhline(chance, color="grey", ls=":", lw=1, label=f"chance {chance:.2f}")
    slope = float(np.polyfit(xw, mw, 1)[0]); env = float(np.median(mg) - np.median(mw))
    trend = "DECLINES" if slope < -0.001 else ("RISES" if slope > 0.001 else "is FLAT")
    ax.set_xticks(list(xw)); ax.set_xlabel("layer index (depth)")
    ax.set_ylabel("linear-probe acc (frozen 2k/2k, C=1.0)")
    ax.set_ylim(min(chance - 0.03, float(mw.min()) - 0.03), 1.0)
    ax.set_title(f"F3+ P2.0 [{name}]: SCFF separability {trend} with depth (slope {slope:+.4f}/layer)\n"
                 f"envelope gap to GD-hidden ~ {env:+.3f} = the headroom Phase 2 must climb (n={n})",
                 fontsize=10)
    # put the legend in the empty corner: top-right when curves sit low (the declining CIFAR wall),
    # bottom-left when they sit high (rising/flat synth) — so it never covers the data on either task.
    ax.legend(fontsize=7.5, loc="upper right" if float(np.median(mg)) < 0.6 else "lower left")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F3plus_wall.png")); plt.close(fig)

    # ---- DECIDE : max-power readout on frozen deep-SCFF + selectivity controls (lost/entangled) ----
    # SCFF vs the pure-GD ceiling decides lost/entangled; the RANDOM bar is the selectivity floor
    # (a high SCFF bar only means SCFF if it sits well above an untrained net of the same shape), and
    # the RAW bar checks the test is informative (if the probe solves it from raw input, DECIDE is moot).
    ds, gh, gap = A["decide_scff"], A["gd_held"], A["decide_gap"]
    has_ctrl = "decide_rand" in A.files
    verdict = "LOST (info destroyed -> fix must PRESERVE)" if np.median(gap) > 0.05 \
        else "ENTANGLED (info present -> fix is an INTERFACE)"
    if has_ctrl:
        dr, draw = A["decide_rand"], A["decide_raw"]
        sel = float(np.median(ds) - np.median(dr))
        series = [("max-power\non SCFF", ds, C_DECIDE), ("on RANDOM\n(selectivity floor)", dr, "#999999"),
                  ("on RAW\ninput", draw, "#9970ab"), ("pure-GD\n(ceiling)", gh, C_GD)]
    else:
        sel = None
        series = [("max-power\non SCFF", ds, C_DECIDE), ("pure-GD\n(ceiling)", gh, C_GD)]
    fig, ax = plt.subplots(figsize=(6.6 if has_ctrl else 5.2, 4.2))
    xs = np.arange(len(series)); vals = [np.median(s[1]) for s in series]
    errs = [[np.median(s[1]) - np.percentile(s[1], 25) for s in series],
            [np.percentile(s[1], 75) - np.median(s[1]) for s in series]]
    ax.bar(xs, vals, yerr=errs, capsize=5, color=[s[2] for s in series], alpha=0.85,
           tick_label=[s[0] for s in series])
    ax.axhline(chance, color="grey", ls=":", lw=1)
    ax.set_ylabel("held-out acc"); ax.set_ylim(0, 1.0)
    sel_txt = f"  |  selectivity (SCFF-RAND) {sel:+.3f}" if sel is not None else ""
    ax.set_title(f"DECIDE [{name}]: gap-vs-ceiling {np.median(gap):+.3f} -> {verdict}{sel_txt}",
                 fontsize=8)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "DECIDE.png")); plt.close(fig)

    # ---- F6+ : width x depth at equal budget ----
    ws, nd = A["ws_acc"], A["nd_acc"]; wd = A["wd_gap"]
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    vals = [np.median(ws), np.median(nd)]
    errs = [[np.median(ws) - np.percentile(ws, 25), np.median(nd) - np.percentile(nd, 25)],
            [np.percentile(ws, 75) - np.median(ws), np.percentile(nd, 75) - np.median(nd)]]
    ax.bar([0, 1], vals, yerr=errs, capsize=5, color=[C_REF, C_WALL], alpha=0.85,
           tick_label=[f"wide-shallow\n(~{int(np.median(A['ws_width']))}x2)", f"narrow-deep\n({int(A['width'])}x6)"])
    ax.set_ylabel("tapped-readout held-out acc"); ax.set_ylim(chance - 0.05, 1.0)
    ax.set_title(f"F6+ [{name}]: width x depth at equal budget — gap {np.median(wd):+.3f}\n"
                 f"(+ve = wide-shallow wins = the substrate-collision number)", fontsize=9)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F6plus_widthdepth.png")); plt.close(fig)

    # ---- REPR/INV : dead-units + effective-rank + goodness-gap per layer (the CAUSE) ----
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    _band(ax[0], xw, A["wall_dead"], C_WALL, "dead frac")
    ax[0].set_xlabel("layer"); ax[0].set_ylabel("dead-unit fraction")
    ax[0].set_title("INV dead units (squared-goodness deactivation)")
    _band(ax[1], xw, A["wall_erank"], C_DECIDE, "erank")
    ax[1].set_xlabel("layer"); ax[1].set_ylabel("effective rank")
    ax[1].set_title("REPR effective rank (collapse with depth?)")
    _band(ax[2], xw, A["wall_gap"], C_REF, "G_pos - G_neg")
    ax[2].axhline(0, color="grey", ls=":", lw=1)
    ax[2].set_xlabel("layer"); ax[2].set_ylabel("goodness gap")
    ax[2].set_title("INV goodness separation per layer")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "REPR_INV.png")); plt.close(fig)
    print(f"  figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    draw_all(np.load(os.path.join(d, "arrays.npz")), os.path.basename(d).replace("figs_exp0_", ""), d)
