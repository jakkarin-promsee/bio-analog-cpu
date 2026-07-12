# Detecting Concept Drift With Neural Network Model Uncertainty (UDD)
- **Authors / Year / Venue:** Lucas Baier, Tim Schlör, Jakob Schöffer, Niklas Kühl / 2021 (arXiv), HICSS 2023 / arXiv 2107.01873
- **Link:** https://arxiv.org/abs/2107.01873
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐⭐ — label-free gate on the **model's confidence** instead of its error; our SLDA namer computes the needed margin for free at every naming.

## TL;DR
UDD detects drift without labels by monitoring the **predictive uncertainty** of the deployed network (via Monte Carlo Dropout) and running **ADWIN on the uncertainty stream**; a trip triggers retraining. Because the signal is model-conditioned (not raw input statistics), it avoids "unnecessary retrainings" on input changes the model doesn't care about. Outperforms state-of-the-art strategies on 12 datasets, classification and regression.

## The mechanism (how it actually works)
The chain is: input → model → uncertainty scalar → change detector → retrain. MC-Dropout supplies the uncertainty (variance across stochastic forward passes); the philosophy is that when the world drifts into regions the model wasn't fit on, its confidence degrades *before/without* labels arriving. ADWIN — an adaptive two-window mean test with a false-positive-rate parameter δ — consumes the scalar stream and trips when the recent mean uncertainty differs significantly from the historical mean. The load-bearing design argument (their words): monitor "the effects of the current input data on the properties of the prediction model rather than detecting change on the input data only," because input-only detection "can lead to unnecessary retrainings."

## Key results / claims
- Beats state-of-the-art retraining strategies on 2 synthetic + 10 real-world datasets, both task types.
- Explicit two-axis accounting: accuracy gained vs number of retrainings paid — the same economy framing as our 80/20.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate signal (P8.1/P8.2); the economy (P8.5 — every false fire burns the 80/20).
- **Same as us:** the whole argument structure — retraining is the expensive act; the trigger must be model-conditioned to avoid paying on nuisance input change; the detector layer is off-the-shelf and the *signal* is the contribution.
- **Different from us:** MC-Dropout needs many stochastic forward passes — expensive and awkward on our substrate. But our namer is a **prototype/Gaussian classifier**: the margin (top-1 minus top-2 discriminant) and the Mahalanobis-style distance to the nearest prototype are *closed-form uncertainty*, already computed at every naming step. No sampling, no extra passes.
- **What we could borrow or test:** a **margin-EMA gate** — feed the per-step SLDA margin (or nearest-prototype distance) to ADWIN/Page-Hinkley in the P8.2 harness. Prediction: earlier than the labeled error (confidence sags before the argmax flips → before errors register), label-free, and nuisance-robust (a pure covariate magnitude shift that layernorm removes leaves margins untouched). Sits between the error-EMA (late, labeled) and tap-drift (earliest, feature-level) on the MTD axis.
- **What contradicts or challenges us:** uncertainty degradation assumes drift lowers confidence — a rotation of class directions that keeps clusters tight (our benign P9.0 rotation) can keep margins high while the *labels* go stale; margin gating alone could under-fire there. Pair with the sleep-refresh, or cross-check with disagreement (STUDD-shaped).

## Follow-on leads
- Prediction-confidence drift detectors without dropout (softmax-entropy streams).
- Selective-prediction / reject-option literature — margins as risk proxies.
- ADWIN's δ as the single interpretable FAR knob for all our continuous signals.
