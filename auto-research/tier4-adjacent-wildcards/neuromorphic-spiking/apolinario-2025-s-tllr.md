# S-TLLR: STDP-inspired Temporal Local Learning Rule for Spiking Neural Networks
- **Authors / Year / Venue:** Marco Paul E. Apolinario, Kaushik Roy / 2023 (v1), accepted 2024 / Transactions on Machine Learning Research (TMLR) 2025
- **Link:** https://arxiv.org/abs/2306.15220
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐ — a *local* three-factor temporal rule with time-step-independent memory, tested on real event-based tasks incl. optical flow; the concrete "cheap online temporal learning for edge hardware" point on the map, and a good sparring partner for our leaky-cap trace.

## TL;DR
S-TLLR trains SNNs on event-based tasks with a **three-factor local rule** whose eligibility trace uses **both causal and non-causal** pre/post timing (unlike STDP's causal-only). Memory and compute are **independent of the number of time steps**, giving 5–50× memory and 1.3–6.6× MAC reductions vs BPTT at comparable accuracy — designed explicitly for low-power edge/online learning.

## The mechanism (how it actually works)
Classic STDP only rewards *causal* order (pre-before-post). S-TLLR argues that for gradient-approximating learning you also want the *non-causal* contribution (post-before-pre), so it builds an eligibility trace that captures both directions of pre/post temporal correlation. Each step: update a per-synapse instantaneous eligibility trace from local pre/post activity, then modulate it by a **third factor = a learning signal** (a broadcast error-like term) to produce the weight change. Because the trace is *instantaneous* (a running register, not a stored T-length history), memory and multiply-accumulates don't grow with the number of time steps — the property that makes it edge-deployable.

## Key results / claims
- Tested across **image + gesture recognition, audio classification, and optical-flow estimation** (event-based) — the optical-flow case is notable (a regression/temporal task, not just classification).
- Accuracy comparable to BPTT.
- **Memory 5–50× lower, MACs 1.3–6.6× lower** than BPTT; cost independent of time steps.

## How it relates to us
- **Organ / phase touched:** north-star temporal loop; the eligibility-register primitive.
- **Same as us:** instantaneous trace (leaky register) + broadcast third factor = our substrate's cheap primitive + a global modulator. The "make cost independent of history length" goal is exactly our "no stored history" constraint. Its causal+non-causal trace is a reminder that *direction of correlation* is a design knob — resonant with our chronic sign/direction paranoia.
- **Different from us:** still surrogate-gradient (the third factor is an error-like learning signal driving per-synapse updates); still spiking + time axis. Ours is closed-form namer, no per-synapse direction in the bulk.
- **What we could borrow or test:** the *causal/non-causal* trace idea is a concrete lever *if* the north-star loop needs bidirectional temporal credit — it's a cheap way to add a second trace register. And S-TLLR is a good baseline to *position against*: same edge-online problem, but it keeps a gradient; we'd argue closed-form + gate beats it on convergence speed and stability.
- **What contradicts or challenges us:** it shows an eligibility-trace local rule already scales to real temporal regression (optical flow) on edge budgets — so "temporal online learning on tiny hardware" is a solved-enough neighbor. Our temporal-loop claim has to add something beyond "we can learn on a stream cheaply", because they can too.

## Follow-on leads
- Apolinario, Roy et al. — follow-up local-rule work from the Purdue (Kaushik Roy) group.
- "NeuroTrain: Surveying Local Learning Rules for SNNs with an Open Benchmark" (arXiv 2605.15058) — the benchmark that ranks S-TLLR/e-prop/OTTT head-to-head (⚠ recent, fetch before citing).
- Optical-flow-on-events (EV-FlowNet lineage) — the temporal-regression task type our loop might target.
