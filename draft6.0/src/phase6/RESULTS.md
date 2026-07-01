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

## P6.2 / P6.3 — flatness / norm-root — **SKIP-CARDS** `exp2` `exp3`
*Pre-registered conditional rungs; neither antecedent met.* **P6.2:** tap ≫ weight (P6.0: weight ret 0.895 mildest)
**and** P6.1 closed the tap gap → flatness would harden a non-dominant channel → **SKIP.** **P6.3:** the dominant gap
was closed *around* the norm (P6.1); the only residual is the non-dominant input channel (Stage-2 read-side); the
per-sample norm is load-bearing for 4 P5/P4 properties → **leave the norm, harden around it (STOP ②)** → **SKIP.**

---

## P6.6 — continual-safety: the home-turf gate `exp6` *(the spine gate)*
*Locked: digits A6 home · CISTREAM 5×2 · sleep-consolidated all-tap · seeds[42,137,271,314,1729] (full 5, NEVER 3) ·
paired-sign veto.*

| change | AA | BWT | forget | ΔBWT paired (neg/5) | verdict |
| --- | --- | --- | --- | --- | --- |
| fix-free committed cell | 0.937 [0.929–0.941] | −0.022 [−0.045,−0.020] | 0.024 | — (referent ≈ P5.7 −0.026) | A6 win |
| **iid-aug σ1.0** | **0.944 [0.940–0.945]** | **−0.017 [−0.020,−0.017]** | 0.020 | **+0.005 (1/5 neg)** | **PASS — banked** |

Per-seed ΔBWT `[+0.048,−0.005,+0.002,+0.025,+0.005]` (4/5 positive); ΔAA 4/5 positive. **The fix preserves — and
slightly improves — the A6 win** (a noise-robust rep is also drift-robust). Paired veto not tripped (1/5, need ≥4/5).

**Reads:** **GATE PASSED → the iid-aug σ1.0 fix is BANKED** as the noise-hardened cell. The verdict survives its most
dangerous gate. → P6.7 (natural), P6.8 (verdict).

---

## P6.4 — Door B: all-noisy stream + buffer purity `exp4`
*Locked: frozen cell trained on an all-corrupted stream (rms 1.0 = σ*/2) · headroom · matched sample budget · n=5.*

| corruption / knob | separability (ratio to clean-data cell) | verdict |
| --- | --- | --- |
| zero-mean stream | 0.930 [0.918–0.935] | direction forms (N2N; 0.07 residual gap) |
| directional stream | 1.001 [0.982–1.030] | forms fully (coherent shift ≠ training problem) |
| purity-on vs off | 0.530 [0.529–0.531] vs 0.525 [0.521–0.543] (3/5) | averaging suffices (within noise) |

**Reads:** the class direction **forms from an all-noisy stream** (both corruptions clear the 0.90 bar); the "all data
is noise" continual fear is answered. **Buffer purity not adopted** (no benefit at this noise level) → an *available*
Phase-9 knob, not required. Strengthens the YES.

---

## P6.7 — natural-data confirmation `exp7`
*Locked: fix-free vs iid-aug σ1.0 · digits 64-D + CIFAR-flat 3072-D · σ*=2.0 · directional · seeds[42,137,271].*

| dataset | clean acc | fix-free tap-dir ret | hardened tap-dir ret | A7 present? | fix holds? |
| --- | --- | --- | --- | --- | --- |
| digits | 0.94–0.96 | 0.763 | **0.888** | YES (<0.95) | YES |
| CIFAR-flat | ~0.27 | 0.697 | **0.779** | YES (<0.95) | YES |

**Reads:** A7 is **not a synthetic artifact** — reproduces on both real datasets, and the fix lifts the dominant tap
channel on both. Input-directional dataset-dependent (weak digits, robust CIFAR); the fix does not create input
robustness (the residual). Synthetic story + fix **committable**.

---

## P6.8 — assembled-cell confirmation + the arc verdict `exp8`
*Locked: adopted iid-aug σ1.0, full A7 curve vs the frozen P6.0 fix-free arrays · headroom · n=5 · σ*=2.0.*

| metric | fix-free | hardened (iid σ1.0) | paired Δ (pos/5) | verdict |
| --- | --- | --- | --- | --- |
| **tap-dir retention** (dominant) | 0.817 [0.781–0.861] | **0.865 [0.851–0.915]** | +0.054 (5/5) | real lift, **near not above** 0.90 band |
| input-dir retention (residual) | 0.733 [0.729–0.771] | 0.696 [0.695–0.769] | −0.03 | not helped (Stage-2) |
| clean acc | 0.526 | 0.555 [0.555–0.560] | +0.029 | improved |

**VERDICT — Scoped-YES (fixable in SCFF, forward-only; with a named residual):** the dominant tap channel is
substantially and reproducibly hardened forward-only (0.817→0.865, 5/5; digits 0.888; CIFAR 0.779) — **near, not
decisively above, the 0.90 band** (an honest *partial* fix) — **continual-safe** (P6.6) and **natural-confirmed**
(P6.7). **Not NO** (the objective did not need reopening); **not clean-YES** (partial + a residual). The **input-
transducer directional** channel + the tap high-σ tail + ADC<3-bit → **Stage-2 read-side brief.** **The SCFF side's
noise question is COMPLETE.**

---

## Phase-6 scorecard

| axis | result |
| --- | --- |
| A7 reproduced, OURS-specific & directional | ✅ (0.60 vs linear 0.96, 5/5; on synthetic + digits + CIFAR) |
| primary fix = forward-only noise-augmentation | ✅ generic iid (directional-specific **overturned**) |
| dominant tap channel hardened | ⚠️ partial — real +0.05–0.13 lift, near the 0.90 band |
| input-transducer channel | ❌ residual → Stage-2 read-side |
| continual A6 win preserved (the gate) | ✅ PASS (BWT −0.022→−0.017, slightly better) |
| Door B (all-noisy stream) | ✅ direction forms (zero-mean 0.93, directional 1.00) |
| natural-data (not a synthetic artifact) | ✅ digits + CIFAR-flat |
| **arc verdict** | **Scoped-YES** — hardened cell + a named Stage-2 residual |
