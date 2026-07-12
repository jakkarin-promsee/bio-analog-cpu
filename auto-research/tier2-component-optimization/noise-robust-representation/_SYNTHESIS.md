# Synthesis — Noise-/shift-robust representation on a frozen backbone: the read-side / test-time fix  (Tier 2, t2.5)

**The question:** For the P6-named deferred residual — a *directional, non-zero-mean input-transducer shift* (a coherent translation along the class axis) that survives the `NoiseAugContrast` hardening and must be corrected on the Stage-2 read side *without touching the frozen bulk* — what test-time / read-side method most cheaply corrects it, ranked by robustness benefit × substrate fit (closed-form? no bulk write? extra pass?).

**Already in `draft6.0/research/`:** the phase6 curated set covers the *train-time* half — noise-as-augmentation (Bishop noise=Tikhonov), flatness (SAM/S-SGD), LP-FT (why a frozen head can't manufacture backbone robustness), the Rasch channel analog, and the forward-only noise toolbox. **Not covered there:** everything *after* training — the test-time-adaptation (TTA) literature this folder cards. Also already ours: **P9.4's proto-reanchor** (sleep-time prototype re-anchoring recovers the transducer residual 0.79→0.99) — which, this sweep finds, is a member of a published family (T3A → ADAPT/PTA) we can now name and extend. ESMER is already carded in t1.4; its label-noise slot here is filled by SPR (Kim 2021).

## The landscape

The field split into four camps after TENT (2021) posed "adapt a deployed model with unlabeled test data only." **(1) Optimization TTA** (TENT, SAR, EATA, CoTTA): descend a self-supervised objective (entropy, consistency) into a small parameter subset — the strongest gains on paper, but the IJCV 2024 survey's re-benchmark shows the gains ride on large iid test batches; at batch size 1 on dependent streams (our regime) they destabilize or fall below the frozen baseline. **(2) Statistics correction** (Schneider 2020, ActMAD, NOTE): re-estimate feature moments on the test stream and re-center/re-scale — closed-form, gradient-free at its core, and Schneider showed the moment-swap alone recovers most corruption robustness. **(3) Prototype / closed-form inference** (T3A, ADAPT, PTA, TDA): keep the backbone and even the weights of the head frozen; move the *class statistics* — running means (+ optionally one shared covariance) updated from confident test samples, classification stays a closed-form discriminant. This camp converged, apparently without noticing, on SLDA's exact algebra. **(4) Input purification** (DDA): project the input back to the source manifold with a frozen generative model — the most robust per-assumption (no cross-sample state to poison), the most expensive per-sample.

Two field-wide verdicts matter for us. First, the *decomposition* result: TENT's gain was always two parts — a closed-form statistics swap plus a small learned modulation — and the closed-form part carries most of the weight (Schneider; FOA's ablation of its activation-shifting half). Second, the *forward-only turn*: by 2024–2025 the flagship line (FOA, ICML 2024 oral; ADAPT, NeurIPS 2025; BFTT3D; Purge-Gate) explicitly targets backprop-free deployment — quantized ViTs, FPGAs, edge — for exactly our reason: the substrate cannot afford a backward pass. The digital edge rediscovered our constraint set and is now publishing inside it.

## How WE differ

- **Our enemy is narrower and better-characterized than theirs.** TTA papers fight arbitrary corruption; P6 pinned our residual as a *coherent translation of the feature cloud* (per-sample cos ≈ 0.97 — it barely rotates; it moves the cloud off the frozen readout). A translation is a *first-moment* error. The literature's cheapest tool (mean-offset correction) is not a compromise for us — it is the geometrically exact tool.
- **We already own half the machinery.** The namer *is* running class means + shared covariance + closed-form solve (SLDA) — ADAPT ships that as a 2025 SOTA test-time adapter. The LUT is their "knowledge bank"; sleep is their anchored re-fit; P9.4's proto-reanchor is T3A executed at sleep time. What we have NOT done is run any of it *awake*, between sleeps, unsupervised.
- **We have the safety result they lack.** P8's "firing more forgets more" is the measured version of what LAME and the survey report anecdotally (adaptation often hurts). Our gate is a published-grade answer to the field's open stability problem — any borrow below must stay gate-conditioned, which is a discipline the TTA camp mostly lacks.
- **Genuinely ours / not in this literature:** the energy-metered accounting of a correction (their cost unit is GFLOPs, and only the survey prices cost at all), the analog reading of mean-correction as an auto-zero/offset stage, and the gate-conditioned (rather than always-on) adaptation economy.
- **Honest re-invention flag:** "proto-reanchor" should cite T3A/ADAPT as its family when written up; it is not novel as a mechanism, only as a *sleep-time, true-label-anchored* variant.

## The gap / what we haven't tried — ranked (benefit × substrate-fit)

1. **Tap-level activation shifting (FOA's output half + Schneider's trust schedule).** Keep a stored clean tap-feature mean μ_s; maintain a running test EMA μ_t as a free byproduct of awake forwards; before the namer, read a := a + λ(μ_s − μ_t), with λ trust-scheduled by Schneider's N/(N+n) blend and enabled only when the error-EMA gate trips. Targets a coherent translation exactly. *Substrate fit: closed-form YES · bulk write NONE · extra pass NONE · analog form = an offset/auto-zero stage at the read amplifier.* **The rung to run first.**
2. **Awake, confidence-weighted prototype tracking (T3A → ADAPT → PTA), gate-conditioned.** Between sleeps, let confident samples update a *shadow* copy of the namer's class means (PTA's confidence-∝ weighting; LUT prototypes as ADAPT's anchor against self-label bias); the DDM gate decides when the shadow is promoted. Extends P9.4 from sleep-time to awake-time. *Fit: closed-form YES (SLDA's own update rule + a weight) · bulk write NONE · extra pass NONE · risk = self-label bias, held by gate + LUT anchor.*
3. **Second-moment escalation only if rung 1 plateaus (Schneider variance / ActMAD per-feature stats).** A diagonal rescale toward stored clean variances — still closed-form; P6's translation geometry and P9.4's no-covariance-refit negative both predict this is NOT needed; run as the falsifier, not the plan.
4. **LUT-Laplacian posterior smoothing (LAME, memory-backed).** Smooth the namer's per-sample posterior against its k nearest *stored prototypes* (persistent neighborhood, so batch-free) via a few concave-convex fixed-point steps. The cheapest "cannot make things worse" control arm. *Fit: closed-form-adjacent (fixed-point iters) · no writes at all · extra dot-products against the LUT only.*
5. **Multi-layer statistic as drift localizer (ActMAD's statistic, our gate's consumer).** Upgrade the validated-not-shipped P8.2 tap-drift trigger to per-feature mean/var across taps — tells transducer-channel from tap-channel shift apart (the diagnostic P6 wanted); feeds rungs 1–2 their λ. *Fit: bookkeeping only.*
6. **Error-weighted LUT admission (ESMER-flavored; SPR as the named escalation).** Admission weight from the error-EMA the gate already maintains; quarantine high-surprise samples until confirmed. Only pays past the noise level where P6.4's purity-null holds; SPR marks that regime's published solution. *Fit: closed-form YES · reuses existing state.*
7. **Self-ensembled correction guard (DDA's trick, one line).** When the gate is suspicious, run corrected + uncorrected views and keep the more confident — a do-no-harm wrapper for rungs 1–2 at the price of one extra forward, only on gate-trip. *Fit: extra pass YES (rare, gated).*
8. **Anti-patterns, on the record:** entropy-descent TTA (TENT lineage) — collapses at batch 1 per the survey, violates no-backward; diffusion input purification (DDA proper) — corrector bigger than the brain, inverts the 80/20 economy.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Schneider 2020 — BN covariate-shift adaptation](schneider-2020-bn-covariate-shift.md) | ⭐⭐⭐⭐⭐ | Moment re-estimation alone recovers most corruption robustness + the N/(N+n) trust schedule |
| [Niu 2024 — FOA (forward-only TTA)](niu-2024-foa.md) | ⭐⭐⭐⭐⭐ | Activation shifting: the one-vector closed-form cure for a coherent feature translation; beats gradient-TENT backprop-free |
| [Zhang 2025 — ADAPT](zhang-2025-adapt.md) | ⭐⭐⭐⭐ | SLDA's algebra as a SOTA test-time adapter; shadow-mean updates + anchor = the safe awake-tracking recipe |
| [Iwasawa 2021 — T3A](iwasawa-2021-t3a.md) | ⭐⭐⭐⭐ | The backprop-free prototype-adjustment root; names P9.4's family |
| [Wang 2024 — OTTA survey (IJCV)](wang-2024-otta-survey.md) | ⭐⭐⭐⭐ | The batch-size-1 verdict: statistics/prototype methods survive our regime, optimization TTA doesn't; price adaptation cost |
| [Mirza 2023 — ActMAD](mirza-2023-actmad.md) | ⭐⭐⭐ | Which statistic localizes shift: per-feature mean/var across depths — the P8.2 trigger upgrade |
| [Boudiaf 2022 — LAME](boudiaf-2022-lame.md) | ⭐⭐⭐ | Output-only correction that cannot destroy the model + the dependent-stream skepticism |
| [Wang 2021 — TENT](wang-2021-tent.md) | ⭐⭐⭐ | The field's anchor and our anti-pattern: the gain decomposes into closed-form stats + learned modulation |
| [Huang 2026 — PTA](huang-2026-pta.md) | ⭐⭐⭐ | Cache-free confidence-∝ prototype accumulation — the O(1)-memory weighting discipline for awake tracking (⚠ preprint) |
| [Kim 2021 — Self-Purified Replay](kim-2021-self-purified-replay.md) | ⭐⭐⭐ | Label-noise CL: purity machinery's payoff regime; scopes P6.4's "not needed" honestly |
| [Gao 2023 — DDA](gao-2023-dda.md) | ⭐⭐ | The input-purification pole: right robustness shape, wrong economy; the self-ensembling do-no-harm guard |

## Leads spawned

- **NOTE / RoTTA (temporally-correlated test streams):** statistics estimation designed for autocorrelated streams — speaks directly to the P11 HAR/ELEC2 floor arenas.
- **CMA-ES on frozen substrates:** FOA's derivative-free optimizer as a general in-situ tuner for analog knobs (north-star adjacent).
- **Graph/Laplacian-regularized closed-form heads:** folding LAME-style smoothing into the namer's Gram algebra — no published treatment found.
- **Confidence calibration of closed-form namers under drift:** what plays ADAPT's zero-shot-prior role when there is no CLIP — open question, one-rung experiment.
- **Efficiency-adjusted TTA benchmarks (2025+):** the external yardstick if the read-side fix is ever written up.
- **Cheaper diffusion-free input purification (GDA lineage):** watch-list only; the economy argument stands.
