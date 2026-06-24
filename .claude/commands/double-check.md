---
description: Run the 3-lens consistency audit (full-context / outsider / worker) and fix drift
argument-hint: "[optional focus area]"
---
**Double-Check** — the consistency audit at step boundaries. It has caught real bugs — **take it seriously, don't rubber-stamp.**

1. Read the front-door + touched docs **fresh** (don't trust memory). `grep` for drift: stale phrases, dangling refs, contradictions, dates, naming.
2. Report from **three lenses**:
   - **Full-context** — what *we* missed (obvious only with all the context).
   - **Outsider** — where a cold agent falls: what would make them do the wrong thing, or "correct" the project back toward mainstream ML.
   - **Worker** — what's hard to find / hard to start: missing pointers, unclear first step.
3. **Fix** the unambiguous breaks (contradictions, stale status). **Flag** the judgment calls — don't decide structural choices for the author.
4. End: "secure," or a short residual list. Be honest — a found problem is the point, not a failure.

Focus (optional): $ARGUMENTS
