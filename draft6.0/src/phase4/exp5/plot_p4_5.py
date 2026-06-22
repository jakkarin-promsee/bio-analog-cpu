"""P4.5 figures: python plot_p4_5.py figs_p4_5 — CONT (AA/BWT bars across difficulty + digits anchor), LINE.
OURS (contrast+sleep)=orange, GD-online (forget)=blue, contrast-nosleep (rot)=grey."""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL = {"contrast_sleep": "#d9690a", "gd": "#2c6fbf", "contrast_nosleep": "#9aa0a6"}
LAB = {"contrast_sleep": "OURS (contrast+coord+sleep)", "gd": "GD-online (forget)",
       "contrast_nosleep": "OURS no-sleep (rot)"}
CONDS = ["gd", "contrast_nosleep", "contrast_sleep"]


def draw_all(a, OUT):
    keys = [str(k) for k in a["keys"]]
    def val(key, c, m):
        k = f"{key}_{c}_{m}"
        return float(a[k]) if k in a.files else np.nan
    x = np.arange(len(keys)); wbar = 0.25

    # CONT: AA (left) and BWT (right) grouped bars per regime
    fig, (p1, p2) = plt.subplots(1, 2, figsize=(13, 4.6))
    for j, c in enumerate(CONDS):
        p1.bar(x + (j - 1) * wbar, [val(k, c, "final") for k in keys], wbar, color=COL[c], label=LAB[c])
        p2.bar(x + (j - 1) * wbar, [val(k, c, "bwt") for k in keys], wbar, color=COL[c], label=LAB[c])
    for p, ttl, yl in [(p1, "AA — final all-task accuracy [higher=better]", "average accuracy"),
                       (p2, "BWT — backward transfer [0=no forgetting, <0=forgets]", "BWT")]:
        p.set_xticks(x); p.set_xticklabels(keys); p.set_title(ttl, fontsize=9); p.set_ylabel(yl)
        p.grid(alpha=0.25, axis="y"); p.legend(fontsize=7.5)
    p2.axhline(0, color="k", lw=0.8)
    fig.suptitle("P4.5 CONT — does the continual win hold across difficulty? (ov = synthetic overlap)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "CONT.png"), dpi=130); plt.close(fig)

    # LINE: AA and BWT vs difficulty (synthetic overlaps only), the "does the win hold" view
    ov_keys = [k for k in keys if k.startswith("ov")]
    ov = [float(k[2:]) for k in ov_keys]
    if ov:
        fig, (q1, q2) = plt.subplots(1, 2, figsize=(11.5, 4.2))
        for c in CONDS:
            q1.plot(ov, [val(k, c, "final") for k in ov_keys], color=COL[c], lw=2.4, marker="o", ms=5, label=LAB[c])
            q2.plot(ov, [val(k, c, "bwt") for k in ov_keys], color=COL[c], lw=2.4, marker="o", ms=5, label=LAB[c])
        q1.set_xlabel("overlap (difficulty ->)"); q1.set_ylabel("AA"); q1.set_title("AA vs difficulty", fontsize=9)
        q2.set_xlabel("overlap (difficulty ->)"); q2.set_ylabel("BWT"); q2.set_title("BWT vs difficulty", fontsize=9)
        q2.axhline(0, color="k", lw=0.8)
        for q in (q1, q2):
            q.legend(fontsize=8); q.grid(alpha=0.25)
        fig.suptitle("P4.5 LINE — the continual win vs difficulty (synthetic stream)", fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "LINE.png"), dpi=130); plt.close(fig)
    print(f"  [plot] CONT/LINE -> {OUT}")


if __name__ == "__main__":
    draw_all(np.load(os.path.join(sys.argv[1], "arrays.npz"), allow_pickle=True), sys.argv[1])
