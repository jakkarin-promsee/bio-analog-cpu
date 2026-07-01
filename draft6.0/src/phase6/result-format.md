# Phase 6 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** Handed only a purpose, an agent's output rots four ways — **(1)** graph
> formats drift; **(2)** table styles drift; **(3)** summaries drift; **(4)** no continuity rung-to-rung. This file
> removes the freedom that causes all four. It is **not advisory** — it is the *spec the run code and the write-up must
> conform to*, the way `design.md` is the spec the experiments conform to. **If a rung's output can't be produced by the
> rules below, the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) and **adds the operational
> machinery** for Phase 6: the locked visual constants, the `plot_p6.py` API, the array schema, the table schemas, the
> 6+2 summary template, a worked card, and a pre-submit checklist. Read it once; then *obey it*, don't re-derive it.

---

## §0 — The three enforcement mechanisms (how consistency is made mechanical)

1. **One plotting module — `plot_p6.py` — ONE function per figure code.** Every rung calls the *same* function (§C); the
   look lives in one place (§A `STYLE`). No rung styles `matplotlib` inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice, with the worked card (§F) as the model.**
3. **One ledger schema + one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D); `plot_p6.py
   regen <run-dir>` redraws *every* figure from `arrays.npz`, never from a live run. A figure you can't regenerate from
   saved data is a screenshot, not a result.

> **The rule of additions.** A rung that genuinely needs a new figure/metric **adds it to this file first** (so the next
> rung inherits it) — never a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (single source of truth; `plot_p6.py:STYLE`)

| constant | value | note |
| --- | --- | --- |
| **dpi** | **300** | PNG default (survives the pandoc→docx A4 path) |
| **figsize** | **single = (6.0, 4.0) in · wide/curve = (7.5, 4.0) · panel-strip = (10, 2.2)** | one of three sizes — never ad-hoc |
| **font** | **DejaVu Sans**, base **10 pt** (title 11 bold · axis 10 · tick 9 · caption 9) | identical every plot |
| **background** | **transparent** | docx/slide reuse |
| **IQR band** | **median line (1.8 lw) + shaded fill at alpha 0.18**, same colour as the line | every headline curve, no exceptions |
| **grid** | light grey `#d9d9d9`, 0.6 lw, behind data | on for line/curve plots, off for bars |

**Method / variant encoding (colour · style — fixed forever; extends P5):**

| method | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **OURS-hardened** (noise-augmented cell) | `#d9690a` (orange) | solid, **bold 2.2 lw** | the fix under test |
| **OURS fix-free** (the committed Phase-5 cell, no noise training) | `#d9690a` (orange) | **dashed** | the baseline the fix must beat under noise |
| **directional-aug variant** | `#d9690a` (orange) | solid + **circle markers** | the spine-targeted augmentation (P6.1) |
| **flatness variant** (S-SGD / zeroth-order) | `#d9690a` (orange) | solid + **square markers** | the weight-channel lever (P6.2) |
| **random-axis-aug** (generic-reg isolator) | `#d9690a` (orange) | solid + **triangle markers** | the P6.1 spine control — directional-aug must beat it |
| **RINCE variant** (robust-InfoNCE loss) | `#d9690a` (orange) | solid + **diamond markers** | the loss-level robustness variant (P6.1) |
| **linear-readout control** (raw input) | `#7f7f7f` (grey) | solid | the relative-fragility reference — **OURS-vs-linear** is the decisive A7 read |
| **noiseless ceiling** (the cell at σ=0) | `#2ca02c` (green) | **dashed** | best case, no noise — the upper bound |
| **SAM-reference** (backprop, never deployed) | `#2ca02c` (green) | **dotted** | the flatness upper bound the forward-only zeroth-order pass is scored against |
| **chance** / **Bayes-optimal** | `#111111` dotted thin / `#2ca02c` dotted thin | — | the floor / the *true* ceiling |
| **noise channels** (A7-CURVE only) | tap `#d9690a` · input `#2c6fbf` · ADC `#8a1b8a` · weight `#111111` | solid (i.i.d.) / **dashed (directional)** | per-channel sensitivity; **dashed = the directional enemy** |

OURS-family = orange always (variants differ by **line/marker**, never colour). On A7-CURVE the four channels get the
fixed channel-colours and **directional is always the dashed pair of its channel** (so the eye reads "dashed = the enemy
that matters"). The only non-OURS references are the noiseless ceiling (green-dash) and SAM-ref (green-dot).

**Required `plot_p6.py` API (one function per figure; signatures fixed):**

```
STYLE                       # the dict of constants above; the ONLY place styling lives
fig_a7_curve(run)           # F: A7-CURVE     (THE headline)
fig_dir_invariance(run)     # F: DIR-INVARIANCE
fig_aug_sweep(run)          # F: AUG-SWEEP
fig_flatness(run)           # F: FLATNESS
fig_door_b(run)             # F: DOOR-B
fig_bulk_drift(run)         # F: BULK-DRIFT
fig_cont_safety(run)        # F: CONT-SAFETY
fig_nat_anchor(run)         # F: NAT-ANCHOR
fig_inv(run)                # F: INV (every run)
regen(run_dir)              # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

The **P6.8 synthesis re-uses these functions** on the assembled-cell run (A7-CURVE + DIR-INVARIANCE + CONT-SAFETY +
NAT-ANCHOR) — it adds **no new plotter**. Every `fig_*` reads `arrays.npz` + `manifest.json`, draws in `STYLE`, writes a
300-dpi PNG. **No rung draws outside these functions**, and **every rung writes `arrays.npz` to the schema below.**

**The `arrays.npz` schema (pinned — key · shape · meaning; a rung emits the subset its figures need):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | seed list (S=5; 9 for ≤0.02-gap rungs; 3 for heavy continual) |
| `rms` | `[R]` | the swept injected-RMS grid (x-axis of A7-CURVE) |
| `a7acc_<method>_<channel>_<variant>` | `[S, R]` | readout-acc vs RMS. **method ∈ {fixfree, hardened, ceiling, flat, linbase}** · channel ∈ tap/input/adc/weight · variant ∈ iid/dir/randax — the **method** axis is what lets A7-CURVE draw fix-vs-fixfree-vs-ceiling-vs-linear |
| `a7dir_<method>_<channel>_<variant>` | `[S, R]` | class-**direction** delta vs RMS (the spine version; same axes) |
| `dirinv_<method>_<channel>` | `[S, L]` | `cos(clean-rep, noisy-rep)` per depth, per channel (method ∈ fixfree/hardened) |
| `sigaug` | `[G]` | the augmentation-strength grid (P6.1) |
| `robust_vs_aug_<variant>` | `[S, G]` | direction-invariance vs `σ_aug`, **per variant** (iid/dir/randax) — the spine-test overlay |
| `select_vs_aug_<variant>` | `[S, G]` | selectivity vs `σ_aug` (collapse + **capacity-knee** guard), per variant |
| `flatness_<method>` | `[S]` | sharpness (loss under unit Rademacher perturbation); methods incl. `sam_ref` |
| `doorb_<corruption>_<purity>` | `[S]` | direction-formed metric (corruption ∈ zeromean/dir; purity ∈ on/off) |
| `purity_<method>` | `[S]` | fraction of LUT clean (filtered vs naive) |
| `drift_<method>` | `[S, T]` | bulk-drift `cos(rep_t, rep_{t+Δ})` over the stream |
| `cont_<metric>_<change>` | `[S]` | continual `bwt`/`aa`/`ret` (P6.6). **change ∈ {fixfree, aug, aug+flat, aug+norm, rince, assembled}** — the pinned per-change label set (so the gate is one-variable-per-change) |
| `selectivity_<method>` | `[S, L]` | per-layer selectivity (anti-collapse) |
| `inv_<panel>` | `[S, …]` | INV panels (`lossslope`/`deadfrac`/`erank`/`automzero`/`rmsmatch`/`fdguard`) |

> **Source-of-truth note:** canonical [`../result-format.md`](../result-format.md) Layer A **owns** any shared constant
> (dpi, IQR band, the n=5 rule); the restatement above is the **binding restatement for the Phase-6 executor**; if they
> diverge, **canonical wins.** Phase-6-*new* and *owned* here: the channel encoding (dashed = directional), the
> noiseless-ceiling + SAM-reference pair, the matched-RMS rule, and the array schema.

---

## §B — The metric dictionary (PINNED; Phase-6 additions in **bold**)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| **A7 sensitivity curve** | Δ(readout acc) **and** Δ(class-direction) vs injected RMS, **per channel** (tap/input/ADC/weight), **i.i.d. vs directional** | acc-or-cos vs RMS |
| **direction-invariance** | `cos(clean-rep, noisy-rep)` of the *same* sample, per depth (the spine metric) | cosine ∈ [−1,1] |
| selectivity / clean acc | per-layer class selectivity + noiseless readout acc (the **anti-collapse** guard) | acc, median [IQR] |
| **flatness** | loss/objective change under a unit Rademacher weight perturbation; ZOSA vs SAM-reference | Δloss (lower = flatter) |
| **noise-model fidelity** | the AIHWKit-structured components present + auto-zero subtracts common-mode + RMS-matched | pass/fail checklist |
| **bulk-drift rate** | `cos(rep_t, rep_{t+Δ})` of fixed inputs across the continual stream | cosine vs stream-step |
| **buffer purity** | fraction of LUT entries clean, PurityFilter vs naive | fraction |
| **continual BWT / AA / retention** | GEM/CL-survey conventions; hardened cell vs **the fix-free committed cell (itself vs the P4.5 baseline)**; + paired-sign veto at the gate | acc / acc-delta |
| backward cost (substrate) | carry P4/P5 — labelled substrate work, **NEVER "energy"/"N× faster"** | analytic count |

**The class-direction is the headline robustness read, not accuracy** (the spine): a fix that holds accuracy by a
magnitude trick but rotates the direction is **not** robust. Report **both** the acc curve and the direction curve; when
they disagree, trust the direction and report the gap.

**Calling a difference real (n=5, carry — load-bearing):** real only if **IQR bands disjoint at the final checkpoint**
*and* **sign consistent in ≥4/5 seeds, paired by seed**; else **"within noise."** **Matched-RMS rule (Phase-6, binding):**
every i.i.d.-vs-directional and fix-vs-baseline noise comparison is at **equal injected RMS energy** — an unmatched
comparison is a dose artifact, reported as such, never as a robustness result.

---

## §C — The figure catalog (declare which you emit; never invent)

Each figure = one `plot_p6.fig_*` function (§A). **Every A7/robustness figure draws BOTH the noiseless ceiling and the
fix-free baseline** — robustness is only interpretable between "no noise" and "no fix."

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **A7-CURVE** *(THE headline)* | `fig_a7_curve` | acc **and** direction vs injected RMS, per channel, **i.i.d. solid / directional dashed**, + noiseless ceiling + fix-free baseline, IQR bands | how bad, which channel, is the enemy directional, does the fix flatten it |
| **DIR-INVARIANCE** *(the spine)* | `fig_dir_invariance` | `cos(clean,noisy)` vs depth, fix vs fix-free | is the **class direction** preserved under noise (not just accuracy) |
| **AUG-SWEEP** | `fig_aug_sweep` | robustness (A7-slope) **and** selectivity vs `σ_aug`, **collapse region shaded** | the augmentation sweet-spot; where it collapses the rep |
| **FLATNESS** | `fig_flatness` | sharpness bars, S-SGD / ZOSA vs SAM-reference + fix-free | is flatness buyable forward-only; the ZOSA-vs-SAM gap |
| **DOOR-B** | `fig_door_b` | direction-formed bars: corruption (zero-mean / directional) × purity (on / off) vs the clean-data cell | can the rep form from an all-noisy stream; does purity beat averaging |
| **BULK-DRIFT** | `fig_bulk_drift` | `cos(rep_t, rep_{t+Δ})` vs stream-step, fix vs fix-free | the self-inflicted, noise-like drift (the Stage-2 assumption) |
| **CONT-SAFETY** *(the gate)* | `fig_cont_safety` | BWT / AA / retention bars, each **change** vs the **fix-free committed cell** (+ paired-sign veto) | does the fix keep the A6 continual win |
| **NAT-ANCHOR** | `fig_nat_anchor` | A7-CURVE / DIR-INVARIANCE headline with **digits + CIFAR-flat** overlaid | does the synthetic noise story survive real flat data |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples: loss-slope · dead-unit % (≈0) · effective-rank · **auto-zero-subtracts-common-mode** · **RMS-match** · FD-guard pass | health + apparatus sanity at a glance |

**Caption rule (every figure, no exceptions):** one sentence, ending with **the takeaway** (not a description), then
`(n=5, task, channel, PROBE_EP=120)`. An A7 caption **never** states a robustness number without naming the **noiseless
ceiling**, the **fix-free baseline**, the **linear-readout control** (the OURS-vs-linear relative read), and **whether
the noise was directional at matched *projected* RMS.** Model caption:

> *"[Fix] flattened the directional tap-channel A7 slope from 0.AA→0.BB (Δdir cos 0.CC→0.DD), closing X% of the gap to
> the noiseless ceiling (0.EE) over the fix-free baseline (0.FF), at matched RMS, with clean selectivity held. (n=5,
> headroom, tap-directional, PROBE_EP=120.)"*
>
> *(Letters are deliberate placeholders — the caption teaches the **shape**, never an expected result. Do **not** anchor
> on any number; the §0.3 hypotheses are not findings — pre-seeding the expected win is the "tune-until-it-works" trap
> the project bans.)*

---

## §D — Table schemas (fixed columns; one IQR format; no bare means)

**IQR format fixed everywhere: `median [q25–q75]`** (two decimals). Never a bare mean.

**The RESULTS.md ledger — one section per rung, this row schema (no prose in the ledger):**

```
| <swept variable> | <metric₁> | <metric₂> | … | gap-to-ref | verdict |
```
Header line states the locked controls (`task, L, channel, RMS-grid, seeds, PROBE_EP`). Last column = a ≤6-word verdict
(`flattens curve`, `within noise`, `STRUCK — collapse`, `ABORT — depth regressed`, …). One variable swept per table; the
swept variable is the **first** column. **Per-rung column tuples are fixed:**

| rung | columns (after the swept variable) |
| --- | --- |
| P6.0 | `channel · Δdir@σ* · OURS-vs-linear · iid-vs-dir(projected) · dominant? · verdict` |
| P6.1 | `dir-invariance@σ* · clean-acc · selectivity · vs-random-axis · verdict` *(σ_aug swept; iid/dir/randax/rince as separate curves)* |
| P6.2 | `flatness · weight-A7 · tap-A7(transfer) · vs-SAM-ref · verdict` |
| P6.3 | `A7-dir · tail-L12 · BWT · readout-vs-BP · A2-nuisance · abort? · verdict` |
| P6.4 | `corruption(zm/dir) · direction-formed(ratio-to-clean) · purity-benefit · verdict` |
| P6.5 | `drift-rate · vs-fix-free · verdict` |
| P6.6 | `change · AA · BWT(+paired-sign) · retention · vs-fixfree-cell · verdict` |
| P6.7 | `dataset · A7-present? · fix-holds? · verdict` |

**Ablation / comparison tables (in cards):** one variable per row, **delta vs baseline in its own column**, IQR in
**every** cell; baseline row first, labelled `(baseline)`. **Struck-negative tables:** identical schema, with the failed
condition and the **mechanistic reason** in the verdict column — a struck mechanism gets the *same* rigor as a win
(failures are data: a collapsed augmentation, a depth-regressing norm, an i.i.d.-only "win").

---

## §E — The summary writing contract (the 6 + 2 slots — fill verbatim, formal voice)

Every `expK/experiment-K.md` *Read* section fills the **6 + 2** slots **in this order, none empty** (if one is "n/a", say
*why*). **Formal research voice** (rules below; the worked card §F):

1. **Claim** — one *falsifiable* sentence. ("A directional noise-augmented contrast flattens the tap-channel A7 slope without losing selectivity.")
2. **Headline number** — median **[IQR]** across seeds, **against its references** (the **noiseless ceiling** *and* the **fix-free baseline**, at **matched RMS**). *Never a bare number.*
3. **Figures** — the catalog refs emitted, each with a one-line read; name the headline figure explicitly.
4. **Mechanism** — *why* the number is what it is (the spine: is the gain a preserved class **direction** (cos held) or an accuracy **magnitude** trick? which **channel**?). This is what makes it research.
5. **Threats to validity** — what *else* could explain it (an **unmatched RMS** dose, a **collapse** masquerading as robustness, a **synthetic-noise artifact**, a swung seed); the methodology rule-1 check, written in.
6. **Decision** — which open knob this **sets** (`σ_aug` / flatness lever / norm / purity-filter), and what the next rung inherits.
7. **Robustness-honesty** *(re-pointed from cost-honesty)* — the enemy was **structured & directional at matched RMS**, not a weak i.i.d. stand-in; the gain is **direction-invariance**, not just accuracy; the **collapse / selectivity guard** passed; the **auto-zero** subtracted the common-mode (so the residual is what was tested).
8. **SCFF-trust / arc-verdict** — what this rung says about **"is the cheap brain robust enough to trust?"**, the **continual-safety (P6.6) verdict** for any change it proposes to bank, and which **YES/NO branch** (fixable-in-SCFF vs arc-reopen) it currently leans. A rung that moves neither the robustness story nor the verdict shouldn't have run.

**Voice rules:** declarative past-tense for what happened ("directional-aug at σ=X flattened the tap slope to 0.BB");
present-tense for standing reads ("a noisy positive view trains the class direction to be perturbation-invariant"); **no
hedging filler**, **no first-person**, **no exclamation**; every adjective backed by a number or dropped; a struck result
stated plainly ("σ_aug>X collapsed selectivity to chance — robustness was rep-collapse, not invariance"). **Continuity:**
each card **opens by naming the knob it inherits** ("Inheriting the dominant channel + the fix-free A7 baseline from
P6.0, …"). A **skipped conditional rung** (P6.2/P6.3 if no gap survives) is a **one-line skip-card** naming the gap-test
that closed it.

---

## §F — Gold-standard worked card (copy this skeleton; this is the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches
> the **shape, voice, and completeness**, never an answer. Do not anchor on them (the §0.3 hypotheses are not findings).*

```markdown
# P6.1 — Noise-as-augmentation: a noisy contrastive view as the primary fix

**Question.** Does corrupting one InfoNCE view with the directional noise model make the class direction
noise-invariant — without collapsing the representation — and is the gain spine-clean (an angle, not a magnitude)?

**Setup.** Swept variable = augmentation strength σ_aug ∈ {grid}; controls locked (temp=0.2, window=2, headroom + flat +
mixed, L12, seeds [42,137,271,314,1729], PROBE_EP=120, RMS-matched) + the two augmentation variants (i.i.d. vs
directional, a separate one-variable check). A7-CURVE + selectivity + direction-invariance. Apparatus:
p6lib.NoiseAugContrast; guards passed (P6.0: σ_aug=0 ≡ plain; auto-zero subtracts common-mode; FD < 1e-5).

**Run.** N cells × 5 seeds, checkpointed (_ckpt.jsonl); 1 cell resumed after a laptop-sleep. Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| σ_aug | A7-slope (tap-dir) | clean-acc | selectivity | dir-invariance | vs fix-free | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 0.00 (fix-free) | 0.AA [..–..] | 0.aa [..–..] | 0.ss [..–..] | 0.dd [..–..] | — | the baseline |
| σ* (candidate) | 0.BB [..–..] | 0.bb [..–..] | 0.s2 [..–..] | 0.d2 [..–..] | <real-better?> | <flattens, selectivity held?> |
| σ_hi | 0.CC [wide] | 0.cc [low] | chance | 1.00 | <collapse?> | <STRUCK — rep collapse?> |
- **A7-CURVE** (headline): <does the slope flatten vs fix-free, toward the noiseless ceiling, at matched RMS?>.
  - **AUG-SWEEP**: <where is the collapse cliff — selectivity vs σ_aug>. - **DIR-INVARIANCE**: <cos held across depth?>.
  - **INV**: dead-frac ≈ 0, auto-zero ✓, RMS-match ✓, FD ✓.

**Read (8 slots).**
1. *Claim* — a directional noise-augmented contrast flattens the tap-channel A7 slope while holding selectivity.
2. *Headline* — σ*: tap-directional A7-slope 0.BB [IQR] vs the noiseless ceiling 0.EE and the fix-free baseline 0.AA, at matched RMS (n=5, headroom).
3. *Figures* — A7-CURVE (slope flatten), AUG-SWEEP (collapse cliff), DIR-INVARIANCE (cos held), INV (clean).
4. *Mechanism* — if dir-invariance rose with selectivity held: the noisy positive view trains the class *direction* to be perturbation-invariant (the spine). If acc held but cos didn't: a magnitude trick — say so.
5. *Threats* — (a) unmatched RMS (controlled); (b) collapse masquerading as robustness (selectivity guard); (c) directional-vs-i.i.d. must be at matched RMS; (d) "real" only if IQR-disjoint + ≥4/5 sign.
6. *Decision* — sets the adopted σ_aug + variant (pending P6.6); next rung inherits the hardened cell.
7. *Robustness-honesty* — the enemy was tap-directional at matched RMS (not i.i.d.); the gain is direction-invariance; the collapse guard passed; auto-zero subtracted the common-mode.
8. *SCFF-trust / arc-verdict* — moves the robustness verdict toward YES iff the slope enters the tolerable band; **continual-safety NOT yet checked → P6.6 gates adoption**; STOPPING MARK ① if it clears alone.
```

This is the bar: every slot filled, IQR in every cell, both refs named, matched-RMS stated, the spine invoked, the
continual gate flagged. A card that looks like this *cannot* be the messy output the contract exists to prevent.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

Paste into the card and tick. A rung is **not** done until every box is true.

- [ ] **Median [IQR]** for every headline number (n=5; 3 only for the heaviest continual cells) — **no bare means**.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 by sign) before any gap is *claimed*; else "within noise."
- [ ] **Matched *projected* RMS** (on the class axis) stated for every i.i.d.-vs-directional comparison; the decisive read is **OURS-vs-`linear_readout`**, not directional-vs-i.i.d.
- [ ] Every A7/robustness figure draws **all** refs: the **noiseless ceiling**, the **fix-free baseline**, and the **linear-readout control**; directional drawn **dashed**.
- [ ] **Fix-free A7/dir arrays LOADED from the pinned P6.0 run-dir**, not recomputed (no-baseline-drift); the co-trained σ_aug=0 arm reproduces them within §B.
- [ ] **"Tolerable band" = the pre-registered retention threshold at σ\*** (cos ≥ Y direction-first, acc-ret ≥ X), picked blind — NOT the §B difference test.
- [ ] **P6.1 random-axis-aug control** run; the spine claim asserted only if directional-aug beats random-axis-aug on the directional curve.
- [ ] **P6.1 capacity-knee probe** run; committed σ_aug is below the knee, not merely below collapse.
- [ ] **P6.3** (if run) checks the full panel {tail-L12, BWT, readout-vs-BP, **A2 nuisance**}; abort-if-any-regressed.
- [ ] **P6.6 the GATE runs 5 seeds** (never 3); "within noise" is NOT an auto-pass — the **paired-sign veto** (negative in ≥4/5 paired seeds = fail) applied.
- [ ] **Auto-zero two-arm** (with/without) reported; the common-mode channel is measured, not assumed away.
- [ ] **Direction** reported alongside accuracy (the spine); when they disagree, the direction is trusted and the gap reported.
- [ ] Every figure drawn by a **`plot_p6.fig_*`** function (no inline styling); caption ends with the **takeaway** + `(n=5, task, channel, PROBE_EP=120)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); **formal voice**; the card **opens by naming the inherited knob**.
- [ ] **`manifest.json`** (git hash, config, seeds, versions, wall-clock) **+ `arrays.npz`** written; **`plot_p6.py regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards** logged: `σ=0 ≡ clean` and `NoiseAug σ0 ≡ plain` equivalence; **auto-zero subtracts the common-mode**; **RMS-match**; FD-gradient < 1e-5 on any new backward path; dead-frac sanity.
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874 guards; the real PID verified alive on multi-hour cells.
- [ ] **Spine check:** robustness measured as **direction-invariance**, not only Δaccuracy; no fix bought by representation collapse (selectivity guard); the enemy is the **directional** residual, not an i.i.d. stand-in.
- [ ] **Continual-safety (P6.6)** verdict recorded for any change proposed to bank; the **P5-invariant panel** (tail-L12, BWT) checked for any P6.3 norm change (abort-if-regressed).
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **struck** result logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P6.0** bench + A7 | A7-CURVE (reproduction, per channel, i.i.d. vs directional, + noiseless ceiling), INV (auto-zero + RMS-match + FD-guard + dead-frac) |
| **P6.1** noise-aug | **A7-CURVE** (fix vs fix-free), **AUG-SWEEP**, **DIR-INVARIANCE**, INV |
| **P6.2** flatness | **FLATNESS** (ZOSA vs SAM-ref), A7-CURVE (weight + tap transfer), INV |
| **P6.3** norm root | A7-CURVE (per norm variant), DEPTH/selectivity P5-invariant panel, INV (abort-if-regressed logged) |
| **P6.4** Door B | **DOOR-B** (corruption × purity), DIR-INVARIANCE on the all-noisy stream, INV |
| **P6.5** bulk-drift | **BULK-DRIFT** (fix vs fix-free over the stream), INV |
| **P6.6** continual-safety | **CONT-SAFETY** (each change vs the fix-free committed cell, 5 seeds + paired-sign veto), INV |
| **P6.7** natural-data | **NAT-ANCHOR** (digits + CIFAR-flat on the headline curves), INV |
| **P6.8** synthesis | the assembled A7-CURVE + DIR-INVARIANCE + CONT-SAFETY + NAT-ANCHOR + the YES/NO verdict + the Stage-2 brief |

## Grounding (what the field does — and what we adopt)

- **Noise-aware training = inject the deployment noise at train time** (Rasch, Nat. Comm. 2023; AIHWKit
  [2104.02184](https://arxiv.org/abs/2104.02184); BayesFT; Variance-Aware [2503.16183](https://arxiv.org/abs/2503.16183))
  → the `NoiseModel` + injection levers, **honest & structured**, not i.i.d.
- **Robustness via a perturbed contrastive view** (consistency/robust contrastive
  [2509.20048](https://arxiv.org/abs/2509.20048); Ditch-the-Denoiser [2505.12191](https://arxiv.org/abs/2505.12191)) →
  **noise-as-augmentation** (P6.1); the forward-only surrogate for Jacobian/Lipschitz smoothing (Bishop 1995).
- **Input-noise = Tikhonov / Jacobian smoothing** (Bishop 1995; Jacobian-reg [1908.02729](https://arxiv.org/abs/1908.02729))
  → why injection works forward-only; the explicit penalty stays the *explanation*, not the method.
- **Flat minima = generalization = perturbation-robustness** (SAM [2010.01412](https://arxiv.org/abs/2010.01412); S-SGD
  [2009.02479](https://arxiv.org/abs/2009.02479); **ZOSA** [2511.09156](https://arxiv.org/abs/2511.09156)) → **FLATNESS**
  (P6.2), ZOSA forward-only vs SAM-reference.
- **Learn from only-noisy data (zero-mean) + buffer purity** (Noise2Noise [1803.04189](https://arxiv.org/abs/1803.04189);
  Self-Purified Replay [2110.07735](https://arxiv.org/abs/2110.07735)) → **DOOR-B** (P6.4).
- **A frozen head can't create backbone robustness** (LP-FT [2202.10054](https://arxiv.org/abs/2202.10054)) → why this is
  Stage 1, and why readout-side defense is deferred to Stage 2.
- **Continual = AA/BWT/forgetting** (CL survey [2302.00487](https://arxiv.org/abs/2302.00487); GEM
  [1706.08840](https://arxiv.org/abs/1706.08840)) → **CONT-SAFETY**, vs the fix-free committed cell (itself vs P4.5).
- IQR / n=5 honesty / reproducibility / the summary slots — carried from Phase 1–5
  ([`../result-format.md`](../result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to the catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent.
