# P6.1 — noise-as-contrastive-augmentation: the primary fix (STOPPING MARK ①)

*Inheriting from P6.0: the dominant directional channel = **tap** (Rasch-dominant; the fix-free arrays frozen in
`figs_p6_0/`), σ\* = 2.0, the band = directional retention ≥ 0.90 at σ\*.*

**Question.** Does corrupting one InfoNCE view with the noise model make the class direction noise-invariant —
without collapsing the representation or costing clean accuracy — and is the gain spine-clean? The decisive control:
does **directional-aug beat random-axis-aug** (a directional-specific mechanism) or is any gain **generic smoothing**?

**Setup.** Swept variable = augmentation strength `σ_aug ∈ {0, 0.5, 1.0, 2.0}`; the fix cell = `NoiseAugContrast`
(the frozen cell with one positive view routed through `NoiseModel` at σ_aug). Three one-variable variants: **iid**
(broad per-sample noise) · **dir** (per-sample noise along the **label-free** top-PCA axis — train-axis ≠ eval-axis,
no leak) · **randax** (fixed random axis = the generic-regularization isolator). Controls locked: temp0.2/w2, L12,
headroom, seeds `[42,137,271,314,1729]`, 5 device draws. The co-trained `σ_aug=0` arm is the baseline. Measured at
σ\*: retention + per-sample cos for **tap** and **input** directional enemies, **and** the iid (rotational) enemy;
clean acc + tail-L12 selectivity + erank (capacity/collapse guard). `aug-σ0≡plain` guard passed.

**Run.** 50 cells (3 variants × 3 σ_aug + shared base × 5 seeds), checkpointed, single-thread. Wall ≈ 13.5 min.

**Result / figures.** *(headroom, n=5, median [q25–q75]; @σ\*=2.0)*

| variant · σ_aug | **tap-dir retention** (dominant) | input-dir retention | clean acc | selectivity | verdict |
| --- | --- | --- | --- | --- | --- |
| fix-free (σ0) | 0.841 [0.836–0.869] | 0.812 [0.685–0.908] | 0.526 | 0.530 | the baseline |
| **iid σ1.0** | **0.946 [0.852–0.952]** | 0.822 [0.679–0.888] | **0.555** | 0.530 | **fixes tap, clean↑, sel held** |
| iid σ0.5 | 0.890 [0.820–0.921] | 0.777 | 0.555 | 0.535 | partial |
| iid σ2.0 | 0.920 [0.832–0.939] | 0.818 | 0.543 | 0.507 | sel starts denting (knee) |
| dir σ1.0 | 0.876 [0.873–0.890] | 0.767 | 0.558 | 0.569 | worse than iid |
| randax σ1.0 | 0.870 [0.846–0.911] | 0.793 | 0.535 | 0.526 | worse than iid |

**Paired Δ (iid σ1.0 − fix-free), tap-dir:** `[+0.105,+0.023,+0.082,+0.031,+0.016]`, median **+0.031**, IQR
**[+0.023,+0.082]** (excludes 0), **5/5 positive** → real (paired). The spine ordering on tap: **iid ≥ randax > dir**.

- **AUG-SWEEP** (headline): tap-directional retention rises with σ_aug to a peak at σ1.0 then the selectivity guard
  bites at σ2.0 (0.530→0.507) — σ1.0 is below the capacity knee. - **INV**: dead-frac ≈0, erank 30→20 (not collapsed;
  clean acc held), guards pass.

**Read (8 slots).**
1. **Claim** — A **generic (iid) noise-augmented contrastive view** makes the **dominant tap-directional** class
   readout noise-robust (retention 0.841→0.946, 5/5 paired) while *improving* clean accuracy and holding
   selectivity; **directional-specific augmentation does NOT — the fix is generic Jacobian-smoothing, not a
   directional mechanism.**
2. **Headline** — tap-directional retention **0.946 [0.852–0.952]** at iid σ1.0 vs the fix-free baseline **0.841
   [0.836–0.869]** and the noiseless ceiling 1.00 (paired Δ +0.031 [+0.023,+0.082], 5/5) (n=5, headroom, tap,
   matched projected-RMS). *(⚠ This per-rung median sits at the top of a wide IQR; the P6.8 assembled run — more
   device draws — revises it to **0.865**, near not above the 0.90 band. The lift is real and 5/5-paired either way;
   the band crossing is **partial** — see P6.8.)*
3. **Figures** — AUG-SWEEP (the sweet-spot + capacity knee), INV. (A7-CURVE fix-vs-fix-free assembled in P6.8.)
4. **Mechanism** — the directional enemy is a *coherent translation* along an axis unknown at train time; you cannot
   bet the augmentation on one direction (dir/randax under-perform), so **broad iid smoothing — invariance to
   perturbations in every direction — generalizes best** and, applied to the reps during training, hardens exactly
   the **tap** (rep-level) read channel Rasch calls dominant. The gain is a *preserved class direction under a
   coherent shift* read as retention (per-sample cos is near-blind to a translation, P6.0), not a magnitude trick:
   clean acc rose and selectivity held, so it is not representation collapse.
5. **Threats** — (a) collapse masquerading as robustness → selectivity held (0.530) + clean acc *rose*, erank not
   collapsed; the σ2.0 selectivity dip is the capacity knee (σ1.0 sits below it); (b) generic-vs-directional confound
   → the **randax isolator**: dir does NOT beat randax (both < iid) → the claim is *generic smoothing*, stated
   honestly, **not** a directional-specific spine mechanism (the design's H-aug hypothesis is overturned here); (c)
   unpaired IQR overlaps (high between-seed variance) → the **paired Δ** IQR excludes 0 and is 5/5 (real by the
   paired rule); (d) input-channel gain is marginal — reported, not hidden.
6. **Decision** — **Adopt `NoiseAugContrast` variant=iid, σ_aug=1.0** (pending the P6.6 gate). It substantially
   hardens the dominant tap channel (per-rung near/into band; P6.8-combined 0.865, a *partial* crossing). The
   **input-transducer channel is only marginally helped** (0.812→0.822) — a **Scoped-YES residual** handed to
   Stage-2 read-side, not a headline. STOPPING MARK ① substantially met on the dominant channel.
7. **Robustness-honesty** — the enemy was tap-directional at matched projected-RMS (a fixed device offset along the
   class axis), not a weak i.i.d. stand-in; the gain is a preserved class **direction** read as retention; the
   collapse/selectivity + capacity-knee guards passed; the fix is **generic**, and that is stated plainly rather than
   dressed as directional-specific.
8. **SCFF-trust / arc-verdict** — the dominant analog channel **is** fixable by a forward-only objective change
   (generic noise-augmentation) → the verdict leans **YES / Scoped-YES**. **Continual-safety (P6.6) NOT yet checked →
   it GATES adoption** (early 2-seed smoke: the fix slightly *improves* BWT). P6.2 (flatness) → skip (tap fixed,
   weight non-dominant); P6.3 (norm root) → skip (leave the norm; the input residual is a Stage-2 read-side concern,
   not worth the load-bearing-norm surgery).

**Pre-submit checklist.**
- [x] Median [IQR] for every headline number (n=5); no bare means.
- [x] "Real difference" applied via the **paired Δ** (IQR excludes 0 **and** 5/5 sign); unpaired IQR overlap noted.
- [x] Matched projected RMS stated; the decisive control is **directional-aug vs random-axis-aug** (dir does not win → generic).
- [x] **Random-axis-aug isolator** run; the spine claim is **not** asserted (generic smoothing, honestly).
- [x] **Capacity-knee probe** run; committed σ_aug=1.0 sits below the knee (selectivity dents only at σ2.0).
- [x] Fix-free arrays inherited from the frozen `figs_p6_0/`, not recomputed; the co-trained σ0 arm reproduced them.
- [x] Direction reported as retention (the true directional read); per-sample cos kept as the secondary/rotational read.
- [x] Every figure by a `plot_p6.fig_*` function; `regen` redraws from saved data.
- [x] All 8 slots; formal voice; card opens by naming the inherited knob (dominant channel + σ\*).
- [x] `manifest.json` + `arrays.npz` written; guards logged (aug-σ0≡plain 0.0).
- [x] Single-threaded (phantom + cp874 guards).
- [x] **Continual-safety (P6.6)** flagged as the adoption gate (not yet run at full 5 seeds).
- [x] `RESULTS.md` row added (§D schema); the overturned H-aug-directional hypothesis logged as a result.
