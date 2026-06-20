"""
exp0 — diagnostic sweep (one variable at a time) to find where SCFF separates.

The gate failed at the locked theta=2.0: goodness rose but did not SPLIT, probe at
chance. Hypothesis: theta=2.0 sits above the whole achievable goodness band in our
ONLINE single-pass regime (He init + unit-norm inputs -> mean-goodness ~0.015 at
init; would need ~11x weight growth to reach 2.0, which offline FF gets from 1000
epochs but we don't). So only the "push G_pos up" term is ever active -> no contrast.

This sweep tests that, disciplined: vary ONE knob per row, same spiral/seed.
Reports: final top-layer (G_pos, G_neg, gap) + tapped-readout held-out acc + verdict.
Run: python diag_sweep.py
"""
import numpy as np
from scff_gate import (SCFF, make_spiral, probe_acc_per_layer, tap_readout,
                       DIMS, SEED, N_TURNS, NOISE_STD)

STREAM = 40_000
BATCH = 32


def run(theta=2.0, lr=0.03, objective="two_sided", init_gain=1.0, stream=STREAM):
    rng = np.random.default_rng(SEED)
    m = SCFF(DIMS, theta, lr, SEED, objective=objective, init_gain=init_gain)
    seen = 0
    while seen < stream:
        Xb, _ = make_spiral(BATCH, rng)
        m.train_step(Xb, rng)
        seen += BATCH
    Xtr, Ytr = make_spiral(2000, np.random.default_rng(SEED + 1))
    Xte, Yte = make_spiral(2000, np.random.default_rng(SEED + 2))
    Xg, _ = make_spiral(2000, np.random.default_rng(SEED + 3))
    Gp, Gn = m.goodness(Xg)
    probe = np.array(probe_acc_per_layer(m, Xtr, Ytr, Xte, Yte))
    acc, _, _ = tap_readout(m, Xtr, Ytr, Xte, Yte)
    rises = probe[-1] - probe[0]
    return Gp, Gn, probe, acc, rises


CONFIGS = [
    ("baseline  two_sided theta=2.0  lr=.03", dict(theta=2.0)),
    ("theta=1.0",                              dict(theta=1.0)),
    ("theta=0.5",                              dict(theta=0.5)),
    ("theta=0.2",                              dict(theta=0.2)),
    ("theta=0.1",                              dict(theta=0.1)),
    ("theta=0.05",                             dict(theta=0.05)),
    ("lr=0.1   theta=2.0",                     dict(theta=2.0, lr=0.1)),
    ("lr=0.3   theta=2.0",                     dict(theta=2.0, lr=0.3)),
    ("init_gain=3 theta=2.0",                  dict(theta=2.0, init_gain=3.0)),
    ("contrast (no theta) lr=.03",            dict(objective="contrast")),
    ("contrast (no theta) lr=.1",             dict(objective="contrast", lr=0.1)),
]

print(f"{'config':42s} | {'Gp_top':>7} {'Gn_top':>7} {'gap':>6} | "
      f"{'probe(L1..L4)':>24} | {'tap_acc':>7} | sep rise")
print("-" * 110)
for name, kw in CONFIGS:
    Gp, Gn, probe, acc, rises = run(**kw)
    sep = "YES" if (Gp[-1] > Gn[-1] and Gp[-1] - Gn[-1] > 0.05) else "no"
    risev = "YES" if rises > 0.03 else "no"
    print(f"{name:42s} | {Gp[-1]:7.2f} {Gn[-1]:7.2f} {Gp[-1]-Gn[-1]:6.2f} | "
          f"{np.array2string(np.round(probe,3), separator=' ')[:24]:>24} | "
          f"{acc:7.3f} | {sep:>3} {risev}")
