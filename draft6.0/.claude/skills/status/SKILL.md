---
name: status
description: The live state of draft 6.0 — the phase ladder, what is done vs open, what Phase 5 is. Use for "where are we", "current status", "what is the live plan", "what did phase N find", "what is next", "what is phase 5".
---

# draft 6.0 — current status

**Stage 1 complete (Phases 1–4); Phase 5 = optimization is the live line.** The ladder — verdict + where the detail lives:

- **P1 ✓ structure** — the continual win: one SCFF+GD block generalizes better than backprop at ~10% backward cost, and sleep recovers what online-BP catastrophically forgets; *not* a deep static-accuracy competitor. → `src/phase1/phase1-summarize.md`
- **P2 ✓ depth round 1** — a deep SCFF stack can't earn depth (transmission *and* a perfect-oracle objective both fail); depth = boosted shallow blocks + tiny GD readouts. → `src/phase2/phase2-summarize.md`
- **P3 ✓ depth round 2 — ADOPTED** — the wall was the **energy objective `Σh²`**, not locality; **contrast (InfoNCE) + a cross-layer coordination window** compose depth, superseding energy-goodness. → `src/phase3/phase3-summarize.md`
- **P4 ✓ characterization** — capability map vs *tuned* backprop: a substrate-native **continual** learner. WINS continual / nuisance-dim / depth-composition / depth-cheap; TRAILS static difficulty / class-count; honest NEGATIVE on eval-time noise. → `src/phase4/phase4-summarize.md`
- **P5 → optimization (live)** — sleep-cadence + Ch7 learning-gate tuned to *this* cell's measured drift; + train-with-noise (hardware-aware) and natural-data follow-ups.

**Solid vs open:** the continual win is proven and robust; contrast+coordination is adopted. Open = Phase-5 tuning, noise-*during*-learning (the A7 follow-up), natural-data scale, and all analog/PVT realism (everything so far is ideal floats).

**The live decision record:** `draft6.0/idea/main.ideas.v1.md` (committed N1–N3 + the open knobs). The full Stage-1 arc: `draft6.0/src/stage1-report.md`.

**Off-limits:** the recurrent lifelong "thinking" brain is the north star, *beyond* the numbered phases — deliberately not specced. Hold as direction (`research/north-star/`, `docs/essence/`), not a task.

**Budget:** this skill + at most one `phaseN-summarize.md`. A multi-phase sweep → dispatch the `Explore` subagent.
