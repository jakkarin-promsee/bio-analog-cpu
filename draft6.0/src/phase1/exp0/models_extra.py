"""
exp0 expand — the pieces the gate didn't need: a hand-coded Adam MLP (the full-GD
ceiling 0c AND the tapped readout), and the two forward-only rivals for 0b (Oja/GHA
and a frozen random projection). Reuses the tested SCFF + tasks from scff_gate.py.

numpy only. The MLP backprop + Adam are written out so nothing is a black box.
"""
from __future__ import annotations
import numpy as np
from scipy.special import softmax

from scff_gate import SCFF, relu, EPS, DIMS  # tested gate pieces


# ----------------------------------------------------------------------------- Adam (over a param list)
class Adam:
    def __init__(self, params, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, l2=0.0):
        self.lr, self.b1, self.b2, self.eps, self.l2 = lr, b1, b2, eps, l2
        self.m = [np.zeros_like(p) for p in params]
        self.v = [np.zeros_like(p) for p in params]
        self.t = 0

    def step(self, params, grads):
        self.t += 1
        for i, (p, g) in enumerate(zip(params, grads)):
            if self.l2:
                g = g + self.l2 * p
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g * g
            mh = self.m[i] / (1 - self.b1 ** self.t)
            vh = self.v[i] / (1 - self.b2 ** self.t)
            p -= self.lr * mh / (np.sqrt(vh) + self.eps)   # in-place on the array


# ----------------------------------------------------------------------------- MLP (full-GD baseline + readout)
class MLP:
    """ReLU MLP, softmax cross-entropy, hand-coded backprop + Adam. Last layer linear."""

    def __init__(self, dims, seed, lr=1e-3, l2=0.0):
        rng = np.random.default_rng(seed)
        self.W = [rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.opt = Adam(self.W + self.b, lr=lr, l2=l2)
        self.L = len(self.W)

    def forward(self, X):
        self.cache = [X]
        a = X
        for l in range(self.L - 1):
            a = relu(a @ self.W[l].T + self.b[l])
            self.cache.append(a)
        return a @ self.W[-1].T + self.b[-1]            # logits

    def train_step(self, X, Y):
        logits = self.forward(X); B = len(X)
        p = softmax(logits, axis=1)
        oh = np.zeros_like(p); oh[np.arange(B), Y] = 1.0
        loss = float(-np.log(p[np.arange(B), Y] + 1e-12).mean())
        dl = (p - oh) / B
        gW = [None] * self.L; gb = [None] * self.L
        gW[-1] = dl.T @ self.cache[-1]; gb[-1] = dl.sum(0)
        da = dl @ self.W[-1]
        for l in range(self.L - 2, -1, -1):
            dz = da * (self.cache[l + 1] > 0)
            gW[l] = dz.T @ self.cache[l]; gb[l] = dz.sum(0)
            da = dz @ self.W[l]
        self.opt.step(self.W + self.b, gW + gb)
        return loss

    def predict(self, X):
        return self.forward(X).argmax(1)

    def accuracy(self, X, Y):
        return float((self.predict(X) == Y).mean())

    def n_weights(self):
        return sum(W.size + b.size for W, b in zip(self.W, self.b))


# ----------------------------------------------------------------------------- forward-only rivals (0b)
class _ForwardStack:
    """Shared forward path: input-norm, ReLU, inter-layer norm (mirrors SCFF exactly)."""

    def __init__(self, dims, seed, init_gain=1.0):
        rng = np.random.default_rng(seed)
        self.W = [init_gain * rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i]))
                  for i in range(len(dims) - 1)]
        self.L = len(self.W)

    @staticmethod
    def _norm(a):
        return a / (np.linalg.norm(a, axis=1, keepdims=True) + EPS)

    def infer(self, X):
        a = self._norm(X)
        reps = []
        for W in self.W:
            a = self._norm(relu(a @ W.T))
            reps.append(a)
        return reps


class RandomProjStack(_ForwardStack):
    """Frozen random projection — the floor: 'does SCFF beat random nonlinear features?'"""
    def train_step(self, X, rng=None):
        return  # no learning


class OjaStack(_ForwardStack):
    """Cheaper forward-only LEARNING rival: Sanger/GHA (online PCA) per layer + ReLU + norm."""

    def __init__(self, dims, seed, lr=0.01):
        super().__init__(dims, seed)
        self.lr = lr

    def train_step(self, X, rng=None):
        a = self._norm(X)
        for l, W in enumerate(self.W):
            z = a @ W.T                                  # linear response [B, out]
            # GHA: dW = lr * mean_b( y x^T - tril(y y^T) W )
            yxT = z.T @ a / len(X)
            yyT = z.T @ z / len(X)
            self.W[l] = W + self.lr * (yxT - np.tril(yyT) @ W)
            a = self._norm(relu(a @ self.W[l].T))
        return


# ----------------------------------------------------------------------------- higher-D rise probe task
def make_checkerboard_hd(n, rng, dim=3, grid=4, spacing=1.4, overlap=0.35):
    """dim-D checkerboard: grid^dim Gaussian clusters, label = parity of summed indices.
    3-D -> 64 clusters: too many for a single random layer, so depth has room to help."""
    import itertools
    idx = list(itertools.product(range(grid), repeat=dim))
    off = (grid - 1) / 2.0
    K = len(idx); base = n // K; counts = [base] * K
    for i in range(n - base * K):
        counts[i] += 1
    Xs, Ys = [], []
    for ix, k in zip(idx, counts):
        c = (np.array(ix) - off) * spacing
        Xs.append(rng.normal(c, overlap, (k, dim)))
        Ys.append(np.full(k, sum(ix) % 2))
    X = np.concatenate(Xs).astype(np.float64); Y = np.concatenate(Ys).astype(np.int64)
    p = rng.permutation(len(X)); return X[p], Y[p]


def match_width(target_weights, in_dim, out_dim, n_hidden):
    """Pick a hidden width so a [in, w*n_hidden, out] ReLU MLP ~= target_weights."""
    best, bestw = None, None
    for w in range(8, 400):
        dims = [in_dim] + [w] * n_hidden + [out_dim]
        nw = sum((dims[i] + 1) * dims[i + 1] for i in range(len(dims) - 1))
        if best is None or abs(nw - target_weights) < abs(best - target_weights):
            best, bestw = nw, w
    return bestw, best
