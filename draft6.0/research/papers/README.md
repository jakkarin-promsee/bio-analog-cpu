# `papers/` — the papers behind draft 6.0, told as stories

The reading splits by the **problem each cycle solved** — the sets mostly don't cross-apply (a Phase-3 paper has no role in the Phase 1–2 design), so they live apart, one folder per cycle:

| Folder | The cycle | The papers |
| ------ | --------- | ---------- |
| **[`phase1-2/`](phase1-2/README.md)** | the **adopted Phase 1–2 design** — the cheap brain + the boosting chain | SCFF · DeeperForward · Distance-Forward · BoostResNet · BYOL · LLRD |
| **[`phase3/`](phase3/README.md)** | the **depth reframe** (Phase 3) — how a forward-only learner *earns* depth | the objective reframe · the 3 coordination directions · the forward-only zoo (+ master paper list) |
| **[`phase5/`](phase5/README.md)** | the **depth-readout reframe** (Phase 5) — keep useful depth & read it cheaply | the cheap-credit survey · preservation (ReZero/Fixup) · adaptive readout (deep-supervision + early-exit) · cheap global direction |
| **[`phase6/`](phase6/README.md)** | **Phase 6 — noise-robust SCFF** (a *Stage-1 extension*): can the cheap brain survive the analog *and* continual noise it will actually see? Pulled forward because a frozen head can't create the robustness (LP-FT). | noise=Tikhonov/flatness (Bishop · SAM · S-SGD) · LP-FT/backbone-robustness · Rasch analog · the noise research pass |
| **[`phase7/`](phase7/README.md)** | **Stage 2 / Phase 7 — the readout** — the GD *namer* on the frozen bulk (convex; the spine = direction) | reservoir/ELM/OCO · cosine/NCM/SLDA/**RanPAC** · the magnitude-bias fixes (SCR/BiC/WA) |
| **[`phase8/`](phase8/README.md)** | **Stage 2 / Phase 8 — the economy** (when to pay for direction) + the cost meter | DDM/ADWIN/ADWIN-U · Skip-RNN · DNI (the *don't*) |
| **[`phase9/`](phase9/README.md)** | **Stage 2 / Phase 9 — maintenance + slow coordination + the north-star hand-off** | replay/EWC/SI/A-GEM/REMIND · EMA/mean-teacher/Lookahead · PonderNet/TENT |

Each file is a **story, not a spec** — the problem the authors were stuck on, the one idea that unstuck them, and *why it matters for our chip*; each ends with a **"What it means for us"** line.

> Cross-references: the design these feed is [`../../idea/ideas1.md`](../../idea/ideas1.md); the learning-rule survey is [`../survey/summary.detail.md`](../survey/summary.detail.md); the Stage-1 report glossary that cites them is [`../../src/ref-report/`](../../src/ref-report/README.md).
