# P5.9 — synthesis + assembled-cell confirmation: the SCFF close-out verdict

*The capstone. **The public README / phase5-report synthesis is DEFERRED** — per the session directive, the author
returns to write it together. This card is the experiment-part **decision record**: the final committed cell, the
assembled-cell confirmation, the two verdicts (reported separately), and the Phase-6 hand-off. Figure: `SCORECARD.png`.*

---

## The final model — "which SCFF we will choose"

> **The committed cell: `SCFFContrastOverlap`, temperature 0.2, coordination window 2, L12 bulk, NO residual,
> deployed with a FIXED reader (a short from-scratch truncation stack, ~L2–3, on the continual home; all-tap when
> peak accuracy is wanted).** Forward-only, per-sample, sleep-consolidated readout. This is the cheap brain, closed.**

The **w4** window is the *bounded depth-closer* — adopted as an option for compositional tasks that need the last
0.03 of composing depth (P5.2), not the continual-home default.

## The assembled-cell confirmation (why no fresh stacking-run was needed)

The design (§3 P5.9) asks for an end-to-end run of the assembled cell to catch non-linear lever stacking. **There is
no stacking to catch:** `temp0.2 / w2` is **one config**, and that same config ran *every* rung — P5.1 swept temp at
w2, P5.2 swept window at temp0.2, and **P5.3–P5.8 all used temp0.2/w2 unchanged.** The levers were never tuned
independently and then combined; the committed cell *is* the cell each rung measured. The assembled-cell confirmation
is therefore the **consistency of the committed-cell columns across rungs**, which `SCORECARD.png` makes visible
(assembled from each rung's `arrays.npz`; regen-able). P5.6 (residual) was skipped → the cell carries no residual, so
there is no residual×norm interaction to confirm either.

## The two verdicts (design §7 — reported SEPARATELY)

| verdict | bar | result | call |
| --- | --- | --- | --- |
| **DEPTH-EARNED** | headroom tail-L12 within band of w12, or peak ≥ profiled extractor depth | readout **0.550 beats tuned-BP 0.531**; probe tail **0.530** (w2) → **0.562** (w4) reaches w12 **0.556**; peak L5→L6 (w2) → L9 (w4) | **EARNED** — the cheap levers (temp, bounded window) compose the depth a task needs; w4 reaches the objective ceiling |
| **READ-CHEAPLY** (STOP ①) | adaptive exit beats all-tap AND truncation on the continual stream | adaptive exit **C5-PESSIMISTIC** (dominated, 0.479@74.7k); **fixed truncation 0.547@9.0k = 8× cheaper than all-tap** | **SCOPED** — read cheaply via a **fixed short stack** (8×), NOT adaptive placement; the flat home doesn't reward per-sample adaptivity |

**Both gates cleared:** continual-SAFE (P5.7 — temp0.2 BWT −0.026 vs −0.017, AA 0.944, the A6 sleep-recovery
mechanism intact) and natural-CONFIRM (P5.8 — decay real on digits+CIFAR; temp-fix +0.152 on digits, null-but-safe on
the CIFAR-flat no-headroom wall).

## Is SCFF "done"?

**Yes, scoped.** SCFF **composes the depth a task needs** (depth-EARNED) **and reads the continual home cheaper than
all-tap via a short fixed stack** (read-CHEAPLY, fixed-truncation branch), **continual-safe** (P5.7) and **real on
natural flat data** (P5.8). The one honest narrowing vs the original hope: depth is read cheaply by a **fixed short
stack, not an adaptive per-sample exit** — the calibrated max-softmax exit was *struck* (P5.5), because on the flat
continual home per-depth heads are weak-but-decorrelated (pooling beats placement; the inverse of P5.4's headroom
result) and confidence is a poor depth-selector. The cheap brain is **finished and trusted**; the project pivots to
optimizing the GD side (Phase 6).

## The one coherent story (the arc in a sentence)

The decay is a **direction** failure (deep local-contrast layers drift off the class manifold once a layer's
abstraction saturates); **a sharper InfoNCE temperature keeps each update on the class direction** and composes the
depth back (P5.1/P5.2, EARNED, continual-safe, real-data-confirmed) — and because the continual *home* is flat, you
**read it with a short fixed stack** (P5.3–P5.5), reserving the deep L12 bulk for the compositional tasks where depth
actually pays. **Single-depth placement wins where one depth is sharply best (headroom); pooling/short-fixed wins where
the signal is weak-but-distributed (flat home)** — the unifying law that ties P5.4 and P5.5 together. The spine held
throughout: every lever read/preserved the class **direction**, never a magnitude (density≠class, paid in full).

## Hand-off to Phase 6 (the GD-optimization era — formerly "Phase 5")

- **The deployed recipe to optimize:** temp0.2/w2 SCFF bulk + sleep-consolidated **fixed** reader (truncation/all-tap)
  + the Ch7 learning-gate + sleep cadence — now **readout-aware** (consolidate *extractor-depth* features; the sweet
  spot is shallow on flat, deep on compositional; re-validate the gate online under shift).
- **Parked, with evidence (not dead):** (a) the **oracle-exit headroom** (0.87 vs deployed 0.55 on the continual home,
  P5.5) — a *better per-sample selector* than max-softmax could unlock large gains, but it is a selector/north-star
  problem (confidence is a magnitude); (b) genuine global-credit machinery (still deferred — the cheap levers sufficed,
  P5.2); (c) preservation/frozen-residual (P5.6 skipped — re-open only on a natural decay the fixed reader can't
  sidestep); (d) a *compositional* continual stream to test whether adaptive exit ever earns its keep off the flat home.
- **Decision-record deltas owed to `idea/main.ideas.v1.md`** (commit when the author writes the README): **S9** —
  readout is **fixed-short-stack placement** (revising S3's literal "tap ALL layers"; S3's *intent* kept), the adaptive
  exit struck; temp0.2/w2 adopted; no residual.
- **Doc sync owed at close** (design §0/§9): flip the draft-6 orientation docs from "P5 = optimization" to "P5 =
  depth-readout fix / P6 = continual optimization", and update the `ref-report/` glossary (composing-depth,
  expected-compute, truncation floor, …). **Deferred to the README session.**

## Status

**Experiment ladder P5.0–P5.9 COMPLETE.** Cards: `exp0`…`exp9` (exp6 = the documented skip). Ledger: `RESULTS.md`.
Apparatus: `p5lib.py` (+ `plot_p5.py`, all figures regen-able). **Owed (with the author): the public `README.md` +
`phase5-report.md` synthesis, the `idea/main.ideas.v1.md` deltas, and the phase-renumber doc sync.**
