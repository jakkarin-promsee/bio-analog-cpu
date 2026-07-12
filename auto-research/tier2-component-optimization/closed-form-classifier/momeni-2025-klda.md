# KLDA: Continual Learning Using a Kernel-Based Method Over Foundation Models
- **Authors / Year / Venue:** Saleh Momeni, Sahisnu Mazumder, Bing Liu / 2024 arXiv, AAAI 2025
- **Link:** https://arxiv.org/abs/2412.15571 (fetched; AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/34150; code: https://github.com/salehmomeni/klda)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐⭐⭐ — the *cheap escape route* from the tied-covariance ceiling: don't split the covariance per class, **lift the features and keep the one shared covariance** — and it claims joint-training accuracy.

## TL;DR
KLDA is SLDA with one move added in front: map the frozen features through **Random Fourier Features** (a fixed random projection + cosine nonlinearity approximating an RBF kernel), then run plain LDA in the lifted space — per-class means plus **one shared covariance**, updated incrementally, classified in closed form. On text and image CIL benchmarks it reports accuracy **comparable to joint training of all classes** — the CIL upper bound — with no replay and no gradient.

## The mechanism (how it actually works)
The story: the tied-covariance ceiling is a statement about *linear* geometry — one shared ellipsoid can't whiten differently-shaped class clouds. But a kernel changes what "shape" means: in a sufficiently rich lifted space, class distributions that are anisotropic and non-Gaussian in the original space become far closer to shared-shape Gaussians, so a *tied* covariance stops being the binding constraint. KLDA buys that lift for the price of a **fixed random matrix**:

1. **RFF lift:** z(x) = √(2/D)·cos(Wx + b) with W, b drawn once from the RBF kernel's spectral distribution and frozen. (Classic Rahimi–Recht random features; D is the lift width.)
2. **Streaming Gaussian statistics in the lifted space:** per-class means μ_c and ONE shared covariance Σ accumulated across all classes/tasks — exactly the SLDA update, just above the lift.
3. **Closed-form LDA decision rule** on (μ_c, Σ). New task ⇒ compute the new class means, update Σ, done. No backward pass exists anywhere in the system.

The head-level forgetting is zero by the same algebra as SLDA/ACIL: the statistics are order-independent sums.

## Key results / claims
- **Accuracy comparable to joint training** (the CIL upper bound) across text and image benchmarks — without replay data. The joint-bound claim is the paper's headline and is unusually strong for the analytic-CL family.
- Addresses both catastrophic forgetting and inter-task class separation via the fixed lift + shared statistics.
- Same authors extended the claim in "Achieving Upper Bound Accuracy of Joint Training in Continual Learning" (arXiv 2502.12388).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer — the direct SLDA replacement; also re-frames the P7 RanPAC result.
- **Same as us:** frozen bulk + fixed random projection + streaming closed-form Gaussian head — this is *literally our component list* (RanPAC's random ReLU projection + SLDA's tied-covariance statistics), assembled in the one combination we didn't test: **projection feeding the LDA head instead of the ridge head**.
- **Different from us:** cosine features from an RBF spectral draw, not ReLU; LDA rule, not ridge regression onto one-hots; foundation-model features (their bulk is a big pretrained transformer — the usual scope caveat, our bulk is small and self-trained).
- **What we could borrow or test:** the **one-cell experiment our P7 grid missed** — RanPAC-projection → SLDA-statistics (tied covariance in the lifted space). Substrate cost: the projection crossbar we already priced in P8 (RanPAC's projection metered ~69× SLDA's solve) + a D×D shared Gram instead of 768². Not free — but it buys the anisotropy fix with **zero per-class storage growth**, and P8's meter already told us the price.
- **What contradicts or challenges us:** P8 deployed SLDA *because* the projection was the expensive part — KLDA says the projection is exactly where the tied ceiling dissolves. If KLDA-on-our-taps closes the FeCAM diagnostic gap, the economy argument (P8) and the accuracy argument (P7.2) land on opposite sides of the same crossbar, and the gate/cadence economics decide.

## Follow-on leads
- Rahimi & Recht 2007, Random Features for Large-Scale Kernel Machines — the RFF anchor.
- Momeni et al. 2025, arXiv 2502.12388 — the joint-accuracy follow-up.
- LoRanPAC (already carded, t1.2) — the other "fix the projection algebra" branch.
