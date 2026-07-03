# Phase 10 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** Handed only a purpose, an agent's output rots four ways — graph formats drift,
> table styles drift, summaries drift, no continuity rung-to-rung. This file removes the freedom that causes all four. It is
> **not advisory** — it is the *spec the run code and the write-up must conform to*, the way `design.md` is the spec the
> experiments conform to. **If a rung's output can't be produced by the rules below, the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) **and the Phase-8 machinery**
> ([`../phase8/result-format.md`](../phase8/result-format.md) — the gate/head/**substrate 2×2** encoding, the ADC-centred
> energy meter, the `arrays.npz`/`manifest.json` discipline) **and the Phase-9 machinery** ([`../phase9/result-format.md`](../phase9/result-format.md)
> — the live-loop / oracle references, the freeze contract) — and **adds only the Phase-10 delta**: the validation figures
> (the existential fight, the cadence-frontier family, the multi-domain gauntlet money-figure with the sleep-position
> overlay, the held-out noise showcase, the Pareto verdict), the P10-new metrics, and the **judged-against-external-baseline**
> contract (the honest inversion of P9's internal-only rule). Read it once; then *obey it*. **Canonical wins on any shared
> constant; P8 wins on any economy/meter/substrate constant; P9 wins on any live-loop/oracle constant; this file owns only
> the P10-new.** *(Kickoff-alignment second review folded 2026-07-03 — the K-deltas below; the binding ledger is design §9.)*

---

## §0 — The three enforcement mechanisms (carried from P8/P9)

1. **One plotting module — `plot_p10.py` — ONE function per figure code.** Every rung calls the *same* function (§C); the
   look lives in one place (`plot_p10.py:STYLE`, which imports `plot_p9.STYLE` — which imports `plot_p8.STYLE` — and extends
   it, never re-defining a shared constant). No rung styles `matplotlib` inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice, with the worked card (§F) as the model.**
3. **One ledger schema + one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D); `plot_p10.py regen
   <run-dir>` redraws *every* figure from `arrays.npz`, never a live run. A figure you can't regenerate from saved data is a
   screenshot, not a result.

> **The rule of additions.** A rung that genuinely needs a new figure/metric **adds it to this file first** (so the next
> rung inherits it) — never a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (P10 delta; the rest inherited from `plot_p9.STYLE` ⊃ `plot_p8.STYLE`)

`plot_p10.STYLE = {**plot_p9.STYLE, **P10_NEW}`. **dpi 300 · figsize {single (6.0,4.0) · wide/frontier (7.5,4.0) ·
panel-strip (10,2.2) · twin-panel (10,4.0)} · DejaVu Sans 10pt · transparent bg · median line + IQR α0.18 / median bar + IQR
whisker · light-grey grid** — all inherited, never re-stated in code. **The P8.7 substrate encoding is inherited verbatim**
(OURS-analog = teal thick ring · OURS-digital = light teal · GD-analog = light magenta · GD-digital = magenta) — the
substrate 3/4-way race reuses it. **P10-new entities (colour · style — fixed forever):**

| entity | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **OURS grid-4** (committed headline) | `#0b8f6a` (teal) | solid, thick, **ring** on scatter | ⭐ the frozen object; the existential-fight point — **always plotted** (never swapped out) |
| **OURS grid-5 / grid-6** (Tier-1) | `#0b8f6a` (teal) | lines: solid (grid-5) / dashed (grid-6); **scatter (§10 E9): filled circle + the grid NUMBER annotated on-point** | the sweet-spot frontier — cheaper viable cadences; grid-5 is the only δ_acc-worst-BWT-eligible *showcase* rep (grid-6 −0.087 fails) |
| **OURS grid-8 / grid-12 / grid-16** (Tier-2) | `#d9690a` (orange) | lines: solid (g8) / dash-dot (g12) / dotted (g16); **scatter (§10 E9): filled circle + the grid NUMBER on-point** | ⚠ the degradation arms (g8 fails the P9 veto; g16 fails accuracy; g12 the 8→16 gap-filler, home stream only) |
| **OURS grid-7 / 13 / 14 / 15** (§10 cliff probes) | `#d9690a` (orange) | **scatter-only (§10 E9): OPEN circle + the grid NUMBER on-point** | characterization probes bracketing the two cliffs (NOT family members; home stream only, P10.2 sweep + P10.6 scatter) |
| **ER-strong** (the fair racer) | `#8a1b8a` (magenta) | solid, circle | ⭐ the load-bearing opponent — tuned experience replay, metered |
| **ER-budget** (FLOPs/bytes matched) | `#8a1b8a` (magenta) | dashed, circle | ER throttled to OURS's budget — the same-budget point |
| **A-GEM** (efficient replay) | `#c98ac9` (light magenta) | solid, square | the compute-efficient BP+replay variant |
| **DER++** (stronger-modern) | `#6a1b6a` (dark magenta) | solid, triangle | the logit-distillation control (byte budget counts logits) |
| **GDumb** (sanity control) | `#7f7f7f` (grey) | solid, diamond | the greedy-balanced "questions-our-progress" control |
| **naive-BP** (the floor) | `#111111` (black) | dotted | the forgetting floor — never the headline (Phase-4's old opponent) |
| **Pareto frontier line** | `#111111` (black) | thin solid, staircase | the non-dominated envelope across (accuracy, energy) |
| **sleep-position marker** | `#bdbdbd` (light grey) | thin vertical tick, α0.5 | ⭐ where a consolidation fires — overlaid on the retention curve (the event that moves accuracy) |
| **domain-boundary marker** | `#7f7f7f` (grey) | thin vertical dashed | a new gauntlet domain arrives (retention/plasticity read) |
| **chance / ceiling** | `#111111` dotted thin / `#111111` dash-dot | — | carried (the floor of floors / the joint-trained ceiling reference) |

Read by role: **teal = OURS (grid-4 ringed = the committed object; Tier-1 solid/dashed)**; **orange = the Tier-2
degradation arms** (they show the scaling break, greyed if they collapse below chance); **magenta family = the BP+replay
opponent** (ER-strong the load-bearing one); **black staircase = the Pareto envelope**; **light-grey ticks = the sleep
events.** **§10 E9 scatter rule (CADENCE-FRONTIER left panel + PARETO):** every cadence point is a **circle in its tier
colour with its grid NUMBER annotated on-point** (probes open-face, grid-4 ringed) — the number IS the sign; the legend
carries only the four tier roles (committed / Tier-1 / Tier-2 / probe) + the field learners, never one entry per grid. **Frontiers order arms by the measured swept quantity** (energy on the Pareto x; cadence on the family sweep),
never by an asserted order; arms failing the accuracy/veto cut are **greyed** (they don't anchor the frontier).

**Required `plot_p10.py` API (one function per figure; signatures fixed):**

```
STYLE                        # {**plot_p9.STYLE, **P10_NEW}; the ONLY place P10 styling lives
fig_fight(run)               # F: FIGHT            (P10.1 — the existential fight: accuracy AND energy, OURS(grid-4) vs the racer field)
fig_cadence_frontier(run)    # F: CADENCE-FRONTIER (P10.2 — the 5-grid family on accuracy × energy × worst-BWT; Tier-1 knee, Tier-2 break; + the per-domain small-multiple strip when P10.3 per-domain grid arrays are present — K7)
fig_gauntlet(run)            # F: GAUNTLET         (THE money figure — twin panel: all-prev retention (+ sleep-overlay + domain markers) AND cumulative energy, OURS headline lines vs BP; optional one-interval zoom inset: trough → sleep → recovery)
fig_gauntlet_stream(run)     # F: GAUNTLET-STREAM  (§10 ext — the per-BATCH training-curve view: live-batch acc + seen-so-far acc (OURS g4 vs ER-strong) over the stream, sleep ticks + domain onsets; twin panel with the per-batch prefix-priced cumulative energy)
fig_gauntlet_stream_rev(run) # F: GAUNTLET-STREAM-REV (§10 E6 — the identical view on the REVERSED domain order {noised→identity}; answers "is ER's low start real" + "is the late drop noise- or position-specific"; completes K9's ER-on-reversed-stream letter)
fig_gauntlet_stream_long(run)# F: GAUNTLET-STREAM-LONG (§10 E8 — the ALIGNMENT-BREAK view: forward order, per-domain blocks pinned [68,63,56,57,68] (non-multiples of the 24-step sleep period), ~2-3 sleeps INSIDE each domain, switches mid-sleep-interval; answers "was the flat OURS line alignment luck")
fig_substrate(run)          # F: SUBSTRATE        (carried from plot_p8 — the 2×2 {OURS,GD}×{analog,digital}, re-metered across the gauntlet)
fig_noise_showcase(run)      # F: NOISE-SHOWCASE   (P10.4 — directional-retention per held-out environment, OURS-hardened vs BP vs naive)
fig_pareto(run)              # F: PARETO           (THE verdict — the (accuracy, energy) frontier across OURS-family + the field; hero ringed; win/tie/loss regions)
fig_inv(run)                 # F: INV              (every run — guards + fire/sleep-counts + the fair-budget check + the freeze-content check)
regen(run_dir)               # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

Every `fig_*` reads `arrays.npz` + `manifest.json`, draws in `STYLE`, writes a 300-dpi PNG. **No rung draws outside these
functions**, and **every rung writes `arrays.npz` to the schema below.**

**The `arrays.npz` schema (P10 delta — a rung emits the subset its figures need; P8/P9 keys carried):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | seed list (S=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) |
| `learners` | `[L]` (str) | the fight roster — {ours_g4, er_strong, er_budget, agem, derpp, gdumb, naive} (P10.1) |
| `acc_<learner>` · `energy_<learner>` | `[S]` | final AA and metered energy per learner — the Pareto point (P10.1/P10.6) |
| `bwt_<learner>` · `aaa_<learner>` | `[S]` | BWT and average-anytime-accuracy per learner (P10.1) |
| `budget_flops_<learner>` · `budget_bytes_<learner>` | `[S]` or scalar | the fair-budget audit — FLOPs/sample + replay bytes (the anti-strawman) |
| `totalbytes_<learner>` | scalar | total memory (model + optimizer/state + buffer bytes) — **reported** beside the *matched* replay-bytes (threat (h), K6) |
| `acc_joint` | `[S]` | the offline **joint-BP ceiling** — the dash-dot summit reference (accuracy-axis only, never a racer; K1) |
| `orderdelta_<cfg>` | `[S]` | the reversed-order control's AA delta (grid-4 + ER-strong only) — the measured order-sensitivity read (P10.3, K9) |
| `grids` | `[G]` (str) | the cadence family — {g4,g5,g6,g8,g12,g16} (P10.2; g12 = the §10 home-only gap-filler) |
| `acc_<grid>` · `energy_<grid>` · `bwtworst_<grid>` | `[S]` | accuracy × energy × worst-point BWT per grid (P10.2) |
| `tier1_rep` | scalar (str) | the Tier-1 *showcase* representative for the 3-line viz only (grid-4 is always the committed headline, never swapped; a rep is added iff δ_acc-worst-BWT-eligible → grid-5 candidate, grid-6 fails) |
| `domains` | `[D]` (str) | the gauntlet domain sequence (P10.3) |
| `retention_<cfg>` | `[S, D, D]` | the acc-matrix per config (task × eval-point) → new / 1-back / all-prev (P10.3) |
| `plasticity_<cfg>` · `oneback_<cfg>` · `allprev_<cfg>` | `[S, D]` | the three author-asks per domain, per config (P10.3) |
| `cumenergy_<cfg>_<sub>` | `[S, D]` | cumulative metered energy over the stream, per config per substrate (P10.3) |
| `sleep_steps_<cfg>` | `[S, ·]` | the stream-steps where a consolidation fired — the sleep-position overlay (P10.3) |
| `streamlive_<cfg>` · `streamseen_<cfg>` | `[S, N]` | §10 ext — per-BATCH live-batch accuracy (prequential, pre-update) and seen-so-far all-domain accuracy (post-update), N = stream steps (P10.3 GAUNTLET-STREAM) |
| `streamcume_<cfg>_<sub>` | `[S, N]` | §10 ext — per-batch cumulative metered energy (exact prefix pricing of the fires/sleeps masks; final point ≡ the committed total, guarded) (P10.3) |
| `streamsleeps_<cfg>` · `streamfires_<cfg>` | `[S, N]` (bool) | §10 ext — the per-step sleep/fire masks behind the stream view's ticks (P10.3) |
| `stream_onsets` | `[D]` | §10 ext — the step index where each gauntlet domain begins (the onset markers) (P10.3) |
| `streamrev*_<cfg>` · `domains_rev` | as above · `[D]` (str) | §10 E6 — the identical stream-view key set on the REVERSED domain order (`streamrevlive_`, `streamrevseen_`, `streamrevcume_`, `streamrevsleeps_`, `streamrevfires_`, `streamrev_onsets`) + the reversed domain names (P10.3) |
| `streamlong*_<cfg>` · `blocklong` · `longallprev_<cfg>` · `ours_long_aa` · `er_long_aa` | as above · `[D]` (int) · `[S, D]` · `[S]` · `[S]` | §10 E8 — the ALIGNMENT-BREAK stream-view key set (`streamlonglive_`, `streamlongseen_`, `streamlongcume_`, `streamlongsleeps_`, `streamlongfires_`, `streamlong_onsets`) + the pinned per-domain block lengths + the long-stream all-prev retention + final AA per learner (P10.3) |
| `alignedlongallprev_g4` · `ours_alignedlong_aa` · `alignedlongsleeps_g4` | `[S, D]` · `[S]` · `[S, N']` (bool) | §10 E8b — the ALIGNED-long control (OURS g4 only, block 72 = 3× the sleep period): retention + final AA + the sleep mask (verifies the sleeps sit back on the boundaries) — decides E8's mechanism attribution (alignment-luck vs length-effect) (P10.3) |
| `throughput_<cfg>` · `stepsbehind_<cfg>` | `[S, D]` or `[S]` | the Ghunaim real-time read — stream samples a per-step BP+replay drops vs OURS under a fixed wall-clock-per-sample budget (P10.3) |
| `gdshare_<domain>` | `[S]` | the SCFF:Namer ratio per domain — the "final ratio" vs difficulty (P10.3) |
| `noise_envs` | `[E]` (str) | held-out environments — {clean, iid, directional, adc3b, nuisance} (P10.4) |
| `dirret_<learner>_<env>` | `[S]` | directional class-retention per learner per environment (P10.4) |
| `pareto_pts` | `[N, 3]` | columns `[accuracy, energy, is_frontier]` — the verdict scatter (P10.6) |
| `E_ours_<sub>` · `E_gd_<sub>` · `substrate_win` · `algorithm_win_digital` · `total_win` | `[S]` | the P8.7 2×2, re-metered across the gauntlet (SUBSTRATE) |
| `inv_<panel>` | `[S, …]` | INV panels (all P8/P9 guards + `fair_budget` + `freeze_content` + `cadence_family` + `gauntlet_data` + `noise_holdout` + `substrate_identity` + fire/sleep-counts) |

> **Source-of-truth note:** canonical [`../result-format.md`](../result-format.md) Layer A **owns** shared constants (dpi,
> IQR band, the n=5 rule); [`../phase8/result-format.md`](../phase8/result-format.md) owns the economy/meter/**substrate**
> encoding; [`../phase9/result-format.md`](../phase9/result-format.md) owns the live-loop/oracle/freeze encoding; **this file
> owns only the P10-new** (the fight/frontier/gauntlet/noise/pareto figures, the sleep-overlay, the fair-budget audit). If
> they diverge, **canonical > P8 > P9 > P10.**

---

## §B — The metric dictionary (P10 additions in **bold**; P8/P9 metrics carried unchanged)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| continual **ACC / AA** | mean acc over all seen tasks (GEM `acc_matrix_metrics`); the live read is the **worst pre-sleep point per inter-sleep interval** (P9 convention), ER at the same convention — on a **fixed, learner-independent eval-checkpoint grid** (every k steps, k pinned at P10.0), the same OURS-sleep interval boundaries applied to every learner (K12) | acc, median [IQR] |
| **AAA (average anytime accuracy)** | mean over stream-checkpoints of AA(t), AA(t) = mean acc over tasks-seen-so-far at t (origin OSAKA, Caccia `2003.05856`; convention [2308.10328]) | acc, median [IQR] |
| **BWT / Forgetting** | GEM/CL conventions; worst mid-stream point (pre-sleep) for the live veto | acc-delta |
| **FWT** (bonus) | forward transfer (GEM) — does old learning help new tasks | acc-delta |
| **plasticity / 1-back** | acc on task *t* at *t* (plasticity); acc on *t−1* after *t* (1-back, worst pre-sleep) | acc, median [IQR] |
| **the Pareto point** | (accuracy, energy) per learner/grid; efficiency = normalized dist to the (max-acc, min-E) corner | (acc, E) |
| **algorithm energy (load-bearing)** | `E(OURS-digital)` vs `E(ER-digital)` — same digital substrate; the contestable win | relative-E |
| **total energy (headline, floor-flagged)** | `E(OURS-analog)` vs `E(GD-digital)` = substrate × algorithm; the analog factor is a **meter-structural floor**, never the contestable claim | relative-E vs step |
| **throughput / steps-behind** | from the **metered FLOPs/sample** (the same instrument that prices energy; replay + amortized sleep included): declared budget `C_stream` = OURS(grid-4)'s FLOPs/sample; drop-fraction = max(0, 1 − C_stream/FLOPs_L) + relative complexity per learner (OURS 0-behind by construction — declared). **Wall-clock is NOT the instrument** (a python/numpy artifact) — a manifest footnote only (K3) | count / fraction |
| **fair-budget audit** (new instrument) | ER/A-GEM/DER++ **FLOPs/sample** + replay **bytes**, matched to OURS (the anti-strawman) | FLOPs · bytes |
| **SCFF:Namer ratio (GD-share) vs difficulty** | metered GD-share per domain — the "final ratio," characterized | fraction |
| **directional noise-retention** | class-direction retention vs noise level per held-out environment, OURS vs BP vs naive | retention ratio |
| **sleep-position overlay** | the stream-steps a consolidation fired, marked on the retention curve | step markers |
| **substrate / algorithm / total win** | the P8.7 decomposition, re-metered across the gauntlet (`OURS-analog` the hero) | ratio (×), median [IQR] |

**The verdict cuts (PINNED, blind — the design §2.3 cuts, restated as the reporting contract). Phase 10 JUDGES against the
external BP+replay baseline (the honest inversion of P9's internal-only rule) — but the verdict SHAPES are fixed here BEFORE
any baseline number is seen:**
- **P10.0 (bench):** no verdict — the `fair_budget`, `freeze_content`, `cadence_family`, `gauntlet_data`, `noise_holdout`,
  `substrate_identity` guards are green (ER byte-matched + FLOPs-reported + ER-strong's tuning protocol pinned to the
  disjoint tuning stream; freeze **content manifest** + grid-4 bit-for-bit
  (`59d2720` a provenance label, not a git `==`); shared **40-D** input, offline, **bit-identical stream across learners, ONE
  pinned →40 projection**; battery margin-disjoint; `pred_analog ==
  pred_digital` — **scoped to `NoiseModel`-off cells; P10.4's noise arms are the declared exception**) **or STOP.**
- **P10.1 (fight):** the accuracy bar is **ER-strong** (tuned); the energy cut is **same-substrate** (`E(OURS-digital)` vs
  `E(ER-digital)` — the algorithm win; the analog total is a floor overlay). **win** iff `acc(OURS) ≥ acc(ER-strong) − δ_acc`
  (paired) **AND** `E(OURS-digital) < E(ER-digital)` strictly; **honest-Pareto** iff `acc(OURS) < acc(ER-strong) − δ_acc`
  **but** `E(OURS-digital) ≪ E(ER-digital)` (report the ratio + gap; the **accuracy half** is banked "not supported");
  **dominated** iff `acc(OURS) < acc(ER-strong) − δ_acc` **AND** `E(OURS-digital) ≥ E(ER-digital)`. ER-budget is the
  same-FLOPs point; naive-BP the floor; GDumb an accuracy-axis control (energy annotated, not a competitor).
- **P10.2 (frontier):** **grid-4 is the committed headline — never swapped, always plotted.** A Tier-1 *showcase rep*
  (visualization only) may be named iff Pareto-non-dominated **AND** worst-BWT **within δ_acc of grid-4's** (paired) **AND**
  energy IQR-disjointly lower → grid-5 is the only candidate (grid-6 −0.087 fails). Tier-2 break confirmed iff grid-8
  worst-BWT < −δ_acc vs oracle and/or grid-16 acc drop > δ_acc; a Tier-2 hold is a wider frontier.
- **P10.3 (gauntlet):** the retention read is **worst pre-sleep all-prev AA per inter-sleep interval** (the P9 honest
  convention, ER at the same convention). **showcase win** iff worst-point `allprev(OURS)` within δ_acc of ER-strong **AND**
  `E(OURS-digital)` strictly lower at every domain boundary; **scaling limit** iff retention decays with #domains (slope);
  **ratio-not-scale-free** iff GD-share grows with difficulty (flag). AAA + **throughput/steps-behind** reported beside AA.
- **P10.4 (noise, held-out):** **Phase-6 payoff** iff OURS directional-retention beats *both* BP+replay and naive under a
  **genuinely-novel** directional environment; **downgrade to "confirms P9.4"** if the channel is only a re-parameterized
  operating point of the tuned mechanism; **residual bites** iff OURS drops > δ_acc under a held-out channel → **named →
  analog layer** (a scoped hand-off, not a P10 failure).
- **P10.6 (verdict):** the Pareto frontier + the win/tie/loss map, each with its number; the founding bet's **economics** and
  **accuracy** halves banked separately; the Stage-2 close-out. Not a scalar.

**No result may be narrated into a branch it does not numerically satisfy.**

**Calling a difference real (n=5; carry):** IQR-disjoint **at the read point** (final AA for the fight P10.1; **worst
pre-sleep AA per inter-sleep interval** for retention P10.3 — the P9 honest convention, ER at the same convention) **and**
sign-consistent in ≥4/5 paired seeds; else "within noise." Retention re-checks run the full 5 seeds with the paired-sign
veto; decisive gaps ≤ 0.02 get 9.

**Threats-to-validity, reported every rung:** (a) the meter is a **behavioral model** — log/cite per-op params, sensitivity-
check the ADC-dominance; **the analog energy factor is meter-structural — never the contestable claim** (the load-bearing
energy cut is same-substrate `E(OURS-digital)` vs `E(ER-digital)`); (b) the fair fight depends on the **ER budget/tuning** — a
crippled ER makes the win vacuous (match FLOPs+bytes *and* tune ER-strong; report both budget-matched and strong; the tuning
consumes only the **disjoint tuning stream** — seed ∉ raced set — never the raced seeds, K2); (c) the
gauntlet depends on the **domain set + order + the frozen-config-vs-per-domain-tuning asymmetry** (OURS runs a frozen-config
backbone, ER gets its own best per-domain config — state all three; the reversed-order control at grid-4 + ER-strong is
**committed**, K9); (d) synthetic
**overstates** static gaps — A5/natural is the honest read; (e) the noise battery is a **margin-disjoint** operating point of
the same transducer model (guard) — a genuinely-novel channel earns "payoff," a re-parameterized one earns "confirms"; (f)
accuracy is **substrate-independent** (guarded `pred_analog == pred_digital`) — the substrate axis lives only in energy (never
double-count it in accuracy); (g) **GDumb is cost-pathological** (trains from scratch at eval) — reported on the accuracy axis,
annotated on the energy axis, never used to inflate the Pareto; (h) **parameter/memory asymmetry** — OURS's bulk carries more
weights than the racer MLP; the budget matches FLOPs/sample + replay-bytes and **reports** total memory per learner; the
racer's shape is its own `race_bp`-tuned choice, not capped (K6).

---

## §C — The figure catalog (declare which you emit; never invent)

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **FIGHT** *(P10.1 headline)* | `fig_fight` | twin: accuracy bars (OURS-g4 vs ER-strong/ER-budget/A-GEM/DER++/GDumb/naive; the **joint-BP ceiling** dash-dot overlaid — K1) **and** energy bars (same roster, per substrate), δ_acc band + Pareto callout | does OURS match/beat a *budgeted* ER on accuracy at lower energy — and how far is the summit |
| **CADENCE-FRONTIER** *(P10.2)* | `fig_cadence_frontier` | the 5 grids on (accuracy × energy), worst-BWT as marker colour; Tier-1 solid, Tier-2 orange; the knee + the break | where the sizes sit; which Tier-1 rep; where Tier-2 degrades |
| **GAUNTLET** *(THE money figure, P10.3)* | `fig_gauntlet` | **twin panel** — top: worst-pre-sleep all-prev retention vs stream (**grid-4 always + Tier-1 rep + grid-8 + grid-16** OURS lines + BP field, **sleep-position ticks + domain-boundary lines**; optional one-interval zoom inset: trough → sleep → recovery); bottom: cumulative energy vs stream (per substrate); **+ the throughput / steps-behind read** (the Ghunaim real-time payoff); **all five grids run** — the per-domain frontier strip (via `fig_cadence_frontier`) shows the full family per world (K7) | does it learn 5 worlds without forgetting, cheaper than BP and keeping up in real time; when do the sleeps land; which cadence does each world like |
| **GAUNTLET-STREAM** *(§10 ext, P10.3)* | `fig_gauntlet_stream` | **twin panel, x = batch** — top: live-batch acc (thin, prequential) + seen-so-far all-domain acc (thick) for OURS(g4) vs ER-strong, sleep ticks + domain-onset lines; bottom: per-batch cumulative metered energy (exact prefix pricing) | the in-domain vs domain-switch activity — onset dips, sleep recoveries, and where the energy is actually spent, batch by batch |
| **GAUNTLET-STREAM-LONG** *(§10 E8, P10.3)* | `fig_gauntlet_stream_long` | the identical twin panel on the **alignment-break** stream — forward order, per-domain blocks pinned `[68,63,56,57,68]` (~2–3 sleeps inside each domain; switches land mid-sleep-interval, phase drifting) | was the committed gauntlet's flat OURS line **alignment luck** (block 24 == the grid-4 sleep period), or does retention survive when sleeps land mid-domain |
| **SUBSTRATE** *(carried from plot_p8)* | `fig_substrate` | the 2×2 {OURS,GD}×{analog,digital} total-energy bars (hero ringed) + the substrate/algorithm/total win box, re-metered over the gauntlet | how much of the win is the analog substrate vs the 80/20 algorithm |
| **NOISE-SHOWCASE** *(P10.4)* | `fig_noise_showcase` | directional-retention vs noise level per held-out environment; OURS-hardened vs BP+replay vs naive | does the noise-hardened cell hold where naive/BP degrade (the directional enemy) |
| **PARETO** *(THE verdict, P10.6)* | `fig_pareto` | the (accuracy, energy) scatter across OURS-family + the field; the non-dominated staircase; win/tie/loss regions; hero ringed | where the whole object stands vs the field — the close-out picture |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples: all P8/P9 guards + fair-budget ✓ + freeze-content ✓ + cadence-family ✓ + gauntlet-data ✓ + noise-holdout ✓ + substrate-identity ✓ + fire/sleep-counts | guards + apparatus sanity + the freeze-content check at a glance |

**Caption rule (every figure):** one sentence ending with **the takeaway** (not a description), then `(n=5, task, …)`. An
**accuracy** caption names the **budgeted ER** reference (and the ceiling); an **energy/cost** caption tags the **meter model
+ params + substrate** and never asserts a Joule it can't source; a **fight/Pareto** caption states the win/honest-Pareto/
dominated branch it satisfies; a **noise** caption states whether the read is a **direction** or a **magnitude** (the spine).
Model caption:

> *"At a matched FLOPs/sample + byte budget, OURS(grid-4) held accuracy within 0.0X of the tuned ER-strong (0.AA vs 0.EE) at
> 0.YY× its energy on the **same digital substrate** (the algorithm win — the contestable branch: win / honest-Pareto /
> dominated); the analog substrate adds a further 0.ZZ× as a meter-structural floor overlay. (n=5, continual home; behavioral
> ADC-centred meter, params in the manifest.)"*
>
> *(Letters are deliberate placeholders — the caption teaches the shape, never an expected result. Do not anchor on any
> number.)*

---

## §D — Table schemas (fixed columns; one IQR format `median [q25–q75]`; no bare means)

**The RESULTS.md ledger — one section per rung; header states locked controls (`task, stream, seeds, object-hash,
racer-budget`); last column = a ≤6-word verdict; one variable swept per table (the swept variable is the first column):**

| rung | columns (after the swept variable) |
| --- | --- |
| P10.0 | `guard · value · vs-reference · pass? · verdict` *(fair-budget FLOPs/bytes · freeze-content manifest+grid-4-bit-exact · cadence bit-exact · data-dim=40 · holdout · substrate-identity)* |
| P10.1 | `learner · accuracy · energy(analog) · energy(digital) · BWT · AAA · vs-OURS · verdict` *(learner swept)* |
| P10.2 | `grid · accuracy · energy · worst-BWT · Pareto? · verdict` *(cadence swept; Tier-1 rep flagged)* |
| P10.3 | `config · plasticity · 1-back · all-prev(AA) · BWT · cum-energy · GD-share · verdict` *(+ a per-domain sub-table)* |
| P10.4 | `environment · dir-retention(OURS) · dir-retention(BP) · dir-retention(naive) · holds? · verdict` |
| P10.5 | `learner · accuracy(natural) · energy · vs-OURS · verdict` *(the recognizable-data confirm)* |
| P10.6 | `axis · OURS · best-field · win/tie/loss · number` *(the Pareto verdict map — accuracy · energy · retention · noise)* |

**Struck / dominated rows:** identical schema, with the failure condition + the **mechanistic reason** in the verdict column
— a dominated fight, a Tier-2 collapse, a residual that bites each get the same rigor as a win (failures are data).

---

## §E — The summary writing contract (the 8 slots — fill verbatim, formal voice; carried, P10-tuned)

Every `expK/experiment-K.md` *Read* section fills these 8 slots in order, none empty (if "n/a", say *why*):

1. **Claim** — one falsifiable sentence.
2. **Headline number** — median **[IQR]**, against the **budgeted BP+replay** reference (the external opponent) + the ceiling.
   Never a bare number; state the **Pareto branch** (win / honest-Pareto / dominated) it satisfies.
3. **Figures** — the catalog refs emitted, each one line; name the headline figure.
4. **Mechanism** — *why* the number is what it is (the spine: is the noise read a **direction** or a **magnitude**? why is
   OURS cheaper — the gate, the no-backward-pass, the analog substrate? does retention hold because the bulk *rotates not
   forgets*?).
5. **Threats to validity** — the §B carry (behavioral meter; ER budget/tuning; domain set/order; synthetic overstatement;
   the held-out battery; substrate-independence of accuracy); the methodology rule-1 check, written in.
6. **Decision / verdict** — which Pareto branch this rung banks, and what the close-out inherits (P10 sets no *learned* knob —
   it *validates*; a "decision" here is a validated/honest-Pareto/not-supported verdict, or the selected Tier-1 rep).
7. **Freeze-honesty** — **the object was frozen before the run** (the `freeze_content_guard` asserted the frozen-knob content
   manifest + grid-4 bit-exact reproduction; `59d2720` is a provenance label, not a runtime git `==`); **the verdict shape was
   pinned BLIND** (no baseline number tuned against); the **only dial moved was the declared cadence cost axis**; the meter
   model + params are stated.
8. **Where-it-stands** — what this rung says about the **founding 80/20 continual bet** (validated / honest-Pareto / not
   supported) and the **money story** ("less energy than modern GD" — the substrate ratio). A rung that moves neither the
   Pareto verdict nor the close-out shouldn't have run.

**Voice rules:** declarative past-tense for what happened; present-tense for standing reads; **no hedging filler, no
first-person, no exclamation**; every adjective backed by a number or dropped; a dominated result stated plainly ("a budgeted
ER edged OURS on accuracy by 0.0X (> δ_acc, 4/5) at 0.YY× the energy — the honest-Pareto branch, not a win"). **Continuity:**
each card opens by naming what it inherits ("Inheriting the frozen object (`59d2720`, grid-4) and the byte-matched ER racer
from P10.0, …"). A folded rung (P10.5 into P10.3) is a one-line pointer.

---

## §F — Gold-standard worked card (copy this skeleton; the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches the
> shape, voice, and completeness, never an answer.*

```markdown
# P10.1 — The existential fight: does OURS beat a budgeted experience replay?

**Question.** At a matched FLOPs/sample + byte budget, does OURS(grid-4) match/beat a tuned ER on accuracy at strictly lower
energy — or is it dominated?

**Setup.** Swept variable = learner ∈ {ours_g4, er_strong, er_budget, agem, derpp, gdumb, naive}; controls locked (frozen
object `59d2720`, continual home, seeds [42,137,271,314,1729], same per-op energy table, replay bytes matched to the LUT).
FIGHT + PARETO + INV. Apparatus: p10lib ContinualBP + awake_sleep_loop; guards passed (fair-budget: ER bytes == LUT, FLOPs
reported; freeze-content: manifest + grid-4 bit-for-bit (`59d2720` provenance); cadence-family grid-4 bit-for-bit;
substrate-identity: pred_analog == pred_digital; + all P8/P9 guards). Verdict shape pinned BLIND (§2.3).

**Run.** L learners × 5 seeds, checkpointed (_ckpt.jsonl); OURS live loop + the BP+replay racers. Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| learner | accuracy | E(analog) | E(digital) | BWT | AAA | vs-OURS | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ours_g4 (OURS) | 0.AA [..–..] | 0.aa (ref) | 0.ad | -0.0b | 0.Aa | (ref) | <win / honest-Pareto / dominated> |
| er_strong | 0.EE [..–..] | 0.ee | 0.ed | -0.0c | 0.Ee | <acc Δ?> | the load-bearing opponent |
| er_budget | 0.EB [..–..] | 0.eb | — | -0.0d | 0.Eb | <at OURS's budget> | the same-budget point |
| agem / derpp / gdumb | … | … | … | … | … | … | the field |
| naive-BP | 0.NN [..–..] | 0.nn | — | -0.0e | 0.Nn | the floor | forgetting floor |
- **FIGHT** (headline): <accuracy Δ vs ER at the byte/FLOPs budget; the energy ratio>.
- **PARETO**: <where OURS sits on the (acc, energy) frontier vs the field>.
  - **INV**: fair-budget ✓, freeze-content ✓ (manifest + grid-4 bit-exact; `59d2720` provenance), cadence-family ✓, substrate-identity ✓, + all P8/P9 guards ✓.

**Read (8 slots).**
1. *Claim* — OURS holds accuracy within δ_acc of the budgeted ER at strictly lower analog energy (the win branch).
2. *Headline* — OURS 0.AA [IQR] vs ER 0.EE at 0.YY× energy (n=5, continual home; behavioral meter).
3. *Figures* — FIGHT (twin bars), PARETO (frontier), INV (guards green).
4. *Mechanism* — if OURS held: the bulk rotates-not-forgets so only the tiny namer replays; no backward pass + the analog
   crossbar make the per-name energy a sliver of BP's gradient-through-the-net.
5. *Threats* — (a) meter behavioral (params logged); (b) ER tuned + byte/FLOPs-matched (both budget/strong reported);
   (c) "real" = IQR-disjoint + ≥4/5 sign.
6. *Verdict* — banks the founding-bet branch (validated / honest-Pareto / not-supported); the close-out inherits it.
7. *Freeze-honesty* — object frozen before the run (freeze-content manifest + grid-4 bit-exact; `59d2720` provenance, not a git ==); verdict shape pinned BLIND; only the cadence dial moves.
8. *Where-it-stands* — the 80/20 continual bet is <validated/…>; the money story is 0.YY× the energy of GD-on-digital.
```

This is the bar: every slot filled, IQR in every cell, the budgeted-ER reference named, the Pareto branch stated, the
freeze-honesty affirmed, the guards green.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

- [ ] **Median [IQR]** for every headline number (n=5; 9 for ≤0.02 gaps; 3 only for the heaviest live cells) — no bare means.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 by sign) before any gap is claimed; else "within noise."
- [ ] Every accuracy figure names the **budgeted BP+replay** reference; every cost figure tags the **meter model + params +
  substrate**; the **Pareto branch** (win / honest-Pareto / dominated) is stated, not implied.
- [ ] **The fair-budget guard is green** — ER's replay buffer == OURS's LUT in **bytes**, ER's **FLOPs/sample** reported, both
  ER points (budget-matched + strong) built, both metered on the identical per-op table. A crippled ER voids the fight.
- [ ] **The second-review K-deltas honored (design §9):** the **joint-BP ceiling** overlaid + annotated (never a racer);
  **ER-strong's tuning protocol** in the manifest (tuning stream seed ∉ raced set — the raced seeds untouched); **throughput
  from metered FLOPs** (wall-clock a footnote only); **input-identity** asserted (bit-identical projected stream, ONE pinned
  →40 mechanism); **total-memory reported** beside the matched replay-bytes; **all five grids on the gauntlet** (or the
  pre-registered demotion logged) + the per-domain frontier strip; the **reversed-order control** reported; the
  **substrate-identity guard scope** respected (P10.4's noise arms exempt); the **professor pack** assembled at P10.6.
- [ ] **The freeze-content guard is green** — the frozen-knob **content manifest** (`COMMITTED_LOOP` + `cadence_every=4` +
  `HEAD="slda"` + the SLDA/cell config) **+ grid-4 bit-exact reproduction** asserted (`59d2720` is a **provenance label**, not
  a runtime git `==` check); **no learned knob moved**; the only dial is the declared cadence cost axis. The verdict shape was
  **pinned BLIND** (slot 7).
- [ ] **P10.2** reports the family as a **declared cost axis** — **grid-4 is the committed headline, NEVER swapped, always
  plotted**; a Tier-1 *showcase rep* (visualization only) is admitted iff Pareto-non-dominated **AND** worst-BWT within δ_acc
  of grid-4's (grid-5 the only candidate; grid-6 −0.087 fails) **AND** energy IQR-disjointly lower; Tier-2 {8,12,16} shown as
  the degradation arms (greyed if sub-chance; g12 = the §10 home-only gap-filler, its Tier-2-axis read pinned in design §10);
  **no per-dataset best grid is passed off as "OURS."**
- [ ] **P10.3** emits the **twin-panel** money figure (worst-pre-sleep retention + cumulative energy), the OURS lines
  (**grid-4 always** + the optional Tier-1 rep + grid-8 + grid-16), the **sleep-position overlay + domain markers**, the
  **throughput / steps-behind** read, the **substrate re-meter**, and the **GD-share vs difficulty** sub-table; **AAA**
  reported beside AA. **§10 ext:** the **GAUNTLET-STREAM** per-batch view is emitted with its three guards green (cell
  replay bit-exact vs the committed cache; head replay ≡ the committed `err_trace`; cumulative-energy endpoint ≡ the
  committed meter total) — a broken replay guard voids the stream view, never the committed money figure. **§10 E8:**
  the **GAUNTLET-STREAM-LONG** alignment-break view is emitted with the same replay guards anchored to **its own
  run's** cache/err_trace (the stream is new by construction — stated); its read (alignment-independence vs
  alignment-luck) is banked per design §10 round 3, and an alignment-luck outcome is written into the GAUNTLET
  caption as a stated limitation, never silently absorbed.
- [ ] **P10.4** uses a **margin-disjoint held-out** noise battery (the `noise_holdout_guard` asserts a concrete margin from
  P9.4's residual **and** flags genuinely-novel-structure "payoff" vs re-parameterized "confirms"); the read is **directional
  retention** (a direction, not a magnitude — the spine); a residual that bites is **named → analog layer**.
- [ ] **P10.5** (or its fold into P10.3) reports the fight on **natural** data (the recognizable-data confirm); the synthetic-
  vs-natural gap direction is stated.
- [ ] **Accuracy is not double-counted across substrates** — OURS-analog and OURS-digital share one accuracy; the substrate
  axis lives only in the energy figures.
- [ ] Every figure drawn by a **`plot_p10.fig_*`** function (no inline styling); caption ends with the takeaway + `(n=…, …)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); formal voice; the card opens by naming the inherited object/racer.
- [ ] **`manifest.json`** (git hash, config, seeds, versions, wall-clock, meter per-op params + citations, **the frozen-object
  content manifest + provenance `59d2720`**, **the racer's FLOPs/bytes budget**) **+ `arrays.npz`** written; **`plot_p10.py
  regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards logged:** all P8/P9 guards + `fair_budget` + `freeze_content` + `cadence_family` + `gauntlet_data` +
  `noise_holdout` + `substrate_identity`. **Any guard fails → STOP.**
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874
  guards; **no sklearn / no River** for compute (GDumb's balanced sampler hand-rolled); the real PID verified alive on
  multi-hour live cells.
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **dominated / struck** arm logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P10.0** bench + guards | INV (fair-budget + freeze-content + cadence-family + gauntlet-data + noise-holdout + substrate-identity + all P8/P9 guards) |
| **P10.1** existential fight | **FIGHT** + **PARETO** (OURS-g4 vs the racer field), INV |
| **P10.2** cadence frontier | **CADENCE-FRONTIER** (5 grids on acc × energy × worst-BWT), INV |
| **P10.3** the gauntlet (money figure) | **GAUNTLET** (twin panel + sleep-overlay) + **GAUNTLET-STREAM** (§10 per-batch view, fwd + REV + **LONG/alignment-break**) + **SUBSTRATE** (re-metered), INV |
| **P10.4** noise showcase | **NOISE-SHOWCASE** (directional retention per held-out env), INV |
| **P10.5** A5 natural *(may fold into P10.3)* | **FIGHT**/**PARETO** on natural data, INV |
| **P10.6** the verdict + close-out | **PARETO** (the full frontier + win/tie/loss map) + the Stage-2 close-out rewrite |

## Grounding (what the field does — and what we adopt)

- **The fair fight = a BUDGETED baseline** (FLOPs/sample + bytes) where ER is strong (Prabhu CVPR'23 [2303.11165]; Ghunaim
  CVPR'23 [2302.01047]; Budgeted-OCL ICLR'25 [2410.15143]) → FIGHT + the fair-budget guard.
- **The baseline family** — ER [1811.11682] · A-GEM [1812.00420] · DER++ [2004.07211] · GDumb (Prabhu et al., ECCV 2020) ·
  naive-BP (floor); REMIND [1910.02509] the anti-pattern → the fight roster.
- **The metrics** — ACC/BWT/FWT (GEM [1706.08840]); Forgetting (RWalk [1801.10112]); AAA/anytime ([2308.10328]); more-than-
  forgetting ([1810.13166]) → §B.
- **The gauntlet scenario** — domain/class-IL (van de Ven [1904.07734]) → GAUNTLET.
- **The meter + substrate 2×2** — carried from P8 (Horowitz ISSCC'14 · NeuroSim · ISAAC ISCA'16 · PUMA ASPLOS'19 · AIHWKit) →
  SUBSTRATE + the cost figures. Full delta: [`../../research/papers/phase10/README.md`](../../research/papers/phase10/README.md).
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 — carried from Phases 1–9
  ([`../result-format.md`](../result-format.md), [`../phase8/result-format.md`](../phase8/result-format.md), [`../phase9/result-format.md`](../phase9/result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to this catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent. **The object is frozen; we
> measure, and report the frontier — win, tie, or loss.**
