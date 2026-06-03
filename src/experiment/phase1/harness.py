"""Phase 1 shared harness — build and drive the REAL single-Ganglion forward.

Characterize the Ganglion *as built*: every surface comes from the actual GanglionALU
forward (Brainstem -> ControlUnit -> GanglionALU), never a numpy re-implementation. This
module is the reusable probe; per-experiment scripts (exp{N}_*.py) import it.

Rung-0 (ideal) uses the library UNCHANGED. The **Axis-1 weight limits are applied here** in the
harness as a static stored-weight transform — for a static read (we don't train), a capped stored
weight is identical to a forward clamp — so NO frozen-kit change is needed: `ceiling` (rung-1)
clamps the weights, `saturation` (rung-2) will soft-map them. `activation` / `residual` (Axes 2-3)
DO touch alu.py and stay reserved (NotImplementedError) until that simulator-code task.
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
    """One weight-ensemble member: 29 small uniform inits (matches example/column_group_xor)."""
    rng = random.Random(seed)
    return [rng.uniform(lo, hi) for _ in range(n)]


def _make_build(inits):
    """A single-Ganglion ColumnGroup build that takes EXPLICIT inits (mirrors
    example/column_group_xor.build, which only takes a seed)."""
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
        Ganglion(1, *common, inits=list(inits))     # Scaps self-register; group id 1

        g_alu = GanglionALU("cg.g_alu", weight_bus, sign_bus, local_weight, local_sign)
        program = [Instr([0, 1], [2, 3], "g_alu", 1)]
        pwm = PWM("cg.pwm", scope_lr=1.0)
        return ControlUnit("cg", program, {"g_alu": g_alu}, caps, set_bus_id, load_id_sig,
                           [0, 1], [2, 3], parent_weight, parent_sign, in_start, out_start,
                           target_group, get_weight, set_momentum, local_update, feedback, pwm,
                           run, done, reset, update_signal)
    return build


# Config keys reserved for later rungs/axes. Rung-0 uses defaults = current library behavior.
DEFAULT_CONFIG = {
    "ceiling": None,         # Axis-1 rung 1: forward-clamp |w|,|b| to this; None = off
    "saturation": None,      # Axis-1 rung 2: forward soft 1-e^- map to this rail; None = off
    "activation": "current",  # Axis-2: 'current' = ReLU@L2 / linear@L3 (library as-is)
    "residual": False,       # §7.7 L1->L4 bypass
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
        if ceil is not None:                          # rung-1: cap the stored weight magnitude (|w|,|b| <= ceil)
            inits = [max(-ceil, min(ceil, w)) for w in inits]
        self.inits = inits
        for k in ("saturation", "residual"):
            if self.config[k]:
                raise NotImplementedError(
                    f"config '{k}' is a later-rung toggle (rung-2 / Axis-3); not implemented yet")
        if self.config["activation"] != "current":
            raise NotImplementedError(
                "the activation switch is Axis-2 (simulator-code task); rungs 0–1 use the library default")
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
