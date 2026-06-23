"""SignalGraph — a waveform-style log of every SignalWire fire (off by default).

Because the control model is push/observer, "who fired when" is otherwise invisible. Turn it on
with `SignalGraph.enabled = True` and read `SignalGraph.timeline` (or `.dump()`), like a VHDL trace.
"""


class SignalGraph:
    enabled = False
    timeline = []          # list of (step, wire_name, value)
    step = 0               # advance once per sample (the runner bumps it)

    @classmethod
    def log(cls, wire, value):
        if cls.enabled:
            cls.timeline.append((cls.step, wire.name, value))

    @classmethod
    def clear(cls):
        cls.timeline = []
        cls.step = 0

    @classmethod
    def dump(cls):
        for row in cls.timeline:
            print(row)
