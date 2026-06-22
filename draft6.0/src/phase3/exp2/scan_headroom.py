"""
P3.2 (side road A) — hunt for a DEPTH-HEADROOM flat-MLP task.

P3.1 found flat-CIFAR has no depth headroom for ANYONE (GD-hidden flat ~0.36), so 'slope >= 0' is the wrong bar
there. To test whether contrast+coordination can actually COMPOSE depth (rise), we need a task where:
  GD-hidden RISES with depth  (depth genuinely helps -> headroom exists)  AND
  energy-SCFF DECLINES         (a real wall -> something to fix)
Then the decisive test (next script) is whether contrast+coordination rises where energy can't.

This scans the TESTED make_tierb generator (p2lib) across HARD settings (many clusters, high overlap) and reports
per-layer probe slopes for GD-hidden vs energy-SCFF. No new generator = no new bugs. Pick the config that
maximizes (GD rises) & (energy declines).

Run:  OMP_NUM_THREADS=1 python -u scan_headroom.py
"""
from __future__ import annotations
import os, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))                 # run_p3_0 bench
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))         # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import SCFF2, make_tierb, probe_per_layer                  # noqa: E402
from run_p3_0 import train_energy, train_mlp, gd_hidden_probe, n_w, BATCH, ENERGY_WALL  # noqa: E402
from models_extra import match_width                                  # noqa: E402

L = 6
NTR, NTE = 4000, 1500
SEED = 42

CONFIGS = [
    dict(grid=4, n_active=3, overlap=0.6, dim=40, n_class=4),    # 64 clusters
    dict(grid=4, n_active=3, overlap=1.0, dim=40, n_class=4),    # 64, more overlap
    dict(grid=3, n_active=4, overlap=0.8, dim=40, n_class=4),    # 81 clusters
    dict(grid=4, n_active=4, overlap=0.8, dim=50, n_class=4),    # 256 clusters
    dict(grid=4, n_active=2, overlap=1.0, dim=40, n_class=4),    # 16 clusters, high overlap
    dict(grid=5, n_active=3, overlap=0.9, dim=50, n_class=8),    # 125 clusters, 8-class
    dict(grid=4, n_active=3, overlap=1.4, dim=40, n_class=4),    # 64, very high overlap (entangled)
    dict(grid=3, n_active=5, overlap=0.9, dim=60, n_class=4),    # 243 clusters
]


def slope(p):
    return float(np.polyfit(np.arange(1, len(p) + 1), p, 1)[0])


def main():
    t0 = time.time()
    print(f"=== HEADROOM SCAN (make_tierb hard) | L={L} | seed={SEED} ===", flush=True)
    print(f"{'cfg':<48} {'GDslp':>7} {'GD L1->L6':>16} {'ENslp':>7} {'EN L1->L6':>16}  headroom?", flush=True)
    best = []
    for c in CONFIGS:
        rng_tr = np.random.default_rng(SEED + 1); rng_te = np.random.default_rng(SEED + 2)
        Xtr, Ytr = make_tierb(NTR, rng_tr, **c); Xte, Yte = make_tierb(NTE, rng_te, **c)
        D = Xtr.shape[1]; C = int(c["n_class"]); WIDTH = 64
        dims = [D] + [WIDTH] * L
        # GD ceiling (matched-ish), per-layer hidden probe
        budget = n_w(dims) + (L * WIDTH * C + C)
        w, _ = match_width(budget, D, C, L)
        gd, _ = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, SEED, 50)
        gd_p = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
        # energy-SCFF (the wall)
        en = train_energy(dims, Xtr, SEED, 25)
        en_p = probe_per_layer(en, Xtr, Ytr, Xte, Yte)
        gslp, eslp = slope(gd_p), slope(en_p)
        hr = (gslp > 0.004) and (eslp < -0.004)            # GD rises AND energy declines
        flag = "  *** YES ***" if hr else ("  gd-rises" if gslp > 0.004 else "")
        print(f"{str(c):<48} {gslp:+.4f} {gd_p[0]:.3f}->{gd_p[-1]:.3f}    "
              f"{eslp:+.4f} {en_p[0]:.3f}->{en_p[-1]:.3f}{flag}", flush=True)
        best.append((hr, gslp - eslp, c, gslp, eslp))
    best.sort(key=lambda t: (t[0], t[1]), reverse=True)
    print(f"\nBEST: {best[0][2]}  (GD {best[0][3]:+.4f}, EN {best[0][4]:+.4f}, headroom={best[0][0]})")
    print(f"  ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
