# A Survey of Process Reward Models: From Outcome Signals to Process Supervisions for Large Language Models
- **Authors / Year / Venue:** Congmin Zheng et al. (11 authors) — 2025 (rev. 2026), arXiv:2510.08049
- **Link:** https://arxiv.org/abs/2510.08049
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐ — the 2025–2026 field map of machine-made correctness signals; documents the drift of the whole field toward *outcome-grounded, automatically generated* process signals and names the verification doctrine (RLVR) that dodges neural reward hacking.

## TL;DR
A lifecycle survey of process reward models: how step-level supervision data is generated (human → Monte-Carlo/automated → model-self-annotated), how PRMs are built, and how they are consumed (test-time reranking/search, RL reward). Covers the label-free frontier (FreePRM: pseudo-labels from outcome correctness; Self-PRM: RL-trained models internally inducing their own step-rewarder; AURORA: ensemble prompting + reverse verification) and the grounding doctrine: **RLVR** — where a deterministic check exists (test suites, exact-match answers), use it instead of a learned judge, avoiding neural reward hacking.

## The mechanism (the field's shape)
Three generations of "where does the step signal come from":
1. **Human step labels** (Lightman) — trustworthy, unscalable.
2. **Outcome-diffused labels** (Math-Shepherd, OmegaPRM, FreePRM) — a sparse verifiable terminal bit spread into dense step values by rollouts or pseudo-labeling. The trust is inherited from the terminal check.
3. **Self-generated labels** (Self-PRM, ensemble/reverse-verification schemes) — the model's own consistency structures used as supervision. Cheapest, and the closest to "correctness as a self-generated feeling" — and precisely the generation where the survey's reliability caveats concentrate.

Consumption side: PRMs steer test-time search (best-of-N, beam/tree search over steps — the PRM is a **halt/prune gate** inside the search) and provide dense RL rewards. The survey also aggregates PRM benchmarks (e.g., ProcessBench-style step-error detection) and the recurring failure: PRMs are themselves hackable when used as optimization targets — hence RLVR's "prefer deterministic verifiers when they exist."

## Key results / claims
- The field's trajectory is *away from human labels and away from pure introspection simultaneously* — converging on outcome-anchored automatic signals (generation 2) as the reliability sweet spot.
- RLVR framing: grounding supervision in objective checks avoids the alignment failures of learned reward models (the survey's anti-collapse doctrine, Gao's hump avoided by construction).
- Open problems named: PRM generalization across domains, step-segmentation for non-text processes, verifier hacking under search pressure.

## How it relates to us
- **Organ / phase touched:** north-star framing; the future critic; the gate's grounding channel.
- **Same as us:** the field's convergence point — dense self-signal, sparse objective anchor — is architecturally the loop we'd build (label-free feeling awake, grounded recalibration at sleep). Independent confirmation the shape is right.
- **Different from us:** their "process" is symbolic step sequences; the check is often exact string/test matching. Our process is an analog trajectory; our checks are noisy labels + physics (agreement, energy). Nothing in the taxonomy handles *continuous* processes — our settle-path scoring would be off-map, i.e., genuinely open territory.
- **What we could borrow or test:** the **generation-2 discipline** as a standing rule: any self-signal we deploy must inherit its trust from a checkable event, with the inheritance path written down (rollout, agreement count, labeled window). Generation-3 signals (pure self-consistency of the judge with itself) are flagged by the field itself as the hackable tier — a published reason to keep re-settle agreement (physics-sourced) and reject introspection-sourced confidence.
- **What contradicts or challenges us:** the survey's open problem "verifier hacked under search pressure" applies to our halt too: once the loop *searches* (settles repeatedly, keeps the best-feeling state), the feeling is under optimization pressure and Gao's hump returns through the side door. Search-over-settles must count as optimization-against-the-signal in our design rules.

## Follow-on leads
- FreePRM (weak-supervision PRM without ground-truth step labels) — the cheapest generation-2 recipe.
- Hard2Verify (arXiv:2510.13744) — step-verification benchmark at the open-ended frontier; how hard verification really is.
- "Process Reward Models That Think" (arXiv:2504.16828) — verifier-that-reasons; sequential self-check before judging.
