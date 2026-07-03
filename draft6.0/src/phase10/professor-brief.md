# The two-brain analog neurocompute chip — a one-page brief (Phase-10 close-out)

*Extends the P8.7 "why analog" brief with the Phase-10 validation. Behavioral (ADC-centred) energy model, NOT SPICE;
numbers are relative-pJ, 5 seeds, median. The object was frozen before any baseline number was seen.*

## The object, in one paragraph
Two brains on one analog substrate. A cheap, unsupervised **SCFF** front (self-contrastive forward-forward: local,
label-free, forward-only, ~80% of the metered compute) organizes the world for free; a small **gradient-free namer**
(streaming SLDA) maps its features to labels (~20%). Both run **live**: SCFF learns forward-only on every input, the
namer tracks the representation drift via a **drift-triggered gate** and periodic **sleep consolidation** over a
prototype memory. Weights are resident analog charge; there is no backward pass leaving the chip. The whole loop was
**frozen** at the end of Phase 9; Phase 10 raced it — untouched — against a tuned, budget-matched **experience-replay**
backprop learner (the strong fair baseline).

## The founding bet, banked as two halves (honestly, separately)
> **Bet:** *"an 80/20 forward-only continual learner that beats backprop's economics **and** accuracy."*

- **Accuracy — competitive on the continual home; a static-accuracy trail; a continual-stability WIN.** On the hard
  continual home OURS ties the tuned replay learner (0.494 vs 0.498); on easy recognizable digits it trails (0.879 vs
  0.950). But on the honest worst-case continual read it is the **safest of the whole field** — it forgets ~**10×
  less** at its worst point (BWT −0.028 vs −0.272; worst-point retention 0.490 vs 0.350 across 5 domains, with higher
  anytime accuracy). *OURS is a continual learner, not a static-accuracy machine — as designed.*
- **Economics — the chip wins; the algorithm alone does not.** On the **same digital substrate**, OURS's deep
  unsupervised bulk costs **1.5× more** than a small tuned replay net — the 80/20 algorithm alone does not win the
  energy race against an efficient discriminative net. The **chip (analog crossbar) is 3.4–3.5× cheaper** than that
  same GD model on a conventional digital accelerator. *"Less energy than modern GD" holds for the chip, and the win
  is the substrate.*
- **Noise robustness — a clean win.** Under a held-out analog-noise battery, OURS holds 0.92–1.10 retention on every
  channel while the replay learner collapses to 0.23–0.61; it is invariant to a layernorm-removable covariate (1.000)
  and *improves* under iid noise (1.095, from noise-augmented training). A small directional/ADC residual remains,
  named to the device-physics (SPICE/PVT) layer.

## The two honesty lines a reviewer will test first
1. **The analog energy factor is a meter-structural floor, not a measured Joule** — the crossbar prices in-memory MACs
   near-zero *by construction of the behavioral model*; the contestable, load-bearing energy cut is **same-substrate**
   (`E(OURS-digital)` vs `E(ER-digital)`), and there OURS is *not* cheaper than a small tuned net (its win is the
   substrate). We report this plainly; we do not rest the headline on the analog number.
2. **The accuracy claim is continual, not static** — a tuned budget replay learner matches OURS on the continual home
   and beats it on static natural data; OURS's measured edge is worst-case **retention/stability** + **noise
   survival**, on a substrate that makes a deep unsupervised backbone affordable. That is the contribution.

## The four figures
- **GAUNTLET** (`exp3/figs_p10_3/GAUNTLET.png`) — 5 domains learned with steady retention (worst-point 0.490 vs 0.350)
  at substrate-realized lower energy; sleep-position + domain markers overlaid.
- **GAUNTLET-STREAM** (`exp3/figs_p10_3/GAUNTLET_STREAM.png` + `_REV.png`) — the same race at **batch resolution**:
  the replay learner crashes to ~0.1 accuracy at every domain switch and re-climbs (a saw-tooth), while OURS holds
  ~0.5 flat (live-batch mean 0.469 vs 0.273); the energy panel shows OURS's sleep staircase vs the replay learner's
  every-step ramp. **The reversed-order twin is the sharpest single comparison:** put the hard noisy world FIRST and
  the replay learner never recovers (final 0.343 vs its forward 0.504) while OURS lands at the same endpoint either
  way (0.494 vs 0.490) — a lifelong learner does not get to choose the order the world arrives in.
- **PARETO** (`exp6/figs_p10_6/PARETO.png`) — the (accuracy × energy) frontier: a small tuned ER dominates on
  same-substrate acc×energy; OURS's wins are the axes it omits (safety, noise, substrate). Every measured cadence
  point is drawn as the model's own cost line (a ~0.49-AA plateau from 6.7e7 down to 4.0e7 pJ, its accuracy cliff
  visible on the line).
- **SUBSTRATE** (`exp3/figs_p10_3/SUBSTRATE.png`) — the 2×2 {OURS,GD}×{analog,digital}: the chip 3.5× under
  conventional GD-on-digital, decomposed into substrate × algorithm.

*Full verdict: [`README.md`](README.md); numbers: [`RESULTS.md`](RESULTS.md); the why-analog decomposition:
[`../phase8/README.md`](../phase8/README.md) §P8.7.*
