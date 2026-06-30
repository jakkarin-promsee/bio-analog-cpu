# Phase 5 — the SCFF close-out: solve the depth decay, read it cheaply

> **✅ Complete (2026-06-30; P5.0 → P5.9, all guards pass).** The front door to Phase 5 — the navigable overview.
> The deep story with every figure is **[`phase5-report.md`](phase5-report.md)**; the scalars are
> **[`RESULTS.md`](RESULTS.md)**; the pre-run design + the binding reporting contract are **[`design.md`](design.md)**
> and **[`result-format.md`](result-format.md)**.
>
> **Verdict in one line:** the depth decay is **solved, scoped** — the cheap brain is finished. Depth is **EARNED**
> (a sharper objective makes the readout **beat** a genuinely-tuned backprop, and the probe tail reaches the objective
> ceiling), **read CHEAPLY** (a fixed short reader, ~8× under the all-tap readout), **continual-SAFE** (the A6
> sleep-recovery continual win is intact), and **natural-CONFIRMED on composable data** (the fix is real on digits;
> null-but-safe on the no-depth CIFAR-flat wall). The project now pivots to Phase 6 — the GD side.

---

## The problem

Phase 4 left the cell with one open wound. Its representation gets **more** class-separable for ~5 layers, then
**decays** — it stops composing and starts drifting. Phase 4's W64 control proved the cause is **depth, not width**
(widening doesn't fix it; dead-fraction ≈ 0), and a follow-up named it: **a direction failure.** The deep layers
are alive and full-rank, but their representation has drifted *off the class manifold* once a layer's abstraction
saturates — the same **density ≠ class** fault that has shadowed this project four times. A deep cell that decays is
a problem on two fronts: it caps how much depth the substrate can spend, and the **all-tap readout** (the deployed
Phase-4 reader that concatenates *every* layer) drags in the drifted deep layers, **diluting** the class signal and
burning the **80/20 cost win** (the ~80% cheap forward-only SCFF / ~20% precise GD split that makes the chip cheap).
Phase 5's job: **earn the depth back, and read it cheaply** — without rewriting the SCFF stream (the P2.5 envelope:
read / gate / add-to-objective is allowed, rewriting is forbidden) and without denting the **A6 continual win**
(Phase 4's result that a periodic sleep recovers what online training catastrophically forgets — the architecture's
reason for being).

## What we did

- **Cell under test (OURS):** `SCFFContrastOverlap` — the Phase-3 adopted contrast (InfoNCE, two-mask) + coordination
  cell, with **temperature** and **window** as the levers. Forward-only, per-sample, no batch statistics.
- **The two references, every depth figure:** the **w12 ceiling** — a *forbidden* full-credit (full-backprop reach)
  window, measured only as the objective-capability upper bound, **never deployed** — and the **truncation floor**
  (a cheap from-scratch short stack), the cost baseline every reader must beat. Plus **tuned-BP / Bayes** as the
  achievable old-world anchor (carried from Phase 4).
- **The ladder (P5.0 → P5.9):** bench + decay reproduction → the two *earn-depth* levers (temperature, window) → the
  diagnosis (lost-vs-rotated + the profiler) → the *read-cheaply* readout (per-depth heads, then a calibrated exit on
  the continual home) → the conditional preservation cell → the continual-safety gate → natural-data confirmation →
  the assembled-cell verdict.
- **Discipline:** seeds `[42,137,271,314,1729]` (3 for the heaviest continual cells), median [IQR], "real" =
  IQR-disjoint **and** ≥4/5 by seed; one variable per rung; guards (FD-gradient, equivalence, dead-frac, cost-monotone)
  logged every run; failures kept as data.

## What we found

The deliverable is the close-out scorecard — four verdicts, reported separately:

![phase-5 scorecard](exp9/figs_p5_9/SCORECARD.png)
*The SCFF close-out in one glance: depth EARNED (the re-tuned readout beats tuned-BP, the probe tail reaches the w12
ceiling), read CHEAPLY (a fixed short stack at ~8× under all-tap — the adaptive exit lost), continual-SAFE (A6
intact), and natural-CONFIRMED on composable data. (Assembled from each rung's committed-cell columns, n=5 / n=3
continual.)*

| verdict (design §7) | bar | result | call |
| --- | --- | --- | --- |
| **① depth-EARNED** | headroom tail in the w12 band, or peak ≥ profiled extractor depth | readout **0.550 [0.545–0.553] beats tuned-BP 0.531 [0.531–0.533]** (IQR-disjoint; the tuned `race_bp` racer, not Phase 3's fixed-budget GD); probe tail **0.530** (w2) → **0.562** (w4) reaches the w12 ceiling **0.556**; peak **L5→L6** (w2), **→L9** (w4) | **EARNED** |
| **② read-CHEAPLY** (the cost gate, STOP ①) | adaptive exit beats all-tap **and** truncation on the continual stream | adaptive exit **dominated** (0.479 @ 74.7k); **fixed truncation 0.547 @ 9.0k = 8× cheaper than all-tap** (readout-MACs; the L12 bulk still runs) | **SCOPED** (fixed, not adaptive) |
| **③ continual-SAFE** (P5.7) | the fix keeps the A6 continual win (BWT within the −0.02 gate) | temp0.2 **BWT −0.026** vs −0.017, AA 0.944; the sleep-recovery mechanism intact | **PASS** |
| **④ natural-CONFIRM** (P5.8) | the synthetic decay + fix survive real flat data | decay **real on both** (digits +0.260, CIFAR-flat +0.094); fix **+0.152** on digits (halves the decay, not erases); **null-but-safe** on CIFAR-flat | **REAL** |

*(Earn-depth numbers are per-layer linear-probe / readout accuracies on a synthetic Gaussian **headroom** task — the
decay's home — confirmed on real digits: a representation claim, not a static-accuracy benchmark. The **w12 ceiling**
is the forbidden full-credit upper bound, never deployed; the **truncation floor** is the cheap fallback.)*

**The mechanism, one paragraph.** The decay was **objective-locality, not an intrinsic "Tunnel"** — the diagnostic
w12 window composes the *whole* 12-layer stack with no decay, so the depth is curable. Two cheap forward-only levers
cure it. **(1)** A **sharper InfoNCE temperature (0.2)** makes each update more class-selective, holding the
representation on the class *direction*; an lr-matched control shows **~82% of the lift is direction, not a disguised
learning-rate** (0.078 of the 0.095 lift survives matching the step-size). **(2)** Because the continual home is the
*flat* regime, per-depth heads read by a **short fixed stack** beat all-tap on cost (all-tap can't zero-weight the
drifted deep layers, so it dilutes the signal). The one honest narrowing: depth is read by a **fixed** short stack,
not an **adaptive** per-sample exit — the calibrated max-softmax exit (an **oracle** best-per-input selector reaches
0.87, but a confidence threshold can't find it) was *struck* (P5.5), because on the flat home the per-depth heads are
weak-but-decorrelated, so **pooling beats placement** (the exact inverse of the headroom result).

## The committed cell

> **`SCFFContrastOverlap`, temperature 0.2, coordination window 2, L12 bulk, NO residual, deployed with a FIXED
> reader** — a short from-scratch truncation stack (~L2–3) on the continual home; all-tap when peak accuracy is
> wanted; **w4** the bounded depth-closer for compositional tasks. Forward-only, per-sample, sleep-consolidated.
> This is the cheap brain, closed.

## What it set / closed (the Phase-6 hand-off)

Picked from data, not guesses:

1. **The deployed recipe to optimize:** temp0.2/w2 SCFF bulk + a sleep-consolidated **fixed** reader + the Ch7 gate +
   sleep cadence — now **readout-aware** (consolidate the *extractor-depth* features the reader reads: shallow on the
   flat home, deep on compositional tasks; re-validate the gate online under shift). **This is Phase 6's core.**
2. **Earn depth with the objective, not machinery** — temperature is the free lever; **w4** is the bounded
   depth-closer for compositional tasks. Genuine global-credit machinery stays **deferred** (the cheap levers sufficed).
3. **Read shallow on the flat home** — a short fixed stack, not the adaptive exit (struck). Reserve the deep L12 bulk
   for the compositional tasks where depth actually pays.
4. **Parked with evidence (not dead):** the **oracle-exit headroom** (the *oracle* best-per-input selector reaches
   0.87 vs the deployed 0.55 on the home — a better per-sample selector could unlock large gains, but it is a
   selector / north-star problem); a *compositional*
   continual stream to test whether an adaptive exit ever earns its keep; preservation/frozen-residual (re-open only on
   a natural decay the fixed reader can't sidestep).
5. **Owed decision-record delta:** **S9** in [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) — readout =
   fixed short-stack placement (revising S3's literal "tap ALL layers", keeping its intent); adaptive exit struck;
   temp0.2/w2 adopted; no residual. *(Recorded.)*

## Validated vs not

| | status |
| --- | --- |
| Depth **earned** — readout **beats tuned-BP**; the probe tail reaches the w12 ceiling | ✅ (P5.1/P5.2) |
| Decay is **objective-locality, not an intrinsic Tunnel** (w12 composes the full stack) | ✅ (P5.0) |
| Useful depth **read ~8× cheaper than all-tap** via a short fixed stack | ✅ (P5.4 static & P5.5 continual) |
| The fix **keeps the A6 continual win** (BWT within gate, sleep-recovery intact) | ✅ (P5.7) |
| The **decay reproduces on real data** (digits + CIFAR-flat); the **temp-fix is real on digits** (halves it) | ✅ (P5.8) |
| Temp-fix helps on **flat data with no composable depth** (CIFAR-flat) | ❌ null-but-safe — needs convolution (out of scope) |
| **Adaptive** per-sample early-exit beats a fixed reader on the home | ❌ **struck** — flat home rewards pooling (P5.5) |
| Preservation (frozen residual) needed | ❌ **skipped** — cheaper levers close the gap (P5.6) |

## Read next

| For | Go to |
| --- | --- |
| **The whole model in one self-contained file (v1.0.0)** | [`../phase5-final-architecture.md`](../phase5-final-architecture.md) |
| The full story, every figure, the per-rung reads | [`phase5-report.md`](phase5-report.md) |
| The scalar ledger (per-rung numbers + verdicts) | [`RESULTS.md`](RESULTS.md) |
| The pre-run design (the ladder, the build plan, the decision record) | [`design.md`](design.md) |
| The binding reporting contract (figures · tables · the 8-slot summary) | [`result-format.md`](result-format.md) |
| The run-cards | `exp0`…`exp9/` `experiment-*.md` (P5.0–P5.9; exp6 = the documented skip) |
| The literature behind it | [`../../research/papers/phase5/`](../../research/papers/phase5/README.md) |
| The Stage-1 arc | [`../stage1-report.md`](../stage1-report.md) · **Prev:** [Phase 4](../phase4/README.md) |
