# Mamba: Linear-Time Sequence Modeling with Selective State Spaces

- **Authors / Year / Venue:** A. Gu, T. Dao / 2023 / arXiv (later COLM 2024)
- **Link:** https://arxiv.org/abs/2312.00752
- **Tier / Topic:** tier4 / t4.4 state-space & liquid atoms
- **Relevance:** ⭐⭐⭐⭐ — the selective-SSM anchor; its "make the decay input-dependent" is the *liquid* idea inside an SSM, but it's exactly what breaks the cheap parallel/analog form.

## TL;DR
S4-style SSMs use **fixed** `A, B, C` across the sequence, so they can be a convolution — but that also means they can't *choose* what to remember based on content. Mamba makes `B, C` and the step size `Δ` **functions of the input** ("selective"): the state now selectively propagates or forgets per token. That input-dependence kills the convolutional form, so Mamba uses a **hardware-aware parallel scan** to stay linear-time. Matches Transformers of 2× its size at 5× throughput.

## The mechanism (how it actually works)
Take the diagonal SSM recurrence `x_t = Ā(Δ_t) x_{t-1} + B̄_t u_t`. In S4 the decay `Ā` and projections `B,C` are constants — a passive leaky-integrator bank. Mamba makes `Δ_t, B_t, C_t` small learned functions of the current input `u_t`. Now the effective time constant *varies with the input* — this is precisely the Liquid-Time-Constant idea (`τ_sys` depends on the signal), imported into the SSM world. The cost: with per-step-varying `Ā`, you can't precompute one convolution kernel. Mamba keeps it fast with a **selective scan** — an associative parallel-scan (prefix-sum) that never materializes the full state in slow memory, fused as a single GPU kernel. Trained end-to-end by backprop; inference is a constant-memory recurrence.

## Key results / claims
- Mamba-3B matches Transformers 2× its size on language; 5× higher inference throughput; linear scaling to million-length sequences.
- Strong across language, audio, genomics.
- Selectivity is the key ablation — fixed-parameter SSMs underperform on content-dependent (discrete) tasks.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star recurrent atom; the gate-like "selectively forget" mechanism echoes our drift-gate.
- **Same as us:** input-dependent forgetting *is* a gate; Mamba's `Δ_t` selecting how much to retain is conceptually our DDM drift-gate deciding when to consolidate — content deciding memory dynamics. And the base atom is still a leaky-integrator SSM.
- **Different from us:** two mismatches. (1) Selectivity makes the recurrence **input-dependent**, which is *harder* to realize in fixed analog device physics than a shared-decay SSM (the CIM-SSM card deliberately drops this to a *shared* decay to map to hardware). (2) Trained by full backprop; no local/closed-form route.
- **What we could borrow or test:** the *idea* — let the leak rate be modulated by a cheap content signal — is worth a probe, but the honest hardware lesson (from IMSSA / CIM-SSM) is that **shared, fixed decay is what the substrate can hold**; Mamba's selectivity is the feature you *give up* to be analog-native. Treat Mamba as the "why we chose a simpler SSM" foil.
- **What contradicts or challenges us:** Mamba's ablations say the *fixed*-parameter SSM (the analog-friendly one) underperforms on content-dependent tasks. So the most-analog atom may also be the least expressive on exactly the discrete/language tasks — a real ceiling for a fixed-decay substrate.

## Follow-on leads
- Mamba-2 / SSD (state-space duality with linear attention) — links SSMs to the delta-rule family (Gated DeltaNet card).
- Selective-scan on analog: HPD / QS4D robustness work for selective SSMs on CIM.
- The gate connection: does our DDM error-gate == a coarse Δ_t?
