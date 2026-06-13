"""Scap — the storage atom. A wire, not a neuron.

Holds a sign-magnitude weight (magnitude >= 0 + sign), a forward_sign bit, and a momentum cap.
Self-registers on three signals (group-gated forward; global backward):

- GetWeight   : drive the signed effective weight onto the main weight lane, sign onto the sign lane.
- SetMomentum : read the ALU's write-back from those same lanes — contribution -> momentum (EMA),
                a·W sign -> forward_sign.
- Update      : weight magnitude += pulse * momentum * (forward_sign * feedback)  [the [ALGO] rule]

Momentum is the ENTIRE per-Scap learning signal (concept.md §8). The Scap does NOT compute its own
forward_sign — it has no input activation; the ALU computes it and hands it back on the sign lane.
"""

ALPHA = 0.75              # momentum EMA factor (right-shift-by-2; draft5.1 §6.8)
MOMENTUM_FLOOR = 1e-3     # floor-at-1 analogue: never let momentum reach zero (dead-weight guard)
MOMENTUM_CEILING = 50.0   # 16-bit ceiling analogue (draft5.1 §2.4 #2)
W_RAIL = 3.0              # PHYSICAL SATURATION: the supply rail (draft5.1 §6.6 / H10). The architecture's
                          # primary defense against winner-take-all. Approximated here: growth toward the
                          # rail slows as dV/dt ~ (V_rail - V_cap), and magnitude is hard-clamped at the rail.


class Scap:
    def __init__(self, group_id, slot, weight_bus, sign_bus, target_group, feedback,
                 get_weight, set_momentum, local_update, init_weight=0.0, alpha=None):
        self.group_id = group_id
        self.slot = slot
        self.weight_bus = weight_bus
        self.sign_bus = sign_bus
        self.target_group = target_group
        self.feedback = feedback
        self.alpha = ALPHA if alpha is None else alpha   # momentum EMA factor (default = arc's 0.75)
        # state (sign-magnitude weight)
        self.weight = abs(init_weight)             # magnitude >= 0
        self.sign = 1 if init_weight >= 0 else -1
        self.forward_sign = 1
        self.momentum = 1.0
        # self-register (the wiring rule)
        get_weight.append_trigger(self._on_get_weight)
        set_momentum.append_trigger(self._on_set_momentum)
        local_update.append_trigger(self._on_update)

    def _selected(self):
        return self.target_group.read(0) == self.group_id

    def _on_get_weight(self, _):
        if not self._selected():
            return
        self.weight_bus.write(self.slot, self.sign * self.weight)   # signed effective weight
        self.sign_bus.write(self.slot, self.sign)

    def _on_set_momentum(self, _):
        if not self._selected():
            return
        contribution = self.weight_bus.read(self.slot)              # |a·W|  (ALU wrote it)
        self.forward_sign = self.sign_bus.read(self.slot)           # sign(a·W)  (ALU wrote it)
        self.momentum = self.alpha * self.momentum + (1 - self.alpha) * contribution
        self.momentum = min(MOMENTUM_CEILING, max(MOMENTUM_FLOOR, self.momentum))

    def _on_update(self, pulse):                                    # global; not group-gated
        direction = self.forward_sign * self.feedback.read(0)       # +1 agree, -1 disagree
        delta = pulse * self.momentum * direction
        if delta > 0.0:                                             # growing toward the rail -> saturate
            delta *= max(0.0, (W_RAIL - self.weight) / W_RAIL)      # dV/dt ~ (V_rail - V_cap)  (§6.6)
        self.weight += delta
        if self.weight < 0.0:                                       # crossed zero -> reflect + flip sign
            self.weight = -self.weight
            self.sign = -self.sign
        if self.weight > W_RAIL:                                    # hard clamp at the rail
            self.weight = W_RAIL
