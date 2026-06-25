# draft 6.0 — operating context (the live line)

> Auto-loads when you work in `draft6.0/`. This is the **draft's mental model + current status + map** — the file
> that changes as work advances (the root `CLAUDE.md` stays stable). Cold-start narrative: [`context.md`](context.md).
> Reading budget: load a phase's `phaseN/README.md` for its gist; open cards/code only to modify them; heavy
> sweeps → dispatch the `Explore` sub-agent.

---

## Architecture in one breath

Two brains on one analog substrate. A cheap, unsupervised **SCFF** front (~80% — Self-Contrastive Forward-Forward:
local, label-free, forward-only) organizes the world for free, and a small precise **gradient-descent** back (~20%)
maps features to real labels — because **direction is the one expensive thing in learning, so we pay for it once,
where it counts.** The two chain as **residual boosting blocks**; learning is **threshold-gated** (cheap local
SCFF most steps, expensive GD only when the cheap path stalls) and **sleep-consolidated** (periodic full-batch GD
over a **hippocampus LUT** prototype memory). It runs via **mono-forward** — one forward sweep carrying a positive
+ negative world side by side through a shared weight crossbar (only the cheap activation buffers double, not the
Scaps). *Why 6.0 exists, in full:* [`README.md`](README.md).

---

## Where we are — current status (the shifting part: edit this, not the root)

**Stage 1 complete (Phases 1–4). Phase 5 = optimization is the live line.** One-glance ladder — the depth lives in
each `src/phaseN/README.md`, not here:

- **P1 ✓ structure** — the cell works; its home is the **continual** regime (a periodic sleep recovers what online backprop catastrophically forgets). Generalizes better than backprop at ~10% backward cost; *not* a deep static-accuracy competitor.
- **P2 ✓ depth round 1** — a deep SCFF stack can't earn depth (transmission *and* a perfect-oracle objective both fail). Depth comes from **boosted ensembles of shallow blocks with tiny GD readouts**, not deep SCFF.
- **P3 ✓ depth round 2 — ADOPTED** — the wall was the **energy objective `Σh²`**, not locality. **Contrast (InfoNCE) + a cross-layer coordination window** compose depth and re-earn the continual win — this **supersedes energy-goodness**.
- **P4 ✓ characterization** — the capability map vs *genuinely-tuned* backprop: **a substrate-native continual learner, not a static-accuracy competitor.** WINS continual / nuisance-dim / depth-composition / depth-is-cheap (the 80/20 cost win is depth-gated); TRAILS static difficulty / class-count; one honest NEGATIVE on eval-time weight noise.
- **P5 → optimization** (live) — the sleep-cadence + Ch7 learning-gate maintenance loop tuned to *this* cell's measured drift, plus train-with-noise (hardware-aware) and natural-data follow-ups.

> Status edit rule: finishing a phase updates **one line above** + adds a `phaseN/CLAUDE.md` signpost. The root never changes for this.

---

## The build discipline (governs every rung)

- **Walk one spine — the neocortex (SCFF + GD).** Build straight down the ladder; don't open a second track.
- **The hippocampus LUT is a service, not a parallel brain.** It feeds SCFF its *negatives* (stub first — a random batch partner) and holds the *replay history* for sleep. Never a milestone of its own.
- **Test convergence, not theory.** Each rung's result is one picture, not an argument. The "so many papers" feeling is the north-star menu ([`research/north-star/`](research/north-star/README.md)) bleeding in — **keep that menu closed.**

---

## The decision record

The live record is [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md) (N1–N3 approved + S1–S8 supporting); the full
derivation (story form) is [`idea/ideas1.md`](idea/ideas1.md). **6.0 is young** — the spine is committed but treat
decisions as *settling*, not frozen the way draft-5.1's "14 locked decisions" were presented; the open knobs are
listed there and the sims set them. What carried forward from the old world *in spirit*: residual connections (now
boosting theory), the two-timescale Cortex/Hippocampus (now sleep + the LUT), resident-weight / sign-as-digital /
the Scap (substrate-level, unchanged).

---

## Scope (what's in, what's out)

- **In:** numpy behavioral simulation of the draft-6.0 hybrid on simple classification / statistics tasks; ideal model first, analog/PVT realism only after the ideal converges.
- **Out (near term):** SPICE, fabrication, external-benchmark-chasing *as the claim* (small tasks are fine as probes).
- **Beyond the numbered phases — the north star (deliberately not specced):** a recurrent, lifelong-learning prefrontal↔hippocampus "thinking" loop where *correctness is a self-generated feeling*. The real long-term target — but **simple intelligence first.** Don't pull it into the live plan or project docs without the author's direction.
- **Triage new ideas:** does it test in the current sim ladder, or is it a later-phase / future track? Catch scope-creep early — but 6.0's spine is still settling, so "promotion" is lighter-weight than 5.1's frozen process.

---

## File map (draft 6.0)

```
draft6.0/
  CLAUDE.md        this file (auto-loads in-draft)
  README.md        the pivot story (why 5.x died, what 6.0 is)
  context.md       ★ full cold-start dump (what / why / how / the person)
  idea/
    main.ideas.v1.md   the decision record (N1–N3 + S1–S8) — the plan
    ideas1.md          the full derivation, story form
  research/        the reading, by role:
    survey/        learning-rule survey (the options considered)
    papers/        paper stories — phase1-2/ (the adopted design) + phase3/ (the depth reframe)
    north-star/    the north-star dossier (21 files + th/ Thai mirror) — beyond the phases, not the live line
  src/             ★ Stage-1 report set + run-specs
    stage1-report.md   the four-phase executive arc
    result-format.md   the canonical house style (figures · metrics · the 6-slot template)
    ref-report/        glossary the reports cite (methods · metrics · papers)
    phaseN/            per phase: README.md (front door / synthesis) · design.md (the pre-run design) ·
                       CLAUDE.md (signpost) · phaseN-report.md · RESULTS.md · result-format.md (delta) · expK/ cards · figs
```

---

## Routing — draft-6 questions

| When the user asks… | Look in |
| --- | --- |
| The plan / what we're doing now | [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md) (decisions) + [`idea/ideas1.md`](idea/ideas1.md) (the story) |
| The written results / Stage-1 story | [`src/stage1-report.md`](src/stage1-report.md) → `src/phaseN/phaseN-report.md` (figures inline) → [`src/ref-report/`](src/ref-report/README.md) (glossary) |
| What did Phase N find? | `src/phaseN/README.md` (front-door synthesis) + `RESULTS.md` (the scalar ledger) |
| Code / read a Phase-N experiment | `src/phaseN/` — start *in* that folder to load only its context; `expK/experiment-K.md` cards; `pNlib.py` apparatus |
| Draw a figure / write up a result | [`src/result-format.md`](src/result-format.md) (canonical house style + base figure catalog; per-phase additions in `src/phaseN/result-format.md`) |
| The papers behind a decision | [`research/papers/`](research/papers/README.md) — `phase1-2/` (design) · `phase3/` (the reframe) |
| The learning-rule survey | [`research/survey/summary.detail.md`](research/survey/summary.detail.md) |
| The north-star / recurrent-brain research | [`research/north-star/`](research/north-star/README.md) — free-time reading, *not* the live plan |

---

## What's historical (draft 5.x)

The draft-5.1 spec, the §20 simulation campaign, the Ganglion-Personality / MVF work, and the `draft5.0/src/`
simulator were built for the **attribution** architecture — superseded (the learning rule distributed loss
*magnitude* but never *direction*). Substrate primitives (Scap, the crossbar) may carry forward; the learning rule
and Ganglion-hierarchy do not. See [`../draft5.0/CLAUDE.md`](../draft5.0/CLAUDE.md) and, for *why* old calls were
made, [`../docs/draft/project-history.md`](../docs/draft/project-history.md).
