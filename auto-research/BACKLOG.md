# BACKLOG — the topic queue (state lives here)

> **This file is the resume point.** State per topic: `pending` (not started) · `active` (subagent running — if the
> loop died, this is where it died) · `done` (files on disk + digest logged below). The orchestrator edits this file
> after every subagent. To resume: work the first non-`done` topic, top to bottom.

**Legend:** `[ ]` pending · `[~]` active · `[x]` done
**Run cadence:** one subagent per topic, sequential. Tier 1 → 2 → 3 → 4, Tier 5 as spillover.

---

## Tier 1 — Nearest neighbors (prior art we'd cite)

- [x] **t1.1 — Forward-only / backprop-free deep learning, the family** — Forward-Forward, PEPITA, SCFF lineage, mono-forward, cascaded/predictive forward. The closest *whole-system* cousins to our SCFF bulk. How is our sum-form mono-forward + frozen-bulk different? → **DONE (9 cards).**
- [x] **t1.2 — Analytic / closed-form continual learning** — ACIL, GKEAL, DS-AL, RanPAC-CL and the "align + closed-form recursive least squares" family. Direct cousins to our SLDA/RanPAC namer. Who else does no-gradient continual naming, and how? → **DONE (9 cards).**
- [x] **t1.3 — On-chip / on-device online learning systems** — local + continual learning that targets edge/hardware (not just an algorithm on a GPU). The systems closest to "learns online, on the substrate." → **DONE (10 cards).**
- [x] **t1.4 — Complementary Learning Systems, built** — fast-memory + slow-cortex + sleep/replay *implementations* (not just the theory). Our sleep + LUT has cousins; who and how different? → **DONE (6 cards).**
- [x] **t1.5 — Frozen-backbone + cheap-head continual learning** — the "pretrain/freeze a representation, adapt only a light head" paradigm (incl. prompt/adapter CL). Our exact 80/20 split has a large literature; map it. → **DONE (11 cards).**
- [x] **t1.6 — Feedback Alignment / DFA / target propagation** *(lead from t1.1)* — the other backprop-free credit-assignment family (fixed random feedback, direct feedback alignment, target prop). A different way to drop backprop than forward-only; where does it beat/lose to the FF family, and to us? → **DONE (8 cards).**
- [x] **t1.7 — Self-supervised / label-free pretrained backbones for CL** *(lead from t1.5)* — the closest analog to our *self-grown* bulk: does a frozen backbone trained WITHOUT internet-scale supervision hold up as a CL representation? Directly tests whether our core bet (a forward-only unsupervised bulk is a good frozen representation) survives outside the toy arenas. → **DONE (10 cards). CORE BET SUPPORTED.**

## Tier 2 — Component optimization (in-scope, P1–11)

- [x] **t2.1 — Better negatives & goodness objectives for FF/SCFF** — negative generation, goodness beyond `Σh²`, InfoNCE variants; collapse prevention (VICReg/Barlow); negative-free/goodness-free (CaFo); MinRed anti-collapse eviction. → **DONE (9 cards).**
- [x] **t2.2 — Closed-form classifier improvements** → **DONE (9 cards).** — FeCAM, NCM refinements, anisotropy/covariance fixes, ridgeless/streaming LDA advances, random-feature (RanPAC) variants. What beats plain SLDA on our anisotropy failure mode? *(from t1.2)* **DS-AL dual-stream** residual compensation · **LoRanPAC** Gram-conditioning + truncated-SVD solve (= analog dynamic range) · **Deep-SRDA** tied↔per-class shrinkage knob. *(from t2.1)* neural-collapse / **ETF fixed-simplex** classifier geometry (fixed equiangular targets — a no-fit anisotropy escape).
- [x] **t2.3 — Replay & sleep-consolidation beyond CBRS** → **DONE (8 cards).** — coreset/herding/gradient-based selection, latent/generative replay, sleep-phase algorithms. Cheaper or safer consolidation than our grid-4 closed-form re-fit? *(from t1.3)* GRASP sleep-sampling policy · stability-gap (Harun & Kanan) as a worst-point-BWT lens · SIESTA wake/sleep budget. *(from t1.5)* task-count scaling of fixed-capacity prototype memory (= our LUT cap / P11 C=20 crossover).
- [x] **t2.4 — Concept-drift detection beyond DDM** → **DONE (10 cards).** — ADWIN, KSWIN, EDDM, HDDM, direction/representation-based drift. A better awake-gate trigger than error-EMA DDM (recall the parked tap-drift direction gate). *(from t2.3)* adaptive sleep cadence conditioned on the gate (ties P10 §10 mid-domain-sleep rescue); reuse ONE error signal for both gate + eviction.
- [x] **t2.5 — Noise-robust representation learning** → **DONE (11 cards).** — the read-side directional/transducer residual named in P6/P10; noise-as-augmentation, flatness/SAM, robustness of frozen features under input drift. *(from t1.4)* label-noise-robust CL (ESMER error-sensitivity modulation).
- [x] **t2.6 — Prototype / covariance drift compensation** → **DONE (5 cards).** *(lead from t1.2)* — SDC → LDC → ADC and AdaGauss: keep stored class prototypes/covariances valid as the frozen-but-drifting representation moves. Directly bears on our sleep re-fit + the P6/P10 drift residual — does closed-form drift compensation beat a periodic full re-fit? *(from t1.7)* optimal-probe / CKA as the drift *measurement* instrument.
- [x] **t2.7 — EMA-of-closed-form-statistics: a slow "stable namer"** → **DONE (10 cards).** *(lead from t1.4)* — CLS-ER/ESMER's core trick (a slow weight-EMA stable memory) rebuilt for a *closed-form* head: EMA the namer's running statistics (SLDA mean+cov / RanPAC Gram), `Σ_stable ← α·Σ_stable + (1−α)·Σ_fast`. Zero gradient, an anti-recency stability anchor aimed at the worst-point-BWT / recency tension our grid-4 cadence fights. + ESMER error-graded consolidation to soften the binary gate.

## Tier 3 — North star / horizon (root README destination)

- [x] **t3.1 — The hippocampus organ (NEXT BUILD)** → **DONE (7 cards).** — associative/retrieval memory grown from the LUT: modern Hopfield, kNN-LM/RETRO, NTM/DNC, fast weights, product-key memory. The concrete buildable menu for the next step. *(from t1.4)* generative / feature replay as a hippocampus mechanism (Shin 2017 DGR, van de Ven 2020 Brain-Inspired Replay, Joint Diffusion 2024) — a store that "dreams" old data vs our literal LUT.
- [x] **t3.2 — Recurrent "think until it settles" compute** → **DONE (9 cards).** — deep equilibrium models, PonderNet/ACT, latent reasoning / test-time compute, energy-based recurrence. Analog-native fixed-point thinking.
- [x] **t3.3 — "Correctness is a feeling" — self-generated learning signal** → **DONE (10 cards).** — active inference / free energy, curiosity/compression-progress, learned critics, self-verification.
- [x] **t3.4 — The controller / prefrontal workspace** → **DONE (8 cards).** — Global Workspace, Shared Global Workspace, RIMs, gating — how the parts talk on limited bandwidth.

## Tier 4 — Adjacent wildcards (out of scope, high leverage)

- [x] **t4.1 — Analog in-memory / crossbar compute for learning** → **DONE (10 cards).** — RRAM/PCM/memristor crossbars doing on-array MVM + on-array update; the hardware reality under our "math model of a chip." *(from t1.3)* quantized latent-replay precision (Ravaglia/VEGA) → our Scap / LUT bit-width. *(from t3.1)* analog CAM (Li 2020) + memristor Hopfield / energy-based in-memory recall — the fabric the hippocampus-LUT read becomes.
- [x] **t4.2 — Equilibrium propagation & physics-based learning** → **DONE (6 cards).** — the analog-native way to get a gradient from local physics; EqProp, energy-based, Hopfield-network learning. *(from t1.6)* analog/optical **DFA built on hardware** (Filipovich silicon-photonic <1 pJ/MAC, PNAS-2025 optical DFA, Nakajima) — a *demonstrated* backprop-free analog training path to contrast with our designed-not-built forward-only. *(from t3.2)* Ising EqProp (Laydevant 2024), oscillator Ising machines, Kendall analog-EqProp-in-SPICE — physical annealers that compute AND learn via local correlation diffs (= our settling loop's learning rule).
- [x] **t4.3 — Neuromorphic / spiking online learning** → **DONE (8 cards).**  *(subagents now on Opus — Fable 5 quota reached)* — e-prop, surrogate gradients, three-factor local rules; the eligibility-trace = leaky-cap correspondence.
- [x] **t4.4 — State-space models & liquid/continuous-time atoms** → **DONE (8 cards).** — Mamba/S4, Liquid Time-Constant Networks, Neural ODEs — candidate recurrent *atoms* for the north-star loop.
- [x] **t4.5 — Matched-accuracy energy benchmarking for forward-only vs backprop** → **DONE (8 cards).** *(lead from t1.1)* — the honest protocol to measure training energy (Spyra & Dzwinel 2025 shows forward-only ≠ energy-efficient). Directly defends our P10 R1 (the 80/20 alone costs *more*; the win is the analog substrate). Methodology topic, not an organ.

## Tier 5 — Open exploration (free reading, no forced comparison)

- [x] **t5.1 — Energy-based learning as the unifying frame** → **DONE (10 cards).** — the capstone view: inference = roll downhill, learning = carve valleys; Landauer / thermodynamic computing floor.
- [x] **t5.2 — Learning-is-compression / MDL / superposition** → **DONE (9 cards).** — why a model fits on-chip; double descent, lottery ticket, superposition.
- [ ] *(more topics land here from subagent follow-on leads)*

---

## Done log (append one block per finished topic)

<!-- Format:
### [x] tX.Y — <topic>  (subagent: <id/date>)
- **Papers written:** N cards → `tierN-.../<topic>/`
- **Headline for us:** <one line — the single biggest finding vs our project>
- **Leads enqueued:** <new topic ids added above>
-->

### [x] t1.1 — Forward-only / backprop-free family  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/forward-only-family/`
- **Headline for us:** We optimize a *direction* (InfoNCE); the entire FF goodness camp optimizes a *magnitude* (`Σh²`) and merely *repairs* it (SymBa/ASGE) — and no family member has our frozen-bulk + separate closed-form namer split (CaFo's per-block predictors are the nearest cousin, but supervised). Energy win must be pinned to the **analog substrate**, not forward-only-ness (Spyra & Dzwinel 2025).
- **Leads enqueued:** t1.6 (Feedback Alignment/DFA), t4.5 (matched-accuracy energy protocol); enriched t2.1 (negative-free/goodness-free). FF-on-spiking folded into existing t4.3.

### [x] t1.2 — Analytic / closed-form continual learning  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/analytic-continual-learning/` (all fetched, 0 unverified)
- **Headline for us:** Our namer's skeleton sits squarely inside the analytic-CL family (F-OAL matches our operating point item-for-item). What's genuinely ours: survival on a *drifting* substrate (sleep re-fit over a bounded LUT) + the **drift-gate economy** (nobody else decides *when NOT to update*) + substrate energy costing. Two warnings: GACL weight-invariance ⇒ scope our head-level order-invariance claim to *whole-system-under-drift*; LoRanPAC ⇒ our `(G+λI)⁻¹M` solve may ride an unmeasured ill-conditioned spectrum (= analog dynamic range).
- **Leads enqueued:** t2.6 (prototype/covariance drift compensation); enriched t2.2 (DS-AL dual-stream, LoRanPAC TSVD, Deep-SRDA shrinkage). Recorded-in-cards only: Analytic Subspace Routing (LLM CL), ORFit (GD↔RLS bridge), LibContinual benchmark.

### [x] t1.3 — On-device / budgeted online continual learning  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/on-device-online-learning/` (0 unverified)
- **Headline for us:** SIESTA is our nearest twin — wake/sleep + gradient-free wake *already exists on GPU*, so the energy claim must be pinned to the **analog meter, never the loop shape**. Genuinely ours: an **always-plastic representation** (everyone else freezes the backbone) + the P8.6 "firing more forgets more" safety inversion. Prabhu/Ghunaim already published our P10 caveat (tuned small replay = the budget frontier). **Unbanked experiment idea:** run the frozen object under Ghunaim's *real-time / stream-doesn't-wait* protocol — we price energy but never TIME; at fire-fraction ≈0.003 we're plausibly near delay-free while per-step ER drowns.
- **Leads enqueued:** enriched t2.3 (GRASP, stability-gap, SIESTA), t4.1 (Scap/LUT bit-width). Cards-only: RECL, Chameleon/DaCapo, CLEAR benchmark.

### [x] t1.4 — Complementary Learning Systems, built (dual-memory)  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 6 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/complementary-dual-memory/` (1 caution: FSC-Net single-author preprint)
- **Headline for us:** DualNet is literally our 80/20 (unsupervised slow bulk + supervised fast head) in mainstream ML — and its "SSL-slow beats supervised-slow" result *supports* keeping the cortex label-free. But every method here trains BOTH memories by SGD and consolidates via weight-EMA / distillation / generative replay; ours is the triple road-not-taken: frozen unsupervised forward-only cortex ⊕ LUT-as-service (never classifies) ⊕ closed-form consolidation. No paper combines these.
- **Leads enqueued:** t2.7 (EMA-of-closed-form-statistics = a slow "stable namer", zero gradient — the standout lever); enriched t3.1 (generative/feature replay for the hippocampus organ), t2.5 (label-noise-robust CL / ESMER). Cards-only: capacity-recycling CL (PackNet/SupSup/NISPA), conditional on LUT allocation.

### [x] t1.5 — Frozen-backbone + cheap-head CL (PTM/prompt/adapter)  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 11 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/frozen-backbone-cheap-head/` (0 unverified)
- **Headline for us (STRATEGIC — sharpest challenge yet):** a prototype-head-on-frozen-features is now **COMMODITY** (Janson NCM, SimpleCIL, FSA) — our namer is validated but *not novel*; **our value must live in the BULK + SUBSTRATE, not the head.** Tang 2023: prompt-CL *collapses without a strong pretrain matched to the stream* — a crutch our stream-grown, unsupervised, forward-only bulk definitionally lacks (P11 gas = existence proof it doesn't need one). FSA is our nearest published twin and bets *against* our always-plastic bulk.
- **Experiment idea (high value):** the **FSA control** — halt SCFF after a formation window (hard-freeze bulk) vs committed always-plastic, on stationary home + P11 drift arenas. Ties-everywhere ⇒ always-on SCFF update circuitry is dead weight; drift-only-loss ⇒ cleanly scopes what continuous self-grown plasticity buys.
- **Leads enqueued:** t1.7 (SSL / label-free backbones for CL — the closest analog to our self-grown bulk); enriched t2.3 (task-count scaling of fixed-capacity prototype memory). Cards-only: GPM/orthogonal-write, InfLoRA subspaces, "Reflecting on Rehearsal-free CL with PTMs", LAMDA-PILOT harness.

### [x] t1.6 — Feedback Alignment / DFA / target propagation  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/feedback-alignment-dfa/` (2 fetch caveats: Nøkland 2016 search-confirmed; PNAS-2025 / reservoir-DFA paywalled leads only)
- **Headline for us (VALIDATING):** Bartunov + Refinetti = a **"locality-tax law"** — dropping the exact gradient costs you on hard/structured tasks and the gap GROWS — published, backprop-adjacent confirmation that our P4/P10/P11 "wins continual/noise, trails static-accuracy" shape is a **family property, not an SCFF defect.** Our flat-vector substrate sits on the *good* side of Refinetti's conditioning line (weight-sharing pathology that kills DFA on conv can't touch us) — a statable advantage. Honest counter: Filipovich BUILT DFA on an analog crossbar at <1 pJ/MAC (more demonstrated; we are more local).
- **Experiment idea:** DRTP-style random-projection supervised head vs our closed-form SLDA/RanPAC namer — a cheap bake-off (random projection may help the 20% namer, never the bulk).
- **Leads enqueued:** enriched t4.2 (analog/optical DFA built on hardware). Cards-only: sign-symmetry scaling (Xiao 2018), target-prop≈Gauss-Newton (Meulemans 2020), conditioning diagnostic on our bulk.

### [x] t1.7 — SSL / label-free frozen backbones for CL  (subagent: Fable 5 + finisher pass, 2026-07-10) — **CLOSES TIER 1**
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier1-nearest-neighbors/ssl-backbones-for-cl/` (0 unverified)
- **Headline for us (VALIDATING — most-supported claim in the sweep):** our **core bet is broadly SUPPORTED** — a label-free, self-grown frozen representation IS a good CL substrate. Gallardo 2021 ≈ our exact machine (label-free backbone + closed-form streaming LDA), SSL wins *biggest at small data* = our regime; LUMP/Cossu/Ostapenko converge (label-free reps forget less + transfer OOD; our stream is always OOD); Davari names the bulk/namer split as the field's own diagnosis. **Two caveats:** (1) *attribution* — Marczak 2024: the win may be the contrastive-OBJECTIVE architecture (InfoNCE-as-projector), NOT label-freeness; (2) Purushwalkam/CaSSLe/POCON: stream-grown SSL floors on autocorrelated streams = our **P11 floor, INTRINSIC to stream-grown SSL, not a substrate bug.**
- **Experiment idea:** Marczak attribution control — supervised-contrast SCFF (labels pick InfoNCE positives, still local+forward-only) vs label-free cell, else locked. Ties ⇒ robustness credits objective *structure*, not label-absence.
- **Leads enqueued:** enriched t2.1 (MinRed max-spread negative eviction), t2.6 (optimal-probe/CKA drift measure). Cards-only: SupCon local rules, projector/feature-buffer, structured/egocentric stream benchmarks, LLM-scale continual pretraining.

---
**TIER 1 COMPLETE** — 7 topics, ~63 cards. Rollup: `tier1-nearest-neighbors/_TIER1-SYNTHESIS.md`. Next: Tier 2 (component optimization).

### [x] t2.1 — SCFF negatives & goodness objectives  (subagent: Fable 5, 2026-07-10) — opens Tier 2
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier2-component-optimization/scff-negatives-and-goodness/` (0 unverified)
- **Headline for us:** three independent papers (Distance-Forward, Hyperspherical-FF, Robinson hard-negatives) triangulate on the same untested cell — **our uniform random-partner LUT draw is the most NAIVE negative policy in the literature, and our LUT already stores the prototypes that would fix it.** Layer-wise VICReg = existence proof a local/label-free/forward-only bulk can run with ZERO negatives (untested under our continual gates). "In Search of Goodness 2025" benchmarks 21 goodness fns: Σh² dominated, **margin-shaping the reliable win**. Temperature-free InfoNCE reframes our P5 temp-0.2 as gradient geometry + deletes a precision-held analog bias.
- **Biggest untried lever:** LUT-prototype negatives + Robinson hardness tilt (negatives = k-nearest resident prototypes, similarity-weighted denominators) — substrate-fit excellent (LUT exists, similarity already computed, tilt = one multiply, no new rails). Rung-2 prize: VICReg-lite negative-free (variance+invariance accumulator-cheap; covariance term = open substrate cost).
- **Leads enqueued:** enriched t2.2 (neural-collapse / ETF fixed-simplex classifier). Cards-only: debiased contrastive (Chuang 2020), MoCHi negative-mixing, Barlow/CorInfoMax decorrelation as a crossbar Gram op, temp schedules (Kukleva 2023), ED/participation-ratio collapse invariant.

### [x] t2.2 — Closed-form classifier improvements (anisotropy)  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier2-component-optimization/closed-form-classifier/` (0 unverified; Friedman 1989 paywalled → verified via secondary)
- **Headline for us:** **SLDA is exactly RDA-at-λ=1, and our P7.4 FeCAM strike is RDA's predicted λ=0 failure** — the fix is the *dial* between tied and per-class, not abandoning per-class info. KLDA is the one combination the P7 grid missed (RanPAC-projection → SLDA-statistics: the tied ceiling dissolves in the lifted space at zero per-class storage growth). Shrinkage theory warns our ceiling may be partly *estimation error*, not model bias — testable for free.
- **Biggest untried lever:** **diagonal-RDA head with count-aware blend** — Σ̂_c = (1−λ_c)·diag(σ²_c) + λ_c·Σ_tied, λ_c from cbrs counters. Substrate cost **+d per class** (one capacitor row beside each mean, no new crossbar); burst-starved classes auto-collapse to today's SLDA (= the A6 guard). Cheapest true tied-bias breaker. (Our composition, not a published result.)
- **Leads:** cards-only — nonlinear/eigenvalue shrinkage, RFF lift-width pricing for KLDA, Procrustes ETF re-anchor at sleep, Tyler robust scatter (→ P11 autocorrelated floor).

### [x] t2.3 — Replay selection & sleep-consolidation beyond CBRS  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier2-component-optimization/replay-sleep-consolidation/` (0 unverified)
- **Headline for us:** **InfoRS's closed-form "surprise" eviction score is the exact shape of our SLDA/RanPAC namer — and ≈ the error-EMA our drift gate already computes and THROWS AWAY.** Harun "Overcoming the Stability Gap": two of its four fixes are things our closed-form prototype namer already *is* → grid-4 may be conservative and *relaxable*. GSS/OCS/GCR converge: uniform-within-class retention is information-blind, wastes capacity at tight caps = our P11 C=20 crossover.
- **Biggest untried lever:** **information-weighted eviction reusing the drift-gate error signal** — within each CBRS class slot, keep informative / evict redundant, scored closed-form from the namer's own precision (Mahalanobis/leverage = the error-EMA already computed for the gate). Substrate-fit maximal. Directly attacks the C=20 crossover. (Camp-A gradient coresets GSS/OCS/GCR violate no-gradient-replay → diagnostic ceiling only.)
- **Leads enqueued:** enriched t2.4 (adaptive cadence conditioned on the gate; reuse one error signal for gate + eviction). Cards-only: closed-form predictive-variance eviction, Rainbow Memory, MIR, feature-space k-center coreset (Sener 2018, gradient-free substrate-runnable), DRO memory evolution.

### [x] t2.4 — Concept-drift detection beyond DDM (the gate)  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier2-component-optimization/drift-detection-gate/` (0 unverified; D3 via GitHub after ACM 403)
- **Headline for us:** **"DDM consumes an error rate" is NOT a real shipping blocker for the validated tap-drift trigger** — ADWIN/Page-Hinkley/KSWIN all eat continuous statistics, and Page-Hinkley is a leaky integrator + comparator (analog-native). So the P8 reason for parking the direction gate is re-openable (future exp). Hinder et al.'s impossibility result (harmful vs harmless drift indistinguishable from P(X) alone) is the sharpest objection to *feature-drift* gates — our class-direction projection is a genuine third escape but owes a broader nuisance battery. Cara/Regol: detection-triggered firing is systematically beaten by **cost-integrated / forecast** retrain policies — a cheap-to-test challenge to the committed gate.
- **Biggest untried lever:** the **self-disagreement trigger** (STUDD-shaped) — freeze the last sleep's namer weights (one C×d crossbar-resident matrix); live-vs-snapshot argmax disagreement is a label-free Bernoulli stream feeding the UNMODIFIED committed DDM. Removes label dependency with zero detector change; substrate cost = one crossbar read + one comparator.
- **Leads:** cards-only — Page-Hinkley as an analog primitive, drift-localization → class-conditional partial sleep, **adversarial trigger-to-forget attacks on the gate** (safety, given firing-more-forgets-more), open-world/novel-class drift blindness, classifier two-sample test (Lopez-Paz).

### [x] t2.5 — Noise-robust representation (read-side residual)  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 11 cards + `_SYNTHESIS.md` → `tier2-component-optimization/noise-robust-representation/` (0 fetch-fails; PTA/ADAPT preprint-flagged)
- **Headline for us:** P6 pinned the deferred residual as a coherent *translation* = a **first-moment error**, and the field's cheapest tool (mean-offset) is **geometrically EXACT** for it. Our SLDA namer + LUT + sleep already IS the ADAPT/T3A test-time-adaptation machinery — just never run awake/unsupervised. The 2024–25 flagship TTA line (FOA) went **forward-only for our exact reason** (no backward on the substrate) — external validation.
- **Biggest untried lever:** **tap-level activation shifting** (FOA output half + Schneider trust schedule) — stored clean tap-mean μ_s, running test EMA μ_t, read `a + λ(μ_s − μ_t)` before the namer, gate-conditioned. Closed-form, no bulk write, no extra pass; the analog form is an **auto-zero / offset stage at the read amplifier** — exactly the read-side fix P6/P10 deferred.
- **Leads:** NOTE/RoTTA (TTA statistics under autocorrelated streams → directly the P11 floor arenas); CMA-ES in-situ analog-knob tuner; confidence calibration of closed-form namers under drift. Cards-only: Laplacian-in-Gram, efficiency-adjusted TTA benchmarks.

### [x] t2.6 — Prototype / covariance drift compensation  (subagent: Fable 5 + finisher, 2026-07-10)
- **Papers written:** 5 cards + `_SYNTHESIS.md` → `tier2-component-optimization/prototype-drift-compensation/` (0 unverified)
- **Headline for us:** **SDC is the seminal closed-form answer to our exact P10 REV-staircase "namer goes stale between sleeps" failure**; LDC is the only compensator validated on a *moving unsupervised* backbone (closest to SCFF's endogenous drift); EFC++'s "train then re-balance prototypes" = our wake/sleep economy rediscovered. **HONEST VERDICT:** drift-compensation does NOT beat our periodic full re-fit on accuracy — sleep re-forwards the raw LUT and re-anchors *exactly* (P9.4 0.787→0.986); these methods only *estimate* it. The win is **between-sleeps interpolation + cadence relief**, not replacement.
- **Biggest untried lever:** **SDC-between-sleeps nudge** [closed-form][bounded][no new store] — transfer the measured motion of present-class running means to absent-class prototypes via one kernel-weighted average per fire, using features the awake namer already computes. Test: flatten the REV staircase at grid-8 → buy cadence back (GD-share 0.178 → lower).
- **Leads:** cards-only — EMA-representations-under-drift (2411.18704 → informs t2.7), Query Drift Compensation for retrieval (→ t3.1), Honda adversarial pseudo-replay, Layerwise Proximal Replay, PASS; build idea: wire an EFM-weighted meter into the deferred tap-drift gate.

### [x] t2.7 — EMA-of-closed-form-statistics: the "stable namer"  (subagent: Fable 5, 2026-07-10) — **CLOSES TIER 2**
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier2-component-optimization/ema-stable-namer/` (0 unverified)
- **Headline for us (de-hyped, honest):** the "stable namer" is a closed-form rebuild of a textbook slow anchor (Mean-Teacher/Polyak) — sound intent, but it **splits by channel**: mean-EMA = clean Polyak; **Gram-EMA = RLS-with-forgetting, which we ALREADY have (`RLSHead`) — not novel**; covariance-EMA = SPD-valid but **swells** (Arsigny: arithmetic SPD averaging inflates the determinant → softens the LDA boundary; log-Euclidean `exp(mean(log Σ))` is the principled fix). The Scap already IS an EMA register → the arithmetic form is nearly free. Literature predicts a **modest** gain → aim it at the *inter-sleep worst-point trough*, not "no averaging."
- **Most promising variant:** **EMA-of-Gram = slow-forgetting RLS, reusing `RLSHead`** (SPD-valid, Scap-native, no swelling for a ridge) — cheapest to test, largely a config of existing code.
- **Leads:** cards-only — RLS-forgetting-factor namer, Fisher/precision-weighted averaging (Matena 2022), tangent-space log-covariance classifier, "does swelling move an LDA boundary?" probe, Borkar two-timescale SA theory.

---
**TIER 2 COMPLETE** — 7 topics, ~62 cards. Rollup: `tier2-component-optimization/_TIER2-SYNTHESIS.md`. Next: Tier 3 (north star / horizon).

### [x] t3.1 — The hippocampus organ (NEXT BUILD)  (subagent: Fable 5, 2026-07-10) — opens Tier 3
- **Papers written:** 7 cards + `_SYNTHESIS.md` → `tier3-north-star/hippocampus-organ/` (0 unverified; all NEW to the dossier)
- **Headline for us (the next-build menu):** the most substrate-native *learning* memory in the whole menu is the **delta-rule Fast Weight Programmer** (Schlag 2021) — write/read are literally a crossbar write and read, **gradient-free**, composing with frozen SCFF (keys) + closed-form namer (values). **Titans (2025) confirms the exact architecture we sketched** (separate memory + surprise/error-gated write + explicit forgetting) is the field's frontier — from engineering, not neuroscience. Wang 2025 proves all these memories = one regression on 3 axes. Li 2020 **analog CAM** = our "recall = a physical settle" demonstrated in silicon.
- **Most promising first build:** a **delta-rule fast-weight associative memory on the crossbar** — `W += β(v−Wk)⊗k` write, `Wk` read. Minimal upgrade turning the passive LUT into a *learning* memory with NO backward pass — and **β is the home for our existing P8 DDM surprise gate.** Titans = the horizon (emulate its skeleton on this closed-form core, not its SGD-MLP); analog CAM = the fabric.
- **Leads enqueued:** enriched t4.1 (analog CAM / memristor Hopfield recall). Strong lead: **DeltaNet / gated-DeltaNet** (parallel delta memory = the substrate-legal Titans → informs t3.2). Cards-only: Sparse Distributed Memory (Kanerva), product-key/FAISS addressing, whitening→namer anisotropy, BABILong eval.

### [x] t3.2 — Recurrent "think until it settles" compute  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier3-north-star/recurrent-thinking/` (0 unverified)
- **Headline for us:** the settling loop has a **free analog-native halt v0** — Geiping 2025's convergence-halt needs no training; in analog it's **a comparator on "currents stopped changing."** monDEQ turns the settle into a **certificate** (constrain the recurrent crossbar contractive by construction → answers the North-star stability question). TRM + Energy-Based Transformers show **"correctness-as-a-feeling" already exists as engineering** (a BCE halt head / an energy plateau) — our novelty must be the *closed-form / analog execution*, not the idea.
- **Most promising first build:** a **contractive weight-tied block over frozen SCFF features, iterated to a fixed point; namer reads z*; halt = ‖Δz‖ threshold.** Zero new learned machinery, composes with all frozen organs, *physics does the iteration*. Measure accuracy-vs-iterations + iterations-vs-difficulty. (Geiping warns: free loops learn *non*-settling dynamics → force convergence.)
- **Leads enqueued:** enriched t4.2 (Ising EqProp, oscillator Ising machines, Kendall analog-EqProp-SPICE). Cards-only: path-independence (Anil), Mixture-of-Recursions, reasoning-by-superposition, Hopfield/CAM attractors as loop memory.

### [x] t3.3 — "Correctness is a feeling" — the self-signal  (subagent: Fable 5, 2026-07-10)
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier3-north-star/correctness-as-feeling/` (0 unverified)
- **Headline for us:** the field's reliable self-signal is a **dispersion over independent re-runs, NOT a magnitude** (Semantic Entropy, Nature 2024) — *literally our spine discipline (direction, not magnitude)* — and our substrate gets the re-runs **FREE**: thermal noise = the sampler, the namer = the meaning-equivalence-class. Gao's RM-overoptimization law makes **tap-drift-from-anchor the quantitative trust axis**. Huang 2023 is the anti-collapse warning: same-weights introspection adds nothing **without external grounding.**
- **Most promising buildable self-signal:** **re-settle agreement** — settle k times under the chip's own noise; the "feeling" = agreement of the namer reads (**semantic entropy run physically**). The one grounding safeguard: **gate, never target** — the feeling never becomes a training objective; its threshold is re-certified every sleep against error-EMA/labels (CALM), certificate validity tied to accumulated tap-drift.
- **Leads:** cards-only — Learn-then-Test / conformal calibration under drift, Semantic Entropy Probes (amortize k settles → 1 read), Skalse reward-hacking theory, generation-verification gap, PRM overoptimization.

### [x] t3.4 — The controller / prefrontal workspace  (subagent: Fable 5, 2026-07-10) — **CLOSES TIER 3**
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier3-north-star/prefrontal-controller/` (0 unverified)
- **Headline for us:** **Devillers & VanRullen 2024 is our near-exact twin** — a Global Workspace over *frozen* modules with self-supervised cycle-consistency glue + a thin labeled trickle = our economy. SGW gives the ready-made protocol (our WTA = slot competition, our DDM/drift gate = the write-gate it learns); Perceiver IO = the "small controller holds little, queries the rest" register. **HONEST VERDICT — not yet:** a coordinator is *premature* (one bulk + reading namer + passive LUT = nothing to coordinate). **Trigger:** once the hippocampus runs as a *second learning organ* and the settle loop must make it + the namer agree within a step budget — the first disagreement that costs loss. Build order then: Devillers frozen-organ register → SGW compete-for-slots → Perceiver k-slot register.
- **The real open research question:** a **gradient-free, streaming routing/gating rule that still induces specialization** — every published win credits *learned* routing. Genuinely ours to solve.
- **Leads:** cards-only — gradient-free/closed-form routing, cycle-consistency over non-invertible organs, BASE-Layers/OT assignment routing, attention-schema self-model (bridges t3.3), GW world-models.

---
**TIER 3 COMPLETE** — 4 topics, ~34 cards. Rollup: `tier3-north-star/_TIER3-SYNTHESIS.md`. Next: Tier 4 (adjacent wildcards).

### [x] t4.1 — Analog in-memory / crossbar compute for learning  (subagent: Fable 5, 2026-07-11) — opens Tier 4
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier4-adjacent-wildcards/analog-in-memory-compute/` (0 unverified)
- **Headline for us (validation + a publishable gap):** the **Scap is VALIDATED, strongly** — the capacitor is the field's best-in-class *update* device (record symmetry, unlimited endurance), and our **always-plastic SCFF sits in its friendly regime** (learning-as-refresh absorbs leakage); anything *static* (LUT, frozen weights) must be SRAM/NVM — a load-bearing choice. Our P8 meter shape is **silicon-confirmed** (MACs near-free, ADC taxed) and **5.4× reads conservative** vs field claims (172×, ~280×). Ambrogio's capacitor-fast/NVM-slow cell = **our awake/sleep economy in device form** (field converged on the 80/20 independently).
- **The single most important hardware reality (a CHALLENGE):** **on-array *update* is where analog learning dies** — a decade of mitigation (Tiki-Taka→TTv2→c-TTv2/AGAD) exists because `w += Δw` is NOT a free primitive; Tiki-Taka's implicit-cost result applies to *any* incremental analog rule incl. SCFF's, and **nobody has measured whether SCFF self-corrects or compounds under asymmetric/granular updates** → **realism-pass experiment #1, a potentially publishable gap.** Secondary: IR drop grows with array size → pressures P11's substrate-factor-grows-with-width extrapolation.
- **Leads:** **SCFF-under-update-non-ideality sweep (AIHWKIT harness) = the flagship realism experiment.** Cards-only: ECRAM (Scap w/o leakage), sign-based analog-native rules, PCM drift on stored prototypes (LUT tax), gain-cell charge-domain CIM, analog-CAM vs attractor-settle for the hippocampus read.

### [x] t4.2 — Equilibrium propagation & physics-based learning  (subagent: Fable 5 cards + Opus finisher, 2026-07-11)
- **Papers written:** 6 cards + `_SYNTHESIS.md` → `tier4-adjacent-wildcards/equilibrium-physics-learning/` (0 unverified)
- **Headline for us — VERDICT: NOT a threat; it's the RECURRENT LOOP's learning rule (complement via merge).** Every EqProp family member is supervised + settling → can't replace our label-free one-pass bulk; but the north-star loop settles anyway, so **SCFF stays the feed-forward bulk while EqProp trains the loop's recurrent weights** (the credit-depth the closed-form namer structurally can't reach). Laborieux **holomorphic EqProp** = exact gradients from **one settle + AC lock-in** (no 2nd phase, ImageNet-32 at BP parity) — kills the main cost. Scellier disarms the "why not EqProp" reviewer: EqProp solves supervised *static*, our bulk solves label-free *continual* — different problems.
- **Key experiment (ties t4.1):** Yi/Kendall's two-state differencing **self-cancels systematic device error** → does **SCFF's contrastive-pair difference also cancel systematic Scap error?** A direct probe at t4.1's flagship update-non-ideality gap. + economy-legal **gate-fired nudged re-settle** (fire EqProp's 2nd phase only when the drift gate trips).
- **Leads:** Restricted Kirchhoff Machine (label-free CLLN = our regime), Laborieux 2023 Jacobian homeostasis (drops W=Wᵀ), non-dissipative/oscillator EqProp. Cards-only: Kendall 2020, deeper-EqProp scaling.

### [x] t4.3 — Neuromorphic / spiking online learning  (subagent: Opus, 2026-07-11)
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier4-adjacent-wildcards/neuromorphic-spiking/` (0 unverified)
- **Headline for us — VERDICT: COMPLEMENT (deferred merge-target); a DISTRACTION if pulled in now.** For the *current* feed-forward i.i.d. closed-form object, spiking/e-prop buys nothing (no time axis; OTTT/SLTT/OSTL keep the very gradient our namer dropped). For the *north-star recurrent loop*, e-prop's **"local trace × broadcast signal" = our SCFF-bulk + drift-gated-namer with a time axis**, and the **eligibility trace = a leaky capacitor we already own.** Merge the *rule*, not the spikes (OSTL proves it works rate-based). **ETLP** = closest twin (third factor = random-projected label, NO gradient = our RanPAC/SLDA namer). **CLP-SNN on Loihi 2 (Intel 2025) is a published on-silicon COMPETITOR on our exact pitch** (rehearsal-free continual on-chip, ties replay at 6,600× less energy) — cite it; neurogenesis+metaplasticity = hippocampus fuel; algorithm×substrate split mirrors P8.7.
- **Biggest untried lever:** a **"SCFF-in-time" sim rung** — one eligibility register per weight (the leaky cap) + a broadcast learning signal on a minimal recurrent bulk. A time axis without spikes.
- **Leads:** RTRL + modern approximations (Zucchet/Orvieto 2023 → t3.2 loop), neurogenesis+metaplasticity (Kudithipudi 2022 → t3.1). Cards-only: DFA/DRTP (already t1.6), NeuroTrain benchmark.

### [x] t4.4 — State-space & liquid / continuous-time atoms  (subagent: Opus, 2026-07-11) — closes Tier-4 core
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier4-adjacent-wildcards/state-space-liquid-atoms/` (0 unverified)
- **Headline for us:** a **diagonal linear SSM IS a leaky-cap register bank** — IMSSA + CIM-SSM prove it maps to our **exact hardware** (memristor short-term-memory decay natively = the SSM `A` matrix); "the substrate's physics IS the math" is demonstrated silicon for the *temporal* case. **Liquid-S4 collapses the whole atom menu** (liquid neuron == SSM, one "liquidness" knob). The **gated delta rule** = the substrate-legal write/forget algebra for the hippocampus LUT (extends t3.1).
- **Most promising recurrent atom:** a **frozen HiPPO-init diagonal SSM (S4D/S5) as a *reservoir* + our existing closed-form namer as the only trained part** — most analog-native, BPTT-free, *literally SCFF+namer extended to time.* **Honest caveat:** every SSM is BPTT-trained and analog-native-ness correlates *negatively* with accuracy → crux = "is frozen-recurrence + closed-form-readout good enough on our drift streams?" (untested).
- **Leads:** **frozen-SSM-reservoir + namer on Phase-11 real streams (crux experiment)** · **local/gradient-free learning of SSM decay & delta-gates** = part of the t3.4 flagship open problem. Cards-only: HiPPO theory, Mamba-2 SSM≡linear-attention (→t3.1), event-driven SSMs (→t4.3), QS4D analog-realism.

### [x] t4.5 — Honest energy benchmarking for training  (subagent: Opus, 2026-07-11) — **CLOSES TIER 4**
- **Papers written:** 8 cards + `_SYNTHESIS.md` → `tier4-adjacent-wildcards/energy-benchmarking-protocol/` (0 unverified)
- **Headline for us:** Dehghani "Efficiency Misnomer" **legitimises our honest split** — we *lose* on FLOPs/sample, *win* on pJ; the decoupling is **predicted, not cherry-picked** (single cost proxies rank models oppositely → report several at matched accuracy). Horowitz + Gholami are the **physics under "the win is the substrate"**: they price the data-movement term compute-in-memory deletes, and Gholami shows that term is **growing** — the mechanism behind P11's substrate factor climbing 5.4→7.4×.
- **The recipe element that matters most:** report energy only at a **matched accuracy/retention point**, with the **same-substrate algorithm-joules ratio as the load-bearing number (reported even though it LOSES — P10 R1)** and the analog substrate factor as a **separately-labelled multiplier** in Horowitz/Gholami currency (arithmetic term unchanged + movement term deleted) — **never fused into one flattering headline.** (This is already our discipline; now it's citable.)
- **Leads:** analog-crossbar/PIM measured energy model to anchor the substrate factor (bridge to the realism layer), continual "energy-to-retention" MLPerf-style protocol. Cards-only: roofline reporting, Luccioni 2024.

---
**TIER 4 COMPLETE** — 5 topics, ~42 cards. Rollup: `tier4-adjacent-wildcards/_TIER4-SYNTHESIS.md`. Next: Tier 5 (open exploration).

### [x] t5.1 — Energy-based learning as the unifying frame  (subagent: Opus, 2026-07-11) — opens Tier 5
- **Papers written:** 10 cards + `_SYNTHESIS.md` → `tier5-open-exploration/energy-based-learning/` (0 unverified)
- **The unifying picture:** one equation runs through all of it — `E(x)` low=good, inference = argmin E, learning = reshape E. Through that lens **SCFF-goodness, Hopfield/attention, EqProp, predictive coding, diffusion, and the settling-loop/halt-feeling are the SAME energy descent.** Beneath it, Landauer: the unavoidable cost is *erasing* bits → a **resident-weight, settle-don't-erase substrate is on the cheap side of physics.**
- **Two ideas to carry back:** (1) **Aifer 2023 + Melanson 2025 make our closed-form namer ANALOG-NATIVE** — a ridge/Gram solve is the *minimum of a quadratic energy*, exactly what an analog oscillator/RLC network settles into (`⟨x⟩=A⁻¹b`, covariance `A⁻¹`, a *built* chip). **The namer re-fit could be a PHYSICAL SETTLE, not a numpy solve — the strongest concrete lever for the deferred analog-realism pass.** (2) **Hoover 2023 Energy Transformer = the north-star think-loop, published** (depth = settle-steps on resident weights; the energy value = the halt/confidence feeling → ties t3.2+t3.3).
- **Leads:** **quadratic-energy↔ridge identity = the analog-namer design equation** (flag for the realism pass); Dense Associative Memory (→ t3.1 hippocampus capacity). Cards-only: thermodynamic training primitives, Bérut 2012 Landauer verification, energy-vs-score for a generative organ.

### [x] t5.2 — Learning IS compression / MDL / superposition  (subagent: Opus, 2026-07-11) — **CLOSES TIER 5 & THE SEEDED SWEEP**
- **Papers written:** 9 cards + `_SYNTHESIS.md` → `tier5-open-exploration/learning-as-compression/` (0 unverified)
- **The picture:** a model that generalizes is one that *compressed* its data (MDL); over-capacity is safe (double descent), used-capacity holds more features than neurons via **sparse superposition**, most weights are search-overhead (lottery ticket). **Our spare-capacity hypothesis IS superposition + lottery ticket — the substrate's sparsity is the precondition superposition needs; the capacity bet and the substrate property are the same claim.**
- **Biggest carry-back:** **we have never MEASURED our compression** (P11 only half-confirmed via retention). Two cheap metrics close it: (1) **prequential codelength in bits** (P11 already computes prequential accuracy — one `−log p` away), (2) **a sparse autoencoder on the frozen bulk → count the feature dictionary = spare capacity *used*.** Honest counterweight: forward-only lacks grokking's weight-norm *cleanup* pressure → the slack could be dead memorization, not shareable capacity (real, testable).
- **Leads:** operational compression metrics (codelength + SAE dictionary) as first-class numbers; **superposition under temporal correlation = the P11 autocorrelated-FLOOR mechanism** (ties t1.7/t2.5). Cards-only: intrinsic-dimension (Pope 2021), progress-measures as a convergence invariant.

---
**TIER 5 COMPLETE** — 2 topics, 19 cards. Rollup: `tier5-open-exploration/_TIER5-SYNTHESIS.md`.

## ★★★ SEEDED SWEEP COMPLETE — all 5 tiers, 27 topics, ~218 verified cards ★★★
Master close-out: `auto-research/_SWEEP-SYNTHESIS.md`. Per-tier rollups: `tierN-*/_TIERn-SYNTHESIS.md`. Full paper table: `auto-research/INDEX.md`.
**Remaining fuel (optional next runs):** the "cards-only" leads + experiment ideas logged in each done-block above are recorded but NOT made into full topics — a future session can promote any of them (see `_SWEEP-SYNTHESIS.md` § "The lead backlog").
