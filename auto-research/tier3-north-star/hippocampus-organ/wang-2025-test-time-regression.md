# Test-Time Regression: A Unifying Framework for Designing Sequence Models with Associative Memory

- **Authors / Year / Venue:** Ke Alexander Wang, Jiaxin Shi, Emily B. Fox / 2025 / arXiv 2501.12352
- **Link:** https://arxiv.org/abs/2501.12352 — fetched
- **Tier / Topic:** tier3 / t3.1 hippocampus organ
- **Relevance:** ⭐⭐⭐⭐ — The **map of the whole menu**: it proves fast weights, linear attention, state-space models, softmax attention, and TTT are all the *same* thing — associative memory via test-time regression — so it tells us exactly which knobs define the hippocampus we should build.

## TL;DR
Associative recall = **memorize then retrieve**, and memorizing is a **regression problem solved at test time**. Every major sequence-mixing layer is one choice of (i) how you weight past tokens, (ii) what function class the regressor is, and (iii) which optimization algorithm you run at test time. Pick "linear regressor + one gradient step" → linear attention / fast weights; "kernel regressor + exact solve" → softmax attention; "MLP + SGD" → TTT. It's the Rosetta Stone for the memory-organ design space.

## The mechanism (how it actually works)
Formalize an associative memory layer as: given a stream of (key, value) pairs, fit a regressor `f` so that `f(k_i) ≈ v_i` for the relevant past, then answer a query `q` with `f(q)`. This is a weighted least-squares (regression) problem *reconstructed at every position from the tokens seen so far* — hence "test-time regression." Three design axes fall out:
1. **Regression weights** — how much each past (k,v) counts (uniform → full attention; exponentially-decaying → recency/RNN; a gate → selective SSMs).
2. **Regressor function class** — linear (fast weights / linear attention), kernel (softmax attention), MLP (TTT).
3. **Test-time optimizer** — one gradient step (additive fast weights), the delta rule (error-correcting write), an exact/closed-form solve (attention), or a few SGD steps (TTT/Titans).
From these, the paper *re-derives* the known architectures and points at unexplored cells (e.g. higher-order attention) — and explains failures mechanistically, e.g. linear attention struggles with inter-token correlation because a single linear regressor can't decorrelate keys.

## Key results / claims
- Linear attention, gated linear attention, SSMs, fast-weight programmers, DeltaNet, softmax attention, and TTT are all recovered as points in the (weights × class × optimizer) cube.
- Explains linear attention's correlation limitation as an under-fit regression → motivates the delta rule and whitening as principled fixes.
- Surfaces new architectures (higher-order generalizations) the framework predicts but nobody had tried.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** hippocampus-LUT (the design space) · closed-form namer (our namer is *already* a test-time regression — RanPAC/SLDA is closed-form ridge over the bulk).
- **Same as us:** this is the theory that says our closed-form namer (running-Gram ridge = exact-solve linear regression over bulk features) and the grown hippocampus (an associative memory) are **the same family** — the namer is the "exact-solve linear" corner, and the memory is the "online-update" corner of one cube. It hands us the vocabulary to place every candidate mechanism on the same axes and pick deliberately.
- **Different from us:** the framework is built for *sequence models trained end-to-end*; it assumes the (key,value) projections and the loss are learned by backprop. We fix the keys (frozen SCFF) and forbid the backward pass — so we live on a constrained slice of the cube (frozen keys, closed-form or delta-rule optimizer, linear/kernel class).
- **What we could borrow or test:** use the three axes as the **decision record** for the hippocampus build: (weights = a forgetting gate we already have; class = linear/RFF-kernel to stay crossbar-native — note KLDA/RanPAC are the kernel-class point; optimizer = delta-rule, the substrate-legal member). The framework predicts a **closed-form / exact-solve** memory should beat a one-step additive one on correlated streams — directly testable against our P11 autocorrelated-stream floor. It also formally connects our namer and our memory: they could be *one* regression object read at two rates (fast = memory, slow = namer), which is a genuine architectural simplification to probe.
- **What contradicts or challenges us:** it makes explicit that the strongest members use an **MLP regressor + multi-step optimization** (Titans/TTT) — the expressive, gradient-trained corner we can't reach. Our substrate confines us to the linear/kernel + closed-form/delta cells, so the framework quantifies *exactly what capability we trade away* by staying gradient-free.

## Follow-on leads
- DeltaNet parallel training (Yang et al. 2024) — the delta-rule cell made scalable.
- Whitening / preconditioned online regression — the principled fix for the correlation limit (ties to our anisotropy ceiling in the namer).
- The "higher-order attention" cells the paper leaves open — a wildcard for a richer recall op.
