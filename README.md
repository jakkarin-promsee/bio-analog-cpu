# Bio-Analog CPU

**A bio-inspired analog compute substrate that learns on-chip — online, local, and forward-only.**

Most neural networks run on digital hardware that shuttles weights through an ALU and learns with a global
backward pass. This project asks a different question: *what if the chip itself were built so that brain-like
computation is the **cheap** path?* Weights live as analog charge on capacitors; the multiply-accumulate happens
as physical current in a crossbar of those capacitors; and learning happens **on the chip, while it runs, without
a backward pass that ever leaves it.**

The guiding method is one line: **copy the brain's *function*, cheat the *implementation*.** You can't simulate a
real neuron one-to-one — so don't. Reproduce *what it does*, and pay for each principle with whatever is cheap on
this substrate: analog physics where physics is cheaper, modern ML math where math is cheaper.

> **Status — draft 6.0 (June 2026).** Stage 1, the first organ, is built and characterized in **behavioral
> simulation** (numpy, ideal floats). This is the math-stabilization phase: **no SPICE, no silicon yet.**

---

## The core idea

**The atom — the Scap.** One synapse's weight, stored as analog charge on a capacitor (the magnitude) plus a
single SRAM bit (the sign). Compute happens *in the wires*: a crossbar of Scaps performs the multiply-accumulate
as physical current, and hardwired op-amps do add / multiply / ReLU directly on charge. There is no ALU moving
data around — the computation is *where the weights physically are*. The four committed properties are **online,
sparse, continuous, and resident-weight** (weights never leave the chip during operation) — what the field calls
**compute-in-memory**.

**Two brains, an 80/20 split.** Learning is divided by cost, because **direction — *which way* each weight should
move — is the one genuinely expensive thing in learning.**

- ~**80%** is a cheap, unsupervised front — **SCFF** (Self-Contrastive Forward-Forward): local, label-free,
  forward-only. It organizes the structure of the world for free, with no backward pass.
- ~**20%** is a small, precise **gradient-descent** namer that maps those features onto real labels.

So you pay for direction *once*, where it counts, and get everything else cheaply. A single **mono-forward** sweep
even carries a positive and a negative "world" side by side through the *same* crossbar, so the contrastive
learning costs one charge cycle, not two.

---

## Where it stands — Stage 1

Draft 6.0's first organ — the SCFF + gradient-descent "neocortex" cell — has been built and characterized across
four phases of behavioral simulation. The headline:

**It is a substrate-native *continual* learner — not a static-accuracy competitor.** That is exactly what the
substrate is *for*, and the experiments say it plainly:

![Stage-1 capability map](draft6.0/src/phase4/figs_summary/CAPABILITY_MAP.png)

*The cheap, forward-only brain measured against a genuinely-tuned backprop ceiling across seven controlled axes.*

- **Wins where the substrate lives:** continual learning (a periodic "sleep" recovers what online backprop
  *catastrophically forgets*), high-nuisance-dimension input, depth-composition, and depth-is-cheap — its backward
  cost stays flat as the network deepens, where backprop's grows linearly.
- **Trails, by design:** raw static accuracy and many-class problems — the cost of being a *structure* learner with
  a cheap namer, rather than a global error-minimizer.
- **One honest negative:** it is *not* (yet) robust to eval-time weight noise — a real tradeoff, owned rather than
  hidden.

The four-phase arc, in one breath: **build the cell and find its home** (continual) → **find that stacking the
cheap learner deep can't earn depth** → **discover the real lever was the learning *objective*, not the locality**
(swap energy-goodness for a contrastive objective + cross-layer coordination, and depth composes) → **map the whole
capability honestly.** Every step was decided by a simulation or a paper overruling the plan, never by tuning until
it passed.

The full, reader-facing write-up lives in **[`draft6.0/src/stage1-report.md`](draft6.0/src/stage1-report.md)**.

---

## Start here

| If you want… | Go to |
| --- | --- |
| The whole picture, cold | [`draft6.0/context.md`](draft6.0/context.md) |
| Why draft 5 died and what 6.0 is | [`draft6.0/README.md`](draft6.0/README.md) |
| The Stage-1 results — narrative + figures | [`draft6.0/src/stage1-report.md`](draft6.0/src/stage1-report.md) → the four `phaseN-report.md` |
| The committed design decisions | [`draft6.0/idea/main.ideas.v1.md`](draft6.0/idea/main.ideas.v1.md) |
| The simulation code (per phase, regenerable) | [`draft6.0/src/`](draft6.0/src/) (`phase1..4/`) |
| The papers behind it | [`draft6.0/research/papers/`](draft6.0/research/papers/) |
| The soul of the project — why it exists | [`docs/essence/the-essence.md`](docs/essence/the-essence.md) |
| The superseded draft-5 (attribution) era — *pre-pivot history, not the current design* | [`draft5.0/`](draft5.0/) |

---

## Scope & roadmap

- **In scope now:** Python behavioral simulation of the draft-6.0 hybrid on small classification / statistics
  tasks. Ideal math first; analog / process realism added only once the ideal converges.
- **Out of scope (for now):** SPICE, fabrication, and external-benchmark-chasing *as the claim* — small tasks are
  fine as probes, but this is not a SOTA-accuracy project.
- **Next — Phase 5:** optimize the maintenance loop (the sleep cadence + a learning-rate gate) against this cell's
  measured drift, and run the hardware-relevant noise tests.
- **The north star, beyond the numbered phases:** a recurrent, lifelong-learning "thinking" loop where
  *correctness is a self-generated feeling*. Deliberately not specced yet — simple intelligence first.

---

## Background

This is an independent, solo research project, built on evenings and weekends. It is **not** a machine-learning
model or a digital ML accelerator — it's a chip-design bet that brain-like computation can be made the *cheap* path
on the right substrate.

It got here the hard way. The previous architecture (drafts 1→5) spent months on a learning rule that distributed
loss *magnitude* but never *direction* — the sign — and so quietly never converged. Catching that meant a collapse
and a rebuild from zero; draft 6.0 is what came back, and it is stronger for the slap. The full story — origin,
collapse, and return — is in [`docs/essence/the-essence.md`](docs/essence/the-essence.md). *(Prior hardware
background: **ChronoForge**, a pure-FPGA 2D game engine running 640×480 @ 60 Hz in ~18k LUTs — no CPU, no OS.)*

One rule governs everything here, and it's worth stating up front: **failures are data; we never tune until it
works.** Every result is reported with its scope, its confounds, and what it does *not* show. That honesty is the
point — it's how the chip learns (corrected by reality), and it's how the project is built.
