"""Phase 1 · Axis 1 · Experiment 3 — Rung-1: what the ceiling does to a Ganglion.

The weight ceiling is the physical-saturation rail (§6.6 / H10) — a **per-weight clip**: it only touches
weights whose magnitude exceeds W_max. We SHOW its effect directly: take the *same* Ganglion at low gain
(U±0.5) and high gain (U±2.0 = the same pattern ×4), and plot the output surface as the cap tightens —
RAW (the amplitude crush) and NORMALIZED (whether the shape survives). The point: the cap is a SELECTIVE
compressor — it crushes high-gain (long-range) configs and barely touches low-gain (short-range) ones, i.e.
the anti-winner-take-all role, made visible — not a residual number.

Run:  python -m src.experiment.phase1.axis1_weightcap.exp3_rung1_ceiling_effect    (from the repo root)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1 import harness, plots

GRID_N = 121
DOMAIN = (-1.0, 1.0)
W_MAX = [None, 0.4, 0.2, 0.1]
GANGLIA = [("low-gain (U+-0.5)", 0.5), ("high-gain (U+-2.0)", 2.0)]   # same seed/pattern, x4 gain
SEED = 42
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "exp3")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    print("# rung-1: what the ceiling does | per Ganglion: clipped/29 weights + out0 range-width vs W_max\n")
    for label, scale in GANGLIA:
        inits = harness.random_inits(SEED, lo=-scale, hi=scale)
        surfaces, sublabels = [], []
        print(f"{label} Ganglion:")
        for wm in W_MAX:
            clipped = sum(1 for w in inits if wm is not None and abs(w) > wm)
            Z0, _ = harness.GanglionProbe(inits, config={"ceiling": wm}).surface(xs, ys)
            width = float(Z0.max() - Z0.min())
            surfaces.append(Z0)
            tag = "no cap" if wm is None else f"W_max={wm}"
            sublabels.append(f"{tag}\nclip {clipped}/29 · width {width:.3f}")
            print(f"  {tag:>9}: clipped {clipped:2d}/29   out0 range-width {width:.4f}")
        slug = "low_gain" if scale < 1 else "high_gain"
        plots.ceiling_grid(surfaces, sublabels, xs, ys,
                           f"ceiling effect — {label} Ganglion (top: amplitude · bottom: shape)",
                           os.path.join(FIGDIR, f"{slug}.png"))
        print()
    plots.make_gallery(FIGDIR, "Axis-1 rung-1 — what the ceiling does (exp-3)")
    print(f"wrote per-Ganglion ceiling-effect figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
