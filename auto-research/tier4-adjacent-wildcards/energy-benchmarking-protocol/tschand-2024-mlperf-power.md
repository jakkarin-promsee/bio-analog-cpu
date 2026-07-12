# MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from Microwatts to Megawatts for Sustainable AI
- **Authors / Year / Venue:** Arya Tschand, A. T. R. Rajan, S. Idgunji, … David Kanter, Vijay Janapa Reddi (MLCommons Power WG, 20+ orgs) / 2024 (arXiv) → HPCA 2025
- **Link:** https://arxiv.org/abs/2410.12032 (fetched)
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐ — the industry standard for *fair, comparable* energy measurement: full-system wall-power at a matched quality target, with rules that stop cherry-picking. The template a reviewer will hold our meter against.

## TL;DR
A consortium methodology for measuring ML-system energy from µW (TinyML) to MW (datacenter). Measures **full-system wall power** under representative MLPerf workloads, enforces measurement rules for comparability, and reports 1,841 reproducible measurements across 60 systems. Its headline methodological lesson: measured system energy diverges meaningfully from chip-only or FLOP-based estimates, because data movement and system overhead dominate.

## The mechanism (how it actually works)
MLPerf benchmarks are defined around a **quality target** (e.g. reach a fixed accuracy) — so energy/throughput is always measured *at matched task performance*, which is iso-accuracy by construction. MLPerf Power adds a standardized power-measurement harness: an external analyzer captures wall-socket power for the whole system under test (not just the accelerator die), across a defined measurement window, with rules on idle handling, averaging, and what may be excluded. This closes the two classic loopholes — reporting component power (hiding memory/host/cooling) and reporting at a favourable operating point. The µW–MW span forces one methodology to be scale-invariant, exposing that *data movement between memory hierarchies* is often the larger energy term than compute.

## Key results / claims
- 1,841 measurements / 60 systems; standardized, reproducible, cross-architecture comparable.
- System-level (wall-power) energy ≠ chip-only ≠ FLOP-estimated; the gap is data movement + system overhead.
- Establishes energy as a first-class, *comparable* benchmark metric with published rules.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P10 fair race (matched-accuracy vs tuned ER); the credibility of the P8.7/P10 meter; the "same-substrate" discipline.
- **Same as us:** MLPerf's *quality-target-first* design is exactly our "freeze in P9, judge in P10 at matched accuracy" discipline, and our fair budget-matched ER baseline (Prabhu CVPR'23) — we independently arrived at iso-accuracy benchmarking. Their "measure the whole system, not the die" rule is *why* our win must be a system/substrate claim, not a FLOP claim.
- **Different from us:** MLPerf Power measures wall-power on real hardware; our meter is a **modeled relative pJ (behavioral, ADC-centred, NOT SPICE)** on a chip that doesn't exist. We cannot claim MLPerf-grade measurement — but we *can* adopt its *rules* (fixed window, count all data movement, no favourable operating point) inside our model.
- **What we could borrow or test:** state our meter's scope in MLPerf's vocabulary — declare what the meter counts as "system" (does it include the ADC, the LUT read, the host?), fix the operating point, and report at the matched quality target. This pre-empts "you measured a favourable slice." Also: MLPerf Training reports *energy-to-target*; we could report *energy-to-reach-a-fixed-continual-retention*, the continual analogue.
- **What contradicts or challenges us:** a reviewer citing MLPerf will say "real energy is system wall-power; your ADC-centred behavioral pJ is neither wall-power nor SPICE." Honest answer: our claim is a *relative ratio at matched accuracy under a stated model*, with absolute joules explicitly deferred to the analog-realism layer — we are not claiming an MLPerf-measured number.

## Follow-on leads
- MLPerf Training (Mattson et al. 2020) — the quality-target-then-measure protocol we should mirror for a continual "energy-to-retention."
- MLPerf Tiny / µW regime — the closest scale to an on-chip learner; its rules for tiny-system power.
