# Synthesis — replay selection / eviction & consolidation schedule beyond CBRS + grid-4  (Tier 2 · t2.3)

**The question:** for our bounded-LUT + closed-form-sleep loop, what **selection or scheduling** mechanism is cheaper or safer than **CBRS + grid-4** while staying substrate-friendly — a bounded store, closed-form re-fit, **no gradient replay through the bulk**? Rank by (safety/efficiency benefit × substrate-fit).

**Already in `draft6.0/research/`:** the maintenance-and-replay curation (`papers/phase9/maintenance-and-replay.md`) covers ER (Rolnick), EWC, SI, A-GEM, MGSER-SAM, REMIND, **CBRS** (Chrysakis & Moens — our committed eviction), balanced-softmax, and Davari drift. Tier-1 already carded SIESTA / on-device (t1.3) and dual-memory *architectures* (t1.4). This card set goes **broader/newer on the selection + schedule MECHANISM** only, and does not re-card those.

## The landscape (the camps)

**Camp A — gradient-space selection (the "ideal", off-substrate).** GSS (Aljundi 2019), OCS (Yoon 2022), and GCR (Tiwari 2022) all say the *right* thing to store is the small weighted subset whose **per-sample gradients** best span / match the gradient of all seen data. GCR states it most cleanly (coreset gradient ≈ full-data gradient); OCS adds a past-task **affinity** term; GSS maximizes gradient **diversity**. All three beat reservoir most **at small buffers and on imbalanced streams** — exactly our regime. All three require a **backward pass per candidate** → structurally forbidden on our substrate. They are our **diagnostic ceiling**, not deployables: CBRS is the free label-count proxy for GSS's gradient-diversity goal.

**Camp B — gradient-free selection (substrate-legal).** Herding (iCaRL 2017) keeps the class-**mean**-matching samples — the policy P9.3 already raced and found **tied** with CBRS (our "buffer-spine null"). GRASP (Harun 2024) ranks by **prototype distance** (easy→hard curriculum) with no gradients. InfoRS (Sun 2022) scores by **surprise + learnability**, computed **closed-form** via Bayesian rank-one updates. These need only means, distances, and a running precision — things a prototype/ridge namer already holds.

**Camp C — consolidation schedule / the stability-gap lens.** De Lange 2023 names the **stability gap** (the per-iteration old-task dip right after a switch) and the **min-ACC** metric to measure it. Harun 2023 (SGM) *overcomes* it and shows the payoff is **safer AND ~16.7× fewer updates** — and critically, two of its four fixes (**class-mean output init**, **freeze old-class outputs**) are things our closed-form prototype namer already *is*. The schedule lesson: remove the onset shock and you can consolidate **less often**.

## How WE differ  ← the money section

Our loop is the **degenerate-but-substrate-perfect** corner of all three camps. We keep a bounded store (CBRS), and consolidation is a **closed-form batch re-fit** over the whole LUT — not iterative gradient replay. That single fact reshapes every idea here:

- Against **Camp A**: we *want* their objective (a buffer that spans class directions / stands in for all past data) but cannot pay their currency (per-sample gradients). CBRS is our free proxy; GSS/GCR are the ceiling we measure against, never deploy.
- Against **Camp B**: because our re-fit is a **batch solve, it is order-invariant** — GRASP's *replay curriculum* buys us nothing as ordering. Herding we already tied. The live opening is to convert these from *retrieval/ordering* signals into **eviction/retention weights**.
- Against **Camp C**: we appear to get the stability-gap fix **for free** — prototype init = class-mean output init (SGM move 1), closed-form namer = frozen old-class outputs (SGM move 4). If so, our **grid-4 may be conservative** *because* we already dodge the onset shock, and a sparser/adaptive cadence could match its safety at lower cost.

The honest placement: CBRS + grid-4 is defensible and cheap, but **three independent papers (GSS, OCS, GCR) + InfoRS all converge on one point — uniform-within-class retention is information-blind and wastes capacity at tight caps** — which is exactly where P11 found the C=20 crossover. That is our real gap.

## The gap / what we haven't tried  (ranked by benefit × substrate-fit)

1. **Information-weighted eviction reusing the drift-gate's error signal** *(top lever)*. Within each CBRS class slot, evict the *least* surprising (most redundant) samples; keep the informative ones — InfoRS's surprise+learnability, computed **closed-form** from the namer's own precision (Mahalanobis / leverage), which is *the same error-EMA our DDM gate already computes and discards*. **Substrate-fit: maximal** — no gradients, no raw-data-gradient, no extra pass; bounded store + closed-form re-fit unchanged. **Benefit:** directly attacks the C=20 retention crossover (more effective history per slot). Respects no-gradient-replay. ✅
2. **Switch-triggered adaptive consolidation density** (Camp C schedule). Consolidate **densely at a genuinely new class / domain switch, sparsely in stationary blocks**, instead of fixed grid-4 — the gate signal to trigger it already exists (P8 error-EMA), and P10 §10 already saw "mid-domain sleeps rescue the REV staircase." **Substrate-fit: high** (reuses the gate; no gradients). **Benefit:** cheaper on average at equal or better worst-point safety. Respects no-gradient-replay. ✅
3. **Prototype-spread eviction (GRASP signal → retention)**. Within a CBRS slot, evict by **prototype distance** to keep a *spread* of typical + boundary samples rather than uniform-random. **Substrate-fit: high** (class means already stored; no gradients). **Benefit:** cheap upgrade to blind within-class random eviction — but must keep a spread, not collapse to the mean (that is the herding null we already tied). Respects no-gradient-replay. ✅
4. **Weighted closed-form re-fit (GCR idea, gradient-free transplant)**. Give LUT entries **importance weights** in the Gram/prototype accumulation (weight by leverage / class-rarity), instead of every sample contributing equally to the solve. **Substrate-fit: high** (weighted ridge is still closed-form). **Benefit:** GCR shows weighting helps most at small buffers = our C=20 regime. Respects no-gradient-replay. ✅
5. **Report min-ACC / the stability-gap metric on the grid-4 loop** *(measurement, not a mechanism)*. Zero-cost, gradient-free instrument that turns "OURS rides flat vs ER saw-tooths" (P10 §10) into a quantitative worst-case number and *verifies* our inter-sleep trough is actually flat before we relax the cadence. **Substrate-fit: maximal** (pure eval). ✅
6. **Gradient-coreset selection (GSS / OCS / GCR)** — **NOT substrate-friendly** (per-sample gradients). Keep as the **diagnostic ceiling** an offline oracle race would measure CBRS against; do not deploy. ❌ (violates no-gradient-replay).

**Which respect our no-gradient-replay constraint:** #1–#5 all do (feature/prototype/precision-space, no backward pass, closed-form re-fit intact). Only #6 (the Camp-A gradient coresets) violates it and is diagnostic-only.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Sun et al. 2022 — InfoRS](sun-2022-inforss.md) | ⭐⭐⭐⭐⭐ | Closed-form surprise+learnability eviction = reuse the gate's error signal we already throw away. |
| [Harun & Kanan 2023 — Overcoming the Stability Gap](harun-2023-overcoming-stability-gap.md) | ⭐⭐⭐⭐⭐ | Its two key fixes (class-mean init, frozen old outputs) are what our namer already IS → grid-4 may be relaxable. |
| [Tiwari et al. 2022 — GCR](tiwari-2022-gcr.md) | ⭐⭐⭐⭐ | The cleanest selection objective (coreset gradient ≈ all-data gradient); motivates a weighted closed-form re-fit. |
| [Yoon et al. 2022 — OCS](yoon-2022-ocs.md) | ⭐⭐⭐⭐ | Representativeness + diversity + past-affinity criteria to re-express gradient-free in feature/prototype space. |
| [Aljundi et al. 2019 — GSS](aljundi-2019-gss.md) | ⭐⭐⭐⭐ | The gradient-diversity ideal CBRS proxies; the offline oracle ceiling for our tight-cap retention. |
| [De Lange et al. 2023 — Stability Gap](delange-2023-stability-gap.md) | ⭐⭐⭐⭐ | min-ACC / per-iteration metric — the sharper safety instrument for our inter-sleep trough. |
| [Harun et al. 2024 — GRASP](harun-2024-grasp.md) | ⭐⭐⭐⭐ | Prototype-distance signal (gradient-free) → convert from replay curriculum to spread-preserving eviction. |
| [Rebuffi et al. 2017 — iCaRL/herding](rebuffi-2017-icarl-herding.md) | ⭐⭐⭐ | The named null: herding tied CBRS in P9.3; the baseline any new lever must beat. |

## Leads spawned
- **Closed-form predictive-variance eviction for SLDA/RanPAC** — derive surprise/leverage from the namer's own precision (the concrete build of lever #1).
- **Adaptive cadence conditioned on the drift gate** — schedule sleep density by onset/switch signal vs fixed grid-4 (lever #2); connects to P10 §10 mid-domain-sleep result.
- **Rainbow Memory / uncertainty-diversity exemplar selection** (Bang et al. 2021) — gradient-free diversity eviction, a GRASP successor.
- **MIR — Maximally Interfered Retrieval** (Aljundi et al. 2019) — retrieval-by-interference; likely order-invariant-null for our batch re-fit, worth confirming.
- **DRO memory evolution** (arXiv 2207.07256) — worst-case buffer evolution vs selection; substrate-fit unclear.
- **Feature-space k-center coreset** (Sener & Savarese 2018) — the gradient-free coreset our substrate could actually run.
