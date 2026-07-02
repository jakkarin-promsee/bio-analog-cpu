# Phase 9 — Close & *freeze* the maintenance loop: the lifelong neocortex, tuned then locked (the plan)

> **Status: 🟡 READY-TO-RUN (plan hardened 2026-07-02; deep-research folded — §0.3, [`deep-research-delta`](../../research/papers/phase9/deep-research-delta.md);
> lab-manager review folded — §8; nothing run, nothing committed to `main.ideas`).** A *live spec an agent executes* — the
> experiment ladder + build plan for the **close-out of the two-brain maintenance loop**: tune the genuinely-open knobs
> against *internal* signals, then **freeze the object** so Phase 10 can race it fairly. When the rungs run they fill
> `expK/experiment-K.md`, `RESULTS.md`, then the public `README.md` + `phase9-report.md`. Reporting contract:
> [`result-format.md`](result-format.md). Literature: [`../../research/papers/phase9/`](../../research/papers/phase9/README.md)
> — **including the deep-research delta** [`../../research/papers/phase9/deep-research-delta.md`](../../research/papers/phase9/deep-research-delta.md).
> The frozen cell it maintains: [`../phase6-final-architecture.md`](../phase6-final-architecture.md). The committed namer +
> economy it inherits: [`../phase8/README.md`](../phase8/README.md). The Stage-2 map: [`../stage2-design.md`](../stage2-design.md) §4.
> Decision record: [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md).
>
> **Phase 9 = the third of four Stage-2 phases** (P7 readout ✓ · P8 economy+cost ✓ · **P9 maintenance / close** · P10
> validation / showcase). Phase 8 turned both brains on and metered the economy; **Phase 9 finishes the machinery that
> lets the loop survive forever, sets every remaining knob against internal signals, and locks the object** so Phase 10
> can race it. The whole back half's honesty rides on one cut: **freeze in P9, judge in P10.**

---

## 0 · Why Phase 9 exists — the problem, the reframe, and what it is NOT

### 0.0 The arc — the Namer is chosen; the *loop around it* is not yet tuned

"We're almost done, so polish it" is the **wrong** reading, and the discipline says so. The Namer is **committed** —
Phase 7 raced nine heads on a pre-registered rubric, Phase 8 metered the survivors and committed **SLDA** (RanPAC the
accuracy/spine reference). Re-opening that is re-litigating S11/S12 — the move rule 8 forbids (*architecture changes are
decisions, not experiments*) and rule 5 warns against (*don't tune until it works*). **Phase 9 does not touch the head.**

What is genuinely still open is the **lifelong maintenance loop** *around* the frozen head — the machinery that keeps the
namer tracking a drifting bulk over a stream that runs forever. Phase 8 built the loop and set its **coarse** knobs (DDM
gate, class-direction trigger, grid-8 sleep) but flagged five things as **measured-not-tuned** or **assumed**:

- the SCFF **bulk-drift rate** the whole "the bulk doesn't forget → sleep is cheap" story rests on (assumed, not measured);
- **N2** — the last un-resolved decision-record knob (EMA-view / late-layer drift-slowdown) — still on *standby*;
- the **sleep cadence's consolidation *depth*** (which extractor layers to re-fit), which P8 punted ("readout-aware");
- **bounded-LUT eviction** under a bursty, class-imbalanced lifelong stream (P8's sleep used a *fixed balanced probe* / a
  growing buffer only in block mode — neither a bounded *evicting* store, which a lifelong stream forces; §2.3-P9.3) — untested;
- the **read-side noise residual** (the Phase-6 brief — the input-transducer directional channel + ADC < 3-bit).

Phase 9 closes these against internal signals, **then freezes.** That freeze is the deliverable as much as the tuning is.

### 0.1 The one discipline — freeze in P9, judge in P10 (load-bearing)

> **You must not tune the loop against the baseline you will be judged by.** If Phase 9 optimizes cadence / N2 / eviction
> while watching the fair BP+replay number, the existential P10 test is contaminated — *tuning-to-win at the phase level.*
> So Phase 9 tunes against **internal signals only** — measured drift, BWT vs the **frozen / known-boundary-oracle**
> reference, self-consistency, fire-rate, and metered energy — **never** against the P10 BP+replay comparison — commits,
> and **freezes** (a git hash proving the loop was locked *before* the fight). Build, then judge. It is the same rhythm
> Stage 1 used (P3 adopt → P4 characterize) and the only cut that lets P10 answer *"did you tune against the baseline?"*
> with **no, and here's the commit.** *(This is standard train/validation hygiene — [`deep-research-delta`](../../research/papers/phase9/deep-research-delta.md) D5.)*

### 0.2 What Phase 9 is NOT — the scope guard

- **NOT re-opening the Namer.** SLDA committed; RanPAC the reference. No head bake-off. A meter/robustness finding that
  moves the head is a *decision to flag*, not a P9 re-run.
- **NOT the fair BP+replay *accuracy* fight, NOT the multi-domain gauntlet, NOT the noise showcase, NOT natural
  multi-class A5 → all Phase 10.** Those are *judgments on the frozen object*; running them here contaminates the tuning or
  pre-empts the freeze. *(⚠ The living [`../stage2-report.md`](../stage2-report.md) §3/§8 still place A5 in P9 — period-correct
  before the 2026-07-02 re-plan; the authoritative split is [`../stage2-design.md`](../stage2-design.md) §4 + [`../phase10/design.md`](../phase10/design.md) P10.4 = **A5 is P10**. P9 may *confirm* a tuned knob on `digits` the way every prior phase did — a natural-confirm surface — but the A5 *characterization number* is P10's.)*
- **NOT re-opening the frozen SCFF objective.** N2 is tested **read-side / rate-only** — a plasticity-*rate* knob on the
  layers the namer reads and an EMA *view* of the taps — it must not move `τ=0.2 / w=2 / the norm / σ_aug=1.0`. If N2 can
  only help by changing the SCFF objective, that is a *Stage-1 reopen*, **flagged and deferred, not done inside P9.**
- **NOT a new trained organ.** A **learned drift-compensation projector** (LDC/SDC — [`deep-research-delta`](../../research/papers/phase9/deep-research-delta.md) D1)
  is the road-not-taken, out of the read-side/rate-only scope → cited, scoped-out, with a precise re-open trigger, not built.
- **NOT SPICE / device physics.** The meter stays the P8 behavioral ADC-centred model (analog + digital substrate axes).
- **NOT the north star.** No recurrence; the direction-grounded gate/margin are carried as a **tie-break bias** only.

### 0.3 The rough guess, and what the deep research changed (the honest-science record)

Per the project's pre-registration habit, the pre-research guess is banked (the **rough-guess column** below — the concept
dump written before the research) and the deep-research pass ([`deep-research-delta`](../../research/papers/phase9/deep-research-delta.md))
tested *"is it enough, and is there a better choice?"* Five deltas were folded into the ladder below:

| rung | the rough guess | what the research changed |
| --- | --- | --- |
| P9.0 | "measure drift; likely slow → cheap" | **the assumption is a real risk** — continuous SSL *does* forget (ECCV'22; 2311.13321). Split **rotation vs destruction**, it is a gate not a warm-up. *(The review then sharpened this to **three** curves — a frozen probe conflates rotation with forgetting; §8 B1.)* |
| P9.1 | "N2 slow/EMA; SDC a vague road-not-taken" | the road-not-taken is **LDC** (ECCV'24, unsupervised-capable, exemplar-free); kept scoped-out with a precise trigger. N2 = a **3-arm** bake-off. |
| P9.2 | "home-grown consolidation depth" | it is **Latent Replay** (IROS'20), published; couples to P9.1 ("slow below the read layer"). |
| P9.3 | "cbrs vs recency vs magnitude" | **drop GSS** (needs gradients we don't have); **herding = the magnitude/mean spine-null**; **D-CBRS** the diversity refinement; add a cap×#classes scaling sub-sweep. |
| P9.4 | "temperature-scaling-style calibration" | plain TS is **ineffective under shift** → the read-side defense must be **feature/prototype-level** (SLDA re-estimation), raising the earn-its-place bar. |

---

## 1 · The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — read the class DIRECTION, never a MAGNITUDE (9th coat).** In Phase 9 it lives in three places: **eviction**
(P9.3 — keep prototypes that span the class *directions*, not the densest / most-recent region; **herding** keeps the class
*mean* = a magnitude, so it is the spine-null, expected to re-import forgetting — density ≠ class, at the buffer); the **N2
EMA-view** (P9.1 — smooth the taps the namer reads without letting a magnitude drift decide what gets consolidated); and
the **read-side calibration** (P9.4 — direction-grounded, never a confidence/entropy magnitude). density ≠ class, still travelling.

**The envelope — GD reads taps, never writes SCFF (the P2.5 forward-leak wall, unbroken).** N2's slowdown touches the
*read-layer plasticity rate* and an EMA *view*; it never writes a supervised signal upstream of SCFF. Sleep, eviction, and
read-side calibration touch **only** the namer and the LUT. The frozen SCFF objective (`τ/w/norm/σ_aug`) does not move — a
guard asserts it (§6).

**Guards FIRST, every run — the netlist rule.** Import P8's tested primitives (the `partial_fit` equivalence, the live-path
anchor, the meter proxy, the detector-FAR floor, the cache-replay guard); each new organ (the N2 view/rate, the eviction
policies, the read-side re-fit) ships with its own equivalence/behaviour guard. **Any guard fails → STOP.**

---

## 2 · The mechanism, the deliverables, and the numeric verdict cuts (pinned BLIND)

### 2.1 What the loop performs, and what P9 tunes on top of P8

Phase 8 committed the live loop's **coarse** shape (per stream step, awake): SCFF forward+local-update *always* (op a);
namer forward *always* (op b); namer `partial_fit` *gated* by DDM on the class-direction trigger (op c); periodic **sleep**
= re-forward the raw LUT → rebuild the running Gram `(G,M)` → re-solve (op d). Phase 9 tunes the **fine** machinery **around**
that fixed shape — it changes *what the namer reads* (N2), *what depth sleep re-fits* (P9.2), *which prototypes the LUT
keeps* (P9.3), and *whether a read-side calibration defends the noise residual* (P9.4) — **never** the head, the objective,
or the gate/trigger P8 committed. Every rung is scored against P8's **internal** references (the frozen/oracle baseline, the
always-pay ceiling, the measured drift, the metered energy), never P10's baseline.

### 2.2 The deliverables

- **A · the measured bulk-drift rate** (P9.0) — the number the whole cheap-replay story assumed, with the **rotation-vs-
  destruction** split that says whether "the bulk doesn't forget" is *true* for our objective on a lifelong stream.
- **B · N2 resolved** (P9.1) — standby → **default** (which form) or **struck**, the last open decision-record knob, tested
  read-side/rate-only.
- **C · the readout-aware sleep cadence** (P9.2) — the consolidation *depth* (latent-replay layer), and the frequency
  re-confirmed if N2 changed the drift rate.
- **D · the bounded-LUT eviction policy** (P9.3) — the committed policy that holds continual-safety under a bursty,
  class-imbalanced, *bounded* lifelong buffer + the cap-vs-#classes scaling flag.
- **E · the read-side noise residual, resolved or named** (P9.4, conditional) — defended read-side, or handed to the
  analog layer with its mechanism stated.
- **F · the frozen loop** (P9.5) — the complete committed neocortex, live-safe on the fully-tuned configuration, **locked
  at a commit hash** Phase 10 races.

### 2.3 The numeric verdict cuts (PINNED BLIND — shapes with thresholds, never expected results)

`δ_acc = 0.02` (the house bar), paired by seed; a difference is **real** iff IQR-disjoint at the final checkpoint **and**
sign-consistent in ≥4/5 paired seeds; A6 re-checks run the full 5 seeds (never 3) with the **paired-sign veto**. **Every cut
below is against an INTERNAL reference — the frozen/known-boundary-oracle baseline, the always-pay ceiling, the measured
drift, or the metered energy — NEVER the P10 BP+replay number.**

- **P9.0 — bulk drift (the risk gate). Report THREE curves, not two** (the probe-basis fix — flagged by all three
  reviewers: a *frozen* linear probe is basis-dependent, so a pure rotation tanks it and gets mis-read as forgetting).
  **(1) rotation** = `bulk_drift` cosine of fixed probes (the rate a fresh sleep re-solve tracks); **(2) readout-staleness**
  = a probe **fit once at birth and re-applied** to the current bulk (how much a *fixed head* rots — exactly what sleep
  exists to fix); **(3) destruction** = an **optimal linear probe RE-FIT on the current bulk**, scored on held-out
  early-task data (the true forgetting measure — Davari et al. *Probing Representation Forgetting*, [2203.13381], which
  factors rotation out). **The verdict keys on (3), the re-fit curve** (not the frozen probe). "Rotation-only / the
  cheapness holds" iff the re-fit retention (3) stays within `δ_acc` of its birth score across the long stream (paired) —
  *even if (1)/(2) move.* **"The bulk forgets" (headline)** iff the re-fit retention (3) drops **> δ_acc**, sign ≥4/5 — the
  founding assumption breaks; flag whether N2 becomes *mandatory* (drift too fast for any cheap cadence) or the loop must be
  reshaped. **Prior (set expectations honestly):** the SSL-continual literature leans toward *some* degradation
  ([2311.13321] finds supervised+MLP learns *higher-quality* continual reps than SSL), so budget for the degrade branch
  rather than treating rotation-only as the default. No knob is tuned here — a measurement + a fork.
- **P9.1 — N2 (adopt / struck / reopen-flag).** **EMA-view is the doubly-grounded, in-scope default** — truly read-side
  (it post-processes the taps the *namer* reads, touches SCFF not at all), and it is the arm the momentum-encoder finding
  ([2208.05744], "EMA of late-layer weights") actually grounds. **LLRD-rate is a flagged secondary arm**: it slows SCFF's
  *late-layer training dynamics* (a `LLRDCell` subclass, objective byte-identical — §6), so it is "rate-only" **only if the
  representation guard holds.** An arm is **adopt-eligible** iff it **reduces sleep frequency (or `bulk_drift`)** at
  **accuracy-held within δ_acc** of the no-N2 loop (paired) **AND worst-point A6-BWT not worse** (veto) **AND plasticity /
  new-task acc not down > δ_acc** (the slowdown tax — an EMA/slowdown that lags a genuinely-shifting world is *late* to
  follow it) **AND** the `n2_readside_guard` is green. For LLRD-rate the guard is **representation-level**: `ρ=1` reproduces
  P8 bit-for-bit **and** the early/mid-layer taps are unmoved (only the late-read layers slowed); if LLRD-rate moves
  early/mid taps it is a **Stage-1-reopen, flagged not executed** (the honest boundary — changing what SCFF *learns* is not
  "rate-only"). Among adopt-eligible arms commit the cheaper. **Struck** iff no arm clears the bar. **Adopted-but-inert:** if
  an adopted arm's drift-reduction does not actually loosen the sleep cadence at P9.2, it must justify its substrate cost or
  be **struck at assemble** (an inert N2 is not carried into the freeze).
- **P9.2 — consolidation depth (adopt depth-matched / keep all-tap).** Adopt the **deployed-depth (trunc-K) sleep re-fit**
  iff its worst-point **A6-BWT is held** (within δ_acc of the all-tap sleep, paired, veto) at a **strictly lower metered
  sleep cost** (`sleep_cost` E-ratio ≥ ~1.5×, frontier-knee not a hard binary). The saving is **real only if trunc means a
  shorter forward stack** (fewer SCFF layers re-forwarded at sleep → the arch-§3.1 ~8× readout-forward saving); if it merely
  re-slices the *top* of the full-depth forward, the saving is only the smaller solve/Gram (`Fdim`) term — the meter prices
  the **actual forward depth per arm** (§6). Else **keep P8's all-tap cadence** and note depth did not matter. **One
  variable per rung:** the depth verdict is read only from the depth sweep at the *committed* frequency; the **sleep-
  frequency re-confirm** (owed only if P9.1 adopted N2 and slowed the drift — the P8 "cadence is drift-rate-conditional"
  debt) runs as a **separate sub-table**, never co-varied with depth in the primary read.
- **P9.3 — eviction (CBRS committed / re-imports forgetting / scaling flag).** *(⚠ Apparatus correction — repo-fit B1:
  P8's streaming sleep re-solves over a **fixed 600-item balanced probe**, not a growing history, so there is no P8
  "full-history" to bound. P9.3 first **builds the accumulating streaming LUT** — a store that appends prototypes as the
  stream runs — and the **unbounded oracle = that new organ at cap=∞**, not a P8 path; §6.)* At a **pinned cap** (set at a
  pressure point — the smallest cap at which the unbounded oracle *itself* first shows measurable BWT sensitivity, or the
  small-buffer 1–3-exemplars/class regime the literature uses; pre-registered so the bound actually bites), **CBRS is
  committed** iff its worst-point BWT is **within δ_acc of the unbounded oracle** (paired) **AND** better than
  recency/herding by ≥ the real-difference bar. A policy **re-imports forgetting** iff its BWT drops > δ_acc vs the oracle
  (logged with mechanism). The **scaling flag** fires iff, in the cap × #classes sub-sweep (a **separate sub-table**), the
  smallest cap holding BWT **grows with class count.** **Herding is the magnitude/mean spine-null** — but it only *bites* if
  the class dense-center diverges from the direction-span in the evicted (raw-input) space; on the bursty/imbalanced stream
  the dense center is a **majority-class artifact**, which is where it should fail. If herding instead lands within δ_acc of
  CBRS, report **"buffer-spine null here (raw ~unimodal — density ≈ class at the buffer on this task)"**, *not* a spine win
  (a null that cannot fail is not a control). GSS is not raced (gradient-free namer).
- **P9.4 — read-side residual (conditional; earn-its-place first).** **Earn-its-place probe:** the Phase-6 residual (input-
  transducer directional + ADC<3-bit, injected with the Phase-6 `NoiseModel` — §6, *not* P8's layernorm-invariant nuisance,
  which SCFF removes by construction → a vacuous probe) is *in scope* iff it dents the **committed SLDA loop's** retention by
  **> δ_acc** on the continual home. **If not → one-line skip card, defer to the analog-realism layer.** If it earns its
  place, the read-side defense is **prototype re-anchoring from the raw LUT** (re-forward the raw exemplars through the
  *current* bulk under the shift → drift-free, shift-consistent prototypes — the plan's own sleep mechanism, = test-time
  prototype shift [2403.12952]; the **primary**), with **SLDA class-mean / shared-covariance re-estimation** the *fallback*
  (feature-level — scalar temperature scaling is ineffective under shift, D4; and the covariance re-fit needs a **shrinkage /
  min-count guard** under the bursty classes, §6). **Recovers** iff retention lifts toward the no-residual level (paired
  ≥4/5); else the residual is **named** (→ analog layer). The calibration signal is **direction-grounded** (never
  entropy/confidence — the spine). **Freeze-hygiene:** P9.4 tunes only against the **home-stream residual vs the internal
  no-residual retention**; **P10's noise showcase must use a held-out noise battery** (different σ / channel mix) never seen
  here — so P9.4 does not pre-run the P10 showcase.
- **P9.5 — assemble + FREEZE.** The fully-tuned loop (all committed knobs on) **freezes** iff, live and 5-seed, the
  worst-point (pre-sleep) **A6-BWT is not negative vs the oracle in ≥4/5** (the paired-sign veto) **AND accuracy-held is
  within δ_acc of the P8.6 committed-loop live AA** (the pinned internal reference — "P9's tuning did not *cost* accuracy vs
  the object P8 already shipped"; paired — this replaces the unpinned "sum-of-components" slogan) **AND** the metered
  GD-share stays ≤ 0.25. A knob **interaction** that breaks any of these is fixed **inside P9** and re-frozen — never carried
  into P10. The freeze = a git hash + a manifest whose **committed-knob block enumerates every knob explicitly, including the
  conditionals resolved off** (e.g. `N2: EMA-view` or `N2: struck`; `read-side-residual: skipped (gate not fired)`) — so the
  frozen object Phase 10 races is fully specified by its manifest alone.

**No result may be narrated into a branch it does not numerically satisfy.** A struck arm (N2-none, a losing eviction
policy, a skipped P9.4) is a card with its mechanism — a result, logged and moved past.

---

## 3 · The ladder — P9.0 → P9.5 (one variable per rung; guards first; each states its read-including-failure BEFORE it runs)

- **P9.0 — bench + the bulk-drift rate + the rotation/staleness/destruction split (the risk gate).** Build `p9lib` on
  `p8lib`; build the **long/lifelong stream** (`make_lifelong_stream` — many cycles / repeating tasks, so drift accumulates
  past P8's single-pass CI schedule) + the **three-curve probe instrument** (`probe_retention` — the re-fit optimal probe,
  the fit-once frozen probe, and the cosine; §6). Run the **P8 guard set** + the new `n2_readside_guard`/`evict_equiv_guard`.
  Measure **(1)** `bulk_drift` cosine (rotation), **(2)** frozen-probe readout-staleness, **(3)** re-fit-probe destruction on
  held-out early-task data. **Read (incl. failure), keyed on curve (3):** *destruction flat within δ_acc (rotation-only —
  the cheapness holds — proceed) / destruction decays > δ_acc (the bulk **forgets** — headline; N2 mandatory or reshape?) /
  drift so fast no cheap cadence tracks (economy drift-bound → N2 mandatory, flag).* No knob tuned — a measurement + the fork
  that gates the rest.
- **P9.1 — N2: the drift-slowdown bake-off (read-side / rate-only).** Swept variable = the N2 mechanism ∈ {**no-N2**
  (P8 loop) · **EMA-view** (namer reads a tap-EMA — the doubly-grounded, truly-read-side default) · **LLRD-rate** (a
  `LLRDCell` subclass slowing the late-read layers — the flagged secondary, guarded representation-level)}. Score
  **drift-reduction × sleep-frequency-at-held-accuracy × worst-point A6-BWT × plasticity (new-task acc)**. **Read:**
  *an arm ↓ drift → sparser sleep at held A6 without a plasticity tax → N2 standby→**default** (commit the cheaper eligible)
  / no arm clears the bar → N2 **struck** / LLRD-rate moves the early/mid taps → **Stage-1 reopen flagged, not done** / an
  adopted arm doesn't loosen the cadence → **adopted-but-inert**, justify cost or strike at assemble.* (LDC = the scoped-out
  road-not-taken — a learned projector, out of the read-side/rate-only scope; cited, not built.)
- **P9.2 — readout-aware sleep cadence: the consolidation depth (latent replay).** Swept variable = the sleep-consolidation
  feature depth ∈ {**all-tap** (P8 default) · **trunc-K** (the deployed reader's depth, S9) · **per-depth**}. Score
  worst-point **A6-BWT × metered sleep-cost**. If P9.1 adopted N2, add a **frequency re-confirm** sub-step on the slowed
  drift. **Read:** *trunc-depth holds A6 at strictly lower sleep cost → adopt depth-matched consolidation / depth doesn't
  matter → keep P8's all-tap cadence, note it / a depth interacts badly with N2 → log and prefer the robust one.*
- **P9.3 — bounded-LUT eviction under the bursty stream.** First **build the accumulating streaming LUT** (§6 — P8 has no
  growing history to bound). Swept variable = the eviction policy ∈ {**unbounded-oracle** (the new LUT at cap=∞ = the
  ceiling) · **CBRS** (committed) · **reservoir** (iid) · **recency/FIFO** · **herding** (feature-mean = the magnitude/
  spine-null)} at a **pinned pressure-point cap**; **D-CBRS** conditional (only if CBRS loses intra-class diversity — and it
  needs a **hand-rolled single-threaded** diversity scorer, **not sklearn K-means**, per the phantom-hang rule, §6); **GSS
  not raced** (gradient-free). Then a **cap × #classes** scaling sub-sweep (separate sub-table). Score worst-point
  **BWT-at-bound vs the oracle**. **Read:** *CBRS holds BWT at the bound (commit) / a policy re-imports forgetting
  (first-class risk, headline; herding expected to *if* the raw dense-center diverges from the direction-span — else the
  buffer-spine is null here) / the bound must grow with #classes (scaling-law flag).*
- **P9.4 — read-side noise residual (CONDITIONAL — earn-its-place probe first).** Gate probe: does the Phase-6 `NoiseModel`
  input-transducer residual dent the committed SLDA loop by > δ_acc on the continual home? **If no → one-line skip card,
  defer to analog layer.** If yes, swept variable = read-side defense ∈ {**off** · **prototype re-anchoring from the raw
  LUT** (primary) · **SLDA covariance re-estimation** (fallback, shrinkage-guarded)}. Score **residual-retention
  recovered**. **Read:** *a read-side defense recovers the residual → adopt / it can't → the residual is real and named →
  analog layer.* (Scalar temperature scaling is a *diagnostic only* — ineffective under shift. P9.4 tunes on the home
  residual only; P10's showcase uses a held-out battery.)
- **P9.5 — assemble + FREEZE (the integration + the lock).** Every committed knob live at once — `NoiseAugContrast` bulk +
  SLDA + DDM gate + class-direction trigger + the P9-tuned cadence/depth + the committed eviction policy (+ N2 if P9.1
  adopted, + read-side if P9.4 earned). Re-run the **P8.6 live-safety gate** on the *fully-tuned* loop, 5 seeds, paired-sign
  veto, BWT at the worst mid-stream point; one integration figure (the complete neocortex loop). **Read:** *the assembled
  loop holds A6 + accuracy at the metered economy → **commit + freeze** (the hash Phase 10 races) / a knob interaction
  breaks it → fix inside P9 and re-freeze.*

*(Rungs are decisions backed by a result, not experiments tuned to pass. A struck arm is a card with its mechanism. Heavy
live cells (P9.1, P9.3, P9.5) checkpoint + single-thread + verify PID — the phantom-hang discipline. Seeds
`[42,137,271,314,1729]`, median + IQR, paired-sign veto on every A6 re-check; decisive gaps ≤ δ_acc get 9 seeds.)*

**Dependency order (load-bearing).** P9.0 gates everything (if the bulk forgets, the fork reshapes the rest). P9.1 (N2)
runs before P9.2 because N2 can slow the drift, and P8 flagged the cadence **drift-rate-conditional** — so P9.2 tunes on
the possibly-slowed drift. P9.3 (eviction) and P9.4 (residual) are independent of each other. P9.5 assembles all survivors.

---

## 4 · Metrics (PINNED; Phase-9 additions in **bold**; the rest carried from P8)

| metric | definition (pinned) | units / format |
| --- | --- | --- |
| **accuracy-held** | live-stream final AA, vs the **frozen/oracle** baseline + the **always-pay** ceiling (P8 refs) | acc, median [IQR] |
| continual **BWT / AA / forget** | GEM/CL conventions (`acc_matrix_metrics`) on the LIVE loop, **at the awake gate's worst mid-stream point (pre-sleep)**; vs oracle/frozen; + paired-sign veto | acc / acc-delta |
| **GD-fire-fraction** `f` / **sleep-frequency** | fraction of steps firing op(c) / sleeps per stream (the economy the tuning must not inflate) | fraction / count |
| **live SCFF drift `bulk_drift` (rotation)** | `cos(rep_t, rep_{t+Δ})` of fixed probes across the **long** stream — the rate a fresh sleep re-solve tracks | cosine vs step |
| **readout-staleness (frozen probe)** | a probe **fit once at birth, re-applied** to the current bulk — how much a *fixed head* rots (what sleep fixes) | acc-ratio vs step |
| **destruction retention (re-fit probe) ⭐** | an **optimal probe RE-FIT on the current bulk**, scored on held-out early-task data — the true forgetting measure (2203.13381; **the P9.0 verdict curve**, rotation factored out) | acc-ratio vs step |
| **drift-reduction** | `bulk_drift` (or sleep-frequency) with N2 vs without — the P9.1 lever's effect | Δ / ratio |
| **plasticity / new-task acc** | acc on the newest task right after it arrives — the N2 slowdown **tax** check | acc, median [IQR] |
| **sleep-cost** | metered readout energy at sleep per consolidation depth (the P9.2 saving) — the P8 ADC-centred meter, sleep path | relative-E |
| **evict-BWT** | worst-point BWT at a **bounded** buffer per eviction policy vs the unbounded oracle (P9.3) | acc-delta |
| **buffer-cap scaling** | smallest cap holding BWT within δ_acc, vs #classes (the scaling law) | cap vs #classes |
| **residual-retention** | directional retention of the committed SLDA loop, read-side-defended vs undefended (P9.4) | retention ratio |
| **hardware energy / metered 80/20** | the P8 behavioral ADC-centred meter; `GD-share` must stay ≤ 0.25 through the tuning | relative-E / fraction |

**Threats-to-validity, every rung (carry P8 + P9-new):** (a) the meter is a **behavioral model** — log/cite per-op params;
(b) the long-stream drift depends on the **stream schedule** — the **re-fit-probe destruction curve** is the
schedule-independent read (rotation factored out); (c) **calibration-under-shift** for P9.4 (feature-level, not scalar TS); (d) the oracle uses hidden
boundaries the loop can't see — matching it is the *win*; (e) **the internal-signals-only rule** — no rung's verdict may
reference the P10 BP+replay number (state it in each card).

---

## 5 · What Phase 9 hands Phase 10 / defers (the seam, stated so nothing is lost)

- **→ Phase 10 (the frozen brief):** the **frozen loop** (commit hash) — the complete committed neocortex; the **measured
  drift rate** (P9.0) so P10's cadence/cost numbers are grounded not assumed; the **named residuals** (anything P9.4
  couldn't reach → analog layer). Phase 10 does not touch a knob.
- **→ Phase 10 (the owed fights, unchanged):** the fair same-budget **BP+replay *accuracy*** baseline (the existential
  test); **natural multi-class A5**; the multi-domain gauntlet; the noise showcase. *P9 must not run these* (the freeze
  discipline).
- **→ analog-realism / north-star (road-not-taken, cited):** a **learned drift-compensation projector** (LDC/SDC) if N2
  can't slow the drift *and* the LUT re-forward meters too expensive (a new trained organ, out of P9 scope); an
  **oracle-exit / better-than-confidence per-sample selector** (parked from P5, wants a direction signal); the read-side
  residual if P9.4 can't reach it read-side.

---

## 6 · What to build — `p9lib.py` on `p8lib` (import, don't retype — the netlist rule)

**Verified-present carries (import — from `p8lib`, which re-exports p7/p6/p5…):** `awake_sleep_loop` (dual-mode),
`build_cache`, `run_economy`, `RanPACHeadStream`/`SLDAHeadStream` (+ `partial_fit`/`sleep_fit`), `make_stream_head`,
`make_drift_stream`/`nuisance_transform`, the detectors (`DDM`/`ADWIN`/`AbsTheta`/`BudgetGate`), the triggers
(`sig_tap_drift_direction`/`_magnitude`/`sig_error_ema`/`sig_driftlens`/`sig_studd`), `hardware_cost_meter`/
`bp_replay_energy`/`meter_from_trace`, `class_balanced_reservoir`, `continual_safety_heads` (the oracle/block-mode
reference **and the only path with a *growing* full-history buffer — the eviction anchor, below**), `readout_feats`/
`all_tap_feats`/`trunc_feats`, `make_committed_cell`/`train_cell`, `acc_matrix_metrics`, `CISTREAM_TASKS`, `synth_stream`,
`load_digits_split`, `linear_probe`, `race_bp`, and **all P8 guards** (the exported names carry the `_guard` suffix —
`partial_fit_equiv_guard`, `live_path_anchor_guard`, `scff_static_frozen_guard`, `meter_proxy_guard`, `detector_far_guard`,
`cache_replay_guard`, `fd_budget_gate_guard`). **Direct from `p6lib` — NOT re-exported by `p8lib`, so `p9lib` must
`sys.path.insert` the `../phase6` dir (as `p8lib` does for `../phase7`):** `bulk_drift` (the P9.0 drift cosine — computed
*inline* in `build_cache`, not imported from `p8lib`) and `NoiseModel`/`infer_noisy` (the P9.4 residual channel). The
committed economy config is frozen in `p8cfg` (SLDA + DDM + class-direction trigger + grid-8/full/λ1.0).

**NEW to build for Phase 9** *(folds the lab-manager review — §8; each item names the finding it closes):*
- **`make_lifelong_stream(...)`** — the **long/repeating** stream (many cycles of the CI tasks + re-visits) so drift
  accumulates past P8's single-pass schedule; emits the same real/nuisance onset markers. The P9.0 bench.
- **`probe_retention(...)`** — the **three-curve** P9.0 instrument (the basis-dependence fix — red-team B1 / repo-fit B4 /
  lit C4): **(1)** the cosine (`bulk_drift`, from `p6lib`); **(2)** a **fit-once frozen** probe — a small helper that fits a
  linear head on birth-time features and **returns `W`** (`linear_probe` returns only accuracy, so it cannot freeze-then-
  reapply — fit a bare linear head / `p4lib.MLP` directly and keep it) then re-applies it to later features (readout-
  staleness — what sleep exists to fix); **(3)** a **re-fit optimal** probe re-trained on the *current* bulk, scored on
  held-out early-task data (destruction — the 2203.13381 protocol, rotation factored out; **the verdict curve**). All three
  read the **per-layer probe reps** (the cache addition below).
- **Cache-schema addition (repo-fit B3/B4):** `build_cache` stores `phi_probe` **all-tap only** — add `rec["reps_probe"] =
  reps_pr` (the per-layer probe reps at grid steps) so (a) P9.0's probes score at any depth and (b) P9.2's depth selector
  can `readout_feats(reps_probe, k)` — trunc/per-depth features **cannot** be re-sliced from a concatenated all-tap vector.
- **N2 arms:** `ema_view(...)` — a **stateful tap-EMA** applied *inside the replay loop* to the features the namer reads
  (`phi_b`/`phi_probe`); read-side, SCFF untouched, **cache-valid** (reuses the P8 cache; a stateful pass over the step
  sequence, not a pure lookup — repo-fit C5). · `LLRDCell(NoiseAugContrast)` — a **subclass** (repo-fit B2: `train_step` has
  a single scalar `lr`, no per-layer kwarg) overriding only the final update loop to multiply layer `l`'s `scale` by a
  per-layer `ρ_l` (1.0 except the late-read layers); the objective (masking, InfoNCE, `τ/w/norm/σ_aug`) stays byte-identical.
  Because LLRD changes SCFF training it needs **its own `build_cache` per `ρ`** (EMA-view reuses the P8 cache). **Guard
  `n2_readside_guard`:** N2-off reproduces the P8 committed run **bit-for-bit**; EMA-view asserts SCFF weights/objective
  untouched; **LLRD-rate is guarded representation-level** (red-team B2) — `ρ=1` ⇒ bit-for-bit P8 **and** the early/mid-layer
  taps unmoved at `ρ<1`; early/mid taps move ⇒ **Stage-1-reopen flag** (not a silent adopt).
- **Consolidation-depth at sleep:** a `sleep_depth ∈ {alltap, truncK, perdepth}` selector in the sleep re-fit path (calls
  `readout_feats(rec["reps_probe"], k)`). `sleep_cost` = the `hardware_cost_meter` sleep path priced **at the actual forward
  depth per arm** (repo-fit C6: trunc = a shorter forward stack → fewer re-forward MACs → the arch-§3.1 ~8× saving; if trunc
  only re-slices the top of the full forward, only the smaller-`Fdim` solve/Gram term saves — pass the depth-appropriate
  `Fdim`/`scff_dims` into the meter).
- **The accumulating streaming LUT + eviction (repo-fit B1):** `StreamingLUT(cap, policy)` — a store that **appends** raw
  prototypes as the stream runs (P8's streaming sleep uses a *fixed 600-item balanced probe* — there is **no growing history
  to bound**), replacing the fixed-probe sleep set with a bounded, evicting one. Policies (**all new-build except cbrs**):
  `evict_cbrs` (wrap `class_balanced_reservoir`), `evict_reservoir` (iid), `evict_recency` (FIFO), `evict_herding` (keep
  feature-mean-nearest over the current bulk — the magnitude null), `evict_dcbrs` (conditional — a **hand-rolled
  single-threaded** intra-class diversity scorer, **NOT sklearn K-means**: the KMeans/OpenMP phantom-hang on this box, lit
  C1 + MEMORY.md). **Guard `evict_equiv_guard`:** `StreamingLUT(cap=∞)` ≡ the **block-mode `continual_safety_heads`
  full-history** replay (the only growing-buffer reference) bit-for-bit; **plus a finite-cap behavioral guard** (red-team
  C5) — `StreamingLUT(cap=k, policy=recency)` holds exactly the last-`k` prototypes (a deterministic FIFO-contents check, so
  the eviction machinery is verified live, not only at the degenerate cap=∞).
- **Read-side calibration (conditional):** the residual **must be injected with the Phase-6 `NoiseModel` input-transducer
  directional channel** (from `p6lib` — the channel SCFF's per-sample norm *cannot* remove forward-only), **not** P8's
  `nuisance_transform` (layernorm-invariant *by construction* — SCFF removes it → a vacuous probe, the P8 C3 trap).
  `residual_probe` measures the earn-its-place dent. **Primary defense `proto_reanchor(...)`** (re-forward the raw LUT
  through the current bulk under the shift → drift-free shift-consistent prototypes — the plan's own sleep mechanism, =
  test-time prototype shift [2403.12952], no covariance estimate; lit A1); **fallback `slda_readside_refit(...)`** (re-
  estimate SLDA class means / shared covariance at sleep on the shifted read, with a **shrinkage / min-count guard** — SLDA
  covariance is unstable under the bursty few-shot classes, lit C5; scalar TS is diagnostic-only). Only built if P9.4's gate
  probe fires.
- **Guards (run FIRST):** all P8 guards + `n2_readside_guard` (incl. the LLRD representation check) + `evict_equiv_guard`
  (incl. the finite-cap FIFO check). **Any guard fails → STOP.**

**Apparatus discipline (carry P8 verbatim):** `manifest.json` (git hash + config + seeds + versions + wall-clock + the
meter's per-op energy params & citations) + `arrays.npz`; `plot_p9.py regen <run-dir>` redraws every figure from saved
data; `_ckpt.jsonl` fsync'd. `OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`, **verify the PID alive on heavy
live cells** (the phantom-hang bug). **CPU float64** (the bit-exact guards need determinism). **No sklearn / no River for
compute.** Commit per-rung on `main` (`feat(draft6/phase9): …`), end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

---

## 7 · Owed decision-record deltas (flag at close; never retro-edit frozen arch files)

To record in [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) the way S10–S12 were banked at their phase close
— **flagged here, not silently applied:**

- **N2** (EMA-view / drift-slowdown) → **resolved**: standby → **default** (the committed form, if P9.1 adopts) or
  **struck** (if it doesn't); the P8 cadence's drift-conditionality discharges here.
- **S7** (sleep) → **extended** with the readout-aware consolidation *depth* (P9.2 adds *what*, to P8's *how often*).
- **The bulk-drift assumption** → **measured** (P9.0), discharging the "assumes the bulk doesn't forget" caveat the whole
  cheap-replay story rested on (or **overturning** it if the bulk forgets — a headline delta).
- **Eviction** → a **new supporting decision** (S13-candidate): the bounded-LUT policy that holds continual-safety under a
  bursty stream (+ the cap-vs-#classes scaling law).
- **The read-side noise residual** → **resolved or named** (P9.4): defended read-side, or handed to the analog layer.
- **The frozen object** → a **new supporting decision**: the complete committed neocortex loop, live-safe, **locked at a
  commit hash** — the Stage-2 maintenance close-out.

---

## 8 · The lab-manager review ledger (3-agent pre-run review — FOLDED 2026-07-02)

Three cold-start reviewers (repo-fit · red-team · literature). Verdicts: **READY-WITH-FIXES · SOUND-WITH-FIXES ·
SOUND-WITH-ADDITIONS.** Three findings **converged** across independent reviewers (⊕) — the strongest signal they are real.
All folded above:

| # | source | finding | resolution |
| --- | --- | --- | --- |
| B1 ⊕ | red-team + repo-fit + lit | the P9.0 **frozen linear probe is basis-dependent** — a pure rotation tanks it and reads as forgetting; and `linear_probe` returns no reusable `W` | **three curves** (§2.3/§3/§4/§6 `probe_retention`): cosine (rotation) · fit-once frozen (staleness) · **re-fit optimal probe** (destruction — the verdict curve, 2203.13381) |
| B2 ⊕ | repo-fit + red-team + lit | **LLRD-rate** is not honestly "rate-only" (changes the representation), needs a subclass (no per-layer lr), and is a looser analogy than EMA-view; the guard checked config scalars only | **EMA-view = the doubly-grounded in-scope default**; LLRD-rate a **flagged secondary** (`LLRDCell` subclass, objective byte-identical), guarded **representation-level** (early/mid taps unmoved, else Stage-1-reopen) |
| B3 ⊕ | repo-fit + red-team | P9.3 assumes a **P8 "full replay history" that doesn't exist** — streaming sleep uses a fixed 600-item balanced probe; the `cap=∞` guard was unimplementable/vacuous | build an **accumulating `StreamingLUT`**; oracle = it at cap=∞ ≡ the **block-mode full-history** buffer bit-for-bit; **+ a finite-cap FIFO behavioral guard** |
| B4 | red-team | the P9.5 freeze cut cited an **unpinned "sum-of-components promise"** | pinned to **P8.6 committed-loop live AA** — "P9 tuning did not cost accuracy vs the shipped object" |
| C1 | repo-fit | `bulk_drift` claimed a `p8lib` carry but is **not in `p8lib.__all__`** | import `bulk_drift`/`NoiseModel` **direct from `p6lib`** (+ the `../phase6` sys.path) |
| C2 | repo-fit | trunc/per-depth **cannot be re-sliced** from the all-tap `phi_probe` | cache **per-layer `reps_probe`** at grid steps |
| C3 | repo-fit | `sleep_cost` meter prices the **full-depth re-forward** regardless of read depth | price the **actual forward depth per arm** (trunc = shorter forward; else only the `Fdim` solve term saves) |
| C4 | red-team | herding null **too weak to fail** if raw features are unimodal (vacuous demonstration) | pre-register the informative condition; if within δ_acc of CBRS report **"buffer-spine null here"**, not a spine win |
| C5 | red-team | "one variable per rung" quietly broken (P9.2 depth+freq; P9.3 policy+cap) | frequency re-confirm + cap-scaling run as **separate sub-tables**; primary verdict can't cite a co-varied cell |
| C6 | red-team | P9.4 could **pre-contaminate P10's noise showcase** | P9.4 tunes on the home residual only; **P10 uses a held-out noise battery** |
| C7 | red-team | eviction **cap never pinned** — could be set so large the bound never bites | **pin the cap at a pressure point** (oracle-BWT onset / 1–3 exemplars/class) |
| C8 | red-team | freeze manifest didn't enumerate the **conditional knobs resolved off** | manifest lists every knob incl. `N2: struck` / `residual: skipped` |
| A1 | lit | a **cheaper/cleaner P9.4 defense** exists — prototype re-anchoring via the raw LUT (the plan's own sleep mechanism) | `proto_reanchor` = primary; SLDA covariance-refit = fallback |
| A2 | lit | **SLDA covariance unstable** under bursty few-shot classes | **shrinkage / min-count guard** on `slda_readside_refit` |
| A3 | lit | **D-CBRS uses K-means** → the sklearn/OpenMP phantom-hang on this box | hand-rolled **single-threaded** diversity scorer, no sklearn |
| A4 | lit | 2311.13321 is **more anti-SSL** than stated → the "bulk forgets" fork is likelier | P9.0 tone: budget for the degrade branch, don't default to rotation-only |
| A5 | lit | **T-CIL = 2503.22163**; calibrates without an old-task val set (a live option, not just a foil) | id added; kept as a live margin-calibration option |

**Not changed (checked, defended):** the vacuous-nuisance-injector guard (P9.4 mandates the Phase-6 `NoiseModel` channel);
GSS dropped (gradient-free); the internal-signals-only freeze discipline (pinned in every cut); the magnitude-as-signal
spine (herding / EMA-view / calibration all routed through direction). The literature reviewer verified **every**
load-bearing citation (LDC, SDC, Latent Replay, CBRS, herding, momentum-encoder, TS-under-shift, D-CBRS, T-CIL, DATS,
REMIND) as **correct** — no blocker-grade misuse.

---

## Grounding (what the field does — and what we adopt)

- **Maintenance = replay** (Rolnick [1811.11682]; A-GEM [1812.00420] = the P10 fair baseline; **REMIND** = the
  frozen-backbone *anti-pattern*; iCaRL/GDumb raw-exemplar replay = our sleep) → [`maintenance-and-replay`](../../research/papers/phase9/maintenance-and-replay.md).
- **Does the unsupervised bulk forget?** — continuous SSL *does* forget (ECCV'22; 2311.13321); CaSSLe [2112.04215] the
  optimistic pole; drift is measurable [2203.13381] → P9.0 ([`deep-research-delta`](../../research/papers/phase9/deep-research-delta.md) D0).
- **Slow coordination = EMA / momentum / stop-gradient** (2208.05744 — EMA matters at *late* layers = the N2 flip;
  Lookahead [1907.08610] = the fast/slow inside the readout) → [`slow-coordination`](../../research/papers/phase9/slow-coordination.md).
  **Drift compensation** (SDC [2004.00440] → **LDC** [2407.08536], unsupervised-capable, exemplar-free) = the road-not-taken (D1).
- **Consolidation depth = Latent Replay** [1912.01100] (replay-layer selection; slow below, learn above) + Layerwise
  Proximal Replay [2402.09542] → P9.2 (D2).
- **Bounded buffer = CBRS** (Chrysakis & Moens ICML'20) > GSS [1903.08671] (gradient-based, dropped); **herding** (iCaRL)
  = the mean/magnitude null; **D-CBRS** [2207.05897] the diversity refinement; small-buffer selection [2407.00673] → P9.3 (D3).
- **Read-side calibration** — plain TS ineffective under shift; T-CIL (CVPR'25) / DATS [2509.21161] the CIL-calibration SOTA;
  feature-level prototype shift [2403.12952] → P9.4 (D4). Spine: direction-grounded, TENT-entropy cautioned [2006.10726].
- **North-star hand-off** (PonderNet [2107.05407] the un-looped gate; the cosine margin the "feeling") — a **tie-break
  bias**, not scope → [`north-star-bridges`](../../research/papers/phase9/north-star-bridges.md).
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 discipline — carried from Phases 1–8
  ([`../result-format.md`](../result-format.md)).

> The **floor**, per [`../result-format.md`](../result-format.md) + [`result-format.md`](result-format.md): median + IQR,
> 5 seeds, reference lines (chance, ceiling, oracle/frozen), a caption ending in the takeaway, a manifest that regenerates
> every figure. A rung that fails is a card with its mechanism — a result, logged and moved past. **Build, then freeze.**

*Up:* [Stage-2 map](../stage2-design.md) · *prev:* [Phase 8 — the economy](../phase8/README.md) · *next:* [Phase 10 —
the validation / the showcase](../phase10/design.md).
