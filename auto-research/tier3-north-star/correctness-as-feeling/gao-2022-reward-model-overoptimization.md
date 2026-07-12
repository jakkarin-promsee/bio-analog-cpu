# Scaling Laws for Reward Model Overoptimization
- **Authors / Year / Venue:** Leo Gao, John Schulman, Jacob Hilton — 2022, arXiv:2210.10760 (OpenAI; published ICML 2023)
- **Link:** https://arxiv.org/abs/2210.10760
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐⭐ — the quantitative law of how a self-generated signal collapses when you optimize against it. The design constraint every "feeling" must be built under.

## TL;DR
Train a proxy reward model on labels from a fixed "gold" reward model, then optimize a policy against the proxy: true (gold) performance **rises, peaks, then falls** as optimization pressure grows — Goodhart's law measured. The degradation follows smooth functional forms in the distance the policy has moved, with coefficients that scale predictably with proxy-model size and data.

## The mechanism (how it actually works)
The trick that makes collapse measurable: use a large "gold" RM as synthetic ground truth (so true reward is queryable), train a smaller proxy RM on gold-labeled comparisons, then optimize the policy against the *proxy* two ways — best-of-n sampling and RL (PPO). Plot gold score against **d = how far the policy has moved from its starting point** (√KL divergence).

The empirical laws: for best-of-n, gold reward ≈ d(α − βd); for RL, ≈ d(α − β·log d). Both are "rise then fall" — the proxy keeps climbing while the gold score turns over. α (the real information in the proxy) and β (the hackability) vary smoothly with proxy size and label count: bigger/better-fed proxies peak later, but **every proxy peaks**. KL penalties shift the picture but don't remove the hump.

The plain-words mechanism: the proxy is accurate near the data it was fitted on. Optimization is a search for the proxy's *errors* — the policy migrates exactly toward where the proxy over-scores. Distance-from-anchor is the honest x-axis of trust.

## Key results / claims
- Overoptimization is smooth and predictable, not a cliff — you can *forecast the peak* from proxy size/data.
- Holds for both optimizers (BoN and RL) with different functional forms; RL moves further in KL for the same gain (less KL-efficient).
- Larger proxy RMs are strictly better but only delay the hump; more labels likewise.

## How it relates to us
- **Organ / phase touched:** the gate (error-EMA / DDM), any future learned critic head, the north-star halt; sleep cadence.
- **Same as us:** we already treat the gate as a *safety* device, not a reward ("firing more forgets more," P8). This paper is the general theorem-shaped version of that instinct.
- **Different from us:** their proxy is a big learned network; our candidate self-signals are cheap statistics (margin, drift, settle-Δ). Cheaper signals have smaller α (less information) but also far fewer parameters to hack — the hump shape still applies whenever *weights are updated to please the signal*.
- **What we could borrow or test:** two design rules. **(1) Gate, never target:** the feeling may decide *when* to learn/halt, but the learning objective must remain grounded (data likelihood, labeled outcome, LUT re-fit) — never "update weights to raise the confidence signal." Our current loop already obeys this; the north-star loop must keep obeying it when the halt becomes learnable. **(2) The x-axis of trust is distance-from-anchor:** their d = √KL from the initial policy is structurally our **tap-drift from the sleep anchor**. The hump predicts a quantitative re-grounding rule — recalibrate/re-fit when accumulated drift approaches the forecast peak, which upgrades cadence from a fixed grid to a measured trust budget.
- **What contradicts or challenges us:** it warns against the most tempting north-star shortcut — "minimize your own energy/goodness as the correctness reward." SCFF goodness is a training objective; using it *also* as the correctness feeling and optimizing it harder is the exact proxy-collapse channel.

## Follow-on leads
- Skalse et al. 2022, "Defining and Characterizing Reward Hacking" (NeurIPS) — the formal theory (when is a proxy unhackable: essentially never, unless it equals the true reward).
- Gao's setup reused for *process* reward models (PRM overoptimization, 2024–2025) — does dense supervision delay the hump?
- Weng/Pan et al. surveys on reward hacking taxonomy — a broader failure catalog for gate design.
