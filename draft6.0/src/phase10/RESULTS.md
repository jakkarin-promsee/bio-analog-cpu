# Phase 10 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema (no prose). Controls locked unless swept. Device under test = the
> **FROZEN** two-brain object (`NoiseAugContrast` SCFF bulk · SLDA namer · DDM/error-EMA awake gate · CBRS · all-tap
> sleep · proto-reanchor · **grid-4** cadence; provenance `59d2720`), raced against a **fair, budgeted, tuned**
> BP+replay baseline. Seeds `[42,137,271,314,1729]`. Median `[q25–q75]`. δ_acc = 0.02. **Phase 10 JUDGES against the
> EXTERNAL BP+replay baseline (the honest inversion of P9's internal-only rule) — but the verdict SHAPES were pinned
> BLIND (design §2.3) before any baseline number was seen.** The cost meter is the P8 behavioral ADC-centred model,
> NOT SPICE; the load-bearing energy cut is **same-substrate** (`E(OURS-digital)` vs `E(ER-digital)` = the algorithm
> win); the analog total is a meter-structural floor overlay.

Ran 2026-07-03 (seeds `[42,137,271,314,1729]`, `--quick` off, single-thread CPU/float64, numpy 2.3.5). All fourteen
guards (8 carried P8/P9 + `fair_budget` + `freeze_content` + `cadence_family` + `gauntlet_data` + `noise_holdout` +
`substrate_identity`) green every rung; grid-4 reproduced bit-for-bit against the P9 freeze. **§10 post-close
extension re-ran P10.1/P10.2/P10.3/P10.6 in four rounds (design §10 — round 1: grid-12, the per-batch GAUNTLET-STREAM
view, the full-family Pareto; round 2: the ours_g5 fight point withdrawn by the author, the cliff probes {7,13,14,15},
the REVERSED stream view completing K9's ER leg, the all-grid Pareto; round 3: the E8 ALIGNMENT-BREAK long stream +
the E8b aligned-long control + the E9 numbered-point legibility redraw; round 4: the E10 REVERSED-LONG
staircase-mechanism test + the D1 staircase description): measurement-only; every carried array
reproduced bit-exactly each round (snapshot-diffed; the E1 withdrawal reproduced the committed P10.1 arrays
IDENTICALLY; round 3 reproduced all 86 carried keys, round 4 all 105); the three replay guards (cell
fingerprint+phi_b · err_trace · energy-endpoint) held on all seeds, all stream layouts.**

---

## P10.0 — bench: the fair racer + the gauntlet harness + the six new guards *(no verdict — a build)*

*Controls: frozen grid-4 object; ER-strong tuned on the disjoint seed 7; byte-matched buffers; shared 40-D gauntlet;
margin-disjoint noise battery. 14 guards, seed-independent (freeze/cadence build a seed-42 lifelong cache).*

| guard | value · vs-reference | pass? | verdict |
| --- | --- | --- | --- |
| fair_budget | OURS-LUT 196 800 B **==** ER-budget 196 800 B; FLOPs/sample reported all learners | ✓ | racer byte-matched, not a strawman |
| freeze_content ⭐ | manifest OK **and** grid-4 bit-exact (dBWT/dAA/dGD/dNslp = 0; `59d2720` provenance) | ✓ | the object is provably frozen |
| cadence_family | grid-4 bit-exact; nsleep {4:25,5:20,6:16,8:12,16:6} monotone-desc | ✓ | family = declared cost axis |
| gauntlet_data | 5 domains @ 40-D; one 64→40 projection; one stream; labels ⊆ 10 | ✓ | offline, no leakage, input-identical |
| noise_holdout | dir-RMS 2.5 vs P9.4 1.5 (+1.0); ADC 3 vs 2 | ✓ | battery margin-disjoint |
| substrate_identity | acc substrate-independent; E(an) 2.88e7 ≠ E(di) 1.47e8 | ✓ | substrate axis is energy-only |
| + 8 carried P8/P9 | partial_fit 4e-15 · meter_proxy ≡ · scff-frozen 0 · cache-replay 0 · n2/evict … | ✓ | apparatus bit-exact |

| fair-budget audit | FLOPs/sample | replay-bytes | total-bytes | note |
| --- | --- | --- | --- | --- |
| ER-strong | 65 268 | 196 800 | 374 616 | [40,49,49,49,10]/lr1e-3/replay 64 (tune-AA 0.540, seed 7) |
| ER-budget | 27 195 | 196 800 | 374 616 | same-FLOPs point (replay 8) |
| A-GEM | 65 664 | 196 800 | 375 216 | one-constraint (real grad-handle) |
| DER++ | 109 440 | 244 800 | 423 216 | logit buffer + distillation |
| GDumb | 0 (eval-time) | 196 800 | 375 216 | cost-pathological control |
| naive-BP | 21 888 | 0 | 178 416 | forgetting floor |
| **OURS grid-4** | **96 938** | 196 800 | 5 357 760 | 12-layer bulk forwards every step (threat h) |

**Verdict:** bench ALL-GREEN → proceed. Full roster is real code (A-GEM/DER++ descope = False). Pre-registered
tension: OURS uses *more* FLOPs/sample than ER-strong → the same-substrate energy cut is genuinely contestable.

---

## P10.1 — the existential fight: OURS(grid-4) vs a budgeted, tuned ER + field *(learner swept)*

*Controls: frozen grid-4, lifelong synthetic home (class-IL leg, n_steps 536), ER-strong seed-7-tuned + byte-matched,
5 seeds. BWT = worst-pre-sleep (P9 honest read, every learner — R6).*

| learner | accuracy | E(analog) | E(digital) | worst-BWT | AAA | vs-OURS · verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **ours_g4 (OURS)** | **0.494 [0.478–0.502]** | 6.70e7 | 3.46e8 | **−0.028** | 0.392 | (ref) · safest of the field |
| er_strong | 0.498 [0.490–0.501] | 3.71e7 | 2.25e8 | −0.272 | 0.503 | acc tie (+0.004); worst-BWT 10× worse |
| er_budget | 0.376 [0.375–0.380] | 1.55e7 | 9.41e7 | −0.807 | 0.461 | OURS +0.118 acc |
| agem | 0.320 [0.320–0.333] | 3.40e7 | 2.26e8 | −0.900 | 0.445 | OURS +0.174 acc |
| derpp | 0.360 [0.358–0.365] | 5.67e7 | 3.76e8 | −0.178 | 0.455 | OURS +0.134 acc |
| gdumb | 0.430 [0.427–0.447] | 1.14e7 | 7.59e7 | −0.344 | 0.568 | OURS +0.064 (cost-pathological control) |
| naive | 0.308 [0.297–0.317] | 1.14e7 | 7.59e7 | −0.880 | 0.434 | the forgetting floor |
| joint-BP ceiling | 0.870 [0.870–0.882] | — | — | — | — | offline summit reference |

- same-substrate (digital) algorithm cut: E(OURS) 3.46e8 vs E(ER-strong) 2.25e8 → **1.54× more** (the deep bulk).
- total (chip vs conventional GD): OURS-analog 6.70e7 → **3.35× cheaper** than ER-on-digital (substrate-realized).

**Verdict:** ACCURACY-COMPETITIVE (tie within δ, OURS 3/5 seeds) / **continual-safety WIN** (worst-BWT −0.028 vs
−0.272) / algorithm-energy NOT a win same-substrate / energy win is **substrate-realized** (3.35× via analog). AAA
favors ER (0.503 vs 0.392 — the sleep-cadence anytime tax). Two halves banked separately: accuracy **supported**,
economics **substrate-realized**. *(§10 E1: an ours_g5 roster point was added, then **withdrawn** by the author in
round 2 — within-noise, added confusion; grid-5 lives in P10.2 + the P10.6 family line. The withdrawal re-run
reproduced the committed arrays IDENTICALLY, every key bit-for-bit.)*

---

## P10.2 — the cadence frontier: the family {4,5,6,8,12,16} + the §10 cliff probes {7,13,14,15} *(cadence swept)*

*Controls: frozen object, lifelong synthetic home, 5 seeds. grid-4 bit-exact vs `figs_p9_5_cadence` (guard). §10
re-runs: all carried arrays bit-exact each round; grid-12 (E2) filled the 8→16 gap, the probes (E5) localized both
cliff edges. Probes are characterization points, NOT family members.*

| grid | accuracy | energy (pJ) | worst-BWT | oracle-wBWT | GD-share | nsleep | Pareto? · verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **g4 ⭐** | 0.494 [0.478–0.502] | 6.70e7 | **−0.028 [−0.039–−0.022]** | −0.028 | 0.178 | 25 | committed headline (no swap) |
| g5 | 0.495 [0.483–0.523] | 5.99e7 | −0.039 [−0.050–−0.033] | −0.167 | 0.166 | 20 | **Tier-1 showcase rep** (δ-eligible) |
| g6 | 0.495 [0.483–0.523] | 5.42e7 | −0.087 [−0.093–−0.067] | −0.087 | 0.153 | 16 | Tier-1, fails δ-BWT gate (the safety **edge**) |
| g7 (probe) | 0.496 [0.473–0.508] | 5.13e7 | −0.322 [−0.356–−0.278] | −0.350 | 0.146 | 14 | ⚠ the safety **plunge** (already g8-deep) |
| g8 | 0.494 [0.478–0.502] | 4.85e7 | −0.317 [−0.439–−0.267] | −0.289 | 0.138 | 12 | ⚠ Tier-2 forgets (veto-fail) |
| g12 (§10) | 0.496 [0.473–0.508] | 4.28e7 | −0.339 [−0.367–−0.333] | −0.461 | 0.119 | 8 | ⚠ Tier-2 forgets; AA still holds |
| g13 (probe) | 0.474 [0.438–0.478] | 4.13e7 | −0.433 [−0.461–−0.400] | −0.447 | 0.113 | 7 | ⚠ AA wobbles to the exact δ boundary |
| g14 (probe) | 0.496 [0.473–0.508] | 4.13e7 | −0.444 [−0.450–−0.328] | −0.533 | 0.113 | 7 | ⚠ AA back to plateau (timing-sensitive zone) |
| g15 (probe) | 0.495 [0.483–0.523] | 3.99e7 | −0.428 [−0.444–−0.406] | −0.500 | 0.107 | 6 | ⚠ AA holds at the SAME energy/nsleep as g16 |
| g16 | 0.458 [0.458–0.478] | 3.99e7 | −0.367 [−0.383–−0.367] | −0.540 | 0.107 | 6 | ⚠ Tier-2 AA drop > δ (the accuracy **cliff**) |

**Verdict:** grid-4 = committed headline (never swapped, bit-exact). Tier-1 showcase rep = **grid-5**; grid-6 fails the
δ-BWT gate (−0.087). The Tier-2 break is a **two-cliff plateau**, now localized by the probes: the **safety axis breaks
in two steps** — the δ-edge at grid-6 (−0.087) and the **plunge at grid-7** (−0.322, already grid-8-deep; nsleep 16→14
is where mid-interval troughs outrun the sleeps) — while **final AA plateaus (0.494–0.496) all the way through
grid-15** (one borderline wobble at g13, 0.474 = exactly the δ boundary) and **cliffs only at 15→16** (0.458). The
sharpest mechanism read: **g15 and g16 have the SAME energy (3.99e7) and the SAME sleep count (6) but AA 0.495 vs
0.458** — at ~6 sleeps the outcome stops being count-limited and becomes **sleep-TIMING-sensitive** (whether the sparse
consolidations happen to cover the revisit structure); the g13/g14 wobble is the same zone's signature. Worst-case
safety degrades ~a full tier before average accuracy. Energy monotone with cadence (6.70e7 → 3.99e7); GD-share 0.178 →
0.107 (all ≤ 0.25). Declared cost axis + characterization probes.

---

## P10.3 — the multi-domain gauntlet (the money figure) *(config swept; 5 native domain-IL digit worlds)*

*Controls: frozen object at all 5 grids vs ER-strong; domains {identity,permuted,rotated,covariate,noised} → shared
40-D input, shared head; cross-domain replay probe (domain-IL fair); 5 seeds + reversed-order control. Retention =
worst pre-sleep all-prev AA (R6).*

| config | final all-prev | worst all-prev | AAA | worst-BWT | cum-energy E(dig) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **OURS grid-4 ⭐** | 0.490 [0.480–0.499] | **0.490** | **0.519** | −0.012 | 7.40e7 | steadiest retention |
| OURS grid-5 (rep) | 0.490 [0.480–0.499] | 0.463 | 0.494 | −0.038 | 6.80e7 | Tier-1 cheaper rep |
| OURS grid-8 | 0.487 [0.483–0.491] | 0.464 | 0.505 | −0.036 | 5.59e7 | Tier-2 (cheaper, less safe) |
| OURS grid-16 | 0.487 [0.483–0.491] | 0.223 | 0.409 | −0.040 | 4.98e7 | Tier-2 (worst-point collapse) |
| **ER-strong** | 0.504 [0.488–0.515] | 0.350 | 0.433 | 0.000 | 5.03e7 | higher final, dips mid-stream |

- same-substrate (digital) cut: OURS g4 7.40e7 vs ER 5.03e7 → **1.47× more**; substrate total (OURS-analog vs
  ER-digital): **3.5× cheaper**. reversed-order AA Δ (g4): **−0.014 [−0.032–+0.018]** (order-robust). throughput: ER
  rel-complexity 0.71× (FLOPs-lighter), steps-behind 0.
- SCFF:Namer GD-share per domain (grid-4): stored (`gdshare_g4`) — low across domains (gate rarely fires; the loop
  consolidates via sleep).
- **§10 E3 — the per-batch GAUNTLET-STREAM view (triple-guarded lockstep replay; all carried arrays bit-exact):**
  live-batch (prequential) mean **OURS 0.469 vs ER 0.273** — ER crashes to ~0.1 at every domain onset and re-climbs
  (the saw-tooth), OURS rides near-flat; final seen-so-far equals the committed final all-prev (0.490 vs 0.504).
  Cumulative energy at batch resolution: OURS = a sleep **staircase**, ER = a smooth ramp; OURS stays the pricier
  same-substrate line throughout (the 1.47×, now exact per batch — supersedes the proportional per-domain shape).
- **§10 E6 — the REVERSED stream view (noised FIRST; completes K9's ER leg):** the low region **moves with the noise**
  (both learners start ~0.1 on the noised block — position-independent, noise-specific), and the order-sensitivity is
  starkly **asymmetric**: **ER's reversed final AA collapses to 0.343 [0.336–0.370] vs its forward 0.504 (Δ −0.161)**
  — a hard/noisy-first curriculum wrecks its whole trajectory (its net + reservoir are shaped by noise early) — while
  **OURS holds 0.494 vs 0.490 (Δ +0.004)**, climbing domain-by-domain regardless of order (the unsupervised bulk
  learns structure even from the all-noisy start — the Phase-6 Door-B result, visible live). ER's committed forward
  number was the *favorable* ordering; OURS's is order-invariant. Live-batch means (rev): OURS 0.445 vs ER 0.225.
- **§10 E8/E8b — the ALIGNMENT-BREAK long stream (round 3; blocks [68,63,56,57,68] = 312 steps, sleeps MID-domain) +
  the aligned-72 control:**

| arm | OURS g4 worst all-prev | OURS final AA | ER final AA | read |
| --- | --- | --- | --- | --- |
| committed (block 24, aligned) | 0.490 | 0.490 [0.480–0.499] | 0.504 [0.488–0.515] | the money figure |
| E8 misaligned long | 0.533 | 0.533 [0.532–0.557] | **0.675 [0.674–0.675]** | sleeps mid-domain; live means 0.501 vs 0.446 |
| E8b aligned long (72×5) | 0.538 | 0.538 [0.536–0.542] | — (control is OURS-only) | paired gap vs E8 **+0.002 ≤ δ** |

  **Pinned branch fired: LENGTH-EFFECT.** Sleep/boundary **alignment is a NON-FACTOR for OURS** (+0.002; its retention
  *rises* on longer domains and its live line still never crashes at a switch) — the flat line was never alignment
  luck. What moves is the **opponent**: with ~68 steps per world ER re-converges before every domain-end checkpoint
  (onset crashes still happen — the checkpoint read just no longer catches them) → **the P10.3 relative retention win
  is switch-frequency-scoped** (OURS leads where switches are frequent relative to ER's re-convergence time; on long
  stationary blocks the tuned ER overtakes the checkpoint read).

- **§10 E10 — the REVERSED-LONG stream (round 4; the staircase-mechanism test — E8 layout, order reversed):** the
  committed REV's staircase treads sag because each block holds exactly ONE sleep at its end; E10 puts 2–3 sleeps
  inside each block. **Pinned verdict fired: STALENESS-DISCONFIRMED/PARTIAL** (rescue-jumps > 0 in **5/5** seeds,
  median +0.052; sag-shallower in only **3/5** — banked as fired). The split is the finding: the **rescue is real
  and repeats** (covariate: 0.435→0.296, sleep →0.416, →0.316, sleep →0.405; within-domain floors *rise*: rotated
  0.347→0.368→0.445), and the endpoint **0.527 ≈ the forward-long 0.533** (OURS order-invariant at length too,
  Δ −0.006) — but the sag-shallower cut was **mis-specified** (equal ~24-step inter-sleep segments on both streams
  ⇒ it measures rotation *rate*, not cumulative run-down; estimator lesson logged), so the head-staleness mechanism
  is **supported, not confirmed** — the bulk-level flag stands formally. Free ER read: rev-long final AA **0.580**
  — between its rev-short collapse (0.343) and fwd-long strength (0.675): length partially rescues the hard-first
  curriculum, but **ER stays order-sensitive even at length (Δ −0.095 > δ); OURS is order-invariant at both scales.**

**Verdict:** RETENTION-COMPETITIVE/BETTER (OURS worst-point all-prev 0.490 vs ER 0.350; AAA 0.519 vs 0.433) at
competitive final AA (0.490 vs 0.504, within δ), order-robust / algorithm-energy NOT a win same-substrate (1.47×) /
energy win **substrate-realized** (3.5×). Continual half **supported** (steadier), economics **substrate-realized**.
**§10 E8 scope line (stated on the money figure):** the relative retention win belongs to the **rapid-switch regime**;
alignment is a non-factor (E8b); OURS's own steadiness is order-, alignment-, and length-invariant. **§10 E10:** the
staircase sag = head-frame staleness **supported-not-confirmed** (sleeps rescue, 5/5; the confirming cut was
mis-specified; bulk-level component not excluded — flagged).

---

## P10.4 — the noise showcase on a held-out battery *(environment swept; directional retention)*

*Controls: committed cell, margin-disjoint battery (dir-RMS 2.5 vs P9.4's 1.5, +ADC-3b + nuisance), 5 seeds. Read =
directional retention (acc under channel / clean) — a DIRECTION, the spine.*

| environment | OURS-hardened | BP+replay | naive | holds? · verdict |
| --- | --- | --- | --- | --- |
| clean | 1.000 | 1.000 | 1.000 | reference |
| iid | **1.095 [1.076–1.151]** | 0.608 [0.589–0.693] | 0.720 [0.661–0.773] | OURS ≫ (noise-aug helps) |
| directional | 0.978 [0.969–0.980] | 0.225 [0.150–0.237] | 0.981 [0.978–0.986] | OURS ≫ BP; small residual > δ |
| adc3b | 0.923 [0.923–0.925] | 0.300 [0.215–0.504] | 0.920 [0.739–0.973] | OURS ≫ BP; small residual > δ |
| nuisance | **1.000 [1.000–1.000]** | 0.469 [0.459–0.539] | 0.423 [0.419–0.441] | OURS invariant (layernorm) |

**Verdict:** CONFIRMS P9.4 at new levels — OURS-hardened ≫ BP+replay on **every** held-out channel; a small
directional/ADC residual (0.978 / 0.923, > δ) persists → **named → the analog-realism layer** (Phase-6 arc cashed on
the assembled object, honestly scoped; battery is re-parameterized, not structurally-novel → "confirms," not payoff).
Deterministic (per-env offset, not `hash()`). naive incidentally ties OURS on directional/adc3b (shallow raw-input
classifier) but collapses on nuisance — the load-bearing comparison is vs the fair continual opponent BP+replay.

---

## P10.5 — A5 natural multi-class: the fight a professor recognizes *(learner swept; natural digits→40)*

*Controls: 8×8 digits → shared 40-D bulk input (the same pinned 64→40 projection as the gauntlet), CISTREAM class-IL
(5 tasks × 2 classes), 5 seeds. BWT = worst-pre-sleep every learner (R6). The natural class-IL leg complementing
P10.3's natural domain-IL gauntlet. Figure FIGHT + INV.*

| learner | accuracy | E(analog) | E(digital) | worst-BWT | vs-OURS · verdict |
| --- | --- | --- | --- | --- | --- |
| **ours_g4 (OURS)** | 0.879 [0.878–0.891] | 6.70e7 | 3.46e8 | −0.051 | (ref) · continual, not static |
| **er_strong** | **0.950 [0.937–0.956]** | 3.71e7 | 2.25e8 | −0.019 | beats OURS **+0.071** (> δ, 5/5) |
| er_budget | 0.922 [0.921–0.928] | 1.55e7 | 9.41e7 | −0.242 | beats OURS +0.043 (forgets more) |
| naive | 0.866 [0.860–0.887] | 1.14e7 | 7.59e7 | −0.505 | OURS +0.013 (the floor) |
| joint-BP ceiling | 0.982 [0.974–0.982] | — | — | — | near-saturated (digits easy) |

**Verdict:** LOSS on static natural accuracy — ER-strong beats OURS **+0.071** (> δ, 5/5), and forgets slightly less
(worst-BWT −0.019 vs −0.051). Synthetic *understated* ER's edge (both near-Bayes-hard at ~0.49); digits are easy so
ER's flexible MLP + replay pull ahead. OURS's continual-safety edge (decisive on lifelong P10.1 −0.028 vs −0.272, and
the 5-domain gauntlet P10.3 0.490 vs 0.350) does **not** appear on a short easy CI stream (nothing for the sleep loop
to out-protect). OURS = a continual, not static-accuracy, learner (P4 confirmed). Static gap flagged → a future draft
(convolutional / larger bulk), never a P10 re-run.

---

## P10.6 — the Pareto verdict + the Stage-2 close-out *(integration; the honest win/tie/loss map)*

*Integration rung — reads P10.1's saved arrays + the P10.2–P10.5 verdicts; runs nothing new. Pareto on (final AA ×
analog energy) across the P10.1 roster; the two energy cuts (same-substrate algorithm + chip-vs-conventional total)
restated as the verdict map. The founding bet's economics & accuracy halves banked separately (R4). Figure PARETO + INV.*

| axis | OURS | best fair opponent | w/t/l | number |
| --- | --- | --- | --- | --- |
| final accuracy (continual synthetic home) | 0.494 | ER-strong 0.498 | **tie** | +0.004 (< δ) |
| final accuracy (natural digits, static-ish) | 0.879 | ER-strong 0.950 | **loss** | −0.071 (static trail) |
| worst-pre-sleep BWT (lifelong) | **−0.028** | ER-strong −0.272 | **win** | ≈10× safer |
| worst-point all-prev retention (gauntlet) | **0.490** | ER-strong 0.350 | **win** | +0.140 (AAA 0.519 vs 0.433) |
| noise robustness (held-out, vs BP) | 0.92–1.10 | BP+replay 0.23–0.61 | **win** | every channel |
| energy — algorithm (same digital substrate) | 3.46e8 | ER-strong 2.25e8 | **loss** | 1.54× (the deep bulk) |
| energy — chip vs conventional GD (total) | 6.70e7 (analog) | ER-digital 2.25e8 | **win** | 3.4× (substrate-realized floor) |

- **PARETO** (final AA × analog energy): non-dominated frontier = **{er_strong, gdumb}** — OURS(g4) is **dominated**
  (ER-strong has higher accuracy *and* lower analog energy, being a small tuned net; the same-substrate digital cut also
  has OURS dominated). OURS's genuine wins are on the axes this scatter omits: worst-case safety, noise, the substrate floor.
- **§10 E4+E7 — every measured cadence point on the verdict scatter** (merge guard: exp1 `ours_g4` == exp2 `g4`
  bit-for-bit): {ours_g4 ⭐, g5, g6, g7, g8, g12, g13, g14, g15, g16} draw the model's own cost line — a ~0.49-AA
  plateau sweeping 6.7e7 → 4.0e7 pJ with the g13 wobble (0.474) and the g16 accuracy-cliff outlier (0.458) visible ON
  the money line, so a reader sees exactly which cadence to test next. Frontier membership unchanged — the family
  enriches the picture, it does not move the verdict (and the scatter cannot show the g7+ safety break — that is why
  grid-4 stays the headline).
- **INV**: assembled from the green-guard rungs.

**Verdict:** an honest Pareto close-out. **Economics half = substrate-realized** (the 80/20 algorithm is NOT a
same-substrate energy win against a small tuned ER — 1.54× more; "less energy than modern GD" holds for the *chip*,
3.4× via the analog crossbar floor, R1). **Accuracy half = competitive-on-home / trails-on-static / WINS-on-continual-
safety & noise.** A substrate-native continual learner — exactly the P4 identity. Stage 2 closes. Delta **S14**.

---
