# Characterizing Concept Drift
- **Authors / Year / Venue:** Geoffrey I. Webb, Roy Hyde, Hong Cao, Hai Long Nguyen, François Petitjean / 2016 / Data Mining and Knowledge Discovery 30(4):964–994 (arXiv 1511.03816)
- **Link:** https://arxiv.org/abs/1511.03816 (journal: https://link.springer.com/article/10.1007/s10618-015-0448-4)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐ — the seminal formalization of **drift magnitude** as a measured quantity — the vocabulary for upgrading our binary gate to a proportional response.

## TL;DR
The first comprehensive quantitative framework for drift: formal definitions of **drift magnitude** (a distribution distance between concepts at two times), **duration**, and derived quantities (rate/velocity, path), plus a taxonomy (abrupt/gradual/incremental/recurring) rebuilt on these measures instead of informal sketches. The point: "how much and how fast," not just "whether."

## The mechanism (how it actually works)
Fix a distance `D` between joint distributions (they use total variation). Then: **magnitude** of a drift between times `s,t` = `D(P_s, P_t)`; **duration** = the interval over which the concept is in motion; **rate** = magnitude per unit time along the path. Classic drift "types" become regions of this quantitative space (abrupt = large magnitude over short duration, incremental = a long path of small steps, etc.), which makes them measurable and lets detectors/adaptation strategies be matched to the measured regime rather than an assumed one.

## Key results / claims
- First formal, complete taxonomy of drift types with quantitative definitions; identifies ambiguities/omissions in the prior qualitative vocabulary.
- The magnitude/duration framing became the standard for drift *severity* estimation downstream (drift curves, severity-aware adaptation).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the gate (binary today) + the sleep response (fixed-size today); P8.0's drift instrumentation.
- **Same as us:** we already measure a magnitude-like quantity (`bulk_drift` ∈ [0.63, 1.00], P8.0) — but only as an invariant check, not as a control signal. Our drift-rate-conditional caveat (P8's committed cadence "assumes P8.0's measured drift rate") is exactly a Webb-style rate statement made informally.
- **Different from us:** our whole economy is tuned to one measured drift regime; Webb's framework says regimes are a *space*, and P11's arenas proved we live in different corners of it (gas = win, autocorrelated = floor). We have no mechanism that *measures the current regime and adapts*.
- **What we could borrow or test:** (1) **proportional sleep** — size the consolidation (fraction of LUT re-fit, λ_ema, cadence multiplier) by measured drift magnitude-since-last-sleep instead of a fixed grid; the tap-drift statistic integrated between sleeps *is* a path-length estimate of Webb's magnitude, available free; (2) report P11 arenas with measured magnitude/rate coordinates — turning "wins real drift, floors autocorrelated streams" into a *predictive* statement (which regimes we win, as a function of measured drift parameters).
- **What contradicts or challenges us:** none directly — but it exposes that "drift-rate-conditional" is an untracked free parameter in our committed design: nothing in the shipped loop notices if the rate changes mid-deployment (P9's grid-4 fix was found by hand, not by the system).

## Follow-on leads
- Drift-severity-aware adaptation (severity → adaptation-budget mapping).
- Total-variation / Hellinger estimation from samples in embedding space (the analog-cheap estimator question).
- "Understanding concept drift" follow-ups by Webb et al. on cyclic/recurring structure.
