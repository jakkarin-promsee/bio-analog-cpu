# P6.0 — the bench + the honest NoiseModel + A7 reproduction + guards

**Question.** Does the apparatus reproduce A7 on the *frozen* Phase-5 cell, with a credible analog-noise model and
the right channels, *before* any fix is tried — and how bad is it, on which channel, and is it directional? Is OURS
*specifically* directionally fragile (the A7 thesis) or is this a cost any model pays?

**Setup.** Device under test = the committed cell `SCFFContrastOverlap` temp0.2 / w2, L12, no residual (not
re-derived). `NoiseModel` = AIHWKit-structured: uncorrelated mismatch (iid) · directional residual (a **fixed
device offset** along an axis — mismatch is frozen at fabrication, identical across samples in a pass) · correlated
common-mode · ADC k-bit. **rms = projected-RMS on the class axis** (so iid and directional are matched *on the
axis*, not on total energy — the tautology-trap guard). Eval axis = the frozen **class axis** (between-class
mean-diff, held-out train split — worst-case probe, no per-sample-label leak). Controls locked: `L=12, W=64,
DIM=40, C=4, NTR=4000, NTE=1500, EP=25`, seeds `[42,137,271,314,1729]`, 5 device draws/RMS. Channels: **tap /
input** (additive, projected-RMS grid `[0,.25,.5,1,2,4]`), **weight** (multiplicative, old-A7 grid `[0,.05,.1,.2,.4]`),
**ADC** (bits `[8,6,4,3,2]`). References: the **noiseless ceiling** (acc@0) and a **linear-readout-on-raw-input
control** (OURS-vs-linear = the decisive relative read). Guards (pre-cell): overlap≡OLU, FD-InfoNCE, noise-σ0≡clean,
aug-σ0≡plain, projected-RMS-match, auto-zero, FD-RINCE.

**Run.** Guards first → **all 7 pass** → 10 cells (headroom + flat × 5 seeds), checkpointed, single-thread. Wall
≈ 5.3 min. No NaN, no resume.

**Result / figures.** *(headroom, n=5, median [q25–q75])*

| channel · enemy | retention @σ*=2.0 | retention @rms 4.0 | reading |
| --- | --- | --- | --- |
| **input · directional** | **0.733 [0.729–0.771]** | **0.596 [0.587–0.630]** | the A7 enemy |
| input · directional — **linear control** | 0.964 [0.914–0.975] | **0.958 [0.840–0.960]** | linear is directionally robust |
| tap · directional | 0.817 [0.781–0.861] | 0.586 [0.583–0.613] | OURS-specific too |
| tap · iid (rotational) | 0.522 [0.480–0.531] | 0.467 [0.424–0.511] | more absolute drop (√d total energy) |
| weight (old-A7 mult.) | 0.965 @0.2 | 0.895 [0.871–0.895] @0.4 | reproduces A7, milder |
| ADC acc @ bits 8→2 | — | `0.525·0.531·0.527·0.521·0.480` | robust ≥3-bit; breaks at 2-bit |

| spine metric (per depth, tap) | L1 → L12 | reading |
| --- | --- | --- |
| dir-invariance **directional** | 0.994 → 0.961 (stays high) | a coherent shift barely rotates a rep |
| dir-invariance **iid** | 0.767 → −0.007 (collapses) | iid noise rotates the rep with depth |

- **A7-CURVE-acc / dir** (headline): OURS directional slides to ~0.60 retention while the linear control holds ~0.96
  — OURS is *specifically* directionally fragile. - **DIR-INVARIANCE**: directional cos stays ≈0.97 (the enemy is a
  translation, not a rotation) while iid cos collapses. - **INV**: dead-frac ≈0, **auto-zero [off,on] = 0.529/0.529
  identical** (the layernorm already rejects common-mode), projected-RMS matched (0.298/0.299), FD 2.1e-8, RINCE ✓.

**Read (8 slots).**
1. **Claim** — On the frozen cell, A7 reproduces and is **OURS-specific**: at matched projected-RMS, a directional
   input/tap perturbation degrades OURS's class readout **~2× more than a plain linear readout** (5/5 seeds), while
   the substrate's common-mode channel is already rejected by the per-sample layernorm.
2. **Headline** — input-directional retention **0.596 [0.587–0.630]** @rms 4.0 vs the **linear-readout control
   0.958 [0.840–0.960]** and the noiseless ceiling 1.00 — **5/5 seeds** OURS < linear (real: IQR-disjoint + paired-sign)
   (n=5, headroom, matched projected-RMS).
3. **Figures** — A7-CURVE-{acc,dir}, DIR-INVARIANCE, INV. All regen from `arrays.npz`.
4. **Mechanism** — the A7 tradeoff made precise: the **per-sample layernorm** that won P5 depth/nuisance-robustness
   *amplifies* a directional input/tap shift into a class-direction distortion the fixed readout can't undo; a plain
   linear map has no such amplification (directionally robust, but its clean acc is only 0.349 vs OURS 0.526 — it
   cannot reach OURS's depth). The two enemies attack **different geometry**: iid noise **rotates** each rep
   (per-sample cos collapses with depth) — a *magnitude* perturbation; directional noise is a **coherent translation
   along the class axis** — it barely rotates any single rep (cos ≈0.97) yet moves the whole cloud off the readout,
   so its damage is *irreducibly a retention phenomenon*. **This sharpens the spine:** per-sample `cos(clean,noisy)`
   catches only the rotational enemy; for the coherent directional enemy the direction-preservation read *is*
   retention-under-directional-noise (made direction-specific by OURS-vs-linear and dir-vs-iid).
5. **Threats** — (a) a plumbing artifact masquerading as A7 → **killed** by noise-σ0≡clean (0.0) + FD guards; (b) the
   tautology trap (matched-*total*-RMS rigs directional-worse) → **matched projected-RMS**, and the decisive read is
   OURS-vs-linear, not dir-vs-iid; (c) common-mode defined away → the **two-arm auto-zero** shows off=on (the norm
   rejects it — measured, not assumed); (d) axis label-leak → eval axis fit on a held-out split, never the per-sample
   label; (e) "real" only if IQR-disjoint + ≥4/5 sign — OURS-vs-linear is 5/5.
6. **Decision** — **BENCH TRUSTED.** Dominant directional channels = **input & tap** (weight milder 0.89; ADC fine
   ≥3-bit; common-mode auto-rejected). **σ\* = 2.0** pinned (where fix-free tap-directional retention first drops to
   0.90). **Pre-registered tolerable band (blind, NOW):** directional retention **≥ 0.90 at σ\*** (the direction-first
   criterion — retention is the true directional read; per-sample cos is blind to a coherent shift), with the
   iid-channel per-sample cos ≥ 0.90 as the rotational-enemy corroborator. Fix-free input-directional retention @σ\*
   = **0.733** → a real gap for P6.1 to close. The **canonical fix-free A7/dir arrays are frozen** to `figs_p6_0/`;
   later rungs LOAD, never recompute.
7. **Robustness-honesty** — the enemy was **structured & directional at matched projected-RMS** (a fixed device
   offset along the class axis), not a weak i.i.d. stand-in; the headline read is **relative fragility (OURS-vs-linear)**;
   the common-mode was measured (auto-zero two-arm), not assumed away; the layernorm's own common-mode rejection is a
   reported finding, not a modelling convenience.
8. **SCFF-trust / arc-verdict** — the cheap brain **is** noise-sensitive, specifically and directionally, confirming
   A7 is a real Stage-1 problem (not fixable downstream). Whether it is *fixable in SCFF* is the open question P6.1
   answers. **Continual-safety (P6.6):** untouched (no change banked). Verdict leaning: **undecided** — a real,
   OURS-specific, directional gap exists; the fork turns on whether a forward-only objective fix closes it.

**Pre-submit checklist.**
- [x] Median [IQR] for every headline number (n=5); no bare means.
- [x] "Real difference" rule applied (IQR-disjoint **and** 5/5 sign) for OURS-vs-linear directional fragility.
- [x] **Matched projected RMS** stated; the decisive read is **OURS-vs-linear**, not directional-vs-iid.
- [x] A7 figures draw the noiseless ceiling, fix-free, and the **linear-readout control**; directional drawn dashed.
- [x] Fix-free A7/dir arrays **frozen** to `figs_p6_0/` for later rungs to load.
- [x] **Tolerable band pre-registered blind** = directional retention ≥ 0.90 at σ\*=2.0 (retention is the direction-first read; cos is blind to a coherent shift — documented).
- [x] **Auto-zero two-arm** (off/on = 0.529/0.529) reported — common-mode is measured (norm-rejected), not assumed.
- [x] **Direction reported alongside accuracy**; where they disagree (directional: cos high, acc low), the coherent-shift mechanism is named and retention is trusted.
- [x] Every figure by a `plot_p6.fig_*` function; `plot_p6.py regen` redraws from saved data.
- [x] All 8 slots filled; formal voice; P6.0 is the bench root (no inherited knob).
- [x] `manifest.json` + `arrays.npz` written to the §A schema.
- [x] Guards logged: 7/7 pass (σ0≡clean 0.0, FD 2.1e-8, proj-RMS matched, auto-zero, FD-RINCE, overlap≡OLU).
- [x] Single-threaded (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — phantom + cp874 guards.
- [x] `RESULTS.md` row added (§D schema).
