# FSC-Net: Fast-Slow Consolidation Networks for Continual Learning
- **Authors / Year / Venue:** Mohamed El Gorrim / 2025 / arXiv preprint (cs.LG, submitted Nov 2025) — ⚠ preprint, single-author, not yet peer-reviewed
- **Link:** https://arxiv.org/abs/2511.11707 (fetched)
- **Tier / Topic:** tier1 / t1.4 complementary dual-memory
- **Relevance:** ⭐⭐⭐⭐ — a 2025 minimalist ablation of the whole dual-memory idea that lands on two conclusions that *directly support our design*: it's the **timescale separation, not architectural complexity**, that beats forgetting, and **pure replay beats replay+distillation** at consolidation (distillation injects recency bias). External, recent validation of "replay-refit a simple head" over fancier consolidation.

## TL;DR
FSC-Net is a deliberately plain two-network dual-timescale system: a **fast net (NN1)** adapts to each new task immediately, and a **slow net (NN2)** consolidates by replaying buffered data (and optionally distilling from the fast net). The paper's finding is the interesting part: (a) a **simple MLP consolidator beats a fancier similarity-gated variant** by ~1.2pp, and (b) **pure replay without distillation consolidates better** — distillation from the fast net introduces recency bias. Retention: 91.71% on Split-MNIST, 33.31% on Split-CIFAR-10 (modest, and the author says so).

## The mechanism (how it actually works)
Two networks at two timescales:
- **Fast net (NN1):** trained on the current task stream, rapid adaptation, high plasticity — inevitably forgets.
- **Slow net (NN2):** periodically **consolidates** by training on a replay buffer of past experience. Two consolidation recipes are compared: **replay only** (fit NN2 on buffered samples) vs **replay + distillation** (also match NN1's outputs).

The controlled experiment is the contribution: the author strips the design down and asks *what actually matters.* Answer — the **dual-timescale consolidation itself** carries the anti-forgetting effect; adding architectural sophistication (a similarity-gated consolidator) or a distillation term does **not** help and can hurt (distillation biases NN2 toward the fast net's most-recent state). The honest headline: modest absolute numbers, but a clean isolation of the mechanism.

## Key results / claims
- **Split-MNIST:** 91.71% ±0.62 retention (+4.27pp over the fast network alone).
- **Split-CIFAR-10:** 33.31% ±0.38 retention (+8.20pp over fast-alone; author flags absolute performance as modest).
- **Pure replay > replay+distillation** during consolidation (distillation = recency bias).
- **Timescale, not architecture:** a simple MLP consolidator beats a similarity-gated one by 1.2pp — the dual-timescale split is the load-bearing idea.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** sleep consolidation · the fast/slow split · the "why closed-form re-fit over replay is enough" question.
- **Same as us:** dead-on our shape — **fast adaptation + periodic slow consolidation over a replay buffer.** And its two findings are gifts to our thesis: (1) "**timescale separation, not architectural complexity**" is precisely why our minimal closed-form namer + periodic sleep can match heavier methods; (2) "**pure replay beats distillation**" validates our sleep being a **direct re-fit over the LUT** rather than a distillation objective — we never distill, we re-solve, and this paper says the distillation term we skipped was a *liability*, not a missing feature.
- **Different from us:** FSC-Net's slow net is still an **SGD-trained network**; our slow consolidation is a **closed-form analytic solve** (SLDA/RanPAC) — an even stronger version of "no architectural complexity." Their fast net is a trained classifier that forgets; our fast store is a **non-parametric LUT** that doesn't classify and doesn't forget by construction. And our slow *representation* (the SCFF cortex) is frozen and unsupervised, whereas theirs consolidates the *whole* classifier.
- **What we could borrow or test:** not a new mechanism so much as a **framing + a control we should run.** FSC-Net is the template for an ablation we can cite: "does distillation-at-sleep beat re-fit-at-sleep?" — they say no, which lets us *not* build it. If we ever want a peer comparator for our P10 race, FSC-Net's replay-only consolidator is a clean, weak-but-honest dual-net baseline. Also: their MLP-beats-gated result is a caution against over-engineering the consolidator — reinforces keeping the namer minimal.
- **What contradicts or challenges us:** nothing contradicts; it *supports*. The one caution is that the **absolute numbers are modest** (33% on CIFAR-10), so it's a mechanism-isolation paper, not a SOTA claim — cite it for the *direction* (timescale + pure-replay), not as a strong performance anchor. ⚠ Single-author preprint, unreviewed — treat as suggestive, corroborate against CLS-ER/ESMER before leaning on it.

## Follow-on leads
- The distillation-replay methods it argues against: DER/DER++ (Buzzega 2020), LUCIR (Hou 2019) — the recency-bias failure mode it names.
- Two-timescale / fast-weight theory (Ba 2016; already in north-star/1-memory) — the principled account of *why* timescale separation works.
- Our own P9.2 all-tap-vs-truncated result — the internal analog of "consolidator complexity vs benefit."
