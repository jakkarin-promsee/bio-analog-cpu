# Hopfield Networks is All You Need
- **Authors / Year / Venue:** Hubert Ramsauer, Bernhard Schäfl, Johannes Lehner, … Sepp Hochreiter (17 authors) / 2020 / arXiv:2008.02217 → ICLR 2021
- **Link:** https://arxiv.org/abs/2008.02217 (fetched)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning as the unifying frame)
- **Relevance:** ⭐⭐⭐⭐ — the Hopfield revival, and the proof that **transformer attention IS one step of energy descent in a continuous Hopfield net**. Memory and attention collapse into "settle to the nearest energy valley" — the frame our LUT recall wants to be.

## TL;DR
Generalize the classic binary Hopfield network to **continuous states** with a new energy function whose minima are the stored patterns. The associated update rule retrieves a stored pattern in **one step**, stores **exponentially many** patterns (in the embedding dimension), and — the headline — is **mathematically identical to the attention mechanism of transformers**. Associative memory, attention, and energy minimization are one object.

## The mechanism (how it actually works)
Store patterns as columns of `X`. Define an energy over a query state `ξ` that combines a `log-sum-exp` over the similarities `X^T ξ` (which digs a valley near each stored pattern) with a quadratic term (which keeps `ξ` bounded). Minimizing this energy by the **Concave-Convex Procedure** gives a closed-form update:

`ξ_new = X · softmax(β · X^T ξ)`

Read that update: it is **exactly attention** — queries `ξ`, keys/values `X`, a softmax with inverse-temperature `β`. One application already lands in a minimum (retrieval is essentially single-step). The temperature `β` controls the regime: high `β` → sharp, retrieves a **single** stored pattern (a true memory); moderate `β` → a **metastable** state averaging a cluster (a category); low `β` → averages **everything** (a global summary). So a transformer layer is a Hopfield retrieval, and stacking layers walks from broad averaging (low layers) to pattern-specific retrieval (high layers).

## Key results / claims
Exponential storage capacity with retrieval error controllable by `β`; one-update convergence; the exact attention equivalence, letting the authors classify transformer heads by which fixed-point regime they occupy. Demonstrated on multiple-instance learning, immune-repertoire classification (a large-memory task), UCI benchmarks, and drug design.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the hippocampus LUT (recall); the north-star "memory = energy descent" and "modern Hopfield = attention = our LUT" line in `21-energy.md`.
- This is the **rigorous version of "recall is a settle"**: our LUT prototype read wants to be *one step of energy descent to the nearest stored pattern* — and this paper says that step is a softmax over stored keys, i.e. a crossbar matvec + a softmax comparator. That is substrate-native.
- The **`β`-regime knob is a design gift**: the same physical recall gives sharp single-memory retrieval or soft category-averaging just by tuning one temperature (an analog bias). Our metastable/category reads and exact-memory reads are one mechanism at two temperatures.
- Placement: our namer's prototype-nearest read and this Hopfield retrieval are the *same algebra*; the difference is we fit prototypes closed-form (SLDA/RanPAC) rather than storing raw patterns.

## Follow-on leads
Energy Transformer (Hoover 2023) — the trainable multi-layer version; modern Hopfield as a drop-in memory layer; analog CAM / memristor Hopfield (tier4 t4.1 Cai 2020) for the physical single-cycle matchline.
