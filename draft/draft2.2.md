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

- **#Explian_H1** (Explain more about my scaps, I think you understand it wrong a bit)
  - First, about your pre/post synaptic history. I will explain my scap again.
  - From 2-3-3-2 Ganglion, my scaps isn't a neural itself, it's a connection wire between neural. For example, 2 to 3 layer, it's 2 neural to 3 neural. IT's require 2x3 wire (a x W) + 3 wire (b), those wire is scaps (the capacitor weight level + SRAM of operation). So now asumme that first layer is L1, and second layer is L2, L1 have 2 neural (L1_1 and L1_2) and L2 have 3 neural (L2_1, L2_2, and L2_3). it will use 6 scaps. The aW is (L1_1 to L2_1, L1_2 to L2_1), (L1_1 to L2_2, L1_2 to L2_2), and (L1_1 to L2_3, L1_2 to L2_3). And anoter 3 scaps that is b as bL2_1, bL2_2, and bL2_3. Those scaps connecting is actual have only 1 duty, that is "is pre neural connect post neural or not". So I think my scaps history already capture that correct current flow. If L1_1 already be zero by it activation function, the L1_1 to L2_1, L1_1 to L2_2, L1_1 to L2_3 will actutally close. The b scaps will be more special such as bL2_1 will be L1_1 to L2_1 Or L1_1 to L2_2 Or L1_1 to L2_3. The bias term will be tilt a bit, but it wil eventually convergence.
  - So my scaps is keep as a wire, While activate function will keep in neural. The neural have to sum up all wire before, then just compute activate functio.

- **#Extend_H1** (I found the way to improve it, making distibution updating instead of constant-c)
  - The reason I use this constant-c backpropagation, because I hit the AD/DC wall. AC can't translate to DC perfectly, DC to AC too. While updating AC level in capacitor, it's required time to drain it (Fixed VCC). And it's so hard to covernt capacitor wieght level to this time. (Can't convernt AC level to time scale that keep on SRAM). So that time I just use only constant-c updating for just a learning concept. (no headace about cpu architecture and converting theory)
  - But now I found new break throught. First, this 2-3-3-2 Ganglion, It need the 2 input capacitor that already charged, then using hardwired ALU that fit with this 2-3-3-2, charging the output capacitor. It's already using a time. So now, what if my 2-3-3-2 fix ALU, having a AC to DC converting module? I will using another capacitor that connect with each weight AC level, then measure the curse, how much time I use to make new capacitor V go from A to B, Using simple bit couter circuit to count a time. With this convert module, we can measure how each scap node distribute the output. We can measure it parallel the time the output capacitor charge.
  - To make it come true, we have to add more architecture. From normal:
    - L1 → L2: 3×2 weights + 3 biases = **9 scaps**
    - L2 → L3: 3×3 weights + 3 biases = **12 scaps**
    - L3 → L4: 3×2 weights + 2 biases = **8 scaps**
    - **Total: 29 scaps per Ganglion**
  - We have to add 4-8 bits SRAM for each scaps to keep distribution level of each scaps
  - Then at ALU for Ganglion, we have to add more 29 capacitor to measure how each scaps distribute are
  - Then when updating time, we can use 1 bit of update_signal + 1 bit of history signal + 4-8 bit of distribution level to make dynamic updating
  - So we we use same amount of time, only adding only 4-8 SRAM fo each scaps, and only add 29 capacitor and time measure module in reuse ALU
  - This trade off we take will be the greatest progress of our model

**H2 — Column reuse increases effective model complexity without adding capacitor / SRAM.**
A Column of the form `G → S₁ → G → S₂ → G → S₃`, where G is a _single physical Generalist Ganglion_ called three times under different Specialist drivers, achieves higher functional complexity than a flat Ganglion chain of the same scap count. The Lottery Ticket Hypothesis says each neuron has unused capacity per output dimension; reuse forces G to allocate that capacity intentionally.

- **#Explian_H2** (Second-order architectural concerns that it will refute each other to zero)
  - That is a good catch. But the key isn't G layer. It's a S_1, S_2, S_3, etc. Even G weight update will refute itself to 0, but these S (special) layer will be train. The G (general) is just to make diversity of path route that expand model complexity.

**HX - Question - Ganglion topology is arbitrary and probably wrong. Why 2-3-3-2?**
The reason I use 2-3-3-2, because it's simple to use. This haven't much width or height. I'm aiming to neural activity path diversity. 2-3-3-2 give 6 activation layer at the middle layer, and give 21 wire (aW + b). And in the future I will test too, which combination is good. may be 1-5-1 will more good.

**HX - Question - Capacitor + 8-bit SRAM refill is DRAM-with-extra-steps unless designed carefully.**
I don't know it good or not. Same as other architecture, SRAM to keep real weight is using so huge areas to keep smooth level. While capacitor can keep more scale and so fast and computation. And if we still use SRAM, eventually I think we will hit the same problem of last achritecture.

**HX - Question - "Encryption" framing will cost you credibility**
This is very very right. Now I just don't know how to call it. So "encrytion" I use now is so temporary.

**HX - Optimization Ideas**

## Ideas 1

Make the Limbic Loop asymmetric in time, not just in input quality. Right now Cortex and Hippocampus update every clock. Brains actually do something different — cortex runs continuously, hippocampus consolidates during specific phases (sleep-like). A version of this: Cortex updates every clock, Hippocampus updates every k clocks but with a larger effective learning rate. This:

- Reduces gradient noise from rapid Hippocampus shifts destabilizing the Cortex.
- Creates a natural two-timescale dynamic that matches biology.
- Doesn't cost you any extra hardware.

---

I think this is so good ideas. You have same thought like me. The real hippocampus update isn't when we awake, it rather update on the night. Human have learning rate due to emotional level. If you get hurt so hard by the tiger, Your hippocampus will update it so hard that time -- the truama. But if you're in normal life, hippo campus is updating so slow, everything will be keep in short term memory then will be update hippocampus at night.

But my problem now is "I don't have stable model till the short term memory brain yet". I don't know that quickly push myself to this complex brain activity will be good or not. So this time I think I should make stable RNN first.

## Ideas 2

Differentiate the two Columns' objectives. Right now both predict the input. There's no principled reason Cortex would learn something different from Hippocampus other than connectivity density. Try:

Cortex predicts next input (sensory prediction).
Hippocampus predicts past input (autoencoding / pattern completion).

Now they have qualitatively different jobs and the loop becomes a sensible decomposition: "what's coming" vs "what just was."

---

This is so great ideas too. You're thinking like me at first. But it's stucking on same problem. If our model isn't stable yet since first backpopagration. This step will be so hard to evealuate. But I think your ideas is interesting than me. Fr, I think that brain should predict the future so hard. But the concept that let hippocampus predict the past is so mind blowing. It's so true in real machanism.

## Ideas 3

Make Synaptic Drift use a real analog position. The ±1 SRAM counter is jittery and either too slow or too noisy. A cleaner version: position is its own analog capacitor charge, decoded to address via a comparator ladder. Now position drifts smoothly the same way weight does. Same H1 update rule applies to both. Conceptual unification.

---

Yeah, the Synaptic Drift is so conceptual. I have no stable plan yet. But the reason I use binary signal, it's because I don't know yet how to broad cast with analog. My progress now is all brain part having a broadcast wire, the target brain just use a clock to broadcast its 1D position with binary, other brain will recieve it perfectly and will compute the response level itself.

## Ideas 4

Initialize scap signs randomly, weights at small magnitude. Draft2 doesn't specify initialization. This matters enormously — symmetry breaking at init is what lets learning happen at all. Standard Xavier/He won't translate directly; you'll need to derive an analog equivalent. This is a small math problem that's worth solving early.

---

This is so critical point too. As you said I didn't plan it yet. And I think it's so crucail. I may test in on actual simulation. But if you have ideas, you can write it to me.

## Ideas 5

Add skip connections inside the Ganglion. L1→L4 direct path (in addition to L1→L2→L3→L4) helps gradient flow and is essentially free in hardware (a few wires). Real residual networks owe much of their success to this. Easy win.

---

Yeah this is so great Ideas too. I'm thinking about it before... again 🤣🤣🤣.
My first ideas is about

L1 (2 to 4) -> (4 to 2) L2 -> (4 to 2) L4
same L1 (2 to 4) -> (4 to 2) L3 -> same (4 to 2) L4

It's a wirign attribute. But I don't know how much it can do. Will it convergne more easy or hard. So It will be test in simulation time too.

## Ideas 6

Consider tanh instead of ReLU for some layers. A super-diode op-amp does ReLU. An unclipped op-amp output gives you something tanh-like for free (saturates at supply rails). Tanh has continuous gradient everywhere, which helps your statistical-credit-assignment rule because every active scap contributes signal, not just the ones above zero. Mix tanh and ReLU layers and you may get better training stability.

---

Tbh, I use relu cause I don't know what to use. 🤣🤣🤣. I just use it cause we just delete the negative value. So if there have more better ideas, I ready to accept it.

**HX - Missing pieces**
Things draft2 doesn't address that will eventually matter:

- Loss function specification. What is the prediction loss? MSE? Cross-entropy? Sign-of-error? The tri-state feedback (−, 0, +) implies sign-of-error, which is closer to Rprop than SGD. State this explicitly.
  - My Loss function now is so shit. From current model that we use all distribute compuataion. I think real cell didn't be like that. real nerve didn't know all how other cell distribution is. So I start with just the regression on open path. And Loss funciton didn't send distribute through layer like normal. But we can control learning via just a updating time (draining/charging time) to real scaps.

- Output decoding. When does the final capacitor charge get read by the outside world? At what precision? Is there an ADC?
  - yeah, this a problem too. Now I think I will use time trigger capacitor level method. Mesureing how long time we use to charge free cpacitor from 20% to 80%.

- Batch processing. Is each input processed sequentially, or can multiple inputs be in flight at once? Capacitor state during sequential processing — does it reset between samples? If it does, how is the reset done without breaking weights?
  - In our architecture now, each scaps can only hold 1 data loop. My ideas now is 1 data in, predict it, check the result, then update it at that time.
  - But I have an ideas to make each scaps have momentum sum of update value from multi batch too. Just I don't know is it good now or not, cause we have to make more circuit to keep that momemtum value.

- Inference vs training modes. Inference doesn't need backprop circuitry powered. Is there a low-power inference-only mode?
  - I think it's great ideas for inference mode. But now I think only python simulation now. Those mode is so easy to making, just like we make new intrution to control signal order.

- Failure modes. What happens when a scap drifts out of range? When the Limbic Loop gets stuck in a fixed-point attractor that's wrong?
  - This is a greatest problem too. Don't even the limbic loop stuck, I don't have even how to handle dead neural. But I have many ideas about it, don't worry. Just I don't put it yet, cause now so many place is still not stable. If I don't even able to determine my backpropagation clearly, I think design this part is so useless. 🤣🤣🤣 Now I think we have to just take a noise to jump from the loop hole (the brute force way)

**HX - The biggest framing question**
You frame this project as "biology-inspired" and lean on neural anatomy (cortex, hippocampus, commissure, ganglion). But your architecture isn't really biology. Real neurons have:

3D synaptic geometry (you have 2D, optionally 1D drift)
~10,000 synapses per neuron (you have ≤5 with DSP, 0 without)
Spiking, not graded signals (you use graded)
Calcium/vesicle/neuromodulator dynamics (you use op-amps)

---

Yeah, real neural have that. But... Eventually our technology can't handle it. Especially now that we build a analog circuit to represent it with smooth mechanism. In my sight, we shouldn't to push hard to make over engineer to copy it 1:1. We should use the analog/binary circuit strength, gradually copy it by make real circuit can scale.

Tbh, this all 1:1 machanism copy can be done easily in a normal cpu, just we build a huge of program. But it's so contray with the real thing that compute in the core. THis project is "biology-inspired", but the target is new computer arc that so efficient to compute the real biology cell mechanism.

**HX - TLDR**
This all draft is just so begining phase. As you see, at first My name is so even poor. All the word, clain, or even the thing I write isn't carefully filter. There are many place that I have to fix now. Such as the "encryption" word I use now that are very very bad. 🤣🤣🤣. So the thing I want really to said is don't be serious much. If you have more great word or ideas, you can tell me.

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
