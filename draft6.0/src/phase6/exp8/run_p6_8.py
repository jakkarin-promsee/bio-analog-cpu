"""
P6.8 — assembled-cell confirmation: the adopted cell's FULL A7 curve + the headline figures (design.md §3 P6.8).

Only ONE fix was adopted (generic iid noise-augmentation σ_aug=1.0), so the "assembled cell" IS that cell — no
levers to stack. P6.1 measured it only at σ*; this run computes its FULL tap/input-directional A7 curve (all RMS) +
direction-invariance per depth, alongside the frozen fix-free P6.0 arrays, to draw the A7-CURVE (fix-free vs
hardened) and DIR-INVARIANCE headline figures and evaluate the verdict conjunction.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_8.py [--quick]
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
from p6lib import (NoiseAugContrast, COMMITTED, train_cell, fit_alltap_readout, a7_sensitivity,   # noqa: E402
                   direction_invariance, class_axis, NoiseModel, make_headroom)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE, EP, BATCH = 4000, 1500, 25, 32
RMS_ADD = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
SIG_ADOPT, VAR_ADOPT = 1.0, "iid"
REPS_DRAW = 5
P60_DIR = os.path.join(_HERE, "..", "exp0", "figs_p6_0")
OUT = os.path.join(_HERE, "figs_p6_8")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def run_seed(seed):
    Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    cell = NoiseAugContrast([DIM] + [W] * L, seed=seed, sig_aug=SIG_ADOPT, variant=VAR_ADOPT,
                            randax_seed=seed + 7, **COMMITTED)
    train_cell(cell, Xtr, np.random.default_rng(seed), ep=EP, batch=BATCH)
    ro = fit_alltap_readout(cell, Xtr, Ytr, NCLASS, seed)
    reps_tr = cell.infer(Xtr)
    out = dict(seed=seed, clean_acc=float((ro.predict(np.concatenate(cell.infer(Xte), 1)) == Yte).mean()))
    for ch in ("tap", "input"):
        r = a7_sensitivity(cell, ro, Xtr, Ytr, Xte, Yte, NCLASS, reps_tr, Ytr, ch, "dir", RMS_ADD, seed,
                           reps_draw=REPS_DRAW)
        out[f"acc_{ch}_dir"] = r["acc"].tolist()
    tap_axes = {l: class_axis(reps_tr[l], Ytr) for l in range(L)}
    di = direction_invariance(cell, Xte, "tap", NoiseModel(2.0, variant="dir"),
                              np.random.default_rng(seed + 99), tap_axes=tap_axes)
    out["dirinv_tap_dir"] = di.tolist()
    return out


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rr["seed"]] = rr
    return done


def main():
    global OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:2] if quick else SEEDS
    OUT = os.path.join(_HERE, "figs_p6_8_quick" if quick else "figs_p6_8")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    p60 = np.load(os.path.join(P60_DIR, "arrays.npz"), allow_pickle=True)
    print(f"=== P6.8 assembled cell = {VAR_ADOPT} σ{SIG_ADOPT} | full A7 curve | seeds {seeds} ===", flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")
    for s in seeds:
        if s in done:
            r = done[s]
        else:
            r = run_seed(s); done[s] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        rr = np.array(r["acc_tap_dir"]) / (r["acc_tap_dir"][0] + 1e-9)
        print(f"  seed {s}: clean {r['clean_acc']:.3f}  tap-dir ret@2.0 {rr[4]:.3f} ret@4.0 {rr[5]:.3f}", flush=True)
    fck.close()

    def stack(key):
        return np.array([done[s][key] for s in seeds], float)

    hard_tap = stack("acc_tap_dir"); hard_in = stack("acc_input_dir")
    save = dict(seeds=np.array(seeds), rms=np.array(RMS_ADD),
                a7acc_fixfree_tap_dir=p60["a7acc_ours_tap_dir"], a7acc_hardened_tap_dir=hard_tap,
                a7acc_fixfree_input_dir=p60["a7acc_ours_input_dir"], a7acc_hardened_input_dir=hard_in,
                a7acc_ceiling_tap_dir=np.repeat(hard_tap[:, :1], len(RMS_ADD), 1),
                a7acc_linbase_input_dir=p60["a7acc_linbase_input_dir"],
                dirinv_hardened_tap=stack("dirinv_tap_dir"), dirinv_fixfree_tap=p60["dirinv_fixfree_tap"],
                clean_acc=stack("clean_acc"))
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    # ============================================================ verdict inputs
    def ret(a):
        return a / (a[:, :1] + 1e-9)

    si = RMS_ADD.index(2.0)
    ff = np.median(ret(p60["a7acc_ours_tap_dir"]), 0)[si]
    hd = np.median(ret(hard_tap), 0)[si]
    print(f"\n--- P6.8 assembled READS (n={len(seeds)}, σ*=2.0) ---")
    print(f"  tap-directional retention: fix-free {ff:.3f} → hardened {hd:.3f}  "
          f"(band ≥0.90: {'PASS' if hd >= 0.90 else 'below'})")
    print(f"  clean acc: {np.median(save['clean_acc']):.3f} (fix-free 0.526)")

    json.dump(dict(experiment="p6_8_assembled", git_commit=_git(), seeds=list(seeds), fix=f"{VAR_ADOPT}{SIG_ADOPT}",
                   tap_dir_ret_fixfree=float(ff), tap_dir_ret_hardened=float(hd),
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
