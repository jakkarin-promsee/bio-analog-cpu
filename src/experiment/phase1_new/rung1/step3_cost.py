"""Phase 1 (new) · Rung 1 · Step 3 — what the cap COSTS the familiar shapes (the rung-0 trio).

We already met parabola / gaussian / xor in rung 0. Now re-fit them with the optimizer's weights
BOUNDED by the cap, and ask two different questions as the cap tightens:

  - GAIN cost (raw residual): can the output reach the target's amplitude? -> collapses past the knee.
  - SHAPE cost (scale-free residual): factoring amplitude out, can the cap'd hardware still CARVE the
    shape? -> stays close to the rung-0 baseline until the cap is brutally tight.

The gap between the two is the headline: the ceiling is a GAIN limit, not a SHAPE limit. It makes the
Ganglion quiet, not dumb. (Continuity: the dashed lines are rung-0's uncapped residuals.)

Run:  python -m src.experiment.phase1_new.rung1.step3_cost
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, reach, plots

SHAPES = ["parabola", "gaussian", "xor"]
RUNG0 = {"parabola": 0.13, "gaussian": 0.24, "xor": 0.50}   # uncapped baselines (rung-0 step-2)
W_MAXES = [0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0]
VIZ_SHAPES = ["gaussian", "parabola"]      # show the real shape under the cap for these
VIZ_CAPS = [3.0, 0.5, 0.2]
GRID_N = 101
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step3")


def real_shape_panels(name, xs, ys):
    """Top row = the capped hardware's raw best attempt (real units) -> amplitude collapses.
    Bottom row = its best SHAPE attempt (scale-free), normalized -> shape persists."""
    X1, X2 = np.meshgrid(xs, ys)
    T_raw = reach.target_surface(name, X1, X2)
    Tn, mu, sd = reach.normalize(T_raw)
    raw_row, norm_row = [T_raw], [T_raw]
    for cap in VIZ_CAPS:
        w_raw, _ = reach.fit_target(name, ceiling=cap, scale_free=False, n_restart=10)
        Zr, _ = harness.GanglionProbe(list(w_raw)).surface(xs, ys)
        raw_row.append(Zr * sd + mu)
        w_sf, _ = reach.fit_target(name, ceiling=cap, scale_free=True, n_restart=10)
        Zs, _ = harness.GanglionProbe(list(w_sf)).surface(xs, ys)
        # the scale-free fit may use a negative coefficient (anti-correlated); re-align to the target
        # the same way it is scored, so the displayed SHAPE matches what the residual measured.
        A = np.column_stack([Zs.ravel(), np.ones(Zs.size)])
        coef, *_ = np.linalg.lstsq(A, Tn.ravel(), rcond=None)
        norm_row.append(coef[0] * Zs + coef[1])
    cols = ["target"] + [f"cap {c}" for c in VIZ_CAPS]
    plots.shape_under_caps(name, raw_row, norm_row, cols, xs, ys,
                           os.path.join(FIGDIR, f"3_{name}_under_caps.png"))


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    print("# rung-1 step-3 cap cost | fit the rung-0 trio under the cap | residual 0=perfect ~1=mean\n")
    raw = {s: [] for s in SHAPES}      # gain cost (amplitude must be reached)
    shape = {s: [] for s in SHAPES}    # shape cost (amplitude factored out)
    print("W_max:     " + "  ".join(f"{w:>5.2f}" for w in W_MAXES))
    for s in SHAPES:
        for w in W_MAXES:
            _, r_raw = reach.fit_target(s, ceiling=w, scale_free=False, n_restart=10)
            _, r_shape = reach.fit_target(s, ceiling=w, scale_free=True, n_restart=10)
            raw[s].append(r_raw)
            shape[s].append(r_shape)
        print(f"{s:>9} raw:   " + "  ".join(f"{v:>5.2f}" for v in raw[s]))
        print(f"{s:>9} shape: " + "  ".join(f"{v:>5.2f}" for v in shape[s]))

    base = [(RUNG0[s] - 0.005, RUNG0[s] + 0.005, "gray", None) for s in SHAPES]  # thin baseline marks
    plots.trend(W_MAXES, raw, "weight cap  W_max", "residual (raw — must reach amplitude)",
                "GAIN cost: under a tight cap the shapes can't reach their amplitude (-> residual ~1)",
                os.path.join(FIGDIR, "1_gain_cost.png"), logx=True,
                bands=[(0.95, 1.0, "red", "no better than mean")])
    plots.trend(W_MAXES, shape, "weight cap  W_max", "residual (scale-free — shape only)",
                "SHAPE cost: factor amplitude out and the carve survives near the rung-0 baseline",
                os.path.join(FIGDIR, "2_shape_cost.png"), logx=True,
                bands=base[:1])  # (single faint band just for scale reference)

    # the concrete version: the REAL shape the capped hardware makes (rung-0 style)
    xs = np.linspace(-1.0, 1.0, GRID_N)
    print()
    for name in VIZ_SHAPES:
        real_shape_panels(name, xs, xs)
        print(f"wrote real-shape panels for {name}")

    plots.make_gallery(FIGDIR, "Rung-1 · Step-3 what the cap costs (rung-0 trio)")
    print(f"\nwrote {2 + len(VIZ_SHAPES)} figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
