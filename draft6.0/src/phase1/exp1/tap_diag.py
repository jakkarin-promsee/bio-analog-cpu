"""
Exp 1 diagnostic: SCFF separability DEGRADES with depth on MNIST [0.82->0.52], yet the
block taps the LAST 2 layers (the worst). Does tapping the BEST/ALL layers recover the
block's accuracy? (S3 says 'last n'; the SCFF paper concatenates ALL layers.)
Compares readout on different tap sets, MNIST, 2 seeds. GD ceiling ~0.937.
Run: python tap_diag.py
"""
import os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp0"))
from scff_gate import SCFF, THETA, LR_SCFF, GOODNESS_MODE
from models_extra import MLP
from run_exp1 import load_data

BATCH, H, SCFF_EP, SUP_EP = 32, 128, 25, 40


def readout(F, Y, Fte, Yte, seed):
    ro = MLP([F.shape[1], 32, int(Y.max() + 1)], seed, lr=2e-3)
    rng = np.random.default_rng(seed)
    for _ in range(SUP_EP):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            ro.train_step(F[idx[s:s + BATCH]], Y[idx[s:s + BATCH]])
    return ro.accuracy(F, Y), ro.accuracy(Fte, Yte)


for seed in (42, 137):
    Xtr, Ytr, Xte, Yte, C = load_data("mnist", 3000, 3000, seed)
    sc = SCFF([Xtr.shape[1], H, H, H, H], THETA, LR_SCFF, seed,
              objective="two_sided", goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed)
    for _ in range(SCFF_EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            sc.train_step(Xtr[idx[s:s + BATCH]], rng)
    Rtr, Rte = sc.infer(Xtr), sc.infer(Xte)
    print(f"\nseed {seed}")
    tapsets = {"last-1 (L4)": [3], "last-2 (L3,L4)": [2, 3], "first-1 (L1)": [0],
               "first-2 (L1,L2)": [0, 1], "all-4": [0, 1, 2, 3]}
    for name, ix in tapsets.items():
        F = np.concatenate([Rtr[i] for i in ix], 1); Fte = np.concatenate([Rte[i] for i in ix], 1)
        tr, te = readout(F, Ytr, Fte, Yte, seed)
        print(f"  taps {name:16s} ({F.shape[1]:3d}-d)  held {te:.3f}  gap {tr-te:+.3f}")
