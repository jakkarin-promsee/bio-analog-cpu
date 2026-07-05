# Draft 6.0

> _The post-pivot line (June–July 2026). This is the **story of the whole build** — why draft 5.x died, what 6.0
> turned out to be, and what ten phases of simulation actually said (some of it overruling the plan, in my favour).
> The **soul** under all of it — the origin, the collapse, the return, the person — is
> [`../docs/essence/the-essence2.md`](../docs/essence/the-essence2.md); this page is the **technical** companion. The
> results in full are in [`src/`](src/README.md); the committed design is [`idea/`](idea/README.md); the acronym
> glossary (SCFF · InfoNCE · RanPAC · BWT · …) is [`src/ref-report/`](src/ref-report/README.md). Read the day-one
> plan below as the hypothesis I came back with — then read what the sims did to it._

## How did we get here?

Draft 6.0 exists because draft 5.0 broke on one missing piece: **direction.** The old learning rule worked out *how
much* loss each neuron should absorb — the magnitude — but never *which way* it should move — the sign. Magnitude
with no direction can't descend anything, so nothing converged. And patching the sign back in properly would have
broken the local-learning core this whole architecture stands on.

So this was a reset, not a patch. The concepts under draft 5.x don't carry forward — I keep the old drafts only as
idea references, not as the design. If you're reading `draft6.0/`, this is the design.

It took me a rough few days to accept that. But the reset is also what made the target clear again, and I came back
with a completely new plan — the one the rest of this page lays out, and then puts to the test.

## Two weeks later — the deeper lesson

Those first days, the missing sign looked like the whole problem. Two weeks of sitting with it showed me it was only
the _symptom_. The real hole was deeper — and the only "fix" for the sign was a trap: patching in full 1:1
directional backprop throws away the whole advantage and marches the chip straight back into the summation wall it
exists to escape. "Just fix the sign" was never on the table.

Here's what I actually got wrong. Draft 5.0 treated the brain as **homogeneous** — one structure repeated
everywhere, running one simple rule: attribute-based backpropagation, a stack of linear regressions on axon
behavior, and intelligence falls out the top. I was so sure of it that I decided _modern ML_ was the thing that was
wrong — brute-forcing computation with an n×n transformer that does everything at once, when real intelligence (I
thought) is continuous, in-chip, and just this one local rule repeated forever.

And I wasn't wrong about the biology. The brain really does run attribute-based backprop, tracked by synapse-history
hormones — I checked, it's real. The problem is we **can't simulate it.** The distribution is cheap; the _direction_
is brutally expensive, and to make my architecture converge I'd have had to compute the exact 1:1 directional
backprop I was trying to escape. So none of it was usable. Eight months, and the architecture wouldn't move. I
hadn't gotten anything wrong. I'd just been looking too shallow.

Then it flipped. Modern ML was never trying to brute-force nature — **it's trying to cheat it.** You cannot simulate
a real axon — one driver feeding many synapses that slide in 3D, distance itself multiplying the signal, synapses
made and destroyed on the fly, many hormones sharing one wire, pulses phase-shifting under myelin, the extracellular
fluid holding every spike's whole history. You can't compute that 1:1 across tens of billions of cells. So modern ML
doesn't — it **projects** all of it down into a low dimension we _can_ compute. That projection isn't a betrayal of
the biology; it's the only honest road to it. (Which is the project's own motto walking back to slap me — _copy the
function, cheat the implementation._ I'd written it down. I just hadn't believed it all the way down.)

And the brutal part: **the brain isn't homogeneous at all.** Every region has its own structure and its own kind of
learning. The one-rule-everywhere picture was the real mistake; the missing sign was just where it finally broke. So
I took many steps back — no in-chip memory, no analog ALU, no real circuit yet — and set out to make the core math
stable **one organ at a time**, using modern ML to cheat the biology: the **neocortex** first (the SCFF + GD block,
the rest of this page), the **hippocampus** as a LUT prototype store standing in until the math tells me its real
shape. The heterogeneous-organs worldview is mapped in [`research/north-star/`](research/north-star/README.md); the
line I actually walk first is the smallest stable thing there is — get SCFF + GD to converge.

## The plan I came back with

The rebuild is **two brains on one substrate**, and the whole bet rides on one observation: **direction is the one
expensive thing in learning.** Distributing *which way* each weight should move is what costs; everything else is
cheap. So pay for direction once, where it counts, and get the rest for free.

- **~80% SCFF — the cheap brain.** Self-Contrastive Forward-Forward: local, derivative-free, forward-only, and
  *unsupervised*. No backward pass, no order wall, no labels — every neuron updates from its own activity. It
  organizes the shape of the world on its own. I picked it because it's the only rule I found that is local *and*
  derivative-free *and* forward-only *and* unsupervised all at once — the only one that can actually live on the
  substrate.
- **~20% gradient descent — the precise brain.** SCFF can't put a real *label* on the shapes it finds, so a small
  modern optimizer does: it reads SCFF's features and maps them to classes. Why GD? Because every learning rule ends
  up paying a cost close to full GD on direction anyway, so I pick the one that buys the most accuracy per unit of
  compute.

Around that core, the plan added the machinery to hold it together — a **middle layer** to smooth the seam so GD
doesn't fall off SCFF's drifting features; the **block concept** (chain `[SCFF → middle → GD]` units, each
re-anchoring to a stable label-shape so direction can chain through a local stack); **threshold-gated learning**
(cheap local SCFF most of the time, expensive GD only when error builds past a threshold); and **sleep + a
hippocampus** (a periodic full-batch re-fit over a memory store, so the gated GD doesn't only track what it recently
saw). That was the hypothesis. The point of the phases was to stop arguing it and let the simulations talk. The full
day-one derivation is [`idea/ideas1.md`](idea/ideas1.md); the living decision record is
[`idea/main.ideas.v1.md`](idea/main.ideas.v1.md).

## What the simulations said — Stage 1: the cheap brain (Phases 1–6)

I built the behavioral simulation (numpy, ideal floats) and walked the ladder one rung at a time, under one rule:
**failures are data — never tune until it passes.** Each phase picks up the wound the last one left. The executive
arc is [`src/stage1-report.md`](src/stage1-report.md); one report per phase sits under it.

- **Phase 1 — the cell, and where it wins.** One block generalizes better than backprop (a smaller memorization gap)
  at ~10% of the backward cost — but the sim corrected my day-one optimism: SCFF clusters by **density, not class**.
  It's a weak low-D learner that degrades with depth. The real win was somewhere I hadn't centered: the **continual**
  regime — SCFF's features don't forget, so a cheap **sleep** recovers what online backprop catastrophically loses.
  *(That one wound — density ≠ class — drives the next four phases.)* → [`src/phase1/README.md`](src/phase1/README.md)
- **Phase 2 — depth is not SCFF's lever.** The substrate's cheap axis is depth, but a deep SCFF stack can't earn it —
  and I closed every escape hatch: not transmission, and not the negatives (even a perfect label **oracle** doesn't
  bend the curve). I concluded the wall was "intrinsic to forward-only locality." Depth comes instead from **boosted
  shallow blocks with tiny GD readouts** — which Phase 3 would sharpen. → [`src/phase2/README.md`](src/phase2/README.md)
- **Phase 3 — the objective reframe (the big correction).** The literature caught the one word that was too strong:
  the wall is intrinsic to the **energy objective `Σh²`**, not to locality. Swap energy for a **contrastive
  (InfoNCE)** objective, add my cross-layer **coordination window** (forward-only), and depth composes. **This is
  adopted — it supersedes the energy-goodness SCFF I came back with.** → [`src/phase3/README.md`](src/phase3/README.md)
- **Phase 4 — the capability map.** Instead of improving the cell, I characterized it against a *genuinely-tuned*
  backprop across seven axes. The map says exactly what the project always claimed: a **substrate-native continual
  learner, not a static-accuracy competitor.** It wins continual, nuisance-dimensional input, depth-composition, and
  depth-is-cheap; it trails on raw accuracy and many-class; one honest negative on eval-time noise. It left one wound
  open: past ~layer 5, the representation stops composing and **decays**. → [`src/phase4/README.md`](src/phase4/README.md)
- **Phase 5 — closing out the cheap brain.** The decay isn't dead units or too little width — it's **direction**
  (density ≠ class, a fifth time): deep layers drift off the class manifold once abstraction saturates. And it isn't
  a wall — a *forbidden* full-credit reach composes the whole stack, so the depth is **curable.** Two cheap,
  forward-only levers fix it: a **sharper contrastive temperature** earns the depth back (the readout beats tuned
  backprop; an lr-matched control proves the lift is *direction*, not step-size), and a **short fixed reader** reads
  the useful depth ~8× cheaper than reading every layer. **The cheap brain's learning is finished.**
  → [`src/phase5/README.md`](src/phase5/README.md)
- **Phase 6 — hardening it (a Stage-1 extension).** Before handing the cheap brain to the namer, I hardened it
  against the noise it will meet on silicon. The dangerous enemy turned out to be **directional** (a coherent shift
  along the class axis) — density ≠ class, a sixth time — and the fix is a **noise-corrupted contrastive view**,
  forward-only, which *improves* clean accuracy and keeps the continual win. The cheap brain is done **and
  noise-hard.** → [`src/phase6/README.md`](src/phase6/README.md)

So the spine I came back with survived — two brains, blocks, gate, sleep — but the sims rewrote two of its parts in
my favour: **the SCFF objective** (energy → contrast + coordination) and **what the architecture is *for*** (a
continual learner, not a classifier racing backprop on accuracy). The cheap 80% is done. But it never learned our
labels — it sorts the world into "kinds of things"; it doesn't know which kind is a *3* and which is a *7*. That's
Stage 2.

## What the simulations said — Stage 2: the namer (Phases 7–10)

Stage 2 builds the precise ~20% that puts our names on the frozen cheap brain — read-only, never re-writing SCFF.
The build arc (P7–9) is [`src/stage2-report.md`](src/stage2-report.md); the trial of the frozen object (P10–11) is
[`src/validation-report.md`](src/validation-report.md); the discipline was *freeze in P9, judge in P10.*

- **Phase 7 — the readout is NOT gradient descent.** I raced a taxonomy of namers, and the winner is **RanPAC** — a
  closed-form random-projection + running-Gram ridge head — with a class-balanced-reservoir guard. **No gradient.**
  So the "20% GD" is a *role*, not a *method*: the committed chip's namer is not gradient descent at all. *(The
  experiment said "nah bro, no need GD.")* The spine bends honestly here — the magnitude-reading head out-competes
  the direction-pure one where the bulk has structure. → [`src/phase7/README.md`](src/phase7/README.md)
- **Phase 8 — the economy, run live.** Both brains ran together for the first time. A drift **gate** meters the
  80/20 real (GD is **12%** of substrate energy with the gate on; it *creates* the split), and OURS costs ≈ **half**
  the energy of backprop-with-replay at matched retention. The twist the sim taught: **firing more forgets more** —
  the gate is a *safety* mechanism, not just a cost-saver. → [`src/phase8/README.md`](src/phase8/README.md)
- **Phase 9 — freeze the maintenance loop.** The founding assumption, finally measured: the SCFF bulk **rotates but
  does not forget** (an optimal probe re-fit on the current bulk holds its birth score), so sleep stays cheap. Five
  open knobs tuned against *internal* signals only, then **locked at a commit hash** for Phase 10 to race. → [`src/phase9/README.md`](src/phase9/README.md)
- **Phase 10 — the honest race.** The frozen object raced a fair, budgeted, tuned experience-replay backprop learner,
  verdicts pinned **blind**. It **ties** on the hard home, **trails** on natural digits (it's a continual, not a
  static-accuracy, learner — P4 again), and **wins** continual safety (≈10× less forgetting) and noise (every
  held-out channel). The energy edge over conventional GD is **substrate-realized** (the analog crossbar), not
  algorithmic. **The founding bet, refined not inflated.** → [`src/phase10/README.md`](src/phase10/README.md)

## The verdict, honestly (S14)

A **substrate-native continual learner** — competitive on the continual home, decisively **safer**, far more
**noise-robust**, its energy edge over conventional GD **substrate-realized.** It is *not* a static-accuracy
competitor, and I never optimized it to be one — which is what makes the tie on the home a surprise rather than a
target. And the shape it settled into carries its own punchline: the chip I set out to build as "brain-function,
cheap-implementation" ended with **no gradient descent anywhere** — the cheap brain is forward-only and unsupervised,
and the precise brain turned out to be closed-form. The bet I came back with after the collapse held; the numbers
refined it, and refused to inflate it. The whole self-contained account of the frozen two-brain model is
[`src/phase9-final-architecture.md`](src/phase9-final-architecture.md).

## Where it's going

The neocortex organ is done and validated. **Phase 11 (the limit map) then proved it on real data + scale** — eight
real arenas (real drift streams, a cross-dataset 30-way stream, capacity sweeps), drawn as an honest
win/tie/loss/**FLOOR** map (S15): gas a genuine real-drift win over a per-arena-tuned baseline, the identity holding
where it should and flooring honestly where the data hits its resolution/persistence limit — the red-team "toy data"
strike answered ([`src/phase11/README.md`](src/phase11/README.md)). Next is the **analog-realism layer** — the SPICE
/ PVT / device-noise pass that the whole ladder deferred until the ideal converged (it now has). And beyond the numbered phases is the
target the original 1 a.m. question was always about: a **recurrent, lifelong "thinking" brain** where *correctness
is a self-generated feeling* — the prefrontal↔hippocampus loop that keeps learning its whole life. But simple
intelligence first. That horizon is [`docs/essence/the-essence2.md` §J](../docs/essence/the-essence2.md) and the
[`research/north-star/`](research/north-star/README.md) dossier — held as direction, not the live line.

## Where things live in this folder

| Path | What it is |
| --- | --- |
| [`../docs/essence/the-essence2.md`](../docs/essence/the-essence2.md) | **the soul** — origin, collapse, return, the spine, the person (the *why*). Start here if you want the human story. |
| [`context.md`](context.md) | the full **cold-start context dump** (what / why / how / the person) — for an agent picking this up cold. |
| [`idea/`](idea/README.md) | **the design** — [`ideas1.md`](idea/ideas1.md) (the origin blueprint) · [`main.ideas.v1.md`](idea/main.ideas.v1.md) (the N1–S14 decision record) · [`gd-replan/`](idea/gd-replan/README.md) (the depth-readout hinge into Stage 2). |
| [`src/`](src/README.md) | **the results.** [`README.md`](src/README.md) (the src front door) · the three volumes — `stage1-report.md` (P1–6, the cheap brain) · `stage2-report.md` (P7–9, the namer + the freeze) · `validation-report.md` (P10–11, the frozen object on trial: the fair race + the limit map) · `phase{1..11}/` (per phase: `README` front door · `phaseN-report` story · `RESULTS` ledger · cards + figures) · `phase9-final-architecture.md` (the whole model in one file) · `ref-report/` (the glossary). |
| [`research/survey/`](research/survey/README.md) | the learning-rule survey — the *options* considered (attribution here is draft-5.1 history). |
| [`research/papers/`](research/papers/README.md) | paper stories behind the adopted design — Phase 1–2, Phase 3, Phase 5. |
| [`research/north-star/`](research/north-star/README.md) | the **north-star** dossier (beyond the numbered phases) — free-time reading, *not* the line to walk now. |
