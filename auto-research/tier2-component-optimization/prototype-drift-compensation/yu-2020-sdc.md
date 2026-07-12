# Semantic Drift Compensation for Class-Incremental Learning (SDC)
- **Authors / Year / Venue:** Lu Yu, Bartłomiej Twardowski, Xialei Liu, Luis Herranz, Kai Wang, Yongmei Cheng, Shangling Jui, Joost van de Weijer / 2020 / CVPR 2020
- **Link:** https://arxiv.org/abs/2004.00440 (code: https://github.com/yulu0724/SDC-IL)
- **Tier / Topic:** tier2-component-optimization / t2.6 prototype drift compensation
- **Relevance:** ⭐⭐⭐⭐⭐ — the seminal closed-form answer to our exact between-sleeps failure: estimate how *absent* classes' prototypes moved from how *present* data moved. Directly targets the P10 REV-staircase stale-namer sag, at near-zero cost.

## TL;DR
When a feature extractor keeps training across tasks, stored old-class prototypes (NCM means) go stale — they point at where classes *used* to live. SDC's move: you cannot re-measure old classes (no exemplars), but you CAN measure exactly how current-task data drifted between the old and new extractor — so transfer that measured drift field to the old prototypes, weighted by proximity. Exemplar-free, closed-form, no training.

## The mechanism (how it actually works)
The setting is an embedding network (metric loss) + nearest-class-mean (NCM) classification: each class is a stored prototype μ_c in feature space. Train on task t and the extractor moves from f_{t−1} to f_t; old prototypes were computed under f_{t−1} and are now expressed in a dead coordinate frame.

1. **Measure the drift you can see.** For every current-task sample x_i (which you have in hand during the task-t training window), compute the displacement vector δ_i = f_t(x_i) − f_{t−1}(x_i). This is a *sampled vector field* of the representation's motion — measured only where current data lives.
2. **Transfer it to where you can't see.** Update each old prototype by a kernel-weighted average of nearby displacements: w_i(c) ∝ exp(−‖f_{t−1}(x_i) − μ_c‖² / 2σ²), then μ_c ← μ_c + Σᵢ w_i(c) δ_i / Σᵢ w_i(c). Old classes near current data get a confident correction; far ones get little (honest: no evidence, no move).
3. Classify with the compensated prototypes. No stored exemplars, no learned modules, no backward pass through anything — one weighted average.

The tacit assumption: the drift field is *smooth* — nearby regions of feature space move similarly, so displacement measured on new data extrapolates to old prototypes. (Successors — LDC, ADC — attack exactly this assumption.)

## Key results / claims
- Embedding networks forget much less than softmax classifier networks to begin with (the paper's second finding — representation forgetting ≪ classifier forgetting, same split Davari 2022 later measured and our P9.0 confirmed for SCFF).
- With SDC, outperforms exemplar-free baselines and is competitive with exemplar-storing methods on CIFAR-100, ImageNet-Subset, and fine-grained sets (CUB, Flowers, Caltech).
- Holds where drift is moderate and the smoothness assumption is decent; degrades when the new task is far from old classes in feature space (weights vanish → prototypes stay stale).

## How it relates to us
- **Organ / phase touched:** the sleep re-fit / stored prototypes (P9.4 proto-reanchor) + the P10 REV-staircase "namer frame goes stale between sleeps" failure + sleep cadence (grid-4, P9.5).
- **Same as us:** identical diagnosis — the head's stored statistics rot in a moving representation while the representation itself is fine (our P9.0: rotation, not forgetting). Identical repair philosophy: closed-form, no gradient, move the *statistics*, never touch the bulk.
- **Different from us:** SDC is exemplar-free by constraint; we hold a bounded raw-exemplar LUT, so at sleep we re-forward and re-anchor *exactly* (P9.4: retention 0.787→0.986). SDC's estimator exists to approximate what our sleep does for real. Also their drift is discrete (per-task fine-tuning); ours is continuous endogenous SCFF rotation.
- **What we could borrow or test:** the between-sleeps nudge. Between sleeps, SLDA's `partial_fit` keeps prototypes of *streaming* classes fresh, but prototypes of classes absent from the current domain go stale as the bulk drifts — that is the REV staircase. SDC transfers the measured motion of *present*-class features to *absent*-class prototypes: per-class displacement of fresh running means vs stored prototypes → kernel-weighted transfer to untouched prototypes. Uses features the awake namer already computes: no extra forwards, no store, one weighted average per fire. Test: does SDC-between-sleeps flatten the REV staircase at grid-8, i.e. buy the cadence back from grid-4 (GD-share 0.178 → lower)?
- **What contradicts or challenges us:** nothing head-on; but their finding that NCM+compensation ≈ exemplar methods quietly asks whether our LUT (and its CBRS machinery) earns its keep on streams with smooth drift — the honest control is SDC-only vs LUT-sleep at matched cost.

## Follow-on leads
- LDC (ECCV 2024) — replaces the smoothness assumption with a learned projector (carded here).
- ADC (CVPR 2024) — replaces it with adversarial probes (carded here).
- The embedding-vs-softmax forgetting split → Davari 2022 probe protocol (carded t1.7) — the same anatomy our P9.0 used.
