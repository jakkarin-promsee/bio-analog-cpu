# Experiment 4 — maintenance: the continual regime (sleep), and does it rot?

> The destination, and the regime the substrate was actually built for. After the static-task arc
> (exp0–Exp3) said "cheap + small-gap, but depth is weak," this asks the question that matters: on a
> **non-stationary stream**, does the model rot (shift/forget), and does **sleep** recover it?
> Spec: [`../README.md`](../README.md) (Exp 4 = ladder 3.x sleep + Ch7 gate); ideas1 Ch7–8.

## Question

1. Is there a **shift/forget problem** — does naive online learning rot on a class-incremental stream?
2. Does **sleep** (periodic full-batch GD over history vs the *current* SCFF map) recover it? (3.1)
3. Does the **prototype LUT** (the hippocampus) replay nearly as well at a fraction of the store? (3.2)
4. Does **SCFF itself forget**, or only the readout? (The thesis hope: unsupervised SCFF is stable.)

## Setup

**Class-incremental** stream: classes arrive in waves `[0,1] → [2,3] → … → [8,9]`; SCFF trains online on
each wave (so its features genuinely shift). All-class held-out evaluated after each task. Conditions:
**GD-online** (plain MLP online — the forgetting baseline), **block no-sleep** (SCFF online + readout
online, 3.0), **block sleep-full** (re-fit readout on the full buffer vs current SCFF taps, 3.1), **block
sleep-LUT** (re-fit on a winner-take-all prototype store, vigilance-gated, 3.2). Plus an all-class linear
probe of SCFF taps over the stream (does SCFF forget?). digits (n=3), MNIST (n=2). Code:
[`run_exp4.py`](run_exp4.py); figure [`exp4_rot_sleep.png`](figs_exp4_digits/exp4_rot_sleep.png).
*(The Ch7 threshold gate is the one remaining sub-cell — not run here; sleep was the priority.)*

## Result / figures (digits, n=3)

| condition | all-class held-out, per task `+0,1 … +8,9` | final |
| --- | --- | --- |
| GD-online | [0.20, 0.20, 0.19, 0.21, 0.18] | **0.18** (catastrophic forgetting) |
| block no-sleep (3.0) | [0.20, 0.13, 0.18, 0.17, 0.18] | **0.18** (readout rots too) |
| **block sleep-full (3.1)** | [0.20, 0.38, 0.58, 0.77, 0.94] | **0.935** (full recovery, ≈ static ceiling) |
| **block sleep-LUT (3.2)** | [0.20, 0.37, 0.56, 0.74, 0.90] | **0.898** (≈ full, at **372 protos vs 1200**) |
| **SCFF all-class probe** | [0.90, 0.90, 0.91, 0.90, 0.90] | **flat — SCFF does NOT forget** |

**MNIST confirmation (n=2):** GD-online **0.192** / no-sleep **0.086** (rot) → sleep-full **0.865** /
sleep-LUT **0.863** (≈ the static block ceiling, Exp 1 = 0.85); SCFF probe flat at **~0.75** (doesn't
forget). The win holds on the hard task. *Caveat:* at vigilance 0.90 the LUT kept 4203/5000 (84%) — high-D
normalized vectors look "novel" to cosine vigilance, so compression needs a per-dataset vigilance sweep (it
still matched full replay; it just didn't compress).

## Read (six-slot)

1. **Claim.** On a non-stationary stream, naive online learning **catastrophically forgets** (→ chance-ish),
   but the SCFF block **+ sleep** recovers to the static ceiling — **because SCFF (unsupervised) does not
   forget**, so only the small readout needs consolidation; and a cheap prototype LUT replays nearly as well
   as full history.
2. **Headline number.** Final all-class held-out: **0.18 (GD-online / no-sleep) → 0.935 (sleep-full) /
   0.898 (sleep-LUT, ⅓ the store)**; SCFF probe flat at **0.90** throughout.
3. **Figures.** exp4_rot_sleep — left: the rot (flat 0.18) vs sleep recovery (→0.9+); right: SCFF probe flat
   (no forgetting).
4. **Mechanism.** SCFF's loss is label-free density-clustering, so a new wave just *adds* clusters without
   overwriting old ones → its representation stays class-separable for all classes (the probe stays 0.90).
   The supervised readout *does* get overwritten by recent classes (forgets), but sleep re-fits it over
   replayed history against the (stable) current SCFF map, restoring all classes. The LUT works because
   deduplicated raw-input prototypes span the data cheaply.
5. **Threats.** GD-online baseline isn't weight-matched (forgetting is size-independent, so fine, but noted).
   5 coarse tasks; finer/streaming shift untested. Sleep here re-fits the readout to convergence each task
   (an upper bound); the *gated*, partial, online sleep cadence (how *little/often*) is unswept. The Ch7
   threshold gate is unbuilt.
6. **Decision.** Below.

## Decision

- **The shift/forget problem is real and severe** (online → 0.18) — and **sleep solves it** (0.935). 3.1
  confirmed.
- **The hippocampus LUT is validated** (3.2): 0.898 ≈ full 0.935 at ~⅓ the store. The prototype store stops
  being a stub and earns its place (S8). Sweep the vigilance / store-size next to find how *little* it needs.
- **The load-bearing finding: SCFF is naturally forgetting-robust** (probe flat at 0.90). This is the
  architecture's real edge — unsupervised stability + a cheap sleep-consolidated readout — and it is exactly
  the property a lifelong/continual learner needs.
- **This reframes the whole Phase-1 verdict positively.** Static-task weakness (Exp 1–3: weak depth, GD wins
  accuracy) is *beside the point* — the architecture's purpose is **continual**, and there it goes from
  catastrophic forgetting to near-ceiling where pure online GD cannot. **This is the bridge to the north
  star** (the recurrent lifelong-learning brain).
- **Remaining Exp-4 piece:** the Ch7 threshold gate (when to pay for GD) + the sleep-cadence/LUT-vigilance
  sweep (how little maintenance suffices). Smaller follow-ups, not blockers.
