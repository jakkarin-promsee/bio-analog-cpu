"""Phase 1 · Axis 1 · Experiment 1 — Rung-0a: the small-init prior (y = aW + b, no limits).

Sweep one 2-3-3-2 Ganglion's 2-D input over a grid for a seeded *random* weight ensemble; plot
each output surface + read the core metric fingerprint (range, curvature, region count). This is
the PRIOR — what a freshly-initialized Ganglion makes (inductive bias), NOT its limit; the
representational limit (best-fit to targets) is exp-2 (rung-0b reachability). Rung-0 ideal == the
library forward as-is (alu.py: ReLU@L2, linear@L3, no limits), so NO frozen-kit change is needed.

Run:  python -m src.experiment.phase1.axis1_weightcap.exp1_rung0_ideal      (from the repo root)
"""

import os
import sys

# this script is 4 levels below the repo root: src/experiment/phase1/axis1_weightcap/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1 import harness, metrics, plots

GRID_N = 121
DOMAIN = (-1.0, 1.0)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "exp1")


def run_one(label, inits, xs, ys, rows):
    probe = harness.GanglionProbe(inits)
    Z0, Z1 = probe.surface(xs, ys)
    plots.surface_heatmaps(Z0, Z1, xs, ys, f"rung0 · {label}", os.path.join(FIGDIR, f"{label}.png"))
    for ch, Z in (("out0", Z0), ("out1", Z1)):
        lo, hi = metrics.output_range(Z)
        curv = metrics.planar_residual(Z, xs, ys)
        reg = metrics.region_count(Z, xs, ys)
        rows.append((label, ch, lo, hi, curv, reg))
        print(f"{label:>10} {ch}:  range=[{lo:+.4f}, {hi:+.4f}]  curvature={curv:.4f}  regions={reg}")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    rows = []
    print(f"# rung-0 ideal | grid {GRID_N}x{GRID_N} on [{DOMAIN[0]},{DOMAIN[1]}]^2 "
          f"| ReLU@L2, linear@L3, no limits\n")
    for seed in harness.STD_SEEDS:
        run_one(f"seed{seed}", harness.random_inits(seed), xs, ys, rows)
    # one hand-set degenerate extreme: all-zero weights -> flat-zero output (the sanity floor)
    run_one("zeros", [0.0] * harness.N_SCAPS, xs, ys, rows)
    plots.make_gallery(FIGDIR, "Axis-1 rung-0a (prior) — exp-1")
    print(f"\nwrote {len(rows) // 2} surface figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
