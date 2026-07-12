# Tier 4 — Adjacent wildcards: the rollup

> Machine-swept 2026-07-11 (Fable 5 + Opus subagents). Five out-of-ladder-but-high-leverage fields, read as one map:
> **does the hardware/physics reality validate or threaten the "math model of a chip," and where does the horizon
> become more analog-native than expected?** ~42 verified cards. **Provenance: automation — ratify before citing.**

Topics: [analog in-memory compute](analog-in-memory-compute/_SYNTHESIS.md) · [equilibrium / physics learning](equilibrium-physics-learning/_SYNTHESIS.md) · [neuromorphic / spiking](neuromorphic-spiking/_SYNTHESIS.md) · [state-space & liquid atoms](state-space-liquid-atoms/_SYNTHESIS.md) · [energy-benchmarking protocol](energy-benchmarking-protocol/_SYNTHESIS.md)

---

## The meta-finding: the substrate's physics keeps *being* the math

The single deepest through-line of Tier 4 — the project's founding conceit is confirmed from five independent hardware/physics literatures:

- the **Scap = the field's best-in-class update device** (record symmetry, unlimited endurance) *(t4.1)*;
- a **memristor's short-term-memory decay natively IS the SSM `A` matrix** — the temporal atom, in silicon *(t4.4)*;
- a **Liquid-Time-Constant neuron IS an RC element with a learnable τ** *(t4.4)*;
- **content-addressable recall IS a physical matchline / attractor settle** (analog CAM, memristor-Hopfield) *(t4.1, t3.1)*;
- **EqProp's learning signal IS local physics at equilibrium** — and *two-state differencing self-cancels device error* *(t4.2)*;
- the **eligibility trace IS a leaky capacitor** *(t4.3)*.

"The substrate's physics is the math" is no longer a slogan — Tier 4 is the receipts.

## The validated / challenged / competitor ledger

| | What Tier 4 says |
| --- | --- |
| **VALIDATED** | Scap update device (t4.1) · P8 5.4× meter is *conservative* vs silicon 172–280× (t4.1) · Ambrogio fast-cap/slow-NVM = our awake/sleep economy *in device form* (t4.1) · matched-accuracy R1 honesty = the correct protocol (t4.5) · the memory-wall = the mechanism behind P11's growing substrate factor (t4.5) |
| **CHALLENGED** | **On-array *update* is where analog learning dies** — Tiki-Taka's implicit-cost result applies to SCFF too; unmeasured (t4.1). IR drop pressures the width-extrapolation (t4.1). Frozen-recurrence-vs-BPTT accuracy gap for SSM atoms is untested (t4.4). |
| **COMPETITORS to cite** | **CLP-SNN on Loihi 2** (rehearsal-free continual on-chip, our exact pitch) (t4.3) · STELLAR / HERMES memristor training chips (t4.1) · IMSSA memristor SSM (t4.4) |
| **COMPLEMENTS (deferred merges)** | EqProp = the recurrent loop's learning rule (t4.2) · e-prop three-factor rule (not spikes) = the loop's temporal rule (t4.3) · frozen HiPPO-SSM reservoir = the loop's atom (t4.4) |

## The experiments Tier 4 surfaced (realism + horizon)

1. **SCFF under analog update non-ideality** (AIHWKIT harness) — the flagship realism experiment *and a potentially publishable gap*: does SCFF self-correct or compound under asymmetric/granular updates? *(t4.1)*
2. **Does SCFF's contrastive-pair difference self-cancel systematic Scap error?** — EqProp's two-state differencing says it might; a direct probe at experiment #1 *(t4.2)*.
3. **Frozen-SSM-reservoir + closed-form namer on the P11 real streams** — is analog-native frozen recurrence "good enough" vs BPTT? *(t4.4)*
4. **A "SCFF-in-time" rung** — one eligibility register/weight + a broadcast signal on a minimal recurrent bulk *(t4.3)*.

## The recurring open thread (ties to the Tier-3 flagship problem)

Every temporal/recurrent complement here (EqProp loop, SSM decay, delta-gates, e-prop) is **BPTT- or gradient-trained** in its published form. The project's real frontier is a **gradient-free / closed-form learning rule for the recurrent parts** — the same open problem Tier 3 named for routing. Solve it once and both the recurrence and the coordinator become substrate-native.

## Must-know anchors (Tier 4)

Gokmen-Vlasov RPU 2016 + Ambrogio 2018 + Rasch c-TTv2 2024 (analog update) · Scellier EP-benchmark 2023 + Laborieux holomorphic-EP 2022 (physics learning) · Bellec e-prop 2020 + CLP-SNN/Loihi-2 2025 (spiking) · Hasani CfC 2022 + IMSSA 2024 (SSM atoms) · Dehghani Efficiency-Misnomer 2022 + Horowitz 2014 + Gholami memory-wall 2024 (energy).

*(Full table with links + per-paper "relation to us": [`../INDEX.md`](../INDEX.md).)*
