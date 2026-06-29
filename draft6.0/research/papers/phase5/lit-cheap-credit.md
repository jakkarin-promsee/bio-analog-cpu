# Lit survey — the cheapest global-credit mechanism that recovers composing depth (forward-stream-safe)

> **The question.** T0.2 proved the ~5-layer composing ceiling is a **credit-reach (locality) limit**, not an
> objective/task limit: the *same* InfoNCE composes all 12 layers under full credit (w12), but w12 *is* the forbidden
> deep backprop chain. So: **what is the cheapest mechanism that delivers enough global credit to lower layers to
> recover a large fraction of w12's composing depth — without a long backprop chain through the whole stack, and
> without rewriting/overwriting the forward activations mid-stack (READ/GATE/add-to-objective is allowed; INJECT-that-
> rewrites is forbidden)?**
>
> Decision axes, in priority order: **(1) cost vs full backprop** (deep gradient chain? extra memory? batch stats?),
> **(2) flow-safe?** (read/gate/objective-only = OK; rewrites the stream = DEAD), then (3) published depth-recovery
> evidence. **Novelty does not count.** A family that is novel but rewrites the stream, or needs a deep chain, is a
> dead end and is marked so plainly.
>
> All arXiv IDs below were web-verified to exist on 2026-06-29 (see "ID verification" at the end). This file is the
> mechanism-first deepening of [`track-c-cheap-direction.md`](track-c-cheap-direction.md); it supersedes that file's
> survey-level treatment and fixes one mis-attributed ID.

---

## The one frame to hold first: there are only three flow-safe ways to inject global credit

Everything below collapses to three shapes. Memorize these; each family is one of them:

1. **Change the LOCAL OBJECTIVE** so the local loss *itself* rewards keeping what the rest of the stack will need.
   No new signal crosses a layer boundary at all — you just stop the local optimum from throwing away the class
   direction. (InfoPro, sharper InfoNCE, CLAPP's predictive term.) **Always flow-safe** — it touches only the loss.
2. **BROADCAST a detached top-down signal** that each layer READS as a reference/modulator/error and turns into a
   *local weight update* (not an activation rewrite). One wire / one fixed projection, no chain. (DFA, EBD, top-down
   feedback, three-factor gate.) **Flow-safe iff the broadcast drives an update, never replaces the activation.**
3. **WIDEN the credit window** — train k consecutive layers jointly so credit reaches k layers down, with k « depth.
   A *bounded* backprop, not a global one. (w4, overlapping windows / OLU, Context Supply.) **Flow-safe** — the stream
   is untouched; only the gradient reaches further.

The forbidden shape — **inject a top-down value that becomes the next layer's input/activation** (target-propagation's
"set this layer's activity to its target", PEPITA's modulated *input*) — rewrites the stream and is out by rule,
*even when it works*.

---

## A. Overlapping local windows / message-chaining across the stack (the w-window family, generalized)

**Mechanism (2–4 sentences).** Train consecutive layers in *overlapping* groups: group g covers layers [i, i+k),
group g+1 covers [i+s, i+s+k) with stride s < k, each group carries one local loss at its top and backprops only
within the group. Because the groups overlap, a layer sits in *two* groups and is touched by two local gradients,
so credit "chains" one window further than a single non-overlapping window of width k. Overlapping Local Updates
(OLU) is the k=2, s=1 instance; Context Supply (ContSup) is the asymmetric cousin that *forward-feeds* earlier
blocks' **detached** features into the later block's **auxiliary head** (not the main stream) so the local loss can
see more context.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** bounded backprop of width k (≈ our w4) plus, for overlap, you re-touch each layer in ≥2 groups → ~2× the
  local-update work of pure greedy, *not* a deep chain. ContSup adds a small detached-feature feed + a slightly bigger
  aux head → "minimal memory and computational overhead" (their claim), no batch stats required.
- **Flow-safe?** ✅. Overlapping windows only widen the *gradient* reach; the forward activations are never
  overwritten. ContSup's context goes into the **auxiliary** network, explicitly leaving the gradient-isolated main
  stream intact — exactly our read/feed-the-head, never-rewrite rule.
- **Depth-recovery evidence:** This is the family our *own* T0.2 already validated — w2→L4, w4→L7 is precisely
  "widen the window, credit reaches deeper." ContSup (2312.07636, ICLR'24) and InfoPro/DGL line report that more
  gradient-isolated modules *degrade* unless context/overlap is added; adding it recovers much of the E2E gap on
  CIFAR/SVHN/STL-10. The honest limit: **no published theory says overlap propagates credit *unboundedly* further
  than k** — each overlap step buys ~one more layer of reach, it does not turn local into global. It is a *ladder
  rung*, not a ceiling-breaker.
- **Verdict: ✅ STRONGEST CHEAP RUNG, and we already own the apparatus.** "w4 + stride-2 overlap" is the lowest-risk
  next experiment: it is a known-good, flow-safe, no-new-wire extension of the result we already have. Its weakness
  is exactly that it is bounded — it will *extend* ~5, not reach 12. Use it as the cheap baseline that any global
  mechanism (B/D) must beat per unit cost.

## B. Direct Feedback Alignment (DFA) and variants (DRTP, sign-DFA, EBD)

**Mechanism.** Skip the backward chain entirely: take the top error e = (output − target), and send it to *every*
layer at once through that layer's **own fixed random matrix** B_ℓ, giving a pseudo-gradient B_ℓ·e that drives a
local Hebbian-style weight update (random-projected-error × local activation). No weight transport, no
layer-to-layer chain — one global broadcast, one fixed projection per layer (a fixed crossbar; substrate-cheap).
DRTP broadcasts the *target* not the error (even cheaper, weaker); **Error Broadcast & Decorrelation (EBD,
2504.11558, 2025)** is the modern variant: each layer's local loss *penalizes the correlation between its activations
and the broadcast output error* (grounded in MMSE orthogonality), which is a cleaner DFA-shaped objective.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** the cheapest of all the "global error" options — one broadcast of a single error vector, no chain, no
  per-step extra memory beyond the fixed B_ℓ matrices. Needs the **output error**, i.e. a *label* (supervised) or a
  surrogate error — this is the catch for us (see below).
- **Flow-safe?** ✅ **in update form** — B_ℓ·e drives a *weight* update; the forward activation is never overwritten.
  (It is forbidden only if used to *replace* an activation, which DFA never does.)
- **Depth-recovery evidence:** ⚠ **the known weak axis is exactly ours — depth on hard/conv tasks.** DFA learns deep
  FC nets and reaches zero *training* error, but "any variant of feedback alignment suffers significant losses in
  classification accuracy on deep convolutional networks" and the alignment angle degrades with depth/width — the
  random feedback stops being a useful gradient surrogate precisely where we need composing depth. The standard rescue
  ("transfer trained conv layers, DFA only the FC head") is not available to us — that *is* backprop on the bulk.
- **The self-supervised gap:** DFA is canonically *supervised* (needs e = output−label). For our InfoNCE there is no
  scalar label-error to broadcast; you would have to define a contrastive "error" to broadcast — **largely unproven**;
  searches surface it only as an explicit open *future direction* ("could a network trained with FA also learn via
  contrastive objectives?"), not a demonstrated result. EBD is the closest bridge (it broadcasts a *generic* error and
  decorrelates), but its published results are supervised benchmarks.
- **Verdict: ⚠ KEEP AS THE GLOBAL-ERROR OPTION, BUT NOT FIRST, AND NOT YET FOR INFONCE.** It is the cheapest possible
  global wire and maps perfectly to a fixed analog crossbar, but its two failure modes (depth-on-hard-tasks; no native
  contrastive error) are precisely the two things we need it to do. Only worth a numpy spike *after* a contrastive
  error term is defined, and only if the cheaper objective-side fix (D) underdelivers. If you do try it, try EBD's
  decorrelation form, not vanilla DFA.

## C. Forward Target Propagation (FTP) and target-propagation families

**Mechanism.** Target-propagation replaces the backward gradient with **per-layer targets**: each layer is trained
to *hit a target activation*, and the targets are generated by feedback/inverse maps. **FTP (2506.11030, June 2025)**
is the forward-only version: it generates the layer-wise targets with a **second forward pass** instead of learned
inverses or symmetric feedback weights — no weight transport, no backward chain. Each layer then does a *local*
update to move its activation toward its target.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** one extra **forward** pass (cheap on our substrate — forward is the cheap operation), no deep gradient
  chain, no symmetric feedback weights, "minimal computational overhead," and it *beats* BP under quantized/
  low-precision hardware — genuinely attractive for an analog chip.
- **Flow-safe?** ❌ **THIS IS THE PROBLEM.** Target propagation's whole mechanism is *"drive each layer's activation
  toward a target"* — the target is a top-down-derived value that the layer's activity is pushed to match. That is the
  forbidden **rewrite of the forward stream**, by construction. The constraint isn't incidental; it's the method's
  core move.
- **Depth-recovery evidence:** competitive-with-BP on MNIST/CIFAR-10/CIFAR-100 + RNN long-range deps — strong. **But
  the published work is all *supervised*; no contrastive/self-supervised FTP exists yet.**
- **Verdict: ✗ DEAD END *under our hard constraint*, despite being the most on-target *named* paper.** The earlier
  dossier flagged it as "likely flow-safe, verify" — verified, and it is **not**: target-prop rewrites activations to
  targets. It stays a *conceptual* reference (forward-only global credit is achievable) but is not implementable as-is
  without violating the no-rewrite rule. If we ever relax "never write the stream," FTP is the first thing to revisit.

## D. Top-down feedback added to a LOCAL objective — CLAPP / Greedy-InfoMax / predictive coding

**Mechanism.** Keep the local InfoNCE, and add a **detached top-down predictive term**: a higher layer's
representation is broadcast down as context that the lower layer's *loss* tries to predict / be consistent with
(CLAPP's recurrent apical-dendrite term; predictive coding's predict-down/error-up). The top-down signal enters as a
**term in the local objective and a broadcast modulation factor** ("widely broadcast modulation factors identical for
large groups of neurons" — CLAPP's own words), *not* as a replacement of the layer's activity. This is shape-1+2
combined: objective-change driven by a one-wire broadcast.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** one top-down broadcast (a reference vector or scalar modulation) + a predictive term in the local loss.
  No deep chain. CLAPP is explicitly *truly local* — pre/post activity + dendritic predictive input + a broadcast
  modulator; **per-sample, no batch stats** (a hard requirement for our continual-safe substrate, and CLAPP satisfies
  it by design).
- **Flow-safe?** ✅ — broadcast-as-reference / loss-term / modulator; the stream is read, never rewritten.
- **Depth-recovery evidence — this is the decisive recent result.** **"Can Local Learning Match Self-Supervised
  Backprop?" (2601.21683, Gerstner & Bellec group, ICML 2026)** is *exactly our question* and reaches *exactly our
  T0.2 finding from the other direction*: local-SSL (FF/CLAPP) **provably matches global BP-SSL on deep *linear*
  nets**, but on nonlinear conv nets "[they] have struggled to build functional representations in deep networks"
  (= our locality ceiling), and their fix is **algorithmic variants that make the local update *align better* with the
  global BP-SSL update** — their best CLAPP-loss variant reaches **parity with comparable global BP-SSL** on image
  benchmarks. Crucially, **they do *not* reach for top-down feedback or wider windows to do it — they fix the local
  loss/update geometry.** This is independent confirmation that the lever is *the local objective*, not new global
  wiring.
- **Verdict: ✅ THE HIGHEST-LEVERAGE FLOW-SAFE FAMILY, and it's where the 2026 literature converged.** Two sub-bets:
  (i) **CLAPP's predictive top-down term** as a one-wire global-ish coordinator (also our north-star top-down loop —
  building it is forward progress, not a detour); (ii) **the 2601.21683 update-alignment variant** — a pure
  objective/update fix with *no new wire at all*, the cheapest possible global-credit recovery. Read 2601.21683 in
  full before designing — it may hand us the knob directly.

## E. PEPITA, Forward-Forward goodness variants, SoftHebb, "signal propagation"

**Mechanism.** PEPITA: two forward passes, the second on a **modulated input** x − F·e (F fixed random, e = output
error) — the modulation carries error info into all downstream activations. Forward-Forward (Hinton): per-layer
"goodness" (Σh²) pushed up on positive data, down on negative; no cross-layer signal at all. SoftHebb: softmax
Hebbian + anti-Hebbian, unsupervised, non-local-free.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** PEPITA = one extra forward pass + a fixed F (cheap). FF/SoftHebb = pure local, cheapest of all.
- **Flow-safe?** PEPITA ❌ — it modulates the **input**, which propagates into and *changes the forward activations*
  of every downstream layer (it's an input-rewrite that becomes an activation-rewrite). FF/SoftHebb ✅ but they are
  *more local than us*, not more global — they add **zero** global credit, so they cannot lift our ceiling.
- **Depth-recovery evidence:** **damning and directly on-point.** PEPITA + top-down feedback (2302.05440) caps at
  **~3 hidden layers without normalization, ~5 with normalization, then *decreases* with depth** — that is *our exact
  ceiling*, reached by the closest cousin method, and the paper names the cause "poor collaboration between layers."
  FF goodness is *the very objective our Phase 2/3 already killed* (energy Σh² can't compose; density≠class). SoftHebb
  trains only specific shallow architectures.
- **Verdict: ✗ DEAD END for *raising* depth.** PEPITA rewrites the stream *and* hits the same ~5 wall; FF/SoftHebb add
  no global credit and (FF) use the disproven energy objective. Useful only as **negative controls** — PEPITA's ~5
  ceiling is independent corroboration that input-modulation/local-goodness does not solve credit-reach.

## F. The "how deep does greedy SSL compose" literature itself (InfoPro, DGL, the 2023–26 line)

**Mechanism (InfoPro, 2101.10832 — the centerpiece).** Diagnose *why* greedy local collapses: each local module,
optimizing only its own short-term loss, **throws away input information that is useless locally but needed
downstream** (this is *literally our drift / density≠class diagnosis*, published). Fix: add to each local loss an
**information-propagation term = a reconstruction loss (preserve input info) + the normal discriminative/contrastive
term**. No gradient crosses module boundaries; only the *local objective* changes. DGL (1901.08164) is the decoupled-
greedy substrate this sits on; the 2023–26 line (ContSup, MAN/MAN++, "Boosting Greedy Local Learning") all attack the
same degradation with auxiliary-network/context tricks.

**Cost / Flow-safe? / Depth-recovery evidence / Verdict.**
- **Cost:** InfoPro adds a small reconstruction head per module (a decoder) — modest extra params, **no chain, no
  batch stats needed for the core idea**; reported <40% of E2E memory.
- **Flow-safe?** ✅✅ — it is *purely an objective change* (shape-1). The reconstruction term changes what the local
  loss rewards; the forward stream is never touched. This is the safest possible category.
- **Depth-recovery evidence:** InfoPro recovers much of the E2E gap and is the canonical demonstration that **the
  fix for greedy depth-collapse is to stop the local loss from discarding downstream-useful information** — i.e.
  *exactly our "preserve the class DIRECTION, don't optimize local density"* spine, validated in the literature.
- **Verdict: ✅ CO-EQUAL TOP PICK with D — and it's the *cheapest* one (no new wire, no extra forward pass, just a
  loss term).** The caution: InfoPro's preserve-term is *reconstruction*, and **our Phase 3 already tested
  reconstruction and rejected it** (reconstruction preserves *density*, falls below random on *class*). So do **not**
  copy InfoPro's reconstruction term literally — copy its *principle* (add a preserve-the-downstream-info term to the
  local loss) but make the preserved quantity the **class direction**, e.g. a contrastive/predictive consistency term
  (CLAPP-style), not pixel/feature reconstruction. InfoPro tells us *what kind of fix wins*; Phase 3 tells us *which
  preserved quantity*.

---

## RANKED shortlist — cheapest-and-most-promising first (the 2–3 worth a numpy experiment)

Ranked by the deciding axes: flow-safe **and** cheap **and** evidence it lifts depth on the *right* (contrast)
objective. All three are flow-safe by construction.

### 1. Objective-side global credit — predictive/consistency term in the local InfoNCE (families D + F merged)
**The cheapest real lever: no new wire, no extra forward pass, no batch stats — just a term added to the local loss.**
Add to each layer's InfoNCE a **detached top-down consistency term** (CLAPP-style: predict/agree-with a broadcast
higher-layer representation) — the principle InfoPro proved wins (don't let the local loss discard downstream-useful
info), but with the preserved quantity = **class direction** (Phase-3-correct), *not* reconstruction (Phase-3-rejected).
- **Single concrete knob to add:** **`λ_topdown`** — the weight on a detached-top-down predictive/consistency term in
  the per-layer loss (top representation broadcast down, detached, layer's loss adds β·predict(top | h_ℓ)). λ=0
  recovers the current cell; sweep λ up and watch the per-layer probe peak march deeper.
- **Why first:** strongest 2026 evidence (2601.21683 reaches BP-SSL parity by fixing the *local update/objective*,
  not by adding wiring; InfoPro recovers depth the same way), it's our north-star top-down loop, and it's the lowest
  possible cost. **Read 2601.21683 in full first — it may hand us the exact update-alignment knob.**

### 2. Wider / overlapping coordination window (family A) — the bounded-backprop rung we already own
**`w4` with stride-2 overlap.** We already proved w4→L7. Overlap re-touches each layer in two windows to chain credit
one rung further, still bounded (no global chain), still flow-safe, zero new wiring — only the gradient reaches deeper.
- **Single concrete knob to add:** **`window_stride`** (s < w) — with w fixed at 4, set s=2 so windows overlap;
  measure depth-gained per the ~2× local-update cost vs the w12 upper bound.
- **Why second:** known-good, lowest-risk, uses the existing apparatus — the **cheap baseline every global mechanism
  must beat per unit cost.** Its ceiling is its honesty: it *extends* ~5, it does not reach 12.

### 3. (Conditional) Global error broadcast — DFA/EBD form (family B) — only if 1 and 2 plateau
A fixed random per-layer projection of a **contrastive** top-error, broadcast to all layers, driving local updates
(never rewriting the stream). Cheapest global *wire*, perfect analog-crossbar fit — but gated behind defining a
contrastive error and behind DFA's known depth-on-hard-tasks weakness.
- **Single concrete knob to add:** **`B_ℓ` broadcast gain** — the scale on a fixed-random projection of a defined
  InfoNCE "error" added as a per-layer update term; try the **EBD decorrelation form**, not vanilla DFA.
- **Why third / conditional:** the two failure modes (no native contrastive error; FA degrades with conv depth) are
  exactly our two needs. Only spike it if the objective-side fix underdelivers *and* we commit to a global wire.

**Explicitly NOT worth implementing under our constraints:** **Forward Target Propagation (C)** and **PEPITA (E)** —
both rewrite the forward stream by construction (target-prop drives activations to targets; PEPITA modulates the input
that becomes downstream activations). **Forward-Forward goodness / SoftHebb (E)** — add no global credit and (FF) use
the energy objective Phase 2/3 already disproved. Keep FTP as a conceptual reference for "forward-only global credit
is possible"; keep PEPITA's ~5 ceiling as a negative control.

---

## ID verification (all checked on arXiv, 2026-06-29)

| ID | Title | Verified |
| --- | --- | --- |
| 2506.11030 | Forward Target Propagation: A Forward-Only Approach to Global Error Credit Assignment via Local Losses | ✅ exists (Jun 2025) |
| **2601.21683** | **Can Local Learning Match Self-Supervised Backpropagation?** (Gerstner/Bellec, ICML 2026) | ✅ exists — **NOTE: the prior `track-c-cheap-direction.md` cited this ID as "Direct feedback / top-down"; the real title is the local-vs-BP-SSL paper. Re-attribute.** |
| 2305.12393 | Layer Collaboration in the Forward-Forward Algorithm | ✅ exists |
| 2101.10832 | Revisiting Locally Supervised Learning (InfoPro line; journal IJCV 2024) | ✅ exists |
| 2312.07636 | Go beyond End-to-End Training: Boosting Greedy Local Learning with Context Supply (ContSup, ICLR'24) | ✅ exists |
| 1901.08164 | Decoupled Greedy Learning of CNNs | ✅ exists |
| 2010.08262 | Local plasticity rules…contrastive predictions (CLAPP / Illing et al, NeurIPS 2021) | ✅ exists |
| 2302.05440 | Forward Learning with Top-Down Feedback (PEPITA analysis) | ✅ exists |
| 2504.11558 | Error Broadcast and Decorrelation (EBD) | ✅ exists (2025) |
| 1609.01596 | Direct Feedback Alignment Provides Learning in Deep NNs (Nøkland) | ✅ exists |
| 2012.03837 | Parallel Training of Deep Networks with Local Updates (OLU / overlapping windows) | ✅ exists |

**Could not independently confirm beyond the survey-engine summary:** none of the cited IDs failed verification. The
one correction is the **re-attribution of 2601.21683** above (it is the local-vs-BP-SSL paper, not a generic
"direct-feedback/top-down" paper). `2601.19261` ("Decoupled Split Learning via Auxiliary Loss") surfaced in search but
was **not used** as a citation here (distributed-learning framing, off our axis) — flagged only so it isn't mistaken
for a load-bearing reference.
