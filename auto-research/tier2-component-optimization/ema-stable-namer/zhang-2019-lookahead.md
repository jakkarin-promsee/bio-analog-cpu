# Lookahead Optimizer: k Steps Forward, 1 Step Back
- **Authors / Year / Venue:** M. R. Zhang, J. Lucas, G. Hinton, J. Ba / 2019 / NeurIPS
- **Link:** https://arxiv.org/abs/1907.08610 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐☆☆ — the explicit **two-timescale fast/slow** template (fast explores, slow interpolates toward it) — the cleanest schematic for a fast-namer + stable-namer pair.

## TL;DR
Maintain fast weights (updated by any inner optimizer for k steps) and slow weights that periodically **interpolate toward** the fast ones: `θ_slow ← θ_slow + α(θ_fast − θ_slow)`, then reset fast to slow. The slow weights cut the inner optimizer's variance at negligible cost and make it robust to hyperparameters.

## The mechanism (how it actually works)
The fast weights sprint k steps in the noisy inner-loop direction; the slow weights take one calm step of size α toward wherever the fast weights ended up. This is a *forgetting* interpolation (an EMA with period k) on the slow track. It smooths oscillations the inner optimizer makes across a valley, so you get the exploration of a big step with the stability of an average — and the fast weights are periodically pulled back to the slow anchor so they can't wander off.

## Key results / claims
- Lowers inner-optimizer variance with negligible compute/memory.
- Improves SGD and Adam at their **default** hyperparameters (robustness to tuning).
- Consistent gains across ImageNet, CIFAR-10/100, NMT, Penn Treebank.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer; the *architecture* of a fast/slow namer pair and the sleep-time "pull back."
- **Same as us:** the fast-explore / slow-anchor split is exactly the fast-namer (tracks drift) + stable-namer (slow EMA) pair. The **"1 step back"** — resetting the fast state toward the slow anchor — is a clean model for what sleep could do: not a full re-fit, but an *interpolation* of the deployed head toward the slow anchor.
- **Different from us:** Lookahead operates on gradient-optimizer weights; we operate on closed-form statistics. But the interpolation rule `slow ← slow + α(fast − slow)` is *identical algebra* to an EMA of our Gram/mean — so Lookahead is basically "EMA-of-statistics with a period and a reset," a variant we can test directly.
- **What we could borrow or test:** the **periodic pull-back** as a cheaper alternative to (or complement of) grid-4 sleep — at each cadence tick, interpolate the fast namer's statistics toward the slow anchor instead of a full LUT re-fit. Ranks high on substrate-fit: it's one Scap-EMA update, no LUT replay.
- **What contradicts or challenges us:** Lookahead's slow track assumes fast/slow stay compatible over k steps; under fast bulk rotation, too large k lets the anchor go stale (same rotation caveat as SWA/soups).

## Follow-on leads
- Lookahead-minmax (GANs). Two-timescale SA (Borkar). Reptile/first-order MAML (a lookahead across tasks). Interpolation-at-sleep vs re-fit-at-sleep ablation for our loop.
