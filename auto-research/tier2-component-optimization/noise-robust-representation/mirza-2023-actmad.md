# ActMAD: Activation Matching to Align Distributions for Test-Time-Training
- **Authors / Year / Venue:** M. Jehanzeb Mirza, Pol Jané Soneira, Wei Lin, Mateusz Kozinski, Horst Possegger, Horst Bischof / 2023 / CVPR 2023
- **Link:** https://arxiv.org/abs/2211.12870
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation
- **Relevance:** ⭐⭐⭐☆☆ — gradient-based (not for us as-is), but it answers a question we own: *which* feature statistic detects and localizes shift — per-feature means/variances at multiple depths, not just the last layer. That statistic is our P8.2 tap-drift signal, published as a loss.

## TL;DR
ActMAD adapts a deployed model by making the *activation statistics* of test data match those recorded on clean training data — not per-channel at the output, but per-feature (per spatial location) across many layers. The match is enforced by an L1 loss between test-batch and stored clean statistics, minimized by gradient steps. Task-agnostic (they adapt an object detector, not just classifiers).

## The mechanism (how it actually works)
The story: corruption leaves fingerprints at every depth of the network, and the fingerprints are *local* — individual features shift individually, not whole channels uniformly. So: (1) offline, record clean means and variances of each feature at chosen layers; (2) online, estimate the same statistics on the incoming test batch; (3) define the loss as the distance between the two sets of statistics; (4) update the model (they update everything; the supervision is dense because statistics are matched location-wise across multiple layers). No labels anywhere — the "supervision" is entirely the stored clean statistics. The dense, multi-layer statistic is why it converges fast on little data.

## Key results / claims
SOTA on CIFAR-100-C and ImageNet-C at publication; +15.4 mAP over prior TTA on KITTI-Fog object detection; reaches full performance from small amounts of streaming data; architecture- and task-agnostic. Still gradient-based — inherits the usual online-TTA fragilities (needs batches, careful lr).

## How it relates to us
- **Organ / phase touched:** the drift gate (P8.2's validated-but-not-shipped class-direction tap-drift trigger); the tap statistics; the read side.
- **Same as us:** the load-bearing object is a *stored clean reference of feature statistics* compared against a *running test estimate* — that pair is exactly what our P8.2 tap-drift trigger computes. ActMAD is independent confirmation that this signal is rich enough to drive full adaptation, and that multi-depth beats last-layer-only.
- **Different from us:** they *descend the gradient of* the statistic mismatch into the bulk weights — we are forbidden to (frozen bulk, no backward). We would consume the same signal two cheaper ways: as a gate (fire the namer/sleep) and as a direct closed-form offset (subtract the mean-shift; Schneider/FOA cards).
- **What we could borrow or test:** (1) upgrade the P8.2 trigger's statistic from class-direction-only to ActMAD's per-feature mean+variance across taps — better shift localization (which layer moved tells transducer vs tap channel apart — a diagnostic we wanted in P6); (2) their finding that location-wise statistics beat channel-wise suggests our per-tap drift EMA should not be collapsed to one scalar too early.
- **What contradicts or challenges us:** their results imply a *fully-corrective* read-side fix may need more than the first moment when shift is structured; if our mean-offset rung plateaus, the ActMAD statistic says what to align next (per-feature variance) — still closed-form as a diagonal rescale.

## Follow-on leads
- NOTE (NeurIPS 2022) — statistics estimation under temporally-correlated (non-iid) streams; directly relevant to our drifting-stream setting.
- CAFe / feature-alignment TTA family (2023–2024) — clean-feature alignment variants.
- Using stored statistics as a *drift localizer* (which-layer-moved) — no direct paper found; candidate experiment of ours.
