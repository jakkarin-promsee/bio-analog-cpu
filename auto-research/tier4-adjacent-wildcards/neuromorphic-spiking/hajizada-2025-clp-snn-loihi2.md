# Online Continual Learning on Intel Loihi 2 via a Co-designed Spiking Neural Network (CLP-SNN)
- **Authors / Year / Venue:** Elvin Hajizada, Danielle Rager, Timothy Shea, Leobardo Campos-Macias, Andreas Wild, Eyke Hüllermeier, Yulia Sandamirskaya, Mike Davies / 2025 / arXiv:2511.01553 (Intel Labs)
- **Link:** https://arxiv.org/abs/2511.01553
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the whole-system nearest neighbor: **rehearsal-free continual on-chip learning** with a local three-factor rule + neurogenesis + metaplasticity, on real neuromorphic silicon. This is what our gate+sleep+LUT does, done with plasticity instead of a closed-form namer — the head-to-head positioning target.

## TL;DR
CLP-SNN does online, few-shot **continual** learning directly on Intel's Loihi 2 with a self-normalizing three-factor local rule, integrated **neurogenesis** (grow neurons for new classes) and **metaplasticity** (protect old ones), and a spike-driven state machine that runs learning autonomously on-core. It matches replay-based accuracy **without any rehearsal**, at 113× lower latency and 6,600× lower energy than a strong edge-GPU baseline.

## The mechanism (how it actually works)
Three co-designed pieces:
1. **Self-normalizing three-factor local rule** — a plasticity rule (pre-trace × post × modulator) with built-in weight normalization, so learning stays stable online without a global optimizer or replay buffer.
2. **Neurogenesis** — new/unfamiliar inputs recruit *fresh* neurons rather than overwriting existing weights → new classes don't clobber old ones (structural, not gradient, protection).
3. **Metaplasticity** — consolidated neurons lower their plasticity, protecting learned classes (a per-unit learning-rate gate).
A **spike-driven neural state machine** orchestrates all of this on-core: neuron and synapse updates fire event-driven as spikes arrive or local timers trigger — no host in the loop. The whole thing is "co-designed": the algorithm was shaped to fit Loihi 2's event-driven, local-memory primitives, and the efficiency win is decomposed into an *algorithm* part and a *neuromorphic-substrate* part.

## Key results / claims
- Task: **OpenLORIS few-shot online continual learning.**
- **Rehearsal-free**, yet matches replay-based accuracy.
- vs strong edge-GPU baseline: **113× lower latency** (0.33 vs 37.3 ms), **6,600× lower energy** (0.05 vs 333 mJ).
- Efficiency decomposition: ~14.5× latency / ~22.6× energy from *algorithm*; ~7.8× latency / ~295× energy from *neuromorphic co-design*.

## How it relates to us
- **Organ / phase touched:** the *entire* neocortex loop — namer + drift gate + sleep + hippocampus-LUT, and the P8.7 "why-analog" energy decomposition.
- **Same as us:** near-identical *system goals* — online, continual, on-chip, rehearsal-light, forgetting-resistant. Their **metaplasticity = our per-unit protection**, their **neurogenesis = growing the LUT/heads for new classes** (our hippocampus-organ next step!), and their **algorithm×substrate energy decomposition is exactly our P8.7 "5.4× substrate × 2.9× algorithm"** framing. This is the most structurally parallel whole-system paper we've found.
- **Different from us:** they achieve continual protection with **local plasticity + structural growth**; we achieve it with a **closed-form namer + drift gate + sleep re-fit + CBRS eviction**. They are spiking on Loihi 2; we are rate-based on an analog capacitor crossbar (math model). They *grow* neurons (neurogenesis); our bulk is a *single frozen* SCFF (we grow only the LUT/heads).
- **What we could borrow or test:** **neurogenesis** is the direct inspiration for the queued hippocampus-organ build — "recruit fresh capacity for novel inputs instead of overwriting" is exactly the LUT-becomes-a-learning-organ idea. Their algorithm/substrate energy decomposition is a template we should mirror when we report the hippocampus-organ economy.
- **What contradicts or challenges us:** CLP-SNN is a *published, on-silicon, rehearsal-free continual learner that ties replay* — a real competitor occupying our exact pitch. It challenges "rehearsal-free continual on-chip learning is novel/hard". We should cite it as the neuromorphic state of the art we position against, and be precise that our differentiator is the analog-charge substrate + closed-form (no per-synapse plasticity) namer, not the continual-on-chip goal itself.

## Follow-on leads
- Davies et al. 2018/2021 — Loihi & Loihi 2 architecture papers (the substrate CLP-SNN targets).
- Hajizada et al. 2022 "Interactive continual learning for spiking neural networks" — the earlier version of this line.
- Kudithipudi et al. 2022 "Biological underpinnings for lifelong learning machines" (Nature MI) — the neurogenesis+metaplasticity design vocabulary.
