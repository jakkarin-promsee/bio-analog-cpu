# Phase 11 — RESULTS (the LIMIT-MAP ledger)

> Every cell: win / tie / loss / FLOOR + number. The committed object (Arm A, frozen recipe) vs the
> stronger per-arena-tuned ER. Losses and floors ship — that is the deliverable.

## The map

| channel \ arena | mnist | gas | har | electric | covtype | xdata(30way) |
| --- | --- | --- | --- | --- | --- | --- |
| accuracy (AA/prequential) | loss: 0.28 loss -0.14 | win: 0.79 win +0.03 | FLOOR: FLOOR (0.69 field+0.07) | FLOOR: FLOOR (0.61 field+0.08) | FLOOR: FLOOR (0.47 field+0.07) | tie: 0.34 30-way |
| safety (worst-BWT) | win: -0.01 win +0.18 | tie: -0.333  | tie: -0.233  | tie: -0.149  | tie: -0.097  | — |
| retention (long/worst) | win: 0.22 win +0.12 | — | — | — | — | loss: 0.42 loss -0.12 |
| order-invariance | win: |Δ|=0.003 win | — | — | — | — | win: |Δ|=0.007 |
| no-change beaten? | — | win: nc 0.61 beaten | FLOOR: nc 0.95 NOT beaten | FLOOR: nc 0.84 NOT beaten | FLOOR: nc 0.65 NOT beaten | — |

## Δbulk overlay (P11.1 — the strike-1 answer, arena-nonlinearity)

- **synth**: Δbulk(home-AA) = +0.417 (bulk 0.589 vs proj 0.172)
- **mnist**: Δbulk(home-AA) = +0.008 (bulk 0.778 vs proj 0.770)
- **digits**: Δbulk(home-AA) = -0.014 (bulk 0.936 vs proj 0.950)

## Per-rung headline

- **P11.1 decomposition**: NARROWED-WITH-MECHANISM — the architecture is MORE than its closed-form namer where the data is NONLINEAR (synth home Δbulk +0.417; iid-noise Δbulk>0), and correctly NULL where a linear namer already saturates (digits Δbulk -0.014). 'Is it just SLDA?' -> No on the data that needs a bulk; effectively yes where a linear head suffices. The bulk's value is arena-nonlinearity, mapped.
- **P11.2 MNIST**: BET HOLDS on MNIST — safety(worst-BWT)/order-invariance stay green (both arms) while static AA does what it does
- **P11.3 gas**: OURS-A 0.789 vs stronger-ER 0.756 vs no-change 0.605 → WIN (OURS >= stronger-ER at prequential accuracy)
- **P11.3 har**: OURS-A 0.686 vs stronger-ER 0.754 vs no-change 0.950 → FLOOR (no-change 0.950 not beaten)
- **P11.3 electric**: OURS-A 0.606 vs stronger-ER 0.687 vs no-change 0.836 → FLOOR (no-change 0.836 not beaten)
- **P11.3 covtype**: OURS-A 0.471 vs stronger-ER 0.542 vs no-change 0.646 → FLOOR (no-change 0.646 not beaten)
- **P11.4 cross-dataset**: TYPE-SCOPED — all types alive but retention trails ER
