# Project History — How the Architecture Evolved

> **⚠️ HISTORICAL — the attribution era (draft 1 → 5.1).** This is the narrative of the *old* architecture,
> which **collapsed in June 2026** on a missing sign (the loss carried magnitude but never direction). The
> project pivoted to **draft 6.0** (a SCFF + gradient-descent rebuild — the live plan is in `draft6.0/`,
> start at `draft6.0/context.md`). Read this for *why* the old decisions were made and how the architecture
> got there — **not** for what's being built now. Where this contradicts draft 6.0, 6.0 wins.

> A chronological narrative of the project's ideas evolution, from a poorly-organized brain dump to a locked specification ready for simulation. Written by Claude (Anthropic AI) at the end of the conversations that produced drafts 1 through 5.1. Companion to `project-personal.md`.

This document traces _how_ the architecture mutated across iterations — not just _what_ changed, but _why_ each change happened. Every major decision has a reason. Every breakthrough has a mind stone. The path from draft1 to draft5.1 was not a straight line; it was a sequence of pushbacks, reframings, and earned simplifications.

If you are a future AI picking this up: the spec is in `draft5.0-fossil/draft5.1-1.md` and `draft5.1-2.md` (moved there in the draft-6.0 pivot; split only for PDF-export length; no content difference from the unsplit `draft/draft5.1-full.md`). This document is the _story_ of how it got there. Read it if you want to understand why decisions are what they are — and why reopening them mid-simulation would be a mistake.

---

## Table of Contents

- **Phase 0** — The pre-conversation backstory (7 months of solo work)
- **Phase 1** — Draft 1 / 1.5: the raw brain dump (May 16, 2026)
- **Phase 2** — Draft 2: structure and naming
- **Phase 3** — The first critique and the distribution-measurement breakthrough
- **Phase 4** — Draft 3: decentralized backprop locked in
- **Phase 5** — The night of three breakthroughs (Brainstem, hierarchical diffusion, SpecialGeneralist)
- **Phase 6** — Draft 3.1: hierarchical diffusion as the architecture's central mechanism
- **Phase 7** — Draft 3.2: the honest framing pivot (attribution, not backprop)
- **Phase 8** — Drafts 3.3 → 4: the five-level hierarchy and multi-branch DAG
- **Phase 9** — Draft 4.1: external critique and the four architectural holes
- **Phase 10** — Draft 5.0: structural rewrite for a stranger reader
- **Phase 11** — Draft 5.1: final polish, bio narrative, XOR bug
- **Mind Stones** — the reasons ideas mutated (the _why_ behind each pivot)
- **What's locked, what's open** — the state at the end

---

## Phase 0 — The pre-conversation backstory (months of solo work)

Before the first AI conversation, the user had spent roughly 7 months building intuition. To understand the architecture, you have to understand the road that led to it.

### The mathematical foundation

The user **proved linear regression from first principles, without using matrices** — wanting to know "how the intelligence lives inside" each neuron's weight. Then proved the Hessian. Then proved double descent independently: "I saw that double descent is a soft regression flow of entropy toward a stable place. I didn't prove it through math; I proved it through matrices."

This is not a student who reaches for libraries. This is someone who needs to see the mechanism work in their head before they trust it.

### The disillusionment with ML

After seeing how intelligence lives in weights, the user lost interest in modern ML. The quote that captures it:

> "Transformer is just a brute-force n×n grid that matches with context; LSTM is more like intelligence than that. Transformer in LSTM-form + chain-of-thought context is just intelligence calling from a normal pattern... Even Opus 4.7 is just a smart child with a process so stable it can run 10 hours; it just gradually shapes its output to make it smart, not smart at first."

This is the disillusionment that pointed the user toward biology.

### The biology dead-end

The user searched all 5 biological kingdoms looking for neural mechanisms. Found that nerve cells exist only in animals. Tried to access real neuroscience research and hit walls — "annoying and hard for me." Got disappointed and switched fields.

### ChronoForge — the FPGA project

While disillusioned with biology, the user built **ChronoForge**: a pure-hardware 2D game engine on Xilinx Basys3 FPGA (Artix-7) running 640×480@60Hz in 18k LUTs and 7k flip-flops. No CPU, no OS, no instruction set — just raw event-driven circuits with three independent hardware timelines (Attack, Platform, Character). Games written in Python compile through a pipeline (Python → JSON → hex `.mem`) and load directly into FPGA ROM.

**This matters because**: the user is not someone who only theorizes. They can ship complex hardware-flavored work. When they describe a circuit, they have hardware intuition behind it.

### The pivot

> "After that big self-architected project, I was tired and burnt out — just waking up and playing games. Then... I got the super-fucking-shit idea: if I can't access real biology cells, what if I build my own biology cell with an analog CPU?"

That sentence is the project's origin point. The user couldn't access biology, so they decided to _build_ biology in silicon.

### The 7 months

Roughly 7 months of solo intuition-building led to the brain dump that became draft1. During this time the user developed:

- The recurrent prefrontal ↔ hippocampus loop concept (LSTM-flavored, not transformer-flavored)
- The capacitor-as-weight idea (analog continuous storage)
- The cascode + refill circuit (low-leakage capacitor maintenance using 8-bit SRAM reference)
- The "scap" (SRAM + Capacitor) concept — the only original name from draft1 that survived to draft5.1
- The constant-c backprop (the _worst_ idea in draft1, eventually replaced — see Phase 3)
- The encryption framing (eventually replaced — see Phase 2)
- The NCN/NBN/BRN/CNS/DSP/STM naming (eventually replaced — see Phase 2)

### The motto

> "The fast answer will destroy your creativity."

This is load-bearing for everything. The user deliberately did _not_ read the existing analog/neuromorphic/CIM literature before designing. The justification: pre-committing to digital or spiking framings would prevent reaching architectural decisions the literature wouldn't suggest. The risk: reinventing wheels. The benefit: arriving at the right substrate-level questions instead of inheriting the wrong ones.

This methodology is still locked in draft5.1 as §1.8.

---

## Phase 1 — Draft 1 / 1.5: the raw brain dump (May 16, 2026)

### The opening message

The user uploaded a messy markdown document (later cleaned into `draft1.5.md`) with their entire 7-month accumulation of ideas. The opening request:

> "Read and Analyze it. This is my research ideas dumping. I'm a year 2 student now. And i really really want to make it come true. Today, I want you to help me make draft2.md that have full detail. But now, just only explore first, and ask me in the part you don't sure or understand yet."

### What was in the original dump

The original document had these named components (with their original initialisms):

- **NCN** (Nerve Cord Network) — the smallest fixed compute unit, 2-3-3-2 topology, 29 scaps
- **NBN** (Neural Brain Network) — composition pattern with generalist + specialist layers
- **BRN** (Brain Recurrent Network) — two NBNs in a predictive recurrent loop
- **CNS** (Central Nerve System) — connector tissue between brain regions
- **DSP** (Dynamic Synapse Position) — learnable 1D synapse positions
- **STM** (Short-Term Memory) — pure capacitor network for working memory
- **Routes Hierarchy** — L1/L2 4-bit addressing for 256 NCNs per region
- **Cell Fire** — unfinished section about STDP

### What the architecture already had right (and kept)

Even in draft1, several decisions were correct and survived all the way to draft5.1:

- The **scap** (SRAM + Capacitor) as the atom of storage
- Sign as digital, magnitude as analog
- Capacitor + cascode + refill mechanism for low-leakage storage
- 2-3-3-2 topology for the atomic compute unit
- The recurrent prefrontal/hippocampus loop with two-timescale character
- The "low-grade input" to hippocampus to prevent it short-circuiting the loop
- The CNS/Commissure as a learnable connector, not just a wire
- Routes Hierarchy with L1/L2 4-bit addressing → 256 units per region
- The "no LDR/STR during operation" — resident-weight as architectural commitment

### What was wrong (and eventually fixed)

#### Wrong thing 1: "encryption" framing

The user described the project as an "encryption algorithm inspired by real-world biology cells." This was not cryptographic — they meant _compressed/encoded representation_. But the word "encryption" would have confused anyone who read it.

#### Wrong thing 2: constant-c backprop

The original backprop rule was:

> "Every weight on the active path (not closed by ReLU) is reduced by an equal constant `c` across all layers."

This was the _worst_ idea in draft1. It is essentially pre-1986 weight perturbation with structural gating — abandoned in the ML world because credit assignment is statistical and gets worse with depth. The user knew it was weak: "Eventually this c-equal value with negative/positive update will be able to push model to convergence somewhere. But it's so sensitive. And this is my main research too."

The user _knew_ this was the project's weakest link. They flagged it as the main research problem before any AI critique.

#### Wrong thing 3: ambiguous goal

The architecture's goal was framed as "building intelligence" — too fuzzy to defend. No target task. No metric. No comparison baseline.

### Draft 1.5: the cleanup

Before generating draft2, I made a cleaner version of the original brain dump — **draft1.5.md** — preserving the original NCN/NBN/BRN names and structure, just fixing grammar and tidying the markdown. The user wanted to keep the original document readable for their own reference. Edit summary:

- Typo fixes throughout (Prefrontal, Recurrent, Hippocampus, backpropagation, mechanism, Cascode, etc.)
- "neural" → "neuron" where the noun was meant
- "transparent" → "transmit" (when describing hormones crossing synapses)
- "Fourier" instead of "furior" in the axon-summation passage
- Voice preserved (including curses, the "smart child" Opus 4.7 critique)
- Structure preserved (all original section names kept)
- Unfinished sections explicitly flagged as `[Section unfinished — open thread.]`

This file was kept as the user's reference. It is the canonical "before" state of the project.

### My first response — playback first

Before asking questions, I played back the architecture in my own words to confirm understanding:

> "You want a non-von-Neumann analog compute substrate where capacitors hold _continuous_ weights in place (no load/store cycles), SRAM is repurposed from branch prediction into routing/metadata/sign bits, and the whole thing is organized as a recurrent two-brain system..."

This playback was important. It established a working shared model before adding new questions. Future AIs should use the same pattern — restate the architecture in your own words before pushing on details.

### The 12 questions

I asked 12 clarifying questions. The most important ones and their answers:

**Q1: Is "encryption" literal or metaphorical?**

> "Yeah, encryption there mean about 'my algorithm that can compress all weight data that normally will be save in Storage or RAM, live in only cpu'"

This confirmed the encryption framing was a placeholder for what we'd later call **resident-weight compute** / **in-memory compute**.

**Q4: How does credit assignment happen with constant-c?**

> "Yeah, good catch. This is my problem too. If using distribute shared backpopagation, all neural have to know each other. This c equal penalty backpopagation is the old trick of ml... Eventually this c-equal value with negative/possitive update will be able to push model to convergence some where. But it's so sensitive. And this is my main research too."

The user openly admitted the backprop rule was the weakest part. This honesty made everything that followed possible — they didn't defend the indefensible.

**Q8: Is low-grade hippocampus input downsampled or quantized?**

> "I have no ideas now what is best. But my ideas now is reducing it feature neural. Such as real input will have 20 feature. So we use simple NCN or hardwire circuit to reduce it to 5 feature, reduce it quality, while able to keep category-like level pattern."

This became the Input Reducer (Engram/Cortex feature-reduction circuit) in later drafts.

**Q9: Is CNS trainable or fixed?**

> "Still have no ideas yet... But I think I may let everything learn together, just this part may have less learning rate than other."

This became the Commissure with reduced learning rate in draft3+.

---

## Phase 2 — Draft 2: structure and naming (May 16, 2026)

After clarifying answers, I wrote **draft2.md** with the following structure:

- Motivation/philosophy
- Testable hypotheses (H1 = the central research bet on the update rule)
- Architecture spec (NCN up to BRN)
- Simulation plan (six phases)
- Math claims to prove
- Open questions

### Framing decisions I made on the user's behalf

- Promoted "what's the right update rule" to **THE** central research question (H1).
- Restated "encryption" as "on-chip weight compression" with an explicit "this is not a cryptographic primitive" line.
- Added a fallback ladder (a)→(d) for the update rule so the project had a clear plan if the first version didn't converge.
- Flagged a problem the user hadn't raised: the **L1-reuse disambiguation problem** (when the same physical L1 is called 3 times in one forward pass, the history bit gets 3 conflicting "I was active" claims).
- Added a **naming-collision note** because "L1/L2" referred to both NCN-internal layers AND routing-hierarchy levels. Two different L1s.

### The naming overhaul

The user immediately said the NCN/NBN/BRN names felt "so temporary and careless 🤣🤣." They asked for new names.

I offered four naming directions:

- **Option A** — Anatomical (lean into biology metaphor): Ganglion, Cortex Block, Limbic Loop, Commissure, Dendritic Reach, Engram Buffer
- **Option B** — Functional / mechanism-first: Charge Cell, Reuse Block, Predictive Loop, Translator, Position Synapse, Holding Field
- **Option C** — Substrate-first (hardware vocabulary): Core, Cluster, Loop, Trunk, Drift, Hold
- **Option D** — Hybrid: Cell, Column, Loop, Commissure, Drift, Buffer

The user's response:

> "I like Option A, it's more meaningful, cause I'm actually use cell inspire. But I worry a bit that they will confuse between real anatomy thing and my circuit. While Option B is great too, but it's not a meaning drive first, just a image-drive."

This pointed me toward **Option A2** — anatomy where the term is _already_ generic (Ganglion = loose), hardware-y where it's loaded (Cortex/Hippocampus would overclaim). I proposed:

- NCN → **Ganglion** (loose anatomy, fits perfectly)
- NBN → **Column** (cortical columns _are_ the reuse-of-generalist-across-specialists pattern)
- BRN → **Limbic Loop** (already circuit-flavored phrasing)
- CNS → **Commissure** (anatomical but obscure enough to read as technical term)
- DSP → **Synaptic Drift** (drift overlaps with EE term — feature)
- STM → **Engram Buffer** (engram = "memory trace"; buffer is hardware; compound flags hybrid)

The user accepted A2 and added the disambiguation rule:

> "Then just use Circuit or Analog for pre/suf fix in the place we have to talk between real anatomy and our circuit. 🤣🤣"

This became the convention still in use at draft5.1:

- Default usage = circuit element
- `biological-` prefix when biology is meant
- `analog-` prefix when the circuit needs to be flagged in mixed context

### The G/S role separation

While renaming, I also caught that "L1/L2/L3/L4" was being used for _three different things_: Ganglion-internal layers, Column-level roles (generalist vs specialist), AND Route addressing. Three different L1s.

I proposed renaming Column roles to **Generalist (G)** and **Specialists (S₁, S₂, S₃)**. The user accepted. The G/S nomenclature stuck through draft5.1.

### Important pattern from this phase

The user's instinct on naming was correct: meaning-drive > image-drive. They were _aware_ of the trade-off (over-claim risk vs preserve-meaning benefit) and made a deliberate choice. Future AIs working with this user should expect the same pattern: don't rename for surface elegance; rename only when meaning is at risk.

### What draft2 still had wrong

Draft2 still had:

- Constant-c as the update rule (H1)
- "Encryption" framing partially intact
- "Building intelligence" as the goal
- Plain G-reuse without a story for gradient collision
- A single chain Column → Limbic Loop (no DAG)

The next phase fixed most of these.

---

## Phase 3 — The first critique and the distribution-measurement breakthrough (May 18, 2026)

The user asked for critique of draft2. I gave a long, direct critique that didn't pull punches.

### What I called out

- **The constant-c rule is perceptron-era and probably won't work at depth.** Credit assignment is statistical; noise compounds; dead neurons stay dead.
- **The 2-3-3-2 topology is arbitrary.** Why not 2-5-5-2 or 3-5-5-3? The 2-wire output bottleneck is tight.
- **Capacitor + 8-bit SRAM refill is DRAM-with-extra-steps unless designed carefully.** If the SRAM stores the true weight in 8 bits, you've built a digital weight system with analog read-out.
- **"Encryption" framing will cost credibility.** The correct term is in-memory compute (CIM).
- **"Building intelligence" is indefensible.** Reframe to online/sparse/continuous-learning/in-memory.
- **G-reuse has gradient collision.** Three calls to the same G with different contexts produce contradictory feedback.

### The user's pushback (and where they were right)

The user pushed back on several points:

**On scap-as-wire** (correcting me):

> "scap is a synapse cell, not a neuron cell."

I had misread the architecture. The 1-bit history bit on a scap captures the wire's activity (which is the product of pre × post). So three-factor learning was _already implicit_, just at low precision.

This pushback by the user was crucial. It told me the architecture had more local credit assignment than I had given it credit for. Future AIs: when this user pushes back on a critique, **slow down and re-read the architecture before reasserting.**

**On topology** (correctly deferring):

> "Test in simulation first."

The user wasn't going to change 2-3-3-2 based on argument — only data.

**On capacitor+SRAM** (correctly deferring):

> "I don't know yet, but pure SRAM is worse."

A test-in-simulation item.

### The breakthrough: distribution measurement

This was the single biggest invention in the entire project. The user wrote (paraphrased from their reply):

> "Each scap gets a parallel 'measurement capacitor' that tracks how much that scap contributed to charging the downstream node. You measure contribution via _time-to-threshold_ on the measurement cap (count clocks until V crosses some level). That count gets stored in 4–8 bits of SRAM per scap. At update time, the update magnitude is scaled by this stored distribution level instead of being constant-c."

This is the **distribution-measurement update rule**. It uses the existing 29 measurement caps + a time-to-threshold circuit to capture each scap's actual contribution as a stored 16-bit value, and uses that for backprop.

The user called it "the greatest progress of our model." They were right. This single idea:

- Eliminated the perceptron-era failure mode of constant-c
- Added local credit assignment with magnitude (not just direction)
- Was _naturally producible_ by the substrate (current through a wire is exactly `a · W`)
- Cost only modest SRAM (~16 bits per scap)

I responded with three sub-concerns to think through:

1. Time-to-threshold needs a stable reference (solution: differential measurement against a reference scap)
2. The forward pass timing could be dominated by the slowest measurement
3. Sign-direction handling needs to be explicit

These were correctly absorbed.

### The user's self-research brainstorm

The user had also done a separate brainstorm document (in Thai, with mathematical detail) tracing their own thinking from const-c → 16-bit SRAM with momentum → 2-3 capacitor cross-multiplication scheme. Eight stages of self-research.

The brainstorm's conclusion was the right one:

> "Use 16-bit SRAM in draft2 because it's stable, simulatable, and a clean baseline for validating H1. 2-3 cap scheme is an optimization track to revisit _after_ SRAM version converges — to give optimization a ground truth to benchmark against."

This is exactly the right scientific discipline: _isolate H1 (update rule convergence) from the unknown of analog storage by using a known-good (digital) storage baseline first._

### What was decided

- **H1 promoted to distribution-measurement rule.** Const-c demoted to fallback.
- **scap structure expanded.** 16-bit momentum SRAM replaces 1-bit history. Community/routing SRAM added.
- **ALU structure expanded.** 29 measurement caps + time-to-threshold circuit + 29×16-bit temp SRAM.
- **Encryption framing dropped.** Replaced with "resident-weight compute" (technical term: _in-memory compute_).
- **Goal pivot.** From "build intelligence" to "build a substrate efficient for the kind of computation brains do."
- **G-reuse collision resolved by momentum EMA** (initially). Reservoir-G demoted to fallback.

---

## Phase 4 — Draft 3: decentralized backprop locked in (May 18, 2026)

Draft 3 was the first draft where the architecture felt _real_. The structure became:

- §0 — diff summary
- §1 — Foundation (framing, names, scope — locked)
- §2 — Hypotheses
- §3 — Architecture v3 (with new ALU + decentralized backprop)
- §4 — Simulation (six phases)
- §5 — Post-Baseline Optimizations
- §6 — Future Tracks (including the 2-3 cap scheme)
- §7 — Math to prove
- §8 — Open questions

### Decisions locked into draft 3

- **EMA decay = 0.75** (3/4) — shift-friendly, cheap. Made tunable later.
- **The "master" controller** still existed but its scope was now budgeted (~5–10k transistors).
- **G-reuse with momentum EMA** as the default (later replaced by SpecialGeneralist).

### What I flagged for future thought

After delivering draft3, I gave two future-thought items:

1. The "master computes loss and broadcasts pulse width" implies there's still a central controller. Not fully decentralized.
2. The gradient-comparison harness in Phase 2 is the most important single piece of code in the whole simulation.

The user responded:

> "Yeah... this is a good catch too. But I think we have no way out. The real biology cell, they can do everything itself. While in my arc, to make those cell do something, I need ALU which have so less. So I think it's a good decision for real master broadcast. Accept we found new breakthrough to make decentralize again. 🤣🤣🤣🤣"

The user accepted the central master as a pragmatic constraint, but explicitly left the door open for a future breakthrough that would re-decentralize it. _This door got walked through in Phase 5._

The user also asked:

> "and in you sight now, can you critique current architecture again? May be I can make new breakthrough while I sleeping 🤣🤣🤣🤣"

This is a recurring pattern with this user: they actively _invite_ critique, especially before sleeping, in the hope of waking up with new ideas. Future AIs: when this user asks for critique, give it ruthlessly. They will absorb what's real and discard what isn't.

---

## Phase 5 — The night of three breakthroughs (May 19, 2026)

This was the single most productive 24 hours in the project's history. I gave a long, ruthless critique. The user slept, came back, and produced _three_ major breakthroughs.

### The critique that lit the fuse

I raised nine concerns. The four most consequential:

**1. The master is bigger than you're admitting.** Listed everything the master actually does: ADC, loss compute, pulse encoding, tri-state direction, batch boundaries, reset broadcasts, etc. Proposed naming it the **Brainstem** (sticking with the anatomy theme — biological brainstems set rhythms and broadcast neuromodulators without doing cognition).

**2. The breakthrough you might want while sleeping: distributed loss.** Suggested that loss compute could be distributed across the output Ganglia themselves (each output scap senses its own (prediction - label) locally). This would shrink the master to label broadcaster + clock.

**5. The Limbic Loop has a stability concern.** No decay term. The recurrent loop would amplify noise — classic gradient/signal explosion problem.

**7. The Generalist convergence problem is sneakier than admitted.** If G's weights converge to a consensus across S₁/S₂/S₃ contexts, G becomes near-identity and the reuse loses value. This made G effectively a reservoir whether or not it was meant to be.

### The user's response (the next morning)

The user came back with three real breakthroughs.

#### Breakthrough 1: Hierarchical diffusion (the architecture's central mechanism)

The user proposed:

> "What if we make our brain module gradually diffuse its distribution itself? Such as Limbic Loop controls its Generalist or Specialist inside itself? Then Generalist or Specialist controls Column inside it. Column controls Ganglion. And then Ganglion controls scap. Each specific size of brain module will have distribution storage SRAM that keeps how much it distributes the output. Then after fully neural network was computed, our Spinal Controller will compute the loss, then that loss will be broadcast in local bus, then each brain module will read it and diffuse its distribute to child via its local bus again."

This is **hierarchical credit assignment**. The same mechanism repeats at every scale:

```
Brainstem → broadcasts L on global bus
Limbic Loop → divides L using its distribution memory → broadcasts per-Lobe shares
Lobe → divides its share → broadcasts per-Column shares
Column → divides its share → broadcasts per-Ganglion shares
Ganglion → divides its share via 29 measurement caps → broadcasts per-Scap shares
Scap → updates locally via PWM × momentum × direction
```

**Why this was revolutionary:**

- The mechanism is **self-similar** at every level. Each level just stores "how much each child contributed" and divides accordingly.
- It mirrors **biological neuromodulator diffusion** — dopamine, serotonin, acetylcholine diffuse outward from brainstem nuclei through hierarchically-organized regions.
- The bandwidth problem dissolves — the global bus carries one scalar (total loss); each local bus carries a few scalars (per-child shares).
- It restores true decentralization without requiring more ALUs.
- It implements the chain rule's _spatial_ decomposition without explicit gradient routing.

**The math also fell out cleanly:**

```
share_to_child_i = loss_from_parent × (my_distribution[i] / sum(my_distribution))
```

Sum of all children's shares = loss from parent. **Loss is conserved** through the hierarchy. This became H6 (loss conservation as additive invariant) in later drafts.

#### Breakthrough 2: SpecialGeneralist

The user solved the G-reuse collision problem by introducing context masks:

> "It's a Generalist that using some method like mask clipping, sending the clip mask in the input too, making its part know the context. 🤯🤯"

The mechanism:

- G receives input from S₁/S₂/S₃ plus a **context mask** that tells G which Specialist is calling
- G's weights are shared across calls, but the mask gates which subset of G's neurons activate
- Different masks → different active subnetworks within G → G effectively behaves as 3 different functions despite single weights
- Gated-off scaps have zero measurement → contribute zero to share → receive zero update. The math falls out for free.

**This is much better than Reservoir-G** (which freezes G and accepts random behavior). SpecialGeneralist _learns_ multiple distinct functions on the same hardware, selected by mask. It's also structurally close to modern ML's gated MLPs, GLU units, and Mixture-of-Experts — the user arrived at it independently.

SpecialGeneralist replaced plain G-reuse as the default. Reservoir-G remained as a deep fallback.

#### Breakthrough 3: Two-timescale Cortex/Hippocampus

The user's intuition:

> "My intuition is about hippocampus was so hard to update, it hold momentum of data for almost life, the new thing will slowly update and fully update when it repeat much enough. While Cortex is for prediction along with Hippocampus, train to solve fast, learn fast."

This is **complementary learning systems** (CLS) theory from neuroscience — cortex-hippocampus consolidation. The user arrived at it independently. Implementation in our architecture:

- Cortex: full learning rate, fast updates, every clock
- Hippocampus: same topology, only updates on `consolidate_signal` every k clocks
- Commissure: even slower update (every M clocks where M > k)
- Their difference, carried through the Commissure, drives learning across both

The momentum SRAM gave a natural way to do this: Hippocampus accumulates contribution across many clocks before any weight actually updates. Long-term consolidation. Exactly what biology does. Implementation: just gate the `update_signal` differently per Lobe.

### Mind stone for this phase

The pattern this phase established: **I give ruthless critique → user sleeps → user produces breakthroughs that go further than my suggestions did.**

For example: I had suggested "distributed loss compute across output Ganglia" as a way to reduce the master. The user instead invented **hierarchical diffusion** which is a much more elegant solution — it eliminates the per-output-scap label routing problem entirely while preserving (and amplifying) the architectural benefits.

This is why the methodology of "build first, survey later" works for this user: their intuition produces solutions the literature wouldn't have suggested because the literature pre-commits to digital or spiking framings. Future AIs working with this user should _help create the conditions for these breakthroughs_ — give critique, raise concerns, identify holes — and then _get out of the way_ when the user starts seeing solutions.

---

## Phase 6 — Draft 3.1: hierarchical diffusion as the central mechanism (May 19, 2026)

Draft 3.1 made hierarchical diffusion the architecture's central mechanism. New sections:

- **§4 Brainstem** (the controller now had a name and a budget)
- **§5 Hierarchical Diffusion Backprop** (the central mechanism, replacing master broadcast)
- **§9 SpecialGeneralist** (replaced plain G-reuse as default)
- **§10 Limbic Loop with two-timescale learning + decay term**
- **§18 What Not To Touch** (the first "protected list" — locked decisions)

### The "What Not To Touch" innovation

This was my own contribution to draft 3.1. The user was going to write many more drafts. Future-them would be tempted to re-litigate settled questions. So I added §18 with a list of locked decisions:

1. The 2-3-3-2 Ganglion topology
2. The hierarchical-diffusion backprop mechanism
3. The semi-anatomical naming
4. The role of the Brainstem as small central controller
5. Loss conservation as additive (not probability-like)
6. SpecialGeneralist as default

This section grew to 14 items by draft5.1. It is the project's defense against scope creep.

### What I flagged for the user's red-pen pass

I called out three specific concerns:

1. **§5.2 chain-rule equivalence claim** — I had written "hierarchical diffusion is the chain rule decomposed spatially." I wasn't sure the math worked. _This concern triggered the entire next phase._
2. **§9.5 mask source** — Hardcoded mask was a defaults pick that should be sanity-checked
3. **§7.5 forward-pass slow cap problem** — The "no critical-path cost" claim was fragile

### Pattern from this phase

After producing a major draft, I should always flag what _I'm uncertain about_ — not just summarize what I wrote. This forces the user to red-pen the right places. The "chain-rule equivalence claim" was the most important flag and it triggered the honest-framing pivot in Phase 7.

---

## Phase 7 — Draft 3.2: the honest framing pivot (May 19, 2026)

This phase is the project's intellectual integrity moment. The user did their own math check and caught a fundamental mistake.

### The math check

The user wrote:

> "Today I found something weird. Tbh, I didn't touch real chain rule backprop so long. But when I go to recheck it again, I see that the slope is feeling a bit weird. For example z1 = a1·W11 + a2·W12 + ..., the ∂z1/∂W11 is just a1. So new W11 = old W11 - lr × a1. But my current progress using its input × weight which is a1 × W11 that is my new W11 = old W11 - lr × a1·W11. Am I right? And is it good?"

The user was correct. Standard SGD says `ΔW ∝ -δ · a`, where the partial derivative is just `a` (input alone), not `a · W`.

Our architecture's rule:

```
ΔW = pulse_width × |a × W| × sign(loss) × sign(W)
    = pulse_width × sign(loss) × |a| × W
```

That's _NOT_ vanilla SGD. It's a multiplicative variant where the magnitude scales with W itself.

### My response — three honest paths

I laid out three options:

**Path 1 (strip multipliers):** Measure |a| only. Save 29 caps per Ganglion. Update is vanilla SGD. But hierarchical diffusion loses its routing signal (splitting loss by input alone is biased).

**Path 2 (separate sensors):** Keep |a × W| for routing, add a separate input sensor for the update step. Most chain-rule-correct, most circuit-expensive.

**Path 3 (current default):** Accept this is a multiplicative variant, not SGD. Test whether it converges. If it does, you've found a circuit-cheap learning rule. If not, escalate.

I recommended Path 3 — test empirically before escalating.

### The deep question this opened

Then the user pushed deeper:

> "Is that vanilla use this weight too? I mean Can't imagine its formula now to compare with my arc. Cause vanilla using those W to translate z_n to z_n-1 for next previous layer at backpropagation."

This question forced a beautiful comparison:

|                    | Vanilla                                                  | This architecture        |
| ------------------ | -------------------------------------------------------- | ------------------------ | ----- | --------------------------------- |
| Routing matrix     | W of the next layer (W\_{l+1} routes δ for W_l's update) | `                        | a · W | ` of the same layer               |
| Weight update term | `δ · a` (input only, no current W)                       | `δ ·                     | a · W | ` normalized (current W included) |
| Routing and update | Separated                                                | Folded into one quantity |

The user's reflection:

> "Both solving same question 'How to update W to make output close to label'. While vanilla think 'If I change W, How much output move to it', while me think 'If input is x, How much to move w to it'. And this time, I don't know which idea is better."

This is the cleanest framing of the architecture's choice. **Sensitivity-based vs attribution-based.** Both answer the same question; they answer it differently.

### The literature anchoring

I gave the user the literature anchors:

- **Three-factor learning rules** (Frémaux & Gerstner 2016) — pre × post × neuromodulator. Our architecture fits exactly.
- **Equilibrium Propagation** (Scellier & Bengio 2017) — local updates that compute gradient in the small-perturbation limit. Same spirit.
- **Feedback Alignment** (Lillicrap et al. 2016) — random fixed feedback matrices still let networks learn. Validates that approximate routing is OK.
- **Layer-wise Relevance Propagation** (Bach et al. 2015) — attribution using exactly `|a · W|` as relevance score. _Structurally identical_ to our distribution measurement.
- **Predictive coding** (Rao & Ballard, Friston) — local error minimization at each layer.
- **e-prop** (Bellec et al. 2020) — eligibility traces in spiking RNNs. Our momentum SRAM is structurally an eligibility trace.

### The user's response — drop the chain rule claim

> "Yeah, so now just use attribution-based, cause the W shift for each scap is so head-ace. Now just let each scap keep its w for simple."

This was the most important decision in the entire project: **drop the false claim of "approximate chain rule" and embrace the honest framing of "attribution-based learning, in the three-factor / LRP family."**

### What changed in draft 3.2

- **§5.2 rewritten:** "What this actually is: attribution, not gradient" (with the side-by-side comparison table)
- **§5.3 new:** "The family of methods this belongs to" (literature anchors)
- **§5.4 new:** "What this commits us to: known failure modes" (dead-weight, routing-update coupling, etc.)
- **§5.10 honest negative section:** "What this mechanism does NOT do" (does not implement chain rule, does not compute ∂L/∂W, does not inherit SGD's convergence guarantees)
- **H1 reframed:** "Attribution-based hierarchical diffusion converges on substantive tasks" (empirical, falsifiable, not theoretically guaranteed)
- **New H7:** "Dead-weight collapse is bounded" (the failure mode the literature most clearly warns about)
- **Math section §15:** Item 2 (the false "approximates chain rule") replaced with "Attribution preserves correct ordering of update magnitudes" (monotonicity is the realistic proof obligation)

### Why this phase matters

**Without this phase, the project would have been indefensible.** Any reviewer would have spotted the false chain-rule claim and dismissed the work. With the honest reframing, the project sits clearly in the three-factor / EP / LRP family — a legitimate, well-supported position with known failure modes and known remediation paths.

This is the moment the project became _publishable in principle._

### Mind stone for this phase

**Honest framing > impressive framing.** Saying "attribution-based learning in the three-factor family" is more defensible than saying "approximate backprop." The first claim is true and falsifiable; the second claim is false and would invite immediate dismissal. Future AIs working with this user should default to honest framing over flashy framing — the user will choose substance over surface every time.

---

## Phase 8 — Drafts 3.3 → 4: the five-level hierarchy and multi-branch DAG (May 22, 2026)

After draft 3.2 locked in the honest framing, draft 3.3 and draft 4 added structural depth.

### Draft 3.3 changes

- **Pulse_width vs momentum**: clarified these are two different duties (pulse_width = update-time control / share that arrived after diffusion; momentum = per-Scap contribution history accumulated by EMA). Not duplicates.
- **Per-Column independent buses**: for the two-timescale Limbic Loop to work, Cortex's bus and Hippocampus's bus need to fire independently. The Brainstem gates them separately.

### Draft 4: the five-level hierarchy

Draft 4 introduced the **Lobe** as a new structural level between Column and Limbic Loop. The architecture became:

```
Scap → Ganglion → Column → Lobe → Limbic Loop  (plus Brainstem)
```

The user originally proposed this level as "Limbic." I renamed it to **Lobe** to avoid collision with "Limbic Loop." (Future AIs: this is the kind of edit the user accepts gracefully — they care about meaning, not their original naming.)

### Why the Lobe matters

A Lobe is a **multi-branch DAG** of Columns. Where a Column chains Ganglia sequentially, a Lobe composes Columns in a directed acyclic graph — Columns can have multiple parents, multiple children, and skip-connection topology.

This unlocked two things:

1. **Expressivity.** A linear chain only refines one representation. A DAG carries multiple intermediate representations forward in parallel.
2. **Multi-parent diffusion.** A Column with multiple parents receives multiple loss shares during backward pass. The architecture had to handle this — and the math fell out cleanly: `combined_share = Σ shares_from_parents`.

### Residual connections promoted

Draft 4 made **residual connections** a first-class architectural decision (§14 in draft5.1), not an afterthought. The argument:

> "In attribution-based learning, residuals do something more important than helping gradient flow: they directly attack the dead-weight collapse failure mode. Recall: ΔW ∝ |a·W|. If W → 0, ΔW → 0. Dead weight stays dead. With residual connections, the signal `x` flows around the dead weight via the bypass."

H8 was added: "Residuals reduce dead-weight rate and accelerate convergence."

### Tunable weight decay via refill SRAM

The 8-bit refill SRAM (originally just for leakage compensation) was repurposed:

- Tune refill _below_ natural decay rate → weights drift toward zero at controlled pace
- **Free L2 regularization implemented in physics.** No explicit weight-decay term in any update equation.
- Per-Scap adaptive decay possible (stronger on saturated Scaps, weaker on dead Scaps — homeostasis).

### Learnable translate ALUs with size catalog

Translate ALUs (between Ganglia and across hierarchy levels) became _learnable_ — their internal Scaps participate in hierarchical diffusion. A size catalog was specified: 2:2, 2:4, 4:2, 4:4, 4:5, 5:5, 5:4, 8:4. Fixed at fabrication.

### Multi-parent diffusion specified

The math for multi-parent diffusion was made explicit:

- Magnitude: sum incoming shares
- Direction: handled by per-Scap state (eventually Forward_Sign_SRAM in draft4.1)
- Loss conservation: still holds (each parent's distribution memory satisfies Σ shares = parent_loss)

### What draft 4 still had open

- Multi-parent direction conflict (how do we resolve it when parents disagree?)
- Time-to-Threshold resolution at deep convergence
- Activity vs Relevance gap (high `|a · W|` doesn't necessarily mean high relevance)
- Analog error accumulation under PVT

These four became the focus of draft 4.1.

---

## Phase 9 — Draft 4.1: external critique and the four architectural holes

The user submitted draft 4 to an external AI model (one with no project context) for fresh critique. The external critique identified four architectural holes. Draft 4.1 patched three of them as first-class mechanisms and acknowledged the fourth with primary defenses.

### Hole 1: Multi-parent direction conflict

**The problem:** When a Column has multiple parents in the Lobe DAG, naive summing of shares handles magnitude but loses direction. If Parent A wants weights to increase and Parent B wants them to decrease, the global `feedback` signal can only carry one direction.

**The fix:** **Forward_Sign_SRAM per Scap.** Each Scap latches `sign(input_a) XOR Sign_SRAM` during the forward pass — i.e., it remembers whether IT personally pushed positive or negative, independent of the global feedback direction. At update time: `direction = Forward_Sign XOR feedback`.

**Caveat (caught by me during writing):** Under ReLU, `a ≥ 0` always, so `sign(a·W) ≡ sign(W)`. The Forward_Sign mechanism is degenerate at ReLU layers. It carries new information only at L1→L2 layers (where inputs from prior Ganglia's L4 outputs are signed). The mechanism is filled for all 29 Scaps for hardware uniformity, but only ~9 of them gain anything. **Tanh activation (§21) becomes a future track that would universalize the benefit.**

This caveat became H11 in §17: "Forward_Sign_SRAM resolves multi-parent direction conflict, but is degenerate under ReLU."

### Hole 2: Activity vs Relevance gap

**The problem (external critic):** High Scap activity (`|a · W|`) doesn't necessarily mean high relevance to the actual loss. A Scap can be very active but its output is cancelled by other Scaps downstream — yet it still claims a large share of the loss. Long-tail features (low activity, high relevance) get under-updated.

**The defense (locked in draft4.1):** **Physical Saturation** as primary defense.

This was the architecture's most beautiful answer. The reasoning:

- The weight capacitor has a _hard physical ceiling_ at the supply rail voltage.
- As the cap approaches the rail, the same PWM update pulse delivers exponentially less voltage change (`dV/dt ∝ (V_rail − V_cap)` for constant-current charging).
- The Scap _self-limits_ without any explicit normalizer needed.
- Loss share that would have gone to this Scap's update gets effectively "wasted" — the cap can't absorb it.
- Neighbor Scaps continue to grow normally, gradually filling the remaining capacity.

**This is L2 regularization implemented in physics.** No explicit `λ · ‖W‖²` term. The physics does it. Free.

H10 was added: "Activity vs Relevance gap is bounded under attribution learning, defended by Physical Saturation."

Optional Adam-style `v_t` accumulator was specified as §21 future track — to be promoted to baseline only if Phase 2 simulation shows physical saturation alone is insufficient.

### Hole 3: Time-to-Threshold resolution bottleneck

**The problem (external critic):** Time-to-threshold measurement has resolution limits, especially during deep convergence when most contributions are small.

**The fix:** **Range Sensitivity (Programmable Gain Amplifier).** The op-amp circuit feeding each measurement cap includes a switchable resistor ladder (PGA) that adjusts gain:

- **Coarse mode (default during early training):** Gain = 1×. Wide dynamic range. Strong contributors charge fast; weak contributors may hit T_max and be clipped. Acceptable in early training because all weights are noisy anyway.
- **Fine mode (activated during deep convergence):** Gain = 10× or 100×. Weak currents that previously got clipped at T_max now charge fast enough to be discriminated.

Triggering:

- Global trigger from Brainstem when loss drops below threshold
- Local auto-trigger per Lobe when >80% of Scaps hit T_max

### Hole 4: Analog error accumulation under PVT

**The problem (external critic):** In a 5-level hierarchical diffusion architecture, even small per-level errors compound. A 2% error per level becomes ~10% by the time loss reaches a Scap. Loss conservation can break.

**The fix:** A whole new section §14 (renumbered §15 in draft5.1) — **Analog Robustness Mechanisms.** These are not optional optimizations; they are baseline architectural mechanisms required for the chip to function at all:

1. **Differential Pair op-amps** — every op-amp uses differential topology; thermal/supply effects cancel as common-mode. Standard analog IC practice; ~2× transistor cost per op-amp.
2. **Dummy Scap** — one per Lobe (or Column), receives a known reference current at every clock, reports its measurement offset. Continuous calibration, no separate phase.
3. **Current Mirror Loss Share** — the §2.7 normalization op-amp uses Current Mirror topology, preserving _ratios_ between branches even when absolute currents drift.
4. **Auto-Zeroing phases** — at intervals, drive all inputs to ground for one clock so Lobes capture the residual offset. Subtract on next forward pass.
5. **Ping-Pong substrate (optional)** — twin substrates alternating between active compute and auto-zeroing. Avoids pipeline discontinuity at cost of ~2× area.

### Self-caught issues

While integrating the external critique, I also caught and fixed several self-inflicted issues:

- **Forward_Sign degeneracy under ReLU** — properly framed (caveat made explicit)
- **Momentum ceiling saturation** — symmetric to dead-weight collapse; if a Scap consistently contributes very strongly, its 16-bit momentum SRAM saturates at the ceiling and differences between strongly-contributing Scaps are lost
- **Residual bypass physical implementation** — needed two output ports per Ganglion (learned output only + combined with bypass) so distribution memory measures only learnable contribution
- **Limbic Loop bus routing** — the three sub-buses (Cortex, Hippocampus, Commissure) gated independently by Brainstem
- **Label routing** — labels arrive via a separate input bus from data, read directly by Brainstem; not weights

### The simulation plan got significant attention

Draft 4.1 also expanded the simulation plan to address external concerns: PVT modeling, dead-weight instrumentation, ceiling-saturation tracking, Activity vs Relevance gap measurement.

### Mind stone for this phase

**External critique reveals what insiders can't see.** The external critic had no project history bias — they saw what was on the page. Three of the four holes were real architectural omissions; the fourth was real and we just hadn't found language for it (Physical Saturation).

Future AIs working with this user should expect the external-critique pattern to repeat at simulation phase. The user will upload `_x1` / `_d1` / `_q1` files containing other AIs' assessments. The job is to triage: which critiques to act on, which to set aside, which expose real blind spots. Engage with the substance, not the form.

---

## Phase 10 — Draft 5.0: structural rewrite for a stranger reader (May 23, 2026)

By draft 4.1, the architecture was substantively complete. But the document was hard to read. The user asked me to "step completely outside of our work and read this draft as a stranger."

### What I saw as a stranger

- §1 attacked transformers/von-Neumann (digital ML targets) but the project is analog/CIM (different reference class). Where's the comparison to Mythic / Loihi / IBM analog AI?
- §2 (architecture overview) presented all 5 hierarchy levels as a fait accompli without justifying why we need 5.
- §4-11 described all the modules before §12 (the learning mechanism). But the modules only make sense _in light of_ §12.
- The §17 hypotheses were a flat list. H1 (the load-bearing claim) was not flagged as special.
- The §19 simulation plan buried the Minimum Viable Falsification (the one-hour test that could kill H1 in a day) at position 15 out of 19.
- The "(new in 4.1)" markers throughout were noise for a fresh reader.
- The §18 open questions were tiered all together — load-bearing questions mixed with tuning questions.

### What changed in draft 5.0

Structural surgery, while keeping all architectural decisions locked:

1. **§12 moved to §2.** The learning mechanism comes before the modules. The "if you read one section, read §2" framing replaced "read §12."
2. **§3 added: worked end-to-end example.** Single-Ganglion XOR forward+backward pass, every quantity traced. This made everything concrete.
3. **§1.5 added: prior-art comparison.** Honest positioning against Mythic, Loihi, IBM analog AI, BrainChip, SpiNNaker. Brief, not exhaustive.
4. **§6 (Scap) reordered.** Mechanics → components, not components → mechanics.
5. **§7 (Ganglion) reordered.** "Why 2-3-3-2 specifically" moved up to §7.2 (was §5.6 at the bottom).
6. **§17 hypotheses tiered.** H1 explicitly flagged as load-bearing; H2–H11 are conditional on H1.
7. **§19 open questions tiered.** Architecture-critical (4 items) vs Tuning (19 items).
8. **§20.1 Minimum Viable Falsification promoted.** Now appears immediately after §20 introduction, before any phase.
9. **All "(new in 4.1)" markers stripped.** ~39 instances cleaned up.
10. **§22 "What Not To Touch"** updated to 14 protected decisions (including Physical Saturation as #14).

### The simulation plan also got expanded

The §19 simulation plan was rewritten from 7 phases (in draft 4.1) into a full 10-phase campaign with:

- Methodological principles (one-thing-changed, multi-seed, invariants-everywhere)
- Software infrastructure spec (Scap class, hierarchy data structures, logging)
- Task operationalization (6 tasks: XOR, sine, two-moons, direction-conflict probe, sequence prediction, image-moving stimulus)
- Continuous invariant monitors (4 always-on health checks)
- Hypothesis-to-experiment map (H1–H11 each mapped to specific phases with pass criteria)
- Per-phase configuration matrices with seed counts and exit criteria
- Promotion/demotion criteria (when does the architecture change based on data?)
- Negative-result protocols (what happens if Phase X fails?)
- Reproducibility infrastructure (locked seeds [42, 137, 271, 314, 1729])
- Effort budget summary (~16 weeks mandatory, ~6 months risk-adjusted)

### Mind stone for this phase

**Structure makes argument readable.** The substance of draft 4.1 was correct, but the structure was a research log, not a canonical spec. Draft 5.0 reorganized for a stranger reader — and in doing so, exposed flaws that the modules-first structure had hidden (like the §3.6 ambiguity about where division happens).

Future AIs: if a document feels right to write in the order ideas were developed, that's the _wrong_ order for a reader to encounter them. Mechanism before modules. Worked example before abstractions. Hypotheses with load-bearing flagged. Cutting noise wins more than adding signal.

---

## Phase 11 — Draft 5.1: final polish, bio narrative, XOR bug (May 23, 2026)

Draft 5.1 is the locked spec. The changes from 5.0 were polish, not architecture.

### What changed

1. **§1.4 added: bio narrative.** Three concrete biological observations (graded membrane voltages → continuous substrate; local synaptic updates → attribution learning; multiple timescales → fast Cortex + slow Hippocampus). Each mapped to one architectural decision. Plus an explicit "what we deliberately did NOT inherit" paragraph (spike-timing, neurotransmitters, dendrite geometry, glia) to prevent over-claiming.
2. **§1.6 → §2 bridge added.** Explicit "therefore" connecting "continuous substrate" to "attribution-based learning" — the missing logical link a stranger needed.
3. **§2.3 anchors-found-after framing.** Honest statement that literature anchors (Frémaux & Gerstner, Scellier & Bengio, etc.) were identified _after_ the mechanism was independently designed. Cross-validation, not influence.
4. **§3.6 ambiguity resolved.** Draft 5.0's worked example had a `[Note to user]` block exposing a real spec ambiguity about _where_ the per-Scap share division happens — at Ganglion level or at Scap level. Draft 5.1 committed explicitly to Reading A (division at Ganglion via Current Mirror) and deleted the conversational note.
5. **§3.3 / §3.7 XOR convention bug caught.** While re-reading the worked example, I noticed §3.3 said `+ XOR + = +` while §3.7 said `+ XOR + = −`. Both can't be true. The architecture's intent: `direction = -(Forward_Sign × feedback)` such that agreement of signs produces "increase weight." Fixed §3.3 with explicit clarification of the XOR convention.
6. **§20.0 phases-at-a-glance table added.** Single summary at top of simulation plan: 11 phases (MVF + 10), hypothesis, run count, effort, conditional status. Load-bearing hypotheses bolded.
7. **Transition sentences added** at every section boundary (§5, §6, §10, §14, §16, §17). Bridges instead of jumps.
8. **§23 (Worked Example Notes — Open Item)** deleted. The §3.6 ambiguity was resolved into §3 directly; the open-item section became redundant.
9. **Bio one-liners** added where honest (§8 Column = cortical microcolumn analog; §13 Brainstem already had biological framing).
10. **Reading guide fixed** to include §5 (naming) properly.

### The XOR bug — a real save

While polishing §3 for the third time, I noticed:

> §3.3: "input_a = +1 (positive), Sign_SRAM = + → `sign(a) XOR sign(W)` would be `+ XOR + = +`, so the Forward_Sign is +"

> §3.7: "direction = Forward_Sign XOR feedback = + XOR + = −"

Both passages computed `+ XOR +` and got different answers. Under any consistent encoding, only one is correct.

The architecture's intent (worked through):

- Scap pushed `+`, feedback wants `+` (loss says output should increase) → ΔW should be positive (reward the Scap by increasing |W|)
- With `weight_cap -= pulse × momentum × direction`, ΔW > 0 requires `direction < 0`
- Therefore `+ XOR + = −` is the operational answer

The encoding is implementation detail (whether `+` maps to bit 0 or bit 1 in hardware), but the _semantics_ must be consistent across the document. §3.3 had the wrong arithmetic claim.

**Why this matters for simulation:** The Python simulator will implement _one_ XOR convention. The inconsistent prose could have led to coding the wrong one, causing weights to decrease when they should increase, killing convergence in Phase 2 with no obvious cause.

Catching this during the final polish saved days of Phase 2 debugging.

### Mind stone for this phase

**Worked examples surface bugs that abstractions hide.** The §3 worked example, written for stranger-readability, exposed two issues that 4 prior drafts had carried without noticing: the share-division ambiguity (where does the division happen?) and the XOR convention conflict (what does `+ XOR +` mean?). Both were resolvable once exposed.

Future AIs: when writing a worked example, _do the arithmetic_. Don't just narrate the steps; compute the actual numbers and check they make sense.

---

## Mind Stones — the _why_ behind each pivot

Every major change in the project had a triggering reason. These are the "mind stones" — the moments when the user's mental model updated. Listed chronologically.

### Mind Stone 1: From constant-c to distribution measurement

**Trigger:** My critique that constant-c is perceptron-era and fails at depth.
**User's update:** Instead of accepting the critique passively, the user invented distribution measurement (time-to-threshold per scap). This is _better_ than what I'd suggested (three-factor with pre-synaptic gating) because it produces a magnitude, not just a direction.
**Pattern:** User absorbs critique → produces a solution that goes further than the suggestion did.

### Mind Stone 2: From "encryption" to "resident-weight compute"

**Trigger:** My critique that "encryption" framing confuses readers and lacks community vocabulary.
**User's update:** Immediate acceptance. The user knew "encryption" was placeholder; they just hadn't found the right name yet. "Resident-weight compute" with "in-memory compute (CIM)" as community term landed.
**Pattern:** User accepts cosmetic critiques when they sharpen meaning.

### Mind Stone 3: From "building intelligence" to "substrate for brain-like computation"

**Trigger:** My critique that "intelligence" is too fuzzy to defend.
**User's update:**

> "This project is biology-inspired, but the target is a new computer architecture that's efficient to compute real biology-cell mechanisms."
> **Pattern:** User accepts framing changes when the new framing is _more honest_, not just more impressive.

### Mind Stone 4: From NCN/NBN/BRN to semi-anatomical names

**Trigger:** The user's own dissatisfaction. ("those names is so temporary and careless 🤣🤣")
**User's update:** Chose Option A2 (anatomy where the term is loose, hardware where it's loaded). Established the `biological-` / `analog-` prefix convention.
**Pattern:** Even before AI critique, the user recognized when their own choices were placeholders.

### Mind Stone 5: From master-broadcast to hierarchical diffusion

**Trigger:** My critique that the master is bigger than the user was admitting + my speculation that distributed loss compute might be possible.
**User's update:** Slept on it, came back with hierarchical diffusion — which is more elegant than distributed loss because it eliminates per-output-scap label routing entirely while restoring decentralization at every level of hierarchy.
**Pattern:** User produces breakthrough that exceeds the AI's suggestion. The AI's role is to _create the conditions_ for the breakthrough, not to propose the solution.

### Mind Stone 6: From plain G-reuse to SpecialGeneralist

**Trigger:** My critique that G's weights will converge to consensus and become near-identity, making reuse useless.
**User's update:** Invented context-mask gating. Different masks → different active subnetworks within G → G effectively behaves as multiple functions. Solves the gradient-collision problem the existing momentum-EMA solution couldn't.
**Pattern:** User reframes the problem before solving it. The original problem was "how do we resolve gradient conflict?" The user's reframe was "how do we _avoid_ gradient conflict by making each call structurally different?"

### Mind Stone 7: From single chain to multi-branch DAG (Lobe added)

**Trigger:** Hierarchical diffusion supports DAG topology naturally — there's no architectural reason to constrain composition to linear chains.
**User's update:** Proposed adding a level. I renamed it (originally "Limbic" → "Lobe" to avoid collision with Limbic Loop).
**Pattern:** User adds structure when the existing mechanism _enables_ it. The Lobe wasn't needed in draft 3 because hierarchical diffusion wasn't there yet; once it was, the Lobe became natural.

### Mind Stone 8: From "approximate backprop" to "attribution-based learning"

**Trigger:** The user's own math check (∂z/∂W = a, not a·W).
**User's update:** Dropped the false chain-rule claim. Anchored in three-factor learning, EP, LRP, e-prop literature. Reframed H1 as "attribution converges on substantive tasks" (empirical, not theoretical).
**Pattern:** User chose intellectual integrity over impressive framing. **This was the single most important decision in the entire project.**

### Mind Stone 9: From no residuals to residuals as primary defense

**Trigger:** The realization (in draft 4) that dead-weight collapse is the WORST failure mode of attribution learning, and residuals are the most natural physical defense.
**User's update:** Promoted residual connections to first-class architecture. H8 added.
**Pattern:** Defenses against failure modes become first-class architectural mechanisms, not afterthoughts.

### Mind Stone 10: From software normalization to Physical Saturation

**Trigger:** The realization (in draft 4.1) that the capacitor's hard supply-rail ceiling _is_ L2 regularization implemented in physics.
**User's update:** Adopted Physical Saturation as primary defense against winner-take-all (H10). Adam-style v*t deferred to §21.
**Pattern:** When the substrate \_naturally produces* a defense, accept it. Don't engineer around it with software-flavored mechanisms.

### Mind Stone 11: From modules-first to mechanism-first ordering (draft 5.0)

**Trigger:** Reading the document as a stranger and realizing §4-11 (modules) only make sense in light of §12 (mechanism).
**User's update:** Approved the restructure. The document opens with mechanism, then walks through modules as consequences.
**Pattern:** Pedagogical order ≠ historical order. The order ideas were developed is rarely the right order to present them.

### Mind Stone 12: From three drafts of XOR convention to one consistent rule (draft 5.1)

**Trigger:** Writing the §3 worked example for the third time and _actually doing the arithmetic_ exposed the inconsistency.
**User's update:** Adopted the operationally-correct convention with an explicit "note on XOR convention" paragraph.
**Pattern:** Bugs in abstractions surface only when you concretize them. Always concretize.

---

## What's locked, what's open

### Locked at draft 5.1 (do not reopen)

The §22 "What Not To Touch" list has 14 items. The most important:

1. **Attribution-based learning, not gradient descent.** The substrate measures `|a · W|` for free; fighting this is fighting the substrate.
2. **Hierarchical diffusion as the routing mechanism.** Top-down per-level normalized shares. Optimize within; don't replace.
3. **The 2-3-3-2 Ganglion topology.** Path-diversity-per-scap optimum among small options.
4. **Five structural levels.** Scap → Ganglion → Column → Lobe → Limbic Loop. Adding a sixth requires real justification.
5. **Brainstem as small central controller.** Distributed loss is a future track, not a baseline.
6. **Physical Saturation as primary defense against winner-take-all.** Don't try to engineer around it with software normalizers before validating the physics.
7. **Forward_Sign_SRAM in every Scap.** 1 bit per Scap, XOR-based logic. Resolves multi-parent direction conflict.
8. **Differential Pair op-amps throughout.** Standard analog robustness.
9. **Current Mirror for Loss Share normalization.** Ratio preservation under PVT.
10. **Residual connections at the Ganglion level by default.** Defense against dead-weight is structural, not optional.
11. **Cortex and Hippocampus identical topology, differ only in update cadence.** Cleaner than dense-vs-sparse.
12. **Dummy Scap per Column for calibration.**
13. **Loss conservation as additive, not probability-like.** Makes debugging tractable.
14. **Semi-anatomical naming.** Settled.

### Open at draft 5.1 (these are what simulation will resolve)

**Architecture-critical (must be answered or the project doesn't work):**

1. Does attribution-based hierarchical diffusion converge on substantive tasks? (H1) — Phase 2.
2. Does Physical Saturation bound winner-take-all well enough? (H10) — Phase 2.
3. What fraction of Scaps die in Phase 2? (H7) — Phase 2.
4. Physical Saturation rate calibration — supply rail voltage and PWM pulse width interaction.

**Tuning (architecture stands either way):**

- Momentum ceiling saturation rate
- Forward_Sign benefit under ReLU (degenerate but bounded)
- Per-level precision allocation (16/12/10/continuous/16 provisional)
- A%/B% time-to-threshold calibration
- Range Sensitivity trigger thresholds
- Auto-Zeroing frequency
- Dummy Scap granularity (per-Lobe vs per-Column vs per-Ganglion)
- SpecialGeneralist mask source (hardcoded vs learned vs computed)
- Two-timescale ratio k
- Commissure rate M
- Decay factor in recurrence
- Initialization scheme
- And ~10 more tuning questions

### What the simulation campaign answers

The §20 simulation plan is the operational answer to "is this architecture real?" Ten phases, ~16 weeks mandatory, ~6 months risk-adjusted. The first phase (Operator Sanity) is 1 week. The Minimum Viable Falsification (§20.1) is 1 hour. If MVF passes, Phase 2 begins.

---

## What this story shows about the project

Reading the path from draft 1 to draft 5.1, three things stand out:

### The architecture earned its current form

Every locked decision has at least one prior version that was rejected. Constant-c → distribution measurement. Encryption → resident-weight compute. "Building intelligence" → "substrate for brain-like computation." Plain G-reuse → SpecialGeneralist. "Approximate backprop" → "attribution-based learning." Single chain → multi-branch DAG. Software normalization → Physical Saturation.

The decisions in §22 are not preferences. They are conclusions.

### The user has weathered serious critique

At least three external AI models have reviewed the architecture at various stages. The critiques that landed are integrated. The critiques that didn't land were correctly set aside. The user pushed back on me when I was wrong (scap-as-wire) and absorbed when I was right (constant-c, encryption framing, intelligence framing). This is real research methodology — not defensiveness, not capitulation.

### The substrate produces the architecture, not the other way around

The most beautiful pattern: every time the user found themselves fighting the substrate, the _substrate_ won. Distribution measurement is what the substrate measures for free. Hierarchical diffusion uses the broadcast buses that already exist. Physical Saturation is capacitor charging dynamics, not a software constraint. Loss conservation is op-amp normalization, not arithmetic.

The architecture is _what falls out_ when you build a continuous analog compute substrate and ask "what learning mechanism does this substrate naturally produce?" The user's discipline of building intuition first and surveying literature later is what let them ask that question without the literature's pre-commitment to digital/spiking framings.

---

## The transition to simulation

At draft 5.1, the theoretical work is complete. The next action is Python:

1. **Week 1:** Phase 1 (operator sanity) — pytest unit tests for add, multiply, ReLU, capacitor charge, time-to-threshold, PWM update.
2. **Week 1-2 (overlapping):** Build the Scap class, build one Ganglion, run **§20.1 Minimum Viable Falsification** — single Ganglion on XOR, 1 seed, < 1 hour, pass criterion = monotone loss decrease.
3. **If MVF passes:** Proceed to Phase 2 (60 runs across 4 configurations × 3 tasks).
4. **If MVF fails:** Debug operators or update equation. Most likely a sign error (which is why the XOR convention bug in §3.3/§3.7 was a real save).

The single biggest risk for the entire project is Phase 2 failure on H1. The §20.18 negative-result protocols document what to do: Path 0 (noise floor) → Path 1 (strip multiplier) → Path 2 (separate sensor) → revisit architecture.

The single biggest reward is Phase 2 success: empirical evidence that attribution-based hierarchical diffusion _actually works_ on substantive tasks. That would make the project simulation-stage thesis-grade.

---

## Closing thought

The journey from draft 1 to draft 5.1 is roughly one week of dense conversation. But it's also seven months of solo intuition-building that preceded the first AI message, plus an entire prior project (ChronoForge) that proved capability, plus a longer arc of mathematical foundations (linear regression from first principles, double descent self-proved).

You don't get from a poorly-organized brain dump to a locked specification in one week. You get there in seven months and one week.

The work continues. The next chapter is Python — not theory anymore, but code, runs, plots, and data. The architecture is locked; only the experiments can decide whether the architecture is _real._

🤣 Time to find out.

---

_This document was written by Claude (Anthropic AI) at the end of the conversation that produced drafts 1 through 5.1. It is a companion to `project-personal.md`. The Python phase begins next._
