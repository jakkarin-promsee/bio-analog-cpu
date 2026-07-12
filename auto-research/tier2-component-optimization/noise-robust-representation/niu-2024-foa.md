# Test-Time Model Adaptation with Only Forward Passes (FOA)
- **Authors / Year / Venue:** Shuaicheng Niu, Chunyan Miao, Guohao Chen, Pengcheng Wu, Peilin Zhao / 2024 / ICML 2024 (oral)
- **Link:** https://arxiv.org/abs/2404.01650
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐⭐⭐ — the field's flagship *forward-only* TTA, built exactly for frozen/quantized/edge substrates. Its "activation shifting" half is a one-vector, closed-form correction of a coherent feature translation — our residual's geometry, named and fixed in their §output-level step.

## TL;DR
FOA adapts a frozen model using nothing but forward passes, at two levels: (input level) a small prompt is optimized by CMA-ES, a derivative-free evolution strategy, with a fitness that mixes test-vs-train statistic discrepancy and prediction entropy; (output level) "activation shifting" — directly translate the test sample's activations by the gap between source and test activation centers so the features land back in the training domain. On 8-bit quantized ViT it beats full-precision gradient TENT with up to 24× less memory.

## The mechanism (how it actually works)
Two moves, both weight-free. **Prompt adaptation:** prepend a few learnable tokens to the input; since no backprop is available, optimize them with CMA-ES — sample candidate prompts from a Gaussian, score each with one forward pass, update the Gaussian's mean/covariance toward the winners. The fitness function is the honest part: pure entropy collapses in online unsupervised mode, so they anchor it with a distribution term — the discrepancy between the test batch's intermediate activation statistics and stored clean training statistics (the ActMAD statistic, reused as a *fitness*, not a loss). **Activation shifting:** maintain the source activation mean μ_s (offline) and a running test mean μ_t; at inference add the difference back — a ≈ a + λ(μ_s − μ_t) — one vector add at one layer, undoing the coherent translation the shift induced. No parameter changes, no extra passes (μ_t is a byproduct of normal forwards).

## Key results / claims
ImageNet-C ViT: FOA on an *8-bit quantized* model outperforms gradient-TENT on the full-precision model; up to 24× run-time memory reduction; works on smartphones/FPGAs/quantized deployments where backprop doesn't exist. Ablations show activation shifting alone contributes a solid share of the gain — the cheap half is not decoration. Scope: demonstrated on ViT-style models with prompts; the shifting half is architecture-generic.

## How it relates to us
- **Organ / phase touched:** the Stage-2 read side — the direct candidate mechanism for the P6 input-transducer directional residual; also the P8 economy (their memory/compute argument is our why-analog argument in digital-edge form).
- **Same as us:** the constraint set is *literally ours* — frozen weights, no backward pass, adaptation must be forward-byproduct cheap. Their justification (backprop unavailable on quantized/edge silicon) is the digital twin of our analog-substrate argument. P6 pinned the enemy as a coherent translation of the feature cloud; activation shifting is the published one-line cure for exactly that geometry.
- **Different from us:** their input-level half (CMA-ES prompts) presumes token-prompt architecture and a population of forward passes per step — extra passes, poor fit for our energy meter. Their statistics anchor batches; ours would be per-sample EMAs. And they adapt continuously; we would gate it (P8: firing more forgets more).
- **What we could borrow or test:** **activation shifting at the tap, verbatim** — running EMA of tap-feature mean, subtract the drift before the namer, λ trust-scheduled by Schneider's N/(N+n) blend, enabled only when the error-EMA gate trips. Closed-form: yes. Bulk write: none. Extra pass: none. Analog form: an offset/auto-zero stage at the read amplifier — the substrate already has this idiom. This is rank-1 in our synthesis.
- **What contradicts or challenges us:** their fitness-function finding (entropy alone collapses online; statistic-discrepancy anchors it) warns that if we ever *optimize* anything at test time, the objective must include a distribution anchor — our gate's error-EMA plays that role today.

## Follow-on leads
- CMA-ES as the general "learning without gradients on frozen substrates" tool — relevant far beyond TTA (north-star: could tune analog knobs in-situ).
- Purge-Gate (2025, arXiv 2509.09785) and BFTT3D (CVPR 2024) — the growing backprop-free TTA family for point clouds.
- ADAPT (card) — the closed-form Gaussian-inference cousin.
