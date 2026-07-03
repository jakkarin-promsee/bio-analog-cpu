"""
P10.0 — the BENCH: the fair racer + the gauntlet harness + the SIX new guards (design §3 P10.0). NO verdict — a
build + guards. Green iff (a) ER's replay buffer == OURS's LUT in BYTES + each learner's FLOPs/sample reported
(fair_budget); (b) the freeze CONTENT manifest + grid-4 bit-exact (freeze_content, `59d2720` a provenance label);
(c) the cadence family reproduces grid-4 bit-for-bit (cadence_family); (d) the gauntlet loads offline at the shared
40-D input, one pinned ->40 projection, bit-identical stream (gauntlet_data); (e) the noise battery is margin-disjoint
from P9.4 (noise_holdout); (f) accuracy is substrate-independent (substrate_identity). ANY guard red -> STOP (a
broken bench poisons every verdict). Also: build the ER-strong config on the DISJOINT tuning stream (seed 7 ∉ raced),
and decide the A-GEM/DER++ descope (time-boxed HERE, not mid-fight — K11).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p10_0.py [--quick]
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
import p10lib as P                                                     # noqa: E402
import p10cfg as CFG                                                   # noqa: E402
import p10run as R                                                     # noqa: E402
import plot_p10                                                        # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p10_0" + ("_quick" if QUICK else ""))


def main():
    t0 = time.time()
    print(f"P10.0 — bench + the six new guards  (QUICK={QUICK})", flush=True)
    g = R.run_all_guards(verbose=True)
    all_green = all(g.values())
    print(f"\n  guards: {'ALL GREEN' if all_green else g}", flush=True)
    if not all_green:
        print("!! GUARD FAILURE — STOP (a broken bench poisons every verdict)", flush=True)
        R.save_run(OUT, dict(**R.inv_arrays(g)),
                   R.base_manifest("P10.0", CFG.SEEDS, QUICK, guards=g, status="STOP"))
        sys.exit(1)

    # --- build ER-strong on the DISJOINT tuning stream (seed 7 ∉ SEEDS; K2) ---
    print("\n  tuning ER-strong on the disjoint tuning stream (seed 7)...", flush=True)
    er_cfg = P.tune_er_strong(CFG, CFG.DIM, CFG.NCLASS, tune_seed=CFG.BP_TUNE_SEED)
    print(f"    ER-strong: dims={er_cfg['bp_dims']} lr={er_cfg['lr']} wd={er_cfg['l2']} replay={er_cfg['replay']} "
          f"buffer_cap={er_cfg['buffer_cap']} (tune-AA {er_cfg['tune_aa']:.3f}, seed 7 only)", flush=True)

    # --- the fair-budget audit for the full roster (FLOPs/sample + bytes) ---
    bp_dims_field = [CFG.DIM, 64, 64, CFG.NCLASS]                       # A-GEM/DER++/naive/GDumb default shape
    roster = {
        "er_strong": dict(bp_dims=er_cfg["bp_dims"], replay=er_cfg["replay"], buffer_cap=er_cfg["buffer_cap"]),
        "er_budget": dict(bp_dims=er_cfg["bp_dims"], replay=CFG.ER_BUDGET_REPLAY, buffer_cap=CFG.PROBE_N),
        "agem": dict(bp_dims=bp_dims_field, replay=er_cfg["replay"], buffer_cap=CFG.PROBE_N),
        "derpp": dict(bp_dims=bp_dims_field, replay=er_cfg["replay"], buffer_cap=CFG.PROBE_N),
        "gdumb": dict(bp_dims=bp_dims_field, replay=0, buffer_cap=CFG.PROBE_N),
        "naive": dict(bp_dims=bp_dims_field, replay=0, buffer_cap=0),
    }
    budget = {}
    print("\n  fair-budget audit (FLOPs/sample · replay-bytes · total-memory):", flush=True)
    for name, rc in roster.items():
        fb = P.fair_budget_meter(CFG, learner=name.split("_")[0] if name.startswith("er") else name,
                                 bp_dims=rc["bp_dims"], replay=rc["replay"], buffer_cap=rc["buffer_cap"],
                                 in_dim=CFG.DIM)
        budget[name] = fb
        print(f"    {name:10s}: FLOPs/sample={fb['flops_per_sample']:8.0f}  replay-bytes={fb['buffer_bytes']:8d}  "
              f"total-bytes={fb['total_bytes']:9d}", flush=True)
    # OURS's budget (needs a real cache) — build one seed-42 grid-4 run for the meter
    _, cache = R.build_life_cache(42, quick=QUICK, store_reps=False, verbose=False)
    hf = R.committed_hf(42)
    ours = P.ours_bundle(cache, hf, CFG, 4)
    fb_ours = P.fair_budget_meter(CFG, learner="ours", ours_res=ours, ours_cache=cache)
    budget["ours_g4"] = fb_ours
    print(f"    {'ours_g4':10s}: FLOPs/sample={fb_ours['flops_per_sample']:8.0f}  replay-bytes={fb_ours['buffer_bytes']:8d}  "
          f"total-bytes={fb_ours['total_bytes']:9d}", flush=True)

    # --- A-GEM/DER++ descope decision (time-boxed here) ---
    # The MLP grad-handle refactor (BPNet.grads/grads_distill/apply) is clean and both run in the smoke test, so the
    # FULL roster carries — A-GEM (one-constraint projection) + DER++ (logit buffer + distillation) are REAL, not
    # documented-simplified field points. Recorded so the fight is not re-scoped mid-run.
    descope = False
    print(f"\n  A-GEM/DER++ descope: {descope} (BPNet grad-handles clean -> full roster is REAL code)", flush=True)

    # --- gauntlet load confirm at 40-D ---
    gdata = P.load_gauntlet_data(CFG, 42)
    print(f"  gauntlet domains loaded: {[k for k in gdata if not k.startswith('_')]} @ 40-D (offline)", flush=True)

    A = dict(seeds=np.array(CFG.SEEDS), **R.inv_arrays(g))
    man = R.base_manifest("P10.0", CFG.SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          status="ALL-GREEN",
                          er_strong_config=er_cfg, fair_budget=budget, agem_derpp_descope=descope,
                          gauntlet_domains=CFG.GAUNTLET_DOMAINS, gauntlet_proj=CFG.GAUNTLET_PROJ,
                          noise_envs=CFG.NOISE_ENVS,
                          notes="bench green; frozen grid-4 bit-exact; ER-strong tuned on seed-7 only; full roster")
    R.save_run(OUT, A, man)
    for p in plot_p10.regen(OUT):
        print("  fig " + os.path.basename(p), flush=True)
    print(f"\n== P10.0 BENCH GREEN (wall {man['wall_s']}s) — proceed to P10.1 ==", flush=True)


if __name__ == "__main__":
    main()
