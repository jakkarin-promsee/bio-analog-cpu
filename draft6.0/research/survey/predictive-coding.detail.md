# Predictive Coding (as a Learning Algorithm)

## Overview / Core Idea

Predictive Coding (PC) is the **computational, trainable** version of the brain's predict-then-correct architecture described in `topdown-bottomup.md`. Where that file is the neuroscience (cortical layers, V1→IT, illusions), this file is the **algorithm**: a concrete, math-complete learning scheme that uses only **local computation and prediction-error messages**, runs on a network of "value units" and "error units," and — this is the headline — **provably converges to the backpropagation gradient** under the right conditions. It is one of the few biologically-plausible algorithms that is not merely *inspired by* backprop but *equal to it in a limit*.

The mechanism in one breath: every layer continuously tries to **predict the layer below it** (top-down). The mismatch between a layer's actual state and the prediction coming from above is an **error**, computed locally by dedicated error units. Learning has two interleaved processes:

1. **Inference (relaxation):** with the weights held fixed, the network adjusts its *activities* to make all the local predictions as consistent as possible — it relaxes until prediction error is minimized across all layers. This is the network "settling on an interpretation."
2. **Learning:** once activities have settled, each weight is updated by a **purely local Hebbian product** of the local error and the local activity. No gradient is routed; the error was already computed locally.

Because the error at each layer is computed as "what I am minus what was predicted of me," and that error is what drives both the activity relaxation and the weight update, PC is **attribution-shaped**: error is attributed to the units that produced it, through the network's own structure, exactly the way the project's `distribution-based.detail.md` rule attributes loss along contributions. The deep result tying it to backprop is what makes PC worth a full read: it shows the brain-like, local, top-down/bottom-up loop is not a crude approximation but can recover the *exact* signal backprop computes.

---

## Benchmark

PC's value, like Equilibrium Propagation's, is a *theorem first, accuracy second*: it shows a local predict-and-correct loop can be exact.

| Setting | Result |
| ------- | ------ |
| **Theory — approximation** | PC's weight updates **approximate the backprop gradient**; under specific conditions (small output error / appropriate relaxation) the approximation becomes tight (Whittington & Bogacz, 2017). |
| **Theory — exactness** | With **Z-IL** (Zero-divergence Inference Learning, Song et al., 2020), PC produces weight updates **exactly equal** to backprop's, at every step, for MLPs/CNNs/RNNs. |
| **MNIST / small** | **≈ backprop** — the local PC loop matches backprop accuracy on standard small benchmarks. |
| **CIFAR-10 (conv PC nets)** | trains genuinely; **small gap** to backprop, narrowing with the exact-update variants. |
| **Property** | fully **local** updates, **no weight transport** for the learning rule, error carried only by local prediction-error messages — the bio-plausible boxes are ticked while matching/equalling the gradient. |

Reading it: on small tasks PC is not "close to" backprop, it *is* backprop computed a different way (with Z-IL, exactly). The open frontier is the same as for every local method — scaling depth/dataset while keeping the relaxation cheap — but the principle (local prediction error ⇒ the true gradient) is on solid theoretical ground.

---

## The architecture: value units and error units

PC organizes the network as a hierarchy of layers, each holding **two** populations:

- **Value units $\mu_l$** — the layer's current *belief* / representation (what it thinks is there).
- **Error units $\varepsilon_l$** — the *prediction error* at that layer: how far the actual value is from what the layer above predicted.

The top-down prediction of layer $l$ is generated from the layer above through the weights:

$$\hat{\mu}_l = f\bigl(W_l\,\mu_{l+1}\bigr)$$

and the error unit computes the mismatch (optionally precision-weighted by $\Sigma_l^{-1}$):

$$\boxed{\;\varepsilon_l = \mu_l - f\bigl(W_l\,\mu_{l+1}\bigr)\;}$$

So each error unit needs only two things, both local: its own layer's value $\mu_l$ and the prediction $f(W_l\mu_{l+1})$ coming down from the layer directly above. No global information, no transposed weights to *compute* the error.

---

## The objective: total prediction-error energy

The whole network minimizes a single scalar — the **sum of squared prediction errors** across all layers (a free-energy / sum-of-squared-residuals functional):

$$F = \sum_l \frac{1}{2}\,\|\varepsilon_l\|^2 = \sum_l \frac{1}{2}\,\bigl\|\mu_l - f(W_l\mu_{l+1})\bigr\|^2$$

Two different "knobs" minimize $F$, on two different timescales:

- the **activities** $\mu_l$ (fast — inference), and
- the **weights** $W_l$ (slow — learning).

This is the same two-timescale structure as Equilibrium Propagation, but here the energy is explicitly a sum of *local prediction errors*, and the error units make that error a physical signal in the network rather than something inferred from a nudge.

---

## Phase 1 — Inference (relax the activities)

Clamp the input (and, during training, the output target), freeze the weights, and let the value units descend $F$:

$$\frac{d\mu_l}{dt} = -\frac{\partial F}{\partial\mu_l} = -\varepsilon_l + \Bigl(\frac{\partial f}{\partial \mu_l}\Bigr)^{\!\top}\!W_l^{\top}\,\varepsilon_{l-1}$$

Read the two forces on each value unit:

- $-\varepsilon_l$ — the **bottom-up** pull: reduce *this* layer's own prediction error (move $\mu_l$ toward what was predicted of it).
- $+W_l^{\top}\varepsilon_{l-1}$ (times the local slope $f'$) — the **top-down** pull: account for the error you are causing in the layer *below* you.

Each value unit settles where these two balance — where the layer is simultaneously consistent with the prediction from above and a good predictor for the layer below. This is literally the predictive-coding loop from the neuroscience file: bottom-up error meets top-down prediction, and the representation relaxes until they agree. When relaxation finishes, $\frac{d\mu_l}{dt}=0$ and the network has "settled on an interpretation."

(Note the $W_l^{\top}$ here is part of the *inference dynamics on activities*; in the brain this is implemented by symmetric/feedback connections, and several PC formulations relax this assumption. The *learning* rule below needs no transpose.)

---

## Phase 2 — Learning (update the weights, locally)

Once the activities have settled, each weight is updated by gradient descent on the *same* $F$ — which, because $\varepsilon_l$ and $\mu_{l+1}$ are already sitting in the network, is a **local Hebbian product**:

$$\boxed{\;\Delta W_l \;\propto\; -\frac{\partial F}{\partial W_l} \;=\; \varepsilon_l\;f(\mu_{l+1})^{\top}\;}$$

That is the entire learning rule: **(local prediction error at this layer) × (activity from the layer above).** Each synapse sees only its two endpoints — the error unit it connects to and the value unit it reads from. There is no backward pass, no routed gradient, no $W^{\top}$ in the learning step. The "credit assignment" was done by the inference relaxation, which spread the errors into place; the weight update just reads them off.

---

## Why PC converges to the backprop gradient

This is the result that elevates PC above "biologically-inspired heuristic."

**Whittington & Bogacz (2017):** for a hierarchical PC network with the structure above, if you run inference to equilibrium and the output error is small, the PC weight updates $\Delta W_l$ **approximate the gradients that backprop would compute** for the same feedforward network. The intuition: at the inference fixed point, the settled error units $\varepsilon_l$ take on the same values as backprop's propagated errors $\delta_l$ — the relaxation *is* the backward pass, performed by local dynamics instead of an explicit reverse sweep. The top-down/bottom-up balance in the inference equation is exactly the chain rule, unrolled in time.

**Z-IL — exactness (Song et al., 2020):** with a particular initialization (start activities at the feedforward pass values) and a particular update schedule (update each layer's weights at the specific inference step when its error equals backprop's), PC's updates become **exactly equal** to backprop's, step for step — not just in a small-error limit. This holds for MLPs, CNNs, and RNNs. So PC is not an approximation of backprop in disguise; it is a *reformulation* of it in which every operation is local and every message is a prediction error.

The takeaway: the brain-style loop of "predict downward, send error upward, relax, update locally" computes the same thing as backprop, with none of backprop's non-local machinery.

---

## Training loop (concrete)

```
receive (x, y)

initialize value units μ_l   (e.g. to the feedforward pass — Z-IL)
clamp:  μ_input = x,  μ_output = y      (target clamped during training)

── Inference phase (weights frozen) ───────────────────
repeat until settled:
    for every layer l:
        ε_l = μ_l − f(W_l μ_{l+1})                 # local prediction error
        dμ_l = −ε_l + f'(·) · (W_lᵀ ε_{l-1})        # bottom-up − top-down
        μ_l ← μ_l + γ · dμ_l                        # relax activity
                                                    # (input & output stay clamped)

── Learning phase (activities settled) ────────────────
for every layer l:
    ΔW_l = ε_l · f(μ_{l+1})ᵀ                        # local Hebbian product
    W_l ← W_l + η · ΔW_l
```

Everything inside is local: an error is a subtraction of a value and a top-down prediction; an activity update is a weighted sum of the two adjacent errors; a weight update is a product of the local error and the local activity.

---

## Relationship to the neuroscience (`topdown-bottomup.md`)

This file and `topdown-bottomup.md` are two views of one idea:

| `topdown-bottomup.md` (biology) | this file (algorithm) |
| --- | --- |
| representation units / error units in cortex | value units $\mu_l$ / error units $\varepsilon_l$ |
| top-down prediction (IT → V4 → V1) | $\hat{\mu}_l = f(W_l\mu_{l+1})$ |
| bottom-up sends *prediction error* only | $\varepsilon_l = \mu_l - \hat{\mu}_l$ propagated up |
| iterative refinement over 100–300 ms | the inference relaxation loop |
| synaptic change at the settled state | $\Delta W_l \propto \varepsilon_l\,f(\mu_{l+1})^{\top}$ |
| optical illusions = strong prior wins | strong top-down term dominates a weak/ambiguous $\varepsilon$ |

If you want the wiring, the cortical layers, and the evidence, read the neuroscience file. If you want the energy function, the relaxation dynamics, and the proof that it equals backprop, this is the file.

---

## Relationship to other methods here

- **Attribution / LRP (`distribution-based.detail.md`):** PC is attribution made dynamic. Both attribute error to contributing units locally; attribution does it in one normalized backward step (conservation by construction), PC does it by relaxing prediction errors to equilibrium (and provably hits the backprop gradient). PC is more exact; attribution is cheaper and needs no relaxation.
- **Equilibrium Propagation (`equilibrium-propagation.detail.md`):** the closest cousin — both are two-phase, energy-minimizing, locally-updating, gradient-recovering. EqProp minimizes a single global energy and reads the gradient from a *nudge transient*; PC minimizes an explicit *sum of prediction errors* with dedicated error units. EqProp needs symmetric weights and a nudge; PC needs the inference relaxation and (for the clean form) feedback weights.
- **Backprop:** PC computes the same gradient (exactly, with Z-IL), trading the reverse sweep for a local relaxation.
- **Forward-Forward family:** also local and biologically motivated, but FF discards the gradient entirely for a per-layer goodness scalar; PC keeps the (exact) gradient via prediction-error dynamics.

---

## Limitations and open issues

- **Inference cost.** Every weight update is preceded by a full activity relaxation to equilibrium — many inner iterations per outer step. This is the dominant cost in simulation (the brain/analog hardware relaxes in real time, so the cost is implementation-specific).
- **Feedback weights / symmetry.** The clean inference dynamics use $W_l^{\top}$ as the top-down/feedback path; biologically and in hardware these feedback weights must come from somewhere (separately learned feedback, or a symmetry assumption). The *learning* rule is transpose-free, but the *inference* dynamics are not, in the basic formulation.
- **Precision parameters.** Precision-weighting ($\Sigma_l^{-1}$ on the error units) is powerful but adds parameters/dynamics that must be set or learned.
- **Scaling.** As with all local methods, matching backprop on large, deep, structured tasks while keeping relaxation cheap remains the active frontier; the exactness results are strongest on standard MLP/CNN scales.

---

## Trade-offs (summary)

```
Predictive Coding (as a learning algorithm):
  ✅ fully local learning rule — ΔW = (local error)·(local activity)ᵀ
  ✅ error carried only by local prediction-error messages — attribution-shaped
  ✅ approximates the backprop gradient; EXACTLY equals it with Z-IL
  ✅ the computational twin of the brain's top-down/bottom-up predictive loop
  ✅ unsupervised-capable (it is a generative model); supervises by clamping the output
  ✅ matches backprop on MNIST; trains conv nets with a small, closing gap
  ❌ each update needs a full activity-relaxation (inference) loop — costly in sim
  ❌ basic inference dynamics use feedback/transpose weights (symmetry assumption)
  ❌ precision parameters add tuning surface
  ❌ scaling deep/large while keeping relaxation cheap is still open
```
