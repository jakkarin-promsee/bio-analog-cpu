# Convolutional Channel-wise Competitive Learning for the Forward-Forward Algorithm (CwComp)
- **Authors / Year / Venue:** Andreas Papachristodoulou, Christos Kyrkou, Stelios Timotheou, Theocharis Theocharides / AAAI 2024 (arXiv Dec 2023)
- **Link:** https://arxiv.org/abs/2312.12668 (code: https://github.com/andreaspapac/CwComp)
- **Tier / Topic:** tier2-component-optimization / t2.1 SCFF negatives & goodness
- **Relevance:** ⭐⭐⭐ — a peer-reviewed proof that FF's negative-data construction can be **eliminated** by intra-layer competition; supervised, so it doesn't drop into our label-free bulk, but the single-pass property is the hardware headline.

## TL;DR
Replaces FF's positive/negative two-pass goodness with **channel-wise competitive learning**: convolutional channel groups compete to claim a sample, and a layer-wise CwC loss makes the correct group's goodness win — so **both positive and negative goodness come out of one forward pass on real data only**; no negative-data synthesis. With a channel-wise feature separator/extractor (CFSE) block: MNIST 0.58% error, CIFAR-10 21.89%, CIFAR-100 48.77% — at the time, the strongest FF-family CNN results, converging notably faster than FF.

## The mechanism (how it actually works)
The story: FF needs a "fake world" to push against. CwComp observes that if a layer's channels are partitioned into class-indexed groups, then for any real sample the *wrong-class channel groups* are already a built-in fake world. The CwC loss scores each channel group's goodness (activation energy of that group) and applies a competitive objective: the group matching the sample's label should have high goodness, all other groups low — a softmax-like competition *across groups inside the layer*. One forward pass on one real image yields a positive signal (own group) and negative signals (all other groups) simultaneously. The CFSE block structures the conv features so groups stay separable. Learning stays local per layer; there is no backward path and no second corrupted pass.

## Key results / claims
- MNIST 0.58% / Fashion-MNIST 7.69% / CIFAR-10 21.89% / CIFAR-100 48.77% test error; significantly faster convergence than FF baselines.
- Eliminates negative-data construction entirely; bridges much of the FF↔BP gap on small CNN benchmarks.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (negative supply); mono-forward dual-rail (this deletes the second rail's *data* requirement).
- **Same as us:** local, forward-only, layer-wise, energy-shaped per-group goodness.
- **Different from us:** **supervised at every layer** — channel groups are class-indexed, so labels drive the competition; our bulk is label-free by commitment. Also conv-native (channel groups), we are flat/crossbar.
- **What we could borrow or test:** the label-free transplant is **unit-group competition without class indexing** — partition each SCFF layer's units into k groups and make groups compete for samples (a winner-take-most across groups), which is classic competitive learning folded into a goodness form. That deletes negatives *and* labels, at the risk of re-incurring our density≠class trap (P2's exp0 lesson: unsupervised competition clusters by density). The honest test: group-competition goodness vs InfoNCE on the checkerboard gate task first.
- **What contradicts or challenges us:** their success confirms the field keeps escaping negative-generation via labels — strengthening the case that the genuinely open problem (and our niche) is negative-free *and* label-free, where VICReg-style statistics or SCFF-style self-contrast are the only current answers.

## Follow-on leads
- "Scalable Forward-Forward Algorithm" (arXiv 2501.03176) — cites CwC/CwComp lineage, FF depth scaling.
- SoftHebb (already in curated phase3 set) — the unsupervised competitive antecedent; the density≠class risk documented.
