# Measuring the Carbon Intensity of AI in Cloud Instances
- **Authors / Year / Venue:** Jesse Dodge, Taylor Prewitt, Remi Tachet des Combes, Erika Odmark, Roy Schwartz, Emma Strubell, Alexandra Sasha Luccioni, Noah A. Smith, Nicole DeCario, Will Buchanan / 2022 / ACM FAccT 2022
- **Link:** https://arxiv.org/abs/2206.05229 (fetched)
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐ — the measured-not-estimated training-energy exemplar (up to a 6.1B-param pretraining), and the source of the marginal-vs-average and "the denominator matters" subtleties that a careful energy reviewer raises.

## TL;DR
Instruments real training runs on Azure to measure operational energy and carbon, up to pretraining a 6.1B-parameter LM. Shows carbon depends heavily on *where* and *when* you run (region 7k vs 26k gCO₂ for the same job) and argues for **marginal**, time-and-location-specific emissions accounting rather than a single average factor.

## The mechanism (how it actually works)
Rather than estimate from FLOPs, they log actual instance energy and multiply by *marginal* grid carbon intensity (the emissions of the last generator dispatched, which is what your extra load actually causes) at the specific place and time — not a national average. The methodological upshot for benchmarking: (1) *measure* the energy, don't derive it from FLOPs; (2) energy and carbon are different quantities — energy is the hardware-agnostic invariant, carbon is a context multiplier that can swing several-fold with region/time; (3) therefore an energy *comparison* between algorithms should be made in energy (joules), holding the deployment context fixed, and carbon reported separately as context.

## Key results / claims
- Region choice can change a job's emissions ~3–4× (7k vs 26k gCO₂); time-of-day is a secondary but real lever.
- Demonstrates end-to-end measurement at large training scale (6.1B params).
- Advocates marginal, granular accounting and direct measurement over average-factor estimation.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the write-up discipline for any P8/P10/P11 energy claim; the separation of the hardware-invariant quantity from context multipliers.
- **Same as us:** the paper's cleanest lesson maps onto our discipline — compare *algorithms in joules on a fixed substrate* (our "same-substrate cut" is the load-bearing claim), and treat the substrate/context factor separately. Our P10 R1 already does this: same-substrate joules (algorithm) vs the analog-substrate multiplier are reported as *two* quantities, never fused.
- **Different from us:** their context multiplier is the electricity grid; ours is the analog substrate. But the structure is identical — a hardware-invariant algorithm-energy times a context/substrate factor. This is a useful rhetorical template: "grid intensity is to Dodge as substrate factor is to us."
- **What we could borrow or test:** borrow the *reporting shape* — one algorithm-energy number (matched accuracy, same substrate) + one clearly-labelled multiplier (the analog floor), never multiplied into a single headline that hides which factor did the work. We essentially already do this; Dodge is the citation that it is the correct, review-surviving shape.
- **What contradicts or challenges us:** Dodge's authority comes from *measuring real joules*; we model them. A reviewer can say our "same-substrate joules" are themselves modeled ratios, not measured. Our defence is the same as for Henderson/MLPerf: relative ratios under one transparent model, absolute joules deferred.

## Follow-on leads
- Luccioni et al. "Power Hungry Processing" (2024) — measured inference energy across many tasks/models; the modern measured-energy corpus.
- Marginal vs average emission factors — relevant only if we ever attach a carbon number; for our energy claim, joules-at-fixed-context is the right invariant.
