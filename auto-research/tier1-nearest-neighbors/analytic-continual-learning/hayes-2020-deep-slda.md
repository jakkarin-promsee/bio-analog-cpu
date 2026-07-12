# Lifelong Machine Learning with Deep Streaming Linear Discriminant Analysis
- **Authors / Year / Venue:** Tyler L. Hayes, Christopher Kanan / 2020 / CVPR-W (CLVision workshop)
- **Link:** https://arxiv.org/abs/1909.01520
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the source of our *deployed* head: SLDA is the P8-committed namer (69× metered cheaper than RanPAC).

## TL;DR
Deep SLDA freezes a deep feature extractor and learns only running class means + one shared (tied) covariance matrix, updated one sample at a time. Classification is the LDA discriminant. It matches or beats far heavier incremental learners on ImageNet-scale streaming at a tiny fraction of the compute — the seminal "streaming closed-form head on frozen features" paper.

## The mechanism (how it actually works)
Pure streaming statistics — no gradient anywhere:

1. **Frozen backbone** produces feature vectors f.
2. **Per class k:** a running mean μ_k (one vector each).
3. **Shared across classes:** one running covariance Σ (tied — this is the load-bearing assumption), updated online with a shrinkage term.
4. **Predict:** the LDA rule — argmax_k of `μ_kᵀ Λ f + b_k` with `Λ = (Σ + εI)⁻¹` (precision matrix). Inference is a single linear map; the "training" per sample is two running-average updates.

Because samples update statistics rather than weights, it learns from a *single pass* over a non-iid stream and can be evaluated at any instant (no batch boundary).

## Key results / claims
- On streaming ImageNet ILSVRC-2012 and CORe50 (temporally correlated video), outperforms incremental batch learners and prior streaming methods.
- Orders of magnitude cheaper in compute/memory than replay-based deep CIL of its era.
- The tied covariance is both the trick (statistical strength shared across classes; only one d×d matrix) and the ceiling (anisotropy per class is invisible to it).

## How it relates to us
- **Organ / phase touched:** the namer — SLDA is literally our deployed fallback (P8: metered 69× cheaper than RanPAC, AA ties live); the hippocampus-LUT sleep re-fit re-estimates exactly these statistics.
- **Same as us:** frozen representation + streaming closed-form statistics + single-pass non-iid robustness — our deployment story is Hayes-SLDA with a different feature machine underneath.
- **Different from us:** (1) SLDA updates on *every* sample; ours fires only when the drift gate trips, and P8 showed always-firing *costs* retention (−0.137). (2) Their Σ is estimated once-and-carried; our sleep loop re-fits from the bounded LUT, letting the statistics track a rotating bulk. (3) Their backbone is ImageNet-supervised; ours is task-trained unsupervised SCFF.
- **What we could borrow or test:** their shrinkage schedule for the streaming covariance is a cheap robustness knob we never swept.
- **What contradicts or challenges us:** nothing structural — but our own P7 found SLDA's known weakness (norm-sensitivity, spine-flip 0.89; tied covariance underfits anisotropic class shapes, the +0.19 tied-covariance lever in P7.2 is the same axis). The successor Deep-SRDA (arXiv 2309.08353, already in the curated library) and per-class-covariance methods (FeCAM, AdaGauss) are the field's answers.

## Follow-on leads
- Deep Streaming RDA (2309.08353) — regularized discriminant analysis: the tied↔per-class covariance interpolation knob, closed-form. The most direct "beats plain SLDA on anisotropy" candidate.
- Hayes' REMIND (ECCV 2020) — streaming replay via compressed features; the buffer-side sibling.
- FeCAM (NeurIPS 2023) — per-class covariance Mahalanobis prototype (curated library already covers it; struck by our A6 gate in P7.4).
