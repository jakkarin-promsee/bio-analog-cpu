# Bio-Inspired Analog Neural Compute Architecture

> A continuous-time analog substrate with on-chip hierarchical credit assignment.
> Specification and experimental campaign.

---

## 0. Reading Guide

This document describes an analog compute substrate designed from the substrate up to make brain-like computation cheap: online, sparse, continuous, with weights that never leave the chip during operation.

**Recommended reading order:**

1. **§1** — the bet, what biology contributes, and why this isn't another digital ML accelerator or another inference-only CIM chip.
2. **§2** — the learning mechanism. This is the project's central architectural commitment. The rest of the document only makes sense in its light.
3. **§3** — a worked end-to-end example. One Ganglion, one XOR sample, every quantity traced.
4. **§4** — the hierarchy at a glance.
5. **§5** — naming conventions and disambiguation (short; skim if comfortable with the terms).
6. **§6–§13** — bottom-up build of each level: Scap, Ganglion, Column, Lobe, SpecialGeneralist, Limbic Loop, Commissure, Brainstem.
7. **§14–§16** — three cross-cutting mechanisms: residuals, analog robustness, routes.
8. **§17–§19** — what we claim (hypotheses), what we still need to derive (math), what we don't know yet (open questions).
9. **§20** — the simulation campaign that tests it.
10. **§21–§23** — reference: future work, locked decisions, glossary.

**If you read only three sections:** §2 (the mechanism), §3 (a concrete example), §20.1 (the one-hour test that can falsify the central claim).

---

## 1. The Bet

### 1.1 Goal in one sentence

Build a substrate where the kind of computation brains do is the _cheap_ path, instead of an emulation layered on top of von Neumann silicon or a programmed-once inference array.

### 1.2 What this project is not

- It is **not** an attempt to build intelligence. "Intelligence" is too fuzzy to optimize against.
- It is **not** a 1:1 copy of biology. Biology is the source of architectural patterns, not a target to reproduce.
- It is **not** another digital ML accelerator. Digital neural networks are a metaphor mistaken for the thing.
- It is **not** another inference-only analog array. The architecture's central commitment is **on-chip learning**, not just programmed weights.

### 1.3 The four properties we want

The substrate should make all of these the natural, cheap path:

| Property            | Meaning                                                                                        |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| **Online**          | Weights update during operation, not in batch-offline epochs.                                  |
| **Sparse**          | Only paths that carry signal consume energy.                                                   |
| **Continuous**      | Weights and signals live in capacitor voltages, not bit patterns.                              |
| **Resident-weight** | Weights never leave the substrate during operation. Storage and compute are the same hardware. |

"Resident-weight compute" is the technical framing. The broader field is **compute-in-memory (CIM)**.

### 1.4 What biology actually does differently

The title says _bio-inspired_. This subsection makes that claim concrete — what we extracted from biology, and what we deliberately left behind.

Biology does three things differently from digital computers, and each one shapes a major design decision in this architecture:

**1. Membrane voltages are graded, not bits.** A biological neuron's membrane potential is a continuous voltage that integrates incoming synaptic currents in real time. There is no quantization step, no clock-bounded "value at time t" snapshot. Information lives in the voltage itself, not in a discretized reading of it.
→ _Therefore_ we use capacitors as the weight storage primitive, and hardwired op-amps as the compute primitive. The "value" of a weight is the analog voltage on its cap. We never quantize to update; updates are PWM pulses delivered directly to the analog charge.

**2. Synaptic updates are local, not globally routed.** A real synapse updates based on three signals available _right where it lives_: pre-synaptic activity, post-synaptic activity, and a diffusing neuromodulator. It does not receive a per-weight error gradient routed back through the rest of the network. This is the central premise behind three-factor learning rules in neuroscience (Frémaux & Gerstner 2016).
→ _Therefore_ we use attribution-based credit assignment, not gradient descent. Each Scap updates from three locally-available signals: its accumulated contribution (the local synaptic "trace"), the broadcast loss share (the local "neuromodulator"), and the broadcast direction (the local "feedback"). The substrate measures `|a · W|` for free — that _is_ the forward current through the wire — and that quantity does the routing.

**3. The brain runs multiple timescales simultaneously.** Cortex adapts on the order of seconds; hippocampal consolidation runs on the order of minutes to hours; long-term structural change is even slower. These timescales don't share weights — they are different physical systems with different update rates, in continuous communication.
→ _Therefore_ the top-level structure is a recurrent loop between a fast-updating Lobe (Cortex) and a slow-updating Lobe (Hippocampus), connected by a slower-still Commissure. Same hardware topology in each Lobe; only the update cadence differs.

These three observations — graded voltage, local update, multiple timescales — are the project's actual biological inheritance. Everything else (the specific 2-3-3-2 topology, the five-level hierarchy, the Current Mirror loss share) is engineering choice that follows from these three commitments plus the substrate constraint that analog op-amps are cheap and digital arithmetic is expensive.

What we deliberately did **not** inherit from biology: spike-timing, specific neurotransmitters, dendrite geometry, biochemical signal cascades, glial cells. The biological detail in the names (Ganglion, Hippocampus, Commissure) is a memory aid, not a claim of fidelity.

### 1.5 Why this isn't just Mythic / Loihi / IBM analog AI

A natural objection: analog CIM and neuromorphic chips already exist. Why build another one?

The honest answer is that none of the existing efforts do all four things at once. As a positioning sketch (not an exhaustive literature review — see §1.8):

- **Mythic AI** uses analog flash transistors to do matrix-vector multiply at the wire level. Weights are programmed once and frozen. There is no on-chip learning mechanism. Inference accelerator only.
- **Intel Loihi** is digital neuromorphic with spike-based compute. It has on-chip learning via STDP-flavored rules. But the substrate is digital — spikes are discrete events, not continuous currents — and the learning rule is local-Hebbian, not credit-assignment-based.
- **IBM analog AI / NorthPole** does analog matrix-vector multiply with some on-chip training research. Closer in spirit, but the training mechanisms are gradient-descent variants requiring per-weight error routing — which means weight-transport, which means moving data, which fights the resident-weight property.
- **BrainChip Akida, SpiNNaker, others** are mostly spike-based or simulation-of-spikes platforms. Useful for biological modeling; not aimed at the substrate-as-cheap-path framing.

The distinguishing claim of this project is: **continuous analog compute, with on-chip credit assignment through a multi-level hierarchy, using locally-measured contribution rather than routed gradients.** That combination — continuous + learning + hierarchical + local-measurement — is what the rest of the document is about.

It is plausible that some research lab has independently converged on something similar. The §1.8 methodological note explains why this project chooses to build first and survey later.

### 1.6 Why current ML architectures don't fit either

Even setting aside CIM, the dominant ML architectures are wrong for the substrate we want:

- Transformers are O(n²) brute-force pattern matching over a fixed window. Not online.
- LSTMs are closer to online thinking but locked to time-series framing and explicit cell state.
- Even very strong models shape good output gradually across many tokens — stable pattern replay, not creative first-token output.
- Von Neumann silicon dedicates large area to branch-prediction SRAM and load/store machinery — none of it useful for continuous compute.
- GPUs widened the data pipe but didn't escape the assemble-from-scratch loop. The CPU still arbitrates.

The ceiling isn't model size. The ceiling is the substrate.

### 1.7 The bet

Real neurons are continuous. Build a continuous compute substrate where:

- **Capacitors** scatter across the die holding all weights as analog charge.
- **SRAM** is repurposed from branch prediction into wiring, sign bits, contribution accumulation, and routing.
- **ALUs** are hardwired op-amps performing add / multiply / ReLU directly on capacitor charges.
- **Learning** diffuses through a hierarchy of modules using locally-measured contribution, not per-weight gradient routing.
- **Input / output** are the only external interfaces during operation.
- **Shutdown** is the only event that serializes weights out of the chip.

**The bridge to the next section.** A continuous analog substrate doesn't just make capacitor-based weight storage cheap — it makes _attribution_ nearly free as a byproduct. The forward current through each Scap is _already_ proportional to `|a · W|`. The same physical wire that performs the forward computation produces the credit-assignment signal as a side effect. No additional circuit is needed to measure "how much did this weight matter"; the substrate is already doing it. This is why §2 is about attribution-based learning and not analog gradient descent: the substrate doesn't naturally route gradients backward, but it does naturally measure forward contributions.

### 1.8 Methodological note

> "The fast answer will destroy your creativity."

This project is built from intuition first, with literature comparison reserved for after architectural stability. Existing work (neuromorphic chips, spiking networks, three-factor learning, predictive coding, Equilibrium Propagation, feedback alignment, LRP) is treated as related work for cross-validation, not as design input.

This is a deliberate methodological choice. Its risk is reinventing wheels. Its benefit is reaching architectural decisions the literature wouldn't suggest because the literature pre-commits to digital or spiking framings. The §2 learning mechanism is the most important place this trade-off pays off: it has clear analogues in three-factor learning and LRP, but the _combination_ with continuous analog measurement is the project's own.

---

## 2. The Central Idea — Attribution-Based Hierarchical Diffusion

This section is the project's load-bearing architectural commitment. Every module in §6–§13 only makes sense as a consequence of this mechanism. Read this before the modules, not after.

> **Terminology note.** This section uses structural-element names — _Scap, Ganglion, Column, Lobe, Limbic Loop_ — that are defined in detail in §6–§13. For now: a **Scap** is the leaf-level analog weight cell; _Ganglion_ through _Limbic Loop_ are progressively larger composition units. The hierarchy diagram in §4 lists them at a glance.

### 2.1 The structural idea

Every level of the hierarchy stores **distribution memory** — how much each of its children contributed to its output on the most recent forward pass. When loss arrives from above, the level divides it among its children in proportion to their stored contributions, broadcasts the shares on its local bus, and each child does the same recursively until the share reaches the leaf storage cells (Scaps).

```
Brainstem computes total loss L per Lobe
    ↓ broadcasts on global bus
Limbic Loop reads L
    ↓ uses distribution memory → (Cortex's share, Hippocampus's share)
    ↓ broadcasts on Limbic-local bus
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

The whole backward pass takes six clocks regardless of network size — **one clock per hierarchy level (5 levels) plus one clock for the local Scap update**. Hierarchy _depth_ bounds backward latency; weight _count_ does not. Adding a sixth structural level would add one clock; doubling the number of Scaps within a Ganglion would add zero.

### 2.2 What this actually is: attribution, not gradient

The mechanism is **attribution-based credit assignment**, not gradient descent. This distinction matters.

**Vanilla backprop is sensitivity-based.** It asks: _if I wiggle weight W by ε, how much does loss L change?_ The answer is `∂L/∂W`, computed via the chain rule by routing per-layer error signals `δ` backward through the _next layer's_ weights: `δ_l = W_{l+1}ᵀ · δ_{l+1} ⊙ σ'(z_l)`.

**This architecture is attribution-based.** It asks: _given that this Scap carried this much current during the forward pass, how much of the parent's error is attributable to it?_ The answer is a proportion: `share = parent_loss × (child_contribution / total_contribution)`. The "contribution" is what the analog substrate literally measures for free — the current through each Scap, which is proportional to `|a · W|`.

**The structural divergence:**

| Aspect                 | Vanilla (sensitivity)                                           | This architecture (attribution)                           |
| ---------------------- | --------------------------------------------------------------- | --------------------------------------------------------- |
| Routing error backward | Use next layer's W as transpose to route δ                      | Use `\|a · W\|` at current layer to split parent's share  |
| Weight in own update   | No (only `δ · a`)                                               | Yes (because `\|a · W\|` is what's measured)              |
| Information needed     | Per-neuron δ propagated from output, requiring weight transport | Per-Scap `\|a · W\|` measured locally during forward pass |
| Loss conservation      | By linearity of chain rule                                      | By explicit normalization                                 |
| Inactive units         | `σ'(z) = 0` kills propagation                                   | `\|a · W\| = 0` kills propagation                         |

The substrate measures `|a · W|` because that _is_ the forward current through the Scap. No extra computation. The same physical wire that does the forward computation produces the backward routing signal as a byproduct.

### 2.3 The family of methods this belongs to

Attribution-based learning sits in the family of **three-factor synaptic learning rules** (pre-activity × post-activity × neuromodulator) — the dominant theoretical framework for biological synaptic plasticity. The following anchors were identified _after_ the mechanism was independently designed; they are cross-validation, not influence. Per the §1.8 methodology note, the architecture was committed to before this literature survey.

- **Frémaux & Gerstner (2016)** — three-factor learning rules review.
- **Scellier & Bengio (2017)** — Equilibrium Propagation. Local updates that compute gradient in the small-perturbation limit.
- **Lillicrap et al. (2016)** — Feedback Alignment. Random fixed feedback matrices still let networks learn.
- **Bach et al. (2015)** — Layer-wise Relevance Propagation. Attribution method using exactly `|a · W|` for relevance.
- **Rao & Ballard (1999), Friston** — predictive coding. Local error minimization.
- **Bellec et al. (2020)** — e-prop. Eligibility traces in spiking RNNs. The momentum SRAM (§6.8) is structurally an eligibility trace.

**What this body of work establishes empirically:**

- Vanilla SGD is the most accurate gradient estimate.
- Feedback alignment shows you can be substantially less accurate and still learn, especially in over-parameterized networks.
- EP and contrastive Hebbian converge to the same place as SGD under specific conditions.
- Local rules with global modulators can work for deep networks; performance varies with architecture and task.

There is no theorem ranking these methods against vanilla SGD. Whether attribution-based learning converges as well as gradient descent on a given task is an empirical question. That's why §20 exists.

### 2.4 Known failure modes

Picking attribution-based learning is a real commitment with known failure modes. Simulation must target them directly:

1. **Dead-weight collapse.** Because `ΔW ∝ |a · W|`, a weight that reaches zero magnitude receives zero update and stays dead forever. The floor-at-1 momentum rule (§6.8) and the residual connections (§14) are the main mitigations. Simulation must instrument zero-magnitude weight counts.
2. **Momentum ceiling saturation.** Symmetric to dead-weight: if a Scap consistently contributes very strongly, its 16-bit momentum SRAM saturates at the ceiling. Beyond that, EMA can't grow further. Differences between strongly-contributing Scaps are lost. Mitigation: scale measurement before EMA accumulation, or move to log-domain momentum.
3. **Routing-update coupling.** The same `|a · W|` does both routing of loss and magnitude of update. Errors in one job contaminate the other.
4. **Slow convergence on tasks needing precise gradient.** Loss surfaces with narrow valleys may converge slower than under SGD.
5. **Initialization sensitivity.** Attribution-based methods are typically more sensitive to init than SGD.
6. **Activity vs Relevance gap.** High Scap activity (`|a · W|`) does not necessarily mean high _relevance_ to the actual loss. A Scap can be very active but its output is cancelled by other Scaps downstream — yet it still claims a large share of the loss. Long-tail features (low activity, high relevance) get under-updated. Primary defense is Physical Saturation (§6.6) — winners hit the supply rail and self-limit. See H10 in §17.

**Four remediation paths, in order of cost:**

- **Path 0 (cheapest):** Add a tiny random noise floor to weight updates. Rescues dead weights without circuit changes. One-line addition.
- **Path 1:** Strip the multiplier from the measurement. Measure `|a|` only. Update becomes vanilla SGD `ΔW ∝ a · δ`. Cost: extra input sensors _and_ hierarchical diffusion loses routing signal (splitting loss by input alone is biased). Routing math needs fix.
- **Path 2:** Keep `|a · W|` for routing, add a separate input sensor for the update step. Most chain-rule-correct, most circuit-expensive.
- **Path 3 (current default):** Accept attribution-based, instrument failure modes, test empirically. Cost to find out is low; the architecture is already producing it for free.

Commit to Path 3 for baseline. Path 0 is the first remediation if dead-weight appears. Paths 1 and 2 documented for deeper failures.

### 2.5 Per-level precision allocation

Loss is multiplied at every level as it diffuses. Quantization compounds. Allocation:

| Level       | Distribution storage                     | Notes                        |
| ----------- | ---------------------------------------- | ---------------------------- |
| Limbic Loop | 16-bit SRAM per child                    | Top level — most bits matter |
| Lobe        | 12-bit SRAM per Column                   |                              |
| Column      | 10-bit SRAM per Ganglion / translate ALU |                              |
| Ganglion    | 29 measurement caps (analog)             | Continuous                   |
| Scap        | 16-bit momentum SRAM                     | EMA accumulation             |

Total stored distribution state is small (one number per child per module). Spending bits at the top is cheap.

### 2.6 Loss conservation as invariant

At every level: `Σ children_shares = parent_loss` within finite-precision tolerance ε. Additive, not probability-like. The total loss flowing into a level equals the total flowing out.

This is verifiable in simulation. It catches bugs immediately. If conservation is violated by more than ε at any level, the implementation has a bug.

### 2.7 Normalization via analog op-amp

The division `child_contribution / total_contribution` happens in the **analog op-amp ALU**, not in binary.

**Recommended topology: Current Mirror.** Implementing the division via a Current Mirror circuit makes the share computation _ratio-preserving_ by construction. The parent's total loss current is forced into a central node; the Current Mirror branches it out to children in proportion to their measured `|a · W|`. Even if absolute current levels drift due to thermal or supply variation, the _ratios_ between branches remain stable. This directly addresses analog robustness (§15).

By the time anything lands in a Scap's momentum SRAM or a level's distribution memory, it is already final-form, ready-to-use, no further division required.

The architecture leans on this: continuous analog math is the cheap path, binary math is the expensive path. Normalization is a place where that bet pays off.

### 2.8 Backward pass timing

Backward pass is **synchronous and clock-driven**, six clocks total:

1. _Clock 0:_ Brainstem broadcasts total loss on global bus.
2. _Clock 1:_ Limbic Loop reads, computes child shares, broadcasts on Limbic-local bus.
3. _Clock 2:_ Lobes read, compute Column shares, broadcast on Lobe-local bus.
4. _Clock 3:_ Columns read, compute Ganglion shares, broadcast on Column-local bus.
5. _Clock 4:_ Ganglia read, compute per-Scap shares using measurement caps, broadcast on Ganglion-local bus.
6. _Clock 5:_ Scaps update weight capacitors locally via PWM.

**Six clocks for a full backward pass, regardless of network size.** Hierarchy depth bounds the backward latency, not weight count.

### 2.9 Why this matters

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

Convergence is empirical, not theoretical. The simulation campaign in §20 exists precisely to test whether it converges in practice.

---

## 3. End-to-End Worked Example — Single Ganglion XOR

This section walks one sample through one Ganglion: forward pass, measurement, loss, backward pass, Scap update. Every quantity is concrete. After this section, the abstractions in §6–§13 should feel mechanical rather than mysterious.

> **Scope note.** This example shows a single Ganglion at the leaf level only — one level of the hierarchy. The full five-level diffusion (Limbic Loop → Lobe → Column → Ganglion → Scap) is not walked here; it is exercised in the Phase 5–7 simulation experiments (§20). One Ganglion is sufficient to make the mechanism concrete; the higher levels recurse the same pattern.

### 3.1 Setup

One Ganglion. Topology 2-3-3-2. Task: XOR. Sample: input = (+1, −1), target output channel = (+1, −1). The Ganglion has 29 Scaps holding random small weights. We will track one Scap in particular: call it `S_AB`, the Scap on the wire from L1 neuron A to L2 neuron B.

Suppose the relevant pre-existing state:

- `S_AB.weight_cap = 0.3`, `S_AB.Sign_SRAM = +` → effective weight = +0.3.
- `S_AB.Momentum_SRAM = 40` (already accumulated some contribution history from prior samples).
- Other Scaps have various weights producing a network output of `(+0.7, −0.4)` on this sample.

### 3.2 Forward pass

L1 receives `(+1, −1)`. These voltages charge the input capacitors. The hardwired 2-3-3-2 op-amp circuit performs:

- L2 pre-activation: `y_L2 = W_{L1→L2} · a_L1 + b_L2`
- L2 activation: `a_L2 = ReLU(y_L2)`
- L3 pre-activation: `y_L3 = W_{L2→L3} · a_L2 + b_L3`
- L3 activation: `a_L3 = ReLU(y_L3)`
- L4 output: `y_L4 = W_{L3→L4} · a_L3 + b_L4` (no clip)

The output capacitors charge to `(+0.7, −0.4)`.

**Simultaneously, the measurement circuit operates.** Each of the 29 Scaps has a dedicated measurement capacitor. As the Scap sources its forward current, the measurement cap charges. The time-measure circuit records how fast each measurement cap crosses its A%/B% threshold. Faster = stronger contribution. The conversion is folded into the circuit so what lands in temp SRAM is the contribution magnitude directly (not its inverse).

For our `S_AB`: input to neuron A = +1, weight = +0.3, so current through `S_AB` is proportional to +0.3. The measurement circuit records a contribution magnitude of, say, `30` (arbitrary integer units, depends on threshold calibration).

### 3.3 Forward_Sign latching

In parallel with measurement, each Scap latches the **sign of its forward contribution `a · W`** into `Forward_Sign_SRAM`. Physically, this is one XOR gate over `sign(input_a)` and `Sign_SRAM`.

For `S_AB`: input_a = +1, Sign_SRAM = + → `a · W` is positive → **Forward_Sign latches to `+`** (this Scap pushed neuron B's sum more positive).

For a Scap with input = −1 and Sign_SRAM = + : `a · W` is negative → **Forward_Sign latches to `−`** (this Scap pushed neuron B's sum more negative).

The latched value matters during backward pass: combined with the global feedback direction via XOR, it produces the per-Scap update direction. Worked out in §3.7. For multi-parent diffusion (§9.4), this per-Scap memory is what lets each Scap update correctly even when its parents disagree on direction. For single-Ganglion XOR it's just bookkeeping.

**A note on XOR convention.** Throughout the document, the XOR between sign-encoded signals is wired such that the update equation `direction = Forward_Sign XOR feedback` followed by `weight_cap -= pulse × momentum × direction` yields the SGD-correct ΔW sign in all four cases (Scap-pushed-positive × feedback-wants-more, Scap-pushed-positive × feedback-wants-less, and the two negative cases). The specific bit encoding (whether + is 0 or 1 in hardware) is a circuit-implementation choice that doesn't affect the semantics. The worked example in §3.7 verifies the result for one case; §6.3 gives the equation as written in hardware.

### 3.4 EMA update of momentum

After the forward pass, each Scap's momentum is updated:

```
momentum_new = (3/4) × momentum_old + (1/4) × new_measurement
```

For `S_AB`: `momentum_new = 0.75 × 40 + 0.25 × 30 = 30 + 7.5 = 37.5`, rounded to integer = `38`.

This new momentum value persists until the next forward pass. Floor-at-1 rule applies: if the EMA would round to 0, pin at 1 instead.

### 3.5 Loss computation

The Brainstem reads the output capacitors via ADC: `prediction = (+0.7, −0.4)`. Target was `(+1, −1)`. Error per channel: `(+0.3, −0.6)`. Squared sum: `0.09 + 0.36 = 0.45`. This is the per-Lobe loss.

(For a single-Ganglion experiment without a Lobe, the Ganglion's parent is degenerate and the loss flows straight in.)

The Brainstem also computes the global feedback direction: prediction was too low overall, so `feedback = +` (we want to increase output).

The Brainstem broadcasts:

- `pulse_width = 0.45` (encoded as PWM pulse duration on the bus).
- `feedback = +` (tri-state direction wire).

### 3.6 Backward pass — share computation at the Ganglion level

The Ganglion's distribution memory consists of its 29 measurement caps (already filled during the forward pass). For each Scap, its share of the Ganglion's loss is:

```
share_i = loss × (contribution_i / Σ contributions_j)
```

The Current Mirror op-amp circuit (§2.7) performs this division in analog _at the Ganglion level_. The Ganglion's total loss current is forced into a central node; the Current Mirror branches it out into 29 separate lines on the Ganglion-local bus, one per Scap, each line carrying that Scap's share as a pulse width.

Suppose `S_AB`'s contribution was 30 and the sum of all 29 contributions was 600. Then `share_AB = 0.45 × (30 / 600) = 0.0225`, and that pulse width arrives on `S_AB`'s line.

**Where the division happens.** Each Scap receives its _pre-divided_ share via a dedicated line on the Ganglion-local bus. The Scap does not perform the division itself — it doesn't have access to the Ganglion's total contribution sum, only to its own. The division is centralized at the Ganglion ALU; the per-Scap update is fully local. This split keeps the Scap circuit simple and matches the §2.7 principle that normalization happens at the level's op-amp ALU.

### 3.7 Backward pass — Scap update

`S_AB` now has all four inputs it needs:

- `Forward_Sign_SRAM = +` (latched during forward pass)
- `feedback = +` (from Brainstem)
- `pulse_width = 0.0225` (its share)
- `Momentum_SRAM = 38` (current EMA value)

It computes:

```
direction = Forward_Sign XOR feedback = + XOR + = −
ΔW = − pulse_width × momentum × direction
    = − 0.0225 × 38 × (−)
    = + 0.855 (in PWM-encoded units; actual weight cap voltage change depends on PWM-to-voltage calibration)
```

Since direction was negative-encoded, the weight goes _up_. This is correct: `S_AB` pushed the output positive (good — we wanted more positive output), so reward it by increasing its weight.

The weight_cap voltage rises by the calibrated amount. Sign_SRAM stays +. Done.

Every other Scap in the Ganglion performs an analogous computation _in parallel_, in the same clock cycle. No external instruction needed per Scap. The Ganglion bus broadcasts; the Scaps act.

### 3.8 What just happened

In one forward+backward cycle:

- The substrate measured what each Scap contributed during forward computation (via measurement caps).
- The Brainstem computed loss as a scalar and broadcast it.
- The Ganglion divided that loss into per-Scap shares using an analog Current Mirror, with the measurement caps as the divisor weights.
- Each Scap independently combined its share with its momentum history and its Forward_Sign, and updated its weight capacitor locally.

No gradient was computed. No per-weight error was routed backward. No weight ever left the chip. The mechanism is the same at every level of the hierarchy: distribution memory at each level, broadcast of loss share, local update at the leaves.

That's the entire learning algorithm.

---

## 4. Architectural Overview

### 4.1 The hierarchy at a glance

The architecture has **five structural levels** plus one controller:

```
[Controller]   Brainstem  ←→  central control, loss compute, clock management
                  │
                  ↓ global broadcast bus
[Top level]    Limbic Loop  ←→  recurrent system (Cortex + Hippocampus + Commissure)
                  │
                  ↓ per-Lobe local bus
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

### 4.2 What sits at each level

| Level       | Role                             | Atom of            | Composition pattern                              |
| ----------- | -------------------------------- | ------------------ | ------------------------------------------------ |
| Scap        | Holds one synapse weight         | Storage            | —                                                |
| Ganglion    | Computes one axon's worth        | Compute            | 29 scaps wired 2-3-3-2                           |
| Column      | Sequential signal transformation | Mid-scale function | Ganglia chained through translate ALUs           |
| Lobe        | Multi-branch DAG composition     | Brain region       | Multiple Columns in parallel or branch structure |
| Limbic Loop | Recurrent prediction             | Top-level system   | Cortex Lobe + Hippocampus Lobe + Commissure      |
| Brainstem   | Central control                  | Controller         | Not in the hierarchy — sits beside it            |

### 4.3 Three cross-cutting mechanisms

Beyond the level hierarchy, three mechanisms run across multiple levels:

- **Residual connections (§14).** Each Ganglion routes its input directly to its output in addition to the computed path. This is the primary intervention against dead-weight collapse, which is the worst failure mode of attribution-based learning.
- **SpecialGeneralist (§10).** Inside a Lobe, one Ganglion can be reused under different context masks, gaining effective capacity without adding scaps.
- **Analog Robustness Mechanisms (§15).** Differential Pair op-amps, Dummy Scaps for on-the-fly calibration, Current Mirror loss share, Auto-Zeroing phases, and Range Sensitivity (PGA) to fight process variation, thermal drift, and resolution loss. These are not optional — they are what make the analog substrate physically realizable.

### 4.4 What lives outside the chip

Only inputs and labels enter the chip during operation. Only outputs leave it. At boot, weights are serialized in. At shutdown, weights are serialized out. **No weight ever leaves the chip during operation.** This is the resident-weight property.

The chip has three external interfaces during operation:

- Data input bus
- Label input bus (separate from data; read by Brainstem only)
- Prediction output bus

---

## 5. Naming and Disambiguation

Before walking each level in detail, a brief naming note. Biological names are used throughout the document — but every name refers to a circuit element, not the biological structure itself. The disambiguation rules below prevent collisions between similarly-named layers, roles, and addresses at different levels of the hierarchy.

### 5.1 Semi-anatomical naming

Architectural elements use biological names: **Scap, Ganglion, Column, Lobe, Limbic Loop, Cortex, Hippocampus, Commissure, Brainstem, SpecialGeneralist, Synaptic Drift, Engram Buffer**.

These are _inspired-by_, not _claiming-to-be_. They preserve intuition without claiming biological fidelity.

When ambiguity matters:

- **Default usage** = circuit element. Writing "Brainstem" means our circuit's central controller.
- Prefix **`biological-`** when the actual biology is meant (e.g. "biological brainstem").
- Prefix **`analog-`** when the circuit needs to be flagged explicitly in a mixed-context paragraph.

### 5.2 Layer / role / route disambiguation

The number "L1" appears in three independent contexts. Always specify which:

- **Ganglion-internal layers** are L1–L4 within a single Ganglion (input, two hidden, output).
- **Column-level roles** use semantic names: Generalist (G) and Specialists (S₁, S₂, S₃).
- **Route addressing levels** are written "Route L1" and "Route L2".

### 5.3 Glossary lookup

Every term used in this document is defined in §23.

---

## 6. The Scap — atom of storage

The next eight sections build the architecture bottom-up, level by level. We start at the Scap because everything else composes from it: a Ganglion is 29 Scaps wired in a 2-3-3-2 pattern; a Column is a chain of Ganglia; a Lobe is a DAG of Columns; the Limbic Loop is two Lobes plus a Commissure; the Brainstem orchestrates the whole thing. Each level adds composition rules, not new primitives — the storage atom never changes.

### 6.1 Role

A **Scap** holds the analog weight of _one synapse_ — one wire between two neurons inside a Ganglion. It is the project's atom of storage. Every weight in the system lives in exactly one Scap.

Critically: **a Scap is a wire, not a neuron.** The history of "did current flow through this wire" implicitly encodes both pre-synaptic and post-synaptic activity. No separate per-neuron state is required.

### 6.2 Forward-pass behavior

A Scap is passive during forward pass. Its weight capacitor sources current through its cascode mirror; that current sums with other Scaps' currents at the post-synaptic neuron's summing junction. The current itself is measured externally by the Ganglion's ALU (§7.5).

During the forward pass, a small XOR gate local to the Scap computes `sign(input_a) XOR Sign_SRAM` and latches the result into `Forward_Sign_SRAM`. This is one XOR gate plus one D-flipflop per Scap — negligible area. The latched value tells this Scap, during the next backward pass, whether it personally pushed positive or negative during the just-completed forward.

### 6.3 Backward-pass behavior — fully autonomous

When `update_signal` goes high on the Ganglion-local bus, the Scap reads four signals locally and computes its own update:

```
direction = Forward_Sign_SRAM XOR feedback
weight_cap -= pulse_width × momentum × direction
```

**The two factors serve different duties:**

- **`pulse_width`** is the **update-time control**, encoding the share that arrived at this Scap after hierarchical diffusion. Functions as the per-Scap learning-rate / update magnitude.
- **`momentum`** is the **per-Scap contribution history**, accumulated across the batch in Momentum_SRAM. Functions as the Scap's own importance signal.

These two are not duplicates. The pulse*width is set at update time by the diffusion result; the momentum is set continuously during forward passes by EMA accumulation. They multiply because we want "Scaps that contributed a lot recently \_and* matter for this particular loss" to update most.

**Why `Forward_Sign_SRAM` instead of just `Sign_SRAM`:**

`Sign_SRAM` is the sign of the weight itself. `Forward_Sign_SRAM` is the sign of the _product `a · W`_ during the last forward pass — i.e., did this Scap push the post-synaptic neuron's sum positive or negative?

- For ReLU activations, `a ≥ 0` always, so `sign(a · W) ≡ sign(W)`. In this case `Forward_Sign_SRAM = Sign_SRAM` and the new mechanism provides no benefit.
- For signed activations (the L4 output layer has _no clip_ per §7.3, so L1 inputs to the next Ganglion are signed), `sign(a · W)` can differ from `sign(W)`. Then `Forward_Sign_SRAM` carries real new information.

**The L1→L2 Scaps benefit; L2→L3 and L3→L4 do not under ReLU.** Out of 29 Scaps per Ganglion, 9 benefit. The Forward_Sign_SRAM is filled for all 29 for hardware uniformity. Whether it's worth the area cost is an empirical question (Phase 5 in §20).

The mechanism matters most for **multi-parent diffusion** (§9.4): when a Column has multiple Lobe-DAG parents wanting opposite update directions, magnitude sums correctly via §2.6 conservation, but the global feedback direction loses the per-parent direction context. Forward_Sign lets each Scap know its own contribution direction. Worked example in §3.7.

**Update is fully parallel.** Every Scap on the die can execute this in a single broadcast pulse. No external instruction needed. This is the decentralization win.

### 6.4 Components

Now that the mechanics are clear, here is what's physically in a Scap cell:

| Component                | Size     | Role                                                                             |
| ------------------------ | -------- | -------------------------------------------------------------------------------- |
| Weight capacitor         | 1 cap    | Holds analog weight magnitude as voltage                                         |
| Cascode mirror           | —        | Sources current proportional to weight × input during forward pass               |
| Sign SRAM                | 1 bit    | Direction of weight (+ or −)                                                     |
| Forward_Sign SRAM        | 1 bit    | Sign of `a · W` during last forward pass (§6.2, §6.3)                            |
| Refill / decay SRAM      | 8 bits   | Reference level for leakage compensation; doubles as tunable weight decay (§6.7) |
| Momentum SRAM            | 16 bits  | EMA-accumulated contribution across the batch (§6.8)                             |
| Community / Routing SRAM | N×M bits | Which input bus to read from, which output bus to write to (set at boot)         |
| Control wires            | 3        | `update_signal`, `reset_signal`, tri-state feedback                              |

Total per-Scap storage: roughly 30 bits SRAM + 1 weight capacitor + 1 measurement capacitor (the measurement cap belongs to the Ganglion's ALU, not to the Scap itself).

### 6.5 Sign-magnitude representation

A signed weight is stored as `sign_bit × |weight_cap_voltage|`. The weight cap voltage is always positive (capacitors can't hold negative voltage absolutely — they hold a voltage relative to a reference). Sign is digital, magnitude is analog.

This means:

- A weight near zero has small `weight_cap` voltage; sign is whichever was last set.
- A weight changing sign requires `weight_cap` to drop to zero, then sign-bit flip, then `weight_cap` to grow.
- The system can never produce a discontinuous sign change — sign changes go through zero, which is a soft barrier.

### 6.6 Physical saturation as implicit regularization

The weight capacitor has a _hard physical ceiling_ at the supply rail voltage. This is not a software limit — it's electrochemistry. As the weight cap voltage approaches the rail, the same PWM update pulse delivers exponentially less voltage change because `dV/dt ∝ (V_rail − V_cap)` for a constant-current charging cascode.

**This is the architecture's primary answer to the Activity vs Relevance / winner-take-all concern from H10 (§17).**

The dynamic plays out like this:

1. A Scap with strong contribution `|a · W|` accumulates large momentum and receives large update magnitudes.
2. Its weight cap grows toward the supply rail.
3. As it approaches the rail, each subsequent update pulse delivers less voltage change (charging saturation: `dV/dt → 0` at the rail).
4. The Scap _self-limits_ without any explicit normalizer needed.
5. Loss share that would have gone to this Scap's update gets effectively "wasted" — the Scap can't absorb it.
6. Neighbor Scaps in the same Ganglion continue to grow normally, gradually filling the remaining capacity.

**Functionally equivalent to L2 regularization** in standard ML: weights large in magnitude have a built-in resistance to growing further. But it's free — no Loss term, no `λ · ||W||²` to compute. The physics does it.

**Why this matters for attribution-based learning specifically:**

Attribution gives the largest updates to the highest-`|a · W|` Scaps. Without saturation, this is winner-take-all: the strongest contributor grows fastest, contributes more, grows even faster — runaway. With physical saturation, the winners hit a ceiling and the runner-ups get a chance to develop. The attribution mechanism remains greedy in _direction_ but becomes self-balanced in _steady-state magnitude_.

**Three layered defenses against attribution pathologies, summarized:**

| Defense                            | What it bounds                    | Mechanism                     |
| ---------------------------------- | --------------------------------- | ----------------------------- |
| Floor-at-1 momentum (§6.8)         | Lower bound on update sensitivity | Pinned minimum momentum value |
| Residual bypass (§14)              | Routes signal around dead weights | Bypass wire L1→L4             |
| Physical saturation (this section) | Upper bound on weight magnitude   | Capacitor charging dynamics   |

Combined: dead-weights can't fully die (floor-at-1 + residual route-around), and winners can't run away (saturation). The system has both lower and upper homeostasis built into physics.

**What still needs simulation verification:** does the _rate_ of saturation match the _rate_ of attribution updates well enough? If saturation is too slow, winners still dominate for too long. If too fast, no Scap differentiates. The supply rail voltage and the PWM pulse width together set this rate. **Phase 2 in §20 measures this.** If saturation happens in the first ~10% of training, that's likely too fast (no differentiation). If never, that's too slow (winner-take-all).

**Optional enhancement (deferred to §21):** explicit Adam-style `v_t` accumulator per Scap. Stores squared-update history, scales updates by `1/√v_t`. Probably unnecessary given physical saturation; promoted to baseline only if Phase 2 shows physical saturation alone is insufficient.

### 6.7 Tunable weight decay via refill SRAM

The refill SRAM normally compensates for natural capacitor leakage — every clock, the cascode mirror tops up the weight to match the stored reference. But the refill rate can be _deliberately tuned below_ the natural decay rate, making the weight drift toward zero at a controlled pace.

This gives **free L2 regularization implemented in physics**. No explicit weight-decay term in any update equation; just under-refill.

Per-Scap refill tuning enables:

- Standard light decay everywhere (typical L2 regularization).
- Stronger decay on saturated Scaps (homeostasis — prevent runaway weights).
- Weaker decay on dead Scaps (push them back from zero — partial remedy for dead-weight collapse).

For first simulation, use uniform light decay across all Scaps. Adaptive per-Scap decay is a §21 optimization.

### 6.8 Momentum SRAM mechanics

The 16-bit momentum SRAM accumulates **contribution measurements** during forward passes. Each forward pass, the Ganglion's measurement circuit (§7.5) produces a contribution value for this Scap; that value is EMA-blended into momentum:

```
momentum_new = α × momentum_old + (1 − α) × new_measurement
```

With **α = 3/4** (a single right-shift-by-2 plus add): cheap to implement, smooth enough.

Finer decay options via shift-by-3 (`α = 7/8`) or shift-by-4 (`α = 15/16`) available for empirical tuning.

**Floor-at-1 rule.** When momentum decays toward zero, it is pinned at 1 (lowest non-zero value) rather than allowed to round to 0. This prevents momentum-driven dead-Scap collapse: a Scap with zero momentum receives zero update forever.

---

## 7. The Ganglion — atom of computation

### 7.1 Role

The **Ganglion** is the project's atom of computation. Fixed topology, hardwired, not reconfigurable after fabrication. It abstracts one biological axon's worth of multi-synapse behavior — synapse distance, density, hormone level — into a 2-3-3-2 compute structure.

### 7.2 Why 2-3-3-2 specifically

Two complementary justifications:

**Biological:** One Ganglion represents one biological axon with multi-synapse output behavior. The 2-3-3-2 expansion-contraction pattern models the way a real synapse takes input, distributes through multiple dendritic branches with varying density and hormone levels, recombines through summation thresholds, and produces a graded output. Not a literal model — a structural abstraction.

**Mathematical:** 2×3×3×2 = 36 distinct paths from input to output, with 29 Scaps. Optimizes **path diversity per scap**. Alternative topologies (deferred — not candidates for the baseline build; listed only for future ablation if 2-3-3-2 turns out to be a bottleneck):

| Topology          | Paths | Scaps | Paths/scap |
| ----------------- | ----- | ----- | ---------- |
| 2-3-3-2 (default) | 36    | 29    | 1.24       |
| 2-5-5-2           | 100   | 49    | 2.04       |
| 3-5-5-3           | 225   | 76    | 2.96       |
| 1-5-1             | 5     | 16    | 0.31       |

Higher paths-per-scap is probably better. Test only after H1 (§17) is locked.

### 7.3 Topology

```
L1 (2 input)  →  L2 (3 hidden + ReLU)  →  L3 (3 hidden + ReLU)  →  L4 (2 output)
```

- L1: 2 input neurons, fed by input capacitors via cascode mirror.
- L2: 3 hidden neurons, hardwired op-amp + ReLU.
- L3: 3 hidden neurons, hardwired op-amp + ReLU.
- L4: 2 output neurons, hardwired op-amp (no clip), drive output capacitors.

Per-neuron compute: `y = aW + b`, with `a = ReLU(y)` for L2/L3, identity for L4.

### 7.4 Scap inventory

- L1 → L2: 3×2 weights + 3 biases = **9 Scaps**
- L2 → L3: 3×3 weights + 3 biases = **12 Scaps**
- L3 → L4: 3×2 weights + 2 biases = **8 Scaps**
- **Total: 29 Scaps per Ganglion**

### 7.5 ALU and contribution measurement

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
5. The time-measure circuit converts time-to-threshold into contribution magnitude. Shorter time = stronger contribution; the conversion is folded into the measurement circuit. By the time the value lands in temp SRAM, it already represents contribution magnitude directly — downstream logic does not need to invert.
6. At end of forward pass, each measurement is:
   - Used immediately for the Ganglion's contribution to its parent Column (sum, for §2 distribution).
   - EMA-blended into the corresponding Scap's momentum SRAM (§6.8).

**Calibration.** The A%/B% thresholds reference a calibration cap inside the ALU. This makes time-to-threshold a _ratio_ measurement, robust to voltage drift and temperature.

**Range Sensitivity (Programmable Gain Amplifier).** The op-amp circuit feeding each measurement cap includes a switchable resistor ladder (PGA) that adjusts gain. Two operating modes:

- **Coarse mode (default during early training):** Gain = 1×. Wide dynamic range. Strong contributors charge fast; weak contributors may hit `T_max` and be clipped to minimum contribution. Acceptable in early training because all weights are noisy anyway.
- **Fine mode (activated during deep convergence):** Gain = 10× or 100×. Weak currents that previously got clipped at `T_max` now charge fast enough to be discriminated. Loss of dynamic range at the top is acceptable because mature weights have already settled to moderate magnitudes.

**Triggering Range Sensitivity:**

- **Global trigger from Brainstem (§13.2):** when global loss drops below a threshold (deep convergence detected), Brainstem broadcasts a single bit to switch all Lobes into fine mode.
- **Local auto-trigger per Lobe:** the Lobe maintains a small counter tracking how many of its Scaps hit `T_max` in the last forward pass. If more than 80% hit `T_max`, the Lobe locally switches into fine mode without waiting for Brainstem.

**Forward-pass timing.** The forward pass cannot complete until the slowest measurement cap finishes its threshold crossing. Worst case: `T_forward = max(output_cap_charge_time, slowest_measurement_time)`. Default mitigation: cap measurement time at `T_max`; Scaps that don't cross threshold by then get `T_max` recorded.

### 7.6 ALU reuse

One Ganglion ALU is _reused_ across many Ganglia in a Column. The ALU steps through Ganglia sequentially, holding intermediate values in global capacitors (§8). This keeps total ALU count manageable.

For 256 Ganglia in a region, a single ALU executes 256 forward passes per inference cycle. The forward-pass time is bounded, not the ALU count.

### 7.7 Ganglion-level residual bypass

A direct wire from each L1 input capacitor to the corresponding L4 output capacitor (input bypasses through to output, summed with the computed result).

This is the entry point for residual connections (§14) — it sits inside the Ganglion at its widest level (input-to-output, both width 2).

The bypass is **physically just two wires** with an op-amp summer at the output. Cost: negligible. Benefit: see §14.

---

## 8. The Column — sequential composition

### 8.1 Role

A **Column** is a sequential chain of Ganglia, connected by **translate ALUs** that reshape dimensionality. One Ganglion handles 2-in / 2-out only. The Column composes many Ganglia to do useful-scale computation.

_Biological framing:_ the Column is the circuit analog of a **cortical microcolumn** — a vertically-organized chain of neurons that processes a single feature stream through multiple stages. Like a microcolumn, our Column has well-defined input and output dimensions but variable internal depth.

### 8.2 Structure

```
input → [translate ALU] → Ganglion → [translate ALU] → Ganglion → ... → output
                ↑                                 ↑
            global cap                       global cap
```

Translate ALUs reshape the signal between Ganglia. Global capacitors hold transient state between ALU steps.

### 8.3 Translate ALU

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
| 8:4           | Multi-input fusion (used in Lobe, §9)      |

The catalog is fixed at fabrication. Adding a new size requires new hardware.

### 8.4 Global capacitors

Between every ALU step (Ganglion or translate), the result is held in **global capacitors**. These are not weight storage — they hold transient activations between ALU passes. They are the only "registers" in the system.

Global capacitors have the same leakage characteristics as Scaps but no refill SRAM — they are read once and overwritten on the next forward pass.

### 8.5 Forward pass through a Column

1. Inputs land in the Column's input capacitors.
2. First translate ALU reads inputs, computes, writes to first set of global caps.
3. First Ganglion ALU reads from global caps, computes, writes to its output caps.
4. Output caps are read into next global caps via the next translate ALU.
5. Repeat through the chain.
6. Final translate ALU writes to the Column's output capacitors.

Total time scales linearly with chain length. Total ALU count is just 1 Ganglion ALU + small set of translate ALUs — reused across all Ganglia in the Column.

### 8.6 Column-level residual bypass

Optional: Column input added directly to Column output. Same idea as Ganglion-level bypass (§7.7), one level up. Useful when a Column is part of a deeper Lobe and is at risk of vanishing through composition.

Implementation: passive analog summing at the Column output. Cost: one summer.

Status: deferred to §21. The default is Ganglion-level bypass only.

---

## 9. The Lobe — multi-branch DAG composition

### 9.1 Role

A **Lobe** is the next level of structural composition above a Column. Where a Column chains Ganglia sequentially, a Lobe composes multiple Columns in a **directed acyclic graph** — Columns can have multiple parents, multiple children, and skip-connection topology.

A Lobe is the unit of "brain region" in this architecture. The Cortex Lobe and Hippocampus Lobe are the two main Lobes in the Limbic Loop (§11).

### 9.2 Structural pattern

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

### 9.3 Why multi-branch matters

Two reasons:

1. **Expressivity.** A linear chain can only refine its single representation. A DAG can carry multiple intermediate representations forward in parallel, fusing them at later stages.
2. **Skip connections for free.** Column 1's output reaching Column 3 directly is structurally a skip connection at the Lobe level. This complements the Ganglion-level residual bypass (§7.7).

### 9.4 Multi-parent diffusion

When a Column has multiple parents in the Lobe DAG, it receives **multiple loss shares during backward pass** — one from each parent. The Column's update equation must handle this.

**The magnitude rule:** a Column with multiple parents sums all incoming shares into a single combined share before diffusing further down.

```
combined_share = Σ shares_from_parents
```

This sum then becomes the share that this Column distributes to its own children (Ganglia and translate ALUs inside it).

**The direction problem and its fix.** Naive share-summing handles magnitude but loses direction. If Parent A wants this Column's weights to increase and Parent B wants them to decrease, the global `feedback` signal can only carry one direction.

The fix is **per-Scap `Forward_Sign_SRAM`** (§6.2, §6.3). Each Scap remembers whether IT pushed positive or negative during its last forward pass, independent of the global feedback direction. At update time, `direction = Forward_Sign XOR feedback` gives the correct per-Scap update direction:

- A Scap that pushed positive when the system wanted positive output → update increases its weight.
- A Scap that pushed negative when the system wanted positive output → update decreases its weight.

This holds even when Parent A and Parent B disagreed on the desired direction. Each Scap resolves its own update based on what it personally contributed, not on a global vote.

**Caveat:** Forward_Sign only carries new information when activations can be signed. Under ReLU (default for L2/L3 hidden layers), `Forward_Sign ≡ Sign_SRAM` and the mechanism is degenerate at those layers. It still helps at L1→L2 Scaps (input layer) where inputs from prior Ganglia's L4 outputs are signed.

**Loss conservation under multi-parent.** Each parent's distribution memory still satisfies `Σ shares_to_children = parent_loss`. When a child has multiple parents, summing their shares is correct: the total loss flowing into this child equals the sum of contributions assigned to it by each parent. The system-wide conservation invariant still holds.

### 9.5 Lobe-local bus

The Lobe has its own broadcast bus for downward distribution. It carries pulse-width-encoded shares to each Column inside the Lobe. The bus structure mirrors Column-local and Ganglion-local buses.

### 9.6 Lobe-level distribution memory

The Lobe maintains distribution memory tracking each Column's contribution during the last forward pass. For a Lobe with K Columns, this is K × (precision) bits of SRAM.

Precision recommendation: **12 bits per Column** at the Lobe level. See §2.5 for precision allocation across the hierarchy.

### 9.7 ALU at the Lobe level

The Lobe does not have its own ALU. It uses the Column-level translate ALUs to perform any reshaping at the Lobe interface (input fan-in, output fan-out). Multi-branch composition happens by **wiring**, not by additional compute.

---

## 10. SpecialGeneralist — gated Ganglion reuse

Before moving to the Limbic Loop (§11), one important pattern that lives _inside_ a Lobe rather than as its own structural level. SpecialGeneralist sits between Column and Lobe conceptually — it is a composition pattern, not a new tier of the hierarchy. If you came here expecting "the next level up from Lobe," skip to §11; the next structural level is the Limbic Loop.

### 10.1 Where this lives

SpecialGeneralist is a pattern that lives **inside a Lobe**. It is a way to compose Ganglia inside a Column or across Columns within a Lobe that achieves higher effective capacity per Scap without adding hardware.

### 10.2 The problem it solves

Naive Ganglion reuse — calling one physical Ganglion multiple times in different contexts — causes gradient conflict. Each call wants to push the Ganglion's weights in a different direction; updates contradict; the Ganglion converges to a useless consensus.

### 10.3 The mechanism

A **Generalist Ganglion (G)** is called multiple times under different contexts, each gated by a **context mask** from a **Specialist Ganglion (S)**:

```
Specialist S₁ → mask M₁ → G operates with subset of neurons gated by M₁
Specialist S₂ → mask M₂ → G operates with different subset
Specialist S₃ → mask M₃ → G operates with another subset
```

G's Scaps are shared across calls, but each call uses a _different sub-network within G_. Different masks → different active sub-networks → different effective computation.

### 10.4 Why this works

- **G can learn multiple functions** on the same hardware, selected by mask. No consensus-compromise.
- **Distribution measurement naturally supports gating.** A gated-off Scap delivers zero current, has zero measurement, contributes zero to the share, receives zero update. The math falls out for free.
- **The mask tells us which call a measurement belongs to.** The gradient-conflict problem disappears.

### 10.5 Components

- **G** — one physical Ganglion with a fixed Scap inventory.
- **S₁, S₂, S₃** — separate physical Ganglia that drive G under different masks.
- **Active mask register** — small SRAM at G holding the current call's mask.
- **Mask source per S** — for first simulation, hardcoded; later, learned.

### 10.6 Mask policy options

**Where the mask comes from**, in increasing complexity:

1. **Hardcoded per Specialist** — each S has a fixed mask, never changes. Cheap. **Default for first simulation.**
2. **Learned per Specialist** — each S has a fixed mask but the mask is trained alongside weights.
3. **Computed from S's output** — mask is a function of S's last output, computed by a tiny circuit. Most flexible, most expensive.

**Mask overlap policy:**

- **Mutually exclusive** — disjoint subsets of G's neurons. Cleanest, no gradient conflict. **Default for first simulation.**
- **Overlapping** — some shared G-neurons between specialists. Allows cross-specialist learning in the overlap, but reintroduces gradient conflict there.

Start with hardcoded mutually-exclusive masks. Escalate based on simulation evidence.

### 10.7 Hierarchical diffusion handles this correctly

The standard mechanism (§2) requires no modification: gated-off Scaps register zero contribution and receive zero update. Active Scaps are updated based on their actual contribution during the call. No special handling needed.

### 10.8 Fallback

If SpecialGeneralist underperforms plain G-reuse in simulation:

- **Reservoir-G fallback:** initialize G with diverse non-zero random weights and _freeze_ it. All learning happens in S₁, S₂, S₃. This is reservoir computing — a well-studied technique with established theory.

Plain G-reuse stays as a baseline comparison. Reservoir-G stays as a deeper fallback.

---

## 11. The Limbic Loop — recurrent prediction with two timescales

### 11.1 Role

The **Limbic Loop** is the top-level structural unit. It is two Lobes (Cortex and Hippocampus) connected by a Commissure, in a recurrent prediction loop with two-timescale learning.

### 11.2 Components

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

### 11.3 Cortex and Hippocampus: same structure, different timescales

The two Lobes have **identical topology** at the Ganglion / Column / Lobe-DAG level. Both have **two output heads**:

- **Head A** — predicts input. Loss signal for this Lobe.
- **Head B** — sends to the other Lobe via Commissure.

The only difference between the two Lobes is **which update bus they listen to**:

- Cortex listens to the always-on update bus.
- Hippocampus listens to a bus gated every k-th clock.

This means Cortex updates every clock, Hippocampus accumulates contribution in its momentum SRAM across k clocks and updates only on the k-th. The slow-consolidation behavior emerges from one gating switch — no structural difference required.

### 11.4 Why this timescale separation works

- Cortex's fast updates track immediate input statistics.
- Hippocampus's slow updates accumulate into a stable prior — what the input "usually looks like" over the recent past.
- Their _difference_, carried through the Commissure, is the prediction error that drives learning across both Lobes. This is the predictive-coding pattern.

### 11.5 Input quality asymmetry

Cortex receives full input; Hippocampus receives input passed through an **Input Reducer** that destroys fine detail (e.g. 20 features → 5 features via a small fixed Ganglion or hardwired reducer).

Without this, Hippocampus could short-circuit the loop by predicting input directly from raw input, bypassing the recurrent dynamic. The reducer forces Hippocampus to rely on Cortex's signal via Commissure for fine-grained prediction.

### 11.6 Recurrence stability — the decay term

A recurrent system with non-zero gain in its feedback loop can amplify noise. To prevent this, the Commissure output is multiplied by a **decay factor** (default 0.9) before entering the receiving Lobe. Implementable as a passive resistor divider — zero compute cost.

This is the architecture's equivalent of biological inhibitory interneurons or modern layer normalization. Without it, the loop is unstable. **The decay is mandatory.**

### 11.7 Backward flow

1. _Forward (every clock):_ Both Lobes run forward. Both produce two-head outputs. Distribution memory fills at every level (Lobe / Column / Ganglion / Scap).
2. _Loss compute:_ Brainstem reads both predictions, computes losses, broadcasts on per-Lobe buses.
3. _Diffusion (six clocks):_ Loss diffuses through Lobe → Column → Ganglion → Scap on the active bus.
4. _Scap updates:_ Active Lobe's Scaps update locally. Inactive Lobe's Scaps don't see an update pulse but continue accumulating momentum from forward passes.

**Cortex's bus is active every clock. Hippocampus's bus is active every k-th clock. Commissure's bus is active every M-th clock.**

**Bus routing inside the Limbic Loop.** The Limbic Loop has its own top-level bus carrying the loss broadcast from Brainstem. From that bus, three sub-buses branch:

- **Cortex Lobe bus** — feeds the Cortex Lobe's internal distribution.
- **Hippocampus Lobe bus** — feeds the Hippocampus Lobe's internal distribution.
- **Commissure bus** — feeds the Commissure Ganglia between the two Lobes.

The Brainstem gates each sub-bus independently. From the Lobe sub-bus, hierarchical diffusion proceeds normally down through Columns → Ganglia → Scaps using the Lobe-local, Column-local, and Ganglion-local buses respectively.

### 11.8 Consolidation pulse-width policy

When Hippocampus's bus fires (every k-th clock), the loss pulse-width could be:

1. **Same as Cortex's normal pulse** — Hippocampus simply gets fewer updates. Total weight movement = `1/k` of Cortex's.
2. **k× larger pulse** — total weight movement matches Cortex's. Requires Brainstem to send amplified pulse on consolidation clocks.
3. **Accumulated loss over k clocks** — Brainstem aggregates loss between consolidations; releases the accumulation as one pulse. More biologically faithful but requires Brainstem state.

**Default for first simulation: option 1.** Simplest, no extra Brainstem state. Test options 2 and 3 as optimizations.

---

## 12. The Commissure — inter-Lobe connector

### 12.1 Role

The **Commissure** connects Cortex Lobe ↔ Hippocampus Lobe. It is itself a small group of Ganglia (not a passive wire), capable of performing learned signal translation between the two Lobes.

### 12.2 Why it's a real compute element, not a wire

The Commissure can perform format conversion, dimensionality matching, and noise filtering between the two Lobes. With learnable Scaps inside it, it adapts to the relationship between Cortex and Hippocampus outputs over training.

### 12.3 Trainability and gating

The Commissure trains at a **reduced learning rate**. Its update bus fires every M clocks, where M > k (i.e. slower than Hippocampus, which is already slower than Cortex).

**Why slow Commissure matters.** The Commissure carries the signal that _both_ Lobes backpropagate against. If the Commissure updates too quickly, it destabilizes the entire loop — both Lobes are chasing a moving target. A slow Commissure gives the Lobes a stable reference to converge against.

### 12.4 Why heavy compute here is affordable

Only one Commissure exists per Limbic Loop. Spending more Scaps on it doesn't blow the total budget. The Commissure can be larger and richer than its sender-Lobe / receiver-Lobe topology would suggest.

### 12.5 Optional: Synaptic Drift in the Commissure

The Commissure is a natural home for **Synaptic Drift** (§21) — learnable per-synapse 1D position. Cross-region routing benefits from spatial-position learning more than within-region computation. Activate Synaptic Drift in the Commissure first.

---

## 13. The Brainstem — central controller

### 13.1 Role

The **Brainstem** is the project's only central controller. Small, named, budgeted — not hand-waved.

Biologically apt: real brainstems set rhythms, broadcast neuromodulators, and do not perform cognition.

### 13.2 Responsibilities

The Brainstem:

- Reads predictions from output capacitors via ADC.
- Holds the previous prediction (one-clock buffer) for autoregressive loss vs current input.
- Computes total loss per Lobe (one MAC's worth of arithmetic per Lobe).
- Broadcasts loss on the global bus, pulse-width-encoded.
- Broadcasts tri-state sign `(+, 0, −)` on the global feedback wire.
- **Manages per-Lobe update gating** — Cortex bus (every clock), Hippocampus bus (every k clocks), Commissure bus (every M clocks).
- Manages clocks: forward, backward, batch boundary, consolidation.
- Manages control signals: `update_signal` (per Lobe), `reset_signal`, `consolidate_signal`.
- **Broadcasts Range Sensitivity mode:** detects when global loss falls below convergence threshold and switches all Lobes into PGA fine mode (§7.5). Also collects local override requests from Lobes that hit the 80%-clipping auto-trigger.
- **Manages Auto-Zeroing phase:** at configurable intervals (e.g. every N forward passes), drives input to ground for one clock to let each Lobe's Dummy Scaps capture current thermal offsets (§15.3).
- Holds the **community map** defining which Routes belong to which Lobe / Column (set at boot, read-only after).

**Label routing.** Labels arrive at the chip via a dedicated label input bus, separate from the data input bus. The Brainstem reads labels directly from this bus into its own internal buffer. Labels are not treated as weights and do not flow through the Scap hierarchy. This means the chip has _two_ external input channels (data + label) and one external output channel (predictions).

### 13.3 Size and complexity

Estimated 8–15k transistors equivalent. Tiny compared to a CPU. Large enough to require explicit design.

Implementation: a small hardwired state machine plus a few MAC units, plus ADCs and pulse-width modulators. Not a programmable processor.

### 13.4 What the Brainstem is not

- Not a CPU. No instruction set, no fetch/decode.
- Not a backprop engine. Does not compute gradients.
- Does not know about individual Scaps. Speaks only to the top of the hierarchy.

### 13.5 Future: distributed loss compute

If each output Ganglion can sense its own (prediction − label) locally — by routing the label voltage to the output Ganglia — the Brainstem's loss compute disappears. Brainstem shrinks to label-broadcaster + clock.

Status: §21 future track. Currently bounded by ALU/routing budget.

---

## 14. Residual Connections — fighting dead-weight in attribution learning

The next three sections (§14–§16) cover the **cross-cutting mechanisms** announced in §4.3 — mechanisms that span multiple levels of the hierarchy rather than living at a single tier. Residuals, analog robustness, and routing each touch every level of the architecture; they're factored out here for clarity.

### 14.1 The argument

Each neuron's output is `H(x) = f(x) + x` instead of `H(x) = f(x)`. Input bypasses the computed path and is added to the output.

This is residual connections (ResNets, He et al. 2016). Familiar in modern ML. But for _this_ architecture, it serves a different purpose than it does in standard ML.

### 14.2 Why residuals matter more here than in vanilla ML

In vanilla SGD, residual connections help gradient flow through depth — the gradient has a direct path back through the bypass, so it doesn't vanish through many layers of multiplication.

In **attribution-based learning**, residuals do something more important: they directly attack the **dead-weight collapse** failure mode (§2.4).

Recall: `ΔW ∝ |a · W|`. If `W → 0`, `ΔW → 0`. Dead weight stays dead.

With residual connections, the signal `x` flows around the dead weight via the bypass. The dead weight still gets `ΔW → 0`, but **downstream neurons keep receiving signal** through the bypass. The network keeps computing, keeps learning. Over time, as other weights reorganize, the dead Scap may receive non-zero attribution again as input statistics shift.

**Residual connections are arguably more important for attribution-based learning than for SGD.** They are not optional — they are a primary defense against the learning rule's worst failure mode.

### 14.3 Implementation in the substrate

A residual bypass is **two wires** with an op-amp summer at the receiver. The cheapest mechanism in the entire architecture.

```
input ───────────────────┐
   │                      │
   └──[Ganglion compute]─→[summer]──→ output
```

Cost: one op-amp summer per residual point. Trivially cheap.

### 14.4 Where residuals live in this architecture

**Ganglion-level (default).** A direct L1 → L4 bypass inside every Ganglion. L1 and L4 both have width 2, so the bypass is dimension-matched and free. Specified as §7.7.

**Per-neuron (future test).** Each neuron internally has `output = f(input) + input`. Requires dimension matching at every layer of the 2-3-3-2 — needs either projection or a topology change to 3-3-3-3 (where every layer matches in width). Status: future test.

**Column-level (optional).** Column input added to Column output. Useful for deep Columns. Status: optional, deferred.

**Lobe-level (effectively free via DAG topology).** Skip connections in the Lobe DAG (§9) are structurally residual connections. Column 1 → Column 3 directly, bypassing Column 2, _is_ a residual. Already part of the architecture.

So residuals operate at three levels: inside Ganglia (default), across Lobe DAGs (structural), and optionally between Columns.

### 14.5 Variance management

`H(x) = f(x) + x` has variance `var(f(x)) + var(x)` (assuming independence). Without management, variance grows through depth.

**Strategy:** initialize `f(x)` to produce small outputs at training start. With small initial Scap magnitudes (§19), `f(x)` starts close to zero; the bypass dominates; the Ganglion starts close to identity. This is the modern ResNet best practice.

As training proceeds, `f(x)` learns to produce a _small correction_ to the bypassed signal. The residual block learns a delta, not a full transformation.

For variance normalization across deeper depth, three options:

1. **Fixed scaling factor** — multiply each Ganglion's output by α < 1. Tune empirically. Cheapest.
2. **Analog normalizer circuit** — op-amp circuit that normalizes layer-output amplitude. Same circuit family as §2.7.
3. **Adaptive analog AGC** — feedback gain control. Well-studied in radio circuits. Most complex.

**Default for first simulation: option 1.** Tune α per layer empirically.

### 14.6 Distribution measurement with residuals

The Scap measurement (§7.5) measures the current through _the Scap_, which is the learned part `a · W`. The bypass current goes around the Scap and is not measured by it. So the per-Scap attribution is correct.

But at higher levels, the Ganglion's _output_ (which goes into the parent Column's distribution memory) now includes both the learned part and the bypass. The bypass contributes to the next-stage signal without having a learnable weight to attribute to.

**Fix:** at the Column / Lobe levels, measure _only the learned-path contribution_, not total output. The bypass is informational, not learnable, and should not show up in distribution memory.

**Physical implementation.** The Ganglion has two output ports:

- **Learned output port** — sum of L4 op-amp results only. This port is what the upstream measurement circuit (the parent Column's distribution measurement) reads. It carries the learnable contribution.
- **Combined output port** — learned output summed with the L1→L4 bypass. This port feeds the next Ganglion's input. It carries the total signal.

The two ports diverge at a junction inside the Ganglion. The learned output is tapped _before_ the bypass summer; the combined output is the _output of_ the bypass summer. Both ports source from the same op-amp circuitry. Cost: one extra wire pair per Ganglion output (4 wires total per Ganglion).

This way, distribution memory at every level measures only learnable contribution, while forward computation correctly carries the bypassed signal. The two responsibilities are physically separated.

---

## 15. Analog Robustness Mechanisms

This section addresses the physical realizability of the analog substrate under process variation, thermal drift, supply variation, and aging. These are not future-track optimizations — they are baseline architectural mechanisms required for the chip to function at all. The Python simulation in Phase 2 doesn't need all of them, but the architecture spec must include them so the simulation can be calibrated against realistic PVT-aware behavior.

### 15.1 The PVT problem

Analog circuits on silicon suffer from:

- **Process variation:** transistors and capacitors fabricated at different positions on the die have slightly different characteristics. Static and chip-specific.
- **Voltage variation:** supply rail droops under high activity. Local and dynamic.
- **Temperature variation:** active regions heat up faster than idle ones. Thermal gradients across the die change resistance and op-amp offsets. Dynamic and spatial.
- **Device aging:** transistor characteristics drift over years of operation. Very slow.

In a 5-level hierarchical diffusion architecture, even small per-level errors compound. A 2% error per level becomes ~10% by the time loss reaches a Scap. Loss conservation can break. Without explicit countermeasures, the architecture is not physically buildable.

### 15.2 Differential Pair op-amps

**The mechanism:** every op-amp in the analog ALUs uses a _differential_ topology — two matched transistors placed adjacent on the die, processing signal as the difference between two paths (`V+` and `V−`).

**Why this works:** thermal effects, supply droop, and slow drift hit both transistors equally. The differential output cancels common-mode drift physically, without any digital correction logic. Standard analog IC practice for a century.

**Cost:** ~2× transistor count per op-amp vs single-ended. Acceptable given the substantial robustness gain. Modern analog design assumes differential by default.

**Applies to:** all op-amp circuits, especially §2.7 normalization (Current Mirror), §7.5 measurement, and the Ganglion ALU.

### 15.3 Dummy Scap for on-the-fly calibration

**The mechanism:** every Lobe contains one **Dummy Scap** — a structurally identical Scap that receives a known reference current at every clock and reports its measurement output to a Lobe-level offset register.

**Why this works:** the Dummy Scap experiences the same process, voltage, and temperature conditions as the real Scaps in that Lobe. Its reading-minus-expected gives a per-Lobe per-clock offset that can be subtracted from real Scap measurements. Calibration is _continuous_ and _automatic_ — no separate calibration phase, no sample collection needed.

**Cost:** one Dummy Scap per Lobe (roughly 1/29 of a Ganglion's storage). ~3% area overhead per Lobe.

**Granularity options:**

- **Per Lobe:** captures thermal gradients between Lobes. Minimum reasonable granularity.
- **Per Column (finer):** captures gradients within a Lobe. More accurate, more overhead.
- **Per Ganglion (finest):** captures gradients within a Column. Best accuracy, highest overhead. Probably overkill.

**Default:** one Dummy Scap per Column. Compromise between accuracy and overhead.

### 15.4 Current Mirror for ratio-preserving Loss Share

Already specified in §2.7. Restated here for completeness: the analog op-amp circuit that divides parent loss into children's shares is built as a **Current Mirror**, which preserves the _ratio_ between branches even when absolute currents drift due to thermal/supply variation.

The shares may all scale up or down together as conditions change, but their _relative_ magnitudes — which is what attribution-based learning depends on — stay correct.

### 15.5 Auto-Zeroing phases

**The mechanism:** at configurable intervals (say, every 100 forward passes), the Brainstem drives all input pins to ground for one clock cycle. During this "zero phase," every Lobe's measurement circuits capture the residual offset at their outputs (which should be zero in an ideal circuit, but isn't due to thermal/supply drift). Each Lobe latches this offset into a small per-Lobe SRAM. On the next normal forward pass, the Lobe subtracts this offset from its measurements.

**Why this works:** the offset captured during zero phase represents the _current_ drift state. By subtracting it from real measurements, real-time thermal and supply drift are cancelled regardless of magnitude.

**Cost:** one clock per N forward passes spent in zero mode (overhead ~1% if N=100). One small SRAM per Lobe for offset storage.

**Frequency tuning:** more frequent zero phases give better thermal tracking but more overhead. Tune empirically.

**Trade-off with continuous operation:** auto-zeroing introduces brief discontinuities in the forward stream. This is acceptable for most workloads. For workloads that genuinely cannot tolerate any pause, see Ping-Pong substrate (§15.6).

### 15.6 Ping-Pong substrate (optional)

**The mechanism:** twin substrates — Core A and Core B — operating in alternation. While Core A processes real workload, Core B runs auto-zeroing calibration. They swap roles periodically. The forward pipeline never sees a discontinuity.

**Cost:** ~2× substrate area. Substantial.

**Status:** optional, deferred. Use only if continuous operation is mandatory for the target application.

### 15.7 Range Sensitivity (PGA on measurement)

Already specified in §7.5. Restated here for completeness: a Programmable Gain Amplifier on the measurement circuit allows gain to be adjusted (1× / 10× / 100×) so weak signals can be discriminated during deep convergence. Triggered globally by Brainstem (when loss is low) or locally per Lobe (when >80% of Scaps hit T_max).

### 15.8 Summary of robustness layering

The architecture's resistance to analog imperfection comes from multiple layers stacked together:

| Layer                          | Defeats                                   | Cost                       |
| ------------------------------ | ----------------------------------------- | -------------------------- |
| Differential Pair op-amps      | Thermal drift, supply droop (common-mode) | ~2× transistors per op-amp |
| Dummy Scap                     | Process variation, slow thermal           | ~3% Lobe area              |
| Current Mirror Loss Share      | Absolute-value drift (preserves ratios)   | Op-amp topology choice     |
| Auto-Zeroing phase             | Fast thermal drift, fast supply drift     | ~1% time overhead          |
| Range Sensitivity (PGA)        | T_max resolution loss during convergence  | Switchable resistor ladder |
| Ping-Pong substrate (optional) | Pause intolerance                         | ~2× substrate area         |

None of these are exotic — all are standard techniques in analog IC design. The architecture's contribution is the _layering_ — applying them together to support a multi-level hierarchical learning algorithm.

### 15.9 What Phase 2 simulation must include

The Python simulation does not need to model all of these physically. But it does need to _model their effects_, so the architecture's behavior under PVT is empirically known:

- **Process variation:** initialize each Scap and each op-amp circuit with a small per-instance multiplicative bias drawn from `N(1, 0.02)`. Held constant per chip-run.
- **Thermal drift:** add a slowly time-varying offset to each Lobe's measurements, function of Lobe activity (more active → more drift).
- **Auto-Zeroing:** at simulated intervals, capture and subtract the current drift offset.
- **Loss conservation tracking:** log `Σ shares − parent_loss` at every level, every backward pass. Report epsilon.
- **Range Sensitivity:** track T_max-clip rate per Lobe; switch to fine mode when threshold exceeded.

The simulation can validate that the robustness mechanisms keep loss-conservation epsilon below ~5% across the hierarchy under realistic PVT — which is the bar for the architecture being buildable.

---

## 16. Routes Hierarchy — physical layout

With the analog robustness mechanisms (§15) in place, one remaining physical question is how Ganglia are actually addressed and routed across the die. This section handles the addressing scheme; it is the last piece of the architectural specification before we shift from "what is built" to "what we claim and how we test it" (§17 onward).

### 16.1 Goal

Ganglia occupy a 2D grid. Addressing must be cheap.

### 16.2 Two-level addressing

- **Route L1**: 4-bit address selects one of 16 unit-route Ganglia (horizontal axis).
- **Route L2**: 4-bit address selects one of 16 L1-route groups (vertical axis).
- **Total per region: 256 Ganglia.**

> Route L1 / L2 are _addressing levels_, unrelated to Ganglion-internal L1–L4.

### 16.3 Hierarchy routing extension

Hierarchical diffusion requires that every level of hierarchy be addressable, not just Ganglia. Routes extend to:

- Column membership of each Ganglion (set at boot).
- Lobe membership of each Column.
- Limbic-Loop membership of each Lobe.
- Brainstem-managed community map indexing all of the above.

All this routing state is held in community SRAM, set once at boot.

### 16.4 Sequential boot load

1. Set Route L1 + L2 to activate one unit-route Ganglion.
2. Send routing assignments (input bus to read, output bus to write, parent Column ID, parent Lobe ID, parent Limbic-Loop ID) — stored in community SRAM.
3. Advance to next Ganglion, repeat.

After load, every Scap knows its input/output buses and parent hierarchy. **No re-routing during operation.**

### 16.5 Scale

256 Ganglia per region in the default configuration. Is this enough for "useful intelligence"? Unknown. Simulate one region at full fidelity first; scale to multi-region as Phase 10+.

---

## 17. Hypotheses (the testable claims)

**The architectural specification is complete (§1–§16).** The next three sections shift mode: §17 states what we will test, §18 lists the math that still needs formal derivation, and §19 lists what we genuinely don't know yet. Together they define the input to the simulation campaign in §20.

Each hypothesis below is falsifiable. The simulation in §20 exists to test them.

**H1 is the load-bearing hypothesis.** H2–H11 only matter conditionally on H1.

**H1 — Attribution-based hierarchical diffusion converges on substantive tasks.**
Loss broadcast from the Brainstem, diffused through five levels of distribution memory using `|a · W|` as the attribution quantity, arriving at Scaps as PWM update pulses, can drive the system to convergence on tasks vanilla SGD would also solve. Convergence is empirical, not theoretically guaranteed. **Central open research question.** If H1 fails, the project's architecture needs revisiting.

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
Combined effect of floor-at-1 momentum (§6.8), residual connections (§14), and tunable refill (§6.7) keeps the fraction of dead Scaps below 5% after Phase 2 training runs. If H7 fails, escalate to Path 0 (noise floor on weight updates, §2.4).

**H8 — Residual connections reduce dead-weight rate and accelerate convergence.**
Ganglion-level residual bypass measurably reduces dead-Scap fraction and improves convergence speed on the Phase 2 task suite, compared to a non-residual baseline of identical topology.

**H9 — Lobe-level multi-branch composition outperforms sequential Columns.**
A Lobe with DAG topology (parallel branches, skip connections) achieves better expressivity per Scap than a sequential Column of equal Scap count.

**H10 — Activity vs Relevance gap is bounded under attribution learning.**
The external concern: high Scap activity doesn't necessarily mean high relevance to loss, so attribution-based updates could systematically over-update active-but-irrelevant Scaps. Primary defense is **Physical Saturation (§6.6)**: weight capacitors hit the supply rail and self-limit, naturally bounding winner-take-all dynamics. We hypothesize this is sufficient for convergence on substantive tasks. Phase 2 simulation must verify the saturation-rate matches the attribution-update-rate well enough.

**H11 — Forward_Sign_SRAM resolves multi-parent direction conflict.**
The per-Scap `Forward_Sign_SRAM` mechanism (§6.3) correctly resolves update direction when a Lobe has multiple parents with conflicting desired update directions. Tested in Phase 5. Note: the mechanism is degenerate under ReLU activations — H11 is fully testable only with signed activations or at L1→L2 layers.

---

## 18. Math to Justify (priority targets)

Written justifications to develop alongside simulation. None of these are derived yet — this is a work list for future formal analysis.

1. **Time-to-threshold to contribution conversion.** Show that under constant-current capacitor charging, the time-measure circuit's output is linear in contribution magnitude.

2. **Attribution preserves monotonicity of update magnitudes.** Scaps that contributed more receive larger updates. This is the minimum mathematical property required — not equivalence to gradient. Empirical comparison against SGD as a diagnostic.

3. **Loss conservation invariant.** `Σ children_shares = parent_loss` at every level, every clock.

4. **Multi-parent diffusion preserves loss conservation.** When a child has multiple parents, the sum of shares it receives equals the sum of contributions its parents assigned to it.

5. **Dead-weight collapse rate is bounded.** Given initialization `(μ_init, σ_init)`, floor-at-1 momentum rule, and residual connections, derive an upper bound on expected fraction of zero-magnitude Scaps after N training steps.

6. **EMA momentum with α=3/4 is contractive.** Under bounded measurement inputs, momentum stays bounded.

7. **Physical saturation as implicit regularizer (§6.6).** Constant-pulse PWM charging produces a stable fixed point at supply rails. Derive the equilibrium of N competing Scaps in the same Ganglion under attribution-weighted updates plus physical saturation: show that no single Scap dominates the entire weight range; show that the steady-state weight distribution depends on relative contribution rates, with saturation acting as the upper-bound balancer. This is the math companion to H10.

8. **Limbic Loop stability with decay factor.** Conditions on Cortex / Hippocampus / Commissure rates and decay factor that prevent oscillation or collapse.

9. **SpecialGeneralist capacity bound.** Why gated G achieves higher effective parameter count than plain G-reuse.

10. **Residual variance management.** Show that with initial Scap magnitude `σ_init` and per-layer scaling α, output variance stays bounded across depth.

11. **Low-grade input bottleneck.** How much feature reduction prevents Hippocampus short-circuiting without destroying category structure.

12. **Sign-magnitude representation correctness.** `sign_SRAM × cap_magnitude` is functionally equivalent to signed weight across all operations.

---

## 19. Open Questions

In two tiers: **architecture-critical** (must be answered or the project doesn't work) and **tuning** (parameters to dial in once architecture is validated).

### 19.1 Architecture-critical

These are the questions Phase 2 of the simulation campaign exists to answer. If they go badly, the architecture itself needs revisiting.

1. **Does attribution-based hierarchical diffusion converge on substantive tasks?** (H1) Phase 2 answers.
2. **Activity vs Relevance gap.** (H10) Does Physical Saturation (§6.6) bound winner-take-all dynamics well enough? Phase 2 measures saturation rate and Activity-vs-Relevance gap directly.
3. **Dead-weight collapse rate.** (H7) What fraction of Scaps die in Phase 2? Is floor-at-1 + residuals enough?
4. **Physical Saturation rate calibration.** Supply rail voltage and PWM pulse width set the saturation rate. Phase 2 must show winners hit the rail between 20% and 50% of training duration — sweet spot between "no differentiation" and "winner-take-all dominates."

### 19.2 Tuning

These have an "answer" that depends on simulation results; the architecture stands either way.

5. **Momentum ceiling saturation.** What fraction of Scaps hit the 16-bit momentum ceiling? If >5%, implement log-domain momentum or gain scaling before EMA.
6. **Forward_Sign_SRAM benefit under ReLU.** Does the mechanism help at L1→L2 Scaps enough to justify the per-Scap area cost?
7. **Per-level precision allocation.** 16/12/10/continuous/16 is provisional. Refine empirically.
8. **Time-to-threshold A%/B% calibration.** 10/30 vs 20/80 vs 30/70.
9. **Range Sensitivity trigger thresholds.** Global loss threshold for fine mode? Local T_max-clip percentage threshold?
10. **Auto-Zeroing frequency.** Every 100 forward passes, 1000, or activity-dependent?
11. **Dummy Scap granularity.** Per Lobe, per Column, or per Ganglion?
12. **SpecialGeneralist mask source.** Start hardcoded; escalate if needed.
13. **SpecialGeneralist mask overlap policy.** Mutually exclusive vs overlapping.
14. **Two-timescale ratio k.** k = 8, 16, 32.
15. **Commissure rate M.** M > k.
16. **Decay factor in recurrence.** 0.9 default. Test 0.8 / 0.9 / 0.95.
17. **Hippocampus consolidation pulse-width policy.** Three options in §11.8.
18. **Initialization scheme.** Weight magnitudes, signs, momentum starting values.
19. **Residual variance scaling α.** Per-layer factor.
20. **Concrete Phase 7 task.** Sequence prediction with cue completion is recommended.
21. **One region or two?** Is 256 Ganglia enough for the target task?
22. **Op-amp normalizer topology.** Specific Current Mirror variant.
23. **PVT simulation realism.** Trade-off between realism and simulation speed.

---

## 20. Simulation Plan — Detailed Experimental Campaign

This section is the operational plan for taking the architecture from spec to data. The theoretical work is locked (§1–19); from here, every remaining decision is driven by experiment, not intuition.

The plan is built around ten phases plus support infrastructure. Each phase answers a specific question. Each experiment changes exactly one variable. Each phase has hard exit criteria.

> **Style note:** the architecture has 11 testable hypotheses (H1–H11) and four critical failure modes (dead-weight collapse, momentum saturation, Activity vs Relevance, PVT drift). The simulation plan is structured so every one of these gets measured concretely, not just talked about.

### 20.0 Phases at a glance

The full campaign in one table, before the detail:

| Phase       | What                      | Hypothesis          | Runs       | Effort    | Status                        |
| ----------- | ------------------------- | ------------------- | ---------- | --------- | ----------------------------- |
| 20.1 MVF    | One-hour sanity gate      | H1 (preview)        | 1          | < 1 day   | Mandatory before any phase    |
| 1 (§20.7)   | Operator sanity           | —                   | unit tests | 1 week    | Mandatory                     |
| 2 (§20.8)   | Single Ganglion baseline  | **H1, H7, H8, H10** | 60         | 2 weeks   | Mandatory — the central test  |
| 3 (§20.9)   | Ablation suites           | refines H1, H7, H8  | 80         | 2 weeks   | Mandatory                     |
| 4 (§20.10)  | Column composition        | H1 at scale, H6     | 15         | 1.5 weeks | Mandatory                     |
| 5 (§20.11)  | Multi-parent Lobe DAG     | **H9, H11**, H6     | 30         | 2 weeks   | Mandatory                     |
| 6 (§20.12)  | SpecialGeneralist         | **H2**              | 25         | 2 weeks   | Mandatory                     |
| 7 (§20.13)  | Limbic Loop two-timescale | **H3**              | 50         | 3 weeks   | Mandatory                     |
| 8 (§20.14)  | PVT robustness            | §15 defenses        | 45         | 3 weeks   | Mandatory                     |
| 9 (§20.15)  | Synaptic Drift            | H4                  | 10         | 2 weeks   | Conditional on Phases 2, 6, 7 |
| 10 (§20.16) | 256-Ganglion scale        | **H5**              | 3          | 3 weeks   | Conditional on Phase 7        |

**Total mandatory effort: ~16 weeks (~4 months) of solo evening/weekend work.** Risk-adjusted ~6 months. Conditional Phases 9–10 add another ~5 weeks if all earlier phases succeed.

**Bold hypotheses** are the load-bearing claims — if their phase fails, the architecture itself needs revisiting. Other hypotheses are tested but don't kill the project if they fail.

### 20.1 Minimum Viable Falsification — start here

**The fastest possible test of H1.** Before any phase, run this to fail fast if attribution doesn't work at all.

**Setup:** single Ganglion, Task A (XOR — defined in §20.4), full ideal configuration, 1 seed.

**Expected runtime:** < 1 hour.

**Pass criterion:** loss decreases monotonically over training; final loss < 50% of initial loss.

**Fail action:** stop. Debug the operator layer (Phase 1) or the update equation (§6.3) before proceeding. Most likely failure: a sign error or measurement-direction bug.

This is a sanity gate, not a hypothesis test. It catches infrastructure bugs in hours instead of days. **Build infrastructure to support this run before building infrastructure for anything else.**

### 20.2 Methodological Principles

These rules govern every experiment, regardless of phase.

**Rule 1: One thing changed per experiment.** Each run differs from its comparison run in exactly one variable. If you change residual + ForwardSign + initialization simultaneously, you can't tell which one mattered. Discipline this from day one — it's the single biggest determinant of whether the campaign produces clear answers.

**Rule 2: Multiple seeds per cell.** Each (configuration, task) pair runs with N ≥ 5 random seeds. Report median + interquartile range, not single-run results. Attribution-based learning is stochastic enough that single-run comparisons lie regularly.

**Rule 3: Controlled variables are explicit.** For every comparison, lock these unless one is the variable under test:

- Random seed list (same N seeds across compared cells)
- Task and dataset split
- Initialization scheme
- Total Scap count
- Total training steps
- Pulse-width schedule (learning-rate-equivalent)
- Precision budget per level
- Evaluation metric

**Rule 4: Invariants checked everywhere, not in dedicated suites.** Loss conservation epsilon, dead-weight fraction, ceiling-saturation fraction, and clip rate are logged in _every_ experiment. There is no separate "loss conservation test" — every run validates it as a side effect. See §20.5.

**Rule 5: Failures are data.** A configuration that fails to converge is a result. Log it, report it, move on. Don't tune until it works — that's how you lie to yourself about what the architecture can do.

**Rule 6: Defer all fallbacks until baseline is characterized.** Path 0 noise floor, adaptive decay, Adam-style v*t, anti-Hebbian gating — none of these go into Phase 2. They are tested as remediations \_after* the baseline failure mode is observed. Otherwise you can't distinguish "the baseline works" from "the fallbacks rescued it."

**Rule 7: Defer PVT realism until the ideal model converges.** Phase 8 introduces PVT. Phases 1–7 use ideal deterministic operators. Otherwise you can't tell baseline failures from PVT-induced failures.

**Rule 8: Architecture changes are decisions, not experiments.** If a phase's data suggests changing the architecture (e.g. promoting tanh from §21 to baseline), that decision goes through the §20.18 promotion criteria. Architecture doesn't drift silently.

### 20.3 Simulation Infrastructure

Before any phase runs, the code base needs structure. This subsection specifies the minimum software architecture.

**Language and stack:**

- Python 3.11+
- NumPy for arrays; PyTorch _only_ for SGD baseline comparison (we do not use autograd for the attribution-based path).
- Matplotlib for visualization (no fancy dashboards).
- pytest for unit tests (Phase 1 operator sanity).

**Core class hierarchy:**

```
Scap                          # leaf storage
  ├ weight_cap (float)
  ├ sign_SRAM (bool)
  ├ forward_sign_SRAM (bool)
  ├ refill_SRAM (uint8)
  ├ momentum_SRAM (uint16)
  ├ community_routing (dict)
  └ methods: forward_contribute(), backward_update()

Ganglion                       # one 2-3-3-2 unit
  ├ 29 Scaps + bias Scaps
  ├ measurement_caps (29 floats)
  ├ residual_bypass_enabled (bool)
  ├ activation_type ('relu' | 'tanh')
  └ methods: forward(input), measure_contributions(), distribute_share()

Column                         # sequential Ganglia + translate ALUs
  ├ Ganglia
  ├ TranslateALUs
  ├ global_caps (intermediate state)
  └ methods: forward(input), distribute(share)

Lobe                           # multi-branch DAG
  ├ Columns (graph structure)
  ├ distribution_memory (per-Column SRAM)
  ├ Dummy_Scap (per Column)
  └ methods: forward(input), distribute(share)

LimbicLoop                     # top-level recurrent system
  ├ cortex_lobe, hippocampus_lobe, commissure
  ├ input_reducer (fixed)
  ├ decay_factor
  └ methods: forward_clock(input), distribute_clock(loss)

Brainstem                      # central controller
  ├ adc, label_buffer
  ├ per_lobe_gates (clocks)
  ├ range_sensitivity_mode
  └ methods: compute_loss(), broadcast(), schedule_autozero()
```

**Logging infrastructure:**

Every experiment writes one JSON log per run containing:

- Configuration hash (every parameter)
- Seed
- Per-step metrics (loss, dead-weight count, ceiling-saturation count, conservation epsilon per level)
- Final state (weight distribution, momentum distribution)
- Wall-clock time

Logs go to a versioned directory (`runs/<phase>/<config_hash>/<seed>.json`). Never overwrite.

**Visualization standards:**

Each phase produces one summary report (Markdown + figures) auto-generated from logs:

- Convergence curve (median + IQR across seeds)
- Dead-weight fraction over training
- Ceiling-saturation fraction over training
- Loss conservation epsilon per level
- Weight distribution histograms (start vs end of training)
- Per-Scap weight trajectories (sampled, not all)

**Regression suite:**

Phase 1 unit tests must continue passing throughout all later phases. CI-style check before any phase starts: "do the operators still work?" Catches infrastructure regressions early.

### 20.4 Task Operationalization

Tasks need concrete definitions. "XOR" is ambiguous in an analog substrate.

**Task A: Analog XOR.**

- 4 input patterns: `(−1, −1), (−1, +1), (+1, −1), (+1, +1)` as voltage levels.
- 4 target outputs: `−1, +1, +1, −1`.
- 100 epochs of 4 samples each (400 forward passes).
- Loss: MSE.
- Used in: Phase 2 (single Ganglion baseline).

**Task B: Sine regression.**

- Input: x ∈ [0, 2π] as voltage.
- Target: sin(x) as voltage.
- 200 samples per epoch, 50 epochs (10,000 forward passes).
- Loss: MSE.
- Used in: Phase 2.

**Task C: Two-moons classification.**

- 200 2D points in two interlocking moon shapes.
- Target: 2D output, one-hot.
- 100 epochs of 200 samples (20,000 forward passes).
- Loss: MSE (cross-entropy deferred until softmax is implemented).
- Used in: Phase 2.

**Task D: Multi-parent direction-conflict probe.**

- A synthetic two-input task where one input wants output up and another input wants output down, sometimes simultaneously.
- Used in: Phase 5 (specifically tests H11 — Forward_Sign resolves direction conflict).
- Construction: input1 ~ Bernoulli(0.5) drives target_a = +1 when active; input2 ~ Bernoulli(0.5) drives target_b = −1 when active; final target = target_a + target_b. Half the samples have conflicting inputs.

**Task E: Sequence prediction with cue completion.**

- Memorize K = 4 short sequences of length 8.
- At test time, present first 4 steps; ask Limbic Loop to complete remaining 4.
- Used in: Phase 7 (recurrence / Limbic Loop test).
- Metric: completion accuracy on held-out cues.

**Task F: Image-moving stimulus (very late, optional).**

- 1D sequence of pixels moving across a small "retina" (10 pixels).
- Predict next-frame pixel intensities.
- Used in: Phase 7+ if everything else works. This is the "human eye mechanism" stretch goal. Will probably break first attempts — that's expected.

### 20.5 Continuous Invariant Monitors

These four monitors run in every experiment, every phase. They are not separate tests. They are the always-on health check.

| Monitor                         | What it measures                                                     | Pass criterion           | Fail action                                     |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------ | ----------------------------------------------- |
| **Loss conservation epsilon**   | `\|Σ children_shares − parent_loss\|` per level, every backward pass | ε < 5% per level         | Flag run; report; do not auto-fix               |
| **Dead-weight fraction**        | `(count Scaps with \|weight_cap\| < 1% of range) / total Scaps`      | < 5% by end of training  | Flag run; escalate to Path 0 in §20.18          |
| **Ceiling-saturation fraction** | `(count Scaps with momentum_SRAM ≥ 99% max) / total Scaps`           | < 5% by end of training  | Flag run; consider log-momentum (§21)           |
| **T_max clip rate**             | `(count Scaps hitting T_max in last forward) / total Scaps`          | < 20% by end of training | Flag run; auto-trigger Range Sensitivity (§7.5) |

These run _as part of the simulation engine_, not as separate tests. Failure of any monitor in any run goes into the JSON log and is reported in the phase summary.

### 20.6 Hypothesis-to-Experiment Map

| Hypothesis                                       | Primary phase          | Secondary phases                           | Pass criterion                                                                |
| ------------------------------------------------ | ---------------------- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| H1 — Attribution converges                       | Phase 2                | Phase 4, 5, 7 (re-validated at each scale) | Converges on 2/3 Task A/B/C within 10× SGD steps                              |
| H2 — SpecialGeneralist > plain reuse             | Phase 6                | —                                          | Beats plain G-reuse on Task C by ≥ 10% final loss                             |
| H3 — Two-timescale Limbic Loop converges         | Phase 7                | —                                          | Stable recall on Task E with k ≥ 4                                            |
| H4 — Synaptic Drift accelerates convergence      | Phase 9 (conditional)  | —                                          | ≥ 20% faster convergence on Task C                                            |
| H5 — No weight LDR/STR during operation          | Phase 10 (conditional) | All phases (asserted in infra)             | Asserted by code structure                                                    |
| H6 — Loss conservation bounded                   | All phases             | —                                          | ε < 5% per level always                                                       |
| H7 — Dead-weight collapse bounded                | Phase 2                | All phases                                 | < 5% dead Scaps                                                               |
| H8 — Residuals reduce dead-weight                | Phase 3 (ablation)     | —                                          | Residual-on has < 50% the dead-weight fraction of residual-off                |
| H9 — Multi-branch Lobe outperforms sequential    | Phase 5                | —                                          | DAG-Lobe beats sequential-Column on Task C by ≥ 10%                           |
| H10 — Physical Saturation bounds winner-take-all | Phase 2                | —                                          | Weight saturation rate within 20–50% of training time                         |
| H11 — ForwardSign resolves multi-parent conflict | Phase 5                | —                                          | With ForwardSign, direction-conflict task converges; without, fails or stalls |

If a hypothesis fails its pass criterion, that's a real result. See §20.19 negative-result protocols.

### 20.7 Phase 1 — Operator Sanity

**Goal:** verify every analog primitive matches its ideal mathematical counterpart within the discrete-time simulation.

**Simulation type:** discrete-time Python at ~1 ms resolution. Continuous-time analog behavior approximated by Euler integration of cap voltages. Real-time SPICE simulation deferred to §21.

**Tests:**

- Add op-amp vs ideal add: `out = a + b`, measure error.
- Multiply op-amp vs ideal multiply: `out = a × b`, measure error.
- ReLU op-amp vs ideal ReLU.
- Capacitor charge dynamics: `v(t) = V × (1 − e^{−t/RC})` with constant current, measure deviation from ideal exponential.
- Time-to-threshold conversion: verify `clocks_to_cross(A%, B%) ∝ 1/current` for known current, and that the post-conversion stored value is linear in current.
- PWM update: verify weight changes by `pulse_width × momentum × direction` with correct sign.

**Metrics:**

- Error per operator (max, mean, std).
- Monotonicity: stronger input → stronger output, always.
- Saturation behavior at supply rails.
- Sensitivity to small noise.

**Implementation:** Python unit tests via pytest. Each operator is a class. Each test is a function.

**Exit criterion:** all operators pass unit tests with errors below 0.1% of expected output. Document worst-case error for each.

**Effort estimate:** 1 week (40 hours).

### 20.8 Phase 2 — Single Ganglion (the central test)

**Goal:** validate H1 (attribution converges), H7 (dead-weight bounded), H8 (residuals help), H10 (physical saturation works), and characterize Activity vs Relevance gap.

**This is the make-or-break phase.** If attribution-based learning doesn't work on a single Ganglion, nothing higher will. Spend serious time here.

**Configuration matrix (4 cells):**

| Cell   | Residual | ForwardSign | Notes                                                    |
| ------ | -------- | ----------- | -------------------------------------------------------- |
| Cell A | On       | On          | Full ideal                                               |
| Cell B | Off      | On          | Tests H8                                                 |
| Cell C | On       | Off         | Tests H11 partial (degenerate under ReLU but log anyway) |
| Cell D | (SGD)    | (n/a)       | Vanilla SGD baseline on same topology                    |

5 seeds × 4 cells × 3 tasks (A, B, C) = **60 runs**.

**Metrics per run:**

- Final loss
- Steps to convergence (loss within 5% of asymptote)
- Cosine similarity between attribution-update-vector and SGD-update-vector (averaged over training)
- Dead-weight fraction at end
- Ceiling-saturation fraction at end
- Weight-magnitude saturation rate (how many forward passes until first Scap hits 90% rail)
- Activity vs Relevance gap: for each Scap, log `|a · W|` (claimed share) vs Δloss when that Scap is ablated. Wide gap = relevance problem.

**Exit criteria:**

- Cell A converges on ≥ 2/3 tasks, with median final loss within 10× of Cell D (SGD).
- Dead-weight fraction < 5% in Cell A on all tasks.
- Ceiling-saturation < 5% in Cell A on all tasks.
- Cell B (no residual) shows ≥ 2× dead-weight fraction vs Cell A — validates H8 directionally.
- Physical saturation reaches 50% of Scaps between 20% and 50% of training duration — validates H10.

**Effort estimate:** 2 weeks (80 hours). Includes diagnostic harness, visualization, and writing the phase report.

**If Phase 2 fails:** see §20.19 negative-result protocols. Likely paths: enable Path 0 noise floor → retry; if still failing, escalate to Path 1 or 2.

### 20.9 Phase 3 — Ablation Suites

**Goal:** isolate the contribution of each mechanism beyond the four-cell matrix in Phase 2.

**Three ablation suites:**

**Suite 3a: Momentum dynamics**

| Cell | EMA α | Floor-at-1 | Momentum bits |
| ---- | ----- | ---------- | ------------- |
| 3a-1 | 3/4   | Yes        | 16            |
| 3a-2 | 7/8   | Yes        | 16            |
| 3a-3 | 15/16 | Yes        | 16            |
| 3a-4 | 3/4   | No         | 16            |
| 3a-5 | 3/4   | Yes        | 8             |
| 3a-6 | 3/4   | Yes        | 24            |

5 seeds × 6 cells × Task C = **30 runs**. Resolves Open Questions 5 (ceiling), 7 (precision).

**Suite 3b: Initialization**

| Cell | Magnitude init    | Sign init | Momentum init |
| ---- | ----------------- | --------- | ------------- |
| 3b-1 | Uniform 10% range | Random    | Zero          |
| 3b-2 | Uniform 50% range | Random    | Zero          |
| 3b-3 | Xavier-equivalent | Random    | Zero          |
| 3b-4 | Uniform 10% range | All +     | Zero          |
| 3b-5 | Sparse (50% zero) | Random    | Zero          |

5 seeds × 5 cells × Task C = **25 runs**. Resolves Open Question 18.

**Suite 3c: Residual variants**

| Cell | Residual location            | Bypass scaling α |
| ---- | ---------------------------- | ---------------- |
| 3c-1 | L1→L4 (default)              | 1.0              |
| 3c-2 | L1→L4                        | 0.9              |
| 3c-3 | L1→L4                        | 0.5              |
| 3c-4 | Per-layer (where dims match) | 1.0              |
| 3c-5 | No residual (control)        | —                |

5 seeds × 5 cells × Task C = **25 runs**. Resolves Open Question 19.

**Total Phase 3:** 80 runs.

**Exit criteria:**

- Suite 3a identifies an EMA α that minimizes both dead-weight and ceiling-saturation. Lock that α.
- Suite 3b identifies an initialization that converges fastest with lowest dead-weight. Lock that init.
- Suite 3c confirms residual reduces dead-weight; identifies best α scaling.

**Effort estimate:** 2 weeks.

### 20.10 Phase 4 — Column Composition

**Goal:** verify that hierarchical diffusion through Column-local buses works as designed, and that translate ALUs (learnable, §8.3) train.

**Configuration:**

- Single Column: input → translate ALU (4:6) → Ganglion → translate ALU (6:4) → output
- Compare against single Ganglion of same total Scap count

**Configuration matrix:**

| Cell | Translate ALUs         | Comparison                               |
| ---- | ---------------------- | ---------------------------------------- |
| 4-1  | Learnable              | Single-Ganglion baseline (matched Scaps) |
| 4-2  | Frozen (random)        | Single-Ganglion baseline                 |
| 4-3  | Learnable, sparse-init | Single-Ganglion baseline                 |

5 seeds × 3 cells × Task C = **15 runs**.

**Exit criteria:**

- Column converges on Task C with conservation ε < 5% at every level.
- Learnable translate ALUs measurably outperform frozen — validates translate-ALU learnability.
- Time-per-forward-pass scales linearly with depth (no exponential blowup).

**Effort estimate:** 1.5 weeks.

### 20.11 Phase 5 — Multi-Parent Lobe DAG

**Goal:** validate H9 (DAG > sequential), H6 under multi-parent (loss conservation holds), H11 (ForwardSign resolves direction conflict).

**Three configurations:**

**Config 5a: DAG vs sequential expressivity (H9)**

- DAG-Lobe: 3 Columns with skip-connections (Column1 → Column2 + Column3; Column2 → Column3)
- Sequential-Lobe: 3 Columns in a chain, matched Scap count
- Task: C (two-moons)

5 seeds × 2 cells × Task C = **10 runs**.

**Config 5b: Multi-parent loss conservation (H6)**

- DAG-Lobe with two parents feeding one child
- Track conservation ε at the multi-parent child
- Compare to single-parent baseline

5 seeds × 2 cells × Task C = **10 runs**.

**Config 5c: Direction conflict (H11)**

- DAG with two parents that pull in opposite directions on Task D
- With ForwardSign vs without

5 seeds × 2 cells × Task D = **10 runs**.

**Exit criteria:**

- 5a: DAG beats sequential by ≥ 10% final loss on Task C.
- 5b: Multi-parent conservation ε < 5% (matches single-parent).
- 5c: With ForwardSign, Task D converges; without ForwardSign, stalls or fails. **This is the cleanest test of H11.**

**Effort estimate:** 2 weeks.

### 20.12 Phase 6 — SpecialGeneralist

**Goal:** validate H2 (gated G-reuse > plain reuse > Reservoir-G).

**Configurations × mask policies:**

| Cell | G-reuse type           | Mask source | Mask overlap       |
| ---- | ---------------------- | ----------- | ------------------ |
| 6-1  | Plain reuse (no mask)  | —           | —                  |
| 6-2  | SpecialGeneralist      | Hardcoded   | Mutually exclusive |
| 6-3  | SpecialGeneralist      | Hardcoded   | 50% overlap        |
| 6-4  | SpecialGeneralist      | Learned     | Mutually exclusive |
| 6-5  | Reservoir-G (G frozen) | —           | —                  |

5 seeds × 5 cells × Task C = **25 runs**.

**Exit criteria:**

- SpecialGeneralist (any mask variant) beats plain reuse by ≥ 10% final loss.
- If SpecialGeneralist fails to beat plain reuse: fall back to Reservoir-G; document failure of H2.
- Identify best mask source and overlap policy; lock for Phase 7.

**Effort estimate:** 2 weeks.

### 20.13 Phase 7 — Limbic Loop with Two-Timescale Learning

**Goal:** validate H3 (two-timescale Limbic Loop converges), characterize recurrence stability, identify timescale parameters.

**Configuration scan:**

| Cell | Cortex update    | Hippocampus update | Commissure update | Decay factor |
| ---- | ---------------- | ------------------ | ----------------- | ------------ |
| 7-1  | Every clock      | Every 4 clocks     | Every 16 clocks   | 0.9          |
| 7-2  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.9          |
| 7-3  | Every clock      | Every 16 clocks    | Every 64 clocks   | 0.9          |
| 7-4  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.8          |
| 7-5  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.95         |
| 7-6  | Cortex-only      | (no Hippocampus)   | (no Commissure)   | (n/a)        |
| 7-7  | Hippocampus-only | (no Cortex)        | (no Commissure)   | (n/a)        |

5 seeds × 7 cells × Task E = **35 runs**.

**Hippocampus consolidation pulse-width policy (sub-sweep):**

- Within best-k cell: test three policies (same pulse / k× pulse / accumulated loss).

5 seeds × 3 policies × Task E = **15 runs**.

**Total Phase 7:** 50 runs.

**Exit criteria:**

- 7-1 to 7-5 converge stably on Task E.
- Best (k, M, decay) configuration identified.
- 7-6 (Cortex-only) underperforms — validates that Hippocampus contributes.
- Best consolidation pulse-width policy identified.

**Effort estimate:** 3 weeks.

### 20.14 Phase 8 — PVT Robustness

**Goal:** validate that the analog robustness mechanisms (§15) preserve performance under realistic PVT.

**Now and only now, add PVT realism to the simulator.**

**Configuration matrix:**

| Cell | Process σ | Thermal | Diff Pair | Dummy Scap | Auto-Zero | Current Mirror | Range Sens |                            |
| ---- | --------- | ------- | --------- | ---------- | --------- | -------------- | ---------- | -------------------------- |
| 8-1  | 0         | None    | On        | On         | On        | On             | On         | Baseline (no PVT)          |
| 8-2  | 2%        | Mild    | On        | On         | On        | On             | On         | Light PVT, full defenses   |
| 8-3  | 5%        | Strong  | On        | On         | On        | On             | On         | Heavy PVT, full defenses   |
| 8-4  | 5%        | Strong  | Off       | On         | On        | On             | On         | Ablate Diff Pair           |
| 8-5  | 5%        | Strong  | On        | Off        | On        | On             | On         | Ablate Dummy Scap          |
| 8-6  | 5%        | Strong  | On        | On         | Off       | On             | On         | Ablate Auto-Zero           |
| 8-7  | 5%        | Strong  | On        | On         | On        | Off            | On         | Ablate Current Mirror      |
| 8-8  | 5%        | Strong  | On        | On         | On        | On             | Off        | Ablate Range Sensitivity   |
| 8-9  | 5%        | Strong  | Off       | Off        | Off       | Off            | Off        | All defenses off — control |

5 seeds × 9 cells × Task C = **45 runs**.

**Exit criteria:**

- Cell 8-3 (full defenses, heavy PVT) shows < 20% performance drop vs Cell 8-1.
- Each ablation (8-4 through 8-8) shows measurable degradation — validates each defense.
- Cell 8-9 (no defenses) catastrophically fails — confirms defenses are doing real work.

**Effort estimate:** 3 weeks.

### 20.15 Phase 9 — Synaptic Drift (conditional)

**Goal:** validate H4. Activate only if Phases 2, 6, 7 succeed.

- Add learnable 1D position SRAM per synapse in Commissure.
- Compare convergence vs fixed-topology Commissure.

5 seeds × 2 cells × Task E = **10 runs**.

**Exit criteria:** ≥ 20% faster convergence with Drift vs without.

**Effort estimate:** 2 weeks.

### 20.16 Phase 10 — Scale to 256 Ganglia per Region (conditional)

**Goal:** validate H5 and characterize scale behavior. Activate only if Phase 7 succeeds.

- Implement Route L1/L2 addressing (§16).
- Scale single region to 256 Ganglia.
- Run Task E end-to-end on full region.
- Assert weight state never leaves the substrate during operation.

3 seeds × 1 config × Task E = **3 runs** (expensive — large network).

**Exit criteria:**

- Task E runs to convergence at 256-Ganglion scale.
- Loss conservation ε stays bounded across all 5 hierarchy levels.
- No weight serialization observed during operation (asserted by code).

**Effort estimate:** 3 weeks.

### 20.17 Promotion / Demotion Criteria

When does the architecture change based on data?

**Promote to baseline (move from §21 Future Tracks to §1–19 spec):**

- Tanh activation (§21): if Phase 2 shows ReLU works _but_ Forward_Sign benefits at only 9/29 Scaps — and Phase 3 shows tanh would benefit all 29 with no convergence cost.
- Adam v*t per Scap (§21): if Phase 2 shows physical saturation alone produces > 5% ceiling-saturation \_or* fails to prevent winner-take-all (measured as: single Scap holds > 30% of total weight magnitude).
- Adaptive per-Scap weight decay (§21): if Phase 3 shows uniform decay produces > 10% dead-weight fraction even with floor-at-1 and residuals.
- Per-neuron residuals (§21): if Phase 3 residual ablation shows L1→L4 bypass insufficient (dead-weight > 5% with bypass on).

**Demote to fallback (mark as backup, simplify baseline):**

- SpecialGeneralist → Reservoir-G fallback: if Phase 6 shows SpecialGeneralist underperforms plain G-reuse on all tasks.
- ForwardSign → drop: if Phase 5c shows no measurable benefit on Task D. Saves 1 bit per Scap.

**Architectural changes require:**

- A documented Phase report showing the data.
- A draft revision (e.g. draft5.1) showing the change.
- The change goes through the §22 Protected List update process.

### 20.18 Negative Result Protocols

What to do when a phase fails its exit criteria.

**Phase 2 fails (H1 — attribution doesn't converge):**

1. Run minimum viable falsification (§20.1). Confirm not an infrastructure bug.
2. Enable Path 0 (noise floor on weight updates) — see §2.4. Re-run.
3. If still failing: enable Path 1 (strip multiplier from measurement, use `|a|` only). Re-run.
4. If still failing: the architecture's central learning mechanism may need revisiting. Stop and rethink before continuing.

**Phase 5 fails (H11 — ForwardSign doesn't help):**

1. Test with explicitly signed activations (skip ReLU at L1 input only).
2. If still no benefit: drop ForwardSign per §20.17 demotion. Document the negative result.

**Phase 6 fails (H2 — SpecialGeneralist no better than plain reuse):**

1. Try learned masks (escalate from hardcoded).
2. Try overlapping masks.
3. If still no benefit: fall back to Reservoir-G. Document.

**Phase 7 fails (H3 — Limbic Loop unstable or doesn't recall):**

1. Reduce decay factor (try 0.8 then 0.7).
2. Try fixed Commissure (no learning) instead of slow-learning Commissure.
3. If still failing: the recurrence structure may need redesign. Pause and rethink before Phase 8.

**Phase 8 fails (PVT crashes the system):**

1. Identify which defense, if any, is single-handedly necessary. Most likely Current Mirror.
2. Consider Ping-Pong substrate (§15.6) if Auto-Zeroing alone is insufficient.

**Universal failure mode:** all monitors red, no convergence anywhere. Likely a fundamental implementation bug. Stop, audit code, restart from Phase 1.

### 20.19 Reproducibility Infrastructure

**Random seeds:** every run records its seed. Standard set: `[42, 137, 271, 314, 1729]` for the 5-seed default. Use these everywhere unless an experiment specifically tests seed sensitivity.

**Configuration hashing:** every config (a Python dict of all parameters) gets a SHA-256 hash. Logs are named by hash. Identical configs collapse to one log directory across runs.

**Versioning:** simulator code is committed to git with every phase. Phase reports cite the git SHA they were run against. No "ran with code modifications I forgot to commit."

**Phase reports:** each phase produces one Markdown report with:

- Hypothesis tested
- Configuration matrix actually run
- Results tables (median + IQR per cell)
- Plots (convergence, dead-weight, conservation)
- Pass/fail vs exit criteria
- Decisions made (promote / demote / lock parameter)
- Open questions for next phase

Reports live in `reports/phase_<N>.md`. They are the project's actual memory.

### 20.20 Effort Budget Summary

Solo, evening / weekend work, Year 2 student pace.

| Phase                            | Effort estimate | Cumulative |
| -------------------------------- | --------------- | ---------- |
| 1 — Operator Sanity              | 1 week          | 1 week     |
| 2 — Single Ganglion              | 2 weeks         | 3 weeks    |
| 3 — Ablation Suites              | 2 weeks         | 5 weeks    |
| 4 — Column Composition           | 1.5 weeks       | 6.5 weeks  |
| 5 — Multi-Parent Lobe            | 2 weeks         | 8.5 weeks  |
| 6 — SpecialGeneralist            | 2 weeks         | 10.5 weeks |
| 7 — Limbic Loop                  | 3 weeks         | 13.5 weeks |
| 8 — PVT Robustness               | 3 weeks         | 16.5 weeks |
| 9 — Synaptic Drift (conditional) | 2 weeks         | 18.5 weeks |
| 10 — 256-scale (conditional)     | 3 weeks         | 21.5 weeks |

**Phases 1–8 are mandatory.** That's ~16 weeks (4 months) of work to characterize the architecture. Phases 9–10 are conditional on success of earlier phases.

**Realistic milestones:**

- Phase 2 completion = first publishable preliminary result (does attribution-based learning converge at all?).
- Phase 5 completion = architectural soundness validated (hierarchical diffusion works end-to-end on a small scale).
- Phase 8 completion = simulation-stage thesis-grade result (architecture is buildable in principle).

**Risk-adjusted timeline:** add 50% buffer. So Phase 8 completion realistically takes 6 months, not 4.

**Single biggest risk:** Phase 2 failure. If H1 doesn't converge after Path 0/1/2, the project's central architectural commitment needs revisiting. This is why §20.1 minimum viable falsification exists — to identify catastrophic failure in hours, not weeks.

---

## 21. Future Tracks — Optional and Deferred Mechanisms

### 21.1 Per-neuron residual connections

Internal residuals at every layer of the Ganglion. Requires dimension matching at every step — either projection circuits or topology change to 3-3-3-3.

### 21.2 Adaptive per-Scap weight decay

Tunable refill SRAM (§6.7) dynamically adjusted based on weight magnitude. Stronger decay on saturated Scaps; weaker on dead Scaps. Homeostasis at long timescales.

### 21.3 Local-aware update normalization

Each Scap exposes its remaining headroom; updates scaled to keep epoch-level update capacity uniform across Scaps. Connects to §21.2 via the recharge SRAM mechanism.

### 21.4 Adam-style v_t per Scap

Add a second 16-bit SRAM per Scap holding `v_t = β₂ × v_{t-1} + (1-β₂) × (pulse_width × momentum)²` — squared-update history. Effective update becomes `ΔW ∝ (pulse_width × momentum × direction) / √v_t`. Provides explicit per-Scap rate adaptation (slow already-large-update Scaps, fast under-updated Scaps).

Cost: doubles per-Scap SRAM (from ~30 to ~46 bits). Requires analog 1/√ circuit or ADC + digital divider per Scap.

**Status:** probably unnecessary. Physical Saturation (§6.6) already provides upper-bound self-limiting behavior. Promote to baseline only if Phase 2 shows saturation alone is insufficient.

### 21.5 Activation mixing — tanh instead of ReLU

Replace L2/L3 ReLU with tanh-like saturation (unclipped op-amp at supply rails). Continuous gradient everywhere. Free in hardware. **Bonus:** makes Forward_Sign_SRAM (§6.2, §6.3) carry useful information at all 29 Scaps per Ganglion (instead of just the 9 L1→L2 input Scaps). Likely promoted to baseline once Phase 2 validates the ReLU version.

### 21.6 Synaptic Drift

Each synapse has a learnable 1D address; signal scales by distance. Activate first in Commissure (§12.5). Analog-position version (capacitor + comparator ladder) is a clean future direction.

### 21.7 Engram Buffer (short-term memory)

Pure capacitor network acting as LSTM-like layer. Stacks between Cortex and Hippocampus. Not specified — revisit after H3.

### 21.8 Cell-fire (STDP)

Hebbian spike-timing-dependent plasticity for group-level rewiring. Open research thread.

### 21.9 Distributed loss compute

Each output Ganglion senses its own (prediction − label) locally. Brainstem shrinks to label-broadcaster + clock.

### 21.10 2-capacitor analog momentum

Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage. Eliminates ADC/SRAM at the Scap level. Post-baseline optimization.

### 21.11 Floating-gate transistor storage

Replace refilled capacitor + 8-bit SRAM with FGT (NAND-flash technology, Mythic AI's choice). Years of retention without refresh.

### 21.12 Op-amp normalizer topology

Specific circuit choice for §2.7 normalization. Multiple candidates from the analog computing literature.

### 21.13 Column-level residual bypass

Optional residual at the Column level (input → output direct path). For deep Columns.

### 21.14 Inference-only low-power mode

Disable backprop circuitry; just forward inference. Trivial mode bit.

### 21.15 Failure mode handling

Dead-Scap recovery, stuck-attractor escape, range-drift correction. Provisional: noise injection. Better mechanisms after empirical failure modes are seen.

### 21.16 SPICE / robustness simulation

After Python ideal-model converges: SPICE simulation of single Scap; noise-injected Python model calibrated against SPICE; degradation quantification.

---

## 22. What Not To Touch (the protected list)

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
10. **Forward_Sign_SRAM in every Scap.** Resolves multi-parent direction conflict. 1 bit per Scap, XOR-based logic. The full hardware uniformity (all 29 Scaps per Ganglion have it, even the 20 that are degenerate under ReLU) is a deliberate trade-off for circuit simplicity.
11. **Differential Pair op-amps throughout.** Standard practice for analog robustness. Not optional.
12. **Dummy Scap per Column for calibration.** Granularity could be debated, but having _some_ on-die reference is mandatory.
13. **Current Mirror for Loss Share normalization.** Ratio preservation is what makes hierarchical diffusion physically tolerable under PVT.
14. **Physical Saturation as primary defense against winner-take-all.** The capacitor charging behavior near the supply rail is the architecture's primary answer to Activity vs Relevance / H10. Don't try to engineer around it with software-flavored normalizers before validating the physics in Phase 2.

Everything else — precision allocations, decay factors, mask sources, timescale ratios, initialization, Auto-Zeroing frequency, Dummy Scap granularity, saturation rate calibration — is up for negotiation as simulation data arrives.

---

## 23. Glossary

| Term                                 | Meaning                                                                                                                                                                                                                                                                    |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scap**                             | Atom of storage. SRAM + Capacitor cell holding one synapse weight.                                                                                                                                                                                                         |
| **Forward_Sign_SRAM**                | 1-bit per-Scap SRAM holding `sign(input_a) XOR Sign_SRAM` from the last forward pass. Resolves multi-parent update direction conflict via `direction = Forward_Sign XOR feedback`. Degenerate under ReLU; meaningful only with signed activations or at L1→L2 input layer. |
| **Ganglion**                         | Atom of computation. Hardwired 2-3-3-2 network, 29 Scaps. Includes default residual bypass. Has two output ports: learned-only (for measurement) and combined (for next stage).                                                                                            |
| **Column**                           | Sequential composition of Ganglia connected by learnable translate ALUs.                                                                                                                                                                                                   |
| **Lobe**                             | Multi-branch DAG composition of Columns. Brain-region scale.                                                                                                                                                                                                               |
| **Limbic Loop**                      | Top-level recurrent system. Cortex Lobe + Hippocampus Lobe + Commissure + decay term.                                                                                                                                                                                      |
| **Cortex Lobe**                      | Fast-learning Lobe. Updates every clock. Two output heads.                                                                                                                                                                                                                 |
| **Hippocampus Lobe**                 | Slow-learning Lobe. Same topology as Cortex; updates every k clocks. Two output heads.                                                                                                                                                                                     |
| **Commissure**                       | Inter-Lobe connector. Small Ganglion group, trainable at reduced rate (every M clocks).                                                                                                                                                                                    |
| **Brainstem**                        | Central controller. Loss compute, broadcasts, clocks, per-Lobe gating, Range Sensitivity broadcast, Auto-Zeroing scheduling. Estimated 8–15k transistors.                                                                                                                  |
| **Generalist (G)**                   | Reused Ganglion inside a Lobe under context masks (SpecialGeneralist).                                                                                                                                                                                                     |
| **Specialist (S₁, S₂, S₃)**          | Ganglia that drive G under different masks.                                                                                                                                                                                                                                |
| **SpecialGeneralist**                | Gated Ganglion reuse — G with context masks from Specialists.                                                                                                                                                                                                              |
| **Translate ALU**                    | Learnable analog reshaping element between Ganglia or between hierarchy levels.                                                                                                                                                                                            |
| **Global capacitor**                 | Inter-step buffer holding transient state. Not weight storage.                                                                                                                                                                                                             |
| **Residual bypass**                  | Input-to-output direct wire summed with computed output. Defense against dead-weight.                                                                                                                                                                                      |
| **Hierarchical Diffusion**           | The learning mechanism. Loss diffuses through level shares from top.                                                                                                                                                                                                       |
| **Distribution memory**              | Per-level storage of children's contributions. SRAM at high levels, measurement caps at Ganglion level, momentum SRAM at Scap level.                                                                                                                                       |
| **Momentum SRAM**                    | 16-bit per-Scap accumulator of contribution. EMA with α=3/4. Floor-at-1 rule.                                                                                                                                                                                              |
| **Refill / decay SRAM**              | 8-bit per-Scap reference for leakage compensation; doubles as tunable weight-decay regularizer.                                                                                                                                                                            |
| **PWM update**                       | Pulse-width-modulated weight cap update. Written locally per Scap.                                                                                                                                                                                                         |
| **Pulse-width**                      | Update-time control. The share that arrived at this Scap after hierarchical diffusion.                                                                                                                                                                                     |
| **Tri-ode feedback**                 | Global wire carrying loss direction `(+, 0, −)`.                                                                                                                                                                                                                           |
| **`update_signal`**                  | Broadcast wire whose pulse width encodes share magnitude. Gated per-Lobe.                                                                                                                                                                                                  |
| **`reset_signal`**                   | Broadcast wire clearing momentum SRAM.                                                                                                                                                                                                                                     |
| **`consolidate_signal`**             | Broadcast clock triggering Hippocampus update phase.                                                                                                                                                                                                                       |
| **Range Sensitivity (PGA)**          | Programmable Gain Amplifier on measurement circuits. Coarse (1×) for early training, fine (10×–100×) for deep convergence. Triggered by Brainstem (global loss low) or per-Lobe auto (>80% Scaps hit T_max).                                                               |
| **Dummy Scap**                       | Per-Column always-on reference Scap receiving known input. Provides real-time PVT offset measurement.                                                                                                                                                                      |
| **Auto-Zeroing phase**               | Brainstem-driven phase where all inputs go to ground briefly so Lobes capture residual thermal/supply offset for subtraction from real measurements.                                                                                                                       |
| **Differential Pair op-amp**         | Twin-transistor op-amp topology that physically cancels common-mode (thermal, supply) drift. Standard analog IC practice.                                                                                                                                                  |
| **Current Mirror Loss Share**        | Op-amp topology for §2.7 normalization that preserves ratios between branches even under absolute current drift.                                                                                                                                                           |
| **Ping-Pong substrate** _(optional)_ | Twin substrates alternating between active compute and Auto-Zeroing. Avoids forward-pipeline discontinuity at cost of ~2× area.                                                                                                                                            |
| **Synaptic Drift**                   | Future mechanism: learnable 1D synapse address.                                                                                                                                                                                                                            |
| **Engram Buffer**                    | Future short-term-memory module.                                                                                                                                                                                                                                           |
| **Cell fire**                        | Future STDP wiring rule.                                                                                                                                                                                                                                                   |
| **Route L1 / L2**                    | 4-bit + 4-bit Ganglion addressing. 256 per region. Unrelated to Ganglion-internal L1–L4.                                                                                                                                                                                   |
| **Resident-weight compute**          | Weights never leave substrate during operation. Synonym: in-memory compute (CIM).                                                                                                                                                                                          |
| **Attribution-based learning**       | The learning family this architecture belongs to. Updates by `\|a · W\|` contribution share, not gradient. Related to three-factor synaptic rules, EP, LRP.                                                                                                                |
| **Loss conservation**                | The invariant `Σ children_shares = parent_loss` at every level.                                                                                                                                                                                                            |
| **Multi-parent diffusion**           | At a child with multiple parents, incoming shares from each parent sum into a combined share.                                                                                                                                                                              |
| **Dead-weight collapse**             | Failure mode where weights near zero stop receiving updates. Worst failure mode of attribution learning.                                                                                                                                                                   |
| **Activity vs Relevance**            | Failure mode where high `\|a · W\|` doesn't imply high relevance to loss. Acknowledged in H10. Primary defense: Physical Saturation.                                                                                                                                       |
| **Momentum ceiling saturation**      | Failure mode where 16-bit momentum hits ceiling and differences between strong contributors are lost. Mitigation deferred to scaling or log-domain momentum.                                                                                                               |
| **PVT**                              | Process, Voltage, Temperature variation. The set of analog imperfections that §15 robustness mechanisms defend against.                                                                                                                                                    |
| **Physical Saturation**              | The capacitor's hard ceiling at the supply rail. Same PWM pulse delivers exponentially less voltage change as `V_cap → V_rail`. The architecture's primary defense against winner-take-all in attribution learning. See §6.6.                                              |
| **biological-X**                     | The biological case.                                                                                                                                                                                                                                                       |
| **analog-X**                         | The circuit case (explicit, used in mixed contexts).                                                                                                                                                                                                                       |

---

_End of specification. Theory locked; experiments now drive remaining decisions._
