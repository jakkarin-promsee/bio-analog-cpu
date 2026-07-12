# Silicon Photonic Architecture for Training Deep Neural Networks with Direct Feedback Alignment
- **Authors / Year / Venue:** Matthew J. Filipovich, Zhimu Guo, Mohammed Al-Qadasi, Bicky A. Marquez, Hugh D. Morison, Volker J. Sorger, Paul R. Prucnal, Sudip Shekhar, Bhavin J. Shastri / 2022 / Optica 9, 1323–1332
- **Link:** https://arxiv.org/abs/2111.06862 (fetched; published Optica 2022)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐⭐ — **the analog-hardware payoff of DFA, and the sharpest comparison to our substrate.** DFA is realized *in situ* on an analog photonic crossbar because its direct random projection maps to hardware in a way backprop's transpose never can. This is the "is a random backward path a good fit for an analog crossbar?" question, answered experimentally.

## TL;DR
An on-chip, CMOS-compatible silicon-photonic architecture trains neural nets with DFA. Microring-resonator arrays perform parallel matrix-vector multiplies on multi-channel analog signals, computing each layer's gradient **in situ**. It runs at **trillions of MAC/s** at **< 1 pJ/MAC**, and the authors experimentally train an MNIST net using on-chip MAC results. The reason DFA (not backprop) is used is architectural: its error feedback is a **direct, parallel broadcast**, which analog photonics can do in one shot.

## The mechanism (how it actually works)
Backprop on analog hardware is painful: it needs the **transpose** of each forward weight matrix (a second, mirror-image crossbar kept in sync) and a **sequential** backward sweep that stalls the pipeline. DFA erases both. The output error is fanned out **directly to every layer** through fixed random projections — and a fixed random projection is *cheap and static* on a photonic mesh (set the microring weights once, never update them). Each layer's update `δ_l = (B_l e) ⊙ f'(a_l)` is computed **locally and in parallel** from the broadcast error, using the same microring-resonator MAC hardware that does the forward pass. No transposed crossbar, no serialized backward chain, no update locking — which is exactly what lets the analog substrate stay fast and low-energy while *training*, not just inferring.

## Key results / claims
- **< 1 pJ/MAC**, **trillions of MAC/s** — training-capable analog photonics.
- Experimentally trained MNIST using on-chip MAC operations (proof it works with real device non-idealities, not just simulation).
- The fixed random DFA matrices are a *feature* for analog: static, never-transported weights suit a physical crossbar.

## How it relates to us
- **Organ / phase touched:** the substrate itself — the analog crossbar / compute-in-memory premise of the whole chip (`phase6-final-architecture.md §1`), and the deferred analog-realism pass.
- **Same as us:** identical top-level motivation — **the backward transpose and stored-activation chain are the analog-expensive parts, so remove them.** Both of us "pay for direction differently because the crossbar makes backprop expensive."
- **Different from us (the decisive contrast for this topic):** DFA still needs a **random backward broadcast path physically wired on the chip** (the `B_l` projections + an error fan-out network) and the **global label error**. Our SCFF needs **neither** — the update is local within a forward window, no error broadcast, no second projection network, label-free. So on a pure analog crossbar we are *strictly more local* than DFA. **But** — and this is the honest bill — DFA is **built and measured on real analog silicon**; our forward-only contrast on an analog substrate is **designed, not built** (our §2.4 "honest bridge" flags the softmax/normalizer + LUT-negative gathering as unbuilt). DFA has crossed the hardware line we have not.
- **What we could borrow or test:** their **energy accounting (pJ/MAC, MAC/s) on a real training-capable crossbar** is the yardstick our Stage-2 analog-realism pass owes. If we ever want a *supervised* fast-adapt path on the substrate, DFA-on-crossbar is the proven template.
- **What contradicts or challenges us:** it is the strongest evidence that a **random backward path is genuinely analog-cheap** — undercutting any claim that "forward-only is the *only* substrate-viable option." Our edge must be the unsupervised + continual + zero-broadcast combination, and we should concede DFA is the more hardware-mature backprop-free route *today*.

## Follow-on leads
- Reservoir DFA (Nakajima et al., Comms Physics 2024) — the random projection computed by *physical reservoir dynamics* instead of a fixed matrix.
- "Physical deep learning ... gradient-free approach for physical hardware" (Nakajima et al., Nature Comms 2022) — DFA-family training on optoelectronic hardware.
- "Streamlined optical training of large modern architectures with DFA" (PNAS 2025) — scaling optical DFA (⚠ page paywalled; verified by search only).
