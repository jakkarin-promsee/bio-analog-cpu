# Synthesis — closed-form classifier fixes for the tied-covariance / anisotropy ceiling  (Tier 2)
**The question:** For our closed-form namer (deployed SLDA; RanPAC alternative), what closed-form classifier fix most cheaply beats the tied-covariance ceiling on an analog substrate — where per-class covariance is storage-expensive, and shrinkage / fixed geometry are cheap?
**Already in `draft6.0/research/`:** phase7's curated library covers the head families themselves (RanPAC 2307.02251, Deep-SLDA, the ACIL/RLS analytic thread incl. F-OAL, FeCAM as a bake-off entrant, RanDumb); t1.2 of this sweep carded ACIL, DS-AL, GACL, F-OAL, RanDumb, LoRanPAC, AdaGauss, AIR, Deep-SLDA. **This folder is the covariance-quality / classifier-geometry layer on top:** shrinkage estimation theory, the tied↔per-class dial, kernel lifts, and fixed-simplex (ETF) geometry.

## The landscape (the four camps)

**Camp 1 — estimation theory (fix the estimate, keep the model).** Ledoit-Wolf 2004 and Chen et al. 2010 (RBLW/OAS) treat the covariance as a statistical object: in the n-not-≫-p regime the sample covariance's eigen-spectrum is systematically spread, and inverting it (what every Mahalanobis/LDA head does) divides by the least-trustworthy numbers first. The repair is a scalar convex pull toward a scaled identity with a **closed-form, data-driven coefficient** — two trace accumulators and a divide. This camp cannot break the tied *assumption*; it makes whatever covariance you keep honest at low sample counts. It is the precondition for every other camp.

**Camp 2 — the tied↔per-class dial (fix the model, pay per class).** Friedman's 1989 RDA is the exact question of this topic answered 37 years ago: blend each class's covariance toward the pooled one with weight λ (counts inside the formula, so starved classes automatically collapse to tied), then shrink toward identity with γ. Simple CNAPS (CVPR 2020) is the same dial deployed with a **count-based weight λ_c = n_c/(n_c+1)** instead of cross-validation — the streaming-safe version. FeCAM (NeurIPS 2023) is the λ=0 endpoint: full per-class covariance plus shrinkage, correlation normalization, and a Tukey Gaussianizer — the strongest anisotropy machinery in the field (~+6 pts over Euclidean NCM on their bench) and the most storage-expensive (d² resident state per class).

**Camp 3 — the kernel lift (dissolve the ceiling instead of splitting the covariance).** KLDA (AAAI 2025) keeps ONE shared covariance and lifts the features through Random Fourier Features first; in the lifted space, differently-shaped class clouds become close-enough-to-shared-shape that plain tied-covariance LDA claims **joint-training accuracy** on CIL benchmarks. The anisotropy budget is paid in a *fixed random crossbar*, not per-class storage — the same hardware class as RanPAC's projection.

**Camp 4 — fixed geometry (don't estimate the classifier at all).** Yang et al. NeurIPS 2022 fix the classifier as a simplex ETF (maximal equiangular separation, known a priori) and train only features; Neural Collapse Terminus (2023) pre-allocates the ETF over the *whole future label space* for CIL; SCL-PNC (2025) concedes the static simplex misaligns under drift and makes it parametric. The magnitude/recency channel is structurally deleted — but the theory assumes features can *move to* the geometry, which our frozen bulk cannot do; only the *targets-swap* transfers to us.

## How WE differ  ← the money section

Our namer already sits at a specific point in this landscape without having named it: **SLDA = RDA at λ=1 (fully tied) with a fixed ridge instead of a data-driven shrink; RanPAC = camp 3 with a ReLU lift feeding a ridge (not LDA) head.** Our P7.2 finding — the cliff is anisotropy, a tied covariance is the +0.19 lever, no mixture needed — is this literature's opening sentence. Our P7.4 A6 strike on FeCAM is RDA's prediction: the λ=0 endpoint loses when counts are bursty; the failure was per-class covariance *without the dial*, not per-class covariance per se. And the P7↔P8 tension (RanPAC's accuracy vs SLDA's 69× cheaper solve) is exactly camp 3's price: the projection crossbar is where the tied ceiling dissolves, and it is also the expensive part. What is genuinely ours: nobody in this literature prices these fixes in **resident analog state** (capacitor rows, crossbars, precision-held scalars) — the substrate-cost column below does not exist in any of these papers.

## The gap / what we haven't tried — ranked by (anisotropy benefit × substrate fit)

1. **Diagonal-RDA head with a count-aware dial** (Friedman + Simple CNAPS, diagonalized): keep the one running tied Σ; add a per-class *diagonal* variance vector; blend Σ̂_c = (1−λ_c)·diag(σ²_c) + λ_c·Σ_tied with λ_c from class counts (counters already exist for cbrs). **Substrate cost: +d per class** — one extra capacitor row beside each stored mean; no new crossbar. The cheapest *true* tied-bias breaker; burst-starved classes collapse to today's SLDA automatically (the guard A6 demanded). *(Our composition — diagonal-only per-class term under the RDA dial — is a substrate-driven proposal, not a published result.)*
2. **KLDA cell: RanPAC-projection → SLDA-statistics** (the one combination our P7 grid missed — lift then tied-LDA, instead of lift-then-ridge or no-lift-then-LDA). **Substrate cost: the projection crossbar P8 already metered (~69× the SLDA solve) + a D×D shared Gram.** Highest ceiling (joint-training claims in the source paper); zero per-class storage growth; the P8 economy argument is the counterweight and the gate/cadence economics decide.
3. **OAS/LW data-driven shrinkage** replacing our fixed ridge λI in every solve. **Substrate cost: two scalar accumulators + one divide at sleep-time — essentially free.** Improves the +0.19 whitening lever's stability at low samples-per-class; will not beat the tied bias alone, but if it closes much of the FeCAM diagnostic gap, our "ceiling" was partly estimation error — a cheaper story.
4. **ETF-target ridge** (Yang 2022, targets-swap only): regress onto fixed simplex-ETF vertices instead of one-hots in the same Gram algebra; optionally pre-allocate vertices for unseen classes (Terminus) for class-count-growth streams. **Substrate cost: a fixed C×(C−1) target matrix in the LUT — free.** Honest tag: unproven for frozen-feature closed-form heads; SCL-PNC predicts the drift failure mode (stale vertices) — expect small-or-null, cheap to find out.
5. **FeCAM correlation-normalization + Tukey transform on the *tied* pipeline** (the separable pieces of FeCAM, without its per-class storage). **Substrate cost: per-feature scaling at sleep-time — near-free.** Attacks the max-magnitude/variance-scale channel the spine hates.
6. **FeCAM full per-class as the offline diagnostic ceiling** (never deploy): measure exactly what the tied assumption costs on our taps so levers 1–5 have a target. **Substrate cost: none (offline, software-only); as deployment it stays struck — d² per class + the A6 recency dent.**

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [FeCAM (Goswami 2023)](goswami-2023-fecam.md) | ⭐⭐⭐⭐⭐ | The per-class pole: ~+6 pts of anisotropy headroom on paper, d²/class + our own A6 strike as its price — the diagnostic ceiling. |
| [RDA (Friedman 1989)](friedman-1989-rda.md) | ⭐⭐⭐⭐⭐ | The tied↔per-class dial with counts inside the formula — our exact question, answered in 1989. |
| [KLDA (Momeni 2025)](momeni-2025-klda.md) | ⭐⭐⭐⭐⭐ | Keep ONE covariance, lift the features — the ceiling escape that pays in a crossbar, not per-class storage. |
| [Ledoit-Wolf 2004](ledoit-wolf-2004-shrinkage.md) | ⭐⭐⭐⭐ | The free, data-driven shrinkage coefficient; the precondition for every covariance we hold. |
| [OAS/RBLW (Chen 2010)](chen-2010-oas-shrinkage.md) | ⭐⭐⭐⭐ | The Gaussian-specialized shrinkage that dominates at n ≪ p — our per-class corner. |
| [Simple CNAPS (Bateni 2020)](bateni-2020-simple-cnaps.md) | ⭐⭐⭐⭐ | λ_c = n_c/(n_c+1): the count-based blend rule that makes the RDA dial streaming-deployable. |
| [Fixed ETF (Yang 2022)](yang-2022-etf-fixed-classifier.md) | ⭐⭐⭐⭐ | The no-fit geometry: delete the learned-magnitude channel by fixing the classifier as a simplex. |
| [NC Terminus (Yang 2023)](yang-2023-neural-collapse-terminus.md) | ⭐⭐⭐ | Pre-allocate the whole label space's geometry — the class-count-growth insurance. |
| [SCL-PNC (Zhang 2025)](zhang-2025-scl-pnc.md) | ⭐⭐ | The boundary marker: even the geometry camp concedes static ETF misaligns under drift. |

## Leads spawned
- **Nonlinear (eigenvalue-wise) shrinkage** (Ledoit-Wolf's later work) — if scalar shrinkage saturates.
- **Robust scatter (regularized Tyler)** — heavy-tailed real streams where the Gaussian core breaks (connects to the P11 autocorrelated-stream floor).
- **Random Fourier Features theory** (Rahimi–Recht line) — lift-width vs kernel-approximation quality, to price the KLDA cell honestly.
- **Momeni et al. 2502.12388** ("Achieving Upper Bound Accuracy of Joint Training in CL") — the KLDA follow-up claim, worth its own verification pass.
- **Procrustes-style closed-form vertex re-anchoring** — if ETF targets ever ship, the sleep-time repair for drift-stale vertices.
