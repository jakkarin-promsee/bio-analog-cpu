# Plasticity-Optimized Complementary Networks for Unsupervised Continual Learning (POCON)
- **Authors / Year / Venue:** Alex Gomez-Villa, Bartłomiej Twardowski, Kai Wang, Joost van de Weijer — 2024 — WACV 2024
- **Link:** https://arxiv.org/abs/2309.06086 (fetched; code: https://github.com/alviur/pocon_wacv2024)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐ — the CLS (fast-expert / slow-main) architecture arriving inside *unsupervised* CL — our two-timescale instinct, reproduced by the SSL community for the bulk itself.

## TL;DR
CaSSLe-style regularized CSSL under-adapts on long task sequences (low plasticity) or forgets. POCON splits the learner: a **fast expert** does pure SSL on the current task with zero forgetting constraints (full plasticity), then an **adaptation-retrospection** phase distills the expert *and* the old main network into the **slow main network** — exemplar-free, no replay buffer. Wins over exemplar-free CURL baselines especially on many-task streams.

## The mechanism (how it actually works)
The stability-plasticity dilemma is resolved by refusing to make one network do both. The expert is throwaway: initialized fresh (or from the main), it chases the current distribution with an unconstrained SSL loss — maximal plasticity because nothing asks it to remember. Consolidation is a separate, offline move: the main network is trained to match the expert's features on current data (adaptation) *and* its own previous features (retrospection) — knowledge flows one way, through distillation, at a chosen cadence. The main network never touches the raw stream directly; it only ever integrates. This is the complementary-learning-systems split executed with two SSL networks and a distillation channel.

## Key results / claims
- Outperforms exemplar-free continual-unsupervised-representation-learning (CURL) baselines (incl. CaSSLe-style regularization) on few-task and, especially, many-task splits, where single-network regularization degrades.
- Reaches performance comparable to exemplar-based methods in semi-supervised CL scenarios — without storing exemplars.
- Fully replay-free for the representation learner.

## How it relates to us
- **Organ / phase touched:** sleep/consolidation cadence (P8 grid sleep, P9 freeze); the two-timescale Cortex/Hippocampus inheritance; north-star hippocampus organ.
- **Same as us:** the architecture-level conclusion — a stream-facing plastic component plus a slow consolidated component, with knowledge transferred at discrete consolidation events (their adaptation-retrospection ≈ our sleep). Also replay-free at the representation, like our bulk.
- **Different from us:** both of their networks are full backprop SSL learners; consolidation is gradient distillation (expensive), not a closed-form re-fit; task boundaries trigger the cycle, whereas our cadence/gate is boundary-free; and their fast/slow split is *inside* the representation, while ours is representation (fast, SCFF) vs naming (slow, namer) — we consolidate the readout, they consolidate the backbone.
- **What we could borrow or test:** the idea that the *bulk itself* might deserve a two-timescale split if we ever hit many-domain lifelong streams where single-bulk rotation stops being benign — e.g., a slow shadow bulk updated only at sleep from the live bulk's weights (an EMA in weight space is the closed-form-cheap version; ties to the CLS-ER card in t1.4). Parked: P9.0 says we don't need it yet at our scale.
- **What contradicts or challenges us:** their premise — that an unaided single SSL network degrades over long task sequences — is a scale warning for our single-bulk commitment on truly long streams (our longest benches are short by their standards).

## Follow-on leads
- CLS-ER / ESMER (t1.4 cards) — the same fast/slow split with EMA instead of distillation (the cheap version).
- Gomez-Villa et al. 2022, Projected Functional Regularization (arXiv 2112.15022) — the same group's earlier single-network attempt.
- Many-task (50+ task) CURL benchmarks — the stress regime our benches haven't touched.
