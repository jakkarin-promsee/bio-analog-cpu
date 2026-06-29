# P5.0 — the bench + the decay reproduction + the guards

**Question.** Does the Phase-5 apparatus reproduce the P4.3 depth-decay (per-layer probe peak ~L5 → tail-L12
slide ~0.43) at full protocol, and pass its sign-bug guards, *before* any cell is trusted? And does the w12
diagnostic confirm the decay is **objective-locality**, not an intrinsic Tunnel?

**Setup.** Cell = `p5lib.SCFFContrastOverlap` (the adopted contrast+coordination cell, ported verbatim from the
T3 seed; `temp=0.5`, `mask=0.5`, `lr=0.03`). Controls locked: `L=12, W=64, DIM=40, NCLASS=4, NTR=4000, NTE=1500,
EP=25, BATCH=32`, seeds `[42,137,271,314,1729]`, **PROBE_EP=120** (full protocol; T3 used 60). Three tasks —
**headroom** (`make_tierb`, depth should pay), **flat** (`make_gauss`, known Bayes), **mixed** (the new
disjoint-label corruption detector, design §6's refinement of P4.3's shared-label version). Two cells — **w2**
(adopted) and **w12** (the objective-capability ceiling = full e2e credit, *never deployed*). References:
**tuned-BP** (`race_bp`, iso-budget, the achievable old-world anchor) on headroom + mixed-per-subtask; **Bayes**
on flat. Guards (pre-cell): `equivalence` (overlap≡OLU bit-for-bit), `fd_gradient` (the InfoNCE window backward),
dead-frac, cost-monotonicity.

**Run.** Guards first → all pass → 30 cells × probes + 15 refs, checkpointed (`_ckpt.jsonl`, fsync), single-thread
(`OMP_NUM_THREADS=1`). Wall ≈ 41 min. No NaN, no resume needed.

**Result / figures.**

| metric (headroom) | OURS w2 (adopted) | w12 ceiling | tuned-BP | reading |
| --- | --- | --- | --- | --- |
| peak layer | **L5** (0.540) | L12 | — | composes then decays |
| tail-L12 (probe) | **0.435 [0.411–0.437]** | 0.556 [0.553–0.557] | — | decay real (IQR-disjoint, 5/5) |
| readout acc | 0.449 [0.446–0.455] | 0.569 [0.563–0.572] | 0.531 [0.531–0.533] | trails both refs |

| task | OURS-w2 decay tell | the control | verdict |
| --- | --- | --- | --- |
| **headroom** | peak L5 0.540 → tail 0.435 | w12 no-decay (tail 0.556) | decay = locality, **reproduced** |
| **flat** | peak **L3** 0.729 → tail 0.620 [0.602–0.669] | Bayes-opt 0.890 | easy → shallower extractor, less decay |
| **mixed** (flat subtask) | peak 0.724@L5 → tail **0.475 [0.469–0.549]** | w12 preserves (0.708); BP holds 0.761 | **corruption reproduced** (OURS-specific) |

- **DEPTH-PROFILE-headroom** (headline): OURS-w2 rises to L5, crosses tuned-BP, then slides below the w12 ceiling
  past L7 — the decay, between the forbidden best (w12) and the deployable reference (BP). - **DEPTH-PROFILE-flat**:
  peaks at L3 (easier → earlier), decays less. - **DEPTH-PROFILE-mixed**: the flat subtask corrupts 0.72→0.48 while
  BP-flat holds 0.76 and w12 preserves 0.71 — the cleanest decay tell. - **INV**: InfoNCE loss falls (learns),
  **dead-frac ≤ 0.016 (≈0)**, erank 48→12, backward-work monotone in window, **FD 2.1e-8 / equiv 0.0e+0 PASS**.

**Read (6 + 2 slots).**

1. **Claim** — The Phase-5 bench reproduces the P4.3 depth-decay at full protocol, and the decay is
   **objective-locality** (the *same* InfoNCE composes all 12 layers under full credit), not an intrinsic Tunnel.
2. **Headline** — Headroom OURS-w2 **tail-L12 0.435 [0.411–0.437]**, peak L5, vs the w12 ceiling **0.556
   [0.553–0.557]** and tuned-BP **0.531 [0.531–0.533]** (n=5, PROBE_EP=120). The earn-depth gap to w12 is **0.121**
   (probe) / **0.120** (readout) — real (IQR-disjoint, 5/5 by seed).
3. **Figures** — DEPTH-PROFILE-{headroom (headline), flat, mixed}, INV. All regen from `arrays.npz`.
4. **Mechanism** — A **direction** failure, not capacity. Dead-frac ≈ 0 at every layer (max 0.016) kills the
   dead-unit story; erank declines (48→12) but P4.3 already proved rank is a *symptom*, not the lever. What moves is
   the **class direction**: the linear probe peaks ~L5 then falls, while w12 — same objective, full credit — never
   falls. So the decay is *trigger* (abstraction saturates ~L5) × *multiplier* (no preserve term → post-saturation
   layers overwrite). The mixed task is the sharpest read: deep layers the headroom subtask needs **corrupt** the
   early-solved flat subtask (0.724→0.475), and full credit (w12) does **not** (0.708) — the corruption is OURS-w2
   (locality)-specific and curable by credit. The spine holds: the lost quantity is the class DIRECTION (the probe),
   never a magnitude.
5. **Threats** — (a) a port bug masquerading as the decay → **killed** by the equivalence guard (bit-exact) + the
   FD-gradient guard (2.1e-8 < 1e-5); (b) a probe-protocol artifact → ran at full PROBE_EP=120, peak/tail stable vs
   T3's 60 (w2 tail 0.435 here ≈ 0.429 there); (c) the mixed flat-subtask IQR is wide [0.469–0.549], but the
   w2-vs-w12 corruption is IQR-disjoint **and** 5/5 by seed (real per §B); (d) erank decline is *not* invoked as the
   lever (symptom, P4.3).
6. **Decision** — **BENCH TRUSTED** (peak within ±1 of L5; tail in the ~0.43 band). The targets this sets for the
   earn/read threads: close OURS-w2 tail **0.435 → w12 0.556 / BP 0.531**; un-corrupt the mixed flat subtask **0.475
   → BP 0.761**. P5.1 (temperature) inherits this bench unchanged.
7. **Cost-honesty** — No cost *claim* at P5.0 (this is a reproduction). The substrate backward-work meter is sane and
   **monotone in window** (52k → 585k forward-equivalent units, INV); w12 is the **11×** forbidden upper bound (never
   deployed); the truncation floor — the cheap baseline every later tier must beat — is established at P5.3, not here.
8. **SCFF-completion** — Nothing is "done" at P5.0; it confirms the flaw is **real and curable in principle** (w12
   composes), which is the precondition for the whole phase. **Continual-safety (P5.7): untouched** — no change is
   banked at P5.0, so the A6 gate is not yet at risk.

**Pre-submit checklist.**
- [x] Median [IQR] for every headline number (n=5); no bare means.
- [x] "Real difference" rule applied (IQR-disjoint **and** ≥4/5 sign) for the decay (w2-vs-w12) and the corruption.
- [x] Every depth figure draws the **w12 ceiling**; the achievable **tuned-BP / Bayes** reference added (truncation
      floor deferred to P5.3, noted on the figure caption).
- [x] Every figure drawn by a `plot_p5.fig_*` function; `plot_p5.py regen <run-dir>` redraws all four from saved data.
- [x] All 8 slots filled, formal voice; the card opens by naming the inherited target (none — P5.0 is the bench root).
- [x] `manifest.json` (git, config, seeds, versions, wall-clock) + `arrays.npz` written to the §A schema.
- [x] Guards logged: FD-gradient 2.1e-8 (<1e-5), equivalence 0.0e0 (bit-exact), dead-frac ≤0.016, cost monotone.
- [x] Single-threaded (`OMP_NUM_THREADS=1`, `python -u`, `PYTHONIOENCODING=utf-8`) — phantom-hang + cp874 guards.
- [x] Spine check: no placement/exit/objective reads goodness or energy; no residual; no whitening. N/A at P5.0.
- [x] Continual-safety (P5.7): no change banked → not yet applicable.
- [x] `RESULTS.md` row added (§D schema).
