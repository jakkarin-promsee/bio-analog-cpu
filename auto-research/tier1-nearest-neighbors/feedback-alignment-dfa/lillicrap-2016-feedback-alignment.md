# Random synaptic feedback weights support error backpropagation for deep learning
- **Authors / Year / Venue:** Timothy P. Lillicrap, Daniel Cownden, Douglas B. Tweed, Colin J. Akerman / 2016 / Nature Communications 7:13276
- **Link:** https://www.nature.com/articles/ncomms13276 (fetched; DOI 10.1038/ncomms13276)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐☆ — the family root: proves the *weight-transport* objection to backprop is not fatal, which is the exact objection our forward-only rule also answers (by a different route).

## TL;DR
Replace backprop's transposed feedback matrix `Wᵀ` with a **fixed random matrix `B`** that is never updated and never kept in sync with `W`. The network still learns: the forward weights spontaneously **align** so that the random feedback becomes a usable descent direction. This dissolved the "backprop needs symmetric two-way wiring, so it can't be physical" argument.

## The mechanism (how it actually works)
Backprop assigns credit by sending the output error backward through the **transpose of every forward weight**: `δ_l = (W_{l+1}ᵀ δ_{l+1}) ⊙ f'(a_l)`. That `W_{l+1}ᵀ` is the *weight-transport problem* — the backward path must know the exact transpose of the forward path, a degree of two-way coordination no synapse (and no cheap analog crossbar) plausibly has.

Feedback Alignment's move: **freeze a random `B_l` in place of `W_{l+1}ᵀ`** and train anyway: `δ_l = (B_l δ_{l+1}) ⊙ f'(a_l)`. `B` is set once and never touched. Naively this should be noise — the teaching signal points the "wrong way." What actually happens is the phenomenon the method is named for: over training, `W` drifts until it approximately satisfies `W ≈ cBᵀ`, i.e. the angle between the FA update and the true backprop update falls **below 90°**. Once inside 90°, the FA signal is a genuine *descent direction* — every step still reduces loss, just along a slightly different path. The network is not handed the correct signal; it **reshapes its forward weights until the random signal becomes correct enough.** Learning aligns the forward path to the feedback, not the feedback to the forward path.

## Key results / claims
- On MNIST-scale MLPs, FA matches backprop accuracy.
- The load-bearing *positive* result is a diagnostic, not an accuracy number: the **alignment angle stays < 90°**, proving the random signal is a descent direction rather than noise.
- Establishes that "precise, symmetric backward connectivity is not required for effective error propagation" — reopening how a brain (or a transpose-free chip) could use error signals.
- Scope where it holds: shallow / easy tasks. Later work (Bartunov 2018, this folder) shows the alignment is too weak to coordinate deep / structured / large-scale nets — the family's ceiling.

## How it relates to us
- **Organ / phase touched:** the *why-not-backprop* framing under the whole SCFF bulk; the weight-transport argument in `phase6-final-architecture.md §1` and `research/survey/feedback-alignment.detail.md`.
- **Same as us:** we and FA both **reject weight transport** — no transposed crossbar, no keeping a backward path in sync with the forward weights. Both are pitched as substrate-friendly for exactly this reason.
- **Different from us:** FA still **has a backward path** (a random matrix multiply from the error back into each layer) and is **supervised** (needs the global output error). Our SCFF pays **zero backward path** and is **label-free** — the credit is a local windowed contrast, derivative-free, no error broadcast at all. FA removes the *transpose*; we remove the *backward pass*.
- **What we could borrow or test:** the alignment diagnostic (angle-to-true-gradient < 90°) is a clean instrument. If we ever gave the namer or a global-direction nudge a random projection path, this is the check for whether it is a descent direction.
- **What contradicts or challenges us:** nothing directly; FA is a *cousin*, not a rival. Its later ceiling is the load-bearing lesson (see Bartunov / Refinetti cards).

## Follow-on leads
- Nøkland 2016 (DFA) — the direct, parallel version.
- Bartunov 2018 — where FA/TP stop scaling.
- Sign-symmetry (Xiao et al. 2018, "Biologically-Plausible Learning Algorithms Can Scale to Large Datasets") — a middle point between FA and BP that scales better on ImageNet.
