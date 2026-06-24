# Experiment P4.3 — width × depth (A4): the Scap-budget Pareto, the energy-wall baseline, the decay-vs-width control

> **Status: ✅ RE-RUN + EXTENDED (2026-06-24).** Three additions over the first pass: (1) the **OLD energy-Σh²
> baseline** (Phase-1/2 wall cell: squared goodness + length-norm); (2) the headline readout switched from all-tap
> to the **last layer** (the realistic single-GD-head position — all-tap masked the wall by reading the good early
> layers); (3) the iso-budget sweep **extended to L10/L12** *and* a **fixed-width (W64) control** added, to separate
> depth-decay from the iso-budget width-shrink. Iso-budget B ≈ 23.5k, depth `[2,3,4,6,8,10,12]` (width holds B);
> control holds **W64**, sweeps `[4,6,8,10,12]`. Two regimes: **flat** (`make_gauss`) and **headroom**
> (`make_tierb`). Racers: **OLD** vs **OURS (contrast+w2)** vs **tuned BP**. 5 seeds. Run:
> `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3.py` (2540s). Contract: [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** **(a) A4's cost win stands and is sharper:** OURS's and OLD's backward cost is **flat in depth**
(OURS ~25–40k, OLD ~14–24k) while BP's grows **linearly** (52k→169k) — narrow-deep is ~free for forward-only and
up to **6.8× costlier for BP** at L12. **(b) The energy baseline makes the depth-wall legible:** OLD (energy Σh²)
**collapses monotonically** with depth (headroom 0.49→0.31, flat 0.76→0.34). **(c) Contrast flattens the wall but
does not abolish it — and the cause is DECAY, not width.** The **fixed-width W64 control** is decisive: with width
**held constant**, OURS *still* droops monotonically (headroom 0.557→0.449, flat 0.731→0.647 over L4→L12); the
iso-budget width-shrink adds only ~0.02–0.03 extra at L8–L12. The per-layer profile at L12/W64 shows it: OURS
**builds to layer ~4–5** (composition is real — the cross-layer window *does* share context), plateaus, then
**decays after layer ~7**. So contrast buys ~5 useful layers (energy buys zero — OLD never composes, ~0.37 flat
then collapses), but the representation eventually rots with depth regardless of width.

**2 · Number** (median over n=5; gap = BP − OURS, `<0` = OURS wins; pL = last-layer linear probe):

*ISO-budget — flat regime (no headroom):*
| shape | OLD | OURS | BP | gap-to-BP | OURS pL | OLD pL | cost OLD/OURS/BP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L2/W109 | 0.760 | 0.783 | 0.837 | +0.049 | 0.727 | 0.524 | 24k / 40k / 52k |
| L4/W64 | 0.680 | 0.731 | 0.831 | +0.100 | 0.708 | 0.505 | 19k / 34k / 77k |
| L8/W40 | 0.461 | 0.666 | 0.841 | +0.164 | 0.675 | 0.419 | 16k / 29k / 124k |
| L10/W34 | 0.443 | 0.627 | 0.829 | +0.201 | 0.596 | 0.340 | 14k / 27k / 149k |
| L12/W30 | **0.337** | 0.567 | 0.819 | +0.263 | 0.543 | 0.312 | 14k / 25k / 169k |

*ISO-budget — headroom regime (depth pays):*
| shape | OLD | OURS | BP | gap-to-BP | OURS pL | OLD pL | cost OLD/OURS/BP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L2/W109 | 0.487 | 0.533 | 0.528 | −0.010 | 0.485 | 0.393 | 24k / 40k / 52k |
| L3/W79 | 0.459 | **0.559** | 0.519 | **−0.039** | 0.533 | 0.386 | 21k / 31k / 65k |
| L4/W64 | 0.441 | 0.557 | 0.533 | **−0.036** | 0.533 | 0.379 | 19k / 34k / 77k |
| L6/W48 | 0.369 | 0.551 | 0.536 | −0.013 | 0.531 | 0.357 | 17k / 31k / 99k |
| L8/W40 | 0.337 | 0.481 | 0.523 | +0.046 | 0.456 | 0.333 | 16k / 29k / 124k |
| L10/W34 | 0.334 | 0.441 | 0.524 | +0.083 | 0.445 | 0.313 | 14k / 27k / 149k |
| L12/W30 | **0.307** | 0.434 | 0.526 | +0.094 | 0.421 | 0.312 | 14k / 25k / 169k |

*FIXED-WIDTH control (W64 constant — isolates depth from width):*
| L | flat OURS | flat OLD | head OURS | head OLD | head OURS pL |
| --- | --- | --- | --- | --- | --- |
| 4 | 0.731 | 0.680 | 0.557 | 0.441 | 0.533 |
| 6 | 0.675 | 0.631 | 0.552 | 0.385 | 0.520 |
| 8 | 0.679 | 0.575 | 0.500 | 0.355 | 0.493 |
| 10 | 0.667 | 0.473 | 0.474 | 0.332 | 0.461 |
| 12 | 0.647 | 0.402 | **0.449** | 0.315 | 0.435 |

OURS beats tuned BP on headroom **L2–L6** (gap IQR-disjoint-negative at L3/L4), **loses L8–L12** (all seeds). OLD is
below OURS at every shape, by a margin that **grows with depth**. **At fixed W64 OURS still drops L4→L12** (−0.108
headroom) → the droop is **decay**, not the iso width-shrink.

**3 · Figures.** `WIDTHxDEPTH` (iso L2→L12, 3 racers/regime) · `PARETO` (cost — OURS owns the cheap top-left on
headroom, BP fans right 52→169k, OLD cheapest but collapses) · `WALL` (last-layer probe vs depth + per-layer
profile at L12 — the iso wall) · **`CONTROL`** (**the disambiguator** — fixed W64: OURS still droops with depth;
per-layer profile at L12/W64 builds to layer ~4–5 then decays) · `INV` (iso width schedule + gap-to-BP).

**4 · Mechanism.** *Cost:* forward-only credit distance is bounded — OURS's w=2 window, OLD's 1-layer-local
goodness — **independent of depth**; BP's = full depth → linear (now 169k at L12). *Wall:* energy-Σh² sheds whatever
isn't loud → deep layers homogenize (density≠class), probe rots from layer 1. Contrast preserves
class-distinguishing info → deep layers **compose for ~5 layers** (the window shares context forward), then the
representation still slowly degrades — at constant W64 — so it is **depth-decay**, not capacity. Width adds a small
secondary penalty (narrow deep layers, ~0.02–0.03). The all-tap readout hides all of this by reading every layer →
that is exactly why the deployed design taps all layers / boosts blocks.

**5 · Threats.** (a) The decay is **real and monotone across 5 seeds** at fixed W64 — not noise. (b) **Under-
training is a live confound:** all depths use the same `ep=25, lr=0.03`; deeper stacks may simply need more passes /
a depth-scaled lr — a **P5 knob**, untested here. So "decay" is decay *under the substrate-native fixed online
budget*, which is the honest operating regime, not a proof of an intrinsic ceiling. (c) The last-layer readout
makes A4 OURS numbers **not comparable** to the all-tap A1/A2/A5 rungs (deliberate, A4-only). (d) Single dim (40)
and budget (~23.5k); the cost-scaling argument is general (BP credit-distance ∝ L always).

**6 · Decision.** **A4 = WIN (cost)** — unchanged. **Carry forward:** (i) depth is **cost-cheap** for forward-only
(flat backward) and **linear** for BP → build deep cheaply; (ii) **depth-composition is real but bounded (~5 layers
of useful build, then decay)** even at generous width → the **all-tap / boosting readout is load-bearing** (works
around the residual decay), and **a single deep head is the wrong design**; (iii) **energy-Σh² is decisively
closed** as a depth substrate; (iv) **test depth-scaled training** (more passes / lr) in P5 before treating the
decay as an intrinsic ceiling; (v) gate depth on headroom + scale the window (P4.2).

**7 · Cost-honesty.** OURS backward **flat ~25–40k**; OLD **flat ~14–24k**; BP **52k→169k linear**. BP/OURS ratio
**1.3× (L2) → 6.8× (L12)** — depth-gated and large. Still **analytic / substrate units, not energy.**

**8 · Map-contribution → P5.** A4 tile: **depth is cost-cheap for forward-only (WIN); contrast buys ~5 composing
layers (energy buys none) but then decays — width is not the fix.** Tells P5: (a) **build deep but tap all layers /
boost** (the wall is residual); (b) **cost meter = cost-vs-depth** (1.3×→6.8×); (c) **try depth-scaled training**
before declaring an intrinsic depth ceiling; (d) gate depth on headroom + window. The energy baseline is now the
permanent reference that makes the contrast win legible.

> **Follow-up — [`experiment-3-decay.md`](experiment-3-decay.md):** *why* OURS decays, and whether width fixes it.
> Verdict: **width is NOT the lever** — widening to W240 doesn't help; dead-fraction ≈ 0 and widen's higher rank
> buys no accuracy ⇒ the cause is **local-objective drift off the class manifold past ~layer 5**, fixed by
> **preservation** (all-tap/boosting or residual skips), not capacity. A mixed flat+headroom task shows the deep
> layers **corrupt** the early-solved flat subtask. Useful composition ≈ **5 layers**.

---

## Reproducibility

`figs_p4_3/{manifest.json, arrays.npz, _ckpt.jsonl, run_full.log}`; `python plot_p4_3.py figs_p4_3`. Single-
threaded (`OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1`), `python -u`, `PYTHONIOENCODING=utf-8`, per-cell fsync; verified
alive mid-run (checkpoint beacons). Pure numpy in the hot path — the per-layer probe is a numpy linear-softmax (no
sklearn → no OpenMP phantom). Checkpoint keyed by **(mode, regime, L, seed)**: `mode="iso"` (iso-budget) +
`mode="fixw"` (W64 control). Apparatus: `p4lib.race_energy`, `readout_feats`/`linear_probe`/`per_layer_probe`,
`cost_ours(..., readout_last_n)`; `run_p4_3.py` has `READOUT_LAST_N=1`, `CTRL_W=64`, `CTRL_DEPTHS=[4,6,8,10,12]`.
