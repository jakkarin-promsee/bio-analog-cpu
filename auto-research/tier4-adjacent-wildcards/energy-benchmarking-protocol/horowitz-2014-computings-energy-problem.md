# 1.1 Computing's Energy Problem (and what we can do about it)
- **Authors / Year / Venue:** Mark Horowitz / 2014 / IEEE ISSCC 2014 (plenary), DOI 10.1109/ISSCC.2014.6757323
- **Link:** https://ieeexplore.ieee.org/document/6757323 · reachable mirror (fetched via search): https://gwern.net/doc/cs/hardware/2014-horowitz-2.pdf
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐⭐ — the canonical pJ table that *proves* data movement, not arithmetic, dominates energy. This is the physical basis of our entire "the win is the substrate / compute-in-memory" claim, and the number a reviewer will demand behind it.

## TL;DR
At 45 nm / 0.9 V, an arithmetic op costs order ~1 pJ (0.9 pJ add, 3.7 pJ FP MAC-ish), an on-chip SRAM/cache access costs ~10–100 pJ, and an **off-chip DRAM access costs ~1,300–2,600 pJ** — roughly 1000× the arithmetic. Therefore, for any memory-bound workload the energy bill is *fetching operands*, not computing on them. Compute is nearly free; moving data is the cost.

## The mechanism (how it actually works)
Horowitz decomposes the energy of an operation into the ALU work plus every byte moved to feed it. Because transistor energy scaled far faster than wire/interconnect and off-chip I/O energy, the ratio has become extreme: a 64-bit DRAM read is ~1 nJ-scale while the MAC it feeds is ~pJ-scale. The consequence for architecture is that **locality is the only lever that matters** — keeping operands resident (in registers/SRAM, or physically *at* the compute site) collapses the dominant term. This is the argument that motivates near-/in-memory computing: if you compute where the weights live, you delete the data-movement term entirely rather than paying it every cycle.

## Key results / claims
- The pJ hierarchy (45 nm, 0.9 V): int add ~0.03–0.9 pJ; FP add/mult ~0.4–3.7 pJ; 8 KB–1 MB SRAM read ~10–100 pJ; off-chip DRAM ~1.3–2.6 nJ per 64-bit access.
- Data movement dominates energy by ~2–3 orders of magnitude over the arithmetic it serves.
- Energy efficiency is now an architecture problem (specialization, locality), not a process-scaling gift.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** P8.7 substrate factor (5.4× compute-in-memory; analog floor ≥2.7×, →53× with the memory wall); the "why analog is load-bearing" claim in P10 R1.
- **Same as us:** our thesis *is* Horowitz's conclusion applied to learning — the analog crossbar holds weights as resident charge and computes on them in place, so the ~1000× data-movement term the digital baseline pays every MAC is structurally absent. This card is the citation that turns "analog is cheaper" from assertion into physics.
- **Different from us:** Horowitz's numbers are for a conventional digital datapath; our analog substrate factor is *modeled* against that datapath, not measured. We inherit his ratios as the justification for our floor, but the exact multiplier is our meter's assumption.
- **What we could borrow or test:** price our energy meter *in Horowitz's currency* — show the digital-baseline cost broken into arithmetic + memory-movement terms, then show the analog substrate deletes the movement term. That makes the 5.4× (and the →53× memory-wall figure) a transparent consequence of a peer-reviewed table, not a free parameter. It also directly answers "you ignored data movement" — the classic reviewer trap.
- **What contradicts or challenges us:** these are 2014, 45 nm numbers; a reviewer can argue modern HBM + on-chip SRAM caching narrows the gap for well-blocked GEMMs. Counter with Gholami 2024 (this folder): the FLOP-vs-bandwidth gap has *widened*, not closed, so the movement term is worse than 2014, not better.

## Follow-on leads
- Gholami 2024 "AI and Memory Wall" (this folder) — the modern update of the same gap.
- Roofline / operational-intensity modeling as the framework to express "movement-bound vs compute-bound" for our meter.
