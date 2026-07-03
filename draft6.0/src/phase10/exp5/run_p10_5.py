"""
P10.5 — A5 natural multi-class confirm (design §3 P10.5). The fight on data a professor recognizes: 8x8 DIGITS
projected to the shared 40-D bulk input, class-incremental (CISTREAM_TASKS = 5 tasks of 2), OURS(grid-4) vs
ER-strong / ER-budget / naive + the joint-BP ceiling. Synthetic OVERSTATES static gaps both ways (threat d), so the
recognizable-data read is the honest confirm: does the P10.1 synthetic verdict hold on natural data, and in which
direction did synthetic distort the gap? The gauntlet (P10.3) is already natural domain-IL digits; this adds the
class-IL natural leg.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_5.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p10lib as P                                                     # noqa: E402
import p10cfg as CFG                                                   # noqa: E402
import p10run as R                                                     # noqa: E402
import plot_p10                                                        # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p10_5" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
ROSTER = ["ours_g4", "er_strong", "er_budget", "naive"]


def digits40(seed):
    """8x8 digits projected to the shared 40-D input via the SAME pinned 64->40 Gaussian as the gauntlet (K5)."""
    from sklearn.datasets import load_digits
    d = load_digits(); X = (d.data / 16.0).astype(np.float64); Y = d.target.astype(np.int64)
    Pj = np.random.default_rng(12345).standard_normal((64, CFG.DIM)) / np.sqrt(64.0)
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    ntr = min(CFG.NTR, len(X) - 500)
    tr, te = idx[:ntr], idx[ntr:ntr + 500]
    return X[tr] @ Pj, Y[tr], X[te] @ Pj, Y[te]


def load_er_cfg():
    m = json.load(open(os.path.join(_HERE, "..", "exp0", "figs_p10_0", "manifest.json")))
    return m["er_strong_config"]


def main():
    t0 = time.time()
    print(f"P10.5 — A5 natural (digits->40) confirm  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)
    er = load_er_cfg()
    field = {"er_strong": dict(policy="er", bp_dims=er["bp_dims"], lr=er["lr"], l2=er["l2"], replay=er["replay"], cap=er["buffer_cap"]),
             "er_budget": dict(policy="er", bp_dims=er["bp_dims"], lr=er["lr"], l2=er["l2"], replay=CFG.ER_BUDGET_REPLAY, cap=CFG.PROBE_N),
             "naive": dict(policy="naive", bp_dims=[CFG.DIM, 64, 64, CFG.NCLASS], lr=er["lr"], l2=er["l2"], replay=0, cap=0)}

    acc = {k: [] for k in ROSTER}; en_an = {k: [] for k in ROSTER}; en_di = {k: [] for k in ROSTER}
    bwt = {k: [] for k in ROSTER}; joint = []
    for s in SEEDS:
        Xtr, Ytr, Xte, Yte = digits40(s)
        stream = P.make_lifelong_stream(Xtr, Ytr, Xte, Yte, CFG.TASKS, s, CFG, quick=QUICK)
        cache = P.build_cache_p9(P.make_committed_cell, stream, s, CFG, store_reps=False, quick=QUICK)
        hf = R.committed_hf(s)
        ours = P.ours_bundle(cache, hf, CFG, 4)
        acc["ours_g4"].append(ours["aa"]); bwt["ours_g4"].append(ours["worst_bwt"])
        en_an["ours_g4"].append(P.ours_stream_energy(CFG, cache, ours, substrate="analog")["total"])
        en_di["ours_g4"].append(P.ours_stream_energy(CFG, cache, ours, substrate="digital")["total"])
        n_steps = len(cache["steps"])
        for k in ROSTER[1:]:
            c = field[k]
            m = P.run_bp_stream(stream, c["policy"], c["bp_dims"], CFG, s, lr=c["lr"], l2=c["l2"],
                                replay=c["replay"], buffer_cap=c["cap"])
            acc[k].append(m["aa"]); bwt[k].append(m["worst_bwt"])   # worst-pre-sleep for ALL (R6; consistent with OURS)
            en_an[k].append(P.bp_stream_energy(CFG, c["bp_dims"], c["policy"], n_steps=n_steps, replay=c["replay"], substrate="analog")["total"])
            en_di[k].append(P.bp_stream_energy(CFG, c["bp_dims"], c["policy"], n_steps=n_steps, replay=c["replay"], substrate="digital")["total"])
        joint.append(P.joint_bp_ceiling(stream, CFG, CFG.DIM, CFG.NCLASS, s))
        print(f"  seed {s}: OURS={acc['ours_g4'][-1]:.3f} ER-strong={acc['er_strong'][-1]:.3f} "
              f"ER-budget={acc['er_budget'][-1]:.3f} naive={acc['naive'][-1]:.3f} joint={joint[-1]:.3f}", flush=True)
        del cache

    dacc = CFG.DELTA_ACC; gap = R.med(acc["er_strong"]) - R.med(acc["ours_g4"])
    verdict = (f"natural CONFIRMS P10.1: ER-strong edges OURS by {gap:+.3f}" if gap > dacc else
               f"natural TIE (gap {gap:+.3f} <= delta)" if abs(gap) <= dacc else
               f"OURS leads on natural by {-gap:+.3f}")
    print(f"\n  == A5 NATURAL (digits->40, delta_acc={dacc}) ==", flush=True)
    print(f"  {'learner':10s} {'acc':>18} {'E(analog)':>11} {'E(digital)':>11} {'BWT':>8}", flush=True)
    for k in ROSTER:
        print(f"  {k:10s} {R.fmt(acc[k]):>18} {R.med(en_an[k]):>11.3e} {R.med(en_di[k]):>11.3e} {R.med(bwt[k]):>+8.3f}", flush=True)
    print(f"  joint ceiling {R.fmt(joint)} | VERDICT: {verdict}", flush=True)

    A = dict(seeds=np.array(SEEDS), learners=np.array(ROSTER), acc_joint=np.array(joint), **R.inv_arrays(g))
    for k in ROSTER:
        A[f"acc_{k}"] = np.array(acc[k]); A[f"bwt_{k}"] = np.array(bwt[k])
        A[f"energy_{k}_analog"] = np.array(en_an[k]); A[f"energy_{k}_digital"] = np.array(en_di[k])
    man = R.base_manifest("P10.5", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          data="digits->40 class-IL", verdict=verdict, joint=R.fmt(joint),
                          summary={k: dict(acc=R.fmt(acc[k]), e_analog=R.med(en_an[k]), e_digital=R.med(en_di[k]),
                                           bwt=R.fmt(bwt[k])) for k in ROSTER})
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.5 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
