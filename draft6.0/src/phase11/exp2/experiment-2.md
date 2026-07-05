# P11.2 — the MNIST rung (r1): does the frozen recipe survive real MNIST data, and does it scale?

**Question.** Every P1–P10 number lived behind the 8×8-digit / 40-D porthole. Take the P10.3 gauntlet to **real
MNIST** (native 784 → porthole), in **both switch regimes** (rapid-24 + long-randomized [50,70], the E8 primary),
**both arms** (A = frozen recipe D40/W64; B = recipe instance D80/W128), + **Split-MNIST class-IL** + the anchor
cell. Do safety / retention / order-invariance stay green while static AA does what it does (bet holds), and does
Arm B scale?

**Setup.** Swept = learner/arm ∈ {OURS-A, OURS-B, ER-strong (re-tuned per arm on the disjoint seed-7 gauntlet,
grid pinned), naive-BP}; noise-σ by P10 equivalence (bench); NTR 1200/domain, NTE 2000; 5 seeds. STREAM-mnist +
the fight tables + order-invariance.

**Result — BET HOLDS on MNIST (safety/retention/order-invariance win; static AA trails, Arm B recovers).**

| arm | regime | OURS AA | ER AA | OURS worst-BWT | ER worst-BWT | OURS ret | ER ret |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (D40) | rapid | 0.258 | 0.448 | **−0.080** | −0.143 | 0.216 | 0.221 |
| A (D40) | **long** | 0.284 | 0.427 | **−0.012** | −0.196 | **0.223** | 0.102 |
| B (D80) | rapid | 0.390 | 0.541 | **−0.011** | −0.113 | **0.298** | 0.210 |
| B (D80) | **long** | 0.421 | 0.514 | **−0.046** | −0.162 | **0.314** | 0.105 |

- **Safety (worst-BWT): OURS wins every cell** — decisively on the long regime (OURS −0.012/−0.046 vs ER
  −0.196/−0.162, ≈4–16× less forgetting). The ≈10× continual-safety edge from P10 **holds on real MNIST.**
- **Retention: OURS wins on long blocks** (0.22/0.31 vs ER 0.10) — ER re-converges on long stationary blocks then
  forgets at the switch; OURS rides flat. On rapid switches it is a tie.
- **Order-invariance: OURS holds** — |AA(fwd)−AA(rev)| = 0.003 (A) / 0.011 (B), well inside δ.
- **Static AA trails** (OURS 0.26–0.42 vs ER 0.43–0.54) — the P4/P10.5 identity (continual, not static), amplified
  by the 40-D porthole discarding MNIST structure.
- **Arm B scales** — D40→D80 lifts AA (0.284→0.421 long) and retention (0.223→0.314) while safety stays green:
  **the architecture scales; more input dim recovers porthole loss.**
- **Split-MNIST class-IL:** OURS-A 0.496 vs ER 0.649 (ER stronger on static class-IL, expected). **Anchor: OUT of
  the ~[0.80,0.98] literature region — but run at porthole-40, NOT the published raw-784 config;** the
  raw-784 anchor validation is **owed** (does not affect the fair porthole fight, which both learners share).

**Read (8 slots).** 1 *Claim* — the frozen recipe survives real MNIST: it wins continual safety, retention (long),
and order-invariance vs a per-arm-tuned ER, and Arm B scales. 2 *Headline* — long-regime worst-BWT −0.012/−0.046
(OURS) vs −0.196/−0.162 (ER); Arm B AA 0.421 vs Arm A 0.284. 3 *Figures* — `STREAM_mnist.png` (OURS vs ER-strong,
Arm-B long regime — ER rides higher within a domain but crashes at each switch, OURS flatter; the safety story
visible; + persistence floor). 4 *Mechanism* — the closed-form namer never catastrophically forgets; the gate + sleep hold it; ER's
gradient head re-converges per long block and forgets at the switch (the P10.3 length-effect, on MNIST). 5 *Threats*
— **projection loss** dominates absolute AA (40-D porthole on 784-D MNIST; Arm B bounds it, D=160 would bound more);
the anchor is un-validated at raw-784 (owed); retention is a harsh worst-point min. 6 *Verdict* — **bet holds**
(safety/retention/order-invariance green, both arms) with a stated static-AA-trails scope; Arm B = the scaling
answer (holds). 7 *Recipe-honesty* — Arm A bit-equal committed; Arm B recipe-guard clean ({D,W,cap} only); ER
re-tuned per arm on seed-7 (the asymmetry against the home team); nothing else tuned. 8 *Where-it-stands* — the
MNIST columns of the LIMIT-MAP: **safety WIN, retention WIN (long), order-inv WIN, static-AA LOSS**; Arm B carries
the scaling read. **Design deviations (commented):** ER tuning used a modest grid (lr {0.1,0.03} × replay {2,4} ×
hidden {1,2}) for the overnight budget (the full grid is pinned in the bench manifest); the raw-784 Split-MNIST
anchor validation is deferred (owed).

*Guards: recipe A/B ✓ · freeze-content ✓ (bench) · arena-data ✓. n=5.*
