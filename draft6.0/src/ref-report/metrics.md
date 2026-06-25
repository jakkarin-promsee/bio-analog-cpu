# Metrics — the measurement dictionary (pinned)

> The one place every Stage-1 metric is defined. The house-style / figure definitions live in the canonical
> [`../result-format.md`](../result-format.md) (per-phase additions in the `phaseN/result-format.md` deltas); this
> dictionary consolidates the *metrics* so a report can write `[BWT](../ref-report/metrics.md#bwt--backward-transfer)`
> and move on. **Pinned = the definition does not drift between phases.** Where a phase refined a metric, the
> entry notes it.

---

## Accuracy & convergence

### Held-out accuracy
Classification accuracy on data the model never trained on — fresh draws (re-drawn per eval) or a frozen test
split — at **equal weight budget** across racers. The raw performance number every other metric is read against.
- **Used in:** all phases

### AAA — anytime average accuracy
The trapezoidal area under the held-out-accuracy vs **log₁₀(samples-seen)** curve, divided by the log-span — a
single convergence-speed-weighted average accuracy in [chance, 1]. Log-x because the checkpoints are log-spaced, so
it rewards a model that climbs early, not just one that ends high.
- **Scope note:** effectively a **Phase-1 scalar**. Phase 2/3 lead on [depth-slope](#depth-slope), Phase 4 on [gap-to-BP](#gap-to-bp) / [BWT](#bwt--backward-transfer) — later reports shouldn't over-promise AAA.
- **Pinned in:** the canonical [`result-format.md`](../result-format.md)
- **Used in:** Phase 1 (the scalar)

### Memorization gap
Train-on-seen accuracy **minus** held-out accuracy — how much a model *memorizes* versus *understands*. Measured by
re-evaluating (no update) on a rolling buffer of already-seen samples; under a fresh-draw single pass it is ~0 by
construction (nothing to memorize), so it only *means* something on a repeating / seen buffer.
- **Pinned in:** the canonical [`result-format.md`](../result-format.md)
- **Used in:** Phase 1 (exp1 headline)

## Representation quality

### Linear probe
The pinned way we read a representation: logistic regression with fixed L2, on a **frozen 2k/2k** train/test split
of activations, trained to convergence. Linear on purpose — the result attributes to the *representation*, not a
clever classifier (Alain & Bengio) — and pinned so a layer can't be rescued by making the probe smarter.
- **Onward:** [`papers.md#alain-bengio-probes`](papers.md#alain-bengio-probes)
- **Used in:** Phase 1–4 (the per-layer read)

### Goodness (the SCFF energy)
SCFF's per-layer objective, `G = Σ‖h‖²` — the **sum** of squared activations. We use the sum form, not the paper's
mean `/M`, so the threshold θ=2.0 is reachable under plain online SGD (the mean starves deeper layers to ~1/M). High
goodness = a loud layer; training pushes positive goodness above θ and negative below. It measures **energy /
density**, which is why it clusters by density, not class.
- **Onward:** [`methods.md#scff--self-contrastive-forward-forward`](methods.md#scff--self-contrastive-forward-forward)
- **Used in:** Phase 1 (set), 2 (the energy wall)

### Selectivity
_Pinned:_ probe accuracy of the trained features **minus** the probe accuracy of an *untrained random projection of
the same architecture*. Answers "is the preserved info class-relevant, or just density?" — the **decisive control**
(it caught the P2.0 mis-route: deep SCFF fell *below* random ⇒ LOST, not merely entangled).
- **Used in:** Phase 2 (DECIDE), 3 (the contrast-vs-recon read: recon −0.062 density vs contrast +0.060 class)

### Depth-slope
The change in per-layer probe accuracy **per layer** (the slope of probe-vs-depth). Positive = depth helps (features
compose); negative = the wall. The central Phase-2/3 number.
- **Used in:** Phase 2, 3, 4 (A3)

### Effective rank (erank) / dead-units
Two transmission-health diagnostics: the **effective rank** of a layer's activations (rank-collapse if it falls) and
the fraction of **dead units** that never activate (deactivation). The two axes of the Phase-2 wall (rank 39→11,
dead 0→0.47); linear goodness cures both mechanically without curing the class wall.
- **Used in:** Phase 2 (P2.0/P2.1)

### CKA
Centered kernel alignment — a similarity score between two representations (across layers or methods). Used in
Phase 2 to show the transmission fix held the representation *mechanically* while class-separability still didn't
rise with depth.
- **Used in:** Phase 2 (REPR_CKA)

### Tail-retention
The deep-layer probe accuracy relative to its peak across depth — how much of a representation's best separability
*survives* to the top of the stack. High (→1) = depth doesn't erode the signal. In P3.2, w4's **0.99** vs w1's
**0.86** is the "composes vs drifts myopically" read. (Computed in the P3.2 card.)
- **Used in:** Phase 3 (P3.2 headroom table)

## Continual

### BWT — backward transfer
The average change in accuracy on **old** tasks after learning later ones. ≈0 = no forgetting; very negative
(−0.8…−1.0) = catastrophic forgetting. The headline continual metric (GEM / CL-survey conventions).
- **Onward:** [`papers.md#gem`](papers.md#gem)
- **Used in:** Phase 1 (exp4), 2 (P2.6), 3 (P3.3), 4 (A6)

### AA — average accuracy · FWT — forward transfer · forgetting
The rest of the continual profile: **AA** = mean accuracy across all tasks at the end of the stream; **FWT** =
head-start on a task before it's trained (forward transfer); **forgetting** = each task's drop from its own peak.
- **Onward:** [`papers.md#gem`](papers.md#gem)
- **Used in:** Phase 4 (A6, the full CONT figure)

## Characterization (Phase 4)

### gap-to-BP
`acc(tuned BP) − acc(OURS)`, **signed** — negative means OURS wins. Swept across a dialed axis (Bartunov-style), it
shows *where* the gap opens or closes; it is the Phase-4 headline characterization metric. *(Baseline note: the
task-accuracy axes race the [genuinely-tuned BP](methods.md#genuinely-tuned-bp--the-ceiling); the representation
axis A3 reads against the GD-hidden probe ceiling instead — two baselines, two questions.)*
- **Onward:** [`papers.md#bartunov`](papers.md#bartunov)
- **Used in:** Phase 4 (every axis)

### Bayes error & Bayes-normalized capture
**Bayes error** = the exact minimum achievable error for the Gaussian generator — the difficulty *dial* and the
*true ceiling* at once. **Capture** = `(acc(OURS) − chance) / (acc(Bayes) − chance) ∈ [0,1]` — the fraction of the
*achievable* the cheap brain captures. Capture is the honest difficulty read when the raw gap "closes" (the
achievable window shrinks as difficulty rises, confounding the absolute gap).
- **Onward:** [`papers.md#bayes-difficulty`](papers.md#bayes-difficulty)
- **Used in:** Phase 4 (A1, A5)

### Backward cost (substrate credit-assignment work)
The substrate's backward credit-assignment work = **credit-distance × weights + #backward weight-updates** (SCFF = 0
or the coordination-window depth, GD = full depth). Analytic, and labelled "substrate backward work" — **never**
"energy" or "N× faster." A numpy sim can't measure GPU energy, and the substrate cares about the former; Spyra's
caution is honoured by scoping the claim, not faking a number.
- **Onward:** [`papers.md#spyra`](papers.md#spyra)
- **Used in:** Phase 1 (exp1 F7), 2 (P2.5), 4 (PARETO, A4 — depth-gated)

### Retention (noise)
Accuracy-under-noise ÷ clean accuracy — the A7 read. We test **eval-time** multiplicative weight noise on a
clean-trained model, which is *distinct* from the substrate's regime (online learning *with* noise = hardware-aware),
which is untested.
- **Used in:** Phase 4 (A7, the honest negative)

## Honesty rules (how we call things)

### Calling a difference "real" (n=5)
_Pinned:_ a difference counts as real only if the **IQR bands are disjoint at the final checkpoint** AND the **sign
is consistent in ≥4/5 seeds, paired by seed**. Everything else is "within noise." Five seeds is too few for honest
p-values — so we don't fake them.
- **Pinned in:** `result-format.md` ("Calling a difference real")
- **Used in:** every comparison in every phase
