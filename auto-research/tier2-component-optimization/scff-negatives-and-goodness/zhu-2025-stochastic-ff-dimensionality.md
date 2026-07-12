# Stochastic Forward-Forward Learning through Representational Dimensionality Compression
- **Authors / Year / Venue:** Zhichao Zhu, Yang Qi, Hengyuan Ma, Wenlian Lu, Jianfeng Feng / 2025 / arXiv:2505.16649
- **Link:** https://arxiv.org/abs/2505.16649
- **Tier / Topic:** tier2-component-optimization / t2.1 SCFF negatives & goodness
- **Relevance:** ⭐⭐⭐⭐ — a second-order goodness (effective dimensionality) that is **negative-free** and treats **noise as the constructive ingredient** — the same bet as our P6 noise-augmented view, taken further: noise is not an augmentation, it is the mechanism.

## TL;DR
Proposes a goodness function based on the **effective dimensionality (ED)** of a layer's noisy response distribution: *compress* ED across noisy copies of the same input (responses to one thing should collapse to a tight, low-dimensional cloud) while *expanding* ED across the sample distribution (different things should spread across many dimensions). Second-order statistics (neuron-neuron correlations) enter the objective directly. No negative samples needed; noise improves generalization; inference reads the mean of squared outputs.

## The mechanism (how it actually works)
The story: run the same input through the layer several times with noise (stochastic units); the cloud of responses has a covariance, and ED ≈ (Σλ)²/Σλ² of that covariance counts "how many dimensions the cloud really uses." The objective is a two-sided pressure on ED: per-input clouds should be *compressed* (all noisy copies of one input agree — this is invariance, played by noise instead of augmentation) while the across-inputs ensemble stays *expanded* (the representation keeps many live dimensions — this is anti-collapse, played by ED instead of negatives or a covariance penalty). It is VICReg's logic re-expressed in one spectral quantity, with the "two views" replaced by cheap intrinsic noise. Because compression is defined per-input and expansion over the stream, no partner sample is ever fetched. Predictions read the mean of squared outputs over noisy runs — averaging turns the noise into an ensemble.

## Key results / claims
- Competitive with other non-BP local methods on standard image benchmarks (their comparisons; modest absolute numbers, consistent with the FF family).
- Noise is constructive: adding it improves generalization and inference-by-averaging — pitched explicitly at neuromorphic hardware where noise is free.
- Incorporates second-order structure that Σh²-style goodness ignores.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk objective; P6 (noise-augmented view); the analog-realism queue (device noise as a resource).
- **Same as us:** local, forward-only, label-free; "one view is a noisy copy" — our P6 NoiseAugContrast is their mechanism at n=2 samples; on our substrate the noisy copies are *free* (device noise), which is the strongest substrate-fit argument in this whole topic.
- **Different from us:** they need *several* noisy forward passes per input to estimate a covariance/ED (we carry two rails); their anti-collapse is spectral (ED), ours is contrast against partners; no temperature, no negatives.
- **What we could borrow or test:** the framing "invariance-to-noise + spread-across-stream, both measured on statistics the layer already produces." A substrate-honest approximation: keep two rails (clean + noisy — what we have), replace the InfoNCE denominator with a running **variance/participation floor** per unit (an EMA accumulator — cheap) — i.e., this paper's objective degraded gracefully toward VICReg-lite. Full ED needs eigen-structure (Σλ² ≈ ||C||_F²) — a D×D correlation estimate per layer; expensive as digital math, though a crossbar computes Gram-like products natively, worth one design note before dismissing.
- **What contradicts or challenges us:** their result that *more* noise samples per input helps says our two-rail mono-forward may be under-using the substrate's free noise — an argument for k>2 rails (or temporal averaging over consecutive noisy steps) that we've never priced.

## Follow-on leads
- The "noise as regularizer" bridge to our P6.8 Door-B result (direction forms from a fully-noisy stream) — same phenomenon class.
- Participation ratio / ED as a *monitoring invariant* (our dead-unit fraction check is the k=1 version of ED).
