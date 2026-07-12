# Large Language Models Cannot Self-Correct Reasoning Yet
- **Authors / Year / Venue:** Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou — 2023 (ICLR 2024), arXiv:2310.01798
- **Link:** https://arxiv.org/abs/2310.01798
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐ — the null result that defines the requirement: a self-signal with no information advantage over the forward pass is worthless. Why the feeling must tap something the answer-producing path doesn't already output.

## TL;DR
Test "intrinsic self-correction": the model reviews and revises its own answer with **no external feedback and no oracle**. Result: accuracy does not improve — it often *drops* (GSM8K, CommonSenseQA, HotpotQA; GPT-3.5/4). Earlier positive self-correction results had quietly used ground-truth labels to decide when to stop correcting. Self-review flips correct answers to wrong about as often as the reverse.

## The mechanism (of the failure)
Why should asking the same model "are you sure?" add nothing? Information-theoretically, the review pass is a second sample from the same distribution, conditioned on a prompt that *suggests doubt*. Two consequences:
1. **No new evidence enters.** The model's best guess already used everything it knows; the critique pass has the same weights, same input. Any change is noise plus prompt-induced bias.
2. **The doubt prompt is itself a signal** — models systematically over-revise when told to reconsider, so the intervention has a directional artifact (away from the first answer), which hurts when the first answer was right.

The paper's decomposition of prior "self-correction works" claims: they either (a) used the true label as the stop rule (oracle leakage — the external ground truth was doing the work), (b) used external tools/feedback (fine, but not *self*), or (c) started from a weak baseline prompt. Under clean conditions the intrinsic effect is ≈0 or negative.

The positive scoping: self-correction *does* work when the checking direction has an advantage — external feedback (tool output, test suite), a task where verification is computationally easier than generation, or a critic trained on different data.

## Key results / claims
- GPT-4 on GSM8K: intrinsic self-correction *reduces* accuracy (e.g., ~95→~91 range in their runs); similar drops on CommonSenseQA and HotpotQA.
- Multi-agent "debate" among copies of the same model ≈ self-consistency voting with extra cost — agreement between clones is not independent evidence.
- Claims of successful self-correction in the literature traced to oracle labels in the loop.

## How it relates to us
- **Organ / phase touched:** the north-star halt/verify loop; the planned critic; the "mind inventing its own test cases" ambition (dossier §self-verification).
- **Same as us:** nothing deployed violates this yet — our gate consumes an *external* grounded quantity (labeled error-EMA). The paper endorses exactly that choice.
- **Different from us:** the failing setup is same-model-same-input introspection. Our candidate self-signals are *not* that: tap-drift is a **temporal** comparison (now vs the sleep anchor — new information: time), re-settle agreement is a **perturbation ensemble** (new information: independent noise draws), and the error-EMA is **external** grounding. Each has an information source the single forward pass lacks.
- **What we could borrow or test:** the acceptance criterion for any future feeling-head: **name its information advantage** before building it. Advantage can be (a) different data (critic trained on sleep-time graded trajectories — the Math-Shepherd card), (b) different time (drift vs anchor), (c) independent perturbations (re-settle ensemble), or (d) an asymmetric check (verification cheaper than generation — e.g., checking a settled state's consistency against the LUT is one CAM read, far cheaper than the settle that produced it). A proposed signal with none of these is Huang-null by construction and should be rejected on paper.
- **What contradicts or challenges us:** it kills the most seductive north-star shortcut — "the bulk re-reads its own settled state and decides if it feels right." Without an anchor/ensemble/outcome, that is intrinsic self-correction and will flip right answers to wrong. The dossier's "self-verification by inventing test cases" survives only because invented test cases come with *checkable outcomes* (epistemic action → grounded result), not free-floating introspection.

## Follow-on leads
- Kamoi et al. 2024 — "When Can LLMs Actually Correct Their Own Mistakes?" (a taxonomy of when self-correction is possible).
- Stechly et al. 2024 — self-critique failures in planning (GPT-4 can't verify its own plans) — the verification-isn't-easier regime.
- Generation-verification gap literature (verification easier than generation: when true, a same-weights verifier is still OK) — the boundary condition worth mapping for our tasks.
