# Draft 3.2 — Bio-Inspired Analog Neural Compute Architecture

> Working research design document, v3.2.
> Pre-draft4 consolidation. Captures every architectural detail we've converged on.
> Purpose: full re-read pass before locking draft4.
> Scope: Python simulation + math justification.
> Constraint: every choice must remain physically realizable in analog circuitry.

> **What's new vs 3.1:** The backprop section is rewritten honestly. The previous claim that hierarchical diffusion "implements the chain rule spatially" was wrong on inspection — this is **attribution-based learning**, not approximate gradient descent. The corrected framing lives in §5; the consequences ripple to §13 (hypotheses), §15 (math), §18 (protected list), and there's a new §5.2 explaining the family of methods this belongs to.

---

## 0. Reading Guide

This draft is written **from scratch**, not as a diff. If you've read draft3, the most important new sections are:

- **§4 (Brainstem)** — small but explicit. Names the central controller.
- **§5 (Attribution-Based Hierarchical Diffusion)** — the project's central mechanism. **Rewritten in 3.2** to drop the false "implements chain rule" claim and honestly position this as attribution-based learning.
- **§5.2 (What this actually is: attribution, not gradient)** — new section. Explains why this isn't a worse version of backprop; it's a different family of methods that fits the analog substrate naturally.
- **§7.5 (SpecialGeneralist)** — gated reuse pattern. Replaces plain G-reuse.
- **§10 (Limbic Loop with two-timescale learning)** — Cortex-fast, Hippocampus-slow.

If you read only one section, read §5. It's the structural decision that makes everything else click — but the framing has shifted in 3.2 and matters.

---

## 1. Project Framing

This project is **not** an attempt to build intelligence. It is also **not** a 1:1 copy of biology. It is the design of an **analog compute substrate** whose primitives match the kind of computation brains do well:

- **Online learning** — weights update during operation, not in batch-offline epochs.
- **Sparse activation** — only the paths that carry signal contribute or consume energy.
- **Continuous values** — weights and signals live in capacitor voltages, not bit patterns.
- **Resident weight** — weights never leave the substrate during operation. The substrate is also the storage.

The word _encryption_ used in earlier drafts is retired. The technical framing is **resident-weight compute**; the field this belongs to is **in-memory compute (CIM)**. Use both interchangeably: _resident-weight_ is the property we want, _in-memory compute_ is the field.

> "The fast answer will destroy your creativity."

The project is built from intuition first, with literature comparison reserved for after architectural stability. This is deliberate.

**Goal in one sentence:** build a substrate where the kind of computation the brain does is the _cheap_ path, instead of an emulation on top of von Neumann silicon.

---

## 2. Why This Architecture Exists

### 2.1 What's wrong with current ML

- Transformers are O(n²) brute-force pattern matching over a fixed context window.
- LSTMs are closer to "thinking" but limited by their time-series framing.
- Even very strong models shape good output gradually across many tokens; they are stable pattern replay over long horizons, not creative at first token.
- The ceiling isn't model size. The ceiling is the substrate: digital, discrete, von Neumann.

### 2.2 What's wrong with von Neumann

- A large fraction of modern CPU silicon goes to branch-prediction SRAM.
- Load/store dominates the real compute cost.
- GPUs widened the data pipe but didn't escape the assemble-from-scratch loop. The CPU still arbitrates.
- Repeating instructions is the wrong primitive for continuous compute.

### 2.3 The bet

Real neurons are continuous. Build a continuous compute substrate where:

- **Capacitors** scatter across the die and hold all continuous weights as analog charge.
- **SRAM** is repurposed from branch prediction into wiring, sign bits, momentum, and routing metadata.
- **ALU** is hardwired op-amps performing add / multiply / ReLU directly on capacitor charges.
- **Backpropagation** diffuses through a hierarchy of modules, not through per-scap message passing.
- **Input / output** are the only external interfaces.
- **Shutdown** is the only event that serializes weights out of the chip.

---

## 3. Naming and Disambiguation

### 3.1 Semi-anatomical naming

The architecture uses biological names: **Ganglion, Column, Limbic Loop, Commissure, Brainstem, Generalist, Specialist, Synaptic Drift, Engram Buffer**. These are _inspired-by_, not _claiming-to-be_.

- **Default usage** = circuit element. Writing "Brainstem" means our circuit's central controller.
- Prefix **`biological-`** when the actual biology is meant (e.g. "biological brainstem").
- Prefix **`analog-`** when the circuit needs to be flagged explicitly in a mixed-context paragraph.

### 3.2 Layer / role / route disambiguation

- **Ganglion-internal layers** are L1–L4 within a single Ganglion.
- **Column-level roles** use semantic names: Generalist (G) and Specialists (S₁, S₂, S₃).
- **Route addressing levels** are written "Route L1" and "Route L2" to avoid collision with Ganglion-internal L1–L4.

### 3.3 Hierarchy at a glance

```
Brainstem (central controller, small)
    ↓ broadcasts on global bus
Limbic Loop (recurrent two-Column system)
    ├── Cortex Column (fast learning)
    │       ↓ Column-local bus
    │   Generalist + Specialist blocks (S₁, S₂, S₃)
    │       ↓ block-local bus
    │   Ganglia (2-3-3-2 atoms)
    │       ↓ Ganglion-local bus
    │   Scaps (autonomous synapse storage)
    │
    ├── Hippocampus Column (slow learning, consolidation)
    │   (same hierarchy)
    │
    └── Commissure (inter-Column connector, reduced learning rate)
```

Five levels of hierarchy. Each level has its own local bus. Each level knows only its immediate children. This is the structure that makes hierarchical diffusion possible — see §5.

---

## 4. Brainstem — the central controller

### 4.1 Role

The **Brainstem** is the project's central controller. It is the only digital, von-Neumann-flavored component in the architecture. It is small — possibly 5–10k transistors equivalent — but it is _named and budgeted_ rather than hand-waved.

### 4.2 Responsibilities

The Brainstem:

- Reads predictions from the system's output capacitors (via an ADC).
- Receives or holds the label signal for the current sample.
- Computes the **total loss** as a scalar (one MAC's worth of arithmetic).
- Broadcasts the loss on the global broadcast bus, encoded as **pulse width** (wider pulse = bigger loss).
- Broadcasts the tri-state sign `(+, 0, −)` on the global feedback wire.
- Manages clocks: forward-pass clock, backward-pass clock, batch-boundary clock.
- Manages **broadcast control signals**: `update_signal`, `reset_history_signal`, `consolidate_signal` (for Hippocampus consolidation phases).
- Holds the **community SRAM map** that defines which Routes belong to which Column / Limbic region (set at boot).

The Brainstem **does not** orchestrate per-scap updates. Once it broadcasts loss + sign, every level of the hierarchy below it handles its own credit assignment locally — see §5.

### 4.3 What the Brainstem is _not_

- It is **not** a CPU. It has no instruction set, no fetch/decode cycle, no general-purpose registers.
- It is **not** a backprop engine. It does not compute gradients.
- It does **not** know about individual scaps. It speaks only to the top of the hierarchy.

### 4.4 Why this is acceptable

The "no central CPU" goal of the project meant _no von Neumann CPU executing per-weight instructions_. A small controller that times clocks and computes one scalar loss per inference is not what that goal was guarding against. The Brainstem is biologically faithful too — biological brainstems set rhythms, broadcast neuromodulators, and do not perform cognition.

If a future breakthrough lets us distribute the loss compute itself (e.g. each output Ganglion senses its own (prediction − label) locally), the Brainstem shrinks further. That is a §13 (Future Tracks) item, not a blocker.

---

## 5. Attribution-Based Hierarchical Diffusion — the central mechanism

> **Framing note (new in 3.2):** Earlier drafts called this "hierarchical diffusion backprop" and claimed it "implements the chain rule spatially." That claim was wrong on inspection. What this architecture actually does is **attribution-based learning** — closer in spirit to three-factor synaptic rules, Equilibrium Propagation, and Layer-wise Relevance Propagation than to gradient descent. It is not approximate backprop. It is a different family of methods that happens to fit analog substrates naturally.
>
> This section explains the mechanism honestly, contrasts it with vanilla backprop, and points at related work.

### 5.1 The structural idea

Every module at every level of the hierarchy stores a **distribution memory** — how much each of its children contributed to its output on the most recent forward pass. When loss arrives from above, the module divides it across its children in proportion to their stored contributions, then broadcasts those shares on its local bus. Each child does the same in turn, recursively, until the loss reaches the scaps.

```
Brainstem computes total loss L
    ↓ broadcasts L on global bus
Limbic Loop reads L
    ↓ uses its distribution memory → (Cortex's share, Hippocampus's share)
    ↓ broadcasts shares on Limbic-local bus
Cortex Column reads its share
    ↓ uses its distribution memory → (G's share, S₁'s share, S₂'s share, S₃'s share)
    ↓ broadcasts shares on Column-local bus
Each G / S block reads its share
    ↓ uses its distribution memory → (Ganglion shares)
    ↓ broadcasts on block-local bus
Each Ganglion reads its share
    ↓ uses its 29 measurement caps (the Ganglion's distribution memory)
    ↓ broadcasts on Ganglion-local bus
Each scap reads its share, applies PWM update locally
```

### 5.2 What this actually is: attribution, not gradient

The mechanism above is **attribution-based credit assignment**, not gradient descent. The distinction matters and is worth stating clearly.

**Vanilla backprop is sensitivity-based.** It asks: _if I wiggle weight W by ε, how much does loss L change?_ The answer is a derivative, `∂L/∂W`. The chain rule gives an exact decomposition: at each layer, the partial of the loss with respect to a weight is `δ · a`, where `δ` is a per-neuron error signal _routed back through the next layer's weights_ (`δ_l = W_{l+1}ᵀ · δ_{l+1} ⊙ σ'(z_l)`). A weight never appears in its own update; it appears as a router for the layer below it.

**This architecture is attribution-based.** It asks: _given that this scap carried this much current during the forward pass, how much of the parent's error is attributable to it?_ The answer is a proportion: `share_to_child = parent_loss × (child_contribution / total_contribution)`. The "contribution" is what the analog substrate literally measures for free — the current through each scap, which is proportional to `|a · W|`.

These are different epistemic objects, even when they happen to produce similar updates on shallow networks.

**Concrete contrast on a 2-layer net.** Forward: `z₁ = a₀·W₁`, `a₁ = σ(z₁)`, `z₂ = a₁·W₂`, loss `L`.

| Operation                     | Vanilla (sensitivity-based)                                             | This architecture (attribution-based)                                                     |
| ----------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Routing error backward        | Use **W₂** (next layer's weight) as transpose to route `δ₂` into `δ₁`   | Use **\|a·W\|** at the current layer to split parent's share among children               |
| Update of W₁                  | `ΔW₁ ∝ δ₁ · a₀` — input only, **no W₁**                                 | `ΔW_k ∝ share_k` where `share_k` came from `\|a_k · W_k\|` — **W_k is in its own update** |
| Information needed for update | Per-neuron `δ` propagated from output (requires weight transport `W^T`) | Per-scap `\|a · W\|` measured locally during forward pass                                 |
| Loss conservation             | By linearity of chain rule                                              | By explicit normalization (§5.5)                                                          |
| Inactive units                | `σ'(z) = 0` kills propagation                                           | `\|a·W\| = 0` kills propagation                                                           |

The crucial structural divergence: in vanilla, the _next layer's_ weights route the error, and the _current layer's_ weights don't appear in the current layer's update. In this architecture, the _current layer's_ weights appear in both jobs — routing and update — because `|a · W|` is what the substrate naturally measures.

**Why this is acceptable.** The reason most of the ML field uses derivatives is not that derivatives are truer. It is that GPUs are matrix-multiply engines, weight-transport is free in software, and autograd libraries dominate the tooling. The moment you leave that substrate — to biology, to spiking networks, to analog circuits — attribution becomes the natural language because that is what physical substrates can actually measure cheaply.

This architecture is not picking a worse method. It is picking the method that fits its physics. The forward-pass current through a scap is `a · W`. Refusing to use that measurement and trying to recover pure `a` (for vanilla SGD) or pure `δ · a` (for chain-rule-correct updates) would mean fighting the substrate — extra circuits to sense input alone, weight-transport machinery to route per-layer `δ`, none of which the architecture wants to pay for.

### 5.3 The family of methods this belongs to

This architecture is squarely in the family of **three-factor learning rules** (pre-activity × post-activity × neuromodulator) — the dominant theoretical framework for biological synaptic plasticity. Specific anchors in the literature, recorded here so future-me can read them:

- **Frémaux & Gerstner (2016)** — three-factor learning rules review. Maps `pre = a`, `post ≈ W` or `|a·W|`, modulator = loss-derived pulse from Brainstem. This is the closest theoretical home for what this project does.
- **Scellier & Bengio (2017)** — Equilibrium Propagation. Energy-based networks with fully local updates `ΔW ∝ a_clamped · y_clamped − a_free · y_free`. Mathematically proven to compute the gradient in the small-perturbation limit. Same spirit.
- **Lillicrap et al. (2016)** — Feedback Alignment and Direct Feedback Alignment. Shows that random fixed feedback matrices (instead of `W^T`) still let deep networks learn. Establishes that approximate routing is a real result, not a hack.
- **Bach et al. (2015)** — Layer-wise Relevance Propagation (LRP). Attribution method using exactly `|a · W|` to assign output relevance to inputs. The distribution measurement here is structurally identical to LRP scores.
- **Rao & Ballard (1999), Friston (free energy)** — predictive coding. Local error minimization at each layer. Whittington & Bogacz (2017) showed predictive coding approximates backprop under specific conditions.
- **Bellec et al. (2020)** — e-prop. Local learning rule for spiking RNNs using eligibility traces. The 16-bit momentum SRAM in each scap (§6.3) is structurally an eligibility trace.
- **Oja (1982), BCM (1982), Galland & Hinton on Contrastive Hebbian Learning (CHL)** — earlier Hebbian variants. CHL is equivalent to backprop in some networks.

What is established empirically by this body of work:

- Vanilla SGD is the most accurate gradient estimate.
- Feedback alignment shows you can be substantially less accurate and still learn, especially in over-parameterized networks.
- EP and contrastive Hebbian converge to the same place as SGD under specific conditions.
- Pure Hebbian alone does not solve credit assignment across deep layers — you need the modulator (which this architecture has, as the loss pulse from the Brainstem).
- Local rules with global modulators can work for deep networks, but performance varies with architecture and task.

There is no theorem that ranks these methods against vanilla SGD. Whether attribution-based learning converges as well as gradient descent on a given task is an empirical question.

### 5.4 What this commits us to: the known failure modes

Picking attribution-based learning is a real commitment. The literature already tells us what failure modes to watch for, so simulation can target them directly:

1. **Dead weight collapse.** Because `ΔW_k` scales with `|a_k · W_k|`, a weight that reaches zero magnitude receives zero update and stays dead forever. The "floor-at-1" rule on momentum SRAM (§6.3) partially mitigates this — but a _true_ zero weight is still trapped. The simulation must instrument zero-magnitude weight counts over training time. If a substantial fraction of scaps collapse, that is the signal to (a) add a tiny random noise floor to weight updates, or (b) move to path 2 below.
2. **Routing-update coupling.** Because the same `|a · W|` does both the routing of loss and the magnitude of update, errors in one job contaminate the other. Vanilla separates these; we don't. If convergence is slow or unstable in ways that resist tuning, this coupling is the suspect.
3. **Slow convergence on tasks needing precise gradient.** Tasks where the loss surface has narrow valleys may converge slower under attribution than under SGD. Compare against an SGD baseline of identical topology in Phase 2 — not to prove attribution is better, but to know the gap.
4. **Initialization sensitivity.** Attribution-based methods are typically more sensitive to initialization than SGD because they cannot recover from bad starts as gracefully. The small-uniform-magnitude + random-sign init proposed elsewhere should be tested against alternatives.

**Three paths if simulation reveals a fatal problem:**

- _Path 1:_ Strip the multiplier from the measurement. Measure `|a|` only (input sensor instead of multiplier). Update becomes vanilla SGD `ΔW ∝ a · δ`. Cost: 29 extra input sensors per Ganglion ALU, _and_ hierarchical diffusion loses its routing signal (splitting loss by input alone is biased — high input × near-zero weight would still claim a share). Routing math needs a fix.
- _Path 2:_ Keep `|a · W|` for routing, add a separate input sensor for the update step alone. Most chain-rule-correct, most circuit-expensive. Both `a` and `a · W` are stored per scap.
- _Path 3 (current default):_ Accept that this is attribution-based, instrument the failure modes above, test convergence empirically. The cost to find out is low and the architecture is already producing it for free.

We are committing to Path 3 for the baseline. Paths 1 and 2 are documented fallbacks if specific failure modes appear.

### 5.5 Loss conservation as an invariant

We choose **additive** shares (not probability-like):

```
Σ children_shares = parent_loss
```

This makes loss conservation an explicit invariant of the system. Total loss energy injected at the top equals total loss energy absorbed at the leaves. This is verifiable in simulation, catches bugs immediately, and gives the math a clean Lyapunov-style property.

### 5.6 The division problem

The share formula contains a division: `share = loss × (a_i / Σa_j)`. Division in analog circuits is expensive. We solve this by **pre-normalizing** the distribution memory at each level.

When a module finishes its forward pass, it normalizes its measured contributions so they sum to a fixed reference (say, full-scale voltage `V_ref`). Then the share is:

```
share = loss × normalized_contribution_i
```

This is pure multiplication — no division. Multiplication is cheap (one op-amp).

The pre-normalization itself requires one division per module per forward pass, but it happens **once per pass** at the module level, not per scap per pass. The cost is per-module, not per-weight.

### 5.7 Per-level precision

Loss is multiplied at every level as it diffuses. Quantization compounds. Each level needs enough precision that the cumulative error stays bounded.

Provisional precision plan (to refine in simulation):

| Level                         | Distribution storage            | Notes                             |
| ----------------------------- | ------------------------------- | --------------------------------- |
| Limbic Loop                   | 16-bit SRAM per child           | Top level — most bits matter here |
| Column                        | 12-bit SRAM per child           |                                   |
| Generalist / Specialist block | 10-bit SRAM per child           |                                   |
| Ganglion                      | Measurement capacitors (analog) | Continuous, see §6.4              |
| Scap                          | 16-bit momentum SRAM            | EMA accumulation, see §6.3        |

Total stored distribution state is small (one number per child per module), so spending bits at the top is cheap.

### 5.8 Forward pass measurement

Each level's distribution memory is filled **during the forward pass**, using mechanisms appropriate to that level:

- **Ganglion level** uses 29 measurement caps + DC time-measure circuit — see §6.4. Time-to-threshold ∝ current ∝ contribution.
- **Block level (G + S)** sums the output magnitudes of its Ganglia. Stored in block-level SRAM.
- **Column level** sums output magnitudes of its blocks.
- **Limbic Loop level** sums output magnitudes of its Columns (Cortex, Hippocampus).

Higher-level measurement is cheaper because it operates on fewer, larger signals.

### 5.9 Backward pass timing

Backward pass is **synchronous and clock-driven**:

1. _Clock 0:_ Brainstem broadcasts total loss on global bus.
2. _Clock 1:_ Limbic Loop reads, computes child shares, broadcasts on Limbic-local bus.
3. _Clock 2:_ Columns read, compute child shares, broadcast on Column-local bus.
4. _Clock 3:_ G/S blocks read, compute child shares, broadcast on block-local bus.
5. _Clock 4:_ Ganglia read, compute per-scap shares using measurement caps, broadcast on Ganglion-local bus.
6. _Clock 5:_ Scaps update weight capacitors locally via PWM.

Six clocks for a full backward pass, regardless of network size. **The depth of hierarchy bounds the backward latency, not the number of weights.**

### 5.10 Why this matters

This mechanism is _the_ central architectural contribution of the project. It:

- Eliminates the need for per-scap gradient routing.
- Uses only broadcast buses that already exist at each level.
- Maps cleanly to biological neuromodulator diffusion.
- Maps cleanly to predictive-coding theory and three-factor synaptic plasticity rules (see §5.3).
- Uses the substrate's natural physical measurement (`a · W` is the forward current through a scap) instead of fighting it for a quantity it can't cheaply provide.
- Scales: adding a level of hierarchy adds one clock to the backward pass, not N clocks.

What it does **not** do, and we should not claim it does:

- It does **not** implement the chain rule, exactly or approximately.
- It does **not** compute `∂L/∂W` in any rigorous sense.
- It does **not** have convergence guarantees inherited from gradient descent. Whether it converges is empirical.

---

## 6. The Scap — atomic synapse storage

### 6.1 Role

A **scap** holds the analog weight of _one synapse_ — one wire between two neurons inside a Ganglion. It is the project's atom. Every weight in the system lives in exactly one scap.

> **Framing note:** a scap is a _wire_, not a _neuron_. The history of "did current flow through this wire" already implicitly encodes both pre-synaptic activity and post-synaptic activity. There is no need for a separate per-neuron state.

### 6.2 Scap contents

| Component                           | Size        | Role                                                                 |
| ----------------------------------- | ----------- | -------------------------------------------------------------------- |
| Weight capacitor                    | 1 cap       | Analog weight magnitude                                              |
| Sign SRAM                           | 1 bit       | Direction of weight (+ or −)                                         |
| Refill SRAM                         | 8 bits      | Reference level for leakage refresh                                  |
| **Momentum SRAM**                   | **16 bits** | **EMA-accumulated contribution across batches**                      |
| **Community / Routing SRAM**        | N×M bits    | Which bus to read input from, which to write output to (set at boot) |
| `update_signal` wire (input)        | —           | Broadcast from Ganglion-local bus                                    |
| `reset_history_signal` wire (input) | —           | Broadcast clears momentum                                            |
| Tri-ode feedback wire (input)       | —           | Sign of loss direction `(+, 0, −)`                                   |

### 6.3 Momentum SRAM mechanics

The 16-bit momentum SRAM accumulates contribution measurements across batches using **EMA (exponential moving average)** with shift-friendly decay:

```
momentum_new = α × momentum_old + (1 − α) × new_measurement
```

With `α = 3/4` (a single right-shift-by-2 + add): cheap to implement, smooth enough.

Finer decay options available via shift-by-3 (`α = 7/8`) or shift-by-4 (`α = 15/16`). Choice is empirical — settle in simulation.

**Precision floor — the "floor at 1" rule.** When momentum decays toward zero, pin it at 1 (lowest non-zero value) instead of letting it round to 0. This prevents dead-scap collapse: a scap whose momentum reaches 0 in finite-precision SRAM would never receive further updates.

### 6.4 Forward-pass behavior

A scap is passive during forward pass. Its weight capacitor sources current; that current contributes to the output of the post-synaptic neuron. The current itself is measured externally by the ALU's measurement cap for this scap (see §7.4).

### 6.5 Backward-pass behavior — fully autonomous

When `update_signal` goes high on the Ganglion-local bus, the scap reads:

- Its local **sign SRAM** (own weight sign).
- The local **tri-ode feedback** (sign of loss direction).
- The **PWM-encoded share** from the Ganglion's local bus (pulse width = magnitude of share).
- Its own **momentum SRAM** (its accumulated importance).

The scap then updates its weight capacitor:

```
direction = sign_SRAM XOR feedback
weight_cap += pulse_width × momentum × direction
```

The pulse-width × momentum product determines update magnitude. The XOR of signs determines direction.

**No external instruction is needed.** Every scap on the die can update in parallel during a single broadcast pulse. **This is the decentralization win.**

---

## 7. Ganglion — the base compute unit

### 7.1 Role

The **Ganglion** is the project's atom of _computation_ (the scap is the atom of _storage_). Ganglia are hardwired, fixed-topology, not reconfigurable after fab.

### 7.2 Topology — 2-3-3-2 feedforward

- L1: 2 input neurons (input capacitors + cascode mirror)
- L2: 3 hidden neurons (hardwired op-amp + ReLU)
- L3: 3 hidden neurons (hardwired op-amp + ReLU)
- L4: 2 output neurons (output capacitors, charging)

**Per-neuron compute:** `y = aW + b`, with `a = ReLU(y)`.

### 7.3 Scap inventory per Ganglion

- L1→L2: 3×2 weights + 3 biases = **9 scaps**
- L2→L3: 3×3 weights + 3 biases = **12 scaps**
- L3→L4: 3×2 weights + 2 biases = **8 scaps**
- **Total: 29 scaps per Ganglion**

### 7.4 ALU — with distribution measurement

The ALU drives one Ganglion's forward pass and measures the per-scap contribution. The ALU is reused across Ganglia in a Column (low-cost option from earlier drafts is now default).

| Component                        | Count        | Role                                                              |
| -------------------------------- | ------------ | ----------------------------------------------------------------- |
| Hardwired 2-3-3-2 op-amp circuit | 1            | Performs full forward pass including activations                  |
| Input capacitors (global)        | 2            | Read inputs, not drained during compute                           |
| Output capacitors (global)       | 2            | ALU charges them as forward output                                |
| **Measurement capacitors**       | **29**       | One per scap — tracks how much current that scap delivered        |
| **DC time-measure circuit**      | 1            | Counts clocks for each measurement cap to cross A% → B%           |
| **Temp distribution SRAM**       | 29 × 16 bits | Holds measured times transiently before merging into scap momenta |

**Measurement cycle (parallel with forward pass):**

1. Inputs charge the input capacitors.
2. The hardwired 2-3-3-2 begins computing the forward pass.
3. Simultaneously, each scap's measurement cap charges from the current that scap delivers.
4. DC time-measure circuit clocks the rise from A% to B% on each measurement cap. Steeper rise = stronger contribution = shorter time.
5. The 29 measured times land in temp SRAM.
6. At end of forward pass, each Ganglion's measurement values are:
   - Used immediately for the Ganglion's contribution to its parent block (sum, for §5 distribution).
   - Combined via EMA into the corresponding scap's momentum SRAM (§6.3).

**Calibration:** the A% / B% thresholds are referenced against a calibration cap (ALU-local). This makes time-to-threshold a _ratio_ measurement, robust to voltage drift and temperature.

### 7.5 Forward-pass timing risk

The forward pass cannot complete until the slowest measurement cap finishes its threshold crossing. A scap delivering very little current charges its measurement cap very slowly. Worst-case forward time:

```
T_forward = max(output_cap_charge_time, slowest_measurement_cap_charge_time)
```

**Mitigations (test in simulation):**

1. **Cap the measurement time.** If a scap doesn't cross threshold within `T_max` clocks, store `T_max` in its temp SRAM. Loses gradient resolution for weakest scaps; acceptable.
2. **Lower the threshold for weak scaps.** Use 10%→30% instead of 20%→80%. Faster but lower precision.
3. **Adaptive thresholds per scap.** Each scap stores its expected charging time and adjusts thresholds locally. More circuit, more state.

The "cap at T_max" mitigation is the default; explore alternatives only if simulation shows it dominates training time.

### 7.6 Topology rationale (2-3-3-2)

2 × 3 × 3 × 2 = 36 distinct paths from input to output, with 29 scaps. Optimizes **path diversity per scap**, not depth or width. Other topologies for future comparison:

| Topology          | Paths | Scaps | Paths / scap |
| ----------------- | ----- | ----- | ------------ |
| 2-3-3-2 (current) | 36    | 29    | 1.24         |
| 2-5-5-2           | 100   | 49    | 2.04         |
| 3-5-5-3           | 225   | 76    | 2.96         |
| 1-5-1             | 5     | 16    | 0.31         |

Higher paths-per-scap is probably better for the same reasons wider matrices help standard ML. Test after H1 is locked.

---

## 8. Column-Level Hierarchy

The Ganglion is too small for any nontrivial computation by itself. The Column hierarchy composes Ganglia upward.

### 8.1 Hierarchy levels above the Ganglion

| Level                         | Width          | Built from                 | Role                       |
| ----------------------------- | -------------- | -------------------------- | -------------------------- |
| Ganglion                      | 2:2            | scaps                      | Atom of compute            |
| Column                        | e.g. 2:6, 4:12 | Ganglia + translate ALU    | Mid-scale composition      |
| Generalist / Specialist block | e.g. 32:64     | Columns + translate ALU    | Functional role            |
| Cortex / Hippocampus Column   | larger         | G+S blocks + translate ALU | Brain region               |
| Limbic Loop                   | full           | two Columns + Commissure   | Top-level recurrent system |

### 8.2 Translate ALUs

Between hierarchy levels, **translate ALUs** reshape dimensionality. A translate ALU is hardwired for a specific input/output width — e.g. 4-to-12, 6-to-2, 20-to-32. Each block-type pre-declares the translate widths it needs.

Translate ALUs share the same op-amp primitive set as the Ganglion ALU; they are just wider arithmetic. Reused across multiple blocks like the Ganglion ALU is.

### 8.3 Global capacitors as inter-level buffers

Between hierarchy levels, **global capacitors** hold intermediate values:

- Ganglion outputs land in global caps that the next translate ALU reads.
- Column outputs land in global caps that the block-level translate ALU reads.
- And so on upward.

These are the only "registers" in the system. They hold transient state between ALU passes. They are _not_ weight storage — weights live only in scaps.

### 8.4 Distribution memory at each level

Per §5.7, each level above Ganglion has its own distribution memory:

- A block knows how much each Column inside it contributed.
- A Column knows how much each G/S block inside it contributed.
- A Limbic Loop knows how much each top-Column contributed.

These are SRAM, not analog caps — the signals at higher levels are already discretized after passing through ADCs at the Brainstem interface, and quantized distribution storage is cheap.

---

## 9. SpecialGeneralist — gated reuse

### 9.1 The problem with plain reuse

In earlier drafts, the Generalist pattern was `G → S₁ → G → S₂ → G → S₃`, reusing one physical Generalist Ganglion three times. The problem: each reuse call adds gradient signal to G's weights, and these gradients can contradict — S₁'s context wants G to push one way, S₃'s context wants the opposite. G's weights converge to a contradiction-averaged "consensus" that may serve no specialist well.

Two prior fallbacks were considered:

- **Consensus via momentum EMA** (just average the gradients) — risks the consensus being useless.
- **Reservoir-G** (freeze G with random weights) — gives up learning entirely.

Neither is satisfying. The right answer is **gating**.

### 9.2 The SpecialGeneralist mechanism

G receives, in addition to its data input, a **context mask** that tells G which Specialist is currently calling. The mask gates which subset of G's neurons (and therefore which scaps) activate during that call.

```
S₁ calls G with mask M₁ → only G-scaps gated by M₁ activate
S₂ calls G with mask M₂ → different subset activates
S₃ calls G with mask M₃ → another subset activates
```

G's weights are shared across calls, but each call uses a _different sub-network within G_. This is gating / mixture-of-experts, biologically loosely similar to context-dependent neural ensembles.

### 9.3 Why this works

- **G can learn multiple functions** on the same hardware, selected by mask. No consensus-compromise.
- **Distribution measurement naturally supports gating.** A gated-off scap delivers zero current, has zero measurement, contributes zero to the share, receives zero update. The math falls out for free.
- **The mask tells us which call a measurement belongs to.** The conflict-resolution problem from prior drafts disappears entirely.

### 9.4 Architectural cost

- Each Specialist emits a context mask alongside its output (a few wires per scap).
- G has an active-mask register (small SRAM).
- The forward pass uses the mask to gate which scaps participate.

This is cheap.

### 9.5 Where the mask comes from

Three options, in increasing complexity:

1. **Hardcoded per Specialist** — each S has a fixed mask, never changes. Cheap, dumb. Default for first simulation.
2. **Learned per Specialist** — each S has a fixed mask but the mask is trained alongside weights. Smarter, slightly more cost.
3. **Computed from S's output** — mask is a function of S's last output, computed by a tiny circuit. Most flexible, most expensive. Research territory.

Start with (1). Escalate if it underperforms.

### 9.6 What plain G-reuse and Reservoir-G become

- **Plain G-reuse** stays as a _baseline comparison_ in simulation (does SpecialGeneralist actually beat it?).
- **Reservoir-G** stays as a _deeper fallback_ if even SpecialGeneralist fails to learn.

---

## 10. Limbic Loop — recurrent prediction with two-timescale learning

### 10.1 Role

The **Limbic Loop** is the top-level recurrent structure: two Columns (Cortex, Hippocampus) linked by a Commissure, both predicting input, both updating from the prediction error, at _different timescales_.

### 10.2 The two Columns — functionally differentiated by timescale, not topology

Earlier drafts described Cortex as "dense" and Hippocampus as "sparse." We retire that distinction and replace it with the cleaner, more defensible idea: **same structure, different learning rates.**

| Column          | Update cadence            | Effective learning rate                   | Role                                   |
| --------------- | ------------------------- | ----------------------------------------- | -------------------------------------- |
| **Cortex**      | Every clock               | Fast (full update_signal)                 | Fast prediction, online responsiveness |
| **Hippocampus** | Every k clocks (e.g. k=8) | Slow effective; large pulse when it fires | Long-term consolidation, stable prior  |

Implementation cost: **zero new hardware** — just gate the broadcast `update_signal` to Hippocampus on every Nth clock. The momentum SRAM accumulates between consolidations.

**Why timescale alone differentiates them functionally:**

- Cortex's fast updates track immediate input statistics.
- Hippocampus's slow updates settle into the stable, consistent prior.
- Their _difference_ (carried through the Commissure) is the prediction error — exactly what predictive-coding theory says drives learning in cortex.

This is a cleaner story than "different sparsity" because it falls out of one switch (broadcast gating) instead of two parallel design decisions (topology + connectivity).

### 10.3 Inputs to each Column

- **Cortex Column:** high-quality input + last Hippocampus output (via Commissure).
- **Hippocampus Column:** low-quality input (feature-reduced) + Cortex output (via Commissure).

**Low-quality input — concrete proposal:**
A small fixed Ganglion (or hardwired reducer) reduces the feature count, e.g. 20 → 5 features. Preserves category-level pattern, destroys fine detail. Prevents Hippocampus from short-circuiting the loop by reading raw input.

### 10.4 Cortex output — two heads

- Head A: predicts next input. This is the loss signal driving Cortex's own learning.
- Head B: sends to Hippocampus via Commissure.

### 10.5 Hippocampus output

Sends predicted memory state back to Cortex via Commissure. Hippocampus also predicts input (same loss target as Cortex), but at its slow update cadence the effective target becomes "the _stable consistent pattern_ of input" rather than "the next sample."

### 10.6 Recurrence stability — the decay term

The Limbic Loop is a feedback system with non-zero gain. Without a decay term, noise amplifies recursively (Cortex's noisy prediction feeds Hippocampus, whose output feeds Cortex, amplifying each cycle).

**Solution:** add an explicit **decay factor on the recurrent path through the Commissure**. Commissure output is multiplied by a fixed factor (e.g. 0.9) before entering the receiving Column. Implementable as a passive resistor divider in the analog path. Zero compute cost, prevents unbounded amplification.

This is the architecture's equivalent of biological inhibitory interneurons (which prevent runaway excitation in real cortex), or transformer layer normalization (which prevents activation explosion).

### 10.7 Backprop flow with hierarchical diffusion

1. _Forward (every clock):_ Cortex and Hippocampus both run forward; both produce predictions; both fill their distribution memories.
2. _Loss compute:_ Brainstem reads predictions, computes total loss, broadcasts on global bus.
3. _Diffusion down (six clocks per §5.9):_ Loss diffuses through Limbic Loop → Columns → blocks → Ganglia → scaps.
4. _Scap updates:_ On the broadcast pulse, every scap on the die updates locally per §6.5.

Hippocampus gating: if it's not a Hippocampus update clock, the `update_signal` for the Hippocampus side is gated off. Cortex still updates.

### 10.8 Why training is stable in principle

- Both Columns see the same input every clock — input is the shared anchor.
- Loss is computed every clock — continuous attribution signal.
- Decay term prevents recurrent amplification.
- Two-timescale dynamics naturally separate "what's stable" from "what's changing."

---

## 11. Commissure — inter-Column connector

### 11.1 Role

The **Commissure** is the connector between Cortex and Hippocampus Columns. It is itself a small group of Ganglia (not a passive wire), so it can perform light learned translation.

### 11.2 Trainability

The Commissure trains at a **reduced learning rate** compared to its connected Columns. Reasoning: training the Commissure at full speed risks destabilizing the loop, because Commissure changes alter the signal both Columns backprop against. A slow Commissure gives the Columns a stable channel.

Implementation: gate the broadcast `update_signal` to Commissure scaps every Mth clock (where M > k for Hippocampus).

### 11.3 Why heavy compute here is affordable

Only 2–3 Columns exist in this architecture; the Commissure does not need to scale with parameter count, so spending compute on it is locally generous, globally cheap.

### 11.4 Optional Synaptic Drift in Commissure

The Commissure is a natural home for the Synaptic Drift mechanism (§14.2) — its job is precisely cross-region routing, and learnable synapse positions could help here even if they don't help inside Columns.

---

## 12. Routes Hierarchy — physical layout

### 12.1 Goal

Ganglia occupy a 2D grid on the substrate. Addressing must be cheap.

### 12.2 Two-level addressing

- **Route L1:** 4-bit address, selects one of 16 unit-route Ganglia (horizontal axis).
- **Route L2:** 4-bit address, selects one of 16 L1-route groups (vertical axis).
- **Total addressable:** 16 × 16 = **256 Ganglia per region.**

> Route L1 / L2 are addressing levels. They are unrelated to Ganglion-internal L1–L4 layers.

### 12.3 Sequential wiring load (init only)

At boot:

1. Set Route L1 + L2 to activate one unit-route Ganglion.
2. Send that Ganglion its community/routing assignments — input bus to read, output bus to write, parent block ID — stored in the Ganglion's community SRAM.
3. Advance to next Ganglion, repeat.

After the load, every scap knows which global capacitor to read from and which to write to. The ALU reads each Ganglion's routing automatically. **No re-routing during operation.**

### 12.4 Hierarchy routing extension

Hierarchical diffusion (§5) requires that _every level of hierarchy_ be addressable for distribution broadcast, not just Ganglia. The Routes Hierarchy extends to:

- Block-level address: parent block of a Ganglion (set during init).
- Column-level address: parent Column of a block.
- Limbic-level address: top-Column membership (Cortex or Hippocampus side).

This routing state is also held in community SRAM. The total area cost is real — eats into the "recovered branch-prediction area" budget — but is small per scap and bounded by hierarchy depth (5 levels).

### 12.5 Per-region optimization

Cortex Column, Hippocampus Column, Commissure, and (later) Engram Buffer each get region-specific tooling layered on the shared L1/L2 schema.

### 12.6 Scale question (open)

Is 256 Ganglia per region enough for "simple intelligence"? Unknown. Simulate one region at full fidelity first. Scale to multi-region as a separate phase.

---

## 13. Hypotheses (the testable claims)

Each is falsifiable. Each is what the simulation exists to test.

**H1 — Attribution-based hierarchical diffusion converges on substantive tasks.**
Loss broadcast from the Brainstem, diffused through five levels of distribution memory using `|a · W|` as the attribution quantity, arriving at scaps as a PWM update pulse, can drive the system to convergence on tasks that vanilla SGD would also solve. The convergence is empirical, not theoretically guaranteed. _Central open research question._ See §5.4 for the specific failure modes simulation must watch for.

**H2 — SpecialGeneralist beats plain G-reuse.**
Gated reuse (G with context masks from Specialists) achieves higher effective capacity per scap than plain G-reuse and is more stable than Reservoir-G.

**H3 — Two-timescale Limbic Loop converges.**
Fast Cortex + slow Hippocampus + decayed Commissure recurrence forms stable memory attractors and recalls patterns from partial cues.

**H4 — Synaptic Drift accelerates convergence (optional).**
1D learnable synapse address improves convergence speed and stability. Activate only after H1 is validated.

**H5 — Weight state never leaves the substrate during operation.**
Full inference + training run without LDR/STR of weights. Only input and output cross the boundary. Serialization only at shutdown.

**H6 — Loss conservation holds across the hierarchy.**
At every backward pass, the sum of shares at every level equals the loss it received. Verifiable invariant in simulation.

**H7 — Dead-weight collapse is bounded.**
Because attribution-based updates scale with `|a · W|`, weights near zero receive near-zero updates. The combined effect of the floor-at-1 momentum rule (§6.3) plus initialization away from zero (§16, open question 9) keeps the fraction of dead scaps below some bound (target: < 5% after Phase 2 training runs). If H7 fails, escalate to one of the §5.4 fallback paths.

---

## 14. Optional / Future Mechanisms

### 14.1 Activation mixing — tanh in middle, ReLU at boundary

Replace L2 and L3 activations with **tanh-like saturation** (unclipped op-amp at supply rails — free in hardware). Keep L4 as ReLU or bounded ReLU.

**Why:** tanh has continuous gradient everywhere; every scap on a path carries some signal, not just the ones above the ReLU threshold. Improves distribution-measurement coverage.

**Activate:** Phase 2 of simulation, as an A/B test against all-ReLU.

### 14.2 Synaptic Drift (optional, conditional on H1)

Each synapse has a learnable 1D address; signal is scaled by distance.

- Each synapse has 3–5 child connections.
- Target neuron broadcasts `(1D position + channel ID)` on a global bus.
- Each child computes `(aW + b) × distance` via hardwired op-amp multiplier.

Both weight and position update during backprop. Position is an integer SRAM counter, ±1 per update step (baseline) or an analog cap with comparator-ladder ADC at broadcast time (future analog version).

**Status:** activate only after H1 is validated. Likely first used in Commissure (§11.4).

### 14.3 Engram Buffer — short-term memory

A pure capacitor network acting as an LSTM-like layer, holding short-term context stacked from Cortex and Hippocampus. Not specified yet — revisit after H3 is solid.

### 14.4 Cell-fire — STDP wiring

Hebbian rule with spike-timing-dependent plasticity: `Δw ∝ f(pre, post, timing)`. Group-level rewiring driven by co-firing patterns. Open research thread. Not specified.

### 14.5 Distributed loss compute

If each output Ganglion can sense its own (prediction − label) locally — by routing the label voltage to the output Ganglia — the Brainstem's loss-compute responsibility disappears. The Brainstem shrinks to label-broadcaster + clock.

**Status:** future track. Currently bounded by ALU/routing budget. Worth revisiting if architecture matures.

### 14.6 2-3 capacitor analog momentum

Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage. Brainstorm Stages 4–8.

**Status:** post-baseline optimization. Revisit after H1 converges on clean SRAM, so the comparison has a baseline.

### 14.7 Floating-gate transistor storage

Replace refilled capacitor + 8-bit SRAM with floating-gate transistors (NAND-flash technology; Mythic AI's choice). Years of charge retention without refresh.

**Status:** post-baseline. Test after Phase 5 confirms refresh is doing real work.

### 14.8 Inference-only low-power mode

Disable backprop circuitry for inference-only operation. Trivial — a mode bit gating the relevant circuits.

**Status:** trivial future addition. Defer until training is validated.

### 14.9 Failure mode handling

Dead scap recovery, stuck-attractor escape, scaps drifting out of range. Provisional: inject noise periodically as a brute-force escape hatch. Better mechanisms when failure modes are observed empirically.

---

## 15. Math to Justify (priority targets)

Each design choice should eventually have a written justification.

1. **Time-to-threshold ∝ scap contribution.** Under constant-current capacitor charging, `clocks_to_cross(A%, B%) ∝ 1/current`, and `current ∝ (input × weight)` for that wire.

2. **Attribution preserves correct ordering of update magnitudes.** _Replaces the dropped "approximates chain rule" item._ Show that under broadcast loss `δ` from above, scaps that contributed more to the parent's output receive larger updates. This is the minimum mathematical property we need from attribution: monotonicity, not equivalence to the gradient. Compare against vanilla SGD update vectors empirically (cosine similarity), but the _proof obligation_ is monotonicity, not approximation.

3. **Loss conservation is invariant.** `Σ children_shares = parent_loss` at every level, every clock — proves a Lyapunov-style property.

4. **Dead-weight collapse rate is bounded.** Given initialization scheme `(μ_init, σ_init)` and momentum floor-at-1, derive an upper bound on the expected fraction of scaps that reach zero magnitude after N training steps. This is the mathematical companion to H7.

5. **EMA momentum with α=3/4 is contractive.** Under bounded measurement inputs, momentum SRAM stays bounded; precision floor at 1 prevents collapse to zero.

6. **e^t soft saturation as implicit regularizer.** Constant-pulse PWM charging produces a stable fixed point at the supply rails.

7. **Limbic Loop stability with decay factor.** Conditions on Cortex / Hippocampus / Commissure rates and decay factor that prevent oscillation or collapse.

8. **SpecialGeneralist capacity bound.** Why gated G achieves higher effective parameter count than plain G-reuse.

9. **Low-grade input bottleneck.** How much feature reduction prevents Hippocampus short-circuiting without destroying category structure.

10. **Sign-bit + magnitude correctness.** `sign-SRAM × cap-magnitude` is functionally equivalent to signed weight across forward and backward operations.

---

## 16. Open Questions

In rough priority order:

1. **Does attribution-based hierarchical diffusion converge on substantive tasks?** Phase 2 simulation answers this. Compare against SGD baseline of identical topology. Track convergence curves, final loss, and how close cosine-similarity of update vectors is to true gradient (not as a pass/fail, but as a diagnostic). If convergence is dramatically slower or fails on tasks SGD solves cleanly, escalate to §5.4 fallback paths.
2. **Dead-weight collapse rate.** What fraction of scaps reach zero magnitude after Phase 2 training? Is the floor-at-1 momentum rule sufficient, or do we need a noise floor on weight updates? (H7.)
3. **Per-level precision allocation.** 16 / 12 / 10 / continuous / 16 is provisional. Refine by measuring quantization compounding in simulation.
4. **Time-to-threshold A% / B% calibration.** 10/30 vs 20/80 vs 30/70 — test empirically.
5. **SpecialGeneralist mask source.** Start hardcoded; escalate to learned per-Specialist if needed.
6. **Two-timescale ratio k.** What k=8, 16, 32 work best for Hippocampus consolidation cadence?
7. **Commissure rate M.** Slower than Hippocampus (M > k). Sweet spot?
8. **Decay factor in the recurrence path.** 0.9 is a guess. Test 0.8 / 0.9 / 0.95.
9. **Forward-pass slowest-cap problem.** Default mitigation is cap-at-T_max; alternatives if it hurts training time.
10. **Initialization scheme.** Small uniform magnitudes + random signs + zero momentum (baseline). Compare against Xavier/He analog equivalent and sparse-init. Initialization sensitivity is a known failure mode of attribution-based methods (§5.4).
11. **Loss function.** Sign-of-error (tri-state feedback) implies Rprop-like. MSE? Cross-entropy? Specify in Phase 2.
12. **Output decoding precision.** Time-to-threshold on a free capacitor — how many bits effective?
13. **One region or two?** Is 256 Ganglia enough for the kind of task we want to demonstrate?
14. **Region count for multi-region experiments.** Open.

---

## 17. Simulation Plan (baseline)

Six phases. Each closes one open question before the next opens.

### Phase 1 — Operator layer

Ideal-model versions of every analog primitive: add, multiply, ReLU, capacitor charge, time-to-threshold, PWM update. Unit tests.
**Exit:** all operators behave as a perfect analog circuit would.

### Phase 2 — Single Ganglion + attribution diagnostic harness

Build one 2-3-3-2 Ganglion. Implement scap class. Implement the attribution-based update at this level (degenerate case: one Ganglion = one level).
**The harness:** run attribution-based updates and a vanilla-SGD baseline of identical topology in parallel on the same tasks. Record:

- Convergence curves of both rules.
- Cosine similarity between attribution and SGD update vectors at each step (diagnostic only — not pass/fail).
- Fraction of dead scaps (zero-magnitude weights) over training time.
- Distribution of weight magnitudes at the end of training.

**Tasks:** XOR, 1D regression (sine), 2D classification (two-moons).
**Exit:** attribution-based rule converges on at least two of three tasks; dead-weight fraction stays below 5%; convergence is within an order of magnitude of SGD baseline (we are not requiring it to match SGD, only to be competitive). If it fails dead-weight or convergence, escalate to one of the §5.4 fallback paths.

### Phase 3 — Column with SpecialGeneralist

Compose Ganglia under the gated reuse pattern. Test mask gating, distribution measurement with masks, EMA accumulation.
**Tests:** SpecialGeneralist vs plain G-reuse vs flat Ganglion chain of equal scap count.
**Exit:** SpecialGeneralist beats plain G-reuse on at least one task; otherwise fall back to Reservoir-G.

### Phase 4 — Limbic Loop with two-timescale learning

Cortex + Hippocampus + Commissure + low-grade input reducer + decay term.
**Tests:** stable convergence on a recall task; sweep k for Hippocampus and M for Commissure; verify loss conservation invariant (H6).
**Exit:** stable convergence, identified timescale ratios.

### Phase 5 — Routes + scaling

Implement Route L1/L2 + hierarchical addressing. Scale to 256 Ganglia per region. Confirm no LDR/STR (H5).
**Exit:** full region runs Phase 4 task end-to-end on-substrate.

### Phase 6 — Synaptic Drift (conditional on H1)

Add 1D learnable position. Test convergence speedup.
**Exit:** measurable convergence improvement, or rejected.

---

## 18. What Not To Touch (the protected list)

For future-me reading this and being tempted to over-redesign:

1. **The 2-3-3-2 Ganglion topology.** Validated rationale (path-diversity-per-scap optimum among small options). Don't shrink to save area — the ALU and global cap costs would dominate.
2. **Attribution-based learning, not gradient descent.** The substrate measures `a · W` for free. Trying to recover pure `a` (vanilla SGD) or pure `δ · a` (chain-rule-correct) fights the substrate. The fallback paths in §5.4 exist for specific failure modes; do not preemptively switch.
3. **Hierarchical diffusion as the routing mechanism.** Loss flows top-down through the level hierarchy by per-level normalized shares. Optimize within this; don't replace with per-scap gradient broadcast.
4. **The Brainstem as a small central controller.** Distributed loss compute is a future track, not a draft-3.x revision.
5. **Loss conservation as additive (not probability-like).** This is what makes simulation debugging tractable.
6. **The semi-anatomical naming.** Settled in draft2.

Everything else — precision allocations, decay factors, mask sources, timescale ratios, initialization, even loss function choice — is up for negotiation as simulation data comes in.

---

## 19. Glossary

| Term                                | Meaning                                                                                                                                                                                                                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Brainstem**                       | Central controller. Computes loss, broadcasts, manages clocks. Small and named.                                                                                                                                                                                                            |
| **scap**                            | SRAM + Capacitor storage cell. Holds one synapse weight.                                                                                                                                                                                                                                   |
| **Ganglion**                        | Fixed 2-3-3-2 hardwired network. Base compute unit. 29 scaps each.                                                                                                                                                                                                                         |
| **Column**                          | Mid-level composition of Ganglia. Uses translate ALUs at boundaries.                                                                                                                                                                                                                       |
| **Generalist (G)**                  | Shared Ganglion reused under context masks (SpecialGeneralist mechanism).                                                                                                                                                                                                                  |
| **Specialist (S₁, S₂, S₃)**         | Distinct Ganglia that drive G between calls with context masks.                                                                                                                                                                                                                            |
| **SpecialGeneralist**               | The gated reuse mechanism — G with context masks from Specialists.                                                                                                                                                                                                                         |
| **Cortex Column**                   | Fast-learning Column in the Limbic Loop. Predicts input online.                                                                                                                                                                                                                            |
| **Hippocampus Column**              | Slow-learning Column. Same structure as Cortex; consolidates on slow cadence.                                                                                                                                                                                                              |
| **Limbic Loop**                     | Two-Column recurrent system with Commissure connector and decay term.                                                                                                                                                                                                                      |
| **Commissure**                      | Inter-Column connector. Small Ganglion group. Reduced learning rate.                                                                                                                                                                                                                       |
| **Hierarchical Diffusion Backprop** | The central mechanism: loss diffuses through hierarchy levels by per-level share-of-contribution.                                                                                                                                                                                          |
| **Distribution memory**             | Per-level storage of how much each child contributed on the last forward pass. SRAM at higher levels, measurement caps at Ganglion level, momentum SRAM at scap level.                                                                                                                     |
| **Momentum SRAM**                   | 16-bit per-scap SRAM holding EMA-accumulated contribution. Floor-at-1 rule.                                                                                                                                                                                                                |
| **PWM update**                      | Pulse-width-modulated capacitor charge transfer. Used to write the weight update locally per scap.                                                                                                                                                                                         |
| **Tri-ode feedback**                | Global wire carrying loss direction `(+, 0, −)`.                                                                                                                                                                                                                                           |
| **`update_signal`**                 | Broadcast wire whose pulse width encodes share magnitude. Gated per level (full to Cortex, every-k to Hippocampus, every-M to Commissure).                                                                                                                                                 |
| **`reset_history_signal`**          | Broadcast wire that clears momentum SRAM.                                                                                                                                                                                                                                                  |
| **`consolidate_signal`**            | Broadcast clock signal triggering Hippocampus update phase.                                                                                                                                                                                                                                |
| **Translate ALU**                   | Hardwired op-amp circuit between hierarchy levels, performing dimensionality reshaping.                                                                                                                                                                                                    |
| **Global capacitor**                | Inter-level buffer holding transient state between ALU passes. Not weight storage.                                                                                                                                                                                                         |
| **Synaptic Drift**                  | Optional: learnable 1D synapse address.                                                                                                                                                                                                                                                    |
| **Engram Buffer**                   | Future STM module. Not specified.                                                                                                                                                                                                                                                          |
| **Cell fire**                       | STDP rule. Open research thread. Not specified.                                                                                                                                                                                                                                            |
| **Route L1 / L2**                   | 4-bit + 4-bit Ganglion addressing. 256 per region. Unrelated to Ganglion-internal L1–L4.                                                                                                                                                                                                   |
| **Resident-weight compute**         | The project's framing: weights never leave the substrate. Synonym: in-memory compute (CIM).                                                                                                                                                                                                |
| **Attribution-based learning**      | The learning family this architecture belongs to. Updates each weight by a share of parent error proportional to that weight's measured contribution `\|a · W\|`, not by a true gradient `∂L/∂W`. Related to three-factor synaptic rules, Equilibrium Propagation, and LRP. See §5.2–§5.4. |
| **Loss conservation**               | The invariant `Σ children_shares = parent_loss` at every level.                                                                                                                                                                                                                            |
| **biological-`X`**                  | The biological case.                                                                                                                                                                                                                                                                       |
| **analog-`X`**                      | The circuit case in mixed-context paragraphs.                                                                                                                                                                                                                                              |

---

## Closing Note

This is **3.2**, not 4.0. Draft4 should be locked, organized for first-time readers, and treated as canonical. This draft is still meant to be re-read with red pen.

**What got resolved between 3.1 and 3.2:**

- The previous open question "Does the hierarchical diffusion math compose into chain-rule behavior?" is now answered: **no, it doesn't**, and it doesn't need to. The honest framing is in §5. This was an important catch — claiming chain-rule equivalence in a paper or thesis defense would have been a hole reviewers would walk straight into.

**What's still open and worth pushing on before draft4:**

1. **Will attribution-based learning actually converge on real tasks?** This is now H1. Phase 2 simulation answers it. Until that data lands, the architecture is still a bet, not a proven thing.

2. **Is SpecialGeneralist the right answer, or is plain G-reuse + momentum EMA already enough?** §9 argues for SpecialGeneralist; the burden of proof should be that it actually beats plain reuse in simulation. If plain reuse is enough, complexity should drop.

3. **Dead-weight collapse.** §5.4 and H7 take this seriously. But the floor-at-1 momentum rule is a stopgap; if Phase 2 shows even small dead-weight rates, the architecture probably needs a noise floor on weight updates too.

Sleep on it. Mark up what's wrong. Then we write draft4.
