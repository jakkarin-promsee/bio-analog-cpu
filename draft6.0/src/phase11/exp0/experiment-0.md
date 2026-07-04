# P11.0 — bench: data + loaders + guards + the two pre-derivations (no verdict, a build)

**Question.** Before any verdict: does every arena load offline with its declared stream order, do the recipe /
data / dominance guards hold, is the noise-σ pinned by P10 equivalence, is the GD-share-vs-W shape derived from the
meter (not memory), and does the frozen object still reproduce bit-exact? **Any red → STOP** (a broken bench
poisons every later verdict).

**Setup.** Loaders in the house signature; the P11 guards; two pre-derivations; anchors transcribed. Bench-only
network already spent (the ONE session — gas/HAR/electric/covtype/Fashion all landed; MNIST/CIFAR/digits cached).
Live cells load from the local cache.

**Result — ALL GREEN (57 s).**

| check | outcome |
| --- | --- |
| **arena-data** | 7 arenas load offline, declared order asserted: digits 8×8 · MNIST/Fashion/CIFAR-gray 784 (CIFAR center-cropped 32→28) · gas 13910×128 C6 (batch 1–10) · HAR 10299×561 C6 (30 subjects) · electric 45312×8 C2 (chronological) · covtype 581012×54 C7 (file order). **Yearbook / BloodMNIST / CIFAR-100 = not fetched (optional bonuses, out of the committed core).** |
| **imbalance (→ balanced-acc trigger)** | gas 1.83 · HAR 1.38 · electric 1.38 · **covtype 10.02 (>3:1 → balanced accuracy mandatory)**. |
| **recipe** | Arm A {D40,W64,L12} bit-equal committed (0 leaks); Arm B {D80,W128}/{D160,W256} whitelist = {D,W,L,C,cap} only (0 leaks). |
| **noise-σ equivalence (F3)** | RMS_P10-digits = 0.4859; σ_rung = (0.6/RMS_P10)·RMS_rung → σ/RMS = **1.239 for every arena** (== P10's absolute-0.6-on-RMS-0.486). The C4 "0.6×RMS" shorthand would have made MNIST's noised domain ~2× milder — caught. |
| **GD-share vs W (pinned shape, C3)** | from `hardware_cost_meter`: W {64,128,256} → GD-share {0.21, 0.34, 0.53} — **RISES with W.** The SLDA solve term ~O((L·W)³) drives it up; the economy does **not** improve with scale (the temp2 "improves with scale" guess, off an O(D·C+D²) formula, is refuted at the source — the recurring direction-killer, caught pre-run). |
| **dominance** | ER-strong (tuned, seed-7 gas) balanced 0.757 ≥ naive-BP 0.238. |
| **freeze_content** | grid-4 **bit-exact** vs the P9 freeze (dBWT = dAA = dGD = dNsleep = 0) — the object measured here IS the P9-frozen object (provenance 59d2720). |
| **anchors** | gas: Vergara 2012 + Dennler 2022 (limitations) cited on the figure. Split-MNIST: van de Ven 2022 class-IL — naive≈0.199, replay high; **exact ER band transcription OWED** (paper did not fetch this box; the anchor cell runs the published config and reports its number, band comparison flagged). |

**Read (build).** Bench green → proceed to P11.1. The two pinned artifacts (σ-equivalence constants, the
GD-share-vs-W shape) and the composition tables are banked in `figs_p11_0/manifest.json` and cited by every later
rung. **Deviations from the spec, and why:** (1) **Yearbook/BloodMNIST/CIFAR-100 not fetched** — the openml *API*
timed out on this box; the committed-core arenas all landed via reliable routes (Zalando GitHub / figshare / UCI),
so the map ships its core columns and marks the bonuses not-run (author's "mark-not-run, keep going" instruction).
(2) **Split-MNIST anchor band = region-approx** — the precise published band needs the paper, which didn't fetch;
the guard mechanism is in place, the exact transcription is the one owed bench item. (3) ER per-arena tuning is run
inside each FIGHT rung (grid pinned here) rather than all at bench — same grid, less idle recompute.

*Guards: arena-data ✓ recipe ✓ noise-equiv ✓ gd-shape-pinned ✓ dominance ✓ freeze-content ✓ anchors ✓.*
