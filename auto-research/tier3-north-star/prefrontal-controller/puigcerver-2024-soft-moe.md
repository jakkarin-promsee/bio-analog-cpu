# From Sparse to Soft Mixtures of Experts (Soft MoE)
- **Authors / Year / Venue:** Puigcerver, Riquelme, Mustafa, Houlsby (Google DeepMind) / 2023→2024 / ICLR 2024
- **Link:** https://arxiv.org/abs/2308.00951 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐ — routing as *fixed slot capacity* + fully-differentiable dispatch; the "who writes which slot" question made stable, but at a density cost we must watch.

## TL;DR
Sparse MoE routing (each token hard-assigned to a top-k expert) is discrete, unstable, and load-imbalanced. Soft MoE keeps the **fixed per-expert slot capacity** but fills each slot with a **weighted combination of *all* tokens** (a soft dispatch), and reads out a weighted combine back. Fully differentiable, no token dropping, no auxiliary load-balance loss — and it beats hard-routed MoE and dense ViT at equal cost.

## The mechanism (how it actually works)
Each expert owns a fixed number of **slots**. A learned dispatch matrix scores every (token, slot) pair; each slot's input is the softmax-weighted average of all tokens (so the slot count — not the token count — sets the expert's workload). The expert processes its slots; a second combine matrix scatters slot outputs back to tokens by the transposed weights. The **slot budget is the bandwidth limit**: it is fixed regardless of how many tokens arrive, so compute is bounded and specialization is forced into a small number of channels — but note *every* token touches *every* slot through the soft weights (dense mixing), which is the opposite of local.

## Key results / claims
Soft MoE Huge/14 (128 experts × 16 layers) holds >40× the parameters of ViT-Huge/14 at **~2% more inference time** and substantially better quality; beats Tokens-Choice and Experts-Choice MoE on vision. The differentiability removes the training pathologies of hard routing.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator (slots = workspace bandwidth; dispatch = "who writes").
- **Same as us:** **fixed slot capacity as the hard bandwidth cap** is precisely our "scarcity is the feature," and the bounded-compute property is what makes it attractive on a fixed analog budget.
- **Different from us:** the soft dispatch is a **dense all-tokens→all-slots weighting** learned by backprop — expensive and non-local, the wrong shape for a crossbar that wants *sparse local* routing. It buys stability by giving up sparsity, which is the property we most want.
- **What we could borrow or test:** the **slot abstraction** (a fixed small number of write channels) as the workspace size; but keep our routing *hard and local* (Expert-Choice-style), using Soft MoE only as the stability baseline to beat.
- **What contradicts or challenges us:** Soft MoE's evidence says hard routing is unstable — a warning that our gradient-free hard write-gate may be the harder path, and needs a stability story.

## Follow-on leads
- Expert-Choice routing (this folder); DeepSeekMoE 2024 (fine-grained + shared experts); Switch Transformer (Fedus 2021, the hard-routing anchor).
