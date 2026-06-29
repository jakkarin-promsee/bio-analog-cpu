"""
P5.8 — natural-data confirmation: does the decay AND the temp fix reproduce off synthetic data? (design §3 P5.8)

The whole Phase-5 diagnosis is synthetic (make_tierb headroom + make_gauss flat). The review's strongest validity
flag: maybe the decay — or the temp0.2 fix — is a synthetic artifact. So a first-class gate: run the SAME per-layer
DEPTH-PROFILE on the in-scope REAL flat anchors — **digits (64-D)** and **CIFAR-flat (3072-D, the Phase-2/3 wall)** —
for the decay baseline (temp0.5) vs the adopted fix (temp0.2), L12/w2, static all-class.

  * decay reproduces  — the per-layer linear probe peaks then slides on real flat input (as on synth).
  * fix reproduces    — temp0.2 lifts the tail / composes deeper than temp0.5 (the P5.1 lever holds on real data).

Reads (design): decay AND fix reproduce → the synthetic story is real, commit it. Decay vanishes on real data → it
was partly a synthetic artifact, re-scope. Fix works on synth but not real → do NOT commit it.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_8.py [--quick]
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
from p5lib import (SCFFContrastOverlap, load_digits_split, load_cifar_flat, linear_probe,    # noqa: E402
                   fit_readout, readout_feats, equivalence_guard, fd_gradient_check, effective_rank)

L, W, WIN, NCLASS = 12, 64, 2, 10
EP, BATCH, PROBE_EP = 25, 32, 120
TEMPS = [0.5, 0.2]                                                      # decay baseline vs adopted fix
# dataset -> (loader, n_train, n_test, seeds)
DATASETS = {
    "digits": (load_digits_split, 1200, 600, [42, 137, 271, 314, 1729]),
    "cifar": (load_cifar_flat, 5000, 2000, [42, 137, 271]),
}
OUT = os.path.join(_HERE, "figs_p5_8")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def train(Xtr, D, temp, seed):
    m = SCFFContrastOverlap([D] + [W] * L, lr=0.03, seed=seed, window=WIN, stride=WIN, mask_ratio=0.5, temp=temp)
    rng = np.random.default_rng(seed)
    for _ in range(EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_cell(dataset, temp, seed):
    loader, ntr, nte, _ = DATASETS[dataset]
    Xtr, Ytr, Xte, Yte = loader(seed, ntr, nte); D = Xtr.shape[1]
    m = train(Xtr, D, temp, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    probe = [linear_probe(a, Ytr, b, Yte, NCLASS, seed, epochs=PROBE_EP) for a, b in zip(reps_tr, reps_te)]
    ro = fit_readout(readout_feats(reps_tr, None), Ytr, NCLASS, seed)
    readout = float((ro.predict(readout_feats(reps_te, None)) == Yte).mean())
    dead = [float((reps_te[l].max(0) <= 1e-9).mean()) for l in range(L)]
    erank = [float(effective_rank(reps_te[l])) for l in range(L)]
    return dict(dataset=dataset, temp=temp, seed=seed, D=D, probe=[float(x) for x in probe],
                readout=readout, peak=int(np.argmax(probe)) + 1, tail=float(probe[-1]), top=float(np.max(probe)),
                dead=dead, erank=erank)


def rkey(r):
    return (r["dataset"], r["temp"], r["seed"])


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
    OUT = os.path.join(_HERE, "figs_p5_8_quick" if quick else "figs_p5_8")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.8 guards ===", flush=True)
    eq_ok, eq_d = equivalence_guard(width=W, L=4, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check()
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    datasets = ["digits"] if quick else list(DATASETS)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.8 natural-data confirm | {datasets} | temps {TEMPS} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for dataset in datasets:
        seeds = DATASETS[dataset][3][:1] if quick else DATASETS[dataset][3]
        for temp in TEMPS:
            for s in seeds:
                if (dataset, temp, s) in done:
                    continue
                r = run_cell(dataset, temp, s); done[rkey(r)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                print(f"  {dataset:6s} temp{temp} seed {s}: peakL{r['peak']} tail {r['tail']:.3f} "
                      f"top {r['top']:.3f} readout {r['readout']:.3f} (D{r['D']})", flush=True)
    fck.close()

    save = dict(L=L, W=W, n_class=NCLASS, probe_ep=PROBE_EP, temps=np.array(TEMPS),
                inv_fdguard=fd_d, inv_equiv=eq_d)
    for dataset in datasets:
        seeds = DATASETS[dataset][3][:1] if quick else DATASETS[dataset][3]
        save[f"{dataset}_seeds"] = np.array(seeds)
        for temp in TEMPS:
            tag = f"{dataset}_t{str(temp).replace('.', '')}"
            cells = [done[(dataset, temp, s)] for s in seeds]
            save[f"{tag}_probe"] = np.array([c["probe"] for c in cells])
            save[f"{tag}_readout"] = np.array([c["readout"] for c in cells])
            save[f"{tag}_peak"] = np.array([c["peak"] for c in cells])
            save[f"{tag}_tail"] = np.array([c["tail"] for c in cells])
    # INV uses the committed-temp (0.2) cell on the first dataset
    d0 = datasets[0]; s0 = DATASETS[d0][3][0]
    save["inv_deadfrac"] = np.array([done[(d0, 0.2, s0)]["dead"]])
    save["inv_erank"] = np.array([done[(d0, 0.2, s0)]["erank"]])
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    print(f"\n--- P5.8 READS (median) — per-layer probe: does decay + temp-fix reproduce on REAL flat data? ---")
    for dataset in datasets:
        seeds = DATASETS[dataset][3][:1] if quick else DATASETS[dataset][3]
        n = len(seeds)
        for temp in TEMPS:
            tag = f"{dataset}_t{str(temp).replace('.', '')}"
            pk = np.median(save[f"{tag}_peak"]); tl = np.median(save[f"{tag}_tail"])
            pr = np.median(save[f"{tag}_probe"], 0); ro = np.median(save[f"{tag}_readout"])
            top = float(np.max(pr))
            print(f"  {dataset:6s} temp{temp}: peakL{pk:.0f} top {top:.3f} tail-L12 {tl:.3f} "
                  f"(decay {top-tl:+.3f}) readout {ro:.3f}  (n={n})")
        t5 = f"{dataset}_t05"; t2 = f"{dataset}_t02"
        decay5 = float(np.max(np.median(save[f"{t5}_probe"], 0)) - np.median(save[f"{t5}_tail"]))
        tail5 = float(np.median(save[f"{t5}_tail"])); tail2 = float(np.median(save[f"{t2}_tail"]))
        decay_real = decay5 > 0.02
        fix_real = tail2 > tail5 + 0.01
        print(f"    -> decay {'REPRODUCES' if decay_real else 'absent'} (t0.5 top-tail {decay5:+.3f}); "
              f"temp-fix {'REPRODUCES' if fix_real else 'absent'} (tail {tail5:.3f}->{tail2:.3f}, "
              f"{tail2-tail5:+.3f})", flush=True)

    json.dump(dict(experiment="p5_8_natural", git_commit=_git(), datasets=datasets, temps=TEMPS, L=L, W=W,
                   window=WIN, probe_ep=PROBE_EP, guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__,
                   wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p5
        figs = [plot_p5.fig_nat_anchor(OUT, dataset) for dataset in datasets] + [plot_p5.fig_inv(OUT)]
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
