# Draft 3 — Bio-Inspired Analog Neural Compute Architecture

> Working research design document, v3.
> Supersedes draft2.
> Scope: Python simulation + math justification.
> Constraint: every choice must remain physically realizable in analog circuitry.

---

## 0. What's New in Draft 3

If you read draft2 already, here's the diff:

- **H1 is rewritten.** The constant-c update rule is demoted to a fallback. The new H1 is the _distribution-measurement_ rule from the brainstorm: each scap stores its own per-batch contribution as 16-bit momentum, and updates locally via PWM when the master broadcasts a pulse.
- **Backprop is now fully decentralized.** Master computes loss, broadcasts one update pulse, every scap on the chip updates in parallel using its own stored momentum. No per-scap gradient routing.
- **scap structure expanded.** Old: 1-bit history + 1-bit sign + 8-bit refill + 1 cap. New: 16-bit momentum (replaces 1-bit history) + 1-bit sign + 8-bit refill + 1 cap + community/routing SRAM.
- **ALU structure expanded.** Adds 29 measurement capacitors and a DC time-measure circuit per ALU, plus 29×16-bit temp SRAM, to capture each scap's contribution as time-to-threshold during forward pass.
- **Multi-batch and Adam-like optimization are now in scope.** The momentum SRAM enables EMA-style accumulation with shift-friendly decay (0.75 = 3/4).
- **Framing pivot:** "encryption" → **resident-weight compute** (technical term: _in-memory compute_). Goal pivot: from "build intelligence" → "build a substrate efficient for the kind of computation brains do."
- **Post-Baseline Optimizations** is a new section. Holds ideas that are good but premature — to layer on once the baseline converges.
- **Future Tracks** is a new section. Holds the 2-3 cap analog momentum scheme (brainstorm Stages 4–8), Engram Buffer, STDP, failure modes, etc.

If you read only one new section, read §3.3 (ALU) and §3.4 (decentralized backprop). That's where the architectural breakthrough lives.

---

## 1. Foundation

### 1.1 Framing

This project is **not** an attempt to build intelligence, nor a 1:1 copy of biology. It is the design of an **analog compute substrate** whose primitives match the kind of computation brains do well: online, sparse, continuous-learning, in-memory. The substrate is the contribution; whether the workload is "intelligent" is a separate question.

The word _encryption_ used in earlier drafts is retired. The correct technical framing is **resident-weight compute** — all weights live on the substrate, never spill to external RAM or storage, and are only serialized at shutdown. In the literature this property is part of _in-memory compute_ (CIM). Use both terms interchangeably; _resident-weight_ is the property, _in-memory compute_ is the field.

> "The fast answer will destroy your creativity."

Draft3 is still built from intuition first. Existing literature (neuromorphic chips, spiking networks, predictive coding, feedback alignment, reservoir computing) is now visible as related work — we'll cross-validate against it after the architecture stabilizes, not before.

### 1.2 Naming Convention

Architectural elements use **semi-anatomical names**: Ganglion, Column, Limbic Loop, Commissure, Synaptic Drift, Engram Buffer. Inspired-by, not claiming-to-be.

- **Default usage** = circuit element. Writing "Ganglion" means the circuit unit.
- Prefix **`biological-`** when the actual biology is meant.
- Prefix **`analog-`** when the circuit needs to be flagged explicitly in a mixed-context paragraph.

Layer / role disambiguation:

- **Ganglion-internal layers** are L1–L4 within a single Ganglion.
- **Column roles** use semantic names: Generalist (G) and Specialists (S₁, S₂, S₃).
- **Route addressing levels** are written "Route L1" and "Route L2".

### 1.3 Scope & Success

| In scope                                           | Out of scope (for now)                        |
| -------------------------------------------------- | --------------------------------------------- |
| Ideal-model Python simulation                      | SPICE / circuit-faithful simulation           |
| Math justification per design choice               | Hardware fabrication                          |
| In-model convergence + pattern recognition metrics | External benchmark comparison (MNIST, etc.)   |
| Behavioral correctness of every module             | Op-amp non-idealities, leakage, thermal noise |
| All choices physically plausible in analog         | Detailed schematics, layout, fab process      |

**Simulation strategy:** ideal first; robustness layered on later.

**Success metric (interim):** does the new H1 converge? Does G-reuse preserve accuracy? Does the Limbic Loop form stable attractors? Compared _to itself_, with a true-gradient SGD baseline as ceiling reference. External benchmarking is deferred.

---

## 2. Updated Hypotheses

Each is falsifiable. Each is what the simulation exists to test.

**H1 — Distribution-weighted local update converges without per-scap gradient routing.**
A weight-update scheme where (a) each scap measures its own forward-pass contribution as time-to-threshold on a measurement cap, (b) the measurement is accumulated into a 16-bit momentum SRAM local to that scap, (c) the master computes loss and broadcasts a single update pulse whose width encodes loss magnitude, and (d) each scap updates its weight capacitor via PWM `(pulse_width × momentum × sign × tri-state-feedback)`, can drive a 2-3-3-2 Ganglion to converge on simple tasks.
_This is the central open research question._ See §3.4 for the proposed mechanism. The old constant-c rule from draft2 is retained as a fallback in §5.

**H2 — G-reuse increases effective complexity per scap.**
A Column `G → S₁ → G → S₂ → G → S₃`, where G is _one physical Generalist Ganglion_ reused under three Specialist drivers, beats a flat Ganglion chain of equal scap count.
_The Generalist's role is path diversity, not learned computation_ — the Specialists carry the learned weights. See §3.6.

**H3 — The Limbic Loop forms stable memory attractors via recurrent prediction.**
Two Columns (Cortex + Hippocampus), each predicting input, linked via Commissure, both updating every clock, converge to a stable recurrent state that recalls patterns from partial cues.

**H4 — Synaptic Drift accelerates convergence (optional).**
Treating each synapse's 1D address as a learnable SRAM-stored integer makes the model converge faster than fixed-topology.
_Activate only after H1 is validated._

**H5 — Weight state never leaves the chip during operation.**
Full inference + learning happen without LDR/STR of weights. Only input and output cross the boundary. Serialization only at shutdown.

---

## 3. Architecture v3 (the locked design)

### 3.1 Operator Layer — analog ALU primitives

| Operation         | Implementation                               | Notes                                       |
| ----------------- | -------------------------------------------- | ------------------------------------------- | --- | --- |
| Add / Subtract    | Op-amp summing, VCC↔GND range                | Low gain, low range                         |
| Multiply          | Op-amp with variable load                    | High gain for `                             | w   | >1` |
| ReLU              | Super-diode op-amp                           | Hard clip below zero                        |
| Tanh-like         | Unclipped op-amp at supply rails             | Soft saturation (free, post-baseline)       |
| Capacitor charge  | Cascode current mirror                       | Low drain                                   |
| Capacitor refill  | 8-bit SRAM refresh on clock                  | Leakage compensation                        |
| Time-to-threshold | DC measure: clock-count from A% to B%        | **New** — used for distribution measurement |
| PWM update        | Apply VCC for pulse-width-modulated duration | **New** — used for weight update            |

### 3.2 Scap — the storage primitive (updated)

A scap holds the analog weight of _one synapse_ (one wire between two neurons in a Ganglion). It is the project's atom.

> **Important framing note** (correction from draft2): a scap is a _wire_, not a _neuron_. The history of "did current flow through this wire" already implicitly encodes both pre-synaptic activity (upstream neuron fired) and post-synaptic activity (downstream neuron received). The 1-bit history bit in draft2 has now been replaced by 16-bit momentum, which captures _how much_ current flowed, not just whether.

**Scap contents:**

| Component                   | Size        | Role                                                                                             |
| --------------------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| Weight capacitor            | 1 cap       | Analog weight magnitude                                                                          |
| Sign SRAM                   | 1 bit       | Direction of weight                                                                              |
| Refill SRAM                 | 8 bits      | Reference level for leakage refresh                                                              |
| **Momentum SRAM**           | **16 bits** | **Accumulated contribution across batches** (new)                                                |
| **Community SRAM**          | N×M bits    | Routing — which bus to read input from, which bus to write output to, etc. Set once during init. |
| `update_signal` wire        | input       | Broadcast from master                                                                            |
| `reset_history_signal` wire | input       | Broadcast — clears momentum                                                                      |
| Tri-ode feedback wire       | input       | Sign of loss direction `(+, 0, −)`                                                               |

The scap is now **autonomous during update**. When the broadcast `update_signal` is high, the scap executes locally:

```
direction = sign XOR feedback           // resolve update direction
weight_cap += pulse_width × momentum × direction    // PWM-driven charge transfer
```

No external instruction is needed. Every scap on the die updates in parallel under one broadcast pulse. **This is the decentralization win.**

### 3.3 ALU — with distribution measurement (updated)

**Role:** one ALU drives one Ganglion's forward pass and measures the contribution of each of its 29 scaps. The same ALU is reused across multiple Ganglia in a Column (low-cost option from draft2 is now default).

**ALU contents:**

| Component                        | Count        | Role                                                                            |
| -------------------------------- | ------------ | ------------------------------------------------------------------------------- |
| Hardwired 2-3-3-2 op-amp circuit | 1            | Performs full forward pass including activations (ReLU; tanh post-baseline)     |
| Input capacitors (global)        | 2            | Read inputs, not drained during compute                                         |
| Output capacitors (global)       | 2            | ALU charges them as forward output                                              |
| Measurement capacitors           | 29           | One per scap in the Ganglion — each tracks how much current that scap delivered |
| DC time-measure circuit          | 1            | Counts clocks for each measurement cap to cross A% → B%                         |
| Temp distribution SRAM           | 29 × 16 bits | Holds the measured time for each scap, transiently                              |

**Measurement cycle (parallel with forward pass):**

1. Inputs charge the input capacitors.
2. The hardwired 2-3-3-2 begins computing the forward pass.
3. Simultaneously, each scap's measurement cap starts charging from the current that scap delivers.
4. The DC time-measure circuit clocks the rise from A% to B% on each measurement cap. Steeper rise = stronger contribution.
5. The 29 measured times land in the ALU's temp SRAM.
6. At end of forward pass, the ALU sums each temp time into the corresponding scap's permanent momentum SRAM (using EMA-style accumulation with shift-friendly decay `α = 0.75` or `0.875`).

**Why "free" timing:** the forward pass already needs to wait for output capacitors to charge. The measurement happens in that same window. **No critical-path cost.**

**Calibration:** the A% / B% thresholds are referenced against a calibration cap (`cap1` in the brainstorm, ALU-local). This makes time-to-threshold a _ratio_ measurement, robust to voltage drift and temperature. Concrete reference values to test: 20%↔80% (wide, stable) vs 10%↔30% (fast, lower precision).

### 3.4 Decentralized Backprop Flow (new core mechanism)

This is the project's central architectural claim. Read carefully.

**During forward pass:**

- Forward output → output capacitors.
- Distribution measurement → temp SRAM in ALU → accumulated into momentum SRAM in each scap.

**At end of pass:**

- Master compares prediction to label (the "future input" in autoregressive framing, or the supervision signal in any other task).
- Master computes loss.
- Master encodes loss as **a single pulse width** on the broadcast `update_signal` wire — wider pulse = bigger loss.
- Master encodes direction as tri-ode feedback `(+, 0, −)` on the global feedback wire.

**During update broadcast:**

- `update_signal` goes high across the entire die.
- Every scap independently executes:
  ```
  direction = sign_SRAM XOR feedback
  weight_cap += pulse_width × momentum_SRAM × direction
  ```
- The PWM × momentum product creates a per-scap update magnitude proportional to that scap's contribution. Strong contributors update more; weak contributors update less.
- All 7424 scaps in a 256-Ganglion region update in parallel during one pulse.

**Why this works as approximate gradient descent:**

- Per-scap contribution ∝ time-to-threshold ∝ current ∝ `(input × weight)` for that wire.
- That's the local part of `∂loss/∂weight` for that wire.
- The broadcast pulse width carries `|loss|`; the tri-state feedback carries `sign(loss)`.
- Local update = `contribution × |loss| × sign(loss) × sign(weight)`.
- This is the local term of the chain rule. Not the full distributed gradient (no `W_{L+1} × W_{L+2} × ...` propagation), but a _locally measured_ approximation.

**Decay schedule (Adam-like, shift-friendly):**

- EMA accumulation: `momentum_new = (3/4) × momentum_old + (1/4) × new_measurement`.
- The 3/4 and 1/4 are right-shifts (no multiplier needed).
- Finer decay options (7/8, 1/8 → shift-by-3; or 15/16, 1/16 → shift-by-4) available if needed.
- `reset_history_signal` clears momentum across the die (used between epochs or after a phase change).

**Failure path:** if H1 doesn't converge in simulation, fallbacks in priority order:

1. Increase momentum precision toward 24 bits.
2. Add per-call accumulators (see §5 — Reservoir-G alternative).
3. Modulate pulse width by layer depth.
4. Demote to old constant-c rule (draft2 H1) for sanity check.

### 3.5 Ganglion — base compute unit

**Role:** lowest-level compute primitive. Fixed topology, hardwired, not reconfigurable. The atom of the architecture.

**Topology:** 2-3-3-2 feedforward.

- L1: 2 input neurons (input capacitors + cascode mirror)
- L2: 3 hidden neurons (hardwired op-amp + ReLU)
- L3: 3 hidden neurons (hardwired op-amp + ReLU)
- L4: 2 output neurons (output capacitors, charging)

**Scap inventory:**

- L1→L2: 3×2 + 3 = 9 scaps
- L2→L3: 3×3 + 3 = 12 scaps
- L3→L4: 3×2 + 2 = 8 scaps
- **Total: 29 scaps per Ganglion**

**Per-neuron compute:** `y = aW + b`, with `a = ReLU(y)`.

**Forward pass:**

1. Inputs charge L1 caps.
2. Hardwired ALU computes the 2-3-3-2 cascade in one analog sweep.
3. ReLU clips at each hidden layer.
4. Output caps receive the result.
5. Distribution measurement (§3.3) runs in parallel.

**Topology rationale (2-3-3-2):**
2×3×3×2 = 36 distinct paths from input to output. 21 weight wires + 8 bias wires = 29 scaps. The choice optimizes path diversity per scap, _not_ depth or width. Alternative topologies (2-5-5-2, 3-5-5-3, 1-5-1) are tested in §5.

### 3.6 Column — Ganglion composition with Generalist reuse

**Role:** compose multiple Ganglia with intentional capacity reuse.

**Reuse pattern (H2):**

```
input → G → S₁ → G → S₂ → G → S₃ → output
        ↑        ↑        ↑
   (same physical Generalist Ganglion, three calls)
```

- **G — Generalist Ganglion**: one physical Ganglion (e.g. 4-in, 6-out width).
- **S₁, S₂, S₃ — Specialist Ganglia**: three distinct Ganglia.

**Where learning happens:**
The Specialists carry the learned weights. The Generalist provides **path diversity**, not learned computation. Even if G's weights converge toward stable mid-range values due to gradient cancellation across its three calls, that is _fine_ — G's contribution is structural diversity, not feature specialization.

**How momentum makes reuse work:**
In draft2, the same physical G being called 3 times in one forward pass caused gradient collision. In draft3, this is resolved:

- Each call's distribution measurement adds into G's momentum SRAM via EMA.
- Conflicting contributions from S₁, S₂, S₃ contexts average out in G's momentum naturally.
- G learns a _consensus weight_ that serves all three calls.

If gradient collision still degrades training in simulation, fallback options in §5 (Reservoir-G, per-call accumulators).

**ALU strategy (low-cost, default):**
One ALU walks Ganglion by Ganglion. Intermediate values held in global capacitors between steps. Matches "no LDR/STR" constraint.

**Per-inference workflow:**

1. Load input to input caps.
2. ALU walks G → S₁ → G → S₂ → G → S₃.
3. Intermediate values held in global caps.
4. Output caps receive final result.
5. Distribution measurement accumulates into each Ganglion's scap momenta along the way.

### 3.7 Limbic Loop — recurrent prediction between two Columns

**Role:** simulate a prefrontal–hippocampus recurrent loop.

**The two Columns:**

- **Cortex Column** — dense connectivity, tuned for pattern transformation (prefrontal role).
- **Hippocampus Column** — sparse hierarchical, tuned for memory recall.

**Inputs:**

- _Cortex:_ high-quality input + last Hippocampus output via Commissure.
- _Hippocampus:_ low-quality input (feature-reduced) + Cortex output via Commissure.

**Low-quality input — concrete proposal:**
Small fixed Ganglion (or hardwired circuit) reduces feature count from N → N/4 (e.g. 20 → 5). Preserves category-level pattern, destroys fine detail. Prevents Hippocampus from short-circuiting the loop.

**Cortex output — two heads:**

- Head A: predict next input (Cortex's training signal).
- Head B: send to Hippocampus via Commissure.

**Hippocampus output:** predicted memory state back to Cortex via Commissure.

**Backprop flow (clock-staggered, both predict input — baseline):**

1. _T=0:_ Cortex runs with previous Hippocampus state; predicts; H1-updates; emits Commissure signal.
2. _T=1:_ Hippocampus runs with low-grade input + Cortex Commissure; predicts; H1-updates; emits Commissure back.
3. _T=2:_ Cortex re-runs with new Hippocampus state. Loop continues.

Both Columns see the same input every clock — input is the shared "key" that reinforces the path across both Columns. The Commissure trains through the recurrent loss itself.

**Note:** asymmetric timing (Hippocampus updates every k clocks) and differentiated objectives (Cortex predicts future, Hippocampus predicts past) are good ideas, but **premature**. They depend on the baseline being stable first. See §5.5–5.6.

### 3.8 Commissure — inter-Column connector

**Role:** connector between Cortex ↔ Hippocampus. Itself a small group of Ganglia.

**Why heavy compute here is affordable:** only 2–3 Columns exist; Commissure density doesn't blow the budget.

**Trainability (baseline decision):** trainable, but at **reduced learning rate** vs the Columns. Training the Commissure at full speed risks destabilizing the loop — Commissure changes alter the signal both Columns backprop against. A slow Commissure gives the Columns a stable reference channel.

Implement reduced rate by **gating the broadcast `update_signal`**: Commissure scaps see the pulse only on, say, every 4th cycle. Cheap.

**Alternative options to test in §5:** fixed Commissure (no learning at all) vs full-rate Commissure.

### 3.9 Routes Hierarchy

**Goal:** Ganglia occupy a 2D grid; addressing is cheap.

**Two-level addressing:**

- **Route L1**: 4-bit → 16 unit-route Ganglia (horizontal).
- **Route L2**: 4-bit → 16 Route-L1 groups (vertical).
- **Total: 256 Ganglia per region.**

**One-time sequential wiring load (boot only):**

1. Set Route L1 + L2 to activate one unit-route Ganglion.
2. Send the Ganglion its output channel assignments → stored in the scap's community SRAM.
3. Advance to next Ganglion, repeat.

After load: every scap knows which global capacitor to read from and which to write to. The ALU reads each Ganglion's routing automatically. **No re-routing during operation.**

**Per-region optimization:**
Cortex Column, Hippocampus Column, and (later) Engram Buffer each get region-specific tooling layered on top of the shared L1/L2 schema.

**Scale question (still open):** is 256 Ganglia per region enough? Unknown. Simulate one region at full fidelity in baseline; scale to multi-region after.

### 3.10 Synaptic Drift (optional, conditional on H1)

**Role:** add a learnable 1D address per synapse, used to scale signal by distance.

**Baseline mechanism (binary):**

- Each synapse has 3–5 child connections.
- Target neuron broadcasts `(1D position + channel ID)` on a global bus.
- Each child computes `(aW + b) × distance` via hardwired op-amp multiplier with binary distance decode.

**Learning:**
Both the capacitor weight AND the 1D position update during backprop. Position is an integer SRAM counter, ±1 per update step.

**Status:** activate only after H1 is validated. Analog-position version (see §5.8) is a cleaner future direction.

---

## 4. Baseline Simulation Plan

Six phases. Each closes one open question before the next opens. Aim: by end of Phase 4, we know whether the architecture is real.

### Phase 1 — Operator layer

**Goal:** ideal-model versions of every analog primitive.

- Add, multiply, ReLU.
- Capacitor charge dynamics `v(t) = V·(1 − e^{−t/RC})`.
- Time-to-threshold measurement.
- PWM update.
- Unit tests per operator.

**Exit criterion:** all operators behave as a perfect analog circuit would, in a Python harness.

### Phase 2 — Single Ganglion + gradient comparison harness

**Goal:** validate H1.

- Build one 2-3-3-2 Ganglion with scap class (cap + sign + refill + 16-bit momentum).
- Forward pass deterministic.
- Backward pass: implement the §3.4 distribution-weighted PWM update.

**The gradient comparison harness:**
Run H1 on a Ganglion in parallel with vanilla SGD on an identical Ganglion. At each step:

- Record H1's update vector.
- Record true gradient (from autograd) on the same network.
- Compute cosine similarity between H1 updates and true gradients.

If cosine similarity is consistently > 0.3, H1 carries real signal — proceed. If near zero, H1 is random walk — fall back to constant-c (§3.4 fallback list) and re-test.

**Tasks to converge on:**

- XOR (smoke test)
- Toy 1D regression (sine wave)
- Toy 2D classification (two-moons)

**Exit criterion:** H1 converges on at least two of the three; cosine similarity to true gradient is non-trivial.

### Phase 3 — Column with G-reuse

**Goal:** validate H2.

- Compose multiple Ganglia with `G → S₁ → G → S₂ → G → S₃` pattern.
- Use the low-cost ALU (sequential walk, intermediate values in global caps).
- Test G-collision resolution: momentum EMA averages across calls.

**Tests:**

- Reuse-Column vs flat Ganglion chain of equal scap count, same task.
- Measure: convergence speed, final loss, weight variance in G across calls.

**Exit criterion:** reuse-Column matches or beats flat chain on at least one task. If not, fall back to Reservoir-G (§5.7).

### Phase 4 — Limbic Loop

**Goal:** validate H3.

- Two Columns (Cortex + Hippocampus) + Commissure + low-grade input reducer.
- Symmetric timing (both update every clock), both predict input — baseline only.
- Clock-staggered backprop per §3.7.

**Tests:**

- Does the loop form a stable recurrent state? (No oscillation, no collapse.)
- Can it recall a learned pattern from a partial cue?
- Compare Commissure rates: fixed / 0.25× / full.

**Exit criterion:** stable convergence on a recall task; Commissure learning-rate sweet spot identified.

### Phase 5 — Routes + scaling

**Goal:** validate H5; check 256-Ganglion scale.

- Implement Route L1/L2 addressing.
- Sequential wiring load at boot.
- Scale to 256 Ganglia per region.
- Confirm no LDR/STR of weights during inference + training.

**Exit criterion:** full 256-Ganglion region runs Phase 4 task end-to-end with weights staying on-substrate.

### Phase 6 — Synaptic Drift (conditional)

**Goal:** validate H4 (only if H1–H3 are solid).

- Add 1D position SRAM per synapse.
- Position update during backprop, ±1 per step.
- Test convergence speedup vs fixed topology.

**Exit criterion:** measurable convergence improvement.

---

## 5. Post-Baseline Optimizations

These are good ideas that should be **tested after baseline converges**, not bundled in. Each is independent; pick the order based on what the baseline reveals.

### 5.1 Activation mixing — tanh in middle, ReLU at boundary

Replace L2 and L3 activations with **tanh-like saturation** (unclipped op-amp at supply rails — free in hardware). Keep L4 as ReLU or bounded ReLU (clean non-negative output for downstream Ganglia).

**Why:** tanh has continuous gradient everywhere; every scap on a path carries some signal, not just the ones above ReLU's threshold. Improves distribution measurement coverage in H1. Mixed-activation networks are standard in modern ML and have no theoretical contraindication for this substrate.

**Test:** Phase 2 task suite with tanh-L2/L3 + ReLU-L4 vs all-ReLU. Measure convergence speed.

### 5.2 Initialization scheme

Draft2/3 don't specify init. This matters enormously — symmetry breaking at init is what lets learning happen at all.

**Proposed baseline init:**

- All scap **weight magnitudes** at a uniform small value (e.g. 10% of capacitor range).
- All **sign bits** randomized uniformly.
- All **momentum SRAM** at zero.

**Why this should work:** sign randomization breaks symmetry structurally (which wires push positive vs negative). Small uniform magnitudes mean no wire dominates at init. The e^t soft saturation of capacitor charging produces magnitude diversity during training.

**Alternative inits to compare:**

- Random magnitude + random signs (more standard).
- Sparse init: 50% of scaps at zero magnitude, rest random (Lottery Ticket starting condition — if it converges as well as dense, that's a research result in itself).
- Xavier/He analog equivalent (derive from input dimensionality of each layer).

### 5.3 Skip connections vs parallel branches

Two distinct ideas, both worth testing — they answer different questions.

**Skip connection:** L1 output (post-ReLU) directly added to L4 input, bypassing L2 and L3. Costs 2×2 = 4 new scaps. Helps gradient flow.

**Parallel branch (your idea):** two paths `L1→L2→L4` and `L1→L3→L4` running side by side, merging at L4. Helps model capacity, not gradient flow.

**Test both** in Phase 2 task suite. Measure: convergence speed (skip) vs ceiling capacity (branch).

### 5.4 Alternative Ganglion topologies

The 2-3-3-2 is optimized for path diversity per scap. Worth comparing:

| Topology | Paths | Scaps | Paths/scap |
| -------- | ----- | ----- | ---------- |
| 2-3-3-2  | 36    | 29    | 1.24       |
| 2-5-5-2  | 100   | 49    | 2.04       |
| 3-5-5-3  | 225   | 76    | 2.96       |
| 1-5-1    | 5     | 16    | 0.31       |

Higher paths/scap is _probably_ better for the same reasons as wider matrices in standard ML. Test once H1 is locked.

### 5.5 Asymmetric Limbic Loop timing

Cortex updates every clock; Hippocampus updates every k clocks (k=4 or k=8) with proportionally larger pulse width.

**Why:** biological hippocampus consolidates in distinct phases (sleep), not continuously. Reduces gradient noise from rapid Hippocampus shifts destabilizing the Cortex. Creates a natural two-timescale dynamic.

**Cost:** zero hardware — just gating the broadcast.

**When:** only after Phase 4 baseline is stable.

### 5.6 Differentiated Column objectives

Baseline: both Columns predict input. Alternative:

- **Cortex** predicts _next_ input (sensory prediction).
- **Hippocampus** predicts _past_ input (pattern completion / autoencoding).

**Why:** gives each Column a qualitatively different job. Matches predictive-coding theory more closely. The loop becomes a sensible decomposition: "what's coming" vs "what just was."

**When:** only after Phase 4 baseline is stable. Until baseline is solid, differentiated objectives are unevaluable (both columns will fail in the same way for unrelated reasons).

### 5.7 Reservoir-G — fallback for G-reuse collisions

If G-reuse collisions degrade Phase 3 training even with momentum EMA, freeze G entirely:

- Initialize G with diverse non-zero random weights.
- Disable updates to G during training.
- All learning happens in S₁, S₂, S₃.

**What this is:** reservoir computing (echo state networks, liquid state machines). Established theory. G becomes a fixed random projection providing path diversity; Specialists do the work.

**Trade-off:** loses the "G has learned generalist features" story but gains mathematical tractability and eliminates collision entirely.

**Test:** if Phase 3 reuse-Column underperforms flat chain by more than 20%, switch to Reservoir-G and re-test.

### 5.8 Analog Synaptic Drift position

Replace the ±1 SRAM counter (jittery, noisy) with an analog position capacitor decoded to address via a comparator ladder.

- Position drifts smoothly via the same H1 update rule that updates weight.
- Broadcast remains binary (comparator-ladder ADC at broadcast time).
- Continuous storage, discrete addressing — best of both.

**When:** after H4 baseline (Phase 6) works at all.

---

## 6. Future Research Tracks

Deferred entirely. Listed here so they're not lost.

### 6.1 2-3 capacitor analog momentum (brainstorm Stages 4–8)

Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage:

- `effective_momentum = cap2.V × cap3.V`
- Fixed-larger normalization rule (Stage 5) eliminates ambiguity.
- Batch-locked role assignment (Stage 8) eliminates swap-timing risk.

**Why later:** the analog version compounds two unknowns (architecture + storage) with the central unknown (H1). Park until H1 is validated on clean SRAM. Then port to 2-3 cap, measure degradation, publish the comparison — that's a _cleaner_ scientific contribution than starting with analog.

Full design preserved in the brainstorm doc.

### 6.2 Floating-gate transistor storage

Replace refilled-capacitor + 8-bit SRAM with floating-gate transistors (the technology used in NAND Flash; also Mythic AI's choice).

- Holds charge for years without refresh.
- True analog storage, no domain crossing.
- Costs: write speed is much slower than capacitor; endurance is finite (~10⁴–10⁶ writes).

**When:** if Phase 5 results show refresh is doing real work and the area cost is real, port to FGT.

### 6.3 SPICE / robustness simulation

After Python ideal-model converges:

- SPICE simulation of single scap (cap dynamics + leakage).
- Noise-injected Python model calibrated against SPICE.
- Quantify degradation per layer depth, per region scale.

### 6.4 Engram Buffer — short-term memory

The brainstorm prototype: a pure capacitor network holding short-term context stacked between Cortex and Hippocampus. LSTM-like.

**Not specified.** Revisit after H3 (Limbic Loop) is solid.

### 6.5 Cell-fire — group-level wiring (STDP)

Hebbian rule with spike-timing-dependent plasticity: `Δw ∝ f(pre, post, timing)`. Captures "neurons that fire together wire together" at the group level.

**Not specified.** Too sensitive to design without baseline data. Open research thread.

### 6.6 Inference-only low-power mode

Disable backprop circuitry (no measurement caps, no broadcast pulse, no momentum updates) for inference-only operation.

**Implementation:** trivial — just a master mode bit that gates the relevant circuits. Defer until simulation validates training.

### 6.7 Failure mode handling

Open issues:

- What happens when a scap drifts out of range?
- What happens when the Limbic Loop sticks in a wrong fixed-point attractor?
- Dead-scap recovery (scaps whose momentum collapses to zero).

**Provisional baseline:** inject noise periodically to jump out of local optima. The brute-force escape hatch. Better mechanisms to be designed once we see failure modes empirically.

---

## 7. Math to Prove / Justify

Each design choice should eventually have a written justification. Priority targets:

1. **Time-to-threshold ∝ scap contribution.** Show that under linear capacitor charging from a constant current source, `clocks_to_cross(A%, B%) ∝ 1/current` where `current ∝ (input × weight)` for that wire. This is the foundation of H1.

2. **Distribution-weighted update approximates the local gradient.** Show that `momentum × pulse_width × sign(loss) × sign(weight)` approximates `∂loss/∂weight` for the wire, modulo a normalization constant.

3. **EMA decay 0.75 is stable.** Show that the running-average accumulator with `α=0.75` is contractive — momentum doesn't diverge under bounded inputs.

4. **e^t soft saturation as implicit regularizer.** Constant-pulse PWM charging produces a Lyapunov-like stable fixed point at the supply rails. Show it.

5. **Column-reuse capacity bound.** Why does a reused Generalist Ganglion contribute more effective parameters than its scap count? Lottery Ticket framing.

6. **Limbic Loop stability.** Conditions on Cortex / Hippocampus / Commissure learning rates that prevent oscillation, explosion, or trivial fixed-point collapse.

7. **Low-grade input bottleneck.** How much feature reduction prevents Hippocampus short-circuiting without destroying category structure?

8. **Sign-bit + magnitude correctness.** Show `sign-SRAM × cap-magnitude` is functionally equivalent to a signed weight across all forward and backward operations.

---

## 8. Open Questions

In rough priority order:

1. **Does H1 actually carry gradient signal?** Phase 2 gradient comparison harness answers this.
2. **Time-to-threshold A%/B% calibration.** What thresholds give the best precision/speed trade-off? Test 10/30, 20/80, 30/70.
3. **G-reuse collision resolution.** Does momentum EMA handle conflicting Specialist contexts gracefully? If not, fall to Reservoir-G.
4. **Commissure learning rate sweet spot.** Fixed vs slow vs full — what ratio keeps the loop stable?
5. **One region or two?** Is 256 Ganglia enough for "simple intelligence" (operationally definable as: convergence on a recall task with partial cues)?
6. **Initialization sensitivity.** How much does the choice of init affect convergence?
7. **What's the right loss function?** Sign-of-error (tri-state feedback) implies Rprop-like. MSE? Cross-entropy? Specify in Phase 2.
8. **Output decoding precision.** Time-to-threshold readout on a free capacitor — how many bits effective?
9. **Synaptic Drift broadcast arbitration.** With many synapses sharing one global channel — TDM? Priority? Defer to Phase 6.

---

## 9. Glossary

| Term                         | Meaning                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | --- |
| **scap**                     | SRAM + Capacitor storage cell. Holds one synapse weight. Contents: 1 cap + 1 sign bit + 8 refill bits + 16 momentum bits + N×M community/routing bits. |
| **Ganglion** (pl. Ganglia)   | Fixed 2-3-3-2 hardwired network. The base compute unit. 29 scaps each.                                                                                 |
| **Column**                   | Composition of Ganglia using the Generalist-reuse pattern.                                                                                             |
| **Generalist (G)**           | The reused Ganglion inside a Column. Provides path diversity.                                                                                          |
| **Specialist (S₁, S₂, S₃)**  | The distinct Ganglia that drive G between reuse calls. Carry learned weights.                                                                          |
| **Limbic Loop**              | Two-Column system (Cortex + Hippocampus) connected via Commissure.                                                                                     |
| **Cortex Column**            | Pattern-transformation Column in the Limbic Loop.                                                                                                      |
| **Hippocampus Column**       | Memory-recall Column in the Limbic Loop.                                                                                                               |
| **Commissure**               | Inter-Column connector. Small Ganglion group. Trainable at reduced rate.                                                                               |
| **Synaptic Drift**           | Optional: each synapse has a learnable 1D address.                                                                                                     |
| **Engram Buffer**            | Future STM module. Not specified.                                                                                                                      |
| **Cell fire**                | STDP wiring rule. Open research thread. Not specified.                                                                                                 |
| **Resident-weight compute**  | The project's framing: weights never leave the substrate. Synonym: in-memory compute (CIM).                                                            |
| **Distribution measurement** | Time-to-threshold readout on a measurement cap, capturing per-scap contribution during forward pass.                                                   |
| **Momentum SRAM**            | 16-bit per-scap SRAM holding EMA-accumulated contribution across batches. Replaces draft2's 1-bit history.                                             |
| **PWM update**               | Pulse-width-modulated capacitor charge transfer, used to write the weight update locally per scap.                                                     |
| **Tri-ode feedback**         | Global wire carrying loss direction `(+, 0, −)`.                                                                                                       |
| **`update_signal`**          | Broadcast wire whose pulse width encodes `                                                                                                             | loss | `.  |
| **`reset_history_signal`**   | Broadcast wire that clears momentum SRAM across the die.                                                                                               |
| **Route L1 / L2**            | 4-bit + 4-bit addressing for Ganglion layout. 256 per region. Unrelated to Ganglion-internal L1–L4.                                                    |
| **biological-`X`**           | The biological case.                                                                                                                                   |
| **analog-`X`**               | The circuit case (explicit, used in mixed contexts).                                                                                                   |

---

## Closing Note

This draft is still a working document. The framing isn't perfect, the names will probably evolve, and at least three sections will get rewritten once Phase 2 data comes back. That's expected.

The two things to protect:

1. **The H1 distribution-measurement rule is the project's central bet.** Everything else is scaffolding around it. If Phase 2 falsifies H1, the architecture pivots; nothing else.
2. **Storage decisions are deferred deliberately.** 16-bit SRAM is the baseline because it isolates the H1 question from the storage question. The 2-3 cap scheme is a beautiful design and will be revisited after baseline. Don't be tempted to start there.

Everything else — names, optimization order, even which Ganglion topology — is up for negotiation as data comes in.
