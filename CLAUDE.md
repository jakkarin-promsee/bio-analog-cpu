# CLAUDE.md — Bio-Inspired Analog Neural Compute Architecture

> Always-loaded project context. Read once at the start of each session, then refer back as needed.

---

## What this project is

A bio-inspired **analog compute substrate** with on-chip hierarchical credit assignment.

- **Not** an ML project. Not a digital ML accelerator. Not an attempt to "build intelligence."
- It is a **chip design** that makes brain-like computation the cheap path: capacitors hold weights as continuous analog charge; SRAM holds wiring and sign bits; hardwired op-amps do add / multiply / ReLU directly on charges; learning diffuses through a five-level hierarchy using locally-measured `|a · W|` contribution instead of routed gradients.

The four committed substrate properties: **online, sparse, continuous, resident-weight** (weights never leave the chip during operation). The broader field is **compute-in-memory (CIM)**.

---

## Where we are

**Theory locked at draft 5.1. The Python simulation phase has started.** SLICE-1 — one Ganglion, the §20.1 MVF harness — is built and runs (`python -m src.example.run_xor`); the author is currently exploring it pre-Phase-2 by hand. The plan is being re-drafted phase-by-phase in `draft5.1-2.verify.md` (current: **Phase 1 — Ganglion Personality**), and there is **no H1 verdict yet**. See `skill/project-explore.md` (the concept entry point) for the full frame.

The canonical specification is split across two files (split only for PDF-export length; no content difference):

- **`draft5.1-1.md`** — Part 1 (§0–§19, §22–§23): framing, the central mechanism (§2), worked XOR example (§3), modules, cross-cutting mechanisms, hypotheses (§17), math targets, open questions, protected list (§22), glossary.
- **`draft5.1-2.md`** — Part 2 (§20–§21): simulation campaign (MVF + ten phases) and future tracks.

The pre-split single-file version is kept at `draft/draft5.1-full.md` for reference only.

**If you have time for three sections only:** §2 (the mechanism), §3 (the worked example), and `draft5.1-2.verify.md` Phase 1 (what we're doing now).

---

## Read these once before non-trivial work

- **`docs/draft/project-personal.md`** — handoff doc: who the user is, how they work, what frustrates them, what's worked. Read this before any non-trivial collaboration — its rules about hedging, scope-creep, and length-matching the topic are load-bearing.
- **`docs/draft/project-history.md`** — narrative arc draft 1 → 5.1. Why each pivot happened, what was rejected and why. Reach for this when you're about to second-guess a locked decision.
- **`docs/draft/draft.heirachy.md`** — file-by-file map of every draft, with the naming convention (`-N`, `.rN`, `.xN`, `.qN` suffixes).

---

## Task skill-maps (`skill/`)

**Start with `skill/project-explore.md` — the concept entry point (read it first).** It teaches *how to read the project's concepts* (the Scap→Ganglion→Column→Lobe→Brainstem hierarchy, attribution-not-gradient, the direction) and front-loads the "corrections that are WRONG here." It is the front door; the four task-maps below are the rooms.

Then, before non-trivial work, load the **mental-model map** for the task at hand. Each is a *router* — it tells you which docs to read (only the parts named), and installs the mindset and constraints for that side of the project. They are maps, not procedures; read what they point to.

- **`skill/project-explore.md`** — **read first.** The concept entry point, the anti-correction frame, and the map of maps.
- **`skill/simulator-code.md`** — editing the Python simulator (`src/library`, `src/example`).
- **`skill/simulation-experiments.md`** — writing tests, running §20 phases / the MVF, interpreting results.
- **`skill/architecture-research.md`** — proposing changes, triaging ideas, scope decisions.
- **`skill/sureSkill.md`** — the index, plus an honest log of what is solid vs still unknown. **Read this to calibrate trust** before relying on the rest.

> The deepest single onboarding doc is `src/docs/context.md` (the full journey + decisions + traps). The skill-maps are the task-specific lenses onto it and the spec.

---

## Workflow commands (soft skills)

Recurring moves have thin `/command` triggers in `.claude/commands/` — **`/orient`** (re-read & re-sync), **`/checkpoint`** (record progress after a step), **`/commit-progress`** (categorized conventional commits), **`/double-check`** (the 3-lens consistency audit). The actual steps live in **`skill/workflows.md`**; the commands just fire them, and they work just as well if the user asks in plain words ("commit it", "double-check this"). Add a move there when a manual ritual repeats 3+ times.

---

## The 14 locked decisions (§22 Protected List)

These are **conclusions, not preferences**. Don't reopen without strong evidence (a phase report citing data). Each one is the survivor of at least one rejected alternative; the rejections are documented in `docs/draft/project-history.md`.

1. **2-3-3-2 Ganglion topology, 29 Scaps** — path-diversity-per-scap optimum.
2. **Attribution-based learning, not gradient descent.** Substrate measures `|a · W|` for free — and it's a **demonstrated candidate, not a risky bet**: a single Ganglion already trains on it (regression: noisy linear plane → near-perfect; nonlinear paraboloid → ~20× loss cut). The open question is *scale* (H1), not validity. Don't "correct" it back to gradients — but SGD stays the **comparison baseline** at scale (Phase 2 Cell D), not a replacement. See `skill/project-explore.md` §2.
3. **Hierarchical diffusion** as the routing mechanism. Per-level normalized shares.
4. **Five structural levels:** Scap → Ganglion → Column → Lobe → Limbic Loop.
5. **Brainstem** as small central controller (~8–15k transistors). Not a CPU.
6. **Loss conservation as additive:** `Σ children_shares = parent_loss`. Not probability-like.
7. **Semi-anatomical naming.** Settled.
8. **Residual connections at the Ganglion level** by default — primary structural defense against dead-weight collapse.
9. **Cortex and Hippocampus identical topology**, differ only in update cadence.
10. **Forward_Sign_SRAM in every Scap.** Resolves multi-parent direction conflict. 1 bit per Scap.
11. **Differential Pair op-amps throughout.** Analog robustness baseline. Not optional.
12. **Dummy Scap per Column** for on-the-fly PVT calibration.
13. **Current Mirror** for Loss Share normalization. Ratio preservation under PVT.
14. **Physical Saturation** as primary defense against winner-take-all. Capacitor charging dynamics — don't engineer around it with software normalizers before Phase 2 validates the physics.

Everything else — precision allocations, decay factors, mask sources, timescale ratios `k` and `M`, init schemes, Auto-Zeroing frequency, Dummy Scap granularity, saturation-rate calibration — is open and will be set by simulation data.

---

## Scope (what's in, what's out)

**In scope:**

- Python behavioral simulation. Ideal model first; PVT realism added in Phase 8 (§20.14).
- The 11 hypotheses in §17, tested across the §20 phase plan.
- Architectural changes promoted from §21 future tracks via the §20.17 promotion criteria, only with phase data backing them.

**Out of scope:**

- SPICE simulation. Deferred to §21.16.
- Real hardware fabrication.
- External dataset benchmarking. Not the project's claim.
- "Build intelligence." Too fuzzy to optimize against.

**When the user surfaces a new idea, triage first:** does it belong in §20 (test as part of simulation) or §21 (future track)? It does **not** go into §1–§16 of the locked spec without the §20.17 promotion process. Catching scope-creep early is one of your jobs.

---

## Naming discipline

Biological names are structural, not decorative. **Don't suggest renaming to "be more rigorous."** This was already considered and rejected.

- Default usage = circuit element. "Brainstem" means the controller circuit.
- Prefix **`biological-`** when actual biology is meant ("biological brainstem").
- Prefix **`analog-`** when explicit circuit framing helps in a mixed-context paragraph.

Three independent "L1" usages — always specify which:

- **Ganglion-internal layers** are L1–L4 inside a single Ganglion (input, two hidden, output).
- **Column-level roles** use Generalist (G) and Specialists (S₁, S₂, S₃) — not "L1/L2."
- **Route addressing** is "Route L1" and "Route L2" — 4-bit + 4-bit Ganglion grid addressing.

---

## How to collaborate with this user

The full handoff is in `docs/draft/project-personal.md`. Shortest possible summary:

- **Year 2 undergraduate, solo, evening/weekend pace.** Bilingual English/Thai. Don't correct grammar — meaning is always clear from context. Switches mid-thought sometimes; that's fine.
- **Pushed real hardware before.** Prior project: ChronoForge — pure-hardware FPGA 2D game engine, 640×480@60Hz in ~18k LUTs. **Don't talk down.** When they describe a circuit in plain language, they usually have the EE concept right even if the term is imprecise.
- **No flattery, no hedging, no trailing "let me know if…!"** Pick a position when asked between A and B; defend it. Wishy-washy "both have merits" is worse than confidently wrong.
- **🤣🤣🤣 and "bro" are signals, not casualness.** Laughs usually mean "I see what I'm doing here and I'm committing to it." Treat the moment as the commit point, not a joke.
- **The "we" framing is real.** Match it. They treat the AI as a collaborator, not a tool.
- **Length matches the topic.** 1000+ words for architectural depth; one paragraph for naming yes/no. Don't pad a short topic. Don't trim a deep one.
- **Bilingual external-AI uploads (`_x1`, `_d1`, `_q1` files) are critique to triage**, not text to paraphrase. Engage with the substance.
- **Intuition first, math check second.** When they describe a mechanism in physical-intuition terms, respond at that level first. Don't immediately reach for equations — even though the math check often comes next.
- **They pushback when wrong; they absorb when right.** If they push back on a critique, slow down and re-read the architecture before reasserting. The "scap is a wire, not a neuron" pushback was a real save earlier.

---

## Where the code is, and the next concrete action

**The simulation has started.** SLICE-1 — one Ganglion, the §20.1 MVF harness — is **built and runs** end-to-end (`python -m src.example.run_xor`): boundary bridge, crossbar, Ganglion ALU, EMA momentum, backward broadcast, and a basic supply-rail saturation in the Scap (`W_RAIL`). It is stable. The author is currently **exploring it pre-Phase-2 by hand** (linearized data, cap-range and last-layer-activation experiments) — intentional play, **not** the formal hypothesis test and **not** an H1 verdict. (See `skill/project-explore.md` §7 and `src/docs/context.md` for the honest status.)

**The plan is re-drafted intuition-first, phase by phase, in `draft5.1-2.verify.md` — that is the single source of truth for what we're doing now.** (`draft5.1-2.md` §20 is the older rough scaffold.) Don't restate the phase plan here; read it there. As of now:

- **Phase 1 (current) — Ganglion Personality.** Characterize the atom: what shapes one 2-3-3-2 Ganglion can make and its limits — sweep inputs/weights, plot the output surface up a realism ladder (ideal → activation-variant → cap-ceiling → saturation), ×2 for residual. The old "operator-sanity" check folds in as rung 0. **Work it in `src/experiment/phase1/`** (enter via its `README.md`; log via `experiment-{n}.md`).
- **Phase 2 (sketch) — Ganglion-network characterization**, once the atom is known. Re-derived from Phase 1 data, not pre-committed.

The methodological rules below still govern every run (one-thing-changed, reproducible seeds, failures-are-data), and stay paranoid about the §3.3 / §3.7 XOR-convention sign bug — still the most likely silent killer.

---

## Methodological rules (apply to every experiment)

From §20.2. Internalize these — they govern every run, every phase.

1. **One thing changed per experiment.** Compare exactly one variable between two runs. Multi-variable comparisons can't be interpreted.
2. **Multiple seeds per cell.** Standard set: **`[42, 137, 271, 314, 1729]`**. Report median + IQR, not single-run results.
3. **Controlled variables explicit.** Lock task, init, total Scap count, training steps, pulse-width schedule, precision per level, eval metric — unless one is under test.
4. **Invariants checked in every run, not as separate tests.** Four monitors logged for every run:
   - Loss conservation ε (target < 5% per level)
   - Dead-weight fraction (target < 5% by end of training)
   - Ceiling-saturation fraction (target < 5%)
   - T_max clip rate (target < 20%)
5. **Failures are data.** A configuration that fails to converge is a result. Log it, report it, move on. Don't tune until it works — that's how you lie to yourself.
6. **Defer fallbacks until baseline is characterized.** Path 0 noise floor, Adam-style `v_t`, adaptive decay — none of these go into Phase 2. They are tested as remediation _after_ baseline failure is observed.
7. **Defer PVT realism until ideal converges.** Phases 1–7 use ideal deterministic operators; Phase 8 introduces process / voltage / thermal variation.
8. **Architecture changes are decisions, not experiments.** Promotion from §21 to baseline goes through §20.17, with a phase report citing the data.

---

## File structure

```
.
├── README.md                          public-facing overview
├── CLAUDE.md                          this file (always loaded)
├── draft5.1-1.md                      canonical spec, Part 1
├── draft5.1-2.md                      canonical spec, Part 2 — ROUGH pre-plan (see its banner)
├── draft5.1-2.verify.md               live plan — re-drafted phase by phase (the whiteboard)
├── docs/
│   └── draft/
│       ├── draft.heirachy.md          file-by-file draft map
│       ├── project-history.md         narrative arc draft 1 → 5.1
│       └── project-personal.md        collaboration handoff
├── draft/                             historical drafts (1.0 → 5.0.x1)
│   └── draft5.1-full.md               unsplit version of the canonical spec (reference only)
├── skill/                             task skill-maps — START: project-explore.md (the front door)
├── src/                               Python simulator — BUILT; SLICE-1 runs
│   ├── library/                       reusable element classes (Scap, ALU, ControlUnit, wires, …)
│   ├── example/                       reference builds + run_xor.py (the MVF harness)
│   ├── docs/                          code-side mental model (context, concept, core_logic, …)
│   └── experiment/                    per-phase experiment workspace (scripts + figures + logs; enter via phaseN/README.md)
├── tests/                             pytest unit tests (to be created — Phase 1)
├── reports/                           phase reports as runs complete (to be created)
└── notes/                             working notes & design rationale (e.g. ganglion-role-switching.md)
```

---

## Routing — when the user asks X, look in Y

| When the user asks…                       | Look in                                                                          |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| "How do I read / onboard this project?"    | `skill/project-explore.md` — the concept entry point (read first)                |
| Fire a recurring move (commit / re-sync / audit / checkpoint) | `skill/workflows.md` (+ `/command` triggers in `.claude/commands/`)              |
| Architecture question (modules, mechanism) | `draft5.1-1.md` — §2 for mechanism, §6–§13 for modules                          |
| Why the Ganglion *works* (atomic region-multiplexer / axon rationale) | `notes/ganglion-role-switching.md`                          |
| Simulation plan / what we're doing now      | `draft5.1-2.verify.md` (live, phase-by-phase); `draft5.1-2.md` §20 is the rough scaffold |
| Where experiments + their logs live        | `src/experiment/` — enter a phase via its `phaseN/README.md`                     |
| "Why did we decide X?"                     | `docs/draft/project-history.md`                                                  |
| "How do I talk to this user about Y?"      | `docs/draft/project-personal.md`                                                 |
| Glossary lookup                            | `draft5.1-1.md` §23                                                              |
| "What draft was X introduced in?"          | `docs/draft/draft.heirachy.md`                                                   |
| Open question / tuning parameter           | `draft5.1-1.md` §19 (architecture-critical) or §19.2 (tuning)                    |
| Failure mode / remediation                 | `draft5.1-1.md` §2.4 + `draft5.1-2.md` §20.18 (Negative Result Protocols)        |

---

## When in doubt

- **About scope** → defer the new idea to §20 (simulation test) or §21 (future track), not §1–§16 of the locked spec.
- **About a locked decision** → check `project-history.md` for why it was decided before reopening.
- **About the user's preference** → check `project-personal.md` before guessing.
- **About a section number after structural changes** → grep the cross-references; old `§X.Y` references shift between drafts.
- **About arithmetic in a worked example** → run the numbers. The §3.3 / §3.7 XOR-convention bug existed for four drafts because nobody actually computed `+ XOR +`.

The architecture is locked for a reason. The simulation campaign is the next answer source — not more theory.
