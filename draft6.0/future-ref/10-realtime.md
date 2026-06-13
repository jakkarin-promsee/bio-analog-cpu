# 10 — Fast & realtime forward + learning (online, streaming, low-latency)

> Your words: *"the forward and learning that can be fast and realtime."* This is the hardest systems requirement in the whole project, because standard deep learning is the *opposite* of realtime: it learns from **whole batches**, by a **backward pass over a stored history**. A chip that learns *while it runs, per sample, now* needs a different family of methods. The good news: that family exists, it's biologically motivated, and your substrate is built for it.

---

## The problem: why normal training isn't realtime

Backprop-through-time (BPTT) — how RNNs/transformers learn sequences — **stores the entire input history**, then sweeps **backward** through it to compute gradients. That's three deal-breakers for realtime: it needs the **future** before it can learn from the **present** (non-causal), it needs **memory of the whole sequence**, and it learns in **offline batches**. A realtime chip can't do any of that. Every method below drops the backward-over-history requirement.

---

## Real-Time Recurrent Learning (RTRL) — exact online gradients, forward-only

*Williams & Zipser, 1989; modern view: [Zucchet & Orvieto, 2023](https://arxiv.org/abs/2305.19044).*

The "correct" answer, and the one that shows why it's hard. RTRL computes the **exact** gradient **online, forward in time**, by carrying an **influence matrix** (how the current state depends on every weight) and updating it each step — so it can learn **after every input**, with **no stored history and no backward pass**. Perfect realtime semantics. The catch: the influence matrix is **huge** — `O(n³)` memory, `O(n⁴)` compute — intractable except for tiny networks *or* with approximations (assume diagonal/sparse connectivity, low-rank influence).

**For us:** RTRL is the *ideal* your chip wants (learn now, forward-only, no history) and the reason everyone approximates it. The key insight for you: it becomes tractable exactly when the network is **sparse/local** — which is your substrate. The next two entries (e-prop, local learning) are the *tractable, biological* approximations of RTRL, and they're what you'd actually build.

---

## e-prop — the realtime learning rule for spiking/recurrent nets

*Bellec, Scherr, Subramoney, Hajek, Salaj, Legenstein & Maass, 2020, Nature Communications ([paper](https://www.nature.com/articles/s41467-020-17236-y)). (Also `../concept/summary.detail.md`.)*

The tractable, on-chip version of RTRL, and **the single most relevant paper in this file.** e-prop factorizes the gradient into two parts that are *both locally available in real time*: an **eligibility trace** (a per-synapse memory of recent pre/post activity, computed **forward**) times a **learning signal** (a top-down "how wrong are we" that can even be a broadcast). The eligibility trace is the "highway into the future" — it holds *what this synapse did* until the learning signal arrives to say *whether it helped*. It approaches BPTT performance **without** storing history or running a backward pass — explicitly designed for **on-chip learning in neuromorphic hardware**.

**For us:** this is **the** template for realtime learning on your substrate. The eligibility trace is a **leaky capacitor per synapse** (you already have momentum/eligibility registers in the Scap!), and the learning signal is your broadcast/feeling. e-prop says: *local forward trace × a global teaching signal = online learning that rivals backprop* — which is almost exactly your draft-6.0 "local SCFF + broadcast GD correction," now with a realtime/temporal justification. If phase 2 must learn on a stream, e-prop is the rule.

---

## Reservoir computing — learning so fast it's just regression

*Echo State Networks / Liquid State Machines (see `8-atom.md`).*

The fastest-learning option, by not learning most of the network. Fix a random recurrent reservoir; train **only a linear readout** — which can be done in **one shot** (linear regression) or online (recursive least squares). Inference is realtime (the reservoir just evolves with the input); learning is trivial.

**For us:** the cheapest realtime path that could possibly work. A fixed analog reservoir + an online-trained readout gives you **realtime inference *and* realtime learning** with essentially no backprop anywhere. It's the "cheat with analog law" extreme: let the messy analog dynamics be the reservoir (mismatch is a *feature*), learn only the thin readout. Strong candidate for a *first* phase-2 prototype before committing to anything heavier.

---

## Liquid networks — realtime inference in continuous time

*Liquid Time-Constant Nets / Closed-form Continuous-time (CfC): Hasani, Lechner, Rus (see `8-atom.md`).*

Covered as an *atom* in `8-atom.md`, but it belongs here too: because liquid neurons are **continuous-time ODEs**, their *inference is inherently realtime* — they process a stream as it arrives, with adaptive time-constants matching the input's timescale, and tiny networks suffice (19 neurons → car control, running live). The later **CfC** variant gives a closed form so you don't even need an ODE solver loop.

**For us:** the realtime *inference* substrate that pairs with e-prop *learning*. Continuous-time atoms + eligibility-trace learning = a chip that perceives and learns from a live stream, both in real time, both analog-native. This pairing (liquid atom + e-prop rule) is, honestly, the most coherent phase-2 realtime story in this whole dossier.

---

## Spiking Neural Networks & neuromorphic hardware — event-driven realtime

*SNN overview; hardware: Intel Loihi, SpiNNaker, IBM TrueNorth.*

The hardware tradition built *for* this. SNNs compute with **sparse, asynchronous spikes** — a neuron does work *only when it fires*, so there's no global clock stepping every unit; computation is **event-driven**, which is naturally low-power and low-latency. Neuromorphic chips (Loihi, SpiNNaker2) run SNNs with **on-chip learning** (often e-prop-style local rules) at tiny energy budgets.

**For us:** this is your nearest neighbor in *intent* (analog/sparse/online learning chip) and your nearest competitor to position against (`../draft5.1-1.md §1.5` did this for the old design — update it for 6.0). The lesson: **event-driven = compute only on change** is the deepest realtime principle, and it's your **sparse** substrate property taken to its limit. You don't have to adopt spikes, but "a unit costs nothing until it's active" is the realtime/energy idea to steal. (e-prop is, not coincidentally, the neuromorphic field's learning rule.)

---

## State-Space Models / Mamba — the modern efficient-sequence option (apply side)

*S4: Gu et al., 2021; Mamba: Gu & Dao, 2023 ([arXiv 2312.00752](https://arxiv.org/abs/2312.00752)).*

The current ML answer to "process long sequences cheaply." SSMs model a sequence as a **continuous linear dynamical system** (`dx/dt = Ax + Bu`) discretized — which gives them a **recurrent form for O(1)-per-step streaming inference** *and* a parallel form for fast training. Mamba adds input-dependent (selective) dynamics and beats transformers on long sequences at **linear** cost.

**For us:** two reasons to know it. (1) The core (`dx/dt = Ax + Bu`) is, again, **a linear analog circuit** — SSMs are "trainable analog filters," and the field is rediscovering that continuous-time linear dynamics are cheap and powerful (the same bet as your substrate). (2) Its **streaming recurrent inference** is the realtime-friendly mode — process each input as it comes, constant memory. If you want a *modern, well-supported* sequence backbone to compare your analog loop against, Mamba is it.

---

## The shape of the answer (this file)

Realtime, for us: **drop BPTT entirely** (it needs the future and the whole history). The realtime-learning family is **local forward traces × a teaching signal** — RTRL is the exact-but-expensive ideal, and **e-prop is its tractable, on-chip form** (eligibility trace = a leaky cap you already have, learning signal = your broadcast/feeling). Pair it with a **continuous-time atom** (liquid neuron, `8-atom.md`) for realtime *inference*, or go even cheaper with a **reservoir** (train only the readout). The deepest principle, from neuromorphic hardware, is **event-driven: a unit costs nothing until it's active** — your *sparse* property as a power/latency strategy. And **state-space models (Mamba)** are the modern proof that **continuous-time linear dynamics** — *literally your substrate* — are the efficient way to do sequences. The whole file converges on one sentence: **your analog chip is already a realtime machine; the missing piece is a realtime *learning rule*, and that rule is e-prop-shaped (local trace × broadcast signal).**
