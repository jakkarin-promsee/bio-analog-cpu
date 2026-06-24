# Phase 4 — what we discovered (the synthesis): the capability map

> The **characterization** phase of draft 6.0, run 2026-06-22 (P4.0 → P4.6). The *story of the findings* — where the
> adopted cell (`[contrast (InfoNCE, two-mask) + coordination w=2] SCFF bulk + sleep-consolidated readout`, the
> Phase-3 winner) wins, ties, and loses against a **genuinely-tuned backprop** ceiling and the **Mono-Forward**
> forward-only-supervised reference, across seven controlled axes. Per-rung detail in each `expN/experiment-N.md`;
> the scalar ledger is [`RESULTS.md`](RESULTS.md); the plan + method canon was [`README.md`](README.md); the
> reporting standard is [`result-format.md`](result-format.md). Stack: numpy-only (`p4lib`) + the reused Phase-1/2/3
> machinery; controlled Gaussian generator with **exact** Bayes error; 5 seeds (3 for continual), median + IQR.

---

## The one-paragraph verdict

**Phase 4 maps the cheap brain honestly — and the map says exactly what the project always claimed: it is not a
static-accuracy competitor, it is a substrate-native continual learner.** OURS **trails** a tuned backprop on the
static axes — raw difficulty (A1: the gap doesn't *open*, but Bayes-capture declines to ~0.68) and class count (A5:
gap widens to +0.23 on harsh synthetic, though real digits is far kinder at +0.03) — and, surprisingly, is **not**
more robust to eval-time weight noise (A7: a clean negative, retention 0.75 vs BP 0.88). But it **wins where the
substrate lives**: nuisance-dimensional input (A2 — *crosses above* tuned BP by dim 500 while Mono collapses),
depth-composition (A3 — *generalizes* across difficulty and out-composes BP in the hard/low-headroom regime),
depth-is-cheap (A4 — backward cost **flat in depth** vs BP's linear blow-up; the 80/20 advantage is **depth-gated**),
and **decisively continual** (A6 — the home: BWT −0.02 to −0.18 vs BP's catastrophic −0.83 to −0.99, robust across
the whole difficulty band). The honest negatives are *features* of the map, not failures: they tell Phase 5 exactly
where **not** to compete (static accuracy, many-class, eval-time noise) and what to **test** (train-with-noise, and
natural-data multi-class) before optimizing. **The cell is sound; no algorithm bug hid in the breadth.**

---

## The capability map (win / tie / lose)

| axis | dial | verdict | the number |
| --- | --- | --- | --- |
| **A1 difficulty** | Bayes error 0.02→0.37 | **trail** (cost of the gap) | gap doesn't open (+0.05→+0.01, uptick at chance); **capture** 0.92→0.68 is the real read |
| **A2 ambient-dim** | nuisance dim 8→500 | **WIN** | OURS **crosses above** BP by dim 500 (gap −0.029); **Mono collapses** (0.75→0.41) |
| **A3 depth × difficulty** | headroom task, overlap 0.4→1.2 | **WIN (composes)** *(representation, not task-acc)* | depth-composition **generalizes** (w2 per-layer-probe slope >0 all difficulties); OURS **out-composes BP** in the hard regime (crossover ≈0.6) |
| **A4 width × depth** | iso-budget L2→L12 + W64 control | **WIN (cost)** | OURS/OLD backward **flat in depth** (~14–40k) vs BP **linear** (52→169k, ratio 1.3×→6.8×); energy-Σh² baseline **collapses with depth** (the wall); contrast composes ~5 layers (beats BP L2–L6 on headroom) then **decays — and the W64 control shows it's DEPTH-DECAY, not width** |
| **A5 class count** | C 2→20 | **trail** (difficulty-gated) | synth gap +0.06→+0.23; **real digits +0.03** — harshness, not a many-class penalty |
| **A6 continual** | class-incremental × difficulty | **DECISIVE WIN** | OURS+sleep BWT −0.02→−0.18 vs online-BP −0.83→−0.99; robust across difficulty |
| **A7 noise** | weight σ 0→0.4 (eval-time) | **NEGATIVE** | OURS *least* robust (ret 0.75 vs BP 0.88) — but eval-time ≠ the substrate's train-with-noise regime (untested) |

---

## The arc, rung by rung

**P4.0 — the bench + difficulty (A1).** Apparatus validated (exact Bayes monotone, cost meter sane, three racers
behave). **The gap to BP does *not* open with difficulty — it *closes*** (the achievable window shrinks as everyone
is squeezed toward chance), so **capture is the honest difficulty read** (monotone 0.92→0.68). First sign the cost
advantage isn't visible per-pass at shallow depth (revisited by A4).

**P4.1 — ambient-dim (A2) — the first WIN.** As nuisance dimensions grow at fixed difficulty, OURS holds (~0.79)
while BP gently declines (budget-squeezed first layer) and **Mono-Forward collapses toward chance** (overfits the
junk, gen-gap 0.59). **OURS crosses *above* tuned BP by dim 500 — cheaper *and* more accurate.** Mechanism: contrast
+ per-sample layernorm down-weight non-discriminative dims for free. Substrate-relevant (analog crossbars are wide).

**P4.2 — depth × difficulty (A3) — composition generalizes.** Using the per-layer probe slope (depth-composition is
invisible to task accuracy), OURS w=2 composes depth **across the whole difficulty band** (slope >0, IQR-disjoint
from 0); the **w=1 no-coordination control never composes** (coordination is the lever). GD-hidden loses its own
headroom by overlap 1.0 — so **OURS and BP compose in complementary regimes** (BP at easy, **OURS in the hard
regime**, crossover ≈0.6). w=2 shows a mild inverted-U at easy+deep (P3.2's w=4 fixes it → a window knob).

**P4.3 — width × depth (A4) — the Scap-collision resolved, via cost (re-run + extended).** At iso-weight budget,
**OURS's *and* OLD's backward cost is flat in depth (~14–40k) while BP's grows linearly (52→169k)** — narrow-deep,
the substrate-native direction, is ~free for the forward-only methods and up to **6.8×** costlier for BP. The re-run
added the **energy-Σh² baseline** (Phase-1/2 wall cell), measured at the **last-layer readout** (where a real GD
head sits; all-tap had *masked the wall* by reading the good early layers), and extended depth to L12 plus a
**fixed-width W64 control**. The baseline makes the wall legible: **OLD collapses monotonically** (headroom
0.49→0.31, flat 0.76→0.34). **Contrast flattens but does not abolish it** — OURS composes to ~L3–L5 and beats tuned
BP L2–L6 on headroom, then **decays (loses to BP L8–L12)**. The prior "OURS climbs to L6" was an all-tap artifact.
**The control settles the cause:** at *constant* W64 OURS still droops with depth (headroom 0.557→0.449) — so it is
**depth-DECAY, not the iso width-shrink** (which adds only ~0.02–0.03). The cross-layer window genuinely shares
context for ~5 layers (energy composes zero), but not unboundedly. **The 80/20 cost advantage is depth-gated**
(1.3×→6.8×), and the deployed **all-tap / boosting readout is load-bearing** — it works around the *residual* decay
(a single deep head is the wrong design). **A follow-up ([P4.3-decay](exp3/experiment-3-decay.md)) names the cause:** widening each layer (up to
W240) does **not** fix it (fix64≈widen by L12), dead-unit fraction ≈ 0, and widen's higher rank buys no accuracy —
so the decay is **local-objective drift off the class manifold past ~layer 5, not width / dead-units / capacity**;
the fix is **preservation** (all-tap/boosting — vindicated — or residual skips). A mixed flat+headroom task shows
the deep layers **corrupt** the early-solved flat subtask (probe ~0.67→0.51) while tuned BP holds it flat (~0.75).
*(Caveat: depth-scaled training still untested.)*

**P4.4 — class count (A5) — competitive-but-trails, difficulty-gated.** On the harsh synthetic the gap widens with
C (+0.06→+0.23) and OURS's edge over Mono erodes (Mono ties by C20). **But the real anchors are far kinder** —
digits (10-class) gap +0.03, CIFAR-flat +0.09 — so the synthetic widening is *discrimination hardness*, not a
many-class penalty. Not a win axis; validate multi-class on natural data, benchmark vs Mono at high C.

**P4.5 — continual (A6) — THE win, robust across difficulty.** OURS+sleep forgets almost nothing (BWT −0.02 to
−0.18) at *every* difficulty + digits (which reproduces P3.3 exactly: 0.954 / −0.017), while online-BP
catastrophically forgets (−0.83 to −0.99) and the no-sleep control rots (sleep is the recovery mechanism; SCFF
itself doesn't forget). AA falls with difficulty but BWT stays excellent — the win doesn't erode off the home config.

**P4.6 — noise (A7) — an honest negative.** The plan expected a win ("forward-only is noise-robust"). Under
*eval-time* multiplicative weight noise on a *clean-trained* model, **OURS is the *least* robust** (ret 0.75 vs BP
0.88). Likely cause: **per-sample layernorm — the A2 win mechanism — doesn't damp weight-direction noise**, so A2's
robustness and A7's fragility share a cause (a real tradeoff). Crucially, eval-time noise ≠ the substrate's regime
(online learning *with* noise = hardware-aware, where the literature's claim lives) — **untested, the proper P5
follow-up.** A caught over-optimistic assumption is a successful pre-flight check.

---

## The cross-cutting discoveries

1. **The win is the continual + depth-on-substrate story, not static accuracy** — exactly the project thesis,
   now *measured*. The static axes (A1, A5) characterize the *cost of the gap*; the wins (A2, A3, A4-cost, A6) are
   where the substrate lives.
2. **The 80/20 cost advantage is depth-gated** (P4.0 null shallow → P4.3 6.8× deep). A single shallow number
   understates it; the substrate operates deep, where it's large. Phase 5's cost meter must report **cost-vs-depth**.
3. **Layernorm is a double-edged sword** — it buys nuisance-robustness (A2) and costs weight-noise-robustness (A7),
   *same cause*. A tunable tradeoff, possibly regime-dependent.
4. **Mono-Forward is an unreliable reference** — collapses in high-D (A2), catches up at high class count (A5).
   Keep it (Spyra's strongest forward-only-supervised bar) but read it in context, not as a fixed baseline.
5. **Capture > raw gap-to-BP** as the difficulty read (A1) — absolute gap is confounded by the shrinking achievable.
6. **Synthetic harshness ≠ real** — real digits is far kinder than the synthetic at the same class count (A5);
   validate on natural data before treating synthetic gaps as real limits.

---

## What's validated vs not

| | status |
| --- | --- |
| Continual win (sleep recovers, online-BP forgets) robust **across difficulty** | ✅ (A6) |
| Nuisance-dim robustness — OURS crosses above BP in high-D | ✅ (A2) |
| Depth-composition **generalizes** across difficulty (coordination = the lever) | ✅ (A3) |
| Depth is **cheap** for OURS (flat backward) vs BP (linear) — 80/20 depth-gated | ✅ (A4) |
| Static multi-class accuracy competitive **on natural data** | ⚠️ digits ✅ (+0.03), CIFAR ⚠️ (+0.09, 1 seed); broader natural data untested |
| Noise robustness **during learning** (hardware-aware, the substrate regime) | ❌ untested — eval-time is a non-win (A7); train-with-noise is the proper test |
| Beats a *tuned* BP on static accuracy | ❌ not claimed (trails on A1/A5 — the cost of the gap) |
| Scale / convolution / time-series | ❌ deferred (needs architecture — north star) |

---

## The Phase-5 brief (the hand-off)

Phase 4 says **what to optimize, where to build, and what to test** — picked from data, not guesses:

1. **Optimize the continual mechanism** (sleep cadence + the Ch7 gate) — A6 is the validated win; tune it against
   *this* cell's measured drift. **This is Phase 5's core.**
2. **Build deep, but gate depth on headroom.** Depth is cheap (A4) and composes (A3) — invest in it — but it only
   *pays* where there's headroom (flat tasks don't reward it). **Scale the coordination window with headroom** (w=2
   cheap in the hard regime; grow to w=4 for easy+deep monotone composition — P4.2/P4.3).
3. **Make the cost meter depth-aware and temporal.** The 80/20 is depth-gated (A4) and the online cheapness lives in
   the gate + sleep cadence (A1/A4) — report cost-vs-depth, and meter the gated/sleep online cost, not a single
   per-pass number.
4. **Run the train-with-noise (hardware-aware) test** before any analog noise-robustness claim (A7) — and treat
   layernorm as a tunable nuisance-robustness↔noise-sensitivity knob.
5. **Validate multi-class on natural data** (A5) — the synthetic overstates the static gap; benchmark vs Mono at
   high class count.
6. **Don't compete on static accuracy, many-class, or eval-time noise** — the map says that's not the architecture's
   place; the continual + substrate-native-depth regime is.

---

## Reproducibility

Every rung writes `figs_*/{manifest.json, arrays.npz, _ckpt.jsonl}`; figures regenerate with no retraining
(`python plot_p4_N.py figs_p4_N`). Seeded/deterministic. **Run single-threaded** (`OMP_NUM_THREADS=1` + `python -u`
+ per-cell fsync checkpoint — resumable; the phantom-hang guard) and **`PYTHONIOENCODING=utf-8`** (the cp874 console
gotcha). Apparatus: `p4lib` (exact-Bayes generator, the three racers, the backward-cost meter); reuses Phase-1/2/3
(`make_tierb`, `probe_per_layer`, the P3.3 continual harness, `SCFFContrastOLU`). Entry points: `exp0/run_p4_0.py`
(difficulty) · `exp1/` (ambient-dim) · `exp2/` (depth×difficulty) · `exp3/` (width×depth) · `exp4/` (class+anchors) ·
`exp5/` (continual) · `exp6/` (noise). A latent OOM bug (`bayes_error`'s `[n,K,dim]` tensor) was caught + fixed (the
dot-product identity) during P4.1 — the breadth-as-bug-catch working as intended.

---

## The bridge to Phase 5 (and the north star)

Phase 1 found *where* this architecture wins (continual). Phase 2 found energy-goodness can't earn depth. Phase 3
found *how it can* (contrast + coordination) and that it doesn't cost the continual win. **Phase 4 drew the map** —
the cheap forward-only brain is a substrate-native continual learner that composes depth cheaply and tolerates
nuisance, not a static-accuracy or eval-time-noise competitor. Phase 5 now *optimizes the win* (the sleep/gate
maintenance loop) on a cell we **trust** — and the train-with-noise + natural-data tests open the door to the
analog-realism layer. The north star — the recurrent prefrontal↔hippocampus loop — sits beyond, but the continual
machinery Phase 4 confirmed is the substrate it will be built on.
