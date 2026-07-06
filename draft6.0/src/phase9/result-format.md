# Phase 9 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** Handed only a purpose, an agent's output rots four ways — graph formats drift,
> table styles drift, summaries drift, no continuity rung-to-rung. This file removes the freedom that causes all four. It
> is **not advisory** — it is the *spec the run code and the write-up must conform to*, the way `design.md` is the spec the
> experiments conform to. **If a rung's output can't be produced by the rules below, the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) **and the Phase-8 machinery**
> ([`../phase8/result-format.md`](../phase8/result-format.md)) — the gate/trigger/head encoding, the frontier ordering, the
> ADC-centred energy meter, the `arrays.npz`/`manifest.json` discipline, the 8-slot summary — and **adds only the Phase-9
> delta**: the maintenance-loop figures (the lifelong-drift panel, the N2 bake-off, the consolidation-depth cadence, the
> eviction bake-off, the conditional residual, the freeze integration), the P9-new metrics, and the freeze contract. Read
> it once; then *obey it*, don't re-derive it. **Canonical wins on any shared constant; P8 wins on any economy/meter
> constant; this file owns only the P9-new.**

---

## §0 — The three enforcement mechanisms (carried from P8)

1. **One plotting module — `plot_p9.py` — ONE function per figure code.** Every rung calls the *same* function (§C); the
   look lives in one place (`plot_p9.py:STYLE`, which imports `plot_p8.STYLE` and extends it — never re-defines a shared
   constant). No rung styles `matplotlib` inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice, with the worked card (§F) as the model.**
3. **One ledger schema + one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D); `plot_p9.py regen
   <run-dir>` redraws *every* figure from `arrays.npz`, never a live run. A figure you can't regenerate from saved data is a
   screenshot, not a result.

> **The rule of additions.** A rung that genuinely needs a new figure/metric **adds it to this file first** (so the next
> rung inherits it) — never a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (P9 delta; the rest inherited from `plot_p8.STYLE`)

`plot_p9.STYLE = {**plot_p8.STYLE, **P9_NEW}`. **dpi 300 · figsize {single (6.0,4.0) · wide/frontier (7.5,4.0) ·
panel-strip (10,2.2)} · DejaVu Sans 10pt · transparent bg · median line + IQR α0.18 / median bar + IQR whisker · light-grey
grid** — all inherited, never re-stated in code. The P8 gate/trigger/head/substrate colour encoding is inherited verbatim
(the committed loop uses SLDA + DDM on error-EMA [tap-drift-direction validated, not deployed] + the oracle/always-pay references — same colours). **P9-new
entities (colour · style — fixed forever):**

| entity | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **frozen/oracle reference** (known boundaries / full-history) | `#111111` (black) | **dash-dot** | ⭐ the achievable internal reference every P9 verdict is measured against (carried from P8) |
| **always-pay** ceiling | `#2ca02c` (green) | **dashed** | the cost/accuracy ceiling (carried from P8) |
| **bulk_drift (rotation)** | `#2c6fbf` (blue) | solid | the cosine drift curve — "the taps rotate" (P9.0) |
| **frozen-probe (readout-staleness)** | `#7f7f7f` (grey) | dashed, circle | a fit-once probe re-applied — what a *fixed head* loses (what sleep fixes) (P9.0) |
| **re-fit probe (destruction)** | `#d62728` (red) | solid, circle | ⭐ the true *forgetting* test — an optimal probe re-fit on the current bulk (P9.0 **verdict** curve, 2203.13381) |
| **no-N2** (P8 loop) | `#7f7f7f` (grey) | solid | the N2 baseline (P9.1) |
| **LLRD-rate** (N2 arm) | `#0b8f6a` (teal) | solid, triangle | ⭐ the doubly-grounded default N2 (rate-only) |
| **EMA-view** (N2 arm) | `#9467bd` (purple) | solid, square | the de-risked N2 upgrade (read-side) |
| **LDC (road-not-taken)** | `#cccccc` (light grey) | dotted | cited, NOT built — the scoped-out learned-projector (annotate only) |
| **all-tap sleep** (P8 depth) | `#7f7f7f` (grey) | solid | the P8 consolidation-depth baseline (P9.2) |
| **trunc-K sleep** (deployed depth) | `#0b8f6a` (teal) | solid, triangle | ⭐ the readout-aware / latent-replay depth (P9.2) |
| **per-depth sleep** | `#2c6fbf` (blue) | dashed, square | the single-sharp-depth consolidation (P9.2) |
| **CBRS** (committed eviction) | `#0b8f6a` (teal) | solid, triangle | ⭐ the committed bounded-LUT policy (P9.3) |
| **reservoir** (iid) | `#2c6fbf` (blue) | solid, square | the iid buffer (P9.3) |
| **recency/FIFO** | `#d9690a` (orange) | solid | the naive eviction (P9.3) |
| **herding** (feature-mean = magnitude null) | `#111111` (black) | **dashed**, x | ⚠ the **spine null** — keeps the class *mean* not the *direction span* (P9.3); expected to re-import forgetting |
| **D-CBRS** (diversity, conditional) | `#0b8f6a` (teal) | dotted, triangle | the CBRS diversity refinement (added only if CBRS loses diversity) |
| **residual undefended / read-side-defended** | `#d62728` / `#0b8f6a` | dashed / solid | the P9.4 conditional pair (retention without vs with the feature-level re-fit) |

Read by role: **black dash-dot = the internal oracle/frozen reference** (matching it at lower cost is the win); **teal =
the committed / adopted P9 choice**; **black-dashed-x = a spine null** (herding, expected to fail — the demonstration);
**light-grey dotted = cited-not-built** (LDC). **Frontiers/bakeoffs order arms by the measured swept quantity** (drift-
reduction, sleep-cost, evict-BWT), never by an asserted order; arms failing the A6/accuracy cut are **greyed**.

**Required `plot_p9.py` API (one function per figure; signatures fixed):**

```
STYLE                        # {**plot_p8.STYLE, **P9_NEW}; the ONLY place P9 styling lives
fig_drift_lifelong(run)      # F: DRIFT-LIFELONG  (THE P9.0 headline — rotation cosine + frozen-probe staleness + RE-FIT-probe destruction, over the long stream)
fig_n2_bakeoff(run)          # F: N2-BAKEOFF      (drift-reduction × sleep-freq × A6-BWT × plasticity; no-N2 vs LLRD-rate vs EMA-view)
fig_cadence_depth(run)       # F: CADENCE-DEPTH   (worst-point A6-BWT × metered sleep-cost vs consolidation depth)
fig_evict(run)               # F: EVICT           (evict-BWT vs policy at the bound + the cap×#classes scaling inset)
fig_residual(run)            # F: RESIDUAL        (P9.4 conditional — directional retention, undefended vs read-side-defended)
fig_freeze(run)              # F: FREEZE          (P9.5 — the assembled live loop: worst-point A6 + accuracy-held + GD-share, vs oracle)
fig_cont_safety(run)         # F: CONT-SAFETY     (carried from plot_p8 — reused on the assembled loop; the live A6 gate + veto)
fig_inv(run)                 # F: INV             (every run — guards + fire/sleep-counts + health)
regen(run_dir)               # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

Every `fig_*` reads `arrays.npz` + `manifest.json`, draws in `STYLE`, writes a 300-dpi PNG. **No rung draws outside these
functions**, and **every rung writes `arrays.npz` to the schema below.**

**The `arrays.npz` schema (P9 delta — a rung emits the subset its figures need; P8 keys carried):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | seed list (S=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) |
| `bulkdrift_life` | `[S, K]` | `cos(rep_t, rep_{t+Δ})` over the **long** stream (K checkpoints) — the **rotation** curve (P9.0) |
| `frozenprobe_ret` | `[S, K]` | a probe **fit once at birth, re-applied** to the current bulk / its birth score — the **readout-staleness** curve (P9.0) |
| `refitprobe_ret` | `[S, K]` | an **optimal probe re-fit on the current bulk**, scored on held-out early-task data / birth score — the **destruction** curve ⭐ (P9.0 verdict; 2203.13381) |
| `n2_arms` | `[A]` (str) | the N2 arm names raced — {no-N2, llrd-rate, ema-view} (P9.1) |
| `drift_red_<arm>` · `sleepfreq_<arm>` · `accheld_<arm>` · `bwt_worst_<arm>` · `plasticity_<arm>` | `[S]` | the P9.1 bake-off axes per arm |
| `depths` | `[D]` (str) | consolidation depths raced — {alltap, truncK, perdepth} (P9.2) |
| `bwt_worst_<depth>` · `sleepcost_<depth>` · `accheld_<depth>` | `[S]` | the P9.2 cadence-depth axes per depth |
| `evict_policies` | `[P]` (str) | eviction policies raced — {oracle, cbrs, reservoir, recency, herding(, dcbrs)} (P9.3) |
| `evictbwt_<policy>` · `accheld_<policy>` | `[S]` | worst-point BWT / accuracy-held at the bound, per policy (P9.3) |
| `cap_scaling` | `[Ncap, 3]` | columns `[cap, #classes, min-cap-holding-BWT]` — the scaling-law sub-sweep (P9.3) |
| `residual_ret` | `[S, 2]` | directional retention `[undefended, read-side-defended]` (P9.4, conditional) |
| `residual_dent` | `[S]` | the earn-its-place probe: committed-SLDA retention drop from the residual (P9.4 gate) |
| `freeze_bwt_worst` · `freeze_accheld` · `freeze_gdshare` | `[S]` | the assembled-loop live-safety + economy (P9.5) |
| `freeze_hash` | scalar (str) | the git commit hash of the frozen object (P9.5 — the artifact P10 races) |
| `bwt_<cfg>` · `aa_<cfg>` · `forget_<cfg>` · `gdshare_<cfg>` · `firefrac_<cfg>` | `[S]` | carried P8 live-loop metrics (reused on the assembled loop) |
| `inv_<panel>` | `[S, …]` | INV panels (all P8 guards + `n2_readside` + `evict_equiv` + fire/sleep-counts) |

> **Source-of-truth note:** canonical [`../result-format.md`](../result-format.md) Layer A **owns** shared constants
> (dpi, IQR band, the n=5 rule); [`../phase8/result-format.md`](../phase8/result-format.md) owns the economy/meter/gate
> encoding; **this file owns only the P9-new** (the drift-destruction split, the N2/depth/eviction encodings, the freeze
> keys). If they diverge, **canonical > P8 > P9.**

---

## §B — The metric dictionary (P9 additions in **bold**; P8 metrics carried unchanged)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| **accuracy-held** | live-stream final AA, vs the **frozen/oracle** baseline + the **always-pay** ceiling | acc, median [IQR] |
| continual **BWT / AA / forget** | GEM/CL (`acc_matrix_metrics`) on the LIVE loop, **at the awake gate's worst mid-stream point (pre-sleep)**; vs oracle/frozen; + paired-sign veto | acc / acc-delta |
| **`bulk_drift` (rotation)** | `cos(rep_t, rep_{t+Δ})` of fixed probes over the **long** stream (the rate a fresh sleep re-solve tracks) | cosine vs step |
| **readout-staleness (frozen probe)** | a probe **fit once at birth, re-applied** to the current bulk — what a *fixed head* rots (what sleep fixes) | acc-ratio vs step |
| **destruction retention (re-fit probe) ⭐** | an **optimal probe re-fit on the current bulk**, scored on held-out early-task data — the true forgetting measure (2203.13381; **the P9.0 verdict**, rotation factored out) | acc-ratio vs step |
| **drift-reduction** | `bulk_drift` (or sleep-frequency) with N2 vs without — the P9.1 lever's effect | Δ / ratio |
| **plasticity / new-task acc** | acc on the newest task right after it arrives — the N2 slowdown **tax** check | acc, median [IQR] |
| **sleep-cost** | metered readout energy at sleep per consolidation depth (P8 ADC-centred meter, sleep path) — the P9.2 saving | relative-E |
| **evict-BWT** | worst-point BWT at a **bounded** buffer per eviction policy, vs the unbounded oracle | acc-delta |
| **buffer-cap scaling** | smallest cap holding BWT within δ_acc, vs #classes — the memory-scaling law | cap vs #classes |
| **residual-retention** | directional retention of the committed SLDA loop, read-side-defended vs undefended (P9.4) | retention ratio |
| **GD-fire-fraction / metered 80/20** | carried from P8 — the economy the P9 tuning must **not inflate** (`GD-share ≤ 0.25`) | fraction |

**The verdict cuts (PINNED, blind — the design §2.3 cuts, restated as the reporting contract; every cut is vs an INTERNAL
reference, NEVER the P10 BP+replay number):**
- **P9.0 (risk gate):** "rotation-only / cheapness holds" iff `bulk_drift` bounded **AND** frozen-probe retention within
  δ_acc of birth (paired); "the bulk forgets" (headline) iff frozen-probe retention drops > δ_acc, ≥4/5 sign. No knob tuned.
- **P9.1 (N2):** adopt-eligible iff sleep-frequency (or drift) ↓ at accuracy-held within δ_acc (paired) **AND** worst-point
  A6-BWT not worse (veto) **AND** `n2_readside_guard` green (no objective knob moved) **AND** plasticity not down > δ_acc;
  commit the cheaper eligible arm; else **struck**; "reopen-flag" iff it helps only by moving the objective (not executed).
- **P9.2 (depth):** adopt trunc-depth iff worst-point A6-BWT held (within δ_acc, paired, veto) at a strictly lower
  `sleep_cost` (E-ratio ≥ ~1.5×, frontier-knee not hard-binary); else keep all-tap. Re-confirm frequency if N2 slowed drift.
- **P9.3 (eviction):** commit CBRS iff evict-BWT within δ_acc of the unbounded oracle (paired) **AND** beats recency/herding
  by the real-difference bar; a policy "re-imports forgetting" iff its BWT drops > δ_acc (logged with mechanism; herding
  *expected* to — the spine null); scaling flag iff min-cap-holding-BWT grows with #classes.
- **P9.4 (conditional):** earn-its-place iff `residual_dent` > δ_acc on the committed SLDA loop; then "recovered" iff
  read-side retention lifts toward no-residual (paired ≥4/5); else named → analog layer. Calibration is direction-grounded.
- **P9.5 (freeze):** freeze iff assembled worst-point A6-BWT not negative vs oracle in ≥4/5 (veto) **AND** accuracy-held
  within δ_acc of the components **AND** GD-share ≤ 0.25; else fix inside P9 + re-freeze. The freeze = a git hash + manifest.

**No result may be narrated into a branch it does not numerically satisfy.**

**Calling a difference real (n=5; carry):** IQR-disjoint at the final checkpoint **and** sign-consistent in ≥4/5 paired
seeds; else "within noise." At every A6 re-check "within noise" is NOT an auto-pass — the paired-sign veto applies.
Decisive gaps ≤ 0.02 get **9 seeds**; A6 re-checks run the full 5, never 3.

**Threats-to-validity, reported every rung:** (a) the meter is a **behavioral model** — log/cite per-op params; (b) the
long-stream drift depends on the **stream schedule** — the frozen-probe retention is the schedule-independent destruction
read; (c) **calibration-under-shift** for P9.4 is **feature-level** (scalar TS is a diagnostic, ineffective under shift);
(d) the oracle uses hidden boundaries the loop can't see — matching it is the *win*; (e) **the internal-signals-only rule**
— no verdict references the P10 BP+replay number (state it in each card).

---

## §C — The figure catalog (declare which you emit; never invent)

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **DRIFT-LIFELONG** *(P9.0 headline)* | `fig_drift_lifelong` | over the long stream: `bulk_drift` cosine (rotation, blue) · fit-once frozen-probe (readout-staleness, grey) · **re-fit probe (destruction, red — the verdict curve)** | does the bulk only **rotate** (sleep fixes it — cheapness holds) or **forget** (the *re-fit* retention decays — the assumption breaks) |
| **N2-BAKEOFF** *(P9.1)* | `fig_n2_bakeoff` | scorecard: drift-reduction · sleep-freq-at-held-accuracy · worst-point A6-BWT · plasticity, per arm (no-N2 / LLRD-rate / EMA-view); LDC annotated cited-not-built | which N2 form ↓ drift → sparser sleep at held A6 without a plasticity tax; or is N2 struck |
| **CADENCE-DEPTH** *(P9.2)* | `fig_cadence_depth` | worst-point A6-BWT **and** metered sleep-cost vs consolidation depth (all-tap / trunc-K / per-depth) | which depth holds A6 at the lowest sleep cost (latent-replay layer selection) |
| **EVICT** *(P9.3)* | `fig_evict` | evict-BWT vs eviction policy at the bound (ordered), oracle reference; **inset:** cap × #classes scaling | does CBRS hold BWT at the bound; does eviction re-import forgetting (herding the null); does the cap scale with #classes |
| **RESIDUAL** *(P9.4, conditional)* | `fig_residual` | directional retention, undefended vs read-side-defended, vs the no-residual reference | can a feature-level read-side re-fit defend the Phase-6 residual, or is it named → analog layer |
| **FREEZE** *(P9.5 headline)* | `fig_freeze` | the assembled live loop: worst-point A6-BWT + accuracy-held + GD-share, vs the oracle/frozen + always-pay refs; the freeze-hash annotated | does the fully-tuned loop hold A6 + accuracy at the metered economy — is it lockable |
| **CONT-SAFETY** *(carried from plot_p8)* | `fig_cont_safety` | BWT / AA / forget bars at the worst mid-stream point, live vs oracle/frozen (+ veto marker) | the live A6 gate on the assembled loop (reused at P9.5) |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples: all P8 guards + `n2_readside` ✓ + `evict_equiv` ✓ + fire/sleep-counts | guards + apparatus sanity at a glance |

**Caption rule (every figure):** one sentence ending with **the takeaway** (not a description), then `(n=5, task, …)`. An
**accuracy-held / BWT** caption always names the **frozen/oracle** reference. A **cost/energy** caption tags the **meter
model + params** and never asserts a Joule it can't source. A **P9.0** caption states both the rotation *and* the
destruction read. A **spine** caption (P9.3 herding, P9.1 EMA-view) states whether the choice reads a **direction** or a
**magnitude**. Model caption:

> *"CBRS held worst-point BWT within 0.0X of the unbounded oracle (−0.0a vs −0.0b) at buffer cap C, while herding — keeping
> the class mean, not the direction span — re-imported forgetting (−0.0c); committed / re-imports-forgetting. (n=5, live
> bounded-LUT CI+nuisance stream)"*
>
> *(Letters are deliberate placeholders — the caption teaches the shape, never an expected result. Do not anchor on any
> number.)*

---

## §D — Table schemas (fixed columns; one IQR format `median [q25–q75]`; no bare means)

**The RESULTS.md ledger — one section per rung; header states locked controls (`task, stream, seeds, head/gate/cadence`);
last column = a ≤6-word verdict; one variable swept per table (the swept variable is the first column):**

| rung | columns (after the swept variable) |
| --- | --- |
| P9.0 | `metric · value(over stream) · vs-birth/floor · rotation/staleness/destruction · verdict` *(the three curves; the verdict keys on the re-fit destruction curve; + guards)* |
| P9.1 | `N2-arm · drift-reduction · sleep-freq · accuracy-held · A6-BWT(worst) · plasticity · vs-no-N2 · verdict` |
| P9.2 | `depth · A6-BWT(worst) · sleep-cost · accuracy-held · vs-all-tap · verdict` *(+ a separate frequency-reconfirm sub-table if N2 slowed the drift — never co-varied with depth)* |
| P9.3 | `policy · evict-BWT(worst) · accuracy-held · vs-oracle · verdict` *(+ a scaling sub-table: cap · #classes · holds?)* |
| P9.4 | `defense · residual-retention · residual-dent(gate) · vs-no-residual · verdict` *(or a one-line skip-card if the gate probe did not fire)* |
| P9.5 | `mechanism · AA · BWT(worst,+paired-sign) · GD-share · vs-oracle · frozen? (hash)` |

**Struck / skipped rows:** identical schema, with the failure/skip condition + the **mechanistic reason** in the verdict
column — a struck arm (N2-none, a losing eviction policy) and a skipped conditional rung (P9.4 gate did not fire) get the
same rigor as a win (failures are data).

---

## §E — The summary writing contract (the 8 slots — fill verbatim, formal voice; carried from P8, P9-tuned)

Every `expK/experiment-K.md` *Read* section fills these 8 slots in order, none empty (if "n/a", say *why*):

1. **Claim** — one falsifiable sentence.
2. **Headline number** — median **[IQR]**, against the **internal** references (the frozen/oracle baseline, the always-pay
   ceiling, the measured drift). Never a bare number; **never the P10 BP+replay number.**
3. **Figures** — the catalog refs emitted, each one line; name the headline figure.
4. **Mechanism** — *why* the number is what it is (the spine: does the choice read a **direction** or a **magnitude**? does
   N2 slow the drift or tax plasticity? is the bulk **rotating** or **forgetting**? does eviction keep the direction span or
   the dense mean?).
5. **Threats to validity** — the §B carry (behavioral meter; stream-schedule dependence; feature-level calibration; the
   oracle uses hidden boundaries); the methodology rule-1 check, written in.
6. **Decision** — which open knob this **sets** (N2 form / consolidation depth / eviction policy / the residual verdict),
   and what the next rung inherits.
7. **Freeze-honesty** — **the internal-signals-only rule is affirmed** (this verdict did not look at the P10 baseline); the
   metered `GD-share ≤ 0.25` still holds after this tuning; the meter model + params are stated.
8. **Live-safety / freeze** — what this rung says about the **live A6 continual-safety** and (at P9.5) the **freeze** (the
   commit hash, the veto result). A rung that moves neither a knob nor live-safety nor the freeze shouldn't have run.

**Voice rules:** declarative past-tense for what happened; present-tense for standing reads; **no hedging filler, no
first-person, no exclamation**; every adjective backed by a number or dropped; a struck result stated plainly ("herding
re-imported forgetting — worst-point BWT −0.0c, below the oracle by > δ_acc in 5/5 seeds — the density≠class demonstration
at the buffer"). **Continuity:** each card opens by naming the knob it inherits ("Inheriting the committed SLDA + DDM +
class-direction economy from P8 and the measured rotation-only drift from P9.0, …"). A skipped conditional rung (P9.4) is a
one-line skip-card naming the gate-test that closed it.

---

## §F — Gold-standard worked card (copy this skeleton; the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches the
> shape, voice, and completeness, never an answer.*

```markdown
# P9.3 — Bounded-LUT eviction: does the continual-safety win survive a finite buffer?

**Question.** At a fixed buffer cap under the bursty class-imbalanced stream, which eviction policy holds worst-point BWT
within δ_acc of the unbounded oracle — and does eviction re-import forgetting?

**Setup.** Swept variable = eviction policy ∈ {unbounded-oracle, CBRS, reservoir, recency, herding}; controls locked (live
NoiseAugContrast bulk, committed SLDA + DDM-on-error-EMA economy (tap-drift-direction validated, not deployed), the P9.2 consolidation depth, bounded-LUT cap=C,
CI+nuisance stream, seeds [42,137,271,314,1729]). EVICT + INV. Apparatus: p9lib StreamingLUT + awake_sleep_loop; guards
passed (partial-fit-equiv; live-path-anchor; evict-equiv ≡ block-mode full-history at cap=∞ + finite-cap FIFO check; n2-readside; meter-proxy;
detector-FAR; cache-replay). Internal-signals-only affirmed: no P10 BP+replay number consulted.

**Run.** P policies × 5 seeds, checkpointed (_ckpt.jsonl); live SCFF + bounded-LUT sleep. Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| policy | evict-BWT(worst) | accuracy-held | vs-oracle | verdict |
| --- | --- | --- | --- | --- |
| unbounded-oracle (ref) | -0.0b [..–..] | 0.OO [..–..] | (ref) | the ceiling |
| CBRS | -0.0a [..–..] | 0.AA [..–..] | <within δ_acc?> | <committed?> |
| reservoir | -0.0d [..–..] | 0.BB [..–..] | <?> | <holds / drops?> |
| recency/FIFO | -0.0e [..–..] | 0.CC [..–..] | <?> | <re-imports forgetting?> |
| herding (mean null) | -0.0c [..–..] | 0.DD [..–..] | <> δ_acc?> | <spine null — expected to fail> |
- **EVICT** (headline): <where BWT holds vs drops; the herding null; the cap×#classes scaling inset>.
  - **INV**: partial-fit-equiv ✓, evict-equiv ✓, n2-readside ✓, meter-proxy ✓, detector-FAR ✓, cache-replay ✓.

**Read (8 slots).**
1. *Claim* — CBRS holds worst-point BWT within δ_acc of the unbounded oracle at cap C; herding re-imports forgetting.
2. *Headline* — CBRS −0.0a [IQR] vs oracle −0.0b (within δ_acc), herding −0.0c (> δ_acc) (n=5, live bounded-LUT stream).
3. *Figures* — EVICT (policies + scaling inset), INV (guards green).
4. *Mechanism* — if CBRS held: class-balanced eviction keeps prototypes spanning the class *directions*; herding keeps the
   dense *mean* and drops the tails → the class direction narrows → forgetting (density≠class at the buffer).
5. *Threats* — (a) behavioral meter params logged; (b) scaling read depends on #classes swept; (c) "real" = IQR-disjoint + ≥4/5 sign.
6. *Decision* — sets the committed bounded-LUT eviction policy (S13-candidate); P9.5 inherits it.
7. *Freeze-honesty* — internal-signals-only affirmed (no P10 baseline consulted); GD-share still ≤ 0.25 with this policy.
8. *Live-safety* — A6 held at the bound (worst-point veto 0/5 negative) → carried into the P9.5 assemble+freeze.
```

This is the bar: every slot filled, IQR in every cell, the internal reference named, the spine stated, the freeze-honesty
affirmed, the guards green.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

- [ ] **Median [IQR]** for every headline number (n=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) — no bare means.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 by sign) before any gap is claimed; else "within noise."
- [ ] Every accuracy/BWT figure names the **frozen/oracle** internal reference; a cost figure tags the **meter model + params**.
- [ ] **Verdict branch matches its numeric cut** (§B): P9.0 (rotation vs destruction), P9.1 (adopt/struck/reopen-flag +
  plasticity tax + `n2_readside` green), P9.2 (depth E-ratio ≥ ~1.5×), P9.3 (CBRS within δ_acc of oracle; herding the null;
  scaling flag), P9.4 (earn-its-place gate → feature-level defense), P9.5 (worst-point veto + accuracy + GD-share → freeze).
  No result narrated into a branch it doesn't satisfy.
- [ ] **The internal-signals-only rule affirmed in slot 7** — the verdict did **not** consult the P10 BP+replay number.
- [ ] **The metered `GD-share ≤ 0.25`** still holds after the tuning (the economy was not inflated to buy accuracy).
- [ ] **P9.0** reports **all three** curves (rotation cosine · fit-once frozen-probe staleness · **re-fit-probe destruction**)
  and keys the verdict on the **re-fit destruction** curve (a frozen probe alone conflates rotation with forgetting).
- [ ] **P9.1** reports the **plasticity tax** (new-task acc) beside the drift-reduction; **EMA-view is the default arm**,
  LLRD-rate the flagged secondary whose `n2_readside_guard` is **representation-level** (`ρ=1` bit-for-bit + early/mid taps
  unmoved, else Stage-1-reopen); an **adopted-but-inert** N2 is struck at assemble; LDC is annotated **cited-not-built.**
- [ ] **P9.3** builds the **accumulating `StreamingLUT`** (P8 has no growing history); the **cap is pinned at a pressure
  point**; races **herding as the magnitude/mean null** (report "buffer-spine null here" if it can't fail); **GSS not raced**
  (gradient-free); **D-CBRS uses a hand-rolled single-threaded scorer, not sklearn K-means**; the **cap × #classes scaling**
  sub-sweep is a separate sub-table.
- [ ] **P9.4** is **conditional** — the earn-its-place gate probe (Phase-6 `NoiseModel` channel, **not** the nuisance
  injector) is reported first; if it did not fire, a one-line skip-card names the gate-test; if it ran, the defense is
  **prototype re-anchoring from the raw LUT** (primary) / SLDA covariance-refit (shrinkage-guarded fallback), **never** a
  scalar TS; and P9.4 tunes on the **home residual only** (P10 uses a held-out battery).
- [ ] **P9.5** runs 5 seeds on the **assembled** live loop, BWT at the **worst mid-stream point (pre-sleep)**, paired-sign
  veto, **accuracy-held within δ_acc of the P8.6 committed-loop live AA** (the pinned reference), GD-share ≤ 0.25; on pass,
  **the commit hash is recorded** (`freeze_hash`) **and the manifest enumerates every committed knob incl. conditionals
  resolved off** (`N2: struck` / `residual: skipped`) — the artifact Phase 10 races.
- [ ] Every figure drawn by a **`plot_p9.fig_*`** function (no inline styling); caption ends with the takeaway + `(n=…, …)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); formal voice; the card opens by naming the inherited knob.
- [ ] **`manifest.json`** (git hash, config, seeds, versions, wall-clock, meter per-op params + citations) **+ `arrays.npz`**
  written; **`plot_p9.py regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards logged:** all P8 guards (partial-fit-equiv · live-path-anchor · scff-static-frozen · meter-proxy ·
  detector-far · cache-replay · fd-budget-gate; exported names carry `_guard`) **+ `n2_readside`** (N2-off ≡ P8 bit-for-bit;
  EMA-view: SCFF untouched; **LLRD-rate: representation-level — `ρ=1` bit-for-bit + early/mid taps unmoved**) **+
  `evict_equiv`** (`StreamingLUT(cap=∞)` ≡ block-mode full-history bit-for-bit **+ a finite-cap FIFO behavioral check**).
  **Any guard fails → STOP.**
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874
  guards; **no sklearn / no River** for compute; the real PID verified alive on multi-hour live cells.
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **struck / skipped** arm logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P9.0** bench + drift + destruction | **DRIFT-LIFELONG** (rotation + destruction), INV (all guards + `n2_readside`/`evict_equiv`) |
| **P9.1** N2 bake-off | **N2-BAKEOFF** (drift-red × sleep-freq × A6-BWT × plasticity), INV |
| **P9.2** consolidation depth | **CADENCE-DEPTH** (A6-BWT × sleep-cost vs depth), INV |
| **P9.3** bounded-LUT eviction | **EVICT** (policies + cap×#classes scaling), INV |
| **P9.4** read-side residual *(conditional)* | **RESIDUAL** (undefended vs defended) — or a one-line skip-card, INV |
| **P9.5** assemble + FREEZE | **FREEZE** + **CONT-SAFETY** (assembled live loop, veto) + the committed loop + the freeze hash + the P10 brief |

## Grounding (what the field does — and what we adopt)

- **Does the unsupervised bulk forget?** continuous SSL forgets (ECCV'22; [2311.13321]); CaSSLe [2112.04215] the optimistic
  pole; drift measurable [2203.13381] → DRIFT-LIFELONG (P9.0).
- **Slow coordination / N2** (momentum-encoder [2208.05744]; EMA reps [2411.18704]; LDC [2407.08536] the cited road-not-taken)
  → N2-BAKEOFF (P9.1).
- **Consolidation depth = Latent Replay** [1912.01100]; Layerwise Proximal Replay [2402.09542] → CADENCE-DEPTH (P9.2).
- **Bounded buffer** = CBRS (Chrysakis & Moens ICML'20) > GSS [1903.08671] (dropped); herding (iCaRL) the mean null; D-CBRS
  [2207.05897] the diversity refinement; small-buffer selection [2407.00673] → EVICT (P9.3).
- **Read-side calibration** — TS ineffective under shift; T-CIL (CVPR'25)/DATS [2509.21161]; feature-level prototype shift
  [2403.12952] → RESIDUAL (P9.4). Full delta: [`../../research/papers/phase9/deep-research-delta.md`](../../research/papers/phase9/deep-research-delta.md).
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 discipline — carried from Phases 1–8
  ([`../result-format.md`](../result-format.md), [`../phase8/result-format.md`](../phase8/result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to this catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent. **Build, then freeze.**
