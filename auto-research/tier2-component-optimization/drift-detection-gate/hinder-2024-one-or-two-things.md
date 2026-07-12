# One or two things we know about concept drift — a survey on monitoring evolving environments (Part A: detecting concept drift)
- **Authors / Year / Venue:** Fabian Hinder, Valerie Vaquet, Barbara Hammer / 2024 / Frontiers in Artificial Intelligence 7:1330257 (arXiv 2310.15826)
- **Link:** https://arxiv.org/abs/2310.15826 (journal: https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1330257/full)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐⭐⭐ — the mathematical survey of **unsupervised** drift detection, and the source of the field's sharpest objection to feature-drift gates: without labels you cannot tell *harmful* drift from *harmless* drift. Our P8.2 nuisance test is precisely an answer to this objection.

## TL;DR
The definitive unsupervised-monitoring survey (most prior surveys assume labels). Gives precise mathematical definitions of drift, a taxonomy of label-free detectors (two-window distribution tests, block-based statistics, model-loss surrogates), standardized experiments comparing strategies on parametric datasets, and usage guidelines. Its running theme: distribution change ≠ performance change, so a label-free detector inherits an unavoidable false-alarm class unless the statistic is conditioned on what the model actually uses.

## The mechanism (how it actually works)
The organizing frame: drift is `P_t(X,Y)` changing over time; unsupervised detectors only see `P_t(X)`. Nearly all label-free detectors reduce to a **two-window scheme** — a reference window vs a sliding recent window, compared by a statistic (KS per feature, MMD, classifier two-sample tests like D3, density ratios), with a threshold from the statistic's null distribution. The taxonomy sorts them by *what statistic* and *what window management*. The key theoretical remark: only drift in `P(Y|X)` — or drift in `P(X)` in regions that move mass across the decision boundary — hurts accuracy; drift confined elsewhere ("virtual drift") is harmless, and no `P(X)`-only detector can distinguish the two. Practical consequence pushed by the authors: unsupervised detection is best framed as *monitoring* (is the world changing? where?) rather than a pure retrain trigger, or the statistic must be model-conditioned to regain relevance.

## Key results / claims
- Standardized head-to-head experiments across two-window detectors on parametric artificial data — no universal winner; sensitivity is governed by the statistic-vs-drift-geometry match.
- Formal argument that harmful-vs-harmless discrimination is impossible from `P(X)` alone.
- Companion piece (Part B, localization) extends to *where* the drift lives — feature/region attribution.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate as a *safety* mechanism (firing more forgets more) — FAR is our load-bearing axis, and this is the survey of exactly that failure class.
- **Same as us:** their harmless-drift false-fire class is our **nuisance covariate shift** (`g·x + α·1`); their conclusion that raw-`P(X)` statistics false-fire is our magnitude-null result (FAR 0.938).
- **Different from us:** the survey treats "condition the statistic on the model" mostly via loss surrogates; our tap-drift trigger conditions **geometrically** — project feature drift onto the namer's class directions, so nuisance components (removed by SCFF's input layernorm, orthogonal to class structure) cancel. That is a *third way* the taxonomy does not name: supervised-subspace-projected feature drift.
- **What we could borrow or test:** (1) the **two-window + null-distribution threshold discipline** for our continuous tap statistic (an interpretable FAR knob, per ADWIN's δ); (2) their standardized parametric drift geometries as extra nuisance nulls beyond our single covariate shift; (3) the monitoring-vs-trigger split — a cheap always-on feature monitor (bookkeeping) + a strict gate (spending), two thresholds on one statistic.
- **What contradicts or challenges us:** the impossibility argument is the strongest published reason our **unshipped direction trigger could false-fire on drift types our one nuisance test never probed** (e.g., within-class density shifts along class directions). Before shipping the tap-drift gate, it owes a broader nuisance battery — this survey supplies the geometries.

## Follow-on leads
- Part B of the same survey (drift localization/explanation) — class-conditional partial sleep.
- Hinder et al., "Suitability of Different Metric Choices for Concept Drift Detection" (arXiv 2202.09486).
- "Adversarial Attacks for Drift Detection" (arXiv 2411.16591) — how detectors are fooled; a red-team menu for our gate.
