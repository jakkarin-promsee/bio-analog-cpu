# Phase 1 — Results ledger

> The **synthesis surface** for the whole phase. Each `expN/experiment-N.md` holds its own run; but *research
> is the arc*, and the arc lives **here** — one row per experiment, accumulated as they land. Without this,
> six folders is a pile of runs, not a phase result.
>
> Reporting format: [`result-format.md`](result-format.md). Live status pointer:
> [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md). Derivation (the *why*):
> [`../../idea/ideas1.md`](../../idea/ideas1.md).
>
> **Fill a row the moment a run's *decision* is made** — not before, and not buried in a side note. The scalar
> is the pinned **AAA** + **final held-out median ± IQR** (definitions in `result-format.md`).

| Exp | Commit | Headline scalar (AAA · final held-out med ± IQR) | Reference (GD ceiling / chance / bound) | Knob it set | Decision it fed | Card |
| --- | --- | --- | --- | --- | --- | --- |
| exp0-gate | _uncommitted_ | tapped-SCFF held-out **0.769** (1 seed; L1 probe 0.66→0.80) | chance 0.50 (GD ceiling = expand step) | goodness = **sum ‖h‖²** · θ=2.0 works · gate task = **2-D checkerboard** (spiral defeats SCFF-alone) · input-norm (ratified) | gate **PASS** → expand | [exp0](exp0/experiment-0.md) |
| exp0-full | _uncommitted_ | **GD ceiling 0.943 [0.938,0.943]** · SCFF lin 0.796 ≈ random 0.817 (within noise, 2-D) · SCFF>random on 64-D digits (0.841 v 0.780) | chance 0.50; gap +0.001 | 0a **two-sided** (≈contrast) · GD ceiling=0.943 · **low-D can't show SCFF>random** | quote 0.943 in Exp 1; **add a high-D (MNIST) probe at Exp 1**; keep 2-D for visualization only | [exp0](exp0/experiment-0.md) |
| exp1a | _uncommitted_ | **MNIST block 0.850 / gap +0.027** vs GD **0.938 / gap +0.062** (disjoint IQR, 5/5) · block backprop = **10%** of GD · digits 0.927 v 0.968 | GD ceiling MNIST 0.938 · digits 0.968 · chance 0.10 | **tap=ALL SCFF layers** (S3 "last-n" wrong) · pass-gate MET | block viable: near-GD acc, smaller gap, ~10% backward — **but SCFF degrades w/ depth → Exp 2's job** | [exp1](exp1/experiment-1.md) |
| exp1b | _uncommitted_ | scale-free: block held 0.79→0.94 as wts 4k→47k, **closes on GD** (Δ 0.15→0.03) | per-size GD ceiling | **default size H=64 (~25k)** | Exp 2/3 hold H=64 | [exp1](exp1/experiment-1.md) |
| exp2c | _uncommitted_ | plasticity: slow ρ=0.3 best 0.923 vs fast 0.912; drift↑ with ρ; **degradation persists at every ρ** | — | N2 knob: **slow read-layers** (ρ≈0.1–0.3) | drift mild in finite data (real test = Exp 4); plasticity ≠ degradation fix | [exp2](exp2/experiment-2.md) |
| exp2a | _uncommitted_ | SCFF:GD trade declines monotonically: digits 0.965→0.920, MNIST 0.943→0.837; **no free-lunch sweet spot** (but on MNIST 25% SCFF = first layer saves 65% backward for −3.7pt) | pure-GD ceiling digits 0.965 / MNIST 0.943 | keep **SCFF shallow** (~25%, the expensive input layer) | depth must come from the **boosting CHAIN (Exp 3)**, not deep SCFF | [exp2](exp2/experiment-2.md) |
| exp3 | _uncommitted_ | boosting chain digits **0.950 (gap +0.028)** > single block ~0.92, ≈GD 0.970; MNIST **0.858 (gap +0.033)** ≈ single block 0.850, vs GD 0.943 (gap +0.057); **saturates ~2 blocks** | pure-GD ceiling digits 0.970 / MNIST 0.943 | N3 boosting confirmed · **full residual ε=1** (diversity>preservation) · Ch9 delta off | depth-via-boosting real but weak/saturating (≈0 on MNIST); cheap+small-gap validated, deep-matches-GD not → **Exp 4 (continual) is the real home** | [exp3](exp3/experiment-3.md) |
| exp4 | _uncommitted_ | class-incremental: online ROTS (digits 0.18 / MNIST 0.19, no-sleep 0.086); **sleep recovers** digits 0.935/MNIST 0.865 (full), 0.898/0.863 (LUT); **SCFF probe flat (0.90/0.75) — doesn't forget** | static ceiling ~0.95/0.85; chance 0.10 | **sleep (3.1) + LUT (3.2) confirmed**; SCFF forgetting-robust | **continual = the architecture's validated home**; bridge to north star; remaining: Ch7 gate + LUT-vigilance/cadence sweep | [exp4](exp4/experiment-4.md) |

_(Add Exp 1, 2a, 2b, 2c, 3 rows as they run. One row per experiment; one variable's story per row.)_
