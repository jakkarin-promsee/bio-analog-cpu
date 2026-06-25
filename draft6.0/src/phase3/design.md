# Phase 3 — Make the cheap forward-only bulk earn depth by changing *what each layer optimizes*

> **Status: ✅ COMPLETE (2026-06-22, P3.0 → P3.3) — ADOPT the objective reframe.** The arc: the objective
> *family* is the lever (P3.0 — contrast preserves class info, energy/reconstruction don't); cross-layer
> coordination (Direction 1) eases the decline (P3.1) and, **given depth headroom, makes `contrast +
> coordination` *compose* depth — rising, matching/beating GD (P3.2), overturning P2.2's "depth intrinsic to
> forward-only locality"**; and it **re-earns and *improves* the Phase-1 continual win** (P3.3 veto: BWT −0.017 vs
> energy −0.026, SCFF-probe flat). **Verdict: `[contrast (InfoNCE) + coordination w≥2] bulk + sleep-consolidated
> readout` is a strict upgrade over energy-goodness and supersedes it as the SCFF objective.** Synthesis pending
> ([`RESULTS.md`](RESULTS.md) is the ledger); the metric/figure contract is [`result-format.md`](result-format.md).
> → **Phase 4** (maintenance: Ch7 gate + sleep-cadence) tunes against this cell.
> Builds on Phase 2's bench (`../phase2/p2lib.py`, the P2.1 healthy cell, the exp4 continual harness) and the
> survey in [`../../research/papers/`](../../research/papers/README.md).
>
> **Read [`../../research/papers/phase3/the-objective-reframe.md`](../../research/papers/phase3/the-objective-reframe.md) first.** v2 changes from v1:
> the prediction target is **decided** (masked-feature reconstruction), the ladder is **reordered to lead with
> the make-or-break objective swap**, and the phase numbering is **resolved** (this is Phase 3; maintenance → 4).

---

## 0. Why Phase 3 exists — and the decision that the old SCFF is broken *for depth*

Phase 2 proved, oracle-tight, that **energy-goodness SCFF** (`G=Σh²`) cannot earn depth — not via transmission
(P2.1) nor via any negative-selection within the energy family (P2.2). **Energy-goodness SCFF is broken as a
depth substrate, and we stop trying to fix it.** *(Its Phase-1 win — shallow, forgetting-robust, continual —
still stands; that is a separate, validated result. What's broken is energy-goodness *with depth*.)*

The Phase-3 literature pass found the one lever Phase 2 never touched — a different **objective family**:

> **The depth wall is intrinsic to the energy objective, not to forward-only locality.** Greedy InfoMax / CLAPP
> ([1905.11786](https://arxiv.org/abs/1905.11786), [2010.08262](https://arxiv.org/abs/2010.08262)) are
> forward-only, gradient-isolated, **unsupervised** local learners whose representations *improve with depth* —
> because the objective is **information-preserving / predictive**, not energy. A 2026 benchmark tests **SCFF by
> name** and shows the predictive family **matches end-to-end backprop-SSL**
> ([2601.21683](https://arxiv.org/abs/2601.21683)). And this is not new: **greedy layer-wise unsupervised
> pretraining** (stacked denoising autoencoders, Bengio 2007; DBNs, Hinton 2006) was the *original* way deep nets
> were built — layer-local, unsupervised, before end-to-end backprop existed. We are returning to the proven
> unsupervised-depth objective, in forward-only local form.

**The Phase-3 question:**

> **Can a forward-only, unsupervised SCFF-family layer be made to *compose with depth* by changing what it
> optimizes — from energy (`density`, which homogenizes) to information-preservation (`structure`, which must be
> kept) — while staying single-sample-online and preserving the continual win?**

The continual veto is the same non-negotiable as Phase 2: **a depth-fix that costs the continual win is
rejected** (P3.3). And because the objective is *new*, the Phase-1 continual win **does not transfer for free** —
the new cell must *re-earn* it.

### The decided answer to "what does a flat-MLP layer predict?"

v1 left this as a sweep. **Decided: a flat-MLP layer predicts the input dimensions masked out of it —
per-layer masked-feature reconstruction (a local denoising objective).** Each layer carries a small auxiliary
decoder `D_l`; the layer's "goodness" becomes *how well `D_l·h_l` reconstructs the held-out dims of its input*.
Five reasons it beats the alternatives:

1. **It dissolves the "flat vectors have no structure to predict" problem.** There is no "next patch," but there
   are *always* held-out dims. Well-defined on any vector — the cleanest fit to the flat-MLP substrate.
2. **It is the only fully single-sample-pure option.** Needs nothing but the one sample (mask dims → predict
   them): no negative bank, no augmentation pairs, no EMA target, no batch. The substrate *is* single-sample.
3. **It directly cures the diagnosis.** The wall *is* information loss with depth; reconstruction *penalizes*
   information loss by construction — you cannot reconstruct what a layer threw away. The mechanistic opposite of
   the energy wall's homogenize-and-shed.
4. **It is a one-line reframe of "goodness."** energy `Σh²` → reconstruction quality `−‖D_l h_l − a_masked‖²`;
   same forward machinery, swap the local loss.
5. **It has the strongest existence proof** — greedy layer-wise denoising autoencoders built deep unsupervised
   representations a decade before SCFF (Hinton 2006 / Bengio 2007), and GIM names *info-preservation* as exactly
   why its depth composes.

**Kept as the control, not the primary: sibling-contrastive (CLAPP-style).** The GIM/CLAPP existence proof is
*contrastive*; I keep one contrastive cell to answer "is pure preservation enough, or do we also need the
discriminative signal?" It needs negatives/augmentations (more machinery, less single-sample-pure), so it is the
comparison, not the headline. **Dropped from the objective grid: next-layer-state prediction** — degenerate as a
core objective on a feedforward flat-MLP (predicting a deterministic function of your own output is trivial); it
belongs as the *coordination* lever (= your Direction 1) in P3.1.

---

## 1. The levers (carried from the Phase-3 survey)

| lever | source | what it changes | unsupervised? | substrate note |
| --- | --- | --- | --- | --- |
| **masked-feature reconstruction** | denoising-AE (Hinton'06/Bengio'07), GIM | goodness = reconstruct held-out input dims (info-preserving) | ✅ | **single-sample-pure**; one small decoder/layer |
| **sibling-contrastive (CLAPP)** | GIM, CLAPP | pos pair agree / neg pair disagree in rep (InfoNCE) | ✅ | reuses SCFF dual-rail + LUT negatives; needs aug on CIFAR |
| **cross-layer goodness (OLU / DF-O)** = your Direction 1 | Trifecta, Distance-Forward | a layer also helps the next layer's objective (2-layer window) | ✅ | 2 layers' activations live (have the buffers) |
| **direct feedback (top-down)** | 2601.21683, DFA | top-layer activations reference all lower layers | ✅ | one top-down broadcast wire (price it) |
| **Mono-Forward (per-layer CE)** | Mono-Forward | tiny class projection + local cross-entropy per layer | ❌ supervised | the proven flat-MLP fallback / a cheaper namer |

**The wall to beat is already measured — do not re-derive it.** The P2.1 healthy cell declines at slope
**−0.020** (probe L1→L8 = 0.333→0.197) on CIFAR-flat; GD-hidden envelope ~0.354. Carry that curve as the
reference (and reproduce it as a regression guard, like P2.1's WALL_REF).

---

## 2. Tasks (rough — confirmed in result-format)

| role | task | why |
| --- | --- | --- |
| **headline wall** | **CIFAR-10-flat** (`load_cifar_local`) | the documented wall; directly comparable to P2.1/P2.2. Masked-reconstruction needs *no* spatial layout — masking random flat dims works natively. |
| **dial / sanity** | **synth Tier-B** (`make_tierb`) | fast sanity; for the *sibling* control, "sibling = same cluster" is clean here without augmentation. |
| **continual veto** | digits / MNIST class-incremental (exp4 exact) | where the Phase-1 win lives; the veto regime. |

*(v1's "structure-exposed pixel-block" task is **removed** — masked-reconstruction dissolved the need for it.
A pixel-block task only returns if a *spatial-predictive* objective is ever tested, which it currently isn't.)*

Seeds `[42,137,271,314,1729]`, median + IQR (3 for continual); standing methodology rules apply.

---

## 3. The experiment ladder (purpose → sub-experiment → steps; pass-gates rough)

Leads with the make-or-break (Phase-2's actual discipline — P2.0 led with the decisive router, not the cheapest
code). Control in every rung = the P2.1 energy wall + the GD-hidden ceiling + a random-projection selectivity
floor (the control that *saved* Phase 2 — kept permanently).

### P3.0 — The objective swap (THE make-or-break gate; the locked first run)
> **✅ RAN (2026-06-21, 3 objectives, 5-seed CIFAR): PARTIAL — objective axis decided, residual decline → P3.1.**
> The objective *family* is the lever (reframe confirmed): energy decays *through* random (−0.020);
> **masked-recon** flattens but is *below* random (selectivity −0.062, preserves density); **contrast
> (CLAPP/InfoNCE)** stays *above* random at every depth (selectivity **+0.060, 5/5, growing with depth** —
> preserves class) **but still declines** (−0.016). So: the right objective = **discriminative preservation
> (contrast)**, and the wall is intrinsic to the *energy objective*, **not** to forward-only locality. The
> residual contrast decline = the **cross-layer-coordination gap** → **route to P3.1 (OLU / Direction 1) on the
> contrastive objective.** Mono-Forward fallback **not** triggered. Result: [`exp0/experiment-0.md`](exp0/experiment-0.md);
> ledger: [`RESULTS.md`](RESULTS.md).
- **Purpose.** Replace energy goodness with **masked-feature reconstruction** and ask the core question: does
  per-layer separability stop declining (slope ≥ 0) with depth, unsupervised? Plus the contrastive control.
- **Sub-experiment.** Objective grid: {**masked-reconstruction** (primary) · **sibling-contrastive** (CLAPP
  control)} vs the energy WALL_REF, depth-slope on CIFAR-flat (+ synth sanity). One objective at a time.
- **Steps.** (1) extend the SCFF cell with a pluggable local objective: a per-layer decoder `D_l` + mask + MSE
  (reconstruction) and an InfoNCE variant (sibling). Anti-collapse guards: layer-norm on, mask non-trivial,
  `D_l` a *separate* auxiliary head (never the forward weights). (2) `run_p3_0.py`: objective grid + WALL_REF
  regression guard + GD ceiling + random-projection floor. (3) smoke (synth, 2 seeds) → CIFAR 5-seed,
  single-threaded (OpenMP phantom guard).
- **Diagnostics (the "why").** depth-slope · **info-preservation curve** (reconstruction error vs depth — does
  info actually survive deeper?) · dead-unit % · effective-rank · selectivity (vs random) · **a light continual
  sniff** (does the new objective obviously forget? — the early veto catch, full veto = P3.3).
- **Rough pass-gate (make-or-break).** At least one objective reaches **depth-slope ≥ 0** (or decisively toward
  0) while unsupervised. **If neither does, STOP and rethink** (route to P3.1 *only* to test whether coordination
  rescues a near-miss; then fall to the Mono-Forward fallback, P3.2). Mirrors the P2.1 STOP discipline.

### P3.1 — Coordination (your Direction 1): does it help, and is it needed?
> **✅ RAN (2026-06-22, coordination window on contrast, 5-seed CIFAR): PARTIAL — Direction 1 works; flat-CIFAR
> has no headroom.** Window `w` on the contrastive cell: w1 (=P3.0) −0.0158 → **w2 −0.0105** (~33% flatter, deep
> endpoint 0.230→0.254, sel +0.066) → w4 saturates. **Synth (has headroom): w2 +0.002, w4 +0.008 — RISES.** So
> coordination is a real correct lever (eases decline, lifts deep layers, holds selectivity, rises where headroom
> exists), but flat-CIFAR can't show "rising" for *anyone* (GD-hidden flat ~0.36) → slope≥0 is the wrong bar
> there. **Lock `contrast + w2` → route P3.3 (continual veto).** Direct-feedback = optional static side-check.
> Result: [`exp1/experiment-1.md`](exp1/experiment-1.md).
>
> **✅ P3.2 side road A — DEPTH-HEADROOM CONFIRMATION (2026-06-22): DECISIVE PASS.** Built a flat-MLP task *with*
> headroom (GD-hidden rises 0.39→0.51). On it: energy declines (−0.006); contrast **w1 rises-then-FALLS** (+0.001,
> myopic); **w2 +0.012, w4 +0.022 — RISE MONOTONICALLY** (w4 0.41→**0.569**, above GD), sel +0.18, 5/5 seeds.
> **⇒ Given headroom, contrast + coordination COMPOSES depth (matches/beats GD); coordination is THE lever.
> P2.2's "depth intrinsic to forward-only locality" is OVERTURNED** (it was the energy objective). Flat-CIFAR's
> PARTIAL = a task-ceiling artifact. Result: [`exp2/experiment-2.md`](exp2/experiment-2.md). **→ P3.3 (veto).**
- **Purpose.** Test cross-layer coordination both as *your standalone idea* and as a *booster* on the P3.0
  winner. (Restructured from v1's "cheap probe" to a full rung — Direction 1 gets a real, fair test.)
- **Sub-experiment.** {OLU on energy-goodness (Direction 1 in its original form) · OLU on the P3.0 winner ·
  direct-feedback on the P3.0 winner}, depth-slope + final probe.
- **Steps.** (1) `train_step` flag: a layer also updates to raise the next layer's goodness (OLU window). (2)
  direct-feedback broadcast (top activations → all layers). (3) `run_p3_1.py`. (4) CIFAR 5-seed.
- **Rough pass-gate.** Coordination lifts slope/probe over the best P3.0 cell (disjoint IQR) → names the cheapest
  unsupervised recipe. If OLU-on-energy is flat but OLU-on-the-new-objective helps, that cleanly confirms
  "objective first, coordination second." *(Run iff P3.0 shows signal; else this is the rescue test.)*

### P3.2 — The supervised-local fallback + "cheaper namer?" (Mono-Forward)
- **Purpose.** The de-risk. If the unsupervised paths underdeliver, characterize **Mono-Forward** — the proven,
  flat-MLP-native, depth-capable local learner — and ask the bonus: could it replace the full-backprop GD blocks
  with something per-layer-local and cheaper?
- **Sub-experiment.** Mono-Forward depth-slope vs the SCFF wall vs the full-GD ceiling; cost (per-layer head
  weight vs full backprop).
- **Steps.** (1) per-layer projection `M_i` + local CE. (2) `run_p3_2.py`: depth + cost Pareto. (3) CIFAR 5-seed.
- **Rough pass-gate.** Mono-Forward earns slope ≥ 0 (expected) → the staged fallback + a candidate cheaper namer.
  *(Spends the unsupervised property → a fallback, not a default; an architecture decision, not just a result.)*

### P3.3 — Substrate filter + the continual veto (the deliverable; closes Phase 3)
- **Purpose.** Whatever wins P3.0–P3.2, run it through single-sample-online + the **continual veto** (ACC + BWT
  on the exp4 stream). The new objective must **re-earn** the Phase-1 continual win, not inherit it. Measure
  drift for the Phase-4 hand-off. Exact mirror of P2.6.
- **Steps.** (1) port the exp4 continual harness with the winning cell. (2) `run_p3_3.py`: ACC/BWT + SCFF-probe
  stability + drift. (3) 3-seed digits.
- **Rough pass-gate.** Surviving lever holds **depth-slope ≥ 0 AND BWT ≥ the Phase-1 baseline.** That recipe is
  Phase 3's deliverable.

---

## 4. The success criterion

> A **forward-only, unsupervised** SCFF-family bulk whose per-layer separability is **non-declining with depth**
> (slope ≥ 0) on the headline task — *earned by the objective, not by labels* — while staying single-sample-online
> and **preserving (re-earning) the continual win** (BWT ≥ Phase-1 baseline).
>
> **Fallback success:** if no unsupervised objective composes on flat-MLP, Mono-Forward still delivers a
> depth-capable cheap per-layer-local learner (a better "GD 20%" than full-backprop blocks), and the negative
> sharply characterizes why the substrate regime is special. Either outcome is a real deliverable (rule #5).

---

## 5. Order to build (cheapest-decisive-information-first)

**P3.0 (objective swap — the make-or-break)** → P3.1 (coordination / Direction 1) → P3.2 (Mono-Forward fallback)
→ P3.3 (substrate + continual veto). **P3.0 is the gate: if no objective reaches slope ≥ 0, stop and rethink
(coordination-rescue, then fallback) before P3.1.**

## 6. What to build (component checklist)

- **Pluggable local objective** in the SCFF cell — masked-reconstruction (decoder `D_l` + mask + MSE) and
  sibling-InfoNCE, swappable for energy goodness. **The core new primitive.** *(P3.0.)*
- **OLU window term** + **direct-feedback broadcast**. *(P3.1.)*
- **Mono-Forward cell** — per-layer `M_i` + local CE. *(P3.2.)*
- **Harness reuse** — depth-slope probe, REPR/INV, selectivity floor, the exp4 continual harness, drift logger —
  all from Phase 2. Metric/figure catalog → **[`result-format.md`](result-format.md)** (written: F3⁺ + SCORECARD
  shape metrics + INFOPRESERVE + SELECT + the 6+2 summary).

## 7. Where results go

One folder per rung (`exp0/`=P3.0 …), each an `experiment-N.md` with the spine **question → setup → run →
result → read → decision** (the *read* = the 6+2-slot template). Phase-wide arc in a **`RESULTS.md` ledger**,
one row per rung — the Phase-1/2 discipline.

## 8. Phase map (resolved) + open items

**Phase numbering — decided (override):** the old SCFF is broken for depth, so this depth-objective work *is*
the live next phase.

| phase | scope | status |
| --- | --- | --- |
| Phase 1 | structure + sleep (the continual win) | done |
| Phase 2 | depth, round 1 — *energy-goodness can't* (the decisive negative) | done |
| **Phase 3** | **depth, round 2 — the objective reframe (this plan)** | **active** |
| Phase 4 | online maintenance — the Ch7 gate + sleep-cadence (was "Phase 3") | future |
| north star | the recurrent lifelong brain | beyond the numbers |

*Doc sync (this commit):* CLAUDE.md, `idea/main.ideas.v1.md`, `context.md`, `phase2/design.md` §8 +
`phase2/README.md`, and the memory index updated to the new numbering.

**Still open (not blockers):**
- ✅ **result-format.md — written (2026-06-21):** [`result-format.md`](result-format.md). Depth-slope **+ the
  depth-shape SCORECARD** (peak-depth, decline-area, tail-retention, center-of-mass, N_eff) **+ the
  info-preservation curve** (reconstruction error vs depth) + the SELECT selectivity floor + the 6+2 summary.
- **Sibling-contrastive's CIFAR augmentation** — which cheap augmentation defines a "sibling" on flat CIFAR
  (the control needs it; the primary masked objective does not). Settle in result-format / P3.0 setup.

## 9. References

Full survey + verdicts: [`../../research/papers/`](../../research/papers/README.md). Core: Greedy InfoMax
[1905.11786](https://arxiv.org/abs/1905.11786) · CLAPP [2010.08262](https://arxiv.org/abs/2010.08262) ·
SCFF-named benchmark [2601.21683](https://arxiv.org/abs/2601.21683) · OLU/Trifecta
[2311.18130](https://arxiv.org/abs/2311.18130) · Mono-Forward [2501.09238](https://arxiv.org/abs/2501.09238) ·
greedy layer-wise pretraining (Hinton 2006 / Bengio 2007). Phase-2 verdict:
[`../phase2/README.md`](../phase2/README.md).
