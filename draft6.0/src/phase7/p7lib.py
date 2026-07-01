"""
p7lib — the Phase-7 apparatus: NAME THE FROZEN BULK (the ~20% GD "namer" bake-off). A CHIP NETLIST, not normal
Python: every class is a substrate element; every reuse is a *tested* primitive carried forward unchanged, because
the project's recurring silent killer is a missing sign/direction and that bug lives in re-implementations — so we
re-implement nothing we can import, and every trained head gets an FD gradient check + every head-port an
equivalence guard before it may score a rung.

The device under test = the FROZEN Phase-6 cell `NoiseAugContrast` (SCFFContrastOverlap temp0.2/w2, L12, no
residual, + one iid-noise-augmented InfoNCE view σ_aug=1.0). GD reads its taps, never writes them (P2.5 envelope).

Reused, NOT re-implemented (imported through p6lib, which re-exports p5/p4/p3/p2):
  p6lib : NoiseAugContrast (the P6 committed cell), COMMITTED, train_cell, SCFFContrastOverlap,
          readout_feats / linear_probe / fit_readout / race_bp, acc_matrix_metrics, CISTREAM_TASKS, synth_stream,
          load_digits_split / load_cifar_flat, make_gauss, effective_rank, normalize / relu / EPS,
          equivalence_guard / fd_gradient_check, continual_safety (the harness we EXTEND, not carry)
  models_extra : MLP (the hand-coded Adam MLP — the linear-softmax floor, the MLP head, the tested backward)

NEW here (Phase 7) — the namer taxonomy (one axis = spine-purity, left=direction-pure → right=max-magnitude):
  Head protocol      : every head has .fit(F,Y) -> self, .logits(F) -> [N,C], .predict(F) -> [N],
      .rescaled_logits(F, scales) (the per-class norm nuisance for spine-cleanliness (a)); scores are argmax-of-logits.
  LinearSoftmaxHead  : the convex FLOOR (gradient linear-softmax = the P5/linear_probe head). magnitude.
  CosineHead(mode)   : ncm (streaming mean of L2-normed feats, no gradient) | softmax (trained cosine-normed
      weights, gradient). THE SPINE-PURE head — cos is invariant to per-class weight norm (flip ≈ 0 by construction).
  NCMHead            : running class mean, Euclidean. distance = a magnitude (recency-robust, not direction-reading).
  SLDAHead           : running per-class mean + ONE tied covariance -> linear-softmax w_c=Σ⁻¹μ_c. the cheaper cov middle.
  FeCAMHead          : running per-class mean + PER-CLASS covariance, correlation-normalized Mahalanobis. the
      max-magnitude pole / the closed-form multimodality escape.
  RanPACHead         : frozen random ReLU projection φ=relu(Wr·f) -> running Gram + ridge prototype W=(G+λI)⁻¹M.
  RLSHead            : the analytic ridge WITHOUT the projection (ACIL/F-OAL family). RanPAC = RLS on an expansion.
  GKEALHead          : Gaussian-kernel (RFF) feature map -> analytic solve (the closed-form non-linear P7.2 fallback).
  MLPHead            : a 2-layer GD head (the non-convex anchor; wraps fit_readout) — also reproduces the OLD
      continual harness bit-for-bit (the P7.4 equivalence guard).
  RandProjBulk       : the RanDumb skeptic control — a frozen random ReLU projection replacing the SCFF bulk as the
      feature source; source ∈ {taps (fair), pixels (harsher, true RanDumb)}.
  continual_safety_heads : EXTEND p6lib.continual_safety to accept a head (it hard-wires fit_readout). Each head
      consolidates by its NATIVE sleep rule (closed-form: recompute stats on the replay buffer; gradient: GD-refit).
      Guard: the MLP head through this ≡ the old hard-coded fit_readout path bit-for-bit.
  spine_cleanliness  : (a) argmax-flip under per-class weight/prototype norm rescale (cosine≈0); (b) old-class acc
      drop under the ACTUAL bursty stream (the task-recency-bias read — NOT synthetic inflation, circular for cosine).
  multimodality_probe: per-class n-modes / silhouette / GMM-BIC in the NATURAL frozen tap space (P7.2 decision-bearer).
  imbalance guards   : logit_adjust, balanced_softmax, class_balanced_reservoir (trained heads); air_rectify
      (Analytic Imbalance Rectifier — the no-gradient family's guard).
  readout_cost       : the forward-MAC + Gram/solve-dim PROXY meter (descriptive-only; real meter = Phase 8).
  aaa_curve          : area under acc vs log10-samples (the AAA static metric).
  guards             : head_equiv_guard (cosine(ncm)≡nearest-normalized-prototype; cosine-softmax(τ→∞)≡linear;
      linear head ≡ linear_probe), fd_head_grad (FD<1e-5 on every trained head), harness_equiv_guard
      (continual_safety_heads(MLP) ≡ old continual_safety). Run BEFORE any head scores (P7.0). ANY guard fails → STOP.

numpy only. The run layer sets OMP_NUM_THREADS=1 + python -u + PYTHONIOENCODING=utf-8 (OpenMP-phantom + cp874 guards)
before importing this. NO sklearn for compute (load_digits/load_cifar_flat are data-only, safe).
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase6"))                # p6lib (re-exports p5/p4/p3/p2)
sys.path.insert(0, os.path.join(_HERE, "..", "phase1", "exp0"))        # models_extra (MLP) — belt-and-braces
from p6lib import (NoiseAugContrast, COMMITTED, train_cell, SCFFContrastOverlap,               # noqa: E402
                   readout_feats, linear_probe, fit_readout, race_bp, acc_matrix_metrics,
                   CISTREAM_TASKS, synth_stream, load_digits_split, load_cifar_flat, make_gauss,
                   effective_rank, normalize, relu, EPS, equivalence_guard, fd_gradient_check)
from p5lib import ours_budget, n_w                                     # noqa: E402  (NOT re-exported by p6lib)
from models_extra import MLP                                            # noqa: E402

# ---- the FROZEN Phase-6 committed cell config (the device under test — NOT re-derived) ----
# NoiseAugContrast = the frozen Phase-5 cell (temp0.2/w2, L12, no residual) + one iid-noise-augmented view σ_aug=1.0.
AUG = dict(sig_aug=1.0, variant="iid", loss="infonce")                 # the P6.8 committed noise-hardening

__all__ = [
    "COMMITTED", "AUG", "make_committed_cell", "train_cell", "all_tap_feats", "trunc_feats",
    "LinearSoftmaxHead", "CosineHead", "NCMHead", "SLDAHead", "FeCAMHead", "RanPACHead", "RLSHead",
    "GKEALHead", "MLPHead", "HEAD_FACTORIES", "make_head", "RandProjBulk", "KNOB_GRIDS", "select_head_knob",
    "continual_safety_heads", "continual_head_metrics", "stream_cache", "eval_head_on_cache",
    "spine_cleanliness", "spineflip_rescale", "recency_drop_bursty", "multimodality_probe",
    "logit_adjust", "balanced_softmax", "class_balanced_reservoir", "air_rectify",
    "readout_cost", "aaa_curve", "jsonsafe",
    "head_equiv_guard", "fd_head_grad", "harness_equiv_guard",
    # carried
    "NoiseAugContrast", "SCFFContrastOverlap", "readout_feats", "linear_probe", "fit_readout", "race_bp",
    "acc_matrix_metrics", "CISTREAM_TASKS", "synth_stream", "load_digits_split", "load_cifar_flat",
    "make_gauss", "effective_rank", "normalize", "relu", "EPS", "equivalence_guard", "fd_gradient_check",
    "ours_budget", "n_w",
]


# ============================================================ the device under test (the frozen bulk)
def make_committed_cell(dims, seed):
    """The FROZEN Phase-6 committed cell: NoiseAugContrast (temp0.2/w2, L12, no residual, +iid-noise view σ_aug=1.0).
    Phase 7 names THIS. GD reads its taps; it is never re-trained or re-tuned by the namer."""
    return NoiseAugContrast(dims, seed=seed, **AUG, **COMMITTED)


def all_tap_feats(cell, X):
    """The canonical readout feature source: all-tap concatenation of the L layer reps (L·W-D). The P5 fixed
    reader's peak-accuracy tap. Every rung LOADS the frozen version P7.0 pins — none recomputes (no-baseline-drift)."""
    return readout_feats(cell.infer(X), None)


def trunc_feats(cell, X, k):
    """The short-truncation read (the P5 fixed reader on the continual home): the LAST k layer reps concatenated."""
    return readout_feats(cell.infer(X), k)


def _onehot(Y, C):
    O = np.zeros((len(Y), C)); O[np.arange(len(Y)), Y] = 1.0
    return O


def _l2n(A):
    """L2 row-normalize (p2lib.normalize(a,'lengthnorm')) — the per-sample unit-norm used by the cosine/RanDumb paths."""
    A = np.atleast_2d(A)
    return A / (np.linalg.norm(A, axis=1, keepdims=True) + EPS)


def _spd_inv(M):
    """Invert a shrinkage-regularized (PD) matrix by fast LU; fall back to the SVD pseudo-inverse if singular.
    The covariance heads add a shrinkage ridge, so LU is safe and ~3x faster than pinv on the 768-D tap space."""
    try:
        return np.linalg.inv(M)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(M)


def jsonsafe(o):
    """Recursively cast numpy scalars/arrays/bools to plain Python types so json.dump never chokes (the manifests)."""
    if isinstance(o, dict):
        return {k: jsonsafe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonsafe(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonsafe(o.tolist())
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    return o


# ============================================================ the namer taxonomy — heads
# Every head: .fit(F,Y) -> self ; .logits(F) -> [N,C] ; .predict(F) ; .rescaled_logits(F, scales[C]) (spine probe (a))
class LinearSoftmaxHead:
    """The convex FLOOR: a gradient linear-softmax (= linear_probe's model = the P5 readout family). A magnitude
    head (w_c·f + b_c). PROBE_EP epochs, Adam. The reference every head is measured against."""

    def __init__(self, C, seed=0, epochs=120, lr=3e-3, batch=64):
        self.C = C; self.seed = seed; self.epochs = epochs; self.lr = lr; self.batch = batch; self.mlp = None

    def fit(self, F, Y):
        self.mlp = MLP([F.shape[1], self.C], self.seed, lr=self.lr)
        rng = np.random.default_rng(self.seed)
        for _ in range(self.epochs):
            idx = rng.permutation(len(F))
            for s in range(0, len(F), self.batch):
                self.mlp.train_step(F[idx[s:s + self.batch]], Y[idx[s:s + self.batch]])
        return self

    def logits(self, F):
        return self.mlp.forward(F)

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        W = self.mlp.W[-1]; b = self.mlp.b[-1]                          # [C,d], [C]
        return F @ (W * scales[:, None]).T + b * scales                 # per-class weight-norm nuisance


class CosineHead:
    """THE SPINE-PURE head. mode='ncm': prototype = streaming mean of L2-normalized features, no gradient;
    logit = (f/‖f‖)·(w_c/‖w_c‖)/τ. mode='softmax': trained cosine-normalized weights (gradient, Adam, FD-checked).
    Classifies by ANGLE, so a per-class weight-norm nuisance cannot move the verdict (argmax-flip ≈ 0)."""

    def __init__(self, C, tau=0.1, mode="ncm", seed=0, epochs=120, lr=1e-2, batch=64):
        self.C = C; self.tau = float(tau); self.mode = mode
        self.seed = seed; self.epochs = epochs; self.lr = lr; self.batch = batch; self.W = None

    @staticmethod
    def _unit(A):
        return A / (np.linalg.norm(A, axis=1, keepdims=True) + EPS)

    def fit(self, F, Y):
        Fn = self._unit(F)
        if self.mode == "ncm":
            self.W = np.stack([Fn[Y == c].mean(0) if (Y == c).any() else np.zeros(F.shape[1])
                               for c in range(self.C)])                 # class mean of normalized feats
            return self
        # cosine-softmax: gradient on cosine-normalized weights (init at the NCM protos → @init ≡ cosine-NCM)
        rng = np.random.default_rng(self.seed)
        self.W = np.stack([Fn[Y == c].mean(0) if (Y == c).any() else rng.standard_normal(F.shape[1]) * 0.01
                           for c in range(self.C)]).astype(np.float64)
        m = [np.zeros_like(self.W)]; v = [np.zeros_like(self.W)]; b1, b2, eps, t = 0.9, 0.999, 1e-8, 0
        for _ in range(self.epochs):
            idx = rng.permutation(len(Fn))
            for s in range(0, len(Fn), self.batch):
                fb = Fn[idx[s:s + self.batch]]; yb = Y[idx[s:s + self.batch]]; B = len(fb)
                g = self._grad(fb, yb, B); t += 1
                m[0] = b1 * m[0] + (1 - b1) * g; v[0] = b2 * v[0] + (1 - b2) * g * g
                mh = m[0] / (1 - b1 ** t); vh = v[0] / (1 - b2 ** t)
                self.W -= self.lr * mh / (np.sqrt(vh) + eps)
        return self

    def _grad(self, Fn, Y, B):
        """dL/dW of cosine-softmax cross-entropy (FD-checked in fd_head_grad). Fn already unit-norm."""
        nc = np.linalg.norm(self.W, axis=1) + EPS                       # [C]
        Wn = self.W / nc[:, None]
        Z = (Fn @ Wn.T) / self.tau                                      # [B,C]
        P = softmax(Z, axis=1); P[np.arange(B), Y] -= 1.0; dZ = P / B   # [B,C]
        A = dZ.T @ Fn                                                   # [C,d]  sum_i dZ_ic Fn_i
        sc = (dZ * Z).sum(0)                                            # [C]    sum_i dZ_ic Z_ic
        return (A - self.tau * sc[:, None] * Wn) / (self.tau * nc[:, None])

    def logits(self, F):
        Fn = self._unit(F); Wn = self._unit(self.W)
        return (Fn @ Wn.T) / self.tau

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        Fn = self._unit(F); Wn = self._unit(self.W * scales[:, None])   # re-normalized → scale cancels → flip 0
        return (Fn @ Wn.T) / self.tau


class NCMHead:
    """Nearest-Class-Mean, Euclidean. logit_c = -‖f-μ_c‖² = 2 f·μ_c - ‖μ_c‖² (drop the ‖f‖² const). A DISTANCE =
    a magnitude (recency-robust because it has no trained softmax weights to inflate — NOT direction-reading)."""

    def __init__(self, C, seed=0):
        self.C = C; self.mu = None

    def fit(self, F, Y):
        self.mu = np.stack([F[Y == c].mean(0) if (Y == c).any() else np.zeros(F.shape[1]) for c in range(self.C)])
        return self

    def logits(self, F):
        return 2.0 * F @ self.mu.T - (self.mu * self.mu).sum(1)[None, :]

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        mu = self.mu * scales[:, None]                                  # scale each prototype → distance moves → flip
        return 2.0 * F @ mu.T - (mu * mu).sum(1)[None, :]


class SLDAHead:
    """Deep-SLDA: running per-class mean + ONE tied (shared) covariance. Algebraically a linear-softmax with
    w_c=Σ⁻¹μ_c, b_c=−½μ_cᵀΣ⁻¹μ_c (a magnitude — the ‖μ‖²-scaled per-class bias). The cheaper covariance MIDDLE."""

    def __init__(self, C, shrinkage=1e-2, seed=0):
        self.C = C; self.shrinkage = float(shrinkage); self.W = None; self.b = None

    def fit(self, F, Y):
        d = F.shape[1]
        mu = np.stack([F[Y == c].mean(0) if (Y == c).any() else np.zeros(d) for c in range(self.C)])
        Xc = F - mu[Y]                                                  # within-class centering
        Sig = (Xc.T @ Xc) / max(len(F), 1)
        Sig = (1 - self.shrinkage) * Sig + self.shrinkage * np.trace(Sig) / d * np.eye(d)
        P = _spd_inv(Sig)                                              # precision (tied)
        self.W = mu @ P                                                 # [C,d]  w_c = Σ⁻¹ μ_c
        self.b = -0.5 * (mu @ P * mu).sum(1)                           # b_c = -0.5 mu_c^T Sigma^-1 mu_c
        self.mu = mu
        return self

    def logits(self, F):
        return F @ self.W.T + self.b[None, :]

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        return F @ (self.W * scales[:, None]).T + self.b * scales


class FeCAMHead:
    """FeCAM: running per-class mean + PER-CLASS covariance, correlation-normalized (paper) + shrinkage,
    anisotropic Mahalanobis. logit_c = −d_c (argmax = min Mahalanobis). The MAX-magnitude pole (whitened distance;
    whitening was rejected-as-a-lever in P5) AND the closed-form heterogeneity escape."""

    def __init__(self, C, shrinkage=1.0, seed=0):
        self.C = C; self.gamma = float(shrinkage); self.mu = None; self.Pinv = None

    def fit(self, F, Y):
        d = F.shape[1]; mus = []; Pinvs = []
        for c in range(self.C):
            Fc = F[Y == c]
            if len(Fc) <= 1:
                mus.append(Fc.mean(0) if len(Fc) else np.zeros(d)); Pinvs.append(np.eye(d)); continue
            mu = Fc.mean(0); Xc = Fc - mu
            Sig = (Xc.T @ Xc) / len(Fc)
            dg = np.sqrt(np.clip(np.diag(Sig), EPS, None))
            Cn = Sig / (dg[:, None] * dg[None, :])                      # correlation normalization (FeCAM)
            Cn = Cn + self.gamma * np.eye(d)                            # shrinkage (diagonal-dominant)
            mus.append(mu); Pinvs.append(_spd_inv(Cn * (dg[:, None] * dg[None, :])))
        self.mu = np.stack(mus); self.Pinv = np.stack(Pinvs)
        return self

    def _maha(self, F):
        out = np.empty((len(F), self.C))
        for c in range(self.C):
            D = F - self.mu[c]
            out[:, c] = -np.einsum("nd,de,ne->n", D, self.Pinv[c], D)   # −Mahalanobis²
        return out

    def logits(self, F):
        return self._maha(F)

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        out = np.empty((len(F), self.C))
        for c in range(self.C):
            D = F - self.mu[c] * scales[c]                              # scale prototype → Mahalanobis moves → flip
            out[:, c] = -np.einsum("nd,de,ne->n", D, self.Pinv[c], D)
        return out


class RanPACHead:
    """RanPAC: a FROZEN random ReLU projection φ=relu(Wr·f) then a ridge prototype W=(G+λI)⁻¹M, G=Σφφᵀ,
    M=Σφ·onehot. Streaming / no-gradient (RLS on an expansion). The projection's separability benefit is a
    HIGH-input-dim result — whether it earns its keep at our scale is exactly what the RLS-vs-RanPAC pair tests."""

    def __init__(self, C, proj_dim=2000, ridge_lambda=1e2, seed=0, scale=1.0):
        self.C = C; self.P = int(proj_dim); self.lam = float(ridge_lambda); self.seed = seed; self.scale = scale
        self.Wr = None; self.br = None; self.W = None

    def _phi(self, F):
        if self.Wr is None:
            rng = np.random.default_rng(self.seed + 90210)
            self.Wr = rng.standard_normal((self.P, F.shape[1])) * (self.scale / np.sqrt(F.shape[1]))
            self.br = rng.standard_normal(self.P) * 0.0
        return np.maximum(F @ self.Wr.T + self.br, 0.0)

    def fit(self, F, Y):
        Phi = self._phi(F)
        G = Phi.T @ Phi + self.lam * np.eye(self.P)
        M = Phi.T @ _onehot(Y, self.C)
        self.W = np.linalg.solve(G, M)                                  # [P,C]
        return self

    def logits(self, F):
        return self._phi(F) @ self.W

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        return self._phi(F) @ (self.W * scales[None, :])


class RLSHead:
    """The analytic ridge WITHOUT the projection (ACIL / F-OAL family): W=(G+λI)⁻¹M on the raw taps, G=Σffᵀ,
    M=Σf·onehot. Joint-equivalent by construction (recursive least squares = the batch solution) → no forgetting
    by construction. RanPAC = RLSHead on a random expansion → the pair isolates whether the projection earns its keep."""

    def __init__(self, C, ridge_lambda=1e2, seed=0):
        self.C = C; self.lam = float(ridge_lambda); self.W = None; self.b = None

    def fit(self, F, Y):
        d = F.shape[1]
        Fa = np.concatenate([F, np.ones((len(F), 1))], 1)              # bias column
        G = Fa.T @ Fa + self.lam * np.eye(d + 1)
        M = Fa.T @ _onehot(Y, self.C)
        Wb = np.linalg.solve(G, M)                                      # [d+1, C]
        self.W = Wb[:-1].T; self.b = Wb[-1]                             # [C,d], [C]
        return self

    def logits(self, F):
        return F @ self.W.T + self.b[None, :]

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        return F @ (self.W * scales[:, None]).T + self.b * scales


class GKEALHead:
    """GKEAL (kernel mechanism): a Gaussian-kernel random-Fourier-feature map z(f)=√(2/D)cos(fΩ+β), Ω~N(0,γ),
    then an analytic ridge solve. The closed-form NON-LINEAR multimodality fallback (P7.2), below FeCAM on the ladder."""

    def __init__(self, C, kernel_dim=2000, gamma=0.1, ridge_lambda=1e1, seed=0):
        self.C = C; self.D = int(kernel_dim); self.gamma = float(gamma); self.lam = float(ridge_lambda)
        self.seed = seed; self.Om = None; self.beta = None; self.W = None

    def _z(self, F):
        if self.Om is None:
            rng = np.random.default_rng(self.seed + 4242)
            self.Om = rng.standard_normal((F.shape[1], self.D)) * np.sqrt(2 * self.gamma)
            self.beta = rng.uniform(0, 2 * np.pi, self.D)
        return np.sqrt(2.0 / self.D) * np.cos(F @ self.Om + self.beta)

    def fit(self, F, Y):
        Z = self._z(F)
        G = Z.T @ Z + self.lam * np.eye(self.D)
        M = Z.T @ _onehot(Y, self.C)
        self.W = np.linalg.solve(G, M)
        return self

    def logits(self, F):
        return self._z(F) @ self.W

    def predict(self, F):
        return self.logits(F).argmax(1)

    def rescaled_logits(self, F, scales):
        return self._z(F) @ (self.W * scales[None, :])


class MLPHead:
    """A 2-layer GD head (the non-convex anchor) — wraps the TESTED fit_readout ([F,32,C] Adam). Also the head that
    reproduces the OLD continual harness bit-for-bit (harness_equiv_guard): its .fit ≡ fit_readout(...,epochs)."""

    def __init__(self, C, seed=0, epochs=60, lr=2e-3, batch=32):
        self.C = C; self.seed = seed; self.epochs = epochs; self.lr = lr; self.batch = batch; self.ro = None

    def fit(self, F, Y):
        self.ro = fit_readout(F, Y, self.C, self.seed, epochs=self.epochs, lr=self.lr, batch=self.batch)
        return self

    def logits(self, F):
        return self.ro.forward(F)

    def predict(self, F):
        return self.ro.predict(F)

    def rescaled_logits(self, F, scales):
        Z = self.ro.forward(F)                                          # scale only the final class logits (proxy)
        return Z * scales[None, :]


# ---- per-head hyperparameter fairness (the race_bp protocol: each head lightly selected on a val split) --------
KNOB_GRIDS = {
    "linear":         [dict()],                                        # the FLOOR — fixed, the reference (not tuned)
    "mlp":            [dict()],                                        # the anchor — fit_readout defaults
    "cosine-ncm":     [dict(tau=t) for t in (0.03, 0.05, 0.1, 0.2, 0.5)],
    "cosine-softmax": [dict(tau=t) for t in (0.05, 0.1, 0.2, 0.5)],
    "ncm":            [dict()],
    "slda":           [dict(shrinkage=s) for s in (1e-3, 1e-2, 1e-1, 3e-1)],
    "fecam":          [dict(shrinkage=s) for s in (0.1, 1.0)],
    "ranpac":         [dict(proj_dim=2000, ridge_lambda=l) for l in (1e0, 1e1, 1e2, 1e3)],   # fixed fair expansion
    "rls":            [dict(ridge_lambda=l) for l in (1e-1, 1e0, 1e1, 1e2, 1e3)],
    "gkeal":          [dict(gamma=g, ridge_lambda=l) for g in (0.05, 0.1, 0.5) for l in (1e0, 1e1)],
}


def select_head_knob(name, C, Ftr, Ytr, Fval, Yval, seed):
    """Lightly select a head's knob on a held-out val split (the race_bp fairness protocol — an un-tuned head loses
    for the wrong reason). Equal selection budget across heads (each grid is small). Returns (best_knob, best_val_acc)."""
    best, best_acc = dict(), -1.0
    for kb in KNOB_GRIDS.get(name, [dict()]):
        try:
            h = make_head(name, C, seed=seed, **kb).fit(Ftr, Ytr)
            acc = float((h.predict(Fval) == Yval).mean())
        except Exception:
            acc = -1.0
        if acc > best_acc:
            best_acc, best = acc, kb
    return dict(best), best_acc


# ---- the head registry (name -> factory(C, seed, **knob)) ----------------------------------------------------
def make_head(name, C, seed=0, **knob):
    """One place that maps a head NAME + its selected knob to a fresh head instance (the manifest records knob)."""
    n = name.lower()
    if n in ("linear", "linear-softmax", "floor"):
        return LinearSoftmaxHead(C, seed=seed, **knob)
    if n in ("cosine-ncm", "cosine", "cos-ncm"):
        return CosineHead(C, mode="ncm", seed=seed, **knob)
    if n in ("cosine-softmax", "cos-softmax"):
        return CosineHead(C, mode="softmax", seed=seed, **knob)
    if n == "ncm":
        return NCMHead(C, seed=seed, **knob)
    if n == "slda":
        return SLDAHead(C, seed=seed, **knob)
    if n == "fecam":
        return FeCAMHead(C, seed=seed, **knob)
    if n == "ranpac":
        return RanPACHead(C, seed=seed, **knob)
    if n in ("rls", "rls-ridge", "foal"):
        return RLSHead(C, seed=seed, **knob)
    if n == "gkeal":
        return GKEALHead(C, seed=seed, **knob)
    if n in ("mlp", "mlp-head"):
        return MLPHead(C, seed=seed, **knob)
    raise ValueError(f"unknown head '{name}'")


HEAD_FACTORIES = ["linear", "cosine-ncm", "cosine-softmax", "ncm", "slda", "fecam", "ranpac", "rls", "mlp"]


# ============================================================ the RanDumb control — random-projection bulk
class RandProjBulk:
    """The skeptic control (RanDumb, 2402.08823): a FROZEN random ReLU projection replacing the SCFF bulk as the
    feature source. source='taps' = of the SCFF tap output (the fair "did the bulk's representation beat a random
    one of the same input the readout sees"); source='pixels' = of the RAW input (true RanDumb — the harsher "did
    the 80% SCFF earn its keep at all"). A FAIR expansion dim (not a matched-64 strawman), same head on top."""

    def __init__(self, out_dim, source, in_dim, seed=0, scale=1.0):
        self.out_dim = int(out_dim); self.source = source
        rng = np.random.default_rng(seed + 13337)
        self.Wr = rng.standard_normal((self.out_dim, in_dim)) * (scale / np.sqrt(in_dim))

    def features(self, src):
        """src = the tap all-tap features (source='taps') OR the raw input X (source='pixels')."""
        return _l2n(np.maximum(src @ self.Wr.T, 0.0))


# ============================================================ the continual-safety harness (P7.4 — BUILT, not carried)
def continual_safety_heads(cell_factory, head_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                           *, scff_ep=8, sleep_ep=60, batch=32, sleep=True, probe=True, feat="alltap", trunc_k=3):
    """The A6 home-turf gate for an ARBITRARY head on the frozen bulk — EXTENDS p6lib.continual_safety (which
    hard-wires fit_readout) to accept a `head_factory(seed) -> head`. The SCFF bulk trains FORWARD-ONLY through the
    class-incremental stream (unsupervised); at each task the head CONSOLIDATES by its native sleep rule — a fresh
    head fit on the full replay buffer (closed-form: recompute stats; gradient: GD-refit). Returns AA/BWT/forget
    (GEM/CL conventions) + the all-class SCFF linear-probe trajectory. Pure numpy (phantom-safe).
    Guard: head_factory reproducing fit_readout ≡ the old hard-coded path bit-for-bit (harness_equiv_guard)."""
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]
    dims = [Xtr.shape[1]] + [64] * 12
    cell = cell_factory(dims, seed)
    a = [[0.0] * len(tasks) for _ in range(len(tasks))]
    bufX, bufY, scff_probe = [], [], []

    def tap(X):
        return readout_feats(cell.infer(X), None if feat == "alltap" else trunc_k)

    for t, cls in enumerate(tasks):
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(scff_ep):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), batch):
                xb = Xt[idx[s:s + batch]]
                if len(xb) >= 4:
                    cell.train_step(xb, rng)
        bufX.append(Xt); bufY.append(Yt)
        BX, BY = np.concatenate(bufX), np.concatenate(bufY)
        if sleep:
            head = head_factory(seed).fit(tap(BX), BY)                  # full-buffer replay = the A6 consolidation
        else:
            head = head_factory(seed).fit(tap(Xt), Yt)                  # no-sleep rot control: current task only
        for k in range(t + 1):
            mk = np.isin(Yte, tasks[k])
            a[t][k] = float((head.predict(tap(Xte[mk])) == Yte[mk]).mean())
        if probe:
            scff_probe.append(linear_probe(tap(Xpr), Ypr, tap(Xte), Yte, C, seed, epochs=120))
    aa, bwt, forget = acc_matrix_metrics(a)
    return dict(aa=aa, bwt=bwt, forget=forget, matrix=a, scff_probe=scff_probe or [0.0] * len(tasks))


def stream_cache(cell_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                 *, scff_ep=8, batch=32, feat="alltap", trunc_k=3):
    """Train the frozen-to-GD SCFF bulk FORWARD-ONLY through the class-incremental stream ONCE (head-independent —
    SCFF is unsupervised), caching the per-task replay-buffer tap features + the per-task test tap features at each
    task's cell state. Every head then replays its consolidation on this cache (eval_head_on_cache) — the same
    matrix continual_safety_heads produces per head, but the expensive bulk training is shared across the whole
    bake-off. Consistency-guarded against continual_safety_heads in P7.0 (must match bit-for-bit)."""
    rng = np.random.default_rng(seed)
    _ = rng.permutation(len(Xtr))[:800]                                # consume the same rng draw as the harness
    dims = [Xtr.shape[1]] + [64] * 12
    cell = cell_factory(dims, seed)

    def tap(X):
        return readout_feats(cell.infer(X), None if feat == "alltap" else trunc_k)

    bufX, bufY, cache = [], [], []
    for t, cls in enumerate(tasks):
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(scff_ep):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), batch):
                xb = Xt[idx[s:s + batch]]
                if len(xb) >= 4:
                    cell.train_step(xb, rng)
        bufX.append(Xt); bufY.append(Yt)
        BX, BY = np.concatenate(bufX), np.concatenate(bufY)
        te = {k: (tap(Xte[np.isin(Yte, tasks[k])]), Yte[np.isin(Yte, tasks[k])]) for k in range(t + 1)}
        cache.append(dict(FB=tap(BX), YB=BY, te=te))
    return cache


def eval_head_on_cache(cache, head_factory, seed):
    """Replay one head's sleep-consolidation on a stream_cache → the AA/BWT/forget dict + acc matrix (the fast
    per-head path for the P7.1 bake-off; identical to continual_safety_heads by construction)."""
    T = len(cache); a = [[0.0] * T for _ in range(T)]
    for t in range(T):
        head = head_factory(seed).fit(cache[t]["FB"], cache[t]["YB"])
        for k in range(t + 1):
            Fk, Yk = cache[t]["te"][k]
            a[t][k] = float((head.predict(Fk) == Yk).mean())
    aa, bwt, forget = acc_matrix_metrics(a)
    return dict(aa=aa, bwt=bwt, forget=forget, matrix=a)


def continual_head_metrics(cell_factory, head_name, C, seed, Xtr, Ytr, Xte, Yte, tasks,
                           *, knob=None, scff_ep=8, sleep_ep=60, feat="alltap", trunc_k=3):
    """Convenience: run one NAMED head through continual_safety_heads and return the AA/BWT/forget dict. `knob` =
    the per-head selected hyperparameters (the manifest records them)."""
    knob = knob or {}
    if head_name in ("mlp",):
        knob = dict(epochs=sleep_ep, **knob)                           # gradient head sleep-refits at sleep_ep

    def hf(s):
        return make_head(head_name, C, seed=s, **knob)
    return continual_safety_heads(cell_factory, hf, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                                  scff_ep=scff_ep, sleep_ep=sleep_ep, feat=feat, trunc_k=trunc_k)


# ============================================================ the SPINE — spine-cleanliness (two probes)
def spineflip_rescale(head, F, rng, *, n_draw=8, sigma=0.5):
    """Spine probe (a): multiply each class weight/prototype by a random positive log-normal scalar and measure the
    argmax-flip rate vs the unperturbed verdict. cosine ≈ 0 (angle-invariant to per-class norm); a magnitude head
    flips. The clean, non-gameable scale-invariance probe. Returns the mean flip fraction over n_draw draws."""
    base = head.logits(F).argmax(1); C = head.logits(F).shape[1]
    flips = []
    for _ in range(n_draw):
        scales = np.exp(rng.standard_normal(C) * sigma)                # positive per-class scalar ~ logN
        pert = head.rescaled_logits(F, scales).argmax(1)
        flips.append(float((pert != base).mean()))
    return float(np.mean(flips))


def spineflip_curve(head, F, rng, sigmas, *, n_draw=8):
    """The argmax-flip rate vs the per-class norm-perturbation grid (SPINE-CLEAN fig, x-axis)."""
    return np.array([spineflip_rescale(head, F, rng, n_draw=n_draw, sigma=s) for s in sigmas])


def recency_drop_bursty(matrix, tasks):
    """Spine probe (b): the OLD-class accuracy drop under the ACTUAL bursty class-incremental stream = the standard
    task-recency-bias read (Masana CIL survey). matrix[t][k] = acc on task k after task t. Returns
    mean_k<T ( a[k][k] − a[T-1][k] ) — how much the earliest-seen classes decayed by the end (a magnitude/recency
    symptom, NOT a synthetic norm-inflation, which is circular for a cosine head)."""
    T = len(matrix)
    if T < 2:
        return 0.0
    return float(np.mean([matrix[k][k] - matrix[T - 1][k] for k in range(T - 1)]))


def spine_cleanliness(head, F, rng, matrix=None, tasks=None, *, sigma=0.5, n_draw=8):
    """Both spine probes together: (a) argmax-flip under per-class norm rescale; (b) old-class drop under the bursty
    stream (needs a continual `matrix`). Read ONLY for accuracy-competitive heads (a dead head is trivially clean)."""
    a = spineflip_rescale(head, F, rng, n_draw=n_draw, sigma=sigma)
    b = recency_drop_bursty(matrix, tasks) if matrix is not None else np.nan
    return dict(flip=a, recency_drop=b)


# ============================================================ multimodality probe (P7.2 — natural space decides)
def multimodality_probe(F, Y, C, *, seed=0, kmax=4):
    """Per-class multimodality in the frozen tap space (the P7.2 decision-bearer on NATURAL data). For each class:
    (i) silhouette-free 'n-modes' = the k∈[1..kmax] minimizing a BIC-like penalized within-cluster spread from a
    tiny numpy k-means (NO sklearn — phantom-safe); (ii) the within/between spread ratio. Returns per-class n_modes
    [C] and the mean BIC-selected mode count. A flat probe (≈1) → one prototype suffices (the clean story holds)."""
    nmodes = np.zeros(C)
    for c in range(C):
        Fc = F[Y == c]
        if len(Fc) < 2 * kmax:
            nmodes[c] = 1.0; continue
        nmodes[c] = _bic_kmeans_k(Fc, kmax, seed + c)
    return nmodes


def _kmeans(F, k, seed, iters=25):
    """A tiny numpy k-means (Lloyd), NO sklearn. Returns (labels, centers, inertia)."""
    rng = np.random.default_rng(seed)
    C0 = F[rng.choice(len(F), k, replace=False)].copy()
    lab = np.zeros(len(F), int)
    for _ in range(iters):
        d = ((F[:, None, :] - C0[None, :, :]) ** 2).sum(2)             # [N,k]
        newlab = d.argmin(1)
        if (newlab == lab).all() and _ > 0:
            break
        lab = newlab
        for j in range(k):
            if (lab == j).any():
                C0[j] = F[lab == j].mean(0)
    inertia = float(((F - C0[lab]) ** 2).sum())
    return lab, C0, inertia


def _bic_kmeans_k(F, kmax, seed):
    """Pick k∈[1..kmax] minimizing a BIC-like score inertia + k·d·log(N) (a cheap penalized-fit mode count)."""
    N, d = F.shape
    best_k, best_s = 1, None
    for k in range(1, kmax + 1):
        _, _, inertia = _kmeans(F, k, seed) if k > 1 else (None, None, float(((F - F.mean(0)) ** 2).sum()))
        s = N * np.log(inertia / N + EPS) + k * d * np.log(N)          # BIC ~ N log(RSS/N) + params·log N
        if best_s is None or s < best_s - 1e-6:
            best_s, best_k = s, k
    return float(best_k)


# ============================================================ imbalance guards (P7.3)
def logit_adjust(logits, class_counts, *, tau=1.0):
    """Logit adjustment (trained head): subtract τ·log(prior_c) from the class logits (down-weight frequent classes)."""
    prior = class_counts / (class_counts.sum() + EPS)
    return logits - tau * np.log(prior + EPS)[None, :]


def balanced_softmax(logits, class_counts):
    """Balanced-softmax inference: add log(count_c) inside the softmax = logit_c + log n_c (the training-time
    balanced-softmax, applied at inference as the equivalent logit shift)."""
    return logits + np.log(class_counts + 1.0)[None, :]


def class_balanced_reservoir(X, Y, C, cap, rng):
    """Class-balanced reservoir sampling of a replay buffer: keep ~cap/C per class (the buffer-side imbalance guard)."""
    per = max(1, cap // C); keepX, keepY = [], []
    for c in range(C):
        idx = np.where(Y == c)[0]
        if len(idx) > per:
            idx = rng.choice(idx, per, replace=False)
        keepX.append(X[idx]); keepY.append(Y[idx])
    return np.concatenate(keepX), np.concatenate(keepY)


def air_rectify(head, class_counts):
    """AIR (Analytic Imbalance Rectifier, 2408.10349) — the no-gradient family's guard: re-weight a fitted analytic
    head's per-class weights by the inverse class frequency (the closed-form long-tail correction, applied post-fit
    to an RLS/RanPAC head). Trained-head guards (logit-adjust/bal-softmax) do not apply to a closed-form head."""
    w = (class_counts.sum() / (C_safe(class_counts) * (class_counts + 1.0)))   # inverse-frequency, normalized
    if getattr(head, "W", None) is not None and head.W.ndim == 2 and head.W.shape[1] == len(class_counts):
        head.W = head.W * w[None, :]                                    # RanPAC/RLS/GKEAL: [P,C] columns
    elif getattr(head, "W", None) is not None and head.W.shape[0] == len(class_counts):
        head.W = head.W * w[:, None]                                    # linear/SLDA: [C,d] rows
    if getattr(head, "b", None) is not None and np.ndim(head.b) == 1 and len(head.b) == len(class_counts):
        head.b = head.b * w
    return head


def C_safe(counts):
    return max(len(counts), 1)


# ============================================================ cost proxy (descriptive-only; real meter = Phase 8)
def readout_cost(head, F_dim, C):
    """The forward-MAC + Gram/solve-dim PROXY meter (result-format §B). DESCRIPTIVE-ONLY, never a decision
    tie-break, never a settled 80/20 — tagged '(proxy; real meter = P8)'. Returns dict(fwd_macs, solve_dim)."""
    name = type(head).__name__
    if isinstance(head, RanPACHead):
        return dict(fwd_macs=F_dim * head.P + head.P * C, solve_dim=head.P)
    if isinstance(head, GKEALHead):
        return dict(fwd_macs=F_dim * head.D + head.D * C, solve_dim=head.D)
    if isinstance(head, RLSHead):
        return dict(fwd_macs=F_dim * C, solve_dim=F_dim + 1)
    if isinstance(head, SLDAHead):
        return dict(fwd_macs=F_dim * C, solve_dim=F_dim)
    if isinstance(head, FeCAMHead):
        return dict(fwd_macs=C * F_dim * F_dim, solve_dim=F_dim)        # C per-class Mahalanobis quadratics
    if isinstance(head, (NCMHead,)):
        return dict(fwd_macs=F_dim * C, solve_dim=0)
    if isinstance(head, CosineHead):
        return dict(fwd_macs=F_dim * C, solve_dim=0)
    if isinstance(head, MLPHead):
        return dict(fwd_macs=F_dim * 32 + 32 * C, solve_dim=0)
    return dict(fwd_macs=F_dim * C, solve_dim=0)                        # linear-softmax floor


# ============================================================ AAA static metric
def aaa_curve(head_factory, Ftr, Ytr, Fte, Yte, *, n_points=4):
    """Area under acc vs log10(#samples) ÷ log-span (the AAA static metric). Fits a fresh head on log-spaced
    training subsets. Returns (aaa, sizes, accs)."""
    N = len(Ftr)
    sizes = np.unique(np.round(np.logspace(np.log10(max(20, N // 50)), np.log10(N), n_points)).astype(int))
    rng = np.random.default_rng(0); accs = []
    for n in sizes:
        idx = rng.permutation(N)[:n]
        h = head_factory().fit(Ftr[idx], Ytr[idx])
        accs.append(float((h.predict(Fte) == Yte).mean()))
    x = np.log10(sizes.astype(float)); accs = np.array(accs)
    aaa = float(np.trapezoid(accs, x) / (x[-1] - x[0] + EPS)) if len(x) > 1 else float(accs[-1])
    return aaa, sizes, accs


# ============================================================ guards (the sign/direction-bug antidote — run FIRST)
def head_equiv_guard(*, C=4, d=48, n=600, seed=0, verbose=True):
    """Head-port equivalences (each MUST hold or a head is silently mis-wired):
      (1) CosineHead(ncm) ≡ nearest-NORMALIZED-prototype on L2-normalized feats (angle = nearest unit proto);
      (2) cosine-softmax(τ→∞) argmax ≡ linear on normalized feats at init cannot be exact, so instead:
          cosine-softmax @init ≡ cosine-NCM (both start at the class-mean protos);
      (3) LinearSoftmaxHead(epochs=120) ≡ linear_probe accuracy bit-for-bit (the P5/floor head).
    Returns (ok, detail)."""
    rng = np.random.default_rng(seed)
    F = rng.standard_normal((n, d)); Y = rng.integers(0, C, n)
    Fte = rng.standard_normal((n // 2, d)); Yte = rng.integers(0, C, n // 2)
    ok = True; detail = {}
    # (1) cosine-ncm ≡ nearest normalized prototype
    Fn = _l2n(F)
    ch = CosineHead(C, mode="ncm").fit(Fn, Y)
    proto = np.stack([_l2n(Fn[Y == c].mean(0)[None, :])[0] for c in range(C)])
    ref = (_l2n(Fte) @ proto.T).argmax(1)
    d1 = int((ch.predict(Fte) != ref).sum()); ok &= (d1 == 0); detail["cos_ncm≡nearest-unit-proto_mismatch"] = d1
    # (2) cosine-softmax @init ≡ cosine-ncm (0 epochs → same protos)
    cs0 = CosineHead(C, mode="softmax", epochs=0).fit(Fn, Y)
    d2 = int((cs0.predict(Fte) != ch.predict(Fte)).sum()); ok &= (d2 == 0); detail["cos_softmax@init≡cos_ncm_mismatch"] = d2
    # (3) LinearSoftmaxHead ≡ linear_probe
    lh = LinearSoftmaxHead(C, seed=seed, epochs=120, lr=3e-3, batch=64).fit(F, Y)
    a_head = float((lh.predict(Fte) == Yte).mean())
    a_lp = linear_probe(F, Y, Fte, Yte, C, seed, epochs=120, lr=3e-3, batch=64)
    d3 = abs(a_head - a_lp); ok &= (d3 < 1e-9); detail["linear_head≡linear_probe_absdiff"] = d3
    if verbose:
        print(f"  [head-equiv guard] cos-ncm≡nearest-unit-proto miss={d1}  cos-softmax@init≡cos-ncm miss={d2}  "
              f"linear≡linear_probe |Δ|={d3:.2e}  {'OK' if ok else '!! HEAD-PORT BUG'}", flush=True)
    return ok, detail


def fd_head_grad(*, C=4, d=24, n=64, eps=1e-6, seed=0, verbose=True):
    """Finite-difference vs analytic gradient of the ONE new trained head — cosine-softmax (linear-softmax + MLP
    ride the already-FD-tested MLP class). max|analytic-FD| MUST be < 1e-5 (the sign/direction-bug antidote)."""
    rng = np.random.default_rng(seed)
    F = rng.standard_normal((n, d)); Y = rng.integers(0, C, n)
    h = CosineHead(C, mode="softmax", tau=0.2)
    Fn = h._unit(F)
    h.W = rng.standard_normal((C, d))                                   # arbitrary weights (not at a special point)

    def loss():
        Z = (Fn @ (h.W / (np.linalg.norm(h.W, axis=1, keepdims=True) + EPS)).T) / h.tau
        P = softmax(Z, axis=1)
        return float(-np.log(P[np.arange(n), Y] + EPS).mean())
    g_an = h._grad(Fn, Y, n)
    worst = 0.0
    for _ in range(60):
        i = int(rng.integers(C)); j = int(rng.integers(d))
        o = h.W[i, j]; h.W[i, j] = o + eps; Lp = loss(); h.W[i, j] = o - eps; Lm = loss(); h.W[i, j] = o
        worst = max(worst, abs((Lp - Lm) / (2 * eps) - g_an[i, j]))
    ok = worst < 1e-5
    if verbose:
        print(f"  [FD-head guard] cosine-softmax max|analytic-FD| = {worst:.2e}  "
              f"{'OK' if ok else '!! HEAD GRADIENT BUG'}", flush=True)
    return ok, worst


def harness_equiv_guard(*, seed=42, verbose=True):
    """continual_safety_heads with the MLP head (≡ the old hard-coded fit_readout path) MUST reproduce
    p6lib.continual_safety bit-for-bit (else the P7.4 gate baseline silently moved). Small synthetic stream."""
    from p6lib import continual_safety as _old
    Xtr, Ytr, Xte, Yte = synth_stream(1200, 600, 0.6, seed, dim=24, n_class=10, n_clusters=20)
    tasks = CISTREAM_TASKS; C = 10

    def cell_factory(dims, s):
        return make_committed_cell(dims, s)

    def mlp_hf(s):
        return MLPHead(C, seed=s, epochs=60)
    old = _old(cell_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed, scff_ep=2, sleep_ep=60, probe=False)
    new = continual_safety_heads(cell_factory, mlp_hf, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                                 scff_ep=2, sleep_ep=60, probe=False)
    dmat = max(abs(old["matrix"][i][k] - new["matrix"][i][k]) for i in range(len(tasks)) for k in range(len(tasks)))
    ok = dmat < 1e-12
    if verbose:
        print(f"  [harness-equiv guard] max|old_continual - continual_heads(MLP)| = {dmat:.2e}  "
              f"AA old={old['aa']:.4f} new={new['aa']:.4f}  {'OK' if ok else '!! HARNESS BUG'}", flush=True)
    return ok, dmat
