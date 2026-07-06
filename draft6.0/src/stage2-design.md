# Stage 2 — the GD side: what is the gradient-descent era, and what fits our arc

> **Status: 🌱 ROUGH / IDEAS-FIRST (sketched 2026-06-30, nothing run, nothing committed).** This is **not** a runnable
> spec yet — it is the *first map* of Stage 2, written right after the cold-start research pass, while the picture is
> wide. The job of this file is to answer three questions the author posed at kickoff — **what is the whole GD era,
> what scope do we actually live in now, and which pieces fit our arc** — and to propose a phase structure to chase it.
> The literature behind every claim here lives in the GD paper folders — [`phase7/`](../research/papers/phase7/README.md)
> (readout), [`phase8/`](../research/papers/phase8/README.md) (economy), [`phase9/`](../research/papers/phase9/README.md)
> (maintenance). The frozen Stage-1 model it builds on: [`phase5-final-architecture.md`](phase5-final-architecture.md).
> When rungs firm up, this rough plan hardens into per-phase `design.md` + ladders the normal way.
>
> **⚠ Renumber (2026-07-01).** Train-with-noise was pulled *out* of Stage 2 and promoted to **Phase 6 — a Stage-1
> extension** (make SCFF noise-robust *before* the GD namer reads it; a frozen head can't manufacture robustness the
> backbone lacks — LP-FT). This file (was `phase6/design.md`) is now **`stage2-design.md`**, and the GD phases renumbered
> **6→7 (readout) · 7→8 (economy+cost) · 8→9 (maintenance)**; the old "Phase 9 noise verdict" and "P0 de-risk probe"
> **moved into Phase 6** ([`phase6/design.md`](phase6/design.md)).
>
> **⚠ Re-plan (2026-07-02, post-P8).** With P7+P8 done, the old single "Phase 9 (maintenance + owed baselines)" is
> **split into two**: **Phase 9 = *close & freeze* the maintenance loop** (tune the genuinely-open knobs — N2,
> cadence-depth, eviction, bulk-drift, read-side noise — against *internal* signals, then **lock the object**) and
> **Phase 10 = the validation / showcase** (race the **frozen** object vs a **fair** BP+replay baseline: the existential
> accuracy fight + a multi-domain adaptive gauntlet + the noise showcase → an honest Pareto verdict). The split enforces
> the one discipline that keeps the headline honest — **freeze in P9, judge in P10** (never tune against the baseline you
> are judged by). The author's kickoff "P9 = optimize the Namer" is **retired**: the Namer bake-off is *already done*
> (P7/P8 committed SLDA); re-opening it violates rule 8. **Stage 2 = Phases 7–10.** Rough plans:
> [`phase9/design.md`](phase9/design.md) · [`phase10/design.md`](phase10/design.md).
>
> **Tone, honestly:** excited. 🔥 Stage 1 was a five-phase grind to make the cheap brain compose depth. Stage 2 looks
> *smaller than it has any right to be*, for a reason that took the whole research pass to see (§2). Let's go.

---

## 0 · Where we are — the cheap brain is done, now the namer

The architecture is two brains on one substrate: **~80% SCFF** (unsupervised, forward-only, local — the cheap brain
that organizes the world) **+ ~20% GD** (the precise brain that puts the *names* on). Phases 1–5 built and closed the
SCFF half — it composes the depth a task needs (`SCFFContrastOverlap`, temp 0.2, w2, L12 bulk), read cheaply, continual-
safe. **But SCFF doesn't talk in our language.** It sorts the world into "kinds of things"; it never learned the labels
we care about. Stage 2 is the part that does — *the gradient-descent namer that shapes every model output.* This is the
last component of the neocortex brain.

I came into this stage cold: a month-and-a-half of reading only SCFF/forward-only papers, **zero modern GD context**.
So Stage 2 opened with a breadth-first research pass — find *everything* on the GD side, prioritize later. This file is
what fell out.

---

## 1 · The kickoff frame — the decisions that reshape Stage 2

Two calls at kickoff change what "the GD side" even is. **They are load-bearing for everything below.**

### 1.1 Boosting is dead → one big SCFF bulk + per-depth read-only heads

The old plan (N3) chained `[SCFF → GD-checkpoint]` **residual boosting blocks**. **Dropped.** The reason is deeper than
the old "GD reads, never writes" rule (P2.5): a boosting *chain* feeds each block's fast, supervised, GD-corrected
residual into the **next** block's SCFF input — so that block sees a moving target (gen-1 features → GD shifts them →
gen-2 → SCFF re-learns from scratch, every batch). SCFF's whole value is a **stable unsupervised base**, and a fast
supervised thing *underneath* it destroys that base. The principle, now a wall across all of Stage 2:

> **Anything between or under SCFF must be unsupervised, or slow enough not to shift everything at once. Fast +
> supervised + upstream-of-SCFF breaks the base.** (Stop-gradient blocks the *backward* leak; the boosting residual was
> a *forward* leak — that's the subtlety.)

So: **the committed era = a single L≈12 SCFF bulk + GD *per-depth readout heads*, read-only.** This retires three things
the old design carried — the boosting chain, the "Interface-GD" tracking organ (no blocks → no per-block tracker), and
the inter-block direction-chaining (Ch9 delta). The "two GD organs" collapse to **one: the readout** — and the only
fast/slow split that survives lives *inside* the readout (a fast online tracker + a slow sleep-consolidated head; §3).
*(This implies a decision-record delta to N3 — flagged in §5, not silently edited.)*

### 1.2 The scope rules (breadth-first; numpy; noise primary; hardware secondary)

- **Breadth-first.** Map the whole GD landscape, find all the papers, *then* prioritize. The "economy loop" is the
  organizing lens, not yet a filter. (Done — GD papers in [`phase7/`](../research/papers/phase7/README.md) ·
  [`phase8/`](../research/papers/phase8/README.md) · [`phase9/`](../research/papers/phase9/README.md).)
- **We live in the numpy ideal-math world.** Analog / hardware-aware training is **secondary / deferred** — build the
  full math model first; pruning for hardware later is easier than pruning now and breaking it.
- **Train-with-noise is the one PRIMARY exception** — because A7 (the cell's eval-time weight-noise sensitivity) must be
  absorbable *somewhere*. If neither SCFF (its per-sample norm *is* the sensitivity) nor the 20% GD can take it, that's
  not a knob — **it's a whole-arc rethink.** Resolved 2026-07-01 → its own **Phase 6** (Stage-1 ext): [`phase6/design.md`](phase6/design.md).
- **The cost meter is secondary** — a comparison-to-backprop tool, not a goal.
- **The north star gets a light pass** — only enough to know which GD choices *promote vs conflict* with the recurrent
  "thinking" brain, for a clean hand-off.

---

## 2 · What is the GD era, and what scope do we live in now — the landscape

Here's the realization that makes Stage 2 feel smaller than five-phases-of-SCFF: **because the SCFF bulk is frozen *to
GD*, the namer's *learning* is reservoir-*like* — and a trained readout on fixed features is (near-)convex.** Echo-state
networks, ELM: *don't train the big nonlinear thing, train only the readout*, and the *regression* has **no bad local
minima, no exotic optimizer needed.** So:

> **The scary part of "now we need gradient descent" isn't scary. The hard part of backprop was the cross-layer credit
> chain; a readout has no chain. We don't need the heavy optimizer zoo (second-order, K-FAC, Shampoo, LARS) — those are
> for the hard non-convex bulk we *don't* GD-train. The simplest thing converges here.**

**Two hedges the critic pass forced, and they matter** (so "small" doesn't become "sloppy"): (a) **"convex" names the
*regression*, not the deployed readout's substrate cost** — the softmax/normalizer is a non-free digital block (arch-file
§2.4), and tap-reading + per-depth-head Scap cost are real; that cost is what Phase 8's meter must measure, and it's why
every "80/20" claim is still a *proxy* until then. (b) **We are reservoir-*like*, not a reservoir proper** — north-star
file 8's reservoir is a *random, untrained* core; ours is *unsupervised-trained then frozen*, so we inherit the readout
convexity but **not** the reservoir's free device-mismatch-tolerance — which is *exactly why the noise question (§3.5) is
open and not auto-solved*. And convexity is per-step against a **drifting** comparator: **tracking the drift, not solving
the regression, is the real cost.** With those held, the 80/20 reframes as "80% unsupervised structure + 20% convex
naming," and the whole GD era sorts into seven buckets — five we'll *use*, one *cautionary*, one *deferred*:

| bucket | the GD-era content | our verdict |
| --- | --- | --- |
| **the readout optimizer** | SGD/momentum/Adam/AdamW/Lion; OCO/FTRL/passive-aggressive | **convex → easy.** Pick the simplest that fits the Scap. AdamW ≥ Lion on small heads. Maybe *no* optimizer (§3.1). |
| **the readout shape** | linear-softmax vs **cosine** / NCM / SLDA / **RanPAC ridge-prototype**; magnitude-bias (SCR/BiC/WA) | **the spine, in the namer.** *Cosine* reads direction; NCM/SLDA carry a magnitude but dodge recency bias — substrate-native, no-forget. |
| **the economy (gate)** | concept-drift detection (DDM/ADWIN/ADWIN-U), plateau detection, Skip-RNN budget loss | **off-the-shelf *designs* (not a free answer).** The Ch7 gate = a drift detector — but the failure modes (false-fires) burn the 80/20. |
| **maintenance** | experience replay, EWC/SI/MAS, A-GEM, generative replay; CLS | **our validated A6 win.** Sleep = replay; only the readout is replayed; owe the fair BP+replay baseline. |
| **slow coordination** | EMA / mean-teacher / momentum encoder, stop-gradient, Lookahead | **what's *allowed* between SCFF layers.** Slow or unsupervised only. EMA matters at *late* layers (= our slowdown flip). |
| **the cautionary one** | synthetic gradients / DNI; confidence-based halting/TENT | **mostly *don'ts*.** Predicted supervised gradient upstream = the §1.1 poison; confidence = a magnitude. |
| **the deferred one** | analog in-memory / hardware-aware noise training (IBM AIHWKit) | **secondary** — on file for the analog phase. *Except* train-with-noise (Bishop/SAM), now promoted out to **Phase 6** (Stage-1 ext). |

---

## 3 · What fits our arc — the shortlist (the excited part 🔥)

The candidates worth actually trying, roughly in fit order. Each is a hypothesis, not a result — temps and claims here
are things to *test*, not findings.

### 3.1 A direction / recency-robust readout (cosine, NCM, SLDA, RanPAC ridge-prototype) — the strongest fit
The spine says *read direction, not magnitude.* A plain linear-softmax head is a magnitude machine and develops the
documented **recency/magnitude bias** in continual learning (SCR's headline; the BiC/WA failure). The fix already exists
as a deployable readout — **but the critic pass caught me letting a magnitude through, and the corrected version is
sharper:**
- **Only the *cosine* classifier is strictly direction-pure** (L2-normalize features *and* weights → angle only).
  **NCM and Deep-SLDA classify by *distance* to a class mean — and a distance is a magnitude.** SLDA with a tied
  covariance is *algebraically a linear-softmax with a per-class bias `b_c = −½μᵀΣ⁻¹μ` that grows like `‖μ‖²`*, and its
  Mahalanobis metric is a *whitened* distance (and whitening was rejected-as-a-lever in P5). So NCM/SLDA are **not "the
  spine handed to us"** — they are **recency-robust** (no trained softmax weights to inflate, which is *why* they dodge
  the bias), which is *not* the same as reading direction.
- **RanPAC** ([2307.02251](https://arxiv.org/abs/2307.02251)) is the published near-twin: frozen feats → frozen random
  projection → a **ridge-regularized prototype** (running mean + running Gram matrix), **rehearsal-free SOTA, no
  gradient** — and crucially **ridge beats plain NCM**, so the second moment earns its keep. The running mean is a
  capacitor EMA and the Gram is a running second moment → substrate-native, *if* the ridge solve (a non-free digital
  block) is affordable.
- **The hypothesis I'm most excited to test, stated honestly:** the bake-off is **linear-softmax (the convex baseline,
  `race_bp`-adjacent) vs cosine (spine-clean) vs NCM vs RanPAC-ridge-prototype**, scored on **accuracy × forgetting
  (BWT) × spine-cleanliness** (does the verdict move when we rescale feature/prototype norms?). The real question isn't
  "prototypes win because direction" — it's **"does the spine-clean cosine head match the recency-robustness of the
  magnitude-carrying prototypes, or do we pay a forgetting cost to stay spine-clean?"** If a no-gradient streaming
  readout wins, the "20% GD" is partly *not even gradient descent* — cheaper *and* (for cosine) more spine-aligned.
- Honest risk: NCM/SLDA/ridge-prototype assume per-class features are ~unimodal in the frozen space. If SCFF makes a
  class multi-modal, one mean underfits → fall back to a *few prototypes per class* (a **mixture — non-convex**, so the
  clean convex story evaporates exactly here) or a thin logistic head on cosine features. The multimodality probe runs
  early. And a drift-*gated* stream presents classes in **bursts** → the head needs a class-imbalance guard (logit
  adjustment / balanced softmax) and the buffer needs class-balancing (CBRS).

### 3.2 The gate = a concept-drift detector (DDM / ADWIN / learned budget)
The unbuilt Ch7 gate is not ours to invent — it's ours to *choose and tune*. **DDM** (error-rate, two thresholds:
warning → buffer, drift → spend GD → replay-since-warning) *is* our two-threshold gate + sleep. **ADWIN** (two-window
mean test) *is* our fast-EMA-vs-slow-EMA plateau detector (it doesn't *remove* the magic number — it moves it to an
interpretable false-positive rate δ). **Skip-RNN** adds a **budget loss** that writes the 80/20 target directly into the
objective. The exciting bit: **fire the gate on the SCFF *features* (a label-free drift detector — ADWIN-U — on the
taps), not on the error** — SCFF drift *leads* the readout's error, so we can schedule a refit *before* accuracy drops.
The gate and the sleep-cadence are the *same detector at two timescales.* **The honest caveat (don't call it "solved"):**
drift detectors false-fire on long streams and on *nuisance* drift that doesn't hurt the readout — and every false fire
**burns the 80/20.** So the bake-off has a real failure axis: *which signal detects the **harmful** stall earliest
without false-firing.*

### 3.3 Sleep cadence = the drift detector, slow + readout-aware
"When to sleep" = "when has enough SCFF drift accumulated that readout coverage decayed" = the §3.2 detector integrated.
Make it **readout-aware** — consolidate the *extractor depth the fixed reader actually reads* (shallow on the flat home,
deep on compositional), not the whole stack. And finally run the **fair baseline we owe**: OURS vs **A-GEM-style
BP+replay** at matched buffer+compute (Phase 4's continual WIN was vs *naive* online-BP — not a fair fight). We may still
win (only the readout replays; the bulk doesn't forget) — but show it.

### 3.4 Slow coordination — already half-decided
If anything ever coordinates across SCFF depth, it must be **slow or unsupervised**: the **coordination window w**
(unsupervised, already adopted) or an **EMA-teacher view** of the taps (slow, read-only — the N2 "EMA-view" upgrade).
The drift-slowdown (slow the *late* SCFF layers GD reads) is now **doubly grounded** — LLRD ("slow what the downstream
reads") *and* the momentum-encoder finding ("EMA matters at the late, unstable layers"). That makes it the **default
hypothesis the sim tests first** — but, per the discipline, a *proposal pending a result*, not a settled promotion (and
promoting N2's EMA-view from standby→default is itself an owed decision-record delta — §5).

### 3.5 Train-with-noise → MOVED OUT to Phase 6 (the Stage-1 noise extension)
This *was* Stage 2's one primary/existential probe, and the kickoff logic held: noise-robustness must be absorbed
*somewhere*, and if neither SCFF nor the GD readout can take it, the arc reopens. The 2026-07-01 reframe **resolved
where it must live.** Two results we already cite settle it: **LP-FT** ([2202.10054]) — a frozen head *preserves* but
cannot *create* the robustness the backbone lacks; **Rasch 2023** — input/tap/ADC-quantization noise dominates, and the
readout *reads* exactly that channel. So the fix **cannot** be a 20% readout knob; it is an **SCFF-objective question** —
promoted to its own **Phase 6**, run *before* the GD namer is built. The full noise plan (the two noise channels, the
structured/directional attack, the *all-data-is-noisy continual* framing, the YES/NO arc fork) now lives in
[`phase6/design.md`](phase6/design.md) + [`../../research/papers/phase6/`](../research/papers/phase6/README.md).

### 3.6 North-star seed — a direction-grounded halt
Build the gate as **PonderNet's ancestor** (the static "compute cheaply until θ" is the recurrent "think until the
feeling settles," un-looped) — but **ground its signal on direction, not confidence.** Confidence/entropy is a magnitude
(why P5 struck the adaptive exit); a cosine-margin / drift signal is spine-aligned and is the seed the recurrent brain
will *reuse* as "the feeling." A confidence gate would be torn out later; a direction gate is the seed. *(Light touch —
this is a tie-break bias, not added scope.)*

---

## 4 · Proposed Stage-2 phase structure (restructured — ideas-first)

The old "Phase 6 = GD optimization" was one undifferentiated lump. Restructured (2026-07-01): the noise question split
out to a **Phase 6 Stage-1 extension that runs *first*** (see [`phase6/design.md`](phase6/design.md)), and the GD work
is **three phases (7–9), each a coherent component.** (Rung sub-numbers follow Stage-1's `PN.k` convention once this
firms up.)

- **Phase 6 (Stage-1 ext — runs *before* Stage 2): make SCFF noise-robust.** The old "P0 de-risk probe" + the old
  "Phase 9 noise verdict" are now **one front-loaded phase**, on the **existing** Phase-5 cell: inject tap/input/ADC
  noise (the channel Rasch says dominates), structured & directional, and decide whether the per-sample-norm objective
  must become noise-aware (the YES/NO arc fork). It precedes the GD work because a frozen head can't create the
  robustness the backbone lacks (LP-FT). **Detailed in [`phase6/design.md`](phase6/design.md), not repeated here** —
  Stage 2 (below) assumes it's done.

- **Phase 7 — The Readout (the namer itself).** *Build & pick the readout on the frozen bulk.*
  - the convex baseline (linear-softmax via **`race_bp`-adjacent** SGD/AdamW) as the floor;
  - **the bake-off: linear-softmax vs *cosine* (spine-clean) vs NCM vs RanPAC-ridge-prototype**, scored on **accuracy ×
    BWT × spine-cleanliness** (does the verdict move under feature/prototype-norm rescaling?). The bet isn't "direction
    wins" — it's "does spine-clean cosine *match* the recency-robustness of the magnitude-carrying prototypes?";
  - per-depth head placement (carry P5's fixed reader); single vs few-prototypes-per-class (the **multimodality** check —
    where the convex story may end); a class-imbalance guard for the bursty stream (logit adjustment);
  - optimizer & Scap-register budget (convexity says the *learning* is easy — but the deployed normalizer/Gram-solve is a
    non-free digital block; that cost is Phase 8's to meter).
  - **Deliverable:** the committed readout. *(Plausibly: "no gradient, a streaming cosine/ridge classifier." Would be 🔥.)*

- **Phase 8 — The Economy (the gate) + the cost meter.** *Build the unbuilt Ch7 gate, and the meter Stage 1 punted here.*
  - the no-gate (always-pay) control;
  - **the gate bake-off: absolute-θ vs DDM two-threshold vs ADWIN(-U) two-window vs learned budget-gate**, scored on
    (accuracy held) × (fraction of steps paying GD), with **false-fire rate** as an explicit failure axis;
  - the trigger signal: error/loss-EMA vs **label-free SCFF-tap drift detector** (fire before error reacts, without
    false-firing on nuisance drift);
  - **build the hardware-meaningful cost meter** (charge cycles / ADC / write energy, replacing the op-count proxy) — a
    required deliverable, because the metered-80/20 and the vs-BP comparisons all depend on it.
  - **Deliverable:** the committed gate **+ the honest cost meter.**

- **Phase 9 — Close & *freeze* the maintenance loop.** *Tune the genuinely-open knobs against **internal** signals, then
  lock the object.* (Full rough plan: [`phase9/design.md`](phase9/design.md).) **NOT "optimize the Namer"** — that
  bake-off is done (P7/P8 → SLDA). The open machinery:
  - **measure the bulk-drift rate** (the "bulk doesn't forget → sleep is cheap" story assumes it — P6.5 debt);
  - **N2** — the last un-resolved decision-record knob (EMA-view / late-layer drift-slowdown), tested **read-side /
    rate-only** so it does not reopen the frozen SCFF objective;
  - sleep cadence **consolidation *depth*** — *what* extractor depth to re-fit (P8 set *how often*; readout-aware);
  - **bounded-LUT eviction** under the bursty, class-imbalanced stream (cbrs vs continual-safety) — a first-class risk;
  - the **read-side noise residual** (the Phase-6 brief — input-transducer directional + ADC<3-bit) — include if it earns
    its place, else → the analog-realism layer.
  - **Deliverable:** the fully-tuned neocortex loop, **frozen** (a commit hash Phase 10 races). The discipline:
    **freeze in P9, judge in P10** — never tune against the P10 baseline.

- **Phase 10 — The validation / the showcase.** *Race the **frozen** object across the lifelong gauntlet — the document
  the professor reads.* (Full rough plan: [`phase10/design.md`](phase10/design.md); bar set with the author:
  **professor-convinced / showcase** — one fair baseline *family*, a legible gauntlet, an honest Pareto.) Three jobs:
  - **the existential fight** — OURS vs **`race_bp` + replay** (ER / A-GEM, matched buffer+compute), on **accuracy ×
    energy**, continual (closes Phase 4's owed comparison — its WIN was vs *naive* online-BP; the load-bearing test);
  - **the multi-domain adaptive gauntlet** (the money figure) — ≈5 distinct datasets/domains in sequence; measure
    **new / 1-back / all-previous accuracy + cumulative OURS-vs-BP cost** (the author's four asks = ACC / BWT /
    Forgetting + the cost curve); + the **SCFF:Namer ratio characterized across difficulty** (the "final ratio," not
    assumed);
  - **the noise showcase** — the gauntlet under {clean · iid · directional · ADC<3b · nuisance-dim}; OURS-hardened vs
    BP+replay vs naive (the Phase-6 arc, cashed in); + **A5** natural multi-class.
  - **Deliverable:** the **Pareto frontier** (win / tie / loss, stated) + the Stage-2 **close-out** report. *The object is
    frozen; P10 measures — the fight may lose, and the honest Pareto is the deliverable either way.*

- **(was Phase 9 — Noise) → promoted to Phase 6**, the Stage-1 noise extension that runs *first*. The arc-diagnosis no
  longer waits at the *end* of Stage 2 for the Stage-2-built cell — the LP-FT prior says a frozen head can't manufacture
  backbone robustness, so the test must run on the **existing Phase-5 SCFF cell, before the namer.** Full plan:
  [`phase6/design.md`](phase6/design.md).

- **North-star hand-off** (threaded, not a phase): one paragraph in the Stage-2 report — *the gate is the halt, the
  readout's **cosine margin** (a direction, not a confidence/distance magnitude) is the feeling, we built them on
  direction signals — and checked their **calibration under shift** — so the recurrent brain can reuse them; here's what
  would have conflicted.*

*(Dependency: **Phase 6 (noise) runs first**, on the existing Phase-5 cell — its verdict can reshape everything below (a
NO reopens the SCFF objective *before* the namer is built). Phases 7→8→9→10 then proceed in order on the noise-hardened
cell — and the **P9→P10 boundary is a hard freeze**: P10 races the object P9 locked, no knob-tuning across it.)*

---

## 5 · Open questions / what I'm unsure about (where the critics should push)

- **Is the readout truly convex *enough* in practice?** It's exactly convex only for a linear/logistic head; a 2–3-layer
  MLP head is non-convex again, and the features drift across the stream (online-convex with a *moving comparator*).
  Does the reservoir intuition survive our actual drift rate, or does the "easy" framing oversell it?
- **Does SLDA/NCM actually fit SCFF's geometry?** The Gaussian/unimodal assumption is doing a lot of work. If SCFF
  classes are multi-modal in the frozen space, the elegant no-optimizer story degrades to "a few prototypes + a small
  head" — still fine, but less clean. Needs the multimodality probe early.
- **Which gate trigger fires earliest without false-firing?** A label-free tap-drift detector is appealing but might
  fire on *nuisance* drift that doesn't hurt the readout — burning the 80/20. The error-based DDM is safer but lags.
- **The decision-record delta (owed — and bigger than first written).** To record in
  [`../../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md) (the way S9 was added at P5) — **flagged here, not
  silently applied, not retro-editing the frozen `phase5-final-architecture.md`:**
  - **N3** ("GD = residual boosting blocks") → **superseded** by "single bulk + per-depth read-only heads";
  - **S4** ("two GD organs") → **collapses to one** (the readout; Interface-GD retired with the blocks);
  - **N2** EMA-view → a *proposed* promotion from "de-risked standby" to default (pending the sim — not yet);
  - **S6** (threshold gate) → its "candidate refinement: gate on loss-slope" is being *resolved* (absolute-θ → a
    drift-detector); recordable once Phase 8 picks one.
- **Is the noise question framed right? (now sharpened.)** The critic pass says I was probing the **wrong channel** —
  Rasch shows **input/tap/ADC-quantization noise dominates, not weight noise**, and LP-FT shows a head can't manufacture
  robustness the backbone lacks. So the open question is no longer "is weight noise the right stand-in" (it isn't) but
  **"if the sensitivity is upstream in SCFF, is there *any* readout-side fix, or does Stage 1 have to reopen?"** This is
  the existential one — I most want it stress-tested.
- **Am I under-reading the optimizer side because "it's convex"?** If the author wants the readout-precision axis (head
  architecture, loss, calibration) treated as deeply as the economy, §3.1/Phase-6 expands. (Kickoff answer: economy-lens
  default, but breadth-first — so prioritization is deliberately deferred to *after* this map.)

---

## 6 · The discipline carried over (unchanged)

The Stage-1 methodology governs every Stage-2 rung: **one variable per experiment** · seeds `[42,137,271,314,1729]`,
median + IQR · controlled variables explicit · invariants every run (convergence, dead-fraction, drift / cluster-churn,
and now **BWT / gate-fire-rate / flatness**) · **failures are data** · defer fallbacks until baseline is characterized ·
**architecture changes are decisions, not experiments.** And the spine, above all: **preserve and read the class
*direction*, never a magnitude** — it is now *in the readout* (cosine/SLDA), *in the gate* (the validated direction
trigger — north-star seed; the shipped gate reads the error-EMA), and *in
the noise test* (directional mismatch attacks the class axis). Density ≠ class, a sixth time, all the way down. 🗿
