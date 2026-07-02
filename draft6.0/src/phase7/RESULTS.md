# Phase 7 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema (no prose). Controls locked unless swept. Device under test = the
> frozen `NoiseAugContrast` cell (SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0). Feature source =
> **all-tap (768-D)**, pinned at P7.0. Seeds `[42,137,271,314,1729]` (9 for the ≤0.02 spine-tension gap). Median
> [q25–q75]. `PROBE_EP=120`. Cost = **proxy, descriptive-only (real meter = P8)**.

---

## P7.0 — bench + guards + convex floor + static ceiling + RanDumb control  `exp0`
*(controls: synthetic CI home, all-tap, seeds ×5, PROBE_EP=120; guards 7/7 pass; wall 24.7 min)*

| ref / head·bulk | acc | vs-floor | vs-static-ceiling | vs-randproj-taps | vs-randproj-pixels | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| linear-softmax **(floor)** | 0.608 [0.582–0.610] | (floor) | −0.258 | +0.002 | +0.147 | the floor |
| MLP head | 0.642 [0.622–0.649] | +0.034 | −0.224 | — | — | small GD head buys +0.034 |
| `race_bp` **(static ceiling, raw input)** | 0.866 [0.861–0.887] | +0.258 | (ceiling) | — | — | tuned BP on pixels ≫ SCFF readout |
| OURS-bulk · **linear** | 0.608 | (floor) | −0.258 | **+0.002 (tie)** | **+0.147** | earns keep vs pixels; ties taps (ELM) |
| OURS-bulk · **rls** (ridge) | 0.579 | −0.029 | −0.287 | **+0.194** | **+0.265** | **earns keep on both arms** |
| OURS-bulk · ncm | 0.261 | −0.347 | — | −0.038 | +0.059 | sub-floor (greyed); earns keep vs pixels |

INV: dead-frac **0.000** · effective-rank **58.7** · FD-guard ✓ · feature-source-pinned ✓.
**Verdict:** BENCH TRUSTED — bulk beats random-from-pixels (5/5, decisive); random-from-taps tie for a linear namer
is the expected ELM effect (flagged to Stage 2, both readings); static ceiling confirms SCFF is a *continual*, not a
static-accuracy, competitor (P4-consistent).

## P7.1 — the readout bake-off (headline)  `exp1`
*(controls: pinned all-tap taps, synthetic CI home, seeds ×5, PROBE_EP=120; wall 54.6 min. head swept)*

| head | acc | AA | BWT | spine-flip@2 | recency-drop | cost-proxy | vs-floor(AA) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear-softmax (floor) | 0.591 [.591–.595] | 0.584 | −0.181 | 0.684 | 0.181 | 7.7e3 | (floor) | the floor |
| cosine-ncm (spine, no-grad) | 0.262 | 0.319 | −0.142 | **0.000** | 0.142 | 7.7e3 | −0.265 | spine-clean, sub-floor (greyed) |
| cosine-softmax (spine, grad) | 0.537 | 0.480 | −0.234 | **0.000** | 0.234 | 7.7e3 | −0.104 | spine-clean, trails frontier |
| NCM | 0.264 | 0.331 | −0.157 | 0.577 | 0.157 | 7.7e3 | −0.253 | magnitude, sub-floor (greyed) |
| SLDA (tied cov, no-grad) | 0.583 | 0.604 | −0.162 | 0.893 | 0.162 | 7.7e3 | +0.020 | top-cluster; norm-sensitive |
| FeCAM (per-class cov, no-grad) | 0.531 | 0.459 | −0.302 | 0.764 | 0.302 | 5.9e6 | −0.125 | max-magnitude; worst BWT |
| **RanPAC (proj+ridge, no-grad)** | **0.647** | **0.617** | −0.157 | 0.537 | 0.157 | 1.6e6 | **+0.033** | **committed (top acc, spine tie-break)** |
| RLS (ridge, no proj, no-grad) | 0.623 | 0.558 | −0.197 | 0.561 | 0.197 | 7.7e3 | −0.026 | proj earns keep (RanPAC−RLS +0.047 real) |
| MLP head (non-convex, grad) | 0.625 | 0.623 | −0.147 | 0.604 | 0.147 | 2.5e4 | +0.039 | top-cluster (the "if we paid GD" anchor) |

**Verdict:** frontier top = 3-way tie {MLP 0.623, **RanPAC 0.617**, SLDA 0.604} (mutually within-noise); best is
**no-gradient RanPAC** (highest acc 0.647, spine tie-break) → *the 20% is not gradient descent*. Spine-tension =
**magnitude-wins-spine-bends** (Δ = paired-by-seed median of [AA(ranpac)−AA(cosine-softmax)] = **+0.128**; head medians
0.617 vs 0.480; real 5/5, >δ=0.02; cosine spine-clean at flip 0 but sub-competitive). Cost proxy: RanPAC ~200× SLDA (→ P8; SLDA = cheaper within-noise no-grad alternative).

---

## P7.2 — multimodality / heterogeneity: the closed-form cliff  `exp2`
*(controls: pinned all-tap taps, natural digits = decider, synth-blob = sanity, seeds ×5; wall 65.6s)*

| ladder-rung | acc (digits, natural) | acc (synth-blob sanity) | n-modes (natural) | closed-form? | verdict |
| --- | --- | --- | --- | --- | --- |
| mean (NCM) | 0.754 [0.742–0.762] | 0.285 | 1.00 | ✓ | one mean underfits |
| **SLDA (tied cov)** | **0.946 [0.946–0.951]** | 0.267 | — | ✓ | **the covariance escape (+0.19)** |
| FeCAM (per-class cov) | 0.921 [0.905–0.933] | 0.298 | — | ✓ | per-class overfits (< SLDA) |
| GKEAL (kernel) | 0.586 [0.583–0.613] | 0.857 | — | ✓ | multimodal fallback (rescues sanity only) |
| mixture (k=3) | 0.824 [0.802–0.839] | 0.693 | — | ✗ | non-convex; **hurts digits (−0.12)** |

**Verdict:** natural features **unimodal** (n-modes 1.0); the lever is the **tied covariance (SLDA), closed-form, no
mixture needed** (mixture hurts). Convex/analytic story holds. SLDA's whitening is a magnitude tool — sharpens (not
dodges) the spine tension.

## P7.3 — the bursty-stream imbalance guard  `exp3`
*(controls: pinned bulk, bounded recency-skewed buffer cap=800, seeds ×5; committed RanPAC + comparators; wall 47s)*

| head (family) | guard | acc-old | acc-recent | recency-gap | verdict |
| --- | --- | --- | --- | --- | --- |
| **RanPAC** (analytic) | none | 0.179 | 0.674 | +0.495 | biased under strong skew |
| **RanPAC** | **cbrs** | **0.562** | 0.575 | **+0.013** | **shipped — near-eliminates gap** |
| RanPAC | air | 0.506 | 0.412 | −0.094 | over-corrects (not shipped) |
| SLDA | cbrs | 0.529 | 0.583 | +0.055 | clean; air over-corrects (recent→0) |
| cosine-softmax (trained) | none | 0.024 | 0.683 | +0.659 | **worst recency bias (trained-softmax)** |
| cosine-softmax | cbrs | 0.392 | 0.587 | +0.195 | logit-adj +0.214, bal-softmax barely |
| mlp (trained) | cbrs | 0.475 | 0.569 | +0.094 | logit-adj +0.254 |

**Verdict:** trained-softmax has the worst intrinsic recency bias (+0.659); no-gradient RanPAC less so (+0.495). The
**shipped guard = class-balanced reservoir (cbrs)**, buffer-side + family-agnostic (RanPAC → +0.013). **AIR
over-corrects** → the design's "AIR is the no-gradient guard" is **overturned** (buffer balance beats output re-weighting).

---

## P7.4 — continual-safety: the home-turf GATE  `exp4`
*(controls: pinned bulk, synthetic CI home, seeds ×5 (never 3), baseline = floor-head-on-same-bulk; wall 5.1 min)*

| head | AA | BWT(+paired-sign) | forget | vs-floor-head | neg/5 | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| linear-softmax | 0.584 | −0.181 | 0.182 | (baseline) | 0/5 | (baseline) |
| cosine-ncm (no-grad) | 0.319 | −0.142 | 0.147 | +0.059 | 0/5 | PASS |
| cosine-softmax (grad) | 0.480 | −0.234 | 0.234 | −0.030 | **5/5** | **STRUCK — dents A6 (trained-softmax recency)** |
| SLDA (no-grad) | 0.604 | −0.162 | 0.162 | +0.013 | 0/5 | PASS |
| FeCAM (no-grad, max-mag) | 0.459 | −0.302 | 0.302 | −0.127 | **5/5** | **STRUCK — dents A6 (per-class cov overfit)** |
| **RanPAC (committed, no-grad)** | **0.617** | **−0.157** | 0.157 | +0.023 | 0/5 | **PASS — adoption stands** |
| RLS (no-grad) | 0.558 | −0.183 | 0.183 | −0.003 | 3/5 | PASS (within noise, <4/5) |
| MLP (grad) | 0.623 | −0.147 | 0.149 | +0.040 | 1/5 | PASS |

**Verdict:** committed **RanPAC PASSES** (keeps the A6 win, 0/5 negative). The gate strikes the trained cosine-softmax
and the max-magnitude FeCAM (5/5 each). Mechanism control: cosine-ncm (no-grad) passes but cosine-softmax (grad, same
angle metric) is struck → the **trained weights**, not the metric, cause the recency dent (BiC/WA/SCR confirmed).

## P7.5 — natural-data confirmation  `exp5`
*(controls: pinned bulk, committed knobs, continual stream; digits ×5, CIFAR-flat ×3; wall 7.6 min)*

| head | digits AA | digits BWT | CIFAR-flat AA | verdict |
| --- | --- | --- | --- | --- |
| **RanPAC (committed)** | **0.949 [.947–.956]** | −0.012 | 0.265 [.261–.269] | **#1 on digits**; projection idle on depth-less CIFAR |
| linear-softmax (floor) | 0.946 [.941–.959] | −0.014 | 0.293 | strong digits; ~chance-band CIFAR |
| RLS (no-grad) | 0.944 | −0.017 | 0.320 | robust on CIFAR |
| MLP (grad) | 0.944 | −0.017 | 0.297 | GD anchor = no better than no-grad |
| SLDA (no-grad) | 0.942 | −0.015 | **0.325** | **top on CIFAR**; cheap robust alt |
| cosine-softmax (spine) | 0.913 [.909–.923] | −0.033 | 0.324 | competitive digits (−0.036); top-tier CIFAR |
| cosine-ncm (spine) | 0.568 | −0.147 | 0.236 | sub-competitive |

**Verdict:** RanPAC **confirmed #1 on the SCFF-working natural home (digits)** with near-zero forgetting; the spine
price **shrinks 4×** (synthetic −0.128 → digits −0.036) and **vanishes on CIFAR-flat** (all heads ~0.3; SCFF has no
depth there — P4/P5/P6 wall; SLDA edges RanPAC). Ordering confirms RanPAC; the CIFAR caveat flags SLDA to P8.

---

## P7.6 — assembled-head confirmation  `exp6`
*(committed pipeline = RanPAC + cbrs; synthetic CI home, seeds ×5; wall 44s)*

| pipeline | AA | BWT | vs P7.1 solo bar (0.617, band 0.02) | verdict |
| --- | --- | --- | --- | --- |
| RanPAC solo | 0.617 | −0.157 | (bar) | the P7.1/P7.4 committed head |
| **RanPAC + cbrs (assembled)** | **0.627** | **−0.132** | **+0.010 (HOLDS)** | **levers stack — guard non-degrading, BWT improves** |

**Verdict:** the assembled committed pipeline HOLDS above the P7.1 solo bar (AA 0.627 ≥ 0.597; BWT improves). The
imbalance guard does not degrade the balanced home and fixes the bursty skew (P7.3).

---

## The verdict (Phase 7)

**Committed namer = RanPAC** (frozen random ReLU projection → running-Gram ridge prototype) **+ class-balanced-reservoir
guard**. **The 20% is NOT gradient descent** — RanPAC is closed-form/streaming analytic; it ties the gradient MLP anchor
on acc×BWT (3-way tie) and leads on natural digits (0.949, #1). **Spine-tension = magnitude-wins-spine-bends**
(Δ=0.128 synthetic, shrinking to −0.036 on digits, ≈0 on CIFAR): cosine is spine-clean (argmax-flip 0.000) but
sub-competitive where the bulk has structure to exploit; the winner reads a magnitude (ridge) but is recency-robust by
having no trained weights. **RanDumb:** the bulk earns its keep vs a raw-pixel random projection (all heads). **A6
gate:** RanPAC PASSES; the trained cosine-softmax + max-magnitude FeCAM are struck. **Cost (proxy, → P8):** RanPAC ~200×
SLDA — **SLDA is the cheaper within-noise no-gradient alternative** flagged to Phase 8.
