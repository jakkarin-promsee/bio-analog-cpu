"""
p2lib — the Phase-2 substrate: SCFF with PLUGGABLE normalization and PLUGGABLE goodness.

Phase 1 hardwired two choices into the rule (the very two Phase 2 is here to test):
  - normalization between layers = length-norm  h/||h||   (FF's "layer-norm" — the WALL)
  - goodness                     = sum of squares  Σh²     (the suspected depth-killer)

Phase 2 makes both a switch, so the P2.1 grid { squared, linear } goodness x { norm } is one
config change, not a fork. The maths is the closed-form LOCAL SCFF gradient (no autograd),
identical to scff_gate.py where the modes coincide — verified by reproducing the wall.

The two axes, and why they are coupled (the DeeperForward finding, research/papers/phase1-2/deeperforward.md):
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
NORM_MODES = ("lengthnorm", "layernorm", "groupnorm", "batchnorm", "online_bn", "none")
STATELESS_NORMS = ("lengthnorm", "layernorm", "groupnorm", "none")  # per-sample; carry no running state
PROBE_C = 1.0


# ----------------------------------------------------------------------------- normalization (pluggable)
def normalize(a, mode, groups=8):
    """Per-sample normalization of the rep passed forward (the STATELESS modes — no batch stats).
    The batch modes (batchnorm / online_bn) carry per-feature running registers and so live as
    SCFF2 methods (_norm_pair / _norm_one), not here. P2.1 (norm x goodness grid)."""
    if mode == "lengthnorm":                          # FF/SCFF/Phase-1 baseline (the WALL); keeps the mean
        return a / (np.linalg.norm(a, axis=1, keepdims=True) + EPS)
    if mode == "layernorm":                           # per-sample, MEAN-ZERO -> linear goodness decouples free
        mu = a.mean(axis=1, keepdims=True)
        var = a.var(axis=1, keepdims=True)
        return (a - mu) / np.sqrt(var + EPS)
    if mode == "groupnorm":                            # per-sample, split features into `groups` groups
        parts = np.array_split(a, min(groups, a.shape[1]), axis=1)   # array_split -> uneven OK (synth dim=20)
        out = [(p - p.mean(1, keepdims=True)) / np.sqrt(p.var(1, keepdims=True) + EPS) for p in parts]
        return np.concatenate(out, axis=1)
    if mode == "none":                                 # cheat / fail control
        return a
    raise ValueError(f"norm mode {mode!r} is not a STATELESS mode (batch modes are SCFF2 methods)")


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
                 normalize_input=True, init_gain=1.0, groups=8, bn_rho=0.05):
        rng = np.random.default_rng(seed)
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.theta, self.lr = theta, lr
        self.objective = objective            # "two_sided" | "contrast" (SymBa-style gap)
        self.goodness = goodness              # "squared" | "linear"
        self.norm = norm                      # see NORM_MODES (stateless or batch)
        self.goodness_scale = goodness_scale  # "sum" (gs=1, width-indep) | "mean" (gs=1/M)
        self.normalize_input = normalize_input
        self.groups = groups                  # group-norm group count
        self.bn_rho = bn_rho                  # batch/online-BN running-register EMA rate
        self.L = len(self.W)
        # per-site running per-feature stats (batch modes only); site 0 = input, 1..L = inter-layer
        self.run_mu = [None] * (self.L + 1)
        self.run_var = [None] * (self.L + 1)

    def _gs(self, M):
        return 1.0 if self.goodness_scale == "sum" else 1.0 / M

    def _ema(self, site, mu, var):
        r = self.bn_rho
        self.run_mu[site] = (1 - r) * self.run_mu[site] + r * mu
        self.run_var[site] = (1 - r) * self.run_var[site] + r * var

    def _norm_pair(self, hp, hn, site, training):
        """Normalize pos & neg reps for the NEXT layer. Batch modes: stats from hp (real rail), ONE
        EMA update per site/step, applied to both rails. batchnorm@train uses the batch stat (GPU
        leak); online_bn@train uses the running stat (substrate lag). Stateless: each rail alone."""
        if self.norm in STATELESS_NORMS:
            return normalize(hp, self.norm, self.groups), normalize(hn, self.norm, self.groups)
        bmu, bvar = hp.mean(0), hp.var(0)
        if self.run_mu[site] is None:                          # cold start: seed the register
            self.run_mu[site], self.run_var[site] = bmu.copy(), bvar.copy()
        if training:
            self._ema(site, bmu, bvar)
        if self.norm == "batchnorm" and training:
            umu, uvar = bmu, bvar                              # GPU: normalize by THIS batch
        else:
            umu, uvar = self.run_mu[site], self.run_var[site]  # online (train+eval) & batchnorm (eval)
        den = np.sqrt(uvar + EPS)
        return (hp - umu) / den, (hn - umu) / den

    def _norm_one(self, a, site, training):
        """Single-rail normalize (infer / eval diagnostics). Batch modes use frozen running stats
        (batch fallback if this site was never trained)."""
        if self.norm in STATELESS_NORMS:
            return normalize(a, self.norm, self.groups)
        if self.run_mu[site] is None:
            mu, var = a.mean(0), a.var(0)
        else:
            mu, var = self.run_mu[site], self.run_var[site]
        return (a - mu) / np.sqrt(var + EPS)

    # ---- inference: real sample, returns the normalized rep per layer (the probe features) ----
    def infer(self, X):
        a = self._norm_one(X, 0, False) if self.normalize_input else X
        reps = []
        for l, (W, b) in enumerate(zip(self.W, self.b)):
            a = self._norm_one(relu(a @ W.T + b), l + 1, False)
            reps.append(a)
        return reps

    def dead_fraction(self, X):
        """Per-layer fraction of units never active across the eval set (the deactivation read)."""
        a = self._norm_one(X, 0, False) if self.normalize_input else X
        fr = []
        for l, (W, b) in enumerate(zip(self.W, self.b)):
            h = relu(a @ W.T + b)
            fr.append(float((h.max(0) <= EPS).mean()))
            a = self._norm_one(h, l + 1, False)
        return np.array(fr)

    def goodness_gap(self, X, seed=0):
        """Per-layer mean (G_pos - G_neg) on the model's real dual-rail path (INV/F4). Eval: both
        rails use frozen stats."""
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(X))
        ap = self._norm_one(2.0 * X, 0, False) if self.normalize_input else 2.0 * X
        an = self._norm_one(X + X[perm], 0, False) if self.normalize_input else X + X[perm]
        gap = []
        for l, (W, b) in enumerate(zip(self.W, self.b)):
            hp, hn = relu(ap @ W.T + b), relu(an @ W.T + b)
            M = hp.shape[1]; gs = self._gs(M)
            Gp, _ = goodness_of(hp, self.goodness, gs)
            Gn, _ = goodness_of(hn, self.goodness, gs)
            gap.append(float((Gp - Gn).mean()))
            ap, an = self._norm_one(hp, l + 1, False), self._norm_one(hn, l + 1, False)
        return np.array(gap)

    def train_step(self, Xb, rng, neg_partner=None):
        """One online step: single forward (both worlds), local update at every layer. The gradient
        is the closed-form local SCFF rule (unchanged from P2.0); only the norm calls thread state.

        x_pos = 2*x_k (coherent) ; x_neg = x_k + partner (a mixture). `neg_partner` selects the partner:
        None -> a random in-batch sample (the P2.1 / SCFF baseline, exact); else a caller-supplied
        partner [B,D] (P2.2 hard negatives: a different-class / different-cluster sample, so the mixture
        is a *between-class* blend -> goodness separates classes, not density)."""
        partner = Xb[rng.permutation(len(Xb))] if neg_partner is None else neg_partner
        Xp, Xn = 2.0 * Xb, Xb + partner
        if self.normalize_input:
            ap, an = self._norm_pair(Xp, Xn, 0, True)
        else:
            ap, an = Xp, Xn
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
            ap, an = self._norm_pair(hp, hn, l + 1, True)


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
