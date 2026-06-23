# Phase 1 — Ganglion Personality (summary)

> **Plan / why:** `../../../draft5.1-2.verify.md` → Phase 1. **This file is the concise phase summary**; the
> *full detail* (ladder, experiment tables, figures, findings) lives in each **axis folder's README**.

**Goal (one line):** map the expressive personality of one 2-3-3-2 Ganglion — the family of surfaces it can
make and its limits — by sweeping inputs/weights, plotting the surface, and reading a **metric fingerprint**
off each, across three axes.

## The three axes (each its own folder + README)

| Axis | Folder | What it varies | Status |
| --- | --- | --- | --- |
| 1 — weight-cap limit | [`axis1_weightcap/`](axis1_weightcap/README.md) | ideal → ceiling → soft-saturation | exp-1–3 done (rung-0, rung-1) |
| 2 — op-amp activation | [`axis2_activation/`](axis2_activation/README.md) | placement (L2 / L2+L3) × type (lin / ReLU / hard-tanh / tanh) | not started |
| 3 — residual bypass | [`axis3_residual/`](axis3_residual/README.md) | §7.7 L1→L4 on/off (the "×2") | not started |

## Shared infra (phase-level, reused by every axis)

- `harness.py` — build + drive the REAL single-Ganglion forward (the probe; config hooks for all axes).
- `metrics.py` — the metric library (range, curvature, region count; census / rank / PCA / reachability later).
- `plots.py` — plotting helpers (heatmaps now; slices / Jacobian field / contour later).

Scripts import these via `from src.experiment.phase1 import harness, metrics, plots`. The **structural probes**
(bias-as-cut-placement, neuron census, output rank) and **deep metrics** (PCA dimensionality, target
reachability) are cross-cutting — run within whichever axis exposes them, aggregated in the final summary.

## Status / headline (concise — detail in the axis READMEs)

- **Axis 1 · exp-1 (rung-0a prior):** as-built forward correct; region count **1–7** (max = the 3-line ceiling
  → the region-multiplexer thesis holds with eyes); some inits degenerate to a plane; range narrow +
  sign-locked under small init.
- **Axis 1 · exp-2 (rung-0b limit / reachability):** a clean capacity envelope — `plane ~0 < quadratics ~0.13
  < saddle/gaussian ~0.2 <` **xor ~0.50 (the wall)**. Best-fit by a generic optimizer (free weights), not the
  chip's learning — so this is the *representational* limit, luck-free.
- **Axis 1 · rung-1 ceiling (exp-3):** the cap is a **selective gain compressor** — it crushes high-gain
  (long-range) output 10× while sparing low-gain, and equalizes everything when tight. The
  anti-winner-take-all rail (§6.6 / H10), seen directly; shape shifts as it clips weight ratios.

## What the ideal Ganglion is (rung-0 synthesis)

One 2-3-3-2 Ganglion is a **piecewise-linear region carver**: L2's 3 ReLU lines cut the 2-D input into linear
regions (≤ 7, or 6 if concurrent — the atom's "resolution"); L3/L4 read out a linear value per region. The
figures show *the same carver* measured two ways — a random **floor** (0a) and an optimized **ceiling** (0b).

**0a · the carver exists, but starts random.** A fresh Ganglion already cuts the plane into regions — by luck,
not design:

![rung-0a · seed42](axis1_weightcap/figures/exp1/seed42.png)

*exp-1, seed42 — 7 regions (the structural max for 3 lines); the ReLU creases are visible. The carver works,
but with random weights, not learned ones.*

**0a · …and often starts broken.** Sometimes all 3 cuts fall outside the domain and the regions merge into one:

![rung-0a · seed271](axis1_weightcap/figures/exp1/seed271.png)

*exp-1, seed271 — curvature exactly 0, a flat plane. A real fraction of random inits are this degenerate.
**This is the floor.***

**0b · how good the carve can get.** Optimize the cuts (a generic fit, free weights — *not* the chip's learning)
and the carver climbs an envelope: `plane ~0 → quadratics ~0.13 → gaussian ~0.24 → xor ~0.50`. The two ends and
the real carve in the middle:

![rung-0b · plane](axis1_weightcap/figures/exp2/plane.png)

*exp-2, plane (~0) — trivial; a linear target needs no carve. Both the heatmap and the 3-D surface are a flat
tilted plane.*

![rung-0b · parabola](axis1_weightcap/figures/exp2/parabola.png)

*exp-2, parabola x1² (~0.13) — a parabolic trough (curved along x1, flat along x2). The carver fits it with a
few parallel cuts across x1, each region a linear segment of the U — the piecewise-linear valley is clear in
the 3-D surface. One bowl-worth of folds is easy.*

![rung-0b · gaussian](axis1_weightcap/figures/exp2/gaussian.png)

*exp-2, gaussian (~0.24) — the region-multiplexer in full view: 3 concurrent lines → 6 wedges approximate the
round dome (clearest in the 3-D surface). The carver doing real work.*

**0b · the wall:**

![rung-0b · xor](axis1_weightcap/figures/exp2/xor.png)

*exp-2, xor (~0.50) — the checkerboard needs two independent boundaries; one carver throws a single fold, so it
answers the steps with a smooth saddle and can't separate the quadrants. **The hard limit of one Ganglion.***

**The relation.** 0a (random floor) and 0b (optimized ceiling) are the **two ends of one band**: every real
Ganglion lives between "degenerate" and "best carve," and the **gap between them is what learning must cross**.
Whether the attribution rule can move a Ganglion from its random 0a prior up to the 0b ceiling is exactly
**H1 (Phase 2)**.

**Rung-1 (the weight ceiling) — a selective gain compressor.** The cap clips per-weight (only weights above
W_max), so its bite depends on the Ganglion's gain: it crushes a high-gain (long-range) Ganglion **10×**
(range 2.13 → 0.21 at W_max=0.4) while barely touching a low-gain one (0.033 → 0.029); a tight cap (0.1)
equalizes everything (both → 0.003). That *is* the physical-saturation / anti-winner-take-all rail (§6.6 /
H10) — squeeze the strong, spare the weak. Shape **shifts** as it clips (truncating big weights changes the
−b/w ratios → boundaries move). So the ceiling is a gain/amplitude control, not a shape expander. (Detail:
axis1 exp-3 — surfaces ± cap, raw vs normalized.)

This is still the *ideal-floats* baseline; rung-2 (saturation) and Axes 2–3 (activation, residual) reshape it
further; the full Phase-1 personality is the gate writeup. (Figures: exp-2
[`gallery.md`](axis1_weightcap/figures/exp2/gallery.md) · exp-3
[`gallery.md`](axis1_weightcap/figures/exp3/gallery.md).)

## Read order

1. `../../../draft5.1-2.verify.md` → Phase 1 — the intent (the axes, the metric philosophy, the gate).
2. This summary — the axis map + cross-axis status.
3. The axis folder README for the axis you're working — full detail + experiment table.
4. `axisN_*/experiment-{k}.md` — the per-experiment logs.

---

### Skeleton for each `experiment-{k}.md` (shared convention)

```
# Phase 1 · {Axis} · Experiment {k} — {short title}

**Question.**  What are we trying to see/measure?
**Setup.**     Config (axis rung / activation / residual), seed set, the exact script + command.
**Result.**    The figures (linked) + the metric row.
**Read.**      What the picture + numbers say.
**Decision.**  What this changes; what to run next.
```
