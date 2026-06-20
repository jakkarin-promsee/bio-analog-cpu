"""
exp0 decisive sanity: does SCFF EVER beat a random projection?
On low-D Gaussian clusters random features already win (JL). The literature says SCFF
wins on high-D (MNIST 98.7%). Test the in-between: sklearn load_digits (64-D, 10 class),
offline, so we learn whether the n=5 'SCFF ~ random' result is a low-D artifact or real.
Linear probe on tapped features. Reports SCFF (two widths) vs random-proj vs full-GD.
Run: python digits_check.py
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from scff_gate import SCFF, THETA, GOODNESS_MODE
from models_extra import MLP, RandomProjStack

TAPS, BATCH, EPOCHS = 2, 32, 40

d = load_digits()
X = d.data / 16.0; Y = d.target                       # 64-D in [0,1], 10 classes
Xtr, Xte, Ytr, Yte = train_test_split(X, Y, test_size=0.3, random_state=0)


def tap(s, A): return np.concatenate(s.infer(A)[-TAPS:], 1)


def lin(s):
    clf = LogisticRegression(C=1.0, max_iter=4000).fit(tap(s, Xtr), Ytr)
    return clf.score(tap(s, Xte), Yte)


def train(stack, lr_steps=True):
    rng = np.random.default_rng(0)
    for _ in range(EPOCHS):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            stack.train_step(Xtr[idx[s:s + BATCH]], rng)


for width in (64, 256):
    dims = [64, width, width, width, width]
    sc = SCFF(dims, THETA, 0.03, 0, objective="two_sided", goodness_mode=GOODNESS_MODE)
    train(sc)
    rp = RandomProjStack(dims, 0)
    print(f"width={width:3d}  SCFF linear-probe {lin(sc):.3f}   random-proj {lin(rp):.3f}")

# full-GD reference on raw 64-D
gd = MLP([64, 64, 64, 10], 0, lr=1e-3)
rng = np.random.default_rng(0)
for _ in range(EPOCHS):
    idx = rng.permutation(len(Xtr))
    for s in range(0, len(Xtr), BATCH):
        gd.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
print(f"full-GD (raw 64-D, [64,64,10]) held-out {gd.accuracy(Xte, Yte):.3f}")
# raw-pixel linear baseline (no features at all)
print(f"raw-pixel linear probe {LogisticRegression(max_iter=4000).fit(Xtr,Ytr).score(Xte,Yte):.3f}")
