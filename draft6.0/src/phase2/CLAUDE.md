# Phase 2 — depth round 1: depth is not SCFF's lever (signpost)

You're in **Phase 2** of draft 6.0's Stage 1. **Verdict:** a deep SCFF stack **cannot earn depth**, and every
escape hatch is closed — not transmission (P2.1) and not the objective (P2.2 — *even a perfect label-oracle* doesn't
bend the slope). Depth instead comes from **boosted ensembles of shallow SCFF blocks with tiny GD readouts** (P2.5
— `read`/ensemble works; `write`/re-inject fails) at ~85% of GD accuracy for ~1/6 the backward cost; the recipe
preserves the continual win (P2.6).

- **Authoritative record:** [`phase2-summarize.md`](phase2-summarize.md) + [`RESULTS.md`](RESULTS.md). **Story:** [`phase2-report.md`](phase2-report.md).
- **Run-cards:** `exp0/1/2/5/6` (= P2.0/1/2/5/6). **There is no `exp3/`/`exp4/`** — P2.3/P2.4 were skipped (moot once P2.1+P2.2 closed the deep-SCFF path); the gap is intentional. **Apparatus:** `p2lib.py`. **Figures:** `figs_*/`.
- **Read-budget:** to use this phase from elsewhere, read **`phase2-summarize.md` only**; open cards/code only to modify them.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · results arc → [`../stage1-report.md`](../stage1-report.md).
