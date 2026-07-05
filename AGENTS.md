# AGENTS.md — Bio-Inspired Analog Neural Compute Architecture

> The cross-tool front door for AI coding agents (the open [`AGENTS.md`](https://agents.md) standard). Humans
> start at [`README.md`](README.md). Claude Code reads [`CLAUDE.md`](CLAUDE.md) — the full operating guide, plus a
> per-draft `CLAUDE.md` in each `draftN/` and a thin one in each `phaseN/`. This file is the shared orientation
> any agent should read first.

## What this project is

A bio-inspired **analog compute substrate** with on-chip learning — the **math model for a chip** (analog is the
constraint-giver, simulation the medium; no circuit drafting or fabrication planned), **not** an ML benchmark
model. In the design picture, weights live as analog charge on capacitors; the multiply-accumulate happens in a
crossbar of them; the chip learns **online, locally, forward-only** (no backward pass ever leaves the chip). The
four committed properties:
**online, sparse, continuous, resident-weight** — what the field calls **compute-in-memory**. Guiding method:
**copy the brain's *function*, cheat the *implementation*.**

**Status:** both brains are built, characterized, and validated (Stage 1 build = P1–6, Stage 2 build = P7–9,
the validation = P10–11; verdict **S14** — a substrate-native continual learner), then taken to **real data +
scale** in **Phase 11** (the limit map, **S15** — 8 real arenas × 5 capability channels, every cell win / tie /
loss / FLOOR: gas a genuine real-drift win, the identity holding and flooring honestly). **Next build: the
hippocampus organ** (grow the LUT stand-in into a learning brain part — the first north-star step); the
analog-constraint (SPICE-grade, simulation-only) realism pass stays queued for when a result needs it. Per-phase
status lives in [`draft6.0/CLAUDE.md`](draft6.0/CLAUDE.md).

## Where things are (the map)

| You want | Go to |
| --- | --- |
| The human overview | [`README.md`](README.md) |
| The **live** work (draft 6.0 — SCFF + GD) | [`draft6.0/`](draft6.0/README.md) → its `CLAUDE.md` (operating) + `context.md` (cold-start) |
| The **results** — the eleven-phase arc | [`draft6.0/src/README.md`](draft6.0/src/README.md) → [`stage1-report.md`](draft6.0/src/stage1-report.md) (P1–6) · [`stage2-report.md`](draft6.0/src/stage2-report.md) (P7–9, the build + freeze) · [`validation-report.md`](draft6.0/src/validation-report.md) (P10–11, the trial — S14 + S15) |
| The whole model in one self-contained file | [`draft6.0/src/phase9-final-architecture.md`](draft6.0/src/phase9-final-architecture.md) |
| Superseded history (draft 5 — attribution era) | [`draft5.0/`](draft5.0/README.md) |
| The idea journey (drafts 1.0 → 5.1) | [`draft-journey/`](draft-journey/README.md) |
| Why the project exists (the soul) | [`docs/essence/the-essence2.md`](docs/essence/the-essence2.md) (the grown spine; seed: [`the-essence.md`](docs/essence/the-essence.md)) |

## For AI agents — how context is organized (read this)

Context is **layered in `CLAUDE.md` files, loaded lazily**: the root is always in scope; each `draftN/CLAUDE.md`
loads when you work in that draft; each `phaseN/CLAUDE.md` is a thin signpost to that phase's record. **Load the
tier your task needs and stop** — to understand a prior phase, read its one `phaseN/README.md` (the front-door synthesis), *not* its code;
for heavy multi-file lookups, use a read-only sub-agent so the pages stay out of the main context. The full
operating guide — collaboration norms, methodology, routing — is in [`CLAUDE.md`](CLAUDE.md). *(Non-Claude tools:
the per-draft context lives in those `CLAUDE.md` files; read the one for the area you're touching.)*

## Build / run

- The work is a **numpy behavioral simulation** (ideal floats; no SPICE, no hardware). Experiments are scripts
  under `draft6.0/src/phaseN/` (`run_*.py` / `plot_*.py`); shared apparatus in `pNlib.py`.
- **Run single-threaded:** `OMP_NUM_THREADS=1 python -u <script>` — there is a known OpenMP hang on this Windows
  box when sklearn/KMeans runs multi-threaded.
- Spec → Word/PDF reports build via `tools/` (`tools/mkdocx.py`).
- There is **no unit-test suite**; "correctness" = the experiment results plus link/consistency checks.

## Conventions that bind any agent (condensed; the full version is in `CLAUDE.md`)

- **Failures are data — never tune until it passes.** Report a result's scope, its confounds, and what it does
  *not* show.
- **One variable per experiment; multiple seeds** (`[42, 137, 271, 314, 1729]`); report **median + IQR**, not a
  single run.
- **Biological names are structural** (Scap, Hippocampus, Cortex = circuit elements, not biology). Do **not**
  "rename to be more rigorous" — already considered and rejected.
- **No flattery, no hedging.** Pick a position and defend it; match the author's depth (deep topic → deep answer).
- **Stay paranoid about signs / direction** — a missing sign (direction, not magnitude) silently collapsed the
  entire draft-5 era. It is this project's recurring failure mode.
