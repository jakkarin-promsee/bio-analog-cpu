# Draft 6.0 — `src/` (the results)

> **What this is.** The behavioral-simulation record of draft 6.0 — the eleven-phase arc that built the two-brain
> neocortex, characterized it, validated it honestly, and mapped its limits on real data + scale. This page is the
> **map**: the arc in order, what every document type is for, and where to start. The **story** is told in three
> volumes — [`stage1-report.md`](stage1-report.md) (the cheap brain) → [`stage2-report.md`](stage2-report.md) (the
> namer, frozen) → [`validation-report.md`](validation-report.md) (the frozen object on trial); the **soul** (why any
> of this exists) is
> [`../../docs/essence/the-essence2.md`](../../docs/essence/the-essence2.md); the **design** (what we committed and
> why) is [`../idea/`](../idea/README.md); the **pivot story** (why 5.x died, what 6.0 is) is
> [`../README.md`](../README.md).

---

## The arc, in order (the eleven phases as one chain)

Every phase picks up the wound the last one left. Read them in order and it's one story — a cheap brain built, made
deep, characterized, closed out, hardened, then named — and finally **taken to real data + scale** to have its limits
mapped. **Stage 1** = the ~80% cheap SCFF brain (Phases 1–6); **Stage 2** = the ~20% precise namer, built and frozen
(Phases 7–9); **the validation** = the frozen object on trial (Phase 10, the fair race; Phase 11, the real-data limit
map).

| Phase | The one-line verdict | Front door |
| --- | --- | --- |
| **1 · structure** | The cell works; its home is the **continual** regime, not static accuracy. (density ≠ class surfaces.) | [phase1/](phase1/README.md) |
| **2 · depth r1** | A deep SCFF stack can't earn depth — even a label oracle can't bend it. Depth = boosted shallow blocks. | [phase2/](phase2/README.md) |
| **3 · depth r2** | The wall was the **energy objective**, not locality. **Contrast + coordination** compose depth — *adopted.* | [phase3/](phase3/README.md) |
| **4 · characterization** | A substrate-native **continual** learner, not a static competitor. One wound: the rep **decays** past ~L5. | [phase4/](phase4/README.md) |
| **5 · SCFF close-out** | The decay is **direction** (curable, not a wall). Sharper temp earns depth; a short reader reads it cheap. | [phase5/](phase5/README.md) |
| **6 · noise-hardening** | Eval-noise is real and **directional**; a noise-augmented view hardens it forward-only. *Cheap brain done.* | [phase6/](phase6/README.md) |
| **7 · the readout** | The 20% is **NOT gradient descent** — a closed-form streaming head (RanPAC/SLDA). A *role*, not a method. | [phase7/](phase7/README.md) |
| **8 · the economy** | Both brains **live**; the gate meters the 80/20 real (GD 12%) — and the gate is a **safety** mechanism. | [phase8/](phase8/README.md) |
| **9 · freeze** | The bulk **rotates, doesn't forget**; the lifelong loop tuned on internal signals and **locked** at a hash. | [phase9/](phase9/README.md) |
| **10 · validation** | Raced a fair backprop baseline: **ties** home, **trails** natural digits, **wins** safety + noise. Refined. | [phase10/](phase10/README.md) |
| **11 · the limit map** | Real data + scale: **gas wins**, MNIST/Fashion safety + order-invariance hold, autocorrelated streams **floor** honestly. The red-team answer. | [phase11/](phase11/README.md) |

**The three volumes, deep:** [`stage1-report.md`](stage1-report.md) (Phases 1–6 — the cheap brain, built and
hardened) · [`stage2-report.md`](stage2-report.md) (Phases 7–9 — the namer, the economy, the freeze; every section
ends in a decision) · [`validation-report.md`](validation-report.md) (Phases 10–11 — the frozen object on trial:
nothing decided, everything measured — the fair race + the limit map). **The whole frozen model in one file:**
[`phase9-final-architecture.md`](phase9-final-architecture.md) (v2.0.0 — an outside researcher can understand the
entire chip from that one file).

---

## The document system (what each file is, and when to read it)

The repo is **one story at five depths.** Each document type has one job and one audience — enter at the depth you
need, and every doc links up (to its front door + the soul) and down (to the next depth).

| Type | For whom | Holds | Read it when |
| --- | --- | --- | --- |
| **`phaseN/README.md`** | everyone | the phase **synthesis** — verdict → problem → what we did → what we found → decisions → validated → read-next | you want a phase's gist fast |
| **`phaseN/phaseN-report.md`** | researcher / future-me | the **full narrative** — every figure + table inline, glossary-linked; *understand everything without opening code or a figure* | you're validating a claim |
| **`stage{1,2}-report.md` · `validation-report.md`** | outsider / future-me | the **executive arcs** — self-sufficient volumes (build Stage 1 → build Stage 2 → judge); each phase's full story with figures, so phase reports are for *auditing* | you want the whole story, not one phase |
| **`phaseN-final-architecture.md`** | outside researcher | the **whole model in one self-contained file** at a milestone (v1.0.0 / v1.1.0 / v2.0.0) | you want the chip, not the journey |
| **`phaseN/CLAUDE.md`** | agent (Claude) | a thin **signpost** — verdict + pointers + read-budget + up-links | you're an agent orienting in a phase |
| **`ref-report/`** | everyone | the **glossary** every report cites (methods · metrics · papers) — one definition, cited everywhere | a term is unfamiliar |
| **`phaseN/RESULTS.md`** | agent / future-me | the **scalar ledger** — numbers + decisions per rung | you need the exact number behind a claim |
| **`phaseN/design.md`** | future-me | the **pre-run plan** (a record of intent, not a to-do) | you want to know what we set out to test |
| **`phaseN/expK/experiment-K.md`** | agent | the six-slot **run-card** (the atomic record of one experiment) | you're reproducing or modifying a run |
| **`result-format.md`** | agent / author | the **house style** (figures · metrics · the template) | you're writing up a new result |

---

## Where to start

- **Outsider / researcher / professor** → [`../README.md`](../README.md) (the pivot story — what the chip is, in one
  page) → the three volumes — [`stage1-report.md`](stage1-report.md) → [`stage2-report.md`](stage2-report.md) →
  [`validation-report.md`](validation-report.md) (the results) → any `phaseN/phaseN-report.md` to validate a claim. For the fastest professor-facing read, the one-pager
  [`phase10/professor-brief.md`](phase10/professor-brief.md); for the person and the *why*,
  [`../../docs/essence/the-essence2.md`](../../docs/essence/the-essence2.md) (the soul — a personal milestone, not a
  pitch; read it when you want the human story). **You never need to open a `.py` or a raw figure.**
- **Cold agent (Claude)** → [`../CLAUDE.md`](../CLAUDE.md) (operating context + live status) →
  [`../context.md`](../context.md) (the full dump) → `phaseN/CLAUDE.md` (the signpost) → the phase README / code only
  to modify.
- **The whole chip in one file** → [`phase9-final-architecture.md`](phase9-final-architecture.md).

**Read-budget (the rule that keeps this cheap):** to understand a phase, read its **one `phaseN/README.md`** — never
its cards or code. Open `expK/` cards or `pNlib.py` only to *modify* them. For a heavy multi-phase sweep, dispatch
the `Explore` sub-agent (its own context window) instead of reading many files into one session.
