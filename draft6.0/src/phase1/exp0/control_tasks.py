"""
exp0 — control diagnostics: is the flat-goodness failure a BUG, a 2D-mixture problem,
or under-training? Isolate by changing the TASK (not the model).

  A. 2D two-blob   — trivial; a correct SCFF must separate this (probe >> 0.5).
  B. 8D two-blob   — tests "does higher-D help the additive-negative contrast?"
  C. 8D 4-cluster XOR-ish (2 classes) — compositional, SCFF's home turf.
  D. spiral, long+hot (lr=0.2, 150k) — tests pure under-training on the locked task.

For each: per-layer (G_pos, G_neg) and per-layer probe acc. If A fails -> bug.
If A/B pass but spiral fails -> the 2D spiral / additive-negative is the issue.
Run: python control_tasks.py
"""
import numpy as np
from scff_gate import SCFF, make_spiral, probe_acc_per_layer, DIMS, SEED

BATCH = 32


def blobs(n, rng, dim=2, centers=None, std=0.3):
    if centers is None:
        centers = np.array([[-1.5] + [0] * (dim - 1), [1.5] + [0] * (dim - 1)], float)
    k = n // 2
    Xs, Ys = [], []
    for c, ct in enumerate(centers[:2]):
        Xs.append(rng.normal(ct, std, (k, dim)))
        Ys.append(np.full(k, c))
    X = np.concatenate(Xs); Y = np.concatenate(Ys)
    p = rng.permutation(len(X)); return X[p], Y[p]


def cluster_xor(n, rng, dim=8, std=0.25):
    """4 clusters at +-2 on two axes; label = XOR of the two axis signs (2 classes)."""
    centers = np.zeros((4, dim))
    signs = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]
    labels = [0, 1, 1, 0]
    for i, (sx, sy) in enumerate(signs):
        centers[i, 0] = 2 * sx; centers[i, 1] = 2 * sy
    k = n // 4
    Xs, Ys = [], []
    for i in range(4):
        Xs.append(rng.normal(centers[i], std, (k, dim)))
        Ys.append(np.full(k, labels[i]))
    X = np.concatenate(Xs); Y = np.concatenate(Ys)
    p = rng.permutation(len(X)); return X[p], Y[p]


def train_eval(gen, in_dim, lr=0.1, stream=60_000, objective="contrast", theta=2.0,
               goodness_mode="sum"):
    dims = [in_dim] + DIMS[1:]
    rng = np.random.default_rng(SEED)
    m = SCFF(dims, theta, lr, SEED, objective=objective, goodness_mode=goodness_mode)
    seen = 0
    while seen < stream:
        Xb, _ = gen(BATCH, rng)
        m.train_step(Xb, rng)
        seen += BATCH
    Xtr, Ytr = gen(2000, np.random.default_rng(SEED + 1))
    Xte, Yte = gen(2000, np.random.default_rng(SEED + 2))
    Xg, _ = gen(2000, np.random.default_rng(SEED + 3))
    Gp, Gn = m.goodness(Xg)
    probe = np.array(probe_acc_per_layer(m, Xtr, Ytr, Xte, Yte))
    return Gp, Gn, probe


def report(name, Gp, Gn, probe):
    print(f"\n=== {name} ===")
    print(f"  G_pos : {np.round(Gp,3)}")
    print(f"  G_neg : {np.round(Gn,3)}")
    print(f"  gap   : {np.round(Gp-Gn,3)}")
    print(f"  probe : {np.round(probe,3)}   (chance 0.5)")


print("\n################  SUM goodness (||h||^2, default now)  ################")
report("A. 2D two-blob (contrast, sum)", *train_eval(lambda n, r: blobs(n, r, 2), 2))
report("C. 8D cluster-XOR (contrast, sum)", *train_eval(lambda n, r: cluster_xor(n, r, 8), 8))
report("D. spiral two_sided theta=2.0 lr=.03 50k (THE LOCKED CONFIG, sum)",
       *train_eval(make_spiral, 2, lr=0.03, stream=50_000, objective="two_sided", theta=2.0))
report("D2. spiral two_sided theta=2.0 lr=.1 100k (sum)",
       *train_eval(make_spiral, 2, lr=0.1, stream=100_000, objective="two_sided", theta=2.0))
report("D3. spiral contrast lr=.1 100k (sum)",
       *train_eval(make_spiral, 2, lr=0.1, stream=100_000, objective="contrast"))
