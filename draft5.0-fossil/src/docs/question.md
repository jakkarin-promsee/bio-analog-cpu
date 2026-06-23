# `src/question.md` — The Questions You'll Ask Reading This Code

> Every question here is one a smart outsider (or future-you, or the next model) actually asks the first
> time they read `library/`. Each has a short answer and a pointer into `core_logic.md` for the full
> story. If you're confused by something not listed, it probably belongs here — add it.
>
> The through-line: **this Python looks like software but is a chip.** Most confusion is "this looks too
> easy" (it's hiding silicon) or "this looks weird" (it's faithful to silicon and software-brain dislikes
> it). `core_logic.md` is the decoder ring.

---

## Part A — "Wait, this looks way too easy"

**Q1. The ControlUnit just does `cap.value = parent_weight.read(i)` to get data from its parent. Aren't
the parent and child two *different* processors? How is that one line?**
It is two different processors, and that one line is the biggest lie in the codebase. In silicon it's a
**MAR/MDR transaction** — the child puts an address on the boundary, the parent presents data, the child
latches it — a multi-cycle bus protocol. Python has no cheap idiom for "do a bus cycle," so we model the
*result* (the read/write). **Never** replace it by "passing the cap object across" — that throws away the
scope walls and makes an unbuildable chip. → `core_logic.md §6`.

**Q2. `weight_bus.write(io_id, v)` is just array indexing. Why the whole `io_id` ceremony?**
Because it's a **multiplexer**, not an array. A cap isn't wired to all 20+ lines; it has one output a mux
routes to line `io_id`. `io_id` is the mux select. Full fan-out (every cap to every line) is quadratic
wiring you can't afford — the mux *is* the point. → `core_logic.md §2`.

**Q3. `alu_by_id[ins.alu_id]` is a dict lookup. That's the "instruction decode"?**
Yes. In silicon the instruction's opcode field drives a **decoder** that enables one ALU. A dict lookup
is the readable form of "opcode → enable line." → `core_logic.md §4`.

**Q4. Selecting a Scap group is just `target_group.write(0, id)` and each Scap checks `== group_id`. That's
a `for` loop over 200 Scaps?**
In Python, yes; in silicon, no. The CU drives a **group-select bus** and every Scap has a **hardwired
comparator** that fires **in parallel**. The "loop" is 200 simultaneous matches. → `core_logic.md §5`.

**Q5. `run.update(1)` runs the whole child and returns. So a handshake is just a function call?**
The handshake is a **req/ack across two clock domains** — parent raises `run`, child runs on its own
clock for many cycles, child raises `done`. Python collapses two clocks + many cycles into one blocking
call. `done` looks ceremonial but marks the seam where real (parallel/async) timing returns later.
→ `core_logic.md §7`.

**Q6. Is this fast? It runs XOR in a second.**
The *sim* is fast; the *chip* is not. We model **no clock and no charge time** — the ALU's
capacitor-charge wait (the real bottleneck) is invisible here. The sim answers "does it compute the right
thing," never "how fast." → `core_logic.md §9, §13`.

---

## Part B — "Wait, this looks weird / wrong"

**Q7. Firing a signal calls a list of functions one by one. Doesn't order matter? Isn't that a race?**
A `SignalWire` is a **wire fanning out to its readers**, which in hardware react **simultaneously**. We
iterate sequentially, and it's **exact** — because the readers write *independent* state (each Scap its
own weight), so order can't change the answer. It would only become a fake race if two readers touched
shared state, which they don't. → `core_logic.md §3`.

**Q8. The same `weight_bus` holds the Scap weights, and then the contributions? It gets overwritten?**
Yes — the main bus is **bidirectional in time.** Phase 1 (GetWeight): Scaps drive their weights out;
the ALU reads them. Phase 2 (SetMomentum): the ALU drives each Scap's *contribution* + `a·W` sign back
onto the *same* wires; the Scaps latch them. One bus, two phases, never simultaneous. → `core_logic.md §1`.

**Q9. Where is the clock? Nothing advances time.**
There isn't one — on purpose. This is an *ideal* correctness sim. Time (the global clock, the PWM pulse
duration, the ALU charge wait) is collapsed away. The `PWM` class and the `done` signal are kept as seams
for when a clocked version is needed (PVT / realtime). → `core_logic.md §9`.

**Q10. The backward "pulse" is a number you multiply by momentum. Weren't we told loss is *time*?**
It is time — a **PWM pulse width.** Holding the update wire high for `pulse` time integrates charge into
the weight cap; the multiply `pulse * momentum` is exactly that integral for a (locally) constant
current. We collapsed time→number because, with no PVT, the integral *is* the product. → `core_logic.md §9`.

**Q11. Why is `alu_id` a string but `weight_model_id` an int? Inconsistent.**
Deliberate. `weight_model_id` is **driven onto a wire** (`target_group`), and wires carry ints (digital
values) — so it's an int. `alu_id` is **only ever a decoder opcode** modeled as a dict key; it never
touches a wire, so it's allowed to stay a human-readable string. → `core_logic.md §4`.

**Q12. Weights are plain floats. Where's the sign-magnitude capacitor, the rail, the analog stuff?**
The Scap weight *is* kept sign-magnitude (magnitude ≥ 0 + a sign bit, with a zero-crossing flip and the
`W_RAIL` saturation). Activations are approximated as signed floats for now. Full analog realism
(leakage, quantization, PVT) is a deferred phase. → `core_logic.md §10`.

**Q13. `ControlUnit` is one class for ColumnGroup, Lobe, and Brainstem. So they share memory/state?**
No — they're **separate physical processors**, each with its own bus, ROM, counters, clock. One class =
**shared RTL**, not a shared processor. Two `ControlUnit` instances talking via `parent_weight` are two
chips on a bus, not two objects sharing a list. → `core_logic.md §11`.

**Q14. Why a contiguous *start pointer* for the boundary instead of just binding each cap to a slot?**
Because the boundary is a bus transaction (Q1/§6). A child's I/O is a **contiguous block**, so one
address + auto-increment locates it — cheaper, and physically honest (a real bus is a contiguous span you
connect to or don't; you can't teleport to an arbitrary line). Per-cap binding stays *inside* a scope
(where the ALU needs any-to-any); start-pointers cross *between* scopes. → `core_logic.md §6, §8`.

**Q15. The Brainstem looks almost identical to a Lobe now. What makes it special at all?**
Almost nothing — that's the point of the recent unification. It's the same instruction-walking machine.
The *only* top-unique parts: it owns no Scaps/ALUs (its program is pure child-dispatch), and it
**synthesizes the backward pulse** via the loss engine because there's no parent to hand it one. Plus the
off-chip sample loop. → `concept.md`, `brainstem.py`.

---

## Part C — "Why is the *result* like this?" (about the experiment, not the wiring)

**Q16. Does it learn? What's the deal with `run_xor`?**
The harness is faithful and runs. The lean baseline (broadcast pulse + single global feedback + momentum)
does **no hidden-layer credit assignment** *by construction*, so it can only fit a (near-)linear model —
the discrete XOR table is beyond a single Ganglion this way (the author found even linear regression breaks
on that constraint). So the author **linearized `run_xor`** for pre-Phase-2 play (and noted how the
cap-range and the last-layer activation bound accuracy). It is intentional exploration — **not** a bug and
**not** an H1 verdict; the formal test is Phase 2. The recorded remediation if the lean baseline stalls is
per-level credit (diffusion). → `context.md §5/§7`.

**Q17. What's the supply rail (`W_RAIL`) for?**
Early on, *without* a rail the weights ran away to NaN — momentum is both the contribution *and* the update
scale, so it's a positive-feedback loop to infinity. Adding §6.6 Physical Saturation (now `W_RAIL` in
`scap.py` — a first-pass clamp + charging slowdown) fixed it. This empirically confirmed that §22 #14
(Physical Saturation) is load-bearing, not optional. Full analog charge dynamics are still deferred.
→ `context.md §6/§7`.

---

## Part D — the meta-question

**Q18. If the Python hides this much hardware, why not just write it in Verilog?**
Because the *design is still moving* (we've reverted decisions many times — see `context.md §4`), and
Python lets us explore the architecture and run real experiments (XOR, loss curves) at a speed Verilog
can't. The deal we strike: keep the **structure** hardware-faithful (scope walls, mux, start-pointers,
instruction stream, the wiring rule) and abstract only the **mechanics** (bus protocols, clocks, analog).
`core_logic.md` is the contract that keeps the abstraction honest — so that when the design freezes, the
Python *is* a netlist someone can hand to an RTL/AMS flow without re-deriving the chip.

---

_When you hit a new "wait, what?" while reading the code — write it here. This file is the cheapest way
to stop the next reader (or the next model) from mistaking our clean Python for actual software._
