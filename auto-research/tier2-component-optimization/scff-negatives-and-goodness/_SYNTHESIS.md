# Synthesis — SCFF negatives & goodness objectives  (Tier 2, t2.1)
**The question:** For the SCFF bulk specifically, what has the literature tried that we have NOT — better negative generation, goodness functions beyond `Σh²`/fixed-temp InfoNCE, forward-only collapse prevention, negative-free training — that could improve representation quality or delete the negative-supply hardware risk, while staying local + forward-only + label-free?

**Already in `draft6.0/research/`:** the phase3 set covers the objective-*family* question (energy vs predictive/contrastive: GIM, CLAPP, the Jan-2026 local-SSL benchmark, LoCo, OLU/Trifecta, Layer-Collaboration, Mono-Forward, SoftHebb, PFF, CaFo one-liner, BiCovG one-liner). This sweep's tier1 already cards SymBa, CaFo, ASGE, PFF (t1.1) and **MinRed/Purushwalkam 2022** (t1.7 — the negative-buffer eviction answer for topic item (f); not re-carded here). This topic goes *inside* the contrast family: which negatives, which scalar, which anti-collapse term.

## The landscape (the four camps)

**Camp 1 — fix the goodness scalar.** The field has stopped treating `Σh²` as a given. A 21-function benchmark (Shah 2025) shows margin-shaped and competition-shaped goodness reliably dominate raw energy, with dataset-dependent winners. Distance-Forward (Wu 2024) makes the deeper diagnosis: the binary goodness question wastes the layer's geometry — replace it with distance-to-centroid metric learning. The 2026 free-riding paper (Yousefiramandi) adds the pathology map for *cumulative/coupled* goodness: once upstream margin accumulates, downstream gradient decays exponentially (repairable locally; barely moves accuracy). Temperature-free InfoNCE (Kim 2025) deletes the τ knob via an artanh reparameterization of cosine similarity.

**Camp 2 — fix the negatives.** Random negatives waste most of the contrast budget: Robinson (ICLR 2021) tilts the *existing* negative pool toward hard (anchor-similar) items by importance-weighting terms already computed — zero overhead — with a debiasing correction so false negatives (same-class impostors, i.e. our autocorrelated-stream case) don't poison it. MinRed (tier1 card) attacks the same supply from the eviction side.

**Camp 3 — make negatives implicit (resident memory, not data).** Distance-Forward's class centroids, HFF's unit-norm prototypes (Sarode 2026): a **resident prototype bank is the negative set** — nothing is generated, fetched, or corrupted; the "fake world" is a memory read. Both are supervised, but the structure is label-agnostic.

**Camp 4 — delete negatives entirely (statistics instead of contrast).** Layer-wise VICReg (Datta 2025, Sci Reports): variance + invariance + covariance terms per layer, two forward passes (original + augmented), fully local, label-free, **no negatives**. Stochastic FF (Zhu 2025) is the same logic made spectral and noise-native: compress the effective dimensionality of noisy copies of one input, expand it across the stream — noise *is* the second view. CwComp (AAAI 2024) deletes negatives via intra-layer class-group competition, but pays with labels.

## How WE differ  ← the money section

Our cell (summation-InfoNCE, temp 0.2, window w2, one iid-noise view, uniform random-partner LUT negatives) sits in the *contrast* camp with the **most naive possible negative policy**. What's genuinely ours: the cross-layer window as the depth mechanism, the continual-safety gates (A6/BWT) as first-class objective constraints — no paper here evaluates its goodness variant under continual/streaming safety — and the substrate energy accounting. What's a re-invention: our noise-augmented view is Zhu's mechanism at n=2; our "one view, corrupt it" is standard. The gap: **every one of our negative-supply choices (uniform draw, equal weighting, raw samples not prototypes, fixed τ) has a published, cheap, tested upgrade we have not run.** And the whole negative path itself now has a credible label-free, local, forward-only *deletion* (VICReg-lite / ED-goodness) that nobody has tested under continual constraints — our home turf.

## The gap / what we haven't tried (ranked by expected benefit × substrate-fit)

1. **LUT-prototype negatives + hardness tilt** (Camps 2+3 merged; Wu + Sarode + Robinson triangulate on it). Negatives = k nearest LUT prototypes (excluding own cluster), and/or importance-weight existing partners by similarity. *Substrate-fit: excellent* — the LUT already exists; the tilt is one multiply on an already-computed similarity; no new rails. Risk: false-negatives on autocorrelated streams → include Robinson's debiasing. This is the cheapest untested win.
2. **VICReg-lite negative-free bulk** (Camp 4). Swap the InfoNCE denominator for per-unit variance floor (EMA accumulator) + keep the two-rail invariance term; stage the covariance term separately (D×D estimate = the expensive part; note a crossbar computes Gram products natively). *Substrate-fit: good for variance+invariance, open for covariance.* Prize: deletes the negative supply chain as an organ — the biggest architectural simplification on the table. Must pass the depth-composition and A6 continual gates that the published version was never tested against.
3. **Temperature-free (artanh) logits** (Camp 1). One-variable swap vs temp-0.2 on the frozen P5 cell. *Substrate-fit: excellent* — replaces a precision-held analog bias with a fixed monotone nonlinearity. Also re-explains P5's "sharpness" mechanistically.
4. **Margin term on the contrast** (Camp 1, Shah's most reliable shaping). One-line addition; run as a bake-off *inside* the contrast family (summation-InfoNCE vs N-pair-margin vs triplet-margin), which P3 never did — P3 compared families.
5. **Free-riding diagnostic on the window** (Camp 1 pathology). Condition per-layer selectivity on upstream margin in w2/w4 stacks; if the signature shows, the hardness-gate remedy is one comparator. Low expected accuracy gain (their own result) — hygiene, not headline.
6. **k>2 noisy rails / temporal noise averaging** (Camp 4, Zhu). Our substrate gets noisy copies for free; we've never priced using more than two. Design-note tier, not experiment tier, until 1–2 land.

**What stays local+forward-only on the crossbar:** 1, 3, 4, 5 unconditionally; 2 with the covariance term deferred or crossbar-native; 6 by construction. **What doesn't:** CwComp/HFF/Distance-Forward as published (label-indexed structures in the bulk) — only their *structural* moves port.

## Papers (table linking the cards)

| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Wu 2024 — Distance-Forward](wu-2024-distance-forward.md) | ⭐⭐⭐⭐⭐ | Goodness → distance-to-resident-centroids, framed for on-chip; negatives become a memory read |
| [Datta 2025 — Layer-wise VICReg](datta-2025-layerwise-vicreg.md) | ⭐⭐⭐⭐⭐ | The negative-FREE local label-free objective — the existence proof for deleting our negative supply |
| [Robinson 2021 — Hard negatives](robinson-2021-hard-negatives.md) | ⭐⭐⭐⭐ | Zero-overhead hardness reweighting of the negatives we already draw (+ the false-negative debias) |
| [Kim 2025 — Temperature-free InfoNCE](kim-2025-temperature-free-infonce.md) | ⭐⭐⭐⭐ | Deletes the τ=0.2 knob via artanh(sim); one fewer analog bias |
| [Shah 2025 — Goodness benchmark](shah-2025-goodness-benchmark.md) | ⭐⭐⭐⭐ | 21-way proof that Σh² is dominated; margin-shaping is the reliable win |
| [Yousefiramandi 2026 — Free-riding](yousefiramandi-2026-cumulative-goodness-freeriding.md) | ⭐⭐⭐⭐ | The exponential-decay pathology of coupled goodness + three local remedies + the diagnostic |
| [Zhu 2025 — Stochastic FF / ED goodness](zhu-2025-stochastic-ff-dimensionality.md) | ⭐⭐⭐⭐ | Noise as the second view; second-order (ED) anti-collapse; negative-free |
| [Sarode 2026 — Hyperspherical FF](sarode-2026-hyperspherical-ff-prototypes.md) | ⭐⭐⭐ | Resident unit-norm prototypes as implicit negatives; single-pass update+inference |
| [Papachristodoulou 2024 — CwComp](papachristodoulou-2024-cwcomp.md) | ⭐⭐⭐ | Negative-free via intra-layer competition — but label-paid; sharpens where the open problem actually is |

## Leads spawned
- **Debiased contrastive learning** (Chuang 2020, 2007.00224) — the false-negative correction; prerequisite for lever 1 on autocorrelated streams.
- **Hard-negative mixing / MoCHi** (Kalantidis 2020) — *synthesizing* negatives by interpolating LUT entries; a possible generator organ.
- **Barlow Twins / CorInfoMax as crossbar-native decorrelation** — is the cross-correlation-to-identity term computable *in* the crossbar (Gram products are its native op)?
- **Temperature schedules on long-tail/streaming data** (Kukleva 2023, 2303.13664) — τ as a wake/sleep-modulated signal rather than a constant.
- **ED / participation ratio as a run invariant** — upgrade the dead-unit-fraction check to a spectral collapse monitor.
- **Fixed-anchor geometry (ETF/fixed classifiers)** — do prototype anchors need to learn at all?
