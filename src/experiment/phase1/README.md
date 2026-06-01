# Phase 1 — Ganglion Personality (the record)

> **Intent / plan:** `../../../draft5.1-2.verify.md` → Phase 1. (That doc is the *why*; this folder is the
> *what happened*.)
>
> **Goal in one line:** map the expressive personality of one 2-3-3-2 Ganglion — the family of shapes it
> can make and its limits — by sweeping inputs/weights and plotting the output surface, up a realism ladder.

## Status

**Not started.** Phase 1 has a one-time **code prerequisite** before any experiment: expose the
realism-ladder toggles in the kit — a rung-0 *ideal* switch (disable `W_RAIL` / the ceiling) in `scap.py`,
and the L3-activation switch in `alu.py`. These are **`simulator-code` tasks** (see `skill/simulator-code.md`),
added so they *default to current behavior* — they extend the kit once to enable the ladder; they don't
fork it per experiment (so "`library/` is frozen" still holds). Then the experiments here drive the toggles.

## The experiments (the realism ladder — one thing changed per step)

Each becomes an `experiment-{n}.md` as it is run. Planned order:

1. **Rung 0 — ideal linear shape.** `y = W·a + b`, plain floats, no ceiling/saturation. Plot the output
   surface over a 2-D input grid; sweep a seeded weight ensemble. Confirms the op math + the base shape.
2. **Rung 1 — activation variant.** `2-3(R)-3(R)-2` vs `2-3(R)-3-2`. Does the 2nd activation multiply the
   linear regions? (the headline-capacity question)
3. **Rung 2 — capacitor ceiling.** `w, b` clamped, × the 2 activation configs = 4 cases. Usable range +
   clipping distortion.
4. **Rung 3 — charge saturation.** `dV/dt ∝ (V_rail − V_cap)`. How saturation bends the surface.
5. **Summary — the personality.** Shape family, region count, usable range, saturation bend.

Then **×2**: repeat the whole ladder with the §7.7 residual bypass on.

## Headline findings (fill as we go)

- _(none yet)_

## Read order for an agent picking this up

1. `../../../draft5.1-2.verify.md` → Phase 1 — the intent.
2. This README — status + experiment list + findings.
3. `experiment-{n}.md` in order — the detail.

---

### Skeleton for each `experiment-{n}.md`

```
# Phase 1 · Experiment {n} — {short title}

**Question.**  What are we trying to see?
**Setup.**     Config (rung, activation, residual on/off), seed set, the exact script + command.
**Result.**    The figures (linked) + the numbers.
**Read.**      What the picture says — region count, usable range, saturation, surprises.
**Decision.**  What this changes; what to run next.
```
