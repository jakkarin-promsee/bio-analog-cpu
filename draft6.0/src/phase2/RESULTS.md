# Phase 2 — Results ledger

> The **synthesis surface** for the whole phase — one row per rung, accumulated as they land. Six folders is a
> pile of runs; *research is the arc*, and the arc lives **here**. Reporting format:
> [`result-format.md`](result-format.md). Plan: [`README.md`](README.md). Phase-1 precedent:
> [`../phase1/RESULTS.md`](../phase1/RESULTS.md).
>
> **Fill a row the moment a rung's *decision* is made.** The scalars for Phase 2 are the **depth-slope** (probe
> change/layer; +ve = depth helps) + **final-layer probe median ± IQR**, plus the rung-specific headline
> (DECIDE gap, BWT, …). Every comparison obeys the n=5 "disjoint-IQR + ≥4/5 seeds" rule.

| Exp | Commit | Headline scalar (depth-slope · final probe ± IQR · rung headline) | Reference (GD-hidden envelope / chance) | Knob / verdict it set | Decision it fed | Card |
| --- | --- | --- | --- | --- | --- | --- |
| **P2.0** synth (dial) | `7766ace` | **5-seed**: wall slope **−0.0005 (FLAT)**, final probe **0.697**; erank **44→7.6** (collapse) yet probe holds (2-class clusters survive low rank); dead 0→0.09. **DECIDE inconclusive here** (selectivity **+0.006** [−0.002,0.019], RAW **0.961 ≈ GD 0.955**). _(P2.1 preview, not plotted in P2.0: layernorm+linear+contrast candidate ≈ wall, +0.0033/0.716 — synth has no wall to separate them.)_ | GD ceiling **0.955**, envelope gap **+0.234**; chance 0.50 | synth has **no real wall** (flat) → it is the F6⁺ dial + code sanity, **not** the headline. The **selectivity control fired**: RAW≈GD + SCFF (0.918) ≈ RAND (0.912) ⇒ the max-power probe solves from *raw*, so lost/entangled is a **probe artifact** on synth | **wall decline · DECIDE verdict · width×depth gap (+0.000) ALL DEFER to CIFAR-flat** | [P2.0](exp0/experiment-0.md) |
| **P2.0** cifar (headline) | `7766ace` | **5-seed**: wall slope **−0.018** [−0.019,−0.015] (DECLINES, all 5 −ve), probe 0.23→**0.117**; dead **0→0.47**, erank **39→11**. **DECIDE = LOST**: SCFF **0.294** ≈ RAND **0.298** ⇒ **selectivity −0.005** [−0.008,−0.005]; RAW 0.389 (lost **0.104** vs raw); gap-vs-ceiling **+0.067**; width×depth **+0.003** | GD-hidden envelope **0.35** (gap **+0.187**); chance **0.10** | **wall reproduced** (the curve P2.1 must bend up) + **LOST** (not entangled) + width×depth +0.003 | **→ P2.1 (norm×goodness grid)**, start at **layernorm+linear** (DeeperForward); **P2.4 interface deprioritized** (SCFF≈RAND ⇒ nothing to re-read) | [P2.0](exp0/experiment-0.md) |

_Pre-run smoke (2026-06-21, not a ledger row): the deactivation mechanism reproduced — wall (squared goodness)
dead-units **0→0.39** over 8 layers; DeeperForward cell (layer-norm + linear goodness) **~0.05** and a flatter,
higher probe curve. Validated the [grid-widening decision](exp0/experiment-0.md) before P2.1._
