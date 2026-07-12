# Gradient based sample selection for online continual learning (GSS)
- **Authors / Year / Venue:** Rahaf Aljundi, Min Lin, Baptiste Goujaud, Yoshua Bengio / 2019 / NeurIPS 2019
- **Link:** https://arxiv.org/abs/1903.08671 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule
- **Relevance:** ⭐⭐⭐⭐ — the seminal gradient-based buffer-selection anchor; defines the "keep the samples whose gradients span the most directions" ideal that CBRS cheaply approximates, but it is gradient-native — the exact thing our substrate forbids.

## TL;DR
Populating a replay buffer is cast as a **constraint-selection** problem: each stored sample defines a gradient constraint, and a good buffer is the subset whose gradients are **most diverse** (span the largest solid angle in gradient space). No task boundaries, no i.i.d. assumption — a greedy sampler as cheap as reservoir but immune to imbalanced streams.

## The mechanism (how it actually works)
Continual learning is viewed through the GEM lens: don't increase loss on stored samples, i.e. keep the new-update gradient in the feasible cone defined by the buffer's gradients. If the buffer's gradients already point in many directions, that cone is tight and protective. So the selection objective becomes **maximize the diversity of the parameter-gradients** of the samples in the buffer (minimize the maximal pairwise cosine / the solid angle they subtend). The exact version is a quadratic program; the practical version is **Gradient Sample Selection–Greedy (GSS-Greedy)**: for each incoming sample compute its gradient, compare (cosine) against a random subset of buffer gradients, and probabilistically replace a buffer item if the newcomer adds a more novel direction. Cost ≈ reservoir sampling, but every decision needs a **per-sample backprop gradient**.

## Key results / claims
Matches or beats task-boundary-dependent methods (GEM, iCaRL-style) on split-MNIST / permuted-MNIST / split-CIFAR in the pure online, boundary-free setting, and is far more robust than reservoir on **imbalanced** streams (it stops the buffer collapsing onto the dominant class). It is the reference other selection papers (OCS, GCR, InfoRS) benchmark against.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** sleep / bounded-LUT eviction (P9.3), the C=20 retention crossover (P11).
- **Same as us:** the *goal* is identical — hold a small set that spans the class **directions**, which is exactly our "CBRS keeps class directions, not the dense mean" spine (P9's herding-null argument).
- **Different from us:** GSS measures diversity in **gradient space** and needs a backward pass per candidate. Our substrate has **no backward pass that leaves the chip** — this is structurally off-limits. CBRS reaches a similar diversity by a label-count proxy, for free.
- **What we could borrow or test:** the *diagnostic* — GSS-Greedy is the near-ideal "maximally diverse buffer" ceiling; racing CBRS against a GSS oracle (offline, gradient allowed) would tell us how much retention our free proxy leaves on the table at the C=20 pressure point. Not deployable, purely a measuring stick.
- **What contradicts or challenges us:** it argues the *right* selection signal is gradient-diversity, implying a label-balance proxy (CBRS) is a lossy shortcut. Our defense is that the shortcut is substrate-mandatory and P9.3 showed it beats reservoir/recency handily.

## Follow-on leads
- OCS (Yoon 2022) and GCR (Tiwari 2022) refine this into affinity/coreset variants.
- Distributionally-Robust Memory Evolution (DRO, arXiv 2207.07256) evolves the buffer against worst-case rather than selecting it.
