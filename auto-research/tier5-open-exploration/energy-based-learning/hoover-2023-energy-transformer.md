# Energy Transformer
- **Authors / Year / Venue:** Benjamin Hoover, Yuchen Liang, Bao Pham, Rameswar Panda, Hendrik Strobelt, Duen Horng Chau, Mohammed J. Zaki, Dmitry Krotov / 2023 / arXiv:2302.07253 → NeurIPS 2023
- **Link:** https://arxiv.org/abs/2302.07253 (fetched)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning as the unifying frame)
- **Relevance:** ⭐⭐⭐⭐ — the explicit unification: **attention + energy-based models + associative memory as one block whose forward pass is gradient descent on a single global energy.** The clearest existing template for a "think-block that settles" — our north-star loop, published.

## TL;DR
Replace a transformer block's stack of operations with a **single scalar energy** over all tokens; the block's "forward pass" is literally **gradient descent on that energy** for a few steps. The design fuses three lineages — attention, EBMs, and modern Hopfield associative memory — so the network *computes by descending a landscape* instead of applying a feedforward recipe.

## The mechanism (how it actually works)
Every token has a state vector. Define a global energy `E(states)` with two terms: (1) an **attention energy** — a `log-sum-exp` over query–key alignments that *lowers* energy when tokens attend coherently (this is the Hopfield energy of Ramsauer 2020, generalized to token interactions); and (2) a **Hopfield / associative-memory energy** per token — a local landscape whose minima are stored feature prototypes. The forward pass **does not** compute `Q,K,V → output` once; instead it takes the state, computes `∂E/∂state`, and **descends** — repeating for `T` steps until the tokens settle into a low-energy configuration. The output is the settled state.

Because the block is defined by an energy rather than a procedure, its dynamics are analyzable (it *provably* decreases `E`), and depth becomes **time**: more descent steps = a deeper effective computation on the *same* weights. Trained end-to-end (the energy has learnable parameters) on image completion and graph tasks.

## Key results / claims
Competitive on masked image completion, graph anomaly detection, and graph classification, while giving transformer attention a **principled energy foundation** it otherwise lacks. Demonstrates that a working, trainable model can be built entirely as "descend a designed energy," with attention emerging as one term of that energy's gradient.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the north-star recurrent "think-until-it-settles" loop; the correctness-as-feeling halt; the LUT-as-attention read.
- This is the **cleanest published shape of our north-star block**: a unit whose computation is *iterate gradient descent on an energy until it settles*, where **depth = number of settle-steps on resident weights** (exactly our "resident weights buy depth from time" economics). An analog network does that descent physically.
- The **energy value itself is a free halt/confidence signal**: "stop when `E` stops dropping" is our settle-Δ feeling, and this paper builds the loop around exactly that scalar. Cross-refs tier3 EBT (Gladstone 2025) and IRED (Du 2024) — Energy Transformer is the *architecture-level* member of that family.
- Honest gap: it is trained end-to-end by backprop-through-descent; our constraint is no backward pass. The **shape** ports (energy block + settle); the *training* is the open north-star problem (EqProp-style local rules would be the substrate-legal way to learn the energy).

## Follow-on leads
Dmitry Krotov's Dense Associative Memory line (energy of higher-order interactions); EqProp / Ising-EqProp (tier4 t4.2) as the local learning rule for such an energy; the orbit/non-convergence risk when the settle doesn't have a unique minimum (monDEQ, tier3 t3.2).
