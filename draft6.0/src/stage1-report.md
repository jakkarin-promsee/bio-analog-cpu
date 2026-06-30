# Stage 1 — the cheap brain, built, characterized, and closed out (the report)

> The executive narrative of Stage 1 of draft 6.0 (Phases 1–5, June 2026) — the five-phase arc that built the
> first organ (the SCFF + GD neocortex cell), found where it wins, failed to make it deep, found *how* it can be
> deep, characterized the result, and **closed out the cheap brain by solving its one remaining wound — the depth
> decay.** Each phase has its own detailed report; this is the spine that connects them, written as a first-person
> research log. The five reports: [Phase 1](phase1/phase1-report.md) · [Phase 2](phase2/phase2-report.md) ·
> [Phase 3](phase3/phase3-report.md) · [Phase 4](phase4/phase4-report.md) · [Phase 5](phase5/phase5-report.md).
> Terms and metrics are defined in [`ref-report/`](ref-report/README.md); the committed design is the
> [decision record](../idea/main.ideas.v1.md); the project's origin is told in
> [`the-essence`](../../docs/essence/the-essence.md).

---

## 1 · What Stage 1 was — the one-page primer

Draft 6.0 is a bio-inspired **analog compute substrate** with on-chip learning — a chip design that tries to make
brain-like computation the *cheap* path, not a machine-learning model. The guiding method is a motto: **copy the
brain's *function*, cheat the *implementation*** — pay for each principle with whatever is cheap on this substrate.

**The substrate.** The atom of storage is the **Scap** — one synapse's weight held as analog charge on a capacitor
(magnitude) plus a digital SRAM bit (sign). Compute happens *in the wires*: a crossbar of Scaps performs the
multiply-accumulate as physical current, and hardwired op-amps do add / multiply / ReLU directly on charges. There
is no ALU shuffling data; the computation is where the weights physically are. The forward scheme is **mono-forward
dual-rail** — a single sweep carries two worlds, a positive and a negative, side by side through the *same* shared
crossbar, doubling only the cheap activation buffers, not the weights.

**The 80/20.** Two brains share that substrate. A cheap, unsupervised **SCFF cortex** (~80%) organizes the world
for free — label-free, local, forward-only, no backward pass that leaves the chip. And a small, precise
**gradient-descent namer** (~20%) maps those features to real labels. The split is principled: **direction is the
one expensive thing in learning**, so we pay for it *once*, where it counts, and get everything else for free.

**The frame.** Stage 1 is the first organ, built and characterized in **behavioral simulation** (numpy, ideal
floats) — *before* analog/PVT realism (Phase 6+) and *before* the north star (the recurrent lifelong brain). The
question Stage 1 set out to answer was never "does this beat backprop on accuracy." It was **where does a cheap,
local, forward-only learner earn its place?**

## 2 · The one arc (the spine)

Five phases, one argument. The shape of it:

> **We kept being right about *where* the cell wins (continual, substrate-native depth) and wrong about *how*
> (deep SCFF, energy-goodness) — and every correction came from a sim or a paper overruling the plan, never from
> tuning-to-pass.**

The connective tissue underneath is a single recurring fault — **density ≠ class.** SCFF's energy goodness
(`G = Σ‖h‖²`) makes a layer *loud* on coherent input and *quiet* on mixtures, so it learns *where the data is
dense*. That recovers classes only when classes *are* density clusters. Watch that one fact travel:

- **Phase 1 found it** (exp0: an equal-density spiral defeats SCFF-alone) and found the home it doesn't hurt — the
  *continual* regime, where SCFF's unsupervised features simply don't forget.
- **Phase 2 hit the wall it builds:** density doesn't compose across depth, and *no* negative-selection fixes it —
  *even a label oracle* (P2.2). We concluded, in the moment, that the wall was "intrinsic to forward-only locality."
- **Phase 3 found the door was the *objective*, not the locality.** Swap energy (preserves density) for **contrast**
  (preserves class), add a forward-only **coordination window**, and depth composes — overturning Phase 2's verdict.
- **Phase 4 drew the map**, and the map reads the whole cell exactly as the spine predicts: a *density/structure*
  learner with a cheap class-namer on top — it wins where the substrate lives and trails on static accuracy, *by
  design*. The map left **one wound open**: past ~layer 5 the deep representation *decays* — the cell stops getting
  more separable and starts getting less.
- **Phase 5 closed it out** — and the wound was *density ≠ class* a fifth time. The decay is not dead units or too
  little width; it is **direction**: deep local-contrast layers drift *off the class manifold* once a layer's
  abstraction saturates, while their *magnitude* (rank, variance, goodness) stays healthy. A **sharper InfoNCE
  objective** that keeps each update on the class direction earns the depth back (the readout beats tuned-BP; the probe tail reaches the objective ceiling), and — because
  the home is the *flat* continual regime — a **short fixed reader** reads the useful depth cheaply. The wound is
  solved, scoped, continual-safe, and confirmed on real data. The cheap brain is finished.

## 3 · Phase by phase (the synthesis)

### Phase 1 — building the cell, finding the home → *continual*

We built one block (SCFF stack + GD readout) and asked what it *is*. On static tasks it is a weak feature learner
and GD wins raw accuracy. But a single block **generalizes better than backprop** — memorization gap +0.027 vs GD's
+0.062 on MNIST (disjoint IQR, 5/5) — at **~10% of the backward cost**. And in the **continual** regime it wins
decisively: where online backprop catastrophically forgets (→ chance, ~0.18), the SCFF features stay class-separable
the whole way (the all-class probe stays flat at 0.90/0.75), so a cheap **sleep** consolidation over a prototype
**LUT** restores near-ceiling accuracy (0.935; 0.898 at a third of the store). That is the win — and the wound it
flagged: **SCFF degrades with depth.** → [full report](phase1/phase1-report.md)

### Phase 2 — depth is not SCFF's lever → *the wall, and the cheap survivor*

The wound collided with the substrate's economics (the Scap crossbar's cheap axis is *depth*; SCFF's strength is
*width*), so Phase 2 tried to move SCFF onto depth — and closed every hatch. Not a **transmission** problem (P2.1:
the DeeperForward fix cures dead-units and rank-collapse mechanically but never makes class-separability rise) and
not an **objective** problem (P2.2: *even a perfect label oracle* negative doesn't bend the depth-slope). The
constructive survivor: depth comes from **boosted ensembles of *shallow* SCFF blocks with tiny GD readouts** —
`read` (boost the readouts) earns ~85% of GD accuracy at ~1/6 of its backward cost; `write` (re-inject) fails. And
the recipe preserves the continual win, continual-safe by construction. We concluded the wall was "intrinsic to
forward-only locality" — a verdict Phase 3 would narrow. → [full report](phase2/phase2-report.md)

### Phase 3 — the objective reframe → *depth, won, and adopted*

The literature caught the one word that was too strong: the wall is intrinsic to the **energy objective `Σh²`**,
not to locality — forward-only, unsupervised learners (GIM, CLAPP) *do* compose depth, because their objective
preserves *information*, not energy. The sims confirmed and sharpened it: **reconstruction** preserves density
(below random, rejected); **contrast** (InfoNCE) preserves class (above random, growing with depth); and the
**coordination window** (the user's "help the next layer" idea, forward-only) converts contrast's preserved-but-
myopic features into *composed* ones — on a task with depth headroom, the per-layer probe rises *monotonically*
(w4 +0.022/layer to 0.569 at L8). This **overturns P2.2**, and it *re-earns and improves* the continual win
(BWT −0.017 vs energy's −0.026). **Adopted; it supersedes energy-goodness.** Honest scope, kept front and center:
the depth-composition is a **rising *slope* on a synthetic headroom task vs a fixed-budget GD baseline** — the
slope is the claim, not a GD-beat. → [full report](phase3/phase3-report.md)

### Phase 4 — the capability map → *a continual learner, not a static competitor*

We stopped improving the cell and **characterized** it — the gap to a *genuinely-tuned* backprop ceiling across
seven controlled axes, for coverage, not triage. The map is the thesis, measured: **WIN** A6 continual (decisive —
BWT −0.02→−0.18 vs online-BP's −0.83→−0.99, robust across difficulty), A2 nuisance-dim (crosses *above* tuned BP
in high-D while Mono-Forward collapses), A3 depth-composition (generalizes; out-composes the GD-hidden ceiling in
the hard regime), A4 depth-is-cheap (backward cost flat-in-depth vs BP's linear — the 80/20 advantage is
**depth-gated**); **TRAIL** A1 difficulty and A5 class-count (capture is the read; real data far kinder than
synthetic); and an honest **NEGATIVE** on A7 eval-time noise (the per-sample layernorm that wins A2 costs A7 — a
real tradeoff, and the substrate-relevant *train-with-noise* test is untested). The breadth even caught a latent
OOM bug and refuted the plan's optimistic noise-win — the pre-flight gate working. → [full report](phase4/phase4-report.md)

![capability map](phase4/figs_summary/CAPABILITY_MAP.png)
*The Stage-1 result in one glance: the cheap forward-only brain WINS where the substrate lives (continual,
nuisance-dim, depth-cheap, depth-composition), TRAILS on static accuracy, and returns one honest NEGATIVE on
eval-time noise. (OURS vs a genuinely-tuned BP ceiling, 7 axes; the continual WIN is measured vs **naive online-BP
without replay** — the fairer same-budget BP+replay baseline is Phase-6 work.)*

### Phase 5 — closing out the cheap brain → *depth solved, read cheaply*

Phase 4 left one wound open: useful composition stops at ~layer 5, then the representation decays. Phase 5 set out
to fix it and close SCFF — and first **named the decay precisely.** It is not dead units and not too little width;
it is **direction** — the deep layers drift *off the class manifold* once a layer's abstraction saturates, alive
and full-rank but mis-aimed. And it is **objective-locality, not an intrinsic "Tunnel"**: a diagnostic full-credit
window (w12 — a *forbidden* full-backprop reach, measured only as the upper bound, never deployed) composes the
whole 12-layer stack with **no decay at all**, so the depth is *curable*. Two cheap, forward-only levers cure it.
**(1) Earn it.** A sharper InfoNCE temperature (0.2) keeps each update more class-selective: it marches the probe
peak L5→L6 (→L9 once the window opens to w4) and lifts the headroom tail 0.435→0.530 (→0.562 at w4) so the **readout
beats a genuinely-tuned backprop** (0.550 [0.545–0.553] vs 0.531 [0.531–0.533], IQR-disjoint — the tuned `race_bp`
racer, not Phase 3's weaker fixed-budget GD) while the probe tail reaches the w12 ceiling (0.556). An lr-matched
control proves ~82% of the lift is *direction*, not a disguised learning-rate — the spine, paid a fifth time. **(2) Read it cheaply.** Per-depth heads read by a
short, fixed truncation stack read the continual home at **8× less readout-forward cost than all-tap** (0.547 @ 9.0k vs
all-tap @ 72.5k readout-MACs; the L12 SCFF bulk still runs — this is a *readout* saving, not total inference) — because all-tap dilutes the class signal with the very drifted deep layers a capacity-limited head
can't zero-weight. Both gates held: the fix **keeps the A6 continual win** (BWT −0.026 vs −0.017, the sleep-recovery
mechanism intact) and the **decay reproduces on real data** (digits + CIFAR-flat), with the **temp-fix real on
digits** (tail +0.152, roughly halving the decay) and null-but-safe on the no-headroom CIFAR-flat wall. Two honest
narrowings, both struck on evidence: the **adaptive per-sample early-exit**
lost to a fixed stack (the flat home rewards *pooling*, not placement — the inverse of the headroom result), and the
**frozen-residual** preservation cell was skipped (the cheap levers closed the gap the fixed reader never reads).
→ [full report](phase5/phase5-report.md)

![phase-5 scorecard](phase5/exp9/figs_p5_9/SCORECARD.png)
*The close-out in one glance: depth EARNED (readout beats tuned-BP), read CHEAPLY (a fixed short stack, 8×; the adaptive
exit lost), continual-SAFE (A6 intact), and natural-CONFIRMED. The committed cell — `SCFFContrastOverlap` temp0.2 / w2,
L12 bulk, no residual, fixed-reader deploy — is the cheap brain, closed.*

## 4 · Where the decisions came from (provenance)

The draft-6.0 spine was committed on paper as **N1–N3** (the net) + **S1–S8** (supporting structure) — the
[decision record](../idea/main.ideas.v1.md). Stage 1 set the open numbers and corrected several of the calls. This
table is the audit trail: which committed decision was set, corrected, or merely carried — and by which result.

> *Honesty note:* what was **un**tested is marked as such (e.g. S4). That candor is what makes the table credible —
> a provenance table that claims everything was validated is the one nobody should trust.

| Decision / knob | Committed as | Set / corrected / tested by | Now |
| --- | --- | --- | --- |
| SCFF = the cheap brain | **N1** | Phase 1 exp0 | _confirmed; goodness = **sum** ‖h‖² (not mean), θ=2.0, input-norm on_ |
| Middle layer = plasticity slowdown | **N2** | Phase 1 exp2c | _slow read-layers ρ≈0.3; a **drift** fix, not a **depth** fix; its coordination half effectively superseded by Phase-3's window_ |
| GD = residual boosting blocks | **N3** | Phase 1 exp3 | _confirmed; full residual ε=1 (diversity > preservation); Ch9 delta off_ |
| Path-diversity from depth, not width | **S1** | the whole depth arc (P2 → P3) | _validated indirectly: deep SCFF can't (P2), depth-via-coordination can (P3)_ |
| Mono-forward, dual-rail | **S2** | Phase 4 A4 | _cost claim **measured**: backward cost flat in depth (the 80/20 is depth-gated)_ |
| GD reads via taps | **S3** | Phase 1 exp1 | _corrected: tap **ALL** layers (not "last n")_ |
| Two GD organs (interface / output) | **S4** | — | _carried, **not separately characterized** (wasn't isolated behaviorally)_ |
| Mandatory inter-layer normalization | **S5** | Phase 1 + Phase 2.1 | _input-norm ratified (P1); length-norm survives but **mean-zero kills** → must pair with linear goodness (P2.1)_ |
| Threshold-gated learning (Ch7 gate) | **S6** | _unbuilt_ | _open → Phase 6 (GD-side)_ |
| Sleep consolidation | **S7** | Phase 1 exp4 | _confirmed; the continual recovery mechanism_ |
| LUT prototype memory | **S8** | Phase 1 exp4 | _confirmed; replays at ⅓ store (0.898 vs 0.935)_ |
| Readout = fixed short-stack placement | **S9** (Phase-5; revises S3) | Phase 5 P5.3–P5.5 | _set: read the sharp extractor depth, not literally every layer; adaptive exit struck; no residual_ |
| — *emergent Stage-1 decisions* — | | | |
| Depth = block-count, not SCFF-layer-count | (Phase-2 finding) | Phase 2 P2.1/2.2/2.5 | _set: deep SCFF can't earn depth; read-not-write_ |
| SCFF objective: energy → contrast + coordination | (reframe) | Phase 3 P3.0–P3.3 | _**adopted**; supersedes energy-goodness `Σh²`_ |
| SCFF depth: earn it via a sharper objective | (Phase-5 fix) | Phase 5 P5.1/P5.2 | _set: **temp 0.2 / w2** default (readout beats tuned-BP); **w4** = bounded depth-closer; the decay was objective-locality, not an intrinsic Tunnel_ |
| The committed cell (close-out) | — | Phase 3 adopt + Phase 4 char + Phase 5 close-out | _`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, NO residual, fixed-reader deploy (truncate ~L2–3 on the home; all-tap for peak; w4 for compositional)_ |

## 5 · The cell as it stands (end of Stage 1)

The committed cell is **`SCFFContrastOverlap` — contrast (InfoNCE, two-mask views) at temperature 0.2 +
coordination window w=2, L12 bulk, NO residual, deployed with a fixed short-stack reader** (truncate ~L2–3 on the
continual home; all-tap when peak accuracy is wanted; **w4** the bounded depth-closer for compositional tasks) —
forward-only, per-sample, no batch statistics, sleep-consolidated, continual-safe by construction. Stage 1 measured
what it is, and Phase 5 closed the one open wound:

- **It wins continual** (the home): sleep recovers what online backprop catastrophically forgets, robustly across
  difficulty — its reason for being.
- **It composes the depth a task needs, and reads it cheaply** (Phase 5): a sharper objective earns the depth back so
  the **readout beats a genuinely-tuned backprop** and the probe tail reaches the w12 ceiling; the useful depth is then read
  **8× cheaper than all-tap** by a short fixed stack. Backward cost stays flat-in-depth where backprop's grows
  linearly, so the narrow-deep, substrate-native shape is ~free for it.
- **It is nuisance-robust:** in high ambient dimension it crosses *above* a tuned backprop, for free.
- **It trails on static accuracy** (difficulty, many synthetic classes) — the cost of being a density/structure
  learner with a cheap namer rather than a global error-minimizer.
- **It is *not* yet noise-robust** in the one test we ran (eval-time weight noise) — a real, owned tradeoff, and a
  *pointed* one: the sensitivity is **directional**, and an analog substrate's dominant mismatch is *also* directional,
  so it attacks the very class-direction the design exists to protect. The substrate-relevant test (train-with-noise) is
  still untested → Phase 6 — and this is the architecture's sharpest open silicon risk, not a footnote.

## 6 · Honest scope of Stage 1 as a whole

- **Behavioral simulation only** — ideal floats, numpy; no analog / PVT / SPICE, no fabrication.
- **Small and partly synthetic tasks** — checkerboard, digits, MNIST, CIFAR-flat, and built Gaussian generators.
  The depth-composition result in particular is on a **built synthetic headroom task** — Phase 5 hardened it (the
  re-tuned **readout now beats** a genuinely-tuned backprop, and the decay reproduces on real digits *and* CIFAR-flat
  with the fix real on digits) but the temp-fix is **null-but-safe on flat data with no composable depth** (CIFAR-flat stays at the wall — it needs
  convolution, which is out of scope). The synthetic headroom result is a representation claim, not a benchmark-beat.
- **Not a static-accuracy claim** — and we don't make one; the architecture trails there on purpose.
- **Key machinery is unbuilt** — the Ch7 threshold gate and a tuned sleep cadence are named and deferred to Phase 6
  (the GD-side optimization phase).
- **Open follow-ups, not blockers** — natural-data / larger-scale validation, train-with-noise (hardware-aware),
  direct-feedback coordination, and anything needing architecture (convolution, time-series) — the north-star track.

## 7 · What's next — Phase 6 (the GD-side era)

The cheap brain's *design* is finished (ideal-float behavioral sim — not silicon- or benchmark-validated).
**Phase 6 = GD-side optimization** — every remaining knob is on the precise ~20% GD back, not the SCFF front. Stage 1 (and now the Phase-5 close-out) hands it a settled cell and a precise brief: tune
the **maintenance loop** — the sleep cadence + the Ch7 learning-gate, now **readout-aware** (consolidate the
*extractor-depth* features the fixed reader actually reads; shallow on the flat home, deep on compositional tasks) —
against *this* cell's measured drift; make the cost meter **depth-aware and temporal** (the 80/20 lives in the gate +
sleep cadence, not a per-pass number); and run the **train-with-noise** (hardware-aware) test before any analog-noise
claim (Phase 4's A7 is a non-win until then). After that, the analog-realism layer opens. Phase 5's parked-with-
evidence threads wait here too: the **oracle-exit headroom** (a better per-sample depth-selector than max-softmax
could unlock large gains on the continual home — but it is a selector / north-star problem), and a *compositional*
continual stream to test whether an adaptive exit ever earns its keep off the flat home. The **recurrent lifelong
brain** — a time-series prefrontal↔hippocampus loop where "correctness is a self-generated feeling" — remains the
north star, beyond the numbered phases, deliberately not specced yet. *Simple intelligence first.*

---

## Reading guide

**If you read only one file:** [`phase5-final-architecture.md`](phase5-final-architecture.md) — the **v1.0.0**
self-contained account of the whole model (what it is, the math, how it extends each paper, the five-phase arc),
written for an outside researcher to understand the architecture without opening any phase report.

Otherwise, enter the set here, then descend by need: **stage1-report** (this file — the arc) → each phase's
**[`README.md`](phase1/README.md)** front door (the navigable synthesis + key figure) → the five
**[phaseN-report.md](phase1/phase1-report.md)** (the detailed logs, with figures and the per-experiment story) →
the **`expK/experiment-K.md`** cards (the full six-slot reads + threats) → **[`ref-report/`](ref-report/README.md)**
for any term, metric, or paper. The per-phase **`RESULTS.md`** ledgers carry every scalar; each phase's
**`design.md`** keeps the pre-run design it was built against. The whole set is meant to read cold to an outside
researcher with only `ref-report/` as the glossary.
