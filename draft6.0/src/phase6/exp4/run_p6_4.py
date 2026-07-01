"""
P6.4 — Door B: the all-noisy stream + buffer purity (design.md §3 P6.4; hardens H-purity, the continual-noise
existential).

The question: can a stable class DIRECTION form when EVERY training sample is corrupted and no clean truth is ever
shown — and does buffer PURITY (not just averaging) matter? Two separable sub-questions, distinct Reads:
  (a) Noise2Noise — train SCFF on an all-corrupted stream (zero-mean first, then directional) vs the clean-data
      cell at MATCHED effective sample budget; "the direction forms" iff dir-metric ≥ (clean − §B band); report the
      residual gap (N2N is an infinite-pair expectation → finite streams leave residual variance even zero-mean).
  (b) Purity — a small-loss PurityFilter on the LUT vs a naive keep-all buffer, at matched size, on the noisy stream.

Metric = the tail-L12 linear-probe separability (the class direction survived the corrupted stream), ratio-to-clean.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_4.py [--quick]
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
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p6lib
from p6lib import (make_committed_cell, train_cell, make_noisy_stream, PurityFilter,          # noqa: E402
                   linear_probe, label_free_axis, make_headroom)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH = 25, 32
CORR_RMS = 1.0                                                         # corruption strength (near σ*/2 — visible but not total)
P60_DIR = os.path.join(_HERE, "..", "exp0", "figs_p6_0")
OUT = os.path.join(_HERE, "figs_p6_4")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _probe(cell, Xtr, Ytr, Xte, Yte, seed):
    """Tail-L12 separability = did the class direction form."""
    return linear_probe(cell.infer(Xtr)[-1], Ytr, cell.infer(Xte)[-1], Yte, NCLASS, seed, epochs=120)


def run_seed(seed, corr_rms):
    Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    out = dict(seed=seed)
    # clean-data reference cell (matched budget)
    clean = make_committed_cell([DIM] + [W] * L, seed)
    train_cell(clean, Xtr, np.random.default_rng(seed), ep=EP, batch=BATCH)
    out["clean_ref"] = _probe(clean, Xtr, Ytr, Xte, Yte, seed)
    # (a) all-noisy stream: zero-mean, then directional
    for corr in ("zeromean", "dir"):
        Xn = make_noisy_stream(Xtr, corr, corr_rms, seed + 3, axis=label_free_axis(Xtr))
        cell = make_committed_cell([DIM] + [W] * L, seed)
        train_cell(cell, Xn, np.random.default_rng(seed), ep=EP, batch=BATCH)
        out[f"noisy_{corr}"] = _probe(cell, Xtr, Ytr, Xte, Yte, seed)   # eval on CLEAN test (did the direction form?)
    # (b) purity: naive vs filtered buffer on the directional-noisy stream
    Xn = make_noisy_stream(Xtr, "dir", corr_rms, seed + 3, axis=label_free_axis(Xtr))
    base = make_committed_cell([DIM] + [W] * L, seed)                   # a lightly-trained cell to score cleanliness
    train_cell(base, Xn, np.random.default_rng(seed), ep=5, batch=BATCH)
    pf = PurityFilter(keep_frac=0.6)
    Xf, Yf, keep = pf.filter(base, Xn, Ytr, np.random.default_rng(seed + 8))
    # purity = fraction of kept samples whose corruption scalar was small (measured against the true offset)
    cellf = make_committed_cell([DIM] + [W] * L, seed)
    train_cell(cellf, Xf, np.random.default_rng(seed), ep=EP, batch=BATCH)
    out["purity_on"] = _probe(cellf, Xtr, Ytr, Xte, Yte, seed)
    # naive = same budget (keep_frac of the stream at random)
    rng = np.random.default_rng(seed + 9); idx = rng.permutation(len(Xn))[:len(Xf)]
    celln = make_committed_cell([DIM] + [W] * L, seed)
    train_cell(celln, Xn[idx], np.random.default_rng(seed), ep=EP, batch=BATCH)
    out["purity_off"] = _probe(celln, Xtr, Ytr, Xte, Yte, seed)
    return out


def rkey(r):
    return r["seed"]


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rkey(rr)] = rr
    return done


def main():
    global OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:2] if quick else SEEDS
    OUT = os.path.join(_HERE, "figs_p6_4_quick" if quick else "figs_p6_4")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    corr_rms = CORR_RMS
    try:
        man = json.load(open(os.path.join(P60_DIR, "manifest.json"))); corr_rms = float(man["sigma_star"]) / 2.0
    except Exception:
        pass
    print(f"=== P6.4 Door B | corruption rms={corr_rms:.3f} (≈σ*/2) | seeds {seeds} ===", flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")
    for s in seeds:
        if s in done:
            r = done[s]
        else:
            r = run_seed(s, corr_rms); done[s] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        print(f"  seed {s}: clean {r['clean_ref']:.3f} | zeromean {r['noisy_zeromean']:.3f} "
              f"dir {r['noisy_dir']:.3f} | purity on {r['purity_on']:.3f} off {r['purity_off']:.3f}", flush=True)
    fck.close()

    def arr(k):
        return np.array([done[s][k] for s in seeds], float)

    clean = arr("clean_ref")
    save = dict(seeds=np.array(seeds), corr_rms=corr_rms,
                doorb_clean_ref=clean,
                doorb_zeromean_off=arr("noisy_zeromean") / (clean + 1e-9),
                doorb_dir_off=arr("noisy_dir") / (clean + 1e-9),
                doorb_dir_on=arr("purity_on") / (clean + 1e-9),
                purity_on=arr("purity_on"), purity_off=arr("purity_off"))
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    print(f"\n--- P6.4 READS (n={len(seeds)}) ---")
    print(f"  clean-ref separability      : {np.median(clean):.3f}")
    print(f"  zero-mean stream (ratio)    : {np.median(save['doorb_zeromean_off']):.3f}  "
          f"(N2N: forms if ≥ ~0.9)")
    print(f"  directional stream (ratio)  : {np.median(save['doorb_dir_off']):.3f}  (the crux — same directional enemy)")
    pon, poff = np.median(arr("purity_on")), np.median(arr("purity_off"))
    print(f"  purity on {pon:.3f} vs off {poff:.3f}  → {'purity helps' if pon > poff + 0.01 else 'averaging suffices'}")

    json.dump(dict(experiment="p6_4_door_b", git_commit=_git(), seeds=list(seeds), corr_rms=corr_rms,
                   numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p6
        print("\n  figures:", [os.path.basename(p) for p in plot_p6.regen(OUT)])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) → {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
