"""
p10run — shared run-layer helpers for the Phase-10 ladder (git hash, the frozen-object config, the guard runner
including the six NEW P10 guards, the fair-budget/energy plumbing, manifest+arrays writing, the stats rules). Kept
tiny; each run_p10_K.py owns its experiment logic. Carries the P9 stats primitives (med/iqr/fmt/real_diff/
paired_sign_neg) verbatim and re-exports the frozen lifelong-cache builder from p9run (the SCFF drift trajectory is
gate-independent, so a lifelong cache is built ONCE per seed and every arm replays on it).
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase9"))
import p10lib as P                                                     # noqa: E402
import p10cfg as CFG                                                   # noqa: E402
import p9run as R9                                                     # noqa: E402  (build_life_cache + committed_hf carried)

# the frozen object (grid-4) + the disjoint tuning seed
COMMITTED_LOOP = P.COMMITTED_LOOP
HEAD = P.HEAD
build_life_cache = R9.build_life_cache
committed_hf = R9.committed_hf

# stats (carried from p9run — the house real-difference rule)
med = R9.med
iqr = R9.iqr
fmt = R9.fmt
paired_sign_neg = R9.paired_sign_neg
real_diff = R9.real_diff


def git_hash(here=_HERE):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=here,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def run_all_guards(verbose=True):
    """All P8/P9 carried guards + the SIX NEW P10 guards (fair_budget · freeze_content · cadence_family ·
    gauntlet_data · noise_holdout · substrate_identity). ANY fail -> caller STOPs. The freeze/cadence guards build a
    real seed-42 lifelong cache (bit-exact reproduction of the frozen grid-4 object) — they take ~1 min each."""
    g = {}
    g["partial_fit_equiv"], _ = P.partial_fit_equiv_guard(verbose=verbose)
    g["fd_budget_gate"], _ = P.fd_budget_gate_guard(verbose=verbose)
    g["meter_proxy"], _ = P.meter_proxy_guard(CFG, verbose=verbose)
    g["detector_far"], _ = P.detector_far_guard(CFG, verbose=verbose)
    g["scff_static_frozen"], _ = P.scff_static_frozen_guard(CFG, verbose=verbose)
    g["cache_replay"], _ = P.cache_replay_guard(CFG, verbose=verbose)
    g["n2_readside"], _ = P.n2_readside_guard(CFG, verbose=verbose)
    g["evict_equiv"], _ = P.evict_equiv_guard(CFG, verbose=verbose)
    # the six NEW P10 guards
    g["fair_budget"], _ = P.fair_budget_guard(CFG, verbose=verbose)
    g["freeze_content"], _ = P.freeze_content_guard(CFG, verbose=verbose)
    g["cadence_family"], _ = P.cadence_family_guard(CFG, verbose=verbose)
    g["gauntlet_data"], _ = P.gauntlet_data_guard(CFG, verbose=verbose)
    g["noise_holdout"], _ = P.noise_holdout_guard(CFG, verbose=verbose)
    g["substrate_identity"], _ = P.substrate_identity_guard(CFG, verbose=verbose)
    return g


def inv_arrays(g):
    return {f"inv_{k}": np.array([1.0 if v else 0.0]) for k, v in g.items()}


def save_run(outdir, arrays, manifest):
    os.makedirs(outdir, exist_ok=True)
    np.savez(os.path.join(outdir, "arrays.npz"), **arrays)
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)


def base_manifest(rung, seeds, quick, **extra):
    m = dict(rung=rung, git=git_hash(), quick=quick, seeds=list(seeds),
             committed_loop=COMMITTED_LOOP, head=HEAD, slda_knob=CFG.SLDA_KNOB, cadence_headline=CFG.CAD_HEADLINE,
             cell="NoiseAugContrast(iid,sig_aug=1.0)+SCFFContrastOverlap temp0.2/w2/L12",
             frozen_provenance="59d2720 (P9 freeze commit; a provenance LABEL, not a runtime git ==)",
             delta_acc=CFG.DELTA_ACC, gd_share_cap=CFG.GD_SHARE_CAP,
             meter_cite=CFG.METER_CITE, versions=dict(numpy=np.__version__),
             judged_against_external_baseline=True,           # the honest inversion of P9's internal-only rule
             verdict_shapes_pinned_blind=True)
    m.update(extra)
    return m
