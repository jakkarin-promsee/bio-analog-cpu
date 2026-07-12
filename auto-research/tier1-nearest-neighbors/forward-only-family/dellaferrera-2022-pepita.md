# Error-driven Input Modulation (PEPITA): Solving the Credit Assignment Problem without a Backward Pass
- **Authors / Year / Venue:** Giorgia Dellaferrera, Gabriel Kreiman / 2022 / ICML 2022 (arXiv:2201.11665)
- **Link:** https://arxiv.org/abs/2201.11665 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐ — the *other* major forward-only family (a modulated second pass, not two contrastive passes); the cleanest contrast to our label-free frame.

## TL;DR
Keep backprop's *global error* but deliver it **without a backward pass**: run a clean forward pass, compute the output error, then run a **second forward pass on the input perturbed by that error** (projected to input space through a fixed random matrix). Each layer updates from the difference between its clean and modulated activations — a purely forward, local delta rule.

## The mechanism (how it actually works)
Pass 1 (clean): `h_clean = f(Wx)` all the way to output `y`, error `e = y − target`. Pass 2 (modulated): perturb the input `x' = x + F·e` where `F` is a **fixed random projection** of the error back onto the input (this is the key trick — it borrows Feedback Alignment's insight that a random fixed feedback matrix is enough to carry a useful learning signal). Re-run the forward pass on `x'`. Each layer's weight update is proportional to `(h_clean − h_modulated)` times the layer input — the modulation *is* the credit signal, so no transposed weights, no stored activations across the backward direction, no update-locking.

## Key results / claims
Demonstrated on MNIST, CIFAR-10, CIFAR-100 with fully-connected and convolutional nets. Addresses weight symmetry, non-local signals, update locking, and activity freezing simultaneously. Accuracy trails backprop but is competitive with other biologically-plausible rules (Feedback Alignment family); notably better than FF on the harder CIFARs in some follow-up comparisons.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the *alternative* to our SCFF bulk; the namer-injection question (§2.4/§3.1).
- **Same as us:** forward-only, no transpose, no activation tape, uses a fixed random projection (we use random projection in the **RanPAC namer**, not the bulk).
- **Different from us:** PEPITA is **fully supervised and global** — every layer's update is driven by the *output label error* carried forward. Our bulk is **label-free and unsupervised**; no error or label ever reaches it. PEPITA needs **two forward passes per sample** (clean + modulated); our mono-forward carries both worlds **in one sweep** on the dual rail. PEPITA is a single learner; we split frozen-bulk + separate namer.
- **What we could borrow or test:** the **modulated-second-pass** is a candidate forward-only way to inject a *tiny* label-direction correction into the top SCFF layers without a backward pass — a possible cheat for the 20% that stays on-substrate. Untested for us.
- **What contradicts or challenges us:** it shows a *global* credit signal can travel forward cheaply — a reminder that "forward-only" does not by itself imply "label-free"; our label-freedom is a separate, deliberate constraint (the continual-safety mechanism), not a consequence of being forward-only.

## Follow-on leads
Feedback Alignment / Direct Feedback Alignment (the random-matrix credit family); "Forward Learning with Top-Down Feedback" (Srinivasan et al. 2023, the analytical characterization of PEPITA-style rules); update-locking-free training for pipeline hardware.
