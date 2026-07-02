# Stage 2 — the GD namer: putting our names on the cheap brain (the report)

> The executive narrative of Stage 2 of draft 6.0 (Phases 7–9, July 2026) — the arc that takes the frozen, noise-hardened
> SCFF cheap brain and builds the **~20% gradient-descent "namer"** that maps its features to our labels. Stage 1 made a
> brain that *organizes* the world; Stage 2 makes it *answer in our language.* This is the last component of the
> neocortex brain.
>
> **⚠ This is a LIVING report — Stage 2 is IN PROGRESS.** Of its three phases, **P7 (the readout) is DONE
> (2026-07-02)**; **P8 (economy + cost) and P9 (maintenance + owed baselines) are planned, not run.** The headline result
> is real and natural-confirmed, but the stage's *existential* test — the fair same-budget BP+replay baseline — lives in
> P9 and is **still owed** (§6). Read this section as "the arc so far," not "the arc closed."
>
> The plan this executes: [`stage2-design.md`](stage2-design.md) (the authoritative Stage-2 map). The frozen cell it
> builds on: [`phase6-final-architecture.md`](phase6-final-architecture.md). The
> committed design record: [`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md). Terms and metrics:
> [`ref-report/`](ref-report/README.md). The Stage-1 arc it inherits: [`stage1-report.md`](stage1-report.md).

---

## 1 · What Stage 2 is — the one-page primer

Draft 6.0 is two brains on one analog substrate. A cheap, unsupervised **SCFF cortex** (~80%) organizes the world for
free — label-free, local, forward-only. Stage 1 built, characterized, closed out, and noise-hardened it: the committed
cell is **`NoiseAugContrast`** (`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, no residual, + one iid-noise-augmented
InfoNCE view). It composes the depth a task needs, reads it cheaply, wins the continual regime, and survives the noise it
will meet on silicon. **But it never learned our labels.** It sorts the world into "kinds of things"; it does not know
which kind is a *3* and which is a *7*.

**Stage 2 is the part that does — the precise ~20% gradient-descent namer, read-only on the frozen bulk.** Every knob
from here on is on this back, not the SCFF front (which is frozen and never re-trained). The split is the project's
founding bet: **direction is the one expensive thing in learning**, so we pay for it *once*, where it counts — putting
the names on — and get everything else for free.

**Why Stage 2 is smaller than five-phases-of-SCFF had any right to be.** Because the SCFF bulk is *frozen to GD*, the
namer's learning is **reservoir/ELM-like** — a trained readout on fixed features is a **(near-)convex regression** with
no bad local minima and no cross-layer credit chain. There is no heavy-optimizer zoo to build; the simplest thing
converges. Two hedges keep "small" from becoming "sloppy," and both are *tested*, not asserted: **(a)** "convex" names the
*regression*, not the deployed readout's **substrate cost** (the softmax / normalizer / Gram-solve is a non-free digital
block — that is Phase 8's meter, so every "80/20" number is a proxy until then); **(b)** we are reservoir-*like*, not a
reservoir proper (trained-then-frozen, not random), so we inherit the readout convexity but **not** free noise-tolerance,
and the real cost is *tracking the drift*, not solving the regression.

**One kickoff decision governs the whole stage: boosting is dead.** The old N3 plan chained `[SCFF → GD-checkpoint]`
residual boosting blocks; it is dropped. A boosting *chain* feeds each block's fast, supervised, GD-corrected residual
into the *next* block's SCFF input — SCFF sees a moving target and its stable unsupervised base is destroyed. The wall,
now across all of Stage 2: **anything between or under SCFF must be unsupervised, or slow enough not to shift everything
at once; fast + supervised + upstream-of-SCFF breaks the base.** So the committed era is **one L12 SCFF bulk + read-only
GD heads** — the "two GD organs" collapse to **one: the readout.**

**The three phases** (run in order on the noise-hardened cell):

- **P7 — the readout.** Build and pick the namer on the frozen bulk. **✓ DONE.**
- **P8 — the economy gate + the cost meter.** The unbuilt Ch7 learning-gate (cheap SCFF most steps, expensive GD only
  when the cheap path stalls) and the honest hardware-meaningful cost meter that replaces the op-count proxy. *Next.*
- **P9 — the maintenance loop + the owed baselines.** Tune the sleep cadence + gate against *this* cell's drift, and
  settle the owed old-world baselines — the fair same-budget BP+replay continual baseline and the natural multi-class
  number. *Last.*

---

## 2 · The arc so far — one thread, still running

Stage 1's arc was "we kept being right about *where* the cell wins and wrong about *how*." Stage 2 has its own thread,
and one phase in, it already has a shape:

> **The "20% GD" is a role, not a method — and the spine bends toward the cheap answer.** We expected to pay gradient
> descent for the precise brain and to pay a forgetting cost to stay direction-pure. The sims said neither: the best
> namer uses **no gradient at all**, and it wins by reading a *magnitude* — while dodging the forgetting the spine feared,
> for a reason that is *not* direction-reading.

The connective tissue is Stage 1's recurring fault, **density ≠ class**, wearing its **7th** coat. The project's spine
says *read the class direction, never a magnitude* — and the tempting move in a readout is to declare the direction-pure
**cosine** head "the spine handed to us." Phase 7 measured it instead of assuming it, and the answer was sharp: on the
frozen bulk the cosine head is **sub-competitive**, and the committed namer (**RanPAC**) reads a *magnitude* (a ridge
prototype) — yet it is **recency-robust**, not because it reads direction, but because it has **no trained softmax
weights to inflate.** Recency-robustness ≠ direction-reading. The spine bent, honestly and numerically, and we named the
tension rather than resolving it silently toward accuracy.

**The honest status, stated up front.** One phase of three is done. The headline — *the precise brain names the world
with no backward pass* — is a real, natural-confirmed **P7** result on the frozen bulk. But the architecture's *founding*
claim (an 80/20 continual learner that beats backprop's economics) is **not** yet fully re-validated in Stage 2: the fair
same-budget **BP+replay** baseline is P9's job and is still owed, and the "80/20" cost number is a proxy until P8's meter.
Stage 2 is going well; it is not finished.

---

## 3 · Phase by phase (the synthesis)

### Phase 7 — the readout → *the 20% is NOT gradient descent* 🔥  **[DONE]**

Phase 7 raced a taxonomy of *namers* on the frozen bulk — gradient heads, direction-pure cosine heads, magnitude
prototypes, and no-gradient analytic/RLS heads — refereed by three axes: **accuracy × forgetting (BWT)**, the **spine**
(does the verdict track class *direction* or a *magnitude*, measured as argmax-flip under a per-class norm nuisance), and
the un-skippable **A6 continual-safety gate**. Cost was a descriptive-only fourth axis (never a tie-break; the real meter
is P8).

![Phase 7 in one figure — the bake-off frontier](phase7/exp1/figs_p7_1/BAKEOFF.png)
*The headline. **Left** — the accuracy×forgetting frontier: **RanPAC** sits at the top-right, in a statistical three-way
tie with the gradient MLP and the un-projected RLS, and **two of the top three use no gradient**; the direction-pure
cosine-softmax and the max-magnitude FeCAM fall below, and the bare prototype heads collapse sub-floor (greyed).
**Right** — the scorecard: RanPAC carries the highest static accuracy, while only the two **cosine** heads are perfectly
spine-clean (argmax-flip 0). The whole phase is this one picture: the frontier peaks *off* the direction-pure corner — so
the spine bends — but it bends toward a no-gradient winner.*

**The committed namer is RanPAC** — a closed-form analytic head (a frozen random ReLU projection → a running-Gram ridge
prototype `W = (G+λI)⁻¹M`, no gradient, streaming) shipped with a **class-balanced-reservoir imbalance guard**. On the
continual home it ties the gradient MLP on accuracy×BWT (a 3-way tie with SLDA, AA 0.617 / 0.623 / 0.604, mutually
within-noise), has the highest static accuracy (0.647), **passes the A6 gate** (BWT +0.023 vs the floor-head baseline,
0/5 seeds negative), and is **#1 on natural digits** (AA 0.949, near-zero forgetting). Because two of the tied top three
are no-gradient, **the precise 20% brain names the world with no backward pass at all** — the "20% GD" is a role, not a
method.

**The spine bends — numerically, and less than feared.** Only the cosine head is direction-pure (argmax-flip **0.000**),
but it is sub-competitive where the bulk has structure to exploit: on the synthetic home it trails the magnitude frontier
by **Δ = 0.128** (real, 5/5, ≫ δ=0.02) → *magnitude-wins-spine-bends*. The gate makes the mechanism empirical: the
no-gradient cosine-ncm **passes** while the trained cosine-softmax — *same angle metric* — is **struck** (5/5), so the
forgetting comes from the **trained weights**, not the readout's geometry. The winner reads a magnitude yet is
recency-robust for exactly that reason. And the price **shrinks 4× on natural digits (−0.036) and vanishes on CIFAR-flat**
(where the bulk itself has no composable depth and every head collapses to ~0.3).

**Two design guesses the sims overturned** (the honest science): **(1)** the imbalance guard is **class-balanced
reservoir (cbrs, buffer-side), not AIR** — the analytic head-side guard the plan expected *over-corrects* (it crushes
recent classes); re-balancing the input beats re-weighting the output (RanPAC's bursty recency-gap +0.495 → +0.013).
**(2)** the "multimodality cliff" is **anisotropy, not multimodality** — natural per-class features are unimodal
(n-modes 1.0); the accuracy lever is a **tied covariance** (NCM 0.754 → SLDA 0.946, +0.19), closed-form, no non-convex
mixture needed (a mixture *hurts*). Both hedges from §1 held: the naming was convex-easy, and the RanDumb skeptic control
confirmed the trained bulk earns its keep vs a raw-pixel random projection (though a random *expansion of its own taps*
ties a plain linear namer — the expected ELM effect — a flag carried forward). → [full Phase 7 report](phase7/phase7-report.md).

### Phase 8 — the economy gate + the cost meter → *when does the namer fire, and what does it truly cost?*  **[NEXT — not run]**

Phase 7 picked *what* the namer is; Phase 8 decides *when* it fires and *what it actually costs on the substrate.* Two
deliverables. First, the **Ch7 learning-gate** Stage 1 punted here: the architecture pays cheap local SCFF most steps and
the expensive GD namer only when the cheap path stalls — a **concept-drift detector**, not a magic threshold. The planned
bake-off is *absolute-θ vs DDM two-threshold vs ADWIN two-window vs a learned budget-gate*, scored on (accuracy held) ×
(fraction of steps paying GD), with **false-fire rate as an explicit failure axis** — because a false fire burns the
80/20, so the gate is not "solved" until it detects the *harmful* stall earliest without firing on nuisance drift. The
appealing bet: fire on a **label-free SCFF-tap drift detector** (SCFF drift *leads* the readout's error), so a refit is
scheduled *before* accuracy drops; the gate and the sleep-cadence are the same detector at two timescales. Second, the
**honest cost meter** — charge cycles / ADC / write energy, replacing the op-count proxy — a required deliverable,
because every "80/20" and vs-BP claim depends on it. Phase 7 hands it a concrete first job: **price RanPAC's random
projection against SLDA's tied-covariance solve** (the ~200× cost gap Phase 7 flagged) — is "no-gradient" actually
cheaper on our substrate, and if the projection is prohibitive, is **SLDA** the committed fallback?

### Phase 9 — the maintenance loop + the owed baselines → *the honest fights Stage 1 deferred*  **[LAST — not run]**

Phase 9 tunes the validated A6 continual loop against *this* cell and settles the debts. The load-bearing one is
**existential**: Phase 4's continual WIN was measured vs *naive* online-backprop-without-replay — not a fair fight. Phase 9
owes **OURS vs `race_bp` + a replay buffer (A-GEM-style) at matched buffer and compute.** We may still win — only the
readout replays, and the bulk doesn't forget — but we have to *show* it, and this is where the architecture's headline
claim gets its honest test. Phase 9 also closes Phase 4's owed **A5** (multi-class on natural digits/CIFAR on the
continual-stream harness — synthetic overstates the static gap), tunes the **readout-aware** sleep cadence (consolidate
the extractor depth the fixed reader actually reads, not the whole stack), tests **bounded-LUT eviction under a bursty,
class-imbalanced stream** (cbrs — the guard Phase 7 already committed — vs continual-safety), and runs the deferred
**P6.5 bulk-drift** measurement that the "the bulk doesn't forget" cheapness assumes. Deliverable: the tuned continual
loop + the honest baselines.

---

## 4 · The decision record (what Stage 2 has set, and what it owes)

The Stage-2 spine was sketched in [`stage2-design.md`](stage2-design.md); Phase 7's results banked the first deltas to
[`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md). Flagged, never silently applied, and never retro-editing the
frozen architecture snapshots.

| Decision / knob | Committed as | Set / owed by | Now |
| --- | --- | --- | --- |
| GD = residual boosting blocks | **N3** | superseded at P7 close | _**S11**: "single frozen bulk + read-only namer" — boosting dropped (the forward-leak wall)_ |
| Two GD organs (interface / output) | **S4** | collapsed at P7 close | _**S11**: collapses to **one** — the namer (Interface-GD retired with the blocks)_ |
| Readout = fixed short-stack placement | **S9** | extended at P7 close | _**S11**: extended with the committed *head* (**RanPAC**, analytic), not just the placement_ |
| The namer is a *method* (gradient descent) | — (implicit) | overturned at P7 | _**S11 new supporting decision**: the namer is a **closed-form/streaming analytic head** — "20% GD" is a role, not a method_ |
| Threshold-gated learning (Ch7 gate) | **S6** | **owed → Phase 8** | _open; resolves to a drift-detector once P8 picks one_ |
| EMA-view slow coordination | **N2** | **owed → Phase 9** | _a *proposed* promotion (standby → default) pending the P9 sim — not yet_ |
| SCFF carries a noise-aware objective | **S10** | Phase 6 (Stage-1 ext) | _done — the frozen cell already carries it_ |

---

## 5 · The namer as it stands (end of Phase 7)

The committed namer is **RanPAC + a class-balanced-reservoir guard** — a frozen random ReLU projection φ = relu(Wr·f) → a
running-Gram ridge prototype, no gradient, streaming, A6-safe. Its value **tracks the bulk's**: it wins where SCFF
composes class structure (the synthetic tie, digits #1) and is idle where SCFF has no depth (CIFAR-flat, where all heads
collapse to ~0.3 and the cheaper SLDA edges it). What Phase 8/9 inherit:

- **The cost trade (Phase 8's call).** RanPAC's projection cost proxy is ~200× SLDA's. **SLDA is a within-noise, far
  cheaper no-gradient alternative** that also passes the A6 gate and is *more robust on depth-less inputs* — so if the
  substrate meter makes RanPAC's projection prohibitive, **SLDA is the committed fallback** (its only cost is
  spine-cleanliness: argmax-flip 0.89 vs RanPAC 0.54).
- **The imbalance guard to carry:** class-balanced reservoir sampling (buffer-side, family-agnostic). AIR is
  available-but-not-shipped (over-corrects).
- **The read-side noise residual (owed from Phase 6, deferred through Phase 7 on purpose):** the input-transducer
  directional channel + ADC < ~3-bit — a calibration-under-shift defence a *chosen* head adds on top of itself. Now that
  the head is chosen (RanPAC / SLDA), Phase 8/9 can address it read-side (LP-FT: a frozen head can't manufacture *base*
  robustness, but it can defend a channel the base can't reach forward-only).
- **The RanDumb flag (not benign):** on the *flat* home a plain linear namer gains ~nothing from the trained taps over a
  random expansion of them (the ELM effect) — verified value for the ridge/analytic namer, a tie for a linear one. The
  bulk's naming-stage value on the flat home is thus head-dependent, handed forward as a flag, not a footnote.

---

## 6 · Honest scope of Stage 2 so far

- **One phase of three is done.** P7 (the readout) is complete and natural-confirmed. P8 (economy + cost) and P9
  (maintenance + owed baselines) are planned, not run. This report is a *living* document; the stage is not closed.
- **The existential test is still owed.** The architecture's headline continual claim rests on a fair same-budget
  **BP+replay** baseline that is Phase 9's deliverable. Phase 4's WIN was vs *naive* online-BP; until P9 runs the fair
  fight, the 80/20 continual claim is *supported but not fully validated in Stage 2.* We say so on purpose.
- **The cost claim is a proxy.** Phase 7's cost numbers are op-count / solve-dim proxies, descriptive-only. The honest
  hardware-meaningful meter (charge / ADC / write energy) is Phase 8's; no settled "80/20" or vs-BP energy claim exists
  yet.
- **Behavioral simulation only** — numpy ideal floats plus Phase 6's behavioral analog-noise model; no SPICE, no device
  physics, no fabrication.
- **Small, partly synthetic tasks** — the continual home, digits, CIFAR-flat. The headline "20% is not GD" is confirmed
  on the SCFF-working natural home (digits); CIFAR-flat is a *bulk* limitation (no composable depth there), not a namer
  result.
- **Key machinery is unbuilt** — the Ch7 gate (P8) and the tuned sleep cadence (P9). What is committed is the *readout
  family*, not the whole neocortex loop.

---

## 7 · The north-star hand-off (threaded, not a phase)

Stage 2 touches the north star — the recurrent, lifelong-learning prefrontal↔hippocampus loop where *correctness is a
self-generated feeling* — only as a **tie-break bias**, so the later brain can reuse Stage-2 signals instead of tearing
them out. The design's seed was: the gate is the *halt*, and the readout's **cosine margin** (a direction, not a
confidence or distance magnitude) is *the feeling.* Phase 7 sharpened this honestly. The committed namer (RanPAC) reads a
**magnitude**, and the direction-pure cosine head turned out sub-competitive as a *classifier* — so the "feeling" is **not**
the deployed head. But the cosine margin survives as an **available, perfectly spine-clean direction signal** (argmax-flip
0), decoupled from the classifier: the recurrent brain can read the *angle* for its self-generated confidence even while
the *names* come from the magnitude head. The gate half of the seed is intact and forward to Phase 8: build it on a
**direction / drift** trigger, never a confidence magnitude (why P5 struck the adaptive exit) — a confidence gate would be
torn out later; a direction gate is the seed. Light touch, held to a tie-break — **simple intelligence first.**

---

## 8 · What's next

Phase 8 — the economy gate + the cost meter — is the live line: build the drift-triggered Ch7 gate (with false-fire as a
first-class failure axis) and the honest substrate cost meter that finally prices RanPAC against SLDA. Then Phase 9 runs
the fair BP+replay baseline that gives the architecture's headline its honest test, closes the owed natural multi-class
number, and tunes the maintenance loop. When P9 closes, this report is rewritten as a Stage-2 *close-out* (the way
[`stage1-report.md`](stage1-report.md) closed Stage 1), and the neocortex brain — cheap unsupervised structure + a
precise continual-safe namer + a metered economy — is done. After that, the analog-realism layer (SPICE / PVT); and,
beyond the numbered phases, the recurrent lifelong brain remains the north star. *Simple intelligence first.*

---

## Reading guide

**If you read only one file for the model:** [`phase6-final-architecture.md`](phase6-final-architecture.md) — the
self-contained, noise-hardened account of the whole cell (the frozen bulk Stage 2 names). **For the plan Stage 2
executes:** [`stage2-design.md`](stage2-design.md) (the authoritative Stage-2 map). **For the result so far:** this file
(the arc) → [Phase 7 front door](phase7/README.md) →
[Phase 7 report](phase7/phase7-report.md) (the deep story, every figure) → [`phase7/RESULTS.md`](phase7/RESULTS.md) (the
scalar ledger) → the `phase7/expK/experiment-K.md` cards. Terms, metrics, and papers are defined in
[`ref-report/`](ref-report/README.md); the committed decisions in [`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md).

*Prev:* [the Stage-1 arc](stage1-report.md) · *Up:* [draft 6.0 context](../CLAUDE.md) · *Next:* Phase 8 — the economy gate
+ the cost meter (the live line).
