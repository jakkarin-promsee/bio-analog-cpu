# The neocortex — final architecture (v2.0.0, the complete two-brain loop, frozen)

> **What this is.** The single, self-contained account of the model we built across **nine** phases of draft 6.0 — the
> whole chip, both brains, the lifelong maintenance loop, now **frozen**. It is written so an **outside researcher can
> understand the entire model from this one file**, without opening a single `phaseN/` report. It is the current head of
> the line and **supersedes [`phase6-final-architecture.md`](phase6-final-architecture.md)** — which is kept, unchanged,
> as the **v1.1.0 cheap-brain-only snapshot** (SCFF alone, before it had a namer). What v2.0.0 adds is the other half of
> the chip and the loop that keeps it alive: the **precise "namer"** that puts our labels on the cheap brain's features
> (Phase 7), the **drift-gated economy** that decides when the namer pays (Phase 8), and the **lifelong maintenance
> loop** that survives forever and has now been **tuned against internal signals and locked** (Phase 9). The cheap brain
> (§2) is frozen and only summarized here; its full derivation is in [`phase6-final-architecture.md`](phase6-final-architecture.md).
>
> **What "v2.0.0 / frozen" means — read this before any claim.** This freezes the **ideal-math *design*** of the whole
> two-brain neocortex — not its silicon, not its scale, not a benchmark win. Almost every number here is from a
> **behavioral simulation** (numpy, ideal floats), with two honest exceptions that are themselves *behavioral*, not
> device physics: Phase 6's analog-**noise** model (§2.5) and Phase 8's analog-**energy** model (a NeuroSim/ISAAC/PUMA-
> level ADC-centred macro-model, relative-pJ, **not SPICE**; §4). The tasks are **small and partly synthetic** (Gaussian
> generators, 8×8 digits, flat CIFAR). "Frozen" means *the design is settled and the maintenance loop was locked at a
> commit hash **before** the final validation runs, so Phase 10 can race it fairly* — **the discipline is: freeze in P9,
> judge in P10.** The existential head-to-head against a fair backprop baseline, the multi-domain gauntlet, and the
> natural many-class number are **Phase 10, still owed** (§10); this file is the *object under test*, not the verdict.
>
> **The spine (the one idea under everything).** The project's recurring failure is confusing **density for class**
> (loudness for label) and losing a **sign / direction**. So the rule the whole design obeys is: *learning must preserve
> and read the class **direction**, never a **magnitude*** (energy, rank, variance, confidence, distance are all
> magnitudes). It has now been paid **nine times** — most recently at the buffer (eviction keeps class *directions*, not
> the dense *mean*) and at the read side (calibration re-anchors a *direction*, never a confidence). When something below
> seems surprising, this is usually why.
>
> **A naming note.** "SCFF" denotes the **forward-only, label-free, self-contrastive *frame*** (the cheap-brain role),
> not the energy-goodness loss of the SCFF paper (Phase 3 replaced that with InfoNCE). The "**GD namer**" / "the 20% GD"
> is a *role* (the precise, label-consuming brain), **not a method**: Phase 7 found the committed namer is **not gradient
> descent at all** — it is a closed-form streaming analytic head (§3). Biological names ("Hippocampus", "neocortex")
> name **circuit elements**, not biology. The committed cell's code name is **`NoiseAugContrast`**; the frozen loop is
> locked at commit **`59d2720`**.

---

## Reader's glossary (the load-bearing terms, defined once)

| term | meaning in this document |
| --- | --- |
| **the spine** | preserve/read the class **direction**, never a magnitude. **density ≠ class** is its recurring violation. |
| **the two brains** | the **cheap brain** = SCFF, ~80% of the network, *learns* forward-only/label-free (frozen, §2); the **precise brain** = the GD "namer," ~20%, maps features → our labels (§3). |
| **the namer** | the precise brain. Committed = **SLDA** (deployed), **RanPAC** the accuracy/spine reference — both **gradient-free, closed-form, streaming** (§3). "GD" is its *role*, not its method. |
| **probe vs readout / namer** | a **linear probe** is a frozen-features *diagnostic* of separability (never deployed). A **readout / namer** is the deployed head. Never blended. |
| **BWT / AA / worst-BWT** | continual metrics: **Backward Transfer** (forgetting; 0 = none, negative = worse), **Average Accuracy**, and **worst-BWT** = the most-negative BWT at the awake gate's **worst mid-stream point (pre-sleep)** — the live-safety read. |
| **the economy / the 80/20 (metered)** | the fraction of total **substrate energy** spent on the namer. Phase 8 makes it a *measured* number (`GD-share`) on a behavioral ADC-centred meter — **not** an op-count proxy, **not** SPICE. Design target ≤ 0.25. |
| **the gate / the trigger** | the **awake learning-gate** (Phase 8): run cheap SCFF every step; fire an expensive namer update only when a **drift trigger** says the cheap path has stalled. Committed gate = **DDM**; trigger = **class-direction tap-drift** (a *direction*, not a magnitude). |
| **sleep / the LUT** | periodic **consolidation**: re-forward a raw-prototype store (the **Hippocampus LUT**) through the *current* SCFF map, rebuild the running Gram, re-solve the namer. The LUT is a bounded, evicting store (§5.4). |
| **the frozen / oracle reference** | an *internal* reference that **cheats with hidden task boundaries** (sleeps/fires exactly at onsets). Matching it is the *win*; it is never a deployable path. Every Phase-9 verdict is measured against it, **never** against the Phase-10 backprop baseline. |
| **rotation vs forgetting** | the SCFF map **rotates** (a fixed head goes stale) but does not **forget** (an optimal probe *re-fit* on the current bulk still decodes the old classes). Phase 9 measured this; it is why cheap sleep suffices (§5.1). |
| **the freeze (P9.5)** | the whole tuned loop, **committed at a git hash**, so Phase 10 races a locked object. `59d2720`. |

---

## 0 · The one-paragraph truth (and why anyone should care)

This is **not a machine-learning model and not a digital ML accelerator.** It is a **bio-inspired analog compute
substrate that learns on-chip, online, forever**: capacitors hold weights as continuous charge, SRAM holds wiring and
sign bits, op-amps do add / multiply / ReLU directly on the charge, and **the weights never leave the chip** (a
resident-weight, compute-in-memory design). The target is **in-field adaptation at analog-circuit energy, with no
gradient or weight ever shipped off-chip** — a device that keeps learning where it sits, cheaply, instead of a frozen
model retrained in a datacenter. That target makes two things matter that mainstream ML treats as afterthoughts: the
**energy of the backward pass** and **catastrophic forgetting**. The design answers both with **two brains** on one
substrate: a large unsupervised **SCFF** front (~80%) whose *learning* is cheap — label-free, local, forward-only, no
backward pass — and a small precise **"namer"** back (~20%) that puts real labels on what the front organized. The whole
bet rides on one observation: **direction is the one expensive thing in learning.** Measuring how loud a neuron is is
free; deciding *which way* each weight must move is what costs. So we **pay for direction once, where it counts.** Two
findings from Stage 2 sharpen this into something more surprising than the plan guessed. First: the "20% GD" **is not
gradient descent** — the precise brain that reads a frozen bulk is best served by a **closed-form, streaming analytic
head** (no gradient at all), because the cheap brain already did the hard representational work (§3). Second: running
both brains forever is **not free but cheap and, crucially, *safe*** — a drift-gate that fires the namer rarely both
**meters out to ~12–18% of energy** *and* **forgets less than firing always** (firing more forgets more — the gate is a
safety mechanism, §4). Phase 9 then proved the founding cheapness assumption (the bulk **rotates but does not forget**,
§5.1), tuned the last open knobs against internal signals, and **froze the object.** The method throughout: **copy the
brain's *function*, cheat the *implementation*.**

---

## 1 · The substrate, in one breath (enough to ground the rest — full detail in the v1.1.0 file)

Three primitives, because they explain *why* the learning rules are shaped the way they are.

- **The Scap** (SRAM + Capacitor): one synapse's weight, as **analog charge on a capacitor** (the magnitude) + a
  **digital SRAM bit** (the sign — so `±` is exact). A Scap is a *wire, not a neuron*.
- **The crossbar** computes in the wires: a grid of Scaps does the multiply-accumulate as physical current; op-amps do
  the nonlinearities on charge. There is no ALU shuttling data — **computation is where the weights physically are.**
- **Mono-forward, dual-rail.** A single forward sweep carries **two activation worlds side by side** through the **same
  shared crossbar**; only the cheap activation buffers double, not the Scaps (the weights).

**Why "direction is expensive" is an *analog* statement.** What a forward-only local rule removes is the **transposed
crossbar, the stored activations, and the cross-layer credit chain** a backward pass needs — the analog-expensive parts
(extra charge cycles, routing, buffers). The sign-plus-delta of a local update is cheap to *decide*. **Two honest
limits:** (1) a local rule still pays the intra-layer error→ΔW product and the per-sample norm — it removes the
*cross-layer* chain, not the *local* update; (2) Stage 1's cost was a structural (op-count) argument. **Phase 8 closed
that gap** with a hardware-meaningful behavioral meter (§4): on a compute-in-memory substrate the many crossbar MACs are
near-free and the **ADC / data converters dominate**, which is exactly what makes the two-brain economy pay off in
energy, not just in op-count. Device physics (SPICE, PVT, finite write precision, capacitor leak) is still deferred.

---

## 2 · The cheap brain: SCFF (the 80%), frozen — the committed essence

*The full derivation (the six-phase arc, the depth cure, the noise fix, the paper-by-paper ledger) is in
[`phase6-final-architecture.md`](phase6-final-architecture.md). Here is the committed cell and the two ideas an outsider
must carry into the GD half.*

**The committed cell — `NoiseAugContrast`.** An **L = 12, width-64** SCFF bulk. Each layer is `h = ReLU(W a + b)`
followed by a **mandatory per-sample L2 normalization** (`a ← h/‖h‖`; no batch/running statistics — this is what makes it
continual-friendly and nuisance-robust). The objective is **not** SCFF's energy-goodness `‖h‖²` (Phase 2 proved energy
measures *density*, and density does not compose with depth) but a **windowed two-view InfoNCE** contrastive loss
(GIM/CLAPP family, adapted to flat vectors): make two masked views of a sample, run both through the shared weights for a
**coordination window of `w = 2` adjacent layers**, pull the two views of the same sample together and push other
samples apart, with **temperature `τ = 0.2`**. Credit flows through only the `w` layers of the window — never the whole
stack — which is why **backward compute stays flat in depth** (the 80/20's depth-gating). Phase 5 found the sharper
temperature (τ 0.5→0.2) is a *direction* lever (~82% survives an lr-matched control) that carries the representation to
its own full-credit ceiling; Phase 6 added **one noise-augmented view** (`σ_aug = 1.0`, broad iid) so the composed class
direction is **noise-invariant** — a forward-only Jacobian/Tikhonov smoothing. Full config: `τ=0.2`, `w=2`/stride 2
(`w=4` a bounded depth-closer), mask `r=0.5`, `σ_aug=1.0`, `B=32`, lr `0.03`, no residual, per-sample norm.

**Idea one the GD half inherits — the bulk composes depth but *trails on raw static accuracy, by design*.** On a
synthetic headroom microscope the deployed readout (0.550) beats a genuinely-tuned backprop MLP (0.531) at matched
budget, and it wins the **continual** regime decisively — but it is a **structure learner with a cheap namer, not a
global error-minimizer**, so it trails on raw single-task accuracy and many-class problems. The GD namer's job is to
extract the class names from that structure as cheaply and as spine-cleanly as possible — not to fix the bulk's static
accuracy (it cannot; the bulk is frozen).

**Idea two — the bulk drifts, and the spine is directional.** As SCFF learns forward-only on a stream, its feature map
**rotates**. A fixed head goes stale; a re-fit head does not (§5.1). And the noise that threatens the design is
*directional* — a coherent shift along the class axis, invisible to a per-sample cosine, caught only by *retention of the
class direction*. Phase 6 hardened the dominant **tap** channel (directional retention 0.817→0.865, 5/5) forward-only,
improved clean accuracy, and kept the continual win (BWT −0.022→−0.017), but named one residual it cannot reach
forward-only — the **input-transducer directional channel** — and handed it to the GD read side. **Phase 9 closed that
residual** (§5.5). These two facts — a rotating bulk and a directional read-side residual — are exactly what the whole
Stage-2 loop is built to survive.

---

## 3 · The precise brain: the namer (the 20%) — and it is NOT gradient descent (Phase 7)

SCFF organizes the world but cannot name it. The precise brain reads SCFF's features (via taps; it **never writes** into
the SCFF stream — the stop-gradient envelope, unbroken since Phase 2) and maps them to real classes — and *only* that.
Stage 1 froze the SCFF half; Stage 2's whole job was this ~20%. The first thing Stage 2 found overturned the plan.

**The "20% GD" is a role, not a method — the committed namer has no gradient.** Phase 7 raced nine heads on a
pre-registered rubric (accuracy × continual-safety × spine-cleanliness × cost). The winner is **RanPAC** — a *frozen
random ReLU projection* of the features into a high-dimensional space, followed by a **running-Gram ridge prototype**
`W = (G + λI)^{-1} M` (`G` the projected feature Gram, `M` the class-sum matrix). No gradient, no backward pass,
**closed-form and streaming.** It **ties** the genuinely-tuned gradient MLP anchor on accuracy × BWT (a 3-way statistical
tie {MLP, RanPAC, SLDA}), **leads** on natural digits (0.949, #1, near-zero forgetting), **passes the A6 continual gate**
(the *trained* cosine-softmax and max-magnitude FeCAM heads are struck — their trained weights carry a recency bias), and
is the most spine-clean of the tied cluster. So the precise brain is a **closed-form analytic head**: the cheap brain
already did the representational work, so naming reduces to a **convex, one-shot solve** — the "gradient descent" the plan
assumed for the 20% is not needed at all. *(This retired the old "GD = residual boosting blocks" plan: boosting is dropped
for a single frozen bulk + read-only heads; the P2.5 forward-leak wall forbids re-injection.)*

**The spine bends here, honestly.** The one *direction-pure* head — a **cosine** classifier — is perfectly spine-clean
(argmax-flip 0.000) but **sub-competitive** where the bulk has real structure. The winning ridge head reads a
**magnitude** (a Mahalanobis/ridge distance), yet is **recency-robust by having no trained weights** (recency-robust ≠
direction-reading). We state this plainly: **magnitude-wins-spine-bends**, with the price shrinking 4× from synthetic
(Δ=0.128) to digits (−0.036) to CIFAR-flat (≈0) — the cosine head is the spine-pure option kept as a north-star signal
(§10), while the deployed head is the ridge, chosen on the measured rubric. **Two guesses the sims overturned:** the
class-imbalance guard is **class-balanced reservoir (cbrs), not AIR** (AIR over-corrects); and the "multimodality cliff"
we feared is **anisotropy (a tied covariance), not multimodality** (natural features are unimodal — the fix is a
closed-form tied covariance, no non-convex mixture).

**Cost picks the deployed head (Phase 8's first job).** RanPAC's random projection is ~200× the per-name cost of the
**second** tied head, **SLDA** (Streaming Linear Discriminant Analysis — per-class running means + one shared, tied
covariance; classify by the LDA rule). On the ADC-centred meter SLDA names the world **69× cheaper** and, measured *live*,
ties or beats RanPAC's accuracy. So **SLDA is deployed; RanPAC is the accuracy/spine reference.** Both are gradient-free.
The one new primitive both need is a streaming **`partial_fit`** — a running Gram `(G, M)` with an EMA forget `λ_ema`,
guarded ≡ a full batch fit to 4e-15.

---

## 4 · The economy: *when* the namer pays, and *what it truly costs* (Phase 8)

The chip runs forever, so the namer cannot pay a full solve every step. Phase 8 turned **both brains on together for the
first time** (SCFF learns forward-only on every input; the namer tracks the drift) and answered *when* the namer fires and
*what it costs in energy* — not op-count.

**The awake gate (a drift-detection economy).** Every step: SCFF forward + local update (**always**, op a); the namer
forward (**always**, op b); the namer's `partial_fit` (**gated**, op c) — fired only when an **awake gate** decides the
cheap path has stalled. The committed gate is **DDM** (Drift Detection Method, a two-threshold error detector) reading a
**class-direction tap-drift** trigger (the drift of the tap features *along the class axis* — a direction). Periodically,
a **sleep** (op d) re-forwards the raw LUT prototypes through the current SCFF map, rebuilds the Gram, and re-solves.

**The metered 80/20 is real — and the gate *creates* it.** With the committed gate on, the namer is **12.1% of total
substrate energy** (`GD-share` 0.121 ≤ 0.25 on the behavioral ADC-centred meter); turn the gate off (fire every step) and
it balloons to **77.8%**. This is the first time "80/20" is a measured hardware-shaped number rather than an op-count tag.
And **OURS ≈ half the energy of backprop-plus-replay** at matched retention on the same substrate table (bp_ratio 0.501).

**The crux inversion — the gate is *safety*, not just thrift.** The assembled economy holds worst-point (pre-sleep) BWT at
**0.000** on the Phase-8 stream (0/5 seeds regress vs the boundary oracle). The profligate **always-pay** loop — namer
every step — *forgets* (worst-BWT −0.137) by chasing the recency-skewed stream. **Firing more forgets more.** So the gate
is a continual-**safety** mechanism the way a good sleep schedule is, not merely a cost saver. **The spine, demonstrated
cleanly:** the trigger fires on the class **direction** (invariant to a nuisance covariate, 0.84× baseline) not on a
**magnitude** (the magnitude-of-shift null spikes 10× and false-fires on 94% of nuisance steps — density ≠ class, and the
gate reads the right side of it).

**Why analog — the substrate decomposition (the professor's 2×2).** Priced against the *conventional* approach (real
backprop+replay on a digital von-Neumann/GPU-class accelerator), the chip is **~15.4× cheaper** in energy, and the win
**factors cleanly**: **~5.4× is the analog substrate** (compute-in-memory — the ~8×10⁸ SCFF crossbar MACs are near-free
while a digital machine pays the memory wall on every one, ~75× more MACs than ADC ops) **× ~2.9× is the 80/20 algorithm**
(our gated, backward-pass-free loop vs backprop+replay on the *same* digital substrate). The 80/20 is
**substrate-independent** (GD-share 0.11–0.16 on either); the analog advantage is a **conservative floor** — ≥2.7× even at
the most-generous arithmetic-only digital assumption, growing past 50× once the memory wall is counted. (Digital numbers
are Horowitz-anchored behavioral, not an empirical GPU measurement.)

---

## 5 · The lifelong maintenance loop, tuned then FROZEN (Phase 9)

Phase 8 shipped the loop on a **single-pass** stream. Phase 9 asked whether the loop *around* the frozen head is actually
tuned for a **lifelong** stream — one that revisits its tasks for many cycles, so drift accumulates — then **locked it**.
Five knobs, each tuned against **internal** signals only (the measured drift, BWT vs the boundary oracle, the metered
energy) — **never** the Phase-10 backprop baseline (the freeze discipline). The result was not "polish": it discharged the
founding assumption and caught one real gap.

### 5.1 The founding assumption, measured — the bulk ROTATES, it does not FORGET (P9.0)

The whole cheap-replay story rests on "SCFF doesn't forget → sleep is cheap." It had never been measured, and it must be
measured with the right instrument: a *frozen* linear probe is basis-dependent (a pure rotation tanks it and reads as
forgetting). So the verdict keys on a third curve — an **optimal probe *re-fit* on the current bulk**, scored on held-out
early-task data (Davari, *Probing Representation Forgetting*). Over a lifelong stream: the cosine-to-birth settles ~0.65
(the taps rotate ~36%, never collapsing); the *frozen* probe rots to ~0.07 (a fixed head loses the rotating world — what
sleep exists to fix); but the **re-fit** probe stays at or above its birth score throughout (final 2.2×, min 0.966). **The
bulk rotates but does not forget.** So a periodic sleep re-solve suffices, and a drift-slowdown (N2) is **not mandatory.**

### 5.2 N2 struck — the drift is already tracked (P9.1)

N2's only job would be to make the namer chase the rotation *less often*. Two read-side arms were raced: **EMA-view** (the
namer reads a per-tap EMA; SCFF untouched) and **LLRD-rate** (a subclass slows the late-read layers' SCFF update,
rate-only only if the representation guard holds). No arm sleeps sparser or improves worst-BWT; EMA-view *worsens* it
(−0.383 vs −0.317 — it introduces a train/eval frame mismatch). The drift is rotation-only and the cadence already tracks
it, so N2 has nothing to grip. LLRD is honestly rate-only (early/mid taps move 0.00 — no Stage-1 reopen). **N2 struck** —
the last open decision-record knob resolves.

### 5.3 Keep all-tap consolidation — capacity is the margin (P9.2)

Could sleep consolidate at a *shorter* read depth (the deployed short reader P5 found reads the flat home ~8× cheaper) and
still hold A6? The truncated readers are **12–52× cheaper** on the sleep refit, but their worst-point A6-BWT is materially
worse (−0.511 / −0.373 vs all-tap −0.317, beyond the δ_acc=0.02 bar). At the worst mid-stream point — right after a revisit
shifts the class emphasis — the short reader has less capacity to keep old and new classes separable under the rotating
frame, so it forgets more. **All-tap's capacity is the margin that absorbs the drift; keep it.**

### 5.4 Bounded-LUT eviction = CBRS (P9.3)

A truly lifelong stream forces a **bounded, evicting** prototype store — the one thing Phase 8 never had (its streaming
sleep re-solved over a fixed balanced probe). Phase 9 built the accumulating `StreamingLUT` and raced eviction policies at
a pinned pressure-point cap. At a tight cap the bound bites — *no* bounded policy matches the unbounded oracle (that gap is
a property of the *cap* — the scaling law — not the policy). Among bounded policies, **CBRS** (class-balanced reservoir) is
**best-bounded**: it keeps prototypes balanced across classes, so it **spans the class *directions*** even at a tight
budget; reservoir/recency skew toward the recent bursty majority and the old class directions narrow → forgetting (−0.400
vs −0.607 / −0.707). The **herding** null (keep the class *mean* — a magnitude) *ties* CBRS here, because on this task the
raw dense-center ≈ the direction-span (density ≈ class at the buffer) — reported as a **buffer-spine null**, not a spine
win. The holding cap **grows with #classes** (a memory-scaling law). **CBRS committed** (it was already the Phase-8 loop's
sleep guard; Phase 9 confirms it under a bounded stream).

### 5.5 The read-side residual, resolved by the sleep mechanism itself (P9.4)

Phase 6's named residual — the **input-transducer directional** offset SCFF's per-sample norm cannot remove forward-only —
really dents the committed SLDA loop (an earn-its-place gate fires: retention drops +0.115, 5/5; worst seed collapses to
0.504). The read-side defense is **prototype re-anchoring**: re-forward the raw LUT through the *current* bulk under the
*same* device offset → prototypes that are drift-free and shift-*consistent* with the read. Retention recovers to **0.986**
(every seed ≥ 0.977). This is the plan's *own sleep mechanism* applied under shift — **no new organ, no covariance estimate**
(the planned SLDA-covariance fallback was never needed), and it is **direction-grounded** (the prototypes move *with* the
class axis, never an entropy/confidence magnitude). **The Phase-6 "scoped-YES → Stage-2 read-side" debt is discharged;**
the residual is defended, not handed to the analog layer.

### 5.6 Assemble + FREEZE — and the freeze caught the one real gap (P9.5)

Four of five knobs kept the committed loop, so the assembled loop equals the Phase-8 shipped object bit-for-bit. **The
first freeze attempt failed — honestly.** At the inherited Phase-8 **grid-8** sleep cadence, the loop failed the worst-point
oracle-veto in **2/5 seeds** on the lifelong *revisit* stream (worst-BWT −0.517 / −0.439 vs oracle −0.317 / −0.272): sparse
sleep lets the pre-sleep state fall into deep troughs between sleeps on high-variance seeds. Since the gate/trigger are
committed (out of Phase-9 scope) and every knob was struck/kept (0/5 regression vs the shipped object), the one P9-legal
lever was the sleep **cadence** — the Phase-8 "cadence is drift-rate-conditional" debt, now owed. A cadence re-confirm
(swept `{2,4,5,6,8,16}`, dense→sparse) settled it: the **freeze band is grid-2 → grid-6** (all clear the veto at held
accuracy and GD-share ≤ 0.25), because frequent consolidation keeps the pre-sleep state fresh so the deep troughs never
form. This overturned the live diagnosis that the gap was the committed gate's *fire-timing* (unfixable) — the lever was
frequency. **grid-4 is the knee** (the best absolute worst-BWT of the whole frontier, −0.028; grid-5/grid-6 are cheaper
viable options); the two failures split by axis — **grid-8 fails the veto** (sparse-sleep troughs) while **grid-16 fails on
accuracy** (6 sleeps under-consolidate → AA 0.458; not random, the over-sparse cliff).

Re-frozen at **grid-4**: worst-point BWT **−0.028** (ties the boundary oracle, 0/5 regress), AA **0.494** (= the shipped
object), metered GD-share **0.178 ≤ 0.25**. The frozen loop is an **order of magnitude safer** at the worst point than the
shipped grid-8 loop on the lifelong stream (−0.028 vs −0.317) — the Phase-8 cadence, tuned on a single pass, silently
under-consolidated under revisits, and Phase 9 restored the near-flat continual-safety. **The object is frozen** at commit
`59d2720`; every knob is enumerated in its manifest.

---

## 6 · How the whole neocortex runs, and where it wins

```
  stream x_t ──▶ [ SCFF bulk: L=12, w64, InfoNCE window w=2, τ=0.2, +noise-aug view σ_aug=1.0 ]   ← FROZEN (Stage 1)
                     │  every step:  ReLU → per-sample L2-norm ; windowed 2-view InfoNCE local update  (op a, ALWAYS)
                     │               the map ROTATES as it learns — but does not FORGET (a re-fit probe still decodes)
                     ▼
               taps  (the namer READS, never writes — stop-gradient envelope)
                     │
                     ▼
     [ the namer: SLDA (deployed) / RanPAC (reference) — closed-form, streaming, NO gradient ]
                     │   op b: namer forward, ALWAYS
                     │   op c: partial_fit, GATED by DDM on the class-direction tap-drift trigger   (the ~metered 12–18%)
                     │   op d: SLEEP — re-forward the bounded CBRS LUT through the CURRENT bulk → rebuild Gram → re-solve
                     │           cadence grid-4 (lifelong) · all-tap consolidation · proto-reanchor under a read-side shift
                     ▼
                 ŷ_t = class            economy: GD-share 0.178 ≤ 0.25 · worst-BWT −0.028 (ties oracle) · FROZEN 59d2720
```

Measured against **internal** references (the boundary oracle, the always-pay ceiling, the metered energy) — the fair
backprop fight is Phase 10:

- **It is a continual learner run LIVE — the decisive win.** Both brains live on a lifelong CI+revisit+nuisance stream, the
  namer tracking a rotating bulk through a gate + sleep, and it holds worst-point BWT at the boundary-oracle level (−0.028,
  0/5 regress) — *an order of magnitude safer than the un-retuned shipped cadence*. The mechanism is the whole point: the
  bulk **doesn't forget** (§5.1), so sleep only re-aims the cheap namer over a **bounded, class-balanced** buffer — it never
  replays gradients through the network. That is why the recovery is cheap.
- **The precise brain is cheap because it is *not* gradient descent.** A closed-form streaming solve (SLDA) names the world
  at ~1.5% of the substrate's per-name energy of the reference head, ties it live, and needs no backward pass — the 20% is a
  *role*, discharged analytically (§3).
- **The economy is cheaper *and* safer, metered.** GD-share 0.121 (P8 stream) / 0.178 (the safer P9 grid-4 cadence), OURS ≈
  ½ backprop+replay energy, and the gate that saves the energy also **prevents** the forgetting that firing-always incurs.
- **It holds its class direction under the substrate's own noise, on both channels.** The dominant tap channel is hardened
  in the frozen bulk (Phase 6); the input-transducer directional residual is defended read-side by prototype re-anchoring
  (§5.5) — the once-sharpest open silicon risk, now answered on both channels.
- **It trails on raw static accuracy and many-class problems, by design.** A structure learner with a cheap analytic namer,
  not a global error-minimizer (§2). Absolute live AA on the synthetic home is modest (0.494 — task difficulty, not
  forgetting: worst-BWT −0.028). The honest static/many-class number on natural data (A5) and the fair same-budget baseline
  are **Phase 10** (§10).

---

## 7 · What we extended, paper by paper — the GD half (the cheap-brain ledger is in the v1.1.0 file)

**RanPAC (Random Projections + Accumulated class prototypes, NeurIPS 2023)** *(the committed namer's form)*
- *Kept:* a **frozen random ReLU projection + a running-Gram ridge prototype** — a gradient-free, closed-form, streaming
  head that is strong for class-incremental learning on a frozen backbone.
- *Changed / extended:* we run it on our **SCFF** features (not a pretrained ViT), race it on a **spine** rubric
  (direction-cleanliness, not just accuracy), add a **class-balanced-reservoir** imbalance guard, and — on the cost meter —
  **deploy its cheaper twin (SLDA)** while keeping RanPAC as the accuracy/spine reference.

**Deep SLDA (Hayes & Kanan, CVPR-W 2020)** *(the deployed head)*
- *Kept:* **streaming per-class means + one shared (tied) covariance**, classify by the LDA rule — an online, closed-form
  head with no gradient.
- *Changed / extended:* made it the **deployed namer** of a two-brain loop (metered 69× cheaper than RanPAC, ties live),
  driven by a new streaming `partial_fit` primitive; its shared covariance is the **anisotropy fix** Phase 7 found (not a
  multimodal mixture).

**DDM / ADWIN (Gama 2004 / Bifet & Gavaldà 2007)** *(the awake gate)*
- *Kept:* an **error-drift detector** as the online learning-gate trigger.
- *Changed / extended:* the detector reads a **class-direction tap-drift** signal (a *direction*, spine-clean), not raw
  error — and the gate's value turned out to be **continual safety, not just cost** (firing more forgets more, §4).

**CBRS (Chrysakis & Moens, ICML 2020) & herding (iCaRL, CVPR 2017)** *(bounded-buffer eviction)*
- *Kept:* **class-balanced reservoir sampling** as the bounded-store policy; **herding** (keep the class mean) as the
  baseline.
- *Changed / extended:* raced them under a **bursty, class-imbalanced lifelong** stream on a **spine** framing — CBRS spans
  the class *directions*, herding keeps the *mean* (a magnitude) and is the **buffer-spine null**; plus a **cap × #classes
  scaling law**. GSS was dropped (it needs gradients we don't have).

**Latent Replay (IROS 2020) & Layerwise Proximal Replay (2024)** *(consolidation depth)*
- *Kept / tested:* the idea of consolidating at a chosen **replay depth** (slow below, learn above).
- *Result:* on our **live lifelong** loop the truncated depths forget more (capacity is the margin) — we **keep all-tap**
  (§5.3). A cheaper-refit option that did not pay under live drift.

**Probing Representation Forgetting (Davari et al., CVPR 2022)** *(the drift instrument)*
- *Kept:* an **optimal probe re-fit on the current representation** as the *true* forgetting measure, with rotation factored
  out — the decisive P9.0 instrument that separated **rotation from forgetting** (§5.1).

**Test-time prototype shift (2024) / SDC→LDC drift compensation (2020→2024)** *(the read-side defense)*
- *Kept:* re-estimating prototypes under a distribution shift as a **feature-level** defense (scalar temperature scaling is
  ineffective under shift).
- *Changed / extended:* our **`proto_reanchor`** re-forwards the *raw LUT* through the *current bulk* under the shift — no
  learned projector, no covariance estimate; the learned drift-compensation projector (LDC) is the cited **road-not-taken**
  (out of the read-side/rate-only scope).

**A-GEM / ER (1812.00420) & REMIND (2020)** *(the owed baseline / the anti-pattern)*
- *A-GEM/ER* = the **fair same-budget backprop+replay** baseline the architecture's headline must race — **Phase 10, owed.**
  *REMIND* (replay into a frozen backbone) is the **anti-pattern** our two-brain split is defined against (our backbone is
  unsupervised and *doesn't forget*, so only the tiny readout replays).

| paper | what we took | our extension / change |
| --- | --- | --- |
| **RanPAC** | random-projection + running-Gram ridge, gradient-free | on SCFF features; spine rubric; cbrs guard; SLDA deployed as the cheaper twin |
| **Deep SLDA** | streaming means + tied covariance, closed-form | the **deployed namer** (69× cheaper, ties live); streaming `partial_fit`; the anisotropy fix |
| **DDM / ADWIN** | error-drift detector as a gate | reads a **class-direction** trigger; the gate is **safety**, not just cost |
| **CBRS / herding** | class-balanced reservoir / mean-keeping | spine framing (direction-span vs mean = null); cap × #classes scaling law |
| **Latent Replay** | replay-depth consolidation | tested; **all-tap kept** (capacity is the margin under live drift) |
| **Davari 2022** | re-fit probe = true forgetting (rotation out) | the P9.0 rotation-vs-forgetting split — the founding assumption, measured |
| **proto-shift / SDC→LDC** | feature-level prototype re-estimation under shift | `proto_reanchor` (re-forward the raw LUT, no projector); LDC = road-not-taken |
| **A-GEM / ER · REMIND** | same-budget replay baseline · frozen-backbone replay | the **owed Phase-10 fight** · the **anti-pattern** we are defined against |

*(Digital energy anchor for §4's 2×2: Horowitz ISSCC 2014; the analog meter: DNN+NeuroSim, ISAAC ISCA'16, PUMA ASPLOS'19,
AIHWKit — all behavioral, not SPICE.)*

---

## 8 · The nine-phase journey that produced this model

One model, nine phases, one argument — a continual, substrate-native learner that pays for **direction** once. Its
*destination* held; several *mechanisms* the plan guessed were overturned by a simulation or a paper, never rescued by
tuning. The connective tissue is one recurring fault, **density ≠ class.**

1. **P1 — build the cell, find its home.** One SCFF+GD block generalizes better than backprop at ~10% backward cost, but is
   a weak density learner. Home = the **continual** regime, where sleep recovers what online backprop forgets.
2. **P2 — depth is not deep-SCFF's lever.** A deep SCFF stack can't earn depth (even a perfect oracle negative doesn't bend
   the curve — the failure is the energy functional). Depth = boosted shallow blocks.
3. **P3 — the objective reframe.** The wall is the **energy objective `‖h‖²`**, not locality. **Contrast (InfoNCE) + a
   coordination window** composes depth and re-earns the continual win. **Adopted; supersedes energy-goodness.**
4. **P4 — the capability map.** A substrate-native **continual** learner, not a static-accuracy competitor. Flagged two
   wounds: a depth **decay** (→ P5) and **noise sensitivity** (A7 → P6).
5. **P5 — close the cheap brain's *learning*.** The decay was **objective-locality, not a Tunnel**; cured by a sharper
   temperature (direction, lr-matched) + a short fixed reader. **The cheap brain's design is finished.**
6. **P6 — harden it against noise.** A7 is real, OURS-specific, directional; a **noise-augmented view** hardens the tap
   channel forward-only, keeps the continual win, names the input-transducer residual → Stage 2. **Scoped-YES.**
7. **P7 — the namer is NOT gradient descent.** A closed-form streaming head (**RanPAC** / **SLDA** committed, cbrs guard)
   ties a tuned MLP and passes the A6 gate; the spine bends (magnitude-wins). *The 20% is a role, not a method.* **(S11.)**
8. **P8 — the economy, run LIVE.** Both brains live; a **DDM** gate on a **class-direction** trigger meters the 80/20 real
   (GD-share 0.121), OURS ≈ ½ backprop+replay, and **firing more forgets more** (the gate is safety). Why-analog: 15.4× =
   5.4× substrate × 2.9× algorithm. **(S12.)**
9. **P9 — close & *freeze* the maintenance loop (this).** The bulk **rotates but does not forget** (measured); N2 struck,
   all-tap kept, **CBRS** committed, the read-side residual defended by **proto-reanchor**; the freeze caught the
   drift-conditional cadence (grid-8→**grid-4**) and **locked the object** at `59d2720`. **(S13.)**

---

## 9 · The committed object, and what's built vs designed

**The frozen neocortex loop (exact config).** `NoiseAugContrast` SCFF bulk (L12/w64, InfoNCE `τ=0.2`/`w=2`, per-sample L2
norm, one noise-aug view `σ_aug=1.0`, no residual) · deployed namer **SLDA** (RanPAC the reference), gradient-free/streaming
`partial_fit` · awake gate **DDM** on the **class-direction tap-drift** trigger · **all-tap** sleep consolidation · **CBRS**
bounded-LUT eviction · **proto-reanchor** read-side defense · **grid-4** lifelong sleep cadence · envelope: **GD reads taps,
never writes SCFF.** Live-safety: worst-BWT −0.028 (ties oracle, 0/5 regress), AA 0.494, GD-share 0.178. Locked at commit
`59d2720`. Methodology throughout: seeds `[42,137,271,314,1729]`, median [IQR], a difference "real" only if IQR-disjoint
**and** ≥4/5 by sign (paired-sign veto on every A6 re-check).

| part | status |
| --- | --- |
| SCFF contrast bulk + depth cure + noise-aug view (the frozen cheap brain) | ✅ **built & measured** (P1–P6) — behavioral sim (+ a behavioral noise model) |
| **The namer — RanPAC / SLDA, gradient-free closed-form** | ✅ **built & measured** (P7) — ties a tuned MLP, passes A6 |
| **The streaming `partial_fit` primitive** | ✅ **built & measured** (P8) — running Gram (G,M)+λ_ema ≡ batch to 4e-15 |
| **The awake DDM gate + class-direction tap-drift trigger** | ✅ **built & measured** (P8) — metered GD-share 0.121; the gate is *safety* |
| **The behavioral ADC-centred cost meter + the why-analog 2×2** | ✅ **built & measured** (P8) — relative-pJ, NOT SPICE |
| **Bulk-drift measured (rotation, not forgetting)** | ✅ **built & measured** (P9.0) — re-fit destruction ≥ birth |
| **CBRS bounded-LUT eviction + the cap×#classes scaling law** | ✅ **built & measured** (P9.3) — best-bounded; herding = the null |
| **All-tap consolidation depth; grid-4 lifelong cadence** | ✅ **built & measured** (P9.2 / P9.5) — the drift-conditional cadence, discharged |
| **proto-reanchor read-side residual defense** | ✅ **built & measured** (P9.4) — retention 0.79→0.99, direction-grounded |
| **The frozen loop, live-safe, locked** | ✅ **built & measured** (P9.5) — worst-BWT −0.028, hash `59d2720` |
| N2 drift-slowdown (EMA-view / LLRD-rate) | ❌ **struck** (P9.1) — no lever on rotation-only drift |
| Boosting blocks; adaptive early-exit; cosine spine-pure head | ❌ **dropped / struck / benched** (single bulk; fixed reader; ridge deployed) |
| On-chip negative streaming (CLAPP/LUT); mono-forward as a circuit; SPICE/PVT/device physics | 🟡 **designed, NOT built** — behavioral sim only |
| The fair same-budget **backprop+replay accuracy** fight; natural many-class **A5**; the multi-domain gauntlet; the noise showcase | 🟡 **Phase 10, owed** — the frozen object is the thing they race |

---

## 10 · What v2.0.0 freezes, and what comes next

**Frozen — the whole neocortex design is closed:** the cheap brain (§2, from v1.1.0), the gradient-free namer (SLDA), the
drift-gated economy (DDM + class-direction trigger + the metered ≤0.25 GD-share), the maintenance loop (all-tap · CBRS ·
proto-reanchor · grid-4 cadence), and the verdict that this is a **continual, substrate-native learner that names cheaply
and holds its class direction under the substrate's own noise.** These do not move without a result that overturns them.
*Frozen means the ideal-math design (plus behavioral noise and energy layers) is settled and the loop was locked at a hash
before the fight — it does **not** mean silicon-validated or benchmark-validated.*

**Phase 10 — the validation / the showcase (the honest fights, next).** Race the **frozen** object (it touches no knob):
the **existential** same-budget **backprop+replay *accuracy*** baseline (Phase 8 settled *energy*; this is the accuracy half
— the load-bearing test, since Phase 4's continual win was vs *naive* online-BP); the **multi-domain adaptive gauntlet**
(new / 1-back / all-previous accuracy + cumulative OURS-vs-BP cost — the money figure); the owed natural many-class **A5**;
and the **noise showcase** on a **held-out** battery (P9.4 tuned only on the home residual). The deliverable is an honest
**Pareto** verdict + the Stage-2 close-out. We may still win — only the readout replays and the bulk doesn't forget — but
it must be *shown*.

**The north star (deliberately not specced).** A recurrent, lifelong-learning "thinking" loop where *correctness is a
self-generated feeling* — the organs re-wired to run recurrently at inference (SCFF goodness → the feeling; the LUT → the
queried memory; the gate → think-until-the-feeling-crosses-θ). The **cosine spine-pure head** benched in Phase 7 and the
better-than-confidence per-sample selector parked in Phase 5 both come home here — the direction signals the recurrent
brain will read. After Phase 10, the analog-realism layer (SPICE / PVT) opens. *Simple intelligence first.*

---

## References (the papers this half stands on — the cheap-brain references are in the v1.1.0 file)

RanPAC ([2307.02251](https://arxiv.org/abs/2307.02251)) · Deep SLDA ([1909.01520](https://arxiv.org/abs/1909.01520)) ·
DDM (Gama et al., 2004) / ADWIN (Bifet & Gavaldà, 2007) · CBRS (Chrysakis & Moens, ICML 2020) · iCaRL / herding
([1611.07725](https://arxiv.org/abs/1611.07725)) · Latent Replay ([1912.01100](https://arxiv.org/abs/1912.01100)) ·
Layerwise Proximal Replay ([2402.09542](https://arxiv.org/abs/2402.09542)) · Probing Representation Forgetting
([2203.13381](https://arxiv.org/abs/2203.13381)) · Test-time prototype shift ([2403.12952](https://arxiv.org/abs/2403.12952))
· SDC ([2004.00440](https://arxiv.org/abs/2004.00440)) → LDC ([2407.08536](https://arxiv.org/abs/2407.08536)) · A-GEM
([1812.00420](https://arxiv.org/abs/1812.00420)) · REMIND ([1910.02509](https://arxiv.org/abs/1910.02509)) · does
continuous SSL forget ([2311.13321](https://arxiv.org/abs/2311.13321)) / CaSSLe
([2112.04215](https://arxiv.org/abs/2112.04215)). **Energy model:** Horowitz (ISSCC 2014) · DNN+NeuroSim · ISAAC (ISCA'16)
· PUMA (ASPLOS'19) · AIHWKit — behavioral, not SPICE. The **cheap-brain** lineage (SCFF, GIM/CLAPP, SimCLR,
Distance-Forward, DeeperForward, BoostResNet, BYOL, Mono-Forward, AIHWKit/Rasch, Bishop, Noise2Noise, LP-FT):
[`phase6-final-architecture.md`](phase6-final-architecture.md) §5. The arc behind every claim:
[`stage1-report.md`](stage1-report.md) · [`stage2-report.md`](stage2-report.md) and each `phaseN/README.md`. The decision
record: [`idea/main.ideas.v1.md`](../idea/main.ideas.v1.md) (N1–N3 + S1–S13). The cheap-brain snapshot this builds on:
[`phase6-final-architecture.md`](phase6-final-architecture.md) (v1.1.0). The frozen loop: commit `59d2720`.
