"""
P7.2 — multimodality / heterogeneity: the closed-form cliff (design.md §3 P7.2).

The question: are SCFF's per-class features ~unimodal in the NATURAL frozen tap space (one prototype suffices -> the
clean no-gradient story holds), or multi-modal (one mean underfits)? If multi-modal, how far up the fallback ladder
(mean -> SLDA -> FeCAM -> GKEAL -> mixture) must we climb before accuracy recovers — and does it stay CLOSED-FORM
(SLDA/FeCAM/GKEAL) or force a non-convex mixture?

Decision-bearer = the NATURAL tap space (digits). The synthetic multi-blob task is DEMOTED to apparatus sanity
(each class = several separated blobs so a single mean PROVABLY underfits — the ladder must recover it; outcome fixed
by construction, so it does NOT decide the committed modeling — only the natural-space probe licenses climbing).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_2.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p7_2" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
STATIC_EP = 6 if QUICK else CFG.STATIC_EP
LADDER = ["mean", "slda", "fecam", "gkeal", "mixture"]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _mixture_fit_predict(Ftr, Ytr, Fte, C, seed, k=3):
    """The non-convex last-resort: k sub-prototypes per class (numpy k-means), predict = nearest sub-prototype's class."""
    protos, plab = [], []
    for c in range(C):
        Fc = Ftr[Ytr == c]
        kk = min(k, max(1, len(Fc) // 5))
        if len(Fc) < kk or kk <= 1:
            protos.append(Fc.mean(0)[None, :] if len(Fc) else np.zeros((1, Ftr.shape[1]))); plab.append([c]); continue
        _, cent, _ = P._kmeans(Fc, kk, seed + c)
        protos.append(cent); plab.append([c] * kk)
    protos = np.concatenate(protos); plab = np.array(sum(plab, []))
    d = ((Fte[:, None, :] - protos[None, :, :]) ** 2).sum(2)          # [N, P]
    return plab[d.argmin(1)]


def _ladder_acc(rung, Ftr, Ytr, Fte, Yte, C, seed):
    if rung == "mean":
        h = P.make_head("ncm", C, seed=seed).fit(Ftr, Ytr)
    elif rung == "slda":
        h = P.make_head("slda", C, seed=seed, shrinkage=1e-2).fit(Ftr, Ytr)
    elif rung == "fecam":
        h = P.make_head("fecam", C, seed=seed, shrinkage=1.0).fit(Ftr, Ytr)
    elif rung == "gkeal":
        h = P.make_head("gkeal", C, seed=seed, gamma=0.1, ridge_lambda=1e1).fit(Ftr, Ytr)
    elif rung == "mixture":
        return float((_mixture_fit_predict(Ftr, Ytr, Fte, C, seed) == Yte).mean())
    return float((h.predict(Fte) == Yte).mean())


def _digits_taps(seed):
    Xtr, Ytr, Xte, Yte = P.load_digits_split(seed)
    cell = P.make_committed_cell([Xtr.shape[1]] + [CFG.WIDTH] * CFG.DEPTH, seed)
    P.train_cell(cell, Xtr, np.random.default_rng(seed), ep=STATIC_EP, batch=32)
    return P.all_tap_feats(cell, Xtr), Ytr, P.all_tap_feats(cell, Xte), Yte, 10


def _synthblob(seed):
    """Apparatus sanity: each class = ~3 separated blobs (n_clusters=30, n_class=10) -> a single mean PROVABLY
    underfits. RAW features (no bulk) so the ladder's recovery is a pure plumbing test of modeling capacity."""
    Xtr, Ytr, _ = P.make_gauss(3000, np.random.default_rng(seed), dim=CFG.DIM, n_class=10, n_clusters=30, overlap=0.5)
    Xte, Yte, _ = P.make_gauss(1500, np.random.default_rng(seed + 7), dim=CFG.DIM, n_class=10, n_clusters=30, overlap=0.5)
    return Xtr, Ytr, Xte, Yte, 10


def run_seed(seed):
    out = {}
    for ds, loader in (("digits", _digits_taps), ("synthblob", _synthblob)):
        Ftr, Ytr, Fte, Yte, C = loader(seed)
        nmodes = P.multimodality_probe(Ftr, Ytr, C, seed=seed, kmax=4)
        ladder = {r: _ladder_acc(r, Ftr, Ytr, Fte, Yte, C, seed) for r in LADDER}
        out[ds] = dict(nmodes=nmodes.tolist(), ladder=ladder)
    return out


def main():
    t0 = time.time()
    print(f"P7.2 — multimodality closed-form ladder (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    rows = [run_seed(s) for s in SEEDS]
    for s, r in zip(SEEDS, rows):
        dl = r["digits"]["ladder"]
        print(f"  seed {s:5d}: digits nmodes(mean)={np.mean(r['digits']['nmodes']):.2f}  ladder=" +
              " ".join(f"{k}:{dl[k]:.3f}" for k in LADDER) + f"  ({time.time()-t0:.0f}s)", flush=True)

    A = dict(seeds=np.array(SEEDS))
    for ds in ("digits", "synthblob"):
        for r in LADDER:
            A[f"mm_{r}_{ds}"] = np.array([row[ds]["ladder"][r] for row in rows])
    A["nmodes"] = np.array([rows[i]["digits"]["nmodes"] for i in range(len(rows))])   # [S,C] natural decider
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    def med_ladder(ds):
        return {r: float(np.median(A[f"mm_{r}_{ds}"])) for r in LADDER}
    dig = med_ladder("digits"); syn = med_ladder("synthblob")
    nmodes_med = float(np.median(A["nmodes"]))
    # decide: is natural multimodal? does a closed-form rung recover before mixture?
    dig_gain_cov = max(dig["slda"], dig["fecam"], dig["gkeal"]) - dig["mean"]
    dig_gain_mix = dig["mixture"] - max(dig["slda"], dig["fecam"], dig["gkeal"])
    manifest = dict(rung="P7.2", git=_git(), quick=QUICK, seeds=SEEDS, wall_s=round(time.time() - t0, 1),
                    digits_ladder=dig, synthblob_ladder=syn, nmodes_median=nmodes_med,
                    closed_form_gain=round(dig_gain_cov, 4), mixture_extra=round(dig_gain_mix, 4),
                    versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)
    for p in plot_p7.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)

    print("\n== P7.2 MULTIMODALITY ==", flush=True)
    print(f"  natural (digits) per-class n-modes median = {nmodes_med:.2f}  (1.0 => unimodal, one prototype suffices)", flush=True)
    print(f"  digits ladder:    " + " ".join(f"{r}:{dig[r]:.3f}" for r in LADDER), flush=True)
    print(f"  synthblob(sanity):" + " ".join(f"{r}:{syn[r]:.3f}" for r in LADDER), flush=True)
    print(f"  closed-form gain over one-mean = {dig_gain_cov:+.3f} ; extra a non-convex mixture buys = {dig_gain_mix:+.3f}", flush=True)
    print(f"  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
