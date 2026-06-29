# Phase 5 — solve depth: compose it, read it cheaply (signpost)

You're in **Phase 5** of draft 6.0's Stage 1 — **✅ COMPLETE (ran 2026-06-30, P5.0→P5.9, all guards PASS).**
**The problem:** the adopted cell composed class structure for ~5 layers, then the representation **drifted off the
class manifold** (a *direction* failure — not dead units, not width) and deep layers *overwrote* the extractor.
**The result:** the decay was **objective-locality, not an intrinsic Tunnel** (full-credit w12 composes the whole
stack), and two *free* levers fix it — (1) **earn the depth** with sharper InfoNCE **temp 0.2** (direction, not lr;
the readout beats tuned-BP, the probe tail reaches the w12 ceiling) and (2) **read it cheaply** with **per-depth heads
+ a short fixed reader** (8× cheaper than all-tap on the continual home). Adaptive early-exit and the frozen residual
were **struck**.

- **The committed cell:** **`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, NO residual, fixed-reader deploy**
  (truncate ~L2–3 on the continual home · all-tap for peak acc · **w4** = bounded depth-closer for compositional
  tasks). Continual-safe (A6 intact, BWT −0.026), real-data-confirmed (digits +0.152; null-but-safe on CIFAR-flat).
- **The spine (held every rung):** preserve / read the class **DIRECTION**, never a **magnitude**. **The hard rule:**
  read/gate/add-to-objective OK; **rewriting the SCFF stream forbidden** (P2.5) — held. **The gate:** no fix may dent
  the A6 continual win (P5.7) — passed.
- **The front door (read this first):** [`README.md`](README.md) — the navigable synthesis (problem → ladder →
  scorecard → committed cell → Phase-6 brief). The deep story with every figure: [`phase5-report.md`](phase5-report.md).
- **The numbers:** [`RESULTS.md`](RESULTS.md) — the scalar ledger, one section per rung (P5.0–P5.9) + the P5.9
  capstone scorecard. The story per rung: [`expK/experiment-K.md`](exp9/experiment-9.md).
- **The spec it was run against:** [`design.md`](design.md) — the ladder, the build plan (`p5lib.py`), the decision
  record. Reporting contract: [`result-format.md`](result-format.md).
- **Phase renumber (now in effect):** Phase 5 = the depth-readout fix (done); the old "P5 = continual optimization"
  → **Phase 6** (GD-side, live). The draft-6 orientation docs are **synced** (`../../CLAUDE.md`, `../../context.md`,
  `../../idea/main.ideas.v1.md` + the **S9** delta, `../stage1-report.md`, the status skill). *(The repo-root
  CLAUDE.md is phase-agnostic — not edited.)*
- **The literature behind it:** [`../../research/papers/phase5/`](../../research/papers/phase5/README.md) — the
  cheap-credit survey + the three tracks (preservation / adaptive-readout / cheap-direction).
- **Still owed (low-priority, with the author):** the `ref-report/` glossary additions (composing-depth,
  expected-compute / forward-MACs, truncation floor, the w12 ceiling) — the new Phase-5 terms the reports define
  inline for now.
- **Read-budget:** for the verdict read **`README.md`**; for the numbers `RESULTS.md`; for the why `design.md`. Open
  cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev phase → [Phase 4](../phase4/README.md).
