# `src/experiment/` — the experiment workspace

> Where experiments actually happen. Each phase of the live plan (`../../draft5.1-2.verify.md`) gets a
> folder here holding its scripts, its figures, and its written log.
>
> **The split — don't duplicate:**
>
> - `draft5.1-2.verify.md` (root) = the **whiteboard / plan**: the topic, the intent, what we're doing now
>   and why. *Forward-looking.* Grows phase by phase.
> - `src/experiment/phaseN/` = the **record**: what we actually ran and found. *Backward-looking.* Each
>   phase is entered through its own `README.md`.
>
> Each fact lives in exactly one place: intent in the verify doc, results here.

## Layout

```
src/experiment/
  README.md              # this file — the workspace map + conventions
  phase1/
    README.md            # phase index: goal, experiment list, status, headline findings, read-order
    experiment-1.md      # one experiment: question -> setup -> run -> result (figures) -> read -> decision
    experiment-2.md
    <scripts>.py         # import the frozen ../../library unchanged; never edit library/ per experiment
    figures/             # the committed "see with eyes" plots the .md logs reference
  phase2/
    ...
```

## Conventions

- **Enter a phase through its `README.md`.** It says what's there and what to read, in order — the same
  front-door idea as the `explore` / `project-frame` skills, scoped to one phase.
- **One experiment per `experiment-{n}.md`.** Write it for a *reader*, not just to save — same bar as a
  good commit message. Skeleton lives in `phase1/README.md`.
- **`library/` is frozen.** Experiment scripts import it unchanged and add their own assembly. If you need
  to change `library/`, that's a `simulator-code` task (see the `simulator-code` skill), not an experiment.
- **Imports:** mirror `src/example/run_xor.py` (it sets `sys.path` so `from src.library import ...` works
  when run from the repo root).
- **Figures:** commit the summary plots the logs reference (the deliverable). Dump raw/bulk sweeps to
  `runs/` (git-ignored, per draft5.1-2.md §20.19), not here.

## Write-boundary for agents

A picking-up agent works in **exactly two places**: it updates **status** in `draft5.1-2.verify.md`, and
it works **inside `src/experiment/`**. The locked spec (`draft5.1-1.md`, §22) and the frozen `src/library/`
are **not** experiment surfaces — changing them is a different kind of task with its own skill map.

## Phases

| Phase | Topic | Plan (intent) | Status |
| --- | --- | --- | --- |
| `phase1/` | Ganglion personality — characterize the atom | `draft5.1-2.verify.md` → Phase 1 | not started |

(Rows are added here as phases are drafted in the verify doc. The planned top-level `reports/` is likely
redundant now — a phase's `README.md` is its report; retire/repurpose `reports/` once confirmed.)
