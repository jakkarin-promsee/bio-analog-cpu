# Analytic & covariance readouts — the families the rough pass missed (the 2nd-pass audit)

> **Why this file exists.** The Phase-7 rough plan fixed the readout bake-off on
> `{linear-softmax, cosine, NCM, RanPAC}` — *spine-correct but incomplete.* A second, deeper research pass (2026-07-01,
> after the author's "the 20% is *cheat-everything*, not GD" reframe) asked one question: **"did the rough research cover
> it all, and is there a better choice?"** Answer: **no, and yes.** The training-free / frozen-backbone CIL-classifier
> literature is a *hot, 2022–2026 area*, and it contains two whole families and one skeptic-control the rough pass never
> named. This file is the mechanism-story for those, ending — like its siblings — in a **"For us."** It **supersedes
> nothing**; it *widens* [`direction-readouts.md`](direction-readouts.md) and [`the-convex-readout.md`](the-convex-readout.md).
>
> **The one scope caveat that governs every number below (read first).** Every paper here runs its readout on a **large
> pretrained ViT/ResNet backbone (ImageNet-scale features, 512–2048-D, sometimes randomly projected to 10k+).** Ours is a
> **tiny 64-wide flat SCFF bulk trained on the task itself** (all-tap ≈ 768-D). **We adopt the *mechanisms*, never the
> absolute numbers** — exactly as Phase 3 adopted GIM/CLAPP's *objective* on flat vectors without their structured-data
> results. Their accuracy figures set *expectations to test*, not results to inherit.

---

## The problem it answers

The rough plan's spine question — *"does the spine-clean cosine head match the recency-robustness of the magnitude
prototypes?"* — implicitly assumed the magnitude prototypes were `{NCM, RanPAC, SLDA}`. But the reframe ("the namer can
be **anything** that names frozen features cheaply") means the honest bake-off must include the **strongest** no-gradient
namers the field actually has. Two questions the rough pass left open, that this literature answers:

1. **When one class-mean underfits (multimodality / heterogeneity), is the only fallback a non-convex mixture?** — No.
   **FeCAM** gives a *closed-form* anisotropic answer.
2. **Is "no-gradient streaming readout" a hopeful bet, or a solved, published paradigm?** — It is a **paradigm**:
   *Analytic Continual Learning* (recursive least squares), and one member is **forward-only *and* online** — our exact
   constraint.

---

## Thread 1 — Analytic Continual Learning: no-gradient IS a published paradigm (RLS)

**The idea.** *Analytic Learning* recasts training a classifier on frozen features as a **least-squares / ridge
regression with a closed form** — and its *recursive* (streaming, batch-by-batch) implementation gives **weights
identical to training on all data at once.** For class-incremental learning this is a killer property: **no exemplars,
no gradient, no forgetting *by construction*** (the recursive update is algebraically equal to the joint solution). The
machinery is a **running autocorrelation/Gram matrix + a rank-update + a solve** — a running second moment and a linear
solve, both substrate-native (a Gram is a cap-array second moment).

The family (Zhuang et al. and successors — repo `ZHUANGHP/Analytic-continual-learning`):

| method | venue | the one move | why it's here |
| --- | --- | --- | --- |
| **ACIL** — Analytic Class-Incremental Learning | NeurIPS 2022 ([2205.14922](https://arxiv.org/abs/2205.14922)) | CIL → **recursive least squares**; keep only the correlation matrix, no samples | the foundational "RLS = joint learning" result |
| **GKEAL** — Gaussian-Kernel Embedded Analytic Learning | CVPR 2023 (⚠ **few-shot** CIL; CVF-only, **no arXiv**) | a **Gaussian-kernel** feature map before the analytic solve | the **closed-form non-linear / multimodal** option (P7.2) — *kernel mechanism only, not a general-CIL result* |
| **Deep SLDA** — Streaming LDA | CVPRW 2020 ([1909.01520](https://arxiv.org/abs/1909.01520)) | running per-class mean + **one shared (tied) covariance**, one-pass streaming | the **cheaper covariance middle** (between NCM and FeCAM) — the substrate-friendlier covariance head |
| **DS-AL** — Dual-Stream Analytic Learning | AAAI 2024 ([2403.17503](https://arxiv.org/abs/2403.17503)) | main stream = **Concatenated RLS** (= joint); a 2nd stream learns the **residual** for plasticity | plasticity *without* gradient — a residual namer |
| **F-OAL** — **Forward-only** Online Analytic Learning *(= AOCIL — same paper, v1→v2 rename)* | **NeurIPS 2024** ([2403.15751](https://arxiv.org/abs/2403.15751)) | analytic classifier + **forward-only** feature path, online, RLS | ⭐ **the near-perfect fit — forward-only + online + no-gradient**; our exact constraint |
| **GACL / G-ACIL** — Generalized Analytic CL | 2024 ([2403.15706](https://arxiv.org/abs/2403.15706)) | handles **mixed / overlapping / unknown-size** class arrivals | our **drift-gated fuzzy-boundary** stream |
| **AIR** — Analytic Imbalance Rectifier | 2024 ([2408.10349](https://arxiv.org/abs/2408.10349)) | an analytic-CL head for **imbalanced / long-tailed** streams | the **no-gradient family's imbalance guard** (P7.3 — the trained-head guards don't apply to a closed-form winner) |
| **AnaCP** — Analytic Contrastive Projection | Nov 2025 ([2511.13880](https://arxiv.org/abs/2511.13880)) | "toward upper-bound CL" via an analytic contrastive projection | the newest state of the art; a stretch-goal reference |

*(⚠ correction, from the lab-manager literature review: **AOCIL and F-OAL are the SAME paper** — arXiv 2403.15751, v1
"AOCIL" → v2/NeurIPS-2024 "F-OAL." The first-pass audit listed them as two; merged here. The 2025 covariance-adaptation
line — DPCR [2503.05423](https://arxiv.org/abs/2503.05423), task-recency-bias-strikes-back
[2409.18265](https://arxiv.org/abs/2409.18265), FoRo [2509.01533](https://arxiv.org/abs/2509.01533) — is noted; we adopt
mechanisms, not those numbers, and add no rungs.)*

**F-OAL is the headline of this thread.** It is *forward-only* (no backward pass anywhere — our P2.5 envelope), *online*
(per-batch streaming — our stream), and *analytic* (recursive least squares — no gradient, substrate-native). If any
single published method is "the namer we were about to reinvent," it is this one. We adopt its **mechanism** (a
recursive-least-squares analytic head on forward-only features), not its ViT-scale numbers.

**The honest substrate caveat (don't let "closed-form" hide it).** The RLS solve is over the **projected feature
dimension**. RanPAC/RanDumb *expand* dimensionality (random projection to 10k+) for separability → the Gram matrix and
its solve grow **quadratically** in that dimension. On a pretrained ViT this is free (offline); on our substrate a big
projection is a **big crossbar + a big solve** = real Scap + ADC + digital-solve cost. So the analytic head is
substrate-native in *form* (running second moment) but its *size* is a Phase-8 cost question — a modest projection may
suffice on our 64-wide features, or the expansion may be exactly what earns separability. **Meter it, don't assume it.**

## Thread 2 — FeCAM: the closed-form answer to multimodality (and the max-magnitude pole)

**FeCAM** (NeurIPS 2023, [2309.14062](https://arxiv.org/abs/2309.14062)) is the rough plan's missing P7.2 answer.
Its thesis: on a frozen backbone, **feature distributions are heterogeneous** (per-class shape differs), so the Euclidean
NCM metric is suboptimal. Fix: model **per-class covariance** and classify by **anisotropic Mahalanobis distance** (a
Bayesian/Gaussian classifier). Result: **without touching the backbone**, SOTA exemplar-free CIL — CIFAR-100/5-task
**70.9%** (per-class covariance) vs FeTrIL 67.6% vs **Euclidean NCM 64.8%** — i.e. the covariance term is worth ~+6 pts
over plain NCM, and later benchmarks report FeCAM "outperforming all others by a large margin."

**Why this matters for us two ways, in tension:**
- **(the good)** It *reframes P7.2's cliff.* The rough plan said: if a class is multi-modal, the fallback is "a few
  prototypes = a **non-convex mixture** → the clean convex story evaporates." FeCAM says there is a **closed-form**
  middle option — one Gaussian *with a shaped covariance* per class — that captures heterogeneity **without** a
  non-convex mixture and **without** gradient. (And GKEAL's kernel is the closed-form *fully-nonlinear* escape if even
  that underfits.) So the multimodality fallback ladder is now: `one mean → tied covariance (SLDA, one shared matrix) →
  per-class covariance (FeCAM, C matrices) → kernel (GKEAL) → few-prototype mixture (non-convex, last resort)` — with
  **Deep SLDA the cheaper middle** climbed before FeCAM's full per-class cost.
- **(the tension — the spine)** FeCAM is the **maximal-magnitude** readout on the table. Mahalanobis distance in a
  covariance-**whitened** space is a magnitude *and* whitening was **rejected-as-a-lever in Phase 5**. So FeCAM is the
  *sharpest anti-spine pole*: if it wins accuracy×BWT but the direction-pure cosine head is close, the bake-off's central
  question gets its teeth — **do we take the spine-clean head and eat a small accuracy cost, or does the spine bend
  here?** That is a decision for the author, informed by the number — exactly the tension Phase 7 exists to surface.

## Thread 3 — RanDumb: the skeptic's control that tests whether the bulk earns its keep

**RanDumb** ("Random Representations Outperform Online Continually Learned Representations," 2024,
[2402.08823](https://arxiv.org/abs/2402.08823)) is a *provocation*: a **fixed random projection + a simple
(Mahalanobis/NCM) classifier** *outperforms* representations learned online by continual-learning methods, on standard
benchmarks. For most of the field it's a cautionary tale; **for us it is the single most useful control in Phase 7**,
because it operationalizes the hedge we already wrote down:

> *We are reservoir-**like**, not a reservoir proper — a trained-then-frozen bulk, not a random one. We inherit readout
> convexity but must **prove** the trained bulk beats a random projection at the readout, or the 80% didn't earn its keep.*

RanDumb IS that test. **P7 must run a random-projection control, in TWO arms** (the lab-manager review sharpened this —
"matched output dim" alone underpowers the skeptic, and RanDumb-proper randomizes from *raw pixels*, not from a learned
representation): **(a) random-from-taps** — a random projection of the SCFF *tap output* at a **fair expansion** + the
same downstream head (the fair "did the bulk's *representation* beat a random one of the same input the readout sees");
**(b) random-from-pixels** — a random projection of the *raw input* (true RanDumb — the harsher "did the 80% earn its
keep *at all*"). If our trained bulk + best readout does **not** beat these on the continual home, the 80% SCFF is not
pulling its weight *at the naming stage* — a load-bearing, falsifiable check the rough plan omitted. (It ties straight
back to Phase 4's A2/A3 "the bulk composes class-relevant depth" claim — this is that claim, re-asked at the readout; and
per the review, a tie on the *flat home* is **not** pre-excused as "composition, move on" — it must be reported as
"naming-stage value unverified," flagged to Stage 2.)

---

## What it means for us — the audit verdict + the widened bake-off

**Did the rough research cover it? No.** It had the spine right (cosine = direction-pure; NCM/RanPAC = recency-robust
magnitudes) and the convexity right, but its *candidate set was a subset* of what "cheat everything" demands. The delta:

1. **Add the Analytic/RLS family — headed by F-OAL (forward-only + online + no-gradient).** This turns the "no-gradient
   streaming namer" from a *hopeful bet* into *adopting a published, on-constraint paradigm.* RanPAC becomes **one
   point** in this space, not the whole no-gradient story. **This is the biggest change to the plan.**
2. **Add FeCAM (per-class covariance) — the closed-form multimodality escape AND the max-magnitude spine pole.** It
   removes P7.2's "non-convex or bust" framing and *sharpens* the spine bake-off.
3. **Add GKEAL (kernel) as the closed-form non-linear fallback** below FeCAM on the multimodality ladder.
4. **Add the RanDumb control** — does the trained bulk beat a random projection at the readout? (The reservoir hedge,
   made an experiment.)
5. **Keep everything the rough pass had.** Cosine stays the spine candidate; linear-softmax stays the convex floor;
   `race_bp` + a small MLP head stay the "if we DID pay real GD" upper anchors (the achievable ceiling — the old-world
   discipline); the magnitude-bias fixes (BiC/WA/SCR/logit-adjust) stay the imbalance toolkit.

**The widened bake-off, as a taxonomy (the naming families, one axis = spine-purity):**

| family | members | gradient? | spine status | substrate note |
| --- | --- | --- | --- | --- |
| **gradient heads (the "if we paid GD" anchor)** | linear-softmax (convex floor) · small MLP (non-convex) · `race_bp` (BP ceiling) | yes | magnitude (linear) | the achievable reference, not the target |
| **direction-pure** | **cosine** head · cosine-margin (north-star seed) | optional | **spine-clean** ✓ | needs an L2-normalizer block |
| **distance / magnitude prototypes** | NCM (Euclidean) · **FeCAM** (per-class Mahalanobis) | no | magnitude (FeCAM = max) | running mean (+ per-class cov for FeCAM) |
| **analytic / RLS (closed-form streaming)** | **RanPAC** (rand-proj + ridge) · **ACL/RLS-ridge** · **F-OAL** (fwd-only online) · GKEAL (kernel) | no | magnitude (ridge/Gram) | running Gram + solve; proj-dim = cost |
| **controls** | **RanDumb** (random-proj + readout) · the convex floor | — | — | the "does the bulk earn its keep" skeptic |

**The bet, restated with the wider field (sharper than the rough version):** *the strongest no-gradient namers in the
field are **magnitude-based** (FeCAM Mahalanobis, RanPAC/RLS ridge). The spine says read **direction**. Phase 7's
headline question is whether the **direction-pure cosine head matches the accuracy×forgetting of the field's
magnitude-based no-gradient SOTA — and if not, how big is the price of staying spine-clean.** Plus the control that keeps
us honest: does any of it beat a **random projection** (RanDumb) — i.e. did the 80% SCFF earn its keep at the naming
stage?* If cosine (or an analytic head) wins or ties, **the 20% is not even gradient descent** — cheaper, continual-safe,
and (for cosine) spine-aligned. That is the 🔥 Phase-7 result.

**Citation hygiene (RESOLVED in the lab-manager literature review — these IDs now bank):**
FeCAM **2309.14062** (NeurIPS 2023); RanDumb **2402.08823**; **F-OAL = AOCIL = 2403.15751** (NeurIPS 2024 — *one paper*,
v1 "AOCIL" → v2 "F-OAL"; the first-pass double-count is fixed); **ACIL = 2205.14922** (NeurIPS 2022); **Deep SLDA
1909.01520** (CVPRW 2020); **AIR 2408.10349**; DS-AL 2403.17503; GACL/G-ACIL 2403.15706; REAL 2403.13522; AnaCP
2511.13880; **GKEAL** CVPR 2023 (**few-shot** CIL, CVF-only — **no arXiv**; cite venue + the family repo
`ZHUANGHP/Analytic-continual-learning`). None is load-bearing as a *result* (we adopt mechanisms), but every ID a card
cites now resolves.
