# Draft 4 — Bio-Inspired Analog Neural Compute Architecture

> Canonical specification. v4.0.
> Supersedes all prior drafts.
> Scope: Python simulation + math justification. Every choice must remain physically realizable in analog circuitry.

---

## 0. Reading Guide

This document describes an **analog compute substrate** for the kind of computation brains do: online, sparse, continuous-learning, in-memory. It is not a brain emulator. It is not approximate backprop. It is a different family of architecture, designed from the substrate up.

**Recommended reading order for first-time readers:**

1. §1–2 (motivation + full architecture overview)
2. §4–11 (bottom-up build: Scap → Ganglion → Column → Lobe → Limbic Loop, plus Commissure and Brainstem)
3. §12 (the learning mechanism)
4. §13 (residual connections)
5. §15 (hypotheses) to see what we claim and what we don't

The rest is reference: math, open questions, simulation plan, future work, glossary.

**If you read only one section, read §12** — attribution-based hierarchical diffusion is the project's central architectural commitment.

---

## 1. Project Framing

### 1.1 Goal in one sentence

Build a substrate where the kind of computation brains do is the *cheap* path, instead of an emulation layered on top of von Neumann silicon.

### 1.2 What this project is *not*

- It is **not** an attempt to build intelligence. "Intelligence" is too fuzzy a goal to optimize against.
- It is **not** a 1:1 copy of biology. Biology is the source of architectural patterns, not a target to reproduce.
- It is **not** another digital ML accelerator. Digital neural nets are a metaphor mistaken for the thing.

### 1.3 The four properties we want

The substrate should make all of these the natural, cheap path:

| Property | Meaning |
|---|---|
| **Online** | Weights update during operation, not in batch-offline epochs. |
| **Sparse** | Only paths that carry signal consume energy. |
| **Continuous** | Weights and signals live in capacitor voltages, not bit patterns. |
| **Resident-weight** | Weights never leave the substrate during operation. Storage and compute are the same hardware. |

"Resident-weight compute" is the technical framing. The field this belongs to is **in-memory compute (CIM)**. Earlier drafts called this property "encryption" — that term is retired.

### 1.4 Why current architectures fail at these properties

- Transformers are O(n²) brute-force pattern matching over a fixed window. Not online.
- LSTMs are closer to online thinking but locked to time-series framing.
- Even very strong models shape good output gradually across many tokens — stable pattern replay, not creative first-token output.
- Von Neumann dedicates large silicon area to branch-prediction SRAM and load/store machinery — none of it useful for continuous compute.
- GPUs widened the data pipe but didn't escape the assemble-from-scratch loop. The CPU still arbitrates.

The ceiling isn't model size. The ceiling is the substrate.

### 1.5 The bet

Real neurons are continuous. Build a continuous compute substrate where:

- **Capacitors** scatter across the die holding all weights as analog charge.
- **SRAM** is repurposed from branch prediction into wiring, sign bits, contribution accumulation, and routing.
- **ALU** is hardwired op-amps performing add / multiply / ReLU directly on capacitor charges.
- **Learning** diffuses through a hierarchy of modules using locally-measured contribution, not per-weight gradient routing.
- **Input / output** are the only external interfaces.
- **Shutdown** is the only event that serializes weights out of the chip.

### 1.6 Methodological note

> "The fast answer will destroy your creativity."

This project is built from intuition first, with literature comparison reserved for after architectural stability. Existing work (neuromorphic chips, spiking networks, three-factor learning, predictive coding, Equilibrium Propagation, feedback alignment, LRP) is treated as related work for cross-validation, not as design input.

---

## 2. Architectural Overview

### 2.1 The hierarchy at a glance

The architecture has **five structural levels** plus one controller:

```
[Controller]   Brainstem  ←→  central control, loss compute, clock management
                  │
                  ↓ global broadcast bus
[Top level]    Limbic Loop  ←→  recurrent system (Cortex + Hippocampus + Commissure)
                  │
                  ↓ per-Column local bus
[Level 4]      Lobe         ←→  multi-branch DAG composition of Columns
                  │
                  ↓ Lobe-local bus
[Level 3]      Column       ←→  sequential chain of Ganglia with translate ALUs
                  │
                  ↓ Column-local bus
[Level 2]      Ganglion     ←→  hardwired 2-3-3-2 atom of computation
                  │
                  ↓ Ganglion-local bus
[Level 1]      Scap         ←→  atom of storage (one synapse weight)
```

Each level has its own local bus carrying control signals (update, reset, feedback) to its children. The hierarchy is read top-down for control signals, bottom-up for forward computation.

### 2.2 What sits at each level

| Level | Role | Atom of | Composition pattern |
|---|---|---|---|
| Scap | Holds one synapse weight | Storage | — |
| Ganglion | Computes one axon's worth | Compute | 29 scaps wired 2-3-3-2 |
| Column | Sequential signal transformation | Mid-scale function | Ganglia chained through translate ALUs |
| Lobe | Multi-branch DAG composition | Brain region | Multiple Columns in parallel or branch structure |
| Limbic Loop | Recurrent prediction | Top-level system | Cortex Lobe + Hippocampus Lobe + Commissure |
| Brainstem | Central control | Controller | Not in the hierarchy — sits beside it |

### 2.3 One-paragraph preview of the learning mechanism

Each level stores **contribution memory** during the forward pass — how much each of its children contributed to its output. When the Brainstem computes loss at the top, the loss is broadcast and *diffuses down* through the hierarchy: each level divides the loss share it received among its children in proportion to their stored contributions, broadcasts those shares on its local bus, and the next level down does the same. After five levels of diffusion, the share reaches each scap, which updates its weight capacitor locally via PWM. No per-weight gradient is computed; no weight-transport is required. Full mechanism in §12.

### 2.4 Two cross-cutting mechanisms

Beyond the level hierarchy, two mechanisms run across multiple levels:

- **Residual connections (§13).** Each Ganglion (and each neuron inside it, where dimensions allow) routes its input directly to its output in addition to the computed path. This is a major intervention against dead-weight collapse, which is the worst failure mode of attribution-based learning.
- **SpecialGeneralist (§8).** Inside a Lobe, one Ganglion can be reused under different context masks, gaining effective capacity without adding scaps.

### 2.5 What lives outside the chip

Only inputs and labels enter the chip during operation. Only outputs leave it. At boot, weights are serialized in. At shutdown, weights are serialized out. **No weight ever leaves the chip during operation.** This is the resident-weight property.

---

## 3. Naming and Disambiguation

### 3.1 Semi-anatomical naming

Architectural elements use biological names: **Scap, Ganglion, Column, Lobe, Limbic Loop, Cortex, Hippocampus, Commissure, Brainstem, SpecialGeneralist, Synaptic Drift, Engram Buffer**.

These are *inspired-by*, not *claiming-to-be*. They preserve intuition without claiming biological fidelity.

When ambiguity matters:

- **Default usage** = circuit element. Writing "Brainstem" means our circuit's central controller.
- Prefix **`biological-`** when the actual biology is meant (e.g. "biological brainstem").
- Prefix **`analog-`** when the circuit needs to be flagged explicitly in a mixed-context paragraph.

### 3.2 Layer / role / route disambiguation

The number "L1" appears in three independent contexts. Always specify which:

- **Ganglion-internal layers** are L1–L4 within a single Ganglion (input, two hidden, output).
- **Column-level roles** use semantic names: Generalist (G) and Specialists (S₁, S₂, S₃).
- **Route addressing levels** are written "Route L1" and "Route L2".

### 3.3 Glossary lookup

Every term used in this document is defined in §21. Refer there when in doubt.

---

## 4. The Scap — atom of storage

### 4.1 Role

A **Scap** holds the analog weight of *one synapse* — one wire between two neurons inside a Ganglion. It is the project's atom of storage. Every weight in the system lives in exactly one Scap.

Critically: **a Scap is a wire, not a neuron.** The history of "did current flow through this wire" implicitly encodes both pre-synaptic and post-synaptic activity. No separate per-neuron state is required.

### 4.2 Components

A Scap is a fixed circuit containing:

| Component | Size | Role |
|---|---|---|
| Weight capacitor | 1 cap | Holds analog weight magnitude as voltage |
| Cascode mirror | — | Sources current proportional to weight × input |
| Sign SRAM | 1 bit | Direction of weight (+ or −) |
| Refill / decay SRAM | 8 bits | Reference level for leakage compensation; doubles as tunable weight decay (§4.4) |
| Momentum SRAM | 16 bits | Accumulated contribution across the batch |
| Community / Routing SRAM | N×M bits | Which input bus to read from, which output bus to write to (set at boot) |
| Control wires | 3 | `update_signal`, `reset_signal`, tri-state feedback |

### 4.3 Sign-magnitude representation

A signed weight is stored as `sign_bit × |weight_cap_voltage|`. The weight cap voltage is always positive (capacitors can't hold negative voltage absolutely — they hold a voltage relative to a reference). Sign is digital, magnitude is analog.

This means:
- A weight near zero has small `weight_cap` voltage; sign is whichever was last set.
- A weight changing sign requires `weight_cap` to drop to zero, then sign-bit flip, then `weight_cap` to grow.
- The system can never produce a discontinuous sign change — sign changes go through zero, which is a soft barrier.

### 4.4 Tunable weight decay via refill SRAM

The refill SRAM normally compensates for natural capacitor leakage — every clock, the cascode mirror tops up the weight to match the stored reference. But the refill rate can be *deliberately tuned below* the natural decay rate, making the weight drift toward zero at a controlled pace.

This gives **free L2 regularization implemented in physics**. No explicit weight-decay term in any update equation; just under-refill.

Per-Scap refill tuning enables:
- Standard light decay everywhere (typical L2 regularization).
- Stronger decay on saturated Scaps (homeostasis — prevent runaway weights).
- Weaker decay on dead Scaps (push them back from zero — partial remedy for dead-weight collapse, §12.4).

For first simulation, use uniform light decay across all Scaps. Adaptive per-Scap decay is a §19 optimization.

### 4.5 Momentum SRAM mechanics

The 16-bit momentum SRAM accumulates **contribution measurements** during forward passes. Each forward pass, the Ganglion's measurement circuit (§5.4) produces a contribution value for this Scap; that value is EMA-blended into momentum:

```
momentum_new = α × momentum_old + (1 − α) × new_measurement
```

With **α = 3/4** (a single right-shift-by-2 plus add): cheap to implement, smooth enough.

Finer decay options via shift-by-3 (`α = 7/8`) or shift-by-4 (`α = 15/16`) available for empirical tuning.

**Floor-at-1 rule.** When momentum decays toward zero, it is pinned at 1 (lowest non-zero value) rather than allowed to round to 0. This prevents momentum-driven dead-Scap collapse: a Scap with zero momentum receives zero update forever (§12.4).

### 4.6 Forward-pass behavior

A Scap is passive during forward pass. Its weight capacitor sources current through its cascode; that current sums with other Scaps' currents at the post-synaptic neuron's summing junction. The current itself is measured externally by the Ganglion's ALU (§5.4).

### 4.7 Backward-pass behavior — fully autonomous

When `update_signal` goes high on the Ganglion-local bus, the Scap reads four signals locally and computes its own update:

```
direction = sign_SRAM XOR feedback
weight_cap -= pulse_width × momentum × direction
```

**The two factors serve different duties:**

- **`pulse_width`** is the **global update-time control**, the same value for every Scap on this bus. It is the share that arrived at this Ganglion after hierarchical diffusion. Functions as a learning-rate / total-update-magnitude signal.
- **`momentum`** is the **per-Scap contribution history**, accumulated across the batch. Functions as the Scap's own importance.

The differentiation between Scaps within a Ganglion comes entirely from their differing momenta. The differentiation between Ganglia comes from their differing pulse widths (post-diffusion). Together they produce the right update structure.

**Worked example.** Consider two Scaps A and B in the same Ganglion. After forward passes, momentum_A = 100, momentum_B = 10 (A contributed more). Loss is positive (need to decrease prediction). Diffusion delivers `pulse_width = 50` to this Ganglion's bus.

- ΔW_A = 50 × 100 × direction_A = 5000 × direction_A
- ΔW_B = 50 × 10 × direction_B = 500 × direction_B

A's update is 10× larger than B's, matching their relative contribution. Same `pulse_width`, different momenta, correct relative update.

**Update is fully parallel.** Every Scap on the die can execute this in a single broadcast pulse. No external instruction needed. This is the decentralization win.

---

## 5. The Ganglion — atom of computation

### 5.1 Role

The **Ganglion** is the project's atom of computation. Fixed topology, hardwired, not reconfigurable after fabrication. It abstracts one biological axon's worth of multi-synapse behavior — synapse distance, density, hormone level — into a 2-3-3-2 compute structure.

### 5.2 Topology — 2-3-3-2 feedforward

```
L1 (2 input)  →  L2 (3 hidden + ReLU)  →  L3 (3 hidden + ReLU)  →  L4 (2 output)
```

- L1: 2 input neurons, fed by input capacitors via cascode mirror.
- L2: 3 hidden neurons, hardwired op-amp + ReLU.
- L3: 3 hidden neurons, hardwired op-amp + ReLU.
- L4: 2 output neurons, hardwired op-amp (no clip), drive output capacitors.

Per-neuron compute: `y = aW + b`, with `a = ReLU(y)` for L2/L3, identity for L4.

### 5.3 Scap inventory

- L1 → L2: 3×2 weights + 3 biases = **9 Scaps**
- L2 → L3: 3×3 weights + 3 biases = **12 Scaps**
- L3 → L4: 3×2 weights + 2 biases = **8 Scaps**
- **Total: 29 Scaps per Ganglion**

### 5.4 ALU and contribution measurement

The Ganglion ALU drives the forward pass *and* measures per-Scap contribution simultaneously.

| Component | Count | Role |
|---|---|---|
| Hardwired 2-3-3-2 op-amp circuit | 1 | Performs the forward computation |
| Input capacitors | 2 | Hold forward-pass inputs |
| Output capacitors | 2 | Receive forward-pass outputs |
| Measurement capacitors | 29 | One per Scap — tracks current that Scap delivered |
| Time-measure circuit | 1 | Converts time-to-threshold to contribution magnitude |
| Temp SRAM | 29 × 16 bits | Transient storage of measurements before EMA into Scap momentum |

**Measurement cycle (runs in parallel with forward pass):**

1. Inputs charge input capacitors.
2. Hardwired 2-3-3-2 computes forward pass.
3. Each Scap's measurement cap charges at a rate proportional to the current that Scap delivers.
4. Time-measure circuit clocks the rise from A% to B% on each measurement cap.
5. **The time-measure circuit converts time-to-threshold into contribution magnitude.** Shorter time = stronger contribution; the conversion is folded into the measurement circuit. By the time the value lands in temp SRAM, it already represents contribution magnitude directly — downstream logic does not need to invert.
6. At end of forward pass, each measurement is:
   - Used immediately for the Ganglion's contribution to its parent Column (sum, for §12 distribution).
   - EMA-blended into the corresponding Scap's momentum SRAM (§4.5).

**Calibration.** The A%/B% thresholds reference a calibration cap inside the ALU. This makes time-to-threshold a *ratio* measurement, robust to voltage drift and temperature.

**Forward-pass timing.** The forward pass cannot complete until the slowest measurement cap finishes its threshold crossing. Worst case: `T_forward = max(output_cap_charge_time, slowest_measurement_time)`. Default mitigation: cap measurement time at `T_max`; Scaps that don't cross threshold by then get `T_max` recorded (i.e. minimum contribution).

### 5.5 ALU reuse

One Ganglion ALU is *reused* across many Ganglia in a Column. The ALU steps through Ganglia sequentially, holding intermediate values in global capacitors (§6). This keeps total ALU count manageable.

For 256 Ganglia in a region, a single ALU executes 256 forward passes per inference cycle. The forward-pass time is bounded, not the ALU count.

### 5.6 Why 2-3-3-2 specifically

Two complementary justifications:

**Biological:** One Ganglion represents one biological axon with multi-synapse output behavior. The 2-3-3-2 expansion-contraction pattern models the way a real synapse takes input, distributes through multiple dendritic branches with varying density and hormone levels, recombines through summation thresholds, and produces a graded output. Not a literal model — a structural abstraction.

**Mathematical:** 2×3×3×2 = 36 distinct paths from input to output, with 29 scaps. Optimizes **path diversity per scap**. Alternative topologies for future testing:

| Topology | Paths | Scaps | Paths/scap |
|---|---|---|---|
| 2-3-3-2 (default) | 36 | 29 | 1.24 |
| 2-5-5-2 | 100 | 49 | 2.04 |
| 3-5-5-3 | 225 | 76 | 2.96 |
| 1-5-1 | 5 | 16 | 0.31 |

Higher paths-per-scap is probably better. Test only after H1 (§15) is locked.

### 5.7 Ganglion-level residual bypass

A direct wire from each L1 input capacitor to the corresponding L4 output capacitor (input bypasses through to output, summed with the computed result).

This is the entry point for residual connections (§13) — it sits inside the Ganglion at its widest level (input-to-output, both width 2).

The bypass is **physically just two wires** with an op-amp summer at the output. Cost: negligible. Benefit: see §13.

---

## 6. The Column — sequential composition

### 6.1 Role

A **Column** is a sequential chain of Ganglia, connected by **translate ALUs** that reshape dimensionality. One Ganglion handles 2-in / 2-out only. The Column composes many Ganglia to do useful-scale computation.

### 6.2 Structure

```
input → [translate ALU] → Ganglion → [translate ALU] → Ganglion → ... → output
                ↑                                 ↑
            global cap                       global cap
```

Translate ALUs reshape the signal between Ganglia. Global capacitors hold transient state between ALU steps.

### 6.3 Translate ALU

A **translate ALU** is a hardwired analog computation that maps `n` inputs to `m` outputs. Internally it is a small matrix-multiply via op-amps, with weights stored in Scaps (one Scap per wire, just like a Ganglion).

**Translate ALUs are learnable.** Their Scaps participate in hierarchical diffusion the same way Ganglion Scaps do. The Brainstem at boot loads the routing for each translate ALU; during operation, its Scap weights update via the standard mechanism.

**Translate ALU size catalog** (for first simulation):

| Size | Use case |
|---|---|
| 2:2 | Identity-shape translation between Ganglia |
| 2:4 | Expand into a wider Column body |
| 4:2 | Compress to match Ganglion input |
| 4:4 | Same-dimension translation |
| 4:5, 5:5, 5:4 | Asymmetric reshaping |
| 8:4 | Multi-input fusion (used in Lobe, §7) |

The catalog is fixed at fabrication. Adding a new size requires new hardware.

### 6.4 Global capacitors

Between every ALU step (Ganglion or translate), the result is held in **global capacitors**. These are not weight storage — they hold transient activations between ALU passes. They are the only "registers" in the system.

Global capacitors have the same leakage characteristics as Scaps but no refill SRAM — they are read once and overwritten on the next forward pass.

### 6.5 Forward pass through a Column

1. Inputs land in the Column's input capacitors.
2. First translate ALU reads inputs, computes, writes to first set of global caps.
3. First Ganglion ALU reads from global caps, computes, writes to its output caps.
4. Output caps are read into next global caps via the next translate ALU.
5. Repeat through the chain.
6. Final translate ALU writes to the Column's output capacitors.

Total time scales linearly with chain length. Total ALU count is just 1 Ganglion ALU + small set of translate ALUs — reused across all Ganglia in the Column.

### 6.6 Column-level residual bypass

Optional: Column input added directly to Column output. Same idea as Ganglion-level bypass (§5.7), one level up. Useful when a Column is part of a deeper Lobe and is at risk of vanishing through composition.

Implementation: passive analog summing at the Column output. Cost: one summer.

Status: deferred to §19. The default is Ganglion-level bypass only.

---

## 7. The Lobe — multi-branch DAG composition

### 7.1 Role

A **Lobe** is the next level of structural composition above a Column. Where a Column chains Ganglia sequentially, a Lobe composes multiple Columns in a **directed acyclic graph** — Columns can have multiple parents, multiple children, and skip-connection topology.

A Lobe is the unit of "brain region" in this architecture. The Cortex Lobe and Hippocampus Lobe are the two main Lobes in the Limbic Loop (§9).

### 7.2 Structural pattern

Example Lobe topology:

```
                input (4 dims)
                  │
                  ↓
            [Column 1 — 4:4]
              ┌───┴────────────┐
              ↓                ↓
        [Column 2 — 4:4]      │
              │                │
              └────────┐       │
                       ↓       ↓
                  [Column 3 — 8:4]
                       │
                       ↓
                   output (4 dims)
```

- Column 1 outputs feed both Column 2 and Column 3 (skip-connection branch).
- Column 3 has 8-dimensional input (4 from Column 1 + 4 from Column 2 — **two separate 4:4 connections**, kept distinct, not concatenated as 4:8).

The Lobe is a DAG; signal can take multiple paths through it.

### 7.3 Why multi-branch matters

Two reasons:

1. **Expressivity.** A linear chain can only refine its single representation. A DAG can carry multiple intermediate representations forward in parallel, fusing them at later stages.
2. **Skip connections for free.** Column 1's output reaching Column 3 directly is structurally a skip connection at the Lobe level. This complements the Ganglion-level residual bypass (§5.7).

### 7.4 Multi-parent diffusion

When a Column has multiple parents in the Lobe DAG, it receives **multiple loss shares during backward pass** — one from each parent. The Column's update equation must handle this.

**The rule:** a Column with multiple parents sums all incoming shares into a single combined share before diffusing further down.

```
combined_share = Σ shares_from_parents
```

This sum then becomes the share that this Column distributes to its own children (Ganglia and translate ALUs inside it).

**Loss conservation under multi-parent.** Each parent's distribution memory still satisfies `Σ shares_to_children = parent_loss`. When a child has multiple parents, summing their shares is correct: the total loss flowing into this child equals the sum of contributions assigned to it by each parent. The system-wide conservation invariant still holds.

### 7.5 Lobe-local bus

The Lobe has its own broadcast bus for downward distribution. It carries pulse-width-encoded shares to each Column inside the Lobe. The bus structure mirrors Column-local and Ganglion-local buses.

### 7.6 Lobe-level distribution memory

The Lobe maintains distribution memory tracking each Column's contribution during the last forward pass. For a Lobe with K Columns, this is K × (precision) bits of SRAM.

Precision recommendation: **12 bits per Column** at the Lobe level. See §12.5 for precision allocation across the hierarchy.

### 7.7 ALU at the Lobe level

The Lobe does not have its own ALU. It uses the Column-level translate ALUs to perform any reshaping at the Lobe interface (input fan-in, output fan-out). Multi-branch composition happens by **wiring**, not by additional compute.

---

## 8. SpecialGeneralist — gated Ganglion reuse

### 8.1 Where this lives

SpecialGeneralist is a pattern that lives **inside a Lobe**. It is a way to compose Ganglia inside a Column or across Columns within a Lobe that achieves higher effective capacity per Scap without adding hardware.

### 8.2 The problem it solves

Naive Ganglion reuse — calling one physical Ganglion multiple times in different contexts — causes gradient conflict. Each call wants to push the Ganglion's weights in a different direction; updates contradict; the Ganglion converges to a useless consensus.

### 8.3 The mechanism

A **Generalist Ganglion (G)** is called multiple times under different contexts, each gated by a **context mask** from a **Specialist Ganglion (S)**:

```
Specialist S₁ → mask M₁ → G operates with subset of neurons gated by M₁
Specialist S₂ → mask M₂ → G operates with different subset
Specialist S₃ → mask M₃ → G operates with another subset
```

G's Scaps are shared across calls, but each call uses a *different sub-network within G*. Different masks → different active sub-networks → different effective computation.

### 8.4 Why this works

- **G can learn multiple functions** on the same hardware, selected by mask. No consensus-compromise.
- **Distribution measurement naturally supports gating.** A gated-off Scap delivers zero current, has zero measurement, contributes zero to the share, receives zero update. The math falls out for free.
- **The mask tells us which call a measurement belongs to.** The gradient-conflict problem disappears.

### 8.5 Components

- **G** — one physical Ganglion with a fixed Scap inventory.
- **S₁, S₂, S₃** — separate physical Ganglia that drive G under different masks.
- **Active mask register** — small SRAM at G holding the current call's mask.
- **Mask source per S** — for first simulation, hardcoded; later, learned.

### 8.6 Mask policy options

**Where the mask comes from**, in increasing complexity:

1. **Hardcoded per Specialist** — each S has a fixed mask, never changes. Cheap. **Default for first simulation.**
2. **Learned per Specialist** — each S has a fixed mask but the mask is trained alongside weights.
3. **Computed from S's output** — mask is a function of S's last output, computed by a tiny circuit. Most flexible, most expensive.

**Mask overlap policy:**

- **Mutually exclusive** — disjoint subsets of G's neurons. Cleanest, no gradient conflict. **Default for first simulation.**
- **Overlapping** — some shared G-neurons between specialists. Allows cross-specialist learning in the overlap, but reintroduces gradient conflict there.

Start with hardcoded mutually-exclusive masks. Escalate based on simulation evidence.

### 8.7 Hierarchical diffusion handles this correctly

The standard mechanism (§12) requires no modification: gated-off Scaps register zero contribution and receive zero update. Active Scaps are updated based on their actual contribution during the call. No special handling needed.

### 8.8 Fallback

If SpecialGeneralist underperforms plain G-reuse in simulation:

- **Reservoir-G fallback:** initialize G with diverse non-zero random weights and *freeze* it. All learning happens in S₁, S₂, S₃. This is reservoir computing — a well-studied technique with established theory.

Plain G-reuse stays as a baseline comparison. Reservoir-G stays as a deeper fallback.

---

## 9. The Limbic Loop — recurrent prediction with two timescales

### 9.1 Role

The **Limbic Loop** is the top-level structural unit. It is two Lobes (Cortex and Hippocampus) connected by a Commissure, in a recurrent prediction loop with two-timescale learning.

### 9.2 Components

```
                input (high quality)
                       │
                       ├──→ [Input Reducer] ──→ input (low quality)
                       │                              │
                       ↓                              ↓
              ┌────[Cortex Lobe]────┐          ┌──[Hippocampus Lobe]──┐
              │                     │          │                       │
              │  (fast learning)    │          │  (slow learning)      │
              │                     │          │                       │
              ↓                     ↓          ↓                       ↓
        prediction A          to Commissure    to Commissure       prediction B
                                    │              │
                                    └─[Commissure]─┘
                                       │      │
                                       ↓      ↓
                                  back to Cortex / Hippocampus
```

- **Cortex Lobe** — fast-learning Lobe. Updates every clock.
- **Hippocampus Lobe** — slow-learning Lobe. Same structure as Cortex. Updates every k clocks.
- **Commissure** — inter-Lobe connector. Updates every M clocks (M > k).
- **Input Reducer** — fixed circuit reducing input feature count (e.g. 20 → 5) to prevent Hippocampus from short-circuiting the loop.

### 9.3 Cortex and Hippocampus: same structure, different timescales

The two Lobes have **identical topology** at the Ganglion / Column / Lobe-DAG level. Both have **two output heads**:

- **Head A** — predicts input. Loss signal for this Lobe.
- **Head B** — sends to the other Lobe via Commissure.

The only difference between the two Lobes is **which update bus they listen to**:

- Cortex listens to the always-on update bus.
- Hippocampus listens to a bus gated every k-th clock.

This means Cortex updates every clock, Hippocampus accumulates contribution in its momentum SRAM across k clocks and updates only on the k-th. The slow-consolidation behavior emerges from one gating switch — no structural difference required.

### 9.4 Why this timescale separation works

- Cortex's fast updates track immediate input statistics.
- Hippocampus's slow updates accumulate into a stable prior — what the input "usually looks like" over the recent past.
- Their *difference*, carried through the Commissure, is the prediction error that drives learning across both Lobes. This is the predictive-coding pattern.

### 9.5 Input quality asymmetry

Cortex receives full input; Hippocampus receives input passed through an **Input Reducer** that destroys fine detail (e.g. 20 features → 5 features via a small fixed Ganglion or hardwired reducer).

Without this, Hippocampus could short-circuit the loop by predicting input directly from raw input, bypassing the recurrent dynamic. The reducer forces Hippocampus to rely on Cortex's signal via Commissure for fine-grained prediction.

### 9.6 Recurrence stability — the decay term

A recurrent system with non-zero gain in its feedback loop can amplify noise. To prevent this, the Commissure output is multiplied by a **decay factor** (default 0.9) before entering the receiving Lobe. Implementable as a passive resistor divider — zero compute cost.

This is the architecture's equivalent of biological inhibitory interneurons or modern layer normalization. Without it, the loop is unstable. **The decay is mandatory.**

### 9.7 Backward flow

1. *Forward (every clock):* Both Lobes run forward. Both produce two-head outputs. Distribution memory fills at every level (Lobe / Column / Ganglion / Scap).
2. *Loss compute:* Brainstem reads both predictions, computes losses, broadcasts on per-Lobe buses.
3. *Diffusion (six clocks):* Loss diffuses through Lobe → Column → Ganglion → Scap on the active bus.
4. *Scap updates:* Active Lobe's Scaps update locally. Inactive Lobe's Scaps don't see an update pulse but continue accumulating momentum from forward passes.

**Cortex's bus is active every clock. Hippocampus's bus is active every k-th clock. Commissure's bus is active every M-th clock.**

### 9.8 Consolidation pulse-width policy

When Hippocampus's bus fires (every k-th clock), the loss pulse-width could be:

1. **Same as Cortex's normal pulse** — Hippocampus simply gets fewer updates. Total weight movement = `1/k` of Cortex's.
2. **k× larger pulse** — total weight movement matches Cortex's. Requires Brainstem to send amplified pulse on consolidation clocks.
3. **Accumulated loss over k clocks** — Brainstem aggregates loss between consolidations; releases the accumulation as one pulse. More biologically faithful but requires Brainstem state.

**Default for first simulation: option 1.** Simplest, no extra Brainstem state. Test options 2 and 3 as optimizations.

---

## 10. The Commissure — inter-Lobe connector

### 10.1 Role

The **Commissure** connects Cortex Lobe ↔ Hippocampus Lobe. It is itself a small group of Ganglia (not a passive wire), capable of performing learned signal translation between the two Lobes.

### 10.2 Why it's a real compute element, not a wire

The Commissure can perform format conversion, dimensionality matching, and noise filtering between the two Lobes. With learnable Scaps inside it, it adapts to the relationship between Cortex and Hippocampus outputs over training.

### 10.3 Trainability and gating

The Commissure trains at a **reduced learning rate**. Its update bus fires every M clocks, where M > k (i.e. slower than Hippocampus, which is already slower than Cortex).

**Why slow Commissure matters.** The Commissure carries the signal that *both* Lobes backpropagate against. If the Commissure updates too quickly, it destabilizes the entire loop — both Lobes are chasing a moving target. A slow Commissure gives the Lobes a stable reference to converge against.

### 10.4 Why heavy compute here is affordable

Only one Commissure exists per Limbic Loop. Spending more Scaps on it doesn't blow the total budget. The Commissure can be larger and richer than its sender-Lobe / receiver-Lobe topology would suggest.

### 10.5 Optional: Synaptic Drift in the Commissure

The Commissure is a natural home for **Synaptic Drift** (§19) — learnable per-synapse 1D position. Cross-region routing benefits from spatial-position learning more than within-region computation. Activate Synaptic Drift in the Commissure first.

---

## 11. The Brainstem — central controller

### 11.1 Role

The **Brainstem** is the project's only central controller. Small, named, budgeted — not hand-waved.

Biologically apt: real brainstems set rhythms, broadcast neuromodulators, and do not perform cognition.

### 11.2 Responsibilities

The Brainstem:

- Reads predictions from output capacitors via ADC.
- Holds the previous prediction (one-clock buffer) for autoregressive loss vs current input.
- Computes total loss per Lobe (one MAC's worth of arithmetic per Lobe).
- Broadcasts loss on the global bus, pulse-width-encoded.
- Broadcasts tri-state sign `(+, 0, −)` on the global feedback wire.
- **Manages per-Lobe update gating** — Cortex bus (every clock), Hippocampus bus (every k clocks), Commissure bus (every M clocks).
- Manages clocks: forward, backward, batch boundary, consolidation.
- Manages control signals: `update_signal` (per Lobe), `reset_signal`, `consolidate_signal`.
- Holds the **community map** defining which Routes belong to which Lobe / Column (set at boot, read-only after).

### 11.3 Size and complexity

Estimated 5–10k transistors equivalent. Tiny compared to a CPU. Large enough to require explicit design.

Implementation: a small hardwired state machine plus a few MAC units, plus ADCs and pulse-width modulators. Not a programmable processor.

### 11.4 What the Brainstem is *not*

- Not a CPU. No instruction set, no fetch/decode.
- Not a backprop engine. Does not compute gradients.
- Does not know about individual Scaps. Speaks only to the top of the hierarchy.

### 11.5 Future: distributed loss compute

If each output Ganglion can sense its own (prediction − label) locally — by routing the label voltage to the output Ganglia — the Brainstem's loss compute disappears. Brainstem shrinks to label-broadcaster + clock.

Status: §19 future track. Currently bounded by ALU/routing budget.

---

## 12. Attribution-Based Hierarchical Diffusion — the learning mechanism

### 12.1 The structural idea

Every level of the hierarchy stores **distribution memory** — how much each of its children contributed to its output on the most recent forward pass. When loss arrives from above, the level divides it among its children in proportion to their stored contributions, broadcasts the shares on its local bus, and each child does the same recursively until the share reaches the Scaps.

```
Brainstem computes total loss L per Lobe
    ↓ broadcasts on global bus
Limbic Loop reads L
    ↓ uses distribution memory → (Cortex's share, Hippocampus's share)
    ↓ broadcasts shares on Limbic-local bus
Each Lobe reads its share
    ↓ uses distribution memory → (Column shares)
    ↓ broadcasts on Lobe-local bus
Each Column reads its share
    ↓ uses distribution memory → (Ganglion shares + translate ALU shares)
    ↓ broadcasts on Column-local bus
Each Ganglion reads its share
    ↓ uses 29 measurement caps (Ganglion's distribution memory) → (per-Scap shares)
    ↓ broadcasts on Ganglion-local bus
Each Scap reads its share (= pulse_width)
    ↓ executes local update via PWM × momentum × direction
```

### 12.2 What this actually is: attribution, not gradient

The mechanism is **attribution-based credit assignment**, not gradient descent. This distinction matters.

**Vanilla backprop is sensitivity-based.** It asks: *if I wiggle weight W by ε, how much does loss L change?* The answer is `∂L/∂W`, computed via the chain rule by routing per-layer error signals `δ` backward through the *next layer's* weights (`δ_l = W_{l+1}ᵀ · δ_{l+1} ⊙ σ'(z_l)`).

**This architecture is attribution-based.** It asks: *given that this Scap carried this much current during the forward pass, how much of the parent's error is attributable to it?* The answer is a proportion: `share = parent_loss × (child_contribution / total_contribution)`. The "contribution" is what the analog substrate literally measures for free — the current through each Scap, which is proportional to `|a · W|`.

**The structural divergence:**

| Aspect | Vanilla (sensitivity) | This architecture (attribution) |
|---|---|---|
| Routing error backward | Use next layer's W as transpose to route δ | Use `\|a · W\|` at current layer to split parent's share |
| Weight in own update | No (only `δ · a`) | Yes (because `\|a · W\|` is what's measured) |
| Information needed | Per-neuron δ propagated from output, requiring weight transport | Per-Scap `\|a · W\|` measured locally during forward pass |
| Loss conservation | By linearity of chain rule | By explicit normalization |
| Inactive units | `σ'(z) = 0` kills propagation | `\|a · W\| = 0` kills propagation |

### 12.3 The family of methods this belongs to

Attribution-based learning sits in the family of **three-factor synaptic learning rules** (pre-activity × post-activity × neuromodulator) — the dominant theoretical framework for biological synaptic plasticity. Specific anchors:

- **Frémaux & Gerstner (2016)** — three-factor learning rules review.
- **Scellier & Bengio (2017)** — Equilibrium Propagation. Local updates that compute gradient in the small-perturbation limit.
- **Lillicrap et al. (2016)** — Feedback Alignment. Random fixed feedback matrices still let networks learn.
- **Bach et al. (2015)** — Layer-wise Relevance Propagation. Attribution method using exactly `|a · W|` for relevance.
- **Rao & Ballard (1999), Friston** — predictive coding. Local error minimization.
- **Bellec et al. (2020)** — e-prop. Eligibility traces in spiking RNNs. The momentum SRAM is structurally an eligibility trace.

**What this body of work establishes empirically:**

- Vanilla SGD is the most accurate gradient estimate.
- Feedback alignment shows you can be substantially less accurate and still learn, especially in over-parameterized networks.
- EP and contrastive Hebbian converge to the same place as SGD under specific conditions.
- Local rules with global modulators can work for deep networks; performance varies with architecture and task.

There is no theorem ranking these methods against vanilla SGD. Whether attribution-based learning converges as well as gradient descent on a given task is an empirical question.

### 12.4 Known failure modes

Picking attribution-based learning is a real commitment with known failure modes. Simulation must target them directly:

1. **Dead-weight collapse.** Because `ΔW ∝ |a · W|`, a weight that reaches zero magnitude receives zero update and stays dead forever. The floor-at-1 momentum rule (§4.5) and the residual connections (§13) are the main mitigations. **Simulation must instrument zero-magnitude weight counts.**
2. **Routing-update coupling.** The same `|a · W|` does both routing of loss and magnitude of update. Errors in one job contaminate the other.
3. **Slow convergence on tasks needing precise gradient.** Loss surfaces with narrow valleys may converge slower than under SGD.
4. **Initialization sensitivity.** Attribution-based methods are typically more sensitive to init than SGD.

**Four remediation paths, in order of cost:**

- **Path 0 (cheapest):** Add a tiny random noise floor to weight updates — every Scap gets a small random perturbation each update independent of measurement. Rescues dead weights without circuit changes. One-line addition.
- **Path 1:** Strip the multiplier from the measurement. Measure `|a|` only. Update becomes vanilla SGD `ΔW ∝ a · δ`. Cost: extra input sensors *and* hierarchical diffusion loses routing signal (splitting loss by input alone is biased). Routing math needs fix.
- **Path 2:** Keep `|a · W|` for routing, add a separate input sensor for the update step. Most chain-rule-correct, most circuit-expensive.
- **Path 3 (current default):** Accept attribution-based, instrument failure modes, test empirically. Cost to find out is low; the architecture is already producing it for free.

Commit to Path 3 for baseline. Path 0 is the first remediation if dead-weight appears. Paths 1 and 2 documented for deeper failures.

### 12.5 Per-level precision allocation

Loss is multiplied at every level as it diffuses. Quantization compounds. Allocation:

| Level | Distribution storage | Notes |
|---|---|---|
| Limbic Loop | 16-bit SRAM per child | Top level — most bits matter |
| Lobe | 12-bit SRAM per Column | |
| Column | 10-bit SRAM per Ganglion / translate ALU | |
| Ganglion | 29 measurement caps (analog) | Continuous |
| Scap | 16-bit momentum SRAM | EMA accumulation |

Total stored distribution state is small (one number per child per module). Spending bits at the top is cheap.

### 12.6 Loss conservation as invariant

At every level, **additive shares**: `Σ children_shares = parent_loss`. The total loss flowing into a level equals the total flowing out. Holds at every backward pass within finite-precision tolerance ε.

This is verifiable in simulation. **It catches bugs immediately.** If conservation is violated by more than ε at any level, the implementation has a bug.

### 12.7 Normalization via analog op-amp

The division `child_contribution / total_contribution` happens in the **analog op-amp ALU**, not in binary. Standard op-amp ratio-of-currents or normalizing-summing-amplifier topology. One normalization circuit per level per forward pass.

By the time anything lands in a Scap's momentum SRAM or a level's distribution memory, it is **already final-form, ready-to-use, no further division required**.

The architecture leans on this: continuous analog math is the cheap path, binary math is the expensive path. Normalization is a place where that bet pays off.

(Specific op-amp topology choice is §19 future detail — for first simulation, assume the operation is available.)

### 12.8 Backward pass timing

Backward pass is **synchronous and clock-driven**, six clocks total:

1. *Clock 0:* Brainstem broadcasts total loss on global bus.
2. *Clock 1:* Limbic Loop reads, computes child shares, broadcasts on Limbic-local bus.
3. *Clock 2:* Lobes read, compute Column shares, broadcast on Lobe-local bus.
4. *Clock 3:* Columns read, compute Ganglion shares, broadcast on Column-local bus.
5. *Clock 4:* Ganglia read, compute per-Scap shares using measurement caps, broadcast on Ganglion-local bus.
6. *Clock 5:* Scaps update weight capacitors locally via PWM.

**Six clocks for a full backward pass, regardless of network size.** Hierarchy depth bounds the backward latency, not weight count.

### 12.9 Why this matters

This mechanism:

- Eliminates per-Scap gradient routing.
- Uses only broadcast buses that already exist at each level.
- Maps cleanly to biological neuromodulator diffusion.
- Maps cleanly to three-factor synaptic plasticity rules.
- Uses the substrate's natural physical measurement (`a · W` is the forward current).
- Scales: adding a hierarchy level adds one clock, not N clocks.

What it does **not** do:

- Implement the chain rule (exactly or approximately).
- Compute `∂L/∂W` rigorously.
- Inherit gradient descent's convergence guarantees.

Convergence is empirical, not theoretical.

---

## 13. Residual Connections — fighting dead-weight in attribution learning

### 13.1 The argument

Each neuron's output is `H(x) = f(x) + x` instead of `H(x) = f(x)`. Input bypasses the computed path and is added to the output.

This is residual connections (ResNets, He et al. 2016). Familiar in modern ML. But for *this* architecture, it serves a different purpose than it does in standard ML.

### 13.2 Why residuals matter more here than in vanilla ML

In vanilla SGD, residual connections help gradient flow through depth — the gradient has a direct path back through the bypass, so it doesn't vanish through many layers of multiplication.

In **attribution-based learning**, residuals do something more important: they directly attack the **dead-weight collapse** failure mode (§12.4).

Recall: `ΔW ∝ |a · W|`. If `W → 0`, `ΔW → 0`. Dead weight stays dead.

With residual connections, the signal `x` flows around the dead weight via the bypass. The dead weight still gets `ΔW → 0`, but **downstream neurons keep receiving signal** through the bypass. The network keeps computing, keeps learning. Over time, as other weights reorganize, the dead Scap may receive non-zero attribution again as input statistics shift.

**Residual connections are arguably more important for attribution-based learning than for SGD.** They are not optional — they are a primary defense against the learning rule's worst failure mode.

### 13.3 Implementation in the substrate

A residual bypass is **two wires** with an op-amp summer at the receiver. The cheapest mechanism in the entire architecture.

```
input ───────────────────┐
   │                      │
   └──[Ganglion compute]─→[summer]──→ output
```

Cost: one op-amp summer per residual point. Trivially cheap.

### 13.4 Where residuals live in this architecture

**Ganglion-level (default).** A direct L1 → L4 bypass inside every Ganglion. L1 and L4 both have width 2, so the bypass is dimension-matched and free. Specified as §5.7.

**Per-neuron (future test).** Each neuron internally has `output = f(input) + input`. Requires dimension matching at every layer of the 2-3-3-2 — needs either projection or a topology change to 3-3-3-3 (where every layer matches in width). Status: future test.

**Column-level (optional).** Column input added to Column output. Useful for deep Columns. Status: optional, deferred.

**Lobe-level (effectively free via DAG topology).** Skip connections in the Lobe DAG (§7) are structurally residual connections. Column 1 → Column 3 directly, bypassing Column 2, *is* a residual. Already part of the architecture.

So residuals operate at three levels: inside Ganglia (default), across Lobe DAGs (structural), and optionally between Columns.

### 13.5 Variance management

`H(x) = f(x) + x` has variance `var(f(x)) + var(x)` (assuming independence). Without management, variance grows through depth.

**Strategy:** initialize `f(x)` to produce small outputs at training start. With small initial Scap magnitudes (§16), `f(x)` starts close to zero; the bypass dominates; the Ganglion starts close to identity. This is the modern ResNet best practice.

As training proceeds, `f(x)` learns to produce a *small correction* to the bypassed signal. The residual block learns a delta, not a full transformation.

For variance normalization across deeper depth, three options:

1. **Fixed scaling factor** — multiply each Ganglion's output by α < 1. Tune empirically. Cheapest.
2. **Analog normalizer circuit** — op-amp circuit that normalizes layer-output amplitude. Same circuit family as §12.7.
3. **Adaptive analog AGC** — feedback gain control. Well-studied in radio circuits. Most complex.

**Default for first simulation: option 1.** Tune α per layer empirically.

### 13.6 Distribution measurement with residuals

The Scap measurement (§5.4) measures the current through *the Scap*, which is the learned part `a · W`. The bypass current goes around the Scap and is not measured by it. So the per-Scap attribution is correct.

But at higher levels, the Ganglion's *output* (which goes into the parent Column's distribution memory) now includes both the learned part and the bypass. The bypass contributes to the next-stage signal without having a learnable weight to attribute to.

**Fix:** at the Column / Lobe levels, measure *only the learned-path contribution*, not total output. The bypass is informational, not learnable, and should not show up in distribution memory.

Implementation: a Ganglion has two outputs — its learned output (which goes into measurement) and its bypass (which is summed downstream). The bypass does not contribute to distribution memory.

---

## 14. Routes Hierarchy — physical layout

### 14.1 Goal

Ganglia occupy a 2D grid. Addressing must be cheap.

### 14.2 Two-level addressing

- **Route L1**: 4-bit address selects one of 16 unit-route Ganglia (horizontal axis).
- **Route L2**: 4-bit address selects one of 16 L1-route groups (vertical axis).
- **Total per region: 256 Ganglia.**

> Route L1 / L2 are *addressing levels*, unrelated to Ganglion-internal L1–L4.

### 14.3 Hierarchy routing extension

Hierarchical diffusion requires that every level of hierarchy be addressable, not just Ganglia. Routes extend to:

- Column membership of each Ganglion (set at boot).
- Lobe membership of each Column.
- Limbic-Loop membership of each Lobe.
- Brainstem-managed community map indexing all of the above.

All this routing state is held in community SRAM, set once at boot.

### 14.4 Sequential boot load

1. Set Route L1 + L2 to activate one unit-route Ganglion.
2. Send routing assignments (input bus to read, output bus to write, parent Column ID, parent Lobe ID, parent Limbic-Loop ID) — stored in community SRAM.
3. Advance to next Ganglion, repeat.

After load, every Scap knows its input/output buses and parent hierarchy. **No re-routing during operation.**

### 14.5 Scale

256 Ganglia per region in the default configuration. Is this enough for "useful intelligence"? Unknown. Simulate one region at full fidelity first; scale to multi-region as Phase 5+.

---

## 15. Hypotheses (the testable claims)

Each is falsifiable. The simulation exists to test them.

**H1 — Attribution-based hierarchical diffusion converges on substantive tasks.**
Loss broadcast from the Brainstem, diffused through five levels of distribution memory using `|a · W|` as the attribution quantity, arriving at Scaps as PWM update pulses, can drive the system to convergence on tasks vanilla SGD would also solve. Convergence is empirical, not theoretically guaranteed. *Central open research question.*

**H2 — SpecialGeneralist beats plain G-reuse.**
Gated reuse (G with context masks from Specialists) achieves higher effective capacity per Scap than plain G-reuse and is more stable than Reservoir-G.

**H3 — Two-timescale Limbic Loop converges.**
Fast Cortex + slow Hippocampus + decayed Commissure recurrence forms stable memory attractors and recalls patterns from partial cues.

**H4 — Synaptic Drift accelerates convergence (optional).**
Learnable 1D synapse address improves convergence speed and stability. Activate only after H1 is validated. Test first in Commissure.

**H5 — Weight state never leaves the substrate during operation.**
Full inference + training run without LDR/STR of weights. Only input/output cross the boundary. Serialization only at shutdown.

**H6 — Loss conservation holds across the hierarchy within bounded precision error.**
At every backward pass, `Σ children_shares = parent_loss` at every level, within finite-precision tolerance ε.

**H7 — Dead-weight collapse is bounded.**
Combined effect of floor-at-1 momentum (§4.5), residual connections (§13), and tunable refill (§4.4) keeps the fraction of dead Scaps below 5% after Phase 2 training runs. If H7 fails, escalate to Path 0 (noise floor on weight updates, §12.4).

**H8 — Residual connections reduce dead-weight rate and accelerate convergence.**
Ganglion-level residual bypass measurably reduces dead-Scap fraction and improves convergence speed on the Phase 2 task suite, compared to a non-residual baseline of identical topology.

**H9 — Lobe-level multi-branch composition outperforms sequential Columns.**
A Lobe with DAG topology (parallel branches, skip connections) achieves better expressivity per Scap than a sequential Column of equal Scap count. Tested in Phase 3+.

---

## 16. Math to Justify (priority targets)

Written justifications to develop alongside simulation:

1. **Time-to-threshold to contribution conversion.** Show that under constant-current capacitor charging, the time-measure circuit's output is linear in contribution magnitude.

2. **Attribution preserves monotonicity of update magnitudes.** Scaps that contributed more receive larger updates. This is the minimum mathematical property required — not equivalence to gradient. Empirical comparison against SGD as a diagnostic.

3. **Loss conservation invariant.** `Σ children_shares = parent_loss` at every level, every clock.

4. **Multi-parent diffusion preserves loss conservation.** When a child has multiple parents, the sum of shares it receives equals the sum of contributions its parents assigned to it.

5. **Dead-weight collapse rate is bounded.** Given initialization `(μ_init, σ_init)`, floor-at-1 momentum rule, and residual connections, derive an upper bound on expected fraction of zero-magnitude Scaps after N training steps.

6. **EMA momentum with α=3/4 is contractive.** Under bounded measurement inputs, momentum stays bounded.

7. **e^t soft saturation as implicit regularizer.** Constant-pulse PWM charging produces a stable fixed point at supply rails.

8. **Limbic Loop stability with decay factor.** Conditions on Cortex / Hippocampus / Commissure rates and decay factor that prevent oscillation or collapse.

9. **SpecialGeneralist capacity bound.** Why gated G achieves higher effective parameter count than plain G-reuse.

10. **Residual variance management.** Show that with initial Scap magnitude `σ_init` and per-layer scaling α, output variance stays bounded across depth.

11. **Low-grade input bottleneck.** How much feature reduction prevents Hippocampus short-circuiting without destroying category structure.

12. **Sign-magnitude representation correctness.** `sign_SRAM × cap_magnitude` is functionally equivalent to signed weight across all operations.

---

## 17. Open Questions

In rough priority order:

1. **Does attribution-based hierarchical diffusion converge on substantive tasks?** Phase 2 answers.
2. **Dead-weight collapse rate.** What fraction of Scaps die in Phase 2? Is floor-at-1 + residuals enough, or do we need Path 0?
3. **Per-level precision allocation.** 16/12/10/continuous/16 is provisional. Refine empirically.
4. **Time-to-threshold A%/B% calibration.** 10/30 vs 20/80 vs 30/70 — test.
5. **SpecialGeneralist mask source.** Start hardcoded; escalate if needed.
6. **SpecialGeneralist mask overlap policy.** Mutually exclusive vs overlapping — start exclusive.
7. **Two-timescale ratio k.** k = 8, 16, 32 — empirical.
8. **Commissure rate M.** M > k. Sweet spot — empirical.
9. **Decay factor in recurrence.** 0.9 default. Test 0.8 / 0.9 / 0.95.
10. **Hippocampus consolidation pulse-width policy.** Three options in §9.8.
11. **Forward-pass slow-cap mitigation.** Default cap-at-T_max; test alternatives.
12. **Initialization scheme.** Small uniform magnitudes + random signs + zero momentum. Concrete starting values: weight magnitudes ~10% of capacitor range, signs uniformly random. Compare against Xavier/He analog equivalent.
13. **Loss function.** MSE vs cross-entropy vs sign-of-error — specify per task.
14. **Output decoding precision.** Time-to-threshold on free cap — how many bits effective?
15. **Residual variance scaling α.** Per-layer factor. Tune empirically.
16. **Concrete Phase 4 task.** Sequence-prediction-with-cue-completion is recommended candidate.
17. **One region or two?** Is 256 Ganglia enough for the target task?
18. **Op-amp normalizer topology choice.** Specific circuit for §12.7 normalization.

---

## 18. Simulation Plan

Seven phases. Each closes the previous phase's open questions before the next opens.

### Phase 1 — Operator layer
Ideal-model versions of every analog primitive: add, multiply, ReLU, capacitor charge dynamics, time-to-threshold, PWM update. Unit tests.
**Exit:** all operators behave as a perfect analog circuit would.

### Phase 2 — Single Ganglion + attribution diagnostic harness
Build one 2-3-3-2 Ganglion with Scap class. Implement attribution-based update.

**Diagnostic harness:** run attribution and a vanilla-SGD baseline on identical topology, same task. Record:
- Convergence curves of both.
- Cosine similarity between attribution and SGD update vectors (diagnostic, not pass/fail).
- Fraction of dead Scaps over training.
- Weight magnitude distribution at end of training.

**Tasks:** XOR, 1D regression (sine), 2D classification (two-moons).

**Tests H1, H7, H8** (compare with-residual vs without-residual).

**Exit:** attribution converges on at least two of three tasks; dead-weight fraction < 5%; convergence within an order of magnitude of SGD.

### Phase 3 — Column with SpecialGeneralist
Compose Ganglia into Columns. Implement gated G-reuse, mask gating, EMA-momentum-with-masks.

**Tests:** SpecialGeneralist vs plain G-reuse vs flat chain of equal Scap count.

**Tests H2.**

**Exit:** SpecialGeneralist beats plain G-reuse on at least one task; else fall back to Reservoir-G.

### Phase 4 — Lobe with multi-branch DAG
Build a Lobe with multi-parent Columns. Implement multi-parent diffusion (shares from multiple parents sum).

**Tests:** Multi-branch Lobe vs sequential single-Column.

**Tests H9, H6** (loss conservation holds under multi-parent).

**Exit:** Multi-branch beats sequential on at least one expressivity test.

### Phase 5 — Limbic Loop with two-timescale learning
Cortex Lobe + Hippocampus Lobe + Commissure + Input Reducer + decay term.

**This is where the Brainstem's full behavior gets validated** — earlier phases use a degenerate Brainstem.

**Tests:** stable convergence on recall task; sweep k and M; verify loss conservation under recurrence.

**Tests H3, H6 (under recurrence).**

**Exit:** stable convergence; timescale ratios identified.

### Phase 6 — Routes + scaling
Implement Route L1/L2 + hierarchical addressing. Scale to 256 Ganglia per region.

**Tests H5** (no LDR/STR).

**Exit:** full region runs Phase 5 task end-to-end on-substrate.

### Phase 7 — Synaptic Drift (conditional)
Add learnable 1D position. Activate first in Commissure.

**Tests H4.**

**Exit:** measurable convergence improvement, or rejected.

---

## 19. Future Tracks — Optional and Deferred Mechanisms

### 19.1 Per-neuron residual connections
Internal residuals at every layer of the Ganglion. Requires dimension matching at every step — either projection circuits or topology change to 3-3-3-3.

### 19.2 Adaptive per-Scap weight decay
Tunable refill SRAM (§4.4) dynamically adjusted based on weight magnitude. Stronger decay on saturated Scaps; weaker on dead Scaps. Homeostasis at long timescales.

### 19.3 Local-aware update normalization
Each Scap exposes its remaining headroom; updates scaled to keep epoch-level update capacity uniform across Scaps. Connects to §19.2 via the recharge SRAM mechanism.

### 19.4 Activation mixing — tanh instead of ReLU
Replace L2/L3 ReLU with tanh-like saturation (unclipped op-amp at supply rails). Continuous gradient everywhere. Free in hardware.

### 19.5 Synaptic Drift
Each synapse has a learnable 1D address; signal scales by distance. Activate first in Commissure (§10.5). Analog-position version (capacitor + comparator ladder) is a clean future direction.

### 19.6 Engram Buffer (short-term memory)
Pure capacitor network acting as LSTM-like layer. Stacks between Cortex and Hippocampus. Not specified — revisit after H3.

### 19.7 Cell-fire (STDP)
Hebbian spike-timing-dependent plasticity for group-level rewiring. Open research thread.

### 19.8 Distributed loss compute
Each output Ganglion senses its own (prediction − label) locally. Brainstem shrinks to label-broadcaster + clock.

### 19.9 2-capacitor analog momentum
Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage. Eliminates ADC/SRAM at the Scap level. Post-baseline optimization.

### 19.10 Floating-gate transistor storage
Replace refilled capacitor + 8-bit SRAM with FGT (NAND-flash technology, Mythic AI's choice). Years of retention without refresh.

### 19.11 Op-amp normalizer topology
Specific circuit choice for §12.7 normalization. Multiple candidates from the analog computing literature.

### 19.12 Column-level residual bypass
Optional residual at the Column level (input → output direct path). For deep Columns.

### 19.13 Inference-only low-power mode
Disable backprop circuitry; just forward inference. Trivial mode bit.

### 19.14 Failure mode handling
Dead-Scap recovery, stuck-attractor escape, range-drift correction. Provisional: noise injection. Better mechanisms after empirical failure modes are seen.

### 19.15 SPICE / robustness simulation
After Python ideal-model converges: SPICE simulation of single Scap; noise-injected Python model calibrated against SPICE; degradation quantification.

---

## 20. What Not To Touch (the protected list)

Locked decisions. Don't reopen without strong evidence:

1. **The 2-3-3-2 Ganglion topology.** Path-diversity-per-scap optimum among small options. Don't shrink — ALU and global-cap costs would dominate.
2. **Attribution-based learning, not gradient descent.** The substrate measures `a · W` for free. Fighting this is fighting the substrate.
3. **Hierarchical diffusion as the routing mechanism.** Top-down per-level normalized shares. Optimize within; don't replace.
4. **Five structural levels.** Scap → Ganglion → Column → Lobe → Limbic Loop. Adding a sixth level requires real justification.
5. **Brainstem as a small central controller.** Distributed loss is a future track, not a baseline.
6. **Loss conservation as additive, not probability-like.** Makes debugging tractable.
7. **Semi-anatomical naming.** Settled.
8. **Residual connections at the Ganglion level by default.** Defense against dead-weight is structural, not optional.
9. **Cortex and Hippocampus have identical topology, differ only in update cadence.** Cleaner than dense-vs-sparse.

Everything else — precision allocations, decay factors, mask sources, timescale ratios, initialization — is up for negotiation as simulation data arrives.

---

## 21. Glossary

| Term | Meaning |
|---|---|
| **Scap** | Atom of storage. SRAM + Capacitor cell holding one synapse weight. |
| **Ganglion** | Atom of computation. Hardwired 2-3-3-2 network, 29 Scaps. Includes default residual bypass. |
| **Column** | Sequential composition of Ganglia connected by learnable translate ALUs. |
| **Lobe** | Multi-branch DAG composition of Columns. Brain-region scale. |
| **Limbic Loop** | Top-level recurrent system. Cortex Lobe + Hippocampus Lobe + Commissure + decay term. |
| **Cortex Lobe** | Fast-learning Lobe. Updates every clock. Two output heads. |
| **Hippocampus Lobe** | Slow-learning Lobe. Same topology as Cortex; updates every k clocks. Two output heads. |
| **Commissure** | Inter-Lobe connector. Small Ganglion group, trainable at reduced rate (every M clocks). |
| **Brainstem** | Central controller. Loss compute, broadcasts, clocks, per-Lobe gating. Tiny but explicit. |
| **Generalist (G)** | Reused Ganglion inside a Lobe under context masks (SpecialGeneralist). |
| **Specialist (S₁, S₂, S₃)** | Ganglia that drive G under different masks. |
| **SpecialGeneralist** | Gated Ganglion reuse — G with context masks from Specialists. |
| **Translate ALU** | Learnable analog reshaping element between Ganglia or between hierarchy levels. |
| **Global capacitor** | Inter-step buffer holding transient state. Not weight storage. |
| **Residual bypass** | Input-to-output direct wire summed with computed output. Defense against dead-weight. |
| **Hierarchical Diffusion** | The learning mechanism. Loss diffuses through level shares from top. |
| **Distribution memory** | Per-level storage of children's contributions. SRAM at high levels, measurement caps at Ganglion level, momentum SRAM at Scap level. |
| **Momentum SRAM** | 16-bit per-Scap accumulator of contribution. EMA with α=3/4. Floor-at-1 rule. |
| **Refill / decay SRAM** | 8-bit per-Scap reference for leakage compensation; doubles as tunable weight-decay regularizer. |
| **PWM update** | Pulse-width-modulated weight cap update. Written locally per Scap. |
| **Pulse-width** | Global update-time control. Same value for all Scaps on a bus. LR-like. |
| **Tri-ode feedback** | Global wire carrying loss direction `(+, 0, −)`. |
| **`update_signal`** | Broadcast wire whose pulse width encodes share magnitude. Gated per-Lobe. |
| **`reset_signal`** | Broadcast wire clearing momentum SRAM. |
| **`consolidate_signal`** | Broadcast clock triggering Hippocampus update phase. |
| **Synaptic Drift** | Future mechanism: learnable 1D synapse address. |
| **Engram Buffer** | Future short-term-memory module. |
| **Cell fire** | Future STDP wiring rule. |
| **Route L1 / L2** | 4-bit + 4-bit Ganglion addressing. 256 per region. Unrelated to Ganglion-internal L1–L4. |
| **Resident-weight compute** | Weights never leave substrate during operation. Synonym: in-memory compute (CIM). |
| **Attribution-based learning** | The learning family this architecture belongs to. Updates by `\|a · W\|` contribution share, not gradient. Related to three-factor synaptic rules, EP, LRP. |
| **Loss conservation** | The invariant `Σ children_shares = parent_loss` at every level. |
| **Multi-parent diffusion** | At a child with multiple parents, incoming shares from each parent sum into a combined share. |
| **Dead-weight collapse** | Failure mode where weights near zero stop receiving updates. Worst failure mode of attribution learning. |
| **biological-X** | The biological case. |
| **analog-X** | The circuit case (explicit, used in mixed contexts). |

---

*End of Draft 4. Canonical until further data invalidates a section.*