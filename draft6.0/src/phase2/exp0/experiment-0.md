# Experiment P2.0 — re-establish the wall + the decisive test (lost vs entangled)

> **Status: ✅ RUN COMPLETE (2026-06-21) — verdict LOST → route P2.1.** The locked first run of Phase 2 and the
> fork that **routes the whole phase**, now resolved on CIFAR-10-flat (the wall reproduced cleanly; deep SCFF
> features fall *below* a random projection). Convention: question → setup → run → result → read → decision. Spec:
> [`../design.md`](../design.md) §P2.0. Reporting: [`../result-format.md`](../result-format.md). The two
> papers it leans on: [`../../../research/papers/phase1-2/scff.md`](../../../research/papers/phase1-2/scff.md) (our base rule) and the new
> [`../../../research/papers/phase1-2/deeperforward.md`](../../../research/papers/phase1-2/deeperforward.md) (the counter-finding that reshaped P2.1).

## Question

1. **Reproduce the wall.** Plain deep SCFF (layer-norm, sum-squared goodness) — does per-layer separability
   **decline** with depth on a task that *has* depth headroom? This is the curve every Phase-2 lever must bend
   up; it must exist cleanly before anything downstream is interpretable.
2. **Lost or entangled? (DECIDE — the fork).** Is the class information **destroyed** by the deep stack, or
   merely **entangled** (present but not linearly readable)? A max-power readout on frozen deep-SCFF features
   vs pure-GD decides it: `< GD by > 0.05` → **lost** (the fix must *preserve* information); `≈ GD` →
   **entangled** (the fix is an *interface* problem). **This routes P2.1–P2.4.**
3. **How big is the gap?** Narrow-deep (substrate regime) vs wide-shallow (paper regime) at equal weight
   budget — the single number Phase 2 must close (F6⁺).
4. **Why is it lost (if lost)? — the enrichment (decided 2026-06-21).** Within "lost," separate the two
   candidate causes: **norm-cause** (re-normalization collapses rank — the Trifecta story) vs
   **goodness-cause** (squared goodness deactivates neurons, deep layers stop learning — the DeeperForward
   story). This pre-routes P2.1's bench (norm swap vs goodness swap).

If (1) shows no wall on every task tried, **stop** — the headroom precondition failed and the phase is
unfalsifiable as framed (revisit the task before P2.1).

## Setup (LOCKED — methodology rule #3)

**The wall config = the Phase-1 locked SCFF, scanned over depth.** One axis at a time: depth for the curve, a
separate equal-budget (width × depth) pair for the gap. Pick, lock, run, let the figure talk.

| Knob | Value | Why this value |
| --- | --- | --- |
| **Headroom task (primary)** | **CIFAR-10 as flat-MLP** (3072-D, 10 classes), no conv front-end | The Trifecta's & DeeperForward's own depth-needing task; LN-decline is *documented* there → guaranteed envelope gap. A *probe*, not a benchmark claim (README §2 carve-out). Phase 1 proved low-D **cannot** show the wall (random projection ties SCFF in 2–3D) — so the headline task must be high-D. |
| **Dial task (companion)** | **Synthetic high-D Tier-B** compositional clusters (`make_tierb`): K Gaussian clusters in d-D, label = **fixed random binary label per cluster** (compositional but *linearly readable once clusters separate*); dials = {K, overlap, **input dim d**}. ⚠ **Not raw parity** — the smoke run proved parity has no linear-probe headroom (XOR pathology); see ## Run. | Gives the *tunable difficulty axis* CIFAR can't — for the F6⁺ surface and a fast, cheap sanity. d set high enough that SCFF > random (Phase-1 lesson). |
| **SCFF stack** | `L = 1…8` layers, **width 64**, ReLU, mono-forward dual-rail | depth is the axis; width fixed for the curve |
| **Normalization** | **layer-norm** (length-norm `ĥ=h/‖h‖`) — the Phase-1 baseline, the line to beat | this *is* the wall; P2.1 swaps it |
| **Goodness** | **sum-squared** `G=Σh²`, two-sided **θ=2.0** | Phase-1 locked; the suspected goodness-cause of the wall |
| **Input norm** | on (`normalize_input=True`) | Phase-1 ratified |
| **Tap** | **all-layer** | Phase-1 corrected (S3 "last-n" reads the *worst* layers) |
| **Probe (PRIMARY)** | logistic, fixed L2 **C=1.0**, frozen **2k/2k** split, to convergence — **per layer** | the pinned ground-truth metric (`result-format.md` Layer B) |
| **DECIDE readout** | **deep MLP** (max-power: 256→128 hidden, Adam, to convergence) on **frozen all-tap SCFF features** vs **pure-GD** (matched depth, end-to-end) — **+ selectivity controls** (the same MLP on a frozen *random-projection* of identical shape, and on *raw input*) | the lost/entangled test, made probe-robust. Give the readout every chance so a remaining gap is *information*, not classifier weakness — but report **selectivity = MLP-on-SCFF − MLP-on-random** (Hewitt & Liang 2019: a powerful *nonlinear* probe has low selectivity, so a bare frozen-feature accuracy can be the *probe* solving the task; the random floor + the raw-input control keep the entangled verdict honest) |
| **Width×depth (F6⁺)** | wide-shallow (`≈2000×2`) vs narrow-deep (`≈64×6`) at **equal weight budget** (via `match_width`) | the substrate-collision number |
| **Seeds** | `[42, 137, 271, 314, 1729]`, median + IQR | methodology rule #2 |
| **Realism** | ideal floats; **no** analog/PVT, no online-stream constraint yet (P2.0 is a static diagnostic) | substrate-feasibility is *tested* in P2.1+/P2.6, not here |

**Must emit** (`result-format.md` map): **F3⁺** (the wall — per-layer probe vs layer index, +GD-hidden &
LN-baseline envelopes, **caption states the envelope gap**), **DECIDE** (lost/entangled bar + per-depth),
**F6⁺** (width×depth gap), **INV** (+ **dead-unit-fraction vs depth** and **effective-rank vs depth** — the
DeeperForward deactivation/collapse diagnostics, first-class here because they are the *causal* read for Q4).

## Run

Foundation built 2026-06-21: the pluggable-norm/goodness SCFF [`../p2lib.py`](../p2lib.py) (refactored from
`../../phase1/exp0/scff_gate.py`; reproduces the wall config exactly where modes coincide) + `make_tierb` (the
high-D dial task). Full `run_exp0.py` (depth scan + GD ceiling + DECIDE + width×depth) and `plot.py`
pending. A **smoke pass** ([`smoke_exp0.py`](smoke_exp0.py), L=8, 2 seeds, 25k stream) ran first to de-risk the
task and the code.

**Smoke findings (pre-run; two of them changed the plan — methodology rule #5, failures are data):**

1. **The deactivation mechanism reproduces cleanly and robustly.** Under the wall (lengthnorm + squared
   goodness) the **dead-unit fraction climbs `0 → 0.39` over 8 layers**; under the DeeperForward cell
   (layernorm + linear goodness) it stays **`~0.05`**. That is DeeperForward's causal story — *squared goodness
   deactivates deep units; linear goodness keeps them alive* — confirmed on our substrate, exactly as
   predicted. The depth-slope also moves the right way (wall `−0.0006/layer`, DeepF `+0.0006/layer`).
2. **The synthetic Tier-B *parity* label has no linear-probe headroom** — both cells sit at chance
   (`~0.51–0.55`) whether the label is 3-way parity (27 clusters) or 2-way (16). **Parity is the XOR
   pathology**: a *linear* probe cannot read it even off well-separated cluster features, and rotated 20-D sits
   near SCFF's weak-learner failure mode (the Phase-1 "SCFF clusters by density; the label must be
   density/linearly-aligned" lesson, re-confirmed). **Consequence:** the synthetic dial task must use a
   **linearly-readable-from-cluster-identity** label (e.g. a fixed *random binary label per cluster* — still
   compositional, not a simple input-space boundary, but readable once clusters separate), **not** raw parity;
   and the headline wall figure leans on **CIFAR-10-flat** (the *documented* wall, with a measured GD-hidden
   envelope) while the synthetic task carries the tunable F6⁺ surface. Locked into the setup table above as a
   correction.

_Next: `run_exp0.py` — adds the pure-GD ceiling + DECIDE readout + the width×depth grid, on CIFAR-10-flat
(headline) and the corrected synthetic dial task, 5 seeds + IQR, manifest + arrays + `plot.py`._

## Result / figures

**Run 2026-06-21**, 5 seeds `[42,137,271,314,1729]`, median + IQR. Two tasks: **synth** (the high-D dial /
code sanity) and **CIFAR-10-flat** (the headline wall). Figures per `result-format.md` in
[`figs_exp0_synth/`](figs_exp0_synth) and [`figs_exp0_cifar/`](figs_exp0_cifar) (F3⁺ · DECIDE · F6⁺ · REPR/INV);
`manifest.json` + `arrays.npz` saved; regenerate with `python plot.py figs_exp0_<task>` (no retrain).

| scalar (n=5 median [IQR]) | synth (dial) | **CIFAR-flat (headline)** |
| --- | --- | --- |
| wall depth-slope /layer | **−0.0005** (FLAT) | **−0.018 [−0.019,−0.015]** (DECLINES) |
| wall probe L1 → L8 | 0.69 → 0.70 | 0.23 → **0.117 [0.10,0.13]** (→ chance 0.10) |
| GD-hidden envelope · gap-vs-wall | 0.95 · **+0.234** | 0.35 · **+0.187** |
| dead-units L1 → L8 | 0.00 → 0.09 | 0.02 → **0.47** |
| effective rank L1 → L8 | 44 → 7.6 | 39 → **11** |
| DECIDE: SCFF / RAND / RAW / GD | 0.918 / 0.912 / 0.961 / 0.955 | **0.294 / 0.298 / 0.389 / 0.354** |
| DECIDE gap-vs-ceiling | +0.036 | **+0.067 [+0.058,+0.067]** |
| **DECIDE selectivity (SCFF−RAND)** | +0.006 (≈0) | **−0.005 [−0.008,−0.005]** (negative) |
| **verdict** | inconclusive (probe-driven: RAW≈GD) | **LOST** |
| width×depth gap (ws−nd) | +0.000 | +0.003 [+0.003,+0.007] |

## Read (eight-slot)

**Pass gate (README §P2.0) — all three met, on the headline (CIFAR):** wall reproduced (slope **−0.018**, all 5
seeds negative; GD-hidden envelope **+0.187** above) ✓ · DECIDE unambiguous (**LOST**) ✓ · width×depth a single
number (**+0.003**) ✓. *Synth failed the headroom precondition (no wall, slope ≈ 0) — it is the dial / code
sanity, not the headline; the verdict rests on CIFAR.*

1. **Claim.** On a task with real depth headroom (CIFAR-10-flat) the deep SCFF wall (length-norm + squared
   goodness) **destroys class information with depth**: per-layer separability declines monotonically to chance,
   and a max-power readout recovers *no more* from the frozen deep features than from an **untrained random
   projection** of the same shape. The information is **LOST**, not merely entangled.
2. **Number + IQR.** Wall slope **−0.018/layer** [−0.019,−0.015]; probe 0.23 → **0.117** [0.10,0.13] (chance
   0.10). DECIDE: SCFF **0.294** [0.291,0.296] ≈ RAND **0.298** [0.296,0.303] → **selectivity −0.005**
   [−0.008,−0.005] (negative, tight); RAW **0.389** → the stack lost **0.104** of readout-recoverable accuracy
   vs raw. gap-vs-ceiling **+0.067** [+0.058,+0.067]. n=5.
3. **Figures.** [F3⁺](figs_exp0_cifar/F3plus_wall.png) (declining wall + GD envelope) ·
   [DECIDE](figs_exp0_cifar/DECIDE.png) (SCFF≈RAND<RAW — the 4-bar selectivity read) ·
   [REPR/INV](figs_exp0_cifar/REPR_INV.png) (dead-units 0.02→0.47, erank 39→11) ·
   [F6⁺](figs_exp0_cifar/F6plus_widthdepth.png) (width×depth +0.003).
4. **Mechanism.** The DeeperForward + Trifecta failure, confirmed on our substrate: **squared goodness
   deactivates units** (dead 0.02→0.47 — the `h`-factor freezes quiet units) and **length-norm forces each
   layer to re-separate from scratch**, so the representation **collapses in rank** (39→11) and sheds class
   directions until deep features sit *below a random net*. Pixel-density clustering ≠ class (the Phase-1
   lesson) makes even L1 thin (0.23), so the stack degrades an already-weak signal to chance.
5. **Threats.** (a) **Absolute accuracies are low** — flat-MLP on raw CIFAR is weak (no conv) and SCFF clusters
   by pixel-density≠class, so the wall is a decline within a thin regime; the *shape* (monotonic decline,
   dead-units↑, rank-collapse, selectivity<0) is load-bearing, not the magnitudes. (b) The matched-budget
   pure-GD "ceiling" (0.354) is **below** the max-power readout on raw (0.389) — a from-scratch reference, not a
   tuned max; but the verdict rests on **selectivity (SCFF−RAND), which is ceiling-independent**, so this does
   not move it. (c) Per-seed the naive lost/entangled *label* straddles 0.05 (4 lost, 1 entangled at n=2-style
   borderline), but **selectivity is ≤ 0 in all 5 seeds** — the robust read, and exactly why the control was
   added (§ design note below).
6. **Decision.** **LOST → route P2.1 (the norm × goodness grid)**; the fix must *preserve/rebuild* information,
   not re-interface. P2.4 (interface) is **deprioritized for the wall config** — there is no entangled signal
   for a cleverer readout to recover. Cause (Q4) points at **both** axes → start P2.1 at the substrate-native
   **layer-norm + linear-goodness** corner (DeeperForward), batch-norm (Trifecta) as the alternative. *(Full in
   ## Decision.)*
7. **Substrate-feasibility.** *n/a — P2.0 is a static, ideal-float diagnostic of the wall; online/single-sample
   feasibility enters at P2.1 (per-sample layer-norm is already substrate-native) and at P2.6.*
8. **Continual-preservation (the veto).** *n/a — P2.0 does not touch the continual regime; the ACC + BWT veto
   enters at P2.6, where each surviving lever is re-run through exp4.*

## Decision

**LOST — the fork is resolved.** On the headline task (CIFAR-flat) the deep SCFF wall destroys class
information: selectivity **−0.005** (SCFF features no better than an untrained random projection), and the
max-power readout loses **0.104** off frozen deep-SCFF vs raw. The naive entangled reading is rejected by the
selectivity control.

- **Route → P2.1 (the norm × goodness grid).** The fix must *preserve / rebuild* the representation. **P2.4
  (interface) is deprioritized** for the wall config — there is no entangled signal for a cleverer readout to
  recover.
- **Cause (Q4) = both axes.** Dead-units 0.02→0.47 (squared-goodness deactivation — **DeeperForward**) **and**
  rank-collapse 39→11 (length-norm re-separation — **Trifecta**). → start P2.1 at the substrate-native
  **layer-norm + linear-goodness** corner; **batch-norm** as the alternative. *(Synth's faint hint that
  layernorm+linear ≈ wall is meaningless there — no wall to bend; CIFAR is where the grid gets tested.)*
- **References set for later rungs.** The CIFAR wall curve (**slope −0.018, envelope gap +0.187**) and the
  **width×depth gap +0.003** are the baselines every P2.1+ F3⁺ overlays. Synth stays the F6⁺ dial / code sanity
  (no wall; its DECIDE is probe-driven, RAW≈GD).
- **Methodology win — keep the selectivity control permanently.** The naive gap-vs-ceiling straddled the 0.05
  line (would have read "entangled → interface"); the **random-projection floor** showed SCFF ≈ RAND → **LOST**.
  Without it, P2.0 would have mis-routed the entire phase. (Added 2026-06-21; see design note below.)

---

## Design decision recorded 2026-06-21 — P2.1 widens to a goodness × norm grid (why P2.0 logs the cause)

The literature pass before P2.0 surfaced a **counter-finding to P2.1's premise**, and it changes what P2.0
must measure. P2.1 as written treats **online batch-norm as the hero** (Trifecta: *layer-norm is the
depth-killer; swap to batch-norm*). But **DeeperForward (ICLR 2025)** — reaching **17-layer** FF — argues the
opposite and backs it empirically (CwComp/batch-norm route **declines** 4→14 layers on CIFAR-10, 78.1→75.3%,
while their route **rises** 79.5→86.2%):

> Batch-norm **leaks goodness into the next layer → overfitting in deep nets.** The real depth-killers are
> **squared goodness** (`Σh²` is outlier-dominated → **deactivates neurons** → dead units stop learning →
> feature loss compounds with depth) plus redundant normalization. Their fix **keeps layer-norm** but switches
> goodness **squared → linear/mean** (`Σh`): because layer-norm is already mean-zero, *goodness = the mean* is
> **automatically decoupled** from the forward representation — **no batch statistics needed.**

**Why this matters for *our* substrate, not just as trivia:** layer-norm is **per-sample** — it needs no batch
at all, so it is the *most* substrate-native normalization. The DeeperForward route therefore **sidesteps both
of P2.1/P2.6's worries about online-BN at once**: the running-stats *lag* (does the online version forfeit the
gain?) and **BN-stat rot under task shift** (the continual veto — *Continual Normalization*, ICLR 2022). A
depth-fix that is intrinsically single-sample and continual-safe is exactly what the chip wants.

**The decision (my position, committed):**

1. **P2.1 is no longer a pure normalization sweep — it becomes a `{squared, linear} goodness × {layer-norm,
   batch-norm, online-BN}` grid** (+ no-norm cheat control). Rationale: DeeperForward shows the two axes are
   **coupled** (linear goodness only decouples *because* layer-norm is mean-zero), so varying norm alone bakes
   in the Trifecta framing and would miss the most substrate-friendly cell (**layer-norm + linear goodness**).
2. **P2.0 (this card) stays the wall + DECIDE — but adds the *cause* diagnostics** (dead-unit-fraction and
   effective-rank vs depth) so the lost/entangled verdict comes pre-split into norm-cause vs goodness-cause.
   That tells P2.1 which corner of the grid to trust *before* it runs all of it.
3. **DeeperForward is written up** as [`../../../research/papers/phase1-2/deeperforward.md`](../../../research/papers/phase1-2/deeperforward.md) (now the
   second-most-relevant paper to this phase, after the Trifecta) so the reasoning lives where the next agent
   looks.

Note on the SymBa loss for P2.2 (sign paranoia, this project's recurring killer): the correct form is
`L = log(1 + exp(−(g_pos − g_neg))) = softplus(g_neg − g_pos)` — decreasing as `g_pos − g_neg` grows. Pin it
before coding; a sign-flipped copy maximizes separation the wrong way. **Confirmed live 2026-06-21:** a paper
summary of the Trifecta rendered SymBa as `log(1 + exp(g_pos − g_neg))` (sign-flipped) — exactly the trap.
When P2.2 lands, pin the sign from the **SymBa original**, not any summary.

---

## Design decision recorded 2026-06-21 (pm) — the literature pass + DECIDE gets selectivity controls

A focused lit pass before launching the full P2.0 run (the Trifecta [2311.18130], DeeperForward, ASGE
[2509.12394], the 2025 FF survey [2504.21662], and the probing-methodology literature) produced three
load-bearing reads:

1. **Our headline figures *are* the field standard — confidence, not novelty, on the measurement.** The
   Trifecta evaluates depth with exactly our F3⁺ (per-layer accuracy vs layer index; length-norm "plateaus or
   even declines", batch-norm rises) and its representation read is *"multi-layer classifiers trained with
   backprop on frozen features from each FF layer"* — i.e. our **DECIDE** max-power readout. Their flat baseline
   is a **6-layer FCN, 2048-wide on CIFAR-10** — direct precedent for our CIFAR-10-flat headline.
2. **Two papers now back the *goodness* lever over the *batch-norm* lever** — DeeperForward **and** ASGE both
   keep a per-sample norm and fix the goodness (linear/mean; spatial-mean) to earn depth, against the Trifecta's
   batch-norm. This strengthens (does not change) the [grid-widening decision](#design-decision-recorded-2026-06-21--p21-widens-to-a-goodness--norm-grid-why-p20-logs-the-cause):
   the **layer-norm + linear-goodness** corner is the substrate's best bet, and the corner the Trifecta never
   tests.
3. **The substrate regime is unexplored in the FF literature.** The survey catalogs the whole zoo but notes
   **continual / online / single-sample FF is "not addressed."** So P2.6's online + continual-veto questions
   have *no prior answer* — the sim is the only oracle (don't expect to import a result).

**The change to this card (my position, committed): DECIDE adds selectivity controls.** A max-power *nonlinear*
probe has **low selectivity** (Hewitt & Liang 2019, the probing-classifier critique): a high accuracy on
frozen features can mean the *probe* solved the task, not that SCFF *encoded* the class — and our 2-seed preview
sat right on the line (gap **+0.049** vs the 0.05 lost/entangled threshold), so the verdict that **routes the
whole phase** was too fragile to trust bare. The fix (now in [`run_exp0.py`](run_exp0.py)): run the *same*
max-power MLP on three feature sets + the GD ceiling —

- **SCFF** (frozen all-tap, under test) · **RANDOM** (frozen random-projection, *identical shape, untrained* —
  the selectivity floor) · **RAW** (raw input — is the test even informative?) · **pure-GD** (the ceiling).
- Report **selectivity = SCFF − RANDOM** (what SCFF *training* added that the probe can read) alongside the
  ceiling gap. A small selectivity flags an "entangled" verdict as probe-driven, not a property of SCFF; if
  RAW ≈ GD the whole DECIDE is moot. The linear-probe-vs-MLP gap on SCFF *is* the literature's
  "nonlinearly-entangled" measure — we already log both.

Also fixed: the F3⁺ caption hardcoded "DECLINES" even when the synth slope is positive (a caption-vs-data drift
result-format.md forbids); it is now slope-aware. The headline *decline* leans on **CIFAR-10-flat** (the
documented wall); synth carries the F6⁺ dial and a fast sanity, as already locked above.

**Addendum (F3⁺ gets a *candidate* line — and a goodness-scale trap caught en route).** F3⁺ now overlays three
curves so old-vs-new-vs-GD is one figure (exp-1 format, GD matched-depth to span the same 1..L axis): **old
SCFF** (the wall, length-norm + squared, two-sided θ=2.0) · **new SCFF** (the DeeperForward-style candidate) ·
**pure-GD**. Building the candidate surfaced a **scale bug worth recording** (sign/scale paranoia paid off):
under layer-norm the linear goodness sits at **G ≈ 35**, *far* above θ=2.0, so the two-sided loss
**saturates to zero positive-branch gradient** and the cell never learns (it pins near chance — looked like a
label swap, was actually a dead loss). The fix is the **threshold-free contrast loss** (push `G_pos > G_neg`,
scale-invariant) — *required*, not cosmetic. Verified at 15 epochs on synth: wall slope **−0.0045** (declines)
vs the contrast candidate **+0.0054** (rises) — the DeeperForward thesis in the preview. **The portable lesson
for P2.1: a fixed θ is not transferable across goodness×norm cells** (each cell's goodness scale is different);
P2.1 should run the grid under the **threshold-free loss** (or per-cell mean-goodness scaling), never a shared
θ. The candidate line bundles 3 changes vs the wall (norm + goodness + loss); P2.1 decomposes which axis earns
the depth — here it is one named "DeeperForward-style" preview, not a controlled ablation.

**Data note — CIFAR source (2026-06-21).** `fetch_openml("CIFAR_10")` is **broken on this machine**: the
download truncates (~26k of 60k rows) so the md5 never matches sklearn's metadata and it errors out (consistent
with the known npm/cert/network quirks here). The cached `.arff.gz` *decompresses cleanly* and its ~25.7k rows
are **class-balanced over all 10 classes** (~2.5k each, verified), so [`run_exp0.py`](run_exp0.py)'s
`load_cifar_local()` parses that cache **directly** (bypassing the md5 check) and draws the 5k/2k split from it.
This is sound for P2.0: CIFAR-10-flat is an explicit **depth probe, not a benchmark claim** (README §2), and a
balanced 25.7k pool is ample. The manifest records the run; reproducers on another machine can point
`load_cifar_local` at any full `CIFAR_10.arff.gz` or restore the openml fetch.
