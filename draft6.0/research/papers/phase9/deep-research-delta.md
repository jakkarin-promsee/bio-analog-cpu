# Phase 9 — deep-research delta: *did the rough plan's research cover it all, and is there a better choice?*

> **What this is.** The first `phase9/` research pass ([`README.md`](README.md) + the three story files) was a **breadth-first
> data-collection** to fix a rough direction. This file is the **second, targeted pass**, run at plan-hardening time
> (2026-07-02), asking of each rung: *is the staged research enough, and did the field build something better than our
> rough guess?* It records only the **delta** — what the first pass missed or under-specified — per rung, with the new
> papers and the resulting design decision. It feeds [`../../../src/phase9/design.md`](../../../src/phase9/design.md) §3+
> (the hardened ladder). Same rule as Phase 8's [`../phase8/deep-research-delta.md`](../phase8/deep-research-delta.md):
> **flagged, then folded into the spec; never a silent edit.**

**Verdict of the pass:** the staged research got the *frame* right (replay is our home; slow-or-unsupervised between
layers; direction-not-confidence for the north-star hand-off) — but it **under-named five things the field has since
built**, and one of them (P9.0) is a **sharper risk than the rough plan assumed**. Each is now pinned into the ladder.

---

## D0 · P9.0 — "the bulk doesn't forget" is NOT a safe assumption (the risk got bigger)

**What the rough plan assumed.** That measuring `bulk_drift` (cosine of fixed probes) confirms the cheapness story, and
the fork "drift slow → cheap" is the likely outcome.

**What the field says (the delta).** Continuous / unsupervised continual learning **does forget under a non-stationary
stream** — it is not a formality:
- *The Challenges of Continuous Self-Supervised Learning* (Purushwalkam et al., ECCV 2022) — continuous SSL on
  non-stationary sources **shows catastrophic forgetting**, contradicting the folk belief that "unsupervised = safe."
- *Revisiting Supervision for Continual Representation Learning* ([2311.13321](https://arxiv.org/abs/2311.13321)) — SSL and
  supervised learning forget **differently, not universally less**: SSL keeps higher *first-task* retention but underfits
  later tasks. So "SCFF doesn't forget" is a **claim about our specific objective on our stream**, not a free inheritance.
- *Self-Supervised Models are Continual Learners* (CaSSLe, Fini et al., CVPR 2022, [2112.04215](https://arxiv.org/abs/2112.04215))
  — the optimistic pole: SSL objectives *can* be made to compose continually. The truth for us is empirical and between
  these poles.
- (Carried: *Probing Representation Forgetting* [2203.13381](https://arxiv.org/abs/2203.13381) — drift is real and measurable.)

**The design decision.** P9.0 must **split the two things the cheapness story conflates — rotation vs destruction** — and
it is a genuine risk gate, not a warm-up. Measure **(a)** `bulk_drift` cosine (the *rotation* rate a fresh sleep re-solve
tracks) **and (b)** a **frozen-early-task linear probe re-scored on the *current* bulk** (does an old task's *separability*
survive as SCFF keeps learning — the *destruction* test). Rotation → sleep fixes it cheaply (assumption holds).
Destruction → the founding cheapness assumption **breaks** (headline; may make N2 mandatory or reshape the loop). The
rough plan's instinct was right; the stakes are higher than it wrote.

---

## D1 · P9.1 — N2 is a 3-arm bake-off, and the road-not-taken now has a name: **LDC**

**What the rough plan had.** N2 as "slow the late layers / EMA-view," with SDC/LDC flagged as a vague "drift-compensation
road-not-taken."

**What the field says (the delta).** Drift-*compensation* (estimate the drift and correct for it) has matured past the
2020 method the first pass half-remembered:
- **SDC** (Yu et al., CVPR 2020, [2004.00440](https://arxiv.org/abs/2004.00440)) — projects new features toward the old
  space; **assumes drift is a local translation** (fails on scaling/rotation). This is the weak original.
- **LDC — Learnable Drift Compensation** (Gomez-Villa et al., ECCV 2024, [2407.08536](https://arxiv.org/abs/2407.08536);
  code `alviur/ldc`) — a **learnable projector** mapping consecutive feature spaces, handling **rotation + scaling**,
  working on **any moving backbone, supervised *or unsupervised***, **exemplar-free**, "fast and straightforward to
  integrate." This is the current SOTA and the *correct* name for our road-not-taken.
- Cousins: **ADC** (adversarial drift, Goswami et al. CVPR 2024), **EFC** (Elastic Feature Consolidation, Magistri et al.
  ICLR 2024). *(EMA note: [2411.18704](https://arxiv.org/abs/2411.18704) — EMA representations are more general and more
  linearly separable, supporting the EMA-view arm.)*

**The design decision.** Keep **N2 primary** as the cheap, in-scope lever — a **3-arm bake-off**: **(0) no-N2** ·
**(1) LLRD-rate** (lower the late-read-layer learning rate; rate-only, moves no objective knob; the doubly-grounded
default) · **(2) EMA-view** (namer reads a slow tap-EMA; read-side, touches SCFF not at all). **LDC is the explicitly
scoped-out road-not-taken**, with a *precise* trigger: reach for it only if **(i)** N2 can't slow the drift enough **AND**
**(ii)** P9.2 meters the LUT re-forward as too expensive — because a learned projector is a **new trained organ** heavier
than "read-side / rate-only," so it belongs to the analog-realism / north-star track, not P9's freeze. Crucial reframe the
first pass missed: **our sleep already re-extracts prototypes by re-forwarding the raw LUT through the current bulk** — so
we do *not* need drift-compensation for the *replay* path (we get fresh, consistent features for free); N2 targets only the
cheaper problem of **awake tracking between sleeps.** That is why N2 (cheap, read-side) beats LDC (a trained organ) *for
us* specifically, and it is worth stating on the record.

---

## D2 · P9.2 — "consolidation depth" is **Latent Replay**, published

**What the rough plan had.** "Readout-aware consolidation depth — which extractor depth sleep re-fits" as a home-grown idea.

**What the field says (the delta).** It is a named, published mechanism:
- **Latent Replay** (Pellegrini et al., IROS 2020, [1912.01100](https://arxiv.org/abs/1912.01100)) — replay at a chosen
  *mid-network layer*: layers **below** the replay layer are slowed (stable low-level features), layers **above** learn
  freely; and pushing the replay layer **down** improves accuracy ("continual tuning of representation layers matters").
  This is *exactly* our sleep-consolidation-depth question, and it **couples P9.2 to P9.1** — "slow below the read layer"
  is the latent-replay recipe, which for us (a reader on a shallow truncation on the flat home) means the N2 slowdown and
  the consolidation-depth choice are one design, not two.
- **Layerwise Proximal Replay** ([2402.09542](https://arxiv.org/abs/2402.09542)) — layer-wise update constraints; the
  refinement if a flat depth-choice underperforms.
- (Also relevant to our unsupervised bulk: *Unsupervised Replay Strategies* [2410.16154](https://arxiv.org/abs/2410.16154).)

**The design decision.** Frame P9.2 as **latent-replay layer selection on the frozen-to-GD bulk**: at sleep, re-fit the
namer over the LUT using the **same feature depth the deployed reader uses** (S9: trunc ~L2–3 on the flat home, all-tap for
peak), *not* all-tap by default. Cite Latent Replay as the machinery. The rough instinct was right and now has a spine of
literature under it.

---

## D3 · P9.3 — refine the eviction arms: **drop GSS, add herding (the magnitude null) + D-CBRS**

**What the rough plan had.** "cbrs vs recency vs magnitude vs unbounded-oracle."

**What the field says (the delta).**
- **CBRS beats GSS**, and **GSS needs per-sample gradients** (Aljundi et al., [1903.08671](https://arxiv.org/abs/1903.08671))
  — which our **gradient-free** namer does not produce, so GSS is *doubly* inapplicable. **Drop it** (don't even race it).
- **Herding** (iCaRL, Rebuffi et al. 2017) selects exemplars whose **features are closest to the class mean** — a
  *magnitude/mean* criterion, **better at small buffers, worse at large** (a real, cited tradeoff). This is the perfect
  **spine null** for P9.3: herding keeps the *dense center*, not the class *direction span* — density ≠ class, at the
  buffer. Race it *to demonstrate the spine*, the way P8 raced the magnitude-of-shift trigger.
- **D-CBRS** ([2207.05897](https://arxiv.org/abs/2207.05897)) — CBRS can collapse **intra-class diversity**; D-CBRS fixes
  it. A **conditional refinement** arm (add only if plain CBRS loses diversity — but P7 found our per-class features
  *unimodal* (anisotropy, not multimodality), so plain CBRS is the expected winner and D-CBRS the fallback).
- **Buffer scaling** (TEAL [2407.00673](https://arxiv.org/abs/2407.00673); the bag-of-tricks survey
  [2010.05595](https://arxiv.org/abs/2010.05595)): small buffers = 1–3 exemplars/class; larger → smaller output-distribution
  shift → better BWT; **selection strategy matters as much as size.** Grounds the **cap × #classes** scaling sub-sweep.

**The design decision.** P9.3 arms = **unbounded-oracle (ceiling) · CBRS (committed) · reservoir (iid) · recency/FIFO ·
herding (the magnitude/mean null)**; **GSS dropped**; **D-CBRS conditional**. Add a **cap-vs-#classes** scaling sub-sweep
(does the needed bound grow with class count — the scaling-law flag). Our LUT stores **raw** prototypes (not features, to
dodge drift), so eviction is over raw inputs — the herding-null still applies (feature-mean over the *current* bulk).

---

## D4 · P9.4 — plain temperature scaling is **ineffective under shift** → the read-side defense must be feature-level

**What the rough plan had.** "Read-side calibration-under-shift, temperature-scaling-style, re-estimated at sleep."

**What the field says (the delta).** A scalar temperature will **not** defend a directional input-transducer shift:
- **Global temperature scaling is ineffective under distribution shift** (multiple 2025 sources) — it fixes over/under-
  confidence on *in-distribution* data, not a *coherent feature translation*.
- **T-CIL** (CVPR 2025) — the first effective TS for class-incremental learning **without an old-task validation set**
  (uses adversarial perturbation to pick the temperature); **DATS** ([2509.21161](https://arxiv.org/abs/2509.21161)) —
  *distance-aware* TS for CIL. These are the CIL-calibration state of the art.
- **Test-time prototype shifting** ("Just Shift It", [2403.12952](https://arxiv.org/abs/2403.12952)) and EMA target-
  prototype test-time adaptation — the *feature/prototype-level* correction that a directional shift actually needs.

**The design decision.** P9.4 stays **conditional (earn-its-place probe first)** — but if it runs, the read-side defense is
**not** a scalar temperature; it is a **feature/prototype-level re-estimation** (re-fit SLDA's class means / shared
covariance at sleep on shifted reads, i.e. a prototype shift), with TS/T-CIL kept only as a **calibration diagnostic**, not
the fix. Spine caution unchanged: any calibration signal is **direction-grounded**, never a confidence magnitude (the
north-star tie-break; TENT-style entropy is a magnitude — cautioned in [`north-star-bridges.md`](north-star-bridges.md)).
This *raises* the bar for P9.4 to earn its place: if a feature-level re-fit is needed, it edges toward the analog-realism
layer, which is the honest place for it.

---

## D5 · The discipline the research *confirms* (no change, but load-bearing)

- **Freeze in P9, judge in P10** is standard train/validation hygiene (don't tune against the test comparator). No new
  literature needed; it is the same rule that governs any honest benchmark. Kept as the P9→P10 hard boundary.
- **Our sleep = raw-exemplar replay with recomputed prototypes** (iCaRL/GDumb-style re-extraction; **REMIND is the
  frozen-backbone anti-pattern**, and **SDC/LDC the exemplar-free road-not-taken**) — the Phase-8 framing survives intact.
- **The gate/cadence are drift-rate-conditional** (P8's flag): if P9.1's N2 slows the drift, P9.2 must re-confirm the sleep
  *frequency*, not only set the *depth*. The research reinforces that "how slow / how often" is set by the *measured* drift,
  never a constant.

---

## New papers to add to the `phase9/` index (were not in the first pass)

| paper | id / venue | rung | why it's here now |
| --- | --- | --- | --- |
| The Challenges of Continuous Self-Supervised Learning | ECCV 2022 | P9.0 | continuous SSL **does** forget — the assumption is a risk, not a formality |
| Revisiting Supervision for Continual Representation Learning | [2311.13321](https://arxiv.org/abs/2311.13321) | P9.0 | SSL forgets *differently*, not less — measure it on *our* objective |
| Self-Supervised Models are Continual Learners (CaSSLe) | [2112.04215](https://arxiv.org/abs/2112.04215) | P9.0 | the optimistic pole; SSL *can* compose continually |
| Semantic Drift Compensation (SDC) | [2004.00440](https://arxiv.org/abs/2004.00440) | P9.1 | the original drift-compensation (translation-only; the weak baseline) |
| **Learnable Drift Compensation (LDC)** | [2407.08536](https://arxiv.org/abs/2407.08536), ECCV 2024 | P9.1 | **the road-not-taken, correctly named** — learnable, unsupervised-capable, exemplar-free |
| EMA of Weights: Dynamics and Benefits | [2411.18704](https://arxiv.org/abs/2411.18704) | P9.1 | EMA reps are more general/separable — supports the EMA-view arm |
| **Latent Replay for Real-Time CL** | [1912.01100](https://arxiv.org/abs/1912.01100) | P9.2 | **the consolidation-depth mechanism, published** (replay-layer selection) |
| Layerwise Proximal Replay | [2402.09542](https://arxiv.org/abs/2402.09542) | P9.2 | layer-wise update constraints (the refinement) |
| D-CBRS (intra-class diversity) | [2207.05897](https://arxiv.org/abs/2207.05897) | P9.3 | the CBRS diversity refinement (conditional arm) |
| TEAL / Bag-of-Tricks replay | [2407.00673](https://arxiv.org/abs/2407.00673) · [2010.05595](https://arxiv.org/abs/2010.05595) | P9.3 | small-buffer selection + the scaling picture |
| T-CIL (temperature scaling for CIL) | [2503.22163](https://arxiv.org/abs/2503.22163), CVPR 2025 | P9.4 | effective TS without an old-task val set — a live margin-calibration option (uses memory exemplars), not just a diagnostic |
| DATS (distance-aware TS) | [2509.21161](https://arxiv.org/abs/2509.21161) | P9.4 | distance-aware calibration for CIL |
| Just Shift It (test-time prototype shift) | [2403.12952](https://arxiv.org/abs/2403.12952) | P9.4 | the **feature-level** correction a directional shift needs (TS alone fails) |

*(iCaRL herding, CBRS, GSS, A-GEM, REMIND, EWC/SI, the momentum-encoder set, PonderNet — already in the
[`README.md`](README.md) index / the three story files; not repeated here.)*
