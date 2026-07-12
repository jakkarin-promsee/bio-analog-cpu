# Synthesis — Analytic / closed-form continual learning  (Tier 1)
**The question:** Who else does continual, gradient-free "naming" on a frozen representation via closed-form updates, and exactly how is our namer (RanPAC committed + SLDA deployed, drift-gated + sleep-consolidated over a bounded LUT, reading a frozen-but-rotating SCFF bulk) different? And what beats plain SLDA on our anisotropy / tied-covariance failure mode?

**Already in `draft6.0/research/`:** the phase-7 curated library covers the mechanisms of RanPAC (2307.02251), Deep-SLDA + Deep-SRDA, FeCAM, the ACIL/RLS paradigm at story level, plus the reservoir/ELM/OCO convex-readout foundations (`analytic-and-covariance-readouts.md`, `the-convex-readout.md`, `direction-readouts.md`). This sweep goes wider and newer: the 2024–2025 analytic-CL family itself (DS-AL, GACL, F-OAL, AIR), the skeptic control (RanDumb), the theory repair (LoRanPAC), and the covariance-under-drift bridge (AdaGauss).

## The landscape (the engineering-native view)

This family is not neuroscience and never was — it is **recursive least squares from adaptive filtering** (Gauss → Plackett 1950 → RLS/Kalman → ELM/pseudo-inverse learning) rediscovered as a continual-learning weapon. The founding theorem (ACIL, NeurIPS 2022) is pure algebra: keep one running correlation matrix over frozen features, rank-update it per batch, and the recursive ridge solution *equals* the joint solution over all data ever seen. Forgetting in the head becomes impossible by construction; task boundaries, phase counts, and (with GACL's exposed/unexposed decomposition) even class mixing and revisits stop mattering. One group (Zhuang et al.) has industrialized the paradigm: ACIL → GKEAL (kernel widening) → DS-AL (a second closed-form compensation stream fixing ridge under-fit) → GACL (boundary-free streams) → F-OAL (forward-only, online, low-memory) → AIR (closed-form imbalance re-weighting), and by 2025 the recursion is being routed into LLM adapters (Analytic Subspace Routing) and embodied schedulers.

Around them sit three important outsiders. **Hayes & Kanan's Deep SLDA (2020)** is the streaming-statistics grandparent: running class means + one tied covariance, per-sample updates, ImageNet-scale streaming for pennies. **RanDumb (NeurIPS 2024)** is the skeptic: a *fixed random kernel lift* + streaming linear head beats SOTA continually-*learned* representations — the published indictment of any "my learned representation helps" claim, including ours. **LoRanPAC (ICLR 2025)** is the theory repair: the RanPAC-style lifted Gram is severely ill-conditioned, and continually-truncated SVD both stabilizes it and yields error bounds over hundreds of tasks.

On the anisotropy question specifically, the field's ladder is: tied covariance (SLDA — cheap, underfits per-class shape) → regularized/shrunk per-class (Deep-SRDA, FeCAM) → *drift-aware* per-class (AdaGauss, NeurIPS 2024: adapt stored covariances through the representation change task-by-task, plus an anti-collapse regularizer, because stale covariances create a task-recency bias of their own).

## How WE differ  ← the money section

**What is honestly re-invention:** our namer's skeleton — random ReLU lift → running Gram → ridge solve, streaming, exemplar-light, gradient-free, on frozen features — is squarely inside this family. F-OAL even matches our deployment constraints item-for-item (forward-only, online, low-memory). "Closed-form continual naming on a frozen representation" is *their* paradigm; we adopted it knowingly in P7 and should cite it that way. Order-invariance of the head alone is also *expected by construction* in this family (GACL's weight-invariance) — our P10/P11 order-invariance wins must be claimed for the whole system under drift, not for the head.

**What is genuinely ours — four things this family does not have:**
1. **A drifting substrate, survived.** Every paper above assumes the frozen encoder never moves; the equivalence theorems die the moment it does. Our bulk *rotates by design* (SCFF keeps learning every step, P9.0), and the namer survives via the sleep re-fit + proto-reanchor (P9.4) over a bounded LUT. The family's exact-recursion memory (a Gram carried forever) is replaced by periodic closed-form re-estimation from a bounded buffer — approximate where they are exact, but robust where they are brittle. AdaGauss is the only neighbor that even names this problem, and it needs backbone gradients for its fix; we don't.
2. **An economy.** Nobody in this family decides *when not to update*. Our drift gate (DDM on error-EMA) exists because firing more forgets more (P8: always-pay −0.137) — update-suppression as a *safety* mechanism is absent from analytic CL, where updates are assumed harmless (true only under their frozen-encoder algebra).
3. **A costed substrate.** Their "efficiency" is GPU-minutes; our head is metered in substrate energy (P8: SLDA deployed at 69× less than RanPAC; P8.7's 2×2), and the head's numerical properties (conditioning, rank, dynamic range) map onto physical precision budgets — a design axis the family never touches.
4. **A self-trained cheap representation under the head.** Their frozen features are ImageNet-supervised ViTs; ours is a tiny task-trained unsupervised SCFF bulk that must (and does — P7.0, P11.0 Δbulk +0.417 vs a random deep reservoir) beat the RanDumb control to justify existing.

**On the anisotropy failure mode:** our P7.2 finding (the lever is a tied covariance, +0.19, closed-form) got us to SLDA-level metric quality. The field has two closed-form rungs above it we have not climbed: (a) **DS-AL's compensation stream** — a second ridge solve on the main map's residual, in its null space, via a second activation: attacks under-fitting generically, no covariance storage blowup; (b) **shrunk per-class covariances re-anchored under drift** (Deep-SRDA's interpolation knob + AdaGauss's adapt-the-stored-Σ move, mean-only version of which is already our P9.4). And beneath both: **LoRanPAC's warning** that our exact solve `(G+λI)⁻¹M` may be riding an unmeasured ill-conditioned spectrum.

## The gap / what we haven't tried

1. **Dual-stream compensation (from DS-AL):** add a second closed-form stream over the same SCFF taps (different activation, residual fit in the main map's null space), summed at read. One extra Gram+solve; slots into the existing sleep unchanged; directly targets the anisotropy under-fit. *The single most testable lever.*
2. **Spectrum audit + TSVD solve (from LoRanPAC):** measure the condition number of our RanPAC Gram on the bench; if bad, replace the sleep re-fit's ridge solve with truncated SVD. On analog hardware, conditioning = dynamic range — this is also a substrate argument, and low-rank factorization shrinks the stored matrix below d².
3. **Covariance re-anchoring at sleep (from AdaGauss):** we re-anchor prototypes (P9.4) but carry covariance statistics stale; re-expressing stored Σ through the measured bulk rotation is the drift-aware anisotropy fix. Plus their rank diagnostic (old-class vs new-class feature rank) as a new every-run invariant.
4. **Exposed/unexposed bookkeeping (from GACL):** a cheap partial update path for revisited classes between full sleeps.
5. **Oracle guard (from ACIL):** on a deliberately frozen bulk, our sleep re-fit should reproduce the exact recursion bit-for-bit — a free correctness test of the namer path.
6. **External anchoring (from F-OAL/RanDumb):** drop our namer onto their OCIL one-pass protocol for an old-world-comparable number; keep the RanDumb control in every future bench.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [ACIL (Zhuang 2022)](zhuang-2022-acil.md) | ⭐⭐⭐⭐⭐ | The paradigm anchor: recursive ridge = joint solution; zero head-forgetting by algebra. |
| [Deep SLDA (Hayes 2020)](hayes-2020-deep-slda.md) | ⭐⭐⭐⭐⭐ | Our deployed head's source; the tied-covariance ceiling named. |
| [DS-AL (Zhuang 2024)](zhuang-2024-dsal.md) | ⭐⭐⭐⭐ | The closed-form fix for ridge under-fit: null-space compensation stream. |
| [GACL (Zhuang 2024)](zhuang-2024-gacl.md) | ⭐⭐⭐⭐ | Boundary-free mixed streams solved in-algebra; weight-invariance = head order-invariance is free. |
| [F-OAL (Zhuang 2024)](zhuang-2024-foal.md) | ⭐⭐⭐⭐ | Our deployment constraints, published: forward-only + online + closed-form. |
| [RanDumb (Prabhu 2024)](prabhu-2024-randumb.md) | ⭐⭐⭐⭐ | The skeptic control our bulk must (and does) beat; our P7.0 control's namesake. |
| [LoRanPAC (Peng 2025)](peng-2025-loranpac.md) | ⭐⭐⭐⭐ | Our exact solve is ill-conditioned in theory; TSVD is the principled repair + error bounds. |
| [AdaGauss (Rypeść 2024)](rypesc-2024-adagauss.md) | ⭐⭐⭐ | Stored covariances go stale under drift; adapt them — the anisotropy×drift bridge. |
| [AIR (Fang 2024)](fang-2024-air.md) | ⭐⭐⭐ | The output-side imbalance guard we tested and struck (CBRS won); the citation for that negative. |

## Leads spawned

- **Drift compensation as its own topic:** SDC (CVPR 2020) → LDC (ECCV 2024) → ADC (CVPR 2024) — "move the statistics, not the data" under representation drift; directly feeds the hippocampus-organ build.
- **Streaming/incremental SVD on analog substrates** (Brand 2002 lineage) — needed if the TSVD namer lever is taken.
- **Deep-SRDA shrinkage family** — the tied↔per-class interpolation knob as a one-cell bench test.
- **Analytic family beyond vision** — Analytic Subspace Routing (arXiv 2503.13575, LLMs), analytic schedulers for embodied models (arXiv 2506.09623): evidence the recursion is becoming infrastructure.
- **ORFit / orthogonal-GD↔RLS bridge** (arXiv 2207.13853) — the theory link between our GD-era instincts and the closed-form world.
- **LibContinual realistic-CL benchmark** (arXiv 2512.22029) — a 2025 external bench our namer could be scored on.
