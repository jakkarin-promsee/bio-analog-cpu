"""
exp0 — overlap dial sweep for the 2D cluster-XOR gate task.
Goal: find the overlap where layer-1 probe is IMPERFECT and deeper layers improve it
(so "rises with depth" is a real, visible test, not saturated at L1).
Reports per-layer probe + dead-unit fraction + top goodness gap. One variable: overlap.
Run: python overlap_sweep.py
"""
import numpy as np
from scff_gate import (SCFF, make_cluster_xor, probe_acc_per_layer, tap_readout,
                       DIMS, SEED, THETA, LR_SCFF, GOODNESS_MODE, CLUST_SEP)

BATCH, STREAM = 32, 50_000


def run(overlap, sep=CLUST_SEP):
    gen = lambda n, r: make_cluster_xor(n, r, dim=2, sep=sep, overlap=overlap)
    rng = np.random.default_rng(SEED)
    m = SCFF(DIMS, THETA, LR_SCFF, SEED, objective="two_sided", goodness_mode=GOODNESS_MODE)
    seen = 0
    while seen < STREAM:
        Xb, _ = gen(BATCH, rng)
        m.train_step(Xb, rng)
        seen += BATCH
    Xtr, Ytr = gen(2000, np.random.default_rng(SEED + 1))
    Xte, Yte = gen(2000, np.random.default_rng(SEED + 2))
    Xg, _ = gen(2000, np.random.default_rng(SEED + 3))
    probe = np.array(probe_acc_per_layer(m, Xtr, Ytr, Xte, Yte))
    dead = m.dead_fraction(Xg)
    Gp, Gn = m.goodness(Xg)
    acc, _, _ = tap_readout(m, Xtr, Ytr, Xte, Yte)
    return probe, dead, Gp - Gn, acc


print(f"{'overlap':>7} | {'probe L1..L4':>28} | {'rise':>5} | {'dead L1..L4':>24} | {'tap':>5}")
print("-" * 86)
for ov in [0.55, 0.8, 1.0, 1.2, 1.4, 1.6]:
    probe, dead, gap, acc = run(ov)
    rise = probe[-1] - probe[0]
    print(f"{ov:7.2f} | {np.array2string(np.round(probe,3),separator=' '):>28} | "
          f"{rise:+5.3f} | {np.array2string(np.round(dead,2),separator=' '):>24} | {acc:5.3f}")
