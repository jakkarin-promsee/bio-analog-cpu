# Phase 1 · Axis 1 · Experiment 1 — Rung-0a: the small-init prior (y = aW + b, no limits)

> **Scope: this is the _prior_** — what a freshly-initialized Ganglion makes under random small init
> (its inductive bias). The _representational limit_ (best-fit to target surfaces, free weights) is
> **[exp-2](experiment-2.md) (rung-0b reachability)** — that is the interpretable "what can the atom
> represent" measure. A single random draw is luck; the ensemble shows the starting distribution.

**Question.** What is one 2-3-3-2 Ganglion's *base* output surface — the family of shapes it makes under
ideal floats (no capacitor ceiling, no charge saturation), before any Axis-1 limit or Axis-2 activation
change? Does the real forward (as built) produce piecewise-linear regions, confirming the op math + the
region-multiplexer reading at the bottom of the ladder?

**Setup.**
- Probe: `harness.GanglionProbe` — the REAL forward (Brainstem → ControlUnit → GanglionALU), not a numpy
  clone. Library unchanged: `alu.py` = ReLU@L2, linear@L3, L4 linear, no limits → this is rung-0 ideal at
  the **L2-only** activation point (so no frozen-kit change was needed; the L2+L3 rung-0 = Axis-2 placement).
- Sweep: 121×121 grid on [−1, 1]²; both output channels.
- Ensemble: the §20.2 seeds [42, 137, 271, 314, 1729], inits ~ U(−0.5, 0.5) over 29 Scaps; plus one
  hand-set degenerate extreme — all-zero weights.
- Metrics: output range, planar residual (curvature, normalized), region count (gradient-cluster heuristic).
- Script: `exp1_rung0_ideal.py`  ·  `python -m src.experiment.phase1.axis1_weightcap.exp1_rung0_ideal`  ·  figures: `figures/exp1/`.

**Result.**

| case | channel | range | curvature | regions |
| --- | --- | --- | --- | --- |
| seed42 | out0 | [−0.402, −0.369] | 0.265 | 7 |
| seed42 | out1 | [+0.288, +0.445] | 0.097 | 6 |
| seed137 | out0 | [−0.829, −0.230] | 0.114 | 4 |
| seed137 | out1 | [−0.132, +0.254] | 0.067 | 5 |
| seed271 | out0 | [+0.385, +0.407] | 0.000 | 1 |
| seed271 | out1 | [−0.408, −0.244] | 0.000 | 1 |
| seed314 | out0 | [−0.198, −0.067] | 0.296 | 6 |
| seed314 | out1 | [+0.214, +0.384] | 0.445 | 6 |
| seed1729 | out0 | [+0.291, +0.377] | 0.077 | 2 |
| seed1729 | out1 | [+0.451, +0.558] | 0.654 | 3 |
| zeros | out0 | [0, 0] | 0.000 | 1 |
| zeros | out1 | [0, 0] | 0.000 | 1 |

Figures: `figures/exp1/seed*.png`, `zeros.png`. seed42 shows visible ReLU folds (a kink band near x2≈0.65 +
a diagonal crease); seed271 is two clean planes (no folds).

**Read.**
- **Op math confirmed.** `zeros` → flat-zero, 1 region, 0 curvature; the as-built forward wiring is correct
  (this folds in the old "operator sanity"). Eyes and numbers agree across every case.
- **Region count spans 1–7, and 7 is the theoretical ceiling** for three L2 ReLU hyperplanes in 2-D
  (1 + 3 + 3 = 7). seed42 hits it. So at the bottom of the ladder the Ganglion already carves up to the max
  its 3 active L2 cuts allow — the region-multiplexer thesis holds *with eyes*. L3 is linear in the current
  code, so this is the **L2-only** ceiling; whether L3-ReLU pushes past 7 is Axis 2.
- **Some random inits are degenerate (purely linear).** seed271 → curvature exactly 0, 1 region, both
  channels: all three L2 ReLUs sit in their always-on (linear) regime over [−1,1]², so the Ganglion collapses
  to an affine map (a plane). Under small uniform init a real fraction of draws don't engage the nonlinearity
  in-domain. (Quantifying that fraction needs the per-neuron activation census — deferred; it needs a small
  ALU-internal a2/a3 exposure.)
- **Output range is narrow and often sign-locked.** Channel widths run from ~0.02 (seed271 out0) to ~0.6
  (seed137 out0); several channels never cross zero. Under U(−0.5, 0.5) init the atom's raw output dynamic
  range is sub-unity — consistent with the "low prediction values are the cap range" note. This is the
  rung-0 usable-range baseline, *before* any ceiling (rung 1).
- **Curvature spans 0 → 0.65:** the shape family runs from flat plane (seed271) to strongly folded
  (seed1729 out1). The two channels of one Ganglion can differ a lot (they share L2/L3 but read out
  differently at L3→L4) — the output-rank metric (deep layer) will quantify how independent.

**Decision.**
- The harness / metrics / plots pattern is established and works end-to-end → reuse unchanged for the rest of
  Axis 1. **Next: rung-1 (capacitor ceiling).** That one needs the first frozen-kit change — a *forward*
  ceiling clamp toggle (a `simulator-code` task), defaulting to off.
- Two kit additions to queue (not blocking): (a) a non-invasive ALU exposure of `a2`/`a3` so the
  **neuron-activation census** can explain the degenerate draws; (b) a **Jacobian-field** plot to show
  regions directly and harden the region-count heuristic (it's resolution/rounding-bounded — fine here, but
  worth sharpening before we lean on the exact number).
- Open thread for Phase 2 (note, don't act): the narrow sub-unity output range — does it bottleneck
  Ganglion-to-Ganglion composition?
