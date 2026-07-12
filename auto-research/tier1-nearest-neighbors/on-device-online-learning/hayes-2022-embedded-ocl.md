# Online Continual Learning for Embedded Devices
- **Authors / Year / Venue:** Tyler L. Hayes, Christopher Kanan / 2022 / CoLLAs 2022
- **Link:** https://arxiv.org/abs/2203.10681
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the published engineering criteria for on-device online CL, with our exact head family (SLDA, NCM) benchmarked under embedded constraints.

## TL;DR
Defines what an online continual learner must satisfy to run on embedded systems (real-time updates, bounded memory/compute, no task boundaries, out-of-domain robustness), then benchmarks seven lightweight streaming methods — Fine-Tune, **NCM**, SOvR, **SLDA**, streaming Naive Bayes, online Perceptron, **Replay** — on embedded-class CNN backbones. NCM wins the efficacy-per-cost trade-off; SLDA is more accurate but costs more.

## The mechanism (how it actually works)
The paper is a *systems requirement spec plus bake-off*, not a new algorithm. The criteria: the learner updates from each example (or tiny batch) in one pass, in real time, with memory and compute that do not grow with the stream, without task labels, and it should generalize to out-of-domain inputs. All seven candidates share one architecture shape — a frozen (or slowly adapted) feature extractor with a cheap streaming head on top — because that is the only shape that fits the budget. The heads are the closed-form/streaming family: class means (NCM), running LDA statistics (SLDA), per-class one-vs-rest counters (SOvR), Gaussian Naive Bayes running moments, a perceptron, and a small replay buffer with gradient steps. Evaluation measures accuracy alongside parameters, memory, and update runtime on mobile-class backbones (MobileNet-v3, EfficientNet, ResNet-18).

## Key results / claims
- **NCM strikes the best trade-off** between classification efficacy and efficiency (only class-mean storage/updates).
- **SLDA is stronger on accuracy but pays more** memory/compute (the covariance).
- Replay (20/class) is competitive but the buffer dominates memory.
- No physical MCU/Jetson deployment — costs are measured in params/runtime on embedded-class architectures.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer (P7 bake-off; the deployed SLDA head) and the P8 cost meter.
- **Same as us:** this is our P7/P8.4 story published two years earlier at the *digital* level — a bake-off of gradient-free streaming heads on a frozen feature map, judged jointly on accuracy AND cost, landing on the NCM/SLDA family. It independently validates the namer family choice from a pure engineering angle (no biology anywhere in the paper).
- **Different from us:** their extractor is frozen and pre-trained — no drift, no gate, no sleep, no consolidation; costs are architectural (params, seconds) not a substrate energy meter; and they never test the heads under representation drift, which is our whole P8–P9 problem.
- **What we could borrow or test:** their **out-of-domain generalization** criterion — we test noise channels but not OOD-input behavior of the namer as its own gate-relevant signal; also NCM-vs-SLDA as an even-cheaper deployed head where anisotropy is mild (our P7 found the tied covariance carries real weight, but a per-arena NCM fallback is untested by us as a *cost* rung).
- **What contradicts or challenges us:** their cost ranking (NCM < SLDA) suggests our 69× SLDA-vs-RanPAC win has one more rung below it that we never metered on the analog table.

## Follow-on leads
- Hayes & Kanan 2020 — Deep SLDA (already carded, t1.2).
- REMIND (Hayes et al. 2020) — latent compressed rehearsal, feeds SIESTA.
- The CoLLAs venue generally — the budget-honest CL community.
