"""Phase 1 shared metrics — read numbers off a surface so eyes + numbers agree.

Rung-0 core set: output range, planar residual (curvature), linear-region count. Deeper
metrics (neuron census, output rank, PCA dimensionality, target reachability) arrive with
their experiments; the neuron census needs a small ALU-internal exposure and is deferred.
"""

import numpy as np


def output_range(Z):
    """min, max of a surface — usable output range / clipping signature."""
    return float(np.min(Z)), float(np.max(Z))


def planar_residual(Z, xs, ys):
    """Normalized RMS residual of the best-fit plane. 0 = perfectly linear (a single plane);
    larger = more nonlinearity the atom is actually using."""
    X, Y = np.meshgrid(xs, ys)
    A = np.column_stack([X.ravel(), Y.ravel(), np.ones(X.size)])
    z = Z.ravel()
    coef, *_ = np.linalg.lstsq(A, z, rcond=None)
    resid = z - A @ coef
    denom = float(np.std(z)) or 1.0
    return float(np.sqrt(np.mean(resid ** 2)) / denom)


def region_count(Z, xs, ys, decimals=2, area_frac=0.004):
    """Estimate the number of piecewise-linear regions: a PWL surface has a piecewise-CONSTANT
    gradient field, so round local gradients and count clusters holding >= area_frac of the grid.
    Heuristic (grid resolution + rounding bound it) — the region-multiplexer headline number."""
    gy, gx = np.gradient(Z, ys, xs)
    key = np.stack([np.round(gx, decimals), np.round(gy, decimals)], axis=-1).reshape(-1, 2)
    _, counts = np.unique(key, axis=0, return_counts=True)
    return int(np.sum(counts >= area_frac * key.shape[0]))
