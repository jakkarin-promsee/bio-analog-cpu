# Online Drift Detection with Maximum Concept Discrepancy (MCD-DD)
- **Authors / Year / Venue:** Ke Wan, Yi Liang, Susik Yoon / 2024 / KDD '24 (arXiv 2407.05375)
- **Link:** https://arxiv.org/abs/2407.05375 (ACM: https://dl.acm.org/doi/10.1145/3637528.3672016)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐ — the field's newest label-free detector works by building a **contrastive embedding** first; our SCFF bulk *is* one already, so we get their expensive step for free.

## TL;DR
MCD-DD detects drift label-free by learning **concept embeddings with contrastive learning** (positive pairs = sub-windows close in time, negatives = temporally distant sub-windows) and monitoring **maximum concept discrepancy** — an MMD-inspired distance between concept embeddings of adjacent windows. Adaptively catches diverse drift forms in high-dimensional streams; beats existing baselines with explainable drift analysis.

## The mechanism (how it actually works)
MMD asks "are these two windows from the same distribution?" using a fixed kernel. MCD-DD replaces the fixed kernel with a **learned embedding trained contrastively on time itself**: samples from the same temporal context are pulled together, distant sub-windows pushed apart. If the stream is stationary, temporal contrast finds nothing to separate and window embeddings collide; under drift, "when" becomes predictable from "what," and adjacent-window embeddings separate. The running discrepancy between summary embeddings of adjacent windows is the drift statistic — thresholded for detection, and its size/direction supports qualitative analysis (which concepts moved). Continual light re-training keeps the embedding current.

## Key results / claims
- Outperforms classic two-window and unsupervised baselines on synthetic + real high-dimensional streams, notably on gradual/recurring drift where fixed-kernel MMD blurs.
- Label-free and distribution-assumption-free; supports explainability via the embedding geometry.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the SCFF bulk (as the embedding) + the awake gate.
- **Same as us:** validates the architecture-level claim that a **contrastive representation is the right space for label-free drift detection** — our tap-drift trigger measures drift in an InfoNCE-trained embedding, which is structurally what MCD-DD builds from scratch.
- **Different from us:** they train a dedicated embedding *for the detector* online (a second learner, GD, temporal-contrastive) — substrate-expensive and redundant for us. Our bulk is trained by input-contrast rather than time-contrast, so it is *stable under stationarity* by construction — arguably the property MCD-DD's temporal contrast tries to induce.
- **What we could borrow or test:** (1) the **discrepancy-between-window-summaries statistic**: mean-tap-vector per window, distance between adjacent windows (a two-window MMD-lite over the taps) as a *class-agnostic* companion to our class-direction statistic — catches new/unseen-class drift the class projection is blind to; (2) their gradual-drift evaluation protocol (adjacent-window overlap) for the P8.2 harness.
- **What contradicts or challenges us:** their results imply fixed statistics miss drift forms a learned detector catches — if true at our scale, a *frozen* class-direction basis (between sleeps) could be blind to novel-class drift. Cheap patch: monitor the global window discrepancy alongside the class projection.

## Follow-on leads
- MMD-based two-sample tests on embeddings (kernel choice = the analog cost knob).
- Temporal-contrastive representation learning for streams (TS2Vec family).
- New-class / open-world drift detection (drift the class-direction projection cannot see).
