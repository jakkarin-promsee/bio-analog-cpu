"""
p4lib — the Phase-4 characterization apparatus: a controlled generator (known Bayes error), the three racers
(OURS = contrast+coordination+readout, BP-ceiling = tuned MLP, Mono-Forward = supervised-local), and a measured
backward-cost meter (credit-distance x weights).

The characterization frame (Bartunov 2018; Spyra 2025): fix a TUNED backprop baseline, dial a difficulty/scale
axis, watch where the gap-to-backprop opens; report the gap + a MEASURED cost Pareto (not theoretical). Difficulty
is principled via the Bayes error (synthetic-with-known-Bayes-error) — computed EXACTLY here from the known
Gaussian-mixture posterior (no classifier needed).

numpy only; reuses p3lib (SCFFContrastOLU + layernorm VJP) and the phase-1 MLP/Adam.
"""
from __future__ import annotations
import os, sys
import numpy as np
from scipy.special import softmax, logsumexp

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase3"))                # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "phase2"))                # p2lib (normalize/relu/EPS)
sys.path.insert(0, os.path.join(_HERE, "..", "phase1", "exp0"))        # models_extra (MLP)
from p3lib import SCFFContrastOLU, _layernorm_fwd, _layernorm_vjp      # noqa: E402
from p2lib import normalize, relu, EPS, SCFF2                          # noqa: E402  (SCFF2 = the energy-wall racer)
from models_extra import MLP, match_width                              # noqa: E402


# ============================================================ controlled generator (known Bayes error)
def make_gauss(n, rng, *, dim=40, n_class=4, n_clusters=16, overlap=0.6, sep=2.4, seed_centers=12345):
    """`n_clusters` isotropic Gaussian clusters (std=overlap) on a sep-spaced grid in a low-active subspace of
    `dim`, each cluster assigned a fixed random class in {0..n_class-1}. Difficulty rises with `overlap`.
    Returns X [n,dim], Y [n], and the generative params (centers, cluster_class, overlap) for EXACT Bayes error."""
    crng = np.random.default_rng(seed_centers)
    side = int(np.ceil(n_clusters ** (1.0 / 2)))                       # 2-active-dim grid
    coords = [(i, j) for i in range(side) for j in range(side)][:n_clusters]
    off = (side - 1) / 2.0
    centers = np.zeros((n_clusters, dim))
    for k, (i, j) in enumerate(coords):
        centers[k, 0] = (i - off) * sep; centers[k, 1] = (j - off) * sep
    cluster_class = crng.integers(0, n_class, size=n_clusters)
    counts = np.full(n_clusters, n // n_clusters); counts[: n - counts.sum()] += 1
    Xs, Ys = [], []
    for k in range(n_clusters):
        Xs.append(rng.normal(centers[k], overlap, (counts[k], dim)))
        Ys.append(np.full(counts[k], cluster_class[k]))
    X = np.concatenate(Xs); Y = np.concatenate(Ys).astype(np.int64)
    Q, _ = np.linalg.qr(np.random.default_rng(seed_centers + 1).normal(size=(dim, dim)))   # fixed rotation
    X = X @ Q
    p = rng.permutation(len(X))
    params = dict(centers=centers @ Q, cluster_class=cluster_class, overlap=overlap, dim=dim, n_class=n_class)
    return X[p].astype(np.float64), Y[p], params


def bayes_error(params, rng, n=40000):
    """EXACT (Monte-Carlo over the TRUE generative posterior) Bayes error. For x ~ the mixture, the optimal
    classifier picks argmax_c P(c|x); Bayes err = 1 - E[max_c P(c|x)]. Isotropic equal-variance Gaussians ->
    posterior ∝ sum over clusters-in-class of exp(-||x-center||^2/(2σ^2)). Σ cancels in the argmax-softmax."""
    C, cc, sig, dim, ncl = params["centers"], params["cluster_class"], params["overlap"], params["dim"], params["n_class"]
    # draw a fresh sample from the mixture
    K = len(C); counts = np.full(K, n // K); counts[: n - counts.sum()] += 1
    X = np.concatenate([rng.normal(C[k], sig, (counts[k], dim)) for k in range(K)])
    # log p(x|cluster k) = -||x-C_k||^2 / (2σ^2)  (+const, cancels)
    # ||x-c||^2 = ||x||^2 - 2 x·c + ||c||^2  -> [n,K] directly, no [n,K,dim] tensor (memory-safe to dim~1000s)
    d2 = (X * X).sum(1)[:, None] - 2.0 * X @ C.T + (C * C).sum(1)[None, :]    # [n, K]
    logpk = -d2 / (2 * sig * sig)
    # aggregate clusters into classes: logsumexp over clusters of each class
    logpc = np.full((len(X), ncl), -np.inf)
    for c in range(ncl):
        mk = (cc == c)
        if mk.any():
            logpc[:, c] = logsumexp(logpk[:, mk], axis=1)
    post = softmax(logpc, axis=1)
    return float(1.0 - post.max(1).mean())


# ============================================================ Mono-Forward (supervised-local racer)
class MonoForward:
    """Per-layer local cross-entropy on a projection M_l (classes x width) — forward-only, gradient-isolated
    between layers (the Mono-Forward reference). Layer-norm forward (matched to OURS). Predict = sum of per-layer
    logits."""
    def __init__(self, dims, C, *, lr=0.02, seed=0):
        rng = np.random.default_rng(seed)
        self.W = [rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i])) for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.M = [rng.normal(0, np.sqrt(1.0 / dims[i + 1]), (C, dims[i + 1])) for i in range(len(dims) - 1)]
        self.mc = [np.zeros(C) for _ in range(len(dims) - 1)]
        self.lr = lr; self.L = len(self.W); self.C = C

    def _fwd_logits(self, X):
        a = normalize(X, "layernorm"); logits = np.zeros((len(X), self.C))
        for W, b, M, mc in zip(self.W, self.b, self.M, self.mc):
            h = relu(a @ W.T + b); a = normalize(h, "layernorm")
            logits = logits + a @ M.T + mc
        return logits

    def predict(self, X):
        return self._fwd_logits(X).argmax(1)

    def train_step(self, Xb, Yb):
        a = normalize(Xb, "layernorm"); B = len(Xb)
        oh = np.zeros((B, self.C)); oh[np.arange(B), Yb] = 1.0
        for l in range(self.L):
            z = a @ self.W[l].T + self.b[l]; h = relu(z)
            an, ln = _layernorm_fwd(h)
            logits = an @ self.M[l].T + self.mc[l]
            dlog = (softmax(logits, axis=1) - oh) / B
            self.M[l] -= self.lr * (dlog.T @ an); self.mc[l] -= self.lr * dlog.sum(0)
            dan = dlog @ self.M[l]
            dz = _layernorm_vjp(dan, ln) * (z > 0)
            self.W[l] -= self.lr * (dz.T @ a); self.b[l] -= self.lr * dz.sum(0)
            a = an                                                     # detached forward to next layer


# ============================================================ readout (for OURS / energy baseline)
def fit_readout(F, Y, C, seed, epochs=60, lr=2e-3, batch=32):
    ro = MLP([F.shape[1], 32, C], seed, lr=lr); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), batch):
            ro.train_step(F[idx[s:s + batch]], Y[idx[s:s + batch]])
    return ro


def readout_feats(reps, last_n=None):
    """Tap the readout. `last_n=None` -> ALL layers concatenated (the legacy all-tap, kept for A1/A2/...).
    `last_n=k` -> only the LAST k layer reps -> the realistic position a single GD readout head sits (the top
    of the bulk). Reading from the top is what stops the readout from BYPASSING decayed deep layers via the
    early ones (P4.3: that bypass is exactly what masks the energy depth-wall)."""
    return np.concatenate(reps if last_n is None else reps[-last_n:], 1)


def linear_probe(Ftr, Ytr, Fte, Yte, C, seed, epochs=120, lr=3e-3, batch=64):
    """Numpy LINEAR probe (1-layer softmax via Adam, NO sklearn -> no OpenMP phantom): held-out accuracy of a
    rep under a linear classifier = its linear separability. The diagnostic that exposes representational decay
    layer-by-layer (the 'context decay by depth')."""
    pr = MLP([Ftr.shape[1], C], seed, lr=lr); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Ftr))
        for s in range(0, len(Ftr), batch):
            pr.train_step(Ftr[idx[s:s + batch]], Ytr[idx[s:s + batch]])
    return float((pr.predict(Fte) == Yte).mean())


def per_layer_probe(reps_tr, Ytr, reps_te, Yte, C, seed):
    """Linear probe at every layer -> the per-layer separability profile (list length L). probe[-1] = the
    last-layer probe (the readout's view); the full list = the within-stack decay curve."""
    return [linear_probe(rt, Ytr, re, Yte, C, seed) for rt, re in zip(reps_tr, reps_te)]


# ============================================================ measured backward-cost meter (credit-dist x weights)
def _mlp_cost(dims):                                                   # full backprop: W_l reached at distance L-l
    Ln = len(dims) - 1
    return sum((Ln - l) * (dims[l] + 1) * dims[l + 1] for l in range(Ln))


def cost_ours(D, Wd, Lb, w, C, readout_last_n=None):
    dims = [D] + [Wd] * Lb; bulk = 0; s = 0
    while s < Lb:
        ww = min(w, Lb - s)
        for j in range(ww):
            l = s + j; bulk += ww * (dims[l] + 1) * dims[l + 1]        # window backprops ww deep (local)
        s += ww
    ro_in = (Lb if readout_last_n is None else min(readout_last_n, Lb)) * Wd
    readout = _mlp_cost([ro_in, 32, C])                               # readout (full but tiny): all-tap or last-n
    return bulk + readout


def cost_bp(dims):
    return _mlp_cost(dims)


def cost_mono(dims, C):                                                # each layer: 1-deep local backprop + proj
    return sum((dims[l] + 1) * dims[l + 1] + (dims[l + 1] + 1) * C for l in range(len(dims) - 1))


# ============================================================ the three racers (train + eval + cost)
def race_ours(Xtr, Ytr, Xte, Yte, C, *, L=4, Wd=64, w=2, ep=25, seed=0, batch=32,
              readout_last_n=None, probe=False):
    """OURS = contrast (InfoNCE, two-mask) + w-window coordination SCFF bulk + GD readout. `readout_last_n`
    selects the readout tap (None = all-tap legacy; k = last-k layers, the realistic GD-head position).
    `probe=True` also returns the per-layer linear-probe profile (the wall diagnostic)."""
    m = SCFFContrastOLU([Xtr.shape[1]] + [Wd] * L, seed=seed, window=w, mask_ratio=0.5, temp=0.5)
    rng = np.random.default_rng(seed)
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    Ftr, Fte = readout_feats(reps_tr, readout_last_n), readout_feats(reps_te, readout_last_n)
    ro = fit_readout(Ftr, Ytr, C, seed)
    out = dict(acc_tr=float((ro.predict(Ftr) == Ytr).mean()), acc_te=float((ro.predict(Fte) == Yte).mean()),
               bwd=cost_ours(Xtr.shape[1], Wd, L, w, C, readout_last_n))
    if probe:
        out["probe"] = per_layer_probe(reps_tr, Ytr, reps_te, Yte, C, seed)
    return out


def race_energy(Xtr, Ytr, Xte, Yte, C, *, L=4, Wd=64, ep=25, seed=0, batch=32,
                goodness="squared", norm="lengthnorm", readout_last_n=None, probe=False):
    """The OLD algorithm = energy-goodness SCFF (Phase-1/2): G=Σh² ('squared') under length-norm = the raw
    depth-wall cell that Phase 3 superseded. Same width / readout / probe protocol as race_ours, so the only
    thing that differs from OURS is the LEARNING RULE (energy-Σh² vs InfoNCE-contrast). Credit is 1-layer-local
    (no cross-layer window) -> backward cost = cost_ours with w=1."""
    m = SCFF2([Xtr.shape[1]] + [Wd] * L, goodness=goodness, norm=norm, goodness_scale="sum",
              theta=2.0, seed=seed)
    rng = np.random.default_rng(seed)
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    Ftr, Fte = readout_feats(reps_tr, readout_last_n), readout_feats(reps_te, readout_last_n)
    ro = fit_readout(Ftr, Ytr, C, seed)
    out = dict(acc_tr=float((ro.predict(Ftr) == Ytr).mean()), acc_te=float((ro.predict(Fte) == Yte).mean()),
               bwd=cost_ours(Xtr.shape[1], Wd, L, 1, C, readout_last_n))
    if probe:
        out["probe"] = per_layer_probe(reps_tr, Ytr, reps_te, Yte, C, seed)
    return out


def race_bp(Xtr, Ytr, Xte, Yte, C, *, total, in_dim, depths=(2, 3, 4),
            lrs=(1e-2, 3e-3, 1e-3, 3e-4), wds=(0.0, 1e-3), ep=60, seed=0, batch=32, te_masks=None):
    """GENUINELY-tuned BP ceiling (Bartunov/Spyra fairness): search {depth-shape × lr × weight-decay} at the
    MATCHED weight budget, pick best held-out, return the chosen config. Not exhaustive Optuna, but well past a
    single lr grid -- the whole gap-to-BP headline rides on this being a real ceiling, not a strawman. Cost is
    the chosen shape's backward credit-assignment work. `te_masks` (dict name->bool-mask over the test set):
    if given, the returned dict also carries `acc_<name>` = the best model's accuracy on that test subset
    (for the mixed-task per-subset BP reference)."""
    best = None; seen = set()
    for nh in depths:
        bw, _ = match_width(total, in_dim, C, nh)
        if (nh, bw) in seen:                                            # skip degenerate duplicate shapes
            continue
        seen.add((nh, bw))
        dims = [in_dim] + [bw] * nh + [C]
        for lr in lrs:
            for wd in wds:
                m = MLP(dims, seed, lr=lr, l2=wd); rng = np.random.default_rng(seed)
                for _ in range(ep):
                    idx = rng.permutation(len(Xtr))
                    for s in range(0, len(Xtr), batch):
                        m.train_step(Xtr[idx[s:s + batch]], Ytr[idx[s:s + batch]])
                te = float(m.accuracy(Xte, Yte))
                if best is None or te > best["acc_te"]:
                    best = dict(acc_te=te, acc_tr=float(m.accuracy(Xtr, Ytr)),
                                bwd=cost_bp(dims), lr=lr, wd=wd, depth=nh, width=bw)
                    if te_masks:
                        pred = m.predict(Xte)
                        for nm, msk in te_masks.items():
                            best[f"acc_{nm}"] = float((pred[msk] == Yte[msk]).mean())
    return best


def race_mono(Xtr, Ytr, Xte, Yte, C, *, dims, ep=40, seed=0, batch=32):
    m = MonoForward(dims, C, seed=seed); rng = np.random.default_rng(seed)
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            m.train_step(Xtr[idx[s:s + batch]], Ytr[idx[s:s + batch]])
    return dict(acc_tr=float((m.predict(Xtr) == Ytr).mean()), acc_te=float((m.predict(Xte) == Yte).mean()),
                bwd=cost_mono(dims, C))


def n_w(dims):
    return sum((dims[i] + 1) * dims[i + 1] for i in range(len(dims) - 1))
