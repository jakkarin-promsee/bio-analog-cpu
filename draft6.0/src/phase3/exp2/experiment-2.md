# Experiment P3.2 (side road A) — the depth-headroom confirmation: does the method *compose* depth?

> **Status: ✅ RUN COMPLETE (2026-06-22) — DECISIVE PASS. Given depth headroom, contrast + coordination COMPOSES
> depth (rises monotonically, matches/exceeds the GD baseline) — confirming P3.1's flat-CIFAR PARTIAL was a
> task-ceiling artifact, and overturning P2.2's "depth intrinsic to locality."** P3.1 showed coordination works
> but flat-CIFAR has no headroom for *anyone* (GD flat). This side road built a flat-MLP task *with* headroom and
> re-ran the comparison. Convention: question → setup → result → read → decision. Builds on
> [`../exp1/experiment-1.md`](../exp1/experiment-1.md). Reporting: [`../result-format.md`](../result-format.md).

## Question

P3.1 left one thing untestable on flat-CIFAR: **when depth *genuinely helps* (GD rises), does `contrast +
coordination` rise too — does the method actually *compose* depth, or only degrade gracefully?** Need a flat-MLP
task where **GD-hidden RISES** with depth (headroom) so "rising" is achievable at all.

## Setup

**The headroom hunt ([`scan_headroom.py`](scan_headroom.py)):** scanned the tested `make_tierb` generator across
8 hard settings (many clusters, high overlap), measuring GD-hidden slope vs energy-SCFF slope. **Finding:** no
config gives *both* "GD rises AND energy declines" — in `make_tierb`'s space the easy/hard transition is *shared*
(easy-for-all or hard-for-all). But **one config has clean GD headroom:** `grid=4, n_active=3, overlap=0.6,
dim=40, n_class=4` (64 clusters) → **GD-hidden rises +0.021 (0.374 → 0.481).** Locked as the `headroom` task
(added to the P3.0 bench `CFG`). The comparison = P3.1's exact harness (`run_p3_1.py headroom`): contrast window
`w ∈ {1,2,4}` + energy-wall + GD ceiling + random floor; 5 seeds, median + IQR; single-threaded.

## Result / figures

**Run 2026-06-22**, 5 seeds. Figures in [`../exp1/figs_p3_1_headroom/`](../exp1/figs_p3_1_headroom):
[F3⁺](../exp1/figs_p3_1_headroom/F3plus_depth.png) · [SLOPE](../exp1/figs_p3_1_headroom/SLOPE.png) ·
[SELECT](../exp1/figs_p3_1_headroom/SELECT.png).

| cell (n=5 median) | probe L1 → L8 | slope/layer | decline | tail-ret | selectivity (mean) |
| --- | --- | --- | --- | --- | --- |
| energy-wall | 0.39 → 0.34 | **−0.0055** (declines — the wall) | — | — | ~0 |
| contrast w1 (= P3.0, no coord) | 0.41 → 0.46 | **+0.0010** (rise-to-L3 then **falls**) | 0.027 | 0.86 | +0.153 |
| contrast w2 (coordination) | 0.41 → 0.52 | **+0.0124** (rises) | 0.010 | 0.94 | +0.175 |
| **contrast w4** (more coordination) | 0.41 → **0.569** | **+0.0220** (rises, monotone) | **0.001** | **0.99** | **+0.181** |
| GD-hidden ceiling | 0.39 → ~0.51 | +0.02 (rises — headroom ✓) | — | — | — |

**5/5 seeds:** w4 final ∈ [0.556, 0.577] (tight); the slope ordering w1 < w2 < w4 is monotone every seed; w4's
deep probe (~0.57) **exceeds** GD's final held-out (~0.52) on this fixed-budget baseline.

## Read (eight-slot, compressed)

1. **Claim.** **Given depth headroom, the discriminative-contrastive objective + cross-layer coordination makes
   forward-only *unsupervised* learning genuinely *compose* depth — per-layer separability rises monotonically to
   the top of the stack, matching/exceeding the GD baseline — and *coordination is the decisive lever* (without it,
   contrast rises then falls; with it, it climbs all the way).** This is the achievable "rising" that flat-CIFAR's
   missing headroom hid in P3.1.
2. **Number.** slope w1 +0.001 → w2 +0.012 → w4 +0.022 (monotone, 5/5); w4 0.41→0.569, tail 0.99, sel +0.181;
   energy −0.0055 (the wall); GD rises 0.39→0.51 (headroom). 
3. **Figures.** [F3⁺](../exp1/figs_p3_1_headroom/F3plus_depth.png) — w4 the top curve at depth, above GD; w1
   peaks at L3 and declines (myopia); energy declines.
4. **Mechanism.** Depth helps here (GD rises). Energy can't use it (clusters density, declines). Contrast *without*
   coordination preserves class info but each layer re-discriminates myopically → rises early, drifts down deep
   (the P3.0/P3.1 "preserved but declining"). Coordination (the window) lets each layer's update serve the next's
   discrimination → the class signal *composes* instead of drifting → monotone rise. This is exactly the
   cross-layer coordination P2.2 named as the missing ingredient, supplied **forward-only** by Direction 1.
5. **Threats.** (a) **Synthetic** headroom task (make_tierb), not natural data — it proves the *mechanism* (method
   composes depth when headroom exists), not a benchmark number. (b) **GD is a fixed-budget from-scratch
   baseline**, not a tuned max — so "exceeds GD" is vs *this* GD; the **load-bearing claim is the monotone rising
   slope**, not the GD-beat. (c) flat-CIFAR remains capped (no headroom) — this doesn't change that, it explains
   it. (d) Energy declines only mildly (−0.0055) here; the wall is gentler than CIFAR's −0.020 but present.
6. **Decision.** **DECISIVE PASS → the reframe + Direction 1 are validated; route to P3.3 (continual veto).**
   P2.2's "depth intrinsic to forward-only locality" is overturned: it was intrinsic to the *energy objective*;
   with a discriminative objective + coordination, forward-only unsupervised learning composes depth. The carried
   cell stays **`contrast + coordination`** (w≥2; w4 best where headroom is large). The static-depth question is
   now *answered yes (with headroom)*; the project-deciding question is continual preservation (P3.3).
7. **Substrate.** unchanged from P3.1 — forward-only between windows, gradient-isolated at boundaries, in-batch
   negatives (LUT). w=2 the cheapest sufficient on mild headroom; bigger windows help more where headroom is large.
8. **Continual.** still the P3.3 question (now with a fully-validated static cell to veto-test).

## Decision

**The Phase-3 thesis is proven on the static axis.** A different objective (contrast) was necessary (P3.0); it
preserved class info but declined; **cross-layer coordination (your Direction 1) makes it *compose* — rising
monotonically with depth, matching/exceeding GD — whenever the task has depth headroom** (here, and overturning
the P2.2 verdict). Flat-CIFAR's P3.1 "PARTIAL" is now understood as a *task-ceiling* artifact, not a method
limit. **Carry `contrast + coordination (w≥2)` → P3.3 (the continual veto)** — the question that decides
adoption. *(Side road B, direct-feedback, is now lower-value — window coordination already earns the rise; it
stays an optional "is global cheaper than a window" refinement.)*

## References

- **P3.1** ([`../exp1/experiment-1.md`](../exp1/experiment-1.md)) — coordination works, flat-CIFAR capped (the
  PARTIAL this resolves). **P3.0** ([`../exp0/experiment-0.md`](../exp0/experiment-0.md)) — the contrastive objective.
- **The reframe** ([`../../../research/papers/phase3/the-objective-reframe.md`](../../../research/papers/phase3/the-objective-reframe.md)) — predictive/
  discriminative preservation composes depth (GIM/CLAPP); now shown on our substrate with coordination.
