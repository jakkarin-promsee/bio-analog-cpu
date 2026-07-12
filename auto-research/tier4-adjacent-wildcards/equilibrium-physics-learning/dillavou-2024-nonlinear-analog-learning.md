# Machine Learning Without a Processor: Emergent Learning in a Nonlinear Analog Network
- **Authors / Year / Venue:** Sam Dillavou, Benjamin D. Beyer, Menachem Stern, Andrea J. Liu, Marc Z. Miskin, Douglas J. Durian / 2024 / PNAS 121, e2319718121
- **Link:** https://www.pnas.org/doi/10.1073/pnas.2319718121 (arXiv mirror: https://arxiv.org/abs/2311.00537)
- **Tier / Topic:** tier4 / t4.2 equilibrium & physics-based learning
- **Relevance:** ⭐⭐⭐⭐ — a self-adjusting transistor network that learns nonlinear tasks with **no processor anywhere**: coupled learning (EqProp's circuit cousin) running as pure electronics.

## TL;DR
A Contrastive Local Learning Network (CLLN): a network of transistor-based self-adjusting nonlinear resistors that learns XOR and nonlinear regression entirely in analog — no digital computer computes the updates. Each edge updates itself from the local voltage difference between two electrical states (free vs clamped), trains in seconds, infers in microseconds, dissipates picojoules per transistor.

## The mechanism (how it actually works)
The network is a resistor mesh where each edge is an N-MOSFET acting as a *variable nonlinear resistor* whose effective conductance is set by a stored gate charge. Physics does inference: apply inputs as boundary voltages and Kirchhoff's laws settle the node voltages — the network's electrical steady state minimizes dissipated power (co-content for nonlinear elements), so **settling is the forward pass**. Learning is **coupled learning**, the circuit-native sibling of EqProp: run the free state (inputs only) and the clamped state (outputs pulled toward targets); each edge measures the difference of its *own* voltage drop between the two states and nudges its own gate charge accordingly. No edge knows the network topology, the task, or any other edge's state — the update is strictly two-terminal-local plus one global free/clamped phase bit. The nonlinearity of the transistor elements is what lifts it past the earlier linear-resistor versions: XOR and curved regressions become reachable.

## Key results / claims
- Learns tasks **impossible for linear systems** (XOR, nonlinear regression) with no processor in the loop.
- Exhibits **spectral bias** like ANNs — error modes reduced in order (mean, then slope, then curvature): gradient-descent phenomenology emerging from pure circuit dynamics.
- Retrainable in seconds; inference in microseconds; **~picojoules per transistor** per operation.
- Scalable in principle: the unit cell is standard CMOS-compatible parts.

## How it relates to us
- **Organ / phase touched:** the substrate premise (analog physics as the compute *and* the learner); the analog-realism pass; north-star loop.
- **Same as us:** weights are resident analog state (gate charge ≈ our Scap charge); learning is a local measured difference; the forward pass is free because it is physics. Their spectral-bias result says circuit learners inherit deep-learning's learning-order phenomenology — our math-model results should transfer to circuit dynamics more faithfully than a skeptic would guess.
- **Different from us:** supervised (clamped phase needs targets), two-phase choreography (a global phase toggle), flow-network topology rather than layered crossbar, and no representation learning — it learns input→output functions, not features.
- **What we could borrow or test:** the two-terminal-local update as the realism bar for our own rule: SCFF's update should be audited edge-by-edge the way CLLN edges are — what exactly must each Scap cell *measure*, and is it two-terminal? Their power-minimization framing also gives the loop's settle a circuit-level Lyapunov story for the analog-realism pass.
- **What contradicts or challenges us:** demonstrates that the supervised-contrastive route reaches *working hardware today* with fewer ideas than ours — the honest cost of our richer architecture (bulk + namer + gate + sleep) is that no one has built it; CLLN is the simplicity pole we should be able to justify our complexity against, task by task.

## Follow-on leads
- Dillavou et al. 2022, "Demonstration of decentralized physics-driven learning" (arXiv:2108.00275) — the linear predecessor, ⚠ not fetched here.
- "Unsupervised and probabilistic learning with Contrastive Local Learning Networks: the Restricted Kirchhoff Machine" (PNAS 2026; arXiv:2509.15842) — CLLNs go *label-free* (an RBM-like circuit) — directly our regime, strong candidate for a future card, ⚠ not fetched here.
- Stern & Murugan 2023 review (carded here) — the field this sits in.
