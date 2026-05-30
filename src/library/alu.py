"""The shallow ALU — stateless, slot-space.

GanglionALU does the hardwired 2-3-3-2 forward (29 weights/biases + ReLU at L2/L3, identity at L4) and,
in the same pass, measures each line's contribution. Two jobs:
  JOB 1: write the L4 outputs to the LOCAL bus output slots (N_IN .. N_IN+N_OUT-1).
  JOB 2: write each Scap's contribution |a·W| to the MAIN weight lane and sign(a·W) to the MAIN sign
         lane (for SetMomentum to latch).

It works in SLOT-SPACE: the ControlUnit has already bound the input caps to local slots 0..N_IN-1 and
driven them, and bound the output caps to N_IN.. for the latch afterward.

Canonical 29-Scap order (matches draft5.1 §7.4):
  0..5   W_L1L2[j][i]   (j=0..2 dst, i=0..1 src)   ;  6..8   b_L2[j]
  9..17  W_L2L3[k][j]   (k=0..2 dst, j=0..2 src)   ; 18..20  b_L3[k]
  21..26 W_L3L4[m][k]   (m=0..1 dst, k=0..2 src)   ; 27..28  b_L4[m]

[ALGO] — this whole forward + contribution computation is a first-pass fill of code_concept.md §7.
"""

from .wires import SignalWire


def _relu(x):
    return x if x > 0.0 else 0.0


def _sgn(x):
    return 1 if x >= 0.0 else -1


class GanglionALU:
    N_IN = 2
    N_OUT = 2

    def __init__(self, name, weight_bus, sign_bus, local_weight, local_sign):
        self.name = name
        self.weight_bus = weight_bus          # main bus: Scap weights / contributions
        self.sign_bus = sign_bus
        self.local_weight = local_weight      # local bus: activations
        self.local_sign = local_sign
        self.execute = SignalWire(name + ".execute")
        self.execute.append_trigger(self._run)   # self-owned signal (the §2 exemption)

    def _run(self, _):
        W = [self.weight_bus.read(s) for s in range(29)]                  # effective weights
        L1 = [self.local_weight.read(s) for s in range(self.N_IN)]        # signed inputs (slots 0,1)

        contrib = [0.0] * 29
        fsign = [1] * 29

        def line(idx, a, w):                  # record one wire's contribution, return a*w
            aw = a * w
            contrib[idx] = abs(aw)
            fsign[idx] = _sgn(aw)
            return aw

        # L2 = ReLU(W_L1L2 · L1 + b_L2)
        a2 = [0.0] * 3
        for j in range(3):
            s = 0.0
            for i in range(2):
                s += line(j * 2 + i, L1[i], W[j * 2 + i])
            s += line(6 + j, 1.0, W[6 + j])                              # bias
            a2[j] = _relu(s)

        # L3 = ReLU(W_L2L3 · L2 + b_L3)
        a3 = [0.0] * 3
        for k in range(3):
            s = 0.0
            for j in range(3):
                s += line(9 + k * 3 + j, a2[j], W[9 + k * 3 + j])
            s += line(18 + k, 1.0, W[18 + k])
            a3[k] = s

        # L4 = W_L3L4 · L3 + b_L4   (no clip)
        out = [0.0] * 2
        for m in range(2):
            s = 0.0
            for k in range(3):
                s += line(21 + m * 3 + k, a3[k], W[21 + m * 3 + k])
            s += line(27 + m, 1.0, W[27 + m])
            out[m] = s

        # JOB 1: outputs -> local bus output slots
        for m in range(self.N_OUT):
            self.local_weight.write(self.N_IN + m, out[m])
            self.local_sign.write(self.N_IN + m, _sgn(out[m]))

        # JOB 2: contribution + a·W sign -> main bus (overwrites the weights the Scaps drove)
        for s in range(29):
            self.weight_bus.write(s, contrib[s])
            self.sign_bus.write(s, fsign[s])
