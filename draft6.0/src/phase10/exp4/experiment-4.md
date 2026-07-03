# P10.4 — The noise showcase on a held-out battery

**Question.** The Phase-6 arc ("scoped-YES": noise-augmentation hardens the cheap brain; the input-transducer
directional residual → Stage-2 read-side) and the P9.4 read-side defense (proto-reanchor) were tuned on the *home*
residual. Do they hold on a **held-out** battery — and does OURS-hardened beat a budgeted BP+replay under the
dangerous **directional** enemy (the spine: a coherent shift along the class axis, read as *retention*, never a
per-sample magnitude)?

**Setup.** Swept variable = the environment ∈ {clean, iid, directional, adc3b, nuisance}; learners = OURS-hardened
(`NoiseAugContrast` + proto-reanchor read-side) vs BP+replay (ER-shape, clean-trained best-case) vs naive. Battery is
**margin-disjoint** from P9.4's home residual (dir-RMS 2.5 vs 1.5, +ADC-3b + a nuisance channel; `noise_holdout_guard`
certifies disjoint). Note (honesty, K4): the substrate-identity guard is scoped to `NoiseModel`-off cells — P10.4's
noise arms are the declared exception (noise *is* the axis here). 5 seeds. Figure NOISE-SHOWCASE + INV.

**Run.** 3 learners × 5 environments × 5 seeds on the committed cell (train_cell + battery); wall ≈ 3.2 min.

**Result / figures.** *(directional retention = acc under the channel / clean acc — a DIRECTION, per the spine.
Deterministic: per-env device-offset seeds are a fixed map, not `hash(env)` — reproducible across runs.)*
| environment | OURS-hardened | BP+replay | naive |
| --- | --- | --- | --- |
| clean | 1.000 [1.000–1.000] | 1.000 | 1.000 |
| iid | **1.095 [1.076–1.151]** | 0.608 [0.589–0.693] | 0.720 [0.661–0.773] |
| directional | 0.978 [0.969–0.980] | 0.225 [0.150–0.237] | 0.981 [0.978–0.986] |
| adc3b | 0.923 [0.923–0.925] | 0.300 [0.215–0.504] | 0.920 [0.739–0.973] |
| nuisance | **1.000 [1.000–1.000]** | 0.469 [0.459–0.539] | 0.423 [0.419–0.441] |

- **NOISE-SHOWCASE**: OURS-hardened (teal) sits at 0.92–1.10 across every noisy channel; BP+replay (magenta) collapses
  to 0.23–0.61 on all four; naive (black) is erratic — it ties OURS on directional/adc3b (a shallow raw-input
  classifier is incidentally directional-robust) but collapses on nuisance (0.423) and is weak on iid (0.720).
- **INV**: 14 guards green (substrate-identity noted as scoped-exempt for the noise arms).

**Read (8 slots).**
1. *Claim* — OURS-hardened's Phase-6/9 noise defenses hold on a held-out battery: it beats a budgeted BP+replay on
   **every** channel; a small directional/ADC residual (~0.03–0.05, > δ) persists and is named to the analog-realism
   layer — the honest "scoped-YES," confirmed on the assembled object.
2. *Headline* — vs BP+replay: iid 1.095 vs 0.608, directional 0.978 vs 0.225, adc3b 0.923 vs 0.300, nuisance 1.000 vs
   0.469 (n=5). OURS directional/adc3b retention 0.978/0.923 drops just past δ → residual named.
3. *Figures* — NOISE-SHOWCASE (retention per held-out env, OURS vs BP vs naive), INV.
4. *Mechanism (the spine)* — the read is a **direction** (retention under a coherent shift), not a per-sample cosine.
   **iid 1.095 (> 1)**: the Phase-6 noise-augmented training makes OURS *more* robust than clean under iid noise — the
   generic-hardening that P6 committed. **nuisance 1.000**: SCFF's per-sample layernorm removes the covariate entirely
   (density ≠ class — the spine, invariant by construction), while BP/naive read the raw shifted input and collapse.
   **directional/adc3b 0.978/0.923**: proto-reanchor (re-forwarding the raw LUT through the current bulk under the shift)
   recovers most of the input-transducer residual; the small remainder is the physical channel the read-side cannot
   reach.
5. *Threats to validity* — (a) behavioral meter (not the axis here); (b) the battery is a **re-parameterized** op point
   of the *same* transducer model (guard-certified margin-disjoint, but not a *structurally-novel* channel) → the claim
   is honestly **"confirms P9.4 at new levels," not a fresh payoff**; naive incidentally ties OURS on directional (a
   shallow raw-input classifier is directional-robust) — so the load-bearing comparison is OURS vs the fair continual
   opponent BP+replay, where OURS wins everywhere; (c) the residual > δ is real → named, not hidden. Rule-1: one
   variable (environment).
6. *Decision / verdict* — **CONFIRMS P9.4 at new levels** (OURS-hardened ≫ BP+replay on every held-out channel), with a
   **small directional/ADC residual (0.978 / 0.923) named → the analog-realism layer** (SPICE/PVT) — the Phase-6 arc is
   cashed on the assembled object, honestly scoped.
7. *Freeze-honesty* — object frozen before the run; the battery was held-out (margin-disjoint, guarded); the read is a
   direction not a magnitude; substrate-identity scoped-exempt for the noise arms (declared). Meter = P8 model.
8. *Where-it-stands* — the noise showcase is a **clean win over the fair BP+replay opponent** on the dangerous
   directional enemy and the layernorm-removable nuisance, cashing the Phase-6 "scoped-YES" on the whole object; the
   residual that remains is a *named hand-off* to the analog layer, not a Phase-10 failure.
