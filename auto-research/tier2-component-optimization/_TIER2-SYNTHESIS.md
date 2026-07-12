# Tier 2 — Component optimization: the rollup

> Machine-swept 2026-07-10 (Fable 5 subagents). Reads the **seven organ-optimization syntheses as one map**: for each
> organ we already have (SCFF bulk · closed-form namer · sleep · gate · read-side), *what the literature has tried that
> we haven't, and how cheaply it fits the substrate*. ~62 verified cards across 7 topics. **Provenance: automation —
> ratify before citing.**

Topics: [SCFF negatives & goodness](scff-negatives-and-goodness/_SYNTHESIS.md) · [closed-form classifier](closed-form-classifier/_SYNTHESIS.md) · [replay & sleep](replay-sleep-consolidation/_SYNTHESIS.md) · [drift-detection gate](drift-detection-gate/_SYNTHESIS.md) · [noise-robust representation](noise-robust-representation/_SYNTHESIS.md) · [prototype-drift compensation](prototype-drift-compensation/_SYNTHESIS.md) · [EMA stable namer](ema-stable-namer/_SYNTHESIS.md)

---

## The one theme that runs through all seven

**The highest-value levers don't add an organ — they reuse a signal we already compute and throw away.** Over and
over the sweep found that the machinery for the "improvement" is already resident:

- the **LUT already stores the prototypes** that would fix our naive random-partner negatives (t2.1);
- the **gate's error-EMA is exactly the "surprise" score** that would drive information-weighted eviction (t2.3);
- the **namer + LUT + sleep already *is* the test-time-adaptation machinery** — just never run awake (t2.5);
- the **Scap already IS an EMA register**, and **`RLSHead` already IS the Gram-EMA** we thought was new (t2.7);
- the **cbrs counters** already carry the per-class counts a diagonal-RDA λ-dial needs (t2.2).

So Tier 2's message is less "bolt on X" and more "you are one wire away from X."

## Two committed P8/P9 decisions the sweep re-opened (future-experiment fuel, per the "separate exps" rule)

1. **The parked tap-drift direction gate (P8) was parked for a non-reason.** "DDM consumes an error rate" is not a real blocker — Page-Hinkley/ADWIN/KSWIN all eat continuous statistics, and Page-Hinkley is a leaky-integrator+comparator (analog-native). *(t2.4)*
2. **grid-4 cadence may be conservative and relaxable.** Two of Harun's four stability-gap fixes are things our closed-form prototype namer already *is*. *(t2.3)* — and a between-sleeps SDC nudge could buy cadence back *(t2.6)*.

## The honest "no"s (as valuable as the wins)

- **Drift-compensation does NOT beat our periodic full re-fit** — sleep re-forwards the raw LUT and re-anchors *exactly* (P9.4 0.787→0.986); SDC/LDC/ADC only *estimate* that ground truth. Use them for between-sleeps cadence relief, not replacement. *(t2.6)*
- **The "stable namer" is partly not novel** — Gram-EMA = RLS-with-forgetting = existing `RLSHead`; and the covariance channel *swells* unless done log-Euclidean. Modest expected gain. *(t2.7)*

---

## Ranked untried levers (the build queue Tier 2 produced)

| Lever | Organ | From | Substrate-fit | What it is |
| ----- | ----- | ---- | ------------- | ---------- |
| **Tap-level activation shifting** (auto-zero at the read amp) | read-side | t2.5 | ★★★ exact, closed-form, no bulk write | The *geometrically exact* fix for the deferred P6/P10 directional (first-moment) residual |
| **Diagonal-RDA head, count-aware λ_c blend** | namer | t2.2 | ★★★ +d/class, one cap row | The tied↔per-class *dial* (our P7.4 FeCAM strike was RDA's λ=0 failure); burst-starved classes auto-collapse to SLDA = A6 guard. *Our composition.* |
| **Information-weighted eviction reusing the gate error** | sleep/LUT | t2.3 | ★★★ reuses error-EMA, no new store | Keep-informative/evict-redundant scored from the namer's own precision; attacks the P11 C=20 crossover |
| **LUT-prototype negatives + Robinson hardness tilt** | SCFF bulk | t2.1 | ★★★ LUT+similarity exist, one multiply | Replaces the most-naive-in-the-literature random-partner negative draw |
| **EMA-of-Gram stable namer** (reuse `RLSHead`) | namer | t2.7 | ★★★ Scap-native | Slow-forgetting RLS anti-recency anchor; mostly a config change |
| **Self-disagreement label-free gate trigger** (STUDD-shaped) | gate | t2.4 | ★★☆ one crossbar read + comparator | Live-vs-last-sleep argmax disagreement feeds the *unmodified* DDM; removes label dependency |
| **SDC-between-sleeps nudge** | sleep | t2.6 | ★★☆ closed-form, bounded | Cadence relief between sleeps (not a re-fit replacement) |
| **VICReg-lite negative-free bulk** | SCFF bulk | t2.1 | ★★☆ variance+invariance cheap; covariance term = open substrate cost | Could delete the InfoNCE negative-supply hardware risk entirely |
| **KLDA (RanPAC-projection → SLDA-statistics)** | namer | t2.2 | ★★☆ RanPAC crossbar cost (P8-metered) | The tied ceiling dissolves in the lifted space at zero per-class storage; the combination P7 never tried |
| **Margin-shaping goodness** (vs `Σh²`) | SCFF bulk | t2.1 | ★★☆ | "In Search of Goodness 2025": the reliable win across 21 goodness functions |

*(★★★ = drops in with resident machinery; ★★☆ = one new bounded piece or an open substrate cost.)*

## Must-cite anchors (Tier 2 ⭐⭐⭐⭐⭐)

SCFF/Distance-Forward + Hyperspherical-FF (negatives) · "In Search of Goodness" 2025 · Friedman RDA 1989 + FeCAM 2023 (the anisotropy dial) · InfoRS 2022 (surprise eviction) · De Lange stability-gap 2023 · FOA 2024 + Schneider 2020 (activation shifting) · SDC 2020 · Polyak-Juditsky 1992 + Arsigny 2006 (averaging soundness).

*(Full table with links + per-paper "relation to us": [`../INDEX.md`](../INDEX.md).)*
