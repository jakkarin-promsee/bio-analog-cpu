"""
P6.1 — noise-as-contrastive-augmentation: the primary fix (design.md §3 P6.1, STOPPING MARK ①).

The question: does corrupting ONE InfoNCE view with the noise model make the class direction noise-invariant —
WITHOUT collapsing the representation or costing clean accuracy — and is the gain spine-clean (an ANGLE, not a
magnitude)? Swept variable = augmentation strength σ_aug. The decisive spine test = directional-aug vs
RANDOM-axis-aug (the generic-regularization isolator): directional-aug must beat random-axis on the DIRECTIONAL
curve, or the gain is generic smoothing. Loads the pinned σ* + the fix-free A7/dir arrays from P6.0 (never recomputes).

Variants (one-variable): iid | dir (label-free top-PCA axis — train-axis ≠ eval-axis, no leak) | randax (fixed
random axis = the isolator). Baseline = the co-trained σ_aug=0 arm (must reproduce the P6.0 fix-free curve).
Guards: capacity-knee (clean selectivity vs σ_aug) + collapse (selectivity below fix-free → abort that σ_aug).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p6_1.py [--quick]
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
from p6lib import (NoiseAugContrast, COMMITTED, make_committed_cell, train_cell, fit_alltap_readout,   # noqa: E402
                   NoiseModel, infer_noisy, direction_invariance, class_axis, readout_feats,
                   linear_probe, effective_rank, make_headroom)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH = 25, 32
SIGAUG = [0.0, 0.5, 1.0, 2.0]                                          # augmentation strength (0 = fix-free co-trained)
VARIANTS = ["iid", "dir", "randax"]
REPS_DRAW = 3
P60_DIR = os.path.join(_HERE, "..", "exp0", "figs_p6_0")
OUT = os.path.join(_HERE, "figs_p6_1")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _load_p60():
    man = json.load(open(os.path.join(P60_DIR, "manifest.json")))
    arr = np.load(os.path.join(P60_DIR, "arrays.npz"), allow_pickle=True)
    return man, arr


def measure(cell, Xtr, Ytr, Xte, Yte, sig_star, seed):
    """Light per-cell measurement at σ* (the operating point): clean acc, tail selectivity, erank, and — for the
    two directional channels — direction-invariance cos + acc-retention at σ*. Cheap (no full curve per cell)."""
    ro = fit_alltap_readout(cell, Xtr, Ytr, NCLASS, seed)
    reps_te = cell.infer(Xte); reps_tr = cell.infer(Xtr)
    clean_F = readout_feats(reps_te, None)
    clean_acc = float((ro.predict(clean_F) == Yte).mean())
    selectivity = linear_probe(reps_tr[-1], Ytr, reps_te[-1], Yte, NCLASS, seed, epochs=120)   # tail-L12 separability
    erank = float(effective_rank(reps_te[-1]))
    out = dict(clean_acc=clean_acc, selectivity=selectivity, erank=erank)
    tap_axes = {l: class_axis(reps_tr[l], Ytr) for l in range(L)}
    in_axis = class_axis(Xtr, Ytr)
    # eval BOTH enemies: directional (coherent translation → retention read) AND iid (rotational → cos read)
    for ch, ax_kw in (("input", dict(input_axis=in_axis)), ("tap", dict(tap_axes=tap_axes))):
        for enemy in ("dir", "iid"):
            cos_draws, acc_draws = [], []
            for k in range(REPS_DRAW):
                nm = NoiseModel(sig_star, variant=enemy)
                di = direction_invariance(cell, Xte, ch, nm, np.random.default_rng(seed + k + 11), **ax_kw)
                cos_draws.append(float(np.median(di)))
                reps_n = infer_noisy(cell, Xte, ch, NoiseModel(sig_star, variant=enemy),
                                     np.random.default_rng(seed + k + 22), **ax_kw)
                acc_draws.append(float((ro.predict(readout_feats(reps_n, None)) == Yte).mean()))
            tag = ch if enemy == "dir" else f"{ch}iid"
            out[f"dircos_{tag}"] = float(np.mean(cos_draws))
            out[f"accret_{tag}"] = float(np.mean(acc_draws)) / (clean_acc + 1e-9)
    return out


def run_cell(variant, sigaug, seed, sig_star):
    Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    if sigaug == 0.0:
        cell = make_committed_cell([DIM] + [W] * L, seed)             # co-trained fix-free (variant-independent)
    else:
        cell = NoiseAugContrast([DIM] + [W] * L, seed=seed, sig_aug=sigaug, variant=variant, loss="infonce",
                                randax_seed=seed + 7, **COMMITTED)
    train_cell(cell, Xtr, np.random.default_rng(seed), ep=EP, batch=BATCH)
    r = measure(cell, Xtr, Ytr, Xte, Yte, sig_star, seed)
    r.update(variant=variant, sigaug=sigaug, seed=seed)
    return r


def rkey(r):
    return (r["variant"], r["sigaug"], r["seed"])


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
    sigaugs = [0.0, 1.0] if quick else SIGAUG
    variants = ["dir", "randax"] if quick else VARIANTS
    OUT = os.path.join(_HERE, "figs_p6_1_quick" if quick else "figs_p6_1")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    man, p60 = _load_p60()
    sig_star = float(man["sigma_star"])
    print(f"=== P6.1 noise-as-augmentation | inheriting σ*={sig_star} + dominant=directional from P6.0 "
          f"(ours_worse_than_linear={man['ours_worse_than_linear']}) ===", flush=True)
    # fix-free reference retention/cos at σ* from P6.0 (loaded, never recomputed)
    rms = list(p60["rms"]); si = rms.index(sig_star) if sig_star in rms else int(man["sig_star_idx"])
    ff_input_ret = float(np.median(p60["a7acc_ours_input_dir"], 0)[si] / (np.median(p60["a7acc_ours_input_dir"], 0)[0] + 1e-9))
    ff_input_cos = float(np.median(p60["a7dir_ours_input_dir"], 0)[si])
    print(f"    P6.0 fix-free @σ*: input-dir retention={ff_input_ret:.3f}  input-dir cos={ff_input_cos:.3f}", flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    fck = open(ckpt, "a")

    def do(variant, sg, s):
        # σ_aug=0 is variant-independent → compute once, alias to every variant
        key = (variant, sg, s) if sg != 0.0 else ("_base", 0.0, s)
        if key in done:
            return done[key]
        r = run_cell(variant if sg != 0.0 else "_base", sg, s, sig_star)
        done[key] = r; fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        return r

    print(f"\n=== cells | variants {variants} × σ_aug {sigaugs} × seeds {seeds} | {len(done)} cached ===", flush=True)
    for s in seeds:
        base = do("_base", 0.0, s)
        print(f"  [base σ0] seed {s}: clean {base['clean_acc']:.3f} sel {base['selectivity']:.3f} "
              f"input-dir cos {base['dircos_input']:.3f} ret {base['accret_input']:.3f}", flush=True)
        for v in variants:
            for sg in sigaugs:
                if sg == 0.0:
                    continue
                r = do(v, sg, s)
                print(f"  {v:6s} σ{sg:<4}: clean {r['clean_acc']:.3f} sel {r['selectivity']:.3f} erank {r['erank']:.1f} | "
                      f"input-dir cos {r['dircos_input']:.3f} ret {r['accret_input']:.3f} | "
                      f"tap-dir cos {r['dircos_tap']:.3f} ret {r['accret_tap']:.3f}", flush=True)
    fck.close()

    # ============================================================ aggregate → arrays.npz (schema §A)
    def base_arr(key):
        return np.array([done[("_base", 0.0, s)][key] for s in seeds], float)

    def var_arr(v, key):                                              # [S, G] over σ_aug (σ0 = base)
        cols = []
        for sg in sigaugs:
            src = ("_base", 0.0) if sg == 0.0 else (v, sg)
            cols.append([done[(src[0], src[1], s)][key] for s in seeds])
        return np.array(cols, float).T                                # [S, G]

    save = dict(seeds=np.array(seeds), sigaug=np.array(sigaugs), sig_star=sig_star,
                ff_input_ret=ff_input_ret, ff_input_cos=ff_input_cos)
    # NOTE (from P6.0): the directional enemy is a COHERENT TRANSLATION along the class axis — it barely rotates a
    # single rep (per-sample cos ~0.97, no headroom) yet destroys accuracy. So the spine read for the directional
    # channel is RETENTION under directional noise (direction-specific via OURS-vs-linear + dir-vs-iid), not
    # per-sample cos. `robust_vs_aug` = retention; per-sample cos kept as the secondary (rotational-enemy) read.
    for v in variants:
        save[f"robust_vs_aug_{v}"] = var_arr(v, "accret_input")        # DIRECTIONAL retention @σ* (the spine read)
        save[f"robust_tap_vs_aug_{v}"] = var_arr(v, "accret_tap")
        save[f"robustiid_vs_aug_{v}"] = var_arr(v, "accret_inputiid")  # IID retention (the rotational enemy)
        save[f"cosiid_vs_aug_{v}"] = var_arr(v, "dircos_inputiid")     # IID per-sample cos (does aug fix rotation?)
        save[f"cos_vs_aug_{v}"] = var_arr(v, "dircos_input")           # DIR per-sample cos (secondary; ~blind)
        save[f"select_vs_aug_{v}"] = var_arr(v, "selectivity")
        save[f"cleanacc_vs_aug_{v}"] = var_arr(v, "clean_acc")
    save["inv_erank"] = var_arr("dir", "erank")[:, -1] if "dir" in variants else base_arr("erank")
    save["inv_cleanacc"] = base_arr("clean_acc")
    np.savez(os.path.join(OUT, "arrays.npz"), **save)

    # ============================================================ the READS (design P6.1)
    print(f"\n--- P6.1 READS (n={len(seeds)}, σ*={sig_star}) ---")
    base_sel = float(np.median(base_arr("selectivity"))); base_ret = float(np.median(base_arr("accret_input")))
    base_iidret = float(np.median(base_arr("accret_inputiid"))); base_iidcos = float(np.median(base_arr("dircos_inputiid")))
    print(f"  fix-free (σ0): clean {np.median(base_arr('clean_acc')):.3f}  sel {base_sel:.3f}  "
          f"input-DIR retention {base_ret:.3f}  (linear-ctrl ceiling ≈0.96) | input-IID retention {base_iidret:.3f} "
          f"cos {base_iidcos:.3f}")
    if "dir" in variants and "randax" in variants:
        for gi, sg in enumerate(sigaugs):
            if sg == 0.0:
                continue
            rd = float(np.median(save["robust_vs_aug_dir"][:, gi]))    # retention (the spine read)
            rr = float(np.median(save["robust_vs_aug_randax"][:, gi]))
            sd = float(np.median(save["select_vs_aug_dir"][:, gi]))
            cd = float(np.median(save["cleanacc_vs_aug_dir"][:, gi]))
            spine = "dir>rand (SPINE)" if rd > rr + 0.01 else ("dir≈rand (generic)" if abs(rd - rr) <= 0.01 else "rand>dir")
            ri = float(np.median(save["robustiid_vs_aug_dir"][:, gi]))
            ci = float(np.median(save["cosiid_vs_aug_dir"][:, gi]))
            print(f"  σ_aug={sg}: dir input-RET {rd:.3f} vs randax {rr:.3f}  [{spine}] | clean {cd:.3f} | "
                  f"sel {sd:.3f} (base {base_sel:.3f}) | IID-enemy: ret {ri:.3f} cos {ci:.3f}")
        # committed σ_aug = strongest that RAISES retention while holding clean acc + selectivity ≥0.97·base
        base_clean = float(np.median(base_arr("clean_acc"))); knee = None
        for gi, sg in enumerate(sigaugs):
            if sg == 0.0:
                continue
            sd = float(np.median(save["select_vs_aug_dir"][:, gi])); rd = float(np.median(save["robust_vs_aug_dir"][:, gi]))
            cd = float(np.median(save["cleanacc_vs_aug_dir"][:, gi]))
            if sd >= 0.95 * base_sel and cd >= 0.95 * base_clean and rd > base_ret + 0.01:
                knee = sg
        print(f"  >> committed σ_aug (raises input-dir retention, clean+sel held ≥0.95·base): "
              f"{knee if knee else 'NONE — H-aug refuted here (lean P6.2/P6.3)'}")

    json.dump(dict(experiment="p6_1_noise_aug", git_commit=_git(), seeds=list(seeds), sigaugs=sigaugs,
                   variants=variants, sig_star=sig_star, numpy=np.__version__,
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
