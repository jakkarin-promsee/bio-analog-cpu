# Neural Collapse Terminus: A Unified Solution for Class Incremental Learning and Its Variants
- **Authors / Year / Venue:** Yibo Yang, Haobo Yuan, Xiangtai Li, Jianlong Wu, Lefei Zhang, Zhouchen Lin, Philip Torr, Dacheng Tao, Bernard Ghanem / 2023 / arXiv (journal extension of the ICLR 2023 NC-FSCIL paper, arXiv 2302.03004)
- **Link:** https://arxiv.org/abs/2308.01746 (fetched; code: https://github.com/NeuralCollapseApplications/UniCIL)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐ — the ETF idea taken to *continual* learning: pre-allocate the whole label space's geometry before any class arrives, so incremental classes never re-carve the feature space.

## TL;DR
In incremental learning, each new task re-divides the feature space, and that re-division *is* (much of) the forgetting. Neural Collapse Terminus fixes a **simplex ETF over the entire label space in advance** — including classes not yet seen — and trains features of every session toward their pre-assigned vertices ("prototype evolving"). One mechanism covers normal CIL, long-tail CIL, and few-shot CIL, with neural-collapse optimality maintained regardless of imbalance or scarcity.

## The mechanism (how it actually works)
The story: a learnable classifier grown class-by-class means the geometry of "where classes live" is renegotiated at every task — old features end up on the wrong side of new boundaries without a single weight of theirs changing. The fix is to make the destination map static:

1. Before training, build an ETF with K vertices for the *maximum* label space (K ≥ total classes ever; the paper also handles unknown K).
2. As sessions arrive, each new class is assigned a reserved vertex; features are pulled to vertices with a fixed (non-learnable) classifier — for CIL/LTCIL via a prototype-evolving scheme that moves features smoothly to the terminus, for FSCIL with minor adaptation.
3. Because the inter-class geometry is maximal-equiangular *by construction and forever*, there is no incremental boundary renegotiation — the classifier contributes zero forgetting, structurally (the same "zero head-forgetting by algebra" property our analytic heads get from order-independent sums, achieved here by geometry instead).

## Key results / claims
- One unified method works across CIL, long-tail CIL, and few-shot CIL — the imbalance/scarcity robustness is inherited from the fixed geometry, not from per-setting machinery.
- Theoretical analysis: neural-collapse optimality holds *in an incremental fashion* regardless of data imbalance or scarcity.
- Extends the ICLR 2023 NC-FSCIL result (which pre-assigned ETF prototypes for the base + all incremental sessions and drove features to them with a dot-regression loss).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer + the hippocampus LUT (where our class prototypes live); conceptually adjacent to the sleep re-fit (which is our version of "renegotiate the geometry safely").
- **Same as us:** the diagnosis that *the head's own adaptation is the forgetting surface* — our answer was closed-form order-independent statistics; theirs is frozen geometry. Two different proofs of the same "zero head-forgetting" property.
- **Different from us:** the whole mechanism assumes a **trainable backbone** that can move features to assigned vertices — our bulk is frozen and label-free. We can't adopt the training scheme, only the target geometry.
- **What we could borrow or test:** the **pre-allocation trick** — when the class count grows over a lifelong stream (our P11 C=20 crossover), reserving ETF-vertex targets for unseen classes in the ridge solve keeps early and late classes on identical geometric footing; today our one-hot targets implicitly grow the label simplex axis-by-axis, which is *not* equiangular. Cost: a fixed target matrix in the LUT, zero resident-weight growth.
- **What contradicts or challenges us:** their forgetting story is entirely about the *backbone* renegotiating boundaries — our frozen bulk sidesteps that by construction, which suggests the marginal value of ETF targets for us is smaller than their headline; the honest expectation is a small, possibly-null effect concentrated in class-count-growth regimes.

## Follow-on leads
- NC-FSCIL (ICLR 2023, arXiv 2302.03004) — the base paper; cleanest statement of ETF pre-assignment.
- SCL-PNC (this folder) — the 2025 "parametric" answer to *static* ETF's rigidity.
- Progressive Neural Collapse for CL (arXiv 2505.24254) — rethinking whether the terminus should be fixed at all.
