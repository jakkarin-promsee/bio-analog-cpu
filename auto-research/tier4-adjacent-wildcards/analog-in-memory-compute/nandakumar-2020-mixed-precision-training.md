# Mixed-Precision Deep Learning Based on Computational Memory
- **Authors / Year / Venue:** S. R. Nandakumar, Manuel Le Gallo, … Abu Sebastian (IBM Zurich, EPFL, ETH) / 2020 / Frontiers in Neuroscience 14:406
- **Link:** https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00406/full (arXiv mirror: https://arxiv.org/abs/2001.11773)
- **Tier / Topic:** tier4 / t4.1 analog in-memory compute for learning
- **Relevance:** ⭐⭐⭐⭐ — the *other* canonical answer to broken analog updates: keep precision where precision is cheap (digital accumulator), spend the crossbar only on MVMs — the hardware cousin of our 80/20 split, with a measured 172× energy win.

## TL;DR
Instead of fixing the analog update (Tiki-Taka's road), sidestep it: PCM crossbars do all forward/backward MVMs; weight updates are accumulated in a high-precision **digital** variable χ per weight; only when |χ| crosses the device's average single-pulse granularity ε does the system fire ⌊χ/ε⌋ blind programming pulses into the array. Hardware MLP training on MNIST reaches 97.73% (0.57% below FP64 baseline); system analysis gives 172× energy over a 32-bit digital implementation.

## The mechanism (how it actually works)
The design accepts the PCM update as-is — stochastic, nonlinear, asymmetric — and *never asks it to be accurate*. The digital accumulator χ carries the true small-magnitude gradient information that analog devices can't resolve; the array only receives updates already quantized to what one device pulse actually does (ε = mean conductance change per pulse). Programming is blind (no read-verify), keeping the write path cheap; the stochasticity of each pulse becomes zero-mean noise around the intended step rather than a systematic bias, because the accumulator meters out pulses against the measured mean. The trade: gradient computation/accumulation costs digital energy and traffic — exactly what Rasch 2024 measures as 50–175× runtime disadvantage vs in-array accumulation. Mixed-precision buys robustness with the digital budget; TT buys speed with analog cleverness.

## Key results / claims
- MNIST MLP, real PCM arrays in the loop: 97.73% test accuracy (−0.57% vs FP64 software).
- Validated in simulation on CNNs, LSTMs, GANs.
- System-level: 172× energy improvement vs dedicated 32-bit digital design (83.2 nJ/image vs 14.35 µJ/image).

## How it relates to us
- **Organ / phase touched:** the two-brain economy (P8); the namer's digital-side statistics; the P8.7 2×2 substrate ablation.
- **Same as us:** the architecture philosophy is our founding formula in device form — *pay for precision only where it's structurally required, keep the bulk analog and cheap*. Their digital-χ-plus-analog-crossbar split maps onto our closed-form namer (precise, small, occasional) + SCFF bulk (analog, resident, every step). Their 172× is field-consistent context for our 15.4× total / 5.4× substrate factor — ours reads *conservative*, not inflated.
- **Different from us:** their digital side carries the entire learning rule (backprop still computed digitally); our precise side is a closed-form fit, not a gradient pipeline — our 20% is strictly smaller in kind.
- **What we could borrow or test:** the ε-thresholded transfer is a ready-made discipline for Scap-to-LUT consolidation at sleep: accumulate prototype/statistic changes digitally, write to analog stores only in units the store can actually resolve. Also the *blind-pulse + metered-mean* write style as the cheap way to program the analog LUT.
- **What contradicts or challenges us:** it quantifies the cost of NOT solving on-array update — the digital accumulator's energy/traffic is precisely the line item our meter never charges for Scap updates. If SCFF's rule turned out to need χ-style precision under real update noise, part of our 5.4× substrate factor would leak back into digital overhead. The realism pass should measure SCFF's tolerance to ε-granularity (how few effective states before clustering degrades).

## Follow-on leads
- Le Gallo et al. 2018 "Mixed-precision in-memory computing" (Nature Electronics) — the concept paper for the architecture.
- "Fast offset corrected in-memory training" (arXiv 2303.04721) — hybrid of this and the TT line.
- Applying ε-metered blind writes to memristive LUT/prototype stores (hippocampus organ).
