---
name: writing-report
description: Write up or format results — which document is which (card / summarize / RESULTS / report / stage-report) and the house-style rules. Use for "write up results", "write a report", "what goes in a summarize", "how is a result documented", "how do I format this".
---

# Documenting a result

**The document hierarchy (each has ONE audience):**
- `expK/experiment-K.md` **card** — the atomic record, 6 slots: *question → setup → run → result/figures → read → decision*. Written during/after a run. Audience: this team.
- `phaseN-summarize.md` — synthesis across the phase: what it means, what it overturned, what it decided. **The one file to read to understand a phase from outside.** Audience: future agents / collaborators / future-you.
- `RESULTS.md` — the scalar ledger: numbers + verdict, no prose. Audience: quick reference.
- `phaseN-report.md` — reader-facing narrative, figures inline, publishable quality. Audience: outside reader (professors).
- `stageN-report.md` — the executive arc across a whole stage. Audience: cold outside reader.
- `ref-report/` — the glossary the reports cite (methods · metrics · papers).

**Format rules (apply across all drafts unless a draft overrides):**
- Report **median + IQR** across the standard seeds `[42, 137, 271, 314, 1729]`, never a single run.
- "Calling a difference real" = check IQR overlap *before* claiming a gap is meaningful.
- **Failures are data** — log them in the card with the same rigor as successes.
- The card's *read* slot is the interpretation; the *decision* slot is what changes (if anything).
- Don't cross audiences — no outside-reader prose in a `summarize`, no internal shorthand in a `report`.

**Budget:** read this skill. Draft-specific figure/house style → `draft6.0/src/phase1/result-format.md`.
