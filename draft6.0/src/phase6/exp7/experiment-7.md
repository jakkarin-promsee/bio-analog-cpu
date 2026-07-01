# P6.7 — natural-data confirmation: the synthetic-artifact gate

*Inheriting the adopted fix (iid-aug σ1.0) and σ\* = 2.0. If A7 vanishes on real data it was a synthetic artifact;
if the fix works on synthetic but not real, it is NOT committed.*

**Question.** Do A7 **and** the adopted fix hold on real flat data — digits (64-D) and CIFAR-flat (3072-D) — with
the directional noise injected into the real inputs/taps?

**Setup.** Fix-free vs the adopted `NoiseAugContrast` iid-σ1.0 cell, trained on each dataset; tap- and
input-directional retention at σ\*=2.0 (5 device draws). Seeds `[42,137,271]` (natural-data confirm; CIFAR-flat is
the heavy 3072-D loader). Metric: directional retention = acc(σ\*)/acc(0), the direction-first read.

**Run.** 12 cells (2 datasets × 2 variants × 3 seeds), checkpointed, single-thread. Wall ≈ 6.8 min.

**Result / figures.** *(n=3, median)*

| dataset | clean acc | fix-free tap-dir ret | hardened tap-dir ret | input-dir (ff→hard) | reading |
| --- | --- | --- | --- | --- | --- |
| **digits** (64-D) | 0.94–0.96 | 0.763 | **0.888** | 0.481 → 0.459 | A7 present; fix lifts tap toward band |
| **CIFAR-flat** (3072-D) | ~0.27 | 0.697 | **0.779** | 0.977 → 0.989 | A7 present; fix lifts tap; input robust |

- **NAT-ANCHOR** (headline): both real datasets reproduce the A7 tap-directional gap (fix-free < 0.95) and the fix
  lifts it — digits 0.763→0.888 (near band), CIFAR 0.697→0.779. Input-directional is dataset-dependent (weak on
  digits, robust on CIFAR); the fix does not create input robustness (the residual).

**Read (8 slots).**
1. **Claim** — A7 is **not a synthetic artifact**: the tap-directional gap reproduces on real digits and CIFAR-flat,
   and the adopted fix **lifts the dominant tap channel on both** (digits 0.763→0.888, CIFAR 0.697→0.779).
2. **Headline** — digits tap-dir retention 0.763→**0.888**, CIFAR 0.697→**0.779** (fix-free → hardened, n=3, σ\*=2.0);
   both fix-free values < 0.95 → A7 present on real data; the fix improves both.
3. **Figures** — NAT-ANCHOR (digits + CIFAR-flat on the headline curve).
4. **Mechanism** — the same rep-level (tap) fragility the synthetic bench exposed is present in real flat inputs, and
   the same generic rep-augmentation hardens it — the fix is a property of the *representation*, not the synthetic
   task. On CIFAR-flat clean acc is ~0.27 (the P5 "no composable depth" regime), yet the *robustness* result still
   holds — robustness and clean accuracy are separable axes.
5. **Threats** — (a) synthetic artifact → **ruled out** (A7 reproduces on both real datasets); (b) fix works on
   synthetic only → **ruled out** (fix lifts tap on both); (c) n=3 (natural confirm) → the direction is consistent
   across seeds/datasets; the input residual is reported, not hidden.
6. **Decision** — the synthetic A7 story **and its fix are real** → committable. The input-transducer residual is
   confirmed dataset-dependent (a Scoped-YES item), not a synthetic quirk.
7. **Robustness-honesty** — the enemy was directional at matched projected-RMS on *real* inputs/taps; the read is
   retention (direction); the fix's gain is genuine on natural data, and the input residual is named, not smoothed over.
8. **SCFF-trust / arc-verdict** — A7 and its fix survive natural data → the **Scoped-YES** verdict is not a synthetic
   artifact. The fix meaningfully improves the dominant channel on real flat data (near band on digits), with the
   input-transducer channel the named residual. **Continual-safety:** unaffected (this is a characterization rung).

**Pre-submit checklist.**
- [x] Median for every number (n=3, natural-data confirm — noted); direction (retention) reported.
- [x] A7 presence tested on both real datasets (fix-free < 0.95 → present); the fix's lift reported on both.
- [x] Matched projected-RMS on real inputs/taps; directional enemy (not i.i.d.).
- [x] NAT-ANCHOR figure by `plot_p6.fig_nat_anchor`; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited fix.
- [x] `manifest.json` + `arrays.npz` written; single-threaded (phantom + cp874 guards); CIFAR cache read-only.
- [x] `RESULTS.md` row added (§D schema).
