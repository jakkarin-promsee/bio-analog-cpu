# Phase 11 — Result format (the binding presentation contract)

> **Not advisory** — the spec the run code and write-up conform to, the way [`design.md`](design.md) is the spec the
> experiments conform to. **If a rung's output can't be produced by the rules below, the rung isn't done.** It
> **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) **and the P8/P9/P10 machinery**
> ([`../phase8/result-format.md`](../phase8/result-format.md) · [`../phase9/result-format.md`](../phase9/result-format.md) ·
> [`../phase10/result-format.md`](../phase10/result-format.md) — the substrate encoding, the meter, the live-loop/freeze
> contracts, the fight/gauntlet/stream/Pareto figures) — and **adds only the Phase-11 delta**: the LIMIT-MAP, the
> decomposition, the generalized per-arena STREAM view, the scaling/crossover figures, the FLOOR cell state, the
> real-stream instruments (no-change baseline, balanced accuracy, composition strip, anchors), and the arena ledger.
> **Canonical wins on any shared constant; P8 on economy/meter; P9 on live-loop/freeze; P10 on fight/gauntlet/stream;
> this file owns only the P11-new.**

---

## §0 — The three enforcement mechanisms (carried)

1. **One plotting module — `plot_p11.py` — ONE function per figure code**; `plot_p11.STYLE = {**plot_p10.STYLE,
   **P11_NEW}`; no rung styles matplotlib inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice.**
3. **One ledger schema + one regeneration path** — `RESULTS.md` rows per §D; `plot_p11.py regen <run-dir>` redraws
   every figure from `arrays.npz`. A figure you can't regenerate from saved data is a screenshot, not a result.

> **The rule of additions:** a rung needing a new figure/metric adds it HERE first — never a one-off.

---

## §A — Locked visual constants (P11 delta; everything else inherited)

**P11-new entities (colour · style — fixed forever):**

| entity | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **OURS Arm A** (frozen recipe, porthole) | `#0b8f6a` (teal) | solid, thick; ⭐ ring on scatter | the committed recipe on foreign data — always plotted where it runs |
| **OURS Arm B** (recipe instance) | `#0b8f6a` (teal) | **dashed**; open circle on scatter | the pre-registered scaled instance — never presented as "the frozen object" |
| **proj→namer** (the strike cell) | `#4d7ea8` (steel blue) | solid, square | the no-bulk decomposition arm (P11.1; carried into real streams) |
| **random-frozen-bulk→namer** | `#4d7ea8` (steel blue) | dotted, square | the reservoir control (dim-matched) |
| **no-change / persistence** | `#555555` (dark grey) | dash-dot, no marker | the streaming community's trap-check — mandatory line on every real-world stream |
| **published anchor** (Vergara / van-de-Ven band) | `#b8860b` (dark goldenrod) | horizontal band / dashed line | transcribed-at-bench literature numbers — an overlay, never a racer |
| ER-strong / ER-budget / A-GEM / DER++ / GDumb / naive-BP / chance / ceiling / sleep ticks / domain-boundary | — | **inherited from P10 §A verbatim** | the opponent field + references |

**LIMIT-MAP cell encoding (the phase money figure):** **win** = teal fill · **tie** = light grey-teal fill ·
**loss** = light magenta fill · **FLOOR** = grey hatch (uninformative — §B criterion; NEVER counted or captioned as
a tie). Every non-FLOOR cell carries its number + the fraction-of-ceiling annotation; Δbulk overlay (small ▲/▼) on
arenas where P11.1's decomposition ran. Columns = arenas in ladder order (digits → MNIST → Fashion → CIFAR-gray →
cross-dataset → gas → HAR → electricity → covertype → [yearbook] → [features]); rows = capability channels (home
AA · safety worst-BWT · retention rapid-switch · retention long-block · order-invariance · noise (where battery
applies) · energy same-substrate · substrate total · throughput). Un-run cells are blank (absent), not FLOOR.

**Required `plot_p11.py` API (one function per figure; signatures fixed):**

```
STYLE                      # {**plot_p10.STYLE, **P11_NEW}; the ONLY place P11 styling lives
fig_limit_map(run)         # F: LIMIT-MAP   (P11.9 — THE phase money figure: arenas × channels, 4-state cells + numbers + ceiling-fractions + Δbulk overlays)
fig_decomp(run)            # F: DECOMP      (P11.1 — Δbulk bars per channel; proj→namer vs bulk→namer vs reservoir vs no-sleep; budgets annotated per cell)
fig_stream(run, arena)     # F: STREAM-<arena> (EVERY arena — the per-batch view: live-batch prequential + seen-so-far + sleep ticks + onsets + cumulative energy; + no-change line & anchor band & composition strip where the arena has natural blocks; the GAUNTLET_STREAM_LONG treatment, generalized)
fig_scaling(run)           # F: SCALING     (P11.6/P11.5 — 4 panels vs scale (W · D · C · stream length): accuracy · GD-share (with the bench-pinned meter-derived shape overlaid) · substrate factor · Δbulk-where-measured)
fig_crossover(run)         # F: CROSSOVER   (P11.5 — analytic bytes-vs-C curves (replay dilution vs prototype+Gram growth) + measured points C=10/20[/100])
fig_fight(run) · fig_pareto(run) · fig_gauntlet(run) · fig_inv(run)   # carried from plot_p10 per arena (FIGHT/PARETO/GAUNTLET/INV)
regen(run_dir)             # redraws every figure whose arrays are present — the citable path
```

**The `arrays.npz` schema (P11 delta — a rung emits the subset its figures need; P8–P10 keys carried):**

| key | shape | meaning |
| --- | --- | --- |
| `arenas` | `[A]` (str) | the arena columns present in this run |
| `cellstate_<channel>_<arena>` | scalar (str) | win/tie/loss/FLOOR + the §B criterion inputs (`ceiling_<arena>`, `chance_<arena>`, `nochange_<arena>` where real) |
| `dbulk_<channel>[_<arena>]` | `[S]` | the decomposition delta per channel (P11.1; carried arenas) |
| `acc_<learner>_<arena>` · `balacc_…` · `energy_…` · `bwt_…` · `aaa_…` | `[S]` | the per-arena fight set (balanced-accuracy keys on imbalanced streams) |
| `ceiling_<arena>` | `[S]` | the per-arena joint-BP ceiling (accuracy-axis reference) |
| `nochange_<arena>` | `[S]` | the persistence baseline (real streams) |
| `anchor_<name>` | scalar/band | transcribed published numbers (bench manifest sourced) |
| `stream{live,seen,cume,sleeps,fires}_<cfg>_<arena>` · `stream_onsets_<arena>` | `[S,N]` / `[D]` | the per-batch STREAM view keys, generalized from P10's gauntlet-stream set |
| `orderdelta_<cfg>_<arena>` | `[S]` | |AA(fwd) − AA(rev)| where a reversed run exists |
| `retention_<cfg>_<arena>_<regime>` | `[S,D,D]` | acc-matrix per switch regime (rapid-24 / long-randomized) |
| `composition_<arena>` | `[D,C]` | the per-block class-composition table (bench artifact, drawn as the strip) |
| `condnum_<cfg>_<arena>` | `[S,nsleep]` | namer covariance condition number at each sleep (volume / cross-dataset watch) |
| `scale_axis` · `acc_vs_scale` · `gdshare_vs_scale` · `gdshare_pinned_shape` · `substrate_vs_scale` | `[K]` / `[S,K]` | the SCALING panels + the bench-pinned meter-derived GD-share shape |
| `crossover_analytic` · `crossover_measured` | `[·,2]` | bytes-vs-C curves + measured points |
| `inv_<panel>` | `[S,…]` | INV: all carried guards + arena-data ✓ anchor ✓ floor-criterion ✓ recipe ✓ porthole ✓ no-change ✓ budget-report ✓ + fire/sleep counts + condition trace |

---

## §B — The metric dictionary (P11 additions; P8–P10 carried unchanged)

| metric | definition (pinned — do not redefine per rung) | units |
| --- | --- | --- |
| **Δbulk** | (bulk→namer) − (proj→namer) per capability channel; budgets REPORTED per cell (not matched — removing the bulk removes its cost; a tie-at-lower-cost is stated as the strike landing twice) | acc-delta |
| **balanced accuracy** | mean per-class recall; replaces accuracy where the composition table shows >3:1 imbalance (gas; per-table) | acc |
| **no-change baseline** | predict-previous-label; mandatory on every real-world stream | acc |
| **fraction-of-ceiling** | AA / joint-ceiling-AA per arena; annotated in every non-FLOOR accuracy cell | fraction |
| **order-invariance Δ** | \|AA(fwd) − AA(rev)\| per learner per arena | acc-delta |
| **cell state** | **FLOOR** iff (a) ceiling < chance + 5·δ_acc, or (b) all raced learners < chance + 2·δ_acc, or (c) real stream: none beat no-change + δ_acc — else win/tie/loss by the P10 real-difference rule | categorical |
| **length invariants** | LUT churn · gate fire-rate · GD-share drift · namer condition number per sleep | traces |

**The verdict cuts are design §2.4, restated as binding** (δ_acc = 0.02; paired seeds; balanced accuracy where
pinned; heavy live cells 3 seeds declared). **No result may be narrated into a branch it does not numerically
satisfy. A FLOOR cell may not be captioned as parity.**

**Threats-to-validity, reported every rung:** P10 (a)–(h) carried + P11 (i)–(vi) (projection loss bounded by Arm B;
stream-order provenance stated; Dennler-2022 gas limitations cited; anchors transcribed pre-run; natural-order
streams vary init/projection seeds only; NTE asymmetry stated per arena) — design §4.

---

## §C — The figure catalog (declare which you emit; never invent)

| code | function | the question it answers |
| --- | --- | --- |
| **LIMIT-MAP** *(P11.9 headline)* | `fig_limit_map` | where does the object hold, where does it break, where is the data floor — every "but does it…" at once |
| **DECOMP** *(P11.1 headline)* | `fig_decomp` | is the architecture more than its closed-form namer (the strike-1 answer) |
| **STREAM-<arena>** *(EVERY arena)* | `fig_stream` | the sleep mechanism batch-by-batch, good and bad — sags, recoveries, gate fires, energy staircase; prequential accuracy in the streaming field's own read |
| **SCALING** *(P11.5/P11.6)* | `fig_scaling` | do the economy/substrate/safety curves survive scale while accuracy does whatever it does — vs the bench-pinned predicted shape |
| **CROSSOVER** *(P11.5)* | `fig_crossover` | at what class count does prototype+Gram memory beat a byte-matched replay buffer (either direction) |
| **FIGHT / PARETO / GAUNTLET / INV** | carried P10 functions | per-arena fight, frontier, retention money figure, guards |

**Caption rules (P10 carried + P11-new):** every real-stream caption names the **no-change baseline** and (where
transcribed) the **published anchor**; every accuracy caption names the **per-arena ceiling**; a FLOOR cell's caption
says *"uninformative at this arena (floor criterion …)"* — never "tie"; an Arm-B caption names the recipe instance
(D/W) and that it is **not** the frozen committed object; a cross-dataset caption states class-IL 30-way (harder than
the field's task-IL convention). Every caption ends with the takeaway + `(n=…, arena, …)`.

---

## §D — Table schemas (fixed columns; `median [q25–q75]`; no bare means)

| rung | columns (after the swept variable) |
| --- | --- |
| P11.0 | `guard · value · vs-reference · pass? · verdict` *(arena-data per set · anchors transcribed · ER-tuning grids pinned · P11.6 shape pinned · floor criterion pinned · wall-clock pre-estimates)* |
| P11.1 | `cell · homeAA · worstBWT · gauntlet-worst · noise-chan · energy · Δbulk-vs-proj · verdict` |
| P11.2 | `protocol · learner/arm · (bal)acc · AAA · worstBWT · retention(rapid/long) · orderΔ · anchor-in-band? · verdict` |
| P11.3 | `stream · learner/arm · balacc · AAA · worstBWT · worst-retention · vs-no-change · energy · verdict` |
| P11.4 | `arm · final30 · per-block-final · worst-retention · orderΔ · condnum-max · LUT-composition · verdict` |
| P11.5 | `rung/C · learner/arm · (bal)acc · worstBWT · retention · ceiling-fraction · [crossover-C] · verdict` |
| P11.6 | `W or D · acc · GD-share (vs pinned shape) · substrate-factor · worstBWT · invariant-moved · verdict` |
| P11.7 | `arena · learner · FLOPs/sample · critical-rate · demo-AA-at-rate · verdict` |
| P11.9 | `arena × channel · OURS · best-field · state (win/tie/loss/FLOOR) · number` *(the map ledger)* |

Struck/broken/FLOOR rows: identical schema + the mechanistic reason in the verdict column (failures are data).

---

## §E — The summary writing contract (the 8 slots — carried, P11-tuned)

Every `expK/experiment-K.md` *Read* fills, in order, none empty: **1 Claim** (falsifiable) · **2 Headline number**
(median [IQR], vs ER-strong + ceiling + (real streams) no-change; the verdict branch stated) · **3 Figures** (catalog
refs; name the headline) · **4 Mechanism** (why — the spine: directions not magnitudes; sags = frame-staleness;
gate = safety; rotates-not-forgets) · **5 Threats** (§B carry + the P11 (i)–(vi)) · **6 Decision/verdict** (which
branch banks; what the map inherits) · **7 Recipe-honesty** (Arm A bit-equal committed / Arm B recipe-guard diff
clean; verdict shapes pinned blind; anchors transcribed pre-run; nothing tuned) · **8 Where-it-stands** (what this
rung adds to the LIMIT-MAP and the founding claims). Voice rules carried verbatim (declarative, no hedging, every
adjective backed by a number; a loss stated plainly).

---

## §F — Gold-standard worked card (fictional numbers — teaches shape, never an answer)

```markdown
# P11.3-gas — Nature's gauntlet: does the frozen recipe survive 36 months of sensor aging?

**Question.** On the time-ordered gas-drift stream, does OURS hold retention/safety vs a per-arena-tuned ER at
competitive balanced accuracy — or does real drift erase the synthetic-gauntlet differentiator?

**Setup.** Swept = learner/arm ∈ {OURS-A(porthole-40), OURS-B(native-128/W205), er_strong(re-tuned, grid pinned),
gdumb, naive, no-change, proj→namer}; controls locked (batches 1→10 time order; scaler fit batch-1 only; balanced
accuracy per the composition table; seeds vary init+projection only; anchors: Vergara-2012 transcribed at bench;
Dennler-2022 cited). STREAM-gas + FIGHT + INV. Guards green (arena-data: batch order asserted; no-change present;
recipe: Arm-B diff = {D,W,cap} only; budget-report). Verdict shape pinned blind (design §2.4-P11.3).

**Run.** 7 arms × 5 seeds, checkpointed; wall ≈ XX min. *(fictional)*

**Result.** OURS-A worst-point retention 0.RR [..–..] vs ER 0.EE [..–..] (branch: <win/scoped/loss>); balanced-AA
0.AA vs ER 0.BB (Δ −0.0C); no-change 0.NN (beaten by +0.MM → cells informative); AAA 0.SS vs 0.TT; energy 1.KK×
same-substrate. STREAM-gas: <the batch-10 story — sag/recovery/gate pattern>.

**Read (8 slots).** 1 *Claim* — … 2 *Headline* — … (branch stated) … 7 *Recipe-honesty* — Arm A bit-equal committed
(recipe-guard diff empty); shapes pinned blind; Vergara anchor transcribed pre-run; nothing tuned. 8 *Where-it-stands*
— the gas column of the LIMIT-MAP is <colour>; the real-world verdict banks <branch>.
```

---

## §G — The pre-submit checklist (before calling ANY rung "done")

- [ ] Median [IQR] everywhere (n=5; 3 declared on heavy live cells; 9 on decisive ≤δ_acc gaps where seed-able).
- [ ] The real-difference rule applied; **balanced accuracy used where the composition table pins it**.
- [ ] **The FLOOR criterion applied before any win/tie/loss is captioned**; FLOOR never narrated as parity.
- [ ] Every accuracy figure names ER-strong + the per-arena ceiling; real streams also draw **no-change** + anchors.
- [ ] **The anchor guard is green** (our ER inside the transcribed published band) before any r1+ verdict banks.
- [ ] **Arm discipline:** Arm A bit-equal committed config (guard diff empty); Arm B recipe-guard whitelist =
      {D, W, LUT-cap} only; NOTHING tuned per arena; ER-strong's per-arena tuning grid pinned in the manifest.
- [ ] **STREAM-<arena> emitted for every arena run** (A1 — the author's ask); sleep ticks + onsets + no-change +
      cumulative energy present; the P10 replay-guard convention where committed arrays are carried.
- [ ] Stream-order assertions in the manifest (electricity chronological · covertype file order · gas batches ·
      HAR subject blocks · yearbook years); scaler-freeze policy stated per arena.
- [ ] The P11.6/GD-share **pinned shape from the bench derivation** overlaid on SCALING before the measured curve is
      interpreted; a broken prediction is a banked finding, not a re-derivation after the fact.
- [ ] Every figure via `plot_p11.fig_*`; caption ends with the takeaway; 8 slots filled; `manifest.json`
      (+ anchors + composition tables + order assertions + pre-estimates) + `arrays.npz` written; `regen` redraws.
- [ ] Guards logged (all carried + the 7 P11 guards); **any guard fails → STOP**. Single-thread discipline
      (`OMP_NUM_THREADS=1`, `python -u`, PID verified on heavy cells); no sklearn/River for compute (bench-only
      `fetch_openml`); commit per rung.
- [ ] `RESULTS.md` row in the §D schema; broken/FLOOR rows carry their mechanism.

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| P11.0 | INV (all guards + anchors + pinned shapes + pre-estimates) |
| P11.1 | **DECOMP** + INV |
| P11.2 | **STREAM-mnist** + FIGHT + GAUNTLET (both regimes) + anchor row + INV |
| P11.3 | **STREAM-gas** (headline) + STREAM-{har,elec,ctype[,yearbook]} + FIGHT per stream + INV |
| P11.4 | **STREAM-xdata** + retention/order table + condition trace + INV |
| P11.5 | GAUNTLET per rung + **CROSSOVER** + INV |
| P11.6 | **SCALING** (with pinned-shape overlay) + INV |
| P11.7 | the critical-rate table + one STREAM demo + INV |
| P11.9 | **LIMIT-MAP** + SCALING final + the close-out |

> The **floor**. Adapt upward per rung; never below it. A new figure → add it to this catalog first. **The recipe is
> frozen; we measure, and ship the map — wins, losses, and floors.**
