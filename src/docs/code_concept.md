# `src/code_concept.md` — What the Final Code Should Look Like

> **The destination image.** The *shape* of the code base, not the code. Skeletons, signatures, one
> fully-wired example. Algorithms are black boxes marked `[ALGO — deferred]`. Read `concept.md` first for
> the *why*. The baseline learning rule is the lean **broadcast + momentum** of `concept.md §8`.

---

## 0. The whole thing in one breath

- **Three primitives:** `AnalogWire` / `DigitalWire` (passive data lanes — *pull*, read/write by slot),
  and `SignalWire` (active control net — *push*; value + triggers, `.update()` fires them).
- **One composed register, `LocalCapacitor`** — an inter-step cap that connects to its bus through a
  **mux** at `io_id` (one slot, not fanned to all lines — the bus is wide; full fan-out is unaffordable).
- **One PWM per ControlUnit** — a per-scope **learning-rate** knob (default ~1.0). *Not* credit.
- **Three live classes:** `Scap` (atom, subscriber), the shallow `ALU` (subscriber), the generic
  `ControlUnit` (driver). Everything else is **data**: a flat instruction list, `id → object` dicts, caps.
- **Wiring is self-registration:** pass a `SignalWire` into a class and it appends its own handler.
- **ids are integers** (real addresses). Group ids, slot ids, cap ids: all `int`. (`alu_id` is a `str`
  dict key — never written to a wire, so it stays a string.)
- **Credit = momentum.** Backward is one broadcast pulse, scaled per scope by its LR, weighted per Scap
  by its momentum.

---

## 1. File layout

```
src/
  library/                # the reusable kit (everyone imports from here)
    wires.py      # AnalogWire, DigitalWire, SignalWire
    capacitor.py  # LocalCapacitor
    pwm.py        # PWM
    scap.py       # Scap
    banks.py      # Bank (base), Ganglion, Translate_2_2, ...   (thin factories)
    alu.py        # GanglionALU, TranslateALU_2_2, ...          (shallow)
    control.py    # ControlUnit, Instr, ChildRunner
    debug.py      # SignalGraph
  example/                # reference wirings using library/
    column_group_012.py   # one ColumnGroup — instructions co-located
    lobe_0.py             # column groups + big translates
    brainstem.py          # one lobe + sample queue + loss engine
    run_xor.py            # the SLICE-1 experiment
  h1/  h2/  ...            # experiments — import library/ unchanged
```

---

## 2. Primitives — `AnalogWire`, `DigitalWire`, `SignalWire` (`wires.py`)

```python
class AnalogWire:
    """Analog data lane (width N), read/write by slot. Split from DigitalWire so future endurance /
    PVT tests add analog-only behaviour here (leakage, noise) without touching digital."""
    def __init__(self, name, width): self.name = name; self.values = [0.0] * width
    def read(self, slot):     return self.values[slot]
    def write(self, slot, v): self.values[slot] = v

class DigitalWire:
    """Digital data lane (width N). Exact integer / bit values; no analog drift."""
    def __init__(self, name, width): self.name = name; self.values = [0] * width
    def read(self, slot):     return self.values[slot]
    def write(self, slot, v): self.values[slot] = v

class SignalWire:
    """Active control net. value + a fan-out of triggers. .update() sets the value and fires every
    trigger, synchronously, in registration order."""
    def __init__(self, name): self.name = name; self.value = 0; self.triggers = []
    def append_trigger(self, fn): self.triggers.append(fn)
    def update(self, value):
        self.value = value
        SignalGraph.log(self, value)
        for fn in self.triggers: fn(value)
```

> **Wiring rule — `append_trigger` *is* the wire.** Pass a `SignalWire` into a class and let it
> self-register in `__init__`. The connection is explicit in the constructor; the build stays a flat
> list of instantiations. (A module may wire a trigger on a signal *it* created — e.g. an ALU on its own
> `execute`.) Rule of thumb: a **number** is *pulled* (an `*Wire` slot or a `LocalCapacitor`); an
> **op/control signal** is *pushed* (a `SignalWire`).

---

## 3. The `LocalCapacitor` — the muxed inter-step register (`capacitor.py`)

A cap connects to its bus through a **mux at `io_id`** — it touches one slot, not every line. `io_id`
is `slot_cell + offset`; the `offset` lets a contiguous block auto-increment from one start pointer.

```python
class LocalCapacitor:
    """Inter-step register: magnitude + sign + io_id (the bus slot it is MUXed onto right now)."""
    def __init__(self, name, slot_cell, weight_bus, sign_bus, bind_sig, offset=0):
        self.name = name; self.value = 0.0; self.sign = +1
        self.io_id = None
        self.slot_cell, self.offset = slot_cell, offset        # io_id = slot_cell + offset
        self.weight_bus, self.sign_bus = weight_bus, sign_bus  # the bus this cap MUXes onto
        bind_sig.append_trigger(self.load_id)                  # self-register: fired to (re)bind me

    def load_id(self, _):   self.io_id = int(self.slot_cell.read(0)) + self.offset   # the MUX select
    def drive(self):        self.weight_bus.write(self.io_id, self.value); self.sign_bus.write(self.io_id, self.sign)
    def latch(self):        self.value = abs(self.weight_bus.read(self.io_id)); self.sign = self.sign_bus.read(self.io_id)
```

**Two uses of the same mux:**

- **Internal caps** mux onto the *scope's own* local bus. `slot_cell = set_bus_id`, `offset = 0`, and
  each has its own `load_id_sig[i]`. The CU rebinds them per instruction (writes `set_bus_id`, fires
  `load_id_sig[i]`) — any cap to any slot.

```python
local_weight = AnalogWire ("local.weight", 20)
local_sign   = DigitalWire("local.sign",   20)
set_bus_id   = DigitalWire("local.set_bus_id", 1)
load_id_sig  = [SignalWire(f"local.load_id_{i}") for i in range(30)]
caps = [LocalCapacitor(f"cap{i}", set_bus_id, local_weight, local_sign, load_id_sig[i])
        for i in range(30)]
```

- **Boundary caps** mux onto the *parent's* bus — that's how a scope's I/O crosses the wall. The parent
  sends one **start pointer** per direction; the boundary caps auto-increment from it via `offset = k`:

```python
in_start  = DigitalWire("in_start", 1)    # parent writes the input block's first slot
out_start = DigitalWire("out_start", 1)
bind_in   = SignalWire("bind_in")         # parent fires → every input boundary cap (re)binds
bind_out  = SignalWire("bind_out")
boundary_in  = [LocalCapacitor(f"in{k}",  in_start,  parent_weight, parent_sign, bind_in,  offset=k) for k in range(n_in)]
boundary_out = [LocalCapacitor(f"out{k}", out_start, parent_weight, parent_sign, bind_out, offset=k) for k in range(n_out)]
```

**Why a mux / start pointer?** A lobe bus is 200+ wide; wiring every cap (and every child ColumnGroup)
to every line is unaffordable, so each connects to *one* slot through a mux. A child's I/O is a
contiguous block, so the parent locates it with a single start pointer and the child auto-increments —
physically honest (a real bus is a contiguous span you connect to or don't; you can't teleport to an
arbitrary id). **`SetDataBus`** is therefore: `in_start.write(0, s); bind_in.update(1)` (+ out), then run.

> **Interpretation flag (#2):** I bridge parent↔scope by making boundary caps mux onto the *parent* bus
> while sitting in the scope's cap pool, and having the CU `latch` the input boundary caps from the
> parent bus before the program and `drive` the output ones after (§9). If you instead want the boundary
> cap to physically sit on *both* buses (a true two-port bridge cell), that's a small change here.

---

## 4. PWM — a per-scope learning-rate knob (`pwm.py`)

```python
class PWM:
    """Per ControlUnit. Scales the backward pulse by this scope's LEARNING RATE. NOT credit
    (credit = momentum). For future multi-rate Lobes. NOW: multiply. FUTURE: clocked circuit."""
    def __init__(self, name, scope_lr=1.0): self.name = name; self.scope_lr = scope_lr
    def shape(self, pulse): return pulse * self.scope_lr
```

---

## 5. The Scap — a subscriber atom (`scap.py`)

```python
class Scap:
    def __init__(self, group_id, slot, weight_bus, sign_bus, target_group, feedback,
                 get_weight, set_momentum, local_update):
        self.group_id, self.slot = group_id, slot           # group_id is an int
        self.weight_bus, self.sign_bus = weight_bus, sign_bus
        self.target_group, self.feedback = target_group, feedback   # shared cells from the top
        self.weight = 0.0; self.sign = +1; self.forward_sign = +1; self.momentum = 1.0
        get_weight.append_trigger(self._on_get_weight)       # self-register
        set_momentum.append_trigger(self._on_set_momentum)
        local_update.append_trigger(self._on_update)         # the scope's backward pulse

    def _selected(self): return self.target_group.read(0) == self.group_id

    def _on_get_weight(self, _):
        if not self._selected(): return
        self.weight_bus.write(self.slot, self.weight)        # magnitude → weight lane
        self.sign_bus.write(self.slot, self.sign)            # weight-sign → sign lane
        # forward_sign is NOT computed here — the Scap has no 'a'; the ALU computes it (§7)

    def _on_set_momentum(self, _):
        if not self._selected(): return
        contribution = self.weight_bus.read(self.slot)       # ALU wrote it here
        self.forward_sign = self.sign_bus.read(self.slot)    # ALU wrote a·W sign here
        # self.momentum = ema(self.momentum, contribution)   [ALGO — deferred]

    def _on_update(self, pulse):                             # global broadcast; NOT group-gated
        direction = self.forward_sign * self.feedback.read(0)   # ±1 * ±1 = the XOR in value-space
        # self.weight -= pulse * self.momentum * direction   [ALGO — deferred; no rail yet, §13]
        ...
```

Both lanes are bidirectional in time: GetWeight = Scap drives (magnitude, weight-sign); SetMomentum =
ALU drives (contribution, a·W sign).

---

## 6. Banks — thin factories (`banks.py`)

```python
class Bank:
    """A named group of `n_scaps` Scaps on slots 0..n_scaps-1. The Scaps self-register on the group's
    signals as they're built."""
    def __init__(self, group_id, n_scaps, weight_bus, sign_bus, target_group, feedback,
                 get_weight, set_momentum, local_update):
        self.group_id, self.n_scaps = group_id, n_scaps
        self.scaps = [Scap(group_id, slot, weight_bus, sign_bus, target_group, feedback,
                           get_weight, set_momentum, local_update) for slot in range(n_scaps)]

class Ganglion(Bank):
    def __init__(self, group_id, *wires): super().__init__(group_id, 29, *wires)   # 2-3-3-2 → 29
class Translate_2_2(Bank):
    def __init__(self, group_id, *wires): super().__init__(group_id, 4,  *wires)
class Translate_2_4(Bank):
    def __init__(self, group_id, *wires): super().__init__(group_id, 8,  *wires)
class Translate_4_2(Bank):
    def __init__(self, group_id, *wires): super().__init__(group_id, 8,  *wires)
```

A bank is a constructor convenience, not a controller. (Build passes small random init weights, spec §19.)

---

## 7. The shallow ALU (`alu.py`) — two jobs in one pass

```python
class GanglionALU:
    """Stateless 2-3-3-2 (29 weights + biases + activation). Works in SLOT-SPACE on the local bus:
    inputs at slots 0..N_IN-1, outputs at N_IN..N_IN+N_OUT-1 (separate ranges, no clobber)."""
    N_IN, N_OUT = 2, 2
    def __init__(self, name, weight_bus, sign_bus, local_weight, local_sign):
        self.weight_bus, self.sign_bus = weight_bus, sign_bus           # main bus: Scap weights
        self.local_weight, self.local_sign = local_weight, local_sign   # local bus: activations
        self.execute = SignalWire(name + ".execute")
        self.execute.append_trigger(self._run)                          # self-owned signal

    def _run(self, _):
        # READ inputs — BOTH lanes (magnitude × sign) → signed activations:
        #   xs = [self.local_sign.read(s) * self.local_weight.read(s) for s in range(self.N_IN)]
        # read Scap weights off the main bus → compute the 2-3-3-2 forward                 [ALGO]
        # JOB 1 (~95%): write outputs to local slots N_IN..N_IN+N_OUT-1 (magnitude + sign) [ALGO]
        # JOB 2 (~80%, uniform → constant LR, no bias): write per-line contribution → main
        #        weight lane, a·W sign → main sign lane (for SetMomentum)                  [ALGO]

class TranslateALU_4_2:  N_IN, N_OUT = 4, 2   # ... same shape, n→m matmul, no bias/activation
```

Shape match is asserted **at build** (where both `group_by_id` and `alu_by_id` are in hand):
a `GanglionALU` pairs with a 29-Scap group, `TranslateALU_4_2` with an 8-Scap group, etc.

---

## 8. Debug — the signal graph (`debug.py`)

```python
class SignalGraph:
    """Waveform-style log, like a VHDL trace. Off by default."""
    enabled = False; timeline = []; step = 0          # step advances once per sample
    @classmethod
    def log(cls, wire, value):
        if cls.enabled: cls.timeline.append((cls.step, wire.name, value))
    @classmethod
    def dump(cls): ...
```

---

## 9. The instruction + the generic ControlUnit (`control.py`)

```python
@dataclass
class Instr:
    input_id:  list[int]     # local cap ids the ALU reads
    output_id: list[int]     # local cap ids the ALU writes
    alu_id:    str           # id → ALU (dict key)
    weight_model_id: int     # id → Scap group whose weights load onto the main bus

class ControlUnit:
    """One class → ColumnGroup / Lobe / Brainstem, by what it's given."""
    def __init__(self, name, program, alu_by_id, caps,
                 set_bus_id, load_id_sig,                       # internal crossbar channel
                 boundary_in, boundary_out, parent_weight, parent_sign, in_start, out_start,  # boundary bridge
                 target_group, get_weight, set_momentum, local_update, feedback, pwm,
                 run, done, reset, update_signal):
        ...store all...
        self.child_cus = [a.child for a in alu_by_id.values() if isinstance(a, ChildRunner)]  # derive once
        run.append_trigger(self._forward)              # self-register on the signals handed in
        update_signal.append_trigger(self._backward)
        reset.append_trigger(self._reset)

    def _forward(self, _):
        for k, cap in enumerate(self.boundary_in):     # bridge IN: pull from parent bus (the mux = one slot)
            cap.value = abs(self.parent_weight.read(int(self.in_start.read(0)) + k))
            cap.sign  = self.parent_sign.read(int(self.in_start.read(0)) + k)
        for ins in self.program:
            self._bind(ins.input_id,  base=0);                 alu = self.alu_by_id[ins.alu_id]
            self._bind(ins.output_id, base=alu_in_count(alu))  # outputs in a separate slot range
            for cid in ins.input_id: self.caps[cid].drive()    # inputs onto the local bus
            self.target_group.write(0, ins.weight_model_id)    # select the Scap group on the main bus
            self.get_weight.update(1)                          # selected Scaps drive weight+sign
            alu.execute.update(1)                              # ALU works in slot-space [ALGO]
            self.set_momentum.update(1)                        # Scaps latch momentum + forward_sign
            for cid in ins.output_id: self.caps[cid].latch()   # outputs back off the local bus
        for k, cap in enumerate(self.boundary_out):    # bridge OUT: push to parent bus
            self.parent_weight.write(int(self.out_start.read(0)) + k, cap.value)
            self.parent_sign.write(int(self.out_start.read(0)) + k, cap.sign)
        self.done.update(1)                            # handshake out

    def _bind(self, cap_ids, base):                    # crossbar: cap_ids[j] → local slot base+j
        for j, cid in enumerate(cap_ids):
            self.set_bus_id.write(0, base + j); self.load_id_sig[cid].update(1)

    def _backward(self, incoming_pulse):               # broadcast + momentum (concept.md §8)
        pulse = self.pwm.shape(incoming_pulse)
        self.local_update.update(pulse)                # → every Scap in this scope
        for cu in self.child_cus:                      # → recurse to child scopes
            cu.update_signal.update(pulse)

    def _reset(self, _): ...                           # clear transient state [ALGO]
```

**`RUN_CHILD` is a handshake wrapped as an ALU** so `_forward` stays one loop. It holds the child's
boundary signals (created by *this* scope) and fires them — `SetDataBus` is two start pointers:

```python
class ChildRunner:
    def __init__(self, name, child, run, in_start, out_start, bind_in, bind_out, in_slot, out_slot):
        self.child = child                                       # the child ControlUnit (for backward)
        self.run, self.in_start, self.out_start = run, in_start, out_start
        self.bind_in, self.bind_out, self.in_slot, self.out_slot = bind_in, bind_out, in_slot, out_slot
        self.execute = SignalWire(name + ".execute"); self.execute.append_trigger(self._run)
    def _run(self, op):                                          # SetDataBus → SetActivate
        self.in_start.write(0, self.in_slot);   self.bind_in.update(1)
        self.out_start.write(0, self.out_slot); self.bind_out.update(1)
        self.run.update(1)        # synchronous: returns when the child has finished + raised done
```

---

## 10. A specific module — `example/column_group_012.py`

```python
def build(parent_weight, parent_sign, in_start, out_start, bind_in, bind_out,
          run, done, reset, update_signal, feedback):
    # --- main bus (Scap weights) + scope op signals ---
    weight_bus   = AnalogWire ("cg012.weight", 80)
    sign_bus     = DigitalWire("cg012.sign", 80)
    target_group = DigitalWire("cg012.target_group", 1)
    get_weight   = SignalWire("cg012.get_weight")
    set_momentum = SignalWire("cg012.set_momentum")
    local_update = SignalWire("cg012.local_update")
    # --- internal cap file (local-bus crossbar) ---
    local_weight = AnalogWire ("cg012.local.weight", 20)
    local_sign   = DigitalWire("cg012.local.sign", 20)
    set_bus_id   = DigitalWire("cg012.set_bus_id", 1)
    load_id_sig  = [SignalWire(f"cg012.load_id_{i}") for i in range(18)]
    caps = [LocalCapacitor(f"cg012.cap{i}", set_bus_id, local_weight, local_sign, load_id_sig[i])
            for i in range(18)]
    # --- boundary caps: mux onto the PARENT bus, auto-incremented from the start pointers ---
    n_in, n_out = 2, 4
    boundary_in  = [LocalCapacitor(f"cg012.in{k}",  in_start,  parent_weight, parent_sign, bind_in,  offset=k) for k in range(n_in)]
    boundary_out = [LocalCapacitor(f"cg012.out{k}", out_start, parent_weight, parent_sign, bind_out, offset=k) for k in range(n_out)]

    # --- banks: int ids; Scaps self-register on the nets ---
    common = (weight_bus, sign_bus, target_group, feedback, get_weight, set_momentum, local_update)
    group_by_id = {i: Ganglion(i, *common) for i in (1, 2, 3, 4, 5)}   # groups 1..5
    group_by_id[10] = Translate_4_2(10, *common)                       # group 10 = T1

    # --- ALUs (str keys) ---
    alu_by_id = {
        "g_alu":     GanglionALU("cg012.g_alu", weight_bus, sign_bus, local_weight, local_sign),
        "t_alu_4x2": TranslateALU_4_2("cg012.t_alu_4x2", weight_bus, sign_bus, local_weight, local_sign),
    }
    assert_shapes(alu_by_id, group_by_id)                              # GanglionALU↔29, T_4_2↔8

    # --- instructions: cap ids 0,1 = boundary_in; the rest internal; last writes boundary_out ---
    program = [
        Instr([0, 1],       [2, 3],   "g_alu",     1),     # group 1
        Instr([4, 5],       [6, 7],   "g_alu",     2),     # group 2
        Instr([2, 3, 6, 7], [12, 13], "t_alu_4x2", 10),    # group 10 (T1)
        Instr([12, 13],     [14, 15], "g_alu",     3),     # group 3 → boundary_out
    ]

    pwm = PWM("cg012.pwm", scope_lr=1.0)
    return ControlUnit("cg012", program, alu_by_id, caps, set_bus_id, load_id_sig,
                       boundary_in, boundary_out, parent_weight, parent_sign, in_start, out_start,
                       target_group, get_weight, set_momentum, local_update, feedback, pwm,
                       run, done, reset, update_signal)
```

To rewire CG-012 you edit `program` — nothing else.

---

## 11. Lobe & Brainstem (same pattern, sketched)

```python
# example/lobe_0.py — no Ganglion ALU; big translates + child ColumnGroups via ChildRunner
def build(parent_weight, parent_sign, in_start, out_start, bind_in, bind_out,
          run, done, reset, update_signal, feedback):
    lobe_weight = AnalogWire("lobe0.weight", 256); lobe_sign = DigitalWire("lobe0.sign", 256)
    # signals THIS lobe creates for its child (passed to the child build AND to the ChildRunner):
    cg_run = SignalWire("cg012.run"); cg_done = SignalWire("cg012.done")
    cg_in_start = DigitalWire("cg012.in_start", 1); cg_out_start = DigitalWire("cg012.out_start", 1)
    cg_bind_in = SignalWire("cg012.bind_in"); cg_bind_out = SignalWire("cg012.bind_out")
    cg_update = SignalWire("cg012.update_signal"); cg_reset = SignalWire("cg012.reset")

    cg012 = column_group_012.build(lobe_weight, lobe_sign, cg_in_start, cg_out_start,
                                   cg_bind_in, cg_bind_out, cg_run, cg_done, cg_reset, cg_update, feedback)
    alu_by_id = {
        "RUN_CG012": ChildRunner("lobe0.run_cg012", cg012, cg_run, cg_in_start, cg_out_start,
                                 cg_bind_in, cg_bind_out, in_slot=0, out_slot=100),
        "t_alu_32_64": BigTranslateALU_32_64("lobe0.t_alu_32_64", lobe_weight, lobe_sign, ...),
    }
    program = [ Instr([...], [...], "RUN_CG012", 0), Instr([...], [...], "t_alu_32_64", 20) ]
    return ControlUnit("lobe0", program, alu_by_id, ...)   # child_cus derived from RUN_CG012
```

```python
# example/brainstem.py — one child (the lone ColumnGroup in SLICE-1, or the Lobe later)
class Brainstem:
    def __init__(self, ...):
        self.chip_weight = AnalogWire("chip.weight", 256); self.chip_sign = DigitalWire("chip.sign", 256)
        self.feedback = DigitalWire("chip.feedback", 1)        # ±1; threaded down to every Scap
        # ... creates the child's run / in_start / out_start / bind_in / bind_out / update / reset,
        #     passes them to the child build, and holds them to drive (like a ChildRunner)
    def run_sample(self, sample):
        for k, x in enumerate(sample.input_value):             # place input on my bus at slots 0..
            self.chip_weight.write(k, abs(x)); self.chip_sign.write(k, +1 if x >= 0 else -1)
        self.in_start.write(0, 0);    self.bind_in.update(1)   # SetDataBus = start pointers
        self.out_start.write(0, 100); self.bind_out.update(1)
        self.run.update(1)                                     # SetActivate; blocks until done
        pred = [self.chip_sign.read(100 + k) * self.chip_weight.read(100 + k) for k in range(self.N_OUT)]
        pulse, direction = self.loss_engine(pred, sample.output_value)   # [ALGO]
        self.feedback.write(0, direction)
        self.child.update_signal.update(pulse)                 # backward — broadcast + momentum
```

`feedback`, `reset`, and the top `update_signal` are created once in the Brainstem and threaded **by
reference** down every `build` to every Scap.

---

## 12. Build this first (`# SLICE-1`)

1. `library/`: `wires.py`, `capacitor.py`, `pwm.py` (lr=1.0), `scap.py`, `banks.{Bank,Ganglion}`,
   `alu.GanglionALU`, `control.py`.
2. One `ControlUnit` with **one** Ganglion group; backward = broadcast pulse × momentum (scope_lr = 1).
3. A minimal `Brainstem` driving that one ColumnGroup directly (no Lobe), binding its boundary with the
   two start pointers (`in_start=0`, `out_start=…`) + `run_xor.py`.
4. Goal: loss on XOR drops monotonically.

**Defer:** the Lobe + `ChildRunner` chain, multiple groups, extra ALU stages, clocked/multi-rate PWM.

---

## 13. Not in this file (deferred) — and two caveats

- **The algorithms** — every `[ALGO]`: forward math, momentum EMA, the update equation, the loss.
- **Caveat — saturation is in, but first-pass.** The Scap `_on_update` has a supply rail (`W_RAIL`: a hard
  clamp + a charging slowdown) — without it weights ran away to NaN (confirmed §22 #14). It approximates
  the H10 self-limiting; full analog charge dynamics are deferred.
- **Caveat — lean baseline.** Backward is *broadcast + momentum*, deliberately simpler than draft5.1 §2's
  normalized Current-Mirror diffusion (a §22 #3/#6 deviation, recorded in `concept.md §8`).
- **Also deferred:** parallel ALUs / non-blocking handshake, clocked + multi-rate PWM, the second Lobe +
  Limbic recurrence, PVT realism (the analog/digital split is the hook), bit-level routing.

---

_Destination first, headache later. When the code disagrees with this file, fix whichever is wrong._
