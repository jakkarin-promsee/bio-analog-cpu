"""PWM — a per-scope learning-rate knob (multiply now).

NOT the credit mechanism (credit is Scap momentum). It exists so future multi-rate Lobes (fast Cortex /
slow Hippocampus) can run at different rates from one shared loss. SLICE-1 uses scope_lr = 1.0.
FUTURE: a real clocked PWM circuit for realtime/PVT timing.
"""


class PWM:
    def __init__(self, name, scope_lr=1.0):
        self.name = name
        self.scope_lr = scope_lr

    def shape(self, pulse):
        return pulse * self.scope_lr
