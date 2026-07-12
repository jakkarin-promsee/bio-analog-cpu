# Latent Replay for Real-Time Continual Learning
- **Authors / Year / Venue:** Lorenzo Pellegrini, Gabriele Graffieti, Vincenzo Lomonaco, Davide Maltoni / 2019–2020 / arXiv (deployed IROS/CVPR-workshop line; the CORe50 group)
- **Link:** https://arxiv.org/abs/1912.01100
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the anchor of the store-representations-not-inputs lineage that our hippocampus LUT belongs to; first real-time CL on a phone.

## TL;DR
Instead of replaying stored *images*, store activation volumes at an intermediate ("latent replay") layer and rehearse from there: layers below the replay point learn at near-zero rate (kept stable), layers above learn at full pace. State-of-the-art on CORe50 NICv2 (~400 non-i.i.d. batches) and runs near-real-time continual learning on a smartphone.

## The mechanism (how it actually works)
The network is split at a chosen depth. Old knowledge lives as a buffer of latent activations sampled at that depth (much smaller than images — a 500-pattern buffer under 2 MB at the penultimate layer). On each new experience, fresh data flows through the whole net while the buffer contents are injected *at the replay layer* and mixed into the upper layers' minibatches — so the expensive lower stack runs forward-only on new data, and gradients only flow through the cheap upper stack. The catch they name honestly: if the lower layers move, the stored activations go stale ("aging"), so the lower layers are nearly frozen — stability is bought by giving up lower-layer plasticity.

## Key results / claims
- SOTA on CORe50 NICv2-391 among methods without task boundaries; also validated on OpenLORIS.
- Replay buffer of latent activations ≈ 4× or more cheaper than raw-image replay at matched pattern count.
- Deployed as a **smartphone app** doing continual learning at near real time — the first credible on-device CL demo.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the hippocampus LUT + sleep (P8.3 full-history consolidation); the read-only envelope (GD reads taps, never writes SCFF).
- **Same as us:** the core move is ours — keep the past as *mid-network representations*, keep the expensive lower stack out of the gradient path, learn only above the tap. Their "slow down the layers below the replay point" is our envelope taken to the limit (we freeze the namer out of the bulk entirely).
- **Different from us:** their latent buffer stores raw activation *samples* and rehearses them with backprop; our LUT stores *prototypes + running Gram* and consolidates closed-form. Their staleness problem ("aging" of stored activations when lower layers move) is exactly our P8/P9 drift problem — but they *suppress* it by freezing, while we *track* it with the gate + sleep re-anchoring (P9.4 proto-reanchor). No energy account; no drift trigger.
- **What we could borrow or test:** their staleness framing gives us a clean ablation — how fast do stored LUT prototypes age per unit of measured bulk drift? (We have bulk_drift ∈ [0.63,1.00] from P8.0; the aging curve vs drift is uncharted.)
- **What contradicts or challenges us:** their result implies most of the continual win is available with a *frozen* lower stack — the burden is on us to show the always-plastic SCFF bulk earns its drift cost (P11's Δbulk decomposition is our current answer).

## Follow-on leads
- REMIND (Hayes et al. 2020) — quantized latent replay at scale.
- Ravaglia et al. 2021 — this method pushed onto an MCU (carded here).
- Chameleon (DATE 2023 / TCAD 2024) — dual short/long-term latent buffers mapped onto on-chip/off-chip memory.
