# Draft 2 — Bio-Inspired Analog Neural Compute Architecture

> Working research design document, v2. Single-author, year-2 student project.
> Scope this draft: Python simulation + mathematical justification.
> Constraint: every architectural choice must remain physically realizable in analog circuitry, even if we never fabricate.

---

## 0. Personal Note

> "The fast answer will destroy your creativity."

This document is built from intuition first, not from prior literature. That's deliberate. Comparison against existing work — neuromorphic chips (Loihi, TrueNorth, memristor crossbars), spiking neural networks (LIF, Izhikevich), real hippocampal–prefrontal neuroscience — becomes important _after_ the architecture stabilizes, as validation, not as design input.

---

## 0.1 Naming Convention

Architectural elements use **semi-anatomical names**: Ganglion, Column, Limbic Loop, Commissure, Synaptic Drift, Engram Buffer. These are inspired-by, not claiming-to-be. The biological case is the starting point; the circuit is a deliberate reinterpretation.

When ambiguity matters:

- **Default (unqualified) usage** refers to the circuit element. Writing "Ganglion" means our circuit unit.
- Prefix **`biological-`** when the actual biology is meant (e.g. "biological ganglion").
- Prefix **`analog-`** when the circuit needs to be flagged explicitly in a mixed-context paragraph (e.g. "analog-Commissure" inside a paragraph that also discusses biological commissures).

Layer / role disambiguation:

- **Ganglion-internal layers** are numbered L1–L4 within a single Ganglion only.
- **Column roles** use semantic names: Generalist (G) and Specialists (S₁, S₂, S₃).
- **Route addressing levels** are written "Route L1" and "Route L2" to keep them separate from Ganglion-internal L1–L4.

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

**Success metric (interim):** convergence behavior and pattern-recognition quality, evaluated _within_ the architecture. Specifically: does the proposed update rule converge? Does Column reuse preserve accuracy? Does the Limbic Loop form stable attractors? External benchmarking is deferred until the core architecture is stable.

---

## 3. Core Hypotheses

The simulation exists to test these. Each is falsifiable.

**H1 — A biology-inspired update rule can replace distributed backprop on small recurrent Ganglia.**
A weight-update scheme using only (a) constant-pulse capacitor charging with natural exponential dynamics, (b) per-scap sign SRAM, (c) tri-state global feedback (−, 0, +), and (d) an active-path history bit, can drive a 2-3-3-2 Ganglion to converge on simple tasks without per-scap gradient broadcast.
**This is the central open research question.** See §4.2 for the proposed rule and its known weaknesses.

**H2 — Column reuse increases effective model complexity without adding capacitor / SRAM.**
A Column of the form `G → S₁ → G → S₂ → G → S₃`, where G is a _single physical Generalist Ganglion_ called three times under different Specialist drivers, achieves higher functional complexity than a flat Ganglion chain of the same scap count. The Lottery Ticket Hypothesis says each neuron has unused capacity per output dimension; reuse forces G to allocate that capacity intentionally.

**H3 — The Limbic Loop forms stable memory attractors via recurrent prediction.**
A two-Column system where the Cortex Column predicts input + emits a Commissure signal, the Hippocampus Column predicts using low-grade input + the Cortex Commissure signal, and both backprop on their own prediction loss every clock, converges to a stable recurrent state that recalls patterns from partial cues.

**H4 — Synaptic Drift (1D address as a learnable parameter) accelerates convergence.**
Treating each synapse's 1D address as a learnable SRAM-stored integer, updated during backprop alongside its capacitor weight, makes the model converge faster and more stably than a fixed-topology baseline.
_Status:_ optional / exploratory. Only worth activating after H1 is validated.

**H5 — Whole-system weight state never leaves the chip during operation.**
The simulated system performs full inference and learning without any LDR / STR of weights to external memory. Only input and output cross the boundary. Serialization happens only at shutdown.

---

## 4. Architecture Specification

### 4.1 Operator layer — op-amp ALU primitives

| Operation        | Implementation                    | Why                        |     |     |
| ---------------- | --------------------------------- | -------------------------- | --- | --- |
| Add / Subtract   | Op-amp summing in VCC↔GND range   | Low signal range, low gain |
| Multiply         | Op-amp with variable load         | Needs high gain for `      | w   | >1` |
| ReLU             | Super-diode op-amp                | Hard clip below zero       |
| Capacitor charge | Cascode current mirror            | Precise charge, low drain  |
| Capacitor refill | 8-bit-level SRAM refresh on clock | Compensates leakage        |

Digital math uses a standard binary ALU; analog math uses the table above.

### 4.2 Ganglion — the base compute unit

**Role:** the lowest-level compute primitive. Fixed topology, hardwired, holds its own complexity. Not reconfigurable after fab. The atom of the system.

**Topology:** 2-3-3-2 feedforward

- L1: 2 input neurons (input capacitors + cascode current mirror)
- L2: 3 hidden neurons (hardwired op-amp)
- L3: 3 hidden neurons (hardwired op-amp)
- L4: 2 output neurons (output capacitors, charging)

> L1–L4 here refer only to layers _inside one Ganglion_. They are unrelated to Column roles (§4.3) or Route addressing (§4.7).

**Per-neuron compute:** `y = a·W + b`, with `a = ReLU(y)`.

**scap (SRAM + Capacitor) cell — the storage primitive:**

- 1 bit SRAM — history (was this neuron active in this forward pass?)
- 1 wire — update_signal (global)
- 1 bit SRAM — weight sign
- 1 capacitor + cascode — continuous weight magnitude
- 8 bits SRAM — refill reference for clock-based leakage compensation

**scap inventory per Ganglion:**

- L1 → L2: 3×2 weights + 3 biases = **9 scaps**
- L2 → L3: 3×3 weights + 3 biases = **12 scaps**
- L3 → L4: 3×2 weights + 2 biases = **8 scaps**
- **Total: 29 scaps per Ganglion**

**ALU inventory per Ganglion:**

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

- (a) Modulate the constant pulse `c` by layer depth (early layers slower).
- (b) Add per-scap stochastic gating to break symmetry across the active set.
- (c) Time-encoded feedback that staggers pulse arrival by layer.
- (d) Local Hebbian update per scap as a last resort.

The eventual update rule is the project's research output, not a fixed input.

### 4.3 Column — Ganglion composition with reuse

**Role:** compose multiple Ganglia into a usable network with intentional capacity reuse. A Column is the next-level building block above a single Ganglion.

**Boundary structure:**

```
2 input → 4 Ganglion-input fan-out → 2 Ganglion block → 4 Ganglion-output → 2 output
```

Plus a recurrent slot for previous-output → 2 Ganglion-input → Ganglion → 2 Ganglion-output, for Columns that fold their own past output back in.

**Reuse pattern (the H2 claim):**

```
input → G → S₁ → G → S₂ → G → S₃ → output
        ↑        ↑        ↑
   (same physical Generalist Ganglion, called 3 times with different Specialists)
```

- **G — Generalist Ganglion**: one physical Ganglion with appropriate width (e.g. 4 in, 6 out).
- **S₁, S₂, S₃ — Specialist Ganglia**: three different Ganglia (e.g. 6 in, 4 out each).
- The same G hardware processes data three times under three different upstream Specialist contexts.

**Why this might work:**
Each neuron in a standard dense net only uses a fraction of its representational capacity per output dimension (Lottery Ticket). Forcing G to serve three different Specialists drives it to allocate the rest of its capacity. Model complexity grows without growing scap count.

**Known concern (open question 2 in §7):**
The same physical G scap gets three "I was active" claims in one forward pass, each under a different Specialist context. During backprop, how do we disambiguate which call the feedback belongs to? Candidate answers:

- Multi-bit history register (one bit per call), feedback also indexed by call.
- Time-staggered backprop, one call's worth of feedback at a time.
- Accept the collision and let statistics sort it out (consistent with H1's spirit).

**ALU strategies:**

- _High-cost:_ 4–8 Ganglion-worth of ALU runs an entire Column slice in parallel.
- _Low-cost:_ 1 Ganglion ALU, walk Ganglion by Ganglion, intermediate values held in capacitors.

**Default for draft2:** low-cost. It matches the "everything in CPU, no LDR/STR" goal and is closer to what fits in real silicon.

**Workflow per inference:**

1. Load input to input capacitors.
2. Column ALU walks the G → S₁ → G → S₂ → G → S₃ path.
3. Intermediate values held in capacitors between steps.
4. Output capacitors charged.
5. ALU moves to next Column instance or loops if recurrent.

### 4.4 Limbic Loop — recurrent prediction between two Columns

**Role:** simulate the prefrontal–hippocampus recurrent loop with two Columns of different character, linked by a Commissure.

**The two Columns:**

- **Cortex Column** — dense connectivity tuned for calculation and pattern transformation. (The "prefrontal" role.)
- **Hippocampus Column** — hierarchical sparse network tuned for memory recall.

**Inputs:**

- _Cortex Column:_ high-quality (full-feature) input + last Hippocampus output via Commissure.
- _Hippocampus Column:_ low-quality (reduced-feature) input + Cortex output via Commissure.

**Low-quality input — concrete proposal:**
Pass the high-quality input through a small fixed Ganglion (or hardwire circuit) that reduces feature count, e.g. 20 → 5 features. Preserves category-level pattern, destroys fine detail. Prevents the Hippocampus from short-circuiting the Loop by reading raw input — without this, the Loop degenerates because the Hippocampus stops needing Cortex input.

**Cortex output — two heads:**

- Head A: predict next input (this is the training signal for Cortex).
- Head B: send to Hippocampus via Commissure.

**Hippocampus output:** send predicted memory state back to Cortex via Commissure.

**Backprop flow (clock-staggered):**

1. _T=0:_ Cortex runs with previous Hippocampus state (random at init); predicts input; updates its own Ganglion weights from prediction loss using the H1 rule; emits Commissure signal to Hippocampus.
2. _T=1:_ Hippocampus receives low-grade input + Cortex Commissure signal; predicts; updates its weights; emits Commissure back to Cortex.
3. _T=2:_ Cortex re-runs with new Hippocampus state. Loop continues.

**Why this is efficient:**
While one Column backprops, the other's output capacitor is charging. Pipelining is natural — no idle cycles.

**Why training is stable in principle:**
Both Columns see the _same_ input every clock (input is the shared "key"). Gradient is computed every clock. This continuous reinforcement strengthens the input-to-pattern pathway across both Columns. The Commissure path strengthens through the recurrent loss itself — both Columns pay a cost when Commissure quality degrades.

### 4.5 Commissure — the inter-Column connector

**Role:** connect Cortex ↔ Hippocampus (and later the Engram Buffer, if revived). Itself a small group of Ganglia, not a passive wire.

**Why heavy compute here is affordable:**
Only 2–3 Columns exist in this architecture, so Commissure density doesn't blow the total budget. A richer connector is within budget.

**Trainability — provisional decision:**
The Commissure is _trainable_ but at a **lower learning rate** than the Cortex / Hippocampus Columns. Reasoning: training the Commissure at full speed risks destabilizing the Limbic Loop, because Commissure changes alter the very signal both Columns backprop against. A slow-changing Commissure gives the Columns a stable channel to converge against. **This is itself a hypothesis to test** — alternative options include a fully fixed Commissure or a full-rate Commissure, both of which the simulation should compare.

**Optional upgrade:** the Commissure can host Synaptic Drift synapses (§4.6) for richer position-based scaling.

### 4.6 Synaptic Drift — learnable 1D synapse position (optional / exploratory)

**Role:** add a learnable 1D address per synapse, used to scale signal by distance. The synapse's position itself becomes a parameter that drifts during learning.

**Mechanism:**

- Each synapse has 3–5 child connections.
- The target neuron broadcasts `(1D position + channel ID)` on a global bus.
- Each child computes `(a·W + b) × distance`, where `distance` is decoded from the binary position and applied through a hardwired op-amp multiplier.
- The target neuron receives the scaled signal on its channel.

**Learning:**
Both the capacitor weight AND the 1D position update during backprop. Position is an integer SRAM counter, incremented or decremented by ±1 per update step (first-pass design — refinement expected). Hence "drift" — the synapse slowly migrates along the address axis as training proceeds.

**Why bother:**
Position acts like a second weight, stored as integer address rather than capacitor charge. Trade-off: SRAM-cheap, but requires global channel arbitration and per-synapse multiply-by-distance hardware. The win is faster, more stable convergence — synapses can "move" instead of fighting their neighbors for the same capacitor range.

**Status:** strictly optional. Activate only after H1 is validated. Route hierarchy must leave room for Drift channels regardless.

### 4.7 Route Hierarchy — physical layout

**Goal:** Ganglia occupy a 2D grid; addressing must be cheap.

**Two-level addressing:**

- **Route L1**: 4-bit, addresses 16 unit-route Ganglia ("horizontal" axis).
- **Route L2**: 4-bit, addresses 16 Route-L1 groups ("vertical" axis).
- **Total addressable: 256 Ganglia per region.**

> Route L1 / L2 are addressing levels. Not to be confused with Ganglion-internal L1–L4 (§4.2).

**One-time sequential wiring load (initialization only):**

1. Set the Route L1 + L2 path to activate one unit-route Ganglion.
2. Send that Ganglion its output channel assignments; it stores them in its local SRAM.
3. Advance to the next Ganglion, repeat.
4. After full load, every Ganglion knows where its inputs come from and where its outputs go.

**After load:**
The ALU reads each Ganglion's SRAM-stored path automatically. No re-routing during operation. This is the "compile once at boot, run for as long as the chip is on" model.

**Per-region optimization:**
The Cortex Column, Hippocampus Column, and (later) Engram Buffer each get specialized variants of the Route L1 / L2 schema — same base addressing, region-specific tooling.

**Scale question (open):**
256 Ganglia per region. Is one region enough for "simple intelligence"? Unknown. **Default for draft2:** simulate one region at full fidelity. Multi-region scaling becomes a phase-2 concern once we know what 256 Ganglia can and can't do. Avoid over-engineering until we have data.

---

## 5. Simulation Plan

### Phase 1 — Operator layer

- Implement ideal add, multiply, ReLU, capacitor-charge dynamics in Python.
- Verify e^t charging behavior under constant-pulse input.
- Unit tests per operator.

### Phase 2 — Ganglion

- Build one 2-3-3-2 Ganglion.
- Implement `scap` as a class (history bit, sign bit, weight magnitude as float, refill state).
- Forward pass: deterministic.
- **Backward pass: this is where H1 lives.**
  Implement the constant-pulse rule.
  Run on toy regression and toy classification.
  Compare convergence against vanilla SGD baseline of identical topology.
  If failure: iterate through the (a)–(d) remediation list in §4.2.

### Phase 3 — Column

- Compose multiple Ganglia with the G-reuse pattern.
- Implement low-cost ALU (sequential walk).
- **Test H2:** does a reuse-Column match or beat a flat Ganglion chain of equal scap count on the same task?
- Resolve the G-multi-call disambiguation question.

### Phase 4 — Limbic Loop

- Two Columns (Cortex + Hippocampus) + Commissure + low-grade-input reducer.
- Implement clock-staggered backprop.
- **Test H3:** does the Loop form stable attractors? Does it recall patterns from partial cues?
- Compare Commissure learning-rate options (fixed / slow / full).

### Phase 5 — Routes + scaling

- Implement Route L1 / L2 addressing.
- Sequential wiring load.
- Scale up to 256 Ganglia per region.
- **Confirm H5:** no external weight serialization during operation.

### Phase 6 — Synaptic Drift (conditional on H1)

- Add 1D position SRAM per synapse, plus position-update logic.
- **Test H4:** convergence speedup vs fixed topology.

---

## 6. Math to Prove / Justify

For each design choice, draft2 should eventually contain a written justification. Priority targets:

1. **e^t soft saturation as implicit regularizer.** Derive why constant-pulse charging of a capacitor produces a Lyapunov-like stable update under symmetric stochastic input. Show the fixed point.
2. **Column-reuse capacity bound.** Argue (informally first, then formally) why a reused Generalist Ganglion has higher effective parameter count than its raw scap count suggests. Lottery Ticket framing is the natural starting point.
3. **Limbic Loop stability.** Conditions on Cortex / Hippocampus / Commissure learning rates that keep the Loop from oscillating, exploding, or collapsing to a trivial fixed point.
4. **Low-grade-input information bottleneck.** How much feature reduction is _enough_ to prevent the Hippocampus from short-circuiting, but _not so much_ that category structure is lost.
5. **Sign-bit + magnitude representation correctness.** Show that `sign-SRAM × cap-magnitude` is functionally equivalent to a signed weight across all forward and backward operations, including the soft-saturation behavior near zero.

---

## 7. Open Research Questions

In rough priority order:

1. **The update rule (H1).** Is constant-pulse + e^t + sign bit + history bit enough to converge? Or do we need (a)–(d) from §4.2?
2. **Generalist reuse disambiguation.** During backprop, how does the same physical G attribute feedback to the correct call (out of 3 calls per forward pass)?
3. **Commissure learning rate.** What ratio of Commissure rate to Column rate keeps the Loop stable? Or should the Commissure be fixed entirely?
4. **Region count for "simple intelligence".** Is one 256-Ganglion region enough? Two? Need an operational definition of "simple intelligence" before this is answerable.
5. **Synaptic Drift global channel arbitration.** With many synapses broadcasting positions simultaneously, how is the channel scheduled? TDM? Priority?

---

## 8. Out of Scope for Draft 2

- **Engram Buffer (short-term memory).** Idea not stable yet; revisit after H3 validates.
- **Cell-fire / STDP.** Too sensitive; no good formulation yet. Open research thread for the future.
- **Real circuit fabrication.** Python only.
- **External benchmark comparison.** Deferred until the architecture stabilizes.
- **Multi-region scaling beyond one Route hierarchy.** Phase 2 work.

---

## 9. Glossary

| Term                                 | Meaning                                                                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **scap**                             | SRAM + Capacitor storage cell. Holds one weight: 1 sign bit, 1 history bit, 1 capacitor magnitude, 8 bits refill reference, 1 update wire. |
| **Ganglion** (pl. **Ganglia**)       | Fixed 2-3-3-2 hardwired network. The base compute unit; the atom of the system.                                                            |
| **Column**                           | Composition of multiple Ganglia built around the Generalist-reuse pattern.                                                                 |
| **Generalist Ganglion (G)**          | The single physical Ganglion reused across Specialist contexts inside a Column.                                                            |
| **Specialist Ganglion (S₁, S₂, S₃)** | The distinct Ganglia that drive G between reuse calls.                                                                                     |
| **Limbic Loop**                      | The recurrent two-Column system (Cortex + Hippocampus) connected via Commissure.                                                           |
| **Cortex Column**                    | The calculation / pattern-transformation Column in the Limbic Loop.                                                                        |
| **Hippocampus Column**               | The memory-recall Column in the Limbic Loop.                                                                                               |
| **Commissure**                       | The connector between Columns. A small group of Ganglia, trainable at reduced learning rate.                                               |
| **Synaptic Drift**                   | Optional mechanism: each synapse has a learnable 1D address that drifts during backprop, used to scale signal by distance.                 |
| **Engram Buffer**                    | Future short-term-memory module. Not specified in draft2.                                                                                  |
| **Cell fire**                        | STDP-like group-level wiring rule. Future research thread. Not specified in draft2.                                                        |
| **Route L1 / L2**                    | The 4-bit + 4-bit addressing hierarchy for Ganglion layout. Unrelated to Ganglion-internal L1–L4.                                          |
| **biological-`X`**                   | Refers to the biological case (e.g. _biological ganglion_).                                                                                |
| **analog-`X`**                       | Refers explicitly to the circuit case in a mixed-context paragraph.                                                                        |
