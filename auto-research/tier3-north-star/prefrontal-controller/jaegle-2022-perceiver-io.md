# Perceiver IO: A General Architecture for Structured Inputs & Outputs
- **Authors / Year / Venue:** Jaegle, Borgeaud, Alayrac, Doersch, Ionescu, Ding, … Carreira (DeepMind) / 2021→2022 / ICLR 2022
- **Link:** https://arxiv.org/abs/2107.14795 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐⭐ — the engineering-native "small controller holds little, queries the rest": a tiny fixed latent array cross-attends to a huge input and to output queries.

## TL;DR
A **small, fixed-size latent array** (the workspace) is the entire working state. It **reads** a large, arbitrary input by cross-attention (input → latents), processes internally with cheap self-attention on the small latents, and **writes** outputs by cross-attention from task-specific output queries (latents → outputs). Latent size is **decoupled** from input and output size, so cost scales linearly with the input instead of quadratically.

## The mechanism (how it actually works)
Three attention operations. (1) **Encode / read**: N latent vectors (N small, e.g. 256–1024) act as queries against the M input elements (M huge) — one cross-attention collapses the whole input into the latent bottleneck. (2) **Process**: a stack of self-attention *over the N latents only* — this is where the "thinking" happens, and it costs `O(N²)`, independent of input size. (3) **Decode / write**: any output you want is produced by cross-attending an output-query array back onto the finished latents. The latent array is a bandwidth-limited buffer that never grows with the world it summarizes — you pay once to read in, think in a small space, and pay once to read out.

## Key results / claims
One architecture, no domain-specific tokenizers: beats a BERT baseline on GLUE (byte-level, no tokenization), SOTA optical flow on Sintel, plus results across audio-video-label multimodal, StarCraft II, and point clouds. Linear scaling in input size is the enabling property.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator (the latent array = the working-memory register the "prefrontal" loop holds).
- **Same as us:** this is the cleanest formalization of the whole intuition — **a controller whose size is fixed and small, that queries the big specialists rather than containing them.** The read/think/write split maps onto settle-loop + namer read. Decoupling controller size from #organs is exactly what we need for a coordinator that scales as organs are added.
- **Different from us:** every cross-attention is a **dense QK matmul trained by backprop**; on our substrate the read is a crossbar op that must be cheap/local and the routing gradient-free. Their latents are learned free parameters; ours would be a bounded register fed by frozen organs.
- **What we could borrow or test:** a **k-slot latent register that cross-attends (read-only) over the frozen SCFF taps + LUT prototypes**, self-attends a couple of steps (the "settle"), and broadcasts a bias back — the concrete first coordinator experiment.
- **What contradicts or challenges us:** the paper's power comes from *learning* the latents end-to-end; a register filled by fixed/closed-form rules may lose most of the benefit — the burden-of-proof experiment.

## Follow-on leads
- Set Transformer / inducing points (Lee 2019) — the bottleneck's ancestor; Perceiver (2021, the classification-only predecessor); Slot Attention (Locatello 2020).
