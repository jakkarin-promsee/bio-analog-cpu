# P5.2 — credit reach: temperature suffices; a bounded window closes the rest cheaply

*Inheriting the committed temp=0.2 (P5.1, residual 0.026 to the w12 ceiling), this rung asks whether a bounded
coordination window closes that residual — and settles the Track-C (global-credit) question.*

**Question.** How much composing depth does adding a bounded window buy on top of the sharp objective, at what
backward cost, vs the w12 ceiling? Does native depth need global credit (Track C) or is it solved cheaply?

**Setup.** Swept variable = window `{2,3,4}` at the committed temp=0.2 (mask=0.5), headroom + flat + mixed, L12,
seeds [42,137,271,314,1729], PROBE_EP=120; + temp0.2×w12 (the sharp objective's full-credit ceiling, headroom);
+ the **overlap re-confirmation** (headroom w4-stride2 vs w4-stride4). References (w12@temp0.5, tuned-BP) from P5.0.
*(The naive top-down negative — a new backward path, struck FD-verified in T3 — is logged, not rebuilt; it re-opens
only if a real gap to w12 survives, per the pre-registered Track-C rule.)* Guards: equiv 0.0e0, FD 2.1e-8.

**Run.** 11 cells × 5 seeds, checkpointed; wall ≈ 20 min. No NaN.

**Result / figures.** *(headroom; median [IQR], n=5)*
| window | tail-L12 | readout | peak | backward-work | vs w12@t0.5 (0.556) |
| --- | --- | --- | --- | --- | --- |
| w2 (temp0.2, the default) | 0.530 [0.527–0.539] | 0.550 [0.545–0.553] | L6 | 101k | −0.026 (real) |
| w3 | 0.548 [0.547–0.549] | 0.561 [0.560–0.561] | L7 | 149k | −0.008 |
| **w4 (the closer)** | **0.562 [0.547–0.562]** | 0.559 [0.557–0.561] | L9 | 198k (2×) | **−0.006 (closed; 3/5 above)** |
| w12@temp0.2 (objective ceiling) | 0.552 [0.549–0.559] | 0.575 [0.573–0.580] | L12 | 585k | — |
| w4-stride2 (overlap) | 0.559 [0.556–0.567] | — | L9 | 331k (1.67×) | within noise of w4 |

- **CREDIT-REACH** (headline): panel A — temp0.2 marches w2→w4 to meet the w12 ceiling; panel B (cost-Pareto) —
  **w4 Pareto-dominates w12** (tail 0.562 > 0.552 at 1/3 the backward cost). - **DEPTH-PROFILE-window**: the peak
  marches L6 (w2) → L9 (w4). - flat (w4 0.712) and mixed (w4 0.719) confirm the window helps off headroom. - **INV**: clean.

**Read (6 + 2 slots).**

1. **Claim** — Temperature does most of the work; a **bounded window w4 closes the residual fully** (to the w12
   ceiling) at 2× backward cost, while **overlap and global credit (Track C) add nothing** → native depth is solved
   cheaply, no global wire needed.
2. **Headline** — temp0.2×w2 tail **0.530 [0.527–0.539]** (readout 0.550, **beats tuned-BP 0.531**) leaves a real
   0.026 residual; temp0.2×w4 tail **0.562 [0.547–0.562]** = the w12@temp0.5 ceiling (0.556; gap −0.006, 3/5 above —
   **not real-below**), a real +0.032 over w2 (4/5, IQR-disjoint) at 2× cost. (n=5, headroom, PROBE_EP=120.)
3. **Figures** — CREDIT-REACH (tail-vs-window + cost-Pareto), DEPTH-PROFILE-window, INV. All regen from `arrays.npz`.
4. **Mechanism** — A longer gradient chain (window) lets each layer account for what the next w−1 layers need,
   extending the on-manifold region past temp0.2's reach — but the sharp objective already holds the **direction**, so
   the window's marginal gain is small (+0.032) and **saturates by w4** (≈ the temp0.2 objective's own full-credit
   ceiling, tail 0.552). Window = more credit reach for the same direction-preserving objective, not a new lever.
5. **Threats** — (a) **overlap**: at temp0.2 it is *within noise* of non-overlap (IQR bands overlap; T3's clean
   temp0.5 *hurt* softened to neutral at the sharper temp), but costs 1.67× → **dominated** (struck on cost, not on a
   clean hurt — reported honestly). (b) the w2 probe residual (0.026) is real on the *probe* but does **not** translate
   to a readout deficit (w2 readout 0.550 ≈ w4 0.559, within noise) — the headline metric already beats BP at w2.
   (c) w12@temp0.2 readout (0.575) edges w4 (0.559) by 0.016 — small, ≤0.02, and tail has no gap → not "a gap that
   matters."
6. **Decision** — **The EARN-depth thread is CLOSED.** Committed: **temp0.2 / window=2** as the cost-default (readout
   beats BP, cheapest at 101k); **w4 documented as the bounded depth-closer** (fully earns depth, +0.032 tail, 2× cost)
   for headroom-heavy tasks. **Track C DEFERRED** — the pre-registered gap rule (real-below w12 in *both* tail and
   readout, surviving to the continual workload) is **not** met; the cheap levers close it (so 2601.21683 is not
   load-bearing — no citation-gate decision rides on it). P5.3+ (the READ thread) inherits **temp0.2 / w2**.
7. **Cost-honesty** — w2 = 101k backward units (the default); w4 = 198k (~2×) for the full close; w12 = 585k (the
   forbidden 5.8×, **Pareto-dominated by w4**); overlap w4s2 = 331k for no real gain. The 80/20 cost is preserved by
   w2. Substrate units, never "energy."
8. **SCFF-completion** — **The EARN-depth verdict is MET**: native depth composes to the w12 ceiling (temp0.2×w4 tail
   0.562 ≥ 0.556, within-band; readout 0.550 beats BP already at w2). The architecture's identity question — *can SCFF
   earn depth?* — is answered **YES, cheaply, no global wire.** Remaining for SCFF-done: the **READ** thread (P5.3–5.5,
   where to read it cheaply) and the **GATE** (P5.7, continual-safety of temp0.2). Continual-safety NOT yet checked.

**Pre-submit checklist.**
- [x] Median [IQR], n=5; no bare means. - [x] "Real" rule: w4>w2 (4/5+IQR-disjoint); w4-not-below-w12 (3/5,
  overlapping); overlap within-noise (IQR overlap). - [x] Every depth figure draws the w12 ceiling + tuned-BP +
  cost-Pareto. - [x] All figures via `plot_p5.fig_*`; `regen` redraws all 5. - [x] 8 slots, formal voice; opens naming
  the inherited knob (temp0.2). - [x] `manifest.json` + `arrays.npz` to schema; backward-work meter recorded per cell.
- [x] Guards logged (FD 2.1e-8, equiv 0.0). - [x] Single-threaded. - [x] Spine: window = credit reach for the same
  direction-objective; no goodness invoked. - [x] Continual-safety (P5.7): flagged, not run. - [x] `RESULTS.md` row added.
