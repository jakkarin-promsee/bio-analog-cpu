# Reactive Soft Prototype Computing for Concept Drift Streams (KSWIN)
- **Authors / Year / Venue:** Christoph Raab, Moritz Heusinger, Frank-Michael Schleif / 2020 / Neurocomputing (arXiv 2007.05432)
- **Link:** https://arxiv.org/abs/2007.05432 (KSWIN reference impl. docs: https://frouros.readthedocs.io/en/v0.6.1/api_reference/detectors/concept_drift/auto_generated/frouros.detectors.concept_drift.streaming.window_based.KSWIN.html)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐ — the classic-detector gap-filler: a **distribution-free test on any continuous scalar** — one candidate adapter for shipping our continuous tap-drift statistic through a DDM-style trip.

## TL;DR
The paper's main contribution is a prototype-based stream learner (RRSLVQ), but its detector — **KSWIN** (Kolmogorov–Smirnov Windowing) — became a standard: keep a sliding window of a scalar signal, compare the most recent `r` samples against a uniform sample of the older remainder with a two-sample KS test, and flag drift when the KS distance is significant at a (very small) α. Works on any univariate signal — raw feature, error, margin, or drift statistic — with no distribution assumption.

## The mechanism (how it actually works)
The two-sample KS statistic is the maximum gap between two empirical CDFs — sensitive to *any* distributional difference (mean, variance, shape), not just a mean shift like DDM/ADWIN. KSWIN streams it: window size `w` (~100), recent slice `r` (~30), test per step, α compensated small (~0.005) because the test repeats every step (the multiple-testing correction is folded into α). Detection resets the window. Cost: sorting the window slice per check — cheap digitally, the most expensive of the classic detectors in analog terms (rank/order statistics, not a running mean).

## Key results / claims
- KSWIN is competitive with DDM/ADWIN/EDDM on standard synthetic + real streams as a detector component (evaluated within the RRSLVQ study).
- Adopted as a standard detector in scikit-multiflow / river / frouros — the de-facto non-parametric window baseline.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the gate's detector layer (the committed DDM; ADWIN already bake-off'd at parity in P8.1).
- **Same as us:** window-based two-sample logic on a scalar stream — the same skeleton as ADWIN, which we already validated at the P8.1 knee (FAR 0.000).
- **Different from us:** DDM consumes a Bernoulli error rate; KSWIN consumes **any continuous scalar** — precisely the adapter the unshipped tap-drift trigger lacks. Distribution shape sensitivity could also catch variance-type drift in the tap statistic that a mean-test (ADWIN/Page-Hinkley) misses.
- **What we could borrow or test:** enter KSWIN-on-tap-drift and Page-Hinkley-on-tap-drift as the detector arms of a P8.2-style trigger-shipping bake-off (vs DriftLens-style calibrated threshold and ADWIN). Honest expectation: ADWIN or a calibrated threshold likely wins on substrate cost (running means vs order statistics); KSWIN is the sensitivity ceiling among the cheap detectors.
- **What contradicts or challenges us:** nothing — this is the detector-menu card; the design risk it flags is ours already: per-step repeated testing means the α knob, not the statistic, controls FAR — and FAR burns the 80/20.

## Follow-on leads
- Page-Hinkley (Page 1954, CUSUM family) — the cheapest mean-shift detector: one running mean + one comparator, the most analog-native adapter of all (a leaky integrator + threshold *is* Page-Hinkley).
- HDDM_A/HDDM_W (Frías-Blanco et al. 2015) — Hoeffding-bound detectors, distribution-free with formal FAR guarantees.
- Frouros / river detector zoos — the standardized bake-off harnesses.
