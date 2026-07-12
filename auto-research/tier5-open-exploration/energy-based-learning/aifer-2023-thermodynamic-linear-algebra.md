# Thermodynamic Linear Algebra
- **Authors / Year / Venue:** Maxwell Aifer, Kaelan Donatella, Max Hunter Gordon, Samuel Duffield, Thomas Ahle, Daniel Simpson, Gavin E. Crooks, Patrick J. Coles / 2023 / arXiv:2308.05660 (cond-mat.stat-mech) — Normal Computing
- **Link:** https://arxiv.org/abs/2308.05660 (fetched)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning — thermodynamic computing)
- **Relevance:** ⭐⭐⭐⭐⭐ — the one that hits our namer directly: **solving linear systems / matrix inverse by letting coupled oscillators relax to thermal equilibrium.** Our closed-form namer *is* a linear solve (ridge/Gram); this says physics can do that solve by settling.

## TL;DR
Classic linear-algebra primitives — **solving `Ax = b`, inverting a matrix, computing a determinant, solving Lyapunov equations** — can be obtained by building a system of **coupled harmonic oscillators** whose equilibrium (Gibbs) distribution encodes the answer, then simply **sampling its thermal fluctuations**. The equilibrium mean gives the linear-system solution; the equilibrium covariance gives the matrix inverse. Rigorous asymptotic speedups over digital methods that scale **linearly in matrix dimension**.

## The mechanism (how it actually works)
Encode a symmetric positive-definite matrix `A` as the **potential (stiffness) matrix** of a network of oscillators: potential energy `E(x) = ½ xᵀA x − bᵀx`. Under Langevin dynamics at temperature `T`, the system relaxes to the Gibbs distribution `∝ e^{-E/T}`, a multivariate Gaussian with:
- **mean** `⟨x⟩ = A⁻¹b` → read the average voltage/position and you have **solved the linear system**;
- **covariance** `⟨xxᵀ⟩ − ⟨x⟩⟨x⟩ᵀ ∝ A⁻¹` → read the fluctuation covariance and you have the **matrix inverse**.

No Gaussian elimination, no `O(d³)` factorization — the oscillators *find* `A⁻¹b` by equilibrating, and you estimate the answer by time-averaging measurements. Determinants follow from free-energy/entropy relations of the same system. The paper proves the estimation-time scaling gives an asymptotic advantage growing **linearly in `d`** versus digital `O(d³)` factorizations for the targeted regime.

## Key results / claims
Thermodynamic algorithms for linear systems, matrix inverse, determinant, and Lyapunov equations, each reduced to "build this quadratic energy, equilibrate, measure." Rigorous asymptotic speedup scaling linearly in matrix dimension; positioned as a **near-term classical** alternative to quantum linear-algebra (HHL) without the coherence requirements.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the closed-form namer (SLDA / RanPAC ridge solve); sleep consolidation (a re-fit = a linear solve); the substrate-efficiency thesis.
- This is **our namer's math done by physics.** SLDA/RanPAC compute a running Gram matrix and invert it (ridge). Aifer says: encode that Gram as oscillator stiffness, let it settle, read the covariance = the inverse. The "closed-form solve without gradient descent" we chose *algorithmically* has a **thermodynamic-hardware realization** — the sleep-time re-fit could, in principle, be a physical equilibration on the analog substrate, not a digital solve.
- The `E(x)=½xᵀA x − bᵀx` → `⟨x⟩=A⁻¹b` map is the **cleanest bridge** between "descend an energy" (learning frame) and "solve linear algebra" (our namer): a ridge solution is the minimum of a quadratic energy, and a quadratic energy is exactly what an analog RLC/oscillator network settles into. Our namer and our settling loop are the *same* physical operation at different scales.
- Bank this as the **strongest "we haven't tried this"**: realize the closed-form re-fit as a physical settle (covariance-read inverse), not a numpy `solve`.

## Follow-on leads
The SPU chip that built it (Melanson 2025); thermodynamic algorithms for *training* (thermodynamic gradient descent / natural gradient by Normal Computing); the quadratic-energy ↔ ridge-regression identity as the design equation for an analog namer.
