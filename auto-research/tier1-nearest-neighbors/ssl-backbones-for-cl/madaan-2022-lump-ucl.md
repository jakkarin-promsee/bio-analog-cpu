# Representational Continuity for Unsupervised Continual Learning (LUMP)
- **Authors / Year / Venue:** Divyam Madaan, Jaehong Yoon, Yuanchun Li, Yunxin Liu, Sung Ju Hwang — 2022 — ICLR 2022 (Oral)
- **Link:** https://arxiv.org/abs/2110.06976 (fetched; code: https://github.com/divyam3897/UCL)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐⭐ — the cleanest published statement of our founding bet: **unsupervised representations forget less than supervised ones**, with a mechanism story (flatter loss landscape).

## TL;DR
Head-to-head unsupervised-CL (UCL) vs supervised-CL (SCL) on split benchmarks: the unsupervised representations are "surprisingly more robust to catastrophic forgetting," consistently perform better, and generalize better out-of-distribution. Adds LUMP — mixup interpolation between current-task inputs and buffered past instances — as a simple UCL-specific forgetting reducer.

## The mechanism (how it actually works)
Two claims, one experiment design. (1) *The comparison:* run the same continual split-task protocol twice — once learning features with a supervised loss, once with an SSL objective (SimSiam / Barlow Twins family), evaluating both with probes — and measure forgetting at the representation level. Labels turn out to be the poison: a supervised loss drags features toward the *current* task's decision boundaries, so each new task overwrites the old geometry; a label-free objective only asks features to encode input structure, which successive tasks largely share. Their loss-landscape analysis backs this: UCL solutions sit in visibly flatter basins, so task-to-task updates displace them less. (2) *The fix:* LUMP replays the past not as extra samples but as **mixup blends** — each training input is an interpolation of a current instance and a buffered past instance, so the SSL objective never sees a purely-new batch and the representation is pulled smoothly rather than yanked.

## Key results / claims
- UCL forgets less and scores higher than SCL counterparts across sequential benchmarks (Split CIFAR-10 / CIFAR-100 / Tiny-ImageNet scale; exact digits in paper tables — not pulled here).
- UCL features transfer better to out-of-distribution downstream tasks.
- LUMP further reduces forgetting on top of the intrinsic UCL advantage.
- Mechanism evidence: flatter loss landscapes and lower feature-space drift for UCL.

## How it relates to us
- **Organ / phase touched:** SCFF bulk — the choice to keep the 80% label-free; the P4/A6 continual win; P9.0 rotates-not-forgets.
- **Same as us:** the core bet, verbatim — grow the representation without labels and continual robustness comes (partly) for free; direction (labels) is the expensive, dangerous ingredient.
- **Different from us:** their UCL is still backprop SSL, multi-epoch, task-partitioned, with a raw-image buffer for LUMP; evaluation is probe-based, not prequential/online. Nothing is forward-only, local, one-pass, or substrate-bound.
- **What we could borrow or test:** the *loss-landscape flatness* probe as an internal invariant — measure sharpness of the SCFF objective around the operating point across the stream; if our bulk's rotation-not-forgetting is the same phenomenon, flatness should show it. Also LUMP's blend-the-old-in idea maps naturally onto our LUT negatives (mix LUT samples into the contrast batch instead of pure-random partners).
- **What contradicts or challenges us:** nothing head-on — but see Marczak 2024: the SSL-vs-supervised gap may be a projector artifact, which would also weaken *this* paper's attribution of the win to label-freeness.

## Follow-on leads
- Loss-landscape flatness as a continual-robustness predictor (Mirzadeh et al. line of work).
- Mixup-in-contrast for streaming negatives (LUMP → LUT-negative blending).
- Davari et al. 2022 (probing) — the measurement-side companion to this paper's claim.
