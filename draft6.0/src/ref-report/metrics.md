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
- **Used in:** Phase 1–5 (the per-layer read; the Phase-5 composing-depth metric is built on it)

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

## Depth close-out & Stage 2 (Phases 5–10)

### Composing-depth (per-layer probe read)
The Phase-5 depth diagnostic: the per-layer [linear probe](#linear-probe) accuracy as a function of depth. "Composes"
= it rises with depth (features build); "decays" = it peaks (~L5 on the adopted cell) then falls (deep layers drift
off the class manifold). The whole P5 question is *earn the rise, read the peak.*
- **Used in:** Phase 5 (the decay + the fix)

### w12 ceiling (the objective-capability upper bound)
A *forbidden* full-credit reference: the same InfoNCE objective trained with a coordination window of 12 (= full
end-to-end backprop reach through the stack). It composes the **whole** 12-layer stack with no decay, proving the
decay is **objective-locality, not an intrinsic wall** — the depth is curable. **Never deployed** (it is the backward
pass the chip exists to avoid); it is the diagnostic ceiling every cheap lever is measured against.
- **Used in:** Phase 5 (the "curable" proof)

### Truncation floor
The cost baseline every readout must beat: a cheap from-scratch short stack built only to the profiled extractor
depth, read at its top. On a chip, fewer layers = fewer Scaps = cheaper silicon — so if nothing beats truncation on
the continual workload, *ship the truncation.*
- **Used in:** Phase 5 (the read-cheaply gate)

### Forward-MACs / expected-compute
The P5 cost read for a readout: the multiply-accumulates the *reader* runs (the L12 bulk runs regardless). The fixed
short reader reads the continual home ~8× cheaper (0.547 @ 9.0k readout-MACs) than all-tap (@ 72.5k).
"Expected-compute" adds the gate/exit overhead for an *adaptive* reader (struck on the flat home).
- **Used in:** Phase 5 (the read-cheaply cost)

### argmax-flip (the spine metric)
The Phase-7 test of whether a head reads class **direction** or **magnitude**: apply a per-class norm nuisance (scale
each class's features) and measure the fraction of predictions whose argmax flips. **0.000** = direction-pure (only
the cosine heads); higher = the verdict rides a magnitude. It made "the spine bends" a *measurement*, not a worry
(RanPAC 0.54, cosine 0.00 — the winner reads a magnitude but is recency-robust by having no trained weights).
- **Used in:** Phase 7 (the spine read), 8 / 9 (the gate / eviction spine nulls)

### worst-pre-sleep BWT (the honest continual read)
[BWT](#bwt--backward-transfer) measured at the **worst mid-stream point** (just before a sleep), not only at the
stream's end — the honest read the final-BWT masks (a loop can end recovered yet dip badly between sleeps on a
lifelong stream). The Stage-2 continual-safety headline: the frozen loop holds worst-BWT **−0.028** (ties a boundary
oracle) vs a fair ER's **−0.272** (≈10× safer).
- **Used in:** Phase 8 (LIVE-SAFE), 9 (the freeze), 10 (the safety win)

### GD-share & bp_ratio (the metered 80/20)
**GD-share** = the fraction of total *metered substrate energy* spent by the GD namer — the first non-proxy "80/20"
(0.121 with the gate on, 0.778 off: the gate *creates* the split). **bp_ratio** = OURS's energy ÷ a fair BP+replay
learner's at matched retention (0.501 = half). Both from the behavioral ADC-centred
[cost meter](methods.md#the-cost-meter-adc-centred-behavioral).
- **Used in:** Phase 8 (the economy), 10 (the Pareto)

### MTD & FAR (drift detection)
**MTD** = mean time to detect a real class onset (in steps); **FAR** = false-alarm rate on a nuisance (covariate)
shift. The Phase-8 trigger read: the class-direction tap-drift signal *leads* the labeled error (MTD 6 < 14) at a
clean nuisance FAR, while the magnitude null false-fires on 94% of nuisance steps.
- **Used in:** Phase 8 (the gate / trigger bake-offs)

### Destruction (rotation-not-forgetting)
The Phase-9 measurement that discharges the founding cheap-replay assumption: an optimal probe **re-fit** on the
*current* bulk, scored on held-out early-task data (Davari 2203.13381 protocol, which factors rotation out). It holds
≥ its birth score throughout (final 2.2×, min 0.966) while a *fixed* head rots to ~0.07 — so the bulk **rotates, it
does not forget**, and sleep stays cheap.
- **Used in:** Phase 9 (P9.0, the risk gate)

### Retention as a direction read (extends [Retention (noise)](#retention-noise))
For the Phase-6 / 10 **directional** enemy (a coherent translation along the class axis), per-sample cosine is blind
(each rep barely rotates), so the direction-preservation read *is* retention — accuracy-under-shift ÷ clean, made
direction-specific by the OURS-vs-linear and directional-vs-iid contrasts. density ≠ class, the read that survives it.
- **Used in:** Phase 6 (the spine metric), 10 (the noise showcase)

## Honesty rules (how we call things)

### Calling a difference "real" (n=5)
_Pinned:_ a difference counts as real only if the **IQR bands are disjoint at the final checkpoint** AND the **sign
is consistent in ≥4/5 seeds, paired by seed**. Everything else is "within noise." Five seeds is too few for honest
p-values — so we don't fake them.
- **Pinned in:** `result-format.md` ("Calling a difference real")
- **Used in:** every comparison in every phase
