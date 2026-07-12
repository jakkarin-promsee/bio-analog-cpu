# On-Device Training Under 256KB Memory
- **Authors / Year / Venue:** Ji Lin, Ligeng Zhu, Wei-Ming Chen, Wei-Chen Wang, Chuang Gan, Song Han / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2206.15472
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the budget anchor of on-device training: what gradient learning costs when the whole system must fit in 256KB, and the tricks that make it fit.

## TL;DR
First on-device training of CNNs inside 256KB SRAM + 1MB Flash, no auxiliary memory — ~1/1000 the memory of PyTorch/TF at matched accuracy on the VWW tinyML benchmark. Three moves: quantization-aware scaling (stable 8-bit training), sparse update (skip gradients for unimportant layers/tensors), and a compile-time Tiny Training Engine.

## The mechanism (how it actually works)
The enemy is training memory (activations + optimizer state), not FLOPs. (1) **Quantization-aware scaling:** train directly in int8; per-tensor gradient scales are calibrated to compensate for the distortion quantization injects, so 8-bit training tracks FP32 without normalization layers. (2) **Sparse update:** most layers don't need updating for downstream adaptation — pick a small, offline-profiled subset of layers/channels whose gradients matter, and never compute the rest of the backward graph; memory and compute for the skipped parts vanish. (3) **Tiny Training Engine:** autodiff is moved to compile time; the backward graph is pruned dead-code-style, kernels fused, so the runtime executes only the arithmetic the sparse update actually needs. The composite point: **backprop is affordable under an extreme budget only if you refuse to compute most of it.**

## Key results / claims
- Trains under **256KB SRAM / 1MB Flash**; ~10^3× less memory than standard frameworks.
- Matches cloud-training accuracy on VWW-class tinyML tasks; enables lifelong on-device adaptation on commodity MCUs (STM32-class).
- Sparse update alone gives most of the memory win with negligible accuracy loss (task-dependent subset).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P8 cost meter's *digital rival* — this is the strongest version of "GD on a budget," the thing our 2.9× algorithm factor is measured against.
- **Same as us:** shares our thesis that direction (gradient) is the expensive thing and must be rationed — their sparse update is "pay for direction only where it counts," our gate is "pay for direction only *when* it counts."
- **Different from us:** they keep backprop and shrink it; we removed it (closed-form namer). Their budget currency is SRAM bytes; ours is metered pJ. No stream/drift semantics at all — it's transfer-learning adaptation, not continual learning; forgetting is out of scope.
- **What we could borrow or test:** (1) **sparse update for the namer** — at sleep we re-fit everything; a profiled "which prototypes/classes actually moved" partial re-fit could cut sleep cost (pairs with the gate's evidence about *what* drifted); (2) their honest baseline discipline — our digital-GD baseline in P8.7 assumes framework-style training; a MCUNetV3-style *optimized* digital learner is the harder, fairer rival for the 2.9× algorithm claim.
- **What contradicts or challenges us:** it weakens any claim that gradient learning *can't* run under tiny budgets — it can, at 256KB. Our differentiator must stay (a) no backward graph at all, (b) the analog substrate floor, (c) continual safety — not raw feasibility.

## Follow-on leads
- MCUNet v1/v2 (Lin et al. 2020/2021) — the inference-side budget ancestors.
- PockEngine (MICRO 2023) — sparse fine-tuning engine for edge devices, same group.
- TinyTrain (ICML 2024, arXiv:2307.09988) — task-adaptive sparse training at the data-scarce edge.
