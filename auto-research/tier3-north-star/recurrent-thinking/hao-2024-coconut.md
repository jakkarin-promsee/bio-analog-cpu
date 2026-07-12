# Training Large Language Models to Reason in a Continuous Latent Space (Coconut)
- **Authors / Year / Venue:** Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li, Zhiting Hu, Jason Weston, Yuandong Tian / 2024 (COLM 2025) / arXiv Dec 2024
- **Link:** https://arxiv.org/abs/2412.06769
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐ — the cleanest statement that reasoning's native medium is a **continuous vector fed back on itself** — i.e., the medium our substrate is made of.

## TL;DR
Coconut ("chain of continuous thought") removes the words from chain-of-thought: instead of decoding the hidden state into a token and re-reading it, the model **feeds its last hidden state directly back as the next input embedding**, reasoning in continuous latent space. The continuous thought can hold *several candidate next steps in superposition*, giving an emergent breadth-first-search behavior that beats token-CoT on planning-heavy logic tasks.

## The mechanism (how it actually works)
In token CoT the loop is: hidden state → argmax to a word → embed the word → next step; the projection to a discrete token throws away everything except the single committed choice. Coconut replaces that projection with identity: hidden state → next input, directly. Trained with a curriculum that progressively replaces written CoT steps with latent steps, so the model learns to use the unconstrained vector as a thought. Because a vector need not commit to one branch, the latent thought encodes a *distribution over alternative next steps*; the authors show the model effectively explores multiple paths in parallel and prunes late — BFS where token-CoT is forced into DFS.

## Key results / claims
- Beats token-CoT on logical reasoning tasks requiring planning/search (e.g., ProntoQA-style graph problems), with fewer inference tokens.
- The superposition effect is measurable: latent thoughts hold multiple candidate continuations simultaneously.
- Language-token reasoning is partly coherence overhead, not computation — the argument that latent space is the right home for the compute.

## How it relates to us
- **Organ / phase touched:** north-star recurrent loop (the medium argument); the LUT/hippocampus recall loop.
- **Same as us:** the feedback edge is ours: state re-entering the same machine as input, continuously — an analog voltage vector recirculating through the crossbar IS a chain of continuous thought, with zero of the digitize-re-embed overhead a token loop pays. The superposition point is substrate-flattering: continuous charge holds "several possibilities at once" natively.
- **Different from us:** a fine-tuned LLM; the number of latent steps is fixed by a training curriculum (no halt, no convergence — the loop runs a scheduled count); trained end-to-end by backprop through the latent chain.
- **What we could borrow or test:** (1) the framing for why our loop should *not* pass through the namer between think-steps (naming = the destructive argmax; think first, name once at the halt); (2) the superposition diagnostic — measure whether our settled state before naming carries more than the winning class (probe entropy along the settle trajectory); (3) the curriculum trick (replace explicit supervision steps with latent steps gradually) if we ever train a loop.
- **What contradicts or challenges us:** Coconut needed careful curriculum training to make latent steps useful — free-running feedback did not organize itself; a physical loop with no training-through-time may need its structure from somewhere else (EqProp, or the LUT pulling states toward stored attractors).

## Follow-on leads
- Zhu et al. 2025, "Reasoning by Superposition" — theory of why continuous thoughts encode parallel search.
- "Soft thinking" / training-free continuous-CoT variants (2025) — latent reasoning without the curriculum.
- LUT-as-attractor: Hopfield-style recall inside the loop (bridges to t3.1 hippocampus organ).
