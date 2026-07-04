# Direction readouts — the spine, inside the namer (and a magnitude that nearly slipped through)

*Supervised Contrastive Replay / NCM-in-online-CI ([2103.13885](https://arxiv.org/abs/2103.13885)); Deep Streaming LDA
(Hayes & Kanan, CVPRW 2020, [arXiv 1909.01520](https://arxiv.org/abs/1909.01520)) and its successor Deep Streaming RDA
([2309.08353](https://arxiv.org/abs/2309.08353)); the magnitude-bias fixes — BiC ([1905.13260](https://arxiv.org/abs/1905.13260)),
Weight Alignment ([1911.07053](https://arxiv.org/abs/1911.07053)), logit-adjusted online CL
([2311.06460](https://arxiv.org/abs/2311.06460)); the near-twin architecture — RanPAC
([2307.02251](https://arxiv.org/abs/2307.02251)).*

> **Correction note (post critic-pass).** An earlier draft of this file claimed "cosine / NCM / Deep-SLDA all read class
> *direction*, not magnitude." **Two independent critics flagged that as false, and they're right** — it was the
> density≠class trap one level up, inside the very file whose job is the spine. A *distance to a prototype* is a
> **magnitude**. This version is precise about which readout is actually spine-clean. The catch is itself the lesson.

---

## The problem it answers

The project's spine is one rule: **preserve and read the class *direction*, never a magnitude** — energy, rank,
variance, confidence, *distance* are all magnitudes, and density ≠ class has bitten us five times. So the question for
the namer: **a plain linear-softmax head scores `wᵀφ + b` — scale, bias, and all — so is it the right readout, or does
it re-import the exact bug we fought for five phases?**

## The one idea that unstuck it — with the magnitude made explicit

**Thread 1 — magnitude bias is the *documented* failure of a naive head.** In class-incremental learning, a plain linear
classifier develops a **strong bias toward recently-seen / high-norm classes**: the weight vectors (and feature norms)
of new classes grow larger, so the softmax over-predicts them — *a magnitude artifact, not a class signal.* The fixes
all say "the magnitude is the bug": **BiC** rescales the biased logits (2 params); **Weight Alignment** literally
**aligns the weight *norms*** of new vs old classes; **logit-adjusted online CL** ([2311.06460]) subtracts a per-class
logit offset *during* streaming (cheaper, online-native). And the strongest single anchor is **Supervised Contrastive
Replay** ([2103.13885]): its headline finding is *"the softmax FC layer has recency bias — replace it with a
Nearest-Class-Mean head and replay improves."* The field independently re-derived "the trained-softmax magnitude is the
continual failure mode."

**Thread 2 — the prototype readouts dodge that bias, but they are *distance*-native, not direction-native.** This is the
part the first draft got wrong and the critics fixed. Be exact about three readouts:

| readout | rule | spine status |
| --- | --- | --- |
| **Cosine classifier** | L2-normalize features *and* class weights → classify by **angle** | **direction-pure.** The only strictly spine-clean one. |
| **NCM** (nearest-class-mean) | **Euclidean distance** to the class mean prototype | **distance = a magnitude.** Equals cosine *only if* features are L2-normalized first (they aren't, by default). |
| **Deep SLDA** | **Mahalanobis distance** to the class mean, shared (tied) covariance | **a magnitude, and worse — algebraically a linear-softmax with a `‖μ‖²` bias.** |

The SLDA point is the sharp one: SLDA with a tied covariance is **identical** to a linear head with weights
`w_c = Σ⁻¹μ_c` and **per-class bias** `b_c = −½ μ_cᵀΣ⁻¹μ_c` — and that bias **grows with `‖μ_c‖²`**, i.e. SLDA *has the
exact magnitude/offset degree of freedom the spine warns against.* It is a distance classifier in a covariance-**whitened**
space — and **whitening was rejected-as-a-lever in Phase 5.** So SLDA is not "the spine handed to us"; it is a
*recency-robust* readout (it has no trained softmax weights to inflate, which is *why* it dodges Thread-1's bias) that
nonetheless **reads a magnitude.** Recency-robust ≠ direction-reading. The honest hierarchy: **cosine is spine-clean;
NCM/SLDA are magnitude-based but bias-robust for a different reason.**

**Why the prototype family is still exciting — RanPAC, the published near-twin.** RanPAC ([2307.02251]) is almost our
architecture: frozen features → a **frozen nonlinear random projection** (a literal reservoir/ELM expansion) → a
**class-prototype head with a ridge-regularized Gram-matrix update** — **rehearsal-free, SOTA on 7 class-incremental
benchmarks.** Two findings matter for us: (1) the **ridge (second-moment-aware) prototype beats plain NCM** — the
covariance/Gram term earns its keep, which is *also* why SLDA carries it; (2) the whole update is **closed-form and
streaming** — a running mean + a running Gram matrix, both **substrate-native statistics** (a mean is a capacitor EMA; a
Gram matrix is a running second moment). So the prototype readout can plausibly run **on-chip with no gradient at all** —
the thing that makes it exciting is *cheapness and continual-safety*, stated honestly, **not** "it reads direction."

## What it means for us

- **The committed-readout experiment is a four-way bake-off, scored on three axes — and "spine-clean" is one of them.**
  Race **linear-softmax (the convex baseline) vs cosine (the direction-pure one) vs NCM vs a ridge-prototype (RanPAC/SLDA
  style)** on the continual home, scored on **accuracy × BWT (forgetting) × spine-cleanliness** (does the readout's
  verdict move when we rescale feature/prototype norms? a direction-pure readout doesn't). The spine bet is *not*
  "prototypes win because direction" — it's the sharper, falsifiable claim: **cosine is the spine-clean option; does it
  match the recency-robustness of the magnitude-carrying NCM/ridge-prototype, or do we pay a forgetting cost to stay
  spine-clean?** That tension is the result.
- **The magnitude bias is our continual failure mode, pre-labeled.** On a long class-incremental stream, BiC/WA/SCR tell
  us exactly what to watch — recency bias from growing norms on a trained softmax — and a cosine head tells us it won't
  appear if we classify by angle. A drift-*gated* stream presents classes in **bursts**, so class-imbalance in the head
  is *guaranteed* — pull in the imbalanced-stream toolkit (logit adjustment, balanced softmax, class-balancing reservoir
  sampling) under [`maintenance-and-replay.md`](../phase9/maintenance-and-replay.md).
- **The substrate is *not* free here — don't oversell "no optimizer."** A running mean is a cap EMA, yes; but a cosine
  head needs an L2-normalizer, a ridge prototype needs a Gram matrix + a solve, and SLDA needs `Σ⁻¹` — all **non-free
  digital blocks** (the architecture file §2.4 is careful that the contrastive normalizer is "real area + ADC traffic").
  "No gradient" ≠ "no readout cost"; the cost meter ([`the-economy-gate.md`](../phase8/the-economy-gate.md), Phase 8) is what
  decides which prototype variant is actually cheap on-chip.
- **It re-reads the struck adaptive exit (Phase 5) — carefully.** P5 struck the confidence-gated exit because confidence
  is a magnitude. A **cosine margin** (angle to the nearest vs runner-up class) is a *direction* signal and a spine-clean
  candidate for "where/whether to read." A Mahalanobis/NCM **distance is not** — so the north-star "feeling" signal
  ([`north-star-bridges.md`](../phase9/north-star-bridges.md)) should be the **cosine margin**, not the SLDA distance the first
  draft proposed. (Corrected there too.)
- **Honest caveat — the Gaussian/unimodal assumption, and where convexity ends.** NCM/SLDA assume per-class features are
  ~unimodal in the frozen space; if SCFF makes a class multi-modal, one mean underfits → fall back to a *few prototypes
  per class* (a **mixture**, which is **non-convex** — so the clean "convex readout" guarantee of
  [`the-convex-readout.md`](the-convex-readout.md) evaporates in exactly this realistic case) or a thin cosine-feature
  logistic head. The multimodality probe runs early, because it decides whether the elegant no-gradient story survives.
