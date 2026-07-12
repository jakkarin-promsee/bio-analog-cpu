# Modular Deep Learning (survey)
- **Authors / Year / Venue:** Pfeiffer, Ruder, Vulić, Ponti / 2023→2024 / TMLR (survey)
- **Link:** https://arxiv.org/abs/2302.11529 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐⭐ — the engineering-native map of the whole field: it names the axes (computation / routing / aggregation) our coordinator lives on, and states our exact discipline ("separate computation from routing, update modules locally").

## TL;DR
A unifying survey of modular deep learning. Any modular system decomposes into four questions: **what a module computes**, **how a module is parameterized**, **how inputs are routed** to modules, and **how module outputs are aggregated**. Separating *computation* from *routing* and updating modules *locally* is what buys positive transfer, systematic generalization, and no negative interference.

## The mechanism (how it actually works)
The taxonomy. **Computation function**: what the module does (adapter, LoRA, prefix, a full sub-net). **Routing function**: which modules fire — **fixed** (hand-specified, e.g. per-task) vs **learned** (a gate reads the input and picks), and hard (top-k) vs soft (weighted). **Aggregation function**: how the chosen modules' outputs combine (sum, attention, sequential composition). The paper's thesis is that keeping these three *decoupled* — modules that don't have to know about each other, a routing layer that can change without retraining modules, local updates — is what makes modular systems transfer and generalize where monoliths interfere.

## Key results / claims
A conceptual synthesis, not a benchmark: it unifies MoE, adapters, prompt/prefix tuning, hypernetworks, and RIM/workspace-style routing under one grammar, and argues modularity is the lever for scaling, cross-lingual/cross-modal transfer, causal/compositional generalization, and RL.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator (the vocabulary for specifying it) + the build discipline.
- **Same as us:** our design **is** this grammar — **fixed computation (frozen organs)** + a **routing function** (the coordinator) + an **aggregation** (broadcast/register), with **local updates** (each organ trains on its own signal). "Separate computation from routing, update locally" is almost verbatim our project rule.
- **Different from us:** the surveyed routing functions are overwhelmingly **learned by backprop**; the few "fixed routing" cases are hand-specified per-task, not gradient-free-but-adaptive as we need.
- **What we could borrow or test:** use the taxonomy to **pin our design point precisely** — "fixed-computation, hard-sparse, gradient-free-adaptive routing, broadcast aggregation" — and to find the nearest published routing function to adapt.
- **What contradicts or challenges us:** the survey's evidence base is that *learned* routing is what delivers the transfer wins; our gradient-free-routing requirement sits in a corner the field has barely populated — a gap, and a risk.

## Follow-on leads
- Fixed vs learned routing sub-lit (Fedus MoE review 2022); hypernetwork routing; "Inductive biases for higher-level cognition" (Goyal & Bengio 2022) as the cognition-side companion.
