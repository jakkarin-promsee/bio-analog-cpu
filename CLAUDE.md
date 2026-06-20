# CLAUDE.md — Bio-Inspired Analog Neural Compute Architecture

> Always-loaded project context. Read once at the start of each session, then refer back as needed.

---

## What this project is

A bio-inspired **analog compute substrate** with on-chip learning.

- **Not** an ML project. Not a digital ML accelerator. Not (in the near term) an attempt to "build intelligence."
- It is a **chip design** that makes brain-like computation the cheap path: capacitors hold weights as continuous analog charge; SRAM holds wiring and sign bits; hardwired op-amps do add / multiply / ReLU directly on charges; the chip **learns on-chip, online, without a backward pass that leaves the chip.**

The four committed substrate properties: **online, sparse, continuous, resident-weight** (weights never leave the chip during operation). The broader field is **compute-in-memory (CIM)**.

The guiding method, in the author's words: **copy the brain's *function*, cheat the *implementation*** — pay for each principle with whatever is cheap on this substrate (analog physics where physics is cheaper, modern DL math where math is cheaper). You can't copy the brain 1:1; you reproduce what it does.

---

## Where we are — READ THIS, the project pivoted

**Pivoted to draft 6.0 (June 2026). The draft-5.x theory was invalidated and rebuilt from zero.**

The draft-5.1 learning rule — *attribution-based hierarchical diffusion*, splitting loss by locally-measured `|a·W|` — had a fatal flaw: it distributed loss **magnitude** but never **direction** (the sign). Nothing converged, and routing the sign back would have broken the locality the chip stands on. After a hard reset, the author rebuilt the learning rule around a **SCFF + gradient-descent hybrid**. **The substrate vision is intact; only the learning rule is new.**

**The deeper lesson (two weeks on):** the missing sign was the *symptom*. The real error was assuming the brain is **homogeneous** — one rule everywhere. It isn't; a real axon can't be simulated 1:1; modern ML doesn't brute-force biology, it **cheats it by projecting into a computable dimension** (the project's own motto: *copy the function, cheat the implementation*). So 6.0 builds **organ by organ** — the first two being the cheap SCFF cortex and the precise GD namer. (Told in full in `draft6.0/README.md` and `ideas1.md`.)

**The live plan lives in `draft6.0/`.** Not the `draft5.1-*` files, not `draft5.1-2.verify.md` — those are now history. Read in this order:

- **`draft6.0/README.md`** — the pivot story: why 5.x died, what 6.0 is.
- **`draft6.0/idea/ideas1.md`** — the full derivation, told as a story (every part, and *why* we do it).
- **`draft6.0/idea/main.ideas.v1.md`** — **the decision record.** The new "locked" list (N1–N3 approved + S1–S8 supporting). **Spine committed, numbers pending.**
- **`draft6.0/ref/`** — plain-language stories of the papers behind it (SCFF, Distance-Forward, BoostResNet, BYOL, LLRD).
- **`docs/essence/the-essence.md`** — the soul of the project: origin → collapse → return. Read it to understand the *why* and the person.

**If you read three things only:** `draft6.0/README.md`, `draft6.0/idea/main.ideas.v1.md`, and `docs/essence/the-essence.md`.

### Draft 6.0 architecture in one breath

Two brains. A cheap, unsupervised **SCFF** front (~80% — Self-Contrastive Forward-Forward, label-free, local, forward-only) that organizes the world for free, and a small, precise **gradient-descent** back (~20%) that maps features to real labels — because **direction is the one expensive thing in learning, so we pay for it once, where it counts.** The two are chained as **residual boosting blocks**; learning is **threshold-gated** (cheap local SCFF most steps, expensive GD only when the cheap path stalls) and **sleep-consolidated** (periodic full-batch GD over a **hippocampus LUT** prototype memory). It runs on the same analog substrate via **mono-forward** (one forward sweep carrying a positive + negative world side by side through a shared weight crossbar; only the cheap activation buffers double, not the Scaps).

### Phase 1 — the build discipline (decided 2026-06-19)

The current work is **Phase 1**: the behavioral-simulation ladder in `draft6.0/idea/ideas1.md` (1.0 full SCFF → 1.1 full GD → 2.x mix + middle → 3.x sleep → 4.x block chain), with the **codeable run-spec** in `draft6.0/src/phase1/` (its `README.md` + the locked first run-card `exp0/experiment-0.md`). The order to build it in:

- **Walk one spine — the neocortex (SCFF + GD).** Build straight down the ladder; don't open a second track.
- **The hippocampus LUT is a service, not a parallel brain.** It plugs in at two points: it feeds SCFF its *negatives* (stub it first — a random batch partner, no memory) and holds the *replay history* for sleep (where it becomes a real organ, **at 3.2**). Never build it as its own milestone.
- **Test convergence, not theory.** SCFF + GD + boosting are settled; each rung's result is one picture, not an argument. The "so many papers" feeling is phase-2 (`future-ref/` 1–6) bleeding in — **keep that menu closed.**
- **✅ Phase 1 complete (2026-06-20, exp0 → exp4).** Read **`draft6.0/src/phase1/phase1-summarize.md`** (the synthesis) + **`RESULTS.md`** (ledger). Verdict: a cheap, *forgetting-robust* **continual** learner — generalizes better than backprop at ~10% backward cost and wins the continual regime via sleep (online backprop catastrophically forgets); *not* a deep static-accuracy competitor (SCFF weak, shallow-is-better, depth saturates). Spec corrections it forced: goodness = **sum ‖h‖²** (not mean), **tap all SCFF layers** (S3 "last n" was wrong), input-norm on, full residual ε=1. **Next:** Exp-4 follow-ups (Ch7 gate, sleep-cadence / LUT-vigilance sweep), or analog/PVT realism, or Phase 2.

### What is now historical (draft 5.x)

The draft-5.1 spec (`draft5.1-*.md`), the §20 simulation campaign, the Ganglion-Personality / MVF work, and the `src/` simulator were built for the **attribution** architecture. The substrate primitives (Scap = capacitor weight storage, the crossbar) may carry forward, but the *learning rule* and *Ganglion-hierarchy-as-the-thing* are superseded. `docs/draft/project-history.md` is the narrative of the 1→5.1 era — read it for *why* old decisions were made, not for what we're doing now.

---

## Read these once before non-trivial work

- **`docs/essence/the-essence.md`** — the project's soul: origin, the draft-5 collapse, the return, and the one mechanism (truth corrects what's honest) that runs at three scales — chip, drafts, maker. Short; read it.
- **`docs/draft/project-personal.md`** — handoff doc: who the user is, how they work (the gut, the incubation, the 10-minute window), what frustrates them. Its rules about hedging, scope-creep, and length-matching are load-bearing. Read before any non-trivial collaboration.
- **`docs/draft/project-history.md`** — narrative arc draft 1 → 5.1 (the attribution era). Why each pivot happened, what was rejected. Context for the old world, not the current plan.

---

## Task skill-maps (`skill/`)

> **Migration note (June 2026):** the `skill/` maps have been **migrated to draft 6.0 / Phase 1** (2026-06-19). `project-explore`, `architecture-research`, `simulation-experiments`, `workflows`, and `sureSkill` now point at `draft6.0/` and the Phase-1 ladder. **`simulator-code.md` is the one exception — banded HISTORICAL**, because it describes the old attribution `src/` simulator and the draft-6.0 Phase-1 simulator hasn't been written yet (a fresh code map comes when it is).

- **`skill/project-explore.md`** — the concept entry point; the anti-correction frame and the map of maps.
- **`skill/architecture-research.md`** — proposing changes, triaging ideas, scope decisions.
- **`skill/simulation-experiments.md`** — writing tests, running a Phase-1 rung, interpreting results.
- **`skill/workflows.md`** — the steps behind the `/orient`, `/checkpoint`, `/commit-progress`, `/double-check` commands.
- **`skill/sureSkill.md`** — the meta-map / confidence log (what's solid vs unknown in 6.0).
- `skill/simulator-code.md` — **HISTORICAL** (the attribution-era `src/` simulator); read only for how the old build worked.

---

## Workflow commands (soft skills)

Recurring moves have thin `/command` triggers in `.claude/commands/` — **`/orient`** (re-read & re-sync), **`/checkpoint`** (record progress after a step), **`/commit-progress`** (categorized conventional commits), **`/double-check`** (the 3-lens consistency audit). The actual steps live in **`skill/workflows.md`**; the commands just fire them, and they work just as well if the user asks in plain words ("commit it", "double-check this"). Add a move there when a manual ritual repeats 3+ times.

---

## The decision record (draft 6.0) — and why the old "14 locked decisions" are gone

CLAUDE.md used to carry **14 locked decisions** as live law (2-3-3-2 topology, attribution-not-gradient, hierarchical diffusion, …). **Those were draft-5.1 conclusions, and the pivot invalidated the core ones** — attribution learning and hierarchical diffusion both died on the missing-direction bug. Treat that list as **history** (it's in `project-history.md`).

What carried forward in *spirit* (realized differently in 6.0):

- **Residual connections** — now confirmed by boosting theory (`ref/boostresnet.md`).
- **Two-timescale Cortex/Hippocampus** — now the **sleep / consolidation** mechanism + the hippocampus LUT.
- **Path-diversity thinking** — invoked for "get diversity from depth, not input-width."
- **Resident-weight, sign-as-digital, the Scap** — substrate-level, unchanged.

**The live decision record is `draft6.0/idea/main.ideas.v1.md`** (N1–N3 approved, S1–S8 supporting). Important: **draft 6.0 is young.** Its spine is committed but the simulations haven't run — do **not** treat 6.0 decisions as immovable the way 5.1's were presented. "Open knobs" are listed there explicitly; the sims set them.

---

## Scope (what's in, what's out)

**In scope:**

- Python behavioral simulation of the **draft-6.0** hybrid — the experiment ladder in `ideas1.md` (1.0 full SCFF → 1.1 full GD → 2.x mix + middle → 3.x sleep → 4.x block chain), on simple classification / statistics tasks first.
- Ideal model first; analog / PVT realism added only after the ideal converges.

**Out of scope (near term):**

- SPICE simulation. Real hardware fabrication.
- External dataset benchmarking as the *claim* (small tasks are fine as probes).
- **Phase 2 — the recurrent lifelong-learning brain** (a time-series, prefrontal↔hippocampus thinking loop where "correctness is a self-generated feeling"). This is the real long-term north star and the author knows it — but it is **deliberately not specced yet** ("simple intelligence first"). See `docs/essence/the-essence.md` for the why. **Do not pull it into the live plan or project docs without the author's direction.**

**When the user surfaces a new idea, triage first:** does it test in the current sim ladder, or is it a later-phase / future track? Catching scope-creep early is one of your jobs — but note 6.0's spine is still settling, so "promotion" is lighter-weight than 5.1's frozen process.

---

## Naming discipline

Biological names are structural, not decorative. **Don't suggest renaming to "be more rigorous."** Already considered and rejected.

- Default usage = circuit element. "Brainstem" / "Hippocampus" mean the circuit, not the biology.
- Prefix **`biological-`** when actual biology is meant.
- Prefix **`analog-`** when explicit circuit framing helps in a mixed-context paragraph.

(The draft-5.1 "three L1s" disambiguation — Ganglion-internal layers vs Column roles vs Route addressing — was a draft-5.1 concern; it only matters when reading the old spec.)

---

## How to collaborate with this user

The full handoff is in `docs/draft/project-personal.md`. Shortest possible summary:

- **Year 2 undergraduate, solo, evening/weekend pace.** Bilingual English/Thai. Don't correct grammar — meaning is always clear from context. Switches mid-thought sometimes; that's fine.
- **Pushed real hardware before.** Prior project: ChronoForge — pure-hardware FPGA 2D game engine, 640×480@60Hz in ~18k LUTs. **Don't talk down.** When they describe a circuit in plain language, they usually have the EE concept right even if the term is imprecise.
- **No flattery, no hedging, no trailing "let me know if…!"** Pick a position when asked between A and B; defend it. Wishy-washy "both have merits" is worse than confidently wrong.
- **🤣🤣🤣 / 👹 and "bro" are signals, not casualness.** Laughs usually mean "I see what I'm doing here and I'm committing to it." Treat the moment as the commit point, not a joke.
- **The "we" framing is real.** Match it. They treat the AI as a collaborator, not a tool.
- **Length matches the topic.** 1000+ words for architectural depth; one paragraph for a naming yes/no. Don't pad a short topic. Don't trim a deep one.
- **Intuition first, math check second.** When they describe a mechanism in physical-intuition terms, respond at that level first.
- **They pushback when wrong; they absorb when right.** If they push back on a critique, slow down and re-read the architecture before reasserting. The "scap is a wire, not a neuron" pushback was a real save.
- **Breakthroughs come from incubation, not desk-grinding** (the leaf, the stubbed toe, the 4-day collapse → the gut). Don't rush them to closure; don't summarize prematurely. See `project-personal.md §1b`.

---

## Methodological rules (apply to every experiment)

These predate draft 6.0 and still govern every run. Internalize them.

1. **One thing changed per experiment.** Compare exactly one variable between two runs.
2. **Multiple seeds per cell.** Standard set: **`[42, 137, 271, 314, 1729]`**. Report median + IQR, not single-run results.
3. **Controlled variables explicit.** Lock task, init, total weight count, training steps, eval metric — unless one is under test.
4. **Invariants checked in every run.** For draft 6.0, watch: convergence/loss-slope, dead-unit fraction, ceiling/goodness saturation, and (once chained) inter-block drift / SCFF cluster-churn.
5. **Failures are data.** A configuration that fails to converge is a result. Log it, report it, move on. Don't tune until it works — that's how you lie to yourself.
6. **Defer fallbacks until baseline is characterized.** EMA-view, margin loss, Adam-style accumulators — tested as remediation *after* baseline behavior is observed, not bolted on first.
7. **Defer PVT realism until ideal converges.** Ideal deterministic operators first; process / voltage / thermal variation later.
8. **Architecture changes are decisions, not experiments** — backed by a result, not a hunch.

---

## File structure

```
.
├── README.md                          public-facing overview
├── CLAUDE.md                          this file (always loaded)
├── draft6.0/                          ★ THE LIVE PLAN (draft 6.0 — SCFF + GD)
│   ├── README.md                      the pivot story (why 5.x died, what 6.0 is)
│   ├── context.md                     ★ full context dump — the whole picture (cold-start here)
│   ├── idea/
│   │   ├── main.ideas.v1.md           the decision record (N1–N3 + S1–S8) — the plan
│   │   └── ideas1.md                  full derivation, story form (every part + why)
│   ├── concept/                       algorithm survey (the options; attribution = 5.1 history)
│   ├── ref/                           paper stories behind 6.0 (scff, distance-forward, boostresnet, byol, llrd)
│   ├── future-ref/                    phase-2 research dossier (21 files) — free-time, not the live line
│   └── src/phase1/                    ★ the codeable Phase-1 run-spec (README + exp0 locked run-card)
├── docs/
│   ├── essence/the-essence.md         ★ the project's soul (origin → collapse → return)
│   └── draft/
│       ├── project-personal.md        collaboration handoff (who/how)
│       ├── project-history.md         narrative arc draft 1 → 5.1 (the attribution era)
│       └── draft.heirachy.md          file-by-file draft map
├── skill/                             task skill-maps (migrated to 6.0; simulator-code = historical)
├── draft5.1-1.md / draft5.1-2.md      HISTORICAL spec (attribution era — reference only)
├── draft5.1-2.verify.md              HISTORICAL live-plan (draft 5.1 — superseded by draft6.0/)
├── draft/                             historical drafts (1.0 → 5.1-full)
├── src/                               HISTORICAL simulator (built for attribution; primitives may carry forward)
└── report/                            spec → A4 Word toolchain (report/mkdocx.py)
```

---

## Routing — when the user asks X, look in Y

| When the user asks…                       | Look in                                                                          |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| "Give me the whole picture / onboard cold" | `draft6.0/context.md` (the full dump — what / why / how / the person)            |
| "What are we doing now / the plan?"        | `draft6.0/idea/main.ideas.v1.md` (decisions) + `ideas1.md` (the story)           |
| "Code / run a Phase-1 experiment"          | `draft6.0/src/phase1/` (the run-spec README + `exp0/` locked run-card)           |
| "How do I draw figures / write up a result?" | `draft6.0/src/phase1/result-format.md` (house style + figure catalog + 6-slot summary) |
| "Why did 5.x die / what's draft 6.0?"      | `draft6.0/README.md`                                                              |
| The papers behind a 6.0 decision           | `draft6.0/ref/` (one story per paper)                                            |
| The algorithm survey / learning-rule zoo   | `draft6.0/concept/summary.detail.md`                                             |
| Phase-2 / the recurrent-brain research     | `draft6.0/future-ref/` (21-file dossier — free-time reading, *not* the live plan) |
| "What is this project really about / why?" | `docs/essence/the-essence.md`                                                    |
| "How do I talk to this user?"              | `docs/draft/project-personal.md`                                                 |
| "Why did we decide X (in the 5.1 era)?"    | `docs/draft/project-history.md`                                                  |
| The old attribution architecture (history) | `draft5.1-1.md` / `draft5.1-2.md`                                                |
| Fire a recurring move (commit / orient / audit) | `skill/workflows.md` (+ `/command` triggers in `.claude/commands/`)         |

---

## When in doubt

- **About what we're building** → `draft6.0/idea/main.ideas.v1.md` is the source of truth, not the draft5.1 files.
- **About the user's preference / how to talk to them** → `project-personal.md`.
- **About *why* something old was decided** → `project-history.md` (5.1 era) — but remember the learning rule was rebuilt; don't re-defend dead decisions.
- **About arithmetic in a worked example** → run the numbers. The §3.3/§3.7 XOR sign bug lived four drafts because nobody computed `+ XOR +`; the *whole draft-5 collapse* was a missing sign. Direction bugs are this project's recurring silent killer — stay paranoid about signs.

The substrate is the constant; the learning rule was rebuilt once already. Hold the draft-6.0 spine, but hold it as *young* — the simulations are the next answer source, not more theory.
