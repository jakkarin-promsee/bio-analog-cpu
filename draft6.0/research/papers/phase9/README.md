# `phase9/` — the loop that doesn't rot: maintenance, slow coordination, the north-star hand-off

> **Stage-2, the third GD phase — and the close-out.** The readout names, the gate decides when to pay; **this folder is
> how the whole thing survives a lifelong stream.** Three story files: the **maintenance loop** (sleep = replay, only the
> readout is replayed — our validated A6 win, now owing a fair baseline); **slow coordination** (what is *allowed* to
> live between SCFF layers — and *why boosting is dropped*); and the **north-star hand-off** (the gate is the halt, the
> readout's cosine *margin* is the feeling — built on direction so the recurrent brain can reuse them).
>
> Context: feeds [`../../../src/stage2-design.md`](../../../src/stage2-design.md) §3.3 / §3.4 / §3.6 + Phase 9.

---

## The frame

**Maintenance = our home turf.** Phase 4 already showed the win — online rots, a periodic sleep recovers it. The
literature names the machinery: **experience replay** (sleep), **EWC/SI/MAS** (the regularization alternative), **A-GEM**
(gradient-projection replay = the efficient same-budget baseline we *owe* — Phase 4's WIN was vs *naive* online-BP, not a
fair fight), **REMIND** (frozen backbone + compressed *feature* replay into the head = **our sleep/LUT, published**). The
bursty, drift-gated stream makes the buffer **class-imbalanced** → a class-balancing reservoir (CBRS) + logit adjustment.
**Caveat:** "only the readout is replayed; the bulk doesn't forget" assumes the frozen-to-GD bulk doesn't drift — but SCFF
is unsupervised and *still updating*, and representation drift is measured ([2203.13381](https://arxiv.org/abs/2203.13381)).
*Measure the bulk-drift rate; don't assume it's zero* (this also feeds Phase 6 — a drifting bulk is a noise-like perturbation).

**Slow coordination = what's allowed between SCFF layers.** Anything between/under SCFF must be **unsupervised or slow.**
The EMA / momentum-encoder is the device: slow = stable = safe near the base, and it matters most at the **late** layers
(= our drift-slowdown flip, doubly grounded). **Stop-gradient** names the read-only relation; the boosting chain died
because its residual was a **forward** leak that stop-gradient doesn't block. **Lookahead** slow/fast weights = the
fast-online / slow-sleep two-timescale, surviving *inside* the readout.

**North-star hand-off (light touch).** The gate is **PonderNet's ancestor** (static "compute until θ" = recurrent "think
until the feeling settles"); but **ground its signal on direction, not confidence** — confidence/entropy is a magnitude
(why P5 struck the adaptive exit), a **cosine margin** is the spine-clean "feeling" the recurrent brain will reuse. The
missing third leg: **calibration under shift** — even a direction-grounded feeling needs a re-calibration at sleep.

---

## The files

| File | What it covers | The one idea |
| ---- | -------------- | ------------ |
| [maintenance-and-replay.md](maintenance-and-replay.md) | Experience replay, EWC / SI / MAS, A-GEM, generative replay, REMIND, the sleep=consolidation analogy, replay scheduling, class-imbalance, the same-budget BP+replay baseline we owe. | **Sleep is replay; the readout is what's replayed; the bulk (mostly) doesn't forget.** |
| [slow-coordination.md](slow-coordination.md) | EMA / mean-teacher / momentum encoder, stop-gradient, EMA-matters-most-at-late-layers, Lookahead slow/fast. Documents *why* boosting-chain is dropped. | **Between SCFF layers: unsupervised or slow. Nothing fast and supervised.** |
| [north-star-bridges.md](north-star-bridges.md) | PonderNet / ACT (learned halting), TENT (entropy = a magnitude — caution), active inference, calibration-under-shift. | **The gate is the seed of "think until the feeling crosses θ" — but confidence is a magnitude; use the cosine margin.** |

## Papers (the maintenance / coordination / hand-off slice)

| paper | id / venue | the one-line reason it's here |
| --- | --- | --- |
| Experience Replay for Continual Learning (Rolnick) | [1811.11682](https://arxiv.org/abs/1811.11682) | replay as the continual workhorse — our sleep |
| EWC (Kirkpatrick PNAS 2017) | [1612.00796](https://arxiv.org/abs/1612.00796) | protect important weights — the regularization alternative to replay |
| Synaptic Intelligence (Zenke 2017) | [1703.04200](https://arxiv.org/abs/1703.04200) | per-weight importance, online (the BCM-register cousin) |
| A-GEM | [1812.00420](https://arxiv.org/abs/1812.00420) | gradient-projection replay — `race_bp`+buffer = the efficient same-budget baseline |
| REMIND / ACAE-REMIND | [2105.08595](https://arxiv.org/abs/2105.08595) | **our sleep/LUT, published**: frozen backbone + compressed *feature* replay into the head |
| Imbalanced online CL / class-balancing reservoir (Chrysakis & Moens, ICML 2020) | classic | the **bursty drift-gated stream → imbalanced buffer** problem |
| Probing Representation Forgetting | [2203.13381](https://arxiv.org/abs/2203.13381) | SSL representation drift is **real** — don't assume the bulk is frozen-stable (shared with Phase 6) |
| MGSER-SAM | [2405.09492](https://arxiv.org/abs/2405.09492) | replay **+** sharpness-aware — a *hypothesised* bridge to flat minima (shared with Phase 6) |
| Mean Teacher (Tarvainen 2017) · MoCo · BYOL · DINO | classics / [2006.07733](https://arxiv.org/abs/2006.07733) | EMA target = the slow, safe thing allowed near SCFF |
| On the Pros and Cons of the Momentum Encoder | [2208.05744](https://arxiv.org/abs/2208.05744) | EMA matters most at **late** layers = our drift-slowdown flip |
| Lookahead Optimizer | [1907.08610](https://arxiv.org/abs/1907.08610) | slow/fast weights = the fast-readout / slow-sleep two-timescale |
| TENT (test-time entropy minimization) | [2006.10726](https://arxiv.org/abs/2006.10726) | adapt the head online by confidence — but entropy is a *magnitude* (caution) |
| PonderNet (Banino 2021) · ACT (Graves 2016) | [2107.05407](https://arxiv.org/abs/2107.05407) | learned halting = "think until the feeling crosses θ" |
