# Compute-in-Memory Implementation of State Space Models for Event Sequence Processing

- **Authors / Year / Venue:** X. Zhang, M. Hu, S. Lu, S. Kim, E. Y.-J. Lee, Y. Liu, W. D. Lu / 2025 / Nature Communications (also arXiv:2511.13912)
- **Link:** https://arxiv.org/abs/2511.13912 (journal: https://www.nature.com/articles/s41467-025-68227-w)
- **Tier / Topic:** tier4 / t4.4 state-space & liquid atoms
- **Relevance:** ⭐⭐⭐⭐⭐ — the existence proof for our whole thesis: an SSM whose **state decay is realized by device physics**, not computed. "The substrate's physics IS the math."

## TL;DR
An SSM state update is `x_t = A x_{t-1} + B u_t` — a leaky integrator per channel. This work maps that onto a **memristor crossbar** where the memristors have **short-term (volatile) memory**: the device's own exponential decay *is* the diagonal `A` matrix. State evolution happens for free as charge decays in the device; no digital recurrence loop. Co-designed algorithm + hardware for asynchronous event-based vision/audio, claiming high accuracy at high energy efficiency.

## The mechanism (how it actually works)
Modern diagonal SSMs (S4D/S5-style) keep a state vector that each step decays by a per-channel constant and adds the new input. The trick here: pick a memristor whose conductance *spontaneously relaxes* with a characteristic time constant. Write the input as a pulse; the device integrates and then leaks — exactly `x_t = a·x_{t-1} + b·u_t` with `a = e^{−Δt/τ_device}`. Because the decay is intrinsic, the "recurrence" is not iterated in a controller — it is the passage of time in the array. To make this mappable they **re-parameterize the SSM to real-valued coefficients with shared decay constants** (complex eigenvalues and per-channel arbitrary decays are hard to program into physical devices), then diagonalize so each crossbar column is one independent leaky line. Readout `y = C x` is the usual crossbar matvec. Fully asynchronous: events arrive when they arrive, and the state is always physically current.

## Key results / claims
- First native CIM realization where memristor short-term-memory dynamics *implement* the SSM state transition (not emulate it).
- Event-based vision and audio tasks; high accuracy with high energy efficiency and asynchronous/event-driven operation.
- The real-coefficient + shared-decay re-parameterization is the enabling algorithm–hardware co-design move.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the analog substrate itself; the north-star recurrent atom; validates "compute-in-memory / leaky-cap" as more than metaphor.
- **Same as us:** this is our chip's core claim, shipped by someone else for the *temporal* case — resident-weight, compute-in-memory, and the physical element (a leaky charge store) *being* the math operator. Their "shared decay constant" is our "leaky cap with a set τ."
- **Different from us:** they run a fixed pre-trained SSM (weights trained off-chip by backprop) and program it in; there is **no on-chip learning**. We are the on-chip-learning substrate. So they prove the *forward substrate* is analog-native; they do not touch the training-rule question that is our whole project.
- **What we could borrow or test:** adopt the **real-coefficient, shared-decay diagonal SSM** as the concrete recurrent atom for our loop — it is the version physics can hold. Pair it with our closed-form namer as the trained part (reservoir split), so the recurrence is frozen device-physics and only the readout learns. Their re-parameterization is a ready recipe for "SSM that a leaky-cap array can actually store."
- **What contradicts or challenges us:** it also shows the community's route is *train off-chip, deploy on-chip*. If we insist on learning the recurrence *on*-chip, we're past where the hardware literature currently lands — a real, honest frontier.

## Follow-on leads
- IMSSA (Siegel 2024) — the memristive S4D sibling with quantization-aware training (own card).
- Device physics: which memristor/leaky-cap time constants are programmable, and their spread (PVT for the analog-realism pass).
- Spiking/neuromorphic SSMs (adjacent `neuromorphic-spiking` folder) — event-driven SSMs overlap.
