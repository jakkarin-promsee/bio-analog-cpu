# Phase 1 — Experiments (`draft6.0/src/phase1`)

> The first behavioral simulations of the SCFF + GD block. **Ideal floats, no analog/PVT yet.** The control
> in every experiment is **pure gradient descent (vanilla backprop)**; the treatment is our block, held at
> the *same total weight count*. We are not asking "does the block beat GD" — we are **characterizing how
> the block behaves differently**, forward and backward, and where (if anywhere) it pays off.
>
> This is the codeable spec for the experiment ladder in [`../../idea/ideas1.md`](../../idea/ideas1.md).
> Mapping: 0th probe = ladder 1.0 + 1.1 · Exp 1 ≈ ladder 2.0 · Exp 2 ≈ ladder 2.1 · Exp 3 ≈ ladder 4.x ·
> **Exp 4 (maintenance) ≈ ladder 3.x + Ch 7 gate.** **Note the reorder:** ideas1 builds sleep (3.x) *before*
> chaining (4.x); Phase 1 deliberately flips that — characterize *structure* first (single block → multi-
> block), then add the online-maintenance layer (gate + sleep) as **Exp 4**, because the drift we see in
> Exp 3 is the *data* that motivates it. (`main.ideas.v1.md` records this reorder + the Ch 9→N3 resolution.)

---

> **✅ Phase 1 complete (2026-06-20, exp0 → exp4).** Read the synthesis of all findings first:
> **[`README.md`](README.md)** (the story) + **[`RESULTS.md`](RESULTS.md)** (the ledger).
> One-line verdict: *draft 6.0 is a cheap, forgetting-robust **continual** learner — it generalizes better
> than backprop at ~10% backward cost and wins decisively in the continual regime (sleep recovers what
> online backprop catastrophically forgets); it is not a deep static-accuracy competitor, and that's the point.*

---

## 0. How we evaluate — read this first

The model **never stops learning**, so there is no clean train-then-freeze boundary. But that creates a
trap: **if every model trains on 100% of the data, they compete on *memorization*, not *understanding*.** A
prequential (test-then-train) curve on a finite or looped stream rewards whoever memorizes hardest. So we
measure two different things, and the **second is the headline**:

- **Adaptation — the online (test-then-train) curve.** For each batch: predict and log loss/acc *first*,
  then update (SCFF locally + GD on the taps). Shows how fast each model tracks the stream. **Secondary** —
  it is contaminated by memorization.
- **Understanding — the held-out generalization curve (HEADLINE).** Keep a **validation set that is *never*
  trained on.** At checkpoints along the stream, evaluate it *without updating* and log val accuracy vs
  samples-seen. This is the fair competition metric: no model wins it by remembering, only by capturing the
  real shape. With a generator, "held-out" = **fresh draws the model has never seen** (cleanest); with
  finite data, a fixed split.
- **The gap = memorization.** `train-stream accuracy − held-out accuracy` is the generalization gap. SCFF's
  whole claim is that it organizes *structure* (small gap); a pure-GD net on a stream can memorize (large
  gap). **That gap is one of the most interesting comparisons in Exp 1.**

Always compare block vs pure GD on the **identical stream and the identical held-out set** (same seed, same
order).

## 1. The controlled setup (locked across Exp 1–3 — the run batch)

| Variable | Locked to | Note |
| --- | --- | --- |
| Task | parametrized synthetic with a **complexity dial** — see *Tasks* below | difficulty is a swept axis, not a fixed point; keeps the features visualizable |
| Held-out validation | a set the model **never trains on** (fresh generator draws; or a fixed split) | the *understanding* metric — see §0; identical across compared models |
| Total weight count | equal for GD control and the block(s) | the fair-comparison constraint — vary *structure*, not capacity. (Exp 2b intentionally relaxes this to isolate GD-translator capacity — flagged there.) |
| Seeds | `[42, 137, 271, 314, 1729]` | report **median + IQR**, never a single run |
| Init, stream order, total samples seen, eval cadence | fixed | unless that one is the variable under test |
| Realism | ideal floats; **no** analog/PVT, **no** gate, **no** sleep | those are separate variables, added later |

**One variable changed per experiment.** A run that fails is a result — log it, characterize it across
configs, move on. Don't tune until it passes.

## 1.5 Tasks — synthetic, with a complexity dial (not external benchmarks, yet)

Fixed famous datasets are the wrong tool *here* — and so are trivially-easy ones: if the task is easy,
every model generalizes and the **memorization gap vanishes**, so there's nothing to compare. The fix is
**parametrized synthetic data with a complexity knob**, so difficulty is an *axis we sweep*, not a single
point. A real dataset gives one fixed difficulty and no dial; a generator gives the whole reachability
curve — and keeps the per-layer features *visualizable*, which is the whole point of Exp 1.

- **Tier A — low-D, visualizable (2–3D).** Spirals (tunable arms + noise), a smooth random boundary
  (Gaussian-process sample; length-scale = frequency = difficulty), nested rings. Use for the 0th probe and
  Exp 1's forward/backward heatmaps + boundary plots — you can *see* what each layer does.
- **Tier B — higher-D, compositional (the real stress).** Many overlapping Gaussian clusters where the
  label is a nontrivial (XOR-like / compositional) function of *which* clusters a point falls in — this
  directly stresses the thesis (SCFF finds the clusters unsupervised; GD names them; pure GD must do both at
  once). Dial: cluster count, overlap, label-function complexity, input dimension, label noise. Use for the
  reachability surfaces and the memorization-gap-vs-complexity reads (Exp 2, Exp 3).
- **The complexity dial is an experiment axis** — sweep it for the reachability surface (defined once in §3).
- **Later (a probe, not the claim).** Once the ideal converges, confirm on **one small real dataset** (a
  small tabular set, or MNIST as a flat-MLP probe) so the result isn't synthetic-only. External benchmark
  *chasing* (CIFAR/ImageNet, conv front-ends) stays out of scope — that's `research/north-star/` territory.

## 2. The mechanics, resolved

### 2.1 pos / neg / normal — two worlds, not three inputs

Mono-forward carries **two worlds** through the *shared* weight crossbar:

- **Positive world** = the real sample, `x_pos = 2·x_k` (summation form of the self-pair).
- **Negative world** = `x_neg = x_k + x_n`, `x_n` a *different* sample.

**GD reads the positive world's taps** and maps them to the label of `x_k`. The negative world exists only
to give SCFF its contrast. Mechanism check (no scale bug): under ReLU + the mandatory inter-layer norm the
2× gain cancels exactly — `ĥ = φ(W·2x_k)/‖φ(W·2x_k)‖ = φ(W·x_k)/‖φ(W·x_k)‖` — so the positive-world
representation **is identical to a plain `x_k` forward.**

**Negative partner (Phase 1 stub):** `x_n` = a random sample from the current batch. No LUT yet — the
prototype store is the later sleep/memory work.

### 2.2 Timing — both update every step

For Exp 1–3: **SCFF updates locally every step; GD updates on the taps every step.** No gate.

> The "70% SCFF / 30% GD" idea is the **threshold gate** (ideas1 Ch 7) — a real part of the design, but a
> *separate variable.* Test it on its own later; folding it in here would confound the structural question.

## 3. Metrics (logged every run)

> **How these are drawn and written up is the [`result-format.md`](result-format.md) standard** — the house
> style (consistent encoding + IQR bands), the figure catalog (F1–F9 + invariant strip), and the six-slot
> summary template. This section is *what* we log; that file is *what a result looks like.*
> **Map:** primary = **F1** (+ F1′ secondary) · forward = **F3 + F4** · backward = **F7** · reachability =
> **F6** · invariants = **INV**.

- **Primary (the shape):** the **held-out generalization curve** (val accuracy vs samples-seen — the
  headline, measures *understanding*) plus the **online adaptation curve** (prequential loss/acc —
  secondary, shows tracking speed), block vs GD on the same stream. Report the **generalization gap**
  (train-stream − held-out) for each.
- **Forward behavior:** **per-layer feature separability** (a linear probe trained on each layer's
  activations → accuracy), plotted as a **layer × time heatmap**; plus SCFF **goodness separation**
  (`G_pos` vs `G_neg` per layer). Shows *where* separability is built — GD top-down from the label, SCFF
  bottom-up with no label.
- **Backward behavior:** **credit locality** — how far an update signal travels: pure GD = full depth
  (non-local); SCFF layers = distance 0 (local); the residual-boosting chain keeps per-block credit local
  (each block fits its *current residual*), with the optional linear inter-block delta as an O(blocks)
  top-up. Plus backward op-count / cost. This is *the* structural difference.
- **Invariants (every run):** loss-slope (convergence), dead-unit fraction, goodness/ceiling saturation,
  and — Exp 3 only — inter-block drift / SCFF cluster-churn.
- **Reachability (the read we trust):** final reachable accuracy as a **surface over (task-difficulty ×
  architecture)**, under the fixed weight budget.

## 4. A 0th sanity probe (before Exp 1)

You cannot interpret a block until you know its two halves work alone:

- **Full SCFF alone** (ladder 1.0): does goodness separate (`G_pos`↑, `G_neg`↓), and do layers grow more
  separable with depth? If not, fix this before bolting GD on. **Sub-cells (set two open knobs here):**
  **two-sided loss vs pure-contrast** objective, and a **cheaper forward-only rival** as a bench check.
- **Full GD alone** (ladder 1.1): the precision ceiling / control that Exp 1–3 quote against.

> **Deferred remediation, not baseline:** BCM homeostasis (the anti-permutation guard, ideas1 Ch 6) is
> *committed* but, per the methodology, stays **out of the baseline** — it's the named fix to reach for *if*
> SCFF cluster-churn shows up (which we already log as an invariant). Don't bolt it on before the baseline
> is characterized.

---

## Experiment 1 — one block vs pure GD

### 1a — behavior at a fixed size

**Question.** How does one block behave differently from vanilla GD, *forward and backward*?

**Setup.** Control = a plain MLP under full backprop. Treatment = one block `[SCFF layers → GD checkpoint]`,
same total weights, same stream/seed.

**Measure.**
- *Forward:* the layer×time separability heatmap + goodness separation, **block vs GD side by side.** Does
  SCFF build separability bottom-up before GD ever touches it?
- *Backward:* credit locality + backward cost. The block's SCFF layers update locally (distance 0); only
  the GD checkpoint does a short backward. GD routes one global signal through the whole depth.
- *Generalization:* the held-out accuracy curve overlaid (block vs GD) and the **memorization gap**
  (train-stream − held-out) for each — does the block *understand* (small gap) where GD *memorizes* (large gap)?
- *Adaptation:* the online curves overlaid (secondary).

**Read.** Not "who wins" — *the difference*. Expect: comparable held-out accuracy, but the block builds
features locally and cheaply while GD builds them globally and expensively — and a **smaller memorization
gap** for the block is the headline result (structure, not rote). If the block's accuracy lags badly, that
gap is the data (it's what the ratio sweep in Exp 2a probes).

**Pass gate (ladder 2.0, traceability).** Beyond the characterization above, the concrete bar is two-part:
tapped-GD on the SCFF features **beats SCFF's bare top-layer readout** *and* **approaches the 1.1 full-GD
ceiling**. The gap / forward / backward reads are the *characterization*; this two-part accuracy check is
the *pass*.

### 1b — does the difference hold across model size? (the scale-free check)

**Question.** Is the block-vs-GD difference (accuracy, and the memorization gap) a property of the
architecture, or an artifact of one chosen size?

**Setup.** Sweep **total weight count** — small → large — with block and pure GD **matched at each size
point** (the fixed-budget control holds *within* a point; size is the explicit variable *across* points).

**Measure.** Held-out accuracy and the memorization gap as a function of size, block vs GD. Watch the two
failure regimes: too small (both underfit), too large (both memorize — gaps blow up).

**Read.** The honest comparison only lives in the middle regime, where capacity is the real constraint. If
the block keeps a smaller memorization gap *across* sizes, that's a **scale-free** property — the
reachability shape shouldn't depend on the exact budget. This cell also **fixes the default size** that
Exp 2 and 3 then hold constant.

## Experiment 2 — Inside the block: the best shape to convert SCFF features to labels

All single-block, all against the pure-GD control, all judged on **held-out** accuracy. Three internal
knobs — **one variable per cell.**

### 2a — SCFF:GD ratio (the split point)

**Question.** How much of the block can be cheap SCFF before precision suffers? (Sets the ~80/20 knob.)
**Setup.** At **fixed total weights**, slide the split: 0% SCFF (= pure GD) → 50% → 75% → 90% SCFF, GD
taking the rest. **Measure.** The trade curve — held-out accuracy *and* backward cost vs SCFF fraction.
**Read.** The sweet spot where held-out accuracy holds near the GD ceiling while cost drops — the empirical
"is 80/20 right?"

### 2b — Interface GD depth (the translator's capacity)

**Question.** How deep does the GD checkpoint need to be to read SCFF features well?
**Setup.** **Freeze one fixed SCFF front** (identical features for every cell), then sweep the GD checkpoint
depth: 1 → 2 → 3 → … layers. *This intentionally relaxes the fixed-budget control* — the question is
internal (translator capacity), not "block vs GD" — so total params grow; **don't** compare its absolute
size to the Exp-1 GD baseline. **Measure.** Held-out accuracy vs GD depth. **Read.** Where accuracy
saturates — the cheapest GD checkpoint that still translates. (Under a *fixed* budget, 2a already sweeps
this axis at its high-GD end; 2b isolates it from the SCFF trade-off.)

### 2c — The plasticity gradient (frozen vs slow vs fast read-layers) — the committed stability cell

This is the *real* ladder 2.1, and it is **committed**, not optional: the plasticity-gradient slowdown is
N2's resolved drift fix (the SCFF layers GD reads learn *slow*; the front stays *fast* — ideas1 Ch 6).
**Question.** What slowdown on the read-layers keeps GD tracking without choking SCFF's learning? **Setup.**
One block, sweep the read-layer plasticity: **frozen vs slow vs fast** (a 3-way ratio sweep — this *sets*
N2's only open knob, the front:back plasticity ratio). **Measure.** Held-out accuracy + the stability
invariants (how much the read-layer features drift between GD updates). **Read.** The slowdown where GD
tracks SCFF *and* SCFF's ceiling doesn't collapse. If frozen wins, that's the cheap end; if even slow
chokes SCFF, the named upgrade is **EMA-view** (let read-layers learn fast, GD reads a slow EMA copy — N2).

> *Optional polish, not this cell:* **direct GD-shaping of the middle / DF-O overlapping-block
> coordination** is what Ch 6 explicitly calls optional. The "is it dead weight?" question belongs *there* —
> test it only if the committed plasticity gradient above leaves residual drift.

## Experiment 3 — residual-boosting block chain vs pure GD

**Question.** Does a chain of weak correctors on a **residual stream** reduce error with depth the way
boosting predicts — and does it *generalize* better (a smaller memorization gap) than a same-size pure-GD
net? (Not "beat backprop on accuracy": BoostResNet lands *slightly below* end-to-end backprop in its own
experiments — the claim under test is "this structure provably trains and converges," and the win we look
for is the error-reduction *shape* and the *gap*, not raw victory.)

**Setup.** Control = a deeper pure-GD MLP, same total weights. Treatment = **N blocks on a residual stream**
(`r_k = r_{k-1} +` Block *k*'s correction; the final prediction reads the accumulated sum — **N3 boosting
telescoping sum**, [`../../research/papers/phase1-2/boostresnet.md`](../../research/papers/phase1-2/boostresnet.md)).
Each block = SCFF feature work + an **Interface GD** checkpoint that fits the **residual its predecessor
left** (the weak corrector), with one **Output GD** namer at the end. The **linear inter-block delta**
(ideas1 Ch 9) is available as the optional O(blocks) direction top-up, **off by default** (boosting makes
per-block credit local) and switched on only to probe its effect.

**Two distinct guards (don't conflate them):** the mandatory inter-layer norm guards the *within-block*
shortcut — a block inflating `‖h‖²` by passing its input straight through (FF goodness-recycling, S5); the
**weak-edge γ check** (in *Measure*) guards the *between-block* failure — a **dead block** that can't beat
its predecessor (γ≈0). The norm alone does **not** protect the chain; the γ check is what catches a lazy block.

**Measure.**
- The held-out generalization curves, chain vs GD (+ memorization gap).
- **Boosting shape:** does training error fall ~exponentially with added blocks (the BoostResNet
  `≤ e^{−½Tγ²}` prediction)? Does each block clear a *weak edge* γ over its input — or is it a **dead block**
  (γ≈0, can't beat its predecessor)? The dead-block watch is the between-block guard (the norm doesn't catch it).
- **Direction chaining / inter-block drift:** when an early block updates, does a later block's input swing?
  (This drift is the *data* that motivates the Exp-4 maintenance layer.)
- **Strain point:** how many blocks before the chain stops improving — and separately, whether switching the
  linear inter-block delta *on* extends that point.

**Read.** Whether the residual-boosting chain (each block a weak corrector of the running residual) buys
error reduction with depth that a same-size pure-GD net doesn't — and where the weak-edge guarantee strains.

## Experiment 4 — maintenance: the gate + sleep *(deferred, named here so it doesn't vanish)*

**Not run in this batch** — but it is the destination, not a dropped rung. Once structure is characterized
(Exp 1–3), add the online-maintenance layer that lets the model learn forever without rotting:

- **The threshold gate** (ideas1 Ch 7) — SCFF-only below θ, SCFF + chained GD above. (This is the real home
  of the "70% SCFF / 30% GD" idea.)
- **Sleep consolidation** (Ch 8) — periodic full-batch GD over history against the current SCFF map; this is
  where the **LUT prototype store stops being a stub and becomes a real organ** (ladder 3.2).

It's deferred on purpose: the inter-block drift surfaced in Exp 3 is exactly the data that says *how much*
maintenance is needed. Build it when that data is in, not before.

---

## What to build (component checklist)

- **Layer primitive** — linear + activation + mandatory inter-layer norm (`ĥ = h/‖h‖`).
- **SCFF layer** — carries both worlds (`a_pos`, `a_neg`); computes `G = ‖h‖²`; two-sided local update
  (`L = log(1+e^{-(G_pos-θ)}) + log(1+e^{+(G_neg-θ)})`), gradient through one layer only.
- **Interface GD** (per-block exit, *tracking*) — SGD + momentum, squared-error; in a chain it fits the
  block's **residual** and emits the block's correction. Used per block in Exp 3.
- **Output GD** (the final *namer*) — a **2–3 layer residual MLP**, Adam-class, cross-entropy; reads the
  positive-world taps (last *n* SCFF layers) → label. The readout in single-block (Exp 1/2) and at the
  chain's end (Exp 3). **Configurable depth** + a **freeze-SCFF mode** (for 2b).
- **Block** — **residual stream in/out**: `r → [SCFF feature work → GD-checkpoint correction] → r + correction`;
  the mandatory inter-layer norm guards the *within-block* goodness-recycling shortcut (S5) — the
  *between-block* dead-block failure is caught by the weak-edge γ check, **not** the norm. Read-layer
  plasticity configurable (frozen / slow / fast, for 2c).
- **Pure-GD baseline** — plain MLP, same total weights, full backprop. **Total size configurable** (the 1b sweep).
- **Negative sampler** — random partner from the current batch (stub).
- **Task generator** — **Tier A** (low-D, visualizable) + **Tier B** (higher-D, compositional clusters);
  exposes a **complexity dial** and a **held-out / fresh-draw mode**.
- **Eval harness** — the test-then-train loop **plus held-out evaluation at checkpoints** (no update); logs
  the held-out generalization curve, the online adaptation curve, the **memorization gap**, the per-layer
  probe heatmap, the goodness separation, the invariants; emits the figures.

## Open knobs (the sims decide, not us)

- SCFF:GD ratio (Exp 2a) · front:back plasticity ratio — frozen/slow/fast (Exp 2c) · Interface GD depth
  (Exp 2b) · how many blocks before strain (Exp 3) · **margin-loss vs log-loss** · **two-sided vs
  pure-contrast** objective (0th probe) · **EMA-view** — N2's de-risked fallback if the read-layer slowdown
  pinches SCFF · **tied-from-start vs converge-to-tied first layer** · negative-partner strategy (random
  now; hard-negative / LUT later) · GD optimizer + learning rate · θ (the goodness threshold) · eval cadence
  · task difficulty range. The gate and sleep are **Exp 4**, not these three.

## Where to record results

One folder per experiment under `draft6.0/src/phase1/` (`exp0/`, `exp1/`, `exp2a/`, `exp2b/`, `exp2c/`,
`exp3/`), each with an `experiment-{n}.md`: **question → setup → run → result/figures → read → decision.**
**The result/figures and read sections follow [`result-format.md`](result-format.md)** — the figure catalog
and the six-slot summary template — so every run is comparable and deep enough to cite. The phase-wide
synthesis lives in one place: the **[`RESULTS.md`](RESULTS.md) ledger** (one row per experiment: scalar → knob
set → decision fed) — fill a row the moment a run's decision is made.
The first one — [`exp0/experiment-0.md`](exp0/experiment-0.md) — has its config **locked and ready to run.** Status pointer lives in
[`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md); don't log runs in the `ideas1.md` derivation
chapters.
