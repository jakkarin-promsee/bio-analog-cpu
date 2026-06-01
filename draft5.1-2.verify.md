# Bio-Inspired Analog Neural Compute Architecture — Part 2 (verify): the live, intuition-driven plan

> **What this file is.** The **re-drafted simulation plan** — built _intuition-first, phase by phase_, each
> phase shaped by the data from the one before. It supersedes `draft5.1-2.md` (the original §20/§21), which
> was a **rough pre-plan** sketched with Opus 4.7 to picture the whole project end-to-end. That file stays
> for reference; this one is the plan we actually run.
>
> **Ground rules — why this file exists:**
>
> - `draft5.1-1.md` is the **locked architecture/intuition** (§22 is law). This plan _serves_ it; it does
>   not touch it.
> - **A full, unedited plan is a myth.** We draft the next phase only once the current one has told us
>   enough. Every later phase is expected to shift. Phases below the current one are _sketches_, not
>   commitments.
> - The discipline of the old §20.2 still holds (one-thing-changed, reproducible seeds, failures-are-data)
>   — but here it is bent toward **characterization** (what does the thing _do_), not only convergence stats.
> - **The work lives in `src/experiment/phaseN/`** — scripts, figures, and per-experiment logs, entered via
>   its `README.md`. This doc is the _plan + status_; that folder is the _record_. Update status here.
>
> **Status (2026-06-01): Phase 1 drafted.** Later phases are added as the data arrives.

---

## Phase 1 — Ganglion Personality (characterize the atom before trusting the molecule)

**The reframe (why this replaces "operator sanity").** We know what a line, a decision tree, an RBF
_look like_. We do **not** yet know what _our_ 2-3-3-2 Ganglion looks like — the family of shapes it can
represent, and where its ceiling is — under the substrate's real constraints. "Do the operators compute
the right number?" (the old Phase 1) is necessary but far too thin. The real Phase-1 question is: **what is
the inductive bias / expressive personality of one Ganglion, and what are its limits?** Characterize the
atom before trusting the molecule.

This is also the **empirical test of the region-multiplexer thesis** (`notes/ganglion-role-switching.md`):
if the plots show piecewise-linear regions (L2's ReLU cuts) plus gain/saturation bends (L3/L4), the
"region multiplexer / axon projection" reading earns its keep — with eyes, not assertion.

**Method — see it.** One Ganglion, a 2-D input swept over a grid; plot each output channel as a surface /
heatmap over that grid. **Personality = the family of shapes reachable by sweeping the weights** (a seeded
random ensemble + a few hand-set extremes), not one weight accident. Change exactly one thing per step,
climbing a realism ladder.

**The realism ladder** (one constraint added per rung — this _is_ §20.2 one-thing-changed, applied to
shape instead of loss):

| Rung | What's on | What we look for |
| --- | --- | --- |
| **0 — Ideal linear** | `y = W·a + b`, plain floats; no ceiling, no saturation; activation per config | the base shape; confirms the op math (this folds in the old operator-sanity) |
| **1 — Activation variant** | compare `2-3(R)-3(R)-2` (ReLU at L2 **and** L3) vs `2-3(R)-3-2` (ReLU at L2 only) | what the 2nd activation buys — more regions? sharper boundaries? (open per §19.2 #6 / §21.5) |
| **2 — Capacitor ceiling** | `w`, `b` clamped to a ceiling — crossed with the 2 activation configs → **4 cases** | the usable input/output range; how clipping distorts the shape |
| **3 — Charge saturation** | the `dV/dt ∝ (V_rail − V_cap)` growth (the e^t-like soft limit) | how saturation bends the surface / soft-limits the gain |

**Summary rung — write the personality down.** Across the ladder: the shape family, the role of the 2nd
activation, the usable range under ceiling, the saturation bend. In one paragraph + a figure set: _what is
a Ganglion?_

**Then ×2 — plain vs residual.** Run the whole ladder twice: **(i)** plain Ganglion; **(ii)** with the §7.7
L1→L4 residual bypass. Residual adds an identity path (`output ≈ input + f(input)`); watch how it shifts the
shape family (toward near-identity at small init, §14.5) and whether it changes the reachable regions. This
is the _shape_ companion to H8 (which is about dead-weight / convergence).

**The gate is understanding, not pass/fail.** Phase 1 is done when we can answer, with figures:

- What family of surfaces can one Ganglion make? Where does it saturate / clip / go flat?
- Does the 2nd activation (L3 ReLU) actually buy expressivity, or not? → decides the open activation question.
- Does the picture confirm the region-multiplexer reading — and **how many linear regions can one 2-3-3-2
  actually carve in 2D?** (The note guesses "up to 3"; three ReLU lines alone can already cut a plane into
  ~7 pieces, and L3's ReLU multiplies that further. Phase 1 measures the _real_ number — that number is the
  atom's headline capacity.)
- How does residual change all of the above?

**Discipline.** One thing changed per rung/config; a fixed seed set for the weight ensembles (so the figures
reproduce); log config + figures; an interesting collapse is _data_ (it marks a limit). Exploratory but
systematic — not the multi-seed convergence statistics of the later phases.

**Code note.** The current `src/` Scap already carries `W_RAIL` (rung 3), so we start _mid-ladder_ — Phase 1
needs simple config toggles to **drop to rung 0** (ideal: no ceiling, no rail) and climb back up, plus the
activation-variant switch. Small additions to the existing kit — a one-time **`simulator-code`** prep task
whose toggles *default to current behavior* (the frozen kit is extended once, not forked per experiment);
no architecture change (toggles are not a §22 matter).

**Output → next phase.** The personality map is the input to the next phase: once we know the atom, we ask
what _molecules_ of it (Ganglion networks) can and can't do.

---

## Later phases — drafted one at a time, as data arrives

Deliberately **not** pre-written (see the ground rules). The immediate next, once Phase 1's pictures exist:

- **Phase 2 (sketch) — Ganglion-network characterization.** Compose Ganglions (a Column / a small DAG) and
  ask the same _"what shape, what limit"_ question one level up, now that the atom's personality is known.
- Everything beyond that is re-derived from data, not committed here. The old `draft5.1-2.md` table
  (MVF → operator-sanity → single-Ganglion → … → 256-scale) stays as an _illustrative_ end-to-end scaffold
  to sanity-check direction against — **not** the running order.

---

_This file grows downward, one phase at a time, as the data comes in._
