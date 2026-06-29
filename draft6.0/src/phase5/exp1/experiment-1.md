# P5.1 — objective sharpness: temperature is the free, direction-driven depth lever

*Inheriting the trusted bench from P5.0 (decay reproduced: baseline-w2 tail 0.435, w12 objective ceiling 0.556,
tuned-BP 0.531), this rung sweeps the InfoNCE temperature — the cheapest, highest-leverage knob.*

**Question.** Is a sharper InfoNCE the free depth fix — where is the floor, does it survive the real readout, and is
it **free** (objective-sharpness = hard-negative reweighting, the spine) or a **disguised learning-rate increase**?

**Setup.** Swept variable = `temp ∈ {0.5, 0.35, 0.2, 0.1, 0.05}`; controls locked (window=2, mask=0.5, headroom +
flat + mixed, L12, W64, seeds [42,137,271,314,1729], PROBE_EP=120). The mandatory **lr-matched arm**: the mean
effective step-norm at temp0.2 vs temp0.5 was measured at identical init (ratio 2.249) → a **temp=0.5 cell run at
lr=0.0675** so its step-norm (4.9e-2) matches temp0.2's (5.3e-2) — the free-vs-lr test. The **batch-floor co-lever**:
temp0.05 (the collapsing temp) @ batch 64 vs 32, with temp0.1 as a no-collapse control. References (w12, tuned-BP)
carried from P5.0. Apparatus: `p5lib.SCFFContrastOverlap`; guards passed (equiv 0.0e0, FD 2.1e-8).

**Run.** 22 cells × 5 seeds, checkpointed; wall ≈ 35 min. No NaN.

**Result / figures.** *(headroom; median [IQR], n=5)*
| temp | tail-L12 | readout | peak | vs w12 (0.556/0.569) · BP (0.531) |
| --- | --- | --- | --- | --- |
| 0.5 (baseline) | 0.435 [0.411–0.437] | 0.449 [0.446–0.455] | L5 | the decay |
| 0.35 | 0.481 [0.461–0.498] | 0.475 [0.473–0.507] | L5 | |
| **0.2 (committed)** | **0.530 [0.527–0.539]** | **0.550 [0.545–0.553]** | L6 | tail −0.026 to w12; **readout beats BP** |
| 0.1 | 0.523 [0.519–0.526] | 0.536 [0.535–0.545] | L9 | |
| 0.05 | 0.491 [0.489–0.491] | 0.501 [0.478–0.513] | L10 | **collapse** |
| **temp0.5 @ lr-matched** | **0.452 [0.435–0.457]** | 0.445 [0.443–0.453] | L5 | the lr control — flat near baseline |

- **TEMP-FLOOR-headroom** (headline): the sweep peaks at temp0.2 (tail 0.530, readout 0.550 — above tuned-BP,
  approaching w12) while the **lr-matched line sits flat at 0.452/0.445**; collapse shaded at 0.05. - **TEMP-FLOOR-mixed**:
  the flat subtask un-corrupts **0.475→0.697** (≈ w12 0.708) at temp0.2, lr-matched only 0.516. - **DEPTH-PROFILE-temps**:
  the probe peak marches L5→L9 as temp sharpens, temp0.2 tracking the w12 ceiling. - **INV**: clean (dead-frac ≈0, guards pass).

**Read (6 + 2 slots).**

1. **Claim** — A sharper InfoNCE temperature composes depth further, and the gain **survives the lr-matched control**
   — so it is **direction** (hard-negative reweighting), not a disguised learning rate.
2. **Headline** — temp0.2: tail-L12 **0.530 [0.527–0.539]**, readout **0.550 [0.545–0.553]** vs the lr-matched temp0.5
   **0.452 [0.435–0.457]** (the free-vs-lr test, **5/5 by seed, IQR-disjoint**), the w12 ceiling 0.556/0.569, and
   tuned-BP 0.531. The lever lifts the tail 0.435→0.530 (+0.095); the lr-matched control lifts it only to 0.452
   (+0.017) — **~82% of the gain is direction.** (n=5, headroom, PROBE_EP=120.)
3. **Figures** — TEMP-FLOOR-{headroom (headline), flat, mixed}, DEPTH-PROFILE-temps-{…}, INV. All regen from `arrays.npz`.
4. **Mechanism** — Lowering temp does two things: scales the gradient ~`1/temp` (magnitude) **and** sharpens the
   softmax over negatives so the **hardest (boundary) negatives dominate** the update (direction). The lr-matched arm
   strips the first; what remains — the bulk of the win — is the second: a sharper contrast keeps each update pointed
   at the class manifold, which is exactly the spine (**direction, not magnitude**). The mixed task confirms it at the
   mechanism's sharpest point — the deep-layer **corruption of the early-solved flat subtask is undone** (0.475→0.697),
   and that too is direction (lr-matched only 0.516). The **batch-floor refines the floor's cause**: at temp0.05 more
   negatives (batch64, 63 vs 31) do **not** rescue the collapse (0.491→0.485, no effect) — so the floor is **intrinsic
   over-sharpening** (the peaky softmax concentrates on the single hardest negative regardless of count), not
   negatives-starvation. The floor is an objective floor, not a batch artifact.
5. **Threats** — (a) the lr confound → addressed by the lr-matched arm (5/5 direction, IQR-disjoint); (b) probe ≠
   readout → both reported, temp0.2 wins both (readout 0.550 > BP 0.531); (c) the residual temp0.2-vs-w12 tail gap
   (0.026) is small — *not* over-claimed as closed; it is P5.2's `temp×w4` job; (d) on **flat** the free margin is
   smaller (temp0.2 0.673 vs lr-matched 0.660, 4/5) — consistent, an easy task has less off-manifold drift to fix, so
   lr helps relatively more; the depth claim lives on **headroom**, where the win is clean 5/5; (e) **continual-safety
   NOT yet checked** — a sharper contrast is more class-selective on the *current* task, plausibly worse for forgetting
   → **P5.7 gates adoption**, with the pre-registered fallback = the mildest temp that passes P5.7 and still beats
   baseline depth (temp0.35/0.1 are the candidates).
6. **Decision** — **Committed temp = 0.2** (the sharpest non-collapsing temp: > temp0.1 5/5, > the collapsed temp0.05
   5/5, passes the lr-control 5/5, beats tuned-BP on the real readout) — **pending P5.7**. Mask held at 0.5. **P5.2
   inherits temp0.2** for the `temp×w{3,4}` combo, to close the residual ~0.026 to the w12 ceiling.
7. **Cost-honesty** — Temperature is **free**: no architecture, forward-only, per-sample, backward work unchanged vs
   baseline (window held at 2 → the substrate cost stays 1.9×, not the 11× of w12). The lr-matched arm confirms the
   gain is not a bigger step. No cost on the continual workload is claimed here (that is P5.5).
8. **SCFF-completion** — This moves the **earn-depth** verdict hard: temperature alone closes most of the gap (tail
   0.435→0.530, within 0.026 of the objective ceiling; readout 0.550, **above the deployable tuned-BP**), *for free*.
   Earn-depth is largely achieved by a knob we already own. **Remaining for SCFF-done:** the residual to w12 (P5.2),
   and — the gate — **continual-safety (P5.7)**: temp0.2 is *provisional* until it preserves the A6 win.

**Pre-submit checklist.**
- [x] Median [IQR] for every headline number (n=5); no bare means.
- [x] "Real difference" rule applied: free-vs-lr 5/5 + IQR-disjoint; collapse (t0.1>t0.05) 5/5; t0.2>t0.1 5/5.
- [x] Every depth figure draws the w12 ceiling + tuned-BP (headroom); truncation floor deferred to P5.3 (noted).
- [x] Every figure via `plot_p5.fig_*`; `plot_p5.py regen <run-dir>` redraws all 7 from saved data.
- [x] All 8 slots filled, formal voice; card opens naming the inherited knob (the P5.0 bench).
- [x] `manifest.json` + `arrays.npz` written to the §A schema; calibration ratio + lr_matched recorded.
- [x] Guards logged (FD 2.1e-8, equiv 0.0e0); the lr-confound control is the rung's central control.
- [x] Single-threaded (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`).
- [x] Spine check: the win is attributed to **direction** (hard-negative reweighting), proven against the magnitude
      (lr) and negative-count (batch) confounds; no goodness/energy invoked.
- [x] Continual-safety (P5.7): flagged as the gate on adopting temp0.2 — not yet run.
- [x] `RESULTS.md` row added (§D schema).
