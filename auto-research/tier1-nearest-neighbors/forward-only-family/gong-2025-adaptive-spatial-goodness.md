# Adaptive Spatial Goodness Encoding (ASGE): Advancing and Scaling Forward-Forward Learning Without Backpropagation
- **Authors / Year / Venue:** Qingchun Gong, Robert Bogdan Staszewski, Kai Xu / 2025 / ICASSP 2026 (arXiv:2509.12394)
- **Link:** https://arxiv.org/abs/2509.12394 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐ — the current **scaling** state-of-the-art for FF (first FF-family result on ImageNet); the ceiling our flat-vector cell is deliberately *below*.

## TL;DR
Make FF-style goodness **spatial**: compute a goodness map from each CNN layer's feature maps rather than one scalar per layer, and decouple classification complexity from channel count. Enables layer-wise supervision without backprop that scales past the small-benchmark ceiling — up to ImageNet.

## The mechanism (how it actually works)
Instead of collapsing a layer to a single `Σh²` goodness, ASGE keeps a **spatially-aware goodness representation** over the feature map, so class-discriminative spatial structure is preserved through depth. A per-layer supervised objective reads this spatial goodness (label-dependent). Three prediction strategies trade accuracy against parameters/memory for edge deployment. Training stays layer-local and backprop-free.

## Key results / claims
MNIST 99.65%, FashionMNIST 93.41%, **CIFAR-10 90.62%**, CIFAR-100 65.42%, and **ImageNet top-1 51.58% / top-5 75.23%** — reported as the first successful FF-based ImageNet result. A large jump over vanilla FF's MNIST-only regime.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the SCFF bulk (the scaling/ceiling context); the flat-vector-vs-spatial-structure boundary (§2.2 "why not CLAPP++").
- **Same as us:** forward-only, layer-local, backprop-free; per-layer objective; edge/hardware motivation; accuracy-vs-resource tradeoff heads (like our all-tap vs truncated reader).
- **Different from us:** ASGE is **supervised (label-dependent goodness), CNN-based, and exploits spatial structure** — exactly the lever our **flat-vector analog substrate lacks** (§2.2). It is also a **single learner**, not frozen-bulk + separate closed-form namer, and has no continual / drift / noise story. It scales *static* accuracy; we optimize *continual, noise-robust, on-chip* behavior.
- **What we could borrow or test:** nothing directly transferable to flat vectors, but ASGE is the honest **static-accuracy ceiling citation**: it shows how far FF-family goes *with convolution + labels*, sharpening our claim that we win off the static-accuracy axis, not on it.
- **What contradicts or challenges us:** it undercuts any implicit "FF can't scale" framing — FF *can* scale, given spatial structure and labels. Our defense is scope: we deliberately live in the structureless flat-vector, unsupervised, continual regime it does not address.

## Follow-on leads
Spatial / structured goodness encoding; FF for convolutional substrates; accuracy-parameter-memory tradeoff heads; FF at ImageNet scale and its cost.
