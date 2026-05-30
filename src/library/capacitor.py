"""LocalCapacitor — the muxed inter-step register.

A cap connects to its bus through a MUX at `io_id` (one slot, not fanned to every line — the resource
argument). `io_id = slot_cell + offset`. drive()/latch() are the muxed write/read.

SLICE-1 simplification: cap `value` is a SIGNED float (the local activation bus carries signed values
in the weight lane; the sign lane is written for structure but the value is read back signed). The
spec's strict sign-magnitude capacitor (voltage >= 0 + a sign bit, zero-crossing flip) is kept where
it matters — inside the Scap weight — and approximated as a signed float here for activations.
"""


class LocalCapacitor:
    def __init__(self, name, slot_cell, weight_bus, sign_bus, load_id_sig, offset=0):
        self.name = name
        self.value = 0.0
        self.io_id = None
        self.slot_cell = slot_cell           # the cell the CU writes the (base) slot into
        self.offset = offset                 # boundary blocks auto-increment from one start pointer
        self.weight_bus = weight_bus
        self.sign_bus = sign_bus
        load_id_sig.append_trigger(self.load_id)   # self-register: fired to (re)bind me

    def load_id(self, _):                    # the MUX select
        self.io_id = int(self.slot_cell.read(0)) + self.offset

    def drive(self):                         # put my value on my one slot
        self.weight_bus.write(self.io_id, self.value)
        self.sign_bus.write(self.io_id, 1 if self.value >= 0 else -1)

    def latch(self):                         # take my slot back into me
        self.value = self.weight_bus.read(self.io_id)
