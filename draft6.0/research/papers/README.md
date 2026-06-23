# `papers/` — the papers behind draft 6.0, told as stories

The reading splits by the **problem each cycle solved** — and the two sets don't cross-apply (a Phase-3 paper has no role in the Phase 1–2 design, and vice-versa), so they live apart:

| Folder | The cycle | The papers |
| ------ | --------- | ---------- |
| **[`phase1-2/`](phase1-2/README.md)** | the **adopted Phase 1–2 design** — the cheap brain + the boosting chain | SCFF · DeeperForward · Distance-Forward · BoostResNet · BYOL · LLRD |
| **[`phase3/`](phase3/README.md)** | the **depth reframe** (Phase 3) — how a forward-only learner *earns* depth | the objective reframe · the 3 coordination directions · the forward-only zoo (+ master paper list) |

Each file is a **story, not a spec** — the problem the authors were stuck on, the one idea that unstuck them, and *why it matters for our chip*; each ends with a **"What it means for us"** line.

> Cross-references: the design these feed is [`../../idea/ideas1.md`](../../idea/ideas1.md); the learning-rule survey is [`../survey/summary.detail.md`](../survey/summary.detail.md); the Stage-1 report glossary that cites them is [`../../src/ref-report/`](../../src/ref-report/README.md).
