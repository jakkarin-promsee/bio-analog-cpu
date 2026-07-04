# Phase 11 — The limit map: the frozen recipe on real data and at scale (the plan)

> **Status: 🟢 READY-TO-RUN (final spec 2026-07-04; deep-research folded — §0.4 +
> [`../../research/papers/phase11/README.md`](../../research/papers/phase11/README.md); 3-agent lab-manager review
> FOLDED — §8 (2 blockers + 20 findings, all resolved); nothing run, nothing committed to `main.ideas`).** A *live spec an agent executes* — the experiment ladder + build
> plan for the phase the red team asked for: **harder data, real-world data, cross-dataset streams, and scale — run
> honestly, expecting and welcoming losses.** The product is not "we win everywhere"; the product is **a map of where
> the object holds and where it breaks**, drawn with the P10 fairness discipline. A loss with a named mechanism is
> worth more than an untested claim; the author's bar: *"if everything fails, let them attack my math, not my missing
> evidence."*
>
> **Lineage:** `temp2/phase10-extend-design.md` (the red-team response) → the critique pass (C1–C12) → the rough
> concept (git `7bcd771`, banked pre-research) → the deep-research pass (D1–D7) → this spec. The frozen object it
> measures: [`../phase9/README.md`](../phase9/README.md) (the committed loop, provenance `59d2720`). The instrument it
> carries: [`../phase10/design.md`](../phase10/design.md) + [`../phase10/result-format.md`](../phase10/result-format.md).
> Reporting contract: [`result-format.md`](result-format.md). Literature:
> [`../../research/papers/phase11/README.md`](../../research/papers/phase11/README.md).
>
> **Phase 11 is a NEW phase, not a P10 appendix.** Phase 10 closed as measurement-only on the frozen object (S14, all
> guards bit-exact); re-opening it would blur the freeze discipline that makes it trustworthy — and Arm B here
> deliberately *builds* scaled instances, which cannot live inside a measurement-only phase. Conversationally this is
> "Phase 10 part 2" (ideal-world personality → real-world limits); in the repo it is **`src/phase11/` — the limit map.**

---

## 0 · Why Phase 11 exists — the strikes, the asks, and what it is NOT

### 0.0 The three strikes (every serious reviewer throws them, in this order)

1. **"Isn't this just SLDA?"** The namer is literature (SLDA/RanPAC). No namer-alone / no-bulk cell exists anywhere
   in `src/phase10/` (checked 2026-07-04 — the only "alone" hits are prose). Until Δbulk is measured, the
   architecture claim is open to "a known closed-form classifier plus a gate." → **P11.1.**
2. **"Toy data."** Every P1–P10 number lives behind the 40-D porthole at 10 classes — 8×8 digits the home,
   CIFAR-flat only as probes, gauntlet pools 1,200 train/domain (F8 — the precise sentence; the overstated version
   was itself falsifiable). Real inside that arena; unknown outside it. → **P11.2–P11.4.**
3. **"Does it scale?"** One width (64), one depth (12), one input dim (40), one class count (10). No scaling read of
   accuracy, of the 80/20 economy, or of the safety win exists. → **P11.5–P11.6.**

### 0.1 The author's kickoff asks (2026-07-04 — first-class deliverables)

- **A1 — the per-batch STREAM view everywhere.** Every arena emits the GAUNTLET-STREAM-style per-batch figure
  (live-batch prequential + seen-so-far + sleep ticks + onset markers + cumulative energy), the
  `GAUNTLET_STREAM_LONG.png` treatment. The sleep mechanism must be visible **"in both bad and good"** — the
  between-sleep sags and the recovery jumps are the mechanism, not noise to hide. (Research note: the live-batch
  curve IS the streaming field's *prequential accuracy* — we inherit their canon by drawing what we already draw.)
- **A2 — the aggressive cross-dataset gauntlet.** Domains that are **different datasets entirely** (MNIST →
  Fashion-MNIST → CIFAR-10-gray), not same-data-plus-transform. "How robust to the TYPE of data." The field's
  **5-Datasets** protocol (Ebrahimi et al., ECCV 2020) at our scale, run class-IL (harder than the field's task-IL,
  stated). → **P11.4.**
- **A3 — the famous real-world datasets, so nobody doubts the data again.** Gas drift (headline) + HAR + the
  streaming canon (Electricity, Covertype) + the bonus real-drift arenas the research surfaced (Wild-Time Yearbook —
  real vision drift 1930–2013; MedMNIST optional). → **P11.3.**

### 0.2 The honest goal (pre-registered posture)

We expect to **lose static accuracy by more** as data hardens — P4 named the identity (continual, not static) and
P10.5 measured it (−0.071 on easy natural data). The claims under test at scale are the ones P10 *banked*:
**continual safety (worst-BWT), retention under switching (switch-frequency-scoped, per E8), order-invariance,
noise robustness, the 80/20 economy, the substrate floor.** If those survive the ladder, the object is real. Where
they break, the break gets a name and a figure — the LIMIT-MAP ships with its red cells. **Phase 11 measures and
builds instances by a pre-registered recipe; it tunes nothing** (methodological rule 5: a rung that fails under the
frozen recipe is a *result*, logged, never tuned into working).

### 0.3 What Phase 11 is NOT — the scope guard

- **NOT a P10 re-open.** Every P10/P9 artifact is read-only; any carried array is snapshot-then-diff bit-exact.
- **NOT tuning.** Committed hyperparameters (InfoNCE τ0.2, w2, σ_aug 1.0, SLDA shrinkage, DDM gate, CBRS, grid-4)
  never move — in either arm. The cadence axis is NOT re-opened (grid-4 fixed; the frontier was P10.2's job).
- **NOT raw-vision-at-scale.** ImageNet/CORe50/CLEAR-raw stay untouched (named non-claims, §5); P11.8's features
  arena (if its off-box precompute lands) borrows a conventional encoder and says so in its first sentence.
- **NOT PVT/analog realism.** Still ideal-operator behavioral sim; the meter stays behavioral (relative-pJ,
  ADC-centred, NOT SPICE). The analog-realism layer remains the next architectural phase.
- **NOT recurrence / the north star.**
- **The map can be red.** A rung where OURS loses is drawn, named, and shipped. Losses are cells, not failures of
  the phase.

### 0.4 The rough guess, and what the deep research changed (the honest-science record)

The pre-research dump is banked (git `7bcd771`). The research pass
([`../../research/papers/phase11/README.md`](../../research/papers/phase11/README.md)) answered *"did the rough plan
cover it all, and is there a better choice?"* — **directionally yes, materially incomplete in seven places**, all
folded here:

| # | the rough guess | what the research changed |
| --- | --- | --- |
| D1 | "cross-dataset gauntlet, class-IL, cite = research task" | the protocol is the field's **5-Datasets** (Ebrahimi ECCV'20 `2003.09553`); ours = the 3-block box-loadable variant, class-IL 30-way (harder than the field's task-IL — stated as such) |
| D2 | "Electricity = streaming canon, verify pathologies" | ELEC2's **label autocorrelation** trap: a no-change (persistence) classifier scores ≈0.85 (Souza et al. 2020) → the **no-change baseline is mandatory on every real-world stream**; a cell that can't beat persistence renders FLOOR, never a win |
| D3 | "gas = the headline; verify batch composition" | the dataset has a published **limitations paper** (Dennler et al. 2022) — cite it preemptively; per-batch class-composition table printed at bench; **balanced accuracy** is the read; batch sizes ≈ {445,1244,1586,161,197,2300,3613,294,470,3600} (verify at bench); anchor = Vergara 2012, numbers transcribed at bench before our runs |
| D4 | "any missed box-feasible real-world set?" | **two found**: Wild-Time **Yearbook** (33,431 × 32×32×1, 1930–2013 — real VISION drift, no backbone needed) = the E2 vision leg (declared bonus, gated on download); **MedMNIST/BloodMNIST** (npz, 28×28×**3** RGB → 2352-D flat — §8 L1) = optional famous-data rung; "E2" = P11.3 in the final numbering. Neither gates the phase |
| D5 | "our ER must reproduce field-strength numbers" | anchor source pinned: **van de Ven et al., Nat MI 2022** + the official `GMvandeVen/continual-learning` numbers; the published Split-MNIST ER band is transcribed into the manifest **before** our ER runs (the anchor guard). *Scope (§8 R4): the anchor retires implementation-bug strawman claims only; per-arena strength is enforced separately (the dominance guard + the pinned grid)* |
| D6 | "openml IDs: research" | pinned: Fashion-MNIST **40996** · Electricity **151 v1** (45,312 chronological — the "balanced" v2 destroys time order, named as the wrong variant) · Covertype **1596** (581k×54×7 confirmed; id 150's equivalence unconfirmed — §8 L2, use 1596) · CIFAR-100 41983 (stretch, verify at bench); MNIST 554 + CIFAR-10 40927 **verified cached on this box** |
| D7 | "fix the CLEAR cite" | CLEAR = Lin et al., NeurIPS'21 D&B `2201.06289` (temp2 had linked CALM `2004.03340`) — fixed here and in the research file |

*(Also folded pre-research: the critique fixes C1–C12 — floor-state cells, per-arena joint ceiling, the E4
meter-derivation direction catch, gas hygiene, gate fire-rate invariant, Permuted/Rotated-MNIST correspondence, NTE
raise, pinned ER tuning grid, E0 budgets-reported-not-matched, the committed-core line, CIFAR-100→stretch with the
analytic crossover, E6 derivation-first.)*

---

## 1 · The spine, the envelope, and the guards (non-negotiables — every rung obeys them)

**The spine — read the class DIRECTION, never a MAGNITUDE.** Every noise/drift read is retention under a coherent
shift, never a per-sample magnitude. On real streams the "shift" is nature's (sensor aging, subject identity,
decades) — the read is unchanged.

**The envelope — GD reads taps, never writes SCFF** (the P2.5 wall, unbroken). Both arms obey it by construction.

**Both arms run the LIVE loop.** The object is an online learner: SCFF learns forward-only every step; the namer
tracks drift via the gate + sleep. "Frozen" means **config-frozen** (the recipe), not weights-frozen — weights are
born at init on each arena and learn on the stream, exactly the P8–P10 live convention. (The one deliberate
exception: P11.1's `random-frozen-bulk` cell, weights-frozen at init — the reservoir control, stated.)

**Guards FIRST, every run — the netlist rule.** Import every P8/P9/P10 guard that applies; new P11 guards (§6):
**arena-data** (shape · declared stream order · scaler-freeze · composition table · offline load) · **anchor** (our
ER-strong lands in the published Split-MNIST band, transcribed pre-run; runs the PUBLISHED configuration — raw 784,
the anchor implementation's head convention and buffer; validates the *implementation*, not per-arena strength) ·
**dominance** (ER-strong ≥ naive-BP and ≥ ER-budget on the tuning stream at every arena — an inversion red-flags a
broken tuning, §8 R4) · **floor-criterion** (the informative-cell cut, pinned §2.4 before any run) · **recipe**
(Arm B instances carry bit-equal committed hyperparameters; only {D, W, LUT-cap-by-rule} differ) · **porthole**
(ONE seed-frozen projection per source, applied identically to every learner; bit-identical projected stream across
learners — K5 carried) · **stream-controls** (no-change + sgd-linear-native + first-block-frozen present on every
real-world stream — §8 R5/R11) · **budget-report** (per-cell FLOPs/sample + bytes reported; the matched-vs-reported
status is enumerated per claim in §2.4, never chosen post hoc — §8 R3). **Any guard fails → STOP.**

---

## 2 · The mechanism: the two arms, the deliverables, and the verdict cuts (pinned BLIND)

### 2.1 The two arms (how to scale without breaking the freeze)

- **Arm A — the frozen recipe through the porthole.** The committed P9 config **bit-equal** (D=40, L12/W64, grid-4,
  every knob at its committed value), fresh-init, live-run on the new arena projected to its native 40-D input
  (seed-frozen Gaussian projection, the P10.3 discipline; transforms applied in NATIVE space, then projected).
  Question: **does the frozen recipe survive data it was never shaped on?** (The LUT cap growing with #classes is
  the committed P9.3 *rule*, not a knob move — it stretches lawfully at 30 classes.)
- **Arm B — the scaling recipe (pre-registered).** Instances built by a rule written before any run:
  **D = min(native-D, 160)** quantized to {40, 80, 160} for projected sources (native-D kept when ≤ 160: gas 128,
  covertype 54, electricity 8) · **W = ⌈1.6·D⌉** (the committed 64/40 ratio, held) · **L = 12 fixed** · LUT cap by
  the P9.3 rule · every other hyperparameter bit-equal to committed. Fresh-init, live-run. A rung that will not
  converge under the recipe (invariants: divergence, dead-unit blowup, gate saturation) **is the result** — recipe
  does not transfer; logged, never tuned.

Arm A answers "is the *recipe* robust"; Arm B answers "does the *architecture* scale." Reviewers ask both; they get
different arms. **Neither arm has a tunable anything.**

### 2.2 The deliverables

- **A · the decomposition** (P11.1) — Δbulk per capability channel: is the architecture more than its closed-form
  namer? The strike-1 answer, and the number every later rung carries as an overlay.
- **B · the hardness ladder** (P11.2 + P11.5) — the P10.3 gauntlet + Split class-IL, re-built per rung
  {MNIST, Fashion, CIFAR-gray}, ER-strong re-tuned per rung; the r1 volume sub-arm (60k single-pass — the invariants
  nobody has watched at length).
- **C · the real-world streams** (P11.3, the phase headline) — gas drift (nature's own gauntlet), HAR by-subject,
  Electricity + Covertype (the streaming canon, prequential), Yearbook (bonus). Reversed-order runs where order is
  nature's (gas, yearbook) or pinned (HAR permutation).
- **D · the cross-dataset gauntlet** (P11.4, the author's ask) — MNIST → Fashion → CIFAR-gray as one class-IL
  stream, forward + reversed; the type-of-data robustness read.
- **E · the scaling reads** (P11.5 r2/r3 + class-count · P11.6 capacity · P11.7 throughput) — accuracy, GD-share,
  substrate factor, and safety vs C, W, D, stream length; the crossover figure; shapes pre-derived from the meter
  (§3-P11.0).
- **F · the LIMIT-MAP + the close-out** (P11.9) — the phase money figure: arenas × capability channels, every cell
  **win / tie / loss / FLOOR** with its number; SCALING panels; the report + professor-pack update.

### 2.3 The committed core, the extensions, and the kill criteria (pre-registered)

- **The committed core — the phase can close honestly after it:** P11.0 (bench) + P11.1 (decomposition) + P11.2-r1
  (MNIST rung) + P11.3-gas (the headline stream) + P11.4 (cross-dataset). The LIMIT-MAP ships on the columns that
  exist; everything beyond widens it. *(Solo evening/weekend pace is the constraint this line protects — the map
  must not become a season.)*
- **Extensions (in credibility-per-evening order):** P11.3 remainder (HAR → Electricity → Covertype → Yearbook) →
  P11.5 (r2/r3 + class-count) → P11.6 (capacity) → P11.7 (throughput) → P11.8 (features arena, gated).
- **The stop rule is results-blind (§8 R10):** extensions run in the stated order until a wall-clock budget (pinned
  at bench) expires; any early stop is logged with its *time-based* reason, never a results-based one. The close-out
  may not claim the "streaming canon" or a deployment envelope over columns that don't exist — specifically,
  Electricity + Covertype may not be cited as tested unless their columns exist (win, lose, or FLOOR).
- **Kill criteria:** (i) P11.1 Δbulk ≤ 0 on **every** channel including noise + drift-retention → STOP the ladder;
  the phase's question re-scopes to "what is the bulk for" and goes back to design before more rungs burn time.
  (ii) P11.2-r1 Arm A safety (worst-BWT) breaks at the porthole → Arm A is dead; the phase becomes Arm-B-only (a
  finding: the frozen recipe is digits-shaped). (iii) Any bench guard red → STOP.
- **Pitch timing:** the plan itself is pitchable ("here is the validated object; here is the pre-registered program
  that maps its limits") — run **P11.1 only** pre-pitch (one evening, answers the sharpest strike; either outcome
  you want in hand before the professor asks). The reflection week is not traded.

### 2.4 The numeric verdict cuts (PINNED BLIND — shapes with thresholds, never expected results)

`δ_acc = 0.02` (the house bar), paired by seed; a difference is **real** iff IQR-disjoint at the read point **AND**
sign-consistent in ≥4/5 paired seeds. **The n=3 rule (§8 R9):** heavy live cells run 3 seeds — the list of which
cells is DECLARED at bench, before any variance is seen; at n=3 "real" = 3/3 sign-consistent + non-overlapping
ranges, and **no decisive verdict banks at n=3** (escalate to 5). Decisive gaps ≤ δ_acc get 9 where seed-able — the
P11 escalation set is `SEEDS + [1009, 2027, 9091, 8191]` (**never `p8cfg.SEEDS9`, which contains seed 7 — the ER
tuning seed; §8 F4**). On natural-order streams the 5 seeds vary init/projection only, so the per-stream
significance read is **McNemar on paired prequential predictions** (§8 R9) reported beside the seed IQR. **Balanced
accuracy** replaces plain accuracy on any stream whose composition table shows >3:1 class imbalance (gas; others
per table); **chance = 1/C when the read is balanced accuracy, the majority-class rate otherwise** (§8 R6). Ties
are always captioned with the exact paired delta. **Every cut is a SHAPE fixed before the run.**

- **The FLOOR criterion (the informative-cell cut — C1, pinned by convention BEFORE any run):** a map cell is
  **FLOOR** (grey, uninformative — not win/tie/loss) iff on that arena (a) the joint-BP ceiling < chance + 5·δ_acc,
  **or** (b) every raced learner < chance + 2·δ_acc, **or** (c) on a real-world stream, no raced learner beats the
  no-change baseline + δ_acc on the accuracy channel. A tie at floor is NOT evidence of parity — the far edge of the
  map may be all-FLOOR and that is the honest far edge. **FLOOR is two-sided (§8 R6):** inside every FLOOR cell the
  paired OURS-vs-best-field delta is still computed and annotated — if the field leads by the real-difference bar
  the cell renders **"FLOOR (field leads +X)"**, and the close-out may not treat a FLOOR cell as absence of
  relative information (the anti-hype guard must not become an anti-loss shield). Fraction-of-ceiling (AA /
  joint-AA) is annotated in every non-FLOOR accuracy cell.
- **P11.0 — bench.** *No verdict — build + guards.* Green iff: every dataset loads offline with declared stream
  order asserted; per-arena composition tables + Vergara/van-de-Ven anchor numbers transcribed into the manifest;
  ER-strong re-tuned per arena on the disjoint stream (seed 7 ∉ raced set) with the P10.0 protocol + **the search
  grid pinned in the manifest** (C8); the P11.6 GD-share-vs-W shape **derived from the meter formulas and pinned**
  (§3-P11.0); the floor criterion + all P11 guards green. **Any red → STOP.**
- **P11.1 — the decomposition.** Read Δbulk = (bulk→namer) − (proj→namer) per channel {home AA, worst-BWT, gauntlet
  worst-point retention, noise channels, energy}, budgets **reported** per cell (not matched — removing the bulk
  removes its cost by construction; if proj→namer ties at a fraction of the energy, the strike lands twice and is
  reported so). **(i) architecture confirmed** iff Δbulk > 0 (real-difference bar) on ≥ {noise, drift-retention};
  **(ii) claim narrowed** iff Δbulk > 0 only off-home or only on some channels (name exactly which — the claim
  shrinks to them); **(iii) claim broken** iff Δbulk ≤ 0 everywhere (kill criterion (i) fires — the object's story
  becomes gate+sleep+closed-form-namer). The `random-frozen-bulk` cell separates "12 nonlinear layers exist"
  (reservoir) from "SCFF learned structure"; the no-sleep cells separate the sleep's earn from the bulk's. All
  three verdicts are publishable sentences.
- **P11.2 — the hardness ladder, r1 (MNIST).** Per protocol {5-domain gauntlet (both switch regimes), Split-MNIST
  class-IL, volume 60k}: **(i) bet holds** iff safety (worst-BWT), retention (worst-point, per regime), and
  order-invariance (|fwd−rev| ≤ δ_acc) stay green while static accuracy does whatever it does; **(ii) bet scoped**
  iff they hold at r1 but not beyond (the claim gains a stated resolution ceiling at whichever rung breaks);
  **(iii) bet broken** iff safety breaks where accuracy breaks (continual-safe was arena-bound — headline finding).
  The **anchor cell** (our ER-strong on Split-MNIST vs the published band) gates the instrument: outside the band →
  fix the racer before any verdict is banked. Volume sub-arm reads the length invariants (LUT churn, gate
  fire-rate drift, GD-share drift, namer condition number) — drift in any of them is a named finding, not a failure.
- **P11.3 — the real-world streams.** **The accuracy channel on real streams = prequential (balanced) accuracy
  over the full stream, pre-update, for every learner including no-change** — the 80/20 eval splits feed only the
  retention/BWT channels, and the LIMIT-MAP accuracy cell shows the prequential number (§8 R2 — one metric, pinned,
  no post-hoc choice). Per stream, the P10 instrument (prequential balanced-AA, AAA, worst-BWT, worst-point
  retention, per-batch STREAM view, energy, GD-share) vs {**ER-strong-matched** (byte-matched buffer, the
  substrate-fairness point), **ER-strong-bigbuf** (buffer a tuned axis under the stated cap min(10% of stream,
  5000 samples) — the field-strength point; §8 R3: byte-matching to a class-count-scaled LUT hands ER a near-zero
  buffer on binary streams, so the retention/safety verdict is judged against the STRONGER of the two ER points),
  GDumb, naive-BP, **sgd-linear** (online logistic SGD on NATIVE features, lr tuned on the seed-7 stream — the
  streaming community's default opponent, §8 R11), **first-block-frozen** (train on the first natural block, then
  freeze — the stability-end anchor, §8 R5), no-change, proj→namer carried from P11.1}. **(i) the win** iff
  retention/safety beat the stronger ER (real-difference bar) at prequential accuracy ≥ that ER − δ_acc —
  deployment story complete; **(ii) the honest scoped claim** iff accuracy loses but safety/retention hold **AND
  OURS's prequential accuracy > first-block-frozen + δ_acc** ("safer, not stronger" must not mean "barely
  learning" — a frozen model has perfect retention by construction, §8 R5); **(iii) the loss** iff the stronger ER
  matches our safety on nature's drift (the synthetic gauntlet overstated the differentiator — say so on the money
  figure). Gas is the headline; a cell that fails the no-change cut renders FLOOR (D2), with the R6 delta
  annotation. *(Optional, one seed: an iid-shuffled OURS run per tabular stream — separates drift-difficulty from
  data-difficulty by measurement.)*
- **P11.4 — the cross-dataset gauntlet.** Class-IL 30-way, single growing head for OURS. **Protocol pins (§8 R1 —
  the comparison is ill-defined without them):** single pass, no revisits — each source is ONE contiguous block,
  iid arrival within the block; the gradient learners' label-space handling = **the anchor implementation's
  class-IL head convention** (transcribed and named in the manifest at bench, applied uniformly to every gradient
  learner — head convention moves class-IL numbers by many points and may not vary per learner); class order
  canonical for the anchor cell, seed-varied otherwise. **(i) type-robust** iff worst-point all-prev retention ≥
  the stronger ER − δ_acc AND no dataset-block's classes collapse below chance + 2·δ_acc after the stream ends (the
  LUT/namer keeps all three data types alive); **(ii) type-scoped** iff one block collapses (name which and the
  mechanism — CBRS eviction skew, Gram conditioning, gate saturation at boundaries); **(iii) type-broken** iff
  retention breaks across the board vs ER. Order-invariance read committed (fwd vs rev). Invariant watched: namer
  covariance condition number per sleep (the D-research Q8 risk, instrumented not assumed).
- **P11.5 — the hardness ladder r2/r3 + class-count scaling.** r2/r3: the P11.2 shapes re-read per rung (bet
  holds/scoped/broken); r3 is *expected* to be the accuracy graveyard — it is in the ladder because the map needs
  its far edge, and the FLOOR criterion keeps it honest. Class-count: **find and report the memory-fairness
  crossover C** (fixed-byte replay dilutes per-class as O(1/C); prototype+Gram grows as O(C·D + D²)) — the analytic
  curve from the formulas, measured points at C=10 and C=20 (CIFAR-100 stretch adds C=100); either direction of
  crossover is the result.
- **P11.6 — capacity scaling.** W ∈ {64,128,256} at fixed D=80, then D ∈ {40,80,160} at recipe-W, on the r2 arena
  (one gas check-cell at the recipe point). Reads: accuracy vs W (does capacity buy the gap back, or is the wall
  objective-shaped — P5 said temperature not size; does that stay true at scale?); **GD-share vs W against the
  meter-derived pinned shape** (§3-P11.0 — whatever the formula predicted, the measurement confirms or breaks it;
  both are findings); the substrate factor vs W (P8.7 re-metered — non-decreasing = the chip's best sentence,
  decreasing = better to know now); safety invariants per width (a width where grid-4 cadence breaks safety is a
  finding about the recipe, reported with the invariant that moved).
- **P11.7 — throughput / stream-rate.** Derived per arena from metered FLOPs/sample (the critical rate where a
  learner at k× cost must skip 1−1/k of the stream — the Ghunaim read, computed not simulated) + ONE demonstration
  run on the gas stream. **Pins (§8 R12 — the direction catch, again):** the derivation table prices BOTH learners
  **same-substrate** (analog pricing a separate labeled row, never mixed into one side); the demonstration rate is
  fixed by rule — the geometric mean of the two learners' critical rates — before any run. **(i) the regime win**
  iff a rate exists where ER visibly degrades (skipped samples → AA drop) and OURS doesn't — report the rate;
  **(ii)** if none in the tested range, the economy claim loses its best real-time sentence (reported); **(iii) the
  inversion** iff OURS's critical rate is LOWER than ER's — live, not rhetorical: P10 measured OURS at MORE
  FLOPs/sample same-substrate (96,938 vs 65,268), so under the skip logic OURS falls behind FIRST unless an arena
  inverts the ratio — the real-time economy claim inverts and is reported as such.
- **P11.8 — the features arena (GATED).** Iff the off-box ResNet-18 feature precompute lands: {proj→namer,
  bulk→namer, ER-strong} on frozen 512-D CIFAR features vs published SLDA/RanPAC anchors. The bulk-vs-no-bulk cell
  on a *supervised* encoder plausibly nulls — that null cleanly scopes the bulk to raw-sensor regimes (the chip
  story) and is banked as such, not as a defeat. Dropped without shame if no network window (§5 names it).
- **P11.9 — the LIMIT-MAP + close-out.** Assemble the map (every cell win/tie/loss/FLOOR + number + Δbulk overlay
  where measured), the SCALING panels, the crossover figure; write the phase report + README; update the professor
  pack; bank the owed deltas (§7). *Not a scalar; the map IS the verdict.*

**No result may be narrated into a branch it does not numerically satisfy.** A broken rung, a FLOOR column, a
crossover in ER's favor, a Δbulk null — each is a card with its mechanism (failures are data).

---

## 3 · The ladder — P11.0 → P11.9 (one variable per rung; guards first; reads pinned above)

- **P11.0 — bench: data + loaders + the fair racer per arena + the guards + the two pre-derivations.** ONE
  deliberate network session: fetch Fashion-MNIST (40996), Gas (UCI), HAR (UCI), Electricity (151), Covertype
  (150/1596), best-effort Yearbook + BloodMNIST + CIFAR-100 (41983) — checksums + shapes + **declared stream order
  asserted** into the manifest (electricity chronological; covertype file order; gas batch order; HAR subject
  blocks; yearbook year order); everything after runs offline; UCI flakiness fallback = manual browser download.
  Write `load_<arena>_split(seed, n_train, n_test)` loaders (the house signature). Build the per-arena ER-strong
  tuning harness — P10.0 protocol, disjoint seed 7, **the search grid pinned HERE, not at bench (§8 R4):**
  lr ∈ {0.3, 0.1, 0.03, 0.01} × replay-ratio ∈ {1, 2, 4} × hidden ∈ {`race_bp`-selected, 2×, 4×} (the capacity axis
  scales with native D), selection = final AA on the seed-7 stream, chosen config in the manifest; the **dominance
  guard** (ER-strong ≥ naive-BP and ≥ ER-budget on the tuning stream) red-flags a broken tuning at every arena.
  Build the stream controls (no-change · sgd-linear · first-block-frozen), the balanced-accuracy read, the
  composition tables, the anchor transcription (van de Ven Split-MNIST ER band; Vergara gas numbers) — **the
  anchor cell runs the PUBLISHED configuration** (raw 784, published head convention and buffer), not the porthole.
  **Declare the heavy-cell list** (which cells run 3 seeds) here, before any variance is seen (§8 R9). **Pre-derivation 1 (C3):** GD-share-vs-W from the meter formulas — the namer reads the
  all-tap stack (`all_tap_feats`, F ≈ L·W: 768 → 3072), so its per-update cost scales ~O(F²)=O(L²W²) and any sleep
  solve ~O(F³) — derive the actual metered terms from `hardware_cost_meter`/`meter_from_trace` code (NOT from
  memory: the temp2 concept pre-registered "economy improves with scale" from an O(D·C+D²) formula whose D is the
  wrong variable — this project's recurring killer is direction; derive, then pin). **Pre-derivation 2:** numpy
  wall-clock pre-estimates for the widest cells. Repo-fit pre-verdict (§8 F5): `sleep_fit`→`_solve` DOES run a full
  `np.linalg.inv` on the tied F×F shrinkage covariance — one solve, not per class — **and `partial_fit` also solves
  on every gated awake fire**, so solves/run = sleeps + fires (count both); at P10-measured fire/sleep counts the
  widest P11.6 cell is **minutes-scale, an evening at worst** — confirm at bench. One apparatus fix required
  before Arm B at F ≥ 2460: `_solve`'s C×F×F einsum temp (~755 MB float64 at F=3072) is re-expressed as a GEMM in
  p11lib (an apparatus-efficiency change, no learned knob). A cell projected > an evening is descoped/reshaped at
  bench, not discovered mid-run. **Read (incl. failure):** *all green → proceed; any data/order/anchor/guard red →
  STOP (a broken bench poisons every verdict).*
- **P11.1 — the decomposition (strike 1; ONE evening; apparatus exists).** Cells on the digits home + the P10.3
  gauntlet, 5 seeds: `proj→namer` (the strike) · `bulk→namer` (committed — **re-used from P10 caches, not re-run**)
  · both `no-sleep` variants · `random-frozen-bulk→namer` (dim-matched reservoir control). Budgets reported.
  **Read:** Δbulk per channel → confirmed / narrowed / broken (§2.4). *Run this before the pitch.*
- **P11.2 — the MNIST rung (r1; both arms).** (a) the 5-domain gauntlet — the P10.3 formulas in native 784-space
  (identity / frozen-permutation / rot90 / 3x+4 / noised) → porthole. **The noised domain is pinned by
  NOISE-TO-SIGNAL EQUIVALENCE with P10, not the "0.6×RMS" shorthand (§8 F3 — the direction/scale family, caught
  pre-run):** P10's code adds σ = 0.6 ABSOLUTE on inputs whose RMS ≈ 0.484, i.e. σ/RMS ≈ 1.24 — the rung rule is
  σ_rung = (0.6 / RMS_P10-digits) × RMS_rung, constants computed once at bench from the P10 train split, frozen
  (the C4 "0.6×RMS" rule would have made r1's noised domain ~2× milder than r0's, confounding the ladder on the
  exact domain that drives the retention differentiator); **name the correspondence:
  the permuted/rotated domains ARE the field's Permuted-/Rotated-MNIST** (C6); **two switch regimes committed at
  r1**: rapid-24 (P10.3 continuity) + long-randomized [50,70] blocks (the E8 convention — primary from here on,
  because P10 showed rapid-switch flatters OURS; don't keep racing only in the regime that favors us); (b)
  Split-MNIST class-IL (5×2, `CISTREAM_TASKS` machinery) + **the anchor cell** (our ER vs the published band);
  (c) the volume sub-arm: 60k single-pass online, Arm B (D=80/W=128), 3 seeds, length invariants. NTR=1200/domain
  held; **NTE=2000** where the test pool allows (test-side only — C7). **Read:** bet holds / scoped / broken;
  anchor in/out of band.
- **P11.3 — the real-world streams (the headline).** Gas first (Arm A porthole-40 + Arm B native-128; scaler fit on
  batch 1 ONLY, frozen; balanced accuracy; forward 1→10 + reversed 10→1; seeds vary init+projection only — nature
  fixed the order; Vergara anchor + Dennler limitations cited on the figure). Then HAR (561→porthole + Arm B
  D=160-projected; stream by subject, subject order seed-shuffled, reversed committed). Then the streaming canon:
  Electricity (native-8; Arm B W=13 — the recipe's small end, itself a read) + Covertype (native-54; first-N slice
  in file order, N pinned at bench ~50k, 3 seeds) — prequential, no-change mandatory. Yearbook bonus if the
  download landed (stream by year-bins; real vision drift). Every stream: the per-batch STREAM view (A1) + the
  P10 metric set + proj→namer carried in as the decomposition's real-world read. **Eval convention (pinned):** the
  live-batch read is prequential (pre-update, no split needed); retention/BWT reads use a seed-split 80/20
  train/eval **within each natural block** (eval samples never trained on; retention = accuracy on all previous
  blocks' eval splits). **Power pins (§8 R8):** blocks whose eval split lands < 100 samples are EXCLUDED from
  worst-point/BWT reads (excluded blocks listed on the figure — gas batches 4/5 (161/197 samples) will trip this);
  classes absent from a block are dropped from that block's balanced mean (stated); per-block eval-n is printed on
  the STREAM composition strip so the reader can weight the sag/recovery story. **Read:** win / scoped ("safer, not stronger") / loss per stream (§2.4); FLOOR where
  no-change wins.
- **P11.4 — the cross-dataset gauntlet (the author's ask).** MNIST → Fashion → CIFAR-gray (**center-cropped
  32→28 so all three sources share the 784 native space**), class-IL 30-way (class-offset labels 0–29), **single
  pass, one contiguous block per source, iid within block** — "long-randomized blocks" does not apply to a
  no-revisit stream (§8 R1); NTR=1200 / NTE=2000 per block, forward + reversed, both arms, 5 seeds. **Porthole
  (primary — the P11.3-consistent discipline, §8 R7):** ONE shared seed-frozen 784→D projection + unit-RMS scaler
  fit on SOURCE 1's train split only, frozen — future sources arrive uncalibrated (the honest gain-shock read; no
  future data touches the stream's front). **Secondary (declared easier):** per-source projection + per-source
  unit-RMS — measures how much of any break is pure gain/scale shock. Baseline head convention per §2.4-P11.4.
  Watch: Gram/covariance condition number per sleep; CBRS class-composition of the LUT at stream end (did all
  three types survive?); gate fire pattern at dataset boundaries. **Read:** type-robust / type-scoped (name the
  block + mechanism) / type-broken (§2.4).
- **P11.5 — Fashion + CIFAR rungs (r2, r3) + class-count scaling.** r2/r3: the P11.2 protocol minus volume (Arm B
  primary D=80/D=160; Arm A the cheap extra column); the FLOOR criterion does the honesty at r3. Class-count: the
  analytic crossover curve + measured C=10 (r1 Split) and C=20 (MNIST+Fashion joint, 10 tasks × 2 classes);
  CIFAR-100 (C=100) stretch-only. **Read:** bet holds/scoped/broken per rung; the crossover C reported (either
  direction).
- **P11.6 — capacity scaling.** As §2.4: W-sweep at D=80 on r2 (one-variable), D-sweep at recipe-W, gas check-cell;
  5 seeds where wall-clock allows, else 3 declared; per-width invariants. **Read:** the meter-derived shape
  confirmed/broken; substrate factor vs W; the width (if any) where safety breaks + which invariant moved.
- **P11.7 — throughput.** The derivation table (per arena, per learner, from metered FLOPs/sample) + one gas
  demonstration. **Read:** the critical-rate table; the regime win or its absence.
- **P11.8 — the features arena (GATED on the off-box precompute; decide at the bridge, not now).**
- **P11.9 — the LIMIT-MAP + the close-out.** Assemble; write; update the professor pack; bank §7.

*(Seeds `[42,137,271,314,1729]`, median + IQR; heavy live cells 3 seeds declared. Heavy cells checkpoint +
`OMP_NUM_THREADS=1` + `python -u` + verify the real PID — the phantom-hang discipline. CPU float64; no sklearn/River
for compute — loaders may use sklearn's `fetch_openml` cache path at BENCH ONLY, never inside a live cell.)*

**Dependency order:** P11.0 gates everything. P11.1 has no data dependency (digits — run any time, ideally
pre-pitch). P11.2 needs MNIST (cached); P11.3-gas needs the UCI fetch; P11.4 needs r1+r2+r3 loaders; P11.5–P11.8
extend. P11.9 assembles whatever exists (the committed-core line, §2.3).

---

## 4 · Metrics (PINNED; Phase-11 additions in **bold**; the rest carried bit-for-bit from P10 §4)

| metric | definition (pinned) | units / format |
| --- | --- | --- |
| AA / AAA / BWT / worst-pre-sleep reads / plasticity / 1-back / Pareto point / energy (algorithm same-substrate + total floor-flagged) / throughput / GD-share / fair-budget audit / sleep-position overlay | **carried from P10 §4 unchanged** (worst-pre-sleep convention on the fixed learner-independent checkpoint grid; ER at the same convention) | as P10 |
| **Δbulk (per channel)** | (bulk→namer) − (proj→namer), per capability channel, per arena where the decomposition runs; budgets reported per cell | acc-delta / ratio |
| **balanced accuracy** | mean per-class recall; REPLACES plain accuracy on any stream whose composition table shows >3:1 imbalance (gas; per-table elsewhere); the composition table itself is a bench artifact | acc, median [IQR] |
| **no-change (persistence) baseline** | predict the previous label; mandatory line on every real-world stream (D2); part of the FLOOR criterion | acc |
| **fraction-of-ceiling** | AA / joint-BP-ceiling-AA on the same arena (the joint ceiling runs per arena — C2); annotated in every non-FLOOR accuracy cell | fraction |
| **order-invariance Δ** | |AA(fwd) − AA(rev)| per learner per arena (committed wherever a reversed run exists) | acc-delta |
| **length invariants** | LUT churn · gate fire-rate (per-rung — C5) · GD-share drift · **namer covariance condition number per sleep** (the P11.4/volume conditioning watch) | per-run traces |
| **cell state** | win / tie / loss / **FLOOR** per LIMIT-MAP cell (the §2.4 criterion; FLOOR is grey, never counted as a tie; **FLOOR cells still annotate the paired OURS-vs-field delta** — "FLOOR (field leads +X)" when real, §8 R6) | categorical + number |
| **paired stream test** | McNemar on paired prequential predictions over the single natural-order stream — the significance read where seeds cannot resample the stream (§8 R9); reported beside the seed IQR | p-value / flag |

**Threats-to-validity, every rung (carried P10 (a)–(h) + the P11-new):** (i) **projection loss** — the porthole
(→40) discards information; Arm B's native/larger-D instances bound how much (state per arena); (ii) **stream-order
provenance** — covertype has no timestamp (file-order convention stated, not invented); HAR subject order is
arbitrary (seed-shuffled, declared); (iii) **the gas dataset's published limitations** (Dennler 2022) — cited on
the figure, balanced accuracy + composition table respond to it; (iv) **anchor transcription** — published numbers
are transcribed pre-run into the manifest (the anchor guard), so "our ER is field-strength" is checkable, not
asserted; (v) **real streams have one natural order** — seeds vary init/projection only; order-resampling exists
only where order is not nature's (HAR); (vi) **NTE asymmetry across arenas** — NTE raised test-side only where the
pool allows (training budgets untouched); stated per arena in the manifest.

---

## 5 · What Phase 11 hands off / does NOT claim (write it in the report before the first run)

- **No raw-vision-at-scale claim** (ImageNet/CORe50/CLEAR-raw untouched; CLEAR cite = `2201.06289`, fixed — D7).
- **P11.8's features results (if run) are not chip results** — the chip's front brain is grown, not downloaded; the
  cell is a comparability bridge, labeled so in its first sentence.
- **No PVT/analog realism** — behavioral meter throughout; **→ the analog-realism layer** (unchanged next phase),
  which also inherits whatever directional/ADC residual the real-world noise reads surface.
- **No recurrence / north star.**
- **→ a future draft (flag, never execute here):** anything the map shows that would move a frozen Stage-1/2
  decision (a convolutional/larger bulk for the static gap; a changed namer for the conditioning risk if P11.4
  breaks it).
- **Losses stay in the map.** The LIMIT-MAP ships with its red and grey cells — that is the deliverable, per the
  author: *"I don't care even we lost, it still more good than no one know that limit."*

---

## 6 · What to build — `p11lib.py` on `p10lib` (import, don't retype — the netlist rule)

**Verified-present carries (import):** the whole P10 stack — `awake_sleep_loop`/`run_economy_p9`,
`SLDAHeadStream` (+ `partial_fit`/`sleep_fit`), `make_committed_cell`, `StreamingLUT` + `evict_cbrs`,
`proto_reanchor`, `acc_matrix_metrics`, `hardware_cost_meter`/`meter_from_trace`/`bp_replay_energy`, `ContinualBP`
(er/agem/derpp/gdumb/naive — P10's real racers), `joint_bp_ceiling`, `fair_budget_meter`/`fair_budget_guard`,
`make_gauntlet_stream`/`load_gauntlet_data` (+ the →40 projection discipline), `throughput_meter`,
`pareto_frontier`, `cl_metrics` (**NOTE §8 F1: the name `gauntlet_metrics` from the P10 design does NOT exist in
code** — the new/1-back/all-prev retention helper lives inline in `run_p10_3.py:82-85` and is PORTED into p11lib),
the GAUNTLET-STREAM replay machinery (live/seen/cume/sleeps/fires arrays), `race_bp` (config selector) + `MLP`,
`load_digits_split`/`load_cifar_flat`, `CISTREAM_TASKS`, `NoiseModel`/`infer_noisy`, **all P8/P9/P10 guards**.
Committed config (**§8 F2 — the wrong-module trap**): **`p10lib.COMMITTED_LOOP`** (which bakes `cadence_every=8` —
override to **4**, the documented Trap-1) + **`p10lib.HEAD` (= "slda")**; DIM=40 + `[64]*12` live in `p8cfg`.
`p8cfg` has NO `COMMITTED_LOOP` and NO `HEAD` — and its `COMMITTED_HEAD="ranpac"` is the P7-era head, a silent
wrong-head trap if read naively.

**NEW to build (each names the deliverable it serves):**
- **`load_<arena>_split(seed, n_train, n_test)` loaders + `arena_data_guard`** (P11.0; deliverables B/C/D) —
  {mnist, fashion, cifar10gray, gas, har, electricity, covertype, yearbook?, bloodmnist?, cifar100?}; asserts
  shape/dtype/class-set/**declared stream order** (electricity chronological by date+period; covertype file order;
  gas batch column; HAR subject blocks; yearbook year); scaler policy per arena (**fit on the first natural block
  only, frozen** — gas batch 1, electricity/covertype first slice, per-source for E7); emits the **composition
  table** into the manifest. Bench-only network; live cells load from the local cache.
- **`make_arena_stream(arena, seed, *, arm, regime)` (P11.2–P11.5)** — generalizes `make_gauntlet_stream`: the
  5-domain synthetic gauntlet per rung (native-space transforms → porthole; σ_noise pinned by P10 noise-to-signal
  EQUIVALENCE, σ_rung = (0.6/RMS_P10-digits)·RMS_rung, computed once at bench, frozen — §8 F3 supersedes the C4
  shorthand), the two switch regimes (rapid-24 / long-randomized [50,70] non-multiples of 24), the real-stream
  wrappers (natural blocks), the cross-dataset stream (shared source-1-fit porthole primary / per-source secondary
  — §8 R7; class-offset labels 0–29; CIFAR center-crop 32→28 to share the 784 native space), forward/reversed.
- **`decomp_cells(...)` (P11.1; deliverable A)** — `proj→namer` (the frozen →40 projection straight into
  SLDA+gate+sleep), `no-sleep` variants, `random-frozen-bulk` (committed cell, weights frozen at init); the
  `bulk→namer` carry = **the P10 result arrays** (exp1/exp3/exp4 `arrays.npz` keys: `acc/bwt/aaa/energy_ours_g4*`,
  `allprev_g4`, `orderdelta_g4`, `dirret_ours_*`), snapshot-then-diff bit-exact — **NO model-state cache exists on
  disk** (the in-memory 4.4-GB discipline); any re-forward is a guarded deterministic rebuild (§8 F7). Emits
  `dbulk_<channel>` arrays.
- **`nochange_baseline(...)` + `stream_controls_guard` (P11.3; D2/R5/R11)** — predict-previous-label; plus
  **`sgd_linear(...)`** (ten-line numpy online logistic SGD on NATIVE features, lr tuned on the seed-7 stream — the
  streaming community's default opponent, in the roster and the FLOOR raced set) and **`first_block_frozen(...)`**
  (train on the first natural block, freeze — the stability-end anchor giving branch (ii) its learning floor); the
  guard asserts all three are present on every real-world stream.
- **`er_strong_bigbuf` roster point (P11.3; R3)** — ER-strong with the buffer a tuned axis under the stated cap
  min(10% of stream, 5000 samples); the field-strength complement to the byte-matched point.
- **`mcnemar_stream(...)` (P11.3; R9)** — McNemar over paired prequential predictions on the single natural-order
  stream; the per-stream significance read.
- **`anchor_guard(...)` (P11.2; D5)** — asserts the manifest carries the published Split-MNIST ER band
  (transcribed at bench, source pinned) and that our ER-strong's number lands inside it — **run at the PUBLISHED
  configuration** (raw 784, published head convention/buffer, §8 R4); red = fix the racer, no verdicts bank.
- **`dominance_guard(...)` (P11.0; R4)** — ER-strong ≥ naive-BP and ≥ ER-budget on the tuning stream, per arena.
- **`recipe_instance(D)` + `recipe_guard` (Arm B)** — builds {D, W=⌈1.6·D⌉, L=12, LUT-cap-by-P9.3-rule} with every
  other knob bit-equal to `COMMITTED_LOOP`; the guard diffs the config against committed and whitelists only
  {D, W, cap}.
- **`floor_state(...)` (P11.9; C1)** — applies the §2.4 FLOOR criterion per cell; emits the LIMIT-MAP cell states.
- **`meter_share_derivation(...)` (P11.0; C3)** — walks the meter's own per-op counts symbolically in W (bulk
  ~L·W² per step; namer update ~F², F = L·W; sleep-solve term as the code actually prices it) and writes the
  predicted GD-share-vs-W curve + the wall-clock pre-estimates into the bench manifest — the P11.6 pinned shape.
- **`condition_trace(...)` (P11.2 volume / P11.4)** — logs the namer covariance/Gram condition number at every
  sleep (the conditioning invariant).
- **`crossover_curve(...)` (P11.5)** — the analytic bytes-vs-C for replay (fixed bytes / C per class) vs
  prototype+Gram (O(C·D + D²)), drawn from the fair-budget meter's own byte counts; measured points overlaid.
- **Figures:** `plot_p11.py` — `fig_limit_map` · `fig_decomp` · `fig_stream(arena)` (the generalized per-batch
  view, A1 — carried GAUNTLET-STREAM machinery + no-change line + anchor line + composition strip where natural
  blocks exist) · `fig_scaling` · `fig_crossover` · carried `fig_fight`/`fig_pareto`/`fig_inv` per arena. STYLE =
  `{**plot_p10.STYLE, **P11_NEW}` (the binding contract: [`result-format.md`](result-format.md)).

**Apparatus discipline (carry verbatim):** `manifest.json` (git hash + config + seeds + versions + wall-clock +
meter params + **anchors transcribed + composition tables + stream-order assertions + the pinned P11.6 shape +
the heavy-cell declaration**) + `arrays.npz`; `plot_p11.py regen <run-dir>`; `_ckpt.jsonl` fsync'd; commit per rung
(`feat(draft6/phase11): …`). **Escalation seeds:** the P11 9-seed set = `SEEDS + [1009, 2027, 9091, 8191]` —
**`p8cfg.SEEDS9` is NOT used: it contains seed 7, the ER tuning seed (§8 F4; latent in P8–P10, fixed here).**

---

## 7 · Owed decision-record deltas (flag at close; never retro-edit frozen files)

To bank to [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) at close (S15, the way S10–S14 were):
- **The decomposition verdict** — Δbulk per channel: the architecture claim confirmed / narrowed / broken (the
  strike-1 answer, on the record).
- **The limit map** — the validated arena envelope of the committed object (which columns green, which red, which
  FLOOR — the honest deployment envelope for the pitch and the analog layer).
- **The recipe-transfer verdict** — does the frozen recipe survive the porthole (Arm A) and does the
  scaling rule transfer (Arm B); any rung where it refused, named.
- **The economy-at-scale verdict** — GD-share vs W against the meter-derived shape; the substrate factor vs W; the
  crossover C.
- **The real-world verdict** — nature's-drift performance (gas headline): win / safer-not-stronger / loss, with the
  per-batch money figure.
- **The type-robustness verdict** (P11.4) — the cross-dataset read; any conditioning/eviction mechanism finding.

---

## 8 · The lab-manager review ledger (3-agent pre-run review — FOLDED 2026-07-05)

Three cold-start reviewers: **red-team** (hostile outside CL/streams reviewer — SOUND-WITH-FIXES, 12 findings),
**repo-fit** (inside, plan vs code reality — READY-WITH-FIXES, 8 findings), **literature/stats** (every citation +
number verified — SOUND-WITH-FIXES, 3 minors, *zero wrong arXiv IDs or dataset facts*). Every finding adjudicated
by the lab manager (full session context); all accepted (some modified); all folded above. R = red-team,
F = repo-fit, L = literature.

| # | sev | finding | resolution (where folded) |
| --- | --- | --- | --- |
| R1 | BLOCKER | class-IL label-space handling for gradient learners unpinned (fixed-30 head? masked? growing?) — moves class-IL numbers by many points; block arrival/revisit semantics undefined | pinned: the anchor implementation's class-IL head convention, uniform across gradient learners; single pass, no revisits, iid within block; canonical class order for the anchor cell (§2.4-P11.4/§3-P11.4) |
| R2 | BLOCKER | two accuracy numbers exist per real stream (prequential vs eval-split) — the win cut + FLOOR each need exactly one; no-change is only defined prequentially | pinned: **the accuracy channel on real streams = prequential (balanced) accuracy, pre-update, every learner incl. no-change**; 80/20 splits feed retention/BWT only; the LIMIT-MAP shows the prequential number (§2.4-P11.3) |
| R3 | MAJOR | byte-matching ER's buffer to a class-count-scaled LUT hands ER a near-zero buffer on binary/long streams — a structural cripple exactly on the new arenas; "matched where claimed" was an unpinned degree of freedom | two ER points on real streams (byte-matched + **bigbuf**, cap min(10% of stream, 5000)); retention/safety judged vs the STRONGER; matched-vs-reported enumerated per claim (§2.4-P11.3/§1) |
| R4 | MAJOR | the anchor guard certifies the implementation, not per-arena strength ("retires the strawman at every rung" overreached); the ER grid was deferred to bench with no capacity axis | D5 scope corrected; the grid pinned IN THE SPEC (lr × replay-ratio × hidden with a capacity axis); dominance guard added; anchor cell runs the published config (§0.4-D5/§1/§3-P11.0) |
| R5 | MAJOR | "safer, not stronger" has no learning floor — a frozen model wins retention by construction; no stability-end anchor in the roster | `first-block-frozen` baseline added to every real-stream roster; branch (ii) additionally requires OURS > frozen + δ_acc (§2.4-P11.3) |
| R6 | MAJOR | FLOOR criterion (c) erases floor-LOSSES (Electricity predictably all-FLOOR with ER possibly ahead); "chance" undefined under imbalance | FLOOR made two-sided: the paired delta annotated in every FLOOR cell ("FLOOR (field leads +X)"); chance pinned = 1/C under balanced accuracy, majority-rate otherwise; ties always captioned with the delta (§2.4/§4) |
| R7 | MAJOR | per-source normalization on the cross-dataset stream uses future data + pre-equalizes the gain shock under test; three independent projections make inter-source geometry an artifact | primary flipped to the P11.3-consistent discipline: ONE shared porthole + scaler fit on source 1 only; per-source demoted to declared-easier secondary; CIFAR center-crop 32→28 shares the native space (§3-P11.4) |
| R8 | MAJOR | gas retention statistics unpowered/undefined: 161-sample batches → ~32-sample eval splits; absent classes make per-class recall undefined; worst-point min-statistic dominated by the smallest blocks | pre-registered: min per-block eval n ≥ 100 for worst-point/BWT reads (excluded blocks listed on the figure); absent classes dropped from the balanced mean (stated); per-block eval-n printed on the composition strip (§3-P11.3 note below) |
| R9 | MAJOR | "≥4/5 sign" undefined at n=3; IQR of 3 = the range; on natural-order streams 5 seeds measure init noise only — no per-stream significance read | n=3 rule pinned (3/3 sign + disjoint ranges; no decisive verdict at n=3); heavy-cell list declared at bench; **McNemar on paired prequential predictions** added (§2.4 preamble/§4/§6) |
| R10 | MAJOR | committed-core + results-seen extension choice = optional stopping over which arenas the map shows | stop rule made results-blind (wall-clock budget, time-based reasons logged); no streaming-canon claim without Electricity+Covertype columns (§2.3) |
| R11 | MAJOR | no native-feature online linear baseline — the streaming community's default opponent absent on the tabular streams | `sgd-linear` (native features, tuned on seed-7) added to every real-stream roster + FLOOR raced set; optional iid-shuffled OURS control noted (§2.4-P11.3/§6) |
| R12 | MINOR | P11.7's branches presumed the cost inequality favors OURS — P10 measured the opposite (96,938 vs 65,268 FLOPs/sample); the demo rate was chooseable post-derivation | branch (iii) "the inversion" added (live, not rhetorical); same-substrate pricing both sides pinned; demo rate = geometric mean rule (§2.4-P11.7) |
| F1 | MAJOR | `gauntlet_metrics` listed as a verified carry but does not exist in code (prose only; the helper is inline in `run_p10_3.py`) | §6 corrected: `cl_metrics` + port the run_p10_3 retention helper into p11lib |
| F2 | MAJOR | committed-config cite pointed at the wrong module (`p8cfg` has no `COMMITTED_LOOP`/`HEAD`; its `COMMITTED_HEAD="ranpac"` is a silent wrong-head trap; the real dict bakes cadence=8) | §6 corrected: `p10lib.COMMITTED_LOOP` (+ 8→4 override, Trap-1) + `p10lib.HEAD`; DIM/`[64]*12` attribution to p8cfg kept |
| F3 | MAJOR | the C4 "σ = 0.6×RMS" rule mischaracterizes P10's noised domain (code adds σ=0.6 ABSOLUTE on RMS≈0.484 inputs ⇒ σ/RMS≈1.24) — r1's noised domain would be ~2× milder than r0's, confounding the ladder | pinned by noise-to-signal EQUIVALENCE: σ_rung = (0.6/RMS_P10-digits)·RMS_rung, constants at bench, frozen (§3-P11.2/§6) — the house's direction/scale killer, caught pre-run |
| F4 | MAJOR | `p8cfg.SEEDS9` contains seed **7** — the ER tuning seed — so 9-seed escalation races the tuning stream (latent in P8–P10) | P11 escalation set = SEEDS + [1009, 2027, 9091, **8191**]; SEEDS9 never used (§2.4/§6) |
| F5 | MINOR | the solve pre-estimate must count gated-fire solves too (`partial_fit` also solves) and the C×F×F einsum temp (~755 MB at F=3072); feasibility verdict: **minutes-scale, not days** | folded into P11.0 pre-derivation 2 (+ the einsum→GEMM apparatus fix, no learned knob) (§3-P11.0) |
| F6 | MINOR | the P11 arrays schema dropped P10's substrate suffix on the cume key | `streamcume_<cfg>_<arena>_<substrate>` pinned (result-format §A) |
| F7 | MINOR | "re-used from P10 caches" — no model-state cache is persisted; what persists is the result arrays | §6 names the actual carry (exp1/exp3/exp4 array keys) + guarded deterministic rebuild |
| F8 | MINOR | strike-2 sentence was itself falsifiable (CIFAR-flat probes exist; home NTR=4000) | §0.0 reworded to the precise sentence |
| L1 | MINOR | BloodMNIST is RGB 28×28×3 (2352-D), not 784 | dims corrected (§0.4-D4 + research README) |
| L2 | MINOR | openml id 150's full-data equivalence to 1596 unconfirmed | pin 1596; 150 dropped (§0.4-D6 + research README) |
| L3 | MINOR | gas collection start-year differs across sources (UCI page vs Vergara citation) | resolved at bench transcription (the anchor step already scheduled); no file change |

**Checked and kept as-is (defended by the reviewers):** the joint-BP ceiling as a pooled-data *reference line*
(never raced); per-arena ER re-tuning while OURS stays config-frozen (the asymmetry runs against the home team);
long-randomized blocks as primary *because* rapid-switch flatters OURS; Electricity v1-not-v2; covertype file-order
stated-as-convention; gas batch-1 scaler freeze; the Arm A/B split + recipe-guard whitelist; Δbulk
budgets-reported-not-matched with the strike-lands-twice clause; the kill criteria + P11.1-before-pitch; every §6
carry name EXCEPT `gauntlet_metrics` verified importable at its stated location; the P10.3 gauntlet formulas
(transforms, seeds 9999/12345, native-space-then-project) verified except the noise σ (F3); the data-cache claims
verified on disk; every load-bearing arXiv ID, attribution, and dataset number verified correct (incl. the exact
gas batch sizes and Yearbook's 33,431).

*(R8's pins, restated where they land: min per-block eval n ≥ 100 for worst-point/BWT reads with excluded blocks
listed; absent classes dropped from the balanced mean; per-block eval-n on the composition strip — §3-P11.3's eval
convention + result-format §C.)*

---

## Grounding (what the field does — and what we adopt)

- **The fair budgeted fight + the strong-ER convention** — carried from P10 (Prabhu CVPR'23 `2303.11165`; Ghunaim
  CVPR'23 `2302.01047`); ER-strong re-tuned **per arena** on the disjoint stream, grid pinned.
- **The cross-dataset protocol** — 5-Datasets (Ebrahimi et al., ECCV 2020 `2003.09553`); ours the 3-block class-IL
  variant (harder than the field's task-IL, stated) → P11.4.
- **The streaming canon + prequential** — Electricity/Covertype, Gama's conventions; the **no-change baseline**
  trap on autocorrelated streams (Souza et al. 2020) → P11.3 + the FLOOR criterion.
- **The real-drift arenas** — Gas (Vergara 2012; limitations: Dennler 2022 — cited preemptively); HAR (UCI);
  Wild-Time Yearbook (Yao NeurIPS'22 `2211.14238`); MedMNIST (Yang, Sci Data '23 `2110.14795`) → P11.3.
- **The scenarios + the anchor** — van de Ven `1904.07734` / Nat MI 2022 + the official implementation's published
  Split-MNIST numbers as the instrument-validation band → P11.2.
- **The frozen-backbone convention** (Deep SLDA `1909.01520`; RanPAC `2307.02251`) — the P11.8 bridge arena and
  the reason the field's own topology matches the bulk+namer split.
- **The meter + substrate 2×2** — carried from P8 (behavioral, ADC-centred; the analog factor a meter-structural
  floor, never the contestable claim). Full delta: [`../../research/papers/phase11/README.md`](../../research/papers/phase11/README.md).

> The **floor**, per [`../result-format.md`](../result-format.md) + [`result-format.md`](result-format.md): median +
> IQR, 5 seeds (3 declared on heavy live cells), reference lines (chance · per-arena joint ceiling · ER-strong ·
> no-change on real streams), a caption ending in the takeaway, a manifest that regenerates every figure. **The
> recipe is frozen; we measure where it holds and where it breaks, and ship the map — wins, losses, and floors.**

*Up:* [draft context](../../CLAUDE.md) · *prev:* [Phase 10 — validation](../phase10/README.md) (closed, S14) ·
*next:* the analog-realism layer (SPICE/PVT), and beyond the numbered phases, the north star.
