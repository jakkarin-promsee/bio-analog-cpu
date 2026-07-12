# Online Spatio-Temporal Learning in Deep Neural Networks (OSTL)
- **Authors / Year / Venue:** Thomas Bohnstingl, Stanisław Woźniak, Wolfgang Maass, Angeliki Pantazi, Evangelos Eleftheriou / 2022 / IEEE Transactions on Neural Networks and Learning Systems (arXiv:2007.12723, 2020)
- **Link:** https://arxiv.org/abs/2007.12723
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐ — generalizes the e-prop idea beyond spikes: a clean **spatial/temporal gradient split** that is BPTT-equivalent (for shallow nets) and applies to SNNs, LSTMs, and GRUs alike — the "this is a general online-learning primitive, not a spiking trick" statement.

## TL;DR
OSTL is a framework that separates each layer's gradient into a **spatial** part (across layers, instantaneous) and a **temporal** part (carried forward in per-neuron eligibility-like traces), letting deep recurrent/spiking nets train **online, forward-in-time**. For shallow nets it is *provably gradient-equivalent to BPTT*, and the same formulation covers SNNs, LSTMs, and GRUs.

## The mechanism (how it actually works)
Take a recurrent layer's exact BPTT gradient and reorganize it so that everything that depends on the *past* is accumulated into forward-propagating **eligibility traces** (temporal component), while everything that depends on the *present* multiplies in as an instantaneous **spatial** factor (the top-down error at this step). The weight update is then `spatial_factor(t) × temporal_trace(t)` — computed each step with no unrolling. For a single recurrent layer this equals the BPTT gradient exactly; stacking layers introduces a controlled approximation. Crucially the derivation is unit-agnostic: swap the neuron model (LIF spike, LSTM cell, GRU cell) and the same trace machinery applies.

## Key results / claims
- **First online training of SNNs with BPTT-equivalent gradients** (shallow case).
- Demonstrated across architectures (SNN / LSTM / GRU) and tasks (language modeling, speech recognition) **on par with BPTT baselines**.
- Positions the spatial/temporal split as a general principle for neuromorphic online learning.

## How it relates to us
- **Organ / phase touched:** north-star temporal loop; the eligibility-trace primitive.
- **Same as us:** the **spatial (now) × temporal (trace) factorization** is the clean statement of what our substrate does cheaply — an instantaneous local product times a slow leaky-cap register. OSTL says this factorization is *general*, which matters: it means the leaky-cap-trace primitive isn't spiking-specific, so adopting it in a rate-based recurrent loop is legitimate.
- **Different from us:** OSTL is exact-online-gradient (still gradient descent, still supervised, still needs the temporal trace per weight). Our object is unsupervised + closed-form. And OSTL's exactness holds only for shallow nets — depth reintroduces approximation, the same "depth is where it gets hard" wall we hit in SCFF.
- **What we could borrow or test:** OSTL is the *rate-based* justification for putting an eligibility trace on our future recurrent loop — we don't have to go spiking to use e-prop-style temporal credit. If/when the north-star loop is built, OSTL's shallow-exact formulation is the cheapest correct starting point (one trace per weight, instantaneous spatial error).
- **What contradicts or challenges us:** its depth-approximation caveat echoes our own — a temporal loop trained this way will likely hit a depth wall, and "cheap online exact gradient" is only really exact when shallow. Don't oversell a deep online-trained loop.

## Follow-on leads
- Bellec 2020 e-prop (sibling card) — the spiking-specialized, broadcast-signal cousin.
- Marschall, Cho & Savin 2020 "A unified framework of online learning algorithms for RNNs" — the taxonomy OSTL/e-prop/RTRL sit inside.
- Zucchet & Orvieto 2023 "Online learning of long-range dependencies" — modern RTRL approximations.
