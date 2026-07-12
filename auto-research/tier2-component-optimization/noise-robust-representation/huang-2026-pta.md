# Prototype-Based Test-Time Adaptation of Vision-Language Models (PTA)
- **Authors / Year / Venue:** Zhaohong Huang, Yuxin Zhang, Wenjing Liu, Fei Chao, Rongrong Ji / 2026 / arXiv:2604.21360 (preprint)
- **Link:** https://arxiv.org/abs/2604.21360
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐☆☆ — the 2026 edge of the gradient-free prototype line: cache-free, confidence-weighted prototype *accumulation* instead of sample caches — the memory-economics upgrade of T3A, directly shaped like our LUT.

## TL;DR
PTA adapts CLIP-style frozen models at test time with per-class "knowledge prototypes" that *accumulate* confident test features by weighted averaging — no cache of individual samples, no gradients, no LLM priors. It keeps 92% of the frozen model's inference speed (cache-lookup competitors drop to ~50%) while beating them on accuracy across 15 recognition benchmarks.

## The mechanism (how it actually works)
The story: cache-based TTA (TDA-style) stores individual confident test samples per class and answers by retrieval — memory and lookup cost grow with the stream. PTA compresses the cache to its sufficient statistic: one prototype per class, updated as a running weighted mean where the weight is the zero-shot confidence of the frozen model on that sample. High-confidence samples move their class prototype more; junk barely registers. Inference blends the frozen classifier's score with proximity to the accumulated prototypes. The whole adapter is K vectors of state and one weighted-average update per sample — O(1) memory in stream length, one MAC-scale update, fully closed-form.

## Key results / claims
ImageNet-1K 65.64% → 69.38% over frozen CLIP across cross-domain benchmarks; evaluated on 15 image and 4 point-cloud benchmarks; retains 92% of frozen-model throughput vs ~50% for cache-retrieval TDA. Preprint (not yet peer-reviewed) — treat numbers as claimed, method as clear.

## How it relates to us
- **Organ / phase touched:** the hippocampus LUT + the namer's prototypes; the awake/sleep economy.
- **Same as us:** "store the running statistic, not the samples" is our LUT-vs-replay-buffer decision, re-derived in TTA-land — their cache-free argument is P11's namer-out-retains-byte-matched-replay finding wearing a throughput costume. Confidence-weighted prototype accumulation is the T3A idea made stream-scale.
- **Different from us:** their confidence weight comes from a zero-shot vision-language prior; ours would come from the namer's own posterior (weaker, self-referential) — the honest gap in porting it. No gate: they accumulate always-on; we would gate.
- **What we could borrow or test:** the *weighting discipline* for any awake prototype tracking we try (T3A/ADAPT borrow): update-weight ∝ confidence, so the drift-tracking is soft rather than filtered-in/out — cheaper than T3A's top-M support-set bookkeeping and closer to an analog implementation (a confidence-scaled write current into the LUT cell).
- **What contradicts or challenges us:** their throughput framing is a reminder that any read-side fix we add gets judged on our own meter (P8): if the correction costs more namer-energy than the errors it prevents, the gate should keep it off.

## Follow-on leads
- TDA (Efficient Test-Time Adaptation for VLMs, CVPR 2024) — the cache-based baseline PTA compresses.
- ProtoTTA (arXiv 2604.15494) — parallel 2026 prototype-guided TTA line.
- Confidence calibration of a closed-form namer under drift (what plays the zero-shot prior's role for us) — open; candidate experiment.
