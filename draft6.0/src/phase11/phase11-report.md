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

## 5 · Does it scale? (P11.5–P11.7) — the strike-3 trilogy

Strike 3 ("one width, one depth, one input dim, one class count") gets three answers.

**Accuracy/hardness (P11.5 r2/r3).** Fashion (r2) holds the safety bet — OURS worst-BWT −0.021/−0.057 vs ER
−0.146/−0.141 (≈2–7× less forgetting) while ER leads absolute accuracy (the continual-not-static identity, now on a
harder recognizable dataset); Arm B recovers retention (0.401 > ER 0.380). CIFAR-gray (r3) is the honest **FLOOR** —
the joint-BP ceiling itself is only 0.199, so grayscale-cropped CIFAR through a 40-D porthole is at the resolution
floor and every channel there is grey, not a parity claim. The far edge of the map is where it should be.

**Memory (P11.5 crossover).** The class-count read is the cleanest scaling result in the phase: at C=10 (Split-MNIST)
a byte-matched ER out-retains OURS (0.423 vs 0.354), but at C=20 (MNIST+Fashion) ER's fixed replay buffer **dilutes
to ≈0 retention (0.014)** while OURS's prototype+Gram namer holds (0.233) — a **+0.219** flip. The gradient-free
namer keeps an exact per-class mean + a shared covariance, so per-class fidelity is C-independent; a fixed replay
buffer splits its budget O(1/C) and collapses. The honest counterweight: on raw *bytes* the all-tap F×F covariance
(F=768) is a large fixed cost, so the memory-byte crossover is beyond any realistic class count — the namer's win is
retention fidelity per class, not byte compactness.

**Economy (P11.6 capacity).** The pre-registered test lands: the **bench-pinned GD-share shape is CONFIRMED** —
measured [0.17, 0.28, 0.45] tracks the meter-derived [0.21, 0.34, 0.53] as W ∈ {64,128,256}. The economy does *not*
improve with scale (the SLDA solve ~O((L·W)³) makes the namer a growing energy fraction — the temp2 direction-guess
refuted at the run, not just the formula). Capacity *does* buy the accuracy gap back (0.42→0.50 over W, 0.39→0.51
over D), at that rising GD-share cost. And the **analog substrate advantage grows** with width (5.4→7.4×) — the
crossbar prices the extra bulk MACs near-free, so the compute-in-memory edge *widens* at scale (the chip's best
sentence); safety holds at every width and dim.

**Real-time (P11.7 throughput).** On the gas stream the retention-tuned ER-strong (wide net + replay) costs more
FLOPs/sample than the frozen D40 recipe, so at a shared budget ER drops 32%/31%/8% of the stream (raw-FLOP / digital
/ analog) while OURS keeps up — **branch (i), the regime win.** Honesty demands the caveat: this *inverts* P10's
synthetic-home measurement (where OURS used more FLOPs than a cheap ER), so the real-time economy is
arena/opponent-dependent, not universal — and the map says so.

---

## 6 · The LIMIT-MAP + what it means (P11.9)

The money figure (`exp9/figs_p11_9/LIMIT_MAP.png`) is 8 arenas × 5 capability channels, every cell win / tie / loss /
FLOOR with its number. Read down the channels, the object's identity is unmistakable and honestly bounded:

- **Wins (teal):** continual **safety** (worst-BWT) on every non-floor gauntlet arena (mnist, fashion); **retention**
  on mnist-long; **order-invariance** everywhere it is measured (mnist, xdata, gas — |Δ| ≤ 0.043, even across data
  *types*); **gas accuracy** (the real-world headline, beating a per-arena-tuned ER and persistence); and the
  **scaling reads** (pinned economy shape, growing substrate factor, the C=20 retention crossover, the gas
  throughput regime win) that live in the SCALING/CROSSOVER panels rather than the arena grid.
- **Losses (pink):** static **accuracy** on mnist and fashion (continual-not-static — P4/P10.5 re-confirmed at
  scale); **retention** on fashion (Arm A) and the 30-way xdata stream (recovered by Arm B in both cases). The object
  is not a static-accuracy competitor and the map never pretends otherwise.
- **Floors (grey):** CIFAR-gray (a native-resolution floor); HAR / electricity / covertype (the ELEC2
  label-autocorrelation trap — persistence unbeatable, the field floors alongside OURS but leads by ~0.07). The far
  and autocorrelated edges of the map are grey, and grey is not parity.

The **Δbulk overlay** (P11.1) keys the whole map to a mechanism: the bulk earns its place where the data is nonlinear
(the synthetic home +0.417, real sensors), and the continual *safety* is the closed-form namer + gate + sleep, not
the bulk. So the honest deployment envelope for the pitch and the analog layer is: **a substrate-native continual
learner that wins safety, noise-robustness, order-invariance, real information-bearing drift (gas), and every
scaling read of the economy/substrate — while trailing on static accuracy and flooring where the data is at its
resolution or persistence limit.** The wins are real; the losses and floors are mapped, not hidden. That was the
deliverable.

---

## Threats to validity (carried + P11-new)

- **Projection loss** dominates absolute accuracy: the →40 porthole discards structure (Arm B's larger-D instances
  bound how much, per arena).
- **Anchor un-validated at raw-784** (owed); the noise retention *ratio* is clean-baseline-confounded (reported as
  absolute noisy accuracy).
- **Descopes named, not faked:** Yearbook/BloodMNIST/CIFAR-100 (openml API down); **P11.8** the features arena (no
  off-box precompute window); the D=160 cross-dataset Arm B (the F5 einsum→GEMM apparatus fix, descoped to D=80); the
  raw-784 Split-MNIST anchor validation (owed — P11.2 ran it at porthole-40). The meter is behavioral (relative-pJ,
  ADC-centred, NOT SPICE).

*Up:* [draft context](../../CLAUDE.md) · *front door:* [`README.md`](README.md) · *numbers:* [`RESULTS.md`](RESULTS.md).
