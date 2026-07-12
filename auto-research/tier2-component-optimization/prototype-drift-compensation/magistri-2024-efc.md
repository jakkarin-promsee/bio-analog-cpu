# Elastic Feature Consolidation for Cold Start Exemplar-Free Incremental Learning (EFC / EFC++)
- **Authors / Year / Venue:** Simone Magistri, Tomaso Trinci, Albin Soutif-Cormerais, Joost van de Weijer, Andrew D. Bagdanov / 2024 / ICLR 2024 (EFC++: arXiv 2025)
- **Link:** https://arxiv.org/abs/2402.03917 · EFC++: https://arxiv.org/abs/2503.10439
- **Tier / Topic:** tier2-component-optimization / t2.6 prototype drift compensation
- **Relevance:** ⭐⭐⭐ — the "not all drift directions matter" idea: a second-order feature-space metric that weights drift by how much old tasks care. The metric concept ports to our drift *meter*; the regularizer itself is backbone-gradient machinery we can't use.

## TL;DR
Instead of estimating drift after the fact (SDC/LDC/ADC) or forbidding it (FeTrIL), EFC *shapes* it while it happens: an Empirical Feature Matrix (EFM) — a tractable second-order approximation of how sensitive old-task predictions are to feature perturbations — defines a pseudo-metric, and new-task training is regularized to drift freely in directions old tasks ignore while resisting drift along directions they need. Gaussian prototypes are rehearsed with an asymmetric loss to keep the classifier balanced. EFC++ splits this into plasticity-then-prototype-re-balancing: a post-training phase that updates the classifier to compensate for whatever feature drift did occur.

## The mechanism (how it actually works)
1. **EFM:** after each task, compute the empirical second moment of prediction-gradient sensitivity in *feature* space (not weight space — that's the difference from EWC/Fisher-style weight regularizers). Its eigenstructure says which feature directions carry old-task information.
2. **Elastic regularization:** while training task t, penalize feature drift ‖f_t(x) − f_{t−1}(x)‖ measured *in the EFM metric* — cheap drift is free, expensive drift is resisted. Plasticity is preserved because most directions are cheap.
3. **Prototype rehearsal:** old classes exist during new-task training only as stored Gaussian prototypes; an asymmetric cross-entropy balances pseudo-old vs real-new so the head doesn't develop task-recency bias.
4. **EFC++:** decouples the two roles — train the backbone elastically first, then run a *prototype re-balancing* phase that refreshes the classifier against the (drifted) feature space. Adds DomainNet; consistently above EFC.

## Key results / claims
- State-of-the-art cold-start EFCIL on CIFAR-100, TinyImageNet, ImageNet-Subset, ImageNet-1K (EFC++ adds DomainNet), specifically in the regime where the first task is too small to freeze a good backbone (the anti-FeTrIL regime).
- The EFM is shown to be a usable, tractable stand-in for full second-order drift sensitivity.

## How it relates to us
- **Organ / phase touched:** drift measurement (P9.0's probe protocol, the banked tap-drift gate signal); the sleep re-fit; N2's grave (P9.1 struck drift-slowdown).
- **Same as us:** treats "the representation will move" as a fact to manage, not a bug (our P9.0 rotation verdict); keeps old classes alive as stored Gaussian statistics refreshed against the moving space (our LUT+sleep, statistically).
- **Different from us:** the elastic regularizer modifies the *backbone's* training objective by gradient — our bulk's objective is committed (SCFF InfoNCE, GD never writes it), and P9.1 already struck the drift-slowdown lever family (N2) on the read side; EFC is N2 done with second-order machinery we declined at first order.
- **What we could borrow or test:** the **anisotropic drift metric** as a *meter*, not a brake: our banked tap-drift gate signal currently treats all drift directions equally; an EFM-flavored weighting — "drift projected onto class-discriminative directions" (for us: onto the SLDA prototype-difference directions, closed-form from stored stats) — would make the between-sleeps staleness alarm fire on drift that *matters* and ignore rotation in dead directions. That is a strictly better trigger feature, computable from statistics we already store.
- **What contradicts or challenges us:** EFC++'s result that a *post-hoc classifier re-balancing phase* is worth separating from backbone training is our sleep, rediscovered from the gradient world — mild confirmation, not contradiction.

## Follow-on leads
- EFC++ (arXiv:2503.10439) — the prototype re-balancing split (covered above).
- Layerwise Proximal Replay (arXiv:2402.09542) — layer-wise drift constraints, already flagged in the P9 delta.
- The EFM-weighted drift meter → connects to the deferred tap-drift gate experiment (repo-internal, commit ef80d1f).
