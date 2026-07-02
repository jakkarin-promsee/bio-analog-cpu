"""
p9run — shared run-layer helpers for the Phase-9 ladder (git hash, the committed-loop config P9 inherits from P8, the
lifelong-cache builder, manifest+arrays writing). Kept tiny; each run_p9_K.py owns its experiment logic. The SCFF
drift trajectory is gate-independent, so a lifelong cache is built ONCE per seed and every knob-arm replays on it.

The committed loop P9 tunes AROUND (the object P8.6 froze + metered — GD-share 0.121, worst-BWT 0.000): deployed head
SLDA, awake gate DDM on the error-EMA, cbrs guard, sleep grid-8 / full-history / lam_ema 1.0. P9 must not move it; it
only adds the fine machinery (N2 view / depth / eviction / residual) on top.
"""
from __future__ import annotations
import json
import os
import subprocess
import time

import numpy as np

import p9lib as P
import p9cfg as CFG


# the committed loop (the P8.6 object) — every P9 rung's internal baseline
COMMITTED_LOOP = dict(gate="ddm", trigger="error_ema", sleep_policy="grid", cadence_every=8, cbrs=True, lam_ema=1.0)
HEAD = "slda"


def committed_hf(seed):
    return lambda: P.make_stream_head(HEAD, CFG.NCLASS, seed=seed, **CFG.SLDA_KNOB)


def git_hash(here):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=here,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def med(x):
    return float(np.median(np.atleast_1d(np.asarray(x, float))))


def iqr(x):
    x = np.atleast_1d(np.asarray(x, float))
    return float(np.percentile(x, 25)), float(np.percentile(x, 75))


def fmt(x):
    q1, q3 = iqr(x)
    return f"{med(x):.3f} [{q1:.3f}-{q3:.3f}]"


def paired_sign_neg(a, b, tol=0.0):
    """#seeds where a is MORE-negative than b by MORE THAN `tol` (the paired-sign veto count for worst-BWT vs a
    reference). tol=δ_acc treats a sub-δ_acc gap as 'not really worse' (the house real-difference bar) — so the veto
    fires only on a materially-worse-than-oracle seed, not on IQR-overlapping noise."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    return int((a < b - tol).sum())


def real_diff(a, b):
    """The 'real difference' rule (n=5): IQR-disjoint at the final value AND sign-consistent >=4/5 paired."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    qa1, qa3 = iqr(a); qb1, qb3 = iqr(b)
    disjoint = (qa1 > qb3) or (qb1 > qa3)
    d = a - b; sign = max((d > 0).sum(), (d < 0).sum())
    return bool(disjoint and sign >= max(4, int(np.ceil(0.8 * len(a))))), disjoint, int(sign)


def build_life_cache(seed, *, quick=False, store_reps=True, cell_factory=None, tasks=None, verbose=True):
    """Build the lifelong SCFF drift-stream cache for one seed (the gate-independent fast-path). Returns (stream,
    cache). `cell_factory` defaults to the committed cell; the P9.1 LLRD arm passes make_llrd_cell (its own SCFF
    trajectory). `tasks` defaults to CFG.TASKS; the P9.3 cap-scaling sub-sweep passes a reduced task set (fewer
    classes). Prints a beacon + wall-clock (the phantom-hang guard). One seed at a time — the run layer never
    holds >1 cache (the 4.4 GB-RAM discipline)."""
    t = time.time()
    cf = cell_factory or P.make_committed_cell
    tk = tasks or CFG.TASKS
    Xtr, Ytr, Xte, Yte = P.synth_stream(CFG.NTR, CFG.NTE, CFG.OVERLAP, seed,
                                        dim=CFG.DIM, n_class=CFG.NCLASS, n_clusters=CFG.NCLUST)
    stream = P.make_lifelong_stream(Xtr, Ytr, Xte, Yte, tk, seed, CFG, quick=quick)
    cache = P.build_cache_p9(cf, stream, seed, CFG, store_reps=store_reps, quick=quick)
    if verbose:
        print(f"  [life-cache] seed {seed}: n_steps={stream['n_steps']} onsets={stream['real_onsets']} "
              f"nuis={stream['nuis_onset']} monitors={len(stream['monitor_steps'])} grid={len(stream['probe_grid'])} "
              f"({time.time() - t:.1f}s)", flush=True)
    return stream, cache


def load_prior(rung_exp, key, default=None):
    """Read a committed choice from a prior rung's manifest (e.g. P9.1's committed N2 -> P9.2 tunes on the slowed
    drift; the coupled-loop dependency). rung_exp e.g. 'exp1'; falls back to `default` if unrun."""
    import glob
    for m in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), rung_exp, "figs_*", "manifest.json")):
        if "_quick" in m:
            continue
        try:
            return json.load(open(m)).get(key, default)
        except Exception:
            pass
    return default


def n2_view_for(committed_n2):
    """Map a committed-N2 name ('ema-0.3'/'ema-0.1'/'llrd-0.5'/'struck'/None) to (n2_view_factory, needs_llrd_cache,
    rho). EMA-view returns a fresh EMAView per call; LLRD returns None view but flags a cell-factory swap."""
    if committed_n2 and committed_n2.startswith("ema"):
        beta = float(committed_n2.split("-")[1])
        return (lambda: P.EMAView(beta)), False, None
    if committed_n2 and committed_n2.startswith("llrd"):
        rho = float(committed_n2.split("-")[1])
        return (lambda: None), True, rho
    return (lambda: None), False, None


def run_all_guards(verbose=True):
    """All P8 carried guards + the two P9 new guards. ANY fail -> caller STOPs. Seed-independent by construction."""
    g = {}
    g["partial_fit_equiv"], _ = P.partial_fit_equiv_guard(verbose=verbose)
    g["fd_budget_gate"], _ = P.fd_budget_gate_guard(verbose=verbose)
    g["meter_proxy"], _ = P.meter_proxy_guard(CFG, verbose=verbose)
    g["detector_far"], _ = P.detector_far_guard(CFG, verbose=verbose)
    g["scff_static_frozen"], _ = P.scff_static_frozen_guard(CFG, verbose=verbose)
    g["live_path_anchor"], _ = P.live_path_anchor_guard(CFG, verbose=verbose)
    g["cache_replay"], _ = P.cache_replay_guard(CFG, verbose=verbose)
    g["n2_readside"], n2d = P.n2_readside_guard(CFG, verbose=verbose)
    g["evict_equiv"], _ = P.evict_equiv_guard(CFG, verbose=verbose)
    return g, n2d


def inv_arrays(g):
    """The INV panel arrays (all guards as 1.0/0.0) for plot_p9.fig_inv."""
    return {f"inv_{k}": np.array([1.0 if v else 0.0]) for k, v in g.items()}


def save_run(outdir, arrays, manifest):
    os.makedirs(outdir, exist_ok=True)
    np.savez(os.path.join(outdir, "arrays.npz"), **arrays)
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)


def base_manifest(rung, here, seeds, quick, **extra):
    m = dict(rung=rung, git=git_hash(here), quick=quick, seeds=list(seeds),
             committed_loop=COMMITTED_LOOP, head=HEAD, slda_knob=CFG.SLDA_KNOB,
             cell="NoiseAugContrast(iid,sig_aug=1.0)+SCFFContrastOverlap temp0.2/w2/L12",
             lifelong=dict(cycles=CFG.LIFE_CYCLES, revisit=CFG.LIFE_REVISIT, probe_every=CFG.LIFE_PROBE_EVERY),
             delta_acc=CFG.DELTA_ACC, gd_share_cap=CFG.GD_SHARE_CAP,
             meter_cite=CFG.METER_CITE, versions=dict(numpy=np.__version__),
             internal_signals_only=True)                              # the freeze discipline, affirmed in every manifest
    m.update(extra)
    return m
