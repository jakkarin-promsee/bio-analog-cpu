# Mixture-of-Experts with Expert Choice Routing
- **Authors / Year / Venue:** Zhou, Lei, Liu, Du, Huang, Zhao, Dai, Chen, Le, Laudon (Google) / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2202.09368 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐ — makes the bandwidth limit a **hard per-expert capacity** that auto-balances; the cleanest "scarcity forces selectivity" routing.

## TL;DR
Invert MoE routing: instead of each token choosing its top-k experts (which leaves some experts starved and others overloaded, needing an auxiliary balance loss), let **each expert choose its top-k tokens**. Every expert has a **fixed capacity** and fills it with the tokens it wants most; a token may go to zero, one, or many experts. Load balance is automatic and convergence is >2× faster.

## The mechanism (how it actually works)
Score the full token×expert affinity matrix. Then take top-k **along the expert axis**: expert e keeps the k tokens with the highest affinity to it (k = capacity). Because every expert fills exactly its capacity, no expert is starved or overrun — the imbalance problem of token-choice disappears by construction, with no load-balancing regularizer. The **capacity is the bandwidth cap**: each expert can only "hear" k inputs per step, so it must be selective about which it commits to.

## Key results / claims
>2× faster training convergence than Switch Transformer / GShard at matched compute; wins on 11 GLUE/SuperGLUE tasks; beats the T5 dense baseline on 7/11 at lower cost. The gains are attributed to eliminating expert under-utilization.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator (capacity = the workspace/organ read budget).
- **Same as us:** **hard capacity as a bandwidth budget** is our "scarcity is the mechanism" made literal, and expert-side selection is more crossbar-friendly than dense soft mixing — each organ reads a *bounded, sparse* set, not everything.
- **Different from us:** the affinity scores are still learned by backprop and the top-k is global (needs to see the whole batch's affinities). Our routing must be gradient-free and online/streaming (per-sample), so the global top-k is not directly legal.
- **What we could borrow or test:** give each organ (and the workspace) a **fixed read/write capacity** and let it keep its top-scoring inputs by a *closed-form* affinity (goodness / prototype distance) instead of a learned gate — a streaming, per-sample approximation of expert-choice.
- **What contradicts or challenges us:** the balance guarantee relies on batched global top-k; per-sample online selection can re-introduce the starvation the method was designed to remove — a real caveat for our streaming regime.

## Follow-on leads
- Soft MoE (this folder); BASE Layers (Lewis 2021, optimal-assignment routing); Switch Transformer (Fedus 2021).
