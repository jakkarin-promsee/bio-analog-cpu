# Feedback Alignment (FA) & Direct Feedback Alignment (DFA)

## Overview / Core Idea

Feedback Alignment is the result that broke the **weight-transport problem's** reputation as a fatal objection to biologically-plausible learning. The objection: backpropagation sends error backward through $W^{\top}$, so the backward path must *know the exact transpose of every forward weight* — a degree of two-way coordination no synapse plausibly has, and an expensive constraint on hardware. Feedback Alignment's answer is almost insolent: **replace $W^{\top}$ with a fixed, random matrix $B$ that has nothing to do with $W$, and train anyway.** It works. The network learns.

The reason it works is the phenomenon the method is named for. With a random fixed feedback matrix $B$, the forward weights $W$ gradually **align** themselves so that $W$ comes to approximate (a scalar multiple of) $B^{\top}$ — or more precisely, so that the angle between the FA update and the true backprop update becomes consistently less than 90°. Once the FA signal is within 90° of the true gradient, it is a **descent direction**: every step still reduces the loss, just along a slightly different path. The network is not given the correct teaching signal; it *reshapes its forward weights until the random teaching signal becomes correct enough.* Learning aligns the forward path to the feedback, rather than forcing the feedback to mirror the forward path.

Two variants:

- **Feedback Alignment (FA)** — keep backprop's layer-by-layer structure, but swap each $W_l^{\top}$ for a fixed random $B_l$. The error still flows sequentially backward through the layers.
- **Direct Feedback Alignment (DFA)** — go further: skip the sequential chain entirely and **project the single output error directly into every layer** through its own fixed random matrix. Every hidden layer is taught straight from the global error, in parallel, with no backward chain at all.

For an analog / local substrate this matters because $B$ can be **anything fixed** — random wiring, set once, never transported, never kept in sync with $W$. It removes the single most-cited reason backprop "can't be physical."

---

## Benchmark

The story of the numbers is "works beautifully where the task is easy, opens a gap where the task is hard" — and that gap is the honest cost of giving up the exact gradient direction.

| Setting | FA | DFA | Backprop |
| ------- | --- | --- | -------- |
| **MNIST** (MLP) | ≈ backprop (~98%+) | ≈ backprop (~98%+) | ~98% |
| **CIFAR-10** (MLP / small conv) | trains, **few-% gap** | trains, **few-% gap** (worse on conv) | reference |
| **ImageNet** (deep conv) | **large gap** — fails to scale | **large gap** — fails to scale | reference |
| **Alignment angle** (diagnostic) | forward weights align so the FA signal sits **< 90°** from the true gradient | same, via direct random projections | (0° by definition) |

Reading it:

- On **MNIST** both FA and DFA are indistinguishable from backprop — the alignment effect fully compensates for the random feedback.
- On **CIFAR-10** a few-percent gap appears; DFA is typically a bit worse than FA on convolutional architectures because a single random projection of the output error is a coarse teaching signal for spatially-structured features.
- On **ImageNet-scale** deep convnets, the FA family **does not keep up** (Bartunov et al., 2018): the alignment that rescues shallow/easy nets is too weak to coordinate very deep, structured networks. This is the established ceiling of the approach.
- The key *positive* result is not an accuracy number at all — it is the **alignment angle staying below 90°**, which is what proves the random signal is a genuine descent direction and not noise.

---

## The weight-transport problem (what FA attacks)

In backprop, the error at layer $l$ is computed from the error at layer $l+1$ by:

$$\delta_l = \bigl(W_{l+1}^{\top}\,\delta_{l+1}\bigr)\odot\sigma'(z_l)$$

The $W_{l+1}^{\top}$ is the problem. It means:

1. the backward pathway must have access to the **exact same weights** as the forward pathway, transposed; and
2. whenever a forward weight changes, its backward counterpart must change **identically and instantly** to stay synchronized.

Biologically there is no known mechanism for a synapse to read out another synapse's weight and use its transpose. In hardware it forces a tight two-way coupling between the forward and backward datapaths. This is *weight transport*, and it was long treated as the decisive reason backprop cannot be what the brain (or a clean analog chip) does.

---

## Feedback Alignment (FA)

The fix is one line: replace the transpose with a **fixed random matrix** $B_l$, drawn once at initialization and never updated:

$$\delta_l = \bigl(B_l\,\delta_{l+1}\bigr)\odot\sigma'(z_l)$$

with the ordinary local weight update $\Delta W_l \propto -\delta_l\,a_{l-1}^{\top}$. $B_l$ has the right *shape* to route the error from layer $l+1$ back to layer $l$, but its *entries* are random and bear no relation to $W_{l+1}$.

Naively this should produce a meaningless teaching signal. It does not, because of alignment:

### Why alignment happens

The forward weight update is driven by $\delta_l$, which is built from $B$. Over training, $W$ moves in directions dictated by $B$, and it can be shown (Lillicrap et al., 2016) that this drives the product $B_{l+1}^{\top}W_{l+1}$ toward a **positive-definite-ish** regime — equivalently, the forward weights rotate until $W_{l+1}$ approximates a scaled $B_{l+1}^{\top}$. The diagnostic is the angle between the FA-prescribed update and the true backprop update:

$$\cos\angle(\delta_l^{\text{FA}},\,\delta_l^{\text{BP}}) > 0 \quad\Longleftrightarrow\quad \text{angle} < 90^\circ \quad\Longleftrightarrow\quad \text{descent direction}.$$

Once the angle is below 90°, the loss decreases every step. FA does not need the *exact* gradient — it only needs a vector on the correct side of the loss surface, and alignment guarantees it gets one. **The feedback is fixed; the forward weights are what move to meet it.**

---

## Direct Feedback Alignment (DFA)

DFA (Nøkland, 2016) removes even the sequential backward chain. Instead of passing error layer-to-layer, it **broadcasts the global output error $e$ directly to every hidden layer** through that layer's own fixed random matrix $B_l$:

$$\delta_l = \bigl(B_l\,e\bigr)\odot\sigma'(z_l), \qquad e = \hat{y} - y$$

Note what is gone: there is no $\delta_{l+1}$ in the formula. Every layer's teaching signal is a fixed random projection of the *same* output error, computed **independently and in parallel**. The backward "pass" is not a pass at all — it is a single fan-out of one error vector to all layers at once.

### Why DFA is even more hardware-friendly

- **No sequential dependency.** All hidden layers can update simultaneously the instant $e$ is known. There is no lock-step reverse sweep.
- **One global signal, fanned out.** The only thing that must reach every layer is the output error $e$ — a single broadcast — plus each layer's private fixed random matrix. This maps cleanly onto a substrate where a global error line is broadcast and each layer has its own fixed local wiring.
- **Same alignment principle.** As with FA, the forward weights align so that $B_l\,e$ becomes a descent direction for layer $l$.

### Where DFA breaks

DFA's coarseness is the price. Projecting the *output* error directly into an early layer skips all the intermediate structure that real backprop would have shaped the signal through. On **convolutional** networks (where the teaching signal should respect spatial locality) and on **very deep** networks (where many layers must be coordinated), a single random projection of the output error is too blunt, and the gap to backprop widens — up to outright failure at ImageNet scale.

---

## Side-by-side

| | Backprop | Feedback Alignment (FA) | Direct Feedback Alignment (DFA) |
| --- | --- | --- | --- |
| Backward signal to layer $l$ | $W_{l+1}^{\top}\delta_{l+1}$ | $B_l\,\delta_{l+1}$ (fixed random $B_l$) | $B_l\,e$ (fixed random $B_l$, global error) |
| Needs weight transport | ✅ yes | ❌ no | ❌ no |
| Sequential backward chain | ✅ yes | ✅ yes | ❌ no — parallel broadcast |
| Layers update in parallel | ❌ | ❌ | ✅ |
| Needs $\sigma'(z)$ | ✅ | ✅ | ✅ |
| Teaching-signal quality | exact gradient | aligned approx (< 90°) | coarser aligned approx |
| Scales to ImageNet | ✅ | ❌ | ❌ |

All three still use the activation derivative $\sigma'(z)$ — FA/DFA solve **weight transport**, not the derivative requirement. (That is the axis where the project's attribution rule goes further: $|a\cdot W|=0$ reproduces dead-unit gating without ever computing $\sigma'$.)

---

## Training loop (DFA, concrete)

```
fix random matrices B_1 ... B_L once at init   (never updated)

forward:   a_0 = x
           for l = 1..L:  z_l = W_l a_{l-1};  a_l = σ(z_l)
           ŷ = a_L
error:     e = ŷ − y                            (one global vector)

teaching:  for every hidden layer l, IN PARALLEL:
              δ_l = (B_l · e) ⊙ σ'(z_l)
update:    for every layer l:
              W_l ← W_l − η · δ_l · a_{l-1}ᵀ
```

There is no backward loop — the `for l` in the teaching step has no dependency between iterations, so it is a parallel fan-out of the single error $e$.

---

## Why this matters for the project

The project's whole learning stance rests on *not* needing $W^{\top}$ in the backward direction (locked decision: attribution, not gradient; no weight transport). Feedback Alignment is the **existence proof** that this stance is not reckless:

- It shows a network can learn with a backward path that is **fixed, random, and never synchronized** with the forward weights — the strongest possible relaxation of weight transport.
- **DFA's broadcast-the-global-error structure** is conceptually close to a substrate with a global error/loss line fanned out to layers with private fixed wiring — and is a useful contrast to the project's *hierarchical, normalized* loss diffusion (which adds the conservation/locality that a single random projection lacks).
- Its **failure at scale** is just as instructive: a backward signal that is merely "a descent direction" is not enough for deep, structured nets. That is precisely the argument for the project's *structured* attribution (normalized $|a\cdot W|$ shares) and for energy-based exact-gradient methods like Equilibrium Propagation — they aim to keep FA's no-weight-transport win while recovering the directional fidelity FA gives up.

In short: FA/DFA de-risk the "drop weight transport" decision, and their limits motivate why the project does not stop at random feedback.

---

## Trade-offs (summary)

```
Feedback Alignment / Direct Feedback Alignment:
  ✅ kills the weight-transport problem — backward matrix is fixed & random
  ✅ forward weights self-align so the random signal becomes a descent direction
  ✅ DFA: no sequential backward pass — all layers update in parallel from one
     broadcast error (very hardware-friendly)
  ✅ trivial to implement; strong on MNIST / shallow nets (≈ backprop)
  ❌ still needs σ'(z) — solves weight transport only, not derivative-freeness
  ❌ teaching signal is approximate (aligned, not exact) — a few-% gap on CIFAR
  ❌ DFA is coarser still; weak on convolutional / spatially-structured nets
  ❌ does NOT scale — large gap / failure on deep ImageNet-scale networks
```
