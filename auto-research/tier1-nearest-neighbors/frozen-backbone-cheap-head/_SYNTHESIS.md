# Synthesis — Frozen-backbone + cheap-head continual learning  (Tier 1)
**The question:** Who else freezes a backbone and adapts only a light head/prompt — and does that literature's success depend on a strong pretrained backbone we don't have? How much does the frozen representation's *source* matter (internet-scale pretrain vs our self-grown, unsupervised, forward-only SCFF bulk)?
**Already in `draft6.0/research/`:** the head-side of this story is fully carded (phase7: RanPAC, Deep-SLDA, the analytic-CL/RLS family, FeCAM, RanDumb; t1.2 re-carded the analytic heads). This folder covers what phase7 did **not**: the prompt/adapter/LoRA PTM-CL paradigm and the representation-source question itself.

## The landscape (2–4 paragraphs)

Since L2P (CVPR 2022) the dominant continual-learning recipe has been: take a ViT pretrained on ImageNet-21k, freeze it, and confine all sequential learning to a tiny writable surface. The field then split into three camps (the IJCAI-2024 survey's taxonomy). **Prompt-based** methods make the writable surface a set of learned input tokens with instance-wise retrieval (L2P → DualPrompt → CODA-Prompt, whose contribution was making the retrieval differentiable — i.e., *more* gradient machinery). **Representation-based** methods drop learning almost entirely: prototype or Gaussian-statistics heads over the frozen features (SimpleCIL, FSA's LDA head, RanPAC). **Adapter/LoRA-based** methods write, but carefully — per-task adapters spanning disjoint subspaces (EASE), or LoRA updates pre-projected into subspaces orthogonal to what old tasks need (InfLoRA); SLCA is the boundary case that fine-tunes everything but ~100× slower in the body than the head.

The field's own skeptics then demonstrated something remarkable: the second camp — the one with *no learning machinery at all* — matches or beats the other two. Janson et al. (2022): NCM on raw frozen features ≈88.5% on 10-split CIFAR-100, above most published methods. SimpleCIL (IJCV 2024): prototype classifiers beat prompt SOTA with zero downstream training. FSA (ICCV 2023): adapt the body *once*, freeze, run an exactly-updatable LDA head — beats SOTA in 15/16 settings, with the explicit finding that **continuous body adaptation is counterproductive**. The survey's matched re-evaluations confirm the pattern: under a fixed pretrained checkpoint, elaborate methods' margins shrink toward the prototype floor.

Two papers explain *why*. Mehta et al. (JMLR 2023): pretraining parks the model in wide, flat loss basins, so sequential updates displace old solutions less — forgetting resistance is largely a property of the *initialization*, not the CL algorithm. And Tang et al. (ICCV 2023) ran the decisive control: with weak or mismatched pretraining, prompt-based methods **collapse** — "their models could be trapped if the potential gap between the pretraining task and unknown future tasks is large." So the answer to the topic's central question is a documented **yes**: the paradigm's success is conditional on a strong pretrained backbone matched to the stream. The standard benchmarks (ImageNet pretrain → ImageNet-derived splits) quietly maximize that match, which is the survey's fairness complaint.

## How WE differ  ← the money section

**Topologically we are inside this paradigm; ontologically we are its missing control group.** Our object — frozen-to-labels representation + streaming closed-form prototype head — is the field's *representation-based* camp, line for line (FSA is the nearest twin: frozen body + LDA/SLDA-style exact head; SimpleCIL/RanPAC are the same shape). Nothing about the head is novel anymore, and we should say so plainly: the cheap-head half of our architecture is now **commodity**, independently converged on by a field with no substrate constraints at all. That convergence is *validation* of the design pattern, not our contribution.

What is genuinely ours is the axis the field never varies: **where the frozen representation comes from.** Every paper here inherits a supervised/internet-scale pretrain; the field's own evidence (Janson, SimpleCIL, Tang, Mehta) says that pretrain *is* most of the win. We cannot have it — no offline corpus, no labels, no off-chip phase — so our bulk is grown unsupervised, forward-only, from the deployment stream itself. The blunt version of the crux: **if the field's win is really the pretrain, our absolute accuracy can never ride their curve, and no head cleverness will change that.** Our P4/P10/P11 results already priced this honestly (we trail static accuracy, always). The claim that survives is different in kind: (1) on-substrate formation where pretraining is *impossible*, (2) a representation whose "pretrain distribution" is definitionally matched to the stream — Tang's failure mode (pretrain-stream gap) cannot exist for us, and the P11 gas-drift win over tuned ER is the existence proof that a stream-grown bulk beats a static representation under real drift; (3) the P11.0 decomposition (Δbulk vs matched random reservoir: +0.417 synth-home, ≈0 near-linear digits) is exactly the "does the representation earn anything beyond its floor" control that Janson/RanDumb demanded of the PTM field — we ran it on ourselves, and where it says ≈0 we are honestly "SLDA with extra steps."

One more real difference: the field's trunks are frozen *absolutely* (L2P) or after session 1 (FSA/APER); our bulk stays label-free-plastic forever (frozen only to GD). FSA's "continuous adaptation is counterproductive" is a direct published bet **against** our design choice — but their "adaptation" is supervised; ours cannot chase labels. Whether *unsupervised* continuous plasticity escapes their verdict is an open, decidable question, and the single most valuable experiment this topic surfaces (below).

## The gap / what we haven't tried

1. **The FSA control (the biggest lever):** run our full system with SCFF *halted after a formation window* (bulk hard-frozen) vs the committed always-plastic bulk — on the stationary home *and* the P11 drift arenas. If frozen-after-warmup ties on stationary but loses on gas-style drift, we get the cleanest statement of what stream-grown continuous plasticity buys, and the scoped rebuttal to FSA. If it ties everywhere, the always-on SCFF update circuitry is dead weight and the energy story must be re-cut.
2. **Formation-budget curve (Tang's protocol, on us):** namer accuracy vs bulk formation budget (steps/width) — our own "how much representation does the cheap head need" curve, locating us on the weak-pretrain axis the field just discovered.
3. **EASE-style similarity-weighted prototype reconstruction at sleep:** rebuild stale prototypes of classes unseen since the last sleep from their old-frame similarity to freshly re-anchored classes (one closed-form matrix step) — targets the P10 REV-staircase staleness mechanism directly.
4. **APER's merge trick, read-side:** tap a stored formation-era snapshot view alongside the live bulk ([early ‖ current] concatenated read) as insurance against SCFF rotation — closed-form-compatible.
5. **InfLoRA-flavored write-shaping of the one writable surface we have:** project SCFF updates away from the subspace the deployed reader taps (fixed cheap projection), slowing reader-relevant rotation — the bulk-side attack on staleness flagged in P10.
6. **Flatness diagnostic (Mehta, transplanted):** measure readout-loss sharpness in tap-space as the bulk forms — a field-legible measure of representation quality beyond probe accuracy.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Janson 2022 — NCM simple baseline](janson-2022-simple-baseline-ncm.md) | ⭐⭐⭐⭐⭐ | The field's confession: the backbone does the work; the head is commodity. |
| [Zhou 2023 — SimpleCIL / ADAM(APER)](zhou-2023-simplecil-aper.md) | ⭐⭐⭐⭐⭐ | Prototype-on-frozen-PTM beats prompt SOTA; adapt-once-then-freeze; the merge trick. |
| [Panos 2023 — FSA](panos-2023-fsa.md) | ⭐⭐⭐⭐⭐ | Our nearest published twin (frozen body + exact LDA head); the anti-plasticity bet to test. |
| [Tang 2023 — APG / weak pretraining](tang-2023-apg-weak-pretraining.md) | ⭐⭐⭐⭐⭐ | The direct answer: prompt-CL collapses without strong matched pretraining. |
| [Mehta 2023 — role of pre-training](mehta-2023-role-of-pretraining.md) | ⭐⭐⭐⭐ | The mechanism: pretraining → wide minima → implicit forgetting protection. |
| [Zhang 2023 — SLCA](zhang-2023-slca.md) | ⭐⭐⭐⭐ | Two-timescale (slow body / fast head) + post-hoc Gaussian re-fit ≈ our sleep, published. |
| [Wang 2022 — L2P](wang-2022-l2p.md) | ⭐⭐⭐ | The paradigm anchor; key-query prompt retrieval. |
| [Smith 2023 — CODA-Prompt](smith-2023-coda-prompt.md) | ⭐⭐⭐ | Prompt-side SOTA = *more* gradient machinery — the direction we didn't take. |
| [Zhou 2024 — EASE](zhou-2024-ease.md) | ⭐⭐⭐ | Per-task adapter subspaces + similarity-based prototype reconstruction (borrowable at sleep). |
| [Liang 2024 — InfLoRA](liang-2024-inflora.md) | ⭐⭐⭐ | Write-carefully-in-orthogonal-subspaces — the principled middle between freeze and fine-tune. |
| [Zhou 2024 — PTM-CL survey](zhou-2024-ptm-cl-survey.md) | ⭐⭐⭐ | The taxonomy + fairness critique; the one-sentence placement of us for this audience. |

## Leads spawned

- **Self-supervised-pretrained backbones for CL** (vs supervised) — the half-step between the field's pretrain and our unsupervised bulk; does label-free pretraining change the flatness/forgetting story?
- **"Reflecting on the State of Rehearsal-free CL with Pretrained Models" (2406.09384)** — 2024 critical analysis; candidate anchor for a deeper representation-source topic.
- **Feature-drift compensation in exemplar-free CIL** (prototype-correction line) — the gradient-world mirror of P9.4 proto-reanchor; worth a component-level topic.
- **GPM / orthogonal-subspace write protection (2103.09762 lineage)** — pre-PTM ancestors of InfLoRA; relevant if we ever shape SCFF writes.
- **Task-count scaling of fixed-capacity prototype memories** — EASE grows linearly; our C=20 crossover needs a task-count-scaling rung to answer the fixed-silicon question.
- **LAMDA-PILOT harness on our arenas** — running the field's methods on P11 arenas would put "their object on our bench" (heavy; only if a public comparison is ever needed).
