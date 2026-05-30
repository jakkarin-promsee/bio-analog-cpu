# `skill/sureSkill.md` — the meta-map: what's covered, what I'm sure of, what I'm not

> This is the index to `skill/` **and** an honest confidence log. It tells the next mind two things a
> normal doc won't: which mental-model maps exist, and — written by the model that built this — **what is
> genuinely solid vs what is still unknown.** Read it to calibrate how much to trust everything else.
>
> Each map in `skill/` is a *router* (it points into `src/docs/*`, `draft5.1-*.md`, `docs/draft/*` for
> the detail), not a procedure. `CLAUDE.md` (always loaded) points here, so the right map is found for the
> task at hand.

## The maps, and their status

| Map (`skill/`) | Use it when… | Status |
| --- | --- | --- |
| `project-explore.md` | **read first** — the concept entry point: how to read the project + the corrections that are wrong here | ✅ done |
| `simulator-code.md` | editing `src/library` / `src/example` | ✅ done |
| `simulation-experiments.md` | writing tests, running §20 phases / the MVF, interpreting results | ✅ done |
| `architecture-research.md` | proposing changes, triaging ideas, scope/scope-creep calls | ✅ done |
| `sureSkill.md` | this meta-map / index | ✅ done |

Maps we may add when the project grows: a **docs-maintenance** map (keeping `context.md` and these maps
fresh), and a **hardware/RTL-handoff** map (for when the design freezes and `core_logic.md` becomes the
netlist spec to hand to an RTL/AMS flow).

---

## What I AM sure of — the full intuition, transferred

High confidence. The mental model is solid and the docs capture it; I could rebuild any of this from
scratch.

- **The code architecture.** Three live classes (Scap, ALU, ControlUnit); the collapse (ColumnGroup /
  Lobe / Brainstem are all the *same* ControlUnit); topology-as-data; the mux + start-pointer boundary;
  the wiring rule (self-registration); the forward(sequential, expensive) / backward(broadcast, cheap)
  asymmetry; the Brainstem-is-just-a-ControlUnit unification.
- **The Python↔hardware mapping** (`core_logic.md`). I know which clean lines hide which silicon — the
  MAR/MDR scope-wall transfer, the mux that looks like array indexing, the decode that looks like a dict
  lookup, the missing clock.
- **The decision history and the reverts** (`context.md §4`). *Why* it's shaped this way, and the dead
  ends we backed out of — external registration, the 3-array instruction format, the Current-Mirror
  per-scap routing. A fresh model will be tempted to re-derive these wrong; the log prevents it.
- **The mechanism trains (unit-level, empirical).** A single Ganglion under broadcast + momentum on
  `|a·W|` converges on noisy linear regression (loss ratio ~0.001) and cuts a nonlinear paraboloid ~20×
  (ratio ~0.05, partial fit). Attribution-based learning is a **demonstrated candidate, not a risky
  guess** — the open question is scale (H1), not validity. It's the *chosen* rule; SGD stays the at-scale
  comparison baseline (Phase 2), not a replacement.
- **The lean-baseline *property* (a structural fact, not a verdict).** The lean baseline (broadcast pulse +
  single global feedback + momentum) has *no hidden-layer credit assignment* by construction — a single
  global feedback sign can't guide hidden ReLU features. That's a consequence of the recorded §22 #3/#6
  deviation, not an experiment. (The regression runs above show the update *direction* is right; what's
  unproven is hidden-layer / substantive-task convergence at scale — i.e. H1, see the gaps below.)
- **Physical Saturation is load-bearing** — empirically: without the rail the model diverged to NaN
  (momentum is both contribution *and* update-scale → positive feedback). The rail (`W_RAIL`, first-pass)
  is now in `scap.py`; §22 #14 was right to protect it.
- **The collaboration model** and the spec's protected list (§22) + our recorded, deliberate deviations.

---

## What I still do NOT know — the honest gaps

Genuinely open. **Don't mistake my confidence about how the thing is *built* for confidence about whether
it *works*.**

- **The central question — does it converge *at scale* (H1)?** Open. The mechanism trains at the unit
  level (above), but **no formal Phase 2** (substantive tasks, multi-seed) has run. The lean baseline
  *structurally* lacks hidden-layer credit, so the open research move is the per-level normalized diffusion
  (the Current Mirror we dropped) — **untested**. Whether momentum-as-credit is strong enough for *deep*
  credit is exactly what Phase 2 must find out.
- **Whether the attribution idea works on a *substantive* task at all.** XOR is the smallest probe. Even
  if the remediation passes XOR, sine / two-moons / sequence tasks are entirely unproven.
- **All analog / PVT behavior** (draft5.1 Phase 8). The sim is ideal floats. Whether the mechanism
  survives realistic noise, drift, charge dynamics, finite precision — untested. The sign-magnitude
  capacitor, the asymptotic saturation, the time-to-threshold measurement — all approximated.
- **The math (§18).** Nothing is formally derived: update-monotonicity, loss conservation, the saturation
  equilibrium, EMA contractivity, Limbic stability. All asserted, none proven.
- **The higher levels.** Limbic Loop two-timescale (H3), SpecialGeneralist (H2), multi-parent diffusion
  (H11), Synaptic Drift (H4) — none built, none tested.
- **The tuning space** (§19.2) — decay factors, timescale ratios k/M, init schemes, saturation rate,
  per-level precision. All provisional; right values unknown until the data says.
- **Scale.** Whether one region (256 Ganglia) is enough for anything useful (§16.5) — unknown.
- **Two local open flags:** the boundary bridge (the CU-mediated copy I implemented vs a true two-port
  bridge cell), and the drive/latch ordering around `execute`. Both implemented one way, neither confirmed.

---

## The honest one-liner

I hold the **full intuition of how the thing is built and why** — that part is done and transferable. The
attribution mechanism **demonstrably trains a single Ganglion** (regression evidence), so attribution is a
working candidate, not a risky bet. What I *don't* have is evidence it works **at scale** — that's the
simulation campaign, still ahead; **no substantive-task H1 result exists yet.** The next real moves: a
formal Phase 2, and — if the lean baseline stalls — the per-level-credit diffusion, to find out whether the
architecture can do the one thing it exists to do.
