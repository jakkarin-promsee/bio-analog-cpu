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

**Stage 1 is done and frozen (Phases 1–6): the SCFF cheap brain composes depth and survives noise. Stage 2 (the GD
*namer*) is underway — Phase 7 (the readout) and Phase 8 (economy + cost) are DONE; Phase 9 (maintenance + the owed
BP+replay accuracy baseline) is the live line.** One-glance ladder — the depth lives in each `src/phaseN/README.md`, not here:

- **P1 ✓ structure** — the cell works; its home is the **continual** regime (a periodic sleep recovers what online backprop catastrophically forgets). Generalizes better than backprop at ~10% backward cost; *not* a deep static-accuracy competitor.
- **P2 ✓ depth round 1** — a deep SCFF stack can't earn depth (transmission *and* a perfect-oracle objective both fail). Depth comes from **boosted ensembles of shallow blocks with tiny GD readouts**, not deep SCFF.
- **P3 ✓ depth round 2 — ADOPTED** — the wall was the **energy objective `Σh²`**, not locality. **Contrast (InfoNCE) + a cross-layer coordination window** compose depth and re-earn the continual win — this **supersedes energy-goodness**.
- **P4 ✓ characterization** — the capability map vs *genuinely-tuned* backprop: **a substrate-native continual learner, not a static-accuracy competitor.** WINS continual / nuisance-dim / depth-composition / depth-is-cheap (the 80/20 cost win is depth-gated); TRAILS static difficulty / class-count; one honest NEGATIVE on eval-time weight noise.
- **P5 ✓ SCFF close-out — depth SOLVED (scoped)** — the decay was **objective-locality, not an intrinsic Tunnel** (full-credit w12 composes the whole stack). Two *free* levers fix it: **sharper InfoNCE temp 0.2** earns the depth back (direction, not lr — ~82% of the lift; the readout beats tuned-BP, the probe tail reaches the w12 ceiling) and **per-depth heads + a short fixed reader** read the continual home **8× cheaper** than all-tap. **Continual-safe** (A6 intact, BWT −0.026) and **real-data-confirmed** (digits tail +0.152; null-but-safe on CIFAR-flat, which has no composable depth). Committed cell: **`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, NO residual, fixed-reader deploy** (truncate ~L2–3 on the home · all-tap for peak acc · w4 = bounded depth-closer). Adaptive early-exit and the frozen residual were **struck**. *The cheap brain is done.*
- **P6 ✓ noise-robust SCFF — Scoped-YES** (ran 2026-07-01, P6.0→P6.8) — A7 (eval-time noise) is real, **OURS-specific & directional** (0.60 vs a linear readout 0.96, 5/5). The primary fix = **generic noise-augmentation** (corrupt one InfoNCE view with broad iid noise, σ_aug=1.0): it **substantially but partially** hardens the Rasch-dominant tap channel (retention 0.817→0.865, 5/5 paired; near the 0.90 band), *improves* clean acc, and **passes the A6 continual gate** (BWT −0.022→−0.017). The **input-transducer directional residual** → Stage-2 read-side (the "scoped"). Sims **overturned** two design guesses: the fix is **generic, not directional-specific** (iid ≥ randax > dir), and the directional enemy is a **coherent translation** (retention, not per-sample cos, is the direction read). Door B (all-data-is-noise) resolved: the direction forms from a fully-noisy stream. Committed cell: **`NoiseAugContrast` = frozen P5 cell + one iid-noise-augmented view**. Front door: [`src/phase6/README.md`](src/phase6/README.md).
- **P7 ✓ the readout / namer — the 20% is NOT gradient descent** (ran 2026-07-02, P7.0→P7.6) — the committed namer is **RanPAC** (closed-form random-projection + running-Gram ridge prototype) **+ a class-balanced-reservoir guard**: no gradient, it ties the gradient MLP anchor on accuracy×BWT (3-way tie with SLDA), leads on natural digits (#1, 0.949), **passes the A6 gate** (the trained cosine-softmax + max-magnitude FeCAM are struck), most spine-clean of the tied cluster. **The spine bends** (magnitude-wins-spine-bends, Δ=0.128 synthetic → −0.036 digits → ≈0 CIFAR: cosine is spine-clean but sub-competitive where the bulk has structure). Sims **overturned** two guesses: the imbalance guard is **cbrs, not AIR**; the "multimodality cliff" is **anisotropy (a tied covariance), not multimodality**. Decision-record delta **S11** (N3 superseded / S4 collapsed / S9 extended). Cost → P8 (**SLDA** = the ~200× cheaper no-grad fallback). Front door: [`src/phase7/README.md`](src/phase7/README.md).
- **P8 ✓ the economy + the cost meter — the two-brain loop, run LIVE (🔥)** (ran 2026-07-02, P8.0→P8.6) — both brains live for the first time (SCFF learns forward-only; the namer tracks the drift via a gate + sleep, on a new streaming `partial_fit`). The committed economy: **SLDA** deployed (metered **69× cheaper** than RanPAC, AA ties live → resolves S11's cost caveat) · **DDM** awake gate · **class-direction tap-drift** trigger (leads error, spine-clean; the magnitude null false-fires) · **grid-8/full-history** sleep. The metered 80/20 is **real** (GD-share **0.121** ≤ 0.25; the gate *creates* it — off it is 0.778); OURS ≈ **half** the energy of BP+replay (bp_ratio 0.501); and it is **LIVE-SAFE** (worst-point BWT **0.000**, 0/5 regress). The crux: **firing more forgets more** (always-pay −0.137) — the gate is a *safety* mechanism. Delta **S12**. **+ P8.7 (why-analog substrate ablation, added 2026-07-02):** the full 2×2 {OURS,GD}×{analog,digital} — the chip is **15.4× cheaper** than conventional GD-on-digital = **5.4× substrate** (compute-in-memory) **× 2.9× algorithm** (the 80/20); analog advantage is a floor (≥2.7×, →53× with the memory wall), the 80/20 is substrate-independent. Front door: [`src/phase8/README.md`](src/phase8/README.md).
- **Stage 2 continues → P9** — the maintenance loop + owed baselines: the fair same-budget **BP+replay *accuracy*** baseline (the existential test — P8 settled *energy*, not accuracy), natural multi-class **A5**, the read-side noise residual, the readout-aware cadence, and re-tuning the drift-rate-conditional cadence if **N2** slows the drift. Map: [`src/stage2-design.md`](src/stage2-design.md); the arc so far (P7+P8 done): [`src/stage2-report.md`](src/stage2-report.md).

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
    phase6-final-architecture.md  ★ the v1.1.0 model in one file (self-contained; noise-hardened — the current head)
    phase5-final-architecture.md  the v1.0.0 ideal-data snapshot (kept as the pre-noise base)
    stage1-report.md   the five-phase executive arc (the cheap brain, closed out)
    result-format.md   the canonical house style (figures · metrics · the 6-slot template)
    ref-report/        glossary the reports cite (methods · metrics · papers)
    phaseN/            per phase: README.md (front door / synthesis) · design.md (the pre-run design) ·
                       CLAUDE.md (signpost) · phaseN-report.md · RESULTS.md · result-format.md (delta) · expK/ cards · figs
```

---

## Routing — draft-6 questions

| When the user asks… | Look in |
| --- | --- |
| **The whole model in one file (v1.1.0, current head)** | [`src/phase6-final-architecture.md`](src/phase6-final-architecture.md) — the self-contained SCFF+GD architecture summary, **noise-hardened**; understand the model + the 6-phase arc without opening any phase report. *(v1.0.0 ideal-data base, kept: [`src/phase5-final-architecture.md`](src/phase5-final-architecture.md).)* |
| The plan / what we're doing now | [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md) (decisions) + [`idea/ideas1.md`](idea/ideas1.md) (the story) |
| The written results / the Stage-1 & Stage-2 story | [`src/stage1-report.md`](src/stage1-report.md) · [`src/stage2-report.md`](src/stage2-report.md) → `src/phaseN/phaseN-report.md` (figures inline) → [`src/ref-report/`](src/ref-report/README.md) (glossary) |
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
