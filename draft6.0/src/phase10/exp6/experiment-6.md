# P10.6 — The Pareto verdict + the Stage-2 close-out

**Question.** Assemble the (accuracy × energy) frontier across the OURS-family + the BP+replay field, state where OURS
wins / ties / loses (each with its number + mechanism), and bank the founding bet's **economics** and **accuracy**
halves **separately** (§7/R4). Not a scalar — the honest map.

**Setup.** Integration rung — reads P10.1's saved arrays (+ the P10.2–P10.5 verdicts); runs nothing new. The Pareto is
on (final AA × analog energy) across {ours_g4, er_strong, er_budget, agem, derpp, gdumb, naive}; the two energy cuts
(same-substrate algorithm + chip-vs-conventional total) restated as the verdict map. Figure PARETO + INV.

**Result / figures.**

*The verdict map:*
| axis | OURS | best-field | w/t/l | number |
| --- | --- | --- | --- | --- |
| accuracy (vs ER-strong, continual home) | 0.494 | 0.498 | tie | gap +0.004 (< δ) |
| accuracy (natural digits, P10.5) | 0.879 | 0.950 | loss | −0.071 (static trail) |
| worst-BWT / retention (P10.1/P10.3) | −0.028 / 0.490 | −0.272 / 0.350 | **win** | ≈10× safer / +0.140 |
| noise (held-out, vs BP, P10.4) | 0.92–1.10 | 0.23–0.61 | **win** | every channel |
| energy — algorithm (same digital) | 3.46e8 | ER 2.25e8 | loss | 1.54× |
| energy — total (chip vs GD-digital) | 6.70e7 (analog) | 2.25e8 | win | 3.4× (substrate-realized floor) |

- **PARETO** (verdict figure): on (accuracy × analog energy) the non-dominated frontier is **{er_strong, gdumb}** —
  OURS(grid-4) is **dominated** (er_strong has higher accuracy *and* lower analog energy, being a small tuned net).
  OURS's genuine wins are on the axes this scatter omits (worst-case safety, noise, the substrate floor).
- **INV**: assembled from the green-guard rungs.

**Read (8 slots).**
1. *Claim* — the honest close-out: OURS is a competitive, decisively **safer**, and far more **noise-robust** continual
   learner whose energy edge over conventional GD is **substrate-realized**; on a same-substrate (accuracy × energy)
   Pareto a small tuned ER dominates it. A substrate-native continual learner, not a static-accuracy/energy winner.
2. *Headline* — Pareto frontier {er_strong, gdumb}; OURS dominated on acc×energy; **economics half = substrate-only**
   (algorithm 1.54× same-substrate, total 3.4× analog-floor); **accuracy half = competitive-on-home / trails-on-static
   / wins-on-safety** (the automated P10.6 read says "validated" from P10.1's synthetic tie; the honest close-out
   integrates P10.5's natural −0.071 and re-labels it as above).
3. *Figures* — PARETO (the frontier + the hero's dominated position), INV.
4. *Mechanism* — a small tuned ER is cheaper *and* higher-accuracy on the same substrate because OURS pays for a
   12-layer unsupervised bulk every step; that bulk is affordable only on the analog crossbar (near-free MACs), which
   is the whole "why analog." OURS's off-Pareto wins come from the sleep-consolidated loop (steady worst-case
   retention) and the noise-augmented + layernorm + proto-reanchor stack (noise survival) — capabilities the acc×energy
   Pareto does not axis.
5. *Threats* — (a) the Pareto is on analog energy (OURS's native deployment); the same-substrate digital cut (the
   contestable one) also has OURS dominated — reported; (b) GDumb sits on the frontier but is cost-pathological
   (retrains at eval — annotated, not an energy competitor); (c) the automated accuracy verdict uses P10.1 only — the
   written close-out integrates all rungs (P10.5 natural). Rule-1: n/a (integration).
6. *Decision / verdict* — bank the two halves separately: **economics = substrate-realized** (validated as a chip claim,
   not an algorithm claim); **accuracy = competitive-on-continual-home, trails-on-static, wins-on-continual-safety.**
   The neocortex brain (cheap unsupervised structure + a gradient-free continual-safe namer + a metered economy + a
   frozen lifelong loop) is **done**; Stage 2 closes.
7. *Freeze-honesty* — the object was frozen before P10 (grid-4 bit-exact, `59d2720`); every verdict shape was pinned
   BLIND; the only dial moved was the declared cadence cost axis; the meter is behavioral (ADC-centred, NOT SPICE).
8. *Where-it-stands* — Stage 2 (the GD namer) is complete and validated honestly: a substrate-native continual learner,
   safest and most noise-robust of the fair field, with a substrate-realized energy advantage over conventional GD, and
   a named residual + a static-accuracy gap flagged to future work. The founding bet is refined, not inflated.
