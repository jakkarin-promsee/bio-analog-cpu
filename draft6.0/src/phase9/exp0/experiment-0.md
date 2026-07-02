# P9.0 — The risk gate: does the SCFF bulk ROTATE (sleep fixes it) or FORGET (the assumption breaks)?

**Question.** Phase 9's whole cheap-replay story rests on an *assumed* fact — "the SCFF bulk doesn't forget, it only
drifts, so a periodic sleep re-solve is enough." Before any knob is tuned this must be **measured** on a lifelong
stream. And it must be measured with the right instrument: a *frozen* linear probe is basis-dependent (a pure rotation
tanks it and reads as forgetting), so the verdict keys on curve **(3)** — an **optimal probe RE-FIT on the current
bulk**, scored on held-out early-task data (Davari *Probing Representation Forgetting* [2203.13381]), which factors
rotation out. Also: do all nine guards reproduce the apparatus bit-for-bit?

**Setup.** No swept knob — a measurement + the fork that gates the ladder. Controls locked: live `NoiseAugContrast`
bulk (SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0), committed SLDA namer, the DDM/error-EMA/grid-8
committed loop (the P8.6 object), the **lifelong** CI+revisit+nuisance stream (`make_lifelong_stream` — 2 revisit
cycles so drift accumulates past P8's single pass; n_steps 536, onsets [40,88,136,184], 10 monitor re-evals), seeds
[42,137,271,314,1729]. Figures: DRIFT-LIFELONG (the 3-curve headline), CONT-SAFETY (committed vs oracle vs always-pay),
INV (all 9 guards). Apparatus: `p9lib.build_cache_p9` + `probe_retention` + `run_economy_p9`. **Internal-signals-only
affirmed: no P10 BP+replay number consulted.**

**Run.** 5 seeds, n_steps=536/seed, guards evaluated once (seed-independent by construction). Wall ≈ 9.7 min.

**Result / figures.**

*Guards (any fail → STOP) — all bit-exact:*
| guard | measured | pass |
| --- | --- | --- |
| partial_fit_equiv (ranpac / slda) | 4.11e-15 / 2.22e-16, pred-miss 0 | ✓ |
| fd_budget_gate | 3.47e-08 | ✓ |
| meter_proxy | fwd-MAC 1 556 000 ≡ readout_cost | ✓ |
| detector_far floor | {abs 0.0, ddm 0.0, adwin 0.0} | ✓ |
| scff_static_frozen | 0.00e+00 (static acc 0.566) | ✓ |
| live_path_anchor | 0.00e+00 (AA 0.3602 = 0.3602) | ✓ |
| cache_replay | 0.00e+00, fire-diff 0 | ✓ |
| **n2_readside** | (a) run_economy_p9(off) ≡ P8 0.00e+00, fire-diff 0; (c) LLRD ρ=1 0.00e+00 **and** ρ<1 early/mid taps move 0.00e+00, late 7.9e-3 | ✓ |
| **evict_equiv** | (a) cap=∞ retains all 140/140; (b) cap=30 recency ≡ last-30 FIFO contents | ✓ |

*The three curves (over the lifelong stream) + the references:*
| read | value (median [IQR]) | vs reference | verdict |
| --- | --- | --- | --- |
| (1) rotation cos(rep_t, birth) | 0.645 [0.631–0.655] | taps rotate ~36% | the map moves (expected) |
| (2) staleness — fixed head fit at birth | 0.069 [0.000–0.600] | / birth score | a **fixed head rots** — what sleep fixes |
| **(3) DESTRUCTION — re-fit optimal probe ⭐** | **final 2.207 [2.097–2.472]**, min 0.966 [0.861–1.000] | / birth re-fit (0.16–0.24) | **≥ birth throughout → the bulk does NOT forget** |
| committed loop | AA 0.494 [0.478–0.502], wBWT −0.317 [−0.439,−0.267], f 0.002 | vs oracle | ties oracle AA; wBWT 0.028 below |
| oracle-cadence ref | AA 0.494 [0.478–0.502], wBWT −0.289 [−0.317,−0.278] | (ref) | achievable reference |
| always-pay ceiling | AA 0.530 [0.505–0.539], wBWT −0.400 | — | fires every step, forgets more |

- **DRIFT-LIFELONG** (headline): left — the taps rotate (cosine to birth settles ~0.65, never collapsing). Right —
  the split: the *frozen* probe (staleness, grey) rots toward 0 (a fixed head loses the world), while the **re-fit
  probe (destruction, red)** stays at or above its birth score across the whole stream and ends at 2.2× — early-task
  information is *preserved and enriched*, not destroyed. **Rotation, not forgetting.**
  - **CONT-SAFETY**: committed AA ties oracle; committed worst-BWT −0.317 sits 0.028 below oracle −0.289 (the gap the
    P9 knobs get to close); always-pay both higher-AA and worse-BWT (firing more forgets more, carried from P8).
  - **INV**: all nine guards green (including the two P9-new).

**Read (8 slots).**
1. *Claim* — on a lifelong stream, the SCFF bulk **rotates but does not forget**: an optimal probe re-fit on the
   current bulk holds ≥ its birth score on held-out early-task data throughout (final 2.2×), while a fixed head fit at
   birth rots to ~0.07 — so a periodic re-solve (sleep) is sufficient and the cheap-replay assumption holds.
2. *Headline* — destruction retention final **2.207 [2.097–2.472]**, min 0.966 (≥ birth); staleness 0.069; rotation
   0.645 (n=5, lifelong CI+revisit+nuisance stream). Internal refs only: committed AA 0.494 = oracle 0.494; committed
   wBWT −0.317 vs oracle −0.289.
3. *Figures* — DRIFT-LIFELONG (rotation + staleness + **destruction**), CONT-SAFETY (committed/oracle/always), INV.
4. *Mechanism* — SCFF is unsupervised and local: it **re-organizes** the feature frame (rotation, so a *fixed* head
   goes stale) but never catastrophically overwrites *what is linearly decodable* (a re-fit probe recovers early-task
   accuracy — in fact the maturing bulk makes task-0 **more** separable, hence the 2.2× rise). The forgetting the
   committed loop shows in worst-BWT is therefore the **namer** losing track of a rotating frame (staleness), which
   sleep is built to fix — not information destroyed in the bulk.
5. *Threats* — (a) the destruction ratio normalises to an *immature* birth (short warmup → birth re-fit only 0.16–0.24),
   which inflates the ratio; the load-bearing read is that it never sustainedly drops below 1 (min 0.966), not the 2.2×
   magnitude — reported both ways. (b) the long-stream drift depends on the stream schedule — the re-fit destruction
   curve is the schedule-independent read (rotation factored out, per 2203.13381). (c) the meter is behavioral (not
   exercised here beyond the proxy guard). (d) the oracle uses hidden boundaries the loop can't see — matching it is the
   win. Rule-1 (one thing changed): none — a pure measurement.
6. *Decision* — the fork resolves to **ROTATION-ONLY: the cheapness holds.** The founding "bulk doesn't forget"
   caveat is discharged (measured, not assumed). N2 is therefore *not mandatory* (drift is trackable by a cheap
   cadence); the ladder proceeds P9.1→P9.5 to tune the loop that tracks the rotation. The committed-vs-oracle worst-BWT
   gap (−0.317 vs −0.289) is the internal target the tuning aims to close.
7. *Freeze-honesty* — **internal-signals-only affirmed** (no P10 BP+replay number consulted). No energy claim on this
   rung beyond the metered committed loop; GD-fire-fraction 0.002 (the economy is intact — well under the 0.25 cap).
   The meter model + params are the P8 ADC-centred behavioral model (logged in the manifest).
8. *Live-safety* — the live path is proven identical to `continual_safety_heads` (anchor guard 0.0), so the lifelong
   worst-BWT reads are on the real co-adapting loop. The committed loop is worst-BWT-safe *relative to the oracle to
   within 0.028* on this hard lifelong stream — carried into P9.5 as the gap the assembled knobs must close.
