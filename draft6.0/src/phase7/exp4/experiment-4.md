# P7.4 — continual-safety: the home-turf GATE  *(the spine gate — un-skippable)*

**Inheriting** the committed namer candidate **RanPAC** (+ the top cluster SLDA/MLP and the cosine candidates) from
P7.1, and the pinned bulk from P7.0. **Question.** Does the committed readout (+ its native online+sleep rule)
**preserve the A6 sleep-recovery continual win** — the architecture's reason for being? An accurate readout that dents
A6 is reverted regardless of its P7.1 accuracy.

**Setup (the BUILT harness, critic-forced).** Each candidate runs through `continual_safety_heads` — the head-factory
extension of `p6lib.continual_safety`, **proven ≡ the old hard-coded `fit_readout` path bit-for-bit** (the
`harness_equiv_guard`, P7.0) — under its **native** rule: closed-form heads (NCM/SLDA/FeCAM/RanPAC/RLS) consolidate by
recomputing statistics on the replay buffer at sleep; gradient heads (cosine-softmax/MLP) sleep-refit by GD. Baseline
= **the floor head (linear-softmax) on the SAME bulk through the SAME gate** (NOT "the P5 readout", which entangles
cell- and head-forgetting). Each head at its P7.1-committed knob. **Power:** 5 seeds (never 3); "within noise" is NOT
an auto-pass — a head negative-BWT vs the floor baseline in ≥4/5 paired seeds **fails**. Wall 5.1 min.

**Result / figures.** *(synthetic CI home, n=5, median; vs-floor paired by seed)*

| head | AA | BWT | forget | vs-floor(BWT) | neg/5 | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| linear-softmax | 0.584 | −0.181 | 0.182 | (baseline) | 0/5 | (baseline) |
| cosine-ncm (no-grad) | 0.319 | −0.142 | 0.147 | +0.059 | 0/5 | **PASS** |
| cosine-softmax (grad) | 0.480 | −0.234 | 0.234 | **−0.030** | **5/5** | **STRUCK — dents A6** |
| SLDA (no-grad) | 0.604 | −0.162 | 0.162 | +0.013 | 0/5 | **PASS** |
| FeCAM (no-grad, max-mag) | 0.459 | −0.302 | 0.302 | **−0.127** | **5/5** | **STRUCK — dents A6** |
| **RanPAC (committed, no-grad)** | **0.617** | **−0.157** | 0.157 | **+0.023** | 0/5 | **PASS — adoption stands** |
| RLS (no-grad) | 0.558 | −0.183 | 0.183 | −0.003 | 3/5 | PASS (within noise, <4/5) |
| MLP (grad) | 0.623 | −0.147 | 0.149 | +0.040 | 1/5 | PASS |

- **CONT-SAFETY** (headline): the committed **RanPAC** and the no-gradient prototypes (SLDA, cosine-ncm) sit at or
  above the floor-head baseline on BWT; the **trained cosine-softmax** and the **max-magnitude FeCAM** fall below it in
  **5/5 paired seeds** — struck. - **INV**: feat-pinned ✓.

**Read (8 slots).**
1. **Claim** — the committed no-gradient RanPAC **preserves the A6 continual win** (BWT +0.023 vs the floor-head
   baseline, 0/5 seeds negative); the gate **strikes the two most magnitude-inflating heads** — the gradient
   cosine-softmax and the per-class-covariance FeCAM — which dent A6 in 5/5 paired seeds.
2. **Headline** — RanPAC BWT −0.157 vs the floor-head baseline −0.181 (**+0.023, 0/5 negative → PASS**); cosine-softmax
   −0.234 (**−0.030 vs floor, 5/5 → STRUCK**); FeCAM −0.302 (**−0.127, 5/5 → STRUCK**) (n=5, synthetic CI home).
3. **Figures** — CONT-SAFETY (each head vs the floor-head baseline, paired-sign marks), INV. Regen from `arrays.npz`.
4. **Mechanism** — the decisive control is **cosine-ncm vs cosine-softmax**: *same angle metric*, but the no-gradient
   ncm variant **passes** (+0.059) while the **gradient** softmax variant is **struck** (−0.030, 5/5). So the recency
   dent is caused by the **trained weights** (which inflate toward recent classes), **not** the readout's metric — the
   exact BiC/WA/SCR magnitude-bias mechanism. The no-gradient heads (RanPAC/SLDA/cosine-ncm) are continual-safe **by
   construction** (no trained softmax weights to inflate); FeCAM is the exception among no-gradient heads because its
   per-class covariance is the *max-magnitude* readout and overfits each task's shape, forgetting the rest.
5. **Threats** — (a) the gate baseline being the wrong reference → it is the floor-head **on the same bulk through the
   same extended gate** (harness_equiv_guard ✓), so head-forgetting is isolated from cell-forgetting; (b) "within noise"
   auto-passing a bad head → the paired-sign veto (≥4/5) is applied, and it *fires* (cosine-softmax/FeCAM struck despite
   modest median gaps); (c) a head passing by being useless → AA reported alongside (cosine-ncm passes but is sub-floor
   on accuracy, so it is not a candidate). RLS is 3/5-negative (within noise, <4/5) → passes but noted as marginal.
6. **Decision** — **RanPAC is banked as the committed namer** (passes the A6 gate at competitive AA). SLDA and MLP also
   pass (the within-noise alternatives); **cosine-softmax and FeCAM are reverted** regardless of their P7.1 numbers. The
   committed head carried to P7.5 (natural confirm) + P7.6 (assembled).
7. **Spine-honesty** — the gate **banks evidence for the P7.1 spine-tension verdict**: the no-gradient heads are
   continual-safe *not because they read direction* (RanPAC/SLDA read a magnitude) but because they have **no trained
   weights** — recency-robust ≠ direction-reading, made empirical here (cosine-softmax, a spine-clean *angle* head,
   still dents A6 because it is trained). Cost not a factor at the gate.
8. **Namer-verdict / continual-safety** — **RanPAC PASSES → the committed namer is a no-gradient analytic head that
   keeps the A6 win.** The spine-tension branch stays **magnitude-wins-spine-bends** (P7.1), now reinforced: the two
   struck heads are the trained-softmax and the max-magnitude pole, precisely the recency-fragile ones.

**Pre-submit checklist.**
- [x] The GATE ran **5 seeds** (never 3) via the **built** `continual_safety_heads` (each head under its native online+sleep rule).
- [x] Baseline = the **floor-head on the same bulk** through the same extended gate (NOT the P5 readout); harness≡old bit-for-bit (P7.0).
- [x] "Within noise" NOT an auto-pass — the **paired-sign veto** (negative-BWT vs floor in ≥4/5) applied; it fired (cosine-softmax, FeCAM struck).
- [x] Median for every headline number (n=5); vs-floor paired by seed.
- [x] Static BP ceiling **not** drawn on the CONT-SAFETY (BWT) figure (static ≠ forgetting baseline).
- [x] AA reported alongside BWT (a head cannot pass by being trivially useless — cosine-ncm passes but is sub-floor on acc).
- [x] Feature source loaded from the pinned P7.0 config; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (committed RanPAC + top cluster).
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded; no sklearn for compute.
- [x] **Continual-safety verdict recorded** for the committed head (RanPAC PASS).
- [x] `RESULTS.md` row added; struck heads (cosine-softmax, FeCAM) logged with the mechanistic reason.
