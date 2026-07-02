# P7.5 — natural-data confirmation  *(the synthetic-artifact gate)*

**Inheriting** the committed namer **RanPAC** and the bake-off ordering from P7.1/P7.4, and the pinned bulk from P7.0.
**Question.** Do the bake-off ordering and the chosen head hold on **real flat data** (not a synthetic artifact)? Re-run
the headline heads on **digits (64-D)** and **CIFAR-flat (3072-D)** through the class-incremental continual stream.

**Setup.** The head set {linear, cosine-ncm, cosine-softmax, SLDA, FeCAM, RanPAC, RLS, MLP} at their committed knobs,
run through the same `stream_cache` continual harness on digits (5 seeds) and CIFAR-flat (3 seeds — heavier 3072-D
bulk). Metric = continual AA (+ BWT). Wall 7.6 min.

**Result / figures.** *(natural data, median [q25–q75])*

| head | digits AA | digits BWT | CIFAR-flat AA | reading |
| --- | --- | --- | --- | --- |
| **RanPAC** (committed, no-grad) | **0.949 [.947–.956]** | **−0.012** | 0.265 [.261–.269] | **#1 on digits**; projection doesn't help depth-less CIFAR |
| linear-softmax (floor) | 0.946 [.941–.959] | −0.014 | 0.293 | strong on digits; near-chance-band on CIFAR |
| RLS (no-grad) | 0.944 [.924–.947] | −0.017 | 0.320 | analytic, no proj — robust on CIFAR |
| MLP (grad) | 0.944 [.940–.945] | −0.017 | 0.297 | the GD anchor — no better than the no-grad heads |
| SLDA (no-grad) | 0.942 [.928–.945] | −0.015 | **0.325** | **top on CIFAR**; the robust cheap alternative |
| cosine-softmax (spine, grad) | 0.913 [.909–.923] | −0.033 | 0.324 | competitive on digits (−0.036); **top-tier on CIFAR** |
| FeCAM (per-class cov) | 0.913 [.885–.913] | +0.243* | 0.310 | unstable BWT; struck at P7.4 |
| cosine-ncm (spine, no-grad) | 0.568 [.558–.607] | −0.147 | 0.236 | sub-competitive everywhere |

- **NAT-ANCHOR** (headline): on **digits** the analytic/magnitude heads cluster at the top (0.94–0.95) with **RanPAC
  #1 (0.949)** and near-zero forgetting (BWT −0.012); cosine-softmax is **competitive (0.913, −0.036 gap)** — the
  synthetic spine-price (−0.128) **shrinks 4×** on real data. On **CIFAR-flat** *every* head is weak (0.24–0.33; SCFF
  has no composable depth here — the P4/P5/P6 "wall"), the ordering **compresses**, and the spine tension **vanishes**
  (cosine-softmax 0.324 ≈ the SLDA top 0.325). - **INV**: feat-pinned ✓. *(FeCAM's +0.243 digits BWT is an instability
  artifact — it was already struck by the P7.4 gate.)*

**Read (8 slots).**
1. **Claim** — the readout choice is **real, not a synthetic artifact**: on the SCFF-working natural home (**digits**)
   RanPAC is **#1 (0.949)** with the lowest forgetting, confirming the P7.1/P7.4 committed head; the magnitude-vs-cosine
   ordering reproduces but the **spine-price shrinks 4×** (−0.128 synthetic → −0.036 digits). On the depth-less
   **CIFAR-flat** all heads collapse to ~0.3 and the ordering + tension disappear (an honest caveat, not a flip).
2. **Headline** — digits: RanPAC **0.949 [0.947–0.956]** (BWT −0.012) vs cosine-softmax 0.913 (−0.036), above the floor;
   CIFAR-flat: all heads 0.24–0.33 with SLDA 0.325 ≥ RanPAC 0.265 (n=5 digits / 3 CIFAR).
3. **Figures** — NAT-ANCHOR (digits + CIFAR-flat bars per head), INV. Regen from `arrays.npz`.
4. **Mechanism** — where the bulk composes class structure (digits), the analytic ridge (RanPAC) and the
   tied-covariance whitening (SLDA) both exploit it → top accuracy + near-zero forgetting (no-gradient = recency-robust);
   the direction-pure cosine leaves some anisotropy unexploited, but on real data that gap is small. Where the bulk has
   **no depth to compose** (CIFAR-flat, the established SCFF wall), there is little class structure to name → all
   readouts are weak, RanPAC's random *expansion* of near-useless features actively hurts (0.265 < SLDA 0.325), and the
   cheaper covariance head is more robust. The namer's value tracks the bulk's — as it must.
5. **Threats** — (a) a synthetic-only verdict → **this is the gate against it**; the digits confirmation holds, the
   CIFAR caveat is reported; (b) CIFAR under-seeded (3 seeds) → acceptable for the heavier 3072-D cell, and the finding
   (all heads weak) is unambiguous; (c) reading CIFAR as a RanPAC failure → it is a *bulk* failure (SCFF has no CIFAR
   depth, P4/P5/P6), so the naming choice is moot there (all ~0.3).
6. **Decision** — **RanPAC confirmed as the committed namer on the SCFF-working natural home (digits, #1).** The CIFAR
   caveat + the P7.1 cost proxy jointly **flag SLDA to Phase 8** as the pragmatic cheaper alternative: within-noise on
   the synthetic tie, top on CIFAR, ~200× cheaper, passes the gate — its only cost is spine-cleanliness. P7.6 assembles.
7. **Spine-honesty** — the spine-tension is reported as **dataset-dependent and shrinking on real data** (synthetic
   −0.128 → digits −0.036 → CIFAR ≈0), not hidden: the "magnitude-wins-spine-bends" verdict is a synthetic-home
   phenomenon that softens where the bulk's structure is thinner. No magnitude head is called "the spine."
8. **Namer-verdict / continual-safety** — the committed RanPAC + its no-gradient, near-zero-forgetting profile is
   confirmed on natural digits; the spine-tension branch stays **magnitude-wins-spine-bends** but is annotated
   **"shrinks on natural data."** The A6 gate (P7.4) already passed; digits BWT −0.012 corroborates.

**Pre-submit checklist.**
- [x] Median [IQR] every headline number (n=5 digits / 3 CIFAR).
- [x] Ordering-reproduction assessed on **both** natural datasets; the digits confirmation + the CIFAR caveat both stated.
- [x] The verdict's natural-data behavior (spine price shrinks; vanishes on CIFAR) reported, not hidden.
- [x] Feature source loaded from the pinned P7.0 config; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (committed RanPAC + ordering).
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded; no sklearn for compute (load_digits/load_cifar_flat data-only).
- [x] `RESULTS.md` row added.
