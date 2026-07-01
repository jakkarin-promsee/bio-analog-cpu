# Phase 6 — noise-robust SCFF: make the cheap brain survive its world (signpost)

You're in **Phase 6** of draft 6.0's Stage 1 — **✅ COMPLETE (ran 2026-07-01, P6.0→P6.8, all guards pass).** A
**Stage-1 extension** run *before* the GD namer (LP-FT: a frozen head can't manufacture backbone robustness).

- **Verdict: Scoped-YES** — A7 (eval-time noise) is real, **OURS-specific & directional** (0.60 vs a linear readout
  0.96, 5/5). The primary fix = **generic noise-augmentation** (corrupt one InfoNCE view with broad iid noise);
  it **substantially but partially** hardens the dominant tap channel (retention 0.817→0.865, 5/5 paired; near, not
  above, the 0.90 band), **improves** clean acc, and **passes the continual gate** (BWT −0.022→−0.017). The
  **input-transducer residual** → Stage-2 read-side. Two hypotheses **overturned/sharpened by the sims:** the fix is
  **generic, not directional-specific** (iid ≥ randax > dir); and the directional enemy is a **coherent translation**
  (per-sample cos is blind to it → **retention** is the direction-first read). Door B (all-data-is-noise) resolved:
  the direction forms from a fully-noisy stream.
- **The committed cell:** `NoiseAugContrast` = the frozen Phase-5 cell (`SCFFContrastOverlap` temp0.2/w2, L12, no
  residual) **+ one iid-noise-augmented InfoNCE view at σ_aug=1.0.** Forward-only; the P2.5 envelope held.
- **The front door (read this first):** [`README.md`](README.md). **Numbers:** [`RESULTS.md`](RESULTS.md) (P6.0–P6.8
  + scorecard). **Per-rung story:** [`expK/experiment-K.md`](exp0/experiment-0.md). **Spec:** [`design.md`](design.md);
  contract [`result-format.md`](result-format.md). **Apparatus:** `p6lib.py` (+ `plot_p6.py`).
- **Skips (pre-registered):** P6.2 (flatness — tap≫weight, tap fixed) · P6.3 (norm-root — leave the load-bearing
  norm, STOP ②). Both one-line skip-cards (`exp2`, `exp3`).
- **Owed at close:** the decision-record delta (*SCFF carries a noise-aware objective*) → `idea/main.ideas.v1.md`;
  the Stage-2 brief (named residuals: input-transducer directional, ADC<3-bit) → [`../stage2-design.md`](../stage2-design.md).
- **Read-budget:** for the verdict read `README.md`; for numbers `RESULTS.md`. Open cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 5](../phase5/README.md) · next → Stage 2.
