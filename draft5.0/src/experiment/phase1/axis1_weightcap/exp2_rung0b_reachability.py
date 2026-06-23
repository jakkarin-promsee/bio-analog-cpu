"""Phase 1 · Axis 1 · Experiment 2 — Rung-0b reachability (the representational LIMIT).

Fit the real 2-3-3-2 forward (out0) to synthetic target surfaces with a GENERIC optimizer
(NOT the chip's attribution rule — that is Phase 2 / H1), weights free/unbounded. Best-fit
norm-residual per target = what the atom CAN represent (a lower bound; ReLU fits are nonconvex).
The fit runs on the numpy mirror (verified == ALU, err 0.0); each best-fit weight set is re-checked
on the REAL probe at full resolution, and that real residual is what we report + plot.

Run:  python -m src.experiment.phase1.axis1_weightcap.exp2_rung0b_reachability    (from the repo root)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1 import harness, reach, plots

GRID_N = 121
DOMAIN = (-1.0, 1.0)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "exp2")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    X1, X2 = np.meshgrid(xs, ys)
    print("# rung-0b reachability | fit out0 to targets (generic optimizer, weights free) "
          "| limit = best-fit norm-residual (0 = perfect, ~1 = no better than the mean)\n")
    rows = []
    for name in reach.TARGET_NAMES:
        w, fit_resid = reach.fit_target(name, n_grid=21, n_restart=12, seed=0)
        # verify on the REAL ALU at full resolution
        probe = harness.GanglionProbe(list(w))
        Z0, _ = probe.surface(xs, ys)
        T_raw = reach.target_surface(name, X1, X2)
        Tn, mu, sd = reach.normalize(T_raw)
        real_resid = float(np.sqrt(np.mean((Z0 - Tn) ** 2)))   # normalized (comparable across targets)
        P_raw = Z0 * sd + mu                                   # de-normalize prediction to real target units
        plots.target_vs_fit(name, T_raw, P_raw, xs, ys, os.path.join(FIGDIR, f"{name}.png"), resid=real_resid)
        rows.append((name, fit_resid, real_resid))
        print(f"{name:>11}:  fit-resid(mirror 21^2)={fit_resid:.3f}   real-resid(ALU 121^2)={real_resid:.3f}")
    plots.make_gallery(FIGDIR, "Axis-1 rung-0b reachability — exp-2 (target | best-fit)")
    print(f"\nwrote {len(rows)} target figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
