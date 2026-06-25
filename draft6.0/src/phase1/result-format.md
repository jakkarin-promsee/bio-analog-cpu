# Phase 1 — result-format delta (figure additions)

> **Inherits the house style from [`../result-format.md`](../result-format.md)** — the colour/linestyle
> encoding, IQR bands, reference lines, axis rules, the reproducibility contract (`manifest.json` + `arrays.npz`
> + a `plot.py` that regenerates every figure), the gap definition, the probe discipline, the "calling a
> difference real at n=5" rule, and the six-slot summary template are all defined there. Phase 1 uses the **base
> figure catalog (F1–F9 + INV)** verbatim; this file adds only the Phase-1-specific *mandatory-per-experiment*
> map.

---

## Mandatory-per-experiment map (the Phase-1 floor)

Each experiment **declares which base-catalog figures it emits**; this is the minimum set per rung. Adapt
upward case-by-case, never below.

| Experiment | Must emit |
| --- | --- |
| **exp0** — SCFF + GD alone (the gate) | F4, F3, F1, F5, INV |
| **exp1** — block vs GD | F1 (gap shaded) + F2 scalar, F3, F7, INV (+F5 if Tier-A, +F6 coarse grid; full surface in 1b) |
| **exp2a/2c** — inside the block | ablation table + F9 (2a) / acc + drift (2c), each with F1, INV |
| **exp3** — residual-boosting chain | F8, F2, F1, inter-block-drift, INV |
| **exp4** — continual (gate + sleep) | rot-vs-sleep + the SCFF all-class probe, INV |

**Both headlines named.** Where a rung sweeps difficulty × size, **F6 (the reachability surface) co-headlines
with F1** — the surface is the scale-free read we trust most, not a 1b afterthought.
