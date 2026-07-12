# IMSSA: Deploying Modern State-Space Models on Memristive In-Memory Compute Hardware

- **Authors / Year / Venue:** S. Siegel, M.-J. Yang, J.-P. Strachan / 2024 / IEEE ISCAS 2025 (arXiv:2412.20215)
- **Link:** https://arxiv.org/abs/2412.20215
- **Tier / Topic:** tier4 / t4.4 state-space & liquid atoms
- **Relevance:** ⭐⭐⭐⭐ — the first S4 kernel on a memristor crossbar; the quantization-aware training recipe for putting an SSM onto analog in-memory hardware.

## TL;DR
IMSSA maps an **S4D** (diagonal S4) recurrent kernel onto a **memristive crossbar array**, combining the state recurrence with the input/output matvecs in-memory. It extends quantization-aware training to analog CIM and pushes weights all the way to **ternary** for a simple real-world task — claimed as the first implementation of S4 kernels on in-memory compute hardware.

## The mechanism (how it actually works)
A diagonal SSM's per-channel recurrence `x_t = a·x_{t-1} + b·u_t` and readout `y = c·x_t` are all matvecs against fixed coefficients — exactly what a crossbar computes in one settle. IMSSA programs the diagonal `A` (decay), `B`, and `C` into memristor conductances so the whole S4D kernel runs in the array, state feedback included, rather than shuttling to a digital core. Because analog devices have limited precision and drift, they retrain the SSM with **quantization-aware training tailored to the analog hardware** — modeling the crossbar's quantization/noise during training so the deployed low-bit (down to ternary) weights still work. The result trades some accuracy for a large cut in model size and compute on edge hardware.

## Key results / claims
- First S4 kernel demonstrated on in-memory compute hardware (memristive crossbar).
- Ternary weights achieved for a simple real-world task via analog-tailored quantization-aware training.
- Significant reduction in model size and computational demand vs digital deployment.
- (Exact crossbar dimensions / energy / accuracy not given in the abstract.)

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the analog substrate; the analog-realism (PVT / quantization) pass; the north-star recurrent atom's hardware feasibility.
- **Same as us:** confirms the diagonal-SSM recurrence lands on the *exact* hardware we model — a crossbar of resident, compute-in-memory weights, state feedback and all. It's the engineering-native proof that "SSM = charge integration in a crossbar" is buildable, not just an analogy.
- **Different from us:** IMSSA deploys a **pre-trained, then quantized** SSM (backprop off-chip). No on-chip learning. And its emphasis is quantization robustness, not a learning rule — orthogonal to our whole project except as substrate evidence.
- **What we could borrow or test:** two things. (1) The **quantization-aware-training-for-analog** methodology is exactly the recipe our deferred analog-realism pass needs when we move any organ from ideal-numpy to device-realistic. (2) It validates picking **S4D (diagonal, real-coefficient)** as our recurrent atom — the version that programs cleanly into a crossbar. Pair it with our closed-form namer for the learned part.
- **What contradicts or challenges us:** ternary weights and analog noise cost accuracy; our ideal-first sims will overstate the atom's performance until we run the same quantization/PVT gauntlet — a concrete honesty debt for when the recurrent loop is built.

## Follow-on leads
- CIM-SSM (Zhang/Lu 2025, own card) — the sibling that uses device *decay* to realize `A` natively (even less to program).
- HPD / QS4D (robustness + quantization-aware training for SSMs on CIM) — the deeper analog-realism reading.
- Strachan-group analog-CAM / crossbar work — overlaps the `analog-in-memory-compute` folder.
