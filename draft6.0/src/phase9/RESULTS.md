# Phase 9 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema (no prose). Controls locked unless swept. Device under test = the
> **frozen-as-a-DESIGN** `NoiseAugContrast` cell (SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0) + the
> committed Phase-8 loop (SLDA namer · DDM/error-EMA awake gate · cbrs guard · grid-8/full/λ1.0 sleep), run **LIVE** on
> a **lifelong** CI+revisit+nuisance stream (`make_lifelong_stream` — 2 revisit cycles, n_steps 536). Seeds
> `[42,137,271,314,1729]`. Median `[q25–q75]`. δ_acc = 0.02. **Every cut is vs an INTERNAL reference — the
> frozen/oracle baseline, the always-pay ceiling, the measured drift, or the metered energy — NEVER the P10 BP+replay
> number** (freeze in P9, judge in P10). The cost meter is the P8 behavioral ADC-centred model, NOT SPICE.

Ran 2026-07-02 (seeds `[42,137,271,314,1729]`, `--quick` off, single-thread CPU/float64, numpy 2.3.5). All nine guards
(7 carried P8 + `n2_readside` + `evict_equiv`) bit-exact every rung.

---

## P9.0 — bench + guards + bulk-drift + the rotation/staleness/DESTRUCTION split *(risk gate; no knob swept)*

*Controls: live bulk, committed loop, lifelong stream (n_steps 536, onsets [40,88,136,184], nuis 472), 5 seeds.*

| guard | measured | pass |
| --- | --- | --- |
| partial_fit_equiv (ranpac/slda) | 4.11e-15 / 2.22e-16, miss 0 | ✓ |
| fd_budget_gate | 3.47e-08 | ✓ |
| meter_proxy | fwd-MAC 1 556 000 ≡ readout_cost | ✓ |
| detector_far floor | {abs 0.0, ddm 0.0, adwin 0.0} | ✓ |
| scff_static_frozen | 0.00e+00 (acc 0.566) | ✓ |
| live_path_anchor | 0.00e+00 (AA 0.3602=0.3602) | ✓ |
| cache_replay | 0.00e+00, fire-diff 0 | ✓ |
| **n2_readside** | off≡P8 0.0/fire-diff 0; LLRD ρ=1 0.0 **and** ρ<1 early/mid 0.0, late 7.9e-3 | ✓ |
| **evict_equiv** | cap=∞ 140/140; cap=30 recency ≡ last-30 FIFO | ✓ |

| curve / read | value (median [IQR]) | vs reference | verdict |
| --- | --- | --- | --- |
| (1) rotation cos(rep_t, birth) | 0.645 [0.631–0.655] | taps rotate ~36% | the map moves |
| (2) staleness (frozen probe) | 0.069 [0.000–0.600] | / birth | a fixed head rots — sleep fixes it |
| **(3) DESTRUCTION (re-fit probe) ⭐** | **2.207 [2.097–2.472]**, min 0.966 | / birth re-fit | **≥ birth throughout → bulk does NOT forget** |
| committed loop | AA 0.494 [0.478–0.502], wBWT −0.317 [−0.439,−0.267], f 0.002 | vs oracle | ties oracle AA; wBWT 0.028 below |
| oracle-cadence ref | AA 0.494, wBWT −0.289 [−0.317,−0.278] | (ref) | achievable reference |
| always-pay ceiling | AA 0.530 [0.505–0.539], wBWT −0.400 | — | fires every step, forgets more |

**Verdict: ROTATION-ONLY — the cheap-replay assumption holds (re-fit destruction retention ≥ birth across the long
stream).** The founding "the bulk doesn't forget" caveat is discharged (measured). N2 is *not mandatory*. Fig:
DRIFT-LIFELONG, CONT-SAFETY, INV. Wall 584s.

---

## P9.1 — N2: the drift-slowdown bake-off *(swept: N2 mechanism; committed cadence grid-8; read-side/rate-only)*

*Controls: committed loop, lifelong stream, 5 seeds. LLRD `n2_readside` rate-only (early/mid taps move 0.00).*

| N2-arm | drift-red | sleep-freq | accuracy-held | A6-BWT(worst) | plasticity | vs-no-N2 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no-N2 (P8) | 0.000 | 0.022 [0.007–0.022] | 0.494 [0.478–0.502] | −0.317 [−0.439,−0.267] | 0.383 | (ref) | baseline |
| EMA-view β0.3 | −0.035 | 0.022 | 0.488 [0.480–0.505] | −0.383 [−0.383,−0.378] | 0.365 | worse BWT | not eligible |
| EMA-view β0.1 | −0.009 | 0.022 | 0.485 [0.480–0.504] | −0.344 [−0.378,−0.294] | 0.377 | worse BWT | not eligible |
| LLRD-rate ρ0.5 | 0.000 | 0.022 | 0.495 [0.487–0.505] | −0.328 [−0.422,−0.256] | 0.378 | within noise | no lever |

**Verdict: N2 STRUCK** (standby → struck). No arm sleeps sparser (all 0.022) or improves worst-BWT; EMA-view *worsens*
it (train/eval frame mismatch). The grid-8 cadence already tracks the rotation-only drift → no drift for N2 to slow.
LLRD is honestly rate-only (no Stage-1 reopen). Fig: N2-BAKEOFF, INV. Wall 396s.

---

## P9.2 — consolidation depth *(swept: sleep depth; committed cadence grid-8; N2 struck inherited)*

*Controls: committed loop, lifelong stream, 5 seeds. sleep-cost = the Fdim solve/Gram term; SCFF re-forward apart.*

| depth | A6-BWT(worst) | sleep-cost | accuracy-held | E-ratio | vs-all-tap | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| all-tap (P8) | −0.317 [−0.439,−0.267] | 4.86e6 | 0.494 [0.478–0.502] | (ref) | (ref) | **committed** |
| trunc-K (last 3) | −0.511 [−0.533,−0.422] | 3.91e5 | 0.474 [0.457–0.481] | 12.4× | A6 not held | rejected |
| per-depth (last 1) | −0.373 [−0.422,−0.261] | 9.26e4 | 0.460 [0.459–0.475] | 52.5× | A6 not held | rejected |

**Verdict: keep ALL-TAP** (S7 extended). trunc/perdepth are 12–52× cheaper on the refit but forget more (A6-BWT beyond
δ_acc) — the short reader loses A6 under live lifelong drift; all-tap's capacity earns its keep. Fig: CADENCE-DEPTH,
INV. Wall 198s.

---

## P9.3 — bounded-LUT eviction *(swept: eviction policy @ cap 120; base committed loop; new StreamingLUT)*

*Controls: base committed loop, lifelong stream, 5 seeds. cap 120 = pressure point (~12 exemplars/class).*

| policy | evict-BWT(worst) | accuracy-held | vs-oracle | verdict |
| --- | --- | --- | --- | --- |
| unbounded-oracle | −0.240 [−0.287,−0.228] | 0.514 [0.492–0.519] | (ref) | ceiling |
| **CBRS** | −0.400 [−0.406,−0.367] | 0.380 [0.374–0.391] | 0.16 below | best bounded (committed) |
| herding (null) | −0.367 [−0.427,−0.361] | 0.318 [0.314–0.380] | 0.13 below | ties CBRS → buffer-spine null |
| reservoir (iid) | −0.607 [−0.613,−0.547] | 0.359 [0.352–0.371] | 0.37 below | re-imports forgetting |
| recency/FIFO | −0.707 [−0.780,−0.587] | 0.327 [0.325–0.336] | 0.47 below | re-imports forgetting |

*Scaling sub-table (cbrs BWT):* cap40/80/120/200/400 = 6cls −0.392/−0.301/−0.263/−0.296/**−0.237** · 10cls
−0.456/−0.444/−0.406/−0.372/−0.311. **min-cap-hold grows with #classes (6cls cap400, 10cls >400) → scaling flag.**

**Verdict: CBRS committed** (S13-candidate) — best bounded policy, ties the herding null (buffer-spine null: density≈
class at the buffer here), decisively beats iid/FIFO; the deployment cap scales with #classes. Fig: EVICT, INV. Wall 342s.

---

## P9.4 — read-side noise residual *(CONDITIONAL — earn-its-place gate FIRED; swept: read-side defense)*

*Controls: committed loop, committed cell, Phase-6 input-transducer DIRECTIONAL residual (NoiseModel dir, RMS 1.5 — the
channel SCFF's per-sample norm cannot forward-remove; NOT p8's layernorm-invariant nuisance, which SCFF removes → vacuous),
5 seeds. Eval residual and proto-reanchor share ONE device offset (direction-consistency). Calibration is direction-grounded
(never entropy/confidence — the spine).*

| defense | residual-retention | residual-dent (gate) | vs-no-residual | verdict |
| --- | --- | --- | --- | --- |
| off (undefended) | 0.787 [0.738–0.833] | 0.115 [0.093–0.145] | (ref) | dents > δ_acc, 5/5 → **gate FIRES** |
| **proto-reanchor** (primary) | 0.986 [0.978–0.993] | — | +0.199 (5/5) | **recovers → ADOPT** |
| SLDA cov re-fit (fallback) | — | — | — | not exercised (primary sufficed) |

**Verdict: read-side residual RESOLVED read-side — proto-reanchor ADOPTED.** The gate fires (dent +0.115 [0.093–0.145],
5/5 > δ_acc; worst seed 1729 collapses undefended retention to 0.504); prototype re-anchoring — re-forwarding the raw LUT
through the current bulk under the *same* device offset → drift-free, shift-consistent (direction-grounded) prototypes —
restores retention to 0.986 [0.978–0.993] (within δ_acc of no-residual, 5/5). The Phase-6 "scoped-YES → Stage-2 read-side"
debt is discharged; the residual is defended, not named to the analog layer. P9.5 carries proto-reanchor as the committed
read-side defense (dormant on a clean stream, active under the channel). Fig: RESIDUAL, INV. Wall 150.5s.

---

## P9.5 — assemble + FREEZE *(integration — all committed knobs live; the lock)*

*Controls: the assembled loop = NoiseAugContrast bulk · SLDA · DDM/error-EMA gate · tap-drift-direction trigger · N2-struck ·
all-tap · CBRS · proto-reanchor, on the lifelong stream, 5 seeds. Three freeze cuts, all vs INTERNAL references: worst-BWT
paired-sign veto vs the oracle; AA within δ_acc of the P8.6 shipped loop; GD-share ≤ 0.25.*

**First assemble (inherited grid-8 cadence = the P8.6 shipped object bit-for-bit) FAILED the veto** — 2/5 seeds (137, 314)
worst-BWT −0.517/−0.439 vs oracle −0.317/−0.272 (materially more-negative); AA-held ✓, GD-share 0.138 ✓. Not a P9 regression
(assembled ≡ base, 0/5 vs shipped); the gap is the sparse cadence + the committed gate's fire-timing (both sleep on the same
grid; oracle fires at onsets, DDM lags). Gate is out of P9 scope → the P9-legal lever is the sleep cadence (S7 / the P8
drift-conditional debt).

*Cadence re-confirm (freeze-driven frequency sub-table; internal refs only):*
| cadence | neg/5 vs oracle | AA | GD-share | worst-BWT | freeze cut |
| --- | --- | --- | --- | --- | --- |
| grid-8 (P8, single-pass) | 2 | 0.494 | 0.138 | −0.317 | fails veto |
| grid-6 | 0 | 0.495 | 0.153 | −0.087 | passes (razor tie) |
| **grid-4 (committed, the knee)** | 0 | 0.494 | 0.178 | −0.028 | **passes** |
| grid-2 | 0 | 0.495 | 0.215 | −0.033 | passes (no safer, costlier) |

*Re-freeze (grid-4, 5 seeds, all nine guards bit-exact):*
| mechanism | AA | worst-BWT (+paired-sign) | GD-share | vs-oracle | frozen? |
| --- | --- | --- | --- | --- | --- |
| **assembled (frozen)** grid-4 | 0.494 [0.478–0.502] | **−0.028 [−0.039,−0.022]** (0/5 more-neg) | 0.178 [0.178–0.178] | ties oracle | **FROZEN** |
| oracle grid-4 (known boundaries) | — | −0.028 [−0.039,−0.022] | — | (ref) | — |
| base P8.6 shipped grid-8 (same stream) | 0.494 [0.478–0.502] | −0.317 [−0.439,−0.267] | 0.138 | — | AA ref |

**Verdict: FROZEN.** The assembled loop holds worst-point BWT at the boundary-oracle level (−0.028, veto 0/5 negative) at held
AA (0.494 = shipped) and GD-share 0.178 ≤ 0.25 — an order of magnitude safer at the worst point than the shipped grid-8 loop
on the lifelong stream (−0.028 vs −0.317). The freeze surfaced (and closed) the drift-rate-conditional cadence debt: the P8
grid-8 cadence, tuned on a single pass, is re-confirmed to **grid-4** for the lifelong revisit regime (S7 extended). The
committed neocortex loop is locked by the P9.5 commit (manifest records the pre-freeze parent `1fb11b3`); every knob is
enumerated in the manifest committed-knob block (incl. `N2: struck`, `read-side-residual: earned`). Phase 10 races this object;
it touches no knob. Fig: FREEZE, CONT-SAFETY, INV. Wall 314.5s (+ cadence re-confirm 544s).

---
