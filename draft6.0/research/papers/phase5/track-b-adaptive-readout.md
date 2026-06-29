# Track B — adaptive readout: find the extractor's end, cheaply

> **The job:** the reframe's core. The useful representation is at a **task-dependent depth** (the extractor's
> end); reading every layer (all-tap) burns the 80/20. So **put readouts at multiple depths and learn which one to
> trust / when to stop** — without reading everything. This is the author's **Solution 3 (the decider GD)** and the
> **"lazy compute"** instinct. It has three mature literatures (deep supervision, early-exit, learned halting) and
> they line up almost exactly with what the author drew.
>
> **⚠ POST-REVIEW CORRECTIONS (see [the Phase-5 design decision-record](../../../src/phase5/design.md), authoritative):** (1)
> **Learned halting / PonderNet is CUT** from the Stage-1 path (over-engineering; pulls the north star forward) →
> use a **calibrated** confidence threshold (CALM-style). Hold the halting *concept* as the north-star "I-get-it"
> seed. (2) **Where-to-read = readout-head CLASS-confidence, never goodness/energy** (goodness is density — Phase 3
> demoted it). (3) The free **native settling-time** halt signal is a **north-star (recurrent) tool**, not Stage-1
> (the feedforward cell can't settle). (4) Cost must be measured on the **continual** workload (early-exit's win is
> smallest exactly where we live), with an **oracle-exit** bound and a **distribution-shift** test. (5) Drop the
> "novel object" framing (scope-creep).

---

## B0 · Why this is the headline track

If [Track A](track-a-preservation.md) fully preserved, you'd just read the top. It won't fully preserve (the Tunnel
Effect says the extractor is task-bounded). So you **must** be able to *read at the right depth per task* — and,
ideally, **per sample** (the author's "lazy": an easy sample exits early, a hard one goes deep). That's exactly the
human-effort analogy the author keeps reaching for. The good news: the readout is on the **GD side** (~20%, where
the author *licenses* non-bio machinery), so this track has the most design freedom.

## B1 · Deep supervision — put a readout at every depth (the substrate-friendly base)

- **Deeply-Supervised Nets (DSN)** — Lee, Xie, Gallagher, Zhang, Tu (AISTATS 2015). Attach a **classifier +
  companion loss to *every* hidden layer**; train the sum of all of them. Originally to fight vanishing gradients,
  but the *structure* is exactly what we want: **a readout head living at every depth.**
- **Deep supervision / auxiliary classifiers** generally (GoogLeNet's aux heads; *Training Deeper CNNs with Deep
  Supervision* [1505.02496](https://arxiv.org/abs/1505.02496)) — the same idea, widely used.
- **Mono-Forward** (already in the repo) **is the forward-only/local version of this** — each layer gets a tiny
  projection → local cross-entropy, no signal crosses layers. So **"a small GD/projection readout head at every
  SCFF layer, trained locally"** is *already proven forward-only and substrate-faithful.*
- **For us:** this is the **base layer of the whole track.** Instead of one big all-tap readout (expensive) or one
  top readout (reads the tunnel), put a **tiny local readout at each depth** (Mono-Forward-style) — cheap, parallel,
  forward-only. Then the question becomes purely *"which head do we trust for this input?"* → B2/B3.
- **Cost-on-chip:** small (one classes×width projection per layer — far cheaper than a deep all-tap MLP).
- **SCFF-flow-safe?** ✅ — heads **read** their layer, never write back (this is `read`, not `write`).

## B2 · Early-exit — pick the depth by confidence (the cheap, deployable answer)

Don't run the whole stack for every sample; exit at the first head that's confident enough.

- **BranchyNet** ([1709.01686](https://arxiv.org/abs/1709.01686), 2017) — the original. Branch classifiers at
  intermediate layers; **exit when the prediction entropy is below a threshold.** Easy samples leave early, hard
  ones continue. Directly the author's "decider decides whether to forward to the next layer."
- **MSDNet** (Huang 2018) — anytime/budgeted inference with **dense connectivity to preserve coarse features** + 
  multiple exits. (The Track-A/Track-B bridge — see [Track A §A2](track-a-preservation.md).)
- **Shallow-Deep Networks (SDN)** (Kaya, Hong, Dumitras 2019) — frames *over-thinking*: deep nets waste compute (and
  can get *worse*) on easy inputs; confidence-based exits fix it. **"Over-thinking" is the author's "thinking harder
  doesn't mean thinking better"** (the general-relativity-vs-Newton-for-a-house line) — same idea, named.
- **CALM — Confident Adaptive Language Modeling** (Schuster et al, NeurIPS 2022) — the modern, careful version:
  *calibrated* confidence with a statistical guarantee on the quality drop from exiting early. The rigor we'd want
  before trusting an exit gate.
- **EENet** ([2301.07099](https://arxiv.org/abs/2301.07099), WACV 2024) — *learns* the exit policy (a small
  scheduler) instead of a hand-set threshold. **Early-Exit DNN: A Comprehensive Survey** (ACM Comput. Surv. 2024,
  [10.1145/3698767](https://dl.acm.org/doi/10.1145/3698767)) — the map of the whole field.
- **For us:** this is the **cheapest deployable form of "where to read."** With DSN heads (B1) already at each
  depth, an entropy/confidence gate picks the shallowest head that's sure → **per-sample lazy compute, and the
  80/20 is restored** (most samples never touch the deep layers). The confidence score is also exactly the kind of
  internal signal the author wants for the gate.
- **Cost-on-chip:** ~free (a comparator on a head's output). **SCFF-flow-safe?** ✅ (reads heads; the stack runs
  forward and just *stops early*).
- **Caveat:** exit thresholds need calibration (CALM's point); and a confidence gate can be over-confident and
  wrong — which is *why* the author's "danger signal" (overshoot) and the north-star "feeling" matter (B3 / Track C).

## B3 · Learned halting — the decider GD, and the seed of the "I get it" feeling

The author's decider GD ("loop: decide whether to forward; stop when the decider says stop; the threshold is a
learned signal") is **learned adaptive computation**, and the cleanest version is:

- **Adaptive Computation Time (ACT)** — Graves 2016. A network learns a per-step **halting probability**; it keeps
  computing until the accumulated halt mass crosses 1. The original "learn how long to think."
- **PonderNet** — *Learning to Ponder* ([2107.05407](https://arxiv.org/abs/2107.05407), DeepMind 2021). Reformulates
  halting **probabilistically** → **unbiased, low-variance** gradient for *when to stop*, no hand-tuned time
  penalty, stable. Halts when the network is **confident about the solution.** This is the author's decider GD done
  right, and **its halting signal is literally a learned "I'm confident / I get it" threshold** — the bridge to the
  north star (correctness-as-feeling). The author's "I get it threshold instead of average-error threshold" (Sol-4)
  **is PonderNet's halting head.**
- **AdaPonderLM** ([2603.01914](https://arxiv.org/abs/2603.01914), 2026) — token-wise adaptive depth via gated
  pondering; the current state of the idea.
- **For us:** **PonderNet-style halting over a deeply-supervised SCFF stack is the precise, literature-backed form
  of the decider GD.** It replaces the author's hand-built "compare prev/next layer accuracy" check-loop with a
  *learned* halting head that the data tunes — cheaper and more stable. And critically: **the halting confidence is
  the same object the north-star wants as "the feeling."** So building the decider now is *also* the first brick of
  the thinking brain.
- **The author's "danger signal" (overshoot beyond threshold → learn harder) and "effort knob" (global threshold
  decays over training)** map onto: PonderNet's halting distribution (how much to ponder) + a **loss-weighting by
  surprise** (learn hard samples harder) — which is *active-inference / prediction-error weighting* (north-star
  `4-signal.md`). Keep these as the *training-signal* refinements on top of the halting head.
- **Cost-on-chip:** small (a halting head = one more tiny readout + an accumulator cap). **SCFF-flow-safe?** ✅
  (reads, gates the forward run; doesn't rewrite SCFF).

## B4 · Conditional compute / "open only what we use" — the author's MoE & SSM mention

The author flagged SSM and MoE for "open SCFF only for the part we actually use." That's **conditional
computation**:

- **Sparsely-Gated Mixture-of-Experts** (Shazeer et al 2017) + **Switch Transformer** (Fedus et al 2021) — a gate
  routes each input to a **few experts**, not all → huge capacity, small per-sample compute. The "open only what we
  use," in the *width* dimension (which experts) rather than *depth* (how many layers).
- **Layer-skipping** — **SkipNet** (Wang et al 2018), **BlockDrop** (Wu et al 2018) — RL/gating to **skip layers
  per input.** The *depth* version of conditional compute, and the closer fit to "don't forward to the next SCFF
  layer."
- **State-Space Models / Mamba** (Gu & Dao 2023; S4, Gu 2021) — **input-dependent (selective) computation**: the
  dynamics adapt to the input. The author's instinct that SSMs "compute as I want" = selectivity. Also substrate-
  resonant: an SSM is *a trainable analog filter* (already in north-star `10-realtime.md` / `8-atom.md`).
- **For us:** **secondary to B1–B3** for the depth problem, but the *right* frame for the broader "lazy brain."
  Layer-skipping (SkipNet/BlockDrop) is the depth-dimension cousin of early-exit and could let the stack **skip
  tunnel layers entirely** for easy inputs. MoE is more relevant later (north-star: different experts = different
  "kinds of things" SCFF already sorts). SSM is an atom-level future, not this fix.
- **SCFF-flow-safe?** ⚠ depends — a *gate that routes/skips* is fine (it chooses a forward path); a gate that
  *rewrites* activations is not. Keep gates read-and-route only.

## B5 · The diagnostic that makes all of this possible — the per-task extractor-length profiler

Before any gate, we need to *see* where the extractor ends per task. The literature's tool is the **per-layer
linear probe** (which the project already uses):

- **Intermediate Layers Matter in Momentum Contrastive SSL** (NeurIPS 2021) — in contrastive SSL the **best layer
  is often *not* the last**; adding losses on intermediate layers improves them. Direct evidence for our reframe in
  the SSL setting, and a hint that **intermediate-layer objectives** (≈ deep supervision on SCFF) help.
- **For us:** build a cheap **extractor-length profiler** — per-layer probe (or per-head accuracy from B1) vs depth,
  per task — and **define the readout placement as "the probe's peak / where the slope flattens."** This
  *operationalizes* "where to read," turns the author's intuition into a number, and is the measurement every
  Track-B gate is approximating online. (It's also the clean way to test Track A: does preservation move the peak
  to the top?)

## B6 · Verdict / how to prioritise

1. **Base: deep-supervision heads (Mono-Forward-style) at each SCFF depth** — proven forward-only, cheap, the
   substrate already wants per-layer readouts. This *is* the readout redesign.
2. **Gate: confidence/entropy early-exit** (BranchyNet→SDN→CALM-calibrated) over those heads → **per-sample lazy
   compute, 80/20 restored.** The deployable answer to "where to read."
3. **Upgrade the gate to learned halting (PonderNet)** = the author's decider GD, done with an unbiased gradient —
   and the **same halting head is the north star's "I-get-it" feeling.** Build it once, use it twice.
4. **Profiler first (B5)** so every gate has ground truth to be checked against.
5. **MoE / layer-skip / SSM = the broader lazy-brain track**, not the immediate depth fix — park in the replan's
   later tiers.

> **The novelty worth naming:** nobody (that this session found) does **forward-only, unsupervised-bulk, adaptive-
> depth readout** — early-exit/halting are all backprop-trained supervised nets. SCFF (unsupervised forward-only
> bulk) + deep-supervision heads + learned halting would be **a genuinely new object**, and it's squarely on the
> project's identity. That's a contribution, not just a fix.

## Papers (this track)

DSN (Lee 2015) · Deep supervision [1505.02496](https://arxiv.org/abs/1505.02496) · Mono-Forward
[2501.09238](https://arxiv.org/abs/2501.09238) *(repo)* · BranchyNet
[1709.01686](https://arxiv.org/abs/1709.01686) · MSDNet (Huang 2018) · SDN (Kaya 2019) · CALM (Schuster 2022) ·
EENet [2301.07099](https://arxiv.org/abs/2301.07099) · Early-Exit Survey
[10.1145/3698767](https://dl.acm.org/doi/10.1145/3698767) · ACT (Graves 2016) · PonderNet
[2107.05407](https://arxiv.org/abs/2107.05407) · AdaPonderLM [2603.01914](https://arxiv.org/abs/2603.01914) ·
MoE (Shazeer 2017) / Switch (Fedus 2021) · SkipNet (Wang 2018) / BlockDrop (Wu 2018) · Mamba (Gu & Dao 2023) ·
Intermediate-Layers-Matter SSL (NeurIPS 2021).
