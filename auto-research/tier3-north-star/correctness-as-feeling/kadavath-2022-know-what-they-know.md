# Language Models (Mostly) Know What They Know
- **Authors / Year / Venue:** Saurav Kadavath, Tom Conerly, Amanda Askell, et al. (36 authors, Anthropic) — 2022, arXiv:2207.05221
- **Link:** https://arxiv.org/abs/2207.05221
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐ — the calibration audit of self-knowledge: a trained "do I know this?" head works in-distribution and **silently miscalibrates under distribution shift** — the failure mode our drift-first regime must design against.

## TL;DR
Two self-knowledge probes: **P(True)** — the model looks at its own proposed answer and rates the probability it is correct — and **P(IK)** ("I Know") — a trained head predicting answer-success *before* answering. Large models are surprisingly well calibrated on both, calibration improves with scale and with showing the model several of its own samples first — but **P(IK) partially breaks when transferred to new task distributions.**

## The mechanism (how it actually works)
- **Calibration groundwork:** on multiple-choice with visible options, large models' token probabilities are near-diagonal on calibration plots (stated confidence ≈ empirical frequency). Small models are not — calibration is an emergent, scale-bought property, not free.
- **P(True):** a second pass — "Here is a question, here is a proposed answer. Is the answer true?" — reusing the same weights as a verifier. It works meaningfully *better when the model first sees multiple of its own samples* (the ensemble/consistency context sneaks dispersion information into the judgment — same physics as semantic entropy).
- **P(IK):** a value-head trained with cross-entropy on the model's actual success/failure over a training distribution of questions. In-distribution: well calibrated; responds correctly to relevant context (hints raise P(IK), source material raises it). Out-of-distribution: calibration degrades — the head learned distribution-specific difficulty cues, not a universal self-model.

## Key results / claims
- Self-evaluation via P(True) beats raw answer probability at selecting correct samples across QA/arithmetic/code tasks; the gain grows with model scale and with shown-samples context.
- P(IK) generalizes *partially* across tasks (trained on trivia, transfers imperfectly to math/code) — miscalibration under shift, direction usually over-confidence.
- Everything here is a *magnitude* signal; the paper's honest framing ("mostly") marks the residual as real.

## How it relates to us
- **Organ / phase touched:** the namer's margin as confidence; any future trained critic head; the sleep-recalibration slot; the drift regime (our home).
- **Same as us:** P(IK) is the learned-critic organ the dossier proposes (a small head beside the brain, trained by grounding, fallible). This is that organ built and audited at scale.
- **Different from us:** their world is static — train the head once, deploy. Ours drifts by definition, which is precisely the axis where P(IK) fails. But we own the machinery they lack: **sleep re-fits statistics on schedule.** A P(IK)-style head that is closed-form (ridge/prototype on tap features → success indicator) gets re-anchored at every sleep for free — the P9.4 proto-reanchor move applied to the confidence organ.
- **What we could borrow or test:** (1) the **shown-samples trick** — self-evaluation sharpens when dispersion information is present; our namer margin should likewise be judged *jointly with* re-settle agreement, not alone. (2) The **calibration plot as an invariant**: add "confidence-vs-accuracy diagonal on the current window" to the every-run invariants list once any confidence head exists — miscalibration is the silent failure, so it must be a measured quantity, not an assumption.
- **What contradicts or challenges us:** magnitude confidences (margins, P(IK)) are exactly what P5/P7 struck for spine work — this paper says they're usable but only in-distribution and only re-calibrated. It bounds how much trust the namer's margin deserves between sleeps: full trust just after calibration, decaying with drift distance — the trust horizon should be a function of tap-drift, not time.

## Follow-on leads
- Lin et al. 2022, "Teaching Models to Express Their Uncertainty in Words" — verbalized calibrated confidence.
- OOD calibration / conformal prediction under covariate shift — the statistical repair for the transfer failure.
- Semantic Entropy Probes (Kossen 2024) — the label-free competitor to trained P(IK) heads.
