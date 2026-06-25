---
name: writing-report
description: Write up or format a result at every tier — which document is which (design / working log / card / RESULTS / README front door / report / stage-report) and the house-style rules. Use for "write up results", "write a report", "what goes in the README", "where does the design/plan go", "how should the phase README look", "how is a result documented", "how do I format this".
---

# Documenting a result

A result is written **up the tiers** — from a freestyle log while you run, to structured internal records, to a
public-facing front door + report. **Each file has exactly ONE job; don't blur them.** (One file ≠ two duties:
the README is *not* also the pre-run plan — that's `design.md`. This split is deliberate; it's why a reader landing
in a phase folder hits the result, not the pre-run design.)

**Internal records — for you, future-you, and agents.**
- **freestyle working log** (*while running*): step by step, text-heavy, no rules — raw notes for both the author
  and the agent. Scratch; not a deliverable.
- **`design.md`** — the **pre-run design + build spec** for the phase: *what to test* (the experiment ladder), *what
  to build* (the component checklist), the controlled setup, the open knobs. Written **before** the runs and kept
  as the record of what was proposed. **It is a record, not an open to-do** — named `design.md` (not `plan.md`) on
  purpose, so a *finished* phase's spec never reads as a live task list. For a completed phase it is **historical**
  (the results live in the `README.md`) and is **not** rewritten (period-correct); only an *active*, not-yet-run
  phase's `design.md` is a spec the agent executes.
- **`expK/experiment-K.md` card** — the atomic record, 6 slots: *question → setup → run → result/figures → read →
  decision*. Written during/after a run.
- **`RESULTS.md`** — the scalar ledger: numbers + verdict, one row per experiment, **no prose**.

**Public documents — for an outside reader (professor / researcher / future-you).**
- **`README.md` — the front door (single duty).** The **navigable synthesis** of the phase: *Problem → Experiment
  → Result (key figure inline) → Decision/verdict*, then a **links table** out to the report, `RESULTS.md`,
  `design.md`, and the cards. Short (~80–120 lines). This is the file an outside reader **lands on** *and* the agent
  **read-budget target** ("to understand a phase from outside, read `README.md` only"). Model it on
  `draft6.0/README.md` (the draft-level front door done right). It **absorbs the old "phase summary" role** — there
  is no separate `phaseN-summarize.md`.
- **`phaseN-report.md`** — the **deep** reader-facing narrative: every figure inline, the per-experiment story,
  publishable quality. The README links here for the full account.
- **`stageN-report.md`** — the executive arc across a whole stage. Audience: cold outside reader.
- **`result-format.md`** — the **canonical house style** lives once at `draft6.0/src/result-format.md` (figures,
  metrics, reproducibility, the 6-slot template). Each phase keeps a *thin* `phaseN/result-format.md` that
  **inherits** the canonical and adds only that phase's new figures.
- **`ref-report/`** — the glossary the reports cite (methods · metrics · papers).

**The file set per phase — one job each (don't add a sixth prose file):**
`README.md` (front door / synthesis) · `design.md` (pre-run design) · `phaseN-report.md` (deep story) ·
`RESULTS.md` (scalar ledger) · `result-format.md` (thin delta → canonical) · `CLAUDE.md` (agent signpost) ·
`expK/experiment-K.md` (cards). If you feel the urge to write a "summary" file, that's the README's job — put it there.

**Format rules (apply across all drafts unless a draft overrides):**

- Report **median + IQR** across the standard seeds `[42, 137, 271, 314, 1729]`, never a single run.
- "Calling a difference real" = check IQR overlap *before* claiming a gap is meaningful.
- **Failures are data** — log them in the card with the same rigor as successes.
- The card's *read* slot is the interpretation; the *decision* slot is what changes (if anything).
- **Don't blur jobs** — no pre-run design content padding the README front door; no internal shorthand in a
  `report`; no prose creeping into `RESULTS.md`.

**Budget:** read this skill. Canonical figure/house style → `draft6.0/src/result-format.md` (per-phase additions
in `draft6.0/src/phaseN/result-format.md`).
