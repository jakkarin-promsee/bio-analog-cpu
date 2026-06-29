# Phase 5 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema, no prose. The story lives in `expK/experiment-K.md` and (at close)
> the front-door `README.md`; this is the numbers-only ledger. Numbers are `median [q25–q75]`, n=5 unless noted.
> The cell under test is `SCFFContrastOverlap` (adopted contrast+coordination, `temp`/`window` the levers); refs
> are the **w12** objective-capability ceiling (forbidden, never deployed) and **tuned-BP** / **Bayes** (achievable,
> old-world). "Real" = IQR-disjoint **and** ≥4/5 by seed (§B).

---

## P5.0 — bench + decay reproduction + guards `exp0`
*Locked: L12 · W64 · DIM40 · C4 · seeds[42,137,271,314,1729] · PROBE_EP=120 · cost-units = substrate backward-work.*

**Guards:** equivalence (overlap≡OLU) `0.0e+00` · FD-gradient `2.06e-08` (<1e-5) · dead-frac max `0.016` (≈0) ·
cost monotone in window `[52676, 101060, 197828, 584900]` → **ALL PASS**.

| task / cell | peak@L | tail-L12 (probe) | readout acc | ref (w12 · BP/Bayes) | verdict |
| --- | --- | --- | --- | --- | --- |
| headroom **w2** | L5 | **0.435 [0.411–0.437]** | 0.449 [0.446–0.455] | w12 0.556 · BP 0.531 | decay reproduced |
| headroom **w12** (ceiling) | L12 | 0.556 [0.553–0.557] | 0.569 [0.563–0.572] | — | no decay → objective composes |
| flat **w2** | L3 | 0.620 [0.602–0.669] | — | w12 0.699 · Bayes-opt 0.890 | peaks early, less decay |
| flat **w12** | L4 | 0.699 [0.693–0.701] | — | Bayes-opt 0.890 | composes (easy task) |
| mixed flat-subtask **w2** | L5 (0.724) | **0.475 [0.469–0.549]** | 0.40-class readout | w12 0.708 · BP 0.761 | **corruption reproduced** |
| mixed flat-subtask **w12** | — | 0.708 [0.701–0.712] | — | BP 0.761 | full credit preserves |
| mixed head-subtask **w2** | — | 0.384 [0.376–0.391] | — | w12 0.471 · BP 0.493 | needs depth, w2 short |

**Reads:** peak within ±1 of L5 ✓ · tail in ~0.43 band ✓ → **BENCH TRUSTED**. Earn-depth gap to w12 = **0.121**
probe / **0.120** readout (real). Corruption (w2 vs w12 flat-subtask) IQR-disjoint, 5/5 by seed (real). The decay is
**objective-locality, not an intrinsic Tunnel** (w12 composes the whole stack). **Banked:** the bench; no cell change.
**Continual-safety (P5.7):** n/a (no change).

---

## P5.1 — objective sharpness: temperature, the free lever `exp1`
*Locked: window=2 · mask=0.5 · L12 · W64 · C4 · seeds[42,137,271,314,1729] · PROBE_EP=120. lr-calibration: step-norm
ratio temp0.2/temp0.5 = 2.249 → lr-matched temp0.5 lr = 0.0675. Guards: equiv 0.0e+00 · FD 2.06e-08 → PASS.*

| temp (headroom) | tail-L12 | readout | peak@L | vs-w12 (0.556/0.569) · BP (0.531) | verdict |
| --- | --- | --- | --- | --- | --- |
| 0.5 (baseline) | 0.435 [0.411–0.437] | 0.449 [0.446–0.455] | L5 | the decay | baseline |
| 0.35 | 0.481 [0.461–0.498] | 0.475 [0.473–0.507] | L5 | — | composes more |
| **0.2 (committed)** | **0.530 [0.527–0.539]** | **0.550 [0.545–0.553]** | L6 | tail −0.026 · **ro beats BP** | **adopt (pend P5.7)** |
| 0.1 | 0.523 [0.519–0.526] | 0.536 [0.535–0.545] | L9 | — | within noise of 0.2 |
| 0.05 | 0.491 [0.489–0.491] | 0.501 [0.478–0.513] | L10 | real-below 0.1 (5/5) | **collapse** |
| temp0.5 @ lr-matched | 0.452 [0.435–0.457] | 0.445 [0.443–0.453] | L5 | the lr control | flat ≈ baseline |

**Controls:** FREE-vs-LR — temp0.2 (0.530) vs lr-matched temp0.5 (0.452), **5/5 + IQR-disjoint → DIRECTION (free)**,
~82% of the +0.095 lift is direction, ~18% lr. BATCH-FLOOR — temp0.05 batch32 0.491 vs batch64 0.485 → **no rescue →
objective floor** (intrinsic over-sharpening, not negatives-starvation). MIXED flat-subtask un-corrupts 0.475→**0.697
[0.680–0.709]** at temp0.2 (≈ w12 0.708; lr-matched only 0.516 → direction). FLAT: 0.620→0.673 at temp0.2 (free margin
smaller — easy task, 4/5). **Banked:** temp=0.2 (provisional — **P5.7 gates it**). **Inherited by P5.2:** temp0.2 for
the temp×w{3,4} combo to close the residual 0.026 to w12.

---

## P5.2 — credit reach: temperature suffices, window closes the rest `exp2`
*Locked: temp=0.2 · mask=0.5 · L12 · W64 · C4 · seeds[…] · PROBE_EP=120 · cost = substrate backward-work. Guards PASS.*

| window (headroom, temp0.2) | tail-L12 | readout | peak@L | bwd-work | vs-w12@t0.5 (0.556) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **w2 (default)** | 0.530 [0.527–0.539] | **0.550** [0.545–0.553] | L6 | 101k | −0.026 (real) | beats BP; small residual |
| w3 | 0.548 [0.547–0.549] | 0.561 [0.560–0.561] | L7 | 149k | −0.008 | composes more |
| **w4 (closer)** | **0.562 [0.547–0.562]** | 0.559 [0.557–0.561] | L9 | 198k (2×) | −0.006 (3/5 above) | **closes to ceiling** |
| w12@temp0.2 (ceiling) | 0.552 [0.549–0.559] | 0.575 [0.573–0.580] | L12 | 585k | — | Pareto-dominated by w4 |
| w4-stride2 (overlap) | 0.559 [0.556–0.567] | — | L9 | 331k (1.67×) | within noise of w4 | **struck on cost** |

**Reads:** w4>w2 real (+0.032, 4/5, IQR-disjoint); w4 not-real-below w12 (3/5 above) → **residual CLOSED**. Overlap
within-noise of non-overlap at temp0.2 (T3's temp0.5 hurt softened to neutral) but 1.67× cost → **dominated**.
**Track C DEFERRED** (no gap that matters; cheap levers close it; 2601.21683 not load-bearing). flat w4 0.712, mixed
flat-subtask w4 0.719 (window helps off-headroom too). **EARN-depth thread CLOSED** — committed **temp0.2/w2** (default,
beats BP), **w4** = bounded depth-closer. **Inherited by P5.3+:** temp0.2/w2. **Continual-safety (P5.7):** still owed.

---

## P5.3 — lost/rotated + profiler + truncation floor `exp3`
*Locked: committed cell temp0.2/w2 · L12 · seeds[…] · PROBE_EP=120. Guards PASS.*

| task | readout-best (extractor end) | readout-top (L12) | placement gain | probe-peak↔readout-opt | verdict |
| --- | --- | --- | --- | --- | --- |
| **flat** | 0.785 [0.782–0.787] @L2 | 0.677 [0.671–0.677] | **+0.108** | L4↔L2 (disagree 2) | read shallow |
| **mixed** | 0.773 [0.768–0.777] | 0.696 [0.689–0.701] | **+0.077** | L4↔L2-3 | read shallow |
| **headroom** | 0.563 @L9 | 0.550 [0.545–0.553] | +0.013 (plateau) | L8↔L9 (**agree ±1**) | placement≈cost-only |

| truncation (headroom top-readout) | L5 | L7 matched | **L7 own-tuned** | L9 | full-L12 best/top |
| --- | --- | --- | --- | --- | --- |
| | 0.557 | 0.543 | **0.564 [0.556–0.565]** | 0.557 | 0.573 / 0.550 |

**Reads:** decay is **LOST not rotated** (MLP recovers Δ0.005 at L12) but small (~0.026 at temp0.2) → placement
sidesteps it, **preservation (P5.6) LOW-VALUE**. **Placement value is task-dependent** — large on easy tasks (read the
extractor end: flat +0.108), ~0 on headroom (broad plateau). Profiler valid on headroom (±1) but ~2 layers too deep on
flat/mixed → **placement is readout/head-driven** (the spine). Complexity dial was *difficulty* (overlap) not
*structure* — peak is difficulty-invariant (re-test owed). **Banked:** lever = PLACEMENT; **truncation floor 0.564** =
the control P5.4/5.5 must beat. **Inherited by P5.4:** read the extractor end; beat 0.564. **P5.6:** flagged skippable.

---

## P5.4 — the readout MVP: per-depth heads Pareto-dominate all-tap `exp4`
*Locked: committed cell temp0.2/w2 · L12·W64 · seeds[…] · PROBE_EP=120. Readout params matched: heads 26 544 ≈ all-tap
24 740 (1.07×) → gap is structure not capacity. Forward-MACs metered. Guards: equiv 0.0 · FD 2.06e-08 → PASS.*

| task | head-best (MLP) | head-best (lin) | all-tap | Δ head−alltap | sign | read-cost | best_d | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **headroom** | **0.573** [0.556–0.577] | 0.556 | 0.526 [0.525–0.535] | **+0.047** | **5/5** | 0.29× | L5 (L3–L7) | heads beat (real) |
| **mixed** | **0.633** [0.617–0.635] | 0.609 | 0.611 [0.607–0.620] | **+0.021** | **5/5** | 0.29× | L4–5 | heads beat (real) |
| **flat** | 0.785 [0.782–0.787] | 0.747 | 0.783 [0.778–0.787] | +0.002 | 4/5 | **0.12×** | L2 (L1–L3) | tie, 8× cheaper |

**Reads:** per-depth heads **Pareto-dominate** all-tap — on composite tasks (headroom +0.047 5/5, mixed +0.021 5/5)
cheaper **and** more accurate; on flat a tie at 0.12× cost. Mechanism: all-tap concatenates the **drifted tunnel
layers** (late-layer direction decay), which a capacity-limited readout can't zero-weight → dilutes the class signal;
one head reads the sharp depth and sidesteps it (the spine). head-best **0.573 > truncation floor 0.564** (+0.009).
**Linear ≈ MLP head** (within 0.02–0.04) → **linear head = deployable base**, MLP optional upgrade. **Caveat:** head-best
is the **ORACLE** depth (best_d spreads L3–L7/seed) → P5.5's calibrated **head-confidence** exit must reach it.
**Banked:** ADOPT per-depth heads (linear base); all-tap dominated. **Inherited by P5.5:** calibrated exit chases the
oracle head-best on the **continual** stream, beat 0.564. **Continual-safety (P5.7):** still owed (static workload here).

---

## P5.5 — calibrated early-exit on the continual home: adaptive exit dominated → ship a fixed reader `exp5`  · STOP ①
*Locked: committed cell temp0.2/w2 · L12·W64 · P4.5 class-incremental stream (10-class make_gauss, 5 tasks of 2,
overlap 0.7) · SCFF_EP=8 (A6 home) · seeds[42,137,271] · forward-MACs meter · τ keep=0.95 all-tap, disjoint cal.
Guards: equiv 0.0 · FD 2.1e-08 → PASS.*

| reader (continual stream) | accuracy | forward cost | verdict |
| --- | --- | --- | --- |
| **all-tap** (deployed) | **0.618** [0.612–0.624] | 72.5k | best deployable acc (pooling helps on flat) |
| **truncation L2–3** (floor) | 0.547 [0.545–0.566] | **9.0k** [9.0–11.1] | 8× cheaper, −0.07 acc |
| oracle (best-per-input) | 0.869 [0.858–0.870] | 19.2k | loose 12-try upper bound (depth ~3.2) |
| **calibrated exit (one-shot τ)** | **0.479** [0.465–0.520] | 74.7k [39.8–74.9] | **DOMINATED** (worst acc, high cost) |
| calibrated exit (refit τ) | 0.479 [0.465–0.535] | 74.7k | refit doesn't rescue (τR=τ1 on 2/3) |

**Reads:** the adaptive max-softmax exit is **Pareto-dominated** (3/3) — calibration collapses to grid extremes
(τ=0.25 floor→exit L1, or τ=0.999 ceiling→exit the **decayed L12**). **STOP① NOT passed** under the pinned gate.
Mechanism = the **inversion of P5.4**: on the static headroom task one sharp depth beats all-tap (placement wins);
on the continual **flat** home the per-depth heads are weak but **decorrelated** (oracle 0.87≫any single 0.60), so
**pooling (all-tap 0.62) beats every single depth** → no single-depth exit can meet the 95%-all-tap bar *by
construction* → calibration degenerates. Decay **reproduces on the continual stream** (peak L2–3 → ~0.45 at L12).
**Banked:** SHIP A FIXED READER on the home — **truncation L2–3 = the cheap deployable** (8× cost at −0.07 → fewer
Scaps), all-tap = max accuracy; the **adaptive exit is STRUCK** (failure card). Read-cheaply cost win comes via a
**short fixed stack**, not adaptive placement. Combined with depth-earned PASS (P5.1/P5.2 headroom), the two §7
verdicts **split**. **P5.6:** still LOW-VALUE (truncation sidesteps it). **Inherited by P5.7:** does temp0.2 keep the
A6 win? (gates whether temp0.2 is banked at all). **Continual-safety (P5.7):** the next rung.

---

## P5.6 — preservation (frozen residual): SKIPPED (conditional, run-condition not met) `exp6`  · STOP ②
*Pre-registered conditional: run iff P5.1+P5.4/5.5 leave a gap. No `arrays.npz` (nothing run) — a documented decision.*

**Decision:** **do not build/run** the frozen near-identity residual. The gap it targets (the decay **multiplier** —
deep layers overwriting the extractor) does not survive the cheaper levers: **P5.1** temp0.2 already un-corrupts the
mixed task (0.475→0.697≈w12); **P5.3** decay is lost-not-rotated but **small** (~0.02) and preservation can't *recover*
lost info; **P5.4/P5.5** the deployed reader (truncation L2–3 / all-tap) **sidesteps** the deep tunnel — nothing reads
the top, so there's no "carry the extractor up" requirement. The S5-norm×residual interaction risks a new
sign/direction bug in the InfoNCE backward for a ≤0.02 upside. **STOP② taken** ("a cheap test, not a tier of
commitment"; its precondition is absent). **Final cell carries NO residual.** Re-open trigger: a large *natural*-data
decay (P5.8/P5.9) the fixed reader can't sidestep. Full reasoning: `exp6/experiment-6.md`.

---

## P5.7 — continual-safety gate: temp0.2 keeps the A6 win → BANKED `exp7`  · THE SPINE GATE
*Locked: `continual_eval` (A6 mechanism promoted into p5lib) · all-tap readout · w2 · class-incremental 5 tasks of 2 ·
SCFF_EP=8 · SLEEP_EP=60 · seeds[42,137,271]. One variable = cell config (temp at L4); depth a separate arm. Guards
PASS.*

| condition | digits AA | digits BWT | synth AA | synth BWT |
| --- | --- | --- | --- | --- |
| t05_L4 (A6 baseline) | 0.954 [0.947–0.956] | −0.017 [−0.020,−0.015] | 0.583 [0.556–0.585] | −0.176 [−0.191,−0.168] |
| **t02_L4 (GATE)** | **0.944** [0.942–0.949] | **−0.026** [−0.027,−0.022] | **0.575** [0.566–0.576] | **−0.162** [−0.172,−0.162] |
| t02_L12 (depth) | 0.929 [0.915–0.935] | −0.020 [−0.042,−0.020] | 0.584 [0.573–0.590] | −0.150 [−0.167,−0.148] |
| t02_L4_nosleep (rot) | 0.191 | −0.998 | 0.199 | −0.902 |

**Reads:** **GATE PASS both tasks** — temp0.2 holds AA (−0.01 digits) and BWT (−0.026 vs −0.017, within the −0.02 gate);
on synth it forgets **less** (−0.162 vs −0.176). The P5.1-feared "sharper temp overwrites prior tasks" does **not**
materialize (the bulk is unsupervised/forward-only — sharper temp sharpens *clustering*, not the current-task boundary;
SCFF-probe flat ~0.93). no-sleep rot collapses (AA ~0.19, BWT ~−0.95) → the A6 sleep-recovery mechanism **reproduces
decisively** on the committed cell. L12 is continual-*tolerable* (digits BWT −0.020 median, wide IQR; synth neutral)
but noisier than L4 → **deploy shallow on the home** (consistent with P5.5). **Banked: temp0.2/w2** as the committed
temperature; no milder-temp fallback needed (P5.1 branch does not fire). **Cell identity settled:** temp0.2/w2,
continual-safe; L12 to compose depth where it pays, shallow read to deploy. **Inherited by P5.8/P5.9:** confirm on
CIFAR-flat; assemble the cell.

---

## P5.8 — natural-data confirmation: decay real on both anchors; temp-fix holds where depth composes `exp8`
*Locked: committed cell L12/w2 · static all-class · per-layer linear probe PROBE_EP=120 · temp{0.5 decay,0.2 fix} ·
digits 64-D (n=5) + CIFAR-flat 3072-D (n=3, the Phase-2/3 wall). Guards PASS. Medians shown; the CIFAR temp0.2≈temp0.5
"null" rests on **IQR-overlap** in `NAT-ANCHOR-cifar` (n=3), not the point estimate.*

| anchor · temp | peak | top | tail-L12 | decay (top−tail) | readout |
| --- | --- | --- | --- | --- | --- |
| digits temp0.5 | L1 | 0.946 | 0.687 | **+0.260** | 0.951 |
| **digits temp0.2** | L1 | 0.958 | **0.839** | +0.119 | 0.950 |
| CIFAR-flat temp0.5 | L1 | 0.332 | 0.238 | **+0.094** | 0.311 |
| CIFAR-flat temp0.2 | L1 | 0.348 | 0.244 | +0.104 | 0.293 |

**Reads:** the **decay REPRODUCES on both real anchors** (digits +0.260, CIFAR +0.094) → not a synthetic artifact. The
**temp-fix REPRODUCES on digits** (tail 0.687→**0.839**, +0.152, clean-separated) and is **null on CIFAR-flat**
(+0.006, within noise). Mechanism: the temp lever extends *composing depth*, so it acts only where there's accessible
compositional structure — digits has it; **CIFAR-flat is the no-headroom wall** (GD-hidden itself flat ~0.36, needs
conv — out of scope §0.4), so the fix is null-but-safe (P5.7). digits peak L1 also re-confirms "read shallow" (P5.5
truncation). **Banked:** COMMIT temp0.2; the synthetic story is **real**, scoped honestly (no temp benefit on flat data
with no composable depth). **Inherited by P5.9:** assemble the verdict (committed cell validated on real flat input).

---

## P5.9 — assembled-cell confirmation: the SCFF close-out verdict `exp9`  · CAPSTONE
*Assembled from the committed-cell columns of every rung (one config — temp0.2/w2 — ran all of P5.1–P5.8, so no
stacking to re-confirm). Figure: SCORECARD.png. Public README/report DEFERRED to the author's return.*

| verdict (design §7) | result | call |
| --- | --- | --- |
| **① depth-EARNED** (headroom: readout vs BP, probe tail vs w12) | readout 0.550 beats BP 0.531; probe tail 0.530 (w2) → 0.562 (w4) reaches w12 0.556; peak L5→L6 (w2) → L9 (w4) | **EARNED** |
| **② read-CHEAPLY** (STOP ①, continual) | adaptive exit dominated (0.479@74.7k); **fixed truncation 0.547@9.0k = 8× cheaper than all-tap** | **SCOPED** (fixed, not adaptive) |
| **③ continual-SAFE** (P5.7) | temp0.2 BWT −0.026 vs −0.017, AA 0.944; A6 intact | **PASS** |
| **④ natural-CONFIRM** (P5.8) | decay real (digits+CIFAR); fix +0.152 digits, null-safe CIFAR-flat | **REAL** |

**Verdict — SCFF is "done" (scoped):** **`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, NO residual, fixed-reader
deployment** (short truncation ~L2–3 on the continual home; all-tap for peak acc; w4 = bounded depth-closer for
compositional tasks). It composes the depth a task needs AND reads the continual home 8× cheaper than all-tap via a
**short fixed stack** (the adaptive max-softmax exit was struck, P5.5 — the flat home doesn't reward per-sample
adaptivity). Continual-safe, real-data-confirmed. The cheap brain is **finished**; the project pivots to Phase 6
(GD-side optimization). **Owed (with the author):** the public `README.md` + `phase5-report.md`, the
`idea/main.ideas.v1.md` S9 delta, the phase-renumber doc sync. **Experiment ladder P5.0–P5.9 COMPLETE.**
