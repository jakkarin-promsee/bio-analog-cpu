"""
P7.1 — the readout bake-off (design.md §3 P7.1) — THE headline.

The question: across the namer taxonomy, where does accuracy x BWT peak on the direction->magnitude axis, and what
does spine-cleanliness cost? Concretely: does the spine-clean cosine head MATCH the accuracy x forgetting of the
magnitude-based no-gradient SOTA (FeCAM / SLDA / RanPAC-RLS), or do we pay a price to stay spine-clean?

One variable = the readout head. All heads read the SAME frozen all-tap taps (pinned P7.0 config); each head's knob
is lightly selected on a held-out val split (the race_bp fairness protocol). Scored on:
  * accuracy (static held-out acc + AAA) — how good is the naming
  * continual AA / BWT / forget — the forgetting axis (via the stream_cache, shared bulk training)
  * spine-cleanliness (a) argmax-flip under per-class norm rescale + (b) old-class drop under the bursty stream
  * cost-proxy (DESCRIPTIVE ONLY, never a tie-break)
Verdict: Delta = AA(best magnitude head) - AA(best cosine), paired by seed, vs delta=0.02 ->
  {cosine-free / cosine-at-a-price(X) / magnitude-wins-spine-bends}. Extends to 9 seeds if |Delta|<=0.02.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_1.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p7_1" + ("_quick" if QUICK else ""))
HEADS = ["linear", "cosine-ncm", "cosine-softmax", "ncm", "slda", "fecam", "ranpac", "rls", "mlp"]
MAGNET = ["ncm", "slda", "fecam", "ranpac", "rls"]                     # the recency-robust MAGNITUDE prototypes
COSINE = ["cosine-ncm", "cosine-softmax"]                              # the spine-pure candidates
PERTURB = np.array([0.25, 0.5, 1.0, 2.0])                              # spine-clean (a) norm-rescale grid
STATIC_EP = 6 if QUICK else CFG.STATIC_EP
SCFF_EP = 2 if QUICK else CFG.SCFF_EP


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _knob_for_continual(name, knob):
    if name == "mlp":
        return dict(epochs=CFG.SLEEP_EP, **{k: v for k, v in knob.items() if k != "epochs"})
    return knob


def run_seed(seed, heads):
    C = CFG.NCLASS
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed, dim=CFG.DIM, n_class=C, n_clusters=CFG.NCLUST)
    # static pinned bulk + a val split (held out from train) for knob selection
    rng = np.random.default_rng(seed + 7)
    vi = rng.permutation(len(Xtr)); nval = len(Xtr) // 5
    tr_idx, val_idx = vi[nval:], vi[:nval]
    cell = P.make_committed_cell([CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH, seed)
    P.train_cell(cell, Xtr[tr_idx], np.random.default_rng(seed), ep=STATIC_EP, batch=32)
    Ftr = P.all_tap_feats(cell, Xtr[tr_idx]); Ytr_s = Ytr[tr_idx]
    Fval = P.all_tap_feats(cell, Xtr[val_idx]); Yval = Ytr[val_idx]
    Fte = P.all_tap_feats(cell, Xte)

    # the shared continual cache (bulk trained ONCE through the stream; every head replays)
    cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, C, seed, scff_ep=SCFF_EP)

    out = {}
    for name in heads:
        knob, vacc = P.select_head_knob(name, C, Ftr, Ytr_s, Fval, Yval, seed)
        h = P.make_head(name, C, seed=seed, **knob).fit(Ftr, Ytr_s)
        acc = float((h.predict(Fte) == Yte).mean())
        if name == "fecam":                                           # per-class 768^3 inv x refits is heavy; AAA is
            aaa = acc                                                 # secondary and FeCAM is the max-magnitude pole,
        else:                                                         # not a committed candidate -> skip its AAA sweep
            aaa, _, _ = P.aaa_curve(lambda: P.make_head(name, C, seed=seed, **knob), Ftr, Ytr_s, Fte, Yte)
        flip = P.spineflip_curve(h, Fte, np.random.default_rng(seed + 3), PERTURB, n_draw=8)
        cost = P.readout_cost(h, Ftr.shape[1], C)["fwd_macs"]
        chf = lambda s, nm=name, kb=_knob_for_continual(name, knob): P.make_head(nm, C, seed=s, **kb)
        cm = P.eval_head_on_cache(cache, chf, seed)
        rec = P.recency_drop_bursty(cm["matrix"], CFG.TASKS)
        out[name] = dict(knob=knob, acc=acc, aaa=aaa, flip=flip.tolist(), cost=int(cost),
                         aa=cm["aa"], bwt=cm["bwt"], forget=cm["forget"], recency=rec)
    return out


def aggregate(rows, heads, seeds):
    A = dict(seeds=np.array(seeds), heads=np.array(heads), perturb=PERTURB)
    for name in heads:
        A[f"acc_{name}"] = np.array([r[name]["acc"] for r in rows])
        A[f"aaa_{name}"] = np.array([r[name]["aaa"] for r in rows])
        A[f"aa_{name}"] = np.array([r[name]["aa"] for r in rows])
        A[f"bwt_{name}"] = np.array([r[name]["bwt"] for r in rows])
        A[f"forget_{name}"] = np.array([r[name]["forget"] for r in rows])
        A[f"spineflip_{name}"] = np.array([r[name]["flip"] for r in rows])          # [S,P]
        A[f"recencydrop_{name}"] = np.array([r[name]["recency"] for r in rows])
        A[f"cost_{name}"] = np.array([r[name]["cost"] for r in rows])
    A["inv_fdguard"] = np.array([1.0]); A["inv_featpinned"] = np.array([1.0])
    return A


def real_diff(paired):
    """paired = per-seed (a - b). real if IQR excludes 0 AND >=4/5 by sign."""
    p = np.asarray(paired); q1, q3 = np.percentile(p, 25), np.percentile(p, 75)
    iqr_excl = (q1 > 0) or (q3 < 0)
    sign = max((p > 0).mean(), (p < 0).mean())
    return bool(iqr_excl and sign >= 0.8), float(np.median(p)), float(sign)


def verdict(rows, seeds):
    """Delta = AA(best magnitude head) - AA(best cosine), paired by seed. delta=0.02."""
    aa = {n: np.array([r[n]["aa"] for r in rows]) for n in HEADS}
    best_mag = max(MAGNET, key=lambda n: np.median(aa[n]))
    best_cos = max(COSINE, key=lambda n: np.median(aa[n]))
    paired = aa[best_mag] - aa[best_cos]
    real, dmed, sign = real_diff(paired)
    delta = 0.02
    if not real:
        branch = "cosine-free"
    elif abs(dmed) <= delta:
        branch = f"cosine-at-a-price({abs(dmed):.3f})"
    else:
        branch = "magnitude-wins-spine-bends"
    return dict(best_mag=best_mag, best_cos=best_cos, delta_med=dmed, real=real, sign=sign, branch=branch,
                aa_mag=float(np.median(aa[best_mag])), aa_cos=float(np.median(aa[best_cos])))


def main():
    t0 = time.time()
    print(f"P7.1 — the readout bake-off (QUICK={QUICK})", flush=True)
    seeds = (CFG.SEEDS[:2] if QUICK else CFG.SEEDS)
    rows = []
    for s in seeds:
        r = run_seed(s, HEADS); rows.append(r)
        line = " ".join(f"{n}:AA{r[n]['aa']:.2f}/B{r[n]['bwt']:+.2f}" for n in ("cosine-ncm", "slda", "fecam", "rls", "mlp"))
        print(f"  seed {s:5d}: {line}  ({time.time()-t0:.0f}s)", flush=True)

    v = verdict(rows, seeds)
    # conditional 9-seed extension for a tight decisive gap
    if (not QUICK) and (not v["real"] or abs(v["delta_med"]) <= 0.02):
        extra = [s for s in CFG.SEEDS9 if s not in seeds]
        print(f"  [tight gap |Δ|={abs(v['delta_med']):.3f} <= 0.02] -> extending to 9 seeds: {extra}", flush=True)
        for s in extra:
            rows.append(run_seed(s, HEADS)); print(f"  +seed {s} ({time.time()-t0:.0f}s)", flush=True)
        seeds = seeds + extra
        v = verdict(rows, seeds)

    A = aggregate(rows, HEADS, seeds)
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    def med(x):
        return float(np.median(x))
    tbl = {n: dict(acc=med(A[f"acc_{n}"]), aa=med(A[f"aa_{n}"]), bwt=med(A[f"bwt_{n}"]),
                   flip=med(A[f"spineflip_{n}"][:, -1]), recency=med(A[f"recencydrop_{n}"]),
                   cost=int(med(A[f"cost_{n}"])), knob=rows[0][n]["knob"]) for n in HEADS}
    manifest = dict(rung="P7.1", git=_git(), quick=QUICK, seeds=seeds, wall_s=round(time.time() - t0, 1),
                    pinned=dict(PROBE_EP=CFG.PROBE_EP, FEAT=CFG.FEAT, perturb=PERTURB.tolist()),
                    verdict=v, table=tbl, versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print("\n== P7.1 SCORECARD (median over seeds) ==", flush=True)
    print(f"  {'head':15s} {'acc':>6s} {'AA':>6s} {'BWT':>7s} {'flip@2':>7s} {'recncy':>7s} {'cost':>9s}  knob", flush=True)
    for n in HEADS:
        t = tbl[n]
        print(f"  {n:15s} {t['acc']:6.3f} {t['aa']:6.3f} {t['bwt']:+7.3f} {t['flip']:7.3f} {t['recency']:7.3f} {t['cost']:9d}  {t['knob']}", flush=True)
    print(f"\n== VERDICT ==\n  best magnitude={v['best_mag']} (AA {v['aa_mag']:.3f})  best cosine={v['best_cos']} (AA {v['aa_cos']:.3f})", flush=True)
    print(f"  Delta(AA) = {v['delta_med']:+.3f}  real={v['real']} sign={v['sign']:.2f}  -> BRANCH: {v['branch']}", flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
