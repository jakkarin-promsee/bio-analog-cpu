"""
p3lib — the Phase-3 substrate: SCFF with a PLUGGABLE OBJECTIVE (energy vs information-preserving).

Phase 2 closed the *energy-goodness* family (G=Sum h^2 / Sum h): a deep stack can't earn depth, transmission
(P2.1) and objective-within-energy (P2.2, oracle-proof) both fail. The wall is intrinsic to the ENERGY
objective, NOT to forward-only locality (research/papers/phase3/the-objective-reframe.md): Greedy InfoMax / CLAPP / greedy
layer-wise denoising-AE pretraining are forward-only, gradient-isolated, unsupervised, AND depth-composing,
because their objective is information-PRESERVING / predictive.

This module adds the decided Phase-3 primary objective:

  MASKED-FEATURE RECONSTRUCTION (per-layer denoising autoencoder).  Each layer l:
    input a (clean, normalized rep from l-1; input-norm at l=1)
    corrupt:  a~ = a * keep_mask        (zero a fraction `mask_ratio` of dims)
    encode :  z = a~ @ W.T + b ; h = relu(z)
    decode :  a^ = h @ D.T + c          (D = a SMALL per-layer aux decoder [din x width])
    loss   :  L = mean( (a^ - a)^2 )     (reconstruct the CLEAN input from the corrupted view)
    update :  {W,b,D,c} by the WITHIN-LAYER AE gradient (local backprop through decode->encode),
              GRADIENT-ISOLATED between layers (no cross-layer signal) -- GIM/denoising-AE structure.
  The clean (unmasked) normalized rep h_clean = norm(relu(a @ W.T + b)) propagates forward (train with
  corruption, encode clean -- the standard denoising-AE protocol). Single-rail, single-sample: NO negatives,
  NO batch stats, NO augmentation pairs -- the most substrate-native objective (README sec 0).

  Why it should stop the wall: the energy layer SHEDS whatever isn't loud (density != class -> probe falls);
  a denoising layer is PENALIZED for shedding (can't reconstruct what it threw away) -> info preserved ->
  the per-layer probe stops declining.

The energy-wall baseline is p2lib.SCFF2 (layer-norm + linear + contrast = the P2.1 healthy cell) -- imported
by the harness, not re-implemented here. numpy only; reuses the tested p2lib primitives.
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase2"))           # p2lib
from p2lib import normalize, relu, EPS                            # noqa: E402  (tested primitives)


class SCFFRecon:
    """Mono-rail SCFF with a per-layer masked-reconstruction (denoising-AE) objective. Same forward / infer
    interface as p2lib.SCFF2 (so probe_per_layer / effective_rank / dead_fraction reuse unchanged), plus
    recon_error() for the INFOPRESERVE curve. Local, forward-only between layers, single-sample, unsupervised."""

    def __init__(self, dims, *, lr=0.03, seed=0, mask_ratio=0.5, norm="layernorm",
                 normalize_input=True, init_gain=1.0, dec_lr_scale=1.0, groups=8):
        rng = np.random.default_rng(seed)
        # encoder
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        # per-layer auxiliary decoder D_l: [din x width] reconstructs the layer's input from its rep
        self.D = [rng.normal(0, np.sqrt(1.0 / dims[i + 1]), (dims[i], dims[i + 1]))
                  for i in range(len(dims) - 1)]
        self.c = [np.zeros(dims[i]) for i in range(len(dims) - 1)]
        self.lr = lr
        self.dec_lr = lr * dec_lr_scale
        self.mask_ratio = mask_ratio
        self.norm = norm
        self.normalize_input = normalize_input
        self.groups = groups
        self.L = len(self.W)

    # ---- forward helpers ----
    def _norm(self, a):
        return normalize(a, self.norm, self.groups)

    def infer(self, X):
        """Clean forward: real sample, returns the normalized rep per layer (the probe features) -- identical
        protocol to SCFF2.infer (layer-norm between layers, input-norm at L1)."""
        a = self._norm(X) if self.normalize_input else X
        reps = []
        for W, b in zip(self.W, self.b):
            a = self._norm(relu(a @ W.T + b))
            reps.append(a)
        return reps

    def dead_fraction(self, X):
        a = self._norm(X) if self.normalize_input else X
        fr = []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            fr.append(float((h.max(0) <= EPS).mean()))
            a = self._norm(h)
        return np.array(fr)

    def recon_error(self, X):
        """INFOPRESERVE metric: per-layer CLEAN reconstruction error mean||D_l h_l - a_l||^2 (no masking at
        eval), normalized per-dim. Low + flat-with-depth = information is preserved (the win's mechanism)."""
        a = self._norm(X) if self.normalize_input else X
        errs = []
        for W, b, D, c in zip(self.W, self.b, self.D, self.c):
            h = relu(a @ W.T + b)
            ahat = h @ D.T + c
            errs.append(float(((ahat - a) ** 2).mean()))
            a = self._norm(h)
        return np.array(errs)

    # ---- the local objective ----
    def train_step(self, Xb, rng, neg_partner=None):
        """One online step: greedy per-layer denoising-AE update, gradient-isolated between layers. `neg_partner`
        accepted for harness signature compatibility but UNUSED (masked-recon is single-rail, no negatives)."""
        a = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb)
        for l in range(self.L):
            W, b, D, c = self.W[l], self.b[l], self.D[l], self.c[l]
            din = a.shape[1]
            keep = (rng.random((B, din)) >= self.mask_ratio).astype(a.dtype)   # zero mask_ratio of dims
            at = a * keep                                                      # corrupted view
            z = at @ W.T + b
            h = relu(z)                                                        # [B, dout]
            ahat = h @ D.T + c                                                 # [B, din] reconstruction
            e = ahat - a                                                       # residual vs the CLEAN input
            dahat = (2.0 / (B * din)) * e                                      # dL/d ahat
            # decoder grads (ahat = h @ D.T + c)
            gD = dahat.T @ h                                                   # [din, dout]
            gc = dahat.sum(0)                                                  # [din]
            # encoder grads (through decode -> relu -> linear on the CORRUPTED input)
            dh = dahat @ D                                                     # [B, dout]
            dz = dh * (z > 0)
            gW = dz.T @ at                                                     # [dout, din]
            gb = dz.sum(0)
            self.D[l] = D - self.dec_lr * gD
            self.c[l] = c - self.dec_lr * gc
            self.W[l] = W - self.lr * gW
            self.b[l] = b - self.lr * gb
            # propagate the CLEAN encoding forward (denoising-AE protocol)
            a = self._norm(relu(a @ self.W[l].T + self.b[l]))


class SCFFContrast:
    """Per-layer CONTRASTIVE (InfoNCE / CLAPP) objective -- DISCRIMINATIVE information preservation. Same
    infer interface as SCFFRecon (layer-norm propagation). Positive pair = two random maskings of the SAME
    sample; negatives = the other samples in the batch. Per-layer InfoNCE on L2-normalized embeddings,
    gradient-isolated between layers. This is the member of the GIM/CLAPP family that preserves only the
    CLASS-distinguishing mutual information (not all of it, as the autoencoder did) -- the P3.0 route.

    Cost vs masked-recon: needs in-batch negatives (a batch, not single-sample) -> the LUT negative sampler
    on-chip (P3.0 slot 7). Knobs: mask_ratio (the two views), temp (InfoNCE temperature)."""

    def __init__(self, dims, *, lr=0.03, seed=0, mask_ratio=0.5, temp=0.5, norm="layernorm",
                 normalize_input=True, init_gain=1.0, groups=8):
        rng = np.random.default_rng(seed)
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.lr = lr
        self.mask_ratio = mask_ratio
        self.temp = temp
        self.norm = norm
        self.normalize_input = normalize_input
        self.groups = groups
        self.L = len(self.W)

    def _norm(self, a):
        return normalize(a, self.norm, self.groups)

    def infer(self, X):
        a = self._norm(X) if self.normalize_input else X
        reps = []
        for W, b in zip(self.W, self.b):
            a = self._norm(relu(a @ W.T + b))
            reps.append(a)
        return reps

    def dead_fraction(self, X):
        a = self._norm(X) if self.normalize_input else X
        fr = []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            fr.append(float((h.max(0) <= EPS).mean()))
            a = self._norm(h)
        return np.array(fr)

    def train_step(self, Xb, rng, neg_partner=None):
        """Per-layer InfoNCE: two masked views, L2-normalized embeddings, contrast positives (same sample,
        diagonal) against in-batch negatives. Local + gradient-isolated; clean rep propagates forward."""
        a = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb)
        I = np.eye(B)
        for l in range(self.L):
            W, b = self.W[l], self.b[l]
            din = a.shape[1]
            a1 = a * (rng.random((B, din)) >= self.mask_ratio)        # two independent masked views
            a2 = a * (rng.random((B, din)) >= self.mask_ratio)
            z1 = a1 @ W.T + b; h1 = relu(z1)
            z2 = a2 @ W.T + b; h2 = relu(z2)
            n1 = np.linalg.norm(h1, axis=1, keepdims=True) + EPS; u1 = h1 / n1   # L2-normalized embeddings
            n2 = np.linalg.norm(h2, axis=1, keepdims=True) + EPS; u2 = h2 / n2
            S = (u1 @ u2.T) / self.temp                               # [B,B] similarity; positive = diagonal
            P = softmax(S, axis=1)
            dS = (P - I) / B                                          # dL/dS, L = -mean log P[i,i] (InfoNCE)
            du1 = (dS @ u2) / self.temp
            du2 = (dS.T @ u1) / self.temp
            # backprop through the L2 row-norm: for u=h/n, dh = (du - u*<u,du>)/n
            dh1 = (du1 - u1 * (u1 * du1).sum(1, keepdims=True)) / n1
            dh2 = (du2 - u2 * (u2 * du2).sum(1, keepdims=True)) / n2
            dz1 = dh1 * (z1 > 0); dz2 = dh2 * (z2 > 0)
            gW = dz1.T @ a1 + dz2.T @ a2                              # both views update the shared weight
            gb = dz1.sum(0) + dz2.sum(0)
            self.W[l] = W - self.lr * gW
            self.b[l] = b - self.lr * gb
            a = self._norm(relu(a @ self.W[l].T + self.b[l]))         # clean rep propagates (no mask)


def _layernorm_fwd(h):
    mu = h.mean(1, keepdims=True); var = h.var(1, keepdims=True)
    sig = np.sqrt(var + EPS); y = (h - mu) / sig
    return y, (y, sig)


def _layernorm_vjp(dy, cache):
    """VJP of per-sample layer-norm (no affine): dh = (dy - mean(dy) - y*mean(dy*y)) / sig."""
    y, sig = cache
    return (dy - dy.mean(1, keepdims=True) - y * (dy * y).mean(1, keepdims=True)) / sig


class SCFFContrastOLU:
    """Contrastive (InfoNCE) SCFF with a CROSS-LAYER COORDINATION WINDOW (P3.1 / the user's Direction 1 / OLU).
    Layers are trained in joint groups of `window`: two masked views of the GROUP's input are forwarded through
    all `window` layers, ONE InfoNCE is computed at the group's TOP embedding, and the gradient is backpropagated
    through the WHOLE window (then detached at group boundaries). `window=1` == SCFFContrast (per-layer,
    gradient-isolated — the P3.0 baseline). `window=2,4` let a layer's update account for what the NEXT
    layer(s) need (the coordination P2.2 said was missing). The forward stack (infer) is unchanged: L layers,
    layer-norm between, so the per-layer depth probe is directly comparable to P3.0."""

    def __init__(self, dims, *, lr=0.03, seed=0, mask_ratio=0.5, temp=0.5, window=2,
                 normalize_input=True, init_gain=1.0):
        rng = np.random.default_rng(seed)
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.lr = lr; self.mask_ratio = mask_ratio; self.temp = temp; self.window = window
        self.normalize_input = normalize_input
        self.L = len(self.W)

    def _norm(self, a):
        return normalize(a, "layernorm")

    def infer(self, X):
        a = self._norm(X) if self.normalize_input else X
        reps = []
        for W, b in zip(self.W, self.b):
            a = self._norm(relu(a @ W.T + b))
            reps.append(a)
        return reps

    def dead_fraction(self, X):
        a = self._norm(X) if self.normalize_input else X
        fr = []
        for W, b in zip(self.W, self.b):
            h = relu(a @ W.T + b)
            fr.append(float((h.max(0) <= EPS).mean()))
            a = self._norm(h)
        return np.array(fr)

    def _view_fwd(self, a_in, s, w):
        """Forward ONE masked view through window layers [s, s+w): returns top L2-embedding u, its norm, and a
        per-layer cache (a_prev, z, ln_cache) for the backward pass."""
        a = a_in
        cache = []
        for j in range(w):
            l = s + j
            z = a @ self.W[l].T + self.b[l]; h = relu(z)
            if j < w - 1:
                a_next, ln = _layernorm_fwd(h)                 # propagate within the window (layer-norm)
            else:
                a_next, ln = None, None                        # top: feeds the InfoNCE embedding, not propagated
            cache.append((a, z, ln)); a = a_next
            h_top = h
        n = np.linalg.norm(h_top, axis=1, keepdims=True) + EPS
        return h_top / n, n, cache, h_top

    def _view_bwd(self, du, n, cache, h_top, w, gW, gb, s):
        """Backprop du (grad wrt top embedding) through the window, accumulating into gW/gb."""
        u = h_top / n
        dh = (du - u * (u * du).sum(1, keepdims=True)) / n     # through L2-norm -> grad wrt h_top
        for j in reversed(range(w)):
            a_prev, z, ln = cache[j]
            if j < w - 1:
                dh = _layernorm_vjp(dh, ln)                    # grad wrt a_{j} -> grad wrt h_{j}
            dz = dh * (z > 0)
            gW[s + j] += dz.T @ a_prev
            gb[s + j] += dz.sum(0)
            dh = dz @ self.W[s + j]                            # grad wrt this window-layer's input

    def train_step(self, Xb, rng, neg_partner=None):
        a = self._norm(Xb) if self.normalize_input else Xb
        B = len(Xb); I = np.eye(B)
        gW = [np.zeros_like(W) for W in self.W]; gb = [np.zeros_like(b) for b in self.b]
        s = 0
        while s < self.L:
            w = min(self.window, self.L - s)
            din = a.shape[1]
            a1 = a * (rng.random((B, din)) >= self.mask_ratio)        # two masked views of the window input
            a2 = a * (rng.random((B, din)) >= self.mask_ratio)
            u1, n1, c1, ht1 = self._view_fwd(a1, s, w)
            u2, n2, c2, ht2 = self._view_fwd(a2, s, w)
            S = (u1 @ u2.T) / self.temp; P = softmax(S, axis=1); dS = (P - I) / B
            du1 = (dS @ u2) / self.temp; du2 = (dS.T @ u1) / self.temp
            self._view_bwd(du1, n1, c1, ht1, w, gW, gb, s)
            self._view_bwd(du2, n2, c2, ht2, w, gW, gb, s)
            # propagate the CLEAN rep through the (now-to-be-updated) window for the next window's input
            ac = a
            for j in range(w):
                ac = self._norm(relu(ac @ self.W[s + j].T + self.b[s + j]))
            a = ac
            s += w
        for l in range(self.L):
            self.W[l] -= self.lr * gW[l]
            self.b[l] -= self.lr * gb[l]
