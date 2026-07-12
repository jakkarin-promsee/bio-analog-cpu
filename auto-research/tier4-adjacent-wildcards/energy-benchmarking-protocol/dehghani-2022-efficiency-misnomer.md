# The Efficiency Misnomer
- **Authors / Year / Venue:** Mostafa Dehghani, Anurag Arnab, Lucas Beyer, Ashish Vaswani, Yi Tay / 2021 (arXiv) → ICLR 2022
- **Link:** https://arxiv.org/abs/2110.12894 (fetched)
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐⭐ — the paper that says our whole worry is real: pick the wrong single cost indicator and you draw the wrong efficiency conclusion; the direct license for a multi-indicator, matched-accuracy report.

## TL;DR
Researchers report *one* cost indicator (FLOPs, or parameter count, or throughput) and silently assume the others track it. They do not — and can actively contradict each other. A model can win on parameters and lose on FLOPs, or win on FLOPs and lose on wall-clock/energy. Incomplete cost reporting produces partial, sometimes reversed, conclusions.

## The mechanism (how it actually works)
The argument is an anatomy of why the three common cost proxies decouple:
- **Parameter count** ignores how many times each parameter is *used*. Weight-shared / recurrent models have few parameters but high compute; sparse models have huge parameter counts but dense-model FLOPs. So "small model" ≠ "cheap model."
- **FLOPs** count multiply-adds but are blind to memory access, parallelism, and operational intensity — two nets at equal FLOPs can differ several-fold in measured latency/energy because one is memory-bound and the other compute-bound (the memory wall, priced elsewhere in this folder).
- **Throughput / speed** is hardware-, batch-, and implementation-specific; it moves with the accelerator, not just the algorithm.
Because each proxy captures a different axis, a paper that reports only its favourable one can claim an "efficiency" win that vanishes under a different, equally valid, indicator. The fix is to report *several* indicators and to compare models **at a matched quality/accuracy point**, so the efficiency axis is isolated from the accuracy axis.

## Key results / claims
- Demonstrates concrete pairs of models where the ranking *flips* depending on whether you measure parameters, FLOPs, or speed.
- Concludes with reporting guidance: use multiple cost indicators, be explicit about the hardware/measurement context, and beware conclusions drawn from any single proxy — especially parameter count in NLP and FLOPs in vision.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole P8/P10/P11 energy claim; the P10.0 pre-registered "OURS uses *more* FLOPs/sample than ER (96 938 vs 65 268)" tension.
- **Same as us:** we already refused a single-proxy claim — our energy story is reported as *two separated factors* (substrate 5.4× × algorithm 2.9×, P8.7) and honestly split into same-substrate vs analog-floor (P10 R1). This paper is the citation that legitimises that discipline.
- **Different from us:** the paper's indicators are all *digital* proxies (params/FLOPs/latency). Our load-bearing quantity is a **behavioral relative-pJ meter** (ADC-centred, not SPICE) plus an analog-substrate factor — a fourth indicator outside their menu. We must show our meter is a *consistent* indicator, not a favourable-proxy cherry-pick.
- **What we could borrow or test:** report the *same* comparison under ≥3 indicators (FLOPs/sample, relative-pJ, and bytes-moved) side by side; if our ranking vs tuned-ER is stable across all three, the win survives this critique. The honest P10 fact that we *lose* on FLOPs/sample but the chip wins on pJ is exactly the decoupling this paper predicts — cite it to pre-empt "you cherry-picked pJ."
- **What contradicts or challenges us:** a reviewer armed with this paper will say "you report pJ because FLOPs go against you." Our defence must be that pJ is the *decision-relevant* indicator for a chip and that we report FLOPs anyway (we do, P10.0) — transparency, not proxy-shopping.

## Follow-on leads
- Operational-intensity / roofline analysis as a fourth reported axis (→ memory-wall cards, this folder).
- MLPerf-style matched-quality benchmarking as the operational form of "compare at equal accuracy" (Tschand 2024, this folder).
