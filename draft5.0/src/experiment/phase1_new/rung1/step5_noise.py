"""Phase 1 (new) · Rung 1 · Step 5 — NOISE: where the two rules really part ways.

Inject the SAME analog jitter (gaussian noise on every stored weight, every update step) into both
learners and dial it up. The meaningful comparison is on the PLANE — the shape attribution actually
learns; on the folds attribution is flat with or without noise, so noise only bites gradient there.

Two figures:
  noise_sweep.png    : final shape residual vs noise sigma, attribution vs gradient (median + IQR).
  noise_surfaces.png : the PLANE's final surface as sigma rises (attribution top, gradient bottom).

Run:  python -m src.experiment.phase1_new.rung1.step5_noise
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import trainers as T, plots

EPOCHS = 150
SEEDS = T.STD_SEEDS[:3]
LEVELS = [0.0, 0.02, 0.05, 0.1, 0.2]
SWEEP_SHAPES = ["plane", "parabola", "valley"]   # plane/parabola: both learn (real noise A/B); valley: a fold
RENDER_N = 61
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step5")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    levels = np.array(LEVELS)

    # --- sweep: final residual vs noise -----------------------------------------------------------
    data, hlines = {}, {}
    print("# rung-1 step-5 noise sweep | final shape-resid vs sigma (median)\n")
    for name in SWEEP_SHAPES:
        a_by, g_by = [], []
        for sig in LEVELS:
            af, gf = [], []
            for s in SEEDS:
                r = T.run_pair(name, seed=s, epochs=EPOCHS, alpha=0.0, beta=0.0, noise_std=sig)
                af.append(r["attr"]["loss"][-1]); gf.append(r["grad"]["loss"][-1])
            a_by.append(af); g_by.append(gf)
        am, alo, ahi = (np.median(a_by, 1), np.percentile(a_by, 25, 1), np.percentile(a_by, 75, 1))
        gm, glo, ghi = (np.median(g_by, 1), np.percentile(g_by, 25, 1), np.percentile(g_by, 75, 1))
        data[name] = [("attribution", levels, am, alo, ahi), ("gradient", levels, gm, glo, ghi)]
        hlines[name] = ("TRF oracle", T.resid_w29(T.oracle_w29(name), name))
        print(f"{name:>11}: attr {am[0]:.2f}->{am[-1]:.2f}   grad {gm[0]:.2f}->{gm[-1]:.2f}  (sigma {LEVELS[0]}->{LEVELS[-1]})")
    plots.panels_with_bands(
        data, SWEEP_SHAPES, "weight-noise σ", "final shape residual",
        f"Rung-1 · Step-5 noise sweep (median + IQR, {len(SEEDS)} seeds)",
        os.path.join(FIGDIR, "noise_sweep.png"), ncol=3, ylim=(0.0, 1.3), hlines=hlines)

    # --- surfaces: the plane under rising noise ----------------------------------------------------
    xs = np.linspace(*T.DOMAIN, RENDER_N); ys = xs
    top, bot = [], []
    for sig in LEVELS:
        r = T.run_pair("plane", seed=42, epochs=EPOCHS, alpha=0.0, beta=0.0, noise_std=sig)
        top.append(T.display_norm(T.surface_w29(r["attr"]["final"], xs, ys)))
        bot.append(T.display_norm(T.surface_w29(r["grad"]["final"], xs, ys)))
    plots.film_strip("plane", top, bot, [f"σ={s:g}" for s in LEVELS], ("attribution", "gradient"),
                     xs, ys, os.path.join(FIGDIR, "noise_surfaces.png"),
                     suptitle="plane under rising weight-noise (final surface, shape)")
    plots.make_gallery(FIGDIR, "Rung-1 · Step-5 noise")
    print(f"\nwrote noise_sweep.png + noise_surfaces.png + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
