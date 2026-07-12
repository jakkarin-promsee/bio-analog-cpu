# The Cascaded Forward Algorithm (CaFo) for Neural Network Training
- **Authors / Year / Venue:** Gongpei Zhao, Tao Wang, Yidong Li, Yi Jin, Congyan Lang, Haibin Ling / 2023 / arXiv:2303.09728 (cs.CV)
- **Link:** https://arxiv.org/abs/2303.09728 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐ — the **negative-free** branch of the family; directly speaks to our single biggest hardware-bridge risk (the LUT-streamed-negatives + softmax block).

## TL;DR
Drop FF's negative samples entirely. Structure the net as a **cascade of blocks**, each with a small locally-attached predictor that **directly outputs a label distribution** from that block's features, trained independently by a normal supervised loss (MSE / cross-entropy / sparsemax). No negatives to synthesize, no goodness threshold, and blocks train in parallel.

## The mechanism (how it actually works)
Each block `B_k` transforms features `f_{k-1} → f_k` (the feature extractor can even be fixed/random per the paper's variants). A **per-block predictor** `P_k` maps `f_k` directly to a class distribution and is trained with a standard supervised loss on that block's output alone — gradients never leave the block. Final prediction aggregates the per-block predictors (e.g. sum/ensemble of label distributions). Because there is no positive/negative contrast, there is no negative-sample generation and no `Σh²`-vs-threshold machinery — the "goodness" is just classification accuracy at each block.

## Key results / claims
On four image benchmarks (incl. MNIST, CIFAR-10) CaFo reports **improved accuracy over FF** while being cheaper (no negative pass, parallel blocks). Positioned as more efficient at both train and test than FF because it halves the passes and removes negative synthesis.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the **namer** (per-depth read-only heads, §3.1) and the negative-supply bridge (§2.4).
- **Same as us:** **per-block / per-depth predictors read locally** — our per-depth read-only heads are structurally CaFo-shaped, and our "read every block, never re-inject" (Phase 2) is the same discipline.
- **Different from us:** CaFo is **supervised at every block** (labels enter each block's predictor); our bulk is **unsupervised and label-free**, named **once** by a separate closed-form head. CaFo has **no unsupervised representation objective** — its blocks organize only by the classification signal, so it is not continual-safe by our mechanism and has no frozen-bulk story.
- **What we could borrow or test:** **the negative-free idea is the lever.** Our whole InfoNCE machinery needs negatives, and streaming them from a bounded LUT (with a softmax block that is *not* charge-native) is our sharpest open Stage-2 gate (§2.4). CaFo shows forward-only training with **zero negatives** by predicting labels per block directly. A CaFo-style distributed namer (cheap closed-form predictor per depth, no negatives) could sidestep the negative-gathering + softmax cost entirely.
- **What contradicts or challenges us:** if per-block *supervised* predictors alone reach competitive accuracy without any contrastive representation stage, it questions how much the unsupervised bulk buys on static tasks (our own Phase-11 "is it just the namer?" narrowing) — CaFo is the external version of that challenge.

## Follow-on leads
Negative-free forward training; per-block ensemble aggregation of label distributions; random/fixed feature extractors + trained local predictors (RanPAC-adjacent); sparsemax vs softmax for local heads.
