# Learning Iterative Reasoning through Energy Diffusion (IRED)
- **Authors / Year / Venue:** Yilun Du, Jiayuan Mao, Joshua B. Tenenbaum / 2024 / ICML 2024 (PMLR 235:11764–11776)
- **Link:** https://arxiv.org/abs/2406.11179 (project: https://energy-based-model.github.io/ired/)
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐ — annealed energy landscapes: **noise as a compute schedule** for the settle, and iteration count that scales with problem difficulty at test time.

## TL;DR
IRED formulates reasoning as energy minimization, but fixes the classic EBM problem (hard, non-convex landscapes) by learning a **sequence of annealed landscapes** — smooth/coarse first, sharp/exact last — diffusion-style. Inference descends through the sequence; because the stopping is governed by the landscapes rather than a fixed unroll, the solver can **spend more optimization steps on harder instances than it ever saw in training** and solve them.

## The mechanism (how it actually works)
Learn a family of energy functions E_k(x, y) indexed by a noise/temperature level k, exactly as diffusion learns denoisers at multiple noise scales: at high k the landscape is heavily smoothed (few, wide basins — easy to descend, roughly right), at low k it is sharp (exact constraints). Inference = start at the smoothest landscape, descend, hand the solution to the next-sharper landscape, repeat — coarse-to-fine optimization where each stage's answer initializes the next. Training combines score-function supervision (as in diffusion) with direct energy-landscape supervision, which they show trains faster and more stably than either alone. At test time, harder problems simply take more descent steps per stage / benefit from extra steps — adaptive compute emerges from the optimization view rather than from a halting head.

## Key results / claims
- Outperforms baselines on continuous algorithmic reasoning (matrix completion/inverse), discrete reasoning (Sudoku), and planning (graph pathfinding).
- **Out-of-distribution generalization by more compute:** solves harder Sudoku than trained on, matrix completion at larger value magnitudes, paths in larger graphs — by adapting the number of optimization steps at inference.
- The annealed-landscape sequence is the key enabler; single-landscape EBM inference gets stuck.

## How it relates to us
- **Organ / phase touched:** north-star loop; North-star 18 (analog noise & temperature) — this is the algorithmic use of that dial; P6's noise story.
- **Same as us:** iterative settle over an energy, with compute spent per-instance. And the annealing schedule is *physically native to us*: analog thermal noise is a temperature we already have — start the settle hot (noise smooths the effective landscape), cool as it converges. Simulated annealing on real physics instead of simulated.
- **Different from us:** the landscapes are learned deep networks trained with diffusion-style supervision (off-substrate); tasks are one-shot constraint problems, not streams; no explicit halt signal (stage schedule instead).
- **What we could borrow or test:** (1) a noise-scheduled settle — inject decaying noise into the loop state during relaxation and measure whether it escapes bad basins (the analog annealer experiment; ties directly to our P6 noise-augmentation finding that noise *helps* structure); (2) the coarse-to-fine idea maps to settling through the bulk's depth taps: settle the shallow (coarse) representation first, let it seed the deeper one; (3) their difficulty→steps curves are the template for our "ponder time tracks hardness" measurement.
- **What contradicts or challenges us:** IRED's generalization-by-more-compute needed the *learned* annealed family; raw physical annealing on a fixed energy may not inherit it. Also everything is trained offline with gradients — the on-chip version needs the energy to come from structure (LUT attractors) rather than training.

## Follow-on leads
- Du et al., "Learning Iterative Reasoning through Energy Minimization" (ICML 2022) — the pre-diffusion ancestor.
- Compositional energy minimization for generalizable reasoning (arXiv 2510.20607).
- Oscillator/Ising annealers as physical coarse-to-fine solvers (bridges to Laydevant card).
