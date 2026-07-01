# `phase6/` — noise-robust SCFF: can the cheap brain survive the noise it will actually see?

> **A Stage-1 *extension*, pulled to the front of the queue (reframed 2026-07-01).** Phases 1–5 made the SCFF cheap
> brain compose depth. Phase 6 asks the question that decides whether any of it survives contact with a real substrate
> *and* a real continual stream: **is the representation robust to noise — and if not, where does the fix have to
> live?** The answer matters *now*, before the GD namer is built, because of one result this folder leans on:
>
> > **A frozen backbone caps the head's robustness. A trained readout *preserves* but cannot *manufacture* robustness
> > the features lack (LP-FT).** So if the sensitivity originates in SCFF, no amount of clever 20% GD can rescue it —
> > the fix is upstream, in the SCFF objective. That is why noise is a **Stage-1** problem, not a Stage-2 knob.
>
> Mechanism-first stories, each ending in a **"For us."** This pass *re-opens* the research with a clear target the
> first (Stage-2) pass didn't have: **make SCFF noise-robust.**

---

## Two things both called "noise" — and we owe both an answer

The word hides two distinct enemies, and the cheap brain has to survive **both**:

1. **Analog device noise — the substrate the weights live on.** Capacitor charge drifts; op-amps offset; ADCs
   quantize. Phase 4's **A7** flagged that the cell is **sensitive to eval-time noise**, and the per-sample L2 norm
   that makes it *nuisance-robust* is the very thing that makes it *noise-sensitive*. The hardware literature (Rasch
   2023) sharpens it: **input / tap / ADC-quantization noise dominates the accuracy loss — not weight noise — and the
   readout-input channel is precision-critical.** And the dangerous component is **directional** (aligned with the
   class axis), the *residual* mismatch that survives draft-5's differential / auto-zero. *Generic i.i.d. Gaussian is
   the easy version; the honest test is structured & directional.*

2. **Continual noise — the data itself (the author's Phase-6 insight, and it may be the bigger one).** Our model is
   **online and lifelong**: every datum is a single noisy real-world sample the hippocampus banks into the LUT to
   replay at sleep. **The model never sees a clean, curated "truth" set — its entire world is noisy samples**, arriving
   one at a time, out of distribution, sometimes mislabeled, never i.i.d. So robustness here isn't only "tolerate a
   noisy *weight*" — it's "**learn a stable class direction from a stream where every single example is corrupted and
   the true signal is never shown directly.**" This is the learning-from-noisy-streams / noisy-label problem, and it
   sits *on top of* the device-noise one.

Both reduce to the same geometric target — **flatness / a smooth representation** — but they attack through different
doors (perturb the weights vs. corrupt the inputs/labels), so the probe must hit both doors.

---

## The unifying target, and the two levers (kept separate — a past slip)

| channel | what's perturbed | the mechanism | the lever |
| --- | --- | --- | --- |
| **input / tap / ADC** | the *features* the readout reads | **Bishop 1995**: input-noise training ≈ a Jacobian-smoothness (Tikhonov) penalty | inject input/tap noise at train time |
| **weight / charge** | the analog weights themselves | **flat minima**: a flat minimum *is* "moving the weights barely moves the loss" = survives charge perturbation | **SAM** (target flatness) / **S-SGD** (inject symmetric weight noise) |
| **data / label stream** | the supervision itself | robust/early-learning + small-loss selection; representation stability under drift | a noise-aware *objective* + replay hygiene |

> **Attribution discipline (a correction this folder carries):** Bishop's theorem is **input** noise, *not* weight
> noise — don't cite it for the charge channel. Flatness unifies generalization and perturbation-robustness, but it is
> reached by **different levers for different channels.** Getting this wrong once already cost us a wrong probe (weight
> noise when the hardware says the tap channel dominates).

---

## The arc fork this phase resolves

The whole point of running noise **first** is a clean go/no-go that can reshape everything downstream:

- **YES — fixable in the SCFF objective.** The per-sample-norm objective can be made noise-aware (a smoothness /
  flatness term, a noise-augmented contrast) and the cheap brain stays cheap. The GD namer (Phases 7–9) then builds on
  a hardened base. *The good branch.*
- **NO — deeper rethink.** If structured directional noise destroys the class direction no matter how SCFF is trained,
  the substrate-as-designed can't hold the representation, and the arc itself reopens. *The literature prior leans
  toward "the fix is upstream, so it had better be reachable in the SCFF objective" — which is exactly why we test it
  now, cheaply, in numpy, before silicon.*

---

## The files

Read in this order — *the enemy → the primary fix → the existential data question → the allowed toolbox*:

| File | What it covers | The one idea |
| ---- | -------------- | ------------ |
| [noise-and-flatness.md](noise-and-flatness.md) | Bishop (input-noise = Tikhonov), flat-minima = generalization = robustness, SAM, S-SGD weight-noise, MGSER-SAM; the part the literature already settles — LP-FT (a head can't create backbone robustness) + Rasch (the tap channel dominates). | **Robustness, generalization, analog-noise tolerance are one thing: flatness — two levers for two channels.** |
| [noise-as-augmentation.md](noise-as-augmentation.md) | The primary fix: a **noise-corrupted contrastive view** makes the class *direction* noise-invariant — the forward-only surrogate for Jacobian/Lipschitz reg (Bishop). "Ditch the Denoiser"; contrastive ⇒ label-noise-robust. | **Make the InfoNCE positive a noisy view → robustness *in* the objective, spine-clean, forward-only.** |
| [all-data-is-noise.md](all-data-is-noise.md) | Door B (the continual insight): **Noise2Noise** — clean is recoverable from only-noisy *if zero-mean*; Self-Purified Replay → buffer **purity**, not just averaging; SSL is the noise-robust half. | **The cheap brain *can* learn with no clean truth — for zero-mean noise; the directional residual is the one crux.** |
| [forward-only-noise-toolbox.md](forward-only-noise-toolbox.md) | The lens (forward-only/local): noise-injection (Bishop/S-SGD) ✅, **ZOSA zeroth-order flatness** ✅ (overturns "SAM is out"), Jacobian-reg ⚠ (needs backprop); the honest AIHWKit noise model; Distance-Forward precedent. | **Forward-only-allowed: noise injection + zeroth-order flatness (at sleep) + replay purity.** |

## Papers (the noise slice; the pass adds more)

| paper | id / venue | the one-line reason it's here |
| --- | --- | --- |
| Training with Noise = Tikhonov (Bishop, Neural Comp. 1995) | classic | the foundation — **input** noise *is* a regularizer (Jacobian smoothness) |
| SAM (Foret 2020) | [2010.01412](https://arxiv.org/abs/2010.01412) | flat minima directly — generalization = robustness |
| S-SGD (symmetric weight-noise → flat minima) | [2009.02479](https://arxiv.org/abs/2009.02479) | **weight**-noise injection for flatness = our analog charge case (the channel Bishop does *not* cover) |
| LP-FT (fine-tuning distorts features) · backbone-robustness | [2202.10054](https://arxiv.org/abs/2202.10054) · [2305.17438](https://arxiv.org/abs/2305.17438) | **the reason noise is Stage-1**: a head *preserves* but can't *create* backbone robustness |
| IBM analog in-memory HW-aware / noise-aware training (Rasch, Nat. Comm. 2023) | [Nat.Comm.](https://www.nature.com/articles/s41467-023-40770-4) | **input/output/ADC noise dominates, not weight** — probe the right channel |
| MGSER-SAM | [2405.09492](https://arxiv.org/abs/2405.09492) | replay **+** sharpness-aware — a *hypothesised* flat-sleep bridge (forgetting-validated, not yet noise) |
| Probing Representation Forgetting | [2203.13381](https://arxiv.org/abs/2203.13381) | the unsupervised bulk *drifts* — stale tap-features are a noise-like perturbation (shared with Phase 9) |
| Noise2Noise (Lehtinen et al., ICML 2018) | [1803.04189](https://arxiv.org/abs/1803.04189) | **Door B's answer**: clean is recoverable from *only-noisy* pairs if zero-mean — learn without clean truth |
| Self-Purified Replay (Kim et al., ICCV 2021) | [2110.07735](https://arxiv.org/abs/2110.07735) | continual on noisy streams: **buffer purity is crucial**; SSL mitigates forgetting under noise (= our SCFF+LUT+sleep) |
| Co-learning w/ self-supervision · CNLL | [2108.04063](https://arxiv.org/abs/2108.04063) · [2204.09881](https://arxiv.org/abs/2204.09881) | the self-supervised (feature) signal is the noise-robust half; small-loss separates clean from noisy |
| "Ditch the Denoiser" — noise robustness in SSL from a curriculum (NeurIPS 2025) | [2505.12191](https://arxiv.org/abs/2505.12191) | robustness can be **pretrained into SSL features**; the denoiser is discardable at deployment |
| Why Contrastive Learning Benefits Robustness vs Label Noise | [2201.12498](https://arxiv.org/abs/2201.12498) | a linear head on contrastive features is **provably label-noise-robust** → the SCFF base is the robust half |
| Robust / consistency contrastive (diffusion-augmented) | [2509.20048](https://arxiv.org/abs/2509.20048) | perturbed-view consistency = noise-as-augmentation, the headline fix |
| Jacobian / Lipschitz regularization (Hoffman, Roberts & Yaida 2019; Jakubovitz & Giryes 2018) | [1908.02729](https://arxiv.org/abs/1908.02729) | the *explicit* noise-robustness penalty; input-noise injection is its forward-only surrogate (Bishop) |
| **ZO-SAM mechanism** — SPSA/ZO-SGD · **MeZO** · **ZOSA** (evidence, LLM-scoped) | [2305.17333](https://arxiv.org/abs/2305.17333) · [2511.09156](https://arxiv.org/abs/2511.09156) | **forward-only flatness** (Rademacher, no backprop) — overturns "SAM is out"; lift the *mechanism*, S-SGD is the reliable lever |
| SAM selects flatter minima late in training | [2410.10373](https://arxiv.org/abs/2410.10373) | a few flat-seeking epochs at the end ≈ full SAM → grounds a **periodic/late flat pass** (SCFF weights; not the readout sleep) |
| **RINCE — Robust InfoNCE against noisy views** (CVPR 2022) | [2201.04309](https://arxiv.org/abs/2201.04309) | a **loss-level** drop-in robust contrastive objective — hardens the *loss* where aug hardens the *inputs* (P6.1 variant) |
| **Noisy Machines** — noise-injection capacity ceiling | [2001.04974](https://arxiv.org/abs/2001.04974) | noise-aware training *reduces capacity* → a plateau **below** collapse (the P6.1 capacity-knee probe; distillation is the remedy) |
| Contrastive ≈ implicit Lipschitz / spectral robustness | [2405.17181](https://arxiv.org/abs/2405.17181) | the base contrastive objective already buys some smoothness — a 2nd theory leg besides Bishop |
| BayesFT — Bayes-optimized noise injection (Comm. Eng. 2023) | [s44172-023-00074-3](https://www.nature.com/articles/s44172-023-00074-3) | a *theoretically-guaranteed*, principled noise-injection distribution (not a guessed σ) |
| Variance-Aware Noisy Training (2025) | [2503.16183](https://arxiv.org/abs/2503.16183) | train *aware of the noise variance* — analog noise is unstable, not stationary |
| Analog NN robustness, noise-agnostic explainable regularizers (2024) | [2409.08633](https://arxiv.org/abs/2409.08633) | **correlated (common-mode, auto-zero subtracts) vs uncorrelated** — names our circuit framing in ML terms |
| AIHWKit analog toolkit · post-training IMC accuracy | [2104.02184](https://arxiv.org/abs/2104.02184) · [2401.09859](https://arxiv.org/abs/2401.09859) | the realistic analog noise model to mirror in numpy; post-training fixes are read-side (Stage 2) |
| Distance-Forward (forward-forward, hardware-noise-robust) | [2408.14925](https://arxiv.org/abs/2408.14925) | **in-family precedent**: a forward-only learner already hardened to device noise at <40% BP memory (also in phase1-2) |

> Cross-references: the model this hardens — [`../../../src/phase5-final-architecture.md`](../../../src/phase5-final-architecture.md);
> the Phase-6 plan — [`../../../src/phase6/design.md`](../../../src/phase6/design.md); the Stage-2 GD work that waits on
> this verdict — [`../../../src/stage2-design.md`](../../../src/stage2-design.md) + [`../phase7/`](../phase7/README.md).
