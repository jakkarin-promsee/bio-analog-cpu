# Track A — preservation: make the tunnel harmless

> **The job:** stop the deep layers from *overwriting* the extractor. If early class-relevant features survive to
> the top, then "read the top" == "read the extractor" and the readout-placement problem dissolves (see
> [README §2](README.md)). This is the author's **Solution 2 (residual)** — and it has a named, proven, very cheap
> form. **But** the literature also has a sharp warning that residuals are not a free win, so this track is "test
> it carefully," not "bolt it on."
>
> **⚠ POST-REVIEW CORRECTIONS (see [the Phase-5 design decision-record](../../../src/phase5/design.md), authoritative):** (1) **α
> defaults to FROZEN / init-based** (Fixup-style) — a *local*-loss-trained α opens the gate exactly when the block
> starts drifting off-manifold; learned-α only if driven by the GD-readout. (2) Preserve the **class DIRECTION**, not
> rank/variance. (3) **Whitening (VICReg/Barlow) is rejected AS THE LEVER** (restores rank — a symptom we discounted —
> and its batch-stats rot under continual shift); prefer a per-sample class-subspace term. (4) The **S5
> mandatory-norm × residual** interaction is a first-class risk. (5) A dead-frozen α also "stops the tail decaying" →
> require **per-block α→0 ablation** to prove contribution.

---

## A0 · The diagnosis this track is fixing

Three literatures say the *same* thing the project found:

- **The Tunnel Effect** ([2305.19753](https://arxiv.org/abs/2305.19753), NeurIPS 2023) — deep layers form a tunnel
  that compresses/drifts; depth only lengthens it; **it hurts OOD + continual.** (The keystone — [README §1](README.md).)
- **The myopia diagnosis** (already in the repo's `direction-1` dossier): *"local algorithms fail because there's
  no mechanism for higher layers to communicate with lower layers — lower layers learn representations that aren't
  productive for the higher layers"* (Parallel Training with Local Updates
  [2012.03837](https://arxiv.org/abs/2012.03837); Interlocking Backprop
  [2010.04116](https://arxiv.org/abs/2010.04116)).
- **Dimensional / rank collapse** in deep self-supervised stacks — the rank-drop the project measured (erank
  declines) is the same signature the tunnel-effect rank-drop names. *(Note our own refinement: we proved rank is a
  **symptom**, not the lever — `widen` adds rank without adding accuracy. So preservation must preserve the
  **class direction**, not merely the rank.)*

## A1 · Near-identity residual init — the author's Sol-2, named and proven (the lead candidate)

The author's exact idea — *"initialize the SCFF output near zero, let it change the output only when confident, so
`residual ≈ input` survives to the last layer"* — is a known, battle-tested trick:

- **ReZero** — *ReZero is All You Need: Fast Convergence at Large Depth*
  ([2003.04887](https://arxiv.org/abs/2003.04887)). Each block computes **`y = x + α·f(x)`** with a **single
  learnable scalar α initialized to 0.** The block *starts as the identity* and only learns to contribute when it
  helps. Result: trains **thousands of fully-connected layers** with fast convergence, where vanilla deep nets
  can't. This is the author's idea, verbatim, with a name and a proof.
- **Fixup** — *Residual Learning Without Normalization* ([1901.09321](https://arxiv.org/abs/1901.09321)). Same
  spirit via initialization: zero-init the last layer of each residual branch + careful rescaling → trains
  **10,000-layer** residual nets with **no normalization**. Relevant because *it removes the dependence on
  batch/normalization* — and our cell is per-sample, no batch stats, so a normalization-free preservation scheme is
  a natural fit.
- **LayerScale** (CaiT, Touvron et al 2021) — a learnable **per-channel** diagonal scale on each residual branch,
  init near 0 (~1e-4..1e-6). The finer-grained cousin of ReZero: lets *some* channels of a block contribute while
  others stay identity — which maps onto the author's "change the output only when confident," per-feature.
- **Hyper-Connections** — ICLR 2025 ([2409.19606](https://arxiv.org/abs/2409.19606)). A generalization of residual
  connections that explicitly trades off the **seesaw between gradient-vanishing and representation-collapse** —
  i.e., a *learnable* mix of "preserve" vs "transform" per layer. The modern, more-expressive version of the
  ReZero gate; worth knowing as the upgrade if a single scalar α is too blunt.

**Mechanism (why it fixes the tunnel):** with `y = x + α·f(x)`, the extractor's representation `x` is *carried
forward additively*. A tunnel layer can no longer overwrite it — the worst it can do is add noise via `α·f(x)`, and
α-near-0 means it adds *nothing until the local objective finds a contribution worth making*. So the top layer
retains the extractor's class structure **plus** whatever real refinement deep layers found. "Read the top" becomes
safe.

- **For us:** this is the **cheapest, most substrate-faithful, most author-native** preservation test. On silicon a
  per-block α is **one extra capacitor** (or the per-channel LayerScale = one small vector); the skip is **a wire**.
  No batch stats, per-sample, forward-only. It directly attacks the *multiplier* in the trigger×multiplier cause.
- **Cost-on-chip:** ~free (one scalar/block + an adder wire).
- **SCFF-flow-safe?** ✅ — it *adds to* the stream, never rewrites it. This is the additive-preserve the author
  wanted, and it's the opposite of the forbidden `write`.
- **The form question the author asked** (`input + SCFF` vs `input − SCFF`): **`+`**, with α init 0. The point is to
  *preserve x and let SCFF contribute a correction*; subtraction would erase, addition-from-zero preserves.

## A2 · Dense feature reuse — preserve by concatenation instead of addition

- **DenseNet** (Huang et al 2017) — every layer receives the concatenation of *all* previous layers' features.
  Already noted in the north-star dossier as "his Mechanism A ≈ DenseNet feature reuse (~1/3 params)." Preservation
  by *keeping every layer available* rather than carrying a running sum.
- **MSDNet** (Multi-Scale Dense Network, Huang et al 2018) — **the bridge to Track B.** Dense connectivity
  *specifically to preserve coarse features* **+ early-exit classifiers** at multiple depths for *anytime*
  prediction. This is **preservation (A) and adaptive-readout (B) in one architecture** — the closest existing
  thing to what this project wants, just done with backprop and conv. A forward-only MLP analogue is a real design
  target.
- **For us:** concatenation preserves *everything* but grows the input width every layer — fights the substrate's
  "depth not width" instinct and the analog crossbar's fixed rails. **Additive (A1) is the better substrate fit;**
  keep DenseNet/MSDNet as the *conceptual* proof that "carry early features forward" earns depth, and steal
  MSDNet's *combined preserve+exit* shape for the [Track B](track-b-adaptive-readout.md) design.
- **SCFF-flow-safe?** ✅ (read/concat, no rewrite) — but **cost-on-chip:** ✗ (growing width = more Scaps).

## A3 · The honest warning — residuals are NOT a free win

Two cautions, both load-bearing, so this track is "test," not "assume":

- **Residual Connections Harm Generative Representation Learning**
  ([2404.10947](https://arxiv.org/abs/2404.10947)). In SSL/generative settings, a residual skip can let information
  **route *around* the layer**, so the layer never has to build a good representation — the skip becomes a cheat
  path that *weakens* the learned features. For a contrastive/discriminative objective this may not bite the same
  way, but it's a direct threat to "just add skips," and it's why **α (ReZero) matters**: a learnable gate that
  *earns* its contribution avoids the lazy-bypass failure better than an ungated `x + f(x)`.
- **The Tunnel Effect's own verdict:** preservation **extends the extractor, it doesn't abolish the tunnel.** The
  extractor length is *task-set*; a residual lets you safely *read the top* and may push the useful boundary a bit
  deeper, but it will **not** turn a 5-useful-layer task into a 50-useful-layer one. So Track A's realistic promise
  is **"make depth safe to read, not unbounded to use."** Don't oversell it; pair it with Track B.

## A4 · The forward-only-depth family (already in the repo — pointer, not duplicate)

The repo's [`research/papers/phase3/direction-3-forward-only-alternatives.md`](../phase3/direction-3-forward-only-alternatives.md)
already maps this; carry it forward unchanged:

- **GIM / CLAPP / CLAPP++** — forward-only, unsupervised, **info-preserving InfoNCE that composes with depth**;
  CLAPP++ matches backprop-SSL on CIFAR-10 ([2601.21683](https://arxiv.org/abs/2601.21683)). *This is the objective
  we already adopted.* The open question Track A adds: **does a residual/ReZero gate on top of contrast+coordination
  push the extractor deeper / hold the tail?**
- **Coordination window (OLU / DF-O)** — the repo's `direction-1`; the w=2 lever we deploy. Track A's residual is
  *orthogonal* to it (preserve vs coordinate) — they likely **stack** (coordinate the climb, preserve against the
  drift).
- **2025 forward-only depth notes (new this session):** *Training CNNs with Forward-Forward* (Sci. Reports 2025)
  confirms vanilla FF "encounters feature-scaling and deactivated-neuron issues, limiting it to shallow nets" —
  i.e., the **energy-FF dead-neuron wall** (which our contrast cell already escaped). **ASGE**
  ([2509.12394](https://arxiv.org/abs/2509.12394)) and **TinyFoA** (AAAI 2025, on-device forward-only) are the
  latest scaling attempts — conv/engineering, not a new principle, but worth a glance for tricks.

## A5 · Verdict / how to prioritise

1. **Lead with the ReZero α-gate** on the adopted cell (contrast + w=2). It's the author's own idea, named and
   proven, **one scalar per block**, forward-only, per-sample, SCFF-flow-safe, and it directly attacks the cause.
   Cheapest high-value architectural test in the whole session.
2. **Measure what it buys** with the per-layer probe + the W64 control re-run: does the tail stop decaying (does
   "read-top" approach "read-peak")? Does the extractor boundary move deeper? Use the headroom + mixed tasks (the
   mixed task is the cleanest decay detector).
3. **If the single scalar is too blunt → LayerScale (per-channel) → Hyper-Connections.**
4. **Hold the honest ceiling in view:** the Tunnel Effect says preservation makes depth *safe to read*, not
   *unbounded*. So Track A's real deliverable is **"reading the top is now correct"** → which then makes
   [Track B](track-b-adaptive-readout.md)'s job easier (or, if read-top fully works, smaller).
5. **Watch the bypass-cheat threat** ([2404.10947](https://arxiv.org/abs/2404.10947)): verify the gated blocks
   still *learn* (probe rises through the extractor), not just pass input through.

## Papers (this track)

ReZero [2003.04887](https://arxiv.org/abs/2003.04887) · Fixup [1901.09321](https://arxiv.org/abs/1901.09321) ·
LayerScale/CaiT (Touvron 2021) · Hyper-Connections [2409.19606](https://arxiv.org/abs/2409.19606) ·
DenseNet (Huang 2017) · MSDNet (Huang 2018) · *Residual Harms Generative Repr.*
[2404.10947](https://arxiv.org/abs/2404.10947) · Tunnel Effect [2305.19753](https://arxiv.org/abs/2305.19753) ·
GIM/CLAPP/CLAPP++ [2601.21683](https://arxiv.org/abs/2601.21683) · ASGE
[2509.12394](https://arxiv.org/abs/2509.12394) · TinyFoA (AAAI 2025).
