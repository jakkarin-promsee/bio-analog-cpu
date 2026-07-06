# Methods — the mechanisms the reports name

> Report-altitude definitions, grouped into five bands. Full stories: [`../../research/papers/`](../../research/papers/README.md) ·
> detail: [`../../research/survey/`](../../research/survey/README.md).
> Decision record: [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md).

---

## Band 1 — the cheap brain

### SCFF — Self-Contrastive Forward-Forward
The cheap brain (~80%). A **positive** is a sample paired *with itself* ("one coherent thing"); a **negative** is a
sample paired *with a different sample* ("a mixture"). Every layer learns one question — *"is what I'm looking at a
single coherent thing, or a mash-up?"* — with no labels, no backward pass, and each unit updating from its own
activity (local, derivative-free, forward-only). Our **sum** reformulation (one weight on `x_pos + x_neg`) equals
the paper's concatenation form exactly because `W₁ = W₂`, and is what makes mono-forward possible. It clusters by
**density, not class** — the through-line wound.
- **Onward:** [`../../research/papers/phase1-2/scff.md`](../../research/papers/phase1-2/scff.md) · [`../../research/survey/SCFF.detail.md`](../../research/survey/SCFF.detail.md) · [`papers.md#scff`](papers.md#scff)
- **Used in:** Phase 1, 2, 3, 4

### Forward-Forward (FF) — the ancestor
Hinton's 2022 idea: replace backprop with *two forward passes* — one on real ("positive") data, one on fake
("negative") — training every layer to be loud on real and quiet on fake, with no gradient travelling backward
(beautiful for hardware: no transpose, no stored activations). FF's weak link was where the fake came from
(stamping wrong labels into corner pixels — which needs labels and doesn't generalize); SCFF fixed it by making
negatives out of the data itself.
- **Onward:** [`papers.md#forward-forward`](papers.md#forward-forward)
- **Used in:** Phase 1, 2

### Mono-forward (dual-rail) — OUR forward scheme
A single forward sweep carries **two worlds** — positive and negative — side by side down a dual-rail datapath,
through the *same shared* weight crossbar. Only the cheap activation buffers double, **not** the Scaps (the weights),
trading ~2× buffer area for one charge cycle instead of two. Because both goodnesses stay explicit, the full
two-sided loss is preserved (no scale runaway).
- **Disambiguation:** this is the project's **forward scheme** (lowercase). **Mono-Forward** (capital-F, Band 4) is
  a *different* thing — Gong et al.'s supervised-local learner used as a Phase-4 racer. Never conflate them.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S2) · [`../../context.md`](../../context.md)
- **Used in:** Phase 1 (setup), 4 (cost claim, measured in A4)

### Taps — GD reads all SCFF layers, never writes
The GD readout *taps* (reads) the SCFF layers' activations but never writes back into them — so SCFF and GD never
share a weight, and there's a built-in stop-gradient (BYOL's anti-collapse condition, for free). Phase 1 corrected
the spec: tap **all** SCFF layers, not the last `n` — the last ones are the most degraded.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S3)
- **Used in:** Phase 1, 2

## Band 2 — the objective family (the Phase-3 lever)

### Energy goodness
SCFF's original per-layer objective: goodness `G = Σ‖h‖²` (the sum of squared activations — see
[metrics: goodness](metrics.md#goodness-the-scff-energy)). Training pushes positive goodness above a threshold θ and
negative below. It measures **energy / density** — how loud a layer is — which only recovers class when classes
*are* density clusters; **superseded** by contrast in Phase 3.
- **Onward:** [`metrics.md#goodness-the-scff-energy`](metrics.md#goodness-the-scff-energy) · [`#scff--self-contrastive-forward-forward`](#scff--self-contrastive-forward-forward)
- **Used in:** Phase 1 (set), 2 (the energy wall), 3 (the baseline it supersedes)

### Masked-reconstruction
A candidate Phase-3 objective: each layer reconstructs held-out input dimensions from the rest (a denoising /
info-preserving target — single-sample, no negatives). It preserves *all* the input information — i.e. **density** —
which sits *below* a random projection on class separability, so it was **rejected** (P3.0): preservation alone
preserves the wrong thing.
- **Onward:** [`../../research/papers/phase3/the-objective-reframe.md`](../../research/papers/phase3/the-objective-reframe.md)
- **Used in:** Phase 3 (P3.0, the rejected arm)

### Contrast objective (InfoNCE, two-mask views)
The **adopted** Phase-3 objective: each layer is trained with a local InfoNCE loss over two masked views of a sample
(close for the same sample, far for others; temperature 0.5), preserving the **discriminative (class)** part of the
information rather than all of it (density). This is why every depth-composing local learner (GIM/CLAPP) is
contrastive, not an autoencoder. It supersedes energy goodness.
- **Onward:** [`../../research/papers/phase3/the-objective-reframe.md`](../../research/papers/phase3/the-objective-reframe.md) · [`papers.md#clapp`](papers.md#clapp)
- **Used in:** Phase 3 (adopted), 4 (the cell under test)

### Coordination window `w` (OLU / Direction 1)
The user's "Direction 1": a layer learns to help the *next* layer's discrimination, not only its own — implemented
as a window of `w` layers trained in joint groups (gradient shared inside the window, then detached at the
boundary), forward-only. It converts contrast's preserved-but-myopic features into **composed** ones — the
cross-layer coordination P2.2 named as missing. `w ≥ 2`; larger windows help more where headroom is large.
- **Onward:** [`../../research/papers/phase3/direction-1-cross-layer-goodness.md`](../../research/papers/phase3/direction-1-cross-layer-goodness.md)
- **Used in:** Phase 3 (P3.1/P3.2), 4 (A3 lever)

## Band 3 — chain + maintenance

### Residual boosting chain
GD checkpoints arranged as residual blocks, each fitting the **residual** the previous one left — a telescoping sum
(BoostResNet), so each block is a *weak corrector*, not a full predictor. The boosting guarantee lives on the
*labels* → in the GD heads, not the unsupervised SCFF. Full residual ε=1 (per-block features individually degrade)
gives the most diverse, best ensemble; in practice error saturates after ~2 blocks.
- **Onward:** [`../../research/papers/phase1-2/boostresnet.md`](../../research/papers/phase1-2/boostresnet.md) · [`papers.md#boostresnet`](papers.md#boostresnet)
- **Used in:** Phase 1 (exp3), 2 (P2.5)

### Plasticity gradient / slow read-layers (N2)
Lower the learning rate of the late SCFF layers the GD readout reads (mirroring LLRD), so the features the readout
depends on drift slowly. It bounds drift cheaply (ρ≈0.3 best in P1 exp2c) — but it is a **drift** fix, **not** a
**depth** fix: degradation persists at every ρ.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (N2) · [`papers.md#llrd`](papers.md#llrd)
- **Used in:** Phase 1 (exp2c)

### Sleep consolidation
A periodic phase that re-fits the GD readout full-batch over replayed history (a prototype store) against the
*current* SCFF map, recovering whatever readout drift accumulated online. Cheap by construction (GD ≈ 20% of
weights, SCFF frozen). It is the continual recovery mechanism — SCFF itself doesn't forget; the readout does
*without* sleep.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S7)
- **Used in:** Phase 1 (exp4), 2 (P2.6), 3 (P3.3), 4 (A6)

### LUT prototype memory (the hippocampus stub)
A deduplicated store of raw-input prototypes (winner-take-all novelty allocation). One store, three customers: SCFF
negatives, sleep replay, and the seed of the future "memory model" (the hippocampus track). In exp4 it replayed
nearly as well as full history at a third of the store.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S8)
- **Used in:** Phase 1 (exp4)

### Threshold gate (Ch7)
The planned mechanism that pays for expensive GD only when the cheap local path stalls: below a loss (or loss-slope)
threshold, update SCFF only; above it, spend the expensive update. **Status: resolved at Phase 8 (S6 → S12)** — the
committed awake gate is **DDM** on the namer's error-EMA — a class-direction tap-drift trigger was validated but not
shipped (see [DDM awake gate](#ddm-awake-gate--class-direction-tap-drift-trigger)) — and Phase 8 found the gate is a *safety*
mechanism, not just a cost saver.
- **Onward:** [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S6 → S12) · [DDM awake gate](#ddm-awake-gate--class-direction-tap-drift-trigger)
- **Used in:** named as an open knob in Phases 1–7; committed in Phase 8

## Band 4 — racers / baselines

### Genuinely-tuned BP — the ceiling
The Phase-4 ceiling: a backprop MLP given a **real hyperparameter search** (lr + weight-decay + a few shapes,
logged) at **equal weight budget** — the Spyra fairness protocol. The whole Phase-4 frame is "gap to a *tuned* BP,"
so a skeptic's "tuned how?" is answered here; without it the wins would look cheap. *(On the representation axis A3
the baseline is instead **GD-hidden**, the per-layer probe ceiling — two baselines for two different questions.)*
- **Onward:** [`papers.md#spyra`](papers.md#spyra) · [`metrics.md#gap-to-bp`](metrics.md#gap-to-bp)
- **Used in:** Phase 4 (the ceiling, every axis); the "GD" ceiling in Phase 1–3

### Mono-Forward (the racer)
Gong et al.'s forward-only **supervised** learner: each layer gets a tiny projection (classes × neurons) →
goodness-as-logits → *local* cross-entropy, with no signal crossing layers; flat-MLP-native and beats backprop on
some image MLPs. We race it as the strongest forward-only-supervised bar — but it's an *unreliable* reference: it
collapses in high-D (A2) and only catches up at high class count (A5).
- **Note:** not "mono-forward" (Band 1, the dual-rail scheme).
- **Onward:** [`../../research/papers/phase3/direction-3-forward-only-alternatives.md`](../../research/papers/phase3/direction-3-forward-only-alternatives.md) · [`papers.md#mono-forward`](papers.md#mono-forward)
- **Used in:** Phase 4 (the third racer)

## Band 5 — the closed object (the Stage-1 close-out + Stage 2)

### Sharper InfoNCE temperature (the depth lever)
The Phase-5 *free* fix for the depth decay: lower the InfoNCE temperature (0.5 → 0.2), so each layer's update is more
class-selective and the representation stops drifting off the class direction with depth. An lr-matched control shows
~82% of the lift is **direction**, not a disguised step-size — the readout then beats a genuinely-tuned BP and the
probe tail reaches the [w12 ceiling](metrics.md#w12-ceiling-the-objective-capability-upper-bound).
- **Onward:** [`../phase5/README.md`](../phase5/README.md)
- **Used in:** Phase 5 (earn-depth)

### Fixed short reader (truncation deploy)
The Phase-5 *read-cheaply* answer: read the useful depth with a short **fixed** truncation stack (~L2–3 on the flat
continual home; all-tap for peak accuracy; w4 the bounded depth-closer for compositional tasks), not an adaptive
per-sample early-exit (struck — the flat home rewards pooling over placement). Reads ~8× cheaper than all-tap.
- **Onward:** [`../phase5/README.md`](../phase5/README.md) · [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S9)
- **Used in:** Phase 5 (the deploy)

### NoiseAugContrast — the committed cheap cell
The Stage-1 close-out cell handed to Stage 2: the frozen Phase-5 `SCFFContrastOverlap` (temp 0.2 / w2, L12, no
residual) **+ one iid-noise-augmented InfoNCE view** (σ_aug 1.0). The augmentation is **generic** (broad iid), not
directional-specific — you cannot bet on one axis for a coherent shift unknown at train time. Forward-only; it
*improves* clean accuracy and keeps the continual win.
- **Onward:** [`../phase6/README.md`](../phase6/README.md) · [`../phase6-final-architecture.md`](../phase6-final-architecture.md)
- **Used in:** Phase 6 (committed), 7–10 (the frozen bulk)

### RanPAC — the namer (P7 winner)
The Phase-7 bake-off winner: a **no-gradient, closed-form** analytic head — a frozen random ReLU projection
`φ = relu(Wr·f)` → running-Gram ridge prototype `W = (G+λI)⁻¹M`. It ties the gradient MLP on accuracy×BWT and is #1
on natural digits, proving *the "20% GD" is a role, not a method* (the precise brain names the world with no backward
pass). Kept as the P8 accuracy/spine reference; SLDA is deployed for cost.
- **Onward:** [`../phase7/README.md`](../phase7/README.md)
- **Used in:** Phase 7 (winner), 8 (the reference)

### SLDA — the deployed namer
Streaming Linear Discriminant Analysis — a tied-covariance analytic head, no gradient. The **committed** deployed
namer from Phase 8: metered **69× cheaper** than RanPAC (no large random projection) while tying/beating its accuracy
live. Streamed via a `partial_fit` primitive (running Gram, guarded ≡ a batch fit to 4e-15).
- **Onward:** [`../phase8/README.md`](../phase8/README.md)
- **Used in:** Phase 8 (committed), 9, 10

### cbrs — class-balanced reservoir sampling
The committed imbalance guard: re-balance the *input* buffer (keep class balance) rather than re-weight the *output*
— buffer-side, family-agnostic (it overturned the plan's AIR, which over-corrects). It is why "firing more forgets
more" is a *design choice*, not fate: a balanced buffer + rare gated fires holds worst-BWT at 0.000. In Phase 9 it is
also the bounded-LUT **eviction** policy (best-bounded; the cap grows with #classes).
- **Onward:** [`../phase7/README.md`](../phase7/README.md) · [`../phase9/README.md`](../phase9/README.md)
- **Used in:** Phase 7 (chosen), 8 (the safety mechanism), 9 (eviction)

### DDM awake gate + class-direction tap-drift trigger
The Phase-8 economy: a **DDM** (two-threshold error) awake gate decides *when* the namer fires; the **deployed** gate reads
the namer's **error-EMA**. Phase 8.2 separately *validated* a **class-direction tap-drift** trigger — the direction the
SCFF taps move — which is invariant to a nuisance covariate (spine-clean) while the magnitude-of-shift null false-fires; it
leads the error but was **not shipped** (DDM consumes an error rate), so it is the north-star gate upgrade. The gate turns
out to be a **safety** mechanism
(always-pay forgets more), not just a cost-saver.
- **Onward:** [`../phase8/README.md`](../phase8/README.md) · [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S6 / S12)
- **Used in:** Phase 8 (committed), 9, 10

### Grid cadence (sleep timing)
A **regular** sleep grid (fire every k inputs) rather than boundary-aligned sleep — because the worst mid-stream
point falls *inside* a segment, not at a task boundary the model can't see. Phase 8 shipped grid-8; the Phase-9
freeze, on a true lifelong revisit stream, re-confirmed the knee at **grid-4** (worst-BWT −0.028 vs grid-8's −0.317).
Drift-rate-conditional.
- **Onward:** [`../phase9/README.md`](../phase9/README.md) · [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (S7 / S13)
- **Used in:** Phase 8 (grid-8), 9 (grid-4 freeze), 10 (the cadence frontier)

### proto-reanchor (read-side calibration)
The Phase-9 read-side defense for the Phase-6 input-transducer directional residual: **re-forward the raw LUT
prototypes through the current bulk** under the shift (the plan's own sleep mechanism, direction-grounded, no
covariance estimate) and re-anchor the head. Recovers retention 0.787 → 0.986 — overturning the planned SLDA
covariance re-estimate.
- **Onward:** [`../phase9/README.md`](../phase9/README.md)
- **Used in:** Phase 9 (P9.4)

### The cost meter (ADC-centred, behavioral)
The Phase-8 energy model: a relative-pJ, ADC-centred macro-model (NeuroSim / ISAAC / PUMA level, Horowitz-anchored),
**not SPICE**. It prices the analog crossbar (MACs near-free, only the ADC taxed) against a digital von-Neumann
baseline (every MAC pays the memory wall). It gives *relative* energy (the metered 80/20, bp_ratio, the 2×2 substrate
ablation), never an absolute Joule.
- **Onward:** [`../phase8/README.md`](../phase8/README.md)
- **Used in:** Phase 8 (the meter), 10 (the Pareto energy)

### ER-strong / BP+replay (the P10 racer)
The fair opponent Phase 10 races: a **tuned, budget-matched experience-replay** backprop learner (Prabhu CVPR'23 —
under a matched FLOPs+bytes budget, ER is *strong*, not a strawman), byte-matched to OURS's LUT and tuned on a
disjoint seed. The honest verdict: OURS ties it on the continual home, trails on natural digits, wins safety + noise;
a small tuned ER *dominates* OURS on a same-substrate (accuracy × energy) Pareto (OURS's wins live off that axis).
- **Onward:** [`../phase10/README.md`](../phase10/README.md)
- **Used in:** Phase 10 (the existential race)
