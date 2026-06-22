# Phase 4 — Characterize the new cell: a capability map vs backprop

> **Status: ✅ COMPLETE (2026-06-22, P4.0 → P4.7).** The capability map is built — synthesis:
> [`phase4-summarize.md`](phase4-summarize.md), ledger: [`RESULTS.md`](RESULTS.md), the assembled map:
> [`figs_summary/CAPABILITY_MAP.png`](figs_summary/CAPABILITY_MAP.png). **Verdict: a substrate-native continual
> learner, not a static-accuracy competitor** — WINS continual (A6, decisive), nuisance-dim (A2), depth-composition
> (A3), depth-is-cheap (A4, the 80/20 is depth-gated); TRAILS on static difficulty (A1) / class-count (A5); an
> honest NEGATIVE on eval-time noise (A7 — layernorm tradeoff; train-with-noise is the real test). No algorithm bug
> hid in the breadth. **Phase 5 = optimize the continual win (sleep/gate).** The original plan follows below.
>
> ---
>
> _(plan, as written before the runs:)_ Phase 3 adopted a *new* SCFF objective —
> `[contrast (InfoNCE) + cross-layer coordination w≥2] bulk + sleep-consolidated readout`. It changed the cell at
> the objective level, so **every Phase-1/2 performance number is dead as a reference** (they measured
> energy-goodness SCFF). Phase 4 builds a fresh **capability map**: where does this cheap, forward-only brain
> *close or open* the gap to backprop, across controlled task regimes — so Phase 5 (optimize) picks its battles
> from data, not guesses. **Characterize before optimize.** Reporting contract: [`result-format.md`](result-format.md).
> Literature behind the method: see §9.
>
> **Phase map (re-scoped 2026-06-22, with the author):** Phase 4 = **characterization** (this); Phase 5 =
> **optimization** (the gate + sleep-cadence + whatever P4 flags). The old "Phase 4 = maintenance" content folds
> into Phase 5 — you tune the maintenance loop *after* you know the model's behaviour. P4 runs a *fixed default*
> sleep so the continual cells run at all.

---

## 0. Why Phase 4 exists — and what it is NOT

**Why.** The adopted cell is new. We know three things about it (P3.2/P3.3): it *composes depth given headroom*,
and it *re-earns the continual win*. We do **not** know its shape across regimes — where it matches backprop,
where the gap opens, what it costs, where it's weak. Optimizing (Phase 5) without that map is optimizing blind.

**Phase 4 is the last checkpoint before we go farther** — a thorough pass over *everything* about the adopted
cell, run for **coverage, not triage**. Phase 5 then optimizes the maintenance loop (sleep cadence, online
learning) *on top of* a cell we trust. So unlike Phase 2 (which trimmed P2.3/4 to save time), Phase 4 runs its
whole orthogonal scorecard: if a serious algorithm bug or a weird behaviour is hiding in the cell, breadth is what
catches it here, cheaply, before it's baked into the optimization phase. *(Caveat to the breadth: "small +
orthogonal" still governs axis **design** — each axis is one sharp question, never the every-task×every-dim
sprawl. Coverage means "don't drop an orthogonal axis," not "add redundant ones.")*

**What it is NOT — the scope guard (CLAUDE.md "keep the menu closed").** This is **not** a race on everything.
The brainstorm list (every task × every dim × every difficulty) is a combinatorial sprawl that would bury the
signal. Phase 4 is a **small, orthogonal scorecard** — each axis one *sharp* question ("where does the gap to
backprop open?"), one variable, the house-style figures. And it **excludes** axes that need *new architecture*:

- **Time series / recurrence** → the **north star** (recurrent prefrontal↔hippocampus loop). The cell is
  feedforward; there is nothing to evaluate until recurrence is built. **Deferred.**
- **Convolution / spatial image** → needs a conv front-end we haven't built. *Flat*-image (digits, CIFAR-flat) is
  in; *spatial* image is "build architecture first." **Deferred.**
- **Large-scale natural data as the claim** → out of behavioral-sim scope (CLAUDE.md). Small real probes are fine.

---

## 1. The framing + the baselines (from the literature)

**The canonical method** (Bartunov 2018; Spyra 2025): fix a **fair, hyperparameter-matched backprop baseline**,
then **dial a difficulty/scale axis and watch where the gap to backprop opens.** The metric is the **gap to
backprop** + the **accuracy/cost Pareto**; the caution is *measure real cost, not theoretical* (Spyra: backward
savings get offset by overhead — so we log *measured* backward work, not a formula).

**The three racers (every cell runs all three):**

| racer | what it is | role |
| --- | --- | --- |
| **OURS** | `[contrast + coordination w=2] bulk + sleep-consolidated readout` (the P3 cell) | the cheap forward-only brain under test |
| **BP-ceiling** | a same-budget, **genuinely tuned** backprop MLP — per regime: lr grid **+ weight-decay + 2–3 depth/width shapes at the matched budget**, best held-out, *chosen config recorded* (not strawmanned; the whole gap-to-BP headline rides on this being a real ceiling) | the ceiling; the gap to it is the headline |
| **Mono-Forward** | per-layer local-CE forward-only (the supervised-local alternative) | the "forward-only but supervised" reference — the author's fork: are we beaten by the *cheap supervised* option? |

Fairness rules (Bartunov/Spyra): **equal weight budget**, the BP baseline **genuinely tuned** (lr + weight-decay +
a few shapes — Spyra uses Optuna; we can't, so the search is wider than one lr grid and the chosen config is
logged, else we'd "beat a weak baseline"), **same task/seeds/eval**, and **measured cost**, not theoretical.

**Cost-honesty caveat (Spyra's, sharpened for a numpy sim).** Spyra's "measure real cost not theoretical" means
measured GPU energy/wall-clock — which a behavioral sim *cannot* produce, and which isn't even the substrate's
question. So our cost meter is the honest proxy for the *substrate* claim: **backward credit-assignment work**
(credit-distance × weights · # backward weight-updates), an analytic count. We therefore **never report "energy"
or "N× faster"** (the exact over-claim Spyra criticises) — only "N× less backward credit-assignment work on the
target substrate." That is what the 80/20 design is actually about.

---

## 2. The axes (the scorecard) — each a sharp "where does the gap open?" question

| # | axis | the dial | the sharp question | prior |
| --- | --- | --- | --- | --- |
| **A1** | **Difficulty** | **controlled Bayes error** (class overlap → known optimal acc). *Note: overlap dials the Bayes-error component of difficulty; the field decomposes difficulty into 3 — Bayes error + boundary complexity + sample size. Boundary complexity rides along via the random cluster→class map (entangled, not independently dialed); sample size = the sample-efficiency probe* | does the gap to BP widen as the task gets *harder*? quantify the slope. Spend seeds in the **informative band** (Bayes ≈ 0.02–0.35); skip the saturated trivial end | SCFF paper; Bartunov; difficulty-decomp (2106/2412) |
| **A2** | **Ambient-dim tolerance** | active structure fixed in a 2-D subspace, ambient dim 8 → 1000+ (so raising dim adds **nuisance** dims, not new signal) | does contrast filter irrelevant/nuisance dimensions as well as BP? (this is *nuisance tolerance at fixed intrinsic difficulty* — not "harder higher-D problem"; Phase-1: random ties SCFF in low-D) | Phase-1 exp0 |
| **A3** | **Depth headroom** | the P3.2 headroom-task family, dialed across A1/A2 | does the depth-composition (P3.2) *generalize*, or was it one config? *(budget for a PARTIAL — P3 showed headroom is fragile; a clean "no generalizable headroom" is still a result)* | P3.2 |
| **A4** | **Width × depth** (the Scap collision) | narrow-deep vs wide-shallow at fixed weight budget | the substrate-budget Pareto: which shape wins per regime? *(kept in P4 as a characterization cell — it's part of "check everything"; the eventual shape-**choice** is Phase 5's)* | P2.0 F6⁺ |
| **A5** | **Class count** | 2 → 4 → 10 → 20 classes | does it hold as the label space grows? | — |
| **A6** | **Continual** (home turf) | the exp4/P3.3 stream, across A1 + A5 | does the continual win hold *across* difficulty/class-count? **This is where the architecture *wins*** (see §3 note) | P3.3, exp4 |
| **A7** | **Noise robustness** (the substrate axis) | inject abstract Gaussian **weight** + **activation** noise (inference, then train-time), σ swept | does the cheap brain degrade *more gracefully* than BP under the noise the analog chip will actually have? (a known forward-only strength — Distance-Forward, analog-IMC corpus — and the axis that most directly tests the substrate thesis) | Distance-Forward; analog-IMC robustness |

**Why A7 is in, and not a rule-#7 violation.** This is *algorithm-level* noise tolerance (abstract Gaussian), **not**
PVT/SPICE device modeling — and rule #7's clock has struck anyway: `main.ideas` sanctions analog realism "once a
phase's ideal converges," and the ideal converged (Phases 1–3). A7 is where OURS is *expected to win* a static
axis, so it balances the difficulty/dim axes where it's expected to trail.

**Synthetic-first, real-confirm.** A1–A5 + A7 ride a **controlled synthetic Gaussian-cluster generator** (known
Bayes error, free dials) — the only way to *measure* difficulty/dim/headroom cleanly. Each **headline** axis
(difficulty, dim, continual, noise) gets a **real-data anchor point** overlaid on its GAP-CURVE — on the in-scope
flat tasks (digits 64-D, CIFAR-flat 3072-D) — so the synthetic story isn't a synthetic artifact. *(Real-data anchors
are overlaid systematically, not confined to one rung.)*

---

## 3. The metrics (PINNED) — what "characterize" means here

The probe-accuracy primary carries from Phase 1–3; Phase 4 adds the **gap** and **cost** family. Full catalog in
[`result-format.md`](result-format.md).

| metric | definition | what it answers |
| --- | --- | --- |
| **held-out accuracy** | OURS / BP-ceiling / Mono-Forward, matched budget | raw performance |
| **gap to backprop** (HEADLINE) | `acc(BP) − acc(OURS)` per cell | the characterization metric (Bartunov) — *where* the gap opens |
| **Bayes-normalized capture** | `(acc(OURS) − chance) / (acc(Bayes) − chance)` | how much of the *achievable* the cheap brain captures (Bayes error from the generator) |
| **cost Pareto** | accuracy vs **backward credit-assignment work** (credit-distance × weights · # backward weight-updates) — an analytic substrate count, **labelled as such, never "energy"** | the 80/20 substrate claim (Spyra's caution honoured by *scoping* the claim, not by faking a GPU measurement) |
| **noise-degradation slope** (A7) | Δacc per unit injected σ, OURS vs BP vs Mono-Forward | does OURS degrade more gracefully under analog-style noise? |
| **generalization gap** | train − held-out | does the cheap brain over/under-fit vs BP per regime? |
| **continual AA / BWT / FWT / forgetting + stability–plasticity** | GEM/CL-survey conventions | the continual profile (A6) |

**Where the win lives (read this before the gap-surface scares you).** Spyra found Mono-Forward *beats* tuned BP on
MLPs — so on the **static** axes (A1/A2/A3/A5) the honest expectation is OURS trails *both* BP and Mono-Forward,
because OURS is not built for static accuracy (Phases 1–3: SCFF is weak, the value is elsewhere). That is **not a
failure** — the static axes characterize *the cost of the gap*. The architecture's **win is the continual axis
(A6)** + graceful **noise degradation (A7)**, where the supervised racers (no sleep, no consolidation) should rot
and OURS should not. Don't let six static heatmaps bury the two axes that are the actual thesis.

**The deliverable is a *map*, not a verdict.** The output of Phase 4 is the **gap-to-backprop surface** (heatmap
over axis pairs) + the **cost Pareto** — a reference corpus that says "here the cheap brain is competitive, here
the gap opens, here's the cost" — exactly what Phase 5 selects optimizations from.

---

## 4. Tasks

| role | task | why |
| --- | --- | --- |
| **the dial (A1–A5)** | **controlled synthetic** Gaussian clusters with a known/estimated **Bayes error** + free {difficulty, dim, depth-headroom, class-count} knobs | the only way to *measure* difficulty/dim cleanly (synthetic-with-known-Bayes-error is the standard) |
| **real confirm** | **digits** (64-D), **CIFAR-flat** (3072-D) | small real probes — the synthetic story must survive real (flat) input |
| **continual (A6)** | class-incremental digits (exp4/P3.3 exact) | the home turf, where the win lives |
| **deferred** | time series, conv-image, large natural data | north-star / needs-architecture (§0) |

Seeds `[42,137,271,314,1729]` (3 for the heaviest continual cells), median + IQR. Single-threaded (phantom guard).

---

## 5. The experiment ladder (cheapest-decisive-first)

Each rung = one axis swept, all three racers, the gap + cost logged. Built as **one checkpointing driver**
(§7) so an overnight death is resumable.

- **P4.0 — the bench + the difficulty axis (A1).** ✅ **DONE (2026-06-22)** — bench validated; **A1: the gap does
  *not* open with difficulty (it closes — capture is the real difficulty read, 0.92→0.68); 80/20 cost not supported
  per-pass → P5 must meter the gate+sleep.** Full read: [`exp0/experiment-0.md`](exp0/experiment-0.md). *(plan:)*
  Stand up the synthetic generator with the **exact closed-form
  Bayes error** (computed from the true Gaussian-mixture posterior — *better* than the literature's estimators, which
  is why no huge-sample classifier proxy is needed); reproduce a clean gap that *opens* with difficulty, **over the
  informative band** (start the overlap dial high enough that Bayes ≈ 0.02–0.35; the trivial end where everyone hits
  ~100% wastes seeds). The locked first run — it validates the whole apparatus (generator, exact Bayes, the three
  racers with the **widened** BP tuning, the gap + cost meters).
- **P4.1 — ambient-dim tolerance (A2).** ✅ **DONE (2026-06-22)** — **OURS's first WIN.** As nuisance dim grows OURS
  holds while BP declines and **Mono-Forward collapses to chance**; OURS **crosses above tuned BP by dim 500**
  (cheaper *and* better) — contrast down-weights non-discriminative dims for free. Substrate-relevant (wide
  crossbars). Full read: [`exp1/experiment-1.md`](exp1/experiment-1.md).
- **P4.2 — depth headroom (A3) × difficulty.** ✅ **DONE (2026-06-22)** — **depth-composition GENERALIZES** (not the
  feared PARTIAL). OURS w=2 composes (probe slope >0) across the *whole* difficulty band; w=1 never does
  (coordination = the lever); GD loses headroom by overlap 1.0. OURS & BP compose in **complementary regimes** —
  **OURS out-composes BP in the hard/low-headroom regime** (crossover ≈0.6). Window-size = a P5 knob (w4 for
  easy+deep). Full read: [`exp2/experiment-2.md`](exp2/experiment-2.md).
- **P4.3 — width × depth (A4).** ✅ **DONE (2026-06-22)** — **Scap-collision resolved (via cost).** At iso-weight
  budget OURS's backward cost is **flat in depth** (w2-bounded credit) while BP's grows **linearly** — narrow-deep
  (substrate-native) is ~free for OURS, 2.6× costlier for BP. On headroom OURS **climbs with depth and overtakes BP
  from L3**; on flat depth doesn't pay. **Depth is OURS's to spend cheaply.** The 80/20 advantage is **depth-gated**
  (refines P4.0). Full read: [`exp3/experiment-3.md`](exp3/experiment-3.md).
- **P4.4 — class count (A5) + real anchors.** ✅ **DONE (2026-06-22)** — **competitive-but-trails (like A1);
  difficulty-gated, not count-gated.** Synthetic gap widens with C (+0.06→+0.23) and OURS's edge over Mono erodes
  (Mono ties by C20) — **but real digits (10-class) gap is only +0.027**, so the synthetic widening is harshness,
  not a many-class penalty. Not a win axis. Full read: [`exp4/experiment-4.md`](exp4/experiment-4.md).
- **P4.5 — continual (A6) across difficulty.** ✅ **DONE (2026-06-22)** — **THE win, robust across difficulty.**
  OURS+sleep forgets almost nothing (BWT −0.02 to −0.18) at every difficulty; online-BP catastrophically forgets
  (−0.83 to −0.99); no-sleep rots (sleep = the mechanism). Digits reproduces P3.3 (0.954/−0.017). The architecture's
  reason for being. Full read: [`exp5/experiment-5.md`](exp5/experiment-5.md).
- **P4.6 — noise robustness (A7).** ✅ **DONE (2026-06-22) — an HONEST NEGATIVE.** Under eval-time multiplicative
  weight noise, OURS is **not** more robust than tuned BP — it's the **least** (retention 0.75 vs 0.88 at σ=0.4).
  Likely cause: per-sample layernorm (the A2 win mechanism) doesn't damp weight-direction noise → **A2 win & A7 loss
  share a cause.** Scope: eval-time ≠ the substrate's train-with-noise regime (the proper P5 test). Don't claim
  noise-robustness yet. Full read: [`exp6/experiment-6.md`](exp6/experiment-6.md).
- **P4.7 — the synthesis: the capability map.** ✅ **DONE (2026-06-22)** — [`phase4-summarize.md`](phase4-summarize.md)
  + [`figs_summary/CAPABILITY_MAP.png`](figs_summary/CAPABILITY_MAP.png) + the Phase-5 brief. **Phase 4 CLOSED.**

*(Order is cheapest-information-first. **Phase 4 runs for coverage, not triage** — rungs are **not** trimmed to save
time the way Phase 2 trimmed P2.3/4; this is the bug-catch gate, so the whole orthogonal set runs. The *only*
reason to drop a rung is if a finding makes it **moot** (the P2.3/4 sense — logically answered, not "we ran out of
evening"). Failures/weaknesses are the point: a clean "here the cheap brain loses to BP" is a result.)*

## 6. The success criterion

> A **capability map** — the gap-to-backprop surface over {difficulty, ambient-dim, depth, width, class-count,
> continual, **noise**} + the accuracy/cost Pareto, OURS vs a genuinely-tuned BP ceiling and the Mono-Forward
> reference — honest about where the cheap brain wins (continual, noise), ties, and loses (static accuracy).
> **Not** "we beat backprop"; a *map* that tells Phase 5 exactly what to fix, and a **clean bill of health** (or a
> caught bug) on the adopted cell before we build the maintenance loop on top of it.

## 7. What to build (the overnight-safe driver)

- **Controlled synthetic generator** — Gaussian clusters, dials {overlap→Bayes-error, ambient-dim, cluster-count/
  headroom, class-count}; **exact closed-form Bayes error** from the true mixture posterior (`bayes_error` in
  `p4lib` — already built; no classifier proxy needed). *(Tighten the default overlap range into the informative band.)*
- **The three racers behind one interface** — OURS (`SCFFContrastOLU` + sleep readout), BP-ceiling (**widen
  `race_bp`**: lr grid + weight-decay + 2–3 depth/width shapes at the matched budget, return the chosen config),
  Mono-Forward (built in `p4lib`).
- **A noise-injection wrapper** (A7) — add Gaussian σ to weights and/or activations at eval (and a train-time
  variant); reused across racers behind the same interface.
- **The cost meter** — backward credit-assignment work (credit-distance × weights · # backward weight-updates) per
  racer; reported as substrate cost, **not** energy.
- **One checkpointing driver** — runs every (axis, cell, seed), **appends each result to a checkpoint file the
  instant it finishes**, and *resumes* from the checkpoint on restart (so a laptop-sleep loses one cell, not the
  run — the P3.1 lesson). Single-threaded, `python -u`, flushed.
- **Plots** per `result-format.md` (gap surface, Pareto, the per-axis gap curves, the noise-degradation curve).

## 8. Open items / scope

**Resolved (review of 2026-06-22):**
- ✅ **Noise robustness (A7) added** as the substrate axis — see §2.
- ✅ **BP-baseline tuning widened** — lr + weight-decay + a few shapes, chosen config logged (not just a 3-lr grid).
- ✅ **Bayes error is exact** (closed-form mixture posterior) — no estimator proxy.
- ✅ **Ladder order kept** (cheapest-info-first) and **A4 kept** in Phase 4 — Phase 4 runs for coverage (bug-catch
  gate); only moot rungs are dropped.
- ✅ **Cost claim scoped** to backward credit-assignment work, never "energy."

**Still open:**
- **The phase renumber** (P4 = characterize, P5 = optimize) — endorsed by the author; **not yet synced** to
  `CLAUDE.md` / `context.md` / `main.ideas.v1.md` (they still read "Phase 4 = maintenance"). Sync after the plan settles.
- **Sample-efficiency axis** (acc vs #training samples) — a genuine field gap (SCFF/FF papers don't measure it) and
  core to a brain-like online learner; held as an **optional add** inside A5/A6's rungs, run if the evenings allow.
- **Mono-Forward in every cell** — kept as the third racer everywhere (cheap; it's the *strongest* forward-only
  supervised bar, per Spyra — racing it is more honest than racing BP alone).

## 9. References (the evaluation-methodology canon)

- **Assessing the Scalability of Biologically-Motivated Deep Learning** — Bartunov et al, NeurIPS 2018
  ([1807.04587](https://arxiv.org/abs/1807.04587)). *The* template: matched BP baseline, sweep difficulty
  (MNIST→CIFAR→ImageNet) + architecture, the gap opens where it scales. Our gap-to-backprop framing.
- **Energy-Efficient DL Without Backprop: A Rigorous Evaluation of Forward-Only Algorithms** — Spyra et al, 2025
  ([2511.01061](https://arxiv.org/abs/2511.01061)). Native-arch, Optuna-tuned BP, accuracy + **cost Pareto**,
  "measure real cost not theoretical." Our fairness rules + the cost meter. (Mono-Forward > tuned BP on MLP.)
- **Bio-plausible learning can scale to large datasets** — Xiao et al ([1811.03567](https://arxiv.org/abs/1811.03567))
  — sign-symmetry approaches BP on ImageNet; where the gap closes.
- **Bayes-error as task difficulty** — synthetic-with-known-Bayes-error is the standard difficulty control
  ([2106.03357](https://arxiv.org/abs/2106.03357); difficulty = Bayes error + boundary complexity + sample size).
- **Continual metrics** — AA / BWT / FWT / forgetting + stability-plasticity (CL survey
  [2302.00487](https://arxiv.org/abs/2302.00487); Lopez-Paz **GEM** [1706.08840](https://arxiv.org/abs/1706.08840)).
- **Noise robustness (A7)** — forward-only / local learning is more hardware-noise-robust than BP:
  **Distance-Forward** (on-chip learning, the project's own [`../ref/distance-forward.md`](../ref/distance-forward.md));
  analog-in-memory robustness ([2411.07023](https://arxiv.org/abs/2411.07023) — inherent robustness of analog IMC;
  [PMC11335942](https://pmc.ncbi.nlm.nih.gov/articles/PMC11335942/) — robust analog in-memory training). The standard
  analog-CIM eval injects abstract Gaussian weight/programming/read noise and reports the degradation curve.
- **Difficulty decomposition** — Bayes error + boundary complexity + sample size
  ([2106.03357](https://arxiv.org/abs/2106.03357) gap-to-Bayes; [2412.02596](https://arxiv.org/abs/2412.02596) RER difficulty-decomp).
- Carry-overs: **Mono-Forward** ([2501.09238](https://arxiv.org/abs/2501.09238)), the Phase-3 cell
  ([`../phase3/phase3-summarize.md`](../phase3/phase3-summarize.md)), `result-format` lineage (Phase 1–3).
