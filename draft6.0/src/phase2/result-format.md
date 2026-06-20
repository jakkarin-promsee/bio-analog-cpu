# Phase 2 — Result format (the reporting standard, decided *before* the runs)

> **Why this exists, written before any experiment runs.** Letting a run produce its own format — its own
> graph style, table shape, summary voice — yields *messy, discontinuous* output: every experiment looks
> different, nothing is comparable, none of it is formal. So we decide **up front what a Phase-2 result looks
> like**, and every run follows it as the **baseline** — overridable or extendable when the actual data
> demands, but never re-invented from scratch.
>
> **This file does NOT re-derive Phase 1's house style — it *inherits* it.** The color/linestyle encoding,
> IQR bands, reference lines, axis rules, caption rule, the **reproducibility contract** (`manifest.json` +
> `arrays.npz` + a `plot.py` that regenerates every figure from saved data), and the **"calling a difference
> real at n=5"** rule are all imported verbatim from [`../phase1/result-format.md`](../phase1/result-format.md).
> This file adds only what Phase 2 needs that Phase 1 didn't: **depth curves, representation-structure
> metrics, drift, multi-block, the substrate-cost table, and the continual veto.**

---

## Layer A — house style additions (Phase-2-specific encoding)

Inherit Phase 1's Layer A. On top of it, lock these so they never drift across the norm/loss/interface runs:

| Rule | Locked to |
| --- | --- |
| **Normalization encoding** | each variant gets ONE colour+style forever: `layer-norm = dashed grey (the baseline to beat)` · `batch-norm = solid blue` · `online/streaming-BN = solid teal (the substrate candidate, our hero line)` · `group-norm = dotted purple` · `no-norm = thin red (the cheat/fail control)`. |
| **Depth axis** | **layer index on x (1…L), separability on y**; y on fixed `[chance, 1.0]`. A *rising* curve = depth helps (the whole Phase-2 goal); annotate the direction once. Always overlay the **pure-GD-hidden** curve (flat-high) and the **Phase-1 layer-norm** curve (declining) as the two reference envelopes. **Headroom is a precondition, not a result:** the curve is only interpretable if those two envelopes are *separated* — the GD-hidden reference must sit measurably above the layer-norm baseline. On an easy task (raw input already linearly separable — flat-MLP MNIST/digits) both envelopes pin near the top and "rising" is unfalsifiable; the depth-curve task must give that separation (README §2). State the measured envelope gap in the caption. |
| **"Hero vs reference"** | every depth/accuracy plot draws the **substrate-feasible** line bold and the GPU-only ones (plain batch-norm) thinner — we are choosing what survives on the chip, not what wins on a GPU. |
| **Lever provenance** | any borrowed mechanism names its source in the caption (`batch-norm: Trifecta` · `γ: Layer Collaboration` · `online-BN: Streaming Norm`) so the writeup stays honest about what's ours vs raided. |

---

## Layer B — the metric dictionary (PINNED — this is the half Phase 2 adds)

The point of pinning: "is depth helping?" must mean the *same measured thing* in every run, or the phase is
noise. Each metric below has a fixed definition; **the linear probe stays the primary, ground-truth metric**
(it measures *task-relevant* information); the others are *diagnostic* (they explain *why* the probe moved).

| Metric | Definition (pinned) | What it answers | Provenance / caveat |
| --- | --- | --- | --- |
| **Linear probe** (PRIMARY) | logistic reg, fixed L2 `C=1.0` (record), frozen 2k/2k activation split, trained to convergence — **per layer** | is this layer's representation *class-usable*? rising-with-depth = healthy | Alain & Bengio 2016. The ground truth; everything else is explanation. |
| **Fisher ratio** | `J = tr(S_B)/tr(S_W)` (between- / within-class scatter) on the probe split, per layer | class separability *margin*, cheaply, deterministically | complements the probe; cheap to log every layer |
| **NCC accuracy** | nearest-class-*mean* classifier accuracy, per layer | degree of *neural collapse* / how cleanly classes cluster | "effective depth" = first layer where NCC separates |
| **CKA** (diagnostic only) | linear CKA layer×layer matrix, `CKA(X,Y)=‖YᵀX‖_F²/(‖XᵀX‖_F‖YᵀY‖_F)` | are deep layers *redundant* with their input (homogenization = high CKA to input, low new info)? | Kornblith 2019. **Caveat: high CKA ≠ useful features (Horoi 2023) — never report CKA alone; always next to the probe.** |
| **Effective rank** | `erank = exp(H(σ̄))`, `H` = entropy of normalized singular values of the activation matrix, per layer | is the representation *collapsing* (low rank) with depth? | the quantitative face of "homogenization" |
| **Drift** (Phase-3 hand-off) | per-checkpoint mean `‖ĥ_t − ĥ_{t−1}‖` on a fixed probe set + **re-track cost** (GD steps/FLOPs to restore accuracy after a drift window) | how fast does *this algorithm's* SCFF move, and how dear is the correction? | **measured in Phase 2, used by the Phase-3 gate** — we don't build the gate, we hand it this |
| **Continual ACC** | mean final test accuracy over all tasks | does the depth-fix keep the Phase-1 continual win? | de-facto standard |
| **Continual BWT** | `(1/(T−1)) Σ_{k<T}(a_{T,k} − a_{k,k})`; **< 0 = forgetting** | rigorous forgetting (replaces exp4's ad-hoc "final all-class acc") | Lopez-Paz GEM; report ACC + BWT together |
| **Forgetting measure** | `(1/(T−1)) Σ_{k<T}(max_i a_{i,k} − a_{T,k})` | worst-case forgetting per task | report alongside BWT when tasks differ in difficulty |
| **Backward cost** | measured backward FLOPs + credit-distance (SCFF=0, GD=depth) | the substrate claim | port of Phase-1 F7 |

---

## Layer C — figure catalog (declare which you emit; don't invent new ones)

Reuse Phase-1 codes where the figure is the same (continuity); new Phase-2 figures get descriptive names.

| Code | Figure | Axes / form | The question it answers |
| --- | --- | --- | --- |
| **F3⁺ DEPTH CURVE** *(headline)* | per-layer **linear-probe vs layer index**, methods/norms overlaid, +GD-hidden & Phase-1-layernorm reference envelopes | **does separability *rise* with depth?** the entire Phase-2 thesis in one plot (the Trifecta-Fig-1 analog) |
| **F6⁺ WIDTH×DEPTH** | held-out acc as a surface/heatmap over (width × depth) at fixed weight budget; **wide-shallow vs narrow-deep** marked | can narrow-deep (substrate) match wide-shallow (paper)? the substrate-regime map |
| **REPR** | CKA layer×layer heatmap **+** effective-rank vs depth **+** Fisher/NCC vs depth (small-multiple) | *why* the probe moved — homogenization/collapse, quantified |
| **DECIDE** | frozen-deep-feature **max-power readout** vs **pure-GD**, bar + per-depth | **lost vs entangled** — the P2.0 fork that routes the whole phase |
| **DRIFT** | drift + re-track cost vs algorithm choice (small-multiple) | the Phase-3 gate hand-off |
| **BLOCK** | held-out acc vs **block-size k** / #blocks (GD-between cadence) | multi-block depth-gain (= the P2.5 "GD-between" knob) |
| **CONT (veto)** | **ACC + BWT** bars, *fix-in* vs *fix-out* vs Phase-1 baseline | does the depth-fix **preserve the continual win**? (the non-negotiable) |
| **F7 BACKWARD** | measured backward FLOPs, block vs GD | substrate cost — port |
| **INV** | loss-slope · dead-unit % · goodness saturation · effective-rank floor | health at a glance — port + erank |
| **SUBSTRATE table** | lever → {Scaps, registers, wires, online-feasible?, continual-safe?} | what actually survives on the chip |

**Worked caption for F3⁺ (the hero figure) — the model voice, so handed-off runs don't drift it.** Like
Phase-1's "Block holds GD accuracy at ¼ the backward cost (n=5, spiral σ=0.1, 16.6k wts)", every F3⁺ caption
ends with the one-sentence verdict + `(n=5, task, the move)`. Example:

> *"Online batch-norm turns SCFF's depth curve from declining to rising (slope −0.07→+0.04/layer), within
> 0.02 of GPU batch-norm — cheap depth survives going single-sample-online. (n=5, Tier-B σ=…, env. gap 0.31,
> layer-norm→online-BN.)"*

A caption that states a number without its **reference** (the GD-hidden envelope, the layer-norm baseline,
the envelope gap) is a toy — same rule as Phase 1.

**Ablation tables** (port Phase 1): one variable per row, delta vs the layer-norm baseline, **IQR in every
cell**, never a bare mean. **The two comparable scalars per run** stay: **AAA** (area under the held-out
curve) + **final held-out median ± IQR** — plus, new for Phase 2, the **depth-slope** (probe change per
layer; positive = depth helps) as the one-number summary of the headline.

---

## Layer D — the summary template (six slots + two Phase-2 slots)

Port Phase 1's six-slot *Read* (claim → number+IQR → figures → mechanism → threats → decision) and add **two
mandatory Phase-2 slots**, because they are the load-bearing questions of this phase and were never optional:

7. **Substrate-feasibility** — does the *online / single-sample* version of this lever keep the benefit, and
   what does it cost (Scaps / registers / wires)? "Works with a batch on a GPU" is **not** a Phase-2 pass.
8. **Continual-preservation (the veto)** — ACC + BWT with the fix in vs out. **A lever that lifts static
   depth but worsens BWT is rejected**, no matter how good the depth curve. State it explicitly every time.

No slot may be empty; a failed lever still fills all eight (slot 4 → "leading hypothesis for why it failed"),
and we do **not** tune-to-pass.

---

## Mandatory-per-experiment map (the floor)

| Experiment | Must emit |
| --- | --- |
| **P2.0** wall + decisive test | F3⁺ (the wall), **DECIDE** (lost/entangled), F6⁺ (width×depth gap), INV |
| **P2.1** normalization swap *(headline)* | **F3⁺** (norm variants overlaid), REPR, DRIFT, CONT-veto, INV |
| **P2.2** loss + negatives | F3⁺, REPR, ablation table (loss × negative), INV |
| **P2.3** collaboration (γ / OLU) | F3⁺, REPR (redundancy↓?), ablation table, INV |
| **P2.4** GD interface | ablation table (tap strategy) + held-out, F7 backward, INV |
| **P2.5** multi-block (GD-between) | **BLOCK**, F3⁺, F7, CONT-veto, INV |
| **P2.6** substrate filter | **SUBSTRATE table**, **CONT-veto (ACC+BWT)**, DRIFT, F7 |

---

## Grounding (what the field actually does — and what we adopt)

- **Depth as a per-layer curve, rising=good:** Trifecta ([2311.18130](https://arxiv.org/abs/2311.18130) Fig 1), and the *linear representation hypothesis* (separability should rise with depth) — Alain & Bengio ([1610.01644](https://arxiv.org/pdf/1610.01644)). → our **F3⁺**.
- **Representation structure across layers:** CKA (Kornblith [1905.00414](https://arxiv.org/pdf/1905.00414); reliability caveat Horoi [2210.16156](https://arxiv.org/abs/2210.16156)); width×depth via CKA (Nguyen [2010.15327](https://arxiv.org/pdf/2010.15327)); effective rank / neural collapse for compression. → **REPR**, **F6⁺**.
- **Continual reporting = ACC + BWT:** Lopez-Paz GEM convention, standard across the survey ([2403.05175](https://arxiv.org/html/2403.05175v1)). → **CONT-veto**.
- **Ablation discipline, IQR, n=5 honesty, reproducibility:** ported from Phase 1's `result-format.md`.

> This is the **floor**. Adapt upward per experiment; never drop below it. When a real result needs a figure
> not in the catalog, *add it to the catalog* (so the next run inherits it) rather than drawing a one-off.
