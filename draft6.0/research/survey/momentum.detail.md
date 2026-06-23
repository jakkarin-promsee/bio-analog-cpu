# Momentum & Nesterov Accelerated Gradient

## Overview / Core Idea

Momentum is the smallest possible change to gradient descent that fixes its two worst behaviors — **crawling through plateaus** and **zig-zagging down ravines** — and it does it by adding one idea: **don't step on the current gradient alone; step on a running average of the recent gradients.**

Plain gradient descent has no memory. Each step looks only at the gradient *right now* and immediately forgets it. In a long narrow valley (an ill-conditioned loss surface) that is a disaster: the gradient points mostly *across* the valley, so the iterate bounces from wall to wall, making slow progress *along* the valley floor toward the minimum. Momentum gives the iterate **inertia**, like a heavy ball rolling downhill: the back-and-forth components cancel out across steps, while the consistent down-the-valley component **accumulates and accelerates**.

The mechanism is an **exponential moving average (EMA) of the gradient**, called the velocity $v$:

$$v_{t} = \mu\,v_{t-1} + \nabla\mathcal{L}(\theta_{t-1}), \qquad \theta_{t} = \theta_{t-1} - \eta\,v_{t}$$

with momentum coefficient $\mu \approx 0.9$. The velocity remembers where it has been going; a gradient that keeps pointing the same way builds up speed, while a gradient that keeps flipping sign averages toward zero.

**Nesterov Accelerated Gradient (NAG)** is a smarter version: instead of measuring the gradient at the current point and then jumping, it **looks ahead** to where the momentum is about to carry it, measures the gradient *there*, and corrects. This "look before you leap" gives NAG a better-damped, provably faster trajectory.

This file is directly relevant to the project: **the Scap's EMA momentum register is exactly this idea** — a per-weight running average of the update signal, smoothing the noisy per-step contribution into a stable trend. Understanding Polyak/Nesterov momentum is understanding what that register is doing and why.

---

## Benchmark

Momentum's "benchmark" is a **convergence-rate improvement**, provable on convex problems and dramatic in practice on deep nets:

| Setting | Plain GD | Momentum / Nesterov |
| ------- | -------- | ------------------- |
| **Smooth convex** | $\mathcal{O}(1/t)$ | **$\mathcal{O}(1/t^2)$** (Nesterov's optimal first-order rate) |
| **Strongly convex, condition number $\kappa$** | rate $\sim\bigl(1-\tfrac{1}{\kappa}\bigr)$ | rate $\sim\bigl(1-\tfrac{1}{\sqrt{\kappa}}\bigr)$ — **$\kappa\to\sqrt{\kappa}$** |
| **Deep nets (empirical)** | slow on ravines, stalls on plateaus | faster, smoother; standard ingredient of SGD-with-momentum, the workhorse optimizer |

Reading it:

- The headline is **$\kappa \to \sqrt{\kappa}$**: on an ill-conditioned problem (condition number $\kappa$, the ratio of largest to smallest curvature), plain GD's convergence is throttled by $\kappa$, but momentum is throttled only by $\sqrt{\kappa}$. For $\kappa = 10{,}000$ that is the difference between $10{,}000$ and $100$ — a 100× speed-up.
- Nesterov achieves $\mathcal{O}(1/t^2)$ on smooth convex problems, which is the **provably optimal** rate for any first-order method — you cannot do better using only gradients.
- In deep learning, **SGD + momentum** (μ ≈ 0.9) is the classic strong baseline; many state-of-the-art image models are trained with it rather than Adam precisely because it generalizes slightly better.

---

## Why plain gradient descent struggles (the ravine)

Consider a loss shaped like a long, narrow valley — steep walls, gentle floor. This is **ill-conditioning**: the curvature is large in one direction (across) and small in another (along). The gradient is dominated by the steep direction, so:

- plain GD takes a big step *across* the valley, overshoots, the gradient flips, it steps back across, overshoots again — **zig-zag**;
- meanwhile the gentle *along-the-valley* component, which is the direction that actually reduces the loss toward the minimum, gets almost no progress.

You are forced to use a small $\eta$ to avoid diverging across the steep walls, but that small $\eta$ makes the along-valley crawl even slower. Plain GD is stuck between "diverge" and "crawl." Momentum breaks the deadlock.

---

## Classical (Polyak / heavy-ball) momentum

Maintain a velocity vector $v$ that is an EMA of the gradients, and step along the velocity:

$$v_{t} = \mu\,v_{t-1} + \nabla\mathcal{L}(\theta_{t-1})$$
$$\theta_{t} = \theta_{t-1} - \eta\,v_{t}$$

(An equivalent common form folds $\eta$ into the velocity: $v_t = \mu v_{t-1} - \eta\nabla\mathcal{L}$, $\theta_t = \theta_{t-1} + v_t$.)

What the EMA does to the two components of the gradient:

- **Across the ravine** the gradient alternates sign every step. The EMA of an alternating signal averages toward **zero** — the zig-zag is damped out.
- **Along the ravine** the gradient points the same way every step. The EMA of a consistent signal **grows** — toward a steady-state speed.

### The effective step size

If the gradient is roughly constant $g$ along the valley, the velocity converges to a geometric sum:

$$v_\infty = g\,(1 + \mu + \mu^2 + \cdots) = \frac{g}{1-\mu}$$

So the **effective learning rate along a consistent direction is amplified by $\tfrac{1}{1-\mu}$.** For $\mu = 0.9$ that is a **10× boost** in the direction that matters, *without* increasing $\eta$ in the direction that would cause divergence. That is the whole trick: selectively accelerate the consistent direction, damp the inconsistent one. The momentum coefficient $\mu$ is, in effect, a **memory length** — $\mu=0.9$ remembers ~10 steps, $\mu=0.99$ remembers ~100.

---

## Nesterov Accelerated Gradient (NAG)

Classical momentum measures the gradient at the current position $\theta_{t-1}$ and *then* takes the momentum jump. Nesterov reverses the order: it first applies the momentum jump to get a **look-ahead point**, measures the gradient *there*, and uses that:

$$v_{t} = \mu\,v_{t-1} + \nabla\mathcal{L}\bigl(\theta_{t-1} - \eta\,\mu\,v_{t-1}\bigr)$$
$$\theta_{t} = \theta_{t-1} - \eta\,v_{t}$$

The term $\theta_{t-1} - \eta\mu v_{t-1}$ is "where momentum is about to take me." Evaluating the gradient there means NAG can **see the upcoming change in slope and correct before overshooting.**

### Why the look-ahead helps

Think of the heavy ball again. Classical momentum is a blind ball — it commits to its velocity, then feels the ground after it has already moved. If it is about to overshoot the minimum, it finds out too late and oscillates. Nesterov's ball **peeks at the slope where it is heading**: if the ground ahead is already turning uphill, it starts braking *this* step instead of next. The result is a better-damped, less oscillatory trajectory and the optimal $\mathcal{O}(1/t^2)$ convergence rate. The cost is essentially nothing — one gradient evaluation, just at a shifted point.

---

## Momentum in stochastic training (SGD + momentum)

With mini-batch gradients the per-step gradient is *noisy*. Momentum's EMA does double duty here: besides accelerating consistent directions, it **averages out the mini-batch noise**, producing a smoother, lower-variance update direction. This is why "SGD with momentum" — not plain SGD — is the standard strong baseline:

$$v_{t} = \mu\,v_{t-1} + g_t^{\text{batch}}, \qquad \theta_t = \theta_{t-1} - \eta\,v_t$$

A subtlety: in the stochastic setting too much momentum ($\mu$ too close to 1) can cause overshoot and instability, because the velocity carries stale gradient information from a region the iterate has already left. $\mu = 0.9$ is the near-universal default; $0.99$ is used with smaller $\eta$ and good schedules.

---

## Connection to the project (the Scap's EMA momentum)

The project's Scap holds an **EMA momentum register** for its weight update — and that is structurally the same object as $v$ here:

$$v_{t} = \mu\,v_{t-1} + (\text{this step's signal})$$

The roles line up:

- **In SGD**, the "signal" is the mini-batch gradient, and $v$ smooths gradient noise + accelerates consistent directions.
- **In the Scap**, the "signal" is the per-step attribution/update contribution, and the EMA smooths the noisy per-step contribution into a stable trend before it moves the capacitor charge.
- **$\mu$ is a memory length in both** — how many past steps the register effectively remembers, set by how fast the analog register leaks/decays.

So the same intuitions transfer directly: a high $\mu$ gives a long, stable memory (good for noisy signals, risk of carrying stale information); a low $\mu$ is responsive but jittery. The project's BCM threshold register and this momentum register are both "moving average of history" hardware — the same primitive used for two different statistics. (See `summary.detail.md` §1.3 / §2 on BCM's $\theta = \langle a_j^2\rangle$.)

This is also why momentum is worth a full read while most other optimizer tricks are summary entries: it is the one mainstream optimizer idea the project **physically instantiates**.

---

## Training loop (concrete)

```
init  v = 0,  pick μ (≈0.9),  η

repeat:
    g = ∇L(θ)                       # classical: gradient at current θ
    # ── classical (Polyak) ──
    v = μ·v + g
    θ = θ − η·v

    # ── Nesterov variant ──
    g = ∇L(θ − η·μ·v)               # gradient at the look-ahead point
    v = μ·v + g
    θ = θ − η·v
```

The only state added over plain GD is the velocity vector $v$ — one extra buffer the size of the parameters. Cheap, and almost always worth it.

---

## Limitations and notes

- **One more hyperparameter.** $\mu$ must be chosen; too high overshoots, too low gives little benefit. But $0.9$ works so broadly it is effectively a constant.
- **Overshoot near sharp minima.** The accumulated velocity can carry the iterate *past* a narrow minimum; it then has to come back. (Often benign, sometimes a reason to lower $\mu$ or $\eta$ late in training.)
- **Still first-order.** Momentum approximates some benefit of curvature (it implicitly favors low-curvature directions) but it is *not* a second-order method — it does not use the Hessian. For true curvature rescaling see `second-order-methods.detail.md`.
- **Adaptive methods combine it.** Adam (`adam.detail.md`) *is* momentum (first moment $m$) plus per-parameter adaptive scaling (second moment $v$). Momentum is one of Adam's two halves.

---

## Trade-offs (summary)

```
Momentum / Nesterov Accelerated Gradient:
  ✅ accelerates consistent directions by 1/(1−μ) (≈10× at μ=0.9) without raising η
  ✅ damps zig-zag in ill-conditioned ravines; pushes through plateaus/saddles
  ✅ improves convergence: κ→√κ (strongly convex); Nesterov hits optimal O(1/t²)
  ✅ averages mini-batch noise — why "SGD+momentum" is the standard strong baseline
  ✅ Nesterov's look-ahead damps overshoot for ~free (one shifted gradient eval)
  ✅ directly mirrors the project's Scap EMA-momentum register
  ❌ adds a hyperparameter μ and one velocity buffer
  ❌ can overshoot narrow minima (carries stale velocity)
  ❌ still first-order — no real curvature information
```
