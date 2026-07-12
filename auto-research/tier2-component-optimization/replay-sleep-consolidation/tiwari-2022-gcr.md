# GCR: Gradient Coreset based Replay Buffer Selection for Continual Learning
- **Authors / Year / Venue:** Rishabh Tiwari, Krishnateja Killamsetty, Rishabh Iyer, Pradeep Shenoy / 2022 / CVPR 2022
- **Link:** https://arxiv.org/abs/2111.11210 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule
- **Relevance:** ⭐⭐⭐⭐ — states the buffer-selection **objective** most cleanly (a weighted coreset whose summed gradient matches the gradient of *all data seen so far*); the exact ideal our closed-form sleep re-fit approximates without ever forming a gradient.

## TL;DR
Keep a small **weighted** subset ("coreset") whose gradient, summed with weights, best approximates the gradient of the entire seen dataset w.r.t. the current model. Re-select it each task by greedy submodular optimization (an OMP-style match). The buffer is then the best small stand-in for full replay.

## The mechanism (how it actually works)
Full replay would mix in the gradient of all past data; that's the target. GCR picks weights **w** and a subset **S** minimizing ‖Σ_{i∈S} wᵢ∇ℓᵢ − ∇L_all‖ — a **gradient-matching coreset** solved greedily (orthogonal-matching-pursuit / GradMatch machinery from the same group). Samples get *importance weights*, so replay is weighted, not uniform. Selection is re-done as the model drifts, because the target gradient moves. Requires per-sample gradients and a running estimate of the full-data gradient.

## Key results / claims
+2–4% absolute over SOTA in offline class-incremental, up to **+5%** in online/streaming, and a further ~5% when combined with supervised-contrastive loss — consistently above reservoir / ER across CIFAR / TinyImageNet buffer-size sweeps. The gains grow as the buffer gets *smaller* (the tight-cap regime).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** sleep re-fit + bounded-LUT eviction (P9), C=20 crossover (P11).
- **Same as us:** GCR's target — "a small buffer that stands in for all past data at consolidation" — is *literally* our sleep story (re-fit the namer over the LUT so it stands in for history). And its finding that **weighting** samples helps at small caps speaks straight to P11's C=20 replay-dilution crossover.
- **Different from us:** the match is done in **gradient** space and produces **gradient replay**; our re-fit is a **closed-form** ridge/prototype solve over stored features — no gradient of any sample is ever formed. GCR's weighting is a gradient importance; ours would have to be a covariance/count importance.
- **What we could borrow or test:** **weighted** entries in the Gram/prototype accumulation — instead of every LUT sample contributing equally to the closed-form solve, weight by a substrate-cheap importance (namer leverage / margin / class-rarity). This is the gradient-free analogue of GCR's core idea and is directly testable in our sleep re-fit.
- **What contradicts or challenges us:** GCR's headline is that gradient-matched weighted selection beats uniform/reservoir most **at small buffers** — precisely where our fixed LUT bites (C=20). It implies our uniform-within-CBRS re-fit is leaving retention on the table exactly where P11 found the crossover.

## Follow-on leads
- GradMatch / CRAIG (Killamsetty et al. 2021) — the coreset-for-efficient-training lineage; feature-space k-center is the gradient-free version.
- Weighted closed-form ridge (importance-weighted Gram) as our substrate-native transplant.
