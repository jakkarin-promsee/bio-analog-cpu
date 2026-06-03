# Phase 1 — Getting to know one Ganglion

> A reader-first walkthrough you can follow top to bottom with no background. If you want to help with
> the project, **start here.**

## What we're doing and why

The whole chip is made of small repeated blocks called **Ganglions** (a Ganglion = a tiny circuit
that takes 2 numbers in and gives 2 numbers out). Before we test the exciting stuff — *can the chip
learn on its own?* — we have to understand the building block itself.

So Phase 1 has one job:

> **Get to know one Ganglion's personality.** What shapes can it make? What's its limit? When does it
> break? We answer with **pictures** — region maps, surfaces, side-by-side fits — not single scores.
> A number like "0.50" means nothing on its own; the *picture* of XOR failing is the real result.

## How the phase is built (a ladder)

We start with the Ganglion in its simplest, most ideal form and add one real-world limit at a time.
Each "rung" of the ladder = one more piece of physical reality, asked as: *how does this bend the
picture from the rung below?*

| Rung | What's added | Status |
| --- | --- | --- |
| **[Rung 0 — ideal](rung0/README.md)** | nothing — the pure `y = ax + b` Ganglion | ✅ **done — start here** |
| **[Rung 1 — weight ceiling](rung1/README.md)** | weights can't grow past a cap (a real capacitor limit) | ✅ done |
| Rung 2 — saturation | weights charge softly toward a rail, not a hard stop | planned |

*(Later we also vary the activation type and the residual bypass — those are separate axes, added
once the weight-limit ladder is understood.)*

## Start here → [Rung 0: What *is* one Ganglion?](rung0/README.md)

Rung 0 is the foundation and it stands alone. In three short steps + pictures it shows:

1. **a Ganglion is a quilt of flat tiles** (each tile a plane `y = ax+b`),
2. **what it can and can't draw** (easy: valleys; the wall: XOR),
3. **the catch** — a random fresh chip can start "asleep," which is what learning has to fix.

## The toolbox (shared by every rung)

You don't need these to read the story, but if you want to run or extend things:

- `harness.py` — builds and drives the **real** Ganglion (not a fake copy). Has the hand-designed
  "canonical" Ganglion and the random ones.
- `metrics.py` — reads structure off a surface (how many tiles/regions, output range).
- `plots.py` — every picture (region maps, slices, surfaces, target-vs-fit).
- `reach.py` — the "best possible fit" search used in Step 2.

Everything runs from the repo root as `python -m src.experiment.phase1_new.rung0.step1_structure`
(and `step2_…`, `step3_…`). See [rung0/README.md](rung0/README.md) for the exact commands.
