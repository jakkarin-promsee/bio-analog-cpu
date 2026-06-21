"""
Smoke test for P2.0 — does the WALL exist, and does the DeeperForward cell bend it?

Not the full run (no GD ceiling, no width x depth, 2 seeds). Just the load-bearing question:
on a high-D compositional task, train one L=8 SCFF stack and read the per-layer linear probe.
  (lengthnorm, squared)  = the Phase-1 wall      -> expect probe to DECLINE with depth
  (layernorm,  linear )  = the DeeperForward cell -> does it decline less / hold / rise?
Also print dead-unit fraction per layer (the deactivation mechanism).

Run:  python smoke_exp0.py
"""
from __future__ import annotations
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from p2lib import SCFF2, probe_per_layer, make_tierb  # noqa: E402

SEEDS = [42, 137]
L, WIDTH = 8, 64
N_STREAM, BATCH = 25_000, 32
DIM, GRID, N_ACTIVE, OVERLAP = 20, 4, 2, 0.30   # 16 clusters, 2-way parity (hi-D checkerboard), 20-D

CELLS = [
    ("wall  (lengthnorm, squared)", dict(norm="lengthnorm", goodness="squared")),
    ("DeepF (layernorm,  linear )", dict(norm="layernorm",  goodness="linear")),
]


def task(n, seed):
    return make_tierb(n, np.random.default_rng(seed), dim=DIM, grid=GRID,
                      n_active=N_ACTIVE, overlap=OVERLAP)


def run_cell(kw, seed):
    Xtr, Ytr = task(2000, seed + 1)
    Xte, Yte = task(2000, seed + 2)
    dims = [DIM] + [WIDTH] * L
    m = SCFF2(dims, seed=seed, **kw)
    rng = np.random.default_rng(seed)
    seen = 0
    while seen < N_STREAM:
        Xb, _ = task(BATCH, rng.integers(1 << 30))
        m.train_step(Xb, rng)
        seen += BATCH
    return np.array(probe_per_layer(m, Xtr, Ytr, Xte, Yte)), m.dead_fraction(Xte)


def main():
    t0 = time.time()
    print(f"Tier-B: dim={DIM} grid={GRID} n_active={N_ACTIVE} -> {GRID**N_ACTIVE} clusters, "
          f"random-per-cluster label, rotated | SCFF L={L} w={WIDTH} | stream={N_STREAM} | seeds={SEEDS}\n")
    for name, kw in CELLS:
        probes, deads = [], []
        for s in SEEDS:
            p, d = run_cell(kw, s)
            probes.append(p); deads.append(d)
        P = np.median(probes, 0); D = np.median(deads, 0)
        slope = float(np.polyfit(np.arange(1, L + 1), P, 1)[0])
        print(f"{name}")
        print(f"   probe/layer : {np.round(P, 3)}")
        print(f"   dead/layer  : {np.round(D, 2)}")
        print(f"   depth-slope : {slope:+.4f}/layer   (L1={P[0]:.3f} -> L{L}={P[-1]:.3f})   "
              f"{'RISES' if slope > 0 else 'DECLINES'}\n")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
