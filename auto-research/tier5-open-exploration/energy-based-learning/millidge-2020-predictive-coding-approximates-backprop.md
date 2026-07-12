# Predictive Coding Approximates Backprop along Arbitrary Computation Graphs
- **Authors / Year / Venue:** Beren Millidge, Alexander Tschantz, Christopher L. Buckley / 2020 (arXiv) → 2022 *Neural Computation* / arXiv:2006.04182
- **Link:** https://arxiv.org/abs/2006.04182 (fetched)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning as the unifying frame)
- **Relevance:** ⭐⭐⭐⭐ — the cleanest proof that "descend an energy with *local* rules" can recover the *exact* gradient of backprop. It is the bridge between the energy frame and the local-learning family our chip lives in.

## TL;DR
Predictive coding minimizes a single scalar **prediction-error energy** by local message passing, with no backward pass and no weight transport. This paper proves that as those local dynamics settle, the resulting weight updates **converge to exact backpropagation gradients** — on arbitrary computation graphs (MLPs, CNNs, RNNs, LSTMs), not just simple stacks.

## The mechanism (how it actually works)
A predictive-coding network attaches to every layer a set of **value nodes** and **error nodes**. Each layer *predicts* the activity of the next; the mismatch is a local **prediction error** `ε`. The global objective is one energy `F = Σ ‖ε‖²` — the total squared prediction error. The network runs an **inference phase**: value nodes relax by gradient descent on `F` until the errors settle to a fixed point (this is the "roll downhill" — a physical relaxation). Then each weight updates by a purely **local Hebbian** product of a presynaptic value and a postsynaptic error — information both endpoints already hold.

The result: at the relaxed fixed point, the local error signals carried by the error nodes **equal the backprop error signals** that would flow down the reverse graph. So the same numbers backprop computes by an explicit backward sweep, predictive coding computes by *letting an energy settle*. The paper extends this from feedforward nets to any differentiable graph, giving PC-CNNs, PC-RNNs, PC-LSTMs at ≈ backprop accuracy.

## Key results / claims
Predictive coding "converges asymptotically (and in practice rapidly) to exact backprop gradients on arbitrary computation graphs using only local learning rules." Empirically matches backprop on standard benchmarks with local + Hebbian plasticity only. Positions energy-minimizing local inference as a *general* substitute for the backward pass, not a toy for MLPs.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the settling loop; the "direction is the expensive thing" thesis (draft-6 core); the feedback-alignment / local-learning neighborhood (tier1 t1.6).
- It is the **counter-example to our own framing** worth holding honestly: we say backprop's *direction* is the one expensive thing we pay for once. PC says a **physical settle can manufacture that direction locally, for free** — no LUT, no closed-form namer, just relaxation. If true at our scale, it is a rival route to "on-chip credit without a backward pass."
- The cost it hides is exactly what our project chose against: PC needs an **iterative inference relaxation to convergence for every update** (many settle-steps per sample) and error-node hardware everywhere. Our bet is that a *frozen* energy bulk + a cheap closed-form namer is cheaper than settling-to-gradient every step. This paper sets the bar that bet must clear.
- Frame to keep: **backprop is not the opposite of energy descent — backprop is one way to read the gradient of an energy that has settled.**

## Follow-on leads
Equilibrium Propagation (already in tier4 t4.2) as the energy-based cousin with a cleaner two-phase rule; the convergence-speed / depth cost of PC inference; predictive coding as generative model (free-energy principle).
