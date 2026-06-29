# P5.6 — preservation (frozen near-identity residual): SKIPPED (conditional run-condition not met)

*Pre-registered as **conditional** — design.md §3 P5.6: "run **iff** P5.1+P5.4/5.5 leave a gap" — with STOPPING
MARK ② ("preservation makes depth safe to read, not unbounded to use — a cheap test, not a tier of commitment").
The gap test came back: **no gap that preservation uniquely closes survives.** This is a documented decision, not an
oversight (cf. the intentional P2.3/P2.4 gap), and it is reversible — the build is specified in §6 if a later rung
re-opens the need.*

**The decision.** **Do not build/run the frozen residual.** Methodology rule #6 ("defer fallbacks until baseline is
characterized") governs: preservation is a *remediation* for the decay's **multiplier** (deep layers overwriting the
extractor), tested only if a gap survives the cheaper levers. Three measured results say it does not:

| evidence | what it showed | why it closes the gap preservation targets |
| --- | --- | --- |
| **P5.1** (temp0.2) | the mixed-task corruption un-corrupts 0.475 → **0.697 ≈ w12 0.708**; headroom tail 0.435 → 0.530 | the **overwrite** preservation targets is already mostly undone by the *objective* (sharper temp keeps each update on the class manifold) — the multiplier is small at temp0.2 |
| **P5.3** (lost-or-rotated) | decay is **lost, not rotated**, but **small** (~0.02 at temp0.2); placement sidesteps it | preservation would buy only ~0.02 on headroom, and only if it could *restore* lost info (it can't — frozen-init preserves, it doesn't recover) |
| **P5.4 / P5.5** | per-depth heads read the sharp depth on headroom (placement); on the **flat home** the issue is **pooling-vs-placement, not decay-overwrite** — truncation L2–3 is the cheap fixed reader | the deployed reader (truncation / all-tap, P5.5) **sidesteps** the deep tunnel entirely — there is no "read the top" requirement for preservation to enable |

**Why preservation can't help where it would matter.** Preservation's premise is "carry the extractor to the top so
*read-top = read-extractor*." But (a) the **deployment doesn't read the top** — P5.5 ships a *short* fixed stack
(truncation L2–3) or all-tap, neither of which needs the top preserved; and (b) on the continual flat home the gap is
**not** decay-overwrite (the per-depth heads are weak-but-decorrelated, P5.5) — a near-identity skip changes *which*
features survive, not the **pooling-beats-single-depth** fact that dominates there. And the **S5-norm × residual**
interaction (design §6) — a length-norm after a near-identity skip projects onto the unit sphere, discarding magnitude
*along* the preserved direction — is a *direction-vs-magnitude* hazard (the spine) that risks a new sign/direction bug
(the project's recurring killer) in the windowed-InfoNCE backward, for a ≤0.02 upside. Not worth the backward-path risk.

**STOPPING MARK ② — taken.** Preservation was always "a cheap test, not a tier of commitment." The cheap test's
*precondition* (a surviving gap) is absent, so the test isn't run. The committed cell carries **no residual**; the
final model's depth-reading is **placement (headroom) / fixed-short-read (continual home)**, not preservation.

**Reversibility (the re-open trigger).** Build `FrozenResidual` (design §6: `y = x + α·f(x)`, α frozen = 0.1, per-block
α→0 ablation, FD-guarded) **iff** P5.8/P5.9 surface a decay that (i) is large on *natural* flat data **and** (ii) the
deployed fixed reader cannot sidestep. Until then: **skipped, by decision.**

**Ledger.** No `arrays.npz` / figure (nothing run). `RESULTS.md` carries the skip row. P5.9 records the decision in the
assembled-cell verdict (the final cell has no residual term).
