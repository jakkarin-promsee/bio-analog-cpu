"""plot_p11 — the ONE Phase-11 plotting module (one function per figure code). STYLE = {**plot_p10.STYLE, **P11_NEW}.
No rung styles matplotlib inline. `regen(run_dir)` redraws every figure whose arrays are present."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase10"))
try:
    import plot_p10
    BASE = dict(getattr(plot_p10, "STYLE", {}))
except Exception:
    BASE = {}

P11_NEW = dict(ours_a="#0b8f6a", ours_b="#0b8f6a", proj="#4d7ea8", reservoir="#4d7ea8",
               nochange="#555555", sgd="#2f6f2f", frozen="#555555", bigbuf="#8a1b8a", anchor="#b8860b",
               er="#c1440e", chance="#999999", ceiling="#333333")
STYLE = {**BASE, **P11_NEW}
WIN, TIE, LOSS, FLOOR = "#0b8f6a", "#bcd9cf", "#e6b8d8", "#cccccc"


def _load(run_dir):
    d = np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True)
    return {k: d[k] for k in d.files}


def fig_decomp(run_dir, out=None):
    """DECOMP (P11.1) — Δbulk vs arena nonlinearity: home-AA bulk/proj/reservoir + the continual worst-BWT."""
    A = _load(run_dir)
    med = lambda k: float(np.median(A[k])) if k in A else np.nan
    arenas = ["synth", "mnist", "digits"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    x = np.arange(len(arenas)); w = 0.26
    bulk = [med(f"home_{a}_homeAA_bulk") for a in arenas]
    proj = [med(f"home_{a}_homeAA_proj") for a in arenas]
    resv = [med(f"home_{a}_homeAA_reservoir") for a in arenas]
    ax[0].bar(x - w, bulk, w, color=STYLE["ours_a"], label="bulk→namer (SCFF learned)")
    ax[0].bar(x, resv, w, color=STYLE["reservoir"], alpha=0.6, label="random-frozen-bulk (reservoir)")
    ax[0].bar(x + w, proj, w, color=STYLE["proj"], hatch="//", label="proj→namer (NO bulk — the strike)")
    for i, a in enumerate(arenas):
        ax[0].annotate(f"Δbulk\n{bulk[i]-proj[i]:+.2f}", (i, max(bulk[i], proj[i]) + 0.03), ha="center", fontsize=9,
                       color=STYLE["ours_a"] if bulk[i] > proj[i] else "#b03060")
    ax[0].set_xticks(x); ax[0].set_xticklabels(["synth-home\n(nonlinear)", "MNIST-40\n(moderate)", "digits\n(near-linear)"])
    ax[0].set_ylabel("clean home accuracy (SLDA)"); ax[0].set_ylim(0, 1.05)
    ax[0].set_title("Δbulk tracks arena NONLINEARITY (the strike-1 answer)"); ax[0].legend(fontsize=8, loc="upper left")
    ax[0].axhline(0.1, ls=":", c=STYLE["chance"], lw=1); ax[0].text(2.3, 0.11, "chance", fontsize=7, color=STYLE["chance"])
    # right: continual worst-BWT bulk vs proj on the gauntlets (safety is closed-form, NOT the bulk)
    ga = ["digits", "mnist"]; xg = np.arange(len(ga))
    wb = [med(f"gaunt_{a}_worst_bwt_bulk") for a in ga]; wp = [med(f"gaunt_{a}_worst_bwt_proj") for a in ga]
    ax[1].bar(xg - 0.2, wb, 0.4, color=STYLE["ours_a"], label="bulk→namer")
    ax[1].bar(xg + 0.2, wp, 0.4, color=STYLE["proj"], hatch="//", label="proj→namer (no bulk)")
    ax[1].set_xticks(xg); ax[1].set_xticklabels([f"{a} gauntlet" for a in ga])
    ax[1].set_ylabel("worst-point BWT (safety; 0 = no forgetting)")
    ax[1].set_title("continual SAFETY is closed-form + gate + sleep\n(proj→namer forgets no more than bulk)")
    ax[1].axhline(0, c="k", lw=0.8); ax[1].legend(fontsize=8)
    fig.suptitle("P11.1 DECOMPOSITION — 'Is it just SLDA?' → the bulk is the NONLINEAR learner; the SAFETY is the namer",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    out = out or os.path.join(run_dir, "DECOMP.png")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def fig_stream(run_dir, arena, out=None):
    """STREAM-<arena> (every arena) — per-batch prequential: OURS vs the STRONGER ER (the best BP baseline on the SAME
    data), with the no-change persistence floor as a horizontal reference + sleep ticks + block onsets. The two lines
    let an outsider read, batch-by-batch, where OURS is strong and where the tuned replay learner leads."""
    A = _load(run_dir)
    live = A.get(f"streamlive_ours_{arena}"); seen = A.get(f"streamseen_ours_{arena}")
    if live is None:
        return None
    er_live = A.get(f"streamlive_er_{arena}")
    sleeps = A.get(f"streamsleeps_ours_{arena}"); onsets = A.get(f"stream_onsets_{arena}")
    nochange = A.get(f"nochange_{arena}")
    fig, ax = plt.subplots(figsize=(11, 4.2)); x = np.arange(len(live))
    if er_live is not None:                                        # ER first, so OURS draws on top
        ax.plot(np.arange(len(er_live)), er_live, color=STYLE["er"], lw=1.1, alpha=0.6,
                label="ER-strong live-batch (best BP)")
    ax.plot(x, live, color=STYLE["ours_a"], lw=1.3, alpha=0.9, label="OURS live-batch (prequential)")
    if seen is not None:
        ax.plot(x, seen, color=STYLE["ours_a"], lw=2.2, label="OURS seen-so-far")
    if nochange is not None:
        ax.axhline(float(np.median(nochange)), ls="-.", c=STYLE["nochange"], lw=1.3, label="no-change (persistence)")
    if sleeps is not None:
        for s in np.where(np.asarray(sleeps) > 0)[0]:
            ax.axvline(s, color="#b8b8b8", lw=0.5, alpha=0.5)
    if onsets is not None:
        for o in np.asarray(onsets):
            ax.axvline(int(o), color="#d0a0a0", ls="--", lw=0.8, alpha=0.6)
    ax.set_xlabel("stream step (batch)"); ax.set_ylabel("accuracy"); ax.set_ylim(0, 1.02)
    ax.set_title(f"STREAM-{arena} — OURS vs ER-strong, batch-by-batch (grey=sleep, dashed=block onset)")
    ax.legend(fontsize=8, loc="lower right", ncol=2)
    fig.tight_layout(); out = out or os.path.join(run_dir, f"STREAM_{arena}.png")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def fig_fight(run_dir, arena, learners, out=None):
    """FIGHT-<arena> — prequential balanced accuracy per learner (OURS vs ER points vs baselines)."""
    A = _load(run_dir)
    vals = {}
    for L in learners:
        k = f"balacc_{L}_{arena}"
        if k in A:
            vals[L] = A[k]
    if not vals:
        return None
    fig, ax = plt.subplots(figsize=(max(6, 1.1 * len(vals)), 4.2))
    names = list(vals); x = np.arange(len(names))
    colmap = {"ours_a": STYLE["ours_a"], "ours_b": STYLE["ours_b"], "er_matched": STYLE["er"],
              "er_bigbuf": STYLE["bigbuf"], "sgd": STYLE["sgd"], "nochange": STYLE["nochange"],
              "frozen": STYLE["frozen"], "proj": STYLE["proj"], "naive": "#888888", "gdumb": "#aa8844"}
    meds = [float(np.median(vals[n])) for n in names]
    q1 = [float(np.percentile(vals[n], 25)) for n in names]; q3 = [float(np.percentile(vals[n], 75)) for n in names]
    cols = [colmap.get(n, "#666666") for n in names]
    ax.bar(x, meds, 0.6, color=cols, yerr=[np.array(meds) - q1, np.array(q3) - meds], capsize=3)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("prequential balanced accuracy"); ax.set_ylim(0, 1.02)
    ax.set_title(f"FIGHT-{arena}")
    fig.tight_layout(); out = out or os.path.join(run_dir, f"FIGHT_{arena}.png")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def fig_scaling(run_dir, out=None):
    """SCALING (P11.6) — 3 panels: (1) GD-share vs W measured vs the bench-pinned meter-derived shape; (2) accuracy vs
    W (capacity ablation @ D80) and vs D (recipe stretched); (3) substrate factor E(digital)/E(analog) vs W."""
    A = _load(run_dir)
    W = A.get("scale_W")
    if W is None:
        return None
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.3))
    # panel 1: GD-share vs W (measured vs pinned)
    ax[0].plot(W, A["gdshare_measured"], "o-", color=STYLE["ours_a"], lw=2, label="measured (this run)")
    if "gdshare_pinned" in A:
        ax[0].plot(W, A["gdshare_pinned"], "s--", color=STYLE["anchor"], lw=2, label="bench-pinned (meter-derived, P11.0)")
    ax[0].axhline(0.25, ls=":", c="#b03060", label="GD-share cap 0.25")
    ax[0].set_xlabel("width W (D=80 fixed)"); ax[0].set_ylabel("GD-share"); ax[0].legend(fontsize=8)
    ax[0].set_title("economy vs scale: GD-share RISES with W\n(measured confirms the pinned shape)")
    # panel 2: accuracy vs W and vs D
    ax[1].plot(W, A["acc_vs_W"], "o-", color=STYLE["ours_a"], lw=2, label="acc vs W (@ D=80)")
    if "scale_D" in A and "acc_vs_D" in A:
        ax2 = ax[1].twiny()
        ax2.plot(A["scale_D"], A["acc_vs_D"], "^--", color=STYLE["proj"], lw=2, label="acc vs D (recipe-W)")
        ax2.set_xlabel("input dim D (recipe-W)", color=STYLE["proj"])
        ax2.legend(fontsize=8, loc="lower right")
    ax[1].set_xlabel("width W"); ax[1].set_ylabel("gauntlet accuracy"); ax[1].legend(fontsize=8, loc="upper left")
    ax[1].set_title("accuracy vs capacity\n(does width buy the gap back?)")
    # panel 3: substrate factor vs W
    if "substrate_vs_W" in A:
        ax[2].plot(W, A["substrate_vs_W"], "o-", color="#5a3d8a", lw=2)
        ax[2].set_xlabel("width W"); ax[2].set_ylabel("substrate factor  E(digital)/E(analog)")
        ax[2].set_title("the analog crossbar advantage vs scale\n(non-decreasing = the chip holds)")
    fig.suptitle("P11.6 SCALING — capacity vs the economy/substrate (Fashion long gauntlet)", fontsize=12, y=1.03)
    fig.tight_layout(); out = out or os.path.join(run_dir, "SCALING.png")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def fig_crossover(run_dir, out=None):
    """CROSSOVER (P11.5) — analytic memory bytes-vs-C: a fixed-byte REPLAY buffer O(C) vs the PROTOTYPE+GRAM namer
    O(C*F + F^2); the crossover C* where the namer is the more memory-efficient representation. + measured
    worst-retention points at C=10/20 (OURS vs byte-matched ER — the dilution shows up as a widening gap)."""
    A = _load(run_dir)
    C = A.get("crossover_analytic_C")
    if C is None:
        return None
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
    rb = A["crossover_replay_bytes"]; pg = A["crossover_protogram_bytes"]
    ax[0].plot(C, rb, "-", color=STYLE["er"], lw=2, label="fixed-rate replay  O(C·k·F)")
    ax[0].plot(C, pg, "-", color=STYLE["ours_a"], lw=2, label="prototype+Gram  O(C·F + F²)")
    cross = np.where(pg < rb)[0]
    if len(cross):
        cstar = C[cross[0]]
        ax[0].axvline(cstar, ls=":", c="#333333", lw=1.2)
        ax[0].annotate(f"crossover C*≈{int(cstar)}", (cstar, pg[cross[0]]), fontsize=9,
                       xytext=(cstar + 6, pg[cross[0]] * 1.4), color="#333333")
    ax[0].set_xlabel("number of classes C"); ax[0].set_ylabel("memory (floats)"); ax[0].set_yscale("log")
    ax[0].legend(fontsize=8, loc="upper left")
    ax[0].set_title("memory fairness: prototype+Gram beats\nbyte-matched replay past C*")
    # measured retention
    Cm = A.get("crossover_measured_C")
    if Cm is not None:
        ax[1].plot(Cm, A["crossover_measured_ours"], "o-", color=STYLE["ours_a"], lw=2, label="OURS (prototype+Gram)")
        ax[1].plot(Cm, A["crossover_measured_er"], "s--", color=STYLE["er"], lw=2, label="byte-matched ER (replay)")
        ax[1].set_xlabel("number of classes C"); ax[1].set_ylabel("worst-point retention")
        ax[1].set_xticks(Cm); ax[1].legend(fontsize=8); ax[1].set_ylim(0, 1.02)
        ax[1].set_title("measured retention vs C\n(replay dilutes as C grows)")
    fig.suptitle("P11.5 CROSSOVER — the class-count memory read", fontsize=12, y=1.03)
    fig.tight_layout(); out = out or os.path.join(run_dir, "CROSSOVER.png")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)
    return out


def fig_limit_map(map_rows, arenas, out, *, title="P11.9 LIMIT-MAP"):
    """LIMIT-MAP (P11.9 headline) — arenas × capability channels, 4-state cells (win/tie/loss/FLOOR) + numbers.
    `map_rows` = dict channel -> dict arena -> dict(state, label). `arenas` = ordered column list."""
    channels = list(map_rows)
    fig, ax = plt.subplots(figsize=(1.35 * len(arenas) + 3.5, 0.62 * len(channels) + 2))
    statecol = {"win": WIN, "tie": TIE, "loss": LOSS, "FLOOR": FLOOR, "": "#ffffff", "n/a": "#f4f4f4"}
    for ri, ch in enumerate(channels):
        for ci, ar in enumerate(arenas):
            cell = map_rows[ch].get(ar, {"state": "", "label": ""})
            ax.add_patch(plt.Rectangle((ci, len(channels) - 1 - ri), 1, 1,
                                       facecolor=statecol.get(cell["state"], "#ffffff"), edgecolor="white", lw=2,
                                       hatch=("xx" if cell["state"] == "FLOOR" else None)))
            txt = cell.get("label", "")
            ax.text(ci + 0.5, len(channels) - 1 - ri + 0.5, txt, ha="center", va="center", fontsize=7.5)
    ax.set_xlim(0, len(arenas)); ax.set_ylim(0, len(channels))
    ax.set_xticks(np.arange(len(arenas)) + 0.5); ax.set_xticklabels(arenas, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(channels)) + 0.5); ax.set_yticklabels(channels[::-1], fontsize=9)
    ax.set_xticks(np.arange(len(arenas) + 1), minor=True); ax.set_yticks(np.arange(len(channels) + 1), minor=True)
    ax.tick_params(length=0)
    from matplotlib.patches import Patch
    leg = [Patch(facecolor=WIN, label="win"), Patch(facecolor=TIE, label="tie"),
           Patch(facecolor=LOSS, label="loss"), Patch(facecolor=FLOOR, hatch="xx", label="FLOOR")]
    ax.legend(handles=leg, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=8, frameon=False)
    ax.set_title(title, fontsize=12)
    fig.tight_layout(); fig.savefig(out, dpi=120, bbox_inches="tight"); plt.close(fig)
    return out


def regen(run_dir):
    outs = []
    A = _load(run_dir)
    if any(k.startswith("home_synth") for k in A):
        outs.append(fig_decomp(run_dir))
    for arena in ["gas", "har", "electric", "covtype", "mnist", "xdata"]:
        if f"streamlive_ours_{arena}" in A:
            outs.append(fig_stream(run_dir, arena))
    if "scale_W" in A:
        outs.append(fig_scaling(run_dir))
    if "crossover_analytic_C" in A:
        outs.append(fig_crossover(run_dir))
    return [o for o in outs if o]


if __name__ == "__main__":
    import sys
    print(regen(sys.argv[1]))
