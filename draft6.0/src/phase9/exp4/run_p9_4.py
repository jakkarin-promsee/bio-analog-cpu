"""
P9.4 — read-side noise residual (CONDITIONAL — earn-its-place probe first) (design.md §3 P9.4). Gate probe: does the
Phase-6 INPUT-TRANSDUCER DIRECTIONAL residual (p6lib.NoiseModel input channel, dir variant — the channel SCFF's
per-sample norm CANNOT remove forward-only; NOT p8's layernorm-invariant nuisance, which SCFF removes -> a vacuous
probe) dent the committed SLDA loop's retention by > delta_acc on the continual home? If NO -> one-line skip card,
defer to the analog layer. If YES, swept variable = read-side defense ∈ {off · proto-reanchor (PRIMARY — re-forward
the raw LUT through the CURRENT bulk UNDER THE SHIFT -> drift-free shift-consistent prototypes, 2403.12952) · SLDA
covariance re-estimation (fallback, shrinkage-guarded)}. Read: a read-side defense recovers the residual -> adopt / it
can't -> the residual is real and NAMED -> analog layer. The calibration signal is direction-grounded (never
entropy/confidence — the spine). Tunes on the HOME residual only (P10 uses a held-out battery).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_4.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p9lib as P                                                      # noqa: E402
import p9cfg as CFG                                                    # noqa: E402
import p9run as R                                                      # noqa: E402
import plot_p9                                                         # noqa: E402
from p6lib import class_axis                                          # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p9_4" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
SCFF_EP = 4 if QUICK else 8


def committed_namer(seed):
    return P.make_stream_head("slda", CFG.NCLASS, seed=seed, **CFG.SLDA_KNOB)


def main():
    t0 = time.time()
    print(f"P9.4 — read-side residual (conditional; Phase-6 input-transducer directional)  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g, _ = R.run_all_guards(verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)

    dents, undef, defend = [], [], []
    for s in SEEDS:
        Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, s,
                                            dim=CFG.DIM, n_class=CFG.NCLASS, n_clusters=CFG.NCLUST)
        dims = [CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH
        cell = P.make_committed_cell(dims, s)
        P.train_cell(cell, Xtr, np.random.default_rng(s), ep=SCFF_EP, batch=CFG.BATCH)
        rng = np.random.default_rng(s + 4444)
        pr = rng.permutation(len(Xtr))[:CFG.PROBE_N]; Xpr, Ypr = Xtr[pr], Ytr[pr]
        # committed namer on CLEAN all-tap reps (the deployed head)
        namer = committed_namer(s).sleep_fit(P.all_tap_feats(cell, Xpr), Ypr)
        clean = float((namer.predict(P.all_tap_feats(cell, Xte)) == Yte).mean())
        # the Phase-6 residual: input-transducer DIRECTIONAL (dir along the input class axis). It is ONE fixed device
        # offset (per_sample=False) — the SAME physical mismatch for the eval read AND the LUT re-forward (same chip).
        # So the eval residual and proto_reanchor MUST use the SAME rng draw (offset), else re-anchoring compensates
        # for the wrong shift (a direction bug — the project's recurring silent killer).
        input_axis = class_axis(Xtr, Ytr)
        nm = P.NoiseModel(CFG.RESID_INPUT_RMS, variant="dir")
        DEV = s + 7                                                   # the fixed device-offset seed (shared)
        reps_res = P.infer_noisy(cell, Xte, "input", nm, np.random.default_rng(DEV), input_axis=input_axis)
        und = float((namer.predict(P.readout_feats(reps_res, None)) == Yte).mean())
        dent = clean - und
        # PRIMARY defense: prototype re-anchoring — re-forward the raw LUT through the CURRENT bulk under the SAME
        # device offset -> drift-free, shift-CONSISTENT prototypes (the plan's own sleep mechanism, 2403.12952).
        Fre, Yre = P.proto_reanchor(cell, Xpr, Ypr, "input", nm, np.random.default_rng(DEV),
                                    input_axis=input_axis, depth=None)
        namer_re = committed_namer(s).sleep_fit(Fre, Yre)
        dfd = float((namer_re.predict(P.readout_feats(reps_res, None)) == Yte).mean())
        dents.append(dent); undef.append(und / (clean + 1e-9)); defend.append(dfd / (clean + 1e-9))
        print(f"  seed {s}: clean={clean:.3f} residual-undef={und:.3f} (dent {dent:+.3f}) "
              f"proto-reanchor={dfd:.3f} (ret {dfd/(clean+1e-9):.3f})", flush=True)

    dent_med = R.med(dents); fired = dent_med > CFG.DELTA_ACC
    if fired:
        recovered = R.med(defend) >= R.med(undef) + CFG.DELTA_ACC and R.med(defend) >= 1.0 - CFG.DELTA_ACC
        verdict = (f"read-side proto-reanchor RECOVERS the residual (ret {R.med(defend):.3f} vs undef {R.med(undef):.3f}) -> ADOPT"
                   if recovered else
                   f"read-side defense INSUFFICIENT (ret {R.med(defend):.3f}) -> residual NAMED -> analog layer")
    else:
        verdict = f"gate did NOT fire (dent {dent_med:+.3f} <= delta_acc {CFG.DELTA_ACC}) -> SKIP, defer to analog layer"

    A = dict(seeds=np.array(SEEDS), residual_dent=np.array(dents),
             residual_ret=np.array([undef, defend]).T, **R.inv_arrays(g),
             inv_firefrac=np.array([R.med([1.0])]))
    man = R.base_manifest("P9.4", _HERE, SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          gate_fired=bool(fired), residual_channel="input-transducer directional (p6 NoiseModel dir)",
                          summary=dict(dent=R.fmt(dents), undef_ret=R.fmt(undef), defend_ret=R.fmt(defend),
                                       verdict=verdict))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p9.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P9.4 SUMMARY (wall {man['wall_s']}s) ==", flush=True)
    print(f"  residual dent {R.fmt(dents)} (gate fires iff > {CFG.DELTA_ACC})  FIRED={fired}", flush=True)
    print(f"  undefended retention {R.fmt(undef)} | proto-reanchor retention {R.fmt(defend)}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)


if __name__ == "__main__":
    main()
