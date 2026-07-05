# P11.5 — the hardness ladder r2/r3 + the class-count crossover: how far down the map, and where does replay dilute?

**Question.** Two reads. **(A) r2/r3 rungs** — take the P11.2 gauntlet protocol (long regime, the E8 primary, both
arms) to **Fashion** (r2) and **CIFAR-gray** (r3): does the bet still hold as the data hardens, and where does the
FLOOR criterion draw the far edge? **(B) the class-count crossover** — a fixed-byte replay buffer dilutes per-class as
O(1/C); the prototype+Gram namer (SLDA) does not. Report the memory-bytes crossover + the **measured** worst-point
retention at C=10 (Split-MNIST) and C=20 (MNIST+Fashion 20-way). NOTHING tuned; ER re-tuned per arm on seed-7.

**Result — Fashion holds the safety bet; CIFAR-gray is the honest FLOOR; the retention crossover is real by C=20.**

### (A) The hardness ladder

| rung | arm | OURS AA | ER AA | OURS worst-BWT | ER worst-BWT | OURS ret | ER ret | ceiling | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **r2 Fashion** | A (D40) | 0.382 | 0.507 | **−0.021** | −0.146 | 0.354 | 0.483 | 0.655 | BET HOLDS (safety) |
| r2 Fashion | B (D80) | 0.454 | 0.530 | **−0.057** | −0.141 | **0.401** | 0.380 | 0.655 | BET HOLDS (safety) |
| **r3 CIFAR-gray** | A/B | 0.123/0.127 | 0.107/0.098 | −0.017/−0.019 | −0.10 | 0.11 | 0.10 | **0.199** | **FLOOR** |

- **r2 Fashion — the safety bet HOLDS, static AA trails (continual-not-static, again).** OURS wins continual safety
  decisively (worst-BWT −0.021/−0.057 vs ER −0.146/−0.141, ≈2–7× less forgetting) while ER leads absolute accuracy
  (0.507/0.530 vs 0.382/0.454) — the P4/P10.5 identity on a harder recognizable dataset. Retention is arm-dependent:
  ER out-retains Arm A in absolute terms (0.483 vs 0.354, ER's capacity), but **Arm B recovers and wins retention**
  (0.401 vs 0.380) — the scaling recipe buying the retention edge back, as in P11.2/P11.4.
- **r3 CIFAR-gray — FLOOR, honestly.** The joint-BP ceiling is only **0.199** (≈2× the 0.1 chance) — grayscale,
  center-cropped CIFAR through a 40-D porthole is at the resolution floor, so the accuracy cell is grey and every
  channel is uninformative (a "safety win" at chance accuracy is trivial — nothing to forget). The far edge of the
  map is all-FLOOR, and that is the honest far edge, not a parity claim.

### (B) The class-count crossover

- **Measured retention — the crossover is real and lands by C=20:** worst-point retention C=10 OURS 0.354 vs ER
  **0.423** (ER leads −0.069) → C=20 OURS **0.233** vs ER **0.014** (OURS leads **+0.219**). At 20 classes the
  byte-matched replay buffer has **diluted to ≈0 retention** while OURS's prototype+Gram namer holds — the design's
  dilution prediction, empirically confirmed: **the prototype+Gram namer does not dilute per-class; a fixed replay
  buffer does.**
- **Analytic memory bytes — the honest counterweight:** for the committed **all-tap** namer (feature dim F = L·W =
  768) the tied F×F covariance is a large *fixed* memory cost (≈590k floats), so on pure bytes the growing-k replay
  buffer stays smaller until C ≈ 766 (no crossover in the realistic C range). So the namer's win is **retention
  fidelity per class**, not raw byte compactness — an honest split: *the prototype+Gram namer buys per-class
  retention that replay cannot, at the cost of a large fixed covariance footprint.*

**Read (8 slots).**
1. *Claim* — the safety bet holds down to Fashion (harder recognizable data); CIFAR-gray is a resolution FLOOR; and
   the prototype+Gram namer's per-class retention overtakes byte-matched replay by C=20 as the buffer dilutes.
2. *Headline* — Fashion worst-BWT −0.021/−0.057 (OURS) vs −0.146/−0.141 (ER); CIFAR ceiling 0.199 → FLOOR;
   retention crossover C10 (ER +0.069) → C20 (OURS +0.219, ER retention 0.014).
3. *Figures* — `CROSSOVER.png` (analytic bytes-vs-C + measured retention C=10/20); the gauntlet fights per rung.
4. *Mechanism* — Fashion: the closed-form namer never catastrophically forgets (safety), but a 40-D porthole on a
   harder dataset caps absolute AA (capacity, recovered by Arm B). Crossover: a fixed-byte replay buffer splits its
   budget across C classes → O(1/C) samples/class → retention collapses at C=20; the prototype+Gram namer keeps an
   exact per-class mean + a shared covariance → per-class fidelity is C-independent.
5. *Threats* — (i) projection loss dominates absolute AA (Arm B bounds it); (ii) CIFAR-gray's FLOOR is a
   native-resolution floor, not purely a CL failure; (iii) the memory-bytes crossover is framing-dependent (F=768
   all-tap vs a D=40 hypothetical namer would cross at C≈38) — the *retention* crossover is the empirical read;
   (iv) r3 3 seeds (declared).
6. *Verdict* — r2 **BET HOLDS (safety)**; r3 **FLOOR**; crossover **real by C=20** (retention), with the honest
   fixed-covariance memory caveat.
7. *Recipe-honesty* — Arm A bit-equal committed; Arm B recipe-guard clean; ER re-tuned per arm on seed-7; FLOOR by
   the joint-BP ceiling (a reference line, never raced); nothing tuned.
8. *Where-it-stands* — the LIMIT-MAP gains a **Fashion** column (accuracy loss / safety win) and a **CIFAR-gray**
   FLOOR column (the honest far edge); the crossover banks: *at high class counts the gradient-free namer out-retains
   byte-matched replay because it does not dilute per-class* — a scaling argument for the whole two-brain memory design.

*Guards: recipe A/B ✓ · floor-criterion ✓ (joint-BP ceiling) · budget-report ✓. n=5 (r3 3, declared heavy).*
