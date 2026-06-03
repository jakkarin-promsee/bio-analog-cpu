# Phase 1 · Axis 2 — Op-amp nonlinearity / activation (the full record)

> **Plan / why:** `../../../../draft5.1-2.verify.md` → Phase 1, Axis 2.  **Phase summary:** `../README.md`.

**Status: not started.** (Axis 1 runs first; this axis needs the activation toggle in `alu.py`.)

**The axis.** What the output nonlinearity buys — and which one the silicon actually wants:

- **Placement:** L2-only vs L2+L3. (The current code is L2-only — the free point already characterized in
  Axis-1 exp-1.)
- **Type:** linear → ReLU → hard-tanh (clamp) → tanh. A differential pair's natural transfer **is** tanh
  (BJT: `tanh(V/2V_T)` exactly; MOS: sigmoid-ish), so **tanh is the *free* op-amp curve while ReLU costs a
  rectifier**; hard-tanh = the op-amp with *hard* rails (still piecewise-linear → regions stay countable);
  tanh = *soft* rails (smears the region count). Use ReLU + hard-tanh for clean region counts, tanh for the
  true soft-saturation shape. (Ties to §21.5 + the role-switching note's "L3/L4 want amplification, not a clip.")

## Code prereq
A `simulator-code` task: an activation **type** + **placement** switch in `alu.py` (default = current:
ReLU@L2, linear@L3), threaded through the `harness` config.

## Experiments (planned)

| # | what | question |
| --- | --- | --- |
| experiment-1 | placement: L2-only vs L2+L3 (rung 0) | does the 2nd activation multiply regions past 7? |
| experiment-2 | type: linear / ReLU / hard-tanh / tanh (rung 0) | saturation shape; is tanh (free) richer than ReLU? |

## Findings (this axis)
- _(none yet)_
