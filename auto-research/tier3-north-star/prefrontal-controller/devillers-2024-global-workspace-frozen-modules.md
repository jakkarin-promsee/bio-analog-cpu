# Semi-supervised Multimodal Representation Learning through a Global Workspace
- **Authors / Year / Venue:** Devillers, Maytié, VanRullen / 2023→2024 / IEEE TNNLS 36(5)
- **Link:** https://arxiv.org/abs/2306.15711 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐⭐ — the closest built analog to *our* setup: **frozen specialist modules** wired through a **small shared latent workspace**, glued mostly self-supervised with only a thin labeled trickle.

## TL;DR
A concrete, buildable Global Workspace over **pretrained, frozen** unimodal modules (e.g. a vision encoder and a language encoder). Small learned **encoders project each frozen module's features into a shared latent workspace**, and **decoders reconstruct back out**. The workspace is trained largely **self-supervised via cycle-consistency** (encode→decode ≈ identity) plus contrastive alignment, needing **4–7× less matched/labeled data** than fully supervised fusion.

## The mechanism (how it actually works)
Each modality's frozen encoder gives a latent. A per-module **encoder** maps that latent *into* the shared workspace; a per-module **decoder** maps the workspace state *back* to that module's latent. Two self-supervised losses do most of the work: (1) **cycle-consistency** — go module→workspace→module and demand you get back where you started (and workspace→module→workspace round-trips too); (2) **contrastive alignment** — matched cross-modal pairs land at the same workspace point. Only a small amount of *paired/labeled* data is needed to anchor the alignment; the frozen modules never move. Ablations show **both** the shared workspace and the cycle-consistency are load-bearing.

## Key results / claims
The workspace representation supports downstream classification, cross-modal retrieval/translation, and robust transfer — while using 4–7× less matched data than supervised baselines. Removing either the workspace bottleneck or the self-supervised cycle-consistency collapses the gains.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator — this is the **template for a coordinator over frozen organs** (SCFF bulk, namer, LUT).
- **Same as us:** frozen specialists + a **small shared latent** + **mostly self-supervised glue** + a **thin labeled trickle** is our whole economy (pay for direction once, read the frozen bulk). The small per-module encoder/decoder into the workspace is a *reader/writer*, not a re-training of the organ — exactly our "read, never write the bulk."
- **Different from us:** the encoders/decoders are still small **backprop-trained** nets, and the modalities are two symmetric encoders, not our asymmetric organ zoo. Cycle-consistency assumes each module can *decode back* from the workspace — our namer/LUT don't obviously invert.
- **What we could borrow or test:** **cycle-consistency as a self-supervised objective to align organ outputs in a shared register** with almost no labels — the gradient-light way to build the bus; and the **4–7× data-efficiency** claim as the yardstick for "is the coordinator earning its keep."
- **What contradicts or challenges us:** it needs *some* gradient training of the projectors and a decode path; a fully closed-form / non-invertible organ set may not support the cycle-consistency that the ablation says is essential.

## Follow-on leads
- VanRullen & Kanai 2021 "Deep learning and the Global Workspace Theory" (the proposal); Maytié et al. 2024 "Zero-shot cross-modal transfer" (RLC); "Multimodal Dreaming: a Global Workspace approach to world-model RL" (2025, arXiv 2502.21142).
