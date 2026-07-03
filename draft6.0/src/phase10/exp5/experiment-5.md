# P10.5 — A5 natural multi-class: the fight a professor recognizes

**Question.** Synthetic overstates gaps both ways (threat d). Does the P10.1 synthetic verdict (OURS ties a tuned ER)
hold on **recognizable natural data** — 8×8 digits projected to the shared 40-D bulk, class-incremental — and in which
direction did synthetic distort the gap? The honest confirm.

**Setup.** Learner ∈ {ours_g4, er_strong, er_budget, naive} + the joint-BP ceiling, on digits→40 (the same pinned
64→40 projection as the gauntlet), CISTREAM (5 tasks of 2 classes), 5 seeds. Controls as P10.1. BWT = worst-pre-sleep
for every learner (R6). Figure FIGHT + INV. The gauntlet (P10.3) is already natural domain-IL digits; this adds the
**class-IL** natural leg.

**Run.** 4 learners × 5 seeds on digits→40 lifelong caches; wall ≈ 4.7 min.

**Result / figures.**
| learner | accuracy | E(analog) | E(digital) | worst-BWT |
| --- | --- | --- | --- | --- |
| ours_g4 (OURS) | 0.879 [0.878–0.891] | 6.70e7 | 3.46e8 | −0.051 |
| **er_strong** | **0.950 [0.937–0.956]** | 3.71e7 | 2.25e8 | −0.019 |
| er_budget | 0.922 [0.921–0.928] | 1.55e7 | 9.41e7 | −0.242 |
| naive | 0.866 [0.860–0.887] | 1.14e7 | 7.59e7 | −0.505 |
| joint-BP ceiling | 0.982 [0.974–0.982] | — | — | — |

- **FIGHT**: on natural digits ER-strong **beats OURS by +0.071** (0.950 vs 0.879) and forgets slightly less
  (worst-BWT −0.019 vs −0.051); OURS beats naive (0.879 vs 0.866) and trails ER-budget (0.922). The joint ceiling (0.982)
  is near-saturated (digits are easy).
- **INV**: 14 guards green.

**Read (8 slots).**
1. *Claim* — on recognizable natural data a *tuned budget ER out-accuracies OURS* (+0.071); OURS is **not a
   static-accuracy competitor** (P4, confirmed). The synthetic home *understated* ER's edge — because synthetic is
   near-Bayes-hard for both, both sat at ~0.49; digits are easy, so ER's MLP capacity + replay pull ahead.
2. *Headline* — OURS 0.879 [0.878–0.891] vs ER-strong 0.950 [0.937–0.956], gap **+0.071** (> δ, ER wins 5/5) (n=5);
   joint ceiling 0.982.
3. *Figures* — FIGHT (accuracy + energy, ceiling overlaid), INV.
4. *Mechanism* — on a **short, easy** class-IL digit stream, replay is enough for ER to both learn well (a flexible MLP
   fits the 10-class boundary to 0.95) *and* not forget (worst-BWT −0.019 — the stream is too short for catastrophic
   drift). OURS's SLDA-on-SCFF-features is unimodal-per-class and reads a frozen unsupervised backbone (0.879). **OURS's
   continual-safety edge (decisive on the lifelong P10.1 stream, −0.028 vs −0.272, and the 5-domain gauntlet P10.3,
   0.490 vs 0.350) does NOT appear here** — because a short easy stream does not stress forgetting, so there is nothing
   for the sleep loop to out-protect. OURS's advantage is *lifelong/multi-domain stability*, not short-CI accuracy.
5. *Threats to validity* — (a) behavioral meter; (b) ER tuned + byte/FLOPs-matched (its small net is FLOPs-lighter →
   cheaper same-substrate too); (d) **this is the honest direction of the synthetic-overstatement threat: natural data
   *reveals* ER's static-accuracy edge that the hard synthetic home masked** — reported plainly; (e) digits→40 is one
   natural anchor (CIFAR-flat→40 would be the harder one — deferred, the bulk has no composable depth on CIFAR per P5).
   Rule-1: one variable (learner).
6. *Decision / verdict* — **natural CONFIRMS and sharpens P10.1: a tuned budget ER beats OURS on static natural
   accuracy (+0.071).** The founding bet's "beats backprop accuracy" is **not supported** on final/static accuracy;
   OURS's accuracy value is **continual stability on hard/long streams**, not static/short-CI accuracy — exactly the P4
   identity. Banked into the close-out accuracy half.
7. *Freeze-honesty* — object frozen before the run (grid-4); the only dial is the cadence axis (fixed g4); verdict
   shape pinned BLIND; meter = P8 model.
8. *Where-it-stands* — the recognizable-data confirm anchors the honest close-out: OURS is a substrate-native
   *continual* learner (wins lifelong stability + noise), **not** a static-accuracy competitor — a tuned ER wins static
   accuracy, and (on the same substrate) energy. The static-accuracy gap is flagged to a future draft (a convolutional /
   larger bulk), not a P10 re-run.
