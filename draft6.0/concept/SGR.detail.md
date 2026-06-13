# SGR — Gradient Reconciliation for Local Learning

## Overview / Core Idea

SGR is a **regularizer for local (block-wise) learning** that fixes the one thing local learning gets wrong: adjacent blocks pull their shared boundary in *different directions*.

Local learning splits a deep network into $K$ blocks. Each block is trained on its **own local loss** through a tiny auxiliary head, and the gradient is **not** allowed to flow across the block boundary — you `detach` the activation between blocks. This is what buys local learning its two advantages: you never have to store every layer's activation for a global backward pass (>40% memory saving), and blocks can in principle be updated in parallel. The price is **myopia**. Block $k-1$ updates its weights to reduce its own local loss $L_{k-1}$ — but what block $k$ actually *needs* is for its input to move in the direction that reduces $L_k$. Those two directions are not the same. The disagreement between them is a per-sample **gradient mismatch** $\boldsymbol{\epsilon}$:

$$\boldsymbol{\epsilon}^{(i)} = \nabla_{x_{k-1}}L_k^{(i)} - \nabla_{x_{k-1}}L_{k-1}^{(i)}$$

If $\|\boldsymbol{\epsilon}\|$ is large, the last block's loss is no longer guaranteed to converge (proof below). SGR's single idea: add a cheap penalty at every boundary that **forces the deeper block's gradient and the shallower block's gradient to agree on how the shared boundary should move.** It reconciles the locally-optimal directions so a stack of myopic blocks behaves like an end-to-end-trained network — *without ever running a backward pass across a block boundary, without weight transport, and without adding any learnable parameters.* The only thing that crosses a boundary is one stored tensor: the previous block's boundary gradient.

(The name reads as "gradient reconciliation" — the SGR regularizer reconciles the per-block gradients at each boundary. The backbone is unchanged; SGR is a term you add to each block's local loss.)

---

## Benchmark

Local learning's headline claim is "match backprop accuracy at a large memory discount." SGR is what makes the accuracy match hold up as you cut the network into more blocks.

| Model / Dataset            | Blocks $K$ | SGR accuracy | Global BP (reference) | Memory vs BP |
| -------------------------- | ---------- | ------------ | --------------------- | ------------ |
| ResNet-32 / CIFAR-10       | 2          | **92.91%**   | 92.82%                | reduced      |
| ResNet-50 / ImageNet       | 3          | within **<1%** of BP | reference        | **>40% saved** |
| ViT / ImageNet             | (blocked)  | within **<1.5%** of BP | reference     | **>40% saved** |

Reading of the table:

- On **ResNet-32 / CIFAR-10 at $K=2$**, SGR (92.91%) slightly *exceeds* global backprop (92.82%) — at two blocks the mismatch is small and the reconciliation term recovers essentially all of the lost coordination.
- On **ImageNet** at larger depth (ResNet-50, $K=3$, and a blocked ViT), SGR stays within ~1–1.5% of global backprop while cutting activation memory by **more than 40%**. The remaining gap is the residual cross-block coordination that a local method cannot fully recover.
- The point of the benchmark is the *pair* of numbers: accuracy ≈ backprop **and** memory ≪ backprop, at the same time. Plain local learning without SGR gives up much more accuracy as $K$ grows; SGR is what keeps the accuracy column flat while the memory column drops.

---

## The problem SGR solves (in full)

Ordinary local learning carves the network into $K$ blocks and trains each on a local loss $L_k$. The hidden assumption is that "make every block individually good" produces "the whole stack is good." It does not, because the blocks share boundaries and disagree about them.

Concretely, at the boundary $x_{k-1}$ (the output of block $k-1$, which is also the input of block $k$) two different gradients live:

- $\nabla_{x_{k-1}} L_{k-1}$ — how block $k-1$'s **own** local loss wants its output to move.
- $\nabla_{x_{k-1}} L_{k}$ — how block $k$'s loss wants its **input** to move.

Block $k-1$ only ever follows the first one. Block $k$ silently wishes for the second. The gap is the mismatch $\boldsymbol{\epsilon}$.

### Why the mismatch breaks convergence

SGR's analysis gives a one-step bound on the final-block loss $L_K$ under a $\mu$-strong-convexity / smoothness assumption, with step size $\alpha$:

$$L_K^{(i+1)} - L_K^* \;\leq\; (1-\alpha\mu)\,\bigl(L_K^{(i)} - L_K^*\bigr) \;+\; \alpha\,\|\boldsymbol{\epsilon}^{(i)}\|^2$$

Two terms compete:

- $(1-\alpha\mu)\,(L_K^{(i)} - L_K^*)$ is the **contraction** term. With $0 < \alpha\mu < 1$ it shrinks the loss gap every iteration — this is the part that *would* converge.
- $\alpha\,\|\boldsymbol{\epsilon}^{(i)}\|^2$ is an **error floor** that is *injected fresh every iteration*. It does not shrink with the loss; it is set by how badly the blocks disagree.

If $\|\boldsymbol{\epsilon}\|$ is small, the contraction wins and $L_K$ drives down toward $L_K^*$. If $\|\boldsymbol{\epsilon}\|$ is large, the additive floor dominates the contraction and the final loss **stalls at a plateau set by the mismatch** — it never reaches the optimum no matter how long you train. So the whole game is to **keep $\|\boldsymbol{\epsilon}\|$ small.** That is exactly what SGR's regularizer does.

---

## Architecture

SGR does **not** change the main network. You keep a standard ResNet or ViT backbone untouched. The only addition is a small **local head** attached to the output of every block:

```
x_0 (input)
    │
[Block 1] ──► x_1 ──► [head_1] ──► ŷ_1 ──► L_1(ŷ_1, y)
    │                  conv 1×1            CrossEntropy
    │                  ReLU                vs. the real y
    │                  AvgPool
    │                  Linear
    │
[Block 2] ──► x_2 ──► [head_2] ──► ŷ_2 ──► L_2(ŷ_2, y)
    │
[Block 3] ──► x_3 ──► [head_3] ──► ŷ_3 ──► L_3(ŷ_3, y)
    │
   ...
    │
[Block K] ──► x_K ──► [head_K] ──► ŷ_K ──► L_K(ŷ_K, y)
```

Each local head is deliberately tiny — together they add only about **~1% of the backbone's parameters.** They exist only to give each block a local supervised signal; they are discarded (or only the last one is kept) at inference.

---

## Per-block local loss

Each block's head turns its block output $x_k$ into a class prediction and scores it against the **same ground-truth label** $y$:

**Prediction:**
$$\hat{y}_k = \text{Linear}\bigl(\text{AvgPool}\bigl(\text{ReLU}\bigl(\text{Conv}_{1\times1}(x_k)\bigr)\bigr)\bigr)$$

**Local loss:**
$$L_k = \text{CrossEntropy}(\hat{y}_k, y) = -\log(p_y), \qquad p_y = \frac{e^{z_y}}{\sum_j e^{z_j}}$$

where $p_y$ is the softmax probability the head assigns to the true class and $z_j$ are its logits.

A key simplicity: **there is one label $y$, broadcast to every block from the start.** There is no $y_1, y_2, \dots$ — every block is asked to predict the *same* final target from its own depth. The local heads differ only in how much of the network they sit on top of.

---

## The gradient SGR actually needs

After computing $L_k$, you backpropagate **only through head $k$ and block $k$** — never into block $k-1$ — to get the boundary gradient:

$$\delta_k \;=\; \frac{\partial L_k}{\partial x_{k-1}} \;=\; \underbrace{\frac{\partial L_k}{\partial x_k}}_{\text{back through head } k}\;\cdot\;\underbrace{\frac{\partial x_k}{\partial x_{k-1}}}_{\text{back through block } k}$$

This backward pass stops at $x_{k-1}$. It produces one tensor the size of the boundary activation $x_{k-1}$, which is all that block $k$ contributes to the reconciliation at that boundary. Nothing crosses into block $k-1$'s weights.

The shallower block contributes the *other* gradient at the same boundary — how its **own** local head wants its output $x_{k-1}$ to move:

$$g_{k-1} \;=\; \frac{\partial L_{k-1}}{\partial x_{k-1}} \;=\; \text{back through head } (k-1) \text{ only}$$

(since $x_{k-1}$ is the *output* of block $k-1$, the head sits directly on it — no block backward is needed). This $g_{k-1}$ is computed when block $k-1$ is processed and **stored** for use one step later.

---

## The SGR regularizer

At boundary $x_{k-1}$ you now have both gradients: $\delta_k$ (what the deeper block wants) and $g_{k-1}$ (what the shallower block wants). SGR penalizes their disagreement directly — it is a squared $L_2$ distance between the two boundary gradients:

$$\mathcal{L}_k^{\text{SGR}} \;=\; \bigl\|\,\delta_k - g_{k-1}\,\bigr\|_2^2 \;=\; \left\|\,\frac{\partial L_k}{\partial x_{k-1}} - \frac{\partial L_{k-1}}{\partial x_{k-1}}\,\right\|_2^2$$

This is exactly $\|\boldsymbol{\epsilon}\|^2$ — the quantity the convergence bound told us to keep small. Minimizing it shrinks the additive error floor in the bound, restoring convergence of the final-block loss.

The total objective for block $k$ adds the reconciliation term to its local loss, weighted by $\lambda$:

$$\mathcal{L}_k^{\text{total}} \;=\; L_k \;+\; \lambda\cdot\mathcal{L}_k^{\text{SGR}}$$

The first block has nothing behind it to reconcile with, so it carries no SGR term:

$$\mathcal{L}_1^{\text{total}} \;=\; L_1$$

Each block updates its weights against its own $\mathcal{L}_k^{\text{total}}$ only — the reconciliation is a *local* penalty computed from one stored tensor, not a backward pass through the rest of the network.

---

## Training loop (one iteration, concrete)

```
receive (x_0, y) from the batch

── Block 1 ──────────────────────────────────────────
forward:   x_1 = block_1(x_0)
           ŷ_1 = head_1(x_1)
           L_1 = CrossEntropy(ŷ_1, y)
backward:  g_1 = ∂L_1/∂x_1        (through head_1 only)
update:    W_1 ← W_1 − η·∂L_1/∂W_1
store:     g_1                    (the shallow-side gradient at boundary x_1)
detach:    x_1                    (cut the gradient chain into block 1)

── Block 2 ──────────────────────────────────────────
forward:   x_2 = block_2(x_1.detach())
           ŷ_2 = head_2(x_2)
           L_2 = CrossEntropy(ŷ_2, y)
backward:  δ_2 = ∂L_2/∂x_1        (through head_2 + block_2, stop at x_1)
SGR:       L_SGR = ‖δ_2 − g_1‖²   (reconcile the two gradients at boundary x_1)
update:    W_2 ← W_2 − η·∂(L_2 + λ·L_SGR)/∂W_2
store:     g_2 = ∂L_2/∂x_2        (shallow-side gradient at the NEXT boundary)
detach:    x_2

── Block k ──────────────────────────────────────────
forward:   x_k = block_k(x_{k-1}.detach())
           L_k = CrossEntropy(head_k(x_k), y)
backward:  δ_k = ∂L_k/∂x_{k-1}    (through head_k + block_k)
SGR:       L_SGR = ‖δ_k − g_{k-1}‖²
update:    W_k ← W_k − η·∂(L_k + λ·L_SGR)/∂W_k
store:     g_k = ∂L_k/∂x_k        (for boundary with block k+1)
detach:    x_k
... identical for every block
```

The bookkeeping is: at boundary $x_{k-1}$ you reconcile the deeper block's *input* gradient $\delta_k=\partial L_k/\partial x_{k-1}$ against the shallower block's *output* gradient $g_{k-1}=\partial L_{k-1}/\partial x_{k-1}$, which was stored one step earlier. Both are evaluated at the same boundary variable $x_{k-1}$, so the subtraction is well-defined.

---

## Memory cost — where the >40% saving comes from

```
Global backprop:
  must keep EVERY block's activation alive, waiting for the
  single global backward pass.
        memory  =  O( L × batch × feature_size )

SGR (local):
  keep only:
    • the activations of the block currently being updated
      (freed immediately after its update), and
    • one stored boundary gradient g_{k-1}, a single tensor
      the size of one activation.
        memory  =  O( batch × feature_size )
```

Global backprop's memory grows with depth $L$ because nothing can be freed until the backward pass reaches it. SGR frees each block's activations the instant that block is updated and carries forward only one boundary-sized tensor. That is the structural reason for the **>40% activation-memory reduction** in the benchmark — and it is independent of the accuracy result; the accuracy is what SGR's reconciliation defends while the memory drops.

---

## What SGR does *not* require

- **No global loss wire.** There is no single end-to-end loss broadcast through the whole network.
- **No gradient across block boundaries.** The chain is cut with `detach` at every boundary.
- **No extra learnable parameters** beyond the tiny ~1% local heads (and the heads are not part of the reconciliation mechanism itself — they only produce the local losses).
- **No backward pass between blocks.** The only thing that travels between blocks is $g_{k-1}$, a single stored tensor the size of one boundary activation. Cheap to keep, cheap to move.

The whole mechanism is: *one extra stored tensor per boundary, one extra squared-distance term per block.* That is the entire cost of turning a stack of myopic local learners into something that tracks end-to-end training.

---

## How SGR relates to the broader local-learning landscape

SGR sits among other "learn without a global backward pass" methods, but attacks the coordination problem differently:

- **Plain greedy/local learning** (e.g. layer-wise local losses, "Local Learning" / decoupled greedy learning): each block is myopic; this is the baseline SGR repairs.
- **Forward-Forward family** (FF, SCFF, CFF): removes the backward pass *entirely* by using a per-layer goodness scalar instead of a gradient. Coordination, where it exists (CFF), is carried by a scalar goodness signal — much coarser than SGR's full boundary-gradient tensor.
- **Target propagation**: sends a *target activation* down instead of a gradient; each layer moves its output toward the target. SGR instead keeps the local-loss gradients and reconciles them at the boundary.
- **SGR's niche**: it stays inside the "each block has a real supervised local loss and a real local gradient" regime, and adds the cheapest possible fix — a boundary-gradient matching penalty — backed by an explicit convergence bound that names exactly which quantity ($\|\boldsymbol{\epsilon}\|$) must be controlled.

---

## Trade-offs (summary)

```
SGR (Gradient Reconciliation for local learning):
  ✅ no global backward pass — gradient never crosses a block boundary
  ✅ no weight transport, no global loss wire
  ✅ >40% activation-memory saving vs end-to-end backprop
  ✅ backbone unchanged; only ~1% extra params (tiny local heads)
  ✅ blocks updatable independently (parallelizable in principle)
  ✅ explicit convergence bound — names ‖ε‖ as the quantity to control
  ✅ matches BP within <1–1.5% at K=2–3 on CIFAR-10 / ImageNet
  ❌ needs labels at every block (supervised local losses, same y broadcast)
  ❌ one extra stored boundary tensor + one squared-distance term per block
  ❌ residual mismatch remains — small accuracy gap that grows with K
  ❌ λ is a tuning knob; too small = no reconciliation, too large = swamps L_k
```
