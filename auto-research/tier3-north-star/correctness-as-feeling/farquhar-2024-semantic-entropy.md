# Detecting Hallucinations in Large Language Models Using Semantic Entropy
- **Authors / Year / Venue:** Sebastian Farquhar, Jannik Kossen, Lorenz Kuhn, Yarin Gal — 2024, **Nature 630, 625–630** (mechanism paper: Kuhn, Gal & Farquhar, "Semantic Uncertainty," ICLR 2023 Spotlight, arXiv:2302.09664)
- **Link:** https://www.nature.com/articles/s41586-024-07421-0 · https://arxiv.org/abs/2302.09664
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐⭐ — the strongest label-free confidence signal in the field is a *dispersion over re-runs, measured in an invariance-respecting space* — a recipe our substrate can run physically (noise re-settles + namer agreement).

## TL;DR
Sample the model several times, cluster the samples into groups that *mean the same thing* (bidirectional entailment), and take the entropy over meaning-clusters. High semantic entropy = the model is confabulating (its answer is an arbitrary draw); low = the answer is stable under resampling. Unsupervised, no architecture change, and it beat every baseline at detecting wrong answers (AUROC 0.790 vs 0.691 for naive token entropy) across five datasets and multiple model families.

## The mechanism (how it actually works)
The core insight is *where* to measure uncertainty. Token-level entropy is contaminated by harmless variation ("Paris" vs "It's Paris"). So:
1. **Sample** M answers to the same question (temperature sampling — injected noise).
2. **Cluster by meaning:** two answers land in one cluster iff each textually entails the other (checked with an NLI model). This quotients out the invariances — different surface forms, same content.
3. **Entropy over clusters** (estimated from cluster probabilities or counts): the uncertainty that remains is uncertainty *about the content*.

Why it works as a self-signal: a model that knows the answer returns to the same meaning from many random starts; a model that doesn't lands somewhere different each time. Correctness shows up as **stability of the answer under perturbation**, not as the magnitude of any single-run score. The signal needs no labels — its grounding is the *structure of agreement itself*, which is expensive to fake: to fool it, the model would have to be consistently wrong the same way across independent noisy runs.

## Key results / claims
- AUROC 0.790 averaged over TriviaQA, SQuAD, BioASQ, NQ-Open, SVAMP with LLaMA-2, Falcon, Mistral — beating naive entropy (0.691) and a *supervised* embedding-regression baseline; generalizes to unseen tasks without retraining.
- Refusing to answer the highest-entropy questions substantially raises accuracy on the rest — i.e., it works as a **halt/abstain gate**, not just a diagnostic.
- Cost: M extra forward passes (typically 5–10) — the price of the signal is repetition, not new machinery.

## How it relates to us
- **Organ / phase touched:** the north-star halt; the settling loop; the namer; the substrate's thermal noise (P6/18-analog-noise).
- **Same as us:** dispersion-not-magnitude is our spine discipline said in their vocabulary — P5/P7 struck confidence-magnitude selectors; this is the field's strongest evidence that the *reliable* self-signal is a distribution shape, not a scalar height.
- **Different from us:** their perturbation source is temperature sampling and their equivalence check is an NLI model. Ours are both cheaper: the substrate has **physical noise for free**, and the namer's discrete output *is* the equivalence classing (two settles "mean the same" iff the namer reads the same class).
- **What we could borrow or test:** the buildable analog — **re-settle agreement**. Run the settling loop k times from the same input with the substrate's own noise (or tiny input jitter); read the namer each time; the confidence = the agreement fraction (or entropy) over named outcomes. Computable today from planned parts: settle → name → count. It is exactly semantic entropy with physics as the sampler and the namer as the entailment check. Halt rule: think/re-settle until agreement crosses the (sleep-calibrated) threshold — an anytime loop where *stability of the answer* is the feeling.
- **What contradicts or challenges us:** k re-settles cost k× settle energy — the meter must price the feeling (their M=10 would be a nontrivial energy multiplier; the experiment should find the smallest useful k). And it detects *arbitrary-draw* wrongness, not systematic wrongness — a consistently-biased namer sails through confidently wrong (their "confabulation ≠ all hallucination" scoping); grounding events remain necessary.

## Follow-on leads
- Kossen et al. 2024 — Semantic Entropy Probes (predict SE from hidden states, amortizing the k samples — the "cheap learned shadow of the expensive signal" trick).
- Self-consistency (Wang et al. 2022, arXiv:2203.11171) — majority-vote agreement as accuracy booster; the decision-side twin of this diagnostic.
- Plan2Explore's ensemble disagreement (this folder) — the same dispersion idea at *training* time for what-to-learn.
