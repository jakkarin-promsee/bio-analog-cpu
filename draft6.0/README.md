# Draft 6.0 — the live line

> _The post-pivot line (June–July 2026), and the repo's live architecture. This is the **story of the whole build** — why draft 5.x died, what 6.0 turned out to be, and what eleven phases of simulation actually said (some of it overruling the plan, in our favour). The **soul** under all of it — the origin, the collapse, the return, the person — is [`../docs/essence/the-essence2.md`](../docs/essence/the-essence2.md); this page is the **technical companion**. The one-breath pitch and the full benchmark live in the [**root README**](../README.md)._

**What 6.0 is — and what it is not.** Draft 6.0 is the **first organ**: a **baby neocortex** — a cheap unsupervised brain plus a precise namer — built, characterized, frozen, and validated across eleven phases. It is the **stable anchor** that five earlier drafts (1.0 → 5.1) were spent learning how to build, using methods the field already trusts, so the real hypothesis has honest ground to stand on. It is *not* the finished mind. The destination — a whole recurrent brain that thinks to itself — is [where it's going](#where-its-going), held as direction, not yet built. This page is step one of a long program, told in full.

**Jump to:** [the pitch (root README)](../README.md) · [the soul](../docs/essence/the-essence2.md) · [the results (`src/`)](src/README.md) · [the design (`idea/`)](idea/README.md) · [the whole model in one file](src/phase9-final-architecture.md) · [the glossary](src/ref-report/README.md) · [cold-start context](context.md) · [the north star](research/north-star/README.md) · [the folder map ↓](#the-draft-60-folder-in-one-look)

---

## How did we get here?

Draft 6.0 exists because draft 5.0 broke on one missing piece: **direction.** The old learning rule worked out *how much* loss each neuron should absorb — the magnitude — but never *which way* it should move — the sign. Magnitude with no direction can't descend anything, so nothing converged. And patching the sign back in properly would have broken the local-learning core this whole architecture stands on.

So this was a reset, not a patch. The concepts under draft 5.x don't carry forward — we keep the old drafts only as idea references, not as the design. If you're reading `draft6.0/`, this is the design.

It took a rough few days to accept that. But the reset is also what made the target clear again, and the project came back with a completely new plan — the one the rest of this page lays out, and then puts to the test.

## Two weeks later — the deeper lesson

Those first days, the missing sign looked like the whole problem. Two weeks of sitting with it showed it was only the _symptom_. The real hole was deeper — and the only "fix" for the sign was a trap: patching in full 1:1 directional backprop throws away the whole advantage and marches the chip straight back into the summation wall it exists to escape. "Just fix the sign" was never on the table.

Here's what was actually wrong. Draft 5.0 treated the brain as **homogeneous** — one structure repeated everywhere, running one simple rule: attribute-based backpropagation, a stack of linear regressions on axon behavior, and intelligence falls out the top. That picture was so convincing it made _modern ML_ look like the thing that was wrong — brute-forcing computation with an n×n transformer that does everything at once, when real intelligence (the theory went) is continuous, in-chip, and just this one local rule repeated forever.

And the biology wasn't the error. The brain really does run attribute-based backprop, tracked by synapse-history hormones — that part checks out. The problem is we **can't simulate it.** The distribution is cheap; the _direction_ is brutally expensive, and to make the architecture converge it would have had to compute the exact 1:1 directional backprop it was trying to escape. So none of it was usable. Eight months, and the architecture wouldn't move. Nothing was wrong in the parts — the view was just too shallow.

Then it flipped. Modern ML was never trying to brute-force nature — **it's trying to cheat it.** You cannot simulate a real axon — one driver feeding many synapses that slide in 3D, distance itself multiplying the signal, synapses made and destroyed on the fly, many hormones sharing one wire, pulses phase-shifting under myelin, the extracellular fluid holding every spike's whole history. You can't compute that 1:1 across tens of billions of cells. So modern ML doesn't — it **projects** all of it down into a low dimension we _can_ compute. That projection isn't a betrayal of the biology; it's the only honest road to it. (Which is the project's own motto walking back to correct us — _copy the function, cheat the implementation._ It was written down; it just hadn't been believed all the way down.)

And the brutal part: **the brain isn't homogeneous at all.** Every region has its own structure and its own kind of learning. The one-rule-everywhere picture was the real mistake; the missing sign was just where it finally broke. So the project took many steps back — no in-chip memory, no analog ALU, no real circuit yet — and set out to make the core math stable **one organ at a time**, using modern ML to cheat the biology: the **neocortex** first (the SCFF + GD block, the rest of this page), the **hippocampus** as a LUT prototype store standing in until the math tells us its real shape. The heterogeneous-organs worldview is mapped in [`research/north-star/`](research/north-star/README.md); the line we walk first is the smallest stable thing there is — get SCFF + GD to converge.

## The plan we came back with

The rebuild is **two brains on one substrate**, and the whole bet rides on one observation: **direction is the one expensive thing in learning.** Distributing *which way* each weight should move is what costs; everything else is cheap. So pay for direction once, where it counts, and get the rest for free.

- **~80% SCFF — the cheap brain.** Self-Contrastive Forward-Forward: local, derivative-free, forward-only, and *unsupervised*. No backward pass, no order wall, no labels — every neuron updates from its own activity. It organizes the shape of the world on its own. We picked it because it's the only rule that is local *and* derivative-free *and* forward-only *and* unsupervised all at once — the only one that can actually live on the substrate.
- **~20% gradient descent — the precise brain.** SCFF can't put a real *label* on the shapes it finds, so a small modern optimizer does: it reads SCFF's features and maps them to classes. Why GD? Because every learning rule ends up paying a cost close to full GD on direction anyway, so we pick the one that buys the most accuracy per unit of compute. _(Spoiler, from Phase 7: the experiments retired even this — the committed namer is closed-form, no gradient at all.)_

Around that core, the plan added the machinery to hold it together — a **middle layer** to smooth the seam so GD doesn't fall off SCFF's drifting features; the **block concept** (chain `[SCFF → middle → GD]` units, each re-anchoring to a stable label-shape so direction can chain through a local stack); **threshold-gated learning** (cheap local SCFF most of the time, expensive GD only when error builds past a threshold); and **sleep + a hippocampus** (a periodic full-batch re-fit over a memory store, so the gated GD doesn't only track what it recently saw). That was the hypothesis. The point of the phases was to stop arguing it and let the simulations talk. The full day-one derivation is [`idea/ideas1.md`](idea/ideas1.md); the living decision record is [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md).

## What the simulations said — Stage 1: the cheap brain (Phases 1–6)

We built the behavioral simulation (numpy, ideal floats) and walked the ladder one rung at a time, under one rule: **failures are data — never tune until it passes.** Each phase picks up the wound the last one left. The executive arc is [`src/stage1-report.md`](src/stage1-report.md); one report per phase sits under it.

- **Phase 1 — the cell, and where it wins.** One block generalizes better than backprop (a smaller memorization gap) at ~10% of the backward cost — but the sim corrected the day-one optimism: SCFF clusters by **density, not class**. It's a weak low-D learner that degrades with depth. The real win was somewhere we hadn't centered: the **continual** regime — SCFF's features don't forget, so a cheap **sleep** recovers what online backprop catastrophically loses (0.18 → 0.935). *(That one wound — density ≠ class — drives the next four phases.)* → [`src/phase1/README.md`](src/phase1/README.md)
- **Phase 2 — depth is not SCFF's lever.** The substrate's cheap axis is depth, but a deep SCFF stack can't earn it — and every escape hatch was closed: not transmission, and not the negatives (even a perfect label **oracle** doesn't bend the curve). The in-the-moment read: the wall is "intrinsic to forward-only locality." Depth comes instead from **boosted shallow blocks with tiny GD readouts** — which Phase 3 would sharpen. → [`src/phase2/README.md`](src/phase2/README.md)
- **Phase 3 — the objective reframe (the big correction).** P2's verdict was too strong: the wall is intrinsic to the **energy objective `Σh²`**, not to locality. Swap energy for a **contrastive (InfoNCE)** objective, add a cross-layer **coordination window** (forward-only), and depth composes. **This is adopted — it supersedes the energy-goodness SCFF we came back with.** → [`src/phase3/README.md`](src/phase3/README.md)
- **Phase 4 — the capability map.** Instead of improving the cell, we characterized it against a *genuinely-tuned* backprop across seven axes. The map says exactly what the project always claimed: a **substrate-native continual learner, not a static-accuracy competitor.** It wins continual, nuisance-dimensional input, depth-composition, and depth-is-cheap; it trails on raw accuracy and many-class; one honest negative on eval-time noise. It left one wound open: past ~layer 5, the representation stops composing and **decays**. → [`src/phase4/README.md`](src/phase4/README.md)
- **Phase 5 — closing out the cheap brain.** The decay isn't dead units or too little width — it's **direction** (density ≠ class, a fifth time): deep layers drift off the class manifold once abstraction saturates. And it isn't a wall — a *forbidden* full-credit reach composes the whole stack, so the depth is **curable.** Two cheap, forward-only levers fix it: a **sharper contrastive temperature** earns the depth back (the readout beats tuned backprop; an lr-matched control proves the lift is *direction*, not step-size), and a **short fixed reader** reads the useful depth ~8× cheaper than reading every layer. **The cheap brain's learning is finished.** → [`src/phase5/README.md`](src/phase5/README.md)
- **Phase 6 — hardening it.** Before handing the cheap brain to the namer, we hardened it against the noise it will meet on the analog substrate. The dangerous enemy turned out to be **directional** (a coherent shift along the class axis) — density ≠ class, a sixth time — and the fix is a **noise-corrupted contrastive view**, forward-only, which *improves* clean accuracy and keeps the continual win. The cheap brain is done **and noise-hard.** → [`src/phase6/README.md`](src/phase6/README.md)

So the spine we came back with survived — two brains, blocks, gate, sleep — but the sims rewrote two of its parts in our favour: **the SCFF objective** (energy → contrast + coordination) and **what the architecture is *for*** (a continual learner, not a classifier racing backprop on accuracy). The cheap 80% is done. But it never learned our labels — it sorts the world into "kinds of things"; it doesn't know which kind is a *3* and which is a *7*. That's Stage 2.

## What the simulations said — Stage 2: the namer (Phases 7–9)

Stage 2 builds the precise ~20% that puts our names on the frozen cheap brain — read-only, never re-writing SCFF. The build arc (P7–9) is [`src/stage2-report.md`](src/stage2-report.md); the discipline was *freeze in P9, judge in P10.*

- **Phase 7 — the readout is NOT gradient descent.** We raced a taxonomy of namers, and the winner is **RanPAC** — a closed-form random-projection + running-Gram ridge head — with a class-balanced-reservoir guard. **No gradient.** So the "20% GD" is a *role*, not a *method*: the committed chip's namer is not gradient descent at all. *(The experiment said "nah bro, no need GD.")* The spine bends honestly here — the magnitude-reading head out-competes the direction-pure one where the bulk has structure. → [`src/phase7/README.md`](src/phase7/README.md)
- **Phase 8 — the economy, run live.** Both brains ran together for the first time. A drift **gate** meters the 80/20 real (naming is **~12%** of substrate energy with the gate on; the gate *creates* the split), and OURS costs ≈ **half** the energy of backprop-with-replay at matched retention. The twist the sim taught: **firing more forgets more** — the gate is a *safety* mechanism, not just a cost-saver. And a substrate ablation (P8.7): the chip is **15.4×** cheaper than conventional GD-on-digital — **5.4×** from compute-in-memory × **2.9×** from the 80/20. The deployed namer is **SLDA** (metered 69× cheaper than RanPAC, ties on accuracy — resolving P7's cost caveat). → [`src/phase8/README.md`](src/phase8/README.md)
- **Phase 9 — freeze the maintenance loop.** The founding assumption, finally measured: the SCFF bulk **rotates but does not forget** (an optimal probe re-fit on the current bulk holds its birth score), so sleep stays cheap. Five open knobs tuned against *internal* signals only, then **locked at a commit hash** for Phase 10 to race — the freeze caught the one real gap (the P8 sleep cadence was too sparse) and restored near-flat safety at **grid-4** (worst-case forgetting −0.028). → [`src/phase9/README.md`](src/phase9/README.md)

## The trial — the frozen object on real ground (Phases 10–11)

Then the frozen object went on trial — first against a fair opponent, then against real data it never designed. Neither touched a knob. Both are in [`src/validation-report.md`](src/validation-report.md).

- **Phase 10 — the honest race.** The frozen object raced a fair, budgeted, tuned experience-replay backprop learner, verdicts pinned **blind**. It **ties** on the hard home (0.494 vs 0.498), **trails** on natural digits (0.879 vs 0.950 — it's a continual, not a static-accuracy, learner; P4 again), and **wins** continual safety (worst-case forgetting −0.028 vs −0.272, ≈10× less) and noise (every held-out channel, 0.92–1.10 vs 0.23–0.61). The energy edge over conventional GD is **substrate-realized** (the analog crossbar prices the bulk MACs near zero, 3.4×) — *not* algorithmic (same-substrate, the algorithm costs 1.5× more). **The founding bet, refined not inflated.** → [`src/phase10/README.md`](src/phase10/README.md)
- **Phase 11 — the limit map (real data + scale).** The red-team "is it just toy data?" strike, answered with measurements: the frozen object across **8 real arenas × 5 capability channels**, drawn as an honest win/tie/loss/**FLOOR** map. It **wins** real sensor drift (gas, prequential 0.789 ≥ a per-arena-tuned ER's 0.756), holds its safety + order-invariance on real MNIST and a cross-dataset 30-way stream, and **floors honestly** where the labels are so autocorrelated that "guess yesterday" is unbeatable (HAR/electric/covtype). The decomposition names which half is which — the **bulk** is the nonlinear learner (Δbulk +0.417 where data is nonlinear), the **closed-form loop** is the continual safety — and the **analog substrate advantage grows with width (5.4→7.4×).** → [`src/phase11/README.md`](src/phase11/README.md)

## The verdict (S14 · S15)

A **substrate-native continual learner** — competitive on the continual home, decisively **safer**, far more **noise-robust**, its energy edge over conventional GD **substrate-realized** (the analog crossbar), not algorithmic. It is *not* a static-accuracy competitor, and it was never optimized to be one — which is what makes the tie on the home a surprise rather than a target. And the shape it settled into carries its own punchline: the chip set out as "brain-function, cheap-implementation" ended with **no _global_ backward pass anywhere** — the cheap brain learns forward-only (bounded local windowed updates, no cross-layer credit chain), and the precise brain turned out closed-form (no gradient). The bet held; the numbers refined it, and refused to inflate it (S14, the fair race). Then it held **off the toy bench too** — real drift, real pixels, real type-shifts, growing scale — with every loss and floor drawn on the same map (S15, the limit map). The whole self-contained account of the frozen two-brain model is [`src/phase9-final-architecture.md`](src/phase9-final-architecture.md).

## Where it's going

The neocortex organ is **done, frozen, raced, and validated on real data.** That closes the first organ — not the project. The road from here, in order (each stage a gate on the next):

- **Next — the hippocampus organ.** Today the hippocampus is deliberately a stand-in: a pure prototype LUT that stores, evicts, and replays but does not _learn_. Growing it into a **real learning organ** — one that consolidates, generalizes, and knows *which* memories are worth replaying — is the next build, and the first step toward the north star. This runs alongside sharpening the objective function, making the sleep mechanism efficient, and carrying the whole thing to **large-scale data while staying stable** (the named "noise-first" limit from Phase 10 — a bulk that can recover clean structure *itself* from a noisy stream — is one target here).
- **Then — the full cortex, once the minimum brain is stable.** Split the single neocortex into **many objectives** (one specialized bulk per objective function), coordinated by a **large namer** that reads across many SCFF fronts.
- **The analog-realism pass — queued, not next.** The SPICE / PVT / device-noise realism the ladder deferred until the ideal converged (it now has); the named directional/ADC residual from Phase 10 is its first work item. It runs when a result needs it. _A simulation-realism layer, not a fabrication step — no silicon is planned._
- **Last — the loop.** The recurrent, lifelong "thinking" brain the original 1 a.m. question was always about, where *correctness is a self-generated feeling* — the prefrontal↔hippocampus loop that keeps learning its whole life. Deliberately not started yet: build it on organs that are not stable and it is _trash in, trash out._ **Simple intelligence first.**

That horizon is [`docs/essence/the-essence2.md` §J](../docs/essence/the-essence2.md) and the [`research/north-star/`](research/north-star/README.md) dossier — held as direction, not the live line.

---

## The draft 6.0 folder, in one look

```
draft6.0/
├── README.md            ← you are here — the whole-build story (draft 5's death → 6.0 → eleven phases)
├── CLAUDE.md            the draft's operating context + live status (auto-loads when you work in-draft)
├── context.md           the full cold-start context dump (what / why / how / the person)
├── idea/                ★ the design — the committed plan + the decision record
│   ├── ideas1.md            the origin blueprint (full day-one derivation, story form)
│   ├── main.ideas.v1.md     the decision record (N1–N3 + S1–S15) — the committed plan
│   ├── phase4-opinion.md · phase4-problem.md   the Phase-4 reflection that redrew Stage 2
│   └── gd-replan/           the depth-readout hinge into Stage 2 (replan + t0/t3 results)
├── src/                 ★ the results — three report volumes + per-phase records
│   ├── README.md            the src front door (the arc map + the document-system key)
│   ├── stage1-report.md     volume 1 — the cheap brain, built + hardened (P1–6)
│   ├── stage2-report.md     volume 2 — the namer, built + frozen (P7–9)
│   ├── validation-report.md volume 3 — the frozen object on trial (P10–11)
│   ├── phase9-final-architecture.md   ★ the whole two-brain model in one file (frozen, current head)
│   ├── phase{5,6}-final-architecture.md   earlier cheap-brain-only snapshots (kept as bases)
│   ├── phase1/ … phase11/   per phase: README (front door) · phaseN-report · RESULTS · design · expK/ cards · figs
│   └── ref-report/          the glossary the reports cite (methods · metrics · papers)
├── research/            the reading behind the design
│   ├── survey/              the learning-rule survey (the options considered)
│   ├── papers/             paper stories, per phase (phase1-2 · phase3 · phase5 … phase11)
│   └── north-star/         the north-star dossier (beyond the phases — direction, not the live line; + Thai mirror)
└── .claude/             draft-6 skills (status · run-experiment · find-paper · simulator-code)
```

## Where things live — the main documents

| If you want… | Go to |
| --- | --- |
| **The one-page pitch + the full benchmark** | [`../README.md`](../README.md) — the outward-facing front page |
| **The soul** — origin, collapse, return, the person (the *why*) | [`../docs/essence/the-essence2.md`](../docs/essence/the-essence2.md) |
| **The whole model in one self-contained file** | [`src/phase9-final-architecture.md`](src/phase9-final-architecture.md) — both brains + the maintenance loop, frozen |
| **The results**, all of them | [`src/README.md`](src/README.md) → the three volumes (`stage1` · `stage2` · `validation`) → `phase{1..11}/` |
| **The design + the decision record** | [`idea/README.md`](idea/README.md) → [`ideas1.md`](idea/ideas1.md) (blueprint) · [`main.ideas.v1.md`](idea/main.ideas.v1.md) (N1–S15) |
| **The acronym glossary** (SCFF · InfoNCE · RanPAC · SLDA · BWT · …) | [`src/ref-report/README.md`](src/ref-report/README.md) |
| **The full cold-start context** (for an agent picking this up) | [`context.md`](context.md) · [`CLAUDE.md`](CLAUDE.md) |
| **The papers** behind each phase's decisions | [`research/papers/README.md`](research/papers/README.md) — `phase1-2/` … `phase11/` |
| **The learning-rule survey** (the options considered) | [`research/survey/README.md`](research/survey/README.md) |
| **The north star** — the recurrent thinking-brain destination | [`research/north-star/README.md`](research/north-star/README.md) — direction, not the line to walk now |
