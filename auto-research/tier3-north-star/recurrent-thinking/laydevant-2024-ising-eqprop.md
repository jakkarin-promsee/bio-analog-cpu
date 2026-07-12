# Training an Ising Machine with Equilibrium Propagation
- **Authors / Year / Venue:** Jérémie Laydevant, Danijela Marković, Julie Grollier / 2024 / Nature Communications 15:3671
- **Link:** https://www.nature.com/articles/s41467-024-46879-4 (open access mirror: https://pmc.ncbi.nlm.nih.gov/articles/PMC11063034/)
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐⭐ — the hardware existence proof: a **physical machine's settle both computes and learns**, with purely local updates — EqProp off the whiteboard, onto real annealing hardware.

## TL;DR
A D-Wave Ising machine (quantum annealer) is trained as a neural network using Equilibrium Propagation: let the physical system anneal to its ground state (free phase), nudge the outputs toward the target and let it settle again (nudge phase), then update each coupling from the *local* difference in spin correlations between the two settled states. Reaches 88.8% on MNIST/100 with a 784-120-40 network — comparable to software — with learning done *by the physics*.

## The mechanism (how it actually works)
The network is an Ising energy function (spins σ, couplings J); inference = the annealer physically finding low-energy spin configurations (~20 µs anneal), with inputs applied as bias fields. Learning follows EqProp's two-phase recipe: (1) **free phase** — anneal to the ground state with only inputs clamped; (2) **nudge phase** — add a small cost-weighted bias pulling outputs toward the target, and re-settle via *reverse annealing* (start from the free solution, perturb gently, re-anneal locally — so the second settle stays in the same basin instead of being destroyed). The weight update is purely local:
`ΔJᵢⱼ ∝ −(1/β) [⟨σᵢσⱼ⟩_nudge − ⟨σᵢσⱼ⟩_free]`
— each coupling looks only at the correlation of *its own two spins* across the two settles. No backward pass exists anywhere; the "gradient" is the difference between two physical equilibria.

## Key results / claims
- MNIST/100 (downsampled): 88.8% ± 1.5 test accuracy, 784-120-40 fully-connected — on par with software EqProp training of the same net.
- Hardware embedding cost is real: ~6 physical spins per logical neuron on the Chimera graph; a compact convolutional variant got this down to ~1.6 spins/neuron.
- First supervised training of a quantum annealer as a neural network with a local, physics-executed learning rule; argues the approach suits any Ising-shaped hardware (D-Wave, but also oscillator and probabilistic-bit machines).

## How it relates to us
- **Organ / phase touched:** the north-star recurrent core's *learning rule*; the analog-realism pass; the dossier's EqProp entry, now with hardware evidence.
- **Same as us:** the whole project thesis in one demo — pay for learning with physics: the settle we get for free is also the learning signal, measured locally at each synapse (for us: at each Scap). The reverse-annealing trick answers EqProp's classic "second settle might jump basins" worry — nudge *from* the free state, gently.
- **Different from us:** binary spins vs our continuous charge (continuous-state EqProp is if anything cleaner — Kendall et al. 2020 did it in SPICE for resistive networks); an annealer with a global schedule vs our free-running relaxation; batch supervised MNIST, not a stream; no halt (fixed 20 µs anneal).
- **What we could borrow or test:** (1) when the settling loop exists in our sim, EqProp is the first candidate for training *through* it without BPTT — the sim-side version is two relaxations + a local correlation diff, directly implementable in a pNlib; (2) the nudge-from-equilibrium (reverse-anneal) protocol is the stability recipe for that experiment; (3) their spins-per-neuron embedding accounting is the honest-cost template our substrate factor claims should imitate.
- **What contradicts or challenges us:** two settles per update (time cost ×2) and a required symmetric coupling structure (Jᵢⱼ = Jⱼᵢ — for us, a reciprocity constraint on the crossbar) are the taxes; and D-Wave's scale (a few thousand usable spins after embedding) shows physical settle machines pay heavy overhead for connectivity — our crossbar is denser but the warning stands.

## Follow-on leads
- Kendall et al. 2020, "Training End-to-End Analog Neural Networks with Equilibrium Propagation" (arXiv 2006.01981) — the continuous resistive-network version (SPICE) — closest to our substrate.
- Scellier & Bengio 2017 — the EqProp root (already in dossier + survey).
- "How to Train an Oscillator Ising Machine using Equilibrium Propagation" (arXiv 2505.02103) — the same recipe on oscillator hardware.
- Yi et al. 2023, activity-difference training on memristor crossbars (Nature Electronics) — the memristive sibling.
