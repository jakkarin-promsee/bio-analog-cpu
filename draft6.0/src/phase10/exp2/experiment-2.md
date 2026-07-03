# P10.2 — The cadence frontier: the frozen object as a 6-point cost-frontier family

**Question.** The kickoff reframe (§0.1): present the frozen object not as a single point but as a **family of
operating points along its one runtime cost dial — the sleep cadence** (`grid-N` = sleep every N segments). Every
*learned* part is frozen; only the sleep interval changes. Where do the grids sit on (accuracy × energy ×
worst-BWT), which Tier-1 cadence is the δ-eligible showcase representative, and where does Tier-2 degrade — measured
against the metered energy this time (P9.5 characterized the accuracy/BWT frontier internally; P10 adds the energy axis
+ the external-scaling framing)? **§10 E2 extension (post-close, author-directed):** the family gains **grid-12** —
never run before, not even in P9.5 — to fill the 8→16 gap the final-AA-vs-energy trend left illegible.

**Setup.** Swept variable = the sleep cadence grid ∈ {4,5,6,8,**12**,16} (the ONLY dial that moves — every learned
weight, head, gate, buffer identical). Controls locked: the frozen object (`59d2720`), the lifelong synthetic home, 5
seeds. Figure CADENCE-FRONTIER + INV. Apparatus `cadence_family_runner` (the `cadence_family_guard` asserts grid-4
bit-exact vs `figs_p9_5_cadence`). Verdict shape pinned BLIND: grid-4 is the committed headline, NEVER swapped; a
Tier-1 *showcase rep* is admitted only if Pareto-non-dominated **AND** worst-BWT within δ of grid-4's (paired) **AND**
energy IQR-disjointly lower. grid-12's read (design §10, expectation-free): veto-fail (g8's axis), AA-drop (g16's
axis), both, or hold. *(§10 re-run: all 35 carried arrays reproduced bit-exactly; only grid-12 is new.)*

**Run.** 6 grids × 2 (DDM + oracle reference) × 5 seeds, replayed on one lifelong cache per seed. Wall ≈ 10 min.

**Result / figures.**
| grid | accuracy | energy (pJ) | worst-BWT | oracle-wBWT | GD-share | nsleep | Pareto/verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **g4 ⭐** | 0.494 [0.478–0.502] | 6.70e7 | **−0.028 [−0.039–−0.022]** | −0.028 | 0.178 | 25 | committed headline (never swapped) |
| g5 | 0.495 [0.483–0.523] | 5.99e7 | −0.039 [−0.050–−0.033] | −0.167 | 0.166 | 20 | **Tier-1 showcase rep** (δ-eligible) |
| g6 | 0.495 [0.483–0.523] | 5.42e7 | −0.087 [−0.093–−0.067] | −0.087 | 0.153 | 16 | Tier-1, fails the δ-BWT gate (−0.087) |
| g8 | 0.494 [0.478–0.502] | 4.85e7 | −0.317 [−0.439–−0.267] | −0.289 | 0.138 | 12 | ⚠ Tier-2 — forgets (veto-fail) |
| g12 (§10) | 0.496 [0.473–0.508] | 4.28e7 | −0.339 [−0.367–−0.333] | −0.461 | 0.119 | 8 | ⚠ Tier-2 — forgets like g8, AA still holds |
| g16 | 0.458 [0.458–0.478] | 3.99e7 | −0.367 [−0.383–−0.367] | −0.540 | 0.107 | 6 | ⚠ Tier-2 — AA drop > δ |

- **CADENCE-FRONTIER**: left — the 6 grids on (energy × accuracy), grid-4 ringed; the frontier runs from grid-4
  (safest, priciest, 6.70e7) to grid-16 (cheapest, unsafe, 3.99e7), monotone in energy with nsleep — and **final AA is
  FLAT all the way down to grid-12 (0.496 at 4.28e7), then cliffs to grid-16 (0.458)**. right — worst-BWT by grid: the
  Tier-1 knee {4,5,6} sits near the 0-line / above the −δ band; Tier-2 {8,12,16} plunges to −0.32/−0.34/−0.37.
- **The §10 grid-12 read (both pinned cuts technically "hold" — and that exposes what they measure):** veto-fail =
  **False** (at grid-12 the committed gate *ties its own same-cadence oracle* — the forgetting is pure cadence
  sparsity, not gate timing; the oracle itself is at −0.461) and AA-drop = **False** (final AA 0.496 ≈ grid-4). But the
  absolute worst-BWT is **−0.339** — grid-8-deep. So the Tier-2 break has **two distinct cliffs**: the **safety cliff
  falls between grid-6 and grid-8** (−0.087 → −0.317) and stays broken through grid-12; the **accuracy cliff falls
  between grid-12 and grid-16** (0.496 → 0.458). The AA-vs-energy trend is not a smooth exponential — it is a plateau
  with a cliff, and grid-12 is the point that makes that legible.
- **INV**: 14 guards green (grid-4 bit-exact vs the frozen slice).

**Read (8 slots).**
1. *Claim* — the frozen object is a legible 6-point cost-frontier: grid-4 the safest headline; grid-5 a δ-eligible
   cheaper showcase representative; grid-6 already exceeds the worst-BWT δ-gate; grid-8/12/16 are the degradation arms —
   and the break has **two cliffs**: safety falls at 6→8, final accuracy only falls at 12→16.
2. *Headline* — grid-4 worst-BWT −0.028 [−0.039–−0.022] at 6.70e7 pJ (the committed knee, bit-exact vs `59d2720`);
   grid-5 −0.039 at 5.99e7 (Tier-1 rep); grid-8 −0.317; **grid-12 AA 0.496 (holds) at worst-BWT −0.339 (broken)**;
   grid-16 AA 0.458 (Tier-2 accuracy cliff). n=5.
3. *Figures* — CADENCE-FRONTIER (accuracy × energy × worst-BWT), INV.
4. *Mechanism* — denser sleep (smaller grid) consolidates more often, so the worst *mid-interval* pre-sleep trough is
   shallower (safer) — but each sleep re-forwards the LUT + re-solves, so energy rises with cadence density (g4 25
   sleeps 6.70e7 → g16 6 sleeps 3.99e7). The GD-share tracks it (0.178 → 0.107, all ≤ 0.25). The Tier-2 break is the
   P9.5 finding, reproduced and now **shaped** (§10): past grid-6 the inter-sleep troughs deepen faster than δ
   (grid-8 −0.317, grid-12 −0.339 — the safety cliff), while the *final* AA is rescued by the last sleep all the way
   down to grid-12 (0.496) and only collapses when sleeps get too sparse to cover the stream at all (grid-16, 6
   sleeps, 0.458 — the accuracy cliff). Worst-case safety degrades a full tier before average accuracy does.
5. *Threats* — (a) behavioral meter (params in manifest); (b) the frontier is internal (the object vs itself) — no ER
   number consulted here, the external race is P10.1/P10.3; the grid-4 arm is asserted bit-exact vs the P9 freeze
   (cadence_family_guard). Rule-1: one variable (cadence).
6. *Decision / verdict* — **grid-4 is the committed headline, never swapped.** The Tier-1 **showcase rep is grid-5**
   (worst-BWT −0.039 within δ of grid-4's −0.028, energy IQR-disjointly lower); **grid-6 fails the δ-BWT gate** (−0.087,
   0.059 worse than grid-4). Tier-2 break confirmed on both axes (grid-8 veto-fail, grid-16 AA drop) — and **grid-12
   (§10) is NOT a viable middle point**: its final AA holds but its worst-case safety is grid-8-broken (−0.339); by the
   literal pinned cuts it "holds" both (its gate ties its own oracle; AA ≈ g4), which shows those cuts measure
   *gate-timing* and *average* accuracy — the absolute worst-BWT is what disqualifies it. The family is a **declared
   cost axis**, not a knob turned to beat the baseline.
7. *Freeze-honesty* — object frozen before the run (grid-4 bit-exact, `59d2720` provenance); the only dial moved is the
   declared cadence cost axis; no learned knob touched; verdict shape pinned BLIND (grid-12's read pinned in design §10
   before its first-ever run; the §10 re-run reproduced all carried arrays bit-exactly).
8. *Where-it-stands* — the cadence cost-frontier is a **supporting decision** for the model scorecard: grid-4 the
   committed headline, grid-5 the cheaper viable point, {8,12,16} the degradation arms with a **two-cliff shape**
   (safety breaks at 6→8; accuracy breaks at 12→16 — worst-case safety degrades a full tier before average accuracy).
   This shapes the sleep-design future (the author's stake) and feeds the P10.3 money figure (grid-4 + grid-5 rep +
   grid-8 + grid-16 lines) and the P10.6 full-family Pareto (§10 E4).
