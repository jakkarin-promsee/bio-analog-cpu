# Towards the Systematic Reporting of the Energy and Carbon Footprints of Machine Learning
- **Authors / Year / Venue:** Peter Henderson, Jieru Hu, Joshua Romoff, Emma Brunskill, Dan Jurafsky, Joelle Pineau / 2020 / JMLR 21(248)
- **Link:** https://jmlr.org/papers/v21/20-312.html (fetched) · arXiv:2002.05651
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐ — the measure-don't-estimate standard: the paper that showed the field essentially never reports energy, and built the tooling + checklist to fix it. The bar our energy section must clear to be taken seriously.

## TL;DR
Audits 100 random NeurIPS 2019 papers: **0 reported carbon, ~1% reported energy, 17% reported any compute metric.** Ships `experiment-impact-tracker` — a tool that logs real-time power (CPU/GPU/DRAM), applies PUE and grid carbon intensity, and emits a standardized appendix — plus concrete reporting recommendations.

## The mechanism (how it actually works)
The tool instruments the running job rather than estimating from FLOPs: it samples hardware power draw (RAPL for CPU/DRAM, NVML for GPU), attributes the fraction used by the process, multiplies by wall-clock, scales by data-centre PUE, and converts to CO₂e using region/time grid intensity. The methodological point is that **measured joules ≠ FLOP-derived joules** — utilization, memory traffic, idle/overhead, and cooling all sit between the two, and only measurement captures them. It also argues for reporting the *full* accounting (energy, carbon, compute, hardware, run time) so a number is interpretable and reproducible, and proposes an energy-efficiency leaderboard to make the metric competitive.

## Key results / claims
- The underreporting statistic (0 / 1% / 17%) — the field's baseline of energy blindness.
- A standardized reporting template + a dollar-value "social cost of carbon" translation for interpretability.
- Case studies showing large gaps between naive estimates and measured consumption; recommendations to measure, disclose hardware/region, and separate experimentation cost from the final-model cost.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P8.7 / P10 cost meter's *credibility*; the write-up of any energy claim in the reports.
- **Same as us:** we already report a *full accounting* rather than a bare number — GD-share, bp-ratio, same-substrate vs analog, the 2×2 ablation. That matches this paper's "report the whole picture, not one scalar" demand.
- **Different from us:** our meter is a **relative behavioral pJ model (ADC-centred, NOT SPICE)** — we do *not* measure wall-power on real silicon, because the chip does not exist. That is the honest gap: Henderson measures joules on hardware; we *model* relative joules. We must state this boundary loudly (we do: "behavioral meter"), and frame our numbers as *ratios under a stated model*, never as measured absolute joules.
- **What we could borrow or test:** adopt their appendix discipline for our reports — a fixed template listing the meter's assumptions (op costs, ADC cost, what is counted as data movement), so a reviewer can re-derive our ratios. Also separate *experimentation/search* cost from the *deployed loop* cost, which we currently blur.
- **What contradicts or challenges us:** the paper's core value is *measurement over estimation* — and our numbers are estimates by necessity. A reviewer will note we cannot invoke Henderson to validate a modeled meter. Our answer: our claims are *relative ratios at matched accuracy under one transparent model*, exactly the regime where a model (not a wattmeter) is the honest instrument; absolute joules are deferred to the analog-realism (SPICE/PVT) layer.

## Follow-on leads
- CodeCarbon / CarbonTracker as lighter-weight trackers (same measure-don't-estimate family).
- The "report search cost separately from final-model cost" idea → a discipline for our sweep/ablation energy.
