# When to retrain a machine learning model
- **Authors / Year / Venue:** Florence Regol, Leo Schwinn, Kyle Sprague, Mark Coates, Thomas Markovich / 2025 / arXiv 2505.14903
- **Link:** https://arxiv.org/abs/2505.14903
- **Tier / Topic:** tier2 / t2.4 drift-detection gate (t2.3 spillover: consolidation cadence)
- **Relevance:** ⭐⭐⭐⭐ — the newest statement of the retrain-timing problem: **forecast the performance trajectory** instead of detecting shifts, with the retrain-cost ratio explicit in the decision.

## TL;DR
Argues that shift *detection* is the wrong primitive for retrain timing: what matters is the forecast of model performance and the cost ratio between retraining and tolerating degradation. Proposes an uncertainty-based method that **continually forecasts the evolution of model performance** (a bounded metric) and fires retraining when the forecast justifies the cost. Consistently beats baselines (shift detection, offline RL, online-learning formulations) across seven classification datasets.

## The mechanism (how it actually works)
Three named difficulties: few new labeled examples, unknown shift process, unclear cost trade-off. Instead of asking "did the distribution move?", maintain a probabilistic forecast of the accuracy trajectory if you do nothing — fit from the observed history of performance-between-retrains — and compare expected accumulated loss against the retrain cost. Uncertainty matters: the decision uses the forecast *distribution*, not the point estimate, so a noisy-but-plausibly-bad future can justify firing early. The output is a policy tuned to an explicit cost ratio, rather than a detector with an implicit one buried in its thresholds.

## Key results / claims
- Consistently outperforms existing baselines on seven datasets for classification retrain-timing.
- Ablation-level claim: distribution-shift detection alone misses the economics; RL/online formulations miss practical constraints (few labels, expensive exploration).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** gate + sleep cadence as one economic policy; the metered 80/20.
- **Same as us:** the two-cost framing is our economy (GD-share vs staleness); "bounded metric forecast" matches our accuracy-held / worst-BWT instruments; and we hold a card they lack — a *hardware meter* giving the true fire cost in pJ, making the cost ratio a measured quantity instead of an assumption.
- **Different from us:** our DDM gate is a detector with the economics implicit (thresholds tuned once, P8.1); their policy makes the cost ratio a first-class input. Also: they forecast *labeled* performance; we would forecast a label-free surrogate (error-EMA, margin-EMA, or tap-drift magnitude).
- **What we could borrow or test:** (1) a **drift-trajectory forecast on the tap statistic** — our P8.0 result says the direction signal *leads* error by ~8 steps, i.e., today's tap drift is literally a forecast feature for tomorrow's error; regress error-EMA(t+k) on tap-drift(t) in the frozen P8 data and fire on the *predicted* error crossing DDM's own threshold — an anticipatory gate with zero new hardware signals; (2) report our gate as a **policy frontier over cost ratios** (fires vs staleness at each assumed ratio) rather than one committed operating point — a stronger validation artifact.
- **What contradicts or challenges us:** their claim that detection-based triggers are systematically beaten by forecast-based policies is a direct challenge to the committed DDM gate — same challenge as Cara's, from the forecasting side.

## Follow-on leads
- Performance-forecasting / model-aging curves (accuracy decay models under drift).
- Bayesian changepoint + forecast hybrids (run-length posteriors as forecast state).
- Cost-ratio sensitivity analysis as a standard reporting artifact for gated systems.
