# P5.3 — lost-or-rotated, the profiler, and the truncation floor: placement value is task-dependent

*Inheriting the committed cell (temp0.2/w2, the EARN-depth thread closed at P5.2), this opens the READ thread: is
the decayed info recoverable, where does the extractor end per task, and what is the cost floor every reader must beat?*

**Question.** (a) Is the post-peak info **lost** or **rotated** (MLP vs linear probe)? (b) Where does the extractor
end (the profiler), and does the probe peak agree with the readout-optimal depth? (c) What is the **truncation floor**
— a from-scratch short stack the READ tiers must beat?

**Setup.** Committed cell (temp0.2/w2, L12), headroom + flat + mixed, 5 seeds, PROBE_EP=120. Per depth: linear probe,
MLP probe (headroom), and the **real readout fit at each depth** (the readout-optimal placement). Complexity: headroom
overlap {0.4,0.6,0.9}. Truncation: from-scratch L∈{5,7,9} (matched budget) + **L7 own-tuned** (lr×ep grid — the
fairness arm), read at the top. Guards passed.

**Run.** ~30 cells × 5 seeds, checkpointed; wall ≈ 19 min.

**Result / figures.** *(median [IQR], n=5)*
| task | readout @ extractor-end (best) | readout @ top (L12) | **placement gain** | probe-peak ↔ readout-opt |
| --- | --- | --- | --- | --- |
| **flat** | 0.785 [0.782–0.787] @ L2 | 0.677 [0.671–0.677] | **+0.108** | L4 ↔ L2 (disagree by 2) |
| **mixed** | 0.773 [0.768–0.777] | 0.696 [0.689–0.701] | **+0.077** | L4–5 ↔ L2–3 |
| **headroom** | 0.563 @ L9 | 0.550 [0.545–0.553] | +0.013 (broad plateau) | L8 ↔ L9 (**agree ±1**) |

| truncation floor (headroom, top-readout) | L5 | L7 matched | **L7 own-tuned** | L9 | full-L12 best / top |
| --- | --- | --- | --- | --- | --- |
| top-readout | 0.557 | 0.543 | **0.564 [0.556–0.565]** | 0.557 | 0.573 / 0.550 |

- **PLACEMENT-flat** (headline): the readout slopes **down** L2→L12 (0.785→0.677) — deep layers are pure tunnel that
  wastes the L2-extracted info. - **PLACEMENT-headroom**: a broad plateau L3–L11 (~0.55–0.56), linear≈MLP (lost, not
  rotated), the truncation floor (0.56) sitting on the plateau. - **INV**: clean.

**Read (6 + 2 slots).**

1. **Claim** — The small residual decay is genuinely **lost** (not rotated); **placement value is task-dependent and
   large on easy tasks** (read the extractor's end, not the top); a short from-scratch stack matches the full one read
   optimally.
2. **Headline** — reading the extractor end vs the top: **flat +0.108** (0.785@L2 vs 0.677), mixed +0.077, headroom
   +0.013 (broad plateau, probe-peak L8 ↔ readout-opt L9 agree). Truncation L7-own-tuned **0.564** ≈ full-L12-best
   0.573, beats L12-top 0.550. (n=5.)
3. **Figures** — PLACEMENT-{flat (downward slope), headroom (plateau), mixed}, INV. Regen from `arrays.npz`.
4. **Mechanism** — The extractor ends where the task's class-abstraction saturates: **flat saturates at L2** (read
   there; everything deeper is tunnel that mildly *drifts the rep down*), **headroom composes to ~L8** (a broad
   plateau). The deep layers add nothing on an easy task and slightly degrade it — the tunnel, in the readout's own
   metric. The residual decay is **lost, not rotated** (MLP recovers Δ0.005 at L12) — but small at temp0.2, so
   placement (read the end) **sidesteps** it; preservation would buy only ~0.02. The profiler (probe peak) agrees with
   the readout-optimal on headroom (±1) but runs ~2 layers **too deep** on flat/mixed → placement must be
   **readout/head-driven**, the spine (read the class *direction* / head-confidence, not the probe).
5. **Threats** — (a) the complexity sweep used a **difficulty** dial (overlap), not a compositional-**complexity** one
   (grid/n_active) → "extractor length rises with complexity" is **untested by the right dial**; what we found is the
   peak is *difficulty-invariant* (set by structure, peak 6/6/4 over overlap 0.4/0.6/0.9) — honest, re-test owed with a
   structure dial. (b) truncation L7-matched (0.543) dips below L5/L9 (0.557) — non-monotonic noise; the **own-tuned
   floor (0.564)** is the fair one (matched-budget undersells — validating the own-tune delta). (c) on headroom the
   readout plateau makes placement's *accuracy* value small (~0.01) — there the READ value is **cost**, not accuracy.
6. **Decision** — Lever class = **PLACEMENT (read the extractor's end), not objective-surgery** (decay small + lost).
   **The truncation floor = 0.564 (L7-own) / 0.573 (L12-best)** — the control P5.4/5.5 must beat on the continual
   workload. Placement is **readout/head-driven** (→ P5.4 heads). **P5.6 (preservation) flagged LOW-VALUE** (decay
   ~0.02, lost, placement sidesteps it) → likely skipped pending the P5.4/5.5 gap test. P5.4 inherits: read shallow on
   flat/mixed, the plateau on headroom; beat 0.564.
7. **Cost-honesty** — the placement win is *both* accuracy (flat +0.11, mixed +0.08 over naive top-reading) *and* cost
   (read ~L2 on flat, ~L5–9 on headroom, not all 12). Truncation shows ~5–7 layers suffice on headroom, ~L2–3 on flat
   → **fewer Scaps**. The continual-workload cost (the real 80/20 meter) is P5.5, not yet measured.
8. **SCFF-completion** — the READ thread's target is set: read the extractor's end cheaply and beat the truncation
   floor (0.564) on the continual stream. The profiler gives the "where," truncation gives the "floor." Not done:
   P5.4 (do heads match all-tap?), P5.5 (does exit beat the floor on continual?), P5.7 (the gate). Continual-safety NOT
   checked.

**Pre-submit checklist.** [x] Median [IQR], n=5. [x] "Real" rule applied (placement gains IQR-disjoint on flat/mixed;
headroom plateau within-noise). [x] Truncation floor established (own-tuned, the fair arm). [x] Figures via
`plot_p5.fig_*`; regen redraws all. [x] 8 slots, formal voice; opens naming the inherited cell. [x] manifest+arrays to
schema. [x] Guards logged (FD 2.1e-8). [x] Single-threaded. [x] Spine: placement = read the class *direction*/head, not
the probe (which runs too deep on easy tasks); no goodness. [x] Complexity-dial caveat flagged honestly. [x] Continual
(P5.7): not run. [x] `RESULTS.md` row added.
