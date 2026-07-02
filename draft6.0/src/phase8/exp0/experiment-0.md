# P8.0 — The bench: guards, the live drift, and is the detection problem even well-posed?

**Question.** Before any gate races, three things must be true or the whole ladder is narration: (1) the new
`partial_fit` primitive and the live loop reproduce the frozen apparatus bit-for-bit (guards); (2) the SCFF bulk
drifts as it learns but does **not** forget (`bulk_drift` bounded); (3) the detection problem is **well-posed** — a
class-direction signal moves at *real* class onsets and stays put under a *nuisance* covariate shift, while a
magnitude-of-shift signal does the opposite (the spine, made visible).

**Setup.** No swept method — this rung pins the bench. Controls locked: live `NoiseAugContrast` bulk
(SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0), committed RanPAC+cbrs head, the CI+nuisance
streaming schedule (warmup→stat→4×[gradual onset+plateau]→long settle→covariate-nuisance ramp→stat2), seeds
[42,137,271,314,1729]. Figures: DRIFT (+drift-visibility panel), INV (all seven guards + refs). Apparatus: p8lib
`build_cache` + `run_economy`; the nuisance injector = `g·x + α·1` (global gain 3.0 + all-ones offset 4.0) — a shift
SCFF's per-sample input layernorm provably removes to ~ε.

**Run.** 5 seeds, n_steps=336 per seed, guards evaluated once (seed-independent by construction). Wall ≈ 14.2 min.

**Result / figures.**

*Guards (any fail → STOP):*
| guard | measured | pass |
| --- | --- | --- |
| partial_fit_equiv (ranpac / slda) | max\|W_stream−W_batch\| = 4.11e-15 / 2.22e-16, pred-miss 0 | ✓ |
| fd_budget_gate | max\|analytic−FD\| = 3.47e-08 | ✓ |
| meter_proxy | fwd-MAC 1 556 000 ≡ readout_cost fwd_macs 1 556 000 (solve_dim 2000) | ✓ |
| detector_far (stationary floor) | {abs 0.0, ddm 0.0, adwin 0.0} | ✓ |
| scff_static_frozen | frozen-tap reproducibility 0.00e+00; static RanPAC acc 0.566 ≡ P7 static | ✓ |
| live_path_anchor | block-mode ≡ `continual_safety_heads` 0.00e+00 (AA ref 0.3602 = new 0.3602) | ✓ |
| cache_replay | deterministic replay 0.00e+00, fire-diff 0 | ✓ |

*Bench + drift-visibility:*
| read | value | vs reference | verdict |
| --- | --- | --- | --- |
| bulk_drift (min..max) | 0.627 .. 1.000 | bounded, > 0 everywhere | the bulk **doesn't forget** |
| always-pay ceiling | AA 0.448, f 1.00, FAR 1.00 | — | cost ceiling |
| oracle-cadence ref | AA 0.448, f 0.286, FAR 0.00 | (ref) | achievable reference |
| drift-vis @ real onset [tap_dir/tap_mag/error] | 1.38 / 1.30 / 1.02 | ×calib | direction rises, error **lags** |
| drift-vis @ nuisance [tap_dir/tap_mag/error] | 0.84 / 10.00 / 0.83 | ×calib | direction **invariant**, magnitude ×10 |

- **DRIFT** (headline): left — `bulk_drift` stays in [0.63, 1.00] across the whole stream (the map moves but never
  collapses); right — the drift-visibility panel: at a *real* class onset the class-direction tap signal rises 1.38×
  and the error-rate barely 1.02× (error lags real drift); at the *nuisance* onset the direction signal is flat (0.84×)
  while the magnitude-of-shift signal spikes 10× — the detection problem is well-posed and the spine is visible.
  - **INV**: all seven guards green; fire-counts sane (always f=1.00, oracle f=0.286).

**Read (8 slots).**
1. *Claim* — the apparatus is faithful (7 guards bit-exact), the bulk drifts without forgetting (bulk_drift ∈ [0.63,1.00]),
   and the detection problem is well-posed (direction moves at real onsets, magnitude fires on nuisance).
2. *Headline* — bulk_drift 0.627..1.000; direction-signal 1.38× at real onset vs 0.84× (invariant) at nuisance while the
   magnitude null spikes 10.00× (n=5, live CI+nuisance stream). Refs: always-pay AA 0.448 f=1.00; oracle AA 0.448 f=0.286.
3. *Figures* — DRIFT (bulk-drift + drift-visibility), INV (guards green + fire-counts).
4. *Mechanism* — `bulk_drift` bounded away from 0 because SCFF is unsupervised and local: it re-organizes but never
   catastrophically overwrites. The drift-visibility split is the layernorm: the nuisance `g·x+α·1` is removed to ~ε by
   the per-sample input norm, so the *class direction* in the taps is provably invariant (0.84×) while the *raw magnitude*
   of the pixel shift is enormous (10×). Error lags real drift (1.02×) because it needs accumulated mistakes to register —
   the reason a direction trigger can *lead* it (tested in P8.2).
5. *Threats* — (a) the meter is behavioral; not exercised here beyond the proxy-equivalence guard. (b) The nuisance
   injector could pass vacuously if too weak — refuted directly: the magnitude signal moves 10× at nuisance (the pixels
   genuinely shifted) *and* the direction signal barely moves (SCFF invariance is real, not a weak injector). Two
   measurements, both shown. (c) The oracle uses hidden boundaries the detectors can't see — matching it is the win.
6. *Decision* — sets the bench every downstream rung inherits: the streaming schedule, the two accuracy references
   (always-pay ceiling 0.448, oracle-cadence 0.448/f=0.286), the calibrated nuisance injector, and the class-direction
   tap signal as the candidate trigger. No knob committed yet.
7. *Economy-honesty* — no energy claim on this rung; the meter's proxy-reduction is only *guarded* here (fwd-MAC ≡
   readout_cost, exact). FAR is reported for the two references (always-pay 1.00, oracle 0.00).
8. *Live-safety / namer* — the live path is proven identical to the frozen `continual_safety_heads` (anchor guard 0.0),
   so any A6 result downstream is measured on the real co-adapting loop, not a frozen stand-in. Namer verdict deferred
   to P8.4.
