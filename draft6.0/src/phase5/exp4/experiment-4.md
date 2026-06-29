# P5.4 — the readout MVP: per-depth heads Pareto-dominate all-tap

*Inheriting the committed cell (temp0.2/w2) and P5.3's placement story (read the extractor's end; truncation floor
0.564), this opens the READ-accuracy thread: can a tiny per-depth head MATCH the deployed all-tap readout at lower
forward cost? It does better — on composite tasks it BEATS all-tap, and everywhere at a fraction of the cost.*

**Question.** Do per-depth deep-supervision heads (pure `read`, one tiny readout at each SCFF depth) match the
all-tap concatenation readout (the thing they'd replace) at lower forward cost — and how does the best head sit vs
the truncation floor (0.564)?

**Setup.** Committed cell (temp0.2/w2, L12·W64), headroom + flat + mixed, 5 seeds, PROBE_EP=120. Per depth: a LINEAR
head (Mono-Forward projection→CE, cheapest) and a capacity-matched MLP head `[W,32,C]`. all-tap = one MLP `[L·W,32,C]`
on the full concatenation. Readout params matched by construction (heads 26 544 ≈ all-tap 24 740, 1.07×) so a gap is
**structure, not capacity**. Forward-MACs metered: read-best-head (forward to best_d + one head) vs all-tap (forward
all L + the big head). head-best = the **oracle** depth (post-hoc argmax) — the ceiling P5.5's calibrated exit chases.
Guards passed (equiv 0.0, FD 2.06e-08).

**Run.** 15 cells × (24 probes + all-tap), checkpointed; wall ≈ 11 min.

**Result / figures.** *(median [IQR], n=5)*
| task | head-best (MLP) | head-best (lin) | all-tap | **Δ head−alltap** | sign | read-cost | best_d |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **headroom** | **0.573** [0.556–0.577] | 0.556 | 0.526 [0.525–0.535] | **+0.047** | **5/5** | 0.29× | L5 (L3–L7) |
| **mixed** | **0.633** [0.617–0.635] | 0.609 | 0.611 [0.607–0.620] | **+0.021** | **5/5** | 0.29× | L4–5 |
| **flat** | 0.785 [0.782–0.787] | 0.747 | 0.783 [0.778–0.787] | +0.002 | 4/5 | 0.12× | L2 (L1–L3) |

Truncation floor (P5.3) = 0.564; headroom head-best 0.573 clears it (+0.009).

- **PLACEMENT-heads-headroom** (headline): the MLP-head curve is a **flat-high plateau L3–L12 (~0.55–0.56)** sitting
  *at/above* the truncation floor (0.564); all-tap (dashed) sits **below** at 0.526; the linear head ramps L1→L4 then
  tracks MLP. all-tap is the worst readout option on the figure. - **flat**: heads peak at L1–L2 then slope down (the
  P5.3 tunnel); all-tap ties only because the easy task's signal is L1-dominant. - **INV**: clean.

**Read (6 + 2 slots).**

1. **Claim** — Per-depth heads **Pareto-dominate** all-tap: on composite tasks (headroom, mixed) the single best head
   is **both cheaper and more accurate** than concatenating all layers; on the easy task it ties at 1/8 the forward
   cost. all-tap is dominated — adopt heads as the readout base.
2. **Headline** — headroom head-best **0.573** vs all-tap 0.526 (**Δ+0.047, 5/5**, 0.29× cost); mixed 0.633 vs 0.611
   (Δ+0.021, 5/5, 0.29×); flat 0.785 vs 0.783 (tie, 4/5, **0.12×** cost). Best head clears the truncation floor
   (0.573 > 0.564). (n=5.)
3. **Figures** — PLACEMENT-heads-{headroom, flat, mixed}, INV. Regen from `arrays.npz`.
4. **Mechanism** — *Why all-tap loses on composite tasks.* The decay (P5.0/P5.3) is the late layers **drifting off the
   class direction** — they're not dead, they're misleading. all-tap concatenates them in, and a capacity-limited MLP
   readout cannot zero-weight drifted-but-correlated features cleanly, so the tunnel **dilutes** the class signal
   (headroom −0.047, mixed −0.021). Reading **one** clean depth (the extractor's end) sidesteps the tunnel entirely —
   the spine again: the win comes from reading the class *direction* at the depth it's sharpest, not from pooling
   magnitude across all depths. On flat the signal is L1-concentrated, so all-tap's dilution is small (tie) but it
   still pays 8× the forward cost. **Linear ≈ MLP head** (within 0.02–0.04; the residual is mildly nonlinear — MLP buys
   a touch) → the **linear head is the deployable base** (Mono-Forward, cheapest), MLP an optional upgrade.
5. **Threats** — (a) head-best is an **ORACLE** depth (post-hoc argmax); the deployed reader must *select* the depth
   without the label. best_d spreads **L3–L7 across seeds on headroom**, so selection is non-trivial → P5.5 must show a
   calibrated **head-confidence** exit (the spine — NOT goodness) reaches near this oracle. The figure's median-*curve*
   peak (0.563 @ L9, a broad plateau) vs the median per-seed-peak (0.573) brackets the oracle gap. (b) on headroom the
   accuracy value of placement is **small** (plateau, head-best only +0.009 over the floor) — there the READ value is
   **cost** (0.29×), not accuracy; the accuracy win is real on composite/easy-corrupted tasks. (c) static workload only;
   the continual cost/accuracy (the real 80/20 meter) is P5.5.
6. **Decision** — **ADOPT per-depth heads as the readout base; all-tap is Pareto-dominated** (more forward cost, ≤
   accuracy). **Linear head = the cheap deployable base; MLP = optional +0.02–0.04 upgrade.** The "where to read"
   selector — a calibrated, head-confidence exit — is **P5.5** (on the continual stream, vs the 0.564 floor).
   **P5.6 (preservation) stays LOW-VALUE** (heads already beat all-tap by sidestepping the tunnel, not preserving it).
7. **Cost-honesty** — the heads win is *both* accuracy (headroom +0.047, mixed +0.021 over all-tap) *and* forward cost
   (0.12× flat, 0.29× headroom/mixed — forward to best_d + one small head, not all 12 + the big head). The deployed
   80/20 backward cost on the continual stream is P5.5/P5.7, not yet measured.
8. **SCFF-completion** — READ-accuracy half **DONE**: a tiny per-depth head matches/beats the all-tap baseline cheaply.
   READ-selection half is P5.5 (calibrated exit reaches the oracle head-best on continual + beats 0.564). Not done:
   P5.5 (the exit), P5.7 (continual-safety gate). Continual-safety NOT checked here (static).

**Pre-submit checklist.** [x] Median [IQR], n=5. [x] "Real" rule (headroom/mixed IQR-disjoint + 5/5; flat tie 4/5).
[x] Params matched (heads 26 544 ≈ all-tap 24 740) → gap is structure. [x] Forward-MACs metered (read-best vs all-tap).
[x] Truncation floor (0.564) drawn; head-best clears it. [x] Figures via `plot_p5.fig_heads`; regen redraws all.
[x] 8 slots, formal voice; opens naming the inherited cell. [x] manifest+arrays to schema. [x] Guards logged (FD
2.06e-08). [x] Single-threaded. [x] Spine: read the class *direction* at one sharp depth; all-tap dilutes with drifted
late layers; no goodness. [x] Oracle-depth caveat flagged (→ P5.5 calibrated exit). [x] Continual (P5.7): not run.
[x] `RESULTS.md` row added.
