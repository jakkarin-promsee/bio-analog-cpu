"""
p2lib — the Phase-2 substrate: SCFF with PLUGGABLE normalization and PLUGGABLE goodness.

Phase 1 hardwired two choices into the rule (the very two Phase 2 is here to test):
  - normalization between layers = length-norm  h/||h||   (FF's "layer-norm" — the WALL)
  - goodness                     = sum of squares  Σh²     (the suspected depth-killer)

Phase 2 makes both a switch, so the P2.1 grid { squared, linear } goodness x { norm } is one
config change, not a fork. The maths is the closed-form LOCAL SCFF gradient (no autograd),
identical to scff_gate.py where the modes coincide — verified by reproducing the wall.

The two axes, and why they are coupled (the DeeperForward finding, ref/deeperforward.md):
  GOODNESS
    squared : G = Σh²·gs   -> dG/dz = 2·gs·h        (the h-factor => quiet units freeze => dead-unit
                                                      cascade with depth; the Trifecta/Phase-1 wall)
    linear  : G = Σh·gs    -> dG/dz = gs·1[z>0]      (no h-factor => quiet-but-active units keep
                                                      learning; DeeperForward's fix)
  NORM (applied to the rep passed forward)
    lengthnorm : h/||h||                 (per-sample; FF/SCFF/Phase-1 baseline; does NOT remove the mean)
    layernorm  : (h-μ)/√(σ²+ε) per sample (per-sample, MEAN-ZERO => linear goodness decouples for free,
                                           NO batch stats — the substrate-native DeeperForward cell)
    none       : h                       (cheat/fail control)
  (batch-norm / online-streaming-BN / group-norm: built deliberately in P2.1, where the running-stats
   register and train/eval split need care — stubbed here so P2.0 stays clean and correct.)

numpy only. Reuses relu/EPS from the tested Phase-1 core.
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression

_EXP0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1", "exp0")
sys.path.insert(0, _EXP0)
from scff_gate import relu, EPS  # noqa: E402  (the exact tested primitives)

GOODNESS_MODES = ("squared", "linear")
NORM_MODES = ("lengthnorm", "layernorm", "none")  # batchnorm/online_bn/groupnorm: P2.1
PROBE_C = 1.0


# ----------------------------------------------------------------------------- normalization (pluggable)
def normalize(a, mode):
    """Normalize the representation passed to the next layer. Per-sample modes only here
    (P2.0/the wall + the DeeperForward cell are all per-sample; batch modes land in P2.1)."""
    if mode == "lengthnorm":
        return a / (np.linalg.norm(a, axis=1, keepdims=True) + EPS)
    if mode == "layernorm":
        mu = a.mean(axis=1, keepdims=True)
        var = a.var(axis=1, keepdims=True)
        return (a - mu) / np.sqrt(var + EPS)
    if mode == "none":
        return a
    raise ValueError(f"norm mode {mode!r} not available in p2lib (P2.1 adds batch/online/group)")


# ----------------------------------------------------------------------------- goodness (pluggable)
def goodness_of(h, mode, gs):
    """Return (G [B], factor [B,M]) where the weight grad uses `factor` (= dG/dz, ReLU folded).
    squared: factor = 2·gs·h  (magnitude-weighted -> deactivation).
    linear : factor = gs·1[h>0] (mask -> quiet units keep full gradient)."""
    if mode == "squared":
        G = (h ** 2).sum(1) * gs
        return G, 2.0 * gs * h
    if mode == "linear":
        G = h.sum(1) * gs
        return G, gs * (h > 0).astype(h.dtype)
    raise ValueError(f"goodness mode {mode!r} unknown")


# ----------------------------------------------------------------------------- SCFF (pluggable)
class SCFF2:
    """Mono-forward dual-rail SCFF, pluggable norm + goodness. Local per-layer update, one layer
    of credit each. x_pos = 2·x_k ; x_neg = x_k + x_n ; shared weight. Input normalized at L1 too."""

    def __init__(self, dims, *, theta=2.0, lr=0.03, seed=0, objective="two_sided",
                 goodness="squared", norm="lengthnorm", goodness_scale="sum",
                 normalize_input=True, init_gain=1.0):
        rng = np.random.default_rng(seed)
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.theta, self.lr = theta, lr
        self.objective = objective            # "two_sided" | "contrast" (SymBa-style gap)
        self.goodness = goodness              # "squared" | "linear"
        self.norm = norm                      # "lengthnorm" | "layernorm" | "none"
        self.goodness_scale = goodness_scale  # "sum" (gs=1, width-indep) | "mean" (gs=1/M)
        self.normalize_input = normalize_input
        self.L = len(self.W)

    def _gs(self, M):
        return 1.0 if self.goodness_scale == "sum" else 1.0 / M

    def _in(self, X):
        return normalize(X, self.norm) if self.normalize_input else X

    # ---- inference: real sample, returns the normalized rep per layer (the probe features) ----
    def infer(self, X):
        a, reps = self._in(X), []
        for W, b in zip(self.W, self.b):
            a = normalize(relu(a @ W.T + b), self.norm)
            reps.append(a)
        return reps

    def dead_fraction(self, X):
        """Per-layer fraction of units never active across the eval set (the deactivation read)."""
        a, fr = self._in(X), []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            fr.append(float((h.max(0) <= EPS).mean()))
            a = normalize(h, self.norm)
        return np.array(fr)

    def goodness_gap(self, X, seed=0):
        """Per-layer mean (G_pos - G_neg) on the model's real dual-rail path (INV/F4)."""
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(X))
        ap, an = self._in(2.0 * X), self._in(X + X[perm])
        gap = []
        for W, b in zip(self.W, self.b):
            hp, hn = relu(ap @ W.T + b), relu(an @ W.T + b)
            M = hp.shape[1]; gs = self._gs(M)
            Gp, _ = goodness_of(hp, self.goodness, gs)
            Gn, _ = goodness_of(hn, self.goodness, gs)
            gap.append(float((Gp - Gn).mean()))
            ap, an = normalize(hp, self.norm), normalize(hn, self.norm)
        return np.array(gap)

    def train_step(self, Xb, rng):
        """One online step: single forward (both worlds), local update at every layer."""
        perm = rng.permutation(len(Xb))
        ap, an = self._in(2.0 * Xb), self._in(Xb + Xb[perm])
        B = len(Xb)
        for l in range(self.L):
            W, b = self.W[l], self.b[l]
            hp, hn = relu(ap @ W.T + b), relu(an @ W.T + b)
            M = hp.shape[1]; gs = self._gs(M)
            Gp, fp = goodness_of(hp, self.goodness, gs)   # fp,fn = dG/dz per unit  [B,M]
            Gn, fn = goodness_of(hn, self.goodness, gs)
            if self.objective == "two_sided":
                dGp = expit(Gp - self.theta) - 1.0        # <0 -> raise G_pos
                dGn = expit(Gn - self.theta)              # >0 -> lower G_neg
            else:  # "contrast": push the gap (G_pos - G_neg), no threshold (SymBa-like)
                s = expit(Gn - Gp); dGp, dGn = -s, s
            cp, cn = dGp[:, None] * fp, dGn[:, None] * fn   # [B,M]  chain to z
            self.W[l] -= self.lr * (cp.T @ ap + cn.T @ an) / B
            self.b[l] -= self.lr * (cp.sum(0) + cn.sum(0)) / B
            ap, an = normalize(hp, self.norm), normalize(hn, self.norm)


# ----------------------------------------------------------------------------- per-layer linear probe
def probe_per_layer(model, Xtr, Ytr, Xte, Yte, C=PROBE_C):
    """The PINNED primary metric: logistic, fixed L2, frozen split, to convergence, per layer."""
    rtr, rte = model.infer(Xtr), model.infer(Xte)
    return [float(LogisticRegression(C=C, max_iter=3000).fit(a_tr, Ytr).score(a_te, Yte))
            for a_tr, a_te in zip(rtr, rte)]


def probe_one(Ftr, Ytr, Fte, Yte, C=PROBE_C):
    """Single linear probe on a given feature matrix (for GD-hidden layers / arbitrary reps)."""
    return float(LogisticRegression(C=C, max_iter=3000).fit(Ftr, Ytr).score(Fte, Yte))


def effective_rank(A):
    """erank = exp(H(σ̄)), H = entropy of normalized singular values — the 'collapse' read (result-format
    Layer B). Low erank with depth = homogenization. Computed on a centered activation matrix."""
    A = A - A.mean(0, keepdims=True)
    s = np.linalg.svd(A, compute_uv=False)
    s = s[s > EPS]
    if len(s) == 0:
        return 0.0
    p = s / s.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


# ----------------------------------------------------------------------------- Tier-B high-D task (the dial)
def make_tierb(n, rng, dim=20, grid=4, n_active=3, spacing=1.4, overlap=0.35, rotate=True,
               label="random", n_class=2):
    """High-D compositional clusters with a difficulty dial (README §2 / Phase-1 §1.5 Tier-B).

    grid^n_active Gaussian clusters live in the first `n_active` axes, embedded in `dim`-D (zeros on the
    extra axes) and optionally rotated by a fixed random orthogonal Q so structure is not axis-aligned
    -> a random projection can't trivially read it (the Phase-1 'SCFF must beat random' bar needs dim high).

    label:
      "random" (DEFAULT) — each cluster gets a FIXED random class in {0..n_class-1}. Compositional (not a
        simple input-space boundary) but **linearly readable once clusters separate** — the corrected dial
        label (P2.0 smoke: raw parity is the XOR pathology, no linear-probe headroom).
      "parity" — label = parity of summed cluster indices (kept for the record; NO linear-probe headroom).
    Dials: grid/n_active (cluster count), overlap (difficulty), dim (where random fails), n_class."""
    import itertools
    idx = list(itertools.product(range(grid), repeat=n_active))
    off = (grid - 1) / 2.0
    K = len(idx)
    if label == "random":
        clab = np.random.default_rng(12345).integers(0, n_class, size=K)  # FIXED cluster->class map
    base = n // K; counts = [base] * K
    for i in range(n - base * K):
        counts[i] += 1
    Xs, Ys = [], []
    for ci, (ix, k) in enumerate(zip(idx, counts)):
        c = np.zeros(dim)
        c[:n_active] = (np.array(ix) - off) * spacing
        Xs.append(rng.normal(c, overlap, (k, dim)))
        lab = int(clab[ci]) if label == "random" else (sum(ix) % 2)
        Ys.append(np.full(k, lab))
    X = np.concatenate(Xs).astype(np.float64); Y = np.concatenate(Ys).astype(np.int64)
    if rotate:
        Q, _ = np.linalg.qr(np.random.default_rng(0).normal(size=(dim, dim)))
        X = X @ Q
    p = rng.permutation(len(X))
    return X[p], Y[p]
