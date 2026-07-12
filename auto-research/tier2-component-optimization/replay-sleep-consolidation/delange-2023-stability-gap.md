# Continual evaluation for lifelong learning: Identifying the stability gap
- **Authors / Year / Venue:** Matthias De Lange, Gido M. van de Ven, Tinne Tuytelaars / 2023 / ICLR 2023 (spotlight)
- **Link:** https://arxiv.org/abs/2205.13452 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule (the *lens*)
- **Relevance:** ⭐⭐⭐⭐ — supplies the fine-grained safety instrument our worst-BWT gestures at but never fully measures: the **per-iteration** accuracy dip right after a switch, and metrics (min-ACC, worst-case) to quantify it.

## TL;DR
Standard CL evaluation only checks accuracy at task boundaries and so **hides** a real failure: when a new task starts, accuracy on old tasks drops fast, then partially recovers — the **stability gap**. They define per-iteration continual-evaluation metrics (min-ACC, worst-case forgetting) and show the gap afflicts *every* method family, replay included.

## The mechanism (how it actually works)
Rather than a mechanism to fix forgetting, this is a **measurement reframe**. Evaluate accuracy on all seen tasks **every training iteration**, not only at boundaries. Two new metrics: **min-ACC** (the lowest old-task accuracy reached during a task's learning) and worst-case measures over the trajectory. A gradient decomposition (a "plasticity" component vs a "stability" component) explains the transient dip: at onset the new-task gradient dominates and transiently corrupts old-task representations before rehearsal/regularization pulls them back. The gap **grows with task dissimilarity** (bigger distribution shift → deeper dip).

## Key results / claims
The stability gap appears for experience replay, GEM-style constraint replay, knowledge distillation (LwF), and regularization (EWC) across class-, task-, and domain-incremental benchmarks. Final-accuracy numbers can look fine while min-ACC is much worse — i.e. the worst-case user experience is systematically under-reported.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the safety metric (worst-point BWT, P9.5 / P10), the sleep cadence, the gauntlet stream (P10 §10).
- **Same as us:** we already reach for *worst-point* safety (worst-BWT −0.028 at grid-4, the oracle-veto) rather than only final accuracy — the same instinct this paper formalizes. Our P10 §10 per-batch GAUNTLET-STREAM views (ER saw-tooths at every domain switch while OURS rides flat) are *exactly* a stability-gap trace, unnamed.
- **Different from us:** our BWT is still sampled at coarser points; the true stability gap is the **min over every iteration between sleeps**. Between two grid-4 sleeps the pre-sleep state can dip (P9.5 saw deep troughs at grid-8) — that trough *is* the stability gap and we don't currently report its depth as a first-class number.
- **What we could borrow or test:** adopt **min-ACC** as a reported metric for the grid-4 loop — a zero-cost, gradient-free instrument that sharpens our safety claim and would make the "OURS rides flat vs ER saw-tooths" result quantitative rather than a picture.
- **What contradicts or challenges us:** if a min-ACC audit of the *inter-sleep* window reveals dips our boundary-sampled BWT misses, our "near-flat continual-safety" claim is softer than stated — worth checking before over-claiming.

## Follow-on leads
- Harun & Kanan 2023 "Overcoming the Stability Gap" (the fix + the compute win) — carded.
- Lange et al.'s continual-evaluation toolkit (Avalanche integration) as a ready metric harness.
