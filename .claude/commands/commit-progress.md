---
description: Stage and commit current work in organized, categorized conventional commits
argument-hint: "[optional scope hint]"
---
Commit the current progress, following the **Commit-Progress** workflow in `skill/workflows.md`:
`git status`, group by category (`feat:` code / `docs:` docs), one conventional commit per group with a
real body + the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer, on `main`. **Do not
push** — offer it. Report the log + clean tree.

Scope hint (optional): $ARGUMENTS
