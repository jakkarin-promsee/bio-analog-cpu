# Multi-agent review + the leader's revisions (the recheck)

> **What this is.** On 2026-06-28 the author asked for a hard recheck of the depth-readout plan before committing to
> experiments. Four **Opus 4.8** subagents reviewed it through deliberately different lenses; this file is the
> **leader's synthesis and decisions** — what survives, what changes, what gets cut, and where I overrule a reviewer.
> **This file is now authoritative over the pre-review track files** on every point below; [`replan.md`](replan.md)
> has been rewritten to **v2** to match. The original tracks (A/B/C) keep their literature value but carry
> post-review correction banners.

---

## The four lenses (and the one-line each delivered)

1. **Cold outsider** (no project context, generic-ML problem): *independently re-derived the Tunnel Effect AND a
   second mechanism we under-weighted — greedy-locality info-collapse (InfoPro family) — and named the lever we
   missed: whitening/decorrelation, plus the controls we lacked (oracle-exit, probe-capacity).* **Convergence from a
   cold start = strong signal our diagnosis is right.**
2. **Outsider red-team**: *the plan is salvageable, but the Tunnel Effect is mis-stated on its load-bearing variable
   (capacity-relative, not task-absolute), the reframe partly rationalizes an unsolved science question, "80/20
   restored" likely fails in the continual regime, and the borrowed fixes assume training machinery the substrate
   bans.*
3. **Insider auditor** (full context): *diagnosis is correct and contradicts no prior phase; adjudicated the 4
   challenges (A partly / B partly / C VALID / D partly); two real consistency flags (Tunnel over-claim; ReZero-α
   signal) + one omission (whitening).* Crystallized the **meta-insight** below.
4. **Substrate checker**: *the ladder is over-built by two tiers; ReZero-α is not substrate-trainable as specified;
   and the plan misses its own cheapest native idea — but with a sharp scope caveat I correct below.*

---

## THE META-INSIGHT (the spine of every change)

The insider said it cleanest, and it is the project's own recurring lesson wearing a new coat:

> **Three of the sharpest findings — the Tunnel Effect's rank reading, the ReZero-α signal, and the whitening lever —
> all circle the SAME trap: mistaking a MAGNITUDE (rank, variance, contrast-loudness, goodness/energy) for the
> DIRECTION that actually carries class information. Preserve the class DIRECTION (the manifold), not the MAGNITUDE.**

This **is** density≠class / the-missing-sign, the project's recurring silent killer ([context.md PART 9](../../context.md)),
showing up a fourth time. Every revision below reduces to it. **The fix must preserve and read the class
*direction* — never a magnitude proxy.** Concretely this kills three tempting-but-wrong moves at once:
- reading **goodness/energy** to decide where to read (magnitude → density, not class),
- training **ReZero-α from the local contrast loss** (chases local-objective magnitude → opens the gate at the
  drift onset),
- adding **VICReg/Barlow variance-covariance** to fight "rank collapse" (restores rank — a magnitude we already
  proved is a *symptom*, not the lever).

---

## Convergent findings (multiple agents, high confidence) → decisions

### C1 — The native physical signal idea, correctly scoped *(my biggest correction of a reviewer)*
The substrate checker's strongest find: the chip emits **goodness/energy** and (in the recurrent design) **settling
time** for free — why *train* a PonderNet halting head to reconstruct a signal the substrate measures? **I adopt the
spirit and split the two jobs, but I correct the scope:**
- **WHERE-TO-READ (placement)** must come from **readout-head class-confidence** — NOT goodness/energy. Goodness is
  density (Phase 3 *demoted* `Σh²` for exactly this). Using it for placement re-incurs density≠class. *(Both the
  substrate checker and insider flagged this caveat; I'm making it a hard rule.)*
- **WHEN-TO-STOP / effort (the settling-time signal)** is genuinely free and class-agnostic — **but it is a
  RECURRENT/north-star-phase signal, not a Stage-1 one.** The current cell is *feedforward* SCFF+GD; there is no
  equilibrium relaxation to time ([context.md PART 6](../../context.md): settling = the analog-native
  *recurrence*, a north-star mechanism). The substrate checker over-reached by importing it into the feedforward
  Stage-1 cell. **Decision: park settling-time as the north-star halt signal (it's a beautiful fit there — it
  becomes the timing of "I get it"); for Stage 1, halt = a calibrated confidence threshold on the heads.** Adding a
  relaxation step now = pulling the north star forward, which we're explicitly avoiding.

### C2 — CUT PonderNet / learned halting from the committed path
Substrate checker + the author's own value ("thinking harder ≠ thinking better" = the SDN over-thinking framing) +
[`draft6.0/CLAUDE.md`](../../CLAUDE.md)'s "keep the north-star menu closed." A *learned* halting policy is
over-engineering for "where to read": a **fixed/calibrated confidence threshold** (CALM gives a guarantee) does the
job. **Decision: CUT learned-halting as a build item; use a calibrated threshold. Hold the halting *concept* as the
north-star seed (it's the "I-get-it feeling") — do not build it in Stage 1.** Building it now is pulling the dream
forward.

### C3 — ReZero-α has no valid training signal under the hard rule → frozen-α default
Red-team raised it, insider ruled **VALID** ("sharpest catch"), substrate checker confirmed "not-substrate-trainable
as specified." ReZero learns α by **backprop from the global loss through the whole stack** — forbidden here.
Training α from the **local contrast objective** opens the gate *exactly when the block starts drifting off-manifold*
(it rewards local-objective magnitude = the cause of decay). **Decisions:**
- **Default Track A to FROZEN / init-based near-identity preservation (Fixup-style)** — the structural win (start as
  identity, deep layers can only *add* a bounded correction) comes from the **initialization**, needs no α training
  signal. Sidesteps the hole entirely.
- **Learned-α only if driven by the GD-readout** (class-direction, licensed 20% side) — never local-contrast, never
  goodness. And then it's a GD knob, not "a free local scalar" (drop that framing).
- **Dead-gate guard (critical test-design catch):** a frozen-*tiny* α that does nothing *also* "stops the tail
  decaying" — so the success metric "tail stops decaying" can be passed by a dead gate. The test **must** show each
  block's contribution is *real* via **per-block α→0 ablation** (red-team 3.4): if ablating a block changes nothing,
  it's a bypass, not a contributor.

### C4 — Demote the Tunnel Effect from keystone → useful analogy
Red-team CRITICAL + insider PARTLY VALID. The facts: it's **capacity-relative** (over-parameterized regime), measured
on **supervised** nets, and a real tunnel is information-**preserving**-but-useless whereas ours is information-
**destroying** (it drops in-distribution accuracy — the mixed-task 0.67→0.51). **Decision: demote from
"keystone/theory" to "a useful loose analogy that names the *shape*" (extractor/tunnel, peak-tracks-complexity).**
Subordinate its rank-drop reading to the project's own "rank is a symptom, not the lever." The *prescriptions*
(preserve early features, read the extractor, protect continual) survive because the **sims** motivated them
independently — but stop citing the theory as if it predicts our numbers. **Note: the "information-destroying"
correction *strengthens* Track A** (you need preservation precisely because the tail *overwrites*, not just wastes).

### C5 — "80/20 restored" is unproven in the continual regime; the readout is being designed on the wrong distribution
Red-team's headline risk, and it's correct and serious. Early-exit's cost win is **largest on the i.i.d. easy stream
and smallest in the continual/novel regime we actually live in** (novel data → low confidence → run deep + pay head
overhead). And the profiler/gate would be **calibrated on stationary synthetic profiles but deployed under
distribution shift**, where the sweet spot *moves*. **Decisions:**
- T1's cost claim must be a **measured expected-compute model on the *continual* workload**, not i.i.d., with
  **all-tap as the explicit baseline** and a required **Pareto win**.
- Add a **continual / distribution-shift stress test to T1** (does placement+gate hold when the task distribution
  shifts?). This is moved *up* from T5. **If the gate must be re-found online per task, that cost goes into the
  80/20 math and may kill "minimum = T0+T1" — which we need to know early, not late.**

### C6 — The locality question is unsettled; add the decisive control
Red-team + insider: **two objectives (energy P2.2-oracle, contrast P4.3) both fail past ~5 layers** — the plan
treats ~5 as objective/task-set, but it could be **locality**-intrinsic. The insider named the clean control:
**end-to-end-backprop InfoNCE vs forward-only-local InfoNCE, same cell, per-layer probe to L12.**
- e2e *also* saturates ~5 → bound is objective/task-set → **Track A/B suffice, Track C optional** (the plan's bet).
- e2e composes past 5 → bound is **locality** → **Track C (global coordination) is MANDATORY**, A/B are palliative.
**Decision: add this as a T0 control. It re-orders the whole dependency graph (see C7) and is cheap (swap the
trainer).** Until it runs, we are *assuming* the answer the plan depends on.

### C7 — The dependency graph may be backwards: is the global signal a prerequisite, not an escape hatch?
Red-team 2.4 + the C3/C6 findings: ReZero-α needs a global/readout signal to train; halting needs one; and C6
decides whether global coordination is mandatory. **Decision: pull the question "what single bounded global signal
is allowed, and what consumes it?" to the FRONT (a T0/T1 design constraint), not a tier-4 experiment.** The
"one-scalar unification" (S6 gate = halt = plasticity-gate = broadcast) stays a **tagged hypothesis to test**, not a
design assumption.

### C8 — Whitening/decorrelation: on the menu, with the right verdict
Cold outsider's "most-missed lever"; insider PARTLY VALID with the decisive correction. VICReg/Barlow/W-MSE fight
**rank/dimensional collapse** — but (a) rank is a **symptom** we already discounted (`widen` adds rank, no accuracy),
(b) they have **no class-direction term**, and (c) their variance/covariance terms are **batch statistics**, and the
EMA/streaming form reintroduces a running statistic that *causes* continual rot in the class-incremental regime.
**Decision: add a Track-A appendix that puts whitening on the menu and REJECTS it as the lever** (fixes the symptom,
not the cause; conflicts with per-sample/continual) — and pivot to the right idea it points at: **a per-sample
*class-direction* preservation term** (hold the class-discriminative subspace fixed), which is closer to the
frozen-residual than to VICReg.

---

## Other adopted catches (single-agent, valid)

- **Harden T0.1** into a 2-D grid (lr-schedule × total-passes) + a contrast-strength/negatives-at-depth control,
  with a **pre-registered decision rule** and **no pre-committed prior** (the red-team and substrate checker
  *disagree* on whether the peak will move with budget — that disagreement is exactly why it must be properly
  powered). *(red-team 1.2; resolves the C4 capacity-regime uncertainty too.)*
- **Probe-capacity control** (linear vs small-MLP per depth): is the decayed info *destroyed* or just *rotated*? If
  an MLP recovers it, the diagnosis shifts toward "entangled, not lost" → placement/whitening over objective
  surgery. *(cold outsider control #4.)*
- **Validate the profiler against the actual (nonlinear, multi-layer) readout** — a linear-probe peak need not be
  the readout's optimum; the profiler is a proxy with a known gap. *(red-team 3.2.)*
- **Oracle-exit upper bound**: best-possible per-input layer selection. If the oracle gain is small, gating can't
  save us and the problem is in the representation. *(cold outsider control #3.)*
- **Split T1** into T1.1 (heads vs all-tap, accuracy) and T1.2 (add exit, cost) — one variable each (methodological
  rule 1). *(red-team 3.3.)*
- **Natural-data spot-check moved into T0** — the decay diagnosis itself is all-synthetic and may be partly a
  synthetic-task artifact (no real class manifold to preserve). *(red-team 4.3.)*
- **S5 (mandatory inter-layer norm) × residual interaction** = a first-class T2 risk (length-norm after a
  near-identity skip can rescale the preserved `x` and defeat it). *(insider.)*
- **Label S9 as revising S3's "tap all"** so a future reader doesn't see a Phase-1↔Phase-5 contradiction. *(insider.)*
- **Self-distillation / "Be Your Own Teacher"** (deep layer regularized toward an earlier confident exit's logits) —
  a forward-compatible way to stop deep layers corrupting solved structure; add to Track B. *(cold outsider.)*
- **InfoPro / greedy-locality literature** ("Revisiting Locally Supervised Learning" ICLR'21; InfoPro IJCV'24; "Go
  Beyond End-to-End: Context Supply" 2023) — the science-side companion to the tunnel effect; add to Track A/C.
  *(cold outsider.)*
- **Quarantine the novelty claim** (Track B6 "a genuinely new object") — chasing a contribution is scope-creep;
  the bar is "reads cheaply and correctly," not "is it new." *(red-team 3.5.)*
- **Citation hygiene**: verify arXiv IDs before any becomes a *decision* citation — esp. FTP `2506.11030`, CLAPP++
  `2601.21683`, AdaPonderLM `2603.01914` (post-cutoff; some came from web results, some from the repo dossier).
  *(red-team 4.1.)*

---

## Where I OVERRULE / temper the reviewers (leader's calls)

- **The reframe is NOT a rationalization (vs red-team 2.1).** The insider is right: the plan already *brackets* the
  science honestly (Stopping Mark ②: "preservation makes depth safe-to-read, not unbounded-to-use"). "Read smart
  while researching the cure in parallel" is a legitimate engineering posture for a chip project. **I keep the
  reframe — but make it honest by adding the C6 locality control** so we *know* whether ~5 is objective- or
  locality-bound rather than assuming it.
- **The native settling-signal is a north-star tool, not a Stage-1 one (vs substrate checker §3).** Correct that
  goodness is class-contaminated for placement; correct that settling-time is free — but it requires recurrence the
  Stage-1 feedforward cell doesn't have. **Park it for the recurrent phase** (where it's the elegant "I get it"
  timing). Don't let it justify adding relaxation now.
- **Keep deep-supervision heads as the load-bearing base (all four agree).** This is the one borrowed mechanism with
  a real forward-only precedent (Mono-Forward). It survives every lens.

---

## KEEP / CHANGE / CUT (the decision ledger)

| Item | Verdict | Why |
| --- | --- | --- |
| Diagnosis (trigger × multiplier; abstraction-*saturated*) | **KEEP** | Survives all evidence; no prior-phase contradiction (insider). |
| Reframe (where-to-read) | **KEEP + harden** | Legit engineering posture; add the C6 locality control to stop it assuming. |
| Deep-supervision heads (per-depth, Mono-Forward-style) | **KEEP — the base** | Cheap, proven forward-only, pure `read`, all four agree. |
| Confidence early-exit | **KEEP — but calibrated threshold, on head-confidence (class), continual-cost-tested** | C1, C2, C5. |
| Native goodness/energy as *placement* signal | **CUT** | density≠class (C1). |
| Native settling-time as *halt* signal | **PARK → north-star phase** | needs recurrence Stage-1 lacks (C1). |
| Learned halting (PonderNet) | **CUT from committed path; hold concept for north star** | over-engineering; pulls north star forward (C2). |
| ReZero residual (Track A) | **CHANGE → frozen/init-based α default; learned-α only via GD-readout; +dead-gate per-block ablation** | C3. |
| Preservation target | **CHANGE → preserve class DIRECTION, not rank/variance** | meta-insight; C8. |
| Whitening (VICReg/Barlow) | **CUT as the lever; keep on menu with rejection rationale** | symptom not cause; batch-stat/continual conflict (C8). |
| Tunnel Effect as keystone | **DEMOTE → loose analogy; subordinate rank reading** | C4. |
| Top-down / DFA / FTP (global direction) | **KEEP PARKED — mandatory *iff* C6 says locality-bound; else optional** | C6, C7; reviewers agree T4 is correctly conditional. |
| MoE / SSM / layer-skip | **KEEP PARKED (broader lazy-brain track)** | not the depth fix. |
| "minimum = T0+T1" | **KEEP as the target, but T1 must pass the continual-cost + distribution-shift bar to earn it** | C5. |
| Novelty framing | **QUARANTINE** | scope-creep (red-team 3.5). |

---

## The revised ladder (v2) — summary (full version in [`replan.md`](replan.md))

- **T0 — settle the ground (cheap, now, ~4 controls):** (a) **hardened** depth-scaled-training *grid* (lr×passes +
  contrast strength), no pre-committed prior; (b) **the locality control** (e2e-backprop-InfoNCE vs
  forward-only-local) — decides if Track C is mandatory; (c) **probe-capacity** (linear vs MLP — destroyed or
  rotated?); (d) **the profiler** (validated vs the real readout, + a **natural-data spot-check**) and the
  **truncation baseline** ("don't build the tunnel; read top of a profiled-depth stack") as the control everything
  must beat.
- **T1 — the readout redesign (the MVP), split + continual-validated:** T1.1 per-depth heads **vs all-tap** (accuracy);
  T1.2 add **calibrated** confidence early-exit (class-confidence, not goodness), measured on the **continual**
  workload with a **distribution-shift stress test** and an **oracle-exit** upper bound. **Where-to-read = head
  confidence.** Decide the global-signal envelope here (C7).
- **T2 — preservation (conditional on T0):** **frozen/init-based** near-identity residual (Fixup-style); learned-α
  only via GD-readout; **per-block ablation** guard; preserve **class direction**; test the **S5-norm × residual**
  interaction. Buys "read-top convenience," not "unbounded depth" — a cheap test, not a tier of commitment.
- **T3 — global coordination: MANDATORY iff the C6 control says ~5 is locality-bound; otherwise optional.** Order:
  top-down broadcast → DFA/FTP. (This replaces the old "learned halting" T3 — halting is cut/parked.)
- **T4 = the old Phase-5 continual optimization** (now informed by the readout + the C5 distribution-shift findings).
  **T5 = north star** (where the parked settling-time signal + the halting *concept* finally live).
- **The static-truncation floor** ("ship fewer Scaps") is the baseline every tier must beat — on a chip, fewer
  layers = cheaper silicon, so if T1 doesn't beat truncation+top-read on the *continual* workload, **ship the
  truncation.**

## The honest "how much do we have to do" (revised)

Even simpler than v1, and more decisive: **T0 is the gate, and it can shrink the problem.** If the hardened T0.1
shows the peak moves a lot with training budget, or the probe-capacity control shows the info is merely *rotated*,
much of the "fix" may dissolve. **The likely minimum is T0 + T1** (profiler + per-depth heads + calibrated exit,
proven on the continual workload). PonderNet, whitening, and global coordination are **out of the committed path**
unless a specific T0 control (C6 locality) forces C back in. The dream (north star) is where the cut ideas
(learned halting, settling-time) come home — deliberately later.
