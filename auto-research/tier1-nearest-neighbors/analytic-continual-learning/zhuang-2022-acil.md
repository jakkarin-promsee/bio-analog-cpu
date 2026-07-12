# ACIL: Analytic Class-Incremental Learning with Absolute Memorization and Privacy Protection
- **Authors / Year / Venue:** Huiping Zhuang, Zhenyu Weng, Hongxin Wei, Renchunzi Xie, Kar-Ann Toh, Zhiping Lin / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2205.14922
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the paradigm anchor: the paper that turned continual classification into recursive least squares, the family our namer belongs to.

## TL;DR
ACIL recasts class-incremental learning as a recursive least-squares (ridge regression) problem on frozen features: keep one running correlation (Gram) matrix, update it batch-by-batch, and the recursive solution is *algebraically identical* to training on all data jointly. No gradients, no exemplars, zero forgetting of the linear map by construction.

## The mechanism (how it actually works)
This is signal-processing, not neuroscience — RLS from adaptive filtering (Gauss → Plackett 1950 → Kalman), applied to a classifier head:

1. **Freeze the feature extractor** (a conventionally pre-trained backbone). All learning happens in one linear map on top.
2. **Expand features** through a random/fixed nonlinear buffer layer (widen, then ReLU) — the ELM move, buying nonlinear capacity for a linear solve.
3. **Keep one matrix:** the running autocorrelation `R = Σ φφᵀ` (equivalently its regularized inverse, updated by Woodbury). This d×d matrix *is* the memory of everything seen — no raw samples stored (their "privacy protection" claim).
4. **Per batch:** rank-update `R` and re-solve `W = (R + λI)⁻¹ Σ φyᵀ` recursively. The theorem ("absolute memorization"): the recursive weights equal the joint-training weights exactly, for any task split.

Forgetting in the head is therefore *impossible by algebra* — the phase count doesn't matter (5 vs 50 phases give near-identical accuracy).

## Key results / claims
- Competitive CIL accuracy with near-identical results across 5–50 phase splits; state-of-the-art in large-phase regimes (25/50 phases) where gradient methods degrade.
- Exemplar-free — beats replay-based methods without storing data.
- The whole later family (GKEAL, DS-AL, GACL, F-OAL, AIR) is built on this recursion.

## How it relates to us
- **Organ / phase touched:** the namer (P7 RanPAC/SLDA commit; P8 economy; P9 sleep re-fit).
- **Same as us:** our committed RanPAC head *is* this machinery — random ReLU expansion → running Gram → ridge solve `W=(G+λI)⁻¹M`. Gradient-free naming on frozen features is their paradigm and our P7 verdict ("the 20% is NOT gradient descent").
- **Different from us:** (1) Their backbone is a large *supervised, pre-trained, truly frozen* ViT/ResNet; ours is a tiny self-trained SCFF bulk that keeps rotating (P9: rotates-not-forgets) — their absolute-memorization theorem silently *breaks* under representation drift, which is exactly the regime we live in. (2) They carry the exact recursion forever; we periodically **re-fit closed-form from a bounded CBRS LUT at sleep** — an approximation they'd call a downgrade, but it's what makes closed-form survive a moving substrate. (3) They update every batch; our namer is **drift-gated** (fires only when the error-EMA gate trips — P8's "firing more forgets more" safety result has no analog here).
- **What we could borrow or test:** the equivalence theorem gives us a clean *oracle*: on a truly frozen bulk, our sleep re-fit should exactly reproduce their recursion — a cheap correctness guard for the namer path.
- **What contradicts or challenges us:** their zero-forgetting-by-construction makes our gate look unnecessary *if* the bulk were frozen; our P8/P9 evidence (gate = safety under drift) is the answer, and the difference should be stated explicitly when we cite them.

## Follow-on leads
- GKEAL (CVPR 2023) — Gaussian-kernel embedding variant for few-shot CIL.
- The Analytic-continual-learning repo (ZHUANGHP) — the family's living index.
- ORFit (arXiv 2207.13853) — one-pass learning bridging orthogonal GD and RLS; the theory bridge between the two worlds.
