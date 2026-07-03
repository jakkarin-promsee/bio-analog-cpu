"""
P10.4 — the NOISE SHOWCASE on a HELD-OUT battery (design §3 P10.4). Swept variable = the environment ∈
{clean, iid, directional, adc3b, nuisance-dim}; learners = OURS-hardened (NoiseAugContrast + proto-reanchor
read-side defense) vs BP+replay vs naive. The battery is a MARGIN-DISJOINT operating point of p6 NoiseModel vs
P9.4's home residual (dir-RMS 2.5 vs 1.5, +ADC 3-bit + a nuisance channel; noise_holdout_guard certifies disjoint).
The read is DIRECTIONAL RETENTION (acc under a coherent shift / clean) — a DIRECTION, never a per-sample magnitude
(the spine).

Read (pinned BLIND): Phase-6 payoff iff OURS directional-retention beats BOTH BP+replay and naive under a
GENUINELY-NOVEL directional environment; downgrade to "confirms P9.4" if the channel is only a re-parameterized
operating point of the tuned mechanism (it IS — same input-transducer structure, higher RMS → the honest read is
"confirms"); residual bites iff OURS drops > delta under a held-out channel → NAMED → analog layer.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_4.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p10lib as P                                                     # noqa: E402
import p10cfg as CFG                                                   # noqa: E402
import p10run as R                                                     # noqa: E402
import plot_p10                                                        # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p10_4" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
SCFF_EP = 4 if QUICK else 8
ENVS = CFG.NOISE_ENVS


def bp_retention(bp_dims, Xtr, Ytr, Xte, Yte, seed, input_axis):
    """A BP classifier (clean-trained, best-case) hit with the SAME held-out input channels — its directional
    retention (no SCFF layernorm, no read-side defense; the input-noise fragility reference)."""
    net = P.MLP(bp_dims, seed, lr=3e-3)
    rng = np.random.default_rng(seed + 11)
    for _ in range(40):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), 32):
            b = idx[s:s + 32]
            if len(b) >= 2:
                net.train_step(Xtr[b], Ytr[b])
    clean = float((net.predict(Xte) == Yte).mean())
    specs = dict(clean=(0.0, "iid", 0), iid=(CFG.NOISE_IID_RMS, "iid", 0),
                 directional=(CFG.NOISE_HOLDOUT_INPUT_RMS, "dir", 0),
                 adc3b=(CFG.NOISE_HOLDOUT_INPUT_RMS, "dir", CFG.NOISE_HOLDOUT_ADC_BITS),
                 nuisance=(CFG.NOISE_NUISANCE_GAIN, "nuisance", 0))
    _env_off = {"clean": 0, "iid": 100, "directional": 200, "adc3b": 300, "nuisance": 400}   # deterministic (NOT hash())
    ret = {}
    for env, (rms, variant, adc) in specs.items():
        if variant == "nuisance":
            Xn = CFG.NUIS_GAIN * Xte + CFG.NUIS_OFFSET
        else:
            nm = P.NoiseModel(rms, variant=variant, adc_bits=adc)
            ax = input_axis if variant == "dir" else None
            Xn = nm.add(Xte, np.random.default_rng(seed + 7 + _env_off[env]), ax, per_sample=False)
        ret[env] = float((net.predict(Xn) == Yte).mean()) / (clean + 1e-9)
    return ret


def main():
    t0 = time.time()
    print(f"P10.4 — noise showcase (held-out battery)  (QUICK={QUICK}, seeds={SEEDS}, envs={ENVS})", flush=True)
    g = R.run_all_guards(verbose=False)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    print(f"  guards: {'all green' if all(g.values()) else g}", flush=True)

    ret = {lr: {e: [] for e in ENVS} for lr in ("ours", "bp", "naive")}
    for s in SEEDS:
        Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, s,
                                            dim=CFG.DIM, n_class=CFG.NCLASS, n_clusters=CFG.NCLUST)
        cell = P.make_committed_cell([CFG.DIM] + [CFG.WIDTH] * CFG.DEPTH, s)
        P.train_cell(cell, Xtr, np.random.default_rng(s), ep=SCFF_EP, batch=CFG.BATCH)
        rng = np.random.default_rng(s + 4444); pr = rng.permutation(len(Xtr))[:CFG.PROBE_N]
        Xpr, Ypr = Xtr[pr], Ytr[pr]
        iax = P.class_axis(Xtr, Ytr)
        bat = P.held_out_noise_battery(cell, Xpr, Ypr, Xte, Yte, CFG, s, input_axis=iax)
        rb = bp_retention([CFG.DIM, 49, 49, 49, CFG.NCLASS], Xtr, Ytr, Xte, Yte, s, iax)
        rn = bp_retention([CFG.DIM, 64, CFG.NCLASS], Xtr, Ytr, Xte, Yte, s + 1, iax)   # naive = a smaller/shallower MLP
        for e in ENVS:
            ret["ours"][e].append(bat["retention"][e]); ret["bp"][e].append(rb[e]); ret["naive"][e].append(rn[e])
        print(f"  seed {s}: OURS dir={bat['retention']['directional']:.3f} adc3b={bat['retention']['adc3b']:.3f} | "
              f"BP dir={rb['directional']:.3f} | naive dir={rn['directional']:.3f}", flush=True)

    dacc = CFG.DELTA_ACC
    # the load-bearing comparison is OURS-hardened vs the fair continual opponent BP+replay (the spine: a DIRECTION read).
    # The battery is a RE-PARAMETERIZED input-transducer op point (not a structurally-novel channel), so a win over BP
    # "confirms P9.4 at new levels" rather than a fresh payoff; a residual > delta on a channel is NAMED -> analog layer.
    noisy = ("iid", "directional", "adc3b", "nuisance")
    beats_bp_all = all(R.med(ret["ours"][e]) > R.med(ret["bp"][e]) + dacc for e in noisy)
    resid = [e for e in ("directional", "adc3b") if R.med(ret["ours"][e]) < 1.0 - dacc]
    novel = False                                                      # same transducer structure as P9.4 -> re-parameterized
    if beats_bp_all and novel and not resid:
        verdict = "PHASE-6 PAYOFF (OURS-hardened >> BP+replay on a genuinely-novel battery; no residual)"
    elif beats_bp_all:
        verdict = ("CONFIRMS P9.4 at new levels: OURS-hardened >> BP+replay on EVERY held-out channel "
                   "(iid/directional/adc3b/nuisance)")
        if resid:
            rtxt = ", ".join(f"{e} {R.med(ret['ours'][e]):.3f}" for e in resid)
            verdict += f"; a small residual persists ({rtxt}, > delta) -> NAMED -> analog-realism layer"
    elif resid:
        verdict = f"RESIDUAL BITES on {resid} -> NAMED -> analog-realism layer"
    else:
        verdict = "within-noise (no learner separates on this battery)"

    print(f"\n  == NOISE-SHOWCASE (delta_acc={dacc}) ==", flush=True)
    print(f"  {'env':>12} {'OURS-hardened':>16} {'BP+replay':>14} {'naive':>14}", flush=True)
    for e in ENVS:
        print(f"  {e:>12} {R.fmt(ret['ours'][e]):>16} {R.fmt(ret['bp'][e]):>14} {R.fmt(ret['naive'][e]):>14}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)

    A = dict(seeds=np.array(SEEDS), noise_envs=np.array(ENVS),
             noise_learners=np.array(["ours", "bp", "naive"]), **R.inv_arrays(g))
    for lr in ("ours", "bp", "naive"):
        for e in ENVS:
            A[f"dirret_{lr}_{e}"] = np.array(ret[lr][e])
    man = R.base_manifest("P10.4", SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          envs=ENVS, verdict=verdict, novel_structure=novel,
                          summary={e: dict(ours=R.fmt(ret["ours"][e]), bp=R.fmt(ret["bp"][e]),
                                           naive=R.fmt(ret["naive"][e])) for e in ENVS})
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.4 done (wall {man['wall_s']}s) ==", flush=True)


if __name__ == "__main__":
    main()
