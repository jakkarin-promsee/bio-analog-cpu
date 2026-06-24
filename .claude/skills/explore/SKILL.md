---
name: explore
description: Navigate this repository — where things live, how it's organized, draft-5 vs draft-6, the 3-layer context hierarchy. Use for "where is X", "how is this repo structured", "how do I navigate this", "what is in draft5 vs draft6".
---

# Navigating the repo

**The 3-layer context hierarchy (loaded lazily — load your tier and stop):**
- `CLAUDE.md` (root, always loaded) = identity + rules + router.
- `draftN/CLAUDE.md` (auto-loads when you work in that draft) = its architecture, **current status**, file map.
- `draftN/src/phaseN/CLAUDE.md` = a thin signpost to that phase's authoritative record.

**What lives where:**
- `draft6.0/` — the **live line** (SCFF + GD). Start here for any current work.
- `draft5.0/` — **history** (the attribution era, superseded). `draft-journey/` — the **idea-journey log** (drafts 1.0 → 5.1); *not* `docs/draft/`.
- `docs/` — cross-draft reference: `docs/essence/` (the why + the person), `docs/draft/` (project-history, project-personal).
- `AGENTS.md` — cross-tool front door · `README.md` — human overview · `tools/` — the spec → Word toolchain.

**Read efficiently:** to understand a draft, load its `CLAUDE.md`; to understand a *prior* phase, read its one
`phaseN-summarize.md` — not its code. For "what IS this project" load the **`project-frame`** skill; for "where
are we / current status" load draft 6's **`status`** skill.

**Routing:** working on Phase 5 → start in `draft6.0/`; why an old decision was made → `docs/draft/project-history.md`;
the idea journey → `draft-journey/`.

**Budget:** this skill + one target `CLAUDE.md`. For a full repo sweep, dispatch the `Explore` subagent.
