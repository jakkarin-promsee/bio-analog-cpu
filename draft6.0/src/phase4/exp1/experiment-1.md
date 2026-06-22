# Experiment P4.1 — ambient-dim tolerance (A2)

> **Status: ✅ DONE (2026-06-22).** Hold difficulty fixed (overlap 0.7 → Bayes **0.108, flat across dim** — the
> signal lives in a 2-D subspace, the rest is pure nuisance) and sweep ambient input dim `[8…500]`. The sharp
> question: **does OURS's contrast filter nuisance dimensions as well as a genuinely-tuned backprop?** Because the
> achievable ceiling is fixed, gap-to-BP is a *clean* read here (no shrinking-window confound, unlike P4.0). Stack:
> numpy-only (`p4lib`), 6 dims × 5 seeds, 4000/1500. Run: `OMP_NUM_THREADS=1 python -u run_p4_1.py` (2897s,
> crash-safe). Contract: [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** A2 lands **OURS's first clear win.** As ambient (nuisance) dimension grows at fixed difficulty,
**OURS holds steady while *both* references degrade** — OURS **crosses *above* tuned BP by dim 500** (gap −0.029,
IQR entirely negative), while **Mono-Forward collapses toward chance** (0.75 → 0.41). OURS is the **most
nuisance-robust racer**, **generalizes best** (lowest train−test gap), and at high dim is **also cheaper than BP**.
The naive worry — "extra dims hurt the cheap brain" — is *wrong*: its contrastive objective *wants the room*.

**2 · Number + IQR** (median [IQR], n=5; Bayes ≈ 0.108 flat):

| dim | OURS | BP (tuned) | Mono | gap-to-BP | capture | OURS gen-gap |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | 0.753 | 0.877 | 0.749 | +0.122 [+0.119,+0.143] | 0.79 | +0.06 |
| 16 | 0.740 | 0.863 | 0.727 | +0.119 [+0.119,+0.121] | 0.76 | +0.14 |
| 40 | 0.795 | 0.830 | 0.734 | +0.035 [+0.033,+0.037] | 0.85 | +0.14 |
| 100 | 0.792 | 0.821 | 0.656 | +0.029 [+0.027,+0.035] | 0.85 | +0.16 |
| 250 | 0.782 | 0.799 | 0.489 | +0.020 [+0.017,+0.022] | 0.83 | +0.18 |
| 500 | 0.763 | 0.741 | 0.411 | **−0.029 [−0.029,−0.025]** | 0.80 | +0.20 |

OURS gap-to-BP **closes monotonically and crosses zero** (~dim 350–400): +0.122 → **−0.029**. **Mono-Forward
collapses**: 0.749 → 0.411 (gap-to-BP *explodes* +0.13 → +0.33). OURS **capture flat ~0.79–0.85** (broadly robust,
mild mid-dim peak). **Cost @dim 500:** OURS ~106k vs BP ~155–232k (seed-dependent shape) vs Mono ~54k — OURS
**cheaper *and* more accurate** than BP in high-D. OURS gen-gap stays low (0.06→0.20); **Mono's explodes 0.07→0.59**.

**3 · Figures.** `RACE` (Bayes-optimal flat ✓; BP declines 0.88→0.74; OURS plateaus ~0.79 and crosses BP; Mono
plunges to 0.41) · `GAP_CURVE` (OURS gap crosses zero; Mono gap explodes; capture flat) · `INV` (Bayes flat in dim
= apparatus ✓; cost grows, BP fastest; gen-gap — Mono explodes, OURS lowest).

**4 · Mechanism.** A nuisance dim is **identical across a sample's positive and negative contrast views**, so it
contributes ~nothing to the InfoNCE signal — OURS **down-weights non-discriminative dims for free** (helped by
per-sample layernorm). **Mono-Forward** has no such filter: every input dim feeds the per-layer supervised CE, so
nuisance dims become **spurious features it memorizes** → catastrophic overfitting (gen-gap 0.59) → collapse toward
chance. **BP** *can* learn to ignore nuisance, but at the **matched weight budget** its first layer is squeezed
(most weights spent on nuisance fan-in) → gentle decline, and its cost balloons. So the high-D winner is whoever
uses a **fixed weight budget** most efficiently on irrelevant inputs — and that's the contrastive forward-only cell.

**5 · Threats.** (a) Synthetic nuisance is **pure isotropic Gaussian**; real nuisance is structured/correlated — a
real-data anchor is owed (carries to P4.4/synthesis). (b) The crossover is **partly BP being budget-constrained in
high-D** — fair (the same Scap budget binds everyone, which is exactly the substrate's constraint) but **named**:
it's "best use of a fixed budget under nuisance," not "BP can't ignore nuisance in principle." (c) Fixed
mid-difficulty (overlap 0.7) — the **crossover dim likely shifts with difficulty**; a difficulty×dim MAP would
settle it (flag for P4.2/synthesis). (d) Dim capped at 500 (dim-1000 BP search too slow for 5 seeds).

**6 · Decision.** **A2 = OURS's first clear WIN — nuisance-dimension robustness, and it's substrate-relevant**
(analog crossbars are *wide* / high-fan-in; noisy high-D analog inputs are the substrate's native regime). **Carry
forward:** (i) the contrast objective is **intrinsically nuisance-robust** (down-weights non-discriminative dims) —
a genuine architectural advantage, not a tuning artifact; (ii) **Mono-Forward is NOT a safe high-D reference** (it
collapses) — keep it precisely *as* the cautionary racer; (iii) the **crossover dim is difficulty-dependent** — a
key map coordinate for the difficulty×dim MAP.

**7 · Cost-honesty.** Numbers are **backward credit-assignment work** (analytic, substrate units). At dim 500 OURS
(~106k) is **roughly half** BP's (~155–232k) *and* more accurate — the only axis so far where OURS wins both
accuracy and cost. The crossover is at **matched weight budget** (the right substrate test), with the caveat in
threat (b) that part of BP's high-D weakness is the budget squeeze, not pure algorithm.

**8 · Map-contribution → P5 / synthesis.** A2 tile: **OURS owns the high-D / nuisance regime.** It tells Phase 5:
the substrate's **wide analog inputs are OURS's friend, not its foe** — the cheap brain earns its keep exactly where
the hardware lives. The **crossover dim** (where OURS overtakes BP) is the headline map coordinate and deserves a
**difficulty × dim heatmap** (P4.2 or the synthesis). Mono-Forward flagged **high-D-unsafe**. First win on the
board; the home axes (continual A6, noise A7) still ahead.

---

## Reproducibility

`figs_p4_1/{manifest.json, arrays.npz, _ckpt.jsonl}`; figures regenerate `python plot_p4_1.py figs_p4_1`.
Single-threaded, `python -u`, per-cell fsync; verified alive mid-run. **Apparatus fix this rung:** `bayes_error`
rewritten to the dot-product identity (`‖x−c‖² = ‖x‖²−2x·c+‖c‖²`) — `[n,K]` not `[n,K,dim]`, memory-safe to
dim~1000s (the old form was ~5 GB at dim 1000 — would have crashed the run). New cell: `exp1/run_p4_1.py` +
`plot_p4_1.py` (dim sweep, log-x, Bayes-flat INV check).
