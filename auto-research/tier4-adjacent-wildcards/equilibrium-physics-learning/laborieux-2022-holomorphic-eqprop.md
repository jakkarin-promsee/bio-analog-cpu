# Holomorphic Equilibrium Propagation Computes Exact Gradients Through Finite Size Oscillations
- **Authors / Year / Venue:** Axel Laborieux, Friedemann Zenke / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2209.00530
- **Tier / Topic:** tier4 / t4.2 equilibrium & physics-based learning
- **Relevance:** ⭐⭐⭐⭐ — kills EqProp's worst constraint (infinitesimal nudge, separate phases): exact gradients from a finite *oscillating* teaching signal — a loop that learns while it hums.

## TL;DR
Extends EqProp to complex-valued network states and shows that if the nudge is applied as an **oscillation** (the teaching signal rotates through the complex plane), the exact gradient can be read out from the network's response to that oscillation — at **finite** amplitude, with no β→0 limit and no separate free/nudged phases. Matches backprop on ImageNet 32×32.

## The mechanism (how it actually works)
Vanilla EqProp estimates a derivative by a finite difference: settle at β=0, settle at β>0, subtract, divide by β. Finite differences of real functions are biased at any finite β. The holomorphic move: treat the network's equilibrium as a function of a **complex** nudge β and exploit Cauchy's integral formula — the exact derivative at β=0 equals the *average of the function around a circle* in the complex plane, not the slope between two points on the real line. Physically: drive the nudge around that circle as a continuous oscillation, average the synapse-local measurements over one period, and the finite-difference bias integrates away exactly. The two static phases become one dynamic phase; "teaching" is a small oscillating force on the outputs, and the gradient is demodulated locally at each synapse from the oscillation it induces.

## Key results / claims
- **Exact** gradients at finite teaching-signal amplitude (the bias is removed by construction, not by shrinking β).
- Gradients computed *on the fly* from neuronal oscillations — no phase bookkeeping, no stored first equilibrium.
- Scales to ImageNet 32×32 matching backprop performance — the strongest EqProp scaling datapoint of its generation.
- Gradient estimate is robust to noise (averaging over a period is a lock-in measurement — narrowband noise rejection for free).
- Deeper models benefit most from finite (larger) teaching amplitudes.

## How it relates to us
- **Organ / phase touched:** north-star recurrent loop; the analog-realism pass (measurement precision).
- **Same as us:** the analog-first instinct — replace an algorithmic limit (β→0) with a physical operation (oscillate and average), the same "pay with physics where physics is cheap" trade we run on.
- **Different from us:** still supervised, still needs an energy-based settling network with (effectively) symmetric coupling; complex-valued states are realized as oscillation phase — a different substrate dialect from our charge-on-Scap DC picture.
- **What we could borrow or test:** for the recurrent-loop organ this is the variant that removes the *phase-sequencing* controller entirely — the loop settles once while a small AC nudge rides on the output, and each synapse demodulates its own gradient (a lock-in amplifier per weight, conceptually). If we ever sim an EqProp rung, compare centered-EP (two extra settles) vs holomorphic (one settle + AC averaging) as the cheaper physical schedule.
- **What contradicts or challenges us:** weakens our "EqProp needs a settle + a nudged phase" cost argument — here the nudge phase is not a second settle but a modulation of the first. The honest cost that remains: a target must exist, and the readout integrates over oscillation periods (time, not phases).

## Follow-on leads
- Laborieux & Zenke 2023, "Improving equilibrium propagation without weight symmetry through Jacobian homeostasis" (arXiv:2309.02214) — attacks the other big constraint (W = Wᵀ), ⚠ not fetched here.
- "Training and synchronizing oscillator networks with Equilibrium Propagation" (arXiv:2504.11884) — the oscillator-native follow-on, ⚠ not fetched here.
- Lagrangian-based EqProp / Hamiltonian Echo Learning (arXiv:2506.06248) — EqProp beyond dissipative settling, ⚠ not fetched here.
