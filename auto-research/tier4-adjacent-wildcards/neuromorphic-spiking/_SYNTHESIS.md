# Synthesis — Neuromorphic / spiking online learning  (Tier 4, t4.3)
**The question:** Is spiking / e-prop a **complement** to our substrate (the temporal/real-time learning atom for the north-star loop), a **distraction**, or a **merge-target**? Does going event-driven/spiking buy a *continual, on-chip* learner anything, or is it orthogonal?

**Already in `draft6.0/research/`:** `north-star/10-realtime.md` curates the realtime family (RTRL → e-prop → reservoir → liquid nets → SNN hardware → Mamba) and already states the key hook — *eligibility trace = a leaky cap you already have; e-prop = local trace × broadcast signal = our SCFF-bulk + namer-correction with a time axis*. This card set **extends** that with the 2022–2025 online-spiking rules the dossier predates (OTTT, SLTT, OSTL, S-TLLR, ETLP) and the on-silicon continual result (CLP-SNN on Loihi 2), and turns the hook into an honest verdict.

## The landscape (the field, engineering-read)
Read for circuits/online-rules value (not neuroscience), the field splits into three camps:

1. **The factorization theory (the anchors).** *Three-factor rules* (Frémaux & Gerstner 2016) and *e-prop* (Bellec 2020) establish the one idea that matters here: the exact through-time gradient factorizes into a **local, forward eligibility trace** × a **top-down/broadcast learning signal**. The eligibility trace is a per-synapse leaky accumulator — an exponentially-decaying register. This is the substrate-native temporal-credit primitive: no backward pass, no stored history, O(#synapses) memory. e-prop reaches near-BPTT on TIMIT/Atari-online; it is *the* neuromorphic on-chip learning rule.

2. **Online surrogate-gradient training (make BPTT cheap & forward).** OTTT (Xiao 2022), SLTT (Meng 2023), OSTL (Bohnstingl 2022) are the engineering workhorses: keep the surrogate gradient but compute it **online with constant memory in the number of time steps**, via forward pre-activity traces. OSTL proves the spatial/temporal split is BPTT-equivalent (shallow) and unit-agnostic (SNN/LSTM/GRU). SLTT drops a bombshell useful to us: *temporal backprop contributes little* — you can prune most of it and still hit ImageNet SOTA (−70% memory). These are all still **gradient descent**, just streamlined.

3. **Local rules → hardware (drop the gradient).** S-TLLR (Apolinario 2025, TMLR) is a causal+non-causal local three-factor rule, time-step-independent, tested to optical-flow on edge budgets. ETLP (Quintana 2024) is the outlier that matters most for us: its third factor is a **random-projected label with no error at all** (spiking Direct-Feedback-Alignment). CLP-SNN (Hajizada 2025, Intel) is the whole-system endpoint: **rehearsal-free continual learning on Loihi 2** via a self-normalizing three-factor rule + neurogenesis + metaplasticity, tying replay at 6,600× lower energy than an edge GPU.

## How WE differ  ← the money section
Our object is **rate-based, feed-forward, i.i.d. sample-at-a-time**, with an **unsupervised SCFF bulk** and a **closed-form namer** (no gradient). Two honest facts fall out:

- **Structurally, we are already a three-factor / e-prop-shaped machine — spatially.** SCFF's local contrastive signal is the pre×post factor; our **DDM drift gate on the namer's error-EMA** is the broadcast third factor (it decides *when* learning fires); and we *already own the eligibility trace* — it's the leaky-capacitor / EMA register (error-EMA, momentum). The hook in `10-realtime.md` is real and confirmed by five more papers: the trace is our cheapest primitive.

- **But we are missing the one thing this whole field is about: a time axis.** e-prop/OTTT/SLTT/OSTL/S-TLLR all solve **temporal credit assignment across time steps in a recurrent/spiking net**. Our current object has *no time axis for a trace to integrate* — each sample is processed once. So for **the current P1–11 object, spiking/e-prop buys nothing**: no recurrence, no spikes, and our namer is *closed-form* (cheaper and more stable than any online gradient rule). Worse, camp #2 (OTTT/SLTT/OSTL/S-TLLR) proposes the *opposite* of our thesis: they *keep the gradient* and make it online; P7 says the namer needs *no* gradient. Adopting them would be trading our differentiator away.

**The verdict — COMPLEMENT, with a deferred, specific merge-target; a distraction if pulled in now.**
- **For the current feed-forward continual object → distraction.** Going event-driven/spiking adds a time axis we don't have and re-introduces a gradient we deliberately dropped. The *only* thing to steal now is the **event-driven principle** ("a unit costs nothing until active") — and that is already our **sparsity** property. No new experiment justified.
- **For the north-star recurrent temporal loop → merge-target, and a precise one.** When the loop has temporal structure, **e-prop / three-factor is the canonical learning rule and we already own its hardware primitive (the leaky cap).** The merge is not "adopt spiking"; it's "adopt the eligibility-trace × broadcast-signal *rule* on our rate-based recurrent loop" — which OSTL proves is legitimate without spikes.
- **Two neighbors to watch, not merge yet:** **ETLP** (no-error, random-projected-label third factor) is the temporal analogue of our closed-form namer — the drop-in if the loop ever needs an *online* namer that keeps our no-gradient bet. **CLP-SNN on Loihi 2** is the published on-silicon competitor occupying our exact pitch (rehearsal-free continual on-chip); its **neurogenesis + metaplasticity** is direct fuel for the queued **hippocampus-organ** build, and its algorithm×substrate energy split mirrors our P8.7.

## The gap / what we haven't tried
1. **We have never given the object a time axis.** The single concrete lever: a **"SCFF-in-time" sim rung** — one eligibility register per weight (the leaky cap we already model) + a broadcast learning signal, on a minimal recurrent version of the bulk, to see if temporal structure can be learned forward-only. This is the north-star loop's first testable atom.
2. **Run SLTT's diagnostic before building the loop.** SLTT shows temporal-backprop often barely matters. Measure, on our target streams, how much a temporal-credit term would change the update — if "little", the loop can stay cheap (feed-forward + gate) instead of truly recurrent-trained. A way to *avoid over-building*.
3. **ETLP-style online namer.** Replace the batched closed-form re-fit with a random-projected-label three-factor trace update and check whether it holds our BWT/safety — keeps the no-gradient thesis while going per-step/online.
4. **Neurogenesis for the hippocampus organ.** CLP-SNN's "recruit fresh capacity for novel inputs" is the exact mechanism the LUT-becomes-an-organ step needs.

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Bellec 2020 — e-prop](bellec-2020-eprop.md) | ⭐⭐⭐⭐⭐ | The anchor: gradient = local forward trace × broadcast signal = our architecture + a time axis; trace = leaky cap. |
| [Frémaux & Gerstner 2016 — Three-factor rules](fremaux-gerstner-2016-three-factor.md) | ⭐⭐⭐⭐ | Names the family `Δw=f(pre,post,modulator)`; our gate is the third factor; mean-subtraction + sign-reversal requirements. |
| [Xiao 2022 — OTTT](xiao-2022-ottt.md) | ⭐⭐⭐⭐ | Online surrogate gradient at constant memory; three-factor Hebbian form — the "keep gradient, make it online" camp we route around. |
| [Meng 2023 — SLTT](meng-2023-sltt.md) | ⭐⭐⭐ | Empirical: temporal backprop barely matters (−70% mem) → don't over-build the temporal loop. |
| [Bohnstingl 2022 — OSTL](bohnstingl-2022-ostl.md) | ⭐⭐⭐ | Spatial/temporal split is BPTT-equivalent & unit-agnostic → the leaky-cap trace is legit for a *rate-based* loop, no spikes needed. |
| [Apolinario 2025 — S-TLLR](apolinario-2025-s-tllr.md) | ⭐⭐⭐⭐ | Local three-factor, time-step-independent, scales to optical flow on edge — the "cheap online temporal learning is solved" neighbor. |
| [Quintana 2024 — ETLP](quintana-2024-etlp.md) | ⭐⭐⭐⭐ | Third factor = random-projected label, **no error** — the spiking twin of our closed-form no-GD namer; the online-namer drop-in. |
| [Hajizada 2025 — CLP-SNN / Loihi 2](hajizada-2025-clp-snn-loihi2.md) | ⭐⭐⭐⭐⭐ | Rehearsal-free continual on-chip learning on silicon; neurogenesis+metaplasticity = fuel for the hippocampus organ; algorithm×substrate energy split = our P8.7. |

## Leads spawned
- **"SCFF-in-time": eligibility-trace learning on a rate-based recurrent bulk** — the north-star loop's first sim rung (uses the leaky cap we already have). *(high-leverage)*
- **RTRL & its modern approximations** (Zucchet & Orvieto 2023; Marschall/Cho/Savin 2020 unified RNN-online taxonomy) — the exact-gradient parent family; where e-prop/OSTL sit.
- **Direct Feedback Alignment / DRTP (Frenkel 2021)** — the non-spiking root of ETLP's no-error third factor; near-identical to our RanPAC intuition — worth a dedicated card.
- **Neurogenesis + metaplasticity for lifelong learners** (Kudithipudi 2022, Nature MI) — design vocabulary for the hippocampus-organ build.
- **NeuroTrain local-rule benchmark (arXiv 2605.15058)** — head-to-head ranking of e-prop/OTTT/S-TLLR; verify then cite.
- **Event-driven sparsity as an energy strategy** — formalize "a unit costs nothing until active" against our sparse property (ties to P8.7 substrate factor).
