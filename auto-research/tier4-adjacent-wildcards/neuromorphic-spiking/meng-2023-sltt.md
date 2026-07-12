# Towards Memory- and Time-Efficient Backpropagation for Training SNNs (SLTT)
- **Authors / Year / Venue:** Qingyan Meng, Mingqing Xiao, Shen Yan, Yisen Wang, Zhouchen Lin, Zhi-Quan Luo / 2023 / ICCV 2023
- **Link:** https://arxiv.org/abs/2302.14311
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐ — the empirical result that **temporal credit assignment barely matters** for SNN accuracy — you can drop most of it and still hit SOTA. A useful counterweight: it says the time-axis machinery e-prop works so hard to get right is often nearly disposable.

## TL;DR
SLTT shows that backpropagating an SNN's error *through the temporal dimension* contributes almost nothing to the final gradient, so it simply **deletes those temporal routes** from the computational graph. Result: near-BPTT accuracy (SOTA on ImageNet for its class) with **>70% less memory and >50% less training time**, and memory that is independent of the number of time steps.

## The mechanism (how it actually works)
In BPTT-for-SNNs the gradient has two kinds of paths: **spatial** (error flowing back across layers within a time step) and **temporal** (error flowing back across time steps through the membrane-potential recurrence). Meng et al. measure the magnitude of the temporal paths and find them small — the spatial paths dominate the useful gradient. So SLTT keeps the spatial backprop and **prunes the temporal backprop routes**. Because the temporal recurrence is what forced you to store all T states, dropping it makes memory constant in T. **SLTT-K** goes further: compute gradients at only K of the T time steps, cutting scalar multiplications independently of T.

## Key results / claims
- **Temporal backprop contributes little** — the paper's central, somewhat surprising empirical claim.
- SOTA-class accuracy on ImageNet (and neuromorphic datasets) among direct-trained SNNs.
- **Memory −70%+, training time −50%+** vs BPTT; memory independent of time steps.

## How it relates to us
- **Organ / phase touched:** north-star temporal loop (as a *caution*), and the general "how much does time actually matter" question.
- **Same as us:** SLTT's finding rhymes with our own instinct — we *don't* carry temporal history at all, and our object still works on streams (via gate + sleep, not through-time gradient). SLTT gives independent evidence that heavy through-time credit assignment is often overkill.
- **Different from us:** still surrogate-gradient descent on a spiking net with a time axis; still supervised. We are unsupervised bulk + closed-form namer.
- **What we could borrow or test:** the *diagnostic* is the borrowable thing — before investing in an e-prop-style temporal loop, run SLTT's test: measure how much a temporal-credit term would actually change the update. If the answer on our target streams is "little", the north-star loop can stay largely feed-forward + gated (cheap) rather than truly recurrent-trained (expensive). This is a concrete way to *avoid* over-building the temporal loop.
- **What contradicts or challenges us:** it slightly undercuts the north-star framing that we *need* a rich temporal learning rule — SLTT says the temporal part may be nearly free to skip. That's actually convenient for us (cheaper loop), but it means "we added real temporal credit assignment" is a weaker selling point than it sounds.

## Follow-on leads
- Xiao et al. 2022 OTTT (sibling card) — same lab, the online-memory version.
- "Temporal Reversible SNNs with O(L) memory" (arXiv 2405.16466) — the reversible-net route to cheap temporal training.
- Deng et al. 2023 "Temporal efficient training of SNNs" — regularizing the temporal loss instead of pruning it.
