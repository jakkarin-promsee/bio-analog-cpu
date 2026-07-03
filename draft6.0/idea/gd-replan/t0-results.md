# T0 results — the two controls ran (2026-06-28); the depth ceiling is LOCALITY-bound

> **What this is.** Results of the two pre-decision controls the multi-agent review demanded, run on the P4.3
> apparatus (`temp/ref/t0/run_t0.py`, 1078s, 3 seeds, L=12/W=64, headroom task, per-layer linear-probe to L12).
> Figure: `t0/figs_t0/T0_RESULTS.png`. Both verdicts were **pre-registered** (decision rules fixed before the run),
> so this reads cleanly. **Headline: the ~5-layer composing ceiling is LOCALITY-bound — the contrast objective can
> compose all 12 layers under global credit; forward-only locality is what caps it — and two CHEAP levers
> (objective temperature, window width) lift it partway for free.** This resolves the open forks in
> [`review-and-revisions.md`](review-and-revisions.md) §C6/C7 and reshapes [`replan.md`](replan.md).

---

## T0.1 — depth-scaled-training grid: the decay is NOT lr/passes under-training (but temperature is a free lever)

Median over n=3, L=12, W=64, headroom, per-layer probe peak + tail-L12:

| config | peak@L | peak | tail-L12 | acc_last |
| --- | --- | --- | --- | --- |
| base lr.03 ep25 *(= the P4.3 cell)* | 4 | 0.537 | 0.423 | 0.446 |
| lr.03 ep75 *(3× passes)* | 4 | 0.551 | 0.439 | 0.456 |
| lr.03 ep150 *(6× passes)* | 4 | 0.563 | 0.444 | 0.451 |
| lr.01 ep25 | 5 | 0.485 | 0.389 | 0.407 |
| lr.10 ep25 | 4 | 0.553 | 0.443 | 0.449 |
| lr.10 ep150 *(max train)* | 4 | 0.567 | 0.438 | 0.456 |
| **temp 0.2 ep75** *(sharper contrast)* | **7** | **0.573** | **0.543** | **0.554** |
| mask 0.3 ep75 *(weaker masking)* | 4 | 0.561 | 0.473 | 0.477 |

**Verdict (pre-registered rule: peak stable ~5 across the grid → intrinsic to budget; marches deeper with lr/passes
→ under-training):**

- **lr and passes do NOT move the peak.** 6× passes (ep25→150) and 10× lr (0.01→0.10) leave the peak at L4 and lift
  the tail only ~0.02. **The decay is real under the training budget — it is *not* an lr/passes under-training
  artifact.** The honest confound the warm-up flagged is settled: more training doesn't extend composing depth.
- **But a NEW cheap lever surfaced — objective STRENGTH.** A sharper InfoNCE (`temp 0.5→0.2`) moves the peak
  **L4→L7**, lifts the tail **0.42→0.54**, and lifts last-layer accuracy **0.45→0.55** — at *zero* architecture cost,
  still forward-only/per-sample/SCFF-flow-safe. `mask 0.3` lifts the tail too (0.42→0.47). **This is the
  contrast-strength-at-depth control the red-team demanded — and it fired.** Tuning the contrast objective is the
  first lever to bank, before any architecture.

## T0.2 — locality control: the ceiling is LOCALITY-bound (the decisive result)

Same InfoNCE objective, only the credit-window reach varies (`window`: 1=pure local → 12=full end-to-end backprop):

| config | window | peak@L | peak | tail-L12 | slope(L1→L12) | acc_last |
| --- | --- | --- | --- | --- | --- | --- |
| w1 (pure local) | 1 | 3 | 0.521 | 0.335 | **−0.0059** *(decays)* | 0.362 |
| w2 (adopted) | 2 | 4 | 0.537 | 0.423 | +0.0024 | 0.446 |
| w4 | 4 | 7 | 0.544 | 0.501 | +0.0099 *(rises)* | 0.513 |
| **w12 (full e2e backprop)** | 12 | **12** | 0.545 | **0.545** | **+0.0136** *(rises to the top)* | 0.569 |
| w12 @ lr.01 | 12 | 11 | 0.454 | 0.440 | +0.0052 | 0.471 |

**Verdict (pre-registered: w12 marches past ~5 while w1/w2 stall ~5 → LOCALITY-bound; w12 also peaks ~5 →
objective/task-bound):**

> **Unambiguous: as the credit window widens, the composing peak marches monotonically deeper — w1→L3, w2→L4,
> w4→L7, w12→L12 — and full end-to-end backprop composes ALL 12 layers with NO decay (slope +0.0136, peak AT the
> top). The same InfoNCE objective composes the whole stack under global credit. The ~5 ceiling is the
> forward-only LOCALITY cap, not an objective/task limit.**

The control is clean because **w1 trains *every* layer directly** (per-layer InfoNCE) and *still* decays (peak L3) —
so this is not "trained vs untrained layers," it is "global credit composes, local credit doesn't." (Caveat: w12's
loss sits at L12 so the top is directly optimized; but the *intermediate* L1–11 probes rise monotonically, which is
genuine composition, and the w1-trains-all-and-decays contrast rules out the trivial reading.)

## Reconciling with Phase 2 / Phase 3 (no contradiction — they compose)

- **Phase 2:** "intrinsic to forward-only locality." **Phase 3:** narrowed to "intrinsic to the *energy* objective"
  (contrast composes; energy can't). **T0.2 shows both were partly right, and how they fit:**
  - The **objective family** gates whether composition is *possible at all* — energy `Σh²` can't (Phase 2/3);
    contrast *can* (Phase 3). **THE enabler.**
  - The **credit reach** gates *how deep* the (correct) contrast objective composes — local w2 caps ~5; global w12
    composes fully. **A binding variable** (Phase 2's locality intuition, now correctly scoped to the contrast cell).
  - **Synthesis:** `contrast + global credit = full composition`; `contrast + local credit = ~5`; `energy + any
    credit = wall`. The "~5 ceiling" is the **locality cap on the right objective.** Phase 2's "intrinsic to
    locality" was *too strong* (it's not a hard wall — wider credit lifts it monotonically) but correctly named
    locality as binding; Phase 3 correctly named the objective as enabling. This is the **density≠class / preserve
    the DIRECTION** spine again: global credit carries "what the class-discriminative top needs" down to every
    layer, so deep layers preserve the class *direction* instead of drifting.

## The crux (the substrate tension) — and why this is GOOD news, carefully

**w12 = full backprop through the SCFF bulk = exactly the expensive/forbidden thing** the architecture avoids. So
w12 is a **diagnostic UPPER BOUND** (proof the ceiling is reachable), *not* a deployable design. The result does not
say "do full backprop"; it says **the depth is there to be unlocked if we can deliver global credit cheaply.** That
turns the native-depth story from "accept ~5 and read around it" (the conservative reframe) into **"extend ~5 toward
full via a cheap-credit ladder, with w12 as the proven ceiling to chase."** More optimistic than the reframe
assumed — and it confirms the review's §C7 worry: **global coordination (Track C) is a *prerequisite* for native
deep SCFF, not an optional escape hatch.**

The cheap-credit ladder the data already sketches (each rung: "how much depth per unit cost," vs the w12 bound):
1. **Objective strength — FREE.** Sharper InfoNCE temperature (+ mask tuning). T0.1: temp0.2 alone bought L4→L7 and
   tail +0.12, *no architecture, forward-only, per-sample.* Bank immediately.
2. **Wider window — BOUNDED, still forward-ish.** w4 bought L7 / tail 0.50 (≈ temp0.2). w4 is a 4-layer local
   window — more credit than w2, still a bounded forward computation (no global backprop). A real, cheap rung.
3. **Cheap global credit — the real Track C.** top-down broadcast / DFA / Forward-Target-Propagation: approximate
   the w12 global signal *without* full backprop, never rewriting the SCFF stream. This is now the **central
   research+experiment question** (how cheap a global signal recovers how much of w12's composition).

## Honest scope / caveats (before any of this becomes a decision citation)

- **3 seeds, not the standard 5** — the trend is monotone across all seeds and reproduces P4.3 on the anchor, but
  extend to `[42,137,271,314,1729]` before citing as a committed decision.
- **PROBE_EP=60** (vs the standard 120) — slightly noisier probe; the *shape* (peak march, slope sign) is robust,
  the third decimal is not.
- **Headroom synth task only.** The owed **flat-regime + natural-data spot-check** (T0.3 in the plan) was NOT run
  here — do it next; the locality verdict should be confirmed off synthetic before it's load-bearing.
- **w12 is the forbidden full backprop** — diagnostic only, never a deployment.
- **Cheap levers interact** — temp + w4 + a global signal may not stack linearly; test combinations, don't assume.

## What this changes in the plan (folded into [`replan.md`](replan.md) v2 → v2.1)

1. **T0.1 cheap levers → BANK NOW (a decision, cheap):** re-tune the adopted cell's **InfoNCE temperature (toward
   0.2) and mask_ratio** — they extend composing depth and lift accuracy for free. The adopted `temp=0.5` should be
   revisited.
2. **Track C is DE-CONDITIONALIZED → MANDATORY for native depth** (was "only if locality-bound"; the control says
   locality-bound). But it must be the **cheap global-signal approximation** of w12, never full backprop. The
   cheap-credit ladder (temp → w4 → cheap-global) is the new native-depth path, each rung benchmarked vs the w12
   upper bound.
3. **The reframe (Track B / where-to-read) stays the MVP** for the *cost* fix — but native depth is now *curable*,
   not just *routable-around*. The plan is more ambitious and more hopeful than the post-review v2 assumed.
4. **Next experiments:** (T0.3) the owed flat + natural-data spot-check; then the **cheap-credit ladder** — temp/
   mask re-tune (free) → w4 (bounded) → a first cheap global signal (top-down broadcast) — each measured for
   depth-gained-per-cost against the w12 ceiling.
