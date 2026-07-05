# P11.6 — capacity scaling: does the economy/substrate/safety survive scale while accuracy does what it does?

**Question.** Strike-3 ("does it scale?"), the economy half. On the Fashion (r2) long-regime gauntlet, sweep width
W ∈ {64,128,256} at fixed D=80 (a capacity ablation) and input dim D ∈ {40,80,160} at recipe-W. Four reads
(design §2.4-P11.6): (1) **accuracy vs W** — does capacity buy the porthole gap back, or is the wall objective-shaped
(P5: temperature not size)? (2) **GD-share vs W against the bench-pinned meter-derived shape** ({0.21,0.34,0.53}
from P11.0 — the pre-registered test: whatever the formula predicted, the measurement confirms or breaks it). (3) the
**substrate factor vs W** (E(OURS-digital)/E(OURS-analog), the P8.7 crossbar advantage re-metered — non-decreasing is
the chip's best sentence). (4) **safety (worst-BWT) per width.**

**Setup.** OURS on the Fashion long gauntlet, 3 seeds (W256 declared heavy at bench). The W-sweep breaks the recipe's
W=⌈1.6·D⌉ rule on purpose (a one-variable capacity ablation, stated — not an Arm-B instance); the D-sweep IS the
recipe stretched. NOTHING tuned. Substrate factor = same op-counts priced analog vs digital.

**Result — the economy/substrate/safety ALL survive scale; the pinned GD-share shape is CONFIRMED.**

| sweep | cell | Fdim | accuracy | worst-BWT | GD-share (meas) | pinned | substrate× |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W @ D80 | W64 | 768 | 0.424 | −0.025 | 0.173 | 0.21 | 5.39 |
| W @ D80 | W128 | 1536 | 0.473 | −0.057 | 0.278 | 0.34 | 6.89 |
| W @ D80 | W256 | 3072 | 0.502 | −0.061 | 0.450 | 0.53 | 7.25 |
| D @ recipe-W | D40/W64 | 768 | 0.390 | −0.030 | 0.175 | — | 5.20 |
| D @ recipe-W | D80/W128 | 1536 | 0.473 | −0.057 | 0.278 | — | 6.89 |
| D @ recipe-W | D160/W256 | 3072 | **0.510** | **−0.033** | 0.445 | — | **7.37** |

- **GD-share RISES with W — the pinned shape confirmed.** Measured [0.173, 0.278, 0.450] tracks the bench-pinned
  meter-derived [0.21, 0.341, 0.531] (same rising trend; measured sits slightly below because the actual gated
  fire/sleep counts are lower than the fractions the pin assumed — the SHAPE is what was pinned, and it holds). **The
  economy does NOT improve with scale**: the SLDA solve term ~O((L·W)³) makes the namer a growing fraction of the
  metered energy as the object widens. The P11.0 pre-registration (refuting the temp2 "economy improves with scale"
  guess) is confirmed at the run, not just the formula.
- **Capacity BUYS the accuracy gap back** (0.424→0.473→0.502 over W; 0.390→0.510 over D) — width and input dim both
  lift gauntlet accuracy (+0.078 / +0.120). So the porthole accuracy gap is **partly capacity-limited, not purely
  objective-shaped** — a nuance on P5's "temp not size" (there the SCFF *depth* lever was temperature; here scaling
  the whole bulk+namer feature dim does help), but the lift is modest and comes at a **rising GD-share cost**: the
  accuracy↔economy tradeoff is real at scale, and the map records both.
- **The analog substrate advantage GROWS** (5.39→7.25× over W; up to 7.37× at D160) — **non-decreasing, the chip's
  best sentence**: as the bulk widens, the near-free crossbar MACs multiply faster than the ADC/solve overhead, so
  the compute-in-memory advantage over a digital accelerator *increases* with scale. Better to know this way round.
- **Safety holds at every width and dim** (worst-BWT −0.025 to −0.061; the largest instance D160/W256 is −0.033,
  *safer* than the mid cells) — the grid-4 cadence keeps continual safety across the scaling range; no width breaks it.

**Read (8 slots).**
1. *Claim* — the founding economy/substrate/safety properties survive scale: GD-share rises as the meter predicted,
   the analog advantage grows, safety holds; capacity buys some accuracy back at a rising economy cost.
2. *Headline* — GD-share measured [0.17,0.28,0.45] vs pinned [0.21,0.34,0.53] (shape CONFIRMED); substrate× 5.4→7.4;
   accuracy 0.42→0.51; worst-BWT ≤ −0.061 throughout.
3. *Figures* — `SCALING.png` (GD-share measured-vs-pinned · accuracy vs W & D · substrate factor vs W).
4. *Mechanism* — the namer reads the all-tap stack (Fdim = L·W), so its solve cost ~O((L·W)³) climbs faster than the
   crossbar's linear MAC growth → GD-share rises. The crossbar prices those extra MACs near-free, so the analog/
   digital ratio *widens*. Safety is cadence-bound (grid-4), independent of width, so it rides flat.
5. *Threats* — (i) the W-sweep breaks the recipe W-rule on purpose (capacity ablation, stated); (ii) measured
   GD-share sits below pinned because actual fire/sleep counts < the pinned fractions (the shape, not the level, was
   the pre-registration); (iii) 3 seeds (W256/D160 declared heavy); (iv) Fashion-only (the r2 arena) — the shape is
   architecture-driven (the meter), so it generalizes, but the accuracy levels are arena-specific.
6. *Verdict* — **scaling SURVIVED**: shape CONFIRMED, substrate NON-DECREASING, safety GREEN; capacity buys the gap
   back at a rising economy cost (both banked).
7. *Recipe-honesty* — the D-sweep is the recipe stretched (recipe-W); the W-sweep is a labeled capacity ablation;
   the substrate factor is same-op-count analog-vs-digital (never mixed); the pinned shape was fixed at bench before
   this run; nothing tuned.
8. *Where-it-stands* — the SCALING panel of the phase: the economy/substrate/safety story is **not a small-scale
   artifact**. The LIMIT-MAP inherits "the chip holds at scale" as a banked scaling read; the honest counterweight
   is the rising GD-share (the namer solve is the thing that scales worst, named for the analog layer).

*Guards: recipe (D-sweep) ✓ · budget-report ✓ · pinned-shape overlay ✓ (bench-derived, pre-run). n=3 (declared heavy).*
