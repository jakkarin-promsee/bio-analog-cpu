# `skill/sureSkill.md` — the meta-map: what's covered, what I'm sure of, what I'm not

> This is the index to `skill/` **and** an honest confidence log. It tells the next mind two things a
> normal doc won't: which mental-model maps exist (and which are current vs historical), and **what is
> genuinely solid vs what is still unknown.** Read it to calibrate how much to trust everything else.
>
> Each map in `skill/` is a *router* (it points into `draft6.0/`, `docs/draft/*` for the detail), not a
> procedure. `CLAUDE.md` (always loaded) points here, so the right map is found for the task at hand.
>
> **Migrated to draft 6.0 (June 2026).** The old confidence log below was about the *attribution* build
> (the `src/` simulator, draft 5.1). It's kept, banded, as a record of what the previous build achieved —
> not as the current state. The current state is: **spine committed, nothing simulated.**

## The maps, and their status

| Map (`skill/`) | Use it when… | Status |
| --- | --- | --- |
| `project-explore.md` | **read first** — the concept entry point: how to read the project + the corrections that are wrong here | ✅ 6.0 |
| `architecture-research.md` | proposing changes, triaging ideas, scope/scope-creep calls | ✅ 6.0 |
| `simulation-experiments.md` | writing tests, running a Phase-1 rung, interpreting results | ✅ 6.0 |
| `workflows.md` | the recurring moves (orient / checkpoint / commit-progress / double-check) | ✅ 6.0 |
| `sureSkill.md` | this meta-map / index | ✅ 6.0 |
| `simulator-code.md` | editing the simulator | ⚠️ **historical** — describes the old `src/` attribution sim; the 6.0 Phase-1 sim isn't written yet |

Maps to add **when 6.0 Phase 1 starts coding:** a **6.0 simulator-code** map (for the fresh SCFF+GD
behavioral sim), and later a **docs-maintenance** map. The hardware/RTL-handoff map waits until the design
re-freezes (6.0 deliberately set the circuit aside to stabilize the math first).

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

## What I still do NOT know — the honest gaps

**Everything empirical. Nothing in draft 6.0 has been simulated.** Don't mistake confidence about the
*design* for confidence about whether it *works*.

- **Does the SCFF + GD hybrid converge and stay stable?** Unproven — this is what rung 1.0 → 2.x exist to find.
- **Does the gated/sleep machinery actually hold the SCFF drift?** The plasticity gradient, the threshold
  gate, sleep replay — all reasoned, none run (rungs 2.1, 3.x).
- **Does direction chain across blocks** without the stack swinging (rung 4.x)? Open — including how many
  blocks before the linear block-delta stand-in strains.
- **All the open knobs** in `main.ideas.v1.md` (front:back plasticity ratio, gate threshold absolute-vs-
  slope, sleep cadence, LUT vigilance, margin-vs-log loss, two-sided-vs-pure-contrast). The sims set them.
- **All analog / PVT behavior.** Phase 1 is ideal floats; noise/drift/charge-dynamics realism is deferred
  until the ideal converges.

## Off-limits to over-eager building

**The recurrent lifelong-learning brain** (correctness-as-a-feeling) — *beyond* the numbered phases (1 =
structure/done, 2 = depth, 3 = maintenance) — is the real north star but **deliberately not specced.** Hold
it as direction (`draft6.0/future-ref/`, `docs/essence`), not a task.

## The honest one-liner

I hold the **full design intuition of draft 6.0 and why each piece is there** — that's transferable. What
does **not** yet exist is **any simulation evidence**: the spine is committed, the numbers are pending, and
the next real move is rung **1.0 — full SCFF.** (The previous build *did* earn a real result — see below —
but that was the attribution chip, now history.)

---

> ## ⚠️ HISTORICAL — the attribution build (draft 5.1), kept as a record
>
> *What the previous `src/` simulator achieved, preserved so the result isn't lost — but it is the dead
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
> The full code-level confidence log lives in git history and `src/docs/`. Read it only to understand the
> old build; the substrate primitives carry forward, the learning rule does not.
