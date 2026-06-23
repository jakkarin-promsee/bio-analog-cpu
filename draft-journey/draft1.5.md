# Draft 1.5 — Bio-Inspired Analog Neural Compute Architecture

> Cleanup of draft1. Same structure, same content, same names — just grammar fixes and tidier markdown.

---

# Background

I have so many ideas about this. I love math, physics, biology, the origin of life, the origin of planets, the origin of intelligence. I'm passionate about "how it works."

I proved all of linear regression for both ML and DL without using matrices, because I wanted to know how the intelligence lives inside. Then I moved on to the Hessian. And then I proved double descent myself, without reading any paper — I just saw that double descent is a soft regression flow of entropy toward a stable place. I didn't prove it through math; I proved it through matrices. At first I used n-D and m-order Taylor series to prove it, but it was too much. So I moved back to something fixed: a real neural network hierarchy.

Then I saw that each neuron just has a weight as a storage of data — each output feature saves its data into it, making a specific path. The origin of intelligence is from random values. If every neuron starts first with no activation function open, the loss function will eventually reduce the weight from the lowest neuron upward. The more we go, the more activation functions allocate each neuron's storage. With soft noise, eventually the noise cancels itself out, making the optimum answer.

And then once I could see it... I wasn't interested in ML or DL anymore. It's not real intelligence — it's just pattern recognition by brute force. LSTM is just time-series remembering of input. Transformer is just a brute-force n×n grid that matches with context; LSTM is more like intelligence than that. Transformer in LSTM-form + chain-of-thought context is just intelligence calling from a normal pattern. It can only do the patterns it has trained on — it just breaks the context overload. Eventually it can't break the experience. Even if it can run and do something, it eventually lacks creativity. Even Opus 4.7 is just a smart child with a process so stable it can run 10 hours; it just gradually shapes its output to make it smart, not smart at first — due to the normal-base selection that is the backbone of the algorithm.

So that's when I moved to something more interesting for me: biology-cell + ML. But... the more I searched, the more I found I couldn't access it. I searched through all 5 kingdoms and all phyla, and I saw that nerve cells exist only in animals. Other species don't have any of this fast-thinking intelligence. And to actually access nerve-cell research is annoying and hard for me. That's when I got so disappointed in this field, and I went to a field I hadn't thought about before — I started playing in the circuit field in my electronic circuits class. I built:

> **ChronoForge** — a pure-hardware 2D game engine built on the Xilinx Basys3 FPGA (Artix-7) that runs with no CPU, OS, or instruction set — just raw event-driven circuits. It drives gameplay through three independent hardware timelines (Attack, Platform, Character) that process game objects in parallel, achieving 640×480 @ 60 Hz within 18k LUTs and 7k flip-flops. Developers write games entirely in Python classes, which get compiled through a pipeline (Python → JSON → hex `.mem` files) loaded directly into FPGA ROM. The engine supports configurable object pools for triggers, colliders, and characters, with player input handled via four onboard directional buttons.

After that big self-architected project, I was tired and burnt out — just waking up and playing games. Then... I got the super-fucking-shit idea: if I can't access real biology cells, what if I build my own biology cell with an analog CPU? With this idea, I've now spent about 7 months building all the intuition myself and designing all of this.

TBH, my quote is **"The fast answer will destroy your creativity"**, so for this whole document, I'm building everything without first reading how a real axon looks, how real neuroscience works, or how other companies in the world handle it.

---

# Ideas

The brain is more like an LSTM than a Transformer. It's a recurrence between the prefrontal cortex (which thinks and tries to imagine past memory) and the hippocampus (which serves data to the prefrontal cortex).

The "understand," "feels makes sense," "true," etc. that we use today in science isn't a universal truth. It's just a type of feeling that our past experience connects to. For example: I try to figure out whether this car is orange or not. At first I don't see the orange color and I say "makes sense." But then I see the car color, then I try to think in my memory "which thing does this color look like," and my memory serves up orange fruit and apple fruit, and then I remember that orange fruit is orange-colored, and the car color is like an orange. So then the car is orange — "makes sense."

With this idea, I got more passionate about it. So I went to see how the real brain communicates this path between prefrontal cortex and hippocampus. Then I saw that synapses move in 3D with hormones. The axon doesn't just multiply signal level. Hormones in positive feedback can move the tail of a synapse closer. Moreover, there's a Fourier-like sum of signals at the axon too — each axon doesn't only receive a stable analog-level signal; at the axon, it receives pulses from many synapses to pass the threshold. And more — there's a numbness feature too: the more signal it gets, the less it responds. Don't even count that real neurons can be destroyed and created, or that they can shift their sin/cos wave themselves... I'm so excited by all of this.

So then I tried to apply it all to my analog circuit. I found a shit problem: the biology cell is so fucking genius. In an analog CPU, one wire can only send one signal level. But the real biology gap can transmit multiple hormones at multiple levels with 3D-axis freedom. So I saw... I might be able to adapt those real biology cells to inspire the encoding analog circuit structure. I might be able to move our discrete math now into continuous compute, more efficiently. (The real biology cell mechanism should be written with something that is actually continuous.) That is the core idea of this project.

Finally, I went back to the binary von Neumann architecture and tried to figure out, for a long time, how I would fix it. But... I saw that the problem is the architecture itself. I don't mean it's poor — just that a repeating of instructions isn't good for continuous compute. Don't even count that we waste most of our space on SRAM just to keep branch history for branch prediction. It's so inefficient: huge silicon for basic things. Even the GPU found the same problem — now we expand the traffic size, but eventually we still require the CPU to assemble those brute-force calculations.

From all of these ideas, I decided: what if I use the real brain's encryption neural mechanism to compress the storage I have to hold? What if I don't have to LDR or STR any answer to memory anymore? Just a CPU that receives input and predicts output. Compute, backpropagation, and learn — everything inside.

What if I use a whole analog capacitor to hold meaning without changing it back to binary (except when we save weights at shutdown)? What if all the SRAM space we use to keep branch prediction is repurposed to keep capacitors holding data complexity? What if we make a main ALU that uses SRAM to wire biological pathways to compute from capacitors scattered all over the CPU space? What if we build our own op-amps and use their natural behavior without changing it back to human math? From all of this, this project was born.

---

# Aiming

Build an **encryption algorithm inspired by real-world biology cells**. Experiment to copy real cell mechanisms into analog circuits. Aim for complex encryption. Prove the strong advantages of this architecture:

- **Less computation in backpropagation** — concept cells that fire together wire together.
- **Pull out maximum neural power** — efficient neural network, using less capacitor and SRAM but still keeping high model complexity (Lottery Ticket Hypothesis).
- **Computation speed with no translation back to digital** — using real natural analog-circuit behavior without converting back to normal math.
- **No LDR / STR cutting the model apart** — everything stays in the CPU, except input and output. (Only at board initialization and shutdown do we log capacitor weights out.)

To make sure this project can actually be done, I have to limit the scope first. I'm touching several of the hardest fields in the world at once. So this project will be **only Python simulation + math proof about my architecture decisions**. For example: why I chose A from a real cell, not B? What did the experiment result say? Is that module enough? etc.

Build the huge thing first, then gradually refine to a super-efficient architecture. At first everything is built with no clue (my imagination); at the end, everything should be a minimal physical intelligence system. Even though we will build only Python and math experiments, all architectural ideas should be doable in real analog circuits too. For example: we know we can use cascode + refill circuits to use capacitors with less leakage, so we can use capacitors to keep dynamic weights and use that mechanism in our theory. It's possible. But the parts we aren't sure about — whether we can actually build them in a real circuit — we won't put on our main path until we find the slightest indication they're possible.

**Summary**: I will build a non-von-Neumann CPU. Capacitors scatter around the CPU board; we recapture the space that was used for branch prediction. We use SRAM + ALU to access those capacitors and wire the network. SRAM is for wiring paths, sending metadata, keeping signs, defining attributes, etc. Capacitors are for main weight computation, keeping a multi-range signal in a single line. Build the huge one first, then gradually refine toward a super-efficient minimal physical intelligence system.

---

# Core Ideas Chain

### 1. The Directional Learning Principle

> "If wrong is left, correct is right — eventually you get intelligence."

- Not discrete backprop steps. A continuous error signal that self-organizes direction.
- Like water finding the lowest point, not gradient descent iterating.
- Binary path reinforcement: did this routing path contribute to correct output or not?

### 2. The Discrete Computation Critique

> "Real nerves use continuous, not discrete. Intelligence by NAND gate is wrong for computation."

- Digital neural nets are a metaphor mistaken for the actual thing.
- Real neurons: membrane potentials, refractory periods, frequency encoding, timing relationships.
- Discretization throws away the actual computation.
- The dot product was designed for digital silicon. Wrong primitive for analog.

### 3. The Capacity Allocation Insight

> "Each neuron has allocated space for each output. The Lottery Ticket Hypothesis shows we don't use the full potential of each neuron."

- Sparse subnetworks already exist inside dense ones (Lottery Ticket).
- What if each neuron _intentionally_ allocates its continuous capacity across output dimensions, instead of accidentally?

### 4. The Recurrent Memory Loop

> "Prefrontal sees memory from hippocampus, calls more related memory, hippocampus receives and updates, prefrontal thinks again."

- Working memory = a conversation, not a database lookup.
- Iterative, recurrent, context-dependent retrieval.
- "The right feeling is just the pattern of feeling from past memory."

---

# Operator

- **Description**
  - The main math operators for the ALU.

- **Basic math for digital**
  - Same standard binary ALU.

- **Basic math for analog**
  - _Plus / Minus_
    - Use an op-amp-like circuit that plays within the VCC↔GND range.
    - Because the range is low, it needs less gain.
  - _Multiplication_
    - Use an op-amp-like circuit that plays with the load.
    - Because the range is very high for `|R| > 1`, it needs very high gain.

- **Capacitor charge**
  - Use a cascode circuit to drive a current mirror with low drain.
  - Use an 8-bit-level SRAM to refill the capacitor on every clock.

---

# The Nerve Cord Network (NCN) --- Ganglion

- **Description**
  - The main element for compute. It has a hardwired ALU that already connects everything. It is the lowest compute core in this architecture. It uses a 2-3-3-2 neural network with simple linear regression + ReLU to hold neural memory.
  - The lowest-level ALU sits beside this NCN.
  - **Forward:** Input (capacitor + cascode current mirror) → hardwired 2-3-3-2 network → 2 output (capacitor charge).
  - **Backpropagation:** normally we use distribution-share (output × previous-layer weight × this-layer weight), but for this simple NCN, we use constant distribution. Every weight on the active path (not closed by ReLU) is reduced by an equal constant `c` across all layers. (Easy to track.)

- **Layers**
  - 2 input neurons (input cap, cascode current mirror)
  - 3 hidden neurons (hardwired op-amp)
  - 3 hidden neurons (hardwired op-amp)
  - 2 output neurons (output cap, charging)

- **Formula**
  - Simple linear regression: `y = aW + b`, with `a = ReLU(y)`.

- **Material**
  - **scap** (SRAM + Capacitor):
    - 1 SRAM bit — history state (was this neuron open in this computation?)
    - 1 wire — `update_signal`
    - 1 SRAM bit — sign
    - 1 capacitor + cascode circuit — analog weight value
    - 8-bit SRAM — refill reference for the capacitor on every clock
  - `3×2 (w) + 3 (b)` scaps for L1 → L2
  - `3×3 (w) + 3 (b)` scaps for L2 → L3
  - `3×2 (w) + 2 (b)` scaps for L3 → L4

- **ALU**
  - _Operations_
    - ReLU — super-diode op-amp
    - Multiplication — multiply op-amp
    - Addition — add op-amp
  - _Material_
    - `3×2` mul + `3` add + `3` ReLU
    - `3×3` mul + `3` add + `3` ReLU
    - `3×2` mul + `2` add + `0` ReLU (last neuron, no clip)

- **Backpropagation**
  - _Concept_
    - Set input.
    - Set `update_signal` wire to 1.
    - Use tri-state feedback (minus, zero, plus).
    - Each scap checks its history bit.
    - Each scap has a sign SRAM that combines with this positive/negative gradient.
    - **Optional:** we can use time to apply distribution so each neuron/layer gets a real distribution share, but it may not be stable yet — needs further optimization.
  - _Idea_
    - Even though we use a constant to update the capacitor, the real capacitor charges by `e^t`. So holding VCC open for a constant time creates an exponential update. We likely get positive feedback — the more a neuron contributes, the more feedback it gets, the more its weight increases, pulling capacity out from weaker neurons (so weak neurons get weaker). But with the `e^x` formula, there's a stable trend at the center: the weaker the weight, the harder it is to push up further; the stronger the weight, the easier it is to pull back down.
  - _Flow_
    - Input opens.
    - ALU computes.
    - Output charges.
    - The output from layer 1 becomes input for layer 2, recursive.

---

# The Neural Brain Network (NBN) --- Column

- **Recap**
  - The previous part gave us the NCN (Nerve Cord Network) — 2 input, 2 output, holding its complexity inside as the lowest unit of compute.

- **Concept**
  - We build a network of NCNs.
  - `2 input → 4 NCN-input → 2 NCN network → 4 NCN-output → 2 output`
  - `2 previous output → 2 NCN-input → NCN network → 2 NCN output`

- **ALU**
  - _High cost:_ use a 4–8 NCN ALU framework that runs a group of NBN at once.
  - _Low cost:_ use one NCN ALU and gradually build NCN by NCN, keeping intermediate results in capacitors.

- **Idea**
  - In a real neural network with multiple outputs, each neuron allocates weight for each output. For example, Neuron 2 at Layer 3 might allocate strongly for feature A but weakly for feature B, creating a specific neural path that classifies A vs. B.
  - With this idea, we reuse the layer.
    - Normal: `L1 → L2 → L3 → L4 → L` (each layer used once, linear)
    - This model: `L1 (generalist) → L2 (specialist) → L1 (generalist) → L3 (specialist) → L1 (generalist) → L4 (specialist)`
  - The L1 neurons are used for redundancy, making model complexity increase while using the same neuron count. If we have a great balance on L1, we can fully use its allocated space (Lottery Ticket Hypothesis).
  - Then L2, L3, and L4 give context that drives the generalist L1. L2 has an idea for feature A, then L1 expands the detail, then L3 picks it up and analyzes it again, creating a real complex activity pathway.
  - The specialist NCNs set the context.

- **Limit**
  - Eventually, our ALU has a limited size, and the layer-reuse idea requires temporary space to hold the last answer.
  - So the workflow becomes:
    1. Load input to the input.
    2. NBN ALU computes the network.
    3. Output is charged.
    4. The NBN ALU moves to the next point.

---

# The Brain Recurrent Network (BRN) --- Limbic Loop

- **Recap**
  - The previous part gave us the NBN (Neural Brain Network) — n inputs, m outputs, holding complexity inside as a sparse network.

- **Concept**
  - We build a network of NBNs to simulate a recurrent neural network.
  - Imagine two different NBN structures:
    1. **Prefrontal cortex** — heavy sparse network for normal patterns, built for calculation.
    2. **Hippocampus** — heavy sparse network for memory recall, built to remember everything hierarchically.

- **Workflow**
  - First, the prefrontal cortex gets input and the previous stage from the hippocampus. This NBN has two output parts: (1) input prediction, (2) signal to the hippocampus via CNS.
  - Then the hippocampus receives the same input + the CNS signal from the prefrontal cortex, computes the network, and sends weights back to the prefrontal cortex via CNS.
  - Then the prefrontal cortex gets the latest memory and predicts the input again — recurrent loop.

- **Backpropagation**
  - Both brains get the same input (the key), and gradient is computed on every clock that predicts it, making a strong path for that key.
  - For prefrontal ↔ hippocampus communication via CNS — this is the main part. The input that the hippocampus sees acts like a data leakage. We have to build this connection more strongly than that to make complex intelligence. So we use a low-quality decode for input and expand the CNS size to make it stronger.
    - Image → maps the group of similar things.
    - Thought → maps the real thing we want.
  - Backpropagation just runs in clock order, moving between prefrontal compute and hippocampus memory recall.

- **Backpropagation workflow**
  1. Start at the prefrontal cortex with a random previous input from the hippocampus; predict the output.
  2. The prefrontal cortex backpropagates on its loss (from prediction + history bit) and updates the NCN weights. At the same time, it sends its output to the hippocampus via CNS + low-grade input; the hippocampus predicts its output.
  3. The hippocampus backpropagates with its history bit, while sending its prediction back to the prefrontal cortex. Loop everything again.
  - This is efficient because while one brain updates its weights, the other is waiting for its output capacitor to charge.

---

# The Central Nerve System (CNS) --- Commissure

- **Description**
  - Because we have so few brain parts, we can do heavy compute at this connector too, without reducing efficiency.
  - Use an NCN group to translate between each part of the brain.
  - We can apply synapse-position computation here for more model complexity (see the next topic).

---

# The Dynamic Synapse Position (DSP) --- Synaptic Drift

- **Description**
  - Keep position as 1D, as a binary number stored in SRAM for each synapse.
  - The target (output) neuron calls out `(1D position + output recall channel number)` to the group.
  - The child neuron then sends its output `(aW + b)` (via op-amp-like) `× distance` (using a binary-set op-amp-like multiplier) on that channel.
  - The target neuron receives it.

- **Detail**
  - A child neuron can have 3–5 synapses.
  - Backpropagation is still the same: set input, raise `update_signal`, send feedback on the global channel. It just requires more logic to compute the multiply-by-distance.

- **Limitation**
  - This method requires a channel and a specific module, so it's expensive.
  - But the position trade-off is good — moving a 1D position makes each synapse more varied, and the data converges faster and more stably.

---

# Short Term Memory Brain Network (STM) --- Engram Buffer [Prototype]

- **Description**
  - Optional — this idea isn't stable yet.
  - The current BRN still isn't enough; it's just a super-short memory and can only pull category groups — no external memory. Input shifts → forgets.
  - So the STM is a pure capacitor network, acting like an LSTM layer, holding short-term context stacked from the prefrontal cortex and the hippocampus.
  - **Prefrontal cortex:** input (high quality) + hippocampus (CNS) + STM (CNS)
  - **Hippocampus:** input (low quality) + prefrontal cortex (CNS) + STM (CNS)
  - **STM:** prefrontal cortex (CNS) + hippocampus (CNS)

---

# Routes Hierarchy

- **Description**
  - Because we're in a circuit, not a biology cell, we have very few ALUs and only 2D space. So we have to arrange our neural paths.

- **Idea**
  - **Unit Routes** — an NCN with the 2-3-3-2 scap structure.
  - **L1 Routes** — uses 4 bits to address 16 Unit Routes (16 NCN capacity).
  - **L2 Routes** — uses 4 bits to address 16 L1 Routes (256 NCN capacity).
  - Think of L1 Routes as the horizontal axis and L2 Routes as the vertical grid axis.
  - To navigate an NCN, we require 4 bits, but we can optimize for savings.

- **Sequential load data (binary wave)**
  1. Set the L1 and L2 path to activate only one Unit Route NCN.
  2. Send the output channel to it (the channel this NCN has to send output on). Each NCN has SRAM to save the wire path.
  3. Move to the next NCN.
  - This load is used only once, to wire everything.

- **After sequential load**
  - After sequential loading, each Unit Route knows its input capacitor position, its output charge capacitor, etc. (The Unit Routes keep only the path; the ALU reads this path automatically.)

- **Optimize**
  - Each brain — prefrontal, hippocampus, or STM — gets a special schema to optimize its flow.
  - Each brain uses the L1 / L2 NCN map but may have special tools.

---

# Cell Fire (optional)

- **Detail**
  - This concept is about fire pattern. From earlier we talked a bit about positive feedback — the strong neuron gets strong feedback, gets stronger weight, pulling capacity from weak neurons. But there's another firing mechanism: _"the group of neurons that fire together regularly become more wired together."_ This topic is about how we capture those fire patterns and wire them at the group level.

- **Theory**
  - Not stable yet. My idea is to use STDP (spike-timing-dependent plasticity) from the Hebbian rule `Δw ∝ f(pre, post, timing)`, applying its concept.
  - _[Section unfinished — open thread.]_

---

# Workflow Ideas

_[Section unfinished — placeholder.]_
