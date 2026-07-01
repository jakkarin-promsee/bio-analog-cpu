# Phase 7 — The Readout (the GD-stage namer): the plan

> **Status: 🟢 LOCKED-FOR-RUN (designed 2026-07-01; 3-agent lab-manager review folded in; ready to run next session).**
> A *live spec an agent executes* — the experiment ladder + build plan for **choosing the namer that puts our labels on
> the frozen SCFF bulk.** No results yet; when rungs run they fill `expK/experiment-K.md`, `RESULTS.md`, then the public
> `README.md` + `phase7-report.md`. Reporting contract: [`result-format.md`](result-format.md). The literature behind
> every mechanism: [`../../research/papers/phase7/`](../../research/papers/phase7/README.md) — **including the 2nd-pass
> audit** [`analytic-and-covariance-readouts.md`](../../research/papers/phase7/analytic-and-covariance-readouts.md) that
> widened the candidate set. The frozen Stage-1 cell this reads:
> [`../phase6-final-architecture.md`](../phase6-final-architecture.md). The Stage-2 map this sits in:
> [`../stage2-design.md`](../stage2-design.md). The lab-manager review that hardened this spec is ledgered in **§8.1**.
>
> **Phase 7 = the first of three GD-stage phases** (P7 readout · P8 economy+cost · P9 maintenance). It is the part that
> makes the cheap brain *usable*: SCFF sorted the world into "kinds of things"; **P7 puts *our* names on the kinds.**

---

## 0. Why Phase 7 exists — the problem, and what it is NOT

### 0.0 The arc — Phase 7 names the frozen bulk, and it is the first GD phase

Stage 1 built, characterized, closed-out, and noise-hardened the cheap brain — the frozen `NoiseAugContrast` cell
(`SCFFContrastOverlap` temp0.2 / w2, L12, no residual, **+ one iid-noise-augmented InfoNCE view σ_aug=1.0**). It
**organizes the world unsupervised but never learned our labels.** Phase 7 is the **~20% precise brain** that maps its
features → real classes — **read-only on the frozen bulk** (GD reads via taps, never writes: P2.5's forward-leak wall +
BYOL stop-gradient). Every knob from here on is on this back, not the SCFF front.

### 0.1 The reframe that defines Phase 7 (the author's call — Q1, load-bearing)

**The "20% GD" is NOT gradient-descent-as-religion.** It is the *cheat-everything* half — the motto "copy the brain's
*function*, cheat the *implementation*" applies hardest here. The namer may be **anything** that maps frozen features →
labels cheaply and continual-safely: a gradient head, a **closed-form prototype**, a **streaming recursive-least-squares
classifier**, a tiny MLP, something weird. So:

> **Phase 7 is a bake-off of *namers*, not a tuning of a GD head. The referees are the SPINE (read direction, not
> magnitude), FORGETTING (BWT), and continual-safety. "The winner uses no gradient at all" is a *feature*, not an
> awkwardness — it makes the 20% cheaper *and* more spine-aligned.** 🔥

**The convexity frame (why this is smaller than it looks) + the two hedges (load-bearing).** Because the bulk is *frozen
to the namer*, the learning is reservoir/ELM-like → a trained linear/logistic head on fixed features has **no bad local
minima** → no heavy-optimizer zoo. **Hedge (a):** "convex" names the *regression*, **not** the *deployed readout's
substrate cost* (the softmax/L2-normalizer/Gram-solve is a non-free digital block — **that is Phase 8's meter, not
ours**). So in Phase 7 **cost is a DESCRIPTIVE axis only — never a decision tie-break** (the spine is the tie-break); no
"cheaper ⇒ prefer" move is licensed here, and every cost number carries the "(proxy; real meter = P8)" tag. **Hedge
(b):** we are reservoir-*like*, **not a reservoir proper** (trained-then-frozen, not random) → we inherit readout
convexity but **not** free noise-tolerance, and convexity is *per-step against a **drifting** comparator* → **tracking
the drift is the real cost, not solving the regression.** Both hedges are *tested*, not asserted (P7.0's
random-projection control tests (b) directly; the drift cost is P9's).

### 0.2 What the 2nd-pass research sharpened — the widened candidate set (the audit)

The rough plan fixed the bake-off on `{linear-softmax, cosine, NCM, RanPAC}` — **spine-correct but incomplete.** A
deeper pass (audit: [`analytic-and-covariance-readouts.md`](../../research/papers/phase7/analytic-and-covariance-readouts.md))
found the training-free / frozen-backbone CIL-classifier field is a hot 2022–2026 area with **two families and one
control the rough pass missed.** The changes, each reshaping a rung:

1. **The Analytic Continual Learning / recursive-least-squares family — headed by F-OAL (Forward-only + Online +
   analytic, arXiv 2403.15751, NeurIPS 2024; = the paper first posted as AOCIL, same work).** No-gradient streaming
   naming is **a published paradigm**, not a hopeful bet: RLS on frozen features is **algebraically equal to joint
   training** (ACIL, 2205.14922), so *no forgetting by construction*, and **F-OAL is forward-only + online + no-gradient
   — our exact constraint.** RanPAC is *one point* in this space. **This is the biggest change: the "no-gradient namer"
   bet becomes "adopt an on-constraint paradigm."**
2. **FeCAM (per-class covariance Mahalanobis, 2309.14062, NeurIPS 2023) — the closed-form multimodality escape AND the
   max-magnitude spine pole.** It removes the false "non-convex mixture or bust" framing (a shaped per-class Gaussian
   captures heterogeneity closed-form, no gradient) **and** it is the field's accuracy SOTA among training-free heads —
   while being the *most* magnitude-based readout (whitened Mahalanobis; whitening was rejected-as-a-lever in P5). So it
   **sharpens** the spine bake-off instead of dodging it. **Deep SLDA (1909.01520)** is the cheaper *middle* of this
   covariance ladder (one **tied** covariance, not per-class) — the substrate-friendlier covariance head, added to the
   core race.
3. **GKEAL (Gaussian-kernel analytic, CVPR 2023 — *few-shot* CIL, CVF-only, no arXiv) — the closed-form *non-linear*
   fallback** below FeCAM on the multimodality ladder. We adopt its **kernel mechanism**, not a general-CIL result
   (its published regime is few-shot).
4. **The random-projection control (RanDumb, 2402.08823 — "random projection + simple classifier beats online-learned
   reps") — the skeptic that operationalizes hedge (b) into an experiment:** *does our trained SCFF bulk even beat a
   random projection at the readout?* If not, the 80% didn't earn its keep *at the naming stage.* **Run it two ways**
   (§P7.0): **random-from-taps** (a random projection of the SCFF tap output — the fair "did the bulk's *representation*
   beat a random one of the same input the readout sees") and **random-from-pixels** (true RanDumb — random projection
   of the *raw input* — the harsher "did the 80% earn its keep at all"). **A load-bearing control the rough pass omitted.**

**The scope caveat that governs every cited number (repeat, because it is the honesty of the phase):** every paper above
runs on a **large pretrained ViT/ResNet** (ImageNet-scale, 512–10k-D). Ours is a **64-wide flat SCFF bulk trained on the
task itself.** We adopt the **mechanisms**, never the absolute numbers — as Phase 3 adopted GIM/CLAPP's objective on flat
vectors without their structured-data results. **A specific consequence:** RanPAC's "ridge-on-a-random-expansion beats
NCM" is a **high-input-dim** result (768→10,000-D, ~12×). From 64-wide features a comparable expansion is ~156× into a
10k² Gram / 10k³ solve, and the *separability benefit itself* (not just the cost) is **unestablished at low input dim**
— so a null on the projection at our scale is **expected, not surprising**, and the random-projection control adjudicates
it empirically. *(The 2025 covariance-adaptation line — DPCR 2503.05423, task-recency-bias-strikes-back 2409.18265, FoRo
2509.01533 — is acknowledged; we adopt mechanisms, not those numbers, and add no rungs for them.)*

### 0.3 What the research suggests — hypotheses to harden (NOT results)

Candidate answers the bake-off runs under full protocol. As **hypotheses**, never findings:

- **H-cosine (the spine bet):** the direction-pure cosine head **matches** the recency-robustness (BWT) of the
  magnitude-based no-gradient SOTA (FeCAM / SLDA / RanPAC-RLS) at ≤ a small accuracy cost — so we get spine-cleanliness
  ~free. **Owed:** the price, if any; whether it holds on natural data + through the continual gate.
- **H-analytic (the cheap bet):** a no-gradient recursive-least-squares head (RanPAC / F-OAL-style / SLDA) matches or
  beats the GD linear-softmax floor on accuracy×BWT, at substrate-native cost (running Gram + solve). **Owed:** the
  solve/projection cost proxy (real meter = P8); whether it survives our tiny 64-wide features — the projection may or
  may not earn its keep (a high-dim result, §0.2), and the random-projection control adjudicates.
- **H-multimodal (the cliff):** SCFF makes some classes multi-modal in the frozen space → one prototype underfits → the
  covariance heads (SLDA tied-cov → FeCAM per-class-cov) or GKEAL's kernel recover it **closed-form** (the convex/analytic
  story survives) before any non-convex mixture is needed. **Owed:** the multimodality probe on the **natural** tap
  space (the decision-bearer — the synthetic blob task only sanity-checks the apparatus); where on the ladder accuracy
  recovers.
- **H-imbalance:** the drift-gated bursty stream chronically imbalances the head → a trained-softmax head shows recency
  bias (magnitude) that a cosine/prototype head dodges; the guard is **logit-adjustment/balanced-softmax** for a *trained*
  head and **AIR (Analytic Imbalance Rectifier, 2408.10349)** for a *no-gradient analytic* head. **Owed:** whether the
  no-gradient heads need any guard at all.
- **Struck-in-advance (re-confirm as logged):** a heavy-optimizer readout (second-order / K-FAC / Shampoo) — *out*, the
  problem is convex; distance-classifier-as-"the-spine" — *out*, NCM/FeCAM/SLDA read a **magnitude** (recency-robust ≠
  direction-reading); read-side calibration as a Phase-7 deliverable — *out*, it defends a channel on a *chosen* head
  (§0.4).

### 0.4 What Phase 7 is NOT — the scope guard ("keep the menu closed")

- **NOT the economy gate (Ch7) or the cost meter → Phase 8.** P7 picks *what* the namer is; P8 decides *when* it fires
  and *what it truly costs* (charge cycles / ADC / Gram-solve — the honest meter). P7 reports an **op-count / solve-dim
  *proxy*** so heads are comparable, but **it is descriptive-only, never a decision axis** (§0.1), and **no "80/20" or
  vs-BP energy claim is settled here.**
- **NOT the read-side noise residual (the author's Q3 call, decided here) → deferred to Phase 8/9.** Phase 6 handed
  forward a named residual (input-transducer directional channel + ADC < ~3-bit) for **read-side calibration under
  shift.** *Deferred out of Phase 7 on purpose:* calibration-under-shift is a defense a *chosen* head adds on top of
  itself; **we do not yet know what the head is**, so calibrating a residual against an unknown namer is premature. It
  belongs *after* the head is committed (P8/P9 read-side). **Flagged loud in the handoff so it is not lost.**
- **NOT the maintenance loop or the owed old-world baselines → Phase 9.** The fair same-budget **BP+replay** continual
  baseline (Phase 4's WIN was vs *naive* online-BP) and the natural multi-class **A5** number need the full maintenance
  loop; P7 uses `race_bp` only as the readout **static-accuracy ceiling reference** — **not** as a continual/BWT baseline
  (a static-tuned BP number is meaningless on the forgetting axis; §5).
- **NOT re-opening the SCFF bulk.** The bulk is **frozen** (Stage 1 closed it). P7 reads it; it never re-trains or
  re-tunes it. A readout that "would work better if SCFF were different" is a *note to the north star*, not a P7 action.
- **NOT the north star.** No recurrence. The cosine-margin is grounded as a **direction** signal (so the recurrent brain
  can later reuse it as "the feeling") — a *tie-break bias*, not added scope. Simple intelligence first.

---

## 1. The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — read the class DIRECTION, never a MAGNITUDE (7th coat).** "Accuracy" is a magnitude symptom; the lever is
whether the classifier's verdict tracks the class **direction** or a **magnitude** (norm, distance, confidence, recency
of firing are all magnitudes). This kills three tempting-but-wrong moves up front: (a) calling NCM/FeCAM/SLDA "the spine
handed to us" — a **distance is a magnitude** (they are *recency-robust* for a different reason: no trained softmax
weights to inflate); (b) reading "which head is best" from accuracy alone, ignoring **spine-cleanliness**; (c) grounding
the north-star "feeling" on **confidence** (a magnitude — why P5 struck the adaptive exit) instead of the **cosine
margin** (an angle). Measure **spine-cleanliness** as a first-class axis (§4) — **but interpret it only for heads that are
competitive in accuracy** (within-band of the convex floor): a dead or near-random head is *trivially* spine-clean
(a useless verdict is stably useless under a norm nuisance), so spine-cleanliness on a sub-floor head is meaningless and
is **greyed out of the frontier** (§4, result-format §C).

**The envelope — read-only, never write the SCFF stream; the bulk is frozen.** The namer reads taps and maps them to
labels. **The hard rule (P2.5, carried):** read / fit-a-head / stop-gradient = OK; **anything that writes into the SCFF
activations mid-stack, or feeds a fast supervised signal *upstream* of SCFF (the boosting forward-leak), is forbidden.**
This is why boosting is dropped (N3 superseded) and the era is *one frozen bulk + read-only heads.* A head may be
gradient, closed-form, or streaming — but it is always a **stop-gradient consumer** of a frozen encoder.

**The gate that governs adoption — continual-safety (A6).** The sleep-recovery continual win is the architecture's reason
for being. **A readout that dents A6 is rejected, however accurate on the static curve.** Every committed head passes
**P7.4** (5 seeds + paired-sign veto) before it is banked.

---

## 2. The structure — one bake-off, three probes, two gates, one verdict

```
                      THE BAKE-OFF (P7.1): name the frozen bulk
    gradient anchors        direction-pure       magnitude protos          analytic / RLS (no-grad)
    linear-softmax(floor)   ► cosine ◄            NCM · SLDA · FeCAM        RanPAC · RLS-ridge · F-OAL
    MLP · race_bp(static    (cosine-NCM +         (tied→per-class cov,      GKEAL(kernel)
       ceiling)             cosine-softmax)        recency-robust)
                        \          |          scored: acc × BWT × spine-clean [× cost-proxy, descriptive]
                         \         |         /
   PROBES:  P7.2 multimodality (natural-space decides) ·  P7.3 bursty-imbalance guard (AIR for no-grad heads)
    CONTROL (P7.0): random-projection — random-from-taps AND random-from-pixels (did the bulk earn its keep?)
                         \        |        /
              GATES (un-skippable):  P7.4 continual-safety (A6, vs floor-head-on-same-bulk)  ·  P7.5 natural-data
                                     |
                        P7.6 synthesis → the committed readout + the spine-tension verdict
```

The **spine axis** organizes the whole bake-off (left = direction-pure, right = max-magnitude, ordered by *measured*
spine-cleanliness among the accuracy-competitive heads), so the headline result is a *frontier*, not a single winner:
**where on the direction↔magnitude axis does accuracy×BWT peak, and what does spine-cleanliness cost?**

**The verdict is a selection with a PRE-REGISTERED, NUMERIC spine-tension resolution** (not a floating narrative). Let
`Δ = (accuracy×BWT of the best magnitude head) − (cosine)`, computed **paired by seed**, and `δ = 0.02` accuracy at
matched BWT (pinned **blind**, matching the project's ≤0.02 "small-gap" convention):
- **cosine-free** — `Δ` is **within noise** (paired-Δ IQR includes 0, or sign < 4/5) → adopt the spine-clean head,
  spine-cleanliness bought free (the hoped-for 🔥);
- **cosine-at-a-price(X)** — `Δ` is **real** (paired-Δ IQR excludes 0 **and** ≥4/5 by sign) but `|Δ| ≤ δ` → report the
  price `X=|Δ|` and hand the author the call (spine-clean at cost X vs magnitude at +X);
- **magnitude-wins-spine-bends** — `Δ` is real **and** `|Δ| > δ` **AND** the recency-under-bursty-stream probe (§P7.1(b))
  shows the magnitude head is **not** actually fragile in *our* continual regime → the spine bends *here*, logged with
  the mechanism (recency-robust-by-no-trained-weights did the work).

The verdict does **not** gate the arc (P7 selects). **The one genuine "uh-oh" branch is P7.0's random-projection
control** — see P7.0, and it is **not** pre-excused.

---

## 3. The experiment ladder (cheapest-decisive-first; one variable per rung; 5 seeds; median + IQR)

Each rung is one sharp question, run with the house-style figures ([`result-format.md`](result-format.md)) and written in
the 6+2-slot card. **Every rung states, before it runs, what each outcome will mean** (a **Reads** line, including the
**failure** reading). **Failures are data.** Conditional rungs fire only if a gap survives. Cards live in `expK/`;
apparatus in `p7lib.py` (§6).

### P7.0 — the bench + guards + the convex floor + the ceiling anchors + the random-projection control `exp0`
- **Question:** does the apparatus reproduce a readout on the frozen bulk, and do the references behave — the convex
  **floor** (linear-softmax), the static-accuracy **ceiling** (`race_bp` + a small MLP head), and the skeptic **control**
  (a random projection in place of the SCFF bulk)? **And does the trained SCFF bulk beat a random projection at the
  readout — i.e. does the 80% earn its keep at the naming stage?**
- **Setup:** stand up `p7lib.py` (§6) on the frozen `NoiseAugContrast` cell (import + **freeze** — GD reads, never
  writes). Feature source = `readout_feats` **all-tap** + a **short truncation** read (what the apparatus actually
  provides — the P5 fixed-reader *placement*; there is no carried per-depth-selector object, so per-depth selection, if
  wanted, is a p7lib build), **frozen to a pinned run-dir** (the canonical tap features every later rung LOADS, never
  recomputes — the no-baseline-drift rule). Pin the **readout-fit budget `PROBE_EP`** here and freeze it for all later
  rungs. Fit: linear-softmax (the convex floor), a 2-layer MLP head + `race_bp` (the anchors), and **two
  random-projection controls** — **(a) random-from-taps** (a random ReLU projection of the SCFF tap output, at a **fair
  expansion dim** + the *same* downstream head — a strong skeptic, not a matched-64-D strawman) and **(b)
  random-from-pixels** (true RanDumb — a random projection of the *raw input*).
- **Guards (FIRST, pre-any-head — the antidote to the sign/direction bug):** equivalence (`equivalence_guard` — a head
  port ≡ its parent bit-for-bit: `CosineHead(unit weights) ≡ NCMHead(on L2-normalized feats)`; the linear head ≡ the P5
  readout; **and the extended continual harness with the linear head ≡ the old hard-coded `fit_readout` path**, §6);
  **FD-gradient `<1e-5`** (`fd_gradient_check`) on every trained head; dead-frac ≈ 0; the **feature-source-pinned**
  INV panel (later rungs read the frozen taps). ANY guard fails → **STOP.**
- **Reads:** the floor/ceiling/control reproduce and bracket the readout → the bench is trusted. **The load-bearing early
  read:** OURS-bulk + best readout **beats both random-projection controls** → the trained bulk earns its keep at naming
  (hedge (b) holds). **If OURS ≈ random-from-taps (or ≈ random-from-pixels) on the flat continual home** — the regime the
  namer is *chosen for* — this is **NOT pre-excused as "composition, move on."** Report **both** readings: (i) it is
  *consistent* with P4/P5 (the bulk's proven value is *composition*, which the flat home does not exercise), AND (ii)
  **the flat-home namer gains nothing from the trained bulk**, so the committed namer could have read a random projection
  — a result handed to Stage 2 with an explicit flag that **the bulk's naming-stage value is unverified on the home**, not
  a benign footnote. **Any guard fails → STOP.**
- **Decides:** go/no-go on the bench; the pinned floor + ceiling + both control numbers all later rungs are measured
  against; the frozen canonical tap-feature run-dir; `PROBE_EP`; the honest random-projection read (both branches).

### P7.1 — the readout bake-off `exp1`  *(THE headline)*
- **Question:** across the namer taxonomy, **where on the direction↔magnitude axis does accuracy×BWT peak, and what does
  spine-cleanliness cost?** Concretely: **does the spine-clean cosine head MATCH the accuracy×forgetting of the
  magnitude-based no-gradient SOTA (FeCAM / SLDA / RanPAC-RLS), or do we pay a price to stay spine-clean?**
- **Setup (one variable = the readout head):** race the **core set** on the continual home — **linear-softmax (floor) ·
  cosine (spine-pure) · NCM (Euclidean) · SLDA (tied covariance) · FeCAM (per-class Mahalanobis) · RanPAC-or-RLS-ridge
  (analytic, no-gradient)** — with the MLP + `race_bp` anchors carried on the static-accuracy figures. **All heads read
  the *same frozen taps* (P7.0's run-dir); one variable = the head.** Score on **accuracy (AAA + final) × BWT ×
  spine-cleanliness**; cost-proxy is reported **descriptively only** (never a tie-break). **Tier-2 heads (run only if the
  core race leaves a live question):** **F-OAL-style forward-only-online analytic** (if the analytic head wins and we
  want the on-constraint streaming form), **GKEAL kernel** (if multimodality bites — P7.2's job).
  - **"Cosine" is TWO heads, run both (disambiguate up front):** **(i) cosine-NCM** — prototype = streaming mean of
    L2-normalized features, no gradient (the pure spine × no-gradient point); **(ii) cosine-softmax** — trained
    cosine-normalized weights, gradient (the pure spine × gradient point). Reporting both isolates *is the spine win from
    the angle-metric or from being no-gradient?* — a confound the single-"cosine" rough plan hid.
  - **Fair per-head hyperparameters (the race_bp fairness protocol, MANDATORY):** each head has its own knob (cosine
    `τ_ro`, ridge `λ`, FeCAM/SLDA shrinkage, RanPAC `proj_dim`, MLP width/lr). Each is **lightly selected on a held-out
    val split, per head**, exactly as `race_bp` tunes the BP racer — an un-tuned head loses for the wrong reason and rigs
    the bake-off. Record each head's selected knob in the manifest; the selection budget is equal across heads.
- **The spine-cleanliness probe (MANDATORY — the axis the field ignores and we don't), two parts:** **(a) per-class
  norm-rescale** — multiply each class weight/prototype by a random positive scalar and measure the **argmax-flip rate**
  (cosine ≈ 0 by construction; a magnitude head flips) — *this is the clean, non-gameable probe (the field's implicit
  definition of scale-invariance, made explicit).* **(b) the recency-bias evidence = the standard task-recency-bias
  read** (Masana CIL survey 2010.15277): the **old-class accuracy drop under the *actual bursty stream*** (P7.3's
  mechanism), NOT a synthetic norm-inflation — because a synthetic inflation of a cosine head's norms does nothing *by
  construction*, so it would circularly "prove" what it assumes. (A synthetic-inflation illustration may accompany it as
  a *mechanism* picture, never as the recency evidence.) **Spine-cleanliness is read only for accuracy-competitive
  heads** (§1); sub-floor heads are greyed.
- **Reads / pre-registered rule:** the committed head **maximizes accuracy×BWT on the continual home, passes P7.4, and —
  at equal accuracy×BWT — is the more spine-clean** (the tie-break is the spine; cost is never the tie-break). The
  three spine-tension outcomes are the **numeric** branches pinned in §2 (`Δ` vs `δ=0.02`): **cosine-free /
  cosine-at-a-price(X) / magnitude-wins-spine-bends.** **If no head clears the floor → the frozen bulk isn't linearly
  nameable → re-scope** (unlikely; the P5 readout already beat tuned-BP).
- **Decides:** the committed readout family (pending the P7.4 gate). The highest-leverage rung — run first after the bench.

### P7.2 — multimodality / heterogeneity: the closed-form cliff `exp2`  *(where the clean story may end)*
- **Question:** are SCFF's per-class features ~unimodal **in the natural frozen tap space** (one prototype suffices → the
  clean no-gradient story holds), or multi-modal/heterogeneous (one mean underfits)? And if multi-modal, **how far up the
  fallback ladder must we climb before accuracy recovers — and does it stay closed-form (SLDA → FeCAM → GKEAL) or force a
  non-convex mixture?**
- **Setup (one variable = the per-class modeling capacity):** the fallback ladder, in order — **one mean → SLDA (tied
  covariance) → FeCAM (per-class covariance) → GKEAL (Gaussian-kernel) → few-prototype-per-class mixture (non-convex,
  last resort).** **The decision-bearer is the NATURAL frozen tap space** (digits / CIFAR-flat): measure a
  **multimodality probe** (per-class n-modes / silhouette / GMM-BIC) there and the accuracy each ladder rung recovers.
  **The synthetic multi-blob-per-class task is DEMOTED to an apparatus sanity check** — a generator where each class is
  2+ separated modes so a single mean *provably* underfits: it confirms the ladder recovers a *known*-multimodal task
  (a plumbing test), and its outcome is fixed by construction, so it **does not decide** the committed modeling — only the
  natural-space probe licenses climbing the ladder in the committed head.
- **Reads:** natural classes ~unimodal (probe flat) → one prototype suffices, the elegant story holds, covariance is
  optional polish. Natural multi-modal → **SLDA/FeCAM/GKEAL recover it closed-form** (the convex/analytic guarantee
  survives — the rough plan's "non-convex or bust" was wrong) → adopt the **cheapest** ladder rung that closes the gap
  (SLDA's one tied covariance before FeCAM's C per-class ones). Only a **mixture** recovers it → the clean convex story
  genuinely ends here (logged; a small non-convex head is then licensed).
- **Decides:** single-prototype vs tied-cov vs per-class-cov vs kernel vs mixture; whether a non-convex head is *forced*
  (and if so, the convexity claim is scoped to "the simplest heads," honestly).

### P7.3 — the bursty-stream imbalance guard `exp3`
- **Question:** a drift-gated stream presents classes in **bursts** → the head is chronically class-imbalanced. Does a
  trained-softmax head develop the documented **recency/magnitude bias** (BiC/WA/SCR) that a cosine/prototype head dodges
  — and what is the guard for the head we keep?
- **Setup (one variable = the imbalance guard):** on the committed head from P7.1, under the bursty class-incremental
  ordering, test the guard **matched to the head family** — for a **trained** head: no-guard vs **logit-adjustment vs
  balanced-softmax**; for a **no-gradient analytic** head: no-guard vs **AIR (Analytic Imbalance Rectifier,
  2408.10349)** — the family-native imbalance rectifier (the trained-head guards do not apply to a closed-form head, so
  AIR closes the "what guards a no-gradient winner?" gap); and **class-balanced reservoir sampling** on the buffer for
  either. Measure **per-class accuracy split (old vs recent)** and the recency-bias magnitude (the task-recency-bias
  read).
- **Reads:** the trained head shows recency bias, its guard removes it → ship the guard. The cosine/prototype/analytic
  head shows **no** recency bias (dodges it by construction) → no guard needed (a point *for* the spine-clean / no-gradient
  head — banked as evidence in the P7.1 spine-tension verdict). A no-gradient head *does* imbalance → AIR is the guard.
  No head shows bias at our burst rate → report it (note for P9's heavier streams).
- **Decides:** the imbalance guard that ships with the committed readout (or "none needed, by construction").

### P7.4 — continual-safety: the home-turf gate `exp4`  *(the spine gate — un-skippable)*
- **Question:** does the committed readout (+ its guard) **preserve the A6 sleep-recovery continual win** — the
  architecture's reason for being?
- **Setup (BUILD, not carry — critic-forced):** the current `p6lib.continual_safety(cell_factory, …)` **hard-wires
  `fit_readout`** (a GD MLP) as the head — it does **not** accept a head. So **p7lib must EXTEND it** into a
  head-parameterized variant `continual_safety_heads(cell_factory, head_factory, head_fit, head_consolidate, …)`, and
  **each head runs under its NATIVE online + sleep rule (the fairness point):** a closed-form head (NCM/SLDA/FeCAM/RanPAC/
  RLS) consolidates by **recomputing its statistics** over the replay buffer at sleep; a gradient head (linear/
  cosine-softmax/MLP) **sleep-refits by GD**. **Guard:** the linear-softmax head through the extended harness ≡ the old
  hard-coded `fit_readout` path bit-for-bit (else the gate baseline silently moved). Measure **BWT / AA / forget** (the
  metrics the harness actually returns — *not* the A7-noise "retention", which is a different quantity) of each *candidate
  committed head* vs **the linear-softmax FLOOR head run through the SAME extended gate on the SAME frozen bulk** (the
  head-swappable per-head baseline — **not** "the P5 readout number," which entangles cell-forgetting with head-forgetting
  and is not an isolatable per-head artifact; the P5 number is a *secondary* cross-check only). Pin the baseline run-dir.
  This surfaces a synergy to bank: the analytic heads are **joint-equivalent by construction** (RLS), so their sleep may be
  a trivial recompute and their BWT ≈ 0 for free (the strongest continual story, if it holds). The sleep *cadence* itself
  is Phase-9's to tune — here it is fixed to the P5 protocol. **Power (this is the GATE):** **5 seeds, never 3**; "within
  noise" is **NOT** an auto-pass — a head that is negative-BWT vs the floor-head baseline in ≥4/5 paired seeds **fails**.
- **Reads:** BWT / AA / forget hold vs the floor-head baseline → continual-safe, bank it. They degrade → the head is
  **rejected regardless of its P7.1 accuracy** (fall back to the strongest head that passes here). *(Expected:
  cosine/prototype/RLS heads should be continual-safe — no-trained-weights or angle-only dodges the recency bias; a plain
  trained-softmax head is the one at risk — itself a result feeding the P7.1 verdict.)*
- **Decides:** the gate. An accurate readout that dents A6 is reverted.

### P7.5 — natural-data confirmation `exp5`  *(the synthetic-artifact gate)*
- **Question:** do the bake-off verdict and the chosen head + guard hold on **real flat data** (not a synthetic artifact)?
- **Setup:** re-run the headline bake-off (or at least the committed head vs the floor / static ceiling / best-magnitude)
  on **digits (64-D)** and **CIFAR-flat (3072-D)**, on the continual-stream harness. (P7.2's natural-space multimodality
  read already lives here — natural data is where the multimodality decision is made.)
- **Reads:** the ordering + the chosen head reproduce on digits/CIFAR-flat → the readout story is real, commit it. The
  verdict flips on real data → the committed head follows the **natural-data** verdict (real > synthetic for a deployment
  choice), re-scope the claim honestly.
- **Decides:** whether the readout choice is real or a synthetic artifact; the natural-data-confirmed committed head.

### P7.6 — synthesis + the committed readout  *(README + phase7-report)*
- **Assembled-head confirmation (RUN, not just synthesized) — with a pre-registered pass/fail bar:** run the *committed*
  head (+ its P7.2 multimodality modeling + its P7.3 imbalance guard) end-to-end on BAKEOFF + SPINE-CLEAN + CONT-SAFETY +
  NAT-ANCHOR. A combined regression **overrides** per-rung optimism (levers may not stack). **The bar (pinned):** if the
  assembled head's accuracy×BWT falls **below its P7.1 solo number by more than the §B band**, the P7.3 guard / P7.2
  modeling is **reverted and the next-best head re-assembled** — a decision, not a narrated note.
- **The verdict (pre-registered — a selection + a numeric spine-tension resolution, natural-confirmed):**
  - **the committed readout** = the head that maximizes accuracy×BWT on the natural-confirmed continual home, passes the
    A6 gate, with the spine as the tie-break;
  - **the spine-tension outcome** = one of {cosine-free / cosine-at-a-price(X) / magnitude-wins-spine-bends} per the §2
    numeric cut, stated with `Δ`, `δ`, and the mechanism;
  - **the random-projection read** = did the trained bulk earn its keep at naming (both branches from P7.0 reported, the
    "uh-oh" not excused);
  - **the cheat-everything read** = is the committed namer gradient, closed-form, or streaming-analytic — and if
    no-gradient, *the 20% is not even GD* (the headline the phase hunts).
- The **decision-record deltas** (§8) committed once the head is banked; the **hand-off brief** to Phase 8/9 (the cost
  meter's target heads; the read-side residual still owed; the imbalance guard + multimodality modeling to carry; the
  bulk's-naming-value flag if the control tied). **Update the `ref-report/` glossary** with the phase's new citable terms
  (spine-cleanliness, the namer taxonomy, analytic/RLS head, the random-projection control) at close.

---

## 4. The metrics (PINNED) — what "the right namer" means here

Carry the canonical set ([`../result-format.md`](../result-format.md)); Phase-7 additions in **bold**.

| metric | definition (pinned) | what it answers |
| --- | --- | --- |
| **readout accuracy** | final held-out acc + **AAA** (trapezoid area under acc vs log₁₀-samples ÷ log-span), vs the convex floor + the **static** BP ceiling | how good is the naming |
| continual **BWT / AA / forget** | GEM/CL-survey conventions (the harness's actual outputs — **not** "retention"); head vs **the floor-head-on-same-bulk baseline**; + paired-sign veto at the gate | **the gate** — does the head keep the A6 win |
| **spine-cleanliness** | **(a)** argmax-flip rate under per-class weight/prototype-norm rescale (clean, non-gameable); **(b)** old-class acc drop under the *actual bursty stream* = the task-recency-bias read. **Interpreted only for accuracy-competitive heads** (sub-floor heads greyed) | how much a pure **magnitude** nuisance moves the verdict (cosine ≈ 0 on (a)) |
| **multimodality** | per-class n-modes / silhouette / GMM-BIC in the **natural** frozen tap space (decision-bearer); + acc recovered per fallback-ladder rung | does one prototype underfit; is a closed-form (SLDA/FeCAM/GKEAL) escape enough |
| **imbalance robustness** | per-class acc split (old vs recent) under the bursty stream, guard on/off (trained: logit-adj/bal-softmax; analytic: **AIR**) | does the head develop recency/magnitude bias |
| **readout cost-proxy** | readout forward-MACs + analytic Gram/solve dim (dim² store, dim³ solve) — **DESCRIPTIVE ONLY, never a decision tie-break; tagged "(proxy; real meter = P8)"** | comparability across heads, NOT a settled 80/20 |
| **random-projection control** | acc: OURS-bulk vs (a) random-from-taps and (b) random-from-pixels, same head | did the trained bulk earn its keep at naming |

**Spine-cleanliness is a first-class axis, not a footnote — but conditional on competitive accuracy** (the spine): a head
that wins accuracy by a magnitude trick but flips its verdict under a per-class norm nuisance is not the namer we want on
a lifelong stream; equally, a head that is *trivially* spine-clean by being useless is greyed. Report accuracy, BWT,
**and** spine-cleanliness together; when accuracy and spine-cleanliness disagree, **name the tension** — it is the phase's
headline. **Cost is a PROXY and descriptive-only** — never a tie-break, never a settled 80/20 or vs-BP energy claim.

**Calling a difference real (n=5, carry):** real only if **IQR bands disjoint at the final checkpoint** *and* the **sign
is consistent in ≥4/5 seeds, paired by seed**; else "within noise." **At the P7.4 GATE, "within noise" is NOT an
auto-pass** — add the paired-sign veto (negative-BWT vs the floor-head baseline in ≥4/5 paired seeds = fail). The
**decisive spine-tension gap** (cosine vs best-magnitude on accuracy×BWT, the `Δ` of §2) gets **~9 seeds** (add
`[1009,2027,9091,7]`) when ≤0.02, so the rung can adjudicate the tension it exists for.

---

## 5. Tasks

| role | task | why |
| --- | --- | --- |
| **the device under test** | the **frozen `NoiseAugContrast` cell** (SCFFContrastOverlap temp0.2/w2, L12, no residual, +noise-aug view) | P7 names *this*; it is frozen, never re-trained |
| **the continual home** | class-incremental synthetic stream (10 classes as 5 tasks) + **digits** (P4.5/P6 exact) | the home turf; where BWT / bursty-imbalance / recency bias live |
| **the multimodality decision** | the **natural** frozen tap space (digits, CIFAR-flat); a synthetic multi-blob generator as **apparatus sanity only** | forces the P7.2 cliff — natural-space multimodality decides, the blob task only plumbs the ladder |
| **the skeptic controls** | **(a) random-from-taps** (random ReLU proj of the tap output, fair expansion) + **(b) random-from-pixels** (true RanDumb, raw input) | did the trained bulk earn its keep at naming (hedge (b)) |
| **natural confirm (P7.5)** | **digits** (64-D), **CIFAR-flat** (3072-D) | the readout choice must survive real flat input |
| **references** | the convex floor (linear-softmax); the **static** BP ceiling (`race_bp` + MLP head) — **static/AAA panels only, NEVER on the BWT/continual figures** (a static-tuned BP is not a forgetting baseline; that fair fight is P9) | a head with no reference is a toy |
| **deferred** | SPICE / PVT / conv / time-series; the fair BP+replay baseline; natural multi-class A5 | device physics (later) or Phase-9 owed baselines |

Seeds `[42,137,271,314,1729]` (9 for the ≤0.02 spine-tension gap), median + IQR, single-threaded (phantom guard),
**`PROBE_EP` pinned at P7.0 and frozen for all later rungs**. **P7.4 the GATE runs the full 5 — never 3** (paired-sign
power). **No sklearn** for compute (phantom-hang) — numpy `linear_probe`/`fit_readout` + the closed-form heads;
`load_digits`/`load_cifar_flat` are data-only (safe).

---

## 6. What to build — `p7lib.py` (the apparatus, on `p6lib`)

Reuse `p6lib` (which re-exports p5/p4/p3/p2): the cell (`NoiseAugContrast`, `make_committed_cell`, `COMMITTED`,
`train_cell`), `readout_feats` (all-tap / truncation), `linear_probe` (numpy Adam linear — **phantom-safe, no sklearn**),
`fit_readout` (MLP head), `race_bp` (the tuned-BP **static** ceiling), `acc_matrix_metrics` (AA/BWT/forget),
`CISTREAM_TASKS`, `synth_stream`, `load_digits_split`, `load_cifar_flat`, `make_mixed`, `effective_rank`, `normalize`,
`relu`, `EPS`, plus `equivalence_guard`/`fd_gradient_check`. **Import, don't retype — the netlist rule.**
**⚠ Verified-against-repo corrections (from the review — do NOT trust the old import list blindly):**
- **`n_w` is NOT re-exported by `p6lib`** → import it from `p4lib`/`p5lib` directly (else `ImportError`).
- **`PerDepthHeads` was never implemented** (docstring only) → do **not** import it; P7.0's feature source is
  `readout_feats` all-tap + truncation, and per-depth *selection* is a p7lib build if wanted.
- **`continual_safety` is a BUILD, not a carry** → see the head-factory extension below.
- **there is no `retention` continual metric** → use `aa`/`bwt`/`forget`.

**Add (with the pinned specs the rungs depend on):**

- **`CosineHead(tau_ro, mode)`** — `mode ∈ {ncm, softmax}`. **cosine-NCM**: prototype = streaming mean of L2-normalized
  features, logit = `(f/‖f‖)·(w_c/‖w_c‖)/τ`, no gradient. **cosine-softmax**: trained cosine-normalized weights,
  gradient. **The spine-pure head(s).**
- **`NCMHead`** — running class mean, Euclidean. **Guard:** `NCMHead(on normalized feats) ≡ CosineHead(unit, ncm)`.
- **`SLDAHead(shrinkage)`** — running per-class mean + **one shared (tied) covariance** → Mahalanobis / equivalently
  linear-softmax with `w_c=Σ⁻¹μ_c`, `b_c=−½μ_cᵀΣ⁻¹μ_c`. The cheaper *middle* covariance head (Deep SLDA, 1909.01520).
- **`FeCAMHead(shrinkage)`** — running per-class mean + **per-class covariance** (paper normalization + shrinkage),
  anisotropic Mahalanobis. The closed-form heterogeneity escape / the max-magnitude pole (FeCAM, 2309.14062).
- **`RanPACHead(proj_dim, ridge_lambda)`** — frozen random ReLU projection `φ=ReLU(Wr·f)` → running mean + **running
  Gram** `G=Σφφᵀ` + cross-corr `M=Σφ·onehot` → ridge prototype `W=(G+λI)⁻¹M`. Streaming.
- **`RLSHead(ridge_lambda)`** — the analytic head *without* the random projection (ACIL 2205.14922 / F-OAL 2403.15751 —
  recursive least-squares ridge on the raw taps); **recursive rank-update** (Sherman-Morrison) = the forward-only-online
  namer. `RanPACHead` = `RLSHead` on a projected expansion → isolates whether the projection earns its keep at 64-D.
- **`GKEALHead(kernel_dim, gamma)`** *(conditional — P7.2)* — Gaussian-kernel feature map → analytic solve (GKEAL, CVPR
  2023, kernel mechanism only). The closed-form non-linear multimodality option.
- **`MLPHead`** — a 2-layer GD head (the non-convex anchor; wrap `fit_readout`).
- **`RandProjBulk(out_dim, source)`** — the **random-projection control**: `source ∈ {taps, pixels}` — a frozen random
  ReLU projection at a **fair expansion dim** replacing the SCFF bulk as the feature source (`taps` = of the tap output;
  `pixels` = of the raw input = true RanDumb), same readout on top.
- **`continual_safety_heads(cell_factory, head_factory, head_fit, head_consolidate, …)`** — **EXTEND** `p6lib`'s
  `continual_safety` to accept a head (it currently hard-wires `fit_readout`). Each head runs its **native** online +
  sleep rule (closed-form: recompute stats; gradient: GD-refit). **Guard:** linear-softmax head through this ≡ the old
  hard-coded path bit-for-bit. The P7.4 gate rides on this — build it first, with the equivalence guard.
- **`spine_cleanliness(head, X, y)`** — **(a)** per-class weight/prototype-norm rescale → argmax-flip rate (cosine ≈ 0);
  **(b)** old-class accuracy drop under the **actual bursty stream** = the task-recency-bias read (NOT synthetic
  inflation, which is circular for the spine-clean heads). Read only for accuracy-competitive heads.
- **`multimodality_probe(feats, y)`** — per-class n-modes / silhouette / GMM-BIC in the frozen tap space (P7.2), run on
  the **natural** space as the decision-bearer.
- **imbalance guards** — `logit_adjust`, `balanced_softmax`, `class_balanced_reservoir` (trained heads); **`air_rectify`**
  (Analytic Imbalance Rectifier, 2408.10349 — the no-gradient analytic-family guard).
- **`readout_cost(head)`** — the forward-MAC + Gram/solve-dim **proxy** meter (descriptive-only; real meter = P8).
- **guards** — `equivalence_guard` (`CosineHead(unit,ncm) ≡ NCMHead(normalized)`; `cosine-softmax(τ→∞, normalized) ≡
  linear-softmax(normalized)`; `cosine-softmax@init ≡ cosine-NCM` within noise; `linear head ≡ P5 readout`;
  `continual_safety_heads(linear) ≡ old continual_safety`) + `fd_gradient_check(<1e-5)` on every trained head; run
  **before any head** (P7.0); the **feature-source-pinned** check.
- **reproducibility (carry, non-negotiable)** — `manifest.json` (git hash + resolved config + seeds + versions +
  wall-clock) + `arrays.npz` per run to the schema in [`result-format.md`](result-format.md) §A; `plot_p7.py regen
  <run-dir>` redraws every figure from saved data; per-run `_ckpt.jsonl` fsync'd (resumable); thread caps before numpy
  import + `python -u` + `PYTHONIOENCODING=utf-8` (the OpenMP-phantom + cp874 guards).

**This is a substantial build — ~8 head classes + 3 probes + the harness extension + guards (the heaviest new apparatus
since P3).** **Rough per-rung wall-clock:** P7.0–P7.3 are readout fits on the **frozen** bulk (fast; ~10–40 min each,
5–9 seeds). **P7.4 (continual-safety) and P7.5 (CIFAR-flat 3072-D continual) are the heaviest** — run **checkpointed,
single-threaded, multi-hour**, and **verify the real PID is alive** (the 14-hr-ghost guard). Keep P7.4 strictly to
**commit-candidates** (not all 7+ heads × 5 seeds × CIFAR) — that is what keeps it tractable.

---

## 7. The success criterion + the verdict

> The committed **namer** for the frozen SCFF bulk — the head that **maximizes accuracy × BWT on the natural-confirmed
> continual home, passes the A6 continual gate (vs the floor-head-on-same-bulk baseline), with spine-cleanliness as the
> tie-break** — together with the honest, **numeric** resolution of the phase's central tension (**does staying
> spine-clean cost accuracy/forgetting, and by how much — `Δ` vs `δ=0.02`?**) and the honest control read (**did the
> trained bulk earn its keep at naming, or is its value unverified on the flat home?**). Not "the most accurate head on a
> static split"; a *characterized, continual-safe, spine-scored* naming decision — and, if the winner uses no gradient,
> the headline that **the 20% is not even gradient descent.**

**The verdict is a selection, not a fork** (§2, §3 P7.6): the committed readout + one of {cosine-free /
cosine-at-a-price(X) / magnitude-wins-spine-bends}, each **numerically** pre-registered. **The one genuine "uh-oh" branch**
is P7.0's random-projection control: if the trained bulk does not beat a random projection at naming *on the flat home*,
that is **not** pre-excused — both readings are reported (P4/P5-consistent *and* "the flat-home namer gains nothing from
the trained bulk → naming-stage value unverified, flagged to Stage 2").

---

## 8. The decision record (the research passes — authoritative for the plan logic)

Two research passes produced this plan. The **1st (cold-start, in `stage2-design.md` §3.1)** set the spine + convexity +
the rough `{linear, cosine, NCM, RanPAC}` set. The **2nd (this phase's audit,
[`analytic-and-covariance-readouts.md`](../../research/papers/phase7/analytic-and-covariance-readouts.md))** widened it.
The **3-agent lab-manager review** then ran; its verdicts are folded into the rungs above and ledgered in §8.1.

> **THE FRAME (the author's Q1 call).** The 20% is *cheat-everything*, not GD-as-religion. The namer is whatever names the
> frozen bulk cheaply, continual-safely, and (the tie-break) spine-clean. "No gradient wins" is the goal, not a surprise.

**KEEP / CHANGE / ADD ledger (from the 2nd-pass audit):**

| Item | Verdict | Why |
| --- | --- | --- |
| The bake-off = accuracy × BWT × **spine-cleanliness** (cost descriptive-only) | **KEEP — the referee structure** | the spine is the tie-break; spine-cleanliness pinned as two probes, conditional on competitive accuracy |
| Cosine = the direction-pure candidate; NCM/SLDA/FeCAM = recency-robust *magnitudes* | **KEEP** | a distance is a magnitude; recency-robust ≠ direction-reading |
| The rough set `{linear, cosine, NCM, RanPAC}` | **CHANGE → widen** | it was a *subset*; "cheat everything" demands the field's strongest no-gradient namers |
| **ADD the Analytic/RLS family — F-OAL (fwd-only+online+no-grad, =AOCIL), ACIL/DS-AL/GACL** | **ADD — the biggest change** | no-gradient streaming naming is a *published paradigm* (RLS = joint-equivalent); F-OAL matches our exact constraint |
| **ADD FeCAM + Deep SLDA (the covariance ladder)** | **ADD** | closed-form multimodality escape (SLDA tied → FeCAM per-class) AND the max-magnitude spine pole |
| **ADD GKEAL (kernel) as the non-linear closed-form fallback** | **ADD** | below FeCAM on the multimodality ladder (P7.2); kernel mechanism only (its regime is few-shot) |
| **ADD the random-projection control (random-from-taps + random-from-pixels)** | **ADD** | operationalizes hedge (b); the pixels arm is the harsher "did the 80% earn its keep" |
| **ADD AIR (Analytic Imbalance Rectifier) for no-gradient heads** | **ADD** | the trained-head imbalance guards don't apply to a closed-form winner |
| Read-side noise-residual defense as a P7 deliverable | **CUT → Phase 8/9** | it defends a channel on a *chosen* head; premature before the head is chosen (Q3, §0.4) |
| The cost meter / the economy gate as P7 deliverables | **CUT → Phase 8** | P7 picks *what*; P8 prices it and decides *when*; P7 reports a flagged, descriptive-only proxy |
| The fair BP+replay baseline + natural multi-class A5 | **DEFER → Phase 9** | need the full maintenance loop; P7 uses `race_bp` as the *static* readout ceiling only |
| Heavy-optimizer zoo (2nd-order / K-FAC / Shampoo / LARS) | **CUT** | the readout regression is convex; those are for the non-convex bulk we don't GD-train |

**Owed decision-record deltas (to `idea/main.ideas.v1.md` — commit only after P7.1/P7.4 give results; FLAGGED, not
silently applied, and NEVER retro-edit the frozen `phase6-final-architecture.md`):**
- **N3** ("GD = residual boosting blocks") → **superseded** by "single frozen bulk + read-only namer";
- **S4** ("two GD organs") → **collapses to one** (the namer; Interface-GD retired with the blocks);
- **S9** (fixed short-stack reader) → **extended** with the committed *head* (cosine/analytic/…), not just the placement;
- a new supporting decision if the winner is no-gradient: *the namer is a closed-form/streaming head, not gradient
  descent — the "20% GD" is a role, not a method*;
- **N2** (EMA-view) and **S6** (the gate) stay Phase-8/9's to resolve — untouched here.

**Citation hygiene (corrected in the review — these IDs now resolve):** FeCAM 2309.14062 ✓ · RanDumb 2402.08823 ✓ ·
**F-OAL = AOCIL = 2403.15751** (NeurIPS 2024 — one paper, v1→v2 rename; the earlier plan double-counted it) · **ACIL =
2205.14922** (NeurIPS 2022) · **GKEAL = CVPR 2023, few-shot, NO arXiv** (cite CVF + repo `ZHUANGHP/Analytic-continual-learning`)
· **Deep SLDA 1909.01520** · **AIR 2408.10349** · DS-AL 2403.17503 · GACL 2403.15706 · AnaCP 2511.13880 · task-recency-bias
survey 2010.15277. We adopt **mechanisms**, not results.

### 8.1 The lab-manager review ledger (2026-07-01 — three cold agents; APPLIED)

Three subagents (repo-fit/executor · outside-literature · red-team) stress-tested the plan "can we confirm before
running?" Verdict: **science / spine / scope sound; the *spec* had real holes — three BLOCKERS + citation errors.** All
material findings are APPLIED above; the load-bearing ones:

| finding (agent) | verdict | where applied |
| --- | --- | --- |
| `continual_safety` hard-wires `fit_readout` — the P7.4 head-factory harness **does not exist**, mislabeled as reuse (repo-fit + red-team) | **FIX — BLOCKER** | §6 `continual_safety_heads` = EXTEND + equivalence guard; §3 P7.4 marked BUILD |
| The P7.4 gate baseline ("the P5 readout") is not an isolatable per-head artifact → confounds head- and cell-forgetting (red-team) | **FIX — BLOCKER** | §3 P7.4 + §4: baseline = the floor-head on the SAME bulk through the SAME extended gate |
| The three verdict branches have **no numeric boundary** → the verdict floats (the Phase-6 "tolerable band" hole, reintroduced) (red-team) | **FIX — BLOCKER** | §2 + §7: `Δ` (paired) vs `δ=0.02` pinned blind; free/at-a-price/bends defined numerically |
| Spine-cleanliness is gameable by a dead head (trivially clean) (red-team) | **FIX** | §1/§4: interpreted only for accuracy-competitive heads; sub-floor greyed |
| The recency probe (synthetic norm-inflation) is **circular** for the no-gradient heads it praises (red-team + lit) | **FIX** | §P7.1(b)/§4: recency = old-class drop under the *actual bursty stream* (task-recency-bias read); synthetic = mechanism illustration only |
| The random-projection control was under-powered ("matched dim" ≠ RanDumb's expansion) and it's random-from-taps, not RanDumb-proper (red-team + lit) | **FIX** | §P7.0/§5/§6: fair expansion + **two arms** (random-from-taps + random-from-pixels) |
| The RanDumb "uh-oh" branch was pre-excused (red-team) | **FIX** | §P7.0/§7/§9: both readings reported; naming-stage value flagged unverified, not benign |
| Cost-proxy flatters the no-gradient heads it hopes win (red-team) | **FIX** | §0.1/§4: cost is DESCRIPTIVE-only, never a tie-break |
| P7.2's synthetic multimodal task is tautological; natural space must decide (red-team) | **FIX** | §3 P7.2: natural tap space = decision-bearer; synthetic blob = apparatus sanity only |
| **AOCIL ≡ F-OAL are the SAME paper (2403.15751)** — the plan double-counted its headline method (lit) | **FIX** | §0.2/§8/§10 + audit file + README: collapsed to one entry |
| ACIL id resolvable = 2205.14922; GKEAL = CVPR-2023 few-shot, no arXiv (lit) | **FIX** | §8/§10 + audit file + README |
| MISSING: Deep SLDA (the covariance-ladder middle) + AIR (the no-gradient imbalance guard) (lit) | **ADD** | §2 taxonomy, §P7.1 core set, §P7.2 ladder, §P7.3 guard, §6 heads |
| `n_w` not re-exported by p6lib; `PerDepthHeads` never built; `retention` not a metric; `PROBE_EP` unpinned (repo-fit) | **FIX** | §6 corrections; §4 forget-not-retention; §5 PROBE_EP pinned at P7.0 |
| `race_bp` is a static ceiling, not a continual baseline — don't draw it on BWT figures (red-team) | **FIX** | §5 + result-format §C: static/AAA panels only |
| RanPAC's projection *benefit* is a high-dim result, may not survive 64-D (lit) | **NOTE** | §0.2 caveat; H-analytic "owed" |
| cosine-softmax lacked an equivalence guard (red-team) | **NOTE→FIX** | §6 guards: `cosine-softmax(τ→∞,normalized) ≡ linear-softmax`; `@init ≡ cosine-NCM` |
| P7.6 assembled-head regression had no pass/fail bar (red-team) | **FIX** | §3 P7.6: revert-and-re-assemble if below the P7.1 solo number by > §B band |

**Rejected / deferred (scope calls, nothing rejected as *wrong*):** the 2025 covariance-adaptation line (DPCR
2503.05423, task-recency-bias-strikes-back 2409.18265, FoRo 2509.01533) — *noted, no rungs added* (mechanisms already
covered by SLDA/FeCAM/F-OAL); AnaCP 2511.13880 — *a stretch reference, not a core head.*

---

## 9. Open items / scope

- **Decision-record deltas** (§8) — flagged, committed only after results.
- **Handed to Phase 8 (the economy + cost):** the committed head(s) whose real cost the meter must price (esp. the
  analytic head's projection/solve — is "no-gradient" actually cheaper on our substrate?); the gate that fires the namer.
- **Handed to Phase 9 (maintenance + owed baselines):** the fair same-budget **BP+replay** continual baseline; the
  natural multi-class **A5** number; the imbalance guard (incl. **AIR** for a no-gradient head) + multimodality modeling
  to carry; and **the read-side noise residual** (input-transducer directional + ADC < 3-bit — the Phase-6 brief).
- **The random-projection read** — if the bulk ties a random projection at flat-home naming, that is a **flagged,
  unverified naming-stage value** handed to the Stage-2 report (both readings), **not** a pre-excused footnote.
- **Deferred to the analog/PVT phase (out of numpy scope):** the true charge/ADC/write-energy cost of each head; SPICE.
- **North-star tie-break:** the **cosine margin** grounded as a *direction* "feeling" signal for the recurrent brain.

---

## 10. References

The mechanism stories: [`../../research/papers/phase7/`](../../research/papers/phase7/README.md) —
[`the-convex-readout.md`](../../research/papers/phase7/the-convex-readout.md) (reservoir/ELM/OCO — why it's convex),
[`direction-readouts.md`](../../research/papers/phase7/direction-readouts.md) (cosine/NCM/SLDA/RanPAC + the magnitude
bias), and the **2nd-pass audit**
[`analytic-and-covariance-readouts.md`](../../research/papers/phase7/analytic-and-covariance-readouts.md) (the Analytic/RLS
family + F-OAL + FeCAM + RanDumb + GKEAL). Key IDs (review-corrected): RanPAC
[2307.02251](https://arxiv.org/abs/2307.02251) · FeCAM [2309.14062](https://arxiv.org/abs/2309.14062) · **Deep SLDA**
[1909.01520](https://arxiv.org/abs/1909.01520) · RanDumb [2402.08823](https://arxiv.org/abs/2402.08823) · **F-OAL/AOCIL**
[2403.15751](https://arxiv.org/abs/2403.15751) (NeurIPS 2024) · **ACIL** [2205.14922](https://arxiv.org/abs/2205.14922)
(NeurIPS 2022) · **GKEAL** CVPR 2023 (few-shot, no arXiv; repo `ZHUANGHP/Analytic-continual-learning`) · DS-AL
[2403.17503](https://arxiv.org/abs/2403.17503) · GACL [2403.15706](https://arxiv.org/abs/2403.15706) · **AIR**
[2408.10349](https://arxiv.org/abs/2408.10349) · SCR [2103.13885](https://arxiv.org/abs/2103.13885) · task-recency-bias
survey [2010.15277](https://arxiv.org/abs/2010.15277) · Lion [2302.06675](https://arxiv.org/abs/2302.06675).

The evaluation-methodology canon (carry from Phase 4/5/6): **gap-to-tuned-BP** — Bartunov 2018
([1807.04587](https://arxiv.org/abs/1807.04587)); **measured (not theoretical) cost** — Spyra 2025
([2511.01061](https://arxiv.org/abs/2511.01061)); **continual = AA/BWT/FWT/forgetting** — CL survey
([2302.00487](https://arxiv.org/abs/2302.00487)), GEM ([1706.08840](https://arxiv.org/abs/1706.08840)). Carry-overs: the
frozen cell ([`../phase6-final-architecture.md`](../phase6-final-architecture.md)), the `result-format` lineage.
