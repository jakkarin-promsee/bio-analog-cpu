# Phase 7 — the readout / namer: put our labels on the frozen bulk (signpost)

You're in **Phase 7** of draft 6.0's **Stage 2** (the GD namer) — **✅ COMPLETE (ran 2026-07-02, P7.0→P7.6, all
guards pass).** The **first** of three GD-stage phases (P7 readout · P8 economy+cost · P9 maintenance). Phase 7 names
the frozen Stage-1 cell: SCFF sorted the world into "kinds of things"; **P7 puts *our* names on the kinds** — read-only
on the frozen `NoiseAugContrast` bulk (GD reads taps, never writes; the P2.5 envelope held).

- **Verdict — the 20% is NOT gradient descent (🔥):** the committed namer is **RanPAC** — a **no-gradient, closed-form
  analytic head** (frozen random ReLU projection → running-Gram ridge prototype). On the continual home it **ties the
  gradient MLP anchor** on accuracy×BWT (a 3-way statistical tie {MLP, RanPAC, SLDA}, mutually within-noise), has the
  **highest static accuracy**, **passes the A6 continual-safety gate**, and is the most spine-clean of the tied cluster.
  Ships with a **class-balanced-reservoir (cbrs)** imbalance guard.
- **The spine bends (honest):** the spine-pure **cosine** head is direction-clean (argmax-flip 0.000) but
  **sub-competitive** on the synthetic home (**magnitude-wins-spine-bends**, Δ=0.128 vs δ=0.02). On **natural digits**
  the price **shrinks** (cosine ≈ competitive). The winner (RanPAC) reads a *magnitude* (ridge) but is recency-robust
  by having **no trained softmax weights** — recency-robust ≠ direction-reading (density≠class, 8th coat).
- **Two design guesses the sims overturned:** (1) **AIR is NOT the no-gradient imbalance guard** — it over-corrects;
  the reliable guard is **class-balanced reservoir (buffer-side)**. (2) The multimodality "cliff" is **not**
  multimodality (natural features are unimodal, n-modes 1.0) — it's an **anisotropic metric**; a **tied covariance**
  (closed-form) is the +0.19 lever, **no non-convex mixture needed**.
- **The RanDumb control (not pre-excused):** the trained bulk **beats a random projection of raw pixels** for every head
  (earns its keep vs raw input); it **ties a random *expansion* of its own taps** for a plain linear namer (the expected
  ELM effect) and **wins it for the ridge head** — so RanPAC's committed value over a random projection is verified.
- **Cost caveat → Phase 8:** RanPAC's projection cost proxy is ~200× SLDA's; **SLDA is a within-noise, far cheaper
  no-gradient alternative** (passes the gate too, but more norm-sensitive). Cost is **descriptive-only** in P7 (never a
  tie-break) — P8 prices it and may prefer SLDA.
- **The front door (read this first):** [`README.md`](README.md). **Deep story + figures:** [`phase7-report.md`](phase7-report.md).
  **Numbers:** [`RESULTS.md`](RESULTS.md). **Per-rung:** [`expK/experiment-K.md`](exp0/experiment-0.md). **Spec:**
  [`design.md`](design.md); contract [`result-format.md`](result-format.md). **Apparatus:** `p7lib.py` (+ `plot_p7.py`, `p7cfg.py`).
- **Owed at close (flagged, deltas to bank):** `idea/main.ideas.v1.md` — **N3** superseded (single frozen bulk +
  read-only namer, boosting dropped), **S4** collapses to one GD organ (the namer), **S9** extended with the committed
  *head* (RanPAC), + a new supporting decision (*the namer is a closed-form/streaming analytic head, not gradient
  descent — the "20% GD" is a role, not a method*). Stage-2 brief to Phase 8/9: the cost meter's target heads
  (RanPAC vs SLDA), the read-side noise residual (Phase-6 brief, still owed), the cbrs guard to carry.
- **Read-budget:** for the verdict read `README.md`; for numbers `RESULTS.md`. Open cards/code only to modify.
- **Up:** draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · prev → [Phase 6](../phase6/README.md) · next → Phase 8 (economy + cost).
