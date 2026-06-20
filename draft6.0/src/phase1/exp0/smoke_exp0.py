"""exp0 smoke test — verify the new pieces work and print the headline numbers (1 seed)."""
import numpy as np
from scff_gate import (SCFF, make_checkerboard, DIMS, SEED, THETA, LR_SCFF,
                       GOODNESS_MODE, TAPS)
from models_extra import MLP, OjaStack, RandomProjStack, match_width

BATCH, STREAM = 32, 50_000


def taps_feat(stack, X):
    return np.concatenate(stack.infer(X)[-TAPS:], axis=1)


def train_readout(stack, Xtr, Ytr, Xte, Yte, seed, epochs=150):
    F = taps_feat(stack, Xtr); Fte = taps_feat(stack, Xte)
    ro = MLP([F.shape[1], 32, 2], seed, lr=2e-3)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            b = idx[s:s + BATCH]; ro.train_step(F[b], Ytr[b])
    return ro.accuracy(Fte, Yte)


def train_forward(stack, gen, rng):
    seen = 0
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng); stack.train_step(Xb, rng); seen += BATCH


gen = make_checkerboard
Xtr, Ytr = gen(2000, np.random.default_rng(SEED + 1))
Xte, Yte = gen(2000, np.random.default_rng(SEED + 2))

# --- 0c: full-GD ceiling (weights matched to SCFF system ~16.9k) ---
scff_sys = sum(W.size + b.size for W, b in zip(SCFF(DIMS, THETA, LR_SCFF, SEED).W,
                                               SCFF(DIMS, THETA, LR_SCFF, SEED).b))
scff_sys += 128 * 32 + 32 + 32 * 2 + 2           # + tapped readout
w, nw = match_width(scff_sys, 2, 2, 4)
gd = MLP([2, w, w, w, w, 2], SEED, lr=1e-3)
rng = np.random.default_rng(SEED)
seen = 0
while seen < STREAM:
    Xb, Yb = gen(BATCH, rng); gd.train_step(Xb, Yb); seen += BATCH
print(f"target weights={scff_sys}  GD baseline width={w} weights={gd.n_weights()}")
print(f"0c  full-GD ceiling           held-out acc = {gd.accuracy(Xte, Yte):.3f}")

# --- SCFF + tapped readout ---
sc = SCFF(DIMS, THETA, LR_SCFF, SEED, objective="two_sided", goodness_mode=GOODNESS_MODE)
train_forward(sc, gen, np.random.default_rng(SEED))
print(f"0a  SCFF(two-sided) + readout  held-out acc = {train_readout(sc, Xtr, Ytr, Xte, Yte, SEED):.3f}")

sc2 = SCFF(DIMS, THETA, LR_SCFF, SEED, objective="contrast", goodness_mode=GOODNESS_MODE)
train_forward(sc2, gen, np.random.default_rng(SEED))
print(f"0a  SCFF(contrast)  + readout  held-out acc = {train_readout(sc2, Xtr, Ytr, Xte, Yte, SEED):.3f}")

# --- 0b rivals ---
oja = OjaStack(DIMS, SEED, lr=0.01); train_forward(oja, gen, np.random.default_rng(SEED))
print(f"0b  Oja/GHA         + readout  held-out acc = {train_readout(oja, Xtr, Ytr, Xte, Yte, SEED):.3f}")

rp = RandomProjStack(DIMS, SEED)
print(f"0b  random-proj     + readout  held-out acc = {train_readout(rp, Xtr, Ytr, Xte, Yte, SEED):.3f}")
