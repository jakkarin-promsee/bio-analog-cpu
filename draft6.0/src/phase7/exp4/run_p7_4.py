"""
P7.4 — continual-safety: the home-turf GATE (design.md §3 P7.4) — un-skippable, the spine gate.

The question: does each commit-candidate head (+ its native online+sleep rule) PRESERVE the A6 sleep-recovery
continual win — the architecture's reason for being? Each head runs through the BUILT continual_safety_heads harness
(each head consolidates by its native sleep rule; the MLP head ≡ the old hard-coded path — the harness_equiv_guard),
vs the FLOOR-HEAD-ON-THE-SAME-BULK baseline (NOT "the P5 readout", which confounds head- and cell-forgetting).
5 seeds, never 3. Paired-sign veto: a head that is negative-BWT vs the floor baseline in >=4/5 paired seeds FAILS,
even if "within noise". Bulk training is shared across heads per seed (stream_cache ≡ continual_safety_heads,
P7.0-guarded), so the gate stays tractable.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_4.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p7_4" + ("_quick" if QUICK else ""))
# commit-candidates: the floor (baseline) + the spine candidates + the strong magnitude/analytic heads (incl the
# committed RanPAC + the cheaper no-grad alternative SLDA + the MLP anchor)
CANDIDATES = ["linear", "cosine-ncm", "cosine-softmax", "slda", "fecam", "ranpac", "rls", "mlp"]
BASELINE = "linear"                                                    # the floor-head-on-same-bulk gate baseline
SEEDS = CFG.SEEDS[:3] if QUICK else CFG.SEEDS
SCFF_EP = 2 if QUICK else CFG.SCFF_EP


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _knob_for_continual(name):
    kb = dict(CFG.COMMITTED_KNOBS.get(name, {}))                       # the P7.1-selected committed knob
    if name == "mlp":
        kb["epochs"] = CFG.SLEEP_EP
    return kb


def run_seed(seed):
    C = CFG.NCLASS
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed, dim=CFG.DIM, n_class=C, n_clusters=CFG.NCLUST)
    cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, C, seed, scff_ep=SCFF_EP)
    out = {}
    for name in CANDIDATES:
        chf = lambda s, nm=name, kb=_knob_for_continual(name): P.make_head(nm, C, seed=s, **kb)
        r = P.eval_head_on_cache(cache, chf, seed)
        out[name] = dict(aa=r["aa"], bwt=r["bwt"], forget=r["forget"])
    return out


def main():
    t0 = time.time()
    print(f"P7.4 — continual-safety GATE (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    print("  [harness] via stream_cache (P7.0-proven == continual_safety_heads bit-for-bit)", flush=True)
    rows = [run_seed(s) for s in SEEDS]
    for s, r in zip(SEEDS, rows):
        print(f"  seed {s:5d}: " + " ".join(f"{n}:B{r[n]['bwt']:+.3f}" for n in CANDIDATES) + f"  ({time.time()-t0:.0f}s)", flush=True)

    A = dict(seeds=np.array(SEEDS), heads=np.array(CANDIDATES))
    for n in CANDIDATES:
        A[f"aa_{n}"] = np.array([r[n]["aa"] for r in rows])
        A[f"bwt_{n}"] = np.array([r[n]["bwt"] for r in rows])
        A[f"forget_{n}"] = np.array([r[n]["forget"] for r in rows])
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    # the gate verdict: paired-sign veto vs the floor-head-on-same-bulk baseline
    base_bwt = A[f"bwt_{BASELINE}"]
    gate = {}
    for n in CANDIDATES:
        paired = A[f"bwt_{n}"] - base_bwt                             # >0 = better (less forgetting) than floor
        n_neg = int((paired < 0).sum())
        veto = (n == BASELINE) is False and n_neg >= max(4, int(np.ceil(0.8 * len(SEEDS))))
        gate[n] = dict(aa=float(np.median(A[f"aa_{n}"])), bwt=float(np.median(A[f"bwt_{n}"])),
                       forget=float(np.median(A[f"forget_{n}"])), vs_floor=float(np.median(paired)),
                       n_neg=n_neg, passes=bool(not veto))
    manifest = dict(rung="P7.4", git=_git(), quick=QUICK, seeds=SEEDS, wall_s=round(time.time() - t0, 1),
                    baseline=BASELINE, gate=gate, versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print(f"\n== P7.4 GATE (baseline = floor-head '{BASELINE}' on the same bulk; 5-seed paired-sign veto) ==", flush=True)
    print(f"  {'head':15s} {'AA':>6s} {'BWT':>7s} {'forget':>7s} {'vs-floor':>9s} {'neg/5':>6s}  verdict", flush=True)
    for n in CANDIDATES:
        gg = gate[n]
        tag = "(baseline)" if n == BASELINE else ("PASS" if gg["passes"] else "STRUCK — dents A6")
        print(f"  {n:15s} {gg['aa']:6.3f} {gg['bwt']:+7.3f} {gg['forget']:7.3f} {gg['vs_floor']:+9.3f} {gg['n_neg']:4d}/{len(SEEDS)}  {tag}", flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
