# P9.1 — N2, the drift-slowdown bake-off: does a read-side/rate-only lever earn its place, or is it struck?

**Inheriting** the committed SLDA + DDM/error-EMA + grid-8/cbrs economy from P8 and the **rotation-only** drift from
P9.0 (the bulk doesn't forget; a fixed head goes stale but the information is preserved), N2's only job is to make the
namer *chase the rotation less often* — hold A6 at a sparser sleep cadence, or improve worst-BWT, without a plasticity
tax. If it can't, it is struck (the last open decision-record knob resolves either way).

**Question.** Does a read-side N2 mechanism — **EMA-view** (the namer reads a per-tap EMA of the features; SCFF
untouched — the doubly-grounded default) or **LLRD-rate** (a `LLRDCell` subclass slows the late-read layers' SCFF
update; rate-only *only if* the representation guard holds) — reduce the sleep frequency needed to hold A6 (or improve
worst-BWT) at held accuracy and plasticity? Or does no arm clear the bar (→ struck), or does LLRD move the early/mid
taps (→ a Stage-1 reopen, flagged not done)?

**Setup.** Swept variable = the N2 mechanism ∈ {no-N2, EMA-view β∈{0.3,0.1}, LLRD-rate ρ=0.5 (late=4)}. Controls
locked (committed loop, lifelong stream, seeds [42,137,271,314,1729]). The lever = *strict improvement*: the arm holds
A6 (worst-BWT within δ_acc of no-N2 grid-8) at a **strictly sparser** cadence (real-diff on sleep-freq, over
{grid-8,16,24}) **or** a **strictly better** worst-BWT (real-diff) — plus acc/plasticity held. EMA-view reuses the P8
cache (read-side); LLRD builds its own cache per ρ (its own SCFF trajectory). N2-BAKEOFF + INV. **Internal-signals-only
affirmed.**

**Run.** 4 arms × {grid-8,16,24} × 5 seeds, `n2_readside` guard green (LLRD ρ=1 bit-for-bit; ρ<1 early/mid taps move
**0.00**, only late layers slowed → rate-only honest, no Stage-1 reopen). Wall ≈ 6.6 min.

**Result / figures.**
| N2-arm | drift-reduction | sleep-freq (@held A6) | accuracy-held | A6-BWT (worst) | plasticity | vs-no-N2 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no-N2 (P8 loop) | 0.000 | 0.022 [0.007–0.022] | 0.494 [0.478–0.502] | −0.317 [−0.439,−0.267] | 0.383 | (ref) | the baseline |
| EMA-view β0.3 | −0.035 | 0.022 | 0.488 [0.480–0.505] | **−0.383** [−0.383,−0.378] | 0.365 | worse BWT | not eligible |
| EMA-view β0.1 | −0.009 | 0.022 | 0.485 [0.480–0.504] | **−0.344** [−0.378,−0.294] | 0.377 | worse BWT | not eligible |
| LLRD-rate ρ0.5 | 0.000 | 0.022 | 0.495 [0.487–0.505] | −0.328 [−0.422,−0.256] | 0.378 | within noise | not eligible (no lever) |

- **N2-BAKEOFF** (headline): every arm holds the same sparsest cadence as no-N2 (sleep-freq 0.022 across the board —
  no arm sleeps sparser); no arm improves worst-BWT (EMA-view *worsens* it, LLRD is within noise); accuracy and
  plasticity are held. **No lever fires → N2 struck.** LDC annotated cited-not-built.
  - **INV**: all nine guards green; `n2_readside` LLRD ρ<1 early/mid-tap movement 0.00 (rate-only, no reopen).

**Read (8 slots).**
1. *Claim* — no N2 mechanism (EMA-view or LLRD-rate) holds A6 at a sparser cadence or a better worst-BWT than the
   committed loop; N2 is **struck** (standby → struck), and LLRD-rate is honestly rate-only (no Stage-1 reopen).
2. *Headline* — sleep-freq 0.022 for all arms (no sparser), worst-BWT no-N2 −0.317 vs EMA-view −0.383/−0.344 (worse)
   vs LLRD −0.328 (within noise), accuracy held (0.485–0.495) (n=5, lifelong stream). Internal refs only.
3. *Figures* — N2-BAKEOFF (drift-red × sleep-freq × A6-BWT × plasticity), INV (guards + LLRD rate-only check).
4. *Mechanism* — the drift is **rotation-only** (P9.0), and the grid-8 cadence already tracks it (all arms share the
   sparsest holding cadence) — so there is **no residual drift for N2 to slow.** EMA-view *hurts* because subtracting a
   time-varying birth-relative accumulator introduces a **train/eval frame mismatch**: the namer consolidates at sleep
   *t* in a frame the eval at the worst mid-stream point *t′* has already moved past — it adds effective drift rather
   than removing it. LLRD-rate is a genuine rate-only slowdown (early/mid taps unmoved, guarded), but slowing the late
   layers neither sparsens the cadence nor improves BWT — a null lever on this trackable drift. The choice reads a
   *direction*-preserving view (EMA-view subtracts a translation, not a rotation), so the strike is not a spine failure
   — it is that the lever has nothing to grip.
5. *Threats* — (a) the cosine-based `drift_red` is unreliable for a re-centring view (it shifts centroids toward the
   origin), so it is reported as a diagnostic only; the verdict keys on the *actual* worst-BWT and sleep-freq. (b)
   stream-schedule dependence — the worst-BWT read is at the awake gate's worst mid-stream point. (c) LLRD tested only
   at ρ=0.5/late=4; a deeper slowdown is a different arm, but the null lever + the rotation-only drift make a win
   unlikely. Rule-1: one variable (the N2 mechanism) swept; cadence is a controlled sub-axis read as a separate hold.
6. *Decision* — **N2 struck.** The decision-record knob N2 (EMA-view / drift-slowdown) resolves standby → struck; the
   P8 cadence's drift-conditionality is discharged (the cadence is *not* drift-bound here — the drift is trackable).
   P9.2 therefore tunes the consolidation depth on the **un-slowed** drift (no N2 to inherit); P9.5 assembles no N2.
7. *Freeze-honesty* — **internal-signals-only affirmed** (no P10 BP+replay number consulted). The economy is untouched
   (N2 struck → GD-share unchanged, well under 0.25); the meter is the P8 ADC-centred behavioral model.
8. *Live-safety* — N2 struck means the assembled loop carries no N2, so live-safety is exactly the committed loop's
   (carried to P9.5). LLRD's representation guard (early/mid taps 0.00) proves the flagged secondary would have been
   rate-only had it won — the honest boundary held.
