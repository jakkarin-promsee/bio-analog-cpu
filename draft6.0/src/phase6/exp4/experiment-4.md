# P6.4 — Door B: the all-noisy stream + buffer purity (the continual-noise existential)

*Inheriting from P6.0: the directional enemy + σ\* = 2.0 (Door B's corruption strength = σ\*/2 = 1.0). The author's
Phase-6 insight — the model is online and lifelong, so **every datum is a single noisy real-world sample banked to
the LUT; it never sees a clean, curated truth set.***

**Question.** Can a stable class **direction** form when **every** training sample is corrupted and no clean truth is
ever shown — and does buffer **purity** (a small-loss filter) beat naive averaging?

**Setup.** Two separable sub-questions. (a) **Noise2Noise** — train the frozen cell on a stream where every sample is
corrupted by `NoiseModel` at rms 1.0, **zero-mean** first, then **directional** (along the label-free top-PCA axis);
measure the tail-L12 linear-probe separability on **clean** test vs the **clean-data cell at matched sample budget**;
"the direction forms" iff the ratio-to-clean ≥ ~0.90. (b) **Purity** — a `PurityFilter` (small-loss, keep_frac 0.6)
on the buffer vs a naive keep-all at matched size, on the directional-noisy stream. Controls: headroom, L12, seeds
`[42,137,271,314,1729]`, EP=25.

**Run.** 5 seeds × {clean-ref, zero-mean, directional, purity-on, purity-off} cells, checkpointed. Wall ≈ 6 min.

**Result / figures.** *(headroom, n=5, median [q25–q75]; ratio = separability / clean-data cell)*

| corruption / knob | separability (ratio to clean) | reading |
| --- | --- | --- |
| clean-data cell (ref) | 0.530 [0.527–0.539] (=1.00) | the matched-budget reference |
| **zero-mean** all-noisy stream | **0.930 [0.918–0.935]** | the direction forms (N2N; small residual gap) |
| **directional** all-noisy stream | **1.001 [0.982–1.030]** | forms **fully** — a coherent training shift doesn't break the contrast |
| purity-on vs purity-off | 0.530 [0.529–0.531] vs 0.525 [0.521–0.543] | **averaging suffices** (3/5, IQR overlaps) |

- **DOOR-B** (headline): both corruptions clear the 0.90 ratio bar; the directional stream is essentially
  indistinguishable from clean; the purity filter adds nothing at this noise level.

**Read (8 slots).**
1. **Claim** — The SCFF forms a stable class **direction from a fully-corrupted stream** — zero-mean (ratio 0.93,
   N2N) *and* directional (ratio 1.00) — and **buffer purity is not needed** at this noise level (averaging suffices).
2. **Headline** — zero-mean ratio **0.930 [0.918–0.935]**, directional ratio **1.001 [0.982–1.030]** vs the
   matched-budget clean-data cell (=1.00); purity-on 0.530 ≈ purity-off 0.525 (3/5, IQR overlaps) (n=5, headroom).
3. **Figures** — DOOR-B (corruption × purity vs the clean-data cell).
4. **Mechanism** — the "all data is noise" fear does not bite for two reasons: (a) **zero-mean** corruption averages
   out over the replay/contrast (Noise2Noise — the equal-conditional-mean condition), leaving only a small
   finite-sample residual gap (0.07); (b) a **directional** stream corruption is a *coherent* shift shared across
   samples along a label-free axis — it is consistent, so it neither breaks the unsupervised in-batch contrast nor
   biases the class direction (the layernorm's per-sample centering absorbs the rest). The directional enemy is
   dangerous **at eval** (a shift off a fixed readout, P6.0) but **not in training** (a consistent shift the
   representation simply adapts around).
5. **Threats** — (a) data-volume confound → **matched effective sample budget** (same stream length × buffer size)
   vs the clean cell; (b) a binary "forms/doesn't" hiding a residual → reported as a **ratio + gap**, not a bit
   (N2N is an infinite-pair expectation → the 0.07 zero-mean residual is expected, not a failure); (c) purity "helps"
   as noise → 3/5 with overlapping IQR = within noise, reported as such.
6. **Decision** — Door B's zero-mean part is **handled for free**; its directional residual is **not** the training
   problem it was feared to be. **Buffer purity → not adopted now** (no benefit at σ\*/2); handed to Phase-9
   maintenance as an *available* knob for higher-noise regimes, not a required one.
7. **Robustness-honesty** — the enemy was the structured `NoiseModel` (not a weak i.i.d. stand-in); the metric is the
   class **direction** (separability), not a magnitude; the clean-cell reference is at **matched budget**, so the
   ratio is corruption cost, not data-volume.
8. **SCFF-trust / arc-verdict** — Door B **strengthens the YES**: the continual "never sees clean truth" concern is
   answered — the cheap brain learns a stable direction from an all-noisy lifelong stream. The Phase-6 ↔ Phase-9
   purity seam is measured (currently unneeded). **Continual-safety:** unaffected (no bulk-objective change here).

**Pre-submit checklist.**
- [x] Median [IQR] for every number (n=5); no bare means.
- [x] "Real difference" rule for purity (3/5 + IQR overlap → "within noise", reported honestly).
- [x] Matched effective sample budget vs the clean-data cell (ratio = corruption cost, not data volume).
- [x] Direction (separability) reported, not accuracy magnitude; zero-mean residual gap reported (0.07), not a binary.
- [x] DOOR-B figure by `plot_p6.fig_door_b`; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited enemy + σ\*.
- [x] `manifest.json` + `arrays.npz` written; single-threaded (phantom guard).
- [x] `RESULTS.md` row added (§D schema).
