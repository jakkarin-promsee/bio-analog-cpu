# 17 — Durability: the theory of computing reliably under noise

> Your instinct: residual layers each "reduce the input as much as they can" so error doesn't chain and **var(x) doesn't stack across layers.** That instinct is a real, deep theory — and it generalizes into a full toolkit for **durability**. The single most useful reframe in this file: **on your chip, noise is not only the enemy — trained against, it is *free regularization.*** This is the theory side; `18-analog-noise.md` is the circuit side.

---

## Your "var(x) doesn't stack" instinct = signal propagation theory (edge of chaos)

*Deep Information Propagation: Schoenholz, Gilmer, Ganguli & Sohl-Dickstein, 2016 ([arXiv 1611.01232](https://arxiv.org/abs/1611.01232)); Mean Field Residual Networks: Yang & Schoenholz, 2017.*

You re-derived a beautiful result. Using mean-field theory, this work shows that as a signal propagates through a deep net, its **variance and the correlation between inputs** evolve layer by layer toward fixed points — and there are **"depth scales"** that bound how far signal (and gradient) can travel. There's a phase transition: the **ordered phase** kills signal (vanishing gradients, everything collapses to one point), the **chaotic phase** explodes it (exploding gradients, tiny differences amplify). Only **at the boundary — "the edge of chaos"** — does variance stay stable and arbitrarily deep nets stay trainable. And the follow-up result is exactly your point: **residual networks sit naturally near that critical edge** — the skip connection is what keeps variance from collapsing *or* exploding as depth grows.

**For us:** your "each layer reduces input, var doesn't stack" is the **edge-of-chaos / variance-preservation** condition, and residuals are *why* you're on it. This matters doubly for an analog chip, because **noise is variance**: if your architecture amplifies variance with depth (chaotic phase), it *also* amplifies noise with depth — a 1% device error becomes 10% by layer 5 (the exact compounding draft-5 §15 worried about). Staying near the edge (residuals + normalization + careful gain) means **noise neither vanishes into uselessness nor explodes into garbage** — it stays bounded as it flows. So your durability starts at *initialization and gain*: keep the per-layer variance map near 1.

---

## Lipschitz bounds — the formal definition of "durable"

*Spectral normalization: Miyato et al., 2018 ([arXiv 1802.05957](https://arxiv.org/abs/1802.05957)); Lipschitz robustness, general.*

The exact theorem for durability. A network's **Lipschitz constant** `L` is the worst-case ratio **(change in output) / (change in input)** — if `L = 2`, a noise of size ε can move the output by at most 2ε. *Durability is literally a small Lipschitz constant.* You control it directly: the Lipschitz constant of a linear layer is its **largest singular value (spectral norm)**, so **spectral normalization** (divide each weight matrix by its largest singular value) makes a layer **1-Lipschitz** — output perturbation ≤ input perturbation, guaranteed, layer after layer.

**For us:** this gives a *measurable, enforceable* durability target. A composition of 1-Lipschitz layers is 1-Lipschitz overall — so **bounded per-layer gain = bounded noise amplification end-to-end** (the formal version of "var doesn't stack"). On analog, the largest-singular-value constraint maps to a **gain ceiling per crossbar** — don't let any block multiply its input (or its noise) up. Pair this with your physical saturation (a hard gain ceiling at the rail, draft-5 §22 #14) and you have Lipschitz control *in physics*.

---

## The big reframe: noise injection *is* regularization (Bishop's theorem)

*Bishop, 1995, "Training with Noise is Equivalent to Tikhonov Regularization," Neural Computation 7(1) ([paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bishop-tikhonov-nc-95.pdf)).*

**This is the most important idea in the file for you, because it flips noise from liability to asset.** Bishop proved that **training with small added noise is mathematically equivalent to Tikhonov regularization** — i.e., adding noise during training *is the same as* adding a penalty that punishes large weights and forces the network's mapping to be **smooth** (low Lipschitz!). So noise during training doesn't just survive — it **improves generalization and durability**, by pushing the model toward solutions that don't care about small perturbations.

**For us — this is the punchline of your whole "fix it in software, keep hardware clean and fast" idea from before.** Your analog substrate *produces noise for free.* Bishop says that free noise, *if you train with it*, is **free Tikhonov regularization** — the chip's imperfection becomes the chip's regularizer. You don't fight the noise; you **train in its presence so the weights become smooth and insensitive to it.** The thing every analog designer curses is, for a *learning* chip, a built-in generalization bonus. This is the bridge to `18`'s noise-aware training.

---

## Randomized smoothing — noise + voting = *certified* durability

*Cohen, Rosenfeld & Kolter, 2019 ([arXiv 1902.02918](https://arxiv.org/abs/1902.02918)).*

The provable version. Take any classifier that works under Gaussian noise, run it **many times with fresh noise, and take the majority vote** — the resulting "smoothed" classifier is **provably robust**: its prediction is *guaranteed* not to change within a certified radius around the input. It's the only certified defense that scales to ImageNet.

**For us:** this says **noise + redundancy + voting → a mathematical robustness guarantee**, not just empirical. On your chip, "run many times with fresh noise and vote" is *natural* — your noisy analog forward passes already differ run-to-run, and a vote/average over a few of them (or over redundant copies) gives certified stability. It's also the exact bridge to the deepest theorem below.

---

## The deepest theorem — reliable computation from unreliable parts (von Neumann, 1956)

*von Neumann, "Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components," 1952 lectures / 1956 ([paper](https://www.peliti.org/Notes/vonNeumannNew.pdf)).*

The foundational result, and it was written *about your exact problem.* Von Neumann asked: can you build a **reliable** computer out of **unreliable** components (he was explicitly modeling **neurons** translating perception into action)? Answer: **yes — by redundancy.** Feed the same input to many noisy copies and take a **majority vote** ("multiplexing"); interleave **"restoring organs"** that periodically clean up accumulated error. With enough redundancy, the *system* is reliable even though every *part* is not — error correction outruns error accumulation.

**For us — this is the theorem your entire project is an instance of.** A brain (and your chip) computes reliably with noisy analog neurons *because* of redundancy and restoration, not despite the noise. It tells you durability is not only "make each part quiet" but "make the *system* self-correcting": **redundant Scaps + a periodic restoring step** (your sleep/consolidation is a restoring organ; your dummy/reference cells are restoring organs; an attractor settling step is a restoring organ). Population coding — average `N` noisy units, noise falls as `√N` — is the brain's multiplexing. Build error-*correction* into the architecture, and you can be reliable on parts that aren't.

---

## And recurrence cleans noise for free — attractor error correction

*Hopfield / equilibrium settling (`1-memory.md`, `3-recurrence.md`).*

One more, because it's free on your substrate: a network that **settles to an attractor** (an energy minimum) **pulls noisy states back toward the clean stored pattern** — the settling *is* error correction. A perturbed input rolls back down to the nearest valid attractor. Your phase-2 equilibrium loop (`3`) and your associative memory (`1`) both do this inherently.

**For us:** the same physical relaxation that does your *thinking* also does your *noise cleanup* — every settle is a "restoring organ" in von Neumann's sense. Durability isn't a separate subsystem; it's a property of building the computation as a settling dynamical system.

---

## The shape of the answer (this file)

Durability is layered. **(1) Keep variance stable** — your residual/var-doesn't-stack instinct is the **edge-of-chaos** condition; stay near criticality so noise neither vanishes nor explodes with depth. **(2) Bound the gain** — small **Lipschitz constant** (spectral norm / your saturation ceiling) means bounded noise amplification, provably. **(3) Train *with* the noise** — Bishop's theorem says injected noise = **Tikhonov regularization**, so your free analog noise becomes free smoothness/robustness (the "fix in software, keep hardware clean" idea, vindicated). **(4) Add redundancy + restoration** — **von Neumann**: reliable computation from unreliable parts via majority/voting (randomized smoothing = the certified modern form) and periodic restoring organs (sleep, dummy cells, attractor settling). You already had the residual layer (1); this file adds the other three. `18-analog-noise.md` grounds it in the actual circuit, including the temperature problem.
