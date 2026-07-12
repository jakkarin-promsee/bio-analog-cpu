# Resurrecting Old Classes with New Data for Exemplar-Free Continual Learning (ADC)
- **Authors / Year / Venue:** Dipam Goswami, Albin Soutif-Cormerais, Yuyang Liu, Sandesh Kamath, Bartłomiej Twardowski, Joost van de Weijer / 2024 / CVPR 2024
- **Link:** https://arxiv.org/abs/2405.19074 (code: https://github.com/dipamgoswami/ADC; CVF: https://openaccess.thecvf.com/content/CVPR2024/papers/Goswami_Resurrecting_Old_Classes_with_New_Data_for_Exemplar-Free_Continual_Learning_CVPR_2024_paper.pdf)
- **Tier / Topic:** tier2-component-optimization / t2.6 prototype drift compensation
- **Relevance:** ⭐⭐ — the most accurate drift estimator of the line, but its probe generation needs input-gradients through the network — substrate-illegal for our forward-only bulk. Useful as the accuracy ceiling the legal methods should be judged against.

## TL;DR
SDC measures drift only where new data happens to live; if no new data lands near an old class, its prototype stays stale. ADC *manufactures* probe data exactly where old classes live: adversarially perturb new-task images until the old model embeds them next to an old prototype, then watch where the new model sends those same probes. The displacement is a direct, per-class drift measurement — no exemplars stored.

## The mechanism (how it actually works)
1. For old class c, take current-task images and run a targeted adversarial perturbation (gradient steps on the *input*) so their embeddings under the old backbone f_{t−1} move close to prototype μ_c — synthetic stand-ins for class c, placed by construction where the estimate is needed.
2. Forward the same perturbed images through the new backbone f_t. Adversarial samples transfer across the two related feature spaces (the paper's empirical load-bearing fact), so their new positions mark where class c's region *went*.
3. Compensate: μ_c ← μ_c + mean displacement of its probes. Cheap per step (a few PGD-style iterations), no raw-data storage.

## Key results / claims
- Better prototype tracking than SDC and stronger accuracy than prior exemplar-free CIL on standard + fine-grained benchmarks, with the largest gains in small-first-task (cold-start) settings — exactly where the smooth-drift assumption of SDC is weakest.
- Described as computationally cheap relative to training; the cost is a handful of forward+input-gradient passes per old class.

## How it relates to us
- **Organ / phase touched:** sleep re-fit / stored prototypes; the between-sleeps staleness axis (P10 REV staircase).
- **Same as us:** wants what our sleep already has — *measurements at the old classes' locations*, not extrapolations. ADC fakes old-class data; our LUT stores real old-class data.
- **Different from us:** the probe generation is gradient-based through the model input — our SCFF bulk exposes no backward path (analog forward physics; GD reads taps, never writes or differentiates the bulk). Structurally unadoptable, not merely expensive.
- **What we could borrow or test:** the *judgment*, not the mechanism: ADC establishes that estimator accuracy is the axis on which compensation methods separate, and that the win case is drift far from new data. For us that translates to: when the current domain is far from an absent class, an SDC nudge will (correctly, but uselessly) do nothing — and the honest fallback is a micro-probe: re-forward a few LUT items of the stale class through the current bulk (a "micro-sleep" costing probe_size × depth forwards, ~100× less than a full re-fit). Our LUT makes the ADC trick unnecessary — real probes beat adversarial ones.
- **What contradicts or challenges us:** none directly; it strengthens the case that holding a small raw store (our LUT) is the cleaner engineering answer than exemplar-free acrobatics — the field pays with gradients for what we pay for with SRAM.

## Follow-on leads
- Honda 2025 — Adversarial Pseudo-replay (WACV 2026): the distillation+covariance-calibration successor (carded here).
- Query Drift Compensation for retrieval embedding models (arXiv:2506.00037) — the same staleness problem in retrieval/embedding systems; possible future wildcard topic.
