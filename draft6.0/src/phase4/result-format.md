# Phase 4 — Result format (the reporting contract, decided before the runs)

> **Why this exists.** Same as Phase 1–3: a characterization sweep that invents its own format per cell yields a
> pile of incomparable numbers. Phase 4 is *especially* prone to it (many axes), so the contract matters most
> here. **It inherits Phase 1–3** (IQR bands, reproducibility = `manifest.json` + `arrays.npz` + a `plot.py` that
> regenerates from saved data, the n=5 disjoint-IQR rule, the 6+2 summary slots) and adds only the
> **characterization** layer: the racer encoding, the **gap-to-backprop** family, the **cost Pareto**, and the
> **capability map**. The output of every rung is a *piece of the map*, drawn the same way.

---

## Layer A — racer encoding (fixed forever, across all axes)

| racer | colour / style | role |
| --- | --- | --- |
| **OURS** (`contrast + coordination + sleep`) | **bold orange** `#d9690a` (carries from P3) | the cheap forward-only brain under test |
| **BP-ceiling** (tuned backprop MLP) | solid blue `#2c6fbf` (carries from P2/3 "GD") | the ceiling; the gap to it is the headline |
| **Mono-Forward** (forward-only supervised) | solid purple `#8a1b8a` | the supervised-local reference |
| **chance / Bayes-optimal** | thin black dotted (chance) · thin green dashed (Bayes) | the floor and the *true* ceiling |

OURS bold; references thinner. Every accuracy plot draws **chance** and (where known) the **Bayes-optimal** line —
the gap to backprop is only interpretable between those two envelopes.

## Layer B — the metric dictionary (Phase-4 additions in **bold**; carry the rest)

| metric | definition (pinned) | what it answers |
| --- | --- | --- |
| held-out accuracy | OURS / BP / Mono-Forward, **equal weight budget**, tuned BP | raw performance |
| **gap-to-BP** (HEADLINE) | `acc(BP) − acc(OURS)`; report signed (negative = OURS wins) | *where* the gap opens — the characterization metric |
| **Bayes-normalized capture** | `(acc(OURS) − chance)/(acc(Bayes) − chance)` ∈ [0,1] | fraction of the *achievable* the cheap brain captures |
| **backward cost** (substrate) | **backward credit-assignment work** = credit-distance (SCFF=0/coord-window, GD=depth) × weights **+** #backward weight-updates. Analytic; labelled "substrate backward work," **never "energy"/"N× faster"** (a numpy sim can't measure GPU energy — Spyra's caution is honoured by *scoping the claim*, not faking the number) | the 80/20 claim, scoped honestly |
| **cost-efficiency** | accuracy per unit backward work (or gap-to-BP at equal backward budget) | the Pareto position |
| **noise-degradation slope** (A7) | Δacc per unit injected σ (weight + activation), per racer | does OURS degrade more gracefully than BP under analog-style noise? |
| generalization gap | train − held-out, per racer | over/under-fit vs BP per regime |
| continual AA / BWT / FWT / forgetting **+ stability–plasticity** | GEM / CL-survey conventions (carry P3.3); plasticity (new-task acc) vs stability (old-task retention) | the continual profile (A6) |

**The linear probe stays the primary representation metric** where features are read (carry Phase 1–3); for
Phase 4 the *task accuracy* of each racer (with its own readout) is the headline, the probe a diagnostic.

## Layer C — figure catalog (declare which you emit; don't invent)

| code | figure | axes / form | the question |
| --- | --- | --- | --- |
| **GAP-CURVE** *(per-axis headline)* | gap-to-BP **vs the dialed axis** (difficulty / dim / classes …), OURS & Mono-Forward vs the BP=0 line, +Bayes envelope | does the gap open/close along this axis, and where? |
| **RACE** | the three racers' accuracy vs the dialed axis, + chance + Bayes | the raw three-way race |
| **MAP** *(the deliverable)* | gap-to-BP **heatmap over an axis pair** (e.g. difficulty × dim) | the capability surface — where the cheap brain wins/ties/loses |
| **PARETO** | accuracy vs **measured backward cost**, all racers, per regime | the 80/20 substrate claim, measured |
| **WIDTHxDEPTH** | gap-to-BP over (width × depth) at fixed budget (carry P2 F6⁺) | the Scap-collision shape (A4) |
| **CONT** | AA + BWT + forgetting bars + stability–plasticity, OURS vs BP-online vs Mono-Forward, across regimes | the continual profile (A6) — carry P3.3 |
| **NOISE-CURVE** *(A7)* | accuracy vs injected σ (weight + activation), the three racers + chance | the substrate axis — does OURS degrade more gracefully under analog-style noise? |
| **INV** | convergence (per racer — confirm each is trained-out, not just at its fixed epoch count) · dead-units · cost-meter sanity · Bayes-value sanity | health + apparatus sanity per cell |

**Worked caption (the model voice, so handed-off runs don't drift it).** Every GAP-CURVE caption ends with the
shape verdict + `(n=5, axis range, Bayes range)`, and **never** states a gap without its envelope (chance + Bayes
+ the BP baseline's own accuracy). Example:

> *"The cheap brain holds within 2 pts of tuned BP up to Bayes-error 0.15, then the gap opens to 9 pts by 0.30 —
> it captures 0.93→0.71 of the achievable as difficulty rises. (n=5, overlap 0.1–0.9, Bayes 0.02–0.34.)"*

## Layer D — the summary template (6 + 2 slots, carry from Phase 1–3)

Port the six-slot *Read* (claim → number+IQR → figures → mechanism → threats → decision). The two back slots are
re-pointed for a characterization phase:

7. **Cost-honesty** — the backward cost is **measured** (FLOPs / credit-distance / updates), not a formula; the
   Pareto position is stated with the *real* number (Spyra's caution baked in).
8. **Map-contribution** — what this rung adds to the capability map, and **what it tells Phase 5 to optimize**
   (the explicit hand-off; a rung that doesn't move the map or inform Phase 5 shouldn't have run).

No slot empty; a regime where OURS *loses* to BP fills all eight (slot 4 → why it loses there) — losing cleanly is
a result, and we do **not** tune-to-win.

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P4.0** difficulty (A1) + apparatus | GAP-CURVE, RACE, PARETO, INV (Bayes-value + cost-meter sanity) |
| **P4.1** ambient-dim (A2) | GAP-CURVE, RACE, INV |
| **P4.2** depth headroom (A3) | GAP-CURVE (vs depth) **+ MAP** (depth × difficulty), INV |
| **P4.3** width × depth (A4) | **WIDTHxDEPTH**, PARETO, INV |
| **P4.4** class count (A5) + real anchors | GAP-CURVE, RACE (+ digits/CIFAR-flat points), INV |
| **P4.5** continual (A6) | **CONT** (AA/BWT/FWT/forgetting + stability–plasticity, across regimes), INV |
| **P4.6** noise (A7) | **NOISE-CURVE** (weight + activation σ, three racers), INV |
| **P4.7** synthesis | the assembled **MAP** + **PARETO** + continual/noise profile + the Phase-5 brief |

## Grounding (what the field does — and what we adopt)

- **Gap-to-backprop, swept across difficulty/scale:** Bartunov 2018 ([1807.04587](https://arxiv.org/abs/1807.04587)) → **GAP-CURVE / MAP**.
- **Tuned-BP baseline + cost Pareto, "don't trust theoretical savings":** Spyra 2025 ([2511.01061](https://arxiv.org/abs/2511.01061)) → **PARETO** + fairness rules. *We honour the caution by scoping the claim to substrate backward-work (analytic), never GPU energy — a numpy sim can't measure the latter, and the substrate cares about the former.*
- **Difficulty = Bayes error** (synthetic with **exact** Bayes, our generator) ([2106.03357](https://arxiv.org/abs/2106.03357)) → the A1 dial + Bayes envelope. Difficulty decomposes 3 ways ([2412.02596](https://arxiv.org/abs/2412.02596)) — A1 dials one (Bayes error).
- **Noise robustness** (forward-only is hardware-noise-robust): Distance-Forward; analog-IMC ([2411.07023](https://arxiv.org/abs/2411.07023)) → **NOISE-CURVE** (A7).
- **Continual = AA/BWT/FWT/forgetting + stability-plasticity** (CL survey [2302.00487](https://arxiv.org/abs/2302.00487); GEM [1706.08840](https://arxiv.org/abs/1706.08840)) → **CONT**.
- IQR / n=5 honesty / reproducibility / the 6-slot read — carried from Phase 1–3.

> The **floor**. Adapt upward per axis; never below it. A real result needing a new figure → **add it to the
> catalog** (the next rung inherits it), never a one-off — the drift this file exists to prevent.
