# Phase 11 — the limit map: real data + scale (signpost)

You're in **Phase 11** of draft 6.0 — **🟢 DESIGNED, REVIEW-FOLDED, NOT YET RUN (spec finalized 2026-07-05).** The
phase the red team asked for: the P10 instrument taken to **harder data, real-world streams, cross-dataset streams,
and scale** — run honestly, expecting and welcoming losses. The product is the **LIMIT-MAP**: arenas × capability
channels, every cell win / tie / loss / FLOOR with its number. Phase 10 stays closed (S14, measurement-only); this
phase measures the frozen recipe (Arm A, porthole) and builds pre-registered scaled instances (Arm B) — nothing is
tuned, in either arm.

- **The spec (read first, execute from):** [`design.md`](design.md) — the ladder P11.0 (bench) → P11.1
  (decomposition: "is it just SLDA?" — run pre-pitch) → P11.2 (MNIST rung) → P11.3 (real streams: gas headline,
  HAR, Electricity, Covertype, Yearbook-bonus) → P11.4 (cross-dataset MNIST→Fashion→CIFAR-gray, class-IL 30-way)
  → P11.5–P11.8 (scaling reads + gated features arena) → P11.9 (the LIMIT-MAP + close-out). Verdict shapes pinned
  BLIND in §2.4; the 3-agent review ledger folded in §8 (23 findings, all resolved — including two blockers and
  four repo-reality traps an executor MUST read: `cl_metrics` not `gauntlet_metrics`, `p10lib.COMMITTED_LOOP` not
  `p8cfg.*` (+ cadence 8→4 override), the noise-σ P10-equivalence pin, and NEVER `p8cfg.SEEDS9` (contains seed 7,
  the ER tuning seed).
- **The reporting contract:** [`result-format.md`](result-format.md) — the per-arena STREAM view is mandatory
  everywhere (the author's ask: sleep visible batch-by-batch, good and bad), LIMIT-MAP 4-state cell encoding,
  8 guards, the §G checklist.
- **The research canon:** [`../../research/papers/phase11/README.md`](../../research/papers/phase11/README.md)
  (D1–D7 deltas: 5-Datasets cite, the ELEC2 no-change trap, gas limitations paper, Yearbook/MedMNIST, ER anchor
  source, openml IDs, the CLEAR cite fix).
- **Committed core (the phase can close honestly after it):** P11.0 + P11.1 + P11.2-r1 + P11.3-gas + P11.4;
  extensions run in order under a results-blind wall-clock stop rule. Kill criteria in design §2.3.
- **Session handoff (cold-start context for the run sessions):** [`../../../temp/handoff6.md`](../../../temp/handoff6.md).
- **Read-budget:** execute from `design.md` + `result-format.md`; open P10 code only to import; the P10 front door
  ([`../phase10/README.md`](../phase10/README.md)) is the verdict being extended, not re-opened.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 10 — validation](../phase10/README.md)
  (closed, S14) · next after this phase → the analog-realism (SPICE/PVT) layer.
