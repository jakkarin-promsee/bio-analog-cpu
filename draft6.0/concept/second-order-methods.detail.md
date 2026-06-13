# Second-Order & Curvature-Aware Methods

## Overview / Core Idea

First-order methods (SGD, momentum, Adam) know only the **slope** of the loss — the gradient. Second-order methods also use the **curvature** — how the slope itself is changing — encoded in the **Hessian** matrix $H = \nabla^2\mathcal{L}$ (all second partial derivatives). Knowing curvature lets you take a **much smarter step**: instead of "go downhill a fixed amount," you can solve for "jump straight to the minimum of the local quadratic approximation."

The defining method is **Newton's method**:

$$\theta_{t+1} = \theta_t - H^{-1}\,\nabla\mathcal{L}(\theta_t)$$

The $H^{-1}$ **rescales the gradient by curvature**: it stretches the step in flat directions (small curvature) and shrinks it in steep directions (large curvature). This cures the exact problem momentum only patches — the **ill-conditioned ravine** — at its root, and it does so with no learning rate to tune (near the optimum the natural step is $1$). The payoff is **quadratic convergence**: near a minimum, the number of correct digits *doubles* each iteration, versus the linear convergence of first-order methods.

So why is all of deep learning trained with first-order methods anyway? **Cost.** For $n$ parameters, the Hessian is $n\times n$ — storing it is $O(n^2)$ and inverting it is $O(n^3)$. For a model with $n = 10^9$ parameters, $H$ has $10^{18}$ entries. It is laughably infeasible. The entire field of second-order optimization is therefore about **approximating $H^{-1}\nabla\mathcal{L}$ without ever forming $H$** — quasi-Newton methods (BFGS/L-BFGS), curvature-free Krylov methods (conjugate gradient), and geometry-based preconditioners (natural gradient / K-FAC / Shampoo).

For this project the value of the chapter is mostly **knowing why you don't use them**, and where the one exception (L-BFGS on small/full-batch problems) lives — plus the conceptual link from **natural gradient** to "the right geometry for the update," which is the same instinct behind the project's normalized, conservation-based attribution.

---

## Benchmark

The headline is "best convergence per iteration, worst cost per iteration":

| Method | Convergence (near optimum) | Per-step cost | Memory | Used in DL? |
| ------ | -------------------------- | ------------- | ------ | ----------- |
| **Newton** | **quadratic** (digits double) | $O(n^3)$ (Hessian solve) | $O(n^2)$ | ❌ infeasible |
| **Gauss-Newton / LM** | super-linear (least-squares) | $O(n^3)$-ish | $O(n^2)$ | ❌ rare (small problems) |
| **BFGS** | super-linear | $O(n^2)$ | $O(n^2)$ | ❌ too big for deep nets |
| **L-BFGS** | super-linear | $O(mn)$ | $O(mn)$, $m\sim$10 | ⚠️ small / full-batch only |
| **Conjugate gradient** | linear, curvature-free | $O(n)$ per step | $O(n)$ | ⚠️ inner solver, full-batch |
| **Natural gradient (K-FAC)** | faster than 1st-order | block/Kronecker | moderate | ⚠️ research / some large-scale |

Reading it:

- **Newton converges in absurdly few iterations** (a handful, near the optimum) — but each iteration is unaffordable at deep-learning scale. The whole table is the search for the **sweet spot**: keep some curvature benefit, drop the $O(n^2)$–$O(n^3)$ cost.
- **L-BFGS** is the one classical second-order method that sees real use — but only on **deterministic / full-batch / smaller** problems (e.g. fine-tuning, physics-informed nets, classical ML), because it assumes low-noise gradients that mini-batching violates.
- **K-FAC and friends** are the active frontier for making natural gradient tractable on large nets; they sometimes win on wall-clock but are not yet the default — Adam's simplicity keeps winning.

---

## Newton's method — the ideal

Take the second-order Taylor expansion of the loss around the current point:

$$\mathcal{L}(\theta + \Delta) \approx \mathcal{L}(\theta) + \nabla\mathcal{L}^{\top}\Delta + \tfrac{1}{2}\Delta^{\top}H\Delta$$

Minimize this quadratic in $\Delta$ (set its gradient to zero): $\nabla\mathcal{L} + H\Delta = 0 \Rightarrow \Delta = -H^{-1}\nabla\mathcal{L}$. Hence the Newton step:

$$\theta_{t+1} = \theta_t - H^{-1}\nabla\mathcal{L}(\theta_t)$$

What $H^{-1}$ buys you:

- **Curvature rescaling.** In a direction of high curvature (steep, narrow), $H$ is large, $H^{-1}$ is small → take a *small* step (don't overshoot the wall). In a low-curvature direction (flat, gentle), $H^{-1}$ is large → take a *big* step (cover ground). This is the ravine problem solved exactly, per-direction — it makes the effective condition number $1$.
- **No learning rate.** The natural step size is built into $H^{-1}$; near a quadratic minimum the step lands you essentially *at* the minimum in one move.
- **Quadratic convergence.** Near the optimum the error squares each step — a few iterations to machine precision.

**Why it fails in practice:**

1. **Cost.** $H$ is $n\times n$: $O(n^2)$ to store, $O(n^3)$ to invert. Fatal for large $n$.
2. **Non-convexity.** Far from a minimum, $H$ can be **indefinite** (negative curvature directions). Then $-H^{-1}\nabla$ can point *uphill* — Newton happily steps toward a saddle or maximum. Practical use needs damping/modification (e.g. trust regions, $H+\lambda I$).

Everything below is a way to get (1) under control, sometimes (2) too.

---

## Gauss-Newton & Levenberg-Marquardt (least squares)

For a **sum-of-squares** loss $\mathcal{L}=\tfrac12\|r(\theta)\|^2$ (residuals $r$), the Hessian is approximately $H \approx J^{\top}J$ where $J = \partial r/\partial\theta$ is the Jacobian — this drops the expensive second-derivative term and is always **positive semi-definite** (fixing Newton's indefiniteness problem). That is the **Gauss-Newton** approximation.

**Levenberg-Marquardt** damps it with a $\lambda I$ that interpolates between Gauss-Newton and gradient descent:

$$\Delta = -\bigl(J^{\top}J + \lambda I\bigr)^{-1}J^{\top}r$$

Small $\lambda$ → Gauss-Newton (fast near the optimum); large $\lambda$ → gradient descent (safe far away). LM is the workhorse for **small nonlinear least-squares** (curve fitting, bundle adjustment, classical neural nets), not large deep nets.

---

## Quasi-Newton: BFGS and L-BFGS

Quasi-Newton methods **never compute $H$**. They *build up* an approximation to $H^{-1}$ from the gradients they observe along the way, using the **secant condition**: how much the gradient changed over the last step tells you about the curvature in that direction.

**BFGS** maintains a full $n\times n$ approximation $B \approx H^{-1}$ and updates it each step from the parameter change $s_t = \theta_t-\theta_{t-1}$ and gradient change $y_t = \nabla\mathcal{L}_t - \nabla\mathcal{L}_{t-1}$ via a rank-2 update. Super-linear convergence, no Hessian — but still $O(n^2)$ memory.

**L-BFGS (limited-memory BFGS)** is the practical version: instead of the full matrix, it stores only the **last $m$ pairs** $(s_t, y_t)$ (typically $m=5$–$20$) and reconstructs the action of $B$ on the gradient by a two-loop recursion. Memory drops to $O(mn)$ — linear in the parameters. L-BFGS is the **one second-order method with real traction**, but with a caveat that matters here:

> L-BFGS assumes **low-noise (deterministic) gradients**. Its curvature estimate is corrupted by mini-batch noise, so it is used on **full-batch or large-batch / deterministic** objectives — classical ML, fine-tuning, physics-informed networks, small nets — **not** standard noisy mini-batch deep learning. That is precisely why SGD/Adam, not L-BFGS, train big models.

---

## Conjugate gradient (curvature-free)

Conjugate gradient (CG) minimizes a quadratic in at most $n$ steps **without storing any matrix** — it only needs Hessian-*vector* products $Hv$ (which can be computed cheaply via a "Pearlmutter trick," at the cost of one extra backward pass, without forming $H$). It walks along a sequence of mutually **conjugate** directions so that progress in one direction is never undone by later steps. CG is the inner engine of **Hessian-free optimization** (Martens, 2010), which applied truncated-Newton ideas to deep nets by solving the Newton system approximately with CG. Powerful, but heavy per step and largely superseded by Adam/K-FAC for mainstream use.

---

## Natural gradient — the right geometry

Natural gradient changes *which space you measure distance in*. Ordinary gradient descent treats parameter space as flat Euclidean — but a fixed step in parameter space can mean a tiny or enormous change in the network's actual **function/output distribution**, depending on where you are. Natural gradient (Amari) measures the step in the geometry of the **output distribution** using the **Fisher information matrix** $F$ as the metric:

$$\theta_{t+1} = \theta_t - \eta\,F^{-1}\nabla\mathcal{L}, \qquad F = \mathbb{E}\bigl[\nabla\log p\,\nabla\log p^{\top}\bigr]$$

The natural gradient is the **steepest descent in distribution space** — the direction that most reduces the loss per unit of change *in what the network computes*, not per unit of change in the raw numbers. It is **invariant to reparametrization** (it does not care how you happened to coordinatize the weights), which is a deep and desirable property. The catch is the same as Newton's: $F$ is $n\times n$.

**Tractable approximations:**

- **K-FAC (Kronecker-Factored Approximate Curvature)** approximates each layer's Fisher block as a **Kronecker product** $A\otimes G$ of two small factors (input covariance ⊗ output-gradient covariance), so the inverse factorizes into two small inverses. This makes natural gradient affordable per layer and is the leading practical natural-gradient method.
- **Shampoo** uses Kronecker-factored preconditioners built from gradient statistics; a descendant idea now used in some large-scale training.

The reason natural gradient is worth knowing for this project: it is the formal statement that **the geometry of the update matters as much as the direction** — that you should normalize the step by the right metric. The project's attribution rule makes a kindred move with its **per-target normalization** ($|a\cdot W|/\sum|a\cdot W|$): conservation/normalization is a (cheap, local) way of imposing a sensible geometry on how error is shared, rather than letting raw magnitudes run unnormalized. Natural gradient is the expensive, exact version of "use the right metric"; attribution's normalizer is the cheap, local cousin.

---

## Why deep learning mostly avoids second-order methods

1. **Scale.** $O(n^2)$–$O(n^3)$ is impossible at billions of parameters; even the approximations add real overhead.
2. **Stochasticity.** Mini-batch gradient noise corrupts curvature estimates (Hessian/Fisher), which need to be accurate to help. First-order methods tolerate noise gracefully; second-order methods are fragile to it.
3. **Non-convexity.** Indefinite Hessians make raw Newton steps unsafe without damping/trust regions.
4. **First-order is "good enough."** Momentum + adaptive scaling (Adam) recover *much* of the curvature benefit (Adam's $1/\sqrt{v}$ is a crude diagonal preconditioner) at a tiny fraction of the cost. The marginal gain of true second-order rarely pays for its complexity at scale.

Where they *do* win: small/medium deterministic problems (L-BFGS), least-squares (LM), and research settings chasing wall-clock wins on huge models (K-FAC, Shampoo, Sophia's diagonal-Hessian shortcut).

---

## Relevance to the project

- **They are the "too expensive" end of the spectrum** — the opposite pole from the project's local, derivative-free attribution rule. An analog, resident-weight substrate cannot form, store, or invert an $n\times n$ curvature matrix; second-order methods are categorically off the table for the substrate, and saying *why* sharpens the case for cheap local rules.
- **Natural gradient is the conceptual bridge.** Its lesson — *normalize the update by the right geometry* — is exactly what the attribution rule's per-level normalization does cheaply and locally. Adam's diagonal $1/\sqrt v$ is the same lesson, cheaper still. The project sits at the far-cheap end of this same axis.
- **Adam already imports the affordable 10%.** Knowing that Adam's denominator is a crude diagonal curvature estimate tells you that the project's deferred "Adam-style $v_t$ remediation" (`adam.detail.md`) is, in effect, importing the *only* slice of second-order information cheap enough to live on the substrate.

---

## Trade-offs (summary)

```
Second-order / curvature-aware methods:
  ✅ use curvature → quadratic convergence (Newton); cures ill-conditioning at the root
  ✅ no/auto learning rate near the optimum; far fewer iterations
  ✅ natural gradient = reparametrization-invariant, steepest descent in function space
  ✅ L-BFGS is genuinely useful on small/full-batch/deterministic problems
  ✅ K-FAC / Shampoo make natural gradient tractable per-layer (active frontier)
  ❌ Hessian is O(n²) to store, O(n³) to invert — infeasible at deep-learning scale
  ❌ fragile to mini-batch gradient noise (curvature estimates get corrupted)
  ❌ indefinite Hessians (non-convexity) make raw Newton steps unsafe without damping
  ❌ categorically off-table for a local/analog substrate — cannot form or invert big matrices
```
