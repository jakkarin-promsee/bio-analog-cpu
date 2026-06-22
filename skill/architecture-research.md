# `skill/architecture-research.md` — research & architecture: mental-model map

> **Use this when** you're about to propose an architecture change, triage a new idea, make a scope call,
> or explore a future direction. This is the **design/research** side.
>
> Router, not procedure. `CLAUDE.md` is always on; this adds the research layer.
> **New here? Read `skill/project-explore.md` first** — the concept entry point.
>
> **Migrated to draft 6.0 (June 2026).** The 5.1-era machinery this map used to cite — `§22` (the 14 locked
> decisions), `§20.17` (promotion), the lean baseline — is **history.** The live decision record is now
> [`draft6.0/idea/main.ideas.v1.md`](../draft6.0/idea/main.ideas.v1.md).

## The one thing to internalize first

**The spine is committed; the numbers are open — and 6.0 is *young*.** Draft 6.0 has a committed shape
(`main.ideas.v1.md`: N1–N3 + S1–S8) but **no simulation has run.** So unlike the frozen 5.1 spec, promotion
here is **light-weight**: the spine holds, but the listed *open knobs* are explicitly the sims' to set.
Don't treat a 6.0 decision as immovable the way 5.1's "14 locked decisions" were presented — and don't
re-defend a *dead* 5.1 decision (attribution, hierarchical diffusion) as if it were live.

And still: **triage every new idea — catching scope-creep is your job.**

## Read these first, in order — only the parts named

1. **[`draft6.0/idea/main.ideas.v1.md`](../draft6.0/idea/main.ideas.v1.md)** — the decision record: N1–N3
   (approved), S1–S8 (supporting), **the open knobs**, and the drift fix. This is what's committed vs open.
2. **[`draft6.0/idea/ideas1.md`](../draft6.0/idea/ideas1.md)** — the full derivation (each chapter solves
   the previous one's problem) **and the Phase-1 build plan** (the experiment ladder). A new idea must land
   somewhere on that ladder, or it's a future track.
3. **[`draft6.0/ref/`](../draft6.0/ref/README.md)** — the paper behind each decision (one story per paper).
   Read the relevant one before second-guessing a call it backs.
4. **[`docs/draft/project-personal.md`](../docs/draft/project-personal.md)** — how to collaborate (no
   hedging; pick a position; when the user pushes back, **slow down and re-read before reasserting**).
5. **[`docs/draft/project-history.md`](../docs/draft/project-history.md)** — *only* for *why* an old (5.1)
   decision was made. Context for the dead world, not the live plan.

## The mindset

- **Triage every idea into three bins:** (a) it tests on the **current ladder** (1.0 → 4.x) → it's a
  Phase-1/2/3/4 experiment (structure / depth round 1 / depth round 2 / maintenance — the live ladder); (b) it's the **north-star /
  future track** (the recurrent thinking brain, *beyond* the numbered phases) → it belongs in
  [`draft6.0/future-ref/`](../draft6.0/future-ref/README.md), held as a compass, **not** pulled into the plan
  without the author; (c) neither → name why and let it go.
- **Architecture changes are decisions, not experiments** — backed by a sim *result*, not a hunch. (6.0 is
  young, so this is lighter than 5.1's frozen process — but a *result*, not an argument, still moves the
  spine.)
- **Build first, survey literature later.** The literature is cross-validation *after* a decision, not
  design input. (And the author keeps re-deriving published results from the circuit side first.)
- **Intuition first, math check second.** When the user describes a mechanism physically, engage there
  first; the derivation follows. **Stay paranoid about signs/direction** — the missing sign killed draft 5;
  run the arithmetic of any worked example.

## Constraints

- Biological names are structural, not decorative — don't suggest renaming "to be rigorous" (rejected).
- **A Scap is a wire, not a neuron** (this pushback was a real save; respect it).
- **Don't pull the north star forward.** The recurrent lifelong-learning brain (correctness-as-a-feeling) is
  the real north star — *beyond* the numbered phases (Phase 2/3 = depth, Phase 4 = maintenance) — and
  **deliberately not specced**, "simple intelligence first." Hold it as direction
  ([`docs/essence/the-essence.md`](../docs/essence/the-essence.md)), not a task.
- **When an old (5.1) doc contradicts draft 6.0, 6.0 wins.** The pivot is the most recent truth.

## Where the work is now (2026-06)

- **Pivoted to draft 6.0** (SCFF + GD hybrid). The spine is committed; **no draft-6.0 sim has run.** The
  live line is the **Phase-1 experiment ladder** in `ideas1.md`, starting at **1.0 — full SCFF**.
- **The build discipline (decided 2026-06-19):** walk one neocortex spine (SCFF + GD); the hippocampus LUT
  is a *service* that plugs in (negatives stubbed first, real at 3.2), not a parallel build; test
  convergence, not theory; keep the phase-2 menu closed.
- **The deeper lesson behind the pivot:** the brain isn't homogeneous, and biology can't be simulated 1:1 —
  modern ML *cheats* it by projecting into a computable dimension. So we build **organ by organ**; 6.0 is
  the first two organs.

## Traps

- Importing ML/backprop framing as if it were the goal (it isn't — the 80/20 split exists to *avoid*
  paying for direction everywhere).
- Re-defending a dead 5.1 decision (attribution, `|a·W|` diffusion, the Ganglion-as-the-atom) as live.
- Treating a 6.0 *open knob* as locked, or the *spine* as casually revisable — know which is which
  (`main.ideas.v1.md` lists both).
- Proposing a future-track (phase-2) mechanism as a Phase-1 change without the author's direction.

## Done means

- A new idea is triaged into **current-ladder / future-track / rejected** — explicitly, with the reason.
- A proposed change to the spine cites a sim result (or is flagged as "needs a run first"), not a hunch.
- You read the relevant `ref/` story (and `project-history.md` for old calls) before reopening anything.
