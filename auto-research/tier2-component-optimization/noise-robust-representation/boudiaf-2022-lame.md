# Parameter-free Online Test-time Adaptation (LAME)
- **Authors / Year / Venue:** Malik Boudiaf, Romain Mueller, Ismail Ben Ayed, Luca Bertinetto / 2022 / CVPR 2022 (oral)
- **Link:** https://arxiv.org/abs/2201.05718
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐☆☆ — the "adapt the *outputs*, not the model" pole: fix predictions with a closed-form-ish smoothing, zero parameters touched. Also the field's best documented "TTA methods break outside their tuning niche" result.

## TL;DR
LAME never touches any weight — not even the classifier. It takes the frozen model's softmax outputs over a batch and refines the *assignment vector* directly: maximize likelihood under a Laplacian (neighborhood-smoothness) regularizer, solved by a fast concave-convex fixed-point iteration. Its headline finding: across a wide grid of realistic scenarios, gradient-TTA methods (Tent etc.) often do *worse than the unadapted model*, while LAME degrades gracefully.

## The mechanism (how it actually works)
The story: under shift, individual posteriors are unreliable but *relational* structure survives — nearby features almost surely share a label. So treat the model's probabilities as a noisy starting point and solve, per test batch: find soft assignments that (a) stay close to the model's posteriors (log-likelihood term) and (b) agree across feature-space neighbors (Laplacian term over a kNN affinity matrix built on the frozen features). The objective is concave in the assignments; a concave-convex procedure gives a few cheap fixed-point iterations (matrix–vector products with the affinity matrix), no gradients, no learning rate, no parameters. Output correction only — the model is untouched, so it can never be *destroyed* by adaptation.

## Key results / claims
On their large "realistically varied" benchmark (non-iid streams, class imbalance, mixed shifts), LAME beats Tent/SHOT-style adaptation on average while being faster and lighter; the deeper claim is methodological — TTA methods tuned on iid ImageNet-C batches fail silently when the stream is dependent. It needs a *batch* with usable neighborhood structure; it does nothing for a single isolated sample.

## How it relates to us
- **Organ / phase touched:** the namer's output stage; the P10/P11 stream evaluation philosophy.
- **Same as us:** "the representation is frozen and the correction must be un-destroyable" — LAME's do-no-harm property is the same instinct as our gate-as-safety result (firing more forgets more). Their non-iid-stream skepticism is our P10/P11 evaluation design, published.
- **Different from us:** LAME corrects assignments *within a batch* using neighbor structure; our stream is per-sample online with no batch to smooth over. And it's transductive — the correction evaporates after the batch; nothing is banked.
- **What we could borrow or test:** a LUT-backed variant: our hippocampus prototypes ARE a persistent neighborhood structure, so a Laplacian smoothing of the namer's posterior against the k nearest *stored prototypes* (rather than batch neighbors) would give a per-sample, memory-backed LAME — a few dot products against the LUT, no writes anywhere. Worth one rung as the "cheapest possible read-side fix" control.
- **What contradicts or challenges us:** LAME's evidence that self-supervised adaptation signals (entropy, pseudo-labels) betray you under dependent streams cuts against any *awake* prototype-chasing borrow (T3A/PTA cards) — it argues for keeping corrections output-side or gate-conditioned.

## Follow-on leads
- The concave-convex procedure (Yuille & Rangarajan) as the closed-form-adjacent solver family.
- "In Search of Lost Online TTA" survey (synthesis) — confirms LAME as the batch-size-1-robust pole.
- Graph-regularized SLDA — whether Laplacian smoothing can be folded into the namer's Gram algebra (open, no direct paper found).
