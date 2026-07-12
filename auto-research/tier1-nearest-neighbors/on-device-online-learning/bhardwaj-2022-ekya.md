# Ekya: Continuous Learning of Video Analytics Models on Edge Compute Servers
- **Authors / Year / Venue:** Romil Bhardwaj, Zhengxu Xia, Ganesh Ananthanarayanan, Junchen Jiang, Nikolaos Karianakis, Yuanchao Shu, Kevin Hsieh, Victor Bahl, Ion Stoica / 2022 / USENIX NSDI 2022 (arXiv 2020)
- **Link:** https://arxiv.org/abs/2012.10557 (USENIX page: usenix.org/conference/nsdi22/presentation/bhardwaj)
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐ — the systems-scale version of our gate: retraining as a *scheduled, benefit-estimated* response to data drift, with inference and learning sharing one box.

## TL;DR
Edge-deployed compressed vision models decay under **data drift**; the fix is periodic retraining on fresh data — but retraining and inference must share the same edge GPU. Ekya jointly schedules both across many video streams, using a **micro-profiler** that cheaply estimates *which model would benefit most from retraining*, and prioritizes those. 29% higher accuracy than the baseline scheduler; the baseline needs 4× the GPU to match it.

## The mechanism (how it actually works)
Every retraining window, Ekya must decide: which streams' models get retrained, with what configuration (epochs, layers to tune, data fraction), and how much GPU is left for serving inference. Exhaustively trying configurations would cost more than it saves, so the **micro-profiler** trains a few configurations on a small data sample for a few epochs and extrapolates the accuracy-vs-resource curve per model — an estimate of the *value of learning* before paying for it. A thief-style scheduler then allocates GPU between inference and the retraining jobs with the best estimated accuracy-per-resource, deferring low-value retraining entirely. Drift handling is thus economic: pay for direction where the estimated return is highest.

## Key results / claims
- **29% higher accuracy** than a fair baseline scheduler at equal GPU; baseline needs **4× resources** to match.
- Micro-profiling (few epochs, small sample, extrapolate) is accurate enough to rank retraining candidates at ~1% of the cost of full profiling.
- Established "continuous learning as a scheduling problem" — spawned RECL, DaCapo, EdgeMA and the edge-video-CL line.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate (P8.1) — specifically what our gate *doesn't* have: a value estimate.
- **Same as us:** learning fires as a discrete, budgeted event in response to drift, on the same substrate that serves inference — their retraining window is our gated fire + sleep, their inference/training contention is our SCFF/namer energy split.
- **Different from us:** their trigger currency is **estimated accuracy gain per unit compute** (a benefit forecast), ours is a binary error-EMA threshold (DDM) — we detect *that* drift happened, they estimate *whether fixing it pays*; multi-tenant (many streams compete), cloud-adjacent scale (edge *servers*, not devices); learner is full backprop; no interest in forgetting (each retrain overwrites — the past is disposable in video analytics).
- **What we could borrow or test:** a **benefit-aware gate**: before a gated fire, cheaply estimate expected Δaccuracy from the LUT (e.g., prototype-shift magnitude per class vs namer margin) and skip fires with low expected return — this would push our GD-share below 0.121 with a principled reason, and it is closed-form-compatible (no micro-training needed; our namer's algebra gives the forecast almost free).
- **What contradicts or challenges us:** their world shows drift response can be *purely reactive and stateless* (retrain-and-overwrite) when the past doesn't matter — the continual-safety half of our story only has value where the past must persist; arenas like video analytics would never pay for our LUT.

## Follow-on leads
- RECL (NSDI 2023) — adds a model zoo: *reuse* a historical model instead of retraining (a "hippocampus of whole models").
- AMS (Khani et al.) — remote knowledge distillation for edge model adaptation.
- EdgeMA (arXiv:2308.08717) — lightweight statistical drift detection (GLCM + random forest) triggering adaptation.
