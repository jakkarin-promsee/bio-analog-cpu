# P11.7 — throughput / stream-rate: at what arrival rate does a learner start dropping samples?

**Question.** Strike-3 ("does it scale?"), the real-time half. Derived — not wall-clock (a numpy artifact) — from the
metered FLOPs/sample on the gas stream (the Ghunaim read): at a shared compute budget, the learner with the higher
per-sample cost saturates first and must skip samples. R12 pins: price BOTH learners **same-substrate** (analog a
separate labeled row, never mixed into one side); the demonstration rate = the **geometric mean** of the two
critical rates, fixed by rule. The pre-registered *expected* branch was (iii) the inversion (P10 measured OURS at
MORE FLOPs/sample). Does gas confirm it — or invert it?

**Setup.** OURS-A on gas (one seed) → FLOPs/sample + energy/sample (analog + digital) from the meter; ER-strong
tuned on the disjoint seed-7 gas stream (its accuracy-optimal config: hidden-128, replay-64) → its FLOPs/sample via
`fair_budget_meter`. Critical rate ∝ 1/cost; demo rate = geomean; skip-fraction = 1 − λ_crit/λ_demo. Three
same-substrate rows: raw FLOPs, energy-digital, energy-analog.

**Result — BRANCH (i) THE REGIME WIN on gas (opponent/arena-dependent — it INVERTS P10's synthetic-home inversion).**

| row (same-substrate) | OURS cost/sample | ER cost/sample | ratio | skip @ demo: OURS / ER |
| --- | --- | --- | --- | --- |
| raw FLOPs | 9.28e4 | 2.00e5 | **0.46×** | 0.0% / **32.0%** |
| energy — digital | 1.94e4 | 4.02e4 | 0.48× | 0.0% / 30.6% |
| energy — analog (the chip) | 3.81e3 | 4.53e3 | 0.84× | 0.0% / 8.2% |

- **On gas, OURS is cheaper per sample on every substrate row** → its critical rate is *higher*, so at the
  geometric-mean demo rate the tuned ER drops 8–32% of the stream while OURS keeps up (0%). A real-time regime
  exists where ER visibly degrades and OURS does not — **branch (i), the economy's best real-time sentence, measured
  on nature's drift.**
- **Why this inverts P10 (honest).** P10 measured OURS at *more* FLOPs/sample (96,938 vs 65,268) on the synthetic
  home, where a small cheap ER sufficed → the pre-registered inversion. On **gas**, the ER-strong that *retains* must
  pay for a wide net + replay (hidden-128, replay-64), so the accuracy-competitive opponent is the expensive one here
  and the frozen D40 recipe is comparatively cheap. **The throughput verdict is arena/opponent-dependent:** OURS wins
  it on gas against a retention-tuned ER; it loses it (the inversion) where a cheap ER competes. Both are true and
  both are reported — the map does not claim a universal throughput win.
- **The analog row tightens but does not erase the win** (0.84×): even priced on the crossbar (where OURS's own bulk
  MACs are cheapest, shrinking its relative advantage), OURS still edges the tuned ER, ER skipping 8.2% at the demo
  rate. On the digital substrate the gap is wider (0.48×, ER skips 30.6%).

**Read (8 slots).**
1. *Claim* — on the gas stream, against the retention-tuned ER-strong, the frozen recipe has the higher throughput
   ceiling: a real-time rate exists where ER drops samples and OURS does not. The claim is arena/opponent-scoped, not
   universal (P10's synthetic home inverts it).
2. *Headline* — raw-FLOP ratio 0.46× (ER 2.15× OURS's cost); ER skips 32%/31%/8% at the demo rate across
   FLOP/digital/analog; OURS 0% by lower cost.
3. *Figures* — none (a derivation table; the STREAM demo is the P11.3 gas figure, cross-referenced).
4. *Mechanism* — throughput is 1/cost; the tuned ER buys gas retention with a wide net + replay minibatch every step
   (3× fwd MACs × (batch+replay)/batch), which the frozen D40 bulk + gated closed-form namer undercuts on this
   arena. On the crossbar OURS's own MAC cost drops, shrinking the margin but not flipping it.
5. *Threats* — (i) arena/opponent-dependence (P10 inverts this — stated); (ii) derived from metered FLOPs, not
   wall-clock (by design — numpy timing is not the chip); (iii) one seed for the OURS cache (the FLOPs are
   near-deterministic in the fire/sleep counts); (iv) the demo rate is fixed by the geomean rule, not chosen.
6. *Verdict* — **branch (i) the regime win, gas-scoped** — the economy keeps a real-time sentence on nature's drift,
   with the honest caveat that it is opponent-cost-dependent and inverts where the ER is cheap.
7. *Recipe-honesty* — same-substrate rows never mixed (analog a separate labeled row); demo rate = geomean by rule;
   ER tuned on the disjoint seed-7; nothing tuned in OURS.
8. *Where-it-stands* — the throughput read completes the strike-3 trilogy (accuracy=P11.6, memory=P11.5-crossover,
   real-time=here). The LIMIT-MAP inherits: *on gas the chip out-throughputs the retention-tuned ER on every
   substrate; elsewhere the FLOP inversion holds — the real-time economy is arena-dependent, named as such.*

*Guards: budget-report ✓ (same-substrate rows) · R12 pins (analog separate, geomean demo rate) ✓. Derivation rung.*
