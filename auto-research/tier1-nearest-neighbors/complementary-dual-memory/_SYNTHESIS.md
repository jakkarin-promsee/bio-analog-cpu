# Synthesis — Complementary Learning Systems as built ML architectures (dual-memory design)  (Tier 1)
**The question:** Who else splits learning into fast + slow memories with consolidation between them, and **exactly how is our object different**? Find dual-memory tricks we haven't used.

**Already in `draft6.0/research/`:** CLS *theory* (McClelland 1995 / Kumaran 2016) and the memory-organ menu (NTM, DNC, Memory Networks, Modern Hopfield, kNN-LM/RETRO, Fast Weights) — `north-star/1-memory.md`. Maintenance mechanics (ER/Rolnick, EWC, SI, A-GEM, REMIND, MGSER-SAM, CBRS/Chrysakis, Davari drift) — `phase9/maintenance-and-replay.md`. On-device wake/sleep systems (SIESTA, latent replay, Miro) are **t1.3**, not re-carded here. This card set covers the **built dual-memory *architecture* principle** and its 2021–2025 variants, which the curated library only names in passing.

## The landscape (the camps)
Everyone in this topic accepts the CLS thesis — one memory can't be both fast-specific and slow-general — and *builds* the split. They differ on **what the two memories are** and **how consolidation happens between them**:

1. **Weight-EMA semantic memory (the mainstream).** **CLS-ER** (Arani 2022) is the canonical build: one backprop worker + two EMA copies (fast "plastic", slow "stable") at different decay rates + a small reservoir buffer; consolidation *is* the EMA, deploy the slow one. **ESMER** (Sarfraz 2023) extends it with an **error statistic** governing both the learning signal (down-weight large/abrupt errors) and buffer admission (keep low-loss samples), buying task-boundary stability + label-noise robustness.
2. **Two-network fast/slow representation.** **DualNet** (Pham 2021): a **self-supervised slow backbone** + a **fast supervised adapter**, co-trained by backprop — the mainstream-ML statement of our "unsupervised bulk + supervised namer" 80/20.
3. **Generative replay dual memory.** **DGDMN** (Kamra 2017): the two memories are *generators*; consolidation replays *dreamed* pseudo-samples instead of stored ones — the store-vs-generate fork.
4. **Multi-mechanism / neuron-level (the kitchen sink).** **TriRE** (Vijayan 2023): retain-salient-neurons + rewind-relearn-idle-neurons + rehearsal, stacked — wins by mechanism count, needs a plastic backbone + task boundaries.
5. **Minimalist ablation (the 2025 corrective).** **FSC-Net** (El Gorrim 2025, ⚠ preprint): strips it to a fast net + a replay-consolidated slow net and finds the **timescale separation, not architecture**, is load-bearing, and **pure replay beats replay+distillation** (distillation = recency bias).

The through-line: in *every* one of these, **both memories are neural networks trained by gradient descent**, and consolidation is either **weight averaging** (CLS-ER/ESMER), **joint backprop** (DualNet), **distillation** (FSC-Net's rejected arm, DER), or **generative replay** (DGDMN).

## How WE differ  ← the money section
Our object is a dual-memory system whose **three defining choices are each the road-not-taken above**:

1. **The slow system is a *frozen, unsupervised, forward-only* cortex — not a trained network and not an EMA of one.** SCFF learns by a local contrastive rule with **no backprop and no labels**; its "slowness" is intrinsic drift/rotation, not a decay rate. Every method here trains its slow system with gradients (and DualNet/TriRE even push *labels* into it). Nobody else's slow memory is label-free-and-gradient-free.
2. **The fast memory is a *service, not a second brain*.** Our LUT is a **non-parametric exemplar/prototype store** that feeds the cortex its contrastive **negatives** and holds **replay history** — it *never classifies*. In CLS-ER the "plastic memory" is itself a working classifier; in DualNet the fast learner does the prediction; in DGDMN the fast memory is a generator. Ours is plumbing for the other two organs.
3. **Consolidation is a *closed-form analytic re-fit*, not SGD/EMA/distillation.** Sleep re-solves the SLDA/RanPAC head over the LUT in closed form (grid-4 cadence, CBRS eviction). No gradient, no weight-average, no distillation term. FSC-Net's 2025 result ("pure replay > distillation") is external evidence this is the *right* minimalism, and our own P9.0 shows why we can afford it: the bulk **rotates but doesn't forget**, so only the small convex head needs re-aiming.

Net placement: the field validates our *skeleton* (fast store + slow general learner + rehearsal, deployed-slow) and even our *objective choice* (DualNet: SSL-slow beats supervised-slow for transfer). What's genuinely **ours** is the **triple substitution** — frozen-unsupervised cortex ⊕ non-parametric LUT-as-service ⊕ closed-form consolidation — which no dual-memory paper combines, and which is what makes the loop cheap enough for an analog substrate with no backward pass on chip. The honest cost, which this literature makes visible: letting supervision into the slow system (DualNet) or governing a plastic net by error (ESMER) can out-accuracy us on static difficulty — consistent with our own P4/P10 "continual-not-static" verdict.

## The gap / what we haven't tried (concrete, testable)
- **★ A slow-EMA "stable namer" (from CLS-ER/ESMER), done in closed form.** Our namer's state is running statistics (SLDA means + tied covariance; RanPAC Gram). An EMA of *those statistics* — `Σ_stable ← α·Σ_stable + (1−α)·Σ_fast` — gives a second, anti-recency, flatter stability anchor **with zero gradient**, deployable alongside the fast namer. This is the dual-memory field's single most load-bearing trick (weight-EMA consolidation) and we've never applied it; it's fully compatible with our closed-form constraint, and it directly targets our worst-point-BWT/recency concern that grid-4 cadence currently fights with sleep frequency. **Top lever.**
- **Error-graded consolidation instead of a binary gate (ESMER).** Replace the fire/don't-fire DDM gate with a per-sample **error weight** on the analytic re-fit (down-weight huge-error boundary/outlier samples). Drops straight into the weighted running Gram/mean — no gradient — and is the published route to the label-noise robustness we currently get only from P6 feature augmentation. May dissolve the "firing more forgets more" tension by admitting boundary samples *gently*.
- **Error-sensitive eviction as a CBRS hybrid (ESMER).** Balance classes (CBRS) *and* prefer low-error exemplars — a concrete P9.3 follow-up.
- **A closed-form gain/modulation head (DualNet's adapter, de-gradiented).** A diagonal tap-channel re-weighting fit at sleep — recovers a little of the expressivity we forgo by forbidding backprop into the bulk, without breaking the forward-only wall.
- **Generative replay for the hippocampus organ (DGDMN / Brain-Inspired Replay).** Not for the frozen loop, but on the backlog for the next build: a hybrid raw-prototype + cheap-generator LUT for the very-long stream, benchmarked against our P11 "prototype out-retains byte-matched replay" result.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Arani et al. 2022 — CLS-ER](arani-2022-cls-er.md) | ⭐⭐⭐⭐⭐ | The canonical built CLS; the slow-EMA "stable memory" = our top untried closed-form lever. |
| [Sarfraz et al. 2023 — ESMER](sarfraz-2023-esmer.md) | ⭐⭐⭐⭐⭐ | Error-statistic governs learning + buffer — plugs into our error-EMA gate + CBRS; gives label-noise robustness. |
| [Pham et al. 2021 — DualNet](pham-2021-dualnet.md) | ⭐⭐⭐⭐ | The fast/slow SSL-vs-supervised split = our 80/20 in mainstream ML; SSL-slow>supervised-slow supports frozen cortex. |
| [El Gorrim 2025 — FSC-Net](elgorrim-2025-fsc-net.md) | ⭐⭐⭐⭐ | 2025 ablation: timescale-not-architecture + pure-replay>distillation — external support for our minimal closed-form re-fit (⚠ preprint). |
| [Vijayan et al. 2023 — TriRE](vijayan-2023-trire.md) | ⭐⭐⭐ | The "stack every brain mechanism" pole — the discipline contrast; usage-recycling framing for LUT eviction. |
| [Kamra et al. 2017 — DGDMN](kamra-2017-dgdmn.md) | ⭐⭐⭐ | The generative-replay fork we chose against (raw store dodges drift); on the hippocampus-organ backlog. |

## Leads spawned
- **Weight/statistic-EMA consolidation family** (Mean-Teacher, Tarvainen 2017 → CLS-ER → ESMER) — the EMA-as-consolidation lineage; worth a focused card on EMA-of-closed-form-statistics feasibility.
- **Generative/feature replay for the hippocampus organ** (Deep Generative Replay Shin 2017; Brain-Inspired Replay van de Ven 2020; Joint Diffusion 2024) — a t3/north-star topic for the *next build*, not the frozen loop.
- **Label-noise-robust continual learning** (ESMER's error-buffer → SPR, noisy-label CL) — the axis where error-sensitivity buys robustness we get elsewhere.
- **Winning-subnetwork / capacity-recycling CL** (PackNet, SupSup, NISPA) — only if the LUT ever needs a smarter allocation policy than CBRS.
