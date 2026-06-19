# Experiment 0 — the sanity probe (full SCFF + full GD, alone)

> **Status: config LOCKED, not run yet.** This is the first thing to run and the gate to everything
> (ladder 1.0 + 1.1). Follow the convention: question → setup → run → result → read → decision. The spec is
> [`../README.md`](../README.md); the *why* is [`../../idea/ideas1.md`](../../idea/ideas1.md).

## Question

1. **Does SCFF separate at all?** Full SCFF alone — does goodness separate (`G_pos`↑, `G_neg`↓), and do the
   layers grow **more separable with depth** (linear-probe accuracy rising layer by layer)?
2. **What's the ceiling?** Full GD alone — the precision ceiling Exp 1–3 quote against.
3. **Two open knobs set here:** two-sided loss vs pure-contrast; and a cheaper **forward-only rival** as a
   bench check.

If (1) fails, stop — nothing downstream is interpretable until SCFF separates.

## Setup (LOCKED — methodology rule #3)

**First point only; Exp 1b sweeps size around it. Pick, lock, run, let the figure talk — don't overthink
the exact values.**

| Knob | Value |
| --- | --- |
| Task | Tier-A **2-arm spiral**, 2-D, label noise σ = 0.10 (moderate), 2 classes |
| Held-out | **fresh draws** (never trained on), 2 000 samples, re-drawn per eval |
| SCFF stack | **4 layers, width 64**, ReLU, mandatory inter-layer norm, mono-forward dual-rail |
| Taps | last **n = 2** SCFF layers (128 features) |
| GD readout | **2 layers** (128 → 32 → 2), Adam-class, cross-entropy |
| Goodness threshold θ | start at **2.0** (open knob) |
| Negative partner | random sample from the current batch (stub) |
| Stream | **50 000** fresh samples, batch size **32**, single online pass |
| Eval cadence | held-out at **log-spaced** checkpoints (≈ 100, 300, 1k, 3k, 10k, 30k, 50k), no update |
| Seeds | `[42, 137, 271, 314, 1729]`, report **median + IQR** |
| Total weight count | **record it** (≈ SCFF 12.4k + readout 4.2k ≈ **16.6k**) → the full-GD control matches this |
| Realism | ideal floats; no analog/PVT, no gate, no sleep |

**Sub-cells (one variable each):**
- **0a** — full SCFF: **two-sided loss vs pure-contrast** (sets that knob).
- **0b** — full SCFF rule vs a cheaper **forward-only rival** (bench check).
- **0c** — full GD alone (the ceiling), total weights matched to 0a.

## Run

_TBD — first run pending._

## Result / figures

_TBD._ Emit: the goodness-separation curve (`G_pos` vs `G_neg` per layer), the **layer × time separability
heatmap** (linear-probe accuracy per layer), the held-out generalization curve + memorization gap, and the
2-D boundary plot (Tier-A is visualizable — actually look at it).

## Read (pass criteria)

- **(1) SCFF separates — the gate:** goodness separates *and* per-layer probe accuracy **rises with depth.**
- **(2) Ceiling:** record full-GD held-out accuracy + its memorization gap as the Exp 1–3 reference.
- **(0a / 0b):** which loss / rule converges cleaner — sets those knobs for everything downstream.

## Decision

_TBD — record: chosen loss (two-sided vs pure-contrast), the θ that worked, the default net size, and the
full-GD ceiling number to carry into Exp 1._
