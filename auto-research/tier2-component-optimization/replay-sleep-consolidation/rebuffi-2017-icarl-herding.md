# iCaRL: Incremental Classifier and Representation Learning (herding exemplar selection)
- **Authors / Year / Venue:** Sylvestre-Alvise Rebuffi, Alexander Kolesnikov, Georg Sperl, Christoph H. Lampert / 2017 / CVPR 2017
- **Link:** https://arxiv.org/abs/1611.07725 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule (the *herding* anchor)
- **Relevance:** ⭐⭐⭐ — the seminal **herding** (mean-matching) exemplar-selection rule; important to us mainly because it is the exact policy P9.3 tested and found **tied with CBRS (the buffer-spine null)** — this is the citation for that null, not an untried lever.

## TL;DR
Under a fixed exemplar budget, select each class's exemplars by **herding**: greedily add samples so the running **mean of the exemplars best approximates the true class mean**. Classify by nearest-mean-of-exemplars. As classes grow, the per-class budget shrinks (fixed total ÷ #classes) — the classic fixed-capacity scaling.

## The mechanism (how it actually works)
For a class with feature mean μ, build the exemplar set greedily: at step k add the sample that makes the average of the first k exemplars closest to μ. This front-loads the most "central/representative" samples so the stored set is a good **mean estimator** at any prefix length — convenient because when the budget later shrinks you just drop the tail. Classification is nearest-class-mean over the stored exemplars (a prototype classifier). The representation itself is co-trained with distillation, but the **selection rule (herding)** is the transferable, model-agnostic part.

## Key results / claims
On CIFAR-100 / ImageNet class-incremental, iCaRL learns many classes over long sequences where fixed-representation and naive methods collapse. Herding modestly beats random exemplar selection in the original ablations; later work (Mensink NCM, and our own P9.3) finds the margin is task-dependent and often small.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** bounded-LUT eviction (P9.3), the namer's prototype classifier, fixed-capacity scaling (P11 C=20).
- **Same as us:** herding's product is a **class-mean-matched buffer** and a **nearest-mean classifier** — structurally our LUT-prototype + closed-form namer. The fixed-budget-÷-classes scaling is *our* C=20 crossover, first stated here.
- **Different from us:** herding keeps the **dense mean** (the most central samples). Our P9 spine argues eviction should preserve class **directions**, not collapse to the mean — which is why P9.3 found herding only **ties** CBRS (a "buffer-spine null": on that task density ≈ class, so mean-matching neither helped nor hurt).
- **What we could borrow or test:** nothing new to *deploy* — we already raced it. Its value is as the **named null/baseline**: any new selection lever (info-weighted, prototype-spread) must be shown to beat *both* CBRS and herding, and P9.3's tie is the reference bar.
- **What contradicts or challenges us:** herding's premise (keep the mean-estimators) is the opposite of our direction-spine. Where a future task has density ≠ class, herding should *lose* to a spread-preserving eviction — a concrete falsifiable prediction of our spine story worth testing on the P11 real streams.

## Follow-on leads
- Mensink et al. 2013 — Nearest-Class-Mean, the classifier iCaRL borrows.
- Bang et al. 2021 — Rainbow Memory (diversity/uncertainty exemplar selection) as a herding successor.
