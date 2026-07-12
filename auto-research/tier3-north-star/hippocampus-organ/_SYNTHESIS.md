# Synthesis — The hippocampus organ: growing the LUT into a learning memory  (Tier 3)

**The question (Tier-3 form):** *What is the buildable path, and who is closest?* Rank candidate mechanisms by
**(a)** fit to "grow the LUT prototype store into a *learning* associative/retrieval memory," **(b)** analog-substrate-native-ness (content-addressable recall = a physical settle / crossbar read is cheap here), and **(c)** how well it composes with the existing **frozen SCFF bulk + closed-form namer**.

**Already in `draft6.0/research/north-star/1-memory.md`:** the dossier maps the *classics* — CLS (why two memories), NTM/DNC (controller + external RAM), Memory Networks (multi-hop read), Modern Hopfield ("retrieval = attention," the crossbar already does it), kNN-LM/RETRO (knowledge outside the weights), and 2016 Fast Weights (a third timescale). This card set does **not** re-summarize those; it adds the **2020–2026 frontier** the dossier lacks: the test-time-learning-memory line (TTT, Titans), the modern **delta-rule fast-weight** formulation, **scalable sparse key-value** memory (product keys / Memory Layers), **editable closed-form** episodic memory (Larimar), the **unifying theory** (test-time regression), and the **analog hardware** that makes recall physical (memristor aCAM).

---

## The landscape (what the field does now)

Two things happened since the dossier's classics. **First, memory became a *learner*, not a store.** The 2024–2026 line (TTT layers → Titans → the test-time-regression framework) reframes an associative memory as a small model whose weights are *updated online at inference* — "remembering = training." Titans makes this concrete with a biologically-shaped write rule: a **surprise** signal (gradient of `||M(k)−v||²`) gated by **momentum** and an **adaptive forgetting** decay. Wang–Shi–Fox then prove the whole zoo (linear attention, SSMs, fast weights, softmax attention, TTT) is *one* operation — **associative recall = test-time regression** — parameterized by three knobs (how you weight the past × the regressor class × the test-time optimizer).

**Second, the write can be gradient-free and the read can be physical.** The **delta-rule fast-weight** memory (Schlag 2021) is an error-correcting associative store built from nothing but an outer-product write and a matrix-vector read. **Larimar** shows a one-shot, closed-form, *editable and forgettable* episodic memory attached to a frozen body. **Memory Layers at Scale** shows content-addressable key-value memory scales to 128B params if you address it sparsely (**product keys**, `~2√N` cost). And **memristor analog CAM** (Li 2020) shows the recall itself — "which stored template matches this query" — is a single passive matchline event in analog silicon, with *ranged* (interval) matching per cell.

The camps, then: **(i) learning-by-gradient memory** (TTT, Titans, Memory Layers) — most capable, needs a backward pass; **(ii) learning-by-algebra memory** (delta-rule fast weights, Larimar, our own namer) — closed-form/local, crossbar-native, capacity-bounded; **(iii) the substrate** (analog aCAM / Hopfield-on-memristor) — where recall physically lives; **(iv) the map** (test-time regression) — the axes that connect them.

## The buildable path: which mechanism first, and why  ← the money section

**Ranked for our three criteria (fit × analog-native × composes with frozen-SCFF + closed-form-namer):**

**#1 — BUILD FIRST: a delta-rule fast-weight associative memory (Schlag 2021) on the crossbar.**
This is the minimal, honest upgrade that turns the LUT from a *passive prototype store* into a *learning memory* without violating a single project constraint. The memory is a matrix `W`; **write** `W += β(v − Wk)⊗k` (error-correcting outer product), **read** `v̂ = Wk` (matrix-vector). That is *literally a crossbar write and a crossbar read* — the most analog-native learning memory in the entire menu, no backward pass. It composes for free: the **frozen SCFF** supplies the key `k` (bulk activation), the **value** `v` is a replayed pattern or a namer target, and the **closed-form namer** reads the recalled value. The write-strength `β` is the natural home for the **drift/surprise gate we already compute (P8 DDM error-EMA)**. Fit ⭐⭐⭐⭐⭐, analog ⭐⭐⭐⭐⭐, composition ⭐⭐⭐⭐⭐.

**#1-substrate — the fabric it should run on: memristor analog CAM (Li 2020).** Not an algorithm to "build first" but the device the read half becomes: content-addressable recall as a passive matchline, with per-cell *interval* matching (a free covariance-tolerance surrogate). This is our "recall = a physical settle" claim, silicon-demonstrated by hardware people. Pair it with #1 to state the memory organ end-to-end (algebra write + physical read).

**#2 — the enrichers, folded onto #1 (all closed-form, all substrate-legal):**
- **Larimar's write/forget** (one-shot ridge solve + outer-product *subtraction*) — gives the LUT the **selective-forget** operation it lacks, and it's the *same algebra as our sleep re-fit*. Fold in for editability/eviction.
- **Product keys** (Memory Layers / Lample 2019) — the scaling answer: address a large prototype store in `~2√N`, so recall stays cheap (and sparse = low matchline energy) as the hippocampus grows. Fold in when capacity, not mechanism, is the bottleneck.

**#3 — the north-star horizon, kept as target not first-build: Titans / TTT.** These are the *behaviour* we want (a memory that keeps learning at test time, gated by surprise, with momentum and forgetting) but their literal mechanism is **gradient descent into an MLP memory** — the one expensive thing the project refuses. The move is not to build Titans; it's to build **"Titans-shaped" on a delta-rule core**: keep the surprise/momentum/forgetting skeleton, swap the SGD-MLP for the #1 delta-rule memory. The **test-time-regression framework (Wang 2025)** is the map that licenses this: it places our closed-form namer and a delta-rule memory in the *same regression cube*, tells us which cells we can reach (frozen keys, linear/kernel class, closed-form/delta optimizer) and exactly which capability we trade away by staying gradient-free (the MLP-regressor + multi-step-optimizer corner).

**One-line placement:** we are *already* on this map — the closed-form namer is the "exact-solve linear regression" corner of associative memory. Growing the LUT means adding the **online delta-rule corner** next to it, on an analog CAM fabric, with surprise-gated writes and closed-form forgetting — Titans' architecture, paid for in algebra and physics instead of backprop.

## The gap / what we haven't tried (concrete, testable)

1. **Make the LUT write.** Replace snapshot-storage with a **delta-rule outer-product write** keyed on SCFF activations; measure recall quality and whether it error-corrects a drifting stream (test against the **P11 autocorrelated-stream floor** — the framework predicts a closed-form/exact-solve memory beats a naive additive one on correlated streams).
2. **Give it a forget.** Add Larimar-style **outer-product subtraction** as the eviction op (vs P9 CBRS drop-a-slot); test targeted forgetting against the **P10 REV-staircase stale-namer sag**.
3. **Surprise-gate the write.** Route the **P8 DDM error-EMA** into the write-strength `β` (Titans' surprise/momentum, but closed-form) — the memory writes hard only when surprised, a leaky-RC-native gate.
4. **Scale addressing.** Swap flat cosine-over-all-prototypes for **product-key** routing; cost recall energy on the analog-CAM/P8.7 substrate ledger.
5. **Unify namer + memory as one regression at two rates** (test-time-regression prediction) — a genuine architectural simplification worth a probe.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Li et al. 2020 — Analog CAM with memristors](li-2020-analog-cam-memristors.md) | ⭐⭐⭐⭐⭐ | Content-addressable recall as a passive, single-cycle analog matchline — the fabric the LUT read becomes. |
| [Schlag et al. 2021 — Fast Weight Programmers / delta rule](schlag-2021-fast-weight-programmers.md) | ⭐⭐⭐⭐⭐ | The build-first learning memory: error-correcting outer-product write + matvec read = crossbar-native, gradient-free. |
| [Behrouz et al. 2025 — Titans](behrouz-2025-titans.md) | ⭐⭐⭐⭐⭐ | The north-star shape: surprise-gated, momentum, forgetting long-term memory — the target to emulate on a closed-form core. |
| [Sun et al. 2024 — TTT layers](sun-2024-ttt-layers.md) | ⭐⭐⭐⭐ | The principle: memory state IS a model, remembering IS a (self-supervised) learning step. |
| [Wang, Shi & Fox 2025 — Test-time regression](wang-2025-test-time-regression.md) | ⭐⭐⭐⭐ | The map: all these memories = test-time regression on 3 axes; places our namer + a delta memory in one cube. |
| [Berges et al. 2024 — Memory Layers at Scale](berges-2024-memory-layers-at-scale.md) | ⭐⭐⭐⭐ | Product-key sparse addressing → content-addressable recall stays cheap (`~2√N`) as the store grows. |
| [Das et al. 2024 — Larimar](das-2024-larimar.md) | ⭐⭐⭐⭐ | One-shot closed-form write + selective **forget** (outer-product subtraction) on a frozen body — same algebra as our sleep. |

## Leads spawned

- **DeltaNet / gated-DeltaNet** (Yang et al. 2024) — the delta-rule memory made parallel/scalable; the likely substrate-legal Titans. → own topic.
- **Memristor Hopfield / energy-based recall in-memory** — Modern Hopfield on the same aCAM fabric; unifies attention-recall with the device. → own topic.
- **Sparse Distributed Memory (Kanerva 1988) + Pseudo-Inverse Memory** — the closed-form associative-store lineage under Larimar. → own topic.
- **Product-key / product-quantization addressing (Lample 2019, FAISS)** — the scalable content-addressable read for a large analog prototype store. → own topic.
- **Whitening / preconditioned online regression** — the test-time-regression fix for correlated keys; ties to the namer's anisotropy ceiling. → cross-links t2.2/t2.6.
- **BABILong / needle-in-haystack** — long-context recall evals for a future recurrent prefrontal↔hippocampus loop test.
