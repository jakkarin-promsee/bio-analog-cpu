"""Phase 1 (new) shared harness — build and drive the REAL single-Ganglion forward.

Everything here characterizes the Ganglion *as built*: every surface comes from the actual
GanglionALU forward (Brainstem -> ControlUnit -> GanglionALU), never a numpy re-implementation.
This is the reusable probe; the per-step scripts (rung0/step*.py) import it.

Two ways to make a Ganglion to look at:
  - `canonical_inits()`  : ONE hand-designed weight set. The three L2 creases are placed inside the
                           input square on purpose, so the region structure is the same every time
                           (no seed luck). This is how we EXPOSE the mechanism.
  - `random_inits(seed)` : a freshly-initialized random Ganglion (small uniform weights), used only
                           to show that init decides whether that structure wakes up.

Rung-0 (ideal) uses the library UNCHANGED. Later rungs reuse `config`: `ceiling` (rung-1) clamps the
stored weights, `saturation` (rung-2) will soft-map them; `activation`/`residual` (Axes 2-3) touch
alu.py and stay reserved (NotImplementedError) until that simulator-code task.
"""

import os
import sys
import random

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.library import (
    AnalogWire, DigitalWire, SignalWire, LocalCapacitor, PWM,
    Ganglion, GanglionALU, Instr, ControlUnit,
)
from src.example.brainstem import Brainstem

N_SCAPS = 29
STD_SEEDS = [42, 137, 271, 314, 1729]   # the §20.2 standard seed set


def random_inits(seed, lo=-0.5, hi=0.5, n=N_SCAPS):
    """One random Ganglion: 29 small uniform inits (matches example/column_group_xor)."""
    rng = random.Random(seed)
    return [rng.uniform(lo, hi) for _ in range(n)]


# --- the canonical Ganglion -------------------------------------------------------------------
# Hand-placed so the three L2 ReLU lines (the "creases") all cut through [-1,1]^2 in general
# position -> the full 7-region carve, identical every run. L3 is the identity (a3 = a2) so the
# structure you see is exactly the three L2 cuts; L4 reads them out as two different planes.
#
# crease 0:  x1 + 0.30 = 0   -> vertical   at x1 = -0.30
# crease 1:  x2 + 0.30 = 0   -> horizontal at x2 = -0.30
# crease 2:  x1 + x2 - 0.50 = 0 -> diagonal at x1 + x2 = 0.50
CANONICAL_CREASES = [(1.0, 0.0, 0.30), (0.0, 1.0, 0.30), (1.0, 1.0, -0.50)]  # (a, b, c): a*x1+b*x2+c=0


def canonical_inits():
    """The one hand-designed weight set (canonical §7.4 order). See CANONICAL_CREASES."""
    w = [0.0] * N_SCAPS
    # L2 weights (0..5) + bias (6..8): the three creases above
    w[0], w[1], w[6] = 1.0, 0.0, 0.30      # a2[0] = ReLU( x1        + 0.30 )
    w[2], w[3], w[7] = 0.0, 1.0, 0.30      # a2[1] = ReLU(       x2  + 0.30 )
    w[4], w[5], w[8] = 1.0, 1.0, -0.50     # a2[2] = ReLU( x1 +  x2  - 0.50 )
    # L3 weights (9..17) = identity 3x3, bias (18..20) = 0   -> a3 = a2
    w[9], w[13], w[17] = 1.0, 1.0, 1.0
    # L4 out0 weights (21..23) + bias (27): one readout plane per region
    w[21], w[22], w[23], w[27] = 1.0, -1.2, 0.8, 0.0
    # L4 out1 weights (24..26) + bias (28): a DIFFERENT readout (so the two channels differ)
    w[24], w[25], w[26], w[28] = -0.7, 1.0, 0.5, 0.0
    return w


def _make_build(inits, alpha=None, _out=None):
    """A single-Ganglion ColumnGroup build that takes EXPLICIT inits (mirrors
    example/column_group_xor.build, which only takes a seed).

    `alpha` overrides the Scap momentum EMA factor (rung-1 Step-3 momentum toggle; None = arc default
    0.75). `_out`, if a dict, receives the built Ganglion under "ganglion" — so a trainer can reach the
    Scaps (e.g. to inject training-time weight noise, rung-1 Step-5)."""
    def build(parent_weight, parent_sign, in_start, out_start,
              run, done, reset, update_signal, feedback, seed=0):
        weight_bus   = AnalogWire("cg.weight", 80)
        sign_bus     = DigitalWire("cg.sign", 80)
        target_group = DigitalWire("cg.target_group", 1)
        get_weight   = SignalWire("cg.get_weight")
        set_momentum = SignalWire("cg.set_momentum")
        local_update = SignalWire("cg.local_update")

        local_weight = AnalogWire("cg.local.weight", 20)
        local_sign   = DigitalWire("cg.local.sign", 20)
        set_bus_id   = DigitalWire("cg.set_bus_id", 1)
        load_id_sig  = [SignalWire(f"cg.load_id_{i}") for i in range(4)]
        caps = [LocalCapacitor(f"cg.cap{i}", set_bus_id, local_weight, local_sign, load_id_sig[i])
                for i in range(4)]

        common = (weight_bus, sign_bus, target_group, feedback, get_weight, set_momentum, local_update)
        gang = Ganglion(1, *common, inits=list(inits), alpha=alpha)   # Scaps self-register; group id 1
        if _out is not None:
            _out["ganglion"] = gang

        g_alu = GanglionALU("cg.g_alu", weight_bus, sign_bus, local_weight, local_sign)
        program = [Instr([0, 1], [2, 3], "g_alu", 1)]
        pwm = PWM("cg.pwm", scope_lr=1.0)
        return ControlUnit("cg", program, {"g_alu": g_alu}, caps, set_bus_id, load_id_sig,
                           [0, 1], [2, 3], parent_weight, parent_sign, in_start, out_start,
                           target_group, get_weight, set_momentum, local_update, feedback, pwm,
                           run, done, reset, update_signal)
    return build


# Physical supply rail (= scap.W_RAIL): the hard ceiling on a stored cap, ~0-3V. Rung-1 sweeps the
# *usable* cap W_max at or below this; the analog MUL scale k then sets where unity gain sits.
W_RAIL = 3.0

# Config keys reserved for later rungs/axes. Rung-0 uses defaults = current library behavior.
DEFAULT_CONFIG = {
    "ceiling": None,          # Axis-1 rung 1: forward-clamp |w|,|b| to this usable cap; None = off
    "gain": 1.0,              # Axis-1 rung 1: the analog MUL scale k (the "decimal shift") — multiplies
                              #   every effective weight, i.e. a per-multiply k across the L2->L3->L4
                              #   cascade. Stays in the harness as the ALU's translate-rule stand-in
                              #   (no alu.py change): clamp-then-scale == per-multiply k (ReLU/bias incl).
    "noise_std": 0.0,         # Axis-1 rung 1 step-4: gaussian noise on the stored (capped) weight (a
                              #   first peek at analog reality; full PVT is Phase 8 / §20.14).
    "noise_seed": 0,
    "saturation": None,       # Axis-1 rung 2: forward soft 1-e^- map to this rail; None = off
    "activation": "current",  # Axis-2: 'current' = ReLU@L2 / linear@L3 (library as-is)
    "residual": False,        # §7.7 L1->L4 bypass
}


class GanglionProbe:
    """One 2-3-3-2 Ganglion you can sweep.

    forward(x1, x2) -> [out0, out1];  surface(xs, ys) -> (Z0, Z1) over the grid.
    Repeated forwards are pure w.r.t. weights (no train_step is called), so a sweep is clean.
    """

    def __init__(self, inits, config=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        inits = list(inits)
        ceil = self.config["ceiling"]
        if ceil is not None:                          # rung-1: cap the stored weight magnitude
            inits = [max(-ceil, min(ceil, w)) for w in inits]
        ns = self.config["noise_std"]
        if ns:                                        # noise on the physical cap, then re-seat in rail
            rng = random.Random(self.config["noise_seed"])
            inits = [w + rng.gauss(0.0, ns) for w in inits]
            if ceil is not None:
                inits = [max(-ceil, min(ceil, w)) for w in inits]
        g = self.config["gain"]
        if g != 1.0:                                  # the MUL scale k: clamp-then-scale == per-multiply k
            inits = [g * w for w in inits]
        self.inits = inits
        for k in ("saturation", "residual"):
            if self.config[k]:
                raise NotImplementedError(
                    f"config '{k}' is a later-rung toggle (rung-2 / Axis-3); not implemented yet")
        if self.config["activation"] != "current":
            raise NotImplementedError(
                "the activation switch is Axis-2 (simulator-code task); rungs 0-1 use the library default")
        self.bs = Brainstem(
            [{"build": _make_build(self.inits), "in_slot": 0, "out_slot": 2, "n_in": 2, "n_out": 2}],
            lr=0.0, seed=0,
        )

    def forward(self, x1, x2):
        return self.bs.forward([float(x1), float(x2)])

    def surface(self, xs, ys):
        Z0 = np.empty((len(ys), len(xs)))
        Z1 = np.empty((len(ys), len(xs)))
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                o = self.forward(x, y)
                Z0[j, i] = o[0]
                Z1[j, i] = o[1]
        return Z0, Z1
