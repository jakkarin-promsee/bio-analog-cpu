# P10.0 — The bench: the fair racer + the gauntlet harness + the six new guards (no verdict — a build)

**Question.** Phase 10 races the *frozen* object against an *external* BP+replay baseline — so before any number is
believed, the apparatus itself must be certified: is the racer a *fair* (byte- + FLOPs-budgeted, tuned) opponent and
not a strawman; is the object we race provably the *frozen* grid-4 (content manifest + bit-exact reproduction); does
the gauntlet load offline at the shared 40-D input; is the noise battery genuinely *held-out* from P9.4; and is
accuracy provably substrate-independent? A broken bench poisons every verdict, so **any guard red → STOP.**

**Setup.** No swept variable — a build + the fourteen guards (the eight carried P8/P9 + the six new P10). Controls
locked: the frozen object (`COMMITTED_LOOP` + `cadence_every=4` + `HEAD="slda"` + SLDA/cell config; provenance
`59d2720`), the ER-strong tuning protocol (disjoint tuning stream **seed 7 ∉ [42,137,271,314,1729]**; K2), the
byte-match (ER buffer == OURS's raw-prototype LUT), the shared 40-D gauntlet input (one pinned seed-frozen 64→40
Gaussian projection), the margin-disjoint noise battery (dir-RMS 2.5 vs P9.4's 1.5; ADC 3 vs 2). Figure: INV.
Apparatus: `p10lib` (`ContinualBP`, `fair_budget_meter`, `make_gauntlet_stream`, the six guards) on `p9lib`.
**Verdict shapes for P10.1–P10.6 pinned BLIND before this run.**

**Run.** Guards evaluated once (seed-independent by construction; freeze/cadence build a real seed-42 lifelong cache
and reproduce grid-4 bit-for-bit). ER-strong selected on seed 7 only. Wall ≈ 3.2 min.

**Result / figures.**

*The fourteen guards (any fail → STOP) — all green:*
| guard | measured | pass |
| --- | --- | --- |
| partial_fit_equiv (ranpac / slda) | 4.11e-15 / 2.22e-16, pred-miss 0 | ✓ |
| fd_budget_gate | 3.47e-08 | ✓ |
| meter_proxy | fwd-MAC 1 556 000 ≡ readout_cost | ✓ |
| detector_far floor | {abs 0.0, ddm 0.0, adwin 0.0} | ✓ |
| scff_static_frozen | 0.00e+00 (static acc 0.566) | ✓ |
| cache_replay | 0.00e+00, fire-diff 0 | ✓ |
| n2_readside | run_economy_p9(off) ≡ P8 0.0; LLRD ρ=1 0.0 + early taps clean | ✓ |
| evict_equiv | cap=∞ retains all; cap=30 recency ≡ last-30 FIFO | ✓ |
| **fair_budget** | OURS-LUT 196 800 B **==** ER-budget buffer 196 800 B; ER FLOPs/sample reported | ✓ |
| **freeze_content** ⭐ | manifest OK **and** grid-4 bit-exact (dBWT 0, dAA 0, dGD 0, dNslp 0; `59d2720` provenance) | ✓ |
| **cadence_family** | grid-4 bit-exact; nsleep {4:25, 5:20, 6:16, 8:12, 16:6} monotone-desc | ✓ |
| **gauntlet_data** | 5 domains @ 40-D; one 64→40 projection; one stream; labels ⊆ 10 | ✓ |
| **noise_holdout** | dir-RMS 2.5 vs P9.4 1.5 (margin +1.0); ADC 3 vs 2 → margin-disjoint | ✓ |
| **substrate_identity** | acc substrate-independent; E(analog) 2.88e7 ≠ E(digital) 1.47e8 | ✓ |

*The tuned ER-strong (seed 7 only) + the fair-budget audit (FLOPs/sample · replay-bytes · total-memory):*
| learner | FLOPs/sample | replay-bytes | total-bytes | note |
| --- | --- | --- | --- | --- |
| **ER-strong** | 65 268 | 196 800 | 374 616 | dims [40,49,49,49,10], lr 1e-3, wd 1e-3, replay 64 (tune-AA 0.540) |
| ER-budget | 27 195 | 196 800 | 374 616 | throttled replay 8 (the same-FLOPs point) |
| A-GEM | 65 664 | 196 800 | 375 216 | one-constraint projection (real BPNet grad-handle) |
| DER++ | 109 440 | 244 800 | 423 216 | logit buffer + distillation (bytes count logits; FLOPs count the extra forward) |
| GDumb | 0 (trains at eval) | 196 800 | 375 216 | cost-pathological — accuracy-axis control |
| naive-BP | 21 888 | 0 | 178 416 | the forgetting floor |
| **OURS grid-4** | **96 938** | 196 800 | 5 357 760 | the 12-layer SCFF bulk forwards every step (threat (h): more weights) |

- **INV**: all fourteen guards green.

**Read (8 slots).**
1. *Claim* — the bench is fair and the object is provably frozen: ER's buffer byte-matches OURS's LUT, ER-strong is
   tuned on a seed disjoint from the raced set, the grid-4 object reproduces the P9 freeze bit-for-bit, the gauntlet
   loads offline at 40-D, the noise battery is margin-disjoint, and accuracy is substrate-independent.
2. *Headline* — 14/14 guards green; grid-4 bit-exact (dBWT/dAA/dGD/dNslp all 0); ER-strong = [40,49,49,49,10]/replay 64
   (tune-AA 0.540, seed 7 only). No verdict on this rung.
3. *Figures* — INV (fourteen guards).
4. *Mechanism* — freeze-content reproduces the object from `{**COMMITTED_LOOP, cadence_every: 4}` (Trap 1: the baked
   `8` overridden) and asserts equality to the stored `figs_p9_5_cadence` grid-4 slice; substrate-identity holds
   because predictions come from `run_economy_p9`, which never sees the substrate (it enters only `meter_from_trace`'s
   per-op energy).
5. *Threats* — (a) the meter is behavioral (params logged in the manifest); (b) the fight's fairness rides on ER being
   tuned + byte/FLOPs-matched — both ER-budget (same-FLOPs) and ER-strong (own config) are built; **(h) parameter
   asymmetry is real and surfaced here: OURS's 12-layer bulk uses MORE FLOPs/sample (96 938) than ER-strong (65 268)**,
   so the same-substrate (digital) energy cut is genuinely contestable, not pre-baked — the analog crossbar is what
   prices those bulk MACs near-zero (R1). Rule-1: none — a build.
6. *Decision* — bench **ALL-GREEN → proceed to P10.1**. A-GEM/DER++ descope decided **False** (the `BPNet` grad-handle
   refactor is clean and both run) — the **full roster is real code**, not documented-simplified field points.
7. *Freeze-honesty* — the object was frozen **before** this run (freeze-content manifest + grid-4 bit-exact; `59d2720`
   is a provenance label, not a runtime git `==`); the verdict shapes for P10.1–P10.6 were pinned BLIND in `design.md`
   §2.3 before any baseline number existed; the only object dial that will move is the declared cadence cost axis.
8. *Where-it-stands* — nothing is validated yet; this rung certifies the instrument. The FLOPs asymmetry pre-registers
   the honest tension P10.1 must resolve: the energy win may be **substrate** (analog), and the same-substrate
   **algorithm** cut is the contestable branch to watch.
