# `phase3/` — the depth-direction reframe (Phase 3 papers)

The literature pass behind the Phase-3 question: *can a forward-only, unsupervised learner earn depth?* It caught the one word Phase 2 had too strong — the depth wall is intrinsic to the **energy-goodness objective** (`Σh²`), **not** to forward-only locality. Forward-only local learners *do* compose depth when their objective is **predictive / info-preserving** (InfoNCE), not energy. Greedy InfoMax is the existence proof; a Jan-2026 paper tests SCFF *by name* and matches end-to-end backprop-SSL. That reframe is what draft 6.0 **adopted** — contrast + a cross-layer coordination window supersede energy-goodness (the verdict lives in [`../../../src/phase3/`](../../../src/phase3/phase3-summarize.md)).

| File | What it covers |
| ---- | -------------- |
| [the-objective-reframe.md](the-objective-reframe.md) | **Read first.** Energy vs predictive goodness; the GIM/CLAPP depth existence proof; P2.2 narrowed; the flat-MLP "what to predict" question. |
| [direction-1-cross-layer-goodness.md](direction-1-cross-layer-goodness.md) | The "A1-helps-layer-2" idea = OLU / DF-O / direct-feedback — the cheap coordination probe (adopted as the coordination window). |
| [direction-2-scff-gd-interleave.md](direction-2-scff-gd-interleave.md) | GD layers *between* SCFF layers (= P2.5 `write`, mostly "don't"); the one live seam, a non-collapsing intermediate objective. |
| [direction-3-forward-only-alternatives.md](direction-3-forward-only-alternatives.md) | The forward-only learner zoo (GIM / CLAPP / SoftHebb / Mono-Forward / predsim / forward-gradient) and the unsup-vs-sup fork. |

### Master paper list (Phase-3 additions, beyond the Phase 1–2 set)

| paper | id | direction | sup? | depth | substrate note |
| --- | --- | --- | --- | --- | --- |
| Greedy InfoMax | [1905.11786](https://arxiv.org/abs/1905.11786) | reframe/3A | no | ✅ | the existence proof |
| CLAPP | [2010.08262](https://arxiv.org/abs/2010.08262) | reframe/3A | no | ✅ | single-sample, Hebbian-plausible |
| Can Local Learning Match SSL-BP? | [2601.21683](https://arxiv.org/abs/2601.21683) | reframe | no | ✅ | tests SCFF; CLAPP++ = BP; direct-feedback + constant width |
| LoCo | [2008.01342](https://arxiv.org/abs/2008.01342) | 1/reframe | no | ✅ | GIM + adjacent-block coupling |
| Mono-Forward | [2501.09238](https://arxiv.org/abs/2501.09238) | 3B | yes | ✅ | **flat-MLP-native**, beats BP, the staged fallback |
| Local Error Signals (predsim) | [1901.06656](https://arxiv.org/abs/1901.06656) | 2/3B | yes | ✅ | non-collapsing `sim` loss |
| SoftHebb | [2107.05747](https://arxiv.org/abs/2107.05747) | 3A | no | ~ | purest local rule; low ceiling |
| OLU / The Trifecta | [2311.18130](https://arxiv.org/abs/2311.18130) | 1 | (either) | ~ | = the coordination-window idea; modest alone |
| Layer Collaboration (γ) | [2305.12393](https://arxiv.org/abs/2305.12393) | 1 | (either) | ~ | one broadcast wire |
| Forward gradient | [2202.08587](https://arxiv.org/abs/2202.08587) · [2210.03310](https://arxiv.org/abs/2210.03310) | 5 | either | ? | forward-only "direction"; high variance |
| PEPITA / top-down feedback | [2302.05440](https://arxiv.org/abs/2302.05440) | 5 | yes | ~ | 2-pass input modulation |
| Predictive Forward-Forward | [2301.01452](https://arxiv.org/abs/2301.01452) | 1/5 | no | ~ | top-down generative + predictive coding |
| Block-Local Learning | [2305.14974](https://arxiv.org/abs/2305.14974) | 2 | yes | ✅ | block auxiliary losses |
| Interlocking Backprop | [2010.04116](https://arxiv.org/abs/2010.04116) | 1/2 | yes | ✅ | overlapping-pair gradient sharing |
| Mono-Forward eval (3 methods) | [2511.01061](https://arxiv.org/abs/2511.01061) | 3 | — | — | energy/memory parity protocol |
| CaFo / ASGE / BiCovG | [2303.09728](https://arxiv.org/abs/2303.09728) · [2509.12394](https://arxiv.org/abs/2509.12394) · [2605.04346](https://arxiv.org/abs/2605.04346) | 3B | yes | ✅ | per-layer-CE CNNs; confirm the pattern |

> Cross-reference: the Phase 1–2 design papers are in [`../phase1-2/`](../phase1-2/README.md); the design these feed is [`../../../idea/ideas1.md`](../../../idea/ideas1.md); the survey is [`../../survey/summary.detail.md`](../../survey/summary.detail.md).
