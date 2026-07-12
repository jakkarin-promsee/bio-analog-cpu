# Log-Euclidean Metrics for Fast and Simple Calculus on Diffusion Tensors
- **Authors / Year / Venue:** V. Arsigny, P. Fillard, X. Pennec, N. Ayache / 2006 / Magnetic Resonance in Medicine 56(2) (conf. version MICCAI 2005)
- **Link:** https://pubmed.ncbi.nlm.nih.gov/16788917/ (fetched) · PDF: https://www-sop.inria.fr/asclepios/Publications/Arsigny/arsigny_mrm_2006.pdf
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐⭐⭐ — **the soundness verdict for averaging covariances.** Names precisely why an *arithmetic* EMA of covariance matrices is flawed (the swelling effect) and gives the cheap principled fix.

## TL;DR
The arithmetic (Euclidean) mean of symmetric-positive-definite matrices has a real defect: the **swelling effect** — the determinant of the average can be **larger than the determinant of any input**, artificially inflating "volume"/variance. Affine-invariant Riemannian metrics fix this but are slow. **Log-Euclidean** metrics — do ordinary Euclidean averaging on the **matrix logarithms**, then exponentiate back — remove swelling with the same theoretical guarantees at near-Euclidean cost.

## The mechanism (how it actually works)
An SPD matrix (a covariance, a diffusion tensor) lives on a curved cone, not a flat space. Average two of them arithmetically and you can get a result "puffier" than both — determinant swells — because the straight line between them bulges outside the natural geometry. The affine-invariant geometric mean walks the *geodesic* instead and avoids this, but needs matrix square-roots/inverses per step. Log-Euclidean's trick: map every SPD matrix through `log()` (matrix logarithm) into a flat vector space where symmetric matrices behave Euclideanly, average *there* (cheap), then map back with `exp()`. The mean is `exp(mean(log(Σ_i)))` — no swelling, determinants behave monotonically, and it's a closed-form geometric mean.

## Key results / claims
- Arithmetic mean of tensors → **swelling** (determinant of mean > determinants of inputs); a documented artifact in DT-MRI interpolation/regularization.
- Log-Euclidean mean removes swelling, matches affine-invariant results in practice, at a fraction of the cost.
- The Log-Euclidean mean of `{Σ_i}` is `exp(Σ w_i log Σ_i)` — a *weighted* geometric mean (weights → an EMA).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer — specifically the **SLDA tied covariance** and the **RanPAC Gram** if we EMA them.
- **Same as us:** answers the topic's exact soundness question. A convex combination of SPD matrices *stays* SPD (the cone is convex) — so `Σ_stable ← α·Σ_stable + (1−α)·Σ_fast` is **always a valid covariance** (never breaks the head). Good. **But** it is the *arithmetic* mean, which **swells**: the implied Gaussian/LDA gets an over-inflated covariance → softened, less discriminative Mahalanobis boundaries. So the naive EMA is *valid but statistically biased*, not neutral.
- **Different from us:** DT-MRI, not classification — but the geometry is identical (covariances are SPD). The fix ports directly: EMA in the **log-domain** (`log Σ`) for a swelling-free stable covariance.
- **What we could borrow or test:** two-tier plan — (1) build the **arithmetic** Gram/cov EMA first (Scap-native, one register), (2) if the implied classifier degrades (boundaries too soft, worst-BWT no better), switch the covariance channel to a **log-Euclidean EMA**. Cost of the fix: one `logm`/`expm` per sleep — feasible at sleep frequency, **not** substrate-native per-step.
- **What contradicts or challenges us:** the mean **vector** channel (SLDA class means) is an ordinary Euclidean quantity → arithmetic EMA is exactly right there. The **Gram** (uncentered 2nd moment) is SPD → subject to swelling like the covariance. So the soundness answer *splits by channel*: mean-EMA = clean; covariance/Gram-EMA = valid-but-swells → prefer log-Euclidean if it matters.

## Follow-on leads
- Congedo 2013 (the geometric mean as a *class prototype* in an MDM classifier). Affine-invariant metric (Pennec 2006). Karcher/Fréchet mean iteration. Whether swelling actually harms an *LDA decision boundary* (vs a generative density) — a small numeric check we can run.
