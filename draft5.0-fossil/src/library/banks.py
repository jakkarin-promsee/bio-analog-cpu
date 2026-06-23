"""Banks — thin factories. A Bank builds `n_scaps` Scaps (which self-register) and holds a group id.
No compute, no control. Ganglion = 29 (2-3-3-2); Translate_* sized to their ALU.
"""

from .scap import Scap


class Bank:
    def __init__(self, group_id, n_scaps, weight_bus, sign_bus, target_group, feedback,
                 get_weight, set_momentum, local_update, inits=None, alpha=None):
        self.group_id = group_id
        self.n_scaps = n_scaps
        if inits is None:
            inits = [0.0] * n_scaps
        self.scaps = [
            Scap(group_id, slot, weight_bus, sign_bus, target_group, feedback,
                 get_weight, set_momentum, local_update, init_weight=inits[slot], alpha=alpha)
            for slot in range(n_scaps)
        ]


class Ganglion(Bank):
    def __init__(self, group_id, *wires, inits=None, alpha=None):
        super().__init__(group_id, 29, *wires, inits=inits, alpha=alpha)


class Translate_2_2(Bank):
    def __init__(self, group_id, *wires, inits=None):
        super().__init__(group_id, 4, *wires, inits=inits)


class Translate_2_4(Bank):
    def __init__(self, group_id, *wires, inits=None):
        super().__init__(group_id, 8, *wires, inits=inits)


class Translate_4_2(Bank):
    def __init__(self, group_id, *wires, inits=None):
        super().__init__(group_id, 8, *wires, inits=inits)
