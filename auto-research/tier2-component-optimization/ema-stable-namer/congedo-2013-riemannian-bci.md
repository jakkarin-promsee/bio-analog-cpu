# A New Generation of Brain-Computer Interface Based on Riemannian Geometry
- **Authors / Year / Venue:** M. Congedo, A. Barachant, A. Andreev / 2013 / arXiv:1310.8115 (later: Congedo, Barachant, Bhatia — "primer & review," Brain-Computer Interfaces 4(3), 2017)
- **Link:** https://arxiv.org/abs/1310.8115 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐⭐☆ — a *classifier* built entirely on the **geometric mean of covariance matrices**: the working precedent that averaging SPD statistics on the manifold makes a robust, drift-tolerant prototype namer.

## TL;DR
Represent each trial as its **covariance matrix**, treat those as points on the SPD manifold, and classify by **minimum distance to the Riemannian (geometric) mean** of each class (MDM). The geometric-mean prototypes give a simple, robust classifier with strong cross-session/cross-subject transfer and little training data.

## The mechanism (how it actually works)
No feature extraction — the covariance *is* the feature. Each class prototype is the **Riemannian geometric mean** (Fréchet mean under the affine-invariant metric) of its training covariances, computed by an iterative Karcher-mean procedure. A new trial's covariance is labeled by whichever class-mean it's geodesically closest to. Because the geometry is affine-invariant, the classifier is naturally robust to linear distortions of the signal (electrode gain, session shift) — the transfer-learning win. Class means can be updated online as new covariances arrive: a *running geometric mean* — i.e. a manifold EMA of second-order statistics.

## Key results / claims
- MDM on geometric-mean prototypes → competitive/winning BCI decoding (five international competition wins for the framework family).
- Strong across-session / across-subject generalization; learns from little data.
- "Simple, both algorithmically and computationally" → viable for online decoders.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer (a covariance/prototype head); the drift-robust anchor.
- **Same as us:** this is a **closed-form, prototype, no-gradient namer whose prototypes are averaged second-order statistics** — structurally the same family as SLDA/RanPAC, and it shows the *geometric* mean of covariances is a battle-tested, drift-robust prototype. It is external, non-biology-native evidence that averaging covariance statistics as a class anchor *works* and *transfers*.
- **Different from us:** BCI uses the **full per-class covariance as the token**; our namer uses feature means + a **tied** covariance (SLDA) or a Gram (RanPAC). And BCI's mean is the **Riemannian** geometric mean — the swelling-free one (see arsigny-2006) — not the arithmetic EMA our proposal starts with.
- **What we could borrow or test:** if a stable-namer's arithmetic covariance EMA underperforms, the **MDM-with-geometric-mean** construction is the principled upgrade and a ready-made baseline; the affine-invariance is exactly the "robust to the bulk's linear rotation" property P9.0 says we need.
- **What contradicts or challenges us:** it argues the *right* average of covariances is the **geometric** one — reinforcing that our cheap arithmetic EMA is the approximation, not the ideal. Counter-point: geometric-mean iteration and geodesic distance are **not** substrate-native (matrix logm/inv), so the arithmetic EMA remains the deployable form and geometric is the sleep-time / diagnostic ceiling.

## Follow-on leads
- Congedo/Barachant/Bhatia 2017 "primer & review" (the fuller treatment). pyRiemann (reference implementation). Riemannian online/adaptive MDM under session drift. Tangent-space (log-Euclidean) mapping → a *flat* classifier over log-covariances (bridges to arsigny-2006).
