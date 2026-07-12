# Test-Time Classifier Adjustment Module for Model-Agnostic Domain Generalization (T3A)
- **Authors / Year / Venue:** Yusuke Iwasawa, Yutaka Matsuo / 2021 / NeurIPS 2021
- **Link:** https://proceedings.neurips.cc/paper/2021/hash/1415fe9fea0fa1e45dddcff5682239a0-Abstract.html
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐⭐☆ — the seminal *backprop-free* TTA: adjust only the classifier's prototypes from confident test features. Our P9.4 proto-reanchor is this idea executed at sleep time.

## TL;DR
T3A fixes domain shift by touching nothing but the final linear classifier: it rebuilds each class's weight vector as a running "pseudo-prototype" — the average of test-sample features the model itself confidently assigned to that class — then classifies by proximity to these updated prototypes. No gradient, no bulk write, negligible compute.

## The mechanism (how it actually works)
The picture: a frozen backbone maps shifted inputs to features that are still *class-organized* but *displaced* — the old classifier weights point at where the classes used to be. T3A moves the pointers instead of the features. For each incoming test sample: (1) forward pass, get the feature z and predicted class ŷ; (2) if the prediction's entropy is low enough (a confidence filter keeps only the M most-confident supports per class), append z to class ŷ's support set; (3) the class-ŷ "template" becomes the mean of its support set; (4) classify by dot-product/nearest-template. The classifier's weights are literally replaced by running class means of self-labeled confident test features. Backprop-free by construction; the only state is the per-class support memory.

## Key results / claims
Consistent gains over ERM and gradient-TTA on PACS / VLCS / OfficeHome / TerraIncognita, across ResNet-18/50, ViT, BiT, MLP-Mixer; stabler than Tent (no stochastic optimization to diverge); minimal overhead. The gains are modest in absolute terms — later work (ADAPT card) attributes this to adjusting means only, ignoring second-order structure.

## How it relates to us
- **Organ / phase touched:** the namer (SLDA prototypes) + the hippocampus LUT; the P6 input-transducer residual; P9.4's proto-reanchor.
- **Same as us:** prototype classifier over a frozen representation; correction = move the class means; backprop-free, closed-form-friendly. This is the published genus of our P9.4 sleep-time re-anchoring (0.79→0.99 recovery).
- **Different from us:** T3A runs *awake* — every confident test sample nudges the prototypes immediately — while our re-anchor waits for sleep. And T3A self-labels from the classifier's own confidence with no drift gate; we already own a better trigger (the error-EMA gate, P8).
- **What we could borrow or test:** the awake-time version of P9.4 — confidence-filtered running prototype updates between sleeps, gated by our existing DDM gate so it only runs when drift is detected. Substrate cost: a per-class running mean = one MAC + one write to the LUT per confident sample. The entropy-filtered support set (keep top-M) is the guard against self-labeling garbage.
- **What contradicts or challenges us:** the P8 lesson "firing more forgets more" — T3A-style always-on prototype chasing is exactly the failure our gate exists to prevent. Any borrow must stay gate-conditioned; T3A's own confidence filter is necessary but (per LAME's critique) not sufficient under strong shift.

## Follow-on leads
- AdaNPC (ICML 2023) — kNN-memory variant of the same idea.
- PTA (card in this folder) — the 2026 cache-free descendant with confidence-weighted prototype accumulation.
- FeCAM (NeurIPS 2023) — prototype + covariance classifier we already struck in P7; relevant boundary for how far prototype-only goes.
