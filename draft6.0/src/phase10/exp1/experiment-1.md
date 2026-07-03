# P10.1 — The existential fight: does OURS beat a budgeted experience replay?

**Question.** Every continual *accuracy* win to date (Phase 1/4/8) was measured against naive online-BP — a strawman.
Does the frozen object (grid-4) match/beat a **budgeted, tuned experience replay** (Prabhu CVPR'23: ER is strong under
a matched FLOPs+bytes budget) on **accuracy**, and at what **same-substrate energy** — win, honest-Pareto, or
dominated? The load-bearing rung.

**Setup.** Swept variable = learner ∈ {ours_g4, er_strong, er_budget, agem, derpp, gdumb, naive} + the offline
**joint-BP ceiling** (non-raced dashed reference). *(§10 E1 note: an ours_g5 roster point was added, then **withdrawn**
by the author in round 2 — the rendered gap was within noise, so the extra bar added confusion, not information;
grid-5's numbers stay banked in P10.2 and on the P10.6 family line. The withdrawal re-run reproduced the committed
arrays IDENTICALLY — every key, bit-for-bit.)* Controls locked: the frozen object (`59d2720`, grid-4), the
lifelong synthetic home (the class-IL leg — K13; `make_lifelong_stream`, n_steps 536), ER-strong = the P10.0
seed-7-tuned config ([40,49,49,49,10], lr 1e-3, replay 64, buffer byte-matched to OURS's LUT), the same per-op energy
table (analog + digital), seeds [42,137,271,314,1729]. Figures FIGHT + PARETO + INV. **Verdict shape pinned BLIND**
(design §2.3); the two founding-bet halves banked separately (§7/R4). Inheriting the bench-green apparatus + the
byte-matched racer from P10.0.

**Run.** 7 learners × 5 seeds on the shared stream (OURS on the SCFF cache, BP on the bit-identical raw-input stream);
GDumb retrains from scratch at every eval. Wall ≈ 7.2 min.

**Result / figures.** *(BWT column = worst-pre-sleep, the P9 honest continual read — R6, applied to every learner.)*
| learner | accuracy | E(analog) | E(digital) | worst-BWT | AAA | vs-OURS |
| --- | --- | --- | --- | --- | --- | --- |
| **ours_g4 (OURS)** | **0.494 [0.478–0.502]** | 6.70e7 | 3.46e8 | **−0.028** | 0.392 | (ref) |
| er_strong | 0.498 [0.490–0.501] | 3.71e7 | 2.25e8 | −0.272 | 0.503 | +0.004 acc (tie); 10× worse worst-BWT |
| er_budget | 0.376 [0.375–0.380] | 1.55e7 | 9.41e7 | −0.807 | 0.461 | OURS +0.118 acc |
| agem | 0.320 [0.320–0.333] | 3.40e7 | 2.26e8 | −0.900 | 0.445 | OURS +0.174 acc |
| derpp | 0.360 [0.358–0.365] | 5.67e7 | 3.76e8 | −0.178 | 0.455 | OURS +0.134 acc |
| gdumb | 0.430 [0.427–0.447] | 1.14e7 | 7.59e7 | −0.344 | 0.568 | OURS +0.064 acc (cost-pathological) |
| naive | 0.308 [0.297–0.317] | 1.14e7 | 7.59e7 | −0.880 | 0.434 | the forgetting floor |
| joint-BP ceiling | 0.870 [0.870–0.882] | — | — | — | — | the summit reference (offline) |

- **FIGHT** (headline): OURS ties ER-strong on final AA (0.494 vs 0.498, gap +0.004 < δ, OURS wins 3/5 seeds → within
  noise) and beats ER-budget / A-GEM / DER++ / naive; the joint ceiling (0.87) shows the synthetic home is far from
  saturated. **On worst-pre-sleep BWT, OURS (−0.028) forgets ~10× less than tuned ER-strong (−0.272).**
- **PARETO**: on (accuracy × analog-energy), the frontier membership is {er_strong, gdumb} — OURS(g4) is
  accuracy-competitive but not frontier on this axis pair; its wins are the off-Pareto axes (worst-case safety,
  noise). ER-strong's cheaper analog energy comes with the −0.272 worst-BWT. The family's cheaper cadence points
  live on the P10.6 full-family scatter, not in this fight.
- **INV**: 14 guards green.

**Read (8 slots).**
1. *Claim* — against a budgeted, tuned ER, OURS is **accuracy-competitive** (ties within δ) and **decisively safer**
   (worst-pre-sleep BWT −0.028 vs −0.272); its energy advantage over conventional GD is **substrate-realized** (the
   analog crossbar), not a same-substrate algorithm win against a *small* tuned net.
2. *Headline* — OURS 0.494 [0.478–0.502] vs ER-strong 0.498 [0.490–0.501] (tie, within δ, n=5); worst-BWT −0.028 vs
   −0.272; same-substrate digital E(OURS) 3.46e8 vs E(ER) 2.25e8 = **1.54× more** (deep bulk); OURS-analog 6.70e7 =
   **3.35× cheaper** than ER-on-digital. Joint ceiling 0.870.
3. *Figures* — FIGHT (accuracy + energy bars, ceiling overlaid), PARETO (frontier, hero ringed), INV.
4. *Mechanism* — the accuracy tie: on this short synthetic home ER's replay recovers by stream-end (final-BWT even
   positive), so it matches OURS on final AA — but its **worst mid-stream point** dips to −0.272 as it chases the
   recency-skewed stream, while OURS's sleep-consolidated loop holds the worst point at −0.028 (the P8 "firing more
   forgets more" crux, seen from the opponent's side). The energy: OURS forwards a 12-layer unsupervised bulk every
   step (96 938 FLOPs/sample vs ER's 65 268), so on a **digital** substrate OURS costs 1.54× more; the analog crossbar
   prices those bulk MACs near-zero, which is the *only* reason the chip beats conventional GD-on-digital (R1, exactly
   as pre-registered). AAA (anytime-average) favors ER (0.503 vs 0.392) — the sleep-cadence tax: OURS consolidates
   periodically, so its between-sleep anytime accuracy trails ER's every-step replay. The honest trade is **anytime
   throughput (ER) vs worst-case safety (OURS).**
5. *Threats to validity* — (a) behavioral meter (params in the manifest); (b) ER **is** tuned (seed 7, disjoint) +
   byte/FLOPs-matched — both ER-budget and ER-strong reported, so the win is not vacuous; **(h) parameter asymmetry is
   real and load-bearing: OURS's bulk is ~7× ER's weights**, which is *why* the same-substrate energy cut goes against
   OURS — reported, not hidden; (d) synthetic overstates static gaps → P10.5 natural confirm. Rule-1: one variable
   (learner); the object is frozen.
6. *Decision / verdict* — **ACCURACY-COMPETITIVE / algorithm-energy NOT a win / continual-safety WIN.** The
   *accuracy* half of the founding bet is **supported** (competitive tie with a tuned budget ER, decisive worst-point
   safety edge); the *economics* half is **substrate-realized** (chip 3.35× cheaper than GD-on-digital) but **not an
   algorithm win** on the same substrate against a small tuned ER. Banked separately. The continual-safety edge is the
   claim to press on the gauntlet (P10.3), where forgetting bites harder.
7. *Freeze-honesty* — the object was frozen before the run (freeze-content guard: manifest + grid-4 bit-exact;
   `59d2720` provenance, not a git ==); the verdict shape was pinned BLIND; the only dial moved was the cadence axis
   (here fixed at grid-4). Meter = P8 ADC-centred behavioral model.
8. *Where-it-stands* — the 80/20 continual bet: **accuracy competitive + worst-case-safest of the field**; the money
   story is honest — the chip's ~3.35× energy edge over modern GD is the **analog substrate** (meter-structural floor),
   not the algorithm alone; against a *small* tuned ER on a shared digital substrate, OURS's deep bulk costs more. This
   is the R1 outcome, measured and banked — the "why analog" is now *load-bearing*, not incidental.
