# P11.1 — the decomposition: "Is it just SLDA?" (the strike-1 answer, pre-pitch)

**Question.** The namer is literature (SLDA/RanPAC). Until Δbulk = (bulk→namer) − (proj→namer) is measured, the
architecture claim is open to "a known closed-form classifier plus a gate." Does the SCFF bulk earn its place — and
if so, on which capability channel?

**Setup.** Cells (each a `build_cache_p9` factory): **bulk** = the committed cell · **proj** = an identity cell (NO
SCFF — the namer reads the frozen →40 porthole input directly, the strike) · **reservoir** = a random-frozen bulk
(12 nonlinear layers, never trained — separates "depth exists" from "SCFF learned"). 5 seeds. **Design deviation
(commented, per the author's leave to change the plan on the result):** the spec pinned P11.1 to the digits home,
but a pre-run diagnostic showed **digits are near-linearly-separable** (raw-SLDA 0.950) — a linear namer already
saturates there, so the bulk *cannot* add and the digits-only read would bank a misleading "the bulk is worthless."
The honest measurement sweeps arenas of **increasing nonlinearity** {synth-home (the P7/P10-validated arena) →
MNIST-40 → digits}, reporting Δbulk as a function of how much nonlinear structure the arena holds.

**Result — NARROWED WITH A MECHANISM (a decomposition of attribution, not a flat number).**

*Home-AA channel — Δbulk tracks nonlinearity (median, 5 seeds):*

| arena | proj→namer (no bulk) | reservoir (random 12L) | bulk→namer | Δbulk |
| --- | --- | --- | --- | --- |
| **synth-home** (nonlinear, 40 overlapping clusters) | **0.172** (≈chance) | 0.389 | **0.589** | **+0.417** |
| MNIST-40 (moderate) | 0.770 | — | 0.778 | +0.008 |
| digits (near-linear) | 0.950 | 0.902 | 0.936 | −0.014 |

*Noise channel — absolute noisy accuracy (iid σ1.0; the retention *ratio* is confounded — a near-chance proj
"retains" trivially, so absolute is the honest read):* synth bulk **0.367** vs proj 0.151 (**+0.215**); digits
bulk **0.245** vs proj 0.158 (**+0.086**, at matched clean — the P6 noise-augmentation earning its keep); MNIST tie.

*Continual-safety channel (gauntlet worst-point BWT):* **proj→namer forgets no more than bulk** — worst-BWT
digits 0.000 (proj) vs −0.016 (bulk); MNIST 0.000 vs −0.096. **The safety is closed-form + gate + sleep, not the
bulk.**

**Read (8 slots).**
1. *Claim* — the SCFF bulk is the **nonlinear feature learner**; the continual **safety** is the closed-form namer
   + gate + sleep. Two distinct organs, two distinct jobs — neither redundant, neither over-claimed.
2. *Headline* — Δbulk **+0.417** on the nonlinear home (0.172→0.589), **+0.086/+0.215** on iid-noise, **≈0 on
   near-linear digits**; the bulk beats a random 12-layer reservoir (0.589 vs 0.389) → **it is *learned* structure,
   not just depth**.
3. *Figures* — `DECOMP.png` (home-AA bulk/proj/reservoir across nonlinearity + the closed-form-safety panel).
4. *Mechanism* — a linear head reads a *magnitude*; where classes are linearly separable (digits) it saturates and
   the bulk has no headroom. Where they are not (the synth home is at chance under a linear read) the bulk's
   nonlinear taps are the only thing that lifts it. Safety is orthogonal: the closed-form namer never
   catastrophically forgets (unlike a gradient MLP), and the gate + sleep hold it — proj inherits all of that.
5. *Threats* — (i) **projection loss**: the →40 porthole itself linearizes/simplifies, shrinking the bulk's
   headroom on MNIST/digits (Arm B at D=80/160 in P11.2 bounds this); (ii) the noise retention-ratio is
   clean-baseline-confounded (reported as absolute); (iii) digits/MNIST gauntlet domains are *linear*
   reparametrizations (permute/rotate) that a linear head handles natively — they under-credit the bulk by
   construction.
6. *Verdict* — **NARROWED-with-mechanism** (not kill (i), not blanket-confirm): the strike lands honestly on
   *safety* (mostly SLDA+gate+sleep) and misses on *capacity* (the bulk is decisive on nonlinear data). The claim
   shrinks to a precise, defensible sentence.
7. *Recipe-honesty* — Arm A bit-equal committed (recipe-guard clean); nothing tuned; proj = a true no-bulk ablation;
   proj energy = namer-only E_gd (removing the bulk removes its cost — the strike lands twice on the energy axis:
   proj is ~140× cheaper). Reservoir = dim-matched control.
8. *Where-it-stands* — the LIMIT-MAP inherits a **Δbulk overlay** keyed to arena nonlinearity: the bulk earns its
   place where the data is nonlinear (real sensors, the synth home) and is honestly redundant where a linear head
   suffices. **The pitch answer to "isn't this just SLDA?": the *safety* largely is — we measured it and say so;
   the *bulk* is the nonlinear learner, and on data a linear head can't crack it is decisive and beats a random
   reservoir.** That is more credible than "we win everywhere."

*Kill criterion (i) did NOT fire (Δbulk > 0 on the nonlinear home + noise). Guards: recipe ✓ freeze-content ✓.*
