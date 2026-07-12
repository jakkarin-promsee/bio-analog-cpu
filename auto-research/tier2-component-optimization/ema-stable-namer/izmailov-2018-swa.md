# Averaging Weights Leads to Wider Optima and Better Generalization (SWA)
- **Authors / Year / Venue:** P. Izmailov, D. Podoprikhin, T. Garipov, D. Vetrov, A. G. Wilson / 2018 / UAI
- **Link:** https://arxiv.org/abs/1803.05407 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐☆☆ — the canonical "averaging finds flatter, more general solutions" evidence; the intuition (not the mechanism) our stable namer trades on.

## TL;DR
Stochastic Weight Averaging collects weight snapshots along an SGD trajectory (under a cyclic or constant learning rate) and returns their **arithmetic mean**. The averaged point sits in a **wider, flatter** region of the loss surface and generalizes better than the last iterate — an ensemble-in-weight-space at zero inference cost.

## The mechanism (how it actually works)
Late in training, SGD with a high/cyclic LR doesn't converge to a point — it bounces around the rim of a wide basin, each snapshot a slightly different corner. SWA just averages those corners. Because the basin is roughly convex locally, the average lands nearer its *center* — a flatter minimum that train/test surfaces agree on better than any single rim point. It approximates Fast Geometric Ensembling with one model and near-zero overhead (you only re-estimate BatchNorm stats once at the end).

## Key results / claims
- Consistent test-accuracy gains over SGD on CIFAR-10/100 and ImageNet across ResNet/PyramidNet/DenseNet/Shake-Shake.
- Finds **flatter** solutions (measured by loss sensitivity to weight perturbation) — the mechanistic story for the generalization gain.
- Negligible compute/memory overhead; trivial to implement.

## Key results / claims
Flatness ↔ generalization; a running average of noisy iterates centers the basin.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer; the stability anchor idea generally.
- **Same as us:** the *reason to average* — a running mean of noisy estimates is more robust/general than the latest one. Our "stable namer" is SWA-in-spirit applied to the namer's sufficient statistics rather than to network weights.
- **Different from us:** SWA averages **weights of a gradient-trained net** over a *stationary* task, offline at the end. We average **closed-form statistics online under drift** — no gradient, non-stationary, continuous. SWA has no forgetting; we need it.
- **What we could borrow or test:** the flatness diagnostic — if a slow-averaged namer really helps, its implied classifier should be *less sensitive* to which recent batch it saw (an order-invariance / worst-point read we already measure).
- **What contradicts or challenges us:** SWA's win assumes iterates share **one basin**. Under drift the namer's statistics move *between* basins (the bulk rotates — P9.0); averaging across a rotation is averaging across incompatible frames, which *hurts* (this is exactly why P9.1's EMA-view worsened worst-BWT). So the stable-namer's α must be fast enough to stay inside one rotation epoch, or it must be re-anchored at sleep.

## Follow-on leads
- Fast Geometric Ensembling (Garipov 2018). SWAG (Bayesian SWA). Loss-landscape flatness ↔ CL forgetting (Mirzadeh, linear-mode connectivity).
