# P6.6 — continual-safety: the home-turf gate (the spine gate, un-skippable)

*Inheriting from P6.1: the adopted fix = `NoiseAugContrast` variant=iid, σ_aug=1.0 (substantially hardens the
dominant tap-directional channel — a partial band crossing, P6.8). This rung decides whether banking it is allowed.*

**Question.** Does the adopted noise fix **preserve the A6 sleep-recovery continual win**? A fix that dents A6 is
rejected regardless of its A7 gain.

**Setup.** The validated A6 loop (`p6lib.continual_safety`, the cell-factory harness) on the **digits home**
(64-D, `CISTREAM_TASKS` = 5 tasks of 2 classes, sleep-consolidated all-tap readout — the exact P5.7 protocol,
BWT −0.026 referent). Two changes: **fix-free** committed cell vs **iid-aug σ1.0**. Metrics: AA / BWT / forget
(GEM/CL conventions). **Power (the GATE):** **5 seeds `[42,137,271,314,1729]` — never 3**; "within noise" is NOT an
auto-pass — the **paired-by-seed sign veto** (a change negative-BWT in ≥4/5 paired seeds FAILS even if IQR overlaps).

**Run.** 10 continual runs (2 changes × 5 seeds), checkpointed, single-thread. Wall ≈ 1.5 min.

**Result / figures.** *(digits A6 home, n=5, median [q25–q75])*

| change | AA | BWT | forget | ΔBWT (paired) | verdict |
| --- | --- | --- | --- | --- | --- |
| fix-free (committed cell) | 0.937 [0.929–0.941] | −0.022 [−0.045,−0.020] | 0.024 | — | the A6 referent (≈ P5.7 −0.026) |
| **iid-aug σ1.0** | **0.944 [0.940–0.945]** | **−0.017 [−0.020,−0.017]** | 0.020 | **+0.005, neg 1/5** | **PASS** |

Per-seed ΔBWT (aug − fix-free): `[+0.048, −0.005, +0.002, +0.025, +0.005]` — **4/5 positive**. Per-seed ΔAA:
`[+0.042, +0.010, +0.004, +0.029, −0.007]` — **4/5 positive**.

- **CONT-SAFETY** (the gate): AA/BWT/forget bars, iid-aug vs fix-free — the fix meets or exceeds the fix-free A6 win
  on every metric in the median, and the paired veto is 1/5 (not ≥4/5) → not tripped.

**Read (8 slots).**
1. **Claim** — The adopted generic-noise-augmentation fix **preserves — and slightly improves — the A6 continual
   win**: BWT −0.022→−0.017 and AA 0.937→0.944, each better in 4/5 paired seeds.
2. **Headline** — iid-aug σ1.0: BWT **−0.017 [−0.020,−0.017]** vs the fix-free committed cell **−0.022 [−0.045,−0.020]**,
   paired ΔBWT +0.005 with only **1/5 negative** (the veto needs ≥4/5) → **PASS** (n=5, digits A6 home, sleep-consolidated).
3. **Figures** — CONT-SAFETY (each change vs the fix-free committed cell + the paired veto).
4. **Mechanism** — a noise-robust representation is also **drift-robust**: training the bulk to be invariant to noise
   makes its features move less across the class-incremental stream, so the sleep-consolidated readout re-fits a more
   stable target → *less* forgetting, not more. The fear that a sharper/noise-augmented cell would worsen
   class-incremental drift is **not** borne out.
5. **Threats** — (a) low-power rubber-stamp → ran the **full 5 seeds** with the **paired-sign veto** (the design's
   anti-rubber-stamp rule); (b) "within noise" masking a real dent → the sign test is 4/5 *positive* (improvement),
   the opposite of a hidden regression; (c) baseline ambiguity → one referent, the fix-free committed cell on the
   exact P5.7 digits protocol (its BWT −0.022 reproduces the banked −0.026).
6. **Decision** — **GATE PASSED → the iid-aug σ1.0 fix is BANKED.** It is the adopted noise-hardened cell for P6.8.
7. **Robustness-honesty** — the gate is the A6 win the whole architecture exists for; the fix clears it on the real
   home turf (digits), at full power, with the paired veto — not defined away by IQR overlap.
8. **SCFF-trust / arc-verdict** — the noise fix is **continual-safe by measurement**, so the YES/Scoped-YES verdict
   survives its most dangerous gate. The cheap brain can be *both* noise-hardened *and* the A6 continual learner it
   was built to be. → P6.7 (natural-data) and P6.8 (the verdict).

**Pre-submit checklist.**
- [x] Median [IQR] for every number (n=5); no bare means.
- [x] **The GATE ran 5 seeds — never 3**; the **paired-sign veto** applied (1/5 negative, not ≥4/5 → pass).
- [x] "Within noise" NOT treated as an auto-pass — the paired sign is 4/5 *positive*.
- [x] Baseline = the fix-free committed cell on the exact P5.7 digits protocol (BWT −0.022 ≈ the banked −0.026).
- [x] CONT-SAFETY figure drawn by `plot_p6.fig_cont_safety`; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited adopted fix.
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded (phantom + cp874 guards).
- [x] `RESULTS.md` row added (§D schema).
