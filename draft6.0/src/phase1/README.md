# Phase 1 — structure, and where the cell wins

> **✅ Complete (2026-06-20, exp0 → exp4).** The front door to Phase 1 — the navigable overview. The deep story
> with every figure is **[`phase1-report.md`](phase1-report.md)**; the scalars are **[`RESULTS.md`](RESULTS.md)**;
> the pre-run design + build spec is **[`design.md`](design.md)**.
>
> **Verdict in one line:** draft 6.0 is a cheap, forgetting-robust **continual** learner — one SCFF+GD block
> generalizes better than backprop (smaller memorization gap) at ~10% backward cost, and in the continual regime
> a periodic **sleep** recovers what online backprop catastrophically forgets. It is **not** a deep static-accuracy
> competitor — *and that's the point.*
>
> *↑ In the arc:* **Phase 1** of the eleven-phase story ([map](../README.md) · [Stage 1](../stage1-report.md)) — the spine under all of it: [`the-essence2`](../../../docs/essence/the-essence2.md).

---

## The problem

Draft 6.0 committed a spine on paper — a cheap, unsupervised **SCFF** front that organizes the world for free, and
a small, precise **gradient-descent** back that names the features — but not a single simulation had run. Phase 1
stops arguing the theory and lets the behavioral sim talk. The question was deliberately **not** "does this beat
backprop on accuracy" (backprop's game, on a substrate built for it) but **where does a cheap, local, forward-only
learner actually earn its keep?**

## What we did

- **Cell under test:** one *block* — a 4-layer SCFF feature stack (width 64, ReLU, mandatory inter-layer norm,
  mono-forward dual-rail) with a small GD readout that taps every SCFF layer.
- **Tasks:** a 2-D checkerboard (visualization), `load_digits` (64-D), MNIST (784-D — the high-D track).
- **Baselines:** a matched-budget pure-GD MLP (the precision ceiling); an untrained random projection (the null).
- **The ladder:** exp0 gate → exp1 block-vs-GD → exp2 ratio/plasticity → exp3 boosting chain → **exp4 continual**.

## What we found

The win is the **continual** regime, and the figure that carries the phase is the rot-vs-sleep curve:

![rot vs sleep — the win](exp4/figs_exp4_mnist/exp4_rot_sleep.png)
*Online learning ROTS to chance (catastrophic forgetting: digits 0.18, MNIST 0.19); a periodic **sleep**
consolidation recovers to the static ceiling (0.935 / 0.865); and the SCFF all-class probe stays **flat** the whole
way — the features never forget. (n=5, class-incremental stream.)*

The arc that got there:

- **exp0 (gate):** SCFF separates — but it clusters by **density, not class** (an equal-density spiral defeats it),
  and in low-D a random projection ties it (its value is a *high-D* bet). Forced three spec fixes: goodness = **sum**
  `Σ‖h‖²` (not the paper's mean), θ=2.0, input-norm on.
- **exp1 (block vs GD):** the headline is the **memorization gap** — MNIST block **+0.027** vs GD **+0.062**
  (disjoint IQR, 5/5) at **~10%** of the backward cost. But SCFF features **degrade with depth**, so the readout must
  tap *all* layers (the spec's "last n" read the worst ones). Default size **H=64**.
- **exp2 (interior):** there is **no free-lunch SCFF:GD ratio** — accuracy declines monotonically with SCFF
  fraction; the only real saving is the costly input layer. Plasticity slowdown is a *drift* fix, not a *depth* fix.
- **exp3 (boosting chain):** a chain of shallow GD-corrected blocks beats a single block and approaches GD, but
  **saturates after ~2 blocks** — boosting wants *diversity* (full residual ε=1), not preserved features. The
  "deep brain matches GD on static accuracy" story is **not** the win.
- **exp4 (continual — the win):** SCFF is **forgetting-robust** (new classes *add* clusters, don't overwrite), so
  forgetting lives entirely in the readout, and a cheap sleep over a prototype **LUT** fixes it — recovering at a
  third of the store. **Continual is the architecture's validated home.**

## What it set (decisions)

goodness = **sum `Σ‖h‖²`** · θ=2.0 · **input-norm on** · **tap ALL SCFF layers** (corrects S3) · two-sided loss
(≈ contrast within noise) · **full residual ε=1** (N3 boosting; Ch9 delta off) · **slow read-layers** ρ≈0.3 (N2 —
a drift fix) · default **H=64**. Sleep (S7) + LUT (S8) **confirmed**.

## Validated vs not

| | status |
| --- | --- |
| SCFF = cheap, label-free, local, forward-only feature learner | ✅ |
| One block generalizes better than backprop (smaller gap) at ~10% backward cost | ✅ |
| **SCFF is forgetting-robust → cheap continual learning via sleep + LUT** | ✅ **(the win)** |
| Boosting chain > single block, approaches GD | ✅ (modest, saturates) |
| "Deep 80%-SCFF brain matches GD" on static tasks | ❌ (weak, shallow-is-better) |
| SCFF beats GD on raw static accuracy | ❌ (GD wins; block is cheaper + generalizes) |

**The through-line that opens here (density ≠ class):** SCFF's energy goodness learns *where the data is dense*,
which is class only when classes are density clusters. That one wound drives the next three phases — it degrades
with depth (Phase 2), the *objective* turns out to be the lever (Phase 3), and the map reads the whole cell as a
density/structure learner with a cheap class-namer (Phase 4).

## Read next

| For | Go to |
| --- | --- |
| The full story, every figure, the per-experiment reads | [`phase1-report.md`](phase1-report.md) |
| The scalar ledger (numbers + decisions) | [`RESULTS.md`](RESULTS.md) |
| The pre-run design + build spec (how each rung was set up) | [`design.md`](design.md) |
| The run-cards (six-slot atomic records) | `exp0/` … `exp4/` `experiment-*.md` |
| Figure/house style | [`result-format.md`](result-format.md) → [`../result-format.md`](../result-format.md) |
| The Stage-1 arc | [`../stage1-report.md`](../stage1-report.md) · **Next:** [Phase 2](../phase2/README.md) |
