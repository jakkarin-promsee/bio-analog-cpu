# Experiment P3.3 — the continual veto: does the objective reframe re-earn the Phase-1 win?

> **Status: ✅ RUN COMPLETE (2026-06-22) — VETO PASSED (and slightly IMPROVED). The objective reframe is ADOPTED;
> Phase 3 CLOSES.** The non-negotiable test: does `contrast + coordination` (the P3.0–P3.2 winner) preserve the
> Phase-1 continual win? It does — and **beats the energy baseline** (BWT **−0.017** vs −0.026, final **0.954** vs
> 0.938, disjoint-IQR, 3 seeds), with the contrastive SCFF-probe **flat** (doesn't forget) and sleep decisive.
> Mirror of P2.6. Spec: [`../README.md`](../README.md) §P3.3. Reporting: [`../result-format.md`](../result-format.md).
> Builds on [`../exp2/experiment-2.md`](../exp2/experiment-2.md) (the validated cell) + P2.6/exp4 (the win it must
> preserve).

## Question

The Phase-1 continual win rested on **energy-SCFF being forgetting-robust** (clusters unsupervised → new classes
*add* clusters, don't overwrite). The new objective is **contrastive** (InfoNCE, in-batch negatives) — it *might*
bias to the current task and forget. So: **does `contrast + coordination` re-earn the continual win (ACC + BWT)
on the exp4/P2.6 class-incremental digits stream — or does the reframe cost it?**

**Pass gate.** BWT(contrast+coord) ≥ BWT(energy) − 0.02 **AND** the contrast all-class SCFF-probe stays flat
(doesn't forget).

## Setup

Reuses the P2.6 continual harness (`run_exp6` helpers) — one variable: the SCFF objective. Single deep stack
(L=4) + sleep-consolidated readout (the P3.2 winner is a single deep contrast+coordination stack, not P2.6's
boosted blocks). Conditions: **gd** (catastrophic baseline) · **energy_sleep** (SCFF2 healthy cell + sleep — the
Phase-1/2 baseline) · **contrast_sleep** (`SCFFContrastOLU` L=4, w=2 + sleep — THE new recipe) · **contrast_nosleep**
(rot control). Digits, tasks `[[0,1]…[8,9]]`; 3 seeds `[42,137,271]`, median + IQR; single-threaded.

## Result / figures

**Run 2026-06-22**, 3 seeds. [CONT veto](figs_p3_3_digits/CONT_veto.png) (trajectory + ACC/BWT + SCFF-probe
stability). `arrays.npz` + `manifest.json` saved.

| condition (n=3 median) | final all-class ACC | BWT [IQR] | forgetting |
| --- | --- | --- | --- |
| GD-online (catastrophic) | 0.186 | −0.992 | 0.992 |
| energy-SCFF + sleep (P1/P2 base) | 0.938 | −0.026 [−0.027,−0.022] | 0.026 |
| **contrast+coord + sleep (NEW)** | **0.954** | **−0.017 [−0.020,−0.015]** | **0.017** |
| contrast+coord no-sleep (rot) | 0.214 | −0.954 | 0.954 |

**Contrast SCFF-probe (all-class): [0.938, 0.938, 0.935, 0.940, 0.936] — FLAT** (the contrastive objective does
not forget). The contrast BWT IQR [−0.020,−0.015] is **disjoint above** energy's [−0.027,−0.022] (3/3 seeds
better). Sleep decisive (no-sleep rots to 0.214).

## Read (eight-slot, compressed)

1. **Claim.** **The objective reframe re-earns the Phase-1 continual win — in fact slightly *improves* it.** The
   contrastive+coordination cell is forgetting-robust just like energy-SCFF (SCFF-probe flat: new classes add
   structure, don't overwrite), sleep restores near-ceiling, and it lands **above** the energy baseline on both
   ACC (0.954 vs 0.938) and BWT (−0.017 vs −0.026, disjoint-IQR). The better static objective helps the continual
   regime too.
2. **Number.** contrast 0.954 / −0.017 [−0.020,−0.015]; energy 0.938 / −0.026 [−0.027,−0.022]; GD 0.186 / −0.992;
   no-sleep 0.214 / −0.954. SCFF-probe flat 0.938→0.936. n=3, 3/3 contrast > energy.
3. **Figures.** [CONT veto](figs_p3_3_digits/CONT_veto.png) — contrast tracks/exceeds energy; both flat SCFF-probes
   ≫ rot/GD.
4. **Mechanism.** Contrast discriminates *instances* unsupervised, per-sample — like energy's density clustering,
   new classes *add* discriminable structure rather than overwriting old, so the all-class probe stays flat; only
   the small readout goes stale, and sleep re-fits it cheaply. The InfoNCE-bias-to-current-task worry did **not**
   materialize (per-sample, no batch statistics — the same continual-safe property as the energy cell).
5. **Threats.** (a) digits is easy/low-D — *magnitudes* are task-specific; the *structure* (contrast ≈/> energy
   ≫ rot/GD; SCFF flat) is load-bearing and matches exp4/P2.6. (b) 3 seeds (the exp4 set); the contrast>energy
   margin is small but disjoint-IQR. (c) full-buffer sleep; LUT (⅓-store, exp4-validated) is the compression
   follow-up.
6. **Decision.** **VETO PASSED → ADOPT the objective reframe → Phase 3 CLOSES.** `contrast + coordination` is a
   strict upgrade over energy-goodness: it *composes depth* where energy can't (P3.2) **and** preserves/improves
   the continual win (here), staying forward-only + per-sample (the only new cost is in-batch negatives = the LUT
   sampler). *(Full in ## Decision.)*
7. **Substrate.** forward-only bulk (gradient-isolated between coordination windows), per-sample norm (no batch
   stats → continual-safe by construction), in-batch negatives via the LUT; tiny sleep-consolidated readout
   (~the GD 20%). Same substrate shape as P2.6, better objective.
8. **Continual-preservation (the veto).** ✅ PASS — re-earned and improved; SCFF forgetting-robust; sleep decisive.

## Decision

**VETO PASSED — the objective reframe is adopted; Phase 3 is complete.** Across the phase: P3.0 (the objective
family is the lever; contrast preserves class info), P3.1 (coordination eases the decline; flat-CIFAR caps it),
P3.2 (with depth headroom, contrast + coordination *composes* depth — rises, matches/beats GD, overturning P2.2's
"intrinsic to locality"), and P3.3 (it *re-earns and improves* the continual win). The carried recipe:

> **`[contrast (InfoNCE, two-mask views) + cross-layer coordination window w≥2]` SCFF bulk + a tiny
> sleep-consolidated GD readout** — forward-only, per-sample, continual-safe by construction; the only new cost
> vs energy-SCFF is an in-batch / LUT negative pool.

**This supersedes energy-goodness as the SCFF objective for draft 6.0.** Hand-off: the **Phase-5** maintenance work
(Ch7 gate + sleep-cadence) now tunes against *this* cell's drift (Phase 4 characterized the cell first); the
natural-data / larger-scale and direct-feedback questions are open follow-ups, not blockers.

## References

- **P3.2** ([`../exp2/experiment-2.md`](../exp2/experiment-2.md)) — the validated static cell this veto-tests.
- **P2.6** ([`../../phase2/exp6/experiment-6.md`](../../phase2/exp6/experiment-6.md)) — the harness + the energy
  baseline this matches/beats. **exp4** — the original continual win.
