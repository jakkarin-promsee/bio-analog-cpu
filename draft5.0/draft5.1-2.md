# Bio-Inspired Analog Neural Compute Architecture — Part 2: Experimental Campaign & Future Tracks

> A continuous-time analog substrate with on-chip hierarchical credit assignment.
> Specification and experimental campaign.
> **Part 2 of 2.** See `draft5.1-1.md` for Part 1 (architecture, mechanism, hypotheses, math targets, open questions, protected list, glossary).

> **⚠ Status (2026-06-01) — this is a _rough pre-plan_, not the committed campaign.** The §20/§21 phases below were sketched with Opus 4.7 to picture what the whole project _could_ look like end-to-end. The author's committed intuition lives in `draft5.1-1.md` (the locked architecture); this Part 2 is being **re-drafted intuition-first, phase by phase**, in `draft5.1-2.verify.md` — each phase shaped by the previous phase's data, and expected to keep shifting. Treat the phases / run-counts / effort here as an _illustrative scaffold_, not fixed targets. **For the live plan, read `draft5.1-2.verify.md`.** This file stays for reference.
>
> **Scope of "rough":** it's the *phase schedule* (§20.0–§20.16 — which phases, run-counts, order) that's being re-drafted. The *methodology* sections here remain the working reference until re-drafted: **§20.2** (rules), **§20.17** (promotion), **§20.18** (negative-result protocols), **§20.19** (reproducibility), and all of **§21** (future tracks).

---

## About this part

This document contains §20 (Simulation Plan) and §21 (Future Tracks) of the canonical specification. These two sections were separated from Part 1 to keep each file at a length that converts cleanly to PDF and other formats.

**What's in Part 1** (`draft5.1-1.md`):

- §0 Reading Guide
- §1 The Bet — project framing, biological inheritance, related work positioning, methodology
- §2 The Central Idea — attribution-based hierarchical diffusion (the mechanism)
- §3 End-to-End Worked Example — single Ganglion XOR forward+backward trace
- §4 Architectural Overview — the five-level hierarchy
- §5 Naming and Disambiguation
- §6–§13 The modules — Scap, Ganglion, Column, Lobe, SpecialGeneralist, Limbic Loop, Commissure, Brainstem
- §14–§16 Cross-cutting mechanisms — residuals, analog robustness, routes
- §17 Hypotheses — H1 through H11
- §18 Math to Justify
- §19 Open Questions
- §22 What Not To Touch (protected list)
- §23 Glossary

**What's in this Part 2:**

- §20 Simulation Plan — Detailed Experimental Campaign (operator sanity → ten phases → reproducibility infrastructure → effort budget)
- §21 Future Tracks — Optional and Deferred Mechanisms

**Cross-references.** Section numbers are preserved from the unsplit version (`draft-journey/draft5.1-full.md`, kept for reference). References like `§6.3` or `§17` point to Part 1; references like `§20.18` or `§21.5` point to Part 2. Both directions of reference occur naturally — the experimental campaign tests claims made in Part 1, and the architecture's hypotheses reference the phases that test them.

---

## 20. Simulation Plan — Detailed Experimental Campaign

This section is the operational plan for taking the architecture from spec to data. The theoretical work is locked (§1–19); from here, every remaining decision is driven by experiment, not intuition.

The plan is built around ten phases plus support infrastructure. Each phase answers a specific question. Each experiment changes exactly one variable. Each phase has hard exit criteria.

> **Style note:** the architecture has 11 testable hypotheses (H1–H11) and four critical failure modes (dead-weight collapse, momentum saturation, Activity vs Relevance, PVT drift). The simulation plan is structured so every one of these gets measured concretely, not just talked about.

### 20.0 Phases at a glance

The full campaign in one table, before the detail:

| Phase       | What                      | Hypothesis          | Runs       | Effort    | Status                        |
| ----------- | ------------------------- | ------------------- | ---------- | --------- | ----------------------------- |
| 20.1 MVF    | One-hour sanity gate      | H1 (preview)        | 1          | < 1 day   | Mandatory before any phase    |
| 1 (§20.7)   | Operator sanity           | —                   | unit tests | 1 week    | Mandatory                     |
| 2 (§20.8)   | Single Ganglion baseline  | **H1, H7, H8, H10** | 60         | 2 weeks   | Mandatory — the central test  |
| 3 (§20.9)   | Ablation suites           | refines H1, H7, H8  | 80         | 2 weeks   | Mandatory                     |
| 4 (§20.10)  | Column composition        | H1 at scale, H6     | 15         | 1.5 weeks | Mandatory                     |
| 5 (§20.11)  | Multi-parent Lobe DAG     | **H9, H11**, H6     | 30         | 2 weeks   | Mandatory                     |
| 6 (§20.12)  | SpecialGeneralist         | **H2**              | 25         | 2 weeks   | Mandatory                     |
| 7 (§20.13)  | Limbic Loop two-timescale | **H3**              | 50         | 3 weeks   | Mandatory                     |
| 8 (§20.14)  | PVT robustness            | §15 defenses        | 45         | 3 weeks   | Mandatory                     |
| 9 (§20.15)  | Synaptic Drift            | H4                  | 10         | 2 weeks   | Conditional on Phases 2, 6, 7 |
| 10 (§20.16) | 256-Ganglion scale        | **H5**              | 3          | 3 weeks   | Conditional on Phase 7        |

**Total mandatory effort: ~16 weeks (~4 months) of solo evening/weekend work.** Risk-adjusted ~6 months. Conditional Phases 9–10 add another ~5 weeks if all earlier phases succeed.

**Bold hypotheses** are the load-bearing claims — if their phase fails, the architecture itself needs revisiting. Other hypotheses are tested but don't kill the project if they fail.

### 20.1 Minimum Viable Falsification — start here

**The fastest possible test of H1.** Before any phase, run this to fail fast if attribution doesn't work at all.

**Setup:** single Ganglion, Task A (XOR — defined in §20.4), full ideal configuration, 1 seed.

**Expected runtime:** < 1 hour.

**Pass criterion:** loss decreases monotonically over training; final loss < 50% of initial loss.

**Fail action:** stop. Debug the operator layer (Phase 1) or the update equation (§6.3) before proceeding. Most likely failure: a sign error or measurement-direction bug.

This is a sanity gate, not a hypothesis test. It catches infrastructure bugs in hours instead of days. **Build infrastructure to support this run before building infrastructure for anything else.**

### 20.2 Methodological Principles

These rules govern every experiment, regardless of phase.

**Rule 1: One thing changed per experiment.** Each run differs from its comparison run in exactly one variable. If you change residual + ForwardSign + initialization simultaneously, you can't tell which one mattered. Discipline this from day one — it's the single biggest determinant of whether the campaign produces clear answers.

**Rule 2: Multiple seeds per cell.** Each (configuration, task) pair runs with N ≥ 5 random seeds. Report median + interquartile range, not single-run results. Attribution-based learning is stochastic enough that single-run comparisons lie regularly.

**Rule 3: Controlled variables are explicit.** For every comparison, lock these unless one is the variable under test:

- Random seed list (same N seeds across compared cells)
- Task and dataset split
- Initialization scheme
- Total Scap count
- Total training steps
- Pulse-width schedule (learning-rate-equivalent)
- Precision budget per level
- Evaluation metric

**Rule 4: Invariants checked everywhere, not in dedicated suites.** Loss conservation epsilon, dead-weight fraction, ceiling-saturation fraction, and clip rate are logged in _every_ experiment. There is no separate "loss conservation test" — every run validates it as a side effect. See §20.5.

**Rule 5: Failures are data.** A configuration that fails to converge is a result. Log it, report it, move on. Don't tune until it works — that's how you lie to yourself about what the architecture can do.

**Rule 6: Defer all fallbacks until baseline is characterized.** Path 0 noise floor, adaptive decay, Adam-style v*t, anti-Hebbian gating — none of these go into Phase 2. They are tested as remediations \_after* the baseline failure mode is observed. Otherwise you can't distinguish "the baseline works" from "the fallbacks rescued it."

**Rule 7: Defer PVT realism until the ideal model converges.** Phase 8 introduces PVT. Phases 1–7 use ideal deterministic operators. Otherwise you can't tell baseline failures from PVT-induced failures.

**Rule 8: Architecture changes are decisions, not experiments.** If a phase's data suggests changing the architecture (e.g. promoting tanh from §21 to baseline), that decision goes through the §20.18 promotion criteria. Architecture doesn't drift silently.

### 20.3 Simulation Infrastructure

Before any phase runs, the code base needs structure. This subsection specifies the minimum software architecture.

**Language and stack:**

- Python 3.11+
- NumPy for arrays; PyTorch _only_ for SGD baseline comparison (we do not use autograd for the attribution-based path).
- Matplotlib for visualization (no fancy dashboards).
- pytest for unit tests (Phase 1 operator sanity).

**Core class hierarchy:**

```
Scap                          # leaf storage
  ├ weight_cap (float)
  ├ sign_SRAM (bool)
  ├ forward_sign_SRAM (bool)
  ├ refill_SRAM (uint8)
  ├ momentum_SRAM (uint16)
  ├ community_routing (dict)
  └ methods: forward_contribute(), backward_update()

Ganglion                       # one 2-3-3-2 unit
  ├ 29 Scaps + bias Scaps
  ├ measurement_caps (29 floats)
  ├ residual_bypass_enabled (bool)
  ├ activation_type ('relu' | 'tanh')
  └ methods: forward(input), measure_contributions(), distribute_share()

Column                         # sequential Ganglia + translate ALUs
  ├ Ganglia
  ├ TranslateALUs
  ├ global_caps (intermediate state)
  └ methods: forward(input), distribute(share)

Lobe                           # multi-branch DAG
  ├ Columns (graph structure)
  ├ distribution_memory (per-Column SRAM)
  ├ Dummy_Scap (per Column)
  └ methods: forward(input), distribute(share)

LimbicLoop                     # top-level recurrent system
  ├ cortex_lobe, hippocampus_lobe, commissure
  ├ input_reducer (fixed)
  ├ decay_factor
  └ methods: forward_clock(input), distribute_clock(loss)

Brainstem                      # central controller
  ├ adc, label_buffer
  ├ per_lobe_gates (clocks)
  ├ range_sensitivity_mode
  └ methods: compute_loss(), broadcast(), schedule_autozero()
```

**Logging infrastructure:**

Every experiment writes one JSON log per run containing:

- Configuration hash (every parameter)
- Seed
- Per-step metrics (loss, dead-weight count, ceiling-saturation count, conservation epsilon per level)
- Final state (weight distribution, momentum distribution)
- Wall-clock time

Logs go to a versioned directory (`runs/<phase>/<config_hash>/<seed>.json`). Never overwrite.

**Visualization standards:**

Each phase produces one summary report (Markdown + figures) auto-generated from logs:

- Convergence curve (median + IQR across seeds)
- Dead-weight fraction over training
- Ceiling-saturation fraction over training
- Loss conservation epsilon per level
- Weight distribution histograms (start vs end of training)
- Per-Scap weight trajectories (sampled, not all)

**Regression suite:**

Phase 1 unit tests must continue passing throughout all later phases. CI-style check before any phase starts: "do the operators still work?" Catches infrastructure regressions early.

### 20.4 Task Operationalization

Tasks need concrete definitions. "XOR" is ambiguous in an analog substrate.

**Task A: Analog XOR.**

- 4 input patterns: `(−1, −1), (−1, +1), (+1, −1), (+1, +1)` as voltage levels.
- 4 target outputs: `−1, +1, +1, −1`.
- 100 epochs of 4 samples each (400 forward passes).
- Loss: MSE.
- Used in: Phase 2 (single Ganglion baseline).

**Task B: Sine regression.**

- Input: x ∈ [0, 2π] as voltage.
- Target: sin(x) as voltage.
- 200 samples per epoch, 50 epochs (10,000 forward passes).
- Loss: MSE.
- Used in: Phase 2.

**Task C: Two-moons classification.**

- 200 2D points in two interlocking moon shapes.
- Target: 2D output, one-hot.
- 100 epochs of 200 samples (20,000 forward passes).
- Loss: MSE (cross-entropy deferred until softmax is implemented).
- Used in: Phase 2.

**Task D: Multi-parent direction-conflict probe.**

- A synthetic two-input task where one input wants output up and another input wants output down, sometimes simultaneously.
- Used in: Phase 5 (specifically tests H11 — Forward_Sign resolves direction conflict).
- Construction: input1 ~ Bernoulli(0.5) drives target_a = +1 when active; input2 ~ Bernoulli(0.5) drives target_b = −1 when active; final target = target_a + target_b. Half the samples have conflicting inputs.

**Task E: Sequence prediction with cue completion.**

- Memorize K = 4 short sequences of length 8.
- At test time, present first 4 steps; ask Limbic Loop to complete remaining 4.
- Used in: Phase 7 (recurrence / Limbic Loop test).
- Metric: completion accuracy on held-out cues.

**Task F: Image-moving stimulus (very late, optional).**

- 1D sequence of pixels moving across a small "retina" (10 pixels).
- Predict next-frame pixel intensities.
- Used in: Phase 7+ if everything else works. This is the "human eye mechanism" stretch goal. Will probably break first attempts — that's expected.

### 20.5 Continuous Invariant Monitors

These four monitors run in every experiment, every phase. They are not separate tests. They are the always-on health check.

| Monitor                         | What it measures                                                     | Pass criterion           | Fail action                                     |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------ | ----------------------------------------------- |
| **Loss conservation epsilon**   | `\|Σ children_shares − parent_loss\|` per level, every backward pass | ε < 5% per level         | Flag run; report; do not auto-fix               |
| **Dead-weight fraction**        | `(count Scaps with \|weight_cap\| < 1% of range) / total Scaps`      | < 5% by end of training  | Flag run; escalate to Path 0 in §20.18          |
| **Ceiling-saturation fraction** | `(count Scaps with momentum_SRAM ≥ 99% max) / total Scaps`           | < 5% by end of training  | Flag run; consider log-momentum (§21)           |
| **T_max clip rate**             | `(count Scaps hitting T_max in last forward) / total Scaps`          | < 20% by end of training | Flag run; auto-trigger Range Sensitivity (§7.5) |

These run _as part of the simulation engine_, not as separate tests. Failure of any monitor in any run goes into the JSON log and is reported in the phase summary.

### 20.6 Hypothesis-to-Experiment Map

| Hypothesis                                       | Primary phase          | Secondary phases                           | Pass criterion                                                                |
| ------------------------------------------------ | ---------------------- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| H1 — Attribution converges                       | Phase 2                | Phase 4, 5, 7 (re-validated at each scale) | Converges on 2/3 Task A/B/C within 10× SGD steps                              |
| H2 — SpecialGeneralist > plain reuse             | Phase 6                | —                                          | Beats plain G-reuse on Task C by ≥ 10% final loss                             |
| H3 — Two-timescale Limbic Loop converges         | Phase 7                | —                                          | Stable recall on Task E with k ≥ 4                                            |
| H4 — Synaptic Drift accelerates convergence      | Phase 9 (conditional)  | —                                          | ≥ 20% faster convergence on Task C                                            |
| H5 — No weight LDR/STR during operation          | Phase 10 (conditional) | All phases (asserted in infra)             | Asserted by code structure                                                    |
| H6 — Loss conservation bounded                   | All phases             | —                                          | ε < 5% per level always                                                       |
| H7 — Dead-weight collapse bounded                | Phase 2                | All phases                                 | < 5% dead Scaps                                                               |
| H8 — Residuals reduce dead-weight                | Phase 3 (ablation)     | —                                          | Residual-on has < 50% the dead-weight fraction of residual-off                |
| H9 — Multi-branch Lobe outperforms sequential    | Phase 5                | —                                          | DAG-Lobe beats sequential-Column on Task C by ≥ 10%                           |
| H10 — Physical Saturation bounds winner-take-all | Phase 2                | —                                          | Weight saturation rate within 20–50% of training time                         |
| H11 — ForwardSign resolves multi-parent conflict | Phase 5                | —                                          | With ForwardSign, direction-conflict task converges; without, fails or stalls |

If a hypothesis fails its pass criterion, that's a real result. See §20.19 negative-result protocols.

### 20.7 Phase 1 — Operator Sanity

**Goal:** verify every analog primitive matches its ideal mathematical counterpart within the discrete-time simulation.

**Simulation type:** discrete-time Python at ~1 ms resolution. Continuous-time analog behavior approximated by Euler integration of cap voltages. Real-time SPICE simulation deferred to §21.

**Tests:**

- Add op-amp vs ideal add: `out = a + b`, measure error.
- Multiply op-amp vs ideal multiply: `out = a × b`, measure error.
- ReLU op-amp vs ideal ReLU.
- Capacitor charge dynamics: `v(t) = V × (1 − e^{−t/RC})` with constant current, measure deviation from ideal exponential.
- Time-to-threshold conversion: verify `clocks_to_cross(A%, B%) ∝ 1/current` for known current, and that the post-conversion stored value is linear in current.
- PWM update: verify weight changes by `pulse_width × momentum × direction` with correct sign.

**Metrics:**

- Error per operator (max, mean, std).
- Monotonicity: stronger input → stronger output, always.
- Saturation behavior at supply rails.
- Sensitivity to small noise.

**Implementation:** Python unit tests via pytest. Each operator is a class. Each test is a function.

**Exit criterion:** all operators pass unit tests with errors below 0.1% of expected output. Document worst-case error for each.

**Effort estimate:** 1 week (40 hours).

### 20.8 Phase 2 — Single Ganglion (the central test)

**Goal:** validate H1 (attribution converges), H7 (dead-weight bounded), H8 (residuals help), H10 (physical saturation works), and characterize Activity vs Relevance gap.

**This is the make-or-break phase.** If attribution-based learning doesn't work on a single Ganglion, nothing higher will. Spend serious time here.

**Configuration matrix (4 cells):**

| Cell   | Residual | ForwardSign | Notes                                                    |
| ------ | -------- | ----------- | -------------------------------------------------------- |
| Cell A | On       | On          | Full ideal                                               |
| Cell B | Off      | On          | Tests H8                                                 |
| Cell C | On       | Off         | Tests H11 partial (degenerate under ReLU but log anyway) |
| Cell D | (SGD)    | (n/a)       | Vanilla SGD baseline on same topology                    |

5 seeds × 4 cells × 3 tasks (A, B, C) = **60 runs**.

**Metrics per run:**

- Final loss
- Steps to convergence (loss within 5% of asymptote)
- Cosine similarity between attribution-update-vector and SGD-update-vector (averaged over training)
- Dead-weight fraction at end
- Ceiling-saturation fraction at end
- Weight-magnitude saturation rate (how many forward passes until first Scap hits 90% rail)
- Activity vs Relevance gap: for each Scap, log `|a · W|` (claimed share) vs Δloss when that Scap is ablated. Wide gap = relevance problem.

**Exit criteria:**

- Cell A converges on ≥ 2/3 tasks, with median final loss within 10× of Cell D (SGD).
- Dead-weight fraction < 5% in Cell A on all tasks.
- Ceiling-saturation < 5% in Cell A on all tasks.
- Cell B (no residual) shows ≥ 2× dead-weight fraction vs Cell A — validates H8 directionally.
- Physical saturation reaches 50% of Scaps between 20% and 50% of training duration — validates H10.

**Effort estimate:** 2 weeks (80 hours). Includes diagnostic harness, visualization, and writing the phase report.

**If Phase 2 fails:** see §20.19 negative-result protocols. Likely paths: enable Path 0 noise floor → retry; if still failing, escalate to Path 1 or 2.

### 20.9 Phase 3 — Ablation Suites

**Goal:** isolate the contribution of each mechanism beyond the four-cell matrix in Phase 2.

**Three ablation suites:**

**Suite 3a: Momentum dynamics**

| Cell | EMA α | Floor-at-1 | Momentum bits |
| ---- | ----- | ---------- | ------------- |
| 3a-1 | 3/4   | Yes        | 16            |
| 3a-2 | 7/8   | Yes        | 16            |
| 3a-3 | 15/16 | Yes        | 16            |
| 3a-4 | 3/4   | No         | 16            |
| 3a-5 | 3/4   | Yes        | 8             |
| 3a-6 | 3/4   | Yes        | 24            |

5 seeds × 6 cells × Task C = **30 runs**. Resolves Open Questions 5 (ceiling), 7 (precision).

**Suite 3b: Initialization**

| Cell | Magnitude init    | Sign init | Momentum init |
| ---- | ----------------- | --------- | ------------- |
| 3b-1 | Uniform 10% range | Random    | Zero          |
| 3b-2 | Uniform 50% range | Random    | Zero          |
| 3b-3 | Xavier-equivalent | Random    | Zero          |
| 3b-4 | Uniform 10% range | All +     | Zero          |
| 3b-5 | Sparse (50% zero) | Random    | Zero          |

5 seeds × 5 cells × Task C = **25 runs**. Resolves Open Question 18.

**Suite 3c: Residual variants**

| Cell | Residual location            | Bypass scaling α |
| ---- | ---------------------------- | ---------------- |
| 3c-1 | L1→L4 (default)              | 1.0              |
| 3c-2 | L1→L4                        | 0.9              |
| 3c-3 | L1→L4                        | 0.5              |
| 3c-4 | Per-layer (where dims match) | 1.0              |
| 3c-5 | No residual (control)        | —                |

5 seeds × 5 cells × Task C = **25 runs**. Resolves Open Question 19.

**Total Phase 3:** 80 runs.

**Exit criteria:**

- Suite 3a identifies an EMA α that minimizes both dead-weight and ceiling-saturation. Lock that α.
- Suite 3b identifies an initialization that converges fastest with lowest dead-weight. Lock that init.
- Suite 3c confirms residual reduces dead-weight; identifies best α scaling.

**Effort estimate:** 2 weeks.

### 20.10 Phase 4 — Column Composition

**Goal:** verify that hierarchical diffusion through Column-local buses works as designed, and that translate ALUs (learnable, §8.3) train.

**Configuration:**

- Single Column: input → translate ALU (4:6) → Ganglion → translate ALU (6:4) → output
- Compare against single Ganglion of same total Scap count

**Configuration matrix:**

| Cell | Translate ALUs         | Comparison                               |
| ---- | ---------------------- | ---------------------------------------- |
| 4-1  | Learnable              | Single-Ganglion baseline (matched Scaps) |
| 4-2  | Frozen (random)        | Single-Ganglion baseline                 |
| 4-3  | Learnable, sparse-init | Single-Ganglion baseline                 |

5 seeds × 3 cells × Task C = **15 runs**.

**Exit criteria:**

- Column converges on Task C with conservation ε < 5% at every level.
- Learnable translate ALUs measurably outperform frozen — validates translate-ALU learnability.
- Time-per-forward-pass scales linearly with depth (no exponential blowup).

**Effort estimate:** 1.5 weeks.

### 20.11 Phase 5 — Multi-Parent Lobe DAG

**Goal:** validate H9 (DAG > sequential), H6 under multi-parent (loss conservation holds), H11 (ForwardSign resolves direction conflict).

**Three configurations:**

**Config 5a: DAG vs sequential expressivity (H9)**

- DAG-Lobe: 3 Columns with skip-connections (Column1 → Column2 + Column3; Column2 → Column3)
- Sequential-Lobe: 3 Columns in a chain, matched Scap count
- Task: C (two-moons)

5 seeds × 2 cells × Task C = **10 runs**.

**Config 5b: Multi-parent loss conservation (H6)**

- DAG-Lobe with two parents feeding one child
- Track conservation ε at the multi-parent child
- Compare to single-parent baseline

5 seeds × 2 cells × Task C = **10 runs**.

**Config 5c: Direction conflict (H11)**

- DAG with two parents that pull in opposite directions on Task D
- With ForwardSign vs without

5 seeds × 2 cells × Task D = **10 runs**.

**Exit criteria:**

- 5a: DAG beats sequential by ≥ 10% final loss on Task C.
- 5b: Multi-parent conservation ε < 5% (matches single-parent).
- 5c: With ForwardSign, Task D converges; without ForwardSign, stalls or fails. **This is the cleanest test of H11.**

**Effort estimate:** 2 weeks.

### 20.12 Phase 6 — SpecialGeneralist

**Goal:** validate H2 (gated G-reuse > plain reuse > Reservoir-G).

**Configurations × mask policies:**

| Cell | G-reuse type           | Mask source | Mask overlap       |
| ---- | ---------------------- | ----------- | ------------------ |
| 6-1  | Plain reuse (no mask)  | —           | —                  |
| 6-2  | SpecialGeneralist      | Hardcoded   | Mutually exclusive |
| 6-3  | SpecialGeneralist      | Hardcoded   | 50% overlap        |
| 6-4  | SpecialGeneralist      | Learned     | Mutually exclusive |
| 6-5  | Reservoir-G (G frozen) | —           | —                  |

5 seeds × 5 cells × Task C = **25 runs**.

**Exit criteria:**

- SpecialGeneralist (any mask variant) beats plain reuse by ≥ 10% final loss.
- If SpecialGeneralist fails to beat plain reuse: fall back to Reservoir-G; document failure of H2.
- Identify best mask source and overlap policy; lock for Phase 7.

**Effort estimate:** 2 weeks.

### 20.13 Phase 7 — Limbic Loop with Two-Timescale Learning

**Goal:** validate H3 (two-timescale Limbic Loop converges), characterize recurrence stability, identify timescale parameters.

**Configuration scan:**

| Cell | Cortex update    | Hippocampus update | Commissure update | Decay factor |
| ---- | ---------------- | ------------------ | ----------------- | ------------ |
| 7-1  | Every clock      | Every 4 clocks     | Every 16 clocks   | 0.9          |
| 7-2  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.9          |
| 7-3  | Every clock      | Every 16 clocks    | Every 64 clocks   | 0.9          |
| 7-4  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.8          |
| 7-5  | Every clock      | Every 8 clocks     | Every 32 clocks   | 0.95         |
| 7-6  | Cortex-only      | (no Hippocampus)   | (no Commissure)   | (n/a)        |
| 7-7  | Hippocampus-only | (no Cortex)        | (no Commissure)   | (n/a)        |

5 seeds × 7 cells × Task E = **35 runs**.

**Hippocampus consolidation pulse-width policy (sub-sweep):**

- Within best-k cell: test three policies (same pulse / k× pulse / accumulated loss).

5 seeds × 3 policies × Task E = **15 runs**.

**Total Phase 7:** 50 runs.

**Exit criteria:**

- 7-1 to 7-5 converge stably on Task E.
- Best (k, M, decay) configuration identified.
- 7-6 (Cortex-only) underperforms — validates that Hippocampus contributes.
- Best consolidation pulse-width policy identified.

**Effort estimate:** 3 weeks.

### 20.14 Phase 8 — PVT Robustness

**Goal:** validate that the analog robustness mechanisms (§15) preserve performance under realistic PVT.

**Now and only now, add PVT realism to the simulator.**

**Configuration matrix:**

| Cell | Process σ | Thermal | Diff Pair | Dummy Scap | Auto-Zero | Current Mirror | Range Sens |
| ---- | --------- | ------- | --------- | ---------- | --------- | -------------- | ---------- | -------------------------- |
| 8-1  | 0         | None    | On        | On         | On        | On             | On         | Baseline (no PVT)          |
| 8-2  | 2%        | Mild    | On        | On         | On        | On             | On         | Light PVT, full defenses   |
| 8-3  | 5%        | Strong  | On        | On         | On        | On             | On         | Heavy PVT, full defenses   |
| 8-4  | 5%        | Strong  | Off       | On         | On        | On             | On         | Ablate Diff Pair           |
| 8-5  | 5%        | Strong  | On        | Off        | On        | On             | On         | Ablate Dummy Scap          |
| 8-6  | 5%        | Strong  | On        | On         | Off       | On             | On         | Ablate Auto-Zero           |
| 8-7  | 5%        | Strong  | On        | On         | On        | Off            | On         | Ablate Current Mirror      |
| 8-8  | 5%        | Strong  | On        | On         | On        | On             | Off        | Ablate Range Sensitivity   |
| 8-9  | 5%        | Strong  | Off       | Off        | Off       | Off            | Off        | All defenses off — control |

5 seeds × 9 cells × Task C = **45 runs**.

**Exit criteria:**

- Cell 8-3 (full defenses, heavy PVT) shows < 20% performance drop vs Cell 8-1.
- Each ablation (8-4 through 8-8) shows measurable degradation — validates each defense.
- Cell 8-9 (no defenses) catastrophically fails — confirms defenses are doing real work.

**Effort estimate:** 3 weeks.

### 20.15 Phase 9 — Synaptic Drift (conditional)

**Goal:** validate H4. Activate only if Phases 2, 6, 7 succeed.

- Add learnable 1D position SRAM per synapse in Commissure.
- Compare convergence vs fixed-topology Commissure.

5 seeds × 2 cells × Task E = **10 runs**.

**Exit criteria:** ≥ 20% faster convergence with Drift vs without.

**Effort estimate:** 2 weeks.

### 20.16 Phase 10 — Scale to 256 Ganglia per Region (conditional)

**Goal:** validate H5 and characterize scale behavior. Activate only if Phase 7 succeeds.

- Implement Route L1/L2 addressing (§16).
- Scale single region to 256 Ganglia.
- Run Task E end-to-end on full region.
- Assert weight state never leaves the substrate during operation.

3 seeds × 1 config × Task E = **3 runs** (expensive — large network).

**Exit criteria:**

- Task E runs to convergence at 256-Ganglion scale.
- Loss conservation ε stays bounded across all 5 hierarchy levels.
- No weight serialization observed during operation (asserted by code).

**Effort estimate:** 3 weeks.

### 20.17 Promotion / Demotion Criteria

When does the architecture change based on data?

**Promote to baseline (move from §21 Future Tracks to §1–19 spec):**

- Tanh activation (§21): if Phase 2 shows ReLU works _but_ Forward_Sign benefits at only 9/29 Scaps — and Phase 3 shows tanh would benefit all 29 with no convergence cost.
- Adam v*t per Scap (§21): if Phase 2 shows physical saturation alone produces > 5% ceiling-saturation \_or* fails to prevent winner-take-all (measured as: single Scap holds > 30% of total weight magnitude).
- Adaptive per-Scap weight decay (§21): if Phase 3 shows uniform decay produces > 10% dead-weight fraction even with floor-at-1 and residuals.
- Per-neuron residuals (§21): if Phase 3 residual ablation shows L1→L4 bypass insufficient (dead-weight > 5% with bypass on).

**Demote to fallback (mark as backup, simplify baseline):**

- SpecialGeneralist → Reservoir-G fallback: if Phase 6 shows SpecialGeneralist underperforms plain G-reuse on all tasks.
- ForwardSign → drop: if Phase 5c shows no measurable benefit on Task D. Saves 1 bit per Scap.

**Architectural changes require:**

- A documented Phase report showing the data.
- A draft revision (e.g. draft5.1) showing the change.
- The change goes through the §22 Protected List update process.

### 20.18 Negative Result Protocols

What to do when a phase fails its exit criteria.

**Phase 2 fails (H1 — attribution doesn't converge):**

1. Run minimum viable falsification (§20.1). Confirm not an infrastructure bug.
2. Enable Path 0 (noise floor on weight updates) — see §2.4. Re-run.
3. If still failing: enable Path 1 (strip multiplier from measurement, use `|a|` only). Re-run.
4. If still failing: the architecture's central learning mechanism may need revisiting. Stop and rethink before continuing.

**Phase 5 fails (H11 — ForwardSign doesn't help):**

1. Test with explicitly signed activations (skip ReLU at L1 input only).
2. If still no benefit: drop ForwardSign per §20.17 demotion. Document the negative result.

**Phase 6 fails (H2 — SpecialGeneralist no better than plain reuse):**

1. Try learned masks (escalate from hardcoded).
2. Try overlapping masks.
3. If still no benefit: fall back to Reservoir-G. Document.

**Phase 7 fails (H3 — Limbic Loop unstable or doesn't recall):**

1. Reduce decay factor (try 0.8 then 0.7).
2. Try fixed Commissure (no learning) instead of slow-learning Commissure.
3. If still failing: the recurrence structure may need redesign. Pause and rethink before Phase 8.

**Phase 8 fails (PVT crashes the system):**

1. Identify which defense, if any, is single-handedly necessary. Most likely Current Mirror.
2. Consider Ping-Pong substrate (§15.6) if Auto-Zeroing alone is insufficient.

**Universal failure mode:** all monitors red, no convergence anywhere. Likely a fundamental implementation bug. Stop, audit code, restart from Phase 1.

### 20.19 Reproducibility Infrastructure

**Random seeds:** every run records its seed. Standard set: `[42, 137, 271, 314, 1729]` for the 5-seed default. Use these everywhere unless an experiment specifically tests seed sensitivity.

**Configuration hashing:** every config (a Python dict of all parameters) gets a SHA-256 hash. Logs are named by hash. Identical configs collapse to one log directory across runs.

**Versioning:** simulator code is committed to git with every phase. Phase reports cite the git SHA they were run against. No "ran with code modifications I forgot to commit."

**Phase reports:** each phase produces one Markdown report with:

- Hypothesis tested
- Configuration matrix actually run
- Results tables (median + IQR per cell)
- Plots (convergence, dead-weight, conservation)
- Pass/fail vs exit criteria
- Decisions made (promote / demote / lock parameter)
- Open questions for next phase

Reports live in `reports/phase_<N>.md`. They are the project's actual memory.

### 20.20 Effort Budget Summary

Solo, evening / weekend work, Year 2 student pace.

| Phase                            | Effort estimate | Cumulative |
| -------------------------------- | --------------- | ---------- |
| 1 — Operator Sanity              | 1 week          | 1 week     |
| 2 — Single Ganglion              | 2 weeks         | 3 weeks    |
| 3 — Ablation Suites              | 2 weeks         | 5 weeks    |
| 4 — Column Composition           | 1.5 weeks       | 6.5 weeks  |
| 5 — Multi-Parent Lobe            | 2 weeks         | 8.5 weeks  |
| 6 — SpecialGeneralist            | 2 weeks         | 10.5 weeks |
| 7 — Limbic Loop                  | 3 weeks         | 13.5 weeks |
| 8 — PVT Robustness               | 3 weeks         | 16.5 weeks |
| 9 — Synaptic Drift (conditional) | 2 weeks         | 18.5 weeks |
| 10 — 256-scale (conditional)     | 3 weeks         | 21.5 weeks |

**Phases 1–8 are mandatory.** That's ~16 weeks (4 months) of work to characterize the architecture. Phases 9–10 are conditional on success of earlier phases.

**Realistic milestones:**

- Phase 2 completion = first publishable preliminary result (does attribution-based learning converge at all?).
- Phase 5 completion = architectural soundness validated (hierarchical diffusion works end-to-end on a small scale).
- Phase 8 completion = simulation-stage thesis-grade result (architecture is buildable in principle).

**Risk-adjusted timeline:** add 50% buffer. So Phase 8 completion realistically takes 6 months, not 4.

**Single biggest risk:** Phase 2 failure. If H1 doesn't converge after Path 0/1/2, the project's central architectural commitment needs revisiting. This is why §20.1 minimum viable falsification exists — to identify catastrophic failure in hours, not weeks.

---

## 21. Future Tracks — Optional and Deferred Mechanisms

### 21.1 Per-neuron residual connections

Internal residuals at every layer of the Ganglion. Requires dimension matching at every step — either projection circuits or topology change to 3-3-3-3.

### 21.2 Adaptive per-Scap weight decay

Tunable refill SRAM (§6.7) dynamically adjusted based on weight magnitude. Stronger decay on saturated Scaps; weaker on dead Scaps. Homeostasis at long timescales.

### 21.3 Local-aware update normalization

Each Scap exposes its remaining headroom; updates scaled to keep epoch-level update capacity uniform across Scaps. Connects to §21.2 via the recharge SRAM mechanism.

### 21.4 Adam-style v_t per Scap

Add a second 16-bit SRAM per Scap holding `v_t = β₂ × v_{t-1} + (1-β₂) × (pulse_width × momentum)²` — squared-update history. Effective update becomes `ΔW ∝ (pulse_width × momentum × direction) / √v_t`. Provides explicit per-Scap rate adaptation (slow already-large-update Scaps, fast under-updated Scaps).

Cost: doubles per-Scap SRAM (from ~30 to ~46 bits). Requires analog 1/√ circuit or ADC + digital divider per Scap.

**Status:** probably unnecessary. Physical Saturation (§6.6) already provides upper-bound self-limiting behavior. Promote to baseline only if Phase 2 shows saturation alone is insufficient.

### 21.5 Activation mixing — tanh instead of ReLU

Replace L2/L3 ReLU with tanh-like saturation (unclipped op-amp at supply rails). Continuous gradient everywhere. Free in hardware. **Bonus:** makes Forward_Sign_SRAM (§6.2, §6.3) carry useful information at all 29 Scaps per Ganglion (instead of just the 9 L1→L2 input Scaps). Likely promoted to baseline once Phase 2 validates the ReLU version.

### 21.6 Synaptic Drift

Each synapse has a learnable 1D address; signal scales by distance. Activate first in Commissure (§12.5). Analog-position version (capacitor + comparator ladder) is a clean future direction.

### 21.7 Engram Buffer (short-term memory)

Pure capacitor network acting as LSTM-like layer. Stacks between Cortex and Hippocampus. Not specified — revisit after H3.

### 21.8 Cell-fire (STDP)

Hebbian spike-timing-dependent plasticity for group-level rewiring. Open research thread.

### 21.9 Distributed loss compute

Each output Ganglion senses its own (prediction − label) locally. Brainstem shrinks to label-broadcaster + clock.

### 21.10 2-capacitor analog momentum

Replace 16-bit SRAM momentum with two analog capacitors using cross-multiplication storage. Eliminates ADC/SRAM at the Scap level. Post-baseline optimization.

### 21.11 Floating-gate transistor storage

Replace refilled capacitor + 8-bit SRAM with FGT (NAND-flash technology, Mythic AI's choice). Years of retention without refresh.

### 21.12 Op-amp normalizer topology

Specific circuit choice for §2.7 normalization. Multiple candidates from the analog computing literature.

### 21.13 Column-level residual bypass

Optional residual at the Column level (input → output direct path). For deep Columns.

### 21.14 Inference-only low-power mode

Disable backprop circuitry; just forward inference. Trivial mode bit.

### 21.15 Failure mode handling

Dead-Scap recovery, stuck-attractor escape, range-drift correction. Provisional: noise injection. Better mechanisms after empirical failure modes are seen.

### 21.16 SPICE / robustness simulation

After Python ideal-model converges: SPICE simulation of single Scap; noise-injected Python model calibrated against SPICE; degradation quantification.

---

_End of Part 2. See `draft5.1-1.md` for the architectural specification, hypotheses, protected list, and glossary._
