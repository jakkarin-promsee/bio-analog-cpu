# Phase 8 — the economy gate + the cost meter, run LIVE (signpost)

You're in **Phase 8** of draft 6.0's **Stage 2** (the GD namer) — **✅ COMPLETE (ran 2026-07-02, P8.0→P8.6, all seven
guards bit-exact; + P8.7 substrate-ablation EXTENSION added 2026-07-02).** The **second** of three GD-stage phases (P7 readout · **P8 economy+cost** · P9 maintenance). Phase 7
picked *what* the namer is (RanPAC + cbrs); **Phase 8 turned both brains on together for the first time** (SCFF learns
live forward-only; the namer tracks the drift via a gate + sleep), decided *when* the namer fires, and put the **first
honest hardware cost number** on the founding 80/20.

- **Verdict — the two-brain economy is real, cheaper *and* safer, run live (🔥):** with the committed gate on, the GD
  namer is **12.1% of total metered energy** (GD-share 0.121 ≤ 0.25 — the first non-proxy 80/20); off, it is 77.8% (the
  gate *creates* the split). OURS ≈ **half** the energy of BP+replay at matched retention (bp_ratio 0.501). And
  **LIVE-SAFE**: the assembled loop holds worst-point (pre-sleep) BWT at **0.000** (0/5 seeds regress vs oracle) at
  oracle-level accuracy.
- **The crux inversion:** **firing more forgets more.** always-pay (namer every step) forgets (worst-BWT −0.137) by
  chasing the recency-skewed stream; the disciplined economy (rare gated fires + cbrs + full-LUT sleep) does not (0.000).
  The gate is a **safety** mechanism, not just a cost saver.
- **The committed economy:** deployed head **SLDA** (P8.4: 69× cheaper than RanPAC, AA ties/beats live → resolves S11) ·
  awake gate **DDM** (P8.1: AA at oracle, FAR 0.000, f≈0.003) · trigger **class-direction tap-drift** (P8.2: MTD 6 < error
  14, excess-FAR 0.000, spine-clean) · sleep **grid-8 / full LUT history / λ_ema 1.0** (P8.3: cheapest holding A6) · guard
  **cbrs** · envelope unchanged (GD reads taps, never writes SCFF).
- **The spine, demonstrated:** the trigger fires on class **direction** (invariant to a nuisance covariate, 0.84×) not
  **magnitude** (the null spikes 10× and false-fires on 94% of nuisance steps) — density≠class, 8th coat.
- **WHY ANALOG (P8.7 extension, for the professor brief):** re-metered the exact committed loop + the fair BP+replay
  baseline on a **digital** (von-Neumann/GPU-class) substrate → the full **2×2**. The chip is **15.4× cheaper** than
  conventional GD-on-digital, factoring into **5.4× substrate** (compute-in-memory: the ~8e8 near-free crossbar MACs vs
  the digital memory wall, ~75× more MACs than ADC ops) **× 2.9× algorithm** (our gated forward-only loop vs BP+replay on
  the *same* digital substrate). The 80/20 is **substrate-independent** (GD-share 0.11–0.16); the analog advantage is a
  **floor** (≥2.7× even at arithmetic-only digital, →53× with the memory wall). Digital = behavioral (Horowitz-anchored,
  NOT an empirical GPU measurement). Card: [`exp7/experiment-7.md`](exp7/experiment-7.md); figure `exp7/figs_p8_7/SUBSTRATE.png`.
- **Two design guesses the sims overturned:** (1) the gate's value is **safety, not just cost** — always-pay forgets, so
  more GD is worse; (2) **regular cadence beats boundary-aligned sleep** (grid worst-BWT 0.000 vs oracle-boundary −0.439,
  because the worst point falls mid-segment, not at a boundary).
- **The one new primitive:** streaming **`partial_fit`** (running Gram `(G,M)` + `λ_ema`), guarded ≡ batch fit to 4e-15.
- **Honest scope:** the fair same-budget **BP+replay *accuracy*** baseline is still owed → **P9** (P8.5 settled *energy*,
  not accuracy); absolute AA on the synthetic home is modest (live 0.447 vs block-frozen 0.614 = task difficulty, not
  forgetting — worst-BWT 0.000); the committed cadence/gate are **drift-rate-conditional** (re-tune if P9's N2 slows the
  drift); the meter is **behavioral** (relative-pJ, ADC-centred, NOT SPICE); the read-side noise residual stays owed.
- **The front door (read this first):** [`README.md`](README.md). **Deep story + every figure:**
  [`phase8-report.md`](phase8-report.md). **Numbers:** [`RESULTS.md`](RESULTS.md). **Per-rung:**
  [`expK/experiment-K.md`](exp0/experiment-0.md). **Spec:** [`design.md`](design.md); contract
  [`result-format.md`](result-format.md). **Apparatus:** `p8lib.py` (+ `p8cfg.py`, `p8run.py`, `plot_p8.py`).
- **Owed deltas (flagged, banked to [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md)):** **S6** resolved (DDM
  gate + direction trigger), **S11** resolved (commit SLDA), the **metered 80/20** replaces the proxy tags, **S7**
  extended (grid-8/full/λ1.0 cadence), a **new supporting decision** (the live two-brain economy is continual-safe; the
  gate is a safety mechanism), **N2** stays Phase 9's.
- **Read-budget:** for the verdict read `README.md`; for numbers `RESULTS.md`. Open cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 7](../phase7/README.md) · next → Phase 9
  (maintenance + the owed BP+replay accuracy baseline).
