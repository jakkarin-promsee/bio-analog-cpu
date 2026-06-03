"""Phase 1 (new) · Rung 1 · Step 2 — the WINDOW (the MUL scale k rescues the cascade).

Step 1 showed a small cap vanishes the signal. The fix is the analog multiplier's built-in scale k
(the "decimal shift": store 0.2, multiply by 10 -> 0.4). k slides where unity gain sits: gain grows
like (k·W_max)^3, so cranking k pulls a vanished Ganglion back up... until it overshoots and slams the
rail (saturates). There is a WINDOW. We sweep both knobs on the canonical Ganglion and map the gain,
marking vanish / healthy / saturate. On log-log axes the healthy band is a straight diagonal
(k·W_max = const) — the cascade law, seen directly.

Run:  python -m src.experiment.phase1_new.rung1.step2_window
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, metrics, plots

GRID_N = 81
DOMAIN = (-1.0, 1.0)
W_MAXES = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
KS = [1, 2, 3, 5, 10, 20, 50]
HEALTHY = (0.5, 3.0)
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step2")


def gain(inits, w_max, k, xs, ys):
    probe = harness.GanglionProbe(inits, config={"ceiling": w_max, "gain": k})
    Z0, _ = probe.surface(xs, ys)
    lo, hi = metrics.output_range(Z0)
    return hi - lo


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    canon = harness.canonical_inits()

    print(f"# rung-1 step-2 window | canonical gain over (W_max, k) | healthy {HEALTHY} | grid {GRID_N}\n")
    G = np.empty((len(KS), len(W_MAXES)))
    for ik, k in enumerate(KS):
        for iw, w in enumerate(W_MAXES):
            G[ik, iw] = gain(canon, w, k, xs, ys)
    # print the grid
    print("k \\ W_max  " + "  ".join(f"{w:>5.2f}" for w in W_MAXES))
    for ik, k in enumerate(KS):
        print(f"k={k:>4}    " + "  ".join(f"{G[ik, iw]:>5.2f}" for iw in range(len(W_MAXES))))

    plots.gain_zone_map(W_MAXES, KS, G, "weight cap  W_max",
                        "The window: gain over (W_max, k); healthy band = cyan contours",
                        os.path.join(FIGDIR, "1_window.png"), healthy=HEALTHY)

    # the rescue, as a line story: a vanished cap (0.2) climbs back into the band as k rises
    iw = W_MAXES.index(0.2)
    series = {f"W_max = {W_MAXES[iw]} (vanished at k=1)": [G[ik, iw] for ik in range(len(KS))]}
    plots.trend(KS, series, "MUL scale  k", "cascade gain (out0 peak-to-peak)",
                "Rescue: cranking k lifts a vanished cap back through healthy -> into saturation",
                os.path.join(FIGDIR, "2_rescue.png"), logx=True, logy=True,
                bands=[(HEALTHY[0], HEALTHY[1], "green", "healthy band")])

    plots.make_gallery(FIGDIR, "Rung-1 · Step-2 window")
    print(f"\nwrote 2 figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
