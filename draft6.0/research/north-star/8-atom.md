# 8 — The atom: what should one compute block be?

> Your words: *"the atom of each block — the ganglion and ganglion ALU."* What is the right smallest learnable unit? The default answer (a neuron = dot-product + fixed nonlinearity) is **one** choice among many, and it may not be the best for an *analog, continuous-time* substrate. This file is the menu of atoms — and two of them (liquid neurons, reservoirs) are *startlingly* close to "an analog circuit, described as a learning primitive."

---

## The default, and why to question it

A standard neuron computes `y = φ(Σ wᵢxᵢ)` — a **dot product** then a **fixed** nonlinearity (ReLU). Your draft-6.0 Scap-crossbar computes exactly this, and your old draft-5 Ganglion was a clever 2-3-3-2 arrangement of them (a "region multiplexer"). It works. But it bakes in choices: the nonlinearity is *fixed*, time is *discrete* (one step = one layer), and all the expressivity lives in the *connections*, not the *unit*. The atoms below each relax one of those assumptions — and the right atom for you is the one whose assumptions match *capacitor physics.*

---

## Kolmogorov–Arnold Networks (KAN) — put the learning in the *activation*, not the weight

*Liu et al., 2024 ([arXiv 2404.19756](https://arxiv.org/abs/2404.19756)).*

A genuinely different atom. An MLP has **fixed nonlinearities on the nodes** and **learnable weights on the edges**. KAN **flips it**: the edges carry **learnable univariate functions** (splines), and there are **no linear weights at all** — every connection *is* a little learned curve. Backed by the Kolmogorov–Arnold theorem (any multivariate function = sums of univariate functions). Result: small KANs match much larger MLPs on function-fitting and are far more **interpretable** (you can *read* the learned curves). Cost: slower to train, spline machinery.

**For us:** this is the most provocative reframe of your atom. *What if the learnable thing isn't the weight, but the shape of the wire's response?* On an analog substrate a "learnable univariate function on an edge" is a **programmable nonlinear transfer element** — and you already have continuous, shapeable analog elements. KAN says expressivity-per-parameter can be higher if you learn *transfer curves* instead of *gains*. Probably not your phase-1 atom, but exactly the kind of "the atom could be richer" idea you asked for — and it fits analog better than digital.

---

## Liquid Time-Constant Networks — the atom is a *continuous-time* neuron

*Hasani, Lechner, Amini, Rus & Grosu, AAAI 2021 ([arXiv 2006.04439](https://arxiv.org/abs/2006.04439)).*

**Read this one closely — it is almost a description of your chip.** A liquid neuron is not a discrete step; it's a **continuous-time dynamical system**: `dx/dt = −x/τ + (inputs)`, where the **time-constant τ itself varies** with the input and state ("liquid"). Its output is computed by an **ODE solver**. The payoff: tiny networks with huge temporal expressivity (the famous result — **19 neurons learned to steer a car**), provably stable and bounded, excellent on time-series.

**For us:** a leaky capacitor *is* `dx/dt = −x/τ + input`. A liquid neuron is **literally an RC element with a state-dependent time constant** — which your substrate builds natively (you already proposed leaky caps with tunable τ for the SCFF read-layers). This is the strongest candidate for the **phase-2 time-series atom**: continuous-time, analog-native, tiny, stable. Where an LSTM forces time into discrete gated steps (`3-recurrence.md`), a liquid neuron *lives in continuous time* — which is what your hardware actually is. If you build a recurrent atom for phase 2, start here. (Caveat: vanishing gradients under BPTT — but you don't train by BPTT; pair with local/online learning from `10-realtime.md`.)

---

## Neural ODEs — the umbrella idea

*Chen, Rubanova, Bettencourt & Duvenaud, NeurIPS 2018 ([arXiv 1806.07366](https://arxiv.org/abs/1806.07366)).*

The frame liquid nets sit inside. Instead of a fixed stack of layers, define the transformation as a **differential equation** `dh/dt = f(h, t)` and let an ODE solver integrate it — "depth" becomes *integration time*, and it's adaptive. Constant-memory training via the adjoint method.

**For us:** the conceptual license for "**let the analog dynamics BE the computation.**" Your chip doesn't execute layers; it *evolves charge over time*. Neural ODEs are the math that says: an analog network settling/evolving in continuous time **is** a deep network, with depth = time. This unifies the atom (liquid neuron) with the recurrence (`3-recurrence.md`'s equilibrium settling) — both are "let the ODE run."

---

## Capsule Networks — the atom as a *vector*, not a scalar

*Sabour, Frosst & Hinton, 2017 ([arXiv 1710.09829](https://arxiv.org/abs/1710.09829)).*

A richer atom. A capsule outputs a **vector** (not a scalar activation): its *length* encodes "is this thing present?" and its *direction* encodes the thing's *properties* (pose, orientation, scale). Capsules in one layer **route** their output to the parent capsule they best agree with ("routing by agreement").

**For us:** mostly ideas-side, but the question it raises is sharp: *should your atom output one number, or a small vector of properties?* A vector atom carries more structure per unit (and "routing by agreement" is a voting/consensus op you can build). Hinton himself moved past capsules to GLOM (`9-hierarchy.md`), so treat this as a *stepping-stone idea*: the atom might be a small typed bundle, not a scalar — relevant if phase-2 thinking needs to pass *structured* things between blocks.

---

## Dendritic computation — one biological neuron is already a 2-layer net

*Poirazi & Mel, 2003; recent: Beniaguev, Segev & London, 2021 ([single neuron ≈ deep net](https://www.cell.com/neuron/fulltext/S0896-6273(21)00501-8)).*

The neuroscience correction to "neuron = dot product." A real neuron's **dendrites** do *local nonlinear* computation *before* the soma sums them — so a single biological neuron is closer to a **small two-layer network** than to one unit. The "atom" in the brain is already a little net.

**For us:** this is permission to make your atom *internally nonlinear* — which your old **2-3-3-2 Ganglion already was** (a multi-element block acting as one atom). The lesson: don't assume the atom is a single op; the brain's atom is a small nonlinear subnetwork, and yours can be too. It retroactively justifies the Ganglion as "atom = tiny net," and suggests the phase-2 atom could likewise be a small liquid/KAN subnetwork rather than one unit.

---

## Reservoir computing — the atom you *don't train*

*Echo State Networks: Jaeger, 2001; Liquid State Machines: Maass, 2002. ([Review](https://www.sciencedirect.com/science/article/abs/pii/S1574013709000173)).*

The cheapest possible atom story. Make a **big, fixed, random recurrent network** (the "reservoir"), don't train it at all, and only train a **simple linear readout** on top. The fixed random dynamics project inputs into a high-dimensional space where they become linearly separable; the readout picks them off. Learning is *just linear regression* — instant, stable, no backprop. (ESN = continuous units; LSM = spiking units.)

**For us:** a profound shortcut for the analog substrate, where a **fixed random recurrent analog circuit is nearly free** (it's just... a messy analog network you don't have to make precise). Reservoir computing says: *you may not need to train the recurrent core at all — only the readout.* For a first phase-2 prototype, this is the lowest-effort thinking loop that could work: a fixed analog reservoir + a trained SCFF/GD readout. It also tolerates device mismatch *by design* (the reservoir is supposed to be random). Strong "cheat with analog law" candidate.

---

## The shape of the answer (this file)

The atom, for us: the default (dot-product + ReLU, your Scap-crossbar) is fine for the **feed-forward** parts, but for the **time-series phase-2 core** the substrate-matched atoms are **continuous-time**: a **liquid neuron** (an RC element with a learnable, state-dependent time constant — the closest thing to "your circuit as a learning primitive"), inside the **Neural-ODE** frame ("let the analog dynamics be the computation"). **KAN** says expressivity can live in *learnable transfer curves* instead of gains (analog-friendly); **dendritic computation** says the atom can be a *small internal net* (your Ganglion already was); **reservoir computing** says you might not train the recurrent core *at all* — just the readout — which is the cheapest analog cheat available. Pick the atom whose math is your physics: that points hard at **liquid / ODE / reservoir.**
