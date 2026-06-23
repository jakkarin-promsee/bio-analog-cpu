"""The instruction + the generic ControlUnit + ChildRunner.

One ControlUnit class becomes a ColumnGroup / Lobe / Brainstem-child by what it's given.

FORWARD (driven, in instruction order):
  - bridge IN:  copy parent_bus[in_start + k] -> boundary-in caps   (the CU-mediated boundary, see below)
  - per instruction: bind input/output caps to local slots (crossbar), drive inputs, select the Scap
    group, GetWeight, ALU.execute, SetMomentum, latch outputs
  - bridge OUT: copy boundary-out caps -> parent_bus[out_start + k]
  - fire done   (the handshake seam)

BACKWARD (broadcast + momentum):  pulse = pwm.shape(incoming); fire local_update to all my Scaps;
  recurse to child scopes.

BOUNDARY BRIDGE (resolves code_concept.md §3 flag #2 the "CU-mediated copy" way): boundary caps live in
the local cap pool like any cap; the CU bridges them to the parent bus by indexed read/write at
in_start/out_start (one slot = the mux). This drops bind_in/bind_out from that design.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Instr:
    input_id: List[int]        # local cap ids the ALU reads
    output_id: List[int]       # local cap ids the ALU writes
    alu_id: str                # id -> ALU (dict key)
    weight_model_id: int       # id -> Scap group whose weights load onto the main bus


class ChildRunner:
    """A handshake wrapped to look like an ALU so the forward loop stays one shape. Holds the child's
    run + start-pointer cells (created by THIS scope) and fires SetDataBus -> SetActivate."""

    def __init__(self, name, child, run, in_start, out_start, in_slot, out_slot):
        self.child = child            # the child ControlUnit (used for backward recursion)
        self.run = run
        self.in_start = in_start
        self.out_start = out_start
        self.in_slot = in_slot
        self.out_slot = out_slot
        from .wires import SignalWire
        self.execute = SignalWire(name + ".execute")
        self.execute.append_trigger(self._run)

    def _run(self, _):
        self.in_start.write(0, self.in_slot)      # SetDataBus = two start pointers
        self.out_start.write(0, self.out_slot)
        self.run.update(1)                        # SetActivate; synchronous, returns at child done


class ControlUnit:
    def __init__(self, name, program, alu_by_id, caps, set_bus_id, load_id_sig,
                 boundary_in_ids, boundary_out_ids, parent_weight, parent_sign, in_start, out_start,
                 target_group, get_weight, set_momentum, local_update, feedback, pwm,
                 run, done, reset, update_signal):
        self.name = name
        self.program = program
        self.alu_by_id = alu_by_id
        self.caps = caps                          # list[LocalCapacitor], indexed by cap id
        self.set_bus_id = set_bus_id
        self.load_id_sig = load_id_sig            # list[SignalWire], indexed by cap id
        self.boundary_in_ids = boundary_in_ids
        self.boundary_out_ids = boundary_out_ids
        self.parent_weight = parent_weight
        self.parent_sign = parent_sign
        self.in_start = in_start
        self.out_start = out_start
        self.target_group = target_group
        self.get_weight = get_weight
        self.set_momentum = set_momentum
        self.local_update = local_update
        self.feedback = feedback
        self.pwm = pwm
        self.done = done
        # backward recurses to children; derive them from the ChildRunners in alu_by_id
        self.child_cus = [a.child for a in alu_by_id.values() if isinstance(a, ChildRunner)]
        # self-register on the signals handed in (the parent created run/update/reset)
        run.append_trigger(self._forward)
        update_signal.append_trigger(self._backward)
        reset.append_trigger(self._reset)

    # ---- forward ----
    def _forward(self, _):
        in0 = int(self.in_start.read(0))
        for k, cid in enumerate(self.boundary_in_ids):       # bridge IN (the mux = one slot)
            self.caps[cid].value = self.parent_weight.read(in0 + k)

        for ins in self.program:
            alu = self.alu_by_id[ins.alu_id]
            if isinstance(alu, ChildRunner):                 # RUN_CHILD: handshake, then continue
                alu.execute.update(1)
                continue
            self._bind(ins.input_id, base=0)                 # input caps -> slots 0..N_IN-1
            self._bind(ins.output_id, base=alu.N_IN)         # output caps -> slots N_IN..
            for cid in ins.input_id:
                self.caps[cid].drive()                       # inputs onto the local bus
            self.target_group.write(0, ins.weight_model_id)  # select the Scap group on the main bus
            self.get_weight.update(1)                        # selected Scaps drive weight+sign
            alu.execute.update(1)                            # ALU: forward + contribution
            self.set_momentum.update(1)                      # Scaps latch momentum + forward_sign
            for cid in ins.output_id:
                self.caps[cid].latch()                       # outputs back off the local bus

        out0 = int(self.out_start.read(0))
        for k, cid in enumerate(self.boundary_out_ids):      # bridge OUT
            self.parent_weight.write(out0 + k, self.caps[cid].value)
            self.parent_sign.write(out0 + k, 1 if self.caps[cid].value >= 0 else -1)

        self.done.update(1)

    def _bind(self, cap_ids, base):                          # crossbar: cap_ids[j] -> local slot base+j
        for j, cid in enumerate(cap_ids):
            self.set_bus_id.write(0, base + j)
            self.load_id_sig[cid].update(1)

    # ---- backward ----
    def _backward(self, incoming_pulse):
        pulse = self.pwm.shape(incoming_pulse)
        self.local_update.update(pulse)                      # -> every Scap in this scope
        for cu in self.child_cus:
            cu.update_signal.update(pulse)                   # -> child scopes  (NOTE: needs cu.update_signal)

    def _reset(self, _):
        pass
