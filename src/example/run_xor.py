"""SLICE-1 experiment: can one Ganglion learn XOR under broadcast + momentum?

This is the §20.1 Minimum Viable Falsification. PASS = loss decreases monotonically and final loss
< 50% of initial. A failure here is DATA (it tests H1), not a code bug per se — though a sign/direction
error in the update is the most likely culprit, so be paranoid.

Run:  python -m src.example.run_xor       (from the project root)
"""

import sys
import os

# allow running both as a module and as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.example.brainstem import Brainstem
from src.example import column_group_xor

# XOR in +/-1 encoding. target = output[0].
SAMPLES = [
    ([0.13, 0.84], 0.107),
    ([0.72, 0.31], 0.100),
    ([0.47, 0.59], 0.140),
    ([0.91, 0.12], 0.106),
    ([0.25, 0.44], 0.058),
    ([0.68, 0.77], 0.212),
    ([0.35, 0.93], 0.174),
    ([0.82, 0.56], 0.196),
    ([0.17, 0.28], 0.019),
    ([0.54, 0.41], 0.097),
    ([0.96, 0.88], 0.370),
    ([0.39, 0.67], 0.126),
    ([0.74, 0.08], 0.071),
    ([0.21, 0.79], 0.107),
    ([0.61, 0.52], 0.144),
    ([0.05, 0.96], 0.106),
    ([0.87, 0.69], 0.265),
]


def run(epochs=1000, lr=0.05, seed=42, report_every=100):
    # The Brainstem's instruction stream: one child (the lone ColumnGroup), its boundary at chip
    # slots [0,1] in -> [2,3] out. Multi-lobe later = just add more child specs here.
    bs = Brainstem(
        [{"build": column_group_xor.build, "in_slot": 0, "out_slot": 2, "n_in": 2, "n_out": 2}],
        lr=lr, seed=seed,
    )

    history = []
    for epoch in range(epochs):
        total = 0.0
        for x, t in SAMPLES:
            loss, _ = bs.train_step(x, t)
            total += loss
        history.append(total)
        if epoch % report_every == 0 or epoch == epochs - 1:
            print(f"epoch {epoch:5d}   total_loss {total:.5f}")

    print("\nfinal predictions (target -> pred):")
    for x, t in SAMPLES:
        out = bs.forward(x)
        print(f"  {x} : target {t:+.4f} -> pred {out[0]:+.4f}")

    initial = sum(history[:5]) / 5.0
    final = sum(history[-5:]) / 5.0
    print(f"\ninitial loss ~{initial:.4f}   final loss ~{final:.4f}   "
          f"ratio {final / initial:.3f}   {'PASS' if final < 0.5 * initial else 'NO-PASS'}")
    return history


if __name__ == "__main__":
    run()
