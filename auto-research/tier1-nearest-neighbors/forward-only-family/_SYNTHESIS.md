# Synthesis — Forward-only / backprop-free deep learning: the family  (Tier 1)
**The question:** Who else trains deep nets forward-only without backprop, and *exactly* how is our object different? Place us precisely in this family.

**Already in `draft6.0/research/`:** SCFF (`survey/SCFF.detail.md`, `papers/phase1-2/scff.md`), DeeperForward, Distance-Forward, Mono-Forward, and the `papers/phase3/direction-3-forward-only-alternatives.md` fork (GIM/CLAPP vs Mono-Forward). This sweep does **not** re-summarize those — it goes broader/newer (2023–2026) and adds the *paradigm boundaries* (PEPITA, SigProp), the *negative-free* branch (CaFo), the *predictive* branch (PFF), the *goodness-repair* branch (SymBa), the *scaling SOTA* (ASGE→ImageNet), and the two *engineering-native critiques* (energy audit; synthetic-vs-real).

## The landscape (the camps)
The "train every layer with a local forward objective, no backward pass" field splits into four mechanistically distinct camps:

1. **Contrastive / goodness (two worlds per layer).** FF (Hinton 2022) is the root: positive vs negative passes, `Σh²` goodness, label-derived negatives. Descendants repair or relabel the contrast — **SCFF** (label-free self-contrast), **SymBa** (symmetric goodness-gap loss + class patterns), **DeeperForward** (keep the norm, fix the goodness), **ASGE** (spatial goodness, scales to ImageNet). All still measure a *magnitude* (energy/goodness) unless, like us, they swap in an info-preserving objective.

2. **Modulated / global-signal-forward (carry the error or target forward).** **PEPITA** (a second forward pass on error-perturbed input) and **SigProp** (carry the target as a parallel forward stream) keep backprop's *global supervised* signal but deliver it without a backward pass, via fixed random projections (Feedback-Alignment lineage). Forward-only, but **fully supervised** — the opposite of label-free.

3. **Negative-free / per-block supervised (predict labels locally).** **CaFo** drops negatives entirely: each block has a small predictor that outputs a label distribution, trained independently. Cheapest of all, but supervised at every block and with no representation objective.

4. **Predictive-coding / generative.** **PFF** learns a generative circuit jointly with a representation circuit, wired by predictive coding — the road toward reconstruction-style objectives.

Cutting across all four are two **engineering-native critiques** we should hold close: Spyra & Dzwinel's **energy audit** (forward-only ≠ energy-efficient by default — the backward-pass saving is paid back elsewhere) and Chen's **synthetic-benchmarks-overstate-scaling** (FF-family gains on curated tasks shrink on real data).

## How WE differ  ← the money section
Our object is a **specific, unusual point** in this space, and the honest placement is:

- **Objective:** we are camp-1 by *lineage* (FF/SCFF frame, the name) but camp-1-**heretic** by *mechanism* — we threw out energy-goodness (`Σh²` measures density, not class; Phase 2 proved no repair encodes a direction) and run **InfoNCE contrast** (GIM/CLAPP-family, made flat-vector via two masked views). SymBa/DeeperForward/ASGE *repair* goodness; we *replace* it. That is the single sharpest line: **everyone else in the goodness camp optimizes a magnitude; we optimize a direction.**
- **Label-freedom:** unlike PEPITA, SigProp, CaFo, ASGE (all supervised), our **bulk never sees a label or an error signal.** Label-freedom is a deliberate constraint for *continual-safety*, not a byproduct of being forward-only — a distinction this landscape makes crisp (forward-only ⊄ label-free).
- **Frozen-bulk + separate closed-form namer:** **no one else in this family has this split.** Every method above is a single end-to-end (if local) learner that classifies. We train an unsupervised bulk, **freeze it**, and read it once with a **gradient-free closed-form head (SLDA/RanPAC)**. CaFo's per-block predictors are the nearest structural cousin, but they are supervised and co-trained, not reading a frozen unsupervised substrate.
- **Substrate primitive:** our **sum-form mono-forward dual-rail** (positive + negative carried side-by-side through *one shared weight crossbar*, only activation buffers double) is a hardware realization; SigProp's "two streams on one forward path" is the closest abstract precedent, but for target-vs-input, not two label-free views.
- **What we win / concede:** we win **off the static-accuracy axis** — continual, noise-robust, on-chip, drift-gated. ASGE shows the family *can* win static accuracy (ImageNet) with convolution + labels; we concede that axis by design. Spyra & Dzwinel show forward-only doesn't save energy digitally — we agree (our own Phase-10 R1) and pin our energy win to the **analog substrate**, not forward-only-ness. Chen shows synthetic benchmarks overstate — we agree and answer with the Phase-11 real-data limit map.

**One-line placement:** *We are the label-free, direction-optimizing (InfoNCE), frozen-bulk-plus-closed-form-namer member of the forward-only family — a combination no other paper here holds at once — validated for continual/noise/on-chip rather than static accuracy.*

## The gap / what we haven't tried
- **Negative-free forward training (CaFo).** Our biggest open hardware-bridge risk is the negative supply: InfoNCE needs negatives, and streaming them from a bounded LUT plus a non-charge-native softmax block is an unbuilt Stage-2 gate (§2.4). CaFo trains forward-only with **zero negatives** by predicting labels per block. A CaFo-style distributed closed-form namer could sidestep the entire negative-gathering + softmax cost. **This is the single biggest untried lever.**
- **Modulated-second-pass (PEPITA) as a forward-only namer-injection** into the top SCFF layers — a way to add a whisper of label-direction on-substrate without a backward pass. Untested.
- **Flat-vector predictive objective (PFF-adjacent).** §2.2 explicitly leaves open whether a *predictive* (cross-layer, fresh-target) objective avoids the same-target depth-decay our masked-view contrast incurs. PFF is the prior art.
- **Matched-accuracy energy protocol (Spyra & Dzwinel).** Meter cost to a target accuracy, not per-step — a sharper Stage-2 cost meter than our op-count proxy.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Hinton 2022 — Forward-Forward](hinton-2022-forward-forward.md) | ⭐⭐⭐⭐⭐ | The family root; the energy-goodness dead-end we replaced. |
| [Dellaferrera & Kreiman 2022 — PEPITA](dellaferrera-2022-pepita.md) | ⭐⭐⭐⭐ | Forward-only ≠ label-free (a supervised second-pass paradigm). |
| [Kohan 2022 — SigProp](kohan-2022-sigprop.md) | ⭐⭐⭐ | Two streams on one forward path — the dual-rail precedent. |
| [Zhao 2023 — Cascaded Forward (CaFo)](zhao-2023-cascaded-forward.md) | ⭐⭐⭐⭐ | Negative-free per-block training — sidesteps our LUT-negatives risk. |
| [Ororbia & Mali 2023 — Predictive FF](ororbia-2023-predictive-forward-forward.md) | ⭐⭐⭐ | The predictive/generative road we didn't take (reconstruction failed for us). |
| [Lee & Song 2023 — SymBa](lee-2023-symba.md) | ⭐⭐⭐ | Repairs goodness; the citation for *why repairing wasn't enough*. |
| [Gong 2025 — ASGE](gong-2025-adaptive-spatial-goodness.md) | ⭐⭐⭐⭐ | FF-family scaling SOTA (ImageNet) — the static-accuracy ceiling we live below. |
| [Spyra & Dzwinel 2025 — Energy audit](spyra-2025-energy-efficient-forward-only-eval.md) | ⭐⭐⭐⭐⭐ | Forward-only ≠ energy-efficient — pins our win to the analog substrate. |
| [Chen 2026 — Synthetic overstates scaling](chen-2026-synthetic-benchmarks-overstate-ff.md) | ⭐⭐⭐⭐ | External validation that we needed the Phase-11 real-data map. |

## Leads spawned
- Negative-free / goodness-free forward training (CaFo, Forward-Only CNNs with learnable channel-class assignment) — could reshape the namer.
- Feedback Alignment / Direct Feedback Alignment family (the random-fixed-matrix credit route behind PEPITA/SigProp).
- Predictive coding as forward-only credit assignment (Millidge / Salvatori / Ororbia) — the flat-vector predictive objective test.
- Matched-accuracy energy benchmarking for local learners (Spyra & Dzwinel protocol).
- Cumulative-goodness free-riding & goodness-function critiques (arXiv 2605.06240, ⚠ unverified) — goodness-camp failure modes.
- FF on spiking / neuromorphic substrates (FFGAF-SNN, backprop-free SNNs) — the hardware-native branch.
