# The objective reframe — the wall is intrinsic to *energy-goodness*, not to locality

> The single most important finding of the Phase-3 literature pass (2026-06-21). It does **not** overturn
> Phase 2 — it *narrows* its verdict, and that narrowing opens the most promising door. Read this first; the
> three direction files hang off it.

---

## What Phase 2 concluded, and the one word that was too strong

P2.2's decision said the depth wall is **"intrinsic to SCFF's forward-only locality"** — composing class
features across depth needs cross-layer coordination that *forward-only locality structurally cannot provide.*

That sentence is *almost* right, and the "almost" is the whole opportunity. P2.2 only ever varied the objective
**inside one family**: the energy-goodness `G = Σh²` (or `Σh`), changing *which negative* gets blended in
(random → class-oracle → prototype → KMeans). Every cell still asked each layer the same question — *"are you
loud on the coherent input and quiet on the mixture?"* — i.e. an **energy/density** question. The oracle proved
no *negative-selection* can make energy-goodness compose with depth. It did **not** test a *different kind of
objective*.

The literature has tested a different kind of objective, and it composes with depth — forward-only, gradient
-isolated, **and unsupervised**.

## The existence proof: Greedy InfoMax

**Greedy InfoMax (GIM)** — *"Putting An End to End-to-End: Gradient-Isolated Learning of Representations,"*
Löwe, O'Connor, Veeling, NeurIPS 2019 ([arXiv 1905.11786](https://arxiv.org/abs/1905.11786)).

- **Gradient-isolated modules, forward-only.** Gradients are explicitly blocked between modules
  (`∇GradientBlock(x) ≜ 0`). Exactly our substrate constraint: no backward pass crosses a layer boundary.
- **The objective is *predictive / info-preserving*, not energy.** Each module is trained with a local
  **InfoNCE** loss: predict your *own future (or neighbouring) representation* against negatives. The loss
  "enforces each module to maximally **preserve the information of its inputs**, while providing the necessary
  regularization for circumventing degenerate solutions."
- **It is fully self-supervised** — no labels touch the feature learning (labels appear only in the downstream
  probe, exactly like our linear-probe metric).
- **It demonstrably scales with depth.** "Each GIM module improves upon the representations of their
  predecessor" — speaker-classification error *falls* across layers 1→5. This is the rising per-layer curve our
  F3⁺ has never produced for energy-goodness SCFF.
- **It matches / beats end-to-end backprop.** STL-10 vision 81.9% (GIM) vs 80.5% (end-to-end CPC); LibriSpeech
  speaker-ID 99.4 vs 99.6. Greedy, forward-only, no backprop between modules — *and still competitive with the
  global method.*

So the barrier in our Phase-2 wall is **not** "forward-only locality." Forward-only local learning can build
deep, improving, unsupervised representations. The barrier is **the energy-goodness objective specifically**:
`Σh²` learns *where the data is loud* (density), and density does not compose across depth (Phase-1's
"clusters by density, not class"; Phase-2's wall). An **information-preserving / predictive** objective composes
because each layer is forced to *keep* the structure its input carried, not re-cluster it from scratch on the
unit sphere.

## The 2026 confirmation that tests *us* by name

**"Can Local Learning Match Self-Supervised Backpropagation?"** (Jan 2026,
[arXiv 2601.21683](https://arxiv.org/abs/2601.21683)) benchmarks the local-SSL family — **CLAPP, Forward-Forward,
LPL, and SCFF explicitly** — against end-to-end backprop-SSL.

- **The bottom line: yes, local SSL can match backprop-SSL** — CLAPP++ hits **80.51%** on CIFAR-10 vs
  BP-CLAPP++ **80.49%** — *with* the right architectural choices.
- **It confirms our wall** in standard form: local learning degrades with depth, early layers show weak
  gradient-alignment with what backprop would do.
- **The two coordination fixes it identifies are both cheap and substrate-shaped:**
  1. **Direct feedback** — use the *top layer's activations* as a reference signal for *all* lower layers
     (a top-down forward broadcast, **not** a backward gradient). This is the "cross-layer coordination" P2.2
     said was missing, supplied forward-only.
  2. **Keep the width constant across depth** (the "orthonormality / constant neuron count" condition) — depth
     equivalence to backprop holds in linear nets when layers don't shrink, and *breaks when dimensions shrink.*
     This is **directly your stated diagnosis** ("as dimensionality drops, each layer loses information") — and
     the fix is free: don't taper the SCFF stack.

## What this changes for the project

1. **P2.2's verdict should be re-stated.** Not *"depth is intrinsic-impossible for forward-only SCFF,"* but
   *"depth is impossible for the **energy-goodness** objective; a predictive / info-preserving local objective is
   the untested lever, and it has an existence proof (GIM) + a 2026 result matching backprop (CLAPP++)."* This is
   a narrowing, not a reversal — every energy-goodness result in Phase 2 still stands.

2. **The "expensive direction" framing gets a third option.** Draft 6.0 says *direction is the one expensive
   thing, so pay GD for it once (the 20%).* GIM/CLAPP say there's a way to get *depth-composing* representations
   **without** paying for global direction at all — by changing what "good" means at each layer from *energy* to
   *information preservation*. That doesn't remove the GD namer (you still need labels → real classes), but it
   could let the **80% bulk go genuinely deep unsupervised**, which is the thing Phase 2 said was impossible.

3. **It keeps everything the project values.** Unsupervised (the continual win — GIM/CLAPP carry no labels and no
   batch stats), forward-only, local, single-sample-plausible. It is the most *on-identity* way forward.

## The honest caveat — why this is a research bet, not a copy-paste

GIM and CLAPP earn their depth on data with **spatial or temporal structure** (image patches, audio sequences):
"predict the future representation" is well-defined because there *is* a next patch / next timestep to predict.
**Our headline regime is flat-MLP on vector input** — there is no sequence or spatial grid to predict across.
So the open research question is **"what does a flat-MLP SCFF layer predict?"** Candidate answers to test:

- **Predict a sibling's representation** (two augmentations / two samples of the same cluster → close; different
  → far) — a BYOL/SimCLR-flavoured local target. (We already flagged BYOL in N2; this is its natural home.)
- **Masked-feature reconstruction** — each layer predicts held-out input dimensions from the rest (a denoising
  /info-preserving objective with no labels).
- **Predict the *next layer's* aggregated state** — which is exactly **Direction 1** (cross-layer goodness):
  your A1-from-layer-2 idea is a one-step, forward, predictive coupling. So Direction 1 and this reframe are the
  *same family* seen from two ends.

If the predictive objective composes with depth on flat-MLP vector tasks, the Phase-2 wall is genuinely beaten
on the substrate's own cheap axis, unsupervised. If it *doesn't* (because flat vectors lack the structure GIM
exploits), that is itself a sharp, publishable result about *why* the substrate regime is special — and the
fallback is the proven supervised-local depth learner (Mono-Forward, see
[direction-3](direction-3-forward-only-alternatives.md)).

## The *older* existence proof — and why it picks the objective for us

Before backprop-SSL existed, deep nets were first trained **unsupervised, layer-locally, greedily**: stacked
**denoising autoencoders** (Bengio et al, NeurIPS 2007) and **Deep Belief Nets** (Hinton, Osindero & Teh, 2006).
Each layer was trained to *reconstruct its input* (or a corrupted version of it), frozen, then the next layer
stacked on top — no end-to-end pass. That is the direct ancestor of GIM, and it composed with depth precisely
because the per-layer objective was **information-preserving (reconstruction)**, not energy. For *us* it does
more than rhyme: it picks the Phase-3 objective. A flat-MLP has no "next patch" to predict (GIM's trick), but it
*always* has held-out dimensions to reconstruct — so **per-layer masked-feature reconstruction** is the
substrate-native member of this family: single-sample, no negatives, forward-only, and it penalizes exactly the
information-loss that the energy wall causes. (This is the decided Phase-3 primary objective — see
[`../src/phase3/README.md`](../src/phase3/README.md) §0.)

## Papers

- **Greedy InfoMax** — [1905.11786](https://arxiv.org/abs/1905.11786). The existence proof: forward-only,
  unsupervised, depth-composing, matches end-to-end.
- **Greedy layer-wise unsupervised pretraining** — Hinton et al 2006 (DBN); Bengio et al 2007 (stacked
  autoencoders); Vincent et al 2008 (denoising AE). The *original* unsupervised-depth method; reconstruction =
  the info-preserving objective; the historical root of the masked-reconstruction choice.
- **CLAPP** (Contrastive Local And Predictive Plasticity) — Illing et al, NeurIPS 2021
  ([2010.08262](https://arxiv.org/abs/2010.08262)). GIM made biologically-plausible / single-sample, Hebbian-ish.
- **LoCo** — [2008.01342](https://arxiv.org/abs/2008.01342). GIM + a small coupling between adjacent blocks
  (closes most of the gap to end-to-end) — a bridge between this reframe and Direction 1.
- **Can Local Learning Match Self-Supervised Backprop?** — [2601.21683](https://arxiv.org/abs/2601.21683). Tests
  SCFF by name; local-SSL = backprop-SSL with direct-feedback + constant width.
- **LPL** (Latent Predictive Learning) — the non-contrastive cousin tested alongside CLAPP/SCFF in 2601.21683.
