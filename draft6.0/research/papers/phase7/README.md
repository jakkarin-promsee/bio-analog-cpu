# `phase7/` — the readout: the GD *namer* on the frozen SCFF bulk

> **Stage-2, the first GD phase.** The SCFF bulk organizes the world unsupervised; **this is the part that puts *our*
> labels on it** — the precise 20% brain. The cold-start surprise of the whole research pass: because the bulk is
> *frozen to GD*, the namer's *learning* is **(near-)convex** — the scary "now we need gradient descent" turns out
> small. Two story files: **what optimizer/shape** the readout is, and **the spine inside it** (read *direction*, not
> magnitude). Mechanism-first; each ends in a **"For us."**
>
> Context: this folder feeds [`../../../src/stage2-design.md`](../../../src/stage2-design.md) §3.1 + Phase 7. The
> noise question that *used* to share this pass was split out to a Stage-1 extension — [`../phase6/`](../phase6/README.md).

---

## The frame (read before the files)

**Because the bulk is frozen-to-GD, the readout's *learning* is a (near-)convex problem.** A trained readout on a fixed
nonlinear bulk is **reservoir-*like***: the *regression* has **no bad local minima**, so we need **no exotic optimizer**.
**Two hedges the critic pass insisted on, and they're load-bearing:** "convex" names the **regression, not the deployed
readout's substrate cost** (the softmax/normalizer is a non-free digital block; tap-reading + the Scap count are real —
that's what the Phase-8 cost meter measures); and we are reservoir-*like* but **not a reservoir proper** — our bulk is
*trained-then-frozen*, not random, so we inherit the readout convexity but **not** the reservoir's free
device-mismatch-tolerance (which is *why* the noise question is a real Phase-6 problem, not auto-solved here).

**The spine, in the namer:** **only the *cosine* classifier is direction-pure.** NCM / Deep-SLDA classify by *distance*
to a class mean — and a distance is a **magnitude** (SLDA with a tied covariance is *algebraically a linear-softmax with
a `‖μ‖²`-scaled per-class bias*; its Mahalanobis metric is a *whitened* distance, and whitening was rejected-as-a-lever
in P5). So NCM/SLDA are **not "the spine handed to us"** — they are **recency-robust** (no trained softmax weights to
inflate, which is *why* they dodge the continual magnitude bias), which is **not** the same as reading direction. The
Phase-7 bake-off scores *which readout stays spine-clean while matching the prototypes' recency-robustness.*

---

## The files

| File | What it covers | The one idea |
| ---- | -------------- | ------------ |
| [the-convex-readout.md](the-convex-readout.md) | Reservoir computing / ELM / online convex optimization. Why a readout on a frozen bulk is convex; FTRL/regret; SGD vs Adam vs Lion vs *no optimizer at all*; what a 2-register Scap can hold. | **The 20% is the easy part — frozen features make it convex.** |
| [direction-readouts.md](direction-readouts.md) | Cosine classifiers, NCM, **Deep SLDA**, **RanPAC** ridge-prototype, classifier magnitude-bias (SCR / BiC / Weight-Alignment), the bursty-stream imbalance guard. | **Cosine reads *direction*; NCM/SLDA carry a magnitude but dodge recency bias — score which stays spine-clean.** |
| [analytic-and-covariance-readouts.md](analytic-and-covariance-readouts.md) *(2nd-pass audit)* | The families the rough pass missed: **Analytic Continual Learning / recursive-least-squares** (ACIL, GKEAL, DS-AL, AOCIL, GACL, and ⭐ **F-OAL** = forward-only + online + no-gradient); **FeCAM** per-class-covariance Mahalanobis; the **RanDumb** skeptic-control. | **No-gradient streaming naming is a *published paradigm*, not a bet — and FeCAM is the closed-form multimodality escape (and the max-magnitude spine pole).** |

## Papers (the readout slice)

| paper | id / venue | the one-line reason it's here |
| --- | --- | --- |
| Echo-State Networks (Jaeger 2001) · Liquid State Machines (Maass 2002) · ELM (Huang 2006) | classics | train **only** the readout on a frozen nonlinear bulk = **us** |
| Deep Randomized Neural Networks | [2002.12287](https://arxiv.org/abs/2002.12287) | the modern survey of frozen-features + trained readout |
| Online Convex Optimization (Hazan, book) · FTRL (McMahan 2011) | classics | readout on frozen features = OCO → **regret bounds, no bad minima** |
| Parameter-free online logistic regression (log-regret) | [1902.09803](https://arxiv.org/abs/1902.09803) | the **honest** OCO regret story for a classification head |
| Lion (EvoLved Sign Momentum) | [2302.06675](https://arxiv.org/abs/2302.06675) | 1-state optimizer (vs Adam's 2) — but AdamW wins on *small* models like ours |
| **RanPAC** (random projection + ridge prototype) | [2307.02251](https://arxiv.org/abs/2307.02251) | **the near-twin**: frozen feats + random proj + ridge-prototype, rehearsal-free SOTA, no gradient; ridge **beats** plain NCM |
| Deep SLDA (Hayes & Kanan, CVPRW 2020) | [1909.01520](https://arxiv.org/abs/1909.01520) | frozen backbone + running mean + **tied covariance** readout — substrate-native (but Mahalanobis = a magnitude) |
| Deep Streaming RDA (SLDA successor) | [2309.08353](https://arxiv.org/abs/2309.08353) | relaxes the single-tied-covariance assumption → the **multimodality** fallback |
| Supervised Contrastive Replay (NCM in online CI) | [2103.13885](https://arxiv.org/abs/2103.13885) | **the magnitude-bias anchor**: softmax FC has recency bias → replace with NCM |
| BiC (Large Scale Incremental Learning) | [1905.13260](https://arxiv.org/abs/1905.13260) | the **magnitude-bias** failure of a naive linear head, post-hoc fix |
| Weight Alignment (Maintaining Discrimination & Fairness) | [1911.07053](https://arxiv.org/abs/1911.07053) | fixes head bias by **aligning weight *norms*** — magnitude is the bug |
| Logit-adjusted online CL | [2311.06460](https://arxiv.org/abs/2311.06460) | online (during-stream) fix for the bursty-stream recency/imbalance bias |
| — *2nd-pass audit adds (IDs review-resolved)* — | | *(see [analytic-and-covariance-readouts.md](analytic-and-covariance-readouts.md))* |
| **FeCAM** (per-class covariance Mahalanobis) | [2309.14062](https://arxiv.org/abs/2309.14062) | **the closed-form multimodality/heterogeneity escape — and the max-magnitude spine pole** (CIFAR100/5t 70.9 vs NCM 64.8) |
| **Deep SLDA** (tied covariance, streaming) | [1909.01520](https://arxiv.org/abs/1909.01520) | **the cheaper covariance *middle*** (one shared cov) — between NCM and FeCAM on the ladder |
| **F-OAL** = **AOCIL** (Forward-only Online Analytic Learning) | [2403.15751](https://arxiv.org/abs/2403.15751) *(NeurIPS 2024; one paper, v1→v2 rename)* | ⭐ **forward-only + online + recursive-least-squares, no gradient — our exact constraint** |
| ACIL · GKEAL · DS-AL · GACL (Analytic CL family) | [2205.14922](https://arxiv.org/abs/2205.14922) / CVPR'23 (few-shot, no arXiv) / [2403.17503](https://arxiv.org/abs/2403.17503) / [2403.15706](https://arxiv.org/abs/2403.15706) | **RLS = joint-learning-equivalent, no-gradient, streaming** — RanPAC is one point in this space |
| **AIR** — Analytic Imbalance Rectifier | [2408.10349](https://arxiv.org/abs/2408.10349) | **the no-gradient family's imbalance guard** (P7.3 — trained-head guards don't apply to a closed-form winner) |
| **RanDumb** (random projection + simple classifier) | [2402.08823](https://arxiv.org/abs/2402.08823) | **the skeptic control** — does the trained bulk even beat a random projection at the readout? (run random-from-taps + random-from-pixels) |
| AnaCP — Analytic Contrastive Projection | [2511.13880](https://arxiv.org/abs/2511.13880) | newest (Nov 2025) "upper-bound CL" analytic head — a stretch reference |
