# Experiment 0 — the sanity probe (full SCFF + full GD, alone)

> **Status: RAN — the gate PASSED** (with three evidence-backed config changes, locked in *Decision*: sum-goodness,
> the 2-D checkerboard task, layer-1 input-norm). This was the first thing run and the gate to everything
> (ladder 1.0 + 1.1). Convention: question → setup → run → result → read → decision. The spec is
> [`../design.md`](../design.md); the *why* is [`../../../idea/ideas1.md`](../../../idea/ideas1.md).

## Question

1. **Does SCFF separate at all?** Full SCFF alone — does goodness separate (`G_pos`↑, `G_neg`↓), and do the
   layers grow **more separable with depth** (linear-probe accuracy rising layer by layer)?
2. **What's the ceiling?** Full GD alone — the precision ceiling Exp 1–3 quote against.
3. **Two open knobs set here:** two-sided loss vs pure-contrast; and a cheaper **forward-only rival** as a
   bench check.

If (1) fails, stop — nothing downstream is interpretable until SCFF separates.

## Setup (LOCKED — methodology rule #3)

**First point only; Exp 1b sweeps size around it. Pick, lock, run, let the figure talk — don't overthink
the exact values.**

> **⚠ Superseded by the gate run (see ## Run).** The table below was the *pre-run* lock. The gate forced
> three evidence-backed changes: **goodness = sum not mean**, **task = 2-D checkerboard not spiral** (SCFF
> clusters by density; the spiral defeats SCFF-alone), and **input normalized at layer 1**. The current
> locked config lives in the *Decision* section. The table is kept for the audit trail.

| Knob | Value |
| --- | --- |
| Task | Tier-A **2-arm spiral**, 2-D, label noise σ = 0.10 (moderate), 2 classes |
| Held-out | **fresh draws** (never trained on), 2 000 samples, re-drawn per eval |
| SCFF stack | **4 layers, width 64**, ReLU, mandatory inter-layer norm, mono-forward dual-rail |
| Taps | last **n = 2** SCFF layers (128 features) |
| GD readout | **2 layers** (128 → 32 → 2), Adam-class, cross-entropy |
| Goodness threshold θ | start at **2.0** (open knob) |
| Negative partner | random sample from the current batch (stub) |
| Stream | **50 000** fresh samples, batch size **32**, single online pass |
| Eval cadence | held-out at **log-spaced** checkpoints (≈ 100, 300, 1k, 3k, 10k, 30k, 50k), no update |
| Seeds | `[42, 137, 271, 314, 1729]`, report **median + IQR** |
| Total weight count | **record it** (≈ SCFF 12.4k + readout 4.2k ≈ **16.6k**) → the full-GD control matches this |
| Realism | ideal floats; no analog/PVT, no gate, no sleep |

**Sub-cells (one variable each):**
- **0a** — full SCFF: **two-sided loss vs pure-contrast** (sets that knob).
- **0b** — full SCFF rule vs a cheaper **forward-only rival** (bench check).
- **0c** — full GD alone (the ceiling), total weights matched to 0a.

## Run

**Gate run — 2026-06-20, single seed (42).** Code: [`scff_gate.py`](scff_gate.py) (numpy-only; SCFF's
update is a closed-form *local* gradient, so no autograd). Diagnostics that drove the changes below:
[`diag_sweep.py`](diag_sweep.py), [`control_tasks.py`](control_tasks.py),
[`overlap_sweep.py`](overlap_sweep.py), [`decisive_learning.py`](decisive_learning.py). Figures + manifest
in [`figs_gate/`](figs_gate/). The 5-seed sweep + 0b rivals + 0c full-GD ceiling are the **expand** step,
not yet run.

**Three config changes were forced by results (each backed by a sweep, methodology rule #8):**

1. **Goodness = SUM `‖h‖²`, not mean `‖h‖²/M`** *(spec said mean; the sim overruled it).* With mean +
   unit-norm inputs, deeper-layer goodness is starved to `~2/M/2 ≈ 0.015`, far below θ=2.0, so plain SGD
   can't move it (reference FF only reaches θ=2.0 via Adam × 1000 epochs — not our online single pass).
   Sum-goodness is `~1.0` at init, **width-independent**, makes θ=2.0 sane, and is substrate-faithful
   (no per-weight Adam state). This **vindicates `ideas1.md`'s `G=‖h‖²`** over `SCFF.detail.md`'s `/M`.
2. **Task swapped: 2-arm spiral → 2-D 4×4 checkerboard of Gaussian clusters** (16 clusters, label
   `(i+j) mod 2`). **SCFF clusters by *density*, not class** — it makes real samples loud and blends
   `x_k+x_n` quiet, which recovers classes *only when classes are density-separated clusters*. The spiral's
   two arms are equal-density interleaved manifolds, so SCFF-alone sits at ~0.55 on it across every config
   swept (θ, lr, init, objective, 150k samples). A 4-cluster task is the opposite failure — a *random*
   projection already solves it (SCFF learning adds nothing). The 16-cluster checkerboard is the 2-D task
   that is density-separated **and** too hard for random features, so SCFF's *learning* measurably wins.
   The spiral moves to the GD cells (Exp 1+), where GD cracks what SCFF can't.
3. **Input normalized to unit length at layer 1 too** (`normalize_input=True`). Without it, the raw-input
   2× head-start gives layer 1 goodness ~360 at init; θ=2.0 then suppresses it so hard that 64–91% of L1
   units die, confounding every depth read. Normalizing the input gives a uniform goodness scale (~2.0)
   across all layers and zero dead L1 units — at the cost of the magnitude head-start (S2/Ch3), so layer-1
   contrast is now directional, which is weaker in 2-D. **This is a real tension with the spec's
   "first layer learns from magnitude+pattern" — flagged for ratification, not silently locked.**

## Result / figures

Emitted per [`../result-format.md`](../result-format.md) (F4, F3, F5, INV; F1 deferred to the expand step,
where the full-GD ceiling exists). House style applied; single-seed here, IQR bands come with the 5-seed
expand.

- **F5 — boundary** ([`figs_gate/F5_boundary.png`](figs_gate/F5_boundary.png)): the tapped-SCFF readout
  draws a clean checkerboard over the 16 clusters, **held-out acc 0.769** (chance 0.5). Non-toy — *look at it.*
- **F4 — goodness separation** ([`figs_gate/F4_goodness.png`](figs_gate/F4_goodness.png)): per-layer gap
  `G_pos − G_neg` climbs from ~0 to **+0.10…+0.14** over training (all 4 layers); top-layer histogram shows
  `G_pos` (mean 2.07) shifted right of `G_neg` (1.98) around θ=2.0 — **weak but real** separation (low-D).
- **F3 — separability heatmap** ([`figs_gate/F3_separability.png`](figs_gate/F3_separability.png)): L1 probe
  rises **0.66 → 0.80** over training (SCFF *learns*); depth does **not** add (L1 best, gentle decline to
  L4) — expected, "rises with depth" is a hierarchical high-D property, absent on a task one layer captures.
- **INV** ([`figs_gate/INV_strip.png`](figs_gate/INV_strip.png)): loss slope smooth; dead-unit fraction L1=0
  (the input-norm fix), deeper layers 0.05–0.23 (healthy).

## Read (pass criteria)

> Write the read-up with the six-slot template ([`../result-format.md`](../result-format.md) Layer C):
> claim → number-with-IQR → figures → mechanism → threats → decision. The pass criteria below are slots 1–2.

- **(1) SCFF separates — the gate:** goodness separates *and* per-layer probe accuracy **rises with depth.**
- **(2) Ceiling:** record full-GD held-out accuracy + its memorization gap as the Exp 1–3 reference.
- **(0a / 0b):** which loss / rule converges cleaner — sets those knobs for everything downstream.

### Six-slot read (gate run, seed 42 — `result-format.md` Layer C)

1. **Claim.** Full SCFF, trained label-free with sum-goodness + a random-batch negative, builds
   *class-separable* features that beat its own random init on a task random features can't solve, and its
   per-layer goodness separates positives from negatives.
2. **Headline number.** Tapped-SCFF held-out **0.769** (chance 0.50); L1 probe **0.66→0.80** with training;
   goodness gap **+0.10…+0.14** by 50k samples. Single seed — IQR pending the expand step.
3. **Figures.** F5 (checkerboard boundary, the visual), F4 (gap grows + pos/neg histogram), F3 (L1 learns,
   depth flat), INV (healthy, L1 dead=0). F1 + the reachability surface (F6) come with the GD ceiling.
4. **Mechanism.** SCFF's loss makes coherent samples loud / blends quiet → it learns *where the data is*
   (density). On density-separated clusters that **is** class structure; on the spiral's interleaved equal-
   density arms it is not, which is why SCFF-alone fails the spiral and the gate task had to be a cluster
   task. Sum-goodness keeps the per-layer signal alive under plain SGD; the gap stays small in 2-D because
   the directional contrast (post input-norm) is intrinsically weak there.
5. **Threats to validity.** (a) **SCFF is a weak low-D learner** — gain over a random projection is only
   +0.06; the thesis bet is that this is enough for GD to read, which Exp 1 tests, not exp0. (b) Single
   seed; 4 of the changes are design decisions, not 5-seed-verified. (c) **input-norm removed the magnitude
   head-start** (spec tension) — the weak goodness gap may partly be that, not a deep property; the 0a
   two-sided-vs-contrast and a per-layer-θ variant could revisit it. (d) "rises with depth" is untestable
   on a 2-D task one layer captures — needs a higher-D hierarchical probe to claim it at all.
6. **Decision.** See below.

## Decision

- **Gate: PASS** on the core question (goodness separates ✔, features class-separable ✔, SCFF learning beats
  random ✔). "Rises with depth" is **reframed** — not achievable on a 2-D single-layer-capturable task;
  re-test on a higher-D hierarchical probe in the expand step, don't gate on it here.
- **Locked for the expand step:** goodness = **sum `‖h‖²`** + plain local SGD; θ = **2.0** (works with sum);
  gate task = **2-D 4×4 checkerboard** (`sep 1.4, σ 0.30`); net **4×64**, taps **2**, lr_scff **0.03**.
- **Ratified 2026-06-20 (locked):** `normalize_input=True` — normalize the input to unit length at layer 1
  too. It removes the S2/Ch3 magnitude head-start (so layer-1 contrast is directional, weaker in 2-D) but
  fixes the 64–91% L1 unit-death and gives a uniform goodness scale. The per-layer-θ alternative that would
  *keep* the head-start is parked as a named variant to revisit if the weak 2-D goodness gap ever bites.
- **Open knobs still to set:** 0a two-sided vs pure-contrast (both run, two-sided used here — contrast gave a
  *larger* gap on harder tasks, worth the head-to-head); 0b vs Oja + random-projection rivals; 0c full-GD
  ceiling number to carry into Exp 1. These are the **expand** step.

---

## Full exp0 — 5 seeds, with IQR (2026-06-20)

Code: [`run_exp0.py`](run_exp0.py) (+ [`models_extra.py`](models_extra.py): hand-coded Adam MLP, Oja/GHA,
random-proj). Decisive high-D sanity: [`digits_check.py`](digits_check.py). Figures + manifest + raw arrays:
[`figs_exp0/`](figs_exp0/). Seeds `[42,137,271,314,1729]`, median [IQR]. Two readouts on purpose — a strict
**linear probe** (feature quality) and the spec's **2-layer Adam MLP** (the "system" number).

**Results (held-out, checkerboard):**

| cell | linear probe | MLP readout | note |
| --- | --- | --- | --- |
| **0c full-GD ceiling** | — | **0.943 [0.938, 0.943]** | the number Exp 1–3 quote; memorization gap **+0.001** (≈0 by construction under fresh-draw single pass) |
| 0a SCFF **two-sided** | 0.796 [0.769, 0.798] | 0.854 [0.852, 0.867] | the locked objective |
| 0a SCFF **contrast** | 0.791 [0.788, 0.796] | 0.855 [0.852, 0.863] | **≈ two-sided (within noise)** — keep two-sided |
| 0b **Oja/GHA** | 0.752 [0.750, 0.787] | 0.867 | cheaper rule, no edge here |
| 0b **random-proj** | 0.817 [0.761, 0.824] | 0.866 | **≥ SCFF, within noise** (see below) |

**Figures:** F1 ([`F1_learning.png`](figs_exp0/F1_learning.png)) — SCFF gives ~0.80 features *instantly* (no
training needed in 2-D), full-GD starts at chance, crosses SCFF at ~300 samples, reaches the 0.943 ceiling:
the cheap-but-capped vs expensive-but-precise trade, drawn. F4/F3/F5 ([`figs_exp0/`](figs_exp0/)) re-confirm
the gate at n=5. INV+rise ([`INV_and_rise.png`](figs_exp0/INV_and_rise.png)) — dead units healthy (L1=0);
the 3-D 64-cluster rise-probe shows SCFF *decreasing* with depth (0.59→0.53) while random-proj rises past it.

### The headline finding (and the resolution)

**On the low-D synthetic tasks, SCFF does NOT beat a random projection** (0b: linear 0.796 vs 0.817,
IQR-overlapping → "within noise" by `result-format`'s n=5 rule; the gate's seed-42 edge was a lucky seed).
**Why — and it is not a bug:** 2-D/3-D Gaussian clusters are *already* solved by random nonlinear features
(Johnson–Lindenstrauss), so SCFF has nothing to add. **Decisive control ([`digits_check.py`](digits_check.py),
64-D `load_digits`):** SCFF **does** beat random there — width 64: **0.841 vs 0.780**; width 256: 0.917 vs
0.898. SCFF's learning only pays off when the input is high-D enough that random features fail.

> **Implication for Phase 1 (flagged for the author):** the low-D *visualizable* tasks can validate that
> SCFF **separates** (gate ✔) and pin the **GD ceiling**, but they **cannot demonstrate SCFF beating
> random** — random is too strong a baseline in 2-D/3-D. The thesis comparison (SCFF+GD vs pure GD) needs a
> **high-D task brought forward** (MNIST flat-MLP, the spec's "later probe"), else Exp 1 risks "random
> features + GD readout would do just as well, cheaper." Recommend adding a high-D track at Exp 1.

### Six-slot read (full exp0)

1. **Claim.** Full SCFF separates and learns class-relevant features; on low-D it matches a random
   projection (random is already sufficient), and it beats random only on higher-D inputs.
2. **Headline numbers.** GD ceiling **0.943 [0.938,0.943]**; SCFF linear 0.796 ≈ random 0.817 (within noise,
   2-D); SCFF > random on 64-D digits (0.841 vs 0.780).
3. **Figures.** F1 (the cheap-vs-precise crossover), F4 (goodness separates), F3 (flat over depth in 2-D),
   F5 (checkerboard boundary), INV+rise (healthy; depth doesn't help in low-D).
4. **Mechanism.** SCFF optimizes density (real vs blend); on JL-easy low-D clusters that adds nothing over
   random features, so the win needs high-D where random fails. GD pays for direction and reaches a far
   higher ceiling given enough data, which is exactly the cost/precision split the architecture is built on.
5. **Threats.** 0b is a *low-D* null result, not a verdict on SCFF (digits rebuts it). The MLP readout
   washes out feature differences (use the linear probe for 0b). "Rises with depth" remains undemonstrated
   (needs high-D hierarchy). Single-pass fresh draws ⇒ memorization gap ≈0 by construction (not informative
   here; it becomes the Exp-1 read on a repeating/looped pool).
6. **Decision.** Below.

### Final decisions (exp0 → Exp 1)

- **GD ceiling to quote in Exp 1–3: 0.943** (checkerboard, 17k weights). Use this reference line in F1/F6.
- **0a: lock two-sided** (≈ contrast, simpler/standard). Contrast kept as a named variant (larger gap on
  harder tasks).
- **0b: SCFF's rule is validated** (beats random on 64-D digits) but **shows no edge on low-D** — so don't
  judge SCFF on low-D alone.
- **Phase-1 plan change to propose:** add a **high-D probe (MNIST flat-MLP)** at Exp 1 so the SCFF+GD-vs-GD
  comparison runs where SCFF's value is real; keep the 2-D checkerboard/spiral for *visualization* (F5) only.
- **Carry to Exp 1:** net 4×64, taps 2, θ=2.0, sum-goodness, input-norm, lr_scff 0.03, random-batch negative.
