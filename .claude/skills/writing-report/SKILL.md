---
name: writing-report
description: Write up or format a result at every tier — which document is which (design / working log / card / RESULTS / README front door / report / stage-report), WHO each is for and WHEN it's written, and the house-style rules. Use for "write up results", "write a report", "what goes in the README", "where does the design/plan go", "how should the phase README look", "how is a result documented", "how do I format this".
---

# Documenting a result

A result is written **up the tiers** — from a freestyle log while you run, to structured internal records, to a
public-facing front door + report. **Each file has ONE job, ONE audience, and ONE moment in the work; don't cross
them.** The whole set splits into two buckets by _when you write it and who reads it_:

- **Internal records** — written **while the experiment is running**, for **you, future-you, and agents** (the
  people inside the work who need to act on it, not be impressed by it).
- **Public documents** — written **once the experiment/phase is complete and you move to the next topic**, for an
  **outside reader** (a professor, another researcher, or future-you returning cold after years).

The `README.md` is the hinge between the two: the _one_ place the internal work becomes the public front door. It
has a single duty (the front-door synthesis) — the pre-run plan it used to _also_ carry now lives in `design.md`,
so the README is never overwritten and no context is lost.

---

## Internal records — for you, future-you, and agents _(while the work is live)_

While running, keep a **freestyle working log**: step by step, text-heavy, no rules — raw notes for both the author
and the agent. It is scratch, not a deliverable. After the run, distill it into the structured records:

- **`design.md`** — the **pre-run design + build spec** for the phase: _what to test_ (the experiment ladder),
  _what to build_ (the component checklist), the controlled setup, the open knobs. Written **before** the runs.
  **It is a record, not an open to-do** — named `design.md` (not `plan.md`) on purpose, so a _finished_ phase's
  spec never reads as a live task list. For a completed phase it is historical (the results live in `README.md`)
  and is **not** rewritten (period-correct); only an _active_, not-yet-run phase's `design.md` is a spec an agent
  executes.
- **`expK/experiment-K.md` card** — the atomic record, 6 slots: _question → setup → run → result/figures → read →
  decision_. Written during/after a run. The _read_ slot is the interpretation; the _decision_ slot is what
  changes (if anything).
- **`RESULTS.md`** — the scalar ledger: numbers + verdict, one row per experiment, **no prose**.

These exist so future-you or another agent can **act on the result without re-running it** — make the next
decision, catch a wrong conclusion via the stated confound, inherit a set knob. They are not there to look good.

---

## Public documents — for an outside reader _(once the phase is done, before the next topic)_

The **published face** of a phase, written when the experiment/phase closes and the work moves on. Story-style and
**consistent across phases** (each phase builds on the last): _what was the problem? what was this phase/experiment
for? what did we find? what does the result mean?_ Figures, graphs, and tables inline — ready for an outside
researcher to read cold, and reusable as a reference for later experiments. The bar is a **clean, professional
research repo**: consistent naming, logical hierarchy, easy for anyone (including future-you) to navigate.

- **`README.md` — the front door (single duty).** The **navigable synthesis** of the phase: _Problem → Experiment
  → Result (key figure inline) → Decision/verdict_, then a **links table** out to the report, `RESULTS.md`,
  `design.md`, and the cards. Short (~80–120 lines). This is the file an outside reader **lands on** _and_ the agent
  **read-budget target** ("to understand a phase from outside, read `README.md` only"). Model it on
  `draft6.0/README.md` (the draft-level front door done right). It **absorbs the old "phase summary" role** — there
  is no separate `phaseN-summarize.md`.
- **`phaseN-report.md`** — the **deep** reader-facing narrative: every figure inline, the per-experiment story,
  publishable quality. The README links here for the full account.
- **`result-format.md`** — the **canonical house style** lives once at `draft6.0/src/result-format.md` (figures,
  metrics, reproducibility, the 6-slot template). Each phase keeps a _thin_ `phaseN/result-format.md` that
  **inherits** the canonical and adds only that phase's new figures.
- **`stageN-report.md`** — the executive arc across a whole stage (many phase). Audience: a cold outside reader.
- **`ref-report/`** — the glossary the reports cite (methods · metrics · papers).

---

**The file set per phase — one job each (don't add a sixth prose file):**
`README.md` (front door / synthesis) · `design.md` (pre-run design) · `phaseN-report.md` (deep story) ·
`RESULTS.md` (scalar ledger) · `result-format.md` (thin delta → canonical) · `CLAUDE.md` (agent signpost) ·
`expK/experiment-K.md` (cards). If you feel the urge to write a "summary" file, that's the README's job — put it there.

**Format rules (apply across all drafts unless a draft overrides):**

- Report **median + IQR** across the standard seeds `[42, 137, 271, 314, 1729]`, never a single run.
- "Calling a difference real" = check IQR overlap _before_ claiming a gap is meaningful.
- **Failures are data** — log them in the card with the same rigor as successes.
- The card's _read_ slot is the interpretation; the _decision_ slot is what changes (if anything).
- **Don't cross audiences** — no internal shorthand in a public `report`; no pre-run plan content padding the
  README front door; no prose creeping into `RESULTS.md`.

**Budget:** read this skill. Canonical figure/house style → `draft6.0/src/result-format.md` (per-phase additions
in `draft6.0/src/phaseN/result-format.md`).
