# Self-Supervised Training Enhances Online Continual Learning
- **Authors / Year / Venue:** Jhair Gallardo, Tyler L. Hayes, Christopher Kanan — 2021 — BMVC 2021
- **Link:** https://arxiv.org/abs/2103.14010 (fetched; BMVC PDF: https://www.bmva-archive.org.uk/bmvc/2021/assets/papers/0636.pdf, fetched)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐⭐ — our operating point, published: a **label-free backbone + Deep SLDA streaming head** for online CL — and SSL beats supervised pretraining, most when pretraining data is small.

## TL;DR
Pretrain the backbone with SSL (MoCo-V2, Barlow Twins, SwAV) instead of supervised labels, then run online continual learners on top — **Deep SLDA** (frozen features, closed-form head), **online softmax with replay** (frozen features), and **REMIND** (lower layers frozen, upper trainable). SSL features win across all three, with a 14.95% relative top-1 gain on class-incremental ImageNet (new SOTA at the time), and the advantage *grows as pretraining data shrinks* (up to 89.14% relative for SwAV+REMIND pretrained on only 10 classes).

## The mechanism (how it actually works)
The hypothesis is representational generality: a supervised pretrain optimizes features for the pretraining label set, so a streaming learner reading those features inherits their bias; an SSL pretrain optimizes for invariance/structure of the inputs themselves, producing features that stay useful as unseen classes stream in. The test is deliberately head-agnostic — three online CL algorithms of increasing plasticity (pure frozen + closed-form LDA head → frozen + replayed softmax → partially trainable with latent replay) — so any consistent gap is attributable to the *backbone's training signal*, not the head. The gap is consistent, and biggest exactly where supervised features are most overfit to their pretraining labels: the small-pretraining-set regime.

## Key results / claims
- SSL pretraining > supervised pretraining for online CL across all three heads; class-incremental ImageNet (1000 classes), transfer checked on Places-365.
- +14.95% relative top-1 over prior online-CL SOTA with 100-class pretraining; up to +89.14% relative (SwAV, 10-class pretrain, REMIND).
- Gains are largest when pretraining samples are fewest — the label-free advantage is a small-data advantage.

## How it relates to us
- **Organ / phase touched:** the whole two-brain layout — label-free bulk + SLDA namer (P7/P8's committed economy); P4/A6 continual home.
- **Same as us:** architecturally the nearest twin in this topic: unsupervised representation, frozen at read-time, with a **closed-form streaming LDA head** doing the continual naming. Their result is direct published evidence for both halves of our 80/20 split.
- **Different from us:** their backbone is grown *offline, IID, multi-epoch, with backprop*, then frozen forever — the stream never touches it. Ours is grown ON the stream, forward-only, local, keeps learning (rotating) for life, and is bound to an analog cost model. Their SSL-vs-supervised comparison also stops at pretraining; they never ask whether the backbone could keep learning label-free during deployment (our whole premise).
- **What we could borrow or test:** their small-pretrain-data finding is *good news we haven't cashed*: our regime (small, stream-grown, label-free) is where the SSL advantage is documented largest. A direct test: freeze our bulk at several points along the stream and measure namer performance vs stream-position — the "how much pretraining does the bulk need" curve, comparable to their 10/100-class sweep.
- **What contradicts or challenges us:** nothing structural; but note their SSL backbones still needed ImageNet-scale *unlabeled* data. Whether a *tiny* label-free bulk holds the same advantage on richer inputs than our benches is untested (our P11 CIFAR-gray floor is the warning).

## Follow-on leads
- Hayes & Kanan, Deep SLDA (already carded, t1.2) — the head half of this paper.
- REMIND (latent replay with partial plasticity) — the middle ground between our frozen-read and full fine-tuning.
- The awesome-continual-self-supervised-learning list (Gallardo maintains it): https://github.com/jhairgallardo/awesome-continual-self-supervised-learning — the topic's living index.
