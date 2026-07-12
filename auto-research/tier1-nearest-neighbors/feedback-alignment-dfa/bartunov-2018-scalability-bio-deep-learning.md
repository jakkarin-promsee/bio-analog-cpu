# Assessing the Scalability of Biologically-Motivated Deep Learning Algorithms and Architectures
- **Authors / Year / Venue:** Sergey Bartunov, Adam Santoro, Blake A. Richards, Luke Marris, Geoffrey E. Hinton, Timothy Lillicrap / 2018 / NeurIPS 2018
- **Link:** https://arxiv.org/abs/1807.04587 (verified via search; NeurIPS proceedings page confirmed)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐⭐ — **the crux paper for us.** The canonical "backprop-free credit assignment fails to scale" result. Its shape is *identical* to our own P4 finding: the gap to backprop grows with task difficulty and structured architecture.

## TL;DR
A careful, matched-budget audit of feedback alignment and target-propagation variants across MNIST → CIFAR-10 → ImageNet. Verdict: they **match backprop on MNIST but fall significantly short on CIFAR and (badly) on ImageNet**, and the shortfall is worst for **locally-connected / convolutional** architectures. This is the reference that pins the ceiling of the whole FA/TP family.

## The mechanism (how it actually works)
Not a new algorithm — a **controlled scaling study**. The authors take FA, DFA, and several target-propagation variants (including a "simplified difference target propagation"), hold the network budget and training protocol fixed, and push each up the difficulty ladder. They test both fully-connected and **locally-connected** (weight-sharing, conv-like) architectures, because the locally-connected case is where a coarse random teaching signal should struggle most.

The finding is a *gap that opens as a function of difficulty*: on MNIST every method is fine; on CIFAR a real gap appears; on ImageNet the biologically-motivated rules "perform significantly worse than backpropagation, especially for networks composed of locally connected units." The exact-gradient direction, it turns out, is what lets backprop coordinate deep, structured, high-class-count problems — and that is precisely what the random-feedback family gives up.

## Key results / claims
- MNIST: FA/TP ≈ backprop.
- CIFAR-10: measurable gap.
- ImageNet: large gap; the family does not keep up.
- **Locally-connected / conv units are the worst case** — weight sharing + a single coarse feedback signal don't mix.
- Interpretation: the alignment that rescues shallow nets is too weak to coordinate very deep / structured / large-scale networks. The cost of dropping the exact gradient is *task-dependent* and grows.

## How it relates to us
- **Organ / phase touched:** the whole positioning of the model; directly mirrors P4 characterization (`phase6-final-architecture.md §4`) and the P11 limit map.
- **Same as us (the lesson):** we independently found the *same shape* — our cell **wins continual / noise / nuisance-robustness and trails on raw static accuracy and many-class** problems, "by design." Bartunov is the published, backprop-adjacent version of the same law: **give up the exact direction and you pay it on the hardest, most structured tasks.** This is external validation that our honest "not a static-accuracy competitor" framing is a *family property*, not a defect unique to SCFF.
- **Different from us:** they measure a *supervised backward-path* family (FA/DFA/TP); we are forward-only + unsupervised. But the ceiling is shared — which is the point.
- **What we could borrow or test:** their matched-budget, difficulty-laddered protocol is essentially what our P10/P11 fair-race + limit-map did. Their locally-connected result is a caution for us: our substrate is *flat-vector* (no weight sharing), which sidesteps the specific conv-conditioning failure (Refinetti card) — a genuine structural difference worth stating.
- **What contradicts or challenges us:** it is the strongest prior that any non-exact-gradient rule will floor on hard structured tasks. Our answer is not "we beat this" — it's "we chose a *different objective* (continual/noise), and we pay for exact direction once in the closed-form namer, not in a random backward path."

## Follow-on leads
- Refinetti 2021 — *why* conv breaks alignment (the conditioning theory).
- Xiao et al. 2018 — sign-symmetry scales better than FA on ImageNet (a partial-transport middle ground).
- Launay 2020 — the counter-narrative: DFA *does* scale to non-conv modern architectures.
