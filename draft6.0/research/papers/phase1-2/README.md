# `phase1-2/` — the papers behind the adopted Phase 1–2 design

The outside papers the **cheap brain + the boosting chain** lean on, each written as a **story, not a spec** — the problem, the one idea that unstuck it, and *why it matters for our chip*. Each ends with a **"What it means for us"** section.

| File | The paper | One-line why it's here |
| ---- | --------- | ---------------------- |
| [scff.md](scff.md) | Self-Contrastive Forward-Forward (Nature Comms 2025) | Our cheap brain — label-free local learning. Also: the concat-vs-sum subtlety in our notes. |
| [deeperforward.md](deeperforward.md) | DeeperForward (ICLR 2025) | **Phase-2 central, with the Trifecta.** Counter-finding: layer-norm isn't the depth-killer — *squared goodness* is; keep the per-sample norm, switch goodness squared→linear. The substrate-friendly route. |
| [distance-forward.md](distance-forward.md) | Distance-Forward Learning (2024) | FF rebuilt *for chips*. We raid its margin loss and its overlapping-block trick. |
| [boostresnet.md](boostresnet.md) | Learning Deep ResNet Blocks Sequentially using Boosting Theory (ICML 2018) | The **proof** under our block concept — residual = boosting, each block a weak corrector. |
| [byol.md](byol.md) | Bootstrap Your Own Latent (DeepMind 2020) | The precedent for our EMA-view: a downstream learner reading a *slow* copy of the encoder. |
| [llrd.md](llrd.md) | Discriminative fine-tuning / layer-wise LR decay (ULMFiT 2018 →) | The precedent for our middle-layer slowdown — "slow what the downstream reads." |

> Cross-reference: the design these feed into is [`../../../idea/ideas1.md`](../../../idea/ideas1.md); the deeper algorithm survey is [`../../survey/summary.detail.md`](../../survey/summary.detail.md); the **Phase-3** depth papers are in [`../phase3/`](../phase3/README.md).
