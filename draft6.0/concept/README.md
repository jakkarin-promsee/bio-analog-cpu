# `concept/` — Learning-Algorithm Theory Notes

Pure-theory reference notes on **how neural networks learn** — the mainstream gradient-based optimizers and the local / biologically-plausible / forward-only alternatives.

**Scope, deliberately narrow:** this folder is *what each model is*, in clean theory — core idea, the math, the trade-offs. It is **not** about mapping these onto the analog-CPU / custom-ALU substrate yet; that connection is noted lightly where natural but is not the point here. Think of `concept/` as the reference library you read *before* deciding which mechanism the substrate should borrow.

> **Draft-6.0 note (June 2026).** This is a **survey of options**, not the current decision. Draft 5.1 chose **attribution** (`distribution-based.detail.md`) as the on-chip rule — and that choice was **invalidated** (the loss carried magnitude but never direction). **Draft 6.0 chose a SCFF + gradient-descent hybrid** instead — the papers behind it are in [`../ref/`](../ref/README.md), the decisions in [`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md). So below, where older notes call attribution *"the project's rule,"* read it as **"the draft-5.1 pick, now historical."** The survey itself is still the right map of the learning-rule landscape.

---

## How the files are organized

Two kinds of files:

- **`summary.detail.md`** — the **survey / index**. Every method in one place at "summary altitude": core idea + key formula + trade-off, enough to understand and compare. **Start here.** It covers ~35 methods across two parts (mainstream gradient-based optimizers; local/bio-plausible alternatives) with a comparison table.
- **`{model}.detail.md`** — **standalone deep-dives** for the methods worth full reading: complete derivation, every formula, benchmark, limitations. Each one leads with `Overview / Core Idea` then `Benchmark`, then everything below.

Every standalone file follows the same shape: **`## Overview / Core Idea` → `## Benchmark` → full detail → `Trade-offs`**.

---

## Reading order

1. **`summary.detail.md`** — the whole landscape. Decide what you care about.
2. **`gradient-descent.detail.md`** — the baseline everything else is defined against (and the project's comparison baseline).
3. Then dive into whichever standalone files the summary pointed you to.

---

## Index of standalone files

### Mainstream — gradient-based optimization

| File | What it is |
| ---- | ---------- |
| [`gradient-descent.detail.md`](gradient-descent.detail.md) | **The default/baseline.** The gradient, the update rule, backprop as the engine, SGD/mini-batch, convergence theory, the loss landscape. |
| [`momentum.detail.md`](momentum.detail.md) | Momentum (Polyak) & Nesterov — EMA of gradients, acceleration, $\kappa\to\sqrt\kappa$. Mirrors the project's Scap EMA-momentum register. |
| [`adam.detail.md`](adam.detail.md) | The adaptive-LR family: AdaGrad → RMSProp → Adam → AdamW, plus the variant zoo. The de-facto default optimizer. |
| [`second-order-methods.detail.md`](second-order-methods.detail.md) | Newton, Gauss-Newton/LM, BFGS/L-BFGS, conjugate gradient, natural gradient/K-FAC — and **why deep learning avoids them**. |

### Alternatives — local / biologically-plausible / forward-only

| File | What it is |
| ---- | ---------- |
| [`distribution-based.detail.md`](distribution-based.detail.md) | **Attribution / loss-sharing learning + LRP.** Route error by *contribution* ($\lvert a\cdot W\rvert$), not sensitivity. **The draft-5.1 learning rule** (invalidated — see the note above; kept for the history). |
| [`SCFF.detail.md`](SCFF.detail.md) | Self-Contrastive Forward-Forward — label-free, forward-only contrastive learning by summation. |
| [`SGR.detail.md`](SGR.detail.md) | Gradient Reconciliation for local block-wise learning — match backprop accuracy at >40% memory saving. |
| [`equilibrium-propagation.detail.md`](equilibrium-propagation.detail.md) | Equilibrium Propagation — energy-based, two-phase, computes the *exact* gradient from local physics. The leading **analog** candidate. |
| [`feedback-alignment.detail.md`](feedback-alignment.detail.md) | Feedback Alignment & Direct Feedback Alignment — the answer to the weight-transport problem (fixed random feedback still learns). |
| [`predictive-coding.detail.md`](predictive-coding.detail.md) | Predictive Coding as a learning algorithm — local prediction-error messages that provably approximate backprop. |
| [`topdown-bottomup.md`](topdown-bottomup.md) | Top-down/bottom-up processing & predictive coding **in the brain** — the neuroscience twin of `predictive-coding.detail.md`. |

---

## Conventions

- **Naming:** standalone algorithm deep-dives use `{model}.detail.md`. `topdown-bottomup.md` is the one **neuroscience** file (no `.detail` — it's biology, not a model).
- **Language:** English throughout.
- **Math:** LaTeX (`$…$` / `$$…$$`).
- **Each standalone file is self-contained** — all the math for that model lives in its own file; the summary only abstracts it.

---

## The anchors

If you read nothing else:

- **`gradient-descent.detail.md`** — the mainstream baseline every alternative is measured against (and, in draft 6.0, the precise ~20% of the model).
- **`SCFF.detail.md`** — the **draft-6.0 cheap brain**, the unsupervised ~80%. (Attribution / `distribution-based.detail.md` was the *draft-5.1* pick — read it for the history, not the current plan.)

Everything else in this folder is a point on the line between gradient descent's learning power and its non-local cost: *how much can you keep while dropping the cost?*
