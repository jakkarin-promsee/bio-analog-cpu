# P10.2 — The cadence frontier: the family {4,5,6,8,12,16} + the §10 cliff probes {7,13,14,15}

**Question.** The kickoff reframe (§0.1): present the frozen object not as a single point but as a **family of
operating points along its one runtime cost dial — the sleep cadence** (`grid-N` = sleep every N segments). Every
*learned* part is frozen; only the sleep interval changes. Where do the grids sit on (accuracy × energy ×
worst-BWT), which Tier-1 cadence is the δ-eligible showcase representative, and where does Tier-2 degrade — measured
against the metered energy this time (P9.5 characterized the accuracy/BWT frontier internally; P10 adds the energy axis
+ the external-scaling framing)? **§10 E2 extension (post-close, author-directed):** the family gains **grid-12** —
never run before, not even in P9.5 — to fill the 8→16 gap the final-AA-vs-energy trend left illegible. **§10 E5
(round 2):** cliff probes **{7, 13, 14, 15}** — characterization points, NOT family members (`CAD_FAMILY` + its guard
untouched) — localize the two cliff edges E2 exposed.

**Setup.** Swept variable = the sleep cadence grid ∈ {4,5,6,**7**,8,**12**,**13**,**14**,**15**,16} (the ONLY dial
that moves — every learned weight, head, gate, buffer identical; {7,13,14,15} = §10 E5 probes). Controls locked: the
frozen object (`59d2720`), the lifelong synthetic home, 5 seeds. Figure CADENCE-FRONTIER + INV. Apparatus
`cadence_family_runner` (the `cadence_family_guard` asserts grid-4 bit-exact vs `figs_p9_5_cadence`). Verdict shape
pinned BLIND: grid-4 is the committed headline, NEVER swapped; a Tier-1 *showcase rep* is admitted only if
Pareto-non-dominated **AND** worst-BWT within δ of grid-4's (paired) **AND** energy IQR-disjointly lower. grid-12's
read (design §10, expectation-free): veto-fail (g8's axis), AA-drop (g16's axis), both, or hold. Per-probe read (§10
round 2): which side of each cliff (|wBWT − g4's| ≤ δ = safety holds; AA ≥ g4 − δ = accuracy holds). *(§10 re-runs:
all carried arrays reproduced bit-exactly each round.)*

**Run.** 10 grids × 2 (DDM + oracle reference) × 5 seeds, replayed on one lifelong cache per seed. Wall ≈ 16 min.

**Result / figures.**
| grid | accuracy | energy (pJ) | worst-BWT | oracle-wBWT | GD-share | nsleep | Pareto/verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **g4 ⭐** | 0.494 [0.478–0.502] | 6.70e7 | **−0.028 [−0.039–−0.022]** | −0.028 | 0.178 | 25 | committed headline (never swapped) |
| g5 | 0.495 [0.483–0.523] | 5.99e7 | −0.039 [−0.050–−0.033] | −0.167 | 0.166 | 20 | **Tier-1 showcase rep** (δ-eligible) |
| g6 | 0.495 [0.483–0.523] | 5.42e7 | −0.087 [−0.093–−0.067] | −0.087 | 0.153 | 16 | Tier-1, fails the δ-BWT gate — the safety **edge** |
| g7 (probe) | 0.496 [0.473–0.508] | 5.13e7 | −0.322 [−0.356–−0.278] | −0.350 | 0.146 | 14 | ⚠ the safety **plunge** (already g8-deep) |
| g8 | 0.494 [0.478–0.502] | 4.85e7 | −0.317 [−0.439–−0.267] | −0.289 | 0.138 | 12 | ⚠ Tier-2 — forgets (veto-fail) |
| g12 (§10) | 0.496 [0.473–0.508] | 4.28e7 | −0.339 [−0.367–−0.333] | −0.461 | 0.119 | 8 | ⚠ Tier-2 — forgets like g8, AA still holds |
| g13 (probe) | 0.474 [0.438–0.478] | 4.13e7 | −0.433 [−0.461–−0.400] | −0.447 | 0.113 | 7 | ⚠ AA wobbles to the exact δ boundary |
| g14 (probe) | 0.496 [0.473–0.508] | 4.13e7 | −0.444 [−0.450–−0.328] | −0.533 | 0.113 | 7 | ⚠ AA back on the plateau (timing zone) |
| g15 (probe) | 0.495 [0.483–0.523] | 3.99e7 | −0.428 [−0.444–−0.406] | −0.500 | 0.107 | 6 | ⚠ AA holds at g16's exact energy/nsleep |
| g16 | 0.458 [0.458–0.478] | 3.99e7 | −0.367 [−0.383–−0.367] | −0.540 | 0.107 | 6 | ⚠ Tier-2 — the accuracy **cliff** (AA drop > δ) |

- **CADENCE-FRONTIER**: left — the 10 grids on (energy × accuracy), grid-4 ringed; the frontier runs from grid-4
  (safest, priciest, 6.70e7) to g15/g16 (cheapest, unsafe, 3.99e7), monotone in energy with nsleep — and **final AA is
  a PLATEAU (0.494–0.496) all the way down to grid-15, with the g13 wobble (0.474) and the single cliff at 15→16
  (0.458)**. right — worst-BWT by grid: the Tier-1 knee {4,5} near the 0-line, g6 at the δ-edge (−0.087), then
  **everything from g7 rightward plunged** (−0.32 … −0.44).
- **The §10 cliff localization (E2 + E5):** the Tier-2 break has **two distinct cliffs, now with edges.** The
  **safety axis breaks in two steps**: the δ-edge at grid-6 (−0.087) and the **plunge at grid-7** (−0.322 — already
  grid-8-deep; between nsleep 16 and 14 the mid-interval troughs outrun the sleeps). The **accuracy axis plateaus
  through grid-15** and cliffs **exactly at 15→16** (0.495 → 0.458). The sharpest mechanism read: **g15 and g16 share
  the SAME energy (3.99e7) and SAME sleep count (6) yet differ 0.495 vs 0.458** — at ~6 sleeps the outcome stops being
  count-limited and becomes **sleep-TIMING-sensitive** (whether the sparse consolidations happen to cover the revisit
  structure; the g13 wobble at nsleep 7 — 0.474, exactly the δ boundary — is the same zone's signature). grid-12's
  pinned cuts both read "hold" (its gate ties its own same-cadence oracle at −0.461 — pure sparsity, not gate timing);
  the absolute worst-BWT (−0.339) is what disqualifies it.
- **INV**: 14 guards green (grid-4 bit-exact vs the frozen slice).

**Read (8 slots).**
1. *Claim* — the frozen object is a legible cost-frontier with **two localized cliffs**: grid-4 the safest headline;
   grid-5 the δ-eligible rep; the safety axis breaks at the grid-6 δ-edge and **plunges at grid-7**; the accuracy axis
   plateaus through grid-15 and cliffs **exactly at 15→16**, where the outcome turns sleep-timing-sensitive.
2. *Headline* — grid-4 worst-BWT −0.028 [−0.039–−0.022] at 6.70e7 pJ (the committed knee, bit-exact vs `59d2720`);
   grid-5 −0.039 at 5.99e7 (Tier-1 rep); **grid-7 −0.322 (the safety plunge)**; grid-12 AA 0.496 at worst-BWT −0.339;
   **grid-15 AA 0.495 vs grid-16 0.458 at identical energy/nsleep** (the timing-sensitive accuracy cliff). n=5.
3. *Figures* — CADENCE-FRONTIER (accuracy × energy × worst-BWT, 10 points), INV.
4. *Mechanism* — denser sleep (smaller grid) consolidates more often, so the worst *mid-interval* pre-sleep trough is
   shallower (safer) — but each sleep re-forwards the LUT + re-solves, so energy rises with cadence density (g4 25
   sleeps 6.70e7 → g16 6 sleeps 3.99e7). The GD-share tracks it (0.178 → 0.107, all ≤ 0.25). The two cliffs have two
   mechanisms: the **safety plunge at g7** (nsleep 16→14) is where mid-interval troughs outrun the consolidations —
   worst-case damage accrues between sleeps and δ-deep troughs appear as soon as the interval stretches past ~14
   sleeps/stream; the **accuracy cliff at 15→16** is NOT a count effect — g15 and g16 both sleep 6 times at the same
   energy, and only the *positions* differ (grid-16's phase misses the revisit structure that grid-15's happens to
   cover). At the plateau's edge the loop is one unlucky sleep-phase away from the cliff — the g13 wobble (0.474,
   exactly δ-boundary, nsleep 7) is the same zone's signature. Worst-case safety degrades a full tier before average
   accuracy does.
5. *Threats* — (a) behavioral meter (params in manifest); (b) the frontier is internal (the object vs itself) — no ER
   number consulted here, the external race is P10.1/P10.3; the grid-4 arm is asserted bit-exact vs the P9 freeze
   (cadence_family_guard). Rule-1: one variable (cadence).
6. *Decision / verdict* — **grid-4 is the committed headline, never swapped.** The Tier-1 **showcase rep is grid-5**
   (worst-BWT −0.039 within δ of grid-4's −0.028, energy IQR-disjointly lower); **grid-6 fails the δ-BWT gate** (−0.087,
   0.059 worse than grid-4). Tier-2 break confirmed on both axes — and **no probe is a viable middle point**: g7 and
   everything sparser is safety-broken (−0.32 … −0.44); the g13–g15 plateau holds *average* accuracy while sitting in
   the timing-sensitive zone one sleep-phase from the cliff. grid-12's literal pinned cuts both "hold" (its gate ties
   its own oracle; AA ≈ g4), which shows those cuts measure *gate-timing* and *average* accuracy — the absolute
   worst-BWT is what disqualifies it. The family is a **declared cost axis** + probes, not a knob turned to beat the
   baseline.
7. *Freeze-honesty* — object frozen before the run (grid-4 bit-exact, `59d2720` provenance); the only dial moved is the
   declared cadence cost axis; no learned knob touched; verdict shape pinned BLIND (grid-12's and the probes' reads
   pinned in design §10 before their first-ever runs; the §10 re-runs reproduced all carried arrays bit-exactly).
8. *Where-it-stands* — the cadence cost-frontier is a **supporting decision** for the model scorecard: grid-4 the
   committed headline, grid-5 the cheaper viable point, and a **fully localized two-cliff degradation map**: the
   safety plunge at **6→7** (worst-case damage outruns consolidation), the accuracy cliff at **15→16** (count-equal,
   timing-sensitive — the loop is one sleep-phase from collapse at the plateau's edge). Worst-case safety degrades a
   full tier before average accuracy. This shapes the sleep-design future (the author's stake) and feeds the P10.3
   money figure and the P10.6 all-grid Pareto (§10 E4+E7).
