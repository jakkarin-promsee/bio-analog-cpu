# Draft 4.1 — Bio-Inspired Analog Neural Compute Architecture

> Canonical specification. v4.1.
> Supersedes draft4.0.
> Scope: Python simulation + math justification. Every choice must remain physically realizable in analog circuitry.

> **What's new vs 4.0:** External criticism surfaced four architectural holes. Three are now patched as first-class mechanisms: (1) Multi-parent direction conflict resolved via `Forward_Sign_SRAM` per Scap (§4.2, §4.8, §7.4); (3) Time-to-Threshold resolution bottleneck resolved via Programmable Gain Amplifier on measurement caps — _Range Sensitivity_ (§5.4); (4) Analog error accumulation under PVT addressed via a new dedicated section on _Analog Robustness Mechanisms_ (§14) covering Differential Pair op-amps, Dummy Scap calibration, Current Mirror Loss Share, Auto-Zeroing phases, and Ping-Pong substrate. Hole 2 (Activity vs Relevance) is acknowledged as a watched failure mode (H10) with three deferred remediation plans, **plus a primary defense via Physical Saturation (§4.4 — new in 4.1)**. Several self-caught issues also patched: Forward_Sign degeneracy under ReLU (§4.8), momentum ceiling saturation (§12.4), residual bypass physical implementation (§13.6), Limbic Loop bus routing (§9.7), label routing (§11.2), Phase 1 simulation type (§19).

---

## 0. Reading Guide

This document describes an **analog compute substrate** for the kind of computation brains do: online, sparse, continuous-learning, in-memory. It is not a brain emulator. It is not approximate backprop. It is a different family of architecture, designed from the substrate up.

**Recommended reading order for first-time readers:**

1. §1–2 (motivation + full architecture overview)
2. §4–11 (bottom-up build: Scap → Ganglion → Column → Lobe → Limbic Loop, plus Commissure and Brainstem)
3. §12 (the learning mechanism)
4. §13 (residual connections)
5. §14 (analog robustness mechanisms — new in 4.1)
6. §16 (hypotheses) to see what we claim and what we don't

The rest is reference: math, open questions, simulation plan, future work, glossary.

**If you read only one section, read §12** — attribution-based hierarchical diffusion is the project's central architectural commitment. Read §4.4 next if you want to understand how the architecture handles winner-take-all dynamics (spoiler: physics, not software). Read §14 if you care about analog robustness against PVT.

---

## 1. Project Framing

### 1.1 Goal in one sentence

Build a substrate where the kind of computation brains do is the _cheap_ path, instead of an emulation layered on top of von Neumann silicon.

### 1.2 What this project is _not_

- It is **not** an attempt to build intelligence. "Intelligence" is too fuzzy a goal to optimize against.
- It is **not** a 1:1 copy of biology. Biology is the source of architectural patterns, not a target to reproduce.
- It is **not** another digital ML accelerator. Digital neural nets are a metaphor mistaken for the thing.

### 1.3 The four properties we want

The substrate should make all of these the natural, cheap path:

| Property            | Meaning                                                                                        |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| **Online**          | Weights update during operation, not in batch-offline epochs.                                  |
| **Sparse**          | Only paths that carry signal consume energy.                                                   |
| **Continuous**      | Weights and signals live in capacitor voltages, not bit patterns.                              |
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

| Level       | Role                             | Atom of            | Composition pattern                              |
| ----------- | -------------------------------- | ------------------ | ------------------------------------------------ |
| Scap        | Holds one synapse weight         | Storage            | —                                                |
| Ganglion    | Computes one axon's worth        | Compute            | 29 scaps wired 2-3-3-2                           |
| Column      | Sequential signal transformation | Mid-scale function | Ganglia chained through translate ALUs           |
| Lobe        | Multi-branch DAG composition     | Brain region       | Multiple Columns in parallel or branch structure |
| Limbic Loop | Recurrent prediction             | Top-level system   | Cortex Lobe + Hippocampus Lobe + Commissure      |
| Brainstem   | Central control                  | Controller         | Not in the hierarchy — sits beside it            |

### 2.3 One-paragraph preview of the learning mechanism

Each level stores **contribution memory** during the forward pass — how much each of its children contributed to its output. When the Brainstem computes loss at the top, the loss is broadcast and _diffuses down_ through the hierarchy: each level divides the loss share it received among its children in proportion to their stored contributions, broadcasts those shares on its local bus, and the next level down does the same. After five levels of diffusion, the share reaches each scap, which updates its weight capacitor locally via PWM. No per-weight gradient is computed; no weight-transport is required. Full mechanism in §12.

### 2.4 Three cross-cutting mechanisms

Beyond the level hierarchy, three mechanisms run across multiple levels:

- **Residual connections (§13).** Each Ganglion (and each neuron inside it, where dimensions allow) routes its input directly to its output in addition to the computed path. This is a major intervention against dead-weight collapse, which is the worst failure mode of attribution-based learning.
- **SpecialGeneralist (§8).** Inside a Lobe, one Ganglion can be reused under different context masks, gaining effective capacity without adding scaps.
- **Analog Robustness Mechanisms (§14).** Differential Pair op-amps, Dummy Scaps for on-the-fly calibration, Current Mirror loss share, Auto-Zeroing phases, and Range Sensitivity (PGA) to fight process variation, thermal drift, and resolution loss. These are not optional — they are what make the analog substrate physically realizable.

### 2.5 What lives outside the chip

Only inputs and labels enter the chip during operation. Only outputs leave it. At boot, weights are serialized in. At shutdown, weights are serialized out. **No weight ever leaves the chip during operation.** This is the resident-weight property.

---

## 3. Naming and Disambiguation

### 3.1 Semi-anatomical naming

Architectural elements use biological names: **Scap, Ganglion, Column, Lobe, Limbic Loop, Cortex, Hippocampus, Commissure, Brainstem, SpecialGeneralist, Synaptic Drift, Engram Buffer**.

These are _inspired-by_, not _claiming-to-be_. They preserve intuition without claiming biological fidelity.

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

Every term used in this document is defined in §22. Refer there when in doubt.

---

## 4. The Scap — atom of storage

### 4.1 Role

A **Scap** holds the analog weight of _one synapse_ — one wire between two neurons inside a Ganglion. It is the project's atom of storage. Every weight in the system lives in exactly one Scap.

Critically: **a Scap is a wire, not a neuron.** The history of "did current flow through this wire" implicitly encodes both pre-synaptic and post-synaptic activity. No separate per-neuron state is required.

### 4.2 Components

A Scap is a fixed circuit containing:

| Component                            | Size      | Role                                                                                                   |
| ------------------------------------ | --------- | ------------------------------------------------------------------------------------------------------ |
| Weight capacitor                     | 1 cap     | Holds analog weight magnitude as voltage                                                               |
| Cascode mirror                       | —         | Sources current proportional to weight × input                                                         |
| Sign SRAM                            | 1 bit     | Direction of weight (+ or −)                                                                           |
| **Forward_Sign SRAM** _(new in 4.1)_ | **1 bit** | **Sign of `a · W` during last forward pass — used for multi-parent direction resolution (§4.8, §7.4)** |
| Refill / decay SRAM                  | 8 bits    | Reference level for leakage compensation; doubles as tunable weight decay (§4.5)                       |
| Momentum SRAM                        | 16 bits   | Accumulated contribution across the batch                                                              |
| Community / Routing SRAM             | N×M bits  | Which input bus to read from, which output bus to write to (set at boot)                               |
| Control wires                        | 3         | `update_signal`, `reset_signal`, tri-state feedback                                                    |

### 4.3 Sign-magnitude representation

A signed weight is stored as `sign_bit × |weight_cap_voltage|`. The weight cap voltage is always positive (capacitors can't hold negative voltage absolutely — they hold a voltage relative to a reference). Sign is digital, magnitude is analog.

This means:

- A weight near zero has small `weight_cap` voltage; sign is whichever was last set.
- A weight changing sign requires `weight_cap` to drop to zero, then sign-bit flip, then `weight_cap` to grow.
- The system can never produce a discontinuous sign change — sign changes go through zero, which is a soft barrier.

### 4.4 Physical saturation as implicit regularization (new in 4.1)

The weight capacitor has a _hard physical ceiling_ at the supply rail voltage. This is not a software limit — it's electrochemistry. As the weight cap voltage approaches the rail, the same PWM update pulse delivers exponentially less voltage change because `dV/dt ∝ (V_rail − V_cap)` for a constant-current charging cascode.

**This is the architecture's primary answer to the Activity vs Relevance / winner-take-all concern from H10.**

The dynamic plays out like this:

1. A Scap with strong contribution `|a · W|` accumulates large momentum and receives large update magnitudes.
2. Its weight cap grows toward the supply rail.
3. As it approaches the rail, each subsequent update pulse delivers less voltage change (charging saturation: `dV/dt → 0` at the rail).
4. The Scap _self-limits_ without any explicit normalizer needed.
5. Loss share that would have gone to this Scap's update gets effectively "wasted" — the Scap can't absorb it.
6. Neighbor Scaps in the same Ganglion continue to grow normally, gradually filling the remaining capacity.

**Functionally equivalent to L2 regularization** in standard ML: weights large in magnitude have a built-in resistance to growing further. But it's free — no Loss term, no `λ · ||W||²` to compute. The physics does it.

**Why this matters for attribution-based learning specifically:**

Attribution gives the largest updates to the highest-`|a · W|` Scaps. Without saturation, this is winner-take-all: the strongest contributor grows fastest, contributes more, grows even faster, runaway. With physical saturation, the winners hit a ceiling and the runner-ups get a chance to develop. The attribution mechanism remains greedy in _direction_ but becomes self-balanced in _steady-state magnitude_.

**Three layered defenses against attribution pathologies, summarized:**

| Defense                                | What it bounds                      | Mechanism                       |
| -------------------------------------- | ----------------------------------- | ------------------------------- |
| Floor-at-1 momentum (§4.6)             | Lower bound on update sensitivity   | Pinned minimum momentum value   |
| Residual bypass (§13)                  | Routes signal around dead weights   | Bypass wire L1→L4               |
| **Physical saturation (this section)** | **Upper bound on weight magnitude** | **Capacitor charging dynamics** |

Combined: dead-weights can't fully die (floor-at-1 + residual route-around), and winners can't run away (saturation). The system has both lower and upper homeostasis built into physics.

**What still needs simulation verification:** does the _rate_ of saturation match the _rate_ of attribution updates well enough? If saturation is too slow, winners still dominate for too long. If too fast, no Scap differentiates. The supply rail voltage and the PWM pulse width together set this rate. **Phase 2 must measure: how many forward passes until the highest-contributing Scaps saturate? Compare to total training length.** If saturation happens in the first ~10% of training, that's likely too fast (no differentiation). If never, that's too slow (winner-take-all).

**Optional enhancement (deferred to §20):** explicit Adam-style `v_t` accumulator per Scap. Stores squared-update history, scales updates by `1/√v_t`. Provides symmetric per-Scap rate control (fast for under-updated Scaps, slow for over-updated). Costs 16 bits per Scap and an analog 1/√ circuit. Probably unnecessary given physical saturation; promoted to baseline only if Phase 2 shows physical saturation alone is insufficient.

### 4.5 Tunable weight decay via refill SRAM

The refill SRAM normally compensates for natural capacitor leakage — every clock, the cascode mirror tops up the weight to match the stored reference. But the refill rate can be _deliberately tuned below_ the natural decay rate, making the weight drift toward zero at a controlled pace.

This gives **free L2 regularization implemented in physics**. No explicit weight-decay term in any update equation; just under-refill.

Per-Scap refill tuning enables:

- Standard light decay everywhere (typical L2 regularization).
- Stronger decay on saturated Scaps (homeostasis — prevent runaway weights).
- Weaker decay on dead Scaps (push them back from zero — partial remedy for dead-weight collapse, §12.4).

For first simulation, use uniform light decay across all Scaps. Adaptive per-Scap decay is a §20 optimization.

### 4.6 Momentum SRAM mechanics

The 16-bit momentum SRAM accumulates **contribution measurements** during forward passes. Each forward pass, the Ganglion's measurement circuit (§5.4) produces a contribution value for this Scap; that value is EMA-blended into momentum:

```
momentum_new = α × momentum_old + (1 − α) × new_measurement
```

With **α = 3/4** (a single right-shift-by-2 plus add): cheap to implement, smooth enough.

Finer decay options via shift-by-3 (`α = 7/8`) or shift-by-4 (`α = 15/16`) available for empirical tuning.

**Floor-at-1 rule.** When momentum decays toward zero, it is pinned at 1 (lowest non-zero value) rather than allowed to round to 0. This prevents momentum-driven dead-Scap collapse: a Scap with zero momentum receives zero update forever (§12.4).

### 4.7 Forward-pass behavior

A Scap is passive during forward pass. Its weight capacitor sources current through its cascode; that current sums with other Scaps' currents at the post-synaptic neuron's summing junction. The current itself is measured externally by the Ganglion's ALU (§5.4).

**Forward_Sign update (new in 4.1).** During the forward pass, a small XOR circuit local to each Scap computes `sign(input_a) XOR Sign_SRAM` and latches the result into `Forward_Sign_SRAM`. This is one XOR gate plus one D-flipflop per Scap — negligible area. Under ReLU activations the result is degenerate (always equals `Sign_SRAM`); under signed activations the latched value carries genuinely new direction information used during backprop (§4.8).

### 4.8 Backward-pass behavior — fully autonomous

When `update_signal` goes high on the Ganglion-local bus, the Scap reads four signals locally and computes its own update:

```
direction = Forward_Sign_SRAM XOR feedback
weight_cap -= pulse_width × momentum × direction
```

**The two factors serve different duties:**

- **`pulse_width`** is the **global update-time control**, the same value for every Scap on this bus. It is the share that arrived at this Ganglion after hierarchical diffusion. Functions as a learning-rate / total-update-magnitude signal.
- **`momentum`** is the **per-Scap contribution history**, accumulated across the batch. Functions as the Scap's own importance.

The differentiation between Scaps within a Ganglion comes entirely from their differing momenta. The differentiation between Ganglia comes from their differing pulse widths (post-diffusion). Together they produce the right update structure.

**Why `Forward_Sign_SRAM` instead of just `Sign_SRAM` (new in 4.1):**

`Sign_SRAM` is the sign of the weight itself. `Forward_Sign_SRAM` is the sign of the _product `a · W`_ during the last forward pass — i.e., did this Scap push the post-synaptic neuron's sum positive or negative?

- For ReLU activations, `a ≥ 0` always, so `sign(a · W) ≡ sign(W)`. In this case `Forward_Sign_SRAM = Sign_SRAM` and the new mechanism provides no benefit.
- For signed activations (the L4 output layer has _no clip_ per §5.2, so L1 inputs to the next Ganglion are signed), `sign(a · W)` can differ from `sign(W)`. Then `Forward_Sign_SRAM` carries real new information.

**The L1→L2 Scaps benefit; L2→L3 and L3→L4 do not under ReLU.** Out of 29 Scaps per Ganglion, 9 benefit. The Forward_Sign_SRAM is filled for all 29 for hardware uniformity (it's just an XOR gate plus 1 bit) but only the 9 input-layer Scaps see useful direction information unless we move to signed activations everywhere (§20.5 tanh option).

**Why this matters for multi-parent diffusion (full discussion in §7.4):** when a Lobe has multiple parents wanting opposite update directions on the same Column, the magnitude of shares sums correctly, but the global `feedback` direction loses the per-parent direction context. `Forward_Sign_SRAM` lets each Scap know whether it personally pushed positive or negative during the forward pass. Combined with the global `feedback` (direction of total loss), the XOR gives the correct per-Scap update direction even when parents disagreed.

**Worked example.** Consider two Scaps A and B in the same Ganglion, both in the L1→L2 layer. Momentum_A = 100, Momentum_B = 10. In the last forward pass, Scap A pushed positive (Forward_Sign_A = +), Scap B pushed negative (Forward_Sign_B = −). Loss broadcast: `pulse_width = 50`, `feedback = +` (prediction was too low, need to increase output).

- direction*A = + XOR + = − → ΔW_A = −50 × 100 × (−) = +5000. \_Scap A's weight increases (it was helping push positive — push it more.)*
- direction*B = − XOR + = + → ΔW_B = −50 × 10 × (+) = −500. \_Scap B's weight decreases (it was pushing negative when we needed positive — reduce its negative contribution.)*

Both updates correctly serve the goal of increasing the output, despite A and B having opposite Forward signs. The XOR resolves the direction conflict locally per Scap.

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

The Ganglion ALU drives the forward pass _and_ measures per-Scap contribution simultaneously.

| Component                        | Count        | Role                                                            |
| -------------------------------- | ------------ | --------------------------------------------------------------- |
| Hardwired 2-3-3-2 op-amp circuit | 1            | Performs the forward computation                                |
| Input capacitors                 | 2            | Hold forward-pass inputs                                        |
| Output capacitors                | 2            | Receive forward-pass outputs                                    |
| Measurement capacitors           | 29           | One per Scap — tracks current that Scap delivered               |
| Time-measure circuit             | 1            | Converts time-to-threshold to contribution magnitude            |
| Temp SRAM                        | 29 × 16 bits | Transient storage of measurements before EMA into Scap momentum |

**Measurement cycle (runs in parallel with forward pass):**

1. Inputs charge input capacitors.
2. Hardwired 2-3-3-2 computes forward pass.
3. Each Scap's measurement cap charges at a rate proportional to the current that Scap delivers.
4. Time-measure circuit clocks the rise from A% to B% on each measurement cap.
5. **The time-measure circuit converts time-to-threshold into contribution magnitude.** Shorter time = stronger contribution; the conversion is folded into the measurement circuit. By the time the value lands in temp SRAM, it already represents contribution magnitude directly — downstream logic does not need to invert.
6. At end of forward pass, each measurement is:
   - Used immediately for the Ganglion's contribution to its parent Column (sum, for §12 distribution).
   - EMA-blended into the corresponding Scap's momentum SRAM (§4.6).

**Calibration.** The A%/B% thresholds reference a calibration cap inside the ALU. This makes time-to-threshold a _ratio_ measurement, robust to voltage drift and temperature.

**Range Sensitivity (Programmable Gain Amplifier, new in 4.1).** The op-amp circuit feeding each measurement cap includes a switchable resistor ladder (PGA) that adjusts gain. Two operating modes:

- **Coarse mode (default during early training):** Gain = 1×. Wide dynamic range. Strong contributors charge fast; weak contributors may hit `T_max` and be clipped to minimum contribution. Acceptable in early training because all weights are noisy anyway.
- **Fine mode (activated during deep convergence):** Gain = 10× or 100×. Weak currents that previously got clipped at `T_max` now charge fast enough to be discriminated. Loss of dynamic range at the top is acceptable because mature weights have already settled to moderate magnitudes.

**Triggering Range Sensitivity:**

- **Global trigger from Brainstem (§11.2):** when global loss drops below a threshold (deep convergence detected), Brainstem broadcasts a single bit to switch all Lobes into fine mode.
- **Local auto-trigger per Lobe:** the Lobe maintains a small counter tracking how many of its Scaps hit `T_max` in the last forward pass. If more than 80% hit `T_max`, the Lobe locally switches into fine mode without waiting for Brainstem. Recovers resolution exactly where it's lost.

**Forward-pass timing.** The forward pass cannot complete until the slowest measurement cap finishes its threshold crossing. Worst case: `T_forward = max(output_cap_charge_time, slowest_measurement_time)`. Default mitigation: cap measurement time at `T_max`; Scaps that don't cross threshold by then get `T_max` recorded (i.e. minimum contribution). Range Sensitivity (above) directly attacks the `T_max` clipping problem by ensuring weak signals are still discriminable.

### 5.5 ALU reuse

One Ganglion ALU is _reused_ across many Ganglia in a Column. The ALU steps through Ganglia sequentially, holding intermediate values in global capacitors (§6). This keeps total ALU count manageable.

For 256 Ganglia in a region, a single ALU executes 256 forward passes per inference cycle. The forward-pass time is bounded, not the ALU count.

### 5.6 Why 2-3-3-2 specifically

Two complementary justifications:

**Biological:** One Ganglion represents one biological axon with multi-synapse output behavior. The 2-3-3-2 expansion-contraction pattern models the way a real synapse takes input, distributes through multiple dendritic branches with varying density and hormone levels, recombines through summation thresholds, and produces a graded output. Not a literal model — a structural abstraction.

**Mathematical:** 2×3×3×2 = 36 distinct paths from input to output, with 29 scaps. Optimizes **path diversity per scap**. Alternative topologies for future testing:

| Topology          | Paths | Scaps | Paths/scap |
| ----------------- | ----- | ----- | ---------- |
| 2-3-3-2 (default) | 36    | 29    | 1.24       |
| 2-5-5-2           | 100   | 49    | 2.04       |
| 3-5-5-3           | 225   | 76    | 2.96       |
| 1-5-1             | 5     | 16    | 0.31       |

Higher paths-per-scap is probably better. Test only after H1 (§16) is locked.

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

| Size          | Use case                                   |
| ------------- | ------------------------------------------ |
| 2:2           | Identity-shape translation between Ganglia |
| 2:4           | Expand into a wider Column body            |
| 4:2           | Compress to match Ganglion input           |
| 4:4           | Same-dimension translation                 |
| 4:5, 5:5, 5:4 | Asymmetric reshaping                       |
| 8:4           | Multi-input fusion (used in Lobe, §7)      |

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

Status: deferred to §20. The default is Ganglion-level bypass only.

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

**The magnitude rule:** a Column with multiple parents sums all incoming shares into a single combined share before diffusing further down.

```
combined_share = Σ shares_from_parents
```

This sum then becomes the share that this Column distributes to its own children (Ganglia and translate ALUs inside it).

**The direction problem (and its fix — clarified in 4.1).** Naive share-summing handles magnitude but loses direction. If Parent A wants this Column's weights to increase and Parent B wants them to decrease, the global `feedback` signal can only carry one direction.

The fix is **per-Scap `Forward_Sign_SRAM`** (§4.2, §4.8). Each Scap remembers whether IT pushed positive or negative during its last forward pass, independent of the global feedback direction. At update time, `direction = Forward_Sign XOR feedback` gives the correct per-Scap update direction:

- A Scap that pushed positive when the system wanted positive output → update increases its weight.
- A Scap that pushed negative when the system wanted positive output → update decreases its weight.

This holds even when Parent A and Parent B disagreed on the desired direction. Each Scap resolves its own update based on what it personally contributed, not on a global vote.

**Caveat:** Forward_Sign only carries new information when activations can be signed. Under ReLU (default for L2/L3 hidden layers), `Forward_Sign ≡ Sign_SRAM` and the mechanism is degenerate at those layers. It still helps at L1→L2 Scaps (input layer) where inputs from prior Ganglia's L4 outputs are signed. See §4.8 for full discussion.

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

G's Scaps are shared across calls, but each call uses a _different sub-network within G_. Different masks → different active sub-networks → different effective computation.

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

- **Reservoir-G fallback:** initialize G with diverse non-zero random weights and _freeze_ it. All learning happens in S₁, S₂, S₃. This is reservoir computing — a well-studied technique with established theory.

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
- Their _difference_, carried through the Commissure, is the prediction error that drives learning across both Lobes. This is the predictive-coding pattern.

### 9.5 Input quality asymmetry

Cortex receives full input; Hippocampus receives input passed through an **Input Reducer** that destroys fine detail (e.g. 20 features → 5 features via a small fixed Ganglion or hardwired reducer).

Without this, Hippocampus could short-circuit the loop by predicting input directly from raw input, bypassing the recurrent dynamic. The reducer forces Hippocampus to rely on Cortex's signal via Commissure for fine-grained prediction.

### 9.6 Recurrence stability — the decay term

A recurrent system with non-zero gain in its feedback loop can amplify noise. To prevent this, the Commissure output is multiplied by a **decay factor** (default 0.9) before entering the receiving Lobe. Implementable as a passive resistor divider — zero compute cost.

This is the architecture's equivalent of biological inhibitory interneurons or modern layer normalization. Without it, the loop is unstable. **The decay is mandatory.**

### 9.7 Backward flow

1. _Forward (every clock):_ Both Lobes run forward. Both produce two-head outputs. Distribution memory fills at every level (Lobe / Column / Ganglion / Scap).
2. _Loss compute:_ Brainstem reads both predictions, computes losses, broadcasts on per-Lobe buses.
3. _Diffusion (six clocks):_ Loss diffuses through Lobe → Column → Ganglion → Scap on the active bus.
4. _Scap updates:_ Active Lobe's Scaps update locally. Inactive Lobe's Scaps don't see an update pulse but continue accumulating momentum from forward passes.

**Cortex's bus is active every clock. Hippocampus's bus is active every k-th clock. Commissure's bus is active every M-th clock.**

**Bus routing inside the Limbic Loop (clarified in 4.1).** The Limbic Loop has its own top-level bus carrying the loss broadcast from Brainstem. From that bus, three sub-buses branch:

- **Cortex Lobe bus** — feeds the Cortex Lobe's internal distribution.
- **Hippocampus Lobe bus** — feeds the Hippocampus Lobe's internal distribution.
- **Commissure bus** — feeds the Commissure Ganglia between the two Lobes.

The Brainstem gates each sub-bus independently. From the Lobe sub-bus, hierarchical diffusion proceeds normally down through Columns → Ganglia → Scaps using the Lobe-local, Column-local, and Ganglion-local buses respectively.

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

**Why slow Commissure matters.** The Commissure carries the signal that _both_ Lobes backpropagate against. If the Commissure updates too quickly, it destabilizes the entire loop — both Lobes are chasing a moving target. A slow Commissure gives the Lobes a stable reference to converge against.

### 10.4 Why heavy compute here is affordable

Only one Commissure exists per Limbic Loop. Spending more Scaps on it doesn't blow the total budget. The Commissure can be larger and richer than its sender-Lobe / receiver-Lobe topology would suggest.

### 10.5 Optional: Synaptic Drift in the Commissure

The Commissure is a natural home for **Synaptic Drift** (§20) — learnable per-synapse 1D position. Cross-region routing benefits from spatial-position learning more than within-region computation. Activate Synaptic Drift in the Commissure first.

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
- **Broadcasts Range Sensitivity mode (new in 4.1):** detects when global loss falls below convergence threshold and switches all Lobes into PGA fine mode (§5.4). Also collects local override requests from Lobes that hit the 80%-clipping auto-trigger.
- **Manages Auto-Zeroing phase (new in 4.1):** at configurable intervals (e.g. every N forward passes), drives input to ground for one clock to let each Lobe's Dummy Scaps capture current thermal offsets (§14.3).
- Holds the **community map** defining which Routes belong to which Lobe / Column (set at boot, read-only after).

**Label routing (clarified in 4.1).** Labels arrive at the chip via a dedicated label input bus, separate from the data input bus. The Brainstem reads labels directly from this bus into its own internal buffer. Labels are not treated as weights and do not flow through the Scap hierarchy. This means the chip has _two_ external input channels (data + label) and one external output channel (predictions). H5 (no weight LDR/STR during operation) holds: weights still never leave the substrate.

### 11.3 Size and complexity

Estimated 8–15k transistors equivalent (slightly grown in 4.1 due to Range Sensitivity broadcast logic, label buffer, and Auto-Zeroing controller). Tiny compared to a CPU. Large enough to require explicit design.

Implementation: a small hardwired state machine plus a few MAC units, plus ADCs and pulse-width modulators. Not a programmable processor.

### 11.4 What the Brainstem is _not_

- Not a CPU. No instruction set, no fetch/decode.
- Not a backprop engine. Does not compute gradients.
- Does not know about individual Scaps. Speaks only to the top of the hierarchy.

### 11.5 Future: distributed loss compute

If each output Ganglion can sense its own (prediction − label) locally — by routing the label voltage to the output Ganglia — the Brainstem's loss compute disappears. Brainstem shrinks to label-broadcaster + clock.

Status: §20 future track. Currently bounded by ALU/routing budget.

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

**Vanilla backprop is sensitivity-based.** It asks: _if I wiggle weight W by ε, how much does loss L change?_ The answer is `∂L/∂W`, computed via the chain rule by routing per-layer error signals `δ` backward through the _next layer's_ weights (`δ_l = W_{l+1}ᵀ · δ_{l+1} ⊙ σ'(z_l)`).

**This architecture is attribution-based.** It asks: _given that this Scap carried this much current during the forward pass, how much of the parent's error is attributable to it?_ The answer is a proportion: `share = parent_loss × (child_contribution / total_contribution)`. The "contribution" is what the analog substrate literally measures for free — the current through each Scap, which is proportional to `|a · W|`.

**The structural divergence:**

| Aspect                 | Vanilla (sensitivity)                                           | This architecture (attribution)                           |
| ---------------------- | --------------------------------------------------------------- | --------------------------------------------------------- |
| Routing error backward | Use next layer's W as transpose to route δ                      | Use `\|a · W\|` at current layer to split parent's share  |
| Weight in own update   | No (only `δ · a`)                                               | Yes (because `\|a · W\|` is what's measured)              |
| Information needed     | Per-neuron δ propagated from output, requiring weight transport | Per-Scap `\|a · W\|` measured locally during forward pass |
| Loss conservation      | By linearity of chain rule                                      | By explicit normalization                                 |
| Inactive units         | `σ'(z) = 0` kills propagation                                   | `\|a · W\| = 0` kills propagation                         |

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

1. **Dead-weight collapse.** Because `ΔW ∝ |a · W|`, a weight that reaches zero magnitude receives zero update and stays dead forever. The floor-at-1 momentum rule (§4.6) and the residual connections (§13) are the main mitigations. **Simulation must instrument zero-magnitude weight counts.**
2. **Momentum ceiling saturation (new in 4.1).** Symmetric to dead-weight: if a Scap consistently contributes very strongly, its 16-bit momentum SRAM saturates at the ceiling. Beyond that, EMA can't grow further. Differences between strongly-contributing Scaps are lost (all at ceiling). Mitigation: scale measurement before EMA accumulation (a per-Lobe gain factor that scales down as average contribution rises), or move to log-domain momentum. Track ceiling-hits in simulation; if more than 5% of Scaps saturate, implement a mitigation.
3. **Routing-update coupling.** The same `|a · W|` does both routing of loss and magnitude of update. Errors in one job contaminate the other.
4. **Slow convergence on tasks needing precise gradient.** Loss surfaces with narrow valleys may converge slower than under SGD.
5. **Initialization sensitivity.** Attribution-based methods are typically more sensitive to init than SGD.
6. **Activity vs Relevance (new in 4.1 — see H10).** High Scap activity (`|a · W|`) does not necessarily mean high _relevance_ to the actual loss. A Scap can be very active but its output is cancelled by other Scaps downstream — yet it still claims a large share of the loss. Long-tail features (low activity, high relevance) get under-updated. This is a known weakness of magnitude-based attribution methods. **Primary defense is Physical Saturation (§4.4)** — winners hit the supply rail and self-limit, giving runner-ups room to develop. If Phase 2 shows this isn't enough, escalate to Path 0 noise floor, §20.2 adaptive decay, or §20.4 Adam-style v_t.

**Four remediation paths, in order of cost:**

- **Path 0 (cheapest):** Add a tiny random noise floor to weight updates — every Scap gets a small random perturbation each update independent of measurement. Rescues dead weights without circuit changes. One-line addition.
- **Path 1:** Strip the multiplier from the measurement. Measure `|a|` only. Update becomes vanilla SGD `ΔW ∝ a · δ`. Cost: extra input sensors _and_ hierarchical diffusion loses routing signal (splitting loss by input alone is biased). Routing math needs fix.
- **Path 2:** Keep `|a · W|` for routing, add a separate input sensor for the update step. Most chain-rule-correct, most circuit-expensive.
- **Path 3 (current default):** Accept attribution-based, instrument failure modes, test empirically. Cost to find out is low; the architecture is already producing it for free.

Commit to Path 3 for baseline. Path 0 is the first remediation if dead-weight appears. Paths 1 and 2 documented for deeper failures.

### 12.5 Per-level precision allocation

Loss is multiplied at every level as it diffuses. Quantization compounds. Allocation:

| Level       | Distribution storage                     | Notes                        |
| ----------- | ---------------------------------------- | ---------------------------- |
| Limbic Loop | 16-bit SRAM per child                    | Top level — most bits matter |
| Lobe        | 12-bit SRAM per Column                   |                              |
| Column      | 10-bit SRAM per Ganglion / translate ALU |                              |
| Ganglion    | 29 measurement caps (analog)             | Continuous                   |
| Scap        | 16-bit momentum SRAM                     | EMA accumulation             |

Total stored distribution state is small (one number per child per module). Spending bits at the top is cheap.

### 12.6 Loss conservation as invariant

At every level, **additive shares**: `Σ children_shares = parent_loss`. The total loss flowing into a level equals the total flowing out. Holds at every backward pass within finite-precision tolerance ε.

This is verifiable in simulation. **It catches bugs immediately.** If conservation is violated by more than ε at any level, the implementation has a bug.

### 12.7 Normalization via analog op-amp

The division `child_contribution / total_contribution` happens in the **analog op-amp ALU**, not in binary. Standard op-amp ratio-of-currents or normalizing-summing-amplifier topology. One normalization circuit per level per forward pass.

**Recommended topology: Current Mirror (new in 4.1).** Implementing the division via a Current Mirror circuit makes the share computation _ratio-preserving_ by construction. The parent's total loss current is forced into a central node; the Current Mirror branches it out to children in proportion to their measured `|a · W|`. Even if absolute current levels drift due to thermal or supply variation, the _ratios_ between branches remain stable. This directly addresses analog robustness concern §14.4.

By the time anything lands in a Scap's momentum SRAM or a level's distribution memory, it is **already final-form, ready-to-use, no further division required**.

The architecture leans on this: continuous analog math is the cheap path, binary math is the expensive path. Normalization is a place where that bet pays off.

(Specific op-amp Current-Mirror topology choice is §20 future detail — for first simulation, assume the operation is available with bounded error.)

### 12.8 Backward pass timing

Backward pass is **synchronous and clock-driven**, six clocks total:

1. _Clock 0:_ Brainstem broadcasts total loss on global bus.
2. _Clock 1:_ Limbic Loop reads, computes child shares, broadcasts on Limbic-local bus.
3. _Clock 2:_ Lobes read, compute Column shares, broadcast on Lobe-local bus.
4. _Clock 3:_ Columns read, compute Ganglion shares, broadcast on Column-local bus.
5. _Clock 4:_ Ganglia read, compute per-Scap shares using measurement caps, broadcast on Ganglion-local bus.
6. _Clock 5:_ Scaps update weight capacitors locally via PWM.

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

This is residual connections (ResNets, He et al. 2016). Familiar in modern ML. But for _this_ architecture, it serves a different purpose than it does in standard ML.

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

**Lobe-level (effectively free via DAG topology).** Skip connections in the Lobe DAG (§7) are structurally residual connections. Column 1 → Column 3 directly, bypassing Column 2, _is_ a residual. Already part of the architecture.

So residuals operate at three levels: inside Ganglia (default), across Lobe DAGs (structural), and optionally between Columns.

### 13.5 Variance management

`H(x) = f(x) + x` has variance `var(f(x)) + var(x)` (assuming independence). Without management, variance grows through depth.

**Strategy:** initialize `f(x)` to produce small outputs at training start. With small initial Scap magnitudes (§18), `f(x)` starts close to zero; the bypass dominates; the Ganglion starts close to identity. This is the modern ResNet best practice.

As training proceeds, `f(x)` learns to produce a _small correction_ to the bypassed signal. The residual block learns a delta, not a full transformation.

For variance normalization across deeper depth, three options:

1. **Fixed scaling factor** — multiply each Ganglion's output by α < 1. Tune empirically. Cheapest.
2. **Analog normalizer circuit** — op-amp circuit that normalizes layer-output amplitude. Same circuit family as §12.7.
3. **Adaptive analog AGC** — feedback gain control. Well-studied in radio circuits. Most complex.

**Default for first simulation: option 1.** Tune α per layer empirically.

### 13.6 Distribution measurement with residuals

The Scap measurement (§5.4) measures the current through _the Scap_, which is the learned part `a · W`. The bypass current goes around the Scap and is not measured by it. So the per-Scap attribution is correct.

But at higher levels, the Ganglion's _output_ (which goes into the parent Column's distribution memory) now includes both the learned part and the bypass. The bypass contributes to the next-stage signal without having a learnable weight to attribute to.

**Fix:** at the Column / Lobe levels, measure _only the learned-path contribution_, not total output. The bypass is informational, not learnable, and should not show up in distribution memory.

**Physical implementation (clarified in 4.1).** The Ganglion has two output ports:

- **Learned output port** — sum of L4 op-amp results only. This port is what the upstream measurement circuit (the parent Column's distribution measurement) reads. It carries the learnable contribution.
- **Combined output port** — learned output summed with the L1→L4 bypass. This port feeds the next Ganglion's input. It carries the total signal.

The two ports diverge at a junction inside the Ganglion. The learned output is tapped _before_ the bypass summer; the combined output is the _output of_ the bypass summer. Both ports source from the same op-amp circuitry. Cost: one extra wire pair per Ganglion output (4 wires total per Ganglion).

This way, distribution memory at every level measures only learnable contribution, while forward computation correctly carries the bypassed signal. The two responsibilities are physically separated.

---

## 14. Analog Robustness Mechanisms

This section is new in 4.1. It addresses the physical realizability of the analog substrate under process variation, thermal drift, supply variation, and aging. These are not future-track optimizations — they are baseline architectural mechanisms required for the chip to function at all. The Python simulation in Phase 2 doesn't need all of them, but the architecture spec must include them so the simulation can be calibrated against realistic PVT-aware behavior.

### 14.1 The PVT problem

Analog circuits on silicon suffer from:

- **Process variation:** transistors and capacitors fabricated at different positions on the die have slightly different characteristics. Static and chip-specific.
- **Voltage variation:** supply rail droops under high activity. Local and dynamic.
- **Temperature variation:** active regions heat up faster than idle ones. Thermal gradients across the die change resistance and op-amp offsets. Dynamic and spatial.
- **Device aging:** transistor characteristics drift over years of operation. Very slow.

In a 5-level hierarchical diffusion architecture, even small per-level errors compound. A 2% error per level becomes ~10% by the time loss reaches a Scap. Loss conservation can break. Without explicit countermeasures, the architecture is not physically buildable.

### 14.2 Differential Pair op-amps

**The mechanism:** every op-amp in the analog ALUs uses a _differential_ topology — two matched transistors placed adjacent on the die, processing signal as the difference between two paths (`V+` and `V−`).

**Why this works:** thermal effects, supply droop, and slow drift hit both transistors equally. The differential output cancels common-mode drift physically, without any digital correction logic. Standard analog IC practice for a century.

**Cost:** ~2× transistor count per op-amp vs single-ended. Acceptable given the substantial robustness gain. Modern analog design assumes differential by default.

**Applies to:** all op-amp circuits, especially §12.7 normalization (Current Mirror), §5.4 measurement, and the Ganglion ALU.

### 14.3 Dummy Scap for on-the-fly calibration

**The mechanism:** every Lobe contains one **Dummy Scap** — a structurally identical Scap that receives a known reference current at every clock and reports its measurement output to a Lobe-level offset register.

**Why this works:** the Dummy Scap experiences the same process, voltage, and temperature conditions as the real Scaps in that Lobe. Its reading-minus-expected gives a per-Lobe per-clock offset that can be subtracted from real Scap measurements. Calibration is _continuous_ and _automatic_ — no separate calibration phase, no sample collection needed.

**Cost:** one Dummy Scap per Lobe (roughly 1/29 of a Ganglion's storage). ~3% area overhead per Lobe.

**Granularity options:**

- **Per Lobe:** captures thermal gradients between Lobes. Minimum reasonable granularity.
- **Per Column (finer):** captures gradients within a Lobe. More accurate, more overhead.
- **Per Ganglion (finest):** captures gradients within a Column. Best accuracy, highest overhead. Probably overkill.

**Default in 4.1:** one Dummy Scap per Column. Compromise between accuracy and overhead.

### 14.4 Current Mirror for ratio-preserving Loss Share

Already specified in §12.7. Restated here for completeness: the analog op-amp circuit that divides parent loss into children's shares is built as a **Current Mirror**, which preserves the _ratio_ between branches even when absolute currents drift due to thermal/supply variation.

The shares may all scale up or down together as conditions change, but their _relative_ magnitudes — which is what attribution-based learning depends on — stay correct.

### 14.5 Auto-Zeroing phases

**The mechanism:** at configurable intervals (say, every 100 forward passes), the Brainstem drives all input pins to ground for one clock cycle. During this "zero phase," every Lobe's measurement circuits capture the residual offset at their outputs (which should be zero in an ideal circuit, but isn't due to thermal/supply drift). Each Lobe latches this offset into a small per-Lobe SRAM. On the next normal forward pass, the Lobe subtracts this offset from its measurements.

**Why this works:** the offset captured during zero phase represents the _current_ drift state. By subtracting it from real measurements, real-time thermal and supply drift are cancelled regardless of magnitude.

**Cost:** one clock per N forward passes spent in zero mode (overhead ~1% if N=100). One small SRAM per Lobe for offset storage.

**Frequency tuning:** more frequent zero phases give better thermal tracking but more overhead. Tune empirically.

**Trade-off with continuous operation:** auto-zeroing introduces brief discontinuities in the forward stream. This is acceptable for most workloads. For workloads that genuinely cannot tolerate any pause, see Ping-Pong substrate (§14.6).

### 14.6 Ping-Pong substrate (optional)

**The mechanism:** twin substrates — Core A and Core B — operating in alternation. While Core A processes real workload, Core B runs auto-zeroing calibration. They swap roles periodically. The forward pipeline never sees a discontinuity.

**Cost:** ~2× substrate area. Substantial.

**Status:** optional, deferred. Use only if continuous operation is mandatory for the target application.

### 14.7 Range Sensitivity (PGA on measurement)

Already specified in §5.4. Restated here for completeness: a Programmable Gain Amplifier on the measurement circuit allows gain to be adjusted (1× / 10× / 100×) so weak signals can be discriminated during deep convergence. Triggered globally by Brainstem (when loss is low) or locally per Lobe (when >80% of Scaps hit T_max).

### 14.8 Summary of robustness layering

The architecture's resistance to analog imperfection comes from multiple layers stacked together:

| Layer                          | Defeats                                   | Cost                       |
| ------------------------------ | ----------------------------------------- | -------------------------- |
| Differential Pair op-amps      | Thermal drift, supply droop (common-mode) | ~2× transistors per op-amp |
| Dummy Scap                     | Process variation, slow thermal           | ~3% Lobe area              |
| Current Mirror Loss Share      | Absolute-value drift (preserves ratios)   | Op-amp topology choice     |
| Auto-Zeroing phase             | Fast thermal drift, fast supply drift     | ~1% time overhead          |
| Range Sensitivity (PGA)        | T_max resolution loss during convergence  | Switchable resistor ladder |
| Ping-Pong substrate (optional) | Pause intolerance                         | ~2× substrate area         |

None of these are exotic — all five are standard techniques in analog IC design. The architecture's contribution is the _layering_ — applying them together to support a multi-level hierarchical learning algorithm.

### 14.9 What Phase 2 simulation must include

The Python simulation does not need to model all of these physically. But it does need to _model their effects_, so the architecture's behavior under PVT is empirically known:

- **Process variation:** initialize each Scap and each op-amp circuit with a small per-instance multiplicative bias drawn from `N(1, 0.02)`. Held constant per chip-run.
- **Thermal drift:** add a slowly time-varying offset to each Lobe's measurements, function of Lobe activity (more active → more drift).
- **Auto-Zeroing:** at simulated intervals, capture and subtract the current drift offset.
- **Loss conservation tracking:** log `Σ shares − parent_loss` at every level, every backward pass. Report epsilon.
- **Range Sensitivity:** track T_max-clip rate per Lobe; switch to fine mode when threshold exceeded.

The simulation can validate that the robustness mechanisms keep loss-conservation epsilon below ~5% across the hierarchy under realistic PVT — which is the bar for the architecture being buildable.

---

## 15. Routes Hierarchy — physical layout

### 14.1 Goal

Ganglia occupy a 2D grid. Addressing must be cheap.

### 14.2 Two-level addressing

- **Route L1**: 4-bit address selects one of 16 unit-route Ganglia (horizontal axis).
- **Route L2**: 4-bit address selects one of 16 L1-route groups (vertical axis).
- **Total per region: 256 Ganglia.**

> Route L1 / L2 are _addressing levels_, unrelated to Ganglion-internal L1–L4.

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

## 16. Hypotheses (the testable claims)

Each is falsifiable. The simulation exists to test them.

**H1 — Attribution-based hierarchical diffusion converges on substantive tasks.**
Loss broadcast from the Brainstem, diffused through five levels of distribution memory using `|a · W|` as the attribution quantity, arriving at Scaps as PWM update pulses, can drive the system to convergence on tasks vanilla SGD would also solve. Convergence is empirical, not theoretically guaranteed. _Central open research question._

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
Combined effect of floor-at-1 momentum (§4.6), residual connections (§13), and tunable refill (§4.5) keeps the fraction of dead Scaps below 5% after Phase 2 training runs. If H7 fails, escalate to Path 0 (noise floor on weight updates, §12.4).

**H8 — Residual connections reduce dead-weight rate and accelerate convergence.**
Ganglion-level residual bypass measurably reduces dead-Scap fraction and improves convergence speed on the Phase 2 task suite, compared to a non-residual baseline of identical topology.

**H9 — Lobe-level multi-branch composition outperforms sequential Columns.**
A Lobe with DAG topology (parallel branches, skip connections) achieves better expressivity per Scap than a sequential Column of equal Scap count. Tested in Phase 3+.

**H10 — Activity vs Relevance gap is bounded under attribution learning (new in 4.1).**
The external critic flagged a fundamental concern: high Scap activity (`|a · W|`) doesn't necessarily mean high relevance to loss, so attribution-based updates could systematically over-update active-but-irrelevant Scaps. The architecture's primary defense is **Physical Saturation (§4.4)**: weight capacitors hit the supply rail and self-limit, naturally bounding winner-take-all dynamics. We hypothesize this is sufficient for convergence on substantive tasks. Phase 2 simulation must verify the saturation-rate matches the attribution-update-rate well enough — too slow and winners dominate too long, too fast and no Scap differentiates. If physical saturation alone proves insufficient, three additional remediation paths (explicit Physical Weight Decay via tunable refill §4.5, Anti-Hebbian gating, Adam-style v_t per Scap — see §20) are documented but deferred.

**H11 — Forward_Sign_SRAM resolves multi-parent direction conflict (new in 4.1).**
The per-Scap `Forward_Sign_SRAM` mechanism (§4.8) correctly resolves update direction when a Lobe has multiple parents with conflicting desired update directions. Tested in Phase 3 (multi-branch Lobe simulation). Note: the mechanism is degenerate under ReLU activations — H11 is fully testable only with signed activations or at L1→L2 layers.

---

## 17. Math to Justify (priority targets)

Written justifications to develop alongside simulation:

1. **Time-to-threshold to contribution conversion.** Show that under constant-current capacitor charging, the time-measure circuit's output is linear in contribution magnitude.

2. **Attribution preserves monotonicity of update magnitudes.** Scaps that contributed more receive larger updates. This is the minimum mathematical property required — not equivalence to gradient. Empirical comparison against SGD as a diagnostic.

3. **Loss conservation invariant.** `Σ children_shares = parent_loss` at every level, every clock.

4. **Multi-parent diffusion preserves loss conservation.** When a child has multiple parents, the sum of shares it receives equals the sum of contributions its parents assigned to it.

5. **Dead-weight collapse rate is bounded.** Given initialization `(μ_init, σ_init)`, floor-at-1 momentum rule, and residual connections, derive an upper bound on expected fraction of zero-magnitude Scaps after N training steps.

6. **EMA momentum with α=3/4 is contractive.** Under bounded measurement inputs, momentum stays bounded.

7. **Physical saturation as implicit regularizer (§4.4).** Constant-pulse PWM charging produces a stable fixed point at supply rails. Derive the equilibrium of N competing Scaps in the same Ganglion under attribution-weighted updates plus physical saturation: show that no single Scap dominates the entire weight range; show that the steady-state weight distribution depends on relative contribution rates, with saturation acting as the upper-bound balancer. This is the math companion to H10.

8. **Limbic Loop stability with decay factor.** Conditions on Cortex / Hippocampus / Commissure rates and decay factor that prevent oscillation or collapse.

9. **SpecialGeneralist capacity bound.** Why gated G achieves higher effective parameter count than plain G-reuse.

10. **Residual variance management.** Show that with initial Scap magnitude `σ_init` and per-layer scaling α, output variance stays bounded across depth.

11. **Low-grade input bottleneck.** How much feature reduction prevents Hippocampus short-circuiting without destroying category structure.

12. **Sign-magnitude representation correctness.** `sign_SRAM × cap_magnitude` is functionally equivalent to signed weight across all operations.

---

## 18. Open Questions

In rough priority order:

1. **Does attribution-based hierarchical diffusion converge on substantive tasks?** Phase 2 answers.
2. **Dead-weight collapse rate.** What fraction of Scaps die in Phase 2? Is floor-at-1 + residuals enough, or do we need Path 0?
3. **Activity vs Relevance gap (H10, new in 4.1).** Phase 2 must measure: when a Scap has high `|a · W|` but the loss doesn't change (cancellation downstream), does it nonetheless claim large share? If yes, what fraction of Scaps are in this state? Most importantly: **is Physical Saturation (§4.4) self-limiting fast enough** to bound winner-take-all dynamics, or do we need to escalate to one of the §20 deferred fixes (§20.2 adaptive decay, §20.4 Adam-style v_t)?
4. **Physical Saturation rate calibration (new in 4.1).** Supply rail voltage and PWM pulse width together set the saturation rate. Phase 2 must measure: how many forward passes until highest-`|a · W|` Scaps saturate? Target: somewhere in the 20–50% of training mark. If <10%, saturation is too fast and no Scap differentiates. If >80% or never, too slow and winner-take-all dominates.
5. **Momentum ceiling saturation (new in 4.1).** What fraction of Scaps hit the 16-bit momentum ceiling? If >5%, implement log-domain momentum or gain scaling before EMA.
6. **Forward_Sign_SRAM benefit under ReLU (new in 4.1).** Empirically: does the mechanism help at L1→L2 Scaps (the 9 input-layer Scaps per Ganglion) enough to justify the per-Scap area cost? Test with multi-branch Lobe.
7. **Per-level precision allocation.** 16/12/10/continuous/16 is provisional. Refine empirically.
8. **Time-to-threshold A%/B% calibration.** 10/30 vs 20/80 vs 30/70 — test.
9. **Range Sensitivity trigger thresholds (new in 4.1).** Global loss threshold for fine mode? Local T_max-clip percentage threshold? Both empirical.
10. **Auto-Zeroing frequency (new in 4.1).** Every 100 forward passes, 1000, or activity-dependent? Empirical.
11. **Dummy Scap granularity (new in 4.1).** Per Lobe, per Column, or per Ganglion? Default per Column.
12. **SpecialGeneralist mask source.** Start hardcoded; escalate if needed.
13. **SpecialGeneralist mask overlap policy.** Mutually exclusive vs overlapping — start exclusive.
14. **Two-timescale ratio k.** k = 8, 16, 32 — empirical.
15. **Commissure rate M.** M > k. Sweet spot — empirical.
16. **Decay factor in recurrence.** 0.9 default. Test 0.8 / 0.9 / 0.95.
17. **Hippocampus consolidation pulse-width policy.** Three options in §9.8.
18. **Forward-pass slow-cap mitigation.** Default cap-at-T_max; Range Sensitivity addresses the resolution issue.
19. **Initialization scheme.** Small uniform magnitudes + random signs + zero momentum. Concrete starting values: weight magnitudes ~10% of capacitor range, signs uniformly random. Compare against Xavier/He analog equivalent.
20. **Residual variance scaling α.** Per-layer factor. Tune empirically.
21. **Concrete Phase 4 task.** Sequence-prediction-with-cue-completion is recommended candidate.
22. **One region or two?** Is 256 Ganglia enough for the target task?
23. **Op-amp normalizer topology choice.** Specific Current Mirror variant for §12.7.
24. **PVT simulation realism (new in 4.1).** How accurately should Phase 2 model thermal/process variation? Trade-off between realism and simulation speed.

---

## 19. Simulation Plan

Seven phases. Each closes the previous phase's open questions before the next opens.

### Phase 1 — Operator layer

Ideal-model versions of every analog primitive: add, multiply, ReLU, capacitor charge dynamics, time-to-threshold, PWM update. Unit tests.

**Simulation type:** discrete-time Python at ~1 ms resolution. Continuous-time analog behavior approximated by Euler integration of cap voltages. Real-time SPICE simulation deferred to §20.16.

**Exit:** all operators behave as a perfect analog circuit would within the discrete-time approximation.

### Phase 2 — Single Ganglion + attribution diagnostic harness

Build one 2-3-3-2 Ganglion with Scap class. Implement attribution-based update.

**Diagnostic harness:** run attribution and a vanilla-SGD baseline on identical topology, same task. Record:

- Convergence curves of both.
- Cosine similarity between attribution and SGD update vectors (diagnostic, not pass/fail).
- **Fraction of dead Scaps** over training (`|weight_cap| < 1% of capacitor range`).
- **Fraction of ceiling-saturated Scaps** (momentum SRAM at max value).
- **Activity vs Relevance gap** (new in 4.1): for each Scap, log `|a · W|` (claimed share) vs change in loss when that Scap is ablated. Wide gap = relevance problem.
- Weight magnitude distribution at end of training.

**Tasks:** XOR, 1D regression (sine), 2D classification (two-moons).

**PVT realism (new in 4.1):** include simulated process variation (per-Scap multiplicative bias from `N(1, 0.02)`) and simulated thermal drift (slow per-Lobe offset). Validate that Loss Conservation epsilon stays below 5% across the hierarchy.

**Tests H1, H7, H8** (compare with-residual vs without-residual), **H10** (Activity vs Relevance instrumented).

**Exit:** attribution converges on at least two of three tasks; dead-weight fraction < 5%; ceiling-saturation < 5%; convergence within an order of magnitude of SGD.

### Phase 3 — Column with SpecialGeneralist

Compose Ganglia into Columns. Implement gated G-reuse, mask gating, EMA-momentum-with-masks.

**Tests:** SpecialGeneralist vs plain G-reuse vs flat chain of equal Scap count.

**Tests H2.**

**Exit:** SpecialGeneralist beats plain G-reuse on at least one task; else fall back to Reservoir-G.

### Phase 4 — Lobe with multi-branch DAG

Build a Lobe with multi-parent Columns. Implement multi-parent diffusion (shares from multiple parents sum).

**Tests:** Multi-branch Lobe vs sequential single-Column.

**Tests H9, H6** (loss conservation holds under multi-parent), **H11** (Forward_Sign resolves direction conflict — test specifically with paired multi-parent setup where parents want opposite directions).

**Exit:** Multi-branch beats sequential on at least one expressivity test; Forward_Sign mechanism measurably reduces gradient-conflict-induced training instability.

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

## 20. Future Tracks — Optional and Deferred Mechanisms

### 20.1 Per-neuron residual connections

Internal residuals at every layer of the Ganglion. Requires dimension matching at every step — either projection circuits or topology change to 3-3-3-3.

### 20.2 Adaptive per-Scap weight decay

Tunable refill SRAM (§4.5) dynamically adjusted based on weight magnitude. Stronger decay on saturated Scaps; weaker on dead Scaps. Homeostasis at long timescales.

### 20.3 Local-aware update normalization

Each Scap exposes its remaining headroom; updates scaled to keep epoch-level update capacity uniform across Scaps. Connects to §20.2 via the recharge SRAM mechanism.

### 20.4 Adam-style v_t per Scap (new in 4.1)

Add a second 16-bit SRAM per Scap holding `v_t = β₂ × v_{t-1} + (1-β₂) × (pulse_width × momentum)²` — squared-update history. Effective update becomes `ΔW ∝ (pulse_width × momentum × direction) / √v_t`. Provides explicit per-Scap rate adaptation (slow already-large-update Scaps, fast under-updated Scaps).

Cost: doubles per-Scap SRAM (from ~30 to ~46 bits). Requires analog 1/√ circuit or ADC + digital divider per Scap.

**Status:** probably unnecessary. Physical Saturation (§4.4) already provides upper-bound self-limiting behavior. Promote to baseline only if Phase 2 shows saturation alone is insufficient to control winner-take-all dynamics — specifically if the highest-`|a · W|` Scaps saturate quickly but other Scaps still fail to differentiate.

### 20.5 Activation mixing — tanh instead of ReLU

Replace L2/L3 ReLU with tanh-like saturation (unclipped op-amp at supply rails). Continuous gradient everywhere. Free in hardware. **Bonus:** makes Forward_Sign_SRAM (§4.2, §4.8) carry useful information at all 29 Scaps per Ganglion (instead of just the 9 L1→L2 input Scaps). Likely promoted to baseline once Phase 2 validates the ReLU version.

### 20.6 Synaptic Drift

Each synapse has a learnable 1D address; signal scales by distance. Activate first in Commissure (§10.5). Analog-position version (capacitor + comparator ladder) is a clean future direction.

### 20.7 Engram Buffer (short-term memory)

Pure capacitor network acting as LSTM-like layer. Stacks between Cortex and Hippocampus. Not specified — revisit after H3.

### 20.8 Cell-fire (STDP)

Hebbian spike-timing-dependent plasticity for group-level rewiring. Open research thread.

### 20.9 Distributed loss compute

Each output Ganglion senses its own (prediction − label) locally. Brainstem shrinks to label-broadcaster + clock.

### 20.10 2-capacitor analog momentum

Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage. Eliminates ADC/SRAM at the Scap level. Post-baseline optimization.

### 20.11 Floating-gate transistor storage

Replace refilled capacitor + 8-bit SRAM with FGT (NAND-flash technology, Mythic AI's choice). Years of retention without refresh.

### 20.12 Op-amp normalizer topology

Specific circuit choice for §12.7 normalization. Multiple candidates from the analog computing literature.

### 20.13 Column-level residual bypass

Optional residual at the Column level (input → output direct path). For deep Columns.

### 20.14 Inference-only low-power mode

Disable backprop circuitry; just forward inference. Trivial mode bit.

### 20.15 Failure mode handling

Dead-Scap recovery, stuck-attractor escape, range-drift correction. Provisional: noise injection. Better mechanisms after empirical failure modes are seen.

### 20.16 SPICE / robustness simulation

After Python ideal-model converges: SPICE simulation of single Scap; noise-injected Python model calibrated against SPICE; degradation quantification.

---

## 21. What Not To Touch (the protected list)

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
10. **Forward_Sign_SRAM in every Scap (new in 4.1).** Resolves multi-parent direction conflict. 1 bit per Scap, XOR-based logic. The full hardware uniformity (all 29 Scaps per Ganglion have it, even the 20 that are degenerate under ReLU) is a deliberate trade-off for circuit simplicity.
11. **Differential Pair op-amps throughout (new in 4.1).** Standard practice for analog robustness. Not optional.
12. **Dummy Scap per Column for calibration (new in 4.1).** Granularity could be debated, but having _some_ on-die reference is mandatory.
13. **Current Mirror for Loss Share normalization (new in 4.1).** Ratio preservation is what makes hierarchical diffusion physically tolerable under PVT.
14. **Physical Saturation as primary defense against winner-take-all (new in 4.1).** The capacitor charging behavior near the supply rail is the architecture's primary answer to Activity vs Relevance / H10. Don't try to engineer around it with software-flavored normalizers before validating the physics in Phase 2.

Everything else — precision allocations, decay factors, mask sources, timescale ratios, initialization, Auto-Zeroing frequency, Dummy Scap granularity, saturation rate calibration — is up for negotiation as simulation data arrives.

---

## 22. Glossary

| Term                                             | Meaning                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Scap**                                         | Atom of storage. SRAM + Capacitor cell holding one synapse weight. Now includes `Forward_Sign_SRAM` (4.1).                                                                                                                                                                                                                                                                                       |
| **Forward_Sign_SRAM** _(new in 4.1)_             | 1-bit per-Scap SRAM holding `sign(input_a) XOR Sign_SRAM` from the last forward pass. Resolves multi-parent update direction conflict via `direction = Forward_Sign XOR feedback`. Degenerate under ReLU; meaningful only with signed activations or at L1→L2 input layer.                                                                                                                       |
| **Ganglion**                                     | Atom of computation. Hardwired 2-3-3-2 network, 29 Scaps. Includes default residual bypass. Has two output ports: learned-only (for measurement) and combined (for next stage).                                                                                                                                                                                                                  |
| **Column**                                       | Sequential composition of Ganglia connected by learnable translate ALUs.                                                                                                                                                                                                                                                                                                                         |
| **Lobe**                                         | Multi-branch DAG composition of Columns. Brain-region scale.                                                                                                                                                                                                                                                                                                                                     |
| **Limbic Loop**                                  | Top-level recurrent system. Cortex Lobe + Hippocampus Lobe + Commissure + decay term.                                                                                                                                                                                                                                                                                                            |
| **Cortex Lobe**                                  | Fast-learning Lobe. Updates every clock. Two output heads.                                                                                                                                                                                                                                                                                                                                       |
| **Hippocampus Lobe**                             | Slow-learning Lobe. Same topology as Cortex; updates every k clocks. Two output heads.                                                                                                                                                                                                                                                                                                           |
| **Commissure**                                   | Inter-Lobe connector. Small Ganglion group, trainable at reduced rate (every M clocks).                                                                                                                                                                                                                                                                                                          |
| **Brainstem**                                    | Central controller. Loss compute, broadcasts, clocks, per-Lobe gating, Range Sensitivity broadcast, Auto-Zeroing scheduling. Estimated 8–15k transistors.                                                                                                                                                                                                                                        |
| **Generalist (G)**                               | Reused Ganglion inside a Lobe under context masks (SpecialGeneralist).                                                                                                                                                                                                                                                                                                                           |
| **Specialist (S₁, S₂, S₃)**                      | Ganglia that drive G under different masks.                                                                                                                                                                                                                                                                                                                                                      |
| **SpecialGeneralist**                            | Gated Ganglion reuse — G with context masks from Specialists.                                                                                                                                                                                                                                                                                                                                    |
| **Translate ALU**                                | Learnable analog reshaping element between Ganglia or between hierarchy levels.                                                                                                                                                                                                                                                                                                                  |
| **Global capacitor**                             | Inter-step buffer holding transient state. Not weight storage.                                                                                                                                                                                                                                                                                                                                   |
| **Residual bypass**                              | Input-to-output direct wire summed with computed output. Defense against dead-weight.                                                                                                                                                                                                                                                                                                            |
| **Hierarchical Diffusion**                       | The learning mechanism. Loss diffuses through level shares from top.                                                                                                                                                                                                                                                                                                                             |
| **Distribution memory**                          | Per-level storage of children's contributions. SRAM at high levels, measurement caps at Ganglion level, momentum SRAM at Scap level.                                                                                                                                                                                                                                                             |
| **Momentum SRAM**                                | 16-bit per-Scap accumulator of contribution. EMA with α=3/4. Floor-at-1 rule; ceiling-saturation watched (4.1).                                                                                                                                                                                                                                                                                  |
| **Refill / decay SRAM**                          | 8-bit per-Scap reference for leakage compensation; doubles as tunable weight-decay regularizer.                                                                                                                                                                                                                                                                                                  |
| **PWM update**                                   | Pulse-width-modulated weight cap update. Written locally per Scap.                                                                                                                                                                                                                                                                                                                               |
| **Pulse-width**                                  | Global update-time control. Same value for all Scaps on a bus. LR-like.                                                                                                                                                                                                                                                                                                                          |
| **Tri-ode feedback**                             | Global wire carrying loss direction `(+, 0, −)`.                                                                                                                                                                                                                                                                                                                                                 |
| **`update_signal`**                              | Broadcast wire whose pulse width encodes share magnitude. Gated per-Lobe.                                                                                                                                                                                                                                                                                                                        |
| **`reset_signal`**                               | Broadcast wire clearing momentum SRAM.                                                                                                                                                                                                                                                                                                                                                           |
| **`consolidate_signal`**                         | Broadcast clock triggering Hippocampus update phase.                                                                                                                                                                                                                                                                                                                                             |
| **Range Sensitivity (PGA)** _(new in 4.1)_       | Programmable Gain Amplifier on measurement circuits. Coarse (1×) for early training, fine (10×–100×) for deep convergence. Triggered by Brainstem (global loss low) or per-Lobe auto (>80% Scaps hit T_max).                                                                                                                                                                                     |
| **Dummy Scap** _(new in 4.1)_                    | Per-Column always-on reference Scap receiving known input. Provides real-time PVT offset measurement for Local Normalization.                                                                                                                                                                                                                                                                    |
| **Auto-Zeroing phase** _(new in 4.1)_            | Brainstem-driven phase where all inputs go to ground briefly so Lobes capture residual thermal/supply offset for subtraction from real measurements.                                                                                                                                                                                                                                             |
| **Differential Pair op-amp** _(new in 4.1)_      | Twin-transistor op-amp topology that physically cancels common-mode (thermal, supply) drift. Standard analog IC practice.                                                                                                                                                                                                                                                                        |
| **Current Mirror Loss Share** _(new in 4.1)_     | Op-amp topology for §12.7 normalization that preserves ratios between branches even under absolute current drift. Defends against PVT-induced loss-conservation breakdown.                                                                                                                                                                                                                       |
| **Ping-Pong substrate** _(new in 4.1, optional)_ | Twin substrates alternating between active compute and Auto-Zeroing. Avoids forward-pipeline discontinuity at cost of ~2× area.                                                                                                                                                                                                                                                                  |
| **Synaptic Drift**                               | Future mechanism: learnable 1D synapse address.                                                                                                                                                                                                                                                                                                                                                  |
| **Engram Buffer**                                | Future short-term-memory module.                                                                                                                                                                                                                                                                                                                                                                 |
| **Cell fire**                                    | Future STDP wiring rule.                                                                                                                                                                                                                                                                                                                                                                         |
| **Route L1 / L2**                                | 4-bit + 4-bit Ganglion addressing. 256 per region. Unrelated to Ganglion-internal L1–L4.                                                                                                                                                                                                                                                                                                         |
| **Resident-weight compute**                      | Weights never leave substrate during operation. Synonym: in-memory compute (CIM).                                                                                                                                                                                                                                                                                                                |
| **Attribution-based learning**                   | The learning family this architecture belongs to. Updates by `\|a · W\|` contribution share, not gradient. Related to three-factor synaptic rules, EP, LRP.                                                                                                                                                                                                                                      |
| **Loss conservation**                            | The invariant `Σ children_shares = parent_loss` at every level.                                                                                                                                                                                                                                                                                                                                  |
| **Multi-parent diffusion**                       | At a child with multiple parents, incoming shares from each parent sum into a combined share.                                                                                                                                                                                                                                                                                                    |
| **Dead-weight collapse**                         | Failure mode where weights near zero stop receiving updates. Worst failure mode of attribution learning.                                                                                                                                                                                                                                                                                         |
| **Activity vs Relevance** _(new in 4.1)_         | Failure mode where high `\|a · W\|` doesn't imply high relevance to loss. Acknowledged in H10, three remediation plans deferred.                                                                                                                                                                                                                                                                 |
| **Momentum ceiling saturation** _(new in 4.1)_   | Failure mode where 16-bit momentum hits ceiling and differences between strong contributors are lost. Mitigation deferred to scaling or log-domain momentum.                                                                                                                                                                                                                                     |
| **PVT** _(new in 4.1)_                           | Process, Voltage, Temperature variation. The set of analog imperfections that §14 robustness mechanisms defend against.                                                                                                                                                                                                                                                                          |
| **Physical Saturation** _(new in 4.1)_           | The capacitor's hard ceiling at the supply rail. Same PWM pulse delivers exponentially less voltage change as `V_cap → V_rail`. The architecture's primary defense against winner-take-all in attribution learning — strong contributors auto-limit at the rail without explicit normalization. Functionally equivalent to L2 regularization, implemented in physics rather than math. See §4.4. |
| **biological-X**                                 | The biological case.                                                                                                                                                                                                                                                                                                                                                                             |
| **analog-X**                                     | The circuit case (explicit, used in mixed contexts).                                                                                                                                                                                                                                                                                                                                             |

---

_End of Draft 4.1. Canonical until further data invalidates a section._
