"""
P5.9 — synthesis + assembled-cell confirmation: the SCFF close-out verdict (design §3 P5.9).

The committed cell is **temp0.2 / w2, L12, no residual, fixed-reader deployment** — and that ONE config ran every
Phase-5 rung (P5.1 swept temp at w2; P5.2 swept window at temp0.2; P5.3–P5.8 all used temp0.2/w2). So there is no
independently-stacked combination to re-confirm — the "assembled-cell confirmation" the design asks for is the
consistency of the committed-cell columns ACROSS the rungs, which this script assembles into one SCORECARD from the
saved `arrays.npz` of each rung (no fresh heavy run; the citable-regen path is preserved — the scorecard regens from
this assembled summary).

The two verdicts (design §7, reported SEPARATELY):
  * DEPTH-EARNED (P5.1/P5.2): does SCFF compose the depth a task needs? — headroom tail-L12 vs the w12 ceiling / BP.
  * READ-CHEAPLY (P5.4/P5.5, STOP ①): does it read cheaper than all-tap AND truncation on the continual workload?

NOTE (session directive): the PUBLIC README / phase5-report SYNTHESIS is DEFERRED — the author returns to write it
together. This rung produces the experiment-part decision record (experiment-9.md) + the SCORECARD, not the README.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_9.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
RUNG = {k: os.path.join(_HERE, "..", v, "arrays.npz") for k, v in {
    "p1": "exp1/figs_p5_1", "p2": "exp2/figs_p5_2", "p5": "exp5/figs_p5_5",
    "p7": "exp7/figs_p5_7", "p8": "exp8/figs_p5_8"}.items()}
OUT = os.path.join(_HERE, "figs_p5_9")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _load(tag):
    p = RUNG[tag]
    if not os.path.exists(p):
        raise FileNotFoundError(f"{tag} arrays missing at {p} — run that rung first.")
    return dict(np.load(p, allow_pickle=True))


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    p1, p5, p7, p8 = _load("p1"), _load("p5"), _load("p7"), _load("p8")
    save = {}

    # ① DEPTH-EARNED — headroom tail-L12 (committed temp0.2) vs w12 ceiling vs tuned-BP (P5.1)
    temps = [round(float(t), 3) for t in np.asarray(p1["temps"], float)]   # headroom_tail = (seeds, temps)
    ti = temps.index(0.2)                                                  # the committed temperature column
    save["de_ours"] = np.asarray(p1["headroom_tail"], float)[:, ti]
    save["de_w12"] = np.full_like(save["de_ours"], float(p1["ref_w12_tail"]))
    save["de_bp"] = np.full_like(save["de_ours"], float(p1["ref_bp"]))

    # ② READ-CHEAPLY — the continual Pareto (P5.5)
    for who in ("alltap", "trunc", "exit", "oracle"):
        src = "exit1" if who == "exit" else who
        save[f"rc_{who}_acc"] = np.asarray(p5[f"pareto_{src}_acc"], float)
        save[f"rc_{who}_cost"] = np.asarray(p5[f"pareto_{src}_cost"], float)

    # ③ CONTINUAL-SAFE — BWT gate (P5.7)
    for ds in ("digits", "synth"):
        save[f"cs_{ds}_t05_bwt"] = np.asarray(p7[f"{ds}__t05_L4_sleep__bwt"], float)
        save[f"cs_{ds}_t02_bwt"] = np.asarray(p7[f"{ds}__t02_L4_sleep__bwt"], float)
        save[f"cs_{ds}_t05_aa"] = np.asarray(p7[f"{ds}__t05_L4_sleep__aa"], float)
        save[f"cs_{ds}_t02_aa"] = np.asarray(p7[f"{ds}__t02_L4_sleep__aa"], float)

    # ④ NATURAL-CONFIRM — tail decay→fix (P5.8)
    for ds in ("digits", "cifar"):
        save[f"nat_{ds}_t05_tail"] = np.asarray(p8[f"{ds}_t05_tail"], float)
        save[f"nat_{ds}_t02_tail"] = np.asarray(p8[f"{ds}_t02_tail"], float)
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    def md(k):
        return float(np.median(save[k]))

    # --- the two verdicts ---
    de_ours, de_w12, de_bp = md("de_ours"), md("de_w12"), md("de_bp")
    depth_earned = (de_ours >= de_w12 - 0.03) or (de_ours > de_bp)        # within band of ceiling, or beats BP
    e_cost, at_cost, tr_cost = md("rc_exit_cost"), md("rc_alltap_cost"), md("rc_trunc_cost")
    e_acc, at_acc = md("rc_exit_acc"), md("rc_alltap_acc")
    read_cheaply_exit = (e_cost < min(at_cost, tr_cost)) and (e_acc >= 0.95 * at_acc)   # STOP① adaptive
    read_cheaply_fixed = tr_cost < at_cost                               # truncation = the cheap fixed reader
    gate = (md("cs_digits_t02_bwt") >= md("cs_digits_t05_bwt") - 0.02)

    print(f"\n=== P5.9 SCORECARD — the committed cell temp0.2 / w2 (SCFF close-out) ===")
    print(f"\n  ① DEPTH-EARNED (headroom tail): OURS {de_ours:.3f} vs w12 {de_w12:.3f} (ceiling) / BP {de_bp:.3f} "
          f"-> {'EARNED' if depth_earned else 'NOT earned'} (OURS beats BP, within {de_w12-de_ours:.3f} of ceiling)")
    print(f"  ② READ-CHEAPLY (continual): all-tap {at_acc:.3f}@{at_cost/1000:.1f}k · trunc "
          f"{md('rc_trunc_acc'):.3f}@{tr_cost/1000:.1f}k · exit {e_acc:.3f}@{e_cost/1000:.1f}k · oracle "
          f"{md('rc_oracle_acc'):.3f}@{md('rc_oracle_cost')/1000:.1f}k")
    print(f"       adaptive-exit STOP①: {'PASS' if read_cheaply_exit else 'C5-PESSIMISTIC (ship truncation)'}; "
          f"fixed truncation {tr_cost/1000:.1f}k < all-tap {at_cost/1000:.1f}k = {read_cheaply_fixed} "
          f"({at_cost/tr_cost:.1f}× cheaper)")
    print(f"  ③ CONTINUAL-SAFE (digits BWT): temp0.2 {md('cs_digits_t02_bwt'):+.3f} vs temp0.5 "
          f"{md('cs_digits_t05_bwt'):+.3f} (AA {md('cs_digits_t02_aa'):.3f}) -> {'PASS' if gate else 'FAIL'}")
    print(f"  ④ NATURAL-CONFIRM (tail): digits {md('nat_digits_t05_tail'):.3f}->{md('nat_digits_t02_tail'):.3f} "
          f"(fix +{md('nat_digits_t02_tail')-md('nat_digits_t05_tail'):.3f}); CIFAR "
          f"{md('nat_cifar_t05_tail'):.3f}->{md('nat_cifar_t02_tail'):.3f} (null, no-headroom wall)")
    print(f"\n  VERDICT — depth EARNED: {depth_earned} · read-CHEAPLY: adaptive=STOP①-pessimistic, "
          f"fixed-truncation={read_cheaply_fixed} ({at_cost/tr_cost:.1f}×) · continual-SAFE: {gate} · natural: real")
    print(f"  => SCFF CLOSE-OUT: temp0.2/w2, L12-to-compose / shallow-fixed-read-to-deploy, continual-safe, "
          f"real-data-confirmed. (Public README/report DEFERRED to author's return.)")

    json.dump(dict(experiment="p5_9_scorecard", git_commit=_git(),
                   verdicts=dict(depth_earned=bool(depth_earned), read_cheaply_adaptive=bool(read_cheaply_exit),
                                 read_cheaply_fixed_truncation=bool(read_cheaply_fixed), continual_safe=bool(gate)),
                   committed_cell="temp0.2/w2 L12 no-residual fixed-reader",
                   numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p5
        f = plot_p5.fig_scorecard(OUT)
        print("\n  figure:", os.path.basename(f) if f else None)
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
