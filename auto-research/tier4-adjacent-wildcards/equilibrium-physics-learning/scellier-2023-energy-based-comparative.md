# Energy-Based Learning Algorithms for Analog Computing: A Comparative Study
- **Authors / Year / Venue:** Benjamin Scellier, Maxence Ernoult, Jack Kendall, Suhas Kumar / 2023 / NeurIPS 2023
- **Link:** https://arxiv.org/abs/2312.15103 (proceedings: https://proceedings.neurips.cc/paper_files/paper/2023/hash/a52b0d191b619477cc798d544f4f0e4b-Abstract-Conference.html)
- **Tier / Topic:** tier4 / t4.2 equilibrium & physics-based learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the definitive menu of analog-native contrastive learning rules, benchmarked on equal footing; the family our forward-only choice must be argued against.

## TL;DR
Puts seven "two-state contrastive" learning algorithms — Contrastive Learning (hard clamp), Equilibrium Propagation variants, Coupled Learning variants — on the same models and datasets for the first time. Verdict: the *sign* of the perturbation matters enormously (negative beats positive), and **centered EP** (the ±β symmetric nudge) wins outright, training deep convolutional Hopfield networks to the best reported results for this family on MNIST, F-MNIST, SVHN, CIFAR-10, CIFAR-100.

## The mechanism (how it actually works)
Every algorithm in the family shares one skeleton: settle the physical system twice (or three times), measure a local quantity at each equilibrium, update each parameter by the *difference*. The family members differ only in **how the second state is produced**:

- **Contrastive Learning (CL):** clamp the output hard to the target. The second state is far from the first; the update is a crude secant, not a gradient.
- **EP, positive nudge (+β):** lean the output gently toward the target. First-order-biased gradient estimate.
- **EP, negative nudge (−β):** lean *away*. Also first-order-biased, but the bias has the opposite sign — and empirically it points in a *safer* direction (it overestimates rather than underestimates curvature penalties).
- **Centered EP (±β):** settle at +β and −β and difference the two. Biases cancel to second order; the estimate tracks the true gradient tightly. This is the winner.
- **Coupled Learning variants:** the same skeleton with a different second-state rule (clamp toward a convex combination of free output and target) — the rule used by the Penn self-learning resistor networks.

The engineering contribution matters as much as the taxonomy: they made deep conv Hopfield networks settle **13.5× faster** in simulation via asynchronous energy minimization + 16-bit precision — the settle cost is the tax on the whole family, and this is the state of the art in paying it.

## Key results / claims
- All seven roughly tie on MNIST — MNIST cannot distinguish learning rules in this family.
- On harder tasks the family fans out: hard-clamp CL degrades, one-sided EP is mid, **centered EP is best**; perturbation sign is a first-order design choice, not a detail.
- SOTA-for-the-family on five vision datasets with deep conv Hopfield nets.
- Framed explicitly as the training theory for analog (post-digital) hardware.

## How it relates to us
- **Organ / phase touched:** the north-star recurrent loop; also the honesty frame around our forward-only choice (P3–P5).
- **Same as us:** measure-locally-and-difference is exactly the shape our substrate exposes cheaply; their "perturbation sign is first-order" resonates with our recurring direction-bug paranoia — signs are where this design space lives or dies.
- **Different from us:** every algorithm here is **supervised** (the second state needs a target) and **settling** (needs equilibrium, twice or thrice per example). Our bulk is label-free and one-pass; our namer is closed-form, not iterative.
- **What we could borrow or test:** if the recurrent loop is ever trained in place, **centered EP is the committed variant** — do not re-derive this; the ±β choice is already benchmarked. Their fast-settle simulation tricks are the apparatus for any EqProp rung in our sim ladder.
- **What contradicts or challenges us:** on *static* accuracy per analog-native rule, this family out-trains anything forward-only — it holds the analog static-accuracy crown we already concede (P4/P10). If a reviewer asks "why not EqProp," this paper is both the threat and the answer: it costs 2–3 settles per labeled example and solves a different problem (supervised static training, not label-free continual organization).

## Follow-on leads
- Scellier 2024, "A fast algorithm to simulate nonlinear resistive networks" (arXiv:2402.11674) — the simulation apparatus, ⚠ not fetched here.
- Kendall et al. 2020, "Training end-to-end analog neural networks with equilibrium propagation" (arXiv:2006.01981) — the crossbar-EqProp seminal, ⚠ not fetched here.
- "Scaling Equilibrium Propagation to Deeper Neural Network Architectures" (arXiv:2509.26003) — the depth frontier, ⚠ not fetched here.
