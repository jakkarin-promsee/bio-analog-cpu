# Phase 5 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** When an agent is handed only a high-level purpose and left to present
> results however it likes, the output rots in four predictable ways — **(1)** graph formats drift (colours, axes,
> dpi change per plot); **(2)** table styles drift (different columns, no IQR, bare means); **(3)** summaries drift
> (each written differently, no formal voice); **(4)** no continuity (rung N reads nothing like rung N−1). This file
> removes the freedom that causes all four. It is **not advisory** — it is the *spec the run code and the write-up
> must conform to*, the same way `design.md` is the spec the experiments conform to. **If a rung's output can't be
> produced by the rules below, the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) and **adds the operational
> machinery** that makes consistency mechanical rather than hoped-for: the locked visual constants, the required
> plot-module API, the exact table schemas, the worded summary template, a **gold-standard worked card** to copy,
> and a **pre-submit checklist** that gates every rung. Read it once; then *obey it*, don't re-derive it.

---

## §0 — The three enforcement mechanisms (how consistency is made mechanical)

Consistency is not left to discipline; it is enforced by three single-sources-of-truth:

1. **One plotting module per phase — `plot_p5.py` — with ONE function per figure code.** Every rung, and every agent
   handed a rung, calls the *same* function (§C). Plots **cannot** drift in look because the look lives in one place
   (§A `STYLE`). No rung defines its own `matplotlib` styling inline — it calls `plot_p5.fig_*`.
2. **One summary template — the 8 slots (§E) — filled verbatim, in the formal voice, with the worked card (§F) as
   the model.** Summaries don't drift because every card has the same skeleton and the same voice.
3. **One ledger schema and one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D);
   `plot_p5.py regen <run-dir>` redraws *every* figure from `arrays.npz` (never from a live training run). A figure
   you can't regenerate from saved data is not a result — it's a screenshot.

> **The rule of additions.** If a rung genuinely needs a figure/metric not catalogued here, **add it to this file
> first** (so the next rung inherits it) — never emit a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (the single source of truth; `plot_p5.py:STYLE`)

These are fixed once, read by every figure function, never overridden per-plot.

| constant | value | note |
| --- | --- | --- |
| **dpi** | **300** | PNG default (survives the pandoc→docx A4 path; SVG/EMF is finicky) |
| **figsize** | **single = (6.0, 4.0) in · wide/pareto = (7.5, 4.0) · panel-strip = (10, 2.2)** | one of three sizes — never ad-hoc |
| **font** | **DejaVu Sans**, base **10 pt** (title 11 bold · axis-label 10 · tick 9 · caption 9) | identical every plot |
| **background** | **transparent** | for docx/slide reuse |
| **IQR band** | **median line (1.8 lw) + shaded fill at alpha 0.18**, same colour as the line | every headline curve, no exceptions |
| **grid** | light grey `#d9d9d9`, 0.6 lw, behind data | on for line/Pareto plots, off for bars |

**Method encoding (colour · style — fixed forever; carries P3/P4):**

| method | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **OURS-adopted** (re-tuned temp/window + per-depth-head readout) | `#d9690a` (orange) | solid, **bold 2.2 lw** | the cheap brain under test |
| **all-tap readout** (the baseline replaced) | `#d9690a` (orange) | **dashed** | reads everything → burns the 80/20 |
| **per-depth heads / early-exit** | `#d9690a` (orange) | solid + **circle markers** at each depth | the readout MVP |
| **frozen-residual variant** | `#d9690a` (orange) | solid + **square markers** | the preservation cell (P5.6) |
| **truncation floor** | `#111111` (near-black) | solid | the cost baseline every tier must beat |
| **w12 ceiling** (diagnostic only) | `#2ca02c` (green) | **dashed** | the depth upper bound — *never deployed* |
| **BP-ceiling** / **Mono-Forward** | `#2c6fbf` (blue) / `#8a1b8a` (purple) | solid | carry P4 — drawn only where a racer comparison is made |
| **chance** / **Bayes-optimal** | `#111111` dotted thin / `#2ca02c` dotted thin | — | the floor / the *true* ceiling |
| **world pos / neg** (SCFF internals) | `#2c6fbf` / `#d62728` | — | carry P1–4 (only in goodness/internal figs) |

OURS-family = orange always (the variants differ by **line/marker**, never colour — they *are* one cell). The
non-OURS references — truncation (black), w12 (green-dash), BP/Mono (blue/purple) — are the only other colours.

**Required `plot_p5.py` API (every figure has exactly one function; signatures fixed):**

```
STYLE                       # the dict of constants above; the ONLY place styling lives
fig_depth_profile(run)      # F: DEPTH-PROFILE
fig_credit_reach(run)       # F: CREDIT-REACH
fig_temp_floor(run)         # F: TEMP-FLOOR
fig_placement(run)          # F: PLACEMENT
fig_exit_pareto(run)        # F: EXIT-PARETO
fig_residual_ablation(run)  # F: RESIDUAL-ABLATION
fig_cont_safety(run)        # F: CONT-SAFETY
fig_nat_anchor(run)         # F: NAT-ANCHOR
fig_inv(run)                # F: INV (every run)
regen(run_dir)              # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

The **P5.9 synthesis re-uses these same functions** on the assembled-cell run (DEPTH-PROFILE + EXIT-PARETO +
CONT-SAFETY + NAT-ANCHOR) — it adds **no new plotter** (consistency over a bespoke summary figure). Every `fig_*`
reads `arrays.npz` + `manifest.json` from `run`, draws in `STYLE`, writes a 300-dpi PNG. **No rung draws outside
these functions**, and **every rung writes `arrays.npz` to the schema below** — that pairing is what makes `regen`
portable across rungs (the one place the contract's "redraw from saved data" promise is otherwise unenforceable).

**The `arrays.npz` schema (pinned — key · shape · meaning; a rung emits the subset its figures need):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | the seed list (S = 5; 9 for ≤0.02-gap rungs; 3 for heavy continual) |
| `probe_<method>` | `[S, L]` | per-layer **linear**-probe acc (method ∈ `ours`/`alltap`/`trunc`/`w12`/`resid`/…) |
| `probe_mlp_<method>` | `[S, L]` | per-layer **MLP**-probe acc (P5.3 lost-vs-rotated) |
| `readout_<method>` | `[S]` | the **real nonlinear** readout acc |
| `temp` / `window` | `[T]` / `[W]` | the swept-axis values (P5.1 / P5.2) |
| `headacc` | `[S, L]` | per-depth-head acc (P5.4 placement) |
| `exit_hist` | `[S, L]` | exit-depth histogram (P5.5) |
| `expcompute_<method>` | `[S]` | forward-MACs expected-compute on the continual stream (P5.5) |
| `oracle_gap` | `[S]` | oracle-exit − gated acc (P5.5) |
| `alpha_ablation` | `[S, B]` | per-block Δ(tail/acc) under α→0 (P5.6) |
| `cont_<metric>_<method>` | `[S]` | continual `bwt`/`aa`/`ret` (P5.7) |
| `inv_<panel>` | `[S, …]` | the INV panels (`lossslope`/`deadfrac`/`erank`/`costsane`/`fdguard`) |

> **Source-of-truth note (so this isn't a second style bible — the repo-fit review's catch):** canonical
> [`../result-format.md`](../result-format.md) Layer A **owns** any constant shared with prior phases (dpi, IQR band,
> the n=5 rule). The constants restated above are the **binding restatement for the Phase-5 executor** (so it needs
> no cross-reference mid-run); **if they ever diverge from canonical, canonical wins and this is re-synced.** Only the
> Phase-5-*new* rules are *owned* here: the OURS-variant marker scheme, the w12-ceiling + truncation-floor ref-pair,
> and the array schema.

---

## §B — The metric dictionary (PINNED; Phase-5 additions in **bold**)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| **composing-depth** | per-layer linear probe: **peak layer** (argmax) · **slope** L1→L12 (OLS) · **tail-L12** | layer / acc / acc-per-layer |
| readout accuracy | the *real nonlinear* readout head (not the probe), held-out | acc, median [IQR] |
| **probe-capacity** | per-depth accuracy under a **linear** vs a **2-layer-MLP** probe | acc pair per depth |
| **placement accuracy** | per-depth-head accuracy vs all-tap; the profiler peak / slope-flatten depth | acc / layer |
| **expected-compute (continual)** | **forward-MACs:** `E_stream[ exit_depth·SCFF_fwd_MACs + Σ_{ℓ≤exit} head_ℓ_MACs + gate_MACs ]`, on the **continual** stream (NOT i.i.d.) — a FORWARD meter (P4's is backward-only) | forward-MACs (one unit) |
| **exit-rate / oracle-exit gap** | exit-depth histogram; best-per-input-layer acc − gated acc | fraction / acc-delta |
| **per-block contribution** | Δ(tail / acc) under per-block **α→0 ablation** | acc-delta per block |
| **continual BWT / AA / retention** | GEM/CL-survey conventions; re-tuned cell vs the **P4.5 baseline** | acc / acc-delta |
| **temp floor** | tail-L12 / readout acc vs temperature; **collapse point marked** | acc vs temp |
| backward cost (substrate) | credit-distance × weights **+** #backward updates; **labelled substrate work, NEVER "energy"/"N× faster"** | analytic count (carry P4) |

**The linear probe is the primary representation metric** (carry P1–4); the **MLP probe is the lost-vs-rotated
diagnostic only** — never the headline classifier (the canonical probe discipline binds: don't make the probe
cleverer to rescue a layer). The **real readout** is the headline where a head is read; the linear-probe peak is a
proxy with a *known gap* — when they disagree, **trust the readout** and report the gap.

**Calling a difference real (n=5, carry — load-bearing):** a difference counts as **real** only if the **IQR bands
are disjoint at the final checkpoint** *and* the **sign is consistent in ≥4/5 seeds, paired by seed**. Everything
else is reported, verbatim, as **"within noise."** Never upgrade a within-noise result to a claim.

---

## §C — The figure catalog (declare which you emit; never invent)

Each figure = one `plot_p5.fig_*` function (§A). **Every depth/accuracy figure draws BOTH the w12 ceiling and the
truncation floor** — composing-depth is only interpretable between "the forbidden best" and "the cheap fallback."

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **DEPTH-PROFILE** *(THE headline)* | `fig_depth_profile` | per-layer probe vs depth, methods overlaid, **+ w12 + truncation refs**, IQR bands | does the lever stop the decay / march the peak deeper? |
| **CREDIT-REACH** | `fig_credit_reach` | tail-L12 & peak-depth vs window (w1…w12) + temp×w points | composing depth per unit credit reach |
| **TEMP-FLOOR** | `fig_temp_floor` | tail-L12 & readout acc vs temperature, **collapse region shaded** | the safe sharpness; is temp the free lever |
| **PLACEMENT** | `fig_placement` | per-depth-head acc vs depth + profiler peak + all-tap line | where to read; do heads match all-tap |
| **EXIT-PARETO** *(cost headline — STOPPING MARK ①)* | `fig_exit_pareto` | accuracy vs **expected-compute on the CONTINUAL stream**, OURS-exit vs **all-tap** vs **truncation** + **oracle** | does placement+exit beat all-tap *and* truncation where we live |
| **RESIDUAL-ABLATION** | `fig_residual_ablation` | per-block α→0 contribution bars (Δ tail/acc) | dead-gate guard — real contribution vs bypass |
| **CONT-SAFETY** *(the gate)* | `fig_cont_safety` | BWT / AA / retention bars, each adopted change vs the **P4.5 baseline** | does the fix keep the A6 continual win |
| **NAT-ANCHOR** | `fig_nat_anchor` | DEPTH-PROFILE / EXIT-PARETO headline with **digits + CIFAR-flat** points overlaid | does the synthetic story survive real flat data |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples (this is the Phase-5 INV, **overriding** the inherited strip): loss-slope · dead-unit % (≈0) · effective-rank · cost-meter sanity · FD-guard pass — arrays `inv_lossslope/deadfrac/erank/costsane/fdguard` | health + apparatus sanity at a glance |

**Caption rule (every figure, no exceptions):** one sentence, ending with **the takeaway** (not a description), then
`(n=5, task, PROBE_EP=120)`. A depth caption **never** states a tail without naming the **w12 ceiling** and the
**truncation floor**. Model caption:

> *"[Lever] marched the peak Lᵢ→Lⱼ and lifted tail-L12 0.AA→0.BB — within the §B real-difference band of the w12
> ceiling (0.CC) at ~1/N× the backward cost, and clear of the truncation floor (0.DD). (n=5, headroom, PROBE_EP=120.)"*
>
> *(Letters/Lᵢ are deliberate placeholders — the caption teaches the **shape** of the sentence, never an expected
> result. Do **not** anchor on any number here; the rough T0/T3 figures are §0.3 hypotheses, and pre-seeding the
> expected win would make a failure-reading harder to file — exactly the "tune until it works" trap the project bans.)*

---

## §D — Table schemas (fixed columns; one IQR format; no bare means)

**The IQR format is fixed everywhere: `median [q25–q75]`** (two decimals; e.g. `0.54 [0.52–0.56]`). Never a bare
mean, never ± unless it's a clearly-labelled std in a diagnostic.

**The RESULTS.md ledger — one section per rung, this row schema (no prose in the ledger):**

```
| <swept variable> | <metric₁> | <metric₂> | … | gap-to-ref | verdict |
```
Header line states the locked controls (`task, L, W, seeds, PROBE_EP, cost-units`). Last column = a ≤6-word verdict
(`composes`, `within noise`, `STRUCK — imports decayed top`, …). One variable swept per table (methodology rule 1);
the swept variable is the **first** column. **Per-rung column tuples are fixed (not free — the `…` above is filled
from here):**

| rung | columns (after the swept variable) |
| --- | --- |
| P5.1 | `peak@L · tail-L12 · readout-acc · vs-w12 · verdict` |
| P5.2 | `peak@L · tail-L12 · slope · readout-acc · bwd-work/w1 · vs-w12 · verdict` |
| P5.3 | `linear-probe · MLP-probe · profiler-peak · trunc-acc · verdict` |
| P5.4 | `head-acc · all-tap-acc · readout-params · verdict` |
| P5.5 | `acc · E-compute(fwd-MACs) · exit-depth · vs-all-tap · vs-trunc · oracle-gap · verdict` |
| P5.6 | `tail-L12 · mixed-flat-subtask-acc · per-block-Δ(α→0) · verdict` |
| P5.7 | `AA · BWT · retention · vs-P4.5 · verdict` |
| P5.8 | `dataset · decay-present? · fix-holds? · verdict` |

**Ablation / comparison tables (in cards):** one variable per row, **delta vs the baseline in its own column**, IQR
in **every** cell. The baseline row is first and labelled `(baseline)`.

**Struck-negative tables:** identical schema, with the failed condition and the **mechanistic reason** in the verdict
column — a struck mechanism gets the *same* rigor as a win (failures are data).

---

## §E — The summary writing contract (the 6 + 2 slots — fill verbatim, formal voice)

Every `expK/experiment-K.md` *Read* section fills the canonical **6 + 2** slots (the six carried from P1–4, plus two
re-pointed for a *fix* phase) **in this order, none empty** (if one is "n/a", say *why* — an empty Threats slot is a
red flag, not a clean result). **Write in the formal research voice** (see the voice rules below and the worked
card §F):

1. **Claim** — one *falsifiable* sentence. ("Sharper temperature composes depth without an architecture change.")
2. **Headline number** — median **[IQR]** across the seeds, **against its reference** (*precedence:* P5.0–P5.2 →
   w12 ceiling + chance; P5.3+ → add the truncation floor once it exists). *Never a bare number.*
3. **Figures** — the catalog refs emitted, each with a one-line read; name the headline figure explicitly.
4. **Mechanism** — *why* the number is what it is, tied to the substrate/algorithm reason (the spine: is it the class
   *direction* or a magnitude?). This is what makes it research, not a benchmark.
5. **Threats to validity** — what *else* could explain it (confound, an artifact, a swung seed); the methodology
   rule-1 check, written in.
6. **Decision** — which open knob this **sets** (temp / window / placement / residual y-n), and what the next rung
   inherits.
7. **Cost-honesty** — the cost is **measured** on the **continual** workload (expected-compute incl. heads + gate
   overhead), vs the truncation floor and all-tap; never a per-pass number, never "energy."
8. **SCFF-completion** — what this rung says about **"is SCFF done?"** + the **continual-safety (P5.7) verdict** for
   any change it proposes to bank. A rung that moves neither the depth story nor the cost story shouldn't have run.

**Voice rules (so summaries stop drifting in tone):** declarative and past-tense for what happened ("temp 0.2
composed to L7"); present-tense for standing reads ("a sharper contrast keeps each update on the class manifold");
**no hedging filler** ("seems to roughly suggest"), **no first-person**, **no exclamation**; every adjective backed
by a number or dropped; a struck result stated plainly ("λ>0 underperformed λ=0 at every value — the detached
reference imports the decayed top"). **Continuity:** each card **opens by naming the knob it inherits** from the
prior rung ("Inheriting the adopted temp from P5.1, …") so the phase reads as one thread, not nine islands. **A
skipped conditional rung** (e.g. P5.6 if no gap survives) is recorded as a **one-line skip-card** naming the gap-test
that closed it — so the inherited-knob chain never has a silent break.

---

## §F — Gold-standard worked card (copy this skeleton; this is the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches
> the **shape, voice, and completeness**, never an answer. Do not anchor on them (the rough T0/T3 figures are §0.3
> hypotheses; pre-seeding the expected win is the "tune-until-it-works" trap the project bans).*

```markdown
# P5.1 — Objective sharpness: temperature as the (maybe-)free depth lever

**Question.** Does sharpening the InfoNCE temperature compose depth further — *for free*, or partly as a disguised
learning-rate increase — and where is the floor?

**Setup.** Swept variable = temperature ∈ {0.5, 0.35, 0.2, 0.1, 0.05}; controls locked (window=2, mask=0.5,
headroom + flat + mixed, L12, W64, seeds [42,137,271,314,1729], PROBE_EP=120) + the mandatory **lr-matched arm**
(temp=0.5 swept to temp=0.2's effective-gradient-norm — the free-vs-lr test). Linear probe + the real nonlinear
readout. Apparatus: p5lib.SCFFContrastOverlap; guards passed (P5.0).

**Run.** N cells × 5 seeds, checkpointed (_ckpt.jsonl); 1 cell resumed after a laptop-sleep. Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| temp | peak@L | tail-L12 | readout acc | vs w12 ceiling | verdict |
| --- | --- | --- | --- | --- | --- |
| 0.50 (baseline) | Lₐ | 0.AA [0.A1–0.A2] | 0.aa [..–..] | −0.PP | composes ~Lₐ |
| 0.5→lr-matched | Lₐ′ | 0.A′ [..–..] | 0.a′ [..–..] | −0.P′ | the lr control |
| τ* (candidate) | L_b | 0.BB [0.B1–0.B2] | 0.bb [..–..] | −0.QQ | <real-better than the lr control?> |
| 0.05 | L_c | 0.CC [wide] | 0.cc [wide] | −0.RR | <collapse, per the §B rule?> |
- **DEPTH-PROFILE** (headline): <does the peak march vs BOTH baseline AND the lr-matched control?>, against the w12
  ceiling and the truncation floor. - **TEMP-FLOOR**: <where is the collapse cliff, per the §B real-difference rule>.
  - **INV**: dead-frac ≈ 0, FD-guard passed.

**Read (8 slots).**
1. *Claim* — A sharper InfoNCE temperature composes depth further, and the gain survives the lr-matched control (or: is partly lr — state which).
2. *Headline* — temp τ*: tail-L12 0.BB [IQR] vs the w12 ceiling 0.CC, the truncation floor 0.DD, **and the lr-matched temp=0.5** (the free-vs-lr test) (n=5, headroom).
3. *Figures* — DEPTH-PROFILE (peak march vs baseline AND lr-control), TEMP-FLOOR (collapse cliff per §B), INV (clean).
4. *Mechanism* — if τ* beats the lr-matched control: a sharper contrast makes each update more class-selective, holding
   the rep on the class manifold — direction-preservation by the objective (the spine). If it doesn't: the gain was
   effective-lr, not direction — say so plainly.
5. *Threats* — (a) the lr confound, addressed by the lr-matched arm; (b) probe ≠ readout — temp closing the *probe* gap need not close the *readout* gap (report both); (c) "real" only if IQR-disjoint + ≥4/5 sign.
6. *Decision* — sets the adopted temp = τ* (pending P5.7); mask held. P5.2 inherits τ* for the temp×w combo.
7. *Cost-honesty* — temp is free (no architecture, forward-only); backward work unchanged vs baseline (substrate units); the lr-matched arm isolates free-vs-lr.
8. *SCFF-completion* — moves the *earn-depth* verdict (tail in the w12 band? peak ≥ profiled depth?); **continual-safety
   NOT yet checked → P5.7 gates adoption, and may force a milder temp.**
```

This is the bar: every slot filled, IQR in every cell, both refs named, the spine invoked in the mechanism, the
continual gate flagged. A card that looks like this *cannot* be the messy output the contract exists to prevent.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

A rung is **not** done until every box is true. Paste this into the card and tick it.

- [ ] **Median [IQR]** shown for every headline number (n=5; 3 only for the heaviest continual cells) — **no bare means**.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 seeds by sign) before any gap is *claimed*; else "within noise."
- [ ] Every depth/accuracy figure draws **both** refs: the **w12 ceiling** and the **truncation floor**.
- [ ] Every figure drawn by a **`plot_p5.fig_*`** function (not inline styling); caption ends with the **takeaway** + `(n=5, task, PROBE_EP=120)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); written in the **formal voice**; the card **opens by naming the inherited knob**.
- [ ] **`manifest.json`** (git hash, resolved config, seeds, versions, wall-clock) **+ `arrays.npz`** written; **`plot_p5.py regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards** logged (FD-gradient < 1e-5 on any new backward path; equivalence checks; dead-frac sanity).
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874 guards.
- [ ] **Spine check:** no placement/exit reads goodness/energy; no residual α trained on local loss; no whitening-to-restore-rank.
- [ ] **Continual-safety (P5.7)** verdict recorded for any change proposed to bank.
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **struck** result logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P5.0** bench + decay | DEPTH-PROFILE (reproduction + w12 + truncation refs), INV (FD-guard + dead-frac) |
| **P5.1** sharpness | TEMP-FLOOR, DEPTH-PROFILE (per temp), INV |
| **P5.2** credit reach | CREDIT-REACH, DEPTH-PROFILE (per window + temp×w), INV (+ the struck-negative cards) |
| **P5.3** lost/rotated + bar | DEPTH-PROFILE (linear vs MLP probe), PLACEMENT (the profiler), the **truncation floor** established, INV |
| **P5.4** heads | PLACEMENT (per-head vs all-tap), INV |
| **P5.5** early-exit | **EXIT-PARETO** (continual, vs all-tap + truncation + oracle), exit-rate hist, INV |
| **P5.6** residual *(cond.)* | DEPTH-PROFILE (residual vs not), **RESIDUAL-ABLATION**, the S5-norm×residual check, INV |
| **P5.7** continual-safety | **CONT-SAFETY** (each adopted change vs P4.5), INV |
| **P5.8** natural-data | **NAT-ANCHOR** (digits + CIFAR-flat on the headline curves), INV |
| **P5.9** synthesis | the assembled DEPTH-PROFILE + EXIT-PARETO + CONT-SAFETY + the Phase-6 brief |

## Grounding (what the field does — and what we adopt)

- **Per-layer probe = where separability lives** (Alain & Bengio 2016; Intermediate-Layers-Matter SSL, NeurIPS 2021)
  → **DEPTH-PROFILE / PLACEMENT / the profiler**.
- **Deep supervision** (DSN, Lee 2015; Mono-Forward [2501.09238](https://arxiv.org/abs/2501.09238)) → the per-depth **heads**.
- **Calibrated early-exit, measured cost** (CALM, Schuster 2022; BranchyNet [1709.01686](https://arxiv.org/abs/1709.01686);
  Early-Exit survey 2024) → **EXIT-PARETO** + the calibration discipline; cost on the **continual** workload, not i.i.d.
- **Init-based preservation** (ReZero [2003.04887](https://arxiv.org/abs/2003.04887); Fixup [1901.09321](https://arxiv.org/abs/1901.09321));
  the bypass-cheat caution ([2404.10947](https://arxiv.org/abs/2404.10947)) → **RESIDUAL-ABLATION** (the α→0 guard).
- **Continual = AA/BWT/forgetting** (CL survey [2302.00487](https://arxiv.org/abs/2302.00487); GEM [1706.08840](https://arxiv.org/abs/1706.08840))
  → **CONT-SAFETY**, vs the P4.5 baseline.
- **Tuned-BP fairness + measured (not theoretical) cost** (Bartunov 2018; Spyra 2025 [2511.01061](https://arxiv.org/abs/2511.01061))
  → cost scoped to substrate backward-work, never energy.
- IQR / n=5 honesty / reproducibility / the summary slots — carried from Phase 1–4 ([`../result-format.md`](../result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to the catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent.
