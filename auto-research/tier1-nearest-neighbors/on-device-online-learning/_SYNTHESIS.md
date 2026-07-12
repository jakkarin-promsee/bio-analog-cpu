# Synthesis — On-chip / on-device online (continual) learning systems  (Tier 1)
**The question:** Who else builds a system that *learns online on the substrate under a budget*, and exactly how is our object — frozen-envelope forward-only bulk + bounded closed-form namer, drift-gated, sleep-consolidated, with a substrate energy account — different?
**Already in `draft6.0/research/`:** the phase-8 gate mechanics (DDM/ADWIN drift detectors, Skip-RNN, DNI — `research/papers/phase8/`); the namer family itself (SLDA/RanPAC/ACIL line — INDEX t1.2); the forward-only family (t1.1). This topic adds the **system level**: who runs the whole learn-online-under-budget loop, and on what accounting.

## The landscape (the four camps)

**1. Latent-replay-on-device (the lineage our LUT lives in).** Pellegrini et al. 2020 set the shape: store the past as *mid-network activations*, freeze (or nearly freeze) the layers below the tap, backprop only above it. Ravaglia et al. 2021 built it into silicon — 8-bit quantization of the frozen front *and* the replay buffer (near-lossless), measured 37× energy over an MCU — and the follow-ons (Chameleon, Miro) turned the buffer into a memory-hierarchy engineering object. This camp's constant: the representation is frozen to keep the stored past valid; drift of the *backbone itself* is suppressed, never tracked.

**2. Budgeted gradient engineering (make backprop fit).** Lin et al. 2022 train CNNs inside 256KB by refusing to compute most of the backward pass (sparse update), training in int8 (quantization-aware scaling), and compiling the autodiff. TinyTrain, PockEngine continue the line. The lesson: gradient learning *is* feasible under extreme budgets — the argument "backprop can't fit on-device" is dead; only "backprop shouldn't be the always-on path" survives.

**3. Budget-honest evaluation reform (the referees).** Prabhu et al. 2023: equalize training compute and *no CL method beats uniform-replay fine-tuning*. Ghunaim et al. 2023: let the stream refuse to wait and slow-but-clever loses to fast-and-simple, endogenously. Seo et al. 2025: count *total* FLOPs+bytes (no hiding cost in teachers/copies) and spend the budget only on informative batches (adaptive layer freezing — a per-batch learning gate). This camp defines how our claims will be judged by ML reviewers.

**4. Learning as a scheduled, gated system service.** SIESTA (wake/sleep: backprop-free online updates awake, compute-restricted rehearsal asleep) is our nearest algorithmic twin. At systems scale, Ekya/RECL treat retraining-under-drift as a resource-allocation problem with a **micro-profiler estimating the value of learning before paying for it**, and Miro adapts the CL system's own knobs online against an accuracy-per-joule objective. Hayes & Kanan 2022 supply the embedded criteria and independently land on our head family (NCM/SLDA) as the budget-optimal namers.

## How WE differ  ← the money section

Every load-bearing *component* of our economy exists in this literature, mostly biology-free: wake/sleep with a gradient-free wake path (SIESTA), latent memory instead of raw replay (Pellegrini), closed-form streaming heads as the budget optimum (Hayes & Kanan), drift-triggered paid learning (Ekya, + our own DDM lineage), energy as the objective (Miro, Ravaglia). What is genuinely ours is the **composition and two specific claims nobody here makes**:

1. **The always-plastic unsupervised bulk.** Every system above freezes the representation to protect its stored past; their drift is *external* (data drift). Our SCFF bulk keeps learning forever, so the namer must track *internally generated* representation drift — a problem this literature avoids by construction (and P11's Δbulk shows the plasticity pays on nonlinear arenas). This is our sharpest novelty at the system level.
2. **The gate as a safety mechanism.** On-device CL treats update frequency as a pure cost knob — fire as often as the budget allows. Our P8.6 inversion (*firing more forgets more*; always-pay −0.137 vs gated 0.000 worst-BWT) has no counterpart in this set; the closest ideas (Ekya's deferral, Seo's freezing) skip learning to save compute, not to protect memory.
3. **The substrate-decomposed energy account.** Miro/Ravaglia measure device joules; Seo counts FLOPs+bytes; nobody separates *algorithm* from *substrate* (our 15.4× = 5.4× CIM × 2.9× algorithm, with the 80/20 shown substrate-independent). Conversely — SIESTA and camp 3 prove the efficiency of the wake/sleep + closed-form composition on plain GPUs, so our energy claim must always be pinned to the analog meter, never to the loop shape alone.

Honest placement: as an *on-device CL system* our object is a member of camp 4 with a camp-1 memory; as a *measurement* (metered substrate energy under drift-gated online learning) it is alone. And camp 3 has already published our own P10 caveat: under matched budget, small tuned replay is the accuracy frontier — our wins live off that axis (safety, noise, order-invariance, substrate floor), and Prabhu/Ghunaim are the citations to frame that against.

## The gap / what we haven't tried

- **Real-time (stream-doesn't-wait) evaluation** — Ghunaim's clock. We meter energy but never charged *time*: the stream pauses during our sleep. With fire-fraction ≈0.003 we are plausibly near delay-free while per-step ER drowns — likely an unbanked WIN, and it closes the one axis where our evaluation is softer than the 2023+ standard.
- **Benefit-aware gate (Ekya's micro-profiler, closed-form).** Our DDM gate detects *that* error drifted; a prototype-shift-vs-margin forecast from the LUT could estimate *whether firing pays*, skipping low-value fires — GD-share below 0.121 with a principled rule, no micro-training needed.
- **Quantize the LUT** (Ravaglia): 8-bit latent storage was near-lossless; the required bit-width of our prototypes/Gram is unmeasured and maps directly onto analog storage precision (Scap resolution) and the P8.7 meter.
- **Runtime knob adaptation (Miro):** our cadence is drift-rate-conditional by admission (P8 honest scope) but frozen; a tiny profiler adapting grid-4/8/16 to the measured drift rate would make the conditionality self-managing.
- **Report FLOPs+bytes alongside pJ** (Seo): one table in their currency makes us placeable by the budgeted-CL community without trusting the analog model.
- **Sleep-side sampling policy:** cbrs balances classes; frequency/seen-count-weighted consolidation (Seo; SIESTA's GRASP) is a cheap untested import for the sleep re-fit.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [SIESTA (Harun et al. 2023)](harun-2023-siesta.md) | ⭐⭐⭐⭐⭐ | Our wake/sleep economy exists on GPU — the nearest twin, and the proof our energy claim needs the substrate, not the loop shape. |
| [Online CL for Embedded Devices (Hayes & Kanan 2022)](hayes-2022-embedded-ocl.md) | ⭐⭐⭐⭐⭐ | The embedded criteria + our namer family (SLDA/NCM) benchmarked as the budget optimum — engineering-native validation of P7. |
| [Latent Replay (Pellegrini et al. 2020)](pellegrini-2020-latent-replay.md) | ⭐⭐⭐⭐ | The store-representations-not-inputs anchor; names the staleness ("aging") problem our gate+sleep tracks instead of suppressing. |
| [Quantized Latent Replays on VEGA (Ravaglia et al. 2021)](ravaglia-2021-tinyml-quantized-latent-replay.md) | ⭐⭐⭐⭐ | Measured-on-silicon energy for the same anatomy; 8-bit memory near-lossless → quantize our LUT. |
| [On-Device Training Under 256KB (Lin et al. 2022)](lin-2022-ondevice-256kb.md) | ⭐⭐⭐⭐ | The strongest budgeted-backprop rival; sparse update = "pay for direction only where it counts." |
| [Budgeted CL (Prabhu et al. 2023)](prabhu-2023-budgeted-cl.md) | ⭐⭐⭐⭐ | Under matched compute nothing beats uniform replay — the published frame for our P10 Pareto result and baseline choice. |
| [Real-Time Evaluation in OCL (Ghunaim et al. 2023)](ghunaim-2023-realtime-ocl.md) | ⭐⭐⭐⭐ | The stream-doesn't-wait clock — the evaluation we haven't run and would likely win. |
| [Miro (Ma et al. 2023)](ma-2023-miro.md) | ⭐⭐⭐⭐ | Accuracy-per-joule as the explicit objective + online adaptation of the CL system's own knobs. |
| [Budgeted OCL, Layer Freezing (Seo et al. 2025)](seo-2025-budgeted-ocl-layer-freezing.md) | ⭐⭐⭐⭐ | Total FLOPs+bytes accounting + a per-batch informativeness gate — the 2025 budget standard to report against. |
| [Ekya (Bhardwaj et al. 2022)](bhardwaj-2022-ekya.md) | ⭐⭐⭐ | The benefit-estimating micro-profiler — a value-of-learning forecast in front of the gate. |

## Leads spawned
- **Real-time/delay-aware evaluation of the frozen object** (Ghunaim protocol + prequential verification latency) — the highest-value follow-on experiment.
- **RECL / model-zoo reuse** (NSDI 2023) — "a hippocampus of whole models": reuse vs relearn as a gate alternative.
- **Chameleon (TCAD 2024) + DaCapo (2024)** — replay buffers and CL mapped onto real memory hierarchies / accelerators.
- **CLEAR benchmark** — natural temporal drift stream; a candidate arena beyond P11's eight.
- **GRASP rehearsal policy (Harun et al. 2023)** — budgeted consolidation-sampling for our sleep.
- **Stability gap (Harun & Kanan)** — transient forgetting right after updates; directly relevant to our worst-point (pre-sleep) BWT metric.
