# Phase 8 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** Handed only a purpose, an agent's output rots four ways — graph formats drift,
> table styles drift, summaries drift, no continuity rung-to-rung. This file removes the freedom that causes all four. It
> is **not advisory** — it is the *spec the run code and the write-up must conform to*, the way `design.md` is the spec
> the experiments conform to. **If a rung's output can't be produced by the rules below, the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) and **adds the operational
> machinery** for Phase 8: the locked visual constants, the `plot_p8.py` API, the array schema, the table schemas, the
> 8-slot summary template, a worked card, and a pre-submit checklist. Read it once; then *obey it*, don't re-derive it.

---

## §0 — The three enforcement mechanisms

1. **One plotting module — `plot_p8.py` — ONE function per figure code.** Every rung calls the *same* function (§C); the
   look lives in one place (§A `STYLE`). No rung styles `matplotlib` inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice, with the worked card (§F) as the model.**
3. **One ledger schema + one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D); `plot_p8.py
   regen <run-dir>` redraws *every* figure from `arrays.npz`, never a live run. A figure you can't regenerate from saved
   data is a screenshot, not a result.

> **The rule of additions.** A rung that genuinely needs a new figure/metric **adds it to this file first** (so the next
> rung inherits it) — never a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (single source of truth; `plot_p8.py:STYLE`)

| constant | value | note |
| --- | --- | --- |
| **dpi** | **300** | PNG default (survives the pandoc→docx A4 path) |
| **figsize** | **single = (6.0, 4.0) · wide/frontier = (7.5, 4.0) · panel-strip = (10, 2.2)** | one of three sizes — never ad-hoc |
| **font** | **DejaVu Sans**, base **10 pt** (title 11 bold · axis 10 · tick 9 · caption 9) | identical every plot |
| **background** | **transparent** | docx/slide reuse |
| **IQR band / error bar** | median line (1.8 lw) + shaded fill α 0.18 for curves; median bar + IQR whisker for bars | every headline, no exceptions |
| **grid** | light grey `#d9d9d9`, 0.6 lw, behind data | on for line/frontier, off for bars |

**Gate / trigger / head encoding (colour · style — fixed forever):**

| entity | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **always-pay** (no-gate ceiling) | `#2ca02c` (green) | **dashed** | the cost ceiling / accuracy near-ceiling reference |
| **oracle-cadence** (known boundaries) | `#111111` (black) | **dash-dot** | ⭐ the achievable reference the detector must approach |
| **absolute-θ** | `#7f7f7f` (grey) | solid | the rough S6 gate |
| **DDM** (two-threshold error) | `#d9690a` (orange) | solid, circle | error-based, two-threshold |
| **ADWIN** (two-window error) | `#2c6fbf` (blue) | solid, square | error-based, self-tuning |
| **error-EMA trigger** | `#d9690a` (orange) | dotted | the **labeled reference** trigger (precise, lags; a labeled magnitude — NOT spine-clean) |
| **tap-drift-direction** (label-free) | `#0b8f6a` (teal) | solid, triangle | ⭐ the committed candidate — drift **along the class/readout directions** (spine-clean) |
| **tap-drift-magnitude** (label-free null) | `#111111` (black) | **dashed**, x | the **false-fire null** — raw mean-shift/MMD (a magnitude-of-shift; ADWIN-U-style input moments) |
| **DriftLens** (label-free reference) | `#0b8f6a` (teal) | **dashed**, triangle | the purpose-built embedding-distance detector (the reference the home-grown signal is checked against) |
| **STUDD** (label-free, conservative) | `#0b8f6a` (teal) | dotted, triangle | student-teacher mimic-loss (fewer false alarms, slower) |
| **budget-gate** (learned) | `#9467bd` (purple) | solid | ⚠ least spine-pure (reads a drift feature, FD-guarded) |
| **HDDM/RDDM** (gradual, conditional) | `#7f7f7f` (grey) | dotted | gradual-drift-tuned arm — added only if P8.0 shows slow creep |
| **RanPAC** (committed head) | `#0b8f6a` (teal) | solid, triangle | the committed namer (cost meter's subject A) |
| **SLDA** (cost fallback head) | `#2c6fbf` (blue) | **dashed**, square | the ~200×-cheaper-proxy no-grad alternative (subject B) |
| **BP energy model** | `#8a1b8a` (magenta) | **dashed** | the backward-every-step energy reference (metered 80/20) |
| **chance** | `#111111` dotted thin | — | the floor of floors |

Read by colour/role: **black dash-dot = the oracle reference** (the win condition is *approaching* it at lower cost);
**green dashed = the always-pay ceiling**; error-based detectors solid, **label-free detectors dashed/teal**; purple =
the learned gate (spine-flagged). The **GATE-BAKEOFF frontier orders arms by measured GD-fire-fraction** (cheapest →
most-expensive), never by an asserted order; arms that fail the accuracy-held cut are **greyed** (they don't anchor the
frontier).

**Required `plot_p8.py` API (one function per figure; signatures fixed):**

```
STYLE                       # the dict of constants above; the ONLY place styling lives
fig_gate_bakeoff(run)       # F: GATE-BAKEOFF   (THE headline — accuracy-held × GD-fire-fraction frontier + scorecard)
fig_trigger(run)            # F: TRIGGER        (MTD × FAR: does tap-drift lead error without false-firing)
fig_cadence(run)            # F: CADENCE        (accuracy-held & A6-BWT vs sleep frequency × history fraction)
fig_cost_meter(run)         # F: COST-METER     (per-op energy breakdown bars: MAC/ADC/write/solve, RanPAC vs SLDA)
fig_metered_8020(run)       # F: METERED-8020   (GD-share vs SCFF-share stacked, vs the BP energy model)
fig_drift(run)              # F: DRIFT          (live bulk_drift cos vs stream-step; "the bulk doesn't forget")
fig_cont_safety(run)        # F: CONT-SAFETY    (the LIVE A6 gate — BWT/AA/forget vs oracle/frozen baseline + veto)
fig_inv(run)                # F: INV            (every run — guards + fire-counts + health)
regen(run_dir)              # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

The **P8.6 synthesis re-uses these** on the assembled live run (GATE-BAKEOFF + METERED-8020 + CONT-SAFETY) — it adds no
new plotter. Every `fig_*` reads `arrays.npz` + `manifest.json`, draws in `STYLE`, writes a 300-dpi PNG. **No rung draws
outside these functions**, and **every rung writes `arrays.npz` to the schema below.**

**The `arrays.npz` schema (pinned — key · shape · meaning; a rung emits the subset its figures need):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | seed list (S=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) |
| `gates` / `triggers` | `[G]` / `[T]` (str) | the gate-arm / trigger-arm names raced — the "method" axis |
| `accheld_<gate>` | `[S]` | live-stream accuracy-held (final AA), vs the oracle-cadence baseline + always-pay ceiling |
| `firefrac_<gate>` | `[S]` | GD-fire-fraction `f` = fraction of steps that trigger a namer update (op (c)) |
| `far_<arm>` · `mtd_<arm>` · `mtfa_<arm>` | `[S]` | FAR on the **nuisance** segment · MTD to *known real*-drift onsets · MTFA on the **stationary** segment (per-arm floor) |
| `bwt_<gate>` · `aa_<gate>` · `forget_<gate>` | `[S]` | LIVE-loop continual metrics (`acc_matrix_metrics`); vs oracle/frozen baseline; **NOT "retention"** |
| `bwt_worst_<gate>` | `[S]` | BWT at the **awake gate's worst mid-stream point (pre-sleep)** — the P8.6 safety read (post-sleep hides it) |
| `energy_<head>_<op>` | `[S]` or scalar | per-op energy `op ∈ {mac, adc, write, solve}` for `head ∈ {ranpac, slda}` — the cost meter (per-op params logged) |
| `gdshare_<config>` | `[S]` | `E[(c)+(d)] / E_total`; `bp_ratio` `[S]` = `E_total / E_BP+replay_model` (matched retention, same substrate table) |
| `bulkdrift` · `driftvis` | `[S, K]` / `[S, K, 2]` | `cos(rep_t, rep_{t+Δ})` across `K` steps; `driftvis` = the class-direction signal at [real-onset, nuisance-onset] markers (the P8.0 drift-visibility panel) |
| `cadence_grid` | `[S, F, H]` | accuracy-held over sleep-frequency `F` × history-fraction `H` × `λ_ema` (CADENCE); `cadence_bwt` (worst-point) same shape |
| `inv_<panel>` | `[S, …]` | INV panels (`partial_fit_equiv`/`live_path_anchor`/`scff_static_frozen`/`meter_proxy`/`detector_far`/`cache_replay`/`fdguard`/`firecounts`) |

> **Source-of-truth note:** canonical [`../result-format.md`](../result-format.md) Layer A **owns** any shared constant
> (dpi, IQR band, the n=5 rule); the restatement above is the **binding restatement for the Phase-8 executor**; if they
> diverge, **canonical wins.** Phase-8-*new* and *owned* here: the gate/trigger/head encoding, the frontier ordering by
> measured GD-fire-fraction, the energy-meter breakdown, the metered-80/20 stack, and the array schema.

---

## §B — The metric dictionary (PINNED; Phase-8 additions in **bold**)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| **accuracy-held** | live-stream final AA, vs the **oracle-cadence** baseline (the achievable reference) + the **always-pay** ceiling | acc, median [IQR] |
| continual **BWT / AA / forget** | GEM/CL conventions (`acc_matrix_metrics`) **on the LIVE loop**, **evaluated at the awake gate's worst mid-stream point (pre-sleep) for the P8.6 safety gate** (post-sleep hides the awake forgetting); vs oracle/frozen baseline; + paired-sign veto | acc / acc-delta |
| **GD-fire-fraction** `f` | fraction of stream steps that trigger a namer update (op (c)); `f*=0.25` a reference line | fraction ∈ [0,1] |
| **MTD** | mean stream-steps from a *known real*-drift onset to detection (true-positives only) — detection delay | steps, median [IQR] |
| **FAR** | fires on the **nuisance** segment (no real drift) per unit stream, vs the **stationary-segment floor** (per arm) | fires / step |
| **MTFA** | mean steps between fires on the **stationary** segment (each detector's empirical floor / δ guard) | steps |
| **hardware energy** `E` | behavioral ADC-centred per-op tally (`n_MAC·e_MAC + n_ADC·e_ADC(bits) + n_write·e_write + n_solve·e_digital`); **the MAC+solve sub-terms reduce to `readout_cost` under unit energies** (ADC/write are net-new terms, not reduction targets) | relative-E (tagged model + params) |
| **metered 80/20** | `GD-share = E[(c)+(d)]/E_total`; `SCFF-share = E[(a)+(b)]/E_total`; + `bp_ratio` vs the BP energy model | fraction + ratio |
| **live SCFF drift** | `bulk_drift` = `cos(rep_t, rep_{t+Δ})` of fixed probes across the stream (P6.5 measurement) | cosine vs step |

**The verdict cuts (PINNED, blind — the design §2.4 cuts, restated as the reporting contract):**
- **Gate frontier (primary):** accuracy-held vs GD-fire-fraction `f`, FAR the third axis, vs the **oracle-cadence**
  reference. **Committed-eligible** = at the frontier knee: accuracy-held within `δ_acc=0.02` of the oracle (paired), low
  `f`, FAR at/below the stationary floor. **`f*=0.25` is a REFERENCE LINE, not a binary pass/fail** (a gate at `f=0.30`
  holding accuracy at low FAR beats one at `f=0.24` that drops accuracy). Failure modes (over/under/false-fire) logged.
- **FAR / false-fire (all arms):** vs each detector's **own stationary-segment fire-rate** (the empirical floor from
  `detector_far_guard`), **not** a private nominal δ. A false fire = a fire on the **nuisance** segment.
- **Trigger:** `earns-early` iff `MTD(tap) < MTD(error)` **AND** `FAR(tap,nuisance) ≤ FAR(error,nuisance)`; else
  `early-but-noisy` or `no-lead`. The magnitude-of-shift null is *expected* to show high FAR (the spine demonstration).
- **RanPAC-vs-SLDA:** commit SLDA iff `E(RanPAC)/E(SLDA) ≥ 2` **AND** `|AA(RanPAC)−AA(SLDA)| ≤ 0.02` with **both AA freshly
  measured on the LIVE loop** (not P7's frozen tie); else keep RanPAC.
- **Metered 80/20:** "confirmed" iff `GD-share ≤ 0.25` with the committed gate on; reported with `bp_ratio` vs the
  **BP+replay energy model at matched retention, same substrate table** (not a naive backward-every-step BP).
- **A6 live-safety (P8.6):** `BWT` measured **at the awake gate's worst mid-stream point (pre-sleep, NOT post-sleep)** —
  not negative vs baseline in ≥4/5 paired seeds (veto) **AND** `AA` within `δ_acc` of the frozen promise.

**No result may be narrated into a branch it does not numerically satisfy.**

**Calling a difference real (n=5; carry):** real only if **IQR-disjoint at the final checkpoint** *and* **sign consistent
in ≥4/5 paired seeds.** At the P8.6 gate "within noise" is NOT an auto-pass — the paired-sign veto applies. Decisive gaps
≤ 0.02 get **9 seeds**; A6 re-checks run the full 5, never 3.

**Threats-to-validity, reported every rung (the §4 carry):** (a) the energy meter is a **behavioral model** — log + cite
its per-op params, sensitivity-check the ADC-dominance assumption; (b) FAR depends on the **nuisance injector** — a too-weak
injector makes "no false fires" vacuous; calibrate it at the **raw-input / early-tap level** (prove the pixels genuinely
shifted) *and separately* show the SCFF output's **class direction** barely moved (two measurements — SCFF invariance
would otherwise mask a weak injector); (c) **calibration-under-shift** for any error/confidence trigger (the direction
trigger sidesteps it); (d) the **oracle baseline uses known boundaries** the detector
can't see — matching it is the *win*, not a loss.

---

## §C — The figure catalog (declare which you emit; never invent)

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **GATE-BAKEOFF** *(headline)* | `fig_gate_bakeoff` | **left:** accuracy-held × GD-fire-fraction frontier, one point per gate arm, ordered by `f`, oracle + always-pay refs, **FAR as marker size/colour**; **right:** scorecard bars (accuracy-held · f · FAR · MTD) | where does accuracy-held peak at the lowest fire-cost without false-firing |
| **TRIGGER** | `fig_trigger` | MTD × FAR scatter — error-EMA (ref) vs **tap-drift-direction** (candidate) vs **tap-drift-magnitude** (null) vs DriftLens vs STUDD; accuracy-held annotated | does the class-direction tap trigger lead error (low MTD) without false-firing (low FAR); does the magnitude null false-fire |
| **CADENCE** | `fig_cadence` | accuracy-held **and** worst-point A6-BWT vs sleep-frequency × history-fraction × `λ_ema` | the cheapest cadence + history + `λ_ema` that holds the A6 win; where the ~90 % staleness bites |
| **COST-METER** | `fig_cost_meter` | stacked per-op energy bars (MAC/ADC/write/solve), RanPAC vs SLDA, ADC term highlighted | is no-gradient cheap on the substrate; does SLDA displace RanPAC |
| **METERED-8020** | `fig_metered_8020` | GD-share vs SCFF-share stacked bar, vs the **BP+replay** energy model (matched retention, same substrate) | the first honest 80/20; how it compares to always-pay + BP+replay |
| **DRIFT** | `fig_drift` | **left:** `bulk_drift` cos vs stream-step (live); **right (P8.0 drift-visibility):** the class-direction signal + error-rate at **real-onset vs nuisance-onset** markers | how fast the bulk drifts + "bulk doesn't forget"; **is the detection problem well-posed** (signals move at real not nuisance onsets; error-rate ≠ tap-drift) |
| **CONT-SAFETY** *(the live A6 gate)* | `fig_cont_safety` | BWT / AA / forget bars **at the worst mid-stream point (pre-sleep)**, live vs oracle/frozen baseline (+ paired-sign veto marker) | does the LIVE mechanism keep the A6 win **where the awake gate is worst** (not just post-sleep) |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples: partial-fit-equiv ✓ · live-path-anchor ✓ · scff-static-frozen ✓ · meter-proxy ✓ · detector-FAR-floor ✓ · cache-replay ✓ · FD ✓ · fire-counts | guards + apparatus sanity + the fire economy at a glance |

**Caption rule (every figure):** one sentence ending with **the takeaway** (not a description), then `(n=5, task, …)`. An
**accuracy-held** caption always names the **oracle-cadence** reference and the **always-pay** ceiling. A **cost/energy**
caption always tags the **meter model + params** and never asserts a Joule it can't source. A **gate** caption reports
**FAR alongside accuracy-held** (a gate is not "solved" on accuracy alone). Model caption:

> *"The label-free tap-drift gate held accuracy-held within 0.0X of the oracle (0.AA vs 0.OO) at fire-fraction 0.FF while
> false-firing at FAR 0.0Y on the nuisance segment — committed-eligible / early-but-noisy. (n=5, live CI+nuisance stream)"*
>
> *(Letters are deliberate placeholders — the caption teaches the shape, never an expected result. Do not anchor on any
> number; the §0.3 hypotheses are not findings.)*

---

## §D — Table schemas (fixed columns; one IQR format; no bare means)

**IQR format fixed everywhere: `median [q25–q75]`** (two decimals). Never a bare mean.

**The RESULTS.md ledger — one section per rung; header states locked controls (`task, stream, seeds, gate/head`); last
column = a ≤6-word verdict; one variable swept per table (the swept variable is the first column):**

| rung | columns (after the swept variable) |
| --- | --- |
| P8.0 | `control/guard · value · vs-reference · pass? · verdict` *(guards + bulk-drift + always-pay/oracle refs)* |
| P8.1 | `gate · accuracy-held · GD-fire-fraction · FAR · MTD · vs-oracle · verdict` *(gate arm swept)* |
| P8.2 | `trigger · MTD · FAR · accuracy-held · lead? · verdict` *(trigger arm swept)* |
| P8.3 | `cadence×history · accuracy-held · sleep-cost · A6-BWT · verdict` |
| P8.4 | `head · E_total · E_adc · E_solve · AA(live) · E-ratio · verdict` *(RanPAC vs SLDA)* |
| P8.5 | `config · GD-share · SCFF-share · bp_ratio · verdict` |
| P8.6 | `mechanism · AA · BWT(+paired-sign) · forget · vs-baseline · verdict` |

**Struck tables (a struck gate/trigger/cadence):** identical schema, with the failure condition + the **mechanistic
reason** in the verdict column — a struck arm gets the same rigor as a win (failures are data: a gate that over-fires, a
trigger that false-fires on nuisance, a cadence too sparse to hold BWT).

---

## §E — The summary writing contract (the 8 slots — fill verbatim, formal voice)

Every `expK/experiment-K.md` *Read* section fills these 8 slots in order, none empty (if "n/a", say *why*):

1. **Claim** — one falsifiable sentence.
2. **Headline number** — median **[IQR]**, against the references (the **oracle-cadence** baseline *and* the **always-pay**
   ceiling for accuracy; the **BP energy model** for cost). Never a bare number.
3. **Figures** — the catalog refs emitted, each one line; name the headline figure.
4. **Mechanism** — *why* the number is what it is (the spine: is the gate firing on **drift/direction** or leaking a
   **magnitude**? does the label-free trigger *lead* error, and why? which op dominates the metered energy — ADC? solve?).
5. **Threats to validity** — the §4 carry (behavioral meter params; nuisance-injector strength; calibration-under-shift;
   the oracle baseline uses hidden boundaries); the methodology rule-1 check, written in.
6. **Decision** — which open knob this **sets** (the committed gate / trigger / cadence / cost-head), and what the next
   rung inherits.
7. **Economy-honesty** — the cost number's **meter model + params are stated** (not a bare Joule); the **FAR** is reported
   beside accuracy (a gate is not "solved" on accuracy alone); the **metered 80/20** replaces the proxy tag only where the
   meter actually ran.
8. **Live-safety / namer-verdict** — what this rung says about the **live A6 continual-safety (P8.6)** and the committed
   namer (RanPAC kept, or SLDA committed on metered cost). A rung that moves neither the gate/cadence choice nor the cost
   verdict nor live-safety shouldn't have run.

**Voice rules:** declarative past-tense for what happened; present-tense for standing reads; **no hedging filler, no
first-person, no exclamation**; every adjective backed by a number or dropped; a struck result stated plainly ("the
tap-drift gate false-fired on the nuisance segment in 5/5 seeds — FAR above the ceiling regardless of its early
detection"). **Continuity:** each card opens by naming the knob it inherits ("Inheriting the committed RanPAC head + the
oracle-cadence baseline from P8.0, …"). A skipped conditional rung is a one-line skip-card naming the gap-test that closed
it.

---

## §F — Gold-standard worked card (copy this skeleton; the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches the
> shape, voice, and completeness, never an answer.*

```markdown
# P8.1 — The gate bake-off: when does the namer fire?

**Question.** Across the gate taxonomy, which detector holds accuracy-held within δ_acc of the oracle-cadence baseline at
the lowest GD-fire-fraction, without false-firing on nuisance drift?

**Setup.** Swept variable = the gate ∈ {always-pay, oracle-cadence, absolute-θ, DDM, ADWIN, budget-gate}; controls locked
(live NoiseAugContrast bulk, committed RanPAC+cbrs head, CI+nuisance stream, seeds [42,137,271,314,1729], error-EMA
trigger). GATE-BAKEOFF + INV. Apparatus: p8lib awake_sleep_loop (streaming mode); guards passed (partial-fit-equiv;
live-path-anchor ≡ oracle bit-for-bit; scff-static-frozen ≡ P7 static; meter-proxy; detector-FAR floor; cache-replay; FD < 1e-5).

**Run.** G gates × 5 seeds, checkpointed (_ckpt.jsonl); live SCFF + gated head. Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| gate | accuracy-held | GD-fire-fraction | FAR | MTD | vs-oracle | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| always-pay (ceiling) | 0.CC [..–..] | 1.00 | — | — | +0.0x | cost ceiling |
| oracle-cadence (ref) | 0.OO [..–..] | 0.oo | 0.00 | 0 | (ref) | achievable reference |
| DDM | 0.AA [..–..] | 0.ff | 0.0y | m | <within δ_acc?> | <committed-eligible?> |
| ADWIN | 0.BB [..–..] | 0.gg | 0.0z | m2 | <within δ_acc?> | <over/under-fire?> |
| budget-gate | 0.DD [..–..] | 0.hh | 0.0w | m3 | <?> | <spine-flagged> |
- **GATE-BAKEOFF** (headline): <where accuracy-held peaks at lowest f; which arms are greyed by the accuracy cut>.
  - **INV**: partial-fit-equiv ✓, live-path-anchor ✓, scff-static-frozen ✓, meter-proxy ✓, detector-FAR-floor ✓, cache-replay ✓, FD ✓.

**Read (8 slots).**
1. *Claim* — DDM holds accuracy-held within δ_acc of the oracle at f ≤ 0.25 without false-firing.
2. *Headline* — DDM 0.AA [IQR] vs oracle 0.OO and always-pay 0.CC, f=0.ff, FAR=0.0y (n=5, live CI+nuisance).
3. *Figures* — GATE-BAKEOFF (frontier + scorecard), INV (guards green).
4. *Mechanism* — if DDM held: the two-threshold error gate fires on the *harmful* stall (new class), coasts otherwise.
5. *Threats* — (a) FAR depends on the nuisance-injector strength (calibrated in P8.0); (b) oracle uses hidden boundaries;
   (c) "real" only if IQR-disjoint + ≥4/5 sign.
6. *Decision* — sets the candidate committed gate (pending the P8.2 trigger + P8.6 live-safety); next rung inherits it.
7. *Economy-honesty* — FAR reported beside accuracy; cost is the fire-fraction proxy here (the energy meter is P8.4).
8. *Live-safety* — A6 not yet re-checked live → P8.6 gates adoption.
```

This is the bar: every slot filled, IQR in every cell, both accuracy references named, FAR beside accuracy, the guards
green. A card that looks like this *cannot* be the messy output the contract prevents.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

- [ ] **Median [IQR]** for every headline number (n=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) — no bare means.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 by sign) before any gap is claimed; else "within noise."
- [ ] Every **accuracy-held** figure names the **oracle-cadence** baseline + the **always-pay** ceiling; **FAR reported
  beside accuracy** on every gate figure (a gate is not "solved" on accuracy alone).
- [ ] **Verdict branch matches its numeric cut** (§B): gate = **frontier position** (accuracy-held within δ_acc of oracle
  at low f + FAR ≤ stationary floor; `f*=0.25` a reference line, **not** binary), trigger (earns-early / early-but-noisy /
  no-lead, FAR vs the error ref), RanPAC-vs-SLDA (E-ratio ≥ 2 ∧ **live-measured** AA within δ_acc), 80/20 (GD-share ≤ 0.25
  + bp_ratio), live-safety (**worst-point** BWT veto). No result narrated into a branch it doesn't satisfy.
- [ ] **The cost meter is tagged a BEHAVIORAL model** with its per-op params + **citations** in the manifest; the
  ADC-dominance assumption is sensitivity-checked; no bare Joule asserted; the **MAC+solve sub-terms reduce to
  `readout_cost`** under unit energies (ADC/write are net-new terms, not reduction targets) — the guard is green.
- [ ] **The metered 80/20** is `GD-share` vs `SCFF-share` + `bp_ratio` vs **BP+replay at matched retention, same substrate
  table** (not a naive BP that forgets); the proxy tag is replaced **only where the meter actually ran** (P8.4/P8.5).
- [ ] **The nuisance injector is calibrated at the raw-input / early-tap level** (pixels provably shifted) **AND** the SCFF
  output's class direction shown to barely move — two measurements (else "no false fires" is vacuous, masked by SCFF
  invariance); the per-arm **stationary-segment FAR floor** is established (`detector_far_guard` green).
- [ ] **The live-drift** (`bulk_drift`) + the **drift-visibility panel** are reported at P8.0: signals move at **real**
  onsets and **not** at nuisance onsets; error-rate and tap-drift shown to measure **different** things; the "bulk doesn't
  forget" read stated; if drift is fast, the economy is flagged drift-bound (→ N2/Phase-9 mandatory).
- [ ] **P8.6 the GATE runs 5 seeds** (never 3) on the **live** loop, BWT **measured at the awake gate's worst mid-stream
  point (pre-sleep, NOT post-sleep)**; baseline = oracle/frozen; "within noise" is NOT an auto-pass — the **paired-sign
  veto** (worst-point negative-BWT in ≥4/5) applied; AA within δ_acc of the frozen promise.
- [ ] **Spine reported:** the committed gate trigger fires on **class-direction drift**, not a confidence magnitude **and
  not a raw magnitude-of-shift** (the tap-drift-magnitude null is expected to false-fire — the demonstration); error-rate
  is the labeled reference, not a spine exemplar; the budget-gate's spine-tension is flagged.
- [ ] Every figure drawn by a **`plot_p8.fig_*`** function (no inline styling); caption ends with the takeaway + `(n=…, …)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); formal voice; the card opens by naming the inherited knob.
- [ ] **`manifest.json`** (git hash, config, seeds, versions, wall-clock, **meter per-op params + citations**) **+
  `arrays.npz`** written; **`plot_p8.py regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards logged:** `partial_fit_equiv` (`N`×partial_fit@λ=1 ≡ batch fit, bit-for-bit) · `live_path_anchor`
  (`awake_sleep_loop` block-mode, always-pay, sleep-every-boundary, SCFF-training-ON ≡ `continual_safety_heads`
  bit-for-bit) · `scff_static_frozen` (SCFF-update-off after `train_cell` ≡ P7.0/P7.1 **static** bake-off) · `meter_proxy`
  (MAC+solve ≡ `readout_cost` under unit energies) · `detector_far` (per-arm stationary floor) · `cache_replay`
  (**non-trivial-fire** arm ≡ cache replay) · `fd_head_grad < 1e-5` (budget-gate). **Any guard fails → STOP.**
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874
  guards; **no sklearn / no River** for compute; the real PID verified alive on multi-hour live cells.
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **struck** gate/trigger/cadence logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P8.0** bench + guards + drift + controls | DRIFT (live bulk-drift), INV (all 5 guards + always-pay/oracle refs) |
| **P8.1** gate bake-off | **GATE-BAKEOFF** (frontier + scorecard, greyed sub-cut arms), INV |
| **P8.2** trigger | **TRIGGER** (MTD × FAR, error vs label-free), INV |
| **P8.3** sleep cadence | **CADENCE** (accuracy-held & A6-BWT vs frequency × history), INV |
| **P8.4** cost meter | **COST-METER** (per-op breakdown, RanPAC vs SLDA), INV |
| **P8.5** metered 80/20 | **METERED-8020** (GD/SCFF share vs BP model), INV |
| **P8.6** assembled + A6 | **CONT-SAFETY** (live, vs oracle/frozen + veto) + GATE-BAKEOFF + METERED-8020 (assembled) + the committed economy + the Stage-2/P9 brief |

## Grounding (what the field does — and what we adopt)

- **Drift-detection metrics** (MTD/MTFA/FAR/MDR; the benchmark [2606.07789]) → the §B metric dictionary + the false-fire axis.
- **The gate = off-the-shelf drift-detection** (DDM/ADWIN; ADWIN-U + STUDD [2103.00903] for label-free) → the GATE-BAKEOFF + TRIGGER arms.
- **The cost meter = a behavioral ADC-dominated CIM macro-model** (NeuroSim/ISAAC/PUMA; AIHWKit) → COST-METER + METERED-8020.
- **Representation/semantic drift on a moving backbone** (online-CL feature drift; REMIND; SDC/LDC the road-not-taken) → DRIFT + the sleep framing.
- **Budgeted halting** (Skip-RNN [1708.06834]; PonderNet [2107.05407]) → the learned budget-gate + the north-star hand-off.
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 discipline — carried from Phases 1–7 ([`../result-format.md`](../result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to this catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent.
