# `skill/architecture-research.md` — research & architecture: mental-model map

> **Use this when** you're about to propose an architecture change, triage a new idea, make a scope call,
> or explore a future direction. This is the **design/research** side.
>
> Router, not procedure. `CLAUDE.md` is always on; this adds the research layer.
> **New here? Read `skill/project-explore.md` first** — the concept entry point.

## The one thing to internalize first

**§22 is law; the code architecture is ours to refine.** Don't drift the locked spec to match the code.
And **triage every new idea** — catching scope-creep is your job.

## Read these first, in order — only the parts named

1. **`docs/draft/project-history.md`** — the arc draft 1 → 5.1: why each pivot happened, what was rejected
   and why. Read this **before second-guessing a locked decision.**
2. **`draft5.1-1.md §22`** — the protected list: 14 locked decisions, each the survivor of a rejected
   alternative. **Conclusions, not preferences.**
3. **`draft5.1-1.md §19`** (open questions) + **`§18`** (math still to derive) + **`draft5.1-2.md §21`**
   (future tracks).
4. **`draft5.1-2.md §20.17`** — the promotion criteria: how a §21 idea earns its way into the baseline.
5. **`docs/draft/project-personal.md`** — how to collaborate (no hedging; pick a position; when the user
   pushes back, **slow down and re-read before reasserting**).

## The mindset

- **Triage every idea into three bins:** does it belong in **§20** (test it in simulation), in **§21**
  (future track, deferred), or nowhere near the locked **§1–§16**? Don't let a new idea into the locked
  spec without the §20.17 process.
- **Architecture changes are decisions, not experiments** (§20.2 #8) — promoted via §20.17, citing data.
- **Build first, survey literature later** (§1.8). The literature is cross-validation *after* a decision,
  not design input.
- **Intuition first, math check second.** When the user describes a mechanism physically, engage there
  first; the derivation follows.

## Constraints

- Biological names are structural, not decorative — don't suggest renaming "to be rigorous" (rejected).
- **A Scap is a wire, not a neuron** (this pushback was a real save; respect it).
- Don't confuse a *fluid* code-architecture choice with a *locked* §22 decision, or vice versa.

## Where the work is now (2026-05)

- Theory locked at draft 5.1. The simulation phase has started: SLICE-1 built and runs (the author is
  exploring it pre-Phase-2; **no H1 verdict yet**). The lean baseline has no hidden-layer credit *by
  construction*, so the **live research question** is *whether / how to add per-level credit back* (the
  diffusion we deliberately dropped) without reintroducing the §2.4 routing-update coupling — decided by
  Phase 2 data, not argument.
- Recorded deviations from §22 (#3 hierarchical diffusion, #6 loss conservation) are in
  `src/docs/context.md §5` — conscious, data-pending. Confirming or reverting them is exactly a §20.17 call.
- **Open future-track candidate:** `notes/ganglion-role-switching.md` — *Dynamic Role Switching* (alternate
  L2 region-segmentation / L3–L4 gain modes) + the "Ganglion = region multiplexer / axon projection"
  rationale. §3 there is a §21 candidate (with a §20 test hook); §1–2 may enrich §7.2. Triage before promoting.

## Traps

- Importing ML/backprop framing as if it were the goal (it's not — §1.2).
- Treating a fluid code choice as locked, or a locked §22 decision as fluid.
- Proposing a §21 mechanism as a baseline change without the §20.17 data path.

## Done means

- A new idea is triaged into §20 / §21 / rejected — explicitly, with the reason.
- A proposed change to a locked decision cites a phase report, or it doesn't happen.
- You re-read `project-history.md` before reopening anything already settled.
