# Unsupervised Concept Drift Detection with a Discriminative Classifier (D3)
- **Authors / Year / Venue:** Ömer Gözüaçık, Alican Büyükçakır, Hamed Bonab, Fazli Can / 2019 / CIKM '19
- **Link:** https://github.com/ogozuacik/d3-discriminative-drift-detector-concept-drift (official code + paper ref; ACM DOI 10.1145/3357384.3358144 — paywalled)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐ — the cheapest classifier-two-sample drift detector: "can a linear model tell old window from new?" — a one-crossbar-read test in our substrate.

## TL;DR
D3 keeps a sliding window with an "old" part (size `w`) and a "new" part (size `ρ·w`), labels them old=1/new=0, trains a logistic regression to discriminate, and reads the **AUC**: near 0.5 means the feature distribution hasn't moved; above threshold `τ` (e.g. 0.7) means new data is separable from old — drift. Label-free, model-agnostic, a few lines; now shipped in the `river` streaming library.

## The mechanism (how it actually works)
A classifier two-sample test in stream form. If `P(X)` is unchanged, no classifier can beat chance at distinguishing "arrived before" from "arrived after," so discriminator AUC hovers at 0.5; distribution movement makes time predictable from features and AUC rises. The sliding window makes it online: on detection, drop the old half, promote the new, continue. Three knobs: `w` (memory), `ρ` (new-fraction), `τ` (sensitivity). The discriminator's weight vector is a free by-product: it is literally the **direction in feature space along which the world moved** — a drift-direction estimate, not just a bit.

## Key results / claims
- On standard stream benchmarks with a downstream adaptive learner, D3 beats popular supervised detectors (DDM/EDDM-style) on final prequential accuracy in most streams, at trivial cost and zero labels.
- Integrated into `river` (community-standard streaming ML), indicating engineering adoption.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate; the trigger bake-off harness (P8.2).
- **Same as us:** operates purely in feature space (our taps); the AUC signal, like our direction statistic, responds to *where* the distribution moved rather than gross magnitude only.
- **Different from us:** D3 fires on **any** separable movement of `P(X)` — it is exactly the class of detector Hinder et al.'s harmless-drift objection targets, and our nuisance covariate shift *is* separable old-vs-new, so vanilla D3 would false-fire on it (our magnitude-null failure, FAR 0.938, in classifier form). Also it trains a discriminator online with GD — light, but not closed-form.
- **What we could borrow or test:** (1) as the **published representative of raw-feature-space detectors** in an extended P8.2 bake-off — the baseline our class-direction trigger must beat on nuisance FAR; (2) the closed-form variant: replace logistic regression with an **LDA discriminator** (two means + shared covariance — machinery our SLDA namer already owns) → old-vs-new Fisher direction and separability in closed form, one crossbar read; (3) the discriminator direction as a *drift-direction* probe: compare it to the namer's class directions — drift along class structure = harmful, fire; orthogonal = nuisance, ignore. That single cosine turns D3 from a harmless-drift victim into a harmful-drift filter.
- **What contradicts or challenges us:** its benchmark wins over DDM remind us that label-latency is DDM's structural weakness — our deployed gate inherits it wherever labels lag the stream.

## Follow-on leads
- Classifier two-sample tests (Lopez-Paz & Oquab 2017) — the theory under D3.
- OCDD (Gözüaçık & Can 2020) — one-class version, no discriminator retraining.
- SUDS (arXiv 2411.02995) — unsupervised drift *sampling*, the buffer-side cousin.
