# Phase 3 — what we discovered (the synthesis)

> The depth-round-2 / objective-reframe phase of draft 6.0, run 2026-06-21 → 22 (P3.0 → P3.3). The *story of the
> findings* — what we asked, what the sims said, and the honest verdict. Per-rung detail in each
> `expN/experiment-N.md`; the scalar ledger is [`RESULTS.md`](RESULTS.md); the reporting standard is
> [`result-format.md`](result-format.md); the plan was [`README.md`](README.md); the literature behind it is
> [`../../ref2/`](../../ref2/README.md). Stack: numpy-only SCFF (pluggable *objective*) + sklearn probes +
> matplotlib; tasks = CIFAR-10-flat (the wall), a built **depth-headroom** synth task (the headroom test), digits
> (the continual veto); 5 seeds (3 continual).

---

## The one-paragraph verdict

**Phase 2 closed the wrong thing — and Phase 3 reopens depth and wins it.** Phase 2 proved a deep *energy-goodness*
SCFF stack can't earn depth and concluded the wall is "intrinsic to forward-only locality." The literature pass
([`../../ref2/`](../../ref2/README.md)) showed that was one word too strong: the wall is intrinsic to the
**energy objective** (`Σh²`), not to locality — Greedy InfoMax / CLAPP (and greedy layer-wise autoencoders before
them) are forward-only, unsupervised, *and* depth-composing because their objective is information-preserving.
Phase 3 tested that on our substrate and found a clean, decomposed answer: **the objective *family* is the lever**
(P3.0 — reconstruction preserves *density*, below random; contrast preserves *class*, above random; energy decays
into random), **cross-layer coordination is the second lever** (P3.1 — the user's "A1-helps-layer-2" / OLU eases
the decline and, **given depth headroom, makes `contrast + coordination` *compose* depth — rising monotonically,
matching/beating the GD baseline** (P3.2), decisively overturning P2.2's verdict), **and it costs nothing we
value** (P3.3 veto — it *re-earns and improves* the Phase-1 continual win, BWT −0.017 vs energy −0.026,
forgetting-robust). **Verdict: adopt.** `[contrast (InfoNCE) + coordination window w≥2] bulk + sleep-consolidated
readout` is a **strict upgrade** over energy-goodness and **supersedes it as the SCFF objective for draft 6.0**.

---

## The arc, rung by rung

### P3.0 — the objective swap (the make-or-break)
**Result.** **The objective family is the lever — and the right one is *discriminative* preservation.** Three
unsupervised objectives on the identical bench (CIFAR-flat) behave completely differently: **energy** decays
*through* the random floor (slope −0.020); **masked-reconstruction** flattens the slope (−0.005) but sits *below*
random (selectivity −0.062 — it preserves pixel/**density** info, the Phase-2 density≠class trap re-incurred in the
*reconstruction target*); **contrast (InfoNCE/CLAPP)** stays *above* random at every depth (selectivity **+0.060**,
5/5, *growing* with depth — it preserves **class** info) **but still declines** (−0.016). Reconstruction =
flat-but-wrong; contrast = right-but-declining. **Set:** the objective must be **contrastive** (why GIM/CLAPP
aren't autoencoders); the residual decline is a *coordination* gap, not an objective gap → P3.1.

### P3.1 — cross-layer coordination (the user's Direction 1)
**Result.** **Coordination is a real, correct lever — flat-CIFAR just can't show it.** A coordination *window* `w`
(layers trained in joint groups, gradient shared then detached; `w=1` ≡ P3.0 contrast, the regression guard)
eased the decline monotonically (w1 −0.0158 → **w2 −0.0105**, deep endpoint 0.230→0.254, selectivity +0.066) and
**rose on synth** (w2 +0.002, w4 +0.008) — but on flat-CIFAR it saturated ~−0.011 and never reached flat.
**The diagnosis that unlocked the phase:** flat-CIFAR has **no depth headroom for anyone** — GD-hidden is flat
~0.36 there — so "slope ≥ 0" was the wrong bar; we were hitting the *task's* ceiling, not the method's. **Set:**
coordination works; need a task with headroom to *prove* it → P3.2.

### P3.2 — the depth-headroom confirmation (side road, decisive)
**Result.** **Given depth headroom, the method *composes* depth.** A scan of the tested `make_tierb` generator
found a config with real headroom (GD-hidden rises 0.39→0.51; *no* config gives both "GD rises AND energy
declines" — in that space difficulty is shared). On it: energy declines (−0.006); contrast **w1 rises-then-falls**
(+0.001, myopic — peaks at L3, drifts down); **w2 +0.012, w4 +0.022 rise *monotonically*** — **w4 climbs to 0.569
at L8, above the GD ceiling**, selectivity +0.18, 5/5 seeds. **Coordination is the decisive lever** (w1 myopic vs
w4 climbing). **This overturns P2.2's "depth intrinsic to forward-only locality"** — it was intrinsic to the
*energy* objective; with a discriminative objective + coordination, forward-only unsupervised learning composes
depth. **Set:** the static-depth question is answered *yes (with headroom)*; flat-CIFAR's PARTIAL was a
task-ceiling artifact. *(Caveats: synthetic task; GD = fixed-budget baseline — the rising slope is load-bearing,
not the GD-beat.)*

### P3.3 — the continual veto (the adoption-deciding rung; closes Phase 3)
**Result.** **VETO PASSED — and improved.** Does `contrast + coordination` re-earn the Phase-1 continual win
(class-incremental digits, sleep-consolidated)? Yes, and it **beats the energy baseline**: final **0.954** / BWT
**−0.017** [−0.020,−0.015] vs energy-SCFF 0.938 / −0.026 [−0.027,−0.022] (disjoint-IQR, 3/3); the contrast
all-class SCFF-probe stays **flat** (doesn't forget); sleep decisive (no-sleep rots to 0.214; GD-online 0.186 /
−0.992). The InfoNCE-bias-to-current-task worry didn't materialize — per-sample, no batch statistics,
continual-safe by construction (same virtue as energy-SCFF). **Set:** the reframe is a strict upgrade → **adopt**.

---

## The cross-cutting discoveries (what the sims forced)

1. **The objective *family* is the lever** — not normalization or negative-selection (those were Phase 2's
   energy-family knobs, both dead). Swapping energy → discriminative-contrastive changes everything.
2. **Reconstruction preserves the *wrong* information** (all of it = density); **contrast preserves the *right*
   part** (discriminative = class). The density≠class wall from Phase 1/2 re-appears in any *reconstruction*
   objective — and is why every depth-composing unsupervised local learner (GIM, CLAPP) is **contrastive**, not an
   autoencoder.
3. **Coordination converts "preserved" into "composed."** Contrast without coordination preserves class info but
   each layer re-discriminates myopically (rises then drifts); the cross-layer window lets a layer serve the
   next's discrimination → monotone rise. This is the exact coordination P2.2 named as missing — supplied
   **forward-only** by the user's Direction 1.
4. **P2.2's "depth intrinsic to forward-only locality" is overturned** — it was intrinsic to the *energy
   objective*. Forward-only unsupervised learning composes depth as well as backprop, with the right objective +
   coordination, when the task has headroom.
5. **Flat-CIFAR has no depth headroom for *anyone*** (GD-hidden flat) — so "rising" is untestable there. The
   methodological unlock was *building a headroom task*; without it, P3.1 looked like a method failure when it
   was a task ceiling.
6. **The contrastive objective is forgetting-robust like energy-SCFF** (per-sample, no batch stats) — the reframe
   doesn't cost the continual win; it slightly improves it.

---

## What's validated vs not

| | status |
| --- | --- |
| The objective family (not norm/negatives) is the depth lever | ✅ (P3.0) |
| Contrast (discriminative) preserves class info; reconstruction preserves density | ✅ (P3.0, selectivity +0.060 vs −0.062) |
| Coordination (Direction 1) composes depth **given headroom** (rises, matches/beats GD) | ✅ (P3.2) |
| `contrast + coordination` re-earns (improves) the continual win | ✅ (P3.3 veto) |
| Depth "rises" on flat-CIFAR | ❌ (task has no headroom for anyone — not a method failure) |
| The result holds on **natural data / at scale** | ⚠️ untested (synthetic + small; a follow-up) |
| **Beats** a *tuned* GD (vs the fixed-budget baseline) | ⚠️ not claimed — the rising *slope* is the result |
| Direct-feedback (global coordination) needed | ❔ untested — the window sufficed |

---

## Open knobs (set) and remaining follow-ups

**Set by Phase 3:** the SCFF objective = **contrast (InfoNCE, two-mask views, temp 0.5)** + **cross-layer
coordination window w≥2** (w=2 cheapest sufficient; larger windows help more where headroom is large);
sleep-consolidated GD readout; per-sample norm (continual-safe). **This supersedes energy-goodness `Σh²`.**

**Remaining (Phase 4 / later):**
- **Natural-data / larger-scale validation** — the headroom result is synthetic; confirm on a real depth-needing task.
- **Direct-feedback (global top-down coordination)** — the 2026 CLAPP++ winner; is global cheaper than a window?
- **A flat-MLP task with *both* headroom and an energy-wall** — `make_tierb` gives easy-for-all or hard-for-all; an open task-design gap.
- **In-batch negatives → the LUT pool** — the substrate form of InfoNCE's negatives.
- **Ch7 gate + sleep-cadence (Phase 4)** — now tuned against *this* cell's drift.
- **Analog / PVT / SPICE realism** — the deferred substrate layer.

---

## The bridge to Phase 4 (and the north star)

Phase 1 found *where* this architecture wins (continual). Phase 2 found energy-goodness can't earn depth. Phase 3
found *how it can* — a different objective + the user's coordination idea — and proved it doesn't cost the
continual win. The cheap brain now has a **better objective end-to-end**: it composes depth *and* doesn't forget,
forward-only and per-sample. That is the substrate Phase 4 builds the *temporal* machinery on (the gate, the
sleep cadence), and the step toward the project's real target — the recurrent prefrontal↔hippocampus loop where
"correctness is a self-generated feeling." Phase 3's gift to it: **a depth-composing, continual-robust,
substrate-native unsupervised objective, validated end-to-end.**

---

## Reproducibility

Every run writes `figs_*/manifest.json` (git commit + config + medians) + `figs_*/arrays.npz`; figures regenerate
with no retraining (`python plot_*.py <dir>`). Seeded/deterministic. **Run heavy jobs single-threaded**
(`OMP_NUM_THREADS=1` + `python -u`) — sklearn/OpenMP phantom-hangs in a backgrounded process; and **a backgrounded
run only saves after all seeds, so a mid-run laptop sleep loses it** (the P3.1 first launch died this way — re-ran
clean). Entry points: `exp0/run_p3_0.py` (objectives), `exp1/run_p3_1.py {cifar,headroom}` (coordination),
`exp2/scan_headroom.py` (the headroom hunt), `exp3/run_p3_3.py` (continual veto). New cells:
`p3lib.py` (`SCFFRecon`, `SCFFContrast`, `SCFFContrastOLU`).
