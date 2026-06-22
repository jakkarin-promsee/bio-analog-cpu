# Experiment P4.2 — depth headroom (A3) × difficulty

> **Status: ✅ DONE (2026-06-22).** Does Phase-3's depth-composition (P3.2: contrast + coordination w≥2 makes the
> per-layer probe RISE with depth) **generalize across difficulty**, or was it the one config P3.2 tested? P3.2
> warned headroom is fragile, so this was the rung most likely to come back PARTIAL — **it didn't.** Instrument:
> the Phase-3 **per-layer probe slope** (depth-composition is a representation property, invisible to task accuracy
> — the all-tap readout masks it). Task: `make_tierb` headroom family (grid 4, n_active 3, dim 40, 4 classes = 64
> clusters), difficulty dial = overlap `[0.4…1.2]`, L=8. Three curves: **OURS w=2** (adopted) · **OURS w=1**
> (no-coordination control) · **GD-hidden** (ceiling — its slope marks where headroom even exists). 5 seeds. Reuses
> the Phase-3 bench (no new generator). Run: `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_2.py` (625s).

---

## The 6+2 slot read

**1 · Claim.** **A3 — depth-composition GENERALIZES** (decisive, not PARTIAL). OURS w=2 has a **positive per-layer
depth-slope across the *entire* difficulty band** (IQR disjoint from zero at every overlap), where P3.2 tested only
one config — so it is **not a one-config fluke**. Coordination is the robust lever (**w=1 is ~flat/negative
everywhere**). And the deeper finding: **OURS and supervised BP compose depth in *complementary* regimes** — GD
composes best at *easy* (high headroom); **OURS out-composes GD in the *mid/hard* regime where BP's composition
collapses** (crossover ≈ overlap 0.6). Honest texture: w=2 is **not a complete fix at easy+deep** (a mild
inverted-U — the myopic-drift P3.2 fixed with w=4).

**2 · Number + IQR** (median [IQR], n=5; per-layer probe depth-slope, L=8):

| overlap | GD-hidden slope | OURS w=2 slope | OURS w=1 slope | w2_top − GD_top | headroom? |
| --- | --- | --- | --- | --- | --- |
| 0.40 | +0.043 [+0.042,+0.044] | +0.010 [+0.010,+0.010] | −0.010 | **−0.173** (GD wins) | YES |
| 0.60 | +0.016 [+0.015,+0.017] | +0.012 [+0.010,+0.013] | +0.001 | +0.009 | YES |
| 0.80 | +0.004 [+0.004,+0.005] | +0.010 [+0.009,+0.010] | +0.002 | +0.070 | borderline |
| 1.00 | −0.003 [−0.004,−0.002] | +0.008 [+0.006,+0.008] | +0.002 | +0.097 | **flat** |
| 1.20 | −0.004 [−0.004,−0.004] | +0.004 [+0.001,+0.004] | −0.000 | +0.076 | **flat** |

**OURS w=2 slope > 0 everywhere** (IQR-disjoint from 0). **GD slope crosses to negative by overlap 1.0** (loses
headroom). **Top-layer readability crosses at ≈0.6**: GD wins easy (−0.173), OURS wins from 0.6 on (+0.07–0.10).
**w=1 (no coordination) never composes** (≤+0.002). *(All absolute levels low in the hard regime — GD_top 0.30,
OURS_top 0.37, chance 0.25 — so the slope/composition is the claim, not the magnitude.)*

**3 · Figures.** `SLOPE` (headline — GD slope plunges +0.043→−0.004 with difficulty; OURS w2 stays flat-positive
~+0.01; they cross ≈0.9; w1 hugs zero) · `DEPTH` (per-layer profiles: easy 0.4 → GD monotone-rises to 0.74 while
OURS *peaks L4 ~0.69 then drifts to 0.56* = inverted-U; mid 0.8 → GD flat, OURS rises+holds above; hard 1.2 → GD
declines, OURS weakly rises above) · `MAP` (OURS probe over layer×difficulty — bright mid-depth at easy, dim at
hard) · `INV` (GD headroom vanishes by ~0.8; top-layer crossover ≈0.6).

**4 · Mechanism.** The coordination window lets a layer's update account for what the *next* layer needs → depth
composes. **GD composes only where the *supervised task* has gradient-headroom** (separable enough that deeper
hidden layers keep improving); at high overlap BP's hidden representations stop improving with depth (slope→neg) —
**supervised depth needs headroom.** OURS's **contrastive** objective keeps building discriminative structure with
depth *regardless* of task headroom, so its composition is **difficulty-robust**. The **inverted-U at easy+deep**
is w=2's myopic drift: with a coordination horizon of 2, under abundant headroom the early layers over-commit and
layers 5–8 drift — exactly what P3.2 showed **w=4 fixes** (a longer horizon climbs monotonically to L8).

**5 · Threats.** (a) This is the **per-layer probe** (representation quality), *not* task accuracy — "OURS top > GD
top" means OURS's penultimate representation is more linearly separable than BP's penultimate *hidden* layer at
matched budget, **not** "OURS beats BP at the final task" (BP still has its output layer). (b) Hard-regime absolute
levels are near chance — the **slope** is the claim. (c) Single task family (`make_tierb`, 64 clusters) — a
real-data depth-needing anchor is owed. (d) **w=2 only** (w=4 untested here, but P3.2 has it — the easy+deep fix).
(e) GD ceiling = fixed-budget (the recurring caveat).

**6 · Decision.** **A3 = depth-composition GENERALIZES** — overturns the PARTIAL worry. **Carry forward:** (i) OURS
composes depth robustly across the whole difficulty band, **more robustly than supervised BP** (which needs
headroom); (ii) the regimes are **complementary** — OURS is the depth-composer for the **hard / low-headroom**
regime, supervised methods for easy; (iii) **window size is a difficulty-dependent knob** — w=2 is cheap and
sufficient in the hard regime, but easy+deep needs a longer horizon (w=4) → a Phase-5 adaptive-window knob.

**7 · Cost-honesty.** OURS's composition is achieved **forward-only with a 2-deep coordination-window backprop**
(credit-distance 2) vs GD's full-depth (8) backprop — the same short-credit-distance advantage as P4.0, here
buying depth-composition the supervised ceiling *loses* in the hard regime. Not re-metered (probe rung); the cost
story is P4.0's, and the window-size knob (w2→w4) is a cost dial for Phase 5.

**8 · Map-contribution → P5.** A3 tile: **OURS owns depth-composition in the hard / low-headroom regime; supervised
methods own it at easy** (crossover ≈ overlap 0.6 — a key map coordinate). Tells Phase 5: (a) for **hard** tasks,
depth-with-coordination is OURS's lever — invest in it; (b) **scale the coordination window with available
headroom** (cheap w=2 in the hard regime; grow to w=4 for easy+deep monotone composition) — a concrete adaptive
knob; (c) at easy+deep with fixed w=2, cap depth (the inverted-U says layers 5–8 don't pay).

---

## Reproducibility

`figs_p4_2/{manifest.json, arrays.npz, _ckpt.jsonl}`; `python plot_p4_2.py figs_p4_2`. Single-threaded, `python
-u`, `PYTHONIOENCODING=utf-8` (the cp874 console gotcha — `×` in a print crashed the first launch; fixed to ASCII).
**Uses sklearn LogisticRegression for the probes — the phantom-hang risk** — ran clean with `OMP_NUM_THREADS=1` +
per-cell fsync; verified alive mid-run. Reuses Phase-3 `make_tierb`, `probe_per_layer`, `gd_hidden_probe`,
`train_mlp`; new: `exp2/run_p4_2.py` (`train_olu` w=1/w=2) + `plot_p4_2.py`.
