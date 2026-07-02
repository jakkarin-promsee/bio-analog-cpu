# Phase 9 — close & *freeze* the maintenance loop (signpost)

You're in **Phase 9** of draft 6.0's **Stage 2** (the GD namer) — **✅ COMPLETE & FROZEN (ran 2026-07-02, P9.0→P9.5, all nine
guards bit-exact).** The **third** of four Stage-2 phases (P7 readout · P8 economy+cost · **P9 maintenance/close** · P10
validate/showcase). Phase 8 turned both brains on and metered the economy; **Phase 9 tuned the five still-open knobs of the
lifelong maintenance loop against *internal* signals, then LOCKED the object** so Phase 10 can race it fairly. Discipline:
**freeze in P9, judge in P10.**

- **Verdict — the maintenance loop is frozen, and it is safer than what P8 shipped (🔥):** the founding assumption is
  *discharged* (the SCFF bulk **rotates but does not forget** on a true lifelong stream), four of five open knobs resolved to
  *keep the committed loop*, and the freeze itself surfaced — and closed — the one real gap: the P8 sleep cadence was too
  sparse for a lifelong revisit stream. The frozen loop holds worst-point BWT at **−0.028** (ties the boundary oracle, 0/5
  seeds regress) vs the shipped grid-8 loop's **−0.317** on the same stream, at AA 0.494 and metered GD-share **0.178 ≤ 0.25**.
- **P9.0 — the risk gate (measured, not assumed):** on a lifelong CI+revisit stream, an optimal probe **re-fit** on the current
  bulk holds ≥ its birth score on held-out early-task data throughout (destruction curve final 2.2×, min 0.966), while a
  *fixed* head fit at birth rots to ~0.07. **Rotation, not forgetting** (Davari 2203.13381 protocol) — the cheap-replay story
  holds; N2 is *not mandatory*.
- **P9.1 — N2 STRUCK.** No read-side arm (EMA-view / LLRD-rate) sleeps sparser or improves worst-BWT; EMA-view *worsens* it
  (train/eval frame mismatch). The drift is rotation-only and already tracked, so N2 has nothing to grip. LLRD is honestly
  rate-only (early/mid taps unmoved — no Stage-1 reopen). The last open decision-record knob resolves standby → struck.
- **P9.2 — keep ALL-TAP consolidation.** Truncated sleep re-fits are 12–52× cheaper but forget more under live lifelong drift
  (worst-BWT −0.511/−0.373 vs all-tap −0.317, beyond δ_acc); all-tap's capacity earns its keep (S7 extended).
- **P9.3 — CBRS committed (S13-candidate).** At a pressure-point cap the bound bites (no bounded policy matches the unbounded
  oracle — a property of the cap). CBRS is the **best-bounded** policy: it ties the herding null (a **buffer-spine null** —
  density≈class here) and decisively beats reservoir/recency (−0.400 vs −0.607/−0.707); the holding cap **grows with #classes**
  (scaling law). GSS not raced (gradient-free); D-CBRS hand-rolled (no sklearn — the phantom-hang).
- **P9.4 — read-side residual RESOLVED read-side.** The Phase-6 input-transducer directional residual really dents the
  committed SLDA loop (gate fires: dent +0.115, 5/5; worst seed retention 0.504); **prototype re-anchoring** from the raw LUT
  (the plan's own sleep mechanism, direction-grounded) restores retention to **0.986** — the residual is defended, not named to
  the analog layer. The Phase-6 "scoped-YES → Stage-2 read-side" debt is discharged.
- **P9.5 — assemble + FREEZE.** The first assemble (inherited grid-8 = the shipped object bit-for-bit) **failed the oracle-veto
  2/5** on the lifelong stream (deep pre-sleep troughs between sparse sleeps). The freeze-driven **cadence re-confirm** (the P8
  drift-conditional debt; full frontier `{2,4,5,6,8,16}`) found the **freeze band is grid-2→grid-6**; **grid-4 is the knee**
  (best absolute worst-BWT of the frontier, −0.028, at GD-share 0.178 — grid-5/grid-6 are cheaper viable options). The two
  failures split by axis: grid-8 fails the **veto**, grid-16 (over-sparse) fails **AA-held** (AA 0.458, not random). Re-frozen
  at grid-4: veto 0/5, AA held, GD ≤ 0.25 → **FROZEN.**
- **Two things the sims overturned:** (1) the live diagnosis that the worst-point gap was the committed gate's *fire-timing*
  (unfixable in P9) — denser **sleep** closed it entirely, because frequent consolidation makes the fire-timing irrelevant;
  (2) the plan's guess that the read-side defense would need an SLDA **covariance** re-estimate — **proto-reanchor** (no
  covariance) fully recovers the residual.
- **The spine, still travelling (9th coat):** eviction keeps class *directions* (CBRS), not the dense *mean* (herding, the
  null); the read-side calibration re-anchors a *direction*, never an entropy/confidence *magnitude*. density ≠ class.
- **Honest scope / owed → Phase 10 (unchanged by the freeze):** the fair same-budget **BP+replay *accuracy*** baseline (the
  existential test), natural multi-class **A5**, the multi-domain gauntlet, the noise showcase (a **held-out** battery — P9.4
  tuned only on the home residual). The cadence knee (grid-4) is drift-rate-conditional (revisit-density dependent). The meter
  is **behavioral** (relative-pJ, ADC-centred, NOT SPICE).
- **The front door (read this first):** [`README.md`](README.md). **Deep story + every figure:**
  [`phase9-report.md`](phase9-report.md). **Numbers:** [`RESULTS.md`](RESULTS.md). **Per-rung:**
  [`expK/experiment-K.md`](exp0/experiment-0.md). **Spec:** [`design.md`](design.md); contract [`result-format.md`](result-format.md).
  **Apparatus:** `p9lib.py` (+ `p9cfg.py`, `p9run.py`, `plot_p9.py`); the frozen object's manifest: `exp5/figs_p9_5/manifest.json`.
- **Owed deltas (flagged, banked to [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) as S13):** N2 resolved
  (struck), S7 extended (all-tap depth + grid-4 lifelong cadence), the bulk-drift assumption **measured** (rotation-only),
  eviction = CBRS (S13), the read-side residual **resolved** (proto-reanchor), and the **frozen object** = the Stage-2
  maintenance close-out.
- **Read-budget:** for the verdict read `README.md`; for numbers `RESULTS.md`. Open cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 8](../phase8/README.md) · next → [Phase 10 —
  the validation / the showcase](../phase10/design.md) (races the frozen object).
