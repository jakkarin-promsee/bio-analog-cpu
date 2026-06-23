# `skill/simulation-experiments.md` — running experiments: mental-model map

> **Use this when** you're about to write a test, run an experiment from the Phase-1 ladder, or
> interpret/report a result. This is the **science** side.
>
> Router, not procedure. `CLAUDE.md` is always on; this adds the experiment layer.
> **New here? Read `skill/project-explore.md` first** — the concept entry point.
>
> **Migrated to draft 6.0 (June 2026).** The old `§20` ten-phase campaign, the `H1` attribution
> hypothesis, the MVF/Ganglion-Personality framing, and `draft5.0-fossil/draft5.1-2.verify.md` are **history.** The live
> line is the **Phase-1 experiment ladder** in [`draft6.0/idea/ideas1.md`](../draft6.0/idea/ideas1.md).

## The one thing to internalize first

**Failures are data. Do NOT tune until it works** — that's how you lie to yourself. Log it, characterize it
across configs, move on. (In the old era the XOR collapse was *reported*, never hacked into passing — keep
that bar.) And you are testing **convergence, not theory**: SCFF + GD + boosting are settled; each rung's
result is one picture, not an argument.

## Read these first, in order — only the parts named

1. **[`draft6.0/idea/ideas1.md`](../draft6.0/idea/ideas1.md) → "The experiment ladder."** The live plan:
   1.0 full SCFF → 1.1 full GD → 2.x mix + middle → 3.x sleep → 4.x block chain, with the **build
   discipline** and a **pass/fail picture per rung.** Start at the rung you're on.
2. **[`draft6.0/idea/main.ideas.v1.md`](../draft6.0/idea/main.ideas.v1.md) → "Open knobs."** What each
   experiment is actually deciding (front:back plasticity ratio, gate threshold, sleep cadence, …).
3. **[`draft6.0/ref/`](../draft6.0/ref/README.md)** (+ **[`ref2/`](../draft6.0/ref2/README.md)** for the
   Phase-3 depth-direction survey) — the paper behind whatever you're testing (SCFF, Distance-Forward,
   BoostResNet, BYOL, LLRD; GIM/CLAPP/Mono-Forward), so you know what "working" looks like.
4. **[`draft6.0/src/phase1/result-format.md`](../draft6.0/src/phase1/result-format.md)** — the house style for
   *reporting* a result (figure catalog, median+IQR, the "calling a difference real" rule, the 6-slot read);
   applies to every phase. For *finished* results, read the narratives: `draft6.0/src/stage1-report.md` + each
   `phaseN/phaseN-report.md`, with `draft6.0/src/ref-report/` as the glossary.

## The mindset (governs every run)

- **One thing changed per experiment.** Exactly one variable between two runs. Multi-variable = uninterpretable.
- **Multiple seeds.** Standard set: `[42, 137, 271, 314, 1729]`. Report **median + IQR**, not a single run.
- **Ideal first.** Ideal deterministic operators (floats) until the rung converges; **defer fallbacks**
  (EMA-view, margin loss, Adam accumulators) and **defer analog/PVT realism** until the baseline is
  characterized — they're remediation tested *after* baseline behavior, not bolted on first.
- **The sim measures correctness, not speed.** There's no clock; the analog charge-wait is invisible. "Sim
  fast" ≠ "chip fast."

## Invariants to log every run

For draft 6.0, watch: **convergence / loss-slope**, **dead-unit fraction**, **ceiling / goodness
saturation**, and — once chained — **inter-block drift / SCFF cluster-churn.** A run that violates one is a
finding, not a nuisance.

## The build discipline (decided 2026-06-19)

- **Walk one spine — the neocortex (SCFF + GD).** Build straight down the ladder; don't open a second track.
- **The hippocampus LUT is a service, not a parallel brain.** It feeds SCFF its negatives (**stub it first**
  — a random partner from the current batch, no memory) and holds the replay history for sleep (where it
  becomes a real organ, **at 3.2**). Never build it as its own milestone.
- **The phase-2 menu** ([`draft6.0/future-ref/`](../draft6.0/future-ref/README.md) topics 1–6) **stays
  closed** — compass for later organs, not this build.

## Constraints

- Don't change the architecture to make a test pass. A test that fails is a result.
- **Architecture changes are decisions, not experiments** — they move the spine only on a result, via
  `skill/architecture-research.md`, not mid-run.
- Don't re-import the dead 5.1 frame (attribution, `|a·W|` diffusion, H1) — it's not what's being tested.

## Where to record

The experiment workspace is **`draft6.0/src/phaseN/`** (one folder per phase). Each phase carries a `README.md`
(the codeable spec), `expK/experiment-K.md` run-cards (the 6-slot reads), a `phaseN-summarize.md` (synthesis) +
`RESULTS.md` (the scalar ledger), and a reader-facing `phaseN-report.md` (the narrative, figures inline). The
figure/table house style is pinned in **`draft6.0/src/phase1/result-format.md`** (applies to every phase).

- **Plan vs record.** The *plan/whiteboard* is `ideas1.md` (the ladder) + `main.ideas.v1.md` (status) + the
  `phase1/README.md` (the experiment spec). The *record* (what we ran + found) lives in a folder per
  experiment under `draft6.0/src/phase1/` (`exp0/`, `exp1/`, `exp2a/`, `exp2b/`, `exp2c/`, `exp3/`), each an
  `experiment-{n}.md`: question → setup → run → result/figures → read → decision.
- **Write-boundary.** Status in `main.ideas.v1.md` ("Status"); detail in the experiment folder. Don't edit
  the *derivation* chapters of `ideas1.md` to record a run's outcome — that's a decision, not a log.
- **Figures:** commit the summary plots the logs reference; git-ignore raw sweeps.

## Where the work is now (2026-06-23)

- **Stage 1 (Phases 1–4) is complete and written up.** Phase 1 (the cell + its continual home), Phase 2
  (energy-SCFF can't earn depth), Phase 3 (the objective reframe — contrast + coordination, **adopted**),
  Phase 4 (the capability map). Synthesis in each `phaseN-summarize.md` + `RESULTS.md`; reader-facing write-up
  in `draft6.0/src/stage1-report.md` + `phaseN/phaseN-report.md` + the `ref-report/` glossary.
- **Verdict so far:** a substrate-native **continual** learner that composes depth cheaply — **not** a
  static-accuracy competitor. Adopted cell = `[contrast (InfoNCE) + coordination w≥2] SCFF bulk +
  sleep-consolidated GD readout`.
- **The live line is Phase 5 = optimization** (the sleep-cadence + Ch7-gate maintenance loop, tuned against
  *this* cell's measured drift; + the train-with-noise and natural-data follow-ups Phase 4 flagged).

## Traps

- Tuning hyperparameters until a rung passes (forbidden — failures are data).
- Single-seed conclusions.
- Changing two things and not knowing which moved the result.
- Reading a stable ideal sim as a working chip (no PVT yet).
- Building the hippocampus LUT as a parallel track instead of stubbing its negative role until sleep (3.2).

## Done means

- The run obeys the methodology (one variable, multi-seed, invariants logged).
- A failure is *recorded as data* (multi-config characterization), not tuned away.
- The result has a record (under `draft6.0/src/phase1/`) and `main.ideas.v1.md` status points to it.
