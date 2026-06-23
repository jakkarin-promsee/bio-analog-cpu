# Top-Down and Bottom-Up Processing in the Brain

## Overview / Core Idea

The brain is **not** a feedforward pipe — it does not simply receive input → process → decide. Two streams of information run in opposite directions *at the same time, continuously*, and the surprising fact is that the downward stream is far larger than the upward one: **feedback (top-down) connections outnumber feedforward (bottom-up) connections by roughly 9 to 1.**

That ratio is not an accident of wiring. It is the signature of a **generative model**. The brain's primary mode is to *predict* what it is about to sense, send that prediction downward, and use the actual senses only to *correct* the prediction. So the two streams carry different things:

- **Top-down** carries the **prediction** (an internal model of what the lower level should be seeing) and **attention** (where to look / what to amplify).
- **Bottom-up** carries the **prediction error** — only the part of the sensory signal that did *not* match what was predicted.

This is the **predictive coding** framework, and it is a biological realization of **attribution-based credit assignment**: when a prediction is wrong, the error is attributed back to the neurons that contributed to it, in proportion to their contribution, by the network's own structure and by retrograde signaling — not by any separately-implemented algorithm. The brain is a *prediction machine* that constantly generates a model of the world and uses sensation to repair it, not a passive receiver waiting for data. Top-down is not "just feedback" — it is the core of the computation.

---

## Benchmark

This is neuroscience, not a benchmarked algorithm, so the "benchmark" is the **empirical evidence base** — the measured numbers and observations that pin the model down:

| Measured fact | Value / evidence |
| ------------- | ---------------- |
| Feedback : feedforward connection ratio | **~9 : 1** (≈90% of cortical connections are top-down) |
| Bottom-up feedforward sweep (retina → IT) | **~50 ms** — the fastest pass, gives a coarse "first impression" |
| Top-down onset (after first sweep reaches IT) | **~100–150 ms**, with iterative refinement over **100–300 ms** |
| Synaptic target — feedforward | cortical **layer 4** |
| Synaptic target — feedback | cortical **layers 1, 2/3, 5, 6** (different targets ⇒ different function, not a mere reverse path) |
| Visual hierarchy | retina → LGN → V1 → V2 → V4 → IT |
| Direct evidence for top-down dominance | **optical illusions** — Kanizsa triangle (seeing edges that aren't there), size constancy (correcting retinal size by perspective) |
| Scale of the substrate | ~**86 billion** neurons, ~**100 trillion** synapses — enormous statistical redundancy |

The two timing numbers and the 9:1 ratio are the load-bearing ones: a fast feedforward sweep that produces a draft, followed by a much larger, slightly slower top-down stream that refines it — exactly the shape predictive coding requires.

---

## Bottom-Up Processing

### What it is

Bottom-up is the flow of information from sensory input *upward* toward higher-order processing. Information starts at its rawest level and becomes progressively more abstract at each stage.

### The real path in the visual system

It begins at the **retina**, which captures light and converts it to electrical signal, passes through the **LGN** (Lateral Geniculate Nucleus) in the thalamus, enters **V1** (primary visual cortex), and then travels onward through **V2 → V4 → IT** (Inferotemporal Cortex).

### What each stage does

Crucially, each stage does **not** pass its raw input upward unchanged — each performs **compression and abstraction** first:

- **Retina** — detects contrast and edges using *on-center/off-surround* cells that respond to *differences* in brightness, not absolute brightness.
- **V1** — responds to edge **orientation**, spatial frequency, and color-opponent pairs. Each V1 cell has its own preferred orientation — a tuning learned through **Hebbian / STDP** plasticity, with no backprop anywhere.
- **V2** — handles **texture**, *illusory contours* (edges the brain perceives though they are not physically present), and **border ownership** (knowing which object an edge belongs to).
- **V4** — does **shape** processing and **color constancy** (an object keeps its perceived color even as the lighting changes).
- **IT** — does **object identity** — knowing *what* a thing is, regardless of pose, angle, or size.

### What bottom-up actually transmits

This is the most important and most misunderstood point: bottom-up does **not** send raw pixels upward. It sends only the **prediction error** — the part of the signal that does not match what top-down predicted.

- top-down predicts correctly → the bottom-up signal is **silent**.
- top-down predicts wrongly → the bottom-up signal is **loud**, carrying the difference upward.

The brain saves enormous bandwidth this way. Instead of shipping the entire scene upward every frame, it ships only what is "surprising" or "off-prediction."

### Timing

The bottom-up sweep is fast — about **50 ms** from retina to IT. It is the quickest feedforward pass and provides a rough "first impression" of the scene before anything else happens.

---

## Top-Down Processing

### What it is

Top-down is higher-order areas sending information *down* to lower-level areas — sending a **prediction** or **expectation** of what the lower level should be seeing.

### Why ~90% top-down?

The brain has roughly **9× more feedback than feedforward** connections. This is not a coincidence; it is a fundamental architectural statement that the brain operates primarily as a **generative model** — it builds a model of the world internally and uses sensory input to *correct* it, rather than acting as a passive receiver.

### The path

Top-down runs back from **IT → V4 → V2 → V1**, and even down to the **LGN**. But the synaptic targets differ: feedforward connections land on cortical **layer 4**, while feedback connections land on **layers 1, 2/3, 5, and 6.** Different targets mean a different *function* — feedback is not merely the forward path run in reverse.

### What top-down sends down

**Prediction (the generative model).** When IT "thinks" it sees a cat, it sends a prediction downward: V4 should see fur texture and curved shapes, V2 should see soft edges, V1 should see *this* orientation pattern at *this* location. This is an internal model built from experience, not a feedforward computation.

**Attention (gain modulation).** Top-down also sends a gain signal — it does not say *what* is there, it says *where to attend.* Like a spotlight, it amplifies the signal in interesting regions and suppresses it elsewhere.

### Timing

Top-down begins about **100–150 ms** after the first bottom-up sweep reaches IT, producing several rounds of **iterative refinement** between roughly **100 and 300 ms.**

---

## Neuron-level mechanism — dendritic computation

### A neuron is not just a threshold function

In the simple model a neuron is: receive input → weighted sum → activation function → output. The real thing is far more structured.

### The dendritic tree

Each neuron has a **dendrite** that branches into a large tree. Each branch performs its *own* local computation first, then integrates upward to the **soma** (cell body) — a hierarchical summation. The result is that a single neuron computes something far more complex than a simple threshold; some work argues a single neuron's computational power approaches that of a small neural network.

### Bottom-up and top-down do not mix at the same synapse

This is the key insight: feedforward (bottom-up) synapses sit on the **proximal** dendrite and soma, while feedback (top-down) synapses sit on the **distal** dendrite, farther out.

- **Bottom-up input** arrives directly at the soma — strong enough, it fires.
- **Top-down input** arrives at the distal dendrite → generates a **dendritic spike** → *modulates the soma's threshold.*

The consequence: a neuron fires most readily when **bottom-up and top-down agree** — when there is both sensory evidence *and* a top-down expectation endorsing it. The neuron is a coincidence detector between "what I sense" and "what I expected."

---

## The predictive coding framework

### Core concept

Predictive coding holds that the brain works by continuously trying to **minimize prediction error.** Each level maintains two populations:

- **Representation units** — hold the current belief about what is being seen, and adjust to the input.
- **Error units** — compute the difference between the bottom-up input and the top-down prediction, and pass only that difference upward.

### The loop

1. Top-down sends a prediction down: "this is what you should see."
2. Bottom-up sends the actual sensory data up.
3. Error units compute **prediction error = actual − predicted.**
4. That error is sent up so the higher level can update its representation.
5. The higher level updates its prediction and sends it back down.
6. Repeat until the error is small enough.

### Why this is genuinely attribution-based

When a top-down prediction is wrong, the error that flows up is **attributed to the neurons that contributed to that prediction error, in proportion to each one's contribution.** It is attribution *through the network's own structure* — not an algorithm bolted on separately. (See `distribution-based.detail.md` for the formal $\lvert a\cdot W\rvert/\sum\lvert a\cdot W\rvert$ rule this implements.)

---

## Optical illusions — evidence that top-down is real

Illusions happen when the top-down prediction is *stronger* than the bottom-up signal: the brain "sees" what it expects rather than what is physically present.

- **Kanizsa triangle** — the brain sees a triangle with no actual edges, because the top-down prediction "there is probably a triangle here" overrides the bottom-up signal "there are no edges."
- **Size constancy** — a distant person is perceived at their true size even though their retinal image is smaller, because the top-down model understands perspective.

These are direct, everyday demonstrations that the downward stream can win — which only makes sense if it is doing real computational work, not just relaying feedback.

---

## Neurotransmitters and retrograde signaling

### Retrograde signaling

Normally signal flows pre-synaptic → post-synaptic. But there are mechanisms by which the post-synaptic side sends a signal *back*.

- **Endocannabinoids** — when the post-synaptic neuron detects error → it synthesizes an endocannabinoid → it diffuses *backward* across the synapse → binds CB1 receptors on the pre-synaptic terminal → reduces neurotransmitter release. The amount released is **proportional to the post-synaptic firing rate**, so the pre-synaptic side learns *how much it contributed to the error.* This is attribution arising naturally from the chemistry.
- **Nitric oxide** — diffuses as a gas in all directions, modulating *all* nearby neurons. Not specific, but it creates a neighborhood effect.

### Synaptic pruning

The brain does not only *strengthen* connections — it actively **destroys** unused ones.

- **Complement system (C1q, C3)** — tags inactive synapses; **microglia** then eliminate them. This is most aggressive in childhood.
- **BDNF** (Brain-Derived Neurotrophic Factor) — low BDNF → the synapse is removed; high BDNF → the synapse is strengthened.

In an analog-hardware analogy, **capacitor leak is a natural synaptic pruning**: a weight that is not reinforced simply decays away on its own.

---

## Multiple timescales

The brain does not learn with one mechanism at one timescale — it runs many in parallel:

- **Milliseconds — STDP (Spike-Timing-Dependent Plasticity).** If the pre-synaptic neuron fires *before* the post-synaptic one within a few ms → strengthen (Hebbian). If post fires first → weaken (anti-Hebbian). A local rule precise down to spike timing.
- **Seconds — neuromodulators.** Dopamine, serotonin, norepinephrine broadcast across the brain as a *global* signal saying whether the outcome was good or bad, working with **eligibility traces** to assign credit across time.
- **Hours / days — LTP / LTD.** Long-Term Potentiation/Depression — durable changes in synaptic strength via molecular mechanisms (e.g. AMPA receptor trafficking), driven by rehearsal and consolidation.
- **Sleep — hippocampal replay.** During sleep the hippocampus replays the day's experiences to the neocortex, consolidating memories and updating layers that received no signal during the day.
- **Weeks / months — synaptic pruning.** Cutting unused connections, making the network sparser and more efficient.
- **Years — structural plasticity.** Growing new connections, relocating synapses, reshaping dendritic morphology.

---

## Why the brain does not need backpropagation

### Weight transport problem

Backprop needs the next layer's weights, transposed, to send error back. The brain has no such mechanism. Instead it uses **local attribution through the dendritic tree** — each synapse knows how much it contributed to the output from the current that passed through *it*, with no need for global information.

### Credit assignment across time

Backprop has no native mechanism for *temporal* credit. The brain uses **eligibility traces + neuromodulators** — a synapse remembers it was recently active, and a later reward signal lands on the synapses still "eligible."

### Exact gradients are unnecessary

With ~86 billion neurons and ~100 trillion synapses, the brain has enormous **statistical redundancy.** A coarse signal still gives good results in the long run; there is no need to be precise about every individual weight.

---

## Summary

| Aspect | Bottom-Up | Top-Down |
| ------ | --------- | -------- |
| Direction | sensory → higher cortex | higher cortex → sensory |
| Carries | prediction **error** | prediction / attention |
| Speed | fast (feedforward sweep ~50 ms) | slower (feedback ~100 ms+) |
| Synaptic target | layer 4 | layers 1, 2/3, 5, 6 |
| Share of connections | ~10% | ~90% |
| Role | sensory evidence | generative model |

The brain is a **prediction machine** that continually generates a model of the world and uses sensory input to correct it — not a passive processor waiting for data. **Top-down is not merely feedback; it is the heart of the computation.**
