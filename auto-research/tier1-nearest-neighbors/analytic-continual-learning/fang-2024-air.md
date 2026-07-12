# AIR: Analytic Imbalance Rectifier for Continual Learning
- **Authors / Year / Venue:** Di Fang, Yinan Zhu, Runze Fang, Cen Chen, Ziqian Zeng, Huiping Zhuang / 2024 / arXiv preprint (2408.10349)
- **Link:** https://arxiv.org/abs/2408.10349
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐ — the closed-form imbalance guard we actually implemented and *struck* in P7.3; this card is the citation for that overturned design guess.

## TL;DR
AIR adds an Analytic Re-weighting Module (ARM) to the analytic-CL recursion: each class's contribution to the least-squares loss is scaled by a closed-form re-weighting factor (inverse-frequency-shaped), so the recursive solve stays optimal-by-algebra while long-tailed and mixed (generalized) streams stop drowning rare classes. Output-side re-balancing, still gradient-free, still exemplar-free.

## The mechanism (how it actually works)
1. **The problem:** the vanilla RLS solve minimizes summed squared error — head classes with more samples dominate the Gram and cross-correlation, so the tail's rows are systematically under-fit (the analytic version of majority bias).
2. **ARM:** per class, compute a re-weighting factor from its running sample count; scale that class's contribution in both the correlation and cross-correlation accumulators. The weighted least-squares problem still has a closed form, and its recursive update is derived so incremental = joint (the family invariant, kept under re-weighting).
3. **Scope:** built for long-tailed CIL and generalized CIL (mixed exposed/unexposed batches, unknown counts).

## Key results / claims
- Significantly outperforms prior methods in long-tailed and generalized CIL scenarios across multiple datasets.
- Keeps the family's properties: no exemplars, no gradient, phase-count robustness.

## How it relates to us
- **Organ / phase touched:** the namer's imbalance guard (P7.3 — the bursty-imbalance rung).
- **Same as us:** the exact problem (bursty, imbalanced label streams hitting a closed-form head) and the same design instinct — our P7 pre-run plan *expected* AIR to be the guard.
- **Different from us — and this is the point:** we ran it. **On our bench AIR over-corrects — it crushes recent classes** — and the committed guard became **class-balanced reservoir sampling (CBRS, buffer-side)**: re-balancing the *input* beat re-weighting the *output* (P7.3, design overturned). One honest hypothesis for the divergence: their factor is tuned for ViT-scale feature dims and long-run class counts; our tiny 768-D tap space + short bursty streams put the correction in a different regime.
- **What we could borrow or test:** their derivation of *weighted* RLS with the joint-equivalence kept is still useful machinery — a gentler (e.g. square-root-frequency) ARM inside our sleep re-fit is a one-knob re-test if imbalance ever bites harder than CBRS can absorb.
- **What contradicts or challenges us:** their headline says output re-weighting wins on long-tail benchmarks; our result says it loses to a buffer fix on ours. Both can be true (different regimes) — but citing AIR requires reporting our negative honestly rather than as a universal verdict.

## Follow-on leads
- GACL (arXiv 2403.15706) — the generalized-CIL algebra AIR extends.
- Logit-adjustment literature (e.g. logit-adjusted online CL, arXiv 2311.06460 — already in the curated library) — the gradient-world version of the same output-side fix.
- CBRS (Chrysakis & Moens, ICML 2020) — the buffer-side guard that actually shipped in our P7.3.
