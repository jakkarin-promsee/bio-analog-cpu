# Phase 6 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema, no prose. The story lives in `expK/experiment-K.md` and (at close)
> the front-door `README.md`; this is the numbers-only ledger. Numbers are `median [q25–q75]`, n=5 unless noted.
> The cell under test is the **frozen Phase-5 cell** `SCFFContrastOverlap` temp0.2 / w2, L12, no residual; the noise
> enemy is `NoiseModel` (AIHWKit-structured: uncorrelated mismatch · directional residual · common-mode · ADC).
> **Robustness = direction-invariance `cos(clean,noisy)`, never Δaccuracy** (the spine). "Real" = IQR-disjoint
> **and** ≥4/5 by seed (§B). Matched on **projected RMS** onto the class axis (the tautology-trap guard); the
> decisive A7 read is **OURS-vs-`linear_readout`**, not directional-vs-i.i.d.

---

## P6.0 — bench + honest NoiseModel + A7 reproduction + guards `exp0`
*Locked: frozen cell temp0.2/w2 · L12 · W64 · DIM40 · C4 · seeds[42,137,271,314,1729] · 5 device-draws · matched
projected-RMS · channel=tap/input/adc/weight.*

**Guards:** overlap≡OLU `0.0` · FD-InfoNCE `2.06e-08` · noise-σ0≡clean `0.0` · aug-σ0≡plain `0.0` · proj-RMS matched
`0.298/0.299` · auto-zero (cm→`4.3e-17`, dir survives) · FD-RINCE `7.4e-09` → **7/7 PASS**.

| channel · variant | ret @σ*=2.0 | ret @rms4.0 | OURS-vs-linear | dominant? | verdict |
| --- | --- | --- | --- | --- | --- |
| input · directional | 0.733 [0.729–0.771] | **0.596 [0.587–0.630]** | linear 0.958 [0.840–0.960] · **5/5 OURS<lin** | **yes** | A7 OURS-specific |
| tap · directional | 0.817 [0.781–0.861] | 0.586 [0.583–0.613] | (no linear ctrl on tap) | **yes** | OURS-specific |
| input · iid (rotational) | 0.586 [0.565–0.589] | 0.548 [0.531–0.552] | linear 0.796 | — | rotational; cos-visible |
| tap · iid | 0.522 [0.480–0.531] | 0.467 [0.424–0.511] | — | — | √d total-energy control |
| weight (mult., old-A7) | 0.965 @0.2 | 0.895 [0.871–0.895] @0.4 | — | no (milder) | A7 reproduced |
| ADC (bits 8→2) | — | acc `.525/.531/.527/.521/.480` | — | no | robust ≥3-bit |

**Spine (dir-invariance, tap, per-depth L1→L12):** directional cos `0.994→0.961` (stays high — coherent translation)
· iid cos `0.767→−0.007` (collapses — rotation). **Auto-zero [off,on] = 0.529/0.529** (layernorm rejects common-mode).
Clean acc **0.526 [0.525–0.535]** (OURS) vs linear-readout clean **0.349** (depth helps clean, costs directional robustness).
FLAT anchor: clean 0.783, tap-dir ret@4.0 0.524, weight ret@0.4 0.863 (A7 holds on the easier task too).

**Reads:** A7 **reproduces**, is **OURS-specific & directional** (5/5 OURS<linear). The enemy is a **coherent
translation along the class axis** (damages retention, not per-sample cos → retention is the direction-first read).
**σ\* = 2.0** pinned; **band (blind) = directional retention ≥ 0.90 @σ\***; fix-free input-dir retention @σ\* = **0.733**
→ gap for P6.1. **BENCH TRUSTED.** **Banked:** the bench + the frozen fix-free arrays. **Continual-safety:** n/a.

---

## P6.1 — noise-as-contrastive-augmentation: the primary fix `exp1` *(STOP ①)*
*Locked: frozen cell + one noise-augmented view · headroom · L12 · seeds[42,137,271,314,1729] · 5 draws · σ*=2.0 ·
dominant channel = tap (Rasch). Guard: aug-σ0≡plain `0.0`.*

| variant · σ_aug | tap-dir retention (dominant) | input-dir ret | clean acc | selectivity | vs-random-axis | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| fix-free (σ0) | 0.841 [0.836–0.869] | 0.812 [0.685–0.908] | 0.526 | 0.530 | — | baseline |
| **iid σ1.0** | **0.946 [0.852–0.952]** | 0.822 [0.679–0.888] | 0.555 | 0.530 | iid>randax(0.870) | **ADOPT — fixes tap** |
| iid σ2.0 | 0.920 [0.832–0.939] | 0.818 | 0.543 | 0.507 | — | knee (sel dents) |
| dir σ1.0 | 0.876 [0.873–0.890] | 0.767 | 0.558 | 0.569 | dir<iid | generic>directional |
| randax σ1.0 | 0.870 [0.846–0.911] | 0.793 | 0.535 | 0.526 | — | generic isolator |

**Paired Δ (iid σ1.0 − fixfree) tap-dir:** median **+0.031** [+0.023,+0.082], **5/5 positive** → real (paired).
Spine ordering **iid ≥ randax > dir** → the gain is **generic smoothing, NOT directional-specific** (H-aug-directional
**overturned**). IID-enemy (rotational) retention unfixed (~0.60, √d energy) but its per-sample cos rises (0.34→0.41).

**Reads:** **ADOPT iid σ_aug=1.0** — fixes the dominant tap-directional channel into band (≥0.90), clean acc ↑,
selectivity held, capacity knee at σ2.0 avoided. Input-transducer channel marginal (0.812→0.822) → **Scoped-YES
residual** to Stage-2 read-side. **STOP ① substantially met.** **Banked (pending P6.6):** the iid-aug fix. **P6.2/P6.3
→ skip-cards** (tap fixed; weight non-dominant; leave the load-bearing norm).

---
