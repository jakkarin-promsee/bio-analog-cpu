# Synthesis — State-space & liquid / continuous-time atoms  (Tier 4)

**The question:** which continuous-time / state-space atom is the best *recurrent atom* for the north-star loop, and which is most **analog-native** — ranked by (analog-native dynamics: RC / charge-integration) × (trainable with a gradient-free or closed-form-friendly rule) × (composes with frozen SCFF + the settling loop + a delta-rule memory)? Honest caveat carried throughout: these atoms are almost all **BPTT-trained**, which collides with our no-backprop stance.

**Already in `draft6.0/research/`:** the north-star dossier `8-atom.md` already covers **Liquid Time-Constant Networks (Hasani 2021)**, **Neural ODEs (Chen 2018)**, **KAN**, **reservoir computing (ESN/LSM)**, dendritic computation, and capsules — and concludes "pick the atom whose math is your physics → liquid / ODE / reservoir." Tier-3 `t3.1 hippocampus-organ` already holds the *memory* side: **Fast Weight Programmers / delta rule (Schlag 2021)**, **Titans**, **TTT**, **test-time regression**. This card set **extends broader/newer (2022–2026)**: the structured-SSM line (S4/S5/Mamba), the *closed-form* liquid atom (CfC), the liquid↔SSM bridge (Liquid-S4), the gated-delta memory, and — the payload — **two analog/in-memory SSM hardware demonstrations** that were missing from our library.

## The landscape (the field, in four moves)
1. **Structured SSMs (S4 → S5 → Mamba).** A deep stack of *linear* state-space recurrences `x_t = Ā x_{t-1} + B̄ u_t, y = C x_t`. With a fixed diagonal `A` (initialized from **HiPPO**, an optimal online history-compression) the recurrence is equivalently a long convolution (S4) or an associative **parallel scan** (S5) — both cheap. The linear recurrence *is a bank of leaky integrators* — per-channel exponential decay + input accumulation. **Mamba** makes the decay/projections **input-dependent** ("selective"), which buys accuracy on content-dependent tasks but breaks the cheap parallel form and needs a hardware-aware scan.

2. **Liquid / continuous-time atoms (LTC → CfC → Liquid-S4).** An LTC neuron is `dx/dt = −x/τ + f`, an RC element whose *time constant varies with the input* — the continuous-time original of "selective decay." **CfC** removes the ODE solver by a **closed-form** time-gate approximation (1–5 orders of magnitude faster). **Liquid-S4** proves the punchline: *a linear LTC is a structured SSM with input-dependent decay* — the liquid atom and the SSM atom are the same object, with "liquidness" as a knob (fixed → input-correlated → fully selective).

3. **Linear-attention / delta-rule memory (Katharopoulos → DeltaNet → Gated DeltaNet).** The same linear recurrence written as a *matrix* associative memory: read = matvec `S k`, write = outer-product **delta rule** `S += β(v − Sk)kᵀ`, forget = scalar gate `S ← αS`. Mamba-2's "state-space duality" makes SSM == linear attention formal. These are crossbar-native, error-correcting, and per-step gradient-free.

4. **Analog / in-memory SSM hardware (the new evidence).** **IMSSA** (Strachan) puts an **S4D kernel on a memristor crossbar** with analog-tailored quantization-aware training (ternary weights). **CIM-SSM** (Wei Lu, Nature Comms 2025) goes further: memristors with **short-term (volatile) memory** so the device's own decay *is* the `A` matrix — state evolution is device physics, not computed, on asynchronous event streams. These two convert "SSM = charge integration" from analogy to demonstrated silicon.

## How WE differ  ← the money section
Our substrate is a leaky-cap / charge-domain crossbar with **on-chip, forward-only, closed-form learning**. Against this landscape:

- **The forward atom is a perfect fit — and it isn't ours, it's the field's.** A diagonal linear SSM is *exactly* a leaky-cap register bank; IMSSA and CIM-SSM prove it maps to our hardware, state feedback included. The claim "the substrate's physics IS the math" is no longer speculative for the *temporal* case — someone built it. That is a huge validation and a mild deflation: the analog-native recurrent atom is a solved forward-substrate problem.
- **The training rule is where we're alone.** Every atom here (S4/S5/Mamba/CfC/Liquid-S4/Gated DeltaNet) gets its *dynamics* from **backprop through time**. Their hardware demos all follow "train off-chip, deploy on-chip." Our entire project is the opposite: learn on-chip without a backward pass. So the honest placement: **the field owns the analog recurrent atom's forward pass; the open frontier we occupy is learning it (or reading it) without BPTT.**
- **The reservoir split is our legal bridge.** north-star `8-atom.md` already named it. Combine it with this literature: take a **frozen, HiPPO-initialized diagonal SSM** as the recurrent reservoir (principled, not random — likely far above a random reservoir), let it integrate charge, and train **only our closed-form namer** on its state. No BPTT, fully substrate-legal, and it reuses the exact P7–P9 machinery we already froze.

**The recommended recurrent atom, ranked by analog-native-ness (× gradient-free-ness):**
1. **Diagonal SSM (S4D / S5-style) with fixed shared-decay `A` + our closed-form readout** — *the pick.* Most analog-native (demonstrated on memristor crossbars; CIM-SSM realizes decay in device physics), and BPTT-free if we freeze the recurrence. Real-coefficient + shared-decay (per CIM-SSM) is the version physics can hold. This drops onto our substrate with the least translation and reuses our namer.
2. **Gated delta-rule memory** — *the pick for the LUT/hippocampus half* (already t3.1's call). Crossbar-native read/write/forget, per-step gradient-free; SCFF supplies keys, namer supplies values, sleep supplies α. Caveat: the *addressing* is normally learned.
3. **CfC (closed-form liquid neuron)** — the trainable-τ upgrade *if* we ever accept a small local/gradient signal on the time constants. Closest to "RC with learnable τ," and closed-form inference suits analog; but its learned dynamics are its whole value, so a frozen CfC ≈ option 1.
4. **Mamba / Liquid-S4 (input-dependent decay)** — highest accuracy, **least** analog-native: input-dependent `A` is what the hardware papers deliberately *drop* to map to devices. Keep as the "what selectivity would buy, and what it costs the substrate" foil.

**The honest training-rule caveat, stated once:** the ranking above optimizes for *analog-native-ness*, which correlates *negatively* with published accuracy — Mamba's own ablations and Liquid-S4 both show the fixed-decay (most-analog) SSM leaves accuracy on the table versus the input-dependent (least-analog, BPTT-hungry) one. So option 1 is a bet that a **frozen-recurrence + closed-form-readout** reservoir is *good enough* on our drift/continual streams. That bet is untested and is the crux experiment.

## The gap / what we haven't tried
- **A frozen HiPPO diagonal-SSM reservoir + our P7 closed-form namer** on the Phase-11 real-drift streams (gas sensor, HAR/electric) — does a principled linear-integrator reservoir beat our current feedforward SCFF bulk on *temporal* structure, with zero BPTT? This is the single highest-leverage test.
- **The "liquidness knob" sweep** (Liquid-S4): order-0 fixed decay → order-k input-correlated, measuring accuracy vs device-state cost — find the cheapest order that still wins under drift.
- **Gated delta rule as the LUT's write/forget algebra** with *fixed* (non-learned) key/value projections — how much in-context retention survives a frozen controller?
- **Quantization-aware-training-for-analog (IMSSA)** as the template for our deferred analog-realism pass on *any* organ.
- Does our physical **settle replace the parallel scan** entirely (continuous-time integration = the scan for free)? A clean thesis probe.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [CfC — closed-form continuous-time (Hasani 2022)](hasani-2022-cfc-closed-form.md) | ⭐⭐⭐⭐⭐ | The RC-with-learnable-τ atom made **closed-form** — our namer creed on the temporal neuron. |
| [CIM-SSM — compute-in-memory SSM (Zhang/Lu 2025)](zhang-2025-cim-ssm-event.md) | ⭐⭐⭐⭐⭐ | Memristor *decay* natively realizes the SSM `A` — "the substrate's physics IS the math," demonstrated. |
| [S4 — structured state spaces (Gu 2021)](gu-2021-s4-structured-state-spaces.md) | ⭐⭐⭐⭐ | The linear-recurrence anchor; fixed HiPPO `A` = the substrate-legal frozen-reservoir path. |
| [S5 — simplified state-space layers (Smith 2022)](smith-2022-s5.md) | ⭐⭐⭐⭐ | Diagonal MIMO SSM via associative scan = the plainest leaky-cap register bank to map. |
| [Mamba — selective SSM (Gu & Dao 2023)](gu-dao-2023-mamba.md) | ⭐⭐⭐⭐ | Input-dependent decay = the liquid/gate idea; the accuracy-vs-analog-native tradeoff, sharply. |
| [Liquid-S4 (Hasani 2022)](hasani-2022-liquid-s4.md) | ⭐⭐⭐⭐ | Proves LTC == SSM-with-input-dependent-decay → collapses our atom menu to one knob. |
| [Gated DeltaNet (Yang 2024)](yang-2024-gated-deltanet.md) | ⭐⭐⭐⭐ | Crossbar-native gated delta memory (read/write/forget) — the LUT's substrate-legal write algebra. |
| [IMSSA — memristive S4D (Siegel 2024)](siegel-2024-imssa-memristive-ssm.md) | ⭐⭐⭐⭐ | First S4 on a memristor crossbar + analog-tailored QAT — the recipe for our analog-realism pass. |

## Leads spawned
- **HiPPO (Gu et al. 2020)** — the online-memory theory that makes a *fixed* `A` principled; the reservoir recipe. → short note / future card.
- **Frozen-SSM-reservoir + closed-form-namer** experiment on Phase-11 real streams → live-plan candidate (needs author's OK; north-star adjacent).
- **Mamba-2 / state-space duality (SSD)** — the formal SSM == linear-attention bridge tying this topic to t3.1.
- **Neuromorphic / event-driven SSMs** (arXiv 2404.18508) → cross-links `neuromorphic-spiking` folder.
- **Local / gradient-free learning of SSM decay & delta-gates** — the missing training rule; the real open problem for us.
- **QS4D / HPD** — quantization & robustness of SSMs on analog CIM → the analog-realism reading list.
