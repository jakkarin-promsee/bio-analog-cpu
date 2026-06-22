"""The assembled Phase-4 capability map (the deliverable): a 7-axis scorecard of where OURS wins/ties/loses vs a
tuned backprop ceiling. python plot_capability_map.py  ->  figs_summary/CAPABILITY_MAP.png"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(_HERE, "figs_summary"); os.makedirs(OUT, exist_ok=True)

WIN, TIE, NEG = "#1b8a3a", "#d9690a", "#b3261e"
# (axis, verdict label, color, the finding, the number)
ROWS = [
    ("A6  Continual", "WIN (decisive)", WIN, "the home: sleep recovers what online-BP forgets, robust across difficulty",
     "BWT -0.02..-0.18  vs  BP -0.83..-0.99"),
    ("A2  Ambient-dim", "WIN", WIN, "nuisance-robust; crosses ABOVE tuned BP in high-D; Mono collapses",
     "gap -0.029 @ dim500 (cheaper + better)"),
    ("A4  Width x depth", "WIN (cost)", WIN, "depth is ~free for OURS (flat backward) vs BP (linear); 80/20 is depth-gated",
     "OURS ~45k flat  vs  BP 52->124k"),
    ("A3  Depth x difficulty", "WIN (composes)", WIN, "depth-composition generalizes; out-composes BP in the hard regime",
     "w2 slope >0 all difficulties (w1 never)"),
    ("A1  Difficulty", "TRAIL", TIE, "gap doesn't open (capture is the read); cost of the gap",
     "capture 0.92 -> 0.68"),
    ("A5  Class count", "TRAIL", TIE, "difficulty-gated, not count-gated; real data far kinder than synthetic",
     "synth gap +0.23  but digits +0.03"),
    ("A7  Noise (eval-time)", "NEGATIVE", NEG, "NOT noise-robust (layernorm tradeoff); train-with-noise = the real test (untested)",
     "retention 0.75  vs  BP 0.88"),
]


def main():
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, len(ROWS)); ax.axis("off")
    ax.set_title("Phase 4 — the capability map:  the cheap forward-only brain vs a tuned backprop ceiling",
                 fontsize=13, fontweight="bold", pad=14)
    for i, (axis, verdict, col, finding, num) in enumerate(ROWS):
        y = len(ROWS) - 1 - i
        ax.add_patch(FancyBboxPatch((0.1, y + 0.12), 9.8, 0.76, boxstyle="round,pad=0.02",
                                    linewidth=0, facecolor=col, alpha=0.10))
        ax.add_patch(FancyBboxPatch((0.1, y + 0.12), 0.16, 0.76, boxstyle="square,pad=0", linewidth=0, facecolor=col))
        ax.text(0.45, y + 0.62, axis, fontsize=11, fontweight="bold", va="center")
        ax.text(0.45, y + 0.30, finding, fontsize=8.3, va="center", color="#333333")
        ax.text(6.7, y + 0.62, verdict, fontsize=10, fontweight="bold", va="center", color=col)
        ax.text(6.7, y + 0.30, num, fontsize=8.3, va="center", color="#333333", family="monospace")
    ax.text(0.1, -0.55, "WIN = where the substrate lives (continual, nuisance, depth-cheap).  "
            "TRAIL = static accuracy (the cost of the gap).  NEGATIVE = a caught over-optimistic assumption.",
            fontsize=8.5, style="italic", color="#555555")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "CAPABILITY_MAP.png"), dpi=140, bbox_inches="tight"); plt.close(fig)
    print(f"  [plot] CAPABILITY_MAP -> {OUT}")


if __name__ == "__main__":
    main()
