# Exemplar-free Continual Representation Learning via Learnable Drift Compensation (LDC)
- **Authors / Year / Venue:** Alex Gomez-Villa, Dipam Goswami, Kai Wang, Andrew D. Bagdanov, Bartłomiej Twardowski, Joost van de Weijer / 2024 / ECCV 2024
- **Link:** https://arxiv.org/abs/2407.08536 (Springer: https://link.springer.com/chapter/10.1007/978-3-031-72667-5_27)
- **Tier / Topic:** tier2-component-optimization / t2.6 prototype drift compensation
- **Relevance:** ⭐⭐⭐ — SDC's successor that works on *unsupervised/SSL backbones* (our bulk's regime), but pays with a gradient-trained projector — the exact "new trained organ" our P9 planning already declined.

## TL;DR
SDC's weighted-average transfer assumes the drift field is smooth; on hard drift (and on self-supervised backbones) it isn't. LDC instead *learns* the map from old feature space to new: a small projector trained to align current-data features across the two backbones, then applied to stored prototypes. Works on supervised and unsupervised backbones; the paper's headline diagnosis is ours: forgetting is prototype drift, not lost discriminative power.

## The mechanism (how it actually works)
1. After training the backbone on task t (old backbone f_{t−1} kept temporarily), train a small projector P_t by gradient descent to minimize ‖P_t(f_{t−1}(x)) − f_t(x)‖ over current-task data x — i.e. regress the coordinate change of feature space, using only data you legally have.
2. Push every stored old prototype through it: μ_c ← P_t(μ_c). Discard f_{t−1} and P_t.
3. Because P_t is fit as a *function* rather than a kernel-smoothed average, it can capture drift that is class-dependent and non-smooth — including the messier drift of self-supervised training, where SDC's assumption breaks worst.
4. Plugs on top of any prototype-based CL method; also yields the first exemplar-free *semi-supervised* continual learner (labels only needed for prototypes, not the backbone).

## Key results / claims
- State-of-the-art among exemplar-free prototype-compensation methods in supervised and semi-supervised settings across standard benchmarks.
- The enabling claim (measured, echoing Davari 2022): the backbone's discriminative power survives sequential training; accuracy loss is recoverable by fixing the *prototypes' coordinates* — compensation, not retraining.
- Explicitly validated on moving *unsupervised* backbones — the setting SDC was never tested in.

## How it relates to us
- **Organ / phase touched:** sleep re-fit / stored prototypes; the N2 decision (P9.1); the P9 deep-research-delta already names LDC by arXiv id.
- **Same as us:** the diagnosis is our P9.0 verdict verbatim (representation rotates, head statistics rot). And it is the only compensation paper in this line tested on an *unsupervised* continuously-trained backbone — structurally the closest to SCFF's endogenous drift.
- **Different from us:** the compensator is a gradient-trained module with its own optimizer, epochs, and a second backbone kept in memory during fitting. Our P9 planning saw exactly this (deep-research-delta D1) and declined: "a learned projector is a new trained organ." We instead re-anchor from the raw LUT — no learned map, no second model copy.
- **What we could borrow or test:** the *shape* of the idea without the gradient: a linear P_t fit closed-form (least squares on (stored-LUT-feature-at-last-sleep, current-LUT-feature) pairs — ridge regression, one solve) would be a substrate-legal LDC. That is worth one cell only if plain SDC-weighted transfer fails on our drift; it costs a small feature cache (features of LUT items at last sleep) but zero extra forwards at fit time if fit *at* sleep, or a probe-batch re-forward if fit between sleeps.
- **What contradicts or challenges us:** their evidence that kernel-smoothed transfer (SDC) underperforms a fitted map on SSL backbones warns that our cheapest lever (SDC-style nudge) may be too blunt for SCFF drift — the bake-off must include both.

## Follow-on leads
- EMA-based representation note the P9 delta flagged alongside LDC: arXiv:2411.18704 (EMA representations more general under drift).
- ADC (CVPR 2024) — the other post-SDC estimator (carded here).
- Continual SSL line: CaSSLe, POCON (both carded t1.7) — same authors' group, the backbone-side view of the same drift.
