# Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations
- **Authors / Year / Venue:** Peiyi Wang, Lei Li, Zhihong Shao, R.X. Xu, Damai Dai, Yifei Li, Deli Chen, Y. Wu, Zhifang Sui — 2023 (ACL 2024), arXiv:2312.08935
- **Link:** https://arxiv.org/abs/2312.08935
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐ — the grounding recipe: grow a *dense* self-signal out of a *sparse verifiable outcome* by rollouts. How a system manufactures its own step-level supervision without labels.

## TL;DR
A process reward model (per-step verifier) trained with **zero human step labels**: each intermediate step is scored by running several completions from that step and checking what fraction reach the *verifiably correct final answer*. The automatic PRM matches/beats human-labeled process supervision and lifts both reranking (GSM8K 89.1%) and RL training (77.9→84.1%).

## The mechanism (how it actually works)
The problem: process supervision (per-step feedback) beats outcome supervision (final-answer feedback), but human step labels are the expensive ingredient (Lightman's PRM800K). The escape: **a step's quality is defined as its potential to lead to the right end** — a value function — and value can be *estimated by rollout* when the terminal outcome is checkable.

For each step s_i of a solution: sample K continuations from s_i to completion; check each final answer against the known-correct answer (math = a deterministic check); the step label is either hard (did any rollout succeed) or soft (the success fraction). Train the PRM on these machine-made labels. Use it two ways: rerank N sampled solutions (score = min/product over steps), or as the dense reward for step-by-step PPO.

The information flow is the whole point: **one sparse grounded bit (final answer correct?) is diffused backwards into a dense per-step signal by self-generated experience.** No human in the loop; the ground truth enters only at the terminal check.

## Key results / claims
- Verification: Mistral-7B + Math-Shepherd PRM reranking → **89.1% GSM8K / 43.5% MATH** (from 77.9/28.6 greedy), outperforming outcome-reward and self-consistency baselines.
- Reinforcement: PPO with the automatic step reward → 84.1% GSM8K without any verifier at test time.
- The automatic labels rival human step labels — the expensive ingredient was replaceable by compute + a checkable outcome.

## How it relates to us
- **Organ / phase touched:** sleep (the natural rollout window), the LUT (stored trajectories), the future learned-critic head, the gate's grounding channel.
- **Same as us:** we already live on sparse grounding — the labeled trickle + error-EMA is exactly a "terminal check" that arrives occasionally. This paper says that's *enough* to train a dense feeling, if we spend replay/rollout compute to spread it.
- **Different from us:** their terminal check is exact (math answer string match); our grounding events are noisy labels under drift. Soft labels (success fractions) and the sleep-window batching absorb some of that, but our version inherits label noise.
- **What we could borrow or test:** the **sleep-time critic-training recipe**. At sleep we hold trajectories (settle paths / tap states) and their eventual graded outcomes. Train the tiny critic head ("this state will be named correctly") on those machine-made labels — closed-form if the critic is ridge/prototype-form, which is our house algebra. The feeling then runs label-free awake and is re-fed by grounding at every sleep — a Math-Shepherd loop with sleep as the rollout budget. This is the concrete, substrate-native path from "error-EMA (sparse, labeled)" to "per-state confidence (dense, label-free)."
- **What contradicts or challenges us:** the recipe *requires* a checkable outcome somewhere. In arenas with no verifiable terminal event (pure unsupervised drift), the diffusion has nothing to diffuse — the feeling degrades to consistency-only signals (see Farquhar card). It quantifies our dependence on the labeled trickle rather than removing it.

## Follow-on leads
- OmegaPRM (Luo et al. 2024) — MCTS-style binary search making the rollout labeling cheaper.
- RLVR (reinforcement learning from verifiable rewards) — the general "ground in deterministic checks, dodge neural reward hacking" doctrine (see the PRM survey card).
- Lightman et al. 2023 (this folder) — the human-labeled ceiling this method approximates.
