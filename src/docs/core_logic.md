# `src/core_logic.md` — The Hardware Hiding Inside the Python

> **Read this if you are about to extend the code.** The Python in `library/` reads like clean,
> high-level software. It is not software. It is a **netlist + microarchitecture** of a chip, written in
> Python because Python is a convenient HDL-with-batteries. Every clean line hides silicon.
>
> Python gives us four things real hardware never gets for free:
> **(1) random-access memory, (2) free function calls, (3) free data movement, (4) no clock.**
> We spend all four to keep the code readable. This file is the **decoder ring** — for each Python
> construct, what silicon it actually is, and what it smuggles for free. If you forget the silicon
> underneath and "optimize" the Python, you will quietly design something unbuildable.
>
> Pairs with `question.md` (the confusion FAQ). `concept.md` is the architecture; this file is the
> Python↔hardware map.

---

## 0. The one rule

**Cleanliness in this codebase is a lie we tell on purpose.** The structure (modules, wires, scope
walls, the mux, start-pointers, the instruction stream) is *faithful* to the hardware. The *mechanics*
of moving data and time are *abstracted away* by Python. So: trust the **shapes**, distrust the **ease**.
When a line looks too easy — a pointer passed, an array indexed, a function called — ask "what bus
transaction / mux / decode / clock cycle did Python just hide?"

The single most dangerous lie: **moving a value across a scope wall.** In Python it's one assignment.
In silicon it's a transaction between two separate processors (a MAR/MDR cycle). See §6 — it's the one
to keep in your bones.

---

## 1. Wires and buses — `read(slot)` / `write(slot, v)`

```python
self.values[slot] = float(v)          # AnalogWire.write
return self.values[slot]              # AnalogWire.read
```

- **Silicon:** `AnalogWire`/`DigitalWire` are **physical bus lanes** — N parallel metal wires. `write(slot, v)`
  is a **driver sourcing a voltage** onto wire `slot`; `read(slot)` is a **sense** of that wire.
- **Hidden:** (a) it's **analog** — a voltage/charge, not a clean float (drift, leakage, noise — all
  deferred to PVT; the `AnalogWire`/`DigitalWire` split exists precisely so we can add analog behaviour
  to one and not the other later). (b) A real wire has **exactly one driver at a time** — two writers =
  a short. We never collide only because the control flow time-multiplexes the bus (weights out, then
  contribution in; one Scap group at a time). Python would happily let two things write the same slot;
  silicon would burn.
- **Why this way:** an array is the obvious model of a bus you address by slot.

---

## 2. The mux — `weight_bus.write(io_id, value)`

```python
def drive(self):                      # LocalCapacitor
    self.weight_bus.write(self.io_id, self.value)
```

- **Silicon:** this is a **multiplexer.** A cap is **not** wired to all 20 (or 200) bus lines — it has
  one output that a mux routes to the single line `io_id`, selected by a decoder. `io_id` is the **mux
  select**.
- **Hidden:** the entire reason `io_id` exists. In Python `weight_bus.write(io_id, v)` looks like free
  random-access into an array. In silicon it's "connect my one wire to line `io_id`," and the resource
  argument (you *can't* fan every cap to every line — that's quadratic wiring) is the whole point.
- **Why this way:** indexing by `io_id` is the cleanest way to express "the mux is currently selecting
  slot `io_id`."

---

## 3. The control net — `SignalWire`, `append_trigger`, `update`

```python
sig.append_trigger(self.handler)      # in __init__
sig.update(v)                         # -> for fn in self.triggers: fn(v)
```

- **Silicon:** a `SignalWire` is a **1-bit control wire with fan-out.** `append_trigger` is a
  **fabrication-time wire connection** (the reader is physically tied to the wire). `update(v)` is
  **driving the wire**, and every connected reader **reacts in parallel**.
- **Hidden — the big one here:** the `for fn in self.triggers` loop is **sequential**, but the hardware
  is **simultaneous**. We get away with it because the reactions write *independent* state (Scap A's
  weight, Scap B's weight) — so order can't change the result. **This is exact, not approximate** — but
  the moment two triggers touch shared state, the sequential order would become a fake race the hardware
  doesn't have. (Also hidden: propagation delay — Python's fan-out is instantaneous; a real wire has
  settle time.)
- **Why this way:** the observer/callback pattern *is* a wire's fan-out, and it lets a reader self-wire
  in its own `__init__` (the "wiring rule").

---

## 4. The instruction & the decode — `Instr`, `alu_by_id[ins.alu_id]`

```python
@dataclass
class Instr: input_id; output_id; alu_id; weight_model_id
...
alu = self.alu_by_id[ins.alu_id]
```

- **Silicon:** an `Instr` is a **ROM word** — fixed-width fields: `input_id`/`output_id` are operand
  **addresses**, `weight_model_id` is a **group address** (it goes on a wire — that's why it's an `int`),
  `alu_id` is an **opcode**. `program` is **microcode ROM**. The dict lookup `alu_by_id[ins.alu_id]` is
  an **instruction decoder** — the opcode field drives a decoder that raises one ALU's enable line.
- **Hidden:** the decoder + enable lines (a dict lookup hides a fan of AND gates), and the fact that
  `alu_id` being a *string* is pure sim sugar — in silicon it's an opcode bit-pattern. (`weight_model_id`
  is an `int` exactly because it is driven onto the `target_group` wire; `alu_id` never goes on a wire,
  so it's allowed to stay a readable string key.)
- **Why this way:** a dataclass list is the readable form of an instruction ROM; a dict is the readable
  form of an opcode→unit decoder.

---

## 5. Group select — `target_group.write(0, id)` + `_selected()`

```python
self.target_group.write(0, ins.weight_model_id)   # CU
def _selected(self): return self.target_group.read(0) == self.group_id   # Scap (×200)
```

- **Silicon:** the CU drives a **group-select bus**; every Scap has a **hardwired comparator** that
  matches its fabrication-fixed `group_id` against the bus. Only matching Scaps respond. This is how
  200+ Scaps time-share 29 bus wires.
- **Hidden:** the Python "`for scap: if _selected()`" is **200+ comparators firing in parallel**, not a
  loop. The selection is broadcast + match, not iteration.
- **Why this way:** a per-Scap `==` check is the obvious model of a per-Scap address comparator.

---

## 6. ⚠ The big one — moving data across a scope wall = a MAR/MDR transaction

```python
# bridge IN  (ColumnGroup reads its parent's bus)
self.caps[cid].value = self.parent_weight.read(in0 + k)
# bridge OUT (ColumnGroup writes its parent's bus)
self.parent_weight.write(out0 + k, self.caps[cid].value)
```

- **Silicon:** these two lines are **transactions between two separate processors.** The ColumnGroup and
  its parent (Lobe / Brainstem) are **distinct control units with their own buses and their own clocks.**
  Moving a value between them is the chip's version of a **MAR/MDR cycle**:
  1. the child puts an **address** on the shared boundary (the start pointer `in0 + k` — that's a MAR);
  2. the parent's bus **presents the data** on the data lines (MDR);
  3. the child **latches** it into its cap.
  And the reverse for the store. It is a **multi-cycle bus protocol with arbitration and timing.**
- **Hidden — almost everything.** In Python it's one `=`. In silicon it is the **entire inter-processor
  memory interface**: address out, settle, data in, latch — per slot. This is *the* line where "clean
  Python" hides the most silicon. The contiguous **start pointer** (one address + auto-increment) instead
  of per-slot addressing is a real hardware economy you can *see* once you remember this is a bus
  transaction; in Python it just looks like a `for k` loop.
- **Why this way:** there is no cheap Python idiom for "do a MAR/MDR cycle," so we model it as the
  read/write it ultimately accomplishes — **and write this paragraph so nobody forgets what it costs.**
- **The trap:** because it looks free, a future reader will be tempted to "just pass the cap object
  across" or "share one big bus for everybody." That throws away the scope walls and makes a chip that
  can't be built (every unit wired to every bus). **The start-pointer boundary is load-bearing; keep it.**

---

## 7. The handshake — `run.update(1)` is req/ack across two clock domains

```python
# ChildRunner._run
self.run.update(1)        # "synchronous: returns when the child has finished + raised done"
```

- **Silicon:** the parent raises **`run` (request)**; the child then runs on **its own clock for many
  cycles**; the child raises **`done` (acknowledge)**; the parent proceeds. Two processors, **two clock
  domains**, coordinating by req/ack.
- **Hidden:** in Python `run.update(1)` is a **blocking call** — it synchronously executes the child's
  whole `_forward` and returns. That collapses *two independent clocks and many cycles* into one function
  call. We keep `done` even though it looks ceremonial *because it marks the seam* where a future
  non-blocking / parallel version reintroduces the real asynchrony.
- **Why this way:** sequential blocking is the simplest faithful model of "parent waits for child," and
  it's exact as long as nothing runs concurrently (it doesn't, yet).

---

## 8. The crossbar bind — addressed register load

```python
def _bind(self, cap_ids, base):
    for j, cid in enumerate(cap_ids):
        self.set_bus_id.write(0, base + j)     # put the slot address on the bus
        self.load_id_sig[cid].update(1)        # strobe THIS cap's load line
```

- **Silicon:** the CU drives a **slot address** onto `set_bus_id`, then **strobes** one cap's `load_id`
  wire; the cap **latches the address into its `io_id` register** (its mux select). It's an **addressed
  register write** — exactly the shape of loading a MAR.
- **Hidden:** two clean lines = "broadcast an address, pulse a strobe, latch a register." The per-cap
  `load_id_sig` is a real per-cap control wire.

---

## 9. Time, and the pulse — `pulse` is a duration, the multiply is an integral

```python
self.weight += pulse * self.momentum * direction          # Scap._on_update
```

- **Silicon:** the backward "pulse" is a **PWM pulse width — a *time*.** Holding the `update` wire high
  for `pulse` units of time lets the weight cap **integrate charge** over that window. The multiply
  `pulse * momentum` is the **integral of a (locally) constant current over that time.**
- **Hidden:** **the entire time axis.** There is **no clock in this sim** — operations are "free" and
  instantaneous. In silicon the ALU's charge-wait dominates wall time, the backward pulse takes real
  duration, and the PWM module (`pwm.shape`, currently a multiply) would be a clocked counter. We
  collapsed time→number on purpose; just never read "the sim is fast" as "the chip is fast."
- **Why this way:** for an *ideal* (no-PVT) correctness sim, a multiply is the exact value the PWM
  integral produces. The `PWM` class is kept as a seam so a clocked version drops in later.

---

## 10. Analog state — floats hide capacitor voltages

- **Silicon:** `Scap.weight` is a **capacitor voltage** (sign-magnitude: a positive charge + a sign
  bit). `momentum` is another cap. The update, the saturation rail (`W_RAIL`), the zero-crossing sign
  flip — all **analog charge dynamics**.
- **Hidden:** quantization, leakage, charge-injection, PVT — and the strict magnitude≥0 discipline (we
  keep it for the Scap weight; we approximate activations as signed floats). All deferred.
- **Why this way:** ideal floats first; analog realism is a whole later phase (draft5.1 Phase 8).

---

## 11. "One class, many processors"

`ControlUnit` is **one Python class**, instantiated per scope. In silicon, **each scope is a separate
physical control unit** — its own state machine, its own instruction ROM, its own counters, its own
decode, on its own patch of die, in its own clock domain. The class reuse expresses **shared RTL**, not
a shared processor. Two `ControlUnit` instances talking via `parent_weight` are two chips talking over a
bus (§6), not two objects sharing memory.

---

## 12. The summary table

| Python you see | Silicon it is | What Python hides | Danger if forgotten |
| --- | --- | --- | --- |
| `bus.read/write(slot)` | drive/sense one bus wire | analog voltage; one-driver rule | bus shorts |
| `bus.write(io_id, v)` | a **mux** select + drive | that it's *not* free random access | quadratic wiring |
| `sig.update(v)` → triggers | a wire fan-out, **parallel** | sequential≠parallel; settle time | fake races |
| `alu_by_id[ins.alu_id]` | instruction **decoder** | opcode→enable gates | — |
| `target_group` + `_selected` | broadcast + **comparators** | 200 parallel matches, not a loop | — |
| **`cap.value = parent_bus.read(i)`** | **MAR/MDR inter-processor xfer** | the entire bus protocol | unbuildable (shared buses) |
| `run.update(1)` | **req/ack, two clock domains** | two clocks, many cycles, async | broken timing model |
| `set_bus_id.write; load_id.update` | addressed register (MAR) load | strobe + latch | — |
| `pulse * momentum` | **PWM-time charge integral** | the whole time axis / clock | "sim fast = chip fast" |
| `Scap.weight` float | capacitor voltage | analog dynamics, PVT | — |
| one `ControlUnit` class | many separate processors | distinct clock domains | shared-memory thinking |

---

## 13. The two things to hold in your bones

1. **Across a scope wall, nothing is free.** A value crossing from child to parent is a bus transaction
   (§6). The start-pointer boundary is the *cheap* hardware way to do it; don't replace it with "just
   pass the object."
2. **There is no clock here, but there is one on the chip.** The sim answers *does it compute the right
   thing*, not *how fast / in what order in time*. Forward cost (ALU charge-wait) and backward timing
   (PWM duration) are real on silicon and invisible here.

Everything else, Python models faithfully enough — as long as you remember this file exists.
