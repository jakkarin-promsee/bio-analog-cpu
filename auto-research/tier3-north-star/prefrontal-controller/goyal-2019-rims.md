# Recurrent Independent Mechanisms (RIMs)
- **Authors / Year / Venue:** Goyal, Lamb, Hoffmann, Sodhani, Levine, Bengio, Schölkopf / 2019→2020 / ICLR 2021
- **Link:** https://arxiv.org/abs/1909.10893 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐ — the module *design* that pairs with a workspace; sparse "only the relevant part fires" = an analog-cheap specialization pattern.

## TL;DR
Replace one monolithic RNN with **many small recurrent cells that have independent dynamics**. At each step only the **top-k most input-relevant cells activate**; the rest hold their state untouched. Active cells communicate **sparingly through attention**. Each cell specializes to a "mechanism" of the world, so the system generalizes better when only a few factors change.

## The mechanism (how it actually works)
Two attention stages per step. (1) **Input attention**: each cell competes to attend to the current input; only the top-k winners are declared *active*. (2) Active cells run their own recurrent update; inactive cells are frozen for that step (state carried, no update). (3) **Communication attention**: active cells read from all cells to share context. Because activation is sparse and per-cell, a change in one factor of the world only wakes the cell that owns it — the rest of the state is provably untouched, which is why OOD factor-shift generalization improves.

## Key results / claims
"Dramatically improved generalization on tasks where some factors of variation differ systematically between train and eval" — copying tasks with longer sequences, physics environments, RL with distractors. The win grows exactly where a monolithic RNN entangles factors it should have kept separate.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator + the sparsity substrate property.
- **Same as us:** **sparse, modular activation** — dormant module = no charge cycles on analog — is directly our sparsity primitive; specialization-by-competition matches "scarcity forces roles."
- **Different from us:** RIM cells are learned by backprop through both attention stages and are *homogeneous* small RNNs; our "modules" are *heterogeneous frozen organs* (SCFF bulk, namer, LUT), not co-trained cells.
- **What we could borrow or test:** the **top-k input-gated activation** as the rule for *which organ the coordinator wakes* this step — a gradient-free version keyed on drift/goodness instead of learned attention.
- **What contradicts or challenges us:** RIMs' specialization emerges *because* the cells train together; frozen organs can't specialize to each other post-hoc, so the coordinator must exploit specialization that already exists rather than induce it.

## Follow-on leads
- Neural Production Systems (Goyal 2021); Bengio "Consciousness Prior" (already in dossier); modular meta-learning (Alet 2018).
