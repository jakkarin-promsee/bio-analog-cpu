# Experiment P4.4 — class count (A5) + real-data anchors

> **Status: ✅ DONE (2026-06-22).** Does the cheap brain hold as the label space grows, and does the synthetic story
> survive REAL flat input? Synthetic sweep: FIXED cluster geometry (40 clusters, dim 40, overlap 0.6), only label
> granularity changes — C ∈ [2,4,10,20], exact Bayes per cell. Real anchors: digits (64-D, 10-class, 5 seeds,
> full-rigor) + CIFAR-flat (3072-D, 10-class, 1-seed sanity — already the "wall" of Phase 2/3). Racers: OURS / tuned
> BP / Mono. Run: `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_4.py` (2851s). Contract:
> [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** **A5 is a "competitive-but-trails" axis (like A1) — and the trail is difficulty-driven, not
count-driven.** On the harsh controlled synthetic the **gap to tuned BP widens with class count** (+0.06 → +0.23,
saturating ~C10) and **OURS's edge over Mono erodes** (Mono ties/passes by C20). **But the real anchors show this
is largely synthetic-harshness:** on **digits (10-class) the gap is +0.027** (OURS competitive), on **CIFAR-flat
(10-class) +0.090** — far below the synthetic C10 gap of +0.23. So "many classes" is *not* OURS's downfall; the
40-cluster random-label discrimination is simply a hard read that favours supervised BP. **Capture plateaus ~0.67.**

**2 · Number + IQR** (median [IQR], n=5 synth / n=5 digits / n=1 cifar):

| C | Bayes | chance | OURS | BP | Mono | gap-to-BP | capture | OURS−Mono |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.035 | 0.500 | 0.854 | 0.917 | 0.753 | +0.063 [+0.057,+0.067] | 0.76 | +0.097 |
| 4 | 0.056 | 0.250 | 0.739 | 0.881 | 0.670 | +0.143 [+0.140,+0.144] | 0.70 | +0.069 |
| 10 | 0.066 | 0.100 | 0.655 | 0.881 | 0.640 | +0.226 [+0.226,+0.233] | 0.67 | +0.015 |
| 20 | 0.071 | 0.050 | 0.647 | 0.881 | 0.661 | +0.234 [+0.223,+0.238] | 0.68 | **−0.015** |

**Real anchors (10-class):** digits gap **+0.027** (OURS 0.960, BP 0.987 — both near Bayes); CIFAR-flat gap +0.090
(OURS 0.304, BP 0.394 — the wall). BP flat ~0.88 across the synthetic sweep; **OURS declines 0.85 → 0.65**.

**3 · Figures.** `GAP_CURVE` (OURS gap widens to +0.23; **digits/CIFAR anchors sit far *below* the synthetic curve**
at C10 — real is kinder; capture flat) · `RACE` (BP flat, OURS & Mono decline and converge by C20; digits stars
hug the Bayes line, CIFAR low) · `INV` (Bayes ~flat, chance ∝ 1/C; gen-gap).

**4 · Mechanism.** At fixed per-cluster difficulty, more classes = a **finer label partition of the *same* 40
clusters** = a harder discrimination boundary. Supervised BP (direct label gradient) tracks it; **unsupervised
contrast (OURS) approximates it more loosely** → the gap widens. More classes also feed **Mono** (supervised local)
more signal → it catches up (OURS−Mono → 0 by C20). On **real digits** the 10 classes are well-separated clusters
(low intrinsic difficulty), so contrast reads them fine — tiny gap. So the curve is really **gap-vs-discrimination-
hardness**, and class count on the harsh synthetic conflates *count* with *hardness*.

**5 · Threats.** (a) The synthetic dial **conflates class count with discrimination hardness** (finer partition of
fixed clusters gets harder to read) — so the +0.23 is *not* a pure "20-class penalty"; the **real anchors are the
more representative read** (digits 10-class ≈ +0.03). (b) **CIFAR n=1** (sanity only — Phase 2/3 has the full
CIFAR-flat characterization). (c) digits is near-Bayes for all racers (an easy anchor — confirms "no catastrophe,"
not a stress test). (d) static accuracy, as throughout — not OURS's win regime.

**6 · Decision.** **A5 = competitive-but-trails (not a win axis); the gap is difficulty-gated, not count-gated.**
**Carry forward:** (i) don't read the synthetic class-count gap as a hard limit — **on real flat data OURS handles
10 classes competitively** (+0.03); (ii) **OURS's edge over Mono is class-count-dependent** — it erodes as
supervised signal grows, so **Mono is the stronger reference at high class count** (consistent with Spyra's
"Mono > BP on richer tasks"); (iii) OURS's value is **not** static multi-class accuracy — it's nuisance (A2),
depth-cost (A3/A4), and continual (A6).

**7 · Cost-honesty.** Backward-cost shape unchanged from P4.0/P4.3 (OURS bulk window-2; cheaper than BP, depth-
gated). Not re-metered — class count doesn't change the credit-distance story.

**8 · Map-contribution → P5.** A5 tile: **static class-count is a trail axis, and the gap is difficulty-gated — real
flat data is far kinder than harsh synthetic.** Tells Phase 5: (a) **validate multi-class on natural data** before
treating the synthetic gap as real; (b) at high class count, **benchmark against Mono-Forward**, not just BP; (c)
**don't optimize for static multi-class accuracy** — it's not where this architecture earns its place.

---

## Reproducibility

`figs_p4_4/{manifest.json, arrays.npz, _ckpt.jsonl}`; `python plot_p4_4.py figs_p4_4`. Single-threaded, `python -u`,
`PYTHONIOENCODING=utf-8`, per-cell fsync. Synthetic = `make_gauss` (40 clusters fixed, labels re-partitioned per C);
real = sklearn `load_digits` + the Phase-3 `load_cifar_local`. CIFAR used a lighter BP grid + 1 seed (3072-D OURS is
minutes-slow; the point is a confirmatory anchor). New: `exp4/run_p4_4.py` + `plot_p4_4.py`.
