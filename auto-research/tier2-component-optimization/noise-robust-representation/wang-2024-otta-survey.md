# In Search of Lost Online Test-time Adaptation: A Survey
- **Authors / Year / Venue:** Zixin Wang, Yadan Luo, Liang Zheng, Zhuoxiao Chen, Sen Wang, Zi Huang / 2024 / International Journal of Computer Vision (IJCV)
- **Link:** https://arxiv.org/abs/2310.20199
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐⭐☆ — the field's re-benchmark of online TTA under honest conditions; its batch-size-1 findings are the published verdict on which correction families survive *our* operating regime (per-sample, online, no do-overs).

## TL;DR
An IJCV survey + re-benchmark of online test-time adaptation (adapt as batches arrive, no revisiting), re-running the method families on ViT backbones across corruption and real-world shift benchmarks, with compute (GFLOPs, wall-clock, memory) reported next to accuracy. The sobering result: much of the reported TTA progress is an artifact of large test batches; at batch size 1, optimization stability — not adaptation capacity — decides who survives.

## The mechanism (what it actually establishes)
Three load-bearing findings. (1) **Batch-size dependency:** most gradient-based OTTA methods (Tent lineage) lean on batch statistics and batched entropy gradients; their gains shrink or invert as batch → 1. (2) **Stability dominates at batch 1:** in the single-sample online regime, resistance to perturbation and non-collapse matter more than expressive updates — favoring normalization-statistic corrections, output-level smoothing, and prototype bookkeeping over descended objectives. (3) **Priced adaptation:** methods differ by orders of magnitude in GFLOPs/memory for similar accuracy; the survey introduces reporting adaptation cost as a first-class metric, challenging prior papers' free-lunch framing.

## Key results / claims
Transformer backbones are natively more shift-resilient than CNNs (shrinking the *need* for aggressive TTA); many OTTA methods fail to beat the frozen baseline once streams are realistic (small/dependent batches); efficiency-adjusted rankings differ sharply from raw-accuracy rankings.

## How it relates to us
- **Organ / phase touched:** the evaluation frame for any Stage-2 read-side fix; the P8 energy meter; the P10/P11 stream methodology.
- **Same as us:** their three corrections to the field — realistic streams, cost-priced adaptation, stability over capacity — are P10/P11's methodology independently converged on. Their batch-1 verdict is external authority for our standing constraint: the read-side fix must be statistic-bookkeeping, not test-time optimization.
- **Different from us:** their cost currency is digital (GFLOPs/GPU-memory); ours is metered substrate energy — but the reporting discipline transfers verbatim.
- **What we could borrow or test:** (1) evaluate any read-side correction rung at *stream batch = 1 with dependent ordering* from day one (our P11 arenas already are this — keep it that way); (2) report the correction's energy share on the P8 meter next to its retention gain, survey-style; (3) their taxonomy (normalization-stat / output-level / prototype / optimization) is the clean frame for our synthesis ranking.
- **What contradicts or challenges us:** nothing — it *de-risks* our bias. The one caution: their resilience finding is ViT-specific; our 12-layer SCFF bulk has no attention, so "the backbone absorbs most shift natively" cannot be assumed — P6.0 measured the opposite (OURS 2× more directionally fragile than linear).

## Follow-on leads
- NOTE (NeurIPS 2022) + RoTTA (CVPR 2023) — statistics estimation designed for temporally-correlated streams (our autocorrelated-arena floor from P11).
- The survey's "continual TTA" branch (CoTTA lineage) — TTA that itself must not forget; adjacent to our gate-vs-forgetting economy.
- Efficiency-adjusted TTA leaderboards (2025+) as the external yardstick if we ever publish the read-side fix.
