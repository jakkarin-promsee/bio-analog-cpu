# `skill/sureSkill.md` — the meta-map: what's covered, what I'm sure of, what I'm not

> This is the index to `skill/` **and** an honest confidence log. It tells the next mind two things a
> normal doc won't: which mental-model maps exist (and which are current vs historical), and **what is
> genuinely solid vs what is still unknown.** Read it to calibrate how much to trust everything else.
>
> Each map in `skill/` is a *router* (it points into `draft6.0/`, `docs/draft/*` for the detail), not a
> procedure. `CLAUDE.md` (always loaded) points here, so the right map is found for the task at hand.
>
> **Migrated to draft 6.0 (June 2026).** The old confidence log below was about the *attribution* build
> (the `draft5.0-fossil/src/` simulator, draft 5.1). It's kept, banded, as a record of what the previous build achieved —
> not as the current state. The current state is: **Stage 1 (Phases 1–4) simulated, complete, and written
> up** (see below) — the live line is now **Phase 5 = optimization.**

## The maps, and their status

| Map (`skill/`) | Use it when… | Status |
| --- | --- | --- |
| `project-explore.md` | **read first** — the concept entry point: how to read the project + the corrections that are wrong here | ✅ 6.0 |
| `architecture-research.md` | proposing changes, triaging ideas, scope/scope-creep calls | ✅ 6.0 |
| `simulation-experiments.md` | writing tests, running a Phase-1 rung, interpreting results | ✅ 6.0 |
| `workflows.md` | the recurring moves (orient / checkpoint / commit-progress / double-check) | ✅ 6.0 |
| `sureSkill.md` | this meta-map / index | ✅ 6.0 |
| `simulator-code.md` | editing the simulator | ⚠️ **historical** — describes the old `draft5.0-fossil/src/` attribution sim; the **6.0 behavioral sim is now written** in `draft6.0/src/phase{1,2,3,4}/` (numpy SCFF+GD+probes), but this map still points at the old one |

Maps to add: a **6.0 simulator-code** map (the fresh SCFF+GD behavioral sim now exists across `draft6.0/src/phase1-4/` —
`p4lib.py` + the per-phase `pNlib`/run/plot scripts — and deserves its own code map), and later a
**docs-maintenance** map. The hardware/RTL-handoff map waits until the design re-freezes (6.0 deliberately set
the circuit aside to stabilize the math first).

---

## What I AM sure of (draft 6.0)

High confidence — the *design reasoning* is solid and the docs capture it; I could rebuild any of it.

- **The thesis and the shape.** Direction is the one expensive thing in learning → pay for it once (GD),
  keep the rest cheap (SCFF). Two brains: a label-free local SCFF front (~80%), a small precise GD back
  (~20%), chained as residual boosting blocks, threshold-gated, sleep-consolidated over a hippocampus LUT.
  Each call has a paper behind it (`draft6.0/ref/`), and the internal logic is consistent (`ideas1.md`
  chapters each solve the prior one's problem).
- **The substrate (unchanged across the pivot).** The Scap (a *wire*, not a neuron), the crossbar MAC,
  mono-forward dual-rail (two worlds through one shared weight crossbar; only the cheap activation buffers
  double), resident-weight, free physical L2 from under-refill. This survived from the attribution era intact.
- **The build discipline.** Walk one neocortex spine; the hippocampus LUT is a *service* (stub negatives,
  real at sleep 3.2), not a parallel brain; test convergence, not theory; phase-2 menu closed.
- **The deeper why.** The brain is heterogeneous and unsimulable 1:1; ML cheats it by projection; so build
  organ by organ. And the soul: truth corrects what's honest (the missing sign that killed draft 5 is the
  same mechanism that rebuilt it). `docs/essence/the-essence.md`.
- **The collaboration model.** `docs/draft/project-personal.md` — mechanism-first, no hedging, incubation,
  the commit-signals, the "we."
- **The empirical spine (Phases 1–4 ran, 2026-06-20 → 22).** The hybrid converges and the **continual win is
  real and robust** (sleep recovers what online-BP catastrophically forgets — Phase 1 exp4, P3.3, P4.5 across
  difficulty). **Energy-goodness can't earn depth** (Phase 2), but **contrast (InfoNCE) + cross-layer
  coordination can** and is the **adopted** objective (Phase 3, supersedes `Σh²`). The **capability map**
  (Phase 4) places it: a *substrate-native continual learner, not a static-accuracy competitor* — wins
  continual / nuisance-dim / depth-composition / depth-is-cheap (80/20 **depth-gated**), trails static
  difficulty / class-count, honest **negative** on eval-time noise. Full reads: `draft6.0/src/phase{1,2,3,4}/*-summarize.md`
  (synthesis) + the reader-facing report set `draft6.0/src/stage1-report.md` + `draft6.0/src/phaseN/phaseN-report.md` + `draft6.0/src/ref-report/` (glossary).

## What I still do NOT know — the honest gaps

**The core spine is now simulated (Phases 1–4); the gaps moved.** What's *designed-and-confirmed* vs *still open*:

- **Phase 5 optimization — unrun.** The maintenance loop (Ch7 gate + sleep-*cadence* / LUT-vigilance) was run
  at a *fixed default* in Phase 4; tuning it against *this* cell's measured drift is the next phase's job.
- **Noise robustness *during learning* — untested (the A7 follow-up).** Phase 4 found OURS is *not* eval-time
  weight-noise-robust (a layernorm tradeoff); the substrate-relevant **train-with-noise / hardware-aware**
  test — where the forward-only robustness claim actually lives — has not been run.
- **Natural-data / scale.** The wins are on controlled synthetic + small probes (digits ✅, CIFAR-flat ⚠️);
  depth-composition is on a *built* headroom task. Confirming on natural, depth-needing data is open.
- **Direct-feedback (global top-down coordination)** — the window (w=2) sufficed; whether global is cheaper is untested.
- **Remaining knobs** in `main.ideas.v1.md` not yet swept (margin-vs-log loss; in-batch negatives → the LUT pool).
- **All analog / PVT behavior.** Phases 1–4 are ideal floats; full noise/drift/charge-dynamics realism is the
  deferred substrate layer (Phase 4's A7 cracked the door — it's now on the table per the "ideal converged" rule).

## Off-limits to over-eager building

**The recurrent lifelong-learning brain** (correctness-as-a-feeling) — *beyond* the numbered phases (1 =
structure/done, 2 = depth round 1/done, 3 = depth round 2/done, 4 = characterization/done, 5 = optimization/
upcoming) — is the real north star but **deliberately not specced.** Hold it as direction (`draft6.0/future-ref/`,
`docs/essence`), not a task.

## The honest one-liner

I hold the **full design intuition of draft 6.0 and why each piece is there**, **and the empirical spine now
exists**: Phases 1–4 ran (2026-06-20 → 22) and the cell is characterized — a substrate-native **continual**
learner that composes depth cheaply, not a static-accuracy competitor (`draft6.0/src/phase4/phase4-summarize.md`). What's
**not** yet done is **Phase 5 — optimization** (tune the sleep/gate maintenance loop against the measured drift)
plus the train-with-noise and natural-data follow-ups Phase 4 flagged. (The attribution chip — a separate earned
result — is now history, see below.)

---

> ## ⚠️ HISTORICAL — the attribution build (draft 5.1), kept as a record
>
> *What the previous `draft5.0-fossil/src/` simulator achieved, preserved so the result isn't lost — but it is the dead
> architecture (attribution / `|a·W|` hierarchical diffusion), not the live plan.*
>
> - **The mechanism trained at the unit level.** A single Ganglion under broadcast + momentum on `|a·W|`
>   converged on noisy linear regression (loss ratio ~0.001) and cut a nonlinear paraboloid ~20× (partial
>   fit). Attribution was a *demonstrated candidate at the atom*, not a wild guess — the open question was
>   always **scale**, and at scale the missing-direction flaw is what killed it.
> - **Physical Saturation was load-bearing** — without the rail the model diverged to NaN (momentum was both
>   contribution *and* update-scale → positive feedback). The supply-rail ceiling self-limited it.
> - **The lean baseline had no hidden-layer credit by construction** (a single global feedback sign can't
>   guide hidden ReLU features) — the structural fact that, with the missing sign, sealed the collapse.
> - **What was never reached:** substantive-task convergence, the higher levels (Limbic two-timescale,
>   SpecialGeneralist, multi-parent diffusion), and all analog/PVT behavior.
>
> The full code-level confidence log lives in git history and `draft5.0-fossil/src/docs/`. Read it only to understand the
> old build; the substrate primitives carry forward, the learning rule does not.
