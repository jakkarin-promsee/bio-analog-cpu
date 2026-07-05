# Phase 11 — the limit map: the deep story (report)

> The narrative behind [`README.md`](README.md) and [`RESULTS.md`](RESULTS.md). Phase 11 took the P9-frozen
> two-brain neocortex — the object Phase 10 validated (S14) — off the 8×8-digit / 40-D bench and onto **real data,
> real streams, cross-dataset streams, and scale.** The instrument is the P10 fair-fight discipline; the posture is
> the author's: *"if everything fails, let them attack my math, not my missing evidence."* This report walks the
> rungs in order, because each read leans on the last.

---

## 0 · The bench (P11.0) — building the arena, honestly

The one deliberate network session landed seven arenas via reliable routes (Zalando GitHub, figshare, UCI), dodging
the dead openml *API*: digits (8×8), MNIST/Fashion/CIFAR-gray (784), gas (128-D, 6 classes, batches 1–10),
HAR (561-D, 6 classes, 30 subjects), electricity (8-D, 2 classes, chronological), covertype (54-D, 7 classes, file
order). Covertype's class imbalance is **10:1** → balanced accuracy is mandatory there.

Three bench artifacts matter for everything after:

1. **`freeze_content` is bit-exact.** The grid-4 object reproduces the P9 freeze to dBWT = dAA = dGD = 0. *We are
   measuring the exact frozen object* — not a re-implementation.
2. **The noise-σ direction-killer, caught.** P10's noised domain adds σ=0.6 *absolute* on RMS≈0.486 inputs (σ/RMS =
   1.239). The naïve "0.6×RMS" shorthand would have made MNIST's noised domain ~2× milder — confounding the exact
   channel that drives the retention differentiator. Pinned by equivalence: σ_rung = (0.6/RMS_P10)·RMS_rung, ratio
   1.239 on every arena.
3. **The economy does NOT improve with scale.** Walking the meter's own op-counts, GD-share vs W = {0.21, 0.34,
   0.53} for W ∈ {64,128,256}: it **rises**, because the SLDA solve term scales ~O((L·W)³). The temp2 pre-registered
   guess ("economy improves with scale," from an O(D·C+D²) formula whose D was the wrong variable) is refuted at the
   meter source — the recurring direction-killer, caught before a single scaling run.

---

## 1 · The decomposition (P11.1) — "isn't this just SLDA?"

This is the strike every serious reviewer throws, and the run the professor pitch wanted in hand. The namer is
literature (SLDA); until Δbulk = (bulk→namer) − (proj→namer) is measured, the architecture claim is open.

A pre-run diagnostic reframed the whole rung. **Digits are near-linearly-separable** (raw-SLDA 0.950): a linear
namer already saturates, so the bulk *cannot* add there — and a digits-only Δbulk would have banked the misleading
"the bulk is worthless." So the honest measurement sweeps arenas of increasing nonlinearity:

| arena | proj→namer (no bulk) | random-frozen reservoir | bulk→namer | Δbulk |
| --- | --- | --- | --- | --- |
| synthetic home (nonlinear) | **0.172** (≈chance) | 0.389 | **0.589** | **+0.417** |
| MNIST-40 (moderate) | 0.770 | — | 0.778 | +0.008 |
| digits (near-linear) | 0.950 | 0.902 | 0.936 | −0.014 |

The reading is a **decomposition of attribution**, and it is more honest — and more useful — than a flat
"confirmed":

- The SCFF **bulk is the nonlinear feature learner.** Where a linear head is at chance (the synthetic home) the bulk
  lifts it by **+0.417**, and it beats a *random* 12-layer reservoir (0.589 vs 0.389) → the lift is *learned SCFF
  structure*, not merely "12 nonlinear layers exist." Where a linear head already saturates (digits) the bulk is
  correctly redundant.
- The continual **safety is the closed-form namer + gate + sleep, not the bulk.** proj→namer forgets no more than
  bulk→namer (gauntlet worst-BWT 0.000 vs −0.016 on digits; 0.000 vs −0.096 on MNIST). The safety the object is
  famous for is largely the SLDA-plus-gate-plus-sleep machinery — the strike lands here, and we say so.
- On **iid noise** at matched clean accuracy (digits) the bulk wins **+0.086** absolute (synth +0.215) — the P6
  noise-augmentation earning its keep.

So the pitch answer is precise and defensible: *the safety largely is SLDA (we measured it); the bulk is the
nonlinear learner, and on data a linear head can't crack it is decisive and beats a random reservoir.* Kill
criterion (i) did not fire. Figure: `exp1/figs_p11_1/DECOMP.png`.

---

## 2 · The MNIST rung (P11.2) — does the frozen recipe survive real data, and scale?

The P10.3 gauntlet, rebuilt in native MNIST-784 space → porthole, in both switch regimes, both arms, vs an ER
re-tuned per arm on the disjoint seed-7 stream.

| arm | regime | OURS AA | ER AA | OURS worst-BWT | ER worst-BWT | OURS ret | ER ret |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (D40) | rapid | 0.258 | 0.448 | −0.080 | −0.143 | 0.216 | 0.221 |
| A (D40) | **long** | 0.284 | 0.427 | **−0.012** | −0.196 | **0.223** | 0.102 |
| B (D80) | rapid | 0.390 | 0.541 | −0.011 | −0.113 | 0.298 | 0.210 |
| B (D80) | **long** | 0.421 | 0.514 | **−0.046** | −0.162 | **0.314** | 0.105 |

The bet **holds on real data**: OURS wins continual safety in every cell (decisively on the long regime, the E8
primary — ~4–16× less forgetting), wins retention on long blocks, and is order-invariant (|fwd−rev| 0.003/0.011),
while static accuracy trails (continual-not-static, the porthole discarding MNIST structure). **Arm B scales** —
D40→D80 lifts AA (0.284→0.421) and retention (0.223→0.314) with safety intact: the recipe transfers upward. The
Split-MNIST anchor ran at porthole-40 (not the published raw-784), so it sits below the literature band — a config
note (owed), not an ER-implementation failure. Figure: `exp2/figs_p11_2/STREAM_mnist.png`.

---

## 3 · The real-world streams (P11.3) — nature's own drift

The pinned channel is **prequential balanced accuracy** (pre-update, every learner incl. no-change; R2). Roster:
OURS-A/B vs the **stronger** of {ER-matched, ER-bigbuf}, plus sgd-linear, first-block-frozen, and the mandatory
no-change baseline.

| stream | OURS-A | OURS-B | stronger-ER | no-change | verdict |
| --- | --- | --- | --- | --- | --- |
| **gas** (6-cls, sensor drift) | **0.789** | **0.856** | 0.756 | 0.605 | **WIN** |
| har (6-cls, by-subject) | 0.686 | 0.820 | 0.754 | 0.950 | FLOOR (field +0.07) |
| electricity (2-cls, chrono) | 0.606 | 0.596 | 0.687 | 0.836 | FLOOR (field +0.08) |
| covertype (7-cls, file order) | 0.471 | 0.472 | 0.542 | 0.646 | FLOOR (field +0.07) |

**Gas is the headline, and it is a genuine win.** On the time-ordered gas-sensor-drift stream — a famous real
benchmark (Vergara 2012) where recognition degrades as the sensors age — the **frozen recipe, untouched, is the
strongest online learner in the room**: OURS-A 0.789 ≥ the stronger per-arena-tuned ER 0.756, and beats the
persistence baseline by +0.184 (so the cell is informative, not a floor). Arm B (native-128) lifts it to **0.856** —
the porthole was costing ~0.07 and the scaling recipe recovers it. The mechanism is the phase's spine: sensor aging
is a *coherent covariate shift*, exactly the drift the SCFF bulk + sleep re-anchoring was built to ride while the
closed-form namer never catastrophically forgets.

**The streaming canon FLOORs — honestly, as pre-registered.** On HAR, electricity, and covertype **no learner beats
the no-change baseline** (0.950 / 0.836 / 0.646). This is the ELEC2 label-autocorrelation trap (Souza 2020, D2):
these streams have such strong label persistence that "predict the previous label" is near-unbeatable by any model
that actually looks at the features — ours *or* ER. The cells are grey and **two-sided**: inside the floor the
stronger ER leads OURS by ~0.07 (the anti-hype guard is not an anti-loss shield — the field is ahead on these, and
the map says so). This cleanly separates **drift-difficulty** (gas: real, information-bearing, OURS wins) from
**data-difficulty** (autocorrelated labels: persistence wins, everyone floors) by measurement.

One honest limit surfaced: the near-zero worst-BWT of the synthetic gauntlet **does not carry to real drift** —
OURS-A worst-point BWT is genuinely negative (gas −0.333, har −0.233, electric −0.149, covtype −0.097), the SLDA
frame going stale between sleeps as nature drifts. Reported, not hidden (and on gas under-powered per R8 — batches
4/5 carry < 100 eval samples — so the *prequential accuracy* is the headline read, not the worst-BWT).

---

## 4 · The cross-dataset gauntlet (P11.4) — robustness to the TYPE of data

The author's aggressive ask: not "same data plus a transform" but **different datasets entirely** —
MNIST→Fashion→CIFAR-gray as ONE class-IL **30-way** stream (the field's 5-Datasets protocol at our scale, but
class-IL, harder than their task-IL), one shared source-1-fit porthole (the honest gain-shock read).

| arm | final-30 | order \|Δ\| | worst-ret | ER worst-ret | mnist / fashion / cifar-gray | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| A (D40) | 0.338 | 0.007 | 0.415 | 0.534 | 0.421 / 0.461 / 0.125 | TYPE-SCOPED |
| B (D80) | 0.440 | 0.004 | **0.581** | 0.551 | 0.588 / 0.581 / 0.143 | **TYPE-ROBUST** |

Three findings. **(1) All three data types stay alive** — no block collapses toward the 0.033 chance floor; the
weakest, CIFAR-gray, holds ~4× chance and never dies; the CBRS LUT keeps every type represented through 30-way
growth. **(2) OURS is order-invariant even across a change in the *kind* of data** (|AA(fwd)−AA(rev)| = 0.007/0.004) —
the P10.3 order-invariance surviving the hardest ordering stress in the phase, a direct consequence of the namer
being closed-form (no gradient path a data-type ordering can bias). **(3) The scaling recipe flips the retention
verdict**: at the frozen porthole (Arm A) worst-point retention 0.415 trails the field's ER 0.534 (TYPE-SCOPED — all
alive but retention behind); the scaled instance (Arm B, D80) recovers to 0.581 ≥ ER 0.551 (TYPE-ROBUST). The
namer's Gram condition number was instrumented (the D-research Q8 risk) and stayed **bounded** (~1–2e8, no blow-up).
The owed leg: Arm B at the full recipe D=160 (descoped to D=80 for the overnight budget — the F5 einsum→GEMM
apparatus fix).

---

## 5 · The LIMIT-MAP + what it means (P11.9)

_[The money figure: arenas × capability channels, win/tie/loss/FLOOR + numbers + the Δbulk overlay. The honest
deployment envelope of the committed object, for the pitch and the analog layer.]_

---

## Threats to validity (carried + P11-new)

- **Projection loss** dominates absolute accuracy: the →40 porthole discards structure (Arm B's larger-D instances
  bound how much, per arena).
- **Anchor un-validated at raw-784** (owed); the noise retention *ratio* is clean-baseline-confounded (reported as
  absolute noisy accuracy).
- **Descopes named, not faked:** Yearbook/BloodMNIST/CIFAR-100 (openml API down), P11.5–P11.8 (single-session
  budget), the D=160 cross-dataset Arm B (the F5 GEMM apparatus fix). The meter is behavioral (relative-pJ,
  ADC-centred, NOT SPICE).

*Up:* [draft context](../../CLAUDE.md) · *front door:* [`README.md`](README.md) · *numbers:* [`RESULTS.md`](RESULTS.md).
