# Phase 1 · Axis 1 · Experiment 2 — Rung-0b reachability (the representational limit)

> **Scope: this is the _limit_** — the best the atom CAN represent, found by a *generic* optimizer with
> free/unbounded weights, **NOT** the chip's attribution rule (that's Phase 2 / H1). The complementary *prior*
> (random fresh init) is [exp-1](experiment-1.md). Why generic-fit: it isolates "what can the *hardware*
> represent" from "can *attribution* learn it" — so a bad residual here is an architecture limit, unambiguously.

**Question.** What is the representational *limit* of one 2-3-3-2 Ganglion (out0) — which synthetic target
surfaces can it match, and where is the wall? (And: does the random-prior "luck" vanish once we optimize?)

**Setup.**
- Fit `out0` to each normalized target over a 21×21 grid on [−1,1]², free weights, **12 random restarts**
  (ReLU fits are nonconvex → best-of-N = a *lower bound* on capacity); `scipy.least_squares` (trf).
- Fit runs on the numpy **mirror** (verified == the real `GanglionALU`, max abs err 0.0); each best-fit
  weight set is re-checked on the **real probe** at full 121×121 resolution — `real-resid` is what we report.
- Targets: plane, parabola `x1²`, paraboloid `0.1(x1+x2)²`, saddle `x1·x2`, gaussian bump, xor-checker
  `sign(x1)·sign(x2)`. Metric: norm-residual = RMSE / std(target) (0 = perfect, ~1 = no better than the mean).
- Script: `exp2_rung0b_reachability.py`. Figures = **2×2 in real output units** (top: target | best-fit
  heatmaps; bottom: target | best-fit **3-D surfaces** — the real shape): `figures/exp2/` (+ `gallery.md`).

**Result.**

| target | fit-resid (mirror 21²) | real-resid (ALU 121²) | read |
| --- | --- | --- | --- |
| plane | 0.000 | 0.039 | exact (the 0.039 is fit-grid resolution, not a capacity limit) |
| parabola `x1²` | 0.081 | 0.134 | good — PWL approximates a 1-D parabola well |
| paraboloid `0.1(x1+x2)²` | 0.103 | 0.137 | good — the diagonal valley is captured (cf. the ~20× regression result) |
| saddle `x1·x2` | 0.194 | 0.202 | partial — the multiplicative sign-flip is hard for one cut set |
| gaussian bump | 0.234 | 0.243 | partial — builds the hump as PWL facets (a ReLU diamond), not smooth |
| xor `sign·sign` | 0.454 | 0.502 | **the wall** — one boundary only; can't carve the 4-quadrant checkerboard |

Figures: `figures/exp2/{target}.png` — 2×2 in real units (heatmaps on top, **3-D surfaces** below) +
`gallery.md`. The 3-D row is the honest shape: `plane` renders as a flat plane, `paraboloid` a bowl, `xor` a
**step-checkerboard** the atom answers with a smooth saddle (can't make the steps → the wall).

> **Viz lesson (recorded).** 1-D collapses distort *shape*: a uniform-grid plane has a triangular value
> distribution, so **sorting by target turns a plane into an S-curve** — the sorted overlay read fit fine but
> lied about shape. A 2-in→1-out function's shape is inherently 2-D; use the heatmap / 3-D surface, not a
> sorted 1-D profile. (1:1 scatter is faithful for *fit* but not for *shape*.)

**Read.**
- **A clean capacity envelope**, monotone and interpretable: `plane(~0) < parabola ≈ paraboloid(~0.13)
  < saddle(~0.20) < gaussian(~0.24) < xor(~0.50)`. This is the "real limit" — luck-free, because the
  optimizer (not a random draw) found the best each target allows.
- **The wall is xor**, for a structural reason visible in the figure: the checkerboard needs *two independent*
  boundaries; one 2-3-3-2 (L2-only ReLU) lands a single diagonal split and smears the rest. The atom's
  headline limit — and it matches "XOR is beyond a single Ganglion."
- **Quadratics easy, localization medium.** parabola/paraboloid fit well (PWL handles one convex bowl); the
  gaussian bump is only partially reachable — the atom uses **3 concurrent L2 lines through the center → 6
  wedges** (vs 7 for general-position lines, exp-1's max) to approximate the radial hump; the L2 cuts read
  straight off the heatmap.
- **mirror vs real:** the 21² fit residual is a touch optimistic vs the full-grid real-ALU residual (plane
  0.000 → 0.039) — a coarse fit grid can miss a ReLU knee the finer grid resolves. The real-ALU 121² number
  is the honest one; mirror == ALU exactly (err 0.0), so the gap is fit-grid resolution, not a clone mismatch.

**Decision.**
- Reachability is now the **Axis-1 through-line**: rungs 1–2 (ceiling, saturation) re-report this residual
  table, so we read **how each physical limit erodes the envelope** (does xor get worse? does the gaussian
  degrade first?) — far more legible than eyeballing random surfaces.
- exp-1 stays as the complementary **prior** (init-sensitivity, dead-draw fraction, starting range).
- Honest caveats to carry: residuals are a *lower bound* (best-of-12 restarts); for a sharp target (xor) the
  fit grid should match/exceed the read grid before quoting exact numbers downstream — bump restarts / fit-grid
  for the wall cases if we lean on them.
- **Next: rung-1 (capacitor ceiling)** — the first frozen-kit toggle — measured *both* ways (prior shift +
  reachability-residual change).
