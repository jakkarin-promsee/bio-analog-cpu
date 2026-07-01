# Phase 6 — Noise-robust SCFF: make the cheap brain survive the world it runs in

> **Status: 🟢 ACTIVE / LOCKED-FOR-RUN (designed 2026-07-01; 3-agent lab-manager review folded in; ready to run next
> session).** A *live spec an agent executes* — the experiment ladder + build plan for hardening SCFF against noise. No
> results yet; when rungs run they fill `expK/experiment-K.md`, `RESULTS.md`, then the public `README.md` +
> `phase6-report.md`. Reporting contract: [`result-format.md`](result-format.md). The literature behind every
> mechanism: [`../../research/papers/phase6/`](../../research/papers/phase6/README.md).
>
> **Phase reframe (the author's call, 2026-07-01):** **Phase 6 = noise-robust SCFF — a Stage-1 *extension*** (this);
> the GD namer that was the undifferentiated "Phase 6 = optimization" shifts to **Stage 2 / Phases 7–9**
> ([`../stage2-design.md`](../stage2-design.md)). The reason for the move is the whole reason this phase runs first:
> **a frozen head preserves but cannot *manufacture* the robustness a backbone lacks (LP-FT)** — so if the
> noise-sensitivity is in SCFF, it must be fixed *in SCFF, before the namer exists.* The provenance — the
> 2026-07-01 cold-start noise-research pass — is folded in: the problem is §0, the research's decision ledger is §8.
> The frozen Stage-1 cell this hardens: [`../phase5-final-architecture.md`](../phase5-final-architecture.md).

---

## 0. Why Phase 6 exists — the problem, and what it is NOT

### 0.0 The arc — Phase 6 is the SCFF noise close-out, and it runs *before* the namer

**Phase 6 finishes the job of making the cheap brain real.** Phases 1–5 built the SCFF bulk and proved it composes the
depth a task needs, read cheaply, continual-safe — *in a noiseless numpy ideal.* But the cell will run on an analog
substrate and on a lifelong, never-clean data stream, and Phase 4 flagged (A7) that it is **noise-sensitive.** The
ordering question — fix it now or after the GD namer? — was settled by one result:

> **LP-FT / backbone-robustness: a trained readout *preserves* but cannot *create* robustness the features lack.** A7's
> sensitivity is in SCFF's representation (its per-sample norm is the source), so **no 20% GD readout can rescue it.**
> The fix is upstream, in the SCFF objective — a **Stage-1** problem. Phase 6 runs before Stage 2.

So every Phase-6 rung is measured against one question — **"is the cheap brain robust enough to *trust* downstream?"** —
not "does it beat backprop." We are hardening a finished component, then handing a *trusted, noise-characterized* cheap
brain to the GD-optimization era — or finding, honestly and cheaply, that we can't (§7, the YES/NO fork).

### 0.1 The problem — two doors, named precisely

"Noise" hides two distinct enemies; the cheap brain must survive **both**.

**Door A — the analog substrate.** Capacitor charge drifts, op-amps offset, ADCs quantize. Phase-4's **A7**: the cell is
sensitive to eval-time noise, and *the per-sample L2 norm that makes it nuisance-robust is the very thing that makes it
noise-sensitive.* The hardware literature (Rasch 2023) sharpens the target: **input / tap / ADC-quantization noise
dominates the accuracy loss — not weight noise — and the readout-input channel is precision-critical.** And the
dangerous component is **directional**: the *residual* class-axis mismatch that survives draft-5's differential /
auto-zero. *Generic i.i.d. Gaussian is the easy enemy; structured + directional is A7's real one.*

**Door B — the data stream itself (the author's Phase-6 insight).** The model is online and lifelong: **every datum is a
single noisy real-world sample the hippocampus banks into the LUT to replay at sleep — it never sees a clean, curated
truth set.** So robustness isn't only "tolerate a noisy weight"; it is "**learn a stable class direction from a stream
where every example is corrupted and the clean signal is never shown directly.**"

### 0.2 The reframe (what the research pass sharpened)

Four things the 2026-07-01 pass settled, each changing the plan:

1. **The two doors share *one* crux.** Door A's residual (directional mismatch surviving auto-zero), Door B's residual
   (structured noise surviving replay-averaging *and* Noise2Noise), and the spine's enemy (a perturbation aligned with
   the class axis) are **the same thing — directional, non-zero-mean noise.** Phase 6 has *one* hard enemy with three
   faces, which means the directional probe tests both doors at once.
2. **Door B is learnable — for the zero-mean part (a loss-dependent caveat, critic-forced).** **Noise2Noise:** the
   clean signal is recoverable from *only* noisy observations when the corrupted target shares the clean target's
   **conditional expectation** — which for an **L2** objective means **zero-mean** noise (for L1 it's the median, L0 the
   mode). Two mechanisms we already own push that way — replay aggregation (the LUT mean → √N suppression of zero-mean
   noise) and a *contrastive* Noise2Noise (pull two noisy views together). **Honest caveat:** Lehtinen's proof is for an
   L2-to-a-target regression; our InfoNCE is *not* that, so **contrastive-N2N is a suggestive analogy — a hypothesis to
   test in P6.4, not a guarantee.** *The structured/directional residual survives regardless — the crux of (1).*
3. **The fix must be forward-only / local** (SCFF has no backward pass). This filters the toolbox: noise injection
   (input/tap/weight) is forward-only-native; **forward-only flatness is reachable** via a **zeroth-order SAM**
   *mechanism* — estimate the sharp direction from random (Rademacher) weight perturbations, no backprop (the general
   ZO-optimization line: SPSA / ZO-SGD; MeZO [2305.17333] shows ZO scales; **ZOSA** [2511.09156] is *evidence the ZO-SAM
   mechanism works*, though that paper is LLM-prompt-tuning-scoped — we lift the mechanism, not the result). This
   **overturns the concept draft's "SAM is out"** — what's out is SAM's *two-pass backprop*, not flatness-seeking
   (S-SGD weight-noise is the reliable lever; the ZO pass is the sharper option, behind an entry gate — P6.2). Explicit
   Jacobian/Lipschitz regularization is *not* forward-only and enters only as the *explanation* of why input-noise
   injection works (Bishop: input-noise ≈ the Jacobian penalty, first-order, small-noise, without the backward pass).
4. **SCFF being unsupervised removes the *label*-noise door.** A linear head on contrastive features is provably
   label-noise-robust; the label only enters the tiny GD readout (Stage 2). So Door B *for SCFF* is input-corruption +
   stream-ordering + **buffer purity** — not label noise.

### 0.3 What the research suggested — hypotheses to harden (NOT results)

The pass produced candidate fixes; Phase 6 runs each under full protocol. As hypotheses:

- **H-aug (the headline):** a **noise-corrupted contrastive view** in the InfoNCE trains the class *direction* to be
  noise-invariant — robustness *in* the objective, forward-only, spine-clean (it's the forward-only surrogate for
  Jacobian/Lipschitz smoothing). **Owed:** the noise-strength sweet-spot (too strong → BYOL-collapse / selectivity
  loss); directional-not-just-i.i.d. augmentation; continual-safety; natural data.
- **H-flat:** weight-noise injection (S-SGD) in the local SCFF update + a **periodic** zeroth-order sharpness pass
  (ZOSA) over the SCFF weights pushes toward a flat minimum that survives charge perturbation; *does charge-channel
  flatness transfer to the tap channel Rasch says dominates?* (the open transfer question). *(Note: the SCFF bulk learns
  online forward-only and does **not** "sleep" — sleep is the GD-over-LUT readout consolidation; so this is a periodic
  forward-only pass over the **SCFF** weights, distinct from the readout's sleep. Readout-flat-sleep / MGSER-SAM is a
  Stage-2 concern.)*
- **H-purity:** Door B needs **buffer purity** (a Self-Centered / small-loss filter on the LUT), not just averaging —
  the Phase-6 ↔ Phase-9 seam.
- **Struck-in-advance (re-confirm as logged):** plain i.i.d.-Gaussian-only training (beats the *weak* enemy, leaves the
  directional one); SAM-proper as a *deployed* lever (two-pass backprop — out; ZOSA is the forward-only stand-in);
  post-training calibration as the *base* fix (read-side → Stage 2, can't manufacture base robustness — LP-FT).

### 0.4 What Phase 6 is NOT — the scope guard ("keep the menu closed")

- **NOT the GD readout's job.** LP-FT settled it: the readout can't manufacture base robustness. Readout-side noise
  defense (calibration, BiC-style) is **Stage 2**, a complement, not the Phase-6 answer.
- **NOT SPICE / device physics.** We stay in numpy with an *honest behavioral* analog-noise model (AIHWKit-structured:
  correlated common-mode + uncorrelated mismatch + ADC quantization + a directional residual) — ideal-math first, real
  silicon later (the standing scope rule). The point is *where the fix lives*, decided cheaply before fabrication.
- **NOT i.i.d.-Gaussian robustness as the claim.** The honest enemy is structured & directional; an i.i.d.-only victory
  is beating a weaker enemy than A7 named (a logged control, not the headline).
- **NOT breaking the committed Phase-5 cell.** Every fix is measured against the A6 continual win (the gate, P6.6) and
  the P5 depth/selectivity it must not cost. A noise fix that un-wins depth or forgetting is rejected, however robust.
- **NOT the north star.** No recurrence, no active inference. Simple intelligence first.

---

## 1. The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — robustness is DIRECTION-invariance, never a MAGNITUDE.** "Accuracy survived noise" is a magnitude
symptom; the lever is whether the **class direction** is preserved under perturbation. This is density≠class wearing its
*5th* coat, and it kills three tempting-but-wrong moves up front: (a) measuring robustness only as Δaccuracy (a scalar
that hides *which* axis moved) instead of **cosine(clean-rep, noisy-rep)** — the direction metric; (b) buying
"robustness" by shrinking the representation (a flat-but-dead code is trivially noise-invariant and useless — the
selectivity guard catches it); (c) defending against **i.i.d. magnitude** noise while the **directional** enemy (the one
aligned with the class axis) walks through. Preserve the class direction under noise; measure it as an angle; and aim
every fix at the *directional* residual, not the easy isotropic part.

**The envelope — forward-only / local; NEVER rewrite the SCFF stream.** The fix lives *inside* SCFF's local forward
update: noise injection (input/tap/weight), a noise-corrupted contrastive view, a periodic zeroth-order sharpness pass —
all forward-only-native. **The hard rule (P2.5, carried):** read / add-to-objective / inject-noise = OK; **anything that
needs a backward pass through the SCFF bulk, or rewrites SCFF activations mid-stack, is forbidden.** This is why
explicit Jacobian regularization and SAM-proper are *out as methods* (they need the backward pass) and survive only as
the *explanation* (Bishop) and the *upper-bound reference* — their forward-only stand-ins (input-noise injection,
zeroth-order sharpness) are what we run.

**The gate that governs adoption — continual-safety.** A6 (the sleep-recovery continual win) is the architecture's
reason for being, and a noise fix is exactly the kind of change that could dent it (a sharper noise-augmented contrast
could worsen class-incremental drift; a flatter minimum could slow adaptation). **A fix that dents A6 is rejected,
however robust it is on the static A7 curve.** Every adopted change passes P6.6 before it is banked.

---

## 2. The structure — three threads, two gates, one verdict

```
 HARDEN the substrate channel (Door A)        SURVIVE the data stream (Door B)
   P6.1 noise-as-augmentation (the primary)     P6.4 all-noisy stream + buffer purity
   P6.2 flatness (S-SGD inject + ZOSA pass)      P6.5 bulk-drift (the noise we make)
   P6.3 the per-sample-norm root (dangerous)
                       \                        /
                        \                      /
              GATES (un-skippable):  P6.6 continual-safety (A6)  ·  P6.7 natural-data
                        |
                   P6.8 synthesis → the YES/NO arc verdict + the noise-hardened cell (or the reopen)
```

The threads share one enemy (the directional residual, §0.2-1), so P6.1's directional augmentation is the spine of
*both* doors. **P6.3 (re-tuning the per-sample norm) is the highest-leverage and most dangerous rung** — the norm is what
won P5's depth — so it is gated hard by the P5 invariants and runs only if P6.1/P6.2 leave a gap. The verdict (P6.8) is
a fork, not a score: **fixable-in-SCFF (hand the hardened cell forward) vs sensitivity-survives (the SCFF objective must
change at a deeper level → arc reopen).**

---

## 3. The experiment ladder (cheapest-decisive-first; one variable per rung; 5 seeds; median + IQR)

Each rung is one sharp question, run with the house-style figures ([`result-format.md`](result-format.md)) and written
in the 6+2-slot card. **Every rung is read against one lens — *is the cheap brain robust enough to trust?*** — and each
states, *before it runs*, **what each outcome will mean** (a **Reads** line, including the **failure** reading), because
a result that changes no decision and a failure we can't interpret both didn't need running. **Failures are data** — a
struck mechanism is logged as a card, not tuned to pass. Conditional rungs fire only if a gap survives. Cards live in
`expK/`; apparatus in `p6lib.py` (§6).

### P6.0 — the bench + the honest noise model + A7 reproduction + guards `exp0`
- **Question:** does the apparatus reproduce A7 on the committed Phase-5 cell, with a *credible* analog-noise model and
  the right channels, before any fix is tried? **And how bad is it, on which channel, and is it directional?**
- **Setup:** stand up `p6lib.py` (§6) on the frozen Phase-5 cell (`SCFFContrastOverlap` temp0.2 / w2, L12, no residual).
  Build the **`NoiseModel`** — *correlated common-mode* (subtractable) + *uncorrelated mismatch* (per-weight Gaussian) +
  *ADC quantization* (k-bit on taps) + a *directional residual*. **Pin the directional axis (critic-forced — this is the
  recurring direction-bug in noise clothing):** the **eval/probe** axis = the **class axis** (between-class
  mean-difference / LDA direction), computed on a **held-out fit split**, frozen — worst-case is the point; *never* the
  per-sample label (no leak). Sweep an **A7 sensitivity curve** per channel — **tap / input / ADC primary, weight
  secondary** (Rasch ordering) — for **i.i.d. vs directional** noise **at matched RMS *on the class axis*** (the
  *projected* component, NOT total RMS — §4). **Add a `linear_readout`-on-raw-input control** to every A7 curve, so
  "OURS is *specifically* directionally fragile" (the A7 thesis) is a **relative** claim, not one any model satisfies.
- **Guards (pre-fix — the antidote to the recurring sign/direction bug):** `NoiseModel` at σ=0 ≡ the Phase-5 cell
  bit-for-bit; FD-gradient `< 1e-5` on any new backward path (the noise-aug VJP, P6.1); dead-frac ≈ 0; the
  **projected-RMS-matching check** (i.i.d. and directional at equal energy *on the class axis* — i.i.d. at matched
  *total* RMS lands only ~1/√Wd on that axis, which would rig the comparison). **Auto-zero — measured, not assumed
  (critic-forced):** the common-mode guard is NOT a free pass — injecting then subtracting the same term only proves the
  stub's arithmetic. Run **two arms, with and without `auto_zero()`**, and report the common-mode channel's cost in
  *both*: the with-arm models the *best case* of a differential / common-mode-rejecting front end (a carried draft-5
  Scap/crossbar substrate assumption — grounded in, not asserted beyond, the substrate doc); the **no-auto-zero arm is
  the honest floor** that keeps the common-mode channel from being defined away.
- **Reads:** A7 reproduces — the class-direction degrades under the dominant channel, and **OURS degrades *more per unit
  class-axis perturbation than the `linear_readout` control*** (matched projected-RMS) → the cell is *specifically*
  directionally fragile (the A7 thesis) and the bench is trusted. *(The bare "directional worse than i.i.d." is NOT a
  finding — at matched projected-RMS it can hold for any model; the decisive read is OURS-vs-linear.)* OURS degrades no
  more than linear → A7 is a generic perturbation cost, re-scope the phase. The cell is *already tolerable* fix-free →
  fixes are polish, deprioritize. **Any guard fails → STOP.** **If even fix-free is catastrophic on the dominant
  channel**, flag the YES/NO fork early — but still run P6.1.
- **Decides:** go/no-go on the bench; the dominant channel + whether OURS is *specifically* directionally fragile (sets
  what P6.1 augments against); **the pinned calibration `σ*`** — the RMS where the fix-free cell hits a named retention
  (e.g. `acc(σ*)/acc(0)=0.90` on the dominant channel), defining the "tolerable band" operating point for STOP ① and
  P6.8 (**pre-registered here, blind to any fix**); and **the canonical fix-free A7/dir arrays** (these seeds + RMS
  grid), **frozen to a pinned run-dir every later rung loads — never recomputes** (else "Δ vs fix-free" drifts with
  re-training noise).

### P6.1 — noise-as-contrastive-augmentation: the primary fix `exp1`  *(hardens H-aug — STOPPING MARK ①)*
- **Question:** does corrupting one InfoNCE view with the (structured/directional) noise model make the class direction
  noise-invariant — *without* collapsing the representation or costing clean accuracy — and is the gain spine-clean
  (an **angle** invariance, not a magnitude artifact)?
- **Setup (one variable = augmentation-noise strength `σ_aug`):** the **`NoiseAugContrast`** cell = `SCFFContrastOverlap`
  with one positive view through `NoiseModel` at `σ_aug`, at temp0.2 / w2, headroom + flat + mixed, L12, 5 seeds (9 for
  the ≤0.02 variant gaps). **Three augmentation variants — the control that makes the spine claim falsifiable
  (critic-forced, one-variable):** (i) **i.i.d.-aug**; (ii) **directional-aug** along a **label-free surrogate axis**
  (top input-PCA, or the cell's own top-singular direction — *NOT* the held-out class axis: a class-axis *training*
  corruption would leak label info into the unsupervised stream and confound robustness with weak supervision; the eval
  probe still uses the class axis — **train-axis ≠ eval-axis**, stated in the card); (iii) **random/orthogonal-axis-aug**
  at matched projected-RMS — the **generic-regularization isolator**: if directional-aug raises direction-invariance on
  the directional channel **more than** random-axis-aug does, the gain is *specifically* directional (the spine); if they
  match, it's generic smoothing. **Plus a loss-level variant — RINCE** (Robust InfoNCE, [2201.04309]): a drop-in robust
  contrastive loss hardening against corrupted positive views; augmentation hardens the *inputs*, RINCE the *loss* — test
  whether they compose or RINCE alone suffices. **The fix-free baseline is a co-trained `σ_aug=0` arm** (same harness /
  seeds / budget — NOT the P6.0 frozen number; it must reproduce the P6.0 fix-free A7 curve within §B, or the bench
  moved). Report the **A7 curve after training**, **clean acc + selectivity**, and **direction-invariance**
  `cos(clean-rep, noisy-rep)` per depth.
- **The collapse control + the capacity-ceiling probe (BOTH MANDATORY):** two distinct failure modes. (a) **Collapse** —
  too-strong augmentation makes the positive pair trivially close → representation collapse (BYOL), which *looks* like
  perfect robustness (cos≈1) but is dead; the **selectivity / clean-acc guard** aborts a `σ_aug` whose "robustness" comes
  with selectivity below the fix-free baseline. (b) **The capacity ceiling *below* collapse (critic-forced — Noisy
  Machines, [2001.04974]):** noise-aware training *reduces representational capacity*, so clean selectivity/acc can **sag
  monotonically with `σ_aug` even at moderate strength**, before any collapse. Pre-register the probe: track clean
  selectivity vs `σ_aug`, flag the knee; the committed `σ_aug` must sit **below the capacity knee**, not merely below
  collapse. (If the knee bites, the documented remedy is distillation — noted for Stage 2, not built here.)
- **Reads / pre-registered rule:** the committed `σ_aug` = the strongest value (**below the capacity knee**) that
  **raises direction-invariance `cos(clean,noisy)` on the dominant directional channel** (per §B) **while holding clean
  acc + selectivity** and **passing P6.6.** **The decisive spine test = directional-aug vs random-axis-aug:**
  directional-aug must beat random-axis-aug on the *directional* curve (matched projected-RMS) → the gain is directional
  invariance, not generic regularization. If random-axis-aug flattens it just as much → the win is generic smoothing
  (reported honestly — useful, but not the spine claim). If RINCE alone matches/beats augmentation → adopt the
  cheaper/loss-level fix. If *no* variant raises direction-invariance into the band without tripping the capacity/collapse
  guards → **H-aug refuted**, lean on P6.2/P6.3, the YES/NO fork tilts NO.
- **STOPPING MARK ① (the "tolerable band" DEFINED — critic-forced; §B is a *difference* test, not a *tolerance*):** the
  band is a **pre-registered retention threshold at the pinned `σ*` (P6.0)**, **direction first** —
  `cos(clean,noisy) ≥ Y` on the dominant directional channel at `σ*`, with readout-retention `acc(σ*)/acc(0) ≥ X` as the
  corroborating secondary (**pick X≈0.90 and Y from the fix-free lineage NOW, blind to results**). If noise-as-augmentation
  alone clears the band (capacity/collapse guards held, P6.6 passed), **the primary fix is found and SCFF is robustly
  trustable** — P6.2/P6.3 are improvements. The honest minimum is plausibly **P6.0 → P6.1 → P6.6 → P6.7**.
- **Decides:** the adopted augmentation (y/n, i.i.d. vs directional, strength). The highest-leverage knob — run first.

### P6.2 — flatness: forward-only weight-noise + zeroth-order sharpness `exp2`  *(hardens H-flat)*
- **Question (conditional — run iff the weight channel is *dominant* in P6.0 AND P6.1 leaves a weight-channel gap):**
  does forward-only flatness reduce *weight/charge*-channel sensitivity — and does charge-channel flatness **transfer**
  to the tap channel Rasch says dominates? **Pre-registered skip (critic-forced):** if P6.0 confirms tap≫weight (the
  Rasch prediction) *and* P6.1 brings the tap curve into band, **P6.2 is a one-line skip-card** — flatness would improve
  a non-dominant channel, not worth continual-scale compute. Run only if the weight channel matters to the verdict.
- **Setup (one variable = the flatness lever):** (a) **S-SGD** symmetric weight-noise in the local SCFF update (the
  reliable lever); (b) a **zeroth-order sharpness pass** on the **SCFF weights** — estimate the sharp direction from
  Rademacher weight perturbations, no backprop (the general ZO line: SPSA / ZO-SGD; ZOSA/MeZO are *evidence the mechanism
  works*, not a liftable method — §0.2-3), applied **periodically** at a **pinned cadence** (every-K-steps / a late-phase
  pass — pin K in `p6lib`; SAM-selects-flat-late grounds the periodic placement). **This is a forward-only SCFF pass, NOT
  the readout's GD sleep** (the SCFF bulk doesn't sleep; readout-flat-sleep / MGSER-SAM is Stage-2). **Entry gate
  (critic-forced):** the ZO lever is admitted only after the ZO-SAM mechanism is confirmed reproducible on a toy cell; if
  not, **P6.2 reduces to S-SGD weight-noise only** (the rung doesn't hinge on one post-cutoff paper). **Forward-only
  proof, mechanized** (a ZO pass has *no* backward path for the FD-check to catch): assert the pass touches only
  per-layer-local weight perturbations + forward objective evals — no cross-layer activation tape, no stream rewrite —
  and log the perturbation/eval count as the proof. Measure a **flatness probe** + the **weight-channel A7 curve**, then
  **the tap-channel A7 curve** (the transfer test).
- **Controls:** SAM-proper (two-pass backprop) as an **upper-bound reference only** — *not deployed* (it violates the
  forward-only envelope; it bounds how much the zeroth-order surrogate leaves on the table). Variance-/Bayes-matched
  injection (BayesFT) vs fixed-σ as a secondary refinement.
- **Reads:** the flatness lever reduces the weight-channel curve and the flatness probe → flatness is buyable
  forward-only. **Transfer measured explicitly:** if charge-flatness *also* flattens the tap curve → one lever, both
  channels (the good outcome); if not → flatness is a *weight-only* patch and the tap channel still needs P6.1's
  augmentation (the likely outcome per Rasch). ZOSA ≈ SAM-reference → the forward-only surrogate is sufficient; a large
  gap → flatness wants a backward pass we can't pay, log the limit.
- **Decides:** include the flatness lever y/n, and where (every-step local update vs a periodic sharpness pass) — banked
  only if it adds robustness *beyond* P6.1 and passes P6.6.

### P6.3 — the per-sample-norm root re-examination `exp3`  *(the dangerous root fix — conditional — STOPPING MARK ②)*
- **Question (conditional — run iff P6.1+P6.2 leave a gap):** A7's *source* is the per-sample L2 norm. Can the
  normalization be made noise-robust **without costing the P5 depth/selectivity the same norm won**?
- **Setup (one variable = the normalization):** test direction-preserving variants that shed noise-fragility — a
  clipped/soft norm, a norm computed after a small denoising/aggregation, or letting P6.1 *train* the norm to be stable.
  Run at temp0.2 / w2, with the **full P5+P4 invariant panel** measured every cell: depth tail-L12, peak march, BWT,
  selectivity, **readout-acc vs tuned-BP** (the committed cell *beat* tuned-BP 0.550 vs 0.531 — that rides the norm too),
  **and A2 nuisance-dim robustness** (critic-forced: A2's win and A7's fragility *share* the layernorm cause, so a
  "noise-robust norm" could silently trade A7 for A2).
- **The hard guard (MANDATORY):** the P5 depth + P4 wins are the architecture's identity. **Any norm variant that moves
  *any* of {tail-L12, BWT, readout-acc-vs-tuned-BP, A2 nuisance-robustness} *real-worse* (per §B) than the committed
  cell is ABORTED**, regardless of its A7 gain — one variable, and the carried invariants outrank the noise gain. (This
  rung can *un-win* the whole of Stage 1 if run carelessly; the norm is load-bearing for *four* properties, not just
  depth — it is fenced accordingly.)
- **Reads:** a norm variant cuts the A7 directional curve **and** holds every P5 invariant → the *root* fix, adopt it.
  Every variant that cuts A7 also costs depth/BWT → **the per-sample norm is load-bearing for depth and we do NOT touch
  it**; robustness comes from P6.1/P6.2 layered on top (the most likely outcome — and a clean result either way).
- **STOPPING MARK ②:** the norm is the root, but it is also the depth lever — so this rung's default outcome is *"leave
  the norm alone, harden around it."* Touching the root is licensed only by a result that pays for itself on *both*
  axes.
- **Decides:** keep the P5 norm (harden around it) vs adopt a noise-robust norm (only if depth-neutral).

### P6.4 — Door B: the all-noisy stream + buffer purity `exp4`  *(hardens H-purity; the continual-noise existential)*
- **Question:** can a stable class direction form when **every** training sample is corrupted and no clean truth is ever
  shown — and does buffer **purity** (not just averaging) matter?
- **Setup (two separable sub-questions; keep their Reads distinct):** (a) **the Noise2Noise test** — train SCFF on a
  stream where every sample is corrupted by `NoiseModel`, **zero-mean** first, then **directional**; measure the class
  direction vs the **clean-data cell at matched effective sample budget** (same stream length × LUT size — else the gap
  is data-volume, not corruption). **Pinned pass/fail (critic-forced):** "the direction forms" iff direction-metric ≥
  (clean-cell − §B band); report the zero-mean **residual gap** explicitly, not a binary — N2N is an *infinite-pair
  expectation*, so finite streams leave residual variance even for zero-mean (a contrastive analogy, not Lehtinen's
  theorem — §0.2-2). (b) **the purity sub-question** — add a **`PurityFilter`** (Self-Centered / small-loss) on the LUT
  and compare *purified* vs *naive* buffer at matched size, on the noisy stream.
- **Reads:** zero-mean corruption → the direction still forms (replay-mean + contrastive N2N do the denoising) →
  Door B's i.i.d. part is handled, partly for free. Directional corruption → degraded → **the same crux as Door A**, and
  **does P6.1's directional-augmentation rescue it?** (the cross-door test). Purified buffer beats naive → buffer purity
  is a real Phase-6 ↔ Phase-9 knob; no difference → averaging alone suffices at our noise level (report it).
- **Decides:** the LUT purity-filter y/n (handed to Phase 9 maintenance); confirmation that Door B is learnable for the
  zero-mean part and that its residual is the *same* directional enemy.

### P6.5 — bulk-drift: the noise we make ourselves `exp5`  *(a MEASUREMENT rung — informs Stage-2, exempt from the verdict-bar; a carried debt, not new)*
- **Question:** how fast does the unsupervised SCFF bulk *drift* over the continual stream (stale tap-features = a
  self-inflicted, noise-like perturbation the readout must tolerate), and does noise-hardening change it?
- **Setup (one variable = the cell variant — fix-free vs P6.1-hardened):** measure representation drift
  (`cos(rep_t, rep_{t+Δ})` of fixed probe inputs) across the P4.5 class-incremental stream, fix-free vs noise-hardened.
- **Reads:** drift is slow → "the bulk doesn't forget" (a Stage-2 cheapness assumption) holds; drift is fast → flag it
  for Stage 2 (stored tap-features go stale → a maintenance *and* a noise cost). Noise-hardening reduces drift → the
  augmentation also stabilizes the bulk (a bonus); increases it → a tension to log.
- **Decides:** the bulk-drift rate as a measured input to Stage-2's maintenance design. **This rung cannot move the
  YES/NO verdict (it's a measurement) — it is exempt from the verdict-bar, and may be deferred to Stage-2/Phase-9 (where
  its only consumer lives) if its continual-stream cost crowds the verdict-bearing rungs.**

### P6.6 — continual-safety: the home-turf gate `exp6`  *(the spine gate — un-skippable)*
- **Question:** does each adopted noise fix (the augmentation, any flatness lever, any norm change) **preserve the A6
  sleep-recovery continual win**?
- **Setup:** the **`continual_harness`** (carried from `p5lib`/`p3lib` — the validated A6 sleep/consolidation loop);
  measure BWT / AA / retention of each candidate change vs **the fix-free committed Phase-5 cell's continual result,
  itself referenced to the P4.5 baseline** (the cell P5.7 banked at BWT −0.026 — *one* referent, not the ambiguous
  "P4.5/P5"), budget/protocol-matched (digits home + swept difficulty). Run as a **checkpoint on every committed
  change**. **Power (critic-forced — this is the GATE, not a characterization rung):** **5 seeds, NOT 3**, and **"within
  noise" is NOT an automatic pass** — a small consistent dent (P5 banked changes at BWT −0.026) hides under IQR-overlap,
  so the gate also requires a **paired-by-seed sign test**: a change that is negative-BWT in ≥4/5 paired seeds **fails**
  even if IQR overlaps. A gate that defaults to "pass" under low power is a rubber stamp.
- **Reads:** BWT / AA / retention hold vs baseline → the change is continual-safe, bank it. They degrade → the change is
  **rejected** regardless of its A7 score (a more noise-augmented or flatter cell that worsens class-incremental drift is
  a *result*, not a thing to tune away — fall back to the strongest fix that passes here).
- **Decides:** the gate. A noise fix that fails here is reverted regardless of its robustness gain.

### P6.7 — natural-data confirmation `exp7`  *(the synthetic-artifact gate)*
- **Question:** do A7 **and** the adopted fixes hold on real flat data (and with noise injected into real inputs)?
- **Setup:** digits (64-D) + CIFAR-flat (3072-D), the in-scope flat anchors, overlaid on the headline curves (A7-CURVE,
  DIR-INVARIANCE) with `NoiseModel` applied to the real inputs/taps.
- **Reads:** A7 *and* the fix reproduce on digits/CIFAR-flat → the synthetic noise story is real, commit it. A7 vanishes
  on real data → it was partly a synthetic artifact, re-scope. The fix works on synthetic but not real → do **not**
  commit it.
- **Decides:** whether the synthetic noise story (and its fix) is real or an artifact.

### P6.8 — synthesis + the arc verdict + the noise-hardened cell  *(README + phase6-report)*
- **Assembled-cell confirmation (RUN, not just synthesized — levers may not stack):** run the *adopted* cell (the
  committed augmentation + any flatness/norm/purity change, **all together**) end-to-end on A7-CURVE + DIR-INVARIANCE +
  CONT-SAFETY + NAT-ANCHOR. A combined regression **overrides** per-rung optimism.
- **The verdict (pre-registered as a conjunction over named channels — critic-forced, so a messy multi-channel result
  still resolves), evaluated at the pinned `σ*` (P6.0):**
  - **YES — fixable in SCFF:** (direction-invariance ≥ Y on the **dominant directional channel**) **AND** (continual-safe,
    P6.6) **AND** (holds on natural data, P6.7). → hand the **noise-hardened cell** to Stage 2
    ([`../stage2-design.md`](../stage2-design.md)); the cheap brain is *truly* done.
  - **Scoped-YES (a YES with a named caveat):** the dominant channel is fixed but a *secondary* channel's residual
    survives (e.g. "tap-directional fixed, ADC-quantization residual remains"). → hand forward **with an explicit brief**
    that Stage 2 must defend the named residual (read-side). Still a YES, not a reopen.
  - **NO — arc reopen:** the **dominant** channel's direction can't be held by any forward-only objective fix (capacity
    knee / collapse / continual-veto block every lever). Then the per-sample-norm representation cannot hold the class
    direction on this substrate → the SCFF objective changes at a deeper level (or the substrate assumptions do) — found
    now in numpy, cheaply, before silicon. *The most consequential Phase-6 result.*
- The decision-record deltas (§8); the hand-off brief to Stage 2 (what noise the namer can assume is already handled,
  what it still must defend — the readout-side calibration, the buffer purity now owed to Phase 9). **Update the
  `ref-report/` glossary** with the phase's new citable terms (A7 sensitivity curve, direction-invariance,
  noise-as-augmentation, the directional residual) at close.

---

## 4. The metrics (PINNED) — what "noise-robust" means here

Carry the canonical set ([`../result-format.md`](../result-format.md)); Phase-6 additions in **bold**.

| metric | definition (pinned) | what it answers |
| --- | --- | --- |
| **A7 sensitivity curve** | Δ(readout acc) **and** Δ(class-direction) vs injected RMS, **per channel** (tap/input/ADC/weight), **i.i.d. vs directional at matched *projected* RMS**, **+ a `linear_readout` control** (OURS-vs-linear = the *relative* fragility) | how bad, which channel, is OURS *specifically* directionally fragile |
| **direction-invariance** | `cos(clean-rep, noisy-rep)` of the *same* sample, per depth (the spine metric) | is the **class direction** preserved under noise (not just accuracy) |
| clean accuracy / **selectivity** | noiseless readout acc + per-layer selectivity, median + IQR | the anti-collapse guard — robustness must not be bought by a dead rep |
| **flatness** | loss/objective change under a unit weight perturbation (Rademacher) | the weight-channel robustness geometry; ZOSA vs SAM-ref |
| **noise-model fidelity** | the AIHWKit-structured components present (common-mode subtracted, mismatch, ADC bits, directional) | is the enemy *honest* (not a weak i.i.d. stand-in) |
| **bulk-drift rate** | `cos(rep_t, rep_{t+Δ})` of fixed inputs across the continual stream | the self-inflicted, noise-like perturbation (the Stage-2 assumption) |
| **buffer purity** | fraction of LUT entries that are clean, under the PurityFilter vs naive | Door B — does purity beat averaging |
| **continual BWT / AA / retention** | GEM/CL-survey conventions, hardened cell vs **the fix-free committed cell (itself referenced to the P4.5 baseline)**; + paired-sign veto at the gate | **the gate** — does the fix keep the A6 win |
| backward cost (substrate) | carry P4/P5 — labelled substrate work, **never "energy"** | the augmentation/flatness training cost, scoped honestly |

**Calling a difference real (n=5, carry):** real only if **IQR bands are disjoint at the final checkpoint** *and* the
**sign is consistent in ≥4/5 seeds, paired by seed**; else "within noise." **At the P6.6 GATE, "within noise" is NOT an
auto-pass** — add the paired-sign veto (negative in ≥4/5 paired seeds = fail). **Matched-RMS rule (Phase-6-specific,
sharpened — critic-forced):** i.i.d.-vs-directional comparisons are matched on **projected RMS onto the class axis**, NOT
total RMS — i.i.d. at matched *total* RMS lands only ~1/√Wd of its energy on the class axis, which would rig "directional
is worse" for *any* model (the tautology trap; the decisive read is always **OURS-vs-`linear_readout`**, not
directional-vs-i.i.d.). Fix-vs-baseline comparisons are at equal injected energy on the channel under test. Every A7
caption states **which RMS convention** it uses.

---

## 5. Tasks

| role | task | why |
| --- | --- | --- |
| **the device under test** | the **frozen Phase-5 cell** (`SCFFContrastOverlap` temp0.2 / w2, L12, no residual) | Phase 6 hardens *this*; it is not re-derived |
| **the noise dial** | `NoiseModel`: correlated common-mode · uncorrelated mismatch · ADC-quant · **directional residual** | the honest analog enemy (AIHWKit-structured); directional = the spine's |
| **the depth/selectivity regimes** | **headroom** + **flat** + **mixed** (carry P5) | the fix must not cost the P5 depth it rides on |
| **the data-stream enemy (Door B)** | the all-noisy stream (zero-mean then directional) + the LUT buffer | the continual "never sees clean truth" test |
| **natural confirm (P6.7)** | **digits** (64-D), **CIFAR-flat** (3072-D), noise on real inputs | the synthetic noise story must survive real flat input |
| **continual (P6.6)** | class-incremental digits + swept difficulty (P4.5/P3.3 exact) | the home turf the fix must not break |
| **deferred** | SPICE / PVT corners / conv / time-series | needs device physics or new architecture (§0.4) |

Seeds `[42,137,271,314,1729]` (P6.4 may run 3 for cost; **P6.6 the GATE runs the full 5 — never 3**, per the
paired-sign power note), median + IQR, single-threaded (phantom guard), `PROBE_EP=120` for any cited number. **Power
note:** the decisive small gaps — **directional-aug vs random-axis-aug** (the spine test) and **P6.2 transfer**
(`tap-A7-slope(flat) − tap-A7-slope(fixfree)` at `σ*`) — get **~9 seeds** (add `[1009, 2027, 9091, 7]`) when ≤0.02, so
the rung can adjudicate the difference it exists for.

---

## 6. What to build — `p6lib.py` (the apparatus, on `p5lib`)

Reuse `p5lib` (`SCFFContrastOverlap`, `PerDepthHeads`, `fit_readout`/`readout_feats`, `linear_probe`, the cost meters,
the racers, `continual_harness`, the digits/CIFAR-flat loaders, `make_mixed`), `p3lib`/`p2lib` (layernorm VJP, norm/relu,
`effective_rank`). **Add (with the pinned specs the rungs depend on):**

- **`NoiseModel(common_mode, mismatch, adc_bits, directional, rms, axis)`** — the honest analog injector. `common_mode`
  = one correlated perturbation shared across a layer (temperature/supply — the common-mode-subtractable part);
  `mismatch` = uncorrelated per-weight Gaussian; `adc_bits` = k-bit quantization on the taps (the Rasch-dominant
  channel); `directional` = a structured residual along `axis`. **The axis is pinned by use (critic-forced, no leak):**
  the **eval/probe** `axis` = the **class axis** (between-class mean-difference / LDA, on a **held-out fit split**,
  frozen — worst-case probe); the **train-aug** `axis` (P6.1) = a **label-free surrogate** (top input-PCA or the cell's
  top-singular direction) — **train-axis ≠ eval-axis**, asserted. Applies to **inputs / taps / weights** selectably.
  **Guards:** σ=0 ≡ the clean cell bit-for-bit; **`auto_zero()` as a TWO-ARM control** (with- and without-subtraction —
  the with-arm models the best-case differential front end (carried Scap/crossbar substrate assumption, grounded not
  asserted); the **without-arm is the honest floor** — never a free pass); a **projected-RMS normalizer** (match energy
  *on the axis*, not total). Optional `bayes_match` / `variance_aware` (BayesFT / Variance-Aware) injection.
- **`NoiseAugContrast(σ_aug, variant, loss)`** — `SCFFContrastOverlap` with one positive view routed through `NoiseModel`
  at `σ_aug`, **`variant ∈ {iid, directional(label-free axis), random_axis}`** (random_axis = the
  generic-regularization isolator at matched projected-RMS) and **`loss ∈ {infonce, rince}`** (RINCE = Robust InfoNCE
  [2201.04309], the loss-level robustness variant). The headline cell (P6.1). **Guards:** `σ_aug=0` ≡ plain
  `SCFFContrastOverlap` bit-for-bit; the co-trained `σ_aug=0` arm reproduces the P6.0 frozen A7 curve within §B (the
  bench-didn't-move check); FD-gradient `<1e-5` on the new VJP; the **capacity-knee probe** (clean selectivity vs σ_aug).
- **`weight_noise_update` / `zosa_sharpness`** — S-SGD symmetric weight-noise in the local update; ZOSA-style zeroth-order
  sharpness (Rademacher, no backprop), callable as a **periodic forward-only sharpness pass over the SCFF weights**
  (P6.2 — *not* the readout's GD sleep). `sam_reference` = a backprop two-pass SAM, **flagged
  reference-only, never deployed** (the forward-only-envelope check).
- **`flatness_probe()`** — loss/objective change under unit Rademacher weight perturbation (P6.2 metric).
- **`a7_sensitivity()`** — the per-channel sensitivity-curve sweep (Δacc + Δdirection vs RMS, i.i.d. vs directional at
  matched *projected* RMS, **+ a `linear_readout`-on-raw-input control** = the relative-fragility reference); the bench's
  headline (P6.0). **It writes the canonical fix-free arrays to a pinned run-dir that every later rung LOADS, never
  recomputes** (the no-baseline-drift rule).
- **`direction_invariance()`** — `cos(clean-rep, noisy-rep)` per depth (the spine metric).
- **norm variants** — the P6.3 candidates (clipped/soft/denoised norm), each with the full P5-invariant panel wired in,
  and the **abort-if-depth-regresses** guard.
- **`PurityFilter`** — a Self-Centered / small-loss filter on the LUT buffer (P6.4 Door B); + the all-noisy stream
  generator (zero-mean and directional corruption modes).
- **`bulk_drift()`** — `cos(rep_t, rep_{t+Δ})` of fixed probe inputs across the continual stream (P6.5).
- **guards** — equivalence (`NoiseModel σ0 ≡ clean`, `NoiseAug σ0 ≡ plain`, `auto_zero subtracts common-mode`) + FD-gradient
  (`<1e-5`) on every new backward path, run before any cell (P6.0).
- **reproducibility (carry, non-negotiable)** — `manifest.json` (git hash + resolved config + seeds + versions +
  wall-clock) + `arrays.npz` per run to the schema pinned in [`result-format.md`](result-format.md) §A; `plot_p6.py regen
  <run-dir>` redraws every figure from saved data; per-cell `_ckpt.jsonl` fsync'd (resumable); thread caps before numpy
  import + `python -u` + `PYTHONIOENCODING=utf-8` (the OpenMP-phantom + cp874 guards).

**Rough per-rung wall-clock:** P6.0–P6.3 are noise-curve sweeps over the frozen cell (~30–90 min each, 5–9 seeds).
**P6.4 (all-noisy continual stream) and P6.6 (continual-safety) are the heaviest** — continual streams × noise × seeds —
run **3-seed, checkpointed, single-threaded, multi-hour**, and **verify the real PID is alive** (the 14-hr-ghost guard,
per the OpenMP-phantom memory).

---

## 7. The success criterion + the two stopping marks + the verdict fork

> A cell that **holds its class direction under the dominant (directional) noise channel** within a tolerable band,
> **without** losing clean accuracy / selectivity, validated to **preserve the A6 continual win (P6.6)** and to hold on
> **natural data (P6.7)** — *or* an honest verdict that no forward-only objective fix can hold the direction, which
> **reopens the SCFF objective before any silicon is committed.** Not "we beat an i.i.d.-noise baseline"; a
> *characterized, forward-only, continual-safe* robustness story (or a decisive negative). **Either way it COMPLETES
> THE SCFF SIDE's noise question** and hands a *known* cell — hardened or honestly-flagged — to the GD era.

**The verdict fork, reported plainly (§3 P6.8):** YES (fixable in SCFF → hand the hardened cell to Stage 2) vs NO
(sensitivity survives → arc reopen). The literature prior leans toward "the fix had better be reachable in the SCFF
objective" — so a clean YES is the hoped-for, a clean NO is the most consequential.

- **STOPPING MARK ① (P6.1):** if noise-as-augmentation *alone* brings the A7 directional curve into the tolerable band
  (clean acc / selectivity held, P6.6 passed), the primary fix is found and SCFF is robustly trustable — **the honest
  minimum is plausibly P6.0 → P6.1 → P6.6 → P6.7.** P6.2/P6.3 are improvements.
- **STOPPING MARK ② (P6.3):** the per-sample norm is the *root* but also the *depth lever* — so the default outcome is
  "leave the norm, harden around it." Touching the root is licensed only by a result that pays on *both* the A7 and the
  P5-depth axes.

---

## 8. The decision record (the 2026-07-01 research pass — authoritative for the plan logic; the critic pass is next)

The cold-start noise-research pass produced the plan above and **overturned five things in the concept draft** — logged
here so the corrections aren't silently absorbed. **The 3-agent lab-manager review (repo-fit · outside-literature ·
red-team/executor) then ran, and its verdicts are folded into the rungs above and ledgered in §8.1.**

> **THE META-INSIGHT (carried, 5th coat).** Door A's residual, Door B's residual, and the spine's enemy are the **same
> directional, non-zero-mean noise.** Robustness is **direction-invariance**, measured as an angle — never a Δaccuracy
> magnitude. (density≠class, 5th appearance.)

**KEEP / CHANGE / CUT ledger (from the research pass):**

| Item | Verdict | Why |
| --- | --- | --- |
| Noise is a **Stage-1 / SCFF** problem, run *before* the namer | **KEEP — the whole reframe** | LP-FT: a frozen head can't manufacture base robustness |
| Noise-as-contrastive-augmentation = the primary fix | **KEEP — the headline (P6.1)** | the forward-only surrogate for Jacobian/Lipschitz smoothing (Bishop); spine-clean (angle) |
| "SAM is not forward-only → out" (concept §2) | **CHANGE → the zeroth-order-SAM *mechanism* is forward-only** (SPSA/ZO-SGD; MeZO/ZOSA = evidence, not liftable methods) | Rademacher perturbations, no backprop; S-SGD is the reliable lever, the ZO pass is entry-gated (P6.2); SAM-proper stays reference-only |
| "Replay aggregation denoises Door B" (concept §3.4) | **CHANGE → averaging is not enough; add buffer PURITY** | Self-Purified Replay: buffer purity is crucial; aggregation handles only zero-mean |
| "Can we even learn with no clean truth?" (Door B fear) | **RESOLVED → yes for zero-mean, *for an L2 objective* (Noise2Noise)** | equal-conditional-mean condition (L2⇒zero-mean, L1⇒median); the contrastive transfer is an analogy to test in P6.4, not Lehtinen's theorem; directional residual survives |
| The per-sample-norm root fix (P6.3) | **KEEP but FENCE — the dangerous rung** | it's the A7 source *and* the P5 depth lever; abort if depth/BWT regress |
| i.i.d.-Gaussian as the noise model | **CUT as the headline → directional/structured + AIHWKit-honest** | i.i.d. is a weaker enemy than A7 named (correlated common-mode is auto-zero-subtracted) |
| Readout-side calibration as the base fix | **CUT → Stage 2 complement** | LP-FT: read-side can't create base robustness |
| Unsupervised ⇒ the label-noise door | **KEEP closed for SCFF** | contrastive features are provably label-noise-robust; labels only at the readout |

**Owed before any number becomes a *decision* citation:** the full-protocol runs (5–9 seeds, `PROBE_EP=120`, real
readout, matched-projected-RMS) — every claim in §0.3 is a *hypothesis*. **Citation hygiene (the critic pass verified
all five post-cutoff IDs resolve):** ZOSA 2511.09156 (real, but LLM-prompt-tuning-scoped — cite the *mechanism*, ground
the method in SPSA/ZO-SGD + MeZO 2305.17333), Ditch-the-Denoiser 2505.12191 ✓, Variance-Aware 2503.16183 ✓,
Layer-Lipschitz 2603.25103 (✓ but backprop-based — a pointer, not a forward-only method), Silicon-analog 2601.19905 ✓.
New IDs the pass added: RINCE 2201.04309, Noisy Machines 2001.04974, MeZO 2305.17333, spectral-robustness 2405.17181.

### 8.1 The lab-manager review ledger (2026-07-01 — three cold agents; APPLIED)

Three subagents (repo-fit · outside-literature · red-team/executor) stress-tested the plan "can we confirm before
running?" Verdict: **science / spine / envelope sound; the *spec* had holes.** All material findings are APPLIED above;
the load-bearing ones:

| finding (agent) | verdict | where applied |
| --- | --- | --- |
| "Tolerable band" undefined — §B is a *difference* test, not a *tolerance*; the YES/NO verdict floats (red-team) | **FIX** | STOP ① + P6.8: a pre-registered retention threshold (cos ≥ Y, acc-ret ≥ X) at the pinned `σ*` |
| Matched-*total*-RMS rigs "directional worse" tautologically (red-team) | **FIX** | matched **projected** RMS + a `linear_readout` control; decisive read = OURS-vs-linear (§4, P6.0) |
| Directional axis circular / label-leaky, PCA vs class-axis (red-team) | **FIX** | eval = frozen class axis (held-out); train-aug = label-free surrogate; train-axis ≠ eval-axis (P6.0/P6.1/§6) |
| P6.1 has no control isolating robustness from generic regularization (red-team) | **FIX** | the **random/orthogonal-axis-aug** arm — the spine test (P6.1) |
| ZOSA is an LLM prompt-tuning paper, not a general method (lit) | **FIX** | cite the ZO-SAM *mechanism* (SPSA/ZO-SGD/MeZO); S-SGD reliable; ZO pass entry-gated (§0.2, P6.2) |
| Noise2Noise "zero-mean ⇒ recoverable" is L2-only; contrastive = analogy (lit) | **FIX** | §0.2-2 + P6.4 downgraded to a hypothesis |
| MISSING: RINCE — Robust InfoNCE against noisy views, 2201.04309 (lit) | **ADD** | a P6.1 loss-level variant (hardens the *loss* where aug hardens the *inputs*) |
| MISSING: Noisy Machines capacity ceiling, 2001.04974 (lit) | **ADD** | the P6.1 capacity-knee probe (a 2nd failure mode below collapse) |
| Auto-zero *assumes* substrate common-mode rejection (red-team) | **FIX** | two-arm control (with/without) — measure, don't assume (P6.0/§6) |
| P6.6 gate at 3 seeds can rubber-stamp a real regression (red-team) | **FIX** | 5 seeds + paired-sign veto; "within noise" ≠ auto-pass (P6.6/§4/§5) |
| P6.3 guard misses readout-acc + A2 nuisance (both ride the norm) (both) | **FIX** | widened the abort panel to {tail-L12, BWT, readout-vs-BP, A2} (P6.3) |
| P6.2 transfer rung always fires with null=expected (red-team) | **FIX** | pre-registered skip-card if tap≫weight and P6.1 closes tap (P6.2) |
| P6.4 "direction forms" no threshold + finite-sample residual (red-team) | **FIX** | ratio-to-clean threshold + matched sample budget (P6.4) |
| P6.5 can't move the verdict yet sits in the main ladder (repo-fit) | **FIX** | tagged a measurement rung, verdict-bar-exempt, deferrable (P6.5) |
| arrays.npz can't store fix-vs-fixfree / iid-vs-dir / per-change (repo-fit) | **FIX** | method / variant / change axes added to the schema (result-format §A/§D) |
| "P4.5/P5 baseline" named two ways, one not a real artifact (repo-fit) | **FIX** | one referent: the fix-free committed cell vs the P4.5 baseline (P6.6/§4) |
| Fix-free A7 arrays re-derived per rung → drift (both) | **FIX** | P6.0 freezes them to a pinned run-dir; later rungs load, never recompute |
| Neuromorphic on-chip noise-robust local learning uncited (lit) | **NOTE** | named as a known adjacent area (forward-only-noise-toolbox.md) |

**Rejected / deferred (with reason — nothing was rejected as *wrong*; these are scope calls):** RUSH / certified
randomized-smoothing for contrastive (2207.05127) — *deferred*, a certification route beyond a numpy go/no-go's needs
(noted, not built); the full neuromorphic-SNN literature — *noted as a blind spot, not chased* (out of numpy behavioral
scope, §0.4).

---

## 9. Open items / scope

- **Decision-record deltas (commit to `idea/main.ideas.v1.md` only after P6.0–P6.1 give results — flagged, not applied):**
  a new supporting decision — *SCFF carries a noise-aware objective (a noise-corrupted contrastive view); robustness is
  built into the base, not bolted onto the readout* — revising the implicit "SCFF objective is noiseless." Plus the
  still-pending Stage-2 deltas (**N3′** boosting-dropped, **S4′** organs→one, **N2** EMA-view, **S6** gate) carried from
  the Stage-2 reframe, untouched here.
- **The Phase-6 ↔ Phase-9 seam:** the LUT **buffer-purity filter** (P6.4) is decided here but *lives* in Stage-2/Phase-9
  maintenance — handed forward, not built twice.
- **Handed to Stage 2 (the namer's brief):** what noise the readout can assume is already absorbed (the directional A7
  channel, if YES) vs what it must still defend (read-side calibration under shift; the buffer purity); the measured
  **bulk-drift rate** (P6.5) as an input to the maintenance-loop design.
- **Deferred to the analog/PVT phase (out of numpy scope):** SPICE, process corners, retention/1-f temporal noise,
  read-disturb — Phase 6 decides *where the fix lives*; the silicon realism comes later.
- **If the verdict is NO (arc reopen):** the candidate deeper fixes — a different normalization geometry, a noise-aware
  objective beyond augmentation, or a substrate-assumption change — are scoped *then*, not pre-committed now.

---

## 10. References

The mechanism stories: [`../../research/papers/phase6/`](../../research/papers/phase6/README.md) — the existential
flatness file, the noise-as-augmentation primary fix, the all-data-is-noise (Door B) file, and the forward-only toolbox,
with arXiv IDs (post-cutoff ones flagged for verification).

The evaluation-methodology canon (carry from Phase 4/5): **gap-to-tuned-BP swept across scale** — Bartunov 2018
([1807.04587](https://arxiv.org/abs/1807.04587)); **measured (not theoretical) cost** — Spyra 2025
([2511.01061](https://arxiv.org/abs/2511.01061)); **continual = AA/BWT/FWT/forgetting** — CL survey
([2302.00487](https://arxiv.org/abs/2302.00487)), GEM ([1706.08840](https://arxiv.org/abs/1706.08840)). Phase-6-specific:
**input-noise = Tikhonov** (Bishop 1995); **flat minima** (SAM [2010.01412](https://arxiv.org/abs/2010.01412); S-SGD
[2009.02479](https://arxiv.org/abs/2009.02479); **ZOSA** [2511.09156](https://arxiv.org/abs/2511.09156)); **a head can't
create backbone robustness** (LP-FT [2202.10054](https://arxiv.org/abs/2202.10054)); **analog noise dominates at the tap
channel** (Rasch, Nat. Comm. 2023); **Noise2Noise** ([1803.04189](https://arxiv.org/abs/1803.04189)); **buffer purity**
(Self-Purified Replay [2110.07735](https://arxiv.org/abs/2110.07735)); **SSL noise robustness** (Ditch-the-Denoiser
[2505.12191](https://arxiv.org/abs/2505.12191)); **correlated-vs-uncorrelated analog noise**
([2409.08633](https://arxiv.org/abs/2409.08633)); **robust InfoNCE against noisy views** (RINCE
[2201.04309](https://arxiv.org/abs/2201.04309)); **noise-injection capacity ceiling** (Noisy Machines
[2001.04974](https://arxiv.org/abs/2001.04974)); **zeroth-order optimization at scale** (MeZO
[2305.17333](https://arxiv.org/abs/2305.17333)); **contrastive ≈ implicit Lipschitz / spectral robustness**
([2405.17181](https://arxiv.org/abs/2405.17181)). Carry-overs: the committed Phase-5 cell
([`../phase5-final-architecture.md`](../phase5-final-architecture.md)), the `result-format` lineage.
