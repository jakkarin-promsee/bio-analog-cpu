# Phase 1 · Axis 1 · Experiment 3 — Rung-1: what the ceiling does to a Ganglion

> **Purpose:** not a number — *understand* how the weight ceiling (the physical-saturation rail, §6.6 / H10)
> reshapes a Ganglion. The ceiling is a **per-weight clip** (it only touches weights with |w| > W_max). We
> show its effect directly on the output surface — raw (amplitude) and normalized (shape).

**Question.** How does a weight cap change a Ganglion's output? Does it hit long-range (high-gain) and
short-range (low-gain) output differently? Does the shape survive?

**Setup.**
- Two Ganglions, the *same random pattern* (seed 42) at two gains: **low-gain** (U±0.5) and **high-gain**
  (U±2.0 = the same weights ×4). Clip to |w| ≤ W_max, W_max ∈ {∞, 0.4, 0.2, 0.1} (a static stored-weight cap —
  no frozen-kit change). 121² grid; per W_max log # weights clipped + out0 range width.
- Figure per Ganglion (`ceiling_grid`): top row = raw surfaces on a **shared** color scale (the amplitude
  crush); bottom row = each **normalized** (does the shape survive). Script: `exp3_rung1_ceiling_effect.py`.

**Result.**

| W_max | low-gain: clipped / width | high-gain: clipped / width |
| --- | --- | --- |
| ∞ | 0/29 · 0.033 | 0/29 · 2.127 |
| 0.4 | 8/29 · 0.029 | 25/29 · 0.208 |
| 0.2 | 19/29 · 0.017 | 27/29 · 0.023 |
| 0.1 | 25/29 · 0.003 | 28/29 · 0.003 |

Figures: `low_gain.png`, `high_gain.png` (+ `gallery.md`).

**Read.**
- **The ceiling is a per-weight clip → a selective compressor.** At W_max=0.4 it touches only the 8 (of 29)
  weights above 0.4 in the low-gain Ganglion, so output barely moves (0.033 → 0.029). The high-gain Ganglion
  has 25/29 weights above 0.4, so it is crushed **10×** (2.127 → 0.208). The cap squeezes the strong, spares
  the weak — the **anti-winner-take-all** role (§6.6 / H10), visible in the raw rows.
- **Long-range output is hit hard; short-range barely.** The high-gain surface collapses toward flat already
  at 0.4; the low-gain one only collapses once the cap drops below its own weights.
- **A tight cap erases gain differences.** At W_max=0.1 both → width 0.003 — clipped into the same ±0.1 box,
  they become the *same* near-flat surface. The rail dominates.
- **Shape SHIFTS as it clips (the nuance).** The normalized (bottom) rows are not identical across W_max:
  truncating only the big weights changes the weight *ratios* (−b/w), so region boundaries move → the shape
  drifts. This is the **chip-true** behavior (the rail clips; it does not re-optimize). It differs from "best
  *reachable* shape is cap-invariant" (you could re-optimize the unclipped weights to recover shape) — the
  chip's reality sits between, since learning adapts the unclipped weights around the railed ones.

**Decision.**
- Rung-1, understood: **a weight ceiling is a selective gain compressor** — it crushes high-gain (long-range)
  output, spares low-gain, equalizes everything when tight, and *shifts* shape as it clips ratios. That IS the
  physical-saturation / winner-take-all defense, seen directly (not inferred from a residual).
- Replaces the earlier messy three (a shallow metric sweep + a gain-confounded residual fit + an abstract
  scale-free sweep). **Lesson kept:** to understand a mechanism, *show its effect on a concrete Ganglion*,
  don't aggregate it into a number.
- Next (rung-2, saturation): the *soft* `1−e^(−·)` rail vs this hard clip — does soft saturation compress more
  gently / preserve shape better?
