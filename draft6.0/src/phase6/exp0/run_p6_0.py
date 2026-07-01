"""
P6.0 — the bench + the honest NoiseModel + A7 reproduction + guards (design.md §3 P6.0).

The question: does the apparatus reproduce A7 on the FROZEN Phase-5 cell, with a credible analog-noise model and
the right channels, before any fix is tried? And how bad is it, on which channel, and is it directional? This rung:
  * stands up p6lib on the committed cell (SCFFContrastOverlap temp0.2/w2, L12, no residual);
  * sweeps per-channel A7 curves — TAP / INPUT (Rasch-dominant, additive projected-RMS) i.i.d. vs directional at
    MATCHED PROJECTED RMS; WEIGHT (multiplicative, the old-A7 model → reproduces the retention finding); ADC (a
    bit-depth sweep on the tap);
  * adds a linear_readout-on-raw-input control → OURS-vs-linear is the decisive relative-fragility read;
  * measures direction-invariance per depth (the spine metric) at a representative RMS;
  * runs the auto-zero TWO-ARM control (with/without) on a common-mode component — measure, don't assume;
  * pins sigma* (retention operating point, X=0.90 blind) and FREEZES the fix-free A7/dir arrays every later rung LOADS;
  * passes the guards: overlap≡OLU + FD-InfoNCE (carried) AND noise-σ0≡clean, aug-σ0≡plain, projected-RMS-match,
    auto-zero, FD-RINCE (new). ANY guard fails → STOP.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_0.py [--quick]
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
from p6lib import (make_committed_cell, train_cell, fit_alltap_readout, a7_sensitivity,          # noqa: E402
                   direction_invariance, class_axis, NoiseModel, infer_noisy, readout_feats,
                   linear_probe, make_headroom, make_flat,
                   equivalence_guard, fd_gradient_check,
                   noise_equiv_guard, aug_equiv_guard, projected_rms_check, auto_zero_check, fd_rince_check)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH = 25, 32
RMS_ADD = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]                             # additive projected-RMS on the class axis
SIG_W = [0.0, 0.05, 0.1, 0.2, 0.4]                                     # multiplicative weight noise (old-A7 model)
ADC_BITS = [8, 6, 4, 3, 2]                                             # ADC bit-depth sweep (on the tap)
SIG_STAR_IDX = 3                                                       # dirinv measured at RMS_ADD[3]=1.0 (mid-high)
REPS_DRAW = 5                                                          # device-mismatch draws averaged per RMS
RET_TARGET = 0.90                                                      # pinned σ* = where fix-free retention hits 0.90
OUT = os.path.join(_HERE, "figs_p6_0")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _task(task, seed):
    if task == "headroom":
        Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    else:
        Xtr, Ytr, _ = make_flat(NTR, seed + 1); Xte, Yte, _ = make_flat(NTE, seed + 2)
    return Xtr, Ytr, Xte, Yte


def run_task_seed(task, seed):
    Xtr, Ytr, Xte, Yte = _task(task, seed)
    cell = make_committed_cell([DIM] + [W] * L, seed)
    train_cell(cell, Xtr, np.random.default_rng(seed), ep=EP, batch=BATCH)
    ro = fit_alltap_readout(cell, Xtr, Ytr, NCLASS, seed)
    reps_tr = cell.infer(Xtr)                                          # axis-fit split (train; held-out from Xte)
    clean_acc = float((ro.predict(readout_feats(cell.infer(Xte), None)) == Yte).mean())

    out = dict(task=task, seed=seed, clean_acc=clean_acc)
    # --- additive channels: tap / input, iid vs directional, matched projected-RMS ---
    for ch in ("tap", "input"):
        for var in ("iid", "dir"):
            r = a7_sensitivity(cell, ro, Xtr, Ytr, Xte, Yte, NCLASS, reps_tr, Ytr, ch, var, RMS_ADD, seed,
                               reps_draw=REPS_DRAW)
            out[f"acc_{ch}_{var}"] = r["acc"].tolist(); out[f"dir_{ch}_{var}"] = r["dircos"].tolist()
    # --- weight channel (multiplicative; old-A7 reproduction) ---
    rw = a7_sensitivity(cell, ro, Xtr, Ytr, Xte, Yte, NCLASS, reps_tr, Ytr, "weight", "iid", SIG_W, seed,
                        reps_draw=REPS_DRAW)
    out["acc_weight_iid"] = rw["acc"].tolist()
    # --- ADC bit-depth sweep on the tap (fixed small additive rms so quantization is the variable) ---
    adc_acc = []
    for bits in ADC_BITS:
        nm = NoiseModel(0.0, variant="iid", adc_bits=bits)
        accs = []
        for k in range(REPS_DRAW):
            F = readout_feats(infer_noisy(cell, Xte, "adc", nm, np.random.default_rng(seed + bits + k)), None)
            accs.append(float((ro.predict(F) == Yte).mean()))
        adc_acc.append(float(np.mean(accs)))
    out["acc_adc_bits"] = adc_acc
    # --- direction-invariance per depth at σ* (tap, iid + dir) ---
    tap_axes = {l: class_axis(reps_tr[l], Ytr) for l in range(L)}
    for var, ax in (("iid", None), ("dir", tap_axes)):
        nm = NoiseModel(RMS_ADD[SIG_STAR_IDX], variant=var)
        di = direction_invariance(cell, Xte, "tap", nm, np.random.default_rng(seed + 99),
                                  tap_axes=ax if var == "dir" else None)
        out[f"dirinv_tap_{var}"] = di.tolist()
    # --- linear_readout control (raw input, same input-channel noise) → OURS-vs-linear ---
    in_axis = class_axis(Xtr, Ytr)
    for var in ("iid", "dir"):
        lin = []
        for rms in RMS_ADD:
            nm = NoiseModel(rms, variant=var)
            Xn = nm.add(Xte, np.random.default_rng(seed + 5), in_axis if var == "dir" else None, per_sample=False)
            lin.append(linear_probe(Xtr, Ytr, Xn, Yte, NCLASS, seed, epochs=120))
        out[f"acc_linbase_input_{var}"] = lin
    # --- auto-zero TWO-ARM on a common-mode component (tap, rms=0.2 + common_mode=0.4) ---
    for az in (False, True):
        nm = NoiseModel(0.2, variant="dir", common_mode=0.4, auto_zero=az)
        F = readout_feats(infer_noisy(cell, Xte, "tap", nm, np.random.default_rng(seed + 3), tap_axes=tap_axes), None)
        out[f"autozero_{'on' if az else 'off'}"] = float((ro.predict(F) == Yte).mean())
    return out


def rkey(r):
    return (r["task"], r["seed"])


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
    tasks = ["headroom"] if quick else ["headroom", "flat"]
    OUT = os.path.join(_HERE, "figs_p6_0_quick" if quick else "figs_p6_0")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    # ---- GUARDS FIRST (any fail → STOP) ----
    print("=== P6.0 guards (pre-cell) ===", flush=True)
    g = []
    g.append(equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)[0])   # overlap ≡ OLU (carried)
    g.append(fd_gradient_check(dim=DIM)[0])                              # FD InfoNCE window (carried)
    g.append(noise_equiv_guard()[0]); g.append(aug_equiv_guard()[0])
    g.append(projected_rms_check()[0]); g.append(auto_zero_check()[0]); g.append(fd_rince_check()[0])
    if not all(g):
        print("!! GUARD FAILED — STOP. A sign/direction bug must not masquerade as a finding.", flush=True)
        sys.exit(1)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P6.0 cells | tasks {tasks} × seeds {seeds} | RMS_ADD {RMS_ADD} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for task in tasks:
        for s in seeds:
            if (task, s) in done:
                r = done[(task, s)]
            else:
                r = run_task_seed(task, s); done[(task, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            ret_dir = np.array(r["acc_tap_dir"]) / (r["acc_tap_dir"][0] + 1e-9)
            print(f"  {task:8s} seed {s}: clean {r['clean_acc']:.3f} | tap-dir acc "
                  f"{r['acc_tap_dir'][0]:.3f}->{r['acc_tap_dir'][-1]:.3f} (ret@max {ret_dir[-1]:.3f}) | "
                  f"tap-iid ret {np.array(r['acc_tap_iid'])[-1]/(r['acc_tap_iid'][0]+1e-9):.3f} | "
                  f"weight ret {np.array(r['acc_weight_iid'])[-1]/(r['acc_weight_iid'][0]+1e-9):.3f}", flush=True)
    fck.close()

    # ============================================================ aggregate → arrays.npz (schema §A)
    def stack(task, key):
        return np.array([done[(task, s)][key] for s in seeds], float)

    T = "headroom"                                                     # the headline task (depth composes)
    save = dict(seeds=np.array(seeds), rms=np.array(RMS_ADD), rms_weight=np.array(SIG_W),
                adc_bits=np.array(ADC_BITS), sig_star_idx=SIG_STAR_IDX, ret_target=RET_TARGET, L=L, W=W,
                task=T, clean_acc=stack(T, "clean_acc"))
    for ch in ("tap", "input"):
        for var in ("iid", "dir"):
            acc = stack(T, f"acc_{ch}_{var}"); dr = stack(T, f"dir_{ch}_{var}")
            save[f"a7acc_ours_{ch}_{var}"] = acc
            save[f"a7dir_ours_{ch}_{var}"] = dr
            save[f"a7acc_ceiling_{ch}_{var}"] = np.repeat(acc[:, :1], len(RMS_ADD), 1)   # noiseless ceiling = acc(0)
    for var in ("iid", "dir"):
        save[f"a7acc_linbase_input_{var}"] = stack(T, f"acc_linbase_input_{var}")
    save["a7acc_ours_weight_iid"] = stack(T, "acc_weight_iid")
    save["a7acc_ours_adc_bits"] = stack(T, "acc_adc_bits")
    save["dirinv_fixfree_tap"] = stack(T, "dirinv_tap_dir")            # the spine metric (directional, per depth)
    save["dirinv_fixfree_tapiid"] = stack(T, "dirinv_tap_iid")
    save["inv_autozero"] = np.array([[done[(T, s)]["autozero_off"], done[(T, s)]["autozero_on"]] for s in seeds]).mean(0)
    save["inv_rmsmatch"] = np.array([projected_rms_check(verbose=False)[1], projected_rms_check(verbose=False)[2]])
    save["inv_cleanacc"] = stack(T, "clean_acc")
    # flat task (old-A7 anchor), stored for the card
    if "flat" in tasks:
        save["flat_a7acc_tap_dir"] = stack("flat", "acc_tap_dir")
        save["flat_a7acc_weight_iid"] = stack("flat", "acc_weight_iid")
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    # ============================================================ the pinned σ* + the READS
    def med(k):
        return np.median(save[k], 0)

    tap_dir = med("a7acc_ours_tap_dir"); tap_iid = med("a7acc_ours_tap_iid")
    inp_dir = med("a7acc_ours_input_dir"); lin_dir = med("a7acc_linbase_input_dir")
    wgt = med("a7acc_ours_weight_iid")
    ret_tap_dir = tap_dir / (tap_dir[0] + 1e-9)
    # σ* = the RMS where fix-free tap-directional retention first drops to RET_TARGET
    below = np.where(ret_tap_dir <= RET_TARGET)[0]
    sig_star = float(RMS_ADD[below[0]]) if len(below) else float(RMS_ADD[-1])
    dir_cos_at_star = float(np.median(save["dirinv_fixfree_tap"]))    # median-over-depth-and-seed dir-cos (at σ* grid pt)

    print(f"\n--- P6.0 READS (n={len(seeds)}, task={T}) ---")
    print(f"  clean acc                 : {np.median(save['clean_acc']):.3f}")
    print(f"  tap  iid  retention @{RMS_ADD[-1]} : {tap_iid[-1]/(tap_iid[0]+1e-9):.3f}")
    print(f"  tap  DIR  retention @{RMS_ADD[-1]} : {ret_tap_dir[-1]:.3f}   (directional = the enemy)")
    print(f"  input DIR retention @{RMS_ADD[-1]} : {inp_dir[-1]/(inp_dir[0]+1e-9):.3f}")
    print(f"  linear-ctrl DIR ret @{RMS_ADD[-1]} : {lin_dir[-1]/(lin_dir[0]+1e-9):.3f}   (OURS-vs-linear read)")
    print(f"  weight ret @{SIG_W[-1]} (old A7)   : {wgt[-1]/(wgt[0]+1e-9):.3f}")
    print(f"  ADC acc @bits {ADC_BITS}      : {[round(x,3) for x in med('a7acc_ours_adc_bits')]}")
    print(f"  auto-zero [off,on] acc      : {[round(x,3) for x in save['inv_autozero']]}")
    print(f"  >> PINNED σ* (tap-dir ret={RET_TARGET}) = {sig_star}   dir-cos@σ* (median over depth) = {dir_cos_at_star:.3f}")
    ours_worse = (ret_tap_dir[-1] < lin_dir[-1] / (lin_dir[0] + 1e-9))
    print(f"  >> OURS more directionally fragile than linear? {'YES (A7 thesis)' if ours_worse else 'NO (re-scope)'}")

    json.dump(dict(experiment="p6_0_bench", git_commit=_git(), seeds=list(seeds), tasks=tasks, L=L, W=W, dim=DIM,
                   n_class=NCLASS, rms_add=RMS_ADD, sig_w=SIG_W, adc_bits=ADC_BITS, reps_draw=REPS_DRAW,
                   ret_target=RET_TARGET, sigma_star=sig_star, dir_cos_at_star=dir_cos_at_star,
                   ours_worse_than_linear=bool(ours_worse),
                   guards=dict(all_pass=True), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    try:
        import plot_p6
        print("\n  figures:", [os.path.basename(p) for p in plot_p6.regen(OUT)])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) → {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
