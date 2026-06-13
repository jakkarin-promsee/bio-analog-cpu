# Draft 6.0 — The Whole Idea, Told Start to End

> A narrative walkthrough of the draft-6.0 architecture: every stage, *why* it exists, and the math we'll actually use. Read this top to bottom — each part only makes sense once you know the problem the part before it left behind.

---

## Prologue — why we burned the old draft down

Draft 5.0 died on one missing word: **direction**.

The whole 5.x model distributed loss by *magnitude* — how much each neuron should be blamed — but never carried the *sign* of that blame. We were telling every neuron "you were wrong by this much" and never "wrong in which way." A network that knows the size of its error but not its direction cannot descend anything. Nothing converged, and the only honest fix — routing a signed error back through the network — would have broken the locality rules the whole chip is built on. So we threw 5.x out and kept only the ideas as reference.

But the failure taught us the thing draft 6.0 is built around:

**Direction is the expensive part of learning.** Magnitude is cheap — the substrate measures `|a·W|` for free. Direction is what costs you a backward pass, a transpose, a chain of dependencies. Every learning algorithm that works pays for direction somewhere. The ones that *don't* pay — pure Hebbian, pure local rules — are cheap precisely because they give up direction, and that's exactly why they stall on hard tasks.

So draft 6.0 stops pretending direction is free. Instead: **pay for it once, in one place, and make everything else cheap.**

---

## Chapter 1 — The two brains

That single decision splits the model into two organs with completely different jobs and completely different costs.

**The cheap brain (≈80%) — SCFF.** A label-free, forward-only, local learner that does one thing: organize the input into clean, separable structure. It never sees a label. It never computes a direction. It just keeps making the data more separable, layer after layer, for free. This is the bulk of the network.

**The precise brain (≈20%) — Gradient Descent.** A small, expensive module that takes the clean structure SCFF produced and maps it onto the *real labels we care about*. This is the only place direction gets paid for. Because it sits on top of already-organized features, it can be small — it's translating, not discovering.

The picture to hold in your head: **SCFF is the senses and the cortex that sorts the world into "kinds of things"; GD is the small part that puts names on them.** The senses run constantly and cheaply. The naming runs rarely and carefully. Most of the brain is the cheap part — that's the 80/20, and it's the whole reason the chip can be cheap.

Everything below is the consequence of making these two brains live together on one analog substrate.

---

## Chapter 2 — How the cheap brain learns (SCFF)

SCFF is **Self-Contrastive Forward-Forward**. It descends from Hinton's Forward-Forward: instead of a forward pass plus a backward pass, you run *two forward passes* — one on "positive" (real) data, one on "negative" (fake) data — and train every layer locally to be **loud on positives, quiet on negatives**. No gradient ever crosses a layer boundary.

Forward-Forward's weak point was always *where the negatives come from* — Hinton faked them with corrupted labels, which needs labels and only works on easy data. SCFF's one move is to **build positives and negatives out of the data itself, by summation**:

- **Positive** = a sample added to itself → "this is one coherent thing."
- **Negative** = a sample added to a *different* sample → "this is a mixture, not one thing."

Each layer is trained so its **goodness** — the energy of its activations, `‖h‖²` — is high for positives and low for negatives. A layer that does this has learned to tell "a real thing" from "a mash-up of two things," and that is enough to pull the data apart into separable clusters. No labels touched.

Two structural gifts fall out of "summation, not concatenation":

1. **The input never grows.** Because we sum *before* the weight, the layer width is unchanged. SCFF is a drop-in change to a normal forward pass — feed it `2·x_k` or `x_k + x_n` instead of `x_k`.
2. **The two weight slots collapse to one.** The positive pair is always identical data, so the two weight matrices would converge to the same thing anyway. We set `W₁ = W₂ = W` from the start. One weight, shared by both worlds — remember this, it's what makes the hardware cheap in Chapter 3.

This is why SCFF is the right cheap brain: it needs **no derivative, no weight transport, no backward pass, and no label wire.** Every layer learns from a scalar it measures on its own output. Among every learning rule we surveyed, it's the only one that is local *and* derivative-free *and* forward-only *and* unsupervised, all at once.

---

## Chapter 3 — Mono-forward: SCFF on our silicon

Here's where it stops being someone else's algorithm and becomes *our chip*.

"Two forward passes" sounds like double the cost. It isn't — because we don't run them one after another in time. We run **one forward sweep**, and carry **two worlds side by side** down the datapath: a **positive world** and a **negative world**. Both `a_pos` and `a_neg` flow forward together, layer to layer — which we need anyway, because the next layer's contrast depends on both.

The key hardware fact: **the weight crossbar is shared.** Both worlds pass through the *same* `W` (that's the `W₁ = W₂ = W` identity made physical). The Scaps — which hold the weights, the expensive resident state, the entire thesis of the chip — are **not** doubled. What doubles is only the **LocalCapacitors**: the small, RAM-like buffers that hold the temporary activation values `a` between layers. Two worlds means two sets of temp activations. That's the cheapest, most transient state on the die.

Between the two worlds sits an ALU that reads off `G_pos` and `G_neg`, computes the SCFF loss term, and writes the weight update straight into each Scap's update capacitor. So one sweep produces: both worlds' activations, the contrast, and the update.

And because we keep `G_pos` and `G_neg` as **two explicit values** — not collapsed onto one node — we keep the **full two-sided objective**: push `G_pos` above the threshold *and* `G_neg` below it. That two-sided form has a built-in dead zone that stops the goodness from inflating forever, so there's no scale-runaway to engineer around. (An earlier sketch that merged the two worlds onto one capacitor *did* have a runaway problem; keeping them separate is what avoids it.)

The trade we're making: ~2× the activation buffers and a bit of ALU, in exchange for **one charge cycle instead of two**. On a substrate where capacitor charge time is the clock, spending cheap RAM-like area to save a whole charge cycle is the correct trade. Resources we optimize later; the charge-cycle count is what we protect now.

**One mandatory detail:** between layers we **normalize the activation length**, `ĥ = h/‖h‖`. Forward-Forward *requires* this — otherwise the next layer could cheat by just reading the previous layer's goodness instead of learning its own. We get a bonus from it later (Chapter 6): a normalized interface is a *stable* interface.

---

## Chapter 4 — The negative-data problem, and the LUT

On-chip, `x_neg = x_k + x_n` raises a question: where does that "different sample `x_n`" come from in a single streaming forward pass? We can't hold the whole batch.

The answer is a small **lookup-table prototype memory**: a deduplicated store of *kinds of inputs* the chip has seen. When a new sample arrives, we compare it against the stored prototypes; if it's close to one, it's not new; if it's far from all of them, we allocate it as a new prototype. The store stays small because it keeps *types*, not every example.

Three reasons this is the right structure:

- **It feeds good negatives.** Mixing a sample with a prototype from a *different* cluster gives a hard, informative negative — far better than a random partner.
- **Store raw inputs, not features.** Features drift over training (that's Chapter 6's whole problem); raw input space is stable ground truth, so the store never silently rots.
- **It builds itself.** A small winner-take-all layer *is* an online prototype store — winners get pulled toward the input, "no winner close enough" allocates a new entry, usage counters retire stale ones. The match is just a dot-product, which is a crossbar op. The LUT is one small content-addressable crossbar.

And it pays off three times: negatives for SCFF now, replay history for sleep later (Chapter 9), and the seed of the "memory model" we want eventually. The hippocampus idea becomes "a learned, compressed version of this same store."

---

## Chapter 5 — The precise brain (GD), and how it reads SCFF

SCFF gives us clean clusters — but they're *unsupervised*. The cluster "all these look like the same kind of thing" has no name on it. GD's job is to put the names on.

**How GD gets its information: it reads, it doesn't reach in.** GD taps the activations of the **last n SCFF layers** and works off that. Reading several layers (not just the final one) does two things: it gives GD richer context than one thin top layer, and — crucially — it means **GD and SCFF never share a weight.** SCFF owns its layers; GD owns its own module and only *reads* SCFF's output. Hold onto that: it dissolves a problem that would otherwise be nasty (Chapter 6).

**GD is allowed to be a real, modern optimizer.** This is a deliberate choice: we already conceded that direction is expensive and that we'd pay for it *here*. Even a biological neuron can't dodge the summation wall when it distributes credit. So we don't make GD pretend to be bio-pure — inside this module we use the best tools that converge, forward and backward both. The bio-inspired cleverness lives in SCFF; GD is the part we let be unapologetically precise.

GD actually shows up in **two sizes**, because it has two different jobs:

- **Interface GD** — small (a layer or two) at a block's exit. Its job is *tracking*: keep the block's output in a fixed range and shape so the next block always sees something familiar. Tracking wants low latency and cheap frequent steps → plain SGD + momentum, simple squared-error.
- **Output GD** — the real "name the world" brain at the very end. Its job is *precision*: the best possible map from features to labels. Here the modern machinery earns its keep → an Adam-class optimizer online, cross-entropy loss, and at sleep (Chapter 9) a full-batch solve to convergence.

---

## Chapter 6 — The drift problem, and the plasticity gradient

Now the hard part, and the one we went back and forth on.

SCFF never stops learning. That's its virtue — more data, more structure — but it means **SCFF's output keeps moving.** The clusters slowly shift position. GD, sitting on top, was trained against where the clusters *used to be*. If SCFF drifts faster than GD can re-track, the names end up on the wrong clusters and the whole output breaks.

The first instinct was heavy machinery — two capacitors per weight, one for SCFF and one for GD, to stop them overwriting each other. **We threw that out.** It was solving a problem that doesn't exist here: SCFF and GD *don't share weights* (Chapter 5 — GD reads, it doesn't write into SCFF). There's no tug-of-war over a shared weight to protect against.

What's actually left is much smaller: **keep the n read-layers from drifting so fast that GD can't keep up.** Not freeze them — *bound* them.

The fix is a **plasticity gradient**: the SCFF layers that GD reads learn **slow**; the front SCFF layers stay **fast**. The front does the hard discovery work and adapts freely; the layers facing GD present a nearly-still face. On our substrate this is *free* — it's just weaker update coupling (a bigger smoothing cap, a smaller learning rate) on those Scaps. **Zero extra state.** Those layers simply run on a slower clock.

Here's why this is the *budget-correct* fix and not just *a* fix. The constraint is:

> SCFF drift across one GD interval < what one GD update can absorb.

GD fires rarely (Chapter 7) — say once in ~1000 steps. So drift ≈ (read-layer learning rate) × (steps between GD updates). You can satisfy the inequality two ways: **slow the read-layers** (free), or **fire GD more often** (expensive — it burns the exact compute budget SCFF exists to save). So you *always* bound the drift on the cheap SCFF side. The plasticity gradient spends nothing and protects the thing that makes the architecture cheap. Biology runs the same gradient, for what it's worth: sensory layers stay plastic, association layers consolidate and slow. Our read-layers are the association end.

**One thing slowing the rate doesn't catch:** a *permutation event* — a layer suddenly re-clustering, neurons swapping which class they code. That's discontinuous; a slower clock only delays it. Two cheap guards, both already in our kit: a **BCM sliding threshold** (homeostasis — an over-active neuron raises its own bar, which kills the winner-take-all collapse that triggers permutations, and it runs on the momentum register we already have), and the **multi-layer tap itself** — if GD reads n layers, one layer flipping doesn't blind it.

If it ever turns out the slow read-layers learn *too* slowly and SCFF's ceiling suffers, there's a known upgrade — let them learn fast but have GD read a slow **EMA copy** of them — at the cost of n extra layer-caps. We reach for it only if the free version pinches.

**This also resolves the "middle layer."** The middle layer originally had to do two jobs at once — give GD context *and* hand off smoothly — and blending two objectives on the same layer made them fight. Split the jobs and the fight disappears: **taps** give GD its context (Chapter 5), the **plasticity gradient** gives the smooth, stable handoff (this chapter). Any direct GD *shaping* of the middle layers becomes optional polish, not the load-bearing mechanism.

---

## Chapter 7 — When do we pay? The threshold gate

GD is expensive, so we don't run it every step. We **gate** it:

- **Loss below threshold:** update **SCFF only.** Cheap, local, constant. The model keeps sharpening its unsupervised structure.
- **Loss above threshold:** update **SCFF as normal, plus GD.** Pay for direction exactly when the cheap brain alone isn't keeping the output good enough.

There's real theory under this, borrowed (just the result, not the mechanism) from gradient-reconciliation analysis of block-wise learning. Local-only learning converges fine **as long as the mismatch between neighboring blocks stays small** — but that mismatch injects an *error floor* into the loss that doesn't shrink with training. While the floor is below the loss, local learning is descending and you don't need GD. Once the floor dominates, local learning *stalls forever* no matter how long you run it — and that's precisely the moment to spend a GD update. The threshold is the chip's way of feeling for that floor.

A refinement worth testing: gate on the **loss slope**, not the absolute loss. When loss under SCFF-only updates stops improving — flat slope — you've hit the floor, regardless of its height. That's "plateau detection," and it's two capacitors: a fast loss-average compared against a slow one.

---

## Chapter 8 — Scaling up: the block concept

One SCFF→middle→GD stack is a **Block**. The block concept chains them:

> [SCFF + middle + GD] → [SCFF + middle + GD] → … → [SCFF + middle + GD]

Why chain instead of building one giant SCFF with a single GD at the end? Because a single GD at the very end has to absorb the drift of the *entire* SCFF stack — the most fragile possible arrangement. Putting a GD checkpoint between every block buys two things:

1. **A fixed-range translation layer at every boundary.** No matter how Block 1's SCFF shifts, its Interface GD pulls the output back toward a stable, labeled shape — so Block 2 always receives something familiar. Each interface only has to absorb the drift of *one* block, not the whole stack.
2. **Direction chains end-to-end.** The GD stages connect to each other, so the one thing SCFF can't provide — direction — links through the whole model, even though most layers are SCFF.

To chain direction between blocks cheaply, we **don't** run a full backward pass through everything. We approximate each block as if it were a single linear layer with one effective weight — roughly `Block_out / Block_in` — and pass the delta block-to-block through that. This turns the backward cost from "length of the network" into "number of blocks." (A cleaner estimate keeps a running correlation instead of a raw ratio, so it stays warm even during long SCFF-only stretches — but the idea is the same: a cheap linear stand-in for each block.)

This is where the gate from Chapter 7 meets the chain: below threshold every block runs **local-only**; above threshold we run the **chained delta** between blocks. It's less "discrete" in that moment — the blocks briefly talk to each other — but that's the price of handling genuinely hard tasks, and we only pay it when the cheap path has visibly stalled.

---

## Chapter 9 — Sleep: covering the whole world again

The gate creates a subtle problem. When loss spikes and GD fires, it only re-fits the **data that just spiked** — the last thing seen. Meanwhile SCFF's whole map has been drifting. If only ~10% of inputs ever trip the threshold, GD ends up correctly covering only ~10% of the *new* SCFF map. The other 90% — everything that wasn't recently surprising — quietly goes stale.

So we add a **sleep-like phase**: periodically, stop streaming and **retrain GD full-batch over the whole history** against the current SCFF map. This re-covers the entire data range, past to present, in one shot — the way sleep is thought to replay the day into long-term structure.

Sleep is cheap *by construction*, which is the nice surprise: GD is only ~20% of the weights, and the SCFF body is frozen during sleep, so each replayed sample is just a forward pass into a small module being fit. That flips the design question from "can we afford sleep?" to "how *little* history do we need?" — which is exactly the knob we want to sweep.

Where the history lives: the **LUT prototype store from Chapter 4.** It already holds deduplicated input types; tag them with labels and counts and it's a compact replay set. The "20% history" experiment becomes "*prototype* history" — principled compression, not an arbitrary subsample.

Three things make the re-fit robust to SCFF's drift: **normalize the taps** (kills most gain/offset drift before GD ever sees it), **replay across the drift history** (so GD learns the *family* of representations, not one snapshot), and **jitter the replayed features** — and here's the analog joke that isn't a joke: our substrate makes Gaussian noise for *free*. The thing every analog designer fights becomes drift-robustness training at zero cost.

---

## The math we'll use (consolidated)

**SCFF — contrastive inputs:**
$$x_\text{pos} = x_k + x_k = 2x_k, \qquad x_\text{neg} = x_k + x_n \ \ (n \neq k)$$

**Forward (shared weight, both worlds), with inter-layer normalization:**
$$h^l = \phi\!\left(W^l\,\hat h^{\,l-1}\right), \qquad \hat h^l = \frac{h^l}{\lVert h^l\rVert + \varepsilon}$$

**Goodness and the two-sided per-layer loss:**
$$G^l = \lVert h^l\rVert^2, \qquad
\mathcal{L}^l = \log\!\big(1+e^{-(G^l_\text{pos}-\theta)}\big) + \log\!\big(1+e^{+(G^l_\text{neg}-\theta)}\big)$$

**Local update (gradient through one layer only) with the plasticity gradient:**
$$\Delta W^l = -\,\eta_l\,\frac{\partial \mathcal{L}^l}{\partial W^l}, \qquad
\eta_l = \eta_0\,\rho^{\,d(l)} \ \ (\rho<1)$$
where `d(l)` grows toward the read-layers, so the layers GD taps learn slowest.

**BCM homeostatic threshold (per neuron, anti-permutation), on the momentum register:**
$$\theta^{\text{BCM}}_j = \langle a_j^2\rangle$$

**LUT prototype store (winner-take-all with novelty allocation):**
$$k^\* = \arg\max_k \langle p_k, x\rangle; \qquad
\langle p_{k^\*}, x\rangle < \tau_\text{vig} \ \Rightarrow\ \text{allocate } p_\text{new} = x$$

**Interface GD (tracking — delta rule, squared error):**
$$\mathcal{L}_\text{IF} = \tfrac12\lVert y-\hat y\rVert^2, \qquad \Delta W_\text{IF} = \eta\,x\,(y-\hat y)$$

**Output GD (precision — Adam-class, cross-entropy):**
$$m \leftarrow \beta_1 m + (1-\beta_1)g, \quad v \leftarrow \beta_2 v + (1-\beta_2)g^2, \quad
W \leftarrow W - \eta\!\left(\frac{\hat m}{\sqrt{\hat v}+\varepsilon} + \lambda W\right)$$
$$\mathcal{L}_\text{out} = -\textstyle\sum_c y_c \log \operatorname{softmax}(z)_c$$

**Block delta — cheap linear stand-in (O(blocks) backward):**
$$\widehat{W}_\text{block} \approx \frac{\text{Block}_\text{out}}{\text{Block}_\text{in}}
\qquad\text{(warm version: } \widehat W_{ij} = \frac{\text{EMA}[\,o_i x_j\,]}{\text{EMA}[\,x_j^2\,]}\text{)}$$

**The gate, and its theory (gradient-mismatch error floor):**
$$\text{if } \mathcal{L} < \Theta:\ \text{SCFF only}; \qquad \mathcal{L} \ge \Theta:\ \text{SCFF} + \text{GD (chained delta)}$$
$$L_K^{(i+1)} - L_K^\* \;\le\; (1-\alpha\mu)\big(L_K^{(i)} - L_K^\*\big) \;+\; \alpha\,\lVert \epsilon^{(i)}\rVert^2$$
(plateau-detection variant: fire when $\text{EMA}_\text{slow}(\mathcal{L}) - \text{EMA}_\text{fast}(\mathcal{L}) \approx 0$.)

**The drift design inequality (sets the plasticity gradient):**
$$\underbrace{\eta_\text{read}\cdot \tau_\text{GD}}_{\text{drift between GD updates}} \;<\; \underbrace{\Delta_\text{GD}}_{\text{one update's correction capacity}}$$

**Sleep:** full-batch GD over LUT prototype history, forward-passed through the frozen SCFF body, taps normalized and noise-jittered.

---

## The experiment ladder

We test on classification / statistics tasks only, simplest first, one thing changed at a time.

**1 — the atoms**
- 1.0 Full SCFF (with: mono-forward dual-rail, mandatory inter-layer norm; sub-cells: two-sided loss vs pure-contrast, and a cheaper forward-only rival as a bench check).
- 1.1 Full gradient descent (the precision ceiling to quote against).

**2 — putting them together**
- 2.0 SCFF + GD (taps, no middle shaping).
- 2.1 SCFF + middle + GD — and the key cell: **frozen vs slow vs fast read-layers**, which directly sets the plasticity gradient.

**3 — staying alive over time (sleep)**
- 3.0 No sleep (watch it rot — failure is data).
- 3.1 Sleep, full-batch history.
- 3.2 Sleep, **prototype-LUT** history.
- 3.3 Sleep, with a learned memory model holding the history.

**4 — scaling out**
- Chain blocks: [SCFF+middle+GD] → … — gated on a stable init from steps 1–3.

---

## Epilogue — what's locked vs what the sims decide

**Locked** (the spine): two brains, SCFF cheap + GD precise; pay for direction once, in GD; mono-forward dual-rail SCFF with shared weights; GD reads SCFF by tapping the last n layers; threshold-gated GD; blocks with interface-GD translation; sleep replay; the LUT as the memory of record.

**The sims decide** (the knobs, not the spine): the front:back plasticity ratio (set by experiment 2.1); the gate threshold, and whether it's absolute or plateau-based; how much history sleep really needs (3.x); the LUT vigilance threshold; whether pure-contrast loss or the two-sided loss converges better; how many blocks before direction-chaining strains.

The shape of the answer is committed. The numbers are what we're about to go find.
