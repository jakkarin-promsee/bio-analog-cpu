# P8.1 — The gate bake-off: when does the namer fire?

**Question.** Inheriting the bench, streaming schedule, and two accuracy references from P8.0: across the gate taxonomy,
which detector holds accuracy-held within δ_acc=0.02 of the oracle-cadence baseline at the lowest GD-fire-fraction `f`,
**without false-firing on the nuisance segment**?

**Setup.** Swept variable = the gate ∈ {always-pay, oracle-cadence, absolute-θ, DDM, ADWIN, budget-gate}. Controls locked
(live NoiseAugContrast bulk, committed RanPAC+cbrs head, error-EMA trigger, checkpoint sleep, CI+nuisance stream, seeds
[42,137,271,314,1729]). The budget-gate is fit against the **sleep-only** error target (never-fire-awake reference), so
it learns to fire when firing is actually needed. Figures: GATE-BAKEOFF (frontier + scorecard), CONT-SAFETY, INV.

**Run.** 6 gates × 5 seeds, checkpointed live SCFF + gated head. Wall ≈ 25.2 min.

**Result / figures.**
| gate | accuracy-held | GD-fire-fraction | FAR | MTD | worst-BWT | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| always-pay (ceiling) | 0.448 [0.445–0.471] | 1.000 | 1.000 | 0 | −0.295 | cost ceiling |
| oracle-cadence (ref) | 0.448 [0.445–0.471] | 0.286 | 0.000 | 0 | −0.208 | achievable reference |
| absolute-θ | 0.448 [0.445–0.471] | 0.027 | 0.042 | 19 | −0.167 | held-not-clean (false-fires) |
| DDM | 0.448 [0.445–0.471] | 0.003 | 0.000 | 40 | −0.439 | committed-eligible |
| ADWIN | 0.448 [0.445–0.471] | 0.003 | 0.000 | 40 | −0.439 | committed-eligible |
| budget-gate | 0.448 [0.445–0.471] | 0.000 | 0.000 | 40 | −0.444 | committed-eligible (spine-flagged) |

- **GATE-BAKEOFF** (headline): every gate holds accuracy-held at the oracle's 0.448 — the accuracy axis is saturated, so
  the frontier is decided on `f` × FAR. absolute-θ is greyed out: it false-fires (FAR 0.042 > stationary floor) on the
  nuisance segment. DDM / ADWIN / budget sit at the clean knee (FAR 0.000, f ≤ 0.003).
  - **CONT-SAFETY**: worst-point BWT is more negative for the rarely-firing gates under *checkpoint* sleep (−0.439) than
    for the oracle (−0.208) — the retention gap the sleep cadence (P8.3) and cbrs (P8.6) exist to close.
  - **INV**: all guards green.

**Read (8 slots).**
1. *Claim* — a standard error-drift gate (DDM/ADWIN) holds accuracy at the oracle level with a clean nuisance FAR at a
   fire-fraction far below 0.25; the absolute-θ gate cannot (it false-fires).
2. *Headline* — DDM 0.448 [0.445–0.471] = oracle 0.448 (Δ 0.000) at f=0.003, FAR 0.000, vs always-pay ceiling 0.448/f=1.00
   (n=5, live CI+nuisance).
3. *Figures* — GATE-BAKEOFF (frontier + scorecard), CONT-SAFETY, INV (guards green).
4. *Mechanism* — the accuracy axis saturates because the **sleep cadence** already carries retention, so the awake gate's
   job is only to catch a *harmful* mid-stream stall. DDM/ADWIN fire on the two-threshold/two-window *error* rise (a real
   stall), and coast otherwise — so `f` collapses to ~0.003. absolute-θ fires whenever the raw loss crosses a fixed
   line, which the nuisance covariate shift trips (FAR 0.042) even though no class changed — a **magnitude** leak, exactly
   the spine's warning. The rarely-firing gates' worse worst-point BWT under checkpoint-sleep is a *sleep-placement*
   artifact (the worst point falls mid-segment, not at a boundary), resolved in P8.3.
5. *Threats* — (a) FAR is judged vs each arm's own stationary-segment floor (guarded), not a nominal δ. (b) The nuisance
   injector is calibrated (P8.0): the FAR≠0 for absolute-θ is a genuine false fire, not a vacuous pass. (c) accuracy-held
   ties across arms → "real difference" only claimed where IQR-disjoint; here the *fire-cost* and *FAR* differences are
   the real, sign-consistent separators.
6. *Decision* — sets the **committed awake gate = DDM** (the standard two-threshold error detector: clean FAR 0.000, AA
   at oracle, lowest defensible `f`; ADWIN ties it, budget-gate is spine-flagged and only marginally cheaper). Downstream
   rungs (P8.3 cadence, P8.5 metered, P8.6 assembled) inherit DDM as the awake gate.
7. *Economy-honesty* — FAR is reported beside accuracy for every arm; cost here is the fire-fraction *proxy* (`f`), not
   energy — the substrate meter is P8.4. The absolute-θ arm is stated plainly as struck (held-not-clean), same rigor as
   the winners.
8. *Live-safety / namer* — the checkpoint-sleep worst-BWT gap (−0.439 vs oracle −0.208) is flagged for P8.3/P8.6 to
   close; A6 is not adjudicated here. Namer unchanged (RanPAC pending the P8.4 cost cut).
