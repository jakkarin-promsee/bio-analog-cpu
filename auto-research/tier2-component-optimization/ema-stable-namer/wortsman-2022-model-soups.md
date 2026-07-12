# Model Soups: Averaging Weights of Fine-Tuned Models Improves Accuracy
- **Authors / Year / Venue:** M. Wortsman, G. Ilharco, S. Gadre, et al. / 2022 / ICML
- **Link:** https://arxiv.org/abs/2203.05482 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐☆☆☆ — averaging *independently* produced models (not a trajectory) still helps; a boundary case for when weight averaging is/ isn't valid.

## TL;DR
Instead of picking the single best fine-tuned model from a hyperparameter sweep, **average their weights** ("soup"). Greedy or uniform soups beat the best individual model and cost nothing extra at inference, because the fine-tuned models fall in a shared low-error basin.

## The mechanism (how it actually works)
Fine-tuning from a common pretrained init keeps all runs in one wide, roughly-convex basin (linear mode connectivity). Averaging their weights lands in the basin interior — flatter, more robust to distribution shift — the same flatness argument as SWA, but across *independent* runs rather than one trajectory. Greedy soup adds models one at a time only if held-out accuracy improves, guarding against a bad ingredient.

## Key results / claims
- ViT-G soup → 90.94% ImageNet top-1 (SOTA at publication); gains on OOD/robustness benchmarks too.
- Weight-averaging ≈ logit-ensembling when the models are close, both explained by loss flatness.
- **Caveat that matters to us:** averaging only works when the models share a basin; averaging weights of *unrelated* solutions is meaningless.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer; the "how far apart can two averaged estimators be" boundary.
- **Same as us:** confirms averaging estimators is a cheap, inference-free stability/robustness win — the general license for a stable namer.
- **Different from us:** soups average *weights of end-to-end nets*; we'd average *closed-form statistics*. And soups require a **shared basin** (common init) — the honest precondition.
- **What we could borrow or test:** the **greedy** guard — only fold the slow anchor into the fast namer if held-out worst-point BWT actually improves (a substrate-cheap acceptance test at sleep), rather than trusting a fixed α.
- **What contradicts or challenges us:** the shared-basin precondition is the same warning as SWA — under bulk rotation the "old" statistics and "new" statistics may not be in one basin, and a naive soup/EMA of them is the wrong operation.

## Follow-on leads
- Linear mode connectivity (Frankle 2020). "Editing models with task arithmetic" (Ilharco 2023). Fisher-weighted averaging (Matena & Raffel 2022) — a *statistically weighted* soup, closer to what an EMA-of-Gram implicitly does.
