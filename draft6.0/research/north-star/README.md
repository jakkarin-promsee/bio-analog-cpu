# `north-star/` — the north-star research dossier

> **What this is.** The north star — *beyond* the numbered phases (all ten numbered phases are done — the neocortex brain is built, characterized, and validated: verdict S14) — is a recurrent, lifelong-learning **thinking brain**: a prefrontal↔hippocampus loop where *correctness is a self-generated feeling*. It is **deliberately not specced** ("simple intelligence first"; see `docs/essence/the-essence2.md`). This folder is the **map of the territory** for when we get there — every popular/trustable paper worth knowing, told as a story, with a **"For us"** line on each. Both the **ideas side** (theory, neuroscience, frames) and the **apply side** (concrete buildable methods).
>
> Nothing here is a decision. It's the menu, not the order. Read for orientation; argue with it.

---

## How this maps to your questions

You asked five things. Here's which file answers each:

| Your question | File | The short answer (argued in the file) |
| --- | --- | --- |
| "What should the **hippocampus** look like?" | [`1-memory.md`](1-memory.md) | An **associative / retrieval memory** — your LUT prototype store, grown up. Content-addressable recall = attention = modern Hopfield. |
| "What should the **prefrontal cortex** look like? Which model?" | [`2-controller.md`](2-controller.md) | A **bandwidth-limited workspace + gating** that holds a little and queries the rest. Not one big net — a *coordinator* of modules. |
| "Should it be a **full LSTM**? How recurrent?" | [`3-recurrence.md`](3-recurrence.md) | **No, not LSTM-as-core.** The "think many times until it settles" is **equilibrium / fixed-point** computation + a **learned halt** — both analog-native. |
| "How do they **communicate**?" | [`2-controller.md`](2-controller.md) + [`6-architectures.md`](6-architectures.md) | A **shared workspace broadcast** + **attention-based read/write**. Limited bandwidth is a *feature* (forces specialization). |
| "Is **2 brains enough**? Should we get more?" | [`6-architectures.md`](6-architectures.md) | **Probably not two — think ~4–6 roles.** Every serious cognitive-architecture proposal (LeCun, Thousand-Brains, SOAR) has more. But add roles only when a failure demands one. |
| "Input with **few labels that doesn't lie to itself**?" | [`7-encoding.md`](7-encoding.md) | Predict in **representation space, not raw input** (so it can't memorize noise); add an explicit **variance floor + decorrelation** to stop collapse. Both are local capacitor statistics. |
| "What should the **atom** (Ganglion / ALU) be?" | [`8-atom.md`](8-atom.md) | For time-series, a **continuous-time atom** (liquid neuron = an RC element with a learnable time-constant). Your physics *is* the math. |
| "How do others build the **hierarchy**?" | [`9-hierarchy.md`](9-hierarchy.md) | Not a fixed stack — a **bidirectional predict-down / error-up loop** with **dynamic agreement** and **time**. That's what draft-5's skeleton lacked. |
| "**Fast / realtime** forward + learning?" | [`10-realtime.md`](10-realtime.md) | Drop BPTT. Use **local forward traces × a broadcast signal** (e-prop) — the eligibility trace is a leaky cap you already have. |
| "Each block sees only a **slice** of input — efficient? breaks GD? the **ALU wall**?" | [`11-connectivity.md`](11-connectivity.md) + [`12-dataflow.md`](12-dataflow.md) | **Efficient (g× cheaper), doesn't break GD (makes credit *local*), and there's a better mix.** Your scheme = grouped/depthwise-separable conv; mix via shuffle/butterfly (log-depth), not a dense clip. |
| "A **compression** that makes in-chip computation possible?" | [`13-compression.md`](13-compression.md) + [`14-compression-methods.md`](14-compression-methods.md) | **You don't bolt on a compressor — learning *is* compression (MDL).** Build the net out of compressive *structure* (sparse + low-rank + shared + superposed); it's born small. Your spare-capacity hypothesis = superposition + lottery ticket, confirmed. |
| "Does **convolution** work on SCFF? Use it? How often?" | [`15-convolution.md`](15-convolution.md) | **Yes — *cleaner* unsupervised — but only where data has spatial/translation structure** (images yes, tabular no). Conv front-end **paired with a channel-mix**. Your Ganglion 'collapse' = a 1×1 conv; keep it. |
| "A **retina + predict-the-image** front-end?" | [`16-vision.md`](16-vision.md) | **Right far-future direction** — but predict the *representation* of the future, not the pixels (or it models noise & lies). It's the phase-2 loop with a camera on it. |
| "Increase **durability** / handle **analog (temperature) noise**?" | [`17-durability.md`](17-durability.md) + [`18-analog-noise.md`](18-analog-noise.md) | **Match the fix to the noise's timescale:** *subtract* slow drift (differential / auto-zero — your draft-5 already has it), *average* fast kT/C (bigger caps + redundancy). And **train *with* the noise** (Bishop: noise = free regularization). Your residual var-control = edge-of-chaos. |
| "Will it even **converge / generalize / settle** — and *why*?" | [`19-optimization.md`](19-optimization.md) + [`20-dynamics.md`](20-dynamics.md) | **Yes, with reasons:** wide nets provably converge (NTK); the only obstacle is saddles, not bad minima (noise escapes them); **flat minima generalize *and* resist noise** (one target); contracting dynamics provably settle. |
| "Is there **one principle** under all of this?" | [`21-energy.md`](21-energy.md) | **Energy.** Inference = roll downhill; learning = carve the valleys. SCFF / memory / recurrence / the-feeling / stability are *all* energy descent — and your analog chip runs it *physically*. Landauer: settle-don't-erase **is** the cheap path. |

And the deepest thread — **"correctness is a feeling"** — runs through [`4-signal.md`](4-signal.md) (the self-generated learning/halting signal) and [`5-continual.md`](5-continual.md) (how to never freeze without rotting).

---

## The files — two layers

The dossier sits at **six layers (A–F) plus two cross-cutting files.** Files **1–6** (A) are the **cognitive system** (the north-star thinking brain). Files **7–10** (B) are the **substrate layer** (the *atom*, *encoding*, *composition*, *realtime*). Files **11–12** (C) are the **physical-organization layer** (connectivity and the ALU/dataflow wall). Files **13–14** (D) are the **compression layer** (why a model fits on-chip). Files **15–16** are **cross-cutting / far-future** (convolution; the vision front-end). Files **17–18** (E) are **durability** (surviving noise). Files **19–21** (F) are the **foundations** (why it converges, settles, and works at all — the floor under everything). Layers B–F **bite the current draft-6.0 build now**, not just the north star.

**Layer A — the cognitive system (phase 2):**

1. **[`1-memory.md`](1-memory.md) — the hippocampus / long-term store.** CLS theory, Neural Turing Machine, Differentiable Neural Computer, Memory Networks, Modern Hopfield, retrieval (kNN-LM / RETRO), Fast Weights.
2. **[`2-controller.md`](2-controller.md) — the prefrontal / working memory / coordinator.** Global Workspace Theory, Shared Global Workspace (Bengio), Recurrent Independent Mechanisms, the Consciousness Prior, PBWM gating.
3. **[`3-recurrence.md`](3-recurrence.md) — the loop / "think until it settles."** Deep Equilibrium Models, Equilibrium Propagation, predictive coding, Adaptive Computation Time / PonderNet, Universal Transformer, LSTM/GRU (and why not).
4. **[`4-signal.md`](4-signal.md) — the learning signal / "correctness as a feeling."** Free Energy / Active Inference, curiosity & compression-progress, World Models, the learned critic.
5. **[`5-continual.md`](5-continual.md) — never freeze / lifelong.** Elastic Weight Consolidation, Synaptic Intelligence, Deep Generative Replay, Progressive Networks, the stability-plasticity dilemma.
6. **[`6-architectures.md`](6-architectures.md) — the whole mind / "is 2 brains enough?"** LeCun's H-JEPA path, System 1/System 2, Thousand Brains, SOAR & ACT-R.

**Layer B — the substrate (bites the current build too):**

7. **[`7-encoding.md`](7-encoding.md) — input/output shape & "don't lie to itself."** VICReg, Barlow Twins, MAE vs I-JEPA, sparse coding / SDR, VQ-VAE, Information Bottleneck. *(collapse + shortcut-learning are the two ways a model lies.)*
8. **[`8-atom.md`](8-atom.md) — the atom / the Ganglion & ALU.** Kolmogorov-Arnold Networks, **Liquid Time-Constant Networks**, Neural ODEs, Capsules, dendritic computation, reservoir computing. *(the substrate-matched atoms are continuous-time.)*
9. **[`9-hierarchy.md`](9-hierarchy.md) — composition / the brain hierarchy.** Hierarchical predictive coding, GLOM, HTM, Slot Attention, Mixture-of-Experts, greedy layer-wise growth. *(your draft-5 skeleton + the top-down loop, dynamic agreement, and time it was missing.)*
10. **[`10-realtime.md`](10-realtime.md) — fast & realtime forward + learning.** RTRL, **e-prop**, reservoir computing, liquid networks, spiking/neuromorphic, State-Space Models / Mamba. *(drop BPTT; local trace × broadcast signal = online learning.)*

**Layer C — physical organization / the ALU wall (your draft-5 territory):**

11. **[`11-connectivity.md`](11-connectivity.md) — local input + mixing.** Grouped/depthwise-separable convolution (**= your Ganglion + translate clip**), channel shuffle, butterfly/Monarch matrices, Mixture-of-Experts, MLP-Mixer. *(your scheme is MobileNet's core trick; the cheaper mix is log-depth/permutation, not dense.)*
12. **[`12-dataflow.md`](12-dataflow.md) — the ALU wall / spatial vs temporal.** The memory wall, the spatial-vs-temporal tradeoff, analog crossbar MVM, systolic arrays. *(your static-wire Ganglion = spatial dataflow; keep crossbars small via grouping.)*

**Layer D — compression / fitting on-chip (the core enabling topic):**

13. **[`13-compression.md`](13-compression.md) — learning *is* compression + your spare-capacity hypothesis.** MDL / learning-is-compression, double descent, intrinsic dimension, Lottery Ticket, **superposition**. *(your "task-cap / slack shared across tasks" = superposition + lottery ticket, confirmed; sparsity is the precondition.)*
14. **[`14-compression-methods.md`](14-compression-methods.md) — how to actually compress + your two mechanisms.** Pruning / Deep Compression, knowledge distillation, low-rank / LoRA, weight-sharing / hashing, **DenseNet** (= your Mechanism A), the supervised anchor (= your Mechanism B). *(never build a dense crossbar — build a structured one; born compressed, not squeezed.)*

**Cross-cutting & far-future:**

15. **[`15-convolution.md`](15-convolution.md) — convolution + SCFF (tier-1).** Conv-FF/SCFF (cleaner *unsupervised*), weight-sharing as the ultimate compression, when/how-often to use conv, and your Ganglion's linear-projection collapse (= a 1×1 pointwise conv — **keep it**, reframed as the channel-mix).
16. **[`16-vision.md`](16-vision.md) — retina / vision front-end (far-future).** Predictive vision, the *predict-the-representation-not-the-pixels* rule, developmental/curriculum learning. *(the vision front-end is the phase-2 loop with a camera on it.)*

**Layer E — durability / surviving noise:**

17. **[`17-durability.md`](17-durability.md) — the theory of computing reliably under noise.** Signal/variance propagation (edge of chaos = your residual insight), Lipschitz bounds, **noise-injection = Tikhonov regularization** (free robustness), randomized smoothing, **von Neumann** reliable-from-unreliable. *(noise, trained against, is free regularization.)*
18. **[`18-analog-noise.md`](18-analog-noise.md) — analog noise & the temperature problem.** The noise taxonomy by timescale, slow-drift cancellation (differential / chopper / auto-zero / dummy — **= your draft-5 §15**), kT/C cap-sizing & averaging, noise-aware training. *(slow noise you subtract; fast noise you average.)*

**Layer F — the foundations (why it works at all):**

19. **[`19-optimization.md`](19-optimization.md) — why learning converges & generalizes.** NTK (wide → convergent), saddle points (not bad minima), **flat minima = generalization = noise-robustness**, implicit regularization of SGD, No Free Lunch. *(over-provision freely; noise finds flat minima; own your inductive bias.)*
20. **[`20-dynamics.md`](20-dynamics.md) — will your analog system settle?** Computation as a dynamical system, Lyapunov stability, contraction theory, edge of chaos, attractors-as-computation. *(make the dynamics contracting near the edge → settling + durability + memory at once.)*
21. **[`21-energy.md`](21-energy.md) — the energy view (the capstone).** Energy-based learning unifies SCFF / Hopfield / EqProp / predictive-coding / the-feeling / stability; + Landauer's thermodynamic floor. *(your chip is an energy-shaping machine that computes by descending landscapes it never erases.)*

---

## If you read only five things

1. **Complementary Learning Systems** (`1-memory.md`) — the *proof* that a fast sparse memory + a slow general one is the right split. You already half-built it (sleep + LUT).
2. **Shared Global Workspace** (`2-controller.md`) — the buildable answer to "how do the parts talk."
3. **Deep Equilibrium Models** (`3-recurrence.md`) — the apply-side of "settle to a fixed point," and it's analog-native.
4. **Active Inference / Free Energy** (`4-signal.md`) — the master frame for "correctness is a feeling" *and* for self-verification (act to reduce your own uncertainty).
5. **LeCun's "A Path Towards Autonomous Machine Intelligence"** (`6-architectures.md`) — the most complete published answer to "how many brains, and which ones."

---

## One synthesis, before you dive in

The papers converge on a picture that matches your intuition uncannily well, and it is **not** "a bigger LSTM":

- **Memory is associative and addressable, kept *outside* the fast compute** (CLS, NTM/DNC, Hopfield). Your hippocampus LUT is the seed; "attention" is just similarity-based recall over it.
- **Thinking is iterative settling, not one feed-forward pass** (DEQ, predictive coding, equilibrium prop) — which analog hardware does *for free*, and which LSTM/transformer both miss.
- **The controller is small and bandwidth-limited on purpose** (global workspace) — it holds little, queries memory, broadcasts a summary. Scarcity forces the parts to specialize.
- **The learning/stop signal is self-generated and grounded** (active inference, curiosity) — exactly "correctness is a feeling," and it must stay tethered to prediction-error or it collapses.
- **A mind is several roles, not two** (LeCun, Thousand Brains) — but you grow into them; you do not start there.

The honest meta-point: phase 2 is a **cognitive architecture** problem, and the field has *many* sketched answers and *zero* finished ones. So this folder is a compass, not a blueprint. Pick the smallest loop that thinks, ground it, and let the failures name the next module — your own method, aimed at the biggest target.
