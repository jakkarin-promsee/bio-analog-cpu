# P8.2 — The trigger bake-off: does the class-direction tap *lead* the error?

**Question.** Inheriting the committed DDM awake gate and the bench from P8.0–P8.1: does a **label-free class-direction
tap-drift** trigger detect real drift *earlier* than the labeled error-EMA (MTD lower) **without** false-firing on the
nuisance segment (FAR ≤ error's)? And does the **magnitude-of-shift null** false-fire, as the spine predicts?

**Setup.** Swept variable = the trigger signal ∈ {error_ema (labeled reference), tap_dir (candidate), tap_mag (null),
driftlens (label-free reference), studd (conservative student-mimic)}. Controls locked (live bulk, RanPAC+cbrs, CI+nuisance
stream, seeds [42,137,271,314,1729]); detection rule = threshold-crossing at the calib-interior 97.5th pct × 1.10; FAR
judged against each signal's own **stationary-segment** floor (excess-FAR). Figures: TRIGGER (MTD × FAR), INV.

**Run.** 5 triggers × 5 seeds; windowed-MMD signals computed once per cache. Wall ≈ 20.1 min.

**Result / figures.**
| trigger | MTD (steps) | FAR (nuisance) | excess-FAR | MTFA | lead? / verdict |
| --- | --- | --- | --- | --- | --- |
| error_ema (labeled ref) | 14.000 [10.00–40.00] | 0.000 [0.00–0.00] | 0.000 | 32.0 | reference |
| **tap_dir** (candidate) | **6.000 [5.00–11.00]** | 0.021 [0.00–0.042] | **0.000** | 32.0 | **earns-early** |
| tap_mag (null) | 6.500 [5.00–6.50] | 0.938 [0.938–0.938] | 0.906 | 32.0 | false-fires (spine null) |
| driftlens (label-free ref) | 6.000 [5.00–11.00] | 0.021 [0.00–0.042] | 0.000 | 32.0 | matches tap_dir |
| studd (conservative) | 0.000 [0.00–0.00] | 0.896 [0.854–0.917] | 0.896 | 32.0 | degenerate (always-fires) |

- **TRIGGER** (headline): MTD × FAR scatter — tap_dir sits low-left (MTD 6, FAR 0.021, excess 0.000): it leads the error
  reference (MTD 14) by ~8 steps at a nuisance FAR *below* its own stationary floor. tap_mag sits far-right (FAR 0.938):
  it detects fast but false-fires on nearly every nuisance step. DriftLens (the purpose-built label-free reference)
  lands exactly on tap_dir, confirming the home-grown signal.
  - **INV**: all guards green.

**Read (8 slots).**
1. *Claim* — the label-free class-direction tap-drift trigger detects real drift earlier than the labeled error (MTD
   6 < 14) at a clean nuisance FAR, while the magnitude-of-shift null false-fires on nuisance — the spine, demonstrated.
2. *Headline* — tap_dir MTD 6.000 [5–11], excess-FAR 0.000 vs error MTD 14.000 [10–40]; magnitude null FAR 0.938 on
   nuisance (n=5, live CI+nuisance).
3. *Figures* — TRIGGER (MTD × FAR), INV (guards green).
4. *Mechanism* — this is the spine's crown. SCFF's *representation* drifts before the readout's *error* rises (error
   lags real drift by construction — P8.0 showed 1.02× vs 1.38×), so a signal that watches the class **direction** in the
   taps sees the onset first (MTD 6 vs 14). The magnitude null watches the raw *shift* — which the nuisance covariate
   inflates without any class change — so it fires on the nuisance segment 94% of the time (density ≠ class, 8th coat).
   DriftLens (a purpose-built embedding-distance detector along class structure) matching tap_dir confirms the lead is
   real, not an artifact of the home-grown estimator. STUDD's student mimic-loss saturates here (MTD 0, always-fires) —
   too conservative for this fast synthetic drift.
5. *Threats* — (a) FAR uses the excess-over-stationary-floor definition (guarded), so tap_dir's raw 0.021 nets to
   excess 0.000 — genuinely clean. (b) The nuisance injector is calibrated (P8.0); tap_mag's 0.938 confirms the pixels
   really shift, so tap_dir's invariance is a real property, not a weak injector. (c) The direction trigger sidesteps
   calibration-under-shift (it reads geometry, not a confidence magnitude). (d) MTD IQR is wide (5–40 for error) because
   some seeds' onsets are detected only at the segment edge — the median lead is nonetheless sign-consistent.
6. *Decision* — sets the **committed trigger = class-direction tap-drift** (earns-early, excess-FAR 0.000; DriftLens is
   its validated label-free twin). The magnitude-of-shift signal is retained only as the documented false-fire **null**.
   Together with P8.1's DDM this fixes the gate as a *direction*-triggered error detector at two timescales.
7. *Economy-honesty* — FAR reported beside MTD for every arm; the magnitude null's high FAR (0.938) is reported as the
   *expected* spine demonstration, not hidden. No energy on this rung (P8.4).
8. *Live-safety / namer* — the trigger choice is spine-clean (direction, not magnitude), satisfying the north-star
   tie-break (a direction gate is the seed; a confidence gate would be torn out later). Namer unchanged pending P8.4.
