---
name: writing-report
description: Write up or format a result at every tier — which document is which (working log / card / summarize / RESULTS / report / stage-report / README) and the house-style rules. Use for "write up results", "write a report", "what goes in a summarize", "how should the phase README look", "how is a result documented", "how do I format this".
---

# Documenting a result

A result is written **up the tiers** — from a freestyle log while you run, to structured internal records, to a public report. **Each tier has ONE audience; don't cross them.**

**Internal records — for you, future-you, and agents.**
While running, keep a **freestyle working log**: step by step, text-heavy, no rules — raw notes for both the author and the agent. After the run, distill it into the three structured records:

- `expK/experiment-K.md` **card** — the atomic record, 6 slots: *question → setup → run → result/figures → read → decision*. Written during/after a run.
- `phaseN-summarize.md` — synthesis across the phase: what it means, what it overturned, what it decided. **The one file to read to understand a phase from outside.**
- `RESULTS.md` — the scalar ledger: numbers + verdict, no prose.

**Public documents — for an outside reader (professor / researcher / future-you).**
The published face of a phase. Story-style and consistent across phases (each phase builds on the last): *what was the problem? what was this phase/experiment for? what did we find? what does the result mean?* Figures, graphs, and tables inline — ready for an outside researcher to read, and reusable as a reference for later experiments. Aim for a clean, professional research repo: consistent naming, logical hierarchy, easy for anyone (including future-you) to navigate.

- `phaseN-report.md` — reader-facing narrative, figures inline, publishable quality.
- `stageN-report.md` — the executive arc across a whole stage. Audience: cold outside reader.
- `ref-report/` — the glossary the reports cite (methods · metrics · papers).

**The README bridge — `README.md` (per phase/exp).**
Lives a two-stage life. *While the experiment runs*, it doubles as the working log — progress + a running result summary. *Once the phase is done and the report is written*, rewrite it into public-document form: a short Problem / Experiment / Result / Decision overview, figures inline, linking out to the full report. The end state is a **rich, navigable README** — publishable quality, outside-reader facing.

**Format rules (apply across all drafts unless a draft overrides):**

- Report **median + IQR** across the standard seeds `[42, 137, 271, 314, 1729]`, never a single run.
- "Calling a difference real" = check IQR overlap *before* claiming a gap is meaningful.
- **Failures are data** — log them in the card with the same rigor as successes.
- The card's *read* slot is the interpretation; the *decision* slot is what changes (if anything).
- Don't cross audiences — no outside-reader prose in a `summarize`, no internal shorthand in a `report`.

**Budget:** read this skill. Draft-specific figure/house style → `draft6.0/src/phase1/result-format.md`.
