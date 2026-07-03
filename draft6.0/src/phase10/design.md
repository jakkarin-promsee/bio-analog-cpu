# Phase 10 — The validation / showcase: race the frozen object (as a cost-frontier family) vs a fair BP (the plan)

> **Status: 🟡 READY-TO-RUN (plan hardened 2026-07-03; deep-research folded — §0.4 + [`../../research/papers/phase10/README.md`](../../research/papers/phase10/README.md);
> 3-agent lab-manager review folded — §8; kickoff-alignment second review folded — §9; nothing run, nothing committed to `main.ideas`).** A *live spec an agent executes* —
> the experiment ladder + build plan for the **Stage-2 close-out**: race the **frozen** two-brain object (handed over by
> Phase 9) against a **fair, budgeted** BP+replay baseline across the full continual gauntlet — the existential accuracy
> fight, the multi-domain money figure, and the noise showcase — and deliver an honest **Pareto**. When the rungs run they
> fill `expK/experiment-K.md`, `RESULTS.md`, then the public `README.md` + `phase10-report.md`, and finally rewrite
> [`../stage2-report.md`](../stage2-report.md) as the Stage-2 **close-out**. Reporting contract: [`result-format.md`](result-format.md).
> Literature: [`../../research/papers/phase10/README.md`](../../research/papers/phase10/README.md). The frozen object it races:
> [`../phase9/README.md`](../phase9/README.md) → the committed loop (`COMMITTED_LOOP` + `cadence_every=4`; provenance commit
> `59d2720`, arrays computed at parent `1fb11b3`). The economy + meter + substrate 2×2 it carries: [`../phase8/README.md`](../phase8/README.md)
> (P8.5 / P8.7). The whole model in one file: [`../phase9-final-architecture.md`](../phase9-final-architecture.md). The founding
> claim it tests: [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md). Stage-2 map: [`../stage2-design.md`](../stage2-design.md) §4.
>
> **Phase 10 = the fourth and last Stage-2 phase** (P7 readout ✓ · P8 economy ✓ · P9 close/freeze ✓ · **P10 validation /
> showcase**). Bar set with the author: **professor-convinced / showcase** — one fair baseline *family*, a legible gauntlet,
> an honest Pareto. **Not** a SOTA-benchmark chase. The headline the showcase must *earn* (not assume), in the author's
> words: **"our model uses less energy than modern GD"** — at competitive, honestly-reported accuracy. The whole phase's
> honesty rides on one cut: **freeze in P9, judge in P10** — the object is locked; P10 *measures*, and the verdict shapes are
> pinned **BLIND** before any baseline number is seen.

---

## 0 · Why Phase 10 exists — the existential hole, the reframe, and what it is NOT

### 0.0 The arc — everything is built; nothing is yet *validated as one object* against a fair opponent

Seven phases characterized *pieces*. The founding claim is a whole-system bet: **"an 80/20 forward-only continual learner
that beats backprop's economics *and* accuracy."** Phase 8 settled the **economics** (OURS ≈ half the energy of BP+replay;
15× vs GD-on-digital). But every continual **accuracy** win to date — Phase 1, Phase 4, the P8 live-safety check — was
measured against **naive online-BP with no replay.** That is a strawman, and it is the *first* thing an outside reviewer
attacks. And the research makes the opponent *stronger* than the rough plan assumed: under a matched **FLOPs-per-sample +
memory-in-bytes** budget, **a well-tuned experience-replay (ER) baseline outperforms the fancy CL methods** (Prabhu CVPR'23;
Ghunaim CVPR'23, §0.4). Until the frozen object races **a strong, budgeted ER** on **accuracy**, the headline is *supported,
not validated.*

Phase 10 is the **thesis defense.** It *measures*; it does not tune. Deliverables (§2.2): **(A)** the existential fair fight,
**(B)** the cadence-frontier family Pareto, **(C)** the multi-domain money figure, **(D)** the noise showcase — all on the
**frozen** object → an honest **Pareto** close-out.

### 0.1 The reframe — the frozen object shown as a 5-cadence *cost-frontier family* 🔥

The kickoff decision that shapes the phase: **do it like a frontier — make it rich.** Rather than racing a single point, we
present the model as a **family of 5 operating points along its one runtime cost dial — the sleep cadence** (`grid-N` = sleep
every N segments). This is the *same frozen object*; **every *learned* part is frozen** (SCFF bulk config, SLDA namer, DDM
gate, class-direction trigger, CBRS eviction, all-tap depth, proto-reanchor) — only the sleep **interval** changes. Phase 9
already characterized this exact frontier internally (the P9.5 `{2,4,5,6,8,16}` cadence re-confirm); Phase 10 races it against
the **external** BP baseline for the scaling story. The two tiers, straight from Phase 9's freeze:

| tier | grids | Phase-9 finding (worst-point BWT) | role in P10 |
| --- | --- | --- | --- |
| **Tier 1 — the sweet spot** | **grid-4 · grid-5 · grid-6** | grid-4 **−0.028** (the knee) · grid-5 **−0.039** · grid-6 **−0.087** — all pass the veto sign, but grid-6 is 0.059 worse than grid-4 (> δ_acc) | the viable frontier; **grid-4 = the committed frozen headline** |
| **Tier 2 — the poor tier** | **grid-8 · grid-16** | grid-8 **−0.317** (fails the veto; sparse-sleep troughs) · grid-16 AA **0.458** (fails accuracy; over-sparse) | the *degradation* arms — they make the scaling break legible |

*(The committed frontier P9.5 ran was `{2,4,5,6,8,16}`; grid-2 is the even-denser veto-passer at the dense end. The author's
chosen family is `{4,5,6,8,16}` — grid-2 is **omitted as the dense end past the committed knee** (grid-4); it can be added as
the densest Tier-1 point if the frontier wants extending. State the omission, don't hide it. **Post-close extension (§10):
grid-12 added to the home-stream family — {4,5,6,8,12,16} — to make the Tier-2 break's shape legible.**)*

**Freeze reconciliation (load-bearing honesty — hardened after the red-team review).** The frozen object *is* **grid-4, full
stop.** It is the existential-fight point (§2.2-A), it appears in **every** figure (including the money figure), and the
family is **never** swapped-in as "OURS." Sleep cadence is a **declared, transparent cost axis** (the x of every Pareto plot),
not a hidden knob turned to beat the baseline. The other four grids are shown as the object's own cost/capability trade curve
for the *scaling picture only*. For the 3-line continual **showcase** visualization we may add one Tier-1 **showcase
representative** beside grid-4 — but it is a *presentation choice for legibility, never a re-designation of the committed
object*, and it is admitted only if its worst-point BWT is **within δ_acc of grid-4's** (paired) — a condition **grid-6 fails
(−0.087 vs −0.028)**, so a "cheaper Tier-1 rep" is not free. **We never cherry-pick a per-dataset best grid and call *that*
"OURS."** Why it matters beyond P10: the cadence *is* the sleep mechanism, so how these five score **shapes the future of the
sleep design** (the author's stake) and the final model scorecard.

### 0.2 The one discipline — freeze in P9, judge in P10; pin the cuts BLIND (the honest inversion)

Phase 9's rule was **internal-signals-only** (never look at the P10 baseline while tuning). Phase 10 is the phase that *does*
consult the external baseline — that is its whole job — so the discipline inverts, and the honesty moves to a different cut:

> **The object was locked BEFORE any baseline number existed, and the verdict SHAPES (what counts as win / tie / loss) are
> pinned BLIND in this file BEFORE the racer runs.** Phase 10 then reports whatever the numbers say — **win or lose** —
> against the pinned shape. Touching a single *learned* knob (an N2 rate, an eviction bound, a temperature) to improve a
> comparison invalidates the fight (tuning-to-win); the only dial that moves is the **declared cadence cost axis** (§0.1).
> This is what lets the close-out answer *"did you tune against the baseline?"* with **no — here is the frozen manifest, and
> here are the cuts pinned before the run.**

### 0.3 What Phase 10 is NOT — the scope guard

- **NOT tuning.** The learned object is frozen (grid-4). The 5-grid family varies only the sleep *interval*; no learned
  weight, head, gate, objective, or buffer policy moves. Verdict shapes pinned **BLIND**.
- **NOT a benchmark-beat / SOTA chase.** Professor bar: **one fair baseline family** (BP+replay), a **legible** gauntlet (≈5
  domains, drop-in flat input), an **honest Pareto** — not ImageNet, not a 20-baseline table. Pretrained-backbone / prompt-CIL
  methods (L2P/DualPrompt/CODA-Prompt) are **out of scope**: they assume a large off-chip pretrained transformer; OURS's
  contribution is precisely the *unsupervised on-chip forward-only backbone that replaces* that pretrained one, so the fair
  comparator to it is **BP-trained-from-scratch + replay** (= ER), not a frozen ImageNet backbone (§8 A5).
- **NOT re-opening SCFF or the Namer** (Stage 1 / P7–P8 committed and frozen). A finding that *would* move them is a *flag for
  a future draft*, not a P10 re-run.
- **NOT SPICE / device physics.** Behavioral ADC-centred meter, carried from P8 (analog + digital substrate axes).
- **The fight can LOSE — and the two halves lose separately.** The founding claim has two halves — **economics** *and*
  **accuracy** — and P10 banks them **independently** (§7). An accuracy loss (OURS < ER-strong − δ_acc, 4/5) is banked plainly
  as *"the accuracy half of the founding bet is not supported,"* even if the energy Pareto is favorable. On a ~0.49-AA
  synthetic home a budgeted ER may well edge us — the honest-Pareto and dominated branches are *live*, not rhetorical.

### 0.4 The rough guess, and what the deep research changed (the honest-science record)

Per the project's pre-registration habit, the pre-research taste dump is banked (the 2026-07-03 concept in this file's git
history) and the deep-research pass ([`../../research/papers/phase10/README.md`](../../research/papers/phase10/README.md))
tested *"is it enough, and is there a better choice?"* Five deltas were folded:

| # | the rough guess | what the research changed |
| --- | --- | --- |
| D1 | "race BP+replay, matched buffer + compute" | budget = **FLOPs/sample + memory-bytes** (Prabhu CVPR'23); ER is the **strong** baseline (not a strawman) — run it **tuned**, meter its true energy; the guard matches FLOPs+bytes |
| D2 | "ER / A-GEM / DER++" | add **GDumb** (progress-questioning control, on the *accuracy* axis — it is cost-pathological, not an energy competitor) + keep **naive-BP** only as the *floor*; DER++ bytes count stored logits + its distillation raises FLOPs/sample; the budgeted-OCL SOTA (ICLR'25 layer-freezing) is an ER *accelerator* → folded into the ER-budget point, not a separate roster line |
| D3 | "ACC / BWT / FWT + plasticity + cost" | add **AAA (average anytime accuracy)** beside final AA — origin **OSAKA** (Caccia et al., NeurIPS'20, `2003.05856`); reporting-convention [2308.10328]. Pin the formula (§4) |
| D4 | "5-domain 28×28 sequence" | name it **domain-IL** (van de Ven), noting the shared-head/shared-index *semantics shift* is harder than permutation-style domain-IL; enforce the **shared input dim = 40** (the frozen bulk's input); **native Permuted/Rotated-digits is the PRIMARY protocol** (MNIST-family is not offline-loadable on this box — §6/§8) |
| D5 | "cumulative cost curve" | frame it as an **accuracy-vs-energy Pareto** (efficiency = normalized distance to the ideal corner); add the **throughput / steps-behind** read (Ghunaim's real-time payoff — cash the motivation, don't just cite it); the **load-bearing energy comparison is same-substrate** (OURS-digital vs ER-digital = the *algorithm* win), with OURS-analog-vs-GD-digital the *total* headline (substrate × algorithm), so the analog advantage is reported as a **meter-structural floor**, never the contestable number (§8 red-team #1) |

---

## 1 · The spine and the envelope (the two non-negotiables — every rung obeys them)

**The spine — read the class DIRECTION, never a MAGNITUDE.** In Phase 10 it lives in the **noise showcase** (D): the dangerous
analog enemy is a *coherent directional shift* along the class axis (Phase 6), so **retention** (not per-sample cosine) is the
direction measurement, and OURS's advantage is *directional* by construction. density ≠ class, cashed in on the assembled object.

**The envelope — GD reads taps, never writes SCFF (the P2.5 forward-leak wall, unbroken).** The frozen object already obeys it.

**Guards FIRST, every run — the netlist rule.** Import P9's tested primitives (all P8/P9 guards). Each new organ ships with its
own guard: the **fair-racer budget guard** (ER/A-GEM/DER++ metered on the *identical* per-op energy table as OURS; buffer
matched in **bytes**; per-learner **FLOPs/sample** reported — no strawman by construction); the **freeze-content guard**
(assert the frozen-knob **content manifest** — `COMMITTED_LOOP` + `cadence_every=4` + `HEAD="slda"` + the SLDA/cell config —
**and** that the grid-4 arm reproduces `phase9/exp5/figs_p9_5_cadence` grid-4 arrays bit-for-bit; the git hash `59d2720` is a
*provenance label*, not a runtime `==` check — §8 repo-fit #1); the **cadence-family guard** (each grid ∈ {4,5,6,8,16} runs the
committed loop with only `cadence_every` changed; grid-4 bit-exact); the **gauntlet-data guard** (every domain projects to the
shared **40-D** input, no label leakage; native data loads offline); the **noise-holdout guard** (the P10.4 battery is a
margin-disjoint operating point of `NoiseModel` vs P9.4's home residual — §6); the **substrate-identity guard** (`pred_analog
== pred_digital` bit-for-bit, so the substrate axis is honestly energy-only; **scope: every `NoiseModel`-off cell — P10.4's
noise arms are the declared exception**, where the substrate axis *is* the noise — §9 K4). **Any guard fails → STOP.**

---

## 2 · The mechanism, the deliverables, and the numeric verdict cuts (pinned BLIND)

### 2.1 What the object is, the family, and the substrate race

**The frozen object (races at grid-4).** `NoiseAugContrast` SCFF bulk (L12/w64, InfoNCE τ0.2/w2, per-sample L2 norm, one
noise-aug view σ1.0, no residual) · **SLDA** namer (RanPAC the reference) · **DDM** awake gate on the **class-direction
tap-drift** trigger · **all-tap** sleep consolidation · **CBRS** bounded-LUT eviction · **proto-reanchor** read-side defense ·
**grid-4** sleep cadence · envelope GD-reads-taps-never-writes. Both brains run **live** on the stream (SCFF learns
forward-only every step; the namer tracks the drift via the gate + sleep).

**The family (the declared cost axis).** The identical object at **grid ∈ {4,5,6,8,16}** — Tier-1 {4,5,6}, Tier-2 {8,16}. The
only difference is the sleep interval; all learned parts identical. grid-4 is the committed headline (§0.1).

**The substrate race (carried from P8.7) — and which comparison is load-bearing.** Accuracy is **substrate-independent**
(OURS-analog and OURS-digital compute the *same* math → identical predictions, asserted bit-for-bit by the substrate-identity
guard → identical accuracy; the substrate changes *energy* only). The energy story therefore has **two comparisons, and only
one is the contestable claim:**

- **The *algorithm* win (load-bearing, honestly contestable): `E(OURS-digital)` vs `E(ER-digital)`** — both on the *same*
  digital substrate table. This is the number a professor can attack, and the one the P10.1 win-cut gates on. (P8.7 measured
  it as the ~2.9× algorithm factor.)
- **The *total* headline (the money shot, but partly meter-structural): `E(OURS-analog)` vs `E(GD-digital)`** — the chip vs the
  status quo (~15×). Because the analog substrate prices crossbar MACs near-zero *by construction of the meter* (P8.7's ~5.4×
  substrate factor), `E(OURS-analog) < E(GD-digital)` is **largely guaranteed before the run** — so it is reported as the
  **substrate × algorithm total with the analog factor flagged as a meter-structural floor**, never as the contestable win
  (§8 red-team #1). The headline "less energy than modern GD" is the *total*; the *earned* claim is the algorithm win.

### 2.2 The deliverables

- **A · the existential fair fight** (P10.1) — OURS(grid-4) vs a **budgeted, tuned ER-strong** on **accuracy AND (same-
  substrate) energy**, continual home. The load-bearing number. Plus ER-budget / A-GEM / DER++ / GDumb / naive-BP populating
  the field, and the offline **joint-BP ceiling** overlaid as the dashed summit reference (accuracy-axis only, never a racer —
  §9 K1). *(The synthetic home is the **class-IL leg** — the Split-X complement the research names — so the gauntlet stays
  purely domain-IL; nothing is missing.)*
- **B · the cadence-frontier family Pareto** (P10.2) — the 5 grids on (accuracy × energy × worst-BWT); grid-4 the headline; the
  Tier-2 break made legible; the Tier-1 showcase rep selected *for visualization only* (§0.1).
- **C · the multi-domain adaptive gauntlet — the money figure** (P10.3) — new / 1-back / all-prev accuracy (reported at the
  **worst pre-sleep point per inter-sleep interval**, ER at the same convention) + AAA + cumulative energy + **throughput /
  steps-behind** across ≈5 domains; the continual showcase (money-figure lines: **grid-4 always plotted** + the Tier-1 rep + grid-8 +
  grid-16; **all five grids run**, so the per-domain CADENCE-FRONTIER strip shows which cadence each world likes — §9 K7)
  with **accuracy AND power** twin panels and the **sleep-position overlay**; the substrate 3-way; the SCFF:Namer ratio across
  difficulty.
- **D · the noise showcase on a HELD-OUT battery** (P10.4) — the gauntlet under {clean · iid · directional · ADC<3b ·
  nuisance-dim}, OURS-hardened vs BP+replay vs naive; the directional-enemy retention read (the Phase-6 payoff), honestly
  scoped where the held-out channel is not genuinely novel (§6).
- **A5 natural multi-class** (P10.5) — the fight on data a professor recognizes (may fold into C).
- **The verdict** (P10.6) — the **Pareto frontier** + the assembled-object figure + the Stage-2 close-out.

### 2.3 The numeric verdict cuts (PINNED BLIND — shapes with thresholds, never expected results)

`δ_acc = 0.02` (the house bar), paired by seed; a difference is **real** iff IQR-disjoint at the read point **AND**
sign-consistent in ≥4/5 paired seeds; retention re-checks run the full 5 seeds with the **paired-sign veto**; decisive gaps ≤
δ_acc get **9 seeds**. **Every cut is a SHAPE fixed before the run — no expected result is written.**

- **P10.0 — bench (the anti-strawman gate).** *No verdict — a build + guards.* Green iff: (a) ER's replay buffer == OURS's LUT
  in **bytes** and each learner's **FLOPs/sample** is reported (both an **ER-budget** at OURS's FLOPs and an **ER-strong** at
  its own good config are built); (b) both metered on the **identical** per-op table, per substrate; (c) the **freeze-content
  guard** passes (content manifest + grid-4 bit-exact); (d) the **cadence-family** reproduces grid-4 bit-for-bit; (e) the
  gauntlet data loads offline at the shared **40-D** input; (f) the **substrate-identity** guard passes (`pred_analog ==
  pred_digital`). **Any guard red → STOP.**
- **P10.1 — the existential fight (grid-4 vs ER-strong).** The accuracy reference is **ER-strong** (tuned, unthrottled — the
  honest bar; §8 red-team #5); the energy reference is **same-substrate** (`E(OURS-digital)` vs `E(ER-digital)`; §2.1). **(i)
  win** iff `acc(OURS) ≥ acc(ER-strong) − δ_acc` (paired) **AND** `E(OURS-digital) < E(ER-digital)` strictly; **(ii) honest-
  Pareto** iff `acc(OURS) < acc(ER-strong) − δ_acc` **but** `E(OURS-digital) ≪ E(ER-digital)` (report the ratio + the accuracy
  gap; the *accuracy half* is banked "not supported" per §7 even here); **(iii) dominated** iff `acc(OURS) < acc(ER-strong) −
  δ_acc` **AND** `E(OURS-digital) ≥ E(ER-digital)` (the founding bet fails on both halves — the headline, reported). The
  OURS-analog / GD-digital total is overlaid as the floor headline; naive-BP is the floor line; ER-budget is the same-FLOPs
  point; the **joint-BP ceiling** is the dash-dot summit reference (accuracy-axis only, energy annotated like GDumb's).
- **P10.2 — the cadence frontier (family).** Read the (accuracy × energy × worst-BWT) frontier over {4,5,6,8,16}. **grid-4 is
  the committed headline — never swapped.** A **Tier-1 showcase rep** (for the 3-line visualization only) may be named iff it
  is Pareto-non-dominated **AND** its worst-point BWT is **within δ_acc of grid-4's** (paired) **AND** its energy is
  IQR-disjointly lower — grid-6 (−0.087) fails the BWT condition, so the rep, if any, is grid-5. **Tier-2 break** confirmed iff
  grid-8 worst-BWT < −δ_acc vs oracle (forgetting) and/or grid-16 accuracy drops > δ_acc (under-consolidation). A Tier-2 hold
  is reported as a wider frontier.
- **P10.3 — the gauntlet (money figure).** Read three curves vs **ER-strong**: **plasticity** (new-task acc), **worst pre-sleep
  all-prev retention** (AA + BWT over history, at the worst mid-sleep-interval point — the P9 honest read, ER at the same
  convention; §8 red-team #7), **cumulative energy** (same-substrate for the claim; analog floor overlay) + **throughput /
  steps-behind**. **(i) showcase win** iff OURS worst-point all-prev retention within δ_acc of ER-strong **AND** `E(OURS-digital)`
  strictly lower at every domain boundary; **(ii) scaling limit** iff all-prev retention decays with #domains (report the
  slope); **(iii) ratio-not-scale-free** iff GD-share grows with domain hardness (flag). AAA reported beside AA. The gauntlet's
  **tuning asymmetry is stated blind**: OURS runs a *frozen-config* backbone (its claim is generality), ER gets its *own best
  per-domain config* (steel-manned) — so an OURS win is *despite* the handicap and a loss is honestly "a tuned end-to-end
  learner beats a frozen substrate on new domains" (§8 red-team #4).
- **P10.4 — the noise showcase (held-out).** Read directional-retention per environment vs BP+replay and naive. **(i) Phase-6
  payoff** iff OURS-hardened directional-retention beats *both* by the real-difference bar under a **genuinely-novel**
  directional environment (a different shift structure/axis than P9.4's fixed input-transducer translation — §6); **(ii) if the
  channel is only a new operating point of the *tuned* mechanism**, the claim is downgraded to *"confirms P9.4's defense at new
  noise levels"* (not a fresh payoff — the honest read; §8 red-team #3); **(iii) residual bites** iff OURS drops > δ_acc under a
  held-out channel → **named → analog-realism layer** (a scoped hand-off, not a P10 failure).
- **P10.5 — A5 natural multi-class.** Read the win/tie/loss on natural data (digits / MNIST-784→40 / CIFAR-flat→40) using the
  same Pareto shape. Synthetic overstates gaps both ways; the recognizable-data confirm. May fold into P10.3.
- **P10.6 — the Pareto verdict + close-out.** *Not a scalar.* Assemble the frontier; state **where OURS wins / ties / loses**,
  each with its number and mechanism; bank the **economics** and **accuracy** halves separately (§7); rewrite the Stage-2 report
  as the close-out.

**No result may be narrated into a branch it does not numerically satisfy.** A dominated fight, a Tier-2 grid that holds, a
residual that bites, a downgraded noise claim — each is a card with its mechanism, logged and reported (failures are data).

---

## 3 · The ladder — P10.0 → P10.6 (one variable per rung; guards first; each states its read-including-failure BEFORE it runs)

- **P10.0 — bench: the fair racer + the gauntlet harness + the guards.** Build `p10lib` on `p9lib`; build the **BP+replay
  learners** (real code — §6: ER-budget/ER-strong/naive + GDumb as load-bearing; A-GEM/DER++ as field points on the
  grad-exposed MLP), each metered with `bp_replay_energy` on the identical per-op table + the **new byte/FLOPs budget meter**;
  the **native domain-IL gauntlet harness** (`make_gauntlet_stream`, shared 40-D input, shared head) + the **data loader**
  (native primary, MNIST-784→40 optional); the **cadence-family runner** (grid ∈ {4,5,6,8,16}); the **held-out noise battery**.
  Run the P9 guard set + the six new guards (fair-racer-budget · freeze-content · cadence-family · gauntlet-data ·
  noise-holdout · substrate-identity). **Read (incl. failure):** *all green → proceed / racer not byte/FLOPs-matched, freeze
  content mismatched, data won't load at 40-D, or preds differ across substrate → STOP (a broken bench poisons every verdict).*
- **P10.1 — the existential fight (grid-4 vs ER-strong).** Swept variable = learner ∈ {OURS(grid-4), ER-strong, ER-budget,
  A-GEM, DER++, GDumb, naive-BP} (+ the **joint-BP ceiling** as a non-raced dashed reference — §9 K1), continual home, 5 seeds. Score **accuracy × same-substrate energy** (the Pareto point) + BWT +
  AAA. **Read:** *OURS on/above the frontier vs ER-strong (win) / below on accuracy but far cheaper (honest-Pareto; accuracy
  half not supported) / dominated (the bet fails — reported).* The load-bearing rung.
- **P10.2 — the cadence frontier (the family).** Swept variable = the sleep cadence grid ∈ {4,5,6,8,16} (the declared cost
  axis), object otherwise frozen, 5 seeds. Score **accuracy × energy × worst-BWT**. **Read:** *grid-4 the headline; Tier-1
  showcase rep (visualization only, δ_acc-worst-BWT-gated → grid-5 candidate, grid-6 fails); Tier-2 break / an unexpected hold.*
- **P10.3 — the multi-domain gauntlet (the money figure).** Controls: the frozen object at **all five grids** (the money
  figure draws grid-4 + the Tier-1 rep + grid-8 + grid-16; the per-domain CADENCE-FRONTIER strip draws all five; demotion
  order under wall-clock pressure, pre-registered: grid-6 first, then non-rep grid-5 — §9 K7) vs ER-strong
  (+ ER-budget/A-GEM/DER++/GDumb field + the joint ceiling), across ≈5 native domain-IL datasets, 5 seeds, **+ one
  order-shuffle control** (the reversed domain order; grid-4 + ER-strong only, 5 seeds — the AA order-delta is reported; a
  verdict that flips under order is reported order-sensitive — §9 K9). Score **new / worst-pre-sleep 1-back / worst-pre-sleep all-prev accuracy + AAA + cumulative same-substrate energy +
  throughput + SCFF:Namer ratio vs difficulty**; overlay **sleep positions**. **Read:** *flat retention at low cost (showcase) /
  retention decays with #domains (scaling limit) / cost creeps toward BP on hard domains (ratio not scale-free — flag).*
- **P10.4 — the noise showcase (held-out battery).** Swept variable = the environment ∈ {clean, iid, directional, ADC<3b,
  nuisance-dim}; learners = OURS-hardened vs BP+replay vs naive (**optional steel-man if the week allows: + ER-strong trained
  with the same iid noise augmentation** — the hardware-aware-training convention; a match on the directional channel is
  reported plainly, and the differentiator narrows to the channels OURS alone survives — §9 K10); battery margin-disjoint
  from P9.4 (guard), 5 seeds. Score
  **directional-retention** per environment. **Read:** *OURS holds under a novel directional enemy (payoff) / only confirms
  P9.4 at new levels (downgrade) / a held-out channel bites → named → analog layer.*
- **P10.5 — A5 natural multi-class.** Controls as P10.1/P10.3 on natural data. Score the Pareto point on recognizable data.
  **Read:** *the win/tie/loss a professor recognizes / synthetic overstated the gap (state the direction).* Fold into P10.3 if
  the gauntlet is already natural.
- **P10.6 — the Pareto verdict + the Stage-2 close-out.** Assemble the frontier + the assembled-object figure; bank the
  economics/accuracy halves separately; rewrite the Stage-2 report as the close-out. **Read:** *the honest map — win / tie /
  loss, each with its number and mechanism.*

*(The object is frozen; these rungs *measure*. Verdict shapes pinned BLIND. Heavy live cells (P10.1, P10.3, P10.4) checkpoint +
single-thread + verify PID — the phantom-hang discipline. Seeds `[42,137,271,314,1729]`, median + IQR, paired-sign veto on
retention; decisive gaps ≤ δ_acc get 9 seeds.)*

**Dependency order (load-bearing).** P10.0 gates everything. P10.1 (the fight at grid-4) and P10.2 (the family) run once the
bench is green; P10.3 inherits P10.2's Tier-1 rep. P10.4 is independent. P10.5 folds into P10.3 if the gauntlet is natural.
P10.6 assembles all.

---

## 4 · Metrics (PINNED; Phase-10 additions in **bold**; the rest carried from P8/P9)

| metric | definition (pinned) | units / format |
| --- | --- | --- |
| continual **ACC / AA** | mean acc over all seen tasks (GEM `acc_matrix_metrics`); the live read is the **worst pre-sleep point per inter-sleep interval** (the P9 honest convention), ER at the same convention — on a **fixed, learner-independent eval-checkpoint grid** (every k steps, k pinned at P10.0), the same OURS-sleep interval boundaries applied to every learner (§9 K12) | acc, median [IQR] |
| **AAA (average anytime accuracy)** | mean over stream-checkpoints of AA(t), AA(t) = mean acc over tasks-seen-so-far at checkpoint t (origin OSAKA, Caccia NeurIPS'20 `2003.05856`; convention [2308.10328]) | acc, median [IQR] |
| continual **BWT / Forgetting** | GEM/CL conventions; worst mid-stream point (pre-sleep) for the live veto | acc-delta |
| **FWT** (bonus) | forward transfer — does old learning help new tasks (GEM) | acc-delta |
| **plasticity / 1-back** | acc on task *t* right after learning *t* (plasticity); acc on *t−1* after *t* (1-back, worst pre-sleep) | acc, median [IQR] |
| **the Pareto point** | (accuracy, energy) per learner/grid; efficiency = normalized dist to the (max-acc, min-E) corner | (acc, E) |
| **algorithm energy (load-bearing)** | `E(OURS-digital)` vs `E(ER-digital)` — same digital substrate; the contestable win | relative-E |
| **total energy (headline, floor-flagged)** | `E(OURS-analog)` vs `E(GD-digital)` = substrate × algorithm; the analog factor is a meter-structural floor | relative-E vs step |
| **throughput / steps-behind** | from the **metered FLOPs/sample** (the same instrument that prices energy; replay + amortized sleep included): the declared real-time budget is `C_stream` = OURS(grid-4)'s FLOPs/sample; each learner's drop-fraction = max(0, 1 − C_stream/FLOPs_L) + its relative complexity FLOPs_L/C_stream (the Ghunaim read; OURS is 0-behind by construction — declared). **Wall-clock is NOT the instrument** (a python/numpy vectorization artifact) — a manifest footnote only (§9 K3) | count / fraction |
| **fair-budget audit (new instrument)** | ER/A-GEM/DER++ **FLOPs/sample** (from the meter's internal MAC counts) + replay **bytes** (`nbytes`), matched to OURS | FLOPs · bytes |
| **SCFF:Namer ratio (GD-share) vs difficulty** | metered GD-share per domain — the "final ratio," characterized | fraction |
| **directional noise-retention** | class-direction retention vs noise level per held-out environment, OURS vs BP vs naive | retention ratio |
| **sleep-position overlay** | the stream-steps a consolidation fired, marked on the retention curve | step markers |

**Threats-to-validity, every rung:** (a) the meter is a **behavioral model** — log/cite per-op params, sensitivity-check the
ADC-dominance; **the analog energy factor is meter-structural — never the contestable claim**; (b) the fair fight depends on
the **ER budget/tuning** — a crippled ER makes the win vacuous (match FLOPs+bytes *and* tune ER-strong; report both budget and
strong; the tuning consumes only the **disjoint tuning stream** — seed ∉ raced set — never the raced seeds, §9 K2); (c) the
gauntlet depends on the **domain set + order + the frozen-config-vs-per-domain-tuning asymmetry** (state all
three; the reversed-order control at grid-4 + ER-strong is **committed**, §9 K9); (d) synthetic **overstates** static gaps — A5/natural is the honest read; (e)
the noise battery is a **margin-disjoint** operating point of the *same* transducer model — a genuinely-novel channel earns
"payoff," a re-parameterized one earns "confirms"; (f) accuracy is **substrate-independent** (guarded `pred_analog ==
pred_digital`) — the substrate axis lives only in energy (never double-count it in accuracy); (g) **GDumb is cost-pathological**
(trains from scratch at eval) — reported on the accuracy axis, annotated on the energy axis, never used to inflate the Pareto;
(h) **parameter/memory asymmetry** — OURS's bulk carries more weights than the racer MLP; the budget matches FLOPs/sample +
replay-bytes and **reports** total memory (model + state + buffer) per learner; the racer's shape is its own `race_bp`-tuned
choice, not capped (§9 K6).

---

## 5 · What Phase 10 hands the close-out / defers (the seam, stated so nothing is lost)

- **→ the Stage-2 close-out ([`../stage2-report.md`](../stage2-report.md)):** the **Pareto verdict** (win/tie/loss on accuracy ×
  energy × retention × noise, each with its number), the **money figure**, the **throughput read**, and the **final
  characterized SCFF:Namer ratio.** The report is rewritten from "living / in-progress" to a closed Stage-2 arc.
- **→ the analog-realism layer (SPICE / PVT), named:** any noise channel P10.4 shows the read-side defense cannot reach → named
  with its mechanism; the absolute-Joule / PVT layer the behavioral meter cannot give.
- **→ the professor pack (the author's next-week meeting):** at P10.6 assemble `phase10/professor-brief.md` (extends the
  P8.7 why-analog brief): one page — the object in one paragraph, the GAUNTLET + PARETO + SUBSTRATE figures, the founding
  bet's two halves stated separately (win / honest-Pareto / not-supported, whichever the numbers say), and the two honesty
  lines the professor will test first (*the analog factor is a meter-structural floor; the load-bearing energy win is
  same-substrate*). (§9 K11.)
- **→ the north star (deliberately not specced):** the cosine spine-pure head (P7) and the better-than-confidence exit (P5) —
  a **tie-break bias** only; P10 adds no recurrence.
- **→ a future draft (flag, do not execute):** anything the fight reveals that would move a *frozen* Stage-1/2 decision (a
  convolutional bulk to lift static accuracy / the CIFAR wall; a pretrained-backbone comparison) — flagged, never a P10 re-run.

---

## 6 · What to build — `p10lib.py` on `p9lib` (import, don't retype — the netlist rule)

**Verified-present carries (import — from `p9lib`, which re-exports p8/p7/p6/p5…):** `awake_sleep_loop`, `run_economy_p9`/
`run_economy`, `SLDAHeadStream`/`RanPACHeadStream` (+ `partial_fit`/`sleep_fit`), `make_committed_cell` (p6/p7), `train_cell`,
`make_lifelong_stream`, `StreamingLUT` + eviction policies (**store-level** `evict_cbrs(store,cap,rng,C)` etc. — not a
feature-level `(F,Y)` API), `proto_reanchor`, `acc_matrix_metrics`, `hardware_cost_meter`, `meter_from_trace` (with
`substrate=`), **`bp_replay_energy`** (the substrate-aware BP+replay **energy** model — energy-only, trains nothing),
**`race_bp`** (p4lib — a **hyperparameter *config selector*** returning the chosen `dims`/`lr`; *not* a reusable stateful
learner — instantiate the `MLP` from its output), `MLP` (p4lib — per-minibatch `train_step`), `load_digits_split`,
`load_cifar_flat` (p5lib), `linear_probe`, `CISTREAM_TASKS`, `synth_stream`, `NoiseModel`/`infer_noisy` (p6lib, via the
`../phase6` sys.path), and **all P8/P9 guards** (the `_guard`-suffixed names). The committed loop config is `p8cfg.COMMITTED_LOOP`
+ `cadence_every=4` (input dim **`DIM=40`** + `[64]*12`).

**NEW to build for Phase 10** *(each names the deliverable it serves + the review finding it closes):*
- **The continual BP+replay learners (real code — the bulk of P10.0's work; §8 repo-fit #5).** `ContinualBP(policy=∈{er,
  agem, derpp, gdumb, naive})` on `MLP` (shape/lr from `race_bp`) made **online** + a **replay buffer** (reservoir; class-
  balanced for GDumb). **Load-bearing roster: ER-budget, ER-strong, naive, GDumb** (GDumb = greedy-balanced buffer +
  **from-scratch retrain at each eval point**). **Field roster (needs MLP refactor): A-GEM** (expose `grad()`/`apply_grad()`
  on `MLP` for the one-projection constraint), **DER++** (a **logit buffer** + a distillation term — its bytes count logits,
  its FLOPs/sample counts the extra forward). If the refactor is too heavy, A-GEM/DER++ are **descoped to documented-simplified
  field points** and ER(budget+strong)+naive+GDumb carry the verdict (**decide the descope AT P10.0, time-boxed — not
  mid-fight**). **ER-strong tuning protocol (pinned — §9 K2):** hyperparameters (lr, replay ratio/steps, batch; shape via the
  `race_bp` selector) are selected on a **tuning stream from a seed outside the raced set** (e.g. seed 7) with its own val
  split, selection metric = final AA; the raced seeds `[42,137,271,314,1729]` are never consumed during tuning; the search
  grid + the chosen config land in the manifest; the same budgeted search is offered to each field learner. Energy via
  `bp_replay_energy`. **Deliverable A/C.**
- **`joint_bp_ceiling(...)` (the summit reference — §9 K1).** The `race_bp`-selected MLP trained offline, multi-epoch, on the
  pooled stream data (all tasks/domains jointly, standard split) — the dash-dot **ceiling line** the reporting contract
  already requires (result-format §A STYLE + §E slot 2). Accuracy-axis only: its training energy is annotated like GDumb's,
  never a Pareto competitor; a reference, not a racer. Cheap; runs once per stream.
- **`fair_budget_meter(...)` + `fair_budget_guard(...)` (new instruments — NOT a carry; §8 repo-fit #6).** A **byte counter**
  (`.nbytes` on OURS's `StreamingLUT` arrays and each racer's buffer) + a **per-sample FLOPs counter** (expose the MAC counts
  already computed inside `hardware_cost_meter`/`bp_replay_energy` as FLOPs). The guard asserts ER-buffer-bytes == LUT-bytes and
  reports FLOPs/sample per learner; builds the **ER-budget** (throttled to OURS's FLOPs) + **ER-strong** (own config) points;
  and reports **total memory** per learner (model + optimizer/state + buffer bytes) beside the matched replay-bytes — the
  buffer is the *matched* knob, the totals are *reported* (threat (h), §9 K6).
- **`make_gauntlet_stream(domains, seed, *, scenario="domain-il")` + `load_gauntlet_data(...)` (native primary; §8 repo-fit
  #2/#3, lit #2).** Sequences ≈5 domains, **all projected to the shared 40-D bulk input** (fixed seed-frozen random projection
  / PCA-to-40), shared head. **Native primary set** (offline-guaranteed): a synthetic Gaussian domain + Permuted-digits + Rotated-digits +
  CIFAR-flat-gray→40 **+ MNIST-784→40, promoted to primary IFF the P10.0 data guard confirms the local cache loads offline**
  (expected — it is the one cached set; else it reverts to optional) = the ≈5. **Best-effort, NON-GATING prefetch (§9 K8):**
  at bench time (P10.0, never inside a live cell) attempt Fashion-MNIST (+ KMNIST) with checksums; a set that lands joins as
  a **declared bonus domain appended after the primary five** (order pre-registered) — the outside-legibility upgrade; if the
  network fails, the primary five stand and nothing blocks. Emits
  per-domain onset markers + the sleep-position overlay hooks. **`gauntlet_data_guard`** asserts one 40-D input + no label
  leakage + offline load + **ONE pinned →40 projection mechanism, repo-consistent with the existing
  `load_digits_split`/`load_cifar_flat` path (verify which at P10.0; state it in the manifest), applied identically to every
  domain** + **every learner consumes the bit-identical projected stream** (input-identity across learners — §9 K5).
  **Never call `fetch_openml` for an uncached set inside a live cell** (the network/phantom-hang guard).
- **`cadence_family_runner(grid ∈ {4,5,6,8,16})` + `cadence_family_guard` (§8 repo-fit #4).** Runs `{**COMMITTED_LOOP,
  cadence_every:g}`; the guard rebuilds the grid-4 arm and asserts equality to `phase9/exp5/figs_p9_5_cadence` grid-4 slice
  bit-for-bit. (grid-2 omitted per the chosen family — the dense-end note, §0.1.)
- **`freeze_content_guard` (§8 repo-fit #1 + red-team #9).** Asserts the frozen-knob **content manifest** (`COMMITTED_LOOP` +
  `cadence_every=4` + `HEAD="slda"` + the SLDA/cell config) **and** grid-4 bit-exact reproduction. `59d2720` = provenance label
  in the manifest; **not** a runtime git `==` check (no artifact carries it; parent is `1fb11b3`).
- **`held_out_noise_battery(...)` + `noise_holdout_guard` (§8 repo-fit #8 + red-team #3).** {clean, iid, directional, ADC<3b,
  nuisance-dim} via `NoiseModel`, **margin-disjoint** from P9.4's home residual (`RESID_INPUT_RMS=1.5`, `RESID_ADC_BITS=2`) —
  the guard asserts a concrete margin AND flags whether the directional channel is a *genuinely-novel structure* (→ "payoff"
  claim) or a *re-parameterized* one (→ "confirms" claim). **Deliverable D.**
- **`throughput_meter(...)` (§8 red-team #8 + lit #4; re-instrumented §9 K3).** From the **metered FLOPs/sample** (the same
  counts that price energy; replay + amortized sleep included): declared budget `C_stream` = OURS(grid-4)'s FLOPs/sample;
  drop-fraction = max(0, 1 − C_stream/FLOPs_L) + relative complexity per learner (OURS 0-behind by construction — declared).
  **Wall-clock is NOT the instrument** (a python/numpy vectorization artifact) — a manifest footnote only. **Deliverable C.**
- **`substrate_identity_guard`, `pareto_frontier(...)`, `gauntlet_metrics(...)`** — the `pred_analog==pred_digital` assert
  (**scope: `NoiseModel`-off cells only; P10.4's noise arms are the declared exception** — §9 K4); the
  (acc, energy) frontier assembler; the new/1-back/all-prev/AAA extractor (worst-pre-sleep convention, on the fixed
  learner-independent eval-checkpoint grid) from the acc-matrix.
- **Guards (run FIRST):** all P8/P9 guards + `fair_budget` + `freeze_content` + `cadence_family` + `gauntlet_data` +
  `noise_holdout` + `substrate_identity`. **Any guard fails → STOP.**

**Apparatus discipline (carry P8/P9 verbatim):** `manifest.json` (git hash + resolved config + seeds + versions + wall-clock +
the meter's per-op energy params & citations + **the frozen-object content manifest + provenance `59d2720`** + **the racer's
FLOPs/bytes budget**) + `arrays.npz`; `plot_p10.py regen <run-dir>` redraws every figure from saved data; `_ckpt.jsonl`
fsync'd. `OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`, **verify the PID alive on heavy live cells**. **CPU
float64.** **No sklearn / no River for compute** (GDumb's balanced sampler + any diversity scorer hand-rolled single-threaded;
data loading is local-cache + numpy only). Commit per-rung on `main` (`feat(draft6/phase10): …`), end with
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

---

## 7 · Owed decision-record deltas (flag at close; never retro-edit frozen arch files)

Phase 10 is *validation*, so it sets no new *design* knob — but its verdict is a recordable decision. To bank to
[`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) at close (the way S10–S13 were), **flagged here, not silently
applied — and the founding bet's two halves banked SEPARATELY (§8 red-team #6):**
- **The founding bet — ECONOMICS half** → **validated / not** (P10.1/P10.3 same-substrate algorithm energy + P8.7 total).
- **The founding bet — ACCURACY half** → **validated / honest-Pareto (not supported) / not** (P10.1/P10.3 vs ER-strong — the
  debt Phase 4 flagged, discharged with its verdict either way; an accuracy loss is banked plainly, even under a favorable
  energy Pareto).
- **The cadence cost-frontier** → a **new supporting decision** (the model's declared operating-point family {4,5,6,8,16};
  grid-4 the committed headline, no swap; the sleep-design characterization the author flagged as shaping the future).
- **The final SCFF:Namer ratio** → **characterized** across difficulty (was assumed ~0.12–0.18).
- **The noise showcase** → the Phase-6 arc **cashed on the assembled object** (held-out, honestly scoped); any residual **named
  → analog layer**.
- **The Stage-2 close-out** → the neocortex brain (cheap unsupervised structure + a gradient-free continual-safe namer + a
  metered economy + a frozen lifelong loop) is **done**; the report closes.

---

## 8 · The lab-manager review ledger (3-agent pre-run review — FOLDED 2026-07-03)

Three cold-start reviewers (repo-fit · red-team · literature). Verdicts: **READY-WITH-FIXES · SOUND-WITH-FIXES ·
SOUND-WITH-ADDITIONS.** Four findings **converged** across independent reviewers (⊕) — the strongest signal they are real. All
folded above.

| # | source | finding | resolution |
| --- | --- | --- | --- |
| B1 ⊕ | red-team + repo-fit | the **freeze hash `59d2720` is unimplementable as a runtime `==` check** — it is the run commit; every P9 manifest carries parent `1fb11b3`; no artifact carries `59d2720` | anchor the freeze on the **content manifest** (`COMMITTED_LOOP`+`cadence_every=4`+SLDA/cell) + **grid-4 bit-exact reproduction**; `59d2720` = provenance label (§1/§6 `freeze_content_guard`) |
| B2 ⊕ | repo-fit + lit | **MNIST-family is not offline-loadable** (only MNIST cached; no Fashion/KMNIST/notMNIST/EMNIST; no torchvision; network unreliable) — and the shared-head maps *conflicting* class semantics | **native Permuted/Rotated-digits + CIFAR-flat-gray + synthetic = the PRIMARY domain-IL gauntlet** (offline-guaranteed); MNIST-784→40 an optional legibility bonus; the semantics-shift noted (§0.4-D4/§6) |
| B3 ⊕ | red-team + lit | the **throughput / steps-behind** read (the Ghunaim real-time payoff) is *motivated* but *unmeasured* | add `throughput_meter` to the money figure (§4/§6) — cash the motivation, don't just cite it |
| B4 ⊕ | red-team + repo-fit | the **noise held-out battery is thin** — same transducer mechanism, only params differ; the "payoff" may test the exact channel proto-reanchor was tuned on | guard a **concrete margin** + flag genuinely-novel-structure ("payoff") vs re-parameterized ("confirms"); downgrade the claim honestly where not novel (§2.3-P10.4/§6) |
| R1 | red-team | the **energy win is largely pre-baked by the analog meter** (`E(OURS-analog) < E(GD-digital)` is ~guaranteed by the CIM cost model) | the **load-bearing energy cut is same-substrate** (`E(OURS-digital)` vs `E(ER-digital)` = the algorithm win); analog = a **meter-structural floor** overlay, never the contestable claim (§2.1/§2.3) |
| R2 | red-team | the **cadence-swap clause is a loophole** — grid-6 (−0.087) is > δ_acc worse than grid-4 (−0.028) yet the swap only checked the veto sign | **grid-4 is the frozen headline, no swap**; a Tier-1 *showcase rep* (visualization only) needs worst-BWT **within δ_acc of grid-4** → grid-5 candidate, grid-6 fails; grid-4 always plotted (§0.1/§2.3-P10.2) |
| R3 | repo-fit | the **frozen bulk input dim is 40**, not 784 — the "28×28 MNIST-family" is un-forwardable as-is | pin the gauntlet's shared input to **40-D**; project every domain to 40 (seed-frozen) (§6 `make_gauntlet_stream`) |
| R4 | red-team | the **"we lose on accuracy" branch has no teeth** — routed to "honest-Pareto win"; the founding claim's two halves conflated | bank **economics** and **accuracy** halves **separately** (§7); an accuracy loss is "the accuracy half is not supported," plainly, even under a favorable energy Pareto |
| R5 | red-team + repo-fit(#9) | the accuracy bar was **generic ER** (could be a throttled strawman); the frozen home AA is ~0.49 so a loss is live | pin the accuracy cut against **ER-strong** (tuned, unthrottled); ER-budget is the same-FLOPs energy point only (§2.3-P10.1) |
| R6 | red-team | **worst pre-sleep** BWT (P9's honest read) vs P10's **final-AA** cut are inconsistent — sleep can smooth troughs | the gauntlet retention read is **worst pre-sleep AA per inter-sleep interval**, ER at the same convention (§2.3-P10.3/§4) |
| R7 | repo-fit | the **BP+replay learners + the FLOPs/bytes meter are real new builds**, not carries; `race_bp` is a *config selector*, `evict_*` are store-level | §6 corrected: `ContinualBP` real code (A-GEM grad-handle, DER++ logit buffer, GDumb retrain); `fair_budget_meter` a new instrument; `race_bp`=selector |
| R8 | red-team | **substrate-independence of accuracy** is asserted, not guarded | add `substrate_identity_guard` (`pred_analog == pred_digital` bit-for-bit) (§1/§6) |
| A1 | lit | **AAA misattributed** to [2308.10328] | cite **OSAKA** (Caccia NeurIPS'20 `2003.05856`) as origin; [2308.10328] the convention; pin the formula (§4) |
| A2 | lit | the **budgeted-OCL SOTA** (ICLR'25 layer-freezing) is cited-not-rostered | scoped out with a defense — it is an ER *accelerator*, folded into the ER-budget point (§0.4-D2) |
| A3 | lit | **GDumb is cost-pathological** (from-scratch retrain) — could flatter OURS on the energy axis | report GDumb on the **accuracy axis** (its intended control role), annotate its energy point "not an energy competitor" (§4-g) |
| A4 | lit | a **pretrained-backbone / prompt-CIL** flank is unanswered | one defensive sentence: OURS *replaces* the off-chip pretrained backbone → the fair comparator is BP-from-scratch+replay (§0.3) |
| A5 | lit | **DER++ FLOPs asymmetry** (distillation adds a forward) is unstated | the fair-budget audit reports FLOPs/sample per learner + the budget-matched-vs-native rationale across the roster (§6) |

**Not changed (checked, defended):** the blind-pinned verdict shapes; guards-first; failures-are-data; the freeze/judge
inversion; the spine (directional retention, not magnitude); the no-sklearn/CPU-float64/phantom-hang discipline; the scope
guard excluding SPICE + pretrained-backbone methods. The literature reviewer verified every load-bearing arxiv ID as correct
except the AAA-origin (A1); no other blocker-grade misuse.

---

## 9 · The kickoff-alignment second review (author Q&A + one external fairness pass — FOLDED 2026-07-03)

A second, independent pass after §8: align the spec to the author's kickoff answers (the 5-size frontier presentation,
"you decide the datasets," the 3-substrate showcase, sleep-position as the visible mechanism, the professor meeting the
week after the run) and re-check fairness with outside eyes. All folded above; K-numbered.

| # | finding | resolution |
| --- | --- | --- |
| K1 | the **joint-BP ceiling is required by the reporting contract** (STYLE ceiling line, §E slot 2, the caption rule) **but no rung builds it** | build `joint_bp_ceiling` (`race_bp` MLP, multi-epoch, pooled data) as a **dashed reference line** — accuracy-axis only, energy annotated like GDumb's, never a racer (§2.2-A / §2.3 / §6); it answers the professor's first question, "what is the summit?" |
| K2 | **"ER-strong tuned" had no tuning protocol** — tuned on the raced stream would be judging on the judge's training set | pinned: tuning stream = seed ∉ raced set + its own val split; selection = final AA; grid + config in the manifest; the same search offered to the field (§6, threat (b)) |
| K3 | **throughput via wall-clock is a numpy artifact** — vectorization quality, not the substrate, would set the number | steps-behind re-defined on the **metered FLOPs/sample** (`C_stream` = OURS grid-4; drop = max(0, 1 − C_stream/FLOPs_L)); wall-clock a footnote (§4 / §6) |
| K4 | the **substrate-identity guard collides with P10.4 by design** (noise arms break pred-equality on purpose) | guard scoped to `NoiseModel`-off cells; P10.4 the declared exception (§1 / §6) — an executor trap, now stated |
| K5 | the racers' **input stream was not pinned identical** to OURS's, and the →40 mechanism was ambiguous (random-proj vs PCA) | the gauntlet guard asserts a **bit-identical projected stream for every learner** + ONE pinned projection, repo-consistent with the existing loaders, stated in the manifest (§6) |
| K6 | **total-memory asymmetry unstated** (OURS's bulk carries more weights than the racer MLP — a reviewer's poke) | the fair-budget meter reports total bytes (model + state + buffer) beside the *matched* replay-bytes; threat (h) (§4 / §6) |
| K7 | the author asked to **see all five grids per dataset** ("which grid is best in each world"); the plan ran only 3–4 arms on the gauntlet | **all five grids run on the gauntlet**; the money figure keeps its 3–4 headline lines; a **per-domain CADENCE-FRONTIER strip** shows the full family; demotion order (grid-6, then non-rep grid-5) pre-registered under wall-clock pressure (§2.2-C / §3-P10.3) |
| K8 | outside-legibility under-served: MNIST is cached yet "optional"; the author's dream gauntlet was a recognizable family | MNIST-784→40 **conditionally promoted to primary** (iff the cache check passes); **best-effort non-gating Fashion-MNIST/KMNIST prefetch** at bench time — declared bonus domains if they land, nothing blocks if not (§6) |
| K9 | **order sensitivity** was "if feasible" — too soft for the first outward-facing figure | the reversed-order control (grid-4 + ER-strong, 5 seeds) is **committed**; the AA order-delta reported (§3-P10.3 / §4-(c)) |
| K10 | the noise showcase's obvious flank: "BP could just train with noise too" (hardware-aware training is standard practice) | optional steel-man arm: ER-strong + the same iid noise-aug — run if the week allows; a match is reported plainly and the claim narrows honestly (§3-P10.4) |
| K11 | the phase ends at the close-out, but the author's **professor meeting is the week after** — no artifact served it | the **professor pack** deliverable at P10.6: a 1-page brief + GAUNTLET/PARETO/SUBSTRATE + the two-halves verdict + the two honesty lines (§5) |
| K12 | "ER at the same convention" (worst-pre-sleep) was under-pinned — an asymmetric read could be invented | a fixed, learner-independent eval-checkpoint grid (k pinned at P10.0); OURS's sleep-interval boundaries applied to every learner (§4) |
| K13 | the research's "Split-X class-IL complement" looked missing from the ladder | stated: the synthetic home IS the class-IL leg; the gauntlet stays purely domain-IL (§2.2-A) |

**Checked and kept as-is (defended):** grid-4 no-swap (the author's Q&A endorses the frontier framing — "do it like a
frontier"); ER-strong as the accuracy bar; the same-substrate energy cut (R1) with analog as the floor overlay; the blind-
pinned verdict shapes; δ_acc = 0.02; the A-GEM/DER++ descope path (now time-boxed to P10.0). And stated for the record: the
home's ~0.49 AA means the accuracy-loss branch is **live** — the showcase does not depend on winning it; the honest-Pareto
branch is a presentable story (flat retention + the energy ratio), and a dominated result is reported as the founding bet
failing, per §0.3.

---

## 10 · The post-close extension (2026-07-03 evening — author-directed; pre-registered BEFORE the runs)

Phase 10 closed at P10.6 the morning of 2026-07-03. The author's same-day read of the report asked for four enrichments.
**All four live on the declared cadence cost axis or are measurement-only — no learned knob moves, the frozen object is
untouched, and the banked P10.1/P10.3/P10.6 verdicts are not re-opened** (determinism means every carried number must
reproduce bit-exactly; the extension adds points and views, never re-judges). Reads pinned here before any run:

- **E1 — grid-5 joins the P10.1 fight roster.** The author's ask: show the cheaper Tier-1 option beside the committed
  headline ("grid-4 still our best model — just add more cheap option to compare"). grid-5 is *already* the P10.2 showcase
  rep (worst-BWT −0.039 within δ of grid-4, cheaper); drawing it in the FIGHT/PARETO is a presentation enrichment of the
  declared cost axis, **never a re-designation** — the P10.1 verdict remains grid-4's, and the §0.1 no-swap clause stands.
  **Read:** where grid-5 sits on (accuracy × energy) between grid-4 and the field — no verdict change possible.
- **E2 — grid-12 fills the Tier-2 gap.** The family {4,5,6,8,16} → **{4,5,6,8,12,16}**; the author read the final-AA-vs-
  energy trend as super-linear and asked for the missing point between grid-8 and grid-16. grid-12 has never run (not even
  in P9.5) — it is a **new Tier-2 measurement on the home stream only** (the gauntlet keeps its committed five grids).
  **Read (expectation-free, both Tier-2 axes):** does grid-12 fail the oracle-veto (grid-8's failure axis: sparse-sleep
  troughs), fail AA-held (grid-16's axis: under-consolidation), both, or hold? Each outcome refines the break's shape;
  whichever the numbers say is banked. Tier-2 becomes {8,12,16}.
- **E3 — the GAUNTLET-STREAM view (the training-curve read) + the GAUNTLET label fix.** A new per-batch figure on the
  P10.3 gauntlet: **live-batch accuracy** (the prequential read — the head's accuracy on each arriving batch, before it
  updates) and **seen-so-far accuracy** (mean held-out accuracy over the domains passed so far — "how much it remembers of
  what it passed") for OURS(grid-4) vs ER-strong, plus a **per-batch prefix-priced cumulative energy** track (the meter is
  closed-form in counts, so the cumulative curve is exact, sleeps clustering where they fire — this *supersedes* the
  per-domain proportional-shape note in the P10.3 manifest). **Measurement-only, triple-guarded:** the OURS curve comes
  from a lockstep replay of the frozen loop whose cell pass is asserted bit-exact against the committed cache
  (rng-fingerprint + per-step `phi_b`), whose head states are asserted against the committed `err_trace` at every step,
  and whose cumulative-energy final point must equal the committed `meter_from_trace` total. Any assert fails → STOP.
  **Read:** the in-domain vs domain-switch mechanism made visible — onset dips, gate fires, sleep recoveries — a
  visualization of the committed result, not a new verdict. (+ the GAUNTLET twin-panel y-labels shortened so they no
  longer collide.)
- **E4 — the full OURS family on the verdict Pareto.** P10.6's Pareto gains the model's own cost-frontier line — **all six
  grids {4,5,6,8,12,16}** beside the field (the author's "money line"), grid-4 ringed, frontier recomputed over
  family + field; asserted: exp1's `ours_g4` == exp2's `g4` bit-for-bit (same cache, same loop). **Read:** the family's
  sweep across the (accuracy × energy) plane vs the field — the P10.6 verdict sentence gains the family, loses nothing.

**Discipline carried:** snapshot-then-diff on every re-run rung (all carried arrays bit-exact or STOP); guards first; the
verdict shapes above pinned blind; failures are data. *(This section is the extension's pre-run record, in the P8.7
extension pattern.)*

### §10 round 2 (2026-07-03 morning — the author's read of the rendered E1–E4; pre-registered BEFORE the runs)

- **E1 WITHDRAWN — ours_g5 leaves the P10.1 fight roster.** The author's pre-render expectation was a *notable* gap;
  the rendered FIGHT showed grid-5 δ-equal to grid-4 on every read — so the extra bar adds confusion, not information.
  Removed for clarity; **the grid-5 numbers stay banked in P10.2 and on the P10.6 family line** (nothing is lost, the
  roster returns to the committed seven + ceiling). The withdrawal is recorded here, not silently reverted.
- **E5 — cliff probes {7, 13, 14, 15} localize the two cliffs.** E2 found the break is two cliffs: safety falls
  somewhere in 6→8, final AA somewhere in 12→16. The probes bracket both: **grid-7** (the safety cliff's interior) and
  **grid-13/14/15** (the accuracy cliff's interior). They are **characterization probes, not family members** — the
  declared family stays `{4,5,6,8,12,16}` (grid-4 headline, grid-5 rep, `CAD_FAMILY` and its guard untouched); the
  probes ride only the P10.2 sweep + the P10.6 scatter. **Read (expectation-free, per probe):** its worst-BWT (which
  side of the safety cliff) and its final AA vs grid-4 − δ (which side of the accuracy cliff) — the two cliff edges
  land wherever the numbers say. Free mechanism read: map both cliffs onto **nsleep** (sleeps-per-stream coverage).
- **E6 — the REVERSED GAUNTLET-STREAM.** The same per-batch view (E3's guarded replay) on the **reversed** domain
  order {noised, covariate, rotated, permuted, identity}, OURS(grid-4) vs ER-strong. Two author questions, pinned:
  (a) **is ER's low start real** — does ER always start near-chance and climb, even when the first world is the hard
  noised one (prediction-free: the curve answers); (b) **is the late-stream drop noise-specific or position-specific**
  — in the forward run both learners' seen-so-far dropped when *noised* arrived last; with noised FIRST, does the drop
  follow the noise (it re-appears early / at noised-eval inclusion) or the position (it re-appears late on whatever
  domain is last)? This also **completes K9's letter**: the committed reversed-order control ran OURS only; ER-strong
  now runs the reversed stream too (its reversed final AA is reported beside OURS's committed order-delta).
- **E7 — the all-grid P10.6 Pareto.** The verdict scatter draws **every** measured cadence point — the family
  {4,5,6,8,12,16} + the E5 probes {7,13,14,15} — so the accuracy cliff is visible on the money line itself and a
  reader can see *which grid to test next*. grid-4 stays the ringed committed hero; frontier recomputed over all
  points + the field; membership is whatever the numbers say.

Same discipline: snapshot-then-diff (bit-exact carries or STOP); the replay guards on every stream view; nothing
learned moves.

---

## Grounding (what the field does — and what we adopt)

- **The fair fight = a BUDGETED baseline** (FLOPs/sample + memory-bytes) where **ER is strong** (Prabhu, *Computationally
  Budgeted CL*, CVPR'23 [2303.11165]; Ghunaim, *Real-Time Evaluation*, CVPR'23 [2302.01047]; Budgeted-OCL ICLR'25 [2410.15143])
  → P10.0/P10.1 + the `fair_budget_guard`.
- **The baseline family** — ER (Rolnick [1811.11682]) · A-GEM (Chaudhry et al., *Efficient Lifelong Learning with A-GEM*, ICLR
  2019 [1812.00420]) · DER++ (Buzzega, NeurIPS'20 [2004.07211]) · **GDumb** (Prabhu, Torr & Dokania, ECCV 2020 — the
  progress-questioning control) · naive-BP (the floor); **REMIND** [1910.02509] the anti-pattern our split is defined against.
- **The metrics** — ACC/BWT/FWT (GEM, Lopez-Paz & Ranzato [1706.08840]); Forgetting (Chaudhry RWalk [1801.10112]); **AAA /
  anytime** (origin OSAKA, Caccia [2003.05856]; convention [2308.10328]); "more than forgetting" [1810.13166] → §4.
- **The gauntlet scenario** — task/domain/class-IL (van de Ven, *Three types of incremental learning* [1904.07734]); ours is
  **domain-IL** (native Permuted/Rotated-digits primary; shared head, shifting-semantics noted) + a Split-X **class-IL**
  complement → P10.3 + `make_gauntlet_stream`.
- **The energy meter + the substrate 2×2** — carried from P8 (behavioral, ADC-centred; Horowitz ISSCC'14 · NeuroSim · ISAAC
  ISCA'16 · PUMA ASPLOS'19 · AIHWKit); the **algorithm win is same-substrate**, the analog factor a meter-structural floor → the
  cost figures + the P8.7 re-meter across the gauntlet.
- **The Pareto presentation** — accuracy-vs-energy bi-objective; efficiency = normalized distance to the ideal corner → the
  verdict figure. Full delta: [`../../research/papers/phase10/README.md`](../../research/papers/phase10/README.md).
- IQR / n=5 honesty / reproducibility / the spine / phantom-hang + CPU-float64 discipline — carried from Phases 1–9
  ([`../result-format.md`](../result-format.md), [`../phase8/result-format.md`](../phase8/result-format.md), [`../phase9/result-format.md`](../phase9/result-format.md)).

> The **floor**, per [`../result-format.md`](../result-format.md) + [`result-format.md`](result-format.md): median + IQR, 5
> seeds, reference lines (chance, ceiling, the budgeted ER-strong racer), a caption ending in the takeaway, a manifest that
> regenerates every figure. The object is frozen; we measure it honestly and report the frontier — **win, tie, or loss.**

*Up:* [Stage-2 map](../stage2-design.md) · *prev:* [Phase 9 — close & freeze](../phase9/README.md) · *next:* the Stage-2
close-out → the analog-realism layer (SPICE / PVT), and beyond the numbered phases, the north star.
