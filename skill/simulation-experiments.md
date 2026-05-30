# `skill/simulation-experiments.md` — running experiments: mental-model map

> **Use this when** you're about to write a test, run a simulation phase (the MVF or a §20 phase), or
> interpret/report a result. This is the **science** side.
>
> Router, not procedure. `CLAUDE.md` is always on; this adds the experiment layer.
> **New here? Read `skill/project-explore.md` first** — the concept entry point.

## The one thing to internalize first

**Failures are data. Do NOT tune until it works** — that's how you lie to yourself (§20.2 #5). Log it,
characterize it across configs, move on. (The XOR collapse was *reported*, never hacked into passing.)

## Read these first, in order — only the parts named

1. **`draft5.1-2.md §20`** — the campaign: the phases, the MVF (§20.1), and especially **§20.2 the
   methodological rules** (one-thing-changed, multi-seed, invariants-everywhere). These govern every run.
2. **`draft5.1-1.md §17`** — the 11 hypotheses. Every experiment tests one. **H1** (does attribution
   converge) is load-bearing; the rest matter only conditional on H1.
3. **`src/docs/context.md §7`** — how to read early results: the two caveats (the supply-rail saturation
   is implemented but first-pass — full analog charge dynamics deferred; the lean baseline ≠ the spec's
   normalized diffusion).
4. **`draft5.1-1.md §2.4`** + **`draft5.1-2.md §20.18`** — known failure modes + negative-result protocols.

## The mindset (governs every run)

- **One thing changed per experiment.** Exactly one variable between two runs. Multi-variable = uninterpretable.
- **Multiple seeds.** Standard set: `[42, 137, 271, 314, 1729]`. Report **median + IQR**, not a single run.
- **Defer fallbacks/PVT until the baseline is characterized.** No Path-0 noise floor, no Adam `v_t`, no
  analog realism in baseline runs.
- **The sim measures correctness, not speed.** No clock; the ALU charge-wait is invisible. "Sim fast" ≠
  "chip fast."

## Invariants to log every run (§20.5)

Loss-conservation ε, dead-weight fraction, ceiling-saturation fraction, T_max clip rate. (In the lean
baseline, conservation is trivial — it becomes meaningful once per-level diffusion is added.)

## Constraints

- **§22** stands. **§20.17 promotion** is the *only* path from a §21 future-track into the baseline, and
  it needs a phase report citing data — not a hunch.
- Don't change the architecture to make a test pass. A test that fails is a result.

## Where the work is now (2026-05)

- **MVF harness (SLICE-1, one Ganglion) is built and runs** — stable with the supply-rail saturation.
  But **no formal phase has run yet**: the current `run_xor` is the author's pre-Phase-2 play on a
  *linearized* task, **not** the discrete-XOR / substantive test, so there is **no H1 verdict**. (The lean
  baseline has no hidden-layer credit *by construction* — the recorded §22 #3/#6 deviation, and the reason
  per-level diffusion is the remediation if Phase 2 stalls.)
- Per §20, **Phase 1** (operator sanity, as pytest) and **Phase 2** (single-Ganglion baseline: H1/H7/H8/H10)
  are the next formal phases.
- **No `reports/` written yet.** The first real phase report comes from Phase 2, not the pre-Phase-2 play
  (config hash + seeds + honest outcome, per §20.19).

## Traps

- Tuning hyperparameters until XOR passes (forbidden — §20.2 #5).
- Single-seed conclusions.
- Changing two things and not knowing which moved the result.
- Reading a stable ideal sim as a working chip (no PVT yet).

## Done means

- The run obeys §20.2 (one variable, multi-seed, invariants logged).
- A failure is *recorded as data* (multi-config characterization), not tuned away.
- If it's a phase, a `reports/` report exists with the config hash, seeds, and the honest result.
