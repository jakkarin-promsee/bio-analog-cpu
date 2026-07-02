# P9.4 — Read-side noise residual: does the Phase-6 input-transducer channel need a read-side defense, and can the sleep mechanism supply it?

**Inheriting** the committed loop from P8, the rotation-only drift from P9.0, N2-struck from P9.1, all-tap sleep from
P9.2, and CBRS from P9.3, P9.4 closes the last conditional knob: the **read-side noise residual** the Phase-6 brief
handed to Stage 2. Phase 6 hardened the tap channel with noise-augmentation but scoped out one channel it could not
reach forward-only — the **input-transducer directional** offset (a coherent per-device translation along the input
class axis, which SCFF's per-sample norm cannot remove). This rung asks, first, whether that residual actually dents the
*committed SLDA loop* (the earn-its-place gate), and if so, whether a read-side defense recovers it.

**Question.** Does the Phase-6 input-transducer directional residual dent the committed SLDA namer's retention by
> δ_acc on the continual home (the gate)? If it fires, does a read-side defense — **prototype re-anchoring** from the
raw LUT (primary) — recover the retention, or is the residual real and **named** → analog layer?

**Setup.** Conditional rung. Gate probe = the Phase-6 `NoiseModel` **input-transducer directional** channel (RMS 1.5,
`variant="dir"` along the input class axis) — **not** P8's `nuisance_transform` (layernorm-invariant → SCFF removes it
→ a vacuous probe, the C3 trap). Swept variable (if the gate fires) = read-side defense ∈ {off · **proto-reanchor**
(primary — re-forward the raw LUT through the *current* bulk under the *same* device offset → drift-free,
shift-consistent prototypes, 2403.12952) · SLDA covariance re-estimation (shrinkage-guarded fallback)}. The residual is
**one fixed device offset** (`per_sample=False`) — the same physical mismatch for the eval read and the LUT re-forward,
so both draw the **same** rng offset (a direction-consistency requirement; the wrong draw would compensate for the wrong
shift — the project's recurring direction-bug). Committed SLDA namer on clean all-tap reps is the deployed head; controls
locked (committed cell, seeds [42,137,271,314,1729]). Calibration signal is **direction-grounded** (never
entropy/confidence — the spine). Tunes on the **home** residual only (P10 uses a held-out battery). RESIDUAL + INV.
**Internal-signals-only affirmed.**

**Run.** 5 seeds; gate probe then the primary defense. All nine guards green (bit-exact). Wall 150.5s.

**Result / figures.**

*Gate probe (does the residual earn a defense?):*
| seed | clean acc | undefended acc | dent | proto-reanchor acc | retention |
| --- | --- | --- | --- | --- | --- |
| 42 | 0.559 | 0.465 | +0.093 | 0.546 | 0.977 |
| 137 | 0.523 | 0.457 | +0.066 | 0.521 | 0.996 |
| 271 | 0.553 | 0.408 | +0.145 | 0.549 | 0.993 |
| 314 | 0.539 | 0.425 | +0.115 | 0.532 | 0.986 |
| 1729 | 0.547 | 0.276 | +0.271 | 0.535 | 0.978 |

| defense | residual-retention | residual-dent (gate) | vs-no-residual | verdict |
| --- | --- | --- | --- | --- |
| off (undefended) | 0.787 [0.738–0.833] | 0.115 [0.093–0.145] | (ref) | dents > δ_acc, 5/5 → **gate FIRES** |
| **proto-reanchor** (primary) | **0.986 [0.978–0.993]** | — | +0.199 | **recovers → ADOPT** |
| SLDA cov re-fit (fallback) | — | — | — | not exercised (primary sufficed) |

- **RESIDUAL** (headline): the input-transducer directional residual dents the committed SLDA loop in **5/5** seeds
  (median dent +0.115, min +0.066 > δ_acc; worst seed 1729 collapses undefended retention to 0.504) → the gate fires.
  Prototype re-anchoring lifts retention to **0.986 [0.978–0.993]** — every seed ≥ 0.977, within δ_acc of the
  no-residual level — so the read-side defense recovers the channel.
  - **INV**: all nine guards green (partial-fit-equiv, fd-budget, meter-proxy, detector-FAR, scff-static-frozen,
    live-path-anchor, cache-replay, n2-readside, evict-equiv).

**Read (8 slots).**
1. *Claim* — the Phase-6 input-transducer directional residual really dents the committed SLDA loop (earns its place),
   and prototype re-anchoring from the raw LUT recovers it read-side (the residual is *resolved*, not named).
2. *Headline* — dent +0.115 [0.093–0.145] (5/5 > δ_acc) → undefended retention 0.787 [0.738–0.833]; proto-reanchor
   restores 0.986 [0.978–0.993] (+0.199, 5/5) (n=5, live committed loop, home residual). Internal refs only.
3. *Figures* — RESIDUAL (undefended vs read-side-defended, vs no-residual reference), INV (guards green).
4. *Mechanism* — the residual is a **coherent directional translation** along the input class axis — a *fixed device
   offset*, not iid nuisance — so SCFF's per-sample norm cannot forward-remove it and the deployed prototypes (fit on
   clean reps) sit off-axis at read time → the head reads a shifted direction → retention drops. **proto-reanchor**
   re-forwards the raw LUT through the *current* bulk under the *same* device offset, producing prototypes that are
   drift-free and shift-**consistent** with the read — the head reads a consistent direction again. This is
   **direction-grounded** (the prototypes move with the class axis), never an entropy/confidence magnitude — the spine.
   It is the plan's own sleep mechanism (re-forward raw exemplars), applied under shift; no new organ.
5. *Threats* — (a) the gate/defense are tuned on the **home** residual only; P10 must show the defense on a held-out
   noise battery (different σ / channel mix) — stated, not pre-run here. (b) the residual and the re-anchor share one
   device-offset draw (same chip) by construction; a mismatched draw would be a direction bug — guarded by the shared
   `DEV` seed. (c) the meter is a behavioral model (params logged); calibration is feature-level (proto re-anchor), not
   scalar TS (ineffective under shift). Rule-1: one variable (the read-side defense) at the fired gate.
6. *Decision* — the **read-side residual is resolved read-side** (proto-reanchor adopted), not handed to the analog
   layer. P9.5 carries proto-reanchor as the committed read-side defense (dormant on a clean stream; active under the
   input-transducer channel). The Phase-6 "scoped-YES → Stage-2 read-side" debt is **discharged**.
7. *Freeze-honesty* — **internal-signals-only affirmed** (no P10 baseline consulted; tuned on the home residual, not the
   P10 showcase battery). proto-reanchor is a sleep-time prototype re-fit — no extra awake fires — so GD-share is
   unchanged (≤ 0.25). Meter model + params logged in the manifest.
8. *Live-safety* — the defense operates at the read side / sleep, so live A6 continual-safety is the committed loop's
   (unchanged on a clean stream); under the residual channel it lifts retention back to the clean level. Carried into
   the P9.5 assemble as the committed read-side defense.
