# A Simple Baseline that Questions the Use of Pretrained-Models in Continual Learning
- **Authors / Year / Venue:** Paul Janson, Wenxuan Zhang, Rahaf Aljundi, Mohamed Elhoseiny / 2022 / NeurIPS 2022 Workshop (Distribution Shifts)
- **Link:** https://arxiv.org/abs/2210.04428
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐⭐⭐ — the field's own confession: a nearest-mean classifier on raw frozen pretrained features beats the elaborate prompt methods — **the backbone is doing the work.**

## TL;DR
Take the same frozen pretrained ViT that L2P uses, learn *nothing at all* except per-class feature means, classify by nearest mean — and you surpass most published PTM-CL methods (≈88.5% on 10-split CIFAR-100 in the updated version). The paper's explicit conclusion: the pretrained feature extractor alone is strong enough, so PTM-CL method comparisons largely measure the pretrain, not the continual-learning machinery.

## The mechanism (how it actually works)
There is deliberately almost none — that is the point. (1) Freeze the pretrained transformer. (2) For each class seen so far, accumulate the running mean of its frozen features (a streaming, order-invariant, one-pass update — no gradient, no buffer). (3) Classify a test sample to the nearest class mean. Since class means are independent accumulators, "learning" a new class cannot corrupt an old one: **zero forgetting by construction**, exactly the algebraic-immunity property of the prototype family. Any measured gap between this and L2P/DualPrompt is the honest value-added of those methods' learnable parts — and the gap turns out to be small or negative.

## Key results / claims
- **88.53% on 10-Split-CIFAR-100** (v2), surpassing most SOTA PTM-CL methods that use the identical pretrained initialization; competitive/better also on CoRe50.
- Conclusion stated outright: the pretrained extractor "can be strong enough to achieve competitive or even better continual learning performance" than methods built on top of it; future methods should demonstrate representational value **beyond** the frozen pretrain.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole architecture claim — bulk value (P11.0 decomposition) + namer (P7).
- **Same as us:** the winning object is *literally our namer's topology* — streaming prototype statistics over frozen features, no gradient, order-invariant. The field's strongest baseline converged onto the shape we committed to for substrate reasons.
- **Different from us:** their frozen features come from a 14M-image supervised pretrain; the paper never asks whether the *classifier* would survive on a weak or self-grown representation — that question is ours to answer (and P11.0's Δbulk-vs-random-reservoir rung is our answer-in-progress: +0.417 on the synthetic home, ≈0 on near-linear digits).
- **What we could borrow or test:** their evaluation discipline — always report the **frozen-features + NCM floor** next to any headline. We already run RanDumb-style controls (P7.0 guard); this paper is the citation for making the control the *front-door* number, not a guard buried in a card.
- **What contradicts or challenges us:** it *supports* our skepticism of the PTM-CL field but also sharpens the knife on us: if a prototype head on any decent representation is enough, then our value-add must be provable in the **bulk** (self-grown features beating a random projection of the same width/cost on the target stream) and in the **substrate economics** — not in the head, which is now commodity. Where the bulk's Δ is ≈0 (near-linear arenas), we genuinely are "SLDA with extra steps," and the honest pitch must say so.

## Follow-on leads
- RanDumb (2402.08823 — already carded, t1.2): the even harsher control (random projection instead of pretrain).
- "Reflecting on the State of Rehearsal-free CL with Pretrained Models" (2406.09384) — the 2024 systematization of this critique.
- A "pretrain-free PTM-CL track" benchmark idea: PTM-CL methods re-run with weak backbones (Tang et al. 2308.10445 did a version of this).
