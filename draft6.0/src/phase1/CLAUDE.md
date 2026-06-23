# Phase 1 — structure & the continual win (signpost)

You're in **Phase 1** of draft 6.0's Stage 1. **Verdict:** a cheap, *forgetting-robust* **continual** learner —
one SCFF+GD block generalizes better than backprop (smaller memorization gap) at ~10% backward cost, and in the
continual regime a periodic **sleep** recovers what online backprop catastrophically forgets. It is **not** a deep
static-accuracy competitor (SCFF clusters by density, not class; shallow-is-better; depth saturates).

- **Authoritative record:** [`phase1-summarize.md`](phase1-summarize.md) + [`RESULTS.md`](RESULTS.md).
- **The story (figures inline):** [`phase1-report.md`](phase1-report.md). **House style:** [`result-format.md`](result-format.md).
- **Run-cards:** `exp0/`…`exp4/` (gate → block-vs-GD → ratio/plasticity → boosting chain → continual+sleep). **Figures:** `figs_*/`.
- **Read-budget:** to use this phase from elsewhere, read **`phase1-summarize.md` only**; open cards/code only to modify them.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · results arc → [`../stage1-report.md`](../stage1-report.md).
