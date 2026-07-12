# The Forward-Forward Algorithm: Some Preliminary Investigations
- **Authors / Year / Venue:** Geoffrey Hinton / 2022 / arXiv:2212.13345 (cs.LG); the NeurIPS 2022 keynote writeup
- **Link:** https://arxiv.org/abs/2212.13345 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐⭐ — the root of the whole family and the direct ancestor of our SCFF frame; every card here is a delta on this.

## TL;DR
Replace the backward pass with **two forward passes** — one on positive (real) data, one on negative (fake) data — and train **every layer locally** to be "loud" (high goodness) on positives and "quiet" on negatives. No gradient ever crosses a layer boundary; no transpose, no stored activation tape.

## The mechanism (how it actually works)
Each layer has a scalar **goodness** — Hinton's default is the **sum of squared activities** `G = Σ h²` (energy). The layer's local objective is to push `G` above a threshold `θ` on a positive example and below it on a negative one, via a per-layer logistic loss on `G − θ`. Crucially each layer must **L2-normalize its output before the next layer**, or the next layer could cheat by simply reading the length of the previous activity vector. Negatives are the hard part: in the supervised MNIST demo they are made by **overwriting the label pixels with a wrong class** (so a positive = image with correct label, negative = image with wrong label). Inference picks the label whose forward pass yields the highest total goodness. An unsupervised variant makes negatives by mixing images with a random mask.

## Key results / claims
Works on small problems (MNIST ~1.4% error region, small CIFAR) "well enough to be worth further investigation." No claim of matching backprop at scale; the paper is explicitly preliminary. The pitch is **hardware/biological**: a learning rule that needs no backward connectivity, no weight transport, no activation storage, and could run on analog / low-power / mortal-computation substrates.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the SCFF bulk (the whole cheap-brain frame descends from here); mono-forward dual-rail.
- **Same as us:** forward-only, layer-local, no cross-layer credit chain, mandatory per-sample L2 norm, the positive/negative "two worlds" idea carried on our dual-rail crossbar.
- **Different from us:** (1) FF's goodness is **energy `Σh²`** — our Phase 2 proved that measures *density, not class* and does not compose with depth, so we **replaced it with InfoNCE contrast**. (2) FF's negatives are **label-derived** (supervised); ours are **label-free** (masked-view positives + in-batch/LUT negatives). (3) FF trains each layer to *classify directly*; we train the bulk to *organize*, then read it once with a **separate closed-form namer** — FF has no frozen-bulk / separate-namer split.
- **What we could borrow or test:** nothing new — this is the substrate we already extended. It anchors the family placement.
- **What contradicts or challenges us:** FF's own scaling failure (MNIST-only) is exactly the ceiling the rest of the family and our project push against; the energy-goodness dead end is our founding negative result.

## Follow-on leads
Mortal computation / analog-substrate learning (Hinton's framing); goodness-function design (SymBa, DeeperForward); label-free negative generation (SCFF, contrastive FF).
