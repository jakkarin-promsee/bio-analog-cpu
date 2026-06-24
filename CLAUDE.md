# CLAUDE.md — Bio-Inspired Analog Neural Compute Architecture

> The always-loaded **operating brain** for this repo: **cross-draft and stable** — identity, how to work here, and
> the router into each draft's own context. **Draft-specific status and detail are NOT here** — they live in each
> `draftN/CLAUDE.md`, which auto-loads when you work in that draft. Cross-tool orientation: [`AGENTS.md`](AGENTS.md).

---

## What this project is

A bio-inspired **analog compute substrate** with on-chip learning — a **chip design**, not an ML model and not a
digital ML accelerator. Capacitors hold weights as continuous analog charge; SRAM holds wiring and sign bits;
hardwired op-amps do add / multiply / ReLU directly on charge; the chip **learns on-chip, online, without a
backward pass that leaves the chip.** Committed properties: **online, sparse, continuous, resident-weight**
(compute-in-memory). Method: **copy the brain's *function*, cheat the *implementation*** — pay for each principle
with whatever is cheap here (analog physics where physics is cheaper, modern DL math where math is cheaper). Full
overview: [`AGENTS.md`](AGENTS.md) / [`README.md`](README.md); the *why* and the person: [`docs/essence/the-essence.md`](docs/essence/the-essence.md).

---

## How context is layered here (read your tier, then stop)

This repo's agent context is a **3-layer hierarchy**, loaded lazily — so you load little and go deep only where
the task is:

1. **Root (this file)** — always loaded: identity, the rules below, the router. Stable; rarely changes.
2. **`draftN/CLAUDE.md`** — auto-loads when you work in that draft: its architecture, **current status**, file
   map, and per-draft routing. *(This is the file that changes as work advances — not the root.)*
3. **`phaseN/CLAUDE.md`** — a thin signpost to that phase's authoritative record (`phaseN-summarize.md` + `RESULTS.md`).

**Reading budget — the rule that keeps sessions cheap:** load the layer your task needs and **stop**. To understand
a *prior* phase, read its one `phaseN-summarize.md` — never its code or cards. For heavy multi-file lookups (sweep
several phases, hunt a paper), **dispatch the `Explore` sub-agent** (its own context window; returns only the
conclusion) instead of reading them into this session. *(If a rule seems missing, it may be in a nested `CLAUDE.md`
that hasn't loaded — run `/memory` to see what's in scope.)*

---

## Router — which world, and where

| Working on… | Load |
| --- | --- |
| **The live line (draft 6.0 — SCFF + GD)** | [`draft6.0/CLAUDE.md`](draft6.0/CLAUDE.md) — operating context + current status |
| The whole picture, cold | [`draft6.0/context.md`](draft6.0/context.md) |
| Superseded history (draft 5 — attribution era) | [`draft5.0/CLAUDE.md`](draft5.0/CLAUDE.md) |
| The idea journey (drafts 1.0 → 5.1) | [`draft-journey/`](draft-journey/README.md) |
| Why the project exists / the person | [`docs/essence/the-essence.md`](docs/essence/the-essence.md) · [`docs/draft/project-personal.md`](docs/draft/project-personal.md) |
| Why an old (5.1-era) decision was made | [`docs/draft/project-history.md`](docs/draft/project-history.md) |

---

## Read these once before non-trivial work

- [`docs/essence/the-essence.md`](docs/essence/the-essence.md) — the project's soul: origin, the draft-5 collapse, the return. Short; read it.
- [`docs/draft/project-personal.md`](docs/draft/project-personal.md) — who the author is and how they work (the gut, the incubation, the 10-minute window). Its rules on hedging, scope-creep, and length-matching are load-bearing.

---

## How to collaborate with this author

The full handoff is in [`docs/draft/project-personal.md`](docs/draft/project-personal.md). Shortest summary:

- **Year-2 undergraduate, solo, evening/weekend pace.** Bilingual English/Thai — don't correct grammar; meaning is always clear from context.
- **Pushed real hardware before** (ChronoForge — a pure-FPGA 2D game engine, 640×480@60 Hz in ~18k LUTs). **Don't talk down.** When they describe a circuit in plain words, they usually have the EE concept right.
- **No flattery, no hedging, no trailing "let me know if…!"** Asked to choose A vs B, pick one and defend it. Wishy-washy "both have merits" is worse than confidently wrong.
- **🤣🤣🤣 / 👹 / "bro" / 🔥 are signals, not casualness** — usually "I see what I'm doing and I'm committing." Treat the moment as the commit point.
- **The "we" framing is real.** Match it — collaborator, not tool.
- **Length matches the topic.** 1000+ words for architectural depth; one paragraph for a naming yes/no. Don't pad short topics; don't trim deep ones.
- **Intuition first, math check second.** When they describe a mechanism physically, answer at that level first.
- **They push back when wrong, absorb when right.** If they push back on a critique, slow down and re-read before reasserting (the "scap is a wire, not a neuron" save).
- **Breakthroughs come from incubation, not desk-grinding.** Don't rush to closure; don't summarize prematurely.

---

## Methodological rules (apply to every experiment)

1. **One thing changed per experiment.** Compare exactly one variable between two runs.
2. **Multiple seeds per cell.** Standard set: **`[42, 137, 271, 314, 1729]`**. Report median + IQR, not single runs.
3. **Controlled variables explicit.** Lock task, init, total weight count, training steps, eval metric — unless one is under test.
4. **Invariants checked every run.** Convergence/loss-slope, dead-unit fraction, ceiling/goodness saturation, and (once chained) inter-block drift / SCFF cluster-churn.
5. **Failures are data.** A config that fails to converge is a result — log it, report it, move on. Don't tune until it works; that's how you lie to yourself.
6. **Defer fallbacks until baseline is characterized.** EMA-view, margin loss, Adam-style accumulators — tested as remediation *after* baseline behavior is seen, not bolted on first.
7. **Defer PVT realism until the ideal converges.** Ideal deterministic operators first; process/voltage/thermal later.
8. **Architecture changes are decisions, not experiments** — backed by a result, not a hunch.

---

## Naming discipline

Biological names are **structural, not decorative**. Don't suggest renaming to "be more rigorous" — already considered and rejected.

- Default usage = the circuit element. "Brainstem" / "Hippocampus" mean the circuit, not the biology.
- Prefix **`biological-`** when actual biology is meant; prefix **`analog-`** when explicit circuit framing helps in a mixed paragraph.

---

## Skills & workflow commands

- **Workflow commands** (`.claude/commands/`, self-contained): **`/orient`**, **`/checkpoint`**, **`/commit-progress`**, **`/double-check`** — explicit moves that fire the same steps if you ask in plain words ("commit it", "double-check this"). Add one when a manual ritual repeats 3+ times.
- **Skills (auto-load by task):** universal ones in **`.claude/skills/`** — `project-frame` (what the project is), `explore` (navigate the repo), `folder-structure` (where things go), `writing-report` (document a result). Draft-6-specific ones in **`draft6.0/.claude/skills/`** — `status`, `run-experiment`, `find-paper`, `simulator-code` (load when you work in draft 6). Design + maintenance guide: [`AGENT-OPTIMIZE-GUIDE.md`](AGENT-OPTIMIZE-GUIDE.md).

---

## When in doubt

- **What we're building** → [`draft6.0/CLAUDE.md`](draft6.0/CLAUDE.md) + [`draft6.0/idea/main.ideas.v1.md`](draft6.0/idea/main.ideas.v1.md) (the decision record) — not the draft-5.1 files.
- **How to talk to the author** → [`docs/draft/project-personal.md`](docs/draft/project-personal.md).
- **Why an old thing was decided** → [`docs/draft/project-history.md`](docs/draft/project-history.md) (5.1 era) — but the learning rule was rebuilt; don't re-defend dead decisions.
- **Arithmetic / signs** → run the numbers. The whole draft-5 collapse was a missing **sign** (direction); the §3.3/§3.7 XOR sign bug lived four drafts because nobody computed `+ XOR +`. Direction bugs are this project's recurring silent killer — stay paranoid.
