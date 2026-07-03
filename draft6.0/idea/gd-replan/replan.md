# The re-plan v2.2 — the depth-readout ladder (post 4-agent review + T0 + T3 cheap-credit ladder)

> **v2.2, 2026-06-29 — T3 RAN (the cheap-credit ladder + a deep-lit pass).** Results:
> [`t3-results.md`](t3-results.md); literature: [`lit-cheap-credit.md`](lit-cheap-credit.md). Two pre-registered,
> guard-checked experiments + a literature survey **reshaped T3 decisively:**
> - **🔥 The decisive cheap lever is OBJECTIVE SHARPNESS, not credit reach.** `temp 0.5→0.2` at the adopted depth-2
>   window reaches tail-L12 **0.539 / acc 0.550 ≈ the full-backprop ceiling (0.549 / 0.569)** at **1.9× cost vs 11×**.
>   The decay is, to first order, an objective-sharpness problem with a **free** fix → **T3.0 temperature is now the
>   PRIMARY cheap-depth lever and a near-term decision.**
> - **Overlapping windows → STRUCK** (clean 5-seed negative: lr-matched overlap *hurts* and costs more — credit-chain
>   *length* composes depth, not credit-path *multiplicity*).
> - **Naive top-down objective credit → STRUCK** (FD-gradient-verified; every λ>0 sits *below* λ=0 — a detached
>   reference imports the decayed top's badness). The genuine objective-side fix (2601.21683 update-alignment) is
>   subtler and **deferred — possibly unnecessary given temperature.**
> - **Wider window (w4) → demoted** to a bounded *backup* (real but cost-dominated by temperature).
> - **FTP / PEPITA → ruled out** (they rewrite the forward stream — verified, not incidental).
> - Locality dose-response **bulletproofed at 5 seeds + replicated on the flat task** (the owed T0.3 flat spot-check
>   is done). Changes marked **[T3]** below.
>
> **v2.1, 2026-06-28 — T0 RAN.** The two pre-decision controls executed (results:
> [`t0-results.md`](t0-results.md)) and **resolved the open forks**, so the ladder below is updated:
> **(T0.1)** the decay is **not** lr/passes under-training — but **objective temperature is a free lever** (temp
> 0.5→0.2 bought L4→L7 + tail +0.12); **(T0.2)** the ~5 ceiling is **LOCALITY-bound** (full e2e backprop on the same
> InfoNCE composes all 12 layers; local w2 caps ~5) → **Track C / global coordination is now MANDATORY for native
> depth (de-conditionalized), but must be a CHEAP approximation of global credit, never full backprop.** Net: native
> depth is **curable**, not just routable-around. Changes are marked **[T0]** below.
>
> **v2, 2026-06-28.** Rewritten after the four-Opus recheck. The authoritative reasoning for every change is in
> [`review-and-revisions.md`](review-and-revisions.md); this is the actionable ladder. **What changed from v1:**
> the Tunnel Effect is demoted to an analogy; ReZero defaults to **frozen** α (it has no valid training signal
> otherwise); **learned halting / PonderNet is CUT** (over-engineering / north-star leak) → calibrated threshold;
> T0 gains **three decisive controls** (locality, probe-capacity, natural-data) and a **truncation baseline**; T1 is
> **split** and must pass a **continual-workload cost + distribution-shift** bar; the **native goodness signal is
> rejected for placement** (density≠class) and **settling-time is parked for the north star.**
>
> Governs: *one thing per experiment · failures are data · architecture changes are decisions, not experiments.*
> Default budget: **~5 layers, ep=25 / lr=0.03, ≤40 min/run** (flexible where an experiment needs it — T0.1 and the
> continual tests will need more).

---

## The spine: preserve / read the class DIRECTION, never a magnitude

Every rung below obeys the one rule the review surfaced (the project's recurring lesson, 4th appearance):

> **The useful thing is the class DIRECTION (the manifold). Rank, variance, contrast-loudness, and goodness/energy
> are MAGNITUDES — symptoms, not the lever.** Read the class direction (head confidence), preserve the class
> direction (frozen residual / a class-subspace term), and never steer a fix by a magnitude proxy (don't read
> goodness, don't train α on local contrast, don't whiten to restore rank).

## The shape (v2.1 — post-T0)

```
 T0  settle the ground        ✅ DONE → decay is locality-bound, not under-training; temp is a free lever
 T1  readout redesign (MVP)   per-depth heads + calibrated exit         ◀ MINIMUM VIABLE (must beat truncation)
 T2  preservation (cond.)     FROZEN near-identity residual
 T3  cheap-credit ladder      ✅ RAN [T3] — lever is OBJECTIVE SHARPNESS (temp 0.5→0.2, FREE) ≈ e2e ceiling at
                                1.9× cost; w4 = bounded backup; overlap + naive top-down STRUCK; global-credit deferred
 T4  continual optimization   the old Phase-5 loop, now readout-aware
 T5  north star               where the CUT ideas come home (learned halting, settling-time)
```

Repo phase mapping: **Phase 5 = T0–T2 ("where to read") + the cheap-credit ladder T3 ("earn the depth cheaply"),
Phase 6 = T4 continual, Phase 7+ = analog realism → north star.** **[T0]** T3 moved from "conditional escape hatch"
to a **named, mandatory ladder** — because the locality control proved the depth is reachable and the only question
is how cheaply.

---

## TIER 0 — settle the ground ✅ **DONE (2026-06-28)** — *and it reshaped the ladder*

Results: [`t0-results.md`](t0-results.md) · figure `t0/figs_t0/T0_RESULTS.png` · script `t0/run_t0.py` (3 seeds,
L12/W64, headroom). **Both forks resolved:**

### T0.1 — depth-scaled-training grid → **decay is NOT lr/passes under-training; temperature IS a free lever** ✅
- **Ran:** `(lr {.01,.03,.10} × ep {25,75,150})` + contrast-strength controls (temp, mask), L12, per-layer probe.
- **Result:** 6× passes and 10× lr leave the peak at **L4** (tail +0.02 only) → the ceiling is **real under the
  training budget**, not an lr/passes artifact (the warm-up confound is settled). **BUT** sharper InfoNCE
  (**temp 0.5→0.2**) moved the peak **L4→L7**, tail **0.42→0.54**, acc **0.45→0.55** — *free, no architecture,
  forward-only.* **→ BANK: re-tune the adopted cell's temperature/mask (a cheap decision).**
- *Owed (not yet run):* extend to 5 seeds; the **flat + natural-data spot-check** (was T0.3's spot-check).

### T0.2 — locality control → **the ~5 ceiling is LOCALITY-bound** ✅ (the decisive result)
- **Ran (elegant):** the cell's `window` IS the local↔global axis — `window` ∈ {1, 2, 4, 12} on the *same* InfoNCE
  (`window=12` = one loss at the top, gradient through all 12 = full end-to-end backprop).
- **Result:** peak marches **monotonically deeper** with credit reach — w1→L3, w2→L4, w4→L7, **w12→L12 (slope
  +0.0136, no decay)**. The objective composes the *whole* stack under global credit; forward-only locality caps it
  ~5. **→ the bound is LOCALITY, not the objective/task → Track C (global coordination) is MANDATORY for native
  depth** (de-conditionalized). w1-trains-every-layer-and-still-decays rules out the trivial reading.
- **The crux:** w12 = the forbidden full backprop → it's the **diagnostic UPPER BOUND** (proof the depth is
  reachable), not a deployment. The native-depth game becomes **how cheaply we can approximate global credit** → the
  T3 cheap-credit ladder.

### T0.3 — probe-capacity + profiler + truncation baseline *(still owed — run next, with the flat/natural-data spot-check)*
- **Probe-capacity** *(NEW):* linear vs small-MLP probe per depth. If the MLP recovers "decayed" layers, the info
  is **rotated, not destroyed** → placement/whitening over objective surgery; if not, it's genuinely lost.
- **The profiler:** per-task per-layer probe-vs-depth → define readout placement = the probe peak / slope-flatten.
  **Validate it against the *actual* (nonlinear, multi-layer) readout** — a linear-probe peak need not be the
  readout's optimum. Sweep difficulty + class-count to confirm "peak rises with task complexity" on *our* cell.
  **Add a natural-data spot-check** (the decay diagnosis is all-synthetic; rule out a synthetic-task artifact).
- **The truncation baseline:** a stack built only to the profiled extractor depth + margin, read at the top. **This
  is the control every tier above must beat** — on a chip, fewer layers = fewer Scaps = cheaper silicon, so if
  nothing beats truncation on the continual workload, *ship the truncation.*

> **After T0** you know: whether the ceiling is training/objective/locality-bound, whether the info is lost or
> rotated, where the sweet spot is per task (on real data too), and the cost floor to beat. **No architecture
> touched. The problem may already be smaller.**

---

## TIER 1 — the readout redesign  ◀ MVP ("SCFF is done" — *if it beats truncation on the continual workload*)

Lives on the licensed GD side. **Split into two one-variable rungs** (methodological rule 1).

### T1.1 — per-depth deep-supervision heads vs all-tap *(accuracy/placement only, fixed full depth)*
- **Do:** a tiny local readout head at each SCFF depth (Mono-Forward-style projection → local CE). The one borrowed
  mechanism with a real forward-only precedent — pure `read`, per-sample, no batch stats.
- **Baseline = all-tap** (the thing it replaces). **Measure:** per-head accuracy reproduces the T0.3 profiler;
  placement accuracy vs all-tap. Decision: heads-at-each-depth as the readout base **iff** it matches all-tap's
  accuracy at lower cost.

### T1.2 — calibrated confidence early-exit *(cost only; on the continual workload)*
- **Do:** a **calibrated** confidence/entropy gate over the heads (CALM-style guarantee), exiting at the shallowest
  confident head. **Where-to-read = head class-confidence — NOT goodness/energy** (goodness is density; Phase 3
  demoted it). **Not** a learned halting policy (that's cut — see below).
- **Measure on the CONTINUAL workload, not i.i.d.:** expected SCFF-depth executed, accuracy retention, true
  expected-compute (heads + gate overhead included). Add an **oracle-exit upper bound** (best per-input layer — if
  the oracle gain is small, gating can't save us). Add a **distribution-shift stress test** (does placement/gate
  hold when the task distribution shifts — the regime we ship into?).
- **Decision point / STOPPING MARK ①:** T1 "restores the 80/20" **only if** expected-compute on the *continual*
  workload beats all-tap *and* beats the truncation baseline, with accuracy held. **If the gate must be re-found
  online per task, that cost may kill the claim — we need to know here, not at T4.**

> **STOPPING MARK ① (revised):** if T1 clears the continual-cost + distribution-shift bar, the depth problem is
> *practically solved* and SCFF is "done." Tiers 2+ are improvements. **The honest minimum is likely T0 + T1.**

---

## TIER 2 — preservation — *re-spec'd; **[T0]** premise confirmed (decay is real under budget), but now a SECOND tool, not the first*

> **[T0] Re-framing:** T0.2 proved the depth is *curable via credit* (T3), not a hard task-bound wall — so the
> relationship is: **T3 extends how deep the stack BUILDS class structure (more credit reach); T2 PRESERVES what's
> built so deep layers can't overwrite it.** They are complementary. But the **free** T0.1 lever (temperature) and
> the **bounded** w4 window (T3) both lifted depth at *lower cost than a residual rewrite* — so run those first;
> reach for the frozen residual when the cheap-credit rungs are spent.

### T2.1 — frozen / init-based near-identity residual *(NOT learnable-local-α)*
- **Do:** wrap each SCFF block as `y = x + α·f(x)` with **α FROZEN at a small near-identity constant** (Fixup-style:
  the structural win — start as identity, deep layers can only *add* a bounded correction, can't overwrite — comes
  from the **initialization**, which needs *no training signal*). This sidesteps the fatal hole: a **local**-loss-
  trained α opens the gate exactly when the block starts drifting off-manifold (it chases local-objective magnitude).
- **Learned-α is allowed ONLY if driven by the GD-readout** (class-direction, licensed side) — never local contrast,
  never goodness. Then it's a GD knob, priced against the heads.
- **Dead-gate guard (mandatory test design):** a frozen-tiny α that does *nothing* also "stops the tail decaying,"
  so "tail stops decaying" can be passed by a dead gate. Verify contribution with **per-block α→0 ablation** — if
  ablating a block changes nothing, it's a bypass (the [residuals-harm-SSL] failure), not a contributor.
- **First-class risk:** the **S5 mandatory inter-layer norm × residual** interaction — a length-norm after a
  near-identity skip can rescale the preserved `x` and defeat preservation. Test it, don't assume it.
- **Preserve the class DIRECTION:** if a learned preservation term is wanted, prefer a **per-sample class-subspace
  preservation** (hold the class-discriminative directions fixed) over VICReg/Barlow variance-covariance (which
  restore *rank* — a symptom — use batch stats, and rot under continual shift). *(Whitening appendix:
  [`track-a-preservation.md`](track-a-preservation.md), post-review note.)*
- **Decision / STOPPING MARK ②:** preservation makes depth **safe to read**, not **unbounded to use** (the extractor
  stays task-bounded). If T0.1 confirmed the ceiling is task-set, T2 buys "read-top convenience," not capability —
  a cheap test, not a tier of commitment.

---

## TIER 3 — the cheap-credit ladder — ✅ **RAN [T3]: the lever is OBJECTIVE SHARPNESS (free), not credit-machinery**

*(v1 = "learned halting / PonderNet" (CUT). v2 = conditional global-coordination. **[T0]** locality control made it
mandatory. **[T3]** the ladder RAN — two guard-checked experiments + a deep-lit pass — and the verdict inverted the
expectation: the cheapest lever is **sharpening the objective we already have**, not adding credit-reach machinery.
Full results + figure: [`t3-results.md`](t3-results.md).)*

- **T3.0 — objective sharpness (FREE; the PRIMARY lever — promoted to a near-term DECISION).** Sharper InfoNCE
  **temperature 0.5→0.2** at the adopted depth-2 window reaches **tail-L12 0.539 / acc 0.550 ≈ the full-e2e ceiling
  (0.549 / 0.569)** at **1.9× cost vs 11×**. A sharper contrast keeps each layer's update on the class manifold, so
  the representation stops drifting with depth — the decay's *cause* attacked at the source, no architecture, no wire,
  flow-safe. **The cheap-credit win, and it isn't credit at all — it's the objective.** *Before committing the value:*
  (a) chart the **temp floor** incl. 0.1/0.05 (very-sharp contrast can collapse — too few effective negatives), and
  (b) a **continual-workload safety check** (does temp0.2 preserve the A6 sleep-recovery win — our actual home?).
- **T3.1 — wider window w4 (BOUNDED BACKUP; demoted).** Non-overlap window composes monotonically deeper (5-seed
  dose-response: tail-L12 w1→w12 = 0.387→0.429→0.469→0.501→0.525→0.549; replicated on flat). w4 (depth-4, tail 0.501,
  3.8×) is real, but **cost-dominated by T3.0** (temp0.2 gives more composition at half the backward depth). Keep as a
  bounded backup if temperature leaves a gap; a small **temp0.2 × w3/w4 combo** is the untested cheap closer.
- **~~T3.x — overlapping windows~~ → STRUCK.** lr-matched overlap (stride < window) *hurts* (w2s1 0.416 < w2 0.429;
  w4s1 0.473 ≪ w4 0.501) and costs 2–6× more. **Credit-chain LENGTH composes depth, not credit-path MULTIPLICITY** —
  averaging two short-reach local objectives at a layer blurs its target, it does not synthesize long-range credit.
- **~~T3.2 — naive top-down objective credit~~ → STRUCK.** A detached top-down consistency term in the local InfoNCE
  (the literature's #1 *cheap* candidate) was FD-gradient-verified and tested at window=1: **every λ>0 (anchor-to-top,
  predict-next, warmup) sits BELOW λ=0** — a detached reference imports the *decayed* top's badness ("anchor-to-
  decayed-top"). The cheapest objective-side fix does not manufacture global credit.
- **The genuine global-credit mechanisms → DEFERRED, possibly UNNECESSARY.** The real objective-side result
  (**2601.21683**, *Can Local Learning Match Self-Supervised Backprop?*, ICML 2026) reaches BP-SSL parity by aligning
  the **local update with the global-backprop update geometry** — strictly more than a reference-anchor term, and an
  open research question. DFA/EBD ([2504.11558]) is the global *wire* (needs a defined contrastive error; degrades
  with depth). **Re-open only if temperature + w4 leave a gap that matters on the continual workload.** **FTP
  ([2506.11030]) and PEPITA are OUT — verified to rewrite the forward stream** (not flow-safe; see
  [`lit-cheap-credit.md`](lit-cheap-credit.md) §C/§E).
- **The reference ceiling:** `window=12` (full e2e backprop) composes to L12 — the **diagnostic upper bound** every
  cheap rung is measured against (5-seed median tail 0.549). **Never deployed** (it's the forbidden full backward).
- **The one-scalar hypothesis** (S6 gate = plasticity gate = broadcast = the same neuromodulator) is parked with the
  deferred global-credit work — a north-star-adjacent hypothesis, not a Stage-1 design assumption.

---

## TIER 4 — continual optimization (the old Phase-5, now readout-aware)

- Tune **sleep cadence + the Ch7 gate** with the new readout in place.
- **Tunnel-aware (now with the C5 caveat):** consolidate **extractor-depth** features; LUT stores **extractor-depth**
  prototypes; **and** — the review's biggest unaddressed risk — handle that the sweet spot **moves under distribution
  shift**, so the placement/gate must be **re-validated online**, not frozen on stationary profiles.
- Land the deferred Phase-4 follow-ups here: **train-with-noise** (A7) and **natural-data multi-class** (A5).

---

## TIER 5 — the north star (where the CUT ideas come home)  🧠 *(held as direction, not specced)*

The depth fix assembles the organs; the *cut* Stage-1 over-engineering is exactly what belongs here:
- **Learned halting (PonderNet)** — cut from Stage 1 as over-engineering, but it **is** the "I-get-it feeling"; it
  lives here, in the recurrent loop.
- **The native settling-time signal** — parked from Stage 1 (the feedforward cell can't settle), it becomes the
  free, substrate-native *timing* of the feeling once the loop is recurrent.
- The recurrent neocortex ↔ hippocampus loop, working-state heads, the neuromodulator gate. Deliberately later —
  *simple intelligence first.*

---

## The honest "how much do we have to do" (v2.1 — post-T0)

T0 ran and **did shrink and re-shape the problem** rather than dissolve it. Two paths now run in parallel:

1. **The cost path (the MVP): T1.** Per-depth heads + calibrated exit, proven to beat the truncation baseline on the
   *continual* workload. Answers "where to read" cheaply. *Stopping Mark ①.* Unchanged by T0.
2. **The native-depth path (T3 RAN): mostly a FREE objective re-tune.** **[T3]** the cheap-credit ladder ran:
   sharpening the InfoNCE **temperature (0.5→0.2)** alone buys tail-L12 **0.539 ≈ the full-e2e ceiling (0.549)** at
   1.9× cost — native depth is largely deliverable by re-tuning the objective we already adopted, *no new architecture
   or wire.* Overlap and naive top-down credit were tested and **STRUCK** (clean negatives); the bounded window (w4)
   is a backup; genuine global-credit machinery is **deferred and may be unneeded**. **The most hopeful outcome: the
   decay is, to first order, an objective-sharpness problem with a free fix.** (Owed before committing: temp floor +
   continual-safety; natural data.)
3. **T2 (frozen residual)** — premise confirmed (decay is real under budget), but now the *second* preservation tool,
   after the cheaper T3.0/T3.1 rungs. Complementary, not either/or.
4. **T4** continual optimization (always next). **T5** the dream.

**Likely minimum to call SCFF "done":** **T1 (cost) + T3.0 (free temperature re-tune)** — the readout reads the right
depth cheaply, and the free objective re-tune **[T3: temp0.2 nearly matches the full-backprop ceiling at 1.9× cost]**
extends the useful depth for free. Everything above T3.0 is earned by how much native depth the chip actually needs
vs the truncation+read baseline — and T3 suggests that "everything above" may be little.

**Out of the committed path** (vs v1): learned halting/PonderNet, whitening-as-the-lever, and the native-goodness
placement signal — all cut, with reasons in [`review-and-revisions.md`](review-and-revisions.md).

## Decision-record deltas (to commit only after T0–T1 give results)

- **S9 — readout placement is adaptive (per-depth heads + a *calibrated class-confidence* exit), and this revises
  S3's literal "tap ALL layers"** (S3's *intent* — read the good early layers — is kept; the *mechanism* changes).
- The Tunnel Effect enters the citebase as a **named analogy for the shape**, not a load-bearing theory.
- ReZero/Fixup enters as **init-based preservation** (frozen α), not a learned gate.
