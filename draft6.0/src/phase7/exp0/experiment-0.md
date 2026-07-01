# P7.0 — the bench + guards + the convex floor + the static ceiling + the two-arm RanDumb control

**Question.** Does the apparatus reproduce a readout on the *frozen Phase-6 bulk* (`NoiseAugContrast`), do the
references behave (convex **floor** = linear-softmax; static **ceiling** = `race_bp` + MLP head), and — the
load-bearing early read — does the trained SCFF bulk **beat a random projection at naming** (random-from-taps *and*
random-from-pixels)? Is the bench trustworthy *before* any head scores a rung?

**Setup.** Device under test = the committed cell `NoiseAugContrast` = `SCFFContrastOverlap` temp0.2/w2, L12, no
residual, **+ one iid-noise-augmented InfoNCE view σ_aug=1.0** (the P6.8 head), frozen — GD reads its all-tap taps,
never writes. Feature source = **all-tap** (768-D = L12·W64), pinned to `figs_p7_0/` with per-seed fingerprints (every
later rung regenerates identical features from the same seeds+config — the no-baseline-drift rule). Controls locked:
`DIM=40, C=10, NCLUST=40, NTR=4000, NTE=1500, STATIC_EP=25`, **`PROBE_EP=120` pinned & frozen for all rungs**, seeds
`[42,137,271,314,1729]`. RanDumb control = a frozen random ReLU projection at a **fair expansion (2000-D)**, two arms:
**taps** (of the 768-D SCFF output) and **pixels** (of the raw 40-D input = true RanDumb), same downstream head.
Guards (pre-any-head): overlap≡OLU, FD-InfoNCE (carried) + head-port equivalences, cosine-softmax FD, harness≡old,
cache≡harness.

**Run.** Guards first → **all 7 pass** → 5 seeds, single-thread, no NaN. Wall ≈ 24.7 min (`race_bp` dominates).

**Result / figures.** *(synthetic CI home, n=5, median [q25–q75])*

| reference | acc | reading |
| --- | --- | --- |
| convex **floor** (linear-softmax on all-tap) | **0.608 [0.582–0.610]** | the floor every head is measured against |
| MLP head (non-convex anchor) | 0.642 [0.622–0.649] | a small GD head buys +0.034 over the floor |
| **static ceiling** `race_bp` (tuned BP on **raw** input) | **0.866 [0.861–0.887]** | tuned BP on pixels ≫ any readout on SCFF features |

| RanDumb 2-arm (same head) | OURS-bulk | rand-taps | rand-pixels | reading |
| --- | --- | --- | --- | --- |
| **linear** head | **0.608** | 0.606 | **0.461** | earns keep vs pixels; **ties** a random expansion of its own taps |
| **rls** (ridge) head | **0.579** | 0.385 | 0.314 | **earns keep on both arms** (the ridge exploits the structured taps) |
| ncm head | 0.261 | 0.299 | 0.202 | earns keep vs pixels; ties taps (and is sub-floor → greyed) |

- **RANDUMB** (headline): OURS beats **random-from-pixels** for every head (0.608 vs 0.461, 0.579 vs 0.314) — the 80%
  SCFF earns its keep vs a raw-pixel random projection. The **random-from-taps** arm ties for the *linear/ncm* heads
  and loses to OURS for the *ridge* head. - **INV**: dead-frac **0.000**, effective-rank **58.7** (the per-layer-normed
  all-tap is low-rank), FD-guard ✓, feature-source-pinned ✓. - **BAKEOFF** (partial): floor/ceiling brackets drawn.

**Read (8 slots).**
1. **Claim** — the bench reproduces a readout on the frozen bulk and its references bracket it correctly; the trained
   bulk **beats a random projection of the raw pixels at naming** for every head (5/5), so the 80% earns its keep vs
   the harsher RanDumb arm — while a random ReLU *expansion of the bulk's own taps* ties a plain linear head (the
   expected ELM effect) and loses to the ridge head.
2. **Headline** — RanDumb linear: OURS **0.608** vs random-pixels **0.461** vs random-taps 0.606; the static ceiling
   (tuned BP on raw input) is **0.866**, far above any SCFF readout — confirming (P4) the bulk is a *continual*, not a
   static-accuracy, competitor (n=5, synthetic CI home, PROBE_EP=120).
3. **Figures** — RANDUMB (both arms), INV (dead-frac 0, erank 58.7, guards green), BAKEOFF (floor/ceiling refs). All
   regen from `arrays.npz`.
4. **Mechanism** — the taps-tie for a *linear* head is not a failure: a frozen random ReLU projection of good features
   is itself a good (ELM/reservoir) feature map — it is *literally the RanPAC mechanism*, one of our own candidate
   heads — so "random-expansion-of-taps ≈ linear-on-taps" is expected, not evidence the bulk is worthless. The decisive
   skeptic is **random-from-pixels** (raw input has no SCFF structure), and OURS beats it on every head. That a *ridge*
   head separates OURS (0.579) from random-taps (0.385) shows the structured taps carry second-moment information a
   random remix destroys.
5. **Threats** — (a) a plumbing artifact masquerading as a readout → **killed** by the 7 guards (all 0.0 / <1e-8); (b)
   the taps-tie pre-excused as "composition, move on" → **NOT excused**: both readings reported (§8); (c) an un-pinned
   feature source drifting across rungs → fingerprints frozen, regenerable; (d) "real" only by IQR + ≥4/5 sign — the
   pixels-arm win is 5/5 for linear and rls.
6. **Decision** — **BENCH TRUSTED.** Pinned for all later rungs: the all-tap feature source (fingerprints in
   `figs_p7_0/`), `PROBE_EP=120`, the convex floor **0.608**, the static ceiling **0.866**, and both RanDumb numbers.
   The `stream_cache` fast path is proven ≡ `continual_safety_heads` bit-for-bit (the bake-off may share bulk training).
7. **Spine-honesty** — no head was called "the spine" here (P7.0 is the bench). Cost is not yet reported (P7.1+), and
   when it is it will be tagged **(proxy; real meter = P8)**. The RanDumb read is stated in **both** honest readings,
   not pre-excused (§8).
8. **Namer-verdict / continual-safety** — no namer committed yet; P7.0 sets the references. **The one "uh-oh" branch**
   (RanDumb) resolves as: the bulk **earns its keep vs raw pixels** (decisive), but its naming-stage value **over a
   random expansion of its own taps is head-dependent** — verified for the ridge/analytic namer, a tie for a plain
   linear head. Flagged to Stage 2, not benign. **A6 gate: not yet checked → P7.4.**

**The two RanDumb readings (design §P7.0 — reported, not pre-excused).**
- *(i) P4/P5-consistent:* the bulk's proven value is **compositional depth** (A2/A3), which a flat *static* readout
  does not exercise; a random expansion of its taps matching a linear head is the ELM/RanPAC effect, fully consistent.
- *(ii) the honest flag:* on the **flat home**, a plain linear namer gains ~nothing from the trained taps over a random
  expansion of them (0.608 vs 0.606) — its naming-stage value there is **unverified for a linear head** (though verified
  for the ridge/analytic head, 0.579 vs 0.385, and for *all* heads vs raw pixels). Handed to Stage 2 with this flag.

**Pre-submit checklist.**
- [x] Median [IQR] for every headline number (n=5); no bare means.
- [x] "Real difference" rule applied (pixels-arm OURS>rand is 5/5 for linear & rls).
- [x] Static-accuracy figures draw the convex floor + the static BP ceiling; ceiling NOT on any BWT figure (none here).
- [x] RanDumb reported in **both arms** (taps + pixels, fair 2000-D expansion); the tie **not** pre-excused — both readings stated.
- [x] Cost not claimed here; will be tagged **(proxy; real=P8)** when reported (P7.1+).
- [x] Feature source **pinned** to `figs_p7_0/` with per-seed fingerprints + `PROBE_EP=120` frozen; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen redraws from `arrays.npz`.
- [x] All 8 slots filled; formal voice; P7.0 is the bench root (no inherited knob).
- [x] `manifest.json` (git, config, seeds, fingerprints, guards, wall) + `arrays.npz` written.
- [x] Guards logged: **7/7 pass** (overlap≡OLU 0.0, FD-InfoNCE 2.1e-8, head-port miss=0, cosine-softmax FD 2.8e-9, harness≡old 0.0, cache≡harness 0.0).
- [x] Single-threaded (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`); no sklearn for compute.
- [x] `RESULTS.md` row added (§D schema).
