# `src/concept.md` — From Spec to Code Base: The Intuition

> **What this file is.** The *story* of how the locked architecture in `../../draft5.1-1.md` becomes a
> buildable code base. Intuition first — every move is motivated before it's stated. Exact class shapes
> live in `code_concept.md`. Algorithms are black boxes marked `[ALGO — deferred]`.
>
> **Prerequisite.** Read `../../draft5.1-1.md` §2 + §3 first. The spec is locked; §22 is non-negotiable.
> One honest heads-up: our **baseline learning rule is leaner than draft5.1 §2** — see §8. That's a
> deliberate, recorded simplification, not a drift.

---

## How to read this (and the three things that will confuse you)

Read **top to bottom.** Each section earns the next; the surprise in §3 won't make sense without §2.
Three questions will nag a spec-reader; each is answered where it lands:

1. **"Where did all the modules go?"** → §3.
2. **"Where's the Current Mirror / measurement caps / per-weight credit routing?"** → §5, §6, §8.
3. **"Why is a *ControlUnit* the whole show?"** → §2–§3.

---

## 1. What the spec promised (one minute)

draft5.1 is a brain-shaped analog substrate: weight cells (**Scaps**) wired into **Ganglia** (2-3-3-2),
chained into **Columns**, branched into **Lobes**, topped by a **Brainstem**. It learns *without
gradients*: the substrate measures, for free, how much current each wire carried on a forward pass
(`|a·W|`), and uses that as credit. Four promises: **online, sparse, continuous, weights-stay-on-chip.**

This file is *how we build it in Python without lying about the hardware.*

---

## 2. The first wall: you cannot build it one-for-one

Drawn literally, the chip is mostly ALUs and wires — the expensive parts — copied thousands of times.
So we make the move every processor makes: **share the expensive part, schedule the work.**

- **One ALU serves many** — one Ganglion-ALU steps through hundreds of Ganglia, one at a time.
- **An instruction list says the order** — "Ganglion 5, then 6, then Translate 1, …"
- **Capacitors hold the in-between values** — a step writes a numbered cap; a later step reads it.

The instant you do this, **the network's shape stops living in wires and starts living in data.** And a
new thing must exist to hold the list and drive the shared ALU: a **ControlUnit.** It's about to eat the
whole architecture.

---

## 3. The great collapse: almost everything *is* the ControlUnit

Once a ControlUnit sequences everything by reading ids, ask: what does a "Ganglion" object need to *do*?
Nothing — it doesn't compute (the ALU does), doesn't route (the instructions do), doesn't hold anyone
else's state. It's just *29 weight cells that share a name.* So it collapses to an **id**. Same for a
Translate. A Column was never more than "these Ganglia, in this order" — already encoded by the list.

> ⚠ **Confusion #1.** Columns and Lobes didn't vanish — they became *shapes the instruction list builds*,
> not code objects. Real the way a melody is real: in the arrangement, not as a brick. **Real but invisible.**

Only **three kinds of thing are alive in the code:**

1. **The Scap** — the storage atom (millions, dumb).
2. **The ALU** — a shallow compute engine (a few, shared, expensive).
3. **The ControlUnit** — the sequencer that owns the instructions, the bus, the caps, and the timing.

> ⚠ **Confusion #3.** The ControlUnit dominates *because topology became data.* The only real hardware
> left is storage, compute, and a thing that reads a list. **ColumnGroup, Lobe, and Brainstem are all
> just ControlUnits** — same machine, different instructions and ALUs.

---

## 4. The Scap — momentum is the whole brain of learning

A Scap is one synapse and the only physical thing below a ControlUnit — a register that answers a few
broadcast signals. It holds a **weight** (magnitude + sign bit), a **forward-sign** bit, and the crucial
one, a **momentum capacitor**.

**Momentum is the entire per-Scap learning signal.** During the forward pass the substrate measures how
much this wire carried (`|a·W|`) and folds it into momentum. During backward, the Scap changes its
weight in proportion to that momentum. There is no second "how much should I learn" channel anywhere —
**momentum is it.** Hold that: if `|a·W|` is a poor proxy for relevance, nothing else saves us.

It answers three signals: **GetWeight** ("drive your weight out"), **SetMomentum** ("take what's on the
bus into momentum"), **Update** ("change your own weight now"). Note: the Scap does **not** compute its
own `forward_sign` — it has no access to its input activation. The ALU computes it and hands it back
(§6); the Scap just latches it on `SetMomentum`.

---

## 5. The bus — how one ALU talks to a group of Scaps

The ALU and a group of Scaps share **one bus (a weight lane + a sign lane), used in two phases of time:**

1. **GetWeight phase** — the ControlUnit names the active group (`target_group`); the matching Scaps each
   drive their slot: **magnitude → weight lane, weight-sign → sign lane.** The ALU reads them.
2. **SetMomentum phase** — the ALU drives the same wires *back*: **contribution → weight lane,
   `a·W` sign → sign lane.** The selected Scaps latch contribution into momentum and the `a·W` sign into
   `forward_sign`.

Two wire-savers: Scaps in a group share one id (the **slot** disambiguates them), and the ControlUnit
selects a group by broadcasting one `target_group` — a Scap acts only when its group matches.

> ⚠ **Confusion #2, half-answered.** There is no separate measurement bus. The spec's measurement caps
> fold into this: the ALU computes each Scap's contribution and writes it straight back on the weight
> lane for `SetMomentum`. Both lanes are **bidirectional in time** — Scap-out on GetWeight, ALU-in on
> SetMomentum. (The other half — the Current Mirror — is §8.)

---

## 6. The ALU — the expensive part, doing two jobs at once

The ALU is a shallow, stateless transform (`GanglionALU` is the hardwired 2-3-3-2 with biases +
activation; `TranslateALU` is an `n→m` matmul). The ControlUnit hands it input/output cap ids and powers
it. It does **two things in one pass:**

- **Computes the forward result** — charges the output capacitor to high precision (~95%, because the
  next layer depends on it).
- **Measures each line's contribution** *while* the output is charging — and writes that back (with the
  `a·W` sign) for `SetMomentum`.

This double duty is exactly why the ALU is the costly element — it must sit and wait for charge. And a
neat consequence: the contribution only needs ~80% precision, because **that 80% is applied uniformly to
every line across the whole batch — so it cancels into a constant learning-rate scale, with no per-weight
bias or tilt.** Cheap measurement is fine.

---

## 7. I/O between layers: capacitors + a two-step handshake

Sealed scopes pass data through **capacitors**, in two scopes: *columngroup-level* caps between steps
inside a group; *lobe-level* caps between groups. A parent runs a child in two named steps:

1. **SetDataBus** — the parent binds *its own* caps onto the child's input/output boundary (this is how
   several ColumnGroups talk: they share lobe-level caps, bound in turn).
2. **SetActivate** — raise the child's `run`; the child reads its bound input and runs to completion,
   then raises **done**. The parent steps to its next instruction.

So there are exactly **two ways anything talks:**

- **ControlUnit → its own ALU: timed.** The ControlUnit decides the run length; the ALU never reports back.
- **ControlUnit ↔ ControlUnit: handshake.** `run` down, `done` up; the parent never reaches inside.

And one habit that keeps it debuggable: **everything is named by id; the ControlUnit is the lookup.**
Instructions name an `alu_id`, a `weight_model_id` — the ControlUnit resolves each to the real thing.
A hair of indirection now; an easy future upgrade to two/three parallel buses later.

---

## 8. Learning without gradients: broadcast + momentum

The big one. The spec routes credit with a Current Mirror that divides each loss into normalized
per-Scap shares. **Our baseline does not.** Here it is, and then the honest divergence note.

> ⚠ **Confusion #2, fully answered.** The per-weight credit routing is *replaced by momentum.* The
> backward pass is a single broadcast pulse, and each Scap weights it by its own momentum.

**Loss becomes a pulse.** The Brainstem turns the loss scalar into a number (a pulse "length"). It
broadcasts. As the pulse passes each scope, a **PWM module scales it by that scope's learning-rate knob**
— default ~1.0, present so a future fast-Cortex and slow-Hippocampus can run at different rates from the
same loss. The (possibly scaled) pulse reaches every Scap, which updates:

```
direction   = forward_sign XOR feedback
weight     -= pulse × momentum × direction
```

**That's the whole rule.** `pulse` is the global loss magnitude (× any scope learning-rate); `momentum`
is the per-Scap credit; `forward_sign` (from the ALU, §6) sets direction. No routing wires, no per-Scap
shares, no distribution memory.

> **The recorded divergence (§22 watch).** This *broadcast + momentum* rule is **leaner than
> draft5.1 §2**, which routes loss by *normalized per-child shares* (the Current Mirror dividing
> `loss × contribution/Σcontribution` at every level) and locks **§22 #3 (hierarchical diffusion as the
> routing mechanism)** and **§22 #6 (additive loss conservation)**. We drop the per-level normalization:
> every Scap gets the full pulse scaled only by its own momentum, so loss is *broadcast and locally
> weighted*, not conserved as shares. This is deliberate — it's the clean resolution of the spec's own
> §2.4 worry ("routing-update coupling: the same `|a·W|` does both routing and magnitude") by cutting
> the routing and keeping the magnitude. **We run the lean baseline first; the full normalized
> Current-Mirror diffusion is a future layer to add only if the lean version won't converge.**

---

## 9. Why forward and backward are different machines (the cost inversion)

In ordinary ML the forward pass is cheap and backward (backprop) is the expensive thing. **We inverted
it.** Forward is where all the cost lives — the ALU sits and waits for charge, group by group,
sequentially. Backward is one broadcast pulse, parallel, nearly free. The reason: **learning rides the
measurement we already paid for** in the forward pass — momentum is filled as a *byproduct* of computing
the output. Forward is bounded by how many steps you run; backward by hierarchy depth, not weight count.
Two timings, two code paths. Don't fuse them.

---

## 10. The instruction: the one piece of data that wires everything

Everything above comes down to one record — the thing you'll type:

```python
@dataclass
class Instr:
    input_id:  list[int]    # cap ids to read
    output_id: list[int]    # cap ids to write
    alu_id:    str          # which ALU  (id → ALU, resolved by the ControlUnit)
    weight_model_id: str    # which Scap group supplies the weights (a Ganglion / Translate id)
```

A network is a **list** of these — two Ganglia in parallel, merged by a 4→2 Translate:

```python
program = [
    Instr([0, 1],       [2, 3], "g_alu",     "G1"),
    Instr([4, 5],       [6, 7], "g_alu",     "G2"),
    Instr([2, 3, 6, 7], [12,13], "t_alu_4x2", "T1"),
]
```

The *only* thing that says "G1 and G2 feed T1" is the cap ids — T1 reads `[2,3,6,7]`, where G1 and G2
wrote. Caps are the nets, the list is the netlist. **To rewire, you edit data, not modules** (series vs
parallel, fan-out, a different shape — all just different ids). Nothing in the Scap, ALU, or bus ever
changes. Hand-write these lists now; a small compiler emits the same lists later. The hardware is frozen;
the program is soft.

---

## 11. ColumnGroup is packaging — and the hierarchy is just ALU stages

The ALU is *very* expensive: a full 2-3-3-2 op-amp, 29 contribution-measurement modules, the internal
cap holds, the momentum compute. You can't afford one per Column. So a **ColumnGroup bundles many
Columns to share one ALU set** — that is its *only* reason to exist. It's physical packaging, not a new
level.

And here's the clean part: **credit granularity is set by how many ALU stages you run, not by a separate
normalizer.** Want per-column normalization (the spec's Column-level diffusion)? Add another ALU layer —
a translate stage whose Scaps carry their own momentum. More stages = finer credit. So the spec's "five
levels" become "five processing stages," and the control hierarchy and the credit hierarchy are the same
thing seen twice. The ColumnGroup is just where the stages physically time-share an ALU.

---

## 12. The shape of the code (and where to start)

`code_concept.md` has the detail. Expect **three live classes** plus data:

- **Scap** — weight, sign, momentum; answers GetWeight / SetMomentum / Update.
- **ALU** — shallow, stateless transform.
- **ControlUnit** — *one class*, reused as ColumnGroup / Lobe / Brainstem; owns the program, bus, caps,
  PWM, timing.
- **Data:** the instruction list, `id → object` dicts, `LocalCapacitor`s.

**Build a vertical slice first.** SLICE-1 (one Ganglion learning XOR) needs: Scap → GanglionALU → one
ControlUnit (one group) → minimal Brainstem, with backward = broadcast pulse × momentum (scope LR = 1).
Only *after* it learns do you add the Lobe, multiple groups, extra ALU stages, and the real PWM.

---

## 13. Deferred — and two caveats to interpret early runs

- **All algorithms** — every `[ALGO]`: forward math, momentum EMA, the update equation, the loss.
- **Caveat — saturation is implemented but simplified.** The spec's main defense against winner-take-all
  (H10) is *physical saturation* — weights near the supply rail self-limit. `scap.py` now has a first-pass
  rail (`W_RAIL`: a hard clamp + a `dV/dt ∝ (V_rail − V_cap)` slowdown); **without it the model diverged
  to NaN**, which confirmed §22 #14. Full analog charge dynamics are still deferred. (Loss conservation,
  by contrast, isn't even a goal in the lean baseline — see §8.)
- **Caveat — the lean baseline ≠ the spec's diffusion.** Per §8, we test *broadcast + momentum*, not the
  normalized Current-Mirror diffusion. If H1 wobbles, the full diffusion is the first thing to add back.
- **Also deferred:** real clocked/multi-rate PWM, the second Lobe + Limbic recurrence, PVT realism,
  parallel ALUs, bit-level routing.

---

_This file is the intuition; `code_concept.md` is the implementation. When they disagree, fix whichever
is wrong — and keep this one readable, because it's how the next person recovers the whole picture in ten
minutes instead of five hours._
