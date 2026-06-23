# Papers & people — the citation backbone

> One line per source, with the people, the arXiv id, and a link to the full story in
> [`../../research/papers/`](../../research/papers/README.md). The reports cite by linking here;
> the *why it matters for us* lives in the story files, not duplicated.
>
> **All authors and titles verified (2026-06-23, arXiv cross-checked).** Both former guards are closed: the
> Mono-Forward (2501.09238) title and the 2601.21683 author list are now confirmed against arXiv.

---

## The Stage-1 canon (at a glance)

| Paper | People | id / venue | Where it lands | Story |
| --- | --- | --- | --- | --- |
| Forward-Forward | Geoffrey Hinton | [2212.13345](https://arxiv.org/abs/2212.13345) (2022) | the ancestor; "goodness", two forward passes | — |
| Self-Contrastive FF (SCFF) | Xing Chen, Dongshu Liu, Jérémie Laydevant, Julie Grollier | [2409.11593](https://arxiv.org/abs/2409.11593), Nature Comms 2025 | **N1** the cheap brain (Grollier = CNRS-Thales neuromorphic group) | [scff](../../research/papers/phase1-2/scff.md) |
| DeeperForward | Liang Sun, Yang Zhang, Weizhao He, Jiajun Wen, Linlin Shen, Weicheng Xie | ICLR 2025 ([OpenReview kOYnXVQCtA](https://openreview.net/forum?id=kOYnXVQCtA)) | Phase-2 transmission fix (linear > squared goodness) | [deeperforward](../../research/papers/phase1-2/deeperforward.md) |
| Distance-Forward | Yujie Wu, Siyuan Xu, Jibin Wu, Lei Deng, Mingkun Xu, Qinghao Wen, Guoqi Li | [2408.14925](https://arxiv.org/abs/2408.14925) (2024) | margin loss; DF-O overlapping blocks | [distance-forward](../../research/papers/phase1-2/distance-forward.md) |
| BoostResNet | Furong Huang, Jordan Ash, John Langford, Robert Schapire | [1706.04964](https://arxiv.org/abs/1706.04964), ICML 2018 | **N3** residual = boosting (Schapire = boosting's inventor) | [boostresnet](../../research/papers/phase1-2/boostresnet.md) |
| BYOL | Grill et al. (DeepMind) | [2006.07733](https://arxiv.org/abs/2006.07733) (2020) | EMA-view precedent (N2) | [byol](../../research/papers/phase1-2/byol.md) |
| LLRD / ULMFiT | Jeremy Howard, Sebastian Ruder | [1801.06146](https://arxiv.org/abs/1801.06146) (2018) | slow-what-the-downstream-reads (N2) | [llrd](../../research/papers/phase1-2/llrd.md) |
| Greedy InfoMax (GIM) | Sindy Löwe, Peter O'Connor, Bastiaan Veeling | [1905.11786](https://arxiv.org/abs/1905.11786), NeurIPS 2019 | **the depth existence proof** (Phase-3 reframe) | [reframe](../../research/papers/phase3/the-objective-reframe.md) |
| CLAPP | Bernd Illing et al. | [2010.08262](https://arxiv.org/abs/2010.08262), NeurIPS 2021 | contrastive local + predictive; single-sample, Hebbian-plausible | [reframe](../../research/papers/phase3/the-objective-reframe.md) |
| Can Local Learning Match SSL-BP? | Zihan Wu, Ariane Delrocq, Wulfram Gerstner, Guillaume Bellec (EPFL) | [2601.21683](https://arxiv.org/abs/2601.21683) (Jan 2026) | tests SCFF by name; CLAPP++ = BP-SSL on CIFAR-10 (80.51 vs 80.49) | [reframe](../../research/papers/phase3/the-objective-reframe.md) |
| Mono-Forward (method) | James Gong, Bruce Li, Waleed Abdulla (Univ. Auckland) | [2501.09238](https://arxiv.org/abs/2501.09238) | Phase-4 reference racer (supervised-local, flat-MLP-native) | [direction-3](../../research/papers/phase3/direction-3-forward-only-alternatives.md) |
| Mono-Forward eval (fairness) | Przemysław Spyra, Witold Dzwinel | [2511.01061](https://arxiv.org/abs/2511.01061) | tuned-BP fairness protocol + the "don't call cost 'energy'/'N×'" caution | — |
| Linear probes | Guillaume Alain, Yoshua Bengio | [1610.01644](https://arxiv.org/abs/1610.01644) (2016) | the per-layer probe discipline | — |
| Gap-to-backprop swept | Sergey Bartunov et al. | [1807.04587](https://arxiv.org/abs/1807.04587), NeurIPS 2018 | the Phase-4 GAP-CURVE/MAP method | — |
| GEM | David Lopez-Paz, Marc'Aurelio Ranzato | [1706.08840](https://arxiv.org/abs/1706.08840), NeurIPS 2017 | BWT/AA/FWT continual metrics | — |
| Continual-learning survey | Liyuan Wang et al. | [2302.00487](https://arxiv.org/abs/2302.00487) | the CL metric definitions | — |
| Bayes-error difficulty | Ryan Theisen, Huan Wang, Lav R. Varshney, Caiming Xiong, Richard Socher | [2106.03357](https://arxiv.org/abs/2106.03357), NeurIPS 2021 | the A1 exact-Bayes dial + true ceiling | — |

_(Also-rans cited in Phase 3's "directions placed", keep as a secondary list: SoftHebb [2107.05747](https://arxiv.org/abs/2107.05747),
Local Error Signals/predsim [1901.06656](https://arxiv.org/abs/1901.06656), forward-gradient [2202.08587](https://arxiv.org/abs/2202.08587)/[2210.03310](https://arxiv.org/abs/2210.03310),
PEPITA [2302.05440](https://arxiv.org/abs/2302.05440), LoCo [2008.01342](https://arxiv.org/abs/2008.01342), LPL, OLU/The Trifecta [2311.18130](https://arxiv.org/abs/2311.18130),
Layer Collaboration [2305.12393](https://arxiv.org/abs/2305.12393) — full list in [`../../research/papers/README.md`](../../research/papers/README.md).)_

---

## Anchors (one-liner each; for report links)

### Forward-Forward
Hinton 2022 — replace backprop with two forward passes; each layer maximizes "goodness" on real, minimizes on fake. The negatives were FF's weak link → SCFF.

### scff
Chen/Liu/Laydevant/Grollier 2025 — FF made unsupervised: positive = sample-with-itself, negative = a mixture. Our sum-goodness reformulation (= the paper's concat since W₁=W₂) enables mono-forward.

### deeperforward
Sun et al., ICLR 2025 — layer-norm + linear (not squared) goodness cures deactivation/rank-collapse and trains deep FF; our Phase-2 transmission fix (mechanism only — doesn't earn class-depth on unsupervised flat MLP).

### distance-forward
Wu et al. 2024 — FF rebuilt for chips; we raid its margin loss (standby) and DF-O overlapping-block coordination.

### boostresnet
Huang/Ash/Langford/Schapire, ICML 2018 — a ResNet *is* boosting (telescoping sum); each block a weak corrector; error ≤ e^(−½Tγ²). The proof under our block concept; the guarantee lives on the GD heads.

### byol
Grill et al. 2020 — a downstream learner reading a slow (EMA) copy of the encoder; the precedent for our EMA-view de-risk (N2).

### llrd
Howard & Ruder 2018 — layer-wise LR decay ("slow what the downstream reads"); the precedent for the N2 plasticity slowdown.

### gim
Löwe/O'Connor/Veeling, NeurIPS 2019 — forward-only, gradient-isolated, *unsupervised*, and depth-composing via InfoNCE. The existence proof that reframed Phase 3 (the wall is the energy objective, not locality).

### clapp
Illing et al., NeurIPS 2021 — GIM made single-sample + Hebbian-plausible; CLAPP++ matches BP-SSL on CIFAR-10. The family our adopted contrast objective belongs to.

### mono-forward
Gong/Li/Abdulla 2025, *"Mono-Forward: Backpropagation-Free Algorithm for Efficient Neural Network Training Harnessing Local Errors"* — forward-only *supervised*, flat-MLP-native; the Phase-4 reference racer (note: not "mono-forward", our dual-rail scheme).

### alain-bengio-probes
Alain & Bengio 2016 — linear probes per layer; pinned as our representation metric (the result attributes to the representation, not the classifier).

### bartunov
Bartunov et al., NeurIPS 2018 — sweep the gap-to-backprop across difficulty/scale; the Phase-4 GAP-CURVE/MAP method.

### gem
Lopez-Paz & Ranzato, NeurIPS 2017 — the BWT / AA / FWT continual metrics we report.

### bayes-difficulty
Theisen et al., NeurIPS 2021 — difficulty = exact Bayes error; the A1 dial and the true ceiling for capture.

### spyra
Spyra & Dzwinel 2025 — the tuned-BP fairness protocol and the caution that a sim's cost is "backward work," never "energy" / "N× faster." We honour it by scoping the claim.
