# The neocortex — final architecture (v2.0.0, the complete two-brain loop, frozen)

> **✅ Validated by Phase 10 (2026-07-03).** This snapshot is the object *as frozen at Phase 9* — written
> **pre-verdict, by design** (freeze in P9, judge in P10). Phase 10 has since raced it, untouched, against a fair,
> budgeted, tuned BP+replay baseline: the verdict (**S14**) is a **substrate-native continual learner** — it ties the
> fair baseline on the continual home, trails on natural digits (continual, not static), and **wins** continual
> safety (≈10× less forgetting) + noise (every held-out channel); the energy edge over conventional GD is
> substrate-realized. The verdict lives in [`validation-report.md`](validation-report.md) + [`phase10/README.md`](phase10/README.md);
> this file is left **period-correct** — the "still owed → Phase 10" notes below reflect its freeze state.
>
> **What this is.** The single, self-contained account of the model we built across **nine** phases of draft 6.0 — the
> whole chip, both brains, the lifelong maintenance loop, now **frozen**. It is written so an **outside researcher can
> understand the entire model from this one file**, without opening a single `phaseN/` report. It is the current head of
> the line and **supersedes [`phase6-final-architecture.md`](phase6-final-architecture.md)** — which is kept, unchanged,
> as the **v1.1.0 cheap-brain-only snapshot** (SCFF alone, before it had a namer). What v2.0.0 adds is the other half of
> the chip and the loop that keeps it alive: the **precise "namer"** that puts our labels on the cheap brain's features
> (Phase 7), the **drift-gated economy** that decides when the namer pays (Phase 8), and the **lifelong maintenance
> loop** that survives forever and has now been **tuned against internal signals and locked** (Phase 9). The cheap brain
> (§2) is folded in **in full** below, so this file stands alone; the frozen v1.1.0 snapshot it was lifted from —
> [`phase6-final-architecture.md`](phase6-final-architecture.md) — is kept, period-correct, as the pre-namer milestone.
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
| **the gate / the trigger** | the **awake learning-gate** (Phase 8): run cheap SCFF every step; fire an expensive namer update only when a **drift trigger** says the cheap path has stalled. Committed gate = **DDM on the namer's error-EMA** (a labeled error-rate). A label-free **class-direction tap-drift** signal was *validated* (P8.2 — leads the error, spine-clean) but is **not the deployed trigger** — the north-star upgrade, not the shipped one (§4). |
| **sleep / the LUT** | periodic **consolidation**: re-forward a raw-prototype store (the **Hippocampus LUT**) through the *current* SCFF map, rebuild the running Gram, re-solve the namer. The LUT is a bounded, evicting store (§5.4). |
| **the frozen / oracle reference** | an *internal* reference that **cheats with hidden task boundaries** (sleeps/fires exactly at onsets). Matching it is the *win*; it is never a deployable path. Every Phase-9 verdict is measured against it, **never** against the Phase-10 backprop baseline. |
| **rotation vs forgetting** | the SCFF map **rotates** (a fixed head goes stale) but does not **forget** (an optimal probe *re-fit* on the current bulk still decodes the old classes). Phase 9 measured this; it is why cheap sleep suffices (§5.1). |
| **A7** | the eval-time **noise sensitivity** the Phase-4 capability map flagged as the cell's one honest NEGATIVE — the wound Phase 6 hardened (§2.5). |
| **directional retention** | the Phase-6 **noise metric** (the spine's form here): `acc(σ)/acc(0)` measured along the frozen class axis. Robustness = "the class *direction* survived," never Δaccuracy, never per-sample cosine. |
| **the two doors / the directional residual** | Door A = analog-substrate noise (tap / input / ADC / weight); Door B = the all-noisy data stream. Shared enemy: a **directional, non-zero-mean** perturbation aligned with the class axis — the residual that survives common-mode auto-zeroing. |
| **`NoiseModel` / projected-RMS / linear-readout control** | the behavioral analog-noise model (AIHWKit-structured); noise measured as **RMS projected onto the class axis** (matching iid and directional on the axis that matters); the **linear readout on raw input** carried as the relative-fragility yardstick (the decisive read is **OURS-vs-linear**). |
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

## 1 · The substrate, in one breath (enough to ground the rest)

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

## 2 · The cheap brain: SCFF (the 80%), frozen — the full derivation

*Everything in §2 was frozen across Phases 1–6 and is reproduced here in full so this file stands alone. The committed
cell's code name is **`NoiseAugContrast`** — an `L = 12`, width-64 SCFF bulk; final config `τ=0.2`, window `w=2`/stride 2
(`w=4` a bounded depth-closer), mask `r=0.5`, `σ_aug=1.0`, `B=32`, lr `0.03`, **no residual**, mandatory per-sample L2
norm. The five subsections derive each of those choices.*

### 2.1 The lineage, and the one wrong turn we corrected

**Forward-Forward** (Hinton 2022) replaces the backward pass with *two forward passes* — one on real ("positive") data,
one on fake ("negative") — training every layer locally to be **loud on the real, quiet on the fake**, no gradient
crossing a layer. Hardware-friendly (no transpose, no stored activations), but it needed *labels* to build the fakes.
**SCFF** (Self-Contrastive Forward-Forward, Nature Comms 2025) made the contrast from the data itself — a positive is a
sample paired with itself, a negative a sample paired with a *different* one, label-free — with an **energy** goodness
`G = ‖h‖²`. We adopt SCFF's **frame** (the only rule that is local *and* derivative-free *and* forward-only *and*
unsupervised at once — the only one that can live on the substrate), but **not its objective.**

Because energy-goodness has a fatal property *for us*, and finding it was the spine of Phases 1–3: **energy measures
density, and density is not class.** `‖h‖²` is loud where the *data* is dense, which recovers classes only when they
happen to *be* density clusters (a checkerboard or an equal-density spiral defeats it), and — worse — **density does not
compose with depth** (Phase 2's "depth wall"). The failure is in the **goodness functional itself**, not the choice of
negative: Phase 2 showed *even a perfect class-oracle negative* does not make energy compose, because no scalar that
measures a **magnitude** (`‖h‖²`) can encode a **direction** (the class axis). That is the spine, stated as an empirical
result about the objective.

### 2.2 The committed objective: windowed two-view InfoNCE

The fix changes *what "good" means* at each layer from **energy** to **information preserved about the class direction.**
The existence proof is **Greedy InfoMax** and **CLAPP**: forward-only, gradient-isolated, unsupervised modules trained
with a local **InfoNCE** loss whose representations *improve* layer over layer — the rising curve energy-goodness never
produced. We adopt that objective in the flat-vector form the substrate needs.

**Forward path (one layer).** Input-normalize, then each layer is a ReLU map followed by a **mandatory L2 normalization:**

$$a_0 = \frac{x}{\lVert x\rVert},\qquad h_l = \mathrm{ReLU}(W_l\,a_l + b_l),\qquad a_{l+1} = \frac{h_l}{\lVert h_l\rVert}.$$

**The local objective.** Credit spans a small **coordination window** of `w` adjacent layers. For a window at depth `s`,
take its input `a_s` and make **two randomly masked views** (each coordinate kept with prob `1 − r`, `r = 0.5`):

$$a^{(1)} = a_s \odot m_1,\qquad a^{(2)} = a_s \odot m_2,\qquad m_v \sim \mathrm{Bernoulli}(1-r).$$

Run **both views through the same shared weights** (the two rails of §1) for the `w`-layer window, giving L2-normalized
tops `u^{(1)}, u^{(2)} \in \mathbb{R}^{B\times d}`. Apply **InfoNCE** with the two views of the same sample as the
positive pair and the other samples as negatives:

$$S_{ij} = \frac{\langle u^{(1)}_i,\; u^{(2)}_j\rangle}{\tau},\qquad
\mathcal{L} = -\frac{1}{B}\sum_{i=1}^{B} \log \frac{\exp(S_{ii})}{\sum_{j=1}^{B}\exp(S_{ij})}.$$

The gradient flows through **only the `w` layers of the window** — never the whole stack — which is why **backward cost
stays flat in depth** (§4's 80/20). **Why two masked views:** they share a sample's **class direction** but differ in
accidental detail, so pulling them together while pushing other samples apart forces each layer to **keep the class axis
and discard the rest** — provided the class signal is *distributed* across coordinates (why a 50% mask retains it in
expectation). We did not prove this; we **tested it** — masked-view *contrast* composed with depth, while the
pre-registered favorite, masked-feature **reconstruction**, *failed* (it preserved density, below random). **What is ours
vs GIM's:** GIM/CLAPP already showed local InfoNCE composes *on data with spatial/temporal structure*; ours is making it
work on **structureless flat vectors** via the two-masked-view target, plus the Phase-5 depth-decay cure (§2.3) and the
Phase-6 noise-hardening (§2.5).

### 2.3 The two knobs that close the depth problem (Phase 5)

Even with contrast, the representation composed for only ~5 layers, then **decayed** — it drifted *off the class
manifold* once a layer's abstraction saturated (alive, full-rank, but mis-aimed — a *direction* failure, density ≠ class
a fifth time). Two **free, forward-only** knobs cure it:

- **Temperature `τ` (the free lever).** A *sharper* InfoNCE temperature (`τ = 0.2`, from `0.5`) concentrates each update
  on the hardest negatives, making it more **class-selective**. Sharpening also raises the gradient scale (`∝ 1/τ`), so
  part of the gain could be a disguised larger step — a **learning-rate-matched control** isolates it: **~82% of the lift
  survives the lr-match**, so it is mostly *direction* (class-selectivity), not step size. (Too sharp, `τ ≤ 0.05`,
  collapses — there is a floor.)
- **Coordination window `w` (the bounded reach).** `w` is mechanically the **truncation length of blocked
  backpropagation** — within `w` adjacent layers gradients flow, across windows they are cut (the LoCo /
  Distance-Forward-O family, supplied forward-only). Committed **stride = w = 2**; `w = 4` a bounded depth-closer; the
  diagnostic **`w = 12` (one window over the whole stack) is a full backward pass** — *forbidden*, used only as a ceiling.

**What actually earns the depth (the flagship claim, with its uncertainty).** At `τ = 0.2`, `w = 2` — the committed,
substrate-legal cell — the **deployed readout reaches `0.550 [0.545–0.553]`, above a genuinely-tuned BP MLP at matched
budget (`0.531 [0.531–0.533]`)** — IQR-disjoint, 5/5 by seed. The linear-probe tail rises `0.435 → 0.530` (`w = 2`),
closing to **`0.562` at `w = 4` ≈ the `0.556` `w = 12` ceiling.** **Read the `w12` comparison correctly:** `w = 12` is
one credit window over the whole stack — effectively *ordinary backprop on this 12-layer cell* — so "reaching the `w12`
ceiling" means a **bounded forward-only window recovers almost all of what unconstrained credit would give on this
objective**, *not* "matches an external backprop." So "depth solved" = the cheap levers carry the representation to *its
own full-credit ceiling*, on a **synthetic headroom microscope** built to have depth headroom (a representation/readout
result, not a benchmark). The forbidden `w = 12` only proves the decay was **objective-locality (curable), not an
intrinsic wall.** **The mandatory L2 norm is load-bearing twice:** it forbids a layer cheating by inflating `‖h‖`, *and*
being **per-sample** (no batch/running statistics) it is what makes the cell continual-friendly and nuisance-robust —
and, honestly, is *also* the source of the eval-time noise sensitivity (A7, §2.5).

### 2.4 How the contrastive objective runs on the substrate (the honest bridge)

The simulation and the intended chip use the objective differently, and we are explicit about which is which. **In
simulation (every number here):** standard **mini-batch InfoNCE** — `B` samples, two masked views, the full `B×B`
similarity, `B−1` in-batch negatives. **On the chip (designed, not built):** the two rails carry the **positive pair**
through the shared crossbar (the "one charge cycle, not two" win), and the **negatives are supplied by the Hippocampus
LUT** — stored prototype activations drawn a few at a time, a contrast against a rolling set accumulated over time. This
is the **CLAPP route** (InfoNCE made single-sample and Hebbian-plausible for online hardware) — which is *why CLAPP is in
the reference list.* **Resolving "no batch statistics":** mini-batch InfoNCE *does* couple samples (the denominator is
the batch), so the precise claim is **not** "no batch coupling" but "**no running / normalization statistics**" (the L2
norm is per-sample; nothing carries one task's distribution into the next) — which is *why* the continual safety holds
(§4). Three honest Stage-2 gates remain: the LUT-streamed-negative estimator differs from in-batch (the `τ` lever works
*by* concentrating on the hardest negatives, which a deduplicated pool may lack); the softmax/normalizer is a **real
digital block**, not a free crossbar op; and a **bounded**, task-spanning LUT under a lifelong stream must evict (the
continual-safety mechanism's tension — Phase 9 addresses it, §5.4).

### 2.5 The noise-hardened objective (Phase 6)

The cell will run on an **analog substrate** (drifting charge, offset op-amps, quantizing ADCs) and a **never-clean data
stream**, and Phase 4 returned one honest NEGATIVE: eval-time noise (**A7**). Phase 6 is its SCFF-side close-out. **Why
the fix must live here, not in the readout:** by **LP-FT**, a trained head *preserves* but cannot *manufacture* backbone
robustness, and A7 is born in SCFF's own **per-sample L2 norm** — so no downstream namer can rescue it; the fix is
upstream, which is why noise got its own phase *before* the namer. **Naming the enemy (P6.0):** against a behavioral
`NoiseModel` (AIHWKit-structured) at matched **projected-RMS on the class axis**, A7 reproduces and is **OURS-specific** —
a directional perturbation degrades OURS's readout **~2× more than a linear-readout control** (retention ~0.60 vs ~0.96,
5/5), while the **common-mode** channel is auto-rejected by the same per-sample norm. **Why "retention," not cosine
(density ≠ class, a sixth time):** iid noise **rotates** each representation (per-sample cosine catches it), but the
dangerous **directional** enemy is a **coherent translation** along the class axis — it barely rotates any single vector
(`cos ≈ 0.97`) yet slides the whole cloud off a fixed readout, so cosine is nearly blind to it; the true read is
**retention of the class direction.** **The fix: one noise-augmented view.** `NoiseAugContrast` corrupts **one** of the
two InfoNCE views at train time, teaching the composed class direction to be **noise-invariant**, forward-only — the
surrogate for a Jacobian/Tikhonov penalty (Bishop: input-noise ≈ a first-order Tikhonov regularizer). **A guess the sims
overturned — generic, not directional:** a random-axis control refuted the directional-specific augmentation (`iid ≥
randax > dir`) — broad smoothing wins, because the enemy's axis is unknown and label-free at train time. **What it buys
(σ_aug = 1.0, n = 5):** the dominant tap-directional retention lifts **0.817 → 0.865** (5/5), clean accuracy *improves*
(0.526 → 0.555), the **A6 continual win is kept and slightly improved** (BWT −0.022 → −0.017 — a noise-robust
representation is also drift-robust), and it holds on real data (digits 0.763 → 0.888). **Door B** (can a direction form
when *every* sample is corrupted?): yes — the direction still forms from a fully-noisy stream (ratio-to-clean 0.93
zero-mean, 1.00 directional). **The honest scope — a *partial* crossing:** the tap lift is near, not decisively above,
the pre-registered 0.90 band, and the **input-transducer directional channel is not reached forward-only** (0.733 →
0.696) — a generic augmentation cannot harden a channel it never corrupts. That residual is handed to **Stage-2
read-side** as a named brief — and **Phase 9 discharges it** (§5.5).

**The two ideas the GD half inherits.** *One — the bulk composes depth but trails on raw static accuracy, by design.* The
deployed readout beats a tuned BP MLP on the synthetic microscope (0.550 vs 0.531) and wins the continual regime
decisively, but it is a **structure learner with a cheap namer, not a global error-minimizer** — so it trails on raw
single-task accuracy and many-class problems, and the namer's job is to *extract* the class names, not fix the frozen
bulk's static accuracy (it cannot). *Two — the bulk drifts, and the read is directional.* As SCFF learns forward-only its
map **rotates** (a fixed head goes stale; a re-fit head does not, §5.1), and the noise that threatens it is *directional*
(caught only by retention of the class direction). A rotating bulk and a directional read-side residual are exactly what
the whole Stage-2 loop is built to survive.

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
cheap path has stalled. The committed gate is **DDM** (Drift Detection Method, a two-threshold detector) on the namer's
own **error-EMA** — a labeled error-rate (the frozen manifest is `gate="ddm", trigger="error_ema"`). Periodically,
a **sleep** (op d) re-forwards the raw LUT prototypes through the current SCFF map, rebuilds the Gram, and re-solves.

**The metered 80/20 is real — and the gate *creates* it.** With the committed gate on, the namer is **12.1% of total
substrate energy** (`GD-share` 0.121 ≤ 0.25 on the behavioral ADC-centred meter); turn the gate off (fire every step) and
it balloons to **77.8%**. This is the first time "80/20" is a measured hardware-shaped number rather than an op-count tag.
And **OURS ≈ half the energy of backprop-plus-replay** at matched retention on the same substrate table (bp_ratio 0.501).

**The crux inversion — the gate is *safety*, not just thrift.** The assembled economy holds worst-point (pre-sleep) BWT at
**0.000** on the Phase-8 stream (0/5 seeds regress vs the boundary oracle). The profligate **always-pay** loop — namer
every step — *forgets* (worst-BWT −0.137) by chasing the recency-skewed stream. **Firing more forgets more.** So the gate
is a continual-**safety** mechanism the way a good sleep schedule is, not merely a cost saver. **The spine here was
*measured*, not *deployed* at the gate.** Phase 8.2 validated a label-free **class-direction tap-drift** signal — it leads
the labeled error by ~8 steps (MTD 6 vs 14) and stays invariant to a nuisance covariate (0.84× baseline), while the
magnitude-of-shift null spikes 10× and false-fires on 94% of nuisance steps (density ≠ class, made a measurement). But the
**deployed** gate rides the error-EMA — a *performance magnitude*, not the direction — because DDM consumes an error rate
by construction; the direction trigger is carried as the **validated north-star upgrade** (§10), not the frozen object's
shipped signal.

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
                     │   op c: partial_fit, GATED by DDM on the namer's error-EMA   (the ~metered 12–18%)
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

## 7 · What we extended, paper by paper (both halves)

**The cheap brain (Stage 1) — the frame, the objective, the noise fix.**
- **SCFF (Nature Comms 2025)** *(the frame and the name)* — kept the **label-free, forward-only, local self-contrastive frame**; **replaced its loss** — energy-goodness `‖h‖²` measures density, and density ≠ class (Phase 2), so out it went. *SCFF the frame, GIM/CLAPP's objective.*
- **Greedy InfoMax / CLAPP (NeurIPS 2019 / 2021)** *(the objective we actually run)* — a **local InfoNCE that composes with depth**, forward-only and unsupervised (the existence proof that Phase 2's wall was the *objective*, not locality). CLAPP is also the **single-sample / online** form that streams the negatives on-chip (§2.4). Ours: the **two-masked-view** target for structureless flat vectors + the Phase-5 depth-decay cure.
- **SimCLR (2020)** *(the positive pair)* — the **augmentation-based two-view** positive under InfoNCE; ours is **coordinate-masking** on flat vectors, and **Phase 6 adds a second, noise-corrupted view** (§2.5).
- **The noise quartet — AIHWKit/Rasch (2023) · Bishop (1995) · Noise2Noise (2018) · LP-FT (Kumar 2022)** — set the Phase-6 threat model (directional, tap ≫ weight), the reason the noise-augmented view works (input-noise ≈ Jacobian/Tikhonov), the **Door-B** theory (a class direction forms from an all-noisy stream), and the **ordering** (fix noise in SCFF, before the namer). *(Also from v1.1.0: Distance-Forward = the window `w`; DeeperForward = "squared goodness kills depth, not the norm"; BYOL = read a stop-gradient encoder; Mono-Forward = per-depth heads; BoostResNet = the boosting theory, since **dropped** for a single bulk, S11.)*

**The namer + maintenance half (Stage 2).**

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
- *Kept:* the **error-drift detector** — DDM on the namer's error-EMA — as the online learning-gate, **deployed as-is.**
- *Measured / extended:* Phase 8.2 validated a **class-direction tap-drift** signal (a *direction*, spine-clean) that
  *leads* the raw error — carried as the north-star upgrade but **not the deployed trigger** (DDM consumes an error rate) —
  and the gate's value turned out to be **continual safety, not just cost** (firing more forgets more, §4).

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
| **SCFF** | label-free forward-only self-contrastive frame + the name | **energy → InfoNCE** objective; summation reformulation (FF-pairing case only) |
| **GIM / CLAPP** | local InfoNCE composes depth; CLAPP = single-sample/online | two-masked-view target for flat vectors; LUT-streamed negatives; the flat-vector decay-cure |
| **SimCLR** | augmentation two-view positive pair under InfoNCE | coordinate-masking + a **noise** view, flat vectors, inside a local window |
| **Distance-Forward** | overlapping-block coordination (DF-O) | parameterized **window `w`** = blocked-backprop truncation length; dose-response |
| **DeeperForward** | "squared goodness kills depth, not the norm" | keep the L2 norm; drop `‖h‖²`; harden *around* the norm (P6) |
| **BoostResNet** | residual *follows* boosting, `e^{-½Tγ²}` | applied to labeled GD checkpoints; read-not-write; **then dropped for a single bulk (S11)** |
| **BYOL** | read a stop-gradient encoder safely | GD-reads-SCFF-never-writes (stability, not anti-collapse) |
| **DSN / Mono-Forward** | per-layer / per-depth heads | placement **Pareto-dominates** all-tap on composite tasks |
| **AIHWKit / Rasch 2023** | honest analog-noise model; tap ≫ weight; directional residual | set the Phase-6 **threat model** (the class-axis enemy) |
| **Bishop 1995** | input-noise ≈ Jacobian/Tikhonov penalty | why the noise-augmented view works; **generic > directional** smoothing |
| **Noise2Noise · LP-FT** | clean-from-only-noisy (zero-mean) · a head can't manufacture backbone robustness | **Door B** (direction from an all-noisy stream) · the **ordering** (noise fixed in SCFF first) |
| **RanPAC** | random-projection + running-Gram ridge, gradient-free | on SCFF features; spine rubric; cbrs guard; SLDA deployed as the cheaper twin |
| **Deep SLDA** | streaming means + tied covariance, closed-form | the **deployed namer** (69× cheaper, ties live); streaming `partial_fit`; the anisotropy fix |
| **DDM / ADWIN** | error-drift detector as a gate | deployed on the namer's **error-EMA**; a class-direction trigger *validated* (P8.2) but **not shipped**; the gate is **safety**, not just cost |
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
8. **P8 — the economy, run LIVE.** Both brains live; a **DDM** gate on the namer's **error-EMA** meters the 80/20 real
   (GD-share 0.121) — a label-free class-direction tap-drift signal validated as the spine-clean upgrade but not deployed —
   OURS ≈ ½ backprop+replay, and **firing more forgets more** (the gate is safety). Why-analog: 15.4× =
   5.4× substrate × 2.9× algorithm. **(S12.)**
9. **P9 — close & *freeze* the maintenance loop (this).** The bulk **rotates but does not forget** (measured); N2 struck,
   all-tap kept, **CBRS** committed, the read-side residual defended by **proto-reanchor**; the freeze caught the
   drift-conditional cadence (grid-8→**grid-4**) and **locked the object** at `59d2720`. **(S13.)**

---

## 9 · The committed object, and what's built vs designed

**The frozen neocortex loop (exact config).** `NoiseAugContrast` SCFF bulk (L12/w64, InfoNCE `τ=0.2`/`w=2`, per-sample L2
norm, one noise-aug view `σ_aug=1.0`, no residual) · deployed namer **SLDA** (RanPAC the reference), gradient-free/streaming
`partial_fit` · awake gate **DDM on the namer's error-EMA** (class-direction tap-drift validated, not deployed — §4) · **all-tap** sleep consolidation · **CBRS**
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
brain will read; so does the **class-direction tap-drift** gate signal validated in Phase 8 but not deployed on the frozen
error-EMA gate — the recurrent *halt* that fires on a direction, never a confidence magnitude. After Phase 10, the
analog-realism layer (SPICE / PVT) opens. *Simple intelligence first.*

---

## References (the papers the whole model stands on)

RanPAC ([2307.02251](https://arxiv.org/abs/2307.02251)) · Deep SLDA ([1909.01520](https://arxiv.org/abs/1909.01520)) ·
DDM (Gama et al., 2004) / ADWIN (Bifet & Gavaldà, 2007) · CBRS (Chrysakis & Moens, ICML 2020) · iCaRL / herding
([1611.07725](https://arxiv.org/abs/1611.07725)) · Latent Replay ([1912.01100](https://arxiv.org/abs/1912.01100)) ·
Layerwise Proximal Replay ([2402.09542](https://arxiv.org/abs/2402.09542)) · Probing Representation Forgetting
([2203.13381](https://arxiv.org/abs/2203.13381)) · Test-time prototype shift ([2403.12952](https://arxiv.org/abs/2403.12952))
· SDC ([2004.00440](https://arxiv.org/abs/2004.00440)) → LDC ([2407.08536](https://arxiv.org/abs/2407.08536)) · A-GEM
([1812.00420](https://arxiv.org/abs/1812.00420)) · REMIND ([1910.02509](https://arxiv.org/abs/1910.02509)) · does
continuous SSL forget ([2311.13321](https://arxiv.org/abs/2311.13321)) / CaSSLe
([2112.04215](https://arxiv.org/abs/2112.04215)). **Energy model:** Horowitz (ISSCC 2014) · DNN+NeuroSim · ISAAC (ISCA'16)
· PUMA (ASPLOS'19) · AIHWKit — behavioral, not SPICE. **The cheap brain (Stage 1):** Forward-Forward (Hinton 2022) ·
SCFF (Nature Comms 2025) · Greedy InfoMax (NeurIPS 2019) / CLAPP (NeurIPS 2021) · SimCLR (2020) · Distance-Forward
(2024) · DeeperForward (ICLR 2025) · BoostResNet (ICML 2018) · BYOL (2020) · Mono-Forward (2025) · AIHWKit / Rasch
(2023) · Bishop (1995) · Noise2Noise (2018) · LP-FT (Kumar 2022) — the full per-paper ledger is §7. The arc behind every
claim:
[`stage1-report.md`](stage1-report.md) · [`stage2-report.md`](stage2-report.md) · [`validation-report.md`](validation-report.md) and each `phaseN/README.md`. The decision
record: [`idea/main.ideas.v1.md`](../idea/main.ideas.v1.md) (N1–N3 + S1–S13). The cheap-brain snapshot this builds on:
[`phase6-final-architecture.md`](phase6-final-architecture.md) (v1.1.0). The frozen loop: commit `59d2720`.
