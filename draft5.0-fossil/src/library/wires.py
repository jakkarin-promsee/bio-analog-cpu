"""The three primitives.

- AnalogWire / DigitalWire: passive data lanes (read/write by slot). Split so future endurance/PVT
  tests can add analog-only drift to AnalogWire without touching digital. For the ideal SLICE-1 sim
  both are just value arrays.
- SignalWire: the active control net (observer). .update() sets the value and fires every registered
  trigger, synchronously, in registration order. `append_trigger` IS the wire.
"""

from .debug import SignalGraph


class AnalogWire:
    def __init__(self, name, width):
        self.name = name
        self.values = [0.0] * width

    def read(self, slot):
        return self.values[slot]

    def write(self, slot, v):
        self.values[slot] = float(v)


class DigitalWire:
    def __init__(self, name, width):
        self.name = name
        self.values = [0] * width

    def read(self, slot):
        return self.values[slot]

    def write(self, slot, v):
        self.values[slot] = int(v)


class SignalWire:
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.triggers = []

    def append_trigger(self, fn):
        self.triggers.append(fn)

    def update(self, value):
        self.value = value
        SignalGraph.log(self, value)
        for fn in self.triggers:
            fn(value)
