# Phase 11 — The limit map (ROUGH CONCEPT — the pre-research dump, 2026-07-04)

> **Status: 🟠 ROUGH CONCEPT (staging).** This is the *pre-research taste dump* — the honest-science record of what we
> think before the deep-research pass tests it ("did the rough plan cover it all, and is there a better choice?"). It
> will be rewritten in the house design style (the P10 `design.md` pattern) after research + the lab-manager review.
> Banked in git history per the §0.4 habit; do not run anything from this version.
>
> **Lineage:** grew from `temp2/phase10-extend-design.md` (the red-team response concept) + the same-day critique pass
> (folded below as C1–C12) + the author's three kickoff asks (folded as A1–A3). The phase races nothing frozen-open:
> **Arm A measures the P9-frozen object bit-identical; Arm B builds pre-registered scaled instances.** Phase 10 stays
> closed (S14); this is a NEW phase — "the limit map."

---

## 0 · Why this phase exists — the strikes, plus the author's new asks

The red team's three strikes (unanswered by P1–P10):

1. **"Isn't this just SLDA?"** No namer-alone / no-bulk cell exists anywhere in `src/phase10/` (checked). → E0.
2. **"Toy data."** Everything so far is 8×8 digits, 40-D, 10 classes, 1,200 train/domain. → E1/E2/E7.
3. **"Does it scale?"** One width, one depth, one input dim, one class count. → E3/E4.

The author's kickoff asks (2026-07-04):

- **A1 — the per-batch stream view is first-class, everywhere.** Every arena emits the GAUNTLET-STREAM-style
  per-batch figure (live-batch + seen-so-far + sleep ticks + cumulative energy), like
  `phase10/exp3/figs_p10_3/GAUNTLET_STREAM_LONG.png`. The sleep mechanism must be visible "in both bad and good."
- **A2 — the aggressive cross-dataset gauntlet.** Not just same-data + noise/rotation: domain 1 = MNIST, domain 2 =
  Fashion-MNIST, domain 3 = CIFAR-10-gray — *different data types entirely* in one continual stream. "How robust to
  the TYPE of data." → E7. (Research task: the field's "5-Datasets" protocol — pin the canonical cite + the label-space
  convention; our rough call is class-IL, 10 classes per dataset-block, single growing head.)
- **A3 — the famous real-world datasets, so nobody doubts the data again.** Beyond gas + HAR: the streaming-canon
  real-drift tabular sets (Covertype, Electricity — the data-stream community's standard real-world benchmarks) fit
  this box and the chip's sensor story. (Research task: verify canon status + openml IDs + any missed canonical set
  that runs on numpy-CPU, e.g. Wild-Time Yearbook, MedMNIST.)

**Honest goal, unchanged:** we expect to *lose static accuracy by more* as data hardens (P4/P10.5). Under test at scale
are the claims P10 banked: **safety (worst-BWT), retention under switching, order-invariance, noise, the 80/20
economy, the substrate floor.** Where they break, the break gets a name and a figure. The product is the map.

---

## 1 · The two arms (how to scale without breaking the freeze)

- **Arm A — the frozen object through the porthole.** The P9-frozen grid-4 object, bit-identical, judged on harder
  data projected to its native 40-D input (seed-frozen Gaussian projection, the P10.3 discipline). No knob moves.
  Question: *does the frozen recipe survive data it was never shaped on?* (Note: the LUT cap growing with #classes is
  the committed P9.3 *rule*, not a knob move — state this when E7's 30 classes stretch it.)
- **Arm B — the scaling recipe (pre-registered, freeze-then-judge per rung).** Rule written before any run: input dim
  D ∈ {40, 80, 160}; width W = ⌈1.6·D⌉ (the committed 64/40 ratio held); L=12 fixed; LUT cap by the P9.3 rule; every
  other hyperparameter frozen at committed values (InfoNCE τ0.2, w2, σ_aug 1.0, SLDA shrinkage, DDM gate, grid-4).
  Each instance trains on its rung's home stream, freezes, then is judged — a miniature freeze-in-P9/judge-in-P10 per
  rung. A rung that refuses to converge without hand-tuning IS the result (recipe does not transfer — logged, rule 5).

---

## 2 · The experiment ladder (rough)

- **E0 — the decomposition: "is it just SLDA?"** (strike 1, run first, one evening, apparatus exists.) Cells on the
  digits home + P10.3 gauntlet: `proj→namer` (no bulk — the strike), `bulk→namer` (committed, re-used not re-run),
  both `no-sleep` variants, `random-frozen-bulk→namer` (untrained L=12 bulk — the reservoir control, dim-matched).
  Δbulk = (bulk→namer) − (proj→namer) per capability channel. **Budgets REPORTED per cell, not matched** — removing
  the bulk removes its cost by construction; if proj→namer ties at a fraction of the energy the strike lands twice
  (C-fix 9). Pre-registered honest outcome: Δbulk ≈ 0 on the clean easy home is *allowed*; the bulk's earn is expected
  on noise (P6 lives in the bulk) + drift/gauntlet channels.
- **E1 — the dataset-hardness ladder** (strike 2, vision half): r1 MNIST-784 (cached) → r2 Fashion-MNIST (fetch) →
  r3 CIFAR-10-gray (cached). Per rung: (a) the P10.3 5-domain domain-IL gauntlet, same formulas, σ_noise re-pinned to
  0.6× the rung's input RMS; (b) Split class-IL (Split-MNIST 5×2 etc. — `CISTREAM_TASKS` machinery exists); (c) r1
  volume sub-arm: full-MNIST 60k single-pass online (the SLDA regime; watches LUT churn / gate fire-rate / GD-share at
  length). Arms: r1 both (A porthole-40 + B recipe-80); r2–r3 Arm B primary, A the cheap extra. NTR=1200/NTE=500 per
  domain except volume — **NTE raised where the test set allows** (test-side only, training fairness untouched, C-fix 7).
  Name the correspondence out loud: our permuted/rotated domains at r1 ARE the field's Permuted-/Rotated-MNIST (C-fix 6).
- **E2 — the real-world streams (the headline).** Primary: **UCI Gas Sensor Drift** (128-D × 13,910 × 6 gases × 10
  batches over 36 months — drift authored by physics; batches in time order = domain-IL by nature). Secondary: **HAR**
  (561-D × 10,299 × 6 × 30 subjects → stream by subject; the recurring-identity drift axis). **Streaming canon:**
  Covertype (54-D × 581k, stream a slice) + Electricity (8-D × 45k) — time-ordered prequential, the data-stream
  community's standard real-world pair (research: verify + pin protocol). Opponents: ER-strong re-tuned per stream
  (disjoint seed), GDumb, naive-BP, **proj→namer from E0** carried to the real world. Reversed-order runs on gas + HAR.
  **Hygiene pinned (C-fix 4):** scaler fit on batch 1 (or the first time-slice) ONLY, frozen — normalizing over all
  batches leaks the future's drift; class imbalance handled by balanced accuracy (gas batches have wildly different
  mixes — research: verify batch compositions); state what seeds vary when nature fixes the order (init + projection
  only); Vergara et al. 2012 ensemble numbers as the published anchor on the GAS_STREAM figure.
- **E3 — class-count scaling** (strike 3, breadth): committed = MNIST+Fashion joint 20-class class-IL; the analytic
  bytes-vs-C crossover curve (fixed-byte replay dilutes per-class; prototype+Gram grows O(C·D)) drawn from formulas
  with measured points at C=10, 20; CIFAR-100 = stretch only (gray-porthole would be floor — can't measure a crossover
  at floor) (C-fix R1).
- **E4 — capacity scaling: does the economy survive width?** W ∈ {64,128,256} × D ∈ {40,80,160}, one-variable
  discipline, on a rung where the object visibly strains. **The pre-registered shape is DERIVED FROM THE METER FIRST
  (C-fix 3 — the direction catch):** the namer reads the all-tap stack (`p10lib.all_tap_feats`), so its feature dim is
  F ≈ L·W (768 → 3072), and its covariance/sleep-solve cost scales ~O(F²)…O(F³) — *faster in W than the bulk's
  O(L·W²) per step*. The temp2 concept pre-registered "economy improves with scale" from an O(D·C+D²) formula whose D
  is the wrong variable. Before running: derive GD-share-vs-W from the meter formulas at W ∈ {64,128,256}, pin THAT
  shape, and pre-estimate the numpy sleep-solve wall-clock (the compute cliff is itself a finding about the
  architecture's closed-form solve at scale). Also per-width invariants: dead-units, cluster churn, gate fire-rate.
- **E5 — the pretrained-backbone arena (gated, unchanged from temp2).** Off-box feature precompute (ResNet-18 512-D →
  npz); the comparability bridge to published SLDA/RanPAC tables; the bulk-vs-no-bulk cell on top of a supervised
  encoder (a null cleanly scopes the bulk to raw-sensor regimes = the chip story). Dropped without shame if no network
  window; §NON-CLAIMS names it.
- **E6 — stream-rate stress: derivation + one demo (C-fix R2).** The critical stream rate falls out of measured
  per-sample FLOPs (ER at k× cost skips at rate 1/k) — derive per rung from the meter; run ONE demonstration on the
  gas stream. No new skip-harness.
- **E7 — the cross-dataset gauntlet (A2 — the aggressive ask).** One continual stream whose domains are DIFFERENT
  DATASETS: MNIST → Fashion-MNIST → CIFAR-10-gray (order pinned; reversed run committed). Rough call: **class-IL,
  30 classes total, 10 per dataset-block, single growing SLDA head** (the field's 5-Datasets shape — research: pin the
  canonical protocol + citation; a domain-IL shared-label variant is rejected because label semantics across datasets
  would be arbitrary). Per-source seed-frozen projection to the shared input dim, each source normalized to unit RMS
  on its OWN train split only. Both arms. Per-batch stream view mandatory — this is where sleep shows its good and bad.
  Watch: does the namer's Gram stay conditioned as radically different feature statistics arrive? Does the gate fire at
  dataset boundaries? Does CBRS keep all three data types alive in the LUT?

---

## 3 · Instruments (rough)

- **Metrics: unchanged from P10** (final AA, AAA, worst-BWT, gauntlet retention/worst-point, per-batch live accuracy,
  energy same-substrate + chip overlay, GD-share, throughput) **+ Δbulk** (E0, per channel, at every rung it runs).
  **+ the joint-BP ceiling PER RUNG** (C-fix 2) so every map cell reads as fraction-of-ceiling.
- **Figures:** LIMIT_MAP.png (columns = arenas digits→MNIST→Fashion→CIFAR→gas→HAR→covertype/electricity→cross-dataset;
  rows = capability channels; cells = **win / tie / loss / FLOOR** — the 4th state is C-fix 1) · SCALING.png (acc,
  GD-share, substrate factor, Δbulk vs W/D/C/length) · GAS_STREAM.png · DECOMP.png · **STREAM-<arena>.png per-batch
  views everywhere (A1)**.
- **Fairness carried from P10 + new guards:** ER re-tuned per rung on the disjoint seed with the P10.0 protocol +
  **the search grid pinned in the manifest** (C-fix 8); FLOPs+bytes matched per rung; verdict shapes pinned blind;
  gate fire-rate logged as a per-rung invariant (C-fix 5); per-rung noise σ from train data only, frozen.
- **Minimum-done (C-fix 10):** the phase can close honestly after **E0 + E1-r1 + E2-gas** — the map ships on the
  columns that exist; everything else widens it. Kill criteria: E0 Δbulk ≤ 0 on every channel incl. noise+drift →
  stop, re-scope ("what is the bulk for"); E1-r1 porthole safety break → Arm A dead, phase goes Arm-B-only (a finding:
  the frozen recipe is digits-shaped).

---

## 4 · Data acquisition (one network window; box gotchas apply)

| dataset | source | ~size | status | serves |
| --- | --- | --- | --- | --- |
| MNIST-784 | openml 554 | 15 MB | **cached** ✓ (verified on disk) | E1-r1, E3, E7 |
| CIFAR-10 | openml 40927 | 166 MB | **cached** ✓ (verified on disk) | E1-r3, E7 |
| Fashion-MNIST | openml (id: research) | 30 MB | fetch once | E1-r2, E3, E7 |
| Gas Sensor Drift | UCI | 25 MB | fetch once | E2 headline |
| HAR smartphones | UCI | 30 MB | fetch once | E2 |
| Covertype | openml (id: research) | ~70 MB | fetch once | E2 canon |
| Electricity | openml (id: research) | ~5 MB | fetch once | E2 canon |
| CIFAR-100 | openml (id: research) | 150 MB | stretch (E3) | E3 stretch |
| ResNet-18 features | off-box → npz | 200 MB | gated | E5 |

Fallback: UCI direct fetch may hit the box's network flakiness — manual browser download is the fallback path.
Rejected: Speech Commands (2 GB + audio pipeline), raw CORe50/CLEAR (backbone + GBs; E5 carries the spirit),
TinyImageNet (nothing over CIFAR-100 at our scale).

---

## 5 · Open research questions (the deep-research pass answers these before the final spec)

1. The **5-Datasets / cross-dataset protocol**: canonical citation, label-space convention (task-IL vs class-IL),
   dataset order conventions, published numbers at small scale. Is 3 datasets enough or is the canonical set 5?
2. **Covertype / Electricity**: canon status in the streaming community, openml IDs, standard prequential protocol,
   published reference accuracies (Hoeffding trees / ARF / SGD baselines), known pathologies (Electricity's
   autocorrelation critique?).
3. **Gas drift**: published per-batch baselines (Vergara 2012 + follow-ups), the batch class-composition table, the
   standard train/test convention (batch 1 train → rest test? sliding?).
4. **Published ER / SLDA anchors** on Split-MNIST/Split-CIFAR at small buffer sizes — the instrument-validation row
   (C-fix: our ER must reproduce field-strength numbers or the whole map is contestable).
5. Any canonical numpy-CPU-feasible real-world stream we missed: Wild-Time (Yearbook 32×32 gray faces over decades?),
   MedMNIST (28×28 npz medical), CLOC/CGLM (too big?), KMNIST/notMNIST as extra E7 blocks?
6. The **CLEAR citation fix**: temp2 linked CLEAR text to arXiv 2004.03340 (that's CALM) — pin the right CLEAR cite.
7. Fraction-of-ceiling reporting: is there a field convention (normalized accuracy) to cite, or do we define it?
8. E7 conditioning risk: does anything in the SLDA/streaming-LDA literature warn about covariance conditioning under
   multi-dataset feature-statistics shifts (the Gram going stale/ill-conditioned)?

---

*The critique fixes folded above (C1–C12, from the 2026-07-04 pre-design review): 1 floor-guard cell state ·
2 joint-ceiling per rung · 3 E4 shape derived from meter (direction catch) · 4 gas hygiene (batch-1 scaler, balanced
acc, seed semantics, Vergara anchor) · 5 gate fire-rate invariant · 6 Permuted/Rotated-MNIST correspondence named ·
7 NTE raised test-side · 8 ER tuning grid pinned · 9 E0 budgets reported-not-matched · 10 minimum-done line ·
R1 CIFAR-100 → stretch + analytic crossover · R2 E6 derivation-first. Plus: phase lands as `src/phase11/` (P10 stays
closed), landing pack = design.md + result-format.md + CLAUDE.md signpost, professor-pack timing per temp2 §7
(pitch the plan; run E0 pre-pitch).*
