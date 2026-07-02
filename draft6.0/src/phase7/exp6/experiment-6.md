# P7.6 — synthesis + the committed readout (the assembled-head confirmation)

**Inheriting** the committed namer **RanPAC** (P7.1 winner, P7.4-gated, P7.5 natural-confirmed) + the P7.3 imbalance
guard **cbrs**, on the pinned bulk. **Question.** Does the *assembled* committed pipeline (RanPAC + cbrs) hold its P7.1
solo accuracy×BWT end-to-end (levers may not stack), and what is the phase's committed readout + numeric verdict?

**Setup.** Assembled = RanPAC {proj_dim 2000, ridge_lambda 1.0} + class-balanced-reservoir buffer (cap 2000) through
the continual harness on the synthetic home, vs RanPAC solo (the P7.1/P7.4 head). Bar (pinned): assembled AA below the
P7.1 solo AA (0.617) by more than the §B band (0.02) → revert the guard. Seeds ×5. Wall 44s.

**Result / figures.**

| pipeline | AA | BWT | vs P7.1 solo bar (0.617, band 0.02) |
| --- | --- | --- | --- |
| RanPAC solo | 0.617 | −0.157 | (bar) |
| **RanPAC + cbrs (assembled)** | **0.627** | **−0.132** | **+0.010 → HOLDS** |

- **CONT-SAFETY** (assembled): the guard is **non-degrading** on the balanced home (AA 0.617→0.627, BWT −0.157→−0.132,
  both *improve*) and P7.3 shows it fixes the bursty-skew regime. Levers stack. - **INV**: feat-pinned ✓.

**Read (8 slots).**
1. **Claim** — the assembled committed pipeline **RanPAC + cbrs holds** its P7.1 solo accuracy×BWT (AA 0.627 ≥ the
   0.597 bar; BWT improves) — the imbalance guard does not degrade the balanced home and rescues the bursty skew (P7.3).
2. **Headline** — assembled AA **0.627** vs solo 0.617 vs the P7.1 bar 0.617 (band 0.02) → **HOLDS +0.010** (n=5).
3. **Figures** — CONT-SAFETY (assembled vs solo), INV. Regen from `arrays.npz`.
4. **Mechanism** — cbrs balances the replay buffer before each analytic sleep-refit; on the already-balanced A6 buffer
   it is near-idempotent (a slight improvement from the cleaner per-class balance), and under the P7.3 recency skew it
   is the decisive fix. Because RanPAC is closed-form, "consolidation" is a re-solve on the (balanced) buffer — the
   guard composes with the head by construction, no optimizer interaction to destabilize.
5. **Threats** — (a) the guard flattering by discarding data → cbrs keeps cap/C per class within the cap budget (fair);
   (b) a lever-stacking regression hidden by the balanced home → P7.3 already stress-tested the guard under skew, and
   this rung confirms no degradation on the home; (c) over-reading a +0.010 gain → it is within-noise-positive, so the
   honest claim is "non-degrading," not "improves."
6. **Decision** — **the committed Phase-7 readout = RanPAC + cbrs** (no-gradient, A6-safe, natural-confirmed). The
   decision-record deltas are banked (N3 superseded, S4→one organ, S9 extended with the head, + the new "namer is
   analytic, not GD" decision). Handed to Phase 8: RanPAC vs SLDA cost trade; the read-side noise residual (owed).
7. **Spine-honesty** — the committed head reads a **magnitude** (ridge prototype); it is chosen because the direction-
   pure cosine is sub-competitive where the bulk has structure (P7.1/P7.5), and it is recency-robust by having no
   trained weights (P7.4). The spine bends here, numerically and named — not resolved silently.
8. **Namer-verdict / continual-safety** — **the committed namer is a no-gradient analytic head that keeps the A6 win**
   — the 🔥 Phase-7 headline. Spine-tension branch = **magnitude-wins-spine-bends** (synthetic; shrinks on natural).

**The Phase-7 verdict (pre-registered, natural-confirmed).**
- **Committed readout** = **RanPAC + cbrs** — maximizes accuracy×BWT on the natural-confirmed continual home (3-way tie
  with MLP/SLDA, spine tie-break), passes the A6 gate (P7.4), #1 on digits (P7.5).
- **Spine-tension outcome** = **magnitude-wins-spine-bends** (Δ = AA(RanPAC) − AA(cosine-softmax) = +0.128 synthetic,
  real 5/5, > δ=0.02; mechanism = recency-robust-by-no-trained-weights + the projection's separability). **Annotated:
  the price shrinks 4× on digits (−0.036) and vanishes on CIFAR-flat.**
- **RanDumb read** = the trained bulk **earns its keep** vs a raw-pixel random projection (all heads, P7.0); the
  taps-arm tie for a linear namer is the ELM effect (flagged), and RanPAC's projection beats plain RLS (+0.047).
- **Cheat-everything read** = **the committed namer is closed-form/streaming analytic — the "20% GD" is a role, not a
  method. The 20% is not even gradient descent.** 🔥

**Pre-submit checklist.**
- [x] Assembled head RUN end-to-end (not just synthesized); pass/fail bar (§B band) applied → HOLDS.
- [x] Median for headline numbers (n=5).
- [x] The committed readout + the numeric spine-tension branch + the RanDumb read + the cheat-everything read all stated.
- [x] Feature source loaded from the pinned P7.0 config; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (committed RanPAC + cbrs).
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded; no sklearn for compute.
- [x] Decision-record deltas flagged (not silently applied); README + report written.
