# Information-theoretic Online Memory Selection for Continual Learning (InfoRS)
- **Authors / Year / Venue:** Shengyang Sun, Daniele Calandriello, Huiyi Hu, Ang Li, Michalis Titsias / 2022 / ICLR 2022
- **Link:** https://arxiv.org/abs/2204.04763 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule
- **Relevance:** ⭐⭐⭐⭐⭐ — an eviction criterion (**surprise + learnability**) computable **closed-form** via Bayesian rank-one updates — the one selection mechanism in this batch that is both gradient-free *and* directly reuses signals our namer already produces (predictive uncertainty / error).

## TL;DR
Keep the samples that carry the most **information**, not a uniform random draw. Score each candidate by **surprise** (how unexpected it is under the current model) and **learnability** (is it learnable signal, not an outlier); a Bayesian model computes both cheaply via rank-one matrix updates. InfoRS is a stochastic reservoir that samples preferentially among high-information points — and is far more robust to class imbalance than plain reservoir.

## The mechanism (how it actually works)
Model the predictor as a Bayesian (last-layer) Gaussian; for a candidate point compute the **information gain** it would give — high when the point is **surprising** (far from what the model predicts) but gated by **learnability** so pure outliers/noise are rejected. Both quantities reduce to **rank-one updates** of a running covariance/precision, so scoring is closed-form and O(d²) with no backprop. Then, instead of reservoir's blind uniform admission, **InfoRS** admits a point stochastically with probability tied to its information — and the paper stresses that ***when* you update memory** (the timing) is itself a lever. Robustness to imbalance comes free: minority-class points are usually the surprising ones.

## Key results / claims
Beats reservoir sampling and is markedly more robust under **imbalanced** streams on task-free CL benchmarks; the surprise+learnability pair outperforms surprise-alone (which chases outliers). Establishes that information-weighted admission + admission-timing both matter.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** bounded-LUT eviction (P9.3 CBRS), the error-EMA drift gate (P8), the C=20 retention crossover (P11), sleep timing.
- **Same as us:** two deep alignments. (1) The Bayesian last-layer that computes "surprise" is **exactly the shape of our closed-form namer** (SLDA/RanPAC = a Gaussian/ridge head with a running precision) — the information score is a byproduct of machinery we already run. (2) InfoRS's "surprise" ≈ **namer prediction error / Mahalanobis distance**, which is *literally the signal our DDM drift gate already consumes* (error-EMA). We compute surprise every step and throw it away after gating.
- **Different from us:** InfoRS uses information to decide **admission**; we use error only to decide **when to fire the namer**. We have never fed the same signal into **eviction** — CBRS evicts by class-count only, blind to within-class informativeness.
- **What we could borrow or test:** **information-weighted eviction that reuses the gate's error/leverage signal** — within each CBRS class slot, evict the *least* surprising (most redundant) samples and keep the informative ones, computed closed-form from the namer's own precision. No gradients, no raw-data-gradient, no extra passes: a bounded store + closed-form re-fit, unchanged. This is the top substrate-native lever against the P11 C=20 crossover (hold more effective history per slot).
- **What contradicts or challenges us:** it implies uniform-within-class retention (our CBRS) is information-blind and leaves capacity unused at tight caps — consistent with GCR/OCS, three independent papers pointing at the same gap.

## Follow-on leads
- Information-Theoretic Dual Memory System (arXiv 2501.07382) — the same criteria in a fast/slow buffer (⚠ dual-memory *architecture* = t1.4 scope; cite the *criterion*, not the architecture).
- Bayesian last-layer predictive variance as the closed-form surprise estimator for SLDA/RanPAC.
