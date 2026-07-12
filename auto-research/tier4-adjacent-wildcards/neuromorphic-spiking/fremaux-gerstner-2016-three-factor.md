# Neuromodulated STDP, and Theory of Three-Factor Learning Rules
- **Authors / Year / Venue:** Nicolas Frémaux, Wulfram Gerstner / 2016 / Frontiers in Neural Circuits 9:85
- **Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4717313/ (DOI: 10.3389/fncir.2015.00085)
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐ — the theory that names the whole family: `Δw = f(pre, post, modulator)`. Our "local SCFF signal + a global gate/error modulator" is a three-factor rule in disguise; this is the citation for *why* an eligibility trace + a broadcast third factor is the general online-learning primitive.

## TL;DR
Formalizes neuromodulated plasticity as a **three-factor rule**: weight change is a function of presynaptic activity, postsynaptic state, **and a third global factor** (a neuromodulator like dopamine) that is generated neither by the synapse nor by its neurons. The eligibility trace is the bridge that lets a *delayed* third factor still act on the *right* synapse — the mathematical core reused by e-prop, R-STDP, and TD-learning-as-plasticity.

## The mechanism (how it actually works)
Classical Hebbian/STDP is two-factor: `ẇ = H(pre, post)`. That cannot learn a task, because coincidence alone doesn't know whether the coincidence was *good*. Frémaux & Gerstner add a third factor M (a global scalar broadcast signal):

`ẇ = F(M, pre, post)`

The engineering move is the **eligibility trace**: the pre×post coincidence does *not* immediately change the weight; it deposits a decaying trace `ė = −e/τ_e + H(pre, post)`. The actual weight change waits for the modulator: `ẇ = M(t) · e(t)`. So a reward/error arriving *hundreds of ms to seconds later* still finds the synapses that were eligible — solving the "distal reward" temporal-credit problem without storing history.

Three canonical instantiations of M:
- **R-STDP (covariance):** `M = R − ⟨R⟩` (reward minus baseline) — subtracting the mean is *required*, or the rule just potentiates everything.
- **TD-STDP:** `M = δ_TD` (temporal-difference error) — value learning as plasticity.
- **R-max (policy gradient):** M derived from a reward-maximization objective.

Functional requirements it pins down: the trace must persist on the modulator's timescale; the third factor must be able to *reverse* sign (reward → LTP, punishment → LTD); and an upstream "critic" is needed to turn raw reward into a useful `R − ⟨R⟩`.

## Key results / claims
- Unifies R-STDP, TD-learning, and policy-gradient as one three-factor family — they differ only in what the third factor *is*.
- Establishes the mean-subtraction (baseline) requirement as non-optional for reward-modulated learning.
- Frames eligibility-trace + neuromodulator as the general solution to delayed credit assignment in spiking nets.

## How it relates to us
- **Organ / phase touched:** the **DDM error-EMA gate** + the namer (the "third factor" analogue); the north-star loop's learning rule.
- **Same as us:** our loop already *has* a three-factor shape — a local SCFF/contrastive signal (pre×post-like), plus a **global broadcast modulator** (the drift gate on the namer's error-EMA decides *when* learning fires). The gate is our "third factor"; the error-EMA is our eligibility-like trace.
- **Different from us:** their third factor is a *reward/TD error* driving *gradient-like* weight changes at every eligible synapse; ours gates a *closed-form* namer re-fit, not a per-synapse update. Our bulk is unsupervised contrastive, not reward-modulated. We use the modulator to schedule (safety gate), not to sign-correct every weight.
- **What we could borrow or test:** the **mean-subtraction / baseline** insight is a clean, testable idea for our gate — is our error-EMA gate implicitly a "reward-minus-baseline"? Also: their "reversal" requirement (the third factor must be able to flip LTP↔LTD) is the *direction* problem that killed draft 5 — a three-factor rule is one principled way a broadcast signal can carry *sign*, not just magnitude.
- **What contradicts or challenges us:** three-factor rules are inherently *reinforcement/error-driven per synapse*. We deliberately avoid per-synapse direction in the bulk. This paper is the reminder that the field's answer to "cheap global credit" is a *signed* modulator times a trace — i.e. it insists direction must be broadcast, which is exactly the thing we route around with a closed-form namer.

## Follow-on leads
- Gerstner et al. 2018 "Eligibility traces and plasticity on behavioral time scales" (Front. Neural Circuits) — the experimental support for behavioral-timescale traces.
- Bellec 2020 e-prop — the deep-learning-grade descendant (sibling card).
- Roelfsema & Holtmaat 2018 "Control of synaptic plasticity in deep cortical networks" — three-factor as a backprop alternative in deep nets.
