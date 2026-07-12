# Coordination Among Neural Modules Through a Shared Global Workspace
- **Authors / Year / Venue:** Goyal, Didolkar, Lamb, Badola, Ke, Rahaman, Binas, Blundell, Mozer, Bengio / 2021→2022 / ICLR 2022
- **Link:** https://arxiv.org/abs/2103.01197 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐⭐ — the buildable Global Workspace: the exact "compete-for-slots + broadcast" protocol for coordinating our organs over a narrow bus.

## TL;DR
Turns Global Workspace Theory into a deep-learning module. Instead of `O(n²)` pairwise all-to-all messaging between specialist modules, the modules **compete for a small number of write slots in a shared workspace**; the winners are written in, and the workspace is then **broadcast back to every module**. The bandwidth cap is shown to be *rational* — it forces specialization and synchronizes otherwise-independent parts.

## The mechanism (how it actually works)
Take K specialist modules (here Transformer/RIM-style cells). Each step every module produces a candidate write. A **shared workspace** with only M ≪ K memory slots runs a **key-query attention competition**: only the top-scoring writes get in (a soft winner-take-all). The workspace state is updated from those winners, then **broadcast** — a single one-to-many read that every module attends to before its next update. So communication is two cheap operations, *write-competition* (narrow) and *broadcast* (wide but one-directional), never a dense pairwise crossbar. The scarcity of slots is the whole point: modules that want their content heard must make it *general enough to win the slot*, which pushes them toward disentangled, composable roles.

## Key results / claims
Across several relational / physical-reasoning / RL benchmarks the shared-workspace coupling beats pairwise-attention and independent-module baselines, with better systematic generalization when factors of variation shift. The headline argument is qualitative-but-principled: **capacity limits improve coordination**, they are not a cost to be engineered away.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator (the "prefrontal" bus over SCFF bulk / namer / LUT / settle loop).
- **Same as us:** narrow shared state + broadcast is exactly the "hold a little, share it widely" intuition; the winner-take-all write is a primitive we already have; broadcast is one-to-many (analog-cheap — a shared line, not a crossbar-to-everything).
- **Different from us:** their modules are **co-trained end-to-end by backprop through the attention competition**. Our organs are *frozen / closed-form* and the routing must be gradient-free and local — so we inherit the *protocol*, not the learning of it.
- **What we could borrow or test:** build the inter-organ bus as a **small workspace with a hard slot cap + broadcast**, not a full crossbar. Use our DDM/drift gate as the write-competition gate instead of a learned key-query.
- **What contradicts or challenges us:** the demonstrated benefit depends on the slot attention being *learned*; a fixed/gradient-free write rule may not induce the specialization the paper credits to the bottleneck — an open risk to test.

## Follow-on leads
- Neural Production Systems (Goyal 2021) — entities + sparse rule application, the rule-based sibling.
- Bitfit/attention-schema variants; "Inductive biases for higher-level cognition" (Goyal & Bengio 2022) manifesto.
