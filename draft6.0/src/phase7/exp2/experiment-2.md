# P7.2 — multimodality / heterogeneity: the closed-form cliff

**Inheriting** the pinned all-tap tap-feature source + the frozen `NoiseAugContrast` bulk from P7.0. **Question.**
Are SCFF's per-class features ~unimodal in the **natural** frozen tap space (one prototype suffices → the clean
no-gradient story holds), or multi-modal (one mean underfits)? If multi-modal, how far up the fallback ladder
(mean → SLDA → FeCAM → GKEAL → mixture) must we climb before accuracy recovers — and does it stay **closed-form** or
force a non-convex mixture?

**Setup (one variable = per-class modeling capacity).** Decision-bearer = the **natural** tap space (digits, all-tap
on the frozen bulk); the synthetic multi-blob task (each class = ~3 separated blobs, `n_clusters=30/n_class=10`, raw
features) is **apparatus sanity only** (its outcome is fixed by construction). Ladder rungs: `mean`=NCM (one mean),
`slda`=tied covariance, `fecam`=per-class covariance, `gkeal`=Gaussian-kernel (RFF), `mixture`=k=3 sub-prototypes/class
(non-convex). Multimodality probe = per-class BIC-selected mode count (numpy k-means, no sklearn). Seeds ×5, median
[q25–q75]. Wall 65.6s.

**Result / figures.** *(n=5, median [q25–q75])*

| ladder rung | acc (natural: digits) | acc (synth-blob sanity) | closed-form? | reading |
| --- | --- | --- | --- | --- |
| mean (NCM, one prototype) | 0.754 [0.742–0.762] | 0.285 | ✓ | one mean underfits *even the unimodal digits* |
| **SLDA (tied covariance)** | **0.946 [0.946–0.951]** | 0.267 | ✓ | **+0.19 over one-mean — the covariance is the lever** |
| FeCAM (per-class covariance) | 0.921 [0.905–0.933] | 0.298 | ✓ | per-class cov *overfits* on limited data (< SLDA) |
| GKEAL (kernel) | 0.586 [0.583–0.613] | **0.857** | ✓ | rescues the *multimodal* sanity task; poor on digits |
| mixture (k=3, non-convex) | 0.824 [0.802–0.839] | 0.693 | ✗ | rescues sanity; **HURTS digits (−0.12 vs SLDA)** |

per-class **n-modes (natural digits) = 1.00** (unimodal). closed-form gain over one-mean **+0.193**; extra a
non-convex mixture buys **−0.122** (it hurts).

- **MULTIMODAL** (headline): on digits, accuracy jumps at the *tied-covariance* rung (SLDA) and does **not** rise
  further up the ladder — FeCAM (per-class) drops, GKEAL/mixture drop hard. On the synth-blob sanity, the pattern
  **inverts** (single-Gaussian heads fail ~0.30; GKEAL/mixture recover to 0.86/0.69) — the ladder apparatus works.
  - **MULTIMODAL_nmodes**: per-class mode count flat at 1.0 (digits unimodal). - **INV**: feat-pinned ✓.

**Read (8 slots).**
1. **Claim** — SCFF's per-class features are **unimodal in the natural tap space** (n-modes=1.0); the accuracy cliff is
   not multimodality but an **anisotropic metric** — a *tied covariance* (SLDA) recovers +0.19 over the Euclidean one-mean
   NCM, **closed-form, no gradient**, and *no non-convex mixture is needed* (a mixture hurts digits by 0.12).
2. **Headline** — digits SLDA **0.946 [0.946–0.951]** vs NCM one-mean 0.754 [0.742–0.762] vs mixture 0.824 [0.802–0.839]
   (n=5, natural digits tap space). The synth-blob sanity inverts (GKEAL 0.857 vs single-Gaussian ≈0.29) — the ladder
   recovers a *known*-multimodal task, so the apparatus is trusted.
3. **Figures** — MULTIMODAL (ladder, natural + sanity), MULTIMODAL_nmodes (flat at 1.0), INV. Regen from `arrays.npz`.
4. **Mechanism** — density ≠ class, once more: the per-class clouds are single blobs (unimodal), but *Euclidean* distance
   to their means is the wrong metric — the classes are anisotropic in the tap space, so a **shared whitening** (SLDA's
   tied covariance) separates them where an isotropic mean cannot. Per-class covariance (FeCAM) *overfits* the limited
   per-class sample; the kernel (GKEAL) and mixture are the *multimodal* tools and correctly fire only on the multimodal
   sanity task, not on the unimodal digits. The closed-form/analytic guarantee **survives** — the rough plan's
   "non-convex mixture or bust" was wrong.
5. **Threats** — (a) the synthetic sanity task being tautological → **it is, deliberately** (apparatus-only, does not
   decide; the *natural* space decides); (b) GKEAL's poor digits number being a tuning artifact → possible, but GKEAL is
   the *multimodal* fallback (it wins the sanity task), not a general head, so its digits number is not decision-bearing;
   (c) the n-modes probe under-counting → corroborated by the ladder shape (accuracy plateaus at tied-cov, no further
   rise → no hidden modes to exploit).
6. **Decision** — the committed modeling is a **single prototype with a tied (shared) covariance = SLDA**; per-class
   covariance, kernel, and mixture are **not** needed on natural data (a non-convex head is **not** forced → the convex
   story stands). This is the covariance escape the P7.1 headline's SLDA/analytic winners already exploit.
7. **Spine-honesty** — SLDA's win comes from a **whitening** (a magnitude tool; whitening was rejected-as-a-lever in P5),
   so this rung *sharpens*, not dodges, the spine tension: the accuracy lever on natural data **is** a magnitude
   transform. Named, not resolved silently — carried into the P7.1/P7.6 verdict. Cost not a factor here.
8. **Namer-verdict / continual-safety** — supports a **closed-form, no-gradient** committed namer (SLDA-family) — the
   covariance rung is where accuracy lives, and it stays analytic. No mixture, so the convexity claim holds. **A6 gate
   for the committed head → P7.4** (this rung is static-only).

**Pre-submit checklist.**
- [x] Median [IQR] every headline number (n=5); no bare means.
- [x] Multimodality decided on the **natural** tap space (digits); synth-blob is sanity-only (stated).
- [x] Fallback ladder run only as far as accuracy recovers; whether the escape stayed **closed-form** (yes: SLDA tied-cov) or forced a **mixture** (no — mixture hurts) is stated.
- [x] Feature source loaded from the pinned P7.0 config; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen redraws from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (pinned taps).
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded; no sklearn for compute (numpy k-means).
- [x] `RESULTS.md` row added.
