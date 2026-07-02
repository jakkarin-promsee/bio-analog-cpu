"""
p8run — shared run-layer helpers for the Phase-8 ladder (git hash, cache building, manifest+arrays writing). Kept
tiny; each run_p8_K.py owns its experiment logic. The SCFF drift stream + its cache are gate-independent, so a cache
is built ONCE per seed and every gate/trigger/cadence arm replays on it (the tractability fast-path).
"""
from __future__ import annotations
import json
import os
import subprocess
import time

import numpy as np

import p8lib as P


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


def build_caches(cfg, seeds, *, quick=False, sleep_every=4, verbose=True):
    """Build the SCFF drift-stream cache once per seed (the gate-independent fast-path). Returns {seed: (stream,
    cache)}. Prints a beacon per seed + verifies progress (the phantom-hang guard: flush + wall-clock)."""
    out = {}
    for s in seeds:
        t = time.time()
        Xtr, Ytr, Xte, Yte = P.synth_stream(cfg.NTR, cfg.NTE, cfg.OVERLAP, s,
                                            dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
        stream = P.make_drift_stream(Xtr, Ytr, Xte, Yte, cfg.TASKS, s, cfg, quick=quick)
        cache = P.build_cache(P.make_committed_cell, stream, s, cfg, sleep_every=sleep_every, quick=quick)
        out[s] = (stream, cache)
        if verbose:
            print(f"  [cache] seed {s}: n_steps={stream['n_steps']} onsets={stream['real_onsets']} "
                  f"nuis={stream['nuis_onset']} ({time.time() - t:.1f}s)", flush=True)
    return out


def save_run(outdir, arrays, manifest):
    os.makedirs(outdir, exist_ok=True)
    np.savez(os.path.join(outdir, "arrays.npz"), **arrays)
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(P.jsonsafe(manifest), f, indent=2)


def base_manifest(rung, here, seeds, quick, cfg, **extra):
    m = dict(rung=rung, git=git_hash(here), quick=quick, seeds=list(seeds),
             cell="NoiseAugContrast(iid,sig_aug=1.0)+SCFFContrastOverlap temp0.2/w2/L12",
             committed_head=cfg.COMMITTED_HEAD, ranpac_knob=cfg.RANPAC_KNOB, slda_knob=cfg.SLDA_KNOB,
             stream=dict(BATCH=cfg.BATCH, WARMUP=cfg.WARMUP_STEPS, STAT=cfg.STAT_STEPS, ONSET_RAMP=cfg.ONSET_RAMP,
                         PLATEAU=cfg.PLATEAU, SETTLE=cfg.SETTLE_STEPS, NUIS=cfg.NUIS_STEPS,
                         NUIS_GAIN=cfg.NUIS_GAIN, NUIS_OFFSET=cfg.NUIS_OFFSET, WIN_W=cfg.WIN_W, WIN_LAG=cfg.WIN_LAG),
             versions=dict(numpy=np.__version__))
    m.update(extra)
    return m
