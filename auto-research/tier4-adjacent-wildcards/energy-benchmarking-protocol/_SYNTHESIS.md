# Synthesis — Honest energy benchmarking for training  (Tier 4, closes the tier)
**The question:** What is the defensible protocol to measure + report our energy advantage so the comparison survives review — and what are the standard traps a reviewer will attack?
**Already carded (t1.1):** Spyra & Dzwinel 2025 (forward-only ≠ energy-efficient) — the shock that forced our win onto the substrate. **Already in our repo:** P8.7 (the 2×2 substrate ablation: 15.4× = 5.4× substrate × 2.9× algorithm), P10 R1 (the honest same-substrate loss: the 80/20 algorithm alone costs 1.5× *more* than a small tuned ER; the chip's 3.4× is the analog crossbar, not the algorithm), P11 (substrate factor grows 5.4→7.4× with width). This topic hardens *how that is reported*, not the result itself.

## The landscape (the four camps)
**1. Reporting-norm camp (Green AI, Strubell).** Make efficiency a first-class, reported metric alongside accuracy; disclose a cost number (FLOPs / a "price tag") for every result. Establishes the *duty to report cost*, and — via Strubell — the distinction between one-run cost and the whole development/search campaign.

**2. Measurement-tooling camp (Henderson experiment-impact-tracker, Dodge cloud carbon, MLPerf Power).** *Measure joules, don't estimate them from FLOPs.* Real energy = live power × time × PUE, attributed to the process; system wall-power ≠ chip-only ≠ FLOP-derived. MLPerf adds the rules that make measurements *comparable* (fixed quality target, defined window, no favourable operating point) and Dodge adds the marginal/context caveat (energy is the invariant; carbon is a context multiplier).

**3. The-metric-lies camp (Dehghani "Efficiency Misnomer").** Any single cost proxy (params, FLOPs, latency) can rank models *oppositely* to another. Report multiple indicators and compare at a matched quality point, or your efficiency claim is proxy-shopping.

**4. Physics camp (Horowitz, Gholami).** Data movement, not arithmetic, dominates energy (~1000× per off-chip access in 2014; the gap has *widened* since — FLOP/s scales 3×/2yr vs bandwidth 1.4–1.6×). FLOPs is therefore a *structurally* wrong proxy for a compute-in-memory substrate: it prices the term we delete and ignores the term we win on.

The camps converge on one recipe: **compare at matched accuracy, in a hardware-invariant energy quantity, with the data-movement term explicit, and with the algorithm factor separated from the substrate factor.** That is almost exactly what P8.7 + P10 R1 already do — the contribution of this topic is to name it, cite it, and pre-empt the attacks.

## How WE differ  ← the money section
Our energy claim is *already* the honest shape the literature demands, which is our strongest position: **we report the factor that goes against us (FLOPs/sample, where the algorithm loses to ER; P10.0) and split the win into algorithm (2.9×) × substrate (5.4×) rather than fusing them into one flattering number.** No paper in this folder would call that proxy-shopping — it is the opposite.

Two genuine gaps remain, both about the *instrument*, not the claim:
- **Our meter is modeled, not measured.** Henderson/Dodge/MLPerf all derive authority from a wattmeter on real silicon; ours is a *behavioral relative-pJ model, ADC-centred, explicitly NOT SPICE*, on a chip that does not exist. We cannot borrow their authority — we can only borrow their *rules*. The honest framing: **our numbers are relative ratios at matched accuracy under one transparent model; absolute joules are deferred to the analog-realism (SPICE/PVT) layer.**
- **Our accounting boundary is unstated.** Strubell's single-run-vs-search distinction applies: the 11-phase sweep that produced the frozen object is uncounted; only the deployed loop is metered. That is defensible *if declared* (steady-state deployment cost), invisible-to-attackable if not.

Where we are *ahead* of the landscape: our training is a **continual per-step rate**, not a one-shot batch cost, so the train-vs-inference conflation trap largely dissolves for us — but only if we quote a *rate* (pJ/sample) and never compare it to a lump-sum training budget.

## THE RECOMMENDED REPORTING RECIPE (the deliverable)
Report our energy advantage as a **five-line disclosure**, in this order, at a **matched accuracy/retention point**:

1. **Iso-accuracy gate first.** State the matched quality target (e.g. the P10 continual-home tie 0.494 vs 0.498, or a fixed retention level) *before* any energy number. Energy is only comparable at equal task performance — this is the MLPerf/Dehghani principle. Never report energy at an accuracy the opponent doesn't reach.
2. **The load-bearing quantity = same-substrate joules-ratio at that point.** `E(OURS-digital) / E(ER-digital)` — the hardware-invariant, algorithm-only comparison. Report it *even when it loses* (it does: 1.5× worse — P10 R1). This is the number that survives, because it isolates the algorithm from the substrate (Dodge's "invariant × context" structure).
3. **The substrate factor, separately labelled.** The analog / compute-in-memory multiplier (5.4×, floor ≥2.7×), quoted *in Horowitz/Gholami currency* — i.e. broken into "arithmetic term (unchanged) + data-movement term (deleted by resident-weight compute)." Never multiply it into line 2 to make a single headline; keep it a declared context factor.
4. **Multi-indicator honesty.** Disclose FLOPs/sample (where we lose), bytes-moved, and relative-pJ side by side (Dehghani). If the ranking is stable across pJ and bytes-moved but not FLOPs, that *is* the argument that FLOPs is the wrong proxy for this substrate — say so explicitly.
5. **Scope + boundary statement.** Declare: (a) the meter is behavioral/relative, not SPICE, absolute joules deferred; (b) the boundary is the deployed steady-state loop, not the design-time sweep (Strubell); (c) it is a continual *rate*, not a one-shot budget.

If a claim can't be stated in these five lines, it isn't ready to report.

## The top reviewer traps to pre-empt
- **"You reported pJ because FLOPs go against you."** → We report FLOPs anyway (P10.0); pJ is the decision-relevant indicator for a chip; the divergence is *predicted* by Dehghani + Horowitz, not hidden.
- **"You ignored data movement."** → It is the *entire* substrate win; priced in Horowitz/Gholami currency (line 3).
- **"Your energy is modeled, not measured."** → Correct; we claim only relative ratios at matched accuracy under a stated model; SPICE/PVT deferred (Henderson/MLPerf authority not invoked).
- **"Cherry-picked operating point."** → Matched-accuracy gate (line 1) + declared cadence cost-axis (P10.2) fix the operating point before energy is read (MLPerf rule).
- **"Train vs inference / one-run vs whole-campaign conflation."** → We quote a continual per-step *rate* for the *deployed loop*; the design-time sweep is explicitly out of scope (Strubell).
- **"Is the win just the substrate, applicable to any algorithm?"** → Yes, and we *say so* (P8.7: the 80/20 is substrate-independent; the substrate helps everyone). The algorithm's separate value is safety/noise/continual-stability, not energy — banked as two halves (P10).

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| Dehghani 2022 — Efficiency Misnomer | ⭐⭐⭐⭐⭐ | Single cost proxies rank models oppositely → report multiple, compare at matched accuracy (legitimises our FLOPs-lose/pJ-win split). |
| Horowitz 2014 — Computing's Energy Problem | ⭐⭐⭐⭐⭐ | The pJ table: off-chip access ~1000× a MAC → the physics under "the win is the substrate." |
| Schwartz 2020 — Green AI | ⭐⭐⭐⭐ | Efficiency as a first-class reported metric + the "price tag"; the norm we exceed — but its FLOP proxy is the trap. |
| Henderson 2020 — Systematic Reporting | ⭐⭐⭐⭐ | Measure-don't-estimate + full-accounting template; the bar our modeled meter must be scoped against. |
| Tschand 2024 — MLPerf Power | ⭐⭐⭐⭐ | Fair-comparison rules: quality-target-first (iso-accuracy), wall-power not chip-only, no favourable operating point. |
| Strubell 2019 — Energy & Policy (NLP) | ⭐⭐⭐⭐ | Single-run vs whole-development-campaign boundary; train-vs-inference conflation named. |
| Gholami 2024 — AI and Memory Wall | ⭐⭐⭐⭐ | The movement gap has *widened* (3×/2yr vs 1.4–1.6×) → our "substrate factor grows with scale" (P11) has an industry mechanism. |
| Dodge 2022 — Carbon Intensity of AI (cloud) | ⭐⭐⭐ | Energy = invariant, context = separate multiplier; the reporting shape for algorithm-joules × substrate-factor. |

## Leads spawned
- **Roofline / operational-intensity reporting** — express our meter as arithmetic-intensity so "movement-bound vs compute-bound" is a figure, not a claim.
- **Continual "energy-to-retention" protocol** — an MLPerf-Training-style quality-target-then-measure adapted to lifelong retention (our natural iso-accuracy axis).
- **A published analog-crossbar / PIM energy model** (memristor/CIM macro papers) to anchor the substrate factor in measured device data, not just Horowitz's digital table — the bridge to the analog-realism layer.
- **Luccioni 2024 "Power Hungry Processing"** — measured task-level energy corpus, if we ever want an external measured comparison point.
