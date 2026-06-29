"""
P5.1 — objective sharpness: temperature as the (maybe-)free depth lever (design.md §3 P5.1).

The question: is a sharper InfoNCE the free depth fix — where is the floor, does it survive the real readout, and
is it FREE (objective-sharpness = hard-negative reweighting) or a DISGUISED learning-rate increase?

  * SWEEP temp in {0.5,0.35,0.2,0.1,0.05} at the adopted window=2, mask=0.5, on headroom + flat + mixed, L12.
  * the lr-CONFOUND control (mandatory): lowering temp scales the gradient by ~1/temp (a disguised lr) AND sharpens
    the softmax over negatives (hard-negative reweighting = the DIRECTION mechanism, the spine). We empirically
    measure the mean effective step-norm at temp0.2 vs temp0.5 (identical init, 1 epoch) and run a temp=0.5 cell at
    lr scaled to MATCH temp0.2's step-norm. The "free objective-sharpness" claim holds ONLY if temp0.2 still
    composes deeper than the lr-matched temp0.5. Otherwise the gain is lr, not direction — reported as such.
  * the BATCH-floor co-lever: temp0.1 @ batch 64 vs 32 — does collapse move with the number of negatives? (a peaky
    softmax over too-few negatives is dominated by one possibly-false negative -> collapse; more negatives per step
    should buy a lower safe temp). Same EP so the total negative-comparison budget ~ matches (steps x negatives).

References (w12 objective ceiling + tuned-BP achievable) are loaded from P5.0 (exp0/figs_p5_0). Guards re-run first.
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_1.py [--quick]
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
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p5lib
from p5lib import (SCFFContrastOverlap, make_headroom, make_flat, make_mixed,    # noqa: E402
                   equivalence_guard, fd_gradient_check, mean_infonce_loss,
                   fit_readout, readout_feats, linear_probe, effective_rank)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH, BASE_LR = 25, 32, 0.03
PROBE_EP = 120
TEMPS = [0.5, 0.35, 0.2, 0.1, 0.05]
TASKS = ["headroom", "flat", "mixed"]
OUT = os.path.join(_HERE, "figs_p5_1")
P50 = os.path.join(_HERE, "..", "exp0", "figs_p5_0", "arrays.npz")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _make(task, n, seed):
    if task == "headroom":
        X, Y = make_headroom(n, seed); return X, Y, None
    if task == "flat":
        X, Y, _ = make_flat(n, seed); return X, Y, None
    X, Y, m = make_mixed(n, seed); return X, Y, m


def train_overlap(Xtr, temp, lr, batch, seed, trace=False):
    m = SCFFContrastOverlap([DIM] + [W] * L, lr=lr, seed=seed, window=2, stride=2, mask_ratio=0.5, temp=temp)
    rng = np.random.default_rng(seed); norms = []
    Xheld = Xtr[:256]; lrng = np.random.default_rng(seed + 555); tr = []
    for _ in range(EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                m.train_step(xb, rng); norms.append(m.last_update_norm)
        if trace:
            tr.append(mean_infonce_loss(m, Xheld, lrng))
    return m, float(np.mean(norms)), [float(x) for x in tr]


def calibrate_lr(seed=42):
    """Mean effective step-norm at temp0.2 vs temp0.5 (headroom, identical init, 1 epoch) -> lr-match ratio."""
    Xtr, _, _ = _make("headroom", NTR, seed + 1)

    def norm1ep(temp):
        m = SCFFContrastOverlap([DIM] + [W] * L, lr=BASE_LR, seed=seed, window=2, stride=2, mask_ratio=0.5, temp=temp)
        rng = np.random.default_rng(seed); ns = []
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng); ns.append(m.last_update_norm)
        return float(np.mean(ns))
    n02, n05 = norm1ep(0.2), norm1ep(0.5)
    ratio = n02 / n05
    return BASE_LR * ratio, n02, n05, ratio


def run_cell(cfg, seed):
    task = cfg["task"]
    Xtr, Ytr, mtr = _make(task, NTR, seed + 1); Xte, Yte, mte = _make(task, NTE, seed + 2)
    is_inv = (cfg["tag"] == "headroom_t0.5")                          # the INV reference cell carries the loss trace
    m, mnorm, trace = train_overlap(Xtr, cfg["temp"], cfg["lr"], cfg["batch"], seed, trace=is_inv)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    base = dict(tag=cfg["tag"], task=task, temp=cfg["temp"], arm=cfg["arm"], lr=cfg["lr"], batch=cfg["batch"],
                seed=seed, updnorm=mnorm, dead=[float(x) for x in m.dead_fraction(Xte)],
                erank=[float(effective_rank(r)) for r in reps_te], losstrace=trace)
    if task == "mixed":
        ftr, fte = mtr["flat"], mte["flat"]; htr, hte = mtr["head"], mte["head"]
        pf = [linear_probe(rt[ftr], Ytr[ftr], re[fte], Yte[fte], NCLASS, seed, epochs=PROBE_EP)
              for rt, re in zip(reps_tr, reps_te)]
        ph = [linear_probe(rt[htr], Ytr[htr] - NCLASS, re[hte], Yte[hte] - NCLASS, NCLASS, seed, epochs=PROBE_EP)
              for rt, re in zip(reps_tr, reps_te)]
        ro = fit_readout(readout_feats(reps_tr, 1), Ytr, 2 * NCLASS, seed); pred = ro.predict(readout_feats(reps_te, 1))
        base.update(probe_flat=[float(p) for p in pf], probe_head=[float(p) for p in ph],
                    readout_flat=float((pred[fte] == Yte[fte]).mean()),
                    readout_head=float((pred[hte] == Yte[hte]).mean()),
                    nan=bool(np.any(~np.isfinite(pf + ph))))
    else:
        probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP) for rt, re in zip(reps_tr, reps_te)]
        ro = fit_readout(readout_feats(reps_tr, 1), Ytr, NCLASS, seed)
        base.update(probe=[float(p) for p in probe], readout=float((ro.predict(readout_feats(reps_te, 1)) == Yte).mean()),
                    nan=bool(np.any(~np.isfinite(probe))))
    return base


def rkey(r):
    return (r["tag"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rkey(rr)] = rr
    return done


def build_cells(lr_matched):
    cells = []
    for task in TASKS:
        for t in TEMPS:
            cells.append(dict(tag=f"{task}_t{t}", task=task, temp=t, lr=BASE_LR, batch=BATCH, arm="sweep"))
    for task in TASKS:                                                # lr-matched control (temp0.5 @ matched lr)
        cells.append(dict(tag=f"{task}_t0.5_lrm", task=task, temp=0.5, lr=lr_matched, batch=BATCH, arm="lrmatch"))
    for task in ["headroom", "mixed"]:                               # batch-floor: the collapsing temp (0.05) +
        for bt in (0.1, 0.05):                                       # the no-collapse control (0.1) @ batch64
            cells.append(dict(tag=f"{task}_t{bt}_b64", task=task, temp=bt, lr=BASE_LR, batch=64, arm="batchfloor"))
    return cells


def main():
    global PROBE_EP
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    PROBE_EP = 40 if quick else 120
    out = os.path.join(_HERE, "figs_p5_1_quick" if quick else "figs_p5_1")
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    print("=== P5.1 guards (pre-cell) ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    lr_matched, n02, n05, ratio = calibrate_lr()
    print(f"\n=== P5.1 lr-CALIBRATION (headroom, identical init, 1 epoch) ===")
    print(f"  mean step-norm: temp0.2 {n02:.4e}  temp0.5 {n05:.4e}  ratio {ratio:.3f}  "
          f"-> lr-matched temp0.5 lr = {lr_matched:.4f} (base {BASE_LR})", flush=True)

    cells = build_cells(lr_matched)
    if quick:
        cells = [c for c in cells if c["task"] == "headroom"]         # coherent headroom-only subset (all temps + ctrls)
    ckpt = os.path.join(out, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.1 cells | {len(cells)} cells x seeds {seeds} | PROBE_EP={PROBE_EP} | {len(done)} cached ===",
          flush=True)
    fck = open(ckpt, "a")
    for cfg in cells:
        for s in seeds:
            if (cfg["tag"], s) in done:
                continue
            r = run_cell(cfg, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            if cfg["task"] == "mixed":
                tail = r["probe_flat"][-1]; pk = int(np.argmax(r["probe_flat"])) + 1; extra = f"flatL12 {tail:.3f}"
            else:
                tail = r["probe"][-1]; pk = int(np.argmax(r["probe"])) + 1; extra = f"tailL12 {tail:.3f}"
            print(f"  {cfg['tag']:22s} seed {s}: peak@L{pk:>2} {extra}  step-norm {r['updnorm']:.3e}"
                  f"{'  [NAN]' if r.get('nan') else ''}", flush=True)
    fck.close()

    # ---- aggregate -> arrays.npz ----
    def tail_of(rec):
        return (rec["probe_flat"] if rec["task"] == "mixed" else rec["probe"])[-1]

    def ro_of(rec):
        return rec["readout_flat"] if rec["task"] == "mixed" else rec["readout"]

    def profile_of(rec):
        return rec["probe_flat"] if rec["task"] == "mixed" else rec["probe"]

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, probe_ep=PROBE_EP, temps=np.array(TEMPS),
                lr_matched=lr_matched, calib_ratio=ratio, calib_n02=n02, calib_n05=n05,
                inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_deadfrac=np.array([done[("headroom_t0.5", s)]["dead"] for s in seeds]),
                inv_erank=np.array([done[("headroom_t0.5", s)]["erank"] for s in seeds]),
                inv_losstrace=np.array([done[("headroom_t0.5", s)]["losstrace"] for s in seeds]))
    for task in TASKS:
        if not all((f"{task}_t{t}", s) in done for t in TEMPS for s in seeds):
            continue                                                  # quick / partial run — skip incomplete tasks
        save[f"{task}_tail"] = np.array([[tail_of(done[(f"{task}_t{t}", s)]) for t in TEMPS] for s in seeds])
        save[f"{task}_readout"] = np.array([[ro_of(done[(f"{task}_t{t}", s)]) for t in TEMPS] for s in seeds])
        save[f"{task}_peakL"] = np.array([[int(np.argmax(profile_of(done[(f"{task}_t{t}", s)]))) + 1
                                           for t in TEMPS] for s in seeds])
        save[f"{task}_updnorm"] = np.array([[done[(f"{task}_t{t}", s)]["updnorm"] for t in TEMPS] for s in seeds])
        save[f"{task}_probe"] = np.array([[profile_of(done[(f"{task}_t{t}", s)]) for t in TEMPS] for s in seeds])
        # lr-matched control
        if all((f"{task}_t0.5_lrm", s) in done for s in seeds):
            save[f"{task}_lrm_tail"] = np.array([tail_of(done[(f"{task}_t0.5_lrm", s)]) for s in seeds])
            save[f"{task}_lrm_readout"] = np.array([ro_of(done[(f"{task}_t0.5_lrm", s)]) for s in seeds])
            save[f"{task}_lrm_probe"] = np.array([profile_of(done[(f"{task}_t0.5_lrm", s)]) for s in seeds])
            save[f"{task}_lrm_updnorm"] = np.array([done[(f"{task}_t0.5_lrm", s)]["updnorm"] for s in seeds])
    for task in ["headroom", "mixed"]:                               # batch-floor (per collapsing/control temp)
        for bt in (0.1, 0.05):
            if not all((f"{task}_t{bt}_b64", s) in done for s in seeds):
                continue
            save[f"{task}_b64_t{bt}_tail"] = np.array([tail_of(done[(f"{task}_t{bt}_b64", s)]) for s in seeds])
            save[f"{task}_b64_t{bt}_readout"] = np.array([ro_of(done[(f"{task}_t{bt}_b64", s)]) for s in seeds])
    # references from P5.0
    if os.path.exists(P50):
        p = dict(np.load(P50))
        save["ref_w12_tail"] = float(np.median(p["hr_probe_w12"][:, -1]))
        save["ref_w12_ro"] = float(np.median(p["hr_ro_w12"]))
        save["ref_bp"] = float(np.median(p["hr_bp"]))
        save["ref_w2_tail"] = float(np.median(p["hr_probe_w2"][:, -1]))
    np.savez(os.path.join(out, "arrays.npz"), **save)
    json.dump(dict(experiment="p5_1_temperature", git_commit=_git(), seeds=list(seeds), L=L, W=W, dim=DIM,
                   n_class=NCLASS, probe_ep=PROBE_EP, temps=TEMPS, lr_matched=lr_matched, calib_ratio=ratio,
                   guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(out, "manifest.json"), "w"), indent=2)

    # ---- the Reads (pre-registered) ----
    print(f"\n--- P5.1 READS (n={len(seeds)}, headroom) ---")
    hr_tail = np.median(save["headroom_tail"], 0); hr_ro = np.median(save["headroom_readout"], 0)
    lrm_tail = float(np.median(save["headroom_lrm_tail"])); lrm_ro = float(np.median(save["headroom_lrm_readout"]))
    for i, t in enumerate(TEMPS):
        print(f"  temp {t:<4}: tail-L12 {hr_tail[i]:.3f}  readout {hr_ro[i]:.3f}  "
              f"peak@L{int(np.median(save['headroom_peakL'][:, i]))}")
    print(f"  temp0.5 lr-MATCHED: tail-L12 {lrm_tail:.3f}  readout {lrm_ro:.3f}  "
          f"(step-norm {np.median(save['headroom_lrm_updnorm']):.3e} vs temp0.2 "
          f"{np.median(save['headroom_updnorm'][:, 2]):.3e})")
    if "ref_w12_tail" in save:
        print(f"  refs: w12 tail {save['ref_w12_tail']:.3f} (ro {save['ref_w12_ro']:.3f})  "
              f"tuned-BP {save['ref_bp']:.3f}  baseline-w2 tail {save['ref_w2_tail']:.3f}")
    t02 = TEMPS.index(0.2)
    print(f"  >> FREE-vs-LR: temp0.2 tail {hr_tail[t02]:.3f} vs lr-matched temp0.5 {lrm_tail:.3f}  "
          f"-> {'DIRECTION (free)' if hr_tail[t02] > lrm_tail else 'LR (not free)'} on the probe")
    for bt in (0.1, 0.05):                                           # collapse rescue: more negatives @ the sharp temp?
        bk = f"headroom_b64_t{bt}_tail"
        if bk in save:
            b32 = hr_tail[TEMPS.index(bt)]; b64 = float(np.median(save[bk]))
            verdict = "batch64 RESCUES (negatives-starvation)" if b64 > b32 + 0.02 else "no batch effect (objective floor)"
            print(f"  >> BATCH-FLOOR temp{bt}: batch32 {b32:.3f} vs batch64 {b64:.3f}  -> {verdict}")

    try:
        import plot_p5
        figs = []
        for task in TASKS:
            figs.append(plot_p5.fig_temp_floor(out, task))
            figs.append(plot_p5.fig_depth_profile_temps(out, task))
        figs.append(plot_p5.fig_inv(out))
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {out}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
