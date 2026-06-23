"""Phase 1 (new) · Rung 1 · Step 4 — THE GAP: where each learner lands vs the oracle ceiling.

Final shape residual per shape, three bars: TRF oracle (rung-0 ceiling) | gradient | attribution.
Median over the standard seed set. The gap above the oracle bar = the LEARNING cost (separated from the
capacity limit rung 0 measured). Baseline = no momentum.

Run:  python -m src.experiment.phase1_new.rung1.step4_gap
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import trainers as T, plots

EPOCHS = 250
SEEDS = T.STD_SEEDS
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step4")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    groups = {}
    print("# rung-1 step-4 gap to oracle | final shape-resid (median)\n")
    for name in T.SHAPES:
        a_fin, g_fin = [], []
        for s in SEEDS:
            r = T.run_pair(name, seed=s, epochs=EPOCHS, alpha=0.0, beta=0.0)
            a_fin.append(r["attr"]["loss"][-1])
            g_fin.append(r["grad"]["loss"][-1])
        orc = T.resid_w29(T.oracle_w29(name), name)
        groups[name] = [orc, float(np.median(g_fin)), float(np.median(a_fin))]
        print(f"{name:>11}: oracle {orc:.3f}   gradient {groups[name][1]:.3f}   attribution {groups[name][2]:.3f}")
    plots.grouped_bars(
        groups, ["TRF oracle", "gradient", "attribution"], {},
        "final shape residual (lower = better)",
        "Rung-1 · Step-4 gap to oracle (median, 5 seeds)",
        os.path.join(FIGDIR, "gap_to_oracle.png"))
    plots.make_gallery(FIGDIR, "Rung-1 · Step-4 gap to oracle")
    print(f"\nwrote gap_to_oracle.png + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
