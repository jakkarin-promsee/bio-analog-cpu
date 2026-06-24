# SKILL-PLAN.md — Skill Redesign Plan

> **What this is.** The spec for a full rewrite of the project's skill system.
> Old `skill/*.md` files are scrapped; new skills are built from scratch, split into a
> universal root layer and draft-specific layers. Build from this doc — don't patch the old files.
>
> **Status: BUILT (2026-06-24).** All skills written to `.claude/skills/` (universal) + `draft6.0/.claude/skills/`
> (draft-6); `workflows.md` folded into the four `.claude/commands/`; old `skill/` deleted. Refinements applied vs
> this draft: the draft-6 `explore` was renamed **`status`** (two same-named skills don't override by name like
> nested `CLAUDE.md` — distinct names avoid the collision); every `SKILL.md` got `name:` + a one-line keyword-front
> `description:`; the `simulator-code` body was corrected (there is **no `p1lib.py`** — Phase 1's code lives in
> `phase1/exp0/models_extra.py`); `claudeMdExcludes` was skipped (rationale in `AGENT-OPTIMIZE-PLAN.md`). The
> living maintenance guide is `AGENT-OPTIMIZE-GUIDE.md`.

---

## 1. The Problem

The old `skill/*.md` setup had five compounding issues:

| # | Problem |
|---|---|
| **Dead weight** | `skill/simulator-code.md` describes the draft5.0 attribution sim — an architecture that's been dead since the pivot. Every token it occupies is wrong information. |
| **Critical rot** | `skill/architecture-research.md` still says "no draft-6.0 sim has run." Four phases ran and closed. A cold agent reading it enters pre-experiment mode on the most complex tasks. |
| **Wrong format** | Old `skill/*.md` files are manual-load reference docs, not native skills. They only enter context when explicitly pulled — no auto-load, no description matching. |
| **No budgets** | Nothing tells the agent to stop reading. "Find a paper" sends it into the full papers tree. "Orient" pulls 920+ lines of skill maps into context. |
| **Flat, no layering** | Everything at root level. Draft-specific maps sit beside cross-draft rules. No per-draft skills, no way to scope context to the active draft. |

---

## 2. Design Principles

1. **Skills load by task description, not by manual reference.** Every skill has a `description:` the model matches against. It fires when the task fits — not when someone remembers to call it.

2. **Root = universal and stable. Draft = specific and can override.** Root skills cover what's true across all drafts. If a draft needs something different, it writes its own skill or extends in its `CLAUDE.md`. Root is never touched for draft-level changes.

3. **Every skill has a read-budget line.** The last line of every skill body: *"Load the files named above and stop. For anything heavier, dispatch the Explore subagent."*

4. **Commands stay commands.** Deliberate user moves (`/orient`, `/checkpoint`, `/commit-progress`, `/double-check`) are explicit — they must never auto-fire. They stay in `.claude/commands/`, not skills.

5. **Draft-specific overrides are opt-in.** A draft only writes a skill if it genuinely differs from the root convention. The default is to inherit root.

---

## 3. Folder Structure

```
[repo root]
├── .claude/
│   ├── commands/                    ← explicit user moves (unchanged)
│   │   ├── orient.md
│   │   ├── checkpoint.md
│   │   ├── commit-progress.md
│   │   └── double-check.md
│   └── skills/                      ← ROOT universal skills (new)
│       ├── explore/
│       │   └── SKILL.md
│       ├── project-frame/
│       │   └── SKILL.md
│       ├── folder-structure/
│       │   └── SKILL.md
│       └── writing-report/
│           └── SKILL.md
│
├── draft6.0/
│   └── .claude/
│       └── skills/                  ← draft6.0-specific skills (new)
│           ├── explore/
│           │   └── SKILL.md
│           ├── run-experiment/
│           │   └── SKILL.md
│           ├── find-paper/
│           │   └── SKILL.md
│           ├── simulator-code/
│           │   └── SKILL.md
│           └── writing-report/      ← only if draft6.0 format differs from root
│               └── SKILL.md
│
└── skill/                           ← OLD folder → DELETE after new skills are written
    (simulator-code.md, workflows.md, simulation-experiments.md,
     sureSkill.md, architecture-research.md, project-explore.md)
```

**SKILL.md format** (every skill file):
```markdown
---
description: <phrase the model matches on — lead with words a request would contain>
---

[body: what to read, what to do, the budget line]
```

---

## 4. Root Skills (Universal)

These are true across all drafts. Written once at root. Any draft that differs writes its own.

---

### `explore`
**Triggers on:** "show me the project structure" / "where is X" / "how is this repo organized" / "what's in draft5 vs draft6" / "how do I navigate this"

**Body covers:**
- The 3-layer context hierarchy (root CLAUDE.md → draftN/CLAUDE.md → phaseN/CLAUDE.md) and how auto-loading works
- What lives at root vs in each draftN/ vs in docs/ vs in draft-journey/
- The live line vs historical world: draft6.0/ is live; draft5.0/ is history; draft-journey/ is the idea journey; docs/ is cross-draft reference
- How to read efficiently: load the layer your task needs and stop; for heavy multi-layer lookups, dispatch the Explore subagent
- The routing table: "working on Phase 5" → start in draft6.0/; "why an old decision" → docs/draft/project-history.md; "what the project is" → load `project-frame` skill

**Budget:** Read this skill + one target CLAUDE.md. For a full repo sweep, dispatch the Explore subagent.

---

### `project-frame`
**Triggers on:** "what is this project" / "is this ML" / "explain the architecture" / "what's SCFF" / "what does this chip do" / "how does it learn"

**Body covers:**
- The one thing to internalize: this is a chip, not a model (analog compute substrate, on-chip learning, the four committed properties: online / sparse / continuous / resident-weight)
- The method: copy the brain's *function*, cheat the *implementation* — analog physics where physics is cheaper, modern DL math where math is cheaper
- The corrections table: the reflexes that are wrong here (it's not just FF; it's not just backprop; it's not an accuracy maximizer; don't rename the bio-names; don't "optimize the Python")
- The two-brain hybrid in one breath: SCFF front (~80%, label-free, forward-only), GD back (~20%, where direction must be paid for), chained as residual boosting blocks
- Pointer to draft6.0/CLAUDE.md for architecture detail; pointer to docs/essence/the-essence.md for the why

**Budget:** Read this skill. For architecture detail, load draft6.0/CLAUDE.md. For the full story, load draft6.0/context.md.

---

### `folder-structure`
**Triggers on:** "where does this file go" / "how should I organize" / "add a new file" / "add a new phase" / "add a new draft" / "what's the canonical structure"

**Body covers:**

**Root canonical layout:**
- `CLAUDE.md` — always-loaded stable root (identity, rules, router only — no status)
- `AGENTS.md` — cross-tool entry (Cursor, Copilot, etc.)
- `README.md` — human-facing project overview
- `draft6.0/` — live line
- `draft5.0/` — historical (attribution era, superseded)
- `draft-journey/` — the idea journey log (drafts 1.0 → 5.1) — NOT docs/draft/
- `docs/` — cross-draft reference: `docs/essence/` (the why + the person), `docs/draft/` (project-history, project-personal)
- `.claude/` — commands + root skills
- `skill/` — OLD; being deleted; do not add files here

**Draft canonical template** (what any draftN/ should contain):
- `CLAUDE.md` — the draft's mental model + current status ladder (this is the file that changes when a phase advances)
- `README.md` — pivot story or draft overview (human-facing)
- `context.md` — full cold-start narrative (what / why / how / the person)
- `idea/` — decision record (`main.ideas.vN.md`) + full derivation story (`ideasN.md`)
- `research/` — organized by role: `survey/` (learning-rule zoo), `papers/` (per-decision paper stories), `north-star/` (beyond-the-phases compass)
- `src/` — simulation workspace: one folder per phase (`phaseN/`), a stage-level report, a reference glossary (`ref-report/`)
- `.claude/skills/` — draft-specific skills

**Phase canonical template** (what any phaseN/ under src/ should contain):
- `CLAUDE.md` — thin signpost (verdict, authoritative record pointers, read-budget)
- `README.md` — the codeable experiment spec
- `phaseN-summarize.md` — synthesis (the one file to read from outside this phase)
- `RESULTS.md` — scalar ledger
- `phaseN-report.md` — reader-facing narrative with figures inline
- `expK/experiment-K.md` — per-experiment run cards
- `pNlib.py` — phase apparatus
- `result-format.md` — (phase1 only, applies globally) house style for figures + reporting

**Budget:** Read this skill and stop. No further files needed for an organization decision.

---

### `writing-report`
**Triggers on:** "write up results" / "write a report" / "how do I format" / "what goes in a summarize" / "write the phase report" / "how is a result documented"

**Body covers:**

**The document hierarchy** (what each file IS):
- `experiment-K.md` card — the atomic record: question → setup → run → result/figures → read → decision (the 6-slot structure). Written during/after a run. Audience: this team.
- `phaseN-summarize.md` — synthesis across all exps in this phase. What it means, what it overturned, what it decided. The one file an agent reads to understand this phase from the outside. Audience: future agents, collaborators, future-you.
- `RESULTS.md` — the scalar ledger. Numbers only, no prose. What ran, what the metric was, what the verdict was. Audience: quick reference.
- `phaseN-report.md` — reader-facing narrative with figures inline. The publishable-quality write-up. Audience: outside reader (professors, collaborators).
- `stageN-report.md` — the executive arc across all phases in a stage. Audience: outside reader coming in cold.
- `ref-report/` — glossary the reports cite: methods, metrics, papers. Audience: any report reader who needs a definition.

**Universal format principles** (apply across all drafts unless the draft overrides):
- Report results as **median + IQR** across seeds, never a single run
- Figures inline in the report file (not separate attachments)
- "Calling a difference real" rule: check IQR overlap before claiming a gap is meaningful
- Failures are data — log them in the card with the same rigor as successes
- The card's "read" slot is the interpretation; the "decision" slot is what changes (if anything)
- Each doc level has one audience — don't write a `summarize.md` for an outside reader or a `report.md` for internal use

**If a draft differs:** check draftN/.claude/skills/writing-report/SKILL.md for overrides. Root principles still apply unless explicitly superseded.

**Budget:** Read this skill. For draft-specific format files, check the draft's `src/phase1/result-format.md` (or equivalent).

---

## 5. draft6.0 Skills (Draft-Specific)

These are specific to how draft6.0 works. They override or extend root skills only where needed.

---

### `explore` (draft6.0)
**Triggers on:** "where are we" / "current status" / "what's phase 5" / "what did phase 4 find" / "what's the live plan" / "what's done and what's next"

**Body covers:**
- The phase ladder: P1 structure ✓ / P2 depth-r1 ✓ / P3 depth-r2 ADOPTED ✓ / P4 characterization ✓ / P5 optimization → (live)
- One-line verdict per phase + pointer to its `phaseN-summarize.md`
- What's solid vs open: the continual win is proven; contrast+coordination adopted; Phase 5 = sleep-cadence + Ch7-gate tuning + train-with-noise + natural-data
- The live decision record: `idea/main.ideas.v1.md` (committed N1–N3 + open knobs)
- Pointer to `src/stage1-report.md` for the full Stage 1 arc

**Budget:** Read this skill + at most one `phaseN-summarize.md`. For a full phase deep-dive, open that phase folder. For a multi-phase sweep, dispatch the Explore subagent.

---

### `run-experiment`
**Triggers on:** "run a phase" / "write an experiment" / "set up a test" / "plan an exp card" / "what's the next rung" / "run phase 5"

**Body covers:**
- Where the work is: `draft6.0/src/phaseN/` (one folder per phase; active phase = Phase 5)
- What to read first: the target `phaseN/README.md` (the spec) + `src/phase1/result-format.md` (house style)
- The methodology: one variable per experiment, standard seeds `[42, 137, 271, 314, 1729]`, median+IQR, failures are data
- Invariants to log every run: convergence/loss-slope, dead-unit fraction, ceiling/goodness saturation, inter-block drift (once chained)
- The card structure: 6 slots — question → setup → run → result/figures → read → decision
- Write-boundary: status in `main.ideas.v1.md`; run detail in `phaseN/expK/`; don't edit `ideas1.md` derivation chapters to log a run

**Budget:** Read this skill + the target `phaseN/README.md` + the one relevant `expK/` card. Prior-phase context = read that phase's `phaseN-summarize.md` only, never its code.

---

### `find-paper`
**Triggers on:** "find the paper behind" / "which paper covers" / "what's the evidence for" / "what does [X paper] say" / "where is the SCFF paper" / "the boosting paper"

**Body covers:**
- The two index files to read first: `research/papers/phase1-2/README.md` (design papers) and `research/papers/phase3/README.md` (the depth-reframe papers)
- The survey: `research/survey/summary.detail.md` (the learning-rule zoo — for "what else was considered")
- How to use the index: each entry names the paper + the file that holds its story; read the README to find the path, then open that one story file
- North-star dossier (`research/north-star/`) is free-time reading, not the live plan — don't open it to answer a design question

**Budget:** ≤3 index files (the two READMEs + survey summary). Never open a story file just to find which one is relevant — the index gives the path.

---

### `simulator-code`
**Triggers on:** "edit the sim" / "modify p4lib" / "touch pNlib" / "what does p4lib do" / "add a probe" / "run the 6.0 sim" / "where is the simulation code"

**Body covers:**
- The sim lives in `draft6.0/src/phase{1,2,3,4}/` — one folder per phase, each with its own apparatus
- `p4lib.py` is the Phase 4 shared library (the most feature-complete); earlier phases have `p1lib.py`, `p2lib.py`, `p3lib.py` layering progressively
- Per-phase structure: `pNlib.py` (the apparatus for that phase) + `run_pN_K.py` (run script per experiment) + `plot_pN_K.py` (figure script)
- The sim is a behavioral numpy sim (floats, ideal operators) — not a chip netlist. "Optimizing the Python" can quietly make it unbuildable. Correctness over speed.
- What "done means" for a code change: it runs, the result is loggable (one variable changed, multi-seed), the exp card is writable from the output
- Pointer to the active phase's `phaseN/README.md` for what Phase 5's code will need

**Budget:** Read this skill + the active `phaseN/README.md`. Open `p4lib.py` or `pNlib.py` only when you're modifying them, not for orientation.

---

## 6. Commands (Unchanged)

The four `/commands/` stay exactly as they are — thin triggers that point to `skill/workflows.md` today. After migration, they'll point to inline steps (the `workflows.md` content gets folded into the command files themselves, since `skill/` is being deleted).

| Command | Trigger | What it does |
|---|---|---|
| `/orient` | Explicit user move | Re-read + re-sync: load draft CLAUDE.md + status; report tight |
| `/checkpoint` | After completing a step | Record progress: update `main.ideas.v1.md` status + exp workspace |
| `/commit-progress` | When committing | Staged, categorized conventional commits with real bodies |
| `/double-check` | At step boundaries | 3-lens consistency audit: full-context / outsider / worker |

---

## 7. Migration — What to Delete

Once all new skills are written and tested:

| Old file | Action | Why |
|---|---|---|
| `skill/simulator-code.md` | Delete | Dead. Describes attribution sim. Replaced by draft6.0 `simulator-code` skill. |
| `skill/architecture-research.md` | Delete | Critical rot + replaced by draft6.0 `explore` skill (status ladder) + root `project-frame` |
| `skill/simulation-experiments.md` | Delete | Replaced by draft6.0 `run-experiment` skill |
| `skill/project-explore.md` | Delete | Split into root `project-frame` + root `explore` |
| `skill/sureSkill.md` | Delete | Index/meta-map → replaced by this document + per-skill descriptions |
| `skill/workflows.md` | Delete | Content folded into the four `.claude/commands/` files directly |
| `skill/` (folder) | Delete | Empty after above |

**`skill/workflows.md` migration note:** Before deleting, copy the step-by-step content of each workflow directly into the relevant `.claude/commands/*.md` file. Currently the commands just say "follow the workflow in skill/workflows.md" — that indirection goes away.

---

## 8. Build Order

1. **Root skills first** — they're the foundation; draft skills may reference them.
   - `folder-structure` (no dependencies)
   - `project-frame` (no dependencies)
   - `explore` (references folder-structure)
   - `writing-report` (no dependencies)

2. **Commands migration** — fold `workflows.md` content into the four command files; then `workflows.md` can be deleted.

3. **draft6.0 skills** — in order of "most likely to be triggered right now":
   - `explore` (Phase 5 is the live work; status is constantly needed)
   - `run-experiment` (Phase 5 experiments will start soon)
   - `simulator-code` (will be needed when Phase 5 code is written)
   - `find-paper` (lower urgency; triggered on architecture questions)

4. **Delete `skill/`** — after all skills are written and spot-tested (open a fresh session, run `/memory`, confirm the right skills load).

---

## 9. Settings Changes (Instant Token Savings)

Add to `.claude/settings.json` (or `settings.local.json`) after the skill migration:

```json
{
  "claudeMdExcludes": [
    "draft5.0/**",
    "draft-journey/**"
  ],
  "permissions": {
    "deny": [
      "Read(draft6.0/src/**/figs_*/*.npz)",
      "Read(draft6.0/src/**/figs_*/*.npy)"
    ]
  }
}
```

`claudeMdExcludes` stops the agent from auto-loading `draft5.0/CLAUDE.md` and `draft-journey/` on every session — they're fossils, not the live line.

The `deny` rules block large numpy figure arrays from being read — they're binary data in markdown-adjacent folders; an agent has no use for them and they waste context.
