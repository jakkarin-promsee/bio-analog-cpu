---
name: folder-structure
description: Decide where a file goes or how to add a phase or draft — the canonical repo / draft / phase layout. Use for "where does this file go", "add a new phase", "add a new draft", "how should I organize this", "the canonical structure".
---

# Canonical layout (where things go)

**Repo root:**
- `CLAUDE.md` (stable rules + router, **no status**) · `AGENTS.md` (cross-tool entry) · `README.md` (human overview)
- `draft6.0/` (live) · `draft5.0/` (history, superseded) · `draft-journey/` (the idea-journey log, drafts 1.0 → 5.1 — **not** `docs/draft/`)
- `docs/` (cross-draft: `essence/` = why + person, `draft/` = project-history + project-personal) · `.claude/` (commands + root skills) · `tools/`

**A `draftN/` contains:**
- `CLAUDE.md` — the draft's mental model + current status ladder (the file that changes when a phase advances)
- `README.md` (overview) · `context.md` (full cold-start) · `idea/` (decision record `main.ideas.vN.md` + derivation `ideasN.md`)
- `research/` — `survey/` (learning-rule zoo) · `papers/` (per-decision stories, split `phase1-2/` + `phase3/`) · `north-star/` (beyond-the-phases compass)
- `src/` — one `phaseN/` per phase + the report volumes (`stage1-report.md` · `stage2-report.md` · `validation-report.md`) + the `*-final-architecture.md` snapshots + `ref-report/` (glossary) · `.claude/skills/` (draft-specific skills)

**A `phaseN/` (under `src/`) contains:**
- `README.md` (**front-door synthesis — the one file to read from outside**) · `design.md` (the pre-run experiment design / codeable spec — a record, not an open to-do) · `CLAUDE.md` (thin signpost) · `RESULTS.md` (scalar ledger) · `phaseN-report.md` (reader-facing narrative + figures) · `result-format.md` (thin per-phase delta) · `expK/experiment-K.md` (run-cards) · `pNlib.py` (apparatus, where one exists) · figures in `figs_*/`
- The **canonical house style** lives once at `src/result-format.md`; each `phaseN/result-format.md` is a thin delta that inherits it.

**Adding a phase** → create `src/phaseN/` from the template + bump the one status-ladder line in `draft6.0/CLAUDE.md`. **Root untouched.**
**Adding a draft** → create `draftN/` from the template (its own `CLAUDE.md` + `.claude/skills/`) + add one router line to root `CLAUDE.md` and `AGENTS.md`.

**Budget:** read this skill, then act. No further files needed for an organization decision.
