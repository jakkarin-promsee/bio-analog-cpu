"""Phase 1 (new) · Rung 1 · Step 2 — LEARNING CURVES: does it converge, and how fast?

Shape residual vs epoch, attribution vs gradient, one panel per shape, multi-seed (median + IQR band
over the standard seed set). The rung-0 oracle floor is the dashed reference. Baseline = no momentum.

Run:  python -m src.experiment.phase1_new.rung1.step2_curves
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import trainers as T, plots

EPOCHS = 250
SEEDS = T.STD_SEEDS
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step2")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    ep = np.arange(EPOCHS + 1)
    data, hlines = {}, {}
    print("# rung-1 step-2 learning curves | median final shape-resid over seeds\n")
    for name in T.SHAPES:
        a_curves, g_curves = [], []
        for s in SEEDS:
            r = T.run_pair(name, seed=s, epochs=EPOCHS, alpha=0.0, beta=0.0)
            a_curves.append(r["attr"]["loss"])
            g_curves.append(r["grad"]["loss"])
        am, alo, ahi = T.median_iqr(a_curves)
        gm, glo, ghi = T.median_iqr(g_curves)
        data[name] = [("attribution", ep, am, alo, ahi), ("gradient", ep, gm, glo, ghi)]
        hlines[name] = ("TRF oracle", T.resid_w29(T.oracle_w29(name), name))
        print(f"{name:>11}: attr {am[-1]:.3f}   grad {gm[-1]:.3f}   oracle {hlines[name][1]:.3f}")
    plots.panels_with_bands(
        data, T.SHAPES, "epoch", "shape residual (0 = perfect)",
        "Rung-1 · Step-2 learning curves (median + IQR, 5 seeds)",
        os.path.join(FIGDIR, "curves.png"), ncol=3, ylim=(0.0, 1.15), hlines=hlines)
    plots.make_gallery(FIGDIR, "Rung-1 · Step-2 learning curves")
    print(f"\nwrote curves.png + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
