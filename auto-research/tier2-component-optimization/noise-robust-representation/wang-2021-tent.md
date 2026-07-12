# Tent: Fully Test-Time Adaptation by Entropy Minimization
- **Authors / Year / Venue:** Dequan Wang, Evan Shelhamer, Shaoteng Liu, Bruno Olshausen, Trevor Darrell / 2021 / ICLR 2021 (spotlight)
- **Link:** https://arxiv.org/abs/2006.10726
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐☆☆ — the field's anchor for "fix shift at test time, no labels" — and the anti-pattern we must NOT copy (it needs a backward pass).

## TL;DR
Tent adapts a deployed model to shifted test data using only the test stream itself: it minimizes the entropy of the model's own predictions, updating *only* the normalization layers' statistics and affine (scale/shift) parameters. It launched the whole "fully test-time adaptation" (TTA) subfield — everything else in this folder is a reaction to it.

## The mechanism (how it actually works)
The story: a confident model is usually a correct model, and corruption makes predictions *diffuse*. So take each unlabeled test batch, run it forward, compute the softmax entropy of the predictions, and take a gradient step to reduce that entropy. To keep this from destroying the network, the gradient is allowed to touch almost nothing: the batch-norm running statistics are replaced by the *test batch's* statistics (a closed-form move), and only the per-channel scale γ and shift β of the norm layers are updated by the gradient (a tiny linear, feature-wise modulation). The bulk weights never move. So Tent = (a) re-estimate normalization moments on test data + (b) a low-dimensional learned feature modulation driven by prediction confidence.

## Key results / claims
State-of-the-art on ImageNet-C at publication; works source-free (no training data at test time); one pass over the test set suffices. Later work (SAR, ICLR 2023; the IJCV 2024 survey) showed the failure modes: it collapses on small batches, temporally correlated streams, and mixed shifts — exactly the online, sample-at-a-time regime we live in.

## How it relates to us
- **Organ / phase touched:** the Stage-2 read side (the P6-named input-transducer directional residual); the frozen SCFF bulk stays frozen — same constraint Tent imposes on itself.
- **Same as us:** the deployment premise is identical — a frozen expensive representation, shift arrives at eval time, no labels, fix it at the cheap periphery. Tent's "only touch the norm layers' scale/shift" is the GD version of our "only touch the read side."
- **Different from us:** the correction is *gradient-driven* (entropy backward pass through the head) — violates our no-backward envelope; and it's batch-defined, while our stream is per-sample online. Its documented instability at batch-size 1 is a warning, not an option.
- **What we could borrow or test:** the *decomposition*, not the method: Tent's gain = closed-form moment re-estimation + a tiny learned modulation. Schneider et al. (card in this folder) showed the closed-form half alone carries most of the robustness — that half is exactly substrate-shaped for us.
- **What contradicts or challenges us:** nothing structural — but if a reviewer asks "why not just TENT the namer," the answer is on the record: per-sample online streams are where entropy-TTA collapses (survey card), and our gate already uses the better signal (error-EMA, not entropy).

## Follow-on leads
- SAR (Niu et al., ICLR 2023) — stabilizing entropy-TTA in the wild (batch=1, mixed shift) via sharpness-aware filtering.
- EATA (ICML 2022) — sample-filtering + anti-forgetting regularizer on TTA updates.
- The IJCV 2024 OTTA survey (cited in `_SYNTHESIS.md`) for the batch-size-1 stability landscape.
