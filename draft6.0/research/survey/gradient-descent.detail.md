# Gradient Descent (the default / baseline)

## Overview / Core Idea

Gradient descent is the **mainstream** way to train almost every neural network, and it is the **baseline this whole project measures itself against**. Every method in the `survey/` folder — attribution, forward-forward, equilibrium propagation, feedback alignment — is defined by *which part of gradient descent it refuses to pay for*. So you need the baseline cold before the alternatives mean anything.

The idea is one sentence: **to make a loss smaller, repeatedly step the parameters a little bit in the direction of steepest decrease — the negative gradient.**

$$\theta_{t+1} = \theta_t - \eta\,\nabla_\theta \mathcal{L}(\theta_t)$$

That is the whole algorithm. Everything else — backprop, SGD, momentum, Adam, second-order methods — is either *how you compute the gradient* $\nabla_\theta\mathcal{L}$ or *how you turn that gradient into a better step than the raw $-\eta\nabla$.*

Two pieces make it work in practice:

1. **The gradient itself** answers "if I nudge each parameter, how does the loss change, and in what direction?" It is the vector of partial derivatives $\partial\mathcal{L}/\partial\theta_i$. It points uphill; you go the other way.
2. **Backpropagation** is how the gradient is actually computed in a deep network — reverse-mode automatic differentiation, the chain rule applied backward through the layers. This is the expensive, non-local machinery (weight transport, the activation derivative, a global backward pass, a frozen forward state) that the biologically-plausible alternatives are all trying to avoid.

Gradient descent asks the **sensitivity** question — "how much does the loss change if I wiggle this weight?" — which is exactly the question the project's attribution rule (`distribution-based.detail.md`) replaces with the **contribution** question ("how much did this weight contribute to the output?"). Holding both in your head is the point: gradient descent is the gold standard for *accuracy of direction*, and the price of that gold standard is the four non-local requirements below.

---

## Benchmark

Gradient descent has no single accuracy number — it *is* the reference everything else is quoted against ("within 1% of backprop," "matches BP on MNIST"). Its "benchmark" is its **convergence guarantees**, which are the strongest of any method here:

| Problem class | Plain GD (full batch) | SGD (stochastic) |
| ------------- | --------------------- | ---------------- |
| **Convex, smooth** | $\mathcal{O}(1/t)$ — error $\sim 1/t$ after $t$ steps | $\mathcal{O}(1/\sqrt{t})$ |
| **Strongly convex, smooth** | **linear** — $\mathcal{O}(\rho^t)$, $\rho<1$ (geometric) | $\mathcal{O}(1/t)$ (with decaying LR) |
| **Non-convex (deep nets)** | converges to a **stationary point** ($\nabla\mathcal{L}\to 0$); no global-optimum guarantee | same, but the gradient *noise* helps escape saddle points and sharp minima |

Reading it:

- On nice (convex) problems gradient descent has provable, fast convergence — this is why it is trusted.
- On deep networks (non-convex) there is **no guarantee of reaching the global optimum** — only a stationary point. Yet it works spectacularly in practice, because high-dimensional loss landscapes have few bad local minima and many benign saddle points, and SGD's noise shakes the iterate out of the bad ones.
- The trade between **GD and SGD** is exactness vs. cost: full-batch GD computes the true gradient (smooth, fast per-step convergence) but must touch the entire dataset for one step; SGD uses a noisy estimate from a mini-batch (slower per-step convergence) but takes thousands of steps in the same wall-clock time and generalizes better. SGD wins for deep learning and is the project's actual comparison baseline.

---

## The gradient and the update rule

The loss $\mathcal{L}(\theta)$ is a scalar function of all parameters $\theta = (\theta_1,\dots,\theta_n)$. Its **gradient** is the vector of partial derivatives:

$$\nabla_\theta\mathcal{L} = \Bigl(\frac{\partial\mathcal{L}}{\partial\theta_1},\ \frac{\partial\mathcal{L}}{\partial\theta_2},\ \dots,\ \frac{\partial\mathcal{L}}{\partial\theta_n}\Bigr)$$

Key facts:

- $\nabla\mathcal{L}$ points in the direction of **steepest increase** of the loss. The negative gradient $-\nabla\mathcal{L}$ points in the direction of steepest decrease — locally the best possible step direction.
- The update $\theta \leftarrow \theta - \eta\nabla\mathcal{L}$ moves downhill by a step scaled by the **learning rate** $\eta$.
- At a minimum, $\nabla\mathcal{L} = 0$, so the update stops moving — a fixed point. (Saddle points and maxima also have zero gradient, which is a problem; see the landscape section.)

This is **first-order** information only: it knows the slope, not the curvature. It does not know whether the valley ahead is gentle or steep — which is exactly what momentum and second-order methods try to add.

---

## Backpropagation — how the gradient is actually computed

In a deep network you cannot write $\partial\mathcal{L}/\partial\theta_i$ by hand; you compute it with **backpropagation**, which is **reverse-mode automatic differentiation** — the chain rule applied backward through the network.

**Forward pass:** compute and *cache* every layer's pre-activation and activation:

$$z_l = W_l\,a_{l-1}, \qquad a_l = \sigma(z_l), \qquad \hat{y} = a_L.$$

**Backward pass:** start from the output error and propagate it backward, layer by layer:

$$\delta_L = \nabla_{a_L}\mathcal{L}\odot\sigma'(z_L), \qquad \delta_l = \bigl(W_{l+1}^{\top}\,\delta_{l+1}\bigr)\odot\sigma'(z_l)$$

then read off each weight's gradient as an outer product:

$$\frac{\partial\mathcal{L}}{\partial W_l} = \delta_l\,a_{l-1}^{\top}.$$

This is efficient — it computes *all* parameter gradients in one backward sweep, at roughly the cost of one forward pass. But it requires four things that are awkward on biological or analog hardware, and these four are the entire reason the alternatives exist:

| Requirement | Where it appears | Why it's a problem off-GPU |
| ----------- | ---------------- | -------------------------- |
| **Weight transport** | $W_{l+1}^{\top}$ in $\delta_l$ | the backward path must know every forward weight, transposed, and stay synced |
| **Activation derivative** | $\sigma'(z_l)$ | needs a differentiable activation and the cached $z_l$ |
| **Global backward pass** | $\delta_l$ depends on $\delta_{l+1}$ | a locked, sequential reverse sweep; no layer updates until it arrives |
| **Frozen forward state** | $a_{l-1}$ kept for the outer product | every activation held in memory until the backward pass consumes it |

(Feedback alignment drops weight transport; attribution and forward-forward drop the derivative and the backward pass; equilibrium propagation replaces the backward pass with a relaxation. See `summary.detail.md` §0.)

---

## Batch, stochastic, and mini-batch

The gradient is an average over training examples. *How many* examples you average per step defines three variants:

**Batch (full) gradient descent** — use the whole dataset every step:

$$\nabla\mathcal{L} = \frac{1}{N}\sum_{i=1}^{N}\nabla\mathcal{L}_i(\theta)$$

Exact gradient, smooth descent — but one step costs a full pass over $N$ examples. Infeasible for large datasets.

**Stochastic gradient descent (SGD)** — use a single random example per step:

$$\theta \leftarrow \theta - \eta\,\nabla\mathcal{L}_i(\theta), \quad i \sim \text{Uniform}(1,N)$$

A noisy, unbiased estimate of the true gradient. Cheap per step, thousands of steps per epoch, and the **noise is a feature** — it helps escape saddle points and sharp minima and improves generalization.

**Mini-batch SGD** — the universal compromise: average over a small batch $B$ (e.g. 32–256):

$$\theta \leftarrow \theta - \eta\,\frac{1}{|B|}\sum_{i\in B}\nabla\mathcal{L}_i(\theta)$$

Lower-variance than pure SGD, still cheap, and maps perfectly onto GPU parallelism. This is what "SGD" means in practice and is the project's **Phase 2 Cell D baseline**.

---

## The learning rate — the one knob that matters most

$\eta$ controls the step size, and it is the single most important hyperparameter:

- **Too large** → the step overshoots the minimum, the loss oscillates or diverges (climbs to infinity).
- **Too small** → convergence is correct but painfully slow; can stall on plateaus.
- **Just right** → steady descent. But "just right" changes over training — large early (cover ground fast), small late (settle precisely).

Hence **learning-rate schedules**: step decay, exponential decay, cosine annealing, linear warmup (start tiny, ramp up to avoid early instability), cyclical / warm restarts (SGDR), and the 1cycle policy. These are not optional polish on large models — the schedule often matters as much as the optimizer. The adaptive optimizers (AdaGrad/RMSProp/Adam, see `adam.detail.md`) were invented largely to make the learning rate **per-parameter and self-tuning** so you do not have to hand-craft one global $\eta$.

---

## Convergence theory (the short version)

- **Convex + L-smooth:** GD with $\eta \le 1/L$ converges at rate $\mathcal{O}(1/t)$. The loss gap shrinks like $1/t$.
- **$\mu$-strongly convex + L-smooth:** GD converges **linearly** (geometrically), at rate governed by the **condition number** $\kappa = L/\mu$: $\bigl(1-\tfrac{\mu}{L}\bigr)^t$. Ill-conditioned problems (large $\kappa$) converge slowly — this is exactly the "ravine" momentum fixes.
- **SGD:** the gradient noise prevents exact convergence with a fixed $\eta$ (it bounces around the optimum in a noise ball of radius $\propto\eta$). You need a **decaying learning rate** ($\eta_t\to 0$, e.g. $\eta_t\propto 1/t$) for SGD to converge to the optimum. Rates: $\mathcal{O}(1/\sqrt{t})$ convex, $\mathcal{O}(1/t)$ strongly convex.
- **Non-convex (deep nets):** only a guarantee of reaching a **stationary point** ($\|\nabla\mathcal{L}\|\to 0$), not a global minimum. In practice this is enough, because of the landscape geometry below.

---

## The loss landscape

Why does a method with no global guarantee work so well? Because of what high-dimensional loss surfaces actually look like:

- **Local minima are rarely a problem.** In high dimensions, most critical points are **saddle points**, not bad local minima. A point is a local min only if curvature is positive in *every* direction — exponentially unlikely. So GD almost always finds a *good* minimum.
- **Saddle points are the real obstacle.** The gradient is near zero there, so plain GD slows to a crawl on the plateau around a saddle. SGD's noise (and momentum) push through them.
- **Flat vs. sharp minima.** Wide, flat minima generalize better than narrow, sharp ones. SGD's noise biases it toward flatter minima — part of why the *noisy* method generalizes better than exact full-batch GD. (This is the premise behind SAM and SWA in `summary.detail.md` §1.)
- **Plateaus and ravines.** Long flat regions stall first-order methods; steep-sided narrow valleys (ill-conditioning) make raw GD zig-zag. Momentum (`momentum.detail.md`) and adaptive methods (`adam.detail.md`) are the standard cures.

---

## The optimizer family tree (where to go next)

Everything below keeps the gradient-descent skeleton $\theta\leftarrow\theta-\eta\,(\text{step})$ and only changes the *step*:

- **Momentum / Nesterov** → accumulate an EMA of past gradients to accelerate and damp oscillation. → `momentum.detail.md`
- **Adaptive learning rate** (AdaGrad → RMSProp → Adam → AdamW) → give every parameter its own self-tuned step size. → `adam.detail.md`
- **Second-order / curvature** (Newton, BFGS/L-BFGS, natural gradient/K-FAC) → use the Hessian or Fisher to rescale the step by curvature; powerful but expensive. → `second-order-methods.detail.md`
- **Variance reduction** (SVRG, SAGA), **generalization-oriented** (SAM, Lookahead, SWA), **schedules**, **regularization knobs** (weight decay, gradient clipping) → `summary.detail.md` §1.

---

## Why gradient descent is the project's baseline (not its method)

The project's locked decision #2 is *attribution, not gradient descent* — but SGD **stays the comparison baseline at scale** (Phase 2, Cell D). The reasoning:

- Gradient descent gives the **exact descent direction**; attribution gives a contribution-weighted approximation. Measuring attribution against SGD is how the project quantifies what it gives up for hardware-friendliness.
- The four backprop requirements above are precisely what an analog, resident-weight, online substrate cannot pay for — so gradient descent is the thing to *beat on cost*, while staying close to it *on direction*.
- Concretely: the single-Ganglion regression results ("near-perfect on a noisy plane, ~20× loss cut on a paraboloid") are only meaningful **relative to what SGD achieves on the same task.** Gradient descent is the ruler, not the territory.

So: know it cold, respect its accuracy, and remember the project's whole bet is that you can keep most of its learning power while dropping its non-local cost.

---

## Trade-offs (summary)

```
Gradient Descent (with backprop):
  ✅ exact steepest-descent direction (the gold standard for direction accuracy)
  ✅ strong convergence theory on convex / strongly-convex problems
  ✅ backprop computes ALL gradients in one backward sweep (≈ one forward pass cost)
  ✅ scales to enormous models on GPUs; the universal default
  ✅ SGD noise escapes saddles, finds flat minima, generalizes well
  ❌ requires weight transport (Wᵀ) — non-local, hard on analog/biological hardware
  ❌ requires σ'(z), a global backward pass, and a frozen forward state in memory
  ❌ no global-optimum guarantee on non-convex deep nets (only a stationary point)
  ❌ learning rate is a delicate, problem-dependent knob (hence schedules / adaptivity)
  ❌ raw GD struggles with ill-conditioning (ravines) and plateaus (saddles)
```
