---
name: writing-report
description: Write up or format results — which document is which (card / summarize / RESULTS / report / stage-report) and the house-style rules. Use for "write up results", "write a report", "what goes in a summarize", "how is a result documented", "how do I format this".
---

# Documenting a result

## The document hierarchy:

**Working log:**
Write while running each experiment. Step by step. Heavy at text, because it's result log for author and ai agent. Have no writing rule, just a freestyle log file.

- `expK/experiment-K.md` **card** — the atomic record, 6 slots: _question → setup → run → result/figures → read → decision_. Written during/after a run. Audience: this team.
- `phaseN-summarize.md` — synthesis across the phase: what it means, what it overturned, what it decided. **The one file to read to understand a phase from outside.** Audience: future agents / collaborators / future-you.
- `RESULTS.md` — the scalar ledger: numbers + verdict, no prose. Audience: quick reference.

**Public Document:**

Use to public the phase. Each report should have similar writing style and format. story telling style (because each phase and exp is update from previous result) such as "What is our problem?", "Qhat is our purpose on this phase and each experiment?", "What is the thing we found?", "what is the result mean?", etc. By this report.md will have those image, graph, table, etc. Making it ready for other researcher to read.

The final structure should look like a clean, professional research repository: consistent naming, logical hierarchy, and easy for anyone (including future-me) to navigate. And each report can reuse to be refferences of future experiment.

Audience: professional researcher / professor / future agents / collaborators / future-you.

- `phaseN-report.md` — reader-facing narrative, figures inline, publishable quality. Audience: outside reader.
- `stageN-report.md` — the executive arc across a whole stage. Audience: cold outside reader.
- `ref-report/` — the glossary the reports cite (methods · metrics · papers).

**Format rules (apply across all drafts unless a draft overrides):**

- Report **median + IQR** across the standard seeds `[42, 137, 271, 314, 1729]`, never a single run.
- "Calling a difference real" = check IQR overlap _before_ claiming a gap is meaningful.
- **Failures are data** — log them in the card with the same rigor as successes.
- The card's _read_ slot is the interpretation; the _decision_ slot is what changes (if anything).
- Don't cross audiences — no outside-reader prose in a `summarize`, no internal shorthand in a `report`.

**Budget:** read this skill. Draft-specific figure/house style → `draft6.0/src/phase1/result-format.md`.
