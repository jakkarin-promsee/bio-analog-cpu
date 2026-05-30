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

**Theory locked at draft 5.1. The Python simulation phase has started.** SLICE-1 — one Ganglion, the §20.1 MVF harness — is built and runs (`python -m src.example.run_xor`); the author is currently exploring it pre-Phase-2 by hand. The formal Phase 1 / Phase 2 campaign is the next milestone, and there is **no H1 verdict yet**. See `skill/project-explore.md` (the concept entry point) for the full frame.

The canonical specification is split across two files (split only for PDF-export length; no content difference):

- **`draft5.1-1.md`** — Part 1 (§0–§19, §22–§23): framing, the central mechanism (§2), worked XOR example (§3), modules, cross-cutting mechanisms, hypotheses (§17), math targets, open questions, protected list (§22), glossary.
- **`draft5.1-2.md`** — Part 2 (§20–§21): simulation campaign (MVF + ten phases) and future tracks.

The pre-split single-file version is kept at `draft/draft5.1-full.md` for reference only.

**If you have time for three sections only:** §2 (the mechanism), §3 (the worked example), §20.1 (Minimum Viable Falsification — the one-hour test that can falsify H1).

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

The operator primitives exist in `src/library` as first-pass `[ALGO]` fills. What is **not** done: the formal Phase 1 pytest suite and the Phase 2 campaign. The next concrete steps, gated on each other:

### Step 1 — Phase 1: Operator Sanity (~1 week, §20.7)

Pin down the primitives (currently first-pass) with pytest unit tests, each against its ideal:

- Add op-amp · Multiply op-amp · ReLU op-amp
- Capacitor charge dynamics (Euler integration of `dV/dt`)
- Time-to-threshold measurement (clocks to cross A%/B% on a measurement cap)
- PWM update (`weight_cap -= pulse_width × momentum × direction`)

**Exit criterion:** each operator passes with max error < 0.1% of expected output; document worst-case error per operator. (The MVF harness already exercises these end-to-end; Phase 1 makes the correctness explicit and regression-checked.)

### Step 2 — Phase 2: Single Ganglion baseline (~2 weeks, §20.8)

The central test of **H1, H7, H8, H10.** 60 runs across a 4-cell config matrix × 3 tasks (XOR, sine, two-moons) × 5 seeds.

**Do not start Phase 2 until the operators are trusted. Do not add Phase 3+ variations to the Phase 2 runs.** One-thing-changed discipline from day one. Be paranoid about the §3.3 / §3.7 XOR-convention bug — a sign or measurement-direction error is the most likely killer.

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
├── draft5.1-2.md                      canonical spec, Part 2
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
│   └── docs/                          code-side mental model (context, concept, core_logic, …)
├── tests/                             pytest unit tests (to be created — Phase 1)
├── reports/                           phase reports as runs complete (to be created)
└── notes/                             working notes & design rationale (e.g. ganglion-role-switching.md)
```

---

## Routing — when the user asks X, look in Y

| When the user asks…                       | Look in                                                                          |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| "How do I read / onboard this project?"    | `skill/project-explore.md` — the concept entry point (read first)                |
| Architecture question (modules, mechanism) | `draft5.1-1.md` — §2 for mechanism, §6–§13 for modules                          |
| Why the Ganglion *works* (atomic region-multiplexer / axon rationale) | `notes/ganglion-role-switching.md`                          |
| Simulation plan / phase / metric question  | `draft5.1-2.md` — §20                                                            |
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
