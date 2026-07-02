# P8.3 — The sleep cadence: how often, and on how much history?

**Question.** Inheriting the committed DDM awake gate (P8.1) and the direction trigger (P8.2): what is the **cheapest**
sleep cadence (frequency × LUT-history fraction × EMA-decay λ) that still holds the A6 continual win — i.e. keeps
accuracy-held at the oracle level *and* keeps the worst-point BWT non-negative?

**Setup.** Swept variables = sleep-frequency ∈ {oracle-boundary, grid-2, grid-4, grid-8} × history ∈ {full/λ1.0,
half/λ1.0, qtr/λ1.0, full/λ0.9}. Controls locked (live bulk, RanPAC+cbrs, DDM awake gate, CI+nuisance stream, seeds
[42,137,271,314,1729]). Reference = [oracle-boundary, full] AA 0.448. Figures: CADENCE (AA + worst-BWT heatmaps), INV.

**Run.** 4 frequencies × 4 histories × 5 seeds. Wall ≈ 20.1 min.

**Result / figures.**

*Accuracy-held (median; ref [oracle-boundary, full] = 0.448):*
| cadence \ history | full/λ1.0 | half/λ1.0 | qtr/λ1.0 | full/λ0.9 |
| --- | --- | --- | --- | --- |
| oracle-boundary | 0.448 | 0.416 | 0.356 | 0.448 |
| grid-2 | 0.448 | 0.416 | 0.356 | 0.448 |
| grid-4 | 0.446 | 0.406 | 0.350 | 0.446 |
| **grid-8** | **0.446** | 0.406 | 0.350 | 0.446 |

*Worst-point BWT (median):*
| cadence \ history | full/λ1.0 | half/λ1.0 | qtr/λ1.0 | full/λ0.9 |
| --- | --- | --- | --- | --- |
| oracle-boundary | −0.439 | −0.356 | −0.333 | −0.439 |
| grid-2 | 0.000 | −0.015 | −0.017 | 0.000 |
| grid-4 | 0.000 | −0.015 | −0.061 | 0.000 |
| **grid-8** | **0.000** | −0.058 | 0.000 | **0.000** |

- **CADENCE** (headline): two heatmaps. Accuracy is flat across frequency (0.446–0.448) but collapses with history
  (full→qtr: 0.448→0.356) — the LUT must keep *full* prototype history. Worst-point BWT is 0.000 on the full-history
  column for every *regular grid* cadence but −0.439 for oracle-boundary sleep — regular cadence beats boundary-aligned
  sleep on retention. EMA-decay λ0.9 is identical to λ1.0 (no benefit). Committed knee = **grid-8, full/λ1.0** (cheapest
  regular cadence, sleep-cost 10.0, AA 0.446, worst-BWT 0.000).
  - **INV**: all guards green.

**Read (8 slots).**
1. *Claim* — the cheapest cadence that holds the A6 win is an infrequent regular grid (grid-8) with **full** LUT history
   and **no** EMA decay; boundary-aligned sleep and truncated history both lose retention.
2. *Headline* — grid-8/full AA 0.446 [vs ref 0.448] at worst-BWT 0.000 and sleep-cost 10.0; qtr-history drops AA to 0.350
   and half-history to 0.406 (n=5, live CI+nuisance).
3. *Figures* — CADENCE (AA + worst-BWT heatmaps), INV (guards green).
4. *Mechanism* — sleep re-forwards the raw-prototype LUT through the *current* SCFF and re-solves the namer on *fresh,
   consistent* features. Two findings: (i) **full history is load-bearing** — the drifting bulk means old prototypes,
   re-forwarded now, still define the class boundaries; truncating the LUT throws away classes the stream stopped showing,
   so AA collapses (0.356 at quarter). (ii) **regular cadence beats boundary-aligned** on worst-point BWT (0.000 vs
   −0.439) because the worst mid-stream point falls *inside* a segment (accumulated drift during the long settle/nuisance
   tail), not at a task boundary — a grid that samples the tail catches the dip before it compounds; oracle-boundary sleep
   misses it. (iii) EMA-decay (λ0.9) buys nothing here because the LUT re-forward already re-consolidates from scratch —
   consistent with the drift being slow relative to the sleep interval.
5. *Threats* — (a) the result is explicitly **drift-rate-conditional**: if Phase 9's N2 (EMA-view / drift-slowdown) slows
   the SCFF drift, the cheapest holding cadence must be re-tuned (a slower drift admits a sparser grid; a faster one would
   not). Flagged, not swept here. (b) "cheapest" is on the fire-count/sleep-cost proxy; the energy cost of sleep is the
   P8.4/P8.5 meter's. (c) worst-BWT 0.000 across the full-history grid is a *worst-point* read; post-sleep would look even
   cleaner (and hide the awake gap — which is why P8.6 measures pre-sleep).
6. *Decision* — sets the **committed sleep cadence = grid-8, full LUT history, λ_ema = 1.0** (no decay). This extends S7
   (sleep) from "oracle-boundary" to a detector-driven regular cadence with a pinned history/λ. P8.6 loads this cadence
   for the assembled live run.
7. *Economy-honesty* — cost here is the sleep-count proxy (sleep-cost 10.0 for grid-8); the energy price of a sleep
   re-forward + re-solve is metered in P8.4/P8.5 and attributed to the SCFF (unsupervised re-forward) + namer (solve)
   shares there.
8. *Live-safety / namer* — the committed cadence holds worst-point BWT at 0.000 with full history — the first evidence
   that the *live* loop's retention is intact under a cheap cadence; the assembled A6 gate (P8.6) is the adjudication.
   Namer unchanged pending P8.4.
