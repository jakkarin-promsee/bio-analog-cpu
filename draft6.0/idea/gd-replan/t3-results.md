# T3 results — the cheap-credit ladder ran; the decisive lever is OBJECTIVE SHARPNESS, not credit reach (2026-06-29)

> **What this is.** The autonomous research session you asked for ("find the way to solving this decay problem with
> our architecture"). It ran two pre-registered experiments on the P4.3 apparatus (L=12, W=64, per-layer linear probe
> to L12, **5 seeds** `[42,137,271,314,1729]`, headroom + flat), each guarded against this project's recurring
> sign-bug curse, plus a deep literature pass ([`lit-cheap-credit.md`](lit-cheap-credit.md)). Figure:
> `t3/figs_t3/T3_RESULTS.png`. Scripts: `t3/run_t3.py` (overlap + locality), `t3/run_topdown.py` (objective-side
> credit), `t3/plot_t3.py`.
>
> **Headline:** the cheapest lever that recovers composing depth is **not** credit-reach machinery (windows, overlap,
> top-down wires) — it is **sharpening the InfoNCE objective itself (temperature 0.5→0.2)**, which at the adopted
> depth-2 window **nearly matches full end-to-end backprop's composition at ~1/6 the backward cost.** Two candidate
> "cheap global credit" mechanisms (overlapping windows; a detached top-down loss term) were tested and **both
> failed** — clean, FD-verified negatives. The decay is, to first order, an **objective-sharpness** problem with a
> **free** fix, not a credit-assignment problem needing new wiring.

---

## The guards (the antidote to the project's silent killer)

Every result below is built on two checks that ran *before* any cell, so a sign/direction bug cannot masquerade as a
finding:

- **Overlap subclass ≡ tested cell:** `SCFFContrastOverlap(window=2,stride=2)` reproduces the tested
  `SCFFContrastOLU(window=2)` **bit-for-bit** (`max|ΔW| = 0.00e+00`).
- **Top-down gradient is correct:** finite-difference vs analytic gradient of the top-down layer loss
  **`max|analytic−FD| = 9.6e-08`** (< 1e-5); and **`λ=0` reproduces `window=1` bit-for-bit** (`0.00e+00`).

So the negatives are real negatives, not bugs.

---

## Result 1 — locality dose-response (non-overlap window sweep): bulletproofs T0.2 at 5 seeds, and on flat

Median over 5 seeds, headroom, the clean credit-reach axis (window = backward gradient-chain length):

| window | peak@L | peak | **tail-L12** | slope L1→L12 | readout acc | backward-work / w1 |
| --- | --- | --- | --- | --- | --- | --- |
| w1 (pure local) | 3 | 0.521 | **0.387** | −0.0013 | 0.393 | 1.0× |
| w2 (adopted) | 5 | 0.537 | **0.429** | +0.0029 | 0.449 | 1.9× |
| w3 | 6 | 0.542 | **0.469** | +0.0061 | 0.485 | 2.8× |
| w4 | 7 | 0.544 | **0.501** | +0.0098 | 0.515 | 3.8× |
| w6 | 6 | 0.550 | **0.525** | +0.0110 | 0.548 | 5.6× |
| **w12 (full e2e backprop)** | 12 | 0.549 | **0.549** | +0.0133 | 0.569 | 11.1× |

**tail-L12 rises monotonically with credit reach (0.387 → 0.549) and the slope flips negative→strongly positive.**
This is T0.2's locality verdict, now at 5 seeds with fine resolution: the ~5 ceiling is the forward-only locality cap;
the InfoNCE objective composes the *whole* stack under full credit. **It replicates on the flat task** (make_gauss,
known Bayes error): tail-L12 w1→w12 = 0.479 → 0.647 → 0.709 → 0.717, peak marching L2→L5 — same shape, easier task
peaks earlier (the "easy task → shallower extractor" prediction). The owed flat spot-check is **done and confirms**.

**Cost reading:** composing depth costs backward-chain length. w4 (depth-4, tail 0.501, 3.8×) is the efficient bounded
rung; w6/w12 buy little extra tail for a lot more cost. **But Result 3 beats all of them for free.**

## Result 2 — overlap is DEAD: credit-path multiplicity ≠ credit-chain length

Overlapping windows (stride < window) were the literature's "#2 cheap rung." Tested lr-matched (per-layer gradients
normalized by participation count, so the only change vs non-overlap is credit *reach*, not effective lr):

| cfg | backward depth | tail-L12 | vs non-overlap | backward-work / w1 |
| --- | --- | --- | --- | --- |
| w2 s2 (non-overlap) | 2 | 0.429 | — | 1.9× |
| w2 s1 (overlap) | 2 | **0.416** | **worse** | 3.5× |
| w4 s4 (non-overlap) | 4 | 0.501 | — | 3.8× |
| w4 s2 (overlap) | 4 | **0.491** | **worse** | 6.3× |
| w4 s1 (overlap) | 4 | **0.473** | **much worse** | 11.3× |

**Overlap slightly HURTS and costs much more.** w4s1 costs as much as full e2e (11.3×) for tail 0.473 (vs w12's
0.549). It replicates on flat (f_w2s1 0.501 ≪ f_w2 0.647). **Mechanistic lesson:** what composes depth is the *length
of a single gradient chain* (window width), not the *number of overlapping short chains*. Averaging two short-reach
local objectives at a layer blurs its target; it does not synthesize long-range credit. **Overlap is removed from the
ladder.**

## Result 3 — 🔥 the win: OBJECTIVE TEMPERATURE is a free lever that nearly matches the e2e ceiling

The contrast-strength control T0.1 flagged, now characterized at 5 seeds:

| cfg | backward depth | peak@L | tail-L12 | readout acc | backward-work / w1 |
| --- | --- | --- | --- | --- | --- |
| w2 temp 0.5 (adopted) | 2 | 5 | 0.429 | 0.449 | 1.9× |
| **w2 temp 0.2** | 2 | **8** | **0.539** | **0.550** | **1.9×** |
| w12 temp 0.5 (full e2e — ceiling) | 12 | 12 | 0.549 | 0.569 | 11.1× |
| w2 s1 temp 0.2 (overlap + temp) | 2 | 6 | 0.513 | 0.529 | 3.5× |

**Sharpening InfoNCE temperature 0.5→0.2 at the cheap adopted depth-2 window buys tail 0.539 / acc 0.550 — essentially
the full-backprop ceiling (0.549 / 0.569) — at 1.9× cost instead of 11×.** No architecture, no new wire, forward-only,
per-sample, SCFF-flow-safe. This is the cheap-credit win, and the surprise is *what kind* of lever it is: not credit
assignment at all, but the **discriminative sharpness of the local objective**. A sharper InfoNCE makes each layer's
update more class-selective, so the representation stops drifting off the class manifold with depth — the decay's
*cause* (local objective drift, [problem doc §3a](../phase4-problem.md)) is attacked at the source, for free.
(Note: overlap drags temp0.2 *down*, 0.539→0.513 — confirming Result 2 a third time.)

## Result 4 — naive top-down objective credit is DEAD (the cheapest objective-side fix does NOT work)

The literature's #1-ranked lever ([`lit-cheap-credit.md`](lit-cheap-credit.md) §D/§F): add a **detached top-down
consistency term** to each layer's local InfoNCE (CLAPP/InfoPro principle, preserve class direction). Tested at the
window=1 base (most-local, most-decayed → any lift is pure top-down credit at backward-depth 1), 5 seeds:

| cfg | reference | λ | peak@L | tail-L12 | readout acc |
| --- | --- | --- | --- | --- | --- |
| λ=0 (= w1, cross-check) | — | 0 | 3 | **0.387** | 0.393 |
| top λ0.5 | top (L12) | 0.5 | 3 | 0.341 | 0.340 |
| top λ1.0 | top (L12) | 1.0 | 2 | 0.335 | 0.342 |
| next λ0.5 | ℓ+1 | 0.5 | 3 | 0.347 | 0.348 |
| next λ1.0 | ℓ+1 | 1.0 | 2 | 0.319 | 0.319 |
| top λ1.0 + warmup | top (L12) | 1.0 | 2 | 0.353 | 0.367 |

**Every λ>0 variant is WORSE than λ=0.** A detached-reference InfoNCE imports the *decayed reference's* badness: the
top (L12) is the worst layer, so anchoring lower layers to it pulls the good early layers *down* (the "anchor-to-
decayed-top" failure predicted in the design). Predict-next is no better; warmup recovers a little but stays below
baseline. Replicates on flat (f_td_top_l10 tail 0.381 ≪ f_td_off 0.479). **The cheapest objective-side fix (a
reference-anchor loss term) does not manufacture global credit.** The genuine objective-side result (2601.21683
reaches BP-SSL parity) works by aligning the local update with the *global backprop update geometry* — which is
strictly more than contrasting against the current (bad) top, and remains an open research question. **But Result 3
suggests we may not need it:** sharpening the existing objective already nearly closes the gap.

---

## The verdict — the cheap-credit ladder, reordered by evidence

| rung | mechanism | backward depth | tail-L12 | cost | verdict |
| --- | --- | --- | --- | --- | --- |
| **0** | **InfoNCE temperature 0.5→0.2** | 2 | **0.539** | **1.9× (free)** | **✅ ADOPT — nearly the e2e ceiling, free** |
| 1 | wider window w4 | 4 | 0.501 | 3.8× | ◐ real but dominated by rung 0 on cost+composition |
| — | overlapping windows | 2–4 | 0.42–0.49 | 3.5–11× | ✗ DEAD (hurts + costs more) |
| — | naive top-down loss term | 1 | 0.32–0.35 | ~2× | ✗ DEAD (imports the decayed reference) |
| — | full e2e backprop (w12) | 12 | 0.549 | 11.1× | ⛔ forbidden — the diagnostic upper bound only |

**The decay is, to first order, an objective-sharpness problem with a FREE fix.** The "savior" (native deep SCFF) is
largely deliverable by re-tuning the temperature of the objective we already adopted — no new architecture, no global
wire, no stream rewrite. This is the most hopeful possible outcome, and it lands squarely on the project spine:
**preserve the class DIRECTION** — a sharper contrast keeps each layer's update pointed at the class manifold, which
is exactly direction-preservation done by the objective, not by a magnitude proxy.

## Honest caveats (before this is a committed decision)

- **temp0.2 ≈ w12 on the linear probe, but w12 still leads readout acc by ~0.02** (0.550 vs 0.569). Temperature mostly
  closes the gap, doesn't fully erase it. The bounded window (w4) or a *small* combo (temp0.2 × w3/w4 — **not yet
  tested**) may close the rest cheaply.
- **The temperature floor is uncharacterized.** temp0.2 is the best *tested*; **temp0.1 was not run** and very-sharp
  contrast can collapse (too few effective negatives). Find the floor before committing the value.
- **Continual-safety of temp0.2 is untested** — sharper contrast could help or hurt the A6 continual win (our actual
  home). This is the **first** follow-up that matters, not an afterthought.
- **Synthetic only** (headroom + flat). Natural-data still owed (carried since T0.3).
- 5 seeds ✓, PROBE_EP=60 (shape robust; third decimal noisy).

## What this changes in the plan (folded into [`replan.md`](replan.md) v2.2)

1. **T3.0 temperature → promoted to the PRIMARY cheap-depth lever and a near-term DECISION:** re-tune the adopted
   cell's `temp` (toward 0.2), after (a) charting the temp floor incl. 0.1, and (b) a continual-safety check.
2. **Overlap and naive-top-down → struck from the ladder** (clean 5-seed negatives; mechanistic reasons recorded).
3. **Wider window (w4) → demoted to a *bounded backup*** if temperature leaves a gap; cost-dominated by rung 0.
4. **The genuine global-credit mechanisms (update-alignment à la 2601.21683; DFA/EBD) → deferred and possibly
   unnecessary** — re-open only if temperature + w4 leave a gap that matters on the *continual* workload.
5. **Next experiments (in order):** (T3.0a) temp floor sweep {0.35,0.2,0.1,0.05} × window {2,4} on headroom+flat;
   (T3.0b) **continual-workload safety** of temp0.2 (does it preserve the A6 sleep-recovery win?); then natural-data.
