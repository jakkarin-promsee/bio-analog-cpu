# Draft 2 — Bio-Inspired Analog Neural Compute Architecture

> Working research design document, v2. Single-author, year-2 student project.
> Scope this draft: Python simulation + mathematical justification.
> Constraint: every architectural choice must remain physically realizable in analog circuitry, even if we never fabricate.

---

## 0. Personal Note

> "The fast answer will destroy your creativity."

This document is built from intuition first, not from prior literature. That's deliberate. Comparison against existing work — neuromorphic chips (Loihi, TrueNorth, memristor crossbars), spiking neural networks (LIF, Izhikevich), real hippocampal–prefrontal neuroscience — becomes important _after_ the architecture stabilizes, as validation, not as design input.

---

## 1. Vision

### 1.1 Why current ML feels wrong

- Transformers are O(n²) brute-force pattern matching over a context window.
- LSTMs are closer to "thinking" but limited by their time-series framing.
- Even strong models (Opus-class) are _stable pattern replay over long horizons_ — they shape good output gradually, not creatively at first token. Their backbone is normal-base selection.
- The ceiling isn't model size. The ceiling is the substrate: digital, discrete, von Neumann.

### 1.2 Why von Neumann feels wrong

- A large fraction of modern CPU silicon is spent on branch-prediction SRAM.
- Load/store dominates real compute cost.
- GPUs widened the data pipe but didn't escape the assemble-from-scratch loop. The CPU still arbitrates.
- Repeating instructions is the wrong primitive for continuous computation.

### 1.3 The bet

Real neurons are continuous. Build a continuous compute substrate where:

- **Capacitors** scatter across the die and hold all continuous weights as analog charge.
- **SRAM** is repurposed from branch prediction to wiring paths, sign bits, history bits, and metadata.
- **ALU** is hardwired op-amps performing add / multiply / ReLU directly on capacitor charges.
- **Input / output** are the only external interfaces.
- **Shutdown** is the only event that serializes weights out of the chip.

### 1.4 What "encryption" means in this project

The Aiming section uses the word _encryption_. To be unambiguous: it means **on-chip weight compression** — the entire model state lives on the CPU substrate (capacitors + SRAM) and never spills to external RAM or storage during operation. Weights are "encrypted" in the sense that they exist only as a distributed analog state that no external bus can read without a full chip dump.

This is not a cryptographic primitive.

---

## 2. Project Scope (this draft)

| In scope                                             | Out of scope (for now)                                  |
| ---------------------------------------------------- | ------------------------------------------------------- |
| Ideal-model Python simulation                        | SPICE / circuit-faithful simulation                     |
| Math justification per design choice                 | Hardware fabrication                                    |
| In-model convergence and pattern-recognition metrics | External benchmark comparison (MNIST etc.)              |
| Behavioral correctness of every module               | Op-amp non-idealities, capacitor leakage, thermal noise |
| All choices physically plausible in analog           | Detailed schematics, layout, fab process                |

**Simulation strategy:** ideal first. Robustness (leakage, noise, op-amp imperfection) is layered on later, once the ideal model converges.

**Success metric (interim):** convergence behavior and pattern-recognition quality, evaluated _within_ the architecture. Specifically: does the proposed update rule converge? Does layer reuse preserve accuracy? Does the prefrontal–hippocampus loop form stable attractors? External benchmarking is deferred until the core architecture is stable.

---

## 3. Core Hypotheses

The simulation exists to test these. Each is falsifiable.

**H1 — A biology-inspired update rule can replace distributed backprop on small recurrent NCNs.**
A weight-update scheme using only (a) constant-pulse capacitor charging with natural exponential dynamics, (b) per-scap sign SRAM, (c) tri-state global feedback (−, 0, +), and (d) an active-path history bit, can drive a 2-3-3-2 NCN to converge on simple tasks without per-scap gradient broadcast.
**This is the central open research question.** See §4.2 for the proposed rule and its known weaknesses.

**H2 — Layer reuse increases effective model complexity without adding capacitor / SRAM.**
A network of the form `L1 → L2 → L1 → L3 → L1 → L4`, where L1 is a _single physical NCN_ called three times with different specialist drivers, achieves higher functional complexity than a flat L1→L2→L3→L4 net of the same scap count. The Lottery Ticket Hypothesis says each neuron has unused capacity per output dimension; reuse forces L1 to allocate that capacity intentionally.

**H3 — Recurrent prefrontal–hippocampus prediction loops form stable memory attractors.**
A two-NBN system where prefrontal predicts input + emits a CNS signal, hippocampus predicts using low-grade input + the prefrontal CNS signal, and both backprop on their own prediction loss every clock, converges to a stable recurrent state that recalls patterns from partial cues.

**H4 — Dynamic synapse position (1D address as a learnable parameter) accelerates convergence.**
Treating each synapse's 1D address as a learnable SRAM-stored integer, updated during backprop alongside its capacitor weight, makes the model converge faster and more stably than a fixed-topology baseline.
_Status:_ optional / exploratory. Only worth activating after H1 is validated.

**H5 — Whole-system weight state never leaves the chip during operation.**
The simulated system performs full inference and learning without any LDR / STR of weights to external memory. Only input and output cross the boundary. Serialization happens only at shutdown.

---

## 4. Architecture Specification

### 4.1 Operator layer — op-amp ALU primitives

| Operation        | Implementation                    | Why                        |
| ---------------- | --------------------------------- | -------------------------- | --- | --- |
| Add / Subtract   | Op-amp summing in VCC↔GND range   | Low signal range, low gain |
| Multiply         | Op-amp with variable load         | Needs high gain for `      | w   | >1` |
| ReLU             | Super-diode op-amp                | Hard clip below zero       |
| Capacitor charge | Cascode current mirror            | Precise charge, low drain  |
| Capacitor refill | 8-bit-level SRAM refresh on clock | Compensates leakage        |

Digital math uses a standard binary ALU; analog math uses the table above.

### 4.2 NCN — Nerve Cord Network (base unit)

**Role:** the lowest-level compute primitive. Fixed topology, hardwired, holds its own complexity. Not reconfigurable after fab.

**Topology:** 2-3-3-2 feedforward

- L1: 2 input neurons (input capacitors + cascode current mirror)
- L2: 3 hidden neurons (hardwired op-amp)
- L3: 3 hidden neurons (hardwired op-amp)
- L4: 2 output neurons (output capacitors, charging)

> Naming note: NCN-internal layers (L1–L4) are unrelated to routing hierarchy L1/L2 levels in §4.7. Context disambiguates.

**Per-neuron compute:** `y = a·W + b`, with `a = ReLU(y)`.

**scap (SRAM + Capacitor) cell — the storage primitive:**

- 1 bit SRAM — history (was this neuron active in this forward pass?)
- 1 wire — update_signal (global)
- 1 bit SRAM — weight sign
- 1 capacitor + cascode — continuous weight magnitude
- 8 bits SRAM — refill reference for clock-based leakage compensation

**scap inventory per NCN:**

- L1 → L2: 3×2 weights + 3 biases = **9 scaps**
- L2 → L3: 3×3 weights + 3 biases = **12 scaps**
- L3 → L4: 3×2 weights + 2 biases = **8 scaps**
- **Total: 29 scaps per NCN**

**ALU inventory per NCN:**

- L1 → L2: 6 multiply + 3 add + 3 ReLU
- L2 → L3: 9 multiply + 3 add + 3 ReLU
- L3 → L4: 6 multiply + 2 add + 0 ReLU (output layer, no clip)

**Forward pass:**

1. Input capacitors charged from upstream.
2. Cascode mirror drives the L1→L2 op-amps.
3. ReLU clips each L2 neuron output; history bit set if non-zero.
4. Repeat through L3, L4.
5. L4 output charges output capacitors.

**Backward pass — proposed rule (central open question):**

1. `update_signal` raised high globally.
2. Output error encoded as tri-state (−, 0, +) on a global feedback channel.
3. Each scap reads its history bit, sign bit, and the tri-state feedback.
4. If history bit = active AND feedback ≠ 0: pulse the capacitor in the direction `(sign XOR feedback)` for a fixed pulse width, applying a constant current.
5. Natural capacitor dynamics `v(t) = V·(1 − e^{−t/RC})` convert constant pulses into exponential update curves.

**Why exponential update is desirable:**
Constant-VCC charging of a capacitor produces soft saturation — repeated equal-direction pulses give diminishing increments as `v` approaches `V`, and repeated discharge gives diminishing decrements near zero. This is a **self-stabilizing nonlinearity**: strong contributors are hard to push further; weak contributors are hard to push further down. Implicit regularization without explicit normalization.

**Known weakness (H1 must address):**
This is "c-equal" updating — a pre-modern-backprop technique. Every active scap moves together in the same direction; credit assignment is statistical, not gradient-derived. The hope is that the e^t curve plus stochastic input variation separates good contributors from bad over many samples. **This is exactly what the simulation must validate or refute.**

If the basic rule doesn't converge, fallback / remediation directions, in priority order:

- (a) Modulate `c` by layer depth (early layers slower).
- (b) Add per-scap stochastic gating to break symmetry across the active set.
- (c) Time-encoded feedback that staggers pulse arrival by layer.
- (d) Local Hebbian update per scap as a last resort.

The eventual update rule is the project's research output, not a fixed input.

### 4.3 NBN — Neural Brain Network

**Role:** compose multiple NCNs into a usable network with intentional capacity reuse.

**Boundary structure:**

```
2 input → 4 NCN-input fan-out → 2 NCN block → 4 NCN-output → 2 output
```

Plus a recurrent slot for previous-output → 2 NCN-input → NCN → 2 NCN-output, for systems that fold their own past output back in.

**Reuse pattern (the H2 claim):**

```
input → L1 → L2 → L1 → L3 → L1 → L4 → output
              ↑          ↑          ↑
        (same physical L1, called 3 times with different specialists)
```

- L1 is one physical NCN with appropriate width (e.g. 4 in, 6 out).
- L2, L3, L4 are different specialist NCNs (e.g. 6 in, 4 out each).
- The same L1 hardware processes data three times under three different upstream contexts.

**Why this might work:**
Each neuron in a standard dense net only uses a fraction of its representational capacity per output dimension (Lottery Ticket). Forcing L1 to serve three different specialists drives it to allocate the rest of its capacity. Model complexity grows without growing scap count.

**Known concern (open question 2 in §7):**
The same physical L1 scap gets three "I was active" claims in one forward pass, each under a different specialist context. During backprop, how do we disambiguate which call the feedback belongs to? Candidate answers:

- Multi-bit history register (one bit per call), feedback also indexed by call.
- Time-staggered backprop, one call's worth of feedback at a time.
- Accept the collision and let statistics sort it out (consistent with H1's spirit).

**ALU strategies:**

- _High-cost:_ 4–8 NCN-worth of ALU runs an entire NBN slice in parallel.
- _Low-cost:_ 1 NCN ALU, walk NCN by NCN, intermediate values held in capacitors.

**Default for draft2:** low-cost. It matches the "everything in CPU, no LDR/STR" goal and is closer to what fits in real silicon.

**Workflow per inference:**

1. Load input to input capacitors.
2. NBN ALU walks the L1 → L2 → L1 → L3 → L1 → L4 path.
3. Intermediate values held in capacitors between steps.
4. Output capacitors charged.
5. ALU moves to next NBN instance or loops if recurrent.

### 4.4 BRN — Brain Recurrent Network

**Role:** simulate the prefrontal–hippocampus recurrent loop with two NBNs of different character.

**The two NBNs:**

- **Prefrontal cortex NBN** — dense connectivity tuned for calculation and pattern transformation.
- **Hippocampus NBN** — hierarchical sparse network tuned for memory recall.

**Inputs:**

- _Prefrontal:_ high-quality (full-feature) input + last hippocampus output via CNS.
- _Hippocampus:_ low-quality (reduced-feature) input + prefrontal output via CNS.

**Low-quality input — concrete proposal:**
Pass the high-quality input through a small fixed NCN (or hardwire circuit) that reduces feature count, e.g. 20 → 5 features. Preserves category-level pattern, destroys fine detail. Prevents the hippocampus from short-circuiting the loop by reading raw input — without this, the loop degenerates because the hippocampus stops needing prefrontal input.

**Prefrontal output — two heads:**

- Head A: predict next input (this is the training signal for prefrontal).
- Head B: send to hippocampus via CNS.

**Hippocampus output:** send predicted memory state back to prefrontal via CNS.

**Backprop flow (clock-staggered):**

1. _T=0:_ Prefrontal runs with previous hippocampus state (random at init); predicts input; updates its own NCN weights from prediction loss using the H1 rule; emits CNS signal to hippocampus.
2. _T=1:_ Hippocampus receives low-grade input + prefrontal CNS; predicts; updates its weights; emits CNS back to prefrontal.
3. _T=2:_ Prefrontal re-runs with new hippocampus state. Loop continues.

**Why this is efficient:**
While one brain backprops, the other's output capacitor is charging. Pipelining is natural — no idle cycles.

**Why training is stable in principle:**
Both brains see the _same_ input every clock (input is the shared "key"). Gradient is computed every clock. This continuous reinforcement strengthens the input-to-pattern pathway across both brains. The CNS path strengthens through the recurrent loss itself — both brains pay a cost when CNS quality degrades.

### 4.5 CNS — Central Nervous System

**Role:** the connector between prefrontal ↔ hippocampus (and later STM, if revived). Itself a small group of NCNs.

**Why heavy compute here is affordable:**
Only 2–3 brain regions exist in this architecture, so CNS density doesn't blow the total budget. Richer connectors are within budget.

**Trainability — provisional decision:**
The CNS is _trainable_ but at a **lower learning rate** than prefrontal / hippocampus. Reasoning: training the CNS at full speed risks destabilizing the recurrent loop, because CNS changes alter the very signal both brains backprop against. A slow-changing CNS gives the cortices a stable channel to converge against. **This is itself a hypothesis to test** — alternative options include fully fixed CNS or full-rate CNS, both of which the simulation should compare.

**Optional upgrade:** CNS can host DSP synapses (§4.6) for richer position-based scaling.

### 4.6 DSP — Dynamic Synapse Position (optional / exploratory)

**Role:** add a learnable 1D address per synapse, used to scale signal by distance.

**Mechanism:**

- Each synapse has 3–5 child connections.
- The target neuron broadcasts `(1D position + channel ID)` on a global bus.
- Each child computes `(a·W + b) × distance`, where `distance` is decoded from the binary position and applied through a hardwired op-amp multiplier.
- The target neuron receives the scaled signal on its channel.

**Learning:**
Both the capacitor weight AND the 1D position update during backprop. Position is an integer SRAM counter, incremented or decremented by ±1 per update step (first-pass design — refinement expected).

**Why bother:**
Position acts like a second weight, stored as integer address rather than capacitor charge. Trade-off: SRAM-cheap, but requires global channel arbitration and per-synapse multiply-by-distance hardware. The win is faster, more stable convergence — synapses can "move" instead of fighting their neighbors for the same capacitor range.

**Status:** strictly optional. Activate only after H1 is validated. Routing hierarchy must leave room for DSP channels regardless.

### 4.7 Routes Hierarchy — physical layout

**Goal:** NCNs occupy a 2D grid; addressing must be cheap.

**Two-level addressing:**

- L1 routes: 4-bit, addresses 16 unit-route NCNs ("horizontal" axis).
- L2 routes: 4-bit, addresses 16 L1-route groups ("vertical" axis).
- **Total addressable: 256 NCNs per region.**

**One-time sequential wiring load (initialization only):**

1. Set L1 + L2 path to activate one unit-route NCN.
2. Send that NCN its output channel assignments; it stores them in its local SRAM.
3. Advance to the next NCN, repeat.
4. After full load, every NCN knows where its inputs come from and where its outputs go.

**After load:**
The ALU reads each NCN's SRAM-stored path automatically. No re-routing during operation. This is the "compile once at boot, run for as long as the chip is on" model.

**Per-region optimization:**
Prefrontal, hippocampus, and (later) STM each get specialized variants of the L1 / L2 schema — same base addressing, region-specific tooling.

**Scale question (open):**
256 NCNs per region. Is one region enough for "simple intelligence"? Unknown. **Default for draft2:** simulate one region at full fidelity. Multi-region scaling becomes a phase-2 concern once we know what 256 NCNs can and can't do. Avoid over-engineering until we have data.

---

## 5. Simulation Plan

### Phase 1 — Operator layer

- Implement ideal add, multiply, ReLU, capacitor-charge dynamics in Python.
- Verify e^t charging behavior under constant-pulse input.
- Unit tests per operator.

### Phase 2 — NCN

- Build one 2-3-3-2 NCN.
- Implement `scap` as a class (history bit, sign bit, weight magnitude as float, refill state).
- Forward pass: deterministic.
- **Backward pass: this is where H1 lives.**
  Implement the constant-pulse rule.
  Run on toy regression and toy classification.
  Compare convergence against vanilla SGD baseline of identical topology.
  If failure: iterate through the (a)–(d) remediation list in §4.2.

### Phase 3 — NBN

- Compose multiple NCNs with the L1-reuse pattern.
- Implement low-cost ALU (sequential walk).
- **Test H2:** does reuse-NBN match or beat flat-NBN of equal scap count on the same task?
- Resolve the L1-multi-call disambiguation question.

### Phase 4 — BRN

- Two NBNs + CNS + low-grade-input reducer.
- Implement clock-staggered backprop.
- **Test H3:** does the loop form stable attractors? Does it recall patterns from partial cues?
- Compare CNS learning-rate options (fixed / slow / full).

### Phase 5 — Routes + scaling

- Implement 4-bit / 4-bit routing.
- Sequential wiring load.
- Scale up to 256 NCNs per region.
- **Confirm H5:** no external weight serialization during operation.

### Phase 6 — DSP (conditional on H1)

- Add 1D position SRAM per synapse, plus position-update logic.
- **Test H4:** convergence speedup vs fixed topology.

---

## 6. Math to Prove / Justify

For each design choice, draft2 should eventually contain a written justification. Priority targets:

1. **e^t soft saturation as implicit regularizer.** Derive why constant-pulse charging of a capacitor produces a Lyapunov-like stable update under symmetric stochastic input. Show the fixed point.
2. **Layer-reuse capacity bound.** Argue (informally first, then formally) why a reused L1 has higher effective parameter count than its raw scap count suggests. Lottery Ticket framing is the natural starting point.
3. **Recurrent loop stability.** Conditions on prefrontal / hippocampus / CNS learning rates that keep the loop from oscillating, exploding, or collapsing to a trivial fixed point.
4. **Low-grade-input information bottleneck.** How much feature reduction is _enough_ to prevent the hippocampus from short-circuiting, but _not so much_ that category structure is lost.
5. **Sign-bit + magnitude representation correctness.** Show that `sign-SRAM × cap-magnitude` is functionally equivalent to a signed weight across all forward and backward operations, including the soft-saturation behavior near zero.

---

## 7. Open Research Questions

In rough priority order:

1. **The update rule (H1).** Is constant-pulse + e^t + sign bit + history bit enough to converge? Or do we need (a)–(d) from §4.2?
2. **L1 reuse disambiguation.** During backprop, how does the same physical L1 attribute feedback to the correct call (out of 3 calls per forward pass)?
3. **CNS learning rate.** What ratio of CNS rate to cortex rate keeps the loop stable? Or should CNS be fixed entirely?
4. **Region count for "simple intelligence".** Is one 256-NCN region enough? Two? Need an operational definition of "simple intelligence" before this is answerable.
5. **DSP global channel arbitration.** With many synapses broadcasting positions simultaneously, how is the channel scheduled? TDM? Priority?

---

## 8. Out of Scope for Draft 2

- **STM (short-term memory).** Idea not stable yet; revisit after H3 validates.
- **Cell-fire / STDP.** Too sensitive; no good formulation yet. Open research thread for the future.
- **Real circuit fabrication.** Python only.
- **External benchmark comparison.** Deferred until the architecture stabilizes.
- **Multi-region scaling beyond one routing hierarchy.** Phase 2 work.

---

## 9. Glossary

| Term               | Meaning                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **scap**           | SRAM + Capacitor storage cell. Holds one weight: 1 sign bit, 1 history bit, 1 capacitor magnitude, 8 bits refill reference, 1 update wire. |
| **NCN**            | Nerve Cord Network. Fixed 2-3-3-2 hardwired network. The base compute unit.                                                                |
| **NBN**            | Neural Brain Network. Composed of multiple NCNs with the L1-reuse pattern.                                                                 |
| **BRN**            | Brain Recurrent Network. Two NBNs (prefrontal + hippocampus) plus CNS, in a recurrent loop.                                                |
| **CNS**            | Central Nervous System. The connector between brain regions. Itself a small NCN group.                                                     |
| **DSP**            | Dynamic Synapse Position. Optional mechanism: each synapse has a learnable 1D address used to scale signal by distance.                    |
| **STM**            | Short-Term Memory. Future module. Not specified in draft2.                                                                                 |
| **Cell fire**      | STDP-like group-level wiring rule. Future research thread. Not specified in draft2.                                                        |
| **Routes L1 / L2** | The 4-bit + 4-bit addressing hierarchy for NCN layout. Unrelated to NCN-internal L1–L4.                                                    |
