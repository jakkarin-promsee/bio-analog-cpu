# Phase 1 · Axis 3 — Residual bypass (the full record)

> **Plan / why:** `../../../../draft5.1-2.verify.md` → Phase 1, Axis 3 (the "×2").  **Phase summary:** `../README.md`.

**Status: not started.** (Runs after Axis 1/2 — it re-runs their sweeps with the bypass on.)

**The axis.** The §7.7 Ganglion-level **L1→L4 residual bypass** (`output ≈ input + f(input)`), on vs off.
Re-run the Axis-1 ladder + the key Axis-2 branches with residual on, and watch:

- how the shape family shifts toward **near-identity** at small init (§14.5),
- whether it cuts the **dead / flat fraction** (the shape companion to **H8** — residual reduces dead-weight).

## Code prereq
A `simulator-code` task: the §7.7 L1→L4 bypass toggle in `alu.py` (default off), threaded through the
`harness` config.

## Experiments (planned)

| # | what | question |
| --- | --- | --- |
| experiment-1 | residual on, Axis-1 ladder | how identity-add shifts range / regions / curvature |
| experiment-2 | residual on, Axis-2 branches | does residual change the activation story? |

## Findings (this axis)
- _(none yet)_
