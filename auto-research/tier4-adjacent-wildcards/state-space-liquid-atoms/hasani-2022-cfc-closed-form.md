# Closed-form Continuous-time Neural Networks (CfC)

- **Authors / Year / Venue:** R. Hasani, M. Lechner, A. Amini, L. Liebenwein, A. Ray, M. Tschaikowski, G. Teschl, D. Rus / 2022 / Nature Machine Intelligence 4(11):992–1003
- **Link:** https://www.nature.com/articles/s42256-022-00556-7 (DOI 10.1038/s42256-022-00556-7); open record https://research-explorer.ista.ac.at/record/12147
- **Tier / Topic:** tier4 / t4.4 state-space & liquid atoms
- **Relevance:** ⭐⭐⭐⭐⭐ — the *closed-form* version of the RC-with-learnable-τ atom: our closed-form philosophy applied to the continuous-time neuron itself.

## TL;DR
A Liquid Time-Constant (LTC) neuron is an RC element with a state- and input-dependent time constant, `dx/dt = −x/τ(x,I) + f(x,I)` — but evaluating it needs a numerical ODE solver, which is the compute bottleneck. CfC derives a **tightly-bounded closed-form approximation** of the integral that governs LTC dynamics (previously unknown in closed form), so the neuron becomes an explicit formula in `t` — no solver. Result: same continuous-time expressivity, 1–5 **orders of magnitude** faster train/infer.

## The mechanism (how it actually works)
Start from the leaky-integrator ODE with a coupling term. The LTC insight is that the *effective time constant* is not a fixed RC value but `τ_sys = τ/(1+τ f(x,I))` — it speeds up or slows down with the input, so one neuron can act fast or slow on demand. That ODE has no analytic solution, so LTC nets call an ODE solver at every step. CfC replaces the solver with a learned **time-continuous gate**: the neuron output is written as an interpolation `x(t) = σ(−[…]t)⊙g(·) + (1−σ(−[…]t))⊙h(·)` — a sigmoidal *time-gate* that smoothly blends between an early-time behaviour `g` and a late-time behaviour `h`, with `t` appearing explicitly. The gate is exactly the closed-form stand-in for "how far has this RC line decayed by time t." Everything is now a feed-forward formula, trained end-to-end by gradient descent.

## Key results / claims
- 1–5 orders of magnitude faster in training and inference than ODE-based (Neural-ODE / LTC) counterparts.
- Competitive-to-better on time-series: human activity recognition, physical dynamics, autonomous-driving steering; scales far better than ODE nets.
- Retains the LTC stability/boundedness story while removing the solver.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star recurrent atom; the namer's *closed-form* stance extended to the recurrence itself.
- **Same as us:** the entire pitch is "the analog dynamics ARE the computation, but you don't have to *integrate* them — you evaluate a closed form." That is our namer creed (SLDA/RanPAC: no gradient loop, solve the formula) transplanted onto the temporal atom. The atom is a leaky cap with a tunable time constant — the exact element our substrate already proposes for SCFF read-layers.
- **Different from us:** CfC learns the neuron parameters (including τ) by **backprop-through-time**. Our whole 11-phase discipline is *no backward pass that leaves the chip*. So CfC gives us a beautiful analog-native forward atom but arrives with the one training rule we've refused.
- **What we could borrow or test:** use the CfC *forward form* as the recurrent atom but do **not** train it by BPTT — freeze/hand-set the dynamics (reservoir-style) and let our closed-form namer read it; OR learn only τ with a local rule. The closed-form time-gate is cheap to evaluate on analog and needs no iterative settle.
- **What contradicts or challenges us:** it is the cleanest evidence that the *high-value* part of a continuous-time atom (the learned dynamics) is currently obtained by gradient. If a frozen/reservoir CfC underperforms a trained one badly, our "don't train the recurrence" bet on the temporal loop is in tension.

## Follow-on leads
- Local / gradient-free learning of the time-constant τ (RC tuning without BPTT).
- Liquid-S4 (same group) — the SSM-flavoured liquid atom (own card).
- Neural ODE (Chen 2018, already in north-star `8-atom.md`) — the ODE frame CfC closes.
