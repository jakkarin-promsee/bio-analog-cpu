# Align, then memorise: the dynamics of learning with feedback alignment
- **Authors / Year / Venue:** Maria Refinetti, Stéphane d'Ascoli, Ruben Ohana, Sebastian Goldt / 2021 / ICML 2021 (PMLR 139); also J. Stat. Mech. 2022
- **Link:** https://arxiv.org/abs/2011.12428 (fetched)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐⭐ — the **theory of why alignment happens and why it breaks**. This is the mechanistic account of the exact tax any non-exact-gradient rule (ours included) pays for dropping the true direction.

## TL;DR
Feedback alignment learns in **two phases**: an **alignment** phase where the forward weights rotate to make the random feedback approximate the true gradient, followed by a **memorisation** phase where the (now-aligned) network fits the data. The key analytic quantity is the **conditioning of the alignment matrices** — and it is exactly poor conditioning under **weight sharing** that gives a "simple explanation for the well-known failure of DFA to train convolutional networks."

## The mechanism (how it actually works)
Working in solvable (deep linear / two-layer) models, the authors show FA/DFA training decomposes cleanly:

1. **Alignment phase.** Early training is not primarily about fitting the data — it is about the forward weights `W` adapting until the *approximate* gradient (the random-feedback update) aligns with the *true* gradient. This is a **degeneracy-breaking** effect: among all the low-loss configurations the network could reach, FA is pushed toward the subset that also **maximizes gradient alignment**. Alignment proceeds **bottom-up**, layer by layer, from the input side toward the output.
2. **Memorisation phase.** Once aligned, the update is a genuine descent direction and the network spends the rest of training fitting (memorising) the data, like an ordinary net.

The failure mode falls out of the same analysis. Alignment requires the relevant **alignment matrices to be well-conditioned**; data structure controls that conditioning. **Convolution's weight sharing** forces many spatial positions to share one kernel, which wrecks the conditioning of the alignment matrices — so the alignment phase can't complete, and DFA never gets a good descent direction. That is *why* conv is the family's blind spot, not just *that* it is.

## Key results / claims
- Two-phase "align then memorise" dynamics, derived analytically and confirmed on MNIST / CIFAR-10.
- Alignment is a degeneracy-breaking bias toward max-alignment low-loss solutions.
- **Conditioning of alignment matrices** = the master variable; poor conditioning ⇒ poor alignment.
- Weight sharing ⇒ poor conditioning ⇒ **DFA fails on CNNs** — a first-principles explanation of the Bartunov ceiling.

## How it relates to us
- **Organ / phase touched:** the deep SCFF bulk's depth behavior (P2 "depth wall", P5 depth-decay + cure) — the closest theoretical parallel to *our* depth story lives here.
- **Same as us (deep parallel):** our Phase-5 depth-decay is *our* version of "alignment can't complete." SCFF's local objective, like FA's random feedback, is a **non-exact direction**; both compose only until the imperfect signal loses aim. We cured ours with a **sharper objective (InfoNCE τ=0.2) + a bounded window (`w`)**, not with any alignment-to-a-random-matrix. This paper is the reason to describe our fix as "we made the *forward* objective carry the direction," structurally different from "we let the weights align to a random backward matrix."
- **Different from us:** FA has an *explicit alignment phase* (forward weights chase a random `B`); our forward-only contrast has **no `B` to align to** — there is no backward matrix at all. So we escape the conditioning failure by construction, but we pay a *different* tax (objective-locality decay), which we measured and cured.
- **What we could borrow or test:** the **conditioning of alignment matrices** is a diagnostic we could adapt — measure the conditioning of our per-window credit and check whether our depth-decay correlates with it. And the "no weight sharing ⇒ good conditioning" result reinforces that our **flat-vector substrate is on the *good* side of this line.**
- **What contradicts or challenges us:** it warns that *any* non-exact rule has a regime where its imperfect direction can't be repaired by more training — a caution against over-claiming that our τ/`w` cure generalizes past the flat, constructed tasks we tested it on.

## Follow-on leads
- Deep-linear-net learning-dynamics theory (Saxe et al.) — the machinery this builds on; a lens for our own depth-decay.
- "How and When Random Feedback Works: low-rank matrix factorization" (arXiv 2111.08706) — adjacent theory of when alignment succeeds.
- Conditioning-based diagnostics for local/forward objectives — a possible instrument for our bulk.
