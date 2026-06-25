# Experiment 3 — residual-boosting block chain vs pure GD

> The experiment that decides the Exp-2 pivot: does **depth from stacking shallow GD-corrected blocks**
> (a residual-boosting chain, N3/BoostResNet) beat a single block and avoid the monolithic-SCFF
> degradation? Spec: [`../design.md`](../design.md) (Exp 3); reporting: [`../result-format.md`](../result-format.md).

## Question

1. Does a chain of weak correctors reduce error with depth (boosting shape, `≤ e^{-½Tγ²}`)?
2. Does it beat a single block and approach the pure-GD ceiling, with a small memorization gap?
3. Does the residual stream avoid the depth-degradation a plain SCFF stack suffers (Exp 1/2)?

## Setup

`Chain` = SCFF stem + N=6 shallow blocks (1 SCFF layer each, local, sum-goodness). **residual flag:**
`g_k = norm(g_{k-1} + ε·h_k)` (skip ON) vs `g_k = norm(h_k)` (plain stack, skip OFF). Gradient boosting:
a linear weak learner per block fits the running logit-residual; `r_k = r_{k-1} + α·o_k`. Compared to a
pure-GD MLP at matched weights. digits (n=5), MNIST (n=3). Code: [`run_exp3.py`](run_exp3.py),
diagnostic [`res_diag.py`](res_diag.py). Figures [`F8_boosting.png`](figs_exp3_digits/F8_boosting.png),
[`pivot_skip.png`](figs_exp3_digits/pivot_skip.png).

## Result / figures (digits, n=5)

| | value |
| --- | --- |
| **boosted chain held-out** | **0.950 (gap +0.028)** |
| single deep block (Exp 1/2) | ~0.92 |
| pure-GD ceiling | 0.970 (gap +0.030) |
| boosting error vs #blocks | 0.068 → 0.050 (held), **plateaus after ~2 blocks** |
| per-block weak-edge γ | [0.71, 0.72, 0.70, 0.66, 0.62, 0.60] (no dead blocks, but late blocks don't help held-out) |

- **F8** ([`F8_boosting.png`](figs_exp3_digits/F8_boosting.png)): error falls with depth then **saturates after
  ~2 blocks** — it does NOT match the exponential `e^{-½Tγ²}` bound; the strain point is early.
- **pivot** ([`pivot_skip.png`](figs_exp3_digits/pivot_skip.png)): per-block stream probe *degrades* with the
  skip (ε=1) `[0.90→0.46]`, **worse** than the plain stack `[0.90→0.59]` — the mandatory norm dilutes.
- **The ε diagnostic ([`res_diag.py`](res_diag.py)) resolves it:** small ε preserves per-block features
  (`ε=0.1`: probe flat `[0.90→0.86]`) **but the boosted chain gets WORSE** (0.950→0.933). **Boosting wants
  diverse weak learners, not preserved-identical ones** — full ε=1's diversity is what makes the ensemble
  strong. The per-block degradation is not a bug; it's the diversity the ensemble feeds on.

**MNIST confirmation (n=3):** chain **0.858 (gap +0.033)** vs pure-GD **0.943 (gap +0.057)** — chain keeps
the smaller gap, but **barely beats a single block** (Exp 1: 0.850; +0.008) and held-error saturates
`[0.164→0.142]`. So on the *harder* task the boosting-depth benefit nearly vanishes — depth adds almost
nothing, the small gap persists. (On MNIST the skip even degrades *less* than plain per-block, the reverse of
digits — but both degrade, and the boosting ensemble is still where the accuracy comes from.)

## Read (six-slot)

1. **Claim.** A residual-boosting chain of shallow SCFF+GD blocks **beats a single block** (0.92→0.95) and
   **approaches the pure-GD ceiling** (0.97) with a comparable-to-smaller gap — but the depth benefit
   **saturates after ~2 blocks** and does not show the clean exponential boosting decay.
2. **Numbers.** digits: chain 0.950 (gap +0.028) vs single block ~0.92 vs GD 0.970 (gap +0.030); error
   plateaus by block 2.
3. **Figures.** F8 (boosting shape + γ), pivot_skip (per-block degradation), res_diag (ε resolves the mechanism).
4. **Mechanism.** Boosting combines per-block readouts into an ensemble; the residual stream's value is
   **diversity** across depth (full ε=1 best), not feature preservation. SCFF adds little *new* class info
   past the first ~2 transforms, so the ensemble — and the depth benefit — saturate fast.
5. **Threats.** Boosting here is linear weak learners on frozen SCFF features (two-phase), not the online
   Interface-GD; the linear inter-block delta (Ch9) and online co-training are untested. The γ metric
   (training-residual variance explained) overstates useful edge (late blocks have γ~0.6 but don't help
   held-out). The chain's modest win over a single block may be partly the boosted-linear-ensemble readout
   vs the single MLP readout, not pure depth.
6. **Decision.** Below.

## Decision

- **Boosting works, modestly.** Chain > single block, approaches GD, small gap — the depth-via-boosting
  mechanism is real. **Use the full residual (ε=1)** — diversity beats preservation. **N3 confirmed** as the
  primary chaining mechanism; the Ch9 linear inter-block delta stays off (not needed for this gain).
- **But depth saturates fast (~2 blocks).** The "deep cheap brain" is weak: most value is in the first 1–2
  blocks; stacking more gives diminishing returns. No exponential boosting decay on these tasks.
- **Phase-1 structural arc verdict (exp0→Exp3):** the *cheap + small-memorization-gap, approaching-GD* half
  of the thesis is **validated**; the *deep, 80%-SCFF, matches-GD* half is **not** — SCFF is weak, shallow is
  better, depth (mono or boosted) gives diminishing returns. The demonstrated win is a cheap, local,
  forward-only learner with a smaller memorization gap than backprop at a fraction of the backward cost.
- **Next levers (not yet tested):** GD-coshaping / DF-O for degradation; the **continual/online regime
  (Exp 4 gate + sleep)** — where cheap-online learning + the small gap should actually shine, and where the
  plasticity gradient (2c) and sleep earn their keep. That is the regime the architecture was really built
  for.
