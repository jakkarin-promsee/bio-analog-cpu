# Distribution-Based Learning (Attribution / Loss-Sharing)

## Overview / Core Idea

Distribution-based learning replaces the **gradient** as the backward signal with **attribution** — it distributes error back to upstream units in proportion to how much each one *contributed* to the output, not how *sensitive* the output is to it.

Backpropagation needs two things that are awkward on biological or analog hardware:

- **Weight transport** — sending error backward needs $W^{\top}$, i.e. the backward path must know the full forward weight matrix of the next layer, transposed. That is non-local.
- **The activation derivative** — backprop needs $\sigma'(z)$ at every neuron of every layer, which requires a differentiable activation and the intermediate pre-activations cached from the forward pass.

Attribution removes both by routing error along a quantity the forward pass *already produced*: the magnitude of the signal that flowed through each weight,

$$c_{ij} = \bigl|\,a_i \cdot W_{ij}\,\bigr|.$$

In analog hardware this is not a number you compute — it is the **current through the weight**, measured for free from the physics of the circuit. The error arriving at a unit is then split across its inputs in proportion to these contributions, normalized so the shares sum back to exactly the incoming error. That normalization is the heart of the method: it makes credit assignment a **conservation law** (Kirchhoff-style — what flows in is split, never amplified), which is where the stability comes from. The same rule, used not to train but to *explain* a trained network, is **Layer-wise Relevance Propagation (LRP)**.

The shift in question is the whole idea:

> Gradient asks: *"if I wiggle weight $W$, how much does the loss change?"* (sensitivity)
> Attribution asks: *"how much did weight $W$ contribute to producing this output?"* (contribution)

---

## Benchmark

Distribution-based learning does not have a single large-scale published accuracy table the way SCFF or SGR do — its "benchmark" is a set of **structural guarantees** plus small-scale demonstrations. Honestly stated:

| Property tested | Result |
| --------------- | ------ |
| **Direction vs. gradient** (signed attribution) | Differs from $W^{\top}\delta\odot\sigma'(z)$ only in (a) the normalization magnitude and (b) the missing $\sigma'(z)$ factor — **the direction is the same**. Dead-neuron behavior is identical (see below). |
| **Conservation (LRP z-rule)** | **Exact** — total relevance is preserved across every layer: $\sum_i R_i^{(\text{input})} = \sum_i R_i^{(\text{hidden})} = \sum_i R_i^{(\text{output})}$. |
| **Explainability (LRP, established use)** | The same rule is the standard tool for producing input-attribution heatmaps of trained CNNs — a mature, widely-used method. |
| **Small-scale learning demonstration** | A single 2-3-3-2 Ganglion trained on $\lvert a\cdot W\rvert$ attribution fits a noisy linear plane to near-perfect, and cuts loss on a nonlinear paraboloid by ~20×. Validity at the atom is shown; **scale is the open question, not validity.** |

So the method's claim is not "it beats backprop on ImageNet." It is: *the direction matches gradient where it matters, conservation is exact by construction, the hardware cost is zero (it is a measured current), and it demonstrably learns at small scale.* The cost side — a vanishing backward signal and a convergence guarantee weaker than gradient's — is in the trade-off section.

---

## Core idea, formalized

Instead of asking "if I wiggle $W$, how much does loss change," attribution asks "how much did this weight contribute to the output." The answer is the current that flowed through the weight during the forward pass:

$$c_{ij} = \bigl|\,a_i \cdot W_{ij}\,\bigr|$$

This is directly measurable from circuit physics — no extra computation, no cached derivative.

---

## The attribution rule

When error $e_j$ arrives at output neuron $j$, it is split back to the input neurons $i$ in proportion to their contributions:

$$e_i = \sum_j \left[\, e_j \times \frac{\lvert a_i \cdot W_{ij}\rvert}{\sum_i \lvert a_i \cdot W_{ij}\rvert + \varepsilon} \,\right]$$

The **normalizing term** $\sum_i \lvert a_i \cdot W_{ij}\rvert$ is the core of the whole system, because it makes the shares sum to one:

$$\sum_i \frac{\lvert a_i \cdot W_{ij}\rvert}{\sum_i \lvert a_i \cdot W_{ij}\rvert} = 1$$

So the error received at $j$ is partitioned among its inputs and **adds back up to exactly the incoming error** — a conservation principle identical in spirit to Kirchhoff's current law: charge that enters a node is divided among the branches, never created.

---

## How this differs from gradient

| Aspect | Gradient (sensitivity) | Attribution (contribution) |
| ------ | ---------------------- | -------------------------- |
| The question | wiggle $W$ → how much does loss change | how much did $W$ contribute to this output |
| Routing | $W^{\top}\cdot\delta$ | $\lvert a\cdot W\rvert / \sum\lvert a\cdot W\rvert$ |
| Needs $\sigma'(z)$ | ✅ yes | ❌ no |
| Needs weight transport | ✅ yes | ❌ no |
| Conservation | by chain rule | by explicit normalization |
| Inactive units | $\sigma'(z)=0$ kills propagation | $\lvert a\cdot W\rvert=0$ kills propagation |

**Dead-neuron behavior is the same** in both. When a ReLU unit is off, $a=\sigma(z)=0$ for $z<0$, so $\lvert a\cdot W\rvert = 0$ — the path is cut exactly as it would be by $\sigma'(z)=0$ in backprop. Attribution reproduces the gating for free, without ever computing $\sigma'$.

---

## How important is the normalizing term?

It is load-bearing. Without it, the unnormalized contributions sum to something that scales with the fan-in $N$:

$$\sum_i c_{ij} \approx N\cdot O(1)$$

so the error passed backward is multiplied by roughly $N$ at **every** layer. Three layers with $N=3$ blows the error up by $27\times$ in the very first epoch. The consequence is a death spiral:

> weights jump hard → all $z_1$ go negative → every ReLU switches off → gradient (and attribution) become 0 → weights never move again → output collapses to 0.

The normalization rescales every backward step into $(0,1)$, so the error passed through a layer can **never** be larger than the parent error. The stability comes from **conservation, not from tuning the learning rate** — you do not have to hand-pick $\eta$ to keep it from exploding, because the math forbids amplification.

---

## Attribution and sign

Raw attribution uses the absolute value, so it loses direction:

$$\text{attribution:}\quad \frac{\lvert a_i\cdot W_{ij}\rvert}{\sum\lvert a\cdot W\rvert}$$

Put the sign back in:

$$\text{attribution + sign:}\quad \frac{a_i\cdot W_{ij}}{\sum\lvert a_i\cdot W_{ij}\rvert}$$

Compare with the gradient:

$$\text{gradient:}\quad W^{\top}\cdot\delta \odot \sigma'(z)$$

They differ in **exactly two places**:

1. **Normalization.** Attribution divides by $\sum\lvert a\cdot W\rvert$; the gradient has no such denominator. This changes the *magnitude* but not the *direction*.
2. **The $\sigma'(z)$ factor.** Attribution has no explicit $\sigma'(z)$ term — but the dead-neuron behavior is identical anyway, because $a=0$ already forces $a\cdot W=0$.

So signed attribution points the same way as the gradient; it just scales the magnitude differently (and that scaling is the conservation property, not a bug).

---

## The cancellation problem

Signed attribution hides a failure mode. Suppose the path products at a neuron are:

$$a\cdot W = [\,+1.0,\; -0.9,\; +0.8,\; -0.7\,]$$

Then:

$$\sum\lvert a\cdot W\rvert = 3.4 \quad\text{(large)}$$
$$\sum (a\cdot W) = 0.2 \quad\text{(tiny)}$$

and the propagated error collapses:

$$\delta_l = \delta \times \frac{0.2}{3.4} = \delta \times 0.06.$$

A network with strong **excitatory/inhibitory cancellation** — large opposing contributions that nearly sum to zero — makes the signed signal vanish fast. (The gradient hits the *same* cancellation through $W^{\top}\delta$, but without the extra normalization it does not pay the double penalty that attribution does.)

Two fixes:

- **Split the excitatory and inhibitory paths** so positives and negatives are routed separately and cannot cancel before normalization.
- **Use an $\varepsilon$-stabilized denominator** so the share stays finite when the signed sum is near zero:

$$\delta_l = \delta \times \frac{a\cdot W}{\lvert\sum(a\cdot W)\rvert + \varepsilon}$$

---

## The chain across layers

Attribution recurses downward, and each step multiplies by a factor in $(0,1)$:

$$e^{(l)} = e^{(l+1)} \times \underbrace{\frac{\lvert a\cdot W\rvert}{\sum\lvert a\cdot W\rvert}}_{\in\,(0,1)}$$

So layers nearer the input receive smaller and smaller error — a **vanishing signal in the backward direction.** For *training*, that is a genuine limitation: the earliest layers learn slowest.

But in the *explainability* context (LRP) the very same property is a **feature, not a bug**, because it is exactly conservation:

$$\sum_i R_i^{(\text{output})} = \sum_i R_i^{(\text{hidden})} = \sum_i R_i^{(\text{input})}$$

Total relevance is preserved through every layer, like current through a circuit. The signal does not vanish in the sense of being lost — it is *redistributed*, conserved at every level.

---

## LRP — attribution in practice

Layer-wise Relevance Propagation uses the identical attribution rule, but to **explain** a trained network rather than to train one:

$$R_i^{(l)} = \sum_j R_j^{(l+1)} \times \frac{a_i\cdot W_{ij}}{\sum_i a_i\cdot W_{ij} + \varepsilon}$$

The output is a relevance score for each input, which visualizes directly as a heatmap of "which inputs mattered." The choice of denominator gives a family of LRP rules trading stability against exact conservation:

| Rule | Denominator | Stability | Conservation |
| ---- | ----------- | --------- | ------------ |
| **z-rule** | $\sum a\cdot W$ | ❌ blows up if $\sum\approx 0$ | ✅ exact |
| **$\varepsilon$-rule** | $\sum a\cdot W + \varepsilon$ | ✅ stable | ❌ slightly broken |
| **$\gamma$-rule** | $W^{+}$ only (positive weights) | ✅ stable | ❌ ignores inhibitory paths |

Code that routes on the **absolute value** $\lvert a\cdot W\rvert$ behaves closest to the **$\gamma$-rule**, since it effectively suppresses the sign cancellation that the z-rule suffers.

---

## Geometric interpretation

Attribution tells each path $(i\to j)$ how much of neuron $j$'s error "budget" it is responsible for:

$$\text{budget}_{ij} = e_j \times \frac{\lvert a_i W_{ij}\rvert}{\sum_i \lvert a_i W_{ij}\rvert}$$

It is like a company dividing **responsibility** among employees by the share of the work each actually did — *not* by how sensitive the outcome is to each person. Sensitivity (gradient) and responsibility (attribution) are different questions, and attribution answers the one that a physical substrate can measure directly.

---

## Connection to retrograde signaling in the brain

Endocannabinoid retrograde signaling in biological neurons works the same way:

> the post-synaptic neuron detects error → synthesizes an endocannabinoid → it diffuses *backward* across the synapse → the amount released is **proportional to firing** → it modulates the pre-synaptic terminal.

The correspondence is one-to-one:

| Biology | Attribution |
| ------- | ----------- |
| endocannabinoid concentration | loss share |
| CB1 receptor density | $\lvert a\cdot W\rvert$ |
| retrograde diffusion | the attribution chain |
| pre-synaptic suppression | the $\Delta W$ update |

The point is conceptual: **attribution is not an algorithm the brain "runs."** It is the natural behavior of an analog system whose backward signal is a diffusing quantity proportional to forward activity. The math falls out of the physics.

---

## Related credit-assignment methods

Distribution-based attribution is one answer to the credit-assignment problem; a few neighbors set it in context:

- **Target propagation** — instead of sending a gradient back, it sends a *target activation* down ("your output should have been this"), and each layer moves toward its target without needing $W^{\top}$ of the next layer. It shares attribution's "no weight transport" goal but carries a target vector rather than a normalized error share, and it inherits the same chained-transform problem — the lowest layer's target has passed through many transforms.
- **Prospective configuration** — the network first *infers* the activation pattern it should settle into after learning, then nudges weights toward that pattern (the reverse order from backprop's "change weights, see what happens"). Intuitively: imagine the result, then adjust the action toward it.
- **Stochastic Variational Propagation (SVP)** — treats each layer's activations as latent variables and optimizes a *local* ELBO per layer, so layers update independently while a variational approximation keeps global coherence.

Attribution's distinctive feature against all three: the backward signal is a quantity the hardware **already measures** ($\lvert a\cdot W\rvert$, a current), and conservation is enforced by an explicit normalization rather than emerging from a chain rule or a probabilistic bound.

---

## Trade-offs (summary)

```
Distribution-based (attribution / loss-sharing) learning:
  ✅ no weight transport (W^T not needed)
  ✅ no σ'(z) needed (dead-neuron gating reproduced for free via a·W = 0)
  ✅ conservation by the normalizing term — error never amplifies backward
  ✅ hardware-friendly — |a·W| is a measured current, zero extra compute
  ✅ direction ≈ gradient once the sign is restored
  ✅ same rule doubles as LRP, a mature explainability method (exact z-rule conservation)
  ❌ vanishing signal toward the input layers (each backward step ×(0,1))
  ❌ cancellation problem when signed (excitatory/inhibitory nearly cancel → signal collapses)
  ❌ no convergence guarantee as strong as gradient's
  ❌ large-scale learning accuracy still unproven — validity shown at the atom, scale is the open question
```

The central trade is **local computation and hardware efficiency** in exchange for a **weaker convergence guarantee and a less exact direction** than the gradient.
