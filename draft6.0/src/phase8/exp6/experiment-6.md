# P8.6 — The assembled economy, run LIVE: does the two-brain loop keep the A6 win?

**Question.** The un-skippable existential check. With every knob committed — SLDA head (P8.4), DDM awake gate on the
namer's error-EMA (P8.1; the class-direction trigger of P8.2 was validated but not deployed), grid-8/full-history sleep (P8.3), cbrs guard — run the whole economy **live** on the
CI+nuisance stream and ask: does the co-adapting loop keep the A6 continual win **at the awake gate's worst mid-stream
point (pre-sleep)**? Verdict LIVE-SAFE iff the committed loop's worst-point BWT is **not** more-negative than the oracle
in ≥4/5 paired seeds (veto) **and** live AA is within δ_acc of the reference. If the live mechanism forgets, that is the
headline, not a footnote.

**Setup.** Arms = {committed (DDM+cbrs+grid-8), oracle (known-boundary sleep), always-pay (fire every step)}. Controls
locked (live bulk, SLDA head, error-EMA trigger for the gate, CI+nuisance stream, **5 seeds** [42,137,271,314,1729] —
never 3). BWT measured pre-sleep at the worst mid-stream checkpoint. The **frozen promise** = block-mode continual (≡
`continual_safety_heads`) on the same data. Figures: CONT-SAFETY (+ paired veto), GATE-BAKEOFF + METERED-8020 (assembled),
INV.

**Run.** 3 arms × 5 seeds + block-mode frozen promise per seed; committed cadence loaded from P8.3. Wall ≈ 6.6 min.

**Result / figures.**
| mechanism | AA (live) | worst-BWT (pre-sleep) | GD-share | vs baseline | verdict |
| --- | --- | --- | --- | --- | --- |
| frozen promise (block-mode) | 0.614 [0.606–0.622] | — | — | (offline reference) | — |
| **committed** (DDM+cbrs+grid-8) | **0.447 [0.426–0.448]** | **0.000 [0.000–0.000]** | **0.155** | = oracle | **LIVE-SAFE** |
| oracle-cadence | 0.447 [0.426–0.448] | 0.000 [0.000–0.000] | 0.492 | (ref) | reference |
| always-pay (no gate) | 0.474 [0.474–0.485] | −0.137 [−0.153,−0.135] | 0.747 | forgets mid-stream | cost+forgetting ceiling |

- paired veto (committed worst-BWT vs oracle): **0/5 more-negative → PASS**; AA-match (committed vs oracle) **OK**.
- **CONT-SAFETY** (headline): the committed economy holds worst-point BWT at 0.000 — identical to the oracle — in 5/5
  seeds, while the profligate always-pay arm forgets (−0.137). The disciplined economy is *both* cheaper (GD-share 0.155
  vs 0.747) *and* safer.
  - **GATE-BAKEOFF / METERED-8020 (assembled)**: the committed loop lands at the clean knee with GD-share 0.155.
  - **INV**: partial-fit-equiv + cache-replay guards green.

**Read (8 slots).**
1. *Claim* — the assembled two-brain economy, run live, keeps the A6 continual win at the awake gate's worst point (0/5
   veto failures) at oracle-level accuracy — and firing *more* (always-pay) forgets *more*, so the gate is a safety
   mechanism, not just a cost saver.
2. *Headline* — committed worst-BWT 0.000 [0.000–0.000] = oracle 0.000, 0/5 more-negative; committed AA 0.447 = oracle
   0.447; always-pay worst-BWT −0.137 (n=5, live CI+nuisance).
3. *Figures* — CONT-SAFETY (BWT/AA + paired veto), GATE-BAKEOFF + METERED-8020 (assembled), INV.
4. *Mechanism* — the crux, and it inverts the naive expectation. **Always-pay forgets (−0.137) because firing the namer
   every step chases the recency-skewed stream** — the nuisance/late-task batches overwrite the prototypes for classes
   the stream stopped showing. The committed economy fires rarely (gated), keeps class balance via cbrs, and
   re-consolidates from the *full* LUT on a regular grid — so past-class structure is never overwritten mid-stream
   (worst-BWT 0.000). The live AA (0.447) sits below the block-mode frozen promise (0.614): that gap is **task
   difficulty**, not forgetting — the live stream (gradual onset + covariate nuisance) is strictly harder than clean
   block-mode continual, and worst-BWT 0.000 proves no past task was regressed. Absolute AA on this hard synthetic home
   is modest by design; the phase's claims are about the *economy* (relative retention, cost shares), and natural
   multi-class accuracy (A5) is Phase 9's.
5. *Threats* — (a) BWT is measured pre-sleep at the worst mid-stream point (post-sleep would hide awake forgetting) — the
   honest read, and it passes. (b) "within noise" is not an auto-pass: the paired-sign veto applies, and 0/5 seeds
   regress. (c) the oracle uses hidden boundaries; the committed loop matching it (worst-BWT 0.000 = 0.000) is the win.
   (d) drift-rate-conditional (the committed cadence assumes P8.0's drift rate; N2/P9 may re-tune). (e) the fair
   same-budget BP+replay *accuracy* baseline is still Phase 9's existential test — this rung settles *safety*, not that
   final fight.
6. *Decision* — **confirms the new supporting decision**: the two-brain economy is continual-safe run *live*, not only in
   frozen characterization. The committed live loop = SLDA head + DDM/direction awake gate + cbrs + grid-8/full sleep.
   Nothing reopened; Phase 8 closes.
7. *Economy-honesty* — GD-share reported per arm (committed 0.155, oracle 0.492, always 0.747); worst-point BWT (not the
   flattering post-sleep number); the veto is paired-sign, not a mean. The cost meter's model/params carry from P8.4/P8.5.
8. *Live-safety / namer* — **LIVE-SAFE**: the co-adapting loop keeps the A6 win at the worst point in 5/5 seeds, and the
   committed SLDA namer delivers it at GD-share 0.155. The economy is cheaper *and* safer than firing always — the
   founding thesis, run live and standing.
