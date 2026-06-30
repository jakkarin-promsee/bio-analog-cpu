# The SCFF cheap brain — final architecture (v1.0.0)

> **What this is.** The single, self-contained account of the model we built across five phases of draft 6.0 — what
> it is, how every part works, *why* it is shaped the way it is, the math under it, and exactly how it extends the
> papers it stands on. It is written so an **outside researcher can understand the whole model from this one file**,
> without opening a single `phaseN/` report.
>
> **What "v1.0.0" means — read this before any claim below.** This freezes the **ideal-math *design*** of the cheap,
> forward-only half of the chip — not its silicon, not its scale, not a benchmark result. Every number here is from
> a **behavioral simulation** (numpy, ideal floats: no analog noise, no finite weight-write precision, no ADC
> quantization). The tasks are **small and partly synthetic** (built Gaussian generators, 8×8 digits, flat CIFAR).
> The headline depth result is a **representation claim** (per-layer linear probe and a small trained readout) on a
> **task we constructed**, *not* a static-accuracy benchmark win. Where a part is *designed but not built*, the text
> says so in line, and §7 has the full ledger. "Finished" means *the design is frozen and the cheap-brain research
> question is answered* — the silicon and at-scale validation are explicitly future work.
>
> **The spine (the one idea under everything).** The project's recurring failure is confusing **density for class**
> (loudness for label) and losing a **sign / direction**. So the rule the whole design obeys is: *learning must
> preserve and read the class **direction**, never a **magnitude*** (energy, rank, variance, confidence are all
> magnitudes). When something below seems surprising, this is usually why.
>
> **A naming note.** "SCFF" here denotes the **forward-only, label-free, self-contrastive *frame*** — the cheap-brain
> *role*. Its *objective* is **not** the energy-goodness of the original SCFF paper: Phase 3 replaced that with a
> GIM/CLAPP-family **InfoNCE** loss (§2). So "SCFF" = the frame and the lineage, not Hinton's / the Nature-Comms
> loss. **Mechanistically the committed cell is closest to CLAPP** (local InfoNCE, made online) carrying
> **SimCLR-style two-view positives** — keeping the "SCFF" name is a statement of project *identity*, not a claim of
> methodological descent from the SCFF paper specifically. We are explicit here so no one mistakes it
> for the paper's exact method. Biological names ("Hippocampus", "Cortex") likewise name **circuit elements**, not
> biology.

---

## Reader's glossary (the load-bearing terms, defined once)

| term | meaning in this document |
| --- | --- |
| **the spine** | the rule above: preserve/read the class **direction**, never a magnitude. |
| **density ≠ class** | a layer can be "loud where the data is dense" without that loudness tracking the label; the project's recurring bug. |
| **probe vs readout** | a **linear probe** is a frozen-features *measurement* of how separable a representation is (a diagnostic, never deployed). A **readout** is the actual small trained classifier head we *deploy*. They are different metrics; we never blend them. |
| **all-tap / per-depth head / truncation** | three ways the readout reads SCFF: **all-tap** = concatenate *every* layer; **per-depth head** = read one chosen layer; **truncation** = a short from-scratch stack read at its top. |
| **headroom task** | a **synthetic, author-built** task (a Gaussian generator with structure that *only deeper composition can exploit*), used to make depth-composition visible. It is not a benchmark; it is a microscope. |
| **w12 ceiling / "objective ceiling"** | the score of **our own cell trained with full credit reach (window = all 12 layers)** — effectively a full backward pass. It is *forbidden* (it breaks the forward-only/local rule), used **only** as a diagnostic upper bound. "Reaches the ceiling" = matches *this internal bound*, **not** "matches backprop." |
| **tuned-BP** | a genuinely-tuned end-to-end backpropagation MLP at **matched weight budget** — the achievable "old-world" reference. |
| **BWT / AA** | continual-learning metrics: **Backward Transfer** (how much learning new tasks hurts old ones; 0 = no forgetting, negative = forgetting) and **Average Accuracy** over all tasks at the end. |
| **backward cost (the 80/20)** | a **compute-proportion proxy**, measured in the sim as *layers-that-receive-a-weight-update × per-layer op-count* — **not** Joules, charge-cycles, or silicon energy. "~80% SCFF / ~20% GD" is a *share-of-compute* design target, not an energy measurement (the hardware-meaningful meter is Phase-6 work). |

---

## 0 · The one-paragraph truth (and why anyone should care)

This is **not a machine-learning model and not a digital ML accelerator.** It is a **bio-inspired analog compute
substrate that learns on-chip**: capacitors hold weights as continuous charge, SRAM holds wiring and sign bits,
op-amps do add / multiply / ReLU directly on the charge, and **the weights never leave the chip** (a *resident-weight*,
compute-in-memory design). **Why build this rather than use a GPU?** Because the target is **online, in-field
adaptation at analog-circuit energy, with no gradient or weight ever shipped off-chip** — a device that keeps
learning where it sits, cheaply, forever, instead of a frozen model retrained in a datacenter. That target makes
two things matter that mainstream ML treats as afterthoughts: the **energy of the backward pass** (weight transport,
a transpose, stored activations) and **catastrophic forgetting** (an online learner must not erase yesterday to
learn today). The design answers both with **two brains** on the one substrate: a large, unsupervised front
(**SCFF**, ~80% of the network) whose *learning* is cheap — label-free, local, forward-only, no backward pass — and a
small, precise **gradient-descent** back (~20%) that puts real labels on what the front organized. ("Cheap" here means
cheap *to learn*, not cheap to run forward — the forward-inference energy of the SCFF bulk is a separate quantity we do
not yet meter; §4 and the glossary are precise about this.) The whole bet rides on
one observation: **direction is the one expensive thing in learning.** Measuring how loud a neuron is is free;
deciding *which way* each weight must move is what costs. So we **pay for direction once, where it counts** (the 20%
GD), and get the rest cheaply (the 80% SCFF). The method throughout: **copy the brain's *function*, cheat the
*implementation*** — reproduce what the brain does with whatever is cheap on this substrate.

---

## 1 · The substrate, in one breath (enough to ground the rest)

Three primitives, because they explain *why* the learning rule is shaped the way it is.

- **The Scap** (SRAM + Capacitor) is the atom of storage: one synapse's weight, as **analog charge on a capacitor**
  (the magnitude) plus a **digital SRAM bit** (the sign — so `±` is exact, never analog). A Scap is a *wire, not a
  neuron*.
- **The crossbar** computes in the wires: a grid of Scaps does the multiply-accumulate as physical current, and
  op-amps do the nonlinearities on charge. There is no ALU shuttling data — *computation is where the weights
  physically are*. (Within device resolution and mismatch; the ideal model writes the current through a Scap as
  `≈ |a·W|`, with the sign carried by the SRAM bit and the magnitude by charge.)
- **Mono-forward, dual-rail.** A single forward sweep carries **two activation "worlds" side by side** down a
  dual-rail datapath, through the **same shared weight crossbar**; only the cheap activation buffers double, *not*
  the Scaps (the weights). It is **objective-agnostic** — the two rails can carry Forward-Forward's (positive,
  negative) pair, or, in our committed cell, the **two augmented views** a contrastive loss needs. (How the
  contrastive objective's *negatives* are supplied on this two-rail substrate is the subtle part — §2.4.)

**Why "direction is expensive" is an *analog* statement, not just a digital one.** On silicon, *applying* a weight
update (programming a capacitor to a new charge) is paid by any learning rule — that write cost is not what we save.
What a forward-only local rule removes is the **transposed crossbar, the stored activations, and the cross-layer
dependency chain** that a backward pass needs to compute *which way* each weight should move. Those are the analog-
expensive parts (extra charge cycles, extra routing, extra buffers); the sign-plus-delta of a local update is cheap
to *decide* even though it is not free to *write*. That is the precise sense in which we "pay for direction once."

**Two honest limits on this claim, stated plainly.** (1) A forward-only local rule is *not* free of all update
machinery — it still pays the intra-layer error→ΔW product, the per-sample L2 normalization, and (for the contrastive
loss) a similarity/softmax block (§2.4). What it removes is the **cross-layer** credit chain (the transpose + deep
activation tape), *not* the **local** update. (2) This is a **structural** argument, not a measured energy one: the
cost meter in Stage 1 is an op-count proxy (glossary), and the costs that dominate real in-memory silicon — the
**ADCs / data converters** and the **forward read energy** — sit *outside* it. So the net *energy* win is
**unquantified and deferred to Phase 6**; what Stage 1 establishes is the credit-assignment *structure* (no cross-layer
chain), not a Joule count.

*(Designed, not simulated: capacitor leak, tuned below the natural rate against an 8-bit charge reference, is
intended to give **free L2-style weight decay in physics** — leakage discharges a capacitor in proportion to its
stored charge (`dQ/dt ∝ −Q`, i.e. a `≈ −λW` pull), which is exactly the gradient of a `λ‖W‖²` penalty arising from the
device instead of an explicit term. Whether this *helps* (regularization) or *hurts* (it erodes the smallest — possibly
most selective — weights, the rate `λ` drifts with temperature, and only the charge *magnitude* leaks while the sign
sits in SRAM) is **untested** — a *hoped-for* free lunch, not a validated feature. It is first-order and
temperature-sensitive, exactly the PVT realism this version defers; the ideal-float simulation **does not model it**,
so no result here depends on it. The full chip, mono-forward as an analog circuit,
and analog/PVT/noise realism are all out of scope for v1.0.0 — this is the ideal-math layer everything physical will
later have to honor. The **substrate-technology choice itself is deferred too**: capacitive storage (chosen here) trades
*leak/refresh* for the *write-endurance/write-noise* of a non-volatile analog conductance (RRAM/PCM) — the standard
resident-weight alternative — and which side wins is a silicon-phase question, not settled here.)*

---

## 2 · The cheap brain: SCFF (the 80%)

### 2.1 The lineage, and the one wrong turn we corrected

**Forward-Forward** (Hinton, 2022): replace the backward pass with *two forward passes* — one on real ("positive")
data, one on fake ("negative") — training every layer locally to be **loud on the real, quiet on the fake**, no
gradient crossing a layer. Great for hardware (no transpose, no stored activations), but it needed *labels* to make
the fakes (wrong-label corner pixels), and only on MNIST.

**SCFF** (Self-Contrastive Forward-Forward, Nature Comms 2025) made the contrast from the data itself: a positive is
a sample paired with *itself*, a negative is a sample paired with a *different* sample — label-free. Its "goodness"
(the quantity made high on positives, low on negatives) is **energy**, the sum of squared activations,
`G = ‖h‖²` per layer. This is the **frame** we adopt: the only learning rule that is local **and** derivative-free
**and** forward-only **and** unsupervised all at once — the only one that can live on the substrate.

But energy-goodness has a fatal property *for us*, and finding it was the spine of Phases 1–3: **energy measures
density, and density is not class.** `‖h‖²` makes a layer loud where the *data* is dense, which recovers the classes
only when classes happen to *be* density clusters (a checkerboard or an equal-density spiral defeats it). Worse,
**density does not compose with depth**: stack energy-goodness layers and the representation gets *less*
class-separable, not more (Phase 2's "depth wall"). And the failure is in the **goodness functional itself**, not in
the choice of negative — Phase 2 showed that *even a perfect class-oracle negative* does not make energy compose with
depth, because no choice of what-is-positive-vs-negative can make a scalar that measures **magnitude** (`‖h‖²`)
encode a **direction** (the class axis). That is the spine, stated as an empirical result about the objective — a
demonstration (the oracle-negative control of Phase 2), not a proof.

### 2.2 The committed objective: windowed two-view InfoNCE

The fix is to change *what "good" means* at each layer from **energy** to **information preserved about the class
direction**. The existence proof is **Greedy InfoMax** and **CLAPP**: forward-only, gradient-isolated, unsupervised
modules trained with a local **InfoNCE (contrastive)** loss, whose representations *improve* layer over layer — the
rising curve energy-goodness never produced. We adopt that objective, in the flat-vector form our substrate needs.

**Forward path (one layer).** Input-normalize the raw input, then each layer is a ReLU map followed by a **mandatory
L2 normalization** (the inter-layer norm, §2.3):

$$a_0 = \frac{x}{\lVert x\rVert},\qquad h_l = \mathrm{ReLU}(W_l\,a_l + b_l),\qquad a_{l+1} = \frac{h_l}{\lVert h_l\rVert}.$$

**The local objective.** Credit is allowed to span a small **coordination window** of `w` adjacent layers (§2.3).
For a window starting at depth `s`, take its input `a_s` and make **two randomly masked views** (each coordinate kept
with prob `1 − r`, mask rate `r = 0.5`):

$$a^{(1)} = a_s \odot m_1,\qquad a^{(2)} = a_s \odot m_2,\qquad m_v \sim \mathrm{Bernoulli}(1-r).$$

Run **both views through the *same shared weights*** (the two rails of §1) for the `w`-layer window, giving
L2-normalized top representations `u^{(1)}, u^{(2)} \in \mathbb{R}^{B\times d}` for `B` samples (`d` = the layer
width, 64 here). Apply **InfoNCE** with the two views of the *same* sample as the positive pair and the *other
samples* as negatives (the asymmetric GIM/CPC form: `B−1` negatives, view-1-of-`i` against view-2-of-`j`):

$$S_{ij} = \frac{\langle u^{(1)}_i,\; u^{(2)}_j\rangle}{\tau},\qquad
\mathcal{L} = -\frac{1}{B}\sum_{i=1}^{B} \log \frac{\exp(S_{ii})}{\sum_{j=1}^{B}\exp(S_{ij})}.$$

The gradient (`dS = (\mathrm{softmax}(S) - I)/B`) flows back through **only the `w` layers of the window** — never the
whole stack. That bounded chain length is the whole reason backward cost stays *flat in depth* (§4).

**Why two masked views — and the honest assumption.** Two masked views of one vector share its **class direction**
but differ in accidental, sample-specific detail; pulling them together while pushing other samples apart forces each
layer to **keep the axis that distinguishes class** and discard the rest. This works **only if the class signal is
distributed across coordinates** (so a 50% mask retains it in expectation); if the class were carried by one
coordinate, random masking could destroy it. We do not prove this — we **tested it**: masked-view *contrast*
composed with depth and preserved class, while the alternative we pre-registered as more likely, masked-feature
**reconstruction**, *failed* (it preserved density, below random) — recorded as a result, not hidden. `r = 0.5` is an
empirical choice from that pass.

**What is genuinely ours here, vs GIM's.** GIM/CLAPP already showed local InfoNCE composes with depth — *on data with
spatial or temporal structure* (predict the next patch / timestep). Our contribution is **not** "local InfoNCE
composes" (theirs). It is: (i) making it work on **structureless flat vectors** via the two-masked-view target (no
patch/timestep to predict), and (ii) the Phase-5 **diagnosis and cure of a depth-decay** that GIM's structured setup
never surfaced (§2.3). When we say "composes with depth," we mean *on flat vectors, with the decay cured* — the part
that is new.

**The honest tension — why not just use CLAPP++?** A Jan-2026 benchmark we cite shows the predictive local-SSL family
(CLAPP++) *matching* end-to-end backprop-SSL on CIFAR-10 (80.51 vs 80.49). So why dwell on a flat-MLP cell that reaches
only ~0.55 on a synthetic generator? Because CLAPP++ earns CIFAR *with convolution and spatial structure* — exactly
what our analog **flat-vector** substrate does not have. The structureless flat regime is both the harder one and the
substrate-relevant one, and the two-masked-view target (with the depth-decay it surfaces, §2.3) is precisely the part
the structured CLAPP++ result does not cover. **One open alternative we do not close:** GIM/CLAPP's *predictive*
objective gives every layer a *fresh* target, which might avoid the same-target decay our masked-view contrast incurs.
A flat-vector predictive objective is an untested route (§5); if it composed without a decay, that too would be a sharp
result about why this regime is special.

### 2.3 The two knobs that close the depth problem (Phase 5)

Even with contrast, the representation composed for only ~5 layers, then **decayed** — it drifted *off the class
manifold* once a layer's abstraction saturated (alive, full-rank, but mis-aimed — a *direction* failure, density≠class
a fifth time). Two **free, forward-only** knobs cure it:

- **Temperature `τ` (the free lever).** A *sharper* InfoNCE temperature (`τ = 0.2`, from a `0.5` baseline)
  concentrates each update on the hardest negatives, making it more **class-selective**. Sharpening also raises the
  gradient scale (`∝ 1/τ`), so part of the gain could be a disguised larger step — we controlled for it: a
  **learning-rate-matched arm** (the `τ = 0.5` cell re-tuned to `τ = 0.2`'s measured update-norm) reached only
  `0.452` vs the sharp cell's `0.530` probe tail, while the `τ=0.5` baseline sat at `0.435`. So of the `+0.095` lift,
  `(0.530−0.452)/(0.530−0.435) ≈ 82%` **survives the lr-match** → it is mostly *direction* (class-selectivity), not
  step size. (Too sharp, `τ ≤ 0.05`, collapses — there is a floor.)
- **Coordination window `w` (the bounded reach).** `w` is, mechanically, the **truncation length of blocked
  backpropagation**: within a window of `w` adjacent layers gradients flow normally; *across* windows they are cut.
  This is the **LoCo / Distance-Forward-O / overlapping-local-backprop** family, supplied forward-only. The committed
  cell uses **stride = `w` = 2** (non-overlapping, each layer in one window). `w = 4` is a bounded "depth-closer".
  The diagnostic `w = 12` (one window over the whole stack) **is a full backward pass** — *forbidden* by the
  forward-only rule, used only as the ceiling.

**Which deployable config actually earns the depth (be precise — this is the flagship claim, so it carries its
uncertainty).** With `τ = 0.2` at `w = 2` — the *committed, substrate-legal* cell — the **deployed readout reaches
`0.550 [0.545–0.553]`, above the tuned-BP reference `0.531 [0.531–0.533]`** — a `+0.019` margin that is IQR-disjoint
and 5/5 by seed, so "real" by our own bar (§glossary). **What "tuned-BP" is here:** the genuinely-tuned `race_bp` racer
carried from Phase 4 — a real search over {depth-shape × lr × weight-decay} at matched budget (the Bartunov/Spyra
fairness protocol), *not* Phase 3's weaker "fixed-budget GD-hidden" representation baseline. (The two are distinct
references and should not be conflated — the headline beats the *tuned* one.) The **linear-probe tail** rises from
`0.435` to `0.530` (`w = 2`), closing to **`0.562` at `w = 4`** ≈ the **`0.556` w12 *probe* ceiling**. **Read the w12
comparison correctly:** `w = 12` is one credit window over the whole stack — i.e. effectively *ordinary backprop on
this 12-layer cell* — so "reaching the w12 ceiling" does **not** mean "matching an external ceiling"; it means a
*bounded* forward-only window recovers almost all of what unconstrained credit would give *on this objective*. So
"depth solved" means: the cheap levers (sharper objective + a bounded window) carry the representation to its own
full-credit ceiling, and a deployed readout on those features beats a genuinely-tuned BP — *on this synthetic headroom
microscope, a task we constructed to have depth headroom; a representation/readout result, not a benchmark.* The
forbidden `w = 12` only proves the decay was **objective-locality (curable), not an intrinsic wall.**

**The mandatory L2 norm** earns "load-bearing twice": it is required for FF-family correctness (a layer can't cheat
by inflating `‖h‖`), *and* it is a **per-sample** normalization (no running/batch-normalization statistics), which is
part of why the cell is continual-friendly (§4) and nuisance-robust (it down-weights non-discriminative dimensions
for free). The same property is *why* it is sensitive to eval-time weight noise — a real, owned tradeoff, and one that
matters more than a footnote: the sensitivity is to weight-**direction** noise, and the substrate's dominant analog
mismatch is *also* directional, so it attacks the very class-direction the whole design exists to preserve. That makes
it the architecture's **sharpest open silicon risk**, not a tunable nuisance (§4, §7).

### 2.4 How the contrastive objective runs on the substrate (the honest bridge)

This is the part an outside hardware reader will (rightly) press, so it gets its own section. **The simulation and
the intended chip use the objective differently, and we are explicit about which is which.**

- **In simulation (what produced every number here):** standard **mini-batch InfoNCE** — a batch of `B` samples, two
  masked views each, the full `B×B` similarity matrix, `B−1` in-batch negatives. This is the well-understood,
  reproducible form, and Stage 1 is a behavioral sim of the *ideal objective*.
- **On the chip (designed, not built):** the two rails carry the **positive pair** (the two views of the current
  sample) through the shared crossbar — that is the "one charge cycle, not two" win, and it covers only the positive
  term. The **negatives are supplied by the Hippocampus LUT** (§3.2 lists "negatives for SCFF" as one of its three
  jobs): a small set of stored prototype activations, drawn a few at a time, so the contrast is computed against a
  rolling set of negatives **accumulated over time**, not a physically-present mini-batch. This is the **CLAPP route**
  — CLAPP is exactly GIM's InfoNCE made **single-sample and Hebbian-plausible** for online hardware — and it is *why
  CLAPP is in our reference list*, not as decoration but as the substrate realization of §2.2's loss.
- **Resolving "no batch statistics."** A mini-batch InfoNCE *does* couple samples (the denominator is the batch) — so
  the precise claim is **not** "no batch coupling," it is "**no running / normalization statistics**" (the L2 norm is
  per-sample; there is no BatchNorm-style state that carries one task's distribution into another). The continual
  safety we actually measured (§4) is **empirical** (BWT in `[−0.02, −0.18]`), and its mechanism is that the
  unsupervised SCFF *weights drift little* under the stream **and** the negatives come from a **task-spanning LUT**,
  not only the current task — *not* a "by construction" guarantee from the objective alone.

**The honest status:** the dual-rail substrate carries the *positive pair* of the committed objective today (in
design); the negative-gathering — buffer depth, where the similarity/softmax is computed (digital, or a second small
crossbar), and the charge-cycle budget for `N` accumulated negatives — is **designed and deferred to the analog phase**,
exactly like mono-forward-as-a-circuit. Nothing in §4's results depends on the chip realization; they are the ideal
objective's behavior. But the bridge from "two rails" to "InfoNCE" is *the LUT supplying streamed negatives*, and we
state it rather than imply the two rails alone discharge the loss (they do not).

**Three caveats this bridge does not get to wave away (Phase-6 gates).** (1) **The estimator changes.** Every number in
this document uses mini-batch InfoNCE with *in-batch* negatives; the chip uses a *rolling, ART-deduplicated* prototype
pool. These are not the same estimator — a deduplicated pool may lack the *hardest* negatives, and the §2.3 temperature
lever works precisely *by* concentrating on the hardest negatives. So **the `τ = 0.2` depth result is validated only
with in-batch negatives; its survival under LUT-streamed negatives is untested**, and is a Phase-6 gate. (2) **The
softmax/normalizer is a digital block, not free.** The contrastive denominator (an inner-product matrix + `exp` +
normalize) is not a charge-native crossbar operation; "a second small crossbar" understates it — it is real area + ADC
traffic that competes with the very backward cost we claim to save. (3) **A finite on-chip LUT and "task-spanning"
negatives are in tension:** the continual-safety mechanism leans on negatives drawn from across tasks, but a *bounded*
store under a lifelong stream must evict — which could re-introduce forgetting through the negative pool. The measured
continual win (§4) used full-history replay in sim; the bounded-store version is unbuilt. (Relatedly, `B = 32` gives
only 31 in-batch negatives — thin for InfoNCE; the on-chip "few negatives at a time" regime is thinner still and
untested.)

---

## 3 · The precise brain: the GD readout (the 20%) — deliberately rough

SCFF organizes the world but cannot name it. The gradient-descent brain reads SCFF's features and maps them to real
classes — and **only that**. It is kept minimal on purpose: **v1.0.0 froze the SCFF half; Phase 6's whole job is to
optimize this half.** Treat everything here as the *rough* readout — validated, but not yet tuned.

### 3.1 What it reads, and from where

GD **reads** SCFF via taps and **never writes** into the SCFF stream. (Phase 2 showed re-injecting GD into the stream
*kills* SCFF; and reading-not-writing makes GD a **stop-gradient consumer** — BYOL-style, it cannot destabilize the
encoder it reads. Note: collapse proper is already prevented by InfoNCE's negatives, so this is a *stability* point,
not an anti-collapse trick.) Three readers, chosen by where the useful depth sits (compute cost in forward-MACs):

- **All-tap** — concatenate every layer and fit one head. Maximum accuracy, but it pays to read the *drifted* deep
  layers it can't ignore, diluting the class signal — it burns the 80/20.
- **A short fixed truncation stack** (the v1.0.0 *deployment* default on the continual home) — a from-scratch ~2–3
  layer stack, read at its top. On the flat continual regime it is **~8× cheaper than all-tap in readout forward-MACs**
  (and fewer Scaps) at a small accuracy cost.
- **Per-depth heads** — read one sharp depth. On compositional tasks these **beat** all-tap (cheaper *and* more
  accurate, sidestepping the drifted layers); a **linear head is the deployable base**, an MLP head an optional
  upgrade.

The readout itself is small: features `φ(x)` → `\hat{y} = \mathrm{softmax}(W_{\mathrm{ro}}\,φ(x) + b_{\mathrm{ro}})`,
trained by cross-entropy — the one "direction" expense, paid once.

> **An honest narrowing (Phase 5).** We hoped to read *adaptively* — a per-sample early-exit (CALM/BranchyNet-style),
> shallow on easy inputs, deep on hard, gated by head confidence. On the flat continual home **it lost** to a fixed
> stack: the per-depth heads there are weak-but-decorrelated, so *pooling* (all-tap) beats any single-depth
> *placement*, and no confidence threshold meets the bar — the exact inverse of the headroom result. So v1.0.0 ships
> a **fixed** reader. (An *oracle* best-per-input selector reaches far higher — a better selector is a Phase-6 /
> north-star problem, because confidence is itself a magnitude, and the spine warns against reading magnitudes.)

### 3.2 Sleep, the LUT, and the chain (mixed: built vs designed)

- **Sleep consolidation (built, validated).** Streaming + a learning-gate means GD only re-fits what *recently* fired
  while SCFF's whole map drifts. The fix is a periodic **sleep**: stop streaming and **re-fit the readout full-batch
  over the history** against the *current* SCFF map. This is the architecture's decisive win (§4): where online
  backprop forgets, sleep *recovers* — because **the SCFF features themselves don't forget**, so sleep only re-aims
  the cheap readout (it never has to replay gradients through the whole network — that is what makes the recovery
  cheap).
- **The Hippocampus LUT (built as a prototype store).** A deduplicated store of input *prototypes* (winner-take-all
  novelty allocation — keep `x` as new if it matches no existing prototype above a vigilance threshold; this is
  Adaptive Resonance Theory's allocation rule). One store, **three customers: the streamed negatives for SCFF's
  InfoNCE (§2.4), the replay for sleep, and the seed of a future memory model.** It replays correctly at a third of
  full store. The two-store design (fast sparse hippocampus + slow cortex, replay consolidating one into the other)
  is **Complementary Learning Systems**, re-derived from the circuit side.
- **Boosting blocks (validated as a depth *option*; v1.0.0 ships a single bulk).** The architecture *can* chain
  `[SCFF → GD-checkpoint]` units as **residual boosting blocks** — each a weak corrector of the residual the last
  left (training error falls as `e^{-\frac{1}{2}T\gamma^2}` with `T` blocks of "edge" `γ`, the margin by which each
  block beats chance). Phase 2 found depth is better bought as a few boosted shallow blocks than one very deep stack,
  and that *reading* block readouts works while *re-injecting* fails. **The committed v1.0.0 cell is a single L≈12
  bulk read at the right depth — boosting is a validated capacity option, not part of the shipped cell.**
- **The threshold learning-gate (DESIGNED, NOT built).** The intended online economy: run cheap local SCFF when the
  loss is low (`\mathcal{L} < \theta` → SCFF only), spend an expensive GD update only when the cheap path stalls
  (`\mathcal{L} \ge \theta`, or on a loss-slope plateau). **It is named and deferred to Phase 6** — v1.0.0 does not
  run it; the sleep cadence + this gate are the GD-side knobs Phase 6 will tune against the measured drift.

---

## 4 · How it all runs (the forward picture) and where it wins

```
  input x ──▶ [ SCFF bulk: L≈12, width 64, contrast objective, window w=2, τ=0.2 ]
                  │  every layer:  ReLU → per-sample L2-normalize     (forward-only, label-free, local)
                  │  learning:     windowed 2-view InfoNCE; negatives via the LUT (chip) / in-batch (sim)
                  │                credit chain = w layers only  →  backward compute flat in depth
                  ▼
            taps (GD reads, never writes — stop-gradient)
                  │
                  ▼
         [ GD readout (~20% of backward work) ]  ◀── sleep: periodic full-batch refit over the LUT replay history
            • deploy : short fixed truncation stack (continual home; ~8× cheaper than all-tap in readout MACs)
            • peak   : all-tap        • compositional : per-depth head   • (boosted blocks = validated option)
                  ▼
              ŷ = class
```

Measured against a **genuinely-tuned backprop** at matched weight budget — with the baselines stated honestly:

- **It is a continual learner — the home, and the decisive win.** On a class-incremental synthetic stream (10
  classes as 5 tasks of 2) and on 8×8 digits, **naive online backprop (no replay)** forgets catastrophically
  (BWT ≈ −0.8 to −1.0); our cell forgets little (BWT ≈ −0.02 to −0.18). **The honest framing of the baseline:** this
  is *naive* online-BP, given no replay — and our cell *does* use a replay buffer (the LUT) and a sleep refit, so it
  is not a same-budget comparison. The real, defensible claim is **mechanistic**: our own **no-sleep control also
  rots** (BWT ≈ −0.95), so the win is the *replay+sleep mechanism on non-forgetting unsupervised features*, not magic;
  and it is *cheap* precisely because only the small readout is replayed (the bulk doesn't forget), whereas BP+replay
  must replay gradients through the whole network. A same-budget BP+replay comparison is the right next baseline
  (Phase 6).
- **Depth is cheap (compute-proportion).** The bounded credit chain (`w`) makes SCFF's **backward compute flat in
  depth** while backprop's grows linearly — measured as the op-count proxy of §glossary, *not* energy. The 80/20 is a
  *backward-work* share, depth-gated (it materializes deep, where the design is intended to operate) — and it says
**nothing** about forward-inference energy, which is dominated by the SCFF bulk and is not metered here (a Phase-6 job).
- **It composes the depth a task needs, and reads it cheaply** — the §2.3 result: on the synthetic headroom task the
  deployed readout (0.550) beats matched tuned-BP (0.531) and the probe tail reaches the cell's own w12 ceiling
  (0.556), read ~8× cheaper than all-tap. *This is a representation/readout claim on a constructed task* — said here,
  not only in §7.
- **Nuisance-robust** (crosses *above* tuned-BP in high ambient dimension, free, via the per-sample norm) — but the *same* per-sample norm makes the cell **sensitive
to weight-direction noise (A7)**, the sharpest open silicon risk on an analog substrate whose dominant mismatch is also
directional (§7); it also **trails on
  raw static accuracy and many-class** problems, *by design* — a structure learner with a cheap namer, not a global
  error-minimizer. We do not claim otherwise.

The through-line, measured: the cell **wins where the substrate lives and trails on static accuracy precisely because
density ≠ class** — it learns structure cheaply and names it cheaply, and that is the whole bet.

---

## 5 · What we extended, paper by paper (the honest ledger)

This model is a recombination, and being precise about *what is ours* vs *borrowed* is how a reader trusts it. For
each paper: what it gave, what we kept, **what we changed and why.**

**Self-Contrastive Forward-Forward (SCFF) — Nature Comms 2025** *(the frame and the name)*
- *Kept:* the **label-free, forward-only, local self-contrastive frame** — the cheap-brain role.
- *Changed (the defining one):* we **replaced SCFF's energy-goodness objective `‖h‖²` with a contrastive InfoNCE
  objective** (below), because energy measures density and density does not compose with depth (our Phase 2). So this
  is *SCFF the frame*, with *GIM/CLAPP's objective* — we keep the name as project identity (see the masthead note),
  not as a claim to the paper's loss.
- *Reformulation (FF-pairing only):* SCFF pairs the FF combining layer by **concatenation** (`[x_k, x_k]`, two weight
  blocks `W_1, W_2`, proven equal). We use the **summation** form (`W(2x_k)`, one shared weight) — exactly equal
  *because `W_1 = W_2`*, halving the input lines. **This equivalence holds for the identical-pair (FF) case only.**
  The committed contrastive cell has **no concatenating combining layer** — it runs two *different* masked views
  *siamese* through the shared crossbar; the substrate point there is simply *one weight set, two cheap activation
  rails* (the dual-rail), not a `2x` collapse.

**Greedy InfoMax (NeurIPS 2019) & CLAPP (NeurIPS 2021)** *(the objective we actually run)*
- *Kept:* the **local InfoNCE / info-preserving objective** that composes with depth, forward-only and unsupervised —
  the existence proof that our Phase-2 wall was the *objective*, not locality. **CLAPP is the single-sample,
  Hebbian-plausible route** that makes this objective realizable online on the substrate (§2.4) — it is the chip's
  negative-streaming form, not a footnote.
- *Changed / extended:* GIM/CLAPP predict a **next patch/timestep** (they need structure). Our regime is a **flat
  vector**, so our target is **two masked views of the same vector** (a SimCLR-flavored positive pair) with **streamed
  negatives**. And we add the Phase-5 **flat-vector depth-decay diagnosis + the `τ` cure** their structured setup never
  surfaced. *(We pre-registered masked **reconstruction** as the likely flat objective; the sims **overturned it** —
  reconstruction preserved density, below random. Recorded, not hidden.)*

**SimCLR (2020)** *(the positive-pair construction)*
- *Kept:* the **augmentation-based positive pair** — two stochastic views of one sample pulled together while other
  samples are pushed apart, under InfoNCE. Our positives are this, *not* GIM/CLAPP's predict-the-adjacent-patch; the
  earlier "SimCLR-flavored" mentions name this debt explicitly.
- *Changed / extended:* the augmentation is **random coordinate masking** (`Bernoulli(1−r)`) on a **flat, non-image
  vector**, applied *inside a local window* rather than through one global end-to-end encoder. So the committed cell is,
  precisely: **SimCLR's positive, CLAPP's locality, on flat vectors.**

**Distance-Forward Learning (2024)** *(the coordination window)*
- *Kept / extended:* its **overlapping-block (DF-O)** trick is our **coordination window `w`** = the blocked-backprop
  truncation length, supplied forward-only. We parameterized it (`window`/`stride`) and mapped the dose-response:
  `w=2` default, `w=4` bounded closer, `w=12` the forbidden upper bound. Its **margin loss** is kept on standby.

**DeeperForward (ICLR 2025)** *(the counter-finding that freed the norm)*
- *Kept:* the finding that **squared goodness is the depth-killer, not the per-sample norm.** This is why we keep the
  mandatory L2 norm (correctness *and* continual-friendliness) while abandoning `‖h‖²`.

**BoostResNet (ICML 2018)** *(the theory under the blocks)*
- *Kept:* the proof that a residual chain *follows* boosting — each block a weak corrector, error `e^{-\frac12 T\gamma^2}`.
- *Changed:* the guarantee lives on **labels**, so it applies to our **GD checkpoints** (not the unsupervised SCFF
  stages); SCFF does feature work *inside* the residual stream. Phase 2 added: **read the block readouts, never
  re-inject**, and **few blocks suffice**. (So "follows BoostResNet," not "is BoostResNet verbatim" — the labeled
  part only.)

**BYOL (2020)** *(the read-don't-write precedent)*
- *Kept:* a downstream learner can read a **stop-gradient** copy of the encoder without destabilizing it. Our
  GD-reads-SCFF-never-writes is that stop-gradient relationship. **(Not for anti-collapse — InfoNCE's negatives
  already prevent collapse; this is a no-feedback *stability* point.)** The momentum "EMA-view" is a standby upgrade,
  not in v1.0.0.

**Layer-wise LR decay / discriminative fine-tuning (ULMFiT, 2018→)** *(the plasticity gradient)*
- *Kept / flipped:* "slow what the downstream reads." LLRD slows the **bottom**; our downstream reads the **top**, so
  we **flip the axis** and slow the *late* SCFF layers — a drift fix, free on the substrate.

**Deep Supervision (DSN) / Mono-Forward (2025)** *(per-depth heads)*
- *Kept / extended:* per-layer supervised heads → our **per-depth readout heads**, with the empirical placement
  result: on composite tasks one head at the sharp depth **Pareto-dominates** the all-tap concatenation. Mono-Forward
  is also our strongest forward-only *supervised* fallback baseline.

**Calibrated early-exit (CALM 2022 / BranchyNet 2017)** *(tested, then scoped out)*
- *What happened:* we built the calibrated confidence-gated exit and **it was struck on our continual home** (pooling
  beats per-sample placement there). We ship a fixed reader instead. Reported as a *negative result with a mechanism*.

**ReZero / Fixup (preservation) — & the Tunnel Effect (2023)** *(considered, not needed / demoted)*
- *What happened:* a frozen near-identity residual to *preserve* the early representation was pre-registered as
  conditional and **skipped** — the cheaper objective/placement levers closed the gap. The **Tunnel Effect** was a
  useful guiding analogy but **demoted from theory**: its tunnel is information-*preserving* on supervised nets, ours
  was information-*destroying* and *curable* by sharpening the objective.

| paper | what we took | our extension / change |
| --- | --- | --- |
| **SCFF** | label-free forward-only self-contrastive frame + the name | **energy → InfoNCE**; summation reformulation (FF-pairing case only) |
| **GIM / CLAPP** | local InfoNCE that composes depth, unsupervised; CLAPP = single-sample/online form | **two-masked-view** target for flat vectors; streamed (LUT) negatives; the flat-vector decay-cure |
| **SimCLR** | augmentation-based two-view positive pair under InfoNCE | random **coordinate-masking** augmentation on flat vectors, inside a local window |
| **Distance-Forward** | overlapping-block coordination (DF-O) | parameterized **window `w`** = blocked-backprop truncation length; dose-response |
| **DeeperForward** | "squared goodness kills depth, not the norm" | keep the L2 norm; drop `‖h‖²` |
| **BoostResNet** | residual *follows* boosting, `e^{-½Tγ²}` | applied to **GD checkpoints** (labeled); read-not-write; few blocks |
| **BYOL** | read a stop-gradient encoder safely | GD-reads-SCFF-never-writes (stability, *not* anti-collapse); EMA on standby |
| **LLRD** | "slow what the downstream reads" | **flipped axis** — slow the *late* layers |
| **DSN / Mono-Forward** | per-layer / per-depth heads | placement **Pareto-dominates** all-tap on composite tasks |
| **CALM / BranchyNet** | calibrated confidence early-exit | **tested & struck** on the flat home (fixed reader wins) |
| **ReZero/Fixup · Tunnel Effect** | preservation residual · extractor/tunnel framing | **skipped / demoted** — decay was curable by objective, not preservation |

---

## 6 · The five-phase journey that produced this model

One model, five phases, one argument. The plan's *destination* held — this is a continual, substrate-native-depth
learner — but two of its *mechanisms* were wrong (deep SCFF; energy-goodness), and each was overturned by a simulation
or a paper, not rescued by tuning. The connective tissue is one recurring fault, **density ≠ class.**

1. **Phase 1 — build the cell, find its home.** One SCFF+GD block generalizes better than backprop (smaller
   memorization gap) at ~10% of the backward compute — but it is a weak *density* learner. Its home is the
   **continual** regime, where its unsupervised features don't forget and **sleep** recovers what online backprop
   loses. (Found the wound it would take four phases to close: *SCFF degrades with depth.*)
2. **Phase 2 — depth is not SCFF's lever.** A deep SCFF stack can't earn depth — not a transmission problem, and not
   the negatives (*even a perfect oracle* negative doesn't bend the curve, because the failure is in the energy
   functional). Depth comes from **boosted shallow blocks**; we wrongly concluded the wall was "intrinsic to
   locality."
3. **Phase 3 — the objective reframe (the big correction).** The wall is intrinsic to the **energy objective `‖h‖²`**,
   not to locality. Swap energy for **contrastive InfoNCE** + a forward-only **coordination window**, and depth
   composes — *and* it re-earns the continual win. **Adopted; supersedes energy-goodness.** *(Honest framing: GIM/CLAPP
   had already shown a predictive/contrastive objective composes depth where energy doesn't — on *structured* data; our
   Phase 2→3 arc hit that wall independently by experiment, diagnosed it via that literature, and extended the result to
   the *flat-vector* regime they don't cover. So Phase 2 "rediscovered," it didn't first-discover, the wall.)*
4. **Phase 4 — the capability map.** Characterized the adopted cell against a *genuinely-tuned* backprop across seven
   axes: **a substrate-native continual learner, not a static-accuracy competitor.** Wins continual / nuisance-dim /
   depth-composition / depth-is-cheap; trails static difficulty / class-count; one honest negative on eval-time
   noise. It flagged the last wound: past ~layer 5 the representation **decays**.
5. **Phase 5 — close out the cheap brain (this).** Named the decay (a *direction* failure, **objective-locality, not
   an intrinsic Tunnel**) and cured it with two free levers — a **sharper temperature** (~82% direction, lr-matched)
   and a **short fixed reader** (the adaptive exit lost). Continual-safe, confirmed on real digits (null-but-safe on
   the no-depth CIFAR-flat wall). **The cheap brain's design is finished.**

---

## 7 · The committed cell, and what's built vs designed

**v1.0.0 cell (exact config).** `SCFFContrastOverlap`: an **L = 12, width-64** SCFF bulk; objective = windowed
two-view InfoNCE with **temperature `τ = 0.2`**, **coordination window `w = 2`, stride 2** (`w = 4` the bounded
depth-closer), **mask rate `r = 0.5`**, **batch `B = 32`** (sim; negatives streamed from the LUT on-chip), mandatory
input + inter-layer L2 norm, learning rate `0.03`; **no residual**. Deployment: a sleep-consolidated **fixed reader**
— a short truncation stack (~L2–3) on the continual home; all-tap for peak accuracy; per-depth heads / boosted blocks
for compositional tasks. Forward-only, per-sample (no running normalization stats). **Methodology:** median over seeds
`[42, 137, 271, 314, 1729]`; a difference is "real" only if the IQR bands are disjoint **and** the sign agrees in
≥4/5 seeds.

| part | status |
| --- | --- |
| SCFF contrast bulk (InfoNCE + window, `τ=0.2`/`w=2`) | ✅ **built & measured** (Phases 3, 5) — *mini-batch* InfoNCE in sim |
| The decay diagnosis + the two-lever fix | ✅ **built & measured** (Phase 5) |
| Fixed short-stack reader / per-depth heads / all-tap | ✅ **built & measured** (Phase 5) |
| Sleep consolidation + the LUT prototype store | ✅ **built & measured** (Phase 1) |
| Boosting blocks (depth-via-blocks option) | ✅ **built & measured** (Phases 1–2); *not in the shipped single-bulk cell* |
| Plasticity-gradient drift slowdown | ✅ measured as a drift fix (Phase 1); a knob for Phase 6 |
| **On-chip negative streaming (CLAPP-style, LUT-sourced)** | 🟡 **designed, NOT built** — sim uses in-batch negatives (§2.4) |
| **The Ch7 threshold learning-gate** | 🟡 **designed, NOT built** → Phase 6 |
| **Mono-forward as an analog circuit; capacitor-leak L2; analog/PVT/noise** | 🟡 designed; behavioral-sim only (ideal floats — no leak, no noise) |
| Adaptive per-sample early-exit | ❌ **struck** on the flat home (Phase 5) — fixed reader ships instead |
| Frozen-residual preservation | ❌ **skipped** (Phase 5) — cheaper levers closed the gap |

**Honest scope (echoed from the masthead, in full).** The headline depth result is a **representation claim**
(per-layer linear probe + a small trained readout) on a **constructed synthetic headroom task**, confirmed on real
digits — *not* a static-accuracy benchmark-beat, and the continual baseline it beats is **naive online-BP without
replay** (§4 states the fairer same-budget comparison as Phase-6 work). The temperature fix is **null-but-safe** on
flat data with no composable depth (CIFAR-flat needs convolution, out of scope). All numbers are ideal-float
behavioral simulation; **no result here has been tested under analog noise, finite weight-write precision, or ADC
quantization** — and the cell's known *eval-time-weight-noise sensitivity* (§2.3) is the first thing the analog
version will have to survive — indeed it is the architecture's **sharpest open silicon risk** (directional noise
attacking the directional class-signal the design exists to protect; §2.3, §4), not routine future work.

**On the L12 depth vs the shallow read (a hardware reader's question).** The committed *bulk* is L12 because depth is
**task-dependent**: compositional tasks read deep (all-tap / `w = 4`), while the flat continual *home* reads only
~L2–3. So a continual-only deployment could be fabricated **shallower** — L12 is the capacity for the tasks that need
it, not a fixed silicon cost the home always pays. Matching fabricated depth to the deployment regime (area vs reach)
is a Phase-6 / silicon-planning decision.

---

## 8 · What v1.0.0 freezes, and what comes next

**Frozen — the cheap brain's *design* is closed:** the SCFF objective (windowed two-view InfoNCE), `τ = 0.2`,
`w = 2`, the per-sample L2 norm, no residual, the fixed-reader deployment, and the verdict that this is a **continual**
learner. These do not move without a result that overturns them. *Frozen means the ideal-math design is settled and
the cheap-brain research question is answered — it does **not** mean silicon-validated or benchmark-validated.*

**Phase 6 — optimize the precise (GD) brain.** Build and tune the **threshold learning-gate**; tune the **sleep
cadence** against the measured drift (now *readout-aware* — consolidate the extractor-depth features the fixed reader
reads); make the cost meter **hardware-meaningful** (charge cycles / ADC / write energy, replacing the op-count proxy);
add the **same-budget BP+replay continual baseline**; and run the substrate-relevant **train-with-noise** test before
any analog-robustness claim.

**Phase 7+ — the north star (deliberately not specced).** A recurrent, lifelong-learning "thinking" loop where
*correctness is a self-generated feeling* — the organs re-wired to run recurrently at inference (SCFF goodness → the
feeling; the LUT → the queried memory; the gate → think-until-the-feeling-crosses-θ). The parked Phase-5 thread (a
better-than-confidence per-sample selector) comes home here. *Simple intelligence first.*

---

## References (the papers this model stands on)

Self-Contrastive Forward-Forward ([2409.11593](https://arxiv.org/abs/2409.11593)) · Greedy InfoMax
([1905.11786](https://arxiv.org/abs/1905.11786)) · CLAPP ([2010.08262](https://arxiv.org/abs/2010.08262)) · SimCLR ([2002.05709](https://arxiv.org/abs/2002.05709)) · "Can
Local Learning Match Self-Supervised Backprop?" (Jan 2026, [2601.21683](https://arxiv.org/abs/2601.21683)) ·
Distance-Forward Learning (2024) · DeeperForward (ICLR 2025) · BoostResNet (ICML 2018) · BYOL (2020) ·
ULMFiT / discriminative fine-tuning (2018) · Mono-Forward ([2501.09238](https://arxiv.org/abs/2501.09238)) · CALM
(2022) / BranchyNet ([1709.01686](https://arxiv.org/abs/1709.01686)) · ReZero ([2003.04887](https://arxiv.org/abs/2003.04887))
/ Fixup ([1901.09321](https://arxiv.org/abs/1901.09321)) · The Tunnel Effect ([2305.19753](https://arxiv.org/abs/2305.19753)).
Full per-paper stories: [`research/papers/`](../research/papers/README.md). The arc behind every claim:
[`stage1-report.md`](stage1-report.md) and each `phaseN/README.md`. The decision record:
[`idea/main.ideas.v1.md`](../idea/main.ideas.v1.md).
