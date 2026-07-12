# Cost-Effective Retraining of Machine Learning Models (Cara)
- **Authors / Year / Venue:** Ananth Mahadevan, Michael Mathioudakis / 2023 (arXiv), Knowledge-Based Systems 2024 / arXiv 2310.04216
- **Link:** https://arxiv.org/abs/2310.04216 (journal: https://www.sciencedirect.com/science/article/pii/S0950705124002454)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate (t2.3 spillover: consolidation cadence)
- **Relevance:** ⭐⭐⭐⭐ — turns "when to sleep" from a fixed grid into an explicit **staleness-cost vs retrain-cost optimization** — the principled replacement for our grid-4.

## TL;DR
Frames retraining as an economic decision: retraining too often burns compute, too rarely accrues a **staleness cost** (lost accuracy on incoming queries). Cara optimizes the trade-off over streams of data *and queries*, approximating staleness online; it matches an offline-optimal retrospective algorithm on synthetic drifts and, on real data, **beats drift-detection triggers with fewer retrainings** — lower total cost.

## The mechanism (how it actually works)
Define a per-window total cost: `retrain_cost` (fixed, paid when you refit) + `staleness_cost` (performance the stale model loses on the queries actually arriving, accumulated since the last refit). The offline oracle (Cara-Opt) plans refits with hindsight; the online algorithm estimates the staleness term from observable surrogates (data change, model scores, query distribution) and refits when accumulated estimated staleness exceeds the retrain cost — a threshold policy (Cara-T variant) over a running debt integral, tuned on offline data. The key reframing vs drift detection: the trigger is **not** "did the world change?" but "**has the change cost me more than a refit costs yet?**" — drift that arrives where no queries land costs nothing and never fires.

## Key results / claims
- Synthetic streams: Cara tracks the retrospective optimum across drift types and retrain-cost regimes.
- Real datasets: better accuracy than drift-detection baselines (DDM-style triggers) **with fewer retraining decisions** — strictly lower total cost.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the sleep cadence (P8.3's grid-8 → P9's grid-4 freeze) + the gate-vs-sleep division of labor; the metered 80/20 (P8.5).
- **Same as us:** the whole economy framing — our energy meter gives us the *actual* retrain cost in pJ, which Cara has to assume; our "firing more forgets more" even adds a term they lack (retraining carries a *forgetting* cost, not just energy).
- **Different from us:** our cadence is open-loop (fixed grid); Cara's is closed-loop on accumulated estimated staleness. P10 mapped our cadence landscape as a plateau with two cliffs (safety plunge at 6→7, accuracy cliff at 15→16) — i.e., on the home stream a fixed grid is nearly optimal, and the upside of adaptivity is bounded. But P11's real arenas (gas drift wins, autocorrelated streams floor) are exactly the non-stationary-rate regimes where a fixed grid mis-spends.
- **What we could borrow or test:** an **error-debt cadence** — integrate the gate's own error-EMA excess (or drift-curve magnitude) between sleeps into a staleness debt; sleep when debt ≥ metered sleep cost. One signal (the error-EMA we already compute) then serves gate, cadence, *and* (per t2.3's InfoRS lead) buffer eviction. Guard rail: the P10 cliff map says any adaptive cadence must never let the effective interval exceed ~6 on the home stream — the debt threshold must respect the safety cliff.
- **What contradicts or challenges us:** their result that drift-triggered retraining is *suboptimal* vs cost-integrated triggering challenges our committed gate→fire design directly: maybe the namer should fire not when DDM trips but when accumulated error-debt clears the metered fire cost. Cheap to test in the frozen P8 harness.

## Follow-on leads
- Regol et al. 2025, "When to retrain a machine learning model" (arXiv 2505.14903) — performance forecasting + cost ratio (carded).
- "Towards Stable Machine Learning Model Retraining via Slowly Varying Sequences" (arXiv 2403.19871) — retrain-stability as a cost term.
- ML-systems staleness literature (model aging curves) for the debt-estimator design.
