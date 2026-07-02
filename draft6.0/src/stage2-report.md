# Stage 2 — the GD namer: putting our names on the cheap brain (the report)

> The executive narrative of Stage 2 of draft 6.0 (Phases 7–10, July 2026) — the arc that takes the frozen, noise-hardened
> SCFF cheap brain and builds the **~20% gradient-descent "namer"** that maps its features to our labels. Stage 1 made a
> brain that *organizes* the world; Stage 2 makes it *answer in our language.* This is the last component of the
> neocortex brain.
>
> **⚠ This is a LIVING report — Stage 2 is IN PROGRESS.** Of its four phases (re-planned 2026-07-02 into *freeze in P9,
> judge in P10*), **P7 (the readout), P8 (economy + cost), and P9 (maintenance — the loop now FROZEN) are DONE (all
> 2026-07-02)**; **P10 (validation / showcase) is the live line, not yet run.** The headline results are real and, for P7,
> natural-confirmed; P8 put the first honest hardware cost on the 80/20 and ran both brains live; P9 measured the
> bulk-drift (it **rotates**, does not forget), tuned the loop's open knobs, and **locked the object** at a commit hash.
> But the stage's *existential* test — the fair same-budget BP+replay **accuracy** baseline (plus natural multi-class
> **A5** and the multi-domain gauntlet) — moved to **P10** (the re-plan; P8 settled the *energy* comparison, not the
> accuracy fight; §6) and is **still owed**. Read this as "the arc so far," not "closed."
>
> The plan this executes: [`stage2-design.md`](stage2-design.md) (the authoritative Stage-2 map). The frozen cell it
> builds on: [`phase6-final-architecture.md`](phase6-final-architecture.md). The
> committed design record: [`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md). Terms and metrics:
> [`ref-report/`](ref-report/README.md). The Stage-1 arc it inherits: [`stage1-report.md`](stage1-report.md).

---

## 1 · What Stage 2 is — the one-page primer

Draft 6.0 is two brains on one analog substrate. A cheap, unsupervised **SCFF cortex** (~80%) organizes the world for
free — label-free, local, forward-only. Stage 1 built, characterized, closed out, and noise-hardened it: the committed
cell is **`NoiseAugContrast`** (`SCFFContrastOverlap` temp0.2 / w2, L12 bulk, no residual, + one iid-noise-augmented
InfoNCE view). It composes the depth a task needs, reads it cheaply, wins the continual regime, and survives the noise it
will meet on silicon. **But it never learned our labels.** It sorts the world into "kinds of things"; it does not know
which kind is a *3* and which is a *7*.

**Stage 2 is the part that does — the precise ~20% gradient-descent namer, read-only on the frozen bulk.** Every knob
from here on is on this back, not the SCFF front (which is frozen and never re-trained). The split is the project's
founding bet: **direction is the one expensive thing in learning**, so we pay for it *once*, where it counts — putting
the names on — and get everything else for free.

**Why Stage 2 is smaller than five-phases-of-SCFF had any right to be.** Because the SCFF bulk is *frozen to GD*, the
namer's learning is **reservoir/ELM-like** — a trained readout on fixed features is a **(near-)convex regression** with
no bad local minima and no cross-layer credit chain. There is no heavy-optimizer zoo to build; the simplest thing
converges. Two hedges keep "small" from becoming "sloppy," and both are *tested*, not asserted: **(a)** "convex" names the
*regression*, not the deployed readout's **substrate cost** (the softmax / normalizer / Gram-solve is a non-free digital
block — that is Phase 8's meter, so every "80/20" number is a proxy until then); **(b)** we are reservoir-*like*, not a
reservoir proper (trained-then-frozen, not random), so we inherit the readout convexity but **not** free noise-tolerance,
and the real cost is *tracking the drift*, not solving the regression.

**One kickoff decision governs the whole stage: boosting is dead.** The old N3 plan chained `[SCFF → GD-checkpoint]`
residual boosting blocks; it is dropped. A boosting *chain* feeds each block's fast, supervised, GD-corrected residual
into the *next* block's SCFF input — SCFF sees a moving target and its stable unsupervised base is destroyed. The wall,
now across all of Stage 2: **anything between or under SCFF must be unsupervised, or slow enough not to shift everything
at once; fast + supervised + upstream-of-SCFF breaks the base.** So the committed era is **one L12 SCFF bulk + read-only
GD heads** — the "two GD organs" collapse to **one: the readout.**

**The four phases** (re-planned 2026-07-02 post-P8 — the old single "P9 maintenance + owed baselines" split into P9
*close* + P10 *validate*; run in order on the noise-hardened cell):

- **P7 — the readout.** Build and pick the namer on the frozen bulk. **✓ DONE.**
- **P8 — the economy gate + the cost meter.** The Ch7 learning-gate (cheap SCFF most steps, expensive GD only when the
  cheap path stalls) and the honest hardware-meaningful cost meter that replaces the op-count proxy. **✓ DONE.**
- **P9 — close & *freeze* the maintenance loop.** Tuned the genuinely-open knobs against *internal* signals — bulk-drift
  (rotates, doesn't forget), N2 (struck), cadence *depth* (all-tap) + frequency (grid-8→grid-4), bounded-LUT eviction
  (CBRS), the read-side noise residual (proto-reanchor) — then **locked the object**. **NOT** re-opening the Namer (SLDA
  committed). **✓ DONE — frozen.**
- **P10 — the validation / showcase.** Race the **frozen** object: the existential fair BP+replay *accuracy* fight, the
  multi-domain adaptive gauntlet (new/1-back/all-prev acc + cost), the noise showcase, natural multi-class A5 → an honest
  **Pareto** verdict + the Stage-2 close-out. Discipline: **freeze in P9, judge in P10.** *Next (live).*

---

## 2 · The arc so far — one thread, still running

Stage 1's arc was "we kept being right about *where* the cell wins and wrong about *how*." Stage 2 has its own thread,
and two phases in, it has a shape:

> **The "20% GD" is a role, not a method — and the economy that pays for it is a *safety* mechanism, not just a cost
> saver.** We expected to pay gradient descent for the precise brain and to pay a forgetting cost to stay direction-pure.
> The sims said neither: the best namer uses **no gradient at all** and wins by reading a *magnitude*; and when we ran
> both brains live, the disciplined drift-gated economy turned out **cheaper *and* safer** than firing the namer every
> step — because firing more chases the recency-skewed stream and forgets more. The cheap answer was also the safe one.

The connective tissue is Stage 1's recurring fault, **density ≠ class**, wearing its **7th** coat. The project's spine
says *read the class direction, never a magnitude* — and the tempting move in a readout is to declare the direction-pure
**cosine** head "the spine handed to us." Phase 7 measured it instead of assuming it, and the answer was sharp: on the
frozen bulk the cosine head is **sub-competitive**, and the committed namer (**RanPAC**) reads a *magnitude* (a ridge
prototype) — yet it is **recency-robust**, not because it reads direction, but because it has **no trained softmax
weights to inflate.** Recency-robustness ≠ direction-reading. The spine bent, honestly and numerically, and we named the
tension rather than resolving it silently toward accuracy.

**The honest status, stated up front.** Two phases of three are done. The headline — *the precise brain names the world
with no backward pass* — is a real, natural-confirmed **P7** result on the frozen bulk; and **P8** ran both brains live,
metered the 80/20 for the first time (GD-share 0.121, no longer a proxy), and showed the loop is continual-safe live.
But the architecture's *founding* claim (an 80/20 continual learner that beats backprop's **economics *and* accuracy**)
is **not** yet fully re-validated: P8 settled the *energy* comparison (OURS ≈ half of BP+replay), but the fair same-budget
**BP+replay accuracy** baseline is P9's job and is **still owed**. Stage 2 is going well; it is not finished.

---

## 3 · Phase by phase (the synthesis)

### Phase 7 — the readout → *the 20% is NOT gradient descent* 🔥  **[DONE]**

Phase 7 raced a taxonomy of *namers* on the frozen bulk — gradient heads, direction-pure cosine heads, magnitude
prototypes, and no-gradient analytic/RLS heads — refereed by three axes: **accuracy × forgetting (BWT)**, the **spine**
(does the verdict track class *direction* or a *magnitude*, measured as argmax-flip under a per-class norm nuisance), and
the un-skippable **A6 continual-safety gate**. Cost was a descriptive-only fourth axis (never a tie-break; the real meter
is P8).

![Phase 7 in one figure — the bake-off frontier](phase7/exp1/figs_p7_1/BAKEOFF.png)
*The headline. **Left** — the accuracy×forgetting frontier: **RanPAC** sits at the top-right, in a statistical three-way
tie with the gradient MLP and the un-projected RLS, and **two of the top three use no gradient**; the direction-pure
cosine-softmax and the max-magnitude FeCAM fall below, and the bare prototype heads collapse sub-floor (greyed).
**Right** — the scorecard: RanPAC carries the highest static accuracy, while only the two **cosine** heads are perfectly
spine-clean (argmax-flip 0). The whole phase is this one picture: the frontier peaks *off* the direction-pure corner — so
the spine bends — but it bends toward a no-gradient winner.*

**The committed namer is RanPAC** — a closed-form analytic head (a frozen random ReLU projection → a running-Gram ridge
prototype `W = (G+λI)⁻¹M`, no gradient, streaming) shipped with a **class-balanced-reservoir imbalance guard**. On the
continual home it ties the gradient MLP on accuracy×BWT (a 3-way tie with SLDA, AA 0.617 / 0.623 / 0.604, mutually
within-noise), has the highest static accuracy (0.647), **passes the A6 gate** (BWT +0.023 vs the floor-head baseline,
0/5 seeds negative), and is **#1 on natural digits** (AA 0.949, near-zero forgetting). Because two of the tied top three
are no-gradient, **the precise 20% brain names the world with no backward pass at all** — the "20% GD" is a role, not a
method.

**The spine bends — numerically, and less than feared.** Only the cosine head is direction-pure (argmax-flip **0.000**),
but it is sub-competitive where the bulk has structure to exploit: on the synthetic home it trails the magnitude frontier
by **Δ = 0.128** (real, 5/5, ≫ δ=0.02) → *magnitude-wins-spine-bends*. The gate makes the mechanism empirical: the
no-gradient cosine-ncm **passes** while the trained cosine-softmax — *same angle metric* — is **struck** (5/5), so the
forgetting comes from the **trained weights**, not the readout's geometry. The winner reads a magnitude yet is
recency-robust for exactly that reason. And the price **shrinks 4× on natural digits (−0.036) and vanishes on CIFAR-flat**
(where the bulk itself has no composable depth and every head collapses to ~0.3).

**Two design guesses the sims overturned** (the honest science): **(1)** the imbalance guard is **class-balanced
reservoir (cbrs, buffer-side), not AIR** — the analytic head-side guard the plan expected *over-corrects* (it crushes
recent classes); re-balancing the input beats re-weighting the output (RanPAC's bursty recency-gap +0.495 → +0.013).
**(2)** the "multimodality cliff" is **anisotropy, not multimodality** — natural per-class features are unimodal
(n-modes 1.0); the accuracy lever is a **tied covariance** (NCM 0.754 → SLDA 0.946, +0.19), closed-form, no non-convex
mixture needed (a mixture *hurts*). Both hedges from §1 held: the naming was convex-easy, and the RanDumb skeptic control
confirmed the trained bulk earns its keep vs a raw-pixel random projection (though a random *expansion of its own taps*
ties a plain linear namer — the expected ELM effect — a flag carried forward). → [full Phase 7 report](phase7/phase7-report.md).

### Phase 8 — the economy gate + the cost meter → *the two-brain economy is real, cheaper and safer, run live* 🔥  **[DONE]**

Phase 7 picked *what* the namer is; Phase 8 turned **both brains on together for the first time** and answered *when* it
fires and *what it truly costs.* SCFF was run **live** (forward-only on every input; it never forgets but its feature map
drifts), and the namer tracked that drift through an awake gate + periodic sleep — on a new streaming **`partial_fit`**
primitive (a running Gram, guarded ≡ a batch fit to 4e-15). The bake-off settled every knob: the awake gate is **DDM**
(two-threshold error, FAR 0.000, fires ~0.3% of steps); the trigger is a **label-free class-direction tap-drift** signal
that leads the error by ~8 steps (MTD 6 vs 14) while a magnitude-of-shift null false-fires on 94% of nuisance steps — the
spine, made a measurement; the sleep cadence is **grid-8 / full LUT history** (regular cadence beats boundary-aligned;
full history is load-bearing). The honest ADC-centred meter priced the ~200× Phase-7 caveat: **SLDA names 69× cheaper**
than RanPAC and, freshly measured live, ties or beats its accuracy — **commit SLDA** (RanPAC kept as the reference).

![Phase 8 in one figure — the live economy is cheaper and safer](phase8/exp6/figs_p8_6/CONT_SAFETY.png)
*The headline. The committed drift-gated economy holds worst-point (pre-sleep) BWT at **0.000** — identical to the
known-boundary oracle — in 5/5 seeds at **GD-share 0.155**, while the profligate **always-pay** loop (namer every step)
**forgets** (worst-BWT −0.137) at **GD-share 0.747**. Firing more chases the recency-skewed stream and forgets more, so
the gate is a **safety mechanism**, not just a cost saver — the disciplined economy is cheaper *and* safer.*

The metered 80/20 is finally a hardware number, not a proxy: with the gate on the GD namer is **12.1% of total substrate
energy** (GD-share 0.121 ≤ 0.25); turn the gate off and it balloons to 77.8% — the gate *creates* the split. Against a
fair BP+replay learner at matched retention on the same substrate table, **OURS draws ~half the energy** (bp_ratio
0.501). And the loop is **LIVE-SAFE** — the co-adapting system keeps the A6 continual win at the awake gate's worst point
(the honest read; post-sleep would hide it). Two design guesses the sims overturned: the gate's value is **safety, not
just cost** (more GD forgets more), and **regular cadence beats boundary-aligned sleep** (the worst mid-stream point
falls inside a segment, not at a boundary). The live-vs-frozen accuracy gap (0.447 vs the 0.614 block-mode promise) is
**task difficulty**, not forgetting (worst-BWT 0.000) — the natural multi-class number (A5) and the fair BP+replay
*accuracy* fight are **Phase 10's** (the re-plan; P9 froze the loop). → [full Phase 8 report](phase8/phase8-report.md).

**Why analog (P8.7 extension — the substrate ablation for the professor brief).** The bp_ratio above compares OURS to
BP+replay on the *same analog* table — the *algorithm* win. P8.7 adds the substrate axis: re-meter the exact committed
loop and the same fair baseline on a **digital** (von-Neumann / GPU-class) substrate (no ADC, digital 8-bit MACs
Horowitz-anchored, matched precision) → the full **2×2 {OURS, GD+replay} × {analog, digital}**. The chip (OURS-analog,
3.4e7 pJ) is **15.4× cheaper** than the conventional baseline (GD-on-digital, 5.2e8 pJ), and the win factors cleanly:
**5.4× is the analog substrate** (compute-in-memory — the ~8e8 SCFF MACs are near-free in the crossbar, while a digital
machine pays the memory wall on every one, and there are ~75× more MACs than ADC reads) **× 2.9× is the 80/20 algorithm**
(our gated forward-only loop vs BP+replay on the *same* digital substrate). The 80/20 is **substrate-independent**
(GD-share 0.11–0.16 on either), and the analog advantage is a **conservative floor** — ≥2.7× even at the most-generous
arithmetic-only digital, growing past 50× once the memory wall is counted. → [Phase 8 report §7](phase8/phase8-report.md).

### Phase 9 — close & *freeze* the maintenance loop  **[DONE — the loop is frozen]**

Phase 9 tuned the five still-open knobs of the lifelong maintenance loop against *internal* signals, then **locked the
object** (a commit hash) so Phase 10 can race it fairly — the re-plan's discipline: *freeze in P9, judge in P10.* It ran
the deferred **bulk-drift** measurement the "the bulk doesn't forget" cheapness assumes and found the bulk **rotates but
does not forget** (an optimal probe re-fit on the current bulk holds ≥ its birth score on held-out early-task data
throughout — Davari 2203.13381, rotation factored out; N2 therefore *not mandatory*). Four knobs kept the committed loop —
**N2 struck**, **all-tap** consolidation, **CBRS** eviction (the guard Phase 7 already committed, now confirmed
best-bounded under a bursty, class-imbalanced *bounded* buffer — it ties the herding buffer-spine null and beats
iid/FIFO), **proto-reanchor** for the Phase-6 read-side residual (retention 0.79→0.99) — and the freeze caught the one
real gap: the P8 **grid-8** sleep cadence, tuned on a single pass, was too sparse for a lifelong revisit stream (worst-BWT
−0.317, failed the oracle-veto 2/5); the freeze-driven cadence re-confirm → **grid-4** restores near-flat
continual-safety (worst-BWT **−0.028**, ties the oracle 0/5, at held AA and metered GD-share 0.178 ≤ 0.25). Delta **S13**;
the object is locked for Phase 10. → [Phase 9 report](phase9/phase9-report.md).

### Phase 10 — the validation / showcase → *the honest fights Stage 1 deferred*  **[LAST — not run]**

Phase 10 races the **frozen** object (it touches no knob) and settles the debts. The load-bearing one is **existential**:
Phase 4's continual WIN was measured vs *naive* online-backprop-without-replay — not a fair fight. Phase 10 owes **OURS vs
`race_bp` + a replay buffer (A-GEM-style) at matched buffer and compute.** We may still win — only the readout replays,
and the bulk doesn't forget (P9.0 measured it) — but we have to *show* it, and this is where the architecture's headline
claim gets its honest test. Phase 10 also closes Phase 4's owed **A5** (multi-class on natural digits/CIFAR on the
continual-stream harness — synthetic overstates the static gap), runs the **multi-domain adaptive gauntlet**
(new/1-back/all-prev acc + cost — the money figure), and the **noise showcase** on a **held-out** battery (P9.4 tuned only
on the home residual). Deliverable: an honest **Pareto** verdict + the Stage-2 close-out.

---

## 4 · The decision record (what Stage 2 has set, and what it owes)

The Stage-2 spine was sketched in [`stage2-design.md`](stage2-design.md); Phase 7's results banked the first deltas to
[`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md). Flagged, never silently applied, and never retro-editing the
frozen architecture snapshots.

| Decision / knob | Committed as | Set / owed by | Now |
| --- | --- | --- | --- |
| GD = residual boosting blocks | **N3** | superseded at P7 close | _**S11**: "single frozen bulk + read-only namer" — boosting dropped (the forward-leak wall)_ |
| Two GD organs (interface / output) | **S4** | collapsed at P7 close | _**S11**: collapses to **one** — the namer (Interface-GD retired with the blocks)_ |
| Readout = fixed short-stack placement | **S9** | extended at P7 close | _**S11**: extended with the committed *head* (**RanPAC**, analytic), not just the placement_ |
| The namer is a *method* (gradient descent) | — (implicit) | overturned at P7 | _**S11 new supporting decision**: the namer is a **closed-form/streaming analytic head** — "20% GD" is a role, not a method_ |
| Threshold-gated learning (Ch7 gate) | **S6** | **resolved at P8 close** | _**S12**: the awake gate is **DDM** on a **class-direction tap-drift** trigger (magnitude-of-shift is the false-fire null)_ |
| The committed head's cost | **S11 caveat** | **resolved at P8 close** | _**S12**: metered E-ratio 69× → **commit SLDA** as the deployed namer (RanPAC kept as the accuracy/spine reference)_ |
| Sleep consolidation cadence | **S7** | **extended at P8 close** | _**S12**: **grid-8 / full LUT history / λ_ema 1.0** detector-driven cadence (was oracle-boundary); drift-rate-conditional_ |
| The "80/20" cost number | proxy (Stage-1) | **metered at P8 close** | _**S12**: real — GD-share **0.121** with the gate on (0.778 off); replaces the proxy tag; bp_ratio 0.501 vs BP+replay_ |
| Why analog (substrate vs algorithm) | unquantified | **decomposed at P8.7** | _**S12 note**: the chip is **15.4× cheaper** than conventional GD-on-digital = **5.4× substrate (CIM)** × **2.9× algorithm (80/20)**; analog advantage is a floor (behavioral, Horowitz-anchored)_ |
| The live two-brain loop is continual-safe | — (untested) | **set at P8 close** | _**S12 new supporting decision**: LIVE-SAFE (worst-BWT 0.000, 0/5 regress); the gate is a **safety** mechanism (more GD forgets more)_ |
| EMA-view slow coordination | **N2** | **owed → Phase 9** | _a *proposed* promotion (standby → default) pending the P9 sim; the P8 cadence is conditional on it — not yet_ |
| SCFF carries a noise-aware objective | **S10** | Phase 6 (Stage-1 ext) | _done — the frozen cell already carries it_ |

---

## 5 · The namer as it stands (end of Phase 7)

The committed namer is **RanPAC + a class-balanced-reservoir guard** — a frozen random ReLU projection φ = relu(Wr·f) → a
running-Gram ridge prototype, no gradient, streaming, A6-safe. Its value **tracks the bulk's**: it wins where SCFF
composes class structure (the synthetic tie, digits #1) and is idle where SCFF has no depth (CIFAR-flat, where all heads
collapse to ~0.3 and the cheaper SLDA edges it). What Phase 8/9 inherit:

- **The cost trade (Phase 8's call).** RanPAC's projection cost proxy is ~200× SLDA's. **SLDA is a within-noise, far
  cheaper no-gradient alternative** that also passes the A6 gate and is *more robust on depth-less inputs* — so if the
  substrate meter makes RanPAC's projection prohibitive, **SLDA is the committed fallback** (its only cost is
  spine-cleanliness: argmax-flip 0.89 vs RanPAC 0.54).
- **The imbalance guard to carry:** class-balanced reservoir sampling (buffer-side, family-agnostic). AIR is
  available-but-not-shipped (over-corrects).
- **The read-side noise residual (owed from Phase 6, deferred through Phase 7 on purpose):** the input-transducer
  directional channel + ADC < ~3-bit — a calibration-under-shift defence a *chosen* head adds on top of itself. Now that
  the head is chosen (RanPAC / SLDA), Phase 8/9 can address it read-side (LP-FT: a frozen head can't manufacture *base*
  robustness, but it can defend a channel the base can't reach forward-only).
- **The RanDumb flag (not benign):** on the *flat* home a plain linear namer gains ~nothing from the trained taps over a
  random expansion of them (the ELM effect) — verified value for the ridge/analytic namer, a tie for a linear one. The
  bulk's naming-stage value on the flat home is thus head-dependent, handed forward as a flag, not a footnote.

---

## 6 · Honest scope of Stage 2 so far

- **Three phases of four are done.** P7 (the readout) is complete and natural-confirmed; P8 (economy + cost) ran both
  brains live, metered the 80/20, and confirmed live continual-safety; P9 (maintenance) measured the bulk-drift, tuned the
  loop's open knobs, and **froze the object**. P10 (validation / showcase) is the live line, not run. This report is a
  *living* document; the stage is not closed.
- **The existential *accuracy* test is still owed — now Phase 10's.** The architecture's headline continual claim rests
  on a fair same-budget **BP+replay accuracy** baseline that the re-plan made **Phase 10's** deliverable (freeze in P9,
  judge in P10). P8 settled the *energy* comparison (OURS ≈ half of BP+replay, bp_ratio 0.501), and Phase 4's WIN was vs
  *naive* online-BP; until P10 runs the fair *accuracy* fight, the 80/20 continual claim is *supported but not fully
  validated in Stage 2.* We say so on purpose.
- **The cost claim is now metered (no longer a proxy) — as a behavioral number.** P8's ADC-centred meter gives GD-share
  0.121 and bp_ratio 0.501, replacing Phase 7's op-count proxy. It is a **behavioral** macro-model (relative-pJ,
  NeuroSim / ISAAC / PUMA level, params + citations logged), not SPICE — the absolute-Joule and PVT layer is later.
- **Behavioral simulation only** — numpy ideal floats plus Phase 6's behavioral analog-noise model; no SPICE, no device
  physics, no fabrication.
- **Small, partly synthetic tasks** — the continual home, digits, CIFAR-flat. The P8 economy is measured on the
  synthetic CI+nuisance stream; absolute live AA there is modest (0.447; the gap to the 0.614 block-mode promise is task
  difficulty, not forgetting). The natural multi-class number (A5) is Phase 10's.
- **The maintenance loop is now built and frozen; the honest baselines remain (P10).** The readout-aware cadence,
  eviction, and the read-side residual are tuned and the loop is locked (P9). What is committed now is the *readout
  family* (P7) + the *economy* (P8: gate, trigger, cadence, deployed head, meter) + the *frozen neocortex maintenance
  loop* (P9); still owed is its honest same-budget accuracy baseline (P10).

---

## 7 · The north-star hand-off (threaded, not a phase)

Stage 2 touches the north star — the recurrent, lifelong-learning prefrontal↔hippocampus loop where *correctness is a
self-generated feeling* — only as a **tie-break bias**, so the later brain can reuse Stage-2 signals instead of tearing
them out. The design's seed was: the gate is the *halt*, and the readout's **cosine margin** (a direction, not a
confidence or distance magnitude) is *the feeling.* Phase 7 sharpened this honestly. The committed namer (RanPAC) reads a
**magnitude**, and the direction-pure cosine head turned out sub-competitive as a *classifier* — so the "feeling" is **not**
the deployed head. But the cosine margin survives as an **available, perfectly spine-clean direction signal** (argmax-flip
0), decoupled from the classifier: the recurrent brain can read the *angle* for its self-generated confidence even while
the *names* come from the magnitude head. The gate half of the seed was carried into Phase 8 and
**built exactly that way**: the committed trigger is a **class-direction tap-drift** signal, never a confidence magnitude
(why P5 struck the adaptive exit) — a confidence gate would be torn out later; the direction gate is the seed, and the
sims confirmed it both *leads* the error and stays invariant to nuisance while the magnitude null false-fires. Light
touch, held to a tie-break — **simple intelligence first.**

---

## 8 · What's next

Phase 9 is done: the maintenance loop is tuned against internal signals and **frozen** — the bulk was measured to
*rotate, not forget*, four knobs kept the committed loop (N2 struck, all-tap, CBRS, proto-reanchor), and the freeze
re-confirmed the sleep cadence (grid-8 → grid-4) to restore near-flat continual-safety on a lifelong revisit stream.
**Phase 10 — the validation / showcase — is now the live line**, and it carries the stage's *existential* test: the fair
same-budget **BP+replay accuracy** baseline that gives the architecture's headline its honest fight (P8 settled the energy
half; P10 owes the accuracy half). Phase 10 also closes the owed natural multi-class number (A5) on the continual harness,
runs the multi-domain adaptive gauntlet, and the noise showcase on a **held-out** battery — racing the **frozen** object
(it touches no knob) → an honest **Pareto** verdict. When P10 closes, this report is rewritten as a Stage-2 *close-out*
(the way [`stage1-report.md`](stage1-report.md) closed Stage 1), and the neocortex brain — cheap unsupervised structure +
a precise continual-safe namer + a metered economy + a frozen lifelong maintenance loop — is done. After that, the
analog-realism layer (SPICE / PVT); and, beyond the numbered phases, the recurrent lifelong brain remains the north star.
*Simple intelligence first.*

---

## Reading guide

**If you read only one file for the model:** [`phase6-final-architecture.md`](phase6-final-architecture.md) — the
self-contained, noise-hardened account of the whole cell (the frozen bulk Stage 2 names). **For the plan Stage 2
executes:** [`stage2-design.md`](stage2-design.md) (the authoritative Stage-2 map). **For the result so far:** this file
(the arc) → [Phase 7 front door](phase7/README.md) →
[Phase 8 front door](phase8/README.md) → the `phaseN/phaseN-report.md` deep stories (every figure) →
`phaseN/RESULTS.md` (the scalar ledgers) → the `phaseN/expK/experiment-K.md` cards. Terms, metrics, and papers are
defined in [`ref-report/`](ref-report/README.md); the committed decisions in
[`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md).

*Prev:* [the Stage-1 arc](stage1-report.md) · *Up:* [draft 6.0 context](../CLAUDE.md) · *Next:* Phase 9 — the maintenance
loop + the owed BP+replay accuracy baseline (the live line).
