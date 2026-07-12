# Tier 1 — Nearest neighbors: the rollup

> Machine-swept 2026-07-10 (Fable 5 subagents). Reads the **seven topic syntheses as one map**: where draft-6.0 sits
> in the prior art, what's genuinely ours, what's commodity, and the decidable experiments the comparison surfaced.
> ~63 verified paper cards across 7 topics. **Provenance: automation — ratify before citing.**

Topics: [forward-only family](forward-only-family/_SYNTHESIS.md) · [analytic continual learning](analytic-continual-learning/_SYNTHESIS.md) · [on-device online learning](on-device-online-learning/_SYNTHESIS.md) · [complementary dual-memory](complementary-dual-memory/_SYNTHESIS.md) · [frozen-backbone + cheap-head](frozen-backbone-cheap-head/_SYNTHESIS.md) · [feedback-alignment / DFA](feedback-alignment-dfa/_SYNTHESIS.md) · [SSL backbones for CL](ssl-backbones-for-cl/_SYNTHESIS.md)

---

## The five things Tier 1 established

1. **Our namer is commodity; our value is the bulk + the substrate.** *(t1.5)* A prototype / closed-form head on frozen features is now a solved, widely-published shape (Janson NCM, SimpleCIL, FSA, F-OAL). SLDA/RanPAC is *validated, not novel*. Pitch the forward-only self-grown bulk and the analog economy — not the head.

2. **Our core bet is SUPPORTED — the most-supported claim in the sweep.** *(t1.7)* A label-free, self-grown frozen representation is a good CL substrate: SSL backbones forget less and transfer OOD (LUMP, Cossu, Ostapenko), biggest at small data (Gallardo — nearly our exact machine: label-free backbone + closed-form streaming LDA). Our always-OOD stream is exactly where this wins.

3. **Our capability SHAPE is a family law, not a defect.** *(t1.6)* "Wins continual/noise, trails static-accuracy" is the published **locality tax** of every non-exact-gradient rule (Bartunov; Refinetti's conditioning theory) — and our flat-vector substrate sits on the *good* side of the conditioning line that kills DFA on conv. P4/P10/P11's shape is lawful.

4. **The energy win must pin to the ANALOG SUBSTRATE, never to forward-only-ness.** *(t1.1, t1.3, t1.6)* Forward-only ≠ energy-efficient (Spyra & Dzwinel); wake/sleep + gradient-free wake already runs on a GPU (SIESTA); DFA is already *built* on an analog crossbar at <1 pJ/MAC (Filipovich). The differentiator is compute-in-memory, not the loop shape.

5. **Two honest attribution risks are now named.** (a) Is the robustness the **objective structure** (InfoNCE-as-projector) rather than label-freeness? — Marczak 2024. (b) Our **P11 autocorrelated-stream floor is intrinsic** to stream-grown SSL, not a substrate bug — Purushwalkam / CaSSLe / POCON. Reframe the floor as a known field limit.

---

## What is uniquely ours (survives all ~63 papers)

**Forward-only ⊕ local ⊕ derivative-free ⊕ label-free bulk ⊕ grown one-pass ON the stream ⊕ no raw-data replay ⊕ closed-form consolidation ⊕ a drift-gated "when-NOT-to-update" economy ⊕ analog-substrate-bound.** No single paper combines these. The nearest twins each miss ≥3:

| Nearest twin | What it shares | What it misses |
| --- | --- | --- |
| **F-OAL** (t1.2) | forward-only + online + closed-form head | drift gate · sleep · substrate energy account |
| **SIESTA** (t1.3) | wake/sleep + gradient-free wake | GPU not analog · freezes the backbone |
| **DualNet** (t1.4) | unsupervised slow + supervised fast (our 80/20) | trains *both* memories by SGD |
| **FSA** (t1.5) | adapt-once body + exact LDA head | freezes after one adaptation (bets against always-plastic) |
| **Gallardo** (t1.7) | label-free backbone + streaming LDA | offline pretraining · backprop · not on-stream |

---

## The decidable experiments Tier 1 surfaced (for the author)

| # | Experiment | From | What it decides |
| - | ---------- | ---- | --------------- |
| **A** | **FSA hard-freeze control** — halt SCFF after a formation window vs always-plastic, on home + P11 drift arenas | t1.5 | Whether always-on SCFF update circuitry earns its keep (ties ⇒ dead weight; drift-only-loss ⇒ scopes what continuous plasticity buys) |
| **B** | **Marczak attribution control** — supervised-contrast SCFF (labels pick InfoNCE positives, still local/forward-only) vs label-free, else locked | t1.7 | Whether the robustness = objective *structure* or label-*absence* |
| **C** | **Ghunaim real-time protocol** — price TIME as we price energy | t1.3 | An unbanked "stream-doesn't-wait" win at fire-fraction ≈0.003 |
| **D** | **DS-AL dual-stream namer** — a 2nd closed-form ridge fitting the residual in the null space | t1.2 | Attacks the anisotropy / under-fit gap; slots into the existing sleep |
| **E** | **Slow-EMA closed-form "stable namer"** — EMA the namer's Gram/covariance | t1.4 | Anti-recency stability vs the worst-point-BWT tension the cadence fights |
| **F** | **DRTP-head bake-off** — random-projection supervised head vs SLDA/RanPAC | t1.6 | Whether a random backward path helps the 20% namer (never the bulk) |

---

## Must-cite anchors (the ⭐⭐⭐⭐⭐ set)

Hinton FF 2022 · **Spyra & Dzwinel 2025** (energy honesty) · ACIL 2022 · Deep SLDA 2020 · **SIESTA 2023** · Hayes & Kanan 2022 · CLS-ER 2022 · ESMER 2023 · Janson 2022 · SimpleCIL 2023 · **FSA 2023** · Tang 2023 · **Bartunov 2018** · **Refinetti 2021** · **Filipovich 2022**.

*(Full table with links + per-paper "relation to us": [`../INDEX.md`](../INDEX.md).)*
