# `skill/project-explore.md` — the concept entry point: how to read this project before you touch it

> **Read this FIRST** — before the other skill maps, before the spec, before any task. It teaches *how to
> read the project* — what the pieces are, how to think about them, where the real detail lives — and it
> installs the frame that stops you from "correcting" the project into something it is not.
>
> **Updated for draft 6.0 (June 2026).** The project **pivoted**: the old attribution learning rule
> (`|a·W|` hierarchical diffusion) broke at the root — it carried loss *magnitude* but never *direction*
> (the sign) — and was rebuilt as a **SCFF + gradient-descent hybrid**. This map now points at `draft6.0/`.
> The draft-5.1 attribution world (`draft5.0/draft5.1-*.md`, `draft5.0/src/`, the Ganglion hierarchy) is **history** —
> read it via `docs/draft/project-history.md` for *why* old calls were made, not for what we build now.
>
> **Router, not spec.** It points into `draft6.0/` (the live plan), `docs/essence/the-essence.md` (the
> why), and the other `skill/*` maps. Read what it points to; don't expect the detail here.

---

## 1. The one thing to internalize first

**This is a chip, not a model.** A bio-inspired *analog compute substrate* whose bet is that brain-like
computation can be the **cheap path in silicon** — not an emulation on von Neumann, not a digital ML
accelerator, not "an AI." Capacitors hold weights as continuous charge; SRAM holds wiring and sign bits;
hardwired op-amps do add / multiply / ReLU directly on charges; the chip **learns on-chip, online.**

Everything else follows from that sentence. **If you read it as machine learning, every instinct you
import will be slightly wrong** (§2). Read it as *hardware that happens to learn.* The four committed
properties — **online, sparse, continuous, resident-weight** — are substrate properties, not training
tricks. That bet survived the pivot untouched. What changed is only *how the chip learns* (§4).

The governing method, in the author's words: **copy the brain's *function*, cheat the *implementation*.**
You cannot copy 3D-moving synapses, growing axons, spiking multi-hormone wires. So you reproduce what the
brain *does* with whatever is cheap on this substrate — analog physics, or modern DL math. That is the
method, not a betrayal of the biology.

---

## 2. What this project is — and the "corrections" that are WRONG here

The fastest way to be useless here is to drag the project back to a mainstream it deliberately left — or,
now, to mis-map it onto the one paper it borrows from. Each reflex below is wrong *here*, for a concrete
reason. Learn the reason, not the rule.

| The reflex | Why it's wrong **here** | What's true instead |
| --- | --- | --- |
| "It uses SCFF — so it's just Forward-Forward / just that paper." | SCFF is only the **cheap ~80%** (the unsupervised front). The architecture is a *hybrid* — SCFF + gradient descent + sleep + a memory — on analog silicon. And our SCFF is **reformulated** (summation not concat, mono-forward dual-rail) for the substrate. | It's a **two-brain hybrid**; SCFF is one organ, reshaped for hardware. (§4) |
| "It uses gradient descent — so it's just a normal net / why not backprop everything?" | GD is the **expensive ~20%**, used only where *direction* must be paid for. Backprop-everything is exactly what the substrate can't afford and what the 80/20 split exists to avoid. | **Pay for direction once**, locally; SCFF does the rest for free. (§4) |
| "Make it more biologically faithful / this isn't accurate to neurons." | The method is *copy the function, cheat the implementation*. Faithfulness is **not** the goal; cheap reproduction of what the brain does is. | Cheat with analog law + modern math, **deliberately.** (§1) |
| "The old spec / Ganglion / `\|a·W\|` attribution is the architecture." | That was the **previous** architecture. It broke (missing direction) and was replaced. | The live world is **`draft6.0/`**; draft 5.1 is history. (§5) |
| "Draft 6.0 is locked — don't touch the decisions." | 6.0's **spine is committed but the sims haven't run.** The decision record lists explicit *open knobs.* | Treat 6.0 as **young**; the sims set the numbers. (§6) |
| "Optimize the Python / vectorize it / that's not best-practice." | The simulator is a **netlist of a chip**; clean lines hide silicon. "Optimizing" can quietly design something **unbuildable.** Correctness, not speed. | **Trust the shapes, distrust the ease.** |
| "Why isn't it converging? Tune it until it does." | A run that fails is **data** — characterize it across configs, report it, move on. Tuning-to-a-pass is how you lie to yourself. | Failures are data. (methodological rule #5) |
| "Rename the bio-names to be rigorous." | The names are a **structural semantic system** for reasoning by analogy — not decoration. Considered and rejected. | Names are circuit elements; prefix `biological-`/`analog-` only to disambiguate. |

When something *feels* like it "should" backprop everything, be purely-biological, or be optimized for
speed — **stop.** That feeling is the wrong lens. The author's words: *"Forget all ml process… the
commonsense shouldn't be used here"* — and *"we have to cheat."*

---

## 3. The architecture (draft 6.0) — how to read it

Detail in `draft6.0/idea/ideas1.md` (the full story) and `draft6.0/idea/main.ideas.v1.md` (the decision
record). The shape:

- **Two brains.** A cheap, unsupervised **SCFF** front (~80%) organizes the world for free; a small,
  precise **gradient-descent** back (~20%) maps features to real labels. *Direction is the one expensive
  thing in learning, so pay for it once.*
- **Residual boosting blocks.** The two brains chain as blocks — each block a *weak corrector* on a
  residual stream (boosting; `research/papers/phase1-2/boostresnet.md`), SCFF doing feature work inside, a GD checkpoint at the
  exit. This is what makes blocks "discrete."
- **The middle layer = stability + coordination.** A *plasticity-gradient slowdown* (slow the late SCFF
  layers GD reads — mirrored LLRD) keeps the interface still; *overlapping blocks* (DF-O) coordinate.
  EMA-view (BYOL) is the de-risked upgrade.
- **Threshold-gated learning.** Loss low → cheap SCFF only. Loss high → SCFF + GD. Pay for direction only
  when the cheap path stalls.
- **Sleep + memory.** Periodic full-batch GD over a **hippocampus LUT** (deduplicated raw-input
  prototypes) re-covers the whole data range so nothing rots.
- **The substrate (unchanged).** **Mono-forward**: one forward sweep carries a positive + negative world
  side by side through a **shared** weight crossbar; only the cheap **LocalCapacitor** activation buffers
  double, not the Scaps. Resident-weight, continuous, online, sparse.

> The old **Scap → Ganglion → Column → Lobe → Limbic Loop** hierarchy belonged to the attribution
> architecture and is **historical.** The *Scap* (capacitor weight storage) survives as the substrate
> atom; the Hippocampus/Cortex *ideas* survive as the sleep/consolidation + LUT memory. Everything else in
> that hierarchy is read-for-history-only (`draft5.0/draft5.1-1.md`).

---

## 4. The learning mechanism (draft 6.0) — SCFF + gradient descent

Read `draft6.0/README.md` then `draft6.0/idea/ideas1.md`; the paper stories are in `draft6.0/research/papers/`.

- **SCFF (the cheap brain).** Label-free, forward-only, local. Build a **positive** = a sample paired with
  itself, a **negative** = a sample paired with a different sample; train each layer so its *goodness*
  (`‖h‖²`) is high on positives, low on negatives. No backward pass, no labels. It is the only rule that is
  local + derivative-free + forward-only + unsupervised at once. *Where SCFF's accuracy gap opens (hard
  tasks) is exactly where the GD brain takes over.* (`research/papers/phase1-2/scff.md`)
- **GD (the precise brain).** A small modern optimizer (Adam-class online, full-batch at sleep) maps SCFF
  features to real labels via the residual boosting checkpoints. It is **licensed to be fully modern** —
  the bio-cleverness lives in SCFF; GD is the part we let be unapologetically precise. (`research/papers/phase1-2/boostresnet.md`)
- **Grounding (the deep why).** A self-generated learning signal must stay tethered to reality (prediction
  error + occasional real labels) or it collapses to "everything is correct." This is the seed of the
  north-star (correctness as a *feeling*, *beyond* the numbered phases), but **that is not specced** — see `docs/essence`.

What it does **NOT** do: it does not claim to be backprop, and it does not freeze at deploy (the whole
point is online, lifelong learning). **Convergence is empirical** — and Stage 1 (Phases 1–4) has now run
and confirmed it (§6).

---

## 5. The two worlds you must never confuse

This causes more accidental "fixes" than anything else.

- **The live plan** (`draft6.0/`) is what we build now. `main.ideas.v1.md` is the decision record; its
  spine is committed and Stage 1 (Phases 1–4) set most of its numbers — the open knobs that remain are Phase 5's.
- **The historical world** (`draft5.0/draft5.1-*.md`, `draft5.0/draft5.1-2.verify.md`, `draft5.0/src/`) is the **attribution chip** —
  the design that broke. The `draft5.0/src/` simulator implemented *that* chip (the Ganglion, broadcast + momentum,
  the lean baseline). Its substrate primitives may carry forward; its learning rule does not. **Don't
  "fix" draft 6.0 to match the old `draft5.0/src/`, and don't treat old §-references as live.**
- **When something in the old docs contradicts draft 6.0, draft 6.0 wins.** The pivot is the most recent
  truth.

---

## 6. Where we are, what to trust

**Where we are.** Pivoted to **draft 6.0**, and **the numbered phases 1–4 have all run and closed
(2026-06-20 → 22)**: Phase 1 (structure — the continual win), Phase 2 (depth round 1 — energy-goodness can't),
Phase 3 (depth round 2 — contrast + coordination ADOPTED), Phase 4 (characterization — the capability map: a
substrate-native *continual* learner, not a static-accuracy competitor; `draft6.0/src/phase4/phase4-summarize.md`).
The whole arc is now written up reader-facing in `draft6.0/src/stage1-report.md` + each `phaseN/phaseN-report.md`,
with `draft6.0/src/ref-report/` as the glossary.

**Where we're going.** **Phase 5 — optimization:** tune the maintenance loop (sleep cadence + Ch7 gate) against
*this* cell's measured drift, plus the train-with-noise (hardware-aware) and natural-data multi-class follow-ups
Phase 4 flagged. *(The original Phase-1 ladder in `ideas1.md` — 1.0 full SCFF → 1.1 full GD → 2.x mix → 3.x sleep
→ 4.x block chain — is the history of how we got here.)* Simple classification / statistics tasks first. **The build discipline (decided 2026-06-19):** walk one neocortex
spine (SCFF + GD); the hippocampus LUT is a *service* that plugs in (negatives stubbed first, real at 3.2),
not a parallel brain; test convergence, not theory; keep the phase-2 menu closed. The deeper lesson behind
the pivot: the brain isn't homogeneous and can't be simulated 1:1 — ML *cheats* it by projection — so build
**organ by organ**; 6.0 is the first two.

**Calibrate your trust:**

- **Solid.** The *design reasoning* is internally consistent and grounded in real published work (each
  decision has a paper story in `research/papers/`). The *why* (the substrate, the 80/20, the grounding) is coherent.
- **Now proven (Stage 1, Phases 1–4).** The hybrid converges; the **continual win** (sleep recovers what
  online-BP catastrophically forgets) is real and robust; **contrast + coordination** earns depth where
  energy-goodness can't (adopted). The numbers that were the *plan's* knobs are now largely **set** by the sims.
- **Still open.** The **Ch7 threshold gate** and a tuned **sleep cadence** are unbuilt (Phase 5); noise
  robustness *during* learning (hardware-aware), natural-data multi-class scale, and all analog/PVT realism
  remain untested.
- **Off-limits to over-eager building.** **The recurrent lifelong-learning brain** — *beyond* the numbered phases (Phase 2/3 = depth, Phase 4 = characterization/done, Phase 5 = optimization) — is the real
  north star, but it is **deliberately not specced** ("simple intelligence first"). Hold it as direction
  (`docs/essence`), not as a task. Don't pull it into the plan without the author.

---

## 7. How to work with the author (the short version)

Full version: `docs/draft/project-personal.md` — read it before any non-trivial collaboration; load-bearing.

- **Year-2 undergrad, solo, evenings/weekends, bilingual EN/Thai.** Don't correct grammar — meaning is
  always clear. Has shipped real hardware (ChronoForge, an FPGA 2D game engine). **Don't talk down**; the
  EE intuition is usually right even when the term is loose.
- **No flattery, no hedging, no trailing "let me know if…!"** Asked A or B → **pick one and defend it.**
- **Intuition first, math/code second.** Engage the physical picture before reaching for equations.
- **They push back when you're wrong and absorb when you're right.** On pushback, **slow down and re-read
  before reasserting** ("a Scap is a wire" was a real save).
- **🤣 / 👹 and "bro" are commit signals, not jokes. The "we" framing is real — match it.** Length matches
  the topic.
- **Breakthroughs come from incubation** (the leaf, the stubbed toe, the 4-day draft-5 collapse → the
  gut). Don't rush to closure; don't summarize prematurely. The 10-minute window is theirs.

---

## 8. The reading order, and the map of maps

**To enter the project cold, read in this order:**

1. `CLAUDE.md` (always loaded) — the project at a glance + the binding rules.
2. **This map** (`skill/project-explore.md`) — the concept frame. *(You are here.)*
3. `draft6.0/context.md` — **the whole picture in one file** (what / why / how / the person). The fastest cold-start.
4. `draft6.0/README.md` — the pivot story (why 5.x died, what 6.0 is).
5. `draft6.0/idea/main.ideas.v1.md` — the decision record (then `ideas1.md` for the full story).
6. `docs/essence/the-essence.md` — the why and the person.
7. Then the **task map** for what you're about to do (below).

**Then route by task:**

| You are about to… | Read |
| --- | --- |
| Understand the live plan / what we're building | `draft6.0/idea/main.ideas.v1.md` + `ideas1.md` |
| Understand a 6.0 decision's evidence | `draft6.0/research/papers/` (one story per paper) |
| Browse the learning-rule zoo | `draft6.0/research/survey/summary.detail.md` |
| Research the north-star / recurrent brain (beyond the numbered phases) | `draft6.0/research/north-star/` (21-file dossier — free-time reading, *not* the live plan) |
| Code / plan a Phase-2 experiment (depth round 1, done) | `draft6.0/src/phase2/` (README plan + result-format) |
| Code / plan a Phase-3 experiment (depth round 2, the objective reframe) | `draft6.0/src/phase3/` (README plan + result-format) + `draft6.0/research/papers/` (survey) |
| Understand the old attribution chip (history) | `draft5.0/draft5.1-1.md` + `docs/draft/project-history.md` |
| Read the (historical) simulator code | `skill/simulator-code.md` → `draft5.0/src/docs/*` (attribution-era) |
| Propose a change / make a scope call | `skill/architecture-research.md` |
| Fire a recurring move (orient / checkpoint / commit / double-check) | `skill/workflows.md` (+ `/command` triggers) |
| Understand **why** an old decision was made | `docs/draft/project-history.md` |
| Understand **how to talk to the author** | `docs/draft/project-personal.md` |

**This map is the front door; the task maps are the rooms.** Start here, then go where the work is.

---

_Keep this file alive — it is the first thing the next mind reads. When the concept frame shifts again
(a rung simulated, the spine revised, Phase 2 finally specced), update this map first, because every other
reading starts from it. Reframed for draft 6.0 on 2026-06-13; Phase-1 build discipline + the heterogeneous-
organ lesson added 2026-06-19; the draft-5.1 attribution version is in git history._
