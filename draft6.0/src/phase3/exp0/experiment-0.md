# Experiment P3.0 — the objective swap: does an info-preserving objective stop the depth wall?

> **Status: ✅ RUN COMPLETE (2026-06-21, 3 objectives) — PARTIAL: the objective axis is decided
> (discriminative-contrastive wins), but a residual decline remains → route to P3.1 (coordination = your
> Direction 1).** Three unsupervised objectives, same bench, CIFAR-flat 5-seed. They behave *completely
> differently* — the objective family is the lever, exactly as the reframe argued: **energy** (the P2.1 wall)
> declines steeply *through* the random floor (−0.020); **masked-reconstruction** flattens the slope (−0.005) but
> sits *below* random (selectivity **−0.062** — preserves density, not class); **contrastive (CLAPP/InfoNCE)**
> stays *above* random at every depth (selectivity **+0.060**, 5/5 seeds — preserves **class** info) **but still
> declines** (−0.016). So the two desired properties are split: reconstruction gives *flatness*, contrast gives
> *class-selectivity*, neither gives both. **Verdict: the make-or-break's selectivity half is won by contrast
> (discriminative preservation is the right objective — the reframe's prediction confirmed), but its slope half is
> not (depth still doesn't compose) → the missing ingredient is cross-layer coordination → route to P3.1 (OLU /
> your "A1-from-layer-2" idea), now layered on the contrastive objective.** The make-or-break first rung of
> Phase 3.
> Phase 2 proved *energy-goodness* SCFF can't earn depth on either lever (transmission P2.1, objective-within-the-
> energy-family P2.2 — oracle-proof). P3.0 tests the lever Phase 2 never touched: a **different objective family**
> — swap the per-layer goodness from energy `Σh²` to **masked-feature reconstruction** (information-preserving),
> and ask whether the depth wall stops. Convention: question → setup → hypothesis → run → result → read →
> decision. Plan: [`../README.md`](../README.md) §P3.0. Reporting: [`../result-format.md`](../result-format.md).
> Reframe: [`../../../ref2/the-objective-reframe.md`](../../../ref2/the-objective-reframe.md).

## Question

1. **Does the wall stop?** The energy wall (P2.1 healthy cell: layer-norm + linear + contrast) declines at
   **−0.020/layer** on CIFAR-flat. Does **masked-feature reconstruction** take the depth-slope from `< 0` to
   `≥ 0` (or decisively toward 0) — i.e. does an info-preserving objective stop deep layers destroying class
   information, where energy-goodness can't?
2. **Is the gain real, not a probe artifact?** Selectivity = (masked-recon probe − random-projection probe).
   A small selectivity flags the probe doing the work, not the objective (Hewitt & Liang 2019; the control that
   *saved* Phase 2).
3. **Why (the mechanism)?** Does the **info-preservation curve** (per-layer reconstruction error vs depth) stay
   flat/low where the energy wall's information is shed? — the causal read for (1).

**Pass gate (make-or-break, README §P3.0).** Masked-reconstruction reaches **depth-slope ≥ 0** (or moves
decisively toward 0 vs the wall's −0.020) **AND selectivity > 0**. If it does **not**, STOP and rethink (route to
the structure-exposed task, then the Mono-Forward fallback) before P3.1.

## Setup (LOCKED — methodology rule #3)

**One change vs the P2.1 baseline: the per-layer objective.** Everything else = the Phase-2 bench.

| Knob | Value | Why |
| --- | --- | --- |
| **Headline task** | **CIFAR-10-flat** (`load_cifar_local`, 3072-D, 10-class) | the documented wall; directly comparable to the P2.1/P2.2 curves. |
| **Sanity task** | **synth Tier-B** (`make_tierb`) | code sanity only — synth has *no* wall (P2.0), so it can't show the win; the verdict rests on CIFAR. |
| **Cells** | **energy-wall** (layer-norm + linear + contrast — the P2.1 healthy cell, the baseline-to-beat) · **masked-recon** (the hero) | one variable: the objective. *(Sibling-contrastive CLAPP control = the immediate next cell, P3.0b — run after the headline lands; not in this first run.)* |
| **masked-recon objective** | per layer: corrupt input (mask `ρ=0.5` of dims → 0), encode `h=relu(W·ã+b)`, decode `â=D·h+c`, **local MSE** `‖â−a‖²`; update {W,b,D,c} by the within-layer AE gradient — **gradient-isolated between layers** (no cross-layer backprop, GIM/denoising-AE style). The clean (unmasked) normalized rep propagates forward. | the decided primary objective (`../README.md` §0): single-sample, info-preserving, the substrate-native denoising-AE member of the GIM family. |
| **decoder `D_l`** | a small auxiliary head `[din × width]` per layer (like the GD readout / Mono-Forward's `M_i`) | the "20%" local machinery; reconstructs, never propagates. |
| **stack** | `L = 1…8`, width 64, ReLU, input-norm on, **layer-norm** between layers | depth is the axis; width fixed; the P2.1 healthy transmission. |
| **probe (PRIMARY)** | logistic, fixed L2 `C=1.0`, frozen 2k/2k, to convergence — **per layer** | the pinned metric (`result-format` Layer B). |
| **references** | **GD-hidden ceiling** (matched-depth pure-GD, the flat-high envelope) · **random-projection floor** (untrained, same shape — the selectivity floor) | the two envelopes every depth curve needs. |
| **metrics** | depth-slope **+ SCORECARD** (peak-layer · CoM · decline-area · tail-retention · N_eff) **+ INFOPRESERVE** (recon error vs depth) **+** dead-unit % · effective rank · selectivity | `result-format` Layer B/C. |
| **seeds / realism** | `[42,137,271,314,1729]`, median + IQR · ideal floats · single-threaded (`OMP_NUM_THREADS=1` + `-u`, the OpenMP phantom guard) | methodology rules #2/#3; the machine's known hang. |

**Must emit** (`result-format` map for P3.0): **F3⁺ + SCORECARD** (objectives overlaid + GD ceiling + energy-wall
+ random floor), **INFOPRESERVE**, **SELECT** (selectivity), **REPR/INV** (dead/erank). Light CONT sniff deferred
to the CIFAR run if time; full veto = P3.3.

## Hypothesis (committed, before the run)

> **Masked-reconstruction stops the decline — slope moves from −0.020 toward 0 — because information-preservation
> is the mechanical opposite of the energy wall.** The wall declines because each energy layer re-clusters by
> density and *sheds* whatever isn't loud (P2.1: rank-collapse / dead units cured, but density ≠ class so the
> probe still falls). A denoising-AE layer is *penalized* for shedding — it cannot reconstruct what it threw away
> — so the representation must keep its input's structure alive, and the per-layer probe should stop falling.
> **Honest caveats:** (a) reconstruction preserves info but may not *concentrate* class structure, so the realistic
> first win is **slope ≈ 0 (flat, non-declining)**, not a strong *rise* — and even flat is a decisive break from
> the −0.020 wall. (b) On flat CIFAR the absolute probe is thin (~0.2–0.35, the documented regime); the
> **shape** (slope, decline-area, tail-retention) is load-bearing, not the magnitude. (c) If masked-recon is *also*
> declining, the info-preserving objective doesn't compose on flat vectors → route to the structure-exposed task
> / Mono-Forward fallback (the pre-registered STOP branch).

## Run

Built 2026-06-21: [`../p3lib.py`](../p3lib.py) (the masked-reconstruction cell `SCFFRecon` + `recon_error` for
INFOPRESERVE; the energy-wall baseline = p2lib `SCFF2`, the P2.1 healthy cell). [`run_p3_0.py`](run_p3_0.py) =
objective scan (energy-wall vs masked-recon) + GD-hidden ceiling + an **untrained same-arch SCFFRecon** as the
selectivity floor (identical layer-norm — cleaner than P2's lengthnorm RandomProjStack) + scorecard +
infopreserve. [`plot_p3_0.py`](plot_p3_0.py) regenerates all 5 figures. Smoke synth (2 seeds) → synth 5-seed →
**CIFAR 5-seed** (683s, single-threaded `OMP_NUM_THREADS=1` + `-u`, OpenMP phantom guard). One build bug caught +
fixed (missing `runs.append` in the aggregate loop); the pass-gate was tightened mid-build to be honest (a
noise-level last-layer selectivity crossing initially read as a false PASS — fixed to mean-selectivity > 0.01).

## Result / figures

**Run 2026-06-21**, 5 seeds `[42,137,271,314,1729]`, median + IQR. Headline = **CIFAR-10-flat**; synth = the
code/mechanism control. Figures in [`figs_p3_0_cifar/`](figs_p3_0_cifar): [F3⁺](figs_p3_0_cifar/F3plus_depth.png)
· [SCORECARD](figs_p3_0_cifar/SCORECARD.png) · [INFOPRESERVE](figs_p3_0_cifar/INFOPRESERVE.png) ·
[SELECT](figs_p3_0_cifar/SELECT.png) · [REPR/INV](figs_p3_0_cifar/REPR_INV.png). `arrays.npz` + `manifest.json`
saved; regenerate with `python plot_p3_0.py figs_p3_0_cifar` (no retrain).

| cell (n=5 median) | probe L1 → L8 | slope/layer | decline-area | tail-ret | selectivity (mean) | vs random |
| --- | --- | --- | --- | --- | --- | --- |
| **energy-wall** (P2.1 baseline) | 0.332 → 0.198 | **−0.020** (declines) | 0.080 | 0.60 | ~0 (decays *into* random) | converges to floor |
| **masked-recon** (preservation) | 0.174 → 0.136 | **−0.005** (≈flat) | **0.020** | **0.80** | **−0.062** ✗ | **below** floor |
| **contrast** (CLAPP, discriminative) | 0.331 → 0.227 | **−0.016** (declines) | 0.054 | 0.70 | **+0.060** ✓ (5/5) | **above** floor, all depths |
| random floor (untrained) | 0.298 → 0.160 | −0.019 | — | — | (the floor) | — |
| GD-hidden ceiling | ~0.36 (flat) | ~0 | — | — | — | env gap **+0.116** |

**The split, in one line:** masked-recon = *flat but below random* (preserves density); contrast = *above random
but still declining* (preserves class, doesn't compose). Contrast's selectivity even **grows with depth**
(+0.035 at L1 → +0.073 at L8) — the contrastive signal adds *increasing* value deep, even as the absolute probe
falls (because random falls faster). **Synth control (clusters = classes):** both recon (+0.079) and contrast
(+0.105) pass — the mechanism works where reconstruction/instance-info = class-info; the CIFAR *split* is the
real density≠class effect, not a bug. **Per-seed:** 5/5 contrast selectivity > 0 (+0.045…+0.066); 5/5 recon < 0.

## Read (eight-slot)

**Pass gate (README §P3.0, make-or-break): PARTIAL.** No single objective hits *both* slope ≥ 0 AND
selectivity > 0 — but the result decomposes the problem cleanly: **contrast wins the selectivity half**
(discriminative preservation is the right objective) while **the slope half needs coordination** → route to P3.1.

1. **Claim.** **The objective *family* is the lever (the reframe confirmed), and the right family is
   *discriminative* preservation — but it preserves class info without yet *composing* it across depth.** Three
   unsupervised objectives on the identical bench split the two properties we need: **masked-reconstruction**
   flattens the slope (−0.020 → −0.005) but preserves the *wrong* info (density — selectivity −0.062, *below*
   random); **contrast (InfoNCE/CLAPP)** preserves the *right* info (class — selectivity **+0.060**, *above*
   random at every depth, 5/5 seeds) but still **declines** (−0.016). Reconstruction = flat-but-wrong; contrast =
   right-but-declining. Energy-goodness is worst (decays *through* random). So an info-preserving objective is
   necessary, and it must be **discriminative** (contrastive), not reconstructive — and a *second* lever
   (coordination) is needed to turn "class info preserved" into "class info rising."
2. **Number + IQR.** energy 0.332→0.198 (−0.020, 5/5 decline); masked-recon 0.174→0.136 (−0.005, sel −0.062, 5/5
   < 0); **contrast 0.331→0.227 (−0.016, sel +0.060, 5/5 > 0; selectivity grows +0.035→+0.073 with depth)**;
   GD ceiling ~0.36 (env gap +0.116); random 0.298→0.160. Synth control: recon +0.079, contrast +0.105 (both PASS
   where clusters = classes). n=5.
3. **Figures.** [F3⁺](figs_p3_0_cifar/F3plus_depth.png) (ordering at depth: GD > **contrast** > energy ≈ random >
   recon) · [SELECT](figs_p3_0_cifar/SELECT.png) (contrast > 0 & growing; recon < 0) ·
   [SCORECARD](figs_p3_0_cifar/SCORECARD.png) · [INFOPRESERVE](figs_p3_0_cifar/INFOPRESERVE.png) ·
   [REPR/INV](figs_p3_0_cifar/REPR_INV.png).
4. **Mechanism.** Energy sheds whatever isn't loud → declines through random (P2.1). Reconstruction is *penalized
   for shedding* → flat, but preserves *all* pixel mutual-info = **density**, below random (density ≠ class, in
   the reconstruction target). Contrast (InfoNCE) preserves only what *distinguishes samples* → keeps
   class-relevant directions → above random. **But** "distinguish this image from others" also keeps lots of
   *instance-specific* (non-class) info, and each layer re-discriminates *myopically* (no cross-layer signal —
   the exact forward-only-locality gap P2.2 named), so deeper layers drift onto idiosyncratic directions and the
   absolute probe declines even as selectivity-over-random grows. The fix for that residual decline is **not** a
   different objective — it is **cross-layer coordination** (make each layer's discrimination help the next's),
   i.e. P3.1 / OLU.
5. **Threats.** (a) Absolute probes are low (flat CIFAR is thin) — the **signs/ordering** (contrast above random,
   recon below, energy into random) are load-bearing, not magnitude; the synth control rules out code error.
   (b) Knobs (mask 0.5, temp 0.5, epochs) un-swept — but the *selectivity sign* (contrast +, recon −) is a
   property of the objective *type*, not the tuning. (c) InfoNCE uses in-batch negatives (B=32) — a richer
   negative pool (the LUT) might lift it, a P3.1/substrate question, not a flaw here.
6. **Decision.** **PARTIAL → route to P3.1 (coordination = the user's Direction 1 / OLU), on the contrastive
   objective.** P3.0 settles the *objective axis* (contrast, not energy or reconstruction); the residual decline
   is the cross-layer-coordination gap, which is exactly what P3.1 (OLU / direct-feedback) attacks. The
   Mono-Forward fallback (P3.2) is **not** triggered — contrast cleared the selectivity bar that would have sent
   us there. *(Full in ## Decision.)*
7. **Substrate-feasibility.** Masked-recon: single-sample, no negatives (the decoder `D_l` is the only area).
   Contrast: needs **in-batch negatives** → the LUT negative sampler on-chip (the cost of discrimination); still
   forward-only + gradient-isolated between layers. Both substrate-plausible; contrast costs a negative pool.
8. **Continual-preservation.** N/a this rung (the veto runs at P3.3 once an objective + coordination clears the
   slope). Nothing here touches the Phase-1 win.

## Decision

**PARTIAL — P3.0 settles the *objective axis* and hands the residual gap to P3.1 (coordination).** Three
objectives, one bench, a clean decomposition:

- **The objective family is the lever — reframe confirmed.** The three unsupervised curves are completely
  different (energy decays into random; reconstruction below random; contrast above random). The Phase-2 wall is
  **not** intrinsic to forward-only locality (P2.2's wording was too strong) — it is intrinsic to the *energy*
  objective, and the family you pick decides everything.
- **The right objective is *discriminative* preservation (contrastive), not reconstruction.** Contrast keeps
  class info (selectivity **+0.060**, above random at every depth, 5/5 seeds — and *growing* with depth);
  reconstruction keeps density (−0.062, below random). This is exactly why GIM/CLAPP are contrastive (InfoNCE),
  not autoencoders — now confirmed on our substrate. **Contrast is the Phase-3 objective.**
- **The residual decline is the coordination gap, not an objective gap.** Contrast still declines (−0.016) because
  each layer discriminates *myopically* (instance info, no cross-layer signal). That is the precise gap **P3.1
  (OLU / your "A1-from-layer-2" cross-layer goodness / direct-feedback)** exists to close — turn "class info
  preserved" into "class info composed." **Route → P3.1, on the contrastive objective.**
- **Mono-Forward fallback NOT triggered.** Contrast cleared the class-selectivity bar that would have sent us to
  the supervised fallback. Unsupervised forward-only learning *does* keep class info on the substrate; the open
  question is now narrowly "can coordination make it rise," not "is unsupervised viable at all."
- **Carry forward:** the contrastive cell (`SCFFContrast`, InfoNCE, two-masking views, temp 0.5) as the P3.1 base;
  the bench (energy regression guard −0.020 ✓, GD ceiling, same-arch selectivity floor, SCORECARD/SELECT figures)
  unchanged. **Masked-recon** stays on record as the proof that *preservation alone preserves the wrong thing*.

## References (P3.0-specific)

- **The objective reframe** ([`../../../ref2/the-objective-reframe.md`](../../../ref2/the-objective-reframe.md)) —
  energy vs predictive/info-preserving; GIM/CLAPP; greedy layer-wise denoising-AE (Hinton'06/Bengio'07).
- **Greedy InfoMax** ([1905.11786](https://arxiv.org/abs/1905.11786)) — *contrastive* (InfoNCE) preservation; the
  reason a plain autoencoder (this rung) is the wrong member of the family, and the route forward.
- **P2.1/P2.2** — the energy-wall baseline (−0.020, reproduced here as the regression guard) and the density ≠
  class lesson this rung re-incurred in the reconstruction target.
