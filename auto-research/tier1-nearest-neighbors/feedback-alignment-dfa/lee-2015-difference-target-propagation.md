# Difference Target Propagation
- **Authors / Year / Venue:** Dong-Hyun Lee, Saizheng Zhang, Asja Fischer, Yoshua Bengio / 2015 / ECML/PKDD 2015 (arXiv 1412.7525, 2014)
- **Link:** https://arxiv.org/abs/1412.7525 (fetched)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐☆☆ — the **target-propagation** branch of the backprop-free family. Included as the *contrast*: it keeps a backward-ish path but makes it a **trained inverse**, which is the opposite trade from FA's *fixed random* path — and a costlier one than ours.

## TL;DR
Instead of propagating error *gradients* backward, propagate **targets**: for each layer, compute what its activation *should have been* to reduce the loss, using **trained autoencoder inverses** to carry targets from layer `l+1` down to layer `l`. The "difference" trick adds a **linear correction** for the fact that those learned inverses are imperfect, which is what makes the method actually work.

## The mechanism (how it actually works)
Target propagation reframes credit assignment: rather than "here is the gradient direction," each layer is handed a **target activation** `ĥ_l` and trains its forward weights to move its output toward that target — a *local* supervised problem per layer. Targets are carried downward by **per-layer inverse functions** `g_l` (decoders of an autoencoder trained to invert the forward map `f_l`). Because a learned inverse is never exact, naive target prop is unstable. **Difference** target propagation corrects it: instead of `ĥ_l = g_l(ĥ_{l+1})`, it uses `ĥ_l = h_l + g_l(ĥ_{l+1}) − g_l(h_{l+1})` — a **linear difference correction** that cancels the inverse's reconstruction error to first order. With that correction, target prop matches backprop on deep nets and reaches SOTA on stochastic/discrete-unit networks (its natural home — targets, unlike gradients, pass fine through discrete units).

## Key results / claims
- Difference correction is what makes target propagation viable — plain TP is too unstable.
- Comparable to backprop on deep continuous nets; **state-of-the-art on stochastic networks** and networks with discrete units.
- Requires a **trained feedback pathway** (the autoencoder inverses) — the opposite design choice from FA/DFA's fixed-random feedback.

## How it relates to us
- **Organ / phase touched:** the survey of backprop-free credit rules (`research/survey/`), and the "forward-only alternatives" catalog (`research/papers/phase3/direction-3-forward-only-alternatives.md`); target prop was explicitly considered and set aside in our idea history (draft-5 `test/ideas.md` "Target Propagation" node).
- **Same as us:** target prop turns global credit into a **stack of local, per-layer objectives** — same *spirit* as our layer-local SCFF windows. Both avoid a single global backward gradient.
- **Different from us (why we didn't take it):** DTP needs a **trained inverse per layer** — a learned backward network kept in sync with the forward one. That is *more* backward machinery than FA (which at least keeps `B` fixed), and far more than us (no backward network at all). On an analog substrate a trained inverse means a **second, plastic crossbar** — exactly the cost we designed away. And DTP is **supervised**; SCFF is label-free.
- **What we could borrow or test:** the **difference/linear-correction idea** (cancel an imperfect map's error to first order) is a general trick; if any part of our pipeline uses an approximate inverse (e.g. a reconstruction-based probe — which we rejected in P3), the difference correction is the standard stabilizer. Low priority given we chose contrast over reconstruction.
- **What contradicts or challenges us:** it shows targets (not gradients) can match backprop on hard discrete nets — a reminder that "local objectives can be strong." But its trained-inverse cost is precisely why it is the *wrong* fit for our transpose-averse substrate, which strengthens our forward-only choice by contrast.

## Follow-on leads
- "A Theoretical Framework for Target Propagation" (Meulemans et al., NeurIPS 2020) — shows DTP approximates Gauss-Newton, not gradient descent.
- Target Propagation via Regularized Inversion (Roulet & Harchaoui 2022) — a cleaner inverse formulation.
- The original Bengio 2014 target-prop note — the family root.
