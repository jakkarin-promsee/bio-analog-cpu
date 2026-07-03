# Phase 10 — the validation / showcase: race the frozen object (signpost)

You're in **Phase 10** of draft 6.0's **Stage 2** (the GD namer) — **✅ COMPLETE (ran 2026-07-03, P10.0→P10.6, all 14
guards bit-exact; grid-4 reproduced bit-for-bit vs the P9 freeze).** The **fourth and LAST** Stage-2 phase (P7 readout ·
P8 economy+cost · P9 maintenance/close+freeze · **P10 validate/showcase**). Phase 9 locked the two-brain object; **Phase 10
raced it — untouched — against a fair, budgeted, tuned BP+replay baseline** across the continual gauntlet. It *measured*;
it tuned nothing (the only dial moved was the declared cadence cost axis). Discipline: **freeze in P9, judge in P10.** The
verdict shapes were pinned **BLIND** in `design.md` §2.3 before any baseline number was seen. **+ §10 post-close
extension (same evening, author-directed; pre-registered in design §10, measurement-only, every carried array
bit-exact):** grid-12 in the family (the Tier-2 break = a two-cliff plateau), grid-5 in the fight, the per-batch
**GAUNTLET-STREAM** view, the full-family Pareto money line.

- **Verdict — an honest Pareto close-out; the founding bet REFINED, not inflated (banked as two halves, R4):** OURS is a
  **substrate-native continual learner** — competitive on the continual home, decisively **safer**, far more
  **noise-robust**, its energy edge over conventional GD **substrate-realized** — exactly the P4 identity, now tested
  against the strongest fair opponent and *refined* rather than overclaimed.
- **P10.0 — bench + 6 new guards (no verdict, a build).** 14/14 green; grid-4 **bit-exact** vs the P9 freeze
  (`freeze_content` = manifest + reproduction; `59d2720` a provenance label). ER-strong tuned on the **disjoint seed 7**,
  byte-matched to OURS's LUT; full roster real code (A-GEM grad-handle, DER++ logit distillation, GDumb from-scratch
  retrain; descope=False). **Pre-registered tension:** OURS uses *more* FLOPs/sample than ER (96 938 vs 65 268) → the
  same-substrate energy cut is genuinely contestable (R1).
- **P10.1 — the existential fight (grid-4 vs tuned ER + field, continual home).** Accuracy **TIE** (0.494 vs 0.498, OURS
  3/5 seeds, within δ); **continual-safety WIN** — worst-pre-sleep BWT **−0.028 vs −0.272** (≈10× less forgetting, the
  honest read the final-BWT masked). Same-substrate energy 1.54× more (the deep bulk); chip-vs-conventional-GD total 3.35×
  cheaper (substrate-realized). AAA favors ER (0.503 vs 0.392 — the sleep-cadence anytime tax). Joint-BP ceiling 0.870.
  §10: **ours_g5** drawn beside the headline (0.495, worst-BWT −0.039, −11% energy — the family's cheaper viable point;
  the verdict stays grid-4's).
- **P10.2 — the cadence frontier (the 6-grid cost-frontier family; +grid-12 by the §10 post-close extension).** grid-4
  the **committed headline** (never swapped, bit-exact); **grid-5 = the Tier-1 showcase rep** (worst-BWT −0.039 within δ
  of grid-4, cheaper); grid-6 **fails** the δ-BWT gate (−0.087); Tier-2 {8,12,16} break confirmed on **both** axes — with
  a **two-cliff shape** (§10): the *safety* cliff falls at 6→8 (−0.087 → −0.317; grid-12 still broken at −0.339) while
  *final AA* stays flat down to grid-12 (0.496 at 4.28e7) and only cliffs at 12→16 (0.458) — worst-case safety degrades a
  full tier before average accuracy. Energy monotone with cadence density (6.70e7 → 3.99e7); GD-share 0.178 → 0.107 (all
  ≤ 0.25). A declared cost axis, not a knob.
- **P10.3 — the multi-domain gauntlet (the money figure).** 5 native domain-IL digit worlds (identity/permuted/rotated/
  covariate/noised → shared 40-D, shared head, cross-domain replay probe = domain-IL-fair). OURS worst-point all-prev
  retention **0.490 vs ER 0.350**, AAA **0.519 vs 0.433** (steadier anytime) at competitive final AA (0.490 vs 0.504,
  within δ), **order-robust** (reversed-order AA Δ −0.014). Same-substrate 1.47× more; substrate total 3.5× cheaper.
  §10 **GAUNTLET-STREAM** (per-batch, triple-guarded replay): ER **saw-tooths** — crashes to ~0.1 at every domain onset
  and re-climbs (live-batch mean 0.273) — while OURS rides near-flat (0.469); energy at batch resolution = OURS sleep
  staircase vs ER ramp (the 1.47×, exact).
- **P10.4 — the noise showcase (held-out, margin-disjoint battery).** OURS-hardened **≫ BP+replay on EVERY channel** (iid
  1.095 vs 0.608, directional 0.978 vs 0.225, adc3b 0.923 vs 0.300, nuisance 1.000 vs 0.469). A small directional/ADC
  residual (0.978 / 0.923, > δ) → **named → the analog-realism layer**; the battery is re-parameterized not
  structurally-novel → "**confirms** P9.4," honestly downgraded from "payoff." Read is a **direction** (retention), the spine.
- **P10.5 — A5 natural multi-class (digits→40, the recognizable confirm).** ER-strong **beats OURS +0.071** (0.950 vs
  0.879) on static natural accuracy — synthetic *understated* ER's edge (both near-Bayes-hard at ~0.49); OURS's
  continual-safety edge does **not** appear on a short easy CI stream. OURS = continual, not static-accuracy (P4 confirmed).
- **P10.6 — the Pareto verdict + the close-out.** On (final AA × analog energy) the non-dominated frontier is
  **{er_strong, gdumb}** — OURS(g4) is **dominated** (a small tuned ER is cheaper *and* higher-accuracy same-substrate).
  OURS's genuine wins live on the axes the Pareto omits: **safety, noise, the substrate floor.** Two halves banked
  **separately:** economics = substrate-realized; accuracy = competitive-on-home / trails-on-static / wins-on-safety.
  §10: the **full OURS family** {ours_g4 ⭐, ours_g5, g6, g8, g12, g16} drawn as the money line (~0.49 AA sweeping
  6.7e7→4.3e7 pJ; merge guard exp1-g4 == exp2-g4 bit-exact); frontier membership unchanged.
- **Two things the sims sharpened (the honest close-out):** the energy win is **substrate-realized, not algorithmic**
  (R1 measured — a small tuned ER is cheaper same-substrate; the analog crossbar is the whole "why analog"); and OURS's
  accuracy value is **continual stability on hard/long/multi-domain streams**, invisible on short easy static data (P10.5).
- **The disciplines that make it honest:** freeze in P9 / judge in P10 (object locked before any baseline number existed);
  the load-bearing energy cut is **same-substrate** (`E(OURS-digital)` vs `E(ER-digital)`), the analog factor a
  meter-structural floor, never the contestable claim; every noise read is a **direction**, never a magnitude. The meter
  is **behavioral** (relative-pJ, ADC-centred, NOT SPICE).
- **The front door (read this first):** [`README.md`](README.md). **Deep story + every figure:**
  [`phase10-report.md`](phase10-report.md). **The professor pack:** [`professor-brief.md`](professor-brief.md).
  **Numbers:** [`RESULTS.md`](RESULTS.md). **Per-rung:** [`expK/experiment-K.md`](exp0/experiment-0.md). **Spec:**
  [`design.md`](design.md); contract [`result-format.md`](result-format.md). **Apparatus:** `p10lib.py` (+ `p10cfg.py`,
  `p10run.py`, `plot_p10.py`); the frozen object it races: [`../phase9/README.md`](../phase9/README.md).
- **Owed deltas (flagged, banked to [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) as S14):** the founding
  bet's economics & accuracy halves banked separately; the cadence cost-frontier `{4,5,6,8,16}` (grid-4 headline, no swap);
  the characterized SCFF:Namer ratio; the Phase-6 noise arc cashed + the residual named → the analog layer; the **Stage-2
  close-out** (the neocortex brain is done). The Stage-2 report is rewritten from "living" → closed: [`../stage2-report.md`](../stage2-report.md).
- **Read-budget:** for the verdict read `README.md`; for numbers `RESULTS.md`. Open cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 9 — freeze](../phase9/README.md) · next →
  the Stage-2 close-out ([`../stage2-report.md`](../stage2-report.md)) → the analog-realism (SPICE/PVT) layer, and beyond
  the numbered phases, the recurrent lifelong brain (the north star).
