# Phase 1 · Axis 1 — Weight-capacitor limit (the full record)

> **Plan / why:** `../../../../draft5.1-2.verify.md` → Phase 1, Axis 1.  **Phase summary:** `../README.md`.
> This README is the *full detail* for the weight-cap axis — its ladder, the two reads, code prereq,
> experiment table, figures, and findings.

**The axis.** How the weight capacitor's ceiling distorts the surface — climbed one rung at a time:

| Rung | What's on | What we look for |
| --- | --- | --- |
| **0 — ideal** | `y = W·a + b`, plain floats; no ceiling, no saturation | the base shape + the base limit |
| **1 — ceiling** | `w, b` clamped to ±W_max | a **selective gain compressor** — crushes high-gain output, spares low-gain; shape shifts as ratios clip |
| **2 — soft saturation** | `w` through a concave `1 − e^(−·)` map to the rail (forward) | soft rail vs hard clip |

**Two reads per rung.** Each rung is read two ways — **(a) the prior:** sweep a random weight ensemble, see
what a fresh Ganglion *makes* (inductive bias, init-sensitivity); **(b) the limit / reachability:** best-fit
`out0` to synthetic targets with a *generic* optimizer (free weights, **not** the chip's attribution rule —
that is Phase 2 / H1), residual = what the atom *can* represent. **Reachability is the through-line:** rungs
1–2 re-report the same residual table, so we read how each physical limit erodes the capacity envelope.

Rung 2 is the static *footprint* of the cap's `dV/dt ∝ (V_rail − V_cap)` charging — the live charging dynamic
is a Phase-2 thing. The in-code `W_RAIL` is in the Scap *update* path, so rungs 1–2 add the footprint as
*forward* toggles. **Activation is held fixed** at the library default (ReLU@L2, linear@L3) — activation is Axis 2.

## Code prereq
- **rung 0:** none — the library forward is already ideal (exp-1, exp-2 are purely additive in `phase1/`).
- **rungs 1–2:** a `simulator-code` task — a forward `|w|,|b| → ±W_max` clamp + a forward soft-saturation map
  in `alu.py`, threaded through the `harness` config, **defaulting to off**.

## Experiments

| # | rung | status | headline |
| --- | --- | --- | --- |
| [experiment-1](experiment-1.md) | 0a — ideal *prior* (random ensemble) | ✅ done | region 1–7 (7 = the 3-line ceiling); degenerate planar draws; narrow sub-unity range |
| [experiment-2](experiment-2.md) | 0b — ideal *limit* (fit-to-targets) | ✅ done | clean envelope: plane ~0 < quadratics ~0.13 < saddle/gaussian ~0.2 < **xor ~0.50 (the wall)** |
| [experiment-3](experiment-3.md) | 1 — ceiling (what it *does*) | ✅ done | a **selective gain compressor**: crushes high-gain (long-range) 10× at W_max=0.4, spares low-gain; shape shifts as it clips ratios |
| experiment-4 | 2 — saturation | planned | the soft `1−e^(−·)` rail vs the hard clip — does soft saturation compress more gently / preserve shape? |

Run: `python -m src.experiment.phase1.axis1_weightcap.exp{N}_*`. Figures + a `gallery.md` per experiment in `figures/exp{N}/`.

## Findings (this axis)
- **rung-0a prior (exp-1):** the as-built forward is correct (zeros → flat-zero). Region count **1–7**, max =
  the theoretical **7** for three L2 ReLU lines in 2-D. Some inits degenerate to a plane (all L2 ReLUs
  always-on). Output range narrow + often sign-locked under U(−0.5, 0.5). Curvature 0 → 0.65.
- **rung-0b limit (exp-2):** a clean, monotone capacity envelope — `plane(~0) < parabola ≈ paraboloid(~0.13)
  < saddle(~0.20) < gaussian(~0.24) < xor(~0.50)`. The **wall is xor**: one Ganglion throws a single boundary
  and can't carve the 4-quadrant checkerboard (`figures/exp2/xor.png`). Quadratics easy; smooth localization
  (gaussian) only partial (PWL facets). Residuals are a lower bound (best-of-12 restarts); real-ALU 121²
  numbers reported (mirror == ALU, err 0.0).
- **rung-1 ceiling (exp-3):** the cap is a **selective gain compressor** — a per-weight clip that only touches
  weights above W_max. It crushes a high-gain (long-range) Ganglion **10×** at W_max=0.4 (range 2.13 → 0.21)
  while barely touching a low-gain one (0.033 → 0.029); tight enough (0.1) it equalizes everything (both →
  0.003). That's the anti-winner-take-all rail (§6.6 / H10) seen directly. Shape **shifts** as it clips
  (truncating big weights changes the −b/w ratios → boundaries move) — the chip-true view (the rail clips, it
  does not re-optimize).
