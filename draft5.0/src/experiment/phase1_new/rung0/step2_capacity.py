"""Phase 1 (new) · Rung 0 · Step 2 — CAPACITY (reachability): what shapes can the carve reach?

Step-1 showed the Ganglion IS a quilt of planes. Step-2 asks the payoff question: given that carve,
which target shapes can it MATCH, and where is the wall? We best-fit out0 to six synthetic targets
with a GENERIC optimizer (free weights — NOT the chip's attribution rule; that is Phase 2 / H1), so
a bad fit means the *hardware* can't represent the shape, not that learning failed to find it.

The fit runs on the fast numpy mirror (verified == the real ALU, err 0.0); each best-fit weight set
is re-checked on the REAL probe at full resolution, and THAT residual is what we report + plot.
Each figure: target | best-fit, as a heatmap (top) and the honest 3-D shape (bottom).

STRESS TEST: for the two telling shapes (xor, gaussian) we ALSO draw the three L2 lines the optimizer
chose, on target vs fit — so we see the *mechanism* (why xor can't be carved by one line-set; the
gaussian's concurrent 3-lines -> 6 wedges), not just a residual number.

Run:  python -m src.experiment.phase1_new.rung0.step2_capacity
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, reach, plots

GRID_N = 121
DOMAIN = (-1.0, 1.0)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step2")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    X1, X2 = np.meshgrid(xs, ys)
    STRESS = ("xor", "gaussian")        # the two shapes where the 3-line mechanism is most telling
    print("# rung-0 step-2 reachability | fit out0 to targets (generic optimizer, weights free) "
          "| 0 = perfect, ~1 = no better than the mean\n")
    rows = []
    for name in reach.TARGET_NAMES:
        w, fit_resid = reach.fit_target(name, n_grid=21, n_restart=12, seed=0)
        probe = harness.GanglionProbe(list(w))
        Z0, _ = probe.surface(xs, ys)
        T_raw = reach.target_surface(name, X1, X2)
        Tn, mu, sd = reach.normalize(T_raw)
        real_resid = float(np.sqrt(np.mean((Z0 - Tn) ** 2)))
        P_raw = Z0 * sd + mu
        plots.target_vs_fit(name, T_raw, P_raw, xs, ys, os.path.join(FIGDIR, f"{name}.png"),
                            resid=real_resid)
        if name in STRESS:
            # the three L2 lines the optimizer chose (canonical order: weights 0..5, biases 6..8)
            lines = [(w[0], w[1], w[6]), (w[2], w[3], w[7]), (w[4], w[5], w[8])]
            plots.lines_on_surfaces(name, T_raw, P_raw, lines, xs, ys,
                                    os.path.join(FIGDIR, f"{name}_lines.png"), resid=real_resid)
        rows.append((name, fit_resid, real_resid))
        print(f"{name:>11}:  fit-resid(mirror 21^2)={fit_resid:.3f}   real-resid(ALU 121^2)={real_resid:.3f}")
    plots.make_gallery(FIGDIR, "Rung-0 · Step-2 reachability (target | best-fit) + stress (xor, gaussian)")
    print(f"\nwrote {len(rows)} target figures (+ {len(STRESS)} stress) + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
