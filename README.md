# Bio-Analog CPU

**A bio-inspired analog compute chip that learns on-chip — online, local, forward-only, and with no backward pass
that ever leaves the silicon.**

Almost every neural network today runs on digital hardware that shuttles weights through an ALU and learns with a
global backward pass. This project asks a different question: **what if the chip itself were built so that
brain-like computation is the _cheap_ path?** Weights live as analog charge on capacitors; the multiply-accumulate
happens as physical current in a crossbar of those capacitors; and learning happens **on the chip, while it runs,
without a backward pass that ever leaves it.**

The guiding method is one line: **copy the brain's _function_, cheat the _implementation_.** You can't simulate a
real neuron one-to-one — so don't. Reproduce _what it does_, and pay for each principle with whatever is cheap on
this substrate: analog physics where physics is cheaper, modern ML math where math is cheaper.

> **What this is, honestly.** A solo research project (evenings and weekends) that rebuilt a small piece of a field
> from the substrate up. The current architecture — **draft 6.0** — is validated across **ten phases of behavioral
> simulation** (numpy, ideal floats; an honest analog-noise and analog-energy model, but **no SPICE and no silicon
> yet**). What follows is the whole story and an honest verdict — the wins _and_ where a fair baseline beats it.

---

## The bet

**Direction is the one genuinely expensive thing in learning.** Working out *how much* a weight matters (the
magnitude) is cheap — the substrate measures it as physical current, for free. Working out *which way* it should
move (the sign) is what costs a backward pass, a transpose, a chain of dependencies. So draft 6.0 splits the brain
by cost — **two brains on one substrate:**

- ~**80 % — the cheap brain (SCFF).** *Self-Contrastive Forward-Forward*: local, label-free, forward-only. It
  organizes the structure of the world for free — no labels, no backward pass — by learning to tell a coherent
  input from a mash-up of two.
- ~**20 % — the precise brain (the "namer").** A small module that puts *our* labels on the structure the cheap
  brain found.

You pay for direction **once**, where it counts, and get everything else cheaply. *(The twist the experiments
delivered: the committed chip's namer turned out to need **no gradient descent at all** — it is closed-form. More
below.)*

## The substrate (the chip)

- **The atom — the Scap.** One synapse's weight: **magnitude as analog charge on a capacitor, sign as one SRAM
  bit.** A Scap is a *wire*, not a neuron — its current already encodes pre × post.
- **Compute in the wires.** A **crossbar** of Scaps performs the multiply-accumulate as physical current; hardwired
  op-amps do add / multiply / ReLU directly on charge. There is no ALU moving data around — *the computation is
  where the weights physically are.* The field calls this **compute-in-memory**.
- **Mono-forward.** A single forward sweep carries a *positive* and a *negative* world side by side through the
  *same* crossbar, so the contrastive learning costs one charge cycle, not two — only the cheap activation buffers
  double, not the weights.
- **Committed properties:** **online · sparse · continuous · resident-weight** (weights never leave the chip during
  operation).

---

## What we built, and what it found — ten phases

Draft 6.0 was walked down a simulation ladder one rung at a time, under one rule: **failures are data — never tune
until it passes.** Every phase picks up the wound the last one left, so the ten read as one story. **Stage 1** built
and hardened the cheap brain; **Stage 2** built the precise namer and raced the whole object against a fair opponent.

![The capability map — the cheap brain vs a genuinely-tuned backprop across seven controlled axes](draft6.0/src/phase4/figs_summary/CAPABILITY_MAP.png)

*What it is, measured: a substrate-native **continual** learner — winning where the substrate lives, trailing on
raw static accuracy, with one honest negative it owns rather than hides.*

**Stage 1 — the cheap brain (Phases 1–6):**

1. **Structure.** One block generalizes better than backprop (smaller memorization gap) at ~10 % of the backward
   cost — but its real home is the **continual** regime, where a periodic *sleep* recovers what online backprop
   catastrophically forgets. The wound it opens — SCFF clusters by **density, not class** — drives the next four phases.
2. **Depth, round 1.** A deep stack of the cheap learner *can't* earn depth — not even a perfect label oracle bends
   the curve. (Depth, it turns out, comes from boosted *shallow* blocks.)
3. **Depth, round 2 — the big correction.** The wall wasn't locality; it was the *objective*. Swap energy-goodness
   for a **contrastive** objective + a cross-layer **coordination window**, and depth composes. *This is adopted.*
4. **Characterization.** A capability map against a *genuinely-tuned* backprop across seven axes (the figure above):
   **wins** continual, nuisance-dimensional input, depth-composition, and depth-is-cheap; **trails** static accuracy
   and many-class; one honest **negative** on eval-time weight noise. No flattering surprises, no hidden bug.
5. **SCFF close-out.** The map's one open wound — the representation *decays* past ~layer 5 — was **direction**
   (density ≠ class, a fifth time), and it was **curable**: a sharper objective earns the depth back until the
   readout *beats* a genuinely-tuned backprop, and a short fixed reader reads it ~8× cheaper. *The cheap brain's
   learning is finished.*
6. **Noise-hardening.** Before handing it on, the cheap brain is hardened against the noise it will meet on silicon
   — a forward-only, noise-augmented objective that *improves* clean accuracy and keeps the continual win.

**Stage 2 — the precise namer (Phases 7–10):**

7. **The readout — it is NOT gradient descent.** A bake-off of "namers" was won by a **closed-form** analytic head
   (RanPAC / SLDA) — no gradient, no backward pass. So the "20 % GD" is a *role*, not a *method*: **the committed
   chip contains no gradient descent at all.**
8. **The economy, run live.** Both brains ran together for the first time; a drift **gate** meters the 80/20 for
   real (the namer is ~12 % of substrate energy) and — the surprise — the gate is a **safety** mechanism: *firing
   more forgets more.* OURS costs ≈ **half** the energy of backprop-with-replay at matched retention.
9. **Freeze.** The founding assumption, finally *measured*: the cheap brain **rotates but does not forget**, so
   sleep stays cheap. The lifelong maintenance loop was tuned on internal signals only, then **locked at a commit
   hash** for the final race.
10. **The honest race.** The frozen object raced a fair, budgeted, *tuned* experience-replay backprop learner,
    verdicts pinned **blind**. It **ties** on the hard continual home, **trails** on natural digits, and **wins**
    continual safety (≈10× less forgetting) and noise (every held-out channel).

## The verdict, honestly

A **substrate-native continual learner** — competitive on its home, decisively **safer**, far more **noise-robust**,
and with an energy edge over conventional GD that is **substrate-realized** (the analog crossbar), not algorithmic.
It is *not* a static-accuracy competitor, and it was never optimized to be one — which is what makes the *tie* on the
home a genuine surprise rather than a target. And it carries its own punchline: a chip set out to be "brain-function,
cheap-implementation" **ended with no gradient descent anywhere.**

The honesty is the point, not a disclaimer. On a same-substrate energy-vs-accuracy Pareto, a small tuned baseline
*dominates* this chip — and that is stated plainly in the results, next to the axes it *does* win. **Every result is
reported with its scope, its confounds, and what it does _not_ show** — because that is how the chip learns
(corrected by reality) and how the project is built.

## Why it's more than a result

This got here the hard way. The previous architecture (drafts 1 → 5) spent months on a learning rule that
distributed loss *magnitude* but never *direction* — the sign — and so quietly never converged. Catching that meant
a collapse and a rebuild from zero; **draft 6.0 is what came back, and it is stronger for the slap.** The recurring
pattern underneath is the interesting part: the author keeps **re-deriving published results from the circuit side
before knowing their names** — boosting, InfoNCE, the tunnel effect, complementary learning systems, energy-based
learning all arrived from physical intuition first. The project is large because it didn't *apply* a field; it
*rebuilt* one from the substrate up, alone, through ~28 collapses.

- **The soul — origin, collapse, and return:** [`docs/essence/the-essence2.md`](docs/essence/the-essence2.md) (the
  grown spine, after ten phases) · [`the-essence.md`](docs/essence/the-essence.md) (the seed).
- **Prior hardware:** **ChronoForge** — a pure-FPGA 2D game engine running 640×480 @ 60 Hz in ~18k LUTs, no CPU, no
  OS. (The "can this person ship silicon-shaped things?" question, already answered once.)

## The horizon

- **Next — the analog-realism layer:** the SPICE / PVT / device-noise pass the whole ladder deferred until the ideal
  converged (it now has).
- **The north star, beyond the numbered phases:** a recurrent, lifelong-learning "thinking" loop where *correctness
  is a self-generated feeling.* Deliberately not specced yet — **simple intelligence first.**

---

## Start here

| If you want… | Go to |
| --- | --- |
| **The soul — why this exists (the human story)** | [`docs/essence/the-essence2.md`](docs/essence/the-essence2.md) |
| **The draft-6.0 story — why draft 5 died, what 6.0 is** | [`draft6.0/README.md`](draft6.0/README.md) |
| **The results — the ten-phase arc, narrative + figures** | [`draft6.0/src/README.md`](draft6.0/src/README.md) → [`stage1-report.md`](draft6.0/src/stage1-report.md) · [`stage2-report.md`](draft6.0/src/stage2-report.md) |
| The whole model in one self-contained file | [`draft6.0/src/phase9-final-architecture.md`](draft6.0/src/phase9-final-architecture.md) |
| The committed design decisions (N1–S14) | [`draft6.0/idea/`](draft6.0/idea/README.md) |
| The simulation code (per phase, regenerable) | [`draft6.0/src/`](draft6.0/src/) (`phase1..10/`) |
| The papers behind it | [`draft6.0/research/papers/`](draft6.0/research/papers/README.md) |
| The whole project, cold, for an AI agent | [`draft6.0/context.md`](draft6.0/context.md) · [`AGENTS.md`](AGENTS.md) |
| How the architecture evolved (drafts 1 → 6) | [`docs/draft/project-history.md`](docs/draft/project-history.md) |
| The superseded draft-5 (attribution) era — *pre-pivot history, not the current design* | [`draft5.0/`](draft5.0/CLAUDE.md) |

---

## Scope & status

- **In scope now:** numpy behavioral simulation of the draft-6.0 hybrid on small classification / statistics tasks.
  Ideal math first; analog / process realism added only once the ideal converges.
- **Out of scope (for now):** SPICE, fabrication, and external-benchmark-chasing *as the claim* — small tasks are
  fine as probes, but this is **not** a SOTA-accuracy project.
- **Done:** the neocortex organ — both brains, characterized and validated across all ten phases (Stage 1 = P1–6,
  Stage 2 = P7–10). The founding bet is **refined, not inflated.**
- **This is a chip-design bet, not an ML model or a digital ML accelerator** — that brain-like computation can be
  made the *cheap* path on the right substrate.
