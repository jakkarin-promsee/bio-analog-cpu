# Superposition, Memorization, and Double Descent
- **Authors / Year / Venue:** Tom Henighan, Shan Carter, Tristan Hume, Nelson Elhage, Robert Lasenby, Stanislav Fort, Nicholas Schiefer, Christopher Olah (Anthropic) / 2023 / Transformer Circuits Thread
- **Link:** https://transformer-circuits.pub/2023/toy-double-descent/index.html
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐⭐ — unifies superposition, memorization, and double descent into one storage story; directly reframes "over-provisioned capacity is safe" and "a bounded bulk stores datapoints or features."

## TL;DR
The same superposition geometry stores **either datapoints or features** as directions, and *which* one a network stores depends on the data-to-capacity ratio. Small datasets → the model stores individual **training points** in superposition (memorization); large datasets → it stores **generalizing features**. Double descent is the transition between these two storage regimes — overfitting is not irrational, it is a rational information-storage strategy that runs out of room.

## The mechanism (how it actually works)
Take the toy superposition model and vary dataset size instead of feature sparsity. With few datapoints, the cheapest way to fit is to memorize: each *training example* becomes its own direction in the hidden space — datapoints are stored in superposition exactly like features were. As you add data, at some point there are more datapoints than the hidden space can hold as clean directions; interference between memorized points blows up test error (the double-descent peak). Past that, the model abandons per-point storage and instead pays for **shared features** that explain many points at once — the generalizing regime, where test error descends again. The paper's key reframing: *"features" and "datapoint activations" are two interpretable views of the same underlying directions.* Memorization and generalization are the same mechanism (superposition) applied to different objects (points vs features); the switch between them **is** double descent.

## Key results / claims
- Three regimes in a one-layer toy model by dataset size: **memorization** (≲1k samples, points stored), **transition** (double-descent peak), **generalizing features** (≳10k samples).
- Double descent emerges *for free* from the superposition account — no separate mechanism needed.
- Overfitting = "storing datapoints, rather than features, in superposition" — a capacity-allocation phenomenon, not a pathology.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (bounded-capacity store), the spare-capacity hypothesis, the double-descent intuition the author re-derived, P11 scaling.
- **Same as us:** this is the mechanism under our author's "noise refutes itself" double-descent read *and* the spare-capacity hypothesis — the slack fills by superposing more directions, and over-capacity is safe because the learner prefers the compressible (feature) solution once it has enough data.
- **Different from us:** they study a supervised toy trained on a fixed dataset; our bulk is a continual, forward-only unsupervised stream with no epoch axis and no fixed dataset size. The "regime" for us is set by stream statistics, not by a dataset-size knob.
- **What we could borrow or test:** the datapoint-vs-feature distinction is a **diagnostic for our bulk**: on a task where our bulk WINS (nonlinear synth-home), is it storing features (generalizing) or points (memorizing)? A probe that measures whether hidden directions align with class-features vs individual samples would tell us *which side of double descent our frozen bulk lives on* — and predict when it will FLOOR.
- **What contradicts or challenges us:** if our tight-capacity streams (C=20, the P11 retention crossover) push the bulk toward the *memorization* regime, our "spare capacity shared across tasks" claim is really "we have not yet crossed into the feature regime" — capacity generosity may be doing the work, not sharing.

## Follow-on leads
- Elhage 2022 (the parent superposition model).
- Nakkiran 2019 (deep double descent — the same phenomenon in real deep nets, with epoch/sample axes).
- A "storage-regime probe" for our bulk — feature-alignment vs sample-alignment of hidden directions.
