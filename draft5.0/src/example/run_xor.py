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
import random

SAMPLES = []

for i in range(0, 50, 1):
    ii = i/50
    x1 = ii + round(random.uniform(-1, 1)*0, 2)
    x2 = ii + round(random.uniform(-1, 1)*0, 2)

    if x1 >= 25:
        y = round(x1 * 3 + 1 * x2, 3)
    else:
        y = round(x1 * 1 + 2 * x2, 3)

    SAMPLES.append(([x1, x2], y))


def run(epochs=1000, lr=0.001, seed=42, report_every=100):
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
