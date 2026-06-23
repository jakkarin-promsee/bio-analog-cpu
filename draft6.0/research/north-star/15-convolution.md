# 15 — Convolution + SCFF (and your Ganglion's "linear-projection collapse")

> **Tier-1.** Three questions: does convolution **work** with SCFF? **should** you use it, and **how often**? And — you revealed you already do a convolution-like move on your 2-3-3-2 Ganglion (collapse dimensions by linear projection), and you're unsure whether to keep it under SCFF+GD. Answers: **yes it works (and it's *cleaner* for SCFF than for supervised FF), use it only where the data has spatial/translation structure, and keep the collapse — it has a name (it's a pointwise/1×1 convolution) and it's a real, useful primitive.**

---

## Does convolution work with SCFF? Yes — and being *unsupervised* makes it easier for you

*Convolutional FF: Scientific Reports 2025 ([arXiv 2312.14924](https://arxiv.org/abs/2312.14924)); Channel-Wise Goodness (ESANN 2023); Adaptive Spatial Goodness Encoding ([arXiv 2509.12394](https://arxiv.org/abs/2509.12394)). And SCFF's own paper used CNNs (CIFAR-10 80.75%).*

Convolution and forward-forward/SCFF compose fine — there's a whole research line on it. The trick is **how to compute "goodness" on a feature map**: instead of one scalar per layer, you compute goodness **per spatial location and/or per channel** (e.g. mean-squared activation across channels at each pixel — "channel-wise" or "spatially-aware" goodness). The convolution does the forward pass as usual; SCFF's loss just reads its output.

**The important catch — and why it's *less* of a problem for you:** the hard part of convolutional **supervised** Forward-Forward is **label integration** — a sliding filter sees every spatial position, so the label has to be made available at *all* positions (people use Fourier/morphological label patterns to smear it across the image). **But SCFF is *unsupervised* — there is no label to integrate.** Your positives/negatives are built from the data (sample+itself vs sample+other), which works at every spatial location without any label-smearing hack. So **conv-SCFF is actually cleaner than conv-FF**: you skip the whole label-integration problem that the supervised papers wrestle with. Your unsupervised choice pays off again.

---

## What convolution *is*, deeply — the ultimate weight-sharing compression

*Why convolution works: weight sharing + locality → translation equivariance.*

Convolution is two ideas you've already met (`11-connectivity.md`, `13-compression.md`) fused: **local connectivity** (each output sees a small patch) **+ weight sharing** (the *same* small kernel is reused at *every* position). The payoff is **translation equivariance** — move the input, the output moves with it — which encodes the true fact that *a pattern means the same thing wherever it appears.* And it's **massively compressive**: a fully-connected layer on an N×N image needs ~`O(N²)` *more* parameters (and that much more data) than a convolution. One small kernel, reused everywhere, replaces a giant dense matrix.

**For us:** convolution is the **strongest form of the compression you researched in `13-14`** — it's weight-sharing taken to the limit (one kernel shared across *all* positions). On your chip that's one tiny set of weights physically reused, or a small kernel-crossbar streamed across the input. It's also the strongest *inductive bias* for the future vision plan (`16-vision.md`): it bakes in "images have local, position-independent structure" for free. So convolution isn't a separate technique — it's your compression and locality principles, specialized to spatially-structured data.

---

## Should you use it, and how often? Only where the structure is real

The honest rule: **convolution is a bet that the data has *local, translation-invariant* structure. Use it exactly when that bet is true, and not otherwise.**

- **Images / the retina front-end (`16-vision.md`): yes, essential.** This is convolution's home turf — pixels are local and patterns recur across the visual field.
- **Time-series (phase 2): yes, as 1-D convolution.** A signal has local temporal structure and patterns that recur over time — 1-D conv shares weights across time, the temporal analog. (Though `8-atom.md`'s liquid/continuous-time atoms are the deeper fit for *streaming* time.)
- **Your current draft-6 tabular/statistics tasks: probably not.** There's no spatial axis to share weights over — the input dimensions aren't "neighbors." Forcing convolution where there's no locality just throws away capacity. Grouped/local connectivity (`11`) still helps; *convolution specifically* needs a spatial structure to share over.

**How frequently / where in the stack:** the standard, and right, pattern is **convolution as the spatial front-end, then mixing/projection, then the body.** Extract local features with conv (weight-shared, cheap), mix across channels with a 1×1/projection (your collapse — below), repeat a few times, then hand the features to the SCFF+GD body. In efficient form that's exactly **depthwise-separable** (`11`): a spatial conv (local) **+** a pointwise 1×1 (channel mix) per block. So: conv wherever there's spatial structure, **always paired with a channel-mix**, not conv-everywhere.

---

## Your Ganglion "linear-projection collapse" = a 1×1 (pointwise) convolution — keep it

*1×1 / pointwise convolution; Network-in-Network (Lin et al., 2014); random projection / Johnson–Lindenstrauss.*

Here's the satisfying part. You described collapsing the Ganglion's dimensions by a **linear projection** — originally reasoned as "one axon with `n` dynamic synapses on a 3-D distance, projected down." **That move is a 1×1 (pointwise) convolution**: a *learnable linear projection across channels at each location* — it mixes channel information without touching spatial neighbors, and it's the standard tool for **dimensionality reduction, bottlenecks, and the mixing step of separable convolutions.** It's the same object as your **translate clip** (`11`) and the **channel-mix** above. You re-derived a primitive that's in essentially every modern CNN (it's the "pointwise" half of MobileNet, the bottleneck in ResNet, the "mlpconv" in Network-in-Network).

And your "3-D distance, collapse to project complexity" instinct is principled, not arbitrary: by **Johnson–Lindenstrauss**, a linear projection from high dimensions to low **approximately preserves pairwise distances** — so collapsing does *not* destroy the geometry/relationships in the synaptic input; it compresses while keeping who's-near-whom. (This is also why a *fixed random* projection works — the reservoir trick from `8-atom.md`/`10-realtime.md`.)

**So: keep it — but reframe it.** The draft-5 rationale (axon with dynamic 3-D synapses) is gone, but the **primitive survives unchanged and useful**, because under SCFF+GD a 1×1 projection is still exactly what you want between local blocks: the **cross-channel mix / bottleneck**. Don't keep it *because of the axon story*; keep it because it's the pointwise-mix that every efficient architecture needs, and it does double duty as **compression** (a bottleneck forces the low intrinsic dimension of `13`). The only question is *learned vs fixed*: learned (a 1×1 conv) for expressivity, fixed-random (JL projection) for near-zero cost — a clean experiment cell.

---

## The shape of the answer (this file)

**Does convolution work on SCFF?** Yes — compute goodness per-location/per-channel, and because SCFF is *unsupervised* you skip the label-integration headache that supervised conv-FF suffers. **What it is:** weight sharing + locality = translation equivariance = your compression principle specialized to spatial data (one kernel reused everywhere, `O(N²)` fewer params than dense). **Should you / how often:** use it **only where the data has local, translation-invariant structure** — essential for the vision front-end, useful as 1-D conv for time-series, *not* for unstructured tabular; place it as a **spatial front-end paired with a channel-mix** (= depthwise-separable), not everywhere. **Your Ganglion collapse:** it's a **1×1/pointwise convolution** — a learnable channel projection/bottleneck, the same thing as your translate clip; **keep it**, reframed as the cross-channel mix (and it's distance-preserving by Johnson–Lindenstrauss, so the collapse is principled). The draft-5 axon story retires; the primitive stays.
