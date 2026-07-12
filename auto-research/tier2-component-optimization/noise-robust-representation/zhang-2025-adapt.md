# Backpropagation-Free Test-Time Adaptation via Probabilistic Gaussian Alignment (ADAPT)
- **Authors / Year / Venue:** Youjia Zhang, Youngeun Kim, Young-Geun Choi, Hongyeob Kim, Huiling Liu, Sungeun Hong / 2025 (rev. 2026) / NeurIPS 2025 (per official code repo)
- **Link:** https://arxiv.org/abs/2508.15568
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐⭐☆ — 2025 state of the art for *closed-form* TTA: running class means + one shared covariance, classify by Gaussian inference. This is SLDA's algebra rediscovered as a test-time adapter — our namer could do this natively.

## TL;DR
ADAPT reframes test-time adaptation as probabilistic inference: model each class as a Gaussian whose mean is updated incrementally from the unlabeled test stream (pseudo-label-weighted) with one *shared* covariance matrix, and classify by closed-form class-conditional likelihood. No gradients, no iterative optimization, no source data; priors (from CLIP zero-shot in their instantiation) plus a historical knowledge bank keep the pseudo-label updates from biasing the likelihoods.

## The mechanism (how it actually works)
The story: if the frozen backbone's features per class are roughly Gaussian, then adaptation = keeping the Gaussian parameters *current*. Per test sample/batch: (1) get features and a provisional posterior; (2) update the implicated class means as confidence-weighted running averages; (3) maintain one shared covariance (statistical strength pooled across classes — the same tied-covariance bet as LDA/SLDA); (4) classify by the Gaussian discriminant — a closed-form solve, no training loop. Two stabilizers matter: an external prior (zero-shot CLIP scores) regularizes the pseudo-labels so early mistakes don't compound, and a knowledge bank of past statistics anchors against drift-induced bias. Everything is running sums and one matrix solve — the whole adapter is bookkeeping plus algebra.

## Key results / claims
Claims SOTA across a wide range of shift benchmarks (corruptions + domain shifts), in both online and transductive modes, with superior scalability (no per-step optimization) and robustness (no collapse mode, since nothing is descended). The dependence on CLIP priors is the instantiation, not the algebra — the update/inference core is model-agnostic.

## How it relates to us
- **Organ / phase touched:** the namer (SLDA = running class means + shared covariance + closed-form solve — the *same object*); the hippocampus LUT (their knowledge bank); P9.4's proto-reanchor.
- **Same as us:** the entire statistical machinery. Our deployed SLDA namer already maintains class means and a shared covariance; ADAPT shows that machinery, fed *unsupervised confidence-weighted test updates*, is itself a SOTA-grade shift adapter. Their knowledge bank ≈ our LUT; their anchor-against-bias ≈ our sleep re-fit from stored prototypes.
- **Different from us:** they update means from *pseudo-labels* continuously; our namer updates only on gated/sleep events from banked (true-label) history. They lean on an external zero-shot prior we don't have — our substitute anchor is the LUT's consolidated prototypes (arguably cleaner: real labels, just stale).
- **What we could borrow or test:** the *unsupervised mean-update path*: between sleeps, let confident samples update a shadow copy of the class means (confidence-weighted, LUT-anchored); the DDM gate decides when the shadow is trusted into the live namer. Zero new algebra — it's SLDA's own update rule with a confidence weight. Their covariance choice also confirms P9.4's negative: no covariance re-fit needed — mean drift dominates.
- **What contradicts or challenges us:** their stabilizer story implies naive self-labeled mean-chasing *does* bias without an anchor — so the borrow is only safe because we have the LUT + gate; a bare T3A-style chase would inherit the failure they engineered around.

## Follow-on leads
- Official code: https://github.com/AIM-SKKU/ADAPT (NeurIPS 2025 tag).
- FeCAM / AdaGauss (already carded in t1.2) — the covariance-staleness bridge.
- "Shadow statistics + gated promotion" as a general pattern — no direct paper found; candidate experiment of ours.
