# Phase 4 — characterization: the capability map (signpost)

You're in **Phase 4** of draft 6.0's Stage 1. **Verdict:** a gap-to-*genuinely-tuned*-backprop map across seven
controlled axes says it plainly — **a substrate-native continual learner, not a static-accuracy competitor.**
It **WINS** continual (A6, decisive), nuisance-dimension input (A2), depth-composition (A3), and depth-is-cheap
(A4 — the 80/20 cost win is depth-gated); **TRAILS** static difficulty (A1) and class-count (A5); and returns one
honest **NEGATIVE** on eval-time weight noise (A7 — the per-sample-layernorm tradeoff; train-with-noise untested → P5).

- **Authoritative synthesis (the front door):** [`README.md`](README.md) + the [`RESULTS.md`](RESULTS.md) ledger + the one-glance [`figs_summary/CAPABILITY_MAP.png`](figs_summary/CAPABILITY_MAP.png). **Story (authoritative for P4.3):** [`phase4-report.md`](phase4-report.md). **Pre-run design:** [`design.md`](design.md).
- **Run-cards:** `exp0`…`exp6` = A1 difficulty / A2 dim / A3 depth / A4 width×depth / A5 class+anchors / A6 continual / A7 noise. **Apparatus:** `p4lib.py`.
- **Read-budget:** to use this phase from elsewhere, read **`README.md` only**; open cards/code only to modify them.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · results arc → [`../stage1-report.md`](../stage1-report.md).
