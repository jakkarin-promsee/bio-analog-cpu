# Planning to Explore via Self-Supervised World Models (Plan2Explore)
- **Authors / Year / Venue:** Ramanan Sekar, Oleh Rybkin, Kostas Daniilidis, Pieter Abbeel, Danijar Hafner, Deepak Pathak — 2020, ICML, arXiv:2005.05960
- **Link:** https://arxiv.org/abs/2005.05960
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐ — the engineering-grade curiosity signal: **ensemble disagreement** isolates *learnable* ignorance from unlearnable noise, and it self-anneals — the anti-collapse upgrade to raw prediction error.

## TL;DR
An agent explores with no task reward by seeking states where an **ensemble of one-step latent predictors disagrees** — an estimate of epistemic uncertainty (expected information gain). It plans *toward expected future disagreement* inside a learned world model (Dreamer), rather than reacting to novelty after the fact. The reward vanishes automatically where data accumulates. Zero/few-shot downstream performance nearly matches an oracle trained with task rewards.

## The mechanism (how it actually works)
Three parts:
1. **A latent world model** (RSSM) learned from experience — the imagination substrate.
2. **The intrinsic signal:** K small one-step forward models, trained on the same experience with different initializations/minibatches, each predicting the next latent embedding. The intrinsic reward at a state-action = **variance across the K predicted means.** Why this and not prediction error: raw error = epistemic (reducible, "I haven't learned this yet") + aleatoric (irreducible noise, the "noisy-TV" trap). Ensemble-mean disagreement estimates only the epistemic part — members converge as data arrives even if the world stays noisy, so the agent is never hooked on chance.
3. **Planning for expected novelty:** the policy is optimized *in imagination* to maximize future disagreement — it goes where learning will be possible, instead of wandering until novelty is stumbled upon.

The self-annealing property is the grounding: disagreement is *defined* to shrink under data. It cannot be maximized forever at one spot; the signal burns itself out exactly when learning succeeds — the built-in anti-delusion.

## Key results / claims
- DM Control Suite from pixels, zero task reward during exploration: state-of-the-art unsupervised exploration; **zero-shot** task performance close to (sometimes matching) Dreamer trained *with* rewards.
- Few-shot adaptation (~100–150 reward episodes) beats prior curiosity methods (ICM, etc.).
- One exploration run transfers to *multiple* downstream tasks — the learned model is task-general.

## How it relates to us
- **Organ / phase touched:** the gate as learn-trigger; the north-star curiosity twin (dossier names ICM/Schmidhuber — this is its sturdier successor); the P6 all-noisy-stream regime.
- **Same as us:** the dossier already argues prediction-error-in-learned-feature-space; Plan2Explore's correction is on the same axis but sharper — measure error *dispersion across replicas*, not error magnitude. Dispersion-not-magnitude is our spine rule appearing independently in RL exploration.
- **Different from us:** they buy K predictor replicas; we won't replicate the bulk. But cheap partial ensembles exist in our object already: the per-depth taps are K *views* of the same input, and the namer can read each tap separately — inter-tap disagreement on the named class is a free ensemble-ish signal. (P8.2's tap-drift is a temporal cousin: disagreement of now-vs-anchor rather than member-vs-member.)
- **What we could borrow or test:** **gate learning on epistemic, not raw, error.** The deployed gate fires on error-EMA (raw error) — under a permanently noisy stream it would see permanent error and fire forever (the P8 "always-pay −0.137" failure is the static version of this trap). The upgrade: fire when *disagreement among taps/anchors* is high (something learnable moved), stay quiet when error is high but agreement is stable (irreducible noise — nothing to learn). This is a concrete, closed-form-computable refinement of "firing more forgets more."
- **What contradicts or challenges us:** the signal needs genuinely diverse replicas; our taps are trained jointly, so their disagreement may be correlated (Huang-card warning: clones are not independent evidence). The diversity of the tap ensemble is a measurable pre-condition — check it before trusting the signal.

## Follow-on leads
- Pathak et al. 2019, "Self-Supervised Exploration via Disagreement" — the model-free original of the disagreement reward.
- Schmidhuber 1991/2010 compression-progress — the theory ancestor (already in the dossier; learning-*progress*, not error level, is the reward).
- Sancaktar et al. 2022, CEE (curious exploration via structured world models) — disagreement + planning in object-centric models.
