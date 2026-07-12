# SymBa: Symmetric Backpropagation-Free Contrastive Learning with the Forward-Forward Algorithm
- **Authors / Year / Venue:** Heung-Chang Lee, Jeonggeun Song / 2023 / arXiv:2303.08418 (cs.CV/LG)
- **Link:** https://arxiv.org/abs/2303.08418 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐ — a goodness-loss fix for FF; relevant to *why we abandoned goodness entirely* rather than repairing it.

## TL;DR
FF's separate per-sample thresholded losses give **conflicting gradient directions** for positives vs negatives, which slows/destabilizes convergence. SymBa replaces them with a **single symmetric loss on the goodness gap** `G_pos − G_neg`, directly maximizing separation, plus an "Intrinsic Class Pattern" to inject class info. Faster convergence, better accuracy than vanilla FF.

## The mechanism (how it actually works)
Vanilla FF pushes `G_pos` up past `θ` and `G_neg` down past `θ` with two independent logistic terms — the two objectives can pull weights in opposing ways. SymBa optimizes one term over the **difference** `Δ = G_pos − G_neg` (a softplus/logistic on `Δ`), so positive and negative goodness are coupled and the update always widens the gap. The Intrinsic Class Pattern (ICP) is a fixed per-class code blended in so class identity survives the goodness compression.

## Key results / claims
Faster, more stable convergence and higher accuracy than FF on standard small benchmarks; still a **goodness-based, label-dependent** method (ICP needs class identity). Presented as a drop-in loss improvement to FF, not a new paradigm.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the SCFF-bulk objective (§2.1–2.2) — the "repair goodness vs replace goodness" decision.
- **Same as us:** contrastive framing (gap between two worlds); the diagnosis that FF's two-term loss is badly conditioned.
- **Different from us:** SymBa **repairs energy-goodness** and stays **label-dependent** (ICP). We **abandoned goodness altogether** — Phase 2 showed no repair to a *magnitude* functional (`Σh²`) can encode a *direction* (class axis), even with a perfect-oracle negative — and went **label-free InfoNCE**. SymBa is the "fix the loss" road; our result says the loss *functional* was the problem, not its balance.
- **What we could borrow or test:** the **symmetric-gap** idea (optimize the difference, not two thresholds) is already implicit in InfoNCE's log-ratio; nothing new to borrow, but it's the cleanest citation for *why balancing goodness isn't enough*.
- **What contradicts or challenges us:** SymBa reports goodness *can* be made to work better than FF suggested — a fair challenge, but on the axis (static small-task accuracy) where we already concede we don't compete; it does not touch depth-composition or continual-safety, where our replacement was motivated.

## Follow-on leads
Goodness-function design space (DeeperForward, cumulative-goodness critiques); symmetric/contrastive losses for FF; class-pattern injection vs label-free contrast.
