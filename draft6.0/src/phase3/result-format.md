# Phase 3 — Result format (the reporting standard, decided *before* the runs)

> **Why this exists, written before any experiment runs.** Letting each run invent its own format — its own
> graph style, table shape, summary voice — yields *messy, discontinuous* output: every experiment looks
> different, nothing is comparable across rungs, none of it is formal. So we decide **up front what a Phase-3
> result looks like**, and every run follows it as the **baseline** — overridable or extendable when the actual
> data demands, but never re-invented from scratch. This is a **contract**, not a suggestion: a handed-off run
> obeys it so P3.0…P3.3 stack into one legible story.
>
> **It does NOT re-derive the house style — it *inherits* it.** Layer A encoding, IQR bands, reference lines,
> axis rules, the caption rule, the **reproducibility contract** (`manifest.json` + `arrays.npz` + a `plot.py`
> that regenerates every figure from saved data with no retrain), and the **"calling a difference real at n=5"**
> rule (disjoint IQR + ≥4/5 seeds) come verbatim from
> [`../phase1/result-format.md`](../phase1/result-format.md) and
> [`../phase2/result-format.md`](../phase2/result-format.md). Phase 3 adds only: the **objective/lever encoding**,
> the **depth-*shape* metric family** (so "where the curve bends" stops being lost in a single slope), and the
> **info-preservation curve** (the new objective's native causal read). The 6+2 summary slots and the continual
> veto carry over unchanged.

---

## Layer A — house-style additions (Phase-3 objective/lever encoding)

Inherit Phase 1+2 Layer A. On top, **lock these so they never drift across P3.0…P3.3** — every objective and
lever gets ONE colour+style forever:

| Element | Encoding (fixed) | Role |
| --- | --- | --- |
| **energy wall** (the P2.1 healthy cell: layer-norm + linear + contrast) | **dashed grey** | the baseline every curve must bend up — same "baseline = dashed grey" as Phase 2 |
| **masked-feature reconstruction** | **bold solid green** | **the Phase-3 hero** (substrate-native, single-sample, the decided primary objective) |
| **sibling-contrastive (CLAPP)** | solid orange | the unsupervised *contrastive* control (is preservation alone enough?) |
| **OLU / direct-feedback** (coordination, P3.1) | same hue as the base objective; **+OLU = dashed, +direct-feedback = dash-dot** | a *booster on* an objective, never a standalone colour |
| **Mono-Forward** | solid blue, thin | the *supervised* reference/fallback (the "other paradigm" line — blue = supervised, as Phase 2) |
| **GD-hidden envelope** | flat-high reference (Phase-2 style) | the ceiling depth must climb toward |
| **random-projection floor** | thin grey | the **selectivity floor** (kept permanently — the control that *saved* Phase 2) |

**Headroom is still a precondition, not a result:** a depth curve is only interpretable if the GD-hidden ceiling
sits measurably above the energy wall (state the envelope gap in the caption — for CIFAR-flat it is +0.187, from
P2). **Substrate-feasible lines bold, supervised/reference lines thin** — we choose what survives on the chip.

---

## Layer B — the metric dictionary (PINNED — Phase-3 additions in **bold**)

The linear probe stays the **primary, ground-truth** metric (task-relevant information); everything else is
*diagnostic* (it explains *why* the probe moved). Carry every Phase-2 metric (Fisher, NCC, CKA, effective rank,
drift, continual ACC/BWT/forgetting, backward cost) unchanged. New for Phase 3:

| Metric | Definition (pinned) | What it answers |
| --- | --- | --- |
| **Linear probe** (PRIMARY) | logistic, fixed L2 `C=1.0`, frozen 2k/2k split, to convergence — **per layer** | is this layer class-usable? non-declining-with-depth = the win |
| **Depth-slope** | linear-fit slope of probe vs layer index; **+ve = depth helps** | the one-number headline (carried from P2) |
| **Peak-layer / peak-probe** | `argmax_l probe_l` and its value | *where* the representation is best, and how good |
| **Center of mass (CoM)** | `Σ_l (l · probe_l) / Σ_l probe_l` | where representational strength concentrates along depth; CoM moving *deeper* across objectives = depth is being *used* |
| **Decline area** | `Σ_{l>peak}(probe_peak − probe_l)`, normalized by depth | cumulative post-peak degradation; **0 = monotone non-declining (ideal)** |
| **Tail retention** | `mean(probe of last ⌈L/4⌉ layers) / probe_peak` | ~1 = deep layers still pull their weight; ≪1 = deep layers wasted |
| **N_eff** (effective participation) | `exp(H(α))`, `α` = normalized fusion/readout weights over layers | how many layers actually contribute to the fused readout (depth used, not one lucky layer) |
| **Info-preservation curve** (the new causal read) | per-layer **reconstruction error** of the masked objective `‖D_l ĥ_l − a_masked‖²` (contrastive control: per-layer InfoNCE / alignment) vs depth | *does the representation keep its input's information as depth grows?* — the Phase-3 analog of P2's dead-unit % (explains *why* the probe held or fell) |

**The depth-*shape* family (slope · peak-layer · CoM · decline-area · tail-retention · N_eff) is mandatory on
every depth curve** — reported as a small **SCORECARD** beside F3⁺. This is the direct fix for "a single slope
hides *where* the curve bends" (the field reports these — BiCovG, ASGE, the SSL-probe literature; see Grounding).

---

## Layer C — figure catalog (declare which you emit; don't invent new ones)

Reuse Phase-1/2 codes where the figure is the same (continuity); new Phase-3 figures get descriptive names.

| Code | Figure | Axes / form | The question it answers |
| --- | --- | --- | --- |
| **F3⁺ DEPTH CURVE** *(headline)* | per-layer **probe vs layer index**, objectives overlaid (Layer-A encoding) + GD-hidden ceiling + energy-wall + random floor | **does separability stop declining / rise with depth?** the entire Phase-3 thesis in one plot |
| **SCORECARD** *(headline companion — always with F3⁺)* | small table/panel: slope · peak-layer · CoM · decline-area · tail-retention · N_eff, per objective, IQR per cell | the *shape* of the curve, not just its slope |
| **INFOPRESERVE** *(new — the mechanism)* | per-layer reconstruction error (or InfoNCE/alignment) vs depth, objectives overlaid | *why* the probe held or fell — is information preserved with depth? |
| **REPR** | CKA layer×layer + effective-rank vs depth + Fisher/NCC vs depth (small-multiple) | homogenization / collapse, quantified (carried) |
| **SELECT** (DECIDE-style) | probe on objective-features vs **random-projection** floor vs GD ceiling, bar + per-depth | is the gain *real* (selectivity > 0) or a probe artifact? (the control that saved P2) |
| **F7 BACKWARD** | measured backward FLOPs / credit-distance, objective vs Mono-Forward vs full-GD | the substrate cost claim (carried) |
| **CONT (veto)** | **ACC + BWT** bars, fix-in vs fix-out vs Phase-1 baseline | does the new objective **re-earn** the continual win? (non-negotiable) |
| **INV** | loss/objective-slope · dead-unit % · effective-rank floor · **reconstruction-error floor** | health at a glance (carried + the new objective's floor) |
| **SUBSTRATE table** | lever → {Scaps, registers, wires, online-feasible?, continual-safe?} | what survives on the chip (carried) |

**Worked caption for F3⁺ (the hero figure) — the model voice, so handed-off runs don't drift it.** Every F3⁺
caption ends with the one-sentence verdict + the shape numbers + `(n=5, task, the move)`, and **never states a
number without its reference** (the GD-hidden ceiling + the energy-wall baseline + the envelope gap). Example:

> *"Masked-feature reconstruction turns SCFF's depth curve from declining to flat (slope −0.020→+0.002/layer,
> decline-area 0.41→0.06, tail-retention 0.55→0.94) — information-preservation stops the wall where
> energy-goodness couldn't, unsupervised. (n=5, CIFAR-flat, env. gap +0.187, energy-wall→masked-recon.)"*

**Ablation tables** (carried): one variable per row, delta vs the energy-wall baseline, **IQR in every cell**,
never a bare mean. **The comparable scalars per run**: **AAA** (area under the held-out/probe curve) + **final
probe median ± IQR** + **depth-slope** + (new) the **decline-area** — the four-number fingerprint of a depth run.

---

## Layer D — the summary template (six slots + the two carried Phase-2/3 slots)

Port the six-slot *Read* (claim → number+IQR → figures → mechanism → threats → decision). For Phase 3, **slot 4
(mechanism) must reference the INFOPRESERVE read** — "the probe held because information was preserved
(reconstruction error flat with depth)" / "fell because it wasn't." Keep both mandatory back slots:

7. **Substrate-feasibility** — does the *online / single-sample* version keep the benefit, at what cost (Scaps /
   registers / wires)? Masked-reconstruction is single-sample by construction; the per-layer decoder `D_l` is
   the only added area — price it. "Works with a batch / negatives bank" is **not** a Phase-3 pass for a cell
   that claims single-sample.
8. **Continual-preservation (the veto)** — ACC + BWT, fix-in vs fix-out. **The new objective does NOT inherit
   the Phase-1 win — it must re-earn it.** A cell that lifts static depth but worsens BWT is rejected. State it
   every time.

No slot may be empty; a failed objective still fills all eight (slot 4 → "leading hypothesis for why it failed"),
and we do **not** tune-to-pass (methodology rule #5).

---

## Mandatory-per-experiment map (the floor)

| Experiment | Must emit |
| --- | --- |
| **P3.0** objective swap *(headline / make-or-break)* | **F3⁺ + SCORECARD** (objectives overlaid), **INFOPRESERVE**, **SELECT** (vs random floor), REPR, INV, **light CONT sniff** |
| **P3.1** coordination (OLU / direct-feedback) | **F3⁺ + SCORECARD** (base vs +OLU vs +DF), INFOPRESERVE, ablation table, INV |
| **P3.2** Mono-Forward fallback | **F3⁺ + SCORECARD** (Mono-Forward vs energy-wall vs GD), **F7 BACKWARD** (cost Pareto), INV |
| **P3.3** substrate + continual veto *(deliverable)* | **SUBSTRATE table**, **CONT-veto (ACC+BWT)**, DRIFT, INFOPRESERVE-stability (does preservation hold under task shift?) |

---

## Grounding (what the field actually does — and what we adopt)

- **Depth as a per-layer probe curve, non-declining = good:** Alain & Bengio ([1610.01644](https://arxiv.org/abs/1610.01644)); FF-depth as Fig-1 of the Trifecta / DeeperForward / ASGE. → **F3⁺**.
- **Depth-*shape* metrics (not just slope):** **decline-area, tail-retention, shallow/deep gain, N_eff** — BiCovG ([2605.04346](https://arxiv.org/abs/2605.04346)); **peak-accuracy, peak-depth, center-of-mass** — the SSL-probe evaluation literature; **Last/Fusion/Best-Pred** readouts — ASGE ([2509.12394](https://arxiv.org/abs/2509.12394)). → **SCORECARD**.
- **Info-preservation as the depth mechanism:** Greedy InfoMax ([1905.11786](https://arxiv.org/abs/1905.11786)) — "each module maximally preserves the information of its inputs"; greedy layer-wise denoising-AE pretraining (Hinton 2006 / Bengio 2007). → **INFOPRESERVE** + the masked-reconstruction objective itself.
- **Selectivity control (probe honesty):** Hewitt & Liang 2019 (a strong probe can solve the task itself) — the random-projection floor. → **SELECT**.
- **Continual reporting = ACC + BWT:** Lopez-Paz GEM. → **CONT-veto**.
- **Ablation discipline, IQR, n=5 honesty, reproducibility:** ported from Phase 1/2.

> This is the **floor**. Adapt upward per experiment; never drop below it. When a real result needs a figure not
> in the catalog, **add it to the catalog** (so the next run inherits it) rather than drawing a one-off — that is
> exactly the drift this file exists to prevent.
