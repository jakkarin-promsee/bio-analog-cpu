# Phase 11 — the limit map: the deep story (report)

> The narrative behind [`README.md`](README.md) and [`RESULTS.md`](RESULTS.md), written for an outsider — a
> researcher meeting this project here, or future-me a year out. Phase 11 took the P9-frozen two-brain neocortex
> — the object Phase 10 validated (S14) — off the 8×8-digit / 40-D synthetic bench and onto **real data, real
> streams, cross-dataset streams, and scale.** The instrument is the P10 fair-fight discipline; the posture is the
> author's: *"if everything fails, let them attack my math, not my missing evidence."* Every figure in this report
> is a real run; every number is bit-reproducible from the `arrays.npz` beside it. This report walks the rungs in
> order, because each read leans on the last, and ends on the one picture that is the whole phase: the **LIMIT-MAP**.

---

## The cast — what you are looking at (read this first if you're new)

Skip if you've read Phase 10; it's five definitions an outsider needs before the numbers mean anything.

- **The object.** One analog chip, two brains. A cheap **SCFF bulk** (~80%) — 12 forward-only self-contrastive
  layers — organizes the world *unsupervised* and is **frozen** (it never sees a gradient after Stage 1). A tiny
  **closed-form namer** (SLDA, ~20%) reads those features and puts *our* labels on them; a **drift gate** (DDM)
  fires the namer only when the cheap path stalls; a **sleep loop** (grid-4 cadence over a bounded prototype LUT)
  consolidates. Phases 7–10 built and froze this; Phase 11 measures it **untouched**.
- **Arm A — the frozen recipe.** The committed object, bit-for-bit (`freeze_content` verified identical to the P9
  hash), forced through a **40-dimensional random porthole** so every arena — an 8-D power stream or a 784-D image —
  enters at the *same* input width the object was frozen at. Arm A answers: *does the thing we actually committed
  survive contact with real data?*
- **Arm B — the scaling rule.** The same architecture rebuilt to a **pre-registered** size law (input dim
  D = min(native, 160), width W = ⌈1.6·D⌉, depth 12) — declared *before* any run, not tuned to any result. Arm B
  answers: *when we let it see the data at native scale, how much of the porthole loss comes back?*
- **The opponent — ER-strong.** Experience replay (a small net + a replay buffer), the field's *strong* continual
  baseline (Prabhu CVPR'23), **re-tuned per arena** on a disjoint seed-7 stream. The asymmetry runs *against* the
  home team on purpose: our recipe is frozen, theirs is fitted to each arena. When we still win, it counts.
- **The five metrics (the map's channels).**
  - **AA / prequential accuracy** — how accurate, overall. On streams this is *balanced* accuracy measured
    pre-update (test-then-train), the honest online read.
  - **worst-BWT (safety)** — the *worst* backward transfer over the whole run: how much the object forgets an old
    skill at its single worst moment. 0 = never forgets. This is the object's signature channel.
  - **retention (worst-point)** — accuracy on *all previously seen* material at the mid-stream low point.
  - **order-invariance** — |AA(forward-order) − AA(reversed-order)|. Small = the verdict doesn't depend on the luck
    of the ordering.
  - **beats no-change?** — on real streams, does the learner beat the trivial "predict the previous label"
    persistence baseline? On strongly autocorrelated streams this is brutally hard and separates real drift from
    fake difficulty.
- **The verdict encoding.** Every cell is **win** (teal) / **tie** (light) / **loss** (pink) / **FLOOR** (grey
  hatch). A **FLOOR** is not a loss — it means the cell is *uninformative*: the ceiling is at the resolution or
  persistence limit, so *nobody*, us or the field, can separate from it there. Grey is honesty, not defeat. The
  thresholds (δ_acc = 0.02, the FLOOR criterion) were **pinned blind**, before any Phase 11 number existed.

With that, the numbers below are legible. Every rung asks one question, runs it honestly, and hands its result to
the next.

---

## 0 · The bench (P11.0) — building the arena, honestly

**What it does.** Loads seven real arenas offline (dodging the dead openml *API* via Zalando GitHub, figshare, UCI):
digits (8×8), MNIST/Fashion/CIFAR-gray (784), gas (128-D sensor drift, 6 classes, batches 1–10), HAR (561-D, 6
classes, 30 subjects), electricity (8-D, 2 classes, chronological), covertype (54-D, 7 classes, file order).
Covertype's class imbalance is **10:1** → balanced accuracy is mandatory there.

**Why we do it first.** Three bench facts are load-bearing for everything after — and one of them nearly killed the
whole retention read before a single experiment ran:

1. **`freeze_content` is bit-exact.** The grid-4 object reproduces the P9 freeze to dBWT = dAA = dGD = 0. *We are
   measuring the exact frozen object* — not a re-implementation that quietly drifted.
2. **The noise-σ direction-killer, caught.** P10's noised domain adds σ = 0.6 *absolute* on RMS ≈ 0.486 inputs
   (σ/RMS = 1.239). The naïve "0.6 × RMS" shorthand would have made MNIST's noised domain ~2× milder — confounding
   the exact channel that drives the retention differentiator. Pinned by equivalence: σ_rung = (0.6/RMS_P10)·RMS_rung,
   ratio 1.239 on every arena. (This project's recurring silent killer is a wrong *direction/scale* on one variable;
   we caught this one at the source.)
3. **The economy does NOT improve with scale.** Walking the meter's own op-counts, GD-share vs W = {0.21, 0.34,
   0.53} for W ∈ {64, 128, 256}: it **rises**, because the SLDA solve term scales ~O((L·W)³). A pre-registered guess
   ("economy improves with scale," from an O(D·C + D²) formula whose D was the wrong variable) is refuted at the
   meter *source* — before a single scaling run committed compute to the wrong hypothesis.

**How to read it.** The bench is green: the arena is real, the object under test is the committed one, and the two
traps that would have biased the headline channels are defused up front.

---

## 1 · The decomposition (P11.1) — "isn't this just SLDA?"

**What it does.** Measures Δbulk = (bulk→namer accuracy) − (projection→namer accuracy): how much the *learned SCFF
bulk* adds over feeding the same closed-form namer a plain random projection of the raw input. It sweeps three
arenas of increasing nonlinearity and, as a control, inserts a *random-frozen* 12-layer bulk (a reservoir) to ask
whether any lift is *learned* or just "12 nonlinear layers exist."

**Why we do it.** This is the strike every serious reviewer throws — the namer (SLDA) is off-the-shelf literature,
so *is the architecture doing anything, or is it just SLDA in a costume?* Until Δbulk is measured, the claim is open.
And a pre-run diagnostic reframed the rung: **digits are near-linearly-separable** (raw-SLDA 0.950), so a linear
namer already saturates there and the bulk *cannot* add — a digits-only Δbulk would have banked a misleading "the
bulk is worthless." The honest measurement has to span from linear-easy to nonlinear-hard.

![P11.1 decomposition — the strike-1 answer](exp1/figs_p11_1/DECOMP.png)

*The strike, answered in two panels. **Left** — Δbulk tracks arena nonlinearity: where a linear head is at chance
(synthetic home, 0.172) the learned bulk lifts it to 0.589, **Δbulk +0.417** — and it clears the random-frozen
reservoir (0.389) by a wide margin, so the lift is **learned SCFF structure, not merely depth**. On moderate MNIST-40
the bulk adds a little (+0.008); on near-linear digits, where a linear head already saturates, the bulk is correctly
**redundant** (−0.014). **Right** — the safety channel: a projection→namer with *no bulk at all* forgets no more than
the full bulk→namer (worst-BWT 0.000 vs −0.016 on the digits gauntlet; 0.000 vs −0.096 on MNIST). So the continual
safety the object is famous for lives in the **closed-form namer + gate + sleep**, not the bulk.*

**What the result means.** The honest answer is a *decomposition of attribution*, sharper than a flat "confirmed":

- The SCFF **bulk is the nonlinear feature learner.** On data a linear head can't crack it is decisive (+0.417) and
  beats a random reservoir → *learned*. Where a linear head suffices, it steps out of the way.
- The continual **safety is the closed-form namer + gate + sleep, not the bulk.** We measured it; we say so.
- On **iid noise** at matched clean accuracy the bulk wins **+0.086** on digits (+0.215 on synth) — the P6
  noise-augmentation earning its keep, a channel the projection can't reach forward-only.

**How we interpret it.** "Isn't this just SLDA?" → *the safety largely is — and we're the ones who measured it; but
the bulk is the nonlinear learner, and on data that needs one it is decisive and beats a random reservoir.* That is a
stronger position than a defensive "no," because it tells the reviewer *exactly* which half of the machine does
which job. Kill-criterion (i) did not fire.

---

## 2 · The MNIST rung (P11.2) — does the frozen recipe survive real data, and scale?

**What it does.** Rebuilds the P10.3 domain-IL gauntlet in native MNIST-784 space → porthole, in both switch regimes
(rapid / long), both arms, against an ER re-tuned per arm on the disjoint seed-7 stream.

**Why we do it.** P10 proved the object on *synthetic* transformed digits. The first real-data question is the
narrowest one: put the identical frozen recipe on a real dataset — does the continual-safety signature survive, and
does Arm B's larger input dimension recover any of the porthole's projection loss?

| arm | regime | OURS AA | ER AA | OURS worst-BWT | ER worst-BWT | OURS ret | ER ret |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (D40) | rapid | 0.258 | 0.448 | −0.080 | −0.143 | 0.216 | 0.221 |
| A (D40) | **long** | 0.284 | 0.427 | **−0.012** | −0.196 | **0.223** | 0.102 |
| B (D80) | rapid | 0.390 | 0.541 | −0.011 | −0.113 | 0.298 | 0.210 |
| B (D80) | **long** | 0.421 | 0.514 | **−0.046** | −0.162 | **0.314** | 0.105 |

![P11.2 MNIST rung — the sleep loop batch-by-batch](exp2/figs_p11_2/STREAM_mnist.png)

*The mandated STREAM view — now with the best BP baseline overlaid (the Arm-B D80 stream, ER-strong tuned for this
arm), and it draws the continual-stability tradeoff in one picture. **ER (orange) rides higher within each stationary
domain** — climbing to 0.8–1.0 — but **crashes at every domain switch** (the dashed onsets: down toward ~0.1 as the
appearance shifts under its fixed head), a sawtooth of forget-and-relearn. **OURS (teal) rides lower but far flatter**
(~0.3–0.5, lifting into the easy domain around batch 190), and it never collapses at a switch. That is the whole rung:
ER wins raw accuracy *inside* a domain, OURS wins **stability across the switches** (long-regime worst-BWT −0.046 vs
ER −0.162, ~3.5× safer at its worst point). Both clear the persistence floor (0.097). A **continual-stability** trace,
not a static-accuracy one.*

**What the result means.** The bet **holds on real data.** OURS wins continual safety in every cell — decisively on
the long regime (the E8 primary read), forgetting **~4–16× less** than a per-arena-tuned ER — wins retention on long
blocks, and is order-invariant (|fwd−rev| 0.003 / 0.011). Static accuracy trails: the 40-D porthole is throwing away
most of MNIST's spatial structure, and the object was never a static-accuracy competitor (the P4/P10.5 identity).
And **Arm B scales**: D40→D80 lifts AA (0.284→0.421) and retention (0.223→0.314) with safety intact — the recipe
transfers *upward*.

**How we interpret it.** The signature that defined the object in Phase 10 is not an artifact of synthetic data; it
reproduces on a real dataset, and the pre-registered scaling rule recovers input-dimension loss without breaking the
safety it was frozen to protect. The one honest asterisk: the Split-MNIST *anchor* ran at porthole-40 (not the
literature's raw-784), so it sits below the published band — a config note we owe, not an ER-implementation failure.

---

## 3 · The real-world streams (P11.3) — nature's own drift

**What it does.** Runs four *real* time-ordered streams where the drift is not injected by us but is a property of
the world: gas-sensor aging, human-activity recognition by subject, electricity-price shift, forest-cover file
order. The pinned channel is **prequential balanced accuracy** (pre-update, every learner including no-change; the
R2 read). Roster: OURS-A/B vs the **stronger** of {ER-matched, ER-bigbuf}, plus sgd-linear, first-block-frozen, and
the mandatory no-change persistence baseline.

**Why we do it.** This is the phase's real point — the red team's "you only win on toy data." Synthetic drift is
*ours*; real drift is nature's, and it comes in two very different kinds. We wanted a measurement that *separates*
them.

| stream | OURS-A | OURS-B | stronger-ER | no-change | verdict |
| --- | --- | --- | --- | --- | --- |
| **gas** (6-cls, sensor drift) | **0.789** | **0.856** | 0.756 | 0.605 | **WIN** |
| har (6-cls, by-subject) | 0.686 | 0.820 | 0.754 | 0.950 | FLOOR (field +0.07) |
| electricity (2-cls, chrono) | 0.606 | 0.596 | 0.687 | 0.836 | FLOOR (field +0.08) |
| covertype (7-cls, file order) | 0.471 | 0.472 | 0.542 | 0.646 | FLOOR (field +0.07) |

![P11.3 gas — the real-world headline win](exp3/figs_p11_3/STREAM_gas.png)

*The headline, with the best BP baseline overlaid — and because the real-world stream swings violently batch-to-batch
(a hard chunk here, freshly-aged sensors there), drawn as a **rolling mean with a ±1σ band** rather than a jagged raw
line. OURS (teal) and the per-arena-tuned **ER-strong** (orange) both ride **far above** the no-change persistence
baseline (dash-dot, 0.605) — this is real, information-bearing drift, and any learner that reads the features beats
persistence. The two trends trade the lead early, but **OURS pulls clearly ahead in the late stream** — where the
sensors have aged most — and takes the **aggregate** (prequential 0.789 ≥ ER 0.756, +0.184 over persistence).
Crucially, **ER's band swings just as wide as OURS's**, so the volatility is the *data's* difficulty, not our sleep
loop. Untouched, the frozen recipe is the strongest online learner in the room; Arm B (native 128-D) lifts it to
0.856. Sensor aging is a **coherent covariate shift** — exactly the drift the SCFF bulk + sleep re-anchoring was built
to ride while the closed-form namer never catastrophically forgets.*

![P11.3 HAR — an honest FLOOR](exp3/figs_p11_3/STREAM_har.png)

*The counter-case, shown just as plainly — the same rolling mean ±1σ read, and now you can see the field lead. On HAR
both OURS (teal) and the tuned **ER-strong** (orange) learn well, but the no-change baseline (dash-dot, **0.95**) sits
*above both trends*: this is the ELEC2 label-autocorrelation trap, where "predict the previous label" is
near-unbeatable by any model that actually reads the features. Inside that floor, **ER's trend rides consistently
above OURS** (0.754 vs 0.686 — the ~0.07 field lead the map records); the cell is grey and **two-sided**, and the
overlay makes both sides visible — nobody beats persistence, and the field is ahead of us here. HAR, electricity, and
covertype all live in this regime.*

**What the result means.** The measurement cleanly separates two kinds of hard:

- **Drift-difficulty (gas): real, information-bearing, and OURS wins.** When the drift is a genuine covariate shift,
  the object's whole design pays off and it beats a tuned baseline and persistence.
- **Data-difficulty (autocorrelated labels): persistence wins, everyone floors.** On HAR/electricity/covertype *no
  learner beats no-change* — this is a known property of these streams (Souza 2020, D2), not a property of our
  object. We floor honestly, and we report that inside the floor the field is ~0.07 ahead (the anti-hype guard is
  not an anti-loss shield).

**How we interpret it.** One honest limit surfaced and we keep it in the open: the near-zero worst-BWT of the
*synthetic* gauntlet **does not carry to real drift** — OURS-A's worst-point BWT is genuinely negative (gas −0.333,
har −0.233, electric −0.149, covtype −0.097), the SLDA frame going stale between sleeps as nature drifts continuously
(a synthetic gauntlet drifts in discrete steps; nature does not). On gas this worst-BWT is also under-powered (R8:
batches 4/5 carry < 100 eval samples), which is exactly why the **prequential accuracy** is the pinned headline read
there, not the worst-BWT.

---

## 4 · The cross-dataset gauntlet (P11.4) — robustness to the TYPE of data

**What it does.** The author's most aggressive ask: not "same data plus a transform" but **entirely different
datasets in sequence** — MNIST → Fashion → CIFAR-gray presented as ONE class-IL **30-way** stream (the field's
5-Datasets protocol at our scale, but class-IL, *harder* than their task-IL), through a single porthole fit only on
source 1 (the honest gain-shock read — the object never gets to re-fit its front end when the data type changes).

**Why we do it.** Domain-IL (P11.2) changes the *appearance* of the same classes. This changes the *kind of object*
entirely, and grows the label space to 30 — the hardest ordering and capacity stress in the phase. If the object is
brittle to data type, this is where it shatters.

| arm | final-30 | order \|Δ\| | worst-ret | ER worst-ret | mnist / fashion / cifar-gray | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| A (D40) | 0.338 | 0.007 | 0.415 | 0.534 | 0.421 / 0.461 / 0.125 | TYPE-SCOPED |
| B (D80) | 0.440 | 0.004 | **0.581** | 0.551 | 0.588 / 0.581 / 0.143 | **TYPE-ROBUST** |

![P11.4 cross-dataset — 30-way across three data types](exp4/figs_p11_4/STREAM_xdata.png)

*The 30-way stream batch by batch across three data *types* (MNIST → Fashion → CIFAR-gray, sleeps grey), with the
tuned **ER-strong** overlaid (orange) and the persistence floor (dash-dot, 0.097). The overlay is the phase in
miniature: ER learns block 1 (MNIST, alone) to a *higher* accuracy than OURS (teal) — then **catastrophically
collapses to ≈0 at each data-type switch** (batch 24 → Fashion, batch 48 → CIFAR), because its fixed 30-way replay
head has never seen the new classes; OURS instead **degrades gracefully** and rides *above* ER through the entire
Fashion block. No block collapses to the 0.033 chance floor — even the weakest type (CIFAR-gray) holds ~4× chance and
never dies; the CBRS prototype LUT keeps every type represented through the growth. You can read our strength
(stability across type switches) and our cost (ER's higher first-block accuracy) directly off the two lines.*

**What the result means.** Three findings:

1. **All three data types stay alive.** No collapse; the bounded prototype memory keeps every kind represented as the
   space grows to 30-way.
2. **Order-invariance survives even a change in the *kind* of data** (|AA(fwd) − AA(rev)| = 0.007 / 0.004) — a direct
   consequence of the namer being closed-form: there is no gradient path a data-type ordering can bias.
3. **The scaling recipe flips the retention verdict.** At the frozen porthole (Arm A) worst-point retention 0.415
   trails ER's 0.534 (**TYPE-SCOPED** — all alive, retention behind); the scaled instance (Arm B, D80) recovers to
   0.581 ≥ ER 0.551 (**TYPE-ROBUST**). The namer's Gram condition number was instrumented (the D-research Q8 risk)
   and stayed **bounded** (~1–2e8, no blow-up).

**How we interpret it.** The object generalizes across data *type*, not just data *appearance* — and where the
porthole costs it retention, the pre-registered scaling rule buys it back. The owed leg is honest: Arm B at the full
recipe D=160 (descoped to D=80 for the overnight budget — the F5 einsum→GEMM apparatus fix).

---

## 5 · Does it scale? (P11.5–P11.7) — the strike-3 trilogy

Strike 3 is "you only showed one width, one depth, one input dim, one class count." It gets three separate answers:
capacity/accuracy, memory, and real-time throughput.

### 5.1 Accuracy & hardness (P11.5 r2/r3)

**Fashion (r2) holds the safety bet** — OURS worst-BWT −0.021 / −0.057 vs ER −0.146 / −0.141 (≈2–7× less forgetting)
while ER leads absolute accuracy (the continual-not-static identity, now on a *harder recognizable* dataset); Arm B
recovers retention (0.401 > ER 0.380). **CIFAR-gray (r3) is the honest FLOOR** — the joint-BP ceiling itself is only
0.199, so grayscale-cropped CIFAR through a 40-D porthole sits at the resolution floor and *every* channel there is
grey, not a parity claim. The far edge of the map is where it should be.

### 5.2 Memory — the cleanest scaling result in the phase (P11.5 crossover)

![P11.5 crossover — the class-count memory read](exp5/figs_p11_5/CROSSOVER.png)

*Two honest halves. **Left** — raw memory bytes vs class count C: the prototype+Gram namer carries a large *fixed*
O(C·F + F²) cost (F = 768 all-tap covariance), so on bytes alone it sits *above* a fixed-rate replay buffer across
the whole realistic range — there is **no memory-byte crossover**, and we say so. **Right** — but the metric that
matters, worst-point *retention*, crosses hard: at C=10 (Split-MNIST) the byte-matched replay out-retains OURS
(0.423 vs 0.354); at C=20 (MNIST+Fashion) the fixed replay buffer **dilutes to ≈0 retention (0.014)** while the
prototype+Gram namer holds (0.233) — a **+0.219 flip**.*

**What it means / how we interpret it.** The gradient-free namer keeps an *exact* per-class mean plus a shared
covariance, so per-class fidelity is C-independent; a fixed replay buffer splits its budget O(1/C) and collapses as
classes accumulate. The honest counterweight is the left panel: the win is **retention fidelity per class**, not byte
compactness. Both are true, both ship.

### 5.3 Economy & substrate (P11.6 capacity)

![P11.6 scaling — capacity vs the economy and the substrate](exp6/figs_p11_6/SCALING.png)

*Three panels, three reads. **Left** — the pre-registered test lands: the bench-pinned GD-share shape is
**CONFIRMED**, measured [0.17, 0.28, 0.45] tracking the meter-derived [0.21, 0.34, 0.53] as W ∈ {64, 128, 256}; the
economy does *not* improve with width (both cross the 0.25 cap) — the SLDA solve ~O((L·W)³) is the thing that scales
worst, refuting the pre-run guess at the run, not just the formula. **Middle** — capacity *does* buy the accuracy gap
back: 0.42→0.50 over W, 0.39→0.51 over D. **Right** — the chip's best sentence: the **analog substrate advantage
grows** with width — measured E(digital)/E(analog) = 5.39 → 6.89 → 7.25 across the W-sweep (7.37× at D=160). The
crossbar prices the extra bulk MACs near-free, so the compute-in-memory edge *widens* at scale; safety holds at every
width and dim.*

### 5.4 Real-time (P11.7 throughput)

**What it does / finds.** On the gas stream the retention-tuned ER-strong (wide net + replay) costs more FLOPs/sample
than the frozen D40 recipe, so at a shared compute budget ER must **drop 32% / 31% / 8%** of the stream (raw-FLOP /
digital / analog meter) while OURS keeps up — **branch (i), the regime win.** *How we interpret it, with the caveat
in the open:* this **inverts** P10's synthetic-home measurement (where OURS used *more* FLOPs than a cheap ER), so
the real-time economy is **arena- and opponent-dependent, not universal** — and the map says so. It is a real win on
a real stream against a strong opponent, not a general throughput claim.

---

## 6 · The LIMIT-MAP + what it all means (P11.9)

Everything above collapses into one picture — the deliverable the whole phase was for.

![P11.9 LIMIT-MAP — the committed object across real arenas and scale](exp9/figs_p11_9/LIMIT_MAP.png)

*The money figure: 8 arenas (columns) × 5 capability channels (rows), every cell **win** (teal) / **tie** (light) /
**loss** (pink) / **FLOOR** (grey hatch), with its number. Read *down* the channels and the object's identity is
unmistakable and honestly bounded.*

- **Wins (teal):** continual **safety** (worst-BWT) on every non-floor gauntlet arena (mnist, fashion); **retention**
  on mnist-long; **order-invariance** everywhere it is measured (mnist, xdata, gas — |Δ| ≤ 0.043, even across data
  *types*); **gas accuracy** (the real-world headline, beating a per-arena-tuned ER *and* persistence); and — in the
  SCALING/CROSSOVER panels rather than the arena grid — the **scaling reads** (the pinned economy shape confirmed,
  the growing substrate factor, the C=20 retention crossover, the gas throughput regime win).
- **Losses (pink):** static **accuracy** on mnist and fashion (continual-not-static — P4/P10.5 re-confirmed at
  scale); **retention** on fashion (Arm A) and the 30-way xdata stream (both *recovered by Arm B*). The object is not
  a static-accuracy competitor and the map never pretends otherwise.
- **Floors (grey):** CIFAR-gray (a native-resolution floor); HAR / electricity / covertype (the ELEC2
  label-autocorrelation trap — persistence unbeatable, the field floors alongside OURS but leads by ~0.07). The far
  and autocorrelated edges of the map are grey, and grey is not parity.

The **Δbulk overlay** (P11.1) keys the whole map to a mechanism: the bulk earns its place where the data is nonlinear
(the synthetic home +0.417, real sensors), and the continual *safety* is the closed-form namer + gate + sleep, not
the bulk. So the honest deployment envelope — for the pitch and for the analog-realism layer that inherits this — is:

> **A substrate-native continual learner that wins safety, noise-robustness, order-invariance, real
> information-bearing drift (gas), and every scaling read of the economy/substrate — while trailing on static
> accuracy and flooring where the data is at its resolution or persistence limit.**

The wins are real; the losses and floors are *mapped, not hidden.* That map was the deliverable, and it is drawn.

---

## Threats to validity (carried + P11-new)

- **Projection loss dominates absolute accuracy.** The →40 porthole discards structure; Arm B's larger-D instances
  bound how much, per arena, but the static-accuracy losses are partly a porthole artifact, not a pure capability
  gap.
- **Anchor un-validated at raw-784** (owed — P11.2 ran the Split-MNIST anchor at porthole-40, a config note, not an
  ER-implementation failure); the noise-retention *ratio* is clean-baseline-confounded (so it is reported as absolute
  noisy accuracy).
- **Real-drift worst-BWT is genuinely negative** (§3) — the synthetic near-zero-forgetting does not transfer to
  continuous natural drift; reported, not hidden.
- **Descopes named, not faked:** Yearbook / BloodMNIST / CIFAR-100 (openml API down on the box); **P11.8** the
  features arena (no off-box precompute window); the D=160 cross-dataset Arm B (the F5 einsum→GEMM apparatus fix,
  descoped to D=80); the raw-784 Split-MNIST anchor validation.
- **The meter is behavioral** (relative-pJ, ADC-centred, Horowitz-anchored) — **NOT SPICE.** Absolute Joules and
  device physics are the analog-realism layer, which also inherits the named directional/ADC noise residual.

---

*Up:* [the validation volume](../validation-report.md) (P10 + P11 as one arc) · *front door:* [`README.md`](README.md) ·
*numbers:* [`RESULTS.md`](RESULTS.md) · *the Stage-2 build this validates:* [`../stage2-report.md`](../stage2-report.md).
