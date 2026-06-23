"""Phase 1 (new) · Rung 1 · Step 3 — MOMENTUM: does the smoothing change either rule's character?

Re-run the curves with momentum ON vs OFF, for both rules. The two momentums are different mechanisms
(don't conflate): attribution = EMA of |a·W| contribution (alpha; arc's 0.75); gradient = classical
heavy-ball velocity (beta). NOT Adam (no v_t RMS term; §20.2 #6). We report "each rule, with vs without
its own momentum" — not a head-to-head of the same knob.

Run:  python -m src.experiment.phase1_new.rung1.step3_momentum
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import trainers as T, plots

EPOCHS = 150
SEEDS = T.STD_SEEDS[:3]
MOM = 0.75              # alpha for attribution, beta for gradient (same number, different mechanism)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step3")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    ep = np.arange(EPOCHS + 1)
    data = {}
    print("# rung-1 step-3 momentum | final shape-resid: rule (no-mom -> mom)\n")
    for name in T.SHAPES:
        curves = {k: [] for k in ("a0", "a1", "g0", "g1")}
        for s in SEEDS:
            off = T.run_pair(name, seed=s, epochs=EPOCHS, alpha=0.0, beta=0.0)
            on = T.run_pair(name, seed=s, epochs=EPOCHS, alpha=MOM, beta=MOM)
            curves["a0"].append(off["attr"]["loss"]); curves["g0"].append(off["grad"]["loss"])
            curves["a1"].append(on["attr"]["loss"]);  curves["g1"].append(on["grad"]["loss"])
        med = {k: T.median_iqr(v)[0] for k, v in curves.items()}
        data[name] = [
            ("attr no-mom", ep, med["a0"], None, None),
            (f"attr α={MOM}", ep, med["a1"], None, None),
            ("grad no-mom", ep, med["g0"], None, None),
            (f"grad β={MOM}", ep, med["g1"], None, None),
        ]
        print(f"{name:>11}: attr {med['a0'][-1]:.3f}->{med['a1'][-1]:.3f}   "
              f"grad {med['g0'][-1]:.3f}->{med['g1'][-1]:.3f}")
    plots.panels_with_bands(
        data, T.SHAPES, "epoch", "shape residual (0 = perfect)",
        f"Rung-1 · Step-3 momentum on/off (median, {len(SEEDS)} seeds)",
        os.path.join(FIGDIR, "momentum_onoff.png"), ncol=3, ylim=(0.0, 1.15))
    plots.make_gallery(FIGDIR, "Rung-1 · Step-3 momentum")
    print(f"\nwrote momentum_onoff.png + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
