# Titans: Learning to Memorize at Test Time

- **Authors / Year / Venue:** Ali Behrouz, Peilin Zhong, Vahab Mirrokni / 2024–2025 / arXiv 2501.00663 (Google Research)
- **Link:** https://arxiv.org/abs/2501.00663 — fetched (HTML v1)
- **Tier / Topic:** tier3 / t3.1 hippocampus organ
- **Relevance:** ⭐⭐⭐⭐⭐ — The **north-star shape** of the hippocampus organ: a long-term memory that is a small neural net which *keeps learning at test time*, written by a surprise signal, forgotten by a gate — the recurrent learning-memory we said we want, spelled out.

## TL;DR
Titans adds a **neural long-term memory module** alongside attention: attention is precise short-term memory (limited context), the module is a persistent long-term memory whose *weights are updated online at test time* by how surprising each token is. Surprise = the gradient of an associative-memory loss `||M(k) − v||²`; the write uses momentum (surprise carried across time) and a learned **forgetting gate** (weight decay). It scales to 2M-token context and beats Transformers/Mamba on needle-in-haystack and long-document reasoning.

## The mechanism (how it actually works)
The memory `M` is a deep MLP that learns a key→value map. At each step it forms a key `k_t` and value `v_t` (linear projections of the input) and measures **surprise** as the gradient of the associative loss `ℓ = ||M(k_t) − v_t||²` w.r.t. M's weights — big gradient = "this didn't fit what I already know" = memorable. The weight update is deliberately built like an optimiser:
- **Momentary surprise** `−θ_t ∇ℓ` (this token's error),
- **Past surprise** `η_t S_{t−1}` (a decaying accumulation → momentum, so a surprising *event* keeps writing for a few steps, not just one token),
- **Forgetting gate** `(1 − α_t)` multiplying the retained memory — a data-dependent weight decay: `α_t→0` keeps everything, `α_t→1` wipes the memory. This is literally "mini-batch SGD with momentum and weight decay," but as the *inference-time* memory dynamics.

Training is parallelised by chunking the sequence and expressing the mini-batch updates as matmuls + a parallel associative scan, so the "learn at test time" loop is not slow. Three ways to wire it in: **MAC** (Memory as Context — retrieve memory tokens, prepend them, then attend), **MAG** (Memory as Gate — gate long-term memory against sliding-window attention), **MAL** (Memory as Layer — stack the memory before attention).

## Key results / claims
- Scales to **>2M context** with sustained needle-in-haystack accuracy where Transformers/linear-RNNs collapse.
- MAC variant outperforms GPT-4 on the BABILong long-reasoning benchmark with ~70× fewer parameters (paper's claim).
- Competitive-or-better than Mamba/GLA/Transformers at 340M–760M scale on LM + commonsense; throughput scales ~linearly in sequence length.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** hippocampus-LUT (its full grown-up form) · drift/error gate (P8 DDM) · sleep/forgetting · north-star recurrent loop.
- **Same as us:** the design *rhymes* with ours at every joint — a separate long-term memory from the compute; a **surprise/error signal** deciding when to write (our DDM gate fires on error-EMA); an explicit **forgetting** control (our sleep + eviction). It confirms the architecture we sketched is the field's current frontier, from an engineering (not neuroscience) source.
- **Different from us:** the memory here is an MLP updated by **gradient descent at test time** — a backward pass into the memory module every step. That is exactly the expensive thing our whole project refuses. Our namer is closed-form; our bulk is forward-only. Titans is the *target behaviour*, but its literal mechanism is not substrate-native for us.
- **What we could borrow or test:** the **surprise = write-gate** formulation is directly reusable — replace Titans' gradient-surprise with our closed-form retrieval error `(v − Wk)` (the delta-rule signal), and the momentum + forgetting-gate become a leaky accumulator on the write strength (analog-native: an RC decay). I.e. build "Titans with a delta-rule memory instead of an SGD-MLP memory" — same surprise/momentum/forget skeleton, no backward pass. The MAC wiring (retrieve → prepend as context → let the controller attend) is the concrete template for the prefrontal↔hippocampus recall loop.
- **What contradicts or challenges us:** Titans shows the *big* wins (2M context, long reasoning) come from a **deep, gradient-trained** memory. If our closed-form/delta-rule substitute can't match that depth, we inherit the same P4/P11 "continual-not-static, great-memory-shallow-reasoning" ceiling at the memory organ too. The honest open question: how much of Titans' win survives when the memory is forced to be gradient-free.

## Follow-on leads
- Behrouz et al. 2025 "It's All Connected" / ATLAS / Miras — the Titans authors' follow-ups generalising the surprise/memory framework.
- DeltaNet / gated-DeltaNet (Yang et al. 2024) — the closed-form-write cousin that may be the substrate-legal Titans.
- BABILong benchmark — the long-context evaluation we could borrow for a recurrent-loop test.
