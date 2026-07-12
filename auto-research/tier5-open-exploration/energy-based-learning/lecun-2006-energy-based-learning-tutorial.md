# A Tutorial on Energy-Based Learning
- **Authors / Year / Venue:** Yann LeCun, Sumit Chopra, Raia Hadsell, Marc'Aurelio Ranzato, Fu Jie Huang / 2006 / in *Predicting Structured Data* (Bakır, Hofmann, Schölkopf, Smola, Taskar, eds.), MIT Press
- **Link:** https://www.semanticscholar.org/paper/A-Tutorial-on-Energy-Based-Learning-LeCun-Chopra/7fc604e1a3e45cd2d2742f96d62741930a363efa (fetched; canonical PDF: yann.lecun.com/exdb/publis/pdf/lecun-06.pdf)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning as the unifying frame)
- **Relevance:** ⭐⭐⭐⭐⭐ — the single frame our whole chip instantiates: inference = descend an energy, learning = shape it. This is the theory our north-star capstone (`north-star/21-energy.md`) is built on.

## TL;DR
Define a scalar **energy** `E(x, y)` that measures the *incompatibility* of a configuration. **Inference** = clamp the observed `x`, search for the `y` that **minimizes** energy. **Learning** = push the energy of correct `(x, y)` pairs *down* and incorrect ones *up*. That is the entire program — and it subsumes discriminative models, generative models, CRFs, max-margin Markov nets, graph-transformer networks, and manifold methods as special cases.

## The mechanism (how it actually works)
The core move is to **give up on normalized probabilities**. A probabilistic model must divide by a partition function `Z = ∫ e^{-E} ` — an intractable integral over all configurations. EBMs keep only the *unnormalized* energy surface: you never need `Z` because inference and learning care only about **relative** energies (which valley is lowest), not calibrated probabilities.

Learning is choosing a **loss functional** that shapes the surface correctly. The subtlety the tutorial dwells on: a naive loss that only *lowers the energy of the right answer* can **collapse** — the model flattens the whole surface to zero energy everywhere. So the loss must also *raise* energy somewhere else. The tutorial's taxonomy of losses is exactly a taxonomy of **how you supply the "push-up"**: the negative log-likelihood pushes up *everywhere* (needs the intractable `Z`); **contrastive** losses push up on one or a few explicitly chosen "most-offending" negatives; **margin** losses push up until a gap opens; and some architectures are "energy-capped" so no push-up is needed at all. Inference itself can be a gradient descent, a relaxation, or a dynamic-programming search over the energy surface.

## Key results / claims
Not an empirical paper — a **unifying framework**. Its lasting contributions: (1) the energy/inference/learning triad; (2) the **collapse problem** and the classification of losses by how they avoid it (the "good loss must pull down the answer AND push up a contrast"); (3) showing CRFs, max-margin Markov networks, GTNs, and ratio-matching are all energy-based learners with different loss + inference choices.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the whole architecture; the north-star capstone (`21-energy.md`).
- The "no partition function, only relative energies" property is **exactly why an analog chip fits**: a physical network settling to equilibrium computes an energy minimum *for free*, and it never needs to compute `Z`. Our substrate rolls downhill; it does not integrate.
- The **collapse problem is our Phase-2 story in disguise**: SCFF's `Σh²` goodness could be driven up trivially (density, not class), so we needed a *contrastive* push-up (InfoNCE negatives) — precisely LeCun's "you must push some energy up, not just pull the answer down." Our whole negatives/LUT machinery is the "most-offending negative" of this tutorial.
- Frame to keep: **SCFF-goodness, the settling loop, and the correctness-feeling are one energy surface**, seen from three angles.

## Follow-on leads
Modern EBM training (Song & Kingma 2021); the collapse-avoidance connection to non-contrastive SSL (VICReg, BYOL); structured-output energy inference (graph-transformer networks) for a future sequence organ.
