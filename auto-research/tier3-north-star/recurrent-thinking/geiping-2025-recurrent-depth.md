# Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach
- **Authors / Year / Venue:** Jonas Geiping, Sean McLeish, Neel Jain, John Kirchenbauer, Siddharth Singh, Brian R. Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, Tom Goldstein / 2025 / arXiv (Feb 2025)
- **Link:** https://arxiv.org/abs/2502.05171
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐⭐ — the frontier proof that "iterate a block in latent space until it stops moving" scales, **with a zero-training convergence-based halt**.

## TL;DR
A 3.5B-parameter language model whose depth is a *loop*: a recurrent block is iterated a variable number of times per token at test time, reasoning in latent space instead of emitting chain-of-thought tokens. More iterations = better reasoning (worth ~"50B parameters" of extra compute on benchmarks), and the model supports **per-token early exit by simply detecting that the latent state has converged** — no halting head was ever trained.

## The mechanism (how it actually works)
Three parts: a *prelude* embeds the input once; a *recurrent core block* is applied r times to a latent state (r sampled randomly during training, e.g. log-normal, with backprop truncated to the last few unrolls so training never pays full depth); a *coda* decodes the settled state into the output token. Thinking harder = spinning the same weights more times — no new tokens, no new parameters, small context window.

The halting result (§6.1): at inference, iterate and measure the KL divergence between the output distributions of successive latent states; **"if this divergence falls below 5×10⁻⁴, we stop iterating"** — per-token adaptive compute, zero-shot, no special training. The latent-dynamics analysis (§7) is the honest part: many tokens converge to plain fixed points, but for reasoning-heavy tokens "the state of the token quickly falls into an **orbit pattern**" (rotating trajectories in PCA space), plus "sliders" that drift directionally — the trained loop uses *dynamics*, not only equilibria.

## Key results / claims
- 3.5B params / 800B training tokens; iterating the block at test time improves reasoning benchmarks up to compute equivalent to a much larger feed-forward model.
- No specialized (CoT) training data needed; reasoning stays latent.
- Zero-shot per-token adaptive compute via KL-convergence exit; easy tokens exit early, hard tokens iterate long.
- Emergent latent structures: fixed points, orbits, sliders — context-dependent computation strategies nobody asked for.

## How it relates to us
- **Organ / phase touched:** north-star recurrent loop + the halt; the correctness-as-feeling story.
- **Same as us:** the whole thesis — depth from time over resident weights, thinking = latent iteration, stop when settled. Their KL-exit is our halt v0: "the state stopped changing" is measurable in analog as *currents stopped changing* — a comparator on successive state deltas, no learned head required.
- **Different from us:** trained by (truncated) backprop through the unrolled loop — substrate-illegal for us; and it's LLM-scale next-token prediction, not a streaming classifier.
- **What we could borrow or test:** (1) the halt v0 design — threshold on ‖Δstate‖ instead of a trained PonderNet head; they prove this works untrained; (2) the train-with-random-iteration-count trick (makes the block iteration-count-robust — cheap to copy in our sim); (3) their difficulty→iterations curve is exactly the "ponder time correlates with hardness" plot our first loop experiment should produce.
- **What contradicts or challenges us:** the **orbits**. Free trained recurrence learns non-converging dynamics that are apparently *useful* for hard reasoning — an analog substrate that physically relaxes to equilibria (and a monDEQ-style constraint that certifies it) may forbid exactly those dynamics. The open question for our loop: how much do you lose when you force every trajectory to be a settle?

## Follow-on leads
- "Path independence" in equilibrium models (Anil et al.) — when does the answer not depend on the initial state.
- Mixture-of-Recursions (arXiv 2507.10524) — router-learned per-token recursion depth (the trained-halt counterpart).
- McLeish et al. follow-ups on recurrent-depth scaling laws.
