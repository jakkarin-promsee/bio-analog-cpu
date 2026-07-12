# GRASP: A Rehearsal Policy for Efficient Online Continual Learning
- **Authors / Year / Venue:** Md Yousuf Harun, Jhair Gallardo, Junyu Chen, Christopher Kanan / 2024 / CoLLAs 2024
- **Link:** https://arxiv.org/abs/2308.13646 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule
- **Relevance:** ⭐⭐⭐⭐ — a **gradient-free**, prototype-distance rehearsal curriculum (easy→hard) that reuses class means we already store; the most substrate-friendly selection idea in this batch, though its "fewer updates" win is for *iterative* replay, not a closed-form re-fit.

## TL;DR
Don't rehearse uniformly. Replay the **most prototypical (class-mean-closest) samples first**, then gradually widen to harder (farther) samples — a curriculum. Cheap (just class-mean distances), and it hits uniform-sampling accuracy with **40% fewer updates**, beating 17 other rehearsal policies on ImageNet.

## The mechanism (how it actually works)
For each class, order its buffered samples by **distance to the class mean** in feature space: closest = prototypical/easy, farthest = atypical/hard. GRASP schedules rehearsal to draw easy samples early and progressively include harder ones (a curriculum, motivated by the claim that pure-easy or pure-hard are both suboptimal). No gradients, no extra memory — just a mean and a distance per sample. It is a **retrieval/ordering** policy (which stored samples to replay, in what order), orthogonal to which samples to *store*.

## Key results / claims
On ImageNet online CL, higher accuracy than 17 competing rehearsal policies (uniform, GSS-retrieval, MIR, etc.), and **matches uniform balanced sampling with ~40% fewer updates** — a direct compute saving. Also validated across five text-classification datasets. Overhead is negligible vs uniform.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** sleep re-fit ordering, bounded-LUT eviction (P9.3), namer prototypes.
- **Same as us:** the signal is **distance to the class prototype** — which our namer already computes (SLDA/RanPAC prototypes; the P9.4 proto-reanchor). Zero new machinery, fully gradient-free, fully on-substrate.
- **Different from us:** GRASP's payoff is a **curriculum over iterative gradient replay** (order matters when you take SGD steps). Our sleep is a **closed-form re-fit over the whole LUT** — a batch solve is order-invariant, so a replay *curriculum* buys us nothing directly.
- **What we could borrow or test:** flip GRASP from a *retrieval order* into an **eviction/retention signal**. Prototype distance ranks samples by typicality; within each CBRS class-slot, deciding *which* sample to evict by prototype-distance (keep a spread of typical + boundary samples rather than uniform-random) is a substrate-cheap upgrade to CBRS's blind within-class random eviction — directly attacks the C=20 tight-cap retention loss. This is the substrate-native reinterpretation.
- **What contradicts or challenges us:** GRASP's own finding (pure-easy and pure-hard both suboptimal) warns that a naive "keep the most prototypical" eviction would over-collapse to class means (the herding null we already found tied in P9.3) — the retention signal must keep a *spread*, not just the center.

## Follow-on leads
- MIR — Maximally Interfered Retrieval (Aljundi et al. 2019) as the interference-based retrieval alternative.
- "Watch Your Step: Optimal Retrieval for CL at Scale" (arXiv 2404.10758) — retrieval at scale.
