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
`substrate_identity`) green every rung; grid-4 reproduced bit-for-bit against the P9 freeze.

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
economics **substrate-realized**.

---
