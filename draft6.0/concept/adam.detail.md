# Adam & the Adaptive-Learning-Rate Family

## Overview / Core Idea

Adam (Adaptive Moment Estimation) is the **default optimizer of deep learning**. If you do not know what else to use, you use Adam, and it usually just works. It is the convergence of two separate good ideas:

1. **Momentum** — keep an EMA of the gradient (the *first moment* $m$), so you accelerate consistent directions and average out noise. (This is the `momentum.detail.md` idea.)
2. **Per-parameter adaptive learning rates** — keep an EMA of the *squared* gradient (the *second moment* $v$), and divide each parameter's step by the square root of its own $v$. Parameters that have seen large, frequent gradients get **smaller** steps; parameters that have seen small or rare gradients get **larger** steps. Every weight gets its own self-tuned learning rate.

Put together, Adam's update is "momentum in the numerator, adaptive scaling in the denominator":

$$\theta_{t} = \theta_{t-1} - \eta\,\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}$$

The motivation is that a single global learning rate $\eta$ is a bad fit for deep networks: different layers and different parameters have wildly different gradient magnitudes (early layers tiny, late layers large; common features frequent, rare features sparse). One $\eta$ cannot serve them all. The adaptive denominator $\sqrt{\hat{v}_t}$ **normalizes each parameter's step by its own recent gradient scale**, so a single $\eta$ becomes a sensible *relative* step for everyone. That robustness — "it works without careful learning-rate tuning" — is why Adam took over.

This file traces the lineage **AdaGrad → RMSProp → Adam → AdamW** (each fixes the previous one's flaw) and surveys the modern variants. It is worth a full read because Adam is the optimizer you will actually reach for, and because its two halves (momentum + adaptive scale) are the two statistics a learning substrate has to track.

---

## Benchmark

Adam's "benchmark" is empirical dominance plus one well-known caveat:

| Aspect | Result |
| ------ | ------ |
| **Convergence speed** | Typically the **fastest to a low training loss** with little tuning — the practical default across NLP, vision, RL, generative models. |
| **Robustness** | Works across a huge range of architectures with the *same* defaults ($\eta=10^{-3}$, $\beta_1=0.9$, $\beta_2=0.999$, $\varepsilon=10^{-8}$) — its main selling point. |
| **Generalization caveat** | On some vision tasks **SGD+momentum generalizes slightly better** than Adam (Adam can find sharper minima). **AdamW** (decoupled weight decay) substantially closes this gap and is now standard for transformers. |
| **Theory** | The original convergence proof had a flaw; **AMSGrad** fixes a class of non-convergence cases by forcing the denominator to be non-decreasing. |

Reading it: Adam wins on *speed and robustness with minimal tuning*, which is why it is the default. The honest asterisk is that a *well-tuned* SGD+momentum can match or beat Adam's *generalization* on some problems — so "Adam to get going fast, SGD+momentum (or AdamW) when squeezing the last bit of test accuracy" is a common rule of thumb. AdamW is the modern default that mostly removes the asterisk.

---

## The lineage, fix by fix

### AdaGrad — the original adaptive method

AdaGrad gives each parameter a learning rate that shrinks based on the **total accumulated squared gradient**:

$$G_t = G_{t-1} + g_t^2 \quad(\text{elementwise}), \qquad \theta_t = \theta_{t-1} - \frac{\eta}{\sqrt{G_t} + \varepsilon}\,g_t$$

Parameters with large historical gradients get damped; rare-feature parameters keep large steps. This was a breakthrough for **sparse** problems (NLP, where rare words need big updates).

**Fatal flaw:** $G_t$ only ever **grows** (it is a sum of squares). So the effective learning rate $\eta/\sqrt{G_t}$ decays monotonically toward **zero**, and training **grinds to a halt** before reaching a good solution. AdaGrad has no way to forget old, large gradients.

### RMSProp — replace the sum with an EMA

RMSProp fixes AdaGrad's vanishing learning rate by swapping the *sum* of squared gradients for an **exponential moving average** of them:

$$E[g^2]_t = \rho\,E[g^2]_{t-1} + (1-\rho)\,g_t^2, \qquad \theta_t = \theta_{t-1} - \frac{\eta}{\sqrt{E[g^2]_t} + \varepsilon}\,g_t$$

Because it is an EMA (with $\rho\approx 0.9$), old gradients **decay away** and the denominator stays bounded and responsive to the *recent* gradient scale. The learning rate no longer collapses, so RMSProp trains indefinitely. It is the direct ancestor of Adam's second moment.

### Adam — RMSProp + momentum + bias correction

Adam combines RMSProp's adaptive denominator with a momentum numerator, and adds a crucial **bias correction**:

$$m_t = \beta_1\,m_{t-1} + (1-\beta_1)\,g_t \qquad\text{(1st moment — momentum / mean of gradient)}$$
$$v_t = \beta_2\,v_{t-1} + (1-\beta_2)\,g_t^2 \qquad\text{(2nd moment — RMSProp / uncentered variance)}$$
$$\hat{m}_t = \frac{m_t}{1-\beta_1^{t}}, \qquad \hat{v}_t = \frac{v_t}{1-\beta_2^{t}} \qquad\text{(bias correction)}$$
$$\theta_t = \theta_{t-1} - \eta\,\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}$$

Defaults: $\beta_1=0.9$, $\beta_2=0.999$, $\varepsilon=10^{-8}$, $\eta=10^{-3}$.

---

## Why the bias correction is needed

$m$ and $v$ are initialized to **zero**. Early in training (small $t$), an EMA initialized at zero is **biased toward zero** — it has not yet "warmed up." For the second moment with $\beta_2=0.999$, $v_t$ is badly underestimated for hundreds of steps, which makes $\sqrt{\hat v_t}$ too small and the steps explosively large exactly when the model is most fragile.

The correction $\hat{v}_t = v_t/(1-\beta_2^t)$ removes this. At $t=1$, $1-\beta_2^t = 1-\beta_2 = 0.001$, so dividing by it scales $v_1$ up by $1000\times$ to undo the zero-initialization shrinkage. As $t\to\infty$, $\beta_2^t\to 0$ and the correction factor $\to 1$ (it switches itself off once the EMA has warmed up). Same logic for $\hat m_t$. Without bias correction Adam is unstable in its first few hundred steps; with it, the early steps are correctly scaled. (RAdam, below, is an alternative way to handle this same early-training variance problem.)

---

## How to read the update

$$\theta_t = \theta_{t-1} - \eta\,\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\varepsilon}$$

- **Numerator $\hat{m}_t$** is the momentum-smoothed gradient: direction + acceleration + noise-averaging.
- **Denominator $\sqrt{\hat{v}_t}$** is the recent gradient *magnitude* per parameter: it normalizes the step so each parameter moves by a comparable *relative* amount.
- The ratio $\hat m/\sqrt{\hat v}$ is roughly a **signal-to-noise ratio**: when a parameter's gradient is consistent (mean large relative to its spread), the ratio is near $\pm 1$ and it takes a confident step; when the gradient is noisy (mean small relative to spread), the ratio shrinks and it takes a cautious step. Adam steps confidently where the signal is clear and timidly where it is noisy — automatically, per parameter.

---

## AdamW — decoupled weight decay (the modern default)

Standard L2 regularization adds $\lambda\theta$ to the gradient. In Adam this $\lambda\theta$ term then goes **through the adaptive denominator** $\sqrt{\hat v}$, so parameters with large gradients get *less* weight decay — the regularization strength becomes entangled with the gradient history, which is not what you want. **AdamW** (Loshchilov & Hutter) **decouples** weight decay from the gradient step, applying it directly to the weights:

$$\theta_t = \theta_{t-1} - \eta\Bigl(\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\varepsilon} + \lambda\,\theta_{t-1}\Bigr)$$

The decay $\lambda\theta$ is applied uniformly, *outside* the adaptive scaling. This single change noticeably improves generalization and is why **AdamW is the standard optimizer for transformers / LLMs.** When people say "we trained with Adam" on a modern large model, they almost always mean AdamW.

---

## The modern variant zoo (brief)

All keep the $m$/$v$ skeleton and tweak one thing:

- **Nadam** — Adam with **Nesterov** look-ahead applied to the momentum term. Slightly better-damped.
- **AMSGrad** — forces the denominator to be **non-decreasing** by using the running max, $\hat v_t = \max(\hat v_{t-1}, v_t)$. Fixes Adam's theoretical non-convergence on certain convex problems.
- **AdaMax** — replaces the L2 second moment with an **L∞** (max) norm: $u_t = \max(\beta_2 u_{t-1}, |g_t|)$, $\theta_t = \theta_{t-1} - \eta\,\hat m_t/u_t$. More stable when gradients have rare huge spikes.
- **RAdam** (Rectified Adam) — adds a **warmup-like rectification term** that down-weights the adaptive learning rate while its variance is still high (early training), removing the need for a manual warmup schedule.
- **LARS / LAMB** — **layer-wise** adaptive rates for **very large batch** training: scale each layer's update by a trust ratio $\|\theta_l\|/\|\text{update}_l\|$. LARS wraps SGD, LAMB wraps Adam. These are what make 32k-batch ImageNet / BERT training stable.
- **Lion** (EvoLved Sign Momentum) — drops the second moment entirely and uses the **sign** of an interpolated momentum: $\theta_t = \theta_{t-1} - \eta\,\text{sign}(\beta_1 m_{t-1} + (1-\beta_1)g_t)$, then updates $m$ with $\beta_2$. Half the optimizer memory (no $v$), competitive on large models.
- **Adafactor** — **factorizes** the second-moment matrix into row and column statistics instead of storing it per-parameter, cutting optimizer memory from $O(n)$ to $O(\sqrt n)$-ish. Built for training huge models (T5).
- **Sophia** — a light **second-order** method using a clipped diagonal Hessian estimate as the denominator; aims to beat AdamW on LLM pretraining wall-clock.

---

## Training loop (Adam, concrete)

```
init  m = 0,  v = 0,  t = 0
defaults  η=1e-3,  β1=0.9,  β2=0.999,  ε=1e-8

repeat:
    t += 1
    g = ∇L(θ)
    m = β1·m + (1−β1)·g            # 1st moment (momentum)
    v = β2·v + (1−β2)·g²           # 2nd moment (RMSProp)
    m̂ = m / (1 − β1^t)            # bias correction
    v̂ = v / (1 − β2^t)
    θ = θ − η · m̂ / (√v̂ + ε)
    # AdamW: θ = θ − η·( m̂/(√v̂+ε) + λ·θ )
```

State cost: **two buffers** ($m$ and $v$) the size of the parameters — i.e. Adam uses ~3× the memory of plain SGD (params + two moments). This is the memory Adafactor/Lion attack.

---

## Relevance to the project

The project does **not** use Adam — its learning rule is attribution, and its baseline is SGD/SGD+momentum (`gradient-descent.detail.md`). But Adam is worth understanding deeply for two reasons:

- **Its two statistics are the two a substrate must track.** Adam = an EMA of the signal ($m$, the project's Scap momentum register) + an EMA of the squared signal ($v$, a *variance* register — structurally the same object as BCM's threshold $\theta=\langle a_j^2\rangle$, see `summary.detail.md`). Adam is the proof that "mean + second-moment of the update signal" is a powerful pair of local statistics — and both are cheap moving averages a per-weight analog register can hold.
- **It is the fallback the methodology explicitly defers.** The project's rules say *"Adam-style $v_t$ is a remediation tested only after baseline failure"* — i.e. if plain attribution + momentum underperforms, an Adam-like per-weight variance normalizer is the first thing to try. Knowing exactly what that $v_t$ does (and that it is just a second moving average) is knowing the project's first remediation lever.

---

## Trade-offs (summary)

```
Adam / adaptive-learning-rate family:
  ✅ fast, robust convergence with almost no learning-rate tuning — the default
  ✅ per-parameter adaptive step = one η works across layers of very different scale
  ✅ combines momentum (m) + adaptive scaling (v); bias correction stabilizes early steps
  ✅ AdamW (decoupled weight decay) ≈ standard for transformers/LLMs
  ✅ rich variant family for scale (LAMB), memory (Adafactor, Lion), stability (RAdam, AMSGrad)
  ❌ ~3× SGD memory — stores two moment buffers per parameter
  ❌ can generalize slightly worse than well-tuned SGD+momentum (sharper minima) — AdamW mitigates
  ❌ vanilla Adam has known non-convergence cases (AMSGrad fixes)
  ❌ more moving parts than SGD; ε, β1, β2 add (usually safe) knobs
```
