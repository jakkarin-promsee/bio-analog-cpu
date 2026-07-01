"""
P7.0 — the bench + guards + the convex floor + the static ceiling + the two-arm RanDumb control (design.md §3 P7.0).

The question: does the apparatus reproduce a readout on the FROZEN Phase-6 bulk, do the references behave (convex
floor = linear-softmax; static ceiling = race_bp + MLP head), and — the load-bearing early read — does the trained
SCFF bulk BEAT a random projection at naming (random-from-taps AND random-from-pixels)? This rung:
  * stands up p7lib on the committed cell (NoiseAugContrast = SCFFContrastOverlap temp0.2/w2 L12 + iid-noise view);
  * runs the guards FIRST (overlap≡OLU, FD-InfoNCE carried; head-port equivalences, FD cosine-softmax, harness≡old);
  * verifies the stream_cache optimization ≡ continual_safety_heads bit-for-bit (the bake-off's fast path);
  * pins the canonical all-tap feature source + PROBE_EP (frozen for every later rung; feature fingerprints saved);
  * fits the convex floor (linear-softmax) + the static ceiling (race_bp on raw input + MLP head);
  * runs the RanDumb control in TWO arms — OURS-bulk vs random-from-taps vs random-from-pixels, same heads;
  * emits RANDUMB + INV (dead-frac, effective-rank, FD-guard, feature-source-pinned). ANY guard fails → STOP.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p7_0.py [--quick]
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
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p7lib, p7cfg
import p7lib as P                                                       # noqa: E402
import p7cfg as CFG                                                     # noqa: E402
import plot_p7                                                          # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p7_0" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
STATIC_EP = 6 if QUICK else CFG.STATIC_EP
RANDHEADS = ["linear", "rls", "ncm"]                                   # the RanDumb readouts (same head, 3 sources)


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _fingerprint(F):
    return dict(shape=list(F.shape), mean=round(float(F.mean()), 6), std=round(float(F.std()), 6),
                head8=round(float(F[0, :8].sum()), 6))


def run_seed(seed):
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed,
                                        dim=CFG.DIM, n_class=CFG.NCLASS, n_clusters=CFG.NCLUST)
    C = CFG.NCLASS
    cell = P.make_committed_cell([CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH, seed)
    P.train_cell(cell, Xtr, np.random.default_rng(seed), ep=STATIC_EP, batch=32)
    Ftr = P.all_tap_feats(cell, Xtr); Fte = P.all_tap_feats(cell, Xte)  # the PINNED canonical features

    # --- floor + static ceiling ---
    floor = P.LinearSoftmaxHead(C, seed=seed, epochs=CFG.PROBE_EP).fit(Ftr, Ytr)
    acc_floor = float((floor.predict(Fte) == Yte).mean())
    mlp = P.MLPHead(C, seed=seed, epochs=CFG.SLEEP_EP).fit(Ftr, Ytr)
    acc_mlp = float((mlp.predict(Fte) == Yte).mean())
    bp = P.race_bp(Xtr, Ytr, Xte, Yte, C, total=P.ours_budget(CFG.DIM, CFG.WIDTH, CFG.DEPTH, C, CFG.DEPTH),
                   in_dim=CFG.DIM, depths=(2, 3, 4), seed=seed, ep=(20 if QUICK else 60))
    acc_bp = float(bp["acc_te"])

    # --- RanDumb control: OURS bulk vs random-from-taps vs random-from-pixels (same head, fair expansion) ---
    rp_taps = P.RandProjBulk(CFG.RANDPROJ_DIM, "taps", in_dim=Ftr.shape[1], seed=seed)
    rp_pix = P.RandProjBulk(CFG.RANDPROJ_DIM, "pixels", in_dim=CFG.DIM, seed=seed)
    Ttr, Tte = rp_taps.features(Ftr), rp_taps.features(Fte)
    Ptr, Pte = rp_pix.features(Xtr), rp_pix.features(Xte)
    randumb = {}
    for name in RANDHEADS:
        kb = dict(epochs=CFG.PROBE_EP) if name == "linear" else {}
        a_ours = float((P.make_head(name, C, seed=seed, **kb).fit(Ftr, Ytr).predict(Fte) == Yte).mean())
        a_taps = float((P.make_head(name, C, seed=seed, **kb).fit(Ttr, Ytr).predict(Tte) == Yte).mean())
        a_pix = float((P.make_head(name, C, seed=seed, **kb).fit(Ptr, Ytr).predict(Pte) == Yte).mean())
        randumb[name] = [a_ours, a_taps, a_pix]

    # --- INV ---
    deadfrac = float((Fte.std(0) < 1e-6).mean())
    erank = float(P.effective_rank(Fte))
    return dict(seed=seed, acc_floor=acc_floor, acc_mlp=acc_mlp, acc_bp=acc_bp, bp_shape=[int(bp["depth"]), int(bp["width"])],
                randumb=randumb, deadfrac=deadfrac, erank=erank,
                fp_tr=_fingerprint(Ftr), fp_te=_fingerprint(Fte))


def main():
    t0 = time.time()
    print(f"P7.0 — bench + guards + floor + ceiling + RanDumb control  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    print("== GUARDS (any fail -> STOP) ==", flush=True)
    g = {}
    g["overlap_equiv"], _ = P.equivalence_guard(verbose=True)          # carried: SCFFContrastOverlap ≡ OLU
    g["fd_infonce"], _ = P.fd_gradient_check(verbose=True)             # carried: InfoNCE window backward
    g["head_equiv"], _ = P.head_equiv_guard(verbose=True)             # NEW: head-port equivalences
    g["fd_head"], _ = P.fd_head_grad(verbose=True)                    # NEW: cosine-softmax gradient FD
    g["harness_equiv"], _ = P.harness_equiv_guard(verbose=True)       # NEW: continual_heads(MLP) ≡ old
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print("  -> all guards PASS", flush=True)

    # cache ≡ harness consistency (the bake-off fast path)
    s0 = SEEDS[0]
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, s0, dim=CFG.DIM, n_class=CFG.NCLASS, n_clusters=CFG.NCLUST)
    cache = P.stream_cache(P.make_committed_cell, Xtr, Ytr, Xte, Yte, CFG.TASKS, CFG.NCLASS, s0, scff_ep=(2 if QUICK else CFG.SCFF_EP))
    mlp_hf = lambda s: P.MLPHead(CFG.NCLASS, seed=s, epochs=CFG.SLEEP_EP)
    cm = P.eval_head_on_cache(cache, mlp_hf, s0)
    hm = P.continual_safety_heads(P.make_committed_cell, mlp_hf, Xtr, Ytr, Xte, Yte, CFG.TASKS, CFG.NCLASS, s0,
                                  scff_ep=(2 if QUICK else CFG.SCFF_EP), sleep_ep=CFG.SLEEP_EP, probe=False)
    dcache = max(abs(cm["matrix"][i][k] - hm["matrix"][i][k]) for i in range(5) for k in range(5))
    g["cache_equiv"] = bool(dcache < 1e-12)
    print(f"  [cache≡harness guard] max|d|={dcache:.2e}  {'OK' if g['cache_equiv'] else '!! CACHE BUG — STOP'}", flush=True)
    if not g["cache_equiv"]:
        sys.exit(1)

    rows = [run_seed(s) for s in SEEDS]
    for r in rows:
        print(f"  seed {r['seed']:5d}: floor={r['acc_floor']:.3f} mlp={r['acc_mlp']:.3f} bp={r['acc_bp']:.3f}{tuple(r['bp_shape'])} "
              f"| RanDumb linear[ours,taps,pix]={[round(x,3) for x in r['randumb']['linear']]} "
              f"rls={[round(x,3) for x in r['randumb']['rls']]} | deadfrac={r['deadfrac']:.3f} erank={r['erank']:.1f}", flush=True)

    # --- aggregate to arrays.npz (§A schema) ---
    A = dict(seeds=np.array(SEEDS), heads=np.array(RANDHEADS))
    A["acc_linear"] = np.array([r["acc_floor"] for r in rows])
    A["acc_mlp"] = np.array([r["acc_mlp"] for r in rows])
    A["acc_race_bp"] = np.array([r["acc_bp"] for r in rows])
    for name in RANDHEADS:
        A[f"randumb_{name}"] = np.array([r["randumb"][name] for r in rows])   # [S,3] ours/taps/pixels
    A["inv_deadfrac"] = np.array([r["deadfrac"] for r in rows])
    A["inv_erank"] = np.array([r["erank"] for r in rows])
    A["inv_fdguard"] = np.array([1.0])
    A["inv_featpinned"] = np.array([1.0])
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "arrays.npz"), **A)

    def med(x):
        return float(np.median(x))
    manifest = dict(rung="P7.0", git=_git(), quick=QUICK, seeds=SEEDS, wall_s=round(time.time() - t0, 1),
                    pinned=dict(PROBE_EP=CFG.PROBE_EP, SLEEP_EP=CFG.SLEEP_EP, SCFF_EP=CFG.SCFF_EP, STATIC_EP=STATIC_EP,
                                FEAT=CFG.FEAT, DIM=CFG.DIM, NCLASS=CFG.NCLASS, NCLUST=CFG.NCLUST, OVERLAP=CFG.OVERLAP,
                                RANDPROJ_DIM=CFG.RANDPROJ_DIM, cell="NoiseAugContrast(iid,sig_aug=1.0)+temp0.2/w2/L12"),
                    guards=g,
                    fingerprints={str(r["seed"]): dict(tr=r["fp_tr"], te=r["fp_te"]) for r in rows},
                    summary=dict(acc_floor=med(A["acc_linear"]), acc_mlp=med(A["acc_mlp"]), acc_bp=med(A["acc_race_bp"]),
                                 randumb={n: [med(A[f"randumb_{n}"][:, j]) for j in range(3)] for n in RANDHEADS},
                                 deadfrac=med(A["inv_deadfrac"]), erank=med(A["inv_erank"])),
                    versions=dict(numpy=np.__version__))
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)

    print("== figures ==", flush=True)
    for p in plot_p7.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    s = manifest["summary"]
    print(f"\n== P7.0 SUMMARY (median) ==\n  floor(linear)={s['acc_floor']:.3f}  MLP={s['acc_mlp']:.3f}  race_bp(static ceil)={s['acc_bp']:.3f}", flush=True)
    for n in RANDHEADS:
        o, t, p = s["randumb"][n]
        verdict = "OURS earns keep" if (o > t + 0.01 and o > p + 0.01) else ("ties taps" if o <= t + 0.01 else "ties pixels")
        print(f"  RanDumb {n:7s}: OURS={o:.3f} taps={t:.3f} pixels={p:.3f}  -> {verdict}", flush=True)
    print(f"  deadfrac={s['deadfrac']:.3f}  erank={s['erank']:.1f}  wall={manifest['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
