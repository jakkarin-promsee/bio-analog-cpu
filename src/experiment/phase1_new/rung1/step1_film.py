"""Phase 1 (new) · Rung 1 · Step 1 — THE FILM: watch each rule form the surface (heatmap + 3-D).

For every shape we train BOTH learners from the SAME init and snapshot the output surface at a few
epochs. Each film: target | TRF expected (rung-0 oracle) | surface at epoch 0 -> end, shown as BOTH a
heatmap AND a 3-D surface, for attribution (our lib) and gradient (numpy). Panels are display-normalized
(shape; a flat/asleep frame is uniform / a flat plane in 3-D).

We render it twice — NO momentum and WITH momentum (alpha=beta=0.75) — so the surface shows what
momentum does to each rule (it lets attribution scratch the simplest fold; it makes gradient overshoot).

Run:  python -m src.experiment.phase1_new.rung1.step1_film
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import trainers as T, plots

SEED = 42
EPOCHS = 250
SNAP = (0, 25, 250)
RENDER_N = 41
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step1")
# tag is ASCII (the Thai console is cp874); figures render the prettier unicode in `ftag`.
SETTINGS = [("", 0.0, 0.0, "no momentum", "no momentum"),
            ("_mom", 0.75, 0.75, "momentum a=b=0.75", "momentum α=β=0.75")]


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(*T.DOMAIN, RENDER_N)
    ys = xs
    X1, X2 = np.meshgrid(xs, ys)
    col_labels = ["target", "TRF expected"] + [f"epoch {e}" for e in SNAP]
    for suffix, alpha, beta, tag, ftag in SETTINGS:
        print(f"# rung-1 step-1 film [{tag}] | attribution (lib) vs gradient (numpy)\n")
        for name in T.SHAPES:
            r = T.run_pair(name, seed=SEED, epochs=EPOCHS, snap_epochs=SNAP, alpha=alpha, beta=beta)
            target = T.display_norm(T._target(name, X1, X2))
            oracle = T.display_norm(T.surface_w29(T.oracle_w29(name), xs, ys))
            top = [target, oracle] + [T.display_norm(T.surface_w29(r["attr"]["snaps"][e], xs, ys)) for e in SNAP]
            bot = [target, oracle] + [T.display_norm(T.surface_w29(r["grad"]["snaps"][e], xs, ys)) for e in SNAP]
            path = os.path.join(FIGDIR, f"film{suffix}_{name}.png")
            af, gf = r["attr"]["loss"][-1], r["grad"]["loss"][-1]
            plots.film_strip_hd(name, top, bot, col_labels, ("attribution", "gradient"), xs, ys, path,
                                suptitle=f"{name} · {ftag}: forming the surface  (final resid — attr {af:.2f} | grad {gf:.2f})")
            print(f"{name:>11}: attr {r['attr']['loss'][0]:.2f}->{af:.2f}   grad {r['grad']['loss'][0]:.2f}->{gf:.2f}   -> {os.path.basename(path)}")
        print()
    plots.make_gallery(FIGDIR, "Rung-1 · Step-1 film (heatmap + 3-D; no-mom and momentum)")
    print(f"wrote {2 * len(T.SHAPES)} films + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
