# Mean Teachers Are Better Role Models: Weight-Averaged Consistency Targets
- **Authors / Year / Venue:** A. Tarvainen, H. Valpola / 2017 / NIPS
- **Link:** https://arxiv.org/abs/1703.01780 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐⭐☆ — the literal "slow EMA copy = the stable anchor" mechanism our stable namer rebuilds in closed form; the parent of CLS-ER's slow memory.

## TL;DR
Keep a **teacher** whose weights are an **EMA of the student's** weights; train the student so its predictions match the teacher's on perturbed inputs (a consistency loss). The slowly-averaged teacher is a more stable, higher-quality target than the student itself, and updates every step (unlike epoch-level Temporal Ensembling).

## The mechanism (how it actually works)
Two nets, same architecture. The student learns by gradient descent. The teacher is *never* trained directly — after each step it becomes `θ_teacher ← ρ·θ_teacher + (1−ρ)·θ_student` (ρ≈0.99–0.999). Because the teacher is a running average of many student states, its predictions are smoother and less jumpy; using them as consistency targets stabilizes the student and denoises the labels. The averaging is the entire source of the teacher's superiority — it's Polyak averaging repurposed as a self-supervision signal.

## Key results / claims
- SVHN 250 labels: 4.35% error (beats Temporal Ensembling with 1000 labels).
- CIFAR-10 4000 labels: 10.55% → 6.28%; ImageNet 10% labels: 35.24% → 9.11% (with ResNet).
- Continuous (per-step) EMA scales to large datasets where epoch-level target ensembling fails.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer; directly the "stable namer" concept.
- **Same as us:** this **is** the slow-weight stability anchor. CLS-ER/ESMER (already carded, t1.4) are Mean-Teacher-for-CL; our proposal is Mean-Teacher-for-a-*closed-form*-head. The intent is identical: an anti-recency reference that changes slowly.
- **Different from us:** Mean Teacher EMAs **gradient-trained network weights** and *feeds back* a training loss. We would EMA **sufficient statistics** (Gram/mean/cov) of a *no-gradient* head, and it has *no loss to feed back into* — the stable namer would be used as an inference-time anchor / re-fit prior, not a training target. That removes the whole "consistency-loss coupling" and makes it far cheaper — but also removes the feedback that makes the teacher earn its keep.
- **What we could borrow or test:** the **ρ≈0.99–0.999** regime as the starting α for the stable namer; the *perturbed-input consistency* idea maps onto our noise-augmentation view (P6) — a stable namer whose anchor is fit on noise-augmented features would be Mean-Teacher-consistency in closed form.
- **What contradicts or challenges us:** the substrate already has an **EMA Scap register** and the Scap "IS an EMA" — so a second slow EMA anchor is nearly free to add, but the value Mean-Teacher gets comes from the *consistency coupling*, which our closed-form head lacks. We must show the anchor helps as a pure statistic-smoother, not as a training signal.

## Follow-on leads
- CLS-ER (Arani 2022) / ESMER (Sarfraz 2023) — already carded (t1.4); the CL descendants. Temporal Ensembling (Laine & Aila 2017). BYOL/DINO EMA-target SSL. π-model consistency.
