# Bio-Inspired Analog Neural Compute Architecture — Part 2 (verify): the live, intuition-driven plan

> **What this file is.** The **re-drafted simulation plan** — built _intuition-first, phase by phase_, each
> phase shaped by the data from the one before. It supersedes `draft5.1-2.md` (the original §20/§21), which
> was a **rough pre-plan** sketched with Opus 4.7 to picture the whole project end-to-end. That file stays
> for reference; this one is the plan we actually run.
>
> **Ground rules — why this file exists:**
>
> - `draft5.1-1.md` is the **locked architecture/intuition** (§22 is law). This plan _serves_ it; it does
>   not touch it.
> - **A full, unedited plan is a myth.** We draft the next phase only once the current one has told us
>   enough. Every later phase is expected to shift. Phases below the current one are _sketches_, not
>   commitments.
> - The discipline of the old §20.2 still holds (one-thing-changed, reproducible seeds, failures-are-data)
>   — but here it is bent toward **characterization** (what does the thing _do_), not only convergence stats.
> - **The work lives in `src/experiment/phaseN/`** — scripts, figures, and per-experiment logs, entered via
>   its `README.md`. This doc is the _plan + status_; that folder is the _record_. Update status here.
>
> **Status (2026-06-03): Phase 1 re-scoped + started.** Deep characterization, organized as three axis
> folders, built to *understand* (show the effect), not just count. **Axis-1 rung-0 + rung-1 done:** rung-0 —
> exp-1 (prior, region 1–7) + exp-2 (limit, clean envelope, **xor ~0.50 wall**); rung-1 — exp-3, the ceiling
> is a **selective gain compressor** (crushes high-gain/long-range output, spares low-gain; shape shifts as it
> clips). Detail in `src/experiment/phase1/`. Later phases as the data arrives.

---

## Phase 1 — Ganglion Personality (characterize the atom before trusting the molecule)

**The frame (why this replaces "operator sanity").** We know what a line, a decision tree, an RBF _look
like_. We do **not** yet know what _our_ 2-3-3-2 Ganglion looks like — the family of input→output surfaces
it can make, and where its ceiling is — under the substrate's real constraints. "Do the operators compute
the right number?" (the old Phase 1) is necessary but far too thin, and folds in here as rung 0. The real
question: **what is the inductive bias / expressive personality of one Ganglion, and what is its limit?**
Characterize the atom before trusting the molecule. The Ganglion stays **2→2, 2-3-3-2 (locked, §22 #1)** —
"shapes" means the _surfaces_, not the topology.

This is also the **empirical test of the region-multiplexer thesis** (`notes/ganglion-role-switching.md`):
if the plots show piecewise-linear regions (L2's ReLU cuts) plus gain/saturation bends (L3/L4), the
"region multiplexer / axon projection" reading earns its keep — with eyes _and_ numbers, not assertion.

**Method — see it, then measure it.** One Ganglion; a 2-D input swept over a grid; plot each output channel
as a surface/heatmap. **Personality = the family of shapes reachable by sweeping the weights** (a seeded
random ensemble + a few hand-set extremes), not one weight accident. But eyes alone under-read — so every
surface also yields a **metric fingerprint** (below). Change exactly one thing per step.

### Two axes, kept separate (the core reframe)

The constraints split into **two different physics**; mixing them into one ladder makes a bend
un-attributable. So keep them apart.

**Axis 1 — the weight-capacitor limit (§6.6).** How the weight cap's ceiling distorts the surface:

| Rung | What's on | What we look for |
| --- | --- | --- |
| **0 — ideal** | `y = W·a + b`, plain floats; no ceiling, no saturation | the base shape; confirms the op math (folds in operator-sanity) |
| **1 — ceiling** | `w, b` hard-clamped to ±W_max | usable input/output range; how clipping distorts the shape |
| **2 — soft saturation** | `w` through a concave `1 − e^(−·)` map to the same rail | how realistic charge compresses the weight axis (vs the crude clip) |

> **Honest framing of rung 2.** The cap's `dV/dt ∝ (V_rail − V_cap)` is a _charging dynamic_ — how a weight
> _grows toward_ the rail over training. In a **static** forward sweep it has no signature beyond the ceiling,
> so rung 2 is the static _footprint_ of that saturation (a compressive weight map), **not** the live
> charging. Watching a weight actually charge up the curve is a Phase-2 thing (when weights move). The
> in-code `W_RAIL` lives in the Scap's _update_ path, so Phase 1 adds the footprint as a _forward_ toggle.

**Axis 2 — the op-amp nonlinearity (the activation).** What the output nonlinearity buys — and which one the
silicon actually wants:

- **Placement:** L2-only vs L2+L3. (The current code is **L2-only** — L3 is linear — so that point is free.)
- **Type:** linear → **ReLU** → **hard-tanh (clamp)** → **tanh**. Physics: a differential pair's natural
  transfer **is** tanh (BJT: `tanh(V/2V_T)` exactly; MOS: sigmoid-ish) — so **tanh is the _free_ op-amp curve,
  while ReLU costs an extra rectifier.** Hard-tanh = the op-amp with _hard_ rails (two-sided, still
  piecewise-linear → regions stay countable); tanh = _soft_ rails (smears the region count). Use ReLU +
  hard-tanh for the clean region metric, tanh for the true soft-saturation shape. (Ties to §21.5 and the
  role-switching note's "L3/L4 want amplification-to-saturation, not a ReLU clip.")

The payoff of the split: **tanh ≈ op-amp output ✓ but ≠ capacitor ✗** — the cap is a one-sided exponential in
_time_, not a two-sided sigmoid in voltage. Axis 1 is the cap; Axis 2 is the op-amp. Different math,
different physics, separate axes.

### Three structural probes the surface alone hides

Sweeping shapes shows _what_; these show _why_, and are specific to 2-3-3-2:

- **Bias as cut-placement.** The 8 bias Scaps (3·b_L2, 3·b_L3, 2·b_L4) _translate_ the ReLU hyperplanes —
  they decide _where_ a cut lands and whether it lands in-domain at all. Sweep bias range **separately** from
  weight: too small → knees pile at the origin (few regions); too large → neurons go always-on/off (dead).
  Bias is the region-multiplexer's placement knob.
- **Neuron activation census.** Per hidden unit, the fraction of the input grid where its ReLU is active.
  Counts the _working_ units (switching) vs dead (always-off) / trivial (always-on). The forward-structural
  precursor to dead-weight (H7); "3+3 hidden" is nominal, this is the real number.
- **Output-channel coupling.** out[0] and out[1] are two linear readouts of the _same_ 3 L3 features (they
  diverge only at L3→L4), so the pair is ≤ rank-3 and correlated by construction. Measures whether one
  Ganglion can make two _independent_ shapes or yokes them.

(Minor axis: input **range/sign** — the same weights give different region structure on [0,1]² vs [−1,1]² vs
wider; run as a variant where it matters, not its own study.)

### The metric fingerprint (eyes + numbers)

Probes per surface: 2-D heatmap · 1-D slices + the **diagonal cut** x₁=x₂ (the direct `(x₁+x₂)` response) ·
contour/level-sets · the **Jacobian field** ∂out/∂x (piecewise-constant for PWL activations → each region is
one flat-gradient patch; the money plot for the thesis).

Metrics, each tied to a question (no metric-for-its-own-sake):

| Metric | Question it answers |
| --- | --- |
| # linear regions (constant-Jacobian patches) | region-multiplexer thesis; the ≤3 / ≤7 count |
| linear-fit residual (surface − best plane) | how much nonlinearity is actually used (§19.2 #6) |
| max‖∇‖ (Lipschitz) | max boundary sharpness; saturation effect (H10/§6.6) |
| neuron-active fraction | dead/working census (H7 precursor) |
| out[0]–out[1] correlation / rank | output independence; effective 2→2 capacity |
| PCA over the surface ensemble (comps @ 90%) | the shape family's effective dimensionality — richness in one number |
| best-fit MSE to each reference target | reachability **limit** per shape (the headline gate) |

Reference targets: {plane, paraboloid `0.1(x₁+x₂)²`, saddle `x₁·x₂`, gaussian bump, XOR-checker}. The best
achievable residual per target = the atom's limit on that shape (XOR-checker is the expected limit-marker).

### Structure: spine + branches, staged core-first

A full cross-product (3 rungs × 2 placement × 4 type × 2 residual × N seeds × M targets) is thousands of
un-eyeballable plots and violates one-thing-changed. Instead a **spine** with **branches**, each branch
moving one axis:

- **Spine:** climb Axis-1 (rung 0→1→2) at a default activation (ReLU, L2+L3 — the spec-canonical Ganglion),
  plain, over the seed ensemble + hand-set extremes.
- **Branch A (placement):** at rung 0, L2-only vs L2+L3 — does the 2nd activation multiply regions? (current
  code = L2-only, the free point)
- **Branch B (type):** at rung 0, linear / ReLU / hard-tanh / tanh — saturation shape; the free-op-amp probe.
- **Branch C (residual ×2):** rerun the spine + key branches with the §7.7 L1→L4 bypass on — how identity-add
  shifts the family (toward near-identity at small init, §14.5) and whether it cuts the dead/flat fraction
  (the shape companion to H8).

**Staged.** Build the **core fingerprint first** — heatmap + Jacobian/region-count + curvature + neuron
census, on the spine + Branches A/B. That answers the headline questions cheaply. Then add the **deep layer**
— bias sub-sweep, output-rank, PCA-dimensionality, reachability residuals, the range axis — only if the
personality looks worth it. §20.2 discipline applied to metrics, not just loss.

### The gate is understanding, not pass/fail

Phase 1 is done when we can answer, with figures **and** the metric table:

- What family of surfaces can one Ganglion make? Where does it saturate / clip / go flat?
- Does the 2nd activation (L3) buy expressivity, or not? → decides the open activation question (§19.2 #6).
- Does the picture confirm the region-multiplexer reading — and **how many linear regions can one 2-3-3-2
  actually carve in 2-D?** (The note guesses ≤3; three L2 lines alone cut a plane into ≤7, and L3 folds
  further. Phase 1 measures the _real_ number — the atom's headline capacity.)
- Is tanh (the free op-amp curve) a comparable or richer nonlinearity than ReLU?
- How many of the hidden units actually work, and can the two outputs be independent?
- What can the atom _not_ reach (the target residuals)?
- How does residual change all of the above?

**Discipline.** One thing changed per rung/branch; a fixed seed set for the ensembles (figures reproduce);
log config + figures + the metric row; an interesting collapse is _data_ (it marks a limit). Exploratory but
systematic — not the multi-seed convergence statistics of the later phases.

**Code note (one-time `simulator-code` prep).** Small additions to the frozen kit, all defaulting to current
behavior, none a §22 matter (toggles + viz, topology untouched): a rung-0 ideal path (forward already has no
ceiling/sat), a **forward** ceiling clamp, a **forward** soft-saturation map (the static footprint — distinct
from the update-time `W_RAIL`), an activation **type + placement** switch (linear/ReLU/hard-tanh/tanh at
chosen layers), the §7.7 residual toggle, and the metric/probe library (grid sweep, Jacobian/region-count,
curvature, neuron census, PCA, reachability, output-rank). Enter via `src/experiment/phase1/README.md` (the
concise phase summary); the three axes — **weight-cap, activation, residual** — each get their own folder +
README (full detail) under it.

**Output → next phase.** The personality fingerprint is the input to the next phase: once we know the atom,
we ask what _molecules_ of it (Ganglion networks) can and can't do.

---

## Later phases — drafted one at a time, as data arrives

Deliberately **not** pre-written (see the ground rules). The immediate next, once Phase 1's pictures exist:

- **Phase 2 (sketch) — Ganglion-network characterization.** Compose Ganglions (a Column / a small DAG) and
  ask the same _"what shape, what limit"_ question one level up, now that the atom's personality is known.
- Everything beyond that is re-derived from data, not committed here. The old `draft5.1-2.md` table
  (MVF → operator-sanity → single-Ganglion → … → 256-scale) stays as an _illustrative_ end-to-end scaffold
  to sanity-check direction against — **not** the running order.

---

_This file grows downward, one phase at a time, as the data comes in._
