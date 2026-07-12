# Linear Transformers Are Secretly Fast Weight Programmers

- **Authors / Year / Venue:** Imanol Schlag, Kazuki Irie, Jürgen Schmidhuber / 2021 / ICML (PMLR 139:9355–9366)
- **Link:** https://arxiv.org/abs/2102.11174 — fetched
- **Tier / Topic:** tier3 / t3.1 hippocampus organ
- **Relevance:** ⭐⭐⭐⭐⭐ — The **learning-memory kernel** for the hippocampus organ: an associative memory that is one outer-product-written weight matrix updated by a local **delta rule** — closed-form, one-shot, crossbar-native.
- **Already in `north-star/1-memory.md`:** the 2016 "Fast Weights" (Ba/Hinton) is cited as a third timescale. This is the modern, load-bearing formulation the dossier does *not* have.

## TL;DR
A fast-weight memory is a matrix `W` that stores associations as a **sum of outer products** `W += v ⊗ k` (write value `v` under key `k`) and recalls by `v̂ = W k` (a matrix-vector read). Schlag et al. prove this *is* linearised self-attention, then fix its capacity problem: replace the naive additive write with a **delta rule** — before writing, read what's already stored at `k`, and write only the *correction* `(v − W k)`. That one change turns a leaky sum-store into an error-correcting associative memory.

## The mechanism (how it actually works)
Classic Fast Weight Programmers (Schmidhuber 1992): a slow network emits, per step, a (key, value) pair and *programs* a fast weight matrix via `W_t = W_{t-1} + v_t ⊗ k_t`. Reading is `W_t q_t`. This is exactly the numerator of linear attention with feature map φ — "attention" and "an outer-product associative memory" are the same object. The failure mode: pure addition overwrites and saturates — write two values under similar keys and they blur (the ~0.14N Hopfield capacity problem in another guise).

The **delta-rule** fix: treat each write as a one-step regression. Compute the current retrieval `v̄ = W_{t-1} k_t`, form the error `(v_t − v̄)`, and write `W_t = W_{t-1} + β_t (v_t − v̄) ⊗ k_t`. Now the memory *corrects* the mapping at `k_t` toward `v_t` instead of piling on top of it — it can update an existing association, not just add new ones. β is a learned write-strength (a per-write learning rate/gate). Everything is local, uses only a read and an outer-product write, and needs no backward pass through time to update the memory itself.

## Key results / claims
- Formal equivalence: linearised softmax attention = a Fast Weight Programmer with additive writes.
- The delta-rule write substantially improves synthetic associative-recall and language-model perplexity over the additive/linear-attention baseline, at the same cost — the capacity fix is essentially free.
- Establishes the modern lineage that Titans/DeltaNet/TTT all descend from: memory = weights, writing = a local optimisation step.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** hippocampus-LUT (the learning upgrade) · SCFF bulk (supplies keys) · closed-form namer (reads values) · north-star recurrent recall loop.
- **Same as us:** the whole operation is **outer-product write + matrix-vector read** — literally a crossbar write and a crossbar read. No gradient descent, no backward pass, fully local. This is the *most substrate-native learning memory in the entire menu.* Our current LUT already does the read (`W k` = similarity match); this adds the *learning write*.
- **Different from us:** our LUT today is a **passive prototype store** — it holds snapshots and hands SCFF a random negative; it does not error-correct or bind a queried key to a retrieved value. The delta rule is exactly the missing "make it a *learning* memory" step: write associations and refine them online.
- **What we could borrow or test:** promote the LUT from "prototype snapshots" to a **delta-rule fast-weight matrix**: SCFF bulk activation = key, the namer target or a replayed pattern = value; write with `(v − Wk)⊗k`, read with `Wk`. It composes with the frozen SCFF (keys come free from the bulk) and the closed-form namer (which reads the recalled value) *without adding a backward pass*. The write-strength β is the natural home for the drift/surprise gate we already compute.
- **What contradicts or challenges us:** capacity is still bounded by dimension d (associations ≈ d before interference); the delta rule buys refinement, not infinite capacity — so eviction/consolidation (our sleep) is still required. And the outer-product write needs signed updates on the crossbar (our sign-as-digital primitive covers this, but it's a real analog constraint).

## Follow-on leads
- Irie et al. 2021 "Going Beyond Linear Transformers with Recurrent Fast Weight Programmers."
- Yang et al. 2024 "Parallelizing Linear Transformers with the Delta Rule over Sequence Length" (DeltaNet) — the parallel/scalable delta memory.
- Schmidhuber 1992 original Fast Weights — the root citation.
