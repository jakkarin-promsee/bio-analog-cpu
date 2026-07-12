# Energy and Policy Considerations for Deep Learning in NLP
- **Authors / Year / Venue:** Emma Strubell, Ananya Ganesh, Andrew McCallum / 2019 / ACL 2019 (arXiv:1906.02243)
- **Link:** https://aclanthology.org/P19-1355/ · arXiv:1906.02243 (fetched via search)
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐ — the paper that put *training* energy on the map and, crucially for us, distinguished the cost of a single training run from the cost of the *full development process* (NAS/tuning). The anchor for the train-vs-search and train-vs-inference conflation traps.

## TL;DR
Estimates dollar and carbon cost of training NLP models by combining reported train time × measured GPU/CPU/DRAM power × PUE × grid CO₂. Its most-cited number — a transformer + neural-architecture-search run emitting on the order of a car's lifetime CO₂ — comes almost entirely from the **search/tuning**, not one training run. The lasting lesson: *what you count* (one run vs the whole R&D process) changes the number by orders of magnitude.

## The mechanism (how it actually works)
Power is sampled live (nvidia-smi for GPU, RAPL-style for CPU/DRAM), multiplied by wall-clock training time and PUE, then by an average grid carbon factor. The paper then separates two very different accounting boundaries: (a) the cost of training the *final reported model* once, versus (b) the cost of the *entire experimentation campaign* — hyperparameter sweeps and architecture search — that produced it. The headline shock value lives in (b). This is the origin of a now-standard reviewer question: "is your reported energy for one run, or for everything you did to get here?" It also implicitly flags train-vs-inference conflation: training is a one-time (or periodic) cost, inference is amortized over deployment, and the two cannot be compared without stating the boundary.

## Key results / claims
- Concrete cost estimates for training BERT / big transformers / NAS, with the NAS run dwarfing the rest.
- Recommends reporting training time + hardware, reporting sensitivity to hyperparameters, and prioritizing computationally efficient hardware/algorithms and reporting budgets.
- Establishes the *development-process* vs *single-run* distinction as a first-class accounting choice.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P8/P10 loop energy (a *continual, always-on training* cost, not a one-shot), the P11 scaling economy, the honest scope of "our training is cheap."
- **Same as us:** our object's whole value proposition is *on-chip, online, continual* learning — i.e. training energy is the recurring operational cost, exactly the quantity Strubell says to price. We already meter the deployed loop (GD-share 0.121, bp-ratio 0.501), not a one-off.
- **Different from us:** Strubell's train energy is a *batch, offline, one-time* pretraining cost amortized over long inference; ours is a *streaming, per-step, perpetual* cost with no train/inference boundary. This is a genuine framing advantage we can claim — but only if we are explicit that our "training energy" is a *rate* (pJ/sample continual), not a one-shot budget, so we aren't accused of comparing a rate to a lump sum.
- **What we could borrow or test:** adopt the single-run-vs-development-process boundary honestly — our P-phase *sweeps/ablations* (all the tuning that produced the frozen object) are Strubell's category (b) and are currently uncounted; the *deployed loop* is category (a). State which we report (we report the deployed loop) so a reviewer can't conflate the two.
- **What contradicts or challenges us:** Strubell's method is *measured/estimated on real GPUs at fixed accuracy checkpoints* — a reviewer can note our continual-training-rate claim has no analogous measured anchor. Also: because search cost dominates, a skeptic could argue the *real* cost of our object is the whole 11-phase campaign, not the deployed loop — we should pre-empt by scoping the claim to steady-state deployment.

## Follow-on leads
- Lacoste et al. 2019 "Quantifying the Carbon Emissions of ML" (ML CO₂ Impact calculator) — the lightweight estimator built on the same accounting.
- The "amortize training over inference" boundary → train-vs-inference conflation as a named trap for our synthesis.
