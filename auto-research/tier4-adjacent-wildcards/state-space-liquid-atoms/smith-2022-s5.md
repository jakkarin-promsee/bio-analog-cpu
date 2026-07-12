# Simplified State Space Layers for Sequence Modeling (S5)

- **Authors / Year / Venue:** J. T. H. Smith, A. Warrington, S. W. Linderman / 2022 / ICLR 2023
- **Link:** https://arxiv.org/abs/2208.04933
- **Tier / Topic:** tier4 / t4.4 state-space & liquid atoms
- **Relevance:** ⭐⭐⭐⭐ — the parallel-**scan** MIMO SSM: shows the linear recurrence needs no convolution/FFT, just an associative scan — the form that maps most cleanly onto a settling analog array.

## TL;DR
S4 uses many independent single-input-single-output SSMs plus an FFT-convolution trick. S5 replaces them with **one multi-input-multi-output** diagonal SSM and computes it with a **parallel scan** instead of a convolution. Same efficiency, simpler, and — the point for us — the scan is just the associative combination of linear recurrence steps, i.e. "integrate the state forward," which is what an analog array does natively.

## The mechanism (how it actually works)
A linear recurrence `x_t = Ā x_{t-1} + B̄ u_t` is an **associative** operation: you can combine step-pairs in any grouping and get the same answer (a prefix scan), so the whole sequence's states compute in `O(log T)` parallel depth — no FFT, no Cauchy kernel. S5 diagonalizes `A` (initialized from HiPPO like S4) so each of the MIMO state channels is an independent complex leaky integrator, and runs the parallel scan over time. Dropping the SISO-bank + convolution machinery makes the layer conceptually a single state vector evolving under a diagonal transition — the plainest possible "bank of RC lines." Trained by backprop.

## Key results / claims
- 87.4% average on Long Range Arena; 98.5% on Path-X (hardest task).
- Matches S4's compute cost with a simpler, scan-based implementation.
- Establishes parallel-scan as the canonical way to run diagonal SSMs (Mamba later builds on this).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star recurrent atom; the analog substrate's "settle = compute" story.
- **Same as us:** the associative-scan view is the cleanest statement that a linear SSM is *just charge integration forward in time* — no special kernel, no solver. A diagonal MIMO SSM is one state vector under a fixed per-channel decay: exactly a leaky-cap register bank. This is the atom that drops onto our substrate with the least translation.
- **Different from us:** trained end-to-end by backprop; and the parallel scan is a *digital* speed trick — on true analog you don't need it, the physical array integrates in real (continuous) time, which is even cheaper. The mismatch is again the training rule, not the forward atom.
- **What we could borrow or test:** adopt the **diagonal MIMO SSM with fixed HiPPO decay** as the reservoir recurrence; because it's one shared state vector it's the simplest thing to hold in a leaky-cap array and read with our closed-form namer. S5's simplicity is a feature for a hardware mapping.
- **What contradicts or challenges us:** same as S4 — the published numbers train the SSM. A frozen-decay S5 reservoir's accuracy on our streams is the open question.

## Follow-on leads
- Parallel-scan hardware: does the analog array's continuous integration *replace* the scan entirely? (a clean thesis probe)
- Neuromorphic S5 (event-by-event deep SSMs, arXiv 2404.18508) — bridges to the `neuromorphic-spiking` folder.
- HiPPO initialization — the fixed-`A` reservoir recipe shared with S4.
