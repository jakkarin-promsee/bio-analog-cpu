# The Predictive Forward-Forward (PFF) Algorithm
- **Authors / Year / Venue:** Alexander Ororbia, Ankur Mali / 2023 / arXiv:2301.01452 (cs.LG)
- **Link:** https://arxiv.org/abs/2301.01452 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐ — the predictive-coding branch of FF; relevant because we *tested and rejected* a reconstruction/generative objective (Phase 3), so PFF is the road we didn't take.

## TL;DR
Generalize FF by learning a **generative circuit jointly with a representation circuit**, both trained with forward passes only, wired together by **predictive coding** (each layer predicts the layer below), plus learnable lateral competition and noise injection. The generative side lets the model synthesize its own inputs and, in principle, its own negatives.

## The mechanism (how it actually works)
Two interacting stacks: a **representation circuit** (bottom-up, FF-style goodness per layer) and a **generative circuit** (top-down, predicts/reconstructs the activity of the layer below). Predictive-coding error signals between predicted and actual activity drive local updates — computed and applied **forward** (no global backprop). Lateral competition sparsifies each layer; injected noise regularizes. The generative circuit can dream up samples, so negatives need not be hand-crafted.

## Key results / claims
Comparable to backprop on small tasks (MNIST-scale) with a biologically-motivated, fully-local, forward learning process; demonstrates generation alongside classification. Emphasis is on plausibility and the joint representation+generation capability, not benchmark leadership.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the SCFF-bulk objective (§2.2) and specifically the **reconstruction-vs-contrast fork** of Phase 3.
- **Same as us:** forward-only, local, layer-wise; noise injection as a regularizer (we add a **noise-augmented contrastive view** in Phase 6 — same spirit, different mechanism).
- **Different from us:** PFF's core is **generative/predictive reconstruction**; our Phase 3 **pre-registered masked reconstruction and it FAILED** (it preserved density, below random — density ≠ class), so we adopted **InfoNCE contrast** instead. PFF also carries a full top-down generative stack; our bulk is bottom-up only, named by a separate closed-form head.
- **What we could borrow or test:** a **flat-vector predictive** objective (predict a held-out coordinate block rather than reconstruct it) is the one open alternative §2.2 explicitly leaves open — PFF is the closest prior art if we ever revisit it. The noise-injection-as-regularizer overlaps our Phase-6 finding.
- **What contradicts or challenges us:** PFF claims generative/predictive coding *does* compose forward-only — a mild tension with our result that *reconstruction* failed. Reconciliation: PFF predicts *across layers* (a fresh target per layer), whereas our failed control reconstructed *masked features at the same layer* — the distinction §2.2 flags as worth testing.

## Follow-on leads
Predictive coding as forward-only credit assignment (Millidge, Salvatori et al.); flat-vector predictive objectives; generative self-negatives; lateral competition / sparsity for FF layers.
