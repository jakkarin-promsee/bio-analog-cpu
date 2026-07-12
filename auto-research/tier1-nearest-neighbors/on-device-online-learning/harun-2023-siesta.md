# SIESTA: Efficient Online Continual Learning with Sleep
- **Authors / Year / Venue:** Md Yousuf Harun, Jhair Gallardo, Tyler L. Hayes, Ronald Kemker, Christopher Kanan / 2023 / TMLR
- **Link:** https://arxiv.org/abs/2303.10725 (code: https://github.com/yousuf907/SIESTA)
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the single nearest published neighbor: a wake/sleep economy with a backprop-free wake phase and compute-restricted sleep consolidation.

## TL;DR
SIESTA splits continual learning into a **wake** phase — cheap, rehearsal-free, **backpropagation-free** online updates so the model is never stale — and a **sleep** phase — compute-restricted offline rehearsal from a compressed latent buffer. It learns ImageNet-1K continually in under 2 hours on one GPU and, augmentation-free, matches the offline learner.

## The mechanism (how it actually works)
The backbone is trained once and then largely frozen. While **awake**, incoming samples are pushed through the frozen lower network; the compressed latent codes (product-quantization, inherited from their REMIND line) are stored in a bounded buffer, and only the output layer is updated with a closed-form-style, data-driven rule (running class statistics — no gradient, no rehearsal). So the model answers correctly *right now* at near-zero learning cost. Periodically the system **sleeps**: the upper network is retrained with supervised backprop rehearsal over the compressed buffer, under an explicit compute cap (a restricted rehearsal policy chooses what to replay). Sleep is *scheduled* (the paper's framing: run it when the device is idle/charging), not triggered by any drift signal. The wake/sleep split is exactly an 80/20 economy: the expensive directional learning is batched into rare consolidation events; the cheap always-on path keeps the system live between them.

## Key results / claims
- Continual ImageNet-1K in **< 2 GPU-hours** — orders of magnitude cheaper than rehearsal-heavy online CL.
- In the augmentation-free setting it **matches the offline (joint) learner** — a "no forgetting left" claim at the benchmark scale.
- Wake updates are rehearsal-free and backprop-free; sleep is the only place gradients run.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole P8–P9 economy (gate + sleep + closed-form namer); the hippocampus LUT.
- **Same as us:** the architecture *shape* is ours — cheap gradient-free awake path + rare consolidation "sleep" over a compressed latent memory; even the motivation (energy) matches. Their compressed-latent buffer plays our LUT's role.
- **Different from us:** (1) their backbone is **frozen** — the representation never drifts, so they have no drift problem and no gate; our SCFF bulk keeps learning unsupervised forever, and the namer must *track* the self-generated drift. (2) Their sleep is **backprop rehearsal**; ours is a closed-form re-fit (no gradient anywhere in the deployed loop). (3) Sleep is **time-scheduled** (idle/charging), not drift-gated; they never observe our P8.6 inversion (firing more forgets more). (4) Cost is measured in GPU-hours, not a substrate energy account.
- **What we could borrow or test:** their compute-restricted rehearsal policy (choose *what* to consolidate under a sleep budget) maps directly onto our LUT→sleep re-fit — we currently consolidate the full history (P8.3 said truncation hurts, but a *policy* is not truncation); also product-quantized latent storage as a LUT compression lever.
- **What contradicts or challenges us:** SIESTA proves the wake/sleep economy is *not* substrate-dependent — a plain GPU gets the efficiency win. Our claim must therefore rest on the analog meter + the drift-gated safety result, not on the wake/sleep composition itself.

## Follow-on leads
- REMIND (Hayes et al. 2020) — the compressed-latent-rehearsal ancestor.
- GRASP (Harun et al. 2023, arXiv:2308.13646) — the rehearsal *policy* under a sleep budget.
- "A Good Start Matters" (2025, arXiv:2503.06385) — data-driven weight init for CL, same group.
