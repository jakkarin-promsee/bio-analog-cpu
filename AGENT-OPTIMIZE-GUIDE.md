# AGENT-OPTIMIZE-GUIDE.md — keeping this repo cheap for agents

> **Who this is for.** Any AI agent (or future-you) working in this repo. This is the **maintenance contract**
> for the context system — the few rules that keep the project cheap to load and easy to navigate *as it grows.*
> If [`AGENT-OPTIMIZE-PLAN.md`](AGENT-OPTIMIZE-PLAN.md) is *why we built it this way* (with the research it's
> validated against), this is *how to keep it that way.* Read it before you add a file, finish a phase, or write
> a skill.

---

## The one principle

**Light top, deep on demand.** Context is layered so an agent loads a little and descends only into the branch
its task needs. Your job when maintaining the repo: **keep each layer in its lane — never let detail float up.**
The reason isn't only cost: an LLM's accuracy *drops* as irrelevant context grows ("context rot"), so a leaner
context is a *more correct* agent, not just a cheaper one.

## The layers, and what must stay true of each

- **Root `CLAUDE.md` + `AGENTS.md`** — always-loaded / cross-tool. **Stable, < ~130 lines, NO dated content.**
  Identity, collaboration + methodology rules, naming, the router. *If you're about to add a phase verdict or a
  status line here — stop. It belongs in `draftN/CLAUDE.md`.*
- **`draftN/CLAUDE.md`** — the draft's mental model + **current status ladder** + file map. The file that
  *changes* as work advances. Keep it under ~200 lines.
- **`draftN/src/phaseN/CLAUDE.md`** — a thin **signpost** (~25 lines): one-line verdict + pointers + a
  read-budget. Never restate the phase's results here; point to `phaseN-summarize.md`.
- **Skills (`.claude/skills/` + `draftN/.claude/skills/`)** — auto-load by description, **one task each**, every
  one ends with a read-budget. Universal skills at root; draft-specific ones under the draft.
- **Commands (`.claude/commands/`)** — explicit user moves only (`/orient`, `/checkpoint`, …); they never auto-fire.

## The maintenance moves (do them this way)

- **Finish a phase** → write the phase's `summarize` / `RESULTS` / cards, add a thin `phaseN/CLAUDE.md`, and bump
  the **one** status-ladder line in `draftN/CLAUDE.md`. **Do not touch the root.**
- **Add a draft** → copy the draft template (the `folder-structure` skill) — its own `CLAUDE.md` +
  `.claude/skills/`; add **one** router line to root `CLAUDE.md` and `AGENTS.md`. Mark the previous live draft
  historical with a `⚠️ Superseded` banner — the live/dead signal lives in **content**, not the folder name.
- **Add a skill** → only when a task type keeps making agents over-read. `.claude/skills/<name>/SKILL.md`;
  frontmatter `name:` + a **description that leads with the words a real request would contain**; body = what to
  read + the budget line. Put it under the draft if it's draft-specific.
- **Update status** → one source of truth: the `draftN/CLAUDE.md` ladder (+ `idea/main.ideas.vN.md`). Everything
  else **points**, never restates.

## What to optimize / watch for (drift signals)

- **Root creeping** past ~130 lines, or gaining a date/verdict → push it down to the draft.
- **The same fact in two files** → keep one, point from the other. Duplication rots — one copy goes stale.
- **An agent reading a phase's code/cards just to "understand" it** → the `phaseN-summarize.md` wasn't enough, or
  the signpost didn't say "read the summary only." Fix the summary or the signpost; don't accept the over-read.
- **A skill with no budget line, or a vague description** → it'll over-fire or over-read. Tighten it.
- **Reading binary outputs** (`figs_*/*.npz`, `*.npy`) → never useful; already denied in `.claude/settings.json`.

## The cheap escape hatches (use them)

- **Load your tier and stop.** To understand a *prior* phase, read its **one** `phaseN-summarize.md`.
- **Start the session in the subdirectory you're working in** — Claude Code then loads only that chain (root +
  that draft + that phase), nothing sideways. The single biggest cheap win.
- **Dispatch the `Explore` subagent** for read-heavy lookups — it reads in its own window and returns the
  conclusion, keeping the pages out of the main context.
- **`/memory`** shows what's actually loaded — use it to catch a rule that didn't load or a file that bloated.

## Self-check

Run **`/double-check`** at step boundaries (the 3-lens audit: full-context / outsider / worker). Periodically
re-read the root `CLAUDE.md` *cold* and ask: *is anything here dated, duplicated, or draft-specific?* If yes,
it has drifted up — push it down.

## See also

- [`AGENT-OPTIMIZE-PLAN.md`](AGENT-OPTIMIZE-PLAN.md) — the design + the practice it's validated against (Claude
  Code's large-codebase guide, Anthropic context-engineering, the `AGENTS.md` standard, Cursor's rules model).
- [`SKILL-PLAN.md`](SKILL-PLAN.md) — the skills-layer spec (what each skill is and why).
