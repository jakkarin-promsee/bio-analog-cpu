# SCFF — Self-Contrastive Forward-Forward

## Overview / Core Idea

SCFF (Self-Contrastive Forward-Forward) is a **forward-only, label-free** training method. It descends from Hinton's Forward-Forward (FF, 2022), which replaces backpropagation with two forward passes — one on "positive" (real) data, one on "negative" (fake) data — and trains every layer **locally** to be loud on positives and quiet on negatives. No gradient ever crosses a layer boundary.

FF's weakness was always the **negative data**. Hinton generated negatives by corrupting the label embedded in the image (overwriting border pixels with a wrong one-hot). That trick only works in a supervised setting and collapses on datasets harder than MNIST. SCFF's single contribution is to **remove that dependency**: it manufactures positive and negative examples out of the batch itself, contrasting each sample against *itself* and against *other samples*. No labels are touched during representation learning.

The contrast is built by **summation, not concatenation**:

- **Positive** = a sample added to itself → "this is one coherent thing":
$$\mathbf{x}_\text{pos} = \mathbf{x}_k + \mathbf{x}_k = 2\mathbf{x}_k$$
- **Negative** = a sample added to a *different* sample in the batch → "this is a mixture, not one thing":
$$\mathbf{x}_\text{neg} = \mathbf{x}_k + \mathbf{x}_n, \quad n \neq k$$

Each layer is then trained, by a purely **local** objective, to produce high activation energy ("goodness") on `x_pos` and low energy on `x_neg`. Because positives and negatives are built only from the data — never from labels — SCFF is an **unsupervised representation learner**. A tiny supervised linear classifier is bolted on *afterward*, on the frozen features, to read out class identity.

The reason this matters for an analog / forward-only substrate: SCFF needs **no derivative of the activation function, no weight transport, no backward pass, and no label wire**. Every layer learns from a scalar it can measure on its own outputs (`‖h‖²`). A single forward sweep — computing the positive and negative responses together — is enough to update the whole network.

---

## Benchmark

All numbers below are obtained with the **main network trained entirely without labels**; only a final single-layer linear classifier sees labels. That is the headline result — near-backprop accuracy on MNIST with zero label information in the feature extractor.

| Dataset              | SCFF accuracy            | Backprop (reference) |
| -------------------- | ------------------------ | -------------------- |
| MNIST (MLP)          | 98.70%                   | ~98.7%               |
| MNIST (CNN)          | 99.37%                   | ~99.4%               |
| CIFAR-10             | 80.75%                   | ~93%                 |
| STL-10               | 77.30%                   | ~90%                 |
| Tiny ImageNet (top-1)| 35.67%                   | ~60%                 |
| Tiny ImageNet (top-5)| 59.75%                   | —                    |

Reading of the table:

- On **MNIST** SCFF is statistically indistinguishable from backprop — the self-contrastive objective is enough to fully separate the ten digit clusters.
- As task complexity rises (CIFAR-10 → STL-10 → Tiny ImageNet) a **gap to backprop opens up**. This is the expected cost of local, label-free learning: each layer optimizes a myopic goodness target with no global error signal to coordinate the layers, so the features it discovers are good but not globally optimal for classification.
- The gap is a feature-quality gap, **not** a classifier gap — the linear readout is the same in both columns. It tells you how much class-relevant structure the unsupervised contrast managed to bake into the representation.

---

## Background: Hinton Forward-Forward and the negative-data problem

FF trains each layer to maximize a **goodness** scalar on real data and minimize it on fake data. For layer $l$ with hidden activation $\mathbf{h}^l$:

$$G^l = \sum_m (h_m^l)^2 = \|\mathbf{h}^l\|^2$$

and the FF per-layer loss (one shared threshold $\theta$):

$$\mathcal{L}^l = \log\!\bigl(1 + e^{-(G^l_\text{pos} - \theta)}\bigr) + \log\!\bigl(1 + e^{+(G^l_\text{neg} - \theta)}\bigr)$$

which wants $G^l_\text{pos} > \theta$ (loud on real) and $G^l_\text{neg} < \theta$ (quiet on fake). The weight update uses the ordinary derivative of $\mathcal{L}^l$ through one layer only — **gradient never propagates across the layer boundary.** That gives FF its two headline advantages: no weight transport, and each layer updates independently.

The cost was the **negative data**. Hinton's negatives embedded a *wrong* label into the corner pixels of the image (one-hot over positions `[0:10]`). This:

1. requires labels (so FF was not really unsupervised), and
2. does not generalize — the corruption trick produces useful negatives on MNIST but degenerate ones on natural images.

SCFF replaces this brittle, supervised negative-generation step with a label-free, data-only one.

---

## Why summation, and why $W_1 = W_2$

The conceptual starting point is to **concatenate two images** and ask the network whether they are "the same thing" or "two different things." A concatenation would feed the pair through two weight blocks $W_1, W_2$:

$$\mathbf{y}_\text{pos} = \phi(W_1\mathbf{x}_k + W_2\mathbf{x}_k)$$
$$\mathbf{y}_\text{neg} = \phi(W_1\mathbf{x}_k + W_2\mathbf{x}_n)$$

But the positive pair is **always** $(\mathbf{x}_k, \mathbf{x}_k)$ — the two slots see identical data. The gradients that flow into $W_1$ and into $W_2$ from the positive term are therefore symmetric, and the two matrices converge to the same value. There is no information that could ever break the symmetry. So we can set $W_1 = W_2 = W$ from the start with no loss of generality:

$$\mathbf{y}_\text{pos} = \phi\bigl(W\cdot 2\mathbf{x}_k\bigr)$$
$$\mathbf{y}_\text{neg} = \phi\bigl(W(\mathbf{x}_k + \mathbf{x}_n)\bigr)$$

The consequence is structural and important: **the input dimensionality never grows.** Because we sum *before* the weight, not concatenate, the layer width is unchanged. SCFF is a drop-in modification of a standard MLP/CNN forward pass — it just feeds it $2\mathbf{x}_k$ or $\mathbf{x}_k + \mathbf{x}_n$ instead of $\mathbf{x}_k$.

---

## Goodness function

Goodness measures **how loud a layer's activation is** — but on the *hidden* activation $\mathbf{h}^l$ (after the weights and nonlinearity), not on the raw input. For a layer of width $M^l$:

$$G^l = \frac{1}{M^l}\sum_{m=1}^{M^l}\bigl(h_m^l\bigr)^2 = \frac{\|\mathbf{h}^l\|^2}{M^l}$$

The $1/M^l$ normalization makes the scalar comparable across layers of different widths. Goodness is the only signal each layer needs — it is computed entirely from that layer's own outputs.

> **Draft-6.0 Phase-1 note (2026-06-20).** The *paper* uses this **mean** form, $\|h\|^2/M$. The project's
> Phase-1 sim deliberately uses the **sum** form, $G=\|h\|^2$ (which is what `ideas1.md` and the run-spec
> already write), for one substrate reason: under unit-norm inter-layer inputs the mean goodness is
> $\approx 1/M\!\approx\!0.015$, so a fixed threshold like $\theta=2.0$ is unreachable under **plain online
> SGD** (the paper only reaches it with Adam × many epochs). The sum form is $\approx 1$ at init,
> *width-independent*, makes $\theta=2.0$ sane, and needs no per-weight optimizer state — substrate-faithful.
> Verified in [`../../src/phase1/exp0`](../../src/phase1/exp0/experiment-0.md) (the gate run): mean starves the
> deeper layers, sum separates them. The gradient simply drops the $1/M^l$ (becomes $2\,h^l(h^{l-1})^\top$).

---

## Loss function (two thresholds, dead zone)

SCFF uses **two separate thresholds** $\Theta_\text{pos}$ and $\Theta_\text{neg}$, where FF used one. The per-layer loss:

$$\mathcal{L}^l = -\,\mathbb{E}\bigl[\log\sigma\!\bigl(G^l_\text{pos} - \Theta_\text{pos}^l\bigr)\bigr]\;-\;\mathbb{E}\bigl[\log\sigma\!\bigl(\Theta_\text{neg}^l - G^l_\text{neg}\bigr)\bigr]$$

with $\sigma$ the logistic sigmoid. The two terms want:

- $G^l_\text{pos} > \Theta_\text{pos}\;\Rightarrow\;\sigma(G_\text{pos}-\Theta_\text{pos})\to 1\;\Rightarrow$ first term $\to 0$ (push positive goodness **up**),
- $G^l_\text{neg} < \Theta_\text{neg}\;\Rightarrow\;\sigma(\Theta_\text{neg}-G_\text{neg})\to 1\;\Rightarrow$ second term $\to 0$ (push negative goodness **down**).

The interval $[\Theta_\text{neg},\,\Theta_\text{pos}]$ is a **dead zone**: when a goodness value lands inside it, the sigmoid is near its saturated tail and the gradient is ~0. The dead zone is a stability device — it stops the layer from fighting over examples whose goodness is already on the correct side of its threshold, and it decouples the "raise the positives" and "lower the negatives" pressures so they do not oscillate against each other. A single shared threshold (as in FF) cannot create this margin.

---

## Gradient update (local, per layer)

Differentiating $\mathcal{L}^l$ with respect to the layer weights gives a fully **local** update — only quantities measured at this layer appear:

$$
\nabla_{W^l}\mathcal{L}^l
= \underbrace{\bigl(\sigma(G^l_\text{pos} - \Theta_\text{pos}) - 1\bigr)}_{\text{pulls } G_\text{pos}\ \text{up}}\cdot\frac{2}{M^l}\,\mathbf{h}^l_\text{pos}\,(\mathbf{h}^{l-1}_\text{pos})^{\!\top}
\;+\;
\underbrace{\sigma(G^l_\text{neg} - \Theta_\text{neg})}_{\text{pulls } G_\text{neg}\ \text{down}}\cdot\frac{2}{M^l}\,\mathbf{h}^l_\text{neg}\,(\mathbf{h}^{l-1}_\text{neg})^{\!\top}
$$

Structure of the update:

- The factor $\dfrac{2}{M^l}\mathbf{h}^l(\mathbf{h}^{l-1})^{\top}$ is $\partial G^l/\partial W^l$ — the goodness gradient. (The activation derivative $\phi'(z)$ is folded into $\mathbf{h}^l$ here; in code, autograd through one layer produces it.)
- The scalar in front is the **sigmoid error** for that branch. For positives it is negative ($\sigma - 1 < 0$), so the step *raises* $G_\text{pos}$; for negatives it is positive, so the step *lowers* $G_\text{neg}$.
- Crucially, **no term in this expression comes from another layer.** There is no $W^{l+1\top}$, no incoming $\delta$, no backward chain. Each layer is a self-contained learner.

---

## Layer normalization before passing on

Between layers, the hidden vector is **normalized to unit length** before it becomes the next layer's input:

$$\hat{\mathbf{h}}^l_\text{pos} = \frac{\mathbf{h}^l_\text{pos}}{\|\mathbf{h}^l_\text{pos}\|}, \qquad \hat{\mathbf{h}}^l_\text{neg} = \frac{\mathbf{h}^l_\text{neg}}{\|\mathbf{h}^l_\text{neg}\|}$$

This is essential. Goodness is *length* (`‖h‖²`). If the raw, un-normalized $\mathbf{h}^l$ were passed forward, layer $l+1$ could "cheat" — it would inherit the goodness layer $l$ already produced and would not have to learn anything; magnitude would compound layer over layer. Normalizing strips out the length and forwards only the **direction** (the pattern), forcing every layer to re-derive its own goodness from the pattern alone. The first layer learns from magnitude+pattern; every later layer learns from pattern only.

---

## Training loop (concrete)

```
receive batch {x_1, x_2, ..., x_N}

build pairs:
  x_pos = 2·x_k            (for every k)
  x_neg = x_k + x_n        (n drawn at random from the batch, n ≠ k)

── Layer 1 ──────────────────────────────────────────────
forward pos:  h¹_pos = φ(W¹ · x_pos)
forward neg:  h¹_neg = φ(W¹ · x_neg)
goodness:     G¹_pos = ‖h¹_pos‖²/M¹
              G¹_neg = ‖h¹_neg‖²/M¹
loss:         L¹ = -log σ(G¹_pos - Θ_pos) - log σ(Θ_neg - G¹_neg)
update:       W¹ ← W¹ - η·∂L¹/∂W¹
normalize:    ĥ¹_pos = h¹_pos/‖h¹_pos‖     ← layer-norm before passing on
              ĥ¹_neg = h¹_neg/‖h¹_neg‖

── Layer 2 ──────────────────────────────────────────────
forward pos:  h²_pos = φ(W² · ĥ¹_pos)
... identical for every layer

── after all layers are trained ──────────────────────────
freeze the entire network
train a single linear classifier on labeled data (ordinary backprop, 1 layer)
```

The positive and negative forwards can be run **in the same sweep** (batched together), so SCFF is effectively a single forward pass per update — no separate backward phase.

---

## Why $x_\text{pos} = 2x$ gives a free inductive bias

The factor of 2 was **not chosen deliberately** — it is an automatic side effect of "concatenate the pair + share the weights." But it turns out to be exactly what the goodness objective wants. Because goodness is $\|\mathbf{h}\|^2$ and $\mathbf{h}_\text{pos} = \phi(2W\mathbf{x}_k)$:

$$G_\text{pos} = \frac{\|\phi(2W\mathbf{x}_k)\|^2}{M} \approx 4\cdot G(\mathbf{x}_k)$$

(exactly $4\times$ for a positively-homogeneous $\phi$ like ReLU, because $\phi(2z) = 2\phi(z)$ and goodness squares the activation). So **positives are born ~4× louder than negatives.** The network gets a head start: positives already sit high on the goodness axis and negatives sit lower, simply because of the magnitudes, before any pattern learning happens.

If one instead normalized the positive (e.g. used $\tfrac{1}{2}(\mathbf{x}_k+\mathbf{x}_k)=\mathbf{x}_k$), positives and negatives would have **similar scale**, and the network would have to separate them on pattern alone — a much harder problem. The "accidental" factor of 2 aligns the construction with the goodness metric, which is why it works.

---

## Geometry of the negative

$$\mathbf{x}_\text{neg} = \mathbf{x}_k + \mathbf{x}_n$$

If $\mathbf{x}_k$ is a "3" and $\mathbf{x}_n$ is a "7", their sum lands **between** the two clusters in input space — it is a point that belongs to neither class. The objective forces the network to give this in-between point *low* goodness. Doing that for many random cross-class pairs effectively **pushes the clusters apart**: the region between any two clusters must be low-goodness, so the clusters are driven to occupy separated, high-goodness islands.

The network achieves this **without ever knowing which cluster is which class.** It only learns "these regions are coherent (high goodness), the spaces between them are not." Class identity is recovered later by the supervised readout. This is what makes SCFF a clustering / representation method, not a classifier.

---

## Output representation

The output fed to the downstream classifier is **not** just the last layer $\mathbf{h}^L$. It is the **concatenation of every layer's activation**:

$$\mathbf{r} = [\mathbf{h}^1;\ \mathbf{h}^2;\ \ldots;\ \mathbf{h}^L] \in \mathbb{R}^{\sum_l M^l}$$

Each layer captures features at a different abstraction level (early layers: edges/textures; later layers: parts/shapes). Taking only $\mathbf{h}^L$ would throw away every low-level feature the early layers learned. Concatenating keeps all abstraction levels available to the linear readout.

Properties of $\mathbf{r}$:

- **Non-negative** everywhere (ReLU output).
- **Sparse** — ReLU zeros all negative pre-activations, so most coordinates are 0.
- **Magnitude-encoded** — cluster membership is carried in activation *energy*, which is exactly what goodness optimized.

---

## The two phases are cleanly separated

```
Phase 1 — Representation learning  (NO labels seen):
  SCFF trains the whole network with self-contrastive pairs.
  The network learns "what is similar / what is different."
  It has no idea what any cluster is called.

Phase 2 — Classification  (labels seen for the first time):
  Freeze the whole network.
  Train one linear classifier on top of r,
  with ordinary backprop on a small amount of labeled data.
```

Phase 1 does all the heavy lifting and consumes no labels. Phase 2 is cheap — a single linear layer mapping an already-separated representation to class names.

---

## A common misreading to avoid

SCFF does **not** construct negatives by gradient ascent on goodness, i.e. it is **not**

$$\mathbf{x}_\text{neg} = \mathbf{x} - \alpha\,\frac{\partial G}{\partial \mathbf{x}}\qquad(\text{this is a different idea, not SCFF}).$$

SCFF uses **plain data augmentation by summation** ($\mathbf{x}_k + \mathbf{x}_n$). All of the innovation is in *how the pair is built from the batch*, not in the goodness formula — goodness and the sigmoid loss are essentially Hinton's, just with the two-threshold dead zone added.

---

## Place in the forward-only family

SCFF is one branch of a small family of forward-only / local-goodness methods that all descend from FF. Each one attacks a different FF weakness:

| Method | What it adds over plain FF | Cross-layer coordination | Negative data |
| ------ | -------------------------- | ------------------------ | ------------- |
| **FF** (Hinton 2022) | the goodness idea itself; per-layer local update | none — each layer myopic | label-corrupted images (supervised) |
| **SCFF** (this doc) | label-free negatives by self/cross summation; two-threshold dead zone | none — still myopic per layer | self-sum vs cross-sum (unsupervised) |
| **CFF** (Collaborative FF) | each layer optimizes a *weighted sum* of all layers' goodness, $G^l_\text{collab}=\sum_k w_{lk}G^k$ ($w_{lk}$ fixed or learned) | yes — lower layers see what upper layers want | inherited from FF/SCFF |
| **Mono-Forward** | a single forward pass, no separate negative pass; contrast generated internally | n/a | none — self-generated within one pass |

The trade space: FF and SCFF are the cheapest per update (one sweep, fully local) but the most myopic — no layer knows what a deeper layer needs. CFF buys cross-layer coordination by sending a *scalar* goodness signal between layers, which is coarse. Mono-Forward is the most hardware-friendly when a forward pass is expensive (e.g. an analog substrate where a capacitor must wait to charge), because it never runs the second pass at all. SCFF sits at the "fully unsupervised, fully local, one effective sweep" corner.

---

## Relationship to contrastive learning

SCFF is a contrastive method, but a degenerate, cheap one. Standard contrastive learning (SimCLR, etc.) needs augmented views, a projection head, a temperature-scaled InfoNCE loss, and backprop through the whole encoder. SCFF replaces all of that with:

- "views" = self-sum vs cross-sum,
- "similarity" = scalar goodness `‖h‖²`,
- "loss" = local two-threshold sigmoid, no backprop.

It trades the tightness of InfoNCE for locality and forward-only computation — fewer guarantees, far cheaper per update.

---

## Trade-offs (summary)

```
Self-Contrastive Forward-Forward:
  ✅ no labels needed for the feature extractor (fully unsupervised phase 1)
  ✅ no weight transport, no σ'(z) chain across layers — fully local
  ✅ no input-size growth (sum, not concat); shared weights W₁=W₂
  ✅ single forward sweep per update (pos & neg batched together)
  ✅ free inductive bias from the accidental ×2 magnitude
  ✅ all-layer concatenated, sparse, non-negative representation
  ❌ accuracy gap to backprop grows with task complexity (myopic per-layer goal)
  ❌ no global coordination between layers — features good, not globally optimal
  ❌ unsupervised clustering only; needs a supervised readout to name classes
  ❌ cluster positions can drift run-to-run (no label anchor in phase 1)
```
