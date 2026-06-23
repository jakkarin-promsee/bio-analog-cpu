# Survey of Learning Algorithms — Summary

A single-file survey of how neural networks are trained — both the **mainstream gradient-based optimizers** and the **local / biologically-plausible / forward-only alternatives** discussed in this project. This is a **map, not a manual**: each entry gives the core idea, the key formula(s), what the method converges to or is good for, and its main trade-off — enough to understand and compare, not the full single-topic treatment. The deepest methods have their own standalone files (marked **→ `file.detail.md`**); read those for the complete derivation.

> **Draft-6.0 note (June 2026).** This is the survey of *options*, not the current decision. Draft 5.1 picked **attribution** (`distribution-based.detail.md`) as the on-chip rule; that was **invalidated** (loss carried magnitude but never direction), and **draft 6.0 chose a SCFF + gradient-descent hybrid** ([`../papers/`](../papers/README.md), [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md)). Where the text below calls attribution *"the project's locked rule,"* read it as **"the draft-5.1 pick, now historical."** Naming: deep-dives use `{model}.detail.md`; `topdown-bottomup.md` is the neuroscience exception.

---

## 0. The backdrop — what gradient descent needs, and what the alternatives drop

Backpropagation-driven gradient descent is the mainstream (Part 1 below). Every method in Parts 2–5 is defined by *which part of it they refuse to pay for.* Backprop needs four things that are awkward on biological or analog hardware:

- **Weight transport** — the backward pass uses $W^{\top}$, so the backward path must know every forward weight, transposed.
- **The activation derivative** — it needs $\sigma'(z)$ at every neuron, hence a differentiable activation and cached pre-activations.
- **A global backward pass** — a full reverse sweep, *locked* to the forward pass (no layer updates until the sweep reaches it).
- **A frozen forward state** — every activation held in memory until the backward pass consumes it.

The properties the alternatives chase, in various combinations:

| Property | Meaning |
| -------- | ------- |
| **Local** | a weight updates from quantities available at its own synapse/layer |
| **No weight transport** | backward signal does not require $W^{\top}$ |
| **Derivative-free** | no explicit $\sigma'(z)$ |
| **Forward-only** | no separate backward pass at all |
| **Online** | update per-sample, no stored activation history |
| **Unsupervised-capable** | can learn representations without labels |

**Part 1 (gradient-based optimizers) *accepts* all four costs** and only refines how the gradient becomes a step. **Parts 2–5 drop one or more of them.** The grand comparison table is in §6.

---

# PART 1 — Gradient-based optimization (the mainstream)

All of these compute the backprop gradient $g=\nabla\mathcal{L}$ and differ only in **how they turn $g$ into a step**. They share the skeleton $\theta\leftarrow\theta-\eta\cdot(\text{step})$. Foundations in **→ `gradient-descent.detail.md`**.

## 1. Optimizers

### 1.1 (Batch) Gradient Descent → `gradient-descent.detail.md`
$$\theta \leftarrow \theta - \eta\,\nabla\mathcal{L}(\theta), \qquad \nabla\mathcal{L} = \tfrac{1}{N}\textstyle\sum_i \nabla\mathcal{L}_i$$
Exact gradient over the full dataset; smooth descent but one step costs a full pass. The reference everything else is quoted against. Convergence: $\mathcal{O}(1/t)$ convex, linear if strongly convex.

### 1.2 Stochastic & mini-batch SGD → `gradient-descent.detail.md`
$$\theta \leftarrow \theta - \eta\,\tfrac{1}{|B|}\textstyle\sum_{i\in B}\nabla\mathcal{L}_i$$
Noisy unbiased gradient from a small batch. Cheap per step, thousands of steps per epoch, and the **noise helps escape saddles and find flat (generalizing) minima**. This is the project's actual baseline (Phase 2, Cell D).

### 1.3 Momentum (Polyak / heavy-ball) → `momentum.detail.md`
$$v \leftarrow \mu v + g, \qquad \theta \leftarrow \theta - \eta v$$
An EMA of gradients gives the iterate inertia: consistent directions accelerate ($\times\tfrac{1}{1-\mu}\!\approx\!10$ at $\mu{=}0.9$), zig-zag in ravines cancels. Mirrors the project's **Scap EMA-momentum register**.

### 1.4 Nesterov Accelerated Gradient → `momentum.detail.md`
$$v \leftarrow \mu v + \nabla\mathcal{L}(\theta - \eta\mu v), \qquad \theta \leftarrow \theta - \eta v$$
Momentum with a **look-ahead** gradient (measured where momentum is about to land). Better-damped; hits the optimal first-order rate $\mathcal{O}(1/t^2)$ on smooth convex problems.

### 1.5 AdaGrad
$$G \leftarrow G + g^2, \qquad \theta \leftarrow \theta - \tfrac{\eta}{\sqrt{G}+\varepsilon}\,g$$
Per-parameter learning rate that shrinks with accumulated squared gradient — great for **sparse** features. Flaw: $G$ only grows, so the LR decays to **zero** and training stalls.

### 1.6 RMSProp
$$E[g^2] \leftarrow \rho E[g^2] + (1-\rho)g^2, \qquad \theta \leftarrow \theta - \tfrac{\eta}{\sqrt{E[g^2]}+\varepsilon}\,g$$
AdaGrad with an **EMA** instead of a sum, so old gradients decay and the LR stays alive. Direct ancestor of Adam's second moment.

### 1.7 AdaDelta
RMSProp variant that also removes the need for a global $\eta$ by tracking an EMA of squared *updates* and using its ratio to the EMA of squared gradients as the step scale.

### 1.8 Adam → `adam.detail.md`
$$m \leftarrow \beta_1 m + (1{-}\beta_1)g,\quad v \leftarrow \beta_2 v + (1{-}\beta_2)g^2,\quad \theta \leftarrow \theta - \eta\,\tfrac{\hat m}{\sqrt{\hat v}+\varepsilon}$$
Momentum ($m$) + RMSProp ($v$) + **bias correction** ($\hat m = m/(1{-}\beta_1^t)$). Robust, fast, almost no LR tuning — the **default optimizer of deep learning**.

### 1.9 AdamW → `adam.detail.md`
$$\theta \leftarrow \theta - \eta\bigl(\tfrac{\hat m}{\sqrt{\hat v}+\varepsilon} + \lambda\theta\bigr)$$
Adam with **decoupled weight decay** (applied directly, not through the adaptive denominator). Closes Adam's generalization gap; **standard for transformers / LLMs**.

### 1.10 Adam variants (Nadam, AMSGrad, AdaMax, RAdam)
**Nadam** = Adam + Nesterov look-ahead. **AMSGrad** = non-decreasing denominator $\hat v_t=\max(\hat v_{t-1},v_t)$ (fixes non-convergence). **AdaMax** = L∞ second moment. **RAdam** = rectified early-training variance (auto-warmup).

### 1.11 Large-batch: LARS / LAMB
Layer-wise adaptive rates scaled by a **trust ratio** $\|\theta_l\|/\|\text{update}_l\|$. LARS wraps SGD, LAMB wraps Adam; they make huge-batch (32k) ImageNet / BERT training stable.

### 1.12 Modern: Lion, Adafactor, Sophia
**Lion** = sign-of-momentum update, half the optimizer memory (no $v$). **Adafactor** = factorized second moment, $O(\sqrt n)$ memory for huge models. **Sophia** = clipped diagonal-Hessian denominator (light second-order) for LLM pretraining.

### 1.13 Newton's method → `second-order-methods.detail.md`
$$\theta \leftarrow \theta - H^{-1}\nabla\mathcal{L}, \qquad H = \nabla^2\mathcal{L}$$
Rescales the gradient by curvature → **quadratic convergence**, no LR. Infeasible at scale ($O(n^2)$ store, $O(n^3)$ invert) and unsafe on indefinite Hessians.

### 1.14 Gauss-Newton / Levenberg-Marquardt → `second-order-methods.detail.md`
For least-squares, $H\approx J^{\top}J$ (PSD). LM damps it: $\Delta = -(J^{\top}J+\lambda I)^{-1}J^{\top}r$, interpolating Gauss-Newton ↔ gradient descent. Workhorse for **small nonlinear least-squares**.

### 1.15 Quasi-Newton: BFGS / L-BFGS → `second-order-methods.detail.md`
Build $H^{-1}$ from gradient differences (secant condition); never form $H$. **L-BFGS** stores only the last $m$ step/gradient pairs ($O(mn)$). The one second-order method with real use — but on **full-batch / deterministic** problems, not noisy mini-batch DL.

### 1.16 Conjugate gradient → `second-order-methods.detail.md`
Minimizes a quadratic in $\le n$ steps using only Hessian-*vector* products (no matrix stored). Inner engine of Hessian-free optimization.

### 1.17 Natural gradient / K-FAC / Shampoo → `second-order-methods.detail.md`
$$\theta \leftarrow \theta - \eta\,F^{-1}\nabla\mathcal{L}, \qquad F = \text{Fisher information}$$
Steepest descent in **distribution space**; reparametrization-invariant. **K-FAC** makes it tractable via Kronecker-factored per-layer Fisher blocks. The formal "use the right geometry" — the expensive cousin of attribution's normalizer.

### 1.18 Variance reduction: SVRG / SAG / SAGA
Reduce SGD's gradient variance with a stored reference: e.g. **SVRG** uses $g = \nabla\mathcal{L}_i(\theta) - \nabla\mathcal{L}_i(\tilde\theta) + \nabla\mathcal{L}(\tilde\theta)$ with a periodic full-gradient snapshot $\tilde\theta$. Linear convergence for strongly convex finite sums. (SAG/SAGA store per-sample gradients.)

### 1.19 Generalization-oriented: SAM, Lookahead, SWA
**SAM** (Sharpness-Aware Minimization) minimizes the worst-case loss in a neighborhood — perturb to $\theta+\rho\tfrac{g}{\|g\|}$, take the gradient there → seeks **flat minima**. **Lookahead** wraps any optimizer with slow/fast weights ($\theta_{\text{slow}}{+}\alpha(\theta_{\text{fast}}{-}\theta_{\text{slow}})$). **SWA** averages weights along the SGD tail for a flatter solution.

### 1.20 Learning-rate schedules
Step decay, exponential, **cosine annealing**, linear **warmup**, cyclical / warm restarts (SGDR), 1cycle. Often as important as the optimizer; adaptive methods (§1.5–1.12) partly automate the per-parameter rate but not the global schedule.

### 1.21 Regularization knobs: weight decay, gradient clipping
**Weight decay / L2**: $\theta\leftarrow\theta(1-\eta\lambda)-\eta g$ (decoupled in AdamW). **Gradient clipping**: cap $\|g\|$ by norm or value to stop exploding gradients (essential for RNNs/transformers).

**Optimizer cheat-sheet:**

| Optimizer | Momentum? | Per-param adaptive? | Curvature? | Extra memory |
| --------- | :---: | :---: | :---: | --- |
| SGD | ❌ | ❌ | ❌ | none |
| SGD+Momentum | ✅ | ❌ | ❌ | 1× (velocity) |
| AdaGrad / RMSProp | ❌ | ✅ | diag (crude) | 1× |
| **Adam / AdamW** | ✅ | ✅ | diag (crude) | 2× (m, v) |
| L-BFGS | — | — | ✅ (quasi-Newton) | $m$ pairs |
| Natural grad / K-FAC | — | — | ✅ (Fisher) | factored blocks |

---

# PART 2 — Local / biologically-plausible / forward-only alternatives

These drop one or more of backprop's four costs (§0).

## 2. Hebbian & correlational rules

The base principle: *"neurons that fire together, wire together."* No error signal, no loss — everything local. The variants fix raw Hebbian's fatal flaw (it only ever grows) with a brake or a sign.

### 2.1 Raw Hebbian
$$\Delta W_{ij} = \eta\,a_i a_j$$
If both endpoints are active, the weight grows. With non-negative activations $\Delta W>0$ always → **diverges**; no equilibrium, no error signal. Every rule below fixes this.

### 2.2 Covariance rule (Sejnowski)
$$\Delta W_{ij} = \eta\,(a_i-\langle a_i\rangle)(a_j-\langle a_j\rangle)$$
Center each activation before multiplying, so the product can be **negative** (LTD). Restores a sign to Hebbian learning; bridges "fire together" to "*correlate* together."

### 2.3 Oja's rule
$$\Delta W_{ij} = \eta\,a_j\,(a_i - a_j W_{ij})$$
Adds a decay $-a_j^2 W_{ij}$ → self-normalizes to $\|W\|=1$; **converges to the top principal component** (online PCA). Equilibrium at $a_i = a_j W_{ij}$.

### 2.4 Generalized Hebbian Algorithm (Sanger)
$$\Delta W_{ij} = \eta\,a_j\bigl(a_i - \textstyle\sum_{k\le j}W_{ik}a_k\bigr)$$
Oja + Gram–Schmidt deflation → extracts the **first $m$ principal components in order**. Full online PCA. (Oja is $m=1$.)

### 2.5 BCM (Bienenstock–Cooper–Munro)
$$\Delta W_{ij} = \eta\,a_i a_j (a_j-\theta), \qquad \theta=\langle a_j^2\rangle$$
A **sliding threshold** $\theta$ (moving average of $a_j^2$): above it strengthen, below it weaken. Homeostatic — over-active neurons raise their own bar. Converges to **selectivity** (V1-style tuning). $\theta$ fits a hardware momentum register.

### 2.6 Anti-Hebbian & decorrelation
$$\Delta W_{ij} = -\eta\,a_i a_j$$
Co-active → *weaken*. On lateral connections it **decorrelates** outputs; Földiák pairs Hebbian feedforward + anti-Hebbian lateral for sparse codes.

### 2.7 Competitive Hebbian / WTA / SOM
$$\text{winner}=\arg\max_k(W_k\!\cdot\!x),\quad \Delta W_\text{winner}=\eta(x-W_\text{winner})$$
Only the winner updates, pulled toward $x$. Converges to **cluster centroids** (online $k$-means); with a neighborhood function, a **Self-Organizing Map**. (Grossberg's instar/outstar are the same "move weight toward pattern" idea.)

### 2.8 Hopfield associative-memory storage
$$W_{ij}=\tfrac1N\textstyle\sum_\mu \xi_i^\mu\xi_j^\mu\ (W{=}W^{\top},W_{ii}{=}0), \quad E=-\tfrac12\textstyle\sum W_{ij}s_i s_j$$
One-shot Hebbian outer-product storage of patterns as energy attractors; recall = relax downhill in $E$. Capacity $\approx 0.138N$. Ancestor of CHL (§4.5) and EqProp (§4.6).

### 2.9 STDP (Spike-Timing-Dependent Plasticity)
$$\Delta w = \begin{cases}+A_+e^{-\Delta t/\tau_+}&\Delta t>0\ (\text{pre→post})\\ -A_-e^{+\Delta t/\tau_-}&\Delta t<0\ (\text{post→pre})\end{cases}$$
Spiking Hebb made temporally precise: causal order decides potentiation vs depression. Canonical SNN rule.

### 2.10 Supervised Hebbian / Delta rule
$$\Delta W_{ij} = \eta\,x_i\,(y_{\text{true},j}-y_{\text{pred},j})$$
Replace the post activation with an **error**. Not truly Hebbian (needs a supervisor); = Hebbian(input,target) − anti-Hebbian(input,prediction). Trains **only one layer** — backprop with a single layer.

### 2.11 Neuromodulated Hebbian + eligibility traces
$$\Delta W_{ij}=\eta\,a_i a_j\,r;\qquad e_{ij}=\lambda e_{ij}+a_i a_j,\ \ \Delta W_{ij}=\eta\,r\,e_{ij}$$
Gate Hebbian by a global reward $r$ (three-factor; biological **REINFORCE**, §5.4). **Eligibility traces** solve temporal credit (synapses remember recent activity until $r$ arrives). Remaining gap: $r$ is one scalar — no spatial credit; attribution (`distribution-based.detail.md`) adds it.

## 3. Forward-only methods

Remove the backward pass entirely; each layer learns from a scalar or a second forward pass.

### 3.1 Forward-Forward (Hinton, 2022)
$$G^l=\|h^l\|^2,\quad \mathcal{L}^l=\log(1{+}e^{-(G^l_\text{pos}-\theta)})+\log(1{+}e^{+(G^l_\text{neg}-\theta)})$$
Each layer made loud on real data, quiet on fake — derivative through **one layer only**, no cross-layer gradient. Weakness: **negative data** (Hinton's wrong-label-in-border trick is supervised, MNIST-only). Pros: no weight transport, layers independent.

### 3.2 Self-Contrastive FF (SCFF) → `SCFF.detail.md`
$$x_\text{pos}=2x_k,\qquad x_\text{neg}=x_k+x_n\ (n{\neq}k)$$
Builds label-free positives/negatives by **summation** (input size fixed, $W_1{=}W_2$). The accidental $\times2$ makes $G_\text{pos}\!\approx\!4G$ for free. Two-threshold dead zone; all-layer concatenated features. **MNIST 98.7%** (≈ BP), gap grows with complexity.

### 3.3 Collaborative FF (CFF)
$$G^l_\text{collab}=\textstyle\sum_k w_{lk}G^k$$
Each layer optimizes a weighted sum of *all* layers' goodness (fixed or learned $w_{lk}$), restoring some cross-layer coordination — but the signal is a coarse **scalar** goodness.

### 3.4 Mono-Forward
A single forward pass, no negative pass — contrast generated internally. Most hardware-friendly where a second pass is expensive (e.g. a capacitor must recharge).

### 3.5 PEPITA
$$x_\text{mod}=x+F\,e$$
Two forward passes (clean, then input perturbed by the projected output error $e$ via fixed random $F$); update from their difference. Forward-only cousin of feedback alignment (§4.1).

### 3.6 Signal Propagation (SigProp) & relatives
**SigProp** routes the learning signal/target through the **same forward connections** as the input — no backward path or feedback weights. Relatives: **PFF** (FF + generative top-down), **CaFo** (each block predicts the label directly, no negatives).

## 4. Feedback-path & biologically-plausible backprop approximations

Keep a backward signal but make it cheaper, more local, or transport-free.

### 4.1 Feedback Alignment (FA) → `feedback-alignment.detail.md`
$$\delta_l=(B_l\,\delta_{l+1})\odot\sigma'(z_l)$$
Replace $W^{\top}$ with a **fixed random** $B$; forward weights *align* to it so the random signal becomes a descent direction. Kills weight transport. ≈ BP on MNIST; gap grows on CIFAR/ImageNet.

### 4.2 Direct Feedback Alignment (DFA) → `feedback-alignment.detail.md`
$$\delta_l=(B_l\,e)\odot\sigma'(z_l)$$
Broadcast the **output error** $e$ directly to every layer via fixed random $B_l$ — no sequential backward chain, all layers update in parallel. Very hardware-friendly; weak on conv/deep nets.

### 4.3 Target Propagation
$$\text{target}_L=y,\qquad \text{target}_{l-1}=a_{l-1}-\alpha\,\delta_{l-1}$$
Send a **target activation** down (not a gradient); each layer moves toward its target without $W^{\top}$. Limit: a chain of imperfect inverses.

### 4.4 Difference Target Propagation (DTP)
$$\hat h_{l-1}=h_{l-1}+g_l(\hat h_l)-g_l(h_l)$$
Target prop + learned inverses $g_l\!\approx\!f_l^{-1}$ and a **difference correction** that cancels inverse error to first order. The version that trains deep nets.

### 4.5 Contrastive Hebbian Learning (CHL)
$$\Delta W_{ij}=\eta\,(a_i^+a_j^+-a_i^-a_j^-)$$
Two phases (free $-$ / output-clamped $+$); the **difference of two Hebbian products**. For symmetric weights this equals the backprop gradient. Direct ancestor of EqProp.

### 4.6 Equilibrium Propagation (EqProp) → `equilibrium-propagation.detail.md`
$$\Delta\theta\propto-\tfrac1\beta\bigl(\tfrac{\partial E}{\partial\theta}(s^\beta)-\tfrac{\partial E}{\partial\theta}(s^0)\bigr)$$
One energy-based network, two relaxations (free, then nudged by $\beta$ toward the target); local contrastive update. As $\beta\!\to\!0$ it computes the **exact backprop gradient** from local physics — the leading **analog** learning candidate. ≈ BP on MNIST; small gap on CIFAR ConvNets.

### 4.7 Predictive Coding (as learning) → `predictive-coding.detail.md`
$$\varepsilon_l=\mu_l-f(W_l\mu_{l+1}),\qquad \Delta W_l\propto\varepsilon_l\,f(\mu_{l+1})^{\top}$$
Value + error units; **inference** relaxes activities to minimize prediction-error energy $F=\sum_l\|\varepsilon_l\|^2$, then a **local** Hebbian weight update. Provably approximates BP (exactly, with Z-IL). The computational twin of `topdown-bottomup.md`.

### 4.8 Attribution-Based / LRP → `distribution-based.detail.md`
$$e_i^{(l)}=\textstyle\sum_j e_j^{(l+1)}\tfrac{|a_i W_{ij}|}{\sum_i|a_i W_{ij}|+\varepsilon}$$
Route error by **contribution**, normalized so shares conserve the incoming error (Kirchhoff-like). $|a\cdot W|$ is a measured current — zero extra compute. Doubles as **LRP**. **The project's locked learning rule.**

### 4.9 Prospective Configuration
**Infer the target activation pattern first**, then nudge weights toward it — the reverse order from backprop. Interferes less across tasks.

### 4.10 Stochastic Variational Propagation (SVP)
Treat each layer's activations as **latent variables**; optimize a **local ELBO** per layer. Layers update independently, global coherence via the variational approximation.

## 5. Decoupled, local-loss & perturbation methods

Break the lock-step of the global backward pass, or estimate the gradient without computing it.

### 5.1 Local error signals (Nøkland & Eidnes, 2019)
A **local loss** (local classifier + similarity-matching) per layer; train each layer on its own loss, **no backprop between layers**. Near-backprop on CIFAR/ImageNet. Ancestor of SGR-style local learning.

### 5.2 Synthetic Gradients / DNI (2017)
A small aux net **predicts the gradient** backprop would send, so a layer updates immediately (decoupled/unlocked); the predictor is trained against the true gradient when it arrives.

### 5.3 SGR — Gradient Reconciliation → `SGR.detail.md`
$$\mathcal{L}_k^{\text{SGR}}=\bigl\|\tfrac{\partial L_k}{\partial x_{k-1}}-\tfrac{\partial L_{k-1}}{\partial x_{k-1}}\bigr\|_2^2$$
Block-wise local learning + a reconciliation penalty forcing adjacent blocks to agree on their shared boundary; shrinks the mismatch $\|\epsilon\|$ that stalls convergence. **>40% memory saving**; ResNet-32/CIFAR-10 **92.91%** vs 92.82% BP.

### 5.4 Node & weight perturbation (and REINFORCE)
$$\Delta\theta\propto-\tfrac{\Delta L}{\xi}\,\xi$$
Jitter an activation/weight, correlate the perturbation with the loss change. Model-free, fully local, but **high variance** scaling badly with parameter count. **REINFORCE** is the stochastic-node version (the reward-modulated rule of §2.11 as a gradient estimator).

### 5.5 e-prop (eligibility propagation, 2020)
$$\Delta w_{ij}=\textstyle\sum_t L_j(t)\,e_{ij}(t)$$
For spiking RNNs: factorize the BPTT gradient into a **local, forward-computable eligibility trace** $e_{ij}$ times a learning signal $L_j$ (which can be a broadcast — combines with feedback alignment). The leading online approximation to BPTT.

---

## 6. Comparison table (bio-plausibility properties)

✅ = has the property; ⚠️ = partial/with caveats. "→ BP grad" asks whether the rule provably approaches the backprop gradient. (All Part-1 optimizers share the backprop profile — weight transport ✅needed, not local, not forward-only — so they are represented by the single "Backprop baseline" row.)

| Method | No weight transport | Derivative-free | Forward-only | Local | Unsup-capable | → BP grad |
| ------ | :---: | :---: | :---: | :---: | :---: | :---: |
| Raw Hebbian | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Oja / GHA | ✅ | ✅ | ✅ | ✅ | ✅ (PCA) | ❌ |
| BCM | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Competitive / SOM | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| STDP | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delta rule | ✅ | ⚠️ | ✅ | ✅ | ❌ | ⚠️ (1 layer) |
| Neuromod. + eligibility | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ (RL) |
| Forward-Forward / SCFF | ✅ | ✅ | ✅ | ✅ | ✅ (SCFF) | ❌ |
| PEPITA | ✅ | ⚠️ | ✅ | ⚠️ | ❌ | ❌ |
| Feedback Alignment | ✅ | ❌ | ❌ | ⚠️ | ❌ | ⚠️ |
| Direct Feedback Align. | ✅ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| Target Prop / DTP | ✅ | ✅ | ❌ | ✅ | ❌ | ⚠️ |
| Contrastive Hebbian | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ (symmetric) |
| Equilibrium Prop | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ (β→0) |
| Predictive Coding | ✅ | ⚠️ | ❌ | ✅ | ✅ | ✅ (limit) |
| Attribution / LRP | ✅ | ✅ | ❌ | ✅ | ❌ | ⚠️ (direction) |
| Local error signals | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Synthetic Gradients | ✅ | ❌ | ❌ | ✅ | ❌ | ⚠️ (predicted) |
| SGR | ✅ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| Node/weight perturb. | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ (noisy) |
| e-prop | ✅ | ❌ | ⚠️ | ✅ | ❌ | ⚠️ (online BPTT) |
| **Backprop + any Part-1 optimizer (baseline)** | ❌ | ❌ | ❌ | ❌ | ❌ | — (it *is* the gradient) |

---

## 7. Standalone deep-dive files

| File | Topic |
| ---- | ----- |
| `gradient-descent.detail.md` | Gradient descent + backprop + SGD (the baseline) |
| `momentum.detail.md` | Momentum & Nesterov (mirrors the Scap EMA-momentum register) |
| `adam.detail.md` | Adam family (AdaGrad→RMSProp→Adam→AdamW + variants) |
| `second-order-methods.detail.md` | Newton / quasi-Newton / natural gradient |
| `SCFF.detail.md` | Self-Contrastive Forward-Forward |
| `SGR.detail.md` | Gradient Reconciliation for local learning |
| `distribution-based.detail.md` | Attribution / loss-sharing + LRP — the project's locked rule |
| `topdown-bottomup.md` | Top-down/bottom-up & predictive coding in the brain (neuroscience) |
| `equilibrium-propagation.detail.md` | Equilibrium Propagation — energy-based analog learning |
| `feedback-alignment.detail.md` | Feedback Alignment & DFA — the weight-transport answer |
| `predictive-coding.detail.md` | Predictive Coding as a learning algorithm |

---

## 8. How these map onto the project's themes

The project cares about four substrate properties — **online, sparse, continuous, resident-weight** — and a learning rule that is **local, no-weight-transport, derivative-free**. Reading the survey through that lens:

- **Gradient descent / SGD** (Part 1) is the **baseline to beat on cost while staying close on direction** — the ruler, not the method. Its four requirements (§0) are exactly what the substrate cannot pay.
- The **attribution rule** (§4.8, `distribution-based.detail.md`) is the chosen rule precisely because $|a\cdot W|$ is a *measured current* — the only entry whose backward signal costs zero extra hardware.
- **Momentum** (§1.3) and **Adam's second moment** (§1.8) are the two statistics a per-weight register must hold — a mean and a second moment of the update signal — both cheap moving averages, both physically present in the Scap (momentum register) and BCM threshold ($\langle a_j^2\rangle$).
- **Equilibrium Propagation** (§4.6) is the strongest "exact gradient from local physics" alternative — its relaxation *is* analog computation.
- **Feedback Alignment / DFA** (§4.1–4.2) de-risk the no-$W^{\top}$ stance; their failure at scale argues for *structured* attribution over random feedback.
- **Predictive Coding** (§4.7) bridges the biology (`topdown-bottomup.md`) to a concrete gradient-approximating algorithm sharing attribution's "error flows along contributions" structure.
- The **forward-only family** (§3) matters wherever a second pass is expensive — a capacitor-charging analog substrate.
- **Second-order methods** (§1.13–1.17) are the off-table far end: an analog substrate cannot form or invert curvature matrices — which is *why* the cheap local rules are the project's bet.
