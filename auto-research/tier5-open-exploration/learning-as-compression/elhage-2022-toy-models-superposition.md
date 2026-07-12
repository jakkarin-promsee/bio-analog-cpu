# Toy Models of Superposition
- **Authors / Year / Venue:** Nelson Elhage, Tristan Hume, Catherine Olsson, Nicholas Schiefer, Tom Henighan, … Christopher Olah (Anthropic) / 2022 / Transformer Circuits Thread
- **Link:** https://transformer-circuits.pub/2022/toy_model/index.html (also arXiv:2209.10652)
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐⭐ — the rigorous form of our "spare-capacity shared across tasks"; sparsity is the precondition, and sparsity is our committed substrate property.

## TL;DR
When features are **sparse** (few active at once), a network represents **more features than it has neurons** by storing them as **almost-orthogonal directions** that share the same neurons. A neuron is not one feature or dead — it carries a *blend* that only interferes when features co-activate, which sparsity makes rare. This is compression: `k` features packed into `n < k` neurons, organized into clean geometric structures.

## The mechanism (how it actually works)
Take a linear-plus-ReLU autoencoder that must reconstruct `k` input features through a bottleneck of `n < k` neurons. With **dense** features it can only keep the `n` most important and must throw the rest away (classical dimensionality reduction). But make the features **sparse** — each active only a small fraction of the time — and a phase change happens: the network starts encoding *extra* features as overlapping directions in the `n`-dim space. Because two features rarely fire together, their interference (off-diagonal dot products) rarely costs anything, so the network tolerates the overlap to gain capacity. The trade is governed by **feature importance × sparsity**: important features get near-dedicated directions; the long tail gets squeezed into shared, non-orthogonal directions. The learned geometries are strikingly clean — antipodal pairs, then **pentagons, tetrahedra**, and other uniform polytopes — the network solving a Thomson-like packing problem. Superposition also predicts **polysemantic** neurons (one neuron, several unrelated meanings) as the observable symptom.

## Key results / claims
- A sharp **phase transition** from "store one feature per neuron" to "store many in superposition" as sparsity rises.
- Capacity is a conserved, allocatable resource: the network distributes a fixed "dimensionality budget" across features by importance.
- Superposition is the reason interpretability is hard (polysemanticity) — but it is also *why* small models can do so much.
- Toy-scale only; the claim that real models do this is left to follow-ups (Henighan 2023; Templeton 2024).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (bounded-capacity store), the spare-capacity hypothesis, sparsity as a substrate property.
- **Same as us:** our author's intuition — "each neuron is used less than it can be; the slack is shareable" — *is* superposition, made rigorous. The enabling condition (sparsity) is exactly our committed substrate property; the two are the same bet from two directions.
- **Different from us:** their toy model is trained end-to-end to reconstruct known synthetic features; our SCFF bulk is a frozen unsupervised stack learned by a local contrastive rule. We never measure how much superposition our bulk actually holds.
- **What we could borrow or test:** the design implication is a rule — **don't force each Scap to be monosemantic.** Let elements carry superposed features under sparsity; that is how `k` capabilities fit in `n < k` analog cells. A concrete probe: sweep bulk sparsity and measure the effective feature-count (dictionary size) the frozen bulk supports.
- **What contradicts or challenges us:** superposition capacity depends on features being *genuinely sparse and near-orthogonal*. Our P11 autocorrelated-stream FLOOR is the failure mode — when features co-activate (temporal correlation), the interference the sparsity was hiding becomes real and the packing breaks.

## Follow-on leads
- Henighan 2023 (superposition ↔ double descent ↔ memorization) — the direct sequel.
- Templeton 2024 / sparse-autoencoder dictionary learning — the measurement instrument for "how many features does our bulk hold?"
- Feature-geometry / Thomson-problem packing under a capacity budget — a possible closed-form model of Scap allocation.
