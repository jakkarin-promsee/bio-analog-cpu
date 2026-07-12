# Energy-Efficient Deep Learning Without Backpropagation: A Rigorous Evaluation of Forward-Only Algorithms
- **Authors / Year / Venue:** Przemysław Spyra, Witold Dzwinel / 2025 / arXiv:2511.01061 (cs.LG)
- **Link:** https://arxiv.org/abs/2511.01061 (fetched; PDF binary — details from arXiv abstract page + search summary)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐⭐ — the **engineering-native energy audit** of the whole family; directly stress-tests our founding "backward pass is the expensive thing" claim. The single most challenging card here.

## TL;DR
A systematic, measurement-driven comparison of backprop-free training methods (Feedback Alignment, Target Propagation, PEPITA/local-learning, mono-forward-style) against backprop — measuring actual compute, memory, and **energy draw**, not just accuracy. Headline: eliminating the backward pass does **not** automatically save energy — competitive accuracy usually requires energy overhead *elsewhere*, so the theoretical efficiency advantage often does not materialize on real hardware.

## The mechanism (how it actually works)
Not a new algorithm — an evaluation protocol. The authors run each forward-only method and backprop under matched conditions and meter: training FLOPs, peak memory (the activation-tape saving forward-only methods claim), and wall-clock/energy on real hardware configs. They separate the *structural* saving (no transpose, no stored activations) from the *net* saving after accounting for extra forward passes, auxiliary predictors, or more epochs to reach target accuracy.

## Key results / claims
Forward-only methods do remove backprop's backward pass and its activation storage, but to reach competitive accuracy they pay it back — extra forward passes (PEPITA's second pass), per-layer auxiliary heads, or many more training steps. The net energy verdict is skeptical: **for practical accuracy targets, forward-only ≠ energy-efficient by default.** (PDF text did not extract cleanly; specific per-method numbers not transcribed here — abstract/venue confirmed, quantitative table UNVERIFIED in detail.)

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole **cost story** — Phase 8 (the cost meter / 80-20) and Phase 10's honest R1.
- **Same as us:** it agrees with our *own* most honest finding — Phase 10 R1: the **80/20 algorithm alone is 1.5× MORE expensive** than a small tuned ER baseline on the same substrate. Being forward-only did not, by itself, win the energy race for us either.
- **Different from us:** our energy win is **not claimed from forward-only-ness**. It is **substrate-realized**: the analog compute-in-memory crossbar floor (5.4→7.4× in Phase 11) × the depth-gated 80/20. Spyra & Dzwinel meter *digital* forward-only methods, where that substrate floor doesn't exist — so their skeptical verdict is exactly what we'd predict for a digital implementation of us.
- **What we could borrow or test:** their **matched-accuracy energy protocol** is a template for a stronger Stage-2 cost meter (meter to a target accuracy, not per-step) — sharper than our op-count proxy.
- **What contradicts or challenges us:** it is the strongest external "forward-only doesn't save energy" argument. We must never lean on forward-only *per se* for the energy claim — this paper is the citation that forces us to attribute the win to the analog substrate + the gate, and to state the digital-forward-only case honestly.

## Follow-on leads
Matched-accuracy energy benchmarking; memory (activation-tape) savings vs net FLOPs; the analog-substrate exception (compute-in-memory changes the energy calculus); target-propagation and feedback-alignment cost profiles.
