# P9.2 — Readout-aware sleep cadence: which consolidation DEPTH holds A6 at the lowest sleep cost?

**Inheriting** the committed loop + the rotation-only drift from P9.0 and **N2 struck** from P9.1 (so the depth is
tuned on the *un-slowed* drift — no N2 to inherit), P9.2 asks whether the sleep re-fit can consolidate at a *shorter*
read depth — the deployed short reader (S9) that P5 found reads the continual home ~8× cheaper — and still hold the
continual-safety win.

**Question.** At the committed cadence (grid-8), does the sleep consolidation at a truncated depth (trunc-K = last 3
layers; per-depth = a single last layer) hold worst-point A6-BWT within δ_acc of all-tap, at a strictly lower metered
sleep cost (E-ratio ≥ 1.5×)? Or does the short reader lose A6 under the live lifelong drift → keep all-tap?

**Setup.** Swept variable = the sleep-consolidation depth ∈ {all-tap (P8), trunc-K, per-depth}; the depth applies to
the whole loop (awake read + sleep re-fit re-slice the same reader). Controls locked (committed loop, N2 struck,
lifelong stream, seeds [42,137,271,314,1729]). `sleep_cost` prices the Fdim-scaled solve/Gram term; the SCFF
re-forward is priced apart (`reforward` — depth-independent, since trunc re-slices the top of the full forward, per
design C6). CADENCE-DEPTH + INV. **Internal-signals-only affirmed.**

**Run.** 3 depths × 5 seeds, committed cadence grid-8. Wall ≈ 3.3 min.

**Result / figures.**
| depth | A6-BWT (worst) | sleep-cost (refit) | reforward (SCFF, apart) | accuracy-held | E-ratio | vs-all-tap | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-tap (P8) | **−0.317** [−0.439,−0.267] | 4.86e6 | 1.23e7 | 0.494 [0.478–0.502] | (ref) | (ref) | **committed** |
| trunc-K (last 3) | −0.511 [−0.533,−0.422] | 3.91e5 | 1.23e7 | 0.474 [0.457–0.481] | 12.4× | A6 not held | rejected |
| per-depth (last 1) | −0.373 [−0.422,−0.261] | 9.26e4 | 1.23e7 | 0.460 [0.459–0.475] | 52.5× | A6 not held | rejected |

- **CADENCE-DEPTH** (headline): the truncated readers are **12.4× / 52.5× cheaper** on the sleep refit's Fdim-scaled
  solve/Gram term, but their worst-point A6-BWT is **materially worse** (−0.511 / −0.373 vs all-tap −0.317, both beyond
  δ_acc) — the short reader forgets more under the live lifelong drift. The SCFF re-forward energy is identical across
  depths (trunc re-slices the top of the full forward — no forward saving), so the only saving is the solve/Gram term,
  and it does not buy A6.
  - **INV**: all nine guards green.

**Read (8 slots).**
1. *Claim* — no truncated consolidation depth holds worst-point A6-BWT within δ_acc of all-tap on the live lifelong
   stream, despite a 12–52× cheaper refit; **all-tap is kept** for continual safety.
2. *Headline* — all-tap worst-BWT −0.317 vs trunc-K −0.511 (E-ratio 12.4×) vs per-depth −0.373 (E-ratio 52.5×), both
   beyond δ_acc in ≥4/5 seeds (n=5, lifelong stream). Internal refs only.
3. *Figures* — CADENCE-DEPTH (A6-BWT × sleep-cost vs depth), INV.
4. *Mechanism* — the deployed short reader has fewer features (192 / 64 vs 768), so at the awake gate's worst
   mid-stream point — right after a revisit block shifts the class emphasis — it has **less capacity to keep old and
   new classes linearly separable** under the rotating frame → it forgets more. All-tap's extra capacity is the margin
   that absorbs the drift. This is the *live-loop* counterpart to P5's static finding (trunc reads the continual home
   cheaply): under the harder live drift, that cheapness costs A6. The saving is real (solve/Gram, ADC-dominated
   re-forward unchanged) but it does not buy safety, so it is not taken.
5. *Threats* — (a) the sleep-cost is the solve/Gram term only; the ADC-dominated SCFF re-forward (reported apart) is
   depth-independent, so the *full-loop* energy barely moves with depth — the depth axis is a refit-cost axis, not a
   loop-energy axis (stated). (b) stream-schedule dependence — worst-BWT at the awake worst mid-stream point. (c) the
   meter is behavioral. Rule-1: one variable (depth) at the committed cadence; the frequency re-confirm is **not owed**
   (N2 struck → the drift was not slowed).
6. *Decision* — **keep all-tap consolidation** (S7 extended: the P8 all-tap cadence stands; depth *does* matter, in the
   direction "all-tap's capacity is needed for A6 under lifelong drift"). P9.5 assembles all-tap.
7. *Freeze-honesty* — **internal-signals-only affirmed** (no P10 baseline consulted). All-tap is the committed depth,
   so the metered GD-share is unchanged (≤ 0.25); the meter model + params are the P8 ADC-centred model.
8. *Live-safety* — all-tap holds the least-negative worst-BWT of the three depths; the truncated readers' A6 loss is
   logged as a *result* (the short reader is a deployment-cost lever that fails the continual-safety bar here). Carried
   to P9.5 as the committed depth = all-tap.
