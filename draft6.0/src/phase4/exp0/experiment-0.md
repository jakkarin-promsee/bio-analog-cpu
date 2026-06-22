# Experiment P4.0 — the bench + the difficulty axis (A1)

> **Status: ✅ DONE (2026-06-22).** The locked first run: validate the whole characterization apparatus
> (controlled generator, **exact** Bayes error, three racers, gap + cost meters) and ask A1 — *does the gap to a
> genuinely-tuned backprop open as the task gets harder?* Stack: numpy-only (`p4lib`), 6 overlaps × 5 seeds
> `[42,137,271,314,1729]`, 4000 train / 1500 test, dim 40, 4 classes, 16 clusters. Reporting contract:
> [`../result-format.md`](../result-format.md). Run: `OMP_NUM_THREADS=1 python -u run_p4_0.py` (2615s, crash-safe
> per-cell checkpoint).

---

## The 6+2 slot read

**1 · Claim.** The bench is **validated and adopted** for Phase 4 — and A1 has a clean, slightly counter-intuitive
answer: **the absolute gap-to-BP does *not* open with difficulty; it *closes*** (then a small overfitting uptick at
the near-chance end). The real difficulty signal lives in **Bayes-normalized capture**, which falls monotonically.
OURS sits a few points under a *genuinely-tuned* BP, **beats Mono-Forward at every difficulty**, **generalizes
better than both** (smaller train−test gap) until the hardest cell, and is only **modestly cheaper** than BP under a
conservative *static* backward-work meter — the dramatic 80/20 cheapness is **not** visible per-pass (it lives in
the gate + sleep cadence this meter omits → Phase 5).

**2 · Number + IQR** (median [IQR], n=5):

| overlap | Bayes | OURS | BP (tuned) | Mono | gap-to-BP | capture |
| --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 0.022 | 0.918 | 0.963 | 0.873 | +0.050 [+0.041,+0.051] | 0.917 [0.917,0.917] |
| 0.65 | 0.082 | 0.827 | 0.873 | 0.771 | +0.047 [+0.046,+0.049] | 0.865 [0.864,0.869] |
| 0.80 | 0.164 | 0.732 | 0.755 | 0.681 | +0.023 [+0.015,+0.030] | 0.822 [0.817,0.831] |
| 0.95 | 0.244 | 0.642 | 0.652 | 0.597 | +0.013 [+0.000,+0.015] | 0.775 [0.768,0.778] |
| 1.10 | 0.315 | 0.569 | 0.586 | 0.538 | +0.011 [+0.007,+0.015] | 0.731 [0.730,0.741] |
| 1.25 | 0.371 | 0.507 | 0.541 | 0.491 | +0.035 [+0.025,+0.037] | 0.679 [0.676,0.701] |

Gap-to-BP **closes** +0.050 → +0.011 (Bayes 0.02→0.32), then upticks to +0.035 at 0.37. Capture **monotone** 0.917
→ 0.679. OURS − Mono **+0.015…+0.056** (OURS always ahead). Backward cost OURS/BP = **0.90 @easy** (47k vs 52k,
BP picks a shallow shape) → **~0.61 @hard** (47k vs 77k, BP needs depth). The **BP ceiling is real**: weight-decay
chosen every cell, shape varies (d2w132…d4w81) — widening the search over the old 3-lr grid lifted BP ~0.7pt.

**3 · Figures.** `RACE` (three racers vs Bayes-optimal — all track the optimal decline, BP hugs it, OURS just
below, Mono lowest) · `GAP_CURVE` (gap closes; capture monotone-down) · `PARETO` (easiest cell: OURS 0.92@47k, BP
0.96@52k, Mono 0.87@25k) · `INV` (Bayes monotone in the dial ✓; cost bars ✓; gen-gap rises with difficulty, OURS
lowest until it crosses up at 1.25).

**4 · Mechanism.** The absolute gap *closes* because rising Bayes error squeezes **every** racer toward chance —
the achievable window `(1−Bayes) − chance` shrinks, so a constant *relative* shortfall reads as a *smaller absolute*
gap. **Capture removes that artifact** and exposes the true, monotone degradation: OURS gives up a steadily larger
slice of the achievable as the task hardens. OURS's lower train−test gap is the Phase-1 *"memorizes less"* property
re-appearing; the hardest-cell uptick (gen-gap spikes above BP at 1.25) is OURS **fitting noise** once the task is
near-chance. On cost: the Phase-3 **coordination window (w=2)** makes the SCFF bulk pay *2-deep* backprop (energy-
goodness paid ~0), and the all-tap readout (256→32→4) is chunky — so the *static per-pass* backward work ≈ BP's.

**5 · Threats.** (a) Synthetic Gaussian clusters with 2-active-dim structure — real-data anchor still owed (carries
to a later rung). (b) Near-chance noise at overlap 1.25 inflates variance — the +0.035 uptick is real but partly an
overfitting artifact, not "the gap reopening." (c) The cost meter is **analytic and static** — no gate, no sleep
cadence — so it *understates* OURS's online cost advantage and may *overcount* the window's cost vs analog physics
(short local credit is cheap on the substrate, linear in the meter). (d) BP tuned over a finite grid (genuinely
tuned ≠ exhaustive Optuna).

**6 · Decision.** **Bench ADOPTED** — exact Bayes monotone, cost meter sane, three racers well-behaved, all figures
render: the apparatus is trustworthy for P4.1–P4.7. **A1 verdict: the gap does not open with difficulty** (the
SCFF-paper intuition is wrong here). **Carry forward:** report **capture** as the difficulty-axis headline, *not*
raw gap-to-BP (the absolute gap is confounded by the shrinking achievable window). OURS > Mono on synthetic
(Spyra's "Mono > BP on MLP" is image-architecture-specific, doesn't transfer here).

**7 · Cost-honesty.** 47k / 52k / 25k are **backward credit-assignment work** (analytic, substrate units) — **not
energy, not wall-clock**. At matched weight budget and *per-pass*, OURS is **competitive-cost, not dramatically
cheap** (~10% under BP at the easy cell, ~40% at the hard cells). The 80/20 design's cheapness is **not** a per-pass
property — it lives in (i) **credit-distance** (OURS ≤2 vs BP full depth 3–5) and (ii) the **online gate + sleep
cadence** (most steps forward-only SCFF; GD/readout only at sleep), *neither* in this static meter by construction.
**We do not claim 80/20 from P4.0.**

**8 · Map-contribution → Phase 5.** First tile of the capability map (the difficulty axis). It tells Phase 5: **(a)**
static accuracy is *competitive-but-behind* (capture 0.68–0.92), exactly as the design predicts — the win is not
here; **(b)** the 80/20 cost claim is **unproven under static accounting** → Phase 5's cost meter *must* add the
gate + sleep-cadence to substantiate it; **(c)** the **all-tap readout width** is a live cost knob; **(d)** OURS
**overfits near chance** → a regularization knob for hard regimes. The win axes (continual A6, noise A7) are still
ahead.

---

## Reproducibility

`figs_p4_0/manifest.json` (git commit + config + gap-easy/hard) + `arrays.npz` (per-overlap medians incl. train
accs) + `_ckpt.jsonl` (every cell, resumable). Figures regenerate with no retraining:
`python plot_p4_0.py figs_p4_0`. Single-threaded (`OMP_NUM_THREADS=1`), `python -u`, per-cell fsync — verified
alive mid-run (not the phantom-hang). New/changed cells: `p4lib.race_bp` (widened: shape × lr × weight-decay),
`run_p4_0.OVERLAPS` (informative band 0.02–0.37), `plot_p4_0` (+INV).
