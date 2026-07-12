# Synthesis — Energy-based learning as the unifying frame (+ the thermodynamic floor)  (Tier 5)

**The question:** Is "inference = roll downhill on an energy landscape, learning = carve the valleys" the single principle under SCFF-goodness, Hopfield, EqProp, predictive coding, the halt-signal, and stability — and what is the thermodynamic floor (Landauer, thermodynamic computing) beneath all of it?

**Already in `draft6.0/research/`:** the north-star capstone `north-star/21-energy.md` already states the unifying picture (LeCun's frame; SCFF-goodness = negative energy; Hopfield/EqProp/predictive-coding/attractor-cleanup as energy descent; Landauer's `kT·ln2` as the floor). Tier-4 `equilibrium-physics-learning/` already covers the *learning-rule* physics (EqProp, coupled learning, Ising-EqProp, memristor activity-difference). **This tier extends past both** into (a) the *modern* EBM literature (Hopfield revival, Energy Transformer, diffusion-as-score/EBM), (b) the *training* menu (Song & Kingma), and (c) the **thermodynamic-computing hardware** line (Landauer → Coles → Aifer → Melanson) that our north-star file names but does not source.

## The landscape (the unifying picture)

**One equation runs through everything: `E(x) low = good, inference = argmin_x E, learning = reshape E`.** LeCun 2006 is the frame; its deepest point is that you never need the partition function `Z` — only *relative* energies — which is precisely why a physical, non-probabilistic substrate fits (it rolls downhill; it does not integrate). The **collapse problem** (a loss that only pulls the answer down flattens the whole surface) is why every energy learner needs a *push-up*, and the taxonomy of push-ups **is** the taxonomy of methods: contrastive/NCE (our InfoNCE branch), score matching, max-likelihood-by-Langevin.

The modern era made the unification *architectural*, not just conceptual. **Modern Hopfield networks (Ramsauer 2020)** proved transformer attention is literally one step of energy descent to the nearest stored pattern — memory, attention, and energy-minimization are one object, tuned by a temperature `β`. **Energy Transformer (Hoover 2023)** turned that into a working block whose forward pass *is* gradient descent on a single global energy, with depth = number of settle-steps. **Score-based / diffusion (Song & Ermon 2019)** showed generation = annealed Langevin descent of a learned energy (`score = −∇E`), and **predictive coding (Millidge 2020)** showed local energy-minimizing dynamics recover *exact backprop gradients* — so even backprop is "read the gradient of a settled energy." Six different fields, one descent.

Beneath the *learning* energy sits the *thermodynamic* one. **Landauer 1961**: the unavoidable cost of computing is **erasing** information (`k_B T ln2` per bit), not computing it — reversible operations are free in principle; only destroying information must dissipate. Then a 2023–2025 hardware wave flips noise from enemy to resource: **Coles 2023** (thermodynamic AI: program an energy, relax to `e^{-E}`, harvest fluctuations — unifying diffusion/MCMC/Bayesian/annealing), **Aifer 2023** (linear algebra by equilibration: `E=½xᵀAx−bᵀx` → `⟨x⟩=A⁻¹b`, covariance `=A⁻¹`), and **Melanson 2025** (a *built* 8-cell RLC "stochastic processing unit" doing matrix inversion and Gaussian sampling by settling to thermal equilibrium).

## How WE fit this landscape

We are an **energy-shaping machine on both meanings of energy at once**, and that is the honest, non-trivial placement:
- **The learning energy:** SCFF goodness is a (negative) energy; the settling loop descends one; the correctness-feeling is that energy hitting its floor; noise-cleanup is rolling back into a valley. Our Phase-2→3 pivot (drop `Σh²`, adopt InfoNCE) is exactly LeCun's collapse lesson — a density-only push-up collapses, a contrastive push-up does not.
- **The thermodynamic energy:** our resident-weight, compute-in-memory, **settle-don't-erase** substrate is designed to stay on the *reversible* side of Landauer — it descends and persists instead of erasing and shuttling, which is *why* the efficiency thesis is physics and not a slogan.
- **The bridge that is genuinely new to us:** Aifer/Melanson make **our closed-form namer and our settling loop the same physical operation** — a ridge solve is the minimum of a quadratic energy, and a quadratic energy is what an analog oscillator network settles into. The "no gradient descent, closed-form solve" we picked *algorithmically* has a *thermodynamic-hardware* realization.

What is **not** ours / a re-invention to stay humble about: the energy frame itself is 20 years old and industrial teams (Normal Computing) are building the "noise-as-resource, relax-to-equilibrium" substrate we describe philosophically. We are on the *learning/representation* side of a paradigm whose *sampling/linear-algebra* side is already in silicon.

## The gap / what we haven't tried (the carry-back)

1. **Realize the closed-form namer re-fit as a physical settle, not a digital solve.** Aifer 2023 + Melanson 2025 give the exact map: encode the namer's Gram/precision matrix as oscillator stiffness, equilibrate, read the covariance = the inverse. This is the single most concrete "our math is analog-native" lever — a target for the deferred analog-realism pass.
2. **Frame the north-star think-loop as an Energy Transformer block** (Hoover 2023): a unit whose computation is *iterate descent on a designed energy until it settles*, depth = settle-steps on resident weights, and the energy value itself = the halt/confidence feeling. This is the published shape of our loop; the open problem is learning the energy without a backward pass (EqProp, tier4).
3. **Modern-Hopfield `β`-regime read for the LUT** (Ramsauer 2020): one physical retrieval gives sharp single-memory *or* soft category-averaging just by tuning a temperature — a design gift for the hippocampus organ.
4. **Score-matching as a negatives-free objective** (Song & Kingma): a future organ could learn an energy with *no* LUT partner, at the cost of needing `∇_x` of the network.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [LeCun et al. 2006 — Tutorial on Energy-Based Learning](lecun-2006-energy-based-learning-tutorial.md) | ⭐⭐⭐⭐⭐ | The frame + the collapse problem = our `Σh²`→InfoNCE story; no partition function = why analog fits. |
| [Song & Kingma 2021 — How to Train Your EBMs](song-kingma-2021-how-to-train-ebms.md) | ⭐⭐⭐⭐ | The training menu (MCMC/score/NCE); places our InfoNCE in the NCE branch and Langevin = our settle loop. |
| [Millidge et al. 2020 — Predictive Coding ≈ Backprop](millidge-2020-predictive-coding-approximates-backprop.md) | ⭐⭐⭐⭐ | Local energy descent recovers exact backprop → the rival "direction for free by settling"; sets the bar our frozen-bulk bet must clear. |
| [Ramsauer et al. 2020 — Hopfield is All You Need](ramsauer-2020-hopfield-networks-all-you-need.md) | ⭐⭐⭐⭐ | Attention = one-step energy descent to a stored pattern; `β`-regime knob for LUT recall. |
| [Hoover et al. 2023 — Energy Transformer](hoover-2023-energy-transformer.md) | ⭐⭐⭐⭐ | The north-star think-block, published: forward pass = descend an energy, depth = settle-steps, `E` = the halt feeling. |
| [Song & Ermon 2019 — Score-based generative](song-ermon-2019-score-based-generative.md) | ⭐⭐⭐ | Annealed Langevin = our settle-with-cooling-noise math; multi-scale-noise schedule for a robust settle. |
| [Landauer 1961 — Irreversibility & Heat](landauer-1961-irreversibility-heat-generation.md) | ⭐⭐⭐⭐⭐ | `kT·ln2`: the cost is *erasing*, not computing → the physics under settle-don't-erase / resident weights. |
| [Coles et al. 2023 — Thermodynamic AI](coles-2023-thermodynamic-ai-fluctuation-frontier.md) | ⭐⭐⭐⭐ | Noise-as-resource, program-an-energy-relax-to-`e^{-E}`: our substrate philosophy as an industrial hardware thesis. |
| [Aifer et al. 2023 — Thermodynamic Linear Algebra](aifer-2023-thermodynamic-linear-algebra.md) | ⭐⭐⭐⭐⭐ | `E=½xᵀAx−bᵀx` → `⟨x⟩=A⁻¹b`: our namer's ridge solve done by physical settling. |
| [Melanson et al. 2025 — Thermodynamic computing system](melanson-2025-thermodynamic-computing-system.md) | ⭐⭐⭐⭐⭐ | A *built* RLC chip inverting matrices by equilibration — hardware proof our closed-form namer is analog-native. |

## Leads spawned
- **Thermodynamic *training* primitives** (thermodynamic gradient descent / natural gradient, Normal Computing) — could a whole learning step be a physical settle? → tier4/tier5 backlog.
- **Dense Associative Memory / higher-order Hopfield energies** (Krotov) — capacity vs the LUT.
- **Experimental Landauer verification** (Bérut et al. 2012) + reversible computing (Bennett) — the measured floor.
- **Quadratic-energy ↔ ridge-regression identity** as the design equation for an analog namer (analog-realism pass).
- **"Should EBMs model the energy or the score?"** — parameterization choice for any future generative organ.
