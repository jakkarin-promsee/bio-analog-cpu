"""Phase 1 (new) shared reachability — the representational LIMIT of the atom.

Fit the 2-3-3-2 (out0) to synthetic target surfaces with a GENERIC optimizer — NOT the chip's
attribution rule (that's Phase 2 / H1) — weights free/unbounded. The best-fit residual per target
= what the hardware CAN represent, isolated from whether learning can find it. (A LOWER bound on
capacity: ReLU fits are nonconvex, so we take the best of N restarts.)

The fit runs on a numpy mirror of the forward (vectorized, fast). The mirror is verified to match
the real GanglionALU exactly (max abs err 0.0); the caller re-checks the best-fit weights on the
real probe, so we never substitute the clone for the as-built forward.
"""

import numpy as np
from scipy.optimize import least_squares


# ---- synthetic target surfaces (analytic; normalized to zero-mean/unit-std at fit time) ----

def _targets():
    return {
        "plane":      lambda X1, X2: 0.3 * X1 + 0.2 * X2,
        "parabola":   lambda X1, X2: X1 ** 2,
        "paraboloid": lambda X1, X2: 0.1 * (X1 + X2) ** 2,
        "saddle":     lambda X1, X2: X1 * X2,
        "gaussian":   lambda X1, X2: np.exp(-(X1 ** 2 + X2 ** 2) / 0.5),
        "xor":        lambda X1, X2: np.sign(X1) * np.sign(X2),
    }


TARGET_NAMES = list(_targets().keys())


def target_surface(name, X1, X2):
    return _targets()[name](X1, X2)


def normalize(T):
    """zero-mean, unit-std — so residuals are comparable across targets (the model's free output
    layer supplies any scale/offset, so we fit shape, not amplitude)."""
    mu = float(np.mean(T))
    sd = float(np.std(T)) or 1.0
    return (T - mu) / sd, mu, sd


# ---- numpy mirror of the 2-3-3-2 forward out0 (matches alu.py: ReLU@L2, linear@L3/L4) ----

def mirror_out0(w, X1, X2):
    """out[0] over a grid, vectorized. w: length-29 (canonical §7.4 order)."""
    a2 = [np.maximum(w[j * 2] * X1 + w[j * 2 + 1] * X2 + w[6 + j], 0.0) for j in range(3)]
    a3 = [w[18 + k] + w[9 + k * 3] * a2[0] + w[9 + k * 3 + 1] * a2[1] + w[9 + k * 3 + 2] * a2[2]
          for k in range(3)]
    return w[27] + w[21] * a3[0] + w[22] * a3[1] + w[23] * a3[2]


# ---- the fit ----

def fit_to(Tn, X1, X2, n_restart=12, seed=0, ceiling=None, scale_free=False):
    """Fit out0 to a NORMALIZED target array `Tn` over the grid (X1, X2); multi-restart least-squares.
    `ceiling` (rung-1): bound |w| <= ceiling. `scale_free`: regress Tn onto [model_output, 1] each
    step, so amplitude/gain is factored out and only SHAPE is fit. Returns (best_w, norm_resid)."""
    rng = np.random.default_rng(seed)
    t = Tn.ravel()

    def resid(w):
        Z = mirror_out0(w, X1, X2).ravel()
        if not scale_free:
            return Z - t
        A = np.column_stack([Z, np.ones_like(Z)])
        coef, *_ = np.linalg.lstsq(A, t, rcond=None)
        return t - A @ coef

    bounds = (-np.inf, np.inf) if ceiling is None else (-ceiling, ceiling)
    w0_hi = 1.5 if ceiling is None else ceiling

    best_w, best_cost = None, np.inf
    for _ in range(n_restart):
        w0 = rng.uniform(-w0_hi, w0_hi, size=29)
        try:
            sol = least_squares(resid, w0, method="trf", bounds=bounds, max_nfev=3000)
        except Exception:
            continue
        c = float(np.mean(sol.fun ** 2))
        if c < best_cost:
            best_cost, best_w = c, sol.x
    return best_w, float(np.sqrt(best_cost))


def fit_target(name, n_grid=21, n_restart=12, seed=0, domain=(-1.0, 1.0), ceiling=None,
               scale_free=False):
    """Best-fit out0 to a named target over an n_grid^2 grid (wraps `fit_to`). `scale_free` (use it
    under a `ceiling`) factors amplitude out, so the residual measures SHAPE reachability, not gain."""
    g = np.linspace(domain[0], domain[1], n_grid)
    X1, X2 = np.meshgrid(g, g)
    Tn, _, _ = normalize(target_surface(name, X1, X2))
    return fit_to(Tn, X1, X2, n_restart=n_restart, seed=seed, ceiling=ceiling, scale_free=scale_free)
