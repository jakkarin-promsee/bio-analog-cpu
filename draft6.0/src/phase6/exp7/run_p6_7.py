"""
P6.7 — natural-data confirmation: the synthetic-artifact gate (design.md §3 P6.7).

The question: do A7 AND the adopted fix hold on REAL flat data (digits 64-D, CIFAR-flat 3072-D) with noise injected
into the real inputs/taps? If A7 vanishes on real data it was a synthetic artifact; if the fix works on synthetic
but not real, it is NOT committed. Fix-free vs the adopted iid-augmentation, tap+input directional retention @σ*.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_7.py [--quick]
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
from p6lib import (make_committed_cell, NoiseAugContrast, COMMITTED, train_cell, fit_alltap_readout,   # noqa: E402
                   NoiseModel, infer_noisy, class_axis, readout_feats, load_digits_split, load_cifar_flat)

SEEDS = [42, 137, 271]                                                 # 3 seeds (natural-data confirm; heavier loaders)
W, L = 64, 12
EP, BATCH = 25, 32
SIG_ADOPT, VAR_ADOPT = 1.0, "iid"                                      # the P6.1-adopted fix
REPS_DRAW = 5
OUT = os.path.join(_HERE, "figs_p6_7")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _sig_star():
    try:
        man = json.load(open(os.path.join(_HERE, "..", "exp0", "figs_p6_0", "manifest.json")))
        return float(man["sigma_star"])
    except Exception:
        return 2.0


def a7_ret(cell, ro, Xtr, Ytr, Xte, Yte, C, channel, sig, seed):
    """Directional retention at σ on a natural dataset (device-mismatch, matched projected-RMS)."""
    reps_tr = cell.infer(Xtr)
    tap_axes = {l: class_axis(reps_tr[l], Ytr) for l in range(L)} if channel in ("tap", "adc") else None
    in_axis = class_axis(Xtr, Ytr) if channel == "input" else None
    clean = float((ro.predict(readout_feats(cell.infer(Xte), None)) == Yte).mean())
    accs = []
    for k in range(REPS_DRAW):
        nm = NoiseModel(sig, variant="dir")
        reps_n = infer_noisy(cell, Xte, channel, nm, np.random.default_rng(seed + k),
                             tap_axes=tap_axes, input_axis=in_axis)
        accs.append(float((ro.predict(readout_feats(reps_n, None)) == Yte).mean()))
    return clean, float(np.mean(accs)) / (clean + 1e-9)


def run_ds(ds, seed, sig_star):
    if ds == "digits":
        Xtr, Ytr, Xte, Yte = load_digits_split(seed); C = 10
    else:
        Xtr, Ytr, Xte, Yte = load_cifar_flat(seed, n_train=4000, n_test=1500); C = 10
    D = Xtr.shape[1]
    out = dict(ds=ds, seed=seed)
    for tag, factory in (("fixfree", lambda: make_committed_cell([D] + [W] * L, seed)),
                         ("aug", lambda: NoiseAugContrast([D] + [W] * L, seed=seed, sig_aug=SIG_ADOPT,
                                                          variant=VAR_ADOPT, randax_seed=seed + 7, **COMMITTED))):
        cell = factory(); train_cell(cell, Xtr, np.random.default_rng(seed), ep=EP, batch=BATCH)
        ro = fit_alltap_readout(cell, Xtr, Ytr, C, seed)
        for ch in ("tap", "input"):
            clean, ret = a7_ret(cell, ro, Xtr, Ytr, Xte, Yte, C, ch, sig_star, seed)
            out[f"{tag}_{ch}_clean"] = clean; out[f"{tag}_{ch}_ret"] = ret
    return out


def rkey(r):
    return (r["ds"], r["seed"])


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
    seeds = SEEDS[:1] if quick else SEEDS
    datasets = ["digits"] if quick else ["digits", "cifar"]
    OUT = os.path.join(_HERE, "figs_p6_7_quick" if quick else "figs_p6_7")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    sig_star = _sig_star()
    print(f"=== P6.7 natural-data | σ*={sig_star} | fix={VAR_ADOPT}σ{SIG_ADOPT} | {datasets} × {seeds} ===", flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")
    for ds in datasets:
        for s in seeds:
            if (ds, s) in done:
                r = done[(ds, s)]
            else:
                r = run_ds(ds, s, sig_star); done[(ds, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {ds:7s} seed {s}: tap-dir ret fixfree {r['fixfree_tap_ret']:.3f} → aug {r['aug_tap_ret']:.3f} | "
                  f"input-dir ret fixfree {r['fixfree_input_ret']:.3f} → aug {r['aug_input_ret']:.3f} | "
                  f"clean {r['fixfree_tap_clean']:.3f}/{r['aug_tap_clean']:.3f}", flush=True)
    fck.close()

    def arr(ds, key):
        return np.array([done[(ds, s)][key] for s in seeds], float)

    save = dict(seeds=np.array(seeds), rms=np.array([sig_star]))
    for ds in datasets:
        for tag in ("fixfree", "aug"):
            for ch in ("tap", "input"):
                save[f"nat_{ds}_{tag}_{ch}"] = arr(ds, f"{tag}_{ch}_ret").reshape(-1, 1)
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    print(f"\n--- P6.7 READS (n={len(seeds)}) ---")
    for ds in datasets:
        ff_t = np.median(arr(ds, "fixfree_tap_ret")); au_t = np.median(arr(ds, "aug_tap_ret"))
        ff_i = np.median(arr(ds, "fixfree_input_ret")); au_i = np.median(arr(ds, "aug_input_ret"))
        a7_present = ff_t < 0.95
        print(f"  {ds}: A7 present (fixfree tap-dir ret {ff_t:.3f}<0.95)? {'YES' if a7_present else 'NO (artifact?)'} | "
              f"fix tap {ff_t:.3f}→{au_t:.3f} ({'holds' if au_t>ff_t else 'no gain'}) | input {ff_i:.3f}→{au_i:.3f}")

    json.dump(dict(experiment="p6_7_natural", git_commit=_git(), seeds=list(seeds), datasets=datasets,
                   sig_star=sig_star, fix=f"{VAR_ADOPT}{SIG_ADOPT}", numpy=np.__version__,
                   wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p6
        print("\n  figures:", [os.path.basename(p) for p in plot_p6.regen(OUT)])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) → {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
