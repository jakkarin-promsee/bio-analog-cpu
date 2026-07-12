# Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet
- **Authors / Year / Venue:** Adly Templeton, Tom Conerly, Jonathan Marcus, … Tom Henighan, Christopher Olah (Anthropic) / 2024 / Transformer Circuits Thread
- **Link:** https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐ — the empirical proof that superposition is real in a production model, and the *instrument* (sparse dictionary learning) for measuring how many features a bulk actually holds.

## TL;DR
A **sparse autoencoder** trained on the residual-stream activations of a real production LLM (Claude 3 Sonnet) recovers **millions of monosemantic, interpretable features** as an overcomplete, sparse dictionary — turning the toy superposition claim into a measurement on a state-of-the-art network. The features are sparse, causal (steering them changes behavior), and generalize across languages and modalities.

## The mechanism (how it actually works)
Superposition says the network packs `k` features into `n < k` neurons as overlapping directions, so no single neuron is a clean feature. To *read them back out*, train a wide sparse autoencoder (dictionary learning): map the `n`-dim activation into a much larger (millions-wide) hidden layer with an L1 sparsity penalty, so each activation is reconstructed as a sparse sum of a few **dictionary atoms**. Each atom turns out to be a human-interpretable feature (the Golden Gate Bridge, sycophancy, code errors, an abstract concept). The dictionary is **overcomplete** — far more atoms than neurons — which is exactly what you need if the neurons hold features in superposition. Scaling laws guide the autoencoder size; up to ~34M features were trained on the middle-layer residual stream. **Feature steering** (clamping an atom's activation) causally changes outputs, confirming the atoms are real computational features, not post-hoc labels.

## Key results / claims
- Sparse autoencoders **scale** from a 1-layer toy to a production transformer — the method does not break at scale.
- Recovered features are sparse, monosemantic, multilingual, multimodal, and abstract; many are safety-relevant (deception, bias, dangerous content).
- Direct evidence that the model stores **far more features than neurons** — superposition confirmed empirically, not just in toys.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (as a feature store), the spare-capacity hypothesis, measurement/diagnostics.
- **Same as us:** confirms the premise our whole spare-capacity bet rests on — real networks store more features than neurons via sparse superposition. If it holds for a frozen residual stream, it plausibly holds for our frozen SCFF bulk.
- **Different from us:** they read features out of a *trained transformer* for interpretability/safety; we would read them to *count capacity* and to check that our sparse bulk actually superposes rather than wastes neurons.
- **What we could borrow or test:** train a small sparse autoencoder (a closed-form or ridge dictionary — no backprop needed if we use a random-projection + L1 solve) on our frozen bulk's activations and **count the interpretable feature dictionary size**. That number *is* an operational measure of "spare capacity used" — the missing measurement in P11's half-confirmation of the hypothesis.
- **What contradicts or challenges us:** dictionary learning needs enough data and a genuinely sparse code to recover clean atoms; on our short, drifting, autocorrelated streams the recovered dictionary may be muddy — the same regime where the bulk FLOORS.

## Follow-on leads
- Elhage 2022 / Henighan 2023 — the theory this measures.
- Sparse-autoencoder / dictionary-learning methods with closed-form or forward-only solvers (substrate-legal variants).
- "Feature absorption / feature splitting" follow-ups — how dictionary size interacts with true feature count.
