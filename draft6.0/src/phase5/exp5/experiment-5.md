# P5.5 — calibrated early-exit on the continual home: the adaptive exit is dominated → ship a fixed reader

*Inheriting the committed cell (temp0.2/w2) and P5.4 (per-depth heads Pareto-dominate all-tap on the static
headroom task), this is STOPPING MARK ① — the cost half on the home turf: on the P4.5 class-incremental stream,
does a calibrated head-confidence exit read deep-enough-per-sample to hold accuracy at lower forward
expected-compute than BOTH all-tap and the truncation floor? It does not — and the reason inverts P5.4.*

**Question.** On the continual (class-incremental) stream, does placement + a calibrated **max-softmax** exit
(class-confidence, the spine) beat all-tap **and** truncation in forward expected-compute, accuracy held (≥95% of
all-tap)? One-shot τ (calibrated on the early tasks, the ship regime) vs per-task-refit τ.

**Setup.** Committed cell (temp0.2/w2, L12·W64) trained **forward-only** through the P4.5 synthetic class-incremental
stream (10 classes / 40 clusters / 5 tasks of 2, make_gauss overlap 0.7), readouts sleep-consolidated on the full
buffer. Five readers, one forward-MACs meter (`exit_compute`): calibrated exit (one-shot/refit τ), **all-tap** (the
deployed P3.3/P4.5 readout), **truncation** (from-scratch L=peak+1, read at top — the floor), **oracle** (best-per-input
layer, the loose upper bound). τ = lowest threshold holding ≥95% all-tap acc on a calibration split **disjoint** from
test; one-shot calibrated on early classes (0–3), refit on all. 3 seeds (heaviest rung), checkpointed. Guards passed.

**Run.** 3 seeds × (L12 stream + 12 heads + all-tap + a from-scratch truncation stack), pure-numpy; wall ≈ 72 s.

**Result / figures.** *(median [IQR], n=3, accuracy @ forward kMACs/sample)*
| reader | continual acc | forward cost | note |
| --- | --- | --- | --- |
| **all-tap** (deployed) | **0.618** [0.612–0.624] | 72.5k | best deployable acc — **pooling helps on flat** |
| **truncation L2–3** (floor) | 0.547 [0.545–0.566] | **9.0k** [9.0–11.1] | 8× cheaper, −0.07 acc |
| oracle (best-per-input) | 0.869 [0.858–0.870] | 19.2k | loose 12-try upper bound (depth ~3.2) |
| **calibrated exit (one-shot τ)** | **0.479** [0.465–0.520] | 74.7k [39.8–74.9] | **DOMINATED** — worst acc, high cost |
| calibrated exit (refit τ) | 0.479 [0.465–0.535] | 74.7k | refit doesn't rescue (τR=τ1 on 2/3) |

Per-depth profile on the continual flat stream: **peak L2–3 (~0.55–0.60) → decay to ~0.45 at L12** — the decay
**reproduces on the continual home** too. INV: dead-unit ≈ 0, effective-rank 44→14, guards PASS (FD 2.1e-8).

- **EXIT-PARETO** (headline): all-tap top-right (0.62@72.5k), truncation far-left (0.55@9k), oracle high (0.87@19k,
  unreachable), and the exit **bottom-right** (0.48@75k) with a huge horizontal error bar — the calibration collapses
  to grid extremes (seed42 τ=0.25 floor → exit L1; seeds137/271 τ=0.999 ceiling → exit the **decayed** L12).

**Read (6 + 2 slots).**

1. **Claim** — On the continual flat home the calibrated max-softmax exit is **Pareto-dominated** by both fixed
   readers. STOPPING MARK ① does **not** pass under the pinned gate → the honest verdict is **ship a fixed reader**
   (all-tap for accuracy, truncation for 8× cost at −0.07 acc). The adaptive exit's premise — per-sample depth-need —
   isn't met where depth doesn't pay.
2. **Headline** — all-tap 0.618@72.5k, truncation 0.547@**9.0k** (8× cheaper, −0.07), exit **0.479**@74.7k (dominated),
   oracle 0.869@19.2k (loose). Refit τ doesn't help (τR=0.999 on 2/3). (n=3.)
3. **Figures** — EXIT-PARETO (the five readers), INV. Regen from `arrays.npz` (`pareto_*` branch).
4. **Mechanism — the inversion of P5.4 (the synthesis).** P5.4 (static **headroom**, depth pays): late layers *drift*,
   so all-tap is diluted and the single best head **wins** (placement). P5.5 (continual **flat**, depth doesn't pay):
   the per-depth heads are individually weak (~0.55) but **decorrelated** (oracle 0.87 ≫ any single 0.60), so **pooling
   (all-tap 0.62) beats every single depth** and single-head placement **loses**. The exit inherits the worse of both:
   (a) no single depth matches the pool → the CALM "95% of all-tap" bar is **unachievable by any single-depth exit** →
   calibration degenerates to grid extremes; (b) max-softmax confidence ≠ correctness on flat → when forced to exit it
   picks badly, defaulting to the **decayed L12**. The unifying law: **single-depth placement wins where one depth is
   sharply best (headroom); pooling wins where the signal is distributed across weak decorrelated depths (flat).** The
   continual **home is flat** → on the home, ship a fixed reader.
5. **Threats** — (a) the CALM bar is "95% of **all-tap**"; on a pooling-favorable task no single head can meet it *by
   construction* → the exit's disqualification is structural, not a tuning miss (a different bar — 95% of best-single,
   or absolute — might let it qualify, but the design pins this one; the structural reason **is** the finding). (b) the
   home is **flat** (make_gauss/digits — the validated A6 home); the exit's adaptivity has nothing to exploit. On a
   *compositional* continual stream (not the A6 home, not pinned) it could earn its keep — **parked, not built**
   (one-variable discipline; revisit at P5.9's assembled-cell over multiple tasks). (c) oracle 0.87 is a **loose 12-try
   union** upper bound — per-sample depth-diversity exists but a deployable gate need not reach it, and max-softmax
   demonstrably can't (the spine: confidence is a *magnitude*). A better per-sample selector is a parked
   selector/north-star problem.
6. **Decision** — **STOPPING MARK ① NOT passed under the pinned max-softmax gate.** Honest verdict: **ship a fixed
   reader on the continual home** — **truncation L2–3** = the cheap deployable (0.55@9k, **8× cost at −0.07 acc → fewer
   Scaps**), **all-tap** = max accuracy. The **adaptive exit is STRUCK** (logged as a failure card, not tuned to pass).
   The "read-cheaply" thread still delivers a cost win — **via truncation (a short stack), not adaptive placement**.
7. **Cost-honesty** — the real 80/20 cost win on the home is **truncation: 9.0k vs 72.5k forward = 8× cheaper** at −0.07
   acc. The exit's **adaptivity tax** (running heads 0..d to check the gate) makes it cost *more* than truncation even
   when it exits shallow — on flat, fixed beats adaptive. The backward (sleep) cost is a one-time consolidation,
   reported separately; P5.7 measures whether the committed temp0.2 cell keeps the A6 win at all.
8. **SCFF-completion** — the read-cheaply STOP① is **answered (pessimistic)**: no adaptive-exit win on the continual
   flat home; ship truncation/all-tap. Combined with **depth-earned PASS** (headroom, P5.1/P5.2), the two §7 verdicts
   **split** — SCFF composes the depth a task needs (headroom) and reads the home cheaply via a *short fixed* stack, but
   *not* via per-sample adaptive placement (the home is flat). **P5.6 (preservation): still LOW-VALUE** (truncation is
   the cheap fixed reader; preservation buys read-top convenience truncation already provides cheaper). **Next: P5.7**
   — the continual-safety gate decides whether temp0.2 itself is banked (it must preserve the A6 sleep-recovery win).

**Pre-submit checklist.** [x] Median [IQR], n=3 (heaviest rung). [x] "Real" rule (exit dominated 3/3; calibration
extremes per-seed shown). [x] FORWARD expected-compute meter (`exit_compute`), all readers commensurable. [x] τ
calibrated on disjoint split, one-shot (early-class shift) + refit. [x] oracle-exit upper bound + the spine risk
(confidence mis-calibrates under shift) named and realized. [x] Figures via `plot_p5.fig_exit_pareto`; regen redraws.
[x] manifest+arrays to schema. [x] Guards logged (FD 2.1e-8, equiv 0). [x] Single-threaded, checkpointed. [x] Spine:
gate = class-confidence not goodness; the failure is the selector, not a magnitude fix. [x] C5-pessimistic branch
pre-registered and taken honestly (ship truncation). [x] `RESULTS.md` row added.
