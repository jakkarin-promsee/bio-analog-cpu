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

## The bet

**Direction is the one genuinely expensive thing in learning.** Working out _how much_ a weight matters (the
magnitude) is cheap — the substrate measures it as physical current, for free. Working out _which way_ it should
move (the sign) is what costs a backward pass, a transpose, a chain of dependencies. So draft 6.0 splits the brain
by cost — **two brains on one substrate:**

- ~**80 % — the cheap brain (SCFF).** _Self-Contrastive Forward-Forward_: local, label-free, forward-only. It
  organizes the structure of the world for free — no labels, no backward pass — by learning to tell a coherent
  input from a mash-up of two.
- ~**20 % — the precise brain (the "namer").** A small module that puts _our_ labels on the structure the cheap
  brain found.

You pay for direction **once**, where it counts, and get everything else cheaply. _(The twist the experiments
delivered: the committed chip's namer turned out to need **no gradient descent at all** — it is closed-form. More
below.)_

Ten phases of behavioral simulation later, the architecture is **finished, frozen, and raced.** The whole benchmark
is below — the wins, the mechanism behind them, and the losses, stated just as plainly. **Stop at the end of the
showcase and you have the shape of the project; or descend the reading ladder at the bottom, layer by layer, as
deep as you want.**

---

## The showcase — one frozen chip vs tuned backprop, from every angle

The proving ground is **continual learning**: data arrives as a stream, the world keeps shifting, and nothing is
ever revisited as a training set. This is the regime that makes ordinary backprop **catastrophically forget** — and
it is where this architecture lives.

The fight was built to be attacked:

- **The contender — OURS (grid-4)** — is the committed two-brain object: a 12-layer **forward-only, unsupervised
  bulk** that learns from every input, plus a tiny **closed-form "namer"** that fires only when a drift gate trips
  and is consolidated by a periodic _sleep_ (every 4 stream segments — that's the "grid-4"). **No gradient descent
  anywhere in it.** It was **frozen at a commit hash before any baseline number existed** and raced untouched.
- **The opponent — ER-strong** — is _not a straw man_: experience-replay backprop, the baseline the
  continual-learning literature says beats the fancy methods, **byte-matched** to OURS's memory (196,800 B),
  **tuned on a held-out seed** with its own validation split, and given its own best architecture.
- **The referee** — verdict shapes pinned **blind** before the racer ran; 5 seeds; a tie band δ = 0.02 declared up
  front; 14 bit-exact reproducibility guards green on every rung. _Freeze first, judge second._

### The money figure — five shifting worlds, no catastrophic forgetting

Five digit-recognition worlds arrive in sequence — identity → permuted → rotated → covariate-shifted → noised —
each overwriting the last. The learner has to keep _all five_, without re-storing the old worlds as training data.

All five are the **same ten handwritten digits** (8×8 images, pixels scaled to [0, 1]) — what changes is the lens
the world is seen through. Per image `x`:

| # | World | Transform | What it does to the learner |
| --- | --- | --- | --- |
| 1 | **identity** | `x′ = x` | the clean world — the pure digit shapes, undistorted |
| 2 | **permuted** | `x′[i] = x[π(i)]` — one frozen random shuffle `π` of the 64 pixel positions | every spatial neighborhood destroyed; the information is all still there, the *layout* is alien |
| 3 | **rotated** | `x′ = rot90(x)` — the 8×8 image turned 90° | the same shapes in a new orientation |
| 4 | **covariate** | `x′ = 3·x + 4` | a global gain + offset (a lighting / sensor shift); per-sample normalization removes it by construction — a raw net has to learn around it |
| 5 | **noised** | `x′ = x + 0.6·ε`, `ε ~ N(0, 1)` per pixel | iid Gaussian at RMS 0.6 against a [0, 1] signal — the digit drowned in noise as large as itself |

_(Every domain then passes through the same frozen random projection to the bulk's 40-D input, and the ten class
labels never change — true domain-incremental learning: one shared head, five lenses.)_

This table is the key to reading the forward and reversed graphs below. **Forward** is the merciful curriculum:
learn the clean `x′ = x` world first, then meet each distortion as a variation on shapes you already know.
**Reversed** is the cruel one: build your *first* representation inside the noise-drowned world 5, then walk toward
data you have never once seen clean. Testing both orders is the difference between a learner that memorized a
curriculum and one that extracts structure from whatever arrives.

![The multi-domain gauntlet — OURS holds retention nearly flat across five shifting worlds while the tuned replay-backprop baseline sags mid-stream](draft6.0/src/phase10/exp3/figs_p10_3/GAUNTLET.png)

_The checkpoint read: worst-moment accuracy over all worlds seen so far (top) and cumulative metered energy
(bottom), OURS's cadence family vs ER-strong. (n = 5 seeds, median + IQR.)_

- **Steadier retention.** OURS holds worst-point all-previous accuracy at **0.490** across the whole stream; the
  tuned backprop baseline sags to **0.350** mid-gauntlet as it chases the newest world. Anytime accuracy **0.519 vs
  0.433** — and the final scores still _tie_ (0.490 vs 0.504, inside δ).
- **Despite a handicap.** OURS runs one frozen configuration across all five worlds; ER got its own best tuned
  config. A frozen substrate held steadier than a tuned end-to-end learner.

One figure can be luck. So the same result was attacked four more times — same story, four different angles.

### Angle 2 — batch by batch: the crash-and-relearn cycle, made visible

The checkpoint read above samples the stream at domain ends. Zoom in to **every single batch** and you see _why_
the lines differ — the mechanism, not just the score:

![The per-batch stream view — ER saw-tooths at every domain switch while OURS rides flat](draft6.0/src/phase10/exp3/figs_p10_3/GAUNTLET_STREAM.png)

_Thick lines = accuracy over all domains seen so far; thin lines = accuracy on the live batch; grey ticks = sleeps
and domain boundaries._

ER's line **crashes at every domain onset and re-climbs** — the saw-tooth of an end-to-end learner re-fitting its
whole representation to each new world (its live-batch accuracy dives to ~0.1 on arrival, mean 0.273 across the
stream). OURS barely moves (live mean 0.469): the unsupervised bulk extracts structure from whatever arrives, and
the namer re-anchors at each sleep. **ER buys its slightly higher final score with a crash-and-relearn cycle at
every switch; the steadiness is OURS's product.** The bottom panel is the exact per-batch energy — OURS a sleep
_staircase_, ER a smooth every-step ramp.

### Angle 3 — reverse the world order: the opponent collapses, ours doesn't care

Run the identical gauntlet **backwards** — the noise-drowned world (`x′ = x + 0.6·ε`) first, so the learner must
build its first representation of digits it has **never seen clean**:

![The reversed gauntlet — ER never recovers from a hard-first curriculum; OURS lands at the same endpoint either way](draft6.0/src/phase10/exp3/figs_p10_3/GAUNTLET_STREAM_REV.png)

**ER never recovers: 0.504 forward → 0.343 reversed.** Its network and its replay buffer are shaped by noise early,
and every later world is learned on that damaged base. **OURS lands at the same endpoint either way (0.490 forward,
0.494 reversed)** — the bulk extracts structure even from an all-noisy opener, and each sleep re-anchors the namer.
The forward gauntlet, it turns out, was ER's _favorable_ ordering — and a lifelong learner does not get to choose
the order the world arrives in.

### Angle 4 — break the schedule: no hidden luck in the sleep timing

The committed stream hid one structural convenience: the domain length (24 steps) exactly equaled the sleep period,
so every sleep landed on a domain's final step — one perfectly-timed consolidation before every switch. If the flat
line depended on that, the money figure would be part scheduling luck. So the alignment was **broken on purpose**:
long randomized domain lengths, sleeps landing mid-domain, plus an aligned-length control to separate "alignment
broke" from "domains got longer":

![The alignment-break view — sleeps land mid-domain and OURS rides flat as ever; ER re-converges given long stationary blocks](draft6.0/src/phase10/exp3/figs_p10_3/GAUNTLET_STREAM_LONG.png)

**Sleep/boundary alignment is a non-factor** — the aligned control ties the misaligned run at a paired gap of
**+0.002**, and OURS's retention _rises_ with the longer worlds (0.533). And this angle bought the **honest scope
line, which is the point rather than a footnote**: given ~68 steps per world, ER has time to fully re-converge
before every checkpoint and finishes higher (0.675). **The retention win belongs to the rapid-switch regime** —
where the world shifts faster than a plastic learner can re-fit. What never moves, in any layout tested, is OURS
itself: order-invariant, alignment-invariant, live line never crashing at a switch.

### Angle 5 — reverse _and_ lengthen: the mechanism, predicted and tested

In the reversed views, OURS's line shows a signature: it sags _within_ each block, then snaps back up at each
sleep. The mechanism claim: the namer's frozen frame goes **stale** while the bulk keeps learning underneath it —
so a sleep landing _mid-domain_ should catch the sag mid-fall and pull it back. That is a falsifiable prediction,
and the reversed-long layout tests it (2–3 sleeps now land inside every world):

![The reversed-long view — mid-domain sleeps catch the sag and pull it back, around a rising floor](draft6.0/src/phase10/exp3/figs_p10_3/GAUNTLET_STREAM_REVLONG.png)

Mid-domain sleeps **rescue the sag — 5/5 seeds** (median jump +0.052 at each sleep tick), the floors between sleeps
_climb_ instead of running down, and OURS is order-invariant at the long scale too (0.527 vs 0.533). Banked with
this project's usual discipline as _supported, not confirmed_ — one confirming sub-cut was mis-specified and is
flagged rather than papered over. ER, meanwhile, stays order-sensitive even at length (0.580 reversed vs 0.675
forward).

And the reversed runs also name **the architecture's own honest limit** — look at where the green line _lives_ in
both reversed figures. When the model never sees the pure world first, it does not collapse the way ER does — the
endpoint is order-invariant — but it runs **thinner**: noisy world to noisy world offers far less pattern to anchor
on, so the representation grown there holds its classes on thin margins, the between-sleep sags run deeper, and the
whole curve has to climb from lower ground. The sleeps rescue it; the margins only widen as clean-ish structure
finally accumulates. **That names the next capability this project goes after: a bulk that can recover the pure
structure _by itself_ from a noisy stream** — the clean data it was never given — so the accuracy holds stable no
matter what order the real world serves. A deployed chip does not get a merciful curriculum.

**Five angles, one story: the retention result is real — mechanism visible, order-proof, schedule-proof, and
honestly scoped — and the one place it runs thin is named, with the next phase pointed at it.** The full narrative behind all five figures:
[`draft6.0/src/phase10/phase10-report.md`](draft6.0/src/phase10/phase10-report.md) §P10.3.

---

## The rest of the benchmark — every axis, wins and losses

The gauntlet is the showcase; Phase 10 measured the whole object on every axis it claims (and two it loses).

### The head-to-head fight on the lifelong home

![The existential fight — OURS ties the tuned ER on accuracy, far above the rest of the field, at 10× less worst-case forgetting](draft6.0/src/phase10/exp1/figs_p10_1/FIGHT.png)

On the long lifelong stream the raw accuracy is a **tie** (0.494 vs 0.498, inside δ; OURS wins 3/5 seeds) — both
far above the rest of the continual-learning field (A-GEM 0.320, DER++ 0.360, naive backprop 0.308) and below the
offline joint-training ceiling (0.870). The real separation is **worst-case forgetting: −0.028 vs −0.272** — the
tuned ER recovers by stream-end (which is what final-score reads hide), but mid-stream it forgets **≈10×** more.
For anything that has to _stay_ reliable while it learns, that is the number that matters.

### Noise — wins every held-out channel

The chip will live on analog hardware, so it was noise-hardened during training (Phase 6) and then tested on a
**held-out** noise battery — levels and channels disjoint from anything used to tune:

![The noise showcase — OURS holds 0.92–1.10 retention on every held-out channel while BP+replay collapses](draft6.0/src/phase10/exp4/figs_p10_4/NOISE_SHOWCASE.png)

OURS holds **0.92–1.10 retention on every channel** — and actually _improves_ under iid noise, a side-effect of the
noise-augmented training objective — while the same BP+replay opponent collapses to **0.23–0.61**. A small residual
on the directional/ADC channels is **named, not hidden**: it is the first work item of the upcoming device-physics
(SPICE/PVT) layer.

### Energy — the honest "why analog"

![The substrate 2×2 — the chip runs ~3.5× under conventional GD-on-digital; the algorithm alone does not win same-substrate](draft6.0/src/phase10/exp3/figs_p10_3/SUBSTRATE.png)

Both learners were metered on both substrates, and the decomposition is stated the uncomfortable way around: **on
the same digital substrate the algorithm _loses_** (≈1.5× more energy — a 12-layer bulk forwarded on every input is
not free against a small tuned net), and **the chip wins ≈3.4× because the analog crossbar prices those bulk MACs
near zero.** The energy edge is **substrate-realized** — it is a _chip_ claim, not an algorithm claim, and every
document in this repo says so. That is precisely the "why analog": this architecture is the one that _needs_ the
crossbar, and the crossbar is what makes it cheap.

### The Pareto — the loss, plotted in public

![The Pareto verdict — on accuracy × energy a small tuned ER dominates; OURS's wins live on axes this plot doesn't have](draft6.0/src/phase10/exp6/figs_p10_6/PARETO.png)

On a plain (accuracy × energy) frontier, a small tuned ER **dominates** this chip — higher accuracy _and_ lower
same-substrate energy. That is reported as loudly as the wins, because it sharpens what the object actually is: its
genuine advantages — worst-case safety, noise survival, the substrate floor — **live on axes this plot does not
have.** The numbered line sweeping the top is OURS's whole operating range along its _one_ runtime dial (the sleep
cadence, declared up front, never used to cherry-pick): a ~0.49-accuracy plateau with its two cliffs mapped — safety
plunges past grid-6, accuracy cliffs at grid-16
([`phase10-report.md`](draft6.0/src/phase10/phase10-report.md) §P10.2).

### The scorecard

| Axis                                      | OURS (grid-4)            | Best fair opponent             | Verdict                            |
| ----------------------------------------- | ------------------------ | ------------------------------ | ---------------------------------- |
| Final accuracy — continual home           | 0.494                    | ER-strong 0.498                | **tie** (inside δ)                 |
| Worst-case forgetting — lifelong          | **−0.028**               | ER-strong −0.272               | **win** (≈10× safer)               |
| Worst-point retention — 5-domain gauntlet | **0.490**                | ER-strong 0.350                | **win** (rapid-switch regime)      |
| Order-robustness — reversed gauntlet      | **0.494** (vs 0.490 fwd) | ER-strong 0.343 (vs 0.504 fwd) | **win** (order-invariant)          |
| Noise retention — held-out battery        | **0.92–1.10**            | BP+replay 0.23–0.61            | **win** (every channel)            |
| Final accuracy — easy natural digits      | 0.879                    | ER-strong 0.950                | **loss** (not a static competitor) |
| Energy — same digital substrate           | 3.46e8 pJ                | ER-strong 2.25e8 pJ            | **loss** (1.5×, the deep bulk)     |
| Energy — chip vs conventional GD          | **6.70e7 pJ (analog)**   | ER-on-digital 2.25e8 pJ        | **win** (3.4×, substrate-realized) |

**And what this does _not_ claim** — the scope is part of the result:

- **Not a static-accuracy competitor.** On short, easy, stationary data a tuned backprop simply wins (0.950 vs
  0.879 on natural digits) — there is nothing there for the sleep loop to protect. This chip's accuracy value is
  _lifelong stability on hard, long, shifting streams_.
- **The retention win is switch-frequency-scoped.** Give the world long stationary stretches and a plastic learner
  re-converges (Angle 4). The claim is exactly what a continual-learning substrate should claim, and no more.
- **The algorithm alone does not win the energy race** — the substrate does. Same-substrate, OURS costs 1.5× more.
- **Behavioral simulation only** — numpy, ideal floats, an honest analog-noise and analog-energy model
  (ADC-centred, literature-calibrated), but **no SPICE and no silicon yet**. That layer is next.

_That's the result. Below: what the chip is, how ten phases got it there, and where to read deeper — stop here and
you have the shape of it, or descend._

> **What this is, honestly.** A solo research project (evenings and weekends) that rebuilt a small piece of a field
> from the substrate up. The current architecture — **draft 6.0** — is validated across **ten phases of behavioral
> simulation** (~60 controlled experiments, 5 seeds each, every figure regenerable from saved arrays). What follows
> is the whole story, told with the same discipline as the benchmark above: failures are data, scope is part of the
> claim.

---

## The substrate (the chip)

- **The atom — the Scap.** One synapse's weight: **magnitude as analog charge on a capacitor, sign as one SRAM
  bit.** A Scap is a _wire_, not a neuron — its current already encodes pre × post.
- **Compute in the wires.** A **crossbar** of Scaps performs the multiply-accumulate as physical current; hardwired
  op-amps do add / multiply / ReLU directly on charge. There is no ALU moving data around — _the computation is
  where the weights physically are._ The field calls this **compute-in-memory**.
- **Mono-forward.** A single forward sweep carries a _positive_ and a _negative_ world side by side through the
  _same_ crossbar, so the contrastive learning costs one charge cycle, not two — only the cheap activation buffers
  double, not the weights.
- **Committed properties:** **online · sparse · continuous · resident-weight** (weights never leave the chip during
  operation).

## The machine that ran the race

The committed object, part by part — every one of these was _chosen by an experiment_, not assumed:

- **The bulk:** 12 layers of SCFF under a sharpened contrastive objective (InfoNCE, two views, temperature 0.2, a
  2-layer coordination window), with one view noise-corrupted during training. Forward-only, label-free, learns
  from **every** input, never written to by anything downstream.
- **The namer:** **SLDA** — closed-form streaming class prototypes over the bulk's features. No gradient, no
  backward pass; metered **69× cheaper** than the runner-up, and it _ties_ gradient-trained heads on accuracy.
- **The gate:** a drift detector decides when the namer fires at all. Metered live, naming is ~11–18 % of substrate
  energy — the 80/20 is _real_, and the gate turned out to be a **safety** mechanism: firing more forgets more.
- **The sleep:** every 4 stream segments, a closed-form re-fit of the namer over a small prototype memory (the
  "hippocampus LUT", class-balanced eviction) re-anchors the labels to wherever the bulk has rotated to.

_The whole model — every part, every equation, every decision that chose it — in one self-contained file:_
[`draft6.0/src/phase9-final-architecture.md`](draft6.0/src/phase9-final-architecture.md).

## What we built, and what it found — ten phases

Draft 6.0 was walked down a simulation ladder one rung at a time, under one rule: **failures are data — never tune
until it passes.** Every phase picks up the wound the last one left, so the ten read as one story. **Stage 1** built
and hardened the cheap brain; **Stage 2** built the precise namer and raced the whole object against a fair opponent.

![The capability map — the cheap brain vs a genuinely-tuned backprop across seven controlled axes](draft6.0/src/phase4/figs_summary/CAPABILITY_MAP.png)

_What it is, measured (Phase 4): a substrate-native **continual** learner — winning where the substrate lives,
trailing on raw static accuracy, with one honest negative it owns rather than hides._

**Stage 1 — the cheap brain (Phases 1–6):**

1. **Structure.** One block generalizes better than backprop (smaller memorization gap) at ~10 % of the backward
   cost — but its real home is the **continual** regime, where a periodic _sleep_ recovers what online backprop
   catastrophically forgets. The wound it opens — SCFF clusters by **density, not class** — drives the next four phases.
2. **Depth, round 1.** A deep stack of the cheap learner _can't_ earn depth — not even a perfect label oracle bends
   the curve. (Depth, it turns out, comes from boosted _shallow_ blocks.)
3. **Depth, round 2 — the big correction.** The wall wasn't locality; it was the _objective_. Swap energy-goodness
   for a **contrastive** objective + a cross-layer **coordination window**, and depth composes. _This is adopted._
4. **Characterization.** A capability map against a _genuinely-tuned_ backprop across seven axes (the figure above):
   **wins** continual, nuisance-dimensional input, depth-composition, and depth-is-cheap; **trails** static accuracy
   and many-class; one honest **negative** on eval-time weight noise. No flattering surprises, no hidden bug.
5. **SCFF close-out.** The map's one open wound — the representation _decays_ past ~layer 5 — was **direction**
   (density ≠ class, a fifth time), and it was **curable**: a sharper objective earns the depth back until the
   readout _beats_ a genuinely-tuned backprop, and a short fixed reader reads it ~8× cheaper. _The cheap brain's
   learning is finished._
6. **Noise-hardening.** Before handing it on, the cheap brain is hardened against the noise it will meet on silicon
   — a forward-only, noise-augmented objective that _improves_ clean accuracy and keeps the continual win.

**Stage 2 — the precise namer (Phases 7–10):**

7. **The readout — it is NOT gradient descent.** A bake-off of "namers" was won by a **closed-form** analytic head
   (RanPAC / SLDA) — no gradient, no backward pass. So the "20 % GD" is a _role_, not a _method_: **the committed
   chip contains no gradient descent at all.**
8. **The economy, run live.** Both brains ran together for the first time; a drift **gate** meters the 80/20 for
   real (the namer is ~12 % of substrate energy) and — the surprise — the gate is a **safety** mechanism: _firing
   more forgets more._ Against the like-for-like BP+replay it was metered on, OURS cost ≈ **half** the energy —
   _(Phase 10's smaller, harder-tuned ER later flips that same-substrate cut to the 1.5× loss in the scorecard,
   which is exactly why the energy claim is banked as substrate-realized, not algorithmic.)_
9. **Freeze.** The founding assumption, finally _measured_: the cheap brain **rotates but does not forget**, so
   sleep stays cheap. The lifelong maintenance loop was tuned on internal signals only, then **locked at a commit
   hash** for the final race.
10. **The honest race.** Everything in the showcase above — the frozen object vs a fair, budgeted, _tuned_
    experience-replay backprop, verdicts pinned **blind**. It **ties** on the hard continual home, **trails** on
    natural digits, and **wins** continual safety (≈10× less forgetting), the gauntlet, and noise (every held-out
    channel).

## The verdict, honestly

A **substrate-native continual learner** — competitive on its home, decisively **safer**, far more **noise-robust**,
and with an energy edge over conventional GD that is **substrate-realized** (the analog crossbar), not algorithmic.
It is _not_ a static-accuracy competitor, and it was never optimized to be one — which is what makes the _tie_ on the
home a genuine surprise rather than a target. And it carries its own punchline: a chip set out to be "brain-function,
cheap-implementation" **ended with no gradient descent anywhere.**

The honesty is the point, not a disclaimer. On a same-substrate energy-vs-accuracy Pareto, a small tuned baseline
_dominates_ this chip — and that is plotted above, next to the axes it _does_ win. **Every result is reported with
its scope, its confounds, and what it does _not_ show** — because that is how the chip learns (corrected by reality)
and how the project is built.

## Why it's more than a result

This got here the hard way. The previous architecture (drafts 1 → 5) spent months on a learning rule that
distributed loss _magnitude_ but never _direction_ — the sign — and so quietly never converged. Catching that meant
a collapse and a rebuild from zero; **draft 6.0 is what came back, and it is stronger for the slap.** The recurring
pattern underneath is the interesting part: the author keeps **re-deriving published results from the circuit side
before knowing their names** — boosting, InfoNCE, the tunnel effect, complementary learning systems, energy-based
learning all arrived from physical intuition first. The project is large because it didn't _apply_ a field; it
_rebuilt_ one from the substrate up, alone, through ~28 collapses.

- **The soul — origin, collapse, and return:** [`docs/essence/the-essence2.md`](docs/essence/the-essence2.md) (the
  grown spine, after ten phases) · [`the-essence.md`](docs/essence/the-essence.md) (the seed).
- **Prior hardware:** **ChronoForge** — a pure-FPGA 2D game engine running 640×480 @ 60 Hz in ~18k LUTs, no CPU, no
  OS. (The "can this person ship silicon-shaped things?" question, already answered once.)

## The horizon

- **Next — the analog-realism layer:** the SPICE / PVT / device-noise pass the whole ladder deferred until the ideal
  converged (it now has). The named directional/ADC residual from the noise showcase is its first work item.
- **Next, beside it — the noise-first limit (named by Angle 5):** a representation grown without ever seeing clean
  data runs on thin margins. The capability target: a bulk that recovers the pure structure _itself_ from a noisy
  stream, so accuracy stays stable no matter what order the world arrives in.
- **The north star, beyond the numbered phases:** a recurrent, lifelong-learning "thinking" loop where _correctness
  is a self-generated feeling._ Deliberately not specced yet — **simple intelligence first.**

---

## The project in one look

```
Bio-AnalogCPU/
├── README.md              ← you are here — the front page
├── CLAUDE.md · AGENTS.md  the agent operating context (how to work in this repo)
├── docs/
│   ├── essence/           the soul — the-essence2.md (the grown spine) + the-essence.md (the seed)
│   └── draft/             the project history, drafts 1 → 6
├── draft6.0/              ★ the live line — the validated architecture
│   ├── README.md          the draft's whole story (why 5 died, what 6.0 is)
│   ├── context.md         the cold-start dump for an agent
│   ├── idea/              the design + the N1–S14 decision record
│   ├── research/          the papers behind it (+ the north-star dossier)
│   └── src/               ★ the results: stage{1,2} reports · phase1..11/ · phase9-final-architecture.md
├── draft5.0/              the superseded attribution era (pre-pivot history)
├── draft-journey/         every earlier draft (1.0 → 5.1) in full
└── post/                  build-in-public writeups
```

**The eleven-phase arc, one line:** P1 structure · P2 the depth-wall · P3 the objective-reframe (contrast supersedes
energy) · P4 the capability map · P5 depth cured · P6 noise-hardened — _the cheap brain, Stage 1_ — then P7 the
readout (it is **not** gradient descent) · P8 the economy (the gate is _safety_) · P9 freeze · P10 the honest race —
_the namer, Stage 2_ — → **the verdict, S14** — then P11 **the limit map** takes the frozen object to real data +
scale (the red-team answer: real streams, gas a genuine win, honest floors) → **S15.** Discipline throughout:
_freeze in P9, judge in P10._

---

## Start here — the reading ladder

Every layer is written to be a valid stopping point: each one gives a true, complete picture at its own depth, and
each one links down to the next. Descend only as far as you care to.

| Depth | Read                                                                                                      | What you get                                                                   |
| ----- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **0** | this README                                                                                               | the result + the shape of the whole project                                    |
| **1** | [`draft6.0/README.md`](draft6.0/README.md)                                                                | the draft's whole story — why draft 5 died, what 6.0 is, what eleven phases found |
| **2** | [`stage1-report.md`](draft6.0/src/stage1-report.md) · [`stage2-report.md`](draft6.0/src/stage2-report.md) | the executive arc of each stage — every phase transition and why               |
| **3** | [`phaseN/README.md`](draft6.0/src/README.md) → `phaseN/phaseN-report.md`                                  | one phase's verdict at a glance → the deep narrative with every figure         |
| **4** | `phaseN/expK/experiment-K.md` · `RESULTS.md`                                                              | the raw per-experiment record — every number, no narrative                     |

And the side doors, for readers with a specific question:

| If you want…                                                                           | Go to                                                                                    |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **The whole model in one self-contained file**                                         | [`draft6.0/src/phase9-final-architecture.md`](draft6.0/src/phase9-final-architecture.md) |
| **The real-data limit map (the red-team answer)**                                      | [`draft6.0/src/phase11/phase11-report.md`](draft6.0/src/phase11/phase11-report.md)       |
| **The soul — why this exists (the human story)**                                       | [`docs/essence/the-essence2.md`](docs/essence/the-essence2.md)                           |
| The committed design decisions (N1–S15)                                                | [`draft6.0/idea/`](draft6.0/idea/README.md)                                              |
| The simulation code (per phase, regenerable)                                           | [`draft6.0/src/`](draft6.0/src/) (`phase1..11/`)                                         |
| The papers behind it                                                                   | [`draft6.0/research/papers/`](draft6.0/research/papers/README.md)                        |
| The whole project, cold, for an AI agent                                               | [`draft6.0/context.md`](draft6.0/context.md) · [`AGENTS.md`](AGENTS.md)                  |
| How the architecture evolved (drafts 1 → 6)                                            | [`docs/draft/project-history.md`](docs/draft/project-history.md)                         |
| The superseded draft-5 (attribution) era — _pre-pivot history, not the current design_ | [`draft5.0/`](draft5.0/CLAUDE.md)                                                        |

---

## Scope & status

- **In scope now:** numpy behavioral simulation of the draft-6.0 hybrid on small classification / statistics tasks.
  Ideal math first; analog / process realism added only once the ideal converges.
- **Out of scope (for now):** SPICE, fabrication, and external-benchmark-chasing _as the claim_ — small tasks are
  fine as probes, but this is **not** a SOTA-accuracy project.
- **Done:** the neocortex organ — both brains, characterized, validated, **frozen, and raced** (Stage 1 = P1–6,
  Stage 2 = P7–10; S14). The founding bet is **refined, not inflated.** And then **validated on real data + scale**
  — Phase 11, the limit map (S15): the frozen object across eight real arenas (real drift streams, cross-dataset,
  scale sweeps), every cell win / tie / loss / **FLOOR** — the red-team "toy data" strike answered honestly.
- **This is a chip-design bet, not an ML model or a digital ML accelerator** — that brain-like computation can be
  made the _cheap_ path on the right substrate.
