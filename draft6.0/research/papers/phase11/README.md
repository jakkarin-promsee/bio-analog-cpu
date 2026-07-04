# Phase 11 papers — the limit-map slice (real data · scale · the decomposition)

> The literature Phase 11 stands on, written as the deep-research delta answering the author's question:
> **"did our earlier rough plan cover all of Phase 11, and is there a better choice?"** (2026-07-04.) Phase 11 takes
> the P10 instrument to harder/real data and to scale — so this slice is about **which arenas the field recognizes**,
> **which protocols are canonical**, and **which published numbers anchor our instrument**. The P10 canon
> ([`../phase10/README.md`](../phase10/README.md) — budgeted-CL, real-time eval, AAA, three scenarios, the baseline
> family) carries unchanged; this file adds only the P11-new legs.
>
> **Verdict up front:** the rough plan (temp2 → the staged concept) was **directionally right and materially
> incomplete in seven places** — D1–D7 below, all folded into [`design.md`](../../../src/phase11/design.md).

---

## 0 · The seven deltas the research changed

- **D1 — the cross-dataset gauntlet has a canonical name and cite: "5-Datasets."** Sequentially learning *entirely
  different datasets* (CIFAR-10, MNIST, SVHN, Fashion-MNIST, notMNIST — ~10 classes each) is an established CL
  benchmark, canonical cite **Ebrahimi et al., *Adversarial Continual Learning*, ECCV 2020
  ([2003.09553](https://arxiv.org/abs/2003.09553))**; the field runs it mostly **task-IL** (task identity given at
  test). Ours is a **3-block variant at our scale** (MNIST → Fashion-MNIST → CIFAR-10-gray, the box-loadable three)
  run **class-IL** (single growing head, 30 classes, no task oracle) — *harder* than the field's convention, stated
  as such. The rough plan's class-IL guess is confirmed as the right honest choice; the protocol family exists and
  is nameable — outside legibility for free.
- **D2 — Electricity carries a published trap: label autocorrelation.** On ELEC2 a **no-change (persistence)
  classifier** — predict the previous label — scores ≈ 85%, beating many learners (Souza et al. 2020, *Challenges in
  Benchmarking Stream Learning Algorithms with Real-world Data*, DAMI). **Adopted: the no-change baseline is a
  mandatory sanity line on every real-world stream**; any cell where a method fails to beat persistence renders as
  FLOOR/uninformative, never as a win. This is the streaming community's own anti-hype guard — running it protects
  the map from the poke every stream-mining reviewer knows.
- **D3 — the gas-drift dataset has a published limitations paper; cite it preemptively.** Dennler et al. 2022
  (*Drift in a popular metal oxide sensor dataset reveals limitations for gas classification benchmarks*, Sensors &
  Actuators B, [S0925400522003100](https://www.sciencedirect.com/science/article/pii/S0925400522003100)): batch/
  run-order artifacts; prior drift-compensation results often lack statistical validation. Consequences adopted:
  per-batch **class-composition table printed into the manifest at bench** (batches are heavily imbalanced; batch
  sizes ≈ {445, 1244, 1586, 161, 197, 2300, 3613, 294, 470, 3600} — verify at bench), **balanced accuracy** as the
  read, and the two standard protocols named (batch-1→rest = the lab setting; cumulative 1..n−1→n = the online
  setting; ours = the time-ordered *stream*, the online analogue, reported per-batch). Original dataset + ensemble
  baseline: **Vergara et al. 2012, *Chemical gas sensor drift compensation using classifier ensembles*** (anchor
  numbers transcribed into the manifest at bench, before our runs).
- **D4 — two real-world arenas the rough plan missed, both box-feasible.** (a) **Wild-Time Yearbook** (Yao et al.,
  NeurIPS 2022 D&B, [2211.14238](https://arxiv.org/abs/2211.14238)): 33,431 **32×32×1 grayscale** US yearbook
  portraits, 1930–2013, binary gender — **real-world VISION drift across eight decades**, needing no backbone and no
  RGB; streamed by year/decade it is the vision twin of the gas stream. (b) **MedMNIST v2** (Yang et al., Sci Data
  2023, [2110.14795](https://arxiv.org/abs/2110.14795)): the famous lightweight biomedical benchmark, 28×28 **npz**
  downloads (BloodMNIST 8-class ≈ 17k the natural pick). Adopted: Yearbook = the E2 vision leg (declared bonus,
  gated on the download landing); BloodMNIST = an optional E1 bonus rung (declared bonus). Neither gates the phase.
- **D5 — the ER instrument-validation anchor source is pinned.** **van de Ven, Tuytelaars & Tolias 2022, *Three
  types of incremental learning*, Nature Machine Intelligence** (scenarios origin: [1904.07734](https://arxiv.org/abs/1904.07734))
  + the official reference implementation (`GMvandeVen/continual-learning`) publish Split-MNIST ER numbers per
  scenario. Adopted: an **E-anchor cell** — our ER-strong runs Split-MNIST (class-IL + domain-IL) at a published
  buffer size; the published band is transcribed into the manifest **before** our run; our ER must land in it or
  the instrument is flagged. Scope (per the lab-manager review, design §8 R4): this retires *implementation-bug*
  strawman claims; per-arena strength is enforced separately (the pinned tuning grid + the dominance guard).
- **D6 — openml IDs pinned (and one wrong-variant trap).** Fashion-MNIST = **40996** (70k × 784, ARFF); Electricity
  = **151** (v1 — the canonical **45,312-row chronological** ELEC2; the "balanced" v2 (43945) re-samples and
  **destroys time order — wrong for a drift stream**, named so nobody grabs it); Covertype = **1596** (v4 — 581,012×54×7
  confirmed; id 150's full-data equivalence is unconfirmed, use 1596 — design §8 L2), stream convention = **file
  order** (the MOA/Gama convention — Covertype has no timestamp; the convention is stated, not invented);
  CIFAR-100 = 41983 (stretch-only; verify at bench). MNIST-784 (554) and
  CIFAR-10 (40927) verified **already cached on this box**.
- **D7 — a citation fix.** CLEAR is **Lin, Shi, Pathak & Ramanan, NeurIPS 2021 D&B
  ([2201.06289](https://arxiv.org/abs/2201.06289))** — the temp2 concept's CLEAR link pointed at CALM
  ([2004.03340](https://arxiv.org/abs/2004.03340)), a different paper. CLEAR + CORe50 remain **named non-claims**
  (pretrained backbone + GBs of images — E5 carries their spirit only).

---

## 1 · The arena canon (what the field recognizes, at this box's scale)

| arena | source / ID | dims → porthole | C | samples | drift axis | role | anchor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sklearn digits | built-in | 64 → 40 | 10 | 1,797 | (P10 anchor) | r0, done | P10 itself |
| MNIST-784 | openml 554 ✓cached | 784 → 40/80 | 10 | 70k | synthetic 5-domain + volume | E1-r1 | van de Ven Split/Permuted-MNIST |
| Fashion-MNIST | openml 40996 | 784 → 40/80 | 10 | 70k | texture-not-stroke | E1-r2 | (same family) |
| CIFAR-10-gray | openml 40927 ✓cached | 1024 → 40/80/160 | 10 | 60k | natural images; known hard floor (P2/P5) | E1-r3 | Split-CIFAR convention |
| **Gas Sensor Drift** | UCI | 128 (native) | 6 | 13,910 / 10 batches / 36 months | **physical sensor aging** | **E2 headline** | Vergara 2012 · Dennler 2022 |
| HAR (smartphones) | UCI | 561 (native) | 6 | 10,299 / 30 subjects | person-to-person shift | E2 secondary | UCI HAR canon |
| Electricity (ELEC2) | openml 151 | 8 (native) | 2 | 45,312 chronological | market/price regime | E2 streaming canon | Gama canon + Souza 2020 no-change |
| Covertype | openml 1596 | 54 (native) | 7 | 581k (slice, file order) | cartographic order | E2 streaming canon | MOA/Gama canon |
| Wild-Time Yearbook | Wild-Time repo | 1024 (32×32×1) | 2 | 33,431 / 1930–2013 | **real vision drift, 8 decades** | E2 vision leg (bonus) | Yao 2022 |
| BloodMNIST | MedMNIST npz | 2352 (28×28×3 RGB — design §8 L1) | 8 | ~17k | (static; famous-data rung) | E1 bonus | Yang 2023 |
| CIFAR-100 | openml 41983 | 1024 → 160 | 100 | 60k | class breadth | E3 stretch | — |
| 5-Datasets (ours: 3-block) | the three above | shared porthole | 30 | 3×NTR | **dataset identity itself** | E7 | Ebrahimi 2020 |

Rejected (unchanged from the rough plan, one line each): Speech Commands (2 GB + audio pipeline), raw CORe50/CLEAR
(backbone + GBs — D7), TinyImageNet (nothing over CIFAR-100 at our scale), SVHN/notMNIST (RGB/availability — the
3-block variant carries the protocol's spirit).

---

## 2 · Protocol pins (so no rung invents its own convention)

- **Prequential (test-then-train) is the streaming read** on every real-world stream — the live-batch curve IS the
  field's prequential accuracy (Gama's convention); our per-batch STREAM view needs no new machinery, only the name.
- **The no-change (persistence) baseline runs on every real-world stream** (D2) — costless, and the strongest
  known cheap opponent on autocorrelated streams (ELEC2 ≈ 85%).
- **Gas**: stream = batches 1→10 in time order; scaler fit on batch 1 only, frozen; balanced accuracy; reversed-order
  run committed (10→1). **HAR**: stream by subject (30 blocks), subject order seed-shuffled per seed (subject
  arrival order is not physically meaningful — unlike gas batches); reversed = the same permutation reversed.
- **5-Datasets/E7**: class-IL, 10 classes per block, single growing head, per-source frozen projection (per-source
  unit-RMS normalization fit on that source's train split only), forward = MNIST→Fashion→CIFAR-gray + committed
  reversed.
- **Fraction-of-ceiling**: every arena's headline read is also reported as AA / joint-BP-ceiling-AA on that arena —
  separating "the stream is hard" from "the data is hard." (In-house convention; the joint ceiling itself is the
  standard upper-reference — GEM/van-de-Ven convention.)

---

## 3 · Carried unchanged from the P10 canon

Budgeted-CL (Prabhu CVPR'23 [2303.11165](https://arxiv.org/abs/2303.11165) — ER strong under FLOPs+bytes) · real-time
eval (Ghunaim CVPR'23 [2302.01047](https://arxiv.org/abs/2302.01047) — the E6 derivation frame) · AAA (OSAKA
[2003.05856](https://arxiv.org/abs/2003.05856)) · three scenarios (van de Ven [1904.07734](https://arxiv.org/abs/1904.07734)) ·
the baseline family ER/A-GEM/DER++/GDumb/naive ([`../phase10/README.md`](../phase10/README.md)) · Deep SLDA (Hayes &
Kanan CVPRW'20 [1909.01520](https://arxiv.org/abs/1909.01520)) + RanPAC (NeurIPS'23 [2307.02251](https://arxiv.org/abs/2307.02251))
— the frozen-backbone convention E5 would enter, and the reason the field's own topology matches our bulk+namer split.
