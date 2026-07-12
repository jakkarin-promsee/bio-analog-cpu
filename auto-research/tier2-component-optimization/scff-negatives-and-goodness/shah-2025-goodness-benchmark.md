# In Search of Goodness: Large Scale Benchmarking of Goodness Functions for the Forward-Forward Algorithm
- **Authors / Year / Venue:** Arya Shah, Vaibhav Tripathi / 2025 / arXiv
- **Link:** https://arxiv.org/abs/2511.18567
- **Tier / Topic:** tier2-component-optimization / t2.1 SCFF negatives & goodness
- **Relevance:** ⭐⭐⭐⭐ — the first systematic answer to "is Σh² actually the right goodness?": 21 goodness functions benchmarked head-to-head, with energy/carbon cost measured alongside accuracy.

## TL;DR
Benchmarks **21 distinct goodness functions** for FF across four image datasets (MNIST, FashionMNIST, CIFAR-10, STL-10), measuring accuracy *and* energy consumption / carbon footprint. Finds the default sum-of-squares is **not** optimal: alternatives like `game_theoretic_local` (97.15% MNIST), `softmax_energy_margin_local` (82.84% FashionMNIST), and `triplet_margin_local` (37.69% STL-10) beat the baseline, with real accuracy-vs-compute trade-offs. Conclusion: the goodness function is a **pivotal hyperparameter**, not a fixed design given.

## The mechanism (how it actually works)
Not a new method — a measurement instrument. They hold the FF training loop fixed and swap only the per-layer scalar objective through a zoo of 21 candidates: energy variants (sum/mean of squares), margin forms (triplet, N-pair, softmax-energy margins), game-theoretic/local-competition scores, and normalized/temperature-scaled variants. Each cell reports classification accuracy plus measured energy and carbon cost, so the output is a Pareto surface over (goodness function × dataset). The headline pattern: **margin-shaped and competition-shaped goodness beats raw energy**, and the winner is dataset-dependent — there is no universal best, but Σh² is reliably dominated.

## Key results / claims
- 21 goodness functions × 4 datasets; code public.
- Best-per-dataset: game_theoretic_local 97.15% (MNIST), softmax_energy_margin_local 82.84% (FashionMNIST), triplet_margin_local 37.69% (STL-10).
- Standard sum-of-squares goodness is outperformed by several alternatives; accuracy and energy trade off — some winners cost more compute.
- Framing: goodness = a first-class hyperparameter of FF design.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk objective (P3's objective-family finding, P5's temperature finding).
- **Same as us:** treats the objective as *the* lever (our P3 conclusion, independently confirmed at scale); measures energy alongside accuracy (our house methodology).
- **Different from us:** they sweep goodness *within* the supervised-FF frame with generated negatives; we swapped family entirely (energy → InfoNCE contrast). Our summation-form InfoNCE is not in their 21.
- **What we could borrow or test:** (1) the **margin-shaped** family — our InfoNCE has no margin; a margin term on the positive-vs-negative similarity gap is a one-line change and their results suggest it is the single most reliable shaping. (2) Their protocol: we never ran a *goodness bake-off inside the contrast family* (summation-InfoNCE vs N-pair vs triplet-margin at matched budget) — P3 compared families, not members. (3) Energy-per-goodness numbers as a sanity check on which shapings are compute-cheap enough for the substrate.
- **What contradicts or challenges us:** dataset-dependence of the winner warns that our temp-0.2 summation-InfoNCE, tuned on our synth+digits ladder, may not be the right member of the family on other streams — consistent with our own P11 arena-dependence.

## Follow-on leads
- The specific `game_theoretic_local` scoring (per-unit competition) — overlaps CwComp's competitive-learning story; possible label-free variant.
- Their energy measurement methodology vs our substrate meter (P8) — different currencies, worth a bridge note.
