"""SLICE-1 ColumnGroup: one Ganglion (2-3-3-2), the minimum to test H1 on XOR.

Cap pool (4 caps, all on the local bus):
    caps 0,1 = boundary IN   (bridged from the parent/chip bus by the ControlUnit)
    caps 2,3 = boundary OUT
Program: read [0,1] -> Ganglion group 1 -> write [2,3].

`build(...)` is called by the Brainstem with the chip-level bus + the boundary/handshake signals.
"""

import random

from ..library import (
    AnalogWire, DigitalWire, SignalWire, LocalCapacitor, PWM,
    Ganglion, GanglionALU, Instr, ControlUnit,
)


def build(parent_weight, parent_sign, in_start, out_start,
          run, done, reset, update_signal, feedback, seed=42):
    rng = random.Random(seed)

    # --- main bus (Scap weights) + scope op signals ---
    weight_bus   = AnalogWire("cg.weight", 80)
    sign_bus     = DigitalWire("cg.sign", 80)
    target_group = DigitalWire("cg.target_group", 1)
    get_weight   = SignalWire("cg.get_weight")
    set_momentum = SignalWire("cg.set_momentum")
    local_update = SignalWire("cg.local_update")

    # --- local cap file (local-bus crossbar) ---
    local_weight = AnalogWire("cg.local.weight", 20)
    local_sign   = DigitalWire("cg.local.sign", 20)
    set_bus_id   = DigitalWire("cg.set_bus_id", 1)
    n_caps = 4
    load_id_sig = [SignalWire(f"cg.load_id_{i}") for i in range(n_caps)]
    caps = [LocalCapacitor(f"cg.cap{i}", set_bus_id, local_weight, local_sign, load_id_sig[i])
            for i in range(n_caps)]
    boundary_in_ids = [0, 1]
    boundary_out_ids = [2, 3]

    # --- bank: one Ganglion, group id 1, small random init weights ---
    common = (weight_bus, sign_bus, target_group, feedback, get_weight, set_momentum, local_update)
    inits = [rng.uniform(-0.5, 0.5) for _ in range(29)]
    _g1 = Ganglion(1, *common, inits=inits)       # Scaps self-register; we don't need to keep it

    # --- ALU ---
    g_alu = GanglionALU("cg.g_alu", weight_bus, sign_bus, local_weight, local_sign)
    alu_by_id = {"g_alu": g_alu}

    # --- the program IS the wiring ---
    program = [Instr([0, 1], [2, 3], "g_alu", 1)]

    pwm = PWM("cg.pwm", scope_lr=1.0)
    return ControlUnit("cg", program, alu_by_id, caps, set_bus_id, load_id_sig,
                       boundary_in_ids, boundary_out_ids, parent_weight, parent_sign, in_start, out_start,
                       target_group, get_weight, set_momentum, local_update, feedback, pwm,
                       run, done, reset, update_signal)
