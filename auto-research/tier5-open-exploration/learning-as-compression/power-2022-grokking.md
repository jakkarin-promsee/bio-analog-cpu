# Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets
- **Authors / Year / Venue:** Alethea Power, Yuri Burda, Harri Edwards, Igor Babuschkin, Vedant Misra (OpenAI) / 2022 / arXiv (ICLR 2022 workshop)
- **Link:** https://arxiv.org/abs/2201.02177
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐ — the phenomenon that *compression can happen long after fitting*; a warning that "converged training loss" ≠ "found the compressed solution."

## TL;DR
On small algorithmic datasets, a network can **memorize** the training set to zero error and sit at chance test accuracy for a very long time — then, *long past overfitting*, validation accuracy **suddenly jumps to perfect generalization**. This delayed transition is "grokking." **Weight decay** is what makes it happen; smaller datasets need vastly more optimization to grok.

## The mechanism (how it actually works)
Train a small transformer on a modular-arithmetic table (e.g. `a ∘ b mod p`) with only a fraction of the entries visible. Early on, the network memorizes the visible entries — training loss hits zero, test loss stays high. If you keep training under a regularizer (weight decay), nothing visibly happens for thousands of steps, then the network **abruptly** generalizes: it has found the *algorithm* behind the table rather than the lookup. The interpretation (developed fully by Nanda 2023) is a **compression race**: the memorizing solution and the generalizing solution both fit the training data, but the generalizing one has smaller weight norm, so weight decay slowly pushes the network from the big (memorized) solution to the small (algorithmic) one. Generalization = the compressed solution winning, and the *delay* is how long it takes the regularizer to complete the compression. Dataset size sets the pressure: less data → weaker signal for the compact solution → more optimization needed.

## Key results / claims
- **Delayed generalization**: chance → perfect, well after training error saturates.
- **Regularization (weight decay) is critical** to induce grokking.
- **Smaller datasets → much longer to grok** — an inverse data/optimization relationship.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk convergence diagnostics, the learning-is-compression frame, the invariants we check every run.
- **Same as us:** grokking is "learning IS compression" caught in slow motion — the network keeps compressing after loss looks done. Our double-descent read ("the noise refutes itself, leaving the real shape") is the same story on a different axis.
- **Different from us:** grokking is a *backprop + weight-decay + fixed-dataset* effect on a clean algorithmic task; our bulk is forward-only, streamed, and never revisits a fixed table under a global regularizer. We should not expect literal grokking.
- **What we could borrow or test:** the *diagnostic caution* — our methodology checks "convergence / loss-slope" as an invariant, but grokking shows a flat loss can hide an ongoing (or not-yet-started) compression. For our bulk, a better readiness signal than "loss stopped moving" would be a **compression/probe measure** (codelength, or probe-accuracy trajectory), not the training objective alone.
- **What contradicts or challenges us:** grokking's driver is an explicit weight-norm regularizer selecting the compact solution. Our forward-only local rule has **no global weight-decay pressure** toward the compressed solution — so the mechanism that *completes* compression in grokking is one we may lack, which could explain why our bulk sometimes plateaus below the achievable structure.

## Follow-on leads
- Nanda et al. 2023 (progress measures) — the mechanistic explanation of *why* grokking is compression.
- Liu et al. 2022 "Omnigrok" / "Towards understanding grokking" — grokking as a representation-norm phase transition; possibly a substrate-relevant knob.
- Weight-norm / implicit-regularization as the compression driver — does our substrate have an analog of it?
