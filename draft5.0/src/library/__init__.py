"""Bio-AnalogCPU simulation library — the reusable element classes.

See ../context.md and ../code_concept.md for the mental model. The only live classes are
Scap (storage atom), the ALU (compute), and ControlUnit (the sequencer); everything else is
a wire, a cap, or data.

NOTE: the [ALGO] parts of code_concept.md are filled here with first-pass implementations so
SLICE-1 (one Ganglion, XOR) can actually run. They are clearly marked and open to revision.
"""

from .debug import SignalGraph
from .wires import AnalogWire, DigitalWire, SignalWire
from .capacitor import LocalCapacitor
from .pwm import PWM
from .scap import Scap
from .banks import Bank, Ganglion, Translate_2_2, Translate_2_4, Translate_4_2
from .alu import GanglionALU
from .control import Instr, ControlUnit, ChildRunner

__all__ = [
    "SignalGraph", "AnalogWire", "DigitalWire", "SignalWire", "LocalCapacitor", "PWM",
    "Scap", "Bank", "Ganglion", "Translate_2_2", "Translate_2_4", "Translate_4_2",
    "GanglionALU", "Instr", "ControlUnit", "ChildRunner",
]
