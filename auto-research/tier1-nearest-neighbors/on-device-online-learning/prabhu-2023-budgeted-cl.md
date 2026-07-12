# Computationally Budgeted Continual Learning: What Does Matter?
- **Authors / Year / Venue:** Ameya Prabhu, Hasan Abed Al Kader Hammoud, Puneet Dokania, Philip H.S. Torr, Ser-Nam Lim, Bernard Ghanem, Adel Bibi / 2023 / CVPR 2023
- **Link:** https://arxiv.org/abs/2303.11165
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the field-level verdict on CL under a compute budget: everything clever loses to uniform sampling — the frame our P10 Pareto result already lives in.

## TL;DR
Fix the *compute* budget (not just the memory buffer) and re-run the continual-learning canon at scale (ImageNet2K, Continual Google Landmarks V2; data-, class-, and time-incremental). Result: **no CL method beats a minimal baseline that just samples uniformly from memory and fine-tunes** — sampling strategies, distillation losses, and partial-tuning schemes all fail to pay for themselves, across 20–200 stream steps and multiple budgets.

## The mechanism (how it actually works)
The move is methodological: prior CL controlled *storage* (buffer size) but let methods spend unlimited compute per step — so "smart" methods silently bought accuracy with FLOPs. Here every method gets the same training-compute allowance per stream step; anything a method spends on distillation teachers, importance weights, or extra passes comes out of its gradient-step allowance. Under that accounting, the ranking inverts: the minimal recipe (uniform sample from the buffer + plain fine-tuning of the whole net or just the classifier) is the frontier. The paper is the *static* twin of Ghunaim et al.'s real-time protocol (same group), and together they define budget-honest CL evaluation.

## Key results / claims
- Traditional CL approaches, **with no exception**, fail to outperform the uniform-sampling baseline under matched compute — consistent across three incremental settings and both large-scale benchmarks.
- Distillation-based methods degrade most; partial fine-tuning (classifier-only) is competitive at low budgets.
- Conclusion: CL-method sophistication as published is largely a compute artifact.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P10 fair race (tuned budgeted ER baseline) and the P8.5 energy comparison — the evaluation frame.
- **Same as us:** this is the *published justification for our baseline choice* — P10's "fair, budgeted, tuned BP+replay" opponent is exactly the minimal baseline this paper says is the true frontier; racing anything weaker would have been a strawman. Our honest R1 (a small tuned ER dominates the acc×energy Pareto) is this paper's finding reproduced on our bench.
- **Different from us:** budget = FLOPs on digital hardware; no substrate axis, no energy meter, no drift gate, no notion that *more* updates can be less safe (their baseline fine-tunes constantly and forgetting is only fought with the buffer).
- **What we could borrow or test:** their per-step compute-allowance accounting — we meter energy *totals* per stream; a per-step allowance framing ("what can each brain afford between two samples") would let us publish GD-share as a budget curve directly comparable to this literature.
- **What contradicts or challenges us:** the blunt reading — "under a budget, just do tiny uniform replay" — is also aimed at *us*: our P10 Pareto loss to tuned ER is predicted by this paper. Our answer (safety ≈10×, noise, order-invariance, substrate floor — the off-Pareto wins) must be stated *against* this specific result, and this is the citation to state it against.

## Follow-on leads
- Ghunaim et al. 2023 — the real-time-stream twin (carded here).
- Seo et al. 2024/2025 — total-budget (FLOPs+bytes) metric + adaptive freezing (carded here).
- Harun et al. 2023, "How Efficient Are Today's Continual Learning Algorithms?" — the CL-compute audit from the SIESTA group.
