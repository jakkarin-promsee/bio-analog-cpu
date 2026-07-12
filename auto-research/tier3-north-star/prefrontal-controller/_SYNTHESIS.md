# Synthesis — The controller / working-memory / coordinator  (Tier 3, t3.4)
**The question:** What is the buildable, analog-native form of a bandwidth-limited coordinator over our organs (SCFF bulk, namer, LUT/hippocampus, the settling loop), and who is closest? Rank by: (a) works with a *small* controller that holds little + queries the rest, (b) routing is cheap/local on a crossbar, (c) forces specialization rather than one big net.

**Already in `draft6.0/research/north-star/2-controller.md`:** Global Workspace Theory (Baars; Dehaene), Shared Global Workspace (Goyal/Bengio ICLR'22), RIMs, the Consciousness Prior (Bengio 2017), and PBWM gating (O'Reilly & Frank). The dossier already reaches the right *shape* — "a small bus that holds one thought and broadcasts it; scarcity forces specialization." This sweep extends it **broader/newer (2022–2026)** into the engineering-native routing/bottleneck literature that gives the *buildable* form.

## The landscape (the engineering view, not the neuroscience)
Strip the biology and the field converges on one idea from four directions:

1. **The bottleneck-as-controller.** Perceiver IO is the cleanest statement: a **small fixed latent array** reads a huge input by cross-attention, thinks in the small space, writes outputs by cross-attention. The controller's size is *decoupled* from the world it summarizes — exactly "hold a little, query the rest." Recurrent Memory Transformer is the *temporal* version: a few memory tokens carried across segments = a bandwidth-limited register that persists through time.

2. **The workspace-as-protocol.** Shared Global Workspace formalizes *how modules talk*: **compete for a few write slots, broadcast the winners to everyone.** This replaces `O(n²)` pairwise wiring with a narrow write + a wide one-directional broadcast — and it argues the scarcity is *rational* (it forces specialization). Devillers/VanRullen's Global Workspace is the **built version over frozen modules**: small encoders/decoders glue pretrained-and-frozen specialists into a shared latent, trained mostly self-supervised (cycle-consistency) with a thin labeled trickle.

3. **The routing-as-economy.** The MoE line prices "who reads/writes" as capacity. Expert-Choice makes the **bandwidth a hard per-expert capacity** that auto-balances; Soft MoE keeps fixed slots but fills them by dense differentiable mixing (stable, but non-local). Both say the *fixed capacity is the feature* — the same claim GWT makes, in FLOPs.

4. **The grammar.** The Modular Deep Learning survey names the axes — **computation / routing / aggregation, updated locally** — and states our discipline almost verbatim: separate computation from routing, update modules locally, and you get transfer without interference.

The dividing fault line across *all* of them: **the routing is learned end-to-end by backprop through attention/gating.** That is the one thing our substrate cannot do.

## How WE differ  ← the money section
Our object is not one of these systems — it is the **frozen-module substrate they all assume the existence of, plus a constraint they all violate.**

- **Genuinely ours:** the modules are already **frozen and closed-form** (SCFF bulk, SLDA/RanPAC namer, LUT), and the coordinator must route **gradient-free, online, per-sample, and local on a crossbar.** Every paper here *learns* its router by BPTT. Nobody in this set builds a bandwidth-limited coordinator whose routing is set by closed-form / local rules. That corner is nearly empty — it is our contribution surface, and our risk.
- **A re-invention we should just adopt:** the **workspace protocol itself** (compete-for-slots + broadcast) and the **bottleneck-as-controller** shape are solved. We should inherit them wholesale, not re-derive them. Our WTA primitive *is* the slot competition; a shared broadcast line *is* analog-cheap.
- **The honest placement:** Devillers/VanRullen is our nearest twin — frozen specialists + a small shared latent + self-supervised glue + a labeled trickle is *our economy exactly*. The gap between us and them is only that their projectors are backprop-trained and their modules can *decode back* from the workspace (cycle-consistency needs invertibility our namer/LUT may lack).

**And the load-bearing honesty: we do not need a coordinator yet.** The current object is a *single* bulk + a reading namer + a passive LUT. There is no second specialist organ to coordinate, no shared state two organs fight over, and no demonstrated failure that comes from their *uncoordinated interaction*. The build discipline is explicit — "walk one spine; add roles only when a failure demands one." A workspace added now would be a solution without a problem. **The trigger that earns it:** once the hippocampus organ exists as a *second learning brain part* running alongside the SCFF-bulk+namer, and the settling loop must make the two **agree on a bounded working state within a fixed step budget** — the first time uncoordinated organ interaction produces a measurable loss (e.g. the LUT recall and the namer read disagree and the settle oscillates), *that* is when the coordinator becomes the next rung, not before.

## The gap / what we haven't tried (the ranked recommendation, for when the trigger fires)
**Which mechanism first, and why:**

1. **#1 — Devillers/VanRullen GLW pattern (frozen organs → small shared latent, self-supervised glue).** It is the only design in the set demonstrated over **frozen heterogeneous modules with almost no labels** — our exact constraint and economy. Build a small shared register with per-organ read/write projectors trained by **cycle-consistency + contrastive alignment** (gradient-light, mostly self-supervised), and use the 4–7× data-efficiency claim as the "is it earning its keep" yardstick.
2. **#2 — Shared Global Workspace protocol (compete-for-slots + broadcast).** Adopt as the *communication rule* once there are ≥2 organs: a hard slot cap on writes, a one-to-many broadcast back. Our DDM/drift gate is the natural **gradient-free write-competition gate** — the piece SGW learns, we already own.
3. **#3 — Perceiver-IO bottleneck as the register shape.** A **k-slot latent register** that cross-attends **read-only** over the frozen SCFF taps + LUT prototypes, self-attends a couple of settle steps, broadcasts a bias back. This is the concrete *first experiment*: measure k-slot register + gradient-free write-gate vs no-workspace on a task that needs two organs to agree.
4. **Capacity discipline from Expert-Choice** (fixed read/write budget per organ, top-scoring inputs kept by a *closed-form* affinity — goodness/prototype-distance — not a learned gate). **Soft MoE / RMT / the survey** are supporting: stability baseline, temporal-register minimal design, and the design-point vocabulary respectively.

**The single missing piece none of them give us:** a **gradient-free, streaming routing/gating rule** that still induces specialization. Every win in this literature is credited to *learned* routing. Closest hints to close it: the survey's "fixed routing," Expert-Choice's hard capacity, and our own drift/goodness signals as the affinity. That is the real open research question behind our coordinator.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Goyal et al. 2022 — Shared Global Workspace](goyal-2022-shared-global-workspace.md) | ⭐⭐⭐⭐⭐ | The protocol: compete-for-slots + broadcast; scarcity is rational — our inter-organ bus, not a crossbar. |
| [Devillers/VanRullen 2024 — GLW over frozen modules](devillers-2024-global-workspace-frozen-modules.md) | ⭐⭐⭐⭐⭐ | Our nearest twin: frozen specialists + small shared latent + self-supervised cycle-consistency + a thin labeled trickle. |
| [Jaegle et al. 2022 — Perceiver IO](jaegle-2022-perceiver-io.md) | ⭐⭐⭐⭐⭐ | The bottleneck-as-controller: a small fixed register reads/thinks/writes, size decoupled from #organs. |
| [Goyal et al. 2019 — RIMs](goyal-2019-rims.md) | ⭐⭐⭐⭐ | Sparse "only the relevant module fires" — dormant = no charge cycles; the analog-cheap specialization pattern. |
| [Zhou et al. 2022 — Expert Choice routing](zhou-2022-expert-choice-routing.md) | ⭐⭐⭐⭐ | Bandwidth as a hard per-expert capacity that auto-balances — scarcity-as-feature made literal. |
| [Pfeiffer et al. 2023 — Modular Deep Learning](pfeiffer-2023-modular-deep-learning.md) | ⭐⭐⭐⭐ | The grammar (computation/routing/aggregation, update locally) — states our discipline; pins our design point. |
| [Puigcerver et al. 2024 — Soft MoE](puigcerver-2024-soft-moe.md) | ⭐⭐⭐⭐ | Fixed slot capacity + the stability baseline our gradient-free hard routing must beat (its density is the anti-pattern). |
| [Bulatov et al. 2022 — Recurrent Memory Transformer](bulatov-2022-recurrent-memory-transformer.md) | ⭐⭐⭐ | The minimal temporal register: a few memory slots carried across steps = working memory for the settle loop. |

## Leads spawned
- **Gradient-free / closed-form routing** — a workspace whose read/write gates are set by drift/goodness/prototype-distance, not BPTT. The real open question; nearly empty in this literature.
- **Cycle-consistency over non-invertible organs** — can a namer/LUT that doesn't cleanly decode still support the self-supervised glue Devillers relies on?
- **Attention-schema / self-model controllers** (Graziano-inspired ML) — a controller that models its own routing state; adjacent to correctness-as-feeling (t3.3).
- **BASE Layers / optimal-transport assignment routing** (Lewis 2021) — balanced hard routing without a learned gate; possibly the streaming-legal Expert-Choice.
- **Global-Workspace world models** (Multimodal Dreaming, 2025, arXiv 2502.21142) — a workspace inside model-based RL; the north-star recurrent-brain bridge.
