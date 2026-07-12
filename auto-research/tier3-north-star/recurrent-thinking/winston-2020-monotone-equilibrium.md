# Monotone Operator Equilibrium Networks (monDEQ)
- **Authors / Year / Venue:** Ezra Winston, J. Zico Kolter / 2020 / NeurIPS 2020
- **Link:** https://arxiv.org/abs/2006.08591 (code: https://github.com/locuslab/monotone_op_net)
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐⭐ — the *certificate* that a settling loop actually settles; the math version of "the circuit is dissipative."

## TL;DR
Vanilla DEQs have no guarantee that a fixed point exists or that iteration converges to it — they can oscillate or diverge. monDEQ constrains the network's parameterization so the fixed-point equation is a *monotone operator splitting problem*, which guarantees a **unique equilibrium** and gives solvers with **provable, stable convergence**. Implicit-depth power, with a settle you can trust.

## The mechanism (how it actually works)
A DEQ computes `z* = σ(Wz* + Ux + b)` — the output is the state that stops changing. The failure mode: nothing about a learned `W` prevents the iteration from spiraling instead of settling. monDEQ's move is to never learn `W` directly; instead it learns matrices `A, B` and *builds* `W = (1−m)I − AᵀA + B − Bᵀ`. This construction forces `I − W ⪰ mI` (strong monotonicity, m > 0) **by construction, for every value of the learned parameters** — the operator always "points inward," so a unique fixed point exists and standard operator-splitting iterations (forward-backward, Peaceman–Rachford) converge to it at a known rate. The backward pass is another linear fixed-point solve of the same structured form. Works for structured operators too (multi-scale convolutions), so it is not limited to dense layers.

The engineering translation: convergence is not a property you hope training preserves — it is a property of the *parameter space you allow*. Dissipativity as an architecture constraint, not a diagnostic.

## Key results / claims
- Guaranteed existence + uniqueness of the equilibrium for **all** parameter values; guaranteed stable convergence of the solver (vanilla DEQs offer neither).
- Competitive accuracy with implicit-depth baselines on standard image benchmarks at much lower memory than explicit deep nets (constant memory in depth).
- Spawned a family: Lipschitz-bounded equilibrium networks, certified-robust implicit models — the "constrain the operator, get the guarantee" recipe generalizes.

## How it relates to us
- **Organ / phase touched:** north-star recurrent loop; North-star 20 (dynamics & stability); the analog-realism pass.
- **Same as us:** the core bet is identical to our substrate fact — computation = relaxation to a fixed point. monDEQ is what "the op-amp network settles" looks like as a theorem.
- **Different from us:** it is a digital root-finder solving the equilibrium; our substrate would *physically relax* to it. Their solver cost is our free physics — but their *guarantee* is exactly what our physics needs certified (an analog network with unconstrained learned feedback can latch or oscillate, the circuit version of a diverging DEQ).
- **What we could borrow or test:** (1) impose the monotone/contractive parameterization on the recurrent crossbar — in circuit terms this is a diagonal-dominance / net-negative-feedback constraint on the weight matrix, checkable at write time; (2) v0 of the settling-loop experiment should use a spectral-norm-bounded weight-tied block so the fixed point provably exists before we ask what it computes; (3) their operator-splitting view gives the convergence-*rate* knob (m trades expressivity vs settle speed = our think-time).
- **What contradicts or challenges us:** the constraint costs expressivity — and Geiping 2025 (this folder) shows *useful* trained recurrences learn orbits, not just fixed points. Certified settle may forbid the most interesting dynamics; that tension is the first thing our sims should measure.

## Follow-on leads
- Revay et al., "Lipschitz Bounded Equilibrium Networks" (arXiv 2010.01732) — tighter robustness certificates, same recipe.
- Positive concave DEQ models (arXiv 2402.04029) — alternative guarantee family.
- Implicit differentiation through equilibria — the O(1)-memory training trick, and its EqProp connection (the nudged equilibrium IS an implicit gradient).
