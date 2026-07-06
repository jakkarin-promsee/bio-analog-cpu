---
name: status
description: The live state of draft 6.0 — the phase ladder (P1–P11 DONE), the verdicts S14 (the neocortex) + S15 (the real-data limit map), what is next. Use for "where are we", "current status", "what is the live plan", "what did phase N find", "what is next", "is it done", "what is phase N".
---

# draft 6.0 — current status

**Both stages are DONE and the neocortex is validated (Phases 1–10, verdict S14: a substrate-native continual learner); and Phase 11 — the limit map — has since validated it on real data + scale (S15). The live line is now the analog-realism (SPICE/PVT) layer.** The ladder — verdict + where the detail lives:

**Stage 1 — the cheap brain (P1–6):**
- **P1 ✓ structure** — the continual win: one SCFF+GD block generalizes better than backprop at ~10% backward cost, and sleep recovers what online-BP catastrophically forgets; *not* a static-accuracy competitor. → `src/phase1/README.md`
- **P2 ✓ depth round 1** — a deep SCFF stack can't earn depth (transmission *and* a perfect-oracle objective both fail); depth = boosted shallow blocks (later dropped for a single bulk, S11). → `src/phase2/README.md`
- **P3 ✓ depth round 2 — ADOPTED** — the wall was the **energy objective `Σh²`**, not locality; **contrast (InfoNCE) + a coordination window** compose depth, superseding energy-goodness. → `src/phase3/README.md`
- **P4 ✓ characterization** — capability map vs *tuned* backprop: a substrate-native **continual** learner. WINS continual / nuisance-dim / depth-composition / depth-cheap; TRAILS static difficulty / class-count; one honest NEGATIVE on eval-time noise. → `src/phase4/README.md`
- **P5 ✓ SCFF close-out — depth SOLVED (scoped)** — the decay was **objective-locality, not an intrinsic Tunnel**; sharper InfoNCE **temp 0.2** earns the depth back (direction, not lr) + a short fixed reader reads the home ~8× cheaper. Committed cell: `SCFFContrastOverlap` temp0.2 / w2, L12, NO residual. → `src/phase5/README.md`
- **P6 ✓ noise-hardening — Scoped-YES** — A7 (eval-time noise) is real, OURS-specific, directional; a **noise-augmented view** (`NoiseAugContrast`, σ_aug=1.0) hardens the tap channel forward-only, *improves* clean acc, keeps the continual win; the input-transducer residual → Stage-2 read-side. → `src/phase6/README.md`

**Stage 2 — the namer (P7–10):**
- **P7 ✓ the namer is NOT gradient descent** — a closed-form streaming head (**RanPAC** / **SLDA** committed, cbrs guard) ties a tuned MLP and passes the A6 gate; the spine bends (magnitude-wins). *The 20% is a role, not a method.* **(S11.)** → `src/phase7/README.md`
- **P8 ✓ the economy, run LIVE** — both brains live; a **DDM** gate on the namer's **error-EMA** (a class-direction trigger validated but not shipped) meters the 80/20 real (GD-share 0.121), OURS ≈ ½ BP+replay, and **firing more forgets more** (the gate is safety). Why-analog: 15.4× = 5.4× substrate × 2.9× algorithm. **(S12.)** → `src/phase8/README.md`
- **P9 ✓ freeze the maintenance loop** — the bulk **rotates but does not forget** (measured); N2 struck, all-tap kept, **CBRS** committed, the read-side residual defended by **proto-reanchor**; the freeze caught the drift-conditional cadence (grid-8→**grid-4**), **locked at `59d2720`**. **(S13.)** → `src/phase9/README.md`
- **P10 ✓ the honest race** — the frozen object raced a fair, budgeted, tuned BP+replay baseline (verdicts pinned blind). **S14:** ties the continual home (0.494 vs 0.498), trails natural digits (continual, not static), **wins** continual safety (worst-BWT −0.028 vs −0.272, ≈10× safer) + noise (every held-out channel); the energy edge is substrate-realized. → `src/phase10/README.md`

**Real-data validation — the limit map (P11):**
- **P11 ✓ the limit map — real data + scale (S15)** — the frozen object (Arm A bit-equal committed; Arm B a pre-registered scaling rule; nothing tuned; ER re-tuned per arena) across **8 real arenas × 5 channels** (win/tie/loss/FLOOR): **gas WINS** (prequential 0.789 ≥ a per-arena-tuned ER 0.756, beats persistence +0.184), real-MNIST safety + order-invariance hold (static AA trails — continual, not static), cross-dataset **type-robust** when scaled, the autocorrelated streams (HAR/electric/covtype) **FLOOR** honestly (ELEC2 persistence trap, field +0.07). Scale: the pinned **GD-share economy shape CONFIRMED**, the analog substrate factor **GROWS** 5.4→7.4×, the namer **out-retains byte-matched replay by C=20**. Decomposition: the bulk is the nonlinear learner (Δbulk +0.417, beats a random reservoir), the safety is the closed-form namer+gate+sleep. The three reviewer strikes (is-it-SLDA / toy-data / does-it-scale) answered. → `src/phase11/README.md`

**Solid vs open:** the neocortex is closed (both brains built, characterized, frozen, raced against a fair opponent, **and validated on real data + scale in Phase 11**). Open = the analog-realism layer (SPICE / PVT / device noise — everything so far is ideal floats + behavioral noise/energy models), and beyond the numbered phases the recurrent lifelong brain (the north star).

**The whole model in one self-contained file:** `draft6.0/src/phase9-final-architecture.md`. **The live decision record:** `draft6.0/idea/main.ideas.v1.md` (committed N1–N3 + S1–S15). **The report volumes:** `src/stage1-report.md` (P1–6, the cheap brain) · `src/stage2-report.md` (P7–9, the namer build + freeze) · `src/validation-report.md` (P10–11, the frozen object on trial — the fair race + the limit map).

**Off-limits:** the recurrent lifelong "thinking" brain is the north star, *beyond* the numbered phases — deliberately not specced. Hold as direction (`research/north-star/`, `docs/essence/`), not a task.

**Budget:** this skill + at most one `phaseN/README.md`. A multi-phase sweep → dispatch the `Explore` subagent.
