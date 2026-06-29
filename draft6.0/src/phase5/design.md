# Phase 5 — Solve depth: compose useful depth, and read it cheaply

> **Status: 🟡 ACTIVE / PLANNED (designed 2026-06-29, not yet run).** This is a *live spec an agent executes* — the
> experiment ladder + build plan for the depth-readout fix. No results yet; when rungs run, they fill
> `expK/experiment-K.md`, `RESULTS.md`, then the public `README.md` + `phase5-report.md`. Reporting contract:
> [`result-format.md`](result-format.md). The literature behind every mechanism:
> [`../../research/papers/phase5/`](../../research/papers/phase5/README.md).
>
> **Phase renumber (the author's call, 2026-06-29):** **Phase 5 = the depth-readout fix** (this); the old
> "Phase 5 = continual optimization (sleep cadence + Ch7 gate)" **shifts to Phase 6** (now readout-aware). The
> **draft-6 orientation docs** that still say "P5 = optimization" — `../../CLAUDE.md` (draft-6 status section),
> `../../context.md`, `../../idea/main.ideas.v1.md`, `../stage1-report.md`, and the status skill
> (`../../.claude/skills/status/SKILL.md`) — are **synced when Phase 5 closes** (the same way Phase 4's renumber was
> narrated, not retro-edited mid-flight). *(The repo-**root** `CLAUDE.md` is phase-agnostic — it says nothing about
> P5 and is NOT edited.)* The provenance of this plan — the 2026-06-28/29 research session + a 4-Opus-agent review —
> is folded in: the problem statement is §0, the review's decision ledger is §8.

---

## 0. Why Phase 5 exists — the problem, and what it is NOT

### 0.0 The arc — Phase 5 is the SCFF close-out

**Phase 5 finishes the cheap brain.** The architecture is SCFF (~80%, the unsupervised forward-only bulk) + GD
(~20%, the precise readout). Phases 1–4 built and characterized the SCFF bulk and found its *one remaining flaw* —
it composes class structure for ~5 layers then drifts. **Phase 5's job is to close that flaw: make SCFF compose the
depth a task needs, and make the readout read it cheaply — after which the SCFF side is *done*.** That is the phase's
identity, and it sets a hard scope line:

> **When Phase 5 closes, the SCFF side is complete, and the project pivots to optimizing the GD side** (Phase 6+ —
> the continual sleep/consolidation loop, the Ch7 learning-gate, the boosting-chain readout). The continual
> maintenance loop is GD-side work; it was the *old* "Phase 5" and is now Phase 6. So every Phase-5 rung is measured
> against one question — **"does this complete SCFF?"** — not "does this beat backprop." We are finishing a component,
> then handing a *trusted, finished* cheap brain to the GD-optimization era.

This is why the success criterion (§7) is **"SCFF is done"** and why the continual win is a *gate* (§1, P5.7), not a
target: Phase 5 must not break the home turf it hands forward.

### 0.1 The problem (from the Phase-4 diagnosis)

Phase 3 adopted `[contrast (InfoNCE, two-mask) + coordination w=2] bulk + all-tap sleep-consolidated readout`, and
Phase 4 confirmed it **composes depth — for ~5 layers — then decays.** The per-layer probe on the adopted cell:
**peak ~0.54 at L5 → 0.435 at L12.** It is **not** the Phase-2 energy wall (that rotted from layer 1, composed
zero); contrast genuinely climbs, then slides. Three controls (P4.3-decay) killed every capacity explanation:

| Hypothesis | Control | Verdict |
| --- | --- | --- |
| Deep layers go **dead** | per-layer dead-unit fraction | **REFUTED** — dead-frac ≈ 0.00 at every layer |
| Deep layers too **narrow** | widen to W240 @L12 | **REFUTED** — W64 and W240 decay to the *same* accuracy |
| Lost **effective rank** is binding | erank vs accuracy | **REFUTED** — `widen` carries higher rank (18.7 vs 12.3) at *identical* accuracy → rank is a symptom |

What's left is a **direction** failure — the project's recurring silent killer, 4th appearance (density≠class →
the missing sign → the §3.3 XOR bug → this):

> **The per-layer local contrast objective drifts the representation off the class manifold once a layer's
> class-relevant abstraction *saturates* — independent of width.** Each layer re-discriminates the input *its own
> way*, toward *some* informative code that is not aligned with the *class* axis the readout needs. For ~5 layers the
> w=2 window keeps neighbours pulling together; past its reach, with no signal to *preserve* what's already
> class-relevant, the deep layers **overwrite** the extractor's work (the mixed-task tell: a flat subtask probe-solved
> by L2–3 at ~0.67 is corrupted to ~0.51 by L12, while tuned BP holds it at ~0.75 — the corruption is OURS-specific).

**Decay = trigger × multiplier.** *Trigger* (the author's "abstraction-saturated"): the task's class-abstraction
saturates at a task-dependent depth (sooner on flat, later on headroom) — this sets *how deep is useful per task*.
*Multiplier* (the data's): no preservation term, so a post-saturation layer overwrites instead of leaving alone. The
fix targets the **multiplier**; the trigger tells us how deep we even need to go.

### 0.2 The reframe (what the research session sharpened)

The problem is **not** only "stop the decay." It is **two problems**, and the rough-idea pass (T0/T3 — see §0.3)
found both are tractable:

1. **Earn the depth** — make the representation keep composing. The rough pass found the ceiling is **locality-bound**
   (the *same* InfoNCE composes all 12 layers under full end-to-end credit; local windows cap ~5), and that the
   cheapest lever to extend it is **sharpening the objective** (a sharper InfoNCE temperature kept each update on the
   class manifold), *not* new credit machinery.
2. **Read the depth cheaply** — the useful layer is at a **task-dependent depth** (the extractor's end); reading every
   layer (all-tap) **burns the 80/20** that justifies SCFF being 80% of the brain. SCFF "isn't done" until the GD
   readout reads the *right* depth cheaply, without reading everything.

The unifying analogy (a *loose* one — see §8, demoted from theory): the **extractor / tunnel**. Useful depth = the
extractor (length set by task complexity); past it is tunnel that, unsupervised, *actively overwrites* the good
features — and **a long tunnel raises catastrophic forgetting**, so this work *defends the A6 continual win*, it is
not a side-quest.

### 0.3 What the rough pass already suggested — and why it is NOT Phase 5

The 2026-06-28/29 research session ran **rough possibility-probes** (3–5 seeds, `PROBE_EP=60`, synthetic only, no
real-readout check, no continual-safety, no natural data). They scoped the search; **they are not results.** Phase 5
re-runs every one under full protocol. The rough findings, as *hypotheses to harden*:

- **H-temp:** sharper InfoNCE temperature (0.5→0.2) at the cheap w=2 window reached tail-L12 ≈ the full-backprop
  ceiling (~0.54 vs ~0.55) at ~1.9× cost vs 11× — *a possibly-free fix.* **Owed:** the temp floor (0.1/0.05 can
  collapse — too few effective negatives), validation on the *real nonlinear readout* (not just the linear probe),
  continual-safety, natural data.
- **H-locality:** composing depth marches with credit reach (w1→L3, w2→L4, w4→L7, w12→L12, no decay) → native depth
  is *curable*, not just routable. (w12 = the **forbidden** full backprop — a diagnostic upper bound only.)
- **Struck (clean negatives, to re-confirm as logged failures):** overlapping windows *hurt* (credit-chain length
  composes depth, not path multiplicity); a naive detached top-down loss term *hurt* (imports the decayed top's
  badness). FTP/PEPITA ruled out (they rewrite the stream).

### 0.4 What Phase 5 is NOT — the scope guard ("keep the menu closed")

- **NOT learned halting / PonderNet, NOT the recurrent loop.** The halting *concept* and the native settling-time
  signal are the **north star's "I-get-it" feeling** — they need a recurrence the Stage-1 feedforward cell does not
  have. **Cut from the committed path** (§8 C2); held for the dream. Building them now is pulling the north star
  forward.
- **NOT genuine global-credit machinery, yet.** DFA/EBD/update-alignment (2601.21683) are **deferred** — re-opened
  only if the cheap levers (temperature, bounded window, readout placement) leave a gap *that matters on the
  continual workload*. The cheap fix may make them unnecessary.
- **NOT a static-accuracy race.** Phase 4 settled that OURS is a continual learner, not a static competitor. Phase 5
  optimizes depth *and cost*, validated against the continual win — not a leaderboard.
- **NOT conv / time-series / large natural data as the claim.** Those need new architecture (north star) or are out of
  behavioral-sim scope. Small flat real probes (digits, CIFAR-flat) are in, as anchors.

---

## 1. The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — preserve / read the class DIRECTION, never a MAGNITUDE.** Rank, variance, contrast-loudness, and
goodness/energy are *magnitudes* — symptoms, not the lever. This is density≠class wearing its 4th coat, and it kills
three tempting-but-wrong moves up front: (a) reading **goodness** to decide where to read (density, not class);
(b) training a residual **α from the local contrast loss** (chases local-objective magnitude → opens the gate at the
drift onset); (c) adding **VICReg/Barlow variance-covariance** to "fix rank collapse" (restores a symptom; its batch
stats rot under continual shift). Read the class direction (**head confidence**), preserve the class direction
(**frozen residual / a class-subspace term**), and steer no fix by a magnitude proxy.

**The envelope — forward-first; bounded global on the GD side; NEVER rewrite the SCFF stream.** Forward-only, local,
per-sample is the default (it is what's cheap on the analog substrate). A *bounded* global/"backward" signal is
licensed only in the GD-side modules (readout, exit, decider) and as a top-down broadcast that *reads/gates*, never
as backprop through the SCFF bulk. **The hard rule (P2.5, `write` kills SCFF):** read-only heads, detached top-down
references, eligibility-trace×modulator updates = OK; **anything that overwrites SCFF activations mid-stack =
forbidden** (this is why FTP and PEPITA are out, even though they work).

**The gate that governs adoption — continual-safety.** A6 (the sleep-recovery continual win) is the architecture's
reason for being. **A fix that dents A6 is rejected, however well it scores on a static probe.** Every adopted change
passes through P5.7 before it is banked.

---

## 2. The structure — three threads, two gates, one synthesis

```
 EARN depth (make it compose)            READ depth cheaply (the cost MVP)
   P5.1 objective sharpness (temp)         P5.3 lost-or-rotated + profiler + truncation floor
   P5.2 credit reach (window; + defer C)   P5.4 per-depth heads vs all-tap
                       \                    P5.5 calibrated early-exit   ◀ STOPPING MARK ①
                        \                  /
                   PRESERVE (conditional 2nd tool)
                        P5.6 frozen near-identity residual   ◀ STOPPING MARK ②
                        |
   GATES (un-skippable):  P5.7 continual-safety   ·   P5.8 natural-data
                        |
                   P5.9 synthesis → the adopted cell + the Phase-6 brief
```

If preservation (Track A / P5.6) carried the extractor to the top, "read the top" *is* "read the extractor" and
placement dissolves. It won't fully (the extractor is task-bounded), so the cost MVP (Track B / P5.3–5.5) reads the
end cheaply. **C** (cheap global direction) is deferred — it enters only if P5.2 proves the gap is locality-bound and
the cheaper rungs underdeliver.

---

## 3. The experiment ladder (cheapest-decisive-first; one variable per rung; 5 seeds; median + IQR)

Each rung is one sharp question, run with the house-style figures (§ [`result-format.md`](result-format.md)) and
written up in the 6+2-slot card. **Every rung is read against one lens — *does this complete SCFF?*** — and each
states, *before* it runs, **what each outcome will mean** (a **Reads** line — or a *pre-registered rule* / *stopping
mark* where the decision is sharp), **including the failure reading**, because a result that changes no decision and
a failure we can't interpret both didn't need running. **Failures are data** — a struck mechanism is logged as a
card, not tuned to pass (the negative-result rule). Conditional rungs fire only if a gap survives. Cards live in
`expK/`; apparatus in `p5lib.py` (§6).

### P5.0 — the bench + decay reproduction + guards `exp0`
- **Question:** does the apparatus reproduce the P4.3 decay and pass its sign-bug guards before any cell runs?
- **Setup:** stand up `p5lib.py` (§6); reproduce the per-layer profile (peak ~L5 → slide) at full protocol on the
  headroom + flat tasks **and the mixed flat+headroom task** (the corruption detector — deep layers overwriting the
  early-solved flat subtask is the cleanest decay tell); establish the w12 **diagnostic upper bound** (full e2e —
  never deployed).
- **Guards (pre-cell, the antidote to the recurring sign-bug):** overlap subclass ≡ `SCFFContrastOLU` bit-for-bit at
  stride=window; residual wrapper α→0 ≡ plain bit-for-bit; FD-gradient check (`max|analytic−FD| < 1e-5`) on every new
  backward path; dead-frac ≈ 0 sanity.
- **Reads:** the profile reproduces P4.3 — **peak within ±1 layer of L5 *and* tail-L12 within the §B real-difference
  band of ~0.43** → the bench is trusted. Outside that band → a porting bug *or* a genuine probe-protocol effect
  (e.g. PROBE_EP 60→120 legitimately moving the peak — distinguish that from a port bug before blaming the port);
  fix the port before any cell runs. **Any guard fails → STOP** — a sign/direction bug (the project's recurring
  killer) would otherwise masquerade as a finding.
- **Decides:** go/no-go on the bench. No *trusted* bench, no results. *(Truncation-ref note: until the P5.3 profiler
  runs, any figure needing a truncation reference uses the provisional P4.3 peak ~L5; P5.3 replaces it with the
  measured profiler peak.)*

### P5.1 — objective sharpness: the (maybe-)free lever, hardened `exp1`  *(hardens H-temp)*
- **Question:** is a sharper InfoNCE the free depth fix — where is the floor, does it survive the *real* readout, and
  is it *free* (objective-sharpness) or partly a **disguised learning-rate increase**?
- **Setup (the swept variable = temperature; window and mask held, not co-swept):** sweep
  `temp ∈ {0.5, 0.35, 0.2, 0.1, 0.05}` at the adopted **window=2**, **mask held at 0.5**, headroom + flat + the mixed
  task, L12, 5 seeds. (Mask is a *separate* one-variable check, not a third axis here; the `window=4` interaction is
  P5.2's `temp×w` combo.) Report the per-layer probe (peak/tail/slope) **and the real nonlinear readout accuracy**.
- **The lr-confound control (MANDATORY):** a lower InfoNCE temperature scales the logits → scales the contrastive
  gradient, so "sharper temp" is *partly* an effective-lr increase (and T0.1 showed lr/passes move the tail ~0.02).
  Add an **lr-matched arm** — either normalize the contrastive gradient to a fixed norm across temperatures, *or*
  sweep lr at `temp=0.5` up to the same effective-gradient-norm as `temp=0.2`. **The "free objective-sharpness" claim
  holds only if temp still composes deeper than the lr-matched `temp=0.5`.** Otherwise the gain is lr, not direction,
  and the §1 spine mechanism is overstated — report it as such.
- **Reads / pre-registered rule:** the committed `temp` = the sharpest value before **collapse** — *defined:* the
  first temp where tail-L12 is **real-worse** (per the §B IQR-disjoint + ≥4/5-sign rule) than the next-milder temp
  (very-sharp contrast collapses for too-few effective negatives) — that **passes the lr-control** and **does not
  fail P5.7**. **Probe ≠ readout:** temp closing the *linear-probe* gap to w12 need not close the *readout-acc* gap
  (T3's caveat — temp0.2 ≈ w12 on the probe but w12 led readout acc by ~0.02); that residual readout gap is what
  P5.2's `temp×w` combo is for. If no temp beats `0.5` on the *real readout* under the lr-control, H-temp is
  **refuted** and the phase leans on P5.2 + the readout MVP.
- **The temp × continual coupling (carry to P5.7):** a sharper contrast is more class-selective on the *current*
  task — plausibly **worse** for forgetting (more aggressive overwriting of prior-task structure, the A6 mechanism).
  Pre-registered resolution: if the sharpest non-collapsing temp **fails P5.7**, fall back to the **mildest temp that
  passes P5.7 and still beats baseline depth** — the continual gate outranks the depth gain.
- **Decides:** the adopted cell's `temp`. The cheapest, highest-leverage knob — run first.

### P5.2 — credit reach: does temperature suffice, or do we need the bounded window? `exp2`  *(hardens H-locality)*
- **Question:** how much composing depth does each credit-reach lever buy per unit backward cost, vs the w12 ceiling?
- **Setup (one variable = credit reach):** window dose-response `w ∈ {1,2,3,4,6,12}` (w12 = the forbidden upper
  bound); the **untested cheap closer** `temp0.2 × w{3,4}` combo; **re-confirm the struck negatives as logged
  failures** — overlap (stride<window) and a naive detached top-down loss term (both predicted to hurt; FD-guarded).
- **Pre-registered gap rule (so the Track-C decision is falsifiable):** "a gap that matters" = the best cheap cell
  (temp, or `temp×w`) is **real-below** (per the §B rule) the w12 ceiling in **both** tail-L12 *and* readout acc on
  the headroom task, **and** that shortfall is *real* on the continual workload (P5.5). Only then does **Track C
  (global credit) re-open**; otherwise it stays deferred. **Citation gate:** verify arXiv `2601.21683` (the basis for
  "Track C may be unneeded") *here*, before the Track-C decision — not at P5.9.
- **Reads:** temp (or `temp×w4`) closes the gap per the rule above → native depth is solved cheaply, Track C stays
  deferred. A real gap survives onto the continual workload → Track C re-opens (top-down broadcast → DFA/EBD, never a
  stream rewrite). Overlap / naive top-down again underperform their baselines → confirmed dead, logged as cards.
- **Decides:** whether native depth is "solved for free" (temperature alone) or needs the bounded window (w4, the
  *backup*); and the Track-C verdict (defer vs re-open), against the pre-registered gap rule.

### P5.3 — lost or rotated? + the profiler + the truncation floor `exp3`  *(new — owed since the rough pass)*
- **Question:** is the decayed info *destroyed* or just *rotated*? Where does the extractor end per task? What is the
  cost floor every later rung must beat?
- **Setup (three separable sub-questions; keep their Reads distinct in the card):** (a) **probe-capacity** — linear
  vs MLP probe per depth (the MLP-probe hyperparameters are pinned in §6; it shares the linear probe's frozen split);
  if the MLP recovers "decayed" layers, the info is **rotated, not lost** → placement over surgery. (b) **the
  profiler** — per-task per-layer probe-vs-depth → placement = the probe peak / slope-flatten, swept over difficulty
  × class-count (confirm "peak rises with complexity"). **Pass/fail vs the real readout:** the profiler peak and the
  real-readout-optimal depth must agree **within ±1 layer**; if they disagree by more, **placement is driven by the
  readout, not the probe** (the probe is then a flagged proxy with a reported gap). (c) **the truncation baseline** —
  a **from-scratch** SCFF stack of depth `peak + 1` (**margin = +1 layer**; `peak` = the profiler argmax, provisional
  ~L5 until measured), trained with the **adopted cell's exact temp / window / seeds / budget**, read at the top.
  *(Matched budget is non-negotiable — an under- or over-trained truncation is an unfair floor in either direction.)*
- **Reads:** the MLP probe recovers the "decayed" deep layers → the class info is **rotated, not destroyed** →
  cheap *placement* beats objective-surgery (the good-news outcome). The MLP can't recover it → genuinely **lost** →
  preservation / objective work is needed (P5.1/P5.6). The profiler peak **rises with task complexity** → the
  *trigger* (task-set extractor length) is confirmed on our cell and placement = the peak. Truncation already matches
  the full stack → the simplest answer wins.
- **Decides:** the lever class (placement vs objective-surgery); the operational "where to read"; and **the
  truncation floor — the control every tier above must beat** (fewer layers = fewer Scaps = cheaper silicon; if
  nothing beats truncation on the continual workload, ship the truncation).

### P5.4 — the readout MVP: per-depth heads vs all-tap `exp4`  *(new — T1.1, accuracy)*
- **Question:** do per-depth deep-supervision heads match all-tap accuracy at lower cost?
- **Setup (one variable = readout structure):** a tiny Mono-Forward-style local head at each SCFF depth (projection →
  local CE — pure `read`, per-sample, no batch stats, the one borrowed mechanism with a forward-only precedent).
  Baseline = **all-tap** (the thing it replaces). Per-head accuracy must reproduce the P5.3 profiler.
- **Capacity & protocol control (MANDATORY — else a heads-vs-all-tap gap is a capacity/training confound, not a
  placement result):** the per-depth heads and the all-tap readout must share the **same readout training protocol**
  (epochs / lr / hidden width) and be compared at **matched total readout parameters** — either cap all-tap to the
  heads' total params, or scale the heads to all-tap's. The comparison must isolate *structure/placement*, not
  capacity. Heads are **refit on whatever frozen stack variant is under test** (so the P5.6 "residual vs not" curve
  is valid).
- **Reads:** heads match all-tap accuracy at lower cost → adopt heads as the readout base (placement becomes
  possible). Heads trail all-tap → the all-tap/boosting readout stays load-bearing and placement must come from
  elsewhere. Per-head accuracy reproduces the profiler → the heads *are* the profiler (one mechanism, two uses).
- **Decides:** heads-at-each-depth as the readout base **iff** they match all-tap's accuracy at lower cost.

### P5.5 — calibrated early-exit on the CONTINUAL workload `exp5`  *(new — T1.2, cost — STOPPING MARK ①)*
- **Question:** does placement + a calibrated exit beat all-tap **and** truncation on the *continual* workload?
- **Setup (the swept variable = the exit gate). Gate statistic (pinned):** **head max-softmax probability**
  (class-confidence — *not* entropy-of-energy, *not* goodness; the spine), thresholded; exit at the **shallowest head
  whose max-softmax ≥ τ**. **Not** a learned halting policy (cut, §8 C2).
- **Calibration (pinned, CALM-style):** `τ` = the lowest threshold holding **≥ 95% of all-tap accuracy** on a
  **calibration split disjoint from test**. Test **both** a *one-shot* `τ` (calibrated once on early data) **and** a
  *per-task-refit* `τ` — *which one is needed is itself the cost question* (the stopping mark).
- **Expected-compute (the cost headline — a FORWARD meter, new in `p5lib`; NOT the P4 backward meter):**
  `E_compute = E_stream[ exit_depth·(per-layer SCFF forward MACs) + Σ_{ℓ≤exit}(head_ℓ MACs) + gate MACs ]`,
  reported in **forward-MACs** (one commensurated unit). all-tap and truncation use the *same* formula (all-tap = all
  L + all heads; truncation = `k` layers + 1 head) so the three are comparable.
- **The distribution shift (pinned):** the **P4.5 class-incremental stream** — `τ` calibrated on the **early tasks**,
  evaluated on the **later tasks** (the ship regime).
- **Spine risk (named, not hidden):** class-confidence is itself a *magnitude*, and confidence **mis-calibrates under
  shift** (a head can be confidently wrong on a drifted class — a softer version of the goodness trap the spine
  bans). So calibration is **validated on the shifted distribution** (CALM's guarantee is i.i.d.), and a
  **true-class-margin oracle** exit is added to bound how much confidence-as-proxy loses vs the class *direction*.
- **Controls:** the **oracle-exit upper bound** (best per-input layer — if the oracle gain is small, no gate can save
  us; the problem is in the representation → back to P5.1/P5.6), on the continual workload. *(Heaviest rung — 3 seeds,
  checkpoint-mandatory, single-thread-verified; §6.)*
- **STOPPING MARK ①:** T1 "restores the 80/20" **only if** `E_compute` on the *continual* workload beats all-tap
  **and** truncation, accuracy held, **under the one-shot `τ`**. **Pre-registered C5-pessimistic branch:** if exit
  wins on i.i.d. but **not** on the continual stream — *or* if `τ` must be **re-fit per task** to win (refit cost
  enters the 80/20 math) — then **placement is static, not adaptive**, and the honest verdict is *"ship truncation /
  all-tap on the continual stream"* (a complete answer, not a failure). Known **here, not at P6.** If it clears the
  bar under a one-shot `τ`, depth is *practically solved* and SCFF is "done"; P5.6+ are improvements.

### P5.6 — preservation: frozen near-identity residual `exp6`  *(new — T2, conditional — STOPPING MARK ②)*
- **Question (conditional — run iff P5.1+P5.4/5.5 leave a gap):** does a frozen near-identity skip preserve the
  extractor so deep layers can only *add*, not overwrite?
- **Setup (one variable = the residual):** wrap each SCFF block `y = x + α·f(x)` with **α FROZEN** (**pinned α = 0.1**
  near-identity; Fixup-style — the structural win is from the *initialization*, needs no training signal; a
  *local*-loss-trained α opens the gate exactly at the drift onset, §8 C3). Learned-α allowed **only** if driven by
  the GD-readout (class-direction), never local contrast, never goodness.
- **Mandatory test design:** **per-block α→0 ablation** (set α literally to 0 ≡ the plain stack, the P5.0 guard — a
  dead-tiny frozen α also "stops the tail decaying," so prove each block *contributes*, else it's a bypass-cheat, not
  a fix); and the **S5 mandatory-norm × residual interaction** — a length-norm after a near-identity skip projects
  onto the unit sphere, **discarding the magnitude *along* the preserved class direction**, so this is a
  direction-vs-magnitude interaction (the spine), not a mere rescale — test it, don't assume. If a learned
  preservation term is wanted, prefer a **per-sample class-subspace** term over VICReg/Barlow.
- **The pass/fail:** the **mixed flat+headroom task** — preservation works iff the residual **stops the deep layers
  corrupting the early-solved flat subtask** (the ~0.67→0.51 corruption tuned BP doesn't have), with the per-block
  ablation proving each block contributes.
- **STOPPING MARK ②:** preservation makes depth **safe to read**, not **unbounded to use** (the extractor stays
  task-bounded). A cheap test, not a tier of commitment.

### P5.7 — continual-safety: the home-turf gate `exp7`  *(new — the spine)*
- **Question:** does each adopted change (the re-tuned temp, the heads, any residual) **preserve the A6
  sleep-recovery win**?
- **Setup:** the **`continual_harness`** promoted into `p5lib` (§6) from the P4.5/P3.3 class-incremental + sleep
  apparatus (the *actual* validated A6 mechanism — the sleep/consolidation loop, currently living in
  `phase3/exp3/run_p3_3.py`, not yet a library function). Measure BWT / AA / retention of each candidate change vs
  the **P4.5 baseline**, budget/protocol-matched (digits home + swept difficulty, 3 seeds). Run as a **checkpoint on
  every committed change**, not just a final rung. **Resolution of the temp × continual tension (from P5.1):** if the
  sharpest non-collapsing temp fails here, adopt the **mildest temp that passes here and still beats baseline depth**
  — the gate outranks the depth gain. *(Heaviest rung — 3 seeds, checkpoint-mandatory, single-thread-verified.)*
- **Reads:** BWT / AA / retention hold vs the P4.5 baseline → the change is **continual-safe**, bank it. They
  degrade → the change is **rejected** regardless of its static-depth score (a sharper temp, or a longer composing
  stack, could worsen class-incremental drift — that is a result, not a thing to tune away).
- **Decides:** the gate. A change that fails here is reverted regardless of its static score.

### P5.8 — natural-data confirmation `exp8`  *(new — the synthetic-artifact gate)*
- **Question:** do the decay **and** the adopted fixes hold off synthetic data?
- **Setup:** digits (64-D) + CIFAR-flat (3072-D) — the in-scope flat anchors — overlaid on the headline curves
  (DEPTH-PROFILE, EXIT-PARETO). The whole diagnosis is synthetic; this is a first-class gate (the review's strongest
  validity flag), not an afterthought.
- **Reads:** the decay *and* the adopted fix reproduce on digits/CIFAR-flat → the synthetic story is real, commit
  it. The decay vanishes on real data → it was partly a synthetic artifact, re-scope the claim. The fix works on
  synthetic but not real → do **not** commit it.
- **Decides:** whether the synthetic story is real or an artifact (no real class manifold to preserve).

### P5.9 — synthesis + assembled-cell confirmation: the depth-readout verdict + the Phase-6 brief  *(README + phase5-report)*
- **Assembled-cell confirmation (RUN, not just synthesize — levers don't stack linearly):** before the verdict, run
  the *adopted* cell (the committed temp + window + readout placement + residual-if-any, **all together**) end-to-end
  on **DEPTH-PROFILE + EXIT-PARETO + CONT-SAFETY + NAT-ANCHOR**. The per-rung wins were measured
  one-variable-at-a-time; this confirms they hold *combined* (T0's "cheap levers may not stack linearly" caution). A
  combined regression here **overrides** the per-rung optimism.
- The adopted cell (temp / window / readout placement / residual y-n); is SCFF "done"? The decision-record deltas
  (§8); the hand-off to **Phase 6** (continual optimization, now readout-aware — consolidate *extractor-depth*
  features; the sweet spot **moves under shift**, so the gate must be re-validated online). **Update the
  `ref-report/` glossary** with the phase's new citable terms (composing-depth, expected-compute, truncation floor,
  …) at close.
- **The verdict (the phase question answered):** SCFF is **"done"** iff it composes the depth a task needs **and**
  reads it cheaper than all-tap *and* truncation on the continual workload, continual-safe (P5.7), on real data
  (P5.8). If not, the honest scoped verdict is the deliverable too — e.g. *"ship the truncation"* or *"native depth
  caps at ~k layers, lean on the boosting readout"* — a complete answer that **closes the SCFF side** and hands a
  *known* cell to the GD-optimization era (Phase 6).

---

## 4. The metrics (PINNED) — what "solve depth" means here

Carry the canonical set ([`../result-format.md`](../result-format.md)); the Phase-5 additions are in **bold**.

| metric | definition (pinned) | what it answers |
| --- | --- | --- |
| **composing-depth** | per-layer linear-probe: **peak layer** (argmax) + **slope L1→L12** + **tail-L12** | does depth compose or decay, and how far |
| held-out / readout accuracy | OURS readout (the *real* nonlinear head), median + IQR | raw performance (the profiler is a proxy with a known gap) |
| **probe-capacity** | linear-probe vs small-MLP-probe per depth | decayed info **lost** (MLP can't recover) vs **rotated** (MLP recovers) |
| **placement accuracy** | per-depth-head accuracy vs all-tap; the profiler peak | where the extractor ends; does heads match all-tap cheaper |
| **expected-compute (continual)** | **forward-MACs:** `E_stream[ exit_depth·SCFF_fwd_MACs + Σ_{ℓ≤exit} head_ℓ_MACs + gate_MACs ]`, on the *continual* stream (not i.i.d.) — a FORWARD meter (the P4 meter is backward-only); all-tap/truncation use the same formula | the 80/20 cost, measured where we live |
| **oracle-exit gap** | best-per-input-layer accuracy − gated accuracy | headroom of any gate (small ⇒ gating can't save us) |
| **per-block contribution** | Δ(tail/acc) under per-block α→0 ablation | dead-gate guard — is the residual real or a bypass |
| **continual BWT / AA / retention** | GEM/CL-survey conventions, re-tuned cell vs the P4.5 baseline | **the gate** — does the fix keep the A6 win |
| backward cost (substrate) | credit-distance × weights **+** #backward updates; **labelled substrate work, never "energy"** | the 80/20 claim, scoped honestly (carry P4) |
| **temp floor** | tail-L12 / readout acc vs temperature, collapse point marked | the safe sharpness before too-few-negatives collapse |

**Calling a difference real (n=5, carry):** real only if **IQR bands are disjoint at the final checkpoint** *and*
the **sign is consistent in ≥4/5 seeds, paired by seed**; else "within noise."

---

## 5. Tasks

| role | task | why |
| --- | --- | --- |
| **the decay dial** | **headroom** (`make_tierb`, depth *should* pay) + **flat** (`make_gauss`, known Bayes, depth shouldn't) | the two regimes the decay appears in (flat peaks earlier — the easy-task-shallow-extractor prediction) |
| **the corruption detector** | **mixed** flat+headroom (iso-budget) | the cleanest decay tell (deep layers corrupt the early-solved flat subtask) |
| **natural confirm (P5.8)** | **digits** (64-D), **CIFAR-flat** (3072-D) | the synthetic story must survive real flat input |
| **continual (P5.7)** | class-incremental digits + swept difficulty (P4.5/P3.3 exact) | the home turf the fix must not break |
| **deferred** | conv-image, time series, large natural data | north-star / needs-architecture (§0.4) |

Seeds `[42,137,271,314,1729]` (3 for the heaviest continual cells P5.5/P5.7), median + IQR, single-threaded (phantom
guard), `PROBE_EP=120` for any cited number (the rough pass used 60 — shape-robust, third-decimal-noisy; Phase 5
cites the full probe). **Power note:** the decisive gaps are small (temp0.2-vs-w12 ≈ 0.01 tail, 0.02 readout) and
n=5 IQR-disjoint may not resolve a 0.01 effect — **bump to ~9 seeds** (add `[1009, 2027, 9091, 7]`) on any rung whose
*decisive* gap is ≤ 0.02 (P5.1/P5.2), so the rung can actually call the difference it exists to adjudicate.

---

## 6. What to build — `p5lib.py` (the apparatus, on the rough seed code)

Reuse `p3lib` (`SCFFContrastOLU`, layernorm VJP), `p4lib` (generator, exact Bayes, `fit_readout`/`readout_feats`,
`linear_probe`, the **backward** cost meter, the racers, the digits anchor), `p2lib` (norm/relu/`effective_rank`).
**Add (with the pinned specs the rungs depend on — these close the executor-review blockers):**

- **`SCFFContrastOverlap(window, stride, temp, mask)`** — promote verbatim from `t3/run_t3.py` (the equivalence guard
  `stride=window ≡ SCFFContrastOLU` already passes); the credit-reach + temperature cell. The **lr-matched arm**
  (P5.1) = a gradient-norm-normalization option on this class.
- **`PerDepthHeads`** — a tiny local-CE projection head at each SCFF depth (Mono-Forward pattern), pure `read`,
  per-sample. **Refit on whatever frozen stack variant is under test** (plain / residual). Shares the all-tap
  readout's training protocol (epochs/lr/width) and is compared at **matched total readout params** (P5.4).
- **`CalibratedExit`** — head **max-softmax** gate (class-confidence, the spine — *not* goodness), `τ` calibrated to
  hold ≥ 95% of all-tap acc on a **calibration split disjoint from test**; supports **one-shot** and **per-task-refit**
  `τ`; + the **true-class-margin oracle** and the **oracle-exit** (best-per-input-layer) computations (P5.5).
- **`forward_cost` / `cost_stream`** — the **FORWARD** expected-compute meter (NEW — the P4 meter is backward-only):
  `E_stream[ exit_depth·SCFF_fwd_MACs + Σ_{ℓ≤exit} head_ℓ_MACs + gate_MACs ]` in **forward-MACs**; plus
  `cost_heads(L,Wd,C)` and `cost_gate(...)`. Head *inference* cost counts toward the 80/20; head *training* cost is a
  one-time sleep-side cost, reported separately.
- **`FrozenResidual`** — `y = x + α·f(x)`, **α frozen = 0.1**, with a per-block **α→0** ablation switch. *(Guard: ≡
  plain at α=0.)*
- **`profiler()`** — per-layer probe → extractor-end estimator; the **±1-layer agreement check vs the real readout**
  (P5.3).
- **`mlp_probe()`** — the lost-vs-rotated probe: an `[F, H=64, C]` MLP using the **same frozen 2k/2k split, epochs,
  lr, L2 as `linear_probe`** (only the hidden layer differs — so "rotated vs lost" can't be a probe-tuning artifact).
- **`truncation_racer`** — a **from-scratch** `L = (profiler_peak + 1)` SCFF stack (margin = +1), **adopted
  temp/window/seeds/budget**, read at top (the floor). NOT the first-`k` layers of the L12 stack (different
  layer-norm dynamics).
- **`make_mixed`** — the iso-budget flat+headroom generator (the corruption detector; NEW — absent from the seed
  code): **equal sample count per subtask, equal class count**, the two subtasks **disjoint in label space**; carries
  `te_masks` so the per-subtask probe (the ~0.67 flat number) can separate them.
- **`continual_harness`** — **promote** the sleep/consolidation loop (`run_condition` + `synth_stream` +
  `load_digits_split`) from `phase3/exp3/run_p3_3.py` & `phase4/exp5/run_p4_5.py` into a clean `p5lib` callable.
  **This is real build work, NOT a reuse** — the A6 mechanism currently lives only inside an exp-card, imported via a
  `sys.path` hack. P5.7 depends on it.
- **natural-data loaders** — digits via `load_digits_split` (in `run_p3_3`); **CIFAR-flat** — confirm/port its loader
  (P4.4 used it as a 1-seed sanity) and point `p5lib` at it.
- **guards** — equivalence (`overlap≡OLU`, `residual α→0 ≡ plain`) + FD-gradient (`<1e-5`) on every new backward path,
  run before any cell (P5.0).
- **reproducibility (carry, non-negotiable)** — `manifest.json` (git hash + resolved config + seeds + versions +
  wall-clock) + `arrays.npz` per run, **to the array-schema pinned in [`result-format.md`](result-format.md) §A** (so
  `regen` is portable across rungs); `plot_p5.py regen <run-dir>` redraws every figure from saved data; per-cell
  `_ckpt.jsonl` fsync'd (resumable); thread caps before numpy import + `python -u` + `PYTHONIOENCODING=utf-8` (the
  OpenMP-phantom + cp874 guards).

**Rough per-rung wall-clock (so the heavy cells are budgeted, not surprises):** P5.0–P5.4 are probe-sweeps
(~30–60 min each, 5 seeds). **P5.5 (continual + oracle-exit) and P5.7 (continual-safety) are the heaviest** —
continual streams × per-input-layer oracle × seeds — run them **3-seed, checkpointed, single-threaded, multi-hour**,
and **verify the real PID is alive** (the 14-hr-ghost guard, per the OpenMP-phantom memory).

---

## 7. The success criterion + the two stopping marks

> A cell that **composes useful depth** (peak marches deeper, tail stops decaying) **and reads it cheaper than
> all-tap *and* cheaper than the truncation floor — on the *continual* workload**, validated to preserve the A6 win
> (P5.7) and to hold on natural data (P5.8). Or an honest verdict that the truncation floor wins and we **ship fewer
> Scaps.** Not "we beat backprop"; a *solved, costed, continual-safe* depth story. **Either way it COMPLETES THE SCFF
> SIDE** — the cheap brain is finished and trusted — and the project pivots to optimizing the GD side (Phase 6+).

**Two verdicts, reported SEPARATELY** (the phase can pass one and not the other — collapsing them lets an honest
"ship the truncation" mask an unanswered earn-depth question):
- **Depth-earned** (the EARN thread, P5.1/P5.2): SCFF *composes the depth a task needs* iff, on the headroom task,
  the adopted cell's **tail-L12 is within the §B real-difference band of the w12 ceiling** *or* its **probe peak ≥ the
  profiled extractor depth**. Without this bar the phase could close "done" while leaving native depth — the
  architecture's identity (§0.1) — only partly answered.
- **Read-cheaply** (the READ thread, P5.4/P5.5): STOPPING MARK ① — beats all-tap *and* truncation on the continual
  workload under a one-shot `τ`.

SCFF is **"done"** when **both** hold (continual-safe P5.7, on real data P5.8). If only read-cheaply holds → the
scoped verdict ("native depth caps at ~k → lean on the boosting readout"); if only depth-earned holds → the cost win
is owed to Phase 6. The §9 open-items track whichever is unmet.

- **STOPPING MARK ① (P5.5):** if the readout MVP clears the continual-cost + distribution-shift bar, depth is
  *practically solved* and SCFF is "done." **The honest minimum is likely P5.0–P5.5** (the readout + the free temp
  re-tune). P5.6+ are improvements.
- **STOPPING MARK ② (P5.6):** preservation buys "read-top convenience," not "unbounded depth" — a cheap test, not a
  tier of commitment.

---

## 8. The decision record (the 4-Opus-agent review — authoritative for the plan logic)

On 2026-06-28 four Opus-4.8 subagents rechecked the plan through different lenses (cold outsider · red-team · insider
auditor · substrate checker). The spine of every change:

> **THE META-INSIGHT.** Three of the sharpest findings — the Tunnel Effect's rank reading, the ReZero-α signal, and
> the whitening lever — all circle the SAME trap: mistaking a **MAGNITUDE** (rank, variance, contrast-loudness,
> goodness/energy) for the **DIRECTION** that carries class information. **Preserve the class DIRECTION, not the
> magnitude.** (density≠class, 4th appearance.)

**KEEP / CHANGE / CUT ledger:**

| Item | Verdict | Why |
| --- | --- | --- |
| Diagnosis (trigger × multiplier; abstraction-*saturated*) | **KEEP** | survives all evidence; no prior-phase contradiction |
| Reframe (where-to-read) | **KEEP + harden** | legit posture; the P5.2 locality control stops it *assuming* |
| Deep-supervision heads (Mono-Forward-style) | **KEEP — the base** | cheap, proven forward-only, pure `read`, all four agreed |
| Confidence early-exit | **KEEP — but *calibrated*, on head-confidence (class), continual-cost-tested** | C1/C2/C5 |
| Native goodness/energy as *placement* signal | **CUT** | density≠class (C1) |
| Native settling-time as *halt* signal | **PARK → north star** | needs recurrence Stage-1 lacks (C1) |
| Learned halting (PonderNet) | **CUT from committed path; hold concept for north star** | over-engineering; pulls north star forward (C2) |
| ReZero residual (Track A) | **CHANGE → frozen/init-based α; learned-α only via GD-readout; +per-block α→0 ablation** | C3 |
| Preservation target | **CHANGE → preserve class DIRECTION, not rank/variance** | meta-insight; C8 |
| Whitening (VICReg/Barlow) | **CUT as the lever; on the menu with rejection rationale** | symptom not cause; batch-stat/continual conflict (C8) |
| Tunnel Effect as keystone | **DEMOTE → loose analogy; subordinate the rank reading** | capacity-relative, supervised, info-destroying-not-preserving (C4) |
| Top-down / DFA / FTP (global direction) | **PARKED — re-open only if P5.2 says locality-bound and cheap levers fall short** | C6/C7 |
| MoE / SSM / layer-skip | **PARKED (broader lazy-brain track)** | not the depth fix |
| "minimum = readout + temp" | **KEEP as target — must pass the continual-cost + distribution-shift bar to earn it** | C5 |
| Novelty framing | **QUARANTINE** | the bar is "reads cheaply + correctly," not "is it new" (scope-creep) |

**Other adopted catches:** harden P5.1 into a 2-D grid with a pre-registered rule, no pre-committed prior;
probe-capacity control (P5.3); validate the profiler vs the real readout; oracle-exit bound; split the readout MVP
into accuracy (P5.4) then cost (P5.5); natural-data into P5.8; the S5-norm × residual risk (P5.6); self-distillation
("Be Your Own Teacher") as a forward-compatible Track-B option; the InfoPro/greedy-locality companion literature;
**citation hygiene** (verify post-cutoff arXiv IDs — 2601.21683, 2603.01914 — before any becomes a *decision*
citation). **Where the leader overruled:** the reframe is *not* a rationalization (it brackets the science honestly +
adds the P5.2 control); settling-time is north-star, not Stage-1; deep-supervision heads survive every lens.

---

## 9. Open items / scope

- **Decision-record deltas (commit to `idea/main.ideas.v1.md` only after P5.0–P5.5 give results):**
  **S9** — readout placement is adaptive (per-depth heads + a *calibrated class-confidence* exit), revising S3's
  literal "tap ALL layers" (S3's *intent* — read the good early layers — is kept; the *mechanism* changes). The
  Tunnel Effect enters the citebase as a **named analogy**, not a theory. ReZero/Fixup enters as **init-based**
  preservation (frozen α).
- **Phase renumber sync (pending — corrected list, verified by grep):** the docs that actually carry
  "P5 = optimization" are **`../../CLAUDE.md`** (draft-6 status section, lines 25/32), **`../../context.md`** (l.27),
  **`../../idea/main.ideas.v1.md`** (status), **`../stage1-report.md`** (l.131/162/168), and the **status skill**
  (`../../.claude/skills/status/SKILL.md`). Flip these from "P5 = optimization" to "P5 = depth-readout fix / P6 =
  continual optimization" **when Phase 5 closes** (or when the plan locks after the next-session review) — not
  retro-edited mid-flight. **The repo-root `../../../CLAUDE.md` is phase-agnostic and is NOT in this list.** (Phase-4's
  frozen docs keep their "P5 = optimize" forward-refs, period-correct.)
- **Deferred to Phase 6 (the old Phase 5):** sleep cadence + the Ch7 gate, now readout-aware (consolidate
  extractor-depth features; LUT stores extractor-depth prototypes; re-validate the gate online under shift); plus the
  Phase-4 follow-ups (train-with-noise A7, natural-data multi-class A5).
- **Deferred to the north star (Phase 7+):** learned halting, the native settling-time halt signal, the recurrent
  neocortex↔hippocampus loop — where the cut Stage-1 over-engineering comes home.
- **Owed before any rough number becomes a *decision* citation:** the full-protocol re-run (5 seeds, `PROBE_EP=120`,
  real readout) — the rough T0/T3 numbers in §0.3 are *hypotheses*, not results.

---

## 10. References

The mechanism stories: [`../../research/papers/phase5/`](../../research/papers/phase5/README.md) — the cheap-credit
survey + the three tracks (preservation / adaptive-readout / cheap-direction), with verified arXiv IDs.

The evaluation-methodology canon (carry from Phase 4): **gap-to-tuned-BP swept across scale** — Bartunov 2018
([1807.04587](https://arxiv.org/abs/1807.04587)); **tuned-BP baseline + cost Pareto, "don't trust theoretical
savings"** — Spyra 2025 ([2511.01061](https://arxiv.org/abs/2511.01061)); **continual = AA/BWT/FWT/forgetting** — CL
survey ([2302.00487](https://arxiv.org/abs/2302.00487)), GEM ([1706.08840](https://arxiv.org/abs/1706.08840)).
Phase-5-specific: **deep supervision** (DSN, Lee 2015; Mono-Forward [2501.09238](https://arxiv.org/abs/2501.09238));
**calibrated early-exit** (CALM, Schuster 2022; BranchyNet [1709.01686](https://arxiv.org/abs/1709.01686); SDN, Kaya
2019); **init-based preservation** (ReZero [2003.04887](https://arxiv.org/abs/2003.04887); Fixup
[1901.09321](https://arxiv.org/abs/1901.09321)); **greedy-locality info-collapse** (InfoPro
[2101.10832](https://arxiv.org/abs/2101.10832)); **local-vs-BP-SSL** (2601.21683); **the analogy** — Tunnel Effect
([2305.19753](https://arxiv.org/abs/2305.19753)). Carry-overs: the Phase-3 cell ([`../phase3/README.md`](../phase3/README.md)),
the Phase-4 map ([`../phase4/README.md`](../phase4/README.md)), the `result-format` lineage.
