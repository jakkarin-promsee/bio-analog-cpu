# Training an Ising Machine with Equilibrium Propagation
- **Authors / Year / Venue:** Jérémie Laydevant, Danijela Marković, Julie Grollier / 2024 / Nature Communications 15
- **Link:** https://www.nature.com/articles/s41467-024-46879-4 (open mirror: https://pmc.ncbi.nlm.nih.gov/articles/PMC11063034/)
- **Tier / Topic:** tier4 / t4.2 equilibrium & physics-based learning *(cross-ref: already carded from the loop side as [tier3 / t3.2](../../tier3-north-star/recurrent-thinking/laydevant-2024-ising-eqprop.md) — this card takes the physics-annealer angle)*
- **Relevance:** ⭐⭐⭐⭐⭐ — the existence proof that a physical annealer *computes and learns with the same physics*: two anneals + a local correlation difference = supervised training, on commercial hardware.

## TL;DR
Trains a D-Wave quantum-annealing Ising machine as a supervised neural network using Equilibrium Propagation. The free phase is an anneal to the ground state; the nudge phase is a **reverse anneal** that re-opens tunneling just enough to slide the ground state toward the target. Weight update = difference of spin-spin correlations between the two anneals, local to each coupler. 88.8% on MNIST/100 with a 784-120-40 fully connected net.

## The mechanism (how it actually works)
An Ising machine physically minimizes E(s) = −Σ J_ij s_i s_j − Σ h_i s_i — which is exactly the energy function EqProp needs, with couplings J as the weights and spins as the neurons. The two EqProp phases map onto two annealing schedules:

1. **Free phase = forward anneal.** Inputs enter as local fields h; the machine anneals to (near) the ground state s⁰. That ground state *is* the inference.
2. **Nudge phase = reverse anneal.** Starting from s⁰, partially re-raise the transverse field (re-enable tunneling), add a small bias on the output spins toward the target, and re-anneal. The machine lands at s^β — close to s⁰ but leaning toward the right answer. Reverse annealing is the physical realization of "perturb the equilibrium slightly": it explores only the neighborhood of the free solution instead of the whole landscape.
3. **Update.** ΔJ_ij ∝ (s_i^β s_j^β − s_i⁰ s_j⁰) — the correlation difference, measurable per coupler. Binary spins make this ±1 arithmetic.

The embedding tax is real: D-Wave's graph is not all-to-all, so one logical neuron costs ~6 physical spins (chains); a convolution-friendly embedding gets ~1.6 spins/neuron.

## Key results / claims
- MNIST/100 (1,000 train / 100 test): **88.8% ± 1.5%** test accuracy, 784-120-40 FC network — comparable to software EqProp at that scale.
- Compact convolutional network trained at ~1.6 spins/neuron: 100% on a 3×3-pixel toy set — the machine's connectivity supports convolutions.
- After training, the initially **stochastic** annealer behaves **deterministically** on inference — training sharpens the energy landscape until single-shot readout suffices.
- First supervised training of an Ising machine where the machine's own physics performs both inference and the learning measurement.

## How it relates to us
- **Organ / phase touched:** north-star recurrent loop (its learning rule); the settle-as-compute thesis.
- **Same as us:** compute is a physical relaxation; learning consumes only locally measured quantities; and their trained-stochastic-becomes-deterministic result is our "correctness as a feeling" told in energy-landscape language — a sharpened landscape is confidence.
- **Different from us:** binary spins, supervised-only, global annealing schedule control (the transverse-field sequencing is an *external digital conductor* — the two-phase choreography isn't free), and a hardware graph that taxes dense connectivity ~6×.
- **What we could borrow or test:** the merge shape for the north star: our loop already plans to settle (monDEQ-style contractive); this shows the *same settle* re-run with a small output bias yields a valid weight update from local correlation differences. The gate-fired version — nudged re-settles only when the drift gate trips — would price EqProp into our 80/20 economy instead of against it.
- **What contradicts or challenges us:** nothing head-on (different problem), but it quietly prices the loop: two anneals + readout per labeled example, plus a scheduling controller. Our current namer gets its direction for a closed-form solve with zero settles — EqProp in the loop must beat that on something (depth of credit into the loop weights, which the closed-form namer cannot touch).

## Follow-on leads
- Gower 2025, OIM + EqProp (carded here) — same rule, CMOS oscillators instead of a cryogenic annealer.
- Böhm et al., simulated-bifurcation / photonic Ising machines as the alternative annealer substrate, ⚠ not fetched here.
- Quantum EqProp: Scellier (arXiv:2406.00879), Wanjura & Marquardt (arXiv:2406.06482) — the Onsager-reciprocity generalization, ⚠ not fetched here.
