"""Brainstem — now instruction-driven, like every other control level.

The collapse (your call): ColumnGroup, Lobe, and Brainstem are the SAME instruction-walking machine —
they differ only in bus size, ALU set, and children. So the Brainstem runs its children via a program
of `ChildRunner` instructions + start-pointer SetDataBus, exactly as a Lobe runs ColumnGroups.
Multi-lobe = just more entries in `self.program`.

What is unique to the top (and ONLY the top):
  - it owns NO Scaps/ALUs — its program is pure child-dispatch;
  - it SYNTHESIZES the backward pulse (the loss engine), because there is no parent to hand it one;
  - it owns the chip bus and the off-chip sample loop.

(For SLICE-1 the single "child" is the lone ColumnGroup, since there's no Lobe yet — same machinery.)
"""

from ..library import AnalogWire, DigitalWire, SignalWire, ChildRunner


def mse_loss_engine(outputs, target, lr):
    """The Brainstem's [ALGO] loss engine. prediction = output[0]; MSE = (target - pred)^2.
    feedback = sign(target - pred); pulse = lr * |target - pred| (broadcast magnitude)."""
    pred = outputs[0]
    err = target - pred
    feedback = 1 if err >= 0 else -1
    pulse = lr * abs(err)
    return pulse, feedback, err * err


class Brainstem:
    def __init__(self, child_specs, lr=0.05, seed=42):
        # child_specs: list of dict(build, in_slot, out_slot, n_in, n_out) — one per child (Lobe / CG)
        self.lr = lr
        self.chip_weight = AnalogWire("chip.weight", 256)
        self.chip_sign = DigitalWire("chip.sign", 256)
        self.feedback = DigitalWire("chip.feedback", 1)
        self.program = []          # list of (ChildRunner, spec) — the Brainstem's instruction stream
        self.child_updates = []    # each child's update_signal (fired during backward)

        for i, spec in enumerate(child_specs):
            run = SignalWire(f"chip.run{i}")
            done = SignalWire(f"chip.done{i}")
            in_start = DigitalWire(f"chip.in_start{i}", 1)
            out_start = DigitalWire(f"chip.out_start{i}", 1)
            update = SignalWire(f"chip.update{i}")
            reset = SignalWire(f"chip.reset{i}")
            child = spec["build"](self.chip_weight, self.chip_sign, in_start, out_start,
                                  run, done, reset, update, self.feedback, seed=seed + i)
            runner = ChildRunner(f"chip.run_child{i}", child, run, in_start, out_start,
                                 spec["in_slot"], spec["out_slot"])
            self.program.append((runner, spec))
            self.child_updates.append(update)

    def forward(self, x):
        in_slot = self.program[0][1]["in_slot"]            # place input where the first child expects it
        for k, v in enumerate(x):
            self.chip_weight.write(in_slot + k, v)
            self.chip_sign.write(in_slot + k, 1 if v >= 0 else -1)
        for runner, _ in self.program:                     # walk the instruction stream: run each child
            runner.execute.update(1)
        spec = self.program[0][1]                          # read prediction from the first child's output
        return [self.chip_weight.read(spec["out_slot"] + m) for m in range(spec["n_out"])]

    def train_step(self, x, target):
        out = self.forward(x)
        pulse, fb, loss = mse_loss_engine(out, target, self.lr)
        self.feedback.write(0, fb)
        for update in self.child_updates:                  # backward: synthesize the pulse, broadcast
            update.update(pulse)
        return loss, out[0]
