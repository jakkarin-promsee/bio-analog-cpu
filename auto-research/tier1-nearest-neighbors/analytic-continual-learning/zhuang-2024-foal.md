# F-OAL: Forward-only Online Analytic Learning with Fast Training and Low Memory Footprint in Class Incremental Learning
- **Authors / Year / Venue:** Huiping Zhuang, Yuchen Liu, Run He, Kai Tong, Ziqian Zeng, Cen Chen, Yi Wang, Lap-Pui Chau / 2024 / NeurIPS 2024 (arXiv v1 titled "AOCIL")
- **Link:** https://arxiv.org/abs/2403.15751
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐⭐ — the family member that shares our *deployment constraints*: forward-only, online (mini-batch stream, one pass), low memory — the nearest published twin to our namer's operating point.

## TL;DR
F-OAL does online class-incremental learning (data arrives in mini-batches, seen once, no exemplars) with zero backpropagation: a frozen pre-trained encoder, a feature-fusion module pooling multiple encoder levels, and a linear classifier updated by recursive least squares. Accuracy beats exemplar-free baselines at a fraction of the time and GPU memory.

## The mechanism (how it actually works)
1. **Frozen encoder** (pre-trained ViT) — stability comes from never touching it.
2. **Feature fusion:** representations from multiple encoder layers are fused (with a smooth projection) into the feature the classifier sees — multi-depth taps, not just the last layer, to make the frozen features richer for a linear solve.
3. **RLS classifier:** per incoming mini-batch, Woodbury rank-update of the inverted autocorrelation + re-solve. One forward pass per sample, ever; the update is O(d²) matrix work, no optimizer state, no second pass.

The pitch is explicitly resource-shaped (the engineering-native framing): exemplar-free methods are cheap but weak, replay is strong but memory-hungry — F-OAL claims both sides: accuracy of the analytic solve, footprint of forward-only.

## Key results / claims
- Higher average/final accuracy than exemplar-free OCIL baselines; competitive with replay-based ones on standard benchmarks.
- Fast training and low GPU footprint (headline claim; the paper's tables quantify vs. baselines).
- NeurIPS 2024; code public (github.com/liuyuchen-cz/F-OAL).

## How it relates to us
- **Organ / phase touched:** the namer end-to-end (P7 commit → P8 economy → P9 loop); the whole "forward-only" identity of the substrate.
- **Same as us:** the constraint set is ours, item for item — forward-only (no backward pass anywhere), online single-pass stream, exemplar-light, frozen representation, closed-form head. Their feature fusion = our all-tap read (P9.2: all-tap consolidation beats truncated). This is the paper to cite when placing our namer: "the field's closest operating point."
- **Different from us:** (1) Their frozen encoder is an ImageNet ViT that never changes; our bulk is a task-trained SCFF that keeps rotating — they have no drift story at all. (2) They update on every mini-batch; we fire on a drift gate and re-fit at sleep — the economy/safety layer (P8: GD-share 0.121, gate = safety) does not exist in their world. (3) No energy/substrate costing — their "efficiency" is GPU minutes, ours is metered substrate energy (P8.7).
- **What we could borrow or test:** their smooth-projection + fusion detail is a concrete recipe to compare against our fixed-reader/all-tap choices; their benchmark protocol (OCIL, one-pass) is the external bench our namer could be dropped onto for an old-world-anchored number.
- **What contradicts or challenges us:** it compresses our novelty claim — "closed-form, forward-only, online continual naming" is published. What it leaves us: the drift-gated economy, the sleep re-fit over a bounded LUT, the rotating (not frozen) substrate, and the analog energy realization.

## Follow-on leads
- LibContinual (arXiv 2512.22029) — the 2025 realistic-CL library that benchmarks this family.
- AEF-OCL / analytic online variants for autonomous driving — the applied tail of the family.
- REMIND (Hayes et al., ECCV 2020) — the replay-side streaming counterpart at the same operating point.
