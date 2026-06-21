"""
P2.6 figures — regenerate from arrays.npz.
Emits: CONT (the veto — all-class acc trajectory + ACC/BWT bars, recipe vs single-block vs baselines),
DRIFT (per-task feature drift + SCFF all-class probe stability — the Phase-3 hand-off).
Run:  python plot_exp6.py figs_exp6_digits
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": True})
CONDS = ["gd", "single_sleep", "boosted_sleep", "boosted_nosleep"]
COL = {"gd": "#e08214", "single_sleep": "#1f5fbf", "boosted_sleep": "#117a78", "boosted_nosleep": "#c1272d"}
LAB = {"gd": "GD-online (forget)", "single_sleep": "single-block + sleep (P1 base)",
       "boosted_sleep": "boosted-read + sleep (RECIPE)", "boosted_nosleep": "boosted-read no-sleep (rot)"}


def draw_all(A, OUT):
    n = len(A["seeds"])
    tasks = [str(t) for t in A["tasks"]] if "tasks" in A.files else None
    T = A["gd__traj"].shape[1]; x = np.arange(1, T + 1)
    tasklab = tasks if tasks else [f"t{i}" for i in x]

    # ---- CONT : trajectory (left) + ACC/BWT bars (right) — the veto ----
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.5))
    for c in CONDS:
        Tr = A[f"{c}__traj"]; m = np.median(Tr, 0)
        ax[0].plot(x, m, color=COL[c], marker="o", label=LAB[c])
        ax[0].fill_between(x, np.percentile(Tr, 25, 0), np.percentile(Tr, 75, 0), color=COL[c], alpha=0.13)
    ax[0].set_xticks(x); ax[0].set_xticklabels(tasklab)
    ax[0].set_xlabel("tasks seen (class-incremental)"); ax[0].set_ylabel("all-class held-out acc")
    ax[0].set_title(f"CONT P2.6 [digits]: rot vs sleep recovery (n={n})"); ax[0].legend(fontsize=7.5)

    xs = np.arange(len(CONDS))
    fin = [np.median(A[f"{c}__final"]) for c in CONDS]
    bwt = [np.median(A[f"{c}__bwt"]) for c in CONDS]
    bwt_e = [[np.median(A[f"{c}__bwt"]) - np.percentile(A[f"{c}__bwt"], 25) for c in CONDS],
             [np.percentile(A[f"{c}__bwt"], 75) - np.median(A[f"{c}__bwt"]) for c in CONDS]]
    w = 0.38
    ax[1].bar(xs - w / 2, fin, w, color=[COL[c] for c in CONDS], alpha=0.9, label="final ACC")
    ax[1].bar(xs + w / 2, bwt, w, yerr=bwt_e, capsize=4, color=[COL[c] for c in CONDS], alpha=0.5,
              hatch="//", label="BWT")
    ax[1].axhline(0, color="black", lw=0.8)
    ax[1].set_xticks(xs); ax[1].set_xticklabels([LAB[c].split(" (")[0] for c in CONDS], rotation=20,
                                                ha="right", fontsize=7.2)
    rec, base = np.median(A["boosted_sleep__bwt"]), np.median(A["single_sleep__bwt"])
    verdict = "PASS (recipe preserves win)" if rec >= base - 0.02 else "FAIL (recipe worsens BWT)"
    ax[1].set_title(f"CONT veto: ACC + BWT — boosted-read BWT {rec:+.3f} vs single {base:+.3f}\n{verdict}",
                    fontsize=8.5)
    ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "CONT_veto.png")); plt.close(fig)

    # ---- DRIFT : feature drift + SCFF all-class probe stability (Phase-3 hand-off) ----
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.0))
    for c in ["single_sleep", "boosted_sleep", "boosted_nosleep"]:
        D = A[f"{c}__drift"]; m = np.median(D, 0)
        ax[0].plot(x, m, color=COL[c], marker="o", label=LAB[c])
    ax[0].set_xticks(x); ax[0].set_xticklabels(tasklab)
    ax[0].set_xlabel("tasks seen"); ax[0].set_ylabel("SCFF feature drift  ‖ĥ_t − ĥ_{t−1}‖")
    ax[0].set_title("DRIFT per task (Phase-3 gate hand-off — does it compound with blocks?)", fontsize=8.5)
    ax[0].legend(fontsize=7.5)
    for c in ["single_sleep", "boosted_sleep", "boosted_nosleep"]:
        P = A[f"{c}__scff_probe"]; m = np.median(P, 0)
        ax[1].plot(x, m, color=COL[c], marker="o", label=LAB[c])
        ax[1].fill_between(x, np.percentile(P, 25, 0), np.percentile(P, 75, 0), color=COL[c], alpha=0.13)
    ax[1].set_xticks(x); ax[1].set_xticklabels(tasklab)
    ax[1].set_xlabel("tasks seen"); ax[1].set_ylabel("SCFF all-class linear-probe acc")
    ax[1].set_title("Does SCFF itself forget? (flat = no — the recipe's continual virtue)", fontsize=8.5)
    ax[1].legend(fontsize=7.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "DRIFT.png")); plt.close(fig)
    print(f"  figures -> {OUT}")


if __name__ == "__main__":
    d = sys.argv[1]
    draw_all(np.load(os.path.join(d, "arrays.npz"), allow_pickle=True), d)
