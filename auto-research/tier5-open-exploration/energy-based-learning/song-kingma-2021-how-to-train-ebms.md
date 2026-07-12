# How to Train Your Energy-Based Models
- **Authors / Year / Venue:** Yang Song, Diederik P. Kingma / 2021 / arXiv:2101.03288 (tutorial/review)
- **Link:** https://arxiv.org/abs/2101.03288 (fetched)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning as the unifying frame)
- **Relevance:** ⭐⭐⭐⭐ — the modern companion to LeCun 2006: it catalogues *how you actually estimate an energy surface without the partition function*, which is the mathematical menu our contrastive objective is one entry in.

## TL;DR
An EBM defines a density `p(x) = e^{-E(x)} / Z` up to the unknown normalizer `Z`. This tutorial is the field's map of **how to train `E` anyway**: (1) maximum likelihood via MCMC/Langevin sampling, (2) **score matching** (MCMC-free, match gradients of log-density), and (3) **noise-contrastive estimation** (MCMC-free, learn to discriminate data from noise). It explains how these methods connect and where each is cheap or expensive.

## The mechanism (how it actually works)
The whole difficulty is `Z`, which couples every configuration. Three escapes:

- **Maximum likelihood + MCMC.** The likelihood gradient is `∇E(data) − E_{model}[∇E]`: pull energy down on real data, push it up on *samples drawn from the model*. Since you can't sample exactly, you run **Langevin dynamics** — gradient descent on `E` plus injected Gaussian noise — to approximate model samples. This is contrastive divergence's family: a "positive phase" (data) and a "negative phase" (model fantasies).
- **Score matching.** Sidestep `Z` entirely by matching the **score** `∇_x log p(x) = −∇_x E(x)` (the normalizer vanishes under the `x`-gradient). Learn the vector field that points toward high density; no sampling loop needed.
- **Noise-contrastive estimation.** Turn density estimation into a **classification** problem: train a discriminator to separate data from a known noise distribution; the optimal discriminator recovers the energy up to a constant. This is the direct ancestor of InfoNCE.

## Key results / claims
A unifying review, not a single result. The load-bearing insight for us: **contrastive / noise-contrastive estimation and score matching are the two MCMC-free ways to learn an energy surface**, and InfoNCE-style objectives are the discriminative (NCE) branch. It also makes explicit the positive-phase / negative-phase structure of every likelihood-based EBM trainer.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** SCFF bulk objective; the negatives/LUT supply; the settling loop.
- Our SCFF training **is** the "positive phase / negative phase" of an EBM: pull energy down on the real (positive) view, push it up on the negative view. Naming our objective this way places it precisely: we are in the **NCE/InfoNCE branch**, not the Langevin-sampling branch — which is *why* we need a negative supply (the LUT) rather than an MCMC chain.
- **Langevin = our settling loop with thermal noise.** The north-star "think until it settles, with noise draws" is literally annealed Langevin descent on a learned energy — this paper is the math for it.
- Lever worth noting: **score matching** would let a future organ learn an energy *without any negatives at all* (no LUT partner) — the non-contrastive escape, at the cost of needing `∇_x` of the network.

## Follow-on leads
Score matching / denoising score matching → diffusion (Song & Ermon 2019); noise-contrastive estimation → InfoNCE lineage; contrastive divergence and its short-run-MCMC pathologies.
