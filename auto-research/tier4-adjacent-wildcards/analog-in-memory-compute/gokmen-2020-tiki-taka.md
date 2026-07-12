# Algorithm for Training Neural Networks on Resistive Device Arrays (Tiki-Taka)
- **Authors / Year / Venue:** Tayfun Gokmen, Wilfried Haensch (IBM Research AI) / 2020 / Frontiers in Neuroscience 14:103
- **Link:** https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00103/full (arXiv mirror: https://arxiv.org/abs/1909.07908)
- **Tier / Topic:** tier4 / t4.1 analog in-memory compute for learning
- **Relevance:** ⭐⭐⭐⭐ — the theorem-shaped fact our math model ignores: device update asymmetry injects an *implicit extra cost term* into ANY gradient-following analog update — including, untested, our SCFF local rule.

## TL;DR
Tiki-Taka is the algorithmic escape from the RPU asymmetry spec. Key insight: an asymmetric device doesn't just add noise to SGD — it adds a systematic *implicit cost term* (each weight is dragged toward its device's zero-update fixed point), which is why plain SGD on realistic devices collapses (~15% MNIST error vs ~2%). The fix: split the weight across two arrays, W = γA + C — A absorbs the noisy gradient stream (its asymmetry now acts like a leaky integrator, mostly harmless), and C is updated sparsely from A's accumulated, sign-filtered content. Asymmetric devices + Tiki-Taka ≈ ideal devices + SGD.

## The mechanism (how it actually works)
Every real resistive device has a **symmetry point** — the one conductance where +pulse and −pulse increments happen to be equal. Away from it, updates are direction-biased. Under plain SGD this bias acts like an unwanted regularizer pulling every weight toward its symmetry point, corrupting the loss actually being minimized. Tiki-Taka's move: (1) zero-shift each A-device to its symmetry point first (alternating pulses converge it there; store that reference), so A's *systematic* bias vanishes at the origin; (2) let A integrate the raw gradient outer-products — fast, noisy, asymmetry-damped; (3) occasionally read rows of A and transfer their sign/magnitude into C with few clean pulses. C — the weight that matters — only ever sees sparse, high-SNR updates. TTv2 (Gokmen 2021, Frontiers in AI — same line) adds a digital low-pass filter between A and C, further relaxing device count and noise requirements.

## Key results / claims
- FCN on MNIST: asymmetric devices, plain SGD ~15% test error → Tiki-Taka ~2%, matching symmetric-device SGD.
- Works across LSTM / CNN benchmarks in simulation; keeps all updates O(1) in-array (no gradient readout).
- The symmetry-point-reference itself becomes the next failure mode: TTv2/c-TTv2 exist because establishing that reference precisely is hard (see Rasch 2024 card).

## How it relates to us
- **Organ / phase touched:** the SCFF bulk's per-step Scap updates; the analog-realism pass; indirectly P8.7's meter assumptions.
- **Same as us:** two-timescale split (fast noisy integrator, slow clean store) — the same architecture instinct as our awake/sleep economy, arrived at from pure device physics.
- **Different from us:** Tiki-Taka rescues *backprop*; our rule is already local and forward-only. And our Scap (capacitor) natively sits near the symmetric ideal (see Li 2018 card) — we chose the device that mostly dodges this disease.
- **What we could borrow or test:** the *diagnosis*, not the cure. The implicit-cost-term analysis applies to any incremental analog update: our SCFF contrastive rule executed as charge pulses would inherit a bias toward each cell's zero-update point. The concrete experiment for the realism pass: inject parametric update asymmetry (α_up ≠ α_down, per-cell spread) into the SCFF simulator and measure whether InfoNCE-driven clustering self-corrects or compounds. Nobody in the FF/SCFF literature has run this.
- **What contradicts or challenges us:** the paper is proof that "the update is a free primitive" is the single most dangerous assumption in analog learning — the entire mitigation industry (TT → TTv2 → c-TTv2/AGAD) exists because it is false for resistive devices. Capacitors soften but don't erase it (current-source mismatch, charge injection are the capacitor's own asymmetries).

## Follow-on leads
- Gokmen 2021 "Enabling Training of Neural Networks on Noisy Hardware" (TTv2) — the digital filter stage.
- Lee, Noh, Ji, Gokmen, Kim — "Impact of Asymmetric Weight Update on NN Training with Tiki-Taka" — the asymmetry sensitivity study.
- Wu et al. 2024 Nano Letters — Tiki-Taka run on real analog resistive devices (experimental confirmation).
- Onen et al. 2022 (ECRAM) — the device-side fix: build a symmetric device instead of an algorithmic bypass.
