# FeTrIL: Feature Translation for Exemplar-Free Class-Incremental Learning
- **Authors / Year / Venue:** Grégoire Petit, Adrian Popescu, Hugo Schindler, David Picard, Bertrand Delezoide / 2023 / WACV 2023
- **Link:** https://arxiv.org/abs/2211.13131
- **Tier / Topic:** tier2-component-optimization / t2.6 prototype drift compensation
- **Relevance:** ⭐⭐⭐ — the degenerate-but-instructive corner of the design space: freeze the extractor so drift is zero, then *synthesize* old-class features by translating new ones. The translation trick is a closed-form re-fit-set generator we could use to relieve the LUT cap.

## TL;DR
FeTrIL sidesteps drift compensation entirely: freeze the feature extractor after the first task (no drift ever again), store only one centroid per old class, and regenerate old-class training features on demand by geometric translation — take a real new-class feature and shift it by the difference of centroids. A linear classifier retrained on real-new + pseudo-old features stays balanced across all classes. Fast, simple, and embarrassingly strong against ten heavier baselines.

## The mechanism (how it actually works)
1. **Freeze** the backbone after task 1. Stability is total; plasticity is delegated to the classifier.
2. **Store** per class only the centroid μ_c (a prototype — no covariance, no exemplars).
3. **Pseudo-features by translation:** to make a sample of old class c, pick a real feature f(x) of a similar new class c′ and translate: f̂_c = f(x) + (μ_c − μ_c′). The within-class *spread* of c is borrowed wholesale from c′; only the mean is corrected. (Choice of c′: nearest centroid.)
4. **Re-train a linear classifier** (LinearSVC-style, one cheap solve per increment) on real new features + translated pseudo-old features — every class is represented at every increment, so no task-recency bias.

## Key results / claims
- Outperforms ten mainstream EFCIL methods in most settings on CIFAR-100, TinyImageNet, ImageNet-Subset across increment sizes; much faster, since only a linear component updates.
- The load-bearing (uncomfortable) implication for the drift line: with a decent first-task backbone, *refusing to move the representation* plus mean-corrected borrowed spread beats most methods that carefully track a moving one.

## How it relates to us
- **Organ / phase touched:** sleep re-fit / the hippocampus LUT (cap + CBRS eviction, P9.3); the namer's re-fit set.
- **Same as us:** frozen-representation + cheap-refit-classifier is our architecture's silhouette; "spread is shareable across classes, means are per-class" is also exactly SLDA's tied-covariance bet — FeTrIL is the sampling version of the assumption our deployed namer already makes analytically.
- **Different from us:** their extractor is literally frozen (drift = 0 by construction); our bulk is frozen in *objective* but keeps learning forward-only, so drift is endogenous and translation from stale centroids would inherit the staleness. FeTrIL is the control condition, not a solution, for our problem.
- **What we could borrow or test:** (1) **Cap relief at sleep:** the CBRS cap holds few exemplars per class as classes grow (P9.3: cap must scale with #classes); at re-fit, densify thin classes with translated pseudo-features from feature-rich classes — closed-form, no new storage, one translation per synthetic sample. (2) **Sanity control for the whole t2.6 program:** any drift-compensation cell we run should beat "freeze the taps at birth + FeTrIL translation" to justify tracking drift at all.
- **What contradicts or challenges us:** its strength quietly argues the field's moving-backbone premise (and our drifting bulk) must *earn* its drift — our P11 answer is that the always-learning bulk is what wins real coherent drift (gas arena), but on static arenas FeTrIL's freeze-everything is the cheaper competitor.

## Follow-on leads
- FeCAM (carded t2.4 closed-form-classifier) — same frozen-backbone family, covariance-aware.
- PASS / prototype-augmentation line (Zhu et al., CVPR 2021) — Gaussian-jitter pseudo-features instead of translation.
- EFC (carded here) — explicitly positions itself as the middle ground between FeTrIL's freeze and full fine-tuning.
