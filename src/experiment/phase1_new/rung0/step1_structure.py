"""Phase 1 (new) · Rung 0 · Step 1 — the STRUCTURE: a Ganglion is a quilt of planes.

The whole point of this step: SHOW (not score) what one 2-3-3-2 Ganglion is at the bottom of the
ladder. L2's three ReLU neurons each draw ONE line across the (x1, x2) plane — that is the
Ganglion's actual job (region segmentation); L3/L4 only amplify. So we drive ONE hand-designed
Ganglion (harness.canonical_inits — fixed, no seed luck) and draw it line-first, top to bottom:

  1. three lines — one panel per L2 neuron: the line it draws + the ramp it switches on. The mechanism.
  2. zones       — the three lines overlaid, plane shaded by how many ReLUs are ON (0..3). How they
                   stack into segmentation zones (readable few-level map, not a 7-color soup).
  3. slices      — a few horizontal cuts; each is a piecewise-LINE (straight y=ax+b segments joined
                   at kinks). The kinks sit exactly on the lines: output is flat-per-zone.
  4. surface     — the raw output over the input square (both channels), for reference.

Run:  python -m src.experiment.phase1_new.rung0.step1_structure      (from the repo root)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, metrics, plots

GRID_N = 241
DOMAIN = (-1.0, 1.0)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step1")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs

    probe = harness.GanglionProbe(harness.canonical_inits())
    Z0, Z1 = probe.surface(xs, ys)

    print(f"# rung-0 step-1 structure | canonical Ganglion | grid {GRID_N}x{GRID_N} on "
          f"[{DOMAIN[0]},{DOMAIN[1]}]^2\n")
    for ch, Z in (("out0", Z0), ("out1", Z1)):
        lo, hi = metrics.output_range(Z)
        curv = metrics.planar_residual(Z, xs, ys)
        k = metrics.region_count(Z, xs, ys)
        print(f"{ch}:  range=[{lo:+.3f}, {hi:+.3f}]  planar-residual={curv:.3f}  cells={k}")

    creases = harness.CANONICAL_CREASES

    # 1. the three L2 lines — one panel per neuron (the mechanism: 3 activations = 3 lines)
    plots.relu_neurons(creases, xs, ys, "L2's three ReLU neurons = three lines across (x1, x2)",
                       os.path.join(FIGDIR, "1_three_lines.png"))

    # 2. the lines overlaid + how many ReLUs fire where (segmentation zones, not a color soup)
    plots.activation_zones(creases, xs, ys, "Three lines segment the plane into zones",
                           os.path.join(FIGDIR, "2_zones.png"))

    # 3. slices of out0 at four heights — flat ramps joined at kinks (y = ax+b per segment)
    plots.slices(Z0, xs, ys, at_rows=[-0.6, -0.2, 0.2, 0.6],
                 title="out0 horizontal slices — each a piecewise-line (y = ax+b per segment)",
                 path=os.path.join(FIGDIR, "3_slices.png"))

    # 4. raw output surface (both channels) with the SAME 3 lines drawn on each:
    #    one segmentation, two voices (out0 and out1 read off the very same L2 cuts).
    plots.surface_heatmaps(Z0, Z1, xs, ys, "canonical", os.path.join(FIGDIR, "4_surface.png"),
                           creases=creases)

    plots.make_gallery(FIGDIR, "Rung-0 · Step-1 structure (canonical Ganglion)")
    print(f"\nwrote 4 figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
