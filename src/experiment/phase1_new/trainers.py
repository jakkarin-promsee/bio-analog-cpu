"""Phase 1 (new) · Rung 1 — the two LEARNERS (attribution vs gradient).

Rung 0 used an ORACLE (TRF, free weights) to find the best fit the hardware COULD reach. Rung 1 swaps
the oracle for two real learners and watches them move:

  AttributionTrainer : the chip's OWN rule, run on the REAL library — `Brainstem.train_step` drives the
                       Scap update in `scap.py`, the same workflow the whole chip uses. Momentum is the
                       Scap's EMA of its local |a·W| contribution (`alpha`; arc default 0.75, alpha=0 ==
                       no momentum).
  GradientMLP        : textbook gradient descent, written fresh on a DEFAULT stack (numpy) — the project
                       lib can't do exact backprop. Classical heavy-ball momentum (`beta`); NOT Adam
                       (no v_t RMS term; §20.2 #6).

Both carry the same 29-weight layout (canonical §7.4 order, == `reach.mirror_out0`), so a learner's
state renders through the SAME fast mirror (verified == the real ALU, err 0) for every figure. The
*learning* is real-lib; only the *pictures* use the equal mirror.

Optional training-time weight noise (Step 5): gaussian jitter on every stored weight each update step,
the SAME model for both learners — a first peek at an analog substrate (full PVT is Phase 8 / §20.14).
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, reach
from src.example.brainstem import Brainstem
from src.library.scap import (ALPHA as SCAP_ALPHA, MOMENTUM_FLOOR, MOMENTUM_CEILING,
                              W_RAIL as SCAP_RAIL)

STD_SEEDS = harness.STD_SEEDS          # [42, 137, 271, 314, 1729]
# Inputs are POSITIVE. A negative input flips an L2 wire's forward_sign = sign(x·W) sample-to-sample,
# so its updates cancel and the L2 weight decays to 0 (the output collapses to bias). Positive inputs
# keep sign(x·W) = sign(W) constant per wire -> coherent L2 learning. So we feed [0,2] and keep each
# target's FOLD by centering it at the mid-point (the crease still sits inside the positive domain).
DOMAIN = (0.0, 2.0)
CENTER = 0.5 * (DOMAIN[0] + DOMAIN[1])
# Rung-1 shapes span the dividing line attribution actually has:
#   MONOTONIC (attribution learns these): plane (linear), parabola (x1^2, rising over [0,2]).
#   INTERIOR FOLD (attribution can't carve): valley (centered parabola), gaussian (bump), xor (quadrants).
#   parabola vs valley is the SAME base shape, monotonic vs folded -> the crispest contrast.
SHAPES = ["plane", "parabola", "valley", "gaussian", "xor"]


def _target(name, X1, X2):
    """The rung-1 target over the POSITIVE input domain. Some shapes are monotonic (no interior fold),
    some are centered so the feature sits inside the domain — see SHAPES."""
    c = CENTER
    if name == "plane":
        return 0.3 * X1 + 0.2 * X2                                  # monotonic, linear
    if name == "parabola":
        return X1 ** 2                                              # monotonic, curved rise (no fold)
    if name == "valley":
        return (X1 - c) ** 2                                        # interior fold (parabola, centered)
    if name == "gaussian":
        return np.exp(-((X1 - c) ** 2 + (X2 - c) ** 2) / 0.5)      # interior bump (fold)
    if name == "xor":
        return np.sign(X1 - c) * np.sign(X2 - c)                    # quadrants (fold)
    raise KeyError(f"unknown rung-1 shape: {name}")


def xavier_inits(seed):
    """Glorot-uniform init for the 2-3-3-2 (biases 0): per-layer limit sqrt(6/(fan_in+fan_out)).
    Bigger, fan-scaled weights than the plain uniform(-0.5,0.5) -> fewer dead ReLUs / less 'asleep'."""
    rng = np.random.default_rng(seed)
    w = np.zeros(29)
    l2 = float(np.sqrt(6.0 / (2 + 3)))   # L2: fan_in 2, fan_out 3
    l3 = float(np.sqrt(6.0 / (3 + 3)))   # L3: 3, 3
    l4 = float(np.sqrt(6.0 / (3 + 2)))   # L4: 3, 2
    w[0:6] = rng.uniform(-l2, l2, 6)
    w[9:18] = rng.uniform(-l3, l3, 9)
    w[21:27] = rng.uniform(-l4, l4, 6)
    return list(w)


def make_inits(seed, init="uniform"):
    """The init both learners share for a given seed: 'uniform' = uniform(-0.5,0.5) (current default),
    'xavier' = Glorot-uniform (biases 0)."""
    return xavier_inits(seed) if init == "xavier" else harness.random_inits(seed)

# Frozen learning rates — each tuned ONCE to its own multi-seed best, then fixed (§20.2 #1), as
# INDEPENDENT knobs (lr_attr / lr_grad). Both landed at 0.1 (different mechanisms):
#   attr 0.1 -> monotonic parabola ~0.27 (lr-insensitive); interior folds ~0.78 at any lr or init.
#   grad 0.1 -> fold (valley) ~0.13 (lr 0.05 was unstable ~0.87).
LR_ATTR = 0.1
LR_GRAD = 0.1

# Targets are affine-mapped to this common POSITIVE range. The attribution rule broadcasts ONE global
# feedback sign, so (like the demonstrated SLICE-1 regression, run_xor) it needs a coherent single-
# signed target to learn — a zero-mean target makes the sign thrash and nothing grows. The shape metric
# is SCALE-FREE (below), so this offset/scale choice does NOT bias the comparison; it only gives the
# global-pulse rule a usable signal. Gradient is indifferent to it.
TARGET_RANGE = (0.05, 0.85)


# ---- data + the shape-residual metric (one metric everywhere: SCALE-FREE shape residual) ----------

def make_dataset(name, n_grid=12, domain=DOMAIN):
    """Fixed training set: an n_grid^2 grid of (x1, x2) with the named target, min-max mapped to the
    common positive `TARGET_RANGE`. Returns (X (M,2), t (M,))."""
    g = np.linspace(domain[0], domain[1], n_grid)
    X1, X2 = np.meshgrid(g, g)
    T = _target(name, X1, X2)
    lo, hi = TARGET_RANGE
    span = (T.max() - T.min()) or 1.0
    Tm = lo + (hi - lo) * (T - T.min()) / span
    return np.column_stack([X1.ravel(), X2.ravel()]), Tm.ravel()


def resid_w29(w, name, n_grid=31, domain=DOMAIN):
    """SCALE-FREE shape residual of out0(w) vs the named target on an n_grid^2 grid (mirror == ALU):
    regress the normalized target onto [out0, 1], so amplitude and offset are factored out and only
    SHAPE is scored (the rung-0 'shape cost' metric, reach.fit_to scale_free). 0 = perfect shape,
    ~1 = no better than the mean (no shape found — e.g. a flat/asleep output)."""
    g = np.linspace(domain[0], domain[1], n_grid)
    X1, X2 = np.meshgrid(g, g)
    Tn, _, _ = reach.normalize(_target(name, X1, X2))
    Z = reach.mirror_out0(np.asarray(w, float), X1, X2).ravel()
    t = Tn.ravel()
    A = np.column_stack([Z, np.ones_like(Z)])
    coef, *_ = np.linalg.lstsq(A, t, rcond=None)
    return float(np.sqrt(np.mean((t - A @ coef) ** 2)))


def surface_w29(w, xs, ys):
    """out0(w) over the render grid (for the film frames)."""
    X1, X2 = np.meshgrid(xs, ys)
    return reach.mirror_out0(np.asarray(w, float), X1, X2)


def display_norm(Z, eps=1e-4):
    """Shape-normalize a surface for the film (zero-mean / unit-std), so SHAPE is comparable across
    panels regardless of amplitude. A flat/asleep panel (std < eps) renders uniform (all zeros) —
    which is exactly the right read: 'no shape here yet'."""
    Z = np.asarray(Z, float)
    sd = float(Z.std())
    return (Z - Z.mean()) / sd if sd > eps else np.zeros_like(Z)


def oracle_w29(name, n_grid=21, n_restart=12, seed=0):
    """TRF best-fit weights for a shape on the positive (centered) domain — the 'expected' ceiling
    drawn on the film. Free weights (NOT the chip rule); the most the hardware could represent."""
    g = np.linspace(*DOMAIN, n_grid)
    X1, X2 = np.meshgrid(g, g)
    Tn, _, _ = reach.normalize(_target(name, X1, X2))
    w, _ = reach.fit_to(Tn, X1, X2, n_restart=n_restart, seed=seed)
    return w


# ---- the gradient learner (numpy, default stack) -------------------------------------------------

class GradientMLP:
    """Textbook 2-3-3-2 (out0 only) trained by gradient descent on the numpy mirror. Heavy-ball
    momentum (`beta`); NOT Adam. Carries the canonical 29-vector so it renders == the real ALU."""

    def __init__(self, w29):
        w = np.asarray(w29, float).copy()
        self._rest = w                                   # keep out1 weights for a faithful 29-vector
        self.W2 = np.array([[w[0], w[1]], [w[2], w[3]], [w[4], w[5]]])      # (3,2)
        self.b2 = np.array([w[6], w[7], w[8]])                              # (3,)
        self.W3 = np.array([[w[9], w[10], w[11]], [w[12], w[13], w[14]],
                            [w[15], w[16], w[17]]])                         # (3,3)
        self.b3 = np.array([w[18], w[19], w[20]])                           # (3,)
        self.wout = np.array([w[21], w[22], w[23]])                         # (3,)  out0 readout
        self.bout = float(w[27])
        self.vW2 = np.zeros_like(self.W2); self.vb2 = np.zeros_like(self.b2)
        self.vW3 = np.zeros_like(self.W3); self.vb3 = np.zeros_like(self.b3)
        self.vwout = np.zeros_like(self.wout); self.vbout = 0.0

    def to_w29(self):
        w = self._rest.copy()
        w[0], w[1] = self.W2[0]; w[2], w[3] = self.W2[1]; w[4], w[5] = self.W2[2]
        w[6], w[7], w[8] = self.b2
        w[9:12] = self.W3[0]; w[12:15] = self.W3[1]; w[15:18] = self.W3[2]
        w[18:21] = self.b3
        w[21:24] = self.wout; w[27] = self.bout
        return w

    def _forward1(self, x):
        z2 = self.W2 @ x + self.b2
        a2 = np.maximum(z2, 0.0)
        a3 = self.W3 @ a2 + self.b3          # L3 linear (matches alu.py / mirror_out0)
        y = self.wout @ a3 + self.bout
        return z2, a2, a3, y

    def train_epoch(self, X, t, lr, beta=0.0, order=None, noise_std=0.0, rng=None, clip=harness.W_RAIL):
        idx = range(len(X)) if order is None else order
        for i in idx:
            x = X[i]
            z2, a2, a3, y = self._forward1(x)
            dy = 2.0 * (y - t[i])                         # d/dy (y - t)^2
            dwout = dy * a3; dbout = dy
            dz3 = dy * self.wout                          # L3 linear -> dz3 == da3
            dW3 = np.outer(dz3, a2); db3 = dz3
            dz2 = (self.W3.T @ dz3) * (z2 > 0)            # ReLU @ L2
            dW2 = np.outer(dz2, x); db2 = dz2
            # EMA momentum:  v = beta*v + (1-beta)*grad ;  w -= lr*v   (beta=0 -> vanilla SGD). This
            # keeps the step SCALE constant (unlike heavy-ball v=beta*v+grad, which amplifies by ~1/(1-beta))
            # and matches the attribution momentum's EMA form, so the two are comparable.
            b1 = 1.0 - beta
            self.vW2 = beta * self.vW2 + b1 * dW2; self.W2 -= lr * self.vW2
            self.vb2 = beta * self.vb2 + b1 * db2; self.b2 -= lr * self.vb2
            self.vW3 = beta * self.vW3 + b1 * dW3; self.W3 -= lr * self.vW3
            self.vb3 = beta * self.vb3 + b1 * db3; self.b3 -= lr * self.vb3
            self.vwout = beta * self.vwout + b1 * dwout; self.wout -= lr * self.vwout
            self.vbout = beta * self.vbout + b1 * dbout; self.bout -= lr * self.vbout
            if noise_std and rng is not None:
                self._jitter(noise_std, rng, clip)

    def _jitter(self, sigma, rng, clip):
        for arr in (self.W2, self.b2, self.W3, self.b3, self.wout):
            arr += rng.normal(0.0, sigma, size=arr.shape)
            np.clip(arr, -clip, clip, out=arr)
        self.bout = float(np.clip(self.bout + rng.normal(0.0, sigma), -clip, clip))


# ---- the attribution learner (the REAL library) --------------------------------------------------

class AttributionTrainer:
    """The chip's own rule on the REAL library: a single-Ganglion Brainstem learned via
    `Brainstem.train_step` -> the Scap update (`scap.py`). `alpha` = Scap momentum EMA (None = arc's
    0.75; 0.0 = no momentum). `lr` is the Brainstem pulse scale."""

    def __init__(self, w29, lr, alpha=None, seed=0):
        self._holder = {}
        build = harness._make_build(list(w29), alpha=alpha, _out=self._holder)
        spec = {"build": build, "in_slot": 0, "out_slot": 2, "n_in": 2, "n_out": 2}
        self.bs = Brainstem([spec], lr=lr, seed=seed)
        self.scaps = self._holder["ganglion"].scaps      # slot order 0..28 == canonical 29-vector

    def to_w29(self):
        return np.array([s.sign * s.weight for s in self.scaps], float)

    def train_epoch(self, X, t, lr=None, beta=0.0, order=None, noise_std=0.0, rng=None,
                    clip=harness.W_RAIL):
        idx = range(len(X)) if order is None else order
        for i in idx:
            self.bs.train_step([float(X[i, 0]), float(X[i, 1])], float(t[i]))
            if noise_std and rng is not None:
                self._jitter(noise_std, rng, clip)

    def _jitter(self, sigma, rng, clip):
        for s in self.scaps:                              # gaussian jitter on the stored cap magnitude
            s.weight = float(np.clip(s.weight + rng.normal(0.0, sigma), 0.0, clip))


# ---- the attribution learner, NUMPY replica (for fast experimentation) ---------------------------

class AttributionNP:
    """A pure-NumPy replica of the chip's attribution rule (scap.py + alu.py), with NO wires — so the
    rule itself is easy to read and modify ('try something') without the lib's signal plumbing. It
    mirrors the real update exactly and is verified == `AttributionTrainer` in the no-noise case
    (see `verify_np_eq_lib`). The lib version (`AttributionTrainer`) stays the source of truth.

    Per sample (matching Brainstem.train_step -> Scap):
      1. forward with the current signed weights; per wire record contribution |a·W| and sign(a·W)
         (a = signed input @ L2, post-ReLU a2 @ L3, linear a3 @ L4; a = 1 for biases).
      2. momentum  = alpha*momentum + (1-alpha)*contribution  (EMA), clamped [FLOOR, CEIL]; latch fsign.
      3. err = target - out0; feedback = sign(err); pulse = lr*|err|.
      4. delta = pulse*momentum*(fsign*feedback); growth saturates by (RAIL - mag)/RAIL; mag += delta;
         reflect at 0 (flip sign); clamp at RAIL.
    """

    def __init__(self, w29, lr, alpha=None):
        w = np.asarray(w29, float)
        self.mag = np.abs(w)                              # sign-magnitude, like the Scap
        self.sign = np.where(w >= 0.0, 1.0, -1.0)
        self.momentum = np.ones(29)
        self.fsign = np.ones(29)
        self.lr = lr
        self.alpha = SCAP_ALPHA if alpha is None else alpha

    def to_w29(self):
        return self.sign * self.mag

    def _forward_contrib(self, x):
        """out0 + per-wire contribution/sign, structured exactly like GanglionALU._run."""
        w = self.sign * self.mag
        contrib = np.zeros(29)
        fs = np.ones(29)

        def line(idx, a, ww):
            aw = a * ww
            contrib[idx] = abs(aw)
            fs[idx] = 1.0 if aw >= 0.0 else -1.0
            return aw

        L1 = (float(x[0]), float(x[1]))
        a2 = np.zeros(3)
        for j in range(3):
            s = line(j * 2, L1[0], w[j * 2]) + line(j * 2 + 1, L1[1], w[j * 2 + 1]) + line(6 + j, 1.0, w[6 + j])
            a2[j] = s if s > 0.0 else 0.0                 # ReLU @ L2
        a3 = np.zeros(3)
        for k in range(3):
            s = line(18 + k, 1.0, w[18 + k])
            for j in range(3):
                s += line(9 + k * 3 + j, a2[j], w[9 + k * 3 + j])
            a3[k] = s                                     # linear @ L3
        out0 = line(27, 1.0, w[27]) + sum(line(21 + k, a3[k], w[21 + k]) for k in range(3))
        # out1's wires (24,25,26,28) are updated too in the real lib -> record their contributions
        _ = line(28, 1.0, w[28]) + sum(line(24 + k, a3[k], w[24 + k]) for k in range(3))
        return out0, contrib, fs

    def train_epoch(self, X, t, lr=None, beta=0.0, order=None, noise_std=0.0, rng=None, clip=SCAP_RAIL):
        idx = range(len(X)) if order is None else order
        for i in idx:
            out0, contrib, fs = self._forward_contrib(X[i])
            self.momentum = self.alpha * self.momentum + (1.0 - self.alpha) * contrib
            np.clip(self.momentum, MOMENTUM_FLOOR, MOMENTUM_CEILING, out=self.momentum)
            self.fsign = fs
            err = float(t[i]) - out0
            feedback = 1.0 if err >= 0.0 else -1.0
            delta = (self.lr * abs(err)) * self.momentum * (self.fsign * feedback)
            grow = delta > 0.0                            # growth toward the rail saturates
            delta = np.where(grow, delta * np.maximum(0.0, (SCAP_RAIL - self.mag) / SCAP_RAIL), delta)
            self.mag = self.mag + delta
            neg = self.mag < 0.0                          # crossed zero -> reflect + flip sign
            self.mag = np.where(neg, -self.mag, self.mag)
            self.sign = np.where(neg, -self.sign, self.sign)
            np.clip(self.mag, None, SCAP_RAIL, out=self.mag)
            if noise_std and rng is not None:
                self.mag = np.clip(self.mag + rng.normal(0.0, noise_std, size=29), 0.0, clip)


# ---- the shared training loop --------------------------------------------------------------------

def train_with_snapshots(learner, X, t, name, epochs, snap_epochs=(), lr=None, beta=0.0,
                         noise_std=0.0, data_seed=0, eval_grid=31):
    """Train `learner` for `epochs` online passes (shuffled, reproducible from `data_seed`). Returns
    (loss_curve shape (epochs+1,), snapshots {epoch: w29}). One metric: normalized RMS residual.

    Same `data_seed` -> identical sample order, so attribution and gradient see the same stream
    (the §20.2 'one thing changed' is the rule). Noise (if any) is the same model, reproducibly seeded.
    """
    rng_order = np.random.default_rng(data_seed)
    rng_noise = np.random.default_rng(data_seed + 9973) if noise_std else None
    M = len(X)
    snaps = {}
    losses = [resid_w29(learner.to_w29(), name, n_grid=eval_grid)]
    if 0 in snap_epochs:
        snaps[0] = learner.to_w29()
    for ep in range(1, epochs + 1):
        order = rng_order.permutation(M)
        learner.train_epoch(X, t, lr=lr, beta=beta, order=order, noise_std=noise_std, rng=rng_noise)
        losses.append(resid_w29(learner.to_w29(), name, n_grid=eval_grid))
        if ep in snap_epochs:
            snaps[ep] = learner.to_w29()
    return np.array(losses), snaps


def make_attr(inits, alpha=None, backend="lib", lr=None):
    """The attribution learner. backend='lib' = the REAL library (AttributionTrainer, source of truth);
    backend='numpy' = the wire-free replica (AttributionNP, for fast experimentation)."""
    lr = LR_ATTR if lr is None else lr
    if backend == "numpy":
        return AttributionNP(inits, lr=lr, alpha=alpha)
    return AttributionTrainer(inits, lr=lr, alpha=alpha)


def run_pair(name, seed, epochs, snap_epochs=(), alpha=None, beta=0.0, noise_std=0.0,
             n_grid=12, eval_grid=31, attr_backend="lib", init="uniform",
             lr_attr=None, lr_grad=None):
    """Train BOTH learners from the SAME init on `name`. Returns each learner's loss curve, snapshots,
    and final w29. `alpha`/`beta` set momentum; `noise_std` the analog jitter; `attr_backend` picks the
    attribution impl ('lib'/'numpy'); `init` the init scheme ('uniform'/'xavier'); `lr_attr`/`lr_grad`
    override the frozen learning rates (each rule its own)."""
    inits = make_inits(seed, init)
    X, t = make_dataset(name, n_grid=n_grid)
    attr = make_attr(inits, alpha=alpha, backend=attr_backend, lr=lr_attr)
    grad = GradientMLP(inits)
    lr_g = LR_GRAD if lr_grad is None else lr_grad
    al, asnap = train_with_snapshots(attr, X, t, name, epochs, snap_epochs,
                                     noise_std=noise_std, data_seed=seed, eval_grid=eval_grid)
    gl, gsnap = train_with_snapshots(grad, X, t, name, epochs, snap_epochs, lr=lr_g, beta=beta,
                                     noise_std=noise_std, data_seed=seed, eval_grid=eval_grid)
    return {
        "attr": {"loss": al, "snaps": asnap, "final": attr.to_w29()},
        "grad": {"loss": gl, "snaps": gsnap, "final": grad.to_w29()},
    }


def median_iqr(curves):
    """Stack a list of equal-length loss curves -> (median, q25, q75) per epoch."""
    A = np.vstack(curves)
    return np.median(A, axis=0), np.percentile(A, 25, axis=0), np.percentile(A, 75, axis=0)


def verify_np_eq_lib(name="parabola", seed=42, epochs=40, alpha=0.0, n_grid=12):
    """Sanity: the NumPy replica must match the REAL lib weight-for-weight in the no-noise case (same
    init, same sample order). Returns the max abs difference in the final 29-vector."""
    inits = harness.random_inits(seed)
    X, t = make_dataset(name, n_grid=n_grid)
    lib = AttributionTrainer(inits, lr=LR_ATTR, alpha=alpha)
    npy = AttributionNP(inits, lr=LR_ATTR, alpha=alpha)
    for learner in (lib, npy):
        rng = np.random.default_rng(seed)            # identical sample order for both
        for _ in range(epochs):
            learner.train_epoch(X, t, order=rng.permutation(len(X)))
    return float(np.max(np.abs(lib.to_w29() - npy.to_w29())))
