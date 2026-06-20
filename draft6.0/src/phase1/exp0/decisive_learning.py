"""
exp0 — the decisive question: does SCFF LEARNING beat a random projection?

So far every task was solved by the random first-layer lift alone (probe flat over
training). A gate that says "SCFF separates" must show SCFF's *learned* features beat
its own *random init*. This needs a task too hard for random features.

Measures, per task: top-tap probe at n=0 (random init) vs after training, + goodness gap.
Config: sum goodness, input-norm, two_sided theta=2.0, lr=.03, 50k. One thing varied: TASK.
Run: python decisive_learning.py
"""
import numpy as np
from scff_gate import SCFF, probe_acc_per_layer, DIMS, SEED, THETA, LR_SCFF, GOODNESS_MODE

BATCH, STREAM = 32, 50_000


# ---- task zoo (harder, to defeat random features) ----
def cluster_xor(n, rng, dim=2, sep=1.4, overlap=1.0):
    signs = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]; labels = [0, 1, 1, 0]
    return _from_centers(n, rng, signs, labels, dim, sep, overlap)


def ring8(n, rng, R=2.0, overlap=0.45):
    """8 clusters on a ring, alternating labels (circular parity)."""
    centers, labels = [], []
    for k in range(8):
        a = k * 2 * np.pi / 8
        centers.append((np.cos(a) * R, np.sin(a) * R)); labels.append(k % 2)
    return _place(n, rng, np.array(centers), labels, 2, overlap)


def checker(n, rng, overlap=0.30):
    """4x4 grid of clusters, checkerboard labels (i+j)%2 — needs adaptive features."""
    centers, labels = [], []
    for i in range(4):
        for j in range(4):
            centers.append((i - 1.5, j - 1.5)); labels.append((i + j) % 2)
    return _place(n, rng, np.array(centers) * 1.4, labels, 2, overlap)


def noisy_xor(n, rng, dim=8, sep=1.4, overlap=0.6):
    """4-cluster XOR in dims 0,1; dims 2..7 are pure noise (dilutes random features)."""
    signs = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]; labels = [0, 1, 1, 0]
    return _from_centers(n, rng, signs, labels, dim, sep, overlap)


def _from_centers(n, rng, signs, labels, dim, sep, overlap):
    centers = np.zeros((len(signs), dim))
    for i, (sx, sy) in enumerate(signs):
        centers[i, 0] = sep * sx; centers[i, 1] = sep * sy
    return _place(n, rng, centers, labels, dim, overlap)


def _place(n, rng, centers, labels, dim, overlap):
    K = len(centers); base = n // K; counts = [base] * K
    for i in range(n - base * K):
        counts[i] += 1
    Xs, Ys = [], []
    for c, lab, k in zip(centers, labels, counts):
        ct = np.zeros(dim); ct[:len(c)] = c
        Xs.append(rng.normal(ct, overlap, (k, dim))); Ys.append(np.full(k, lab))
    X = np.concatenate(Xs).astype(float); Y = np.concatenate(Ys).astype(int)
    p = rng.permutation(len(X)); return X[p], Y[p]


def assess(gen, in_dim, name):
    dims = [in_dim] + DIMS[1:]
    rng = np.random.default_rng(SEED)
    m = SCFF(dims, THETA, LR_SCFF, SEED, objective="two_sided", goodness_mode=GOODNESS_MODE)
    Xtr, Ytr = gen(2000, np.random.default_rng(SEED + 1))
    Xte, Yte = gen(2000, np.random.default_rng(SEED + 2))
    Xg, _ = gen(2000, np.random.default_rng(SEED + 3))
    p0 = np.array(probe_acc_per_layer(m, Xtr, Ytr, Xte, Yte))   # random init
    seen = 0
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng); m.train_step(Xb, rng); seen += BATCH
    p1 = np.array(probe_acc_per_layer(m, Xtr, Ytr, Xte, Yte))   # trained
    Gp, Gn = m.goodness(Xg)
    print(f"{name:28s} | random {p0.max():.3f} -> trained {p1.max():.3f} "
          f"(delta {p1.max()-p0.max():+.3f}) | top-G gap {Gp[-1]-Gn[-1]:+.3f} "
          f"| per-layer trained {np.round(p1,3)}")


print("task                         | random-init -> trained (learning gain) | goodness | depth")
print("-" * 104)
assess(lambda n, r: cluster_xor(n, r), 2, "4-cluster XOR 2D")
assess(lambda n, r: ring8(n, r), 2, "8-cluster ring 2D")
assess(lambda n, r: checker(n, r), 2, "4x4 checkerboard 2D")
assess(lambda n, r: noisy_xor(n, r), 8, "XOR + 6 noise dims (8D)")
