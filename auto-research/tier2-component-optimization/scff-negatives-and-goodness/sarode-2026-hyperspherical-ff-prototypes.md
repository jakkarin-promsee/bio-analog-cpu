# Hyperspherical Forward-Forward with Prototypical Representations (HFF)
- **Authors / Year / Venue:** Shalini Sarode, Brian Moser, Joachim Folz, Federico Raue, Tobias Nauen, Stanislav Frolov, Andreas Dengel / 2026 / arXiv:2605.00082
- **Link:** https://arxiv.org/abs/2605.00082
- **Tier / Topic:** tier2-component-optimization / t2.1 SCFF negatives & goodness
- **Relevance:** ⭐⭐⭐ — the "implicit negatives" idea in its cleanest form: fixed unit-norm prototypes act as geometric anchors *and* negatives, so the negative-data path disappears; supervised, but the anchor trick ports to our LUT.

## TL;DR
Reframes each FF layer's job from binary goodness discrimination to **multi-class classification on a hypersphere**: project the layer output onto the unit sphere and score it against **class-specific, unit-norm prototypes** that serve as geometric anchors and *implicit negatives*. No explicit negative sampling, single forward pass for update+inference, >40× faster inference than FF, and the first FF-family method with >25% top-1 on ImageNet-1k greedily (65.96% with transfer).

## The mechanism (how it actually works)
The story: FF's binary question wastes the layer's geometry (same diagnosis as Distance-Forward). HFF plants one fixed (or slowly maintained) unit-vector prototype per class on the hypersphere and asks each layer: *land your normalized output near your class's prototype*. The softmax over prototype similarities makes every other class's prototype a repeller — the **prototypes are the negatives**, permanently resident, no negative data ever constructed or fetched. Because the objective is a local multi-class score, one forward pass produces both the update signal and the class prediction (no per-class goodness sweeps as in FF inference, hence the 40× inference speedup). Depth composes because each layer refines the same prototype-alignment task in its own space.

## Key results / claims
- ">25% top-1 on ImageNet-1k" trained greedily local — a first for the FF family; 65.96% with transfer learning.
- ">40× faster" inference than original FF (single pass vs per-class goodness evaluation).
- Weight update and inference in a single forward pass; closes gaps with BP on standard benchmarks.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk negative supply; hippocampus LUT (which *already stores prototypes* for sleep-consolidation and the namer).
- **Same as us:** local, forward-only, layer-wise; resident prototype memory as a first-class organ; normalization before similarity (our `_norm`).
- **Different from us:** supervised (class-indexed prototypes); prototypes are the *whole* objective, not a supply for a contrast; hypersphere-native.
- **What we could borrow or test:** the architectural observation is the valuable part: **a resident prototype bank converts the negative-supply problem from a data-generation problem into a memory-read problem.** Our LUT already holds cluster prototypes. Label-free version: negatives for InfoNCE = the k nearest *LUT prototypes* (excluding the sample's own cluster) instead of random raw partners — resident, harder, and deduplicated by construction. This is the same lever as Distance-Forward's centroids and Robinson's hardness tilt, arriving from a third direction — three independent papers pointing at the same untested cell in our design.
- **What contradicts or challenges us:** their single-pass update+inference beats our two-rail mono-forward on pass count — a reminder that "negatives resident in memory" can be cheaper than "negatives carried on a rail."

## Follow-on leads
- NCM/prototype classifiers in our tier1 t1.5 cards (Janson 2022) — the namer-side twin of the same geometry.
- Fixed vs learned prototypes (do the anchors need to move at all? cf. fixed classifiers / ETF-geometry literature).
