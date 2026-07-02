# Phase 7 — The Readout: the GD *namer* on the frozen SCFF bulk

> **The front door.** Read this for the verdict; open [`phase7-report.md`](phase7-report.md) for the full story with
> every figure, `RESULTS.md` for the numbers, `expK/experiment-K.md` for a rung's story, `design.md` for the pre-run
> plan. Phase 7 is **Stage 2's first GD phase** (P7 readout · P8 economy+cost · P9 maintenance). SCFF sorted the world
> into "kinds of things"; **P7 puts *our* names on the kinds** — read-only on the frozen `NoiseAugContrast` bulk (GD
> reads taps, never writes; the P2.5 envelope held). Ran 2026-07-02, P7.0→P7.6, single-thread, seeds
> `[42,137,271,314,1729]`, all guards pass.

---

## The verdict — **the 20% is NOT gradient descent** 🔥

**The committed namer is RanPAC — a no-gradient, closed-form analytic head** (a frozen random ReLU projection →
running-Gram ridge prototype), shipped with a **class-balanced-reservoir imbalance guard**. On the continual home it
sits in a **3-way statistical tie {MLP, RanPAC, SLDA}** for the accuracy×BWT frontier (mutually within-noise), has the
**highest static accuracy**, **passes the A6 continual-safety gate**, is **#1 on natural digits** (AA 0.949, near-zero
forgetting), and is the most spine-clean of the tied cluster. The two heads it ties are *also* no-gradient (SLDA
analytic, MLP the only gradient one) — so **the precise 20% brain names the world with no backward pass at all.** The
"20% GD" is a *role*, not a *method*.

**The spine bends — honestly, and less than feared.** The project's spine says read the class **direction**, not a
magnitude; only the **cosine** head is direction-pure. It is perfectly spine-clean (argmax-flip **0.000**) but
**sub-competitive** where the bulk has structure to exploit: on the synthetic home it trails the magnitude frontier by
**Δ = 0.128** (real, 5/5, ≫ δ=0.02) → **magnitude-wins-spine-bends**. But that price **shrinks 4× on natural digits
(−0.036)** and **vanishes on CIFAR-flat** (where the bulk itself has no composable depth). The winner (RanPAC) reads a
*magnitude* (a ridge prototype) yet is **recency-robust — not because it reads direction, but because it has no trained
softmax weights to inflate** (density ≠ class, wearing its 7th coat).

**Two design guesses the sims overturned (the honest science):**
- **AIR is NOT the no-gradient imbalance guard.** The plan expected the Analytic Imbalance Rectifier to guard a
  closed-form winner; it **over-corrects** (crushes recent classes). The reliable guard is **class-balanced reservoir
  sampling (buffer-side, family-agnostic)** — re-balancing the *input* beats re-weighting the *output*.
- **The multimodality "cliff" is not multimodality.** Natural per-class features are **unimodal** (n-modes = 1.0); the
  accuracy lever is an **anisotropic metric** — a **tied covariance** (whitening) buys +0.19 over a Euclidean prototype,
  **closed-form, no non-convex mixture needed** (a mixture *hurts*). The convex/analytic story survives.

---

## The bake-off — where accuracy×BWT peaks on the direction↔magnitude axis

| head (family) | acc | AA (continual) | BWT | spine-flip | committed? |
| --- | --- | --- | --- | --- | --- |
| cosine-ncm / cosine-softmax (direction-pure) | 0.26 / 0.54 | 0.32 / 0.48 | −0.14 / −0.23 | **0.00 / 0.00** | spine-clean but sub-competitive |
| linear-softmax (convex floor) | 0.59 | 0.58 | −0.18 | 0.68 | the floor |
| NCM · SLDA · FeCAM (magnitude prototypes) | 0.26 / 0.58 / 0.53 | 0.33 / **0.60** / 0.46 | −0.16 / −0.16 / −0.30 | 0.58 / 0.89 / 0.76 | SLDA in the top tie; FeCAM struck |
| **RanPAC · RLS (analytic, no-gradient)** | **0.65** / 0.62 | **0.62** / 0.56 | −0.16 / −0.20 | 0.54 / 0.56 | **RanPAC = committed** |
| MLP head (non-convex, gradient) | 0.63 | 0.62 | −0.15 | 0.60 | the "if we paid GD" anchor — no better |
| `race_bp` (static BP ceiling, raw input) | 0.87 | — | — | — | static reference only |

*(synthetic CI home, median; full IQR + the 9-head scorecard in [`RESULTS.md`](RESULTS.md).)* The frontier top is a
statistical tie of **MLP, RanPAC, SLDA**; the projection earns its keep (**RanPAC − RLS = +0.047, real**); the
direction-pure cosine sits below the frontier.

![Phase 7 in one figure — the bake-off frontier](exp1/figs_p7_1/BAKEOFF.png)
*The phase in one glance. **Left** — the accuracy×forgetting frontier: **RanPAC** sits at the top-right, tied with the
gradient MLP and the un-projected RLS, two of the top three using **no gradient**; the direction-pure cosine-softmax and
the max-magnitude FeCAM fall below, and the bare prototype heads collapse sub-floor (greyed). **Right** — the scorecard:
RanPAC carries the highest static accuracy, while only the two **cosine** heads are perfectly spine-clean (flip 0). The
whole Phase-7 tension is this one picture: the frontier peaks off the direction-pure corner, so **the spine bends** — but
it bends toward a *no-gradient* winner.*

---

## The ladder (what ran, what each decided)

| rung | question | verdict |
| --- | --- | --- |
| **P7.0** `exp0` | bench + guards + floor/ceiling + the RanDumb control | **BENCH TRUSTED** — 7/7 guards; bulk beats a raw-pixel random projection (all heads); ties a random *expansion* of its own taps for a linear namer (ELM) |
| **P7.1** `exp1` | the readout bake-off — does cosine match the magnitude no-grad SOTA? | **magnitude-wins-spine-bends** (Δ=0.128); **RanPAC committed** (no-gradient, top acc, spine tie-break) |
| **P7.2** `exp2` | is the frozen space multi-modal; is the escape closed-form? | **unimodal** (n-modes 1.0); the lever is **tied covariance** (+0.19), closed-form, **no mixture** |
| **P7.3** `exp3` | the bursty-imbalance guard for the committed head | **class-balanced reservoir** (cbrs); **AIR over-corrects** (design overturned) |
| **P7.4** `exp4` | does the committed head keep the A6 win? *(the gate, 5 seeds + veto)* | **RanPAC PASSES**; trained cosine-softmax + max-magnitude FeCAM **STRUCK** (recency dent) |
| **P7.5** `exp5` | does it hold on real flat data (digits, CIFAR-flat)? | **YES on digits** (RanPAC #1); spine price shrinks/vanishes on natural; CIFAR flags SLDA |
| **P7.6** `exp6` | assembled RanPAC + cbrs end-to-end | **HOLDS** (AA 0.627 ≥ bar; BWT improves) — levers stack |

---

## The committed namer (handed to Phase 8)

**RanPAC + class-balanced-reservoir guard** — a frozen random ReLU projection φ=relu(Wr·f) → a running-Gram ridge
prototype `W=(G+λI)⁻¹M`, no gradient, streaming, A6-safe. Its value **tracks the bulk's**: it wins where SCFF composes
class structure (synthetic tie, digits #1) and is idle where SCFF has no depth (CIFAR-flat, where all heads collapse to
~0.3 and the cheaper SLDA edges it).

**The Stage-2 brief (what Phase 8/9 must weigh):**
- **The cost trade (Phase 8's call).** RanPAC's projection cost proxy is **~200× SLDA's** (a 2000-D Gram + solve vs a
  768-D one). **Cost was descriptive-only in Phase 7 (never a tie-break)** — but **SLDA is a within-noise, far cheaper
  no-gradient alternative** that also passes the A6 gate and is *more robust on depth-less inputs* (CIFAR). If the
  substrate cost meter (P8) makes RanPAC's projection prohibitive, **SLDA is the committed fallback** — its only cost is
  spine-cleanliness (argmax-flip 0.89 vs RanPAC 0.54).
- **The imbalance guard to carry:** class-balanced reservoir sampling (buffer-side). **AIR is available but not shipped**
  (over-corrects).
- **Still owed (from Phase 6, deferred here on purpose):** the **read-side noise residual** (input-transducer
  directional + ADC < 3-bit) — a calibration defense a *chosen* head adds on top of itself; now that the head is chosen
  (RanPAC/SLDA), Phase 8/9 can address it.

---

## The decision-record deltas (to bank at phase close — flagged, in `idea/main.ideas.v1.md`)

- **N3** ("GD = residual boosting blocks") → **superseded** by "single frozen bulk + read-only namer" (boosting dropped).
- **S4** ("two GD organs") → **collapses to one** — the namer (Interface-GD retired with the blocks).
- **S9** (fixed short-stack reader) → **extended** with the committed *head* (RanPAC / analytic), not just the placement.
- **new supporting decision:** *the namer is a closed-form/streaming analytic head, not gradient descent — the "20% GD"
  is a role, not a method.*
- **N2** (EMA-view) + **S6** (the gate) stay **Phase-8/9's** — untouched here. The frozen `phase6-final-architecture.md`
  is **never** retro-edited.

## Read next

| For | Go to |
| --- | --- |
| **The full story, every figure, the per-rung reads** | [`phase7-report.md`](phase7-report.md) |
| The scalar ledger (per-rung numbers + the verdict) | [`RESULTS.md`](RESULTS.md) |
| The pre-run design (the ladder, the bake-off, the numeric verdict cut) | [`design.md`](design.md) |
| The binding reporting contract | [`result-format.md`](result-format.md) |
| The run-cards | `exp0`…`exp6/` `experiment-*.md` (P7.0–P7.6) |
| The literature behind every mechanism | [`../../research/papers/phase7/`](../../research/papers/phase7/README.md) |
| The Stage-2 map | [`../stage2-design.md`](../stage2-design.md) |

*Prev:* [Phase 6](../phase6/README.md) · *Next:* Phase 8 — the economy gate + the cost meter (RanPAC vs SLDA).
