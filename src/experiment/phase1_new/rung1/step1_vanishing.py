"""Phase 1 (new) · Rung 1 · Step 1 — the VANISHING WALL (the cascade-gain collapse).

A Ganglion multiplies its signal through three layers (L2 -> L3 -> L4). Multiply shrinks below 1:
0.2 * 0.2 = 0.04, not 0.4. So if the weight cap forces every weight small, the output collapses
roughly as (weight)^3 with depth -- the three layers vanish the signal. This step measures exactly
that: sweep the usable cap W_max (k = 1, the plain MUL) and watch the output amplitude (gain) fall
off a cliff. We also draw the surface + its three lines at a few caps, so you see the lines slide
AND the surface go flat at the same time.

Run:  python -m src.experiment.phase1_new.rung1.step1_vanishing
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import numpy as np

from src.experiment.phase1_new import harness, metrics, plots

GRID_N = 161
DOMAIN = (-1.0, 1.0)
W_MAXES = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
FIGDIR = os.path.join(os.path.dirname(__file__), "figures", "step1")


def capped_lines(inits, w_max):
    """The three L2 lines (a, b, c) after clamping the canonical weights to +/-w_max."""
    c = [max(-w_max, min(w_max, w)) for w in inits]
    return [(c[0], c[1], c[6]), (c[2], c[3], c[7]), (c[4], c[5], c[8])]


def gain_of(inits, w_max, xs, ys):
    """Output peak-to-peak (the cascade gain proxy) of one Ganglion under cap w_max, k = 1."""
    probe = harness.GanglionProbe(inits, config={"ceiling": w_max})
    Z0, _ = probe.surface(xs, ys)
    lo, hi = metrics.output_range(Z0)
    return hi - lo, Z0


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    xs = np.linspace(DOMAIN[0], DOMAIN[1], GRID_N)
    ys = xs
    refs = {"canonical": harness.canonical_inits(),
            "random seed42": harness.random_inits(42),
            "random seed137": harness.random_inits(137)}

    print(f"# rung-1 step-1 vanishing wall | gain = out0 peak-to-peak | k=1 | grid {GRID_N}\n")
    print("W_max:   " + "  ".join(f"{w:>5.2f}" for w in W_MAXES))
    series = {}
    for name, inits in refs.items():
        gains = [gain_of(inits, w, xs, ys)[0] for w in W_MAXES]
        series[name] = gains
        print(f"{name:>14}: " + "  ".join(f"{g:>5.2f}" for g in gains))

    # the knee: where the canonical gain falls through the bottom of the healthy band (0.5)
    cg = series["canonical"]
    knee = next((W_MAXES[i] for i in range(len(W_MAXES)) if cg[i] >= 0.5), W_MAXES[-1])

    plots.trend(W_MAXES, series, "weight cap  W_max", "cascade gain (out0 peak-to-peak)",
                "Vanishing wall: gain collapses as the cap tightens (k = 1)",
                os.path.join(FIGDIR, "1_gain_curve.png"), logx=True, logy=True,
                bands=[(0.5, 3.0, "green", "healthy band")], vlines=[(knee, f"knee~{knee}")])

    # surface + capped lines at loose / knee / tight
    caps = [1.5, 0.5, 0.15]
    canon = refs["canonical"]
    surfaces, lines_list, sublabels = [], [], []
    for w in caps:
        ptp, Z0 = gain_of(canon, w, xs, ys)
        surfaces.append(Z0)
        lines_list.append(capped_lines(canon, w))
        sublabels.append(f"cap = {w}   (gain {ptp:.2f})")
    plots.cap_panels(surfaces, lines_list, sublabels, xs, ys,
                     "Same Ganglion, tightening cap: lines slide + surface flattens",
                     os.path.join(FIGDIR, "2_cap_panels.png"))

    # why do different random seeds land at different gain? NOT weight size -- the sizes barely differ;
    # it's sign-alignment + ReLU gating luck through the cascade (constructive vs destructive).
    def layer_means(inits):
        w = np.array(inits)
        return [float(np.mean(np.abs(w[a:b]))) for a, b in ((0, 9), (9, 21), (21, 29))]
    groups, annot = {}, {}
    print()
    for name in refs:
        groups[name] = layer_means(refs[name])
        annot[name] = f"gain {series[name][-1]:.2f}"
        print(f"{name:>14}: layer mean|w| = "
              + ", ".join(f"{v:.2f}" for v in groups[name]) + f"   -> {annot[name]}")
    plots.grouped_bars(groups, ["L2", "L3", "L4"], annot, "mean |weight| per layer",
                       "Same weight size, very different gain: it's alignment, not size",
                       os.path.join(FIGDIR, "3_why_seeds.png"))

    plots.make_gallery(FIGDIR, "Rung-1 · Step-1 vanishing wall")
    print(f"\nknee (gain drops below 0.5) near W_max = {knee}")
    print(f"wrote 3 figures + gallery.md to {os.path.relpath(FIGDIR)}")


if __name__ == "__main__":
    main()
