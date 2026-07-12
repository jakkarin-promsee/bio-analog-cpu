# SLCA: Slow Learner with Classifier Alignment for Continual Learning on a Pre-trained Model
- **Authors / Year / Venue:** Gengwei Zhang, Liyuan Wang, Guoliang Kang, Ling Chen, Yunchao Wei / 2023 / ICCV 2023 (SLCA++ extension: arXiv 2408.08295)
- **Link:** https://arxiv.org/abs/2303.05118
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐⭐☆ — the two-timescale result: a *slow* body + *fast* head beats the prompt methods, and its classifier fix is a post-hoc Gaussian re-fit — our sleep, published.

## TL;DR
SLCA doesn't freeze the backbone — it fine-tunes it sequentially but at ~1/100 the head's learning rate ("slow learner"), which alone mitigates most of the progressive overfitting in continual fine-tuning. Then it repairs the classifier post-hoc: keep per-class Gaussian feature statistics (mean + covariance), sample from them, and re-align the classification layer across all classes seen so far. Large gains over prompt-based SOTA on split benchmarks.

## The mechanism (how it actually works)
Two timescales, cleanly separated. **Body:** sequential full fine-tuning with a large lr wrecks the pretrained representation task-by-task (progressive overfitting); dropping the body lr ~100× keeps the representation near the pretrain basin while still absorbing task-relevant structure — most of the CL problem dissolves right there. **Head:** the linear classifier still develops recency bias (later classes dominate). Fix: store class-wise Gaussian sufficient statistics of features; after each task, draw synthetic features from every class's Gaussian and re-train/align the classifier on the balanced synthetic set — a rehearsal in *statistics space*, no stored images. (SLCA++ replaces the sampling with a closed-form/refined alignment.)

## Key results / claims
- Split CIFAR-100, ImageNet-R, CUB-200, Cars-196: improvements up to ~45–50% over naive sequential fine-tuning, and it **generally beats L2P/DualPrompt-style SOTA** under the same pretrain.
- Both pieces matter: slow learner alone recovers most accuracy; classifier alignment adds the rest.
- Message to the field: the elaborate prompt machinery was compensating for a mis-set learning rate and an unbalanced head.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the 80/20 two-timescale split; sleep consolidation (P8 grid sleep, P9.4 proto-reanchor); namer recency bias (P7.3 CBRS).
- **Same as us:** the architecture-level moral is ours exactly — representation changes slowly and label-free-ishly, naming changes fast and cheaply, and periodic **statistics-space re-alignment** (their Gaussian re-fit ≡ our sleep's closed-form re-fit over the hippocampus LUT) keeps the head honest. It is the strongest mainstream evidence that the two-timescale + post-hoc-re-fit design pattern wins even when gradient everything is allowed.
- **Different from us:** their slow body still takes *supervised* gradients (ours takes none — SCFF is label-free); their alignment needs feature sampling + gradient re-training in the base version (our re-fit is closed-form from the start); they inherit the pretrain.
- **What we could borrow or test:** (1) their **Gaussian-statistics replay** validates storing per-class (μ, Σ)-style summaries instead of raw exemplars — an argument for enriching our LUT prototypes with cheap second-moment info where anisotropy bites (the P7 tied-covariance limit). (2) The lr-ratio sweep as a diagnostic: our effective "body:head timescale ratio" (SCFF step size vs sleep cadence) could be characterized the way they swept lr ratios — is our committed cadence sitting at their optimum analog?
- **What contradicts or challenges us:** SLCA shows a *slowly-supervised* body beats a *frozen* one under matched pretrain — i.e., some supervised plasticity in the representation is worth real accuracy. Our hard rule (never write the bulk with labels) forfeits that margin by design; the honest accounting is that we trade it for substrate cost + safety, and SLCA is the citation for what the trade costs on the accuracy axis.

## Follow-on leads
- SLCA++ (2408.08295) — the closed-form-alignment upgrade; closer to our sleep mechanics.
- Wang et al., "A Comprehensive Survey of Continual Learning" (2302.00487) — situates the two-timescale pattern.
- Neural-collapse / class-statistics classifier realignment line (e.g., feature-Gaussian replay in exemplar-free CIL) — the statistics-space rehearsal family.
