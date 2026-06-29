# P5.7 — the continual-safety gate: temp0.2 keeps the A6 win → banked

*The architecture's reason for being is the A6 sleep-recovery continual win. Phase 5's one real cell change is the
sharper InfoNCE temperature (0.5 → 0.2, P5.1), which P5.1 flagged as a continual RISK (a sharper contrast is more
class-selective on the current task → plausibly more aggressive overwriting of prior-task structure). This is the
un-skippable gate: does temp0.2 preserve the A6 win? It does.*

**Question.** Does the committed temperature change (0.5 → 0.2) preserve the A6 sleep-recovery continual win (AA / BWT)
vs the P4.5 baseline, on the class-incremental home — and does the committed bulk depth (L12) cost continual
stability?

**Setup.** The `continual_eval` harness promoted into `p5lib` (the validated A6 mechanism — SCFF forward-only through
a class-incremental stream + an all-tap readout sleep-consolidated per task — out of `phase3/exp3/run_p3_3.py`). Four
conditions, one variable = the cell config: **t05_L4** (temp0.5/L4 = the A6 baseline), **t02_L4** (temp0.2/L4 = the
temp-only GATE), **t02_L12** (temp0.2/L12 = temp + committed depth), **t02_L4_nosleep** (the rot control). Tasks:
digits (64-D home anchor) + synth (40-D class-incremental, overlap 0.7), 5 tasks of 2, 3 seeds. GEM/CL metrics. Guards
passed. Pure-numpy (no sklearn compute → phantom-safe).

**Run.** 4 conds × 2 tasks × 3 seeds, checkpointed; wall ≈ 4.4 min.

**Result / figures.** *(median [IQR], n=3)*
| condition | digits AA | digits BWT | synth AA | synth BWT |
| --- | --- | --- | --- | --- |
| **t05_L4** (A6 baseline) | 0.954 [0.947–0.956] | −0.017 [−0.020,−0.015] | 0.583 [0.556–0.585] | −0.176 [−0.191,−0.168] |
| **t02_L4** (GATE) | **0.944** [0.942–0.949] | **−0.026** [−0.027,−0.022] | **0.575** [0.566–0.576] | **−0.162** [−0.172,−0.162] |
| t02_L12 (depth) | 0.929 [0.915–0.935] | −0.020 [−0.042,−0.020] | 0.584 [0.573–0.590] | −0.150 [−0.167,−0.148] |
| t02_L4_nosleep (rot) | 0.191 | −0.998 | 0.199 | −0.902 |

- **CONT-SAFETY-digits / -synth**: AA bars ~0.93–0.95 for all *sleep* conditions; the no-sleep rot bar craters
  (AA 0.19, BWT → −1.0). The all-class **SCFF-probe trajectory is flat** (~0.93 digits) across every condition — the
  **bulk doesn't forget**; only the readout needs sleep.

**Read (6 + 2 slots).**

1. **Claim** — **temp0.2 is continual-safe** — it preserves the A6 win (AA within −0.01, BWT within the −0.02 gate on
   digits; on synth it forgets *less* than the baseline). The P5.1-feared "sharper temp overwrites prior tasks" does
   **not** materialize. **Bank temp0.2.** The committed bulk depth (L12) is continual-*tolerable* but noisier/slightly
   lower-AA than L4 on the home.
2. **Headline** — GATE PASS on both tasks: digits temp0.2 BWT −0.026 vs baseline −0.017 (AA 0.944 vs 0.954); synth
   temp0.2 BWT −0.162 vs −0.176 (AA 0.575 vs 0.583, **less** forgetting). No-sleep rot collapses to AA ~0.19, BWT ~−0.95
   → the A6 sleep-recovery mechanism reproduces decisively on the committed cell. (n=3.)
3. **Figures** — CONT-SAFETY-{digits, synth} (AA/BWT bars + SCFF-probe trajectory). Regen from `arrays.npz`.
4. **Mechanism** — A sharper InfoNCE is more class-selective on the *current* batch, but the **bulk is unsupervised and
   forward-only** — it clusters, it doesn't chase the current label, so a sharper temperature sharpens *clustering*
   without biasing toward the current task's *decision boundary* (the SCFF-probe stays flat at ~0.93 under temp0.2 ⇒ the
   bulk's all-class separability is preserved task-to-task). Forgetting lives in the **readout**, and sleep (full-buffer
   replay refit) recovers it identically for temp0.5 and temp0.2 (no-sleep → −1.0 BWT for both). So the temp knob, which
   bought composing depth (P5.1/P5.2) on the *static* headroom task, costs **nothing** on the continual home — the two
   wins are compatible. Depth (L12) adds a little continual noise on digits (one seed's BWT −0.065; median −0.020) — a
   longer stack has more readout surface to drift — but stays within tolerance; on synth depth is neutral-to-helpful.
5. **Threats** — (a) the synth AA is low in absolute terms (0.58, BWT −0.16 even for the baseline) — synth is a *harder*
   continual task than digits; but the *comparison* (candidate vs baseline) is what the gate tests, and it holds, so the
   absolute difficulty doesn't threaten the verdict. (b) the L12 digits IQR is wide ([−0.042,−0.020]) — seed 42 forgets
   more; n=3 on the heaviest rung is thin, but the GATE condition (L4) is tight across seeds, and the **deployment call
   is shallow anyway** (P5.5). (c) all-tap readout is used here (the A6-validated reader, matched to baseline) — the
   per-depth-heads readout was *struck* for deployment at P5.5, so the gate correctly tests the reader we ship.
6. **Decision** — **PASS — bank temp0.2** as the committed cell temperature (the gate that outranks depth is cleared).
   The committed bulk runs **L12 to earn depth where it pays** (headroom, P5.2) but the **continual home deploys
   shallow** (L4 cleanest here; P5.5's truncation L2–3) — depth is continual-tolerable, not continual-free, so it is not
   paid for on the flat home. No fallback to a milder temp is needed (the P5.1 pre-registered branch does not fire).
7. **Cost-honesty** — the gate adds no deployment cost (it's a one-time validation). It confirms the **sleep loop is
   load-bearing** (no-sleep → catastrophic), which is the Phase-6 (continual-optimization) target — Phase 5 hands
   forward a *trusted* sleep-recovery mechanism on the re-tuned cell, not a broken one.
8. **SCFF-completion** — the spine gate is **cleared**: every adopted Phase-5 change (temp0.2; the fixed-reader readout)
   preserves the A6 win. Remaining: **P5.8** (does the decay + the temp fix hold on natural data — digits already an
   anchor here at AA 0.944; CIFAR-flat owed), **P5.6** (preservation, lean falsification — still LOW-VALUE), **P5.9**
   (the assembled-cell confirmation + verdict). The cell's identity is now settled: **temp0.2 / w2, continual-safe**;
   depth L12 to compose, shallow read to deploy.

**Pre-submit checklist.** [x] Median [IQR], n=3 (heaviest rung). [x] "Real" rule (GATE within-gate both tasks; rot
collapse 3/3). [x] GEM/CL metrics (AA/BWT/forget) vs the P4.5 baseline, budget/protocol-matched. [x] One variable
isolated (temp at L4); depth a separate arm. [x] no-sleep rot control = the A6 mechanism check. [x] SCFF-probe
trajectory = the bulk-forgetting check. [x] Figures via `plot_p5.fig_cont_safety`; regen redraws. [x] manifest+arrays
to schema. [x] Guards logged (FD 2.1e-8). [x] Single-threaded, checkpointed, phantom-safe (no sklearn compute).
[x] Spine: the gate outranks the depth gain; temp0.2 banked because it *passes here*. [x] P5.1 temp×continual tension
resolved (no fallback needed). [x] `RESULTS.md` row added.
