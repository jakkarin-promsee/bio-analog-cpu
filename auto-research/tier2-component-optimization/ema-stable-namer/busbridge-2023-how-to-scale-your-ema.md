# How to Scale Your EMA
- **Authors / Year / Venue:** D. Busbridge, J. Ramapuram, P. Ablin, T. Likhomanenko, E. G. Dhekane, X. Suau, R. Webb / 2023 / NeurIPS (Spotlight)
- **Link:** https://arxiv.org/abs/2307.13813 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐⭐☆ — the modern theory of the EMA momentum as a *timescale*: it tells us how to set α as a function of how fast the fast track moves — exactly the knob our stable namer needs under drift.

## TL;DR
Treats model-EMA as a genuine **two-timescale** system and derives an **EMA scaling rule**: when you change the fast track's update rate (batch size / step frequency), you must rescale the EMA momentum ρ to preserve the same *effective averaging horizon*. Getting ρ right lets BYOL train at batch size 24,576 without loss.

## The mechanism (how it actually works)
An EMA `y ← ρ·y + (1−ρ)·x` has a characteristic memory length ≈ 1/(1−ρ) *updates*. If each update now covers more data (bigger batch) or arrives at a different rate, the *wall-clock/data* horizon that same ρ implements changes — so to keep the target model's behavior identical you scale ρ so the horizon-in-data is constant. The paper formalizes the fast (optimizer) and slow (EMA) tracks as coupled dynamics and shows the rule that keeps them in step.

## Key results / claims
- A concrete **EMA scaling rule** (rescale ρ with the update rate) preserves training dynamics across batch sizes.
- Enables BYOL at batch 24,576 → ~6× wall-clock reduction (idealized) with no performance drop.
- Validated across architectures, optimizers, modalities; applies to pseudo-labeling and EMA-target SSL.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer (the stable-namer α); the gate/sleep cadence coupling.
- **Same as us:** the EMA "horizon = 1/(1−α) updates" identity is the design equation for a stable namer. It says the anchor's memory length is a *tunable timescale* — and it must be set relative to the drift/rotation rate of the bulk, not picked arbitrarily.
- **Different from us:** they preserve dynamics across *batch size* in a stationary SSL loop; our fast track's "rate" is set by the **drift rate** and the **gate firing frequency**, not batch size. The rule transfers as: **α_stable should scale with the revisit/drift rate** — the same drift-rate-conditional dependency P9 flagged for grid-4 cadence.
- **What we could borrow or test:** derive α_stable from the measured drift rate (Webb-2016 drift-magnitude vocabulary, already carded) so the anchor's horizon spans ~one rotation epoch — making it self-tuning instead of a fixed knob.
- **What contradicts or challenges us:** it reinforces that a *fixed* α is wrong under variable drift — the anchor can silently go stale (too slow) or add no stability (too fast). Any stable-namer experiment must sweep α against drift rate, not report a single α.

## Follow-on leads
- Two-timescale SA (Borkar). BYOL/DINO EMA-target collapse-avoidance. The link between EMA horizon and effective LR-decay (see morales-brotons-2024).
