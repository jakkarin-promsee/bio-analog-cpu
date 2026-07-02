# P7.1 — the readout bake-off: naming the frozen bulk  *(THE headline)*

**Inheriting** the pinned all-tap tap-feature source, `PROBE_EP=120`, the convex floor (0.608) and static ceiling
(0.866) from P7.0. **Question.** Across the namer taxonomy, where does accuracy×BWT peak on the direction→magnitude
axis, and what does spine-cleanliness cost? Concretely: does the spine-clean **cosine** head match the accuracy×
forgetting of the magnitude-based no-gradient SOTA (FeCAM / SLDA / RanPAC-RLS), or do we pay a price to stay
spine-clean?

**Setup (one variable = the readout head).** Nine heads race the **same frozen all-tap taps** on the synthetic
class-incremental home; each head's knob is lightly selected on a held-out val split (the `race_bp` fairness protocol,
recorded per head). Scored on static **acc** + **AAA**, continual **AA / BWT / forget** (via the shared `stream_cache`,
one bulk training per seed), **spine-cleanliness** (a) argmax-flip under per-class norm rescale + (b) old-class drop
under the actual bursty stream, and **cost-proxy** (descriptive-only). Cosine is **two heads** (ncm = no-gradient;
softmax = gradient). Seeds ×5 (verdict gap Δ≫0.02 ⇒ no 9-seed extension needed). Wall 54.6 min.

**Run.** 9 heads × 5 seeds, checkpointed, single-thread; guards inherited-green from P7.0.

**Result / figures.** *(synthetic CI home, n=5, median [q25–q75])*

| head | acc | AA | BWT | spine-flip@2 | recency | cost-proxy | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear-softmax (floor) | 0.591 [.591–.595] | 0.584 [.570–.594] | −0.181 | 0.684 | 0.181 | 7.7e3 | the floor |
| **cosine-ncm** (spine-pure, no-grad) | 0.262 [.260–.263] | 0.319 [.298–.336] | −0.142 | **0.000** | 0.142 | 7.7e3 | spine-clean but sub-floor (greyed) |
| **cosine-softmax** (spine-pure, grad) | 0.537 [.531–.547] | 0.480 [.478–.490] | −0.234 | **0.000** | 7.7e3 | 0.234 | spine-clean, competitive-ish, but trails |
| NCM (Euclidean) | 0.264 [.261–.267] | 0.331 [.307–.346] | −0.157 | 0.577 | 0.157 | 7.7e3 | magnitude, sub-floor (greyed) |
| SLDA (tied cov, no-grad) | 0.583 [.574–.611] | 0.604 [.600–.613] | −0.162 | 0.893 | 0.162 | 7.7e3 | top-cluster AA, **most norm-sensitive** |
| FeCAM (per-class cov, no-grad) | 0.531 [.503–.534] | 0.459 [.451–.462] | −0.302 | 0.764 | 5.9e6 | 0.302 | max-magnitude pole; **worst BWT** |
| **RanPAC** (proj+ridge, no-grad) | **0.647 [.640–.653]** | **0.617 [.616–.619]** | −0.157 | 0.537 | 1.6e6 | **top acc + top-cluster AA; committed** |
| RLS (ridge, no proj, no-grad) | 0.623 [.609–.635] | 0.558 [.550–.574] | −0.197 | 0.561 | 7.7e3 | analytic, no proj — below RanPAC |
| MLP head (non-convex, grad) | 0.625 [.615–.641] | 0.623 [.615–.627] | −0.147 | 0.604 | 2.5e4 | top-cluster AA (the "if we paid GD" anchor) |

**Verdict cut (§2, blind).** `Δ = the paired-by-seed median of [AA(ranpac) − AA(cosine-softmax)] = +0.128` (per-seed
diffs [0.136, 0.109, 0.153, 0.129, 0.122]; head medians AA 0.617 vs 0.480), **real** (paired IQR excludes 0, sign 5/5),
`|Δ| > δ=0.02` → **magnitude-wins-spine-bends**, and the mechanism
condition holds: the winning magnitude head (RanPAC, BWT −0.157) is **not** more fragile than cosine (BWT −0.234) under
the bursty stream — it is recency-robust by having no trained softmax weights.

- **BAKEOFF** (headline): the accuracy×BWT frontier peaks in a **statistical three-way tie** — MLP (0.623), **RanPAC
  (0.617)**, SLDA (0.604), all within noise (mlp−ranpac +0.007 not real; ranpac−slda +0.004 not real). Two of the top
  three are **no-gradient**. Cosine sits well below the frontier. - **SPINE-CLEAN**: cosine flat at **0.000** flips
  across the whole perturbation grid; every accuracy-competitive head flips (RanPAC 0.537 least, SLDA 0.893 most). -
  **COST-PROXY** (descriptive; real=P8): RanPAC 1.6e6 ≫ SLDA/RLS 7.7e3 (the 2000-D projection). - **INV**: dead-frac 0,
  feat-pinned ✓.

**Read (8 slots).**
1. **Claim** — the accuracy×BWT frontier is led by a **statistical tie of MLP, RanPAC, and SLDA**; the best is a
   **no-gradient analytic head (RanPAC)** — it has the highest static accuracy (0.647) and ties the gradient MLP anchor
   on AA (within noise) while being the more spine-clean of the tied cluster. **The 20% need not be gradient descent.**
   The spine-pure cosine head is **not** competitive on all-tap SCFF features (AA 0.480, −0.128 vs RanPAC).
2. **Headline** — RanPAC AA **0.617 [0.616–0.619]** vs MLP 0.623 [0.615–0.627] (tie), SLDA 0.604 (tie), cosine-softmax
   0.480 [0.478–0.490] (−0.128), above the convex floor 0.584, below the static BP ceiling 0.866 (n=5, synthetic CI
   home, PROBE_EP=120).
3. **Figures** — BAKEOFF (frontier three-way tie, cosine below), SPINE-CLEAN (cosine flat at 0; competitors flip),
   COST-PROXY (RanPAC dear — proxy, real=P8), CONT-SAFETY (BWT bars), INV. Regen from `arrays.npz`.
4. **Mechanism** — the spine bends **here**, with the mechanism made explicit: (i) the direction-pure cosine cannot
   compete because the all-tap SCFF space is anisotropic (P7.2: a tied-covariance *whitening* buys +0.19 on natural
   data) — an angle-only metric leaves that structure on the table; (ii) the winning magnitude heads dodge the continual
   *recency* bias not by reading direction but by **having no trained softmax weights to inflate** (RanPAC/SLDA are
   closed-form; their BWT ≈ the floor, far better than a plain trained-softmax); (iii) **the projection earns its keep**
   — RanPAC (proj+ridge) beats RLS (ridge, no proj) by +0.047 (real, 5/5), so at our scale the random expansion adds
   separability (the H-analytic hedge resolves *for* the projection here).
5. **Threats** — (a) cost flattering the no-gradient winner → cost is **descriptive-only**, tagged (proxy; real=P8), and
   RanPAC is in fact the **most expensive** competitive head (it wins *despite* cost, not because of it); (b) a synthetic
   artifact → P7.5 re-runs on digits + CIFAR-flat; (c) the tie mis-called → checked paired (mlp/ranpac/slda mutually
   within-noise, sign 0.60); (d) cosine under-tuned → its argmax is τ-invariant for NCM and τ was selected for softmax,
   so 0.480 is its real ceiling here, not a tuning miss.
6. **Decision** — **committed namer candidate = RanPAC** (analytic, no-gradient), by: maximizes acc×BWT (tied top),
   and, at the tie, is the most spine-clean of the competitive heads (flip 0.537). **SLDA is a within-noise, ~200×
   cheaper no-gradient alternative** (flip 0.893, norm-sensitive) — flagged to P8 as the cost/spine trade. **Pending the
   P7.4 A6 gate** (adoption is not final until the gate passes). P7.3 (imbalance) + P7.5 (natural) carry RanPAC + SLDA.
7. **Spine-honesty** — spine-cleanliness was **measured** ((a) argmax-flip + (b) recency-drop), not assumed: cosine is
   the only argmax-flip-0 head, and it is **sub-competitive**, so the tension is named, not resolved silently toward
   accuracy. No magnitude head was called "the spine": RanPAC/SLDA/FeCAM read a ridge/Mahalanobis = a magnitude; they
   are *recency-robust*, which is **not** direction-reading. Cost tagged proxy; RanPAC's win is not a cost artifact.
8. **Namer-verdict / continual-safety** — spine-tension branch = **magnitude-wins-spine-bends** (Δ=0.128, δ=0.02,
   mechanism above); cheat-everything read = **the committed namer is closed-form/streaming analytic, NOT gradient
   descent** (the 🔥 headline, modulo the P7.4 gate). **A6 gate NOT yet checked → P7.4 gates adoption of RanPAC.**

**Pre-submit checklist.**
- [x] Median [IQR] every headline number (n=5); no bare means.
- [x] "Real difference" rule applied (Δ paired IQR-disjoint + 5/5 sign; top-cluster ties confirmed not-real).
- [x] Static figures draw the convex floor + static BP ceiling; ceiling **not** on the BWT/CONT-SAFETY figure.
- [x] Spine-cleanliness measured ((a) flip + (b) recency); interpreted only for accuracy-competitive heads (cosine-ncm/ncm sub-floor → greyed); cosine≈0 flips confirmed.
- [x] Cost tagged **PROXY, descriptive-only** (real=P8); cost **never** a tie-break (RanPAC wins the spine tie-break despite being dearest).
- [x] Feature source loaded from the pinned P7.0 config; `PROBE_EP=120` frozen; feat-pinned INV green.
- [x] Verdict branch matches its numeric cut (§B): Δ=+0.128 real >δ → magnitude-wins-spine-bends.
- [x] Spine reported alongside accuracy; the tension named (cosine spine-clean but sub-competitive).
- [x] Every figure by a `plot_p7.fig_*` function; regen redraws from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (pinned taps + floor/ceiling).
- [x] `manifest.json` + `arrays.npz` written; per-head selected knobs recorded.
- [x] Single-threaded; no sklearn for compute.
- [x] **A6 continual-safety (P7.4) verdict flagged** for the committed head (RanPAC) — not yet gated.
- [x] `RESULTS.md` row added.
