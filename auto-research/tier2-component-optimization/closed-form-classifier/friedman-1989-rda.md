# Regularized Discriminant Analysis
- **Authors / Year / Venue:** Jerome H. Friedman / 1989 / Journal of the American Statistical Association 84(405), 165–175
- **Link:** https://www.tandfonline.com/doi/abs/10.1080/01621459.1989.10478752 (DOI page is paywalled/403; citation verified via https://parsnip.tidymodels.org/reference/discrim_regularized.html and the reachable author-hosted PDF https://hastie.su.domains/Papers/RDA-6.pdf)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐⭐⭐ — the 37-year-old exact answer to our exact question: a **single closed-form dial between tied (LDA) and per-class (QDA) covariance**, built for the few-samples-per-class regime.

## TL;DR
LDA (one tied covariance) is too rigid when class shapes differ; QDA (per-class covariance) is too hungry when samples per class are few. RDA puts a knob between them: shrink each class covariance toward the pooled one by λ, then shrink the result toward a scaled identity by γ. λ=1 recovers LDA, λ=0 recovers QDA; everything in between is a *partially* per-class Gaussian classifier, still fully closed-form.

## The mechanism (how it actually works)
Two nested convex blends:

1. **The tied↔per-class dial (λ):** Σ̂_c(λ) = [(1−λ)·n_c·Σ_c + λ·n·Σ_pooled] / [(1−λ)·n_c + λ·n]. Note the sample counts inside the blend — a class with few samples is *automatically* pulled harder toward the pooled estimate. This is the statistically honest version of "per-class covariance where we can afford it, tied where we can't."
2. **The identity shrink (γ):** Σ̂_c(λ,γ) = (1−γ)·Σ̂_c(λ) + γ·(tr Σ̂_c(λ)/p)·I — Ledoit-Wolf-shaped conditioning, fifteen years early, with γ picked by validation rather than a plug-in formula.
3. (λ, γ) are chosen by minimizing an estimate of misclassification risk (cross-validation in the paper; a plug-in or count-based rule works in streaming settings — see Simple CNAPS in this folder for exactly that).

The classifier itself stays the Gaussian discriminant rule with Σ̂_c(λ,γ) — a Mahalanobis head with tunable class-specificity.

## Key results / claims
- On small-sample, high-dimensional simulated and real problems, intermediate (λ, γ) reliably beats both endpoints (pure LDA and pure QDA) — the interpolation is not a compromise, it *wins*.
- The framework is the origin of the modern default that "regularized covariance" means a two-knob family: toward-pooled and toward-identity.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer — the direct upgrade path for the deployed SLDA head (which is exactly RDA at λ=1, γ≈fixed-ridge).
- **Same as us:** closed-form Gaussian head, small-samples-per-class pressure, explicit refusal to fit what the data can't support.
- **Different from us:** RDA at λ<1 stores a **per-class Σ_c (d²/class)** before blending — on our substrate that's the FeCAM storage wall again. But the *dial* doesn't require the *full matrix*: the blend is equally well-defined with a **diagonal per-class term**, Σ̂_c = (1−λ)·diag(σ²_c) + λ·Σ_pooled, which stores only **+d per class** (same order as the class mean we already keep).
- **What we could borrow or test:** the **diagonal-RDA head** — keep our one running tied Σ, add a d-vector of per-class variances (a second capacitor row per class), blend with a count-aware λ_c (n_c/(n_c+k), no cross-validation). This is the cheapest *true* tied-ceiling breaker in this folder: it models per-class scale/axis-aligned shape difference at prototype-level storage cost. Test against the FeCAM diagnostic ceiling: how much of the per-class gap does diagonal-only recover?
- **What contradicts or challenges us:** RDA's λ-inside-counts formula quietly says our A6 strike on FeCAM was predictable — un-blended per-class covariance from bursty counts is the λ=0 endpoint, which RDA's own experiments show losing. The failure wasn't per-class covariance per se; it was per-class covariance *without the dial*.

## Follow-on leads
- Hastie et al., Elements of Statistical Learning ch. 4 — the standard modern treatment of the RDA family.
- High-Dimensional RDA variants (2016+) — plug-in (λ, γ) selection without CV.
- Simple CNAPS (this folder) — the count-based blend deployed inside a deep few-shot head.
