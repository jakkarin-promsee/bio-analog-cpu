# `skill/workflows.md` — the recurring moves (soft-skill triggers)

> Small, repeatable workflows the author fires often. Each has a thin `/command` trigger in
> `.claude/commands/` (`/orient`, `/checkpoint`, `/commit-progress`, `/double-check`) — but the *real*
> steps live **here**, so they work whether invoked by slash command or by just asking ("commit it",
> "double-check this"). These are **routers + checklists**, not new rules: they point at the existing
> skill maps and the project's discipline.
>
> New here? Read `skill/project-explore.md` first — these assume the project frame (chip-not-ML;
> SCFF + GD, not the dead attribution rule; the committed draft-6.0 spine vs the open knobs the sims set).

---

## `/orient [code | experiment | arch]` — re-read & re-sync

The "get me up to speed / re-think before we continue" move.

1. Skim `CLAUDE.md` (already loaded) → `skill/project-explore.md` (the frame).
2. Read the live plan: `draft6.0/idea/main.ideas.v1.md` (decisions + "Status") and the experiment ladder
   in `draft6.0/idea/ideas1.md` (which rung we're on). For the whole picture cold: `draft6.0/context.md`.
3. If a focus arg is given, also load that lens — **code** → `skill/simulator-code.md` (historical `draft5.0-fossil/src/`;
   the 6.0 sim isn't written yet); **experiment** → `skill/simulation-experiments.md`; **arch** →
   `skill/architecture-research.md`.
4. Report **tight**: where we are · the frame · what's solid vs open · what I'd watch next. Flag any doc
   drift you notice in passing.

Orient, don't lecture — don't restate the whole spec.

## `/checkpoint` — record progress after a step

The "we just finished something, write it down before it's lost" move. (This is the discipline that kept
*slipping* — status not getting recorded — so fire it often.)

1. Update **status** in `draft6.0/idea/main.ideas.v1.md` ("Status"). If a run happened, record it in the
   experiment workspace (`draft6.0/src/phaseN/` — see its `README.md` and `skill/simulation-experiments.md`).
2. If the plan/rung shifted, sync the pointers that *name* it (CLAUDE.md "next action"; the skill maps'
   "where the work is now"). Keep **one source of truth** — `main.ideas.v1.md` status — and let others
   point to it, not restate it.
3. **Write-boundary:** status in `main.ideas.v1.md`, run detail in the experiment workspace. Don't edit the
   *derivation* chapters of `ideas1.md` to log a run — that's a decision, not a checkpoint.
4. Then suggest `/commit-progress`.

## `/commit-progress` — the organized commit

The categorized, readable commit dance (so the GitHub log reads as *progress*, not "wip").

1. `git status` — see what changed since HEAD. **Never `git add -A` blindly**; stage by group.
2. **Group by category**, one commit each: `feat:` for simulator code; `docs:` for docs / plan / notes /
   skill. Split new-content from wiring/consistency when that's cleaner.
3. Each commit: a conventional `type: subject` **plus a real body** (what + why, written for a reader —
   same bar as a phase log), ending with the trailer:
   `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
4. Commit on **`main`** — the working branch for this solo project; the GitHub progress log lives there.
   **Do not push** unless asked: offer `git push origin main`, and note HTTPS may want a login (run
   `!git push origin main` so the auth prompt works).
5. Report the new log + confirm a clean tree. `LF→CRLF` warnings are benign (Windows), not errors.

## `/double-check` — the two-verify / 3-lens audit

The consistency audit the author fires at step boundaries ("check the whole project"). It has caught real
bugs — **take it seriously, don't rubber-stamp.**

1. Read the front-door + touched docs **fresh** (don't trust memory). `grep` for drift: stale phrases,
   dangling refs, contradictions, dates, naming.
2. Report from **three lenses**:
   - **Full-context** — what *we* missed (obvious only with all the context).
   - **Outsider** — where a cold agent *falls*: what would make them do the wrong thing, or "correct" the
     project back toward mainstream ML.
   - **Worker** — what's *hard to find / hard to start*: missing pointers, unclear first step.
3. **Fix** the unambiguous breaks (contradictions, stale status). **Flag** the judgment calls — don't
   decide structural choices for the author.
4. End: "secure," or a short residual list. Be honest — a found problem is the point, not a failure.

---

_Add a move here when a manual ritual repeats 3+ times. Keep each a tight checklist; the depth lives in the
skill maps these point to. The `/command` triggers in `.claude/commands/` should stay thin — this file is
where the steps change._
