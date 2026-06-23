# 7 — Input / output shape, and "don't let the model lie to itself"

> Your words: *"the input that doesn't label much, but still doesn't make the model lie to itself."* This is the **representation problem**, and "lying to itself" has two precise names: **collapse** (the encoder outputs the same thing for everything — trivially "consistent," totally useless) and **shortcut learning** (it latches onto a spurious cue instead of the real structure). This file is the menu of how to encode weakly-labeled input into a representation that is *honest*. It bites in **draft 6.0 now**, not just phase 2 — SCFF's whole job is encoding.

---

## VICReg — the cleanest "don't collapse" recipe

*Bardes, Ponce & LeCun, ICLR 2022 ([arXiv 2105.04906](https://arxiv.org/abs/2105.04906)).*

The keystone of this file. Self-supervised encoders learn by making two views of the same thing land on the same embedding — but the trivial cheat is to map *everything* to one constant point (collapse). Most methods dodge this with fragile tricks (stop-gradient, momentum encoders, negatives, batch-norm). VICReg replaces all of that with **three explicit, interpretable loss terms**:

1. **Variance** — force each embedding dimension's variance *above a threshold* (so the code can't shrink to a point — **the direct anti-collapse term**).
2. **Invariance** — the two views of the same input must match (the actual learning signal).
3. **Covariance** — decorrelate the dimensions (so they don't all encode the same thing — **anti-redundancy**).

No negatives, no stop-grad, no momentum needed. The three knobs are *exactly* "be informative (variance), be consistent (invariance), be non-redundant (covariance)."

**For us:** this is the literal, buildable answer to "don't let the model lie to itself." Your SCFF already has an *implicit* anti-collapse (the two-sided goodness loss, the negative pass) — VICReg is the *explicit, decomposed* version, and its three terms are all **local statistics a capacitor can hold** (a running variance, a correlation). If SCFF ever collapses in sim, **bolt a variance floor + a decorrelation term onto the goodness** — that's VICReg, and it's analog-cheap. This is the single most directly useful paper for the current build.

---

## Barlow Twins — collapse-avoidance as redundancy reduction

*Zbontar, Jing, Misra, LeCun & Deny, 2021 ([arXiv 2103.03230](https://arxiv.org/abs/2103.03230)).*

The same goal from information theory. Compute the **cross-correlation matrix** between the embeddings of two views, and push it toward the **identity**: diagonal = 1 (the same input feature is consistent across views) and off-diagonal = 0 (different features are decorrelated, carrying non-redundant information). One objective, both jobs. It's named after neuroscientist Horace Barlow's *redundancy-reduction* hypothesis — the brain encodes to remove redundancy.

**For us:** Barlow Twins says the anti-collapse condition *is* "make your features decorrelated and consistent" — a single matrix pushed to identity. It's a cousin of VICReg with one clean target. Worth knowing because the principle (decorrelate your code) is *also* a noise-robustness principle on analog hardware, and the cross-correlation is a crossbar outer-product (which you compute natively).

---

## MAE vs I-JEPA — reconstruct *pixels*, or predict in *representation space*?

*MAE: He et al., 2021 ([arXiv 2111.06377](https://arxiv.org/abs/2111.06377)); I-JEPA: Assran et al. (LeCun), 2023 ([arXiv 2301.08243](https://arxiv.org/abs/2301.08243)).*

The most important *design fork* in self-supervised encoding, and it's exactly your "don't lie to itself" question. **MAE** masks most of the input and trains the model to **reconstruct the missing pixels** — simple, scalable, strong. But reconstructing pixels forces the model to waste capacity modeling *every* detail, including noise it can't predict. **I-JEPA** masks the input and predicts the **representation** of the missing part, *not the pixels* — in abstract embedding space. The result: features that are **more semantic, generalize with far fewer labels**, and — crucially — **don't burn capacity memorizing unpredictable noise.**

**For us:** this fork is the deep version of your worry. *Predicting raw input = the model can lie by memorizing noise (overfitting to detail it shouldn't).* *Predicting in representation space = it can only "lie" about structure it actually understands.* This is **the** argument for why your encoder should be **predictive in feature space** (which SCFF's goodness already is, and which JEPA formalizes). The lesson: **never make the output target the raw input; make it a learned representation.** It's also the encoding-side of LeCun's whole program (`6-architectures.md`).

---

## Sparse coding & Sparse Distributed Representations — the honest, noise-robust code

*Sparse coding: Olshausen & Field, 1996 (Nature); SDR: Numenta/Hawkins ([Properties of SDRs](https://arxiv.org/pdf/1503.07469)).*

How the input should be *shaped*, from neuroscience. **Sparse coding** says: represent input as a combination of *few* active units from an *overcomplete* dictionary — and when Olshausen & Field did this on natural images, the learned dictionary became **edge detectors**, exactly like V1. **SDRs** (Numenta) push it further: binary codes where only ~2% of bits are on. Sparse codes have beautiful properties: huge capacity, **robustness to noise** (a few flipped bits barely change the meaning), and natural **similarity-by-overlap** (two codes are similar iff they share active bits).

**For us:** this is the encoding made *for your substrate.* Sparse = your committed **sparse** substrate property; few active units = few charge cycles = cheap; noise-robustness = exactly what an analog chip needs (PVT, drift). And **similarity-by-overlap is your LUT's matching operation.** If you ask "what shape should the signal between blocks be?", SDR is a strong answer: **sparse, high-dimensional, similarity-by-overlap.** It also resists "lying" — a sparse code can't collapse to a constant without losing all its overlap structure.

---

## VQ-VAE — turn the analog signal into stable discrete symbols

*van den Oord, Vinyals & Kavukcuoglu, 2017 ([arXiv 1711.00937](https://arxiv.org/abs/1711.00937)).*

A bridge from continuous to symbolic. A VQ-VAE encodes input to a continuous vector, then **snaps it to the nearest entry in a learned codebook** (vector quantization) — producing a *discrete token*. This is how modern systems turn images/audio into sequences of symbols a downstream model can reason over.

**For us:** relevant in two ways. (1) The **codebook is a learned LUT** — "snap to nearest prototype" is your novelty-allocation LUT, again. (2) **Discretization is a stability mechanism**: a noisy analog value snapped to the nearest symbol is *quantization-as-error-correction*, which an analog chip wants. If phase 2 needs stable symbols for the "thinking" loop (you can't reason over drifting floats), VQ is how you get them — and it's a crossbar nearest-match.

---

## Information Bottleneck — the principle of an honest representation (ideas side)

*Tishby, Pereira & Bialek, 1999; deep version: Tishby & Zaslavsky, 2015 ([arXiv 1503.02406](https://arxiv.org/abs/1503.02406)).*

The theory of *what a good representation even is.* A representation `Z` of input `X` should **compress `X` as much as possible** while **keeping everything relevant to the target `Y`** — minimize `I(X;Z)` (forget the input) subject to keeping `I(Z;Y)` (predict the target). Good learning is *forgetting the irrelevant.*

**For us:** this is the formal definition of "doesn't lie to itself": a representation lies when it keeps spurious detail (`I(X;Z)` too high → shortcut/overfit) or drops task-relevant signal (`I(Z;Y)` too low). It tells you the *target* SCFF's encoding should aim for — maximally forgetful, minimally task-blind — and it's why representation-space prediction (I-JEPA) beats pixel prediction: pixels force `I(X;Z)` up.

---

## The output side, briefly — weak labels

Your "input that doesn't label much" also has an output question. The trustable frames: **self-supervised pretrain + tiny supervised head** (your SCFF+GD split *is* this — encode without labels, read out with few), **semi-supervised** (a little labeled + lots unlabeled), and **contrastive/metric** outputs (represent the *target* as "near the right anchor," like Distance-Forward in `../papers/phase1-2/distance-forward.md`). The unifying rule: **let the labels shape only the last, cheap step; let structure do the rest.** That is already your 80/20.

---

## The shape of the answer (this file)

Encoding, for us: **predict in representation space, never raw input** (I-JEPA) so the model can't lie by memorizing noise; **explicitly prevent collapse** with a variance floor + decorrelation (VICReg/Barlow Twins) — both local, capacitor-friendly statistics; **shape the code sparse and high-dimensional** (sparse coding / SDR) for capacity, noise-robustness, and similarity-by-overlap (= your LUT); **discretize when you need stable symbols** (VQ); and aim, in principle, for the **information bottleneck** — forget the irrelevant, keep the task-relevant. SCFF is already an encoder of this family; these papers are how to keep it honest when it wobbles.
