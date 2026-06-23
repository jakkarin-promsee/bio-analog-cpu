# 13 — Learning *is* compression (and your "spare-capacity" hypothesis is real)

> Your central thesis: an **in-chip compression** that makes resident-weight computation possible — and your intuition that *each neuron has a task-cap it doesn't fully use, and the slack can be shared.* This file is the theory side, and the headline is the deepest unification in the whole dossier: **learning is not *helped by* compression — learning *is* compression.** Which means "make it fit on-chip" and "make it learn well" are **the same problem**, not two. And your spare-capacity hypothesis has three names in the literature, all confirming it.

---

## The frame: a model that generalizes is a model that compressed the data

*Minimum Description Length: Rissanen, 1978; for neural nets: Hinton & van Camp, 1993 ([paper](https://www.cs.toronto.edu/~hinton/absps/colt93.pdf)); Kolmogorov complexity; Schmidhuber's compression-progress (`4-signal.md`).*

The principle that ties everything together. **MDL** says the best model of a dataset is the one that **minimizes the total bits = description-length(model) + description-length(data given the model).** A model that memorizes is huge (no compression); a model that found the *real structure* is small (the structure *is* the compression). Hinton & van Camp's exact result: **a network generalizes well precisely when there is far less information in its weights than in the outputs it explains.** Generalization = the weights are a *compressed* description of the regularity in the data.

**For us — this is the unifying insight you were reaching for.** You said "we need a compression algorithm to fit on-chip; now we only do it in software." MDL says you **don't need a separate compression algorithm bolted on** — you need a *learning rule that compresses as it learns*. A network that learns the real shape (not the noise) is *already* small enough to be the compressed form. So your resident-weight constraint (fit on-chip) and your learning goal (find the real shape) are **one objective**: minimize the description length of the weights. Every method in `14-compression-methods.md` is a way to *enforce* that; this file is *why* it's possible.

---

## Your double-descent intuition, grounded — "noise refutes itself"

*Double descent: Belkin et al., 2019, PNAS ([arXiv 1812.11118](https://arxiv.org/abs/1812.11118)).*

You proved double descent yourself, and described it as: *the model converges to the real data shape, leaving only noise; then the noise refutes itself, leaving the real shape.* The literature's version: as you grow a model past the **interpolation threshold** (where it can fit the training data exactly), test error first *peaks* (classical overfitting) and then **descends again** — over-parameterized models that interpolate *still generalize.* Why? Among all the ways to fit the data exactly, gradient descent finds the **smoothest / lowest-norm** one — which is the **most compressible** one. The noise, being incompressible, gets spread thin and **averaged toward zero**; the real structure, being compressible, dominates.

**For us:** your phrasing is the *compression reading* of double descent, and it's correct. "Noise refutes itself" = the incompressible part cancels because the model is biased toward the compressible solution. This matters for your chip because it says **over-provisioning capacity is safe and even helpful** — extra Scaps don't cause overfitting if the learning rule prefers the compressible (low-norm/smooth) fit. Your analog substrate's natural smoothing (saturation, leak, noise) *is* such a bias. You don't fear extra capacity; you exploit it.

---

## Why compression is even possible: the task is *tiny*

*Intrinsic dimension: Li et al., ICLR 2018 ([arXiv 1804.08838](https://arxiv.org/abs/1804.08838)).*

The measurement that makes "fit on-chip" believable. Train a network **inside a random low-dimensional subspace** and slowly raise the dimension until solutions appear — that dimension is the task's **intrinsic dimension**. The finding: it's *shockingly small.* A task that needs millions of parameters in the native space often has an intrinsic dimension in the **hundreds to low thousands** (MNIST ≈ 750). The million parameters are mostly *redundant coordinates*; the actual problem lives in a tiny subspace. The paper notes this directly gives an **MDL upper bound** and compresses networks **100×+**.

**For us:** this is *the* permission slip for resident-weight. The reason a whole model can fit on a chip is that **the task it solves is far smaller than its parameter count suggests** — you're storing a low-dimensional thing in a high-dimensional substrate, and the redundancy is compressible. Your job isn't to cram a million independent weights onto silicon; it's to represent a ~thousand-dimensional thing efficiently. That reframes the whole engineering problem from "impossible storage" to "find the small subspace," which is what structured/low-rank/sparse methods (`14`) do.

---

## Your hypothesis, named (1): spare capacity is real — the Lottery Ticket

*Frankle & Carbin, ICLR 2019 ([arXiv 1803.03635](https://arxiv.org/abs/1803.03635)).*

Your words: *"some neurons in each layer aren't used 100%; there's spare space."* The **Lottery Ticket Hypothesis**: a dense network contains a small **"winning" subnetwork** (often **<10–20%** of the weights) that, trained alone from the same init, matches the full network's accuracy. The other 80–90% is **slack** — it helped *find* the solution but isn't needed to *represent* it.

**For us:** you re-derived this exactly. The lesson for your chip: **most of the capacity is overhead for *learning*, not for *running*.** This suggests a two-phase story that fits your sleep/consolidation: learn *over-provisioned* (use the slack to find the solution — double descent says this is safe), then **consolidate to the winning ticket** (free the slack for the next task). Your "spare space shareable to future tasks" is the lottery-ticket slack, reused — which is continual learning (`5-continual.md`) meeting compression.

---

## Your hypothesis, named (2): capacity is shared by *superposition* — the deep one

*Anthropic, "Toy Models of Superposition," Elhage et al., 2022 ([arXiv 2209.10652](https://arxiv.org/abs/2209.10652)).*

This is the closest match to your intuition in the entire dossier, so read it twice. You said: *each neuron is used **less than it can be** — not dead, just under-allocated — and that capacity can be **shared**.* **Superposition** is exactly this, made rigorous: when features are **sparse** (only a few active at once), a network represents **more features than it has neurons** by storing them as **almost-orthogonal directions** that *share* the same neurons. A neuron isn't one feature or dead — it carries a *blend* of several features, and as long as they rarely co-activate, they don't interfere. The network packs `k` features into `n < k` neurons by exploiting sparsity, organizing them into clean geometric structures (pentagons, tetrahedra).

**For us — this is your "task-cap, allocated by learning, slack shareable," formalized.** Superposition says the slack is filled by **sharing**: a neuron's spare capacity holds *other* features in near-orthogonal superposition. The condition is **sparsity** — which is your committed substrate property *and* the thing that makes it work. So your hypothesis isn't just plausible; it's a known, studied phenomenon, and your chip's sparseness is the exact precondition for it. The design implication: **don't try to make each Scap monosemantic (one job).** Let them carry superposed features under sparsity — that's how you fit `k` capabilities into `n < k` analog elements. Your compression *is* superposition, and superposition *needs* your sparsity.

---

## The shape of the answer (this file)

The theory you were reaching for: **learning is compression** (MDL) — so "fit on-chip" and "learn the real shape" are **one objective**, not two; you need a *compressive learning rule*, not a separate compressor. It works because the **task is tiny** (intrinsic dimension ≪ parameter count) — you're storing a low-dimensional thing in a big substrate. Your **double-descent** read is right: over-capacity is safe because the learner prefers the *compressible* fit and the noise cancels — so don't fear extra Scaps. And your spare-capacity hypothesis is three confirmed things at once: the slack is real (**Lottery Ticket**, 80–90% is overhead-for-learning), the task is small (**intrinsic dimension**), and the slack is shared by packing near-orthogonal features under sparsity (**superposition**) — *which your sparse substrate is the precondition for.* You didn't guess; you re-derived the field's compression view of learning. `14-compression-methods.md` is how to *build* it.
