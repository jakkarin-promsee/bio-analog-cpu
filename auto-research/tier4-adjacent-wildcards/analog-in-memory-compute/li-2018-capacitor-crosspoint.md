# Capacitor-based Cross-point Array for Analog Neural Network with Record Symmetry and Linearity
- **Authors / Year / Venue:** Yulong Li, Effendi Leobandung, et al. (IBM) / 2018 / IEEE Symposium on VLSI Technology
- **Link:** https://ieeexplore.ieee.org/document/8510648/ (IEEE page verified via search; abstract/detail confirmed via https://phys.org/news/2018-07-capacitor-based-architecture-ai-hardware.html)
- **Tier / Topic:** tier4 / t4.1 analog in-memory compute for learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the direct hardware validation of our Scap: capacitor charge as the analog weight, with the best update symmetry/linearity ever measured in a cross-point array — and the honest leakage tax quantified.

## TL;DR
IBM built a cross-point array where the synaptic weight is **charge on a trench capacitor** (14 nm technology): two current-source FETs add/subtract charge, a readout FET converts stored charge to a conductance for the MVM. Because charge moves electron-by-electron rather than by filament physics, the update is continuous, near-linear, and symmetric — the *record* for any analog cross-point cell. The price is volatility: leakage bounds retention, quantified as needing τ > 10⁶ × the training cycle length (≈100 fF/cell at DRAM-class leakage).

## The mechanism (how it actually works)
The unit cell: a capacitor holds the weight as charge; its voltage gates a readout FET whose channel conductance enters the crossbar MVM; two matched current-source FETs (one to charge, one to discharge) implement ±Δw as fixed-duration current pulses. Symmetry comes for free from physics — adding a packet of charge and removing a packet of charge are the *same physical operation with opposite sign*, unlike RRAM (filament growth ≠ dissolution) or PCM (gradual crystallization vs abrupt melt-quench RESET). 8,000 alternating update pulses showed stable, repeatable conductance steps.

Leakage analysis is the honest half: a fully-connected net needs weight retention ~10⁶ training cycles for accuracy to be unaffected; conv nets relax this ~600× (weight reuse). Crucially — **while training runs, leakage doesn't matter**, because the learning loop itself continuously rewrites the weights (learning is the refresh).

## Key results / claims
- Best symmetry + linearity ever reported for an analog cross-point weight cell (vs all NVM contenders).
- MNIST training accuracy unaffected by leakage when the retention condition holds; ~100 fF/cell suffices at DRAM-level leakage.
- Fabricated with trench capacitors in a 14 nm-class process — a mainstream-CMOS answer, no exotic materials.

## How it relates to us
- **Organ / phase touched:** the Scap itself — the substrate primitive under every phase; the analog-realism pass.
- **Same as us:** this IS our weight cell. Capacitor charge = weight, readout transistor into a crossbar, incremental analog update. Independent, fabricated validation that the Scap choice is not a naive simplification — it is the *best-in-class* update device, chosen by IBM for exactly the property (symmetric update) that kills RRAM/PCM training.
- **Different from us:** their array trains backprop; and their weights are transient scratch for training runs, not a lifelong store.
- **What we could borrow or test:** the retention arithmetic. Our SCFF bulk updates every step forever — the friendly regime (learning-as-refresh means leakage is absorbed). But anything *static* on a capacitor is the hostile regime: paused streams, the frozen deploy-only mode, slow-changing weights in a converged bulk. Test: how long can our stream stall before Scap leakage (τ from this paper) degrades the bulk beyond the drift the gate can absorb?
- **What contradicts or challenges us:** unlimited endurance + symmetry come bundled with volatility. Our math model implicitly assumes Scaps hold indefinitely; this paper says the real device leaks with a time constant, and the mitigation is either continuous learning (we have it), refresh circuitry (we don't model it), or transfer to NVM (the Ambrogio 2018 mixed cell). The LUT/prototype store, which must hold across long spans, should NOT be capacitive — SRAM/NVM there is load-bearing, not incidental.

## Follow-on leads
- Ambrogio et al. 2018 (sibling card) — the system that pairs this volatile capacitor with PCM for long-term storage: the two-timescale cell.
- ECRAM (electrochemical RAM, e.g. Onen et al. 2022 Science; Nature Electronics 2023 CMOS-compatible arrays) — the nonvolatile device line chasing the same symmetry the capacitor gets natively.
- DRAM-based compute-in-memory (gain-cell) lines — the same charge-domain idea at commodity density.
