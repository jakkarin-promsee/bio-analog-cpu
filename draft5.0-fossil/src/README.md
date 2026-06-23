# `src/` — the Python simulation

The behavioural simulator for the bio-inspired analog compute substrate. The chip spec it simulates is
locked in `../draft5.1-1.md` / `../draft5.1-2.md`; this directory is *how* we simulate it.

## What's here

```
src/
  library/   the reusable element classes — the frozen kit (build from here)
  example/   reference wirings + the runnable experiment (run_xor.py)
  docs/      the design + handoff docs (read order below)
  README.md  this index
```

> ⚠ This Python *looks* like software but is a **chip** — every clean line hides silicon (a bus, a mux,
> an inter-processor transaction). Read `docs/core_logic.md` before you extend the code, or you'll
> quietly design something unbuildable.

## Docs — read in this order

1. **`docs/context.md`** — **START HERE.** Onboarding: what the project is, the journey, the decisions
   we made and reverted, the traps, and current status. The fastest way to recover the whole mental model.
2. **`docs/concept.md`** — the architecture *intuition*: why the whole chip collapses into three live
   classes (Scap, ALU, ControlUnit) and the broadcast-+-momentum learning rule.
3. **`docs/code_concept.md`** — the *blueprint*: what the code looks like, class by class, with one
   fully-wired example.
4. **`docs/core_logic.md`** — the **Python ↔ hardware** decoder ring: what each clean construct actually
   is in silicon, and what Python smuggles for free (buses, muxes, MAR/MDR transfers, clocks).
5. **`docs/question.md`** — the confusion FAQ: the "wait, that looks too easy / too weird" questions,
   answered.

## Run the experiment

```
python -m src.example.run_xor        # from the project root
```

SLICE-1: one Ganglion — the Minimum Viable Falsification harness (draft5.1 §20.1). Current state: runs and
is stable (with a basic supply-rail saturation). The author is exploring it pre-Phase-2 on linearized data
(range / activation probes) — intentional play, not the formal §20 test, so there is no H1 verdict yet. The
lean baseline has no hidden-layer credit by construction. See `docs/context.md §5/§7` and `docs/question.md §C`.
