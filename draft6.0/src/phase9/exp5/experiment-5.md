# P9.5 — Assemble + FREEZE: does the fully-tuned neocortex loop hold A6 at the metered economy, and lock?

**Inheriting** every knob the ladder resolved — the committed P8.6 loop (NoiseAugContrast bulk · SLDA namer · DDM/error-EMA
awake gate · class-direction tap-drift trigger · cbrs) plus **N2 struck** (P9.1), **all-tap** consolidation (P9.2), **CBRS**
eviction (P9.3), and **proto-reanchor** read-side defense (P9.4, earned) — P9.5 turns them all on at once, re-runs the P8.6
live-safety gate on the *assembled* loop, and (on pass) locks the object at a commit hash for Phase 10 to race. **Nothing new
is tuned against the P10 baseline; every cut is internal.**

**Question.** Does the fully-assembled loop hold worst-point (pre-sleep) A6-BWT not-worse-than the known-boundary oracle in
≥4/5 seeds (the paired-sign veto), at accuracy within δ_acc of the P8.6 shipped object, at metered GD-share ≤ 0.25 — so it
can be frozen? If a knob interaction breaks it, fix inside P9 and re-freeze.

**Setup.** Integration — all committed knobs live on the lifelong CI+revisit+nuisance stream, 5 seeds. Three freeze cuts, all
vs INTERNAL references (never the P10 BP+replay number): (1) worst-point BWT paired-sign veto vs the oracle (neg ≤ 1);
(2) AA within δ_acc of the P8.6 shipped-loop live AA (the pinned reference — "P9 tuning did not cost accuracy vs what P8
shipped"); (3) GD-share ≤ 0.25. FREEZE + CONT-SAFETY + INV. **Internal-signals-only affirmed.**

**Run — the honest two-step (a failed first assemble, then the freeze-driven cadence re-confirm).**

*First assemble (the inherited P8 grid-8 cadence — which is the P8.6 shipped object bit-for-bit, since every P9 knob was
struck/kept).* It **FAILED the oracle-veto: 2/5 seeds** (137, 314) had worst-point BWT materially more-negative than the
boundary oracle (−0.517 vs −0.317; −0.439 vs −0.272), though AA-held (0.494) and GD-share (0.138) passed. Distribution-level
the two are within noise (IQRs overlap, 3/5 better), but the strict paired-sign veto needs ≥4/5 not-worse. This is a real
result, logged (`run_p9_5_grid8_attempt.log`), not narrated away.

*Diagnosis.* The assembled loop == the shipped object bit-for-bit (0/5 regression vs P8.6 — P9 tuning cost nothing), so the
gap is not a P9 knob interaction. In `run_economy_p9` the oracle and the committed loop **sleep on the same grid cadence** and
differ only in the awake fire (op c): the oracle fires at task onsets, the committed loop fires when DDM detects drift. On the
lifelong **revisit** stream, the sparse grid-8 sleep (~12 sleeps) lets the pre-sleep state fall into deep troughs between
sleeps on high-variance seeds; the boundary oracle's onset-timed fires avoid them. The gate/trigger are **committed and out of
P9 scope** (design §0.2) — so the one P9-legal lever is the sleep **cadence** (S7 / P9.2's deferred frequency re-confirm, owed
by the P8 "cadence is drift-rate-conditional" caveat, now discharged by the freeze).

*The cadence re-confirm* (`run_p9_5_cadence.py`; the freeze-driven frequency sub-table; internal references only; the full
frontier `{2,4,5,6,8,16}`, dense→sparse, saved to `figs_p9_5_cadence/arrays.npz`):
| cadence | neg/5 vs oracle | AA | GD-share | nsleep | worst-BWT | freeze cut |
| --- | --- | --- | --- | --- | --- | --- |
| grid-2 | 0 | 0.495 [0.483–0.523] | 0.215 | 50 | −0.033 | passes (no safer than grid-4, costlier) |
| **grid-4 (committed — the knee)** | **0** | 0.494 [0.478–0.502] | **0.178** | 25 | **−0.028** | **passes (best worst-BWT of the frontier)** |
| grid-5 | 0 | 0.495 [0.483–0.523] | 0.166 | 20 | −0.039 | passes (cheaper than grid-4; near-flat) |
| grid-6 | 0 | 0.495 [0.483–0.523] | 0.153 | 16 | −0.087 | passes (razor tie) |
| grid-8 (P8, single-pass-tuned) | **2** | 0.494 [0.478–0.502] | 0.138 | 12 | −0.317 | **fails veto** |
| grid-16 | 0 | **0.458 [0.458–0.478]** | 0.107 | 6 | −0.367 | **fails AA-held** |

The **freeze band is grid-2 → grid-6** — all four clear the veto at held AA + GD-share ≤ 0.25. **grid-4 is the knee**: it has
the **best absolute worst-BWT of the entire frontier** (−0.028), so it stays committed, while grid-5 (cheaper, GD 0.166,
near-flat −0.039) and grid-6 (cheaper still, but a razor tie at −0.087) are viable lighter options. The two failures are on
*different* axes: **grid-8 fails the veto** (sparse-sleep troughs on 2/5 seeds), while **grid-16 fails AA-held** — 6 sleeps
under-consolidate, so accuracy itself drops to 0.458 (< the 0.474 bar) and worst-BWT collapses to −0.367; it is *not* random
(well above chance), just the over-sparse "paid-less-compute" cliff. (Note: at grid-5 and grid-16 the boundary-onset *oracle*
hits an unlucky pre-sleep phase alignment and its own worst-BWT jumps, so there the assembled loop *beats* the oracle — the
veto passes, but the load-bearing read is the assembled worst-BWT, not a "ties-oracle" framing.) grid-4 committed unchanged
(the freeze is `59d2720`).

*Re-freeze (grid-4, 5 seeds).* All nine guards bit-exact.

**Result / figures.**
| mechanism | AA | worst-BWT (+paired-sign) | GD-share | vs-oracle | frozen? |
| --- | --- | --- | --- | --- | --- |
| **assembled (frozen)** — grid-4 | 0.494 [0.478–0.502] | **−0.028 [−0.039,−0.022]** (0/5 more-neg) | 0.178 [0.178–0.178] | ties oracle (−0.028) | **FROZEN** |
| oracle (grid-4, known boundaries) | — | −0.028 [−0.039,−0.022] | — | (ref) | — |
| base (P8.6 shipped, grid-8, same stream) | 0.494 [0.478–0.502] | −0.317 [−0.439,−0.267] | 0.138 | — | the AA ref |

- **FREEZE** (headline): the assembled grid-4 loop holds worst-point BWT at **−0.028**, exactly matching the boundary oracle
  (0/5 seeds more-negative), at AA 0.494 (= the shipped object, within δ_acc) and GD-share 0.178 (≤ 0.25). The frozen loop is
  **an order of magnitude safer** at the worst point than the shipped grid-8 loop on the lifelong stream (−0.028 vs −0.317) —
  the cadence re-confirm recovered the near-flat continual-safety the P8-single-pass cadence had lost under lifelong revisits.
  - **CONT-SAFETY**: assembled worst-point BWT ties oracle (veto 0/5 negative); AA ties oracle-level; the always-pay reference
    (carried) forgets more.
  - **INV**: all nine guards green.

**Read (8 slots).**
1. *Claim* — the fully-assembled maintenance loop (SLDA · DDM · tap-drift-direction · N2-struck · all-tap · CBRS ·
   proto-reanchor · **grid-4 lifelong cadence**) holds worst-point A6-BWT at the boundary-oracle level (−0.028, 0/5 more-neg)
   at held accuracy and GD-share ≤ 0.25 → the object **freezes**.
2. *Headline* — assembled worst-BWT **−0.028 [−0.039,−0.022]** = oracle −0.028 (veto 0/5), AA 0.494 = shipped 0.494, GD-share
   0.178 (n=5, lifelong CI+revisit+nuisance). Internal refs only; the shipped grid-8 loop is −0.317 on the same stream.
3. *Figures* — FREEZE (worst-BWT + AA + GD-share vs oracle/shipped), CONT-SAFETY (assembled vs oracle, veto marker), INV.
4. *Mechanism* — every P9 knob resolved to *keep* the committed loop, so the assembled loop equals the shipped object except
   for the one lever the freeze itself surfaced: the sleep **cadence**. Frequent consolidation (grid-4) keeps the pre-sleep
   state fresh, so the deep troughs the sparse grid-8 cadence allowed on high-variance seeds never form — and, crucially, the
   assembled loop's worst-point becomes *identical* to the oracle's (frequent sleep makes the DDM-vs-onset fire-timing
   difference irrelevant). The choice is a cadence-frequency knob, not a spine (direction/magnitude) knob; the spine lives in
   the eviction (CBRS) and read-side (proto-reanchor) knobs already committed.
5. *Threats* — (a) the worst-BWT-vs-oracle veto is against a reference that *cheats* with hidden boundaries — matching it
   (0/5) is the win, per design §2.3(d). (b) the cadence knee (grid-4) is read on the lifelong revisit schedule; a different
   revisit density could move the knee (the frequency is drift-rate-conditional — stated). (c) the meter is the P8 behavioral
   ADC-centred model (params logged). (d) the freeze passing required re-confirming a P8 knob (cadence) on the harder stream —
   reported openly (the grid-8 first-attempt failure is a first-class result, not hidden). Rule-1: the freeze is an
   integration (all knobs on); the cadence re-confirm swept one variable (cadence) as a separate sub-table.
6. *Decision* — **the object is frozen.** The committed neocortex loop = NoiseAugContrast bulk · SLDA · DDM/error-EMA gate ·
   class-direction tap-drift trigger · N2-struck · all-tap consolidation · CBRS eviction · proto-reanchor read-side ·
   **grid-4 lifelong sleep cadence**. S7 is extended again (the P8 grid-8 cadence, tuned on a single pass, is re-confirmed to
   grid-4 for the lifelong revisit regime). Phase 10 races this object; it touches no knob.
7. *Freeze-honesty* — **internal-signals-only affirmed** (the veto, AA-held, and GD-share cuts referenced only the oracle, the
   shipped object, and the metered economy — never the P10 BP+replay number). GD-share 0.178 ≤ 0.25 holds after the cadence
   re-confirm (denser sleep raised it from 0.138 to 0.178, still comfortably under the cap). Meter model + params logged.
8. *Live-safety / freeze* — the assembled loop holds worst-point BWT at the oracle level (0/5 negative — the paired-sign veto
   passes) and near-flat in absolute terms (−0.028). The freeze is locked by the P9.5 commit (manifest records the pre-freeze
   parent `1fb11b3`); the frozen object is fully specified by its manifest's committed-knob block (every knob enumerated,
   including the conditionals resolved off: `N2: struck`, and on: `read-side-residual: earned`). **P9 is closed and frozen.**
