# Phase 11 — RESULTS (the LIMIT-MAP ledger)

> Every cell: win / tie / loss / FLOOR + number. The committed object (Arm A, frozen recipe) vs the stronger
> per-arena-tuned ER. Losses and floors ship — that is the deliverable. Real-stream safety/retention read '—'
> (no paired ER worst-BWT on a prequential stream; the accuracy channel is the pinned real-stream read, R2).

## The map

| channel \ arena | mnist | fashion | cifar | xdata(30way) | gas | har | electric | covtype |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accuracy (AA/prequential) | loss: 0.28 loss -0.14 | loss: 0.38 loss -0.13 | FLOOR: FLOOR 0.12 (tie) | tie: 0.34 30-way | win: 0.79 win +0.03 | FLOOR: FLOOR 0.69 (field+0.07) | FLOOR: FLOOR 0.61 (field+0.08) | FLOOR: FLOOR 0.47 (field+0.07) |
| safety (worst-BWT) | win: -0.01 win +0.18 | win: -0.02 win +0.12 | FLOOR: FLOOR (uninform.) | — | — | — | — | — |
| retention (worst-point) | win: 0.22 win +0.12 | loss: 0.35 loss -0.13 | FLOOR: FLOOR (uninform.) | loss: 0.42 loss -0.12 | — | — | — | — |
| order-invariance | win: |Δ|=0.003 win | — | — | win: |Δ|=0.007 win | win: |Δ|=0.043 win | — | — | — |
| beats no-change? | — | — | — | — | win: nc 0.61 beaten | FLOOR: nc 0.95 NOT beaten | FLOOR: nc 0.84 NOT beaten | FLOOR: nc 0.65 NOT beaten |

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
- **P11.4 cross-dataset**: Arm A TYPE-SCOPED — all types alive but retention trails ER; Arm B TYPE-ROBUST — worst-point retention >= ER and all 3 data types stay alive
- **P11.5 r2_A (fashion)**: OURS aa 0.382 worstBWT -0.021 vs ER aa 0.507 worstBWT -0.146 (ceiling 0.655) → BET HOLDS (safety win)
- **P11.5 r2_B (fashion)**: OURS aa 0.454 worstBWT -0.057 vs ER aa 0.530 worstBWT -0.141 (ceiling 0.655) → BET HOLDS (safety win)
- **P11.5 r3_A (cifar10gray)**: OURS aa 0.123 worstBWT -0.017 vs ER aa 0.107 worstBWT -0.102 (ceiling 0.199) → FLOOR (ceiling 0.20)
- **P11.5 r3_B (cifar10gray)**: OURS aa 0.127 worstBWT -0.019 vs ER aa 0.098 worstBWT -0.095 (ceiling 0.199) → FLOOR (ceiling 0.20)
- **P11.5 crossover**: no memory-bytes crossover in realistic C (F=768 all-tap covariance is a large fixed cost); but the RETENTION crossover is real by C=20 — measured worst-retention C10 OURS 0.354/ER 0.423 (ER leads) → C20 OURS 0.233/ER 0.014 (ER's buffer dilutes; OURS holds)
- **P11.6 scaling (W [64, 128, 256] @ D80)**: GD-share measured [0.173, 0.278, 0.45] vs pinned [0.21, 0.341, 0.531] → shape CONFIRMED; acc [0.424, 0.473, 0.502] (capacity buys the gap back); substrate× [5.39, 6.89, 7.25] (non-decreasing)
- **P11.7 throughput**: BRANCH (i) THE REGIME WIN — OURS's critical rate exceeds ER's (a rate exists where ER drops and OURS does not).
