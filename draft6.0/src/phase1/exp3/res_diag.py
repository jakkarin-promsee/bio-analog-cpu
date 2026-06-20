"""
Exp 3 diagnostic: does a SCALED residual g_k = norm(g_{k-1} + eps*h_k) rescue the
per-block degradation (the norm-dilution artifact)? If small eps stops the degradation
but doesn't add depth benefit, it confirms SCFF adds no class info past the first layers.
digits, 3 seeds.  Run: python res_diag.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp0"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp1"))
from run_exp3 import Chain, gradient_boost, perlayer_probe, N_BLOCKS, BATCH
from run_exp1 import load_data

H, EP, SEEDS = 64, 40, [42, 137, 271]

for eps in [1.0, 0.5, 0.25, 0.1]:
    probes, finals = [], []
    for seed in SEEDS:
        Xtr, Ytr, Xte, Yte, C = load_data("digits", 600, 600, seed)
        ch = Chain(Xtr.shape[1], H, N_BLOCKS, seed, residual=True, res_scale=eps)
        rng = np.random.default_rng(seed)
        for _ in range(EP):
            idx = rng.permutation(len(Xtr))
            for s in range(0, len(Xtr), BATCH):
                ch.train_step(Xtr[idx[s:s + BATCH]], rng)
        probes.append(perlayer_probe(ch, Xtr, Ytr, Xte, Yte))
        _, te, _ = gradient_boost(ch.stream(Xtr), Ytr, ch.stream(Xte), Yte, C)
        finals.append(1 - te[-1])
    pm = np.median(probes, 0)
    print(f"eps={eps:<4}  per-block probe {np.round(pm,3)}  boosted-chain held {np.median(finals):.3f}")
