# P6.8 — assembled-cell confirmation + the arc verdict

*The capstone. Only ONE fix was adopted (generic iid noise-augmentation σ_aug=1.0), so the "assembled cell" IS that
cell — no levers to stack. This rung runs its FULL A7 curve (P6.1 measured only at σ\*) end-to-end and resolves the
YES/Scoped-YES/NO fork, pre-registered as a conjunction over named channels at σ\*=2.0.*

**Question.** Assembled and measured independently, does the noise-hardened cell hold its class direction on the
dominant channel within the pre-registered band, keep the A6 win, and hold on natural data — and what is the verdict?

**Setup.** The adopted `NoiseAugContrast` iid-σ1.0 cell, freshly trained (5 seeds, headroom), full tap/input
directional A7 curve (all RMS, 5 device draws) + direction-invariance per depth, drawn against the **frozen P6.0
fix-free arrays** and the linear-readout control. The verdict conjunction draws on P6.6 (continual-safe) and P6.7
(natural data). *A combined regression overrides per-rung optimism* (design §3 P6.8).

**Run.** 5 seeds, checkpointed. Wall ≈ 2.2 min.

**Result / figures.** *(headroom, n=5, median [q25–q75]; @σ\*=2.0)*

| metric | fix-free | hardened (iid σ1.0) | paired Δ | reading |
| --- | --- | --- | --- | --- |
| **tap-dir retention** (dominant) | 0.817 [0.781–0.861] | **0.865 [0.851–0.915]** | **+0.054, 5/5** | real lift, **near not above** the 0.90 band |
| input-dir retention (residual) | 0.733 [0.729–0.771] | 0.696 [0.695–0.769] | −0.03 | not helped (the residual) |
| clean acc | 0.526 | **0.555 [0.555–0.560]** | +0.029 | improved |
| dir-invariance tap (per depth) | — | 0.97→0.91 | — | class direction held under depth |

- **A7-CURVE** (headline): the hardened tap-directional curve sits above the fix-free curve across the RMS grid
  (toward the noiseless ceiling), while the input curve is unchanged. - **DIR-INVARIANCE**: the hardened tap
  direction-invariance holds high across all 12 depths.

## The verdict — **Scoped-YES (fixable in SCFF, forward-only; with a named residual)**

Evaluated as the pre-registered conjunction at σ\*=2.0:

- **Dominant (tap) channel — substantially hardened, forward-only:** retention 0.817→0.865 (5/5 paired, real),
  digits 0.763→0.888, CIFAR 0.697→0.779 (P6.7) — a genuine, reproducible, natural-data-confirmed improvement. It
  lands **near** the 0.90 band (0.87–0.89 on headroom/digits, 0.78 on the hardest CIFAR), **not decisively above** it
  at every operating point — an honest **partial** fix, banked as the best forward-only lever available (P6.2/P6.3
  correctly skipped: the norm is load-bearing).
- **Continual-safe (P6.6):** PASS — the fix keeps and slightly improves the A6 win (BWT −0.022→−0.017).
- **Natural data (P6.7):** holds — A7 and the fix both reproduce on digits + CIFAR-flat.
- **The named residual (the "scoped"):** the **input-transducer directional** channel is unhelped (0.733→0.696) and
  the tap channel's high-σ tail is not fully closed → handed to **Stage-2 read-side** (calibration under shift), plus
  ADC < ~3-bit. Door B (P6.4) is separately resolved (the direction forms from an all-noisy stream).

**Not NO:** a forward-only objective change *does* reproducibly harden the dominant channel without denting depth,
selectivity, or the A6 win — the SCFF objective did not need to be reopened. **Not clean-YES:** the fix is partial at
σ\* and leaves a named residual. → **Scoped-YES:** hand the noise-hardened cell forward with an explicit Stage-2 brief.

**Read (8 slots).**
1. **Claim** — The assembled noise-hardened cell **substantially and reproducibly improves the dominant
   tap-directional channel forward-only** (0.817→0.865, 5/5), keeps the A6 win, and holds on natural data — a
   **Scoped-YES** with the input-transducer residual named for Stage 2.
2. **Headline** — tap-dir retention **0.865 [0.851–0.915]** (fix-free 0.817 [0.781–0.861], paired Δ +0.054, 5/5),
   clean acc 0.555, continual-safe (P6.6), natural-confirmed (P6.7); input-dir residual 0.696 (n=5, headroom, σ\*=2.0).
3. **Figures** — A7-CURVE (fix-free vs hardened, per channel), DIR-INVARIANCE (hardened tap held across depth).
4. **Mechanism** — the assembled measurement, at more device draws than P6.1, confirms the fix's direction and
   magnitude honestly: a real but partial lift (the P6.1 per-rung 0.946 sat at the top of its wide IQR; the combined
   run lands at 0.865, within that IQR). The generic augmentation hardens the rep-level (tap) channel it corrupts at
   train time; it cannot manufacture robustness for the input-transducer channel it doesn't touch — exactly the
   forward-only envelope's reach and limit.
5. **Threats** — (a) per-rung optimism → the **combined run overrides** (0.865, below the 0.90 the per-rung 0.946
   suggested — reported, not hidden); (b) claiming a clean band crossing → **avoided**; the honest statement is a
   partial, real, paired lift; (c) input residual → named, handed to Stage 2, not smoothed over.
6. **Decision** — **Bank the noise-hardened cell** (`NoiseAugContrast` iid σ1.0) as the Stage-1 output; write the
   Stage-2 brief (the named residuals); update the decision record (SCFF carries a noise-aware objective).
7. **Robustness-honesty** — the enemy was directional at matched projected-RMS; the read is retention (direction);
   the fix is generic (not directional-specific — stated plainly); the band crossing is partial, not overclaimed; the
   residuals are named.
8. **SCFF-trust / arc-verdict** — **Scoped-YES: the cheap brain is noise-hardened enough to trust downstream, with a
   named residual.** The SCFF objective did not need reopening (not NO); the fix is real, forward-only, continual-safe,
   and natural-data-confirmed (not a synthetic artifact). **The SCFF side's noise question is COMPLETE** — a known,
   hardened, honestly-flagged cell is handed to the GD era.

**Pre-submit checklist.**
- [x] Median [IQR] for every number (n=5); no bare means; paired Δ (5/5, IQR excludes 0) for the tap lift.
- [x] **Combined run overrides per-rung optimism** — the 0.865 (below the per-rung 0.946) reported as the honest number.
- [x] A7-CURVE draws fix-free + hardened + ceiling + linear control; directional dashed; by `plot_p6.fig_a7_curve`.
- [x] The verdict is the **pre-registered conjunction** over named channels at σ\*; Scoped-YES (not overclaimed YES).
- [x] The named residuals (input transducer, tap high-σ tail, ADC<3-bit) written into the Stage-2 brief.
- [x] All 8 slots; formal voice; opens by naming the assembled cell.
- [x] `manifest.json` + `arrays.npz` written; single-threaded (phantom guard).
- [x] `RESULTS.md` capstone row + README verdict updated; the decision-record delta flagged for banking.
