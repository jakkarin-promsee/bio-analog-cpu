# Draft 6.0

> _The post-pivot line (June 2026). Stage 1 — the first organ, the SCFF + GD neocortex — is now built and
> characterized across Phases 1–4; the live line is Phase 5. This page is the story: why 5.x died, what 6.0
> turned out to be. The day-one plan is kept below as the hypothesis I came back with; the section after it is
> what the simulations actually said (some of it overruled the plan, in my favour)._

## How did we get here?

Draft 6.0 exists because draft 5.0 broke on one missing piece: **direction.** The old learning rule worked out *how much* loss each neuron should absorb — the magnitude — but never *which way* it should move — the sign. Magnitude with no direction can't descend anything, so nothing converged. And patching the sign back in properly would have broken the local-learning core this whole architecture stands on.

So this was a reset, not a patch. The concepts under draft 5.x don't carry forward — I keep the old drafts only as idea references, not as the design. If you're reading `draft6.0/`, this is the design.

It took me a rough few days to accept that. But the reset is also what made the target clear again, and I came back with a completely new plan — the one the rest of this page lays out, and then puts to the test.

## Two weeks later — the deeper lesson

Those first days, the missing sign looked like the whole problem. Two weeks of sitting with it showed me it was only the _symptom_. The real hole was deeper — and the only "fix" for the sign was a trap: patching in full 1:1 directional backprop throws away the whole advantage and marches the chip straight back into the summation wall it exists to escape. "Just fix the sign" was never on the table.

Here's what I actually got wrong. Draft 5.0 treated the brain as **homogeneous** — one structure repeated everywhere, running one simple rule: attribute-based backpropagation, a stack of linear regressions on axon behavior, and intelligence falls out the top. I was so sure of it that I decided _modern ML_ was the thing that was wrong — brute-forcing computation with an n×n transformer that does everything at once, when real intelligence (I thought) is continuous, in-chip, and just this one local rule repeated forever.

And I wasn't wrong about the biology. The brain really does run attribute-based backprop, tracked by synapse-history hormones — I checked, it's real. The problem is we **can't simulate it.** The distribution is cheap; the _direction_ is brutally expensive, and to make my architecture converge I'd have had to compute the exact 1:1 directional backprop I was trying to escape. So none of it was usable. Eight months, and the architecture wouldn't move. I hadn't gotten anything wrong. I'd just been looking too shallow.

Then it flipped. Modern ML was never trying to brute-force nature — **it's trying to cheat it.** You cannot simulate a real axon: one driver feeding many synapses that slide in 3D, where the distance itself multiplies and sums the signal; synapses and drivers created and destroyed on the fly; many hormones sharing one wire at the same instant; pulses whose phase shifts under the myelin sheath; extracellular fluid holding the entire history of every hormone spike; axons that grow and move themselves; hormones that broadcast. You can't compute that 1:1 across tens of billions of cells. So modern ML doesn't — it **projects** all of that down into a low dimension we _can_ compute. That projection isn't a betrayal of the biology; it's the only honest road to it. (Which is the project's own motto walking back to slap me — _copy the function, cheat the implementation._ I'd written it down. I just hadn't believed it all the way down.)

And the brutal part: **the brain isn't homogeneous at all.** The more I read, the clearer it got — every region has its own structure and its own kind of learning. The one-rule-everywhere picture was the real mistake. The missing sign was just where it finally broke.

So I'm taking many steps back. No in-chip memory, no analog ALU, no real circuit yet — all of it waits. **First I make the core math stable, one organ at a time, using most modern ml theory to cheat the biology:**

- **Neocortex** → the SCFF + GD block (the rest of this page).
- **Hippocampus** → a LUT prototype store. I don't have its real shape yet, so the LUT stands in as the default until the math tells me what it wants to be.

The worldview I'm aiming at now — heterogeneous organs, each with its own job and its own learning rule — is the one mapped out in [`research/north-star/`](research/north-star/README.md), topics **1–6**. That's the _direction_. The line I actually walk first is still the smallest stable thing there is: get SCFF + GD to converge.

## The plan I came back with

The rebuild is **two brains on one substrate**, and the whole bet rides on one observation: **direction is the one expensive thing in learning.** Distributing *which way* each weight should move is what costs; everything else is cheap. So pay for direction once, where it counts, and get the rest for free.

- **~80% SCFF — the cheap brain.** Self-Contrastive Forward-Forward: local, derivative-free, forward-only, and *unsupervised*. No backward pass, no order wall (no waiting on other layers), no labels — every neuron updates from its own activity. It organizes the shape of the world on its own. I picked it because it's the only rule I found that is local *and* derivative-free *and* forward-only *and* unsupervised all at once — the only one that can actually live on the substrate.
- **~20% gradient descent — the precise brain.** SCFF can't put a real *label* on the shapes it finds, so a small modern optimizer does: it reads SCFF's features and maps them to classes. Why GD specifically? Because every learning rule ends up paying a cost close to full GD on direction anyway, so I pick the one that buys the most accuracy per unit of compute.

Around that core, the plan added the machinery to make it hold together:

- **A middle layer** to smooth the seam between the two brains, so when SCFF's unsupervised features drift, the GD sitting on top doesn't fall off them.
- **The block concept** — chain `[SCFF → middle → GD]` units, each block's GD checkpoint re-anchoring its output to a fixed label-shape. That way the next block always sees a stable input, and direction can chain end-to-end through an otherwise-local stack.
- **Threshold-gated learning** — run cheap local SCFF most of the time, and only spend the expensive GD update when the error builds past a threshold (the way real cortex seems to).
- **Sleep + a hippocampus** — because the gated GD only re-tracks the data it has recently seen, a periodic "sleep" re-fits GD full-batch over the whole history, with a memory store (a LUT, to start) holding that history.

That was the hypothesis. The point of Stage 1 was to stop arguing it and let the simulations talk.

## What the experiments said — Stage 1 (Phases 1–4)

I built the behavioral simulation (numpy, ideal floats) and walked it down the ladder, one rung at a time, with the rule that **failures are data — never tune until it passes.** The full write-up is in [`src/stage1-report.md`](src/stage1-report.md) (the arc) plus one report per phase; the glossary is [`src/ref-report/`](src/ref-report/README.md). The short version:

**Phase 1 — the cell, and where it actually wins.** One block (SCFF + GD readout) really does generalize better than backprop: a smaller memorization gap (+0.027 vs +0.062 on MNIST) at ~10% of the backward cost. But the sim also corrected my day-one optimism — SCFF does **not** make "a near-perfect classifier." It clusters by **density, not class**: it learns where the data is dense, which is only "class" when classes happen to be dense clusters. It's a weak low-dimensional learner, and it degrades with depth. The real win turned up somewhere I hadn't centered — the **continual** regime. SCFF's unsupervised features don't forget, so where online backprop catastrophically forgets, a cheap **sleep** consolidation recovers near-ceiling accuracy. Sleep + the hippocampus LUT: confirmed. → [`src/phase1/phase1-report.md`](src/phase1/phase1-report.md)

**Phase 2 — depth is not SCFF's lever.** The substrate's cheap axis is *depth*, but a deep SCFF stack can't earn it — and I closed every escape hatch before believing that. Not a transmission problem, and not the negatives: even a perfect label **oracle** doesn't bend the depth curve. Depth instead comes from **boosted ensembles of shallow blocks** with tiny GD readouts (read the readouts, never re-write the stream) — ~85% of GD's accuracy at ~1/6 the backward cost. I concluded the wall was "intrinsic to forward-only locality" — which Phase 3 would narrow. → [`src/phase2/phase2-report.md`](src/phase2/phase2-report.md)

**Phase 3 — the objective reframe (the big correction).** The literature caught the one word that was too strong: the wall is intrinsic to the **energy objective** `Σh²`, not to locality. Forward-only, unsupervised learners *do* compose depth — when their objective preserves *information* instead of energy. So I swapped energy-goodness for a **contrastive (InfoNCE)** objective and added the cross-layer **coordination window** (my own "help the next layer" idea, supplied forward-only). With both, depth composes (on a task with the headroom to show it) — and it re-earns and slightly improves the continual win. **This is adopted; it supersedes the energy-goodness SCFF I came back with.** → [`src/phase3/phase3-report.md`](src/phase3/phase3-report.md)

**Phase 4 — the capability map.** Instead of improving the cell further, I characterized it: the gap to a *genuinely-tuned* backprop across seven controlled axes. The map says exactly what the project always claimed — a **substrate-native continual learner, not a static-accuracy competitor.** It wins continual, nuisance-dimensional input, depth-composition, and depth-is-cheap (the 80/20 advantage is real but **depth-gated** — flat-in-depth for us, linear for backprop); it trails on raw static accuracy and many-class; and it returned one honest **negative** on eval-time weight noise. No flattering surprises, no hidden bug. → [`src/phase4/phase4-report.md`](src/phase4/phase4-report.md)

So the spine I came back with survived — two brains, blocks, gate, sleep — but the simulations rewrote two of its parts in my favour: **the SCFF objective** (energy → contrast + coordination) and **what the architecture is *for*** (a continual learner, not a classifier racing backprop on accuracy). One piece is still only on paper: the **threshold gate** is named but unbuilt. Tuning that, plus the sleep/maintenance loop against this cell's measured drift, is **Phase 5**. And the horizon beyond the numbered phases is still the one the whole question was about — a recurrent, lifelong "thinking" brain where correctness is a self-generated feeling — but simple first.

## Where things live in this folder

| Path                                             | What it is                                                                                                        |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| [`context.md`](context.md)                       | **the full context dump** — the whole picture (what / why / how / the person). Start here if you're cold.         |
| [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md) | **the decision record** — N1–N3 + S1–S8, the live plan (spine committed; Stage 1 set most of the numbers).        |
| [`idea/ideas1.md`](idea/ideas1.md)               | the full derivation, told as a story (every part + _why_).                                                        |
| [`src/`](src/stage1-report.md)                   | **the results.** `stage1-report.md` (the four-phase arc) · `ref-report/` (glossary: methods / metrics / papers) · `phase{1..4}/` (per phase: the report, the summary, the `RESULTS.md` ledger, the run-cards + figures). |
| [`research/survey/`](research/survey/README.md)         | survey of learning algorithms — the _options_ considered (attribution here is draft-5.1 history).                 |
| [`research/papers/`](research/papers/README.md)         | paper stories behind the adopted design — Phase 1–2 (SCFF, Distance-Forward, BoostResNet, BYOL, LLRD) **and** Phase 3 (Greedy InfoMax, CLAPP, Mono-Forward, the objective reframe). |
| [`research/north-star/`](research/north-star/README.md) | the **north-star** research dossier (beyond the numbered phases) — free-time reading, _not_ the line to walk now (`th/` = Thai mirror). |
