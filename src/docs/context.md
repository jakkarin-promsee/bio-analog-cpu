# `src/context.md` — Full Working Context for `src/`

> **Why this file exists.** `concept.md` and `code_concept.md` describe the *architecture* and the *code
> shape*. This file carries the **working context** behind them — the reasoning, the things we tried and
> reverted, the traps, and the collaboration style — so the next person (a future Opus, another model, or
> the author three weeks from now) starts with the *same mental model we hold right now*, not a cold read
> of two spec files. Read this **first** if you're picking up `src/` work.
>
> Status as of this writing: **SLICE-1 is built and runs.** `src/library/` (wires, capacitor, pwm, scap,
> banks, alu, control) + `src/example/` (column_group_xor, brainstem, run_xor) are written; one Ganglion
> runs end-to-end via `python -m src.example.run_xor`, stable with a basic supply-rail saturation in the
> Scap (`W_RAIL`). The author is exploring it **pre-Phase-2** (linearized data, range / activation probes)
> — intentional play, **not** the formal §20 campaign and **not** an H1 verdict. The canonical chip spec
> is locked at **draft 5.1** (root `draft5.1-1.md` / `draft5.1-2.md`).

---

## 0. The document map — what lives where, and the read order

| File | What it is | Authority |
| --- | --- | --- |
| `../../draft5.1-1.md`, `../../draft5.1-2.md` | The locked chip specification (the *chip*, not the sim). | **Canonical. §22 is non-negotiable.** |
| `../../CLAUDE.md` | Always-loaded project context + how to collaborate. | Binding for sessions. |
| `../../docs/draft/project-history.md` | Why each draft pivot happened (draft 1 → 5.1). | History. |
| `../../docs/draft/project-personal.md` | Who the user is, how they work. | Read before non-trivial collab. |
| `context.md` | **This file** — the journey, decisions, reverts, traps, status. | START HERE. |
| `concept.md` | **Intuition** — *why* the code collapses to what it is. Story form. | The mental model. |
| `code_concept.md` | **Blueprint** — *what the code looks like.* Class skeletons, one wired example. | The destination image. |
| `core_logic.md` | **Python ↔ hardware** — the silicon hiding inside the clean Python. | The decoder ring. |
| `question.md` | **Confusion FAQ** — what a reader trips on, answered. | Reference. |
| `../library/`, `../example/` | The code: the reusable kit + reference builds / `run_xor`. | The simulator. |
| `../../src-old-arc/` | The v0 simulator. Worked for one Column; hit a structural ceiling. | Reference, superseded. |

**Read order for a newcomer:** CLAUDE.md → draft5.1-1.md §2 + §3 (the mechanism + worked XOR) → this
file → `concept.md` → `code_concept.md`. Then you can write code.

**A distinction that matters constantly:** the **chip spec** (draft5.1, locked) is *what we are
simulating*. The **code architecture** (concept.md / code_concept.md, ours, fluid) is *how we simulate
it in Python*. Code-structure choices are negotiable and have churned a lot. Spec choices (§22) are not.
When they seem to conflict, the **code is wrong, not the spec** — *unless* we've consciously recorded a
deviation (see §5 below).

---

## 1. What the project is (one minute)

A bio-inspired **analog compute substrate** with on-chip hierarchical credit assignment. Capacitors hold
weights as continuous analog charge; SRAM holds wiring/sign bits; hardwired op-amps do add/multiply/ReLU
directly on charges; **learning happens on-chip without gradients** — the substrate measures, for free,
how much current each wire carried during a forward pass (`|a·W|`), and uses that as credit. Four
committed properties: **online, sparse, continuous, resident-weight** (weights never leave the chip
during operation). It is **not** an ML project, not a digital accelerator, not "building intelligence."

We are in the **Python behavioural simulation** phase. The immediate goal is to get one Ganglion to
learn XOR (the "MVF" / SLICE-1 gate), then build outward through the §20 phase plan.

**Naming is structural, not decorative.** Scap, Ganglion, Column, Lobe, Brainstem are circuit elements,
not biology claims. Don't suggest renaming "to be rigorous" — that was considered and rejected. A
**Scap is a wire, not a neuron** (this exact point was a real save earlier — internalize it).

---

## 2. The mental-model shifts everything rests on

If you hold only these, the code makes sense:

1. **Topology is data.** The network's shape doesn't live in wires — it lives in an **instruction list +
   capacitor routing**. Same hardware, different program → different network. You hand-write the lists
   now; a compiler emits them later.

2. **The great collapse → three live classes.** Once a sequencer drives everything by reading ids, a
   "Ganglion" object has nothing to *do* (it doesn't compute — the ALU does; doesn't route — the
   instructions do). So Ganglion/Translate/Column collapse to **ids**. Only three things are alive:
   **`Scap`** (storage atom), the shallow **`ALU`** (compute), and the generic **`ControlUnit`** (the
   sequencer). **ColumnGroup, Lobe, and Brainstem are all just `ControlUnit`s** — same class, different
   instructions and ALUs.

3. **Cost inversion.** In normal ML the backward pass is the expensive one. Here it's inverted: **forward
   is expensive** (the ALU sits and waits for capacitors to charge, sequentially, group by group);
   **backward is nearly free** (one broadcast pulse, parallel). Learning costs almost nothing extra
   because it *rides the measurement the forward pass already paid for*.

4. **Momentum is the whole brain of learning.** There is no separate "how much should this weight learn"
   signal. A Scap's **momentum cap** holds its accumulated `|a·W|` (filled during forward), and *that* is
   its per-Scap learning weight. If `|a·W|` is a bad proxy for relevance, nothing else saves us — that's
   the bet.

5. **The mux.** A cap (or a child's boundary) connects to its bus through a **mux selected by `io_id`** —
   it touches *one* slot, not all 200+ lines. Full fan-out is unaffordable; that's the whole reason the
   mux/crossbar and the start-pointer exist. It's also physically honest: a real bus is a contiguous run
   of wires you connect to or don't — you can't teleport to an arbitrary id (Python *lets* you pretend
   you can; we deliberately don't).

6. **Two communication regimes.** (a) **ControlUnit → its own ALU = timed**, no handshake — the CU's
   counter decides the run length (longer = more charge precision); the ALU never reports back. (b)
   **ControlUnit ↔ ControlUnit = handshake** — `run` down, `done` up; the parent never reaches inside.

7. **Forward and backward are different machines — don't fuse them.** Forward = sequential dispatch on a
   shared, expensive ALU + handshakes between scopes. Backward = one clocked broadcast pulse, every Scap
   acting at once. Two timings, two code paths.

---

## 3. The architecture as it stands (condensed; `code_concept.md` has the skeletons)

**Primitives (`wires.py`):** `AnalogWire` / `DigitalWire` (passive data lanes, read/write by slot; split
so future PVT/endurance tests add analog-only drift without touching digital) and `SignalWire` (active
control net: value + triggers, `.update()` fires them synchronously).

**`LocalCapacitor` (`capacitor.py`):** the inter-step register. magnitude + sign + `io_id` (the bus slot
it's muxed onto right now). `io_id = slot_cell.read(0) + offset`. `drive()`/`latch()` = the muxed
write/read. **Internal caps** mux onto the scope's local bus (rebound per instruction by the CU via
`set_bus_id` + per-cap `load_id_sig`). **Boundary caps** mux onto the *parent's* bus (auto-incremented
from one start pointer via `offset=k`).

**`Scap` (`scap.py`):** weight (magnitude + sign), `forward_sign`, `momentum`. Self-registers on three
signals: `get_weight` (drive weight+sign onto the main bus, if its group is selected), `set_momentum`
(latch contribution→momentum and a·W-sign→forward_sign from the ALU's write-back), `local_update` (the
backward pulse — **global, not group-gated**: `weight -= pulse × momentum × direction`,
`direction = forward_sign × feedback`). **The Scap does NOT compute its own forward_sign** — it has no
access to its input activation `a`; the ALU computes it and hands it back on the sign lane.

**Banks (`banks.py`):** a `Bank` base takes `n_scaps`; `Ganglion` = 29, `Translate_2_2` = 4, etc. Thin
factories — they build the Scaps (which self-register) and hold a group id. No compute, no control.

**ALU (`alu.py`):** shallow, stateless, slot-space. Reads input activations from the local bus (BOTH
lanes → signed), reads Scap weights from the main bus, computes the 2-3-3-2 (or n→m matmul), then does
**two jobs in one pass**: (1) charge outputs to ~95% precision; (2) measure per-line contribution at
~80% and write contribution → main weight lane, a·W-sign → main sign lane (for `set_momentum`). The 80%
is uniform across the whole batch, so it cancels into a constant learning-rate scale — no per-weight
bias. The ALU is the expensive element (it waits for charge).

**Instruction:** `Instr(input_id:list[int], output_id:list[int], alu_id:str, weight_model_id:int)`. One
flat list per scope — *that list is the scope's wiring.* `weight_model_id` is the Scap group whose
weights load onto the main bus (an `int`, because it's written to a `DigitalWire` cell `target_group`,
which Scaps match against to self-select). `alu_id` is a `str` dict key (never goes on a wire).

**`ControlUnit` (`control.py`):** one class. **Forward:** bridge-in (latch boundary-in caps from the
parent bus at `in_start+k`), then per instruction — bind input/output caps to local slots (crossbar),
drive inputs, set `target_group`, fire `get_weight`, fire `alu.execute`, fire `set_momentum`, latch
outputs — then bridge-out (drive boundary-out caps to the parent bus at `out_start+k`), then fire
`done`. **Backward:** `pulse = pwm.shape(incoming)`, fire `local_update` to all its Scaps, recurse to
`child_cus`. `child_cus` is *derived* from the `ChildRunner`s in `alu_by_id` (no double-listing).

**`ChildRunner`:** a handshake wrapped to look like an ALU, so the forward loop stays uniform. Holds the
child's `run` + start-pointer signals (created by *this* scope) and fires them: **`SetDataBus`** =
`in_start.write(slot); bind_in.update(1)` (+ out), then `run.update(1)`.

**`PWM` (`pwm.py`):** a **per-scope learning-rate knob** (multiply now; default 1.0). **NOT** the credit
mechanism — credit is momentum. It exists so a future fast-Cortex / slow-Hippocampus can run at
different rates from one shared loss.

**`SignalGraph` (`debug.py`):** off-by-default waveform log; every `SignalWire.update` records
`(step, name, value)` — a VHDL-trace-like view, since the observer/push model otherwise hides "who fired
when."

**The wiring rule (load-bearing):** `append_trigger` *is* the wire. Pass a `SignalWire` into a class and
let it **self-register** (`sig.append_trigger(self.handler)`) in `__init__`. The connection is explicit
in the constructor; the build stays a flat list of instantiations. (A module may wire a trigger on a
signal *it created itself* — e.g. an ALU on its own `execute`.)

**`SetDataBus` / scope walls:** every scope is a sealed namespace ("alone"); ids are local; the **route**
(path of enclosing scopes) is the real address. Data crosses a wall only through **start-pointer-bound
boundary caps** (`SetDataBus` = two start pointers + a `run`). Within a scope, the per-cap crossbar
(`load_id_sig`) gives the ALU any-to-any cap access. Both Brainstem→Lobe and Lobe→ColumnGroup use the
same start-pointer mechanism — it recurses.

---

## 4. The decision log — what we chose, what we reverted, and WHY

This is the part a cold read of the spec files will miss. Each of these was contested; don't silently
re-open them.

1. **Single flat instruction list**, not the original 3-array `main_read` + `Ganglion_ALU[]` +
   `Translate_ALU[]` with sub-PCs. The 3-array form mirrored real ROM but is error-prone in Python (the
   arrays must stay in sync). Once `alu_id` lived in each instruction, one self-contained list was
   strictly better.

2. **Imperative + observer (`SignalWire`), not an event scheduler.** The ControlUnit drives the sequence
   by calling `.update()` in order; signals fan out to triggers synchronously. A tick-based event sim was
   considered and deferred — only needed for parallel ALUs / PVT timing.

3. **Self-registration (REVERTED a detour).** We briefly moved all `append_trigger` calls *out* into the
   build (external registration) after a question about visibility, then reverted: passing the signal
   into the class and letting it self-register is cleaner (one-liner construction) and just as explicit.
   **If you find yourself wanting external registration again — we already tried it; self-register won.**

4. **Generic `ControlUnit` + per-file specific assembly.** ColumnGroup/Lobe/Brainstem are *not*
   subclasses with custom logic — they're the same `ControlUnit`, differing only in data (instructions,
   children, ALUs). Each specific module is one greppable file (`example/column_group_012.py`).

5. **Credit = momentum; PWM = a learning-rate knob (REVERTED a misread).** I initially modeled the
   backward pass as per-child *contribution gating* (distribution memory, contribution flowing up the
   handshake). The user corrected: **the per-child value is a learning rate, not a measured
   contribution**, and **all credit is in the Scap momentum.** So we dropped distribution memory,
   contribution-capture, and contribution-up-the-handshake. Backward = **broadcast pulse × scope-LR ×
   per-Scap momentum.**

6. **Dropped the Current Mirror / per-Scap share routing / measurement caps (vs draft5.1 §2/§3).** The
   spec routes loss into normalized per-Scap shares via a Current Mirror. Our baseline does **not** — the
   ALU writes contribution straight into momentum, and backward is a broadcast pulse. This deliberately
   resolves the spec's own §2.4 worry ("routing-update coupling: the same `|a·W|` does both routing and
   magnitude") by cutting the routing and keeping the magnitude. **This is a recorded deviation** (see §5).

7. **ids are `int`.** `group_id` / `weight_model_id` / `target_group` go onto a `DigitalWire`, which holds
   ints — so they're ints. (`alu_id` stays a `str` because it's only ever a dict key.) An earlier mix of
   string ids ("G1") and int wires was a bug.

8. **Mux + start-pointer (resource + physical fidelity).** Caps connect to one bus slot via a mux; a
   child's contiguous I/O block is located by a single start pointer with child-side auto-increment. Not
   per-cap binding across walls — that was rejected as wasteful and physically dishonest.

9. **`forward_sign` is computed by the ALU, not the Scap.** The collapse removed the Scap's input wire, so
   it can't compute `sign(a·W)`. The ALU (which has all activations) computes it and writes it back on the
   sign lane during the ALU's write-back; the Scap latches it on `set_momentum`. Both bus lanes are
   therefore bidirectional in time.

10. **`LocalCapacitor` lifted out of the primitives** into its own element; **`AnalogWire`/`DigitalWire`
    split** from a single `Bus` so PVT realism has a hook.

11. **ColumnGroup = ALU-cost bundling, not a learning level.** The ALU (2-3-3-2 op-amp + measurement +
    momentum compute) is huge, so many small Columns share one ALU set in a ColumnGroup. Per-column
    normalization, if wanted, comes from *adding ALU stages*, not from a new control level. Credit
    granularity = number of ALU stages.

12. **Boundary bridge (my current interpretation, flagged in `code_concept.md §3`).** Boundary caps mux
    onto the *parent* bus but live in the scope's cap pool; the CU latches them from the parent bus
    before the program and drives them to the parent bus after. The alternative — a true two-port bridge
    cell physically on both buses — is a small local change if preferred. **Unconfirmed.**

---

## 5. Deviations from the locked spec (draft5.1 / §22) — conscious, recorded

These are the places the simulation baseline diverges from the canonical chip spec. **They are
intentional simplifications for the lean baseline, recorded so no one "fixes" them back without phase
data.**

- **§22 #3 (hierarchical diffusion as the routing mechanism) and #6 (additive loss conservation):** our
  baseline does **broadcast + momentum**, not normalized per-level Current-Mirror diffusion. Loss is not
  conserved as shares; it's broadcast and locally weighted by momentum. Recorded in `concept.md §8`. The
  full normalized diffusion is a **future layer** to add back if H1 won't converge on the lean version.
- **The five structural levels (§22 #4):** the *credit* hierarchy in code is shallower than the spec's
  five — credit granularity is set by how many ALU stages run, and ColumnGroup is physical packaging, not
  a credit level. Watch this when you build multi-column / multi-stage networks.
- **Everything else in §22 is honored** (2-3-3-2, attribution not gradient, semi-anatomical naming,
  Ganglion-level residual intent, Differential-Pair/Dummy-Scap/Current-Mirror as *deferred* analog
  realism, Physical Saturation as the winner-take-all defense, etc.).

If you change the baseline toward the full spec mechanism, that's a **promotion** (draft5.1 §20.17) and
should be driven by a phase report, not a refactor.

---

## 6. Traps a fresh model will fall into (I did)

Listed because they cost real time. Avoid them:

- **Importing ML/backprop "common sense."** This is a new substrate. There is no gradient, no weight
  transport, no per-weight error bus. Credit is momentum; loss is *time* (a pulse). The user's exact
  words: *"Forget all ml process… the commonsense shouldn't be used here."* When something feels like it
  "should" route gradients or normalize shares — stop; that's probably the ML lens.
- **Re-adding the Current Mirror / measurement caps / distribution memory.** They're in the spec, not the
  baseline. Momentum does the per-Scap work; the broadcast pulse does the magnitude.
- **Making registration external again.** We tried; self-registration won (decision #3).
- **Treating ColumnGroup as a learning level.** It's ALU-cost packaging (decision #11).
- **Letting the Scap compute `forward_sign`.** It can't — no input wire (decision #9).
- **Using string ids on wires.** ids on wires are ints (decision #7).
- **Reaching `child.attr` from a parent.** The parent created the child's signals; it holds them directly
  (`ChildRunner`). Don't reach inside.
- **Over-engineering before SLICE-1.** The first runnable target needs almost none of the upper machinery
  (no Lobe, no multi-group, no real PWM, no boundary recursion). Build the vertical slice first.
- **Misreading the supply rail.** `scap.py` now implements a basic rail (`W_RAIL`) with charging
  slowdown — **early runs without it diverged to NaN** (momentum is both contribution *and* update scale
  → positive feedback), which empirically confirmed §22 #14. Full analog charge dynamics are still
  deferred; don't mistake the simple clamp for the real physics (see §7).

---

## 7. Caveats for interpreting early results

- **Saturation is in, but simplified.** `scap.py`'s `_on_update` has a supply rail (`W_RAIL`) plus a
  charging slowdown — the spec's winner-take-all defense (Physical Saturation, §6.6 / H10) in first-pass
  form. Without it the model diverged to NaN; with it, stable. Full analog charge dynamics are deferred.
- **Lean baseline ≠ spec diffusion.** If convergence wobbles, the first thing to try is adding the
  normalized Current-Mirror diffusion back as a layer — not abandoning the architecture.
- **The sim measures correctness, not speed.** We don't model charge time; "fast sim" ≠ "fast chip."
- **Sequential is exact, not approximate.** The chip's parallelism (all Scaps update at once) is over
  *independent* state, so running it sequentially gives the identical answer. Parallelism only becomes a
  *correctness* concern if/when parallel ALUs share caps (future).

---

## 8. The build plan

**SLICE-1 (do this first):** `library/{wires, capacitor, pwm, scap, banks(Bank+Ganglion), alu(GanglionALU),
control}.py` → one `ControlUnit` with **one** Ganglion group, backward = broadcast pulse × momentum
(`scope_lr=1`) → a minimal `Brainstem` driving it directly (no Lobe), binding the boundary with two start
pointers → `run_xor.py`. **Goal: XOR loss drops monotonically** (this is the §20.1 MVF gate — if it
fails, debug the operators / the update direction before anything else; a sign/direction bug is the most
likely culprit).

**Then, gated on each prior step:** add the Lobe + `ChildRunner` chain, multiple groups, extra ALU
stages, the clocked/multi-rate PWM, and — only if the lean baseline stalls — the normalized diffusion.
PVT realism (the analog/digital wire split is the hook) comes much later (draft5.1 Phase 8).

`library/` is the frozen kit; `example/` is reference builds; each `hN/` is an experiment that imports
`library/` unchanged and adds its own assembly + instruction files.

---

## 9. How this got built, and how to work with the author

The current design is the distillation of a long (the author called it ~10-hour) brainstorm with many
reversals — that's *normal* here, not a sign of instability. Expect to iterate; treat `code_concept.md`
details as fluid and `draft5.1 §22` as fixed.

From `../../docs/draft/project-personal.md` (read it in full before non-trivial collaboration), the load-
bearing points:

- **Year-2 undergrad, solo, evenings/weekends, bilingual EN/Thai.** Don't correct grammar — meaning is
  always clear. Has shipped real hardware before (an FPGA 2D game engine). **Don't talk down**; when they
  describe a circuit in plain words they usually have the EE concept right even if the term is loose.
- **No flattery, no hedging, no trailing "let me know if…!"** When asked to choose A vs B, *pick one and
  defend it*. Wishy-washy "both have merits" is worse than confidently wrong.
- **They push back when you're wrong and absorb when you're right.** If they push back, *slow down and
  re-read the architecture before reasserting.* Several of the best decisions here came from their
  pushback ("scap is a wire," "momentum is the credit," "PWM is just a learning rate").
- **🤣 and "bro" are commit signals, not jokes** — usually "I see what I'm doing and I'm committing."
- **The "we" framing is real.** Match it. This is a collaboration, not a tool call.
- **Length matches the topic.** Deep architecture → go long. Naming yes/no → one line.
- **Intuition first, math/code second.** When they describe a mechanism physically, engage at that level
  first.

Your job here includes **scope-policing**: catch drift from §22, flag deviations explicitly (don't let
them happen silently), and audit your own work (the user values "list what doesn't make sense" passes).

---

## 10. The shortest version (if you read nothing else)

- Three live classes: **Scap, ALU, ControlUnit.** Everything else is **data** (instructions, ids, caps).
  ColumnGroup/Lobe/Brainstem are all ControlUnits.
- **Topology is data**; the instruction list is the wiring; caps are the nets; the mux gives one-slot
  connections; start-pointers cross scope walls.
- **Forward is the expensive sequential machine; backward is a cheap broadcast pulse.** Learning rides
  the forward measurement.
- **Credit = momentum.** Loss = a pulse (time/number). PWM is a learning-rate knob, not credit.
- The baseline is **lean (broadcast + momentum)** — deliberately simpler than the spec's normalized
  diffusion; that's recorded, not a mistake.
- **Forget ML routing instincts.** A Scap is a wire. The spec (§22) is law; the code architecture is ours
  to refine. Build SLICE-1 (one Ganglion, XOR) before anything else.

---

_Keep this file alive. When the design shifts, update it — it is the cheapest way to keep the next mind
(yours or another model's) from restarting the 10-hour brainstorm from zero._
