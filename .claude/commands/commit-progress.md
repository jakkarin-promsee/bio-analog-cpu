---
description: Stage and commit current work in organized, categorized conventional commits
argument-hint: "[optional scope hint]"
---
**Commit-Progress** — the categorized, readable commit (so the log reads as *progress*, not "wip").

1. `git status` — see what changed since HEAD. **Never `git add -A` blindly**; stage by group.
2. **Group by category**, one commit each: `feat:` for simulator code · `docs:`/`refactor:` for docs, plan, notes, skills, structure. Split new-content from wiring/consistency when that's cleaner.
3. Each commit: a conventional `type: subject` **plus a real body** (what + why, written for a reader — same bar as a phase log), ending with the trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
4. Commit on the **current working branch**. **Do not push** unless asked — offer it, and note HTTPS may want a login (run `!git push …` so the auth prompt works).
5. Report the new log + confirm a clean tree. `LF→CRLF` warnings are benign (Windows), not errors.

Scope hint (optional): $ARGUMENTS
