# AGENT-OPTIMIZE-GUIDE.md — keeping this repo cheap for agents

> **Who this is for.** Any AI agent (or future-you) maintaining this repo. This is the **single guide** to the
> agent-context system — how it's shaped, *why*, and how to keep it lean as the project grows. It folds in the
> two build docs it replaces (the retired `AGENT-OPTIMIZE-PLAN.md` and `SKILL-PLAN.md` — the build is done, so
> the plans became this guide). Read it before you add a file, finish a phase, write a skill, or start a draft.
>
> **The job this guide protects:** the repo must stay (a) clean for the professors/paper, and (b) cheap for AI
> agents to load and work in. Those pull the same direction — *less, in the right place.*

---

## 1. The one principle

**Light top, deep on demand.** Context is layered so an agent loads a little and descends only into the branch its
task needs. Your job when maintaining the repo: **keep each layer in its lane — never let detail float up.** The
reason isn't only token cost: an LLM's accuracy *drops* as irrelevant context grows ("context rot" — finite
attention budget), so a leaner context is a *more correct* agent, not just a cheaper one.

The two axes everything is organized by:
- **Stable vs shifting** — rules/identity that never change (root) vs status that changes every phase (per-draft).
- **Altitude** — *map* (where things are) → *mental model* (how a draft thinks) → *detail* (results/code).

---

## 2. The layered structure — what each layer holds, what must stay true

```
root CLAUDE.md + AGENTS.md   (always / cross-tool)   MAP + rules     stable, < ~130 lines, NO dated content
  └ draftN/CLAUDE.md         (auto-loads in-draft)   MENTAL MODEL    architecture + status ladder + map, < ~200
      └ phaseN/CLAUDE.md     (auto-loads in-phase)   SIGNPOST        ~25 lines: verdict + pointers + read-budget
          └ phaseN/README.md (front-door synthesis = read first) → phaseN-report.md / RESULTS.md / design.md / expK/ …   DETAIL   on demand
```

- **Root `CLAUDE.md` + `AGENTS.md`** — always-loaded / cross-tool. Identity, collaboration + methodology rules,
  naming, the router. *If you're about to add a phase verdict or a status line here — stop; it belongs in
  `draftN/CLAUDE.md`.* `AGENTS.md` is the same orientation for non-Claude tools (the open standard).
- **`draftN/CLAUDE.md`** — the draft's mental model + **current status ladder** + file map. The file that *changes*
  as work advances.
- **`draftN/src/phaseN/CLAUDE.md`** — a thin **signpost**: one-line verdict + pointers + a read-budget. Never
  restate the phase's results; point to `phaseN/README.md` (the front-door synthesis).
- **Skills** (`.claude/skills/` + `draftN/.claude/skills/`) — auto-load by description, one task each, with a
  read-budget. §3.
- **Commands** (`.claude/commands/`) — explicit user moves only; they never auto-fire.

**Canonical folder template** (or just invoke the `folder-structure` skill): a `draftN/` holds `CLAUDE.md` ·
`README.md` · `context.md` · `idea/` (`main.ideas.vN.md` + `ideasN.md`) · `research/` (`survey/` · `papers/` ·
`north-star/`) · `src/` (one `phaseN/` each + `stageN-report.md` + `result-format.md` + `ref-report/`) ·
`.claude/skills/`. A `phaseN/` holds `README.md` (front-door synthesis — the one file to read from outside) ·
`design.md` (pre-run experiment design / spec — a record, not a to-do) · `CLAUDE.md` (signpost) · `RESULTS.md` ·
`phaseN-report.md` (deep narrative) · `result-format.md` (thin delta) · `expK/` · `pNlib.py` · figures in `figs_*/`.

---

## 3. The skills — the catalog and the rules

**The rules (every skill):**
- Native form: `.claude/skills/<name>/SKILL.md`, frontmatter `name:` + a **`description:` that leads with the
  words a real request would contain** (it's truncated when many skills exist, so keyword-front matters).
- Body = *what to read* + a **read-budget line** ("load these and stop; heavier → dispatch the Explore subagent").
- **One task each.** Universal skills live at root; draft-specific ones under the draft (and may differ by
  name from a root skill — they don't override by name, so don't reuse a root skill's name).
- **Commands stay commands** — deliberate moves (`/orient` …) never become auto-firing skills.

**The catalog (built 2026-06-24):**

| Skill | Where | Fires on |
| --- | --- | --- |
| `project-frame` | `.claude/skills/` | "what is this project", "is this ML", "what's SCFF" — the chip-not-model frame + the wrong reflexes |
| `explore` | `.claude/skills/` | "where is X", "how is this repo organized", "draft5 vs draft6" |
| `folder-structure` | `.claude/skills/` | "where does this file go", "add a phase/draft", the canonical layout |
| `writing-report` | `.claude/skills/` | "write up results", "what goes in the README", "where does the design go", the doc hierarchy + house style |
| `status` | `draft6.0/.claude/skills/` | "where are we", "current status", "what did phase N find", "what's next" |
| `run-experiment` | `draft6.0/.claude/skills/` | "run a phase", "write an experiment", the methodology + card structure |
| `find-paper` | `draft6.0/.claude/skills/` | "the paper behind X", "which paper covers", the paper indexes |
| `simulator-code` | `draft6.0/.claude/skills/` | "edit the sim", "modify pNlib", "add a probe" — it's a chip netlist |

---

## 4. The native mechanisms (the levers Claude Code gives you)

| Mechanism | What it does | Use for |
| --- | --- | --- |
| **Per-directory `CLAUDE.md`** | lazy-loads with its subtree (root + ancestors at launch; a subdir's only when read) | the layer-2/3 files |
| **`.claude/skills/<name>/SKILL.md`** (`description`, optional `paths:`) | model auto-loads the skill when the task matches; only the chosen one's body enters context | task-scoped routing (§3) |
| **`permissions.deny` → `Read(...)`** (`.claude/settings.json`) | blocks reading paths | binary figure arrays (`figs_*/*.npz|*.npy`) — already set |
| **`SessionStart` hook** (`.claude/settings.json` + `.claude/hooks/`) | prints an orientation banner into context at launch | nudge every session toward the skills + load-your-tier rule — already set |
| **Start Claude *in* a subdirectory** | loads only that dir + ancestors | scope a session to one phase/draft (biggest cheap win) |
| **Subagents** (`Explore`) | read in an isolated window, return a ~1–2k summary | read-heavy lookups (the context wall) |
| **`claudeMdExcludes`** | never-load specific `CLAUDE.md` | *deliberately unused now* — with one live draft, lazy-load already keeps siblings out, and excluding the fossil's CLAUDE.md only drops context when you *do* work there. Revisit when drafts multiply. |

---

## 5. The maintenance moves (do them this way)

- **Finish a phase** → write the phase's `README` (front-door synthesis) / `RESULTS` / cards, add a thin `phaseN/CLAUDE.md`, and bump
  the **one** status-ladder line in `draftN/CLAUDE.md`. **Do not touch the root.**
- **Add a draft** → copy the draft template (the `folder-structure` skill) — its own `CLAUDE.md` + `.claude/skills/`;
  add **one** router line to root `CLAUDE.md` and `AGENTS.md`. Mark the previous live draft historical with a
  `⚠️ Superseded` banner — the live/dead signal lives in **content**, not the folder name.
- **Add a skill** → only when a task type keeps making agents over-read. Follow the §3 rules.
- **Update status** → one source of truth: the `draftN/CLAUDE.md` ladder (+ `idea/main.ideas.vN.md`). Everything
  else **points**, never restates.
- **Move/rename anything** → fix every reference (`git mv` to keep history; grep the old token to zero), and run a
  link check. The link web is the real cost of any move, not the move itself.

---

## 6. What to optimize / watch for (drift signals)

- **Root creeping** past ~130 lines, or gaining a date/verdict → push it down to the draft.
- **The same fact in two files** → keep one, point from the other. Duplication rots — one copy goes stale.
- **An agent reading a phase's code/cards just to "understand" it** → the `README` wasn't enough, or the
  signpost didn't say "read the README only." Fix the README/signpost; don't accept the over-read.
- **A skill with no budget line, or a vague description** → it over-fires or over-reads. Tighten it.
- **Reading binary outputs** (`figs_*/*.npz|*.npy`) → never useful; already denied in `.claude/settings.json`.
- **A `draftN/CLAUDE.md` ballooning** → its detail belongs in `context.md` or the phase files; keep it a map.

---

## 7. The cheap escape hatches (use them)

- **Load your tier and stop.** To understand a *prior* phase, read its **one** `phaseN/README.md` (front-door synthesis).
- **Start the session in the subdirectory you're working in** — loads only that chain. The biggest cheap win.
- **Dispatch the `Explore` subagent** for read-heavy lookups — it returns the conclusion, not the pages.
- **`/memory`** shows what's actually loaded — use it to catch a rule that didn't load or a file that bloated.

---

## 8. Self-check

Run **`/double-check`** at step boundaries (the 3-lens audit: full-context / outsider / worker). Periodically
re-read the root `CLAUDE.md` *cold* and ask: *is anything here dated, duplicated, or draft-specific?* If yes, it
has drifted up — push it down.

---

## 9. Why this shape (validated — so you trust it)

The problems this solved (measured 2026-06): the always-loaded root `CLAUDE.md` was 240 lines reloaded every
session; agents over-read (researching phase 4 pulled all of phase 2/3, ~1,000+ lines, for a one-line fact); the
root was rewritten every phase (the most volatile content in the always-loaded file); skill maps were flat,
manual-load, and carried rot.

The shape above is **not bespoke** — it matches the consensus of:
- **Claude Code — [large-codebase guide](https://code.claude.com/docs/en/large-codebases)** (per-directory
  `CLAUDE.md`, lazy load, `claudeMdExcludes`, `.claude/skills/`, `permissions.deny`, start-from-subdir, subagents).
- **Anthropic — [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)**
  (just-in-time loading, progressive disclosure, sub-agent isolation, context rot, "right altitude").
- **[AGENTS.md](https://agents.md/)** — the cross-tool standard (30+ tools); we keep a self-contained `AGENTS.md`
  at root so non-Claude tools get oriented too.
- **[Cursor rules](https://cursor.com/docs/rules)** — the Always / Auto-glob / Agent-requested / Manual load model.
