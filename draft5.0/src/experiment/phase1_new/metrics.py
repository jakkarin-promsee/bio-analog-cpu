"""Phase 1 (new) shared metrics — read numbers off a surface so eyes + numbers agree.

The point of rung-0 is to SHOW the structure, not score it, so the headline here is `region_labels`
(a picture of the regions), not a single number. `output_range` and `planar_residual` are kept as
small honesty checks next to the figures.
"""

import numpy as np


def output_range(Z):
    """min, max of a surface — the usable output swing (the Ganglion's 'voice')."""
    return float(np.min(Z)), float(np.max(Z))


def planar_residual(Z, xs, ys):
    """Normalized RMS residual of the best-fit single plane. 0 = the whole surface IS one plane
    y=ax+b (no carve); larger = the atom is actually folding the plane into pieces."""
    X, Y = np.meshgrid(xs, ys)
    A = np.column_stack([X.ravel(), Y.ravel(), np.ones(X.size)])
    z = Z.ravel()
    coef, *_ = np.linalg.lstsq(A, z, rcond=None)
    resid = z - A @ coef
    denom = float(np.std(z)) or 1.0
    return float(np.sqrt(np.mean(resid ** 2)) / denom)


def region_labels(Z, xs, ys, decimals=2, area_frac=0.004):
    """Label every grid point by WHICH linear region it sits in.

    A piecewise-linear surface has a piecewise-CONSTANT gradient: inside one region the slope
    (gx, gy) is fixed (that region's single plane y = gx*x1 + gy*x2 + c), and it jumps at a crease.
    So we round the local gradient and group points that share it. Big groups (>= area_frac of the
    grid) are the real regions, renumbered 0..K-1 by size; the thin transition pixels at creases get
    NaN so they render as blank boundary lines.

    Returns (labels, n_regions): `labels` is a float image (NaN on boundaries), `n_regions` = K.
    """
    gy, gx = np.gradient(Z, ys, xs)
    key = np.stack([np.round(gx, decimals), np.round(gy, decimals)], axis=-1).reshape(-1, 2)
    uniq, inv, counts = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    big = counts >= area_frac * key.shape[0]
    new_id = np.full(len(uniq), -1, dtype=int)
    k = 0
    for idx in np.argsort(-counts):       # biggest region gets id 0, etc. (stable colors)
        if big[idx]:
            new_id[idx] = k
            k += 1
    labels = new_id[inv].reshape(Z.shape).astype(float)
    labels[labels < 0] = np.nan
    return labels, k


def region_count(Z, xs, ys, decimals=2, area_frac=0.004):
    """Just the number K of linear regions (wraps region_labels)."""
    _, k = region_labels(Z, xs, ys, decimals=decimals, area_frac=area_frac)
    return k
