# Phase 7 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema (no prose). Controls locked unless swept. Device under test = the
> frozen `NoiseAugContrast` cell (SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0). Feature source =
> **all-tap (768-D)**, pinned at P7.0. Seeds `[42,137,271,314,1729]` (9 for the ≤0.02 spine-tension gap). Median
> [q25–q75]. `PROBE_EP=120`. Cost = **proxy, descriptive-only (real meter = P8)**.

---

## P7.0 — bench + guards + convex floor + static ceiling + RanDumb control  `exp0`
*(controls: synthetic CI home, all-tap, seeds ×5, PROBE_EP=120; guards 7/7 pass; wall 24.7 min)*

| ref / head·bulk | acc | vs-floor | vs-static-ceiling | vs-randproj-taps | vs-randproj-pixels | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| linear-softmax **(floor)** | 0.608 [0.582–0.610] | (floor) | −0.258 | +0.002 | +0.147 | the floor |
| MLP head | 0.642 [0.622–0.649] | +0.034 | −0.224 | — | — | small GD head buys +0.034 |
| `race_bp` **(static ceiling, raw input)** | 0.866 [0.861–0.887] | +0.258 | (ceiling) | — | — | tuned BP on pixels ≫ SCFF readout |
| OURS-bulk · **linear** | 0.608 | (floor) | −0.258 | **+0.002 (tie)** | **+0.147** | earns keep vs pixels; ties taps (ELM) |
| OURS-bulk · **rls** (ridge) | 0.579 | −0.029 | −0.287 | **+0.194** | **+0.265** | **earns keep on both arms** |
| OURS-bulk · ncm | 0.261 | −0.347 | — | −0.038 | +0.059 | sub-floor (greyed); earns keep vs pixels |

INV: dead-frac **0.000** · effective-rank **58.7** · FD-guard ✓ · feature-source-pinned ✓.
**Verdict:** BENCH TRUSTED — bulk beats random-from-pixels (5/5, decisive); random-from-taps tie for a linear namer
is the expected ELM effect (flagged to Stage 2, both readings); static ceiling confirms SCFF is a *continual*, not a
static-accuracy, competitor (P4-consistent).

<!-- P7.1 .. P7.6 rows appended as they run -->
