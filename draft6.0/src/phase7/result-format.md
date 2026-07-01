# Phase 7 — Result format (the binding presentation contract)

> **The drift this file exists to kill.** Handed only a purpose, an agent's output rots four ways — **(1)** graph formats
> drift; **(2)** table styles drift; **(3)** summaries drift; **(4)** no continuity rung-to-rung. This file removes the
> freedom that causes all four. It is **not advisory** — it is the *spec the run code and the write-up must conform to*,
> the way `design.md` is the spec the experiments conform to. **If a rung's output can't be produced by the rules below,
> the rung isn't done.**
>
> It **inherits** the canonical house style ([`../result-format.md`](../result-format.md)) and **adds the operational
> machinery** for Phase 7: the locked visual constants, the `plot_p7.py` API, the array schema, the table schemas, the
> 6+2 summary template, a worked card, and a pre-submit checklist. Read it once; then *obey it*, don't re-derive it.

---

## §0 — The three enforcement mechanisms (how consistency is made mechanical)

1. **One plotting module — `plot_p7.py` — ONE function per figure code.** Every rung calls the *same* function (§C); the
   look lives in one place (§A `STYLE`). No rung styles `matplotlib` inline.
2. **One summary template — the 8 slots (§E) — filled verbatim, formal voice, with the worked card (§F) as the model.**
3. **One ledger schema + one figure-regeneration path.** `RESULTS.md` rows follow the fixed schema (§D); `plot_p7.py
   regen <run-dir>` redraws *every* figure from `arrays.npz`, never from a live run. A figure you can't regenerate from
   saved data is a screenshot, not a result.

> **The rule of additions.** A rung that genuinely needs a new figure/metric **adds it to this file first** (so the next
> rung inherits it) — never a one-off. That one-off *is* the drift.

---

## §A — Locked visual constants (single source of truth; `plot_p7.py:STYLE`)

| constant | value | note |
| --- | --- | --- |
| **dpi** | **300** | PNG default (survives the pandoc→docx A4 path) |
| **figsize** | **single = (6.0, 4.0) in · wide/frontier = (7.5, 4.0) · panel-strip = (10, 2.2)** | one of three sizes — never ad-hoc |
| **font** | **DejaVu Sans**, base **10 pt** (title 11 bold · axis 10 · tick 9 · caption 9) | identical every plot |
| **background** | **transparent** | docx/slide reuse |
| **IQR band / error bar** | **median line (1.8 lw) + shaded fill at alpha 0.18** for curves; **median bar + IQR whisker** for bar charts | every headline, no exceptions |
| **grid** | light grey `#d9d9d9`, 0.6 lw, behind data | on for line/frontier plots, off for bars |

**Head / method encoding (colour · style — fixed forever; the readout family IS the method here):**

| head (method) | colour (hex) | line / marker | role |
| --- | --- | --- | --- |
| **cosine** (spine-pure; NCM + softmax variants) | `#d9690a` (orange) | solid, **bold 2.2 lw**, circle | ⭐ the spine candidate — the head we hope wins |
| **linear-softmax** (convex floor) | `#7f7f7f` (grey) | solid | the floor every head is measured against |
| **NCM** (Euclidean prototype) | `#2c6fbf` (blue) | solid, square | recency-robust magnitude |
| **SLDA** (tied covariance) | `#2c6fbf` (blue) | **dashed**, square | the cheaper covariance *middle* (one shared cov) |
| **FeCAM** (per-class Mahalanobis) | `#8a1b8a` (magenta) | solid, diamond | the **max-magnitude** pole (accuracy SOTA) |
| **RanPAC** (rand-proj + ridge) | `#0b8f6a` (teal) | solid, triangle | analytic / no-gradient (with projection) |
| **RLS-ridge / F-OAL** (analytic, no proj) | `#0b8f6a` (teal) | **dashed**, triangle | analytic / no-gradient (same family, no projection) |
| **GKEAL** (kernel, conditional) | `#0b8f6a` (teal) | dotted, plus | closed-form non-linear fallback |
| **MLP head** (non-convex anchor) | `#9467bd` (purple) | solid | the "if we paid non-convex GD" anchor |
| **race_bp** (tuned-BP **static** ceiling) | `#2ca02c` (green) | **dashed** | the achievable old-world **static-accuracy** ceiling — **static/AAA panels ONLY, never on BWT/continual figures** |
| **random-proj control** (taps / pixels) | `#111111` (black) | **dotted** (taps) / dash-dot (pixels) | the skeptic — did the bulk earn its keep (taps = fair; pixels = harsher, true RanDumb) |
| **chance** | `#111111` dotted thin | — | the floor of floors |

Head families read by **colour**: orange = the spine candidate (cosine-NCM + cosine-softmax); grey = the convex floor;
blue = magnitude prototypes (NCM solid / SLDA dashed); magenta = FeCAM (max-magnitude); teal = analytic/no-gradient (solid
= with projection, dashed = without); purple = the non-convex anchor; green = the **static** BP ceiling; black = the
random-projection control (dotted = taps, dash-dot = pixels). **The frontier plots order heads left→right by *measured*
spine-cleanliness** (direction-pure → max-magnitude), among the **accuracy-competitive** heads only (sub-floor heads are
**greyed**, never anchoring the spine axis), never by an asserted order.

**Required `plot_p7.py` API (one function per figure; signatures fixed):**

```
STYLE                       # the dict of constants above; the ONLY place styling lives
fig_bakeoff(run)            # F: BAKEOFF      (THE headline — the frontier + the 4-axis scorecard)
fig_spine_clean(run)        # F: SPINE-CLEAN
fig_multimodal(run)         # F: MULTIMODAL
fig_imbalance(run)          # F: IMBALANCE
fig_cont_safety(run)        # F: CONT-SAFETY  (the gate)
fig_nat_anchor(run)         # F: NAT-ANCHOR
fig_randumb(run)            # F: RANDUMB
fig_cost(run)               # F: COST-PROXY
fig_inv(run)                # F: INV (every run)
regen(run_dir)              # redraws every figure whose arrays are present in <run-dir>/arrays.npz — the citable path
```

The **P7.6 synthesis re-uses these functions** on the assembled-head run (BAKEOFF + SPINE-CLEAN + CONT-SAFETY +
NAT-ANCHOR) — it adds **no new plotter**. Every `fig_*` reads `arrays.npz` + `manifest.json`, draws in `STYLE`, writes a
300-dpi PNG. **No rung draws outside these functions**, and **every rung writes `arrays.npz` to the schema below.**

**The `arrays.npz` schema (pinned — key · shape · meaning; a rung emits the subset its figures need):**

| key | shape | meaning |
| --- | --- | --- |
| `seeds` | `[S]` | seed list (S=5; 9 for the ≤0.02 spine-tension gaps; 3 only for the heaviest continual cells) |
| `heads` | `[H]` (str) | the head names raced — **the "method" axis** that lets BAKEOFF draw every head + the anchors |
| `acc_<head>` | `[S]` | final held-out accuracy (also `aaa_<head>` `[S]` = area under acc vs log-samples) |
| `bwt_<head>` · `aa_<head>` · `forget_<head>` | `[S]` | continual BWT / average accuracy / forgetting — the harness's **actual** outputs (`acc_matrix_metrics`); **NOT "retention"** (no such continual metric exists — that word is the A7-noise `acc(σ)/acc(0)`, a different quantity) |
| `spineflip_<head>` | `[S, P]` | argmax-flip rate vs the per-class norm-perturbation grid (`perturb` `[P]`); cosine ≈ 0 — the clean, non-gameable spine probe (a) |
| `recencydrop_<head>` | `[S]` | old-class accuracy drop under the **actual bursty stream** = the task-recency-bias read (spine probe (b); **not** synthetic norm-inflation, which is circular for cosine) |
| `mm_ladder_<rung>` | `[S, D]` | accuracy per fallback-ladder rung (`rung ∈ mean/slda/fecam/gkeal/mixture`), per dataset `D ∈ {digits, cifarflat, synthblob}` — the **natural** datasets decide; `synthblob` is apparatus-sanity only |
| `nmodes` | `[S, C]` | per-class mode count / silhouette in the **natural** frozen tap space (the decision-bearing multimodality probe, P7.2) |
| `imbal_<head>_<guard>` | `[S, 2]` | per-class accuracy `[old, recent]`, `guard ∈ {none, logitadj, balsoftmax, cbrs, air}` (`air` = the no-gradient analytic-family guard) (P7.3) |
| `cost_<head>` | `[S]` or scalar | readout forward-MACs + Gram/solve-dim **proxy** — **DESCRIPTIVE-only, never a decision axis; tagged "(proxy; real=P8)"** |
| `randumb_<head>` | `[S, 3]` | accuracy `[ours_bulk, randproj_taps, randproj_pixels]` for the same head (the two-arm control, P7.0) |
| `inv_<panel>` | `[S, …]` | INV panels (`lossslope`/`deadfrac`/`erank`/`fdguard`/`featpinned`) |

> **Source-of-truth note:** canonical [`../result-format.md`](../result-format.md) Layer A **owns** any shared constant
> (dpi, IQR band, the n=5 rule); the restatement above is the **binding restatement for the Phase-7 executor**; if they
> diverge, **canonical wins.** Phase-7-*new* and *owned* here: the head-family colour encoding, the frontier ordering by
> measured spine-cleanliness, the RanDumb-control pairing, the cost-is-a-proxy tag, and the array schema.

---

## §B — The metric dictionary (PINNED; Phase-7 additions in **bold**)

| metric | definition (pinned — do not redefine per rung) | units / format |
| --- | --- | --- |
| **readout accuracy** | final held-out acc + **AAA** (trapezoid area under acc vs log₁₀-samples ÷ log-span), vs the convex floor + the **static** BP ceiling | acc, median [IQR] |
| continual **BWT / AA / forget** | GEM/CL-survey conventions — the harness's actual outputs (**not "retention"**); head vs **the floor-head-on-same-bulk baseline**; + paired-sign veto at the gate | acc / acc-delta |
| **spine-cleanliness** | **(a)** argmax-flip rate under per-class weight/prototype-norm rescale (clean, non-gameable); **(b)** old-class acc drop under the **actual bursty stream** (task-recency-bias read — NOT synthetic inflation, which is circular for cosine). **Read only for accuracy-competitive heads** (sub-floor greyed) | flip-fraction ∈ [0,1] / acc-drop |
| **multimodality** | per-class n-modes / silhouette / GMM-BIC in the **natural** frozen tap space (decision-bearer); + acc recovered per fallback-ladder rung | count / acc |
| **imbalance robustness** | per-class acc split (old vs recent) under the bursty stream, guard on/off (trained: logit-adj/bal-softmax; analytic: **AIR**) | acc, median [IQR] |
| **readout cost-proxy** | readout forward-MACs + analytic Gram/solve dim (dim² store, dim³ solve) — **DESCRIPTIVE-only, never a decision tie-break; tagged "(proxy; real = Phase 8)"** | analytic count (tagged proxy) |
| **random-projection control** | acc: OURS-bulk vs (a) random-from-taps (fair expansion) and (b) random-from-pixels (true RanDumb), same head | acc, median [IQR] |

**Spine-cleanliness is a first-class axis, not a footnote — but conditional on competitive accuracy** (the spine): a head
that wins accuracy by a magnitude trick but flips its verdict under a per-class norm nuisance is not the namer we want;
equally, a head that is *trivially* spine-clean by being useless (a stably-useless verdict) is **greyed out of the
frontier** — spine-cleanliness is interpreted only for heads within-band of the convex floor. Report accuracy, BWT,
**and** spine-cleanliness together; when they disagree, **name the tension** — it is the phase's headline. **Cost is a
PROXY, descriptive-only** — never a tie-break, never a settled 80/20 or vs-BP energy claim in Phase 7.

**The verdict cut (PINNED, blind — the spine-tension resolution):** let `Δ = (acc×BWT of the best magnitude head) −
(cosine)`, **paired by seed**, and `δ = 0.02` (acc at matched BWT). **cosine-free** = `Δ` within noise (paired-Δ IQR
includes 0, or sign < 4/5); **cosine-at-a-price(X)** = `Δ` real (paired-Δ IQR excludes 0 ∧ ≥4/5 sign) but `|Δ| ≤ δ`;
**magnitude-wins-spine-bends** = `Δ` real ∧ `|Δ| > δ` ∧ the recency-under-bursty probe shows the magnitude head is not
fragile in our regime. No result may be narrated into a branch it does not numerically satisfy.

**Calling a difference real (n=5, carry — load-bearing):** real only if **IQR bands disjoint at the final checkpoint**
*and* **sign consistent in ≥4/5 seeds, paired by seed**; else **"within noise."** **At the P7.4 GATE, "within noise" is
NOT an auto-pass** — add the paired-sign veto (negative-BWT vs the floor-head baseline in ≥4/5 paired seeds = fail). The
**decisive spine-tension gap** `Δ` gets **~9 seeds** when ≤0.02, so the rung can adjudicate the tension it exists for.

---

## §C — The figure catalog (declare which you emit; never invent)

Each figure = one `plot_p7.fig_*` function (§A). **Every accuracy figure draws the convex floor AND the BP ceiling** —
a head is only interpretable between "the dumbest linear head" and "genuinely-tuned BP."

| code | function | axes / form | the question it answers |
| --- | --- | --- | --- |
| **BAKEOFF** *(THE headline)* | `fig_bakeoff` | **left:** accuracy×BWT frontier scatter, one point per head, ordered left→right by measured spine-cleanliness, floor+ceiling refs; **right:** 4-axis scorecard bars (acc · BWT · spine-clean · cost-proxy) per head | where does accuracy×BWT peak on the direction↔magnitude axis; what does spine-cleanliness cost |
| **SPINE-CLEAN** *(the spine)* | `fig_spine_clean` | **left:** argmax-flip rate vs per-class norm-perturbation, per head (cosine flat at 0; **sub-floor heads greyed**); **right:** old-class acc drop under the **actual bursty stream** (task-recency read), bars | how much a pure magnitude nuisance moves each *competitive* head's verdict |
| **MULTIMODAL** | `fig_multimodal` | acc vs the fallback ladder (mean→SLDA→FeCAM→GKEAL→mixture) on the **natural** data (digits/CIFAR-flat, the decider) + the synth-blob **sanity** arm; + the per-class n-modes probe | does one prototype underfit *on natural data*; is a closed-form escape enough |
| **IMBALANCE** | `fig_imbalance` | per-class acc (old vs recent) with/without guard (trained: logit-adj/bal-softmax; analytic: **AIR**), per head, bursty stream | does the head develop recency bias; does its family-matched guard fix it |
| **CONT-SAFETY** *(the gate)* | `fig_cont_safety` | BWT / AA / **forget** bars, each head vs the **floor-head-on-same-bulk baseline** (+ paired-sign veto marker) | does the head keep the A6 continual win |
| **NAT-ANCHOR** | `fig_nat_anchor` | the BAKEOFF headline with **digits + CIFAR-flat** overlaid | does the readout choice survive real flat data |
| **RANDUMB** | `fig_randumb` | acc bars, OURS-bulk vs **random-from-taps** vs **random-from-pixels**, same head | did the trained bulk earn its keep at naming (both arms) |
| **COST-PROXY** | `fig_cost` | readout forward-MACs + Gram/solve-dim per head, **labelled PROXY, descriptive-only** | comparability across heads (NOT a decision axis, NOT a settled 80/20) |
| **INV** *(EVERY run)* | `fig_inv` | small-multiples: loss-slope/convergence · dead-unit % (≈0) · effective-rank · FD-guard pass · **feature-source-pinned** | health + apparatus sanity at a glance |

**Caption rule (every figure, no exceptions):** one sentence, ending with **the takeaway** (not a description), then
`(n=5, task, PROBE_EP=…)`. A **static-accuracy** caption **never** states a number without naming the **convex floor** and
the **static BP ceiling** — but the **static BP ceiling appears ONLY on static/AAA panels, never on BWT/CONT-SAFETY
figures** (a static-tuned BP is not a forgetting baseline — that fair fight is P9). A "cheaper" caption **always** tags
**(proxy; real meter = P8)** and never implies a *preference* (cost is descriptive-only). A spine caption reports the
**argmax-flip / recency-drop** for the *competitive* heads, not just accuracy. Model caption:

> *"The cosine head matched the FeCAM accuracy×BWT frontier (0.AA vs 0.BB, within noise) at **argmax-flip 0.0 vs FeCAM
> 0.CC** — spine-clean at no accuracy cost, above the convex floor (0.FF), below the BP ceiling (0.EE). (n=9, continual
> digits, PROBE_EP=…)"*
>
> *(Letters are deliberate placeholders — the caption teaches the **shape**, never an expected result. Do **not** anchor
> on any number; the §0.3 hypotheses are not findings — pre-seeding the expected win is the "tune-until-it-works" trap the
> project bans.)*

---

## §D — Table schemas (fixed columns; one IQR format; no bare means)

**IQR format fixed everywhere: `median [q25–q75]`** (two decimals). Never a bare mean.

**The RESULTS.md ledger — one section per rung, this row schema (no prose in the ledger):**

```
| <swept variable> | <metric₁> | <metric₂> | … | vs-ref | verdict |
```
Header line states the locked controls (`task, feature-source, seeds, PROBE_EP`). Last column = a ≤6-word verdict
(`spine-clean & free`, `within noise`, `STRUCK — dents A6`, `magnitude wins`, …). One variable swept per table; the swept
variable is the **first** column. **Per-rung column tuples are fixed:**

| rung | columns (after the swept variable) |
| --- | --- |
| P7.0 | `head/bulk · acc · vs-floor · vs-static-ceiling · vs-randproj-taps · vs-randproj-pixels · verdict` |
| P7.1 | `head · acc · BWT · spine-flip · recency-drop · cost-proxy(descriptive) · vs-floor · verdict` *(head swept; cosine-NCM/cosine-softmax/NCM/SLDA/FeCAM/RanPAC/RLS/linear/MLP rows)* |
| P7.2 | `ladder-rung · acc(natural: digits/CIFAR-flat) · acc(synth-blob sanity) · n-modes(natural) · closed-form? · verdict` |
| P7.3 | `guard · acc-old · acc-recent · recency-bias · verdict` *(per committed head; guard family-matched — AIR for analytic)* |
| P7.4 | `head · AA · BWT(+paired-sign) · forget · vs-floor-head-on-same-bulk · verdict` |
| P7.5 | `dataset · ordering-holds? · committed-head-acc · vs-floor/static-ceiling · verdict` |

**Ablation / comparison tables (in cards):** one variable per row, **delta vs the reference in its own column**, IQR in
**every** cell; the reference row first, labelled `(floor)` or `(ceiling)`. **Struck-negative tables:** identical schema,
with the failed condition and the **mechanistic reason** in the verdict column — a struck head gets the *same* rigor as a
win (failures are data: a head that dents A6, a magnitude head that flips under norm-rescale, a mixture that goes
non-convex without recovering accuracy).

---

## §E — The summary writing contract (the 6 + 2 slots — fill verbatim, formal voice)

Every `expK/experiment-K.md` *Read* section fills the **6 + 2** slots **in this order, none empty** (if one is "n/a", say
*why*). **Formal research voice** (rules below; the worked card §F):

1. **Claim** — one *falsifiable* sentence. ("The cosine head matches FeCAM's accuracy×BWT while staying spine-clean.")
2. **Headline number** — median **[IQR]** across seeds, **against its references** (the convex **floor** *and* the BP
   **ceiling**). *Never a bare number.*
3. **Figures** — the catalog refs emitted, each with a one-line read; name the headline figure explicitly.
4. **Mechanism** — *why* the number is what it is (the spine: is the win a preserved class **direction** (cosine, low
   argmax-flip) or a **magnitude** trick (recency-robust-by-no-trained-weights)? which head **family**?). This is what
   makes it research.
5. **Threats to validity** — what *else* could explain it (a **cost proxy** flattering the analytic head, a **synthetic**
   multimodality artifact, an **unpinned feature source**, a swung seed); the methodology rule-1 check, written in.
6. **Decision** — which open knob this **sets** (the committed head / the multimodality modeling / the imbalance guard),
   and what the next rung inherits.
7. **Spine-honesty** *(re-pointed from cost-honesty)* — spine-cleanliness was **measured** (argmax-flip + recency-drop),
   not assumed; the "cheaper" claim is tagged **proxy (real meter = P8)**; the **RanDumb** control read is stated (did the
   bulk earn its keep); no head was called "the spine" for being a *distance* classifier.
8. **Namer-verdict / continual-safety** — what this rung says about the **committed namer**, the **A6 continual-safety
   (P7.4) verdict** for any head it proposes to bank, and which **spine-tension branch** (cosine-free /
   cosine-at-a-price / magnitude-wins-spine-bends) it currently leans. A rung that moves neither the namer choice nor the
   spine verdict shouldn't have run.

**Voice rules:** declarative past-tense for what happened ("the cosine head matched FeCAM within noise at argmax-flip
0.0"); present-tense for standing reads ("a cosine head classifies by angle, so a per-class norm nuisance cannot move its
verdict"); **no hedging filler**, **no first-person**, **no exclamation**; every adjective backed by a number or dropped;
a struck result stated plainly ("the trained-softmax head dented BWT in 5/5 paired seeds — rejected by the A6 gate
regardless of its accuracy"). **Continuity:** each card **opens by naming the knob it inherits** ("Inheriting the pinned
tap-feature run-dir + the convex floor from P7.0, …"). A **skipped conditional rung** (e.g. GKEAL if FeCAM already
recovers multimodality) is a **one-line skip-card** naming the gap-test that closed it.

---

## §F — Gold-standard worked card (copy this skeleton; this is the target)

> *⚠ The numbers below are **deliberately fictional** — chosen NOT to match any expected result — so the card teaches the
> **shape, voice, and completeness**, never an answer. Do not anchor on them (the §0.3 hypotheses are not findings).*

```markdown
# P7.1 — The readout bake-off: naming the frozen bulk

**Question.** Across the namer taxonomy, where does accuracy×BWT peak on the direction↔magnitude axis, and what does
spine-cleanliness cost? Does the cosine head match the magnitude-based no-gradient SOTA?

**Setup.** Swept variable = the readout head ∈ {linear-softmax(floor), cosine, NCM, FeCAM, RanPAC/RLS, MLP, race_bp(ceil)};
controls locked (frozen NoiseAugContrast bulk, pinned tap-feature run-dir from P7.0, continual digits home, seeds
[42,137,271,314,1729] (+4 for the ≤0.02 spine gap), PROBE_EP=…). BAKEOFF + SPINE-CLEAN + COST-PROXY. Apparatus:
p7lib heads; guards passed (P7.0: head-port ≡ parent; FD < 1e-5; feature-source pinned).

**Run.** H heads × 5–9 seeds, checkpointed (_ckpt.jsonl); fast (bulk frozen, only heads fit). Wall ≈ XX min.

**Result / figures.** *(fictional numbers — shape only)*
| head | acc | BWT | spine-flip | recency-drop | cost-proxy | vs-floor | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear-softmax (floor) | 0.FF [..–..] | −0.xx | 0.HH | 0.rr | 1.0× | (floor) | the floor |
| cosine | 0.AA [..–..] | −0.aa | **0.00** | **0.00** | c× | <better?> | <spine-clean & free?> |
| FeCAM | 0.BB [..–..] | −0.bb | 0.CC | 0.dd | c2× | <better?> | <max acc, max magnitude?> |
| RanPAC/RLS | 0.GG [..–..] | −0.gg | 0.JJ | 0.jj | c3×(proxy) | <better?> | <no-gradient, cheap?> |
| race_bp (ceiling) | 0.EE [..–..] | −0.ee | 0.KK | 0.kk | — | (ceiling) | the BP reference |
- **BAKEOFF** (headline): <where does acc×BWT peak on the spine axis; is cosine on the frontier?>.
  - **SPINE-CLEAN**: <cosine flat at 0 flips; FeCAM/linear rise with the norm nuisance?>.
  - **COST-PROXY**: <analytic head cheaper by proxy — tagged real-meter-P8>. - **INV**: dead-frac ≈ 0, FD ✓, feat-pinned ✓.

**Read (8 slots).**
1. *Claim* — the cosine head sits on the accuracy×BWT frontier while being the only argmax-flip-0 head.
2. *Headline* — cosine acc 0.AA [IQR] vs FeCAM 0.BB and the convex floor 0.FF, BP ceiling 0.EE (n=9, continual digits).
3. *Figures* — BAKEOFF (frontier), SPINE-CLEAN (flip-0 for cosine), COST-PROXY (analytic cheap, proxy), INV (clean).
4. *Mechanism* — if cosine matched with flip-0: angle-only classification is invariant to the magnitude nuisance (the spine). If FeCAM won on acc but flipped under norm-rescale: a magnitude edge — name the tension.
5. *Threats* — (a) cost is a proxy (real meter = P8); (b) synthetic-home multimodality may favor FeCAM (P7.2 checks); (c) unpinned features (guarded); (d) "real" only if IQR-disjoint + ≥4/5 sign.
6. *Decision* — sets the candidate committed head (pending the P7.4 gate); next rung inherits it.
7. *Spine-honesty* — spine-cleanliness measured (flip + recency), not assumed; "cheaper" tagged proxy; NCM/FeCAM not called "the spine" (they read a distance = magnitude).
8. *Namer-verdict* — leans <cosine-free / cosine-at-a-price(X) / magnitude-wins-spine-bends>; **A6 gate NOT yet checked → P7.4 gates adoption**.
```

This is the bar: every slot filled, IQR in every cell, both references named, cost tagged proxy, the spine measured, the
continual gate flagged. A card that looks like this *cannot* be the messy output the contract exists to prevent.

---

## §G — The pre-submit checklist (run before calling ANY rung "done")

Paste into the card and tick. A rung is **not** done until every box is true.

- [ ] **Median [IQR]** for every headline number (n=5; 9 for the ≤0.02 spine-tension gap; 3 only for the heaviest continual cells) — **no bare means**.
- [ ] The **"real difference" rule** applied (IQR disjoint **and** ≥4/5 by sign) before any gap is *claimed*; else "within noise."
- [ ] Every **static-accuracy** figure draws the **convex floor** + the **static BP ceiling** (`race_bp`); the static BP ceiling is **NOT** drawn on any **BWT / CONT-SAFETY** figure (static ≠ forgetting baseline — that's P9).
- [ ] **Spine-cleanliness measured** ((a) argmax-flip under per-class norm-rescale + (b) old-class drop under the **actual bursty stream**, not synthetic inflation) and **interpreted only for accuracy-competitive heads** — sub-floor heads **greyed**, never anchoring the frontier; cosine ≈ 0 flips confirmed.
- [ ] **Cost tagged a PROXY and used descriptively ONLY** (real meter = Phase 8); cost is **never a tie-break**; no settled "80/20" or vs-BP energy claim made in Phase 7.
- [ ] **Feature source LOADED from the pinned P7.0 run-dir** + `PROBE_EP` frozen from P7.0, not re-extracted/re-set (the no-baseline-drift rule); the feature-source-pinned INV panel is green.
- [ ] **Random-projection control** reported at P7.0 in **both arms** (random-from-taps + random-from-pixels, fair expansion); the "did the bulk earn its keep" read stated — and if it ties on the flat home, **both readings** reported (P4/P5-consistent AND naming-stage value unverified, flagged to Stage 2), **not** pre-excused.
- [ ] **P7.2 multimodality** decided on the **natural** tap space (synth-blob is sanity-only); the fallback ladder (mean→SLDA→FeCAM→GKEAL→mixture) run only as far as accuracy recovers; whether the escape stayed **closed-form** or forced a **non-convex mixture** is stated.
- [ ] **P7.3 imbalance** — the **family-matched** guard tested per committed head (trained: logit-adj/bal-softmax; analytic: **AIR**); whether the no-gradient head needed any guard (or dodged it by construction) recorded.
- [ ] **P7.4 the GATE runs 5 seeds** (never 3) via the **built** `continual_safety_heads` (head-factory; each head under its native online+sleep rule); baseline = the **floor-head on the same bulk** (NOT "the P5 readout"); "within noise" is NOT an auto-pass — the **paired-sign veto** (negative-BWT vs that baseline in ≥4/5 paired seeds = fail) applied.
- [ ] **Verdict branch matches its numeric cut** (§B): `Δ` paired, `δ=0.02`; no result narrated into a branch it doesn't satisfy.
- [ ] **Spine reported alongside accuracy** (the spine); when accuracy and spine-cleanliness disagree, the tension is **named** (not resolved silently toward accuracy).
- [ ] Every figure drawn by a **`plot_p7.fig_*`** function (no inline styling); caption ends with the **takeaway** + `(n=…, task, PROBE_EP=…)`.
- [ ] All **8 summary slots** filled (none empty; "n/a" justified); **formal voice**; the card **opens by naming the inherited knob**.
- [ ] **`manifest.json`** (git hash, config, seeds, versions, wall-clock) **+ `arrays.npz`** written; **`plot_p7.py regen <run-dir>`** redraws every figure from saved data.
- [ ] **Guards** logged: head-port ≡ parent equivalence (`cosine(unit,ncm) ≡ NCM(normalized)`, `cosine-softmax(τ→∞,normalized) ≡ linear-softmax`, `linear head ≡ P5 readout`, **`continual_safety_heads(linear) ≡ old continual_safety`**); FD-gradient < 1e-5 on every trained head; dead-frac sanity; feature-source pinned.
- [ ] Single-threaded run confirmed (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — the phantom-hang + cp874 guards; **no sklearn** for compute; the real PID verified alive on multi-hour cells.
- [ ] **Continual-safety (P7.4)** verdict recorded for any head proposed to bank.
- [ ] `RESULTS.md` row added in the fixed schema (§D); a **struck** head logged with its mechanistic reason.

---

## Mandatory-per-experiment map (the floor)

| rung | must emit |
| --- | --- |
| **P7.0** bench + refs + control | acc reproduction (floor/static-ceiling), **RANDUMB** (taps + pixels arms), INV (FD-guard + feature-source-pinned + dead-frac) |
| **P7.1** bake-off | **BAKEOFF** (frontier + scorecard), **SPINE-CLEAN** (sub-floor greyed), **COST-PROXY** (descriptive), INV |
| **P7.2** multimodality | **MULTIMODAL** (fallback ladder on natural data + n-modes probe; synth-blob sanity arm), INV |
| **P7.3** imbalance | **IMBALANCE** (old vs recent, family-matched guard on/off, per head), INV |
| **P7.4** continual-safety | **CONT-SAFETY** (each head vs the floor-head-on-same-bulk, 5 seeds + paired-sign veto), INV |
| **P7.5** natural-data | **NAT-ANCHOR** (digits + CIFAR-flat on the bake-off headline), INV |
| **P7.6** synthesis | the assembled BAKEOFF + SPINE-CLEAN + CONT-SAFETY + NAT-ANCHOR + the committed readout + the spine-tension verdict + the Stage-2 brief |

## Grounding (what the field does — and what we adopt)

- **Train only the readout on a frozen bulk = convex** (Reservoir/ESN, Jaeger 2001; ELM, Huang 2006; OCO, Hazan) → the
  convex floor + the "no heavy optimizer" frame ([`the-convex-readout.md`](../../research/papers/phase7/the-convex-readout.md)).
- **Cosine reads direction; NCM/SLDA read a distance = magnitude** (cosine-normalization; SCR [2103.13885]; Deep SLDA
  [1909.01520]) → the spine-clean candidate + the spine-cleanliness probe
  ([`direction-readouts.md`](../../research/papers/phase7/direction-readouts.md)).
- **No-gradient streaming naming is a published paradigm** (RanPAC [2307.02251]; ACL/RLS family — ACIL, DS-AL
  [2403.17503], **F-OAL** NeurIPS 2024) → the analytic heads; RLS = joint-equivalent, forward-only-online is on-constraint
  ([`analytic-and-covariance-readouts.md`](../../research/papers/phase7/analytic-and-covariance-readouts.md)).
- **Per-class covariance handles heterogeneity closed-form** (FeCAM [2309.14062]; GKEAL kernel) → the multimodality
  fallback ladder (P7.2) that stays closed-form before a non-convex mixture.
- **A random projection + a good readout is a strong baseline** (RanDumb [2402.08823]) → the RanDumb control (P7.0), the
  "did the bulk earn its keep" test.
- **The magnitude/recency bias is the continual failure of a trained head** (BiC [1905.13260]; Weight-Alignment
  [1911.07053]; logit-adjust [2311.06460]) → the imbalance guard (P7.3) + why spine-cleanliness predicts BWT.
- **Continual = AA/BWT/forgetting** (CL survey [2302.00487]; GEM [1706.08840]) → **CONT-SAFETY**, vs the Phase-5 readout.
- IQR / n=5 honesty / reproducibility / the summary slots — carried from Phase 1–6
  ([`../result-format.md`](../result-format.md)).

> The **floor**. Adapt upward per rung; never below it. A real result needing a new figure → **add it to the catalog
> first** (the next rung inherits it), never a one-off — the drift this file exists to prevent.
