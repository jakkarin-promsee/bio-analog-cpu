# P10.3 — The multi-domain gauntlet: the money figure

**Question.** Does the frozen object learn a **sequence of ≈5 domains without forgetting**, cheaper than a budgeted
BP+replay, and keep up in real time — the "money figure" the professor brief rests on? Read three curves vs
ER-strong: plasticity (new-domain acc), **worst pre-sleep all-prev retention** (the P9 honest continual read, ER at
the same convention), and cumulative same-substrate energy; plus AAA, throughput/steps-behind, the substrate 2×2, and
a reversed-order control.

**Setup.** Swept: the frozen object at all five grids {4,5,6,8,16} (money-figure lines: grid-4 + the Tier-1 rep
grid-5 + grid-8 + grid-16) vs ER-strong; across 5 **native domain-IL** digit worlds {identity, permuted, rotated,
covariate, noised}, all projected to the shared 40-D bulk input via one pinned seed-frozen 64→40 Gaussian, one shared
10-class head; 5 seeds + a reversed-order control (grid-4 + ER-strong; K9). **Fairness fix (commented in `p10lib`):**
the sleep/replay probe is a balanced **cross-domain** sample — domain-IL requires the replay memory to span domains
(ER's reservoir accumulates cross-domain, so OURS's hippocampus probe must too; a domain-0-only probe made the namer
trivially unable to adapt — a construction artifact, not a learning result). Figures GAUNTLET + **GAUNTLET-STREAM
(§10 E3)** + SUBSTRATE + INV. **§10 E3 extension (post-close, pre-registered):** the per-BATCH stream view — for
OURS(g4) and ER-strong, per batch: **live-batch accuracy** (prequential, pre-update) + **seen-so-far all-domain
accuracy** (post-update) + **exact prefix-priced cumulative energy**. Measurement-only, via the triple-guarded
lockstep replay (`gauntlet_batch_curves`): the SCFF cell pass asserted bit-exact vs the committed cache
(rng-fingerprint + `phi_b` every step), the head states asserted vs the committed `err_trace` every step, the
cumulative-energy endpoint asserted == the committed meter total. All asserts held on all 5 seeds; **all 62 carried
arrays reproduced bit-exactly** on the re-run. **§10 round 3 (E8/E8b — the alignment-break test):** the author caught
that the committed stream's block (24) equals the grid-4 sleep period exactly (every sleep landed on a domain's last
step), so the flat OURS line could be alignment luck. E8 re-runs the forward gauntlet with per-domain blocks pinned
`[68,63,56,57,68]` (drawn once, rng(20260703), non-multiples of 6 — sleeps land MID-domain, switches at drifting sleep
phases; 312 steps); **E8b** is the de-confounding control (block 72 = exactly 3× the sleep period — same length scale,
sleeps back ON the boundaries; OURS only), because E8 changes two things at once (alignment AND length). g4 +
ER-strong, 5 seeds; the replay guards anchor to this run's own cache (the stream is new by construction). **All 86
carried arrays reproduced bit-exactly** on the round-3 re-run.

**Run.** 5 grids × 5 seeds on the gauntlet cache + ER-strong (curves on) + the reversed-order control + the §10
replay; wall ≈ 3.6 min.

**Result / figures.** *(retention = worst pre-sleep all-prev AA per inter-domain interval — R6/K12.)*
| config | final all-prev | **worst all-prev** | AAA | worst-BWT | E(digital) |
| --- | --- | --- | --- | --- | --- |
| **OURS grid-4 ⭐** | 0.490 [0.480–0.499] | **0.490** | **0.519** | −0.012 | 7.40e7 |
| OURS grid-5 (rep) | 0.490 [0.480–0.499] | 0.463 | 0.494 | −0.038 | 6.80e7 |
| OURS grid-8 | 0.487 [0.483–0.491] | 0.464 | 0.505 | −0.036 | 5.59e7 |
| OURS grid-16 | 0.487 [0.483–0.491] | 0.223 | 0.409 | −0.040 | 4.98e7 |
| **ER-strong** | 0.504 [0.488–0.515] | 0.350 | 0.433 | 0.000 | 5.03e7 |

- same-substrate (digital) algorithm cut: OURS grid-4 7.40e7 vs ER-strong 5.03e7 → **1.47× more**.
- substrate total (OURS-analog vs ER-digital): **3.5× cheaper** (the chip vs conventional GD-on-digital).
- reversed-order AA delta (grid-4): **−0.014 [−0.032–+0.018]** → order-robust (< δ).
- throughput/steps-behind: ER rel-complexity 0.71× (ER is FLOPs-lighter); steps-behind 0 (neither throttled).
- **GAUNTLET** (money figure): top panel — worst-pre-sleep all-prev retention across the 5 domains, OURS lines
  (grid-4 always + grid-5 rep + grid-8 + grid-16) vs ER, with sleep-position ticks + domain-boundary markers; OURS
  grid-4 holds a near-flat ~0.49 (worst 0.490) while ER dips to 0.350 mid-stream before recovering to 0.504. Bottom —
  cumulative energy (OURS above ER on digital; the analog line far below). *(§10: the two panels' y-labels shortened —
  they collided in the first render.)* **SUBSTRATE**: the 2×2, OURS-analog ringed, 3.5× under ER-digital. **INV**: 14
  guards green.
- **GAUNTLET-STREAM (§10 E3)** — the batch-resolution mechanism view. **Top:** OURS's seen-so-far line rides
  near-flat ~0.5 across all five worlds while ER's saw-tooths — it **crashes at every domain onset and re-climbs**
  (the thick-line envelope of its every-step replay chasing the newest domain); the live-batch (thin) lines show the
  adaptation dips directly — ER dives to ~0.1 at each onset while OURS's live accuracy barely moves (live-batch mean
  **0.469 vs ER 0.273**). Final seen-so-far converges to the committed final all-prev (0.490 vs 0.504) — the two
  reads agree where they overlap. **Bottom:** the exact per-batch cumulative energy — OURS is a **staircase** (each
  sleep's LUT re-forward + solve is a visible jump, clustering after domain onsets) vs ER's smooth every-step ramp;
  ER's ramp converges toward OURS just before the first sleep, then each sleep staircases OURS back above — OURS
  stays the pricier same-substrate line throughout, exactly the committed 1.47× read, now visible per batch (this
  exact read supersedes the proportional per-domain shape).
- **GAUNTLET-STREAM-REV (§10 E6)** — the same view, domain order **reversed** {noised → identity}, answering the two
  pinned questions + completing K9's ER leg. **(a) ER's low start is real, and it is not just a start:** both
  learners open ~0.1 on the noised block (a hard opener hits both), but ER **never recovers** — its reversed final AA
  collapses to **0.343 [0.336–0.370] vs its forward 0.504 (Δ −0.161, ≫ δ)**: the discriminative net + reservoir get
  shaped by noise early and every later domain is learned on that damaged base (its live-batch stays ~0.1–0.2 even on
  the easy late domains; live mean 0.225). **OURS holds 0.494 vs forward 0.490 (Δ +0.004)** — it climbs
  domain-by-domain to the same endpoint regardless of order (the unsupervised bulk extracts structure even from the
  all-noisy opener — Phase-6's Door-B, now visible live; each onset's sleep re-anchors the namer). **(b) the drop
  follows the NOISE, not the position:** reversed, there is no late-stream collapse — the low region moves to the
  start with the noised domain; noise suppresses the live read *while it is the live world* and drags the seen-so-far
  average *while it is included*, in both orders. **The committed forward gauntlet was ER's favorable ordering; OURS
  is order-invariant** — the asymmetry the single order-delta number (−0.014, OURS only) could not show. **The
  staircase shape (D1):** OURS's reversed line rises in sleep-jumps whose treads *sag* within each block — the
  two-timescale signature, not forgetting: the bulk rotates every batch while the SLDA frame is re-anchored only at
  sleeps, so between sleeps the stale frame reads the old worlds progressively worse and each sleep snaps it back
  (every tread floor higher than the last: 0.17→0.42→0.44→0.46→0.49; endpoint == forward; the live line never sags).
  The committed REV cannot show the *rescue* (block 24 = the sleep period → exactly one sleep per block, at its end)
  — that is E10's job.

**Read (8 slots).**
1. *Claim* — across 5 domains OURS holds **steadier** retention than a budgeted ER (worst-point all-prev 0.490 vs
   0.350; AAA 0.519 vs 0.433) at a competitive final AA (0.490 vs 0.504, within δ), order-robustly; its energy is
   substrate-realized (3.5× via analog), not a same-substrate algorithm win (1.47× more digital).
2. *Headline* — worst pre-sleep all-prev **0.490 (OURS g4) vs 0.350 (ER)**; final 0.490 vs 0.504 (within δ); AAA 0.519
   vs 0.433; same-substrate E 1.47× more; substrate total 3.5× cheaper; reversed-order Δ −0.014 (n=5).
3. *Figures* — GAUNTLET (twin panel + sleep/domain overlay), GAUNTLET-STREAM (§10 — the per-batch live/seen/energy
   view), GAUNTLET-STREAM-REV (§10 E6 — the reversed order), GAUNTLET-STREAM-LONG (§10 E8 — the alignment-break),
   GAUNTLET-STREAM-REVLONG (§10 E10 — the staircase-mechanism test), SUBSTRATE (2×2 re-metered), INV.
4. *Mechanism* — OURS's sleep-consolidation gives a **steady** trajectory (high anytime + high worst-point), while ER's
   every-step replay is more variable (dips to 0.350 mid-stream as it chases the newest domain, then recovers by
   stream-end to a marginally higher final). density ≠ class holds at the buffer: OURS's cross-domain CBRS probe
   re-forwarded at sleep tracks each domain's class directions. The energy: OURS forwards the 12-layer bulk every step
   (1.47× ER's digital energy); only the analog crossbar's near-free MACs make the chip 3.5× cheaper than ER-on-digital
   — the substrate is load-bearing (R1).
5. *Threats to validity* — (a) behavioral meter (params logged); (b) ER tuned + byte/FLOPs-matched (its shape is its
   own race_bp choice, not capped — threat h, so it is FLOPs-lighter); (c) the domain set/order/tuning-asymmetry: OURS
   runs a **frozen** config, ER gets its **own best** per-domain config — the retention edge is *despite* that
   handicap; the reversed-order control is order-robust for OURS (Δ −0.014) — and the §10 E6 completion shows the
   asymmetry: **ER is order-SENSITIVE (reversed final AA 0.343 vs forward 0.504)**, so the forward gauntlet was ER's
   *favorable* ordering, strengthening not weakening the OURS comparison; **the cross-domain probe is mildly
   non-causal (all domains present at t0) — benign: re-forwarding an unseen-domain input through an unadapted bulk
   yields uninformative features, no future-domain knowledge leaks**; (d) single-pass gauntlet → forgetting is milder than the lifelong
   P10.1 stream (where ER's worst-BWT reached −0.272); the per-DOMAIN cumulative-energy curve is a
   proportional-to-steps shape, now **superseded at batch resolution** by the §10 exact prefix-priced stream view
   (endpoint guarded == the committed meter total); **(e — §10 E8) the retention win is switch-frequency-scoped:** on
   long stationary blocks (~68 steps/domain) a tuned ER re-converges before every checkpoint and overtakes the
   checkpoint retention read (0.675 vs 0.533) — the committed gauntlet's short blocks (24) are the rapid-drift regime
   where OURS leads; the E8b control shows the sleep/boundary alignment itself moves nothing (paired gap +0.002);
   **(f — §10 E10) the sag-shallower cut was mis-specified** — equal inter-sleep segment lengths on both streams
   made "shallower" measure rotation rate, not cumulative run-down; the pinned PARTIAL verdict is banked as fired
   and the floor-trend read is reported post-hoc, labeled — a bulk-level decay component is not excluded.
   Rule-1: one variable (grid / learner); the §10 stream views are guarded replays / pre-registered measurement arms,
   never new tuning.
6. *Decision / verdict* — **RETENTION-COMPETITIVE/BETTER** (OURS worst-point all-prev ≥ ER, AAA higher) /
   **algorithm-energy NOT a win** same-substrate (1.47×) / **substrate-realized** (3.5×). The accuracy/continual half
   is **supported** (steadier retention at competitive final AA); the economics half is **substrate-realized**.
   **§10 E8 banks the scope:** LENGTH-EFFECT — the retention win holds in the rapid-switch regime; alignment is a
   non-factor (E8b); on long stationary blocks the tuned ER overtakes the checkpoint read (stated on the money figure,
   not silently absorbed). **§10 E10 banks the staircase mechanism at "supported, not confirmed":** the pinned
   verdict fired PARTIAL (rescue-jumps 5/5, sag-shallower 3/5 — the second cut mis-specified); the sleeps demonstrably
   rescue the sag and order-invariance holds at length (0.527 vs 0.533), but the bulk-level flag stands formally.
7. *Freeze-honesty* — object frozen before the run (grid-4 bit-exact, `59d2720`); only the cadence dial moves; verdict
   shape pinned BLIND; the cross-domain probe changes the replay *source* (domain-IL-appropriate), not the learned
   object; meter = P8 ADC-centred model.
8. *Where-it-stands* — the money figure shows the substrate-native continual learner's real edge: **steady multi-domain
   retention** (higher worst-point + anytime) at a substrate-realized 3.5× energy advantage over conventional GD. The
   honest caveat carried from P10.1 holds: on the same digital substrate against a small tuned ER, OURS's deep bulk
   costs more — the win needs the analog crossbar. The §10 stream views make the *mechanism* visible at batch
   resolution: ER buys its higher final AA with a crash-and-relearn cycle at every domain switch (live-batch mean
   0.273), while OURS's forward-only bulk + sleep loop holds both the live and the remembered read near-flat (0.469)
   — the steadiness IS the product. And the reversed order (E6) shows the steadiness is **curriculum-robust**: swap
   the hard noisy world to the front and ER's whole run collapses (0.343) while OURS lands at the same endpoint
   (0.494) — a lifelong learner cannot choose the order the world arrives in. And the alignment-break round (E8/E8b)
   closes the last suspicion about the flat line: it is not the sleep schedule happening to fit the world — OURS's
   retention is alignment-invariant (paired gap +0.002) and rises on longer domains — while honestly bounding the
   claim: the *relative* win over a tuned ER belongs to the rapid-switch regime; give a plastic learner long
   stationary blocks and it out-converges the checkpoint read (0.675 vs 0.533). The steadiness stays OURS's product
   in every regime (live 0.501 vs 0.446 even there); the *ranking* depends on how fast the world moves.
- **GAUNTLET-STREAM-REVLONG (§10 E10)** — the staircase-mechanism test: the E8 layout verbatim, domain order
  reversed (noised first) — the committed REV could never show a *rescue* (one sleep per block, at its end); this
  stream puts 2–3 sleeps inside every block. **Pinned verdict fired: STALENESS-DISCONFIRMED/PARTIAL** (jump>0 in
  5/5, sag-shallower in only 3/5 — banked as fired). The two cuts split, and the split is informative: **(a) the
  rescue is real and repeats** — every mid-domain sleep jumps seen-so-far back up (median +0.052, 5/5 seeds;
  covariate: falls 0.435→0.296, sleep →0.416, falls →0.316, sleep →0.405), the within-domain floors *rise*
  (rotated 0.347→0.368→0.445; identity 0.469→0.486→0.496), and the endpoint lands at **0.527 ≈ the forward-long
  0.533** (order-invariance holds at length; Δ −0.006) — the saw-tooth oscillates around a rising level instead of
  running down the block. **(b) the "sag-shallower" cut was mis-specified** (an estimator lesson, logged): both
  streams' inter-sleep segments are the *same* ~24 steps (the sleep period), so per-segment depth measures the
  rotation *rate*, which the hypothesis never predicted would change — it predicted the *cumulative* run-down would
  be bounded, which the floor read (post-hoc, labeled) shows. The head-staleness mechanism is supported by every
  read except the mis-specified cut; a bulk-level component is **not excluded by the pinned cut, so the flag
  stands formally**. Free ER read: rev-long final AA **0.580** — between its rev-short collapse (0.343) and its
  fwd-long strength (0.675): length *partially* rescues a hard-first curriculum for the plastic learner, but **ER
  stays order-sensitive even at length (Δ −0.095 > δ) while OURS is order-invariant at both scales**.- **GAUNTLET-STREAM-LONG (§10 E8/E8b)** — the **alignment-break** view, answering "was the flat OURS line alignment
  luck?" **NO — and the control proves it.** On the misaligned long stream (sleeps at steps
  [23,47,67,89,…] vs onsets [0,68,131,187,244] — 2–3 sleeps *inside* every domain, no sleep on a boundary) OURS's
  retention is **unchanged-to-better** (worst-point all-prev **0.533** vs its committed 0.490; final AA 0.533
  [0.532–0.557]), its live line still never crashes at a switch (live-batch mean **0.501**), and the E8b aligned-72
  control lands at the same place: **0.538 vs 0.533, paired gap +0.002 ≤ δ — sleep/boundary alignment is a NON-FACTOR
  for OURS.** What the long stream *does* change is the **opponent**: ER-strong strengthens dramatically when domains
  are long (final AA **0.675** [0.674–0.675] vs its committed 0.504) — with ~68 steps per world it fully re-converges
  before every domain-end checkpoint (its onset crashes are still there, live mean 0.446, but the checkpoint read no
  longer catches them) and its 5-domain reservoir covers this easy digit world. Pinned branch fired: **LENGTH-EFFECT**
  (E8b's rule) — **the P10.3 relative retention win is switch-frequency-scoped**: OURS leads where domain switches are
  frequent relative to the opponent's re-convergence time (the committed gauntlet, the lifelong home); on long
  stationary blocks a tuned plastic learner catches up and overtakes the checkpoint read. OURS's own steadiness is
  order-invariant (E6), alignment-invariant (E8b), and length-stable — the scope line belongs to the *comparison*,
  not the object.