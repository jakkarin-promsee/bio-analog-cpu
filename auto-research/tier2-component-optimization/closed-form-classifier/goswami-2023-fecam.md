# FeCAM: Exploiting the Heterogeneity of Class Distributions in Exemplar-Free Continual Learning
- **Authors / Year / Venue:** Dipam Goswami, Yuyang Liu, Bartłomiej Twardowski, Joost van de Weijer / 2023 / NeurIPS 2023
- **Link:** https://arxiv.org/abs/2309.14062 (fetched; code: https://github.com/dipamgoswami/FeCAM)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐⭐⭐ — the *per-class-covariance pole* of our anisotropy question; it was in our P7 bake-off and **struck at the A6 gate**, so this card is the honest full read of what we struck.

## TL;DR
FeCAM replaces the Euclidean prototype distance (NCM) with a **per-class anisotropic Mahalanobis distance** — one covariance matrix per class, estimated once from that class's features on a frozen backbone, never updated by gradient. To make per-class covariances estimable from few samples it stacks three closed-form repairs: covariance **shrinkage**, **correlation normalization** (equalizing variance scale across classes), and a **Tukey power transform** on features to make them more Gaussian.

## The mechanism (how it actually works)
The story: on a frozen extractor, classes are *differently shaped* clouds — some elongated, some round, differently scaled. A tied covariance (SLDA) whitens all of them with one shared shape and under-fits exactly where shapes disagree. FeCAM's move is to model each class as its own Gaussian:

1. **Per-class covariance.** For class c, compute Σ_c from that class's training features (once, at the task it appears in; the backbone is frozen so Σ_c never goes stale from feature drift — only from never being revisited).
2. **Shrinkage** (their α₁, α₂ hyperparameters): inflate the diagonal and damp off-diagonals toward their means, so a few-sample Σ_c is invertible and well-conditioned — the same trick as Ledoit-Wolf, applied per class with fixed knobs.
3. **Correlation normalization:** rescale Σ_c by its own diagonal (turn it correlation-like) so *all* classes end up with comparable variance scale — otherwise the class with the biggest raw variance eats the argmax. This is the anti-"max-magnitude" repair.
4. **Tukey's ladder-of-powers** on features (x → x^λ, λ≈0.5) to reduce skew, because a Gaussian model is being asserted.
5. Classify by smallest squared Mahalanobis distance (x−μ_c)ᵀ Σ̂_c⁻¹ (x−μ_c). No gradient anywhere; inversions are done once per class.

## Key results / claims
- On their CIL benchmarks the per-class covariance term is the lever: our curated audit (`draft6.0/research/papers/phase7/analytic-and-covariance-readouts.md`) banks **70.9% (per-class) vs 64.8% (Euclidean NCM)** — the anisotropic metric is worth ~+6 pts over the isotropic prototype.
- Generalizes across many-shot, few-shot, and domain-incremental settings, all without touching the backbone.
- The abstract's own framing: Euclidean is fine for *jointly trained* features, suboptimal for features learned from non-stationary data — i.e., **anisotropy is a symptom of the continual regime**, which is exactly our home.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer (P7 bake-off; the P7.2 anisotropy finding; the P7.4 A6 strike).
- **Same as us:** frozen representation + no-gradient Gaussian head; the diagnosis (tied covariance under-fits heterogeneous class shapes) is *literally our P7.2 finding* — "the cliff is anisotropy, not multimodality."
- **Different from us:** pays **d² storage per class** (768² ≈ 590k values/class — on our substrate, a whole crossbar of resident state per class) where SLDA pays d²

 *total*. And our P7.4 gate **struck FeCAM for a recency dent** — per-class covariances estimated from a bursty stream inherit the burst.
- **What we could borrow or test:** (a) **correlation normalization on our *tied* covariance** — the variance-scale equalization is separable from the per-class storage and attacks the max-magnitude bias our spine hates; (b) the **Tukey transform** as a zero-storage Gaussianizer before the SLDA solve; (c) FeCAM run *offline* as the **diagnostic ceiling** — measure exactly how many points the tied assumption costs us, so cheaper fixes have a target to recover.
- **What contradicts or challenges us:** its headline says per-class covariance is worth +6 pts — if that transfers to our taps, our tied ceiling is leaving real accuracy on the table; but our own A6 result says the *streaming* estimate of it is unsafe. The tension is the topic's whole question.

## Follow-on leads
- FeTrIL (the translated-prototype baseline FeCAM beats) — the covariance-free contrast.
- AdaGauss (already carded, t1.2) — the "adapt the Gaussians" answer to stale Σ_c.
- Shrinkage estimators with *data-driven* coefficients (Ledoit-Wolf / OAS, this folder) — replacing FeCAM's fixed α₁, α₂.
