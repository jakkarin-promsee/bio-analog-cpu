# Less is More: Recursive Reasoning with Tiny Networks (TRM)
- **Authors / Year / Venue:** Alexia Jolicoeur-Martineau (Samsung SAIL Montréal) / 2025 / arXiv Oct 2025
- **Link:** https://arxiv.org/abs/2510.04871 (code: https://github.com/SamsungSAILMontreal/TinyRecursiveModels)
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐⭐ — the buildable-scale existence proof: a **2-layer, 7M-param net recursing on a latent + an answer**, with a **one-head learned halt**, beating LLMs on hard puzzles.

## TL;DR
TRM strips the brain-inspired Hierarchical Reasoning Model (HRM, two nets at two frequencies + fixed-point gradient approximations + Q-learning halting) down to one tiny 2-layer network recursing over two variables — a latent scratchpad z and a current answer y — plus a halting probability head trained with plain BCE on "is the answer right." With 7M parameters it hits 45% on ARC-AGI-1 and 87.4% on Sudoku-Extreme, beating most frontier LLMs at <0.01% of their size.

## The mechanism (how it actually works)
Two variables, one network f. Within a *supervision step*: update the latent n=6 times, z ← f(x, y, z) — "recursive reasoning" over the scratchpad given the question and the current answer — then update the answer once, y ← f(y, z). Run T=3 of these cycles, the first T−1 = 2 **without gradients** (free-running thought), backprop only through the final cycle — no BPTT through the whole recursion, no implicit-function-theorem approximation (which the author shows was unsound in HRM). Deep supervision loops the whole thing up to 16 times, carrying (y, z) forward — each supervision step is "think a bit more, correct the answer."

**Halting:** HRM used a Q-learning head (halt/continue) needing a second forward pass. TRM "remov[es] the continue loss and only learn[s] a halting probability through a Binary-Cross-Entropy loss of having reached the correct solution" — one head, one pass: the net learns to *predict whether its own current answer is correct* and stops when that confidence crosses threshold.

## Key results / claims
- Sudoku-Extreme 87.4% (HRM 55.0%), Maze-Hard 85.3% (74.5%), ARC-AGI-1 44.6% (40.3%), ARC-AGI-2 7.8% (5.0%) — 7M params vs HRM's 27M.
- Above most LLMs (DeepSeek R1, o3-mini, Gemini 2.5 Pro) on ARC-AGI-1 with ~1/10000 the parameters, trained on ~1000 examples per task family.
- Less is more is causal, not incidental: 2 layers generalize better than 4 in their data regime; the two-net hierarchy, the fixed-point gradient trick, and the extra biological machinery all *hurt*.

## How it relates to us
- **Organ / phase touched:** north-star loop + the learned halt; the correctness-as-feeling head; scale-wise, the closest thing to our sim ladder.
- **Same as us:** the shape is our north star drawn small — a tiny fixed substrate re-applied many times, a scratchpad state that accumulates thought, an answer refined over iterations, and a halt that is literally *self-judged correctness* (the "feeling" as a trained confidence head). Also the anti-bio-ornament result rhymes with our house method: the engineering distillation beat the brain-derived original.
- **Different from us:** supervised puzzle-solving with full data-augmentation and offline training; gradients flow through the last recursion cycle (substrate-illegal); discrete token grids, not streams; halting trained with labels ("was I right"), which a lifelong stream only gets sparsely.
- **What we could borrow or test:** (1) the two-variable split (z scratchpad / y answer) is a clean loop architecture for our first recurrent sim — bulk features x frozen, z recirculates, y = the namer's running estimate fed back; (2) the halt head recipe: train/fit a tiny predictor of "namer correct?" from the loop state — note our closed-form namer already emits margin/confidence, so v0 can be fit-free; (3) the no-BPTT training schedule (free-run T−1 cycles, learn only on the last) is the *least* substrate-illegal gradient scheme in this folder — worth testing as the sim-side stand-in before EqProp.
- **What contradicts or challenges us:** TRM's wins live where thousands of clean supervised examples of one puzzle family exist; nothing here says the recursion helps a drifting sensor stream. The task-shape gap between "ARC puzzle" and "gas-sensor drift" is exactly what our loop experiment must bridge or bound.

## Follow-on leads
- Wang et al. 2025, Hierarchical Reasoning Model (arXiv 2506.21734) — the parent; useful for what TRM proved unnecessary.
- ARC Prize analyses of HRM (the independent ablations that motivated TRM).
- Probabilistic Tiny Recursive Model (arXiv 2605.19943) — uncertainty-aware TRM follow-on.
