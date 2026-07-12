# Task-recency bias strikes back: Adapting covariances in Exemplar-Free Class Incremental Learning (AdaGauss)
- **Authors / Year / Venue:** Grzegorz Rypeść, Sebastian Cygert, Tomasz Trzciński, Bartłomiej Twardowski / 2024 / NeurIPS 2024
- **Link:** https://arxiv.org/abs/2409.18265
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐ — the field's direct attack on our two named weak points at once: per-class covariance (anisotropy) *and* what happens to stored statistics when the representation drifts.

## TL;DR
EFCIL methods that represent classes as Gaussians (mean + covariance) in feature space quietly assume those Gaussians stay valid while the feature extractor keeps training. AdaGauss shows they don't: covariances go stale task-by-task, and dimensionality collapse during training shrinks old-class ranks, creating a task-recency bias *in the covariances themselves*. The fix: adapt old covariance matrices to the new feature space after each task, plus an anti-collapse loss that keeps feature ranks up.

## The mechanism (how it actually works)
1. **Classes as Gaussians:** per class, store (μ_k, Σ_k); classify by Bayes/Mahalanobis or replay pseudo-features from the Gaussians to train the head — per-class covariance, so anisotropy is first-class (unlike SLDA's tied Σ).
2. **Covariance adaptation:** when the backbone trains on task t+1, learn the feature-space transformation (via an auxiliary projector/distillation pair between old and new extractor) and push each stored Σ_k through it — old Gaussians are *re-expressed in the new space* instead of carried stale.
3. **Anti-collapse loss:** a regularizer that keeps the feature covariance well-ranked during training; without it, new-task training collapses dimensions, old-class Gaussians end up lower-rank than new ones, and Mahalanobis distances systematically favor recent classes (the "strikes back" bias).

## Key results / claims
- State-of-the-art EFCIL results on standard benchmarks, from-scratch *and* from pretrained backbones.
- Demonstrates old-class representations have measurably lower rank than new ones absent the anti-collapse term — the bias is geometric, not just statistical.

## How it relates to us
- **Organ / phase touched:** the namer's metric (P7.2 anisotropy: tied covariance +0.19) + the sleep/re-anchor loop (P9.4 proto-reanchor) + the rotating bulk (P9.0).
- **Same as us:** the core insight is one we bought independently — stored class statistics must be *re-anchored when the representation moves*. Our P9.4 proto-reanchor (sleep re-computes prototypes from the LUT through the current bulk, recovering the transducer residual 0.79→0.99) is the mean-only version of their covariance adaptation.
- **Different from us:** (1) They adapt *covariances*, we re-anchor *means* — our sleep re-fit recomputes statistics from replayed LUT features, while they *transform* stored statistics without any buffer. (2) Their drift source is backbone fine-tuning; ours is SCFF's endogenous rotation. (3) Their anti-collapse loss is a gradient-trained term on the backbone — not available to us (we never write the bulk); the transferable half is the *statistic-side* adaptation.
- **What we could borrow or test:** the anisotropy upgrade path that doesn't fight our P7.2 finding — per-class (or shrunk per-class, RDA-style) covariances stored in the LUT, *re-expressed through the measured bulk rotation at sleep* instead of re-estimated from scratch; and their rank diagnostic (old-class feature rank vs. new) is a cheap new invariant for our P9-style freeze checks — does SCFF rotation collapse old-class rank the way GD fine-tuning does?
- **What contradicts or challenges us:** their premise says statistics-carrying heads (our SLDA fallback especially) degrade under representation drift *even when accuracy looks fine* — a mechanism-level warning that our tied-Σ fallback plus rotating bulk is the exact configuration their bias analysis flags. Worth one bench cell before trusting SLDA on long horizons.

## Follow-on leads
- FeCAM (NeurIPS 2023) — the static per-class-covariance Mahalanobis head (curated; struck by our A6 gate) — AdaGauss is its drift-aware successor.
- SDC (Yu et al., CVPR 2020) — semantic drift compensation: the original "move the prototypes, not the data" paper.
- LDC (Gomez-Villa et al., ECCV 2024) — learnable drift compensation; ADC (Goswami et al., CVPR 2024) — adversarial drift compensation: the growing "statistics under drift" subfield — arguably its own future sweep topic.
