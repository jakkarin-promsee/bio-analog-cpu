# Phase 8 — deep-research delta: *did the rough pass cover it, and is there a better choice?*

> **Written 2026-07-02, the second (deep) research pass.** The kickoff pass ([`the-economy-gate.md`](the-economy-gate.md))
> was a *direction-finder* — it named DDM/ADWIN/Skip-RNN as "the gate is a solved streaming problem" and flagged the
> false-fire caveat. This file asks the author's question head-on: **does that rough pass cover all of Phase 8, or did it
> miss something a run would trip on?** Verdict per topic below. **Two things reshape the plan** (the co-adapting-backbone
> literature + the ADC-dominated cost model); the rest confirms the rough direction with sharper tools and a real
> evaluation vocabulary. This feeds [`../../../src/phase8/design.md`](../../../src/phase8/design.md).

---

## 0 · The one-line verdict

**The rough pass had the right *spine* (the gate is off-the-shelf drift-detection; false-fires burn the 80/20) but was
missing three things a run needs:** (1) a **standard evaluation vocabulary** for the false-fire axis (MTD / MTFA / FAR /
MDR — so "false-fire rate" stops being a hand-wave); (2) the **co-adapting-backbone / representation-drift** literature —
which is *exactly* our live-SCFF problem and gives our sleep-re-forward a name and a road-not-taken; (3) a concrete
**cost-meter model** (ADC-dominated CIM energy — NeuroSim-family), the deliverable the rough pass only named. All three
are now in hand. No topic overturned the rough direction; two sharpened it materially.

---

## 1 · The gate detectors — rough direction CONFIRMED, candidate set widened

**Rough had:** DDM (error, two-threshold), ADWIN (two-window), Skip-RNN (learned budget), ADWIN-U (label-free), DNI (the
*don't*). **Deep adds / sharpens:**

- **The 2024 benchmark** ([A Framework for Evaluating & Benchmarking CDDMs, 2606.07789](https://arxiv.org/abs/2606.07789))
  raced 14 detectors (ADWIN, DDM, EDDM, RDDM, HDDM-A/W, CUSUM, PH, SEED, STEPD, **ABCD**, STUDD…) across four drift
  **types** — and the result is directly load-bearing for us: **ADWIN excels at class-prior drift but underperforms on
  feature-permutation; it "almost systematically flags virtual drift as real."** Error-based detectors are more precise
  but lag. **This is our exact tension, measured in the field**: the label-free feature trigger fires early but
  false-fires on nuisance; the error trigger is precise but late.
- **A genuinely better label-free option the rough pass missed — STUDD** ([2103.00903](https://arxiv.org/abs/2103.00903)):
  a *student* mimics the *teacher*; monitor the student's mimicking loss (no labels). Its property is **the opposite
  trade from ADWIN-on-features: "more conservative — fewer false alarms, but slower to detect."** So the label-free axis
  is not one point but a **trade-off curve** (fast/false-fires ↔ conservative/lags) — worth a bake-off arm, because *for
  us false-fires are the expensive failure*, which tilts toward the conservative end.
- **The purpose-built label-free tool the rough pass didn't race — DriftLens** ([Greco et al., IEEE TKDE 2025,
  2406.17813](https://arxiv.org/abs/2406.17813)): a **real-time distribution-distance detector on the model's embeddings**
  vs a fixed reference window — *precisely* "fire when the SCFF taps move," and a better fit than a hand-rolled statistic.
  Carry it as the label-free **reference** the home-grown class-direction tap-drift signal is checked against.
- **⚠ "ADWIN-U" is a REAL published method, not our coinage** ([Assis & Souza, KAIS 2025](https://link.springer.com/article/10.1007/s10115-025-02523-1)):
  it runs ADWIN on **unsupervised higher-order *input*-distribution moments (std / skew / kurtosis)** — so it is *most*
  sensitive to exactly the covariate/nuisance shift we want to **ignore**. So we do NOT call our tap arm "ADWIN-U"; the
  raw-moment/magnitude-of-shift detector is carried as the **predicted-to-false-fire null** (the spine demonstration), and
  the P8.2-preferred candidate reads drift **along the class direction** (design §1/§2.2) — though the frozen loop ultimately deployed the labeled error-EMA on DDM; the direction trigger is validated, not shipped.
- **ABCD** (autoencoder-based) tops feature-permutation drift — an option if the tap-drift signal needs a learned
  compressor, but heavier; note it, don't default to it (our taps are already a learned compression).
- **Gradual drift is the likely regime, and DDM/ADWIN are abrupt-biased** — SCFF's representation *creep* is slow, and the
  field warns error-detectors lag on gradual drift. **HDDM-A/W or RDDM** (both in the 2606.07789 benchmark, gradual/
  recurring-tuned) are the conditional arm to add **if P8.0 shows the creep is slow.**
- **The reliability lens** ([Are Concept Drift Detectors Reliable Alarming Systems?, 2211.13098](https://arxiv.org/abs/2211.13098))
  is the paper that says out loud what the rough caveat implied: detectors trade detections for false alarms, and the
  false-alarm cost is under-reported. Cite it as the *why* behind making FAR a first-class axis.

**Verdict:** keep DDM + ADWIN + abs-θ + learned-budget from the rough plan; label-free triggers = **class-direction
tap-drift** (P8.2-preferred candidate — validated but the frozen loop deployed DDM-on-error-EMA) · **DriftLens** (reference) · **STUDD** (conservative) · **magnitude-of-shift**
(the false-fire null); conditional **HDDM/RDDM** if drift is gradual. DNI stays the *don't*.

## 2 · The evaluation vocabulary — the rough pass had NO metric for "false-fire" (now fixed)

The rough plan said "false-fire rate as a failure axis" but never defined it. The drift community has a standard set
([survey](https://www.sciencedirect.com/science/article/pii/S1051200426004434); benchmark 2606.07789):

- **MTD** — Mean Time to Detection (detection *delay*; lower better; true-positives only).
- **MTFA** — Mean Time between False Alarms (higher = rarer false alarms).
- **FAR** — False-Alarm Rate (false fires per unit stream).
- **MDR** — Missed-Detection Ratio.
- **MTR** — an aggregate of MDR/MTD/MTFA.
- Precision/Recall/F1 within an **acceptable detection window** (δ_max delay, δ_pre precedence) around a *known* drift.
- **The fundamental trade-off (the gate's whole Pareto axis):** optimizing MTFA (fewer false alarms) *necessarily*
  worsens MTD/MDR (slower / more misses), and vice-versa. There is no free detector; the gate bake-off is *choosing where
  on this curve our 80/20 lives.*
- **How to measure false-fires:** inject drift at *known* positions and count fires *outside* the acceptable window as
  false positives; and/or run a **stationary** segment and count *any* fire as a false alarm (= the detector-δ guard).

**Verdict:** adopt MTD + FAR (+ MTFA) as the Phase-8 gate metrics, alongside our own (accuracy-held × GD-fire-fraction).
This turns "false-fire rate" from a hand-wave into a pinned, gradeable axis.

## 3 · The co-adapting backbone — the literature the rough pass entirely missed (reshapes the frame)

The rough pass treated the gate as if the backbone were frozen (Phase-7 framing). But Phase 8's premise is a **live,
drifting SCFF** — and there is a whole named literature on exactly this:

- **"Feature / semantic drift" in online continual learning** — "changing tasks causes the representation of old classes
  to conflict with new, inducing large changes in past representations." *That is our problem, named.*
- **Two answer families**, and we are cleanly in the first:
  - **(a) exemplar replay + re-forward** — store data, re-forward through the *current* backbone to refresh the head.
    **This is our raw-prototype LUT + sleep.** The correct cousin is **raw-exemplar replay with recomputed prototypes**
    (iCaRL-style re-extracted class means; GDumb-style raw buffer) — replay *raw* data, recompute the head against the
    *current* backbone. The principled reason: raw input is drift-stable; the re-forward gives mutually-consistent
    features. **⚠ NOT REMIND** ([1910.02509] / ACAE-REMIND [2105.08595]): REMIND **freezes the backbone** after task 1 and
    replays **compressed features** — the two things we deliberately avoid (we store raw *because* the backbone moves). So
    REMIND is the **anti-pattern** here (the frozen-backbone, feature-storage design that *cannot* handle a moving
    backbone), not our cousin — the earlier draft mis-cited it.
  - **(b) exemplar-free drift-compensation** — *estimate* the drift and correct the prototypes without re-forwarding:
    **SDC** (Semantic Drift Compensation, Yu 2020), **LDC** ([Learnable Drift Compensation, 2407.08536](https://arxiv.org/abs/2407.08536),
    ECCV'24 — a trainable projector that maps old→new feature space, works on *any* moving backbone, supervised *or*
    unsupervised), FeTrIL, NAPA-VQ, ADC (CVPR'24).
- **The read for us:** our sleep-re-forward is a **valid, principled answer** to representation drift (not naïve) — and
  **(b) is the road-not-taken**: if sleep-re-forward is metered *too expensive* (re-forwarding the whole LUT costs ADC
  traffic), a drift-*compensation* projector (LDC-style, cheap) is the Phase-9/north-star alternative that avoids the
  re-forward. **Flag it, don't build it** (Phase 8 = the mechanism as designed; the cheaper compensation is a later lever).
- Also relevant: **Momentum Knowledge Distillation in online CL** ([2309.02870](https://arxiv.org/abs/2309.02870)) and the
  EMA-teacher line — the N2 "slow the late layers / EMA-view" route, which stays **Phase 9's** (slow-coordination.md).

**Verdict:** name our sleep as the exemplar-replay answer to representation drift; cite LDC/SDC as the exemplar-free
alternative deferred to Phase 9. This is the single biggest gap the rough pass had, and it's the *core* of Phase 8.

## 4 · The cost meter (Q3, delegated to me) — behavioral, ADC-calibrated, NeuroSim-family

**Rough had:** "charge cycles / ADC / write energy, replacing the op-count proxy" — the *goal*, no model. **Deep resolves
the fidelity question:**

- **The standard tools are behavioral macro-models, not SPICE:** **DNN+NeuroSim** (Georgia Tech — circuit-level
  area/energy/latency for CIM, versatile device tech), **ISAAC** (ISCA'16), **PUMA** (ASPLOS'19), MNSIM, CrossSim, and
  **IBM AIHWKit** — *which Phase 6 already used* for its noise-model structure. So a behavioral energy model is the
  field-standard level, and it is **consistent with our Phase-6 scope rule** (behavioral analog model, no device physics).
- **The dominant finding, everywhere: ADC energy dominates.** ADCs at layer/column boundaries dominate peripheral energy
  and area (ISAAC: peripherals ≈ half the tile energy, ADCs the single largest term; ADCs occupy **5–50× the crossbar
  area**). **Concrete pJ anchors to calibrate the meter's e_ADC/e_MAC ratio:** a SAR-ADC ≈ **0.2 pJ/conversion-step**
  (Walden FoM), energy ≈ **×2 per effective bit** (exponential in ENOB); a 6-bit SAR ADC alone = 33 % of one capacitive-CIM
  macro; a crossbar 8-bit **MAC < 100 fJ** — i.e. e_ADC ≫ e_MAC by 1–2 orders. **Weight writes** (capacitor/RRAM
  programming, iterative write-verify) are expensive *per write* but done rarely (at consolidation/refresh) → the gate's
  point. (Log these in the manifest + run an ADC-bits sensitivity sweep — the meter's verdict is only as honest as e_ADC.)
- **So the meter is a weighted per-operation tally, ADC-centred:** `E = n_MAC·e_MAC + n_ADC·e_ADC(bits) + n_write·e_write
  + n_solve_flop·e_digital`, with literature-sourced *relative* magnitudes (ADC ≫ MAC; write large but rare; the digital
  ridge/tied-cov solve is the "non-free digital block" the arch-file flagged). Report **relative energy** (and pJ where a
  number is defensible), not SPICE Joules. **The meter reduces to the P7 op-count proxy under unit energies** — that's the
  guard that ties it to Phase 7.
- **The RanPAC-vs-SLDA verdict it will render:** RanPAC's 2000-D projection vs SLDA's 768-D read → ~2.6× the ADC read
  traffic *and* a 2000³-vs-768³ solve (~18× the solve cost). On an ADC-and-solve-dominated substrate that is a large gap;
  the meter quantifies whether the Phase-7 accuracy *tie* justifies it. **Prior: SLDA likely wins the metered cost** — the
  honest call Phase 7 deferred here on purpose.

**Verdict (Q3 decided):** a **behavioral, literature-calibrated, ADC-centred per-operation energy meter** (NeuroSim-family
level), relative-energy units, guarded to reduce to the P7 proxy. Not SPICE.

## 5 · The test stream (Q4, delegated to me) — real vs virtual drift, with a false-fire bait

**Rough had:** nothing concrete. **Deep resolves it:**

- **The real-vs-virtual distinction is the whole design:** **real drift** moves `P(y|x)` (hurts the classifier → *should*
  fire); **virtual/nuisance drift** moves `P(x)` only, boundary intact (does *not* hurt → firing = a false fire). The
  literature explicitly builds detectors to "catch real drift while ignoring virtual."
- **Standard generators:** SEA (abrupt, 3-D, threshold-on-sum), Rotating Hyperplane (gradual), RBF (drift), Agrawal,
  STAGGER; abrupt vs gradual conditions. Drift-type taxonomy (benchmark 2606.07789): class-prior, class-label-swap,
  feature-permutation, feature-filtering.
- **Mapped to OUR home:** *real drift* = the class-incremental stream (new classes appear = class-prior/appearance) **+**
  SCFF's own representation drift (old-class names slide). *virtual/nuisance drift* = a **covariate shift SCFF is
  invariant to** (its A2 nuisance-robustness) — a smooth input transform (intensity/scale/rotation of the digit
  distribution) that leaves the class boundary intact. **Firing on it = a false fire.** This is the bait the current CI
  home lacks.
- **The stream to build:** the CI digits/synthetic home + a **nuisance-drift injector** (covariate shift, boundary
  intact) + a **stationary segment** (the FAR/δ guard). Known onset positions for the real-drift markers (→ MTD) and the
  nuisance markers (→ FAR).

**Verdict (Q4 decided):** build a `make_drift_stream` = CI-home + nuisance-covariate injector + stationary segment; score
MTD on the real markers and FAR on the nuisance/stationary markers. The nuisance injector is the load-bearing new piece.

## 6 · Budgeted halting + the north-star tie — CONFIRMED, with one constraint

- **Skip-RNN** ([1708.06834](https://arxiv.org/abs/1708.06834)): budget loss `L_budget = λ·Σ u_t` (cost-per-update ×
  #updates) writes the 80/20 target *into the objective* — the learned-budget-gate arm. **PonderNet**
  ([2107.05407](https://arxiv.org/abs/2107.05407)): probabilistic halting — the north-star ancestor of our gate.
- **The constraint (from [`../phase9/north-star-bridges.md`](../phase9/north-star-bridges.md)):** a learned gate must read
  a **direction/drift** feature, **never softmax confidence/entropy** (a magnitude — why P5 struck the adaptive exit; the
  north-star brain would tear a confidence gate out). And a learned gate is a *tiny trained thing on the read side* — it
  does **not** violate the no-fast-supervised-*upstream*-of-SCFF wall (it reads taps, never writes them). Include it as an
  arm; flag its spine-tension; FD-guard it. Calibration-under-shift is the threat-to-validity for any error/confidence
  trigger — the drift trigger sidesteps it (another reason to prefer tap-drift).

**Verdict:** learned-budget-gate stays a bake-off arm, constrained to a direction/drift feature and FD-guarded; the gate
is built as PonderNet's un-looped ancestor for a clean north-star hand-off.

---

## New papers this pass adds (beyond `the-economy-gate.md`)

| paper | id / venue | why it enters Phase 8 |
| --- | --- | --- |
| A Framework for Evaluating & Benchmarking CDDMs | [2606.07789](https://arxiv.org/abs/2606.07789) | the 14-detector race + the drift-type taxonomy + the eval metrics (MTD/FAR/MTFA); "ADWIN flags virtual as real" |
| Are Concept Drift Detectors Reliable Alarming Systems? | [2211.13098](https://arxiv.org/abs/2211.13098) | the false-alarm reliability lens — the *why* FAR is first-class |
| STUDD (student–teacher unsupervised drift) | [2103.00903](https://arxiv.org/abs/2103.00903) | the **conservative** label-free detector (fewer false alarms, slower) — the false-fire-aware arm |
| **DriftLens** (label-free embedding-distance drift) | [2406.17813](https://arxiv.org/abs/2406.17813) (TKDE'25) | the **purpose-built** "fire when the taps move" detector — the label-free **reference** arm |
| **ADWIN-U** (unsupervised, input higher-order moments) | [KAIS 2025](https://link.springer.com/article/10.1007/s10115-025-02523-1) | a *real* method (not our coinage) — monitors input moments → primed to false-fire on nuisance (the null, not the candidate) |
| **iCaRL / GDumb** (raw-exemplar replay, recomputed prototypes) | [1611.07725](https://arxiv.org/abs/1611.07725) · [2007.05640](https://arxiv.org/abs/2007.05640) | the **correct cousin** of our sleep (replay raw, recompute head vs current backbone) |
| **REMIND / ACAE-REMIND** (frozen backbone, feature replay) | [1910.02509](https://arxiv.org/abs/1910.02509) · [2105.08595](https://arxiv.org/abs/2105.08595) | the **anti-pattern** — freezes the backbone + stores features (what we deliberately do NOT do) |
| **HDDM-A/W · RDDM** (gradual-drift-tuned detectors) | in benchmark 2606.07789 | the **conditional** arm if P8.0 shows the SCFF creep is slow/gradual (DDM/ADWIN are abrupt-biased) |
| Learnable Drift Compensation (LDC) | [2407.08536](https://arxiv.org/abs/2407.08536) | exemplar-free drift-compensation on a moving backbone — the **road-not-taken** vs our sleep re-forward |
| Semantic Drift Compensation (SDC) | Yu et al. 2020 | the original moving-backbone prototype-drift fix — same road-not-taken |
| Momentum KD in online CL | [2309.02870](https://arxiv.org/abs/2309.02870) | the EMA-teacher slow-coordination route (N2) — **Phase 9's**, noted for the seam |
| DNN+NeuroSim / ISAAC / PUMA | GT · ISCA'16 · ASPLOS'19 | the behavioral CIM energy macro-models — the meter's level + the ADC-dominance finding |
| Skip-RNN · PonderNet | [1708.06834](https://arxiv.org/abs/1708.06834) · [2107.05407](https://arxiv.org/abs/2107.05407) | the learned budget-gate + the north-star halting ancestor (carried, now with the direction constraint) |

**Sources:** [CDDM benchmark framework](https://arxiv.org/abs/2606.07789) · [Reliable alarming systems](https://arxiv.org/abs/2211.13098) · [STUDD](https://arxiv.org/abs/2103.00903) · [DriftLens (TKDE'25)](https://arxiv.org/abs/2406.17813) · [ADWIN-U (KAIS'25)](https://link.springer.com/article/10.1007/s10115-025-02523-1) · [iCaRL](https://arxiv.org/abs/1611.07725) · [GDumb](https://arxiv.org/abs/2007.05640) · [REMIND](https://arxiv.org/abs/1910.02509) · [LDC](https://arxiv.org/abs/2407.08536) · [Momentum KD online CL](https://arxiv.org/abs/2309.02870) · [Skip-RNN](https://arxiv.org/abs/1708.06834) · [PonderNet](https://arxiv.org/abs/2107.05407) · [drift-detection eval-metrics survey](https://www.sciencedirect.com/science/article/pii/S1051200426004434) · [NeuroSim V1.5](https://arxiv.org/abs/2505.02314) · [ADC energy/area modeling](https://arxiv.org/abs/2404.06553).
