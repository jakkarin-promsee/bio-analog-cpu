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

## How the phase is built

Two questions, in order. First **what shapes can the atom even make** (rung 0), then **can its own
learning rule actually find them** (rung 1). Everything past that — the real-chip physical limits — is
parked in *Ideas* below until these two are solid.

### The actual plan (what we're doing)

| Rung | The question | Status |
| --- | --- | --- |
| **[Rung 0 — what can it represent?](rung0/README.md)** | the ideal `y = ax + b` Ganglion — which shapes can the carve reach, and where's the wall (xor)? Measured with an *oracle* (a free-weight best-fit, not the chip learning). | ✅ **done — start here** |
| **[Rung 1 — can it learn it?](rung1/README.md)** | swap the oracle for two real learners — the chip's **attribution** rule (our lib) vs textbook **gradient descent** (numpy) — over five shapes, per epoch, with momentum and **noise**. **Finding:** the lean rule learns *monotonic* shapes (plane, rising parabola) but can't carve an *interior fold* (valley/gaussian/xor) — a credit limit robust to lr **and** init; gradient carves; under noise they cross over (gradient precise-fragile, attribution coarse-robust). | ✅ **done** |

### Ideas (not done yet — the real-chip limits to layer on later)

Once rung 1 is solid, we add physical reality one piece at a time — each asked as *how does this bend
the picture from the clean rung?* None of these is committed; it's the backlog.

| Idea | What it adds |
| --- | --- |
| weight ceiling | weights can't grow past a cap (a real capacitor limit) — an earlier draft found it's a *gain* limit, not a shape limit (kept in git history) |
| soft saturation | weights charge *softly* toward a rail, not a hard clip |
| activation variant | swap the L2/L3 activation (an Axis-2 `simulator-code` change) |
| residual bypass | the §7.7 L1→L4 skip connection (Axis-3) |

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
