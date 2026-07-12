# Memory Layers at Scale

- **Authors / Year / Venue:** Vincent-Pierre Berges, Barlas Oğuz, Daniel Haziza, Wen-tau Yih, Luke Zettlemoyer, Gargi Ghosh / 2024 / arXiv 2412.09764 (Meta FAIR)
- **Link:** https://arxiv.org/abs/2412.09764 — fetched (code: github.com/facebookresearch/memory)
- **Tier / Topic:** tier3 / t3.1 hippocampus organ
- **Relevance:** ⭐⭐⭐⭐ — The **scalable, sparse key-value memory** blueprint: a trainable content-addressable lookup with **product keys** so recall touches only a few rows — the "grow the LUT to millions of entries without paying to read all of it" answer.
- **Already in `north-star/1-memory.md`:** kNN-LM/RETRO (retrieval outside the weights). This is the *in-weights, trainable, sparse-access* memory the dossier lacks; anchors to Lample et al. 2019 (PKM), also new to us.

## TL;DR
A memory layer is a big trainable key-value table queried by similarity: a query picks its top-k keys, and the output is the weighted sum of the matching values. The trick that makes it scale is **product keys** — factor the key space into two halves so finding the top-k over `N` keys costs `~2√N` comparisons instead of `N`. Meta scales this to 128B memory params and shows memory-augmented models beat dense models with >2× the compute, *especially on factual recall*.

## The mechanism (how it actually works)
Take an external table of `N` (key, value) slots. Naive lookup compares the query to all `N` keys — too expensive at scale. **Product-key memory** (Lample et al. 2019) splits each key into two sub-keys from two small codebooks of size `√N`; the query is likewise split, you find the top-k in each half (`√N` compares each), and their Cartesian combination gives the global top-k. So sub-linear, sparse addressing: only `k` values are read and updated per query. Both keys and values are trainable by gradient, but *only the selected slots receive gradient* — the access pattern is inherently sparse. "Memory Layers at Scale" makes this parallelizable across GPUs, shares one memory pool across several layers, and adds input-dependent gating; the result is dedicated **look-up capacity** that adds parameters without adding FLOPs, complementing the compute-heavy feed-forward layers.

## Key results / claims
- Scales cleanly to **128B memory parameters**, pretrained to 1T tokens; augmented models beat dense baselines with **>2× the compute budget**, and beat compute-and-param-matched MoE.
- Gains are **largest on factual / knowledge tasks** — the memory carries facts the dense net no longer has to store in its weights (the "resident facts ≠ resident weights" thesis, now at scale and trainable).
- Sparse top-k access keeps read/update cost roughly constant as the table grows.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** hippocampus-LUT (scaling it up) · SCFF bulk (query source) · closed-form namer (the "values" could be namer statistics).
- **Same as us:** this **is** our LUT's mature form — a content-addressable key-value store that the compute reads by similarity, holding knowledge the slow brain never absorbs into weights. It validates keeping the hippocampus as a *separate, growable* organ and the 80/20 division of labour (cheap lookup vs expensive compute), from an engineering source.
- **Different from us:** keys *and* values are learned by **gradient**, and access is via learned soft top-k, not our winner-take-all cosine-vigilance allocation. Our store today is passive snapshots; theirs is a trained parameter bank.
- **What we could borrow or test:** the **product-key trick** is the single most useful transplant for analog scaling — factored addressing means a crossbar recall over a *huge* prototype store touches only `~2√N` rows, i.e. content-addressable recall stays cheap as the hippocampus grows. That directly answers "how does the LUT scale to a real memory without the read cost exploding," and `~√N` sparse access is exactly what an analog matchline array wants (fewer active lines = less energy). Test: replace our flat cosine-over-all-prototypes lookup with product-key sub-key routing; measure recall quality vs read energy against the P8.7 substrate ledger.
- **What contradicts or challenges us:** the values here are trained end-to-end; to stay substrate-legal we'd write values by delta-rule/closed-form (Schlag/Larimar) instead. And the paper's wins are on *factual recall in a big LM* — whether the same capacity story holds for a small analog continual learner is untested (our scale is 1000× smaller).

## Follow-on leads
- Lample, Sablayrolles, Ranzato, Denoyer, Jégou 2019 "Large Memory Layers with Product Keys" (arXiv 1907.05242) — the root mechanism.
- FAISS / product quantization — the retrieval-systems lineage for approximate content-addressable search.
- Mixture-of-Experts routing — the sibling "sparse-access big-parameter" idea; contrast for the hippocampus addressing scheme.
