# Phase 8 — The Economy: *when* the namer fires, and *what it truly costs* (the plan)

> **Status: 🟢 RAN & COMPLETE (P8.0→P8.6 ran 2026-07-02; deep-research folded; 3-agent lab-manager review folded — §8).
> + P8.7 substrate ablation EXTENSION added & ran 2026-07-02 (the "why analog" 2×2 for the professor brief — §2.5, §3).**
> A *live spec an agent executes* — the experiment ladder + build plan for the **economy of the two-brain chip**: the
> awake/sleep learning-gate that decides *when* to pay for direction, and the honest hardware cost meter that prices it.
> When the rungs run they fill `expK/experiment-K.md`, `RESULTS.md`, then the public `README.md` + `phase8-report.md`.
> Reporting contract: [`result-format.md`](result-format.md). Literature: [`../../research/papers/phase8/`](../../research/papers/phase8/README.md)
> — **including the deep-research delta** [`deep-research-delta.md`](../../research/papers/phase8/deep-research-delta.md).
> The frozen cell it reads: [`../phase6-final-architecture.md`](../phase6-final-architecture.md). The committed namer it
> fires: [`../phase7/README.md`](../phase7/README.md). The Stage-2 map: [`../stage2-design.md`](../stage2-design.md) §4.
>
> **Phase 8 = the second of three GD-stage phases** (P7 readout ✓ · **P8 economy + cost** · P9 maintenance). Phase 7
> picked *what* the namer is (RanPAC + cbrs); Phase 8 decides *when* it fires and *what it costs* — and, for the first
> time, **runs both brains live together.**

---

## 0. Why Phase 8 exists — the problem, the reframe, and what it is NOT

### 0.0 The arc — Phase 8 completes the real learning mechanism

Stage 1 built + noise-hardened the cheap brain; Phase 7 picked the namer. Both were *characterized* on a bulk that was
frozen for the static bake-off. The chip's real mechanism runs **both brains live at once**, and Phase 8 is where we turn
it on.

### 0.1 The reframe that defines Phase 8 (the author's Q-call — load-bearing)

> SCFF is unsupervised, so it is great at continual learning: train it on **every input it gets, forward-only, and it
> never forgets.** The only problem is the GD readout. The more input SCFF gets, the more **its class representation
> shifts**. Phases 1–7 dodged this by freezing SCFF before fitting GD, so the shift never appeared. **Phase 8 completes
> the real learning mechanism: both organs live.**

So the device under test is a **co-adapting system**, not a frozen encoder with a head:

- **SCFF is LIVE** — forward-only update on every input, always. It doesn't forget, but its feature map **drifts** as it
  learns (and the stream keeps handing it new classes). This drift has a name in the field: **representation / semantic
  drift** in online continual learning.
  - *("LIVE" does not overturn the frozen commitment.* "Frozen" always meant frozen **to GD** — GD reads taps, never
    writes SCFF — and frozen **as a design** — the objective/knobs (`τ=0.2`, `w=2`, the norm, `σ_aug=1.0`) don't move.
    SCFF **weights** were always intended to keep updating on the unsupervised stream: arch §3.2 says exactly "SCFF's
    whole map drifts… the SCFF features themselves don't forget." Phase 8 does not reopen a single committed knob — it
    turns on the live loop the design always specified.)*
- **The GD namer reads the drifting taps** — and, fit against where the clusters *used to be*, its names slide off unless
  it re-tracks. **The chip maintains the namer's statistics as a running Gram on capacitors** (arch §2.4: "the running
  mean is a capacitor EMA and the Gram is a running second moment"), so those statistics **accumulate across the drift** —
  early-stream φ and late-stream φ are in *different* representations, so a running Gram is a **blur of inconsistent
  features** until a re-solve on **fresh, consistent** features re-aligns it. *(⚠ Apparatus note, from the repo-fit
  review: the current `p7lib` heads re-solve from scratch on whatever buffer they are handed — they do **not** maintain a
  running Gram. So the streaming running-Gram update is a **new tested primitive Phase 8 must build** — `partial_fit`,
  §6 — precisely because it is the chip-faithful mechanism, and building it is what makes the drift-poisoning effect a
  **measurable** phenomenon rather than a narration. This is the phase's one genuinely-new primitive.)*

**The whole economy of the chip exists to keep the namer tracking that drifting bulk cheaply** — the awake/sleep loop
(§0.2), metered (§2.3). **This is the end-to-end test of the founding thesis** ("80 % cheap unsupervised structure + 20 %
precise naming, paid for only when it counts"): a design claim for seven phases; Phase 8 runs the loop that makes it true
or false and puts the first honest cost number on it.

### 0.2 The mechanism, stated once (from `ideas1.md` Ch7–8, now testable)

**Awake (streaming default).**
- **Loss below θ** (output error low): **update SCFF only.** Cheap, local, constant; the namer coasts on current weights.
- **Loss above θ** (output error high): **update SCFF as normal, *plus* the namer.** Pay for direction exactly when the
  cheap brain alone isn't keeping the output good enough (a new class arrived, or SCFF drifted far enough).

**Sleep (periodic full recovery).** The awake gate creates the problem Ch8 named precisely: firing only on high-error
(recent/surprising) samples re-covers only the ~10 % of the current SCFF map that recently spiked — **the other ~90 %
goes stale** as SCFF drifts underneath it. So periodically **sleep**: stop streaming, **re-fit the namer full-batch over
the whole history (the LUT) against the *current* SCFF map.** Sleep is cheap *by construction*: the SCFF bulk doesn't
forget, so sleep re-aims only the small namer; and the LUT stores **raw input prototypes** (not features — features
drift; raw input is stable ground truth), so sleep **re-forwards raw prototypes through the *current* SCFF → fresh,
mutually-consistent features → one closed-form re-solve.**

- **The correct literature cousin (fixed after the literature review).** This is **raw-exemplar replay with recomputed
  prototypes** (iCaRL-style re-extracted class means; GDumb-style raw buffer) — replay *raw* data and recompute the head
  against the *current* backbone. It is **NOT REMIND**: REMIND freezes the backbone after task 1 and replays *compressed
  features* — the two things we deliberately avoid (we store raw *because* the backbone moves). So REMIND is the
  **anti-pattern** (the frozen-backbone, feature-storage design that *cannot* handle a moving backbone), and the
  exemplar-free drift-*compensation* line (SDC / LDC) is the **road-not-taken** (§5 → Phase 9).

**One detector, two timescales.** "When to fire awake" and "when to sleep" are the **same drift signal read at two
rates** — the per-step gate reacts to fast local staleness; the sleep cadence integrates slow global drift. Phase 8
builds *one* detector and reads it at both.

### 0.3 What the research suggests — hypotheses to harden (NOT results)

As **hypotheses**, never findings:

- **H-tap-lead (the bet):** a **class-direction** label-free tap-drift detector fires *before* the readout's error reacts
  (SCFF drift *leads* error), scheduling a refit early — **without** false-firing on nuisance drift. **Owed:** the FAR on
  a nuisance segment; whether "early" survives the false-fire tax.
- **H-conservative (the false-fire hedge):** because *for us a false fire burns the 80/20*, a **conservative** label-free
  detector (STUDD-style: fewer false alarms, slower) may beat the fast-but-noisy magnitude-of-shift detectors on our
  *net* objective. **Owed:** the MTD↔FAR trade at our cost weighting.
- **H-cheap (the metered bet):** the no-gradient namer is **actually cheap** on an ADC-dominated substrate, and the gate
  gets the GD-share of energy near the 80/20 target. **Owed:** the metered 80/20; whether **SLDA displaces RanPAC** once
  the 2000-D projection's ADC + solve cost is priced (Phase-7 flagged ~200× proxy).
- **H-live-safe (the existential one):** the *live* co-adapting mechanism **keeps the A6 continual win** the frozen
  characterization promised. **Owed:** BWT vs baseline, 5 seeds + paired-sign veto, **measured at the awake gate's worst
  point (pre-sleep)** — the un-skippable gate (P8.6).
- **Struck-in-advance (re-confirm as logged):** a **confidence/entropy** gate — *out* (a magnitude; P5 struck the adaptive
  exit); a **raw magnitude-of-shift** tap detector as the *committed* trigger — *out*, it false-fires on nuisance by
  construction (it becomes the null/control, §2.2); **synthetic-gradient / DNI** upstream of SCFF — *out* (forward-leak
  poison); **re-opening the frozen bulk or re-litigating the head** — *out* (RanPAC/cbrs committed, SLDA the metered alt).

### 0.4 What Phase 8 is NOT — the scope guard

- **NOT the fair same-budget BP+replay *accuracy* baseline, NOT natural multi-class A5 → Phase 9.** Phase 4's WIN was vs
  *naive* online-BP; the fair same-budget accuracy fight is the still-owed existential test, and it is **P9's**. Phase 8
  compares **metered energy** to a BP energy *model* **at matched retention** (§2.3), never accuracy-vs-BP+replay.
- **NOT re-opening SCFF, NOT re-litigating the head.** The bulk is frozen-as-a-*design*; RanPAC + cbrs committed, SLDA the
  metered fallback. A meter verdict that SLDA wins is a *Phase-8 cost decision*, not a Phase-7 re-run.
- **NOT the N2 drift-slowdown / EMA-view tuning → Phase 9.** Phase 8 *measures* the live SCFF drift (P8.0) and takes it as
  given; slowing the late layers to *reduce* drift is Phase 9's lever (slow-coordination.md).
- **NOT SPICE / device physics.** The cost meter is a **behavioral** charge/ADC/write model (NeuroSim-family level), the
  same scope rule as Phase 6's noise model.
- **NOT the LUT-streamed-negative estimator question.** SCFF trains live with the validated **mini-batch in-batch-negative**
  InfoNCE (Phases 1–7); the on-chip LUT-streamed-negative regime stays deferred (arch §2.4 caveat 1). Phase 8's LUT is the
  **replay store for sleep + the cbrs buffer**, not the negative pool.
- **NOT the north star.** No recurrence. The gate is built as PonderNet's *un-looped* ancestor, grounded on a
  **direction/drift** signal so the recurrent brain can reuse it — a *tie-break bias*, not scope.

---

## 1. The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — read the class DIRECTION, never a MAGNITUDE (8th coat).** In Phase 8 the spine lives in the **gate
trigger**: it fires on whether the **class direction** has shifted (off the readout), **never** on a **confidence
magnitude** (softmax confidence/entropy — why P5 struck the adaptive exit) **and never on a raw magnitude-of-distribution-
shift** (a mean-shift / MMD / input-moment statistic — *density ≠ class one level up*: a large nuisance covariate shift is
a big distribution move with zero class-direction change, so a magnitude-of-shift trigger is **primed to false-fire on
nuisance by construction** — the red-team's catch). So the committed label-free trigger reads drift **along the class /
readout directions**; the raw magnitude-of-shift version is carried only as the **predicted-to-false-fire null** (§2.2).
An **error-rate** trigger is a *labeled magnitude* — it is a legitimate **labeled reference** (the thing the direction
trigger must beat), **not** a spine exemplar; we do not call it spine-clean.

**The envelope — the live loop still obeys the forward-leak wall.** SCFF trains live and forward-only; the namer **reads
taps, never writes into the SCFF stream** (P2.5 forward-leak wall + BYOL stop-gradient). The gate/sleep touch *only* the
namer and the LUT — never SCFF's objective or weights. A learned budget-gate is a tiny trained thing **on the read side**
(reads taps/error, never writes SCFF), so it does not violate the wall — but it is FD-guarded and its spine-tension (the
least direction-pure arm) is flagged.

**Guards FIRST, every run — the netlist rule.** Import tested primitives; the one new primitive (`partial_fit`) ships with
its own equivalence guard. Before any gate runs, the guard set (§6) must pass; **any guard fails → STOP.**

---

## 2. The mechanism, the deliverables, and the numeric verdict cuts (pinned BLIND)

### 2.1 The operations the loop performs (what the meter prices, what the gate schedules)

Per stream step (a mini-batch), the live loop performs:

| op | when | cost character (to be *measured*, not assumed) |
| --- | --- | --- |
| **(a) SCFF forward + local update** | **always** (awake) | crossbar MAC-read + ADC per layer + local ΔW write; the "80 %" |
| **(b) namer forward (inference)** | **always** (an output every step) | tap-read + projection/forward + argmax; ADC traffic ∝ read-out dim |
| **(c) namer update** (`partial_fit` recent → refresh `W`) | **gated** (awake, loss ≥ θ) | running-Gram accumulate (rank-k, cheap) + solve + weight-write |
| **(d) sleep** (re-forward LUT → rebuild `G,M` → solve → write) | **gated** (slow detector) | LUT re-forward (reads+ADC) + full solve + writes; the periodic recovery |

**Which of (c)/(d) dominates is a meter output, not an assumption** — that is why the meter and the gate are one phase.
The gate chooses (c)'s frequency; the cadence chooses (d)'s.

**The namer-update model (the closed-form head, made streaming — repo-fit fix).** The chip maintains a **running
`(G, M)`** on capacitors (arch §2.4). Phase 8 builds this as `partial_fit` (§6): op (c) = `partial_fit(recent batch)` →
accumulate into `(G, M)` → re-solve `W`. Below θ the namer **coasts** (no accumulate, no solve). Sleep (op (d)) **rebuilds
`(G, M)` from the re-forwarded LUT** (fresh consistent features) and solves — the recovery that undoes the running Gram's
drift-blur. **A sub-knob (P8.3):** the running Gram's **EMA decay** `λ_ema` (pure cumulative `λ=1` blurs across all drift;
`λ<1` down-weights stale-representation features) — the mitigation that trades sleep frequency against accumulate fidelity.

**The dual-mode harness (repo-fit + red-team fix).** `awake_sleep_loop` (§6) has two modes: **(i) block/oracle mode**
(SCFF trained per-task-block, sleep at every known boundary, no awake gate) — reproduces `continual_safety_heads`
bit-for-bit, the guard + the oracle-cadence reference; **(ii) streaming mode** (interleaved / gradual-onset schedule, a
per-step awake gate, detector-driven sleep) — **the real Phase-8 regime.** All the economy experiments (P8.1–P8.6) run in
streaming mode; block mode exists for the guard and the oracle reference. **P8.0 pins and justifies the streaming
schedule** (single/few-pass, gradual class onset so drift is *continuous* not stepwise — the reframe's "every input"
regime), because every MTD/FAR/cadence number depends on it.

### 2.2 Deliverable A — the economy gate (awake) + the sleep cadence

**The gate bake-off (P8.1 — the detector, label-based error trigger):** **no-gate/always-pay** (cost ceiling) · **oracle-
cadence** (block mode — "if you knew when the world changed"; the achievable reference) · **absolute-θ** · **DDM**
(two-threshold error) · **ADWIN** (two-window error) · **learned budget-gate** (Skip-RNN-style, `L_budget=λ·Σu_t`; reads a
direction/drift feature, FD-guarded; the least spine-pure arm). *(Conditional arm — if P8.0 shows the SCFF drift is
**slow/gradual**: add a gradual-drift-tuned detector (HDDM-A/W or RDDM) — DDM/ADWIN are abrupt-biased, and the field warns
they lag on gradual creep, which is exactly what representation drift is.)*

**The trigger bake-off (P8.2 — orthogonal to the detector):**
- **error/loss-EMA** — the **labeled reference** (precise, lags; a labeled magnitude, not spine-clean).
- **class-direction tap-drift** — the **committed candidate**: drift measured *along the class/readout directions* of the
  taps (spine-clean; fires when the class direction moves, not when the distribution merely shifts).
- **magnitude-of-shift tap-drift** — the **null/control**: a raw mean-shift / MMD / input-moment statistic (the
  ADWIN-U-style signal). Predicted to false-fire on nuisance (§1); carried to *demonstrate* the spine point, not to ship.
- **DriftLens** — the **purpose-built label-free reference** (Greco et al., TKDE 2025): distribution-distance on the
  embedding/tap window vs a fixed reference — the validated tool the home-grown class-direction statistic is checked
  against.
- **STUDD-style** — the **conservative** label-free arm (student mimics the namer; monitor mimic-loss; fewer false alarms,
  slower).

**The sleep cadence (P8.3)** = the same detector, slow. How often to sleep and how much LUT history it needs — the
cheapest cadence that holds the A6 win, replacing the oracle boundary with a detector output; plus the `λ_ema` sub-knob.
**The committed cadence is flagged drift-rate-conditional** (if P9's N2 slows the drift, re-tune).

### 2.3 Deliverable B — the honest hardware cost meter

A **behavioral, literature-calibrated, ADC-centred** per-operation energy model (NeuroSim / ISAAC / PUMA level — **not**
SPICE):

```
E_total = Σ [ n_MAC·e_MAC  +  n_ADC·e_ADC(bits)  +  n_write·e_write  +  n_solve_flop·e_digital ]
```

with **ADC as the dominant term** (the field-wide finding: ADCs dominate CIM peripheral energy/area). **Calibration
anchors (cite in the manifest):** SAR-ADC ≈ **0.2 pJ/conversion-step**, energy ≈ ×2 per effective bit; a crossbar 8-bit
MAC can be **< 100 fJ** while ADCs consume **5–50×** the crossbar area and ≈ half the tile energy (ISAAC). The ridge/tied-cov
**solve** is the "non-free digital block" (`e_digital`). Relative-energy units (pJ where defensible), params + citations
logged. **Guarded to reduce to the P7 `readout_cost` proxy under unit energies — for the MAC + solve sub-terms only** (the
ADC + write terms are net-new; `readout_cost` never had them — repo-fit nit).

The meter delivers:
- **The RanPAC-vs-SLDA verdict (P8.4)** — RanPAC's 2000-D projection ≈ 2.6× SLDA's ADC read traffic + a 2000³-vs-768³ solve
  (~18× solve cost). Does the Phase-7 accuracy tie survive going *live*, and does it justify the cost?
- **The metered 80/20 (P8.5)** — GD-share vs SCFF-share of total metered energy over the stream, vs a **BP energy model at
  matched retention**: the BP reference must be **BP+replay** (its per-step backward + its replay passes to reach OURS's
  retention), metered on the **identical per-op energy table** (same `e_ADC`, `e_MAC`, `e_write`) — *not* a generic FLOP
  count and *not* a naive backward-every-step BP that forgets (a strawman). The first non-proxy 80/20 the project has had.
- **The substrate ablation (P8.7 — EXTENSION)** — the same committed loop + the same BP+replay baseline, re-metered on the
  **digital substrate** (§2.5) so the full **2×2 {OURS, GD+replay} × {analog, digital}** decomposes the win into
  **substrate** × **algorithm** — the "why analog" answer for the professor brief.

### 2.4 The numeric verdict cuts (PINNED BLIND — the Phase-6/7 "unpinned verdict" hole, never reintroduced)

Pinned as *shapes with thresholds*, never expected results. `δ_acc = 0.02` (the house bar), paired by seed.

- **Gate frontier (P8.1/P8.2).** The primary read is the **frontier**: accuracy-held vs GD-fire-fraction `f`, with FAR as
  the third axis, all vs the **oracle-cadence** reference. A gate is **committed-eligible** if it sits on the frontier's
  knee — (i) **accuracy-held** within `δ_acc` of the oracle (paired), (ii) at low `f`, (iii) with **FAR at/below the
  stationary-segment floor**. `f* = 0.25` is a **reference line** (the "20 % with slack"), **not a hard binary pass/fail**
  — a gate at `f=0.30` holding full accuracy with low FAR beats a gate at `f=0.24` that drops accuracy; the frontier
  position decides, the reference line only annotates. Failure modes (over-fire / under-fire / false-fire) are logged.
- **FAR / false-fire (all arms).** Measured against a **common empirical floor** — each detector's own fire-rate on the
  **stationary segment** (its MTFA), established by `detector_far_guard` — **not** each detector's private nominal δ (abs-θ,
  DDM, STUDD, budget-gate have no calibrated δ). A false fire = a fire on the **nuisance** segment (no real drift).
- **Trigger verdict (P8.2).** The class-direction tap trigger **earns-early** iff `MTD(tap) < MTD(error)` **AND**
  `FAR(tap, nuisance) ≤ FAR(error, nuisance)`; else `early-but-noisy` (report the tension) or `no-lead`. The
  magnitude-of-shift null is *expected* to show high FAR (the spine demonstration).
- **RanPAC-vs-SLDA (P8.4).** Commit **SLDA over RanPAC** iff `E_meter(RanPAC)/E_meter(SLDA) ≥ 2` **AND** `|AA − AA| ≤ δ_acc`
  where **both AA are freshly measured on the *live* loop** (not inherited from P7's frozen tie — the tie may not survive
  going live). Else keep RanPAC.
- **Metered 80/20 (P8.5).** `GD-share = E[(c)+(d)]/E_total`; "**80/20 confirmed**" iff `GD-share ≤ 0.25` with the committed
  gate on; reported alongside the `bp_ratio` (OURS `E_total` / BP+replay `E_total`, matched retention, same substrate).
- **A6 live-safety (P8.6, un-skippable).** **BWT measured at the awake gate's worst point (mid-stream, just before a
  scheduled sleep — NOT post-sleep)** — post-sleep hides the awake gate's recency forgetting (red-team catch). Live BWT
  **not negative** vs the oracle/frozen baseline in `≥ 4/5` paired seeds (veto) **AND** live AA within `δ_acc` of the
  frozen promise. A negative-BWT-at-worst-point in ≥4/5 = the economy is not safe (a first-class failure).
- **Substrate ablation (P8.7 — EXTENSION).** Reported as a **decomposition**, no binary pass/fail. The **substrate win**
  `= E(OURS-digital)/E(OURS-analog)` (same algorithm, CIM vs von-Neumann) and the **algorithm win** `= E(GD-digital)/
  E(OURS-digital)` (same digital substrate, our 80/20 vs BP+replay) must **multiply to the total win** `= E(GD-digital)/
  E(OURS-analog)` (an identity check — if they don't, the meter is inconsistent). The analog advantage is **honest only
  if it survives the `E_MAC_DIG` sweep** — OURS-analog < OURS-digital across the whole arithmetic-only → memory-wall
  range, so the reported number is a floor, not a knife-edge on one MAC-energy assumption.

**No result may be narrated into a branch it does not numerically satisfy.**

### 2.5 The digital substrate (P8.7) — the conventional baseline, made fair

The meter's analog model (§2.3) prices the **crossbar/CIM chip**: the MAC is near-free (in-memory, `E_MAC`) and the
**ADC dominates**. The "why analog" question needs its counterfactual — the **same computation on a conventional
von-Neumann / digital-accelerator (GPU-class) substrate**, priced on the **same per-op accounting** so the only thing
that changes is the *physics*:

- **The MAC is no longer free.** A digital 8-bit multiply-accumulate must **fetch its operands** (the memory wall):
  `E_MAC_DIG ≫ E_MAC`. Anchor: **Horowitz ISSCC'14** (45 nm) — 8-bit MULT ≈ 0.2 pJ, ADD ≈ 0.03 pJ → an 8-bit MAC
  ≈ **0.2 pJ arithmetic-only**; an on-chip SRAM operand fetch adds ~1–5 pJ (DRAM ~100×). So `E_MAC_DIG = 0.2` is the
  *arithmetic-only floor* (most generous to digital) and the **memory-wall penalty is folded into the sweep**
  `E_MAC_DIG ∈ {0.1 … 2.0}`.
- **There is no ADC.** The datapath is digital end-to-end — the analog tax (the ADC term, §2.3's dominant cost) **vanishes**
  (`e_ADC = 0`). This is the term that *helps* digital; the meter grants it fully.
- **Weight writes are SRAM stores** (`E_WRITE_DIG = 0.5 pJ`, vs the 10 pJ analog capacitor/RRAM write-verify); the digital
  **solve** is `E_DIGITAL`, substrate-independent.
- **Matched 8-bit precision** — the analog crossbar+ADC path is also 8-bit, so the axis under test is the **substrate**,
  not the number format (the fairness clamp). The BP+replay baseline (§2.3) is priced on the digital table the same way
  (drop the ADC, use `E_MAC_DIG`) — the fair conventional-GD baseline (matched retention, weight budget, precision).

Anchors + params logged in the manifest (`METER_CITE_DIG`), sensitivity-swept — the same honesty rule as the analog meter.

---

## 3. The ladder — P8.0 → P8.7 (one variable per rung; guards first; each rung states its read-including-failure BEFORE it runs)

- **P8.0 — bench + guards + the live drift + the controls + the drift-visibility sanity panel.** Build `awake_sleep_loop`
  (dual-mode) + `partial_fit` + the meter skeleton. **Pin & justify the streaming schedule** (§2.1). Run the **guard set**
  (§6). **Measure the live SCFF drift** (`bulk_drift`) on the streaming schedule; confirm "the bulk doesn't forget" (drift
  slow + bounded). Establish the always-pay ceiling + the oracle-cadence baseline. **The drift-visibility panel
  (blind-spot fix):** show on the *actual* stream (a) where real-drift onsets are, (b) that `bulk_drift`/the class-direction
  signal move at real onsets and **not** at nuisance onsets, (c) that error-rate and tap-drift measure *different* things
  (else the trigger bake-off compares two views of one signal). **Read (incl. failure):** *how fast + what structure is the
  drift (gradual → add the HDDM/RDDM arm); does the frozen guard reproduce P7's static bake-off exactly (else the harness
  is wrong, STOP); is the drift so fast no cheap cadence tracks it (→ economy drift-bound, flag N2/Phase-9 mandatory)?*
- **P8.1 — the gate bake-off (detector, label-based trigger).** Sweep the detector arm on the streaming CI stream. Score
  **accuracy-held × GD-fire-fraction × FAR** (frontier). **Read:** *which gate sits at the frontier knee — accuracy within
  δ_acc of the oracle at low `f` without false-firing; which fail and why.*
- **P8.2 — the trigger signal.** Sweep the trigger (error-EMA ref · class-direction tap-drift · magnitude-of-shift null ·
  DriftLens · STUDD) on the **drift stream with harmful + nuisance drift**. Score **MTD × FAR** + accuracy-held. **Read:**
  *does the class-direction tap trigger lead error (MTD) without false-firing on nuisance (FAR) — earns-early /
  early-but-noisy / no-lead; does the magnitude null false-fire as predicted (the spine demonstration).*
- **P8.3 — the sleep cadence.** Same detector, slow. Sweep cadence (oracle-boundary → detector-driven) × LUT history
  fraction × `λ_ema`. Score accuracy-held × sleep-cost × (A6 BWT held at worst point). **Read:** *the cheapest cadence +
  smallest history + `λ_ema` that holds the A6 win; where the ~90 % staleness bites. (Verdict flagged drift-conditional.)*
- **P8.4 — the cost meter + RanPAC-vs-SLDA.** Build the behavioral ADC-centred meter; price the whole *live* loop for
  RanPAC vs SLDA (freshly-measured live AA). Apply the §2.4 rule. **Read:** *is no-gradient cheap on the substrate; does
  SLDA displace RanPAC?*
- **P8.5 — the metered 80/20.** The committed loop metered vs the **BP+replay energy model at matched retention** (same
  substrate table). **Read:** *the first honest 80/20 (GD-share ≤ 0.25?); the honest `bp_ratio`.*
- **P8.6 — assembled + the A6 gate (un-skippable).** Committed gate + cadence + head + cbrs, **live streaming**, 5 seeds +
  paired-sign veto, **BWT measured at the worst mid-stream point**. **Read:** *does the live mechanism keep the continual
  win (BWT not negative ≥4/5 at worst point; AA within δ_acc)? If not → the economy is not safe, and that is the headline.*
- **P8.7 — the substrate ablation: WHY ANALOG? (EXTENSION, added 2026-07-02 post-run — author Q-call for the professor
  brief).** P8.4/P8.5 metered OURS and BP+replay on the *same analog table* (the `bp_ratio` = the **algorithm** win on
  analog); this rung adds the axis the "why build the analog chip" question needs — price the **exact committed economy**
  (P8.6's loop: SLDA + DDM + cbrs + grid-8/full/λ1.0) **and** the fair BP+replay baseline on **both substrates** → the
  full **2×2 {OURS, GD+replay} × {analog, digital}**, headline three = **OURS-analog vs OURS-digital vs GD-digital.**
  The digital substrate = the conventional von-Neumann / digital-accelerator (GPU-class) baseline (§2.5). Decompose the
  total win into **substrate** (`E(OURS-digital)/E(OURS-analog)` — CIM vs von-Neumann, same algorithm) × **algorithm**
  (`E(GD-digital)/E(OURS-digital)` — our 80/20 vs real backprop+replay, same substrate); + an **`E_MAC_DIG` memory-wall
  sensitivity sweep**. **Read:** *how much of the win is the analog substrate vs the 80/20 algorithm; is the analog
  advantage robust across the digital MAC-energy assumption (a floor, not a knife-edge); does the 80/20 hold on digital?*

*(Rungs are decisions backed by a result, not experiments to tune to pass. A struck arm is a card with its mechanism.
Heavy live cells (P8.3, P8.6) checkpoint + single-thread + verify PID.)*

---

## 4. Metrics (PINNED; Phase-8 additions in **bold**)

| metric | definition (pinned) | units / format |
| --- | --- | --- |
| **accuracy-held** | live-stream final AA, vs the **oracle-cadence** baseline + the **always-pay** ceiling | acc, median [IQR] |
| continual **BWT / AA / forget** | GEM/CL conventions (`acc_matrix_metrics`) **on the LIVE loop**, **evaluated at the awake gate's worst mid-stream point (pre-sleep) for the safety gate**; vs oracle/frozen baseline; + paired-sign veto at P8.6 | acc / acc-delta |
| **GD-fire-fraction** `f` | fraction of stream steps that trigger a namer update (op (c)) | fraction ∈ [0,1] |
| **MTD** | mean stream-steps from a *known real*-drift onset to detection (true-positives only) | steps, median [IQR] |
| **FAR** | fires on the **nuisance** segment (no real drift) per unit stream, vs the stationary-segment floor | fires / step |
| **MTFA** | mean steps between fires on the **stationary** segment (the per-arm empirical floor / δ guard) | steps |
| **hardware energy** `E` | behavioral ADC-centred per-op tally (§2.3); **MAC+solve sub-terms reduce to `readout_cost` under unit energies** | relative-E (tagged model + params) |
| **metered 80/20** | `GD-share = E[(c)+(d)]/E_total`; + `bp_ratio` vs the BP+replay energy model (matched retention, same substrate) | fraction + ratio |
| **live SCFF drift** | `bulk_drift = cos(rep_t, rep_{t+Δ})` of fixed probes across the streaming schedule | cosine vs step |

**Calling a difference real (n=5; carry):** IQR-disjoint at the final checkpoint *and* sign consistent in ≥4/5 paired
seeds; else "within noise." At the P8.6 gate "within noise" is NOT an auto-pass — the paired-sign veto applies. Decisive
gaps ≤ 0.02 get **9 seeds**; A6 re-checks run the full 5, never 3.

**Threats-to-validity, every rung:** (a) the meter is a **behavioral model** — log/cite its per-op params, sensitivity-check
ADC-dominance; (b) FAR depends on the **nuisance injector** — calibrate it at the **raw-input / early-tap level** (prove the
pixels genuinely shifted) *and separately* show the SCFF output's **class direction** barely moved — two measurements, or
"no false fire" is vacuous (SCFF invariance would otherwise mask a too-weak injector); (c) **calibration-under-shift** for
any error/confidence trigger (the direction trigger sidesteps it); (d) the **oracle baseline uses known boundaries** the
detector can't see — matching it is the *win*, not a loss; (e) cached-replay results are **conditional on the forward-leak
wall** (SCFF drift is gate-independent — verified P8.0, but stated).

---

## 5. What Phase 8 hands forward / defers (the seam, stated so nothing is lost)

> **A deliberate refinement of the handoff seam (author's Q2 call).** The Stage-2 handoffs placed "sleep cadence" in
> Phase 9. Phase 8 takes the **sleep *cadence*** because the gate's economy **cannot be evaluated without it** — the awake
> gate creates the ~90 % staleness only sleep fixes (§0.2), so gate + cadence are one coupled loop (P8.3). Phase 9 keeps
> the **finer** maintenance tuning (readout-aware consolidation *depth* — which layers) and the **owed fair fights.**

- **→ Phase 9 (owed fair fights + fine-tuning):** the fair same-budget **BP+replay accuracy** baseline (the existential
  test); **natural multi-class A5**; the **N2 drift-slowdown / EMA-view** to *reduce* SCFF drift (P8 only *measures* it) —
  and the committed cadence is drift-conditional on this; **readout-aware** consolidation *depth*; **bounded-LUT eviction**
  under the bursty stream (cbrs vs continual-safety).
- **→ Phase 9 / north-star (road-not-taken, cited):** **exemplar-free drift-compensation** (SDC / LDC — a trainable
  projector mapping old→new feature space *without* re-forwarding the LUT). If P8.3/P8.4 meter the LUT re-forward as too
  expensive, this is the cheaper alternative — a *new trained organ*, out of Phase-8 scope.
- **→ read-side noise residual (Phase-6 brief, owed):** input-transducer directional channel + ADC < 3-bit — **assigned to
  Phase 9** unless P8.4's meter shows the ADC-bit choice materially changes the cost verdict (then P8 notes it).

---

## 6. What to build — `p8lib.py` on `p7lib` (import, don't retype — the netlist rule)

**Verified-present carries (import — repo-fit confirmed all present):** `RanPACHead`, `SLDAHead`, `make_head`,
`select_head_knob`, `class_balanced_reservoir`, `continual_safety_heads` (= the oracle/block-mode reference + the guard
target), `stream_cache`/`eval_head_on_cache` (frozen-bulk fast path — the *static* guard only), `continual_head_metrics`,
`readout_cost` (the proxy — MAC+solve only; keep the signature), `readout_feats`/`all_tap_feats`/`trunc_feats`,
`make_committed_cell`, `NoiseAugContrast`, `COMMITTED`, `train_cell`, `bulk_drift`, `synth_stream`, `CISTREAM_TASKS`,
`acc_matrix_metrics` (the `[[...]]` acc-matrix layout the loop must emit), `load_digits_split`, `linear_probe`, `race_bp`,
`head_equiv_guard`, `fd_head_grad`, `harness_equiv_guard`. `cell.train_step(xb, rng)` is unsupervised (gate-independent —
verified) and supports per-batch live updates; the LUT re-forward is `cell.infer(X)` → `readout_feats`. *(Dropped from the
carry list: `spineflip_*`/`recency_drop_bursty` — the static spine probes aren't Phase-8's spine surface; the spine here
is the gate trigger, measured as FAR-on-nuisance.)*

**NEW to build for Phase 8:**
- **`RanPACHead.partial_fit` / `SLDAHead.partial_fit`** (the one genuinely-new primitive) — a **streaming running-`(G, M)`
  accumulate** with an optional **EMA-decay `λ_ema`**, then solve `W` — the chip-faithful capacitor-resident Gram (arch
  §2.4). **Guard:** `N` sequential `partial_fit` at `λ_ema=1` (pure cumulative) ≡ one batch `fit` **bit-for-bit** (float64),
  + `fd_head_grad`-style check. Without this, op (c) and the drift-poisoning mechanism are not expressible (repo-fit B1).
- **`awake_sleep_loop(..., mode, gate, trigger, cadence, meter)`** — the live co-adapting harness. **Block mode** ≡
  `continual_safety_heads` bit-for-bit (same task loop, same `scff_ep`/permutation/`train_step` RNG order, same
  `rng.permutation(len)[:800]` probe draw). **Streaming mode** = interleaved/gradual-onset schedule, per-step awake gate
  (op (c) via `partial_fit`), detector-driven sleep (op (d)). Returns the acc trajectory + the `acc_matrix_metrics`-layout
  matrix (**incl. the worst-mid-stream-point eval**) + fire-counts + the per-op energy trace. **The central new organ.**
- **`stream_tap_cache(...)`** — **the tractability fast-path (per-mini-batch, new build — NOT the task-granularity
  `stream_cache`).** SCFF's live training is **gate-independent** (verified — unsupervised, reads no head/label/gate), so
  the **per-mini-batch** tap trajectory is computed once per seed and cached (**recording the exact per-step RNG draw
  order** so replay is deterministic); each gate/trigger/cadence arm replays its firing + sleep decisions on the cache.
  Keeps P8.1/P8.2 tractable. **Guard:** an arm with **non-trivial fire + sleep events** via `awake_sleep_loop` ≡ its cached
  replay, bit-for-bit (not a no-op arm — else the guard passes vacuously).
- **Detectors:** `abs_theta`, `ddm`, `adwin` (error) · `budget_gate` (learned, reads a drift feature, FD-guarded) ·
  (conditional) `hddm`/`rddm` (gradual). **Triggers:** `error_ema` (labeled ref) · `tap_drift_direction` (**drift along the
  class/readout directions — the committed candidate**) · `tap_drift_magnitude` (mean-shift/MMD — the false-fire null) ·
  `driftlens` (embedding-distance vs reference window — the label-free reference) · `studd_signal` (student-teacher mimic
  loss, conservative). Each ~20–40 lines numpy (**no River/sklearn** for compute).
- **`hardware_cost_meter(...)`** — the behavioral ADC-centred energy model (§2.3); the **BP+replay energy model** (matched
  retention, same per-op table); `readout_cost` = the MAC+solve unit-energy special case (the guard). **P8.7 extension:**
  a `substrate="analog"` (default — every frozen P8.0–P8.6 call unchanged, guards bit-exact) / `"digital"` switch
  (§2.5: `e_ADC=0`, `e_MAC=E_MAC_DIG`, `e_write=E_WRITE_DIG`; `e_mac_dig` overridable for the memory-wall sweep) on both
  `hardware_cost_meter` and `bp_replay_energy` — the SAME op-counts, different per-op physics. New figure `fig_substrate`
  (the 2×2 + the `E_MAC_DIG` sweep). New config block `E_MAC_DIG / E_WRITE_DIG / E_MAC_DIG_SWEEP / METER_CITE_DIG`.
- **`make_drift_stream(...)`** — the streaming CI schedule (gradual onset) + a **nuisance-covariate injector** (a smooth
  input transform SCFF is invariant to, boundary intact) + a **stationary segment**. Emits known real-drift onset markers
  (→ MTD) and nuisance markers (→ FAR). **The injector is calibrated at the raw-input/early-tap level** (prove the pixels
  shifted) with a separate check that the SCFF output's class direction barely moved (else FAR is vacuous).
- **Guards (run FIRST):** `partial_fit_equiv_guard` (`N`×`partial_fit`@λ=1 ≡ batch `fit`) · `live_path_anchor_guard`
  (`awake_sleep_loop` block-mode, gate=always-pay, sleep=every-boundary, **SCFF training ON** ≡ `continual_safety_heads`
  bit-for-bit — anchors the *live* path, not just the frozen one) · `scff_static_frozen_guard` (SCFF-update-off after
  `train_cell` pretrain ≡ the **P7.0/P7.1 static bake-off** accuracy — the only truly-frozen path) · `meter_proxy_guard`
  (MAC+solve sub-terms ≡ `readout_cost` under unit energies) · `detector_far_guard` (each detector on a stationary stream
  → its empirical FAR floor ≈ its nominal rate) · `cache_replay_guard` (non-trivial-fire arm ≡ cache replay) ·
  `fd_head_grad` (budget-gate). **Any guard fails → STOP.**

**Apparatus discipline:** `manifest.json` (git hash + config + seeds + versions + wall-clock + **the meter's per-op energy
params & citations**) + `arrays.npz`; `plot_p8.py regen <run-dir>` redraws every figure from saved data; `_ckpt.jsonl`
fsync'd. `OMP_NUM_THREADS=1 …`, `python -u`, `PYTHONIOENCODING=utf-8`, verify the PID on heavy cells. **CPU float64** (the
bit-exact guards need determinism). Commit per-rung on `main` (`feat(draft6/phase8): …`), end with
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

---

## 7. Owed decision-record deltas (flag at close; never retro-edit frozen arch files)

- **S6** (threshold-gated learning) → **resolves** to the committed detector + trigger once P8.1/P8.2 pick one.
- **The metered 80/20** → **replaces every "80/20 (proxy)" tag** once P8.5 lands (discharges the arch-file's "net energy win
  unquantified, deferred to Stage 2" — as a *behavioral* number).
- **S11 cost caveat** (RanPAC ~200× SLDA proxy) → **resolved** by P8.4's metered verdict.
- **S7** (sleep) → **extended** with the committed detector-driven cadence + `λ_ema` (was oracle-boundary).
- **N2** (EMA-view / drift-slowdown) → stays **Phase 9's** (P8 measures drift, doesn't tune it); the P8 cadence is
  drift-conditional on it.
- The **live co-adapting mechanism** (SCFF + gated namer + sleep, run together) → a **new supporting decision** if P8.6
  confirms it keeps the A6 win at the worst point: *the two-brain economy is continual-safe run live, not only in frozen
  characterization.*

---

## 8. The lab-manager review ledger (3-agent pre-run review — FOLDED 2026-07-02)

Three cold-start reviewers (repo-fit · red-team · literature). Verdicts: **READY-WITH-FIXES · SOUND-WITH-FIXES ·
SOUND-WITH-ADDITIONS.** Blockers + concerns and their resolution (all folded above):

| # | source | finding | resolution |
| --- | --- | --- | --- |
| B1 | repo-fit | heads have **no incremental accumulate**; op (c) + running-Gram framing not expressible | **build `partial_fit`** (running `G,M` + `λ_ema`) as the new primitive + its equivalence guard (§0.1, §2.1, §6) |
| B2 | red-team | inherited harness trains SCFF in **per-task blocks**, not a stream → boundary drift the oracle knows | **dual-mode `awake_sleep_loop`**; streaming mode is the real regime; **P8.0 pins the streaming schedule** (§2.1, §3) |
| B3 | red-team | P8.6 measured **post-sleep** → the awake gate's forgetting is invisible | **measure BWT at the worst mid-stream point (pre-sleep)** (§2.4, §3-P8.6, §4) |
| B4 | red-team | **`tap_drift` as MMD/mean-shift = magnitude-of-shift** → false-fires on nuisance (density≠class) | committed trigger = **class-direction tap-drift**; magnitude version = the false-fire **null** (§1, §2.2, §6) |
| B5 | red-team | metered 80/20 vs a **naive BP** that forgets = strawman | BP model = **BP+replay at matched retention, same substrate table** (§2.3, §3-P8.5) |
| B6 | repo-fit | `gate_off ≡ continual_safety_heads` needs a **block mode cloning the RNG choreography** | block mode spec'd; **`live_path_anchor_guard`** anchors the live path (§6) |
| B7 | repo-fit | "frozen ≡ P7" ambiguous — only the **static** bake-off was frozen | `scff_static_frozen_guard` pinned to P7.0/P7.1 static numbers (§6) |
| B8 | repo-fit | `stream_tap_cache` is **per-mini-batch new build**, not `stream_cache` reuse; RNG-order determinism | spec'd per-batch + RNG-order; cache guard uses a **non-trivial** arm (§6) |
| C1 | red-team | `f ≤ 0.25` retro-fit to the slogan | **frontier is primary; 0.25 a reference line**, not binary (§2.4) |
| C2 | red-team | "2× nominal δ" undefined for arms without a calibrated δ | FAR vs a **common empirical stationary floor** for all arms (§2.4, §4) |
| C3 | red-team | nuisance injector can pass **vacuously** (SCFF invariance masks a weak injector) | calibrate at **raw-input/early-tap**, separately show class-direction invariance (§4, §6) |
| C4 | red-team | error-rate framed as spine-clean | demoted to the **labeled reference**, not a spine exemplar (§1, §2.2) |
| C5 | red-team | cadence result **drift-rate-conditional** | flagged; re-tune if N2 (P9) slows drift (§2.2, §3-P8.3, §5) |
| C6 | red-team | RanPAC-vs-SLDA AA inherited from P7's **frozen** tie | AA **freshly measured live** in the P8.4 cut (§2.4) |
| C7 | red-team | blind spot: is the detection problem even well-posed on the stream | **P8.0 drift-visibility sanity panel** (§3-P8.0) |
| A1 | literature | **REMIND is the wrong cousin** (frozen backbone, feature storage) | re-cast as the **anti-pattern**; true cousin = raw-exemplar replay w/ recomputed prototypes (§0.2) |
| A2 | literature | **"ADWIN-U" is a real paper** (input moments) → false-fires on nuisance | renamed our arm `tap_drift_magnitude` (the null); ADWIN-U cited correctly as the input-moment method (§2.2, delta) |
| A3 | literature | **DriftLens** is the purpose-built label-free detector | added as the label-free **reference** trigger arm (§2.2, §6) |
| A4 | literature | gradual drift is the likely regime; DDM/ADWIN abrupt-biased | **conditional HDDM/RDDM arm** if P8.0 shows slow creep (§2.2) |
| A5 | literature | pin concrete **pJ anchors**; clamp the BP baseline to the same substrate | anchors cited (§2.3); BP substrate clamp (§2.3, B5) |

---

## Grounding (what the field does — and what we adopt)

- **The gate = off-the-shelf drift-detection** (DDM Gama 2004; ADWIN Bifet 2007; the benchmark [2606.07789]; "ADWIN
  flags virtual as real") → the arms + the false-fire axis. Label-free = a **trade curve** (DriftLens [2406.17813] /
  class-direction tap-drift ↔ STUDD [2103.00903] conservative; the magnitude/input-moment ADWIN-U end false-fires).
- **The false-fire vocabulary** (MTD / MTFA / FAR / MDR; the MTFA↔MTD trade) → §4.
- **The co-adapting backbone = representation/semantic drift** (our sleep = raw-exemplar replay w/ recomputed prototypes,
  iCaRL/GDumb-style; **REMIND = the frozen-backbone anti-pattern**; **SDC/LDC** [2407.08536] = the exemplar-free
  road-not-taken) → §0.2, §5.
- **The cost meter = a behavioral ADC-dominated CIM macro-model** (DNN+NeuroSim; ISAAC; PUMA; AIHWKit — Phase-6's noise
  source); SAR-ADC ≈ 0.2 pJ/conv-step, crossbar MAC < 100 fJ, ADC 5–50× area → §2.3.
- **Budgeted halting** (Skip-RNN [1708.06834] budget loss; PonderNet [2107.05407] the north-star ancestor) → the learned
  budget-gate + the direction-grounded halt.
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 discipline — carried from Phases 1–7
  ([`../result-format.md`](../result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure/metric → **add it to
> `result-format.md` first** (the next rung inherits it), never a one-off.
