---
description: Record progress after a step (update the live plan status + experiment logs)
argument-hint: "[short note on what we just did]"
---
**Checkpoint** — record where we are before it's lost. (This is the discipline that keeps *slipping* — fire it often.)

1. Update **status** in `draft6.0/idea/main.ideas.v1.md`, and the status ladder in `draft6.0/CLAUDE.md` if a phase advanced. If a run happened, record it in the experiment workspace (`draft6.0/src/phaseN/` — see the `run-experiment` skill).
2. Keep **one source of truth** (the status); other pointers reference it, they don't restate it.
3. **Write-boundary:** status in `main.ideas.v1.md` + the ladder; run detail in `phaseN/expK/`. Don't edit the *derivation* chapters of `ideas1.md` to log a run — that's a decision, not a checkpoint.
4. Then suggest `/commit-progress`.

What we just did (optional): $ARGUMENTS
