# Equilibrium Propagation (EqProp)

## Overview / Core Idea

Equilibrium Propagation is a learning algorithm for **energy-based networks** that computes the **exact backpropagation gradient** using only **one network, two relaxation phases, and a local contrastive update** — no separate backward network, no weight transport, and no stored computation graph. It is the leading theoretical candidate for learning *on analog hardware*, because the central operation it needs — letting a physical network settle to the minimum of its energy — is exactly what an analog circuit does for free.

The setup: the network is not a feedforward chain but a **dynamical system** whose neuron states $s$ relax toward the minimum of a scalar **energy** $E(s,\theta)$. Inference *is* relaxation: you clamp the input, let the network settle to a fixed point, and read the output off the settled state. Learning then works in two phases:

1. **Free phase** — clamp the input only, let the network relax to equilibrium $s^0$. This is ordinary inference.
2. **Nudged phase** — add a *small* force that gently pulls the output toward the target (strength $\beta$), and let the network relax again to a new equilibrium $s^\beta$.

The weight update is the **difference between the two equilibria**, measured locally at each synapse:

$$\Delta\theta \;\propto\; -\frac{1}{\beta}\left(\frac{\partial E}{\partial\theta}(s^\beta) - \frac{\partial E}{\partial\theta}(s^0)\right)$$

The remarkable theorem (Scellier & Bengio, 2017): as the nudge $\beta \to 0$, this update **equals the gradient of the loss** that backprop would compute — $\Delta\theta \propto -\partial \mathcal{L}/\partial\theta$ — even though every quantity used is available *locally at the synapse* and the *same* network and *same* dynamics produce both phases. The "backward pass" is replaced by "nudge the output a little and let physics re-settle." That is why it is the right shape for analog learning: a real network of op-amps and capacitors relaxes to an energy minimum on its own; EqProp only asks you to measure it twice.

EqProp is the modern, single-network descendant of **Contrastive Hebbian Learning** (the difference-of-two-Hebbian-products rule), generalized to continuous dynamics and arbitrary small nudges.

---

## Benchmark

EqProp's headline is *not* raw accuracy — it is "recovers the true gradient from local physics." The accuracy numbers exist to show the theory survives contact with real datasets.

| Setting | Result |
| ------- | ------ |
| **Theory** | As $\beta\to 0$, the EqProp update **equals the backprop gradient** of the loss (proven for energy-based / fixed-point networks). |
| **MNIST** (fully connected & small conv) | **≈ backprop**, ~2% test error — the gap to BP is within noise on the original networks. |
| **CIFAR-10** (deep ConvNets, "scaling EqProp", Laborieux et al. 2021) | Roughly **~88%** accuracy — trains genuinely deep nets, with a **few-percent gap** to backprop that shrinks as the bias-correcting (symmetric-nudge) estimator is used. |
| **Gradient-estimate fidelity** | With a single one-sided nudge the estimate is **biased** (first-order in $\beta$); a **symmetric two-sided nudge** ($+\beta$ and $-\beta$) cancels the bias to second order and makes the estimated gradient track the true gradient closely. |

Reading it: on small tasks EqProp is indistinguishable from backprop, which is the point — the local, physics-based update *is* the gradient. The remaining work is engineering (long relaxation times, the bias/variance of finite $\beta$, and scaling depth), not a question of whether the principle holds.

---

## Energy-based networks — the substrate EqProp runs on

EqProp does not run on a feedforward net. It runs on a network whose state $s$ (the vector of all neuron activations) evolves to minimize an energy $E(s,\theta)$, where $\theta$ are the trainable parameters (weights and biases). A standard choice is a **Hopfield-like energy**:

$$E(s,\theta) = \frac{1}{2}\sum_i s_i^2 \;-\; \frac{1}{2}\sum_{i\neq j} W_{ij}\,\rho(s_i)\,\rho(s_j) \;-\; \sum_i b_i\,\rho(s_i)$$

where $\rho(\cdot)$ is a nonlinearity (e.g. a hard-sigmoid clamping activations to $[0,1]$) and $W$ is **symmetric** ($W_{ij}=W_{ji}$). The state evolves by gradient descent on the energy:

$$\frac{ds_i}{dt} = -\frac{\partial E}{\partial s_i}$$

Left alone with a clamped input, the network slides downhill in $E$ and stops at a **fixed point** (equilibrium) where $\partial E/\partial s_i = 0$ for all free neurons. That equilibrium is the network's "answer." The symmetry of $W$ is what makes $E$ a valid Lyapunov function (the dynamics actually descend it) and is the analog of "no weight transport" — there is only one weight $W_{ij}$, used the same way in both directions, so the question "does the backward path know $W^\top$?" never arises.

---

## The total function: energy plus a nudge

To learn, EqProp augments the energy with the loss, scaled by a small **nudging parameter** $\beta \ge 0$:

$$F(s,\theta,\beta) = E(s,\theta) + \beta\,\mathcal{C}(s, y)$$

where $\mathcal{C}$ is the cost (e.g. squared error between the output neurons and the target $y$). $F$ is the quantity the network actually minimizes over $s$:

- $\beta = 0$ → $F = E$: pure inference, the network ignores the target.
- $\beta > 0$ small → the output neurons feel a gentle extra force pulling them toward $y$, on top of the normal dynamics.

The nudge is *weak*: it does not clamp the output to the target (that would be Contrastive Hebbian Learning's hard clamp); it only leans on it. The whole trick is that an infinitesimal lean, measured carefully, reveals the gradient.

---

## The two phases

**Free phase ($\beta = 0$).** Clamp the input $x$. Let the network relax to the free equilibrium:

$$s^0 = \arg\min_s E(s,\theta), \qquad \frac{\partial E}{\partial s}(s^0) = 0.$$

Read the prediction off the output neurons of $s^0$. Record the local quantity $\partial E/\partial\theta$ at $s^0$.

**Nudged phase ($\beta > 0$).** Keep the input clamped, turn on the nudge, and relax again to the nudged equilibrium:

$$s^\beta = \arg\min_s\bigl[E(s,\theta) + \beta\,\mathcal{C}(s,y)\bigr].$$

The output (and, by propagation through the recurrent dynamics, the hidden neurons) shifts slightly toward what would reduce the loss. Record $\partial E/\partial\theta$ at $s^\beta$.

The difference between "where the neurons settled normally" and "where they settled when nudged toward the right answer" is the error signal — and it is encoded in the neuron states themselves, not in a separate set of gradient variables.

---

## The learning rule

The parameter update is the normalized difference of the local energy-gradient between the two phases:

$$\boxed{\;\Delta\theta \;=\; -\frac{\eta}{\beta}\left(\frac{\partial E}{\partial\theta}(s^\beta) - \frac{\partial E}{\partial\theta}(s^0)\right)\;}$$

For the Hopfield-like energy above, $\partial E/\partial W_{ij} = -\rho(s_i)\rho(s_j)$, so the weight update becomes a **contrastive Hebbian** rule:

$$\Delta W_{ij} \;=\; \frac{\eta}{\beta}\Bigl(\rho(s_i^\beta)\,\rho(s_j^\beta) \;-\; \rho(s_i^0)\,\rho(s_j^0)\Bigr)$$

Read this directly: *strengthen the connection by how much the product of activities went up under the nudge.* Each synapse needs only its own two endpoints' activities, recorded at the two equilibria — nothing from any other layer, no transposed weights, no derivative chain. It is local in the strongest sense.

---

## Why it equals the backprop gradient

The core theorem connects the two phases to a derivative. Define the loss at equilibrium as a function of $\theta$ via the free fixed point. EqProp's identity is:

$$\frac{\partial \mathcal{L}}{\partial\theta} \;=\; \lim_{\beta\to 0}\frac{1}{\beta}\left(\frac{\partial F}{\partial\theta}(s^\beta,\theta,\beta) - \frac{\partial F}{\partial\theta}(s^0,\theta,0)\right)$$

i.e. the finite-difference of the local energy-gradient across the nudge **is** the loss gradient in the $\beta\to 0$ limit. The deeper statement (Scellier & Bengio): the *transient* of the nudged relaxation — how each neuron starts to move the instant the nudge is applied — carries exactly the same information as the backpropagated error $\delta$ in a feedforward net. EqProp computes backprop's $\delta$ as a **temporal derivative of the neural dynamics**, not as a spatial backward pass. The gradient was always there in the physics; the nudge makes it observable.

A useful intuition: backprop propagates errors *backward in space* (layer $L$ to layer $1$); EqProp propagates the same errors *forward in time* (the nudge introduced at the output ripples back through the recurrent connections as the network re-equilibrates). Same information, different axis.

---

## Bias correction — the symmetric nudge

A single one-sided nudge ($+\beta$) gives a **biased** estimate of the gradient, because the finite-difference is only first-order accurate and the relaxation has its own curvature. The standard fix is the **symmetric (two-sided) estimator**: relax once with $+\beta$ and once with $-\beta$ and center the difference:

$$\Delta\theta \;=\; -\frac{\eta}{2\beta}\left(\frac{\partial E}{\partial\theta}(s^{+\beta}) - \frac{\partial E}{\partial\theta}(s^{-\beta})\right)$$

The two one-sided biases cancel to second order, so the estimate tracks the true gradient much more tightly. This is the change that made EqProp scale to deep ConvNets on CIFAR-10. It costs a third relaxation (free, $+\beta$, $-\beta$) but removes the systematic error.

---

## Training loop (concrete)

```
receive (x, y)

── Free phase ─────────────────────────────────────────
clamp input x
relax dynamics  ds/dt = -∂E/∂s   until equilibrium  → s⁰
read prediction from output neurons of s⁰
record local stats  ρ(sᵢ⁰)ρ(sⱼ⁰)  at every synapse

── Nudged phase ───────────────────────────────────────
keep x clamped, turn on nudge  F = E + β·C(s,y)
relax dynamics again            → s^β
record local stats  ρ(sᵢ^β)ρ(sⱼ^β)

   (for the unbiased version, also relax with -β → s^{-β})

── Update (local, contrastive) ────────────────────────
ΔW_ij = (η/β)·( ρ(sᵢ^β)ρ(sⱼ^β) − ρ(sᵢ⁰)ρ(sⱼ⁰) )
        ( or the symmetric ±β form )
```

Everything inside the loop is either a **relaxation** (which an analog network does physically) or a **local product of two adjacent activities** (which a local circuit can measure). There is no point at which a global, transposed, or cached quantity is required.

---

## Why this is the right shape for analog hardware

- **Relaxation is free.** An analog network of op-amps, resistors and capacitors *is* a physical energy-minimizer. The free and nudged phases are just "let the circuit settle," twice. You are not simulating dynamics — you are reading them.
- **No weight transport.** The energy uses a single symmetric $W$; there is no separate backward weight to keep in sync.
- **The update is a local measurement.** $\rho(s_i)\rho(s_j)$ is the product of two node voltages at a synapse — measurable in place, exactly the kind of quantity an analog substrate exposes (cf. the $|a\cdot W|$ current that the project's attribution rule uses).
- **No stored graph.** Backprop must hold every activation for the backward pass; EqProp holds only the two equilibrium states.

These are the same motivations behind the project's attribution rule — EqProp is the "energy-based, provably-exact-gradient" point in the same design space, and is the natural comparison baseline for any analog learning claim.

---

## Limitations and open issues

- **Relaxation time.** Reaching equilibrium can take many iterations, especially for deep networks; the free and nudged phases are both full relaxations. Real analog hardware settles fast, but in *simulation* this is the dominant cost.
- **Symmetric weights required.** The clean theory needs $W = W^\top$. Real devices have asymmetry; "vector-field" / non-symmetric variants exist but complicate the guarantee.
- **Finite-$\beta$ bias/variance.** Too small a $\beta$ and the difference is swamped by numerical/measurement noise; too large and the finite-difference is inaccurate. The symmetric nudge mitigates but does not eliminate this tension.
- **Scaling depth.** Vanilla EqProp degrades with depth; the ConvNet results needed the bias-corrected estimator and careful initialization to match backprop within a few percent.
- **Continuous-time assumption.** The cleanest results assume the network truly reaches a fixed point each phase; truncated relaxation introduces additional error.

---

## Relationship to neighbors

- **Contrastive Hebbian Learning (CHL):** EqProp's direct ancestor. CHL uses a *hard clamp* of the output (two phases: free and fully-clamped) and the difference of two Hebbian products. EqProp replaces the hard clamp with an *infinitesimal nudge* $\beta$, which (a) generalizes to arbitrary loss functions and (b) yields the exact gradient in the $\beta\to 0$ limit rather than only for the clamped/free extremes.
- **Backprop:** EqProp computes the same gradient; it trades backprop's spatial backward pass for a temporal relaxation transient.
- **Predictive Coding (`predictive-coding.detail.md`):** another two-phase, energy-minimizing, locally-updating scheme that also approximates backprop — but PC minimizes prediction-error energy with explicit error units, while EqProp minimizes a single global energy and reads the gradient from the nudge transient.
- **Attribution (`distribution-based.detail.md`):** shares the "learning signal is a measured local quantity in an analog network" philosophy; EqProp is exact-gradient and energy-based, attribution is conservation-based and cheaper.

---

## Trade-offs (summary)

```
Equilibrium Propagation:
  ✅ computes the EXACT backprop gradient as β→0 (proven)
  ✅ one network, one set of (symmetric) weights — no weight transport
  ✅ update is a local contrastive Hebbian product — measurable in-circuit
  ✅ relaxation = native analog computation; no separate backward pass, no stored graph
  ✅ generalizes Contrastive Hebbian Learning to any loss and arbitrary nudges
  ✅ matches backprop on MNIST; trains deep ConvNets on CIFAR-10 within a few %
  ❌ needs symmetric weights (W = Wᵀ) for the clean guarantee
  ❌ two (or three) full relaxations per update — slow in simulation
  ❌ finite-β estimate is biased unless the symmetric ±β nudge is used
  ❌ degrades with depth without the bias-corrected estimator / careful init
```
