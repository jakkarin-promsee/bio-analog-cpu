# Phase 1 — what we discovered (the synthesis)

> The behavioral-simulation phase of draft 6.0, run 2026-06-20 (exp0 → exp4). This is the *story of the
> findings* — what we asked, what the sims said (often overruling the theory), and the honest verdict.
> Per-experiment detail lives in each `expN/experiment-N.md`; the scalar ledger is [`RESULTS.md`](RESULTS.md);
> the reporting standard is [`result-format.md`](result-format.md). Stack: numpy-only (SCFF's update is a
> closed-form *local* gradient), sklearn probes, matplotlib; tasks = 2-D checkerboard, `load_digits` (64-D),
> MNIST (784-D); 5 seeds `[42,137,271,314,1729]`, median + IQR.

---

## The one-paragraph verdict

**Draft 6.0 is a cheap, forgetting-robust, *continual* learner — not a deep static-accuracy competitor, and
that's the point.** On static tasks SCFF is a weak feature learner and GD wins raw accuracy; depth (whether a
monolithic SCFF stack or a boosting chain) gives diminishing returns. But a single SCFF+GD block already
**generalizes better than backprop** (smaller memorization gap) at **~10% of the backward cost**, and in the
**continual regime the architecture wins decisively**: where online backprop catastrophically forgets
(→ chance), the SCFF block **does not forget** (its unsupervised features stay class-separable for all
classes), so a cheap **sleep**-consolidated readout — replaying a small prototype **LUT** — restores
near-ceiling accuracy. That is exactly the regime the substrate was built for, and the bridge to the
project's north star (the recurrent lifelong brain).

---

## The arc, experiment by experiment

### exp0 — does SCFF separate at all? (the gate)
**Result.** Gate PASS. Full SCFF, label-free + local, builds class-separable features; full-GD ceiling on the
2-D checkerboard = **0.943**. **But** across 5 seeds SCFF only *ties* a random projection in low-D (0.796 vs
0.817, within noise) — it beats random only on higher-D input (64-D digits: 0.841 vs 0.780).
**What it set.** goodness = **sum** `‖h‖²`; θ=2.0; two-sided ≈ pure-contrast (keep two-sided); input-norm on.

### exp1 — one block vs pure GD
**Result.** A single block (SCFF → GD readout) vs matched pure-GD. **Memorization gap is the headline:** MNIST
block **+0.027** vs GD **+0.062** (disjoint IQR, 5/5 seeds — real). Block held-out 0.850 vs GD 0.938 (digits
0.927 vs 0.968). Block's serial backprop = **10%** (MNIST) of GD's; the rest is SCFF local, forward-only,
credit-distance 0. **1b:** the block closes on GD as size grows; default size **H=64**.
**What it set.** Tap **ALL** SCFF layers (S3's "last n" was wrong — see below). GD ceilings: MNIST 0.938,
digits 0.968.

### exp2 — inside the block (ratio + plasticity)
**Result.** **2a (ratio):** accuracy *declines monotonically* with SCFF fraction (digits 0.965→0.920, MNIST
0.943→0.837) — **no free-lunch sweet spot**; on MNIST the backward saving concentrates in the *first* layer
(25% SCFF saves 65% of backprop for −3.7 pt). **2c (plasticity):** slow read-layers marginally best (ρ≈0.3),
lower drift — but drift is *mild* in finite data, and plasticity does **not** fix depth-degradation.
**What it set.** Keep SCFF **shallow** (depth degrades it); N2's knob = slow read-layers (ρ≈0.1–0.3).

### exp3 — residual-boosting chain
**Result.** The chain of shallow GD-corrected blocks **beats a single block** (digits 0.92→**0.950**,
approaching GD 0.970; MNIST barely, 0.858 vs single 0.850) with a small gap — **but error saturates after ~2
blocks** (no exponential boosting decay). The ε-diagnostic resolved the mechanism: **boosting wants *diverse*
weak learners, not preserved-identical features** — full residual ε=1 (per-block features individually
degrade) gives the best ensemble; preserving features (small ε) collapses the diversity and *lowers* the
final.
**What it set.** N3 boosting confirmed; **full residual ε=1**; Ch9 linear delta off (not needed).

### exp4 — the continual regime (gate + sleep) — *the win*
**Result.** Class-incremental stream. **Online learning ROTS** (digits 0.18 / MNIST 0.19; no-sleep readout
0.086) — catastrophic forgetting. **Sleep recovers to the static ceiling** (digits **0.935**, MNIST
**0.865**); the **LUT hippocampus** replays nearly as well (0.898 / 0.863) at a fraction of the store. **And
SCFF itself does not forget** — its all-class probe stays flat (0.90 / 0.75) the whole way.
**What it set.** Sleep (3.1) + LUT (3.2) confirmed; SCFF is forgetting-robust; **continual is the
architecture's validated home.**

---

## The cross-cutting discoveries (the surprises that reshaped the plan)

These are the things we *did not* know going in — each was forced by a sim, not argued from theory:

1. **Goodness must be the SUM `‖h‖²`, not the paper's mean `/M`.** Under unit-norm inputs the mean starves
   deeper layers to ~`1/M`, so θ=2.0 is unreachable under plain online SGD (the FF references only reach it
   with Adam × 1000 epochs). The sum is ~1 at init, width-independent, substrate-faithful. *(exp0; corrected
   in `ideas1.md` + `SCFF.detail.md`.)*
2. **SCFF clusters by *density*, not by *class*.** It makes real samples loud and blends quiet → it learns
   *where the data is*. This recovers classes only when classes *are* density clusters; the 2-arm **spiral**
   (equal-density interleaved arms) defeats SCFF-alone at every config. The gate task had to be a cluster
   task. *(exp0.)*
3. **SCFF is a weak low-D learner.** On 2-D/3-D Gaussian clusters a random projection already matches it
   (Johnson–Lindenstrauss); its value needs high-D input where random features fail. *(exp0.)*
4. **SCFF features DEGRADE with depth**, and the readout must tap **all** layers (S3's "last n" reads the
   *worst* ones). Each SCFF layer re-optimizes goodness/density and sheds class-relevant directions.
   *(exp1/2/3.)*
5. **No "80% deep SCFF nearly free."** Accuracy falls with SCFF fraction; cost savings concentrate in the
   expensive *input* layer (~25%), not the bulk. The 80/20 framing is re-read as *shallow SCFF + GD
   correction.* *(exp2.)*
6. **Boosting wants diversity, not preservation.** The residual stream's job is to make per-block features
   *diverge* (diverse weak learners), not to keep a pristine representation. *(exp3.)*
7. **THE win — SCFF is forgetting-robust, and that makes cheap continual learning work.** Because it clusters
   unsupervised, new classes *add* clusters instead of overwriting old ones; only the small readout needs a
   sleep-consolidation over a cheap prototype store. *(exp4.)*

---

## Spec corrections made (Phase 1 → the decision record)

- **goodness = sum `‖h‖²`** (not mean) — `ideas1.md` consolidated-math note + `research/survey/SCFF.detail.md` note.
- **tap ALL SCFF layers** — supersedes S3's "GD reads the last n layers."
- **`normalize_input = True`** (unit-norm input at layer 1 too) — ratified; trades the magnitude head-start
  for a uniform goodness scale and zero L1 unit-death.
- **80/20 reframed** — SCFF should be *shallow* (the cheap input front), not the deep bulk; depth comes from
  *boosted blocks*, not deep SCFF.
- **N3 residual boosting** confirmed as the chaining mechanism, **full residual ε=1**; the **Ch9 linear
  inter-block delta stays off** (not needed). **N2** knob = **slow read-layers (ρ≈0.1–0.3)**.

---

## What's validated vs not

| | status |
| --- | --- |
| SCFF = cheap, label-free, local, forward-only feature learner | ✅ |
| One block generalizes better than backprop (smaller gap) at ~10% backward cost | ✅ |
| **SCFF is forgetting-robust → cheap continual learning via sleep + LUT** | ✅ **(the win)** |
| Boosting chain > single block, approaches GD | ✅ (modest) |
| "Deep 80%-SCFF brain matches GD" on static tasks | ❌ (weak, shallow-is-better, saturates) |
| SCFF beats GD on raw static accuracy | ❌ (GD wins; block is cheaper + generalizes, but lags ceiling) |

---

## Open knobs (set) and remaining follow-ups

**Set by Phase 1:** goodness=sum · θ=2.0 · input-norm · all-layer tap · two-sided loss · full residual ε=1 ·
slow read-layers (ρ≈0.3) · default H=64.

**Remaining (not blockers):**
- **Ch7 threshold gate** — when to *pay* for GD (loss-slope/plateau gating). The one Exp-4 piece unbuilt.
- **Sleep-cadence / LUT-vigilance sweep** — how *little* maintenance suffices; on high-D the cosine
  vigilance needs per-dataset tuning to compress (MNIST kept 84% at vig 0.90).
- **GD-coshaping / DF-O** — the other untested degradation fix (Ch6 optional).
- **Analog / PVT realism** — the deferred substrate layer (out of Phase-1 scope by design).

---

## The bridge to the north star

Phase 1's deepest lesson is *where* this architecture wins: not static accuracy (GD's game) but **lifelong,
non-stationary, online** learning — cheap forward-only updates, a representation that doesn't forget, and a
sleep that consolidates for pennies. That is precisely the substrate of the project's real long-term target
(the recurrent prefrontal↔hippocampus thinking loop). Phase 1 turned that ambition from a hope into a
measured property: **the cheap brain doesn't forget, and sleep keeps it whole.**

---

## Reproducibility

Every run writes `figs_*/manifest.json` (git commit + resolved config + medians + versions) and
`figs_*/arrays.npz` (the raw logged arrays). Figures regenerate from the arrays with **no retraining**:
`python exp0/plot.py <run-dir>` (and `exp1/plot_exp1.py`). Re-running any `expN/run_*.py` is deterministic
(seeded) and reproduces the cards exactly (verified 2026-06-20). Entry points:

| exp | run | figures |
| --- | --- | --- |
| 0 | `exp0/run_exp0.py` (+ `scff_gate.py` gate, 5 diagnostics) | F1/F3/F4/F5/INV via `plot.py` |
| 1 | `exp1/run_exp1.py {digits,mnist}`, `run_exp1b.py`, `tap_diag.py` | F1/F3/F7/INV/F6 via `plot_exp1.py` |
| 2 | `exp2/run_exp2a.py`, `run_exp2c.py` | F9 trade, plasticity |
| 3 | `exp3/run_exp3.py`, `res_diag.py` | F8 boosting, pivot |
| 4 | `exp4/run_exp4.py` | rot-vs-sleep + SCFF-probe |
