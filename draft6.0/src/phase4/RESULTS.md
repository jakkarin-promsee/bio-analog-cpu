# Phase 4 — RESULTS ledger (the scalars)

> The capability-map numbers, one rung per section. Story/threats live in each `expN/experiment-N.md`; the synthesis
> lives in the [`README.md`](README.md) front door. Pre-run design: [`design.md`](design.md); reporting contract:
> [`result-format.md`](result-format.md). Cell = `[contrast (InfoNCE, two-mask) + coordination w=2] SCFF bulk +
> all-tap sleep-readout` (the Phase-3 adopted cell). Racers: **OURS** vs **genuinely-tuned BP** vs **Mono-Forward**.
> Seeds `[42,137,271,314,1729]`, median [IQR]. Cost = **backward credit-assignment work** (analytic, substrate
> units — *not* energy).

---

## P4.0 — difficulty axis (A1) · ✅ DONE 2026-06-22

Synthetic Gaussian clusters (dim 40, 4 classes, 16 clusters), difficulty = **exact** Bayes error via the dial
`overlap ∈ [0.50…1.25]` → Bayes `0.022…0.371` (informative band). 4000 train / 1500 test.

| overlap | Bayes | OURS | BP (tuned) | Mono | gap-to-BP | capture |
| --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 0.022 | 0.918 | 0.963 | 0.873 | +0.050 | 0.917 |
| 0.65 | 0.082 | 0.827 | 0.873 | 0.771 | +0.047 | 0.865 |
| 0.80 | 0.164 | 0.732 | 0.755 | 0.681 | +0.023 | 0.822 |
| 0.95 | 0.244 | 0.642 | 0.652 | 0.597 | +0.013 | 0.775 |
| 1.10 | 0.315 | 0.569 | 0.586 | 0.538 | +0.011 | 0.731 |
| 1.25 | 0.371 | 0.507 | 0.541 | 0.491 | +0.035 | 0.679 |

**Cost (backward credit-assignment work):** OURS 47k · BP 52k (@easy, shallow) → 77k (@hard, deep) · Mono 25k.
OURS/BP ratio 0.90 → ~0.61.

**Verdict:** bench **ADOPTED** (apparatus validated: exact Bayes monotone, cost meter sane, racers well-behaved).
**A1 — the gap does NOT open with difficulty;** it *closes* (achievable window shrinks), and the difficulty signal
is **capture** (monotone 0.92→0.68). OURS > Mono everywhere; OURS generalizes best until it overfits at the
near-chance cell. **80/20 cost claim NOT supported per-pass** → Phase 6 must meter the gate + sleep cadence.
Figures: `exp0/figs_p4_0/{RACE,GAP_CURVE,PARETO,INV}.png`. Full read: [`exp0/experiment-0.md`](exp0/experiment-0.md).

---

## P4.1 — ambient-dim tolerance (A2) · ✅ DONE 2026-06-22

Fixed difficulty (overlap 0.7 → Bayes **0.108, flat across dim** — apparatus ✓), sweep ambient dim `[8…500]`
(signal in a 2-D subspace, rest is nuisance). 4000 train / 1500 test.

| dim | OURS | BP (tuned) | Mono | gap-to-BP | capture |
| --- | --- | --- | --- | --- | --- |
| 8 | 0.753 | 0.877 | 0.749 | +0.122 | 0.79 |
| 16 | 0.740 | 0.863 | 0.727 | +0.119 | 0.76 |
| 40 | 0.795 | 0.830 | 0.734 | +0.035 | 0.85 |
| 100 | 0.792 | 0.821 | 0.656 | +0.029 | 0.85 |
| 250 | 0.782 | 0.799 | 0.489 | +0.020 | 0.83 |
| 500 | 0.763 | 0.741 | 0.411 | **−0.029** | 0.80 |

**Cost @dim 500:** OURS ~106k · BP ~155–232k · Mono ~54k (backward credit-assignment work).

**Verdict: OURS's FIRST WIN.** As nuisance dim grows, OURS holds (~0.79) while BP gently declines (budget-squeezed
first layer) and **Mono-Forward collapses toward chance** (overfit, gen-gap 0.59). **OURS crosses *above* tuned BP
by dim 500** (gap −0.029, IQR all-negative) — *cheaper and more accurate* there. Mechanism: contrast+layernorm
down-weights non-discriminative dims for free. Substrate-relevant (wide analog crossbars). **Mono-Forward flagged
high-D-unsafe.** Crossover dim is difficulty-dependent → MAP candidate. Full read: [`exp1/experiment-1.md`](exp1/experiment-1.md).

---
## P4.2 — depth headroom (A3) × difficulty · ✅ DONE 2026-06-22

Headroom task (`make_tierb`, 64 clusters), difficulty dial = overlap `[0.4…1.2]`, L=8. Instrument = **per-layer
probe slope** (depth-composition, not task accuracy). OURS w=2 vs OURS w=1 (control) vs GD-hidden (ceiling). 5 seeds.

| overlap | GD slope | OURS w=2 slope | OURS w=1 slope | w2_top − GD_top | headroom? |
| --- | --- | --- | --- | --- | --- |
| 0.40 | +0.043 | +0.010 | −0.010 | −0.173 | YES |
| 0.60 | +0.016 | +0.012 | +0.001 | +0.009 | YES |
| 0.80 | +0.004 | +0.010 | +0.002 | +0.070 | borderline |
| 1.00 | −0.003 | +0.008 | +0.002 | +0.097 | flat |
| 1.20 | −0.004 | +0.004 | −0.000 | +0.076 | flat |

**Verdict: depth-composition GENERALIZES** (not the feared PARTIAL). OURS w=2 slope **positive across the whole
band** (IQR disjoint from 0); **w=1 never composes** (coordination is the lever); **GD loses headroom by overlap
1.0**. OURS and BP compose in **complementary regimes** — GD wins easy, **OURS out-composes BP in the hard/low-
headroom regime** (top-layer crossover ≈ overlap 0.6). Caveat: probe (representation), not task accuracy; w=2 shows
a mild inverted-U at easy+deep (P3.2's w=4 fixes it → window-size is a Phase-5 difficulty-dependent knob). Full
read: [`exp2/experiment-2.md`](exp2/experiment-2.md).

---
## P4.3 — width × depth (A4) · ✅ RE-RUN + EXTENDED 2026-06-24  *(+energy-Σh² baseline · last-layer readout · L10/L12 · W64 control)*

Iso-weight-budget shape sweep (B ≈ 23.5k = canonical L4/W64), depth `[2…12]` (wide-shallow → narrow-deep), two
regimes: flat (`make_gauss`) and headroom (`make_tierb`). **Three racers: OLD (energy Σh², the Phase-1/2 wall cell)
vs OURS (contrast+w2) vs tuned BP.** 5 seeds. **Headline accuracy = the LAST-LAYER readout** (the realistic GD-head
position; all-tap masks the wall by reading the early layers → A4 not comparable to all-tap A1/A2/A5). Plus a
**fixed-width W64 control** (L4→12) to separate depth-decay from the iso width-shrink.

| shape | flat OLD | flat OURS | flat BP | head OLD | head OURS | head BP | head gap | cost OLD/OURS/BP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L2/W109 | 0.760 | 0.783 | 0.837 | 0.487 | 0.533 | 0.528 | −0.010 | 24k / 40k / 52k |
| L3/W79 | 0.703 | 0.759 | 0.830 | 0.459 | **0.559** | 0.519 | **−0.039** | 21k / 31k / 65k |
| L4/W64 | 0.680 | 0.731 | 0.831 | 0.441 | 0.557 | 0.533 | **−0.036** | 19k / 34k / 77k |
| L6/W48 | 0.578 | 0.672 | 0.830 | 0.369 | 0.551 | 0.536 | −0.013 | 17k / 31k / 99k |
| L8/W40 | 0.461 | 0.666 | 0.841 | 0.337 | 0.481 | 0.523 | +0.046 | 16k / 29k / 124k |
| L10/W34 | 0.443 | 0.627 | 0.829 | 0.334 | 0.441 | 0.524 | +0.083 | 14k / 27k / 149k |
| L12/W30 | **0.337** | 0.567 | 0.819 | **0.307** | 0.434 | 0.526 | +0.094 | 14k / 25k / 169k |

**Fixed-width control (W64, the decay-vs-width test):** headroom OURS **0.557→0.449** (L4→L12), flat OURS
**0.731→0.647** — **OURS droops with depth even at constant width** ⇒ the dip is **DECAY**, not the iso width-shrink
(which adds only ~0.02–0.03 extra at L8–L12). Per-layer profile at L12/W64: OURS **builds to layer ~4–5** then decays.

**Verdict: A4 = WIN (cost), unchanged.** Backward cost **flat in depth** for both forward-only methods (OLD ~14–24k,
OURS ~25–40k) while BP grows **linearly** (52k→169k) — narrow-deep ~free for OURS/OLD, **up to 6.8× costlier for BP**
(depth-gated 1.3×→6.8×). **The energy baseline makes the wall legible:** OLD collapses monotonically (flat 0.76→0.34,
headroom 0.49→0.31). **Contrast flattens the wall but does not abolish it, and the cause is DECAY not width:** OURS
composes to ~L3–L5 (beats BP L2–L6 on headroom), then decays (loses to BP L8–L12) — *even at fixed W64*. The
context-sharing buys ~5 useful layers (energy buys zero) but not unbounded depth → the deployed **all-tap/boosting
readout is load-bearing** and a single deep head is the wrong design. (Caveat: fixed `ep=25/lr=0.03` all depths →
depth-scaled training is an untested P5 knob before calling the decay intrinsic.) Full read: [`exp3/experiment-3.md`](exp3/experiment-3.md).

**Follow-up — P4.3-decay (why it decays; width is NOT the lever) · ✅ 2026-06-24.** Widening each layer with depth
(`widen` W=64+16·l, up to W240 @L12) **does not fix the decay** — fix64 and widen converge by L12 (headroom 0.449
vs 0.441). Mechanism diagnostics refute capacity: **dead-unit fraction ≈ 0** at every layer, and effective rank
declines but widen carries **higher rank (18.7 vs 12.3 @L12) at identical accuracy** → the decay is **local-objective
drift off the class manifold past ~layer 5**, not dead units or capacity. A **mixed flat+headroom** task (iso-budget,
+tuned BP) confirms it: flat-good (0.71→0.51) / headroom-weaker (0.47→0.34), and the flat subtask (probe-solved by
layer 2–4) is **corrupted by the deeper layers** (probe ~0.67→0.51) — while **tuned BP holds the flat subset flat
across depth (~0.75)**, so the corruption is OURS-specific. **Verdict: useful composition ≈ 5 layers; the fix is
preservation (all-tap/boosting — vindicated — or residual skips), not width.** Full read: [`exp3/experiment-3-decay.md`](exp3/experiment-3-decay.md).

---
## P4.4 — class count (A5) + real anchors · ✅ DONE 2026-06-22

Synthetic: fixed 40-cluster geometry, only labels re-partitioned, C ∈ [2,4,10,20], exact Bayes. Real anchors:
digits (64-D, 5 seeds) + CIFAR-flat (3072-D, 1-seed sanity). OURS / tuned BP / Mono.

| C | OURS | BP | Mono | gap-to-BP | capture | OURS−Mono |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.854 | 0.917 | 0.753 | +0.063 | 0.76 | +0.097 |
| 4 | 0.739 | 0.881 | 0.670 | +0.143 | 0.70 | +0.069 |
| 10 | 0.655 | 0.881 | 0.640 | +0.226 | 0.67 | +0.015 |
| 20 | 0.647 | 0.881 | 0.661 | +0.234 | 0.68 | −0.015 |

**Real anchors (10-class):** digits gap **+0.027** (OURS 0.960) · CIFAR-flat +0.090 (OURS 0.304, the wall).

**Verdict: competitive-but-trails (like A1); gap is difficulty-gated, not count-gated.** Synthetic gap widens
(+0.06→+0.23, saturating ~C10) and OURS's edge over Mono erodes (Mono ties by C20) — but **real digits (10-class)
gap is only +0.027**, so the synthetic widening is harshness, not a "many-class penalty." Capture plateaus ~0.67.
Not a win axis; Mono is the stronger reference at high class count. Full read: [`exp4/experiment-4.md`](exp4/experiment-4.md).

---
## P4.5 — continual (A6) across difficulty · ✅ DONE 2026-06-22  *(home turf — THE win)*

Class-incremental stream (5 tasks of 2), validated P3.3 harness, synthetic at swept difficulty + digits anchor. 3 seeds.

| regime | OURS-sleep AA | OURS-sleep BWT | online-BP BWT | no-sleep BWT |
| --- | --- | --- | --- | --- |
| ov0.4 | 0.710 | −0.122 | −0.929 | −0.88 |
| ov0.7 | 0.583 | −0.176 | −0.876 | −0.86 |
| ov1.0 | 0.435 | −0.183 | −0.826 | −0.84 |
| **digits (home)** | **0.954** | **−0.017** | −0.992 | −0.95 |

**Verdict: THE win, robust across difficulty.** OURS+sleep forgets almost nothing (BWT −0.02 to −0.18) at every
difficulty while online-BP catastrophically forgets (−0.83 to −0.99); no-sleep rots (sleep is the mechanism).
Digits reproduces P3.3 exactly (0.954/−0.017). AA falls with difficulty (harder task) but BWT stays excellent —
the win doesn't erode off the home config. The architecture's reason for being. → P6 optimizes the sleep cadence +
gate. Full read: [`exp5/experiment-5.md`](exp5/experiment-5.md).

---
## P4.6 — noise robustness (A7) · ✅ DONE 2026-06-22  *(an HONEST NEGATIVE)*

Train clean, inject multiplicative Gaussian weight noise at eval, sweep σ. Flat make_gauss, 5 seeds, 5 draws/cell.

| σ | OURS ret | BP ret | Mono ret |
| --- | --- | --- | --- |
| 0.10 | 0.987 | 0.992 | 0.989 |
| 0.20 | 0.935 | 0.974 | 0.946 |
| 0.40 | **0.754** | **0.875** | 0.786 |

**Verdict: hypothesis REFUTED (this noise model).** OURS is **not** more weight-noise-robust than tuned BP — it's
the **least** robust (retention 0.75 vs BP 0.88 at σ=0.4); both forward-only methods (OURS, Mono) degrade more than
BP. Likely cause: **per-sample layernorm** (A2's robustness mechanism) doesn't damp weight-*direction* noise → A2
win and A7 loss **share a cause** (a real tradeoff). **Scope:** eval-time noise on a clean-trained model ≠ the
substrate regime (online learning *with* noise = hardware-aware, where forward-only's claim lives) — **untested,
the proper P6 follow-up.** Don't claim noise-robustness yet. Full read: [`exp6/experiment-6.md`](exp6/experiment-6.md).

---
## P4.7 — synthesis: the capability map + hand-off brief · ✅ DONE 2026-06-22

The map: **WIN** A6 continual (decisive), A2 ambient-dim, A3 depth-composition, A4 depth-is-cheap (80/20 depth-gated);
**TRAIL** A1 difficulty, A5 class-count (difficulty-gated, real-data kinder); **NEGATIVE** A7 eval-time noise
(layernorm tradeoff; train-with-noise untested). Verdict: a **substrate-native continual learner, not a static-
accuracy competitor.** Synthesis: [`README.md`](README.md); assembled map:
`figs_summary/CAPABILITY_MAP.png`. **Phase 5 closes out the SCFF depth decay; Phase 6 = optimize the continual win
(sleep cadence + Ch7 gate).** PHASE 4 CLOSED.
