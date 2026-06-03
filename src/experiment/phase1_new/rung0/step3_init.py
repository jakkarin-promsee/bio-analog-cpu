"""Phase 1 (new) · Rung 0 · Step 3 — does the carve wake up? (init sensitivity — the footnote).

Steps 1-2 used ONE hand-placed Ganglion so the structure was always visible. But a real chip starts
from RANDOM small weights. This step asks: with random init, does the carve from step-1 actually
appear? We draw a few random Ganglions and show each one's region map in the SAME way as step-1.

The finding (the honest caveat for Phase 2): the carve is *born*, but small uniform init decides
whether it engages in-domain — some draws carve several regions, some collapse to a single plane
(all three L2 lines sit in their always-on side over [-1,1]^2). That gap — random prior vs the
hand-placed structure — is exactly what learning (H1) has to cross.

Run:  python -m src.experiment.phase1_new.rung0.step3_init
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, metrics, plots

GRID_N = 161
DOMAIN = (-1.0, 1.0)
SEEDS = [42, 314, 271]      # 42/314 carve; 271 is the degenerate planar draw
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step3")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    print(f"# rung-0 step-3 init sensitivity | random Ganglions | grid {GRID_N}x{GRID_N}\n")
    panels = []
    for seed in SEEDS:
        probe = harness.GanglionProbe(harness.random_inits(seed))
        Z0, _ = probe.surface(xs, ys)
        lo, hi = metrics.output_range(Z0)
        labels, k = metrics.region_labels(Z0, xs, ys)
        word = "plane (asleep)" if k <= 1 else f"{k} regions"
        panels.append((labels, k, f"seed{seed}: {word}"))
        print(f"seed{seed:>5} out0:  range=[{lo:+.3f}, {hi:+.3f}]  regions={k}")
    plots.region_map_row(panels, xs, ys,
                         "out0 carve under random init — same atom, different luck",
                         os.path.join(FIGDIR, "init_region_maps.png"))
    plots.make_gallery(FIGDIR, "Rung-0 · Step-3 init sensitivity")
    print(f"\nwrote 1 figure + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
