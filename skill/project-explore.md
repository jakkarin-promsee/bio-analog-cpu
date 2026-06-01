# `skill/project-explore.md` — the concept entry point: how to read this project before you touch it

> **Read this FIRST** — before the other skill maps, before the spec, before any task. The project is
> large; you cannot hold all of it at once. This map is the **entry point to the concept**: it teaches
> *how to read the project* — what the pieces are, how to think about them, where the real detail lives —
> and it installs the frame that stops you from "correcting" the project into something it is not.
>
> **Router, not spec.** It points into `draft5.1-1.md` / `draft5.1-2.md` (the canonical chip),
> `src/docs/*` (the code mental model), `docs/draft/*` (history + collaboration), and the other
> `skill/*` maps (task-specific). Read what it points to; don't expect the detail here.
>
> The other maps (`simulator-code`, `simulation-experiments`, `architecture-research`, `sureSkill`) are
> **task** routers, and they are trustworthy about the *code*. This one is the **concept** router — the
> part that was thin before.

---

## 1. The one thing to internalize first

**This is a chip, not a model.** A bio-inspired *analog compute substrate* whose bet is that brain-like
computation can be the **cheap path in silicon** — not an emulation layered on von Neumann, not a digital
ML accelerator, not "an AI." Capacitors hold weights as continuous charge; SRAM holds wiring and sign
bits; hardwired op-amps do add / multiply / ReLU directly on charges; learning happens *on-chip* by
measuring how much current each wire carried, not by routing gradients.

Everything else follows from that sentence. **If you read it as machine learning, every instinct you
import will be slightly wrong** (see §2). Read it as *hardware that happens to learn.* The four committed
properties — **online, sparse, continuous, resident-weight** (weights never leave the chip during
operation) — are substrate properties, not training tricks.

---

## 2. What this project is — and the "corrections" that are WRONG here

The fastest way to be useless here is to drag the project back to the mainstream it deliberately left.
These reflexes fire in every ML-trained or software-trained mind. Each is wrong *here*, for a concrete
reason — learn the reason, not just the rule.

| The reflex | Why it's wrong **here** | What's true instead |
| --- | --- | --- |
| "Use gradient descent / it should backprop." | The substrate can't route per-weight gradients — that needs weight-transport = moving data = fighting the resident-weight property. It *can* measure `\|a·W\|` (the forward current) for free. | Learning is **attribution**, not gradient. The weight is *in* its own update; credit is *contribution*, not sensitivity. (§4) |
| "`\|a·W\|` / attribution is *risky* — no convergence guarantee, it won't really learn." | There's no *theorem* ranking it against SGD (true, and the spec says so) — but it's a recognized family (three-factor / LRP / EP) **and it empirically trains** (evidence box below). The risk is *unquantified scale*, not *validity*. | Treat it as a **working candidate to test**, not a mistake to fix. The open question is reach (H1), not whether the idea is sound. (§4) |
| "It just fit a regression — it's a small MLP, nothing new." | A Ganglion is **not a regressor** — it's a **region multiplexer**: L2 segments the input into regions, L3/L4 drive each to saturation. It's the hardware **projection of one axon** (`§7.1`), the *atomic* compute unit. "It fit a plane" undersells *what it is*. | Read a Ganglion as an **axon / region-multiplexer**, not a regression model. The power is *compositional* (atoms compose + switch roles → arbitrary surfaces) — this is the atomic-level "why it works." See `notes/ganglion-role-switching.md`. |
| "Why isn't it converging? Let's tune it until it does." | Convergence is the **open empirical question (H1)**, not a target to engineer toward. Tuning until it passes is how you lie to yourself about what the architecture can do. | A run that fails is **data** — characterize it across configs, report it, move on. (`§20.2 #5`) |
| "Optimize the Python / this is slow / vectorize it / that's not best-practice." | The Python is a **netlist of a chip**; clean lines hide silicon (a bus, a mux, a MAR/MDR inter-processor transfer). "Optimizing" it can quietly design something **unbuildable**. The sim measures *correctness, not speed*. | **Trust the shapes, distrust the ease.** (`src/docs/core_logic.md`) |
| "Rename the bio-names to be rigorous (Ganglion→Region, Brainstem→Controller)." | The names are a **structural semantic system** that lets the author reason by analogy — not decoration. Already considered and rejected. | Names are circuit elements; prefix `biological-` / `analog-` only when disambiguation is needed. (§5) |
| "The goal is to build intelligence / beat a benchmark / match SGD accuracy." | "Intelligence" was dropped as too fuzzy; external-dataset benchmarking is explicitly out of scope. | The goal is a **substrate** where brain-like compute is cheap, judged by the §17 hypotheses — **H1 above all**. (§1.2) |
| "Add a normalizer / Adam / a clamp to fix the runaway / winner-take-all." | The architecture's answer is **Physical Saturation** — the weight cap hits the supply rail and self-limits. Physics, not software. Engineering around it before the physics is validated is forbidden. | `§22 #14` protects this; software normalizers live in §21 and are promoted only on phase data. (§6.6) |
| "It's basically CIM / Mythic / Loihi — an inference array." | Those program weights once and freeze, or are digital/spiking. The whole point is **on-chip learning** in continuous analog. | The distinguishing combination is *continuous + learning + hierarchical + local-measurement*. (§1.5) |
| "Just pass the object across / share one big bus / index any wire directly." | Across a scope wall nothing is free — a value crossing is a bus transaction. One big shared bus = every unit wired to every line = unbuildable. | The **start-pointer boundary + mux** are load-bearing; keep them. (`core_logic.md §6`) |

When something *feels* like it "should" route gradients, normalize shares, or be optimized for speed —
**stop.** That feeling is the ML/software lens. The author's exact words: *"Forget all ml process… the
commonsense shouldn't be used here."*

> **The evidence — so you don't relitigate the premise.** Attribution-based learning (`|a·W|`, broadcast +
> momentum) is **not an untested hunch**: a single Ganglion (2-3-3-2, ideal floats) already trains.
>
> - **Noisy linear plane** `y = 0.05 + 0.15·x₁ + 0.20·x₂ + ε` (ε ∈ ±0.02): total loss falls from **~3.8**
>   to **~0.001** over training (a clean PASS); predictions land inside the noise band — the update
>   direction and magnitude scaling are correct.
> - **Nonlinear paraboloid** `y = 0.1·x₁² + 0.1·x₂² + 0.2·x₁·x₂ + ε` (= `0.1·(x₁+x₂)²`): total loss falls
>   from **~3.0** to **~0.07** (a clear PASS); it captures the trend but underfits the curvature — expected
>   from one Ganglion's capacity + the lean baseline + the current activation choices.
>
> So the live question is **not** "is `|a·W|` valid?" (it demonstrably learns) but "**how far does it scale
> to substantive tasks?**" — that's H1, what Phase 2 tests. Don't spend the author's time arguing the
> premise; engage with the mechanism and help test its *reach*.
>
> **Chosen ≠ only.** Attribution is the *chosen* on-chip rule (the substrate can't route gradients anyway),
> and it's now demonstrated — so don't "correct" it back to gradient as if it were a mistake. But SGD is
> **not** the enemy: it stays the **comparison baseline** at scale, by design (Phase 2's Cell D SGD
> baseline, the attribution-vs-SGD cosine-similarity diagnostic, the "converge within 10× SGD steps" bar).
> Gradient is the *yardstick*, not the *replacement*.

---

## 3. How to read the hierarchy

Five structural levels plus one controller, built bottom-up. Each level **composes** the one below by
adding wiring rules, not new primitives — the storage atom never changes. Read the levels as
*composition patterns*, not as new kinds of thing. (Detail: §4 at a glance, §6–§13 per level.)

- **Scap** — one synapse's weight (sign-magnitude: analog magnitude + a digital sign bit). *Hold:* a Scap
  is a **wire, not a neuron** — its current history already encodes pre × post; and its **momentum is the
  entire per-Scap learning signal.** *Detail:* §6.
- **Ganglion** — the atom of *computation*: a hardwired **2-3-3-2** op-amp net, **29 Scaps**, 36 input→output
  paths (the path-diversity-per-scap optimum). *Hold:* it's a **region multiplexer**, not a small
  regressor — L2 segments the input into regions, L3/L4 amplify each to saturation; the block is the
  hardware **projection of one axon** (fixed at fabrication). That framing — *not* "it fit a line" — is
  *why composing atoms learns anything*. *Detail:* §7 + `notes/ganglion-role-switching.md`. (2-3-3-2 locked
  — `§22 #1`.)
- **Column** — a *sequential* chain of Ganglia joined by learnable **translate ALUs** that reshape
  dimensionality. *Hold:* depth = more ALU stages; translate ALUs learn too. *Detail:* §8.
- **Lobe** — a *multi-branch DAG* of Columns (skip-connections, multiple parents). *Hold:* this is where
  **multi-parent diffusion** and structural (Lobe-level) residuals live. *Detail:* §9.
- **Limbic Loop** — the top: **Cortex + Hippocampus + Commissure** in a two-timescale recurrent loop
  (fast / slow / slower) with a *mandatory* decay term. *Hold:* Cortex and Hippocampus have **identical
  topology** and differ only in **update cadence** (`§22 #9`). *Detail:* §11–§12.
- **Brainstem** — the *only* central controller (≈8–15k transistors): computes loss, broadcasts the pulse
  + direction, manages clocks and per-Lobe gating. *Hold:* **not a CPU** — no instruction set, no
  fetch/decode, doesn't know individual Scaps. *Detail:* §13.

Two disambiguations you must keep straight:

- **Three independent "L1"s — always say which:** Ganglion-internal layers (L1–L4), Column roles
  (Generalist G / Specialists S₁S₂S₃), Route addressing (Route L1 / L2). (§5.2)
- **Cross-cutting mechanisms** (span many levels): residual bypass (§14, the dead-weight defense),
  SpecialGeneralist (§10, gated Ganglion reuse), analog robustness (§15, PVT defenses), routes (§16,
  2D addressing).

---

## 4. How to read the learning mechanism — attribution, not gradient

This is the project's load-bearing commitment. **Read `draft5.1-1.md` §2 then §3 before the modules** —
the modules only make sense in its light.

- **The measurement is free.** The forward current through a Scap *is* `|a·W|`. The same physical wire
  that does the forward computation produces the credit signal as a byproduct. No extra circuit.
- **Loss diffuses top-down.** The Brainstem computes one scalar loss; each level splits it among its
  children in proportion to their stored contribution; it reaches the Scaps as a PWM update pulse.
  Backward is **six clocks regardless of network size** — hierarchy *depth* bounds latency, not weight
  *count*.
- **Attribution vs gradient — the divergence to hold:** SGD asks *"if I wiggle W, how much does loss
  change?"* (`∂L/∂W`, computed by routing error backward through the next layer's weights). This asks
  *"given that this Scap carried this much current, how much of the parent's error is attributable to
  it?"* (a proportion). So **the weight appears in its own update**, and inactive units (`|a·W| = 0`)
  self-prune.
- **The family it belongs to:** three-factor synaptic learning / LRP / Equilibrium Propagation / feedback
  alignment — anchors found *after* the mechanism was designed (cross-validation, not influence; §1.8).
- **What it does NOT do:** implement the chain rule, compute `∂L/∂W`, or inherit SGD's convergence
  guarantees. **Convergence is empirical** — that is exactly what H1 and the §20 campaign exist to test.
- **Evidence it works (unit level):** a single Ganglion under broadcast + momentum fits a noisy linear
  plane near-perfectly (loss ratio ~0.001) and cuts a nonlinear paraboloid ~20× (ratio ~0.05, partial
  curvature). The mechanism and update direction are empirically correct; the open question is *scale*
  (H1), not validity. (See §2's evidence box and §7.)

---

## 5. The two layers you must never confuse

This causes more accidental "fixes" than anything else in the project.

- **The chip spec** (`draft5.1-1.md` / `draft5.1-2.md`) is the **locked** design we are simulating.
  **§22 is law** — 14 conclusions, each the survivor of a rejected alternative (the rejections are in
  `docs/draft/project-history.md`). Don't drift it.
- **The code architecture** (`src/`, described in `src/docs/concept.md` + `code_concept.md`) is **ours and
  fluid** — *how* we simulate the chip in Python. It has churned a lot, and that's normal.
- **When they seem to conflict, the code is wrong, not the spec — *unless* it's a recorded deviation.**
  The big recorded one: the **lean baseline** does **broadcast + momentum**, *not* the spec's normalized
  Current-Mirror per-level diffusion. This is **deliberate** (it cuts the §2.4 routing-update coupling)
  and **recorded** in `src/docs/context.md §5`. Adding the full diffusion back is a **§20.17 promotion**
  driven by phase data — not a refactor.
- **Reading rule:** if the code has no Current Mirror / measurement caps / distribution memory, that is
  **baseline by choice**, not a missing feature. Momentum does the per-Scap work; the broadcast pulse
  carries the magnitude.

---

## 6. How to read the code in one breath

For depth, use `skill/simulator-code.md` and `src/docs/{concept,code_concept,core_logic,question}.md`.
The orientation that makes the code legible:

- **The great collapse → three live classes:** `Scap` (storage), `ALU` (compute — shared and expensive),
  `ControlUnit` (the sequencer). **ColumnGroup, Lobe, and Brainstem are all the same `ControlUnit`** —
  different data, not different classes.
- **Topology is data.** The instruction list is the wiring; capacitors are the nets; a mux gives a cap
  one-slot bus access; start-pointers cross scope walls. **To rewire, edit data, not modules.**
- **Cost inversion.** Forward is the *expensive* sequential machine (the ALU sits and waits for
  capacitors to charge); backward is a *cheap* broadcast pulse. **Learning rides the measurement the
  forward pass already paid for.**
- **Credit = momentum. PWM = a per-scope learning-rate knob, not credit. `forward_sign` is computed by
  the ALU, not the Scap** (the Scap has no access to its input activation).
- **The Python is a netlist.** Trust the shapes, distrust the ease (§2; `core_logic.md`).

---

## 7. Where we are, where we're going — and what to trust

**Where we are.** Theory is **locked at draft 5.1**. We are in the **Python behavioural-simulation**
phase. SLICE-1 — one Ganglion, the §20.1 MVF harness — is **built and runs** end-to-end
(`python -m src.example.run_xor`). The author is currently **exploring pre-Phase-2**: poking the single
Ganglion by hand (linearized data, cap-range and last-layer-activation experiments) ahead of the formal
campaign. That play is *intentional* — not the hypothesis test, and not bugs.

**Where we're going.** The §20 ten-phase campaign. **H1 — *does attribution-based hierarchical diffusion
converge on substantive tasks?* — is the load-bearing question;** H2–H11 only matter if H1 holds. The
current phase is **Phase 1 — Ganglion Personality** (characterize the atom — the old "operator sanity" folds in as rung 0), re-drafted in `draft5.1-2.verify.md`. §22 is locked;
§19 lists what's still open — those are what simulation resolves, not argument.

**Calibrate your trust before you rely on anything:**

- **Solid.** The architecture and the code mental model are well-reasoned, internally consistent, and
  fully transferable. The attribution mechanism **demonstrably trains** a single Ganglion (the regression
  evidence in §2). The *how it is built and why* is done.
- **Unknown.** Whether it works **at scale / on substantive tasks** — H1 is unproven (the unit-level
  evidence above is encouraging but is *not* the H1 test). No multi-seed Phase 2 result yet. The math
  (§18) is asserted, not derived. The higher levels (Limbic Loop, SpecialGeneralist, multi-parent
  diffusion) are unbuilt. All PVT / analog realism is untested (ideal floats only).
- **The `run_xor` situation (so you don't misread it).** `run_xor.py` is the author's **pre-Phase-2
  playground** — the discrete XOR table is beyond a single Ganglion (even linear regression breaks on that
  constraint), so regression targets are swapped in to probe the mechanism (the low prediction values are
  the Python cap's range; the last-layer activation is a noted experiment). It **demonstrably trains**: a
  noisy linear plane → near-perfect (loss **3.77 → 0.001**); a nonlinear paraboloid `0.1(x₁+x₂)²` → **~20×
  loss cut** (ratio ~0.05, partial curvature — one Ganglion's capacity + the lean baseline). So the
  mechanism and update direction are **empirically sound at the unit level** — but this is **not** the
  formal H1 test (substantive tasks, multi-seed, at scale), which is Phase 2. **Net: attribution is a
  demonstrated working candidate; the H1 *scale* verdict is still pending.** (Status docs were reconciled
  on 2026-05-31; older "fails XOR / no code yet / saturation-blind" phrasing predates that — trust the code.)

---

## 8. How to work with the author (the short version)

Full version: `docs/draft/project-personal.md` — read it before any non-trivial collaboration; its rules
are load-bearing.

- **Year-2 undergrad, solo, evenings/weekends, bilingual EN/Thai.** Don't correct grammar — meaning is
  always clear from context. Has shipped real hardware (ChronoForge, an FPGA 2D game engine). **Don't talk
  down**; the EE intuition is usually right even when the term is loose.
- **No flattery, no hedging, no trailing "let me know if…!"** Asked A or B → **pick one and defend it.**
  Wishy-washy "both have merits" is worse than confidently wrong.
- **Intuition first, math/code second.** When a mechanism is described physically, engage at that level
  before reaching for equations.
- **They push back when you're wrong and absorb when you're right.** On pushback, **slow down and re-read
  the architecture before reasserting** ("a Scap is a wire" was a real save).
- **🤣 and "bro" are commit signals, not jokes. The "we" framing is real — match it.** Length matches the
  topic: long for architecture, one line for a naming yes/no.
- **Triage every new idea:** does it belong in **§20** (test in simulation) or **§21** (future track)? It
  does *not* go into the locked §1–§16 without the §20.17 promotion process. Catching scope-creep is part
  of the job.

---

## 9. The reading order, and the map of maps

**To enter the project cold, read in this order:**

1. `CLAUDE.md` (always loaded) — the project at a glance + the binding rules.
2. **This map** (`skill/project-explore.md`) — the concept frame. *(You are here.)*
3. `draft5.1-1.md` **§2 then §3** — the mechanism, then the worked single-Ganglion XOR. *(If you read only
   two spec sections, these.)*
4. `draft5.1-1.md` **§4** — the hierarchy at a glance.
5. Then the **task map** for what you're about to do (below).

**Then route by task:**

| You are about to… | Read |
| --- | --- |
| Edit the simulator (`src/library`, `src/example`) | `skill/simulator-code.md` → `src/docs/{core_logic,code_concept,context}.md` |
| Understand the live plan / what we're doing now | `draft5.1-2.verify.md` (re-drafted phase by phase; `draft5.1-2.md §20` is the rough scaffold) |
| Write a test / run a phase / log a result | `skill/simulation-experiments.md` → `draft5.1-2.verify.md` + `src/experiment/phaseN/` |
| Propose a change / triage an idea / make a scope call | `skill/architecture-research.md` → `project-history.md`, `§22`, `§20.17` |
| Why a Ganglion *works* — the atomic region-multiplexer / axon rationale | `notes/ganglion-role-switching.md` |
| Calibrate what's solid vs still unknown | `skill/sureSkill.md` |
| Understand **why** a decision was made | `docs/draft/project-history.md` |
| Understand **how to talk to the author** | `docs/draft/project-personal.md` |
| Look up a term | `draft5.1-1.md §23` (glossary) |

**This map is the front door; the four task maps are the rooms.** Start here, then go where the work is.

---

_Keep this file alive — it is the first thing the next mind reads. When the concept frame shifts (a level
renamed, the lean baseline promoted toward the spec, H1 finally answered), update this map first, because
every other reading starts from it._
