---
name: run-experiment
description: Plan, write, or run a draft-6 phase experiment — the sim ladder, the methodology, the exp-card structure. Use for "run a phase", "write an experiment", "set up a test", "plan an exp card", "the next rung", "run phase 5".
---

# Running a draft-6 experiment

**Where the work is:** `draft6.0/src/phaseN/` (one folder per phase; the active phase is **Phase 5**).
**Read first:** the target `phaseN/README.md` (the codeable spec) + `draft6.0/src/phase1/result-format.md` (house style). Prior-phase context = read that phase's `phaseN-summarize.md` **only**, never its code.

**Methodology (non-negotiable):**
- **One variable** changed per experiment; lock everything else (task, init, weight count, steps, metric).
- Standard seeds `[42, 137, 271, 314, 1729]`; report **median + IQR**, not a single run.
- **Failures are data** — a config that won't converge is a logged result, not a thing to tune away.
- Defer fallbacks (EMA-view, margin loss, Adam accumulators) until the baseline is characterized; defer PVT realism until the ideal converges.

**Invariants to log every run:** convergence / loss-slope · dead-unit fraction · ceiling/goodness saturation · inter-block drift (once chained).

**The card = 6 slots:** *question → setup → run → result/figures → read → decision* (written in `phaseN/expK/experiment-K.md`).

**Write-boundary:** status goes in `draft6.0/idea/main.ideas.v1.md`; run detail in `phaseN/expK/`. Don't log a run in the `ideas1.md` derivation chapters — that's a decision, not a checkpoint.

**Budget:** this skill + the target `phaseN/README.md` + the one relevant `expK/` card. Open `pNlib.py` only when modifying it.
