"""
P7.3 — the bursty-stream imbalance guard (design.md §3 P7.3).

The question: a drift-gated stream presents classes in BURSTS -> the head is chronically class-imbalanced. Does a
trained-softmax head develop the documented recency/magnitude bias that a cosine/prototype head dodges — and what is
the family-matched guard for the head we keep?

Our A6 mechanism normally consolidates on a BALANCED replay buffer (no imbalance). To probe the imbalance question
honestly we INDUCE it: a BOUNDED, recency-biased buffer (cap << all data -> recent classes dominate). Then, per head
family: trained head -> {none, logit-adjust, balanced-softmax, class-balanced-reservoir}; analytic head -> {none,
AIR}. Measure per-class accuracy split (old tasks vs recent tasks) at stream end = the task-recency-bias read.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_3.py [--quick]
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
import p7lib as P                                                       # noqa: E402
import p7cfg as CFG                                                     # noqa: E402
import plot_p7                                                          # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p7_3" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:3] if QUICK else CFG.SEEDS
SCFF_EP = 2 if QUICK else CFG.SCFF_EP
CAP = 500                                                             # bounded buffer -> recency-biased imbalance
# (head, family, guards): trained heads take logit-adj/bal-softmax/cbrs; analytic heads take AIR.
# RanPAC = the committed head (analytic); SLDA = the cheaper no-grad alternative; cosine/mlp = the trained comparators.
PROBES = [
    ("ranpac", "analytic", ["none", "air"]),
    ("slda", "analytic", ["none", "air"]),
    ("cosine-softmax", "trained", ["none", "logitadj", "balsoftmax", "cbrs"]),
    ("mlp", "trained", ["none", "logitadj", "cbrs"]),
]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _knob_c(name):
    kb = dict(CFG.COMMITTED_KNOBS.get(name, {}))
    if name == "mlp":
        kb["epochs"] = CFG.SLEEP_EP
    return kb


def bursty_eval(cache, head_name, C, seed, guard, cap):
    """Fit the head on a BOUNDED (recency-biased or class-balanced) buffer at stream end, apply the guard, return
    (old-task acc, recent-task acc) = the task-recency-bias split."""
    T = len(cache)
    FBf, YBf = cache[T - 1]["FB"], cache[T - 1]["YB"]
    if guard == "cbrs":
        FB, YB = P.class_balanced_reservoir(FBf, YBf, C, cap, np.random.default_rng(seed))
    else:
        FB, YB = FBf[-cap:], YBf[-cap:]                              # naive bounded buffer = recent-heavy
    counts = np.bincount(YB, minlength=C).astype(float)
    head = P.make_head(head_name, C, seed=seed, **_knob_c(head_name)).fit(FB, YB)
    if guard == "air":
        head = P.air_rectify(head, counts)
    accs = []
    for k in range(T):
        Fk, Yk = cache[T - 1]["te"][k]
        Z = head.logits(Fk)
        if guard == "logitadj":
            Z = P.logit_adjust(Z, counts)
        elif guard == "balsoftmax":
            Z = P.balanced_softmax(Z, counts)
        accs.append(float((Z.argmax(1) == Yk).mean()))
    old = float(np.mean(accs[:T // 2])); recent = float(np.mean(accs[T // 2:]))
    return old, recent


def run_seed(seed):
    C = CFG.NCLASS
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed, dim=CFG.DIM, n_class=C, n_clusters=CFG.NCLUST)
    cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, C, seed, scff_ep=SCFF_EP)
    out = {}
    for head, fam, guards in PROBES:
        for g in guards:
            out[f"{head}_{g}"] = bursty_eval(cache, head, C, seed, g, CAP)
    return out


def main():
    t0 = time.time()
    print(f"P7.3 — bursty-imbalance guard (QUICK={QUICK}, seeds={SEEDS}, cap={CAP})", flush=True)
    rows = [run_seed(s) for s in SEEDS]
    print(f"  ran {len(rows)} seeds ({time.time()-t0:.0f}s)", flush=True)

    A = dict(seeds=np.array(SEEDS))
    for head, fam, guards in PROBES:
        for g in guards:
            key = f"{head}_{g}"
            A[f"imbal_{key}"] = np.array([r[key] for r in rows])       # [S,2] old, recent
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    def med(k):
        v = np.atleast_2d(A[f"imbal_{k}"]); return float(np.median(v[:, 0])), float(np.median(v[:, 1]))
    summ = {}
    for head, fam, guards in PROBES:
        summ[head] = {}
        for g in guards:
            o, r = med(f"{head}_{g}"); summ[head][g] = dict(old=o, recent=r, gap=round(r - o, 4))
    manifest = dict(rung="P7.3", git=_git(), quick=QUICK, seeds=SEEDS, cap=CAP, wall_s=round(time.time() - t0, 1),
                    imbalance=summ, versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print("\n== P7.3 IMBALANCE (old vs recent task acc under a bounded recency-biased buffer) ==", flush=True)
    for head, fam, guards in PROBES:
        print(f"  {head} [{fam}]:", flush=True)
        base_gap = summ[head]["none"]["gap"]
        for g in guards:
            s = summ[head][g]
            fix = "" if g == "none" else f"  (gap {base_gap:+.3f} -> {s['gap']:+.3f})"
            print(f"     {g:12s} old={s['old']:.3f} recent={s['recent']:.3f} recency-gap={s['gap']:+.3f}{fix}", flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
